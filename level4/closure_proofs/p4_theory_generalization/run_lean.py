#!/usr/bin/env python3
"""Compile the Priority-4 Lean spine and audit its axioms.

Priority 4 imports the closed Priority-3 synthesis spine, which in turn imports
the closed Priority-1 and Priority-2 derivative spines.  All three are compiled
here from their own protected sources into a scratch directory; none is
modified.
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
DEPENDENCIES = (
    ("m_gt_1_priority1", "MGtOneClosure"),
    ("sr_derivative_priority2", "SRPriority2"),
    ("m_rho_stability_priority3", "StabilityMapP3"),
)
SOURCE = CAMPAIGN / "lean" / "GeneralLocationFamilyP4.lean"
AUDIT = CAMPAIGN / "lean" / "AxiomAudit.lean"
ALLOWED = {"propext", "Classical.choice", "Quot.sound"}
EXPECTED_DECLARATIONS = 19


def _compile(root: Path, source: Path, out: Path, work: Path) -> None:
    env = os.environ.copy()
    env["LEAN_PATH"] = f"{work}:{env.get('LEAN_PATH', '')}"
    subprocess.run(
        ["lake", "env", "lean", "-R", str(root), "-o", str(out), str(source)],
        cwd=LEAN_PROJECT, check=True, env=env,
    )


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="rebaseguard-p4-lean-") as raw:
        work = Path(raw)
        for campaign, module in DEPENDENCIES:
            root = ROOT / "level4" / "closure_proofs" / campaign / "lean"
            _compile(root, root / f"{module}.lean", work / f"{module}.olean", work)
        _compile(CAMPAIGN / "lean", SOURCE,
                 work / "GeneralLocationFamilyP4.olean", work)

        env = os.environ.copy()
        env["LEAN_PATH"] = f"{work}:{CAMPAIGN / 'lean'}:{env.get('LEAN_PATH', '')}"
        result = subprocess.run(
            ["lake", "env", "lean", "-R", str(CAMPAIGN / "lean"), str(AUDIT)],
            cwd=LEAN_PROJECT, env=env, check=True, text=True, capture_output=True,
        )

    text = result.stdout + result.stderr
    flat = " ".join(text.split())
    reports = re.findall(r"'([^']+)' depends on axioms: \[([^\]]*)\]", flat)
    trivial = re.findall(r"'([^']+)' does not depend on any axioms", flat)
    audited = sorted({name for name, _ in reports} | set(trivial))
    assert len(audited) == EXPECTED_DECLARATIONS, audited
    assert "sorryAx" not in text
    source_text = SOURCE.read_text()
    assert "sorry" not in source_text
    assert "axiom " not in source_text
    for _, raw_axioms in reports:
        assert {x.strip() for x in raw_axioms.split(",") if x.strip()} <= ALLOWED

    (CAMPAIGN / "results" / "axiom_audit.txt").write_text(text)
    source_hash = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    manifest = json.loads((CAMPAIGN / "manifest.json").read_text())
    assert source_hash == manifest["lean"]["source_sha256"], "Lean source hash drift"

    payload = {
        "compiled": True,
        "source": "lean/GeneralLocationFamilyP4.lean",
        "source_sha256": source_hash,
        "audited_declarations": audited,
        "axiom_audit_declarations": len(audited),
        "allowed_axioms": sorted(ALLOWED),
        "sorryAx": False,
        "project_specific_scientific_axioms": False,
        "imports_closed_spines": [module for _, module in DEPENDENCIES],
        "reuse_rationale": manifest["lean"]["consumption_rationale"],
        "boundary": (
            "Lean proves the abstract-likelihood derivative bridge under a "
            "Lipschitz difference-quotient hypothesis, derives the frozen "
            "Gaussian statement from it as an instance, proves the general "
            "random-denominator decomposition and the sign analysis of its "
            "short-cycle correction, the algebraic neutrality corollary, the "
            "symmetry fixed point, and the bridges into the closed Priority-3 "
            "classification. It does NOT construct any probability space, "
            "stopping time, or location-family density, does not discharge the "
            "concrete integrability, tail, or domination obligations for the "
            "frozen CUSUM or SR processes, and evaluates no gain."
        ),
    }
    (CAMPAIGN / "results" / "lean_compile.json").write_text(
        json.dumps(payload, indent=2) + "\n"
    )
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
