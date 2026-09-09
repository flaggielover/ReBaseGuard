"""Cap accounting and cell-atomic resume for the SR driver-bound successor.

Cap semantics are NOT reinterpreted here. The frozen model is
    charged = OVERHEAD * (measured SR CPU-seconds + CUSUM CPU-seconds)
and the campaign refuses to start work that could knowingly cross the cap.
Accounting is deliberately conservative: a cell is charged its measured cost
when committed, and admission uses a worst-observed-cell reservation so the cap
cannot be crossed by work already in flight.
"""
from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

from gates import GateFailure, canonical, sha256_file
import hashlib


class CapExceeded(RuntimeError):
    """Admitting more work could knowingly cross the frozen cap."""


class DuplicateCell(RuntimeError):
    """A cell already committed under this campaign identity."""


def atomic_write_json(path: Path, obj) -> None:
    """Write-then-rename. A partially written file is never visible."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), suffix=".tmp")
    try:
        with os.fdopen(fd, "w") as fh:
            json.dump(obj, fh, indent=1, sort_keys=True)
            fh.write("\n")
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp, path)
    except BaseException:
        Path(tmp).unlink(missing_ok=True)
        raise


class CapLedger:
    """Append-only, audit-visible CPU-hour accounting against the frozen cap."""

    def __init__(self, path: Path, cap_cpu_h: float, overhead: float,
                 cusum_cpu_h: float, *, reserve_cpu_h: float):
        self.path = Path(path)
        self.cap = float(cap_cpu_h)
        self.overhead = float(overhead)
        self.cusum = float(cusum_cpu_h)
        self.reserve = float(reserve_cpu_h)
        if self.path.exists():
            self.state = json.loads(self.path.read_text())
        else:
            self.state = {"schema": "k1.sr.cap-ledger.v1",
                          "cap_cpu_h": self.cap, "overhead_factor": self.overhead,
                          "cusum_cpu_h": self.cusum,
                          "raw_sr_cpu_seconds": 0.0, "entries": []}
            atomic_write_json(self.path, self.state)   # exists from the start
        for k, v in (("cap_cpu_h", self.cap), ("overhead_factor", self.overhead),
                     ("cusum_cpu_h", self.cusum)):
            if float(self.state[k]) != v:
                raise GateFailure(f"cap ledger {k} drift: {self.state[k]} != {v}")

    # ---- derived quantities -------------------------------------------------
    @property
    def raw_sr_cpu_h(self) -> float:
        return self.state["raw_sr_cpu_seconds"] / 3600.0

    def charged_cpu_h(self) -> float:
        """Total charged against the cap under the FROZEN cap semantics."""
        return self.overhead * (self.raw_sr_cpu_h + self.cusum)

    def remaining_cpu_h(self) -> float:
        return self.cap - self.charged_cpu_h()

    # ---- admission ----------------------------------------------------------
    def admit(self, *, n_in_flight: int = 1) -> None:
        """Refuse BEFORE starting work that could knowingly exceed the cap.

        Conservative: reserves `reserve_cpu_h` per in-flight worker, charged at
        the overhead factor, so committing everything in flight cannot cross.
        """
        need = self.overhead * self.reserve * max(1, n_in_flight)
        if self.charged_cpu_h() + need > self.cap:
            raise CapExceeded(
                f"charged {self.charged_cpu_h():.3f} + reservation {need:.3f} "
                f"> cap {self.cap:.3f} CPU-h")

    def charge(self, *, cell_id, cpu_seconds: float, record_sha256: str) -> dict:
        entry = {"cell_id": cell_id, "cpu_seconds": float(cpu_seconds),
                 "record_sha256": record_sha256,
                 "charged_cpu_h_after": None}
        self.state["raw_sr_cpu_seconds"] += float(cpu_seconds)
        entry["charged_cpu_h_after"] = self.charged_cpu_h()
        self.state["entries"].append(entry)
        if self.charged_cpu_h() > self.cap:
            # persist first: an overrun must be audit-visible, not lost
            atomic_write_json(self.path, self.state)
            raise CapExceeded(
                f"cap crossed after committing {cell_id}: "
                f"{self.charged_cpu_h():.3f} > {self.cap:.3f}")
        atomic_write_json(self.path, self.state)
        return entry


class CellStore:
    """Cell-atomic commit with duplicate detection and audit-visible resume."""

    def __init__(self, root: Path, campaign_identity: dict):
        self.root = Path(root)
        self.cells = self.root / "cells"
        self.journal = self.root / "resume_journal.jsonl"
        self.identity = dict(campaign_identity)
        self.cells.mkdir(parents=True, exist_ok=True)

    def path_for(self, cell_id) -> Path:
        return self.cells / f"sr_CELL_{cell_id}_256.json"

    def _journal(self, event: dict) -> None:
        self.journal.parent.mkdir(parents=True, exist_ok=True)
        with open(self.journal, "a") as fh:
            fh.write(json.dumps(event, sort_keys=True) + "\n")
            fh.flush()
            os.fsync(fh.fileno())

    def completed(self) -> dict:
        """cell_id -> record, for records that are COMPLETE and identity-matched."""
        out = {}
        for p in sorted(self.cells.glob("sr_CELL_*_256.json")):
            try:
                r = json.loads(p.read_text())
            except json.JSONDecodeError:
                continue                      # a torn file is not complete
            if not r.get("cell_complete"):
                continue
            if self.identity_of(r) != self.identity:
                continue
            out[r["cell_id"]] = r
        return out

    @staticmethod
    def identity_of(record: dict) -> dict:
        return {k: record.get(k) for k in
                ("producer_commit", "checkpoint_sha256", "runtime_contract_hash")}

    def is_done(self, cell_id) -> bool:
        return cell_id in self.completed()

    def commit(self, record: dict, *, allow_duplicate=False) -> Path:
        """Atomically commit ONE complete cell. Refuses silent double-counting."""
        for k in ("cell_id", "producer_commit", "checkpoint_sha256",
                  "runtime_contract_hash", "scientific_content_hash",
                  "auxiliary_evidence_hash", "cpu_seconds", "wall_seconds",
                  "peak_rss_kib", "worker_id", "core_id", "retry_count",
                  "obligations_completed"):
            if k not in record:
                raise GateFailure(f"cell record missing required binding field: {k}")
        if self.identity_of(record) != self.identity:
            raise GateFailure("cell record identity does not match the campaign")
        cid = record["cell_id"]
        if not allow_duplicate and self.is_done(cid):
            self._journal({"event": "duplicate_rejected", "cell_id": cid})
            raise DuplicateCell(f"cell {cid} already committed; refusing to recount")
        record = dict(record)
        record["cell_complete"] = True
        body = {k: v for k, v in record.items() if k != "record_sha256"}
        record["record_sha256"] = hashlib.sha256(canonical(body)).hexdigest()
        atomic_write_json(self.path_for(cid), record)
        self._journal({"event": "cell_committed", "cell_id": cid,
                       "cpu_seconds": record["cpu_seconds"],
                       "retry_count": record["retry_count"],
                       "record_sha256": record["record_sha256"]})
        return self.path_for(cid)

    def resume_plan(self, all_cell_ids) -> dict:
        done = self.completed()
        todo = [c for c in all_cell_ids if c not in done]
        self._journal({"event": "resume_plan", "completed": len(done),
                       "remaining": len(todo)})
        return {"completed": sorted(done), "remaining": todo,
                "n_completed": len(done), "n_remaining": len(todo)}
