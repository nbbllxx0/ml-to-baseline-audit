# P00183 — repairs and choices (census pre-registration §6.2)

1. **Python 3 / TensorFlow 2.** `port.py` makes the working copy `work/` of "CAD code/" at commit 02de10e and patches
   `main_1D.py` only (`work/PATCHES.diff`): `tensorflow.compat.v1` with v2 behaviour disabled; Python 2 integer
   division in tensor shapes and loop counts written as floor division; seeds 20260925 for random, numpy and
   TensorFlow (the original draws its initial training set without a seed); the MATLAB engine is pointed at the working
   folder before `cal_c_1D` runs.
2. **Load vector.** The released `infill_topology_optimization.m` never preallocates `F`; assigning the two load
   entries leaves it 9,882 long, and `F(freedofs)` fails for the 9,922-DOF model ("Index exceeds the number of array
   elements", first L1 attempt, 2026-09-25 09:15). The logged copy (`matlab/infill_logged.m`, made by
   `make_logged.py`) preallocates `F = sparse(2*(nely+1)*(nelx+1),1)`, as the repository's own
   `calculate_compliance.m` does. The released TO function therefore does not run as published; the 100 ground-truth
   designs in `experiment_data/phi_true_1D.mat` were produced by code not in the repository (`infill_1D` is called
   but absent).
3. **Case.** Case 2 (`main_adaptiv.py`) calls `cal_c_high_dim1_3d`, which is not in the repository; case 1 is used.
4. **Training.** Budget clock 08:52:33–09:14:55 (22.4 min, within §6.1): 5 active-learning rounds, 9 training designs,
   final test error 0.944 against the stopping criterion 1 (`train.log`). Checkpoint `model_1D_sample_9`.
5. **Evaluator.** The released `calculate_compliance.m` computes the compliance and then stops at an undefined variable
   (`rho_bar`) in its constraint lines (second L1 attempt, 09:19, after its first TO run finished). The copy
   `matlab/compliance_eval.m` (made by `make_logged.py`; diff `matlab/compliance_eval.diff`) returns the compliance and
   drops the two constraint lines. The compliance computation is unchanged.
