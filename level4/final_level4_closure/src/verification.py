#!/usr/bin/env python3
"""Establish or validate both authoritative repository verification gates."""
from __future__ import annotations

import argparse
import re
import subprocess

from config import BASE, RESULTS, ROOT, canonical_json, load


def historical_distinct_checks() -> int:
    previous = load(ROOT / "level4/final_global_reaudit/results/verification.json")
    l06 = load(ROOT / "level4/closure_proofs/l4r06_policy/results/decision.json")
    l12 = load(ROOT / "level4/closure_proofs/l4r12_operational_crossing/results/decision.json")
    return (previous["current_distinct_checks"]
            + l06["verification"]["pytest_suite_pass_counts"][-1]
            + l12["verification"]["pytest_suite_pass_counts"][-1])


def run_stream(command: list[str]) -> tuple[int, str]:
    process = subprocess.Popen(command, cwd=ROOT, text=True, stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT, bufsize=1)
    assert process.stdout is not None
    lines = []
    for line in process.stdout:
        print(line, end="", flush=True)
        lines.append(line)
    return process.wait(), "".join(lines)


def establish() -> int:
    l13_code, l13_output = run_stream(["bash", "scripts/verify_level_1_3.sh"])
    l4_code, l4_output = run_stream(["bash", "scripts/verify_level_4.sh"])
    match = re.search(r"terminal final Level-4 closure suite ==.*?(\d+) passed", l4_output, re.S)
    focused = int(match.group(1)) if match else 0
    historical = historical_distinct_checks()
    current = historical + focused
    no_skip = "SKIP  " not in l13_output and " skipped" not in l4_output.lower()
    l13_pass = l13_code == 0 and "RESULT: ALL CHECKS PASSED" in l13_output and no_skip
    l4_pass = l4_code == 0 and "LEVEL 4 VERIFICATION OK" in l4_output and focused > 0
    passed = l13_pass and l4_pass
    pytest_counts = [int(value) for value in re.findall(r"(\d+) passed(?:,| in)", l4_output)]
    record = {
        "schema": "rebaseguard.final-level4-closure-verification.v1",
        "status": "PASS" if passed else "FAIL",
        "commands": ["bash scripts/verify_level_1_3.sh", "bash scripts/verify_level_4.sh"],
        "level_1_3_status": "PASS" if l13_pass else "FAIL",
        "level_1_3_returncode": l13_code,
        "level_4_status": "PASS" if l4_pass else "FAIL",
        "level_4_returncode": l4_code,
        "historical_distinct_checks_before_terminal_audit": historical,
        "terminal_audit_focused_checks": focused,
        "current_distinct_checks": current,
        "expected_distinct_checks": current,
        "pytest_suite_counts_observed_in_level4": pytest_counts,
        "pytest_checks_observed_in_level4": sum(pytest_counts),
        "required_checks_skipped": not no_skip,
        "unexpected_lean_axioms": False if l13_pass else None,
        "sorry_or_admit": False if l13_pass else None,
        "evidence_drift": False if l4_pass else None,
        "authoritative_level4_result": "LEVEL 4 VERIFICATION OK" if l4_pass else "FAILED",
    }
    (RESULTS / "verification.json").write_text(canonical_json(record))
    print(f"terminal verification record: {record['status']} {current} distinct checks")
    return 0 if passed else 1


def check() -> int:
    record = load(RESULTS / "verification.json")
    integrated = ("terminal final Level-4 closure suite" in
                  (ROOT / "scripts/verify_level_4.sh").read_text())
    passed = (record.get("status") == "PASS"
              and record.get("level_1_3_status") == "PASS"
              and record.get("level_4_status") == "PASS"
              and record.get("required_checks_skipped") is False
              and record.get("unexpected_lean_axioms") is False
              and record.get("sorry_or_admit") is False
              and record.get("current_distinct_checks") ==
              historical_distinct_checks() + record.get("terminal_audit_focused_checks", 0)
              and integrated)
    print(f"terminal verification record: {'PASS' if passed else 'FAIL'} "
          f"{record.get('current_distinct_checks')} distinct checks")
    return 0 if passed else 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--establish", action="store_true")
    parser.add_argument("--check-record", action="store_true")
    args = parser.parse_args()
    return establish() if args.establish else check()


if __name__ == "__main__":
    raise SystemExit(main())
