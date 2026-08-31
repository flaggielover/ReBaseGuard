#!/usr/bin/env python3
"""Render STABILITY_MAP_REPORT.md from the final map JSON only."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from rebaseguard_p3_map import reports  # noqa: E402

if __name__ == "__main__":
    print(reports.build())
