"""Checkpoint-D (R2) tests.  Must not reveal the benchmark outcome."""
from __future__ import annotations
import hashlib, json
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
R2 = NS / "compute_optimization_r2"


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def test_profile_is_measured_not_guessed():
    prof = json.loads((NS / "results" / "r2_profile.json").read_text())
    assert prof["cells"], "no profiled cells"
    top = prof["cells"][0]["buckets"][0]["bucket"]
    assert top in ("poly_bi_primitives", "bernstein_subdivide")
    assert prof["primitives"]["max_abs_on_reachable_ONE"] > \
        50 * prof["primitives"]["kernel_polynomials_ONE"]


def test_audit_records_the_structural_limit():
    doc = (R2 / "R2_PROFILE_AND_AUDIT.md").read_text()
    assert "Only one certified path exists" in doc
    assert "NOT RUNNABLE" in (R2 / "R2_FROZEN_SPEC.md").read_text()


def test_rejected_candidates_are_rejected_on_measurement():
    doc = (R2 / "R2_PROFILE_AND_AUDIT.md").read_text()
    assert "The Taylor order is NOT over-resolved" in doc
    assert "falsifies the caching hypothesis" in doc
    spec = (R2 / "R2_FROZEN_SPEC.md").read_text()
    assert "Explicitly rejected, on measurement" in spec


def test_two_candidates_only_and_neither_is_a_science_change():
    spec = (R2 / "R2_FROZEN_SPEC.md").read_text()
    assert "### C1" in spec and "### C2" in spec and "### C3" not in spec
    assert spec.count("CLASS = CERTIFIED_BOUND_REFACTOR") == 2
    assert "Neither candidate is\n`SCIENTIFIC_METHOD_CHANGE`" in spec


def test_scope_and_threshold_unchanged():
    spec = (R2 / "R2_FROZEN_SPEC.md").read_text()
    assert "the scope `e in [0,12]`, the `0.2` gate threshold" in spec
    assert "no scope reduction, no threshold change" in spec


def test_speedup_and_campaign_bands_frozen():
    spec = (R2 / "R2_FROZEN_SPEC.md").read_text()
    for tok in (">= 8x       -> R2_BREAKTHROUGH", "R2_READY_FOR_FULL_COVER",
                "R2_USEFUL_BUT_MORE_OPT_REQUIRED"):
        assert tok in spec, tok


def test_prediction_pre_registered():
    spec = (R2 / "R2_FROZEN_SPEC.md").read_text()
    assert "predicted speedup      = 9.0" in spec


def test_no_r2_result_at_the_anchor():
    forbidden = ["r2_benchmark.json", "r2_selftest.json"]
    present = [f for f in forbidden if (NS / "results" / f).exists()]
    assert not present, f"R2 results must not exist at the anchor: {present}"


def test_prior_campaigns_frozen():
    m = json.loads((NS / "results" / "integrity" / "protected_tree_manifest_r2_pre.json").read_text())
    for rel, digest in m["prior_campaign_files_frozen"].items():
        assert _sha(NS / rel) == digest, rel


def test_r2_digests_match_files():
    for name in ("R2_PROTOCOL_DIGEST.json", "R2_SOURCE_MANIFEST.json"):
        doc = json.loads((R2 / name).read_text())
        for rel, rec in doc["files"].items():
            assert _sha(R2 / rel) == rec["sha256"], rel


def test_prior_results_intact():
    r1 = json.loads((NS / "results" / "r1_benchmark.json").read_text())
    assert r1["stop_gate"]["verdict"] == "PASS"
    assert r1["achieved_half_width"] == 0.008045668639929672
    ra = json.loads((NS / "results" / "ra_stop_gate.json").read_text())
    assert ra["achieved_half_width"] == 0.014176477298268092
    old = json.loads((NS / "results" / "stop_gate_cell.json").read_text())
    assert old["stop_gate"]["verdict"] == "FAIL"


def test_no_lean_sources_yet():
    assert not list(NS.rglob("*.lean"))
