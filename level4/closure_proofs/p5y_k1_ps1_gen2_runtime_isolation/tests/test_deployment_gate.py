"""Deployment-gate tests (added AFTER the qualified acceptance run; they do not alter qualified sources)."""
import argparse
import hashlib
import json
import sys
from pathlib import Path

import pytest

NS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(NS / "code"))
import check_deployment_gate as CG  # noqa: E402


def canon(o):
    return (json.dumps(o, sort_keys=True, separators=(",", ":"), ensure_ascii=True) + "\n").encode()


def fixture(tmp, *, sealed=16, torn=None, open_res=None, open_run=False, lock_file=False, gen_drain=False):
    prod = tmp / "prod"
    ns = prod / CG.NS_REL / "production"
    (ns / "cells").mkdir(parents=True)
    completed = {}
    for c in range(sealed):
        rec = {"cell_id": c, "scientific_content_hash": f"h{c}"}
        completed[str(c)] = rec
        (ns / "cells" / f"{c:04d}.json").write_text(json.dumps(rec))
    st = {"completed_cells": completed, "open_reservations": open_res or {},
          "operational_lifecycle": {"runs": {"r": {"status": "OPEN" if open_run else "SETTLED"}},
                                    "torn_attempts": torn if torn is not None else {}, "halt": None}}
    (ns / "PRODUCTION_LEDGER.json").write_text(json.dumps(st))
    if lock_file:
        (ns / "PRODUCTION_LEDGER.json.lock").write_text("123\n")
    rt = tmp / "rt"
    (rt / "work").mkdir(parents=True)
    rec = {"seq": 0, "event": "RUN_SETTLED", "prev_sha256": None}
    rec["sha256"] = hashlib.sha256(canon(rec)).hexdigest()
    (rt / "continuity.jsonl").write_text(json.dumps(rec) + "\n")
    (rt / "campaign.lock").write_text("")
    if gen_drain:
        (rt / "work" / "DRAIN").write_text("{}")
    return argparse.Namespace(phase="settled", production_root=str(prod), runtime_dir=str(rt), expected_sealed=16,
                              legacy_work_dir=[], unit_glob=None, acceptance=None)


def test_settled_state_allows_freeze(tmp_path):
    rep = CG.evaluate(fixture(tmp_path))
    assert rep["FREEZE_ALLOWED"] is True, [k for k, v in rep["gates"].items() if not v["pass"]]


@pytest.mark.parametrize("kw,gate", [({"sealed": 15}, "G8_expected_sealed_cells"),
                                     ({"torn": {"3": 1}}, "G6_torn_attempts_empty"),
                                     ({"open_res": {"AWS:3": {}}}, "G4_zero_open_reservations"),
                                     ({"open_run": True}, "G5_no_unsettled_runs"),
                                     ({"lock_file": True}, "G3_frozen_ledger_lock_absent")])
def test_each_unsettled_condition_blocks_freeze(tmp_path, kw, gate):
    rep = CG.evaluate(fixture(tmp_path, **kw))
    assert rep["FREEZE_ALLOWED"] is False and rep["gates"][gate]["pass"] is False


def test_pre_resume_requires_frozen_contract_acceptance_and_cleared_drain(tmp_path):
    a = fixture(tmp_path, gen_drain=True)
    a.phase = "pre-resume"
    rep = CG.evaluate(a)
    assert rep["RESUME_ALLOWED"] is False
    for g in ("G12_contract_frozen_and_bound", "G13_focused_acceptance_rerun_all_pass", "G14_generation_drain_cleared"):
        assert rep["gates"][g]["pass"] is False


def test_repository_state_is_unfrozen_and_production_refuses():
    assert not (NS / "config/OPERATIONAL_CONTRACT_HASH").exists()
    sys.path.insert(0, str(NS / "ops"))
    import opscommon as OC
    with pytest.raises(OC.OpsRefusal, match="UNFROZEN"):
        OC.load_contract()


def test_gate_record_is_exact():
    g = json.loads((NS / "config/DEPLOYMENT_GATE.json").read_text())
    assert g["LANE_A_DEPLOYMENT_ALLOWED_ONLY_AFTER"] == "CURRENT_LIVE_DRAIN_SETTLED"
    assert g["LANE_A_REPAIR"] == "PASS_SYNTHETIC_NOT_DEPLOYED"
    steps = [s["do"] for s in g["ordered_steps"]]
    assert steps.index(next(s for s in steps if s.startswith("clear the stale"))) > \
        steps.index(next(s for s in steps if s.startswith("rerun focused acceptance")))


def test_qualified_sources_unchanged():
    q = json.loads((NS / "config/QUALIFIED_SOURCE_HASHES.json").read_text())["files"]
    assert len(q) == 14
    assert all(hashlib.sha256((NS / r).read_bytes()).hexdigest() == h for r, h in q.items())
