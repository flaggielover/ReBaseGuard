"""PHASE 2: propagation with EXPLICIT dependency injection.

WHY THIS MODULE EXISTS
----------------------
The predecessor redirected the scientific behaviour of a reviewed module by
assigning into it at runtime:

    propagate.refine = sys.modules[__name__]         # rejected

That makes the scientific call graph depend on import order and on which module
last performed an assignment; it cannot be read off the source, and a reader of
`propagate.py` sees the wrong callee. This module replaces that with ordinary
wiring: the refinement backends are CONSTRUCTED by the caller and PASSED IN, and
every callee is named at its call site.

    aux_qualify -> cell_obligations(cert,
                                    whole_cell_refinement=refine2.refine,
                                    node_refinement=AuxiliaryRefinement(...))

Nothing is assigned into an imported module anywhere in this namespace, and
`tests/test_aux3.py` fails if any is.

WHAT IS REPRODUCED EXACTLY
--------------------------
`cell_dag` mirrors the reviewed `propagate.propagate` node for node, edge for
edge, owner for owner: same topology, same coefficients, same operator norms,
same ownership tags, same charge sites. With `node_refinement=None` it must
produce bit-identical node values to the reviewed function, and a test asserts
exactly that on a real cell. The only addition is one call per node, AFTER the
frozen cascade value has been computed, which may replace that value with a
smaller certified one and records the decision.

`cell_obligations` likewise mirrors the reviewed orchestration -- the same two
DAG traversals, the same enclosures, the same exact ledger usage, the same
channel provenance -- with the refinement dependencies passed rather than
patched, and the auxiliary evidence recorded in the returned record.
"""
from __future__ import annotations

from fractions import Fraction as F
from math import comb

import ancestry                                                 # noqa: F401

from flint import arb                                           # noqa: E402

import assembly                                                 # noqa: E402
import cusum_layer1 as L1                                       # noqa: E402
import depgraph                                                 # noqa: E402
import ledger                                                   # noqa: E402
import propagate as reviewed                                    # noqa: E402
import spec                                                     # noqa: E402
from intervals import exact, mag_fraction, tight_upper          # noqa: E402

ORDER_OWNER = reviewed.ORDER_OWNER
W_OWNER = reviewed.W_OWNER
_source_node = reviewed._source_node


def cell_dag(cert, which: str) -> depgraph.ErrorDAG:
    """The frozen order-0/1/2 error DAG: a node-for-node mirror of the reviewed
    `propagate.propagate`, with the same topology, coefficients, norms, owners
    and charge sites. It is never refined in place -- the reviewed DAG refuses to
    reassign a node, and that guard stays intact."""
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


class RefinedCellValues:
    """Whole-cell node values over the frozen topology, with the auxiliary
    Taylor bound applied node by node.

    A DERIVED object, not a mutation: it walks the same topology in the same
    order, reproducing the reviewed DAG's arithmetic exactly

        local node        eps = local
        operator_sum      eps = local + sum_i |c_i| ||T_i|| eps(src_i)
        resolvent value   eps = C (local + sum eps(src))
        resolvent deriv   eps = C (local + k1 eps(F) + sum eps(src))
        resolvent curv    eps = C (local + k2 eps(F) + 2 k1 eps(D) + sum eps(src))

    and takes `min(cascade, Taylor)` at each h/S/W node, so a tightened node
    feeds its dependants. With `refinement=None` the values are bit-identical to
    the DAG's, which `tests/test_aux3.py` asserts on a real cell.
    """

    def __init__(self, cert, dag: depgraph.ErrorDAG, refinement=None):
        self._dag = dag
        self.refinement = refinement
        self.nodes: dict = {}
        self._build(cert, dag, refinement)

    # the reviewed DAG applies tight_upper on every local() and set()
    @staticmethod
    def _store(value):
        return tight_upper(value)

    def _put(self, node, value):
        self.nodes[node] = self._store(value)
        return self.nodes[node]

    def _refined(self, node, value, family, index, order):
        kept = self._store(value)
        if self.refinement is not None:
            kept = self.refinement.bound(family, index, order, node, kept)
        self.nodes[node] = self._store(kept)
        return self.nodes[node]

    def _build(self, cert, dag, refinement):
        loc = dag._locals
        k_ = cert.norms["k"]
        j_ = cert.norms["j"]
        C = exact(cert.C)
        g = self.get

        for k in range(3):
            self._refined(f"h:1:{k}", loc[f"h:1:{k}"], "h", 1, k)
        for j in range(2, 5):
            for k in range(3):
                acc = loc[f"local:h:{j}:{k}"]
                for i in range(k + 1):
                    acc = acc + exact(abs(F(comb(k, i)))) * k_[i] * g(f"h:{j - 1}:{k - i}")
                self._refined(f"h:{j}:{k}", acc, "h", j, k)
        for k in range(3):
            self._put(f"Sclosed:{k}", loc[f"Sclosed:{k}"])
            self._refined(f"S:0:{k}", loc[f"S:0:{k}"], "S", 0, k)
        for r in range(1, 5):
            for k in range(3):
                acc = loc[f"local:S:{r}:{k}"]
                for i in range(k + 1):
                    acc = acc + exact(abs(F(comb(k, i)))) * j_[i] * g(f"h:{r}:{k - i}")
                self._refined(f"S:{r}:{k}", acc, "S", r, k)
        for r in range(5):
            total = loc[f"local:F:{r}"] + g(_source_node(r, 0))
            self._put(f"F:{r}", C * total)
        for r in range(5):
            total = (loc[f"local:D:{r}"] + k_[1] * g(f"F:{r}")
                     + g(_source_node(r, 1)))
            self._put(f"D:{r}", C * total)
        for r in range(5):
            total = (loc[f"local:H:{r}"] + k_[2] * g(f"F:{r}")
                     + arb(2) * k_[1] * g(f"D:{r}") + g(_source_node(r, 2)))
            self._put(f"H:{r}", C * total)
        for r in range(4):
            for k in range(3):
                self._put(f"W:{r}:0:{k}", g(f"S:{r}:{k}"))
        for (r, j) in L1.W_INDICES:
            for k in range(3):
                acc = loc[f"local:W:{r}:{j}:{k}"]
                for i in range(k + 1):
                    acc = acc + exact(abs(F(comb(k, i)))) * k_[i] * g(f"W:{r}:{j - 1}:{k - i}")
                self._refined(f"W:{r}:{j}:{k}", acc, "W", (r, j), k)

    # ---- the read-only surface the reviewed consumers use
    def get(self, node_id: str):
        if node_id not in self.nodes:
            raise depgraph.MissingDependency(f"no certificate for {node_id}")
        return self.nodes[node_id]

    def audit(self) -> dict:
        return self._dag.audit()

    def usage_by_budget(self) -> dict:
        return self._dag.usage_by_budget()


def cell_obligations(cert, *, whole_cell_refinement,
                     node_refinement_factory=None, ms=None) -> dict:
    """Everything the frozen ledger needs for one cell, for every requested m.

    `whole_cell_refinement(cert, mid, crude)` and `node_refinement_factory(cert,
    mid_nodes)` are passed explicitly; nothing is patched. The factory exists
    because the node bound is anchored at the midpoint, so it can only be built
    once the midpoint traversal has run. With both omitted this is the reviewed
    computation.
    """
    ms = spec.M_VALUES if ms is None else ms
    cert.all_residuals()
    mid = cell_dag(cert, "delta_mid")
    node_refinement = (None if node_refinement_factory is None
                       else node_refinement_factory(cert, mid.nodes))
    cellwise_dag = cell_dag(cert, "delta_cell")
    cellwise = (cellwise_dag if node_refinement is None
                else RefinedCellValues(cert, cellwise_dag, node_refinement))
    refined = whole_cell_refinement(cert, mid, cellwise)
    enc = reviewed.enclosures(cert, mid, cellwise, refined)
    C = F(cert.C)
    out = {"detector": "CUSUM", "cell_index": cert.cell["index"],
           "e0": cert.cell["e0"], "rho": cert.cell["rho"],
           "C_upper": cert.cell["C_upper"], "precision_bits": cert.bits,
           "dag_audit_mid": mid.audit(), "dag_audit_cell": cellwise.audit(),
           "whole_cell_refinement": refined["audit"],
           "node_refinement": (None if node_refinement is None
                               else node_refinement.report()),
           "m": {}}
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
