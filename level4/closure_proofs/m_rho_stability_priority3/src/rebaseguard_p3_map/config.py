"""Frozen Priority-3 configuration, loaded from the hashed map protocol."""

from __future__ import annotations

from pathlib import Path

from .common import read_json, sha256

CAMPAIGN = Path(__file__).resolve().parents[2]
ROOT = CAMPAIGN.parents[2]
CONFIGS = CAMPAIGN / "configs"
RESULTS = CAMPAIGN / "results"
FIGURES = CAMPAIGN / "figures"
PROTOCOL_PATH = CONFIGS / "MAP_PROTOCOL.json"

PROTOCOL = read_json(PROTOCOL_PATH)
PROTOCOL_SHA256 = sha256(PROTOCOL_PATH)

M_GRID: list[int] = [int(m) for m in PROTOCOL["m_grid"]]
RHO_GRID: list[float] = [float(r) for r in PROTOCOL["rho_grid"]]
LAYERS: list[dict] = PROTOCOL["layers"]
RHO_DOMAIN: tuple[float, float] = tuple(PROTOCOL["admissible_rho_domain"]["interval"])
BOUNDARY_TOLERANCE: float = float(PROTOCOL["classification"]["boundary_tolerance"])
Z95: float = float(PROTOCOL["uncertainty"]["z95"])
GATES: dict = PROTOCOL["gates"]
EVIDENCE_RANK: dict[str, int] = {
    row["class"]: int(row["rank"]) for row in PROTOCOL["evidence_hierarchy"]
}
