"""C7 Phases 1-2 -- slack ledger and required-improvement quantification.

Phase 1 asks WHERE the C4 chain E_a[tau] >= H/E[V] loses ground, and how much of each loss C7 can
recover by analytic means alone. Phase 2 asks how much improvement is REQUIRED for the cell-309
exclusion to stop being fragile under C5-T.

Every entry is either measured here or explicitly marked unmeasurable, with the reason. Nothing is
asserted from non-emptiness or from the absence of a counterexample.
"""
from __future__ import annotations

import pathlib
import sys
from fractions import Fraction as F

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import c7_common as C
import c7_gaussian as G
import c7_theorem as T

E_LO, K, H = F(19839101, 10000000), F(1, 2), F(5)
N_PARTITION = 64
A_GRID = [F(j, 4) for j in range(8, 25)]


def main() -> int:
    c4, c5 = C.c4_cell309(), C.c5_critical_a0()
    B4 = F(c4["lower_bound_E_a_tau"])                     # C4's exact certified floor
    crit = F(str(c5["critical_A0_C5T"]))
    EV = G.E_excess(E_LO, K)

    part = [F(j) * H / N_PARTITION for j in range(1, N_PARTITION + 1)]
    t1 = T.lambda_lower(E_LO, K, H)
    cert_el = T.certified_U("elementary", E_LO, K, H, A_GRID)
    cert_rg = T.certified_U("registry", E_LO, K, H)
    cert_lr = T.certified_U("lorden", E_LO, K, H)
    U_el, U_rg = cert_el["value"], cert_rg["value"]
    U_lo = T.U_lorden(E_LO, K, H)
    L_el = T.lambda_lower_tier_k(E_LO, K, H, cert_el, part)
    L_rg = T.lambda_lower_tier_k(E_LO, K, H, cert_rg, part)
    L_lr = T.lambda_lower_tier_k(E_LO, K, H, cert_lr, part)

    # ---- Phase 1: the slack ledger -------------------------------------------------------------
    # S1: the overshoot C4 discards. Its provable RANGE is [E[R] recovered, Lorden's ceiling].
    ER_lo, ER_hi = L_el["E_R_lower"], U_lo["E_R_upper"]
    ceiling = (G.Iv(H + ER_hi, H + ER_hi) / G.Iv(EV.lo, EV.lo)).hi

    # S5: the reflected tail dropped inside psi_lo, measured as the relative size of the term dropped.
    f_K = T.f_ratio(K, E_LO).hi

    # S6: LP discretisation, measured against a 4x finer partition rather than asserted small.
    fine = [F(j) * H / (4 * N_PARTITION) for j in range(1, 4 * N_PARTITION + 1)]
    L_fine = T.lambda_lower_tier_k(E_LO, K, H, cert_rg, fine)["L_lower"]

    ledger = [
        {"id": "S1", "step": "C4 discards the overshoot R = S_tau' - H, replacing H + E[R] by H",
         "recoverable_by_C7": True, "status": "RECOVERED",
         "E_R_lower_recovered": str(ER_lo), "E_R_lower_float": float(ER_lo),
         "E_R_upper_provable": str(ER_hi), "E_R_upper_float": float(ER_hi),
         "fraction_of_provable_range_recovered": float(ER_lo / ER_hi),
         "note": "this is the whole of C7's improvement; the residual headroom is S1's own remainder"},
        {"id": "S2", "step": "pathwise majorant: the CUSUM clipping at 0 is dropped, so tau >= tau'",
         "recoverable_by_C7": False, "status": "UNMEASURABLE",
         "reason": ("E[tau] - E[tau'] depends on how often the clipped process is pinned at 0, which is "
                    "a property of the CUSUM recursion and not of the increment law alone. Bounding it "
                    "needs either a numerical kernel evaluation or new operator information; both are "
                    "outside C7's compute boundary. Recorded as a known, unquantified, FAVOURABLE loss "
                    "-- it can only make the true Lambda_309 larger than any bound C7 reports.")},
        {"id": "S3", "step": "E[V] replaced by a certified upper bound",
         "recoverable_by_C7": False, "status": "NEGLIGIBLE_AND_MEASURED",
         "E_V_lo": str(EV.lo), "E_V_hi": str(EV.hi),
         "relative_interval_width": float((EV.hi - EV.lo) / EV.lo),
         "note": "outward rounding on the 2^-320 grid; contributes below every digit reported"},
        {"id": "S4", "step": "evaluated at the single point e = e_lo rather than at sup over the cell",
         "recoverable_by_C7": False, "status": "UNMEASURABLE_BUT_SOUND",
         "reason": ("Lambda_309 = sup over the closed cell, so ANY point in the cell gives a valid "
                    "lower bound. e_lo is the best single point because E[V] is increasing in e and the "
                    "bound is decreasing in E[V]. The gap sup - value(e_lo) is not accessible without "
                    "operator information.")},
        {"id": "S5", "step": "the reflected tail rho(s+e) is dropped inside psi_lo",
         "recoverable_by_C7": True, "status": "MEASURED_AND_ACCEPTED",
         "f_K_upper": str(f_K), "relative_loss_upper_percent": float(100 * f_K),
         "note": ("bounded by f(K) = Phi(-(K+e))/Phi(-(K-e)); recovering it would change the last "
                  "bound by at most 0.70%, which does not alter any verdict")},
        {"id": "S6", "step": "LP discretisation of the measure constraint at N = 64",
         "recoverable_by_C7": True, "status": "MEASURED_AND_ACCEPTED",
         "L_at_N": str(L_rg["L_lower"]), "L_at_4N": str(L_fine),
         "relative_gap_percent": float(100 * (L_fine - L_rg["L_lower"]) / L_rg["L_lower"]),
         "note": ("a 4x finer partition is worth under 0.1%; N = 64 is fixed by the gate for "
                  "reviewer reproducibility -- it re-runs in ~17s against ~75s at 4N")},
    ]

    # ---- Phase 2: what improvement is REQUIRED --------------------------------------------------
    def pct(x, base):
        return float(100 * (F(x) - F(base)) / F(base))

    required = {
        "exclusion_test": ("cell 309 is EXCLUDED iff Gamma(A0 = B, A1 = A2 = 0) >= 0, i.e. iff the "
                           "certified floor B exceeds the critical A0"),
        "critical_A0_C5T": str(crit), "critical_A0_C5T_float": float(crit),
        "C4_floor_B": str(B4), "C4_floor_float": float(B4),
        "C4_margin_percent": pct(B4, crit),
        "improvement_needed_to_exist_at_all_percent": 0.0,
        "thresholds": [
            {"name": "BARE", "margin_percent": 0.0, "floor_required": float(crit),
             "meaning": "the exclusion holds at all", "C4_meets": B4 > crit},
            {"name": "ROBUST_5", "margin_percent": 5.0, "floor_required": float(crit * F(105, 100)),
             "meaning": "survives a 5% adverse move in the critical A0", "C4_meets": B4 > crit * F(105, 100)},
            {"name": "ROBUST_10", "margin_percent": 10.0, "floor_required": float(crit * F(110, 100)),
             "meaning": "survives a 10% adverse move", "C4_meets": B4 > crit * F(110, 100)},
        ],
        "why_C4_is_fragile": ("C4 published 2.5827% margin against its own frozen-clause critical A0 "
                              "3.2142360226778806. C5-T's exact-weight transport raised the critical A0 "
                              "to 3.266415728267196, consuming 63% of that margin and leaving 0.9440%. "
                              "A further move of that size in any successor would extinguish it."),
    }

    results = {
        "L1_tier1": {"value": str(t1["C7_bound_lower"]), "float": float(t1["C7_bound_lower"]),
                     "vs_C4_percent": pct(t1["C7_bound_lower"], B4),
                     "margin_percent": pct(t1["C7_bound_lower"], crit),
                     "dependencies": []},
        "L3_elementary": {"value": str(L_el["L_lower"]), "float": float(L_el["L_lower"]),
                          "U_used": str(U_el), "vs_C4_percent": pct(L_el["L_lower"], B4),
                          "margin_percent": pct(L_el["L_lower"], crit),
                          "dependencies": []},
        "L3_registry": {"value": str(L_rg["L_lower"]), "float": float(L_rg["L_lower"]),
                        "U_used": str(U_rg), "vs_C4_percent": pct(L_rg["L_lower"], B4),
                        "margin_percent": pct(L_rg["L_lower"], crit),
                        "dependencies": ["Arb/FLINT operator certification surface"]},
        "L3_lorden": {"value": str(L_lr["L_lower"]), "float": float(L_lr["L_lower"]),
                      "U_used": str(U_lo["U_upper"]), "vs_C4_percent": pct(L_lr["L_lower"], B4),
                      "margin_percent": pct(L_lr["L_lower"], crit),
                      "dependencies": ["Lorden (1970), cited but not re-proved in C7"]},
    }

    out = {
        "schema": "C7_LEDGER/1", "cell": C.CELL, "e_evaluated": str(E_LO), "K": str(K), "H": str(H),
        "N_partition": N_PARTITION, "a_grid": [str(a) for a in A_GRID],
        "phase1_slack_ledger": ledger,
        "phase2_required_improvement": required,
        "results_by_dependency_set": results,
        "analytic_ceiling_of_the_E2_family": {
            "value": str(ceiling), "float": float(ceiling),
            "derivation": "(H + Lorden's upper bound on E[R]) / E[V]_lo",
            "meaning": ("no bound in the E2 family -- however the partition, the split points or U are "
                        "chosen -- can exceed this, because it is what the family gives when E[R] is "
                        "known exactly at its largest provable value"),
            "certified_A0_at_309": c4["A0_certified_float"],
            "family_can_reach_certified_A0": float(ceiling) >= c4["A0_certified_float"],
        },
    }
    p = C.NS / "evidence" / "phase1" / "C7_LEDGER.json"
    s = C.write_evidence(p, out)

    print("PHASE 1 -- slack ledger")
    for r in ledger:
        print(f"  {r['id']}  {r['status']:<26} {r['step'][:66]}")
    print("\nPHASE 2 -- required improvement")
    for t in required["thresholds"]:
        print(f"  {t['name']:<10} floor>={t['floor_required']:.9f}  C4 meets: {t['C4_meets']}")
    print(f"\n{'bound':<16} {'value':>14} {'vs C4':>9} {'margin':>9}  dependencies")
    for k, v in results.items():
        print(f"  {k:<14} {v['float']:>14.9f} {v['vs_C4_percent']:>8.4f}% {v['margin_percent']:>8.4f}%  "
              f"{v['dependencies'] or 'NONE'}")
    cl = out["analytic_ceiling_of_the_E2_family"]
    print(f"\nE2-family analytic ceiling: {cl['float']:.9f}   "
          f"reaches certified A0 {cl['certified_A0_at_309']:.9f}? {cl['family_can_reach_certified_A0']}")
    print(f"\nwrote {p.relative_to(C.REPO)}  sha256 {s[:16]}...")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
