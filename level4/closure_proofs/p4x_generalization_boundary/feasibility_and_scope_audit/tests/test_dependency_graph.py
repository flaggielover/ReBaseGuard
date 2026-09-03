"""The claim dependency graph and the cut set must match the P9R ledger."""

from __future__ import annotations


def _p4_nodes(ledger):
    return {n["id"]: n for n in ledger["nodes"] if n["id"].startswith("P4")
            or n["id"] == "ASM-P4-A1A7"}


def test_p4_nodes_are_present_with_their_adjudicated_classes(p9r_ledger):
    nodes = _p4_nodes(p9r_ledger)
    assert nodes["P4-T1"]["claim_class"] == "CONDITIONAL_THEOREM"
    assert nodes["P4-T2N"]["claim_class"] == "CONDITIONAL_THEOREM"
    assert nodes["P4-L1"]["claim_class"] == "FORMALLY_VERIFIED"
    assert nodes["P4-F1"]["claim_class"] == "NEGATIVE_RESULT"
    assert nodes["P4-RESULT"]["claim_class"] == "PARTIAL_PRIORITY_RESULT"
    assert nodes["ASM-P4-A1A7"]["claim_class"] == "NOT_ESTABLISHED"


def test_p4_status_node_says_partial(p9r_ledger):
    status = [n for n in p9r_ledger["nodes"] if n["id"] == "P4-STATUS"][0]
    assert status["statement"] == "P4 = PARTIAL."


def test_p4_is_a_scientific_leaf(p9r_ledger, results):
    """Nothing outside the P4 sub-graph takes P4 as a logical premise."""
    external = [
        e for e in p9r_ledger["graph"]
        if e["parent"].startswith("P4")
        and not e["child"].startswith("P4")
        and e["type"] in {"LOGICAL_PREMISE", "ASSUMPTION", "FORMAL_SUPPORT"}
    ]
    assert external == []
    assert results["dependency_graph"]["p4_is_scientific_leaf"] is True


def test_p4_reaches_global_closure_by_status_propagation_only(p9r_ledger):
    edges = [e for e in p9r_ledger["graph"]
             if e["child"] == "GLOBAL-CLOSURE" and e["parent"] == "P4-STATUS"]
    assert len(edges) == 1
    assert edges[0]["type"] == "STATUS_PROPAGATION"


def test_p4_t1_carries_the_a1a7_assumption_edge(p9r_ledger):
    edges = [e for e in p9r_ledger["graph"]
             if e["child"] == "P4-T1" and e["parent"] == "ASM-P4-A1A7"]
    assert len(edges) == 1
    assert edges[0]["type"] == "ASSUMPTION"


def test_no_open_edge_sits_on_the_theorem_layer(results):
    graph = results["dependency_graph"]
    assert graph["theorem_layer_open_edges"] == 0
    assert graph["evidence_layer_open_edges"] == 3
    assert len(graph["open_edges"]) == 3


def test_cut_set_has_exactly_three_elements_and_matches_the_failed_gates(results):
    cuts = results["smallest_open_cut_set"]
    assert len(cuts) == 3
    assert len(results["verdicts"]["P4_ORIGINAL_FAILED_GATES"]) == 3
    for tag in ("CUT-1", "CUT-2", "CUT-3"):
        assert any(c.startswith(tag) for c in cuts), tag


def test_p4x_core_required_is_seven_items_and_fully_detailed(results):
    core = results["p4x_core_required"]
    detail = results["p4x_core_required_detail"]
    assert core == ["C1", "C2", "C3", "C4", "C5", "C6", "C7"]
    assert sorted(detail) == core
    assert all(detail[c] for c in core)


def test_p4x_core_requires_no_new_theorem_lean_or_certificate(results):
    assert results["lean_requirement"]["minimum_additional_for_p4x_closure"] == "NONE_NEW"
    assert results["certificate_requirement"][
        "minimum_additional_for_p4x_closure"
    ] == "NO_NEW_CERTIFICATION_BEYOND_RE-VERIFICATION"
    assert results["p4x_core_required_detail"]["C1"].startswith("INHERIT")
