"""GPU SIMP loop (torch, float64) with the matrix-free Galerkin multigrid PCG solver (S-GPU).

Same formulation as simp_cpu.py (fem2d.py conventions); the density filter is the same weights applied
as a convolution on the (nely, nelx) element grid with zero padding and row-sum normalisation.

graphs=True captures (a) E -> multigrid hierarchy update and (b) sensitivities -> filter -> OC bisection ->
new design as CUDA graphs. The OC bisection is top88's sequential bisection run on the device for a fixed
budget of steps with updates frozen once top88's stopping test holds, so its midpoints and final xnew are
the same as the host loop's. graphs=False runs the same arithmetic eagerly (host-loop bisection); the two
paths are compared in tests/run_tests.py.
"""
import time

import numpy as np
import torch
import torch.nn.functional as F

from .fem2d import element_dofs, element_stiffness, filter_kernel
from .gmg2d import GMGSolver

BISECT_STEPS = 100   # >= log2(5e11 / lambda) for lambda >= 4e-19; convergence is asserted every iteration


def run(prob, iters=150, omega=0.6, nu_pre=2, nu_post=2, tol=1e-8, true_tol=1e-7, log=None,
        device="cuda", graphs=True, return_x=False):
    dt = torch.float64
    sync = torch.cuda.synchronize if device == "cuda" else (lambda: None)
    graphs = graphs and device == "cuda"
    t_setup = time.perf_counter()
    KE_np = element_stiffness(prob.nu)
    KE = torch.as_tensor(KE_np, device=device, dtype=dt)
    edof = torch.as_tensor(element_dofs(prob.nelx, prob.nely), device=device)
    kern = torch.as_tensor(filter_kernel(prob.rmin), device=device, dtype=dt)[None, None]
    R = (kern.shape[-1] - 1) // 2
    grid = (1, 1, prob.nely, prob.nelx)

    def conv(v):
        return F.conv2d(v.reshape(grid), kern, padding=R).reshape(-1)

    Hs = conv(torch.ones(prob.nel, device=device, dtype=dt))
    dv = conv(1.0 / Hs)
    solver = GMGSolver(prob, KE_np, device=device, dtype=dt, omega=omega, nu_pre=nu_pre, nu_post=nu_post,
                       use_graphs=graphs)
    f = torch.as_tensor(prob.force, device=device, dtype=dt)
    vtarget = prob.volfrac * prob.nel
    move = 0.2
    # static state (updated in place so captured graphs stay valid)
    x_s = torch.full((prob.nel,), prob.volfrac, device=device, dtype=dt)
    xPhys_s = x_s.clone()
    u_s = torch.zeros(prob.ndof, device=device, dtype=dt)
    c_s = torch.zeros((), device=device, dtype=dt)
    change_s = torch.zeros((), device=device, dtype=dt)
    active_s = torch.zeros((), device=device, dtype=torch.bool)

    def pre():
        solver.update(prob.Emin + xPhys_s ** prob.penal * (prob.E0 - prob.Emin))

    def post_device():
        Ue = u_s[edof]
        ce = ((Ue @ KE) * Ue).sum(dim=1)
        c_s.copy_(torch.dot(solver.E, ce))
        dc = -prob.penal * (prob.E0 - prob.Emin) * xPhys_s ** (prob.penal - 1) * ce
        # Clamp at 0: a rounding-level positive sensitivity (e.g. +3e-16 on OpenTO problem 1974, 256²) would make
        # sqrt(q/lmid) NaN and stall the bisection. A no-op whenever all sensitivities are <= 0 (2026-09-25 fix).
        q = torch.clamp(-conv(dc / Hs) / dv, min=0.0)
        l1 = torch.zeros((), device=device, dtype=dt)
        l2 = torch.full((), 1e9, device=device, dtype=dt)
        xnew = x_s.clone()
        active = torch.ones((), device=device, dtype=torch.bool)
        for _ in range(BISECT_STEPS):
            active = (l2 - l1) / (l1 + l2) > 1e-3
            lmid = 0.5 * (l2 + l1)
            t = x_s * torch.sqrt(q / lmid)
            xc = torch.clamp(torch.maximum(x_s - move, torch.clamp(torch.minimum(x_s + move, t), max=1.0)), min=0.0)
            over = torch.dot(dv, xc) > vtarget
            l1 = torch.where(active & over, lmid, l1)
            l2 = torch.where(active & ~over, lmid, l2)
            xnew = torch.where(active, xc, xnew)
        active_s.copy_(active)
        change_s.copy_((xnew - x_s).abs().max())
        xPhys_s.copy_(conv(xnew) / Hs)
        x_s.copy_(xnew)

    def post_eager():
        Ue = u_s[edof]
        ce = ((Ue @ KE) * Ue).sum(dim=1)
        c_s.copy_(torch.dot(solver.E, ce))
        dc = -prob.penal * (prob.E0 - prob.Emin) * xPhys_s ** (prob.penal - 1) * ce
        # Clamp at 0: a rounding-level positive sensitivity (e.g. +3e-16 on OpenTO problem 1974, 256²) would make
        # sqrt(q/lmid) NaN and stall the bisection. A no-op whenever all sensitivities are <= 0 (2026-09-25 fix).
        q = torch.clamp(-conv(dc / Hs) / dv, min=0.0)
        l1, l2 = 0.0, 1e9
        while (l2 - l1) / (l1 + l2) > 1e-3:
            lmid = 0.5 * (l2 + l1)
            t = x_s * torch.sqrt(q / lmid)
            xnew = torch.clamp(torch.maximum(x_s - move, torch.clamp(torch.minimum(x_s + move, t), max=1.0)), min=0.0)
            if torch.dot(dv, xnew).item() > vtarget:
                l1 = lmid
            else:
                l2 = lmid
        active_s.fill_(False)
        change_s.copy_((xnew - x_s).abs().max())
        xPhys_s.copy_(conv(xnew) / Hs)
        x_s.copy_(xnew)

    g_pre = g_post = None
    if graphs:
        pre()                                   # first update allocates the solver's static tensors
        side = torch.cuda.Stream()
        side.wait_stream(torch.cuda.current_stream())
        x0, p0 = x_s.clone(), xPhys_s.clone()
        with torch.cuda.stream(side):
            for _ in range(2):
                pre()
                post_device()
                x_s.copy_(x0)
                xPhys_s.copy_(p0)
        torch.cuda.current_stream().wait_stream(side)
        g_pre, g_post = torch.cuda.CUDAGraph(), torch.cuda.CUDAGraph()
        with torch.cuda.graph(g_pre):
            pre()
        with torch.cuda.graph(g_post):
            post_device()
        x_s.copy_(x0)
        xPhys_s.copy_(p0)
    sync()
    t_setup = time.perf_counter() - t_setup

    rec = {k: [] for k in ("c", "vol", "change", "t_iter", "t_solve", "t_update", "pcg_its", "true_res", "fallback")}
    for it in range(iters):
        sync()
        t0 = time.perf_counter()
        if graphs:
            g_pre.replay()
        else:
            pre()
        sync()
        t1 = time.perf_counter()
        u, its, tres, fb = solver.solve(f, x0=u_s, tol=tol, true_tol=true_tol)
        u_s.copy_(u)
        sync()
        t2 = time.perf_counter()
        if graphs:
            g_post.replay()
        else:
            post_eager()
        sync()
        t3 = time.perf_counter()
        if bool(active_s.item()):
            raise RuntimeError("OC bisection did not converge within BISECT_STEPS")
        rec["c"].append(c_s.item())
        rec["vol"].append(xPhys_s.mean().item())
        rec["change"].append(change_s.item())
        rec["t_iter"].append(t3 - t0)
        rec["t_solve"].append(t2 - t1)
        rec["t_update"].append(t1 - t0)
        rec["pcg_its"].append(its)
        rec["true_res"].append(tres)
        rec["fallback"].append(bool(fb))
        if log:
            log(it, rec["c"][-1], rec["change"][-1], t3 - t0)
    rec["t_setup"] = t_setup
    rec["t_total"] = float(np.sum(rec["t_iter"]))
    if return_x:
        return rec, xPhys_s.cpu().numpy(), u_s.cpu().numpy(), x_s.cpu().numpy()
    return rec, xPhys_s.cpu().numpy(), u_s.cpu().numpy()
