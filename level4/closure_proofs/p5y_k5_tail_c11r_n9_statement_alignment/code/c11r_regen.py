"""C11R Repair E -- regenerate ALL pre-result evidence from scratch, in dependency order.

No artifact is kept because it previously passed. Each producer runs in a fresh process, in the
order its inputs require, and the driver stops at the first non-zero exit. The final step is
c11r_status.py, which recomputes every artifact's producer, closure and input hashes against the
tree and refuses on any staleness or contradiction.

This driver never launches c11r_compare.py (the post-seal comparator) or c11r_runs.py (target
execution) or c11r_qualify.py (target qualification). The firewall scanner checks the first of
those mechanically; the other two are simply absent from ORDER.
"""
from __future__ import annotations

import os
import pathlib
import subprocess
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent
ORDER = [
    "c11r_b0.py",          # predecessor state, LOCAL and REMOTE main refs
    "c11r_errata.py",      # the corrected record, first
    "c11r_table.py",       # statement table (no magnitude) + quarantine
    "c11r_equiv.py",       # comparator controls, from the statement table
    "c11r_validate.py",    # V1-V16, non-target block only
    "c11r_policy.py",      # the frozen configuration, from geometry and non-target cost
    "c11r_gate.py",        # binds the statement table and the policy
    "c11r_firewall.py",    # AST proof of the original-value firewall
    "c11r_mutations.py",   # reads statements, policy, gate, validation, firewall
    "c11r_status.py",      # freshness, contradictions, pre-result state -- last
]
NEVER = ("c11r_runs.py", "c11r_qualify.py", "c11r_compare.py")


def main() -> int:
    assert not set(ORDER) & set(NEVER)
    env = {**os.environ, "PYTHONINTMAXSTRDIGITS": "0"}
    log = []
    for mod in ORDER:
        t = time.time()
        r = subprocess.run([sys.executable, "-B", str(HERE / mod)], cwd=str(HERE.parent),
                           env=env, capture_output=True, text=True)
        dt = round(time.time() - t, 1)
        tail = (r.stdout.strip().splitlines() or [""])[-1][:110]
        log.append((mod, r.returncode, dt))
        print(f"  exit {r.returncode}  {dt:8.1f}s  {mod:20s} {tail}", flush=True)
        if r.returncode != 0:
            print(r.stdout[-3000:])
            print(r.stderr[-3000:])
            print(f"\nREGEN HALTED at {mod}: exit {r.returncode}")
            return 1
    print(f"\nREGEN COMPLETE: {len(ORDER)} producers, all exit 0, "
          f"{sum(x[2] for x in log):.0f}s total")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
