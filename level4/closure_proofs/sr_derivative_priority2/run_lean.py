#!/usr/bin/env python3
"""Compile the Priority-2 Lean spine and record its axiom audit."""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import tempfile
from pathlib import Path

CAMPAIGN = Path(__file__).resolve().parent
ROOT = CAMPAIGN.parents[2]
LEAN_PROJECT = ROOT / "rebaseguard-lean"
SOURCE = CAMPAIGN / "lean" / "SRPriority2.lean"
AUDIT = CAMPAIGN / "lean" / "AxiomAudit.lean"


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="rebaseguard-p2-lean-") as work:
        olean = Path(work) / "SRPriority2.olean"
        subprocess.run(
            ["lake", "env", "lean", "-R", str(CAMPAIGN / "lean"),
             "-o", str(olean), str(SOURCE)], cwd=LEAN_PROJECT, check=True,
        )
        env = os.environ.copy()
        env["LEAN_PATH"] = f"{work}:{CAMPAIGN / 'lean'}:{env.get('LEAN_PATH', '')}"
        result = subprocess.run(
            ["lake", "env", "lean", "-R", str(CAMPAIGN / "lean"), str(AUDIT)],
            cwd=LEAN_PROJECT, env=env, check=True, text=True, capture_output=True,
        )
    text = result.stdout + result.stderr
    flat = " ".join(text.split())
    reports = re.findall(r"'([^']+)' depends on axioms: \[([^\]]*)\]", flat)
    allowed = {"propext", "Classical.choice", "Quot.sound"}
    assert len(reports) == 7, reports
    assert "sorryAx" not in text
    for _, raw in reports:
        assert {x.strip() for x in raw.split(",") if x.strip()} <= allowed
    (CAMPAIGN / "results" / "axiom_audit.txt").write_text(text)
    source_hash = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    manifest = json.loads((CAMPAIGN / "manifest.json").read_text())
    assert source_hash == manifest["lean"]["source_sha256"]
    payload = {
        "compiled": True, "source": "lean/SRPriority2.lean",
        "source_sha256": source_hash, "axiom_audit_declarations": len(reports),
        "allowed_axioms": sorted(allowed), "sorryAx": False,
        "project_specific_scientific_axioms": False,
        "imports_historical_sr_theorem": False,
        "imports_priority1_campaign_theorem": False,
        "concrete_gaussian_tail_machine_checked": False,
        "concrete_gaussian_moments_machine_checked": False,
        "concrete_gaussian_domination_machine_checked": False,
        "boundary": "Lean proves the finite SR/window and conditional dominated-derivative spine; concrete infinite Gaussian obligations are human-proved outside Lean.",
    }
    (CAMPAIGN / "results" / "lean_compile.json").write_text(
        json.dumps(payload, indent=2) + "\n"
    )
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
