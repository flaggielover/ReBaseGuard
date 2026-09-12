"""THE ONE sanctioned invocation of the frozen production path.

It is `production_launcher.main(["--produce"])` with exactly two OPERATIONAL
differences, each closing a load-bearing lifecycle defect; nothing scientific,
no scheduling rule and no gate is changed:

  R01  `run_production_cells(pf, poll_timeout=None)`. The frozen main() uses the
       default poll_timeout=3600 s while one single-core cell costs 8-11.5 CPU-h,
       so the first result arrives hours after start and queue.Empty kills every
       run. Worker LOSS is detected by the supervisor instead.
  R02  `pf["budget"]` is the frozen GlobalBudget with release() converted into a
       TORN escrow (never a zero-charge drop), and a worker-reported/malformed
       failure raises ScientificHalt (the protocol never retries it).

Every frozen gate still runs: `production_launcher.production_preflight()` is
called unchanged, and the result-bearing loop is the frozen
`production_launcher.run_production_cells`.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from opscommon import OpsRefusal, host_spec, load_contract, prod_ns   # noqa: E402
import ledger_ops as LO                                                # noqa: E402

EXIT_OK, EXIT_HALT, EXIT_REFUSED = 0, 20, 30


def run(contract, role, run_id, *, preflight_kwargs=None, before_run=None) -> dict:
    spec = host_spec(contract, role)
    drv = prod_ns(spec) / "driver"
    if str(drv) not in sys.path:
        sys.path.insert(0, str(drv))
    # recovery generation: the bound executor is the cells-outer, per-cell-durable
    # launcher. make_ops_budget therefore scans ITS release sites (4, each exactly
    # once) rather than the frozen group-level launcher's 3.
    import ps1_cellseq_launcher as PL                              # noqa: E402
    import global_budget as GB                                     # noqa: E402
    if Path(PL.__file__).resolve().parent != drv.resolve():
        raise OpsRefusal(f"imported launcher {PL.__file__} is not the bound one under {drv}")
    pf = PL.production_preflight(**(preflight_kwargs or {}))       # EVERY frozen gate
    for t in pf["trace"]:
        print(f"  {t['status']:5s} {t['gate']}", flush=True)
    if pf["role"] != role:
        raise OpsRefusal(f"preflight role {pf['role']} != service role {role}")
    print(f"  role={pf['role']} owned={len(pf['owned'])} pending={len(pf['pending'])} "
          f"genuine_completed={pf['production']['genuine_cells_completed']}", flush=True)
    pf["budget"] = LO.make_ops_budget(GB, pf["budget"], run_id, PL.__file__)
    if before_run is not None:
        before_run(pf)                          # synthetic harness only
    out = PL.run_production_cells(pf, poll_timeout=None)
    print(json.dumps({"completed_this_run": len(out["completed"]),
                      "stopped": out["stopped"]}), flush=True)
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--contract", required=True)
    ap.add_argument("--role", required=True, choices=("AWS", "VULTR"))
    ap.add_argument("--run-id", required=True)
    a = ap.parse_args(argv)
    c = load_contract(a.contract)
    if c["mode"] != "PRODUCTION":
        print("REFUSE: produce_entry runs only under the frozen PRODUCTION contract")
        return EXIT_REFUSED
    try:
        run(c, a.role, a.run_id)
    except LO.ScientificHalt as exc:
        print(f"HALT {exc}", flush=True)
        return EXIT_HALT
    return EXIT_OK


if __name__ == "__main__":
    raise SystemExit(main())
