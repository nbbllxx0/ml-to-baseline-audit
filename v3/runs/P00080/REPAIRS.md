# P00080 — repairs and choices (census pre-registration §6.2)

1. **torch_sparse_solve.** VoroTO's `solver.py` imports `solve` from torch_sparse_solve, a C++ extension around the
   SuiteSparse KLU sparse LU solver that does not build on Windows without SuiteSparse. `shim/torch_sparse_solve.py`
   provides the same call: a sparse direct LU solve (SciPy SuperLU) with the adjoint backward pass. Checked against
   dense PyTorch autograd on a random 6×6 system: solution, b-gradient and A-gradient agree to below 2e-17. Both are
   exact direct solvers; the macro problem (40×20 elements) is small, so the solver swap has no material effect on time.
2. **Notebooks.** The dataset, training and optimization code is in three notebooks. `run_notebook.py` runs their
   code cells unchanged, in order, from a working copy of the repository files (`work/`); plots are not displayed.
3. **Budget clock.** Data generation plus training count against the 1 GPU-hour budget (§6.1) as wall time. VoroTO
   trains on the CPU (the notebooks never move data to a GPU).
