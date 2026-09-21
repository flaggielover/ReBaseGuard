"""Theorem C5-T: an exact-weight, sign-aware transport for the frozen K5-B direct clause.

THE FROZEN CLAUSE. On a K1 cell [e0 - rho, e0 + rho] the K5-B direct test certifies g(e) < 0 uniformly on the
cell, where g(e) := R(e) - e R'(e) and therefore g'(e) = -e R''(e). It does so as

    Gamma := g_hi + rho * x_hi * M  <  0,        g_hi := R.hi - e0 * D.lo,   M := a whole-cell bound on |R''|,

i.e. it transports the midpoint enclosure to the cell edge using |g'| <= x_hi * M.

WHAT IS LOOSE. The transport integrates |g'(t)| = |t| |R''(t)| over an interval of length rho, but bounds |t| by
x_hi over the WHOLE range, although |t| <= x_hi only at the right-hand endpoint. The exact integral of |t| is
smaller, and the two directions of travel weight the two ENDS of the R'' enclosure differently.

THEOREM C5-T. Let 0 < x_lo = e0 - rho, x_hi = e0 + rho. Suppose
    (i)  g(e0) <= g_hi                                      (certified at the midpoint), and
    (ii) H_lo <= R''(e) <= H_hi for every e in the cell      (certified on the whole cell).
Then for every e in the cell

    g(e)  <=  g_hi + P,      P := max( (-H_lo)^+ * w_R ,  (H_hi)^+ * w_L ),
    w_R := rho * (x_hi - rho/2),     w_L := rho * (x_lo + rho/2).

*Proof.* g is absolutely continuous with g'(t) = -t R''(t). For e >= e0,

    g(e) - g(e0) = -int_{e0}^{e} t R''(t) dt <= int_{e0}^{e} t (-R''(t))^+ dt <= (-H_lo)^+ int_{e0}^{e0+rho} t dt,

using t > 0 on the cell, which is where x_lo > 0 is needed. The last integral is ((e0+rho)^2 - e0^2)/2 =
rho*(e0 + rho/2) = rho*(x_hi - rho/2) = w_R. For e <= e0,

    g(e) - g(e0) = int_{e}^{e0} t R''(t) dt <= (H_hi)^+ int_{e0-rho}^{e0} t dt = (H_hi)^+ * rho*(e0 - rho/2),

and e0 - rho/2 = x_lo + rho/2, so that integral is w_L. Taking the larger of the two gives P. QED

C5-T IS NEVER WORSE THAN THE FROZEN CLAUSE, AND IS USUALLY STRICTLY BETTER. With M = max(|H_lo|, |H_hi|),

    P <= M * max(w_R, w_L) = M * w_R = M * rho * (x_hi - rho/2)  <  M * rho * x_hi,

because rho > 0. The improvement factor on the penalty is at least (x_hi - rho/2)/x_hi. The sign-aware part adds
a further strict gain exactly when the POSITIVE end of the R'' enclosure dominates in magnitude; on the K5 tail
cells the negative end dominates, so there the gain is the exact-weight factor alone.

WHAT IT DOES NOT DO. C5-T changes only the transport. It leaves g_hi, the enclosure of R'', the atom constants and
every measurement input exactly as certified. It is a zero-new-real, exact-rational refinement of one inequality.
"""
from fractions import Fraction as F


class TransportRefusal(Exception):
    pass


def weights(e0: F, rho: F) -> tuple:
    """(w_R, w_L, x_lo, x_hi). Refuses a cell that does not lie strictly in e > 0, where the proof needs t > 0."""
    e0, rho = F(e0), F(rho)
    if rho <= 0:
        raise TransportRefusal("rho must be positive")
    x_lo, x_hi = e0 - rho, e0 + rho
    if x_lo <= 0:
        raise TransportRefusal("theorem C5-T needs the whole cell in e > 0 (it integrates t, not |t|)")
    return rho * (x_hi - rho / 2), rho * (x_lo + rho / 2), x_lo, x_hi


def penalty(H_lo: F, H_hi: F, e0: F, rho: F) -> dict:
    """The C5-T penalty P, beside the frozen clause's rho * x_hi * M, on the same certified enclosure."""
    H_lo, H_hi = F(H_lo), F(H_hi)
    if H_lo > H_hi:
        raise TransportRefusal("inverted R'' enclosure")
    w_R, w_L, x_lo, x_hi = weights(e0, rho)
    M = max(abs(H_lo), abs(H_hi))
    right = max(-H_lo, F(0)) * w_R
    left = max(H_hi, F(0)) * w_L
    P = max(right, left)
    frozen = F(rho) * x_hi * M
    if P > frozen:
        raise TransportRefusal("C5-T exceeded the frozen penalty, which is impossible")
    return {"P": P, "frozen_penalty": frozen, "w_R": w_R, "w_L": w_L, "M": M,
            "binding_direction": "rightward" if right >= left else "leftward",
            "improvement_factor": P / frozen if frozen else None}


def gamma(g_hi: F, H_lo: F, H_hi: F, e0: F, rho: F) -> dict:
    """The refined direct clause. Closure is Gamma < 0, exactly as in the frozen consumer."""
    p = penalty(H_lo, H_hi, e0, rho)
    G = F(g_hi) + p["P"]
    return {**p, "g_hi": F(g_hi), "Gamma": G, "pass": G < 0,
            "Gamma_frozen": F(g_hi) + p["frozen_penalty"]}
