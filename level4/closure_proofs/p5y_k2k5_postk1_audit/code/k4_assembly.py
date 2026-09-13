"""K4 (H2 on (0, 2]) mechanical ASSEMBLY over K1 production cell records. Issues NO verdict.

Authoritative specification: config/K4_ASSEMBLY_CHECKPOINT.json, bound by config/K4_ASSEMBLY_CHECKPOINT_HASH
(the history record config/K4_ASSEMBLY_PREDECLARATION.json is kept byte-unchanged).

  R_cell      = [R.lo - rho*mag(D) - rho^2*M/2 , R.hi + rho*mag(D) + rho^2*M/2]   (frozen ledger.taylor_enclosure)
  Rprime_cell = [D.lo - rho*M , D.hi + rho*M]                                         (mean value, |R''| <= M = M_R2)

  domain cells: frozen cover cells with left < 2 and right > 0; cover contiguous from exactly 0 to >= 2
  -> maximal prefix chain with Rprime_cell.hi < 0 (R(0) = 0 exact, P5-T3)
  -> every other cell needs R_cell.hi < 0;  R.lo > 0 is a certified counterexample; anything else is too loose.

Exact rational arithmetic over the recorded outward endpoints; no floating point in any decision.

GENUINE mode requires: the frozen checkpoint (hash-bound, source hashes of this file / its tests / the predeclaration
equal to the checkpoint), SR sealed production cell records re-verified by hash, the Lane C integrity audit
reporting INTEGRITY_READY_FOR_ADJUDICATION and a complete 369-cell record, and a CUSUM integrity attestation.

  python k4_assembly.py --synthetic --records DIR --out OUT.json
  python k4_assembly.py --sr-sealed-cells DIR --sr-integrity-audit ADJ.json \
                        --cusum-records DIR --cusum-attestation ATT.json --out OUT.json
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
CHECKPOINT = NS / "config/K4_ASSEMBLY_CHECKPOINT.json"
CHECKPOINT_HASH = NS / "config/K4_ASSEMBLY_CHECKPOINT_HASH"
BOUND_SOURCES = ("code/k4_assembly.py", "tests/test_k4_assembly.py", "config/K4_ASSEMBLY_PREDECLARATION.json")
E_CAP = F(2)
M_SCOPE = ("1", "2", "3", "5")
DETECTORS = ("CUSUM", "SR")
CUSUM_ATTESTATION_SCHEMA = "rebaseguard.p5y.k1.cusum-production.integrity-attestation.v1"


class AssemblyRefusal(RuntimeError):
    """Input or mode not admissible. Never a scientific outcome."""


def sha_file(p) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


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
    symbolic = fr(e0[1]) != 0 or fr(rho[1]) != 0
    if symbolic:
        return None                       # c_SR-dependent terminal cell: never meets (0, 2]; refused if forced in
    e0f, rhof = fr(e0[0]), fr(rho[0])
    if rhof <= 0:
        raise AssemblyRefusal("non-positive cell radius")
    return e0f - rhof, e0f + rhof, e0f, rhof


def in_domain(left: F, right: F) -> bool:
    return left < E_CAP and right > 0


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
    """cells: [{'index','left','right','rho','entry'}] for ONE (D, m), every domain cell."""
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
        geo = geometry(rec)
        if geo is None:
            continue
        left, right, _e0, rho = geo
        if not in_domain(left, right):
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
    per = {f"{d}|m={m}": (assemble_Dm(c) if c else {"cells": 0, "outcome": "K4_SCOPE_INCOMPLETE"})
           for (d, m), c in groups.items()}
    return {"schema": "rebaseguard.p5y.k4.assembly-report.v2", "verdict_issued": False,
            "checkpoint_sha256": sha_file(CHECKPOINT) if CHECKPOINT.exists() else None,
            "domain": "(0, 2]", "arithmetic": "exact rational", "per_Dm": per,
            "all_eight_cellwise_certified": all(v["outcome"] == "K4_CELLWISE_ALL_CERTIFIED" for v in per.values()),
            "note": "mechanical assembly report; the K4 disposition is issued only by independent adjudication "
                    "applying the frozen outcome mapping of the checkpoint"}


# ------------------------------------------------------------------ genuine-mode gates
def genuine_mode_allowed() -> bool:
    if not (CHECKPOINT.exists() and CHECKPOINT_HASH.exists()):
        return False
    if CHECKPOINT_HASH.read_text().strip() != sha_file(CHECKPOINT):
        return False
    bound = json.loads(CHECKPOINT.read_text()).get("bound_sources", {})
    return set(bound) == set(BOUND_SOURCES) and all(sha_file(NS / r) == h for r, h in bound.items())


def load_sr_sealed(sealed_dir: Path) -> list[dict]:
    """SR T4 records reached ONLY through sealed production cell records, each re-verified by hash."""
    out = []
    for p in sorted(Path(sealed_dir).glob("[0-9][0-9][0-9][0-9].json")):
        sealed = json.loads(p.read_text())
        ev = (sealed.get("evidence") or {}).get("t4")
        if not ev or not Path(ev["path"]).exists() or sha_file(ev["path"]) != ev["sha256"]:
            raise AssemblyRefusal(f"sealed cell {p.name}: T4 evidence missing or hash drift")
        t4 = json.loads(Path(ev["path"]).read_text())
        if t4.get("cell") != sealed.get("cell_id"):
            raise AssemblyRefusal(f"sealed cell {p.name}: T4 cell identity mismatch")
        verify_sr_t4_integrity(t4)
        out.append(t4)
    return out


def check_sr_integrity_audit(path: Path) -> None:
    a = json.loads(Path(path).read_text())
    if not (a.get("schema") == "rebaseguard.p5y.k1.ps1.postk1-adjudication-audit.v1"
            and a.get("INTEGRITY_READY_FOR_ADJUDICATION") is True and (a.get("A_completeness") or {}).get("complete") is True):
        raise AssemblyRefusal("SR integrity audit does not report a complete, integral 369-cell production record")


def check_cusum_attestation(path: Path, records: list[dict]) -> None:
    a = json.loads(Path(path).read_text())
    if not (a.get("schema") == CUSUM_ATTESTATION_SCHEMA and a.get("cells_verified") == 326
            and a.get("all_scientific_hashes_verified") is True and a.get("producer_identity_hash")
            and a.get("producer_checkpoint_sha256")):
        raise AssemblyRefusal("CUSUM integrity attestation missing or incomplete")
    bad = [r.get("cell_index") for r in records if r.get("producer_identity_hash") != a["producer_identity_hash"]]
    if bad:
        raise AssemblyRefusal(f"CUSUM records not bound to the attested producer identity: {bad[:5]}")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--records", help="--synthetic: directory of per-cell JSON fixtures")
    ap.add_argument("--synthetic", action="store_true")
    ap.add_argument("--sr-sealed-cells")
    ap.add_argument("--sr-integrity-audit")
    ap.add_argument("--cusum-records")
    ap.add_argument("--cusum-attestation")
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    if a.synthetic:
        recs = [json.loads(p.read_text()) for p in sorted(Path(a.records).glob("*.json"))]
        if any(not r.get("SYNTHETIC_FIXTURE_NOT_SCIENCE") for r in recs):
            raise AssemblyRefusal("--synthetic accepts only records stamped SYNTHETIC_FIXTURE_NOT_SCIENCE")
        mode = "SYNTHETIC"
    else:
        if not genuine_mode_allowed():
            raise AssemblyRefusal("GENUINE mode locked: K4 checkpoint absent, unbound, or source hashes drifted")
        if not (a.sr_sealed_cells and a.sr_integrity_audit and a.cusum_records and a.cusum_attestation):
            raise AssemblyRefusal("GENUINE mode requires --sr-sealed-cells, --sr-integrity-audit, --cusum-records "
                                  "and --cusum-attestation")
        check_sr_integrity_audit(Path(a.sr_integrity_audit))
        cusum = [json.loads(p.read_text()) for p in sorted(Path(a.cusum_records).glob("*.json"))]
        check_cusum_attestation(Path(a.cusum_attestation), cusum)
        recs = load_sr_sealed(Path(a.sr_sealed_cells)) + cusum
        mode = "GENUINE"
    rep = assemble(recs, verify_sr_integrity=True)
    rep["mode"] = mode
    Path(a.out).write_text(json.dumps(rep, indent=1, sort_keys=True) + "\n")
    print(json.dumps({k: rep[k] for k in ("mode", "all_eight_cellwise_certified", "verdict_issued")}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
