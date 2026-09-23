"""C11R -- the committed, reproducible NON-TARGET cost measurement (review round 2, erratum E12).

WHY THIS MODULE EXISTS. Revision 2's policy froze per-box-panel cost constants that it called
pessimistic, citing a measurement (2bfbe5a3) that is in no commit. The second reviewer measured
them OPTIMISTIC -- the live cost was 1.073x the frozen one at 64 panels -- which put the chosen
configuration at about 99.6% of the cap. A cost model the policy depends on must be an artifact:
committed, reproducible, bound to the code and host that produced it, and carrying its raw
observations so every derived constant can be recomputed from them.

WHAT IT MEASURES, AND WHERE. Only the NON-TARGET block NT = [5/2, 5/2 + 108337/1250000] (above cell
309, in no m=5 cell, with exactly cell 306's width). For each panel count it runs, under ONE Phi
cache as Phase 14 does, exactly the per-box operations Phase 14 performs:
  data pass      box_upper_coeffs + box_lower_coeffs
  certification  for K_e and Khat_e: poly_eval_iv + kernel_box_upper_iv (the body of the reviewed
                 supersolution_margin_iv); for the sub-solution: h1_box_lower + kernel_box_lower_iv
                 + poly_eval_iv (the body of subsolution_margin_iv)
on a deterministic box sample, and the full pointwise stage (every state of the 15x15 grid).
The weights are manufactured; no certified value is produced or recorded.

SEQUENTIAL. It refuses to start, and refuses to write, if any other campaign worker is running:
the round-2 constants were taken while a validation job ran alongside. REVISION 2 (round 4, errata
E26/E27): the check now uses the revision-2 detector (code/c11r_procs.py), which sees the
framework build of Python this host runs; the revision-1 detector could not, so the round-3
artifact's "sequential" fields were vacuous. The detector is sampled before the measurement,
between every stage, and after it, and every sample is recorded.

DERIVATION (mechanical, in `derive`): per panel count, the per-box-panel constant is the MAXIMUM
over sampled boxes of (data + certification seconds) / (P + 1); the pointwise constant is the
measured total. The policy multiplies by a safety factor it declares itself.
"""
from __future__ import annotations

import os
import platform
import resource
import subprocess
import sys
import time
from fractions import Fraction as F

import pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import c11r_boxdata as BD
import c11r_common as C
import c11r_idrift as I
import c11r_procs as PR

X, G = I.X, I.G

W = F(108337, 1250000)                                   # cell 306's block width, exact
NT = I.Blk(F(5, 2), F(5, 2) + W)                          # the non-target block
PANELS = (32, 64, 128)
SCREEN_N = 15
# the three box GEOMETRIES review round 1 used as worst cases (coordinates only; no value), plus
# two deterministic boxes from each of the depth-4 and depth-5 covers
REVIEW_BOXES = ((F(0), F(5, 16), F(0), F(5, 16)), (F(0), F(5, 16), F(15, 16), F(5, 4)),
                (F(5, 2), F(45, 16), F(0), F(5, 16)))
W_K = {(0, 0): F(12), (0, 1): F(-3, 2)}                  # manufactured weights, NT only
W_H = {(0, 0): F(8), (0, 1): F(-1)}
U_D = {(0, 0): F(1, 2), (0, 1): F(1, 20)}


def sample_boxes() -> list[tuple]:
    out = list(REVIEW_BOXES)
    for depth in (4, 5):
        cov = X.cover(depth)
        for k in (1, 2):
            out.append(tuple(cov[(k * len(cov)) // 3]))
    return out


def _rss_mb() -> float:
    r = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return r / (1024 * 1024) if sys.platform == "darwin" else r / 1024


def host_identity() -> dict:
    def sysctl(k):
        r = subprocess.run(["sysctl", "-n", k], capture_output=True, text=True)
        return r.stdout.strip() if r.returncode == 0 else None
    return {"node": platform.node(), "platform": platform.platform(),
            "machine": platform.machine(), "cpu_brand": sysctl("machdep.cpu.brand_string"),
            "ncpu": sysctl("hw.ncpu"), "memsize": sysctl("hw.memsize"),
            "python": platform.python_version(),
            "implementation": platform.python_implementation(),
            "executable": sys.executable}


def measure_panels(P: int, boxes: list[tuple]) -> dict:
    rows = []
    with BD.PhiCache():                                   # one cache, as in Phase 14
        data = []
        for bx in boxes:
            t = time.perf_counter()
            BD.box_upper_coeffs(*bx, NT, P)
            BD.box_lower_coeffs(*bx, NT, P)
            data.append(time.perf_counter() - t)
        for bx, td in zip(boxes, data):
            a, b, c, d = bx
            t = time.perf_counter()
            for w, ar in ((W_K, False), (W_H, True)):
                X.poly_eval_iv(w, G.Iv(a, b), G.Iv(c, d))
                I.kernel_box_upper_iv(w, a, b, c, d, NT, P, atom_removed=ar)
            BD.h1_box_lower(a, b, c, d, NT)
            BD.kernel_box_lower_iv(U_D, a, b, c, d, NT, P)
            X.poly_eval_iv(U_D, G.Iv(a, b), G.Iv(c, d))
            tc = time.perf_counter() - t
            rows.append({"box": [str(x) for x in bx], "data_seconds": round(td, 4),
                         "certification_seconds": round(tc, 4)})
    return {"panels": P, "per_box": rows, "peak_rss_mb": round(_rss_mb(), 1)}


def measure_screen() -> dict:
    states = BD.pointwise_grid(SCREEN_N)
    with BD.PhiCache():
        t = time.perf_counter()
        for (p, m) in states:
            BD.pointwise_coeffs(p, m, NT)
        total = time.perf_counter() - t
    return {"states": len(states), "total_seconds": round(total, 3)}


def derive(raw: dict) -> dict:
    """Constants from the raw observations, mechanically. Recomputable from the artifact alone."""
    per = {}
    for P, r in raw["panels"].items():
        worst = max(F(str(x["data_seconds"])) + F(str(x["certification_seconds"]))
                    for x in r["per_box"])
        mean = sum(F(str(x["data_seconds"])) + F(str(x["certification_seconds"]))
                   for x in r["per_box"]) / len(r["per_box"])
        per[P] = {"per_box_panel_seconds_max": str(worst / (int(P) + 1)),
                  "per_box_panel_seconds_mean": str(mean / (int(P) + 1)),
                  "peak_rss_mb": r["peak_rss_mb"]}
    return {"rule": ("per_box_panel = max over sampled boxes of (data + certification seconds) "
                     "/ (P + 1); screen = measured total for the full 15x15 grid"),
            "per_panels": per,
            "screen_total_seconds": str(F(str(raw["screen"]["total_seconds"]))),
            "screen_states": raw["screen"]["states"]}


def sample(stage: str, log: list) -> None:
    """One detector sample; refuse at once if any other campaign worker is running."""
    w = PR.campaign_workers()
    log.append({"stage": stage, "t": round(time.time(), 1), "workers": w["workers"],
                "foreign_python": w["foreign_python"],
                "interpreters_seen": w["interpreters_seen"],
                "load_average": [round(x, 2) for x in os.getloadavg()]})
    if w["workers"]:
        raise SystemExit(f"REFUSE: not sequential at {stage}; campaign workers: {w['workers']}")


class Sampler:
    """Samples the detector every `period` seconds in a background thread for the whole
    measurement, so a worker that starts and stops between stages is still seen."""
    def __init__(self, period: float = 10.0):
        import threading
        self.period, self.log, self._stop = period, [], threading.Event()
        self._t = threading.Thread(target=self._run, daemon=True)

    def _run(self):
        while not self._stop.wait(self.period):
            w = PR.campaign_workers()
            self.log.append({"t": round(time.time(), 1), "workers": w["workers"],
                             "foreign_python": w["foreign_python"]})

    def __enter__(self):
        self._t.start()
        return self

    def __exit__(self, *exc):
        self._stop.set()
        self._t.join()
        return False


def main() -> int:
    samples: list = []
    sample("before", samples)
    sampler = Sampler().__enter__()
    t0 = time.time()
    boxes = sample_boxes()
    raw = {"panels": {}, "screen": None}
    for P in PANELS:
        print(f"measuring P={P} on {len(boxes)} NT boxes ...", flush=True)
        raw["panels"][str(P)] = measure_panels(P, boxes)
        sample(f"after P={P}", samples)
    print("measuring the pointwise stage on NT ...", flush=True)
    raw["screen"] = measure_screen()
    sampler.__exit__(None, None, None)
    sample("after", samples)
    seen_bg = [x for x in sampler.log if x["workers"]]
    if seen_bg:
        raise SystemExit(f"REFUSE: not sequential; the background sampler saw workers: {seen_bg}")
    out = {"schema": "C11R_COST/2",
           "block": "NON-TARGET [5/2, 5/2 + 108337/1250000] only",
           "host": host_identity(),
           "sequential": {"detector": "code/c11r_procs.py (revision 2)",
                          "samples": samples,
                          "background_samples": len(sampler.log),
                          "background_sample_period_seconds": sampler.period,
                          "background_workers_seen": sum(len(x["workers"]) for x in sampler.log),
                          "campaign_workers_seen": sum(len(x["workers"]) for x in samples)
                          + sum(len(x["workers"]) for x in sampler.log),
                          "foreign_python_max": max(x["foreign_python"] for x in samples),
                          "what_it_does_not_establish": (
                              "no campaign worker was running at any sample; foreign Python "
                              "processes and other load are counted, not excluded, and the "
                              "load average is recorded at every sample")},
           "sample_boxes": [[str(x) for x in b] for b in boxes],
           "manufactured_weights": {"K_e": "12 - 3/2 m", "Khat_e": "8 - m",
                                    "sub-solution": "1/2 + m/20"},
           "raw": raw,
           "derived": derive(raw),
           "wall_seconds": round(time.time() - t0, 1)}
    s = C.write_evidence(C.NS / "evidence" / "cost" / "C11R_COST.json", out, producer=__file__)
    for P, d in out["derived"]["per_panels"].items():
        print(f"  P{P:>4s}: per box-panel max {float(F(d['per_box_panel_seconds_max'])):.4f}s "
              f"mean {float(F(d['per_box_panel_seconds_mean'])):.4f}s  rss {d['peak_rss_mb']} MB")
    print(f"  screen: {out['derived']['screen_total_seconds']}s for "
          f"{out['derived']['screen_states']} states")
    print(f"wrote evidence/cost/C11R_COST.json sha256 {s[:16]}...  ({out['wall_seconds']}s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
