"""Exact containment checks of engine output against manufactured truth. NON-SCIENTIFIC.

Samples the closed cell at GRID+1 equispaced exact rational points (both endpoints included) and the midpoint.
A sample check is a necessary condition only; the whole-cell proof is DESIGN_REAL.md section 4.
"""
from __future__ import annotations

from fractions import Fraction as Fr

import manufactured_chain as MC
from rung3_engine import M_VALUES, W_INDICES, upper_fraction

GRID = 16


def grid(e0: Fr, rho: Fr) -> list[Fr]:
    return [e0 - rho + 2 * rho * Fr(g, GRID) for g in range(GRID + 1)]


def violations(sysm: MC.ChainSystem, rig: MC.Rigorous, res: dict, *, sample=None) -> list[str]:
    out: list[str] = []
    comp = res["components"]
    P = rig.P
    e0, rho = rig.e0, rig.rho
    up = upper_fraction

    def objects(tr, which: str, tag: str):
        def chk(node, cand, true_vec):
            if node not in comp or comp[node][which] is None:
                return
            err = MC.vnorm(MC.vsub(cand, true_vec))
            if err > up(comp[node][which]):
                out.append(f"{tag} {which} {node}: error {float(err):.3e} > bound {float(up(comp[node][which])):.3e}")
        for r in range(5):
            chk(f"F:{r}:3", P["G", r, 0], tr[("F", r)][3])
        for (r, j) in W_INDICES:
            chk(f"W:{r}:{j}:3", P["W", (r, j), 3], tr[("W", (r, j))][3])
        for j in range(1, 5):
            chk(f"h:{j}:3", P["h", j, 3], tr[("h", j)][3])
        for r in range(5):
            chk(f"S:{r}:3", P["S", r, 3], tr[("S", r)][3])
        chk("Sclosed:3", P["Sclosed", 0, 3], tr[("S", 0)][3])

    tr0 = sysm.truth(e0)
    objects(tr0, "eps_mid", "e0")
    for m in M_VALUES:
        v = res["m"][m]
        t = sysm.true_R(e0, m, 3, tr0)
        if not v["R3_mid"][0] <= t <= v["R3_mid"][1]:
            out.append(f"e0 R3_mid m={m}")
    points = grid(e0, rho) if sample is None else sample
    for e in points:
        tr = sysm.truth(e)
        objects(tr, "kept", f"e={e}")
        for m in M_VALUES:
            v = res["m"][m]
            t = sysm.true_R(e, m, 3, tr)
            L, U = v["R3_cell"]
            if not L <= t <= U:
                out.append(f"e={e} export m={m}: truth {float(t):.6e} not in [{float(L):.6e}, {float(U):.6e}]")
    return out


def truth_range(sysm: MC.ChainSystem, e0: Fr, rho: Fr, m: int) -> tuple[Fr, Fr]:
    vals = [sysm.true_R(e, m, 3) for e in grid(e0, rho)]
    return min(vals), max(vals)
