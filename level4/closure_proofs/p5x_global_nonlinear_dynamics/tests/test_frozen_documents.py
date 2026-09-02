"""Checkpoint-A tests: the frozen documents exist, agree with their digests,
and say what the campaign promised they would say."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

NS = Path(__file__).resolve().parents[1]


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def test_protocol_digest_matches_files():
    doc = json.loads((NS / "PROTOCOL_DIGEST.json").read_text())
    assert doc["kind"] == "protocol"
    assert doc["files"], "empty protocol digest"
    for rel, rec in doc["files"].items():
        p = NS / rel
        assert p.exists(), rel
        assert _sha(p) == rec["sha256"], f"{rel} changed after freezing"


def test_source_manifest_matches_files():
    doc = json.loads((NS / "SOURCE_MANIFEST.json").read_text())
    assert doc["kind"] == "source"
    for rel, rec in doc["files"].items():
        p = NS / rel
        assert p.exists(), rel
        assert _sha(p) == rec["sha256"], f"{rel} changed after freezing"


def test_temporal_anchor_is_not_frozen_into_the_digest():
    doc = json.loads((NS / "PROTOCOL_DIGEST.json").read_text())
    assert "TEMPORAL_ANCHOR.md" not in doc["files"]


def test_p5_is_never_recoloured():
    for name in ("README.md", "FROZEN_GATES.md", "FEASIBILITY_AUDIT.md",
                 "CODEX_HANDOFF.md"):
        text = (NS / name).read_text()
        assert "P5 = PARTIAL" in text or "P5_ORIGINAL_VERDICT = PARTIAL" in text \
            or "PARTIAL" in text, name
    gates = (NS / "FROZEN_GATES.md").read_text()
    assert "P5  = PARTIAL   (unchanged, permanent)" in gates
    assert "CLOSED_BY_SUCCESSOR_CAMPAIGN" in gates


def test_campaign_is_not_labelled_p5r():
    for p in NS.glob("*.md"):
        text = p.read_text()
        for line in text.splitlines():
            stripped = line.strip()
            # the only admissible mentions are prohibitions
            if "P5R" in stripped:
                assert ("not" in stripped.lower() or "never" in stripped.lower()
                        or "P5R_LAUNCHED = NO" in stripped
                        or "p5r*" in stripped), f"{p.name}: {stripped}"


def test_novelty_not_overclaimed():
    assert "NOVELTY_STATUS      = NOT_ESTABLISHED" in (NS / "README.md").read_text()
    assert "NOT_ESTABLISHED" in (NS / "LIMITATIONS.md").read_text()


def test_gate_ids_are_complete():
    gates = (NS / "FROZEN_GATES.md").read_text()
    for i in range(1, 14):
        assert f"`G{i}`" in gates, f"missing gate G{i}"
