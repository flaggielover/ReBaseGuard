"""SR production driver -- cap-authorized, driver-bound successor.

Modes
  --verify-only  run every pre-production gate and report (DEFAULT)
  --dry-run      gates + enumerate the exact frozen campaign plan, NO science
  --produce      refuses unless the checkpoint enables production (it does not)

This driver performs NO scientific computation in any mode available here.
It is the enforcement surface for the frozen campaign; the scientific kernel is
the accepted O9 backend, which it does not modify.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import gates                                                        # noqa: E402
from gates import GateFailure                                       # noqa: E402
from ledger import CapLedger, CellStore, CapExceeded                # noqa: E402

NS = HERE.parent


def cell_ids(cp: dict) -> list[int]:
    """The exact frozen 316-cell executable cover, in frozen order."""
    return list(cp["cover"]["cell_ids"])


def shard_cells(ids: list, n_shards: int) -> list[list]:
    """Frozen floor rule -- the same partition rule as sr_universe.shard."""
    N = len(ids)
    out = []
    for k in range(n_shards):
        out.append(ids[(k * N) // n_shards:((k + 1) * N) // n_shards])
    return out


def run_gates(cp: dict, *, repo=None, env=None, cores=None) -> dict:
    """Every gate, in order. Any failure raises GateFailure -- fail closed."""
    return {
        "A_repository": gates.gate_repository(cp, repo=repo),
        "B_runtime": gates.gate_runtime(cp),
        "C_threads": gates.gate_threads(cp, env=env),
        "D_topology": gates.gate_topology(cp, cores=cores),
        "E_scope": gates.gate_scope(cp),
    }


def build_plan(cp: dict, gate_report: dict) -> dict:
    ids = cell_ids(cp)
    scope = cp["frozen_scope"]
    if len(ids) != scope["sr_cells"]:
        raise GateFailure(f"cover has {len(ids)} cells != {scope['sr_cells']}")
    if len(set(ids)) != len(ids):
        raise GateFailure("duplicate cell id in the frozen cover")
    top = cp["worker_topology"]
    shards = shard_cells(ids, top["workers"])
    flat = [c for s in shards for c in s]
    if flat != ids:
        raise GateFailure("shard partition is not exact")
    per_cell = scope["obligations_per_cell"]
    total_ob = len(ids) * per_cell + scope["far_field_units"]
    if total_ob != scope["obligations"]:
        raise GateFailure(
            f"obligation conservation: {len(ids)}x{per_cell}+{scope['far_field_units']}"
            f" = {total_ob} != {scope['obligations']}")
    contracts = cp["census"]["certified_contracts"]
    return {
        "cells": len(ids),
        "cell_ids_first": ids[:5], "cell_ids_last": ids[-5:],
        "workers": top["workers"],
        "core_assignment": gate_report["D_topology"]["core_assignment"],
        "shards": [{"worker": k, "core": gate_report["D_topology"]["core_assignment"][k],
                    "n_cells": len(s), "first": s[0] if s else None,
                    "last": s[-1] if s else None} for k, s in enumerate(shards)],
        "shard_sizes": [len(s) for s in shards],
        "exact_partition": True,
        "obligations_per_cell": per_cell,
        "far_field_units": scope["far_field_units"],
        "total_obligations": total_ob,
        "contracts_per_cell": contracts,
        "panel_contract_evaluations":
            contracts * len(ids) * scope["panels"],
        "backend": cp["backend"]["accepted"],
        "precision_bits": scope["precision_bits"],
        "scientific_computation_performed": False,
    }


def verify_final_assembly(cp: dict, store: CellStore, ledger: CapLedger) -> dict:
    """Post-run verifier. Enforces exact conservation before a campaign is closed."""
    ids = cell_ids(cp)
    done = store.completed()
    scope = cp["frozen_scope"]
    problems = []
    missing = [c for c in ids if c not in done]
    extra = [c for c in done if c not in ids]
    if missing:
        problems.append(f"missing {len(missing)} cells, e.g. {missing[:5]}")
    if extra:
        problems.append(f"{len(extra)} cells outside the frozen cover: {extra[:5]}")
    paths = list(store.cells.glob("sr_CELL_*_256.json"))
    if len(paths) != len(set(p.name for p in paths)):
        problems.append("duplicate cell record files")
    ob = sum(r.get("obligations_completed", 0) for r in done.values())
    expected_ob = scope["obligations"] - scope["far_field_units"]
    if done and ob != expected_ob:
        problems.append(f"obligation conservation {ob} != {expected_ob} (pre far-field)")
    ident = {store.identity_of(r) != store.identity for r in done.values()}
    if True in ident:
        problems.append("producer/runtime identity inconsistency among cells")
    charged = ledger.charged_cpu_h()
    if charged > cp["compute_cap"]["cap_cpu_h"]:
        problems.append(f"aggregate cost {charged:.3f} > cap "
                        f"{cp['compute_cap']['cap_cpu_h']}")
    return {"cells_expected": len(ids), "cells_committed": len(done),
            "complete": len(done) == len(ids) and not problems,
            "obligations_committed": ob, "obligations_expected": expected_ob,
            "charged_cpu_h": charged, "cap_cpu_h": cp["compute_cap"]["cap_cpu_h"],
            "problems": problems}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--checkpoint", default=None)
    ap.add_argument("--mode", choices=("verify-only", "dry-run", "produce"),
                    default="verify-only")
    ap.add_argument("--work-dir", default=None)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)

    cp = gates.load_checkpoint(a.checkpoint)
    report = {"checkpoint_sha256": cp["checkpoint_sha256"], "mode": a.mode}

    # Unconditional: a disabled campaign is refused before ANY environment check,
    # so no environmental accident can ever make production reachable.
    if a.mode == "produce" and not cp["production_state"]["production_enabled"]:
        report["admitted"] = False
        report["production_performed"] = False
        report["refusal"] = (
            "production_enabled is false in the frozen checkpoint. This driver "
            "refuses to perform result-bearing work. Enabling production requires "
            "a NEW adjudicated checkpoint, not a flag.")
        print(json.dumps(report, indent=1, sort_keys=True))
        return 3
    try:
        report["gates"] = run_gates(cp)
    except GateFailure as e:
        report["gate_failure"] = str(e)
        report["admitted"] = False
        print(json.dumps(report, indent=1, sort_keys=True))
        return 2

    if a.mode in ("dry-run", "produce"):
        report["plan"] = build_plan(cp, report["gates"])

    if a.mode == "produce":
        report["refusal"] = "unreachable under the frozen pre-result checkpoint"
        report["admitted"] = False
        print(json.dumps(report, indent=1, sort_keys=True))
        return 3

    if a.work_dir:
        cap = cp["compute_cap"]
        ledger = CapLedger(Path(a.work_dir) / "cap_ledger.json",
                           cap["cap_cpu_h"], cap["overhead_factor"],
                           cap["cusum_cpu_h"],
                           reserve_cpu_h=cap["per_cell_reservation_cpu_h"])
        store = CellStore(Path(a.work_dir), cp["campaign_identity"])
        report["resume"] = store.resume_plan(cell_ids(cp))
        report["cap"] = {"charged_cpu_h": ledger.charged_cpu_h(),
                         "remaining_cpu_h": ledger.remaining_cpu_h(),
                         "cap_cpu_h": ledger.cap}
        report["final_assembly"] = verify_final_assembly(cp, store, ledger)

    report["admitted"] = True
    report["production_performed"] = False
    print(json.dumps(report, indent=1, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
