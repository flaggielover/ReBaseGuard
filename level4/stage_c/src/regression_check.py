#!/usr/bin/env python
"""Stage C criterion C9 — verify no frozen Stage A/B claim regressed.

Resolves C9 from evidence rather than by assertion: it runs the frozen suites,
hashes the Stage B certificate's scientific content, and compares the Stage A
Gate 4.1 headline numbers against what Stage C measured.
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from campaign import RESULTS

ROOT = Path(__file__).resolve().parents[3]

# The Stage B theorem values that must not move.
STAGE_B_EXPECTED = {
    "decision": "STAGE-B-CLOSED-RIGOROUS-PERIOD2",
    "root_interval": [1.0287242887184211, 1.0447242887184212],
    "lambda2": [0.10814763581379079, 0.832531705019702],
}


def run_suite(args, cwd=ROOT):
    out = subprocess.run(args, cwd=cwd, capture_output=True, text=True)
    m = re.search(r"(\d+) passed", out.stdout)
    f = re.search(r"(\d+) failed", out.stdout)
    return {"cmd": " ".join(args), "passed": int(m.group(1)) if m else 0,
            "failed": int(f.group(1)) if f else 0,
            "returncode": out.returncode}


def main() -> int:
    py = str(ROOT / "level4" / ".venv" / "bin" / "python")
    frozen_py = str(ROOT / "rebaseguard-proof" / ".venv" / "bin" / "python")
    suites = [
        run_suite([frozen_py, "-m", "pytest", "-q"], cwd=ROOT / "rebaseguard-proof"),
        run_suite([py, "-m", "pytest", "level4/tests", "-q"]),
        run_suite([py, "-m", "pytest", "level4/stage_b/tests", "-q"]),
        run_suite([py, "-m", "pytest", "level4/stage_c/tests", "-q"]),
    ]
    total_passed = sum(s["passed"] for s in suites)
    total_failed = sum(s["failed"] for s in suites)

    cert_path = ROOT / "level4/stage_b/certificate/period2_certificate.json"
    cert = json.loads(cert_path.read_text())
    theorem = cert["theorem"]
    stage_b_ok = (cert["decision"] == STAGE_B_EXPECTED["decision"]
                  and theorem["root_interval"] == STAGE_B_EXPECTED["root_interval"]
                  and theorem["lambda2"] == STAGE_B_EXPECTED["lambda2"])
    science_hash = hashlib.sha256(
        json.dumps({k: cert[k] for k in ("decision", "theorem", "bounds")},
                   sort_keys=True).encode()).hexdigest()

    # Stage A Gate 4.1 headline must still be reproduced by Stage C
    stage_a = json.loads(
        (ROOT / "level4/results/processed/gate4.1-full-0ef53096975d"
                "/campaign.summary.json").read_text())
    ic = json.loads((RESULTS / "incontrol_main.json").read_text())
    ic_by = {r["rho"]: r for r in ic["rows"]}
    comparisons = []
    for row in stage_a["headline"]:
        rho = row["rho"]
        if rho not in ic_by:
            continue
        gap = abs(ic_by[rho]["cycle_arl"] - row["cycle_arl"]) / row["cycle_arl"]
        comparisons.append({"rho": rho, "stage_a_arl": row["cycle_arl"],
                            "stage_c_arl": ic_by[rho]["cycle_arl"],
                            "rel_gap": gap})
    arl_ok = all(c["rel_gap"] < 0.02 for c in comparisons)

    payload = {
        "criterion": "C9",
        "suites": suites, "total_passed": total_passed,
        "total_failed": total_failed,
        "stage_b_certificate_unchanged": stage_b_ok,
        "stage_b_science_sha256": science_hash,
        "stage_a_arl_reproduced": arl_ok,
        "stage_a_comparisons": comparisons,
        "passed": bool(total_failed == 0 and stage_b_ok and arl_ok),
    }
    (RESULTS / "regression_check.json").write_text(
        json.dumps(payload, indent=2, default=float))
    for s in suites:
        print(f"  {s['passed']:>4} passed, {s['failed']} failed  {s['cmd']}")
    print(f"  total {total_passed} passed / {total_failed} failed")
    print(f"  Stage B certificate unchanged: {stage_b_ok}")
    print(f"  Stage A ARL reproduced (max rel gap "
          f"{max(c['rel_gap'] for c in comparisons):.2e}): {arl_ok}")
    print(f"  C9: {'PASS' if payload['passed'] else 'FAIL'}")
    return 0 if payload["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
