#!/usr/bin/env python3
"""Generator-owned scoped L4R-06 decision and original-requirement mapping."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from config import RESULTS, canonical_json


def _load(name: str) -> dict[str, Any]:
    return json.loads((RESULTS / name).read_text())


def build() -> dict[str, Any]:
    science = _load("scientific_findings.json")
    adversarial = _load("adversarial_final.json")
    verification = _load("verification.json")
    reproduction = _load("reproduction.json")
    integrity = science["historical_firewall"]["integrity"]
    gates = {
        "C06.1": (integrity["status"] == "PASS",
                   "original L4R-06 reconstructed from the protected 18-row ledger"),
        "C06.2": (science["H6-1"]["status"] == "PASS",
                   "P3 mechanically uses the protected D4 lower 95% boundary"),
        "C06.3": (science["protocol_sha256"] == "2abda564099eae20079806609af5d9a48144fa78c95c29de7ccf5e31f8a49faa",
                   "policy, allocation, endpoints, inference, and thresholds were frozen pre-outcome"),
        "C06.4": (science["H6-2"]["status"] == "PASS",
                   "simultaneous reference-MSE improvement in all active regimes"),
        "C06.5": (science["H6-3"]["status"] == "PASS",
                   "simultaneous false-alert-burden consequence in all active regimes"),
        "C06.6": (science["H6-4"]["status"] == "PASS",
                   "normalized response non-inferior to fresh in all 16 conditions"),
        "C06.7": (science["absolute_delay_safety"]["status"] == "PASS",
                   "absolute-delay guard and simulator semantic tests pass"),
        "C06.8": (science["historical_firewall"]["D4_operational_interpretation"]
                   == "MATHEMATICAL, NOT OPERATIONAL",
                   "D4 remains local/deterministic, not an operational phase transition"),
        "C06.9": (science["historical_firewall"]["historical_C6"] == "FAILED"
                   and integrity["historical_C6_preserved"],
                   "historical Stage C/C6 remains unchanged and failed"),
        "C06.10": (adversarial["status"] == "PASS" and adversarial["n_passed"] == 23,
                    "all 23 frozen adversarial checks pass"),
        "C06.11": (verification["status"] == "PASS" and reproduction["status"] == "PASS",
                    "focused tests, authoritative verification, and byte-stable replay pass"),
    }
    criteria = [{"id": cid, "status": "PASS" if ok else "FAIL", "evidence": evidence}
                for cid, (ok, evidence) in gates.items()]
    all_pass = all(ok for ok, _ in gates.values())
    invalid = (integrity["status"] != "PASS" or verification["status"] != "PASS"
               or reproduction["status"] != "PASS")
    verdict = ("L4R06-POLICY-CLOSED" if all_pass else
               "L4R06-POLICY-FAILED" if invalid else "L4R06-POLICY-PARTIAL")
    same = verdict == "L4R06-POLICY-CLOSED" and science["same_requirement_mapping_candidate"]
    original_status = "PASS" if same else "UNMET" if verdict.endswith("FAILED") else "PARTIAL"
    return {
        "schema": "rebaseguard.l4r06-decision.v1",
        "generator_owned": True,
        "target": "L4R-06 — Stability-aware reuse policy with monitoring consequences",
        "scoped_verdict": verdict,
        "criteria": criteria,
        "H6": {name: science[name]["status"] for name in
               ("H6-1", "H6-2", "H6-3", "H6-4", "H6-5")},
        "absolute_delay_safety": science["absolute_delay_safety"]["status"],
        "same_requirement_mapping": same,
        "mapping_reason": science["mapping_reason"] if same else
            "The complete frozen closure criteria did not all pass, so later evidence cannot map to original L4R-06 PASS.",
        "original_L4R06_current_status": original_status,
        "historical_C6_preserved": True,
        "historical_stage_c_verdict": "STAGE-C-PARTIAL",
        "historical_final_global_reaudit": "LEVEL-4-PARTIAL",
        "global_reaudit_performed": False,
        "l4r12_touched": False,
        "adversarial": {"first_file": "adversarial_first.json",
                        "final_passed": adversarial["n_passed"], "final_total": 23},
        "verification": verification,
        "reproduction": reproduction,
        "claim_scope": (
            "Frozen Gaussian two-sided CUSUM; m={1,20,70,100}; "
            "Delta={0.25,0.5,1.0,1.5}. No universal safety or operational "
            "phase-transition claim and no semi-real validation."
        ),
        "next_blocker": "L4R-12 — OPERATIONAL CONSEQUENCE OF GAMMA_M CROSSING",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    generated = canonical_json(build())
    path = RESULTS / "decision.json"
    if args.check:
        if not path.exists() or path.read_text() != generated:
            print("L4R-06 decision is not byte-stable")
            return 1
        print("L4R-06 decision: byte-stable")
        return 0
    path.write_text(generated)
    decision = json.loads(generated)
    print(decision["scoped_verdict"])
    print("original L4R-06:", decision["original_L4R06_current_status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
