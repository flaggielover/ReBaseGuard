"""Drive one certified enclosure of G(0,0) = E_{(0,0)}[z_tau] at drift -e."""

from __future__ import annotations

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np

from backends import ArbBackend, FloatBackend
from domain import build_partition
from enclosure import Iterator, a_priori_bound
from killing import best_killing_bound
from transitions import build_transitions


def enclose_G(
    *, e_lo: float, e_hi: float, n_axis: int, axis_power: float, n_tri: int,
    backend, z_cut: float = 12.0, max_iter: int = 400, verbose: bool = True,
    axis_p_edges=None, axis_m_edges=None,
) -> dict:
    t0 = time.time()
    part = build_partition(n_axis=n_axis, axis_power=axis_power, n_tri=n_tri,
                           axis_p_edges=axis_p_edges, axis_m_edges=axis_m_edges)
    kill = best_killing_bound(e_lo, e_hi)
    m_bound = a_priori_bound(max(abs(e_lo), abs(e_hi)), kill["arl_upper_bound"])
    if verbose:
        print(f"  cells={part.n_cells}  killing n={kill['n']} "
              f"ARL<= {kill['arl_upper_bound']:.3f}  |G|<= {m_bound:.2f}",
              flush=True)
    t1 = time.time()
    struct = build_transitions(part, backend, e_lo, e_hi, z_cut=z_cut)
    t2 = time.time()
    if verbose:
        print(f"  segments={struct.n_segments}  build {t2 - t1:.1f}s", flush=True)
    it = Iterator(struct)
    br = it.run(m_bound, max_iter=max_iter, verbose=verbose)
    t3 = time.time()
    return {
        "e_lo": e_lo, "e_hi": e_hi, "n_axis": n_axis, "axis_power": axis_power,
        "n_tri": n_tri, "n_cells": part.n_cells, "n_segments": struct.n_segments,
        "backend": backend.name, "certified_backend": backend.certified,
        "z_cut": z_cut, "killing": {k: v for k, v in kill.items() if k != "scan"},
        "a_priori_M": m_bound,
        "iterations": br.iterations,
        "G_lower": br.atom_lower, "G_upper": br.atom_upper,
        "G_width": br.atom_width, "max_cell_width": br.max_width,
        "rounding_slack": br.rounding_slack,
        "seconds_build": t2 - t1, "seconds_iterate": t3 - t2,
        "bracket": br,
        "partition": part,
        "structure": struct,
    }


if __name__ == "__main__":
    e = 1.0367242887184211
    for n_axis, power, n_tri in [(80, 2.0, 20), (160, 2.5, 30), (240, 2.5, 40)]:
        print(f"n_axis={n_axis} power={power} n_tri={n_tri}")
        r = enclose_G(e_lo=e, e_hi=e, n_axis=n_axis, axis_power=power,
                      n_tri=n_tri, backend=FloatBackend(), verbose=True)
        print(f"  => G(0,0) in [{r['G_lower']:.8f}, {r['G_upper']:.8f}]  "
              f"width {r['G_width']:.3e}   (reference -2.07342550)")
        print(f"     iterate {r['seconds_iterate']:.1f}s\n", flush=True)
