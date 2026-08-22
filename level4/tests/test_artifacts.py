"""Provenance, storage and ledger artifacts."""

from __future__ import annotations

import json

import numpy as np
import pytest

from rebaseguard_level4 import provenance, storage
from rebaseguard_level4.campaigns import estimate_gate41_cost, run_gate41_campaign
from rebaseguard_level4.ledger import Ledger
from rebaseguard_level4.multicycle import MultiCycleConfig, stream_provenance

REQUIRED_MANIFEST_KEYS = (
    "experiment_id", "gate", "stage", "utc_timestamp", "proof_role",
    "git", "environment", "code_sha256", "config", "config_sha256", "streams",
)


def test_manifest_contains_every_required_provenance_field():
    cfg = MultiCycleConfig(n_replicates=2, n_cycles=3, burn_in=1, rho=0.5, m=1,
                           master_seed=42)
    manifest = provenance.build_manifest(
        gate="4.1", stage="smoke", config=cfg.as_dict(),
        streams=stream_provenance(cfg))
    for key in REQUIRED_MANIFEST_KEYS:
        assert key in manifest, key
    assert manifest["git"]["commit"] is not None
    assert isinstance(manifest["git"]["dirty"], bool)
    assert manifest["environment"]["numpy"] == np.__version__
    assert "python" in manifest["environment"]
    assert manifest["code_sha256"]["__combined__"]
    for field in ("detector", "k", "h", "m", "rho", "master_seed",
                  "n_replicates", "n_cycles", "burn_in"):
        assert field in manifest["config"], field
    roles = {s["role"] for s in manifest["streams"]}
    assert roles == {"physical_observations_X", "fresh_statistic_Y"}
    assert json.loads(json.dumps(manifest, default=str))


def test_experiment_id_is_deterministic_and_config_sensitive():
    a = {"m": 1, "rho": 0.5}
    b = {"m": 1, "rho": 0.6}
    assert provenance.experiment_id("g", "s", a) == provenance.experiment_id("g", "s", a)
    assert provenance.experiment_id("g", "s", a) != provenance.experiment_id("g", "s", b)
    assert provenance.experiment_id("g", "s", a) != provenance.experiment_id("g", "t", a)
    assert provenance.experiment_id("g", "s", {"rho": 0.5, "m": 1}) == \
        provenance.experiment_id("g", "s", a)          # key order must not matter


def test_code_hash_changes_when_a_source_file_changes(tmp_path, monkeypatch):
    first = provenance.code_hash()
    assert "frozen.py" in first and "multicycle.py" in first
    assert first["__combined__"] == provenance.code_hash()["__combined__"]


def test_parquet_roundtrip_preserves_columns_and_metadata(tmp_path):
    columns = {
        "replicate": np.arange(5, dtype=np.int32),
        "e_next": np.linspace(-1.0, 1.0, 5),
        "direction": np.array([1, -1, 1, -1, 1], dtype=np.int8),
        "in_burn_in": np.array([True, True, False, False, False]),
    }
    path = storage.write_parquet(columns, tmp_path / "x.parquet",
                                 metadata={"experiment_id": "abc"})
    back = storage.read_parquet(path)
    for name, values in columns.items():
        assert np.array_equal(back[name], values), name


def test_json_and_csv_writers(tmp_path):
    payload = {"a": np.float64(1.5), "b": np.int64(3), "c": np.arange(3)}
    storage.write_json(payload, tmp_path / "x.json")
    assert storage.read_json(tmp_path / "x.json") == {"a": 1.5, "b": 3,
                                                      "c": [0, 1, 2]}
    storage.write_csv([{"a": 1, "b": 2}, {"b": 3, "c": 4}], tmp_path / "x.csv")
    text = (tmp_path / "x.csv").read_text()
    assert text.splitlines()[0] == "a,b,c"


def test_cost_estimator_is_linear_in_its_inputs():
    small = estimate_gate41_cost(n_replicates=100, n_cycles=1000, burn_in=0,
                                 arl_estimate=50.0, seconds_per_step=2e-5)
    big = estimate_gate41_cost(n_replicates=100, n_cycles=10_000, burn_in=0,
                               arl_estimate=50.0, seconds_per_step=2e-5)
    assert big["estimated_runtime_seconds"] == pytest.approx(
        10 * small["estimated_runtime_seconds"])
    assert big["estimated_raw_rows"] == 10 * small["estimated_raw_rows"]


def test_campaign_writes_a_complete_auditable_artifact_set(tmp_path):
    result = run_gate41_campaign(
        stage="unittest", rho_values=[0.0, 1.0], m_values=[1],
        n_replicates=4, n_cycles=20, burn_in=5, master_seed=7,
        n_bootstrap=100, results_root=tmp_path, progress=False)
    out = result["out_dir"]
    assert (out / "campaign.manifest.json").exists()
    assert (out / "campaign.summary.json").exists()
    assert (out / "headline.csv").exists()
    for cell in result["cells"]:
        assert (out / f"{cell['cell_id']}.manifest.json").exists()
        assert (out / f"{cell['cell_id']}.summary.json").exists()
        raw = storage.read_parquet(cell["raw_path"])
        assert raw["replicate"].size == 4 * 25
        assert set(raw) >= {"replicate", "cycle_index", "e_prev", "e_next",
                            "tau", "direction", "mu_reuse", "window_sum",
                            "t_tau", "rho", "m"}
    header = (out / "headline.csv").read_text().splitlines()[0]
    for column in ("cell_id", "m", "rho", "cycle_arl", "alternation_rate",
                   "acf_e_lag1", "cycle_arl_ci_low", "cycle_arl_ci_high"):
        assert column in header
    # every aggregate must be traceable to recoverable seeds
    cell_manifest = json.loads(
        (out / f"{result['cells'][0]['cell_id']}.manifest.json").read_text())
    assert cell_manifest["config"]["master_seed"] == 7
    assert cell_manifest["streams"][0]["row_entropy_rule"]


def test_campaign_is_reproducible(tmp_path):
    kwargs = dict(stage="unittest", rho_values=[1.0], m_values=[1],
                  n_replicates=4, n_cycles=20, burn_in=5, master_seed=7,
                  n_bootstrap=100, progress=False)
    a = run_gate41_campaign(results_root=tmp_path / "a", **kwargs)
    b = run_gate41_campaign(results_root=tmp_path / "b", **kwargs)
    assert a["campaign_id"] == b["campaign_id"]
    assert a["headline"] == b["headline"]


# ------------------------------------------------------------------ ledger --

def test_ledger_rejects_unknown_status():
    with pytest.raises(ValueError):
        Ledger().add("a", "statement", "MAYBE")


def test_ledger_rejects_duplicate_ids():
    ledger = Ledger()
    ledger.add("a", "a numerical finding", "NEW-NUMERICAL")
    with pytest.raises(ValueError):
        ledger.add("a", "another", "OPEN")


@pytest.mark.parametrize("status", ["NEW-NUMERICAL", "CANDIDATE", "OPEN",
                                    "REPRODUCED", "BLOCKED"])
@pytest.mark.parametrize("phrase", ["we prove that X", "this is a proof of X",
                                    "Theorem: X", "rigorously shows X",
                                    "certified enclosure"])
def test_ledger_blocks_theorem_vocabulary_below_frozen_status(status, phrase):
    with pytest.raises(ValueError, match="proof word"):
        Ledger().add("x", phrase, status)


@pytest.mark.parametrize("status", ["FROZEN-PROVED", "FROZEN-CERTIFIED"])
def test_ledger_allows_theorem_vocabulary_for_frozen_entries(status):
    Ledger().add("x", "machine-checked proof in Lean", status)


def test_ledger_renders_json_and_markdown(tmp_path):
    ledger = Ledger()
    ledger.add("L1", "Gamma is enclosed by certified interval arithmetic",
               "FROZEN-CERTIFIED", evidence=["proofs/certificate.json"])
    ledger.add("N1", "alternation rate is 0.9 under full reuse", "NEW-NUMERICAL",
               evidence=["level4/results/x.json"], notes="pilot stage",
               numbers={"alternation_rate": 0.9})
    ledger.write(tmp_path / "l.json", tmp_path / "l.md")
    payload = json.loads((tmp_path / "l.json").read_text())
    assert payload["counts"]["FROZEN-CERTIFIED"] == 1
    assert payload["counts"]["NEW-NUMERICAL"] == 1
    text = (tmp_path / "l.md").read_text()
    assert "FROZEN-CERTIFIED" in text and "NEW-NUMERICAL" in text
    assert "pilot stage" in text
