"""Phases 5 & 7: durable-marker qualification and idempotence, deterministically.

These exercise the real ps1_reconcile marker filter -- the gate that decides what may ever
become a FINALIZED commit. No systemd, no CPU.
"""
import json
import sys
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(NS / "driver"))
import ps1_reconcile as RC  # noqa: E402

PID = 4242


def marker(d: Path, cell: int, *, pid=PID, schema=RC.MARKER_SCHEMA, final=True, extra=None):
    d.mkdir(parents=True, exist_ok=True)
    m = {"marker_schema": schema, "cell_id": cell, "launcher_pid": pid,
         "task_id": "T1", "run_id": "R1", "ok": True, "synthetic": True,
         "scientific_content_hash": f"hash-{cell}", "evidence_dir": str(d),
         "completed_utc": "2026-09-12T00:00:00Z"}
    m.update(extra or {})
    name = f"cell_done_{cell:04d}.json" if final else f".tmp-cell_done_{cell:04d}.json-1"
    (d / name).write_text(json.dumps(m, sort_keys=True))
    return d / name


def spec_for(tmp): return {"runtime_dir": str(tmp)}


# ---------------------------------------------------------------- Phase 7 case 2 / 5B
def test_durable_final_marker_qualifies(tmp_path):
    marker(tmp_path / "evidence" / "run1" / "g0000", 1)
    found = RC._markers(spec_for(tmp_path), PID)
    assert set(found) == {1}


# ------------------------------------------- Phase 5D / Phase 7 case 1: temp never counts
def test_temp_marker_never_qualifies(tmp_path):
    marker(tmp_path / "evidence" / "run1" / "g0000", 2, final=False)
    assert RC._markers(spec_for(tmp_path), PID) == {}, "a .tmp- marker must never qualify"


def test_truncated_marker_never_qualifies(tmp_path):
    d = tmp_path / "evidence" / "run1" / "g0000"
    d.mkdir(parents=True)
    (d / "cell_done_0003.json").write_text('{"marker_schema": "rebase')   # torn mid-write
    assert RC._markers(spec_for(tmp_path), PID) == {}


# ------------------------------------------------ Phase 5F: wrong run/generation rejected
def test_marker_from_another_run_is_rejected(tmp_path):
    marker(tmp_path / "evidence" / "old" / "g0000", 4, pid=999)
    assert RC._markers(spec_for(tmp_path), PID) == {}, "a marker from another run must not replay"
    assert set(RC._markers(spec_for(tmp_path), 999)) == {4}


def test_wrong_schema_is_rejected(tmp_path):
    marker(tmp_path / "evidence" / "run1" / "g0000", 5, schema="something.else.v9")
    assert RC._markers(spec_for(tmp_path), PID) == {}


# --------------------------------------------------------------- mixed / selective
def test_only_matching_run_survives_a_mixed_tree(tmp_path):
    marker(tmp_path / "evidence" / "run1" / "g0000", 10)
    marker(tmp_path / "evidence" / "run1" / "g0004", 11)
    marker(tmp_path / "evidence" / "old" / "g0000", 12, pid=999)
    marker(tmp_path / "evidence" / "run1" / "g0008", 13, final=False)
    found = RC._markers(spec_for(tmp_path), PID)
    assert sorted(found) == [10, 11], "only durable markers bound to THIS run may qualify"


def test_no_evidence_root_is_safe(tmp_path):
    assert RC._markers(spec_for(tmp_path), PID) == {}


def test_marker_binding_fields_present(tmp_path):
    p = marker(tmp_path / "evidence" / "run1" / "g0000", 7)
    m = json.loads(p.read_text())
    for k in ("marker_schema", "cell_id", "launcher_pid", "task_id",
              "scientific_content_hash", "completed_utc"):
        assert k in m, f"marker must bind {k}"
