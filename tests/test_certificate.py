import json
from pathlib import Path

from rebaseguard_certify.certificate import build_certificate


def test_certificate_assembles_current_proof_artifacts():
    certificate = build_certificate(Path.cwd())
    assert certificate["result"] == "Gamma_lower > 2"
    assert certificate["gaussian_handling"]["tail_cutoff"] is None
    assert len(certificate["artifacts"]) == 5
    json.dumps(certificate)

