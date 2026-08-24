#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

CAMPAIGN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(CAMPAIGN / "src"))

from rebaseguard_d4.reports import build  # noqa: E402

if __name__ == "__main__":
    build()
