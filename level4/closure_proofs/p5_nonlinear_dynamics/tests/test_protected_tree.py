"""Protected-tree integrity: no frozen P1-P4/P7/Stage-D artifact may change."""
from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path

CAMPAIGN = Path(__file__).resolve().parents[1]
ROOT = CAMPAIGN.parents[2]
BEFORE = CAMPAIGN / "results" / "protected_hashes_before.txt"
ROOTS = [
    "level4/closure_proofs/m_gt_1_priority1",
    "level4/closure_proofs/sr_derivative_priority2",
    "level4/closure_proofs/m_rho_stability_priority3",
    "level4/closure_proofs/p4_theory_generalization",
    "level4/closure_proofs/p7_statistical_consequences",
    "level4/stage_d",
    "level4/src",
]


def _hashes() -> dict[str, str]:
    out = {}
    for r in ROOTS:
        for p in sorted((ROOT / r).rglob("*")):
            if p.is_file() and "__pycache__" not in p.parts:
                out[str(p.relative_to(ROOT))] = hashlib.sha256(
                    p.read_bytes()).hexdigest()
    return out


def _baseline() -> dict[str, str]:
    out = {}
    for line in BEFORE.read_text().splitlines():
        h, path = line.split(maxsplit=1)
        out[path.strip()] = h
    return out


def test_protected_tree_unchanged():
    now, base = _hashes(), _baseline()
    assert set(now) == set(base), (set(base) ^ set(now))
    diff = {k for k in base if base[k] != now[k]}
    assert not diff, diff


def test_worktree_touches_only_p5():
    r = subprocess.run(["git", "status", "--porcelain"], cwd=ROOT,
                       capture_output=True, text=True, check=True)
    paths = [ln[3:].strip().strip('"') for ln in r.stdout.splitlines() if ln.strip()]
    stray = [p for p in paths
             if not p.startswith("level4/closure_proofs/p5_nonlinear_dynamics")]
    assert not stray, stray
