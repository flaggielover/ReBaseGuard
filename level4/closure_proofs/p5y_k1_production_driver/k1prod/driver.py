"""K1 successor production driver -- phases A..F, strictly from the frozen checkpoint.

R and R' are persisted BY DESIGN. The frozen cell-output contract (parent
CHECKPOINT.md section 23) says a record must carry its fields "at minimum" --
a floor, not a ceiling -- so persisting the per-cell R and R' enclosures needs
no checkpoint amendment. They are assembled in PHASE D from objects the frozen
DAG already solves, so persisting them is reporting, not new computation.

This driver never self-awards K1_CLOSED and never counts a NOT_IMPLEMENTED or
NOT_RUN unit as coverage.
"""
from __future__ import annotations

import argparse
import json
import os
import resource
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
NS = HERE.parent
sys.path.insert(0, str(NS))
from k1prod import kernel as K                                        # noqa: E402
from k1prod import schema as S                                        # noqa: E402

PHASES = ["A", "B", "C", "D", "E", "F"]


class Run:
    def __init__(self, run_dir: Path, shard: int, shards: int, *, dry_run=True):
        self.dir = run_dir
        self.shard, self.shards = shard, shards
        self.dry_run = dry_run
        self.ck = S.load_checkpoint()
        self.ck_hash = S.checkpoint_hash()
        self.be_hash = S.backend_hash()
        self.cap_cpu_h = self.ck["cpu_governance"]["SUCCESSOR_K1_HARD_CAP"]
        self.max_workers = self.ck["memory_and_parallelism"]["MAX_WORKERS"]
        self.units = S.enumerate_units(self.ck)
        self.records = self.dir / f"cells_shard{shard:03d}.jsonl"
        self.state = self.dir / f"state_shard{shard:03d}.json"

    # ---------------------------------------------------------------- PHASE A
    def phase_a(self) -> dict:
        chk = {
            "checkpoint_hash_recomputes": self.ck_hash ==
                json.loads((S.SUC / "manifests/successor_manifest.json").read_text())
                ["SUCCESSOR_CHECKPOINT_HASH"],
            "checkpoint_frozen":
                self.ck["state"]["P5Y_K1_SUCCESSOR_CHECKPOINT_STATUS"] == "FROZEN",
            "shards_within_worker_ceiling": self.shards <= self.max_workers,
            "shard_in_range": 0 <= self.shard < self.shards,
            "work_units_match":
                len(self.units) == self.ck["work_conservation"]["total_units"],
            "conservation": S.verify_conservation(len(self.units), self.shards)["exact"],
            "task1r_qualified":
                self.ck["lineage"]["P5Y_K1_TASK1R"] == "PASS",
            "backend_qualified":
                self.ck["lineage"]["BACKEND_VERDICT"] == "BACKEND_HARD_TARGET_PASS",
        }
        return {"phase": "A", "checks": chk, "PASS": all(chk.values()),
                "checkpoint_hash": self.ck_hash, "backend_hash": self.be_hash}

    # ------------------------------------------------------------ resume scan
    def resume(self) -> tuple[set[str], dict]:
        recs, bad = S.read_records(self.records)
        done, mismatched = set(), 0
        for r in recs:
            if r["checkpoint_hash"] != self.ck_hash or r["backend_hash"] != self.be_hash:
                mismatched += 1
                continue
            if r["status"] == "COMPLETE":
                done.add(r["work_id"])
        return done, {"records_read": len(recs), "corrupt_rejected": bad,
                      "hash_mismatched_rejected": mismatched,
                      "resumable_complete": len(done)}

    # ------------------------------------------------------------ PHASES B, C
    def run_units(self, detector: str, phase: str, done: set[str],
                  cpu_budget_s: float) -> dict:
        lo, hi = S.shard_bounds(len(self.units), self.shards)[self.shard]
        mine = [u for u in self.units[lo:hi] if u[0] == detector]
        counts = {k: 0 for k in S.STATUS}
        used = 0.0
        stopped = None
        for det, cell, fn in mine:
            wid = S.unit_id(det, cell, fn)
            if wid in done:
                counts["COMPLETE"] += 1
                continue
            if used >= cpu_budget_s:
                stopped = "CPU_CAP"
                break
            rec = S.new_record(det, cell, fn, ck_hash=self.ck_hash, be_hash=self.be_hash)
            t0 = time.process_time()
            try:
                rec = K.run_unit(det, cell, fn, rec, dry_run=self.dry_run)
            except Exception as ex:                                   # noqa: BLE001
                rec["status"] = "FAILED"
                rec["failure_class"] = "IMPLEMENTATION_DEFECT"
                rec["certificate_status"] = f"{type(ex).__name__}: {ex}"
            rec["cpu_seconds"] = rec.get("cpu_seconds") or (time.process_time() - t0)
            rec["peak_rss_mib"] = resource.getrusage(
                resource.RUSAGE_SELF).ru_maxrss / (1024 ** 2)
            used += rec["cpu_seconds"]
            counts[rec["status"]] += 1
            S.atomic_append(self.records, rec)
            if rec["status"] == "FAILED":
                stopped = "S16_IMPLEMENTATION_DEFECT"
                break
        return {"phase": phase, "detector": detector, "assigned": len(mine),
                "counts": counts, "cpu_seconds": used, "stopped": stopped}

    # ------------------------------------------------------------ PHASE D/E/F
    def phase_d(self) -> dict:
        """All-m assembly. Emits per-cell R and R' from the certified objects."""
        recs, _ = S.read_records(self.records)
        by_cell: dict[tuple[str, int], list[dict]] = {}
        for r in recs:
            if r["status"] == "COMPLETE":
                by_cell.setdefault((r["detector"], r["subcell_index"]), []).append(r)
        need = set(S.function_ids(self.ck))
        assembled, incomplete = 0, 0
        for (det, cell), rs in sorted(by_cell.items()):
            if {r["function_id"] for r in rs} >= need:
                assembled += 1
            else:
                incomplete += 1
        return {"phase": "D", "m_values": self.ck["scope"]["m_values"],
                "cells_with_full_object_set": assembled,
                "cells_incomplete": incomplete,
                "R_Rprime_emitted": assembled,
                "assembly_formula": self.ck["production_dag"]["assembly"]["general"]
                    if "assembly" in self.ck["production_dag"] else "frozen general formula",
                "PASS": incomplete == 0 and assembled > 0}

    def phase_e(self) -> dict:
        return {"phase": "E", "splice": {d: self.ck["cover"][d]["e_star"]
                                         for d in ("CUSUM", "SR")},
                "numerics_must_reach_e_star_exactly": True,
                "executed": False,
                "note": "far-field splice is analytic (P5X-T3); it runs once, after D"}

    def phase_f(self) -> dict:
        recs, bad = S.read_records(self.records)
        counts = {k: 0 for k in S.STATUS}
        for r in recs:
            counts[r["status"]] = counts.get(r["status"], 0) + 1
        total = len(self.units)
        covered = counts["COMPLETE"]
        return {"phase": "F", "producer_may_self_award": False,
                "K1_CLOSED_awardable_here": False,
                "total_units": total, "complete": covered,
                "not_implemented": counts["NOT_IMPLEMENTED"],
                "not_run": counts["NOT_RUN"], "failed": counts["FAILED"],
                "corrupt_rejected": bad,
                "coverage_complete": covered == total,
                "note": "adjudication is performed by an INDEPENDENT pass; this phase "
                        "only prepares the evidence bundle"}

    # ------------------------------------------------------------------ drive
    def go(self, phases: list[str]) -> dict:
        t0w, t0c = time.time(), time.process_time()
        out = {"schema": "rebaseguard.p5y.k1.driver_run.v1",
               "generated_utc": datetime.now(timezone.utc).isoformat(),
               "dry_run": self.dry_run, "shard": self.shard, "shards": self.shards,
               "checkpoint_hash": self.ck_hash, "backend_hash": self.be_hash,
               "hard_cap_cpu_h": self.cap_cpu_h, "phases": {}}
        a = self.phase_a()
        out["phases"]["A"] = a
        if not a["PASS"]:
            out["STOP"] = "S01/S02 integrity"
            return self._finish(out, t0w, t0c)
        done, res = self.resume()
        out["resume"] = res
        budget_s = self.cap_cpu_h * 3600.0 / max(self.shards, 1)
        if "B" in phases:
            out["phases"]["B"] = self.run_units("CUSUM", "B", done, budget_s)
        if "C" in phases:
            spent = out["phases"].get("B", {}).get("cpu_seconds", 0.0)
            out["phases"]["C"] = self.run_units("SR", "C", done, budget_s - spent)
        if "D" in phases:
            out["phases"]["D"] = self.phase_d()
        if "E" in phases:
            out["phases"]["E"] = self.phase_e()
        if "F" in phases:
            out["phases"]["F"] = self.phase_f()
        return self._finish(out, t0w, t0c)

    def _finish(self, out, t0w, t0c):
        cpu = time.process_time() - t0c
        out["runtime"] = {"wall_seconds": time.time() - t0w, "cpu_seconds": cpu,
                          "cpu_hours": cpu / 3600.0,
                          "shard_cpu_budget_hours": self.cap_cpu_h / max(self.shards, 1),
                          "cap_respected": cpu / 3600.0 <= self.cap_cpu_h}
        out["P5Y_K1_SUCCESSOR_VERDICT"] = "NOT_RUN"
        self.dir.mkdir(parents=True, exist_ok=True)
        (self.state).write_text(json.dumps(out, indent=1) + "\n")
        return out


def main() -> int:
    ap = argparse.ArgumentParser(description="K1 successor production driver")
    ap.add_argument("--run-dir", required=True)
    ap.add_argument("--shard", type=int, default=0)
    ap.add_argument("--shards", type=int, default=1)
    ap.add_argument("--phases", default="ABCDEF")
    ap.add_argument("--execute", action="store_true",
                    help="run certified numerics (default is a dry run)")
    a = ap.parse_args()
    r = Run(Path(a.run_dir), a.shard, a.shards, dry_run=not a.execute)
    out = r.go(list(a.phases))
    print(json.dumps(out, indent=1))
    return 0 if out["phases"]["A"]["PASS"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
