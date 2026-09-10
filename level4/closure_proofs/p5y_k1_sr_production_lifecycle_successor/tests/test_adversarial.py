"""PHASE-17 adversarial sweep: the cases not already exercised by the unit and
integrated suites. RESULT-FREE; every campaign lives in a temporary clone."""
from __future__ import annotations

import json
import os
import signal
import subprocess
import time
from pathlib import Path

import pytest

import conftest as C
import opscommon as OC
import ledger_ops as LO
import supervisor as SV

PNS = OC.PARENT_NS_REL
ROOTLESS = pytest.mark.skipif(os.geteuid() == 0, reason="permission denial is not observable as root")


@pytest.fixture(scope="module")
def clone(tmp_path_factory):
    return C.make_clone(tmp_path_factory.mktemp("adv") / "c")


def entry(cp, **kw):
    code = ("import sys,json;sys.path.insert(0,%r);import produce_entry as PE, opscommon as OC\n"
            "c=OC.load_contract(%r)\ntry:\n PE.run(c,'AWS','20260101T000000Z-00000000',preflight_kwargs=json.loads(%r))\n"
            " print('RAN')\nexcept Exception as e:\n print('REFUSED',type(e).__name__,str(e)[:160])") % (
        str(C.OPS), str(cp), json.dumps(kw))
    return subprocess.run([C.PY, "-c", code], capture_output=True, text=True, timeout=300).stdout.strip()


SIX = {v: "1" for v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
                        "NUMEXPR_NUM_THREADS", "BLIS_NUM_THREADS", "VECLIB_MAXIMUM_THREADS")}
GOOD = dict(role="AWS", env=SIX, live_hash="d49f043755ef658a60e3c4017022ddecf0642a087a6e5bb0c1f2aefbe9721191",
            cores=list(range(16)), siblings={str(c): [c, c + 16] for c in range(16)})


@pytest.mark.parametrize("bad", [
    {"live_hash": "0" * 64},                                     # wrong runtime
    {"cores": list(range(15)) + [16]},                           # wrong worker topology (SMT sibling)
    {"env": {}},                                                 # thread contract absent
    {"role": "VULTR", "live_hash": "c7f9fc671664a1bcfef6d2d3d93d6cc865a2a241a869f2e93f94e6e00b6489d9",
     "cores": [0, 2, 4, 6], "siblings": {"0": [0, 1], "2": [2, 3], "4": [4, 5], "6": [6, 7]}},  # wrong role
])
def test_wrong_runtime_topology_threads_role_refuse_before_any_ledger_write(tmp_path, clone, bad):
    cp = C.synthetic_contract(tmp_path, aws_root=clone)
    kw = dict(GOOD, **bad)
    kw["siblings"] = {int(k): v for k, v in kw["siblings"].items()}
    out = entry(cp, **{k: (v if k != "siblings" else {str(a): b for a, b in v.items()}) for k, v in kw.items()})
    assert out.startswith("REFUSED"), out
    assert C.ledger(clone) is None


def test_wrong_authorization_or_source_hash_refuses(tmp_path, clone):
    spec = {"production_root": str(clone), "producer_binding": "SOURCE_MANIFEST"}
    c = json.loads(OC.CONTRACT_PATH.read_text())
    SV.verify_parent(c, spec)
    for rel in ("config/LAUNCH_AUTHORIZATION.json", "driver/production_provenance.py",
                "config/SHARD_MANIFEST.json", "config/protocol.json"):
        f = clone / PNS / rel
        orig = f.read_bytes()
        f.write_bytes(orig + b" ")
        try:
            with pytest.raises(OC.OpsRefusal, match="drift"):
                SV.verify_parent(c, spec)
        finally:
            f.write_bytes(orig)


@ROOTLESS
def test_runtime_directory_permission_failure_fails_closed(tmp_path, clone):
    cp = C.synthetic_contract(tmp_path, aws_root=clone)
    rt = tmp_path / "runtime-AWS"
    rt.mkdir()
    rt.chmod(0o500)
    try:
        rc, _ = C.run_supervisor(cp, "AWS", log=tmp_path / "s.log")
    finally:
        rt.chmod(0o700)
    assert rc != 0 and C.ledger(clone) is None


def test_disk_write_failure_leaves_previous_bytes(tmp_path, monkeypatch):
    target = tmp_path / "L.json"
    target.write_bytes(b"OLD")
    real = os.write

    def enospc(fd, data):
        raise OSError(28, "No space left on device")
    monkeypatch.setattr(os, "write", enospc)
    with pytest.raises(OSError):
        OC.atomic_write(target, b"NEW")
    monkeypatch.setattr(os, "write", real)
    assert target.read_bytes() == b"OLD"
    assert [p.name for p in tmp_path.iterdir()] == ["L.json"]      # no temp debris


def test_interrupted_atomic_rename_never_adopts_the_temp(tmp_path, clone):
    cp = C.synthetic_contract(tmp_path, aws_root=clone)
    C.set_control(cp, spin_s=0.01)
    rc, _ = C.run_supervisor(cp, "AWS", log=tmp_path / "s.log")
    assert rc == 0
    prod = clone / PNS / "production"
    good = (prod / "PRODUCTION_LEDGER.json").read_bytes()
    forged = json.loads(good); forged["committed_cpu_h_by_role"]["AWS"] = 0.0
    (prod / "PRODUCTION_LEDGER.tmp").write_text(json.dumps(forged))      # fsynced, never renamed
    (prod / "cells/.tmp-interrupted").write_text('{"cell_id": 1')
    rc, out = C.prodctl(cp, "AWS", "recover")
    assert rc == 0, out
    assert {q["path"] for q in out["quarantined"]} == {"production/PRODUCTION_LEDGER.tmp",
                                                      "production/cells/.tmp-interrupted"}
    assert (prod / "PRODUCTION_LEDGER.json").read_bytes() == good


def test_duplicated_and_foreign_reservations(tmp_path, clone):
    root = tmp_path / "r"; ns = root / PNS
    (ns / "production").mkdir(parents=True)
    (ns / "driver").symlink_to(clone / PNS / "driver")
    spec = {"production_root": str(root), "runtime_dir": str(tmp_path / "rt")}
    c = json.loads(OC.CONTRACT_PATH.read_text())
    M, GB = OC.frozen_accounting(spec)
    io = LO.LedgerIO(OC.ledger_path(spec), M, GB, OC.frozen_budget(spec, c))
    rt = OC.RuntimeDir(spec).ensure()
    rid = "20260101T000000Z-000000aa"
    LO.open_run(io, rt, "AWS", rid, unit=None, invocation_id=None, cpu_kind="T", e_stale=0.01, boot="b")
    io.budget.draw("AWS", 0, 11.474662)
    with pytest.raises(GB.BudgetRefusal, match="already has an open reservation"):
        io.budget.draw("AWS", 0, 11.474662)
    with io.locked():
        st = io.read()
        st["open_reservations"]["VULTR:4"] = {"role": "VULTR", "cell_id": 4, "reserved_cpu_h": 1.0}
        io.write(st)
    with pytest.raises(OC.OpsRefusal, match="foreign open reservation"):
        LO.settle_run(io, rt, "AWS", rid, 1000, "TEST")


def test_ledger_finalize_without_valid_cell_is_inadmissible(clone):
    import sys
    sys.path.insert(0, str(clone / PNS / "driver"))
    import multihost as M, production_launcher as PL
    a = PL.load_production_authorization()
    owners = M.gate_shards(M.load_shard_manifest(clone / PNS / "config/SHARD_MANIFEST.json",
                                                 a["shard_manifest_sha256"]))
    for bad in ({"cell_id": 0}, {"cell_id": 4, "role": "AWS", "producer_commit": a["producer_commit"],
                                 "checkpoint_sha256": a["checkpoint_sha256"],
                                 "runtime_contract_hash": a["runtime_contract_hashes"]["AWS"],
                                 "scientific_content_hash": "a" * 64, "cpu_seconds": 1.0,
                                 "obligations_completed": 28, "complete": True}):
        with pytest.raises(M.MultiHostRefusal):
            M.validate_record(bad, "AWS", owners, a["producer_commit"], a["checkpoint_sha256"])


def test_second_launcher_refused_while_first_runs(tmp_path):
    clone = C.make_clone(tmp_path / "own")                       # a campaign that is NOT complete
    cp = C.synthetic_contract(tmp_path, aws_root=clone)
    C.set_control(cp, spin_s=2.0)
    p1, r1 = C.start_supervisor(cp, "AWS", log=tmp_path / "s.log")
    try:
        C.wait_for(lambda: C.ledger(clone) and C.ledger(clone)["open_reservations"], timeout=120)
        before = (clone / PNS / "production/PRODUCTION_LEDGER.json").read_bytes()
        rc2, r2 = C.run_supervisor(cp, "AWS", log=tmp_path / "s.log")
        assert rc2 == SV.EXIT_BUSY
        L = C.ledger(clone)
        assert r2 not in L[LO.OPS_FIELD]["runs"]                    # the second launcher opened nothing
    finally:
        os.kill(p1.pid, signal.SIGTERM)
        p1.wait(timeout=300)
    L = C.ledger(clone)
    assert L[LO.OPS_FIELD]["runs"][r1]["status"] == "SETTLED" and L["open_reservations"] == {}
