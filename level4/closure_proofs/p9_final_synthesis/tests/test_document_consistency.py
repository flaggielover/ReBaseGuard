"""G9, G10, G13 - result-table / document consistency, and verdict discipline."""
import os, re

def read(root, name): return open(os.path.join(root, name)).read()

def test_open_discrepancies_are_surfaced_in_limitations(root):
    disc = read(root, "DISCREPANCY_REGISTER.md")
    lim = read(root, "LIMITATIONS.md")
    open_ids = set(re.findall(r"\| (D-\d+) \|[^|]*\|\s*`(?:OPEN|CONTRADICTION)", disc))
    assert open_ids, "no OPEN rows parsed; the test would be vacuous"
    for d in sorted(open_ids):
        assert d in lim, f"{d} is OPEN but absent from LIMITATIONS.md"

def test_every_status_has_a_language_rule(root, ledger):
    pol = read(root, "CLAIM_LANGUAGE_POLICY.md")
    for s in ledger["status_vocabulary"]:
        assert f"`{s}`" in pol, s

def test_scope_map_has_no_p8_dependent_filled_cell(root):
    """P8 is FAIL; a failed campaign fills no scope cell."""
    m = read(root, "MODEL_SCOPE_MAP.md")
    assert "PROVISIONAL_P8" not in m
    assert "UNKNOWN" in m
    assert "fills no" in m

def test_g14_passes_after_reconciliation(root):
    g = read(root, "CLOSURE_GATES.md")
    assert "G14" in g and "BLOCKED" not in g
    assert os.path.exists(os.path.join(root, "P8_TO_P9_RECONCILIATION.md"))

def test_verdict_matches_the_precommitted_rule(root):
    """All 14 gates pass, so the rule yields CLOSED_CANDIDATE - and the verdict
    stated in README.md must be exactly that, with the candidate caveat."""
    g = read(root, "CLOSURE_GATES.md")
    assert "`G1`–`G14` PASS (14/14)" in g
    r = read(root, "README.md")
    assert "`P9 = CLOSED_CANDIDATE`" in r
    assert "not authoritative" in r
    for bad in ("P9 = PARTIAL_CANDIDATE", "P9 = FAIL_CANDIDATE"):
        assert bad not in r

def test_p8_is_reported_as_fail_everywhere(root):
    for name in ("README.md", "RESULTS.md", "P8_TO_P9_RECONCILIATION.md"):
        t = read(root, name)
        assert "FAIL" in t, name
        assert "P8 = PARTIAL_CANDIDATE" not in t.replace(
            "Claude's `PARTIAL_CANDIDATE`", "").replace(
            "reported `PARTIAL_CANDIDATE`", ""), name
