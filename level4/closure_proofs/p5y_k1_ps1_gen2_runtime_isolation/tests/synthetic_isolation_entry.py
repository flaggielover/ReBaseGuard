"""SYNTHETIC-CONTROL child for the generation-2 RUNTIME ISOLATION successor (and its negative control).

Same produce_entry.run() path as genuine production (PS1 preflight with the fresh-interpreter probe,
OpsBudget, the bound ps1_cellseq_launcher.run_production_cells, the real pinned pool). Only the
science is replaced by per-cell synthetic spins that write real durable cell_done markers.

DIFFERENCE FROM THE PREDECESSOR HARNESS (the masking defect): the predecessor hook rewrote the
authorization work_dir/evidence_dir to the contract runtime_dir, i.e. it performed the very path
alignment the GENUINE path never performs. Here the authorization is made to name a DECOY legacy
root -- exactly like the frozen PS1 authorization names the generation-1 root -- and the hook never
touches work_dir or evidence_dir. Whether the run is isolated is then decided by the ops under test.

Env: RBG_SYNTH_CONTROL=<control.json>, RBG_OPS_ROOT=<ops namespace under test>.
Control: {"spin_s":2,"cells":[..],"cores":[..],"die":{"<cell>":[attempt..]},
          "decoy_work_dir":..., "decoy_evidence_dir":..., "kill_launcher_after_cell":n, ...}
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

OPS_NS = Path(os.environ["RBG_OPS_ROOT"])
sys.path.insert(0, str(OPS_NS / "ops"))
from opscommon import host_spec, load_contract, prod_ns          # noqa: E402
import ledger_ops as LO                                          # noqa: E402
import produce_entry as PE                                       # noqa: E402


def attempt_no(d: Path, cell: int) -> int:
    n = 1
    while True:
        try:
            os.close(os.open(str(d / f"attempt-{cell:04d}-{n}"), os.O_CREAT | os.O_EXCL))
            return n
        except FileExistsError:
            n += 1


def install(PL, ctl_path: Path):
    ctl = json.loads(ctl_path.read_text())
    adir = ctl_path.parent / "attempts"
    adir.mkdir(exist_ok=True)
    submit0 = PL.Pool.submit
    load0 = PL.load_production_authorization

    def load_production_authorization(*a, **kw):
        auth = load0(*a, **kw)                       # frozen file + frozen hash check, unchanged
        for role in auth["hosts"]:
            h = auth["hosts"][role]
            h["work_dir"] = ctl["decoy_work_dir"]              # emulate: authorization names a legacy root
            h["evidence_dir"] = ctl["decoy_evidence_dir"]
            # HOST ADAPTATION ONLY (harness host != authorised host): the interpreter and HOME the
            # authorization names do not exist here; use the contract-bound interpreter running us.
            h["python"] = sys.executable
            h["environment"] = dict(h["environment"], HOME=os.environ.get("HOME", "/root"))
        return auth

    def submit(self, slot, task):
        cells = task["cells"]
        syn = dict(task, kind="SYNTHETIC_CELLSEQ", seconds=float(ctl.get("spin_s", 0.2)))
        # attempts are counted PER declared-death cell (not per group leader): a restarted group
        # that no longer starts with the same cell must still see its true attempt number
        for c in cells:
            if str(c) in ctl.get("die", {}) and attempt_no(adir, c) in ctl["die"][str(c)] \
                    and "die_on_cell" not in syn:
                syn["die_on_cell"] = c
        for k in ("kill_launcher_after_cell", "kill_launcher_before_cell"):
            if ctl.get(k) is not None:
                syn[k] = int(ctl[k])
        submit0(self, slot, syn)

    PL.load_production_authorization = load_production_authorization
    PL.Pool.submit = submit
    PL._verified = lambda r, cell, task: bool(
        isinstance(r, dict) and r.get("synthetic") and r.get("cell_id") == cell)

    def hook(pf):
        h = pf["auth"]["hosts"][pf["role"]]
        h["core_assignment"] = list(ctl["cores"])
        h["workers"] = len(ctl["cores"])
        want = list(ctl["cells"])
        pf["pending"] = [c for c in pf["pending"] if c in want]
        pf["groups"] = [[c for c in g if c in want] for g in pf["groups"] if any(c in want for c in g)]
        if ctl.get("drain_after_completed") is not None:
            pf["drain_after_completed"] = int(ctl["drain_after_completed"])
        print(f"  launcher work_dir={h['work_dir']} evidence_dir={h['evidence_dir']}", flush=True)
    return hook


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--contract", required=True)
    ap.add_argument("--role", required=True)
    ap.add_argument("--run-id", required=True)
    a = ap.parse_args(argv)
    c = load_contract(a.contract)
    if c["mode"] != "SYNTHETIC_CONTROL":
        print("REFUSE: synthetic_isolation_entry never runs under the PRODUCTION contract")
        return PE.EXIT_REFUSED
    spec = host_spec(c, a.role)
    sys.path.insert(0, str(prod_ns(spec) / "driver"))
    import ps1_cellseq_launcher as PL
    hook = install(PL, Path(os.environ["RBG_SYNTH_CONTROL"]))
    try:
        PE.run(c, a.role, a.run_id, preflight_kwargs={"role": a.role}, before_run=hook)
    except LO.ScientificHalt as exc:
        print(f"HALT {exc}", flush=True)
        return PE.EXIT_HALT
    return PE.EXIT_OK


if __name__ == "__main__":
    raise SystemExit(main())
