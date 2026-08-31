#!/usr/bin/env python3
"""Compile the P5 Lean skeleton spine and audit its axiom dependencies.

The spine is self-contained (Mathlib only): it does not import, modify or
depend on the closed P1/P2/P3 Lean files.
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
LEAN_DIR = CAMPAIGN / "lean"
SOURCE = LEAN_DIR / "NonlinearSkeletonP5.lean"
AUDIT = LEAN_DIR / "AxiomAudit.lean"
ALLOWED = {"propext", "Classical.choice", "Quot.sound"}
EXPECTED = 12


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="rebaseguard-p5-lean-") as raw:
        work = Path(raw)
        env = os.environ.copy()
        env["LEAN_PATH"] = f"{work}:{env.get('LEAN_PATH', '')}"
        subprocess.run(
            ["lake", "env", "lean", "-R", str(LEAN_DIR), "-o",
             str(work / "NonlinearSkeletonP5.olean"), str(SOURCE)],
            cwd=LEAN_PROJECT, check=True, env=env)
        env["LEAN_PATH"] = f"{work}:{LEAN_DIR}:{env.get('LEAN_PATH', '')}"
        result = subprocess.run(
            ["lake", "env", "lean", "-R", str(LEAN_DIR), str(AUDIT)],
            cwd=LEAN_PROJECT, env=env, check=True, text=True,
            capture_output=True)

    text = result.stdout + result.stderr
    flat = " ".join(text.split())
    reports = re.findall(r"'([^']+)' depends on axioms: \[([^\]]*)\]", flat)
    assert "sorryAx" not in text, text
    assert len(reports) == EXPECTED, (len(reports), reports)
    used = set()
    for _, ax in reports:
        used |= {a.strip() for a in ax.split(",") if a.strip()}
    assert used <= ALLOWED, used
    out = {
        "compiled": True,
        "source": "lean/NonlinearSkeletonP5.lean",
        "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        "n_declarations": len(reports),
        "audited_declarations": sorted(d for d, _ in reports),
        "axioms_used": sorted(used),
        "axioms_allowed": sorted(ALLOWED),
        "sorry_free": True,
        "imports_closed_spines": False,
    }
    (CAMPAIGN / "results" / "lean_compile.json").write_text(
        json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
