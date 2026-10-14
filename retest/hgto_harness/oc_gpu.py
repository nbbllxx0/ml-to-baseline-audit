"""GPU port of HGTO's SIMP-OC reference (src/hgto/reference/oc.py, commit d9828ef) for the same-machine re-test.

Pre-registered in plan/BASELINE_PREREG.md §9 (HGTO re-test row). The formulation is the reference's, unchanged:
  * hat density filter, weights max(0, r - d), row-normalised (unit-square cells, so the element-measure weighting of
    the reference is the identity); tanh projection with beta; post-projection floor rho_min = 0.001;
  * modulus E_min + (E0 - E_min) rho^p with E0 = 1, E_min = 1e-6, nu = 0.3, plane stress, Q4 with 2x2 Gauss points;
  * (p, beta) continuation from the configuration; continuation stages capped, final stage up to max_stage_steps;
  * OC update with move 0.2 / max(1, beta) and bisection on the multiplier (relative tolerance 1e-8, <= 100 steps);
  * volume restoration by a logit shift at the start of every stage (120 bisection steps);
  * the physical stopping rule of src/hgto/stopping.py (restated in DeviceStopping and checked against it in
    validation runs).
Only the state solve (S-GPU multigrid PCG, retest/baseline/gmg2d.py) and the array arithmetic run on the GPU. Mesh,
node and DOF numbering of HGTO's linear2d problems equal retest/baseline/fem2d.py; to_problem() asserts it.
The per-update work after the solve (sensitivities, filter pullback, OC bisection, stopping quantities) and the
hierarchy update before it are captured as CUDA graphs, as in retest/baseline/simp_gpu.py.
"""
import math
import time

import numpy as np
import torch
import torch.nn.functional as F

from retest.baseline.fem2d import Problem, element_dofs, element_stiffness, filter_kernel
from retest.baseline.gmg2d import GMGSolver

E0, EMIN, NU = 1.0, 1e-6, 0.3
BISECT_STEPS = 100            # the reference's loop bound
RESTORE_STEPS = 120           # the reference's restore_volume bound


def to_problem(hp):
    """HGTO linear2d Problem -> fem2d.Problem, after checking that the numbering conventions agree."""
    ny, nx = hp.shape
    edof = element_dofs(nx, ny)
    if not np.array_equal(edof[:, 0::2] // 2, np.asarray(hp.cells)):
        raise ValueError("HGTO cell connectivity differs from fem2d's element ordering")
    x = np.asarray(hp.coords)
    if not (np.array_equal(x[:, 0], np.tile(np.arange(nx + 1), ny + 1))
            and np.array_equal(x[:, 1], np.repeat(np.arange(ny + 1), nx + 1))):
        raise ValueError("HGTO node coordinates differ from fem2d's node numbering")
    f = np.asarray(hp.forces, dtype=float)
    if f.ndim == 2:
        if f.shape[1] != 1:
            raise ValueError("single load case expected")
        f = f[:, 0]
    return Problem(hp.name, nx, ny, float(hp.volume_fraction), float(hp.filter_radius),
                   np.asarray(hp.fixed, dtype=np.int64), f, penal=3.0, E0=E0, Emin=EMIN, nu=NU)


class DeviceStopping:
    """src/hgto/stopping.py PhysicalStopping, restated for scalars computed on the device.

    `delta` is max|rho - previous rho|, computed on the device against the rho of the previous observe() call."""

    def __init__(self, window=10, objective_tolerance=1e-3, density_tolerance=5e-3, patience=5,
                 volume_tolerance=1e-7, equilibrium_tolerance=1e-8):
        self.window, self.objective_tolerance, self.density_tolerance = window, objective_tolerance, density_tolerance
        self.patience, self.volume_tolerance, self.equilibrium_tolerance = patience, volume_tolerance, equilibrium_tolerance
        self.values = []
        self.has_previous = False
        self.key = None
        self.stable = 0

    def observe(self, objective, rho_finite, delta, *, parameters, continuation_complete, volume_error, residual):
        key = tuple(parameters)
        valid = bool(math.isfinite(objective) and rho_finite and math.isfinite(residual)
                     and abs(volume_error) <= self.volume_tolerance and residual <= self.equilibrium_tolerance)
        same = self.key == key
        delta = None if not self.has_previous or not same else float(delta)
        eligible = valid and continuation_complete and same
        if not eligible:
            self.values.clear()
            self.stable = 0
        if valid and continuation_complete:
            self.values.append(float(objective))
            self.values = self.values[-self.window:]
        relative = None
        if eligible and len(self.values) == self.window:
            v = np.asarray(self.values)
            relative = float(np.ptp(v) / max(abs(v.mean()), np.finfo(float).tiny))
        satisfied = bool(relative is not None and relative < self.objective_tolerance
                         and delta is not None and delta < self.density_tolerance)
        self.stable = self.stable + 1 if satisfied else 0
        self.has_previous = True
        self.key = key
        return dict(stopping_eligible=eligible, objective_relative_window=relative, maximum_density_change=delta,
                    stable_checks=self.stable, converged=self.stable >= self.patience,
                    volume_error=float(abs(volume_error)), equilibrium_residual=float(residual))


def optimize(prob, betas, penalties, *, max_stage_steps=850, continuation_stage_cap=50, stable_steps=5,
             change_tolerance=5e-3, compliance_tolerance=1e-3, rho_min=1e-3, move=0.2,
             pcg_tol=1e-9, pcg_true_tol=1e-8, pcg_maxit=500, device="cuda", graphs=True,
             reference_stopping=None, started_at=None, log=None):
    """Run the reference SIMP-OC on the GPU. Returns rho (host), history, summary.

    reference_stopping: optional hgto.stopping.PhysicalStopping instance; when given (validation runs only, never
    timed), every observe() is repeated on host copies of rho and must agree with DeviceStopping."""
    started_at = time.perf_counter() if started_at is None else started_at
    if len(betas) != len(penalties) or penalties[-1] != 3.0:
        raise ValueError("one penalty per beta, ending at p = 3")
    dt = torch.float64
    sync = torch.cuda.synchronize if device == "cuda" else (lambda: None)
    graphs = graphs and device == "cuda"
    n, target = prob.nel, prob.volfrac
    KE_np = element_stiffness(NU)
    KE = torch.as_tensor(KE_np, device=device, dtype=dt)
    edof = torch.as_tensor(element_dofs(prob.nelx, prob.nely), device=device)
    kern = torch.as_tensor(filter_kernel(prob.rmin), device=device, dtype=dt)[None, None]
    R = (kern.shape[-1] - 1) // 2
    grid = (1, 1, prob.nely, prob.nelx)

    def conv(v):
        return F.conv2d(v.reshape(grid), kern, padding=R).reshape(-1)

    Hs = conv(torch.ones(n, device=device, dtype=dt))
    f = torch.as_tensor(prob.force, device=device, dtype=dt)
    solver = GMGSolver(prob, KE_np, device=device, dtype=dt, use_graphs=graphs)
    w = torch.full((n,), 1.0 / n, device=device, dtype=dt)          # element-measure weights (unit cells)

    beta_s = torch.zeros((), device=device, dtype=dt)
    pen_s = torch.zeros((), device=device, dtype=dt)
    move_s = torch.zeros((), device=device, dtype=dt)
    x_s = torch.full((n,), target, device=device, dtype=dt)
    rho_s, drho_s = x_s.clone(), x_s.clone()
    cand_s, rhoc_s, prev_s = x_s.clone(), x_s.clone(), x_s.clone()
    u_s = torch.zeros(prob.ndof, device=device, dtype=dt)
    stats_s = torch.zeros(7, device=device, dtype=dt)

    def physical(x, beta):
        bar = conv(x) / Hs
        t = torch.tanh(beta * (bar - 0.5))
        th = torch.tanh(beta / 2)
        den = 2 * th
        return rho_min + (1 - rho_min) * (th + t) / den, (1 - rho_min) * beta * (1 - t * t) / den

    def pre():
        rho, drho = physical(x_s, beta_s)
        rho_s.copy_(rho)
        drho_s.copy_(drho)
        dens = torch.clamp(rho, 0.0, 1.0)
        solver.update(EMIN + (E0 - EMIN) * dens ** pen_s)

    def post():
        Ue = u_s[edof]
        energy = ((Ue @ KE) * Ue).sum(dim=1)
        c = torch.dot(f, u_s)
        dens = torch.clamp(rho_s, 0.0, 1.0)
        grad = -pen_s * (E0 - EMIN) * dens ** (pen_s - 1) * energy
        dc = conv(grad * drho_s / Hs)                                 # A^T (g * d); A = diag(1/Hs) H, H symmetric
        dv = conv(w * drho_s / Hs)
        lower = torch.clamp(x_s - move_s, min=0.0)
        upper = torch.clamp(x_s + move_s, max=1.0)
        scale = torch.sqrt(torch.clamp(-dc, min=0.0) / torch.clamp(dv, min=1e-30))
        left = torch.zeros((), device=device, dtype=dt)
        right = torch.clamp((scale * scale).max(), min=1.0)
        active = torch.ones((), device=device, dtype=torch.bool)
        cand, rhoc = x_s.clone(), rho_s.clone()
        for _ in range(BISECT_STEPS):
            mid = 0.5 * (left + right)
            cc = torch.minimum(torch.maximum(x_s * scale / torch.sqrt(mid), lower), upper)
            rr, _ = physical(cc, beta_s)
            over = torch.dot(w, rr) > target
            left = torch.where(active & over, mid, left)
            right = torch.where(active & ~over, mid, right)
            cand = torch.where(active, cc, cand)
            rhoc = torch.where(active, rr, rhoc)
            active = active & ~((right - left) / (right + left + 1e-30) < 1e-8)
        cand_s.copy_(cand)
        rhoc_s.copy_(rhoc)
        stats_s.copy_(torch.stack([c, torch.dot(w, rho_s), (cand - x_s).abs().max(), (rhoc - rho_s).abs().max(),
                                   (rho_s - prev_s).abs().max(), torch.isfinite(rho_s).all().to(dt),
                                   active.to(dt)]))
        prev_s.copy_(rho_s)

    def restore_volume():
        """The reference's restore_volume at the current stage's beta (beta_s)."""
        z = torch.logit(torch.clamp(x_s, 1e-12, 1 - 1e-12))
        left, right = z.min() - 48.0, z.max() + 48.0
        for _ in range(RESTORE_STEPS):
            shift = 0.5 * (left + right)
            rho, _ = physical(torch.sigmoid(z - shift), beta_s)
            over = torch.dot(w, rho) > target
            left = torch.where(over, shift, left)
            right = torch.where(over, right, shift)
        x_s.copy_(torch.sigmoid(z - 0.5 * (left + right)))

    g_pre = g_post = None
    beta_s.fill_(float(betas[0]))
    pen_s.fill_(float(penalties[0]))
    move_s.fill_(move / max(1.0, float(betas[0])))
    if graphs:
        pre()                                          # allocates the solver's static tensors and its own graphs
        side = torch.cuda.Stream()
        side.wait_stream(torch.cuda.current_stream())
        keep = [t.clone() for t in (x_s, rho_s, drho_s, prev_s)]
        with torch.cuda.stream(side):
            for _ in range(2):
                pre()
                post()
        torch.cuda.current_stream().wait_stream(side)
        g_pre, g_post = torch.cuda.CUDAGraph(), torch.cuda.CUDAGraph()
        with torch.cuda.graph(g_pre):
            pre()
        with torch.cuda.graph(g_post):
            post()
        for t, k in zip((x_s, rho_s, drho_s, prev_s), keep):
            t.copy_(k)
    sync()
    setup_s = time.perf_counter() - started_at

    stopping = DeviceStopping(objective_tolerance=compliance_tolerance, density_tolerance=change_tolerance,
                              patience=stable_steps)
    history, stages = [], []
    pcg_total, fallbacks, max_res = 0, 0, 0.0
    last = len(betas) - 1
    for stage, (beta, pen) in enumerate(zip(betas, penalties)):
        beta, pen = float(beta), float(pen)
        beta_s.fill_(beta)
        pen_s.fill_(pen)
        move_s.fill_(move / max(1.0, beta))
        restore_volume()
        budget = min(max_stage_steps, continuation_stage_cap) if stage < last else max_stage_steps
        for iteration in range(budget):
            if graphs:
                g_pre.replay()
            else:
                pre()
            u, its, res, fb = solver.solve(f, x0=u_s, tol=pcg_tol, true_tol=pcg_true_tol, maxit=pcg_maxit)
            u_s.copy_(u)
            if graphs:
                g_post.replay()
            else:
                post()
            c, vol, dchange, change, delta, finite, active = stats_s.tolist()
            if active:
                raise RuntimeError("OC bisection did not converge within 100 steps")  # the reference would continue
            pcg_total += its
            fallbacks += int(fb)
            max_res = max(max_res, res)
            chk = stopping.observe(c, finite > 0.5, delta, parameters=(pen, beta),
                                   continuation_complete=stage == last, volume_error=vol - target, residual=res)
            if reference_stopping is not None:
                ref = reference_stopping.observe(c, rho_s.cpu().numpy(), parameters=(pen, beta),
                                                 continuation_complete=stage == last, volume_error=vol - target,
                                                 residual=res)
                for k in ("stopping_eligible", "stable_checks", "converged"):
                    if ref[k] != chk[k]:
                        raise RuntimeError(f"stopping rule mismatch at update {len(history)}: {k} {ref[k]} vs {chk[k]}")
            elapsed = time.perf_counter() - started_at
            row = dict(iteration=len(history), stage=stage, beta=beta, penalty=pen, C=c, volume=vol,
                       design_change=dchange, max_density_change=change, elapsed_s=elapsed,
                       equilibrium_residual=res, pcg_iterations=its, fallback=bool(fb))
            row.update(chk)
            history.append(row)
            if log:
                log(row)
            if chk["stable_checks"] >= stable_steps or iteration == budget - 1:
                break
            x_s.copy_(cand_s)
        stages.append(dict(beta=beta, penalty=pen, steps=iteration + 1, converged=chk["stable_checks"] >= stable_steps,
                           stage_budget=budget, continuation_stage=stage < last))
        if stage < last:
            x_s.copy_(cand_s)
    sync()
    elapsed = time.perf_counter() - started_at
    converged = stages[-1]["converged"]
    summary = dict(method="SIMP-OC (GPU port)", C_raw=history[-1]["C"], volume=history[-1]["volume"],
                   target_volume=target, converged=converged, termination="converged" if converged else "max_stage_steps",
                   stages=stages, state_evaluations=len(history), setup_s=setup_s,
                   optimization_s=elapsed - setup_s, pcg_iterations_total=pcg_total, pcg_fallbacks=fallbacks,
                   max_state_residual=max_res, cuda_graphs=graphs)
    return rho_s.cpu().numpy(), history, summary
