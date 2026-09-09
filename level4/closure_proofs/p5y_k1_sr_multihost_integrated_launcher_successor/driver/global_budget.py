"""Race-safe accounting for the ONE global 4500 CPU-h cap.

There is exactly one global budget. This module never creates a per-host,
per-shard or per-cell hard cap: a reservation is an atomic DRAW FROM THE SINGLE
GLOBAL BUDGET, not a subcap, and any unused part is returned to the same global
budget for either host to use.

Concurrency (Phase 9). Two modes are defined; the frozen authorization selects
one and the launcher fails closed on anything else.

  SERIALIZED_ACTIVE_HOST (this pre-result authorization)
      The authorization names exactly one active_host. A host whose role is not
      the active host refuses before any admission, so AWS and Vultr can never
      draw concurrently and no cross-host channel is required for correctness.
      Handover requires a NEW additive authorization. This is the conservative
      serialized cell-admission coordinator: it trades wall-clock concurrency for
      accounting integrity, which is the required preference.

  SHARED_COORDINATOR (implemented, NOT yet qualified)
      Both hosts draw from one authoritative ledger reached over a shared
      coordinator endpoint, serialised by an O_EXCL lock. It is refused unless
      the authorization binds a coordinator_endpoint AND that endpoint is
      reachable, so it cannot be entered by accident.
"""
from __future__ import annotations

import json
import os
import time
from pathlib import Path

CONCURRENCY_MODES = ("SERIALIZED_ACTIVE_HOST", "SHARED_COORDINATOR")


class BudgetRefusal(RuntimeError):
    """The global budget coordinator refused."""


class _Lock:
    """Atomic mutual exclusion via O_CREAT|O_EXCL."""

    def __init__(self, path, timeout_s=30.0):
        self.path, self.timeout_s, self.fd = Path(str(path) + ".lock"), timeout_s, None

    def __enter__(self):
        deadline = time.monotonic() + self.timeout_s
        while True:
            try:
                self.fd = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o644)
                os.write(self.fd, f"{os.getpid()}\n".encode())
                return self
            except FileExistsError:
                if time.monotonic() > deadline:
                    raise BudgetRefusal(
                        f"could not acquire the global budget lock at {self.path}; "
                        "refusing rather than proceeding without exclusion")
                time.sleep(0.01)

    def __exit__(self, *exc):
        if self.fd is not None:
            os.close(self.fd)
            try:
                os.unlink(self.path)
            except FileNotFoundError:
                pass


class GlobalBudget:
    """The single authoritative global governed-cost ledger."""

    SCHEMA = "rebaseguard.p5y.k1.sr.multihost.global-budget.v1"

    def __init__(self, path, validate_cost, gate_global_cap, *,
                 overhead_cpu_h, cap_cpu_h):
        self.path = Path(path)
        self._validate = validate_cost
        self._gate = gate_global_cap
        self.overhead_cpu_h = validate_cost(overhead_cpu_h, "governed overhead")
        self.cap_cpu_h = cap_cpu_h

    # ---------------------------------------------------------------- state
    def _read(self) -> dict:
        if not self.path.exists():
            return {"schema": self.SCHEMA, "committed_cpu_h_by_role": {},
                    "open_reservations": {}, "completed_cells": {}}
        st = json.loads(self.path.read_text())
        if st.get("schema") != self.SCHEMA:
            raise BudgetRefusal(f"global budget ledger schema mismatch: {st.get('schema')!r}")
        return st

    def _write_atomic(self, state: dict) -> None:
        tmp = self.path.with_suffix(".tmp")
        tmp.write_text(json.dumps(state, indent=1, sort_keys=True) + "\n")
        os.replace(tmp, self.path)                      # atomic finalisation

    # ------------------------------------------------------------ accounting
    def _governed_total(self, state: dict) -> dict:
        """committed + still-open reservations, through the trusted domain."""
        by_role = {}
        for role, v in state.get("committed_cpu_h_by_role", {}).items():
            by_role[role] = self._validate(v, f"committed CPU-h for {role}")
        for res in state.get("open_reservations", {}).values():
            role = res["role"]
            amt = self._validate(res["reserved_cpu_h"], f"open reservation for {role}")
            by_role[role] = by_role.get(role, 0.0) + amt
        return self._gate(by_role, self.overhead_cpu_h)   # THE one global cap

    def status(self) -> dict:
        with _Lock(self.path):
            state = self._read()
            cap = self._governed_total(state)
        return {"cap": cap, "completed_cells": sorted(
            int(c) for c in state.get("completed_cells", {}))}

    def draw(self, role: str, cell_id: int, reservation_cpu_h: float) -> str:
        """Atomically draw a reservation from the SINGLE global budget."""
        amount = self._validate(reservation_cpu_h, "cell reservation")
        with _Lock(self.path):
            state = self._read()
            if str(cell_id) in state.get("completed_cells", {}):
                raise BudgetRefusal(f"cell {cell_id} is already complete; refusing to redo it")
            key = f"{role}:{cell_id}"
            if key in state.get("open_reservations", {}):
                raise BudgetRefusal(f"cell {cell_id} already has an open reservation on {role}")
            state.setdefault("open_reservations", {})[key] = {
                "role": role, "cell_id": cell_id, "reserved_cpu_h": amount}
            self._governed_total(state)                  # fails closed if over cap
            self._write_atomic(state)
        return key

    def commit(self, key: str, actual_cpu_h: float, record: dict) -> dict:
        """Replace the reservation with the ACTUAL governed cost, then re-gate."""
        actual = self._validate(actual_cpu_h, "actual cell CPU-h")
        with _Lock(self.path):
            state = self._read()
            res = state.get("open_reservations", {}).pop(key, None)
            if res is None:
                raise BudgetRefusal(f"no open reservation {key}")
            role = res["role"]
            prev = self._validate(
                state.setdefault("committed_cpu_h_by_role", {}).get(role, 0.0),
                f"committed CPU-h for {role}")
            state["committed_cpu_h_by_role"][role] = self._validate(
                prev + actual, f"updated committed CPU-h for {role}")
            state.setdefault("completed_cells", {})[str(res["cell_id"])] = record
            cap = self._governed_total(state)            # re-gate AFTER the cell
            self._write_atomic(state)
        return cap

    def release(self, key: str) -> None:
        """Return an unused reservation to the global budget (torn cell)."""
        with _Lock(self.path):
            state = self._read()
            if state.get("open_reservations", {}).pop(key, None) is not None:
                self._write_atomic(state)
