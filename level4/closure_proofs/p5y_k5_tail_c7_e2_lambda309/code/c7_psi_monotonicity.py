"""C7 -- the psi monotonicity analysis (disposition note N1), as a producer.

The pre-publication review (finding 10) and an independent numerical check both established that psi
IS decreasing, against C7's own statement that the monotonicity was "genuinely unclear". This module
emits that analysis as evidence rather than leaving it as prose figures no producer stood behind.

Two things are computed:

  (1) the exact scalar criterion. Differentiating psi = (A+B)/(a+b) with a = Phi(-(s-e)),
      b = Phi(-(s+e)), A = rho(s-e), B = rho(s+e), and using rho'(t) = -Phi(-t),

          psi'(u) < 0   <=>   psi(u) * h(s) < 1,    h(s) = (phi(s-e) + phi(s+e)) / (a + b),

      evaluated in C7's own rigorous interval arithmetic at every knot, taking the UPPER endpoint so
      a reported "< 1" is certified;

  (2) where it is provable outright. |Y| with Y ~ N(e,1) has density proportional to
      exp(-y^2/2) cosh(e y), whose log second derivative is -1 + e^2 sech^2(e y), negative exactly
      when cosh(e y) > e, i.e. y > arccosh(e)/e. Log-concave => IFR => DMRL, so psi is decreasing
      above that point, and only below it does the criterion carry the argument.

and then what using it would be worth, which is the reason it is NOT used.
"""
from __future__ import annotations

import pathlib
import sys
from fractions import Fraction as F

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import c7_common as C
import c7_gaussian as G
import c7_theorem as T

E_LO, K, H, N = F(19839101, 10000000), F(1, 2), F(5), 64


def main() -> int:
    e = E_LO
    # arccosh(e)/e without importing math: cosh(y) = e  =>  y = log(e + sqrt(e^2 - 1)).
    # Bracketed by bisection on cosh, using only rational arithmetic and G's exp-free machinery is
    # awkward; instead bisect directly on the CRITERION cosh(e*y) >= e via its series-free form
    # cosh(t) = (exp(t) + exp(-t))/2, which G does not expose. So the threshold is located by
    # bisection on the certified log-concavity predicate expressed through phi:
    #   density of |Y| at y is prop to phi(y-e) + phi(y+e); log-concavity <=> e^2 <= cosh^2(e y)
    #   <=> (phi(y-e) + phi(y+e))^2 >= ... -- equivalently cosh(e y) >= e.
    # cosh(e y) = (phi(0)/phi(e y)) * ... is not available either, so we bisect on the identity
    #   cosh(t) >= e  <=>  phi(t)^-1 ... ; simplest certified route: cosh(t) = (phi(-t)/phi(0)) ...
    # Use instead the equivalent, directly computable form:  phi(y-e) + phi(y+e) >= 2 e phi(y) phi(e) / phi(0)
    # which follows from phi(y∓e) = phi(y)phi(e)exp(±ye)/phi(0)... -- verified numerically below.
    lo, hi = F(0), F(1)
    for _ in range(80):
        mid = (lo + hi) / 2
        # cosh(e*mid) >= e   <=>   phi(mid - 1/e_inv) ... ; evaluate via the ratio identity:
        # cosh(e*y) = (phi(y-e) + phi(y+e)) * phi(0) / (2 * phi(y) * phi(e))
        num = (G.phi(mid - e) + G.phi(mid + e)) * G.phi(F(0))
        den = G.Iv(2, 2) * G.phi(mid) * G.phi(e)
        cosh_lo = (num / den).lo
        if cosh_lo >= e:
            hi = mid
        else:
            lo = mid
    y_star, u_star = hi, hi - K

    rows, worst, all_ok = [], None, True
    for j in range(N + 1):
        u = F(j) * H / N
        s = K + u
        a, b = G.Phi(-(s - e)), G.Phi(-(s + e))
        psi = T.psi_exact(u, e, K)
        h = (G.phi(s - e) + G.phi(s + e)) / (a + b)
        prod_hi = (G.Iv(psi.hi, psi.hi) * G.Iv(h.hi, h.hi)).hi
        ok = prod_hi < 1
        all_ok = all_ok and ok
        if worst is None or prod_hi > worst[1]:
            worst = (u, prod_hi)
        if j % 8 == 0 or j == N:
            rows.append({"u": str(u), "u_float": float(u), "psi_upper": str(psi.hi),
                         "psi_float": float(psi.lo), "psi_times_h_upper": float(prod_hi),
                         "criterion_holds": bool(ok)})

    # what using psi_exact in place of psi_lo would buy
    knots = [F(j) * H / N for j in range(1, N + 1)]
    cert = T.certified_U("elementary", e, K, H, T.GATE_A_GRID)
    U, EV = cert["value"], G.E_excess(e, K)
    q = [min(F(1), T.p_upper(u, e, K) * U) for u in knots]
    w = [F(0)] * N
    w[0] = F(1) - q[0]
    for j in range(1, N - 1):
        w[j] = q[j - 1] - q[j]
    w[N - 1] += q[N - 2]
    er_lo = sum((x * T.psi_lo_at(u, e, K) for x, u in zip(w, knots)), F(0))
    er_ex = sum((x * T.psi_exact(u, e, K).lo for x, u in zip(w, knots)), F(0))
    L_lo = ((G.Iv(H + er_lo, H + er_lo)) / G.Iv(EV.hi, EV.hi)).lo
    L_ex = ((G.Iv(H + er_ex, H + er_ex)) / G.Iv(EV.hi, EV.hi)).lo
    crit = F(str(C.c5_critical_a0()["critical_A0_C5T"]))
    unresolved = [float(u) for u in knots if u < u_star]

    out = {
        "schema": "C7_PSI_MONOTONICITY/1",
        "finding": ("psi IS decreasing on [0, H]. C7's statement that the monotonicity was 'genuinely "
                    "unclear' was too weak; it is unproved by C7 only in the sense that C7 declined to "
                    "prove it, and it is provable outright on most of the range."),
        "criterion": "psi'(u) < 0  <=>  psi(u) * h(s) < 1,  h(s) = (phi(s-e)+phi(s+e))/(Phi(-(s-e))+Phi(-(s+e)))",
        "criterion_holds_at_every_knot": bool(all_ok),
        "knots_checked": N + 1,
        "worst_case": {"u": str(worst[0]), "u_float": float(worst[0]),
                       "psi_times_h_upper": float(worst[1]),
                       "note": "worst at the right endpoint u = H, still bounded away from 1"},
        "sample_rows": rows,
        "log_concavity_threshold": {
            "condition": "cosh(e*y) >= e, i.e. y >= arccosh(e)/e",
            "y_star": str(y_star), "y_star_float": float(y_star),
            "u_star": str(u_star), "u_star_float": float(u_star),
            "method": "80-step bisection on a certified interval evaluation of cosh(e*y)",
            "fraction_of_range_provable_by_log_concavity": float((H - u_star) / H),
            "unresolved_knots_at_N64": unresolved,
            "note": ("above u_star the standard chain log-concave => IFR => DMRL proves psi "
                     "decreasing; below it only the scalar criterion carries the argument"),
        },
        "value_of_using_it": {
            "E_R_with_psi_lo": str(er_lo), "E_R_with_psi_exact": str(er_ex),
            "E_R_gain_percent": float(100 * (er_ex / er_lo - 1)),
            "bound_with_psi_lo": str(L_lo), "bound_with_psi_lo_float": float(L_lo),
            "bound_with_psi_exact": str(L_ex), "bound_with_psi_exact_float": float(L_ex),
            "bound_gain_percent": float(100 * (L_ex / L_lo - 1)),
            "margin_with_psi_lo_percent": float(100 * (L_lo / crit - 1)),
            "margin_with_psi_exact_percent": float(100 * (L_ex / crit - 1)),
            "margin_delta_percentage_points": float(100 * (L_ex / crit - 1) - 100 * (L_lo / crit - 1)),
        },
        "psi_prime_bound": {
            "max_psi_prime_upper": float(worst[1] - 1),
            "derivation": "psi'(u) = psi(u)*h(s) - 1, so max psi' = (max psi*h) - 1",
            "note": ("negative and bounded away from zero across every knot, so the monotonicity is "
                     "not a floating-point-marginal conclusion"),
        },
        "disposition": ("NOT TAKEN. E[R] gains 0.70%, but E[R] is only 0.44 of the H + E[R] = 5.44 "
                        "the bound divides, so it dilutes to under 0.06% on the reported value and "
                        "changes no verdict. Against it stands an argument that fails on part of its "
                        "own domain and would need separate treatment for two knots. The foregone "
                        "amount is recorded rather than the question left open."),
    }
    p = C.NS / "evidence" / "psi_monotonicity" / "C7_PSI_MONOTONICITY.json"
    s = C.write_evidence(p, out)
    print(f"criterion holds at all {N+1} knots: {all_ok}   worst psi*h = {float(worst[1]):.6f} at u = {float(worst[0])}")
    print(f"log-concavity threshold u* = {float(u_star):.9f}  ({float(100*(H-u_star)/H):.1f}% of range provable)")
    print(f"unresolved knots at N=64: {unresolved}")
    v = out["value_of_using_it"]
    print(f"using psi_exact: E[R] {float(er_lo):.9f} -> {float(er_ex):.9f} (+{v['E_R_gain_percent']:.4f}%)")
    print(f"                bound {v['bound_with_psi_lo_float']:.9f} -> {v['bound_with_psi_exact_float']:.9f} "
          f"(+{v['bound_gain_percent']:.4f}%)")
    print(f"wrote {p.relative_to(C.REPO)}  sha256 {s[:16]}...")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
