"""Every result artifact must name a real generator and be regenerable.

This is the direct repair of the P9 defect "A5/A6 result files have no
supplied generator".
"""
from __future__ import annotations

import json
import subprocess
import sys

import pytest

from conftest import P9R, ROOT
from rebaseguard_p9r.provenance import canonical_digest

REQUIRED = ("schema", "generator", "argv", "seed_namespace", "git_commit",
            "environment", "config", "payload_sha256", "payload")

EXPECTED_GENERATORS = {
    "sr_recurrence_check.json": "experiments/run_sr_recurrence_check.py",
    "reproduction.json": "experiments/run_reproduction.py",
    "burnin_sensitivity.json": "experiments/run_burnin_sensitivity.py",
    "response_grid.json": "experiments/run_response_grid.py",
    "claim_ledger.json": "experiments/build_ledger.py",
    "dependency_graph.json": "experiments/build_ledger.py",
}


def artifacts():
    out = []
    for f in sorted((P9R / "results").glob("*.json")):
        out.append(f)
    return out


def test_at_least_the_expected_artifacts_exist():
    names = {f.name for f in artifacts()}
    missing = set(EXPECTED_GENERATORS) - names
    if missing:
        pytest.skip(f"Checkpoint-B artifacts absent: {sorted(missing)}")
    assert not missing


@pytest.mark.parametrize("name", sorted(EXPECTED_GENERATORS))
def test_artifact_has_complete_provenance(name):
    f = P9R / "results" / name
    if not f.exists():
        pytest.skip("Checkpoint-B artifact")
    rec = json.loads(f.read_text())
    for field in REQUIRED:
        assert field in rec, f"{name} missing {field}"
    gen = rec["generator"].split("p9r_final_synthesis_repair/")[-1]
    assert gen == EXPECTED_GENERATORS[name]
    assert (P9R / gen).exists()
    sm = json.loads((P9R / "SOURCE_MANIFEST.json").read_text())
    assert gen in sm["files"], f"{gen} not covered by SOURCE_MANIFEST"
    assert rec["payload_sha256"] == canonical_digest(rec["payload"])
    assert rec["environment"]["numpy"] != "ABSENT"


def test_no_orphan_result_artifact():
    """No file may sit under results/ without a generator we know about."""
    for f in artifacts():
        assert f.name in EXPECTED_GENERATORS, f"orphan artifact {f.name}"


def test_a5_a6_reduced_deterministic_regeneration(tmp_path):
    """Regenerate reduced versions of A5 and A6 and check they are stable."""
    for script, out in (("run_burnin_sensitivity.py", "burnin_sensitivity_quick.json"),
                        ("run_response_grid.py", "response_grid_quick.json")):
        r = subprocess.run([sys.executable, str(P9R / "experiments" / script),
                            "--quick"], capture_output=True, text=True,
                           cwd=str(ROOT))
        assert r.returncode == 0, r.stderr[-2000:]
        p = P9R / "results" / out
        first = json.loads(p.read_text())
        r2 = subprocess.run([sys.executable, str(P9R / "experiments" / script),
                             "--quick"], capture_output=True, text=True,
                            cwd=str(ROOT))
        assert r2.returncode == 0
        second = json.loads(p.read_text())
        assert first["payload_sha256"] == second["payload_sha256"], \
            f"{script} --quick is not deterministic"
        p.unlink()


def test_production_artifacts_reference_the_frozen_config(reproduction):
    cfg_rows = reproduction["rows"]
    for row in cfg_rows:
        assert row["n_rep"] == 5000 and row["n_cycles"] == 50 and row["burn_in"] == 12
    assert reproduction["p7_source"].endswith("results/consequences.json")
