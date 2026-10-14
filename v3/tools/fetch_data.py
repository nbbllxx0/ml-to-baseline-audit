"""Download the third-party data approved for the census (user, 2026-09-25) into v3/runs/, with checksums.

    v3/.venv/census-torch/Scripts/python.exe v3/tools/fetch_data.py

1. P00610: the four CFD result CSVs of Mendeley Data 10.17632/454dsrmdyf.2 (CC BY 4.0), SHA-256 checked, and a
   seeded sample of 100 images (25 from each of CirclePack, EllipsePack, QuadrilateralPack, QSGS; indices drawn with
   numpy default_rng(20260925) from the first 1,000 files each folder lists).
2. P00140: the four pre-trained de-homogenization weight files (data.dtu.dk, figshare article 16902961, CC BY 4.0),
   MD5 checked.
Generic User-Agent, no contact data, 1 s between requests. Existing files with a matching checksum are skipped.
Writes v3/runs/P00610/data/ and v3/runs/P00140/weights/ and a provenance file in each.
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import time
import urllib.request

import numpy as np

V3 = pathlib.Path(__file__).resolve().parents[1]
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
MENDELEY = "https://data.mendeley.com/public-api/datasets/454dsrmdyf/files?folder_id={}&version=2"
FOLDERS = {"CFD Results": "dee18ba4-8874-490a-b50f-6e7b88104eb7", "CirclePack": "cdb03023-f7be-404a-8897-b67ced826649",
           "EllipsePack": "61b83877-0c33-4734-97ca-8915799ec70d",
           "QuadrilateralPack": "73225bb8-6a9e-4841-8bf6-e8723238a2e2", "QSGS": "db273a40-ef57-49a8-9e5d-caa5c1673759"}
FIGSHARE = "https://api.figshare.com/v2/articles/16902961"


def get(url: str) -> bytes:
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=120) as r:
        data = r.read()
    time.sleep(1.0)
    return data


def save(path: pathlib.Path, url: str, algo: str, digest: str | None) -> dict:
    if path.exists() and digest and hashlib.new(algo, path.read_bytes()).hexdigest() == digest:
        return {"file": path.name, "url": url, algo: digest, "status": "present"}
    b = get(url)
    got = hashlib.new(algo, b).hexdigest()
    if digest and got != digest:
        raise SystemExit(f"{algo} mismatch for {path.name}: {got} != {digest}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b)
    return {"file": path.name, "url": url, algo: got, "bytes": len(b), "status": "downloaded"}


def mendeley():
    out = V3 / "runs" / "P00610" / "data"
    prov = []
    for f in json.loads(get(MENDELEY.format(FOLDERS["CFD Results"]))):
        c = f["content_details"]
        prov.append(save(out / "cfd" / f["filename"], c["download_url"], "sha256", c["sha256_hash"]))
    rng = np.random.default_rng(20260925)
    for name in ("CirclePack", "EllipsePack", "QuadrilateralPack", "QSGS"):
        files = sorted(json.loads(get(MENDELEY.format(FOLDERS[name]))), key=lambda f: f["filename"])
        for i in sorted(rng.choice(len(files), 25, replace=False).tolist()):
            f = files[i]
            c = f["content_details"]
            rec = save(out / "images" / name / f["filename"], c["download_url"], "sha256", c["sha256_hash"])
            rec["folder"] = name
            prov.append(rec)
    (out / "PROVENANCE.json").write_text(json.dumps({"source": "Mendeley Data 10.17632/454dsrmdyf.2, CC BY 4.0",
                                                     "files": prov}, indent=1) + "\n", encoding="utf-8")
    print("P00610:", sum(p["status"] == "downloaded" for p in prov), "downloaded,", len(prov), "total")


def figshare():
    """figshare answers scripted file downloads with an empty bot-check response (HTTP 202, 2026-09-25), which this
    script does not try to get around. Download the files in a browser into v3/runs/P00140/weights/; this function
    then only verifies their MD5 against the article record."""
    out = V3 / "runs" / "P00140" / "weights"
    art = json.loads(get(FIGSHARE))
    missing = [f["name"] for f in art["files"]
               if not (out / f["name"]).exists()
               or hashlib.md5((out / f["name"]).read_bytes()).hexdigest() != f["computed_md5"]]
    if missing:
        print("P00140: download manually from", art["url_public_html"], "into", out, "->", missing)
        return
    prov = [save(out / f["name"], f["download_url"], "md5", f["computed_md5"]) for f in art["files"]]
    (out / "PROVENANCE.json").write_text(json.dumps({"source": f"{art['title']}, doi {art['doi']}, "
                                                     f"{art['license']['name']}", "files": prov}, indent=1) + "\n",
                                         encoding="utf-8")
    print("P00140:", len(prov), "weight files")


if __name__ == "__main__":
    mendeley()
    figshare()
