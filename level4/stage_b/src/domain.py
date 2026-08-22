"""State-space partition for the frozen two-sided CUSUM live region.

The live (pre-alarm) reachable region is, by the enclosure lemma (Stage B
`theorem.md`, lemma L1, which is the Level 1-3 certificate's `reachable_domain`):

    L = {(p,0) : 0 <= p < h}  u  {(0,m) : 0 <= m < h}
        u  {(p,m) : p > 0, m > 0, p + m < h - 2k}

The partition below is a *bookkeeping* device only: the certificate never
assumes the value function is constant on a cell.  Cells carry rigorous lower
and upper bounds, and the monotone interval iteration keeps those bounds valid
at every step.  A coarse cell therefore costs interval width, never soundness.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

# The frozen Level 1-3 constants.  Stage B makes no claim for any other pair,
# so the driver refuses to run with anything else rather than silently
# producing a certificate about a different model.
FROZEN_K = 0.5
FROZEN_H = 5.0


def assert_frozen_constants(k: float, h: float) -> None:
    if k != FROZEN_K or h != FROZEN_H:
        raise ValueError(
            f"Stage B is certified only for the frozen constants "
            f"k={FROZEN_K}, h={FROZEN_H}; got k={k}, h={h}. "
            f"Change them only by starting a new, separately scoped stage."
        )

ATOM = 0
AXIS_P = 1
AXIS_M = 2
TRI = 3


def graded_edges(hi: float, n: int, power: float) -> np.ndarray:
    """Cell edges on [0, hi], graded to be finest at ``hi``.

    ``G`` is flat away from the alarm boundary and steepens as an arm
    approaches ``h``, so a uniform grid would spend nearly all of its cells
    where the function does not move.
    """
    t = np.linspace(0.0, 1.0, n + 1)
    return hi * (1.0 - (1.0 - t) ** power)


@dataclass(slots=True)
class Partition:
    h: float
    k: float
    axis_p_edges: np.ndarray
    axis_m_edges: np.ndarray
    tri_p_edges: np.ndarray
    tri_m_edges: np.ndarray
    kind: np.ndarray
    p_lo: np.ndarray
    p_hi: np.ndarray
    m_lo: np.ndarray
    m_hi: np.ndarray
    axis_p_index: np.ndarray
    axis_m_index: np.ndarray
    tri_index: np.ndarray

    @property
    def n_cells(self) -> int:
        return int(self.kind.size)

    @property
    def atom(self) -> int:
        return 0


def build_partition(
    *, h: float = 5.0, k: float = 0.5,
    n_axis: int = 160, axis_power: float = 3.0,
    n_tri: int = 40,
    axis_p_edges: np.ndarray | None = None,
    axis_m_edges: np.ndarray | None = None,
) -> Partition:
    sigma = h - 2.0 * k
    ap = graded_edges(h, n_axis, axis_power) if axis_p_edges is None else np.asarray(axis_p_edges, float)
    am = graded_edges(h, n_axis, axis_power) if axis_m_edges is None else np.asarray(axis_m_edges, float)
    n_axis = ap.size - 1
    if am.size != ap.size:
        raise ValueError("axis grids must have the same number of cells")
    tp = np.linspace(0.0, sigma, n_tri + 1)
    tm = np.linspace(0.0, sigma, n_tri + 1)

    kind = [ATOM]
    p_lo, p_hi, m_lo, m_hi = [0.0], [0.0], [0.0], [0.0]

    axis_p_index = np.full(n_axis + 1, -1, dtype=np.int64)
    for i in range(1, n_axis + 1):
        axis_p_index[i] = len(kind)
        kind.append(AXIS_P)
        p_lo.append(ap[i - 1]); p_hi.append(ap[i])
        m_lo.append(0.0); m_hi.append(0.0)

    axis_m_index = np.full(n_axis + 1, -1, dtype=np.int64)
    for j in range(1, n_axis + 1):
        axis_m_index[j] = len(kind)
        kind.append(AXIS_M)
        p_lo.append(0.0); p_hi.append(0.0)
        m_lo.append(am[j - 1]); m_hi.append(am[j])

    tri_index = np.full((n_tri + 1, n_tri + 1), -1, dtype=np.int64)
    for i in range(1, n_tri + 1):
        for j in range(1, n_tri + 1):
            if tp[i - 1] + tm[j - 1] >= sigma:
                continue
            tri_index[i, j] = len(kind)
            kind.append(TRI)
            p_lo.append(tp[i - 1]); p_hi.append(tp[i])
            m_lo.append(tm[j - 1]); m_hi.append(tm[j])

    return Partition(
        h=h, k=k,
        axis_p_edges=ap, axis_m_edges=am, tri_p_edges=tp, tri_m_edges=tm,
        kind=np.array(kind, dtype=np.int8),
        p_lo=np.array(p_lo), p_hi=np.array(p_hi),
        m_lo=np.array(m_lo), m_hi=np.array(m_hi),
        axis_p_index=axis_p_index, axis_m_index=axis_m_index,
        tri_index=tri_index,
    )


def _range_on_axis(edges: np.ndarray, index: np.ndarray,
                   lo: float, hi: float) -> list[int]:
    lo = max(lo, 0.0)
    i0 = int(np.searchsorted(edges, lo, side="left"))
    i1 = int(np.searchsorted(edges, hi, side="right"))
    out = []
    for i in range(max(i0, 1), min(i1 + 1, index.size)):
        if index[i] >= 0:
            out.append(int(index[i]))
    return out


def destination_cells(
    part: Partition, p_lo: float, p_hi: float, m_lo: float, m_hi: float
) -> list[int]:
    """Every cell the destination box can meet.

    Returning a *superset* is sound (the bound only gets wider); returning too
    few is not, so every comparison here is deliberately inclusive.
    """
    out: list[int] = []
    p_pos, m_pos = p_hi > 0.0, m_hi > 0.0
    p_zero, m_zero = p_lo <= 0.0, m_lo <= 0.0

    if p_zero and m_zero:
        out.append(part.atom)
    if p_zero and m_pos:
        out += _range_on_axis(part.axis_m_edges, part.axis_m_index, m_lo, m_hi)
    if m_zero and p_pos:
        out += _range_on_axis(part.axis_p_edges, part.axis_p_index, p_lo, p_hi)
    if p_pos and m_pos:
        i0 = int(np.searchsorted(part.tri_p_edges, max(p_lo, 0.0), side="left"))
        i1 = int(np.searchsorted(part.tri_p_edges, p_hi, side="right"))
        j0 = int(np.searchsorted(part.tri_m_edges, max(m_lo, 0.0), side="left"))
        j1 = int(np.searchsorted(part.tri_m_edges, m_hi, side="right"))
        for i in range(max(i0, 1), min(i1 + 1, part.tri_index.shape[0])):
            for j in range(max(j0, 1), min(j1 + 1, part.tri_index.shape[1])):
                idx = part.tri_index[i, j]
                if idx >= 0:
                    out.append(int(idx))
    return sorted(set(out))


def adaptive_edges(sample_x: np.ndarray, sample_f: np.ndarray, n: int,
                   hi: float, *, floor_frac: float = 0.15) -> np.ndarray:
    """Cell edges equidistributing the variation of a sampled profile.

    The profile comes from a *non-rigorous* float solve.  That is sound: the
    grid only decides how wide the certified bracket ends up, never whether it
    is valid.  A bad grid costs width; it cannot make a false statement true.
    The profile used is recorded in the certificate so the choice is auditable.
    """
    x = np.asarray(sample_x, dtype=float)
    f = np.asarray(sample_f, dtype=float)
    dens = np.abs(np.gradient(f, x))
    dens = dens + floor_frac * dens.max() if dens.max() > 0 else np.ones_like(x)
    cum = np.concatenate([[0.0], np.cumsum(0.5 * (dens[1:] + dens[:-1]) * np.diff(x))])
    cum /= cum[-1]
    targets = np.linspace(0.0, 1.0, n + 1)
    edges = np.interp(targets, cum, x)
    edges[0], edges[-1] = 0.0, hi
    return np.maximum.accumulate(edges)
