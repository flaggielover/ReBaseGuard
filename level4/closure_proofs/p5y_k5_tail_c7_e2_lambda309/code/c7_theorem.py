"""Theorem C7-E2: an overshoot-corrected lower bound on Lambda = E_a[tau], strictly stronger than C4's.

    E_a[tau]  >=  ( H + psi_min ) / E[V],        V := (|z| - K)^+,   z ~ N(-e, 1)

against C4's  E_a[tau] >= H / E[V].  The whole gain is the term psi_min > 0, the OVERSHOOT C4 discarded.

------------------------------------------------------------------------------------------------------
WHERE C4 LEAVES VALUE ON THE TABLE
------------------------------------------------------------------------------------------------------
C4's chain is: max(s+, s-) <= W_t := sum_{i<=t} V_i pathwise, so tau >= tau' := min{t : W_t > H}; then
Wald gives H <= E[W_tau'] = E[V] E[tau'], hence E[tau] >= E[tau'] >= H / E[V].

The inequality `H <= E[W_tau']` throws away the overshoot. W_tau' does not land on H, it JUMPS past it,
and the expected jump is a positive quantity that can be bounded below with no new information at all.

------------------------------------------------------------------------------------------------------
THEOREM C7-E2
------------------------------------------------------------------------------------------------------
Let V >= 0 be i.i.d. with 0 < E[V] < infinity, W_n := sum_{i<=n} V_i, W_0 = 0, and for H > 0 let
tau' := min{n : W_n > H}, assumed to have E[tau'] < infinity. Define, for u >= 0,

    g(u) := E[(V - u)^+],    p(u) := P(V > u),    psi(u) := g(u) / p(u)   (the mean residual life of V),
    psi_min := inf_{u in [0, H]} psi(u).

Then      E[tau']  >=  ( H + psi_min ) / E[V].

*Proof.* Write R := W_tau' - H > 0 and D_n := H - W_{n-1}. On {tau' >= n} we have W_{n-1} <= H and
W_{n-1} >= 0, so D_n in [0, H]. Since {tau' >= n} = {W_{n-1} <= H} is F_{n-1}-measurable and V_n is
independent of F_{n-1},

    E[R] = sum_n E[(W_{n-1} + V_n - H) 1{tau' >= n, V_n > D_n}]
         = sum_n E[ 1{tau' >= n} g(D_n) ]                                (freeze F_{n-1}, integrate V_n)
         = sum_n E[ 1{tau' >= n} psi(D_n) p(D_n) ]
        >= psi_min * sum_n E[ 1{tau' >= n} p(D_n) ]
         = psi_min * sum_n P(tau' = n)   =   psi_min,

because P(tau' = n | F_{n-1}) = P(V_n > D_n) = p(D_n) on {tau' >= n}. Wald (valid in [0, +infinity] by
Tonelli, and finite here) gives E[V] E[tau'] = E[W_tau'] = H + E[R] >= H + psi_min. Divide. QED

Setting psi_min = 0 recovers C4 exactly, so C7-E2 is never worse and is strictly better whenever
psi_min > 0 -- which holds for any V with unbounded support.

------------------------------------------------------------------------------------------------------
A CERTIFIABLE LOWER BOUND ON psi_min FOR THE FROZEN CUSUM V
------------------------------------------------------------------------------------------------------
With Y := -z ~ N(e, 1) and s := K + u, {V > u} = {|z| > s} = {Y > s} u {Y < -s}, so psi(u) is a weighted
average of the two one-sided Gaussian mean residual lives at distances s - e and s + e. Writing
r(t) := phi(t)/Phi(-t) - t for the standard normal MRL and h(t) := phi(t)/Phi(-t) for the hazard,

    psi(u) = w * r(s - e) + (1 - w) * r(s + e),    w = Phi(-(s-e)) / (Phi(-(s-e)) + Phi(-(s+e))).

Dropping the (non-negative) lower-tail numerator and keeping the lower tail in the denominator,

    psi(u)  >=  r(s - e) / (1 + f(s)),        f(s) := Phi(-s-e) / Phi(-s+e)  in (0, 1).

TWO CLASSICAL MONOTONICITY FACTS, both used and both proved:

  (M1) r is strictly DECREASING on R.  r' = h' - 1 = h(h - t) - 1 < 0 is exactly the standard Mills
       upper bound h(t) < (t + sqrt(t^2 + 4))/2.  Hence r(s-e) >= r(K + H - e) for all u in [0, H].

  (M2) f is strictly DECREASING in s.  d(ln f)/ds = h(s - e) - h(s + e) < 0 because h is increasing,
       which is log-concavity of Phi(-.).  Hence f(s) <= f(K) for all u >= 0.

Therefore, uniformly on u in [0, H],

    psi_min  >=  r(K + H - e) / (1 + f(K)),

every factor of which is an explicit Gaussian expression at a rational argument. Both monotonicity facts
are additionally exercised numerically on a ladder by `c7_mutations.py`; the ladder is a check, not the
proof.

------------------------------------------------------------------------------------------------------
SCOPE
------------------------------------------------------------------------------------------------------
Lambda_309 = sup over the CLOSED cell of E_a[tau](e), so a pointwise bound at ANY single e in the closed
cell is a valid lower bound on Lambda_309. This is the same structural fact C4 used and C4's adjudicator
verified; C7 changes the bound, not the quantifier. The evaluation point is e_lo, which is optimal for
this family because both H/E[V] and the psi term fall as e rises.
"""
import sys
from fractions import Fraction as F
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import c7_gaussian as G                                                            # noqa: E402


class TheoremRefusal(Exception):
    pass


def hazard(t: F) -> G.Iv:
    """h(t) = phi(t) / Phi(-t), as a rigorous interval."""
    return G.phi(t) / G.Phi(-F(t))


def mrl(t: F) -> G.Iv:
    """r(t) = phi(t)/Phi(-t) - t, the standard normal mean residual life. Rigorous interval."""
    return hazard(t) - G.Iv(F(t), F(t))


def f_ratio(s: F, e: F) -> G.Iv:
    """f(s) = Phi(-s-e) / Phi(-s+e) in (0, 1)."""
    s, e = F(s), F(e)
    return G.Phi(-(s + e)) / G.Phi(-(s - e))


def psi_min_lower(e: F, K: F, H: F) -> dict:
    """A certified lower bound on inf_{u in [0,H]} psi(u), via (M1) and (M2)."""
    e, K, H = F(e), F(K), F(H)
    if not (K > 0 and H > 0):
        raise TheoremRefusal("K and H must be positive")
    if e - K <= 0:
        raise TheoremRefusal("this bound is written for e > K, where the upper tail of Y dominates")
    t_worst = K + H - e                       # (M1): r is minimised at the largest s = K + H
    if t_worst <= 0:
        raise TheoremRefusal("K + H - e must be positive for the upper-tail MRL to be the binding one")
    r_lo = mrl(t_worst)
    f_hi = f_ratio(K, e)                      # (M2): f is maximised at the smallest s = K
    if not (f_hi.hi < 1):
        raise TheoremRefusal("f(K) must be < 1")
    lower = G.Iv(r_lo.lo, r_lo.lo) / (G.Iv(1, 1) + G.Iv(f_hi.hi, f_hi.hi))
    if lower.lo <= 0:
        raise TheoremRefusal("psi_min lower bound is not positive")
    return {"t_worst": t_worst, "r_at_t_worst": r_lo, "f_at_K": f_hi, "psi_min_lower": lower.lo}


def lambda_lower(e: F, K: F, H: F) -> dict:
    """The theorem, assembled with every rounding in the safe direction.

    A LOWER bound on (H + psi_min)/E[V] needs psi_min from below and E[V] from ABOVE.
    """
    e, K, H = F(e), F(K), F(H)
    pm = psi_min_lower(e, K, H)
    EV = G.E_excess(e, K)                     # interval; the upper end is the safe one here
    if EV.lo <= 0:
        raise TheoremRefusal("E[V] must be positive")
    num_lo = H + pm["psi_min_lower"]
    L = G.Iv(num_lo, num_lo) / G.Iv(EV.hi, EV.hi)
    c4 = G.Iv(H, H) / G.Iv(EV.hi, EV.hi)      # C4's bound from the same E[V], for an exact comparison
    if not L.lo > c4.lo:
        raise TheoremRefusal("C7-E2 did not strictly improve on C4 at the same E[V]; impossible for psi_min > 0")
    return {"e": e, "K": K, "H": H,
            "E_V_upper": EV.hi, "E_V_interval": EV,
            "psi_min_lower": pm["psi_min_lower"], "psi_detail": pm,
            "C4_bound_lower": c4.lo, "C7_bound_lower": L.lo,
            "absolute_improvement": L.lo - c4.lo,
            "relative_improvement": (L.lo - c4.lo) / c4.lo}


# ==================================================================================================
# TIER 2 -- a sharper psi bound using a CERTIFIED UPPER bound on E[tau']
# ==================================================================================================
"""Theorem C7-E2b (two-tier overshoot bound).

Tier 1 replaces E[R] by inf psi, which is attained only where the deficit D is near H -- an event of tiny
probability. Tier 2 shows that directly, using a certified UPPER bound on E[tau'] and nothing else.

From the tier-1 proof, E[R] = integral of psi against a PROBABILITY measure mu on [0, H], namely
mu(du) = sum_n E[1{tau' >= n} p(D_n) 1{D_n in du}]  (it has total mass sum_n P(tau' = n) = 1).
For any u0 in [0, H], since p is non-increasing and p(D_n) <= p(u0) whenever D_n > u0,

    mu((u0, H])  =  sum_n E[1{tau' >= n} p(D_n) 1{D_n > u0}]
                 <= p(u0) * sum_n P(tau' >= n)  =  p(u0) * E[tau']  <=  p(u0) * U

for any certified U >= E[tau']. With q := min(1, p(u0) * U),

    E[R]  >=  psi_lo(u0) * (1 - q)  +  psi_lo(H) * q,

where psi_lo(u) := r(K + u - e) / (1 + f(K)) is the tier-1 uniform lower bound on psi over [0, u]
(valid there because r and f are both decreasing -- (M1) and (M2); NO monotonicity of psi itself is
needed). The expression is decreasing in q, so q must be taken from ABOVE.

E[tau'] <= E[tau] because tau >= tau' pathwise, and E[tau] <= Lambda_309 <= A0 for any admissible
atom constant A0 -- a certified upper bound, which is not circular: we use an upper bound on the
quantity to sharpen a LOWER bound on it.

Tier 2 therefore depends on a committed operator constant and so on the Arb/FLINT certification surface;
tier 1 does not depend on any registry constant at all. Both are reported, and the surface-independent
tier-1 value is the floor that survives if that surface is ever questioned.
"""


def p_upper(u: F, e: F, K: F) -> F:
    """An upper bound on p(u) = P(V > u) = Phi(-(s-e)) + Phi(-(s+e)), s = K + u."""
    s = F(K) + F(u)
    return (G.Phi(-(s - F(e))) + G.Phi(-(s + F(e)))).hi


def psi_lo_at(u: F, e: F, K: F) -> F:
    """r(K + u - e) / (1 + f(K)) -- a lower bound on psi(v) for EVERY v in [0, u]."""
    t = F(K) + F(u) - F(e)
    # t may be NEGATIVE for small u: with e = 1.98 > K = 0.5 the lower reflected tail sits on the
    # favourable side. Both monotonicity facts hold on all of R -- (M1) because the Gaussian is
    # log-concave everywhere, (M2) because d/ds log f = h(s-e) - h(s+e) < 0 for every real s -- so no
    # positivity hypothesis is needed. What IS needed is r > 0, which holds identically since
    # r(t) = E[Z - t | Z > t].
    r = mrl(t)
    fk = f_ratio(F(K), F(e))
    if not r.lo > 0:
        raise TheoremRefusal(f"certified lower bound on the mean residual life at t={float(t)} is not positive")
    return (G.Iv(r.lo, r.lo) / (G.Iv(1, 1) + G.Iv(fk.hi, fk.hi))).lo


def lambda_lower_tier2(e: F, K: F, H: F, U: F, ladder) -> dict:
    """Tier 2, maximised over a PROSPECTIVELY FIXED ladder of split points u0.

    `ladder` is fixed by the frozen gate before evaluation. Taking the max over a fixed finite set of
    individually valid lower bounds is itself valid and is not result-dependent selection.
    """
    e, K, H, U = F(e), F(K), F(H), F(U)
    EV = G.E_excess(e, K)
    psi_H = psi_lo_at(H, e, K)
    rows = []
    for u0 in ladder:
        u0 = F(u0)
        if not (0 <= u0 <= H):
            raise TheoremRefusal("split point outside [0, H]")
        pu = p_upper(u0, e, K)
        q = min(F(1), pu * U)                                  # q from ABOVE: the bound decreases in q
        psi_u0 = psi_lo_at(u0, e, K)
        ER = psi_u0 * (1 - q) + psi_H * q
        if ER < psi_H:
            raise TheoremRefusal("tier-2 E[R] fell below the tier-1 floor, which is impossible")
        L = (G.Iv(H + ER, H + ER) / G.Iv(EV.hi, EV.hi)).lo
        rows.append({"u0": u0, "p_upper": pu, "q_upper": q, "psi_lo_u0": psi_u0,
                     "E_R_lower": ER, "L_lower": L})
    best = max(rows, key=lambda r: r["L_lower"])
    return {"U_used": U, "psi_lo_H": psi_H, "E_V_upper": EV.hi, "ladder": [str(F(x)) for x in ladder],
            "rows": rows, "best": best}
