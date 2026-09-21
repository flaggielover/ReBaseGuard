"""The frozen C3 mechanism: operator-level componentwise-best supply, then A-level componentwise minimum.

Implements config/FEASIBILITY_GATES_C3.json section `mechanism` and nothing else. Every refusal the gate names is
enforced here, not assumed:

  * a component may only be taken from a source that certifies it uniformly on the WHOLE cell;
  * the MIXED tuple must satisfy the Lemma Dv' premises in its own right, checked by the pinned
    `deflated_consume.atom_constants_r2`, which raises rather than returning constants for an inadmissible tuple;
  * a cell whose mixed tuple fails a premise falls back to the best single source and is flagged;
  * ties resolve to the lexicographically first source name and are recorded in provenance;
  * order3 is None everywhere - C3 proposes no candidate of F.

This module computes; it does not decide. Classification against the frozen gate lives in c3_forecast.py.
"""
import hashlib
import json
import sys
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve()
NS = HERE.parents[1]
CP = HERE.parents[2]
C2 = CP / "p5y_k5_tail_c2_closure"
GATE_SHA = "f0bd87ecaeea4485560969770c95c9d4ad20bceedf9ac7ca11fb6d8d5de53ac7"

OPERATOR_UPPER = ("tau", "C_T", "D1", "D2", "Abar")   # smaller is tighter
OPERATOR_LOWER = ("D_lo",)                            # larger is tighter
FIELDS = ("A0", "A1", "A2")


def sha(p) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def frozen_gate() -> dict:
    p = NS / "config/FEASIBILITY_GATES_C3.json"
    if sha(p) != GATE_SHA:
        raise SystemExit("the C3 gate is not the frozen one")
    return json.loads(p.read_bytes())


def whole_cell_ok(src_name: str, block: dict, cover: dict, rat) -> bool:
    """Every component must be certified uniformly on [e0-rho, e0+rho]. Checked, not assumed."""
    e0, rho = rat(cover["e0"]), rat(cover["rho"])
    lo, hi = e0 - rho, e0 + rho
    if "sub_rows" in block:                       # C2: sub-blocks must tile the cell exactly
        rows = sorted(block["sub_rows"], key=lambda r: F(r["e_lo"]))
        if F(rows[0]["e_lo"]) != lo or F(rows[-1]["e_hi"]) != hi:
            return False
        for i, r in enumerate(rows):
            if i + 1 < len(rows) and F(r["e_hi"]) != F(rows[i + 1]["e_lo"]):
                return False
        return True
    return F(str(block["e_lo"])) == lo and F(str(block["e_hi"])) == hi


def operator_best(sources: dict) -> tuple:
    """Componentwise best over sources, with per-field provenance and deterministic tie resolution."""
    tup, prov = {}, {}
    for fld in OPERATOR_UPPER:
        cand = sorted(((F(str(b[fld])), n) for n, b in sources.items()), key=lambda vn: (vn[0], vn[1]))
        tup[fld], prov[fld] = cand[0]
    for fld in OPERATOR_LOWER:
        cand = sorted(((F(str(b[fld])), n) for n, b in sources.items()), key=lambda vn: (-vn[0], vn[1]))
        tup[fld], prov[fld] = cand[0]
    return tup, prov


def combine_A(supplies: dict) -> tuple:
    """A-level componentwise minimum with per-field provenance; ties to the lexicographically first name."""
    A, prov = {}, {}
    for j in FIELDS:
        cand = sorted(((s[j], n) for n, s in supplies.items()), key=lambda vn: (vn[0], vn[1]))
        A[j], prov[j] = cand[0]
    return A, prov


def build(cell: int, c1b: dict, c2b: dict, cover: dict, meas: dict, DC, T, rat) -> dict:
    """The full C3 supply for one cell, with every gate-mandated refusal enforced."""
    sources = {"C1": c1b, "C2": c2b}
    rejected = {n: "not certified uniformly on the whole cell"
                for n, b in sources.items() if not whole_cell_ok(n, b, cover, rat)}
    usable = {n: b for n, b in sources.items() if n not in rejected}
    if not usable:
        raise SystemExit(f"cell {cell}: no source is whole-cell valid")

    tup, op_prov = operator_best(usable)

    # Lemma Dv' premises are enforced on the MIXED tuple by the pinned consumer, which raises on failure.
    fallback = None
    try:
        mixed = DC.atom_constants_r2(*(tup[x] for x in ("Abar", "tau", "C_T", "D_lo", "D1", "D2")))
    except Exception as exc:
        fallback = f"mixed tuple violates a Lemma Dv' premise ({type(exc).__name__}); falling back"
        mixed = None

    kn = {i: F(meas["norms"]["k"][i]) for i in range(5)}
    supplies = {"G": T.atom_constants_generic(F(meas["C_upper"]), kn[1], kn[2])}
    for n, b in usable.items():
        # A source whose OWN constants violate a Lemma Dv' premise is rejected like a non-covering one, rather
        # than propagating. Propagating would make the mixed-tuple guard unobservable: both the correct code and
        # a mutant that swallows the guard would refuse identically, for the wrong reason.
        try:
            supplies[n] = DC.atom_constants_r2(*(F(str(b[x])) for x in ("Abar", "tau", "C_T", "D_lo", "D1", "D2")))
        except Exception as exc:
            rejected[n] = f"source violates a Lemma Dv' premise ({type(exc).__name__})"
    if mixed is not None:
        supplies["operator_mixed"] = mixed

    A, prov = combine_A(supplies)
    return {"cell": cell, "operator_tuple": {k: str(v) for k, v in tup.items()},
            "operator_provenance": op_prov, "rejected_sources": rejected,
            "premise_fallback": fallback,
            "supplies": {n: {j: str(s[j]) for j in FIELDS} for n, s in supplies.items()},
            "A": A, "A_provenance": prov}
