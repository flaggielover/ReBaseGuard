from __future__ import annotations

from rebaseguard_phase4c.analytic_audit import audit_analytic_structure


def test_analytic_structure_audit_proves_all_declared_checks():
    result = audit_analytic_structure(bits=128)
    assert all(result["checks"].values())
    assert result["reachable_enclosure"]["reset"] == "(0,0) added separately"
