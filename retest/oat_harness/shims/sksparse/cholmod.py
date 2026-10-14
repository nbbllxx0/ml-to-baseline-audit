def cholesky(*args, **kwargs):
    raise RuntimeError("CHOLMOD is unavailable in this environment (scikit-sparse import shim); "
                       "use a non-CHOLMOD pyEDGE solver.")
