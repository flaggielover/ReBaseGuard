"""Generate ops/supervisor.py for the recovery successor.

ONE asserted substitution: a deterministic durable-marker reconciliation pass runs BEFORE
LO.settle_run() classifies any open reservation as torn.

Measured justification: on WORKER_LOST the supervisor calls kill_all() -> child.kill(),
i.e. SIGKILL. The launcher's finally/atexit never run, so launcher-side reconciliation
cannot be made correct by any poll interval. The supervisor therefore owns it.
"""
import hashlib
import sys
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
SRC = Path("/home/ubuntu/work/ReBaseGuard-ps1-ops/level4/closure_proofs/"
           "p5y_k1_ps1_lifecycle_adapter/ops/supervisor.py")
OUT = NS / "ops" / "supervisor.py"

IMPORT_PREFIX = "import runtime_state as RS"
IMPORT_ADD = ('sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "driver"))\n'
              "import ps1_reconcile as RECON                                               # noqa: E402\n")


def _insert_import(src: str) -> str:
    lines = src.splitlines(keepends=True)
    hits = [i for i, l in enumerate(lines) if l.startswith(IMPORT_PREFIX)]
    if len(hits) != 1:
        raise SystemExit(f"IMPORT anchor not found exactly once ({len(hits)})")
    lines.insert(hits[0] + 1, IMPORT_ADD)
    return "".join(lines)

HELPER_ANCHOR = "def run(contract, role, run_id) -> int:\n"
HELPER_NEW = '''def _synthetic_validator(contract):
    """Under SYNTHETIC_CONTROL only, accept the synthetic marker shape -- exactly mirroring
    what tests/synthetic_cellseq_entry.py patches into the child. Under the PRODUCTION
    contract this returns None, so reconciliation uses the real _verified(), which demands
    the full t3/t4/t5/patches_gz bundle and re-hashes every file from disk."""
    if (contract or {}).get("mode") != "SYNTHETIC_CONTROL":
        return None
    return lambda r, cell, task: bool(isinstance(r, dict) and r.get("synthetic")
                                      and r.get("cell_id") == cell)


''' + HELPER_ANCHOR

SETTLE_OLD = '''            LK.reclaim_ledger_lock(Path(str(io.path) + ".lock"), contract, campaign_lock=lock)
            s = LO.settle_run(io, rt, role, run_id, u_final, "SUPERVISOR_FINAL")'''
SETTLE_NEW = '''            LK.reclaim_ledger_lock(Path(str(io.path) + ".lock"), contract, campaign_lock=lock)
            # A durable marker is a write-ahead completion fact. Convert every valid one
            # into an authoritative commit BEFORE any reservation can be classified torn.
            try:
                rrep = RECON.reconcile(contract, role, spec, io, child.pid,
                                       validator=_synthetic_validator(contract), say=say)
                if rrep.get("finalized") or rrep.get("rejected"):
                    rec["reconciliation"] = rrep
                    write_json_atomic(rt.run_record(run_id), rec)
            except Exception as exc:                              # noqa: BLE001
                say(f"RECONCILE_FAILED {type(exc).__name__}: {exc}")
                rec["reconciliation_error"] = f"{type(exc).__name__}: {exc}"[:300]
                write_json_atomic(rt.run_record(run_id), rec)
            s = LO.settle_run(io, rt, role, run_id, u_final, "SUPERVISOR_FINAL")'''


def main() -> int:
    src = SRC.read_text()
    for name, blk in (("HELPER", HELPER_ANCHOR), ("SETTLE", SETTLE_OLD)):
        if src.count(blk) != 1:
            raise SystemExit(f"{name} anchor not found exactly once ({src.count(blk)})")
    out = (_insert_import(src)
              .replace(HELPER_ANCHOR, HELPER_NEW, 1)
              .replace(SETTLE_OLD, SETTLE_NEW, 1))
    OUT.write_text(out)
    print(f"wrote {OUT}")
    print(f"  frozen supervisor sha256 : {hashlib.sha256(SRC.read_bytes()).hexdigest()}")
    print(f"  generated sha256         : {hashlib.sha256(OUT.read_bytes()).hexdigest()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
