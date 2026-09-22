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
    _require_frozen_model(K, H)
    _require_in_cell(e)
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
# TIER 2 -- REMOVED
# ==================================================================================================
# lambda_lower_tier2 was the single-split precursor of the multi-tier theorem and had no caller. It
# was removed rather than left in place: it took a BARE U with no certificate and no _resolve_U, and
# never checked cell membership, so both repaired exploits stayed reachable through it
# (lambda_lower_tier2(e=1.90, U=0.1) returned 4.219038180 with no refusal). A dead public entry point
# that bypasses the guards the erratum says are "now enforced in code" falsifies that sentence. The
# gate's u0_ladder_for_tier2 is consequently inert; see ERRATUM_C7_GATE.md E7.

# --- shared helpers (these lived in the removed tier-2 block; tier k depends on them) ----------

def p_upper(u: F, e: F, K: F) -> F:
    """An upper bound on p(u) = P(V > u) = Phi(-(s-e)) + Phi(-(s+e)), s = K + u."""
    s = F(K) + F(u)
    return (G.Phi(-(s - F(e))) + G.Phi(-(s + F(e)))).hi


def psi_lo_at(u: F, e: F, K: F) -> F:
    """r(K + u - e) / (1 + f(K)) -- a lower bound on psi(v) for EVERY v in [0, u].

    Valid on the whole subinterval because r and f are both decreasing -- (M1) and (M2) -- so
    evaluating each at the endpoint that minimises the quotient bounds psi below throughout. No
    monotonicity of psi itself is needed or claimed.
    """
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


# ==================================================================================================
# TIER k -- the multi-tier bound. Tier 2 is the k = 2 case.
# ==================================================================================================
"""Theorem C7-E2c (multi-tier overshoot bound).

Tier 2 splits [0, H] once. Splitting it k times is strictly better and costs nothing new: the same
two monotonicity facts and the same certified U.

Fix a partition 0 = u_0 < u_1 < ... < u_k = H and write m_j = mu((u_{j-1}, u_j]), so m_j >= 0 and
sum_j m_j = 1. Two families of facts constrain m:

  (i) psi >= psi_lo(u_j) on (u_{j-1}, u_j], because psi_lo(u) is a valid lower bound for psi on ALL
      of [0, u] -- it is built from r and f at the right-hand endpoint, both decreasing.
  (ii) sum_{j > i} m_j = mu((u_i, H]) <= p(u_i) * E[tau'] <= p(u_i) * U =: q_i, and also <= 1.

So E[R] >= min { sum_j psi_lo(u_j) m_j : m >= 0, sum m_j = 1, sum_{j>i} m_j <= q_i for all i }.

Because psi_lo(u_j) is non-increasing in j, the minimising m pushes as much mass as far RIGHT as the
tail constraints allow, and the LP is solved in closed form by the greedy assignment

    m_k = q_{k-1},   m_j = q_{j-1} - q_j  (1 < j < k),   m_1 = 1 - q_1,

which is feasible exactly because q is non-increasing (p is decreasing) with q_0 = 1 after clipping,
and telescopes to sum_j m_j = 1. Hence

    E[R] >= psi_lo(u_1) (1 - q_1) + sum_{j=2}^{k-1} psi_lo(u_j) (q_{j-1} - q_j) + psi_lo(u_k) q_{k-1}.

Every q_i is taken from ABOVE and every psi_lo from BELOW, so the whole expression is a certified
lower bound. Refining the partition can only raise it -- it adds constraints to the same LP -- and it
saturates at the information content of U, which is what the family-exhaustion argument then uses.
"""


def lambda_lower_tier_k(e: F, K: F, H: F, U_cert, partition) -> dict:
    """`partition` is the interior-and-right knots u_1 < ... < u_k = H, fixed by the frozen gate.

    `U_cert` MUST be a certificate from certified_U(); a bare number is refused. See the U PROVENANCE
    section below for why.
    """
    e, K, H = F(e), F(K), F(H)
    _require_frozen_model(K, H)
    _require_in_cell(e)
    U, U_deps = _resolve_U(U_cert, e, K, H)
    us = [F(u) for u in partition]
    if not us or us[-1] != H:
        raise TheoremRefusal("partition must end exactly at H")
    if any(b <= a for a, b in zip(us, us[1:])) or us[0] <= 0:
        raise TheoremRefusal("partition must be strictly increasing and positive")

    psi = [psi_lo_at(u, e, K) for u in us]
    if any(b > a for a, b in zip(psi, psi[1:])):
        raise TheoremRefusal("psi_lo must be non-increasing along the partition; monotonicity violated")

    # INDEPENDENT admissibility check on every psi_lo the LP consumes. psi_lo[j] must lower-bound psi
    # on the whole of (u_{j-1}, u_j], and u_j lies in that subinterval, so psi_lo[j] <= psi(u_j). psi is
    # recomputed here from its definition, sharing no code path with psi_lo_at beyond the Gaussian
    # primitives. This is the check that catches an endpoint error; see psi_exact's docstring.
    for j, u in enumerate(us):
        pe = psi_exact(u, e, K)
        if psi[j] > pe.lo:
            raise TheoremRefusal(
                f"psi_lo[{j}] = {float(psi[j])} exceeds psi({float(u)}) <= {float(pe.hi)}, so it does "
                f"not lower-bound psi on the subinterval ending at u_{j}")

    q = [min(F(1), p_upper(u, e, K) * U) for u in us]
    if any(b > a for a, b in zip(q, q[1:])):
        raise TheoremRefusal("q must be non-increasing along the partition; p is not decreasing")

    k = len(us)
    weights = [F(0)] * k
    if k == 1:
        # Edge case: a single knot at H means the only subinterval is (0, H], which carries ALL the
        # mass. There is no tail constraint, because the only tail is beyond H and mu([0,H]) = 1. The
        # greedy formula below would wrongly leave m_1 = 1 - q_1 and lose mass q_1. Kill gate KG4,
        # which requires tier-k at k = 1 to reproduce tier 1 exactly, is what surfaced this.
        weights[0] = F(1)
    else:
        weights[0] = F(1) - q[0]                   # m_1
        for j in range(1, k - 1):
            weights[j] = q[j - 1] - q[j]           # m_{j+1}
        weights[k - 1] += q[k - 2]                 # m_k absorbs the surviving tail mass
    if any(w < 0 for w in weights):
        raise TheoremRefusal("greedy LP solution is infeasible; a monotonicity assumption failed")
    tot = sum(weights)
    if tot != 1:
        raise TheoremRefusal(f"LP weights must sum to exactly 1, got {tot}")

    ER = sum((w * ps for w, ps in zip(weights, psi)), F(0))
    floor = psi[-1]
    if ER < floor:
        raise TheoremRefusal("multi-tier E[R] fell below the tier-1 floor, which is impossible")

    EV = G.E_excess(e, K)
    L = (G.Iv(H + ER, H + ER) / G.Iv(EV.hi, EV.hi)).lo
    return {"k": k, "U_used": U, "U_source": U_cert["source"], "U_dependencies": U_deps,
            "E_V_upper": EV.hi, "E_R_lower": ER, "L_lower": L,
            "tier1_floor_psi_lo_H": floor,
            "knots": [{"u": u, "psi_lo": ps, "q_upper": qq, "lp_weight": w}
                      for u, ps, qq, w in zip(us, psi, q, weights)]}


# ==================================================================================================
# LEMMA C7-U -- a certified upper bound on E[tau'] that needs NO registry constant and NO citation
# ==================================================================================================
"""Lemma C7-U (elementary truncation bound on the overshoot, hence on E[tau']).

The multi-tier theorem needs some certified U >= E[tau']. The obvious supply is a certified admissible
atom constant A0 (Lemma SM(d) makes A0 >= sup_cell E_a[tau] >= E[tau] >= E[tau']), but that ties the
result to the Arb/FLINT certification surface. Lorden's inequality E[R] <= E[V^2]/E[V] supplies a
better one with no registry, but it is an external theorem C7 does not re-prove. This lemma supplies a
third, weaker than both but proved here from scratch, so that a bound exists which depends on neither.

STEP 0 (finiteness, which tiers 2+ need in any case). V >= 0 iid with E[V] > 0, so there is c > 0 with
p := P(V > c) > 0. Reaching H needs at most ceil(H/c) increments exceeding c, so tau' is dominated by a
sum of ceil(H/c) + 1 iid Geometric(p) variables and E[tau'] <= (ceil(H/c) + 1)/p < infinity. Both c and
p are chosen and evaluated rigorously below, so the finiteness is certified, not assumed.

STEP 1. S_{tau'-1} <= H by definition of tau', so the overshoot satisfies

    R = S_{tau'} - H = S_{tau'-1} + V_{tau'} - H  <=  V_{tau'}.

STEP 2. For any a > 0, V_{tau'} <= a + V_{tau'} 1{V_{tau'} > a}, and

    E[V_{tau'} 1{V_{tau'} > a}]  =  sum_n E[1{tau' = n} V_n 1{V_n > a}]
                                 <= sum_n E[1{tau' >= n} V_n 1{V_n > a}]
                                  = sum_n P(tau' >= n) E[V 1{V > a}]  =  E[tau'] g(a),

where g(a) := E[V 1{V > a}]. The factorisation is legitimate because {tau' >= n} = {S_{n-1} <= H} is
measurable with respect to V_1, ..., V_{n-1} and hence independent of V_n. So E[R] <= a + E[tau'] g(a).

STEP 3. Wald gives E[tau'] = (H + E[R])/E[V] (an identity in [0, infinity] by Tonelli, and finite by
step 0). Substituting and rearranging, whenever g(a) < E[V],

    E[R]  <=  (a E[V] + H g(a)) / (E[V] - g(a)),        U(a) := (H + that) / E[V]  >=  E[tau'].

With s = K + a, g(a) = rho(s-e) + rho(s+e) + a [Phi(-(s-e)) + Phi(-(s+e))], where rho(t) = E[(Z-t)^+].
Every a in a prospectively fixed grid yields a VALID U, so taking the minimum over that grid is sound
and is not result-dependent selection.
"""


def rho1(t: F) -> G.Iv:
    """E[(Z - t)^+] = phi(t) - t Phi(-t)."""
    t = F(t)
    return G.phi(t) - G.Iv(t, t) * G.Phi(-t)


def rho2(t: F) -> G.Iv:
    """E[((Z - t)^+)^2] = (1 + t^2) Phi(-t) - t phi(t)."""
    t = F(t)
    return G.Iv(1 + t * t, 1 + t * t) * G.Phi(-t) - G.Iv(t, t) * G.phi(t)


def g_tail(a: F, e: F, K: F) -> F:
    """An UPPER bound on g(a) = E[V 1{V > a}].

    REQUIRES a > 0, which is Lemma C7-U's own hypothesis. The closed form below equals E[V 1{V>a}]
    only when {V > a} = {|z| > K + a}; for a < 0 the event is all of Omega and g(a) = E[V], so the
    formula silently returns something that is not g(a). Leaving this unchecked was exploitable: a
    negative a sweeps U smoothly downward through the admissible window (a = -2.35 gives U = 3.5494,
    below C7's own certified lower bound on E[tau']), producing a dependency-free, re-derivation-
    surviving, kill-gate-clean bound that is unsound.
    """
    a, s = F(a), F(K) + F(a)
    if a <= 0:
        raise TheoremRefusal(
            f"Lemma C7-U requires a > 0; got a = {a}. For a <= 0 the closed form does not equal "
            f"E[V 1{{V > a}}] and the resulting U is not an upper bound on E[tau'].")
    return (rho1(s - F(e)) + rho1(s + F(e))
            + G.Iv(a, a) * (G.Phi(-(s - F(e))) + G.Phi(-(s + F(e))))).hi


def E_tau_prime_finite(e: F, K: F, H: F, c: F) -> dict:
    """Step 0: certify E[tau'] < infinity via an explicit geometric domination at threshold c."""
    e, K, H, c = F(e), F(K), F(H), F(c)
    s = K + c
    p_lo = (G.Phi(-(s - e)) + G.Phi(-(s + e))).lo          # P(V > c) from BELOW
    if not p_lo > 0:
        raise TheoremRefusal("could not certify P(V > c) > 0")
    n = -((-H) // c) + 1                                    # ceil(H/c) + 1, exact integer arithmetic
    return {"c": c, "p_lower": p_lo, "geometric_stages": int(n),
            "E_tau_prime_upper_crude": (G.Iv(n, n) / G.Iv(p_lo, p_lo)).hi}


def U_elementary(e: F, K: F, H: F, grid) -> dict:
    """Lemma C7-U: min over a prospectively fixed grid. No registry constant, no cited theorem."""
    e, K, H = F(e), F(K), F(H)
    EV = G.E_excess(e, K)
    rows, best = [], None
    for a in grid:
        a = F(a)
        gh = g_tail(a, e, K)
        if gh >= EV.lo:
            rows.append({"a": a, "g_upper": gh, "admissible": False})
            continue
        ER = ((G.Iv(a, a) * G.Iv(EV.hi, EV.hi) + G.Iv(H, H) * G.Iv(gh, gh))
              / G.Iv(EV.lo - gh, EV.lo - gh)).hi
        U = (G.Iv(H + ER, H + ER) / G.Iv(EV.lo, EV.lo)).hi
        rows.append({"a": a, "g_upper": gh, "admissible": True, "E_R_upper": ER, "U_upper": U})
        if best is None or U < best["U_upper"]:
            best = rows[-1]
    if best is None:
        raise TheoremRefusal("no admissible a in the grid: g(a) >= E[V] throughout")
    return {"grid": [str(F(x)) for x in grid], "rows": rows, "best": best,
            "dependency": "NONE beyond C7's own rigorous Gaussian; no registry, no external citation"}


def U_lorden(e: F, K: F, H: F) -> dict:
    """Lorden's inequality E[R] <= E[V^2]/E[V]. NO registry, but an EXTERNAL theorem C7 does not prove."""
    e, K, H = F(e), F(K), F(H)
    EV, EV2 = G.E_excess(e, K), rho2(K - e) + rho2(K + e)
    ER = (G.Iv(EV2.hi, EV2.hi) / G.Iv(EV.lo, EV.lo)).hi
    U = (G.Iv(H + ER, H + ER) / G.Iv(EV.lo, EV.lo)).hi
    return {"E_V2_upper": EV2.hi, "E_R_upper": ER, "U_upper": U,
            "dependency": "Lorden (1970) renewal overshoot inequality -- cited, NOT re-proved in C7"}


# ==================================================================================================
# U PROVENANCE -- a bare number is not admissible as U
# ==================================================================================================
"""Why this exists.

`lambda_lower_tier_k` is monotone DECREASING in U, so understating U inflates the bound in the
unsound direction. Probing the unguarded entry point showed the failure is invisible to every other
check: U = 0.1, which is false by a factor of ~47, yields Lambda_309 >= 4.175, which is well-ordered,
LP-consistent, and still below the certified A0 4.867216117 -- so even the kill gate that compares a
lower bound against a certified upper bound does not fire. It is the same species of hole as C5's
negate-and-swap, which survived every check C5 had because C5 checked self-consistency rather than
provenance.

The repair is structural rather than a note: U must arrive as a certificate produced by
`certified_U`, and `lambda_lower_tier_k` RE-DERIVES the value from the declared source and refuses on
mismatch. A mutated or invented U cannot survive re-derivation, and a source not on the gate's
admitted list is refused outright.
"""

_U_TAG = "C7_CERTIFIED_U/1"
_U_SOURCES = ("elementary", "registry", "lorden")

# The gate freezes a_grid_for_lemma_C7_U = {j/4 : j = 8..24}. It is bound HERE, in code, because a
# frozen value that only exists as prose in the gate binds nothing: _resolve_U previously re-derived
# from the grid carried in the certificate under test, so the provenance check constrained `source`
# -- the field the mutants exercised -- and never the field carrying the payload.
GATE_A_GRID = tuple(F(j, 4) for j in range(8, 25))

# The closed cell for 309, from C4's certificate. Validity of every bound requires e in this cell.
GATE_E_LO, GATE_E_HI = F(19839101, 10000000), F(2092283, 1000000)

# Erratum E3 fixes the finiteness threshold c that Lemma C7-U step 0 uses.
GATE_C_FINITENESS = F(1)


# The frozen CUSUM model. K and H are NOT free parameters: every derivation in this module is tied
# to the alarm rule of the frozen kernel, and KG7 exists because mis-taking the threshold inflates
# the bound in the UNSOUND direction while leaving every other check happy. That gate lived only in
# c7_certificate.py, testing that module's own constants, and in the mutation suite's MIRROR -- so
# the real entry points accepted any K, H at all. Driving lambda_lower_tier_k at H = 11/2 gave
# 3.925355098 and at H = 6 gave 4.250984509, both above the published PRIMARY, both below the
# certified A0 and the family ceiling, so KG5 did not fire either: a +18.5% inflation through the
# public API with no mutation, and a larger one than either exploit the pre-publication review found.
GATE_K, GATE_H = F(1, 2), F(5)


def _require_frozen_model(K: F, H: F) -> None:
    if F(K) != GATE_K or F(H) != GATE_H:
        raise TheoremRefusal(
            f"K = {K}, H = {H} are not the frozen CUSUM model constants K = {GATE_K}, H = {GATE_H} "
            f"(K + H must equal the frozen threshold C_CUSUM = 11/2); every derivation here is tied "
            f"to that kernel's alarm rule")


def _require_in_cell(e: F) -> None:
    """Lambda_309 is a sup over the CLOSED cell, so any point in it gives a valid lower bound -- and
    any point OUTSIDE it gives a number that bounds nothing. e = 1.90 yields 3.642963840, above the
    published PRIMARY, and fires no kill gate. Enforced here rather than trusted to the caller."""
    if not (GATE_E_LO <= F(e) <= GATE_E_HI):
        raise TheoremRefusal(
            f"e = {e} lies outside the closed cell [{GATE_E_LO}, {GATE_E_HI}] for cell 309; a bound "
            f"evaluated there is not a lower bound on Lambda_309")


def certified_U(source: str, e: F, K: F, H: F, a_grid=None) -> dict:
    """Produce a U certificate. `source` must be on the gate's admitted list."""
    if source not in _U_SOURCES:
        raise TheoremRefusal(f"U source {source!r} is not on the gate's admitted list {_U_SOURCES}")
    e, K, H = F(e), F(K), F(H)
    _require_frozen_model(K, H)
    _require_in_cell(e)
    if source == "elementary":
        if a_grid is None:
            raise TheoremRefusal("the elementary source requires the gate's frozen a-grid")
        d = U_elementary(e, K, H, a_grid)
        val, dep = d["best"]["U_upper"], []
        deriv = f"Lemma C7-U at a = {d['best']['a']}"
    elif source == "lorden":
        d = U_lorden(e, K, H)
        val, dep = d["U_upper"], ["Lorden (1970), cited but not re-proved in C7"]
        deriv = "E[R] <= E[V^2]/E[V]"
    else:
        import c7_common as _C                     # local import: c7_common does not import this module
        val = F(str(_C.c4_cell309()["A0_certified_float"]))
        dep = ["Arb/FLINT operator certification surface"]
        deriv = "certified admissible A0 at cell 309 via Lemma SM(d), read from C4_CERTIFICATE.json"
    # Step 0 of Lemma C7-U: certify E[tau'] < infinity. Every tier >= 2 needs it, and step 3 of the
    # lemma divides by E[V] - g(a) after substituting Wald, which is invalid if E[R] = infinity. This
    # was previously proved in a docstring and executed nowhere, so the PRIMARY bound's EMPTY
    # dependency set rested on an unexecuted step. c = 1 is fixed by erratum E3.
    fin = E_tau_prime_finite(e, K, H, GATE_C_FINITENESS)
    if not fin["p_lower"] > 0:
        raise TheoremRefusal("could not certify P(V > c) > 0, so E[tau'] < infinity is not established")

    # An INDEPENDENT floor on E[tau'], so that a U understated by a mutation of the derivation code
    # itself -- which re-derivation cannot catch, since it would re-run the mutated code -- is still
    # refused once it falls below a value E[tau'] provably exceeds. E[tau'] = (H + E[R])/E[V] >= H/E[V]
    # because R >= 0; this is exactly C4's own bound applied to tau' rather than tau.
    floor = (G.Iv(H, H) / G.Iv(G.E_excess(e, K).hi, G.E_excess(e, K).hi)).lo
    if val < floor:
        raise TheoremRefusal(
            f"U = {val} from source {source!r} is below the certified floor H/E[V] = {floor} on "
            f"E[tau'], so it is provably not an upper bound")
    return {"_tag": _U_TAG, "source": source, "value": val, "dependencies": dep,
            "derivation": deriv, "E_tau_prime_floor": floor,
            "finiteness": {"c": str(fin["c"]), "p_lower": str(fin["p_lower"]),
                           "geometric_stages": fin["geometric_stages"],
                           "E_tau_prime_upper_crude": str(fin["E_tau_prime_upper_crude"])},
            "a_grid": [str(F(x)) for x in a_grid] if a_grid else None}


def _resolve_U(U_cert, e: F, K: F, H: F) -> tuple:
    """Refuse anything that is not a certificate, and re-derive it from its declared source."""
    if not isinstance(U_cert, dict) or U_cert.get("_tag") != _U_TAG:
        raise TheoremRefusal(
            "U must be a certificate from certified_U(), not a bare value. Understating U inflates "
            "the bound in the unsound direction and is invisible to every self-consistency check.")
    # Re-derive from the GATE's frozen grid, never from the grid the presented certificate carries.
    presented = tuple(F(x) for x in U_cert["a_grid"]) if U_cert.get("a_grid") else None
    if U_cert["source"] == "elementary":
        if presented != GATE_A_GRID:
            raise TheoremRefusal(
                f"presented a_grid does not match the gate's frozen grid; presented "
                f"{[str(x) for x in (presented or ())][:4]}..., frozen "
                f"{[str(x) for x in GATE_A_GRID][:4]}...")
    elif presented is not None:
        raise TheoremRefusal(f"source {U_cert['source']!r} must not carry an a_grid")
    fresh = certified_U(U_cert["source"], e, K, H, GATE_A_GRID if presented else None)
    if fresh["value"] != U_cert["value"]:
        raise TheoremRefusal(
            f"U certificate does not survive re-derivation from source {U_cert['source']!r}: "
            f"presented {U_cert['value']}, re-derived {fresh['value']}")
    return fresh["value"], fresh["dependencies"]


def psi_exact(u: F, e: F, K: F) -> G.Iv:
    """psi(u) itself, as a rigorous interval -- not a bound on it.

    psi(u) = [rho(s-e) + rho(s+e)] / [Phi(-(s-e)) + Phi(-(s+e))],  s = K + u,
    which is the exact mean residual life of V = (|z|-K)^+ at u. This is used as an INDEPENDENT
    admissibility check on the psi_lo values the LP consumes: whatever lower bound is assigned to the
    subinterval ending at u_j must not exceed psi's true value there, since the assigned value has to
    lower-bound psi on the WHOLE subinterval and u_j belongs to it.

    This is what detects an endpoint error. psi_lo is built from r and f at one endpoint; if the wrong
    endpoint is used the LP still runs, the weights still sum to 1, psi_lo is still non-increasing, and
    the bound still lands below every certified upper bound -- it is simply wrong, by ~1%. No
    self-consistency check reaches it, because nothing in the computation is inconsistent. Only an
    independent recomputation of the quantity being bounded does.
    """
    u, s = F(u), F(K) + F(u)
    e = F(e)
    num = rho1(s - e) + rho1(s + e)
    den = G.Phi(-(s - e)) + G.Phi(-(s + e))
    return num / den
