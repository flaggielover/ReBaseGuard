"""Deterministic successor partition generator (RULE RHO_CAP, r_max = 1/25).

INPUTS: the frozen SR cell table (p5y_k1_cover_ledger_successor/config/cells.json via spec.CELLS, whose sha256 must
equal the frozen checkpoint's geometry.cells_sha256) and the constants below. It reads NO T2-T5 record, verdict,
ratio or diagnostic, and no historical PASS/FAIL label.

RULE: for every frozen SR parent cell P (in frozen order), N(P) = the smallest N in {1, 2, 4, 8, ...} with
rho(P)/N <= R_MAX. P is split into N children of equal exact-rational width:
    left_k = L + k (R - L)/N,  right_k = L + (k+1)(R - L)/N,  e0_k = (left_k + right_k)/2,  rho_k = (R - L)/(2N).
C_upper(child) = C_upper(P) (a proved bound on ||(I-K_e)^-1|| for every e in P, hence in every child);
C_evaluation(child) = C_evaluation(P). The terminal parent keeps its exact affine c_SR encoding; its rho is compared
through its 256-bit outward UPPER bound (conservative: never fewer children).
OUTPUT: config/successor_cells.json, canonical ASCII JSON (sorted keys, compact separators, one LF).
"""
import hashlib
import json
from fractions import Fraction as F
from pathlib import Path

import sr_o9_candidates as T

NS = Path(__file__).resolve().parents[1]
R_MAX = F(1, 25)
DYADIC = (1, 2, 4, 8, 16, 32, 64)
SCHEMA = "rebaseguard.p5y.k1.sr.partition-successor.table.v1"
CELL_SCHEMA = "rebaseguard.p5y.k1.sr.partition-successor.cell.v1"
FROZEN_CELLS_SHA256 = "341eb5e95161bbdc2d15c1dca72eb8c4565982fab562e1c5a337139375b67c2f"


def canonical(o) -> bytes:
    return (json.dumps(o, sort_keys=True, separators=(",", ":"), ensure_ascii=True) + "\n").encode()


def enc(x: F) -> str:
    return f"{x.numerator}/{x.denominator}"


def rho_upper(cell):
    p, s = F(cell["rho"][0]), F(cell["rho"][1])
    if s == 0:
        return p
    from flint import arb
    with T.scientific_precision():
        _A, _b, c = T.sr_constants()
        v = (arb(p.numerator) / arb(p.denominator) + (arb(s.numerator) / arb(s.denominator)) * c).upper()
        m, e = v.man_exp()
        return F(int(m)) * F(2) ** int(e)


def generate():
    assert T.spec.CELLS_SHA256 == FROZEN_CELLS_SHA256, "frozen cell table moved"
    parents = sorted([c for c in T.spec.CELLS if c["detector"] == "SR"], key=lambda c: c["index"])
    assert len(parents) == 316 and [c["index"] for c in parents] == list(range(316))
    last = parents[-1]["index"]
    out = []
    for P in parents:
        ru = rho_upper(P)
        n = next(k for k in DYADIC if ru / k <= R_MAX)
        psha = hashlib.sha256(canonical(P)).hexdigest()
        if n == 1:
            kids = [(P["left"], P["right"], P["e0"], P["rho"])]
        else:
            if F(P["left"][1]) != 0 or F(P["right"][1]) != 0:
                raise RuntimeError("split of an affine (c_SR) cell is not defined by this protocol")
            L, R = F(P["left"][0]), F(P["right"][0])
            w = (R - L) / n
            kids = []
            for k in range(n):
                lo, hi = L + k * w, (L + (k + 1) * w if k < n - 1 else R)
                kids.append(([enc(lo), "0/1"], [enc(hi), "0/1"], [enc((lo + hi) / 2), "0/1"], [enc((hi - lo) / 2), "0/1"]))
        for k, (l, r, e0, rho) in enumerate(kids):
            out.append({"schema": CELL_SCHEMA, "detector": "SR", "index": len(out),
                        "id": f"PS1-SR-P{P['index']:03d}-N{n}-K{k}", "parent_index": P["index"], "children": n, "child": k,
                        "left": l, "right": r, "e0": e0, "rho": rho, "C_upper": P["C_upper"],
                        "C_evaluation": P["C_evaluation"], "parent_record_sha256": psha,
                        "terminal": P["index"] == last and k == n - 1})
    table = {"schema": SCHEMA, "rule": {"name": "RHO_CAP", "r_max": enc(R_MAX), "dyadic_ladder": list(DYADIC),
                                       "children": "equal exact-rational width", "C_upper": "inherited from parent",
                                       "terminal": "exact affine c_SR kept; rho compared by 256-bit outward upper bound"},
             "frozen_parent_cells_sha256": FROZEN_CELLS_SHA256, "n_cells": len(out), "cells": out}
    return table


def verify(table):
    """Exact tiling of [0, c_SR]: shared boundaries equal, identities exact, cap satisfied, terminal exception."""
    cells = table["cells"]
    assert [c["index"] for c in cells] == list(range(len(cells)))
    assert cells[0]["left"] == ["0/1", "0/1"] and cells[-1]["right"] == ["0/1", "1/1"]
    for a, b in zip(cells[:-1], cells[1:]):
        assert a["right"] == b["left"], (a["id"], b["id"])
    for c in cells:
        l, r = [F(x) for x in c["left"]], [F(x) for x in c["right"]]
        e0, rho = [F(x) for x in c["e0"]], [F(x) for x in c["rho"]]
        assert e0 == [(l[0] + r[0]) / 2, (l[1] + r[1]) / 2] and rho == [(r[0] - l[0]) / 2, (r[1] - l[1]) / 2]
        if not c["terminal"]:
            assert l[1] == 0 and r[1] == 0 and rho[0] > 0 and rho[0] <= R_MAX, c["id"]
        assert c["terminal"] == (c is cells[-1])
    parents = sorted({c["parent_index"] for c in cells})
    assert parents == list(range(316))
    return True


def main():
    t = generate()
    verify(t)
    b = canonical(t)
    (NS / "config/successor_cells.json").write_bytes(b)
    hist = {}
    for c in t["cells"]:
        if c["child"] == 0:
            hist[c["children"]] = hist.get(c["children"], 0) + 1
    print("n_cells", t["n_cells"], "sha256", hashlib.sha256(b).hexdigest(), "split histogram", dict(sorted(hist.items())),
          "old313", [c["id"] for c in t["cells"] if c["parent_index"] == 313], "terminal", t["cells"][-1]["id"])


if __name__ == "__main__":
    main()
