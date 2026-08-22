from __future__ import annotations

import hashlib
import json
from pathlib import Path

CAMPAIGN = Path(__file__).resolve().parents[1]
RESULTS = CAMPAIGN / "results"


def load(name: str):
    return json.loads((RESULTS / name).read_text())


def test_arb_attempt_uses_only_authoritative_runtime_threshold():
    attempt = load("arb_attempt.json")
    assert attempt["threshold"]["decimal_label"] == "520.886133602749"
    assert attempt["threshold"]["runtime_rational"] == [
        4581762885148045,
        8796093022208,
    ]
    assert attempt["threshold"]["binary64_hex"] == "0x1.04716cd36dd8dp+9"
    assert "520.3125" not in (
        CAMPAIGN / "certificate/run_arb_attempt.py"
    ).read_text()


def test_fresh_candidate_digest_and_symmetry_are_audited():
    candidate = load("arb_candidate.json")
    attempt = load("arb_attempt.json")
    audit = load("arb_attempt_audit.json")
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
    assert digest == candidate["sha256"] == attempt["candidate_sha256"]
    assert audit["checks"]["candidate_a_antisymmetric"] is True
    assert audit["checks"]["candidate_b_symmetric"] is True


def test_arb_attempt_is_explicitly_open_and_not_a_gamma_enclosure():
    attempt = load("arb_attempt.json")
    requirements = attempt["certificate_requirements"]
    assert attempt["status"] == "OPEN"
    assert attempt["claim"] == "NO RIGOROUS SR GAMMA INEQUALITY CERTIFIED"
    assert requirements["outward_rounded_arb"] is True
    assert requirements["exact_threshold_serialization"] is True
    assert requirements["representative_residual_cells_only"] is True
    assert requirements["exact_global_patch_cover"] is False
    assert requirements["certified_global_residual_suprema"] is False
    assert requirements["certified_propagated_gamma_interval"] is False
    assert requirements["strict_gamma_lower_endpoint_above_two"] is False


def test_independent_open_attempt_audit_passes_without_certifying_gamma():
    audit = load("arb_attempt_audit.json")
    assert audit["passed"] is True
    assert all(audit["checks"].values())
    assert audit["audit_target"] == (
        "OPEN attempt only; this is not a Gamma certificate audit"
    )
    assert audit["certificate_status"] == "OPEN"
    assert audit["rigorous_sr_local_instability_certificate"] == "OPEN"


def test_status_language_preserves_nonblocking_derivative_closure():
    status = (CAMPAIGN / "certificate/STATUS.md").read_text()
    diagnosis = (CAMPAIGN / "FAILURE_DIAGNOSES.md").read_text()
    assert "SR-GAMMA-CERTIFIED` is not recorded" in status
    assert "non-blocking for `SR-DERIVATIVE-CLOSED`" in status
    assert "rigorous SR local instability" in diagnosis
    assert "forbidden conclusions" in diagnosis

