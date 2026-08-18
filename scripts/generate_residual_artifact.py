"""Generate exact candidate inputs and the Arb continuum residual artifact."""

from __future__ import annotations

import json
from pathlib import Path

from rebaseguard_certify.residual import (
    certify_continuum_residuals,
    construct_candidate_payloads,
)


def main() -> None:
    candidates = construct_candidate_payloads(
        degree=12, quadrature_order=400, scale_bits=50
    )
    residual = certify_continuum_residuals(
        candidates,
        phi_order=50,
        subdivision_depth=0,
        bits=256,
    )
    Path("proofs/candidates.json").write_text(
        json.dumps(candidates, indent=2, sort_keys=True) + "\n"
    )
    Path("proofs/residual.json").write_text(
        json.dumps(residual, indent=2, sort_keys=True) + "\n"
    )
    print(json.dumps({"delta_a": residual["delta_a"], "delta_b": residual["delta_b"], "b_hat_origin": residual["b_hat_origin"]}, indent=2))


if __name__ == "__main__":
    main()
