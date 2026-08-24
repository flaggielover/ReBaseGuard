#!/usr/bin/env python3
"""Record byte-stable replay of analysis and figures from committed summaries."""
from __future__ import annotations

import argparse
import hashlib
import json
import tempfile
from pathlib import Path

from analysis import build_findings
from config import FIGURES, RESULTS, canonical_json
from figures import NAMES, generate


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check() -> dict:
    science = RESULTS / "scientific_findings.json"
    expected_science = canonical_json(build_findings())
    science_stable = science.exists() and science.read_text() == expected_science
    with tempfile.TemporaryDirectory(prefix="l4r06-replay-") as tmp:
        replay = generate(output=Path(tmp))
    figure_stable = all((FIGURES / name).exists()
                        and sha(FIGURES / name) == replay["files"][name]
                        for name in NAMES)
    return {
        "schema": "rebaseguard.l4r06-reproduction.v1",
        "status": "PASS" if science_stable and figure_stable else "FAIL",
        "scientific_findings_byte_stable": science_stable,
        "figures_byte_stable": figure_stable,
        "scientific_findings_sha256": sha(science) if science.exists() else "MISSING",
        "figure_sha256": {name: sha(FIGURES / name) if (FIGURES / name).exists() else "MISSING"
                          for name in NAMES},
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = check()
    path = RESULTS / "reproduction.json"
    if args.check:
        if not path.exists() or path.read_text() != canonical_json(result):
            print("L4R-06 reproduction record is not byte-stable")
            return 1
    else:
        path.write_text(canonical_json(result))
    print("L4R-06 reproduction:", result["status"])
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
