#!/usr/bin/env python3
"""Compile the Priority-3 Lean spine on top of the two closed spines.

Priority 3 is a declared synthesis layer, so its Lean file imports the closed
Priority-1 and Priority-2 derivative spines rather than restating them.  Both
dependencies are compiled here from their own protected sources; neither file
is modified.
"""

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
P1_LEAN = ROOT / "level4" / "closure_proofs" / "m_gt_1_priority1" / "lean"
P2_LEAN = ROOT / "level4" / "closure_proofs" / "sr_derivative_priority2" / "lean"
SOURCE = CAMPAIGN / "lean" / "StabilityMapP3.lean"
AUDIT = CAMPAIGN / "lean" / "AxiomAudit.lean"
ALLOWED = {"propext", "Classical.choice", "Quot.sound"}
EXPECTED_DECLARATIONS = 14


def _compile(root: Path, source: Path, out: Path, work: Path) -> None:
    env = os.environ.copy()
    env["LEAN_PATH"] = f"{work}:{env.get('LEAN_PATH', '')}"
    subprocess.run(
        ["lake", "env", "lean", "-R", str(root), "-o", str(out), str(source)],
        cwd=LEAN_PROJECT, check=True, env=env,
    )


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="rebaseguard-p3-lean-") as raw:
        work = Path(raw)
        _compile(P1_LEAN, P1_LEAN / "MGtOneClosure.lean",
                 work / "MGtOneClosure.olean", work)
        _compile(P2_LEAN, P2_LEAN / "SRPriority2.lean",
                 work / "SRPriority2.olean", work)
        _compile(CAMPAIGN / "lean", SOURCE, work / "StabilityMapP3.olean", work)

        env = os.environ.copy()
        env["LEAN_PATH"] = f"{work}:{CAMPAIGN / 'lean'}:{env.get('LEAN_PATH', '')}"
        result = subprocess.run(
            ["lake", "env", "lean", "-R", str(CAMPAIGN / "lean"), str(AUDIT)],
            cwd=LEAN_PROJECT, env=env, check=True, text=True, capture_output=True,
        )

    text = result.stdout + result.stderr
    flat = " ".join(text.split())
    reports = re.findall(r"'([^']+)' depends on axioms: \[([^\]]*)\]", flat)
    assert len(reports) == EXPECTED_DECLARATIONS, reports
    assert "sorryAx" not in text
    assert "sorry" not in SOURCE.read_text()
    for _, raw_axioms in reports:
        assert {x.strip() for x in raw_axioms.split(",") if x.strip()} <= ALLOWED

    (CAMPAIGN / "results" / "axiom_audit.txt").write_text(text)
    source_hash = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    manifest = json.loads((CAMPAIGN / "manifest.json").read_text())
    assert source_hash == manifest["lean"]["source_sha256"]

    payload = {
        "compiled": True,
        "source": "lean/StabilityMapP3.lean",
        "source_sha256": source_hash,
        "audited_declarations": sorted(name for name, _ in reports),
        "axiom_audit_declarations": len(reports),
        "allowed_axioms": sorted(ALLOWED),
        "sorryAx": False,
        "project_specific_scientific_axioms": False,
        "imports_priority1_closed_spine": True,
        "imports_priority2_closed_spine": True,
        "reuse_rationale": manifest["lean"]["consumption_rationale"],
        "boundary": (
            "Lean proves the generic stability-map algebra and the two bridges "
            "into the closed derivative spines. It does not evaluate any "
            "GammaTilde value, does not certify the Monte Carlo Gaussian gains, "
            "and asserts nothing beyond first-order local behaviour."
        ),
    }
    (CAMPAIGN / "results" / "lean_compile.json").write_text(
        json.dumps(payload, indent=2) + "\n"
    )
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
