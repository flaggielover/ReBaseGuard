#!/usr/bin/env python3
"""Regenerate the publication figures from the final map JSON only."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from rebaseguard_p3_map import figures  # noqa: E402

if __name__ == "__main__":
    print(json.dumps(figures.build(), indent=2))
