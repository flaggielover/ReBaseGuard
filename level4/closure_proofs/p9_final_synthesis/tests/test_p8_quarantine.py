"""G5 - P8 is authoritatively FAIL; no P9 conclusion may rest on a P8 premise.

After reconciliation the invariant is no longer "P8 is provisional" but the
stronger, permanent one: P8 = FAIL, so no P8 node may have any outgoing edge.
The authoritative adjudication PERMITS P9 to use four tiers; P9 uses none.
"""
NOT_USED = "PERMITTED_BY_P8_BOUNDARY_BUT_NOT_USED_BY_P9"

def p8(claims): return [c for c in claims if c["priority"] == "P8"]

def test_p8_claims_exist(claims):
    assert p8(claims), "quarantine test would be vacuous"

def test_no_p8_node_has_outgoing_edges(claims):
    ids = {c["id"] for c in p8(claims)}
    for c in claims:
        for e in c["edges"]:
            assert e["parent"] not in ids, (
                f"{c['id']} depends on failed-campaign P8 node {e['parent']}")

def test_no_p8_node_has_premise_parents(claims):
    """P8 rows are transcriptions of an authoritative boundary, not derivations."""
    for c in p8(claims):
        assert not c["edges"], c["id"]

def test_no_provisional_status_remains(claims):
    assert not [c for c in claims if c["status"] == "PROVISIONAL_P8_PENDING_CODEX"], \
        "reconciliation incomplete: provisional P8 statuses remain"

def test_permitted_tiers_are_marked_unused(claims):
    marked = [c for c in p8(claims) if c["p9_may_use"] == NOT_USED]
    assert len(marked) >= 3, "the permitted-but-unused tiers are not recorded"

def test_negative_and_not_established_are_carried(claims):
    st = {c["status"] for c in p8(claims)}
    assert "NEGATIVE_RESULT" in st and "NOT_ESTABLISHED" in st
