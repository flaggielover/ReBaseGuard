"""R4 certified operator constants and the gated real entry point (fail closed; real-cell evaluation out of scope).

    load_certificates() -> {"C_o0": Fraction, "C_e0": Fraction}
        C_o0: R4 exact odd-block certificate (config/operator_certificates/C_o0_odd_block_certificate.json)
        C_e0: R3 whole-space certificate (R3 artifact, byte-pinned; R3 is not modified)
    Refuses (R4Refusal) if the registry bytes differ from the pinned sha256, if an entry is missing, or if an artifact's
    bytes differ from its registry sha256. There is NO silent fallback: the R3 coupling bound C_o0 <= 20.4322 remains
    a valid constant but is used only where a caller passes it explicitly.
"""
from __future__ import annotations

import hashlib
import json
from fractions import Fraction as F
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
REPO = NS.parents[2]

AUTH_REGISTRY = NS / "config/REAL_CELL_AUTHORIZATION_REGISTRY_R4.json"
AUTH_REGISTRY_SHA256 = "43b5dd2bd3ef014250724cb892a3175c523fc3462cb204dac9b58e79c8115ebb"
CERT_REGISTRY = NS / "config/OPERATOR_CERTIFICATES_R4.json"
CERT_REGISTRY_SHA256 = "a645a15716e74b69c89e06f09dfdbddd9b5cee8f19d34ea5635c9c0d06de6413"
REQUIRED = ("C_o0", "C_e0")


class R4Refusal(RuntimeError):
    pass


def load_certificates() -> dict:
    raw = CERT_REGISTRY.read_bytes()
    if hashlib.sha256(raw).hexdigest() != CERT_REGISTRY_SHA256:
        raise R4Refusal("OPERATOR_CERTIFICATE_REGISTRY_ALTERED")
    reg = json.loads(raw)
    out = {}
    for entry in reg["certificates"]:
        art = REPO / entry["artifact"]
        if not art.exists() or hashlib.sha256(art.read_bytes()).hexdigest() != entry["artifact_sha256"]:
            raise R4Refusal(f"OPERATOR_CERTIFICATE_ARTIFACT_ALTERED {entry['name']}")
        if json.loads(art.read_text())["certified"]["C_upper_bound"] != entry["value_upper"]:
            raise R4Refusal(f"OPERATOR_CERTIFICATE_VALUE_MISMATCH {entry['name']}")
        out[entry["name"]] = F(entry["value_upper"])
    for name in REQUIRED:
        if name not in out:
            raise R4Refusal(f"MISSING_OPERATOR_CERTIFICATE {name}")
    return out


def certify_real_cell_r4(cell_index: int, *, authorization=None, record_bytes: bytes | None = None):
    raw = AUTH_REGISTRY.read_bytes()
    if hashlib.sha256(raw).hexdigest() != AUTH_REGISTRY_SHA256:
        raise R4Refusal("REAL_CELL_NOT_AUTHORIZED: authorization registry altered")
    registry = json.loads(raw)
    digest = None if authorization is None else hashlib.sha256(
        json.dumps(authorization, sort_keys=True).encode()).hexdigest()
    if not any(a.get("sha256") == digest and cell_index in a.get("cells", []) for a in registry["authorizations"]):
        raise R4Refusal(f"REAL_CELL_NOT_AUTHORIZED: cell {cell_index} (R4 registry is frozen empty)")
    load_certificates()
    raise R4Refusal("OUT_OF_R4_SCOPE: real-cell evaluation requires a separately governed successor")
