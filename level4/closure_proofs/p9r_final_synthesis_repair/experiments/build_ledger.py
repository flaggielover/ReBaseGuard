#!/usr/bin/env python3
"""R5 — build the P9R claim ledger and dependency graph from source, and
validate them against the frozen rules in ``ledger_schema.py``.

The ledger is generated, never hand-edited.  Its input is
``claims_source.py``, whose every row cites an authoritative path plus the
section it was read from; ``build_ledger.py`` re-reads those paths and fails
if one is missing (rule V8).

Two graphs are emitted:

``dependency_graph.json``      the typed graph P9R actually uses.
diagnostic collapse mode       the same graph with every edge type flattened to
                               ``LOGICAL_PREMISE``.  The validator is re-run on
                               it and the resulting violations are reported, to
                               demonstrate concretely that an untyped
                               dependency graph of this project is unsound.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
P9R = HERE.parent
sys.path.insert(0, str(P9R / "src"))
sys.path.insert(0, str(HERE))

from claims_source import NODES                                # noqa: E402
from ledger_schema import (                                    # noqa: E402
    CLAIM_CLASSES, CLOSED_PRIORITIES, CONDITIONAL_RANK, EDGE_TYPES,
    FORBIDDEN_EXACT_WORDING, HYPOTHESES, NODE_KINDS,
    NON_EXACT_PREMISE_CLASSES, PARTIAL_OR_FAIL_PRIORITIES, RANK, RULES,
    STRENGTH_EDGES,
)
from rebaseguard_p9r.provenance import REPO_ROOT, write_artifact  # noqa: E402


def index(nodes):
    return {n["id"]: n for n in nodes}


def cls(n):
    return n.get("claim_class")


def licensed_strength(nodes):
    """min over the declared rank and the strength-bearing parents.

    An ``ASSUMPTION`` edge caps the child at ``CONDITIONAL_THEOREM`` rank
    rather than at the assumption's own rank: declaring a hypothesis openly is
    exactly what a conditional theorem is allowed to do.  A ``LOGICAL_PREMISE``
    edge propagates the parent's full strength, because a proof that consumes
    a premise can be no stronger than that premise.
    """
    by_id = index(nodes)
    memo: dict[str, int] = {}

    def rho(nid, stack=()):
        if nid in memo:
            return memo[nid]
        if nid in stack:
            raise ValueError(f"cycle at {nid}")
        n = by_id[nid]
        base = RANK.get(cls(n), 6) if n["kind"] != "STATUS" else 6
        if n["kind"] == "DEFINITION":
            base = 6
        best = base
        for e in n["edges"]:
            if e["type"] == "LOGICAL_PREMISE":
                best = min(best, rho(e["parent"], stack + (nid,)))
            elif e["type"] == "ASSUMPTION":
                best = min(best, CONDITIONAL_RANK)
        memo[nid] = best
        return best

    return {n["id"]: rho(n["id"]) for n in nodes}


def acyclic(nodes) -> tuple[bool, list]:
    by_id = index(nodes)
    colour: dict[str, int] = {}
    bad = []

    def visit(nid, stack):
        if colour.get(nid) == 2:
            return
        if colour.get(nid) == 1:
            bad.append(stack + [nid])
            return
        colour[nid] = 1
        for e in by_id[nid]["edges"]:
            visit(e["parent"], stack + [nid])
        colour[nid] = 2

    for n in nodes:
        visit(n["id"], [])
    return (not bad), bad


def validate(nodes, *, collapsed: bool, final: bool) -> dict:
    by_id = index(nodes)
    v: dict[str, list] = {k: [] for k in RULES}

    for n in nodes:
        nid, kind = n["id"], n["kind"]
        if kind not in NODE_KINDS:
            v["V8"].append(f"{nid}: unknown kind {kind}")
        c = cls(n)
        if kind == "CLAIM" and c not in CLAIM_CLASSES:
            v["V8"].append(f"{nid}: claim class {c!r} not in the frozen vocabulary")
        if kind == "DEFINITION" and c is not None:
            v["V8"].append(f"{nid}: a DEFINITION may not carry a claim class")
        if kind == "STATUS" and c is not None:
            v["V8"].append(f"{nid}: a STATUS may not carry a claim class")
        for e in n["edges"]:
            if e["type"] not in EDGE_TYPES:
                v["V8"].append(f"{nid}: unknown edge type {e['type']}")

        premise_parents = [by_id[e["parent"]] for e in n["edges"]
                           if e["type"] == "LOGICAL_PREMISE"]
        assumption_edges = [e for e in n["edges"] if e["type"] == "ASSUMPTION"]

        if c == "EXACT_THEOREM":
            for p in premise_parents:
                if cls(p) in NON_EXACT_PREMISE_CLASSES:
                    v["V1"].append(f"{nid} <- {p['id']} ({cls(p)})")
            if assumption_edges:
                v["V2"].append(f"{nid} carries "
                               f"{len(assumption_edges)} ASSUMPTION edge(s)")
            if n.get("hypotheses") not in ("NONE_BEYOND_MODEL",
                                           "DISCHARGED_FOR_FROZEN_MODEL"):
                v["V5"].append(f"{nid}: hypotheses={n.get('hypotheses')!r}")
            low = n["statement"].lower()
            for w in FORBIDDEN_EXACT_WORDING:
                if w in low:
                    v["V11"].append(f"{nid}: exact statement contains {w!r}")
        if c == "CONDITIONAL_THEOREM" and n.get("hypotheses") != "STATED_NOT_DISCHARGED":
            v["V4"].append(f"{nid}: hypotheses={n.get('hypotheses')!r}")
        if c == "FORMALLY_VERIFIED" and not n.get("formal_evidence"):
            v["V3"].append(f"{nid}: FORMALLY_VERIFIED without formal_evidence")
        if c == "CERTIFIED_NUMERICAL" and not n.get("certified_evidence"):
            v["V3"].append(f"{nid}: CERTIFIED_NUMERICAL without certified_evidence")
        if c == "FORMALLY_VERIFIED":
            for e in n["edges"]:
                if e["type"] in ("CERTIFIED_SUPPORT", "EMPIRICAL_SUPPORT"):
                    v["V3"].append(f"{nid}: formal class supported by "
                                   f"{e['type']} from {e['parent']}")
        if n.get("hypotheses") and n["hypotheses"] not in HYPOTHESES:
            v["V8"].append(f"{nid}: unknown hypotheses value")

        for e in n["edges"]:
            if (by_id[e["parent"]]["kind"] == "STATUS"
                    and e["type"] in STRENGTH_EDGES):
                v["V6"].append(f"{nid} <- STATUS {e['parent']} as {e['type']}")

        # V8 source existence
        src = n.get("source")
        if src:
            path = REPO_ROOT / src
            own_result = src.startswith("level4/closure_proofs/"
                                        "p9r_final_synthesis_repair/results/")
            if not path.exists() and not (own_result and not final):
                v["V8"].append(f"{nid}: missing source {src}")
        if n["kind"] == "CLAIM" and not n.get("section"):
            v["V8"].append(f"{nid}: no source section recorded")

        low_stmt = n["statement"].lower()
        if "novel" in low_stmt and c != "NOT_ESTABLISHED" \
                and "not established" not in low_stmt:
            v["V14"].append(f"{nid}: novelty statement classified {c} without "
                            "an explicit not-established qualifier")

    ok, cycles = acyclic(nodes)
    if not ok:
        v["V7"].append(f"cycles: {cycles}")

    for pri in PARTIAL_OR_FAIL_PRIORITIES:
        usable = [n["id"] for n in nodes
                  if n.get("priority") == pri and n["kind"] == "CLAIM"
                  and cls(n) not in ("NOT_ESTABLISHED",)]
        if not usable:
            v["V9a"].append(f"{pri}: no surviving usable claim")
    fail_survivors = [n["id"] for n in nodes
                      if n.get("priority") == "P8" and n["kind"] == "CLAIM"]
    if not fail_survivors:
        v["V9c"].append("P8 FAIL deleted all evidence")
    for pri in CLOSED_PRIORITIES:
        claims = [n for n in nodes
                  if n.get("priority") == pri and n["kind"] == "CLAIM"]
        if claims and all(cls(n) in ("EXACT_THEOREM", "FORMALLY_VERIFIED")
                          for n in claims):
            v["V9b"].append(f"{pri}: every claim sits at maximal class — "
                            "CLOSED appears to auto-validate")

    if "ASM-DOM" not in by_id:
        v["V10"].append("ASM-DOM node missing")
    else:
        t2b = by_id.get("P9R-T2b")
        if not t2b or not any(e["parent"] == "ASM-DOM" and e["type"] == "ASSUMPTION"
                              for e in t2b["edges"]):
            v["V10"].append("P9R-T2b does not carry the ASM-DOM ASSUMPTION edge")
        for n in nodes:
            if cls(n) == "EXACT_THEOREM":
                for e in n["edges"]:
                    if e["parent"] in ("ASM-DOM", "ASM-MONO"):
                        v["V10"].append(f"{n['id']} takes {e['parent']} as "
                                        f"{e['type']} while claiming EXACT")

    if cls(by_id.get("P3-X1", {})) == "FORMALLY_VERIFIED":
        v["V12"].append("P3-X1 is FORMALLY_VERIFIED")
    if by_id.get("P8-STATUS", {}).get("priority_status") != "FAIL":
        v["V13"].append("P8 status is not FAIL")
    if by_id.get("P8R-STATUS", {}).get("priority_status") != "CLOSED":
        v["V13"].append("P8R status is not CLOSED")
    for n in nodes:
        if (n["kind"] == "CLAIM" and n.get("priority") == "P8"
                and "P8R" in n["statement"]):
            v["V13"].append(f"{n['id']}: a P8 claim cites P8R evidence")
        if (n["kind"] == "CLAIM" and n.get("priority") == "P8R"
                and n.get("source", "").startswith(
                    "level4/closure_proofs/p8_model_class_robustness")):
            v["V13"].append(f"{n['id']}: a P8R claim is sourced from P8")

    strength = licensed_strength(nodes)
    for n in nodes:
        if n["kind"] != "CLAIM":
            continue
        declared = RANK[cls(n)]
        if strength[n["id"]] < declared:
            v["V15"].append(f"{n['id']}: declared {cls(n)} (rank {declared}) "
                            f"exceeds licensed strength {strength[n['id']]}")

    total = sum(len(x) for x in v.values())
    return {"collapsed_diagnostic": collapsed,
            "violations": {k: x for k, x in v.items() if x},
            "n_violations": total,
            "rules": RULES,
            "licensed_strength": strength}


def collapse(nodes):
    out = []
    for n in nodes:
        c = dict(n)
        c["edges"] = [{"parent": e["parent"], "type": "LOGICAL_PREMISE"}
                      for e in n["edges"]]
        out.append(c)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--final", action="store_true",
                    help="require P9R's own result artifacts to exist (V8)")
    args = ap.parse_args()

    report = validate(NODES, collapsed=False, final=args.final)
    strength = report["licensed_strength"]

    claims = [n for n in NODES if n["kind"] == "CLAIM"]
    from collections import Counter
    class_counts = Counter(cls(n) for n in claims)
    edge_counts = Counter(e["type"] for n in NODES for e in n["edges"])

    ledger_rows = []
    for n in NODES:
        ledger_rows.append({
            "id": n["id"], "kind": n["kind"], "priority": n.get("priority"),
            "claim_class": cls(n),
            "priority_status": n.get("priority_status"),
            "statement": n["statement"],
            "source_path": n.get("source"), "source_section": n.get("section"),
            "assumptions": [e["parent"] for e in n["edges"]
                            if e["type"] == "ASSUMPTION"],
            "scope": n.get("scope"),
            "hypotheses": n.get("hypotheses"),
            "formal_evidence": n.get("formal_evidence"),
            "certified_evidence": n.get("certified_evidence"),
            "limitation": n.get("limitation"),
            "licensed_strength": strength[n["id"]],
            "declared_rank": RANK[cls(n)] if cls(n) else None,
            "survived_partial_or_fail_priority":
                n.get("priority") in PARTIAL_OR_FAIL_PRIORITIES,
            "usable_in_p9r": n.get("priority") != "P8"
                             or n["id"] in ("P8-L0L1", "P8-T1", "P8-F1"),
        })

    collapsed_report = validate(collapse(NODES), collapsed=True, final=args.final)

    payload = {
        "n_nodes": len(NODES), "n_claims": len(claims),
        "n_edges": sum(len(n["edges"]) for n in NODES),
        "class_distribution": dict(sorted(class_counts.items())),
        "edge_type_distribution": dict(sorted(edge_counts.items())),
        "kind_distribution": dict(Counter(n["kind"] for n in NODES)),
        "validation": {k: v for k, v in report.items()
                       if k != "licensed_strength"},
        "collapsed_diagnostic": {
            "n_violations": collapsed_report["n_violations"],
            "violations": collapsed_report["violations"],
            "interpretation":
                "Flattening every edge to LOGICAL_PREMISE makes formal, "
                "certified, empirical, reproduction, provenance, "
                "negative-constraint and status edges indistinguishable from "
                "logical premises. The violations listed here are precisely "
                "the unsound propagations that a collapsed graph would "
                "license or hide, which is why P9R's edge types are frozen "
                "and typed.",
        },
        "nodes": ledger_rows,
        "graph": [{"child": n["id"], "parent": e["parent"], "type": e["type"]}
                  for n in NODES for e in n["edges"]],
    }

    write_artifact("claim_ledger.json",
                   schema="rebaseguard.p9r.claim-ledger.v1",
                   generator="experiments/build_ledger.py",
                   config={"source_table": "experiments/claims_source.py",
                           "schema_module": "experiments/ledger_schema.py",
                           "final": args.final},
                   payload=payload)
    write_artifact("dependency_graph.json",
                   schema="rebaseguard.p9r.dependency-graph.v1",
                   generator="experiments/build_ledger.py",
                   config={"edge_types": list(EDGE_TYPES),
                           "strength_edges": list(STRENGTH_EDGES),
                           "final": args.final},
                   payload={"n_nodes": len(NODES),
                            "n_edges": payload["n_edges"],
                            "edge_type_distribution":
                                payload["edge_type_distribution"],
                            "acyclic": report["n_violations"] == 0
                                       or "V7" not in report["violations"],
                            "edges": payload["graph"],
                            "licensed_strength": strength,
                            "collapsed_diagnostic":
                                payload["collapsed_diagnostic"]})

    print(f"nodes={len(NODES)} claims={len(claims)} edges={payload['n_edges']}")
    print("classes:", dict(sorted(class_counts.items())))
    print("typed-graph violations:", report["n_violations"],
          report["violations"] or "")
    print("collapsed-graph violations:", collapsed_report["n_violations"])
    return 0 if report["n_violations"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
