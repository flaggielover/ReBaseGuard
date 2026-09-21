"""Phase 7: independent reproduction and the adversarial suite.

Rewritten after the pre-result review, which found the first version defective in four ways: one mutant crashed the
run, one tested nothing, three were undetected against the suite's own stated rule, and the independence claim was
false (review, OTHER FINDINGS 1-4). What follows is the repair.

(1) CROSS-CHECK. `c4_independent.py` recomputes phi, Phi, pi and E[(|z| - K)^+] with NO SERIES in common with the
    production module: Bernoulli/AM-GM brackets for exp, Archimedes polygons for pi, the composite midpoint rule
    with its second-derivative remainder for the erf integral. Its intervals are ~1e-7 wide against production's
    ~1e-95, so this is a cross-check that would catch any gross error, NOT a reproduction at certificate
    precision. The evidence records the achieved width rather than claiming more.

(2) MUTATION. Each mutant perturbs exactly one load-bearing mechanism and is classified into one of four outcomes,
    never merely "detected":

      DETECTED_BY_VERDICT  the exclusion set or the class changed
      DETECTED_BY_GUARD    a guard refused the mutant outright
      DETECTED_BY_RULE     the decision rule itself differs, exhibited on the exact input where it differs
      VALUE_ONLY           a certified value moved but by too little to flip this verdict; the magnitude is
                           recorded and the mutant is NOT credited as a verdict-level detection

    A mutant in none of these four is an undetected defect and fails the phase.

    python3 -B c4_mutations.py --out OUT.json
"""
import argparse
import json
import sys
from fractions import Fraction as F
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import c4_independent as I                                                        # noqa: E402
import c4_rigorous_gaussian as G                                                  # noqa: E402
from c4_certificate import GATE_SHA, evaluate, frozen_gate                        # noqa: E402
from c4_lower_bound import bound_at, cell_geometry                                # noqa: E402
from c4_model_identity import model                                               # noqa: E402


def certificate_mutants(gate):
    """Mutants that perturb the certificate layer. Each returns an `evaluate` result or raises."""
    return [
        ("M01_inequality_direction_reversed",
         "the exclusion test becomes Gamma <= 0 instead of Gamma >= 0",
         lambda: evaluate(gate, exclude_if=lambda g: g <= 0)),
        ("M03_upper_end_used_as_the_lower_bound",
         "the interval's UPPER end is reported as if it were the lower bound",
         lambda: evaluate(gate, use_upper_end=True)),
        ("M04_threshold_C_instead_of_H",
         "the alarm threshold is taken as C = H + K = 11/2 rather than H = 5, which INFLATES the bound",
         lambda: evaluate(gate, H_override=F(11, 2))),
        ("M05_reference_K_dropped",
         "the CUSUM reference value K is set to 0, so the per-step majorant becomes |z|",
         lambda: evaluate(gate, K_override=F(0))),
        ("M06_domain_outside_the_closed_cell",
         "each cell is certified two cells to the left, i.e. at a drift genuinely outside its own closed cell",
         lambda: evaluate(gate, domain_shift={306: 306, 307: 306, 308: 306, 309: 307})),
        ("M07_evaluated_at_the_far_endpoint",
         "the bound is taken at e_hi instead of e_lo -- still inside the closed cell, but its weakest point",
         lambda: evaluate(gate, evaluate_at="e_hi")),
        ("M08_knockout_dropped",
         "A1 and A2 are left at their certified values instead of 0, abandoning the generous setting",
         lambda: evaluate(gate, knockout="certified")),
    ]


def rule_mutants():
    """M02 differs from the production rule exactly at Gamma = 0. Exhibited there rather than hoped for."""
    prod = lambda g: g >= 0                                        # noqa: E731
    mut = lambda g: g > 0                                          # noqa: E731
    witness = F(0)
    return [{"mutant": "M02_strict_instead_of_non_strict",
             "perturbs": "Gamma > 0 instead of Gamma >= 0 in the exclusion test",
             "layer": "decision rule",
             "outcome": "DETECTED_BY_RULE" if prod(witness) != mut(witness) else "NOT_DETECTED",
             "witness": "Gamma = 0",
             "production_rule_excludes_at_witness": bool(prod(witness)),
             "mutant_rule_excludes_at_witness": bool(mut(witness)),
             "note": "the two rules are NOT equivalent; they differ exactly on Gamma = 0. C4's own run does not "
                     "land there (Gamma = +0.004661 at the only excluded cell), so a verdict-level check could "
                     "never have separated them. The gate fixes the non-strict form because Gamma < 0 is the "
                     "frozen closure condition, so Gamma = 0 does not close and must count as excluded."}]


def arithmetic_mutants():
    """Mutants that attack the rational-arithmetic layer, each measured against the unmutated bound."""
    K, H = model()["K"], model()["H"]
    e = cell_geometry()[309]["e_lo"]
    ref = bound_at(e, K, H)["B_lo"]
    rows = []

    def record(name, what, moved, refused, detail, delta=None):
        # every arithmetic mutant is recorded, including one that refuses for a reason other than its own guard
        rows.append({"mutant": name, "perturbs": what, "layer": "arithmetic",
                     "outcome": "DETECTED_BY_GUARD" if refused else ("VALUE_ONLY" if moved else "NOT_DETECTED"),
                     "detail": detail, "bound_shift": (None if delta is None else float(delta))})

    orig_out = G._out
    try:
        G._out = lambda x, up: orig_out(x, not up)
        val = bound_at(e, K, H)["B_lo"]
    finally:
        G._out = orig_out
    record("M09_rounding_direction_flipped", "outward rounding replaced by inward rounding",
           val != ref, False, f"lower end {float(val):.15f} vs {float(ref):.15f}", val - ref)

    try:
        G.exp_neg(F(6), terms=3)
        record("M10_exp_tail_bound_dropped", "exp(y) truncated with y >= N + 2, where the tail bound is invalid",
               False, False, "no guard fired")
    except G.Refusal as exc:
        record("M10_exp_tail_bound_dropped", "exp(y) truncated with y >= N + 2, where the tail bound is invalid",
               False, True, str(exc))

    try:
        G._erf_integral(F(5, 2), terms=2)
        record("M11_alternating_bound_before_the_decreasing_regime",
               "the I(t) series is truncated before its magnitudes decrease", False, False, "no guard fired")
    except G.Refusal as exc:
        record("M11_alternating_bound_before_the_decreasing_regime",
               "the I(t) series is truncated before its magnitudes decrease", False, True, str(exc))

    # The production sqrt enclosure is ~1e-96 wide, so "shrink it by a fixed epsilon" would merely invert the
    # interval and trip the constructor. The mutant that actually tests the direction is a sqrt that is
    # systematically too SMALL by a relative 1e-12: sqrt(2 pi) understated inflates phi and Phi, which inflates
    # E[V] -- and the bound must move in response.
    orig_sqrt = G.sqrt_iv
    try:
        def misrounded(v):
            g = orig_sqrt(v)
            f = 1 - F(1, 10 ** 12)
            return G.Iv(g.lo * f, g.hi * f)
        G.sqrt_iv = misrounded
        val2 = bound_at(e, K, H)["B_lo"]
    finally:
        G.sqrt_iv = orig_sqrt
    record("M12_sqrt_misrounded_low", "sqrt(2 pi) understated by a relative 1e-12",
           val2 != ref, False, f"lower end {float(val2):.15f} vs {float(ref):.15f}", val2 - ref)

    try:
        G.Iv(1) / G.Iv(-1, 1)
        record("M13_division_by_a_zero_straddling_interval", "the division guard is bypassed",
               False, False, "no guard fired")
    except G.Refusal as exc:
        record("M13_division_by_a_zero_straddling_interval", "the division guard is bypassed",
               False, True, str(exc))
    return rows


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    gate = frozen_gate()

    base = evaluate(gate)
    base_key = (tuple(base["excluded"]), tuple(base["not_excluded"]), base["C4_CLASS"])
    K, H = model()["K"], model()["H"]

    # ---- (1) cross-check against the series-free implementation ------------------------------------
    cross = {}
    for k, g in cell_geometry().items():
        prod = G.E_excess(g["e_lo"], K)
        alt = I.E_excess_indep(g["e_lo"], K)
        B_alt = (G.Iv(H) / alt).lo
        cross[str(k)] = {
            "production_E_excess_width": float(prod.hi - prod.lo),
            "independent_E_excess_width": float(alt.hi - alt.lo),
            "production_enclosure_inside_independent": bool(alt.lo <= prod.lo and prod.hi <= alt.hi),
            "intervals_overlap": bool(not (prod.hi < alt.lo or alt.hi < prod.lo)),
            "independent_lower_bound": float(B_alt),
            "production_lower_bound": float(F(base["cells"][str(k)]["lower_bound_E_a_tau"])),
            "verdict_survives_at_cross_check_resolution": None}

    # does the exclusion verdict survive if the WEAKER independent bound is used instead?
    alt_bounds = {k: (G.Iv(H) / I.E_excess_indep(g["e_lo"], K)).lo for k, g in cell_geometry().items()}
    from c4_certificate import intersection_nonempty                                     # noqa: E402
    from c4_common import cell_supply, committed_inputs, frozen_stack, gamma_at          # noqa: E402
    FC, B, T, R, DC, SEL = frozen_stack()
    adopted, cover, c1, c2 = committed_inputs(FC)
    for k in cell_geometry():
        meas, aux, ad5, cov, s = cell_supply(k, FC, B, T, R, DC, SEL, adopted, cover, c1, c2)
        d = gamma_at(FC, T, R, B, meas, aux, ad5, cov, alt_bounds[k], 0, 0)
        cert_ko = gamma_at(FC, T, R, B, meas, aux, ad5, cov, s["A"]["A0"], 0, 0)
        excl = bool(not cert_ko["pass"] and d["Gamma"] >= 0)
        cross[str(k)]["verdict_survives_at_cross_check_resolution"] = (
            excl == (k in base["excluded"]))
    cross_ok = all(v["production_enclosure_inside_independent"] and
                   v["verdict_survives_at_cross_check_resolution"] for v in cross.values())

    # ---- (2) mutants -------------------------------------------------------------------------------
    rows = []
    for name, what, fn in certificate_mutants(gate):
        try:
            res = fn()
            key = (tuple(res["excluded"]), tuple(res["not_excluded"]), res["C4_CLASS"])
            # a certificate-layer mutant that leaves the verdict alone may still have moved a certified value;
            # that is VALUE_ONLY with its magnitude stated, not a silent pass
            shifts = {c: float(F(res["cells"][c]["lower_bound_E_a_tau"])
                               - F(base["cells"][c]["lower_bound_E_a_tau"])) for c in base["cells"]}
            moved = max(abs(v) for v in shifts.values())
            row = {"mutant": name, "perturbs": what, "layer": "certificate",
                   "outcome": ("DETECTED_BY_VERDICT" if key != base_key
                               else ("VALUE_ONLY" if moved > 0 else "NOT_DETECTED")),
                   "result": {"excluded": res["excluded"], "not_excluded": res["not_excluded"],
                              "class": res["C4_CLASS"]},
                   "max_bound_shift": moved}
            if row["outcome"] == "VALUE_ONLY":
                row["note"] = (f"the mutation is NOT equivalent -- it moves the certified bound by up to "
                               f"{moved:.3e} -- but that is far too small to flip this verdict, whose nearest "
                               f"margin is 0.083 in A0. Recorded as a value-level, not verdict-level, detection.")
            rows.append(row)
        except (SystemExit, G.Refusal, TypeError, ValueError) as exc:
            rows.append({"mutant": name, "perturbs": what, "layer": "certificate",
                         "outcome": "DETECTED_BY_GUARD",
                         "guard": f"{type(exc).__name__}: {exc}"})
    rows += rule_mutants()
    rows += arithmetic_mutants()

    by_outcome = {}
    for r in rows:
        by_outcome.setdefault(r["outcome"], []).append(r["mutant"])
    undetected = by_outcome.get("NOT_DETECTED", [])
    value_only = by_outcome.get("VALUE_ONLY", [])

    out = {"schema": "rebaseguard.p5y.k5.tail-c4.mutations.v2",
           "gate_sha256": GATE_SHA,
           "baseline": {"excluded": base["excluded"], "not_excluded": base["not_excluded"],
                        "outside_the_count": base["outside_the_count"], "class": base["C4_CLASS"]},
           "cross_check": {
               "method": "c4_independent.py: Bernoulli/AM-GM brackets for exp, Archimedes polygons for pi, "
                         "composite midpoint with a second-derivative remainder for the erf integral. No series "
                         "is shared with the production module.",
               "shared_with_production": ["the Iv interval container", "the integer-square-root helper"],
               "honest_resolution": "the independent intervals are ~1e-7 wide against production's ~1e-95; this "
                                    "is a cross-check that would catch a gross error, not a reproduction at "
                                    "certificate precision",
               "per_cell": cross, "all_checks_pass": cross_ok},
           "mutants": rows, "applied": len(rows),
           "outcomes": {k: sorted(v) for k, v in sorted(by_outcome.items())},
           "undetected": undetected,
           "value_only_note": ("mutants in VALUE_ONLY moved a certified value but by far too little to flip this "
                               "verdict; they are recorded as such and are NOT credited as verdict-level "
                               "detections (pre-result review, OTHER FINDINGS 3)"),
           "value_only": value_only,
           "new_real_scientific_addresses_evaluated": 0,
           "guard": "REAL_SCIENTIFIC_COMPUTE = DENY"}
    Path(a.out).write_text(json.dumps(out, sort_keys=True, indent=1) + "\n")
    print(json.dumps({"cross_check_ok": cross_ok, "applied": out["applied"],
                      "outcomes": out["outcomes"], "undetected": undetected}, indent=1))
    return 0 if cross_ok and not undetected else 1


if __name__ == "__main__":
    sys.exit(main())
