"""Result-free tests for the SR driver-bound successor.

NOTHING here performs scientific production. Every test uses the frozen
checkpoint, mocks, or tiny synthetic fixtures. The governing property is:
EVERY invalid configuration FAILS CLOSED.
"""
from __future__ import annotations

import copy
import json
import os
import sys
from pathlib import Path

import pytest

NS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(NS / "driver"))

import gates                                                        # noqa: E402
import ledger as L                                                  # noqa: E402
import sr_production_driver as D                                    # noqa: E402
from gates import GateFailure                                       # noqa: E402

CP_PATH = NS / "config/PRE_RESULT_CHECKPOINT.json"
GOOD_ENV = {v: "1" for v in gates.THREAD_VARS}


@pytest.fixture
def cp():
    return gates.load_checkpoint(CP_PATH)


def reseal(c):
    """Recompute the self-hash so a MUTATED checkpoint is still loadable."""
    c = copy.deepcopy(c)
    c["checkpoint_sha256"] = None
    c["checkpoint_sha256"] = gates.hashlib.sha256(
        gates.canonical({k: v for k, v in c.items() if k != "checkpoint_sha256"})
    ).hexdigest()
    return c


# ---------------------------------------------------------------- checkpoint
def test_checkpoint_self_hash_valid(cp):
    assert cp["checkpoint_sha256"]
    assert cp["production_state"]["production_enabled"] is False
    assert cp["production_state"]["result_bearing"] is False


def test_corrupted_checkpoint_hash_fails_closed(tmp_path):
    c = json.loads(CP_PATH.read_text())
    c["checkpoint_sha256"] = "0" * 64
    p = tmp_path / "cp.json"
    p.write_text(json.dumps(c))
    with pytest.raises(GateFailure, match="self-hash mismatch"):
        gates.load_checkpoint(p)


def test_tampered_checkpoint_body_fails_closed(tmp_path):
    c = json.loads(CP_PATH.read_text())
    c["compute_cap"]["cap_cpu_h"] = 99999.0          # body changed, hash stale
    p = tmp_path / "cp.json"
    p.write_text(json.dumps(c))
    with pytest.raises(GateFailure, match="self-hash mismatch"):
        gates.load_checkpoint(p)


def test_missing_checkpoint_fails_closed(tmp_path):
    with pytest.raises(GateFailure, match="absent"):
        gates.load_checkpoint(tmp_path / "nope.json")


# -------------------------------------------------------------------- threads
def test_thread_contract_ok(cp):
    assert gates.gate_threads(cp, env=GOOD_ENV)["value"] == "1"


@pytest.mark.parametrize("var", list(gates.THREAD_VARS))
def test_each_wrong_thread_var_fails_closed(cp, var):
    env = dict(GOOD_ENV)
    env[var] = "2"
    with pytest.raises(GateFailure, match="thread contract violated"):
        gates.gate_threads(cp, env=env)


@pytest.mark.parametrize("var", list(gates.THREAD_VARS))
def test_each_missing_thread_var_fails_closed(cp, var):
    env = dict(GOOD_ENV)
    del env[var]
    with pytest.raises(GateFailure, match="thread contract violated"):
        gates.gate_threads(cp, env=env)


def test_thread_variable_set_drift_fails_closed(cp):
    c = reseal({**cp, "thread_contract": {**cp["thread_contract"],
                                          "variables": ["OMP_NUM_THREADS"]}})
    with pytest.raises(GateFailure, match="drifted"):
        gates.gate_threads(c, env=GOOD_ENV)


# ------------------------------------------------------------------- topology
CORES16 = list(range(16))


def test_topology_ok(cp):
    r = gates.gate_topology(cp, cores=CORES16)
    assert r["workers"] == 16 and r["smt_used"] is False


def test_too_few_physical_cores_fails_closed(cp):
    with pytest.raises(GateFailure, match="physical cores"):
        gates.gate_topology(cp, cores=list(range(8)))


def test_wrong_worker_count_fails_closed(cp):
    for n in (1, 8, 15, 17, 24, 32):
        c = reseal({**cp, "worker_topology": {**cp["worker_topology"], "workers": n}})
        with pytest.raises(GateFailure):
            gates.gate_topology(c, cores=CORES16)


def test_smt_siblings_rejected(cp):
    c = reseal({**cp, "worker_topology": {**cp["worker_topology"],
                                          "use_smt_siblings": True}})
    with pytest.raises(GateFailure, match="SMT"):
        gates.gate_topology(c, cores=CORES16)


def test_nondeterministic_core_assignment_fails_closed(cp):
    c = reseal({**cp, "worker_topology": {**cp["worker_topology"],
                                          "core_assignment": list(range(16, 32))}})
    with pytest.raises(GateFailure, match="core assignment"):
        gates.gate_topology(c, cores=CORES16)


def test_physical_cores_excludes_smt_siblings(tmp_path):
    """Synthetic sysfs: 4 physical cores, each with an SMT sibling."""
    for cpu in range(8):
        d = tmp_path / f"cpu{cpu}" / "topology"
        d.mkdir(parents=True)
        core = cpu % 4
        (d / "thread_siblings_list").write_text(f"{core},{core + 4}\n")
    assert gates.physical_cores(tmp_path) == [0, 1, 2, 3]


# ------------------------------------------------------------------- cap
def mk_ledger(tmp_path, **kw):
    d = dict(cap_cpu_h=4500.0, overhead=1.15, cusum_cpu_h=206.086,
             reserve_cpu_h=11.475)
    d.update(kw)
    return L.CapLedger(tmp_path / "cap.json", d["cap_cpu_h"], d["overhead"],
                       d["cusum_cpu_h"], reserve_cpu_h=d["reserve_cpu_h"])


def test_cap_starts_with_cusum_charged(tmp_path):
    lg = mk_ledger(tmp_path)
    assert lg.charged_cpu_h() == pytest.approx(1.15 * 206.086)
    assert lg.remaining_cpu_h() < 4500.0


def test_cap_admits_when_room(tmp_path):
    mk_ledger(tmp_path).admit(n_in_flight=16)


def test_cap_near_exhaustion_refuses_before_starting(tmp_path):
    lg = mk_ledger(tmp_path)
    lg.state["raw_sr_cpu_seconds"] = (4500.0 / 1.15 - 206.086) * 3600 - 10.0
    with pytest.raises(L.CapExceeded):
        lg.admit(n_in_flight=16)


def test_cap_overrun_is_persisted_and_raises(tmp_path):
    lg = mk_ledger(tmp_path)
    with pytest.raises(L.CapExceeded):
        lg.charge(cell_id=0, cpu_seconds=4500 * 3600, record_sha256="x")
    assert json.loads((tmp_path / "cap.json").read_text())["entries"]


def test_cap_ledger_drift_fails_closed(tmp_path):
    mk_ledger(tmp_path)
    with pytest.raises(GateFailure, match="drift"):
        L.CapLedger(tmp_path / "cap.json", 9999.0, 1.15, 206.086, reserve_cpu_h=1.0)


def test_cap_accounting_is_conservative(tmp_path):
    lg = mk_ledger(tmp_path)
    before = lg.charged_cpu_h()
    lg.charge(cell_id=1, cpu_seconds=3600.0, record_sha256="x")
    assert lg.charged_cpu_h() == pytest.approx(before + 1.15)   # overhead applied


# ------------------------------------------------------------------- resume
IDENT = {"producer_commit": "c" * 40, "checkpoint_sha256": "d" * 64,
         "runtime_contract_hash": "e" * 64}


def mk_record(cell_id, **kw):
    r = {**IDENT, "cell_id": cell_id, "scientific_content_hash": "s" * 64,
         "auxiliary_evidence_hash": "a" * 64, "cpu_seconds": 10.0,
         "wall_seconds": 10.0, "peak_rss_kib": 1000, "worker_id": 0,
         "core_id": 0, "retry_count": 0, "obligations_completed": 28}
    r.update(kw)
    return r


def test_commit_and_resume(tmp_path):
    st = L.CellStore(tmp_path, IDENT)
    st.commit(mk_record(0))
    assert st.is_done(0)
    plan = st.resume_plan([0, 1, 2])
    assert plan["n_completed"] == 1 and plan["remaining"] == [1, 2]


def test_duplicate_cell_rejected(tmp_path):
    st = L.CellStore(tmp_path, IDENT)
    st.commit(mk_record(0))
    with pytest.raises(L.DuplicateCell):
        st.commit(mk_record(0))


def test_partial_cell_never_counts(tmp_path):
    st = L.CellStore(tmp_path, IDENT)
    st.cells.mkdir(parents=True, exist_ok=True)
    (st.cells / "sr_CELL_7_256.json").write_text('{"cell_id": 7, "cell_comp')
    assert st.is_done(7) is False
    assert st.resume_plan([7])["remaining"] == [7]


def test_record_without_complete_flag_never_counts(tmp_path):
    st = L.CellStore(tmp_path, IDENT)
    r = mk_record(9)
    r["cell_complete"] = False
    L.atomic_write_json(st.path_for(9), r)
    assert st.is_done(9) is False


def test_foreign_identity_record_ignored(tmp_path):
    st = L.CellStore(tmp_path, IDENT)
    bad = mk_record(3, producer_commit="f" * 40)
    L.atomic_write_json(st.path_for(3), {**bad, "cell_complete": True})
    assert st.is_done(3) is False


def test_commit_with_foreign_identity_fails_closed(tmp_path):
    st = L.CellStore(tmp_path, IDENT)
    with pytest.raises(GateFailure, match="identity"):
        st.commit(mk_record(4, runtime_contract_hash="0" * 64))


@pytest.mark.parametrize("field", ["cell_id", "scientific_content_hash",
                                   "auxiliary_evidence_hash", "cpu_seconds",
                                   "wall_seconds", "peak_rss_kib", "worker_id",
                                   "core_id", "retry_count",
                                   "obligations_completed"])
def test_missing_binding_field_fails_closed(tmp_path, field):
    st = L.CellStore(tmp_path, IDENT)
    r = mk_record(5)
    del r[field]
    with pytest.raises(GateFailure, match="missing required binding field"):
        st.commit(r)


def test_interrupted_cell_resume_simulation(tmp_path):
    """Abrupt loss: 16 in-flight cells lose at most one cell each."""
    st = L.CellStore(tmp_path, IDENT)
    for c in range(10):
        st.commit(mk_record(c))
    for c in range(10, 26):                       # 16 torn, in-flight files
        (st.cells / f"sr_CELL_{c}_256.json").write_text('{"cell_id": ' + str(c))
    plan = st.resume_plan(list(range(30)))
    assert plan["n_completed"] == 10
    assert plan["remaining"] == list(range(10, 30))


def test_resume_journal_is_audit_visible(tmp_path):
    st = L.CellStore(tmp_path, IDENT)
    st.commit(mk_record(0))
    st.resume_plan([0, 1])
    events = [json.loads(l) for l in st.journal.read_text().splitlines()]
    assert {"cell_committed", "resume_plan"} <= {e["event"] for e in events}


# ------------------------------------------------------------------- scope
def test_dry_run_plan_enumerates_frozen_campaign(cp):
    fake = {"D_topology": {"core_assignment": list(range(16))}}
    plan = D.build_plan(cp, fake)
    assert plan["cells"] == 316
    assert plan["total_obligations"] == 8849
    assert plan["obligations_per_cell"] == 28
    assert plan["contracts_per_cell"] == 102
    assert plan["workers"] == 16
    assert sum(plan["shard_sizes"]) == 316
    assert plan["exact_partition"] is True
    assert plan["precision_bits"] == 256
    assert plan["backend"] == "O9"
    assert plan["panel_contract_evaluations"] == 102 * 316 * 83452
    assert plan["scientific_computation_performed"] is False


def test_shard_partition_is_exact_for_16(cp):
    ids = D.cell_ids(cp)
    shards = D.shard_cells(ids, 16)
    assert [c for s in shards for c in s] == ids
    assert len({c for s in shards for c in s}) == 316


def test_cover_drift_fails_closed(cp):
    c = reseal({**cp, "cover": {**cp["cover"], "cell_ids": cp["cover"]["cell_ids"][:-1]}})
    with pytest.raises(GateFailure, match="cells"):
        D.build_plan(c, {"D_topology": {"core_assignment": list(range(16))}})


def test_duplicate_cell_id_in_cover_fails_closed(cp):
    ids = list(cp["cover"]["cell_ids"])
    ids[1] = ids[0]
    c = reseal({**cp, "cover": {**cp["cover"], "cell_ids": ids}})
    with pytest.raises(GateFailure, match="duplicate cell id"):
        D.build_plan(c, {"D_topology": {"core_assignment": list(range(16))}})


def test_obligation_conservation_drift_fails_closed(cp):
    c = reseal({**cp, "frozen_scope": {**cp["frozen_scope"], "obligations": 8850}})
    with pytest.raises(GateFailure, match="obligation conservation"):
        D.build_plan(c, {"D_topology": {"core_assignment": list(range(16))}})


# ------------------------------------------------------------------- runtime
def test_wrong_runtime_hash_fails_closed(cp, monkeypatch):
    c = reseal({**cp, "runtime_identity": {**cp["runtime_identity"],
                "required_runtime_contract_hash": "0" * 64}})
    with pytest.raises(GateFailure, match="runtime contract"):
        gates.gate_runtime(c)


def test_non_aws_host_fails_closed(cp, monkeypatch, tmp_path):
    c = reseal({**cp, "host_scope": {**cp["host_scope"],
                                     "accepted_sys_vendor": ["Definitely Not AWS"]}})
    with pytest.raises(GateFailure, match="AWS_ONLY"):
        gates.gate_runtime(c)


def test_host_scope_must_be_aws_only(cp):
    c = reseal({**cp, "host_scope": {**cp["host_scope"], "scope": "ANY"}})
    with pytest.raises(GateFailure, match="AWS_ONLY"):
        gates.gate_runtime(c)


# ------------------------------------------------------------------- producer
def test_wrong_producer_commit_fails_closed(cp):
    c = reseal({**cp, "repository_identity": {**cp["repository_identity"],
                                              "producer_commit": "0" * 40}})
    with pytest.raises(GateFailure, match="producer_commit"):
        gates.gate_repository(c)


def test_wrong_branch_fails_closed(cp):
    c = reseal({**cp, "repository_identity": {**cp["repository_identity"],
                                              "branch": "not-a-branch"}})
    with pytest.raises(GateFailure, match="branch"):
        gates.gate_repository(c)


def test_corrupted_bound_artifact_fails_closed(cp):
    c = reseal({**cp, "bound_artifact_sha256": {**cp["bound_artifact_sha256"],
                                                "driver/gates.py": "0" * 64}})
    with pytest.raises(GateFailure, match="bound artifact"):
        gates.gate_repository(c)


# ------------------------------------------------------------------- produce
def test_produce_mode_refuses_while_production_disabled(capsys):
    rc = D.main(["--mode", "produce", "--checkpoint", str(CP_PATH)])
    out = json.loads(capsys.readouterr().out)
    assert rc == 3
    assert out["admitted"] is False
    assert "production_enabled is false" in out["refusal"]


def test_final_assembly_rejects_incomplete(cp, tmp_path):
    st = L.CellStore(tmp_path, cp["campaign_identity"])
    lg = mk_ledger(tmp_path)
    r = D.verify_final_assembly(cp, st, lg)
    assert r["complete"] is False
    assert r["cells_committed"] == 0 and r["cells_expected"] == 316
