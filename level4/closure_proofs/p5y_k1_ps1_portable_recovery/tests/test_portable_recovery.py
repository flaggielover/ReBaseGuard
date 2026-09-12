"""Phase K acceptance. Synthetic only -- no genuine PS1 CPU is spent.

Cells are simulated, but the checkpoint/export/resume/drain code under test is the real
driver/ps1_checkpoint.py, and the seal protocol is the real one the generated executor
uses (an atomic cell_done_XXXX.json written the instant a cell is scientifically complete).
"""
import hashlib
import json
import shutil
import sys
from pathlib import Path

import pytest

NS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(NS / "driver"))
import ps1_checkpoint as CK  # noqa: E402

GEN = {"generation_id": "G2", "generation_index": 2,
       "started_utc": "2026-09-12T10:00:00Z", "host_role": "AWS"}
PRED = {"predecessor_commit": "29b3bffb6a739121b66bdfcb23cb6b6544b39baf",
        "halted_ledger_sha256": "0557bc229c3fcdb10cb0dd0b5836fa62a6b0e6c2512656e6ec7e49294b4d6cab",
        "halted_run_id": "20260912T041203Z-962132d3",
        "halt_reason": "RETRY_LIMIT",
        "halt_class": "EXECUTION_LIFECYCLE_NOT_SCIENTIFIC_COUNTEREXAMPLE",
        "forensic_incident": "HOST_OR_SYSTEMD_INFRASTRUCTURE_EVENT/apt-daily-upgrade/2026-09-12T06:01:57Z"}
IDENT = {"producer_commit": "c9b12670d4da677d384747aa703c725c58bac65a",
         "scientific_adapter_hash": "13ba2ecd1c8afdaafb3463233f246716f599dd935c5b3722f4074327d8eec5fd",
         "successor_cells_sha256": "dfaced89653bd71a0bab4a61729407694768456b1e841f042df84c4544bfe349",
         "live_patches_sha256": "fccd4db30b52c641d3cd83012659fa7ed6d7cd20374f7c4f60e2b6f6004c8291",
         "precision_bits": 256}
ACC = {"historical_cpu_h": 92.32, "generation_cpu_h": 0.0, "cumulative_cpu_h": 92.32,
       "scientific_cpu_h": 0.0, "unattributed_cpu_h": 92.32, "global_cap_cpu_h": 6600.0}


# ----------------------------------------------------------------- synthetic cell runner
def seal(ev: Path, cell: int, host="AWS", run_id="R1") -> dict:
    """Mimics the generated executor's _seal_cell: evidence then atomic done marker."""
    cd = ev / f"cell_{cell:04d}"
    cd.mkdir(parents=True, exist_ok=True)
    evid = {}
    for name in ("t3.json", "t4.json", "t5.json", "patches.jsonl.gz"):
        p = cd / name
        p.write_bytes(CK.canonical({"cell": cell, "artifact": name}))
        evid[name] = {"sha256": CK.sha256_file(p), "bytes": p.stat().st_size}
    sch = hashlib.sha256(CK.canonical({"cell": cell, "t5": "T5_28_OF_28_PASS"})).hexdigest()
    meta = {"scientific_content_hash": sch, "evidence": evid, "host": host,
            "run_id": run_id, "cpu_seconds": 14.98 * 3600, "t5_status": "T5_28_OF_28_PASS"}
    tmp = cd / "cell_done.json.tmp"
    tmp.write_bytes(CK.canonical(meta))
    tmp.replace(cd / "cell_done.json")          # atomic durability point
    return meta


def run_group(ev, cells, *, drain_flag=None, crash_on=None, host="AWS", run_id="R1"):
    """Cells-outer: each cell is sealed the moment it completes. Drain is checked only at a
    cell boundary. A crash mid-cell leaves earlier sealed cells untouched."""
    finalized, torn, never_started = {}, [], []
    for idx, c in enumerate(cells):
        if drain_flag is not None and Path(drain_flag).exists():
            never_started += cells[idx:]
            return finalized, torn, never_started, CK.GRACEFUL_DRAIN
        if crash_on == c:
            torn.append(c)
            never_started += cells[idx + 1:]
            return finalized, torn, never_started, CK.INFRASTRUCTURE_TEAR
        finalized[c] = seal(ev, c, host=host, run_id=run_id)
    return finalized, torn, never_started, None


def mk(fin, ev, torn_lineage=None, acc=None, runs=None, hosts=None):
    pend = sorted(set(range(CK.TOTAL_CELLS)) - set(int(k) for k in fin))
    return CK.build(generation=GEN, predecessor=PRED, identities=IDENT,
                    finalized=fin, pending=pend,
                    torn_lineage=torn_lineage or {str(c): 3 for c in range(64)},
                    accounting=acc or ACC, runs=runs or ["R1"],
                    hosts=hosts or {"AWS": {"role": "AWS", "workers": 16}},
                    evidence_root=ev, ledger_continuity_sha256="c0ffee")


# ------------------------------------------------------------------------------- TEST 1
def test_1_drain_preserves_finalized_and_starts_nothing_new(tmp_path):
    ev = tmp_path / "ev"
    flag = tmp_path / "DRAIN"
    fin, torn, never, kind = run_group(ev, [0, 1, 2, 3])
    assert sorted(fin) == [0, 1, 2, 3] and not torn
    flag.write_text("drain")
    fin2, torn2, never2, kind2 = run_group(ev, [4, 5, 6, 7], drain_flag=flag)
    assert fin2 == {} and torn2 == [] and never2 == [4, 5, 6, 7]
    assert kind2 == CK.GRACEFUL_DRAIN
    ck = mk(fin, ev)
    assert CK.verify(ck, evidence_root=ev)["evidence_verified_cells"] == 4
    assert ck["finalized_cells"] == [0, 1, 2, 3]


# ------------------------------------------------------------------------------- TEST 2
def test_2_crash_mid_group_keeps_earlier_cells_finalized(tmp_path):
    ev = tmp_path / "ev"
    fin, torn, never, kind = run_group(ev, [0, 1, 2, 3], crash_on=2)
    assert sorted(fin) == [0, 1], "A and B must be finalized"
    assert torn == [2], "C must be torn, not finalized"
    assert never == [3], "D must never be falsely completed"
    assert kind == CK.INFRASTRUCTURE_TEAR
    assert (ev / "cell_0000" / "cell_done.json").exists()
    assert (ev / "cell_0001" / "cell_done.json").exists()
    assert not (ev / "cell_0002" / "cell_done.json").exists()
    assert not (ev / "cell_0003").exists()
    ck = mk(fin, ev)
    CK.verify(ck, evidence_root=ev)
    assert 2 in ck["pending_cells"] and 3 in ck["pending_cells"]


# ------------------------------------------------------------------------------- TEST 3
def test_3_checkpoint_export_resume_only_pending(tmp_path):
    ev = tmp_path / "ev"
    fin, *_ = run_group(ev, [0, 1, 2, 3])
    ck = mk(fin, ev)
    exp = CK.export_bundle(ck, evidence_root=ev, out_dir=tmp_path / "out")
    fresh = tmp_path / "fresh"                       # clean runtime, nothing shared
    shutil.copytree(exp["bundle_dir"], fresh)
    rep = CK.verify_bundle(fresh)
    assert rep["finalized"] == 4 and rep["pending"] == CK.TOTAL_CELLS - 4
    ck2 = json.loads((fresh / "checkpoint.json").read_text())
    schedulable = ck2["pending_cells"]
    assert not (set(schedulable) & set(ck2["finalized_cells"]))
    assert 0 not in schedulable and 4 in schedulable


# ------------------------------------------------------------------------------- TEST 4
def test_4_checkpoint_corruption_fails_closed(tmp_path):
    ev = tmp_path / "ev"
    fin, *_ = run_group(ev, [0, 1])
    ck = mk(fin, ev)
    CK.verify(ck, evidence_root=ev)
    bad = json.loads(json.dumps(ck))
    bad["finalized_cells"] = [0, 1, 2]               # claim a cell that was never run
    with pytest.raises(ValueError, match="content hash mismatch"):
        CK.verify(bad, evidence_root=ev)
    bad2 = json.loads(json.dumps(ck))
    bad2["accounting"] = dict(bad2["accounting"], historical_cpu_h=0.0)
    bad2["checkpoint_content_sha256"] = CK._content_hash(bad2)   # re-seal: hash now valid
    with pytest.raises(ValueError, match="historical CPU accounting regressed"):
        CK.verify(bad2, evidence_root=ev)            # still fails closed


# ------------------------------------------------------------------------------- TEST 5
def test_5_finalized_evidence_corruption_fails_closed(tmp_path):
    ev = tmp_path / "ev"
    fin, *_ = run_group(ev, [0, 1])
    ck = mk(fin, ev)
    CK.verify(ck, evidence_root=ev)
    (ev / "cell_0001" / "t5.json").write_bytes(b'{"tampered":true}\n')
    with pytest.raises(ValueError, match="evidence verification failed"):
        CK.verify(ck, evidence_root=ev)
    (ev / "cell_0000" / "t3.json").unlink()
    with pytest.raises(ValueError, match="evidence verification failed"):
        CK.verify(ck, evidence_root=ev)


# ------------------------------------------------------------------------------- TEST 6
def test_6_duplicate_scheduling_of_finalized_cell_fails_closed(tmp_path):
    ev = tmp_path / "ev"
    fin, *_ = run_group(ev, [0, 1])
    pend = sorted(set(range(CK.TOTAL_CELLS)) - set(fin))
    with pytest.raises(ValueError, match="overlap"):
        CK.build(generation=GEN, predecessor=PRED, identities=IDENT, finalized=fin,
                 pending=sorted(set(pend) | {0}),     # re-schedule a finalized cell
                 torn_lineage={}, accounting=ACC, runs=["R1"],
                 hosts={"AWS": {}}, evidence_root=ev, ledger_continuity_sha256="x")


# ------------------------------------------------------------------------------- TEST 7
def test_7_drain_does_not_increment_torn(tmp_path):
    ev = tmp_path / "ev"
    flag = tmp_path / "DRAIN"
    lineage = {str(c): 3 for c in range(64)}
    fin, torn, never, kind = run_group(ev, [100, 101, 102, 103])
    assert not torn
    flag.write_text("drain")
    fin2, torn2, never2, kind2 = run_group(ev, [104, 105], drain_flag=flag)
    assert kind2 == CK.GRACEFUL_DRAIN
    assert torn2 == [], "graceful drain must never tear a cell"
    assert kind2 not in CK.TEARING_KINDS
    after = dict(lineage)
    for c in torn + torn2:
        after[str(c)] = after.get(str(c), 0) + 1
    assert after == lineage, "no torn_attempt may be incremented by a drain"


# ------------------------------------------------------------------------------- TEST 8
def test_8_hard_interruption_tears_only_the_active_cell(tmp_path):
    ev = tmp_path / "ev"
    fin, torn, never, kind = run_group(ev, [10, 11, 12, 13], crash_on=12)
    assert sorted(fin) == [10, 11] and torn == [12] and never == [13]
    assert kind in CK.TEARING_KINDS
    lineage = {}
    for c in torn:
        lineage[str(c)] = lineage.get(str(c), 0) + 1
    assert lineage == {"12": 1}, "only the in-flight cell is torn"
    ck = mk(fin, ev, torn_lineage=lineage)
    CK.verify(ck, evidence_root=ev)
    assert ck["finalized_cells"] == [10, 11]


# ------------------------------------------------------------------------------- TEST 9
def test_9_cross_host_provenance_stays_attributable(tmp_path):
    ev = tmp_path / "ev"
    finA, *_ = run_group(ev, [0, 1], host="AWS", run_id="RA")
    ckA = mk(finA, ev, hosts={"AWS": {"role": "AWS", "workers": 16}})
    CK.verify(ckA, evidence_root=ev)
    finB, *_ = run_group(ev, [2, 3], host="HOST_B", run_id="RB")
    allfin = dict(finA); allfin.update(finB)
    ckB = CK.build(generation={**GEN, "generation_id": "G3", "generation_index": 3},
                   predecessor={**PRED, "resumed_from_checkpoint": ckA["checkpoint_content_sha256"]},
                   identities=IDENT, finalized=allfin,
                   pending=sorted(set(range(CK.TOTAL_CELLS)) - set(allfin)),
                   torn_lineage={}, accounting=ACC, runs=["RA", "RB"],
                   hosts={"AWS": {"role": "AWS"}, "HOST_B": {"role": "HOST_B"}},
                   evidence_root=ev, ledger_continuity_sha256="y")
    CK.verify(ckB, evidence_root=ev)
    by_host = {}
    for c, m in ckB["finalized"].items():
        by_host.setdefault(m["host"], []).append(int(c))
    assert sorted(by_host["AWS"]) == [0, 1]
    assert sorted(by_host["HOST_B"]) == [2, 3]
    assert ckB["predecessor"]["resumed_from_checkpoint"] == ckA["checkpoint_content_sha256"]


# ------------------------------------------------------------------------------ TEST 10
def test_10_cpu_accounting_continuity_cannot_be_reset(tmp_path):
    ev = tmp_path / "ev"
    fin, *_ = run_group(ev, [0, 1])
    gen_cpu = sum(m["cpu_seconds"] for m in fin.values()) / 3600.0
    acc = {"historical_cpu_h": 92.32, "generation_cpu_h": gen_cpu,
           "cumulative_cpu_h": 92.32 + gen_cpu, "scientific_cpu_h": gen_cpu,
           "unattributed_cpu_h": 92.32, "global_cap_cpu_h": 6600.0}
    ck = mk(fin, ev, acc=acc)
    rep = CK.verify(ck, evidence_root=ev)
    assert rep["historical_cpu_h"] == 92.32
    assert rep["cumulative_cpu_h"] == pytest.approx(92.32 + gen_cpu)
    assert ck["accounting"]["cumulative_cpu_h"] > 92.32
    for reset in (0.0, 91.0, -1.0):
        bad = json.loads(json.dumps(ck))
        bad["accounting"]["historical_cpu_h"] = reset
        bad["checkpoint_content_sha256"] = CK._content_hash(bad)
        with pytest.raises(ValueError, match="historical CPU accounting regressed"):
            CK.verify(bad, evidence_root=ev)


# ------------------------------------------------------------- identity drift fail-closed
def test_identity_drift_fails_closed(tmp_path):
    ev = tmp_path / "ev"
    fin, *_ = run_group(ev, [0])
    ck = mk(fin, ev)
    CK.verify(ck, evidence_root=ev, require_identities=IDENT)
    with pytest.raises(ValueError, match="identity drift"):
        CK.verify(ck, evidence_root=ev,
                  require_identities={**IDENT, "producer_commit": "deadbeef"})
    with pytest.raises(ValueError, match="identity drift"):
        CK.verify(ck, evidence_root=ev, require_identities={**IDENT, "precision_bits": 128})


def test_domain_completeness_is_enforced(tmp_path):
    ev = tmp_path / "ev"
    fin, *_ = run_group(ev, [0])
    with pytest.raises(ValueError, match="!= PS1 domain"):
        CK.build(generation=GEN, predecessor=PRED, identities=IDENT, finalized=fin,
                 pending=[1, 2, 3], torn_lineage={}, accounting=ACC, runs=[],
                 hosts={}, evidence_root=ev, ledger_continuity_sha256="x")
