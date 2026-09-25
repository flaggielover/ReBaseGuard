"""Generate config/ASSEMBLY_CONTRACT.json (+_HASH). Hash model A: sha256 of the file bytes."""
import hashlib
import json
import sys
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
OPS = Path("/home/ubuntu/work/ReBaseGuard-ps1-ops/level4/closure_proofs/"
           "p5y_k1_ps1_portable_recovery/config")


def main() -> int:
    c = {
        "schema": "rebaseguard.p5y.k1.ps1.assembly-contract.v1",
        "what_this_is": (
            "ADDITIVE downstream assembly successor for the COMPLETED PS1 SR production "
            "shard. Execution/consumption only: no scientific semantics, no re-run, no "
            "modification of production evidence or of either historical ledger."),
        "role": "AWS",
        "operational_contract_path": str(OPS / "OPERATIONAL_CONTRACT.json"),
        "operational_contract_hash_path": str(OPS / "OPERATIONAL_CONTRACT_HASH"),
        "routes": {
            "AWS_ONLY": "local complete-shard assembly (driver/ps1_assembly.py)",
            "MULTI_HOST": ("ops/prodctl.py assemble --role VULTR in the frozen "
                           "p5y_k1_ps1_portable_recovery namespace: UNTOUCHED"),
        },
        "route_selection": (
            "frozen evidence only: authorization topology must equal the shard manifest "
            "topology; AWS_ONLY additionally requires AWS ownership of the complete frozen "
            "shard, zero off-AWS cells and NO handoff material; MULTI_HOST requires a handoff "
            "public key fingerprint AND off-AWS ownership; anything else fails closed"),
        "aws_only_gates": [
            "complete local ownership of the frozen shard",
            "exactly 369 unique completed cells", "zero pending", "zero open reservations",
            "zero unsettled runs", "campaign lock FREE",
            "no halt on the active execution generation",
            "every sealed record verifies: frozen record gate, provenance gate, evidence "
            "re-hash at its BOUND path, recomputed scientific content hash",
            "complete frozen cell coverage and successor identity match",
            "10332/10332 campaign obligations (28 per cell)",
            "the inherited far-field obligation verified separately",
            "imported predecessor CPU reconciled explicitly",
            "charged CPU-h strictly below the frozen 6600 cap",
        ],
        "accounting_identity": ("committed_cpu_h == scientific_record_cpu_h + "
                                "settlement_or_operational_cpu_h + imported_predecessor_cpu_h"),
        "imported_cpu_authority": [
            "config/GENERATION_TRANSITION.json accounting_import.predecessor_science_cpu_h",
            "OPERATIONAL_CONTRACT execution_generation.imported_science_cpu_h",
            "the earliest generation-2 run: committed_start with no completed_start",
            "the frozen predecessor ledger (hash-pinned, zero completed cells)",
        ],
        "tolerances": {"accounting_cpu_h": 1e-06, "import_rounding_cpu_h": 0.01},
        "far_field": {"work_id": "SR:-1:far_field:all_m",
                      "handling": "INHERITED from P5X-T3, verified separately, never re-run"},
        "evidence_split_is_expected": {
            "historical_predecessor_runtime": "the first 16 genuine cells, never relocated",
            "generation_2_runtime": "the remaining 353 cells"},
        "output_path": str(NS / "evidence" / "FINAL_ASSEMBLY.json"),
        "writes": ["only <namespace>/evidence/FINAL_ASSEMBLY.json"],
        "prohibited": [
            "re-running any scientific cell", "modifying any sealed cell or production evidence",
            "modifying either historical ledger", "relocating the historical first-16 evidence",
            "fabricating VULTR participation or a handoff",
            "deleting the stale predecessor DRAIN marker",
            "changing the executor, thresholds, precision, cell universe or the 6600 CPU-h cap",
        ],
        "result_bearing": False,
        "k1_closure": "NOT DECIDED BY ASSEMBLY: independent scientific adjudication is separate",
    }
    out = NS / "config" / "ASSEMBLY_CONTRACT.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(c, indent=1, sort_keys=True) + "\n")
    h = hashlib.sha256(out.read_bytes()).hexdigest()
    (NS / "config" / "ASSEMBLY_CONTRACT_HASH").write_text(h + "\n")
    print(f"wrote {out}\n  sha256: {h}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
