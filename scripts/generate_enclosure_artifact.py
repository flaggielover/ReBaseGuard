"""Propagate the certified residual and contraction artifacts."""

from __future__ import annotations

import json
from pathlib import Path

from rebaseguard_certify.enclosure import propagate_residual_enclosure


def main() -> None:
    residual = json.loads(Path("proofs/residual.json").read_text())
    contraction = json.loads(Path("proofs/contraction_monotone.json").read_text())
    enclosure = propagate_residual_enclosure(residual, contraction, bits=256)
    Path("proofs/enclosure.json").write_text(
        json.dumps(enclosure, indent=2, sort_keys=True) + "\n"
    )
    print(json.dumps(enclosure, indent=2, sort_keys=True))
    if not enclosure["gamma_lower_gt_2"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
