"""SYNTHETIC-CONTROL child: the SAME produce_entry.run() path (frozen preflight,
OpsBudget, frozen run_production_cells(poll_timeout=None), real WorkerPool with
real pinned processes) with ONLY the science callable replaced by a controllable
result-free stub. Refuses to run under the PRODUCTION contract.

Control file (env RBG_SYNTH_CONTROL):
  {"spin_s": 0.05, "fail": {"12": [1]}, "die": {"7": [1, 2]}, "hang": {"3": [1]}}
  lists are the attempt numbers (1-based, per cell) on which the action fires.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
from pathlib import Path

OPS = Path(__file__).resolve().parents[1] / "ops"
sys.path.insert(0, str(OPS))
from opscommon import OpsRefusal, host_spec, load_contract     # noqa: E402
import ledger_ops as LO                                         # noqa: E402
import produce_entry as PE                                      # noqa: E402

SIX = {v: "1" for v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
                        "NUMEXPR_NUM_THREADS", "BLIS_NUM_THREADS", "VECLIB_MAXIMUM_THREADS")}
RT = {"AWS": "d49f043755ef658a60e3c4017022ddecf0642a087a6e5bb0c1f2aefbe9721191",
      "VULTR": "c7f9fc671664a1bcfef6d2d3d93d6cc865a2a241a869f2e93f94e6e00b6489d9"}


def attempt_no(ctl_dir: Path, cell: int) -> int:
    n = 1
    while True:
        try:
            fd = os.open(str(ctl_dir / f"attempt-{cell:04d}-{n}"), os.O_CREAT | os.O_EXCL)
            os.close(fd)
            return n
        except FileExistsError:
            n += 1


def install_stub(pf):
    import worker_pool as WP
    ctl_path = Path(os.environ["RBG_SYNTH_CONTROL"])
    ctl = json.loads(ctl_path.read_text())
    ctl_dir = ctl_path.parent / "attempts"
    ctl_dir.mkdir(exist_ok=True)
    frozen = WP._run_task

    def stub(task, root, science_enabled):
        if task["kind"] != "SCIENCE":
            return frozen(task, root, science_enabled)
        assert science_enabled
        cell = int(task["cell_id"])
        n = attempt_no(ctl_dir, cell)
        if n in ctl.get("die", {}).get(str(cell), []):
            os._exit(137)
        if n in ctl.get("hang", {}).get(str(cell), []):
            time.sleep(10 ** 6)
        end = time.process_time() + float(ctl.get("spin_s", 0.05))
        x = 0
        while time.process_time() < end:
            x += 1
        if n in ctl.get("fail", {}).get(str(cell), []):
            raise RuntimeError(f"SYNTHETIC injected worker failure cell {cell} attempt {n}")
        cert = {"SYNTHETIC_CONTROL_NOT_SCIENCE": True, "cell": cell, "attempt": n}
        return {"cell_id": cell, "certificate": cert,
                "scientific_content_hash": hashlib.sha256(
                    f"SYNTHETIC-CONTROL-LIFECYCLE:{cell}".encode()).hexdigest()}

    WP._run_task = stub                          # inherited by the forked workers


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--contract", required=True)
    ap.add_argument("--role", required=True)
    ap.add_argument("--run-id", required=True)
    a = ap.parse_args(argv)
    c = load_contract(a.contract)
    if c["mode"] != "SYNTHETIC_CONTROL":
        print("REFUSE: synthetic entry never runs under the PRODUCTION contract")
        return 30
    cores = c["parent"]["cores"][a.role]
    sibs = {x: [x, x + 16] for x in cores} if a.role == "AWS" else \
        {0: [0, 1], 2: [2, 3], 4: [4, 5], 6: [6, 7]}
    kw = dict(role=a.role, env=SIX, live_hash=RT[a.role], cores=cores, siblings=sibs)
    try:
        PE.run(c, a.role, a.run_id, preflight_kwargs=kw, before_run=install_stub)
    except LO.ScientificHalt as exc:
        print(f"HALT {exc}", flush=True)
        return 20
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
