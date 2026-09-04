"""P5Y K1 binding campaign -- emit the frozen machine-readable config.

DESIGN ARTIFACT. Pure arithmetic; no certified numerics; non-result-bearing.
Every numeric constant is either (a) carried verbatim from a completed gate
artifact, or (b) DERIVED here by an explicit formula that is itself frozen.
"""
from __future__ import annotations

import json
import pathlib
from fractions import Fraction

HERE = pathlib.Path(__file__).resolve().parent
NS = HERE.parent
CFG = NS / "config"
MAN = NS / "manifests"

# ------------------------------------------------------ carried from gates
C_SR_ZERO = 1205.9371382854872          # Gate-2B /cross_check_e0/C_SR_0
C_SR_QUARTER = 187.7471962405577        # Gate-2B /representative/1_4/C_SR
C_CERTIFIED_CAP = 1315.7894736842106    # sr_monotone_contraction.json  25000/19
N_PANELS_REF = 30                       # Gate-2E reference patch panel count
GATE2E_W_PANEL_MAX = 3.550874083164312e-05
GATE2E_DELTA_CANDIDATE_MAX = 5.340432825927636e-04

# ------------------------------------------------------ frozen metric (2E/2F)
BOUNDARY = 2.0
SLACK_R = 2.0
ALPHA = 0.1
W_TARGET = ALPHA * SLACK_R
LEDGER_FRACTIONS = {
    "B_cover": Fraction(1, 4),
    "B_candidate": Fraction(1, 5),
    "B_kernel": Fraction(1, 5),
    "B_other": Fraction(1, 5),
    "B_rounding": Fraction(1, 20),
    "B_interval": Fraction(1, 20),
}
RESERVE_FRACTION = Fraction(1, 20)
LOCAL_GATE_COMPONENTS = ["B_candidate", "B_kernel", "B_interval", "B_rounding"]


def budget_ledger() -> dict:
    wt = Fraction(1, 5)  # w_target = 0.2 exactly
    absolute = {k: float(v * wt) for k, v in LEDGER_FRACTIONS.items()}
    absolute["B_resolvent"] = 0.0
    allocated = sum(LEDGER_FRACTIONS.values())
    local = float(sum(LEDGER_FRACTIONS[k] for k in LOCAL_GATE_COMPONENTS) * wt)
    return {
        "scientific_target": "R_MAX_LT_2",
        "metric_type": "ABSOLUTE",
        "boundary": BOUNDARY,
        "slack_R": SLACK_R,
        "alpha": ALPHA,
        "w_target": W_TARGET,
        "ledger_fractions": {k: [v.numerator, v.denominator]
                             for k, v in LEDGER_FRACTIONS.items()},
        "ledger_absolute": absolute,
        "reserve_fraction": [RESERVE_FRACTION.numerator, RESERVE_FRACTION.denominator],
        "reserve_absolute": float(RESERVE_FRACTION * wt),
        "allocated_fraction_sum": [allocated.numerator, allocated.denominator],
        "allocated_plus_reserve_eq_one": allocated + RESERVE_FRACTION == 1,
        "local_gate_components": LOCAL_GATE_COMPONENTS,
        "local_gate_budget": local,
        "B_resolvent_zero_reason":
            "C is a MULTIPLICATIVE amplifier of local error, never an additive "
            "budget line; giving it an additive share would double-count.",
        "redistribution_allowed": False,
        "reserve_drawable": False,
        "post_result_rebudgeting_allowed": False,
        # ---- the m=1 tightening, DERIVED here (see CHECKPOINT.md 6.1)
        "assembly_coefficient_max_over_m": 1.0,
        "assembly_coefficient_argmax_m": 1,
        "gate2e_assembly_coefficient_used": 0.5,
        "gate2e_coefficient_was_m2_specific": True,
        "delta_max_formula": "LOCAL_GATE_BUDGET / C_D(e_lo)",
        "w_panel_max_formula": "LOCAL_GATE_BUDGET / ( C_D(e_lo) * n_panels(patch) )",
        "reference_cell": {
            "detector": "SR", "e": 0.25, "patch": [17, 11],
            "C_D": C_SR_QUARTER, "n_panels": N_PANELS_REF,
            "delta_max": local / C_SR_QUARTER,
            "w_panel_max": local / (C_SR_QUARTER * N_PANELS_REF),
            "gate2e_w_panel_max": GATE2E_W_PANEL_MAX,
            "tightening_factor_vs_gate2e": (local / (C_SR_QUARTER * N_PANELS_REF))
                                           / GATE2E_W_PANEL_MAX,
            "gate2e_delta_candidate_max_carried": GATE2E_DELTA_CANDIDATE_MAX,
            "delta_max_provenance_note":
                "Gate-2E carried 5.340433e-04; the frozen FORMULA above is "
                "authoritative and yields 5.326287e-04 at the same drift. The "
                "0.27% difference is a Gate-2E constant-formation artifact and "
                "is recorded, not silently adopted; the formula is stricter.",
        },
        "worst_case_C_at_e0": {
            "detector": "SR", "C_D": C_SR_ZERO,
            "delta_max": local / C_SR_ZERO,
        },
        "C_evaluated_at": "e_lo, the smallest |e| of the cell (worst case by M2)",
    }


P1 = {
    "eps_P1": 1e-3,
    "P1_RULE_TARGET_EXPR": "(1 - eps_P1) * 1e-9",
    "P1_CHECK_THRESHOLD": 1e-9,
    "P1_HEADROOM_GUARD": 1e-6,
    "P1_RULE_WORKPREC_BITS": 512,
    "rule_and_check_distinct": True,
    "headroom_rel_expr": "(P1_CHECK_THRESHOLD - E_d) / P1_CHECK_THRESHOLD",
    "expected_headroom_rel": 1e-3,
    "headroom_over_guard": 1000.0,
    "gate2f_defect_repaired":
        "P1_RULE_TARGET must be evaluated INSIDE workprec(512); Gate-2F evaluated "
        "it at ambient module precision, giving a 2.22e-16 relative provenance "
        "discrepancy against Gate-2E. Verdict-irrelevant there; fixed here.",
}

COMPLEXITY = {
    "score_formula": "(deg_a + 1) * (deg_b + 1) * (composed_z_degree + 1)",
    "hard_bidegree": {"SR": [16, 16], "CUSUM": [12, 12]},
    "composed_z_degree": {"SR": 128, "CUSUM": 145},
    "measured_scores": {"SR": 17 * 17 * 129, "CUSUM": 13 * 13 * 146},
    "PRODUCTION_COMPLEXITY_CEILING": 60000,
    "headroom": {"SR": 60000 / (17 * 17 * 129), "CUSUM": 60000 / (13 * 13 * 146)},
    "rejects_bidegree_20": 21 * 21 * 161,
    "gate2c_defect_score_order": 122 * 122 * 366,
    "pilot_era_ceiling_not_used": 100000,
    "fires_before_kernel_construction": True,
}

PRECISION = {
    "SR_production_bits": 256,
    "CUSUM_production_bits": 256,
    "P1_rule_workprec_bits": 512,
    "PRECISION_ESCALATION_ALLOWED": False,
    "DEGREE_ADAPTATION_ALLOWED": False,
    "POST_RESULT_REBUDGETING_ALLOWED": False,
    "on_interval_too_wide": "STOP (S10 / PRECISION_FAILURE); never silent rerun",
}


def main() -> int:
    CFG.mkdir(exist_ok=True)
    payloads = {
        "budget_ledger.json": budget_ledger(),
        "p1_rule.json": P1,
        "complexity_guard.json": COMPLEXITY,
        "precision_policy.json": PRECISION,
    }
    for name, obj in payloads.items():
        obj = {"schema": f"rebaseguard.p5y.k1.{name[:-5]}.v1", "binding": True, **obj}
        (CFG / name).write_text(json.dumps(obj, indent=1, sort_keys=False) + "\n")
        print("wrote config/" + name)
    b = payloads["budget_ledger.json"]
    print("  local_gate_budget      =", b["local_gate_budget"])
    print("  ref delta_max          =", b["reference_cell"]["delta_max"])
    print("  ref w_panel_max        =", b["reference_cell"]["w_panel_max"])
    print("  tightening vs Gate-2E  =", b["reference_cell"]["tightening_factor_vs_gate2e"])
    print("  allocated+reserve == 1 :", b["allocated_plus_reserve_eq_one"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
