"""K4 (H2 on (0, 2]) mechanical ASSEMBLY over K1 production cell records. Issues NO verdict.

Implements exactly config/K4_ASSEMBLY_PREDECLARATION.json:

  R_cell      = [R.lo - rho*mag(D) - rho^2*M/2 , R.hi + rho*mag(D) + rho^2*M/2]   (frozen ledger.taylor_enclosure)
  Rprime_cell = [D.lo - rho*M , D.hi + rho*M]                                         (mean value, |R''| <= M = M_R2)

  cover from e = 0, contiguous, to >= 2  ->  maximal prefix chain with Rprime_cell.hi < 0 (R(0) = 0 exact, P5-T3)
  -> every other cell needs R_cell.hi < 0;  R.lo > 0 is a certified counterexample; anything else is too loose.

Exact rational arithmetic over the recorded outward endpoints; no floating point anywhere in a decision.

GENUINE mode (production records) is LOCKED until config/K4_ASSEMBLY_CHECKPOINT_HASH exists and equals the sha256 of
the predeclaration. Until then only --synthetic fixtures are accepted.

  python k4_assembly.py --synthetic --records DIR --out OUT.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from fractions import Fraction as F
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
PREDECL = NS / "config/K4_ASSEMBLY_PREDECLARATION.json"
CHECKPOINT_HASH = NS / "config/K4_ASSEMBLY_CHECKPOINT_HASH"
E_CAP = F(2)
M_SCOPE = ("1", "2", "3", "5")
DETECTORS = ("CUSUM", "SR")


class AssemblyRefusal(RuntimeError):
    """Input or mode not admissible. Never a scientific outcome."""


def fr(s) -> F:
    if isinstance(s, float):
        raise AssemblyRefusal("floating-point value in a certified field")
    return F(s)


def t4_canonical(o) -> bytes:
    """Byte-identical to p5y_k1_sr_o9_t345_successor/code/t4_cell.canonical."""
    return (json.dumps(o, sort_keys=True, separators=(",", ":"), ensure_ascii=True, default=str) + "\n").encode()


def verify_sr_t4_integrity(rec: dict) -> None:
    body = {k: v for k, v in rec.items() if k != "t4_record_sha256"}
    if hashlib.sha256(t4_canonical(body)).hexdigest() != rec.get("t4_record_sha256"):
        raise AssemblyRefusal(f"t4_record_sha256 mismatch for cell {rec.get('cell')}")


def geometry(rec: dict) -> tuple[F, F, F, F]:
    e0, rho = rec["e0"], rec["rho"]
    if fr(e0[1]) != 0 or fr(rho[1]) != 0:
        raise AssemblyRefusal(f"symbolic (c_SR-dependent) cell {rec.get('cell', rec.get('cell_index'))} inside the K4 domain")
    e0f, rhof = fr(e0[0]), fr(rho[0])
    if rhof <= 0:
        raise AssemblyRefusal("non-positive cell radius")
    return e0f - rhof, e0f + rhof, e0f, rhof


def cell_enclosures(entry: dict, rho: F) -> dict:
    R = (fr(entry["R_interval"]["lo"]), fr(entry["R_interval"]["hi"]))
    D = (fr(entry["D_interval"]["lo"]), fr(entry["D_interval"]["hi"]))
    M = fr(entry["M_R2"])
    if R[0] > R[1] or D[0] > D[1] or M < 0:
        raise AssemblyRefusal("malformed interval (lo > hi) or negative curvature bound")
    magD = max(abs(D[0]), abs(D[1]))
    rem = rho * magD + rho * rho * M / 2
    return {"R_mid": R, "R_cell": (R[0] - rem, R[1] + rem), "Rprime_cell": (D[0] - rho * M, D[1] + rho * M)}


def assemble_Dm(cells: list[dict]) -> dict:
    """cells: [{'index','left','right','rho','entry'}] for ONE (D, m), every cell meeting (0, 2]."""
    cells = sorted(cells, key=lambda c: c["left"])
    out = {"cells": len(cells), "per_cell": []}
    gap = (not cells or cells[0]["left"] != 0 or cells[-1]["right"] < E_CAP
           or any(a["right"] != b["left"] for a, b in zip(cells, cells[1:])))
    if gap:
        out["outcome"] = "K4_COVER_GAP"
        return out
    chain_end, in_chain = F(0), True
    counter, loose = [], []
    for c in cells:
        enc = cell_enclosures(c["entry"], c["rho"])
        if in_chain and enc["Rprime_cell"][1] < 0:
            how = "CHAIN_RPRIME_NEGATIVE"
            chain_end = c["right"]
        else:
            in_chain = False
            if enc["R_mid"][0] > 0:
                how = "MATHEMATICAL_COUNTEREXAMPLE"
                counter.append(c["index"])
            elif enc["R_cell"][1] < 0:
                how = "DIRECT_R_NEGATIVE"
            else:
                how = "CERTIFICATE_TOO_LOOSE"
                loose.append(c["index"])
        out["per_cell"].append({"index": c["index"], "left": str(c["left"]), "right": str(c["right"]), "how": how,
                                "R_cell_hi": str(enc["R_cell"][1]), "Rprime_cell_hi": str(enc["Rprime_cell"][1])})
    out["chain_certifies_up_to"] = str(chain_end)
    out["outcome"] = ("K4_MATHEMATICAL_COUNTEREXAMPLE" if counter else
                      "K4_CERTIFICATE_TOO_LOOSE" if loose else "K4_CELLWISE_ALL_CERTIFIED")
    out["counterexample_cells"], out["too_loose_cells"] = counter, loose
    return out


def collect(records: list[dict], *, verify_sr_integrity: bool) -> dict:
    """Group per (D, m) the cells whose closed interval meets (0, 2]."""
    groups = {(d, m): [] for d in DETECTORS for m in M_SCOPE}
    seen = set()
    for rec in records:
        idx = rec.get("cell", rec.get("cell_index"))
        det = {v.get("detector") for v in rec["m"].values()}
        if len(det) != 1 or next(iter(det)) not in DETECTORS:
            raise AssemblyRefusal(f"cell {idx}: detector identity missing or inconsistent")
        det = det.pop()
        if det == "SR" and verify_sr_integrity:
            verify_sr_t4_integrity(rec)
        left, right, _e0, rho = geometry(rec)
        if not (left <= E_CAP and right > 0):
            continue
        if (det, idx) in seen:
            raise AssemblyRefusal(f"duplicate record for {det} cell {idx}")
        seen.add((det, idx))
        if set(rec["m"]) != set(M_SCOPE):
            raise AssemblyRefusal(f"{det} cell {idx}: m scope {sorted(rec['m'])} != {list(M_SCOPE)}")
        for m in M_SCOPE:
            groups[(det, m)].append({"index": idx, "left": left, "right": right, "rho": rho, "entry": rec["m"][m]})
    return groups


def assemble(records: list[dict], *, verify_sr_integrity: bool = True) -> dict:
    groups = collect(records, verify_sr_integrity=verify_sr_integrity)
    per = {}
    for (d, m), cells in groups.items():
        per[f"{d}|m={m}"] = assemble_Dm(cells) if cells else {"cells": 0, "outcome": "K4_SCOPE_INCOMPLETE"}
    return {"schema": "rebaseguard.p5y.k4.assembly-report.v1", "verdict_issued": False,
            "predeclaration_sha256": hashlib.sha256(PREDECL.read_bytes()).hexdigest(),
            "domain": "(0, 2]", "arithmetic": "exact rational", "per_Dm": per,
            "all_eight_cellwise_certified": all(v["outcome"] == "K4_CELLWISE_ALL_CERTIFIED" for v in per.values()),
            "note": "mechanical assembly report; a K4 verdict requires a frozen checkpoint and independent adjudication"}


def genuine_mode_allowed() -> bool:
    return CHECKPOINT_HASH.exists() and \
        CHECKPOINT_HASH.read_text().strip() == hashlib.sha256(PREDECL.read_bytes()).hexdigest()


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--records", required=True, help="directory of per-cell JSON records")
    ap.add_argument("--synthetic", action="store_true", help="synthetic fixtures only")
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    recs = [json.loads(p.read_text()) for p in sorted(Path(a.records).glob("*.json"))]
    if a.synthetic:
        if any(not r.get("SYNTHETIC_FIXTURE_NOT_SCIENCE") for r in recs):
            raise AssemblyRefusal("--synthetic accepts only records stamped SYNTHETIC_FIXTURE_NOT_SCIENCE")
    elif not genuine_mode_allowed():
        raise AssemblyRefusal("GENUINE mode locked: K4 assembly predeclaration is not frozen "
                              "(config/K4_ASSEMBLY_CHECKPOINT_HASH absent or mismatched)")
    rep = assemble(recs, verify_sr_integrity=True)
    rep["mode"] = "SYNTHETIC" if a.synthetic else "GENUINE"
    Path(a.out).write_text(json.dumps(rep, indent=1, sort_keys=True) + "\n")
    print(json.dumps({k: rep[k] for k in ("mode", "all_eight_cellwise_certified", "verdict_issued")}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
