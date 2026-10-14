"""P00610 L2 strong baseline: the article-era Keff-CFD finite-volume system, solved by a sparse direct method.

The matrix and right-hand side follow DiscretizeMatrixCD2D in Keff-CFD commit 720be71 (keff2D.h, lines 438-538):
cell-centred finite volumes on the unit square, harmonic-mean face conductivities, Dirichlet temperatures TL (left)
and TR (right), adiabatic top and bottom. k_eff follows keff2D.cpp (lines 150-169): the mean of the left and right
boundary heat flows divided by (TR - TL). Only the solver changes: instead of Gauss-Seidel or TDMA line sweeps to a
relative k_eff change of 1e-5, the linear system is solved to round-off by SuperLU (scipy.sparse.linalg.splu, one
thread). Pixel >= 150 is solid (k_s), else fluid (k_f), as in keff2D.cpp.

    from strong import keff_direct
"""
from __future__ import annotations

import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spla


def conductivity(img: np.ndarray, ks: float, kf: float = 1.0) -> np.ndarray:
    return np.where(img < 150, kf, ks).astype(np.float64)


def system(K: np.ndarray, tL: float = 0.0, tR: float = 1.0):
    """Five-point matrix A (CSR) and right-hand side b, as DiscretizeMatrixCD2D builds them (row-major, i = row)."""
    ny, nx = K.shape
    dx, dy = 1.0 / nx, 1.0 / ny
    xc = (np.arange(nx) + 0.5) * dx
    yc = (np.arange(ny) + 0.5) * dy
    hm = lambda a, c: 2.0 / (1.0 / a + 1.0 / c)  # weighted harmonic mean with equal weights
    idx = np.arange(nx * ny).reshape(ny, nx)
    diag = np.zeros((ny, nx))
    b = np.zeros((ny, nx))
    rows, cols, vals = [], [], []
    # east-west faces (interior): coefficient ke*dy/dxe with dxe = dx
    kx = hm(K[:, :-1], K[:, 1:])
    cx = kx * dy / (xc[1] - xc[0])
    diag[:, :-1] += cx
    diag[:, 1:] += cx
    rows += [idx[:, :-1].ravel(), idx[:, 1:].ravel()]
    cols += [idx[:, 1:].ravel(), idx[:, :-1].ravel()]
    vals += [-cx.ravel(), -cx.ravel()]
    # left and right boundaries: kw*dy/xc[0] and ke*dy/(1 - xc[-1]) with the cell's own conductivity
    cl = K[:, 0] * dy / xc[0]
    cr = K[:, -1] * dy / (1.0 - xc[-1])
    diag[:, 0] += cl
    diag[:, -1] += cr
    b[:, 0] += tL * cl
    b[:, -1] += tR * cr
    # north-south faces (interior)
    ky = hm(K[:-1, :], K[1:, :])
    cy = ky * dx / (yc[1] - yc[0])
    diag[:-1, :] += cy
    diag[1:, :] += cy
    rows += [idx[:-1, :].ravel(), idx[1:, :].ravel()]
    cols += [idx[1:, :].ravel(), idx[:-1, :].ravel()]
    vals += [-cy.ravel(), -cy.ravel()]
    rows.append(idx.ravel()); cols.append(idx.ravel()); vals.append(diag.ravel())
    A = sp.csr_matrix((np.concatenate(vals), (np.concatenate(rows), np.concatenate(cols))), shape=(nx * ny, nx * ny))
    return A, b.ravel(), xc


def keff_from_T(T: np.ndarray, K: np.ndarray, xc: np.ndarray, tL: float = 0.0, tR: float = 1.0) -> float:
    ny, nx = K.shape
    dy = 1.0 / ny
    T = T.reshape(ny, nx)
    QL = K[:, 0] * dy * (T[:, 0] - tL) / xc[0]
    QR = K[:, -1] * dy * (tR - T[:, -1]) / (1.0 - xc[-1])
    return float((QL.sum() + QR.sum()) / 2.0 / (tR - tL))


def keff_direct(img: np.ndarray, ks: float, kf: float = 1.0) -> float:
    K = conductivity(img, ks, kf)
    A, b, xc = system(K)
    T = spla.splu(A.tocsc(), permc_spec="COLAMD").solve(b)
    return keff_from_T(T, K, xc)
