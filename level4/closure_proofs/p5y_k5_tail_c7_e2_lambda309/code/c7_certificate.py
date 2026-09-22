"""C7 Phases 9-11 -- final certified evaluation, downstream feasibility, family exhaustion.

Every kill gate in the frozen gate is enforced here and REFUSES rather than warns. The verdict rule
contains no tuned threshold: it compares C7's output against C4's own published numbers only.
"""
from __future__ import annotations

import json
import pathlib
import sys
from fractions import Fraction as F

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import c7_common as C
import c7_gaussian as G
import c7_theorem as T

E_LO, E_HI, K, H = F(19839101, 10000000), F(2092283, 1000000), F(1, 2), F(5)
N = 64
A_GRID = [F(j, 4) for j in range(8, 25)]
GATE_SHA = "9f7083b9ef45f48ede9addcc8374005187785c789cf7a24403bed2e519d4a604"


class KillGate(Exception):
    pass


def main() -> int:
    gate_path = C.NS / "config" / "FEASIBILITY_GATES_C7.json"
    gate_sha = C.sha256_file(gate_path)
    fired: list[str] = []

    def kg(name: str, ok: bool, detail: str) -> None:
        if not ok:
            fired.append(f"{name}: {detail}")

    # KG6 / KG7 -- the frozen model
    kg("KG6", C.sha256_file(C.MODEL) == C.MODEL_SHA256, "frozen CUSUM model file changed")
    kg("KG7", K + H == F(11, 2), f"K + H = {K + H} != 11/2")
    kg("GATE", gate_sha == GATE_SHA, f"gate sha {gate_sha} != frozen {GATE_SHA}")

    c4, c5 = C.c4_cell309(), C.c5_critical_a0()
    B4 = F(c4["lower_bound_E_a_tau"])
    crit = F(str(c5["critical_A0_C5T"]))
    A0_cert = F(str(c4["A0_certified_float"]))

    part = [F(j) * H / N for j in range(1, N + 1)]
    bounds: dict[str, dict] = {}

    t1 = T.lambda_lower(E_LO, K, H)
    bounds["L1_tier1"] = {"value": t1["C7_bound_lower"], "dependencies": [],
                          "derivation": "Theorem C7-E2 tier 1: E[R] >= inf psi over [0,H]"}
    for src in ("elementary", "registry", "lorden"):
        cert = T.certified_U(src, E_LO, K, H, A_GRID if src == "elementary" else None)
        r = T.lambda_lower_tier_k(E_LO, K, H, cert, part)
        bounds[f"L3_{src}"] = {"value": r["L_lower"], "dependencies": r["U_dependencies"],
                               "derivation": f"Theorem C7-E2c multi-tier, N = {N}, U from {src}",
                               "U_used": str(cert["value"]), "E_R_lower": str(r["E_R_lower"])}

    # KG4 -- tier-k at k = 1 must reproduce tier 1 exactly
    cert_l = T.certified_U("lorden", E_LO, K, H)
    k1 = T.lambda_lower_tier_k(E_LO, K, H, cert_l, [H])
    kg("KG4", k1["L_lower"] == t1["C7_bound_lower"],
       f"tier-k at k=1 gave {k1['L_lower']} != tier-1 {t1['C7_bound_lower']}")

    # KG1 / KG5
    ceiling = (G.Iv(H + T.U_lorden(E_LO, K, H)["E_R_upper"], H + T.U_lorden(E_LO, K, H)["E_R_upper"])
               / G.Iv(G.E_excess(E_LO, K).lo, G.E_excess(E_LO, K).lo)).hi
    for name, b in bounds.items():
        kg("KG1", b["value"] > B4, f"{name} = {b['value']} does not exceed C4's floor {B4}")
        kg("KG5", b["value"] <= A0_cert and b["value"] <= ceiling,
           f"{name} exceeds a certified upper bound (A0 {float(A0_cert)}, ceiling {float(ceiling)})")

    # KG8 -- the mutation suite must have passed
    mut_p = C.NS / "evidence" / "mutations" / "C7_MUTATIONS.json"
    mut = C.load(mut_p) if mut_p.exists() else {}
    kg("KG8", mut.get("MUTATION_CLASS") == "PASS",
       f"mutation class {mut.get('MUTATION_CLASS')!r}, undetected {mut.get('undetected')}")
    kg("KG8b", mut.get("mirror_equivalence_asserted") is True, "mirror equivalence not asserted")

    # KG9 -- compute boundary
    b0 = C.load(C.NS / "evidence" / "b0" / "C7_B0_AUDIT.json")
    cb = b0["compute_boundary"]
    kg("KG9", all(cb[k] == 0 for k in ("NEW_REAL", "SCIENTIFIC_KERNEL_EVALUATIONS",
                                       "REMOTE_HOSTS_CONTACTED", "TOOLCHAIN_PROVISIONED"))
       and cb["guard"] == "DENY" and cb["EXECUTION_AUTHORIZED"] is False,
       f"compute boundary violated: {cb}")
    kg("KG9b", b0["B0_CLASS"] == "PASS", f"B0 class {b0['B0_CLASS']!r}")

    if fired:
        print("KILL GATES FIRED -- C7_CLASS = REFUSED")
        for f_ in fired:
            print(f"  {f_}")
        C.write_evidence(C.NS / "evidence" / "certificate" / "C7_CERTIFICATE.json",
                         {"schema": "C7_CERTIFICATE/1", "C7_CLASS": "REFUSED", "kill_gates_fired": fired})
        return 1

    # ---- selection, per the gate's frozen rule --------------------------------------------------
    free = {k: v for k, v in bounds.items() if not v["dependencies"]}
    primary_key = max(free, key=lambda k: free[k]["value"])
    overall_key = max(bounds, key=lambda k: bounds[k]["value"])
    primary, overall = bounds[primary_key], bounds[overall_key]

    def pct(x, base):
        return float(100 * (F(x) - F(base)) / F(base))

    c4_margin = pct(B4, crit)
    p_margin = pct(primary["value"], crit)
    C7_CLASS = ("STRENGTHENED" if primary["value"] > B4 and p_margin > c4_margin
                else "MARGINAL" if overall["value"] > B4 else "NO_IMPROVEMENT")

    # ---- Phase 10: downstream feasibility against C5-T (FEASIBILITY_ONLY) ----------------------
    downstream = {
        "scope": "FEASIBILITY_ONLY -- no cell status changes, no closure is claimed, guard stays DENY",
        "exclusion_test": c4["gate_sha256"] and
        "cell 309 is EXCLUDED iff the certified floor on E_a[tau] exceeds the critical A0",
        "critical_A0_C5T": str(crit),
        "C4_margin_percent": c4_margin,
        "C7_primary_margin_percent": p_margin,
        "margin_multiple": float(F(str(p_margin)) / F(str(c4_margin))),
        "adverse_move_in_critical_A0_now_tolerated_percent": p_margin,
        "C5T_consumed_of_C4_margin_percent": float(
            100 * (F(str(c4["slack_over_critical_percent"])) - F(str(c5["slack_percent_C5T"])))
            / F(str(c4["slack_over_critical_percent"]))),
        "interpretation": (
            "C4's exclusion tolerated a 0.94% adverse move in the critical A0. A single successor, C5-T, "
            "had already consumed 63% of C4's original margin. Under C7's PRIMARY bound the exclusion "
            f"tolerates {p_margin:.4f}%, so a C5-T-sized move no longer threatens it. This is a statement "
            "about the ROBUSTNESS of an existing exclusion, not a new closure."),
    }

    # ---- Phase 11: scoped exhaustion of the E2 analytic family ---------------------------------
    exhaustion = {
        "family": "E2 -- overshoot corrections to the C4 bound H/E[V] using only the increment law",
        "analytic_ceiling": str(ceiling), "analytic_ceiling_float": float(ceiling),
        "ceiling_derivation": ("(H + sup provable E[R]) / E[V], with E[R] at Lorden's upper bound. No "
                               "choice of partition, split points or U can exceed this, because it is "
                               "what the family yields when E[R] is known exactly at its largest "
                               "provable value."),
        "certified_A0_at_309": str(A0_cert),
        "family_reaches_certified_A0": bool(ceiling >= A0_cert),
        "conclusion": ("The E2 family CANNOT reach the certified operator constant A0 = 4.867216117, "
                       "so it can never make the cell-309 blocker vanish on its own. It does not need "
                       "to: the exclusion test is against the critical A0, which it clears by "
                       f"{p_margin:.4f}%. The remaining headroom inside the family is the gap between "
                       f"the primary bound and the ceiling, i.e. up to "
                       f"{pct(ceiling, primary['value']):.4f}% more, obtainable only by sharpening the "
                       "lower bound on E[R] toward its true value."),
        "what_would_be_needed_to_go_further": [
            "S2: a bound on E[tau] - E[tau'], the cost of the clipping majorant. Needs a kernel "
            "evaluation or new operator information; outside C7's boundary.",
            "S4: the gap between sup over the cell and the value at e_lo. Needs operator information.",
            "a sharper two-sided handle on E[R] than the mean-residual-life argument supplies.",
        ],
    }

    out = {
        "schema": "C7_CERTIFICATE/1",
        "C7_CLASS": C7_CLASS,
        "cell": C.CELL, "detector": C.DETECTOR, "m": C.M,
        "gate_sha256": gate_sha,
        "model_sha256": C.MODEL_SHA256,
        "evaluated_at_e": str(E_LO), "K": str(K), "H": str(H), "N_partition": N,
        "kill_gates_fired": [],
        "baseline_C4": {"value": str(B4), "float": float(B4), "margin_percent": c4_margin},
        "bounds": {k: {"value": str(v["value"]), "float": float(v["value"]),
                       "vs_C4_percent": pct(v["value"], B4),
                       "margin_over_critical_A0_percent": pct(v["value"], crit),
                       "dependencies": v["dependencies"], "derivation": v["derivation"],
                       **({"U_used": v["U_used"], "E_R_lower": v["E_R_lower"]} if "U_used" in v else {})}
                   for k, v in bounds.items()},
        "PRIMARY": {"key": primary_key, "value": str(primary["value"]),
                    "float": float(primary["value"]),
                    "why": "the largest bound with an EMPTY dependency set, per the gate's selection rule"},
        "MAX_OVER_ALL": {"key": overall_key, "value": str(overall["value"]),
                         "float": float(overall["value"]), "dependencies": overall["dependencies"]},
        "phase10_downstream_feasibility": downstream,
        "phase11_family_exhaustion": exhaustion,
        "compute_boundary": cb,
        "permitted_conclusions": C.load(gate_path)["permitted_conclusions"],
        "forbidden_conclusions": C.load(gate_path)["forbidden_conclusions"],
    }
    p = C.NS / "evidence" / "certificate" / "C7_CERTIFICATE.json"
    s = C.write_evidence(p, out)

    print(f"C7_CLASS = {C7_CLASS}   (no kill gates fired)\n")
    print(f"{'bound':<16} {'value':>14} {'vs C4':>9} {'margin':>9}  dependencies")
    for k, v in out["bounds"].items():
        mark = " <- PRIMARY" if k == primary_key else ""
        print(f"  {k:<14} {v['float']:>14.9f} {v['vs_C4_percent']:>8.4f}% "
              f"{v['margin_over_critical_A0_percent']:>8.4f}%  {v['dependencies'] or 'NONE'}{mark}")
    print(f"\nC4 floor {float(B4):.9f} at margin {c4_margin:.4f}%")
    print(f"PRIMARY  {float(primary['value']):.9f} at margin {p_margin:.4f}%  "
          f"({downstream['margin_multiple']:.2f}x C4's margin)")
    print(f"\nE2-family ceiling {float(ceiling):.9f}; reaches certified A0 "
          f"{float(A0_cert):.9f}? {exhaustion['family_reaches_certified_A0']}")
    print(f"\nwrote {p.relative_to(C.REPO)}  sha256 {s[:16]}...")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
