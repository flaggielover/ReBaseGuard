#!/usr/bin/env python3
"""P5 provenance: hashes of every produced artifact and of the frozen inputs."""
from __future__ import annotations

import hashlib
import json
import platform
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from rebaseguard_p5 import P5, P3, P7, RESULTS, SEED_FAMILY, SEED_FAMILY_ALT

ROOT = P5.parents[2]


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def tree(d: Path, pat="*"):
    return {str(p.relative_to(P5)): sha(p) for p in sorted(d.rglob(pat))
            if p.is_file() and "__pycache__" not in p.parts}


head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT,
                      capture_output=True, text=True, check=True).stdout.strip()
out = {
    "campaign": "level4/closure_proofs/p5_nonlinear_dynamics",
    "git_head_at_start": "3ae61138dc2353e86788d4c5e44ab3e3286e1a6f",
    "git_head_now": head,
    "python": sys.version.split()[0],
    "platform": platform.platform(),
    "seed_families": {"primary": SEED_FAMILY, "replication": SEED_FAMILY_ALT},
    "seed_derivation": "np.random.SeedSequence([family, detector_code, tag, index]); "
                       "detector_code = {'cusum': 11, 'sr': 13}; hash(str) never used",
    "frozen_inputs": {
        "p3_boundary_table": sha(P3 / "results" / "boundary_table.json"),
        "p7_chain": sha(P7 / "src" / "rebaseguard_p7" / "chain.py"),
        "p7_cycles": sha(P7 / "src" / "rebaseguard_p7" / "cycles.py"),
        "p7_detectors": sha(P7 / "src" / "rebaseguard_p7" / "detectors.py"),
        "frozen_cusum": sha(ROOT / "level4" / "src" / "rebaseguard_level4"
                            / "frozen.py"),
    },
    "src": tree(P5 / "src", "*.py"),
    "experiments": tree(P5 / "experiments", "*.py"),
    "tests": tree(P5 / "tests", "*.py"),
    "lean": tree(P5 / "lean", "*.lean"),
    "results": tree(P5 / "results", "*.json"),
    "figures": tree(P5 / "figures", "*.png"),
}
(RESULTS / "provenance.json").write_text(json.dumps(out, indent=1))
print("wrote provenance.json:", len(out["results"]), "result files,",
      len(out["figures"]), "figures")
