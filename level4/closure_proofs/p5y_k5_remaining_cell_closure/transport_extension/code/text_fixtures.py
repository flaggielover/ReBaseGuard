"""T-EXT qualification on manufactured sigma-systems with EXACT rational truth, at WIDENED hulls.

The frozen R4 harness first_cell_r4.run(spec) (unmodified) builds a manufactured odd sigma-system, runs the graded point
DAG at e = 0, the frozen local_r5.local_tower on the hull [0, x1] with hull norms of that system, and checks on 17 grid
points of [0, x1] against exact truth: every (e, o, t) component of every tower node (n <= 5) and local anchor, the
Strategy-B bounds (L_B <= min R''', U_B >= max R''') and M5 >= max |R^(5)|. T-EXT reuses exactly this machinery with the
hull radius widened, so the qualification re-runs it on the frozen R4 fixtures with x1 replaced by factor * x1.

A case whose manufactured rig refuses its own precondition (e.g. sup ||K|| >= 1 on the widened hull) is recorded as
NOT_APPLICABLE and counts neither as a pass nor as a failure; the frozen protocol fixes the minimum number of
applicable cases and the regime they must cover.

    python -B code/text_fixtures.py --out FIXTURES.json [--seed-offset 900000 for DEV calibration only]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve()
REPO = HERE.parents[5]
CP = REPO / "level4/closure_proofs"
R4 = CP / "p5y_k5_cusum_order3_r4_tightening"
R4_PROTOCOL_SHA256 = None   # pinned in TEXT_PROTOCOL.json; checked by the qualification runner
for p in ("p5y_k5_cusum_order3_r4_tightening/code", "p5y_k5_cusum_order3_r3_infrastructure/code",
          "p5y_k5_cusum_order3_r2_repair/code", "p5y_k5_cusum_order3_real_producer/code"):
    sys.path.insert(0, str(CP / p))

import first_cell_r4 as FC4  # noqa: E402
import graded_dag as G  # noqa: E402
import manufactured_chain as MC  # noqa: E402
import rung3_engine as R1E  # noqa: E402
import sigma_systems as SS  # noqa: E402

WIDENING = {"FR4_04_parity_pure_cusum_like": [1, 2, 4, 8, 16, 32, 44],
            "FR4_06_slow_even_mode": [1, 2, 4, 8, 16, 32],
            "FR4_01_tight_M5_a": [1, 4, 16, 64],
            "FR4_02_tight_M5_b": [1, 4, 16],
            "FR4_05_parity_leak": [1, 2],
            "FR4_07_well_conditioned_odd": [1, 2]}
# T-EXT wide family (new, frozen with the protocol; seeds disjoint from R4 and from the DEV calibration seeds 941xxx):
# slow even (Perron) mode with small drift so that the manufactured rig stays below ||K|| = 1 on wide hulls,
# covering eta * C_e0 from 1 to about 20 (the CUSUM graded zone reaches about 10.7 at cell 40).
WIDE = [{"id": f"TEXT_W_slow_C{C}_x{x}", "family": "slow_even", "seed": 52000 + C, "C_target": C, "c": "1/5",
         "k_scale": ks, "x1": x, "noise": "0"}
        for C, ks, xs in ((100, "1/100", ("1/100", "1/50", "1/25", "1/10")),
                          (400, "1/400", ("1/400", "1/100", "1/40", "1/20")),
                          (50, "1/20", ("1/50", "1/20", "1/10")))
        for x in xs]
# T-EXT small-determinant family (new, frozen): slow even AND slow odd mode with strong drift, eta approaching the rig's
# own Neumann limit, so the graded resolvent determinant reaches the CUSUM regime of hulls 30-40 (det 0.48 -> 0.05).
# A dense eta grid (1/n, n = 60..300 step 4) so the 0 < det <= 0.1 window is hit whatever the random drift of the seed.
DET = [{"id": f"TEXT_D{v}_x1/{n}", "family": "slow_even", "seed": 53100 + v, "C_target": 100, "d": d, "c": c,
        "k_scale": "1", "x1": f"1/{n}", "noise": "0"}
       for v, d, c in ((0, "1/20000", "1/40000"), (1, "1/4000", "1/8000"), (2, "1/1000", "1/2000"))
       for n in range(60, 301, 4)]


def regime(spec: dict) -> dict:
    """Mode, determinant and ee entry of the graded resolvent block of the manufactured rig on its hull (the same
    frozen graded_dag.resolvent_block the tower calls), for the coverage gate."""
    x1 = F(spec["x1"])
    grH = SS.GradedRig(SS.build(spec), x1 / 2, x1 / 2, seed=int(spec["seed"]), noise=F(spec.get("noise", "0")))
    with R1E.precision(256):
        ex = R1E.exact
        hk = [MC.sup_deriv_poly(grH.rig.ex["K"], i, x1 / 2, mat=True) for i in range(3)]
        R = G.resolvent_block(ex(grH.C), ex(grH.C_e0), ex(grH.C_o0), ex(hk[1]), ex(hk[2]), ex(x1), True)
        a, b = x1 * x1 * F(hk[2]) / 2, x1 * F(hk[1])
        det = (1 - F(grH.C_e0) * a) * (1 - F(grH.C_o0) * a) - F(grH.C_e0) * F(grH.C_o0) * b * b
        ee = float(R1E.fraction_of(R["ee"].abs_upper())) if R["mode"] == "graded" else None
    return {"mode": R["mode"], "det": float(det), "ee": ee}


def run(seed_offset: int = 0) -> dict:
    proto = json.loads((R4 / "config/QUALIFICATION_PROTOCOL_R4.json").read_bytes())
    fixtures = {f["id"]: f for f in proto["fixtures"]}
    rows = []
    for fid, factors in WIDENING.items():
        for fac in factors:
            spec = dict(fixtures[fid])
            spec["x1"] = str(F(spec["x1"]) * fac)
            spec["seed"] = int(spec["seed"]) + seed_offset
            spec["id"] = f"{fid}_x{fac}"
            t0 = time.process_time()
            try:
                r = FC4.run(spec, reference=False)
                rows.append({"id": spec["id"], "fixture": fid, "factor": fac, "x1": spec["x1"], "status": "RAN",
                             "violations": r["violation_count"], "kinds": r["violation_kinds"],
                             "first": r["violations"][:3], "C_e0": r["C_e0"], "C_o0": r["C_o0"], "C": r["C"],
                             "eta_C_e0": float(F(spec["x1"])) * r["C_e0"],
                             "M5_over_true": {m: (v["M5_local"] / v["true_max_abs_R5"] if v["true_max_abs_R5"] else None)
                                              for m, v in r["radii"].items()},
                             "cpu_s": time.process_time() - t0})
            except Exception as exc:     # the rig's own precondition or a fail-closed refusal
                rows.append({"id": spec["id"], "fixture": fid, "factor": fac, "x1": spec["x1"], "status": "NOT_APPLICABLE",
                             "reason": f"{type(exc).__name__}: {str(exc)[:200]}", "cpu_s": time.process_time() - t0})
    for spec0 in WIDE + DET:
        spec = dict(spec0)
        spec["seed"] = int(spec["seed"]) + seed_offset
        t0 = time.process_time()
        try:
            r = FC4.run(spec, reference=False)
            rows.append({"id": spec["id"], "fixture": spec["id"].split("_x")[0], "factor": 0, "x1": spec["x1"],
                         "status": "RAN", **{"regime": regime(spec)},
                         "violations": r["violation_count"], "kinds": r["violation_kinds"], "first": r["violations"][:3],
                         "C_e0": r["C_e0"], "C_o0": r["C_o0"], "C": r["C"], "eta_C_e0": float(F(spec["x1"])) * r["C_e0"],
                         "M5_over_true": {m: (v["M5_local"] / v["true_max_abs_R5"] if v["true_max_abs_R5"] else None)
                                          for m, v in r["radii"].items()},
                         "cpu_s": time.process_time() - t0})
        except Exception as exc:
            rows.append({"id": spec["id"], "fixture": spec["id"].split("_x")[0], "factor": 0, "x1": spec["x1"],
                         "status": "NOT_APPLICABLE",
                         "reason": f"{type(exc).__name__}: {str(exc)[:200]}", "cpu_s": time.process_time() - t0})
    ran = [r for r in rows if r["status"] == "RAN"]
    return {"schema": "rebaseguard.p5y.k5.remaining-cell-closure.text-fixtures.v1", "seed_offset": seed_offset,
            "r4_protocol_sha256": hashlib.sha256((R4 / "config/QUALIFICATION_PROTOCOL_R4.json").read_bytes()).hexdigest(),
            "rows": rows, "ran": len(ran), "violations_total": sum(r["violations"] for r in ran),
            "wide_ran": sum(1 for r in ran if r["factor"] != 1), "max_eta_C_e0": max((r["eta_C_e0"] for r in ran), default=0),
            "ran_eta_C_e0_ge_4": sum(1 for r in ran if r["eta_C_e0"] >= 4),
            "min_det": min((r["regime"]["det"] for r in ran if "regime" in r), default=1),
            "ran_det_le_0_1": sum(1 for r in ran if "regime" in r and r["regime"]["det"] <= 0.1),
            "ran_graded_det_in_0_0p1": sum(1 for r in ran if "regime" in r and r["regime"]["mode"] == "graded"
                                           and 0 < r["regime"]["det"] <= 0.1),
            "min_graded_positive_det": min((r["regime"]["det"] for r in ran if "regime" in r
                                            and r["regime"]["mode"] == "graded" and r["regime"]["det"] > 0), default=1),
            "ran_scalar_fallback": sum(1 for r in ran if "regime" in r and r["regime"]["mode"] == "scalar_fallback")}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--seed-offset", type=int, default=0)
    a = ap.parse_args()
    res = run(a.seed_offset)
    Path(a.out).write_text(json.dumps(res, sort_keys=True, indent=1) + "\n")
    print("ran", res["ran"], "wide", res["wide_ran"], "violations", res["violations_total"], "max eta*C_e0",
          round(res["max_eta_C_e0"], 3), "n(etaC>=4)", res["ran_eta_C_e0_ge_4"], "min det", round(res["min_det"], 4),
          "n(det<=0.1)", res["ran_det_le_0_1"], "n(graded 0<det<=0.1)", res["ran_graded_det_in_0_0p1"],
          "min graded det", round(res["min_graded_positive_det"], 4), "n(scalar fallback)", res["ran_scalar_fallback"])
    return 0



if __name__ == "__main__":
    sys.exit(main())
