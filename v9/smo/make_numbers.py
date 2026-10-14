"""Generate TeX result macros from the author guide's frozen number registry."""
from pathlib import Path
import json
import re

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
REGISTRIES = (
    ROOT / "evidence" / "numbers.json",
    ROOT / "v3" / "evidence" / "numbers_v3.json",
    ROOT / "v4" / "evidence" / "numbers_v4.json",
    HERE / "numbers_review.json",          # values added after the strict review; written by make_review_numbers.py
    HERE / "numbers_xprov.json",           # v6: post hoc cross-provider check; written by make_xprov_numbers.py
    HERE / "numbers_review2.json",         # values added after the 2026-09-29 review; written by make_review2_numbers.py
)
OUT = HERE / "numbers.tex"
ARXIV_OUT = HERE.parent / "arxiv" / "numbers.tex"


def tex_escape(value: str) -> str:
    escaped = (
        value.replace("\\", r"\textbackslash{}")
        .replace("%", r"\%")
        .replace("&", r"\&")
        .replace("#", r"\#")
        .replace("_", r"\_")
    )
    escaped = escaped.replace("κ", r"\ensuremath{\kappa}")
    escaped = escaped.replace("×", r"\texttimes{}")
    escaped = escaped.replace("–", "--")
    superscripts = str.maketrans("⁻⁰¹²³⁴⁵⁶⁷⁸⁹", "-0123456789")
    return re.sub(
        r"([0-9]+)([⁻⁰¹²³⁴⁵⁶⁷⁸⁹]+)",
        lambda match: (
            r"\ensuremath{" + match.group(1) + "^{" +
            match.group(2).translate(superscripts) + "}}"
        ),
        escaped,
    )


entries = {}
for registry in REGISTRIES:
    if not registry.exists():
        raise SystemExit(f"Required number registry is missing: {registry}")
    for key, record in json.loads(registry.read_text(encoding="utf-8")).items():
        if not re.fullmatch(r"N\d+", key):
            raise SystemExit(f"Invalid number token in {registry}: {key}")
        value = tex_escape(record["text"])
        if key in entries and entries[key] != value:
            raise SystemExit(f"Conflicting number token {key} in {registry}")
        entries[key] = value

# Ship only the values the manuscript prints: the source is public on arXiv, and unused registry values have no
# meaning outside the evidence files.
used = set()
for tex in (HERE / "manuscript.tex", HERE.parent / "arxiv" / "manuscript.tex"):
    used |= set(re.findall(r"\\N\{(N\d+)\}", tex.read_text(encoding="utf-8")))
missing = sorted(used - set(entries))
if missing:
    raise SystemExit("Tokens used in the manuscript but not registered: " + " ".join(missing))
generated = (
    "% Result values used in the manuscript.\n"
    + "\n".join(
        rf"\expandafter\def\csname result{key}\endcsname{{{value}}}"
        for key, value in sorted(entries.items()) if key in used
    )
    + "\n"
)
OUT.write_text(generated, encoding="utf-8")
ARXIV_OUT.write_text(generated, encoding="utf-8")
print(f"Wrote both number files ({len(used)} of {len(entries)} registered result macros)")
