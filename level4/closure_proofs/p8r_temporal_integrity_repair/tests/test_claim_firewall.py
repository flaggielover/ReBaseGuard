"""Claim-class, negative-result and novelty firewalls.

The P8 adjudication's §16 handoff table is the reference: P8R may not quietly
promote anything P8 left at a lower evidence tier, and a repair campaign may not
manufacture novelty.
"""
import json
import re

import pytest

from conftest import payload_or_skip

PROSE = ("README.md", "RESULTS.md", "LIMITATIONS.md", "FROZEN_PROTOCOL.md",
         "FROZEN_GATES.md", "REPAIR_RATIONALE.md", "DEFINITION_AUDIT.md",
         "CALIBRATION_PLAN.md", "RNG_ADDRESS_PLAN.md", "PRODUCTION_PLAN.md",
         "STATISTICAL_ANALYSIS_PLAN.md", "CODEX_HANDOFF.md",
         "TEMPORAL_ANCHOR.md")

#: phrases that would overclaim.  Each is checked case-insensitively against
#: every prose artifact P8R writes.
FORBIDDEN = (
    r"\bP8\s*=\s*CLOSED\b",
    r"\bP8R\s*=\s*CLOSED\b(?!_CANDIDATE)",
    r"window[- ]separability law (?:holds|is established|transfers)",
    r"detector transfer (?:holds|is established|is proved)",
    r"unconditional(?:ly)? (?:establishes|proves) P8R?-T1",
    r"\bnovel(?:ty)? (?:is )?established\b",
    r"\bfirst[- ]ever\b",
    r"successfully preregistered P8 closure",
)


def _prose(p8r):
    for name in PROSE:
        p = p8r / name
        if p.exists():
            yield name, p.read_text()


def test_no_forbidden_overclaim_appears_in_any_prose_artifact(p8r):
    hits = []
    for name, text in _prose(p8r):
        for pat in FORBIDDEN:
            for m in re.finditer(pat, text, re.IGNORECASE):
                line = text[:m.start()].count("\n") + 1
                hits.append(f"{name}:{line}: {m.group(0)!r}")
    assert not hits, hits


def test_novelty_status_is_not_established(p8r):
    v = payload_or_skip("results/verdict.json")
    assert v["novelty_status"] == "NOT_ESTABLISHED"


def test_verdict_is_a_candidate_and_says_so(p8r):
    v = payload_or_skip("results/verdict.json")
    assert v["authoritative"] is False
    assert v["verdict"] in ("CLOSED_CANDIDATE", "PARTIAL_CANDIDATE",
                            "FAIL_CANDIDATE")
    assert v["authoritative_status_recommendation"] == "AWAIT_CODEX_ADJUDICATION"


def test_p8_negative_results_are_carried_forward_explicitly(p8r):
    """Every hypothesis P8 rejected must be *addressed* by P8R -- resolved
    under the frozen rule and compared to P8's outcome -- never dropped."""
    v = payload_or_skip("results/verdict.json")
    from derive_verdict import P8_NEGATIVE_RESULTS
    for q in P8_NEGATIVE_RESULTS:
        assert q in v["p8_negative_result_comparison"], q
        assert v["scientific_questions"].get(q) in (
            "SUPPORTED", "REJECTED", "INCONCLUSIVE", "OUT_OF_SCOPE"), q


def test_a_negative_result_is_never_relabelled_as_supported_without_evidence():
    """If P8R reports SUPPORTED where P8 reported a negative result, the
    resolution record must carry the statistic that justifies it."""
    res = payload_or_skip("results/scientific_resolution.json")
    from derive_verdict import P8_NEGATIVE_RESULTS
    by_q = {q["question"]: q for q in res["questions"]}
    for q in P8_NEGATIVE_RESULTS:
        if by_q.get(q, {}).get("status") == "SUPPORTED":
            assert by_q[q]["statistic"], q
            assert by_q[q]["detail"], q


def test_theory_remains_conditional(p8r):
    """P8R-T1 inherits P4's undischarged differentiation/integrability
    hypotheses and must stay labelled conditional."""
    p = p8r / "RESULTS.md"
    if not p.exists():
        pytest.skip("RESULTS.md not written yet")
    text = p.read_text()
    assert re.search(r"P8R-T1[^\n]*CONDITIONAL", text), \
        "RESULTS.md must label P8R-T1 as a conditional theorem"


def test_extrapolation_windows_are_never_used_to_support_the_window_law():
    res = payload_or_skip("results/scientific_resolution.json")
    by_q = {q["question"]: q for q in res["questions"]}
    for q in ("S7", "S7D", "S7F"):
        detail = json.dumps(by_q[q]["detail"])
        assert '"m": 10' not in detail and '"m": 20' not in detail, q
