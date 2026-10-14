"""Flag possible duplicates that the exact keys of build_pool.py miss (retitled journal versions of preprints).

    python -m audit.pool.dedup_flags

A pair is flagged when the title token sets have Jaccard similarity >= 0.6 and the two records share at least one
author surname. Flags are advisory: screening proceeds as usual, and full-text coding decides (FT-DUPLICATE,
plan/PROTOCOL.md §4). Writes audit/pool/possible_duplicates.csv (later pid, earlier pid, similarity, titles).
"""
import csv
import pathlib
import re
import unicodedata

ROOT = pathlib.Path(__file__).resolve().parents[2]
STOP = {"a", "an", "the", "of", "for", "and", "in", "on", "with", "via", "using", "to", "by", "based", "from", "its"}
AUTHOR_SPLIT = re.compile(r";|,|\band\b")


def tokens(title):
    return {w for w in re.sub(r"[^a-z0-9]+", " ", title.lower()).split() if w not in STOP and len(w) > 1}


def surnames(authors):
    """Last names, accent-folded; handles "A; B" (pool) and "A, B, and C." (bibliography) author strings."""
    folded = unicodedata.normalize("NFKD", authors).encode("ascii", "ignore").decode()
    out = set()
    for part in AUTHOR_SPLIT.split(folded):
        words = part.strip().split()
        if words:
            name = re.sub(r"[^a-z-]", "", words[-1].lower())
            if name:
                out.add(name)
    return out


def main():
    csv.field_size_limit(10 ** 9)
    rows = list(csv.DictReader(open(ROOT / "audit/pool/pool.csv", encoding="utf-8")))
    toks = [tokens(r["title"]) for r in rows]
    names = [surnames(r["authors"]) for r in rows]
    flags = []
    for j in range(len(rows)):
        if not toks[j]:
            continue
        for i in range(j):
            if not toks[i] or not (names[i] & names[j]):
                continue
            sim = len(toks[i] & toks[j]) / len(toks[i] | toks[j])
            if sim >= 0.6:
                flags.append({"pid": rows[j]["pid"], "possible_duplicate_of": rows[i]["pid"], "jaccard": f"{sim:.2f}",
                              "title": rows[j]["title"], "title_earlier": rows[i]["title"]})
    with open(ROOT / "audit/pool/possible_duplicates.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["pid", "possible_duplicate_of", "jaccard", "title", "title_earlier"])
        w.writeheader()
        w.writerows(flags)
    print(f"{len(flags)} possible duplicate pairs -> audit/pool/possible_duplicates.csv")


if __name__ == "__main__":
    main()
