import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def _sha256(relative: str) -> str:
    return hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()


def test_protected_historical_and_certificate_hashes_are_unchanged():
    assert _sha256("src/rebaseguard_certify/bellman.py") == (
        "5731eb539d73d0f0ca578c22ebc48be14220c9cb61e71d2ac816b9c85dc48343"
    )
    assert _sha256("proofs/certificate.json") == (
        "85e68c7dde306f2e6ce464203def22089e9b935d1cfca4b4944cef191d80545e"
    )


def test_pregate_artifact_records_resolved_discrepancy():
    payload = json.loads((ROOT / "diagnostics/phase4_pregate.json").read_text())
    assert payload["classification"]["category"] == "D. FINITE DISCRETIZATION BIAS"
    assert payload["historical_reproduction"]["gamma_finite"]["ball"].startswith(
        "[18.740148445039828"
    )
    point = payload["corrected_point_estimate"]["gamma"]
    assert 15.88 < point < 15.90
    assert payload["monte_carlo"]["combined"]["n"] == 2_000_000
