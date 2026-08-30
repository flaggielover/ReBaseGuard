from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path

CAMPAIGN = Path(__file__).resolve().parents[1]


def test_finite_support_certificate() -> None:
    result = json.loads((CAMPAIGN / "certificates" / "certificate.json").read_text())
    assert result["evidence_class"] == "RIGOROUS_INTERVAL_FINITE_SUPPORT_SR_ONLY"
    assert result["all_checks_pass"]
    assert [row["certified_tau"] for row in result["sr_stopping_certificates"]] == [1, 1, 6, 6]
    for row in result["records"]:
        m = row["m"]
        assert Fraction(row["exact"]["gamma"]) == Fraction(2) + Fraction(2, m)
        assert all(row["checks"].values())
    assert "not a frozen" in result["evidence_boundary"]
