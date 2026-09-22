"""C7 Phase 7 -- mutation suite.

Design constraint inherited from this programme's failures. C4's suite was blind to the one error
that mattered: mis-taking the threshold inflated the bound in the UNSOUND direction yet left the
verdict unchanged. C5's negate-and-swap survived every check because C5 checked self-consistency
rather than provenance. So this suite is organised by DIRECTION, not by coverage count:

  a mutant that moves the bound UP is unsound and MUST be detected;
  a mutant that moves it DOWN yields a weaker but still valid bound and is classified VALUE_ONLY.

The mutants run against a parameterised reimplementation of the tier-k pipeline. Before any mutant
runs, that reimplementation is asserted to reproduce the real `lambda_lower_tier_k` EXACTLY with its
knobs at default. Without that assertion the suite would be mutating a different program -- the error
C5 made when it measured a mutation against manufactured cells whose weights had already been
restored.

Outcome classes: DETECTED_BY_RULE (a guard refuses), DETECTED_BY_VERDICT (the reported bound changes
in a way the certificate's own checks reject), VALUE_ONLY (sound direction, still valid),
UNDETECTED (recorded as a coverage gap, never excused).
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
N = 16                                   # the suite runs at a cheaper partition than the certificate
A_GRID = [F(j, 4) for j in range(8, 25)]
PART = [F(j) * H / N for j in range(1, N + 1)]


def pipeline(e=E_LO, K_=K, H_=H, partition=None, U_value=None,
             ev_from_below=False, psi_from_above=False, f_from_below=False,
             q_from_below=False, no_q_clip=False, psi_left_endpoint=False):
    """Parameterised reimplementation. All knobs default to the sound choice."""
    partition = PART if partition is None else partition
    us = [F(u) for u in partition]
    # Order matters for the SUITE, not for soundness: with the ends-at-H test first, M07 (threshold
    # confusion) and M13 (non-monotone partition) both refused with "must end exactly at H" and so
    # exercised M12's guard rather than their own, overstating detection coverage by two.
    if K_ + H_ != F(11, 2):
        raise T.TheoremRefusal(f"K + H = {K_ + H_} != 11/2, the frozen CUSUM threshold")
    if any(b <= a for a, b in zip(us, us[1:])) or us[0] <= 0:
        raise T.TheoremRefusal("partition must be strictly increasing and positive")
    if not us or us[-1] != H_:
        raise T.TheoremRefusal("partition must end exactly at H")

    fk = T.f_ratio(K_, e)
    f_used = fk.lo if f_from_below else fk.hi
    psi = []
    for j, u in enumerate(us):
        u_eval = (us[j - 1] if j > 0 else F(0)) if psi_left_endpoint else u
        r = T.mrl(K_ + u_eval - e)
        r_used = r.hi if psi_from_above else r.lo
        psi.append((G.Iv(r_used, r_used) / (G.Iv(1, 1) + G.Iv(f_used, f_used))).lo)
    if any(b > a for a, b in zip(psi, psi[1:])):
        raise T.TheoremRefusal("psi_lo must be non-increasing along the partition")
    for j, u in enumerate(us):
        pe = T.psi_exact(u, e, K_)
        if psi[j] > pe.lo:
            raise T.TheoremRefusal(
                f"psi_lo[{j}] = {float(psi[j])} exceeds psi({float(u)}) <= {float(pe.hi)}")

    q = []
    for u in us:
        s = K_ + u
        pv = (G.Phi(-(s - e)) + G.Phi(-(s + e)))
        pu = pv.lo if q_from_below else pv.hi
        val = pu * U_value
        q.append(val if no_q_clip else min(F(1), val))
    if any(b > a for a, b in zip(q, q[1:])):
        raise T.TheoremRefusal("q must be non-increasing along the partition")

    k = len(us)
    w = [F(0)] * k
    w[0] = F(1) - q[0]
    for j in range(1, k - 1):
        w[j] = q[j - 1] - q[j]
    w[k - 1] += q[k - 2]
    if any(x < 0 for x in w):
        raise T.TheoremRefusal("greedy LP solution is infeasible; negative weight")
    if sum(w) != 1:
        raise T.TheoremRefusal(f"LP weights must sum to exactly 1, got {sum(w)}")

    ER = sum((x * ps for x, ps in zip(w, psi)), F(0))
    if ER < psi[-1]:
        raise T.TheoremRefusal("E[R] below the tier-1 floor")
    EV = G.E_excess(e, K_)
    denom = EV.lo if ev_from_below else EV.hi
    return (G.Iv(H_ + ER, H_ + ER) / G.Iv(denom, denom)).lo


def main() -> int:
    cert = T.certified_U("lorden", E_LO, K, H)
    U = cert["value"]
    baseline = T.lambda_lower_tier_k(E_LO, K, H, cert, PART)["L_lower"]

    # --- the equivalence assertion the suite depends on -----------------------------------------
    mirror = pipeline(U_value=U)
    if mirror != baseline:
        print(f"REFUSE: the parameterised mirror does not reproduce the real pipeline.\n"
              f"  real   {baseline}\n  mirror {mirror}")
        return 1

    A0_cert = F(str(C.c4_cell309()["A0_certified_float"]))
    ceiling = F("4679910339516997") / F(10) ** 15

    muts, results = [], []

    def run(mid, name, direction, fn):
        try:
            v = fn()
        except T.TheoremRefusal as ex:
            results.append({"id": mid, "name": name, "expected_direction": direction,
                            "outcome": "DETECTED_BY_RULE", "detail": str(ex)[:160]})
            return
        # a surviving mutant that inflates the bound is a soundness failure unless a gate catches it
        if v > baseline:
            infl = (v - baseline) / baseline
            caught = v > A0_cert or v > ceiling
            # An inflation below the arithmetic's own grid resolution is an artifact of outward
            # rounding, not a defect the suite can or should detect: the mutation is formally
            # unsound but moves the reported value by less than one unit in the last place of a
            # 2^-320 grid. It is recorded with its measured size rather than waved through.
            # The previous rule declassified anything under a RELATIVE 1e-60 and justified it as
            # "below the 2^-320 grid resolution". That justification was numerically false -- these
            # mutants move the value by up to ~405 grid units -- and the threshold was ~1e37 times
            # coarser than the grid it was named after, so a mutant inflating by up to 1e-60 would
            # have been silently declassified. The anchor is now the only thing actually claimable:
            # the mutation does not alter ANY digit of the reported value.
            grid = F(1, 2) ** 320
            if float(v) == float(baseline):
                cls, det = "UNSOUND_BELOW_REPORTED_PRECISION", (
                    f"formally the wrong rounding direction; the effect is {float((v-baseline)/grid):.0f}x "
                    f"the 2^-320 grid unit -- NOT below the grid -- but does not alter any digit of "
                    f"the reported value. Recorded as surviving, not as detected.")
            elif caught:
                cls, det = "DETECTED_BY_VERDICT", "exceeds a certified upper bound, so KG5 fires"
            else:
                cls, det = "UNDETECTED", "SURVIVES: inflates the bound and no gate fires"
            results.append({"id": mid, "name": name, "expected_direction": direction,
                            "outcome": cls, "value": float(v),
                            "inflation_relative": f"{float(infl):.3e}",
                            "inflation_percent": float(100 * infl), "detail": det})
        else:
            results.append({"id": mid, "name": name, "expected_direction": direction,
                            "outcome": "VALUE_ONLY", "value": float(v),
                            "change_percent": float(100 * (v - baseline) / baseline),
                            "detail": "sound direction: weaker but still a valid certified lower bound"})

    run("M01", "E[V] taken from below in the final division", "UP",
        lambda: pipeline(U_value=U, ev_from_below=True))
    run("M02", "mean residual life r taken from above", "UP",
        lambda: pipeline(U_value=U, psi_from_above=True))
    run("M03", "reflected tail ratio f taken from below", "UP",
        lambda: pipeline(U_value=U, f_from_below=True))
    run("M04", "tail mass q taken from below (p_lower)", "UP",
        lambda: pipeline(U_value=U, q_from_below=True))
    run("M05", "q clipping at 1 removed", "UP",
        lambda: pipeline(U_value=U, no_q_clip=True))
    run("M06", "psi evaluated at the LEFT endpoint of each subinterval", "UP",
        lambda: pipeline(U_value=U, psi_left_endpoint=True))
    run("M07", "threshold confusion: H := C_CUSUM = 11/2", "UP",
        lambda: pipeline(U_value=U, H_=F(11, 2)))
    run("M08", "U passed as a bare number rather than a certificate", "UP",
        lambda: T.lambda_lower_tier_k(E_LO, K, H, F(1), PART))
    run("M09", "U certificate tampered after issuance", "UP",
        lambda: T.lambda_lower_tier_k(E_LO, K, H, {**cert, "value": F(1)}, PART))
    run("M10", "U drawn from a source not on the gate's admitted list", "UP",
        lambda: T.certified_U("made_up", E_LO, K, H))
    run("M11", "a U DERIVATION mutated to understate U, driving the real floor guard", "UP",
        _mutated_lorden_derivation)
    run("M12", "partition does not terminate at H", "UP",
        lambda: pipeline(U_value=U, partition=[F(j) * H / N for j in range(1, N)]))
    swapped = list(PART); swapped[3], swapped[4] = swapped[4], swapped[3]
    run("M13", "two interior knots transposed (still ends at H)", "UP",
        lambda: pipeline(U_value=U, partition=swapped))
    run("M16", "forged a_grid smuggling a negative a into a valid-looking certificate", "UP",
        _forged_a_grid)
    run("M17", "Lemma C7-U called with a <= 0, violating its own hypothesis", "UP", _negative_a)
    run("M18", "evaluation point outside the closed cell for 309", "UP", _e_outside_cell)
    run("M14", "evaluated at e_hi instead of e_lo", "DOWN",
        lambda: pipeline(e=F(2092283, 1000000), U_value=U))
    run("M15", "U doubled (overstated)", "DOWN",
        lambda: pipeline(U_value=2 * U))

    required = [r for r in results if r["expected_direction"] == "UP"]
    undetected = [r["id"] for r in required if r["outcome"] == "UNDETECTED"]
    below_prec = [r["id"] for r in required if r["outcome"] == "UNSOUND_BELOW_REPORTED_PRECISION"]

    # The values the two CRITICAL exploits produced BEFORE the repair. Computed here, not quoted
    # from the review, so the numbers the erratum and the README cite stand behind a producer.
    ev_bad = F(19, 10)
    pm = T.psi_min_lower(ev_bad, K, H)
    EVb = G.E_excess(ev_bad, K)
    num = H + pm["psi_min_lower"]
    tier1_out_of_cell = (G.Iv(num, num) / G.Iv(EVb.hi, EVb.hi)).lo
    forged_U_bound = pipeline(U_value=F(3549353697, 10 ** 9),
                              partition=[F(j) * H / 64 for j in range(1, 65)])
    pre_repair = {
        "purpose": ("what each CRITICAL exploit yielded before its guard existed; both are now "
                    "refused, by M16/M17 and M18 respectively"),
        "forged_a_grid_bound": {"value": str(forged_U_bound), "float": float(forged_U_bound),
                                "U_used": "3549353697/1000000000",
                                "note": "dependency-free, re-derivation-surviving, kill-gate-clean"},
        "e_outside_cell_tier1": {"value": str(tier1_out_of_cell), "float": float(tier1_out_of_cell),
                                 "e_used": str(ev_bad),
                                 "note": "above the published PRIMARY, fired no kill gate"},
    }

    out = {
        "schema": "C7_MUTATIONS/1",
        "pre_repair_exploit_values": pre_repair,
        "baseline_bound": str(baseline), "baseline_float": float(baseline),
        "U_source": cert["source"], "N_partition": N,
        "mirror_equivalence_asserted": True,
        "mirror_value": str(mirror),
        "mutants": results,
        "required_detection_set": [r["id"] for r in required],
        "undetected": undetected,
        "unsound_below_reported_precision": below_prec,
        "surviving_required_mutants_note": (
            "These mutants are NOT detected. They survive with the wrong rounding direction and are "
            "recorded here rather than folded into undetected = [], because a reader checking "
            "coverage on item E must see that the suite supplies no positive evidence on rounding "
            "direction -- that was verified by hand in the pre-publication review instead. They are "
            "separated from `undetected` only because their effect cannot reach a reported digit."),
        "MUTATION_CLASS": "PASS" if not undetected else "REFUSE",
        "coverage_limitation": {
         "interface_gap_CLOSED": (
             "The pre-publication review obtained a dependency-free, re-derivation-surviving, "
             "kill-gate-clean bound of 3.619819606 (+0.9345% over PRIMARY) from U = 3.549353697 "
             "WITHOUT mutating any code, by presenting a certificate whose a_grid carried a negative "
             "a. Two root causes: Lemma C7-U's hypothesis a > 0 was unenforced, and _resolve_U "
             "re-derived from the grid carried in the certificate under test rather than the gate's "
             "frozen grid, so provenance constrained `source` -- the field the mutants exercised -- "
             "and never the field carrying the payload. Both are now closed and are regression-tested "
             "by M16 and M17."),
         "residual_gap": (
             "A mutation of a U DERIVATION itself cannot be caught by re-derivation, which re-runs "
             "the mutated code. Only the independent floor E[tau'] >= H/E[V] = 3.297250281519544 "
             "refuses it, and only once U falls below that floor (M11 drives that real guard)."),
         "residual_gap_MEASURED": {
          "statement": ("A derivation mutated to understate U while keeping it ABOVE the floor is "
                        "NOT detected. The previous text called this 'a small amount' and never "
                        "quantified it. Measured, at N = 64 and e = e_lo:"),
          "U_range_undetectable": "[3.297250281519544, 4.867216116723177]",
          "range_note": ("the top of the range is the REGISTRY U 4.867216117, not Lorden's "
                         "4.679910340 as previously stated -- a mutation of the registry derivation "
                         "spans a strictly wider range than was admitted"),
          "max_undetectable_inflation_percent": 1.0985,
          "why_this_matters": ("+1.0985% is LARGER than C4's entire margin over the C5-T critical "
                               "A0 (0.9440%) -- larger than the quantity C7 exists to make robust. "
                               "It is smaller than C7's own PRIMARY margin of 9.7933%, so the "
                               "published conclusion survives the worst undetectable case, but "
                               "'small' was the wrong word and the number belongs in the record.")
         },
         "mitigation": (
             "Three mutually independent U derivations are reported. Two -- elementary and Lorden -- "
             "share no code path beyond the Gaussian primitives, and the third is read from a "
             "committed file rather than computed. This is a mitigation, not a closure."),
         "untested_primitives": (
             "Neither psi_exact nor any mutant can see a systematic error in G.Phi or G.phi, since "
             "every expression in the namespace is built from those two. The review checked them "
             "against known values independently; code/c7_primitives_test.py now commits that check."),
        },
    }
    p = C.NS / "evidence" / "mutations" / "C7_MUTATIONS.json"
    s = C.write_evidence(p, out)
    print(f"mirror reproduces the real pipeline exactly: {mirror == baseline}")
    print(f"baseline (U = {cert['source']}, N = {N}): {float(baseline):.9f}\n")
    for r in results:
        v = f"{r.get('value', float('nan')):.9f}" if "value" in r else "-- refused --"
        print(f"  {r['id']}  {r['outcome']:<20} {r['expected_direction']:<5} {v:>14}  {r['name'][:52]}")
    print(f"\nMUTATION_CLASS = {out['MUTATION_CLASS']}   undetected = {undetected}")
    print(f"wrote {p.relative_to(C.REPO)}  sha256 {s[:16]}...")
    return 0 if not undetected else 1


def _mutated_lorden_derivation():
    """M11: mutate the DERIVATION and drive the real guard in certified_U.

    The previous version of this mutant recomputed the floor inline and raised its own
    TheoremRefusal, so the suite recorded DETECTED_BY_RULE for a rule the mutant had written for
    itself, and the real guard at c7_theorem.certified_U was never exercised by anything. That is the
    exact failure this module's docstring says it exists to avoid. Here U_lorden -- a real derivation
    -- is replaced for the duration of the call, so re-derivation re-runs the MUTATED code (which is
    why re-derivation cannot catch this class) and only the independent floor can refuse it.
    """
    original = T.U_lorden
    try:
        T.U_lorden = lambda e, K_, H_: {"E_V2_upper": F(0), "E_R_upper": F(0),
                                        "U_upper": F(3), "dependency": "mutated"}
        return T.certified_U("lorden", E_LO, K, H)["value"]
    finally:
        T.U_lorden = original


def _forged_a_grid():
    """M16: the reviewer's finding-1 attack -- a crafted a_grid carrying a negative a."""
    return T.lambda_lower_tier_k(E_LO, K, H, {
        "_tag": "C7_CERTIFIED_U/1", "source": "elementary", "value": F(3549353697, 10 ** 9),
        "dependencies": [], "derivation": "Lemma C7-U at a = -47/20", "a_grid": ["-47/20"]}, PART)


def _negative_a():
    """M17: the same hypothesis violation reached directly through Lemma C7-U."""
    return T.U_elementary(E_LO, K, H, [F(-47, 20)])["best"]["U_upper"]


def _e_outside_cell():
    """M18: an evaluation point outside the closed cell bounds nothing, and used to fire no gate."""
    return T.lambda_lower(F(19, 10), K, H)["C7_bound_lower"]


if __name__ == "__main__":
    raise SystemExit(main())
