"""PS1 LIVE systemd acceptance (RESULT-FREE). OPERATOR-RUN on AWS: it uses the frozen PS1 contract's privilege
prefix (hosts.AWS.launch_prefix, inherited unchanged from the audited lifecycle contract), which the automated
tooling of this round cannot use.

It builds a SYNTHETIC production root under WORK: a fresh local clone of the PS1 authorization tag (own .git and
runtime exclude policy) and a SYNTHETIC_CONTROL contract derived from the frozen PS1 contract with service_mode=true
and the contract's own privilege prefix, so each run goes through the exact `prodctl start` -> systemd-run rendering,
the transient SYSTEM unit, the cgroup CPU accounting and ExecStopPost settlement used in production, while the
science is replaced by synthetic spins (tests/synthetic_entry.py). Cores 16,17 (SMT siblings) are used.

  prepare --work W            build the clone and the synthetic contract; prints the exact operator commands
  report  --work W            collect ledger / run records / journal CPU / unit state as JSON evidence
Scenario (operator, separate shells): start -> wait for completion -> status; start with {"hang": {"0": [1]}} ->
prodctl stop -> status (settled by SUPERVISOR_FINAL or EXECSTOPPOST_CGROUP) -> start again -> completes.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

ADAPTER = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ADAPTER / "ops"))
sys.path.insert(0, str(ADAPTER / "tests"))
import opscommon as OC                                           # noqa: E402
import conftest as CF                                            # noqa: E402


def prepare(work: Path, control: dict) -> dict:
    if work.exists() and any(work.iterdir()):
        raise SystemExit(f"{work} must be empty")
    work.mkdir(parents=True, exist_ok=True)
    prefix = json.loads(OC.CONTRACT_PATH.read_text())["hosts"]["AWS"]["launch_prefix"]
    root = CF.make_clone(work / "clone")
    cp = CF.synthetic_contract(work, root, control)
    c = json.loads(cp.read_text())
    c["synthetic"]["service_mode"] = True
    for s in c["hosts"].values():
        s["launch_prefix"] = prefix
        s["user"] = os.environ.get("USER", "ubuntu")
    cp.write_text(json.dumps(c, indent=1, sort_keys=True))
    OC.load_contract(cp)                                         # guard: never a production path
    ops = ADAPTER / "ops/prodctl.py"
    return {"contract": str(cp), "clone": str(root), "privilege_prefix_from_contract": prefix,
            "operator_commands": [f"{sys.executable} {ops} {x} --contract {cp} --role AWS" for x in ("start", "status", "stop")]}


def report(work: Path) -> dict:
    c = json.loads((work / "synthetic_contract.json").read_text())
    rt = Path(c["hosts"]["AWS"]["runtime_dir"])
    led = json.loads((work / "clone/level4/closure_proofs/p5y_k1_ps1_production/production/PRODUCTION_LEDGER.json").read_text())
    ops = led["operational_lifecycle"]
    runs = {}
    for f in sorted((rt / "runs").glob("*.json")):
        rec = json.loads(f.read_text())
        s = ops["runs"].get(rec["run_id"], {}).get("settlement") or {}
        unit, inv = rec.get("unit"), rec.get("invocation_id")
        runs[rec["run_id"]] = {"status": rec.get("status"), "reason": rec.get("reason"), "unit": unit,
                               "evidence": s.get("evidence"), "u_usec_final": s.get("u_usec_final"),
                               "journal_cpu_usec": OC.journal_cpu_usage_usec(unit, inv) if unit and inv else None,
                               "unit_state": OC.unit_state(unit) if unit else None}
    return {"completed": sorted(int(x) for x in led["completed_cells"]), "open_reservations": sorted(led["open_reservations"]),
            "committed": led["committed_cpu_h_by_role"], "halt": ops["halt"], "torn": ops["torn_attempts"], "runs": runs}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=("prepare", "report"))
    ap.add_argument("--work", required=True)
    ap.add_argument("--control", default='{"spin_s": 2.0, "cells": [0, 1, 2, 3, 4], "cores": [16, 17]}')
    a = ap.parse_args()
    out = prepare(Path(a.work), json.loads(a.control)) if a.cmd == "prepare" else report(Path(a.work))
    print(json.dumps(out, indent=1, default=str))


if __name__ == "__main__":
    main()
