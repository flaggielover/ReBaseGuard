"""Generation-2 runtime path isolation (checks A-J).

Defect: LAUNCH_AUTHORIZATION.hosts.AWS binds the generation-1 runtime tree, while drain and
ps1_reconcile resolve the contract's runtime_dir -- a split that forced a compatibility
drain on run 20260912T154658Z-2011fded.

The authorization CANNOT be regenerated: PP.seal binds its hash into every production
record, so the 16 already-finalized cells depend on it. The contract's runtime_dir is
therefore the authority for mutable runtime paths, threaded in by produce_entry.
"""
import ast
import json
import sys
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(NS / "ops"))
from opscommon import host_spec, load_contract  # noqa: E402

DRV = Path("/home/ubuntu/work/ReBaseGuard-ps1-prod-gen2/level4/closure_proofs/"
           "p5y_k1_ps1_production/driver")
LAUNCHER = DRV / "ps1_cellseq_launcher.py"
GEN1_RUNTIME = Path("/home/ubuntu/rbg-runtime/p5y_k1_ps1_production")


def contract_spec():
    c = load_contract(None)
    return c, host_spec(c, "AWS")


def sim_pf():
    """What produce_entry now hands run_production_cells."""
    c, s = contract_spec()
    auth = json.loads((Path(s["production_root"]) /
                       "level4/closure_proofs/p5y_k1_ps1_production/config/"
                       "LAUNCH_AUTHORIZATION.json").read_text())
    return {"auth": auth, "role": "AWS", "runtime_dir": s["runtime_dir"]}, s


def launcher_mod():
    sys.path.insert(0, str(DRV))
    import ps1_cellseq_launcher as PL
    return PL


# ---- A / B: work + evidence resolve to generation 2
def test_A_work_dir_is_generation2():
    PL = launcher_mod(); pf, s = sim_pf()
    w, _ = PL.runtime_paths(pf)
    assert w == Path(s["runtime_dir"]) / "work"
    assert GEN1_RUNTIME not in w.parents and w != GEN1_RUNTIME


def test_B_evidence_dir_is_generation2():
    PL = launcher_mod(); pf, s = sim_pf()
    _, e = PL.runtime_paths(pf)
    assert e == Path(s["runtime_dir"]) / "evidence"
    assert GEN1_RUNTIME not in e.parents


# ---- C / D: drain flag identity
def test_C_D_drain_flag_matches_prodctl_exactly():
    PL = launcher_mod(); pf, s = sim_pf()
    launcher_polls = PL.drain_flag_path(pf)
    prodctl_writes = Path(s["runtime_dir"]) / "work" / "DRAIN"      # cmd_drain's expression
    assert launcher_polls == prodctl_writes, f"{launcher_polls} != {prodctl_writes}"


# ---- E / F: markers land where reconcile scans
def test_E_F_marker_tree_equals_reconcile_scan_root():
    sys.path.insert(0, str(NS / "driver"))
    import ps1_reconcile as RC
    PL = launcher_mod(); pf, s = sim_pf()
    _, edir = PL.runtime_paths(pf)
    scan_root = Path(s["runtime_dir"]) / "evidence"                 # RC._markers' expression
    assert edir == scan_root
    assert "runtime_dir" in Path(RC.__file__).read_text()


# ---- G / H: checkpoint + export read generation 2
def test_G_H_checkpoint_and_export_use_contract_runtime():
    src = (NS / "ops" / "prodctl.py").read_text()
    assert 'evidence_root=Path(spec["runtime_dir"]) / "evidence"' in src
    assert 'src_root = Path(spec["runtime_dir"]) / "evidence"' in src
    assert 'auth["hosts"][role]["evidence_dir"]' not in src


# ---- I: produce_entry threads the contract runtime namespace
def test_I_produce_entry_threads_runtime_dir():
    lines = [l.strip() for l in (NS / "ops" / "produce_entry.py").read_text().splitlines()]
    # compare CODE lines, not substring offsets: "make_ops_budget" also appears in a comment
    i = next(n for n, l in enumerate(lines) if l.startswith('pf["runtime_dir"] ='))
    j = next(n for n, l in enumerate(lines) if l.startswith('pf["budget"] = LO.make_ops_budget'))
    assert i < j, "runtime_dir must be set before the launcher runs"


# ---- J: no launcher path still reads the authorization's runtime dirs
def test_J_launcher_no_longer_reads_authorization_runtime_paths():
    src = LAUNCHER.read_text()
    assert 'host["work_dir"]' not in src
    assert 'host["evidence_dir"]' not in src
    # the fallback is the ONLY remaining reference, and it is inside runtime_paths()
    tree = ast.parse(src)
    fn = next(n for n in ast.walk(tree)
              if isinstance(n, ast.FunctionDef) and n.name == "runtime_paths")
    body = ast.get_source_segment(src, fn)
    assert 'h["work_dir"]' in body and 'h["evidence_dir"]' in body
    # the ONLY authorization reads are the two inside runtime_paths(). Other occurrences are
    # task["evidence_dir"] -- the task-dict key the worker and reaper use, which is required.
    assert src.count('h["work_dir"]') == 1
    assert src.count('h["evidence_dir"]') == 1
    non_task = [l for l in src.splitlines()
                if '["evidence_dir"]' in l and 'task["evidence_dir"]' not in l
                and '"evidence_dir": str(' not in l]
    assert non_task == [l for l in src.splitlines() if 'h["evidence_dir"]' in l], \
        f"unexpected authorization evidence_dir read: {non_task}"


# ---- generation-1 fallback preserved (predecessor behaviour unchanged)
def test_fallback_preserves_generation1_behaviour():
    PL = launcher_mod()
    auth = {"hosts": {"AWS": {"work_dir": "/gen1/work", "evidence_dir": "/gen1/evidence"}}}
    w, e = PL.runtime_paths({"auth": auth, "role": "AWS"})           # no runtime_dir
    assert w == Path("/gen1/work") and e == Path("/gen1/evidence")


# ---- authorization must stay byte-identical (16 sealed cells depend on it)
def test_authorization_byte_identical():
    import hashlib
    p = (DRV.parent / "config" / "LAUNCH_AUTHORIZATION.json")
    assert hashlib.sha256(p.read_bytes()).hexdigest() == \
        "fc7cb93465916c3a7842066701b0e11fb6799bfdfc7fff55073a3f6e4cfc03ef"


def test_generation1_ledger_byte_identical():
    import hashlib
    p = Path("/home/ubuntu/work/ReBaseGuard-ps1-prod/level4/closure_proofs/"
             "p5y_k1_ps1_production/production/PRODUCTION_LEDGER.json")
    assert hashlib.sha256(p.read_bytes()).hexdigest() == \
        "0557bc229c3fcdb10cb0dd0b5836fa62a6b0e6c2512656e6ec7e49294b4d6cab"


def test_sixteen_finalized_cells_preserved():
    cells = sorted((DRV.parent / "production" / "cells").glob("[0-9]*.json"))
    assert len(cells) == 16
    ids = [int(p.stem) for p in cells]
    assert ids == [0, 4, 8, 12, 16, 20, 24, 28, 32, 36, 40, 44, 48, 52, 56, 60]


def test_sealed_cell_evidence_paths_remain_archival_where_produced():
    """The settled run's evidence stays at its historical gen-1 location; sealed records
    carry absolute paths, so nothing needs moving and checkpoint still verifies them."""
    rec = json.loads((DRV.parent / "production" / "cells" / "0000.json").read_text())
    ev = (rec.get("record") or rec)["evidence"]
    for v in ev.values():
        assert str(GEN1_RUNTIME) in v["path"], "historical evidence must not be relocated"
