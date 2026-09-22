"""C8 Phases 8-10 -- authoritative C5-T inversion, E1 toolchain reconstruction, cost/value frontier,
and route selection under the gate frozen at 55e74332.

The authoritative transport is C5-T, adopted by C5's adjudicator. C2's frozen clause is retained only
as a cross-check. Pass iff M < M_needed_C5T, with the budget read from C5_FORECAST.
"""
from __future__ import annotations

import json
import pathlib
import sys
from decimal import Decimal
from fractions import Fraction as F

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import c8_common as C
import c8_chain as X

OPEN = (306, 307, 308, 309)
GATE_SHA = "55e743320987a1e031c586938216e70839ed8d0ef1e9d518304197563dde9a7a"
D = lambda x: F(Decimal(str(x)))


def main() -> int:
    if C.sha256_file(C.NS / "config" / "DECISION_GATE_C8.json") != GATE_SHA:
        raise SystemExit("the C8 decision gate is not the frozen one")
    ch = X.Chain()
    ver = ch.verify()
    if not ver["all_agree"]:
        raise SystemExit("chain reconstruction failed")

    fc = C.c5_forecast()["cells"]
    c4, c7 = C.c4_cells(), C.c7_certificate()
    lam = F(c7["bounds"][c7["PRIMARY"]["key"]]["value"])
    floors = {k: F(c4[str(k)]["lower_bound_E_a_tau"]) for k in OPEN}
    floors[309] = max(floors[309], lam)
    budget = {k: D(fc[str(k)]["M_needed_C5T"]) for k in OPEN}
    Z = {"A1": F(0), "A2": F(0)}

    # cross-check the reconstruction against C5's own M_used before inverting
    xchk = {}
    for k in OPEN:
        A = dict(ch.committed_supplies(k)["operator_mixed"]["A"])
        mine, theirs = ch.M_of(k, A), D(fc[str(k)]["M_used"])
        xchk[str(k)] = {"M_recomputed": float(mine), "M_used_committed": float(theirs),
                        "abs_err": float(abs(mine - theirs))}
        if abs(mine - theirs) > F(1, 10 ** 12):
            raise SystemExit(f"M reconstruction disagrees with C5 at cell {k}")

    def maxfield(k, A, f_, bud, hi0=F(40)):
        if ch.M_of(k, {**A, f_: F(0)}) >= bud:
            return None
        lo, hi = F(0), hi0
        while ch.M_of(k, {**A, f_: hi}) < bud:
            hi *= 2
        for _ in range(70):
            mid = (lo + hi) / 2
            if ch.M_of(k, {**A, f_: mid}) < bud:
                lo = mid
            else:
                hi = mid
        return lo

    inv = {}
    for k in OPEN:
        A = dict(ch.committed_supplies(k)["operator_mixed"]["A"])
        m, bud = ch.M_of(k, A), budget[k]
        passes = m < bud
        ceil0 = maxfield(k, {**A, **Z}, "A0", bud)
        a0 = maxfield(k, A, "A0", bud)
        a1 = maxfield(k, A, "A1", bud)
        a2 = maxfield(k, A, "A2", bud)
        Af = {**A, "A0": floors[k]}
        a1_at_floor = maxfield(k, Af, "A1", bud)
        row = {
            "M_used": float(m), "M_needed_C5T": float(bud), "passes_now": passes,
            "A_now": {j: float(A[j]) for j in A},
            "Lambda_floor_on_A0": float(floors[k]),
            "A0_ceiling_with_A1_A2_zero": float(ceil0) if ceil0 else None,
            "max_admissible_A0": float(a0) if a0 else None,
            "max_admissible_A1": float(a1) if a1 else None,
            "max_admissible_A2": float(a2) if a2 else None,
            "required_A0_factor": float(F(A["A0"]) / a0) if a0 and F(A["A0"]) > a0 else None,
            "M_at_perfect_A0": float(ch.M_of(k, Af)),
            "A1_ceiling_at_perfect_A0": float(a1_at_floor) if a1_at_floor else None,
            "operator_route_verdict": ("ALREADY_PASSES" if passes else
                                       "FEASIBLE" if (ceil0 and ceil0 > floors[k])
                                       else "MATHEMATICALLY_REFUTED"),
        }
        if passes:
            row["cheapest_sufficient_fact"] = ("NONE -- passes under the authoritative C5-T clause "
                                               "with committed certified supplies. The blocker is "
                                               "ADOPTION, not information.")
        elif a0 and a0 > floors[k]:
            row["cheapest_sufficient_fact"] = (
                f"a certified operator tuple giving A0 <= {float(a0):.6f} (from {float(A['A0']):.6f}, "
                f"a {float(F(A['A0'])/a0):.4f}x tightening); the floor {float(floors[k]):.6f} permits it")
        elif ch.M_of(k, Af) < bud:
            row["cheapest_sufficient_fact"] = f"A0 driven to its floor {float(floors[k]):.6f}"
        elif a1_at_floor:
            row["cheapest_sufficient_fact"] = (
                f"A0 to its floor {float(floors[k]):.6f} AND A1 <= {float(a1_at_floor):.6f} "
                f"(from {float(A['A1']):.6f}, {float(F(A['A1'])/a1_at_floor):.4f}x)")
        else:
            row["cheapest_sufficient_fact"] = ("NONE within the atom-constant family -- refuted")
        inv[str(k)] = row

    # ---------------- Phase 8: E1 toolchain reconstruction ----------------------------------
    reg = C.load(C.C2 / "evidence" / "registry_c2" / "REGISTRY_C2.json")
    per_cell_cpu = [b["arl"]["cpu_seconds"] for b in reg["blocks"]]
    arl = C.load(C.C2 / "evidence" / "registry_c2" / "arl_cell_309.json")
    toolchain = {
        "SOURCE": "version pins read from committed evidence; nothing was installed or queried",
        "python": "3.12.3 (the historical certifier host); 3.14.5 also appears in later records",
        "numpy": "2.5.2", "python_flint": "0.9.0", "flint_library": "3.6.0",
        "arb": "NOT REQUIRED as a separate install -- FLINT 3.x subsumes Arb",
        "producer": ("the operator taboo/arl Chebyshev certifier that produced REGISTRY_C1 and "
                     "REGISTRY_C2 (rule r2, operator_only, certified)"),
        "addresses_already_defined": True,
        "addresses_are_zero_new_real": ("yes -- the programme has consistently classified operator "
                                        "certification as zero-new-real; C1 and C2 each spent "
                                        "CPU-hours of it under that classification"),
        "historical_cost_measured": {
            "per_cell_arl_cpu_seconds": per_cell_cpu,
            "registry_c2_cpu_seconds_total": reg["cpu_seconds_total"],
            "cell_309_bits": arl["bits"], "cell_309_depth": arl["depth"],
            "cell_309_patches": arl["patches"], "cell_309_kernel_calls": arl["kernel_calls"],
            "degree_arl": reg["degree_arl"], "degree_taboo": reg["degree_taboo"],
            "sub_block_max_width": reg["sub_block_max_width"]},
        "current_availability": {"local": C.toolchain_present(),
                                 "note": ("C6 re-measured the programme's worker rebaseguard-vultr-02 "
                                          "read-only and found the same absence; AWS is forbidden. "
                                          "There is NO certifying host in scope.")},
    }
    base = reg["cpu_seconds_total"]
    # The three profiles must describe THE SAME scientific scope on different hardware, otherwise
    # "FAST" is meaningless. The first version scaled the work allowance with the core count, so
    # RECOMMENDED and FAST reported identical wall time. Work allowance is now fixed per profile's
    # stated scope and only the parallelism varies within a scope.
    SCOPE = {"targeted": (4, "cells 307 and 308 only, at C2's degree and a modestly finer partition"),
             "full": (16, "all four open cells, deeper sub-block sweep")}

    def prof(cores, ram, disk, mult, scope_note, eff=0.75):
        cpu_h = base * mult / 3600.0
        wall = cpu_h / (cores * eff)
        return {"cores": cores, "RAM_GB": ram, "disk_GB": disk,
                "work_allowance_vs_C2_registry": f"{mult}x",
                "cpu_hours_estimate": round(cpu_h, 2),
                "wall_time_hours_estimate": round(wall, 2),
                "parallel_efficiency_assumed": eff, "scope": scope_note}

    profiles = {
        "MINIMUM": prof(2, 4, 10, SCOPE["targeted"][0], SCOPE["targeted"][1]),
        "RECOMMENDED": prof(8, 16, 40, SCOPE["full"][0], SCOPE["full"][1]),
        "FAST": prof(32, 64, 100, SCOPE["full"][0], SCOPE["full"][1] + ", same scope as RECOMMENDED"),
        "BASIS": (f"C2 re-certified 5 tail cells in {base:.0f} CPU-seconds total at degree "
                  f"{reg['degree_arl']}, depth 2, sub-block width <= {reg['sub_block_max_width']}. "
                  f"Per-cell arl cost was {min(per_cell_cpu):.1f}-{max(per_cell_cpu):.1f} s."),
        "CAVEAT": ("ESTIMATES extrapolated from ONE committed measurement, not a benchmark. The "
                   "dominant unknown is not CPU: it is whether a finer partition tightens A0 at all. "
                   "C2 measured its own refinement as NON-MONOTONE -- D_lo improved but tau got "
                   "1.90-2.24% WORSE, and the net A0 gain was only 4.5-4.9%. The 1.1203x tightening "
                   "cell 307 needs is therefore NOT guaranteed by buying more CPU, and no host "
                   "profile can make it so."),
    }

    # ---------------- Phase 9: the frontier -------------------------------------------------
    frontier = {
        "R1": {"max_leverage": "ZERO -- perfect information changes Gamma by exactly 0",
               "minimum_useful_improvement": "n/a", "zero_new_real": True,
               "needs_operator_cert": False, "needs_toolchain": False, "needs_remote": False,
               "cpu_hours": 0, "governance": "none",
               "class": "LOW_LEVERAGE",
               "why": "raises the A0 floor; strengthens exclusions; cannot close a cell"},
        "R2": {"max_leverage": "ZERO -- perfect information changes Gamma by exactly 0",
               "minimum_useful_improvement": "n/a", "zero_new_real": True,
               "needs_operator_cert": False, "needs_toolchain": False, "needs_remote": False,
               "cpu_hours": 0, "governance": "none",
               "class": "LOW_LEVERAGE",
               "why": "same structural reason as R1"},
        "R3": {"max_leverage": "closes 307 and 308; CANNOT close 309",
               "minimum_useful_improvement": (f"A0 tightening of "
                                              f"{inv['307']['required_A0_factor']:.4f}x at cell 307"),
               "zero_new_real": True, "needs_operator_cert": True, "needs_toolchain": True,
               "needs_remote": "probably -- no certifying host is in scope",
               "cpu_hours": profiles["RECOMMENDED"]["cpu_hours_estimate"],
               "cpu_hours_targeted_307_308": profiles["MINIMUM"]["cpu_hours_estimate"],
               "governance": "host provisioning is a separately governed prerequisite (C6)",
               "class": "TOOLCHAIN_BLOCKED"},
        "R4": {"max_leverage": "closes every open cell INCLUDING 309",
               "minimum_useful_improvement": "a certified order-3 surrogate",
               "zero_new_real": False, "needs_operator_cert": True, "needs_toolchain": True,
               "needs_remote": True, "cpu_hours": "unknown",
               "governance": "a new governed K1 address; NOT the R-stage",
               "class": "NEW_REAL_BLOCKED"},
    }

    # ---------------- Phase 10: selection under the frozen gate ------------------------------
    gate = C.load(C.NS / "config" / "DECISION_GATE_C8.json")
    adoption_only = [k for k in OPEN if inv[str(k)]["passes_now"]]
    refuted = [k for k in OPEN if inv[str(k)]["operator_route_verdict"] == "MATHEMATICALLY_REFUTED"]
    feasible = [k for k in OPEN if inv[str(k)]["operator_route_verdict"] == "FEASIBLE"]
    selection = {
        "gate_sha256": GATE_SHA,
        "rule_1_adoption_first": {
            "cells": adoption_only,
            "finding": ("cell 306 passes the authoritative C5-T clause under committed certified "
                        "supplies. Its blocker is ADOPTION, not information. Under the gate's rule 1 "
                        "no new information may be bought for it."),
            "action_for_C9": "a governance adoption step, not a science campaign"},
        "rule_2_analytic_zero_new_real": {
            "candidates": ["R1", "R2"],
            "result": ("both have ZERO closure leverage by the gate's leverage test. They are "
                       "excluded as closure routes. This is the decisive negative of C8."),
            "selected": False},
        "rule_3_operator_certification": {
            "candidate": "R3", "zero_new_real": True,
            "leverage_material": True,
            "cells_it_can_close": feasible,
            "cells_it_cannot": refuted,
            "minimum_useful_improvement": frontier["R3"]["minimum_useful_improvement"],
            "producer_and_toolchain_known": True,
            "blocked_by": "no certifying host in scope; provisioning is separately governed",
            "selected": True},
        "rule_4_new_real": {"candidate": "R4", "selected": False,
                            "why": ("forbidden while R3, a materially competitive zero-new-real "
                                    "route, remains untested -- and R4 is the only route with "
                                    "leverage on 309, so it is the successor to R3, not its rival")},
        "OUTCOME": "NEXT_ROUTE_OPERATOR_CERT",
        "selected_route": "R3 -- E1 operator certification, targeted at cell 307 first",
        "why_307_first": ("it has the smallest sufficient information requirement anywhere in the "
                          "tail: a single A0 tightening of "
                          f"{inv['307']['required_A0_factor']:.4f}x, with the certified floor "
                          f"{inv['307']['Lambda_floor_on_A0']:.6f} leaving ample room"),
        "R_stage": "NOT AUTHORIZED", "guard": "DENY",
    }

    # The pre-C7 floor is load-bearing for the attribution claim: C8 must show that the cell-309
    # refutation ALREADY held under C4's weaker floor, so that C7's strengthening is recorded as
    # widening it rather than creating it. Emitted here because the README quotes it.
    c4_floor_309 = F(c4["309"]["lower_bound_E_a_tau"])
    ceil309 = F(str(inv["309"]["A0_ceiling_with_A1_A2_zero"]))
    attribution = {
        "A0_ceiling_309_C5T": float(ceil309),
        "C4_floor_309_pre_C7": float(c4_floor_309),
        "C7_PRIMARY_floor_309": float(floors[309]),
        "refuted_under_C4_floor": bool(c4_floor_309 > ceil309),
        "refuted_under_C7_floor": bool(floors[309] > ceil309),
        "C7_raised_floor_by": float(floors[309] - c4_floor_309),
        "conclusion": ("the refutation of cell 309 ALREADY held under C4's weaker floor; C7's "
                       "strengthening WIDENED it and did not create it. C8 claims no credit for it, "
                       "and the underlying exclusion is C4's published result."),
    }

    out = {"schema": "C8_DECISION/1", "gate_sha256": GATE_SHA,
           "cell_309_refutation_attribution": attribution,
           "authoritative_clause": "C5-T (adopted by C5's adjudication); C2 frozen clause cross-checks only",
           "M_reconstruction_crosscheck_vs_C5": xchk,
           "phase4_inversion_C5T": inv, "phase8_toolchain": toolchain,
           "phase8_host_profiles": profiles, "phase9_frontier": frontier,
           "phase10_selection": selection,
           "counterfactual_labelling": ("every A tuple that is not a committed certified supply is "
                                        "COUNTERFACTUAL_ONLY and is not evidence")}
    s = C.write_evidence(C.NS / "evidence" / "phase9" / "C8_DECISION.json", out)

    print("M reconstruction vs C5 M_used: max err "
          f"{max(v['abs_err'] for v in xchk.values()):.1e}\n")
    print(f"{'cell':>5} {'M_used':>12} {'M_need C5T':>12} {'verdict':>24} {'cheapest sufficient fact'}")
    for k in OPEN:
        r = inv[str(k)]
        print(f"{k:>5} {r['M_used']:>12.9f} {r['M_needed_C5T']:>12.9f} "
              f"{r['operator_route_verdict']:>24} {r['cheapest_sufficient_fact'][:60]}")
    print(f"\nOUTCOME: {selection['OUTCOME']}  ->  {selection['selected_route']}")
    for nm in ("MINIMUM", "RECOMMENDED", "FAST"):
        q = profiles[nm]
        print(f"  {nm:<12} {q['cores']:>3} cores {q['RAM_GB']:>3} GB  work {q['work_allowance_vs_C2_registry']:>4}  "
              f"{q['cpu_hours_estimate']:>6.2f} CPU-h  {q['wall_time_hours_estimate']:>6.2f} wall-h")
    print(f"wrote evidence/phase9/C8_DECISION.json sha256 {s[:16]}...")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
