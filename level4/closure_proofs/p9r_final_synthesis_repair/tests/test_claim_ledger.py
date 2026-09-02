"""Claim classes, dependency-edge semantics and premise propagation."""
from __future__ import annotations

import pytest

from claims_source import NODES
from ledger_schema import CLAIM_CLASSES, EDGE_TYPES, RANK
from build_ledger import collapse, validate


BY_ID = {n["id"]: n for n in NODES}


def test_typed_graph_validates_cleanly():
    report = validate(NODES, collapsed=False, final=False)
    assert report["violations"] == {}, report["violations"]


def test_collapsing_edge_types_is_demonstrably_unsound():
    """The diagnostic mode required by the repair mandate.

    Flattening every edge to LOGICAL_PREMISE must produce violations the typed
    graph does not have; that difference IS the argument for typed edges.
    """
    typed = validate(NODES, collapsed=False, final=False)
    flat = validate(collapse(NODES), collapsed=True, final=False)
    assert flat["n_violations"] > typed["n_violations"]
    # in particular formal/certified/empirical support edges become premises
    assert "V1" in flat["violations"] or "V6" in flat["violations"]


def test_every_claim_cites_a_source_path_and_section():
    for n in NODES:
        if n["kind"] != "CLAIM":
            continue
        assert n.get("source"), n["id"]
        assert n.get("section"), n["id"]


def test_class_vocabulary_is_frozen():
    for n in NODES:
        if n["kind"] == "CLAIM":
            assert n["claim_class"] in CLAIM_CLASSES, n["id"]
    for n in NODES:
        for e in n["edges"]:
            assert e["type"] in EDGE_TYPES, (n["id"], e)


# ------------------------------------------------------- the specific repairs
def test_p3_x1_is_no_longer_formally_verified():
    n = BY_ID["P3-X1"]
    assert n["claim_class"] == "CERTIFIED_NUMERICAL"
    assert "Fraction" in n["certified_evidence"] or "Arb" in n["certified_evidence"]


def test_formally_verified_claims_all_carry_kernel_evidence():
    for n in NODES:
        if n.get("claim_class") == "FORMALLY_VERIFIED":
            assert n.get("formal_evidence"), n["id"]
            assert "kernel" in n["formal_evidence"].lower() \
                or "Lean" in n["formal_evidence"]


def test_p7_a_is_split_into_identity_monotonicity_and_grid():
    assert BY_ID["P7-A-ID"]["claim_class"] == "EXACT_THEOREM"
    assert BY_ID["P7-A-MONO"]["claim_class"] == "NOT_ESTABLISHED"
    assert BY_ID["P7-A-OP"]["claim_class"] == "EMPIRICAL_ONLY"
    assert "monoton" not in BY_ID["P7-A-ID"]["statement"].lower()


def test_p7_d0_is_split_into_identity_and_conditional_deficit():
    assert BY_ID["P7-D0-ID"]["claim_class"] == "EXACT_THEOREM"
    assert BY_ID["P7-D0-DEF"]["claim_class"] == "CONDITIONAL_THEOREM"
    assert any(e["parent"] == "ASM-DOM" and e["type"] == "ASSUMPTION"
               for e in BY_ID["P7-D0-DEF"]["edges"])


def test_p7_monotonicity_is_never_exact_anywhere_in_the_table():
    for n in NODES:
        if n.get("claim_class") == "EXACT_THEOREM":
            low = n["statement"].lower()
            for word in ("monoton", "non-increasing", "nonincreasing"):
                assert word not in low, n["id"]


def test_t2a_is_exact_and_assumption_free():
    n = BY_ID["P9R-T2a"]
    assert n["claim_class"] == "EXACT_THEOREM"
    assert n["hypotheses"] == "NONE_BEYOND_MODEL"
    assert not [e for e in n["edges"] if e["type"] == "ASSUMPTION"]
    for e in n["edges"]:
        if e["type"] == "LOGICAL_PREMISE":
            parent = BY_ID[e["parent"]]
            assert parent.get("claim_class") in (None, "EXACT_THEOREM"), e


def test_t2b_is_conditional_on_the_named_dominance_premise():
    n = BY_ID["P9R-T2b"]
    assert n["claim_class"] == "CONDITIONAL_THEOREM"
    assert n["hypotheses"] == "STATED_NOT_DISCHARGED"
    assert any(e["parent"] == "ASM-DOM" and e["type"] == "ASSUMPTION"
               for e in n["edges"])


def test_the_dominance_premise_is_an_explicit_node_and_not_established():
    n = BY_ID["ASM-DOM"]
    assert n["kind"] == "ASSUMPTION"
    assert n["claim_class"] == "NOT_ESTABLISHED"


def test_no_exact_theorem_depends_on_an_assumption_node():
    for n in NODES:
        if n.get("claim_class") != "EXACT_THEOREM":
            continue
        for e in n["edges"]:
            assert e["parent"] not in ("ASM-DOM", "ASM-MONO",
                                       "ASM-P1-EXPMOM", "ASM-P4-A1A7"), n["id"]


# ------------------------------------------------------- status propagation
def test_partial_and_fail_priorities_still_have_usable_claims():
    for pri in ("P4", "P5", "P8", "P9"):
        usable = [n for n in NODES
                  if n.get("priority") == pri and n["kind"] == "CLAIM"
                  and n["claim_class"] != "NOT_ESTABLISHED"]
        assert usable, pri


def test_fail_priority_does_not_delete_surviving_evidence():
    p8 = [n for n in NODES if n.get("priority") == "P8" and n["kind"] == "CLAIM"]
    assert any(n["claim_class"] == "EXACT_THEOREM" for n in p8)
    assert any(n["claim_class"] == "NEGATIVE_RESULT" for n in p8)


def test_closed_priority_does_not_auto_validate():
    for pri in ("P1", "P3", "P6", "P7"):
        claims = [n for n in NODES
                  if n.get("priority") == pri and n["kind"] == "CLAIM"]
        assert not all(n["claim_class"] in ("EXACT_THEOREM", "FORMALLY_VERIFIED")
                       for n in claims), pri


def test_status_nodes_are_never_logical_premises():
    statuses = {n["id"] for n in NODES if n["kind"] == "STATUS"}
    for n in NODES:
        for e in n["edges"]:
            if e["parent"] in statuses:
                assert e["type"] == "STATUS_PROPAGATION", (n["id"], e)


def test_p8_and_p8r_statuses_are_distinct():
    assert BY_ID["P8-STATUS"]["priority_status"] == "FAIL"
    assert BY_ID["P8R-STATUS"]["priority_status"] == "CLOSED"
    assert "does NOT convert" in BY_ID["P8R-RECON"]["statement"]


def test_p9r_core_theorems_do_not_depend_on_p8_or_p8r():
    parents = {}
    for n in NODES:
        parents[n["id"]] = [e for e in n["edges"]
                            if e["type"] in ("LOGICAL_PREMISE", "ASSUMPTION")]
    seen, stack = set(), ["P9R-T2a", "P9R-T2b"]
    while stack:
        for e in parents.get(stack.pop(), []):
            if e["parent"] not in seen:
                seen.add(e["parent"])
                stack.append(e["parent"])
    offenders = [n for n in seen if BY_ID[n].get("priority") in ("P8", "P8R")]
    assert offenders == []


def test_novelty_is_not_established():
    assert BY_ID["P9R-N1"]["claim_class"] == "NOT_ESTABLISHED"


def test_discrepancies_d09_d13_d15_are_retained():
    ids = {n["id"] for n in NODES}
    assert {"GLOBAL-CLOSURE", "P5-D13", "P3-PROV"} <= ids
    assert BY_ID["GLOBAL-CLOSURE"]["claim_class"] == "NOT_ESTABLISHED"
    assert BY_ID["P5-D13"]["claim_class"] == "NOT_ESTABLISHED"
    assert BY_ID["P3-PROV"]["claim_class"] == "PROVENANCE_LIMITATION"


def test_licensed_strength_never_exceeds_the_declared_class(ledger_rows):
    for r in ledger_rows.values():
        if r["kind"] != "CLAIM":
            continue
        assert r["licensed_strength"] >= RANK[r["claim_class"]], r["id"]
