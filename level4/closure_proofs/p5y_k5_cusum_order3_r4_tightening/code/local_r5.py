"""R4-C: local first-cell R^(5) majorant by exact-parity local anchoring (hull [0, x1] only; no whole-cell run).

Needs only what a certified POINT run at e = 0 produces (candidate suprema, graded point errors) plus the certified
operator constants; the R3 graded tower (r5_majorant.true_tower, unchanged) is re-anchored until a fixed number of
iterations. Every iterate is a valid bound.

LEMMA (local anchor). Let X be a true object of order n <= 3 with exact parity s = s_base (-1)^n at e = 0 (h even,
S, F, W odd; theorem of R2/R3), P_r the projection onto parity s and P_w the other one. For e in [0, x1]:
  (a) P_w X^(n)(0) = 0 exactly, so ||P_w X^(n)(e)|| <= e sup_[0,e] ||P_w X^(n+1)||;
  (b) ||P_r X^(n)(e)|| <= ||P_r X^(n)(0)|| + e sup_[0,e] ||P_r X^(n+1)||
                      <= ||P_r cand|| + ||P_r (X^(n)(0) - cand)|| + x1 sup ||P_r X^(n+1)||;
  (c) ||X^(n)(e)|| <= (a) + (b).
The sup ||P X^(n+1)|| are components of the current graded tower on the hull (valid by R3); the point error is the
graded point-run error at e = 0. A componentwise minimum of valid bounds is valid, so by induction every iterate
(anchors_k = min(anchors_(k-1), local(tower_(k-1))), tower_k = true_tower(anchors_k)) is a valid tower, and
M5 = sum |c| sup ||P_e F^(5)|| (R3 semantics: only the even part survives at the sigma-fixed x0) is a certified
absolute majorant of sup_[0,x1] |R^(5)|.
"""
from __future__ import annotations

import sys
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
CP = NS.parents[0]
for _p in (str(CP / "p5y_k5_cusum_order3_r3_infrastructure/code"), str(CP / "p5y_k5_cusum_order3_r2_repair/code"),
           str(CP / "p5y_k5_cusum_order3_real_producer/code")):
    if _p not in sys.path:
        sys.path.append(_p)

import graded_dag as G  # noqa: E402
import r5_majorant as R5  # noqa: E402
import rung3_engine as R1E  # noqa: E402

BASE_PARITY = {"h": 1, "S": -1, "F": -1, "W": -1}
ITERATIONS = 12


class LocalR5Refusal(RuntimeError):
    pass


def node_parity(node: str) -> int:
    return BASE_PARITY[node.split(":")[0]] * (-1) ** int(node.split(":")[-1])


def next_order(node: str) -> str:
    parts = node.split(":")
    parts[-1] = str(int(parts[-1]) + 1)
    return ":".join(parts)


def local_anchor(node, cand, err, tower, x1):
    """Lemma (a)-(c) for one node. cand, err: graded (e, o) pairs of arb; tower: graded tower (valid)."""
    nxt = tower[next_order(node)]
    if node_parity(node) == 1:
        e = cand[0] + err.e + x1 * nxt.e
        o = x1 * nxt.o
    else:
        o = cand[1] + err.o + x1 * nxt.o
        e = x1 * nxt.e
    return G.V(e, o, e + o)


def local_tower(base: dict, candidates: dict, point_nodes: dict, *, x1, r5=R5, iterations: int = ITERATIONS,
                start_anchors: dict | None = None) -> dict:
    """base: true_tower inputs without anchors (C, C_e0, C_o0, k, j hull norms, eta = x1, S0, optional h1).
    candidates: {node: (sup ||P_e cand||, sup ||P_o cand||)} for anchored nodes (orders <= 3);
    point_nodes: graded point-run errors at e = 0 {node: V}."""
    for key in ("C", "C_e0", "C_o0", "k", "j", "eta", "S0"):
        if key not in base:
            raise LocalR5Refusal(f"missing tower input {key}")
    if not candidates:
        raise LocalR5Refusal("no candidate suprema")
    missing = [n for n in candidates if n not in point_nodes]
    if missing:
        raise LocalR5Refusal(f"candidate without point error: {missing[:3]}")
    if any(int(n.split(":")[-1]) > 3 for n in candidates):
        raise LocalR5Refusal("anchors are restricted to orders <= 3")
    anchors = dict(start_anchors or {})
    tower = r5.true_tower(dict(base, anchors=anchors), parity=True)["towers"]
    trace = [R1E.fraction_of(r5.m5(tower)[1].abs_upper())]
    for _ in range(iterations):
        new = {}
        for node, cand in candidates.items():
            a = local_anchor(node, cand, point_nodes[node], tower, x1)
            new[node] = R5._minv(a, anchors[node]) if node in anchors else a
        anchors = new
        tower = r5.true_tower(dict(base, anchors=anchors), parity=True)["towers"]
        trace.append(R1E.fraction_of(r5.m5(tower)[1].abs_upper()))
    return {"towers": tower, "anchors": anchors, "M5": r5.m5(tower, parity=True), "trace_m1": trace}
