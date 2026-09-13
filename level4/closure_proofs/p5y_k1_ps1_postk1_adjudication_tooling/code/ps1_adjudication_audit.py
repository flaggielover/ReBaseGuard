"""Post-K1 PS1 adjudication PREPARATION audit. READ-ONLY and RESULT-AGNOSTIC.

It establishes whether the production record is complete, internally consistent and correctly
accounted -- never whether the science passed. By default it is BLINDED: scientific status values
(T3_PASS, T5 status/pass_count, B_cover_ratio) are never read into the report; only presence, hashes
and identities are. `--unblind` is reserved for the independent adjudicator and only adds a verbatim
per-cell status column; no verdict is ever computed here.

Audits
  A  sealed-cell completeness over the frozen 369-cell domain
  B  ledger <-> sealed-file reconciliation (canonical byte equality)
  C  scientific-hash audit: evidence file sha256 and recomputed scientific_content_hash
  D  torn / duplicate / reservation / run / halt state
  E  CPU-hour accounting (imported history + science + settlement charges; governed cap)
  F  continuity hash-chain verification of every runtime dir given
  G  per-cell coverage matrix (CSV)

  python ps1_adjudication_audit.py --production-root <gen2 tree> [--runtime-dir D ...]
        [--evidence-root E ...] [--gen1-ledger L] [--out-dir OUT] [--unblind]
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

NS_REL = "level4/closure_proofs/p5y_k1_ps1_production"
TOTAL_CELLS = 369
IMPORTED_HISTORY_CPU_H = 92.32
SCIENTIFIC_FIELDS = ("scientific_content_hash", "successor_id", "evidence.*.sha256", "t3_record_sha256",
                     "t4_record_sha256", "t5 certificate_hash list", "B_cover_ratio", "precision_bits",
                     "producer_commit", "checkpoint_sha256", "runtime_contract_hash")
INCIDENTAL_FIELDS = ("cpu_seconds", "task_id", "evidence.*.path", "run ids", "completed_utc", "peak_rss_kib",
                     "cache_hits", "cache_misses", "role", "host paths", "wall clock")
STATUS_KEYS = ("T3_PASS", "status", "pass_count", "total", "B_cover_ratio")


def sha_file(p) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def canon(o) -> bytes:
    return json.dumps(o, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()


def recompute_scientific_hash(t3, t4, t5) -> set:
    """Both serialisations used by the bound code path: worker canonical() (newline included) and
    launcher M.canonical()+b'\\n'. Returns the candidate digests; matching either is consistent."""
    body = {"t3_record_sha256": t3["t3_record_sha256"], "t4_record_sha256": t4["t4_record_sha256"],
            "t5_certificate_hashes": [o["certificate_hash"] for o in t5["obligations"]]}
    return {hashlib.sha256(canon(body) + b"\n").hexdigest(), hashlib.sha256(canon(body)).hexdigest(),
            hashlib.sha256(canon(body) + b"\n\n").hexdigest()}


def verify_chain(path: Path) -> dict:
    if not path.exists():
        return {"present": False}
    prev, n = None, 0
    for line in path.read_text().splitlines():
        if not line.strip():
            continue
        rec = json.loads(line)
        body = {k: v for k, v in rec.items() if k != "sha256"}
        want = hashlib.sha256(canon(body) + b"\n").hexdigest()
        if rec.get("sha256") != want or rec.get("prev_sha256") != (prev["sha256"] if prev else None):
            return {"present": True, "valid": False, "broken_at_seq": rec.get("seq"), "records": n}
        prev, n = rec, n + 1
    return {"present": True, "valid": True, "records": n, "last_event": prev and prev["event"],
            "last_view": prev and prev.get("view")}


def audit(production_root: Path, runtime_dirs, evidence_roots, gen1_ledger=None, unblind=False) -> dict:
    ns = production_root / NS_REL
    ledger_p = ns / "production/PRODUCTION_LEDGER.json"
    st = json.loads(ledger_p.read_text())
    ops = st.get("operational_lifecycle") or {}
    completed = st.get("completed_cells", {})
    cells_dir = ns / "production/cells"
    sealed = {int(p.stem): p for p in sorted(cells_dir.glob("[0-9]*.json"))} if cells_dir.exists() else {}
    stray = sorted(p.name for p in cells_dir.iterdir()
                   if cells_dir.exists() and not (p.name[:4].isdigit() and p.name.endswith(".json"))) \
        if cells_dir.exists() else []
    domain = set(range(TOTAL_CELLS))

    # ---- markers across every evidence root (duplicates / orphans)
    markers = defaultdict(list)
    for root in evidence_roots:
        root = Path(root)
        if root.exists():
            for p in sorted(root.rglob("cell_done_[0-9]*.json")):
                try:
                    m = json.loads(p.read_text())
                    markers[int(m["cell_id"])].append({"path": str(p), "run_id": m.get("run_id"),
                                                       "launcher_pid": m.get("launcher_pid"),
                                                       "scientific_content_hash": m.get("scientific_content_hash")})
                except (OSError, ValueError, KeyError, TypeError):
                    markers[-1].append({"path": str(p), "unreadable": True})

    rows, issues = [], defaultdict(list)
    sci_by_hash = defaultdict(list)
    open_res = st.get("open_reservations", {})
    open_cells = defaultdict(list)
    for k, r in open_res.items():
        open_cells[r.get("cell_id")].append(k)
    torn = ops.get("torn_attempts", {})
    record_cpu_s = 0.0
    for cell in range(TOTAL_CELLS):
        row = {"cell": cell, "sealed_file": cell in sealed, "ledger_completed": str(cell) in completed,
               "record_equal_ledger": None, "evidence_files_ok": None, "scientific_hash_consistent": None,
               "markers": len(markers.get(cell, [])), "torn_attempts": torn.get(str(cell), 0),
               "open_reservations": len(open_cells.get(cell, [])), "successor_id": None}
        rec = None
        if cell in sealed:
            rec = json.loads(sealed[cell].read_bytes())
            row["record_equal_ledger"] = rec == completed.get(str(cell))
            if not row["record_equal_ledger"]:
                issues["B_sealed_file_differs_from_ledger" if str(cell) in completed else "B_orphan_sealed_file"].append(cell)
        elif str(cell) in completed:
            rec = completed[str(cell)]
            issues["B_ledger_completed_without_sealed_file"].append(cell)
        if rec is not None:
            row["successor_id"] = rec.get("successor_id")
            record_cpu_s += float(rec.get("cpu_seconds") or 0.0)
            ev = rec.get("evidence") or {}
            ok, loaded = True, {}
            for name in ("t3", "t4", "t5", "patches_gz"):
                e = ev.get(name)
                if not e or not Path(e["path"]).exists():
                    ok = False
                    issues["C_evidence_missing"].append([cell, name])
                    continue
                if sha_file(e["path"]) != e["sha256"]:
                    ok = False
                    issues["C_evidence_hash_mismatch"].append([cell, name])
                elif name != "patches_gz":
                    loaded[name] = json.loads(Path(e["path"]).read_text())
            row["evidence_files_ok"] = ok
            if {"t3", "t4", "t5"} <= set(loaded):
                try:
                    row["scientific_hash_consistent"] = rec.get("scientific_content_hash") in \
                        recompute_scientific_hash(loaded["t3"], loaded["t4"], loaded["t5"])
                except (KeyError, TypeError):
                    row["scientific_hash_consistent"] = "UNVERIFIABLE_EVIDENCE_SHAPE"
                if row["scientific_hash_consistent"] is False:
                    issues["C_scientific_hash_inconsistent"].append(cell)
                ids = [loaded[k].get("cell") for k in ("t3", "t4", "t5")]
                if any(i is not None and i != cell for i in ids):
                    issues["C_evidence_cell_identity_mismatch"].append(cell)
                if unblind:
                    row["status_verbatim"] = {"T3_PASS": loaded["t3"].get("T3_PASS"),
                                              "t5_status": loaded["t5"].get("status"),
                                              "t5_pass_count": loaded["t5"].get("pass_count")}
            sci_by_hash[rec.get("scientific_content_hash")].append(cell)
            for m in markers.get(cell, []):
                if m.get("scientific_content_hash") not in (None, rec.get("scientific_content_hash")):
                    issues["D_marker_hash_differs_from_sealed_record"].append([cell, m["path"]])
        elif markers.get(cell):
            issues["D_durable_marker_without_sealed_cell"].append(cell)
        if len({m.get("run_id") for m in markers.get(cell, [])}) > 1:
            issues["D_cell_marked_complete_in_multiple_runs"].append(cell)
        if rec is not None and open_cells.get(cell):
            issues["D_open_reservation_on_completed_cell"].append(cell)
        rows.append(row)
    for h, cs in sci_by_hash.items():
        if h and len(cs) > 1:
            issues["D_same_scientific_hash_on_distinct_cells"].append(cs)
    extra_ids = sorted(set(int(c) for c in completed) - domain) + sorted(set(sealed) - domain)
    if extra_ids:
        issues["A_cells_outside_domain"] = extra_ids

    runs = ops.get("runs", {})
    settlements = ops.get("settlements", [])
    charges = sum(float(s.get("charge_cpu_h", 0.0)) for s in settlements)
    committed = st.get("committed_cpu_h_by_role", {})
    science_h = record_cpu_s / 3600.0
    expected = IMPORTED_HISTORY_CPU_H + science_h + charges
    acct = {"committed_cpu_h_by_role": committed, "imported_history_cpu_h": IMPORTED_HISTORY_CPU_H,
            "science_record_cpu_h": science_h, "settlement_charges_cpu_h": charges,
            "expected_committed_aws_cpu_h": expected,
            "reconciles": abs(float(committed.get("AWS", 0.0)) - expected) < 1e-6 if not open_res else "OPEN_RESERVATIONS_PRESENT",
            "open_reservation_cpu_h": sum(float(r.get("reserved_cpu_h", 0.0)) for r in open_res.values()),
            "global_cap_cpu_h": 6600.0, "overhead_factor": 1.15, "governed_overhead_cpu_h": 102.123}
    acct["governed_charged_cpu_h_if_settled"] = 1.15 * (sum(float(v) for v in committed.values())
                                                        + acct["open_reservation_cpu_h"] + 102.123)
    if gen1_ledger and Path(gen1_ledger).exists():
        g1 = json.loads(Path(gen1_ledger).read_text())
        acct["generation1"] = {"ledger_sha256": sha_file(gen1_ledger), "committed_cpu_h_by_role": g1.get("committed_cpu_h_by_role"),
                               "completed_cells": len(g1.get("completed_cells", {}))}

    sealed_set, ledger_set = set(sealed), {int(c) for c in completed}
    out = {"schema": "rebaseguard.p5y.k1.ps1.postk1-adjudication-audit.v1", "result_agnostic": True,
           "blinded": not unblind, "production_root": str(production_root),
           "ledger_sha256": sha_file(ledger_p), "field_classification": {"scientific": SCIENTIFIC_FIELDS,
                                                                       "incidental": INCIDENTAL_FIELDS},
           "A_completeness": {"domain": TOTAL_CELLS, "sealed_files": len(sealed_set), "ledger_completed": len(ledger_set),
                              "sealed_and_ledger": len(sealed_set & ledger_set),
                              "missing_from_both": len(domain - sealed_set - ledger_set),
                              "complete": sealed_set == ledger_set == domain, "stray_files_in_cells_dir": stray},
           "B_reconciliation": {"sealed_equal_ledger": sum(1 for r in rows if r["record_equal_ledger"] is True)},
           "C_scientific_hash": {"evidence_ok_cells": sum(1 for r in rows if r["evidence_files_ok"] is True),
                                 "scientific_hash_consistent_cells": sum(1 for r in rows if r["scientific_hash_consistent"] is True)},
           "D_state": {"open_reservations": sorted(open_res), "torn_attempts": torn,
                       "release_kinds": dict(Counter(r.get("kind") for r in ops.get("releases", []))),
                       "runs_by_status": dict(Counter(r.get("status") for r in runs.values())),
                       "unsettled_runs": sorted(k for k, r in runs.items() if r.get("status") == "OPEN"),
                       "halt_field_verbatim": ops.get("halt"),
                       "markers_total": sum(len(v) for k, v in markers.items() if k >= 0),
                       "unreadable_markers": len(markers.get(-1, []))},
           "E_accounting": acct,
           "F_continuity": {str(d): verify_chain(Path(d) / "continuity.jsonl") for d in runtime_dirs},
           "issues": {k: v for k, v in issues.items()},
           "INTEGRITY_READY_FOR_ADJUDICATION": (sealed_set == ledger_set == domain and not issues and not open_res
                                                and not any(r.get("status") == "OPEN" for r in runs.values())
                                                and all(v.get("valid", True) for v in
                                                        (verify_chain(Path(d) / "continuity.jsonl") for d in runtime_dirs)))}
    return out, rows


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--production-root", required=True)
    ap.add_argument("--runtime-dir", action="append", default=[])
    ap.add_argument("--evidence-root", action="append", default=[])
    ap.add_argument("--gen1-ledger")
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--unblind", action="store_true")
    a = ap.parse_args()
    out, rows = audit(Path(a.production_root), a.runtime_dir, a.evidence_root, a.gen1_ledger, a.unblind)
    od = Path(a.out_dir)
    od.mkdir(parents=True, exist_ok=True)
    (od / "ADJUDICATION_AUDIT.json").write_text(json.dumps(out, indent=1, sort_keys=True, default=str) + "\n")
    with open(od / "COVERAGE_MATRIX.csv", "w", newline="") as f:
        cols = sorted({k for r in rows for k in r}, key=lambda k: (k != "cell", k))
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in rows:
            w.writerow({k: json.dumps(v) if isinstance(v, (dict, list)) else v for k, v in r.items()})
    print(json.dumps({"INTEGRITY_READY_FOR_ADJUDICATION": out["INTEGRITY_READY_FOR_ADJUDICATION"],
                      "A": out["A_completeness"], "issues": {k: len(v) for k, v in out["issues"].items()}}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
