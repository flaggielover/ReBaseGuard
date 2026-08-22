"""Lemma L2 — uniform killing bound for the frozen CUSUM at drift -e.

From ANY live state (p,m) with p,m >= 0, the recursion
    S+_t = max(0, S+_{t-1} + z_t - k) >= S+_{t-1} + z_t - k
gives, by induction, S+_n >= p + G_n - nk >= G_n - nk with G_n = sum_{t<=n} z_t,
and symmetrically S-_n >= m - G_n - nk >= -G_n - nk.  Hence

    |G_n| >= h + nk   ==>   max(S+_n, S-_n) >= h   ==>   tau <= n .

Under reference error e the innovations are z_t ~ iid N(-e, 1), so G_n ~
N(-ne, n) and

    q_n(e) := P(|G_n| >= h + nk) = 1 - Phi((h+nk+ne)/sqrt(n))
                                     + Phi((ne-h-nk)/sqrt(n))

is a lower bound, UNIFORM over live states, for P_s(tau <= n).  Therefore
P_s(tau > jn) <= (1-q_n)^j, and

    sup_s E_s[tau] <= n / q_n ,      ||(I - K_e)^{-1}||_inf <= n / q_n .

This is a continuum statement: no grid, no quadrature, no truncation.  It is
the same argument the frozen Level 1-3 certificate uses
(`rebaseguard_certify.contraction.certify_block_contraction`), evaluated here
at drift -e instead of at e = 0.
"""

from __future__ import annotations

from typing import Any


def killing_bound(e_lo: float, e_hi: float, n: int, *, h: float = 5.0,
                  k: float = 0.5, bits: int = 128) -> dict[str, Any]:
    """Rigorous lower bound on q_n and upper bound on n/q_n, for e in [e_lo,e_hi]."""
    from flint import arb, ctx

    old = ctx.prec
    ctx.prec = bits
    try:
        def Phi(x):
            return (1 + (x / arb(2).sqrt()).erf()) / 2

        H = arb(h) + arb(n) * arb(k)
        rn = arb(n).sqrt()
        # upper tail is decreasing in e -> worst case at e_hi
        upper_tail = 1 - Phi((H + arb(n) * arb(e_hi)) / rn)
        # lower tail is increasing in e -> worst case at e_lo
        lower_tail = Phi((arb(n) * arb(e_lo) - H) / rn)
        q = upper_tail + lower_tail
        q_low = float((q - q.rad()).mid())
        if not q_low > 0.0:
            raise ArithmeticError("failed to prove q_n > 0")
        bound = n / q_low
        return {
            "n": n, "e_lo": e_lo, "e_hi": e_hi, "h": h, "k": k,
            "precision_bits": bits,
            "q_n_lower": q_low,
            "arl_upper_bound": bound,
            "resolvent_upper_bound": bound,
            "statement": "P_s(tau <= n) >= q_n for every live s; "
                         "sup_s E_s[tau] <= n/q_n",
            "scope": "entire live continuum; no discretization involved",
        }
    finally:
        ctx.prec = old


def best_killing_bound(e_lo: float, e_hi: float, *, h: float = 5.0,
                       k: float = 0.5, n_max: int = 60,
                       bits: int = 128) -> dict[str, Any]:
    """Scan n and keep the tightest bound.  Every candidate n is itself valid."""
    best = None
    scan = []
    for n in range(1, n_max + 1):
        try:
            rec = killing_bound(e_lo, e_hi, n, h=h, k=k, bits=bits)
        except ArithmeticError:
            continue
        scan.append({"n": n, "q_n_lower": rec["q_n_lower"],
                     "arl_upper_bound": rec["arl_upper_bound"]})
        if best is None or rec["arl_upper_bound"] < best["arl_upper_bound"]:
            best = rec
    if best is None:
        raise ArithmeticError("no n gave a positive killing probability")
    best["scan"] = scan
    return best
