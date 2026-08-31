"""Records the provenance of every P7 artifact: hashes, sizes, seeds, inputs."""
from __future__ import annotations

import hashlib
import json
import platform
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from rebaseguard_p7.config import (                                    # noqa: E402
    DETECTOR_CODE, M_GRID, P3, RESULTS, SEED_FAMILY, load_p3_boundaries,
)

CAMPAIGN = Path(__file__).resolve().parents[1]
ROOT = CAMPAIGN.parents[2]


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> None:
    files = {}
    for p in sorted(CAMPAIGN.rglob("*")):
        if (p.is_dir() or "__pycache__" in p.parts or p.name.startswith("_log_")
                or p.name in {"PROVENANCE.json", "PROVENANCE.md"}):
            continue
        files[str(p.relative_to(CAMPAIGN))] = {"sha256": sha(p),
                                               "bytes": p.stat().st_size}
    inputs = {}
    for rel in ("level4/closure_proofs/m_rho_stability_priority3/results/boundary_table.json",
                "level4/closure_proofs/m_rho_stability_priority3/THEOREM.md",
                "level4/closure_proofs/m_gt_1_priority1/THEOREM.md",
                "level4/closure_proofs/sr_derivative_priority2/THEOREM.md",
                "level4/stage_d/STAGE_D_PROTOCOL.md",
                "level4/stage_d/src/chain.py",
                "level4/stage_d/src/stopped.py",
                "level4/src/rebaseguard_level4/frozen.py",
                "level4/stage_d/results/calibration_d1.json",
                "level4/stage_d/results/d2_5_verdict.json"):
        p = ROOT / rel
        inputs[rel] = {"sha256": sha(p), "read_only": True}

    out = {
        "campaign": "Level-4 Priority 7 statistical consequences",
        "scientific_verdict": "CLOSED",
        "repository_integration_verdict": "READY_FOR_COMMIT",
        "python": platform.python_version(),
        "numpy": np.__version__,
        "seed_family": SEED_FAMILY,
        "detector_codes": DETECTOR_CODE,
        "seed_stages": {
            "2": "chain sweep  [SEED_FAMILY, 2, detector_code, m, round(rho*1e7)]",
            "3": "response curves  [SEED_FAMILY, 3, detector_code, sign, round(|x|*1e6)]",
            "5": "delay validation  [SEED_FAMILY, 5, detector_code, m, round(rho*1e7), round(Delta*1000)]",
            "7": "gain correspondence  [SEED_FAMILY, 7, detector_code, batch]",
            "adversarial replication": "seed family 20260901, stage 2 (deliberately outside the production family)",
            "independent adjudication": "seed family 20260917, stages 71/72",
        },
        "m_grid": list(M_GRID),
        "p3_boundaries_used": {f"{d}_m{m}": load_p3_boundaries()[(d, m)]["rho_crit"]
                               for d in ("cusum", "sr") for m in M_GRID},
        "read_only_inputs": inputs,
        "p4_used": False,
        "p4_supplementary_diagnostic_used": True,
        "p4_note": ("P4 remains PARTIAL and is not a premise. Its adjudicated "
                    "1.6M-path SR replay is used only as supplementary diagnosis; "
                    "P7 closure rests on closed P1-P3."),
        "files": files,
    }
    (CAMPAIGN / "PROVENANCE.json").write_text(json.dumps(out, indent=1))
    lines = ["# P7 provenance", "",
             f"Machine-readable copy: `PROVENANCE.json` "
             f"({len(files)} campaign files hashed).", "",
             f"* Python {out['python']}, numpy {out['numpy']}",
             f"* Seed family `{SEED_FAMILY}` (Stage D uses `20261001`; no overlap)",
             f"* Detector codes `{DETECTOR_CODE}` — fixed integers, because "
             "Python salts `hash(str)` per process", "",
             "## Seed derivation", ""]
    for k, v in out["seed_stages"].items():
        lines.append(f"* stage `{k}`: `{v}`")
    lines += ["", "## Read-only inputs (never modified)", "",
              "| path | sha256 |", "|---|---|"]
    for k, v in inputs.items():
        lines.append(f"| `{k}` | `{v['sha256'][:16]}...` |")
    lines += ["", "## P4", "",
              "P4 remains **PARTIAL** and is not a premise. Its adjudicated "
              "1.6-million-path SR replay is used only as supplementary diagnosis; "
              "P7 closure rests on the closed P1--P3 artifacts.", "",
              "## Sample sizes", "",
              "| experiment | size |", "|---|---|",
              "| chain sweep | 104 cells x 5,000 replicates x 50 cycles (38 post burn-in) |",
              "| response curves | 4x10^5 paths for `|x| <= 0.15`, 2x10^5 to `0.5`, 10^5 beyond; 34 grid points per detector |",
              "| delay validation | 8 cells x 40,000 replicates, shift at cycle 25 |",
              "| gain correspondence | 20 batches x 100,000 cycles per detector |",
              "| adversarial replication | 6 cells x 5,000 replicates, independent seed family |",
              "| independent adjudication | 16 in-control cells x 2,500 replicates; 2 delay cells x 30,000 replicates |"]
    (CAMPAIGN / "PROVENANCE.md").write_text("\n".join(lines) + "\n")
    print("wrote PROVENANCE.md and PROVENANCE.json;", len(files), "files hashed")


if __name__ == "__main__":
    main()
