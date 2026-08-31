#!/usr/bin/env python3
"""Regenerate every Priority-3 machine-readable map artifact."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from rebaseguard_p3_map import figures, mapbuild, provenance, reports  # noqa: E402


def main() -> None:
    provenance.build()
    payload = mapbuild.build()
    index = figures.build()
    reports.build()
    print(json.dumps({
        "map_valid": payload["valid"],
        "checks": payload["checks"],
        "cells": len(payload["cells"]),
        "boundary_cells": len(payload["boundary_cells"]),
        "figures": sorted(index["figures"]),
        "every_plotted_cell_traceable":
            index["traceability"]["every_plotted_cell_traceable"],
    }, indent=2))
    if not payload["valid"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
