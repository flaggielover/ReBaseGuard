import json
from pathlib import Path

import pytest

from rebaseguard_certify.audit import AuditError, audit_certificate


def test_quick_audit_accepts_current_artifacts():
    source_root = Path.cwd()
    certificate_path = source_root / "proofs" / "certificate.json"
    report = audit_certificate(certificate_path, full=False)
    assert report["status"] == "PASS"
    assert report["Gamma_lower_gt_2"] is True


def test_quick_audit_rejects_wrong_model(tmp_path):
    source_root = Path.cwd()
    original = source_root / "proofs" / "certificate.json"
    payload = json.loads(original.read_text())
    payload["model"]["h"]["numerator"] = 6
    tampered = tmp_path / "certificate.json"
    tampered.write_text(json.dumps(payload))
    with pytest.raises(AuditError, match="wrong model"):
        audit_certificate(tampered, full=False)
