#!/usr/bin/env python3
"""Rebuild and byte-check the deterministic V3 scientific artifact pipeline."""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess

from config import BASE, ROOT


PY = ROOT / "level4/.venv/bin/python"
GENERATED = [
    "results/gates.json",
    "results/task_metropt_confirmatory.json",
    "results/task_retail_confirmatory.json",
    "results/task_metropt_analysis.json",
    "results/task_retail_analysis.json",
    "results/scientific_decision.json",
    "results/summary.json",
    "figures/figure_a_cross_campaign_reference_distortion.png",
    "figures/figure_b_operational_consequences.png",
    "figures/figure_c_p2_noninferiority.png",
    "figures/figure_d_joint_support_matrix.png",
    "figures/figure_e_effective_blocks.png",
]


def digest() -> str:
    value = hashlib.sha256()
    for relative in GENERATED:
        path = BASE / relative
        name = relative.encode()
        data = path.read_bytes()
        value.update(len(name).to_bytes(8, "big")); value.update(name)
        value.update(len(data).to_bytes(8, "big")); value.update(data)
    return value.hexdigest()


def run_pipeline() -> None:
    for script in ("gate.py", "confirmatory.py", "analyze.py", "decision.py",
                   "summarize.py", "figures.py"):
        subprocess.run([str(PY), str(BASE / "src" / script)], cwd=ROOT, check=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--establish", action="store_true")
    parser.add_argument("--check-run", action="store_true")
    parser.add_argument("--check-record", action="store_true")
    args = parser.parse_args()
    if args.check_record:
        record = json.loads((BASE / "results/reproduction.json").read_text())
        actual = digest()
        passed = record.get("status") == "PASS" and record.get("digest") == actual
        print(f"reproduction record: {'PASS' if passed else 'FAIL'} {actual}")
        return 0 if passed else 1
    before = digest()
    run_pipeline()
    after = digest()
    stable = before == after
    if args.establish:
        record = {
            "schema": "rebaseguard.external-validation-v3.reproduction.v1",
            "status": "PASS" if stable else "FAIL", "byte_stable": stable,
            "artifacts": len(GENERATED), "digest": after,
            "protocol_hash": json.loads((BASE / "results/protocol_hash.json").read_text())["protocol_sha256"],
            "outcome_checkpoint": "5a43ee9",
        }
        (BASE / "results/reproduction.json").write_text(
            json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(f"generated science bytes: {'PASS' if stable else 'FAIL'} {after}")
    return 0 if stable else 1


if __name__ == "__main__":
    raise SystemExit(main())
