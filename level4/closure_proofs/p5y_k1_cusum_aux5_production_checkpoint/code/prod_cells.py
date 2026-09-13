"""The frozen 326-cell CUSUM cover geometry, read from the hash-verified frozen K1 table. NON-CERTIFYING.

The per-cell (e0, rho, left, right, C_upper) and the m scope are never re-derived: they are read from
`p5y_k1_cover_ledger_successor/config/cells.json` after its sha256 matches the frozen K1 table.
"""
from __future__ import annotations

import json
from fractions import Fraction as F

from prod_common import ROOT, Refusal, canonical, sha256_bytes, sha256_file

CELLS_REL = "level4/closure_proofs/p5y_k1_cover_ledger_successor/config/cells.json"
CELLS_SHA256 = "341eb5e95161bbdc2d15c1dca72eb8c4565982fab562e1c5a337139375b67c2f"
N_CELLS = 326
M_VALUES = ("1", "2", "3", "5")
GEOMETRY_FIELDS = ("index", "e0", "rho", "left", "right", "C_upper")
K4_E_CAP = F(2)


def cusum_cells() -> dict:
    path = ROOT / CELLS_REL
    if sha256_file(path) != CELLS_SHA256:
        raise Refusal("FROZEN_GEOMETRY_MUTATED", f"{CELLS_REL} sha256 differs from the frozen K1 table")
    cells = sorted((c for c in json.loads(path.read_text()) if c["detector"] == "CUSUM"),
                   key=lambda c: c["index"])
    if [c["index"] for c in cells] != list(range(N_CELLS)):
        raise Refusal("FROZEN_GEOMETRY_MUTATED", "CUSUM indices are not exactly 0..325")
    return {c["index"]: {k: c[k] for k in GEOMETRY_FIELDS} for c in cells}


def geometry_digest(cells: dict) -> str:
    return sha256_bytes(canonical([cells[i] for i in sorted(cells)]))


def _exact(pair):
    return F(pair[0]) if F(pair[1]) == 0 else None


def cover_facts(cells: dict) -> dict:
    """Structural facts of the frozen cover. Geometry only; no certified value is read."""
    rows = [cells[i] for i in sorted(cells)]
    exact = all(_exact(c[f]) is not None for c in rows for f in ("e0", "rho", "left", "right"))
    half_width = exact and all(_exact(c["e0"]) - _exact(c["rho"]) == _exact(c["left"])
                               and _exact(c["e0"]) + _exact(c["rho"]) == _exact(c["right"]) for c in rows)
    k4 = [c["index"] for c in rows if exact and _exact(c["left"]) < K4_E_CAP and _exact(c["right"]) > 0]
    return {"cells": len(rows), "first_index": rows[0]["index"], "last_index": rows[-1]["index"],
            "contiguous": all(a["right"] == b["left"] for a, b in zip(rows, rows[1:])),
            "cover_left": rows[0]["left"], "cover_right": rows[-1]["right"],
            "all_endpoints_exact_non_symbolic": exact,
            "e0_minus_rho_is_left_and_e0_plus_rho_is_right": half_width,
            "m_values": list(M_VALUES),
            "k4_domain": {"predicate": "left < 2 and right > 0 (exact, non-symbolic)", "cells": len(k4),
                          "first_index": k4[0] if k4 else None, "last_index": k4[-1] if k4 else None,
                          "indices_contiguous": bool(k4) and k4 == list(range(k4[0], k4[-1] + 1)),
                          "last_right": cells[k4[-1]]["right"] if k4 else None}}
