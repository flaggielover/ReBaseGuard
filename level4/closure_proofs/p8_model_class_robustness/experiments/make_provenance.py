"""Pin the exact bytes of every P8 source file and every artifact P8 read."""
from __future__ import annotations

import datetime
import hashlib
import json
import platform
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE / "src"))
from rebaseguard_p8.config import (                                 # noqa: E402
    P3, P4, RESULTS, ROOT, SEED_NAMESPACE, STAGE_D)


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> None:
    import numpy
    import scipy
    srcs = sorted(list((HERE / "src").rglob("*.py"))
                  + list((HERE / "experiments").rglob("*.py"))
                  + list((HERE / "tests").rglob("*.py")))
    inherited = {
        "level4/src/rebaseguard_level4/frozen.py":
            ROOT / "level4/src/rebaseguard_level4/frozen.py",
        "level4/stage_d/results/d3_nongaussian.json":
            STAGE_D / "results/d3_nongaussian.json",
        "level4/stage_d/results/calibration_d1.json":
            STAGE_D / "results/calibration_d1.json",
        "P3 boundary_table.json": P3 / "results/boundary_table.json",
        "P4 correspondence.csv": P4 / "results/correspondence.csv",
        "P4 route_a.py": P4 / "src/rebaseguard_location_family/route_a.py",
    }
    prov = {
        "schema": "rebaseguard.p8.provenance.v1",
        "recorded_utc": datetime.datetime.now(datetime.UTC).isoformat(),
        "anchor_commit": subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True,
            text=True).stdout.strip(),
        "anchor_commit_declared": "ffe23a63181e2ff11380768d3c73980de80f94fb",
        "environment": {"python": sys.version.split()[0],
                        "numpy": numpy.__version__, "scipy": scipy.__version__,
                        "platform": platform.platform(),
                        "interpreter": "level4/.venv/bin/python"},
        "seed_namespace_hex": hex(SEED_NAMESPACE),
        "p8_source_sha256": {str(p.relative_to(HERE)): sha(p) for p in srcs},
        "inherited_artifact_sha256": {k: sha(v) for k, v in inherited.items()},
        "note": ("the inherited digests pin the exact bytes of every artifact P8 "
                 "read. If any differs at replay time, P8's reproduction "
                 "comparisons are against a different object and must be "
                 "re-derived."),
    }
    (RESULTS / "provenance.json").write_text(json.dumps(prov, indent=1) + "\n")
    print(prov["anchor_commit"], prov["environment"])


if __name__ == "__main__":
    main()
