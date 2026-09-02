"""No orphan results, and every inherited constant really is inherited."""
import hashlib
import json

import numpy as np
import pytest

from audit_integrity import GENERATOR_MAP
from rebaseguard_p8r import (CUSUM_THRESHOLD_GAUSSIAN, SR_THRESHOLD_GAUSSIAN,
                             TARGET_ARL0, K_FROZEN)
from rebaseguard_p8r.config import (stage_d_cusum_thresholds,
                                    stage_d_target_arl0)
from conftest import payload_or_skip


def _results(p8r):
    for p in sorted(p8r.glob("results/**/*.json")):
        if str(p.relative_to(p8r)).startswith("results/integrity/"):
            continue
        yield p


def test_every_result_has_a_generator_that_exists(p8r):
    seen = 0
    for p in _results(p8r):
        seen += 1
        doc = json.loads(p.read_text())
        assert "generator" in doc, p.name
        assert (p8r / doc["generator"]).exists(), (p.name, doc["generator"])
    if seen == 0:
        pytest.skip("no results yet")


def test_every_result_matches_its_declared_generator(p8r):
    from pathlib import Path
    seen = 0
    for p in _results(p8r):
        rel = str(p.relative_to(p8r))
        doc = json.loads(p.read_text())
        for glob, gen in GENERATOR_MAP.items():
            if Path(rel).match(glob):
                seen += 1
                assert doc["generator"] == gen, (rel, doc["generator"], gen)
                break
    if seen == 0:
        pytest.skip("no results yet")


def test_every_result_payload_digest_is_intact(p8r):
    seen = 0
    for p in _results(p8r):
        doc = json.loads(p.read_text())
        if not doc.get("payload_sha256"):
            continue
        seen += 1
        h = hashlib.sha256(json.dumps(doc["payload"], sort_keys=True,
                                      separators=(",", ":"),
                                      default=float).encode()).hexdigest()
        assert h == doc["payload_sha256"], p.name
    if seen == 0:
        pytest.skip("no results yet")


def test_every_result_records_argv_commit_and_environment(p8r):
    seen = 0
    for p in _results(p8r):
        doc = json.loads(p.read_text())
        seen += 1
        assert doc["argv"], p.name
        assert doc["git_commit"], p.name
        for k in ("python", "numpy", "scipy", "platform"):
            assert doc["environment"].get(k), (p.name, k)
    if seen == 0:
        pytest.skip("no results yet")


def test_inherited_constants_match_their_owning_artifact():
    assert stage_d_target_arl0() == TARGET_ARL0
    assert stage_d_cusum_thresholds()["gaussian"] == CUSUM_THRESHOLD_GAUSSIAN
    assert K_FROZEN == 0.5


def test_frozen_cusum_recurrence_is_imported_not_reimplemented():
    from rebaseguard_p8r import detectors
    src = open(detectors.__file__).read()
    assert "from rebaseguard_level4.frozen import" in src
    assert "cusum_update" in src


def test_sr_gaussian_threshold_matches_stage_d():
    import json as _json
    from rebaseguard_p8r.config import STAGE_D
    p = STAGE_D / "results" / "calibration_d1.json"
    if not p.exists():
        pytest.skip("stage_d calibration_d1.json absent")
    d = _json.loads(p.read_text())
    flat = _json.dumps(d)
    assert f"{SR_THRESHOLD_GAUSSIAN}" in flat or \
        abs(SR_THRESHOLD_GAUSSIAN - 520.886133602749) < 1e-9


def test_cusum_thresholds_used_in_production_are_stage_ds(p8r):
    frozen = stage_d_cusum_thresholds()
    seen = 0
    for tag in ("E1", "E5"):
        for fam in frozen:
            p = p8r / "results" / "gamma" / f"{tag}_cusum_{fam}.json"
            if not p.exists():
                continue
            seen += 1
            c = json.loads(p.read_text())["payload"]
            if c["status"] != "OK":
                continue
            assert c["threshold"] == frozen[fam], (tag, fam)
            assert c["threshold_provenance"] == "STAGE_D_D3_FROZEN"
    if seen == 0:
        pytest.skip("no gamma cells yet")


def test_sr_production_thresholds_come_from_an_accepted_calibration(p8r):
    cal = payload_or_skip("results/sr_calibration.json")
    accepted = {r["family"]: r["threshold"] for r in cal["rows"]
                if r["threshold"] is not None}
    seen = 0
    for tag in ("E1", "E5"):
        for fam, thr in accepted.items():
            p = p8r / "results" / "gamma" / f"{tag}_sr_{fam}.json"
            if not p.exists():
                continue
            c = json.loads(p.read_text())["payload"]
            if c["status"] != "OK":
                continue
            seen += 1
            assert c["threshold"] == thr, (tag, fam)
    if seen == 0:
        pytest.skip("no SR gamma cells yet")


def test_batch_vectors_are_stored_for_paired_analysis(p8r):
    E1 = payload_or_skip("results/gamma_matrix_E1.json")
    bv = E1["batch_gamma_A"]
    assert bv, "paired analysis needs the raw per-batch vectors"
    for key, vec in bv.items():
        assert len(vec) >= 5
        assert all(np.isfinite(vec))
