"""The complete SR raw-variable object DAG, derived from the frozen assembly table.

Nothing here is hand-listed that can be derived: the W index set, the m-ownership
and the top-level obligation mapping are all computed from the frozen
`assembly.coefficients` and `universe.work_ids`, so the DAG cannot drift from the
frozen scope. Structural only -- no numerics.

Node identity is the canonical string used everywhere downstream:

    K            kernel operator, order k          -> "op:K:k{K}"
    h_j^(k)      reward chain                      -> "h:{j}:k{K}"
    S_r^(k)      source chain                      -> "S:{r}:k{K}"
    W_(r,j)^(k)  finite kernel power K^j S_r       -> "W:{r},{j}:k{K}"
    F_r/D_r/H_r  resolvent solutions, order 0/1/2  -> "F:{r}:k{K}"
    R_m^(k)      assembled target                  -> "R:{m}:k{K}"
    M_R2_m       whole-cell curvature magnitude    -> "M_R2:{m}"
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
ROOT = NS.parents[2]
IMPL = ROOT / "level4/closure_proofs/p5y_k1_cover_ledger_implementation/code"
SPECC = ROOT / "level4/closure_proofs/p5y_k1_cover_ledger_successor/code"
for _p in (str(IMPL), str(SPECC)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import spec                                                        # noqa: E402
import assembly                                                    # noqa: E402
import universe                                                    # noqa: E402

ORDERS = (0, 1, 2)
R_MAX = 5                     # S_0..S_4, F_0..F_4, dF_0..dF_4
H_MAX = 4                     # h_1..h_4
DETECTOR = "SR"

# Owner tags are the frozen ledger claimant owners (spec.CLAIMANT_OWNERS keys).
OWNER = {
    0: {"h": "finite_kernel_chain_value", "S": "source_dependency_value",
        "W": "finite_kernel_chain_value", "F": "F_equation_certificate_value",
        "R": "value_assembly_arithmetic_not_in_certificate"},
    1: {"h": "finite_derivative_chain", "S": "derivative_source_dependency",
        "W": "finite_derivative_chain", "F": "dF_equation_certificate",
        "R": "derivative_arithmetic"},
    2: {"h": "finite_derivative_chain", "S": "derivative_source_dependency",
        "W": "finite_derivative_chain", "F": "curvature_envelope",
        "R": "curvature_envelope"},
}


def w_indices() -> list[tuple[int, int]]:
    """(r, j) pairs actually consumed, derived from the frozen coefficient table."""
    idx = set()
    for m in spec.M_VALUES:
        for kind, r, j, _c in assembly.coefficients(m):
            if kind == "W":
                idx.add((r, j))
    return sorted(idx)


def m_owners_of_w(r: int, j: int) -> list[int]:
    return sorted(m for m in spec.M_VALUES
                  if any(k == "W" and rr == r and jj == j
                         for k, rr, jj, _ in assembly.coefficients(m)))


def m_owners_of_f(r: int) -> list[int]:
    return sorted(m for m in spec.M_VALUES
                  if any(k == "F" and rr == r for k, rr, _j, _ in assembly.coefficients(m)))


def build() -> dict:
    W = w_indices()
    nodes: dict[str, dict] = {}

    def add(nid, *, cls, order, deps, source, error_algebra, owner,
            r=None, j=None, m=None, cert):
        if nid in nodes:
            raise ValueError(f"duplicate node identity {nid}")
        nodes[nid] = {
            "id": nid, "class": cls, "derivative_order": order,
            "r_index": r, "j_index": j, "m_ownership": m,
            "dependencies": deps, "exact_source": source,
            "error_algebra": error_algebra, "owner": owner,
            "certificate_output": cert,
        }

    # ---- operators. K' and K'' are EXACT finite combinations of the frozen triple.
    add("op:K:k0", cls="operator", order=0, deps=[], m=list(spec.M_VALUES),
        source="EXACT_SR_TARGET.md s3: (K_e f)(y) = int_l^u f(q_SR(y,z)) phi(z+e) dz",
        error_algebra="panel enclosure; norm k0 = ||K_e||", owner="finite_kernel_chain_value",
        cert="operator norm bound k0")
    add("op:Kz:k0", cls="operator", order=0, deps=[], m=list(spec.M_VALUES),
        source="EXACT_SR_TARGET.md s3: (K_z,e f)(y) = int_l^u z f(q_SR) phi(z+e) dz",
        error_algebra="panel enclosure", owner="finite_kernel_chain_value",
        cert="operator norm bound")
    add("op:Kz2:k0", cls="operator", order=0, deps=[], m=list(spec.M_VALUES),
        source="EXACT_SR_TARGET.md s3: (K_z2,e f)(y) = int_l^u z^2 f(q_SR) phi(z+e) dz",
        error_algebra="panel enclosure", owner="finite_kernel_chain_value",
        cert="operator norm bound")
    add("op:K:k1", cls="operator", order=1, deps=["op:Kz:k0", "op:K:k0"], m=list(spec.M_VALUES),
        source="SR_DERIVATION.md s3: K' = -(K_z,e + e K_e)  [l,u are e-free]",
        error_algebra="exact operator identity; norm k1 = ||K'||",
        owner="finite_derivative_chain", cert="operator norm bound k1")
    add("op:K:k2", cls="operator", order=2, deps=["op:Kz2:k0", "op:Kz:k0", "op:K:k0"],
        m=list(spec.M_VALUES),
        source="SR_DERIVATION.md s3: K'' = K_z2,e + 2e K_z,e + (e^2-1) K_e",
        error_algebra="exact operator identity; norm k2 = ||K''||",
        owner="finite_derivative_chain", cert="operator norm bound k2")
    add("op:Kz:k1", cls="operator", order=1, deps=["op:Kz2:k0", "op:Kz:k0"], m=list(spec.M_VALUES),
        source="SR_DERIVATION.md s3: K_z' = -(K_z2,e + e K_z,e)",
        error_algebra="exact operator identity", owner="finite_derivative_chain",
        cert="operator norm bound")
    add("op:resolvent", cls="operator", order=0, deps=["op:K:k0"], m=list(spec.M_VALUES),
        source="C = ||(I - K_e)^{-1}||, frozen depgraph.ErrorDAG.C",
        error_algebra="resolvent norm; multiplies every F/D/H bound",
        owner="F_equation_certificate_value", cert="C")

    # ---- reward chain h_j, orders 0..2
    for k in ORDERS:
        for jj in range(1, H_MAX + 1):
            if jj == 1:
                deps = ["op:K:k%d" % k] if k > 0 else ["op:K:k0"]
                src = ("h_1 = 1 - K_e 1" if k == 0 else
                       "h_1' = -K' 1" if k == 1 else "h_1'' = -K'' 1")
            else:
                deps = [f"h:{jj-1}:k{kk}" for kk in range(k + 1)] + \
                       [f"op:K:k{kk}" for kk in range(k + 1)]
                src = {0: f"h_{jj} = K_e h_{jj-1}",
                       1: f"h_{jj}' = K' h_{jj-1} + K h_{jj-1}'",
                       2: f"h_{jj}'' = K'' h_{jj-1} + 2K' h_{jj-1}' + K h_{jj-1}''"}[k]
            add(f"h:{jj}:k{k}", cls="reward_chain", order=k, r=jj, m=list(spec.M_VALUES),
                deps=deps, source=src,
                error_algebra="Leibniz operator-sum rule: epsY <= lY + sum |b_i| ||T_i|| epsX_i",
                owner=OWNER[k]["h"],
                cert=("top-level object h_%d" % jj) if k == 0 else "dependency_bundle order %d" % k)

    # ---- source chain S_r, orders 0..2
    for k in ORDERS:
        for r in range(R_MAX):
            if r == 0:
                deps = []
                src = {0: "S_0 = rho_{1,e} (closed form)",
                       1: "S_0' = rho_{1,e}' (closed form, SR_DERIVATION s4)",
                       2: "S_0'' = rho_{1,e}'' (closed form, SR_DERIVATION s4)"}[k]
            else:
                deps = [f"h:{r}:k{kk}" for kk in range(k + 1)] + \
                       [f"op:Kz:k{kk}" for kk in range(min(k, 1) + 1)]
                src = {0: f"S_{r} = K_z,e h_{r}",
                       1: f"S_{r}' = K_z' h_{r} + K_z h_{r}'",
                       2: f"S_{r}'' = K_z'' h_{r} + 2 K_z' h_{r}' + K_z h_{r}''"}[k]
            add(f"S:{r}:k{k}", cls="source_chain", order=k, r=r, m=list(spec.M_VALUES),
                deps=deps, source=src,
                error_algebra="closed-form enclosure (r=0) / Leibniz operator-sum rule",
                owner=OWNER[k]["S"],
                cert=("top-level object S_%d" % r) if k == 0 else "dependency_bundle order %d" % k)

    # ---- finite kernel powers W_(r,j) = K^j S_r
    for k in ORDERS:
        for (r, jj) in W:
            if jj == 0:
                deps = [f"S:{r}:k{k}"]
                src = f"W_({r},0) = S_{r}"
            else:
                deps = [f"W:{r},{jj-1}:k{kk}" for kk in range(k + 1)] + \
                       [f"op:K:k{kk}" for kk in range(k + 1)]
                src = {0: f"W_({r},{jj}) = K W_({r},{jj-1})",
                       1: f"W'_({r},{jj}) = K W'_({r},{jj-1}) + K' W_({r},{jj-1})",
                       2: (f"W''_({r},{jj}) = K W''_({r},{jj-1}) + 2K' W'_({r},{jj-1})"
                           f" + K'' W_({r},{jj-1})")}[k]
            add(f"W:{r},{jj}:k{k}", cls="finite_power", order=k, r=r, j=jj,
                m=m_owners_of_w(r, jj), deps=deps, source=src,
                error_algebra="frozen Leibniz recurrence depgraph: epsW_next,k <= l_k + sum",
                owner=OWNER[k]["W"],
                cert="dependency_bundle (finite kernel powers)")

    # ---- resolvent solutions F_r (k0), D_r (k1), H_r (k2)
    for r in range(R_MAX):
        add(f"F:{r}:k0", cls="resolvent", order=0, r=r, m=m_owners_of_f(r),
            deps=["op:resolvent", f"S:{r}:k0", "h:1:k0"],
            source="RAW-VARIABLE: (I - K_e) F_r = S_r + e * h_1   [SR_DERIVATION s2]",
            error_algebra="epsF_r = C (deltaF_r + epsS_r)",
            owner=OWNER[0]["F"], cert=f"top-level object F_{r}")
        add(f"F:{r}:k1", cls="resolvent", order=1, r=r, m=m_owners_of_f(r),
            deps=["op:resolvent", f"F:{r}:k0", "op:K:k1", f"S:{r}:k1", "h:1:k0", "h:1:k1"],
            source="(I - K_e) D_r = K' F_r + S_r' + h_1 + e h_1'   [SR_DERIVATION s4]",
            error_algebra="epsD_r = C (deltaD_r + k1 epsF_r + epsS1_r)",
            owner=OWNER[1]["F"], cert=f"top-level object dF_{r}")
        add(f"F:{r}:k2", cls="resolvent", order=2, r=r, m=m_owners_of_f(r),
            deps=["op:resolvent", f"F:{r}:k0", f"F:{r}:k1", "op:K:k1", "op:K:k2",
                  f"S:{r}:k2", "h:1:k1", "h:1:k2"],
            source="(I - K_e) H_r = K'' F_r + 2 K' D_r + S_r'' + 2 h_1' + e h_1''",
            error_algebra="epsH_r = C (deltaH_r + k2 epsF_r + 2 k1 epsD_r + epsS2_r)  [whole cell]",
            owner=OWNER[2]["F"], cert="curvature bundle input (not a separate top-level object)")

    # ---- assembly R_m^(k) and M_R2
    for m in spec.M_VALUES:
        terms = assembly.coefficients(m)
        for k in ORDERS:
            deps = []
            for kind, r, jj, _c in terms:
                deps.append(f"F:{r}:k{k}" if kind == "F" else f"W:{r},{jj}:k{k}")
            add(f"R:{m}:k{k}", cls="assembly", order=k, m=[m], deps=sorted(set(deps)),
                source=("R_m^(k) = (1/m) sum_{r<m} F_r^(k) + sum_t c_(m,t) "
                        "sum_{r<t} W_(r,t-r-1)^(k),  c_(m,t) = 1/t - 1/m"),
                error_algebra=("exact rational coefficients through Arb division; "
                               "assembly_arithmetic_excess -> B_interval"),
                owner=OWNER[k]["R"],
                cert={0: f"assembly unit m={m} (R_interval)",
                      1: f"assembly unit m={m} (D_interval)",
                      2: f"curvature unit m={m} (R2_interval)"}[k])
        add(f"M_R2:{m}", cls="curvature", order=2, m=[m], deps=[f"R:{m}:k2"],
            source="M_R2 = mag(R2_interval) >= sup_{e in cell} |R''_(D,m)(e)|  [assembly.curvature_bound]",
            error_algebra="magnitude of the order-2 whole-cell enclosure; not re-charged",
            owner="curvature_envelope", cert=f"curvature obligation m={m}")
        add(f"cover:{m}", cls="cover", order=2, m=[m],
            deps=[f"R:{m}:k0", f"R:{m}:k1", f"M_R2:{m}"],
            source=("W_cover_exact = rho * mag(D_interval) + rho^2 * M_R2 / 2 "
                    "[ledger.cover_charge]"),
            error_algebra="STYLE_1: derivative uncertainty is inside D_interval exactly once",
            owner="cover_arithmetic", cert=f"B_cover utilisation m={m}")

    return {"schema": "k1.sr.dag.v1", "detector": DETECTOR,
            "cells": spec.COUNTS["SR"], "m_values": list(spec.M_VALUES),
            "w_indices": [list(x) for x in W], "nodes": nodes}


# --------------------------------------------------------------------- audit
def audit(dag: dict) -> dict:
    nodes = dag["nodes"]
    findings, ok = [], True

    missing = sorted({d for n in nodes.values() for d in n["dependencies"]} - set(nodes))
    if missing:
        ok = False
        findings.append(f"dangling dependencies: {missing[:6]}")

    dup = [nid for nid, n in nodes.items()
           if len(n["dependencies"]) != len(set(n["dependencies"]))]
    if dup:
        ok = False
        findings.append(f"duplicate edges: {dup[:6]}")

    # topological sort -> acyclicity
    colour, order_out, cycles = {}, [], []

    def visit(nid, stack):
        c = colour.get(nid, 0)
        if c == 1:
            cycles.append(stack[stack.index(nid):] + [nid])
            return
        if c == 2:
            return
        colour[nid] = 1
        for d in nodes[nid]["dependencies"]:
            if d in nodes:
                visit(d, stack + [d])
        colour[nid] = 2
        order_out.append(nid)

    sys.setrecursionlimit(10000)
    for nid in nodes:
        visit(nid, [nid])
    if cycles:
        ok = False
        findings.append(f"cycles: {cycles[:2]}")

    # every dependency must precede its consumer in the topological order
    pos = {nid: i for i, nid in enumerate(order_out)}
    bad = [(nid, d) for nid, n in nodes.items() for d in n["dependencies"]
           if d in pos and pos[d] > pos[nid]]
    if bad:
        ok = False
        findings.append(f"order violation: {bad[:4]}")

    # order-k node may not depend on an order-(k+1) node
    inversion = [(nid, d) for nid, n in nodes.items() for d in n["dependencies"]
                 if d in nodes and nodes[d]["derivative_order"] > n["derivative_order"]]
    if inversion:
        ok = False
        findings.append(f"derivative-order inversion: {inversion[:4]}")

    # the DAG must cover exactly the frozen SR top-level obligation classes
    sr_ids = [w for w in universe.work_ids() if w[0] == "SR"]
    per_cell = sorted({(w[2], w[3]) for w in sr_ids if w[1] >= 0})
    covered = set()
    for n in nodes.values():
        c = n["certificate_output"]
        if c.startswith("top-level object "):
            covered.add(("object", c.split()[-1]))
        elif c.startswith("assembly unit m="):
            covered.add(("assembly", c.split("=")[1].split()[0]))
        elif c.startswith("curvature obligation m="):
            covered.add(("curvature", c.split("=")[1]))
        elif c.startswith("dependency_bundle"):
            covered.add(("dependency_bundle", "orders_0_1"))
    expect = set(per_cell)
    if covered != expect:
        ok = False
        findings.append(f"obligation cover mismatch: missing {sorted(expect-covered)} "
                        f"extra {sorted(covered-expect)}")

    # the top-level universe must not have moved
    universe_ok = len(universe.work_ids()) == spec.TOTAL_UNITS == 17978
    if not universe_ok:
        ok = False
        findings.append("top-level universe changed")

    return {"ok": ok, "findings": findings, "n_nodes": len(nodes),
            "n_edges": sum(len(n["dependencies"]) for n in nodes.values()),
            "topological_order_len": len(order_out),
            "obligation_classes_covered": sorted(covered),
            "sr_top_level_obligations": len(sr_ids),
            "universe_preserved": universe_ok}


if __name__ == "__main__":
    d = build()
    a = audit(d)
    out = NS / "config/sr_dag.json"
    out.write_text(json.dumps({**d, "audit": a}, indent=1, sort_keys=True) + "\n")
    print(json.dumps(a, indent=1))
    print("written:", out)
