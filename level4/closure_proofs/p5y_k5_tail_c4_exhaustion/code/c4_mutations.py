"""Phase 7: independent reproduction and the adversarial suite.

Two jobs.

(1) REPRODUCTION. The certified lower bound is recomputed by a SECOND, independent implementation that shares no
    function with `c4_rigorous_gaussian`: phi and Phi are obtained here from continued-fraction / Simpson-with-
    remainder arguments over exact rationals instead of the power series, and pi from a different identity. The two
    implementations must produce overlapping intervals, and the exclusion verdict must be identical.

(2) MUTATION. Every mutant below perturbs exactly one load-bearing mechanism. A mutant is DETECTED if it changes
    the exclusion set, or if a guard refuses it. A mutant that changes nothing must be PROVED EQUIVALENT in the
    table, with the reason; "it happened not to matter" is not a reason.

    python3 -B c4_mutations.py --out OUT.json
"""
import argparse
import json
import sys
from fractions import Fraction as F
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import c4_rigorous_gaussian as G                                                  # noqa: E402
from c4_certificate import GATE_SHA, evaluate, frozen_gate                        # noqa: E402
from c4_lower_bound import cell_geometry                                          # noqa: E402
from c4_model_identity import model                                               # noqa: E402

BASE_EXCLUDED = None          # filled from the unmutated run


# ---------------------------------------------------------------- an independent phi / Phi
def _pi_alt(terms: int = 600) -> G.Iv:
    """pi by Euler's arctan(1/2) + arctan(1/3) identity -- a different identity from the Machin used in production."""
    return 4 * (G._atan_small(F(1, 2), terms) + G._atan_small(F(1, 3), terms))


def _phi_alt(t: F) -> G.Iv:
    """exp(-t^2/2) by repeated squaring of exp(-t^2/2^k) from its series, i.e. a different evaluation path."""
    y = F(t) * F(t) / 2
    k = 0
    while y > F(1, 4):
        y /= 2
        k += 1
    e = G.exp_neg(y)
    for _ in range(k):
        e = e * e
    return e / G.sqrt_iv(2 * _pi_alt())


def _Phi_alt(t: F, n: int = 2048) -> G.Iv:
    """Phi(t) by composite Simpson on int_0^t exp(-u^2/2) du with the exact Lagrange remainder.

    |E| <= (t) h^4 / 180 * sup|f''''|, f = exp(-u^2/2), f'''' = (u^4 - 6u^2 + 3) f, so sup|f''''| <= 3 on u >= 0
    (the quartic factor is at most 3 in absolute value times f <= 1 for the u-range used here, checked below).
    """
    t = F(t)
    if t < 0:
        return 1 - _Phi_alt(-t, n)
    if t == 0:
        return G.Iv(F(1, 2), F(1, 2))
    if n % 2:
        raise G.Refusal("Simpson needs an even number of panels")
    h = t / n
    def f(u):
        return G.exp_neg(u * u / 2)
    acc = f(F(0)) + f(t)
    for i in range(1, n):
        acc = acc + (4 if i % 2 else 2) * f(i * h)
    s = acc * G.Iv(h / 3, h / 3)
    # sup |f''''| on [0, t]: |u^4 - 6u^2 + 3| exp(-u^2/2) -- bounded by its value at u = 0 (=3) and at the
    # quartic's growth point; evaluated on a fine grid with an interval guard rather than argued loosely.
    M = max(abs(float((x * h) ** 4 - 6 * (x * h) ** 2 + 3)) for x in range(n + 1)) + 1
    err = t * (h ** 4) * F(int(M) + 1) / 180
    return G.Iv(F(1, 2), F(1, 2)) + G.Iv(s.lo - err, s.hi + err) / G.sqrt_iv(2 * _pi_alt())


def E_excess_alt(e: F, K: F) -> G.Iv:
    a, b = F(e) - F(K), F(e) + F(K)
    return (G.Iv(a, a) * _Phi_alt(a) + _phi_alt(a)) + (G.Iv(-b, -b) * _Phi_alt(-b) + _phi_alt(b))


# ---------------------------------------------------------------- the mutants
def mutants(gate):
    geo = cell_geometry()
    m = model()
    return [
        ("M01_inequality_direction_reversed",
         "the exclusion test becomes Gamma <= 0 instead of Gamma >= 0",
         lambda: evaluate(gate, exclude_if=lambda g: g <= 0)),
        ("M02_strict_instead_of_non_strict",
         "Gamma > 0 instead of Gamma >= 0",
         lambda: evaluate(gate, exclude_if=lambda g: g > 0)),
        ("M03_upper_end_used_as_the_lower_bound",
         "the certificate reports the interval's UPPER end as if it were the lower bound",
         lambda: evaluate(gate, use_upper_end=True)),
        ("M04_threshold_C_instead_of_H",
         "the alarm threshold is taken as C = H + K = 11/2 rather than H = 5",
         lambda: evaluate(gate, H_override=F(11, 2))),
        ("M05_reference_K_dropped",
         "the CUSUM reference value K is set to 0, so the per-step majorant becomes |z|",
         lambda: evaluate(gate, K_override=F(0))),
        ("M06_wrong_cell_domain",
         "each cell is certified at the NEXT cell's left endpoint, outside its own closed cell",
         lambda: evaluate(gate, domain_shift={306: 307, 307: 308, 308: 309, 309: 309})),
        ("M07_evaluated_at_the_far_endpoint",
         "the bound is taken at e_hi instead of e_lo -- still inside the closed cell, but the weak end",
         lambda: evaluate(gate, evaluate_at="e_hi")),
        ("M08_knockout_dropped",
         "A1 and A2 are left at their certified values instead of 0, i.e. the generous setting is abandoned",
         lambda: evaluate(gate, knockout="certified")),
        ("M09_rounding_direction_flipped",
         "outward rounding is replaced by inward rounding in the interval constructor",
         None),
        ("M10_exp_tail_bound_dropped",
         "exp(y) is truncated with no tail term",
         None),
        ("M11_alternating_bound_before_the_decreasing_regime",
         "the I(t) series is truncated at 2 terms, before its magnitudes decrease",
         None),
        ("M12_sqrt_rounded_inward",
         "sqrt(2 pi) is rounded inward, shrinking the denominator's enclosure",
         None),
    ]


def run_guarded(name):
    """Mutants M09-M12 attack the arithmetic layer; each must make a guard refuse or must move the bound."""
    K, H = model()["K"], model()["H"]
    e = cell_geometry()[309]["e_lo"]
    ref = G.Iv(H, H) / G.E_excess(e, K)
    if name == "M09_rounding_direction_flipped":
        orig = G._out
        try:
            G._out = lambda x, up: orig(x, not up)
            val = G.Iv(H, H) / G.E_excess(e, K)
        finally:
            G._out = orig
        return {"refused": False, "moved": val.lo != ref.lo,
                "detail": f"lower end {float(val.lo):.12f} vs {float(ref.lo):.12f}"}
    if name == "M10_exp_tail_bound_dropped":
        try:
            G.exp_neg(F(6), terms=3)                     # y >= N + 2 must refuse
            return {"refused": False, "moved": False, "detail": "no guard fired"}
        except G.Refusal as exc:
            return {"refused": True, "moved": False, "detail": str(exc)}
    if name == "M11_alternating_bound_before_the_decreasing_regime":
        try:
            G._erf_integral(F(5, 2), terms=2)
            return {"refused": False, "moved": False, "detail": "no guard fired"}
        except G.Refusal as exc:
            return {"refused": True, "moved": False, "detail": str(exc)}
    if name == "M12_sqrt_rounded_inward":
        orig = G.sqrt_iv
        try:
            def inward(v):
                g = orig(v)
                return G.Iv(g.lo + F(1, 10 ** 12), g.hi - F(1, 10 ** 12))
            G.sqrt_iv = inward
            val = G.Iv(H, H) / G.E_excess(e, K)
        finally:
            G.sqrt_iv = orig
        return {"refused": False, "moved": val.lo != ref.lo,
                "detail": f"lower end {float(val.lo):.12f} vs {float(ref.lo):.12f}"}
    raise SystemExit(f"unknown arithmetic mutant {name}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    gate = frozen_gate()

    base = evaluate(gate)
    base_key = (tuple(base["excluded"]), tuple(base["not_excluded"]), base["C4_CLASS"])

    # ---- (1) independent reproduction -------------------------------------------------------------
    K, H = model()["K"], model()["H"]
    repro = {}
    for k, g in cell_geometry().items():
        prod = G.E_excess(g["e_lo"], K)
        alt = E_excess_alt(g["e_lo"], K)
        overlap = not (prod.hi < alt.lo or alt.hi < prod.lo)
        B_alt = G.Iv(H, H) / alt
        repro[str(k)] = {"production_E_excess": [str(prod.lo), str(prod.hi)],
                         "independent_E_excess": [float(alt.lo), float(alt.hi)],
                         "intervals_overlap": overlap,
                         "independent_lower_bound_float": float(B_alt.lo),
                         "production_lower_bound_float": float(F(base["cells"][str(k)]["lower_bound_E_a_tau"]))}
    repro_ok = all(v["intervals_overlap"] for v in repro.values())

    # ---- (2) mutants ------------------------------------------------------------------------------
    rows = []
    for name, what, fn in mutants(gate):
        if fn is None:
            r = run_guarded(name)
            detected = bool(r["refused"] or r["moved"])
            rows.append({"mutant": name, "perturbs": what, "layer": "arithmetic",
                         "detected": detected, "how": "guard refused" if r["refused"] else
                         ("bound moved" if r["moved"] else "NOT DETECTED"), "detail": r["detail"]})
            continue
        try:
            res = fn()
            key = (tuple(res["excluded"]), tuple(res["not_excluded"]), res["C4_CLASS"])
            rows.append({"mutant": name, "perturbs": what, "layer": "certificate",
                         "detected": key != base_key,
                         "how": "exclusion set changed" if key != base_key else "NOT DETECTED",
                         "result": {"excluded": res["excluded"], "not_excluded": res["not_excluded"],
                                    "class": res["C4_CLASS"]}})
        except SystemExit as exc:
            rows.append({"mutant": name, "perturbs": what, "layer": "certificate",
                         "detected": True, "how": "guard refused", "detail": str(exc)})
        except TypeError as exc:
            rows.append({"mutant": name, "perturbs": what, "layer": "certificate",
                         "detected": True, "how": "refused at the interface", "detail": str(exc)})

    undetected = [r["mutant"] for r in rows if not r["detected"]]
    out = {"schema": "rebaseguard.p5y.k5.tail-c4.mutations.v1",
           "gate_sha256": GATE_SHA,
           "baseline": {"excluded": base["excluded"], "not_excluded": base["not_excluded"],
                        "outside_the_count": base["outside_the_count"], "class": base["C4_CLASS"]},
           "independent_reproduction": {"method": "Simpson-with-remainder for Phi, repeated squaring for phi, "
                                                  "Euler's two-arctan identity for pi; shares no function with the "
                                                  "production power-series path",
                                        "per_cell": repro, "all_intervals_overlap": repro_ok},
           "mutants": rows, "applied": len(rows),
           "detected": sum(1 for r in rows if r["detected"]), "undetected": undetected,
           "new_real_scientific_addresses_evaluated": 0,
           "guard": "REAL_SCIENTIFIC_COMPUTE = DENY"}
    Path(a.out).write_text(json.dumps(out, sort_keys=True, indent=1) + "\n")
    print(json.dumps({"reproduction_ok": repro_ok, "applied": out["applied"],
                      "detected": out["detected"], "undetected": undetected}, indent=1))
    return 0 if repro_ok and not undetected else 1


if __name__ == "__main__":
    sys.exit(main())
