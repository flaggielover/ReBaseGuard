"""Certified one-step transition structure for the frozen CUSUM.

For a live state s = (p,m) and innovation z ~ N(-e, 1) the one-step map is

    (T G)(s) = int_{-inf}^{inf} psi(s,z) phi(z+e) dz ,

    psi(s,z) = z                      if z <= -v(s) or z >= u(s)   [alarm]
             = G(q(s,z))              otherwise                    [continue]

with u(s) = h+k-p, v(s) = h+k-m, q(s,z) = ((p+z-k)^+, (m-z-k)^+).
G = T G is the fixed-point equation for G(s) = E_s[z_tau], and T is monotone in
G, which is what makes the interval iteration in `enclosure.py` sound.

WHAT IS AND IS NOT APPROXIMATED HERE
------------------------------------
* The z-axis is cut at breakpoints; each piece is integrated in CLOSED FORM
  against the Gaussian.  There is no quadrature rule and hence no quadrature
  error.
* The outer tails |z| > Z_CUT are pure-alarm regions (because the continuation
  set is contained in (-(h+k), h+k)) and are integrated in closed form to
  infinity.  There is no domain truncation and hence no truncation error.
* A source *cell* is a box, so u, v and the breakpoints are intervals.  Every
  quantity derived from them is enclosed, never evaluated at a midpoint.
* A destination is resolved to a *superset* of cells, and the value is taken as
  the min/max over that superset.  This is the only place cell size enters, and
  it enters as interval width, never as an unbounded error.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from domain import Partition, destination_cells

SEG_ALARM = 0
SEG_CONT = 1
SEG_MIXED = 2


@dataclass(slots=True)
class TransitionStructure:
    n_cells: int
    seg_src: np.ndarray          # source cell index per segment
    seg_type: np.ndarray
    seg_a: np.ndarray            # segment z-endpoints
    seg_b: np.ndarray
    mass_lo: np.ndarray
    mass_hi: np.ndarray
    zmom_lo: np.ndarray          # integral of z*phi over the segment
    zmom_hi: np.ndarray
    members: np.ndarray          # flattened destination cell indices
    member_offsets: np.ndarray   # reduceat offsets into `members`
    member_counts: np.ndarray
    src_offsets: np.ndarray      # reduceat offsets into segments, per source
    tail_lo: np.ndarray          # exact closed-form outer-tail z-moment, per source
    tail_hi: np.ndarray
    tail_edge_lo: np.ndarray
    tail_edge_hi: np.ndarray
    e_lo: float
    e_hi: float
    n_segments: int


class Backend:
    """Numeric backend: must return OUTWARD-rounded (lo, hi) enclosures."""

    def phi_Phi(self, x_lo: np.ndarray, x_hi: np.ndarray):
        raise NotImplementedError


def _breakpoints(part: Partition, p0, p1, m0, m1, lo, hi) -> np.ndarray:
    """Every z in [lo,hi] at which the destination cell can change."""
    k = part.k
    pts = [lo, hi, k - p1, k - p0, m0 - k, m1 - k]
    for levels in (part.axis_p_edges, part.tri_p_edges):
        pts.extend((levels + k - p1).tolist())
        pts.extend((levels + k - p0).tolist())
    for levels in (part.axis_m_edges, part.tri_m_edges):
        pts.extend((m0 - k - levels).tolist())
        pts.extend((m1 - k - levels).tolist())
    arr = np.array(pts, dtype=float)
    arr = arr[(arr >= lo) & (arr <= hi)]
    return np.unique(np.concatenate([arr, [lo, hi]]))


def build_transitions(
    part: Partition, backend: Backend, e_lo: float, e_hi: float,
    *, z_cut: float = 12.0,
) -> TransitionStructure:
    """Assemble the certified segment table for reference error e in [e_lo,e_hi].

    Segment layout per source cell, left to right:

        (-inf, -v_lo]        outer alarm tail   -- ONE segment, closed form
        [-v_lo, -v_hi]       lower boundary strip (MIXED: may alarm or continue)
        [-v_hi, u_lo]        certain continuation, cut at destination boundaries
        [u_lo, u_hi]         upper boundary strip (MIXED)
        [u_hi, +inf)         outer alarm tail   -- ONE segment, closed form

    Keeping each alarm tail as a SINGLE segment matters: the z-moment enclosure
    is naive in e, so splitting the tails into hundreds of pieces would let that
    looseness accumulate the same way the mass enclosure did.
    """
    h, k = part.h, part.k
    if z_cut <= h + k + 1.0:
        raise ValueError("z_cut must strictly exceed h+k so the outer tails are "
                         "pure-alarm regions")

    seg_src, seg_type, seg_a, seg_b = [], [], [], []
    mem, mem_counts = [], []
    src_offsets = np.zeros(part.n_cells, dtype=np.int64)
    tail_edge_lo = np.empty(part.n_cells)
    tail_edge_hi = np.empty(part.n_cells)

    for s in range(part.n_cells):
        p0, p1 = part.p_lo[s], part.p_hi[s]
        m0, m1 = part.m_lo[s], part.m_hi[s]
        nv_lo, nv_hi = m0 - h - k, m1 - h - k
        u_lo, u_hi = h + k - p1, h + k - p0
        tail_edge_lo[s] = nv_lo
        tail_edge_hi[s] = u_hi
        src_offsets[s] = len(seg_src)

        edges = _breakpoints(part, p0, p1, m0, m1, nv_lo, u_hi)
        for i in range(edges.size - 1):
            a, b = float(edges[i]), float(edges[i + 1])
            if b <= a:
                continue
            certain = (a >= nv_hi) and (b <= u_lo)
            seg_src.append(s); seg_a.append(a); seg_b.append(b)
            seg_type.append(SEG_CONT if certain else SEG_MIXED)
            dp_lo, dp_hi = p0 + a - k, p1 + b - k
            dm_lo, dm_hi = m0 - b - k, m1 - a - k
            cells = destination_cells(part, dp_lo, dp_hi, dm_lo, dm_hi)
            if not cells:
                raise RuntimeError(
                    f"cell {s}: segment [{a},{b}] has no destination cell; the "
                    f"live-region enclosure (Lemma L1) is violated on this grid"
                )
            mem.extend(cells)
            mem_counts.append(len(cells))

    seg_a = np.array(seg_a); seg_b = np.array(seg_b)
    seg_src = np.array(seg_src, dtype=np.int64)
    seg_type = np.array(seg_type, dtype=np.int8)
    mem_counts = np.array(mem_counts, dtype=np.int64)
    members = np.array(mem, dtype=np.int64)
    member_offsets = np.concatenate([[0], np.cumsum(mem_counts)[:-1]]).astype(np.int64)

    geom = dict(
        n_cells=part.n_cells, seg_src=seg_src, seg_type=seg_type,
        seg_a=seg_a, seg_b=seg_b, members=members,
        member_offsets=member_offsets, member_counts=mem_counts,
        src_offsets=src_offsets, tail_edge_lo=tail_edge_lo,
        tail_edge_hi=tail_edge_hi,
    )
    if backend is None:
        return geom

    mass_lo, mass_hi, zmom_lo, zmom_hi = backend.segment_integrals(
        seg_a, seg_b, e_lo, e_hi)
    tail_lo, tail_hi = backend.tail_moment(tail_edge_lo, tail_edge_hi, e_lo, e_hi)

    return TransitionStructure(
        n_cells=part.n_cells, seg_src=seg_src, seg_type=seg_type,
        seg_a=seg_a, seg_b=seg_b,
        mass_lo=mass_lo, mass_hi=mass_hi, zmom_lo=zmom_lo, zmom_hi=zmom_hi,
        members=members, member_offsets=member_offsets, member_counts=mem_counts,
        src_offsets=src_offsets, tail_lo=tail_lo, tail_hi=tail_hi,
        tail_edge_lo=tail_edge_lo, tail_edge_hi=tail_edge_hi,
        e_lo=e_lo, e_hi=e_hi, n_segments=seg_src.size,
    )


def attach_integrals(geom: dict, backend: Backend, e_lo: float,
                     e_hi: float) -> TransitionStructure:
    """Re-price a cached segment geometry at a new e.

    The partition and the breakpoint layout do not depend on `e` at all -- only
    the Gaussian masses do.  Rebuilding the geometry for every mesh point would
    repeat the same Python loops dozens of times for identical output.
    """
    mass_lo, mass_hi, zmom_lo, zmom_hi = backend.segment_integrals(
        geom["seg_a"], geom["seg_b"], e_lo, e_hi)
    tail_lo, tail_hi = backend.tail_moment(
        geom["tail_edge_lo"], geom["tail_edge_hi"], e_lo, e_hi)
    return TransitionStructure(
        n_cells=geom["n_cells"], seg_src=geom["seg_src"],
        seg_type=geom["seg_type"], seg_a=geom["seg_a"], seg_b=geom["seg_b"],
        mass_lo=mass_lo, mass_hi=mass_hi, zmom_lo=zmom_lo, zmom_hi=zmom_hi,
        members=geom["members"], member_offsets=geom["member_offsets"],
        member_counts=geom["member_counts"], src_offsets=geom["src_offsets"],
        tail_lo=tail_lo, tail_hi=tail_hi,
        tail_edge_lo=geom["tail_edge_lo"], tail_edge_hi=geom["tail_edge_hi"],
        e_lo=e_lo, e_hi=e_hi, n_segments=geom["seg_src"].size,
    )
