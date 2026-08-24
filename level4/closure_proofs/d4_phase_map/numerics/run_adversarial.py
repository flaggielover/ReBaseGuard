#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

CAMPAIGN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(CAMPAIGN / "src"))

from rebaseguard_d4.adversarial import run  # noqa: E402

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--pre-full", action="store_true")
    args = parser.parse_args()
    result = run(pre_full=args.pre_full)
    print(f"adversarial: {result['passed']}/{result['total']}")
