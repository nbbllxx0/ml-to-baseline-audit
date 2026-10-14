"""Full-text exclusion codes (audit/schema/screening_codes.md, second table) and the mapping of legacy prefill labels.

    from analysis.codes import ft_code
    ft_code("FT-ML-only")                               # -> "FT-MLONLY"
    ft_code("FT-DOMAIN (electrical conduction ...)")    # -> "FT-DOMAIN"

An unknown label raises ValueError, so the record is recoded instead of the analysis guessing.
"""
import re

FT_CODES = ("FT-DUPLICATE", "FT-SCOPE", "FT-TYPE", "FT-DOMAIN", "FT-NOML", "FT-FORWARD", "FT-MLONLY",
            "FT-NOBASELINE", "FT-OTHER")
LEGACY = {"FT-NOCOMPARISON": "FT-NOBASELINE"}      # keys after upper-casing and removing inner hyphens


def ft_code(reason):
    m = re.match(r"\s*FT-([A-Za-z-]+)", reason or "")
    if not m:
        raise ValueError(f"not a full-text exclusion code: {reason!r}")
    code = "FT-" + m.group(1).replace("-", "").upper()
    code = LEGACY.get(code, code)
    if code not in FT_CODES:
        raise ValueError(f"unknown full-text exclusion code {code!r} (from {reason!r}); recode it per screening_codes.md")
    return code
