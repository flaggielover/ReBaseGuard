"""C11R Repair E -- regenerate ALL pre-result evidence from scratch, in dependency order.

No artifact is kept because it previously passed. Each producer runs in a fresh process, in the
order its inputs require, and the driver stops at the first non-zero exit. The final step is
c11r_status.py, which recomputes every artifact's producer, closure and input hashes against the
tree and refuses on any staleness or contradiction.

This driver never launches c11r_compare.py (the post-seal comparator) or c11r_runs.py (target
execution) or c11r_qualify.py (target qualification). The firewall scanner checks the first of
those mechanically; the other two are simply absent from ORDER. The qualifier's PURE, non-target
self-test runs inside c11r_status.py; its main() is never called here.

Revision 3 adds the committed non-target cost measurement (c11r_cost.py, ~13 minutes; it must run
alone, and it refuses if any other campaign worker is running) and the value-based leak check,
which runs after every artifact it scans exists and before the status report.
"""
from __future__ import annotations

import os
import pathlib
import subprocess
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import c11r_common as C  # noqa: E402

ORDER = [
    ("c11r_b0.py",),                       # predecessor state, LOCAL and REMOTE main refs
    ("c11r_errata.py",),                   # the corrected record, first
    ("c11r_table.py",),                    # statement table (no magnitude) + quarantine
    ("c11r_equiv.py",),                    # statement-level comparator controls
    ("c11r_validate.py",),                 # V1-V17, non-target block only
    ("c11r_cost.py",),                     # committed non-target cost measurement, alone
    ("c11r_policy.py",),                   # the frozen configuration, from the cost artifact
    ("c11r_gate.py",),                     # binds the statement table, policy and toolchain
    ("c11r_firewall.py",),                 # load-path dataflow proof of the firewall
    ("c11r_mutations.py",),                # production guards under mutation
    ("c11r_table.py", "--leak-check"),     # value-based leak check over everything above
    ("c11r_status.py",),                   # freshness, contradictions, pre-result state -- last
]
NEVER = ("c11r_runs.py", "c11r_qualify.py", "c11r_compare.py")


def main() -> int:
    assert not {step[0] for step in ORDER} & set(NEVER)
    # pre-flight: nothing else running, nothing authorised, no target output anywhere
    pre = {"no_campaign_worker_running": not C.classified_processes()["campaign_workers"],
           "no_authorization": not (C.NS / "config" / "C11R_AUTHORIZATION.json").exists(),
           "no_evidence_runs": not (C.NS / "evidence" / "runs").exists(),
           "no_comparison": not (C.NS / "evidence" / "comparison").exists(),
           "no_qualification": not (C.NS / "evidence" / "qualification").exists()}
    print(f"pre-flight: {pre}", flush=True)
    if not all(pre.values()):
        print("REGEN REFUSED: pre-flight failed")
        return 1
    env = {**os.environ, "PYTHONINTMAXSTRDIGITS": "0"}
    log = []
    for step in ORDER:
        mod, args = step[0], list(step[1:])
        t = time.time()
        r = subprocess.run([sys.executable, "-B", str(HERE / mod), *args], cwd=str(HERE.parent),
                           env=env, capture_output=True, text=True)
        dt = round(time.time() - t, 1)
        tail = (r.stdout.strip().splitlines() or [""])[-1][:110]
        log.append((mod, r.returncode, dt))
        print(f"  exit {r.returncode}  {dt:8.1f}s  {' '.join(step):32s} {tail}", flush=True)
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
