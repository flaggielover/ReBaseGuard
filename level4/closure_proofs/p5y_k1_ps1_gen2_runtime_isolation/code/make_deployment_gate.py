"""Emit config/QUALIFIED_SOURCE_HASHES.json (the exact sources the final synthetic acceptance ran) and
config/DEPLOYMENT_GATE.json. Refuses if any local source differs from the qualified run's hashes."""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
RUNLOG = NS / "evidence/r2_final/RUNLOG.txt"
VULTR_NS = "/root/work/ReBaseGuard-ps1-gen2/level4/closure_proofs/p5y_k1_ps1_gen2_runtime_isolation/"


def main() -> int:
    files = {}
    for line in RUNLOG.read_text().splitlines():
        m = re.match(r"^([0-9a-f]{64})\s+(\S+)$", line)
        if m:
            files[m.group(2).replace(VULTR_NS, "")] = m.group(1)
    drift = [r for r, h in files.items() if hashlib.sha256((NS / r).read_bytes()).hexdigest() != h]
    if drift or not files:
        raise SystemExit(f"local sources differ from the qualified acceptance run: {drift}")
    (NS / "config/QUALIFIED_SOURCE_HASHES.json").write_text(json.dumps({
        "schema": "rebaseguard.p5y.k1.ps1.gen2-runtime-isolation.qualified-sources.v1",
        "qualified_by": "evidence/r2_final/ACCEPTANCE.json (9 scenarios PASS + 2 negative controls reproducing the defect)",
        "runlog_sha256": hashlib.sha256(RUNLOG.read_bytes()).hexdigest(),
        "acceptance_sha256": hashlib.sha256((NS / "evidence/r2_final/ACCEPTANCE.json").read_bytes()).hexdigest(),
        "files": dict(sorted(files.items()))}, indent=1, sort_keys=True) + "\n")
    gate = {
        "schema": "rebaseguard.p5y.k1.ps1.gen2-runtime-isolation.deployment-gate.v1",
        "LANE_A_REPAIR": "PASS_SYNTHETIC_NOT_DEPLOYED",
        "LANE_A_DEPLOYMENT_ALLOWED_ONLY_AFTER": "CURRENT_LIVE_DRAIN_SETTLED",
        "live_run_at_gate_creation": {"unit": "rbg-p5y-k1-ps1-recov-aws-20260912T154658Z-2011fded.service",
                                      "state": "active, under operator compatibility DRAIN since 2026-09-12T16:04:18Z",
                                      "touched": False},
        "technical_enforcement": [
            "config/OPERATIONAL_CONTRACT_HASH is absent: the generated opscommon refuses the PRODUCTION contract (UNFROZEN)",
            "the proposed contract's ops_root is not deployed on AWS; the live unit runs p5y_k1_ps1_portable_recovery",
            "code/check_deployment_gate.py returns non-zero unless every phase gate passes"],
        "ordered_steps": [
            {"step": 1, "do": "wait for the live unit to exit by the graceful drain; never prodctl stop it (AUDIT M3)"},
            {"step": 2, "do": "verify settlement", "check": "check_deployment_gate.py --phase settled --expected-sealed 16",
             "requires": ["16 expected cells sealed (one in-flight cell per worker at drain time); any other count -> adjudicate before freeze",
                          "ledger/reservations reconciled: open_reservations {} and no OPEN run",
                          "torn_attempts {}", "campaign lock released and frozen ledger lock absent",
                          "continuity chain valid", "repair sources == QUALIFIED_SOURCE_HASHES"]},
            {"step": 3, "do": "freeze Lane A: commit config/OPERATIONAL_CONTRACT_HASH = sha256(config/OPERATIONAL_CONTRACT.json) "
                              "and an OPS_SOURCE_MANIFEST over ops/ and driver/"},
            {"step": 4, "do": "bind exact hashes: repair commit, OPERATIONAL_CONTRACT_HASH, OPS_SOURCE_MANIFEST_HASH, qualified source hashes"},
            {"step": 5, "do": "deploy the frozen commit to the AWS ops worktree (no change to the production tree, ledger or evidence)"},
            {"step": 6, "do": "rerun focused acceptance on the frozen sources (synthetic contract, never the live runtime dir)"},
            {"step": 7, "do": "clear the stale generation DRAIN only after steps 2-6 pass (prodctl clear-drain archives it); "
                              "the gen1 compatibility flag is legacy, ignored by the repaired launcher, and never deleted"},
            {"step": 8, "do": "verify resume", "check": "check_deployment_gate.py --phase pre-resume --acceptance <step-6 ACCEPTANCE.json>"},
            {"step": 9, "do": "prodctl start --role AWS (production resume)"}],
        "forbidden_until_gate": ["deploy the repair", "update the live runtime contract", "clear the live DRAIN marker",
                                 "restart or stop the live campaign", "modify live evidence"]}
    (NS / "config/DEPLOYMENT_GATE.json").write_text(json.dumps(gate, indent=1, sort_keys=True) + "\n")
    print(json.dumps({"qualified_files": len(files)}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
