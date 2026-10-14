"""Import-only shim for scikit-sparse (no Windows wheel). Lets pyEDGE import; any CHOLMOD use raises.
Deviation recorded in plan/BASELINE_PREREG.md section 9 (2026-09-24). The OAT code paths used here
(pyEDGE CUDA SPSOLVE / CG / MultiGrid) never call CHOLMOD."""
