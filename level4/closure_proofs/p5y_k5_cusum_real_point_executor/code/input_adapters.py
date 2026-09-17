"""Input adapters: the only producers of an executor k1_binding (EXECUTOR_SPEC.md section 3).

RealInputAdapter (metadata only)
    validates the frozen K1 CUSUM cell-0 record with R1 k1_inputs.validate (V01-V10: export manifest 29ad1f9b, record
    bytes, scientific hash, producer identity, cell identity, m blocks, midpoint semantics, whole-cell R2, statuses,
    target gates) and emits ONLY identities, geometry and C_upper / C_evaluation of the frozen cell. Every numerical
    record payload (R, D, R2 intervals, magnitudes, auxiliary evidence) is REDACTED: it never leaves the adapter.
ManufacturedInputAdapter
    the same schema for a manufactured fixture (identities are hashes of the fixture specification).
The adapter performs no order-3 arithmetic. REAL_INPUT_ARITHMETIC_GUARD lives in executor_core / backends.
"""
from __future__ import annotations

import hashlib
import json
from fractions import Fraction as F

import paths

import executor_core as EC  # noqa: E402


class InputRefused(RuntimeError):
    pass


def _rat(pair) -> str:
    v = F(pair[0]) if isinstance(pair, list) else F(pair)
    if isinstance(pair, list) and len(pair) > 1 and F(pair[1]) != 0:
        raise InputRefused("non-real geometry component")
    return f"{v.numerator}/{v.denominator}"


class RealInputAdapter:
    name = "RealInputAdapter"

    def bind(self, record_bytes: bytes | None = None) -> dict:
        import k1_inputs
        p = EC.prereg()
        ident = p["k1_input_identity"]
        if record_bytes is None:
            record_bytes = (paths.REPO / ident["record"]).read_bytes()
        try:
            sealed = k1_inputs.validate(record_bytes, cell_index=0)
        except Exception as exc:                                    # malformed schema or identity: fail closed
            raise InputRefused(f"K1 validation refused: {type(exc).__name__}: {exc}") from None
        cells_sha = hashlib.sha256(k1_inputs.CELLS.read_bytes()).hexdigest()
        cell = k1_inputs.frozen_cell(0)
        binding = {"kind": "real", "detector": "CUSUM", "k1_cell_index": 0, "left": _rat(cell["left"]),
                   "right": _rat(cell["right"]), "C_upper": str(cell["C_upper"]), "C_evaluation": _rat(cell["C_evaluation"]),
                   "record_sha256": sealed["record_sha256"], "export_manifest_sha256": sealed["export_manifest_sha256"],
                   "cells_json_sha256": cells_sha, "adapter": self.name, "redacted": True}
        if binding["record_sha256"] != ident["record_sha256"] or cells_sha != ident["cells_json_sha256"]:
            raise InputRefused("K1_IDENTITY_MISMATCH: record or cells.json differs from the preregistration")
        return binding


class ManufacturedInputAdapter:
    name = "ManufacturedInputAdapter"

    def bind(self, spec: dict) -> dict:
        x1 = F(spec["x1"])
        spec_sha = hashlib.sha256(json.dumps(spec, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        return {"kind": "manufactured", "detector": "CUSUM", "k1_cell_index": 0, "left": "0/1",
                "right": f"{x1.numerator}/{x1.denominator}", "C_upper": "manufactured-rig", "C_evaluation": "0/1",
                "record_sha256": spec_sha, "export_manifest_sha256": "MANUFACTURED", "cells_json_sha256": "MANUFACTURED",
                "adapter": self.name, "redacted": True}
