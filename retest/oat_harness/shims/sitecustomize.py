"""Compatibility shim for running OAT's pyEDGE (written for an older CuPy) under CuPy 14 on Windows.

torch (bundled CUDA 12.8) and CuPy 14 (system CUDA 13.0) cannot share one process here: CUDA 13.0 ships
cusparse64_12.dll / cusolver64_12.dll under the same file names as torch's CUDA 12.8 copies. The harness
therefore runs two kinds of process:
  * OAT_CUPY=1 : pyEDGE (CuPy only; pyEDGE never imports torch). This shim adds the CUDA 13.0 DLL folder,
                 restores the removed alias cupy.sparse -> cupyx.scipy.sparse (it was a pure alias), and maps the
                 Krylov keyword tol= to rtol= (CuPy 14 rename).
  * otherwise  : OAT model inference (torch only); the shim does nothing.
No OAT file is modified. Recorded as a deviation in plan/BASELINE_PREREG.md section 9.
"""
import os

if os.environ.get("OAT_CUPY") == "1":
    cuda13 = os.path.join(os.environ.get("CUDA_PATH", ""), "bin", "x64")
    if os.path.isdir(cuda13):
        os.add_dll_directory(cuda13)
    import cupy
    import cupyx.scipy.sparse
    import cupyx.scipy.sparse.linalg  # noqa: F401
    if not hasattr(cupy, "sparse"):
        cupy.sparse = cupyx.scipy.sparse
    # CuPy 14 renamed the Krylov keyword `tol` to `rtol` (SciPy >= 1.14 API). pyEDGE passes `tol=`; translate it
    # before pyEDGE imports these names. Semantics unchanged: relative residual tolerance.
    import functools
    import cupyx.scipy.sparse.linalg as _spla

    def _tol_compat(fn):
        @functools.wraps(fn)
        def wrapper(*a, **k):
            if "tol" in k and "rtol" not in k:
                k["rtol"] = k.pop("tol")
            return fn(*a, **k)
        return wrapper

    for _name in ("cg", "gmres", "cgs", "minres"):
        if hasattr(_spla, _name):
            setattr(_spla, _name, _tol_compat(getattr(_spla, _name)))
