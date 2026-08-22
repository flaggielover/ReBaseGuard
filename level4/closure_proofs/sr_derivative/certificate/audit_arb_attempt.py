#!/usr/bin/env python3
"""Independent audit of the OPEN authoritative-threshold Arb attempt."""

from __future__ import annotations

import hashlib
import json
import math
import os
import tempfile
from pathlib import Path

from flint import arb, ctx

CAMPAIGN = Path(__file__).resolve().parents[1]
RESULTS = CAMPAIGN / "results"
PRODUCER = CAMPAIGN / "certificate/run_arb_attempt.py"
NUMERATOR = 4581762885148045
DENOMINATOR = 8796093022208


def exact(numerator: int, denominator: int = 1) -> arb:
    return arb(numerator) / arb(denominator)


def atomic_json(path: Path, value: dict) -> None:
    with tempfile.NamedTemporaryFile(
        mode="w", dir=path.parent, prefix=f".{path.name}.", delete=False
    ) as handle:
        json.dump(value, handle, indent=2, sort_keys=True)
        handle.write("\n")
        temporary = Path(handle.name)
    os.replace(temporary, path)


def main() -> int:
    attempt = json.loads((RESULTS / "arb_attempt.json").read_text())
    candidate = json.loads((RESULTS / "arb_candidate.json").read_text())
    payload = json.dumps(
        {
            "degree": candidate["degree"],
            "scale_bits": candidate["scale_bits"],
            "a": candidate["a"],
            "b": candidate["b"],
        },
        separators=(",", ":"),
        sort_keys=True,
    ).encode()
    digest = hashlib.sha256(payload).hexdigest()

    a = candidate["a"]
    b = candidate["b"]
    size = candidate["degree"] + 1
    antisymmetric = all(a[i][j] == -a[j][i] for i in range(size) for j in range(size))
    symmetric = all(b[i][j] == b[j][i] for i in range(size) for j in range(size))
    diagonal_zero = all(a[i][i] == 0 for i in range(size))

    with ctx.workprec(256):
        threshold = exact(NUMERATOR, DENOMINATOR)
        one = arb(1)
        # Algebraically independent reconstruction of the invariant cap:
        # exp(C) = e*A*(A+1)/(e*A-(A+1)).
        exp_cap = arb.const_e() * threshold * (threshold + one) / (
            arb.const_e() * threshold - (threshold + one)
        )
        sum_cap = exp_cap.log()
        min_width = arb(2) * threshold.log() + one - sum_cap
        producer_sum_cap = arb(attempt["geometry"]["sum_cap"]["ball"])
        producer_width = arb(
            attempt["geometry"]["minimum_continuation_width"]["ball"]
        )
        geometry_overlap = not (sum_cap < producer_sum_cap or producer_sum_cap < sum_cap)
        width_overlap = not (min_width < producer_width or producer_width < min_width)

    requirements = attempt["certificate_requirements"]
    checks = {
        "status_is_open": attempt["status"] == "OPEN",
        "no_certificate_claim": attempt["claim"]
        == "NO RIGOROUS SR GAMMA INEQUALITY CERTIFIED",
        "threshold_ratio_exact": attempt["threshold"]["runtime_rational"]
        == [NUMERATOR, DENOMINATOR],
        "threshold_hex_exact": attempt["threshold"]["binary64_hex"]
        == float(NUMERATOR / DENOMINATOR).hex(),
        "candidate_digest_reconstructed": digest
        == candidate["sha256"]
        == attempt["candidate_sha256"],
        "candidate_a_antisymmetric": antisymmetric,
        "candidate_a_diagonal_zero": diagonal_zero,
        "candidate_b_symmetric": symmetric,
        "independent_sum_cap_overlap": geometry_overlap,
        "independent_continuation_width_overlap": width_overlap,
        "representative_cells_not_globalized": requirements[
            "representative_residual_cells_only"
        ]
        and not requirements["certified_global_residual_suprema"],
        "no_gamma_interval": not requirements["certified_propagated_gamma_interval"],
        "no_strict_lower_bound": not requirements[
            "strict_gamma_lower_endpoint_above_two"
        ],
        "historical_threshold_absent_from_producer": "520.3125"
        not in PRODUCER.read_text(),
    }
    passed = all(checks.values())
    output = {
        "schema": "rebaseguard.sr-derivative.arb-attempt-audit.v1",
        "audit_target": "OPEN attempt only; this is not a Gamma certificate audit",
        "checks": checks,
        "passed": passed,
        "certificate_status": "OPEN",
        "rigorous_sr_local_instability_certificate": "OPEN",
    }
    atomic_json(RESULTS / "arb_attempt_audit.json", output)
    print(f"Arb OPEN-attempt audit: {'PASS' if passed else 'FAIL'}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())

