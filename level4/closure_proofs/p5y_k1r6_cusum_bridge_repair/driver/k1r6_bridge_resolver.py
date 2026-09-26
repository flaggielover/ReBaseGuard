"""K1R6 bridge-only identity resolver. Hand-written, orchestration only (no scientific content).

Replaces, for identity geometry ONLY, the historical resolver repair_universe._cell_of, which looks
the cell up in aux4's frozen 326-cell spec.CELLS (the K1R5 production defect: KeyError on 1000).

    * accepts exactly ("CUSUM", 1000) and ("CUSUM", 1001);
    * reads them from the K1R4 CUSUM bridge table and verifies its exact SHA-256 BEFORE use,
      against a pin that must itself equal the hash frozen in the K1R4 checkpoint;
    * refuses every other (detector, index) -- historical, negative, unknown, SR;
    * has NO fallback to the historical table (repair_universe is not imported here).
"""
import copy
import hashlib
import json
from pathlib import Path

K1R4 = Path(__file__).resolve().parents[2] / "p5y_k1r4_bridge_successor"
TABLE = K1R4 / "config/CUSUM_BRIDGE_CELL_TABLE.json"
PINNED_TABLE_SHA256 = "db02a798b57e6317bcdbdd6bc40b7ac9ae31e2e966f0ba303cec12df8f54ab90"
BRIDGE_CELLS_SHA256 = PINNED_TABLE_SHA256          # identity field cells_sha256 (CELL_PROVENANCE)
BRIDGE_INDICES = (1000, 1001)
HISTORICAL_INDICES = range(0, 326)


class BridgeIdentityRefused(RuntimeError):
    """A (detector, index) outside the bridge, or a bridge table that is not the frozen one."""


def _k1r4_frozen_table_hash() -> str:
    cp = json.loads((K1R4 / "config/CHECKPOINT.json").read_text())
    return cp["frozen_artifacts"]["CUSUM_BRIDGE_CELL_TABLE.json"]


if _k1r4_frozen_table_hash() != PINNED_TABLE_SHA256:
    raise BridgeIdentityRefused("K1R6 table pin differs from the hash frozen in the K1R4 checkpoint")


def resolve(detector, index, *, table=TABLE, pinned=PINNED_TABLE_SHA256) -> dict:
    if detector != "CUSUM":
        raise BridgeIdentityRefused(f"detector {detector!r}: the K1R6 resolver serves CUSUM bridge cells only")
    if type(index) is not int or index not in BRIDGE_INDICES:
        if type(index) is int and index in HISTORICAL_INDICES:
            raise BridgeIdentityRefused(f"historical CUSUM index {index}: never resolved here (no historical fallback)")
        raise BridgeIdentityRefused(f"index {index!r} is not a K1R6 CUSUM bridge cell")
    if pinned != PINNED_TABLE_SHA256:
        raise BridgeIdentityRefused("bridge-table pin altered: refusing an unpinned table hash")
    raw = Path(table).read_bytes()
    got = hashlib.sha256(raw).hexdigest()
    if got != pinned:
        raise BridgeIdentityRefused(f"bridge table hash {got} != frozen {pinned}")
    hits = [c for c in json.loads(raw)["cells"] if c.get("detector") == "CUSUM" and c.get("index") == index]
    if len(hits) != 1:
        raise BridgeIdentityRefused(f"bridge cell {index} not uniquely present in the frozen table")
    return copy.deepcopy(hits[0])


def _bridge_cell_of(detector, index) -> dict:
    """Drop-in for the identity geometry lookup; production binding (fixed table and pin)."""
    return resolve(detector, index)


PROVENANCE = {
    "CELL_PROVENANCE": {
        "source": "p5y_k1r4_bridge_successor/config/CUSUM_BRIDGE_CELL_TABLE.json",
        "sha256": PINNED_TABLE_SHA256,
        "identity_fields": ["cells_sha256", "detector", "cell_index", "e0", "rho", "left", "right", "C_upper"],
    },
    "SCIENTIFIC_REGIME_PROVENANCE": {
        "source": "inherited aux4 / cover-ledger spec (spec.CHECKPOINT_SHA256, spec.ERROR_ALGEBRA_SHA256, spec.TOTAL_UNITS)",
        "identity_fields": ["checkpoint_hash", "error_algebra_sha256", "obligation_universe_total",
                            "implementation_hash_kind"],
        "meaning": ("the frozen scientific regime the bridge cells are certified under: CUSUM detector (h=5, k=1/2), "
                    "m universe {1,2,3,5}, 256-bit precision, target, error algebra, ledger budgets and geometry "
                    "CONSTRUCTION rules (grid, step, C rule), and the 28-unit-per-cell obligation scheme. The "
                    "checkpoint also names the historical 642-cell table; K1R6 does NOT claim that table as the "
                    "origin of cells 1000/1001 -- cell origin is carried exclusively by CELL_PROVENANCE."),
    },
}
