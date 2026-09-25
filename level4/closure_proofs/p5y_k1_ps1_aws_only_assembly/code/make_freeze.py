"""Freeze record: every hash the genuine assembly is bound to.

Run AFTER the checks pass and BEFORE consuming the genuine production evidence.
Read-only with respect to every production artifact.
"""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(NS / "driver"))
import ps1_assembly as A  # noqa: E402


def git(*a):
    return subprocess.check_output(["git", "-C", str(NS), *a]).decode().strip()


def utc():
    return subprocess.check_output(["date", "-u", "+%Y-%m-%dT%H:%M:%SZ"]).decode().strip()


def build() -> dict:
    """Compose the freeze from a FULL read-only verification pass."""
    acfg = json.loads((NS / "config/ASSEMBLY_CONTRACT.json").read_text())
    rep = A.preflight(acfg)
    auth = rep["_frozen"]["auth"]
    return {
        "schema": "rebaseguard.p5y.k1.ps1.aws-only-assembly.freeze.v1",
        "frozen_utc": utc(),
        "route": rep["route"],
        "result_bearing": False,
        "k1_closure": "NOT DECIDED BY ASSEMBLY",
        "successor": {
            "namespace": NS.name,
            "source_manifest_sha256": A.sha256_file(NS / "config/SOURCE_MANIFEST.json"),
            "assembly_contract_sha256": A.sha256_file(NS / "config/ASSEMBLY_CONTRACT.json"),
            "worktree_commit_at_freeze": git("rev-parse", "HEAD"),
        },
        "production_inputs": rep["inputs"],
        "scientific_executor": dict(rep["executor"],
                                    producer_commit=auth["producer_commit"],
                                    checkpoint_sha256=auth["checkpoint_sha256"],
                                    live_patches_sha256=auth["live_patches_sha256"],
                                    protocol_sha256=auth["ps1_protocol_sha256"]),
        "accounting_input_identities": dict(
            rep["accounting"],
            identity=("committed_cpu_h == scientific_record_cpu_h + "
                      "settlement_or_operational_cpu_h + imported_predecessor_cpu_h"),
            cap=rep["cap"]),
        "shard": {"cells_completed": rep["cells_completed"], "pending": rep["pending"],
                  "obligations": rep["obligations_completed"], "far_field": rep["far_field"],
                  "ledger_state": rep["ledger_state"]},
        "evidence_roots": dict(rep["evidence_split"],
                               relocation="PROHIBITED: consumed at their bound paths"),
    }


def main() -> int:
    f = build()
    out = NS / "config" / "ASSEMBLY_FREEZE.json"
    out.write_text(json.dumps(f, indent=1, sort_keys=True) + "\n")
    h = hashlib.sha256(out.read_bytes()).hexdigest()
    (NS / "config" / "ASSEMBLY_FREEZE_HASH").write_text(h + "\n")
    print(json.dumps(f, indent=1, sort_keys=True))
    print(f"\nwrote {out}\n  sha256: {h}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
