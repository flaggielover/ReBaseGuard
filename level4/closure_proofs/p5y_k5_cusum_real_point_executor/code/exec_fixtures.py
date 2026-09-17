"""Manufactured fixtures and exact truth for the real point executor qualification.

Truth: exact rational derivatives of the manufactured sigma-system (R3 first_cell.true_derivs / true_R, the R1 Taylor
recurrence), independently confirmed by the R4 acb Cauchy cross-check (m5_crosscheck).
"""
from __future__ import annotations

from fractions import Fraction as F

import paths  # noqa: F401

import executor_core as EC  # noqa: E402

M_SET = EC.M_SET


def truth(spec: dict, grid_points: int = 17) -> dict:
    import first_cell as FC3
    import sigma_systems as SS
    sysm = SS.build(spec)
    x1 = F(spec["x1"])
    grid = [x1 * F(g, grid_points - 1) for g in range(grid_points)]
    ders = {e: FC3.true_derivs(sysm, e) for e in grid}
    out = {}
    for m in M_SET:
        r3 = [FC3.true_R(ders[e], m, 3) for e in grid]
        r5 = [abs(FC3.true_R(ders[e], m, 5)) for e in grid]
        out[m] = {"R3_at_0": r3[0], "min_R3": min(r3), "max_R3": max(r3), "max_abs_R5": max(r5)}
    nodes = {}
    for e in grid:
        for node, vec in ders[e].items():
            ge, go, gt = SS.gnorm(vec)
            cur = nodes.get(node, (F(0), F(0), F(0)))
            nodes[node] = (max(cur[0], ge), max(cur[1], go), max(cur[2], gt))
    out["node_sups"] = nodes                                   # exact sup over the grid of every graded true object
    return out


def containment(record: dict, tr: dict) -> list[str]:
    viol = []
    for m in M_SET:
        v = {k: F(x) for k, x in record["scientific"]["per_m"][str(m)].items()}
        t = tr[m]
        if not v["L0"] <= t["R3_at_0"] <= v["U0"]:
            viol.append(f"m={m}: I0 misses R'''(0)")
        if not v["L1"] <= t["min_R3"]:
            viol.append(f"m={m}: L1 > min R''' on [0,x1]")
        if not v["U1"] >= t["max_R3"]:
            viol.append(f"m={m}: U1 < max R''' on [0,x1]")
        if not v["M5"] >= t["max_abs_R5"]:
            viol.append(f"m={m}: M5 < max|R5|")
    it = record["scientific"]["intermediates"]
    for table in ("tower_nodes", "local_anchors"):
        for node, bounds in it[table].items():
            if node in tr["node_sups"]:
                for lab, true, bound in zip("eot", tr["node_sups"][node], bounds):
                    if true > F(bound):
                        viol.append(f"{table} {node}.{lab}: truth exceeds bound")
    return viol
