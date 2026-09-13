"""Fixture tests for the result-agnostic post-K1 adjudication audit. Synthetic ledgers only; no science."""
import hashlib
import json
import sys
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(NS / "code"))
import ps1_adjudication_audit as AU  # noqa: E402


def canon(o):
    return json.dumps(o, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()


def sha(b):
    return hashlib.sha256(b).hexdigest()


def build(tmp: Path, cells, *, charge=0.5, tamper=None, orphan_marker=None, open_res=None):
    root = tmp / "prod"
    ns = root / AU.NS_REL
    (ns / "production/cells").mkdir(parents=True)
    ev_root = tmp / "rt" / "evidence"
    completed, cpu = {}, 0.0
    for c in cells:
        d = ev_root / "run1" / f"g{c:04d}"
        d.mkdir(parents=True)
        t3 = {"cell": c, "t3_record_sha256": sha(f"t3-{c}".encode()), "T3_PASS": "SECRET"}
        t4 = {"cell": c, "t4_record_sha256": sha(f"t4-{c}".encode()), "B_cover_ratio": "SECRET"}
        t5 = {"cell": c, "status": "SECRET", "obligations": [{"certificate_hash": sha(f"o{k}-{c}".encode())} for k in range(28)]}
        ev = {}
        for name, obj in (("t3", t3), ("t4", t4), ("t5", t5), ("patches_gz", {"p": c})):
            p = d / f"{name}_{c:04d}.json"
            p.write_bytes(canon(obj))
            ev[name] = {"path": str(p), "sha256": sha(p.read_bytes())}
        sch = sha(canon({"t3_record_sha256": t3["t3_record_sha256"], "t4_record_sha256": t4["t4_record_sha256"],
                         "t5_certificate_hashes": [o["certificate_hash"] for o in t5["obligations"]]}) + b"\n")
        rec = {"cell_id": c, "scientific_content_hash": sch, "evidence": ev, "cpu_seconds": 3600.0,
               "successor_id": f"PS1-{c}", "task_id": "run1"}
        cpu += 1.0
        completed[str(c)] = rec
        (ns / f"production/cells/{c:04d}.json").write_bytes(json.dumps(rec, indent=1, sort_keys=True).encode())
        (d / f"cell_done_{c:04d}.json").write_text(json.dumps({"cell_id": c, "run_id": "run1", "launcher_pid": 1,
                                                                "scientific_content_hash": sch}))
    if tamper is not None:
        Path(completed[str(tamper)]["evidence"]["t5"]["path"]).write_bytes(b'{"tampered":1}')
    if orphan_marker is not None:
        d = ev_root / "run2" / "gx"
        d.mkdir(parents=True)
        (d / f"cell_done_{orphan_marker:04d}.json").write_text(json.dumps({"cell_id": orphan_marker, "run_id": "run2"}))
    st = {"schema": "s", "committed_cpu_h_by_role": {"AWS": 92.32 + cpu + charge},
          "open_reservations": open_res or {}, "completed_cells": completed, "remote_completed_cells": {},
          "operational_lifecycle": {"runs": {"r1": {"status": "SETTLED"}}, "settlements": [{"charge_cpu_h": charge}],
                                    "releases": [], "torn_attempts": {}, "halt": None}}
    (ns / "production/PRODUCTION_LEDGER.json").write_text(json.dumps(st))
    return root, ev_root


def test_blinded_by_default_never_reads_status_values(tmp_path):
    root, ev = build(tmp_path, [0, 1, 2])
    out, rows = AU.audit(root, [], [ev])
    assert "SECRET" not in json.dumps(out) and "SECRET" not in json.dumps(rows)
    assert out["blinded"] is True and out["result_agnostic"] is True


def test_consistent_partial_record_is_integral_but_incomplete(tmp_path):
    root, ev = build(tmp_path, [0, 1, 2])
    out, rows = AU.audit(root, [], [ev])
    assert out["A_completeness"]["sealed_and_ledger"] == 3 and out["A_completeness"]["complete"] is False
    assert out["C_scientific_hash"]["scientific_hash_consistent_cells"] == 3
    assert out["E_accounting"]["reconciles"] is True
    assert out["issues"] == {}
    assert out["INTEGRITY_READY_FOR_ADJUDICATION"] is False, "369 cells are required"


def test_tampered_evidence_and_orphan_marker_are_reported(tmp_path):
    root, ev = build(tmp_path, [0, 1], tamper=1, orphan_marker=7)
    out, _ = AU.audit(root, [], [ev])
    assert [1, "t5"] in out["issues"]["C_evidence_hash_mismatch"]
    assert 7 in out["issues"]["D_durable_marker_without_sealed_cell"]


def test_open_reservation_blocks_accounting_reconciliation(tmp_path):
    root, ev = build(tmp_path, [0], open_res={"AWS:5": {"cell_id": 5, "reserved_cpu_h": 19.0, "role": "AWS"}})
    out, _ = AU.audit(root, [], [ev])
    assert out["E_accounting"]["reconciles"] == "OPEN_RESERVATIONS_PRESENT"
    assert out["D_state"]["open_reservations"] == ["AWS:5"]


def test_unblind_adds_verbatim_status_column_only(tmp_path):
    root, ev = build(tmp_path, [0])
    out, rows = AU.audit(root, [], [ev], unblind=True)
    assert rows[0]["status_verbatim"]["t5_status"] == "SECRET"
    assert "verdict" not in json.dumps(out).lower()
