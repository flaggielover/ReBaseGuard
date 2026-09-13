"""Emit the PROPOSED (unfrozen) operational contract of the runtime isolation successor.

Derived from the frozen generation-2 contract with exactly these operational changes:
  * hosts.*.ops_root -> this namespace (so ExecStart/ExecStopPost run the isolated ops);
  * a `runtime_isolation` block naming the generation paths rule and the legacy
    authorization-bound roots (read-only for marker reconciliation; never polled, never written);
  * `what_this_is` / `freeze_status`.
Scientific identity, parent identities, budget, retry and halt rules are copied unchanged.

NO OPERATIONAL_CONTRACT_HASH is written: the generated opscommon refuses the PRODUCTION contract
until an operator freezes it. This script never touches a runtime directory or production tree.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
SRC = NS.parent / "p5y_k1_ps1_portable_recovery" / "config" / "OPERATIONAL_CONTRACT.json"
AWS_OPS_ROOT = ("/home/ubuntu/work/ReBaseGuard-ps1-ops/level4/closure_proofs/"
                "p5y_k1_ps1_gen2_runtime_isolation")
GEN1_RUNTIME = "/home/ubuntu/rbg-runtime/p5y_k1_ps1_production"


def build() -> dict:
    c = json.loads(SRC.read_text())
    unchanged = {k: json.dumps(c[k], sort_keys=True) for k in
                 ("parent", "accounting", "execution_generation", "recovery", "service",
                  "stop_conditions", "runtime_state", "locks")}
    for role in c["hosts"]:
        c["hosts"][role]["ops_root"] = AWS_OPS_ROOT
    c["runtime_isolation"] = {
        "defect": "GENERATION2_RUNTIME_PATH_SPLIT",
        "rule": "every mutable path = <hosts[role].runtime_dir>/{work,evidence,work/DRAIN,checkpoints,"
                "export,export_src,quarantine/drain_flags}; resolved ONLY by driver/generation_paths.py",
        "authorization_rebinding": {"keys": ["work_dir", "evidence_dir"],
                                    "applied_in": "ops/produce_entry.py after the frozen preflight",
                                    "frozen_authorization_file_changed": False},
        "legacy_bound_roots": {"AWS": {"work_dirs": [GEN1_RUNTIME + "/work"],
                                       "evidence_dirs": [GEN1_RUNTIME + "/evidence"]}},
        "legacy_policy": "legacy roots are never polled for DRAIN and never written; durable markers "
                         "there are reconciled only when bound to the settling run's launcher pid",
        "stale_drain_gate": "pre-start refuses while <runtime_dir>/work/DRAIN exists; "
                            "prodctl clear-drain archives it with a continuity record",
    }
    c["what_this_is"] = ("PS1 GENERATION-2 RUNTIME ISOLATION successor: one generation path resolver for "
                         "work/evidence/DRAIN/reconcile/checkpoint/export/resume. Operational only; "
                         "no scientific semantics change.")
    c["freeze_status"] = "PROPOSED_UNFROZEN (no OPERATIONAL_CONTRACT_HASH; production refuses)"
    for k, v in unchanged.items():
        if json.dumps(c[k], sort_keys=True) != v:
            raise SystemExit(f"unexpected change to {k}")
    return c


def main() -> int:
    out = NS / "config" / "OPERATIONAL_CONTRACT.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(build(), indent=1, sort_keys=True) + "\n")
    if (NS / "config" / "OPERATIONAL_CONTRACT_HASH").exists():
        raise SystemExit("a HASH file exists: this generator must never freeze the contract")
    print(f"wrote {out} (unfrozen)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
