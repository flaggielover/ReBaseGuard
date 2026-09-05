"""Wire the certified CUSUM residuals into the frozen dependency DAG and produce
the certified all-m enclosures, curvature and complete cover ledger for one cell.

The DAG is traversed TWICE with identical topology:

    which = "delta_mid"   midpoint residuals  -> R_interval, D_interval  (order 0, 1)
    which = "delta_cell"  whole-cell residuals -> H, W'' chain           (order 2)

so the curvature obligation never borrows a midpoint bound, exactly as
ERROR_ALGEBRA section 3 requires ("All quantities on this right-hand side must be
uniform cell bounds, not the midpoint versions used for R_interval and
D_interval").
"""
from __future__ import annotations

from fractions import Fraction as F
from math import comb

from flint import arb

import assembly
import cusum_layer1 as L1
import depgraph
import ledger
import refine
import spec
from intervals import exact, mag_fraction

ORDER_OWNER = {0: "source_dependency_value",
               1: "derivative_source_dependency",
               2: "curvature_envelope"}
W_OWNER = {0: "finite_kernel_chain_value",
           1: "finite_derivative_chain",
           2: "curvature_envelope"}


def _source_node(r: int, k: int) -> str:
    """F/D/H consume the CLOSED FORM source for r=0 and the candidate otherwise."""
    return f"Sclosed:{k}" if r == 0 else f"S:{r}:{k}"


def propagate(cert, which: str) -> depgraph.ErrorDAG:
    """Complete order-0/1/2 error propagation over the frozen DAG."""
    res = cert.residuals
    dag = depgraph.ErrorDAG(C=exact(cert.C), norms=cert.norms)
    k_ = cert.norms["k"]
    j_ = cert.norms["j"]

    def d(key):
        return res[key][which]

    # ---- h_1: closed form, no incoming propagation edge
    for k in range(3):
        nid = f"h:1:{k}"
        dag.local(nid, d(f"h_1:{k}"), owner=ORDER_OWNER[k], order=k)
        dag.set(nid, dag._locals[nid])

    # ---- h_j = sum_i C(k,i) K_i h_(j-1)
    for j in range(2, 5):
        for k in range(3):
            lid = f"local:h:{j}:{k}"
            dag.local(lid, d(f"h_{j}:{k}"), owner=ORDER_OWNER[k], order=k)
            terms = [(comb(k, i), k_[i], f"h:{j - 1}:{k - i}") for i in range(k + 1)]
            dag.operator_sum(f"h:{j}:{k}", k, lid, terms, owner=ORDER_OWNER[k])

    # ---- S_0: closed form (exact source) and its degree-12 candidate
    for k in range(3):
        nid = f"Sclosed:{k}"
        dag.local(nid, d(f"Sclosed_{k}"), owner=ORDER_OWNER[k], order=k)
        dag.set(nid, dag._locals[nid])
        cid = f"S:0:{k}"
        dag.local(cid, d(f"S_0:{k}"), owner=ORDER_OWNER[k], order=k)
        dag.set(cid, dag._locals[cid])

    # ---- S_r = sum_i C(k,i) J_i h_r
    for r in range(1, 5):
        for k in range(3):
            lid = f"local:S:{r}:{k}"
            dag.local(lid, d(f"S_{r}:{k}"), owner=ORDER_OWNER[k], order=k)
            terms = [(comb(k, i), j_[i], f"h:{r}:{k - i}") for i in range(k + 1)]
            dag.operator_sum(f"S:{r}:{k}", k, lid, terms, owner=ORDER_OWNER[k])

    # ---- resolvent chain: value, derivative, curvature
    for r in range(5):
        lid = f"local:F:{r}"
        dag.local(lid, d(f"F_{r}"), owner="F_equation_certificate_value", order=0)
        dag.resolvent_value(f"F:{r}", lid, [_source_node(r, 0)])
    for r in range(5):
        lid = f"local:D:{r}"
        dag.local(lid, d(f"dF_{r}"), owner="dF_equation_certificate", order=1)
        dag.resolvent_derivative(f"D:{r}", lid, f"F:{r}", [_source_node(r, 1)])
    for r in range(5):
        lid = f"local:H:{r}"
        dag.local(lid, d(f"H_{r}"), owner="curvature_envelope", order=2)
        dag.resolvent_curvature(f"H:{r}", lid, f"F:{r}", f"D:{r}", [_source_node(r, 2)])

    # ---- finite kernel powers W_(r,j) = K^j S_r
    for r in range(4):
        for k in range(3):
            dag.set(f"W:{r}:0:{k}", dag.get(f"S:{r}:{k}"))
    for (r, j) in L1.W_INDICES:
        for k in range(3):
            lid = f"local:W:{r}:{j}:{k}"
            dag.local(lid, d(f"W_{r}_{j}:{k}"), owner=W_OWNER[k], order=k)
            terms = [(comb(k, i), k_[i], f"W:{r}:{j - 1}:{k - i}") for i in range(k + 1)]
            dag.operator_sum(f"W:{r}:{j}:{k}", k, lid, terms, owner=W_OWNER[k])
    return dag


def enclosures(cert, mid: depgraph.ErrorDAG, cell: depgraph.ErrorDAG,
               refined: dict | None = None) -> dict:
    """Certified object enclosures at x0, per derivative order."""
    F_vals = {r: assembly.enclose(cert.origin(("F", r, 0)), mid.get(f"F:{r}"))
              for r in range(5)}
    D_vals = {r: assembly.enclose(cert.origin(("D", r, 0)), mid.get(f"D:{r}"))
              for r in range(5)}
    eps_H = (refined or {}).get("eps", {})
    H_vals = {r: assembly.enclose(cert.origin(("H", r, 0)),
                                  eps_H.get(f"H:{r}", cell.get(f"H:{r}")))
              for r in range(5)}
    W = {}
    for order, dag in ((0, mid), (1, mid), (2, cell)):
        W[order] = {}
        for r in range(4):
            for j in range(0, 4 - r):
                W[order][(r, j)] = assembly.enclose(
                    cert.origin(("W", (r, j), order)), dag.get(f"W:{r}:{j}:{order}"))
    return {"F": F_vals, "D": D_vals, "H": H_vals, "W": W}


def cell_obligations(cert, *, ms=None) -> dict:
    """Everything the frozen ledger needs for one cell, for every requested m."""
    ms = spec.M_VALUES if ms is None else ms
    cert.all_residuals()
    mid = propagate(cert, "delta_mid")
    cellwise = propagate(cert, "delta_cell")
    refined = refine.refine(cert, mid, cellwise)
    enc = enclosures(cert, mid, cellwise, refined)
    C = F(cert.C)
    out = {"detector": "CUSUM", "cell_index": cert.cell["index"],
           "e0": cert.cell["e0"], "rho": cert.cell["rho"],
           "C_upper": cert.cell["C_upper"], "precision_bits": cert.bits,
           "dag_audit_mid": mid.audit(), "dag_audit_cell": cellwise.audit(),
           "whole_cell_refinement": refined["audit"], "m": {}}
    for m in ms:
        R_int = assembly.assemble(m, enc["F"], enc["W"][0])
        D_int = assembly.assemble(m, enc["D"], enc["W"][1])
        R2_int = assembly.assemble(m, enc["H"], enc["W"][2])
        M_R2 = assembly.curvature_bound(R2_int)

        # --- exact ledger usage, ERROR_ALGEBRA section 6
        u_cand = F(0)
        ch_eq = ch_tr = F(0)
        for r in range(m):
            r_ = cert.residuals[f"F_{r}"]
            u_cand += C * _up(r_["delta_mid"]) / m
            ch_eq += C * _up(r_["polynomial_residual"]) / m
            ch_tr += C * _up(r_["truncation_allowance"]) / m
        u_kernel = F(0)
        for r in range(m):
            u_kernel += C * _up(mid.get(_source_node(r, 0))) / m
        for t in range(1, m):
            for r in range(t):
                u_kernel += (F(1, t) - F(1, m)) * _up(mid.get(f"W:{r}:{t - r - 1}:0"))
        eta_interval = _up(assembly.assembly_arithmetic_excess(
            m, enc["F"], enc["W"][0], R_int))
        usage = {"B_candidate": u_cand, "B_kernel": u_kernel,
                 "B_interval": eta_interval, "B_rounding": F(0), "B_other": F(0)}
        channels = {"eq": ch_eq, "trunc": ch_tr,
                    "tail": F(0), "end": F(0), "int": F(0), "round": F(0)}
        led = ledger.cell_ledger(m=m, cell=cert.cell, R_interval=R_int,
                                 D_interval=D_int, M_R2=M_R2, usage=usage,
                                 candidate_channels=channels)
        led["channel_provenance"] = {
            "tail": "INCLUDED_IN eq: the recentred Bernstein range bound is taken "
                    "over the complete reachable continuum, with no sampled grid "
                    "and no truncated state tail",
            "end": "INCLUDED_IN eq: the CUSUM raw certificate has no patch/panel "
                   "endpoint decomposition; there is no separate endpoint sliver",
            "int": "INCLUDED_IN trunc: quadrature/series interval error is inside "
                   "the certified Taylor allowance",
            "round": "INCLUDED_IN eq: Arb outward rounding is inside every ball",
            "B_rounding": "0: certified endpoints export exactly as dyadic "
                          "rationals; no value-export rounding occurs",
        }
        led["R_interval"] = _rec(R_int)
        led["D_interval"] = _rec(D_int)
        led["R2_interval"] = _rec(R2_int)
        out["m"][m] = led
    out["objects"] = {
        name: {"delta_mid": str(_up(v["delta_mid"])),
               "delta_cell": str(_up(v["delta_cell"])),
               "envelope": str(_up(v["envelope"])),
               "cpu_seconds": v.get("cpu_seconds", 0.0),
               "bernstein_calls": v.get("bernstein_calls", 0),
               "kernel_calls": v.get("kernel_calls", 0)}
        for name, v in cert.residuals.items()}
    out["eps_mid"] = {k: str(_up(v)) for k, v in mid.nodes.items()}
    out["eps_cell"] = {k: str(_up(v)) for k, v in cellwise.nodes.items()}
    out["eps_cell_refined"] = {k: str(_up(v)) for k, v in refined["eps"].items()}
    out["work"] = {"bernstein_calls": cert.bernstein_calls,
                   "kernel_calls": cert.kernel_calls}
    return out


def _up(x: arb) -> F:
    return mag_fraction(x)


def _rec(x: arb) -> dict:
    from intervals import record
    return record(x)
