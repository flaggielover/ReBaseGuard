"""Test fixtures: a MUTABLE view of the completed shard.

config/ and driver/ are symlinked to the genuine (frozen) trees; only the ledger and the
sealed cell files are copied, so a test can mutate a COPY. Evidence is never copied and
never written: records keep their genuine bound paths and are read from there.
"""
import json
import os
import shutil
import tempfile
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
OPS_CFG = Path("/home/ubuntu/work/ReBaseGuard-ps1-ops/level4/closure_proofs/"
               "p5y_k1_ps1_portable_recovery/config")
GENUINE_CONTRACT = OPS_CFG / "OPERATIONAL_CONTRACT.json"


def _sha(p):
    import hashlib
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def build(tmp: Path, *, contract_edit=None, ledger_edit=None, auth_edit=None,
          shard_edit=None, transition_edit=None) -> dict:
    """Return an assembly-contract dict pointing at a mutable copy of the shard."""
    contract = json.loads(GENUINE_CONTRACT.read_text())
    spec = contract["hosts"]["AWS"]
    ns = contract["parent"]["namespace"]
    src_ns = Path(spec["production_root"]) / ns
    root = tmp / "prod"
    dst_ns = root / ns
    dst_ns.mkdir(parents=True)
    for name in ("driver", "code", "tests", "README.md"):
        if (src_ns / name).exists():
            os.symlink(src_ns / name, dst_ns / name)
    # config: symlink unless a test needs to edit the authorization / shard manifest
    if auth_edit or shard_edit:
        shutil.copytree(src_ns / "config", dst_ns / "config")
        if auth_edit:
            a = json.loads((dst_ns / "config/LAUNCH_AUTHORIZATION.json").read_text())
            auth_edit(a)
            (dst_ns / "config/LAUNCH_AUTHORIZATION.json").write_text(
                json.dumps(a, indent=1, sort_keys=True) + "\n")
            (dst_ns / "config/LAUNCH_AUTHORIZATION_HASH").write_text(
                _sha(dst_ns / "config/LAUNCH_AUTHORIZATION.json") + "\n")
            contract["parent"]["production_authorization_sha256"] = \
                _sha(dst_ns / "config/LAUNCH_AUTHORIZATION.json")
        if shard_edit:
            s = json.loads((dst_ns / "config/SHARD_MANIFEST.json").read_text())
            shard_edit(s)
            (dst_ns / "config/SHARD_MANIFEST.json").write_text(
                json.dumps(s, indent=1, sort_keys=True) + "\n")
            contract["parent"]["shard_manifest_sha256"] = _sha(dst_ns / "config/SHARD_MANIFEST.json")
    else:
        os.symlink(src_ns / "config", dst_ns / "config")
    # the other repo-relative inputs the authorization pins (executor, universe, patches)
    for rel in ("level4/closure_proofs/p5y_k1_sr_o9_partition_successor",
                "level4/closure_proofs/p5y_k1_sr_o9_t345_successor"):
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        if not (root / rel).exists():
            os.symlink(Path(spec["production_root"]) / rel, root / rel)
    auth = json.loads((dst_ns / "config/LAUNCH_AUTHORIZATION.json").read_text())
    for f in auth["executor_source_manifest"]:
        t = root / f
        if t.exists():                      # already reachable through a symlinked parent
            continue
        if any(par.is_symlink() for par in t.parents if root in par.parents or par == root):
            continue
        t.parent.mkdir(parents=True, exist_ok=True)
        os.symlink(Path(spec["production_root"]) / f, t)
    # ledger + sealed cells are COPIES
    (dst_ns / "production").mkdir()
    shutil.copytree(src_ns / "production/cells", dst_ns / "production/cells")
    ledger = json.loads((src_ns / "production/PRODUCTION_LEDGER.json").read_text())
    if ledger_edit:
        ledger_edit(ledger, dst_ns / "production/cells")
    (dst_ns / "production/PRODUCTION_LEDGER.json").write_text(
        json.dumps(ledger, indent=1, sort_keys=True) + "\n")
    spec["production_root"] = str(root)
    if transition_edit:
        cfg = tmp / "opscfg"
        shutil.copytree(OPS_CFG, cfg)
        t = json.loads((cfg / "GENERATION_TRANSITION.json").read_text())
        transition_edit(t)
        (cfg / "GENERATION_TRANSITION.json").write_text(
            json.dumps(t, indent=1, sort_keys=True) + "\n")
        spec["ops_root"] = str(cfg.parent)
        contract["execution_generation"]["transition_record"] = "opscfg/GENERATION_TRANSITION.json"
        contract["execution_generation"]["transition_record_sha256"] = \
            _sha(cfg / "GENERATION_TRANSITION.json")
    if contract_edit:
        contract_edit(contract)
    cpath = tmp / "OPERATIONAL_CONTRACT.json"
    cpath.write_text(json.dumps(contract, indent=1, sort_keys=True) + "\n")
    hpath = tmp / "OPERATIONAL_CONTRACT_HASH"
    hpath.write_text(_sha(cpath) + "\n")
    acfg = json.loads((NS / "config/ASSEMBLY_CONTRACT.json").read_text())
    acfg["operational_contract_path"] = str(cpath)
    acfg["operational_contract_hash_path"] = str(hpath)
    acfg["output_path"] = str(tmp / "FINAL_ASSEMBLY.json")
    return acfg


def tmpdir():
    return Path(tempfile.mkdtemp(prefix="ps1-assembly-test-"))
