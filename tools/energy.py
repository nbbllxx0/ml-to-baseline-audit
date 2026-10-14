"""GPU board-power sampling with nvidia-smi, and energy integration.

    from tools.energy import PowerSampler, idle_power
    idle = idle_power(seconds=5)                       # mean W with nothing running
    with PowerSampler(run_dir / "power.csv") as ps:    # samples every 100 ms
        ... timed work ...
    joules = ps.energy_j()                             # trapezoid over exactly the timed window
    joules_above_idle = ps.energy_j(subtract_w=idle)

Uses the nvidia-smi CLI (no extra Python package). The integrated quantity is `power.draw.instant`: on Ampere and
newer GPUs `power.draw` is a 1 s average (nvidia-smi --help-query-gpu), which lags over windows of a few seconds;
it is logged as a second column only. Each sampler writes <csv>.window.json with the window, so every energy can be
recomputed from files. CPU package energy is not measured on this Windows machine; that limitation is stated in
plan/BASELINE_PREREG.md.
"""
import json
import csv
import datetime as dt
import pathlib
import subprocess
import time

QUERY = "timestamp,power.draw.instant,power.draw,clocks.sm,utilization.gpu,memory.used"


def _parse_ts(text):
    return dt.datetime.strptime(text.strip(), "%Y/%m/%d %H:%M:%S.%f").timestamp()


class PowerSampler:
    def __init__(self, out_csv, interval_ms=100):
        self.out_csv = pathlib.Path(out_csv)
        self.interval_ms = interval_ms
        self.proc = None
        self.t_start = None
        self.t_stop = None

    def __enter__(self):
        self.out_csv.parent.mkdir(parents=True, exist_ok=True)
        self._fh = open(self.out_csv, "w", encoding="utf-8", newline="")
        self.proc = subprocess.Popen(
            ["nvidia-smi", f"--query-gpu={QUERY}", "--format=csv,noheader,nounits", f"-lms={self.interval_ms}"],
            stdout=self._fh, stderr=subprocess.DEVNULL)
        time.sleep(0.5)  # let the first samples arrive before the timed work starts
        self.t_start = time.time()
        return self

    def __exit__(self, *exc):
        self.t_stop = time.time()
        time.sleep(0.3)
        self.proc.terminate()
        self.proc.wait(timeout=10)
        self._fh.close()
        window = {"t_start": self.t_start, "t_stop": self.t_stop, "interval_ms": self.interval_ms, "query": QUERY}
        self.out_csv.with_name(self.out_csv.name + ".window.json").write_text(json.dumps(window), encoding="utf-8")
        return False

    def samples(self):
        rows = []
        with open(self.out_csv, encoding="utf-8") as fh:
            for rec in csv.reader(fh):
                if len(rec) < 2:
                    continue
                try:
                    rows.append((_parse_ts(rec[0]), float(rec[1])))
                except ValueError:
                    continue
        return rows

    def energy_j(self, subtract_w=0.0):
        """Trapezoidal energy (J) of (power - subtract_w) over exactly [t_start, t_stop]."""
        return integrate(self.samples(), self.t_start, self.t_stop, subtract_w)


def integrate(samples, t0, t1, subtract_w=0.0):
    """Trapezoid of (power - subtract_w) over [t0, t1]; power at t0 and t1 is linearly interpolated between the
    neighbouring samples. Returns nan unless samples exist on both sides of the window."""
    pts = sorted(samples)
    if len(pts) < 2 or pts[0][0] > t0 or pts[-1][0] < t1 or t1 <= t0:
        return float("nan")

    def at(t):
        for (ta, pa), (tb, pb) in zip(pts, pts[1:]):
            if ta <= t <= tb:
                return pa if tb == ta else pa + (pb - pa) * (t - ta) / (tb - ta)
        return float("nan")

    seq = [(t0, at(t0))] + [(t, p) for t, p in pts if t0 < t < t1] + [(t1, at(t1))]
    e = 0.0
    for (ta, pa), (tb, pb) in zip(seq, seq[1:]):
        e += 0.5 * (pa + pb - 2.0 * subtract_w) * (tb - ta)
    return e


def idle_power(seconds=5.0, out_csv=None):
    out_csv = out_csv or pathlib.Path("idle_power.csv")
    with PowerSampler(out_csv) as ps:
        time.sleep(seconds)
    vals = [p for t, p in ps.samples() if ps.t_start <= t <= ps.t_stop]
    return sum(vals) / len(vals) if vals else float("nan")
