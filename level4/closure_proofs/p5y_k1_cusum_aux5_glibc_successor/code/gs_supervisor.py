"""The new-glibc successor supervisor. NON-CERTIFYING.

It is the frozen ProvenanceSupervisor (admission, drain, cap invariant, reconciliation, keeper, authorization-born
genesis, envelope binding: all unchanged code) with one added refusal: a campaign whose universe contains a carry-over
cell never opens a ledger. Production starts only through `gs_entry.py launch`.

  python gs_supervisor.py --synthetic-spec CFG.json [--keep]                       synthetic successor (acceptance)
  python gs_supervisor.py --synthetic-spec CFG.json --predecessor-shape [--keep]   synthetic terminal predecessor fixture
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import gs_schema as GS                                                      # noqa: E402
import prod_supervisor as PS                                                # noqa: E402
from gs_authorization import load_authz                                     # noqa: E402
from gs_spec import check_universe, synthetic_drift_spec, synthetic_spec    # noqa: E402
from prod_common import Refusal                                             # noqa: E402
from prov_supervisor import ProvenanceSupervisor, synthetic_authz           # noqa: E402


class SuccessorSupervisor(ProvenanceSupervisor):
    def _run_locked(self, lock) -> int:
        check_universe(self.spec.cell_indices)
        return super()._run_locked(lock)


def synthetic_successor_authz(spec, cfg: dict):
    cp = json.loads(Path(cfg["checkpoint_path"]).read_text())
    return load_authz(spec, cp, auth_path=cfg["authorization_path"], hash_path=cfg["authorization_hash_path"],
                      cs_path=cfg["countersignature_path"])


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="new-glibc successor supervisor (synthetic acceptance entry)")
    ap.add_argument("--synthetic-spec", required=True)
    ap.add_argument("--predecessor-shape", action="store_true")
    ap.add_argument("--keep", action="store_true")
    a = ap.parse_args(argv)
    cfg = json.loads(Path(a.synthetic_spec).read_text())
    if a.predecessor_shape and not cfg.get("predecessor_shape"):
        print(json.dumps({"event": "REFUSED", "code": "FIXTURE", "detail": "config is not a predecessor-shape fixture"}))
        return PS.EXIT_REFUSED
    try:
        spec = synthetic_drift_spec(cfg) if cfg.get("drift_after_records") else synthetic_spec(cfg)
    except Refusal as r:
        PS.log("REFUSED", code=r.code, detail=r.detail)
        return PS.EXIT_REFUSED
    if a.keep:
        extra = ["--predecessor-shape"] if a.predecessor_shape else []
        return PS.keep([sys.executable, "-B", str(Path(__file__).resolve()), "--synthetic-spec", a.synthetic_spec, *extra],
                       root=spec.root)
    if a.predecessor_shape:
        return ProvenanceSupervisor(spec, authz_loader=lambda: synthetic_authz(spec, cfg)).run()
    return SuccessorSupervisor(spec, authz_loader=lambda: synthetic_successor_authz(spec, cfg)).run()


if __name__ == "__main__":
    raise SystemExit(main())
