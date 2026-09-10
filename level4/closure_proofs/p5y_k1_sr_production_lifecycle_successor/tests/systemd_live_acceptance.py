"""LIVE systemd acceptance of the sanctioned detached mechanism (RESULT-FREE).

Run as root (Vultr) or, on AWS, by the operator with the contract's privilege
prefix passed through --prefix. It builds a SYNTHETIC production root (the parent
production namespace COPIED, never symlinked -- the frozen code resolves
__file__; science namespaces read-only via symlink), a temporary Ed25519 key, a
validly signed SYNTHETIC AWS completion handoff, and a SYNTHETIC_CONTROL contract
with service_mode=true, so every run goes through the exact `prodctl start` ->
systemd-run rendering used in production.

  prepare --src-tree T --work W      build + import the synthetic handoff
  report  --work W                   collect ledger / runs / journal / unit evidence

Scenario steps are driven with prodctl/systemctl from SEPARATE shell sessions, so
survival of session termination is observed, not assumed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

SUCC = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SUCC / "ops"))
import opscommon as OC                                           # noqa: E402

PNS = OC.PARENT_NS_REL
PARENT_COMMIT = "bd7cf269792bc146e911ee57a85533b7b7b1aa9d"
SEED_CODE = r'''
import sys, json, hashlib
tree_driver, ops, manifest, ledger_p, priv, out, commit = sys.argv[1:8]
sys.path.insert(0, tree_driver); sys.path.insert(0, ops)
import production_launcher as PL, production_provenance as PP, handoff as HO, multihost as M
import global_budget as GB, integrated_sr_launcher as L, ledger_ops as LO
a = PL.load_production_authorization(); ah = PL.authorization_hash()
owners = M.gate_shards(M.load_shard_manifest(manifest, a['shard_manifest_sha256']))
recs = {}
for c in sorted(x for x, r in owners.items() if r == 'AWS'):
    rec = {'cell_id': c, 'role': 'AWS', 'producer_commit': a['producer_commit'],
           'checkpoint_sha256': a['checkpoint_sha256'],
           'runtime_contract_hash': a['runtime_contract_hashes']['AWS'],
           'scientific_content_hash': hashlib.sha256(f'SYNTHETIC-CONTROL-LIFECYCLE:{c}'.encode()).hexdigest(),
           'cpu_seconds': 1.0, 'obligations_completed': L.obligations_for_cell(a, owners, 'AWS', c),
           'complete': True}
    recs[str(c)] = PP.seal(rec, production_authorization_hash=ah,
                          scientific_adapter_hash=a['scientific_adapter_hash'],
                          certificate_digest=hashlib.sha256(f'SYNTHETIC-CERT:{c}'.encode()).hexdigest())
st = {'schema': GB.GlobalBudget.SCHEMA,
      'committed_cpu_h_by_role': {'AWS': M.per_host_cpu_h(list(recs.values()))},
      'open_reservations': {}, 'completed_cells': recs, 'remote_completed_cells': {},
      LO.OPS_FIELD: LO.new_ops('AWS')}
open(ledger_p, 'w').write(json.dumps(st, indent=1, sort_keys=True) + '\n')
b = GB.GlobalBudget(ledger_p, M.validate_governed_cost, M.gate_global_cap,
                    overhead_cpu_h=a['governed_overhead_cpu_h'], cap_cpu_h=4500.0)
HO.export_handoff(auth=a, ns=PL.PROD_NS, owners=owners, budget=b, approved_head=commit,
                  privkey_pem=priv, out_path=out, validate_governed_cost=M.validate_governed_cost,
                  gate_global_cap=M.gate_global_cap)
print('seeded', len(recs))
'''


def prepare(src: Path, work: Path, python: str, role: str, prefix: list) -> dict:
    if work.exists() and any(work.iterdir()):
        raise SystemExit(f"{work} must be empty")
    tree = work / "tree"
    (tree / "level4/closure_proofs").mkdir(parents=True)
    for d in (src / "level4/closure_proofs").iterdir():
        if d.name == "p5y_k1_sr_production_authorized_successor":
            shutil.copytree(d, tree / PNS, ignore=shutil.ignore_patterns("__pycache__"))
        elif d.name != "p5y_k1_sr_production_lifecycle_successor":
            (tree / "level4/closure_proofs" / d.name).symlink_to(d)
    (tree / "rebaseguard-proof").symlink_to(src / "rebaseguard-proof")
    for p in list((tree / PNS / "production").rglob("*")):
        if p.is_file() and p.name != "README.md":
            p.unlink()
    hc = tree / PNS / "evidence/handoff_consumed.json"
    if hc.exists():
        hc.unlink()
    keys = work / "keys"
    keys.mkdir()
    priv, pub = keys / "priv.pem", keys / "pub.pem"
    subprocess.run(["openssl", "genpkey", "-algorithm", "Ed25519", "-out", str(priv)], check=True)
    subprocess.run(["openssl", "pkey", "-in", str(priv), "-pubout", "-out", str(pub)], check=True)
    fp = hashlib.sha256(subprocess.check_output(["openssl", "pkey", "-pubin", "-in", str(pub),
                                                 "-outform", "DER"])).hexdigest()
    ctl = work / "control.json"
    ctl.write_text(json.dumps({"spin_s": 1.0}))
    c = json.loads(OC.CONTRACT_PATH.read_text())
    c["mode"] = "SYNTHETIC_CONTROL"
    c["service"]["unit_prefix"] = "rbg-synthetic-"
    for r in ("AWS", "VULTR"):
        s = c["hosts"][r]
        s.update(production_root=str(tree if r == role else work / f"absent-{r}"),
                 ops_root=str(SUCC), python=python, runtime_dir=str(work / f"runtime-{r}"),
                 launch_prefix=prefix, online_cpus=os.cpu_count(),
                 user=os.environ.get("USER", "root"))
        c["service"]["environment"][r]["RBG_SYNTH_CONTROL"] = str(ctl)
        c["service"]["environment"][r]["HOME"] = os.environ.get("HOME", "/root")
    c["hosts"][role]["producer_binding"] = "SOURCE_MANIFEST"
    c["synthetic"] = {"entry": "tests/synthetic_entry.py", "service_mode": True,
                      "handoff_pubkey": str(pub), "handoff_fingerprint": fp,
                      "disable_stop_post_settle_file": str(work / "DISABLE_STOP_POST_SETTLE")}
    cp = work / "synthetic_contract.json"
    cp.write_text(json.dumps(c, indent=1, sort_keys=True))
    OC.load_contract(cp)                                          # guard: never a production path
    seed = work / "aws-seed"
    seed.mkdir()
    subprocess.run([python, "-c", SEED_CODE, str(tree / PNS / "driver"), str(SUCC / "ops"),
                    str(tree / PNS / "config/SHARD_MANIFEST.json"),
                    str(seed / "AWS_PRODUCTION_LEDGER.json"), str(priv),
                    str(seed / "AWS_TO_VULTR_HANDOFF.json"), PARENT_COMMIT], check=True)
    r = subprocess.run([python, str(SUCC / "ops/prodctl.py"), "handoff-import", "--contract", str(cp),
                        "--role", role, "--from", str(seed)], capture_output=True, text=True)
    return {"contract": str(cp), "tree": str(tree), "import": json.loads(r.stdout)}


def report(work: Path) -> dict:
    c = json.loads((work / "synthetic_contract.json").read_text())
    role = next(r for r, s in c["hosts"].items() if Path(s["production_root"]) == work / "tree")
    rt = Path(c["hosts"][role]["runtime_dir"])
    L = json.loads((work / "tree" / PNS / "production/PRODUCTION_LEDGER.json").read_text())
    ops = L["operational_lifecycle"]
    runs = {}
    for f in sorted((rt / "runs").glob("*.json")):
        rec = json.loads(f.read_text())
        rid = rec["run_id"]
        lr = ops["runs"].get(rid, {})
        s = lr.get("settlement") or {}
        unit, inv = rec.get("unit"), rec.get("invocation_id")
        runs[rid] = {"status": rec.get("status"), "reason": rec.get("reason"), "unit": unit,
                     "invocation_id": inv, "ledger_status": lr.get("status"),
                     "evidence": s.get("evidence"), "u_usec_final": s.get("u_usec_final"),
                     "journal_cpu_usec": OC.journal_cpu_usage_usec(unit, inv) if unit and inv else None,
                     "orphans": s.get("orphan_cells"),
                     "completed_in_run": len(s.get("completed_in_run", [])),
                     "unit_state": OC.unit_state(unit) if unit else None}
    fin = rt / "FINAL_ASSEMBLY.json"
    return {"role": role, "completed": len(L["completed_cells"]),
            "remote_completed": len(L["remote_completed_cells"]),
            "open_reservations": sorted(L["open_reservations"]),
            "committed": L["committed_cpu_h_by_role"], "halt": ops["halt"],
            "torn": ops["torn_attempts"], "runs": runs,
            "final_assembly": json.loads(fin.read_text()) if fin.exists() else None}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=("prepare", "report"))
    ap.add_argument("--src-tree")
    ap.add_argument("--work", required=True)
    ap.add_argument("--python", default=sys.executable)
    ap.add_argument("--role", default="VULTR")
    ap.add_argument("--prefix", nargs="*", default=[])
    a = ap.parse_args()
    out = prepare(Path(a.src_tree), Path(a.work), a.python, a.role, a.prefix) if a.cmd == "prepare" \
        else report(Path(a.work))
    print(json.dumps(out, indent=1, default=str))


if __name__ == "__main__":
    main()
