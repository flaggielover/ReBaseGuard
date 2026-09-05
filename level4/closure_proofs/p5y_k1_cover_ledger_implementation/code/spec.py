"""Read-only loader for the FROZEN p5y_k1_cover_ledger_successor specification.

This module never writes into the frozen namespace and never reinterprets it.
Every constant used anywhere in this implementation namespace is read from the
frozen files and hash-verified against the hashes published in the frozen
CHECKPOINT.md table. A hash mismatch is a hard stop, not a warning.
"""
from __future__ import annotations

import hashlib
import json
from fractions import Fraction as F
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
ROOT = NS.parents[2]
SPEC_NS = ROOT / "level4/closure_proofs/p5y_k1_cover_ledger_successor"

# Published in the frozen CHECKPOINT.md "Binding artifact SHA-256 hashes" table.
FROZEN_HASHES = {
    "config/checkpoint.json": "1c2a6825f19e19de6fb588647ca3fc4618068087ef0976292ca7bbeca701f13f",
    "config/cells.json": "341eb5e95161bbdc2d15c1dca72eb8c4565982fab562e1c5a337139375b67c2f",
    "config/cover_witnesses.json": "dcb89ccc1a15729a0fb2469ce9c28b0891a81dffe112840b2325417cda31f446",
    "config/cost_model.json": "2a3ec2171d1d639770b6cca8b131e7947677b7ec89e39da24e7c729f3a8e0d34",
    "config/record_schema.json": "666dee60b9ab60203f7582d01e49416c23e75cbacd713655344ff459689038a0",
    "ERROR_ALGEBRA.md": "4f32df0273d05b1b4e0136e2a901adec9979e158b5decd8c9bf3cce0e35b9ffa",
    "manifests/authority.json": "4ffd0e47d301886646f45884c5c233bf8f42f3ed6dd785d778de3298ed2f523e",
    "manifests/protected_start.json": "d30f011447df72315e568c279f53fdf8a0d7f152a9720321d26a4f1ae9f40873",
}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def verify_frozen_spec() -> dict[str, str]:
    """Hash every frozen binding artifact. Raises on any mismatch."""
    seen = {}
    for rel, expect in FROZEN_HASHES.items():
        got = digest((SPEC_NS / rel).read_bytes())
        if got != expect:
            raise RuntimeError(
                f"FROZEN_SPEC_MUTATED: {rel} sha256 {got} != published {expect}")
        seen[rel] = got
    return seen


def _load(rel: str):
    return json.loads((SPEC_NS / rel).read_text())


verify_frozen_spec()

CHECKPOINT = _load("config/checkpoint.json")
CELLS = _load("config/cells.json")
COST_MODEL = _load("config/cost_model.json")
RECORD_SCHEMA = _load("config/record_schema.json")

# The frozen checkpoint hash used as part of every resume identity.
CHECKPOINT_SHA256 = FROZEN_HASHES["config/checkpoint.json"]
CELLS_SHA256 = CHECKPOINT["geometry"]["cells_sha256"]
ERROR_ALGEBRA_SHA256 = FROZEN_HASHES["ERROR_ALGEBRA.md"]

# ---------------------------------------------------------------- scope
M_VALUES = tuple(CHECKPOINT["scope"]["m_values"])                 # (1,2,3,5)
DETECTORS = ("CUSUM", "SR")
PRODUCTION_BITS = CHECKPOINT["precision"]["CUSUM_production_bits"]  # 256
assert PRODUCTION_BITS == CHECKPOINT["precision"]["SR_production_bits"] == 256
PRECISION_ESCALATION_ALLOWED = CHECKPOINT["precision"]["PRECISION_ESCALATION_ALLOWED"]
DEGREE_ADAPTATION_ALLOWED = CHECKPOINT["precision"]["DEGREE_ADAPTATION_ALLOWED"]

# ---------------------------------------------------------------- ledger
TOP_BUDGETS = {k: F(v) for k, v in CHECKPOINT["ledger"]["top_level_budgets"].items()}
NESTED_CANDIDATE = {k: F(v) for k, v in CHECKPOINT["ledger"]["nested_B_candidate"].items()}
CLAIMANT_OWNERS = dict(CHECKPOINT["ledger"]["claimant_owners"])
TOP_RESERVE = F(CHECKPOINT["ledger"]["top_reserve"])
LOCAL_GATE_BUDGET = F(CHECKPOINT["ledger"]["local_gate_budget"])
B_END_GATE = NESTED_CANDIDATE["B_end"]
OWNERSHIP_KEY = tuple(CHECKPOINT["ledger"]["ownership_key"])
RESERVE_DRAWABLE = CHECKPOINT["ledger"]["reserve_drawable"]
REDISTRIBUTION_ALLOWED = CHECKPOINT["ledger"]["redistribution_allowed"]

# ---------------------------------------------------------------- work
COUNTS = dict(CHECKPOINT["work"]["counts"])                        # CUSUM 326, SR 316
OBJECTS_PER_CELL = CHECKPOINT["work"]["objects_per_cell"]          # 19
DEPENDENCY_BUNDLES_PER_CELL = CHECKPOINT["work"]["dependency_bundles_per_cell"]
CURVATURE_BUNDLES_PER_CELL = CHECKPOINT["work"]["curvature_bundles_per_cell"]
ASSEMBLY_UNITS_PER_CELL = CHECKPOINT["work"]["assembly_units_per_cell"]
FAR_FIELD_UNITS = CHECKPOINT["work"]["far_field_units"]
OBJECT_UNITS = CHECKPOINT["work"]["object_units"]                  # 12198
TOTAL_UNITS = CHECKPOINT["work"]["total_units"]                    # 17978
CURVATURE_SHARED_OWNER_M = CHECKPOINT["work"]["curvature_shared_owner_m"]

# ---------------------------------------------------------------- cost
HARD_CAP_CPU_H = COST_MODEL["hard_cap_cpu_h"]                      # 1126
WORKER_CEILING = CHECKPOINT["worker_ceiling"]                      # 64
PER_WORKER_BUDGET_MIB = CHECKPOINT["memory_and_cache"]["inherited"]["per_worker_budget_mib"]

PRODUCTION_ENABLED = CHECKPOINT["production_enabled"]              # False

# ---------------------------------------------------------------- assembly
ASSEMBLY_TERMS = {
    int(m): [(kind, int(r), int(j), F(c)) for kind, r, j, c in rows]
    for m, rows in CHECKPOINT["assembly"].items()
}

SPLICE_EXACT = dict(CHECKPOINT["geometry"]["splice_exact"])
SR_TERMINAL_EXPR = SPLICE_EXACT["SR"]


def cells_for(detector: str) -> list[dict]:
    return [c for c in CELLS if c["detector"] == detector]


def affine_fractions(pair) -> tuple[F, F]:
    """A frozen [p, s] endpoint encoding means p + s * c_SR."""
    return F(pair[0]), F(pair[1])


def is_symbolic(pair) -> bool:
    return F(pair[1]) != 0


assert len(CELLS) == COUNTS["CUSUM"] + COUNTS["SR"] == 642
assert OBJECT_UNITS == OBJECTS_PER_CELL * len(CELLS) == 12198
assert TOTAL_UNITS == 28 * len(CELLS) + FAR_FIELD_UNITS == 17978
assert HARD_CAP_CPU_H == 1126
assert PRODUCTION_ENABLED is False
