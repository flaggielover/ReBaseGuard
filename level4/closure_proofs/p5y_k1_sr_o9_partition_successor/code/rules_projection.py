"""Phases 2 and 5: evaluate candidate partition rules on the FROZEN 316-cell SR table (geometry and frozen constants
only; no T2-T5 record, verdict or ratio is read). Cost projection is an estimate, not a qualification.

a-priori feedback factor (frozen sr_refine contraction formula, certified closed-form norms on the child window):
    q(child) = C_upper(parent) * rho_c * (2*A_1(W_c) + A_2(W_c)*rho_c/2),   W_c = [-c_SR + e_lo, c_SR + e_hi]
Rules (dyadic children N in {1,2,4,...}, equal exact-rational splitting of each parent):
  GLOBAL_xN       : every parent split into N children
  RHO_CAP(r_max)  : smallest dyadic N with rho_parent / N <= r_max
  Q_CAP(q_max)    : smallest dyadic N with q(child) <= q_max for every child of that parent
"""
import json
from fractions import Fraction as Fr
from pathlib import Path

import sr_o9_candidates as T
import curv_mv as M
from flint import arb

NS = Path(__file__).resolve().parents[1]
T3_MID_CPU_H_PER_CELL = 20.0     # curvature-successor projection: ~18 CPU-s/patch x 3,994 patches (midpoint mode)
T3_BOTH_CPU_H_PER_CELL = 51.0    # measured cell 150 / six-cell runs, both drift modes
T45_CPU_H_PER_CELL = 0.05        # T4 + T5 + mean-value curvature: minutes


def sr_cells():
    return sorted([c for c in T.spec.CELLS if c["detector"] == "SR"], key=lambda c: c["index"])


def q_child(cell, Nc, k):
    with T.scientific_precision():
        g = T.cell_geometry(cell)
        L, R = g["left"], g["right"]
        w = (R - L) / arb(Nc)
        lo, hi = L + arb(k) * w, L + arb(k + 1) * w
        _A, _b, c = M.PC.L.sr_constants()
        a1, a2 = M.A(1, -c + lo, c + hi), M.A(2, -c + lo, c + hi)
        rc = w / arb(2)
        cu = Fr(cell["C_upper"])
        C = arb(cu.numerator) / arb(cu.denominator)
        return float((C * rc * (arb(2) * a1 + a2 * rc / arb(2))).upper()), float(rc.upper())


def main():
    cells = sr_cells()
    assert len(cells) == 316
    parent = []
    for c in cells:
        q1, r1 = q_child(c, 1, 0)
        parent.append({"index": c["index"], "rho": r1, "q_parent": q1})
    rules = {}
    for n in (2, 4, 8, 16):
        rules[f"GLOBAL_x{n}"] = {c["index"]: n for c in cells}
    for rmax in ("1/25", "1/32", "1/50"):
        rm = float(Fr(rmax))
        rules[f"RHO_CAP_{rmax}"] = {p["index"]: next(n for n in (1, 2, 4, 8, 16, 32, 64) if p["rho"] / n <= rm) for p in parent}
    qcache = {}
    for qmax in (0.1, 0.08, 0.05):
        sel = {}
        for c in cells:
            for n in (1, 2, 4, 8, 16, 32):
                key = (c["index"], n)
                if key not in qcache:
                    qcache[key] = max(q_child(c, n, k)[0] for k in range(n)) if (n <= 4 or c["index"] >= 280) else \
                                  max(q_child(c, n, k)[0] for k in (0, n - 1))
                if qcache[key] <= qmax:
                    sel[c["index"]] = n
                    break
        rules[f"Q_CAP_{qmax}"] = sel
    proj = {}
    for name, sel in rules.items():
        ncell = sum(sel.values())
        proj[name] = {"successor_cells": ncell, "refined_parents": sum(1 for v in sel.values() if v > 1),
                      "children_of_313": sel[313], "children_of_315_terminal": sel[315],
                      "split_histogram": {str(n): sum(1 for v in sel.values() if v == n) for n in sorted(set(sel.values()))},
                      "max_child_rho": max(p["rho"] / sel[p["index"]] for p in parent),
                      "T3_midpoint_runs": ncell, "obligations": 28 * ncell,
                      "cpu_h_midpoint_only_T3": ncell * (T3_MID_CPU_H_PER_CELL + T45_CPU_H_PER_CELL),
                      "cpu_h_if_interval_e_T3_kept": ncell * (T3_BOTH_CPU_H_PER_CELL + T45_CPU_H_PER_CELL)}
    out = {"schema": "rebaseguard.p5y.k1.sr.o9.partition-rules.v1", "inputs": "frozen cells.json + frozen constants only",
           "parents": parent, "rules": {k: {str(i): n for i, n in v.items()} for k, v in rules.items()}, "projection": proj,
           "cost_basis": {"T3_midpoint_cpu_h_per_cell": T3_MID_CPU_H_PER_CELL, "T3_both_modes_cpu_h_per_cell": T3_BOTH_CPU_H_PER_CELL,
                          "T45_cpu_h_per_cell": T45_CPU_H_PER_CELL, "status": "ESTIMATE ONLY; cap not requalified"}}
    (NS / "evidence/phase25_rules_projection.json").write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    print("parent q 300..315:", [(p["index"], round(p["rho"], 4), round(p["q_parent"], 4)) for p in parent[300:]])
    for name, p in proj.items():
        print(f"{name:16s} cells={p['successor_cells']:5d} refined={p['refined_parents']:3d} 313->{p['children_of_313']} 315->{p['children_of_315_terminal']} "
              f"max_child_rho={p['max_child_rho']:.4f} cpu_h(mid-only)={p['cpu_h_midpoint_only_T3']:.0f} hist={p['split_histogram']}")


if __name__ == "__main__":
    main()
