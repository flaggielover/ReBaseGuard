"""Scan P9R prose for the wording the claim-language firewall forbids."""
from __future__ import annotations

import re

import pytest

from conftest import P9R

MD = sorted(p for p in P9R.glob("*.md"))

#: phrases that may not appear as P9R's own assertions.  Each is paired with a
#: regex of permitted contexts (a quotation of P9, or an explicit ban).
BANNED = [
    (r"no conceivable[^.]{0,80}operational boundary",
     r"banned|may not|forbidden|P9 wrote|quantifies over|overbroad"),
    (r"no threshold in `?rho`? is an operational safety boundary",
     r"banned|may not|forbidden|P9 wrote|overbroad"),
    (r"exact agreement", r"never|not|banned|may not"),
]


def body(p):
    return p.read_text()


@pytest.mark.parametrize("path", MD, ids=lambda p: p.name)
def test_no_banned_operational_overclaim(path):
    text = body(path)
    for pattern, allowed in BANNED:
        for m in re.finditer(pattern, text, re.I):
            window = text[max(0, m.start() - 260): m.end() + 260]
            assert re.search(allowed, window, re.I), \
                f"{path.name}: unguarded phrase {m.group(0)!r}"


@pytest.mark.parametrize("path", MD, ids=lambda p: p.name)
def test_p8r_closed_is_never_written_as_changing_p8(path):
    text = body(path)
    for m in re.finditer(r"P8\s*=\s*CLOSED", text):
        window = text[max(0, m.start() - 200): m.end() + 200]
        assert re.search(r"not|never|does NOT|may not", window, re.I), \
            f"{path.name}: P8 written as CLOSED"


@pytest.mark.parametrize("path", MD, ids=lambda p: p.name)
def test_novelty_is_never_claimed(path):
    text = body(path)
    for m in re.finditer(r"\bnovel(ty)?\b", text, re.I):
        window = text[max(0, m.start() - 200): m.end() + 200]
        assert re.search(r"NOT_ESTABLISHED|not established|never stronger|"
                         r"not a novelty|not proof of novelty|no new literature|"
                         r"never implies|not established", window, re.I), \
            f"{path.name}: unqualified novelty claim"


def test_theory_states_t2b_as_conditional():
    t = (P9R / "THEORY.md").read_text()
    assert "ASM-DOM" in t
    assert re.search(r"Theorem P9R-T2b", t)
    # the strict inequality must never be asserted outside a conditional frame
    for m in re.finditer(r"E_\{e ~ N\(0,1/m\)\}\[A\(e\)\]\s*<\s*A\(0\)", t):
        window = t[max(0, m.start() - 400): m.end() + 200]
        assert re.search(r"Under `ASM-DOM`|ASM-DOM|conditional", window, re.I)


def test_results_carry_the_required_verdict_lines():
    p = P9R / "RESULTS.md"
    if not p.exists():
        pytest.skip("Checkpoint-B document")
    t = p.read_text()
    for key in ("P9_ORIGINAL_VERDICT = PARTIAL", "P8_ORIGINAL_VERDICT = FAIL",
                "P8R_VERDICT = CLOSED", "NOVELTY_STATUS = NOT_ESTABLISHED",
                "LEVEL4_GLOBAL_CLOSURE = NO",
                "AUTHORITATIVE_STATUS_RECOMMENDATION = AWAIT_CODEX_ADJUDICATION"):
        assert key in t, key
    assert "P9R_VERDICT = CLOSED\n" not in t, \
        "P9R must not self-promote to CLOSED; only *_CANDIDATE is allowed"
