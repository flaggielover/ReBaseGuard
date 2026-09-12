"""SYNTHETIC-CONTROL child for the PS1 adapter: the SAME produce_entry.run() path (PS1 preflight, OpsBudget over the
PS1 launcher, PS1 run_production_cells(poll_timeout=None), the real persistent pinned PS1 pool) with ONLY the science
replaced by result-free synthetic spins. Refuses to run under the PRODUCTION contract.

Control file (env RBG_SYNTH_CONTROL): {"spin_s": 0.2, "cells": [0,1,2], "cores": [16,17],
  "fail": {"5": [1]}, "die": {"4": [1]}, "hang": {"3": [1]}}   (attempt numbers, 1-based, per first cell of a group)
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

OPS = Path(__file__).resolve().parents[1] / "ops"
sys.path.insert(0, str(OPS))
from opscommon import host_spec, load_contract, prod_ns     # noqa: E402
import ledger_ops as LO                                     # noqa: E402
import produce_entry as PE                                  # noqa: E402


def attempt_no(d: Path, cell: int) -> int:
    n = 1
    while True:
        try:
            os.close(os.open(str(d / f"attempt-{cell:04d}-{n}"), os.O_CREAT | os.O_EXCL))
            return n
        except FileExistsError:
            n += 1


def install(PL, ctl_path: Path, runtime_dir: Path):
    ctl = json.loads(ctl_path.read_text())
    adir = ctl_path.parent / "attempts"
    adir.mkdir(exist_ok=True)
    submit0, get0 = PL.Pool.submit, PL.Pool.get

    def submit(self, slot, task):
        cells = task["cells"]
        n = attempt_no(adir, cells[0])
        hit = lambda k: any(n in ctl.get(k, {}).get(str(c), []) for c in cells)        # noqa: E731
        syn = {"task_id": task["task_id"], "kind": "SYNTHETIC_SPIN", "cells": cells,
               "seconds": 10 ** 6 if hit("hang") else float(ctl.get("spin_s", 0.2)), "verdict": not hit("fail")}
        submit0(self, slot, syn)
        if hit("die"):
            slot["proc"].kill()

    def get(self, timeout=None):
        task, res = get0(self, timeout)
        if res.get("synthetic") and res.get("ok"):
            res["results"] = {str(c): {"cell_id": c, "ok": True, "synthetic": True, "successor_id": f"SYNTHETIC-{c}",
                                       "scientific_content_hash": hashlib.sha256(f"SYNTHETIC-CONTROL-PS1:{c}".encode()).hexdigest(),
                                       "B_cover_ratio": {}, "cpu_seconds": float(ctl.get("spin_s", 0.2)),
                                       "evidence": {"t5": {"path": "SYNTHETIC_CONTROL_NOT_SCIENCE",
                                                           "sha256": hashlib.sha256(
                                                               f"SYNTHETIC-CONTROL-LIFECYCLE:{c}".encode()).hexdigest()}},
                                       "precision_bits": 256} for c in task["cells"]}
        return task, res
    PL.Pool.submit, PL.Pool.get = submit, get
    PL._verified = lambda r, cell, task: bool(isinstance(r, dict) and r.get("synthetic") and r.get("cell_id") == cell)

    def hook(pf):
        h = pf["auth"]["hosts"][pf["role"]]
        h["core_assignment"] = list(ctl["cores"])
        h["workers"] = len(ctl["cores"])
        h["work_dir"] = str(runtime_dir / "work")
        h["evidence_dir"] = str(runtime_dir / "evidence")
        want = list(ctl["cells"])
        pf["pending"] = [c for c in pf["pending"] if c in want]
        pf["groups"] = [[c for c in g if c in want] for g in pf["groups"] if any(c in want for c in g)]
    return hook


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--contract", required=True)
    ap.add_argument("--role", required=True)
    ap.add_argument("--run-id", required=True)
    a = ap.parse_args(argv)
    c = load_contract(a.contract)
    if c["mode"] != "SYNTHETIC_CONTROL":
        print("REFUSE: synthetic_entry never runs under the PRODUCTION contract")
        return PE.EXIT_REFUSED
    spec = host_spec(c, a.role)
    drv = str(prod_ns(spec) / "driver")
    sys.path.insert(0, drv)
    import production_launcher as PL                      # the module object PE.run will import
    hook = install(PL, Path(os.environ["RBG_SYNTH_CONTROL"]), Path(spec["runtime_dir"]))
    try:
        PE.run(c, a.role, a.run_id, preflight_kwargs={"role": a.role}, before_run=hook)
    except LO.ScientificHalt as exc:
        print(f"HALT {exc}", flush=True)
        return PE.EXIT_HALT
    return PE.EXIT_OK


if __name__ == "__main__":
    raise SystemExit(main())
