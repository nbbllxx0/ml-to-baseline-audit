"""The project's manifest tool (tools/manifest.py), writing to v3/evidence/MANIFEST.sha256 instead of evidence/.

    python v3/tools/manifest_v3.py freeze --label L paths...
    python v3/tools/manifest_v3.py verify

Paths stay relative to the project root, so entries read the same as in the v2 manifest.
"""
import pathlib
import sys

V3 = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(V3.parent / "tools"))
import manifest  # noqa: E402

manifest.MANIFEST = V3 / "evidence" / "MANIFEST.sha256"

if __name__ == "__main__":
    manifest.main()
