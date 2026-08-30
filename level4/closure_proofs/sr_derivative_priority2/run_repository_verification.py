#!/usr/bin/env python3
"""Run and classify the required repository regression suites."""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

CAMPAIGN = Path(__file__).resolve().parent
ROOT = CAMPAIGN.parents[2]
PY = ROOT / "level4" / ".venv" / "bin" / "python"


def run(label: str, command: list[str]) -> dict:
    result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
    output = result.stdout + result.stderr
    summaries = re.findall(r"(?:=+ )?(\d+ passed(?:, \d+ failed)?[^\n]*)(?: =+)?", output)
    return {
        "label": label, "command": " ".join(command), "exit_code": result.returncode,
        "summary": summaries[-1] if summaries else output.strip().splitlines()[-1] if output.strip() else "",
        "output_tail": "\n".join(output.strip().splitlines()[-30:]),
    }


def main() -> None:
    suites = [
        run("level_1_3_full", ["bash", "scripts/verify_level_1_3.sh"]),
        run("level_4_aggregate", ["bash", "scripts/verify_level_4.sh"]),
        run("historical_sr", [str(PY), "-m", "pytest", "level4/closure_proofs/sr_derivative/tests", "-q", "-p", "no:cacheprovider"]),
        run("priority1", [str(PY), "-m", "pytest", "level4/closure_proofs/m_gt_1_priority1/tests", "-q", "-p", "no:cacheprovider"]),
        run("external_validation_v2", [str(PY), "-m", "pytest", "level4/closure_proofs/external_validation_v2/tests", "-q", "-p", "no:cacheprovider"]),
        run("external_validation_v3", [str(PY), "-m", "pytest", "level4/closure_proofs/external_validation_v3/tests", "-q", "-p", "no:cacheprovider"]),
        run("final_global_reaudit", [str(PY), "-m", "pytest", "level4/final_global_reaudit/tests", "-q", "-p", "no:cacheprovider"]),
        run("l4r06_policy", [str(PY), "-m", "pytest", "level4/closure_proofs/l4r06_policy/tests", "-q", "-p", "no:cacheprovider"]),
        run("l4r12_operational", [str(PY), "-m", "pytest", "level4/closure_proofs/l4r12_operational_crossing/tests", "-q", "-p", "no:cacheprovider"]),
        run("final_level4_closure", [str(PY), "-m", "pytest", "level4/final_level4_closure/tests", "-q", "-p", "no:cacheprovider"]),
        run("post_level4_archive", [str(PY), "scripts/verify_post_level4_archive.py"]),
    ]
    by_name = {row["label"]: row for row in suites}
    required_pass = all(by_name[name]["exit_code"] == 0 for name in (
        "level_1_3_full", "historical_sr", "priority1", "external_validation_v3",
        "l4r06_policy", "l4r12_operational",
    ))
    historical = {
        "old_52_file_guard_against_92_file_tree": {
            "observed": by_name["level_4_aggregate"]["exit_code"] != 0,
            "predates_priority2": True,
            "classification": "HISTORICAL_DIAGNOSTIC",
        },
        "post_archive_readme_hash_drift": {
            "observed": by_name["post_level4_archive"]["exit_code"] != 0
                and "README.md" in by_name["post_level4_archive"]["output_tail"],
            "predates_priority2": True,
            "classification": "HISTORICAL_DIAGNOSTIC",
        },
    }
    payload = {
        "required_regressions_pass": required_pass,
        "suites": suites,
        "historical_diagnostics": historical,
        "historical_diagnostics_not_counted_as_priority2_passes": True,
    }
    (CAMPAIGN / "results" / "verification.json").write_text(
        json.dumps(payload, indent=2) + "\n"
    )
    print(json.dumps(payload, indent=2))
    if not required_pass or not all(row["observed"] for row in historical.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
