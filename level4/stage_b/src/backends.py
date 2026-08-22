"""Numeric backends returning OUTWARD-rounded enclosures.

`FloatBackend` uses SciPy and is for *sizing experiments only* — it is fast but
its enclosures are not certified, because SciPy's `ndtr` carries no proven
error bound.  `ArbBackend` uses python-flint / Arb ball arithmetic and is the
one the certificate is allowed to rest on.  Both implement the same interface
and share `transitions.py`'s partition logic, so the sizing run and the
certified run cut the z-axis in exactly the same places.
"""

from __future__ import annotations

import numpy as np

SQRT2PI = float(np.sqrt(2.0 * np.pi))

# sup |phi''| = |phi''(0)| = phi(0) = 0.39894...; 0.4 is a safe over-estimate.
PHI_SECOND_SUP = 0.4


def _taylor_mass(m0_lo, m0_hi, d1_lo, d1_hi, a, b, w):
    """Enclose the segment mass over e in [c-w, c+w] WITHOUT losing telescoping.

    The naive enclosure  Phi(b+e_hi) - Phi(a+e_lo)  over-counts by about
    phi * (e_hi - e_lo) on EVERY segment, and a source cell carries ~10^3
    segments, so the total continuation mass bound blows past 1 and the upper
    operator stops being a contraction.  Expanding in e instead,

        mass(e) = mass(c) + (e-c)(phi(b+c) - phi(a+c)) + (e-c)^2/2 * mass''(xi),

    the first-order coefficients sum to the total variation of phi (= 2 phi(0)
    ~ 0.8) rather than to phi summed over every breakpoint, and the remainder
    is bounded via |phi'(b+e) - phi'(a+e)| <= (b-a) sup|phi''|.
    """
    d1_abs = np.maximum(np.abs(d1_lo), np.abs(d1_hi))
    rem = 0.5 * w * w * (b - a) * PHI_SECOND_SUP
    lo = np.maximum(m0_lo - w * d1_abs - rem, 0.0)
    hi = np.maximum(m0_hi + w * d1_abs + rem, 0.0)
    return lo, hi



def _phi(x: np.ndarray) -> np.ndarray:
    return np.exp(-0.5 * x * x) / SQRT2PI


def _phi_interval(x_lo: np.ndarray, x_hi: np.ndarray):
    """Enclose phi over [x_lo, x_hi].  phi is unimodal with its peak at 0."""
    f_lo, f_hi = _phi(x_lo), _phi(x_hi)
    lo = np.minimum(f_lo, f_hi)
    hi = np.maximum(f_lo, f_hi)
    straddles = (x_lo < 0.0) & (x_hi > 0.0)
    hi = np.where(straddles, 1.0 / SQRT2PI, hi)
    return lo, hi


class FloatBackend:
    """SciPy backend. NOT certified; used to size grids before the Arb run."""

    name = "float-scipy"
    certified = False

    def __init__(self) -> None:
        from scipy.special import ndtr
        self._ndtr = ndtr

    def segment_integrals(self, a, b, e_lo, e_hi):
        c, w = 0.5 * (e_lo + e_hi), 0.5 * (e_hi - e_lo)
        m0 = self._ndtr(b + c) - self._ndtr(a + c)
        d1 = _phi(b + c) - _phi(a + c)
        mass_lo, mass_hi = _taylor_mass(m0, m0, d1, d1, a, b, w)
        # z-moments are only consumed on the two outer alarm tails, which are
        # single segments per cell, so the naive enclosure is harmless there.
        pa_lo, pa_hi = _phi_interval(a + e_lo, a + e_hi)
        pb_lo, pb_hi = _phi_interval(b + e_lo, b + e_hi)
        zmom_lo = (pa_lo - pb_hi) - e_hi * mass_hi
        zmom_hi = (pa_hi - pb_lo) - e_lo * mass_lo
        return mass_lo, mass_hi, zmom_lo, zmom_hi

    def tail_moment(self, lo_edge, hi_edge, e_lo, e_hi):
        """Exact closed-form z-moment of (-inf, lo_edge] u [hi_edge, +inf)."""
        outs = []
        for e in (e_lo, e_hi):
            low = -_phi(lo_edge + e) - e * self._ndtr(lo_edge + e)
            high = _phi(hi_edge + e) - e * (1.0 - self._ndtr(hi_edge + e))
            outs.append(low + high)
        return np.minimum(outs[0], outs[1]), np.maximum(outs[0], outs[1])


    def derivative_integrals(self, a, b, e_lo, e_hi):
        """Weights for the differentiated operator (Lemma L6).

        d/de of the segment mass is  w = phi(b+e) - phi(a+e),
        d/de of the segment z-moment is  dr = b*phi(b+e) - a*phi(a+e) - mass,
        and J2 = int |z+e| phi(z+e) dz bounds the mixed-segment contribution.
        """
        pa_lo, pa_hi = _phi_interval(a + e_lo, a + e_hi)
        pb_lo, pb_hi = _phi_interval(b + e_lo, b + e_hi)
        dw_lo = pb_lo - pa_hi
        dw_hi = pb_hi - pa_lo
        mass_lo, mass_hi, _, _ = self.segment_integrals(a, b, e_lo, e_hi)
        bp_lo = np.minimum(b * pb_lo, b * pb_hi)
        bp_hi = np.maximum(b * pb_lo, b * pb_hi)
        ap_lo = np.minimum(a * pa_lo, a * pa_hi)
        ap_hi = np.maximum(a * pa_lo, a * pa_hi)
        dr_lo = bp_lo - ap_hi - mass_hi
        dr_hi = bp_hi - ap_lo - mass_lo
        j2 = _abs_moment_bound(a, b, e_lo, e_hi)
        return dw_lo, dw_hi, dr_lo, dr_hi, j2


    def tail_derivative(self, lo_edge, hi_edge, e_lo, e_hi):
        """d/de of the outer-tail alarm reward.

        d/de int_{-inf}^{A} z phi(z+e) dz = A phi(A+e) - Phi(A+e)
        d/de int_{B}^{inf}  z phi(z+e) dz = -B phi(B+e) - (1 - Phi(B+e))
        """
        outs = []
        for e in (e_lo, e_hi):
            A, B = lo_edge + e, hi_edge + e
            low = lo_edge * _phi(A) - self._ndtr(A)
            high = -hi_edge * _phi(B) - (1.0 - self._ndtr(B))
            outs.append(low + high)
        return np.minimum(outs[0], outs[1]), np.maximum(outs[0], outs[1])
    def tail_integrals(self, z_cut, e_lo, e_hi):
        lows, highs = [], []
        for e in (e_lo, e_hi):
            lower = -_phi(e - z_cut) - e * self._ndtr(e - z_cut)
            upper = _phi(z_cut + e) - e * (1.0 - self._ndtr(z_cut + e))
            lows.append(lower + upper)
            highs.append(lower + upper)
        return min(lows) - 1e-30, max(highs) + 1e-30


class ArbBackend:
    """python-flint / Arb ball arithmetic.  Every result is a proven enclosure.

    All Gaussian evaluations are done on the *unique* segment endpoints and then
    scattered back, because the same breakpoint recurs across many source cells
    (a breakpoint is `level + k - p`, and both `level` and `p` run over grid
    edges).  This is a pure speed device: identical inputs, identical outputs.
    """

    name = "python-flint/Arb"
    certified = True

    def __init__(self, bits: int = 96) -> None:
        from flint import arb, ctx
        self.arb = arb
        self.ctx = ctx
        self.bits = bits

    def _Phi(self, x):
        return (1 + (x / self.arb(2).sqrt()).erf()) / 2

    def _phi(self, x):
        return (-(x * x) / 2).exp() / (2 * self.arb.pi()).sqrt()

    def _tables(self, xs: np.ndarray, e_lo: float, e_hi: float):
        """Outward-rounded Phi and phi tables on the unique endpoint set."""
        arb = self.arb
        E_lo, E_hi = arb(e_lo), arb(e_hi)
        n = xs.size
        Phi_lo = np.empty(n); Phi_hi = np.empty(n)
        phi_lo = np.empty(n); phi_hi = np.empty(n)
        peak = arb_upper(self._phi(arb(0)))
        for i in range(n):
            x = arb(float(xs[i]))
            Phi_lo[i] = arb_lower(self._Phi(x + E_lo))
            Phi_hi[i] = arb_upper(self._Phi(x + E_hi))
            a = self._phi(x + E_lo)
            b = self._phi(x + E_hi)
            lo = min(arb_lower(a), arb_lower(b))
            hi = max(arb_upper(a), arb_upper(b))
            if float(xs[i]) + e_lo < 0.0 < float(xs[i]) + e_hi:
                hi = max(hi, peak)
            phi_lo[i] = lo; phi_hi[i] = hi
        return Phi_lo, Phi_hi, phi_lo, phi_hi

    def segment_integrals(self, a, b, e_lo, e_hi):
        old = self.ctx.prec
        self.ctx.prec = self.bits
        try:
            c, w = 0.5 * (e_lo + e_hi), 0.5 * (e_hi - e_lo)
            xs, inv = np.unique(np.concatenate([a, b]), return_inverse=True)
            Pc_lo, Pc_hi, pc_lo, pc_hi = self._tables(xs, c, c)
            ia, ib = inv[: a.size], inv[a.size:]
            m0_lo = Pc_lo[ib] - Pc_hi[ia]
            m0_hi = Pc_hi[ib] - Pc_lo[ia]
            d1_lo = pc_lo[ib] - pc_hi[ia]
            d1_hi = pc_hi[ib] - pc_lo[ia]
            mass_lo, mass_hi = _taylor_mass(m0_lo, m0_hi, d1_lo, d1_hi, a, b, w)
            Phi_lo, Phi_hi, phi_lo, phi_hi = self._tables(xs, e_lo, e_hi)
            zmom_lo = (phi_lo[ia] - phi_hi[ib]) - e_hi * mass_hi
            zmom_hi = (phi_hi[ia] - phi_lo[ib]) - e_lo * mass_lo
            return mass_lo, mass_hi, zmom_lo, zmom_hi
        finally:
            self.ctx.prec = old

    def n_unique(self, a, b) -> int:
        return int(np.unique(np.concatenate([a, b])).size)


    def derivative_integrals(self, a, b, e_lo, e_hi):
        old = self.ctx.prec
        self.ctx.prec = self.bits
        try:
            xs, inv = np.unique(np.concatenate([a, b]), return_inverse=True)
            Phi_lo, Phi_hi, phi_lo, phi_hi = self._tables(xs, e_lo, e_hi)
            ia, ib = inv[: a.size], inv[a.size:]
            mass_lo = np.maximum(Phi_lo[ib] - Phi_hi[ia], 0.0)
            mass_hi = np.maximum(Phi_hi[ib] - Phi_lo[ia], 0.0)
            dw_lo = phi_lo[ib] - phi_hi[ia]
            dw_hi = phi_hi[ib] - phi_lo[ia]
            bp_lo = np.minimum(b * phi_lo[ib], b * phi_hi[ib])
            bp_hi = np.maximum(b * phi_lo[ib], b * phi_hi[ib])
            ap_lo = np.minimum(a * phi_lo[ia], a * phi_hi[ia])
            ap_hi = np.maximum(a * phi_lo[ia], a * phi_hi[ia])
            dr_lo = bp_lo - ap_hi - mass_hi
            dr_hi = bp_hi - ap_lo - mass_lo
            peak = 1.0 / SQRT2PI + 1e-16
            A_lo, A_hi = a + e_lo, a + e_hi
            B_lo, B_hi = b + e_lo, b + e_hi
            straddle = (A_lo < 0.0) & (B_hi > 0.0)
            j2 = np.where(
                straddle,
                2.0 * peak,
                np.maximum(phi_hi[ia] - phi_lo[ib], phi_hi[ib] - phi_lo[ia]),
            )
            j2 = np.maximum(j2, 0.0) + 1e-16
            return dw_lo, dw_hi, dr_lo, dr_hi, j2
        finally:
            self.ctx.prec = old



    def tail_derivative(self, lo_edge, hi_edge, e_lo, e_hi):
        arb = self.arb
        old = self.ctx.prec
        self.ctx.prec = self.bits
        try:
            lo_edge = np.atleast_1d(lo_edge); hi_edge = np.atleast_1d(hi_edge)
            n = lo_edge.size
            out_lo = np.empty(n); out_hi = np.empty(n)
            for i in range(n):
                vals = []
                for e in (arb(e_lo), arb(e_hi)):
                    Ae = arb(float(lo_edge[i])); Be = arb(float(hi_edge[i]))
                    A, B = Ae + e, Be + e
                    total = (Ae * self._phi(A) - self._Phi(A)
                             - Be * self._phi(B) - (1 - self._Phi(B)))
                    vals.append((arb_lower(total), arb_upper(total)))
                out_lo[i] = min(v[0] for v in vals)
                out_hi[i] = max(v[1] for v in vals)
            return out_lo, out_hi
        finally:
            self.ctx.prec = old
    def tail_moment(self, lo_edge, hi_edge, e_lo, e_hi):
        arb = self.arb
        old = self.ctx.prec
        self.ctx.prec = self.bits
        try:
            n = np.asarray(lo_edge).size
            lo_edge = np.atleast_1d(lo_edge); hi_edge = np.atleast_1d(hi_edge)
            out_lo = np.empty(n); out_hi = np.empty(n)
            for i in range(n):
                vals = []
                for e in (arb(e_lo), arb(e_hi)):
                    A = arb(float(lo_edge[i])) + e
                    B = arb(float(hi_edge[i])) + e
                    total = (-self._phi(A) - e * self._Phi(A)
                             + self._phi(B) - e * (1 - self._Phi(B)))
                    vals.append((arb_lower(total), arb_upper(total)))
                out_lo[i] = min(v[0] for v in vals)
                out_hi[i] = max(v[1] for v in vals)
            return out_lo, out_hi
        finally:
            self.ctx.prec = old

    def tail_integrals(self, z_cut, e_lo, e_hi):
        arb = self.arb
        old = self.ctx.prec
        self.ctx.prec = self.bits
        try:
            los, his = [], []
            for e in (arb(e_lo), arb(e_hi)):
                lower = -self._phi(e - z_cut) - e * self._Phi(e - z_cut)
                upper = self._phi(arb(z_cut) + e) - e * (1 - self._Phi(arb(z_cut) + e))
                total = lower + upper
                los.append(arb_lower(total)); his.append(arb_upper(total))
            return min(los), max(his)
        finally:
            self.ctx.prec = old




def _abs_moment_bound(a, b, e_lo, e_hi):
    """Upper bound for J2 = int_a^b |z+e| phi(z+e) dz, valid for all e in range."""
    peak = 1.0 / SQRT2PI
    A_lo, B_hi = a + e_lo, b + e_hi
    pa_lo, pa_hi = _phi_interval(a + e_lo, a + e_hi)
    pb_lo, pb_hi = _phi_interval(b + e_lo, b + e_hi)
    straddle = (A_lo < 0.0) & (B_hi > 0.0)
    monotone = np.maximum(pa_hi - pb_lo, pb_hi - pa_lo)
    return np.where(straddle, 2.0 * peak, np.maximum(monotone, 0.0)) + 1e-16


def arb_lower(x) -> float:
    """Rigorous float lower bound of an arb ball (rounds outward)."""
    return float((x - x.rad()).mid()) - abs(float(x.rad())) * 1e-12 - 1e-300


def arb_upper(x) -> float:
    return float((x + x.rad()).mid()) + abs(float(x.rad())) * 1e-12 + 1e-300
