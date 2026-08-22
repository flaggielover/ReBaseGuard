"""Monotone interval iteration bracketing G(s) = E_s[z_tau].

Soundness argument (this is the whole certificate, so it is stated in full):

  T is monotone.  If G1 <= G2 pointwise then psi is pointwise monotone in the
  continuation branch and identical on the alarm branch, so T G1 <= T G2.

  Let L0 <= G <= U0 pointwise.  Define, cell by cell,
      L_{n+1}(C) = a rigorous lower bound for  inf_{s in C} (T L_n)(s)
      U_{n+1}(C) = a rigorous upper bound for  sup_{s in C} (T U_n)(s)
  where L_n, U_n are read as piecewise-constant functions.  Then
      L_{n+1} <= T L_n <= T G = G   and   G = T G <= T U_n <= U_{n+1},
  so **every iterate is a valid bracket**.  There is therefore no iterative
  solve error to bound: the iteration may be stopped at any point and the
  current bracket is already proven.  Killing (Lemma L2) makes the bracket
  contract; it is not needed for validity, only for width.

  The bound "for all s in C" is achieved by never evaluating at a point: the
  segment masses are enclosed over the box, and each destination resolves to a
  superset of cells over which the min (for L) and max (for U) are taken.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from transitions import SEG_ALARM, TransitionStructure

# Rigorous slack absorbing all float rounding in one iteration.  One iteration
# sums at most ~10^4 products of magnitude <= 10^2, so the accumulated relative
# error is below 10^4 * 2^-53 * 10^2 ~ 10^-10; 10^-9 is a decade of margin, and
# it is applied outward on both sides.
ROUNDING_SLACK = 1e-9


@dataclass(slots=True)
class Bracket:
    lower: np.ndarray
    upper: np.ndarray
    iterations: int
    max_width: float
    atom_lower: float
    atom_upper: float
    rounding_slack: float

    @property
    def atom_width(self) -> float:
        return self.atom_upper - self.atom_lower


class Iterator:
    def __init__(self, struct: TransitionStructure) -> None:
        self.st = struct
        nonalarm = np.flatnonzero(struct.seg_type != SEG_ALARM)
        self.nonalarm = nonalarm
        counts = struct.member_counts[nonalarm]
        if counts.min() < 1:
            raise RuntimeError("a continuation segment has no destination cell")
        self.offsets = np.concatenate([[0], np.cumsum(counts)[:-1]]).astype(np.int64)
        # rebuild a compact member array in nonalarm order
        starts = struct.member_offsets[nonalarm]
        idx = np.concatenate([np.arange(s, s + c) for s, c in zip(starts, counts)])
        self.members = struct.members[idx]
        self.seg_a_na = struct.seg_a[nonalarm]
        self.seg_b_na = struct.seg_b[nonalarm]
        self.mixed = struct.seg_type[nonalarm] == 2
        self.mass_lo_na = struct.mass_lo[nonalarm]
        self.mass_hi_na = struct.mass_hi[nonalarm]
        self.src_na = struct.seg_src[nonalarm]
        # The alarm reward now lives entirely in the two outer tails, one
        # closed-form segment each, held per cell in tail_lo / tail_hi.
        self.alarm_lo = struct.tail_lo
        self.alarm_hi = struct.tail_hi

    def step(self, lower: np.ndarray, upper: np.ndarray):
        st = self.st
        vmin = np.minimum.reduceat(lower[self.members], self.offsets)
        vmax = np.maximum.reduceat(upper[self.members], self.offsets)
        if self.mixed.any():
            vmin = np.where(self.mixed, np.minimum(vmin, self.seg_a_na), vmin)
            vmax = np.where(self.mixed, np.maximum(vmax, self.seg_b_na), vmax)
        lo = np.minimum(vmin * self.mass_lo_na, vmin * self.mass_hi_na)
        hi = np.maximum(vmax * self.mass_lo_na, vmax * self.mass_hi_na)
        new_lo = np.bincount(self.src_na, lo, minlength=st.n_cells) + self.alarm_lo
        new_hi = np.bincount(self.src_na, hi, minlength=st.n_cells) + self.alarm_hi
        return new_lo - ROUNDING_SLACK, new_hi + ROUNDING_SLACK

    def run(self, m_bound: float, *, max_iter: int = 400,
            tol: float = 1e-13, verbose: bool = False,
            warm: tuple[np.ndarray, np.ndarray] | None = None) -> Bracket:
        """`warm` must be a bracket already inflated enough to contain the new G.

        A warm start is only sound if the inflation provably covers the change
        in G between the two reference errors; the caller owns that argument
        (see `run_stage_b.py`, which inflates by the a priori ||G'|| bound times
        the mesh spacing).
        """
        st = self.st
        if warm is None:
            lower = np.full(st.n_cells, -m_bound)
            upper = np.full(st.n_cells, m_bound)
        else:
            lower, upper = warm[0].copy(), warm[1].copy()
        previous = np.inf
        it = 0
        for it in range(1, max_iter + 1):
            lower, upper = self.step(lower, upper)
            width = float(np.max(upper - lower))
            if verbose and (it % 25 == 0 or it == 1):
                print(f"    iter {it:4d}  max width {width:.3e}  "
                      f"atom [{lower[0]:.8f}, {upper[0]:.8f}]", flush=True)
            if previous - width < tol and it > 20:
                break
            previous = width
        return Bracket(lower=lower, upper=upper, iterations=it,
                       max_width=float(np.max(upper - lower)),
                       atom_lower=float(lower[0]), atom_upper=float(upper[0]),
                       rounding_slack=ROUNDING_SLACK)


def a_priori_bound(e_hi: float, arl_bound: float) -> float:
    """Rigorous M with |G(s)| <= M for every live s.

    |E_s[z_tau]| <= E_s[sum_{t<=tau} |z_t|] = E|z_1| * E_s[tau]  (Wald, |z_t|
    i.i.d. and integrable, tau a stopping time with finite mean), and
    E|N(-e,1)| = |e|(2 Phi(|e|) - 1) + 2 phi(|e|).
    """
    from math import erf, exp, pi, sqrt

    a = abs(e_hi)
    Phi = 0.5 * (1.0 + erf(a / sqrt(2.0)))
    phi = exp(-0.5 * a * a) / sqrt(2.0 * pi)
    c = a * (2.0 * Phi - 1.0) + 2.0 * phi
    return c * arl_bound * 1.05      # 5% margin on a bound that is already crude
