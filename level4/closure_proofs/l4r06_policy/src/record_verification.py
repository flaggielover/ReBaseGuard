#!/usr/bin/env python3
"""Run and record the authoritative repository verifier without timestamps."""
from __future__ import annotations

import json
import re
import subprocess

from config import RESULTS, ROOT, canonical_json


def main() -> int:
    proc = subprocess.run(
        ["bash", "scripts/verify_level_4.sh"], cwd=ROOT, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
    )
    (RESULTS / "verification.log").write_text(proc.stdout)
    pass_counts = [int(x) for x in re.findall(r"(?:^|\s)(\d+) passed(?:[,\s]|$)", proc.stdout)]
    result = {
        "schema": "rebaseguard.l4r06-verification.v1",
        "status": "PASS" if proc.returncode == 0 and "LEVEL 4 VERIFICATION OK" in proc.stdout else "FAIL",
        "command": "bash scripts/verify_level_4.sh",
        "returncode": proc.returncode,
        "pytest_pass_count": sum(pass_counts),
        "pytest_suite_pass_counts": pass_counts,
        "terminal_marker": "LEVEL 4 VERIFICATION OK" in proc.stdout,
    }
    (RESULTS / "verification.json").write_text(canonical_json(result))
    print(f"repository verification: {result['status']} ({result['pytest_pass_count']} pytest checks)")
    if result["status"] != "PASS":
        print(proc.stdout[-4000:])
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
