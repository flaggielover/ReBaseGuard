"""Result-free fail-closed tests for the multi-host CAP REPAIR successor.

Inherits the predecessor suite unchanged except for the prohibited per-host cap
test, which is replaced by the global-cap-only semantics suite (A-H).

Every invalid case MUST raise MultiHostRefusal. No test performs scientific
computation and no test emits a result-bearing SR cell.
"""
import copy
import json
import math
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


def _ledgers_with(manifest, aws_cpu_s, vultr_cpu_s):
    """Ledgers over the frozen 247/69 shard at chosen per-cell CPU charges."""
    aws = [record(c, "AWS", aws_cpu_s) for c in manifest["AWS"]["cells"]]
    vul = [record(c, "VULTR", vultr_cpu_s) for c in manifest["VULTR"]["cells"]]
    aws[0]["obligations_completed"] = 29
    return {"AWS": aws, "VULTR": vul}


# ---- Codex counterexample, exactly as adjudicated -------------------------
def test_12_codex_counterexample_11_cpuh_vultr_cell(manifest, owners):
    """A single Vultr cell charged 11 CPU-h exceeds the former per-cell
    reservation of 10.217741 CPU-h. The predecessor's gate_per_host_reservation
    refused it (allowed = 10.217741 * 1 record). The governed campaign total is
    only ~249.6489 CPU-h, far under the ONE 4500 CPU-h cap, so it MUST be
    admitted. The repaired module has no such gate at all."""
    one = [record(manifest["VULTR"]["cells"][0], "VULTR", 11 * 3600.0)]
    assert not hasattr(M, "gate_per_host_reservation")
    acct = M.host_accounting("VULTR", one)                 # must NOT raise
    assert acct["cpu_h"] == pytest.approx(11.0)
    assert acct["projected_share_cpu_h"] == pytest.approx(10.217741105316279)
    assert acct["over_projected_share"] is True            # warning only
    assert acct["enforcement"] == "ACCOUNTING_ONLY"
    cap = M.gate_global_cap({"VULTR": 11.0, "AWS": 0.0})   # must NOT raise
    assert cap["charged_cpu_h"] == pytest.approx(249.6489, abs=1e-3)
    assert cap["charged_cpu_h"] <= M.GLOBAL_CPU_CAP


# ---- A. Vultr over its projected share, global under cap -> PASS ------------
def test_12A_vultr_over_projected_share_but_global_under_cap_passes(manifest, owners):
    """Vultr consumes 828 CPU-h against a 705.02 CPU-h projected share while AWS
    uses less than its own. Globally admissible, so it MUST pass."""
    led = _ledgers_with(manifest, aws_cpu_s=5.0 * 3600.0, vultr_cpu_s=12.0 * 3600.0)
    out = M.assemble_global_ledger(led, owners, PRODUCER, CKPT)
    acc = out["host_accounting"]
    assert acc["VULTR"]["over_projected_share"] is True
    assert acc["AWS"]["over_projected_share"] is False
    assert out["hosts_over_projected_share"] == ["VULTR"]
    assert out["cap"]["charged_cpu_h"] <= M.GLOBAL_CPU_CAP


# ---- B. AWS over its projected share, global under cap -> PASS --------------
def test_12B_aws_over_projected_share_but_global_under_cap_passes(manifest, owners):
    led = _ledgers_with(manifest, aws_cpu_s=13.0 * 3600.0, vultr_cpu_s=5.0 * 3600.0)
    out = M.assemble_global_ledger(led, owners, PRODUCER, CKPT)
    acc = out["host_accounting"]
    assert acc["AWS"]["over_projected_share"] is True
    assert acc["VULTR"]["over_projected_share"] is False
    assert out["hosts_over_projected_share"] == ["AWS"]
    assert out["cap"]["charged_cpu_h"] <= M.GLOBAL_CPU_CAP


# ---- C. BOTH hosts over their projected shares, aggregate under cap -> PASS --
def test_12C_both_hosts_over_projected_share_but_aggregate_under_cap_passes(manifest, owners):
    led = _ledgers_with(manifest, aws_cpu_s=11.8 * 3600.0, vultr_cpu_s=11.0 * 3600.0)
    out = M.assemble_global_ledger(led, owners, PRODUCER, CKPT)
    acc = out["host_accounting"]
    assert acc["AWS"]["over_projected_share"] and acc["VULTR"]["over_projected_share"]
    assert sorted(out["hosts_over_projected_share"]) == ["AWS", "VULTR"]
    assert out["cap"]["charged_cpu_h"] <= M.GLOBAL_CPU_CAP


# ---- D. aggregate comfortably below the cap -> PASS --------------------------
def test_12D_aggregate_below_cap_passes(manifest, owners):
    led = _ledgers_with(manifest, aws_cpu_s=11.0 * 3600.0, vultr_cpu_s=10.0 * 3600.0)
    out = M.assemble_global_ledger(led, owners, PRODUCER, CKPT)
    assert out["cap"]["charged_cpu_h"] < M.GLOBAL_CPU_CAP
    assert out["cap"]["headroom_cpu_h"] > 0


# ---- E. exactly at the frozen acceptance boundary: <= is admitted ------------
def _sr_hitting_cap_exactly():
    sr = M.GLOBAL_CPU_CAP / M.OVERHEAD_FACTOR
    for _ in range(256):
        charged = M.OVERHEAD_FACTOR * (sr + 0.0)
        if charged == M.GLOBAL_CPU_CAP:
            return sr
        sr = math.nextafter(sr, 0.0 if charged > M.GLOBAL_CPU_CAP else math.inf)
    raise AssertionError("no float lands exactly on the cap")


def test_12E_exactly_at_cap_follows_frozen_le_convention(manifest, owners):
    """The frozen convention is `charged > cap` refuses, so charged == cap is
    ADMITTED. That convention is preserved exactly."""
    sr = _sr_hitting_cap_exactly()
    assert M.OVERHEAD_FACTOR * sr == M.GLOBAL_CPU_CAP
    out = M.gate_global_cap({"AWS": sr}, governed_overhead_cpu_h=0.0)
    assert out["charged_cpu_h"] == M.GLOBAL_CPU_CAP
    assert out["headroom_cpu_h"] == 0.0
    assert out["enforcement"] == "GLOBAL_HARD_LIMIT"


# ---- F. aggregate above the cap -> FAIL CLOSED -------------------------------
def test_12F_above_cap_fails_closed(manifest, owners):
    sr = math.nextafter(_sr_hitting_cap_exactly(), math.inf)
    with pytest.raises(M.MultiHostRefusal):
        M.gate_global_cap({"AWS": sr}, governed_overhead_cpu_h=0.0)
    led = _ledgers_with(manifest, aws_cpu_s=15.0 * 3600.0, vultr_cpu_s=15.0 * 3600.0)
    with pytest.raises(M.MultiHostRefusal):
        M.assemble_global_ledger(led, owners, PRODUCER, CKPT)


# ---- G. per-host accounting that does not reconcile -> FAIL CLOSED -----------
def test_12G_corrupted_host_accounting_fails_closed(manifest, owners, ledgers):
    accounts = {r: M.host_accounting(r, recs) for r, recs in ledgers.items()}
    assert M.reconcile_accounting(accounts, ledgers) > 0
    understated = copy.deepcopy(accounts)
    understated["VULTR"]["cpu_h"] = 0.0                  # hide real spend
    with pytest.raises(M.MultiHostRefusal):
        M.reconcile_accounting(understated, ledgers)
    miscounted = copy.deepcopy(accounts)
    miscounted["AWS"]["cells"] = 1
    with pytest.raises(M.MultiHostRefusal):
        M.reconcile_accounting(miscounted, ledgers)
    dropped = copy.deepcopy(accounts)
    del dropped["VULTR"]
    with pytest.raises(M.MultiHostRefusal):
        M.reconcile_accounting(dropped, ledgers)


# ---- H. duplicate / missing / non-physical cost entries -> FAIL CLOSED -------
def test_12H_duplicate_missing_and_nonphysical_costs_fail_closed(manifest, owners, ledgers):
    dup = copy.deepcopy(ledgers)
    dup["AWS"].append(record(manifest["AWS"]["cells"][0], "AWS", 1.0, obligations=0))
    with pytest.raises(M.MultiHostRefusal):
        M.assemble_global_ledger(dup, owners, PRODUCER, CKPT)
    missing = copy.deepcopy(ledgers)
    missing["VULTR"].pop()
    with pytest.raises(M.MultiHostRefusal):
        M.assemble_global_ledger(missing, owners, PRODUCER, CKPT)
    for bad_cost in (float("nan"), float("inf"), -1.0):
        bad = copy.deepcopy(ledgers)
        bad["AWS"][0]["cpu_seconds"] = bad_cost
        with pytest.raises(M.MultiHostRefusal):
            M.assemble_global_ledger(bad, owners, PRODUCER, CKPT)
    nanrole = {"AWS": float("nan"), "VULTR": 1.0}
    with pytest.raises(M.MultiHostRefusal):
        M.gate_global_cap(nanrole)


# ---- audit: the prohibited host hard limit is GONE, not softened -------------
def test_12I_host_hard_limit_is_removed_from_the_module():
    assert not hasattr(M, "gate_per_host_reservation"), \
        "the prohibited per-host hard limit must be removed, not retained"
    assert M.REMOVED_HOST_HARD_LIMITS == ("gate_per_host_reservation",)
    assert M.host_accounting("VULTR", [])["enforcement"] == "ACCOUNTING_ONLY"


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
