"""Run HGTO's own command line, unchanged, in a process pinned to the performance cores.

    python -m retest.hgto_harness.run_hgto_pinned run --config <yaml> --output <new dir> [--method oc] [--threads N]

Arguments go to hgto.cli.main as given. Pinning (tools/pin.py, PIN_PCORES=1) is applied before hgto is imported, so
every thread HGTO or MKL starts inherits it. The applied setting is written to <output>/pinning.json afterwards.
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))


def main():
    from tools.pin import pin_from_env
    pinning = pin_from_env()
    from hgto.cli import main as hgto_main
    argv = sys.argv[1:]
    hgto_main(argv)
    out = pathlib.Path(argv[argv.index("--output") + 1])
    (out / "pinning.json").write_text(json.dumps({"cpu_pinning": pinning, "argv": argv}, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
