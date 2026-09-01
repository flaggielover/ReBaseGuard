"""G6 - PARTIAL priorities are not carried as closure; scope-bound closure is
not novelty."""
PARTIAL = {"P4", "P5"}

def test_partial_priority_claims_are_qualified(claims):
    for c in claims:
        if c["priority"] in PARTIAL and c["status"] in (
                "EXACT_THEOREM", "CONDITIONAL_THEOREM", "FORMALLY_VERIFIED"):
            qualified = c["p9_may_use"] != "YES"
            assert qualified or c["limitations"].strip(), (
                f"{c['id']} from PARTIAL {c['priority']} is unqualified")

def test_partial_priorities_present(claims):
    assert {c["priority"] for c in claims} >= PARTIAL

def test_no_closure_implies_novelty(claims, byid):
    """P4, P5, P6 and P8 novelty must all remain NOT_ESTABLISHED regardless of
    any priority's closure status."""
    for cid in ("P4-NOV", "P5-NOV", "P6-NOV"):
        assert byid[cid]["status"] == "NOT_ESTABLISHED", cid
    assert byid["P8-S5"]["status"] == "NOT_ESTABLISHED"

def test_p6_closure_is_recorded_as_scope_bound(byid):
    lim = byid["P6-F1"]["limitations"]
    assert "NOT NOVELTY" in lim.upper()
    assert "D-10" in lim
