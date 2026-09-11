"""Successor identity / geometry layer (explicit wiring; no frozen module is modified or redirected).

The frozen T1 layer (sr_o9_candidates.validate_cell / cell_geometry / cell_identity) accepts only records that are
byte-identical to the FROZEN 316-cell table and binds the frozen table hash; that is correct for the frozen campaign
and is left untouched. This successor defines the same exact affine geometry for ITS OWN predeclared table:
records must be byte-identical to config/successor_cells.json (whose hash is fixed in the protocol), only the
terminal successor cell may carry a c_SR component, and e0 = (L+R)/2, rho = (R-L)/2 are checked at 256 bits.
"""
import hashlib
import json
from fractions import Fraction as F
from pathlib import Path

import sr_o9_candidates as T
from flint import arb

NS = Path(__file__).resolve().parents[1]
TABLE = NS / "config/successor_cells.json"


class SuccessorCellRefused(RuntimeError):
    pass


def canonical(o) -> bytes:
    return (json.dumps(o, sort_keys=True, separators=(",", ":"), ensure_ascii=True) + "\n").encode()


def table_bytes() -> bytes:
    return TABLE.read_bytes()


def table_sha256() -> str:
    return hashlib.sha256(table_bytes()).hexdigest()


def cells() -> list:
    return json.loads(table_bytes())["cells"]


def cell(index: int) -> dict:
    hits = [c for c in cells() if c["index"] == index]
    if isinstance(index, bool) or not isinstance(index, int) or len(hits) != 1:
        raise SuccessorCellRefused(f"no unique successor cell {index!r}")
    return json.loads(json.dumps(hits[0]))


def cells_of_parent(parent_index: int) -> list:
    return [c for c in cells() if c["parent_index"] == parent_index]


def validate(rec: dict) -> dict:
    if canonical(rec) != canonical(cell(rec.get("index"))):
        raise SuccessorCellRefused(f"successor cell {rec.get('index')} differs from the predeclared table")
    for field in ("left", "right", "e0", "rho", "C_evaluation"):
        pair = rec[field]
        if not (isinstance(pair, list) and len(pair) == 2 and all(isinstance(s, str) for s in pair)):
            raise SuccessorCellRefused(f"{field}: affine [p, s] pair required")
        if F(pair[1]) != 0 and not (rec["terminal"] and field in ("right", "e0", "rho")):
            raise SuccessorCellRefused(f"{field}: c_SR component only on the terminal successor cell")
    if rec["terminal"] and [F(x) for x in rec["right"]] != [F(0), F(1)]:
        raise SuccessorCellRefused("terminal right endpoint must be exactly c_SR")
    return rec


def geometry(rec: dict) -> dict:
    """Same exact affine geometry as the frozen T1 cell_geometry, validated against the successor table."""
    T.require_precision()
    validate(rec)
    A, b, c = T.sr_constants()
    L, R = T.affine(rec["left"], c), T.affine(rec["right"], c)
    e0, rho = T.affine(rec["e0"], c), T.affine(rec["rho"], c)
    tol = arb(2) ** -(T.FROZEN_BITS - 8)
    if not (e0 - (L + R) / arb(2)).abs_upper() < tol:
        raise SuccessorCellRefused("e0 != (left+right)/2")
    if not (rho - (R - L) / arb(2)).abs_upper() < tol:
        raise SuccessorCellRefused("rho != (right-left)/2")
    if not (rho > 0 and R > L):
        raise SuccessorCellRefused("degenerate cell")
    return {"A": A, "b": b, "c": c, "left": L, "right": R, "e0": e0, "rho": rho}


def identity(rec: dict) -> dict:
    return {"detector": "SR", "successor": "PS1", "index": rec["index"], "id": rec["id"], "parent_index": rec["parent_index"],
            "children": rec["children"], "child": rec["child"], "left": rec["left"], "right": rec["right"], "e0": rec["e0"],
            "rho": rec["rho"], "C_upper": rec["C_upper"], "C_evaluation": rec["C_evaluation"],
            "parent_record_sha256": rec["parent_record_sha256"], "successor_cells_sha256": table_sha256(),
            "frozen_cells_sha256": T.spec.CELLS_SHA256, "checkpoint_sha256": T.spec.CHECKPOINT_SHA256}
