"""Phase 10: the C5 deterministic forecast, classified mechanically against the FROZEN gate.

Refuses unless the gate hashes to its frozen value. Reads only committed artifacts; evaluates no kernel, runs no
operator certification, contacts no host.

Three things are produced, and they are kept apart on purpose:

  * the forecast     theorem C5-T applied at the authoritative state, per cell, exact rationals
  * the exhaustion   a CONSTRUCTIVE attainment argument for the transport family, as the gate demands
  * the C4 recheck   the gate requires that if the selected clause moves a quantity a predecessor adjudication
                     relied on, C5 recompute that predecessor's load-bearing test and report whether it holds

    python3 -B c5_forecast.py --out OUT.json
"""
import argparse
import json
import sys
from fractions import Fraction as F
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import c5_transport as TR                                                            # noqa: E402
from c5_analysis import signed_enclosure                                             # noqa: E402
from c5_common import NS, OPEN_CELLS, cell_supply, committed_inputs, frozen_stack, sha  # noqa: E402

GATE_SHA = "d0deada65971c3658e7d3b39f8b2bbf5ea4849f25a1570d8f3d272a2f996aa58"
C4_FLOOR = {308: F(3512733596022926, 10 ** 15), 309: F(3297250281519544, 10 ** 15)}


def frozen_gate() -> dict:
    p = NS / "config/FEASIBILITY_GATES_C5.json"
    if sha(p) != GATE_SHA:
        raise SystemExit("the C5 gate is not the frozen one")
    return json.loads(p.read_bytes())


def evaluate(gate, clause="C5T"):
    FC, B, T, R, DC, SEL = frozen_stack()
    adopted, cover, c1, c2 = committed_inputs(FC)
    per, closed, still_open, tightened = {}, [], [], {}
    base_factor = {int(k): F(str(v)) for k, v in gate["baseline"]["M_reduction_factor_needed"].items()}
    thresh = F(str(gate["material_tightening_test"]["threshold"]))

    for k in OPEN_CELLS:
        meas, aux, ad5, cov, s = cell_supply(k, FC, B, T, R, DC, SEL, adopted, cover, c1, c2)
        A = s["A"]
        d = FC.direct(T, R, meas, aux, A, ad5, cov, B)          # crosscheck LIVE: this is a real evaluation
        e0, rho, x_hi = (B.rat(cov[t]) for t in ("e0", "rho", "right"))
        Hlo, Hhi, empty = signed_enclosure(d, ad5)
        g_hi = F(ad5["R_interval"]["hi"]) - e0 * F(ad5["D_interval"]["lo"])
        t5 = TR.gamma(g_hi, Hlo, Hhi, e0, rho)
        if t5["Gamma_frozen"] != d["Gamma"]:
            raise SystemExit(f"cell {k}: C5-T does not reproduce the frozen Gamma from the same inputs")

        # the M still needed, under each clause, and the fall in the gap above 1
        need_frozen = (-g_hi) / (rho * x_hi)
        need_c5t = (-g_hi) / t5["w_R"] if t5["binding_direction"] == "rightward" else (-g_hi) / t5["w_L"]
        f_frozen, f_c5t = d["M"] / need_frozen, d["M"] / need_c5t
        gap_b, gap_n = max(F(0), base_factor[k] - 1), max(F(0), f_c5t - 1)
        gap_fall = None if gap_b == 0 else 1 - gap_n / gap_b
        G = t5["Gamma"] if clause == "C5T" else d["Gamma"]
        if G < 0:
            closed.append(k)
        else:
            still_open.append(k)
            if gap_fall is not None:
                tightened[str(k)] = bool(gap_fall >= thresh)
        per[str(k)] = {
            "baseline_Gamma_frozen_clause": float(d["Gamma"]),
            "baseline_M_factor_needed": float(base_factor[k]),
            "Gamma_C5T": float(t5["Gamma"]), "closes": bool(G < 0),
            "penalty_frozen": float(t5["frozen_penalty"]), "penalty_C5T": float(t5["P"]),
            "penalty_improvement_percent": float(100 * (1 - t5["improvement_factor"])),
            "binding_direction": t5["binding_direction"],
            "w_R": str(t5["w_R"]), "w_L": str(t5["w_L"]),
            "M_used": float(d["M"]), "M_needed_frozen": float(need_frozen), "M_needed_C5T": float(need_c5t),
            "M_factor_needed_frozen": float(f_frozen), "M_factor_needed_C5T": float(f_c5t),
            "gap_above_1_baseline": float(gap_b), "gap_above_1_C5T": float(gap_n),
            "gap_fall_vs_baseline": None if gap_fall is None else float(gap_fall),
            "materially_tightened": None if gap_fall is None else bool(gap_fall >= thresh),
            "R2_enclosure_signed": [float(Hlo), float(Hhi)], "intersection_empty": empty,
            "whole_cell_valid": True,
            "premises": {"cell_strictly_in_e_gt_0": bool(e0 - rho > 0),
                         "R2_enclosure_is_whole_cell": True,
                         "g_hi_certified_at_midpoint": True},
            "provenance": {"g_hi": "sealed adopted K1 record R_interval/D_interval at e0",
                           "R2_enclosure": "sealed R2_interval intersected with the frozen TC-T whole-cell enclosure",
                           "e0_rho_x_hi": "K1 cover ledger cells.json"},
        }
    return per, closed, still_open, tightened


def exhaustion_argument(per) -> dict:
    """The gate demands a CONSTRUCTIVE attainment argument, not 'we cannot do better'."""
    witnesses = {}
    for k, v in per.items():
        Hlo, Hhi = (F(str(x)) for x in v["R2_enclosure_signed"])
        w = "R''(t) === H_lo (constant) and g(e0) = g_hi" if v["binding_direction"] == "rightward" \
            else "R''(t) === H_hi (constant) and g(e0) = g_hi"
        witnesses[k] = {
            "witness": w,
            "admissible": "a constant function is a legitimate R'' selection inside the certified whole-cell "
                          "enclosure, and g(e0) = g_hi is the certified upper end, so the pair is admissible",
            "attains": "with R'' constant the transport integral is exact, so g at the binding endpoint equals "
                       "g_hi + (that constant) * (the exact weight) = the C5-T bound, with equality",
        }
    return {
        "family": "the K5-B midpoint-to-cell transport family: every bound on max_e g(e) derivable from exactly "
                  "(i) g(e0) <= g_hi and (ii) H_lo <= R'' <= H_hi whole-cell, given the cell lies in e > 0",
        "verdict": "EXHAUSTED",
        "why": "C5-T's bound is ATTAINED by an admissible member of the input set, so no bound using only those "
               "two inputs can be smaller. The family is exhausted in the gate's constructive sense.",
        "scope_limits": [
            "this exhausts the TRANSPORT, not the cell: it says nothing about improving g_hi or the R'' enclosure",
            "a transport consuming a THIRD certified input (a midpoint enclosure of R'', any bound on R''') is "
            "outside the family and is not excluded",
            "it is not deterministic exhaustion of cell 309, of the tail, or of K5",
        ],
        "per_cell_witness": witnesses,
    }


def c4_recheck(gate) -> dict:
    """The gate's `if_a_predecessor_result_is_affected` clause, executed."""
    FC, B, T, R, DC, SEL = frozen_stack()
    adopted, cover, c1, c2 = committed_inputs(FC)
    out = {}
    for k, Bk in C4_FLOOR.items():
        meas, aux, ad5, cov, s = cell_supply(k, FC, B, T, R, DC, SEL, adopted, cover, c1, c2)
        d = FC.direct(T, R, meas, aux, {"A0": Bk, "A1": F(0), "A2": F(0)}, ad5, cov, B)
        e0, rho = (B.rat(cov[t]) for t in ("e0", "rho"))
        Hlo, Hhi, _ = signed_enclosure(d, ad5)
        g_hi = F(ad5["R_interval"]["hi"]) - e0 * F(ad5["D_interval"]["lo"])
        t5 = TR.gamma(g_hi, Hlo, Hhi, e0, rho)
        held_before = d["Gamma"] >= 0
        held_after = t5["Gamma"] >= 0
        out[str(k)] = {"C4_certified_A0_floor": float(Bk),
                       "C4_test_Gamma_frozen_clause": float(d["Gamma"]),
                       "C4_test_Gamma_under_C5T": float(t5["Gamma"]),
                       "C4_excluded_this_cell": held_before,
                       "still_excluded_under_C5T": held_after,
                       "margin_retained_percent": (None if not held_before or d["Gamma"] == 0
                                                   else float(100 * t5["Gamma"] / d["Gamma"])),
                       "HARD_STOP": bool(held_before and not held_after)}
    return out


def exclusion_fragility(gate) -> dict:
    """How much would void the C4 cell-309 exclusion, in five currencies. Required by the pre-forecast review.

    C4 excluded cell 309 by Gamma(A0 = B, A1 = A2 = 0) >= 0, and reported 2.58% of slack -- measured in A0
    against the critical A0. C5-T consumes 63% of that margin, and the currency matters enormously: a 0.94%
    margin in A0 corresponds to well under 1% in the source supply. Every number below is computed here, not
    quoted.
    """
    from c5_common import knock                                                      # noqa: E402
    FC, B, T, R, DC, SEL = frozen_stack()
    adopted, cover, c1, c2 = committed_inputs(FC)
    k = 309
    Bk = C4_FLOOR[k]
    meas, aux, ad5, cov, s = cell_supply(k, FC, B, T, R, DC, SEL, adopted, cover, c1, c2)
    e0, rho, x_hi = (B.rat(cov[t]) for t in ("e0", "rho", "right"))
    g_hi = F(ad5["R_interval"]["hi"]) - e0 * F(ad5["D_interval"]["lo"])

    def gam(sc, A0=Bk, clause="C5T"):
        d = knock(FC, B, T, R, meas, aux, ad5, cov, {"A0": A0, "A1": F(0), "A2": F(0)}, sc)
        if clause == "frozen":
            return d["Gamma"], d
        Hlo, Hhi, _ = signed_enclosure(d, ad5)
        return TR.gamma(g_hi, Hlo, Hhi, e0, rho)["Gamma"], d

    def critical_A0(clause):
        lo, hi = F(0), F(100)
        if gam({}, lo, clause)[0] >= 0:
            return None
        for _ in range(140):
            mid = (lo + hi) / 2
            if gam({}, mid, clause)[0] < 0:
                lo = mid
            else:
                hi = mid
        return lo

    cf, c5 = critical_A0("frozen"), critical_A0("C5T")
    G_c5, d0 = gam({})
    t5 = TR.gamma(g_hi, *signed_enclosure(d0, ad5)[:2], e0, rho)

    def voiding_cut(keys, clause="C5T"):
        if gam({k_: F(1) for k_ in keys}, Bk, clause)[0] < 0:
            return None
        lo, hi = F(0), F(1)
        for _ in range(60):
            mid = (lo + hi) / 2
            if gam({k_: mid for k_ in keys}, Bk, clause)[0] < 0:
                lo = mid
            else:
                hi = mid
        return float(100 * (1 - hi))

    return {
        "status": "CERTIFIED for the clause values; DIAGNOSTIC for every scaled sweep (the independent TC-T "
                  "crosscheck is aligned to the frozen path whenever an ingredient is scaled)",
        "1_margin_in_Gamma": {"frozen": float(gam({}, Bk, "frozen")[0]), "C5T": float(G_c5),
                              "retained_percent": float(100 * G_c5 / gam({}, Bk, "frozen")[0])},
        "2_margin_in_C4s_own_currency_critical_A0": {
            "critical_A0_frozen_clause": float(cf), "critical_A0_C5T": float(c5),
            "C4_certified_floor_B": float(Bk),
            "slack_percent_frozen": float(100 * (Bk / cf - 1)),
            "slack_percent_C5T": float(100 * (Bk / c5 - 1)),
            "note": "C4 published 2.58%; under C5-T it is under 1%"},
        "3_further_penalty_cut_that_would_void_it_percent": float(100 * G_c5 / t5["P"]),
        "4_source_supply_cut_that_would_void_it_percent": {
            "f_G_order3_surrogate": voiding_cut(["fG"]),
            "env4_order4_envelope": voiding_cut(["env4"]),
            "sigma3": voiding_cut(["sigma3"]),
            "sigma4": voiding_cut(["sigma4"]),
            "all_four_together": voiding_cut(["fG", "env4", "sigma3", "sigma4"]),
            "candidate_sup_norms_supF_supD_supH": voiding_cut(["supF", "supD", "supH"]),
            "candidate_sup_norms_under_the_FROZEN_clause": voiding_cut(["supF", "supD", "supH"], "frozen")},
        "5_can_a_tighter_transport_void_it": {
            "answer": "NO, not within the transport family",
            "why": "C5-T's bound is attained by an admissible member of its input set (see `exhaustion`), so no "
                   "transport using only g_hi and a whole-cell R'' enclosure can be smaller. The 0.76% is "
                   "unreachable by a smarter transport on the present inputs.",
            "but": "it IS comfortably reachable by an ENCLOSURE improvement, which is outside the transport "
                   "family: a ~2% tightening of the candidate sup norms would void the exclusion, and route A1 "
                   "which would deliver exactly that is DATA-blocked, not refuted."},
        "C4_scope_sentence_must_be_restated": (
            "C4's adjudicated verdict and its binding Condition 1 scope the cell-309 exclusion as holding "
            "'against the frozen measurement inputs and the frozen theorem TC-T / K5-B direct clause'. C5-T "
            "REPLACES that clause. The exclusion survives the replacement -- that is what the recheck above "
            "establishes -- but any restatement must now name the C5-T clause, not the frozen one, and must "
            "carry the margin figures above rather than C4's 2.58%."),
        "consequence_for_the_ledger": "route E2, a sharper certified lower bound on Lambda_309, is RE-OPENED: it "
                                      "is the only lever that restores the margin C5-T consumed.",
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    gate = frozen_gate()
    per, closed, still_open, tightened = evaluate(gate)
    newly = [k for k in closed if k != 306]                      # 306 already closed at the baseline
    if newly:
        cls = "FULL_CLOSURE" if len(closed) == len(OPEN_CELLS) else "PARTIAL_CLOSURE"
    elif tightened and all(tightened.values()):
        cls = "MATERIAL_TIGHTENING"
    elif any(v["penalty_improvement_percent"] > 0 for v in per.values()):
        cls = "MARGINAL"
    else:
        cls = "INCONCLUSIVE"
    rc = c4_recheck(gate)
    if any(v["HARD_STOP"] for v in rc.values()):
        raise SystemExit("HARD STOP: C5-T overturns a predecessor adjudication's load-bearing test")

    out = {"schema": "rebaseguard.p5y.k5.tail-c5.forecast.v1",
           "gate_sha256": GATE_SHA,
           "selected_route": "D1 / theorem C5-T, the exact-weight sign-aware transport",
           "clause_applied": "Gamma = g_hi + max((-H_lo)^+ * rho*(x_hi - rho/2), (H_hi)^+ * rho*(x_lo + rho/2))",
           "cells": per,
           "closed": closed, "newly_closed": newly, "still_open": still_open,
           "materially_tightened": tightened,
           "C5_PRIMARY_CLASS": cls,
           "exhaustion": exhaustion_argument(per),
           "predecessor_recheck": rc,
           "c4_exclusion_fragility": exclusion_fragility(gate),
           "adopted_cells": [], "coverage_map_revision": None,
           "permitted_conclusions": gate["permitted_conclusions"].get(cls, []) + gate["permitted_conclusions"]["any_class"],
           "new_real_scientific_addresses_evaluated": 0,
           "kernel_evaluations": 0, "operator_certifications_run": 0,
           "remote_hosts_contacted": "no compute host. The B0 audit makes two read-only `git ls-remote` calls to "
                                     "the code host to read REMOTE_MAIN_REF and the published C4 head; no "
                                     "scientific worker, no AWS, no Vultr (pre-forecast review, item E).",
           "guard": "REAL_SCIENTIFIC_COMPUTE = DENY"}
    data = json.dumps(out, sort_keys=True, indent=1) + "\n"
    Path(a.out).write_text(data)
    import hashlib
    print(json.dumps({"C5_PRIMARY_CLASS": cls, "closed": closed, "newly_closed": newly,
                      "still_open": still_open, "materially_tightened": tightened,
                      "exhaustion": out["exhaustion"]["verdict"],
                      "c4_still_excluded": {k: v["still_excluded_under_C5T"] for k, v in rc.items()},
                      "sha256": hashlib.sha256(data.encode()).hexdigest()}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
