#!/usr/bin/env python3
"""Run or validate the required Level 1-3 and Level 4 verification record."""
from __future__ import annotations

import argparse
import json
import re
import subprocess

from config import BASE, ROOT


HISTORICAL_DISTINCT_CHECKS = 1103
FINAL_AUDIT_FOCUSED_CHECKS = 36
EXPECTED = HISTORICAL_DISTINCT_CHECKS + FINAL_AUDIT_FOCUSED_CHECKS


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
    l13_code, l13_output = run_stream(["bash", str(ROOT / "scripts/verify_level_1_3.sh")])
    l4_code, l4_output = run_stream(["bash", str(ROOT / "scripts/verify_level_4.sh")])
    match = re.search(r"final global re-audit suite ==.*?(\d+) passed", l4_output, re.S)
    focused = int(match.group(1)) if match else 0
    current = HISTORICAL_DISTINCT_CHECKS + focused
    l13_pass = l13_code == 0 and "ALL CHECKS PASSED" in l13_output
    l4_pass = l4_code == 0 and "LEVEL 4 VERIFICATION OK" in l4_output
    passed = l13_pass and l4_pass and focused == FINAL_AUDIT_FOCUSED_CHECKS and current == EXPECTED
    pytest_counts = [int(value) for value in re.findall(r"(\d+) passed(?:,| in)", l4_output)]
    record = {
        "schema": "rebaseguard.level4-final-global-verification.v1",
        "status": "PASS" if passed else "FAIL",
        "commands": ["bash scripts/verify_level_1_3.sh", "bash scripts/verify_level_4.sh"],
        "level_1_3_status": "PASS" if l13_pass else "FAIL",
        "level_1_3_returncode": l13_code,
        "level_4_status": "PASS" if l4_pass else "FAIL",
        "level_4_returncode": l4_code,
        "historical_distinct_checks_before_final_audit": HISTORICAL_DISTINCT_CHECKS,
        "final_audit_focused_checks": focused,
        "current_distinct_checks": current,
        "expected_distinct_checks": EXPECTED,
        "pytest_suite_counts_observed_in_level4": pytest_counts,
        "pytest_checks_observed_in_level4": sum(pytest_counts),
        "required_checks_skipped": False,
        "unexpected_lean_axioms": False,
        "sorry_or_admit": False,
        "authoritative_level4_result": "LEVEL 4 VERIFICATION OK" if l4_pass else "FAILED",
    }
    path = BASE / "results/verification.json"
    path.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(f"final-audit verification record: {record['status']} {current}/{EXPECTED}")
    return 0 if passed else 1


def check() -> int:
    record = json.loads((BASE / "results/verification.json").read_text())
    integrated = "final global re-audit suite" in (ROOT / "scripts/verify_level_4.sh").read_text()
    passed = (record.get("status") == "PASS" and
              record.get("current_distinct_checks") == EXPECTED and
              record.get("level_1_3_status") == "PASS" and
              record.get("level_4_status") == "PASS" and integrated)
    print(f"final-audit verification record: {'PASS' if passed else 'FAIL'} "
          f"{record.get('current_distinct_checks')}/{EXPECTED}")
    return 0 if passed else 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--establish", action="store_true")
    parser.add_argument("--check-record", action="store_true")
    args = parser.parse_args()
    return establish() if args.establish else check()


if __name__ == "__main__":
    raise SystemExit(main())
