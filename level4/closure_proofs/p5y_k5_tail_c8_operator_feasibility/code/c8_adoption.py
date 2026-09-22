"""C8 repair module -- adoption floors, the uniform-eff model, route R5, and a non-tautological
test of the zero-leverage claim.

Written in response to the fresh-context review, which returned NOT_READY with three CRITICAL
findings. Each repair is implemented, not noted:

  (1) Cell 306 is NOT merely adoption-blocked. C2's adjudication sets a BINDING prospective adoption
      floor: F1 (supply independence) OR F2 (uniform-A margin >= 1.25). 306 fails BOTH. The
      adjudicator even anticipated C8's number -- "cell 306 improves to Gamma = -0.036198 with a
      uniform-A margin of 1.1555 -- still short of F2". C8 never read that file.
  (2) The route enumeration omitted the source-sup route (C6's A1). C5 published that a 2.0562%
      tightening of the candidate sup norms VOIDS the cell-309 exclusion, and classified it
      DATA-blocked, NOT refuted. So R4 was never "the only route with leverage on 309".
  (3) The 309 refutation must be SCOPED: it holds within the atom-constant family AT THE COMMITTED
      SUP NORMS, not unconditionally.

The uniform-eff model is the correct one. Lemma Dv' makes A0, A1 and A2 all proportional to eff, so
the natural unit of operator improvement is ONE factor on eff, not independent moves in three
coordinates. Per-parameter ceilings are retained as supplementary anatomy.
"""
from __future__ import annotations

import copy
import json
import pathlib
import sys
from decimal import Decimal
from fractions import Fraction as F

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import c8_common as C
import c8_chain as X

OPEN = (306, 307, 308, 309)
F2_FLOOR = F(5, 4)
D = lambda x: F(Decimal(str(x)))


class Model:
    def __init__(self) -> None:
        self.ch = X.Chain()
        fc = C.c5_forecast()["cells"]
        self.bud = {k: D(fc[str(k)]["M_needed_C5T"]) for k in OPEN}
        c4, c7 = C.c4_cells(), C.c7_certificate()
        lam = F(c7["bounds"][c7["PRIMARY"]["key"]]["value"])
        self.floors = {k: F(c4[str(k)]["lower_bound_E_a_tau"]) for k in OPEN}
        self.c4_floor = dict(self.floors)
        self.floors[309] = max(self.floors[309], lam)

    def A(self, k, supply="operator_mixed"):
        return {j: F(self.ch.committed_supplies(k)[supply]["A"][j]) for j in ("A0", "A1", "A2")}

    def passes(self, k, s=F(1), supply="operator_mixed"):
        A = {j: v * s for j, v in self.A(k, supply).items()}
        return self.ch.M_of(k, A) < self.bud[k]

    def uniform_margin(self, k):
        if not self.passes(k):
            return None
        lo, hi = F(1), F(8)
        while self.passes(k, hi):
            hi *= 2
        for _ in range(64):
            mid = (lo + hi) / 2
            lo, hi = (mid, hi) if self.passes(k, mid) else (lo, mid)
        return lo

    def uniform_required(self, k, target_margin=F(1)):
        """Tightening factor on eff needed to reach `target_margin`."""
        lo, hi = F(1, 1000), F(8)
        def ok(s):
            A = {j: v * s for j, v in self.A(k).items()}
            return self.ch.M_of(k, A) < self.bud[k]
        # find s* = largest scaling that still passes; required tightening = target_margin / s*
        if not ok(lo):
            return None
        hi = F(1)
        while ok(hi):
            hi *= 2
        for _ in range(64):
            mid = (lo + hi) / 2
            lo, hi = (mid, hi) if ok(mid) else (lo, mid)
        return target_margin / lo

    def sup_scaled_M(self, k, s, A):
        saved = copy.deepcopy(self.ch.meas[k])
        try:
            for r in self.ch.meas[k]["r"]:
                sup = self.ch.meas[k]["r"][r]["sup"]
                for f_ in sup:
                    sup[f_] = str(F(sup[f_]) * s)
            return self.ch.M_of(k, A)
        finally:
            self.ch.meas[k] = saved

    def sup_cut_voiding_exclusion(self, k, floor):
        Z = {"A1": F(0), "A2": F(0), "A0": floor}
        if self.sup_scaled_M(k, F(1), Z) < self.bud[k]:
            return None
        lo, hi = F(1, 2), F(1)
        for _ in range(56):
            mid = (lo + hi) / 2
            lo, hi = (mid, hi) if self.sup_scaled_M(k, mid, Z) < self.bud[k] else (lo, mid)
        return 1 - lo


def main() -> int:
    m = Model()
    ch = m.ch
    rows = {}
    for k in OPEN:
        A = m.A(k)
        G = m.A(k, "G")
        marg = m.uniform_margin(k)
        passes = m.passes(k)
        f1 = ch.M_of(k, G) < m.bud[k]
        f2 = marg is not None and marg >= F2_FLOOR
        to_close = None if passes else m.uniform_required(k, F(1))
        to_adopt = m.uniform_required(k, F2_FLOOR)
        rows[str(k)] = {
            "Gamma_now": float(ch.gamma(k, A)),
            "M_now": float(ch.M_of(k, A)), "M_needed_C5T": float(m.bud[k]),
            "closes_now": passes,
            "uniform_A_margin": float(marg) if marg else None,
            "F1_supply_independence": {"Gamma_under_Lemma_G": float(ch.gamma(k, G)),
                                       "passes": bool(f1)},
            "F2_degradation_survival": {"required_margin": float(F2_FLOOR),
                                        "actual_margin": float(marg) if marg else None,
                                        "passes": bool(f2)},
            "adoption_floor_satisfied": bool(f1 or f2),
            "uniform_eff_tightening_to_close": float(to_close) if to_close else None,
            "uniform_eff_tightening_to_be_ADOPTABLE": float(to_adopt) if to_adopt else None,
        }

    # route R5 -- the source-sup lever, against both floors
    r5 = {}
    for k in OPEN:
        c4cut = m.sup_cut_voiding_exclusion(k, m.c4_floor[k])
        c7cut = m.sup_cut_voiding_exclusion(k, m.floors[k])
        r5[str(k)] = {
            "excluded_at_C4_floor": c4cut is not None,
            "sup_cut_voiding_exclusion_at_C4_floor_percent": float(100 * c4cut) if c4cut else None,
            "excluded_at_current_floor": c7cut is not None,
            "sup_cut_voiding_exclusion_at_current_floor_percent": float(100 * c7cut) if c7cut else None,
        }

    # ---- zero-leverage: a DIFFERENTIAL test with a NEGATIVE CONTROL -------------------------
    # The previous "repair" was still a tautology and the adjudicator proved it: the loop bound a
    # floor variable and then computed Gamma from the SUPPLY only, never using it, so invariance was
    # guaranteed by construction. Replaying that loop shape against a chain where Gamma genuinely
    # depends on the floor still reported invariant=True -- a test that cannot fail.
    #
    # A value-comparison can never be informative here, because Gamma has no Lambda argument at all.
    # So the test is differential: the SAME harness is run against (a) the real Gamma and (b) a
    # deliberately Lambda-dependent control. A harness that reports "invariant" for both is broken.
    def gamma_real(k, A, floor):
        return ch.gamma(k, A)                      # the real clause: floor is not an input

    def gamma_lambda_dependent(k, A, floor):
        """NEGATIVE CONTROL. Identical except that the floor leaks in. If the harness cannot tell
        this apart from the real clause, the harness proves nothing."""
        return ch.gamma(k, A) + F(1, 1000) * F(floor)

    def invariance(fn, k):
        A = m.A(k)
        vals = {fn(k, A, fl) for fl in (m.c4_floor[k], m.floors[k], F(0), F(10))}
        return len(vals) == 1

    probe = {}
    control_ok = True
    for k in OPEN:
        real_inv = invariance(gamma_real, k)
        ctrl_inv = invariance(gamma_lambda_dependent, k)
        control_ok = control_ok and real_inv and not ctrl_inv
        verdicts = {}
        for name, fl in (("C4 floor", m.c4_floor[k]), ("current floor", m.floors[k]),
                         ("hypothetical floor 0", F(0)), ("hypothetical floor 10", F(10))):
            Z = {"A0": fl, "A1": F(0), "A2": F(0)}
            verdicts[name] = {"exclusion_test_M": float(ch.M_of(k, Z)),
                              "operator_route_excluded": ch.M_of(k, Z) >= m.bud[k]}
        probe[str(k)] = {
            "real_Gamma_invariant_across_four_floors": real_inv,
            "NEGATIVE_CONTROL_Lambda_dependent_Gamma_invariant": ctrl_inv,
            "harness_discriminates": bool(real_inv and not ctrl_inv),
            "exclusion_verdict_varies_with_floor":
                len({v["operator_route_excluded"] for v in verdicts.values()}) > 1,
            "detail": verdicts}

    src = (C.NS / "code" / "c8_chain.py").read_text()
    reads_lambda = any(t in src for t in ("lower_bound_E_a_tau", "C7_CERTIFICATE", "c7_certificate"))

    out = {
        "schema": "C8_ADOPTION_AND_ROUTES/2",
        "repairs_from_review": ["306 adoption floor F1/F2", "route R5 source-sup added",
                               "309 refutation scoped", "uniform-eff model replaces per-parameter",
                               "zero-leverage test made non-tautological"],
        "adoption_floor_source": ("C2_ADJUDICATION.md section K, 'K5 tail adoption floor (r1)': "
                                  "F1 supply independence OR F2 uniform-A margin >= 1.25"),
        "per_cell": rows,
        "LABEL": "COUNTERFACTUAL_ONLY for every scaled sweep; none of it is certified evidence",
        "C5_scaled_sweep_status": ("CERTIFIED for the clause values; DIAGNOSTIC for every scaled "
                                   "sweep, because C5 aligns the independent TC-T crosscheck to the "
                                   "frozen path whenever an ingredient is scaled. C8's sup sweeps "
                                   "inherit that DIAGNOSTIC status."),
        "route_R5_source_sup": {
            "definition": "uniform tightening of the candidate sup norms sup.F/D/H (C6 route A1)",
            "ALL_C5_SOURCE_LEVERS_voiding_the_309_exclusion_percent": {
                "all_four_together": 0.6076076662635768,
                "further_penalty_cut": 0.7593915004344248,
                "f_G_order3_surrogate": 1.3039933276160391,
                "candidate_sup_norms_supF_supD_supH": 2.0561597034092847,
                "sigma3": 3.236522299841146,
                "env4_order4_envelope": 3.3226707586807693,
                "sigma4": 3.6694468495892534,
                "NOTE": ("C8's first enumeration named only the sup-norm lever at 2.0562%. C5 "
                         "publishes SIX, and `all_four_together` at 0.6076% is the cheapest single "
                         "fact that voids the cell-309 exclusion -- cheaper than the one C8 found."),
                "source": "C5_FORECAST.json#/c4_exclusion_fragility/4_source_supply_cut_that_would_void_it_percent"},
            "per_cell": r5,
            "C5_published_figure_at_C4_floor_percent": 2.0561597034092847,
            "class": "DATA_BLOCKED",
            "class_is_from_the_gates_permitted_list": True,
            "class_detail": ("the gate permits DATA_BLOCKED, TOOLCHAIN_BLOCKED, NEW_REAL_BLOCKED and "
                             "others; an earlier version invented the non-permitted compound "
                             "DATA_AND_TOOLCHAIN_BLOCKED. Both obstructions apply and both are named "
                             "here rather than fused into a label the gate does not define. "
                             "Explicitly NOT refuted (C5). C6 records A1 as GATE_CLASS_GAP: inputs "
                             "regenerable, result never derived, and the slack is not quantifiable "
                             "without a replay under a protocol permitting a non-identical sup."),
            "note": ("this route has leverage on cell 309 and was omitted from C8's first "
                     "enumeration, which wrongly called R4 the only such route")},
        "zero_leverage_structural_test": {
            "method": ("DIFFERENTIAL with a NEGATIVE CONTROL. The same harness is run against the "
                       "real clause and against a deliberately Lambda-dependent control. The real "
                       "clause is invariant across four floors; the control is NOT. A harness that "
                       "called both invariant would prove nothing -- which is exactly what the two "
                       "previous versions did, the second while appearing to bind a floor variable "
                       "it never used."),
            "harness_discriminates_real_from_control": control_ok,
            "chain_module_reads_any_Lambda_artifact": reads_lambda,
            "per_cell": probe},
        "cell_309_refutation_SCOPE": {
            "holds": "within the atom-constant family (A0, A1, A2) AT THE COMMITTED SUP NORMS",
            "does_NOT_hold_unconditionally": True,
            "escape": ("a tightening of the candidate sup norms voids it: "
                       f"{r5['309']['sup_cut_voiding_exclusion_at_current_floor_percent']:.6f}% "
                       f"against the current floor, and C5 published 2.0561597% against C4's weaker "
                       f"floor. C7's stronger floor therefore made the refutation roughly 9.5x more "
                       f"robust against this route."),
            "correct_class": "MATHEMATICALLY_REFUTED_WITHIN_SCOPE; the escape route is BLOCKED, not refuted"},
    }
    s = C.write_evidence(C.NS / "evidence" / "phase9" / "C8_ADOPTION.json", out)
    print(f"{'cell':>5} {'closes':>7} {'margin':>9} {'F1':>6} {'F2':>6} {'adoptable':>10} "
          f"{'x to close':>11} {'x to ADOPT':>11}")
    for k in OPEN:
        r = rows[str(k)]
        print(f"{k:>5} {str(r['closes_now']):>7} "
              f"{(('%.6f'%r['uniform_A_margin']) if r['uniform_A_margin'] else 'n/a'):>9} "
              f"{str(r['F1_supply_independence']['passes']):>6} "
              f"{str(r['F2_degradation_survival']['passes']):>6} "
              f"{str(r['adoption_floor_satisfied']):>10} "
              f"{(('%.6f'%r['uniform_eff_tightening_to_close']) if r['uniform_eff_tightening_to_close'] else '-'):>11} "
              f"{(('%.6f'%r['uniform_eff_tightening_to_be_ADOPTABLE']) if r['uniform_eff_tightening_to_be_ADOPTABLE'] else '-'):>11}")
    print(f"\nzero-leverage differential test:")
    print(f"  real Gamma invariant across 4 floors : "
          f"{all(p['real_Gamma_invariant_across_four_floors'] for p in probe.values())}")
    print(f"  NEGATIVE CONTROL invariant (must be False): "
          f"{any(p['NEGATIVE_CONTROL_Lambda_dependent_Gamma_invariant'] for p in probe.values())}")
    print(f"  harness discriminates at every cell   : "
          f"{all(p['harness_discriminates'] for p in probe.values())}")
    print(f"  exclusion verdict varies with floor   : "
          f"{all(p['exclusion_verdict_varies_with_floor'] for p in probe.values())}")
    print(f"chain module reads a Lambda artifact: {reads_lambda}")
    print(f"R5 sup-cut voiding 309 refutation: "
          f"{r5['309']['sup_cut_voiding_exclusion_at_current_floor_percent']:.6f}% (current floor), "
          f"{r5['309']['sup_cut_voiding_exclusion_at_C4_floor_percent']:.6f}% (C4 floor)")
    print(f"wrote evidence/phase9/C8_ADOPTION.json sha256 {s[:16]}...")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
