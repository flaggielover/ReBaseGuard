"""Persist the Arb SR operator/geometry audit."""

from __future__ import annotations

import json
from pathlib import Path

from rebaseguard_phase4c.analytic_audit import audit_analytic_structure


ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "proofs" / "phase4c" / "analytic_structure.json"


def main() -> None:
    payload = audit_analytic_structure(bits=192)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
