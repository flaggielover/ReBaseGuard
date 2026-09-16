"""K5 order-3 minimality scan: which cells does Theorem K5-B still need a certified R''' bound for?

READ-ONLY, RESULT-AGNOSTIC, NON-CERTIFYING. This evaluates the frozen recurrences of
`p5y_k5_feasibility/K5_GLOBAL_BRIDGE.md` (Theorem K5-B) on ALREADY CERTIFIED K1 cell records, with no order-3
evidence at all (`L_k = -inf`). It runs no scientific computation, produces no certified object, authorizes
nothing, and touches no production runtime. Its only output is a bookkeeping answer: on which cells the existing
K1 enclosures already discharge the theorem, and on which they cannot.

Theorem K5-B, cells `C_k = [x_{k-1}, x_k]` with half-width `rho_k` and midpoint `e0_k`, `l_0 = 0`, `gamma_0 = 0`:

    mu_k    = max(H_k.lo, l_{k-1} + min(0, 2 rho_k L_k))          L_k = -inf  =>  mu_k = H_k.lo
    l_k     = max(H_k.lo, l_{k-1} + 2 rho_k L_k)                  L_k = -inf  =>  l_k  = H_k.lo
    Gamma_k = hi(R_k - e0_k D_k) + rho_k x_k M_k                  (K1-only direct bound on sup_{C_k} g)
    U_k     = max(gamma_{k-1}, gamma_{k-1} - mu_k (x_k^2 - x_{k-1}^2) / 2)
    gamma_k = min(gamma_{k-1} - mu_k (x_k^2 - x_{k-1}^2) / 2, Gamma_k)

    pass(k) <=> (k = 1 and L_1 > 0) or (k >= 2 and U_k < 0) or (Gamma_k < 0)

with `g(e) = R(e) - e R'(e)`, `H_k = R2_interval` (whole-cell R'' enclosure) and `M_k = M_R2 = mag(H_k)`.
`R_k`, `D_k` are the certified midpoint enclosures of `R(e0_k)`, `R'(e0_k)`. All arithmetic is exact rational; the
interval endpoints are read as the outward exact rationals the K1 records export.

A cell reported as NEEDS_ORDER3 is one that no part of the frozen theorem can discharge from K1 records alone. A
cell reported as CLOSED_BY_K1 needs no order-3 evidence under this theorem, whatever a future R''' campaign finds.

  python -B code/k5_minimality.py scan --records DIR --cells CELLS.json --detector CUSUM --out EVIDENCE.json
  python -B code/k5_minimality.py verify --evidence EVIDENCE.json [--records DIR --cells CELLS.json]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from fractions import Fraction as F
from pathlib import Path

SCHEMA = "rebaseguard.p5y.k5.order3-readiness.minimality-scan.v1"
MS = ("1", "2", "3", "5")
DOMAIN_RIGHT = F(2)


def rat(p) -> F:
    """A K1 exact-rational field: either a string 'p/q' or a two-element exact pair."""
    return F(p) if isinstance(p, str) else F(p[0]) + F(p[1])


def sha256_file(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_cells(cells_json: Path, detector: str) -> list[dict]:
    cells = [c for c in json.loads(Path(cells_json).read_bytes()) if c["detector"] == detector]
    cells.sort(key=lambda c: c["index"])
    if [c["index"] for c in cells] != list(range(len(cells))):
        raise SystemExit("cell indices are not contiguous from 0")
    if rat(cells[0]["left"]) != 0:
        raise SystemExit("the cover does not start at x_0 = 0 exactly")
    for a, b in zip(cells, cells[1:]):
        if rat(a["right"]) != rat(b["left"]):
            raise SystemExit(f"cover gap between cells {a['index']} and {b['index']}")
    return [c for c in cells if rat(c["left"]) < DOMAIN_RIGHT]            # cells meeting (0,2]


def record_path(records: Path, detector: str, index: int) -> Path:
    stem = {"CUSUM": "aux5_CUSUM"}.get(detector, detector)
    return Path(records) / f"{stem}_{index}_256.json"


def scan(records: Path, cells_json: Path, detector: str, ms=MS) -> dict:
    cells = load_cells(cells_json, detector)
    per_m: dict[str, dict] = {}
    for m in ms:
        gamma = F(0)
        needs, closed, rows, r2_lo_positive = [], [], [], []
        for c in cells:
            k = c["index"]
            rec = json.loads(record_path(records, detector, k).read_bytes())
            if rec.get("cell_index") != k or rec.get("detector") != detector:
                raise SystemExit(f"record {k} does not identify itself as {detector} cell {k}")
            r = rec["m"][m]
            x_lo, x_hi, rho, e0 = rat(c["left"]), rat(c["right"]), rat(c["rho"]), rat(c["e0"])
            if rat(r["e0"]) != e0 or rat(r["rho"]) != rho:
                raise SystemExit(f"record {k} geometry does not match the frozen cover")
            H_lo = F(r["R2_interval"]["lo"])
            M = F(r["M_R2"])
            if H_lo > 0:
                r2_lo_positive.append(k)
            g_mid_hi = F(r["R_interval"]["hi"]) - e0 * F(r["D_interval"]["lo"])
            Gamma = g_mid_hi + rho * x_hi * M
            mu = H_lo                                                  # L_k = -inf
            step = -mu * (x_hi ** 2 - x_lo ** 2) / 2
            U = max(gamma, gamma + step)
            passed = (Gamma < 0) or (k > 0 and U < 0)
            (closed if passed else needs).append(k)
            rows.append({"cell": k, "H_lo": str(H_lo), "M_R2": str(M), "Gamma": str(Gamma),
                         "U": str(U), "gamma_before": str(gamma), "pass": passed,
                         "pass_direct": Gamma < 0, "pass_chain": bool(k > 0 and U < 0)})
            gamma = min(gamma + step, Gamma)
        per_m[m] = {"needs_order3": ranges(needs), "needs_order3_count": len(needs),
                    "closed_by_k1": ranges(closed), "closed_by_k1_count": len(closed),
                    "first_closed_cell": (closed[0] if closed else None),
                    "cells_with_R2_interval_lo_positive": ranges(r2_lo_positive),
                    "cells_with_R2_interval_lo_positive_count": len(r2_lo_positive),
                    "boundary_rows": boundary_rows(rows)}
    union_needs = sorted({k for m in ms for k in expand(per_m[m]["needs_order3"])})
    union_closed = [c["index"] for c in cells if c["index"] not in set(union_needs)]
    return {"schema": SCHEMA, "detector": detector, "domain": "(0,2]",
            "cells_meeting_domain": len(cells), "universe": [cells[0]["index"], cells[-1]["index"]],
            "m_values": list(ms),
            "inputs": {"cells_json_sha256": sha256_file(cells_json),
                       "records_dir": str(records),
                       "record_count": len(cells)},
            "per_m": per_m,
            "union_needs_order3": ranges(union_needs),
            "union_needs_order3_count": len(union_needs),
            "provably_not_needed": ranges(union_closed),
            "provably_not_needed_count": len(union_closed),
            "interpretation": (
                "NEEDS_ORDER3 = the frozen Theorem K5-B cannot discharge this cell from K1 records alone "
                "(L_k = -inf). PROVABLY_NOT_NEEDED = the direct bound Gamma_k < 0, or the gamma chain, already "
                "discharges it for every m, so no order-3 evidence on that cell can be required by this theorem. "
                "This is a scope result about the theorem, not a claim about H3a or about R''' itself.")}


def ranges(xs: list[int]) -> list[list[int]]:
    out: list[list[int]] = []
    for x in sorted(xs):
        if out and x == out[-1][1] + 1:
            out[-1][1] = x
        else:
            out.append([x, x])
    return out


def expand(rs: list[list[int]]) -> list[int]:
    return [x for a, b in rs for x in range(a, b + 1)]


def boundary_rows(rows: list[dict]) -> list[dict]:
    """The rows where pass/fail changes, with one row of context on each side."""
    keep: set[int] = set()
    for i, r in enumerate(rows):
        if i and r["pass"] != rows[i - 1]["pass"]:
            keep |= {i - 2, i - 1, i, i + 1}
    return [rows[i] for i in sorted(x for x in keep if 0 <= x < len(rows))]


def verify(evidence: Path, records: Path | None, cells_json: Path | None) -> list[str]:
    ev = json.loads(Path(evidence).read_bytes())
    problems: list[str] = []
    if ev.get("schema") != SCHEMA:
        return [f"WRONG_SCHEMA: {ev.get('schema')}"]
    n = ev["cells_meeting_domain"]
    lo, hi = ev["universe"]
    if hi - lo + 1 != n:
        problems.append("UNIVERSE_DOES_NOT_MATCH_CELL_COUNT")
    for m, v in ev["per_m"].items():
        cells = expand(v["needs_order3"]) + expand(v["closed_by_k1"])
        if sorted(cells) != list(range(lo, hi + 1)):
            problems.append(f"m={m}: needs/closed do not partition the universe")
        if len(expand(v["needs_order3"])) != v["needs_order3_count"]:
            problems.append(f"m={m}: needs_order3_count disagrees with the ranges")
    union = set(expand(ev["union_needs_order3"]))
    if union != {k for v in ev["per_m"].values() for k in expand(v["needs_order3"])}:
        problems.append("UNION_IS_NOT_THE_UNION_OF_THE_PER_M_SETS")
    if set(expand(ev["provably_not_needed"])) & union:
        problems.append("PROVABLY_NOT_NEEDED_OVERLAPS_THE_UNION")
    if records and cells_json:
        again = scan(Path(records), Path(cells_json), ev["detector"], tuple(ev["m_values"]))
        if json.dumps(again, sort_keys=True) != json.dumps({**ev, "inputs": again["inputs"]}, sort_keys=True):
            problems.append("SCAN_DOES_NOT_REPRODUCE_FROM_THE_RECORDS")
    return problems


def main() -> int:
    ap = argparse.ArgumentParser(description="K5 order-3 minimality scan (read-only)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("scan")
    s.add_argument("--records", required=True)
    s.add_argument("--cells", required=True)
    s.add_argument("--detector", default="CUSUM")
    s.add_argument("--out", required=True)
    v = sub.add_parser("verify")
    v.add_argument("--evidence", required=True)
    v.add_argument("--records")
    v.add_argument("--cells")
    a = ap.parse_args()
    if a.cmd == "scan":
        rep = scan(Path(a.records), Path(a.cells), a.detector)
        Path(a.out).write_text(json.dumps(rep, indent=1, sort_keys=True) + "\n")
        print(json.dumps({k: rep[k] for k in ("detector", "cells_meeting_domain", "union_needs_order3",
                                              "union_needs_order3_count", "provably_not_needed_count")}, indent=1))
        return 0
    problems = verify(Path(a.evidence), Path(a.records) if a.records else None,
                      Path(a.cells) if a.cells else None)
    print(json.dumps({"MINIMALITY_SCAN_VALID": not problems, "problems": problems}, indent=1))
    return 0 if not problems else 1


if __name__ == "__main__":
    sys.exit(main())
