"""Focused tests for EXECUTION_GENERATION_LEDGER_NAMESPACE_DEFECT."""
import hashlib, json, sys
from pathlib import Path
import pytest

NS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(NS / "code"))
sys.path.insert(0, str(NS / "ops"))
import make_generation2 as G2  # noqa: E402

GEN1_LEDGER = Path("/home/ubuntu/work/ReBaseGuard-ps1-prod/level4/closure_proofs/"
                   "p5y_k1_ps1_production/production/PRODUCTION_LEDGER.json")
GEN1_SHA = "0557bc229c3fcdb10cb0dd0b5836fa62a6b0e6c2512656e6ec7e49294b4d6cab"
TR = NS / "config" / "GENERATION_TRANSITION.json"


def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()


# 1 / 2 -- generation 1 immutable and still halted
def test_generation1_ledger_unchanged_byte_for_byte():
    assert sha(GEN1_LEDGER) == GEN1_SHA


def test_generation1_remains_halted_retry_limit():
    st = json.loads(GEN1_LEDGER.read_text())
    ops = st["operational_lifecycle"]
    assert ops["halt"]["reason"] == "RETRY_LIMIT"
    assert set(str(c) for c in range(64)) <= set(ops["torn_attempts"])
    assert all(ops["torn_attempts"][str(c)] == 3 for c in range(64))
    assert st["completed_cells"] == {}


# 3-6 -- generation 2 initial state
def _init():
    return G2.initial_ledger("rebaseguard.p5y.k1.global-budget.v1", "ops.v1", "AWS")


def test_generation2_initializes_ready_halt_null():
    st = _init()
    assert st["operational_lifecycle"]["halt"] is None


def test_generation2_finalized_zero_and_no_reservations():
    st = _init()
    assert st["completed_cells"] == {} and st["open_reservations"] == {}
    assert st["operational_lifecycle"]["runs"] == {}


def test_generation2_torn_counters_start_empty():
    assert _init()["operational_lifecycle"]["torn_attempts"] == {}


# 7 -- historical CPU imported, never below
def test_historical_cpu_imported_and_floor_enforced():
    st = _init()
    assert st["committed_cpu_h_by_role"]["AWS"] == 92.32
    tr = G2.transition_record()
    assert tr["accounting_import"]["predecessor_science_cpu_h"] == 92.32
    assert tr["accounting_import"]["global_cpu_cap"] == 6600.0


# 8 -- predecessor lineage visible but not active
def test_predecessor_lineage_visible_but_not_active_halt():
    tr = G2.transition_record()
    assert tr["predecessor"]["torn_attempt_lineage"] == {"cells_0_to_63": 3}
    assert tr["predecessor"]["final_phase"] == "HALTED"
    assert _init()["operational_lifecycle"]["halt"] is None, \
        "predecessor halt must never become generation-2's active halt"


# 9 / 10 -- separate retry accounting; drain not a tear
def test_retry_accounting_is_separated():
    ra = G2.transition_record()["retry_accounting"]
    assert ra["graceful_drain_is_a_tear"] is False
    assert ra["max_infra_tears_per_cell_generation_2"] == 3
    assert "never overwritten" in ra["generation_1_torn_counters"]


# 3 -- supersession is additive, not a clear
def test_halt_supersession_is_not_a_clear():
    s = G2.transition_record()["halt_supersession"]
    assert s["record"] == "PREDECESSOR_HALT_SUPERSEDED_FOR_NEW_EXECUTION_GENERATION"
    assert s["immutable"] is True and s["pre_result"] is True
    assert "NOT cleared" in s["not_a_clear"]
    assert len(s["grounds"]) >= 5


# 12 / 13 -- cross-generation aliasing fails closed
def test_generation_roots_are_disjoint():
    tr = G2.transition_record()
    p1 = Path(tr["predecessor"]["production_root"]).resolve()
    p2 = Path(tr["generation_2"]["production_root"]).resolve()
    assert p1 != p2 and p1 not in p2.parents and p2 not in p1.parents


def test_contract_binds_generation2_roots():
    c = json.loads((NS / "config" / "OPERATIONAL_CONTRACT.json").read_text())
    tr = G2.transition_record()
    assert c["hosts"]["AWS"]["production_root"] == tr["generation_2"]["production_root"]
    assert c["hosts"]["AWS"]["runtime_dir"] == tr["generation_2"]["runtime_dir"]
    eg = c["execution_generation"]
    assert eg["generation"] == 2
    assert eg["predecessor_ledger_sha256"] == GEN1_SHA
    assert eg["transition_record_sha256"] == sha(TR)


# 11 -- checkpoint lineage
def test_transition_record_hash_is_external_and_stable():
    assert (NS / "config" / "GENERATION_TRANSITION_HASH").read_text().strip() == sha(TR)
    assert "_sha256" not in json.loads(TR.read_text())


# 14 -- no scientific drift
def test_no_scientific_source_changed():
    prod = Path("/home/ubuntu/work/ReBaseGuard-ps1-prod")
    auth = json.loads((prod / "level4/closure_proofs/p5y_k1_ps1_production/config/"
                       "LAUNCH_AUTHORIZATION.json").read_text())
    wt = Path("/home/ubuntu/work/ReBaseGuard-sr-o9-t1")
    assert [r for r in auth["executor_source_manifest"] if sha(prod / r) != sha(wt / r)] == []
    assert auth["scientific_adapter_hash"] == \
        "13ba2ecd1c8afdaafb3463233f246716f599dd935c5b3722f4074327d8eec5fd"
