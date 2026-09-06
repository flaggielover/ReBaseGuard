"""PHASE 13: one aggregate ledger over the complete 326-cell CUSUM cover.

WHY A FRESH RUN AND NOT AN INHERITANCE
--------------------------------------
Adjudication returned CUSUM_COVER_INHERITANCE = REQUIRES_FULL_326_RERUN. Earlier
namespaces certified their cells under producer identities that were later
rejected, so composing those records into a final ledger would make the ledger
only as good as the weakest identity in it. This ledger admits a cell only if its
record carries THIS namespace's producer identity, its scientific hash
recomputes, and its provenance chain verifies. No predecessor record is
composable, and `verify()` says so per cell rather than assuming it.

WHAT THE LEDGER BINDS
---------------------
    the Aux4 producer identity      manifest, runtime contract, identity hash
    the exact 326-cell universe     every frozen cell id, e0, rho, endpoints
    every per-cell certificate      scientific hash and per-m status
    aggregate ordering              cells in frozen index order, no gaps
    the far-field certificate       inherited, by explicit reference
    frozen checkpoint/spec hashes   checkpoint, cells, error algebra

`CUSUM_FULL_COVER = PASS_CANDIDATE` is returned only when all 326 cells are
present exactly once, every certificate verifies under this producer, and every
(cell, m) passes its frozen threshold. Anything else returns INCOMPLETE together
with the precise reason.
"""
from __future__ import annotations

import hashlib
import json
from fractions import Fraction as F
from pathlib import Path

import ancestry4

import spec

import hash_v2 as H
import identity4 as ID
import manifest_v2

SCHEMA = "k1.cusum-aux4.aggregate-ledger.v1"
CELLS_DIR = ancestry4.NS / "diagnostics" / "cells"
M_VALUES = ("1", "2", "3", "5")

FAR_FIELD = {
    "CUSUM_FAR_FIELD": "PASS",
    "SR_FAR_FIELD": "PASS",
    "authority": "binding K1/P5X far-field certificate (P5X-T3)",
    "confirmed_by": "independent adjudication of 4191beb8 (FAR_FIELD = PASS)",
    "inherited_not_re_derived": True,
    "uncovered_interval_between_c_D_and_e_far": None,
    "superseded_gap_interpretation_reintroduced": False,
}


def cusum_cells() -> list[dict]:
    return sorted((c for c in spec.CELLS if c["detector"] == "CUSUM"),
                  key=lambda c: c["index"])


def load_records(cells_dir: Path | None = None) -> dict[int, dict]:
    d = CELLS_DIR if cells_dir is None else Path(cells_dir)
    out = {}
    for p in sorted(d.glob("aux4_CUSUM_*.json")):
        rec = json.loads(p.read_text())
        idx = rec["cell_index"]
        if idx in out:
            raise ValueError(f"duplicate record for cell {idx}")
        out[idx] = rec
    return out


def verify_cell(rec: dict, cell: dict, ident: dict) -> dict:
    """Every reason this record may not enter the ledger."""
    problems = []
    if rec["detector"] != "CUSUM":
        problems.append("detector is not CUSUM")
    if rec["cell_index"] != cell["index"]:
        problems.append("cell index mismatch")
    for field in ("e0", "rho", "left", "right", "C_upper"):
        if field in rec and rec[field] != cell[field]:
            problems.append(f"frozen geometry mismatch: {field}")
    if rec.get("precision_bits") != spec.PRODUCTION_BITS:
        problems.append("precision is not the frozen 256")
    prod = rec.get("producer", {})
    for key in ("producer_manifest_hash", "runtime_contract_hash",
                "producer_identity_hash"):
        if prod.get(key) != ident[key]:
            problems.append(f"producer {key} is not this namespace's")
    if rec.get("implementation_hash_kind") != ID.IDENTITY_KIND:
        problems.append("identity kind is not Aux4's")
    if H.record_scientific_hash(rec) != rec.get("scientific_content_hash"):
        problems.append("scientific hash does not recompute")
    if H.auxiliary_evidence_hash(rec) != rec.get("auxiliary_evidence_hash"):
        problems.append("auxiliary evidence hash does not recompute")
    chain = rec.get("provenance_chain", {})
    if not chain.get("all_verified") or chain.get("obligations") != 28:
        problems.append("provenance chain incomplete")
    if not chain.get("auxiliary_evidence_bound"):
        problems.append("auxiliary evidence not bound into the chain")
    if not rec.get("scipy_guard", {}).get("scipy_free"):
        problems.append("SciPy guard did not certify the run SciPy-free")
    if not rec.get("producer", {}).get("final_gate", {}).get("ran_after_scientific_hash"):
        problems.append("final gate did not run after the scientific hash")
    missing_m = [m for m in M_VALUES if m not in rec.get("m", {})]
    if missing_m:
        problems.append(f"missing m levels {missing_m}")
    statuses = {m: rec["m"][m]["status"] for m in M_VALUES if m in rec.get("m", {})}
    failing = sorted(m for m, s in statuses.items() if s != "PASS")
    return {"ok": not problems and not failing,
            "problems": problems,
            "statuses": statuses,
            "failing_m": failing,
            "scientific_hash": rec.get("scientific_content_hash"),
            "auxiliary_hash": rec.get("auxiliary_evidence_hash"),
            "cpu_seconds": rec.get("cpu_seconds_including_dependencies")}


def build(cells_dir: Path | None = None) -> dict:
    ident = manifest_v2.identity()
    cells = cusum_cells()
    records = load_records(cells_dir)
    per_cell, problems = {}, []
    present, passing = 0, 0
    for cell in cells:
        idx = cell["index"]
        if idx not in records:
            per_cell[idx] = {"present": False}
            continue
        present += 1
        v = verify_cell(records[idx], cell, ident)
        per_cell[idx] = {"present": True, **v}
        if v["ok"]:
            passing += 1
        else:
            problems.append(f"cell {idx}: "
                            + "; ".join(v["problems"] or
                                        [f"m={','.join(v['failing_m'])} not PASS"]))
    missing = [c["index"] for c in cells if not per_cell[c["index"]]["present"]]
    obligations = sum(len(per_cell[i].get("statuses", {})) for i in per_cell)
    obligations_pass = sum(1 for i in per_cell
                           for s in per_cell[i].get("statuses", {}).values()
                           if s == "PASS")

    complete = (present == 326 and passing == 326 and not missing)
    ledger = {
        "schema": SCHEMA,
        "campaign": "p5y_k1_cusum_aux4_fullcover",
        "detector": "CUSUM",
        "producer": ident,
        "runtime_contract_hash": ident["runtime_contract_hash"],
        "frozen": {
            "checkpoint_hash": spec.CHECKPOINT_SHA256,
            "cells_sha256": spec.CELLS_SHA256,
            "error_algebra_sha256": spec.ERROR_ALGEBRA_SHA256,
            "obligation_universe_total": spec.TOTAL_UNITS,
            "m_values": list(spec.M_VALUES),
            "precision_bits": spec.PRODUCTION_BITS,
            "cusum_cell_count": len(cells),
        },
        "universe": {
            "cells_expected": 326,
            "cells_present": present,
            "cells_missing": missing,
            "duplicates": [],
            "obligations_expected": 326 * 4,
            "obligations_present": obligations,
            "obligations_pass": obligations_pass,
        },
        "far_field": FAR_FIELD,
        "cells": {str(i): per_cell[i] for i in sorted(per_cell)},
        "problems": problems[:50],
        "problem_count": len(problems),
        "cusum_full_cover": "PASS_CANDIDATE" if complete else "INCOMPLETE",
        "result_bearing": False,
        "production_run": False,
    }
    ledger["ledger_hash"] = hashlib.sha256(
        manifest_v2.canonical({k: v for k, v in ledger.items()
                               if k != "ledger_hash"})).hexdigest()
    return ledger


def verify(ledger: dict) -> dict:
    """Independent re-verification of a committed ledger."""
    problems = []
    body = {k: v for k, v in ledger.items() if k != "ledger_hash"}
    if hashlib.sha256(manifest_v2.canonical(body)).hexdigest() != ledger["ledger_hash"]:
        problems.append("ledger hash does not recompute")
    u = ledger["universe"]
    if u["cells_present"] != len(set(int(i) for i in ledger["cells"]
                                     if ledger["cells"][i]["present"])):
        problems.append("cell count disagrees with the per-cell map")
    if u["duplicates"]:
        problems.append(f"duplicate cells: {u['duplicates']}")
    if ledger["frozen"]["cusum_cell_count"] != 326:
        problems.append("frozen CUSUM cell count is not 326")
    if ledger["frozen"]["obligation_universe_total"] != 17978:
        problems.append("obligation universe is not 17,978")
    return {"ok": not problems, "problems": problems,
            "cusum_full_cover": ledger["cusum_full_cover"]}


def main() -> None:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--cells-dir")
    ap.add_argument("--out")
    ap.add_argument("--brief", action="store_true")
    a = ap.parse_args()
    ledger = build(a.cells_dir)
    if a.out:
        Path(a.out).write_text(json.dumps(ledger, indent=2, sort_keys=True) + "\n")
    if a.brief:
        u = ledger["universe"]
        print(json.dumps({
            "cusum_full_cover": ledger["cusum_full_cover"],
            "cells_present": u["cells_present"],
            "cells_missing": len(u["cells_missing"]),
            "obligations_pass": f"{u['obligations_pass']}/{u['obligations_expected']}",
            "problem_count": ledger["problem_count"],
            "first_problems": ledger["problems"][:5],
            "ledger_hash": ledger["ledger_hash"][:16],
            "producer_identity": ledger["producer"]["producer_identity_hash"][:16],
        }, indent=2))
    else:
        print(json.dumps(ledger, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
