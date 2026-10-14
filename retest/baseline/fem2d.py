"""Shared 2D plane-stress FE and SIMP ingredients (numpy only).

Conventions (used by every solver so that designs are directly comparable):
  * nelx x nely unit-square bilinear (Q4) elements; y points up.
  * node id  n = iy*(nelx+1) + ix          (ix in [0, nelx], iy in [0, nely])
  * element  e = ey*nelx + ex              (row-major; field arrays reshape to (nely, nelx))
  * element nodes in order BL, BR, TR, TL; element DOFs [2n0, 2n0+1, ..., 2n3, 2n3+1]
  * density filter = top88 ft=2 weights max(0, rmin - d) over |dx|,|dy| <= ceil(rmin)-1
"""
from dataclasses import dataclass, field
import math

import numpy as np


def element_stiffness(nu=0.3, E=1.0):
    """Q4 plane-stress stiffness of a unit square, 2x2 Gauss, node order BL, BR, TR, TL."""
    D = E / (1.0 - nu * nu) * np.array([[1.0, nu, 0.0], [nu, 1.0, 0.0], [0.0, 0.0, (1.0 - nu) / 2.0]])
    xi_n = np.array([-1.0, 1.0, 1.0, -1.0])
    eta_n = np.array([-1.0, -1.0, 1.0, 1.0])
    g = 1.0 / math.sqrt(3.0)
    KE = np.zeros((8, 8))
    for xi in (-g, g):
        for eta in (-g, g):
            dN_dxi = 0.25 * xi_n * (1.0 + eta * eta_n)
            dN_deta = 0.25 * eta_n * (1.0 + xi * xi_n)
            # x = (1+xi)/2, y = (1+eta)/2  ->  d/dx = 2 d/dxi, detJ = 1/4
            dN_dx, dN_dy = 2.0 * dN_dxi, 2.0 * dN_deta
            B = np.zeros((3, 8))
            B[0, 0::2] = dN_dx
            B[1, 1::2] = dN_dy
            B[2, 0::2] = dN_dy
            B[2, 1::2] = dN_dx
            KE += B.T @ D @ B * 0.25
    return KE


def node_id(ix, iy, nelx):
    return iy * (nelx + 1) + ix


def element_dofs(nelx, nely):
    ex, ey = np.meshgrid(np.arange(nelx), np.arange(nely))  # shape (nely, nelx)
    ex, ey = ex.ravel(), ey.ravel()
    n0 = node_id(ex, ey, nelx)
    n1 = node_id(ex + 1, ey, nelx)
    n2 = node_id(ex + 1, ey + 1, nelx)
    n3 = node_id(ex, ey + 1, nelx)
    nodes = np.stack([n0, n1, n2, n3], axis=1)
    edof = np.empty((nelx * nely, 8), dtype=np.int64)
    edof[:, 0::2] = 2 * nodes
    edof[:, 1::2] = 2 * nodes + 1
    return edof


def filter_offsets(rmin):
    """(dx, dy, weight) triples of the top88 density filter."""
    R = int(math.ceil(rmin)) - 1
    out = []
    for dy in range(-R, R + 1):
        for dx in range(-R, R + 1):
            w = rmin - math.sqrt(dx * dx + dy * dy)
            if w > 0.0:
                out.append((dx, dy, w))
    return out


def filter_matrix(nelx, nely, rmin):
    """Sparse H (CSR) and row sums Hs, identical to top88's construction."""
    import scipy.sparse as sp
    ex, ey = np.meshgrid(np.arange(nelx), np.arange(nely))
    ex, ey = ex.ravel(), ey.ravel()
    rows, cols, vals = [], [], []
    for dx, dy, w in filter_offsets(rmin):
        jx, jy = ex + dx, ey + dy
        ok = (jx >= 0) & (jx < nelx) & (jy >= 0) & (jy < nely)
        rows.append((ey * nelx + ex)[ok])
        cols.append((jy * nelx + jx)[ok])
        vals.append(np.full(ok.sum(), w))
    H = sp.csr_matrix((np.concatenate(vals), (np.concatenate(rows), np.concatenate(cols))),
                      shape=(nelx * nely, nelx * nely))
    Hs = np.asarray(H.sum(axis=1)).ravel()
    return H, Hs


def filter_kernel(rmin):
    """Dense 2D kernel equal to the filter weights (for convolution on a (nely, nelx) grid)."""
    R = int(math.ceil(rmin)) - 1
    K = np.zeros((2 * R + 1, 2 * R + 1))
    for dx, dy, w in filter_offsets(rmin):
        K[dy + R, dx + R] = w
    return K


@dataclass
class Problem:
    name: str
    nelx: int
    nely: int
    volfrac: float
    rmin: float
    fixed: np.ndarray            # fixed global DOF indices
    force: np.ndarray            # global load vector
    penal: float = 3.0
    E0: float = 1.0
    Emin: float = 1e-9
    nu: float = 0.3
    meta: dict = field(default_factory=dict)

    @property
    def ndof(self):
        return 2 * (self.nelx + 1) * (self.nely + 1)

    @property
    def nel(self):
        return self.nelx * self.nely

    def free_mask(self):
        m = np.ones(self.ndof)
        m[self.fixed] = 0.0
        return m


def cantilever(n, volfrac=0.4, rmin=None):
    """P1: left edge clamped, unit downward force at the right-edge mid-node (n even)."""
    nelx = nely = n
    rmin = 1.5 * n / 64 if rmin is None else rmin
    left = node_id(np.zeros(nely + 1, dtype=np.int64), np.arange(nely + 1), nelx)
    fixed = np.sort(np.concatenate([2 * left, 2 * left + 1]))
    f = np.zeros(2 * (nelx + 1) * (nely + 1))
    f[2 * node_id(nelx, nely // 2, nelx) + 1] = -1.0
    return Problem("P1_cantilever", nelx, nely, volfrac, rmin, fixed, f)


def mbb(n, volfrac=0.5, rmin=None):
    """P2: MBB half-beam; left edge u_x = 0, bottom-right node u_y = 0, unit downward force top-left."""
    nelx = nely = n
    rmin = 1.5 * n / 64 if rmin is None else rmin
    left = node_id(np.zeros(nely + 1, dtype=np.int64), np.arange(nely + 1), nelx)
    br = node_id(nelx, 0, nelx)
    fixed = np.sort(np.concatenate([2 * left, [2 * br + 1]]))
    f = np.zeros(2 * (nelx + 1) * (nely + 1))
    f[2 * node_id(0, nely, nelx) + 1] = -1.0
    return Problem("P2_mbb", nelx, nely, volfrac, rmin, fixed, f)


PROBLEMS = {"P1": cantilever, "P2": mbb}
