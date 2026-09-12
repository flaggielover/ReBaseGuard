"""Write the PS1 OPERATIONAL_CONTRACT (+ hash) derived from the audited historical contract, changing ONLY PS1 values,
then the OPS_SOURCE_MANIFEST over every adapter file. argv: PARENT_COMMIT (the PS1 authorization commit = production
clone HEAD) and PARENT_TAG."""
import hashlib
import json
import sys
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
CP = NS.parent
HIST = CP / "p5y_k1_sr_production_lifecycle_successor/config/OPERATIONAL_CONTRACT.json"
PNS = CP / "p5y_k1_ps1_production"


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def closure(ns):
    files = {r: sha(ns / r) for r in sorted(("driver/production_launcher.py", "driver/production_provenance.py"))}
    return hashlib.sha256("".join(f"{k}:{v}\n" for k, v in files.items()).encode()).hexdigest()


def main():
    commit, tag = sys.argv[1], sys.argv[2]
    c = json.loads(HIST.read_text())
    auth = json.loads((PNS / "config/LAUNCH_AUTHORIZATION.json").read_text())
    c["what_this_is"] = ("PS1 lifecycle ADAPTER contract: the audited operational lifecycle (bcec064) bound, unchanged in "
                         "behaviour, to the PS1 production namespace. Operational only; no science.")
    c["parent"] = {"aws_cells": 369, "vultr_cells": 0, "total_cells": 369, "obligations": 369 * 28 + 1,
                   "commit": commit, "tag": tag, "checkpoint_sha256": auth["checkpoint_sha256"],
                   "cores": {"AWS": list(range(16)), "VULTR": []}, "workers": {"AWS": 16, "VULTR": 0},
                   "execution_order": ["AWS"], "far_field": "SR:-1:far_field:all_m",
                   "global_cpu_cap": auth["global_cpu_cap"], "governed_overhead_cpu_h": auth["governed_overhead_cpu_h"],
                   "overhead_factor": 1.15, "per_host_hard_caps_present": False,
                   "handoff_public_key_fingerprint": None, "namespace": "level4/closure_proofs/p5y_k1_ps1_production",
                   "production_authorization_sha256": sha(PNS / "config/LAUNCH_AUTHORIZATION.json"),
                   "production_closure_sha256": closure(PNS), "protocol_sha256": sha(PNS / "config/protocol.json"),
                   "scientific_adapter_hash": auth["scientific_adapter_hash"],
                   "shard_manifest_sha256": sha(PNS / "config/SHARD_MANIFEST.json"),
                   "integrated_source_manifest_sha256": auth["scientific_adapter_hash"]}
    c["accounting"]["invariant"] = (f"1.15*(committed + open cell reservations + TORN escrows + SHADOW + requested + overhead) "
                                    f"<= {auth['global_cpu_cap']:g} at every admission")
    aws = c["hosts"]["AWS"]
    aws.update(production_root="/home/ubuntu/work/ReBaseGuard-ps1-prod",
               ops_root="/home/ubuntu/work/ReBaseGuard-ps1-ops/level4/closure_proofs/p5y_k1_ps1_lifecycle_adapter",
               runtime_dir="/home/ubuntu/rbg-runtime/p5y_k1_ps1_production")
    v = c["hosts"]["VULTR"]
    v.update(production_root="/root/ps1-not-deployed/tree", ops_root="/root/ps1-not-deployed/tree/level4/closure_proofs/p5y_k1_ps1_lifecycle_adapter",
             runtime_dir="/root/rbg-runtime/p5y_k1_ps1_production", status="NOT_QUALIFIED_FOR_PS1 (owns no cells)")
    c["service"]["unit_prefix"] = "rbg-p5y-k1-ps1-prod-"
    c["genuine_sr_production_cells_at_freeze"] = 0
    c["scientific_identity_changed"] = False
    c["result_bearing"] = False
    c["runtime_state"]["exclude_sha256"] = sha(NS / "config/RUNTIME_STATE_EXCLUDE")
    c["runtime_state"]["installed_into"] = "<git common dir of the SEPARATE PS1 production clone>/info/exclude"
    b = (json.dumps(c, indent=1, sort_keys=True) + "\n").encode()
    (NS / "config/OPERATIONAL_CONTRACT.json").write_bytes(b)
    (NS / "config/OPERATIONAL_CONTRACT_HASH").write_text(hashlib.sha256(b).hexdigest() + "\n")
    files = sorted(str(p.relative_to(NS)) for p in NS.rglob("*") if p.is_file() and "__pycache__" not in p.parts
                   and p.name not in ("OPS_SOURCE_MANIFEST.json", "OPS_SOURCE_MANIFEST_HASH"))
    man = {"schema": "rebaseguard.p5y.k1.sr.production.ops-source-manifest.v1", "files": {f: sha(NS / f) for f in files}}
    mb = (json.dumps(man, indent=1, sort_keys=True) + "\n").encode()
    (NS / "config/OPS_SOURCE_MANIFEST.json").write_bytes(mb)
    (NS / "config/OPS_SOURCE_MANIFEST_HASH").write_text(hashlib.sha256(mb).hexdigest() + "\n")
    print("contract", hashlib.sha256(b).hexdigest(), "ops manifest", hashlib.sha256(mb).hexdigest(), "files", len(files))


if __name__ == "__main__":
    main()
