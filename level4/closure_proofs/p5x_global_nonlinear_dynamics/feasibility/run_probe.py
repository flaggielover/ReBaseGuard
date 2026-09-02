"""Run the P5X feasibility probe and write NON-AUTHORITATIVE evidence JSON.

Three questions, all about *proof feasibility*, none about science:

  Q1  does the two-dimensional reduction reproduce P5's independently measured
      R_{D,m}(e) for m in {1,2,3,5} and both frozen detectors?
  Q2  does it reproduce P5's measured S_{D,1}(e)?
  Q3  is the discretisation converging (n_grid 61 -> 121), i.e. is the
      remaining gap Monte-Carlo error rather than a modelling error?

Outputs `results/reduction_probe.json`.  Nothing here is a certificate.
"""
from __future__ import annotations

import json
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fredholm_probe import CUSUM, SR, selection_map          # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
P5_MAP = ROOT / "level4/closure_proofs/p5_nonlinear_dynamics/results/nonlinear_map.json"
P5_TAIL = ROOT / "level4/closure_proofs/p5_nonlinear_dynamics/results/map_tail.json"

CHECK_E = [0.005, 0.02, 0.1, 0.3, 0.8, 1.5, 2.2, 3.0, 4.0, 5.0]
SCAN_E = ([round(v, 3) for v in np.arange(0.05, 1.0, 0.05)]
          + [1.2, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0, 6.5,
             7.0, 7.5, 8.0, 9.0, 10.0, 11.0, 12.0])


def git_head() -> str:
    return subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT,
                          capture_output=True, text=True).stdout.strip()


def main() -> None:
    ref = json.load(open(P5_MAP))
    by_det = {}
    for row in ref["rows"]:
        by_det.setdefault(row["detector"], {})[round(row["e"], 6)] = row

    correspondence = []
    for det in (CUSUM, SR):
        for e in CHECK_E:
            row = by_det[det].get(round(e, 6))
            if row is None:
                continue
            coarse = selection_map(det, e, [1, 2, 3, 5], n_grid=61)
            fine = selection_map(det, e, [1, 2, 3, 5], n_grid=121, second_moment=True)
            for m in (1, 2, 3, 5):
                mc = next(d for d in row["per_m"] if d["m"] == m)
                correspondence.append({
                    "detector": det, "e": e, "m": m,
                    "fredholm_R_n61": coarse["R"][m],
                    "fredholm_R_n121": fine["R"][m],
                    "grid_delta": fine["R"][m] - coarse["R"][m],
                    "p5_mc_R": mc["R"], "p5_mc_R_se": mc["R_se"],
                    "z_vs_p5": (fine["R"][m] - mc["R"]) / mc["R_se"],
                })
            mc1 = next(d for d in row["per_m"] if d["m"] == 1)
            correspondence[-4]["fredholm_S_m1"] = fine["S_m1"]
            correspondence[-4]["p5_mc_S_m1"] = mc1["S"]
            correspondence[-4]["p5_mc_S_m1_se"] = mc1["S_se"]

    scan = []
    for det in (CUSUM, SR):
        for e in SCAN_E:
            got = selection_map(det, float(e), [1, 2, 3, 5], n_grid=101,
                                second_moment=True)
            scan.append({"detector": det, "e": float(e),
                         "R": got["R"], "S_m1": got["S_m1"],
                         "M2_m1": got["M2_m1"]})

    summary = {}
    for det in (CUSUM, SR):
        rows = [r for r in scan if r["detector"] == det]
        for m in (1, 2, 3, 5):
            arg = max(rows, key=lambda r: abs(r["R"][m]))
            summary[f"{det}_m{m}_sup_absR_on_scan"] = abs(arg["R"][m])
            summary[f"{det}_m{m}_argmax_absR"] = arg["e"]
        summary[f"{det}_m1_inf_S_on_scan"] = min(r["S_m1"] for r in rows)
        summary[f"{det}_m1_argmin_S"] = min(rows, key=lambda r: r["S_m1"])["e"]
        summary[f"{det}_m1_sup_M2_on_scan"] = max(r["M2_m1"] for r in rows)
        summary[f"{det}_sign_R_negative_on_positive_e"] = all(
            r["R"][m] < 0 for r in rows for m in (1, 2, 3, 5))
    worst = max(correspondence, key=lambda r: abs(r["z_vs_p5"]))
    summary["max_abs_z_vs_p5_mc"] = abs(worst["z_vs_p5"])
    summary["max_abs_grid_delta_61_to_121"] = max(
        abs(r["grid_delta"]) for r in correspondence)

    payload = {
        "status": "FEASIBILITY_PROBE_NON_AUTHORITATIVE",
        "not_a_certificate": True,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": git_head(),
        "python": platform.python_version(),
        "numpy": np.__version__,
        "platform": platform.platform(),
        "reduction": "P5X-T1 (see ../FROZEN_THEOREM.md)",
        "summary": summary,
        "correspondence": correspondence,
        "scan": scan,
    }
    out = HERE / "results" / "reduction_probe.json"
    out.write_text(json.dumps(payload, indent=1))
    print(json.dumps(summary, indent=1))
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
