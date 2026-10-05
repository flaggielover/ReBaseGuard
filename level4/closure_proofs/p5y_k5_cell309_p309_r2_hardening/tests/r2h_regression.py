#!/usr/bin/env python3
"""Regression: r2's own static and protocol gates on a replica (post-synthetic-freeze), for the baseline and the
hardened package side by side.  A hardening that trips r2's scanner, static check, QC11 flows, D5 controls or host
tests would show here as a difference.

  python3 r2h_regression.py --replica R --scratch S --out FILE

Runs, exactly as r2's runner defines them where it defines them (python -I -S -B):
  QC11 tests/test_p309_exactly_once.py, QC12 code/p309_static_check.py,
  QC-D5 tests/test_p309_d5_exception.py + tests/test_p309_site_backstop.py + code/p309_scan_pins.py --list,
  and r2's host / static-control tests (tests/test_p309_host.py, test_p309_host_controls.py,
  test_p309_static_controls.py).
Nothing evaluates a target; the driver is exercised only in TEST sandboxes by r2's own tests.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path

NS2 = "level4/closure_proofs/p5y_k5_cell309_p309_r2"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--replica", required=True)
    ap.add_argument("--scratch", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    fns = Path(a.replica) / NS2
    evid = Path(a.scratch) / "evidence"
    evid.mkdir(parents=True, exist_ok=True)
    env = {k: v for k, v in os.environ.items() if not k.startswith(("PYTHON", "P309_"))}
    env.update({"P309_SCRATCH_ROOT": str(a.scratch), "P309_EVIDENCE_DIR": str(evid)})
    py = sys.executable
    plan = [("QC11", [py, "-I", "-S", "-B", "tests/test_p309_exactly_once.py"]),
            ("QC12", [py, "-I", "-S", "-B", "code/p309_static_check.py"]),
            ("QC_D5_controls", [py, "-I", "-S", "-B", "tests/test_p309_d5_exception.py"]),
            ("QC_D5_backstop", [py, "-I", "-S", "-B", "tests/test_p309_site_backstop.py"]),
            ("QC_D5_pins", [py, "code/p309_scan_pins.py", "--list"])]
    for t in ("test_p309_host.py", "test_p309_host_controls.py", "test_p309_static_controls.py"):
        if (fns / "tests" / t).exists():
            plan.append((t, [py, "-B", "tests/" + t]))
    res = {"schema": "P309_R2H_REGRESSION/1", "replica_head": subprocess.run(
        ["git", "-C", a.replica, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip(),
        "runner_sha256": hashlib.sha256((fns / "code" / "p309_qualify.py").read_bytes()).hexdigest(), "runs": {}}
    for name, cmd in plan:
        t0 = time.time()
        p = subprocess.run(cmd, cwd=str(fns), capture_output=True, text=True, env=env, timeout=4 * 3600)
        tail = p.stdout[-4000:]
        res["runs"][name] = {"rc": p.returncode, "wall_s": round(time.time() - t0, 1), "stdout_tail": tail,
                             "stderr_tail": p.stderr[-1500:],
                             "fail_lines": [l for l in p.stdout.splitlines() if l.startswith("[FAIL]") or "STALE" in l
                                            or "NOT LISTED" in l][:20]}
        Path(a.out).write_text(json.dumps(res, indent=1, sort_keys=True) + "\n")
        print(f"{name}: rc={p.returncode} ({res['runs'][name]['wall_s']} s)", flush=True)
    flows = evid / "fc6" / "EXACTLY_ONCE_FLOWS.json"
    if flows.exists():
        d = json.loads(flows.read_text())
        res["qc11_table"] = {"all_pass": d.get("all_pass"), "flows": d.get("flows"),
                             "failed": [k for k, x in d.get("results", {}).items() if x.get("pass") is not True]}
    res["pins_all_current"] = "P309 SCAN PINS: all current" in res["runs"]["QC_D5_pins"]["stdout_tail"]
    Path(a.out).write_text(json.dumps(res, indent=1, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
