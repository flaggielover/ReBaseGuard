"""Frozen CUSUM cover walk -- deterministic reconstruction, no redesign.

Authoritative sources, read not inferred:
  cover_cusum.json   interval [0, 5.5], 323 sub-cells,
                     step rule h(e) = 1/(4 a C(e)), a = 2 phi(0),
                     greedy from e = 0, exact tiling, no adaptive splitting
  R1_FROZEN_SPEC.md  T7: every e_0 is an exact rational with denominator 10^7,
                     the sub-cells tile exactly
  R1_COST_REPROJECTION.md  cells/unit e = 1/(2h), i.e. h is the HALF-width and
                     the cell width is 2h  (verified: at e = 0.25, C = 207.75
                     gives 1/(2h) = 331.5 against the table's 332)

C(e) is the R1 drift-monotone resolvent evaluated at the cell's LEFT endpoint,
which is the smallest |e| of the cell and therefore the worst case by M2.
"""
from __future__ import annotations

import json
import math
import sys
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
for _p in (str(ROOT / "rebaseguard-proof/src"),
           str(ROOT / "level4/closure_proofs/p5x_global_nonlinear_dynamics"
                      "/compute_optimization_r1")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from drift_minorant import drift_monotone_resolvent                   # noqa: E402

Q = 10 ** 7                       # frozen T7 rational denominator
E_STAR = Fraction(11, 2)          # frozen c_CUSUM
E_STAR_Q = E_STAR.numerator * Q // E_STAR.denominator
A_CONST = 2.0 / math.sqrt(2.0 * math.pi)     # a = 2 phi(0)


def step_half_width(e_num_q: int) -> tuple[float, float]:
    """(h, C) at the cell's left endpoint, on the frozen denominator grid."""
    f = Fraction(e_num_q, Q)
    C = drift_monotone_resolvent(e_num=f.numerator, e_den=f.denominator)[
        "resolvent_bound_upper_float"]
    return 1.0 / (4.0 * A_CONST * C), C


def walk() -> list[dict]:
    """Greedy frozen walk. Endpoints are exact rationals with denominator 10^7;
    the step is FLOORED onto that grid, which can only shorten a cell and so is
    conservative. The final cell is truncated at e_star, giving exact tiling."""
    cells: list[dict] = []
    e_q = 0
    while e_q < E_STAR_Q:
        h, C = step_half_width(e_q)
        adv = int(math.floor(2.0 * h * Q))
        if adv < 1:
            adv = 1                                   # grid resolution floor
        nxt_q = min(e_q + adv, E_STAR_Q)
        cells.append({
            "cell_id": len(cells),
            "left_num": e_q, "right_num": nxt_q, "den": Q,
            "left": e_q / Q, "right": nxt_q / Q,
            "width": (nxt_q - e_q) / Q,
            "half_width_rule_h": h,
            "C_at_left_endpoint": C,
            "provenance": "h = 1/(4 a C(e_left)); width = floor(2h*10^7)/10^7",
        })
        e_q = nxt_q
    return cells


def invariants(cells: list[dict]) -> dict:
    n = len(cells)
    gaps = [i for i in range(n - 1)
            if cells[i]["right_num"] != cells[i + 1]["left_num"]]
    dups = [i for i in range(n - 1)
            if cells[i]["right_num"] > cells[i + 1]["left_num"]]
    mono = all(cells[i]["left_num"] < cells[i]["right_num"] for i in range(n))
    return {"cell_count": n,
            "start_num": cells[0]["left_num"], "start_match": cells[0]["left_num"] == 0,
            "end_num": cells[-1]["right_num"], "end_match": cells[-1]["right_num"] == E_STAR_Q,
            "splice_match": cells[-1]["right"] == float(E_STAR),
            "no_gaps": not gaps, "gap_indices": gaps[:5],
            "no_duplicates": not dups, "overlap_indices": dups[:5],
            "monotone": mono,
            "total_measure": sum(c["width"] for c in cells),
            "measure_match": abs(sum(c["width"] for c in cells) - float(E_STAR)) < 1e-9}


def canonical_table(cells: list[dict]) -> str:
    return json.dumps(cells, sort_keys=True, separators=(",", ":"))


def cell_drift(cell_id: int, cells: list[dict]) -> tuple[int, int]:
    """Certification drift for a cell: its LEFT endpoint, as an exact rational.

    The left endpoint is the smallest |e| in the cell and therefore the worst
    case for the resolvent by M2 -- the same convention the frozen budget uses
    (`C_D evaluated at e_lo`)."""
    c = cells[cell_id]
    f = Fraction(c["left_num"], c["den"])
    return f.numerator, f.denominator


if __name__ == "__main__":
    import time
    t = time.process_time()
    cs = walk()
    inv = invariants(cs)
    inv["walk_cpu_seconds"] = time.process_time() - t
    print(json.dumps(inv, indent=1))
