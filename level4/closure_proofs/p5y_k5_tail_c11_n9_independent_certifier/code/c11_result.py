"""C11 Phase 13 -- the N9 verdict, under the criterion frozen in N9_GATE_C11.json.

Every number here was produced by the independent certifier. The original's values are read from
REGISTRY_C2 only at comparison time.
"""
from __future__ import annotations

import pathlib
import sys
from fractions import Fraction as F

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import c11_common as C

GATE_SHA = "84e1128d1fca20bb"
CELL = 307


def main() -> int:
    reg = C.load(C.C2 / "evidence" / "registry_c2" / "REGISTRY_C2.json")
    blk = {b["cell"]: b for b in reg["blocks"]}[CELL]
    tau_orig = F(blk["tau"])
    abar_orig = F(blk["Abar"])
    e_lo, e_hi = F(blk["e_lo"]), F(blk["e_hi"])

    # what the independent certifier achieved, as measured
    independent = {
        "drift_used": "18355/10000",
        "drift_note": ("the cell's centre to four places; chosen as a development value and "
                       "therefore recorded as DEVELOPMENT, not as a governed target execution"),
        "cell_centre_exact": str((e_lo + e_hi) / 2),
        "certified_constant_supersolution": {
            "w": 9000, "certified": True, "margin_lower_bound": 0.1152,
            "depth": 3, "panels": 16,
            "statement": "w >= 1 + K_e w on R, hence E_x[tau] <= w(x) and tau_independent <= 9000"},
        "failed_constant": {"w": 6000, "certified": False, "margin_lower_bound": -0.2565},
        "theoretical_threshold": {
            "value": "1 / min_R h1 ~ 8070",
            "agreement_with_measurement": ("the certificate straddles it exactly -- 9000 certifies, "
                                           "6000 does not -- which is a correctness signal for the "
                                           "implementation, not a tightness signal")},
        "drift_aware_family": {
            "form": "w = A - B(p+m)",
            "tried": [{"A": 9, "B": 1.3, "margin": -4.5243, "certified": False},
                      {"A": 12, "B": 2.0, "margin": -6.4251, "certified": False},
                      {"A": 20, "B": 3.0, "margin": -9.1343, "certified": False}],
            "finding": ("all fail, and the margin WORSENS as the candidate grows. The cause is "
                        "identified and is an engineering limit, not a soundness problem: the "
                        "box-uniform kernel bound takes the widest alarm-free window over each box, "
                        "so at a computationally feasible subdivision depth it over-counts mass "
                        "faster than the drift gain recovers.")},
        "cost": {"depth_3_panels_12_16_seconds": "110-121 per candidate",
                 "scaling": "4x boxes per depth level; depth 5 is ~16x and was not affordable here"},
    }

    ratio = F(9000) / tau_orig
    verdict_reasons = []
    agree = ratio <= 2
    if not agree:
        verdict_reasons.append(
            f"N6 fails: the independent bound 9000 is {float(ratio):.0f}x the original tau "
            f"{float(tau_orig):.6f}, far outside the frozen factor-of-2 criterion")
    verdict_reasons.append(
        "N10 fails independently of the numbers: no blinded comparison was available, because the "
        "original's tau is committed and was read in phase B0 before implementation began")
    verdict_reasons.append(
        "N7 was only partially exercised: precision escalation beyond depth 3 was not affordable")

    out = {
        "schema": "C11_N9_RESULT/1",
        "gate_sha256_prefix": GATE_SHA,
        "target_quantity": "the K5 m=5 tail operator supply at cell 307",
        "original_certifier": {"tau": str(tau_orig), "tau_float": float(tau_orig),
                               "Abar": str(abar_orig), "Abar_float": float(abar_orig),
                               "source": "REGISTRY_C2 block 307"},
        "independent_certifier": independent,
        "comparison": {"independent_bound": 9000, "original_tau": float(tau_orig),
                       "ratio": float(ratio), "criterion": "ratio <= 2", "agrees": bool(agree)},
        "criteria_status": {
            "N1_implementation_independence": "SATISFIED",
            "N2_no_load_bearing_import": "SATISFIED",
            "N3_no_use_of_original_outputs": "SATISFIED",
            "N4_same_frozen_inputs": "SATISFIED",
            "N5_both_sound": "SATISFIED for the independent certifier; the original's soundness is "
                             "not re-litigated by C11",
            "N6_agreement": "FAILED",
            "N7_precision_escalation": "PARTIAL",
            "N8_manufactured_cases": "SATISFIED",
            "N9_mutation_suite": "SATISFIED",
            "N10_seal_before_compare": "FAILED -- not available in this campaign"},
        "N9_VERDICT": "AGREEMENT_INSUFFICIENT",
        "N9_STATUS_AFTER_C11": "OPEN",
        "verdict_reasons": verdict_reasons,
        "WHAT_C11_DID_ESTABLISH": [
            "a second certifier for this problem EXISTS, is implementationally independent, and is "
            "arithmetic-backend independent as well -- exact rationals against numpy + flint.arb",
            "it is SOUND: standard-normal moments exact; (K_e 1) = 1 - h1 to 0.00e+00 at five "
            "states; the box bound dominates pointwise values; the certificate straddles the "
            "theoretical threshold exactly",
            "it produces VALID certified upper bounds on the same quantity with no reuse of the "
            "first certifier",
            "there is NO scientific disagreement: the independent bound is consistent with the "
            "original's, merely far weaker"],
        "WHAT_BLOCKS_CLOSURE": (
            "tightness, not soundness. The box-uniform kernel bound is too loose at affordable "
            "subdivision depth. Closing N9 needs a sharper uniform bound -- one that tracks how the "
            "alarm-free window varies across a box instead of taking the union -- or enough compute "
            "to subdivide far deeper."),
        "EXPLICITLY_NOT_CLAIMED": [
            "that N9 is closed", "that F1 has lapsed",
            "that the C2 adoption floor may be replaced",
            "that any cell is closed or adopted", "that r6 may be created"],
        "compute_boundary": {"NEW_REAL": 0, "OPERATOR_CERTIFICATIONS_OF_THE_ORIGINAL": 0,
                             "AWS": 0, "VULTR": 0, "TOOLCHAIN_PROVISIONED": 0, "guard": "DENY"},
    }
    s = C.write_evidence(C.NS / "evidence" / "n9" / "C11_N9_RESULT.json", out)
    print(f"original tau (cell 307)      : {float(tau_orig):.9f}")
    print(f"independent certified bound  : 9000")
    print(f"ratio                        : {float(ratio):.0f}x   criterion: <= 2")
    print(f"\nN9_VERDICT = {out['N9_VERDICT']}   N9 remains {out['N9_STATUS_AFTER_C11']}")
    for r in verdict_reasons:
        print(f"  - {r}")
    print(f"\nwrote evidence/n9/C11_N9_RESULT.json sha256 {s[:16]}...")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
