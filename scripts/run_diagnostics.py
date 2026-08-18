"""Generate the explicitly non-rigorous reference diagnostic."""

from __future__ import annotations

import json
from pathlib import Path

from rebaseguard_certify.diagnostics import simulate


def main() -> None:
    output = {
        "proof_role": "NON-RIGOROUS DIAGNOSTIC ONLY",
        "runs": [
            simulate(200_000, seed=1729).summary(),
            simulate(200_000, seed=20260818).summary(),
        ],
    }
    destination = Path("diagnostics/reference.json")
    destination.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n")
    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

