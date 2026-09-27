"""Producer of K5_TAIL_DEPENDENCY_GRAPH.json (machine-readable companion of the .md).

Nodes and edges encode the structure only (no numbers of any target cell). The script checks that
every edge endpoint exists, that the graph is acyclic, that every node reaches Gamma (N30), and runs a
planted-cycle negative control that the acyclicity check must detect.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "code"))
import ov_quarantine as Q  # noqa: E402

Q.install_import_guard()

# id, name, bound, enters, scope, improvable, new_science, frozen_on_r2_path, detail_ref
NODES = [
    ("N1", "cover geometry e0, rho, x_lo, x_hi", "exact", "transport factor rho*x_hi; Taylor radius", "cell", "yes: refine cover", "R+G", True, "A:N1"),
    ("N2", "R_k midpoint enclosure of R(e0)", "two-sided", "g_hi", "cell", "yes: AD Corollary T on the tail", "T-light+G", True, "A:N2"),
    ("N3", "D_k midpoint enclosure of R'(e0)", "two-sided", "g_hi", "cell", "yes: AD Corollary T on the tail", "T-light+G", True, "A:N2"),
    ("N4", "R2_interval / M_R2 (K1 whole-cell)", "two-sided", "cap on M", "cell", "not binding", "-", True, "A:N4"),
    ("N5", "C_upper", "upper", "Lemma G", "cell", "frozen", "R", True, "A:N5"),
    ("N6", "k_i, j_i drift-aware norms", "upper", "Lemma G, f_G, Env4, towers", "cell", "frozen", "R", True, "A:N6"),
    ("N7", "delta_{F,D,H}, eps_src", "upper", "f_F, f_D, f_H", "cell x r", "pointless", "-", True, "A:N7"),
    ("N8", "candidate sups s_F, s_D, s_H", "upper", "f_G, Env4", "cell x r", "yes: composite sup (stream D)", "D+T", True, "A:N8"),
    ("N9", "sup_S0[n]", "upper", "towers, sigma4 r=0", "cell", "-", "-", True, "A:N9"),
    ("N10", "Aux3 order-3 source evidence", "upper", "sigma3, sigma4 via P3'", "cell", "yes", "R", True, "A:N10"),
    ("N11", "centres H_r(a)", "point", "centre", "cell x r", "no", "-", True, "A:N11"),
    ("N12", "W2 enclosures", "two-sided", "centre", "cell", "yes", "R", True, "A:N12"),
    ("N13", "operator constants C_T, tau, Abar, D_lo, D1, D2", "upper/lower block-uniform", "Dv' supply", "cell", "yes: operator certification; LR route", "T", True, "A:N13"),
    ("N14", "kappa1, kappa2", "upper", "Dv' A1, A2", "shared", "negligible", "-", True, "A:N14"),
    ("N15", "g_hi = R.hi - e0 D.lo", "upper", "additive", "cell", "via N2/N3", "T-light+G", True, "A:N15"),
    ("N16", "Lemma G supply A_G", "upper", "min supply", "cell", "-", "-", True, "A:N16"),
    ("N17", "Dv' r2 supply (eff, delta1, delta2)", "upper", "min supply", "cell", "yes (N13), floored by Lambda", "T", True, "A:N17"),
    ("N18", "chosen supply S (componentwise min)", "upper", "rad_r", "cell", "D' mixed not admissible under r2", "G", True, "A:N18"),
    ("N19", "J/h towers", "upper", "sigma3, sigma4", "cell", "yes", "T", True, "A:N19"),
    ("N20", "sigma3", "upper", "f_G", "cell x r", "yes", "R/T", True, "A:N20"),
    ("N21", "sigma4", "upper", "Env4", "cell x r", "yes", "R/T", True, "A:N21"),
    ("N22", "f_F, f_D, f_H", "upper", "p0, p1, p2", "cell x r", "negligible", "-", True, "A:N22"),
    ("N23", "f_G order-3 surrogate (G := 0)", "upper norm-only", "p2 via rho f_G", "cell x r", "yes: real G (R), composite sup (T+D), cancellation (T)", "R/T/D", True, "A:N23"),
    ("N24", "Env4", "upper", "p2 via rho^2 Env4/2", "cell x r", "yes", "T/R", True, "A:N24"),
    ("N25", "p0, p1, p2 Taylor bounds", "upper", "rad_r", "cell x r", "yes: profile p_j(s) (TPT)", "T", True, "A:N25"),
    ("N26", "rad_r = A0 p2 + 2A1 p1 + A2 p0", "upper", "enclosure", "cell x r", "via A, p, TPT, LR", "T", True, "A:N26"),
    ("N27", "assembly coefficients and centre [C_lo, C_hi]", "exact/interval", "enclosure", "cell", "-", "-", True, "A:N27"),
    ("N28", "TC-T enclosure H_5 = [C_lo - S, C_hi + S]", "two-sided", "M", "cell", "via S", "-", True, "A:N28"),
    ("N29", "M = min(M_R2, mag(H cap H_5))", "upper", "transport", "cell", "-", "-", True, "A:N29"),
    ("N30", "Gamma: K5-B direct clause (adoption quantity)", "upper on max g", "-", "cell", "TPT / C5-T transport", "T+G", True, "A:N30"),
    ("N31", "Gamma_C5T", "upper", "scientific clause", "cell", "dominated by TPT", "-", False, "A:N31"),
    ("N32", "chain clause (mu, l, gamma, U)", "upper", "not in adoption quantity", "adjacent cells", "-", "-", False, "A:N32"),
    ("N33", "adoption predicates (floor r2)", "governance", "-", "cell", "-", "G", True, "A:N33"),
    ("N34", "Lemma SM(d) floor Lambda_k", "constraint", "floor on A0 only", "cell", "-", "-", False, "A:N34"),
]
EDGES = [
    ("N1", "N15"), ("N1", "N25"), ("N1", "N30"), ("N2", "N15"), ("N3", "N15"), ("N4", "N29"),
    ("N5", "N16"), ("N6", "N16"), ("N13", "N17"), ("N14", "N17"), ("N16", "N18"), ("N17", "N18"),
    ("N6", "N19"), ("N9", "N19"), ("N10", "N19"), ("N19", "N20"), ("N10", "N20"), ("N19", "N21"),
    ("N10", "N21"), ("N7", "N22"), ("N6", "N23"), ("N8", "N23"), ("N20", "N23"), ("N7", "N23"),
    ("N6", "N24"), ("N8", "N24"), ("N21", "N24"), ("N22", "N25"), ("N23", "N25"), ("N24", "N25"),
    ("N18", "N26"), ("N25", "N26"), ("N11", "N27"), ("N12", "N27"), ("N26", "N28"), ("N27", "N28"),
    ("N28", "N29"), ("N15", "N30"), ("N29", "N30"), ("N15", "N31"), ("N28", "N31"), ("N1", "N31"),
    ("N30", "N33"), ("N13", "N34"),
]
# prospective overlay (new routes of this campaign; none evaluated on any target)
OVERLAY = [
    {"route": "TPT", "replaces": ["N30"], "consumes": ["N15", "N25", "N26", "N27", "N28", "N1"],
     "note": "profile transport; closure-only under floor r2"},
    {"route": "LR", "replaces": ["N17"], "consumes": ["N13"],
     "note": "score-representation A1/A2; closure-only under floor r2"},
    {"route": "RSO", "replaces": ["N26"], "consumes": ["N22"], "note": "pointwise residual majorant; data-blocked"},
    {"route": "SUPNORM", "replaces": ["N23"], "consumes": ["N8"], "note": "composite sup; data-blocked"},
    {"route": "ORDER3_REAL", "replaces": ["N23"], "consumes": ["N8", "N20"], "note": "real G; new real addresses"},
    {"route": "COROLLARY_T_GHI", "replaces": ["N15"], "consumes": ["N2", "N3", "N17"],
     "note": "atom-functional midpoint eps (existing AD Corollary T); closure-only under floor r2"},
]


def acyclic(nodes: list, edges: list) -> bool:
    adj = {n: [] for n in nodes}
    indeg = {n: 0 for n in nodes}
    for a, b in edges:
        adj[a].append(b)
        indeg[b] += 1
    stack = [n for n in nodes if indeg[n] == 0]
    seen = 0
    while stack:
        n = stack.pop()
        seen += 1
        for b in adj[n]:
            indeg[b] -= 1
            if indeg[b] == 0:
                stack.append(b)
    return seen == len(nodes)


def main() -> None:
    ids = [n[0] for n in NODES]
    assert len(set(ids)) == len(ids)
    missing = [e for e in EDGES if e[0] not in ids or e[1] not in ids]
    assert not missing, missing
    ok_dag = acyclic(ids, EDGES)
    neg = acyclic(ids, EDGES + [("N30", "N1")])  # planted cycle must be detected
    # reachability to Gamma (N30) or to the governance/constraint sinks
    rev = {}
    for a, b in EDGES:
        rev.setdefault(b, []).append(a)
    reach, stack = set(), ["N30"]
    while stack:
        n = stack.pop()
        if n in reach:
            continue
        reach.add(n)
        stack.extend(rev.get(n, []))
    not_reaching = sorted(set(ids) - reach)
    out = {
        "schema": "OV_K5_TAIL_DEPENDENCY_GRAPH/1",
        "target_values_included": False,
        "nodes": [dict(zip(("id", "name", "bound", "enters", "scope", "improvable", "new_science",
                            "frozen_on_r2_path", "detail_ref"), n)) for n in NODES],
        "edges": [{"from": a, "to": b} for a, b in EDGES],
        "prospective_overlay": OVERLAY,
        "checks": {"acyclic": ok_dag, "planted_cycle_detected": not neg,
                   "nodes_not_reaching_Gamma": not_reaching},
        "sources": ["graph/sources/graph_A_consumer.md", "graph/sources/graph_B_operators.md",
                    "graph/sources/graph_C_inputs.md"],
    }
    (HERE / "K5_TAIL_DEPENDENCY_GRAPH.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out["checks"]))
    Q.log_execution("graph/build_graph_json.py", "dependency graph JSON producer", cells_touched=[],
                    klass="INFRASTRUCTURE")
    assert ok_dag and not neg


if __name__ == "__main__":
    main()
