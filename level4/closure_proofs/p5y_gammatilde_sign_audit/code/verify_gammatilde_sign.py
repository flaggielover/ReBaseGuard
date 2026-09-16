"""Verifier for the GammaTilde_m > 1 sign audit (CUSUM, m = 1, 2, 3, 5), result r1.

    python3 -B code/verify_gammatilde_sign.py            # recompute every fact, compare to the committed result
    python3 -B code/verify_gammatilde_sign.py --emit     # print the recomputed machine section (used once to write r1)

No scientific computation. Every number is exact rational arithmetic on fields of ONE committed, hash-bound
certified record: the CUSUM Aux5 cell-0 record copy committed by the premise-binding audit
(p5y_k5b_k1_premise_binding_audit/result_r1/records/aux5_CUSUM_0_256.json).

THE DERIVED BOUND (route "odd-C3")
----------------------------------
Cell 0 is [0, 2 e0] with midpoint e0 and radius rho = e0.  From the record:

    D_interval(m)          encloses R_m'(e0)                                  (ERROR_ALGEBRA s.4-5, PB5)
    supF3_final(r)         >= sup_cell ||d_e^3 F_r||, r = 0..4                  (refine2, REFINE2_SOUND = YES)
    tower T_W[(r,j),3]     >= sup_cell ||d_e^3 W_(r,j)||  (W_(r,0) = S_r)       (aux_refine towers, order 3;
                                                                                recorded on the order-1 node as
                                                                                'tower_next_order' = T[.,.,1+2])
Assembly (ERROR_ALGEBRA s.4, exact positive coefficients c_(m,t) = 1/t - 1/m):

    M3(m) = (1/m) sum_(r<m) supF3_r + sum_(t=1)^(m-1) c_(m,t) sum_(r<t) T_W[(r, t-r-1), 3]  >=  sup_cell |R_m'''|

R_m is odd (P5-T3) and C^3 (P5X L5), so R_m'' is odd and R_m''(0) = 0, hence

    R_m'(e0) - R_m'(0) = int_0^e0 (e0 - s) R_m'''(s) ds,   |.| <= (e0^2 / 2) M3(m)  =: E(m)

and R_m'(0) in [D.lo - E, D.hi + E].  By P1-T1 at rho = 1, GammaTilde_m = 1 - R_m'(0), so

    GammaTilde_m in [1 - D.hi - E, 1 - D.lo + E],   GammaTilde_m > 1  <=>  D.hi + E < 0 suffices.

The predecessor (premise-binding r1) used the first-order widening e0 * M_R2 instead of E; both are recomputed.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from fractions import Fraction as F
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
REPO = NS.parents[2]
CP = "level4/closure_proofs/"
RESULT = NS / "result_r1/GAMMATILDE_SIGN_RESULT.json"
SOURCES = NS / "config/SOURCES.json"
RECORD = REPO / CP / "p5y_k5b_k1_premise_binding_audit/result_r1/records/aux5_CUSUM_0_256.json"
EXPORT = REPO / CP / "p5y_k1_cusum_aux5_composite_closure/evidence/closure_r1/COMPOSITE_EXPORT_MANIFEST.json"
CELLS = REPO / CP / "p5y_k1_cover_ledger_successor/config/cells.json"
M_VALUES = (1, 2, 3, 5)
GAMMA_ESTIMATES = {"1": "15.916540430", "2": "13.264824962", "3": "11.957078195", "5": "10.226363970"}  # P1-N1
GAMMA_CERT_M1 = ("3.9243482005828971282", "27.8493821275467032805")                                   # CORE-C1


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def git_blob(commit: str, path: str) -> bytes:
    return subprocess.run(["git", "-C", str(REPO), "show", f"{commit}:{path}"], check=True,
                          capture_output=True).stdout


def coefficient(m: int, t: int) -> F:
    return F(1, t) - F(1, m)


def w_node(r: int, j: int) -> str:
    """Node id carrying T[W,(r,j),3]: the order-1 node (tower index = order + 2)."""
    return f"S:{r}:1" if j == 0 else f"W:{r}:{j}:1"


def binding_section(raw: bytes, rec: dict) -> dict:
    sys.path.insert(0, str(REPO / CP / "p5y_k1_cusum_aux4_fullcover/code"))
    import hash_v2 as H  # frozen, stdlib-only
    export = json.loads(EXPORT.read_text())["files"]
    frozen = next(c for c in json.loads(CELLS.read_text()) if c["detector"] == "CUSUM" and c["index"] == 0)
    return {
        "record_sha256": sha(raw),
        "record_sha256_equals_composite_export_manifest": sha(raw) == export["k4_records/aux5_CUSUM_0_256.json"],
        "scientific_content_hash_recomputes": H.record_scientific_hash(rec) == rec["scientific_content_hash"],
        "geometry_equals_frozen_cells": (rec["e0"], rec["rho"]) == (frozen["e0"], frozen["rho"]),
        "detector": rec["detector"], "cell_index": rec["cell_index"],
    }


def _v(pair) -> F:
    return F(pair[0]) + F(pair[1])


def bound_section(rec: dict) -> dict:
    e0, rho = _v(rec["e0"]), _v(rec["rho"])
    assert rho == e0 and e0 > 0, "cell 0 must be [0, 2 e0]"
    supF3 = {r: F(rec["whole_cell_refinement"][str(r)]["second_order"]["supF3_final"]) for r in range(5)}
    decisions = rec["node_refinement"]["decisions"]
    # Two independently recorded copies of sup_cell|S_0'''|: refine2's supS3 (r = 0) and aux_refine's T[S,0,3].
    tower_indexing_crosscheck = (F(decisions["S:0:1"]["tower_next_order"])
                                 == F(rec["whole_cell_refinement"]["0"]["second_order"]["sup_source_third_derivative"]))
    out = {"e0": str(e0), "rho": str(rho), "half_e0_squared": str(e0 * e0 / 2),
           "tower_indexing_crosscheck_S0_order3": tower_indexing_crosscheck,
           "supF3_final": {str(r): str(v) for r, v in supF3.items()}, "m": {}}
    for m in M_VALUES:
        L = rec["m"][str(m)]
        D = (F(L["D_interval"]["lo"]), F(L["D_interval"]["hi"]))
        M_R2 = F(L["M_R2"])
        towers = {}
        finite = F(0)
        for t in range(1, m):
            for r in range(t):
                node = w_node(r, t - r - 1)
                T3 = F(decisions[node]["tower_next_order"])
                towers[f"W({r},{t - r - 1})<-{node}"] = str(T3)
                finite += coefficient(m, t) * T3
        resolvent = sum((supF3[r] for r in range(m)), F(0)) / m
        M3 = resolvent + finite
        E_odd = e0 * e0 / 2 * M3
        E_first = e0 * M_R2
        rp0_odd = (D[0] - E_odd, D[1] + E_odd)
        rp0_first = (D[0] - E_first, D[1] + E_first)
        gam = (1 - rp0_odd[1], 1 - rp0_odd[0])
        est = F(GAMMA_ESTIMATES[str(m)])
        row = {
            "D_interval": [str(D[0]), str(D[1])],
            "M3_resolvent_part": str(resolvent), "M3_finite_part": str(finite), "M3": str(M3),
            "finite_part_towers": towers,
            "E_odd_C3": str(E_odd), "E_first_order_e0_M_R2": str(E_first),
            "Rprime0_upper_odd_C3": str(rp0_odd[1]), "Rprime0_upper_first_order": str(rp0_first[1]),
            "GammaTilde_interval_odd_C3": [str(gam[0]), str(gam[1])],
            "GammaTilde_lower_minus_1": str(gam[0] - 1),
            "GammaTilde_gt_1_certified_by_odd_C3": gam[0] > 1,
            "GammaTilde_gt_1_certified_by_first_order": 1 - rp0_first[1] > 1,
            "M3_needed_for_sign": str(-D[1] / (e0 * e0 / 2)) if D[1] < 0 else None,
            "M3_excess_factor": str(M3 / (-D[1] / (e0 * e0 / 2))) if D[1] < 0 else None,
            "contains_P1N1_estimate": gam[0] <= est <= gam[1],
            "float_view": {"GammaTilde_lower": float(gam[0]), "GammaTilde_upper": float(gam[1]),
                           "Rprime0_upper": float(rp0_odd[1]), "E_odd_C3": float(E_odd), "M3": float(M3)},
        }
        if m == 1:
            lo_c, hi_c = F(GAMMA_CERT_M1[0]), F(GAMMA_CERT_M1[1])
            row["intersects_certified_m1_enclosure"] = max(gam[0], lo_c) <= min(gam[1], hi_c)
        out["m"][str(m)] = row
    return out


def pins_section(base: str) -> dict:
    pins = json.loads(SOURCES.read_text())["pinned_at_base_commit"]
    return {p: sha(git_blob(base, p)) == d for p, d in pins.items()}


def build() -> dict:
    raw = RECORD.read_bytes()
    rec = json.loads(raw)
    base = json.loads(SOURCES.read_text())["base_commit"]
    return {"binding": binding_section(raw, rec), "bound": bound_section(rec), "pins_match": pins_section(base)}


def consistency_problems(result: dict, live: dict) -> list[str]:
    errs = []
    if result.get("recomputed") != live:
        errs.append("recomputed section differs from live recomputation")
    b = live["binding"]
    if not (b["record_sha256_equals_composite_export_manifest"] and b["scientific_content_hash_recomputes"]
            and b["geometry_equals_frozen_cells"]):
        errs.append("record binding failed")
    if not live["bound"]["tower_indexing_crosscheck_S0_order3"]:
        errs.append("order-3 tower indexing cross-check failed")
    if not all(live["pins_match"].values()):
        errs.append("a pinned source differs from the base commit")
    v = result["verdicts"]
    for m in (2, 3, 5):
        certified = live["bound"]["m"][str(m)]["GammaTilde_gt_1_certified_by_odd_C3"]
        if v[f"GAMMATILDE_GT_1_M{m}"] == "CERTIFIED" and not certified:
            errs.append(f"m={m}: CERTIFIED claimed but the derived bound does not exceed 1")
        if v[f"GAMMATILDE_GT_1_M{m}"] == "REFUTED":
            errs.append(f"m={m}: REFUTED requires a certified upper bound < 1, which this audit never produces")
    all_cert = all(v[f"GAMMATILDE_GT_1_M{m}"] == "CERTIFIED" for m in (2, 3, 5))
    if (v["ALL_CUSUM_M_GAMMATILDE_GT_1"] == "CERTIFIED") != all_cert:
        errs.append("ALL_CUSUM_M_GAMMATILDE_GT_1 inconsistent with per-m verdicts")
    if (v["H3A_POSITIVE_BRANCH_PREMISE"] == "SATISFIED") != all_cert:
        errs.append("H3A_POSITIVE_BRANCH_PREMISE inconsistent with per-m verdicts")
    for k in ("SCIENTIFIC_COMPUTE_RUN", "CUSUM_CLOSURE_MODIFIED", "K1_MODIFIED", "AWS_PS1_TOUCHED",
              "ORIGIN_MAIN_TOUCHED", "K5_DECLARED_CLOSED", "P5Y_DECLARED_CLOSED"):
        if v.get(k) != "NO":
            errs.append(f"{k} must be NO")
    return errs


def main(argv) -> int:
    live = build()
    if "--emit" in argv:
        print(json.dumps(live, indent=1, sort_keys=True))
        return 0
    result = json.loads(RESULT.read_text())
    errs = consistency_problems(result, live)
    print("GAMMATILDE_SIGN_RESULT_VERIFIED" if not errs else "GAMMATILDE_SIGN_RESULT_REFUSED",
          sha(RESULT.read_bytes()))
    for e in errs:
        print(" -", e)
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
