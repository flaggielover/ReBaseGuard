"""C11R Phase 3/4 -- block-uniform drift, and the atom-removed kernel Khat_e.

INDEPENDENCE. This module imports nothing from the original certifier's load-bearing graph
(taboo_certify, resolvent_certificate, opnorms, ra_certifier, fast_range, intervals,
rebaseguard_certify, rung3_engine, spec). It builds on C11's own certifier and on C7's rational
Gaussian primitives, both of which are this programme's independent line, not the original's.

WHY NOT A GRID. The campaign forbids certifying only endpoints, the midpoint, or a finite drift
grid unless a theorem proves those checks bound the whole interval. This module does not check
drift samples at all. It carries the drift as an INTERVAL through every step, so a single
evaluation encloses the quantity SIMULTANEOUSLY for every e in the block. The only facts needed are
elementary and are proved here rather than assumed:

  (i)  Phi is strictly increasing, so Phi([x, y]) is contained in [Phi(x).lo, Phi(y).hi];
  (ii) phi is unimodal with its maximum at 0 and is even, so on [x, y] its supremum is phi(0) when
       0 lies in [x, y] and max(phi(x), phi(y)) otherwise, and its infimum is
       min(phi(x), phi(y));
  (iii) a monomial u^n over an interval attains its extrema at the endpoints, except that for even
       n the infimum is 0 when the interval straddles 0.

The alarm-free window [m - C, C - p] does NOT depend on e; only the density's shift does. So the
drift enters exactly through A = a + E and B = b + E in the moment arguments and through the
binomial coefficients (-E)^(j-i). Nothing else has to be re-derived.

SCALAR COLLAPSE. With E = [e, e] every function here must reproduce C11's scalar implementation
bit for bit. That is checked, not asserted -- it is the strongest available evidence that the
interval extension did not silently change the mathematics.
"""
from __future__ import annotations

import pathlib
import sys
from fractions import Fraction as F
from math import comb

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import c11r_common as C

sys.path.insert(0, str(C.C11 / "code"))
sys.path.insert(0, str(C.C7 / "code"))
import c11_certifier as X            # noqa: E402  C11's own second certifier (scalar drift)
import c7_gaussian as G              # noqa: E402  rational Phi/phi; imports only `fractions`

K = X.K                              # 1/2   -- taken from C11, which read them from the frozen model
H = X.H                              # 5
CC = X.CC                            # 11/2
ATOM = X.ATOM


class Refusal(Exception):
    pass


class Blk:
    """A drift block, carried as EXACT rationals with no outward rounding.

    This is deliberately NOT a c7_gaussian.Iv. An Iv rounds every endpoint onto the 2^-320 grid,
    which turns the registry's own drift bounds -- 680769/400000, a 19-bit denominator -- into
    320-bit rationals. Every downstream Phi/phi series then works on 320-bit inputs, and a single
    Phi evaluation goes from 0.083 s to 2.708 s: a 33x slowdown, for a value that was already
    exact and needed no rounding at all. Carrying the block exactly is both faster and TIGHTER,
    since no rounding is introduced where none is required.
    """
    __slots__ = ("lo", "hi")

    def __init__(self, lo, hi=None):
        self.lo = F(lo)
        self.hi = self.lo if hi is None else F(hi)
        if self.lo > self.hi:
            raise Refusal("inverted drift block")

    def is_point(self) -> bool:
        return self.lo == self.hi

    def width(self) -> F:
        return self.hi - self.lo

    def __repr__(self):
        return f"Blk[{float(self.lo):.7f}, {float(self.hi):.7f}]"


# ---------------------------------------------------------------------------------------------
# interval-argument Gaussian primitives
# ---------------------------------------------------------------------------------------------
def Phi_iv(A: Blk) -> G.Iv:
    """Phi over an interval argument. Phi is increasing, so the endpoints give the enclosure."""
    return G.Iv(G.Phi(A.lo).lo, G.Phi(A.hi).hi)


def phi_iv(A: Blk) -> G.Iv:
    """phi over an interval argument. phi is even and unimodal with its peak at 0."""
    return _phi_pair(A.lo, A.hi)


def ipow(A: Blk, n: int) -> G.Iv:
    """A monomial over an interval. Extrema at the endpoints, except even n straddling 0."""
    lo, hi = _monomial_pair(A.lo, A.hi, n)
    return G.Iv(lo, hi)


def moments_iv(A: Blk, B: Blk, jmax: int) -> list[G.Iv]:
    """M_j over interval limits. Thin wrapper over the exact-endpoint form."""
    return _moments_pair(A.lo, A.hi, B.lo, B.hi, jmax)


def _moments_pair(a_lo: F, a_hi: F, b_lo: F, b_hi: F, jmax: int) -> list[G.Iv]:
    """M_j = int_A^B u^j phi(u) du for every A in [a_lo, a_hi] and B in [b_lo, b_hi].

    The limits are carried as EXACT rational pairs rather than as pre-rounded intervals. That
    matters: every Iv constructor rounds outward onto the 2^-SCALE grid, so an intermediate Iv
    costs an ulp of width. Keeping the endpoints exact until the last moment is what makes the
    degenerate case a_lo == a_hi reproduce the scalar implementation EXACTLY rather than merely
    enclose it.
    """
    if b_hi < a_lo:
        raise Refusal("moment interval is inverted")
    phiA = _phi_pair(a_lo, a_hi)
    phiB = _phi_pair(b_lo, b_hi)
    out = [G.Iv(G.Phi(b_lo).lo, G.Phi(b_hi).hi) - G.Iv(G.Phi(a_lo).lo, G.Phi(a_hi).hi)]
    # C11 erratum E5, carried forward: M_0 is a probability mass, so an enclosure that is not a
    # usable subset of [0, 1] is vacuous and must refuse rather than propagate.
    m0 = out[0]
    if m0.hi - m0.lo > F(1) or m0.hi < 0 or m0.lo > 1:
        raise Refusal(f"vacuous Gaussian enclosure on [{float(a_lo):.4g}, {float(b_hi):.4g}]: "
                      f"M_0 = [{float(m0.lo):.3e}, {float(m0.hi):.3e}]")
    if jmax >= 1:
        out.append(phiA - phiB)
    for j in range(2, jmax + 1):
        pa_lo, pa_hi = _monomial_pair(a_lo, a_hi, j - 1)
        pb_lo, pb_hi = _monomial_pair(b_lo, b_hi, j - 1)
        out.append(G.Iv(j - 1, j - 1) * out[j - 2]
                   + G.Iv(pa_lo, pa_hi) * phiA - G.Iv(pb_lo, pb_hi) * phiB)
    return out


def _phi_pair(x_lo: F, x_hi: F) -> G.Iv:
    """phi over [x_lo, x_hi]. phi is even and unimodal with its peak at 0."""
    if x_lo == x_hi:
        return G.phi(x_lo)
    lo_end, hi_end = G.phi(x_lo), G.phi(x_hi)
    lo = lo_end.lo if lo_end.lo < hi_end.lo else hi_end.lo
    if x_lo <= 0 <= x_hi:
        hi = G.phi(F(0)).hi
    else:
        hi = lo_end.hi if lo_end.hi > hi_end.hi else hi_end.hi
    return G.Iv(lo, hi)


def _monomial_pair(x_lo: F, x_hi: F, n: int) -> tuple[F, F]:
    """Exact rational enclosure of u^n over [x_lo, x_hi]; extrema at the endpoints."""
    if n == 0:
        return F(1), F(1)
    a, b = x_lo ** n, x_hi ** n
    lo, hi = (a, b) if a <= b else (b, a)
    if n % 2 == 0 and x_lo <= 0 <= x_hi:
        lo = F(0)
    return lo, hi


def shifted_moments_iv(a: F, b: F, E: Blk, jmax: int) -> list[G.Iv]:
    """int_a^b z^j phi(z + e) dz, simultaneously for every e in E.

    The window [a, b] is drift-independent; substituting u = z + e moves the drift into the
    integration limits and into the binomial expansion of (u - e)^j. Limits and coefficients are
    kept as exact rationals so that a degenerate E collapses onto the scalar implementation.
    """
    Ms = _moments_pair(a + E.lo, a + E.hi, b + E.lo, b + E.hi, jmax)
    nlo, nhi = -E.hi, -E.lo                    # -E, exactly; both endpoints already on the grid
    out = [Ms[0]]                              # j = 0: the coefficient is exactly 1, so no product
    for j in range(1, jmax + 1):
        acc = G.Iv(0, 0)
        for i in range(j + 1):
            c = comb(j, i)
            plo, phi_ = _monomial_pair(nlo, nhi, j - i)
            acc = acc + G.Iv(c * plo, c * phi_) * Ms[i]
        out.append(acc)
    return out


# ---------------------------------------------------------------------------------------------
# the kernels, with the atom split recovered rather than assumed
# ---------------------------------------------------------------------------------------------
def _pieces(p: F, m: F):
    """The alarm-free window split at its kinks, plus the atom sub-window.

    The atom piece is the z-range on which BOTH arms clamp to zero:
        p + z - K <= 0  and  m - z - K <= 0   <=>   m - K <= z <= K - p,
    which is non-empty exactly when p + m < 2K. That is the origin/atom window the original
    certifier removes to form Khat_e.
    """
    lo, hi = m - CC, CC - p
    beta, alpha = m - K, K - p
    atom_lo, atom_hi = max(lo, beta), min(hi, alpha)
    has_atom = beta < alpha and atom_lo < atom_hi
    cuts = sorted({lo, hi} | {c for c in (alpha, beta) if lo < c < hi})
    return lo, hi, cuts, (atom_lo, atom_hi) if has_atom else None


def _piece_integral(w: dict, p: F, m: F, z0: F, z1: F, E: Blk) -> G.Iv:
    """Integral of w(p', m') phi(z + e) over one smooth piece, for every e in E.

    Coefficients are collected by z-DEGREE as exact rationals first, so each degree costs exactly
    one interval multiplication. An earlier draft multiplied term by term, which was mathematically
    the same but paid an outward rounding per term; that alone broke bit-equality with C11's scalar
    path on every weight of degree >= 1, and made the enclosure needlessly wider.
    """
    if z1 <= z0:
        return G.Iv(0, 0)
    mid = (z0 + z1) / 2
    pz_pos = (p + mid - K) > 0
    mz_pos = (m - mid - K) > 0
    zc: dict[int, F] = {}
    for (i, j), c in w.items():
        if (i and not pz_pos) or (j and not mz_pos):
            continue                      # that arm is clamped to 0 on this piece
        cp = X._pow_lin(p - K, F(1), i) if i else [F(1)]
        cm = X._pow_lin(m - K, F(-1), j) if j else [F(1)]
        for u, cu in enumerate(cp):
            if cu == 0:
                continue
            for v, cv in enumerate(cm):
                if cv == 0:
                    continue
                zc[u + v] = zc.get(u + v, F(0)) + c * cu * cv
    if not zc:
        return G.Iv(0, 0)
    Ms = shifted_moments_iv(z0, z1, E, max(zc))
    acc = G.Iv(0, 0)
    for d, c in zc.items():
        acc = acc + G.Iv(c, c) * Ms[d]
    return acc


def kernel_apply_iv(w: dict, p: F, m: F, E: Blk, *, atom_removed: bool = False) -> G.Iv:
    """(K_e w)(p, m), or (Khat_e w)(p, m) when atom_removed, for every e in E."""
    lo, hi, cuts, atom = _pieces(p, m)
    if hi <= lo:
        return G.Iv(0, 0)
    acc = G.Iv(0, 0)
    for z0, z1 in zip(cuts[:-1], cuts[1:]):
        if atom_removed and atom is not None and z0 >= atom[0] and z1 <= atom[1]:
            continue                      # this is the atom piece: removed to form Khat_e
        acc = acc + _piece_integral(w, p, m, z0, z1, E)
    return acc


def atom_contribution_iv(w: dict, p: F, m: F, E: Blk) -> G.Iv:
    """The removed piece on its own: (K_e - Khat_e) w at (p, m).

    On the atom window both arms clamp to zero, so w(p', m') = w(0, 0) is CONSTANT there and the
    integral is w(atom) times the Gaussian mass of the window. The sign and normalisation are not
    assumed -- this is derived from the same _pieces split the kernels use, and the decomposition
    K_e = Khat_e + atom is checked numerically in the validation suite.
    """
    lo, hi, cuts, atom = _pieces(p, m)
    if hi <= lo or atom is None:
        return G.Iv(0, 0)
    wa = X.poly_eval_iv(w, G.Iv(0, 0), G.Iv(0, 0))
    mass = shifted_moments_iv(atom[0], atom[1], E, 0)[0]
    return wa * mass


def alarm_prob_iv(p: F, m: F, E: Blk) -> G.Iv:
    """h_1(p, m) = 1 - (K_e 1)(p, m), the one-step alarm probability, for every e in E."""
    lo, hi = m - CC, CC - p
    if hi <= lo:
        return G.Iv(1, 1)
    mass = _moments_pair(lo + E.lo, lo + E.hi, hi + E.lo, hi + E.hi, 0)[0]
    return G.Iv(1, 1) - mass


# ---------------------------------------------------------------------------------------------
# uniform bound over a box of states, uniform in e
# ---------------------------------------------------------------------------------------------
def kernel_box_upper_iv(w: dict, a: F, b: F, c: F, d: F, E: Blk, panels: int = 16, *,
                        atom_removed: bool = False) -> G.Iv:
    """Rigorous upper bound on (K_e w)(p, m) for every state in [a,b] x [c,d] and every e in E.

    THE PARTITION IS IN u = z + e, NOT IN z. This is the difference between a bound that tightens
    with panels and one that diverges. Partitioning in z makes each panel's Gaussian mass an
    interval Phi([z1+e_lo, z1+e_hi]) - Phi([z0+e_lo, z0+e_hi]), whose upper end covers a window
    widened by the WHOLE block width at both ends. Summing n such panels pays that width n times,
    so the bound grows linearly in the panel count: measured 11.49 at 8 panels, 11.81 at 16, 12.87
    at 32, diverging exactly as predicted.

    In u the panel endpoints are drift-independent, so each panel's mass is Phi(u1) - Phi(u0) with
    POINT arguments and no interval widening at all. The drift uncertainty moves instead into the
    image state, where z = u - e ranges over [u0 - e_hi, u1 - e_lo] -- a width-W interval in the
    argument of w, costing roughly |w'| * W once, rather than inflating probability mass n times.

    The u-range [lo_z + e_lo, hi_z + e_hi] covers the window for every e in the block, so it
    over-counts mass by O(W) at the two ends -- once, not once per panel. With w >= 0 enforced
    separately, extra mass can only raise the bound, so it remains an upper bound.
    """
    lo_z, hi_z = c - CC, CC - a
    if hi_z <= lo_z:
        return G.Iv(0, 0)
    u0_all, u1_all = lo_z + E.lo, hi_z + E.hi
    step = (u1_all - u0_all) / panels
    acc = G.Iv(0, 0)
    for k in range(panels):
        u0, u1 = u0_all + step * k, u0_all + step * (k + 1)
        z_lo, z_hi = u0 - E.hi, u1 - E.lo          # the z-range this u-panel can correspond to
        if atom_removed:
            at_lo, at_hi = d - K, K - b            # atom window, intersected over the state box
            if at_lo < at_hi and z_lo >= at_lo and z_hi <= at_hi:
                continue
        p_lo = max(F(0), a + z_lo - K)
        p_hi = max(F(0), b + z_hi - K)
        m_lo = max(F(0), c - z_hi - K)
        m_hi = max(F(0), d - z_lo - K)
        wv = X.poly_eval_iv(w, G.Iv(p_lo, p_hi), G.Iv(m_lo, m_hi))
        mass = _moments_pair(u0, u0, u1, u1, 0)[0]   # POINT arguments: exact, no widening
        hi = wv.hi if wv.hi > 0 else F(0)
        acc = acc + G.Iv(0, hi) * G.Iv(0, mass.hi if mass.hi > 0 else F(0))
    return acc


def supersolution_margin_iv(w: dict, E: Blk, depth: int = 4, panels: int = 16, *,
                            atom_removed: bool = False):
    """Lower bound of L = w - 1 - K w over R, uniformly in e over the whole block E."""
    boxes = X.cover(depth)
    mn_L, mn_w = None, None
    for (a, b, c, d) in boxes:
        wv = X.poly_eval_iv(w, G.Iv(a, b), G.Iv(c, d))
        kv = kernel_box_upper_iv(w, a, b, c, d, E, panels, atom_removed=atom_removed)
        L_lo = wv.lo - F(1) - kv.hi
        mn_L = L_lo if mn_L is None or L_lo < mn_L else mn_L
        mn_w = wv.lo if mn_w is None or wv.lo < mn_w else mn_w
    return {"margin_lower_bound": mn_L, "w_min_lower_bound": mn_w, "boxes": len(boxes),
            "kernel": "Khat_e" if atom_removed else "K_e",
            "certified": bool(mn_L is not None and mn_L > 0 and mn_w >= 0)}


def pointwise_refute_iv(w: dict, E: Blk, n: int = 15, *, atom_removed: bool = False) -> dict:
    """Cheap necessary-condition screen: a rigorous UPPER bound on min_R L, uniform in e.

    Negative anywhere on R means no certificate exists at any subdivision depth, for this w over
    this drift block. Mandatory before any expensive certification run (C11 erratum E9).
    """
    ax = [F(5 * i, n - 1) for i in range(n)]
    states = [(p, m) for p in ax for m in ax if (p + m <= 4) or p == 0 or m == 0]
    worst, arg = None, None
    for p, m in states:
        L = (X.poly_eval_iv(w, G.Iv(p, p), G.Iv(m, m)) - G.Iv(1, 1)
             - kernel_apply_iv(w, p, m, E, atom_removed=atom_removed))
        if worst is None or L.hi < worst:
            worst, arg = L.hi, (str(p), str(m))
    return {"grid": f"{n}x{n} on R", "states": len(states),
            "kernel": "Khat_e" if atom_removed else "K_e",
            "min_L_upper_bound": float(worst), "binding_state": arg,
            "POINTWISE_REFUTED": bool(worst < 0)}
