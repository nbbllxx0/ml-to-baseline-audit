"""Stand-in for torch_sparse_solve (github.com/flaport/torch_sparse_solve), which wraps the SuiteSparse KLU sparse LU
solver as a differentiable PyTorch function and does not build on Windows without SuiteSparse. Repair logged in
v3/runs/P00080/REPAIRS.md.

Same call as VoroTO uses: x = solve(A, b) with A a sparse COO tensor of shape (1, n, n) and b a dense (1, n, m) tensor,
float64. Forward: sparse direct LU solve (SciPy SuperLU instead of KLU). Backward: the adjoint solve, grad_b = A^-T g
and grad_A = -grad_b x^T restricted to the sparsity pattern of A, which is what the original returns.
"""
from __future__ import annotations

import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spla
import torch


class _SparseSolve(torch.autograd.Function):
    @staticmethod
    def forward(ctx, A, b):
        A = A.coalesce()
        idx = A.indices().cpu().numpy()
        vals = A.values().detach().cpu().numpy()
        n = A.shape[1]
        M = sp.csc_matrix((vals, (idx[1], idx[2])), shape=(n, n))
        lu = spla.splu(M)
        x = lu.solve(b[0].detach().cpu().numpy())
        ctx.lu, ctx.idx, ctx.x, ctx.shape = lu, idx, x, A.shape
        return torch.from_numpy(x).to(b.dtype).unsqueeze(0)

    @staticmethod
    def backward(ctx, gx):
        g = gx[0].detach().cpu().numpy()
        gb = ctx.lu.solve(g, trans="T")
        grad_b = torch.from_numpy(gb).to(gx.dtype).unsqueeze(0)
        grad_A = None
        if ctx.needs_input_grad[0]:
            i, j = ctx.idx[1], ctx.idx[2]
            gvals = -(gb[i] * ctx.x[j]).sum(axis=1)
            grad_A = torch.sparse_coo_tensor(torch.from_numpy(ctx.idx), torch.from_numpy(gvals).to(gx.dtype),
                                             ctx.shape)
        return grad_A, grad_b


def solve(A: torch.Tensor, b: torch.Tensor) -> torch.Tensor:
    return _SparseSolve.apply(A, b)
