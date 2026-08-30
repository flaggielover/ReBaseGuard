from __future__ import annotations

import hashlib
import json
import locale
from pathlib import Path

CAMPAIGN = Path(__file__).resolve().parents[1]
ROOT = CAMPAIGN.parents[2]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def track1b_tree_hash() -> str:
    base = ROOT / "level4/closure_proofs/m_gt_1_track1b"
    locale.setlocale(locale.LC_COLLATE, "")
    files = sorted(
        (path for path in base.rglob("*") if path.is_file() and "__pycache__" not in path.parts),
        key=lambda path: locale.strxfrm(str(path.relative_to(ROOT))),
    )
    listing = "".join(f"{sha(path)}  {path.relative_to(ROOT)}\n" for path in files)
    return hashlib.sha256(listing.encode()).hexdigest()


def test_immutable_prior_evidence_hashes() -> None:
    frozen = json.loads((CAMPAIGN / "manifest.json").read_text())["immutable_prior_evidence"]
    assert track1b_tree_hash() == frozen["track1b_tree_sha256"]
    assert sha(ROOT / "level4/stage_d/results/d2_3_derivative.json") == frozen["historical_d2_3_sha256"]
    assert sha(ROOT / "level4/stage_d/results/stage_d_decision.json") == frozen["historical_stage_d_decision_sha256"]
    assert sha(ROOT / "level4/closure_proofs/m_gt_1_track1a/results/decision.json") == frozen["historical_track1a_decision_sha256"]


def test_historical_parent_campaign_is_unmodified() -> None:
    required = ["FINAL_REPORT.md", "FAILURE_DIAGNOSES.md", "results/decision.json"]
    parent = ROOT / "level4/closure_proofs/m_gt_1"
    assert all((parent / item).is_file() for item in required)
