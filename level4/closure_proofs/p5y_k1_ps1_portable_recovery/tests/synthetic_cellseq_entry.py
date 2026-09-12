"""SYNTHETIC-CONTROL child for the PORTABLE RECOVERY successor.

Same produce_entry.run() path (PS1 preflight, OpsBudget, the recovery launcher's
run_production_cells, the real persistent pinned pool) with ONLY the science replaced by
per-cell synthetic spins that emit the real durable cell_done_XXXX.json markers.

Refuses to run under the PRODUCTION contract. Records are stamped synthetic=True, which the
PRODUCTION _verified() rejects; only the patched _verified below accepts them.

Control: {"spin_s":0.2,"cells":[...],"cores":[16,17],"die":{"<cell>":[attempt,...]}}
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

ADAPTER = Path(__file__).resolve().parents[1]
OPS = ADAPTER / "ops"
sys.path.insert(0, str(OPS))
sys.path.insert(0, str(Path("/home/ubuntu/work/ReBaseGuard-ps1-ops/level4/closure_proofs/"
                            "p5y_k1_ps1_lifecycle_adapter/ops")))
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


def install(PL, ctl_path: Path, runtime_dir: Path):
    ctl = json.loads(ctl_path.read_text())
    adir = ctl_path.parent / "attempts"
    adir.mkdir(exist_ok=True)
    submit0 = PL.Pool.submit

    def submit(self, slot, task):
        cells = task["cells"]
        n = attempt_no(adir, cells[0])
        die = None
        for c in cells:
            if n in ctl.get("die", {}).get(str(c), []):
                die = c
        syn = dict(task)
        syn["kind"] = "SYNTHETIC_CELLSEQ"
        syn["seconds"] = float(ctl.get("spin_s", 0.2))
        if die is not None:
            syn["die_on_cell"] = die
        submit0(self, slot, syn)

    PL.Pool.submit = submit
    PL._verified = lambda r, cell, task: bool(
        isinstance(r, dict) and r.get("synthetic") and r.get("cell_id") == cell)

    def hook(pf):
        h = pf["auth"]["hosts"][pf["role"]]
        h["core_assignment"] = list(ctl["cores"])
        h["workers"] = len(ctl["cores"])
        h["work_dir"] = str(runtime_dir / "work")
        h["evidence_dir"] = str(runtime_dir / "evidence")
        want = list(ctl["cells"])
        pf["pending"] = [c for c in pf["pending"] if c in want]
        pf["groups"] = [[c for c in g if c in want] for g in pf["groups"] if any(c in want for c in g)]
        if ctl.get("drain_after_completed") is not None:
            pf["drain_after_completed"] = int(ctl["drain_after_completed"])
    return hook


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--contract", required=True)
    ap.add_argument("--role", required=True)
    ap.add_argument("--run-id", required=True)
    a = ap.parse_args(argv)
    c = load_contract(a.contract)
    if c["mode"] != "SYNTHETIC_CONTROL":
        print("REFUSE: synthetic_cellseq_entry never runs under the PRODUCTION contract")
        return PE.EXIT_REFUSED
    spec = host_spec(c, a.role)
    sys.path.insert(0, str(prod_ns(spec) / "driver"))
    sys.path.insert(0, str(ADAPTER / "driver"))
    import ps1_cellseq_launcher as PL
    sys.modules["production_launcher"] = PL        # PE.run imports it by this name
    hook = install(PL, Path(os.environ["RBG_SYNTH_CONTROL"]), Path(spec["runtime_dir"]))
    try:
        PE.run(c, a.role, a.run_id, preflight_kwargs={"role": a.role}, before_run=hook)
    except LO.ScientificHalt as exc:
        print(f"HALT {exc}", flush=True)
        return PE.EXIT_HALT
    return PE.EXIT_OK


if __name__ == "__main__":
    raise SystemExit(main())
