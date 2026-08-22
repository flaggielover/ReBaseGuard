"""B6/B7 — interval-Newton root certificate and multiplier certificate.

    H(e) = F_1(e) + e = 2e + G_e(0,0)

Interval Newton: for H in C^1 on I, c in I, and an enclosure H'(I) of
{H'(x) : x in I} with 0 not in H'(I),

    N(I) = c - H(c) / H'(I)

contains every zero of H in I; and if N(I) is contained in I then H has
EXACTLY ONE zero in I.  Containment in the interior gives existence robustly.
C^1 is Lemma L4, so the hypothesis is discharged analytically, not assumed.

The multiplier uses the *proved* odd symmetry (Lemma L3): F_1' is even, so
lambda_2 = F_1'(e*) F_1'(-e*) = [F_1'(e*)]^2.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, asdict
from typing import Any

import numpy as np

from derivative import DerivativeIterator
from run_enclosure import enclose_G

Z_CUT = 12.0


def interval_square(lo: float, hi: float) -> tuple[float, float]:
    if lo >= 0.0:
        return lo * lo, hi * hi
    if hi <= 0.0:
        return hi * hi, lo * lo
    return 0.0, max(lo * lo, hi * hi)


def interval_div(nlo, nhi, dlo, dhi):
    if dlo <= 0.0 <= dhi:
        raise ArithmeticError("interval division by an interval containing zero")
    cands = [nlo / dlo, nlo / dhi, nhi / dlo, nhi / dhi]
    return min(cands), max(cands)


@dataclass
class RootCertificate:
    center: float
    half_width: float
    I_lo: float
    I_hi: float
    H_center_lo: float
    H_center_hi: float
    Hprime_lo: float
    Hprime_hi: float
    newton_lo: float
    newton_hi: float
    newton_inside_interior: bool
    zero_excluded_from_I: bool
    hprime_excludes_zero: bool
    root_certified: bool
    G_center_lo: float
    G_center_hi: float
    G_interval_lo: float
    G_interval_hi: float
    Gprime_lo: float
    Gprime_hi: float
    F1prime_lo: float
    F1prime_hi: float
    lambda2_lo: float
    lambda2_hi: float
    multiplier_certified: bool
    grid: dict[str, Any]
    killing: dict[str, Any]
    backend: str
    certified_backend: bool
    precision_bits: int | None
    seconds: float

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def certify_root(
    *, center: float, half_width: float, n_axis: int, n_tri: int,
    axis_p_edges, axis_m_edges, backend_factory, verbose: bool = True,
) -> RootCertificate:
    t0 = time.time()
    lo, hi = center - half_width, center + half_width

    if verbose:
        print(f"  [1/3] G at the thin center e = {center!r}", flush=True)
    b1 = backend_factory()
    rc = enclose_G(e_lo=center, e_hi=center, n_axis=n_axis, axis_power=0,
                   n_tri=n_tri, backend=b1, verbose=False,
                   axis_p_edges=axis_p_edges, axis_m_edges=axis_m_edges,
                   z_cut=Z_CUT)
    H_lo = 2.0 * center + rc["G_lower"]
    H_hi = 2.0 * center + rc["G_upper"]
    if verbose:
        print(f"        G(c) in [{rc['G_lower']:.8f}, {rc['G_upper']:.8f}]  "
              f"H(c) in [{H_lo:+.6f}, {H_hi:+.6f}]", flush=True)

    if verbose:
        print(f"  [2/3] G over the interval e in [{lo!r}, {hi!r}]", flush=True)
    b2 = backend_factory()
    ri = enclose_G(e_lo=lo, e_hi=hi, n_axis=n_axis, axis_power=0, n_tri=n_tri,
                   backend=b2, verbose=False, axis_p_edges=axis_p_edges,
                   axis_m_edges=axis_m_edges, z_cut=Z_CUT)
    if verbose:
        print(f"        G(I) in [{ri['G_lower']:.8f}, {ri['G_upper']:.8f}]  "
              f"width {ri['G_width']:.3e}", flush=True)

    if verbose:
        print("  [3/3] G' over the interval, via the differentiated equation",
              flush=True)
    b3 = backend_factory()
    di = DerivativeIterator(ri["structure"], b3, ri["bracket"].lower,
                            ri["bracket"].upper,
                            ri["killing"]["resolvent_upper_bound"], Z_CUT)
    db = di.run(verbose=False)
    gp_lo, gp_hi = db.atom_lower, db.atom_upper
    hp_lo, hp_hi = 2.0 + gp_lo, 2.0 + gp_hi
    if verbose:
        print(f"        G'(I) in [{gp_lo:+.6f}, {gp_hi:+.6f}]  "
              f"H'(I) in [{hp_lo:+.6f}, {hp_hi:+.6f}]", flush=True)

    hprime_ok = not (hp_lo <= 0.0 <= hp_hi)
    if hprime_ok:
        qlo, qhi = interval_div(H_lo, H_hi, hp_lo, hp_hi)
        n_lo, n_hi = center - qhi, center - qlo
    else:
        n_lo, n_hi = float("-inf"), float("inf")

    inside = bool(hprime_ok and lo < n_lo and n_hi < hi)
    zero_excluded = bool(lo > 0.0 or hi < 0.0)
    f1p_lo, f1p_hi = 1.0 + gp_lo, 1.0 + gp_hi
    l2_lo, l2_hi = interval_square(f1p_lo, f1p_hi)

    return RootCertificate(
        center=center, half_width=half_width, I_lo=lo, I_hi=hi,
        H_center_lo=H_lo, H_center_hi=H_hi,
        Hprime_lo=hp_lo, Hprime_hi=hp_hi,
        newton_lo=n_lo, newton_hi=n_hi,
        newton_inside_interior=inside,
        zero_excluded_from_I=zero_excluded,
        hprime_excludes_zero=hprime_ok,
        root_certified=bool(inside and zero_excluded and hprime_ok),
        G_center_lo=rc["G_lower"], G_center_hi=rc["G_upper"],
        G_interval_lo=ri["G_lower"], G_interval_hi=ri["G_upper"],
        Gprime_lo=gp_lo, Gprime_hi=gp_hi,
        F1prime_lo=f1p_lo, F1prime_hi=f1p_hi,
        lambda2_lo=l2_lo, lambda2_hi=l2_hi,
        multiplier_certified=bool(l2_hi < 1.0),
        grid={"n_axis": n_axis, "n_tri": n_tri,
              "n_cells": rc["n_cells"], "n_segments": rc["n_segments"],
              "z_cut": Z_CUT},
        killing=ri["killing"],
        backend=b1.name, certified_backend=b1.certified,
        precision_bits=getattr(b1, "bits", None),
        seconds=time.time() - t0,
    )
