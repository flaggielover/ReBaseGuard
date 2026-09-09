"""Result-free fail-closed tests for the additive multi-host successor.

Every invalid case MUST raise MultiHostRefusal. No test performs scientific
computation and no test emits a result-bearing SR cell.
"""
import copy
import json
import sys
from pathlib import Path

import pytest

NS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(NS / "driver"))
import multihost as M                                              # noqa: E402

CKPT = json.loads((NS / "config/CHECKPOINT_HASH").read_text().strip() and
                  '"' + (NS / "config/CHECKPOINT_HASH").read_text().strip() + '"')
PRODUCER = "a" * 40
SHARD_SHA = json.loads((NS / "config/SHARD_MANIFEST_SHA256.json").read_text())["sha256"]

AWS_SIBS = {c: [c, c + 16] for c in range(16)}
VULTR_SIBS = {0: [0, 1], 1: [0, 1], 2: [2, 3], 3: [2, 3],
              4: [4, 5], 5: [4, 5], 6: [6, 7], 7: [6, 7]}


@pytest.fixture
def manifest():
    return json.loads((NS / "config/SHARD_MANIFEST.json").read_text())


@pytest.fixture
def owners(manifest):
    return M.gate_shards(manifest)


def record(cell, role, cpu_s, obligations=28, complete=True):
    return {"cell_id": cell, "role": role, "producer_commit": PRODUCER,
            "checkpoint_sha256": CKPT,
            "runtime_contract_hash": M.ROLES[role]["runtime_contract_hash"],
            "scientific_content_hash": "%064x" % cell,
            "cpu_seconds": cpu_s, "obligations_completed": obligations,
            "complete": complete}


@pytest.fixture
def ledgers(manifest):
    aws = [record(c, "AWS", 40000.0) for c in manifest["AWS"]["cells"]]
    vul = [record(c, "VULTR", 36000.0) for c in manifest["VULTR"]["cells"]]
    aws[0]["obligations_completed"] = 29          # the single far-field obligation
    return {"AWS": aws, "VULTR": vul}


# --------------------------------------------------------------- positive control
def test_valid_multihost_run_is_admitted(manifest, owners, ledgers):
    assert M.gate_role("AWS", "Amazon EC2") == "AWS"
    assert M.gate_role("VULTR", "Vultr") == "VULTR"
    M.gate_workers("AWS", 16, list(range(16)), AWS_SIBS)
    M.gate_workers("VULTR", 4, [0, 2, 4, 6], VULTR_SIBS)
    out = M.assemble_global_ledger(ledgers, owners, PRODUCER, CKPT)
    assert out["cells_completed"] == 316
    assert out["obligations_completed"] == 8849
    assert out["cap"]["charged_cpu_h"] <= M.GLOBAL_CPU_CAP
    M.verify_aggregate_ledger(out, out["aggregate_ledger_sha256"])


# ------------------------------------------------------------------ 1..16 refusals
def test_01_wrong_host_role():
    with pytest.raises(M.MultiHostRefusal):
        M.gate_role("AWS", "Vultr")
    with pytest.raises(M.MultiHostRefusal):
        M.detect_role("Google Compute Engine")


def test_02_wrong_runtime_hash():
    with pytest.raises(M.MultiHostRefusal):
        M.gate_runtime_hash("VULTR", M.ROLES["AWS"]["runtime_contract_hash"])


def test_03_wrong_worker_count():
    with pytest.raises(M.MultiHostRefusal):
        M.gate_workers("VULTR", 8, [0, 2, 4, 6], VULTR_SIBS)


def test_04_smt_misuse_is_refused():
    with pytest.raises(M.MultiHostRefusal):
        M.gate_workers("VULTR", 4, [0, 1, 2, 3], VULTR_SIBS)


def test_05_overlapping_shards(manifest):
    bad = copy.deepcopy(manifest)
    bad["VULTR"]["cells"] = bad["VULTR"]["cells"] + [bad["AWS"]["cells"][0]]
    with pytest.raises(M.MultiHostRefusal):
        M.gate_shards(bad)


def test_06_missing_cells(manifest):
    bad = copy.deepcopy(manifest)
    bad["AWS"]["cells"] = bad["AWS"]["cells"][:-1]
    with pytest.raises(M.MultiHostRefusal):
        M.gate_shards(bad)


def test_07_duplicate_ownership(manifest):
    bad = copy.deepcopy(manifest)
    bad["AWS"]["cells"] = bad["AWS"]["cells"] + [bad["AWS"]["cells"][0]]
    with pytest.raises(M.MultiHostRefusal):
        M.gate_shards(bad)


def test_08_wrong_shard_manifest():
    with pytest.raises(M.MultiHostRefusal):
        M.load_shard_manifest(NS / "config/SHARD_MANIFEST.json", "0" * 64)


def test_08b_authorised_shard_manifest_loads():
    man = M.load_shard_manifest(NS / "config/SHARD_MANIFEST.json", SHARD_SHA)
    assert man["cells_total"] == 316


def test_09_wrong_producer_commit():
    lm = json.loads((NS / "config/LAUNCH_MANIFEST.json").read_text())
    with pytest.raises(M.MultiHostRefusal):
        M.gate_producer_commit(lm, "b" * 40, CKPT, SHARD_SHA)


def test_10_foreign_host_cell(manifest, owners):
    aws_cell = manifest["AWS"]["cells"][0]
    with pytest.raises(M.MultiHostRefusal):
        M.gate_cell_ownership("VULTR", aws_cell, owners)


def test_11_cross_host_recomputation(manifest, owners, ledgers):
    bad = copy.deepcopy(ledgers)
    dup = manifest["AWS"]["cells"][0]
    bad["AWS"].append(record(dup, "AWS", 40000.0, obligations=0))
    with pytest.raises(M.MultiHostRefusal):
        M.assemble_global_ledger(bad, owners, PRODUCER, CKPT)


def test_12_per_host_cap_violation(owners, ledgers):
    bad = copy.deepcopy(ledgers)
    for r in bad["VULTR"]:
        r["cpu_seconds"] = 999999.0
    with pytest.raises(M.MultiHostRefusal):
        M.assemble_global_ledger(bad, owners, PRODUCER, CKPT)


def test_13_global_cap_violation():
    with pytest.raises(M.MultiHostRefusal):
        M.gate_global_cap({"AWS": 4000.0, "VULTR": 1000.0})


def test_13b_cap_is_not_per_host():
    """4500 is ONE global budget: two hosts at 2400 each must be refused."""
    with pytest.raises(M.MultiHostRefusal):
        M.gate_global_cap({"AWS": 2400.0, "VULTR": 2400.0})


def test_14_torn_cell_resume(owners, ledgers):
    bad = copy.deepcopy(ledgers)
    bad["AWS"][5]["complete"] = False
    with pytest.raises(M.MultiHostRefusal):
        M.assemble_global_ledger(bad, owners, PRODUCER, CKPT)
    missing = copy.deepcopy(ledgers)
    del missing["AWS"][5]["scientific_content_hash"]
    with pytest.raises(M.MultiHostRefusal):
        M.assemble_global_ledger(missing, owners, PRODUCER, CKPT)


def test_15_wrong_obligation_conservation(owners, ledgers):
    bad = copy.deepcopy(ledgers)
    bad["VULTR"][0]["obligations_completed"] = 27
    with pytest.raises(M.MultiHostRefusal):
        M.assemble_global_ledger(bad, owners, PRODUCER, CKPT)


def test_16_corrupted_aggregate_ledger(owners, ledgers):
    out = M.assemble_global_ledger(ledgers, owners, PRODUCER, CKPT)
    with pytest.raises(M.MultiHostRefusal):
        M.verify_aggregate_ledger(out, "0" * 64)


def test_17_foreign_checkpoint_and_runtime_in_record(owners, ledgers):
    bad = copy.deepcopy(ledgers)
    bad["AWS"][0]["checkpoint_sha256"] = "c" * 64
    with pytest.raises(M.MultiHostRefusal):
        M.assemble_global_ledger(bad, owners, PRODUCER, CKPT)
    bad2 = copy.deepcopy(ledgers)
    bad2["VULTR"][0]["runtime_contract_hash"] = M.ROLES["AWS"]["runtime_contract_hash"]
    with pytest.raises(M.MultiHostRefusal):
        M.assemble_global_ledger(bad2, owners, PRODUCER, CKPT)


def test_09b_authorised_producer_commit_is_accepted():
    """Positive control: the binding must ADMIT the authorised checkout, so the
    refusal in test_09 is a real discrimination and not a blanket failure."""
    lm = json.loads((NS / "config/LAUNCH_MANIFEST.json").read_text())
    pc = lm["producer_commit"]
    assert M.gate_producer_commit(lm, pc, CKPT, SHARD_SHA) == pc


def test_09c_launch_manifest_must_stay_result_free():
    lm = json.loads((NS / "config/LAUNCH_MANIFEST.json").read_text())
    bad = dict(lm, result_bearing=True)
    with pytest.raises(M.MultiHostRefusal):
        M.gate_producer_commit(bad, bad["producer_commit"], CKPT, SHARD_SHA)
    bad2 = dict(lm, shard_manifest_sha256="0" * 64)
    with pytest.raises(M.MultiHostRefusal):
        M.gate_producer_commit(bad2, bad2["producer_commit"], CKPT, SHARD_SHA)
