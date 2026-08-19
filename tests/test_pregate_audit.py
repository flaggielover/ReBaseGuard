from pathlib import Path

from rebaseguard_certify.pregate_audit import audit_pregate


def test_phase4_pregate_audit_passes():
    repository = Path(__file__).resolve().parent.parent
    result = audit_pregate(repository)
    assert result["status"] == "PASS"
    assert result["level4_route"] == "GREEN"
