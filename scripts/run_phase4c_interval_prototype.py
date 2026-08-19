"""Generate representative-cell Arb interval feasibility measurements."""

from __future__ import annotations

import json
from pathlib import Path

from rebaseguard_phase4c.interval_prototype import run_representative_prototype


ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "proofs" / "phase4c" / "interval_prototype.json"


def main() -> None:
    payload = run_representative_prototype(bits=192)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
