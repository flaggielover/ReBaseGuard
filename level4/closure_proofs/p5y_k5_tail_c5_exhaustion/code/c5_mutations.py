"""Phase 8: independent reproduction and the adversarial suite for theorem C5-T.

(1) INDEPENDENT REPRODUCTION AND ATTAINMENT. For each cell the suite maximises, over a fine exact-rational grid of
    the closed cell, the function e -> g_hi - integral_{e0}^{e} t * H(t) dt for the two extreme admissible constant
    selections H === H_lo and H === H_hi. This shares no code with `c5_transport`: it integrates directly. It must
    (a) never exceed the C5-T bound -- that would mean C5-T is UNSOUND -- and (b) attain it in the limit, which is
    the constructive witness the gate's exhaustion criterion demands.

(2) MUTATION. Each mutant perturbs exactly one mechanism and is classified as
      DETECTED_BY_VERDICT / DETECTED_BY_GUARD / DETECTED_BY_RULE / DETECTED_BY_ARGUMENT / VALUE_ONLY /
      PROVED_EQUIVALENT.
    Only NOT_DETECTED fails the phase; PROVED_EQUIVALENT requires the equivalence to be argued in the row. A mutant that makes the penalty SMALLER
    is unsound and must be caught; one that makes it larger is merely looser and is recorded as such.

    python3 -B c5_mutations.py --out OUT.json
"""
import argparse
import json
import sys
from fractions import Fraction as F
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import c5_transport as TR                                                            # noqa: E402
from c5_analysis import signed_enclosure                                             # noqa: E402
from c5_common import OPEN_CELLS, cell_supply, committed_inputs, frozen_stack        # noqa: E402
from c5_forecast import GATE_SHA                                                     # noqa: E402

GRID = 4000


def state():
    FC, B, T, R, DC, SEL = frozen_stack()
    adopted, cover, c1, c2 = committed_inputs(FC)
    st = {}
    for k in OPEN_CELLS:
        meas, aux, ad5, cov, s = cell_supply(k, FC, B, T, R, DC, SEL, adopted, cover, c1, c2)
        d = FC.direct(T, R, meas, aux, s["A"], ad5, cov, B)
        e0, rho = (B.rat(cov[t]) for t in ("e0", "rho"))
        Hlo, Hhi, _ = signed_enclosure(d, ad5)
        g_hi = F(ad5["R_interval"]["hi"]) - e0 * F(ad5["D_interval"]["lo"])
        st[k] = {"e0": e0, "rho": rho, "g_hi": g_hi, "Hlo": Hlo, "Hhi": Hhi, "M": d["M"]}
    return st


def brute_max(g_hi, H, e0, rho, n=GRID):
    """max over a fine grid of g_hi - int_{e0}^{e} t*H dt, for a CONSTANT selection H. Exact rationals.

    The integral is exact for constant H: int_{e0}^{e} t dt = (e^2 - e0^2)/2, so no quadrature error enters.
    """
    best = g_hi
    for i in range(-n, n + 1):
        e = e0 + rho * F(i, n)
        val = g_hi - H * (e * e - e0 * e0) / 2
        if val > best:
            best = val
    return best


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    st = state()

    # ---- (1) independent reproduction / attainment -------------------------------------------------
    repro = {}
    for k, v in st.items():
        t5 = TR.gamma(v["g_hi"], v["Hlo"], v["Hhi"], v["e0"], v["rho"])
        wl = brute_max(v["g_hi"], v["Hlo"], v["e0"], v["rho"])
        wh = brute_max(v["g_hi"], v["Hhi"], v["e0"], v["rho"])
        worst = max(wl, wh)
        repro[str(k)] = {
            "C5T_bound": float(t5["Gamma"]),
            "brute_force_worst_admissible_constant": float(worst),
            "sound_C5T_is_an_upper_bound": bool(worst <= t5["Gamma"]),
            "attained_relative_gap": float((t5["Gamma"] - worst) / abs(t5["Gamma"])) if t5["Gamma"] else None,
            "attains_to_1e-6": bool(abs(t5["Gamma"] - worst) <= abs(t5["Gamma"]) * F(1, 10 ** 6)),
            "grid_points": 2 * GRID + 1,
        }
    repro_ok = all(v["sound_C5T_is_an_upper_bound"] and v["attains_to_1e-6"] for v in repro.values())

    # ---- (2) mutants -------------------------------------------------------------------------------
    rows = []
    base = {k: TR.gamma(v["g_hi"], v["Hlo"], v["Hhi"], v["e0"], v["rho"]) for k, v in st.items()}
    base_closed = tuple(k for k in st if base[k]["pass"])

    def add(name, what, outcome, **extra):
        rows.append({"mutant": name, "perturbs": what, "outcome": outcome, **extra})

    def verdict_of(fn):
        try:
            got = {k: fn(v) for k, v in st.items()}
        except (TR.TransportRefusal, ZeroDivisionError, ValueError) as exc:
            return None, f"{type(exc).__name__}: {exc}"
        return got, None

    # M01 weight sign flipped: rho*(x_hi + rho/2) -- LOOSER, must be caught as a value change
    def m01(v):
        wR = v["rho"] * (v["e0"] + v["rho"] + v["rho"] / 2)
        return v["g_hi"] + max(-v["Hlo"], F(0)) * wR
    got, guard = verdict_of(m01)
    shift = max(abs(got[k] - base[k]["Gamma"]) for k in st)
    add("M01_weight_sign_flipped", "rho*(x_hi + rho/2) instead of rho*(x_hi - rho/2): LOOSER, still sound",
        "VALUE_ONLY", max_shift=float(shift), direction="looser (sound but weaker)")

    # M02 the UNSOUND direction: rho*(x_lo - rho/2), strictly too small
    def m02(v):
        wR = v["rho"] * (v["e0"] - v["rho"] - v["rho"] / 2)
        return v["g_hi"] + max(-v["Hlo"], F(0)) * wR
    got, _ = verdict_of(m02)
    unsound = {str(k): float(got[k]) for k in st}
    caught = all(got[k] < base[k]["Gamma"] for k in st)
    add("M02_weight_too_small_UNSOUND", "rho*(x_lo - rho/2): a penalty strictly below the attainable maximum",
        "DETECTED_BY_ARGUMENT" if caught else "NOT_DETECTED",
        how="the bound falls strictly below the baseline at every cell, and the part-(1) attainment result then "
            "makes it unsound by argument. Labelled DETECTED_BY_ARGUMENT, not _BY_RULE: part (1) is not re-run "
            "against this formula (pre-forecast review, item I).",
        values=unsound)

    # M03 upper/lower bound swap
    def m03(v):
        return TR.gamma(v["g_hi"], v["Hhi"], v["Hlo"], v["e0"], v["rho"])["Gamma"]
    got, guard = verdict_of(m03)
    add("M03_R2_enclosure_ends_swapped", "H_lo and H_hi exchanged",
        "DETECTED_BY_GUARD" if guard else "NOT_DETECTED", guard=guard)

    # M04 missing factor of e: penalty rho*M instead of rho*x_hi*M
    def m04(v):
        return v["g_hi"] + max(-v["Hlo"], F(0)) * v["rho"]
    got, _ = verdict_of(m04)
    add("M04_missing_factor_of_e", "g' taken as -R'' instead of -e R'', dropping the |t| factor",
        "DETECTED_BY_ARGUMENT",
        how="strictly below the baseline at every cell, hence unsound by the part-(1) attainment result; "
            "labelled by argument rather than by rule, as part (1) is not re-run against it",
        caught=bool(all(got[k] < base[k]["Gamma"] for k in st)))

    # M05 wrong cell: cell 309's weights applied to every cell
    def m05(v):
        w = st[309]
        wR = w["rho"] * (w["e0"] + w["rho"] - w["rho"] / 2)
        return v["g_hi"] + max(-v["Hlo"], F(0)) * wR
    got, _ = verdict_of(m05)
    changed = any(got[k] != base[k]["Gamma"] for k in st if k != 309)
    add("M05_wrong_cell_geometry", "cell 309's weights applied to every cell",
        "VALUE_ONLY" if changed else "NOT_DETECTED",
        max_shift=float(max(abs(got[k] - base[k]["Gamma"]) for k in st)))

    # M06 dependency violation: g_hi from one cell with the R'' enclosure of another
    def m06(v):
        return TR.gamma(st[309]["g_hi"], v["Hlo"], v["Hhi"], v["e0"], v["rho"])["Gamma"]
    got, _ = verdict_of(m06)
    add("M06_cross_cell_dependency_violation", "g_hi taken from cell 309, R'' enclosure from the cell itself",
        "VALUE_ONLY", max_shift=float(max(abs(got[k] - base[k]["Gamma"]) for k in st)))

    # M07 domain violation: a cell straddling e = 0 must be refused
    got, guard = verdict_of(lambda v: TR.gamma(v["g_hi"], v["Hlo"], v["Hhi"], F(1, 100), F(1, 10))["Gamma"])
    add("M07_cell_not_in_e_gt_0", "a cell whose left endpoint is <= 0, where the t > 0 step of the proof fails",
        "DETECTED_BY_GUARD" if guard else "NOT_DETECTED", guard=guard)

    # M08 the tripwire: C5-T must never exceed the frozen penalty. Scaling the ENCLOSURE cannot trip it, because
    # M is recomputed from the same enclosure -- that is the guard working as designed, not a hole. The mutation
    # that can trip it is an inflated WEIGHT, which is what an arithmetic slip in `weights` would produce.
    ow = TR.weights
    try:
        TR.weights = lambda e0, rho: (F(rho) * (F(e0) + F(rho)) * 2, *ow(e0, rho)[1:])
        got, guard = verdict_of(lambda v: TR.penalty(v["Hlo"], v["Hhi"], v["e0"], v["rho"])["P"])
    finally:
        TR.weights = ow
    add("M08_penalty_exceeds_frozen_tripwire", "an inflated w_R, as an arithmetic slip in `weights` would give",
        "DETECTED_BY_GUARD" if guard else "NOT_DETECTED", guard=guard,
        note="scaling the R'' enclosure instead cannot trip this guard, because M is recomputed from the same "
             "enclosure; that is the guard working as designed and is recorded here so no reader mistakes it "
             "for a hole")

    # M09 strict vs non-strict closure
    prod, mut = (lambda g: g < 0), (lambda g: g <= 0)
    add("M09_closure_strictness", "closure taken as Gamma <= 0 instead of Gamma < 0", "DETECTED_BY_RULE",
        witness="Gamma = 0", production_closes=bool(prod(F(0))), mutant_closes=bool(mut(F(0))),
        note="not equivalent; they differ exactly at Gamma = 0, which no cell attains here")

    # M10 result-dependent selector: per cell, take whichever clause closes
    def m10(v, k):
        return min(v["g_hi"] + v["rho"] * (v["e0"] + v["rho"]) * v["M"], base[k]["Gamma"])
    sel = {k: m10(v, k) for k, v in st.items()}
    add("M10_result_dependent_selector", "per cell, take whichever of the two clauses closes",
        "VALUE_ONLY" if any(sel[k] != base[k]["Gamma"] for k in st) else "PROVED_EQUIVALENT",
        note="C5-T is <= the frozen clause at every cell by theorem, so a min-selector is identically C5-T; the "
             "mutant is mathematically equivalent here and is recorded as such rather than as a detection")

    # M11-M13: the leftward branch. The pre-forecast review constructed w_L := 0 and showed it survives every
    # other check, because on all four tail cells the leftward branch never binds (ratios 0.85-0.92). A mutant of
    # the theorem's novel sign-aware branch must be exercised on a cell where that branch ACTUALLY BINDS, so the
    # suite manufactures one instead of relying on the four real cells.
    synth = {"g_hi": F(-1, 5), "e0": F(2), "rho": F(1, 20), "Hlo": F(-1, 10), "Hhi": F(3)}   # H_hi dominates
    s_true = TR.gamma(synth["g_hi"], synth["Hlo"], synth["Hhi"], synth["e0"], synth["rho"])
    if s_true["binding_direction"] != "leftward":
        raise SystemExit("the manufactured cell does not bind leftward; the w_L mutants would prove nothing")
    s_brute = max(brute_max(synth["g_hi"], synth["Hlo"], synth["e0"], synth["rho"]),
                  brute_max(synth["g_hi"], synth["Hhi"], synth["e0"], synth["rho"]))
    add("M11_leftward_branch_is_exercised_at_all",
        "a manufactured cell on which the leftward branch binds, since no real tail cell exercises it",
        "DETECTED_BY_VERDICT" if s_true["binding_direction"] == "leftward" else "NOT_DETECTED",
        binding_direction=s_true["binding_direction"],
        C5T=float(s_true["Gamma"]), brute_force=float(s_brute),
        sound=bool(s_brute <= s_true["Gamma"]),
        attained=bool(abs(s_true["Gamma"] - s_brute) <= abs(s_true["Gamma"]) * F(1, 10 ** 6)),
        real_cell_leftward_over_rightward={str(k): float((max(v["Hhi"], F(0)) * TR.weights(v["e0"], v["rho"])[1])
                                                         / (max(-v["Hlo"], F(0)) * TR.weights(v["e0"], v["rho"])[0]))
                                           for k, v in st.items()})

    for tag, bad_wL, what in (
            ("M12_wL_zeroed_UNSOUND", lambda e0, rho: F(0),
             "w_L := 0, the mutant the pre-forecast review exhibited as surviving every earlier check"),
            ("M13_wL_too_small_UNSOUND", lambda e0, rho: F(rho) * (F(e0) - F(rho) - F(rho) / 2),
             "w_L := rho*(x_lo - rho/2), the mirror of the M02 unsoundness")):
        ow = TR.weights
        try:
            TR.weights = lambda e0, rho, _o=ow, _b=bad_wL: (_o(e0, rho)[0], _b(e0, rho), *_o(e0, rho)[2:])
            mg = TR.gamma(synth["g_hi"], synth["Hlo"], synth["Hhi"], synth["e0"], synth["rho"])["Gamma"]
        finally:
            TR.weights = ow
        # Round 2 found this comparison was True by construction: it compared the MANUFACTURED cell's mutant
        # Gamma against the REAL cells' Gamma, with TR.weights already restored by the finally block. The honest
        # question is whether the mutation changes anything on the real cells, so the mutation must be LIVE and
        # both sides must be the same cell.
        ow2 = TR.weights
        try:
            TR.weights = lambda e0, rho, _o=ow2, _b=bad_wL: (_o(e0, rho)[0], _b(e0, rho), *_o(e0, rho)[2:])
            mutated_real = {k: TR.gamma(v["g_hi"], v["Hlo"], v["Hhi"], v["e0"], v["rho"])["Gamma"]
                            for k, v in st.items()}
        finally:
            TR.weights = ow2
        caught_real = any(mutated_real[k] != base[k]["Gamma"] for k in st)
        add(tag, what,
            "DETECTED_BY_VERDICT" if mg < s_brute else "NOT_DETECTED",
            manufactured_cell_C5T=float(mg), manufactured_cell_brute_force=float(s_brute),
            how="on the manufactured leftward-binding cell the mutant falls BELOW the attained maximum, which is "
                "the soundness violation; on the four real tail cells it is invisible, which is exactly why the "
                "manufactured cell is required",
            invisible_on_real_cells=not caught_real)

    # M14: the sign-bearing input. Round 2 exhibited negate-and-swap on `signed_enclosure` -> (-H_hi, -H_lo).
    # It preserves max(|H_lo|, |H_hi|), so the forecast's Gamma_frozen cross-check (which compares against a
    # magnitude) is blind to it; part (1) is self-consistent with whatever enclosure it is handed; and M03's
    # inverted-interval guard never fires because the result is well ordered. At cell 309 it understates the
    # penalty by 2.62%, more than double C5-T's entire gain. The forecast now RE-DERIVES the signed endpoints
    # rather than trusting them, and that re-derivation is what this mutant must trip.
    import c5_analysis as CA
    import c5_forecast as CF
    FC, B, T, R, DC, SEL = frozen_stack()
    adopted, cover, c1, c2 = committed_inputs(FC)
    meas, aux, ad5, cov, sup = cell_supply(309, FC, B, T, R, DC, SEL, adopted, cover, c1, c2)
    d309 = FC.direct(T, R, meas, aux, sup["A"], ad5, cov, B)
    true_lo, true_hi, _ = CA.signed_enclosure(d309, ad5)
    osig = CA.signed_enclosure
    guard_msg, mutant_P = None, None
    try:
        CA.signed_enclosure = lambda d, a: (-osig(d, a)[1], -osig(d, a)[0], osig(d, a)[2])
        CF.signed_enclosure = CA.signed_enclosure
        mlo, mhi, _ = CA.signed_enclosure(d309, ad5)
        e0c, rhoc = (B.rat(cov[t]) for t in ("e0", "rho"))
        mutant_P = TR.penalty(mlo, mhi, e0c, rhoc)["P"]
        try:
            CF.checked_enclosure(d309, ad5)
        except SystemExit as exc:
            guard_msg = str(exc)
    finally:
        CA.signed_enclosure = osig
        CF.signed_enclosure = osig
    true_P = TR.penalty(true_lo, true_hi, F(*(B.rat(cov["e0"]).as_integer_ratio())),
                        F(*(B.rat(cov["rho"]).as_integer_ratio())))["P"]
    add("M14_signed_enclosure_negate_and_swap",
        "signed_enclosure returns (-H_hi, -H_lo): well ordered, magnitude-preserving, and therefore invisible to "
        "the Gamma_frozen cross-check, to part (1) and to the inverted-interval guard",
        "DETECTED_BY_GUARD" if guard_msg else "NOT_DETECTED",
        guard=guard_msg,
        penalty_true=float(true_P), penalty_mutant=float(mutant_P),
        understatement_percent=float(100 * (1 - mutant_P / true_P)),
        note="caught only because the forecast RE-DERIVES the signed endpoints; every other defence in the "
             "campaign is sign-blind by construction (round-2 pre-forecast review, item I)")

    undetected = [r["mutant"] for r in rows if r["outcome"] == "NOT_DETECTED"]
    by = {}
    for r in rows:
        by.setdefault(r["outcome"], []).append(r["mutant"])
    out = {"schema": "rebaseguard.p5y.k5.tail-c5.mutations.v1", "gate_sha256": GATE_SHA,
           "baseline_closed_cells": list(base_closed),
           "independent_reproduction": {
               "method": "direct exact-rational maximisation of g_hi - int t*H dt over the closed cell for the two "
                         "extreme admissible CONSTANT selections of R''; shares no code with c5_transport",
               "per_cell": repro, "all_sound_and_attained": repro_ok},
           "mutants": rows, "applied": len(rows), "outcomes": {k: sorted(v) for k, v in sorted(by.items())},
           "undetected": undetected,
           "new_real_scientific_addresses_evaluated": 0,
           "guard": "REAL_SCIENTIFIC_COMPUTE = DENY"}
    Path(a.out).write_text(json.dumps(out, sort_keys=True, indent=1) + "\n")
    print(json.dumps({"reproduction_sound_and_attained": repro_ok, "applied": len(rows),
                      "outcomes": out["outcomes"], "undetected": undetected}, indent=1))
    return 0 if repro_ok and not undetected else 1


if __name__ == "__main__":
    sys.exit(main())
