"""P00610 L0/L1 check: does the article-era Keff-CFD (commit 720be71) reproduce the published k_eff on the article's
own images?

    v3/.venv/census-torch/Scripts/python.exe v3/runs/P00610/validate.py

For the 100 sampled images (data/images/, see v3/tools/fetch_data.py) and the four conductivity ratios, runs both
solver builds (build/keff2D_gs.exe, build/keff2D_tdma.exe) with the released input defaults (Convergence 1e-5,
MaxIter 500000, TL 0, TR 1, kf 1), one core each, 10 jobs in parallel (not a timed run). Compares k_eff with the
published value in data/cfd/Keff_130k_*.csv. Row of an original image i: CirclePack i, EllipsePack 40000 + i,
QuadrilateralPack 80000 + i, QSGS 120000 + i (dataset description: each pack is followed by its three transformed
copies; QSGS is last and untransformed). Writes validate/results.csv and validate/summary.json.
"""
from __future__ import annotations

import concurrent.futures as cf
import csv
import json
import pathlib
import statistics
import subprocess
import tempfile

from PIL import Image

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "validate"
RATIOS = {10.0: "Keff_130k_10p.csv", 50.0: "Keff_130k_50p.csv", 100.0: "Keff_130k_100p.csv", 341.7: "Keff_130k_Al.csv"}
OFFSET = {"CirclePack": 0, "EllipsePack": 40000, "QuadrilateralPack": 80000, "QSGS": 120000}
INPUT = """Input File:
ks: {ks}
kf: 1
MeshAmpX: 1
MeshAmpY: 1
InputName: img.png
TR: 1
TL: 0
OutputName: out.csv
printTMap: 0
TMapName: T.csv
printQMap: 0
QMapName: Q.csv
Convergence: 0.00001
MaxIter: 500000
Verbose: 0
NumCores: 1
MeshFlag: 0
MaxMesh: 10
RunBatch: 0
NumImages: 1
"""


def published() -> dict[float, list[float]]:
    out = {}
    for ks, name in RATIOS.items():
        rows = list(csv.reader(open(HERE / "data" / "cfd" / name, encoding="utf-8")))
        # Keff_130k_10p/50p/Al start with a header ("k_eff" or "keff"); Keff_130k_100p has none. All have 130,000 values.
        vals = [float(r[0]) for r in rows if r and r[0] not in ("k_eff", "keff")]
        assert len(vals) == 130000, (name, len(vals))
        out[ks] = vals
    return out


def run(solver: str, image: pathlib.Path, ks: float) -> dict:
    with tempfile.TemporaryDirectory(dir=OUT) as d:
        d = pathlib.Path(d)
        # The solver accepts one-channel images only; 75 of the 100 dataset JPEGs are RGB with equal channels.
        # Repair (REPAIRS.md 4): convert to 8-bit grayscale and save losslessly as PNG.
        Image.open(image).convert("L").save(d / "img.png")
        (d / "input.txt").write_text(INPUT.format(ks=ks), encoding="ascii")
        pr = subprocess.run([str(HERE / "build" / f"keff2D_{solver}.exe")], cwd=d, capture_output=True, text=True)
        if pr.returncode != 0:
            raise RuntimeError(f"{solver} {image.name} ks={ks}: exit {pr.returncode}: {pr.stdout[-300:]}")
        row = next(csv.reader(open(d / "out.csv")))
    return {"keff": float(row[0]), "QL": float(row[1]), "QR": float(row[2]), "iter": int(row[3]),
            "porosity": float(row[9]), "time_s": float(row[14])}


def main():
    OUT.mkdir(exist_ok=True)
    pub = published()
    counts = {ks: len(v) for ks, v in pub.items()}
    images = sorted((HERE / "data" / "images").glob("*/*.jpg"))
    jobs = [(s, im, ks) for s in ("tdma", "gs") for im in images for ks in RATIOS]
    rows = []
    with cf.ThreadPoolExecutor(max_workers=10) as ex:
        futs = {ex.submit(run, *j): j for j in jobs}
        for f in cf.as_completed(futs):
            s, im, ks = futs[f]
            r = f.result()
            idx = OFFSET[im.parent.name] + int(im.stem)
            p = pub[ks][idx]
            rows.append({"solver": s, "folder": im.parent.name, "image": im.name, "row": idx, "ks": ks,
                         "keff_published": p, "rel_diff": (r["keff"] - p) / p, **r})
    rows.sort(key=lambda r: (r["solver"], r["ks"], r["folder"], r["image"]))
    with open(OUT / "results.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    summary = {"published_rows_per_ratio": counts, "images": len(images)}
    for s in ("tdma", "gs"):
        for ks in RATIOS:
            sel = [r for r in rows if r["solver"] == s and r["ks"] == ks]
            ad = [abs(r["rel_diff"]) for r in sel]
            summary[f"{s}_ks{ks}"] = {"n": len(sel), "median_abs_rel_diff": statistics.median(ad), "max_abs_rel_diff": max(ad),
                                      "median_iter": statistics.median(r["iter"] for r in sel),
                                      "median_time_s_untimed": statistics.median(r["time_s"] for r in sel)}
    (OUT / "summary.json").write_text(json.dumps(summary, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
