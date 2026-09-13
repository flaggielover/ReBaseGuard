"""Deterministic unit tests for the generation-2 runtime isolation successor. No systemd, no science."""
import json
import sys
from pathlib import Path

import pytest

NS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(NS / "driver"))
import generation_paths as GP  # noqa: E402
import ps1_reconcile as RC  # noqa: E402

PID = 4242


def contract(tmp, legacy=True):
    c = {"hosts": {"AWS": {"runtime_dir": str(tmp / "rt-gen2"), "production_root": str(tmp / "prod-gen2"),
                           "ops_root": str(tmp / "ops")}},
         "execution_generation": {"predecessor_production_root": str(tmp / "prod-gen1")}}
    if legacy:
        c["runtime_isolation"] = {"legacy_bound_roots": {"AWS": {
            "work_dirs": [str(tmp / "rt-gen1" / "work")], "evidence_dirs": [str(tmp / "rt-gen1" / "evidence")]}}}
    return c


def auth(tmp):
    return {"schema": "x", "producer_commit": "abc", "hosts": {"AWS": {
        "work_dir": str(tmp / "rt-gen1" / "work"), "evidence_dir": str(tmp / "rt-gen1" / "evidence"),
        "workers": 16, "core_assignment": list(range(16)), "environment": {"OMP_NUM_THREADS": "1"}}}}


def marker(d: Path, cell: int, pid=PID):
    d.mkdir(parents=True, exist_ok=True)
    (d / f"cell_done_{cell:04d}.json").write_text(json.dumps(
        {"marker_schema": RC.MARKER_SCHEMA, "cell_id": cell, "launcher_pid": pid, "synthetic": True}))


def test_every_path_derives_from_the_one_runtime_root(tmp_path):
    p = GP.GenerationPaths.for_host(contract(tmp_path), "AWS")
    rt = tmp_path / "rt-gen2"
    assert p.work_root == rt / "work" and p.evidence_root == rt / "evidence"
    assert p.drain_flag == rt / "work" / "DRAIN"
    for v in (p.checkpoints, p.export_stage, p.export_src, p.drain_archive):
        assert str(v).startswith(str(rt))
    assert GP.gate_isolation(contract(tmp_path), "AWS", p)["isolated"] is True


def test_rebinding_changes_exactly_two_keys_and_never_the_original(tmp_path):
    a = auth(tmp_path)
    before = json.dumps(a, sort_keys=True)
    p = GP.GenerationPaths.for_host(contract(tmp_path), "AWS")
    b = GP.rebind_authorization(a, "AWS", p)
    assert json.dumps(a, sort_keys=True) == before, "the frozen authorization object must not mutate"
    assert b["hosts"]["AWS"]["work_dir"] == str(p.work_root)
    assert b["hosts"]["AWS"]["evidence_dir"] == str(p.evidence_root)
    for k in ("workers", "core_assignment", "environment"):
        assert b["hosts"]["AWS"][k] == a["hosts"]["AWS"][k]
    assert b["producer_commit"] == a["producer_commit"]
    rec = GP.rebinding_record(a, "AWS", p)
    assert rec["changed"] == ["evidence_dir", "work_dir"] and rec["scientific_identity_changed"] is False


def test_drain_flag_polled_equals_drain_flag_written(tmp_path):
    """The defect in one line: launcher DRAIN (authorization) must equal prodctl DRAIN (contract)."""
    c, a = contract(tmp_path), auth(tmp_path)
    p = GP.GenerationPaths.for_host(c, "AWS")
    launcher_polls_unrepaired = Path(a["hosts"]["AWS"]["work_dir"]) / "DRAIN"
    prodctl_writes = Path(c["hosts"]["AWS"]["runtime_dir"]) / "work" / "DRAIN"
    assert launcher_polls_unrepaired != prodctl_writes, "precondition: the generation-2 split"
    launcher_polls_repaired = Path(GP.rebind_authorization(a, "AWS", p)["hosts"]["AWS"]["work_dir"]) / "DRAIN"
    assert launcher_polls_repaired == prodctl_writes == p.drain_flag


@pytest.mark.parametrize("bad", ["inside_production_root", "aliases_legacy", "aliases_predecessor"])
def test_isolation_gate_fails_closed(tmp_path, bad):
    c = contract(tmp_path)
    if bad == "inside_production_root":
        c["hosts"]["AWS"]["runtime_dir"] = str(tmp_path / "prod-gen2" / "rt")
    elif bad == "aliases_legacy":
        c["hosts"]["AWS"]["runtime_dir"] = str(tmp_path / "rt-gen1")
    else:
        c["hosts"]["AWS"]["runtime_dir"] = str(tmp_path / "prod-gen1" / "rt")
    with pytest.raises(GP.IsolationRefusal):
        GP.gate_isolation(c, "AWS", GP.GenerationPaths.for_host(c, "AWS"))


def test_reconcile_scans_generation_root_then_legacy_root(tmp_path):
    c = contract(tmp_path)
    p = GP.GenerationPaths.for_host(c, "AWS")
    marker(p.evidence_root / "run" / "g0000", 1)
    marker(tmp_path / "rt-gen1" / "evidence" / "run" / "g0004", 5)
    marker(tmp_path / "rt-gen1" / "evidence" / "old" / "g0008", 9, pid=999)      # another run
    found = RC._markers(c["hosts"]["AWS"], PID, roots=p.marker_roots())
    assert sorted(found) == [1, 5], "pid-bound markers in both roots, never another run's"
    assert RC._markers(c["hosts"]["AWS"], PID) .keys() == {1}, "default stays the contract root"


def test_generation_root_wins_over_legacy_duplicate(tmp_path):
    c = contract(tmp_path)
    p = GP.GenerationPaths.for_host(c, "AWS")
    marker(p.evidence_root / "run" / "g0000", 3)
    marker(tmp_path / "rt-gen1" / "evidence" / "run" / "g0000", 3)
    path, _ = RC._markers(c["hosts"]["AWS"], PID, roots=p.marker_roots())[3]
    assert str(path).startswith(str(p.evidence_root))


def test_legacy_drain_flag_is_reported_not_polled(tmp_path):
    c = contract(tmp_path)
    p = GP.GenerationPaths.for_host(c, "AWS")
    (tmp_path / "rt-gen1" / "work").mkdir(parents=True)
    (tmp_path / "rt-gen1" / "work" / "DRAIN").write_text("{}")
    assert p.legacy_drain_flags() == [str(tmp_path / "rt-gen1" / "work" / "DRAIN")]
    assert not p.drain_flag.exists()


def test_generated_ops_carry_every_anchor():
    """Guards against a regenerated file silently losing a repair."""
    ops = NS / "ops"
    assert "GP.rebind_authorization" in (ops / "produce_entry.py").read_text()
    sup = (ops / "supervisor.py").read_text()
    assert "STALE_DRAIN_FLAG" in sup and "gate_isolation" in sup and "ps1_cellseq_worker.py" in sup
    pc = (ops / "prodctl.py").read_text()
    assert '"clear-drain"' in pc and 'auth["hosts"][role]["evidence_dir"]' not in pc
    assert 'p5y_k1_ps1_portable_recovery" / "driver"' not in pc
    assert "marker_roots()" in (NS / "driver" / "ps1_reconcile.py").read_text()
