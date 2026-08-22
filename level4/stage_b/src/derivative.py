"""Certified enclosure of G'(e) = d/de E_e[z_tau] via the differentiated equation.

Lemma L6 gives   (I - K_e) G'_e = (partial_e K_e) G_e + partial_e r_e =: R_e ,
so G' = K_e G' + R.  K_e is positive and R is enclosed from the *certified* G
bracket, so the same monotone iteration applies and every iterate is again a
valid bracket.

This is a genuinely independent route from a finite difference of G: it never
evaluates G at two nearby e and subtracts.  A finite-difference cross-check is
computed separately and reported, but the claim rests on this equation.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from enclosure import ROUNDING_SLACK
from transitions import SEG_ALARM, SEG_CONT, SEG_MIXED, TransitionStructure


def interval_mul(vlo, vhi, wlo, whi):
    """General interval product; `w` (the d/de weights) changes sign."""
    p1, p2 = vlo * wlo, vlo * whi
    p3, p4 = vhi * wlo, vhi * whi
    return (np.minimum(np.minimum(p1, p2), np.minimum(p3, p4)),
            np.maximum(np.maximum(p1, p2), np.maximum(p3, p4)))


@dataclass(slots=True)
class DerivativeBracket:
    lower: np.ndarray
    upper: np.ndarray
    r_lower: np.ndarray
    r_upper: np.ndarray
    iterations: int
    atom_lower: float
    atom_upper: float
    r_sup: float
    a_priori_bound: float

    @property
    def atom_width(self) -> float:
        return self.atom_upper - self.atom_lower


class DerivativeIterator:
    def __init__(self, struct: TransitionStructure, backend,
                 g_lower: np.ndarray, g_upper: np.ndarray,
                 resolvent_bound: float, z_cut: float) -> None:
        self.st = struct
        st = struct
        dw_lo, dw_hi, dr_lo, dr_hi, j2 = backend.derivative_integrals(
            st.seg_a, st.seg_b, st.e_lo, st.e_hi)

        nonalarm = np.flatnonzero(st.seg_type != SEG_ALARM)
        counts = st.member_counts[nonalarm]
        offsets = np.concatenate([[0], np.cumsum(counts)[:-1]]).astype(np.int64)
        starts = st.member_offsets[nonalarm]
        idx = np.concatenate([np.arange(s, s + c) for s, c in zip(starts, counts)])
        members = st.members[idx]

        self.nonalarm = nonalarm
        self.offsets = offsets
        self.members = members
        self.mass_lo_na = st.mass_lo[nonalarm]
        self.mass_hi_na = st.mass_hi[nonalarm]
        self.src_na = st.seg_src[nonalarm]
        self.mixed = st.seg_type[nonalarm] == SEG_MIXED

        # ---- assemble R = (partial_e K) G + partial_e r ----
        gmin = np.minimum.reduceat(g_lower[members], offsets)
        gmax = np.maximum.reduceat(g_upper[members], offsets)
        clo, chi = interval_mul(gmin, gmax, dw_lo[nonalarm], dw_hi[nonalarm])
        # mixed segments: bound both branches crudely but soundly
        gabs = np.maximum(np.abs(gmin), np.abs(gmax))
        zabs = np.maximum(np.abs(st.seg_a[nonalarm]), np.abs(st.seg_b[nonalarm]))
        bound = (zabs + gabs) * j2[nonalarm]
        clo = np.where(self.mixed, np.minimum(clo, -bound), clo)
        chi = np.where(self.mixed, np.maximum(chi, bound), chi)

        # partial_e of the alarm reward now comes from the two outer tails.
        # d/de int_{-inf}^{A} z phi(z+e) dz = -A phi(A+e) - Phi(A+e)  and
        # d/de int_{B}^{inf}  z phi(z+e) dz =  B phi(B+e) - (1 - Phi(B+e)).
        dtail_lo, dtail_hi = backend.tail_derivative(
            st.tail_edge_lo, st.tail_edge_hi, st.e_lo, st.e_hi)
        r_lo = np.bincount(self.src_na, clo, minlength=st.n_cells) + dtail_lo
        r_hi = np.bincount(self.src_na, chi, minlength=st.n_cells) + dtail_hi
        self.r_lo, self.r_hi = r_lo, r_hi
        self.r_sup = float(np.max(np.maximum(np.abs(r_lo), np.abs(r_hi))))
        self.a_priori = resolvent_bound * self.r_sup * 1.05

    def step(self, lower, upper):
        st = self.st
        vmin = np.minimum.reduceat(lower[self.members], self.offsets)
        vmax = np.maximum.reduceat(upper[self.members], self.offsets)
        if self.mixed.any():
            # on the alarm part of a mixed segment the continuation kernel is 0
            vmin = np.where(self.mixed, np.minimum(vmin, 0.0), vmin)
            vmax = np.where(self.mixed, np.maximum(vmax, 0.0), vmax)
        lo = np.minimum(vmin * self.mass_lo_na, vmin * self.mass_hi_na)
        hi = np.maximum(vmax * self.mass_lo_na, vmax * self.mass_hi_na)
        new_lo = np.bincount(self.src_na, lo, minlength=st.n_cells) + self.r_lo
        new_hi = np.bincount(self.src_na, hi, minlength=st.n_cells) + self.r_hi
        return new_lo - ROUNDING_SLACK, new_hi + ROUNDING_SLACK

    def run(self, *, max_iter: int = 400, tol: float = 1e-13,
            verbose: bool = False) -> DerivativeBracket:
        st = self.st
        lower = np.full(st.n_cells, -self.a_priori)
        upper = np.full(st.n_cells, self.a_priori)
        previous = np.inf
        it = 0
        for it in range(1, max_iter + 1):
            lower, upper = self.step(lower, upper)
            width = float(np.max(upper - lower))
            if verbose and (it % 25 == 0 or it == 1):
                print(f"    d-iter {it:4d} width {width:.3e} "
                      f"atom [{lower[0]:.6f}, {upper[0]:.6f}]", flush=True)
            if previous - width < tol and it > 20:
                break
            previous = width
        return DerivativeBracket(
            lower=lower, upper=upper, r_lower=self.r_lo, r_upper=self.r_hi,
            iterations=it, atom_lower=float(lower[0]), atom_upper=float(upper[0]),
            r_sup=self.r_sup, a_priori_bound=self.a_priori)
