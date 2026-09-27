"""Regression tests for tpt.py r1 (V3 findings T1-T4). Each test must be able to fail on the r0 code.

G1  a profile whose GEOMETRY lies in the quarantined tail band is refused even when labelled as a
    non-target cell (label spoofing, T2) -- by guard_drift, not by the label;
G2  a profile whose label m disagrees with len(terms) is refused (T2);
G3  every public function refuses a target-labelled profile (T1): rad_poly, lo_hi_polys,
    whole_cell_enclosure, penalty_* and evaluate;
G4  split-side (T3): a synthetic profile whose cap crossing lies inside the last bisection interval no
    longer raises a spurious TPT-D violation, and the closed form stays <= C5-T and >= the Riemann lower sum;
G5  unordered intervals are refused (T4);
G6  (r2, N6) float inputs are refused; G7 (r2, N5) a pointwise-empty intersection at s = 0 is refused;
G8  (r2, N7) a consumed M inconsistent with mag(H_final) is refused.
"""
from __future__ import annotations

import sys
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "code"))
sys.path.insert(0, str(HERE))
import ov_quarantine as Q  # noqa: E402
import tpt  # noqa: E402

Q.install_import_guard()


def term(**kw):
    base = dict(H_at_a=(F(-1), F(-1)), abs_G_at_a=F(0), fF=F(1, 100), fD=F(1, 100), fH=F(1, 100),
                fG=F(1), Env4=F(2))
    base.update(kw)
    return tpt.SourceTerm(**base)


def profile(**kw):
    base = dict(detector="SYNTH", m=1, cell=1, e0=F(1, 2), rho=F(1, 20), g_hi=F(-1, 10), A0=F(2),
                A1=F(3), A2=F(10), terms=[term()])
    base.update(kw)
    return tpt.CellProfile(**base)


def refused(fn, *a) -> str | None:
    """Refusal message, or None if the call went through (or the function does not exist: unguarded)."""
    try:
        fn(*a)
    except (Q.QuarantineRefusal, ValueError) as exc:
        return type(exc).__name__ + ": " + str(exc)[:80]
    except AttributeError:
        return None
    return None


def main() -> None:
    res = {}
    # G1: tail geometry (e0 ~ 1.83, inside the band) labelled as lower-front cell 44, m=5
    spoof = profile(detector="CUSUM", m=5, cell=44, e0=F(183, 100), rho=F(1, 20), terms=[term()] * 5)
    res["G1_label_spoof_geometry_refused"] = refused(tpt.evaluate, spoof)
    # G2: label m=3 carrying five terms
    res["G2_m_label_mismatch_refused"] = refused(tpt.evaluate, profile(m=3, terms=[term()] * 5))
    # G3: every public function refuses a target label (cell label 307 with benign geometry)
    tgt = profile(detector="CUSUM", m=5, cell=307, terms=[term()] * 5)  # ov-quarantine: literal-ok refusal test
    fns = {"rad_poly": lambda: tpt.rad_poly(tgt, tgt.terms[0]), "lo_hi_polys": lambda: tpt.lo_hi_polys(tgt),
           "whole_cell_enclosure": lambda: tpt.whole_cell_enclosure(tgt),
           "penalty_closed": lambda: tpt.penalty_closed(tgt), "penalty_riemann": lambda: tpt.penalty_riemann(tgt),
           "penalty_riemann_lower": lambda: tpt.penalty_riemann_lower(tgt),
           "penalty_c5t": lambda: tpt.penalty_c5t(tgt), "penalty_frozen": lambda: tpt.penalty_frozen(tgt),
           "evaluate": lambda: tpt.evaluate(tgt)}
    res["G3_public_functions_refusing"] = {k: (refused(f) is not None) for k, f in fns.items()}
    # G4: cap crossing placed at an exact dyadic point beyond 60-bit resolution: lo(s) = c0 - s, cap = c0 - s*
    rho = F(1, 20)
    s_star = rho / 2 ** 70  # crossing below the 60-bit bisection resolution, near s = 0 (the V3 T3 probe)
    t = term(H_at_a=(F(0), F(0)), fF=F(0), fD=F(0), fH=F(0), fG=F(1), Env4=F(0))  # rad(s) = A0*s (A1=A2=0)
    cp = profile(A0=F(1), A1=F(0), A2=F(0), terms=[t], H_K1=(-s_star, s_star))  # both sides capped near 0
    try:
        r = tpt.evaluate(cp)
        res["G4_split_side"] = {"raised": False, "closed_le_c5t": r["P_tpt"] <= r["P_c5t"],
                                "lower_le_closed": r.get("P_riemann_lower", F(10 ** 9)) <= r["P_tpt"]}
    except AssertionError as exc:
        res["G4_split_side"] = {"raised": True, "msg": str(exc)}
    # G5: unordered centre interval
    res["G5_unordered_refused"] = refused(tpt.evaluate, profile(terms=[term(H_at_a=(F(1), F(0)))]))
    # G6 (r2, N6): float input refused
    res["G6_float_refused"] = refused(tpt.evaluate, profile(terms=[term(Env4=2.0)]))
    # G7 (r2, N5): pointwise-empty intersection at s = 0 refused (cap above the profile's upper end at e0)
    cp7 = profile(H_K1=(F(0), F(10)))  # centre -1, rad(0) tiny: hi(0) < 0 = cap.lo -> empty at s = 0
    res["G7_empty_pointwise_refused"] = refused(tpt.evaluate, cp7)
    # G8 (r2, N7): M_consumed inconsistent with mag(H_final) refused
    res["G8_M_consumed_mismatch_refused"] = refused(tpt.penalty_frozen, profile(M_consumed=F(12345)))
    ok = (res["G6_float_refused"] and res["G7_empty_pointwise_refused"]
          and res["G8_M_consumed_mismatch_refused"]
          and res["G1_label_spoof_geometry_refused"] and "DRIFT_BAND" in res["G1_label_spoof_geometry_refused"]
          and res["G2_m_label_mismatch_refused"]
          and all(res["G3_public_functions_refusing"].values())
          and res["G4_split_side"].get("raised") is False and res["G4_split_side"]["closed_le_c5t"]
          and res["G4_split_side"]["lower_le_closed"]
          and res["G5_unordered_refused"])
    for k, v in res.items():
        print(k, v)
    print("TPT GUARD TESTS", "PASS" if ok else "FAIL")
    Q.log_execution("streams/E_assembly/test_tpt_guards.py", "tpt.py r1 regression tests (T1-T4)",
                    cells_touched=[], klass="SYNTHETIC_VALIDATION")
    raise SystemExit(0 if ok else 1)


if __name__ == "__main__":
    main()
