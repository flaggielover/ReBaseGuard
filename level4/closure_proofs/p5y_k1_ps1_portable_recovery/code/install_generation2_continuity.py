"""Install the generation-2 ledger continuity record.

DEFECT: GENERATION2_LEDGER_CONTINUITY_RECORD_OMISSION.

Sanctioned fresh-production path (ledger_ops.open_run):
    if io.read() is None and last_continuity(rt) is None:
        append_continuity(rt, "GENESIS", None, {"role": role})
GENESIS is written while NO ledger exists; the lifecycle then creates the ledger. The
generation-2 deploy-time initializer created the ledger FIRST, so at prestart
last_continuity(rt) was None while st was not None, and check_continuity correctly raised
UNSANCTIONED_LEDGER. The gate was right; the omission was ours.

REPAIR (external provenance, matching the established design; the ledger is NOT touched):
append a hash-chained pair via the established ledger_ops.append_continuity writer, in the
established location <runtime_dir>/continuity.jsonl:
    seq 0  GENESIS                        view=None
    seq 1  GENERATION2_LEDGER_INITIALIZED view=ledger_view(current gen-2 ledger)
check_continuity then takes its CONTINUOUS branch (lv not None, no rollback, now == lv).
Nothing is special-cased, no gate disabled, neither ledger changes a byte.
"""
import json
import sys
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(NS / "ops"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import make_generation2 as G2
from opscommon import (RuntimeDir, host_spec, ledger_path, load_contract,
                       frozen_accounting, frozen_budget, sha256_file)
import ledger_ops as LO

INSTALLER = "install_generation2_continuity.v1"


def main() -> int:
    contract = load_contract(None)
    spec = host_spec(contract, "AWS")
    rt = RuntimeDir(spec).ensure()
    tr = G2.transition_record()
    lp = ledger_path(spec)
    if not lp.exists():
        raise SystemExit("REFUSED: no generation-2 ledger at %s" % lp)
    before = sha256_file(lp)
    if before == tr["predecessor"]["ledger_sha256"]:
        raise SystemExit("REFUSED: that is the generation-1 ledger")
    prev = LO.last_continuity(rt)
    if prev is not None:
        print("continuity already present: %s" % rt.continuity)
        print("  last event : %s (seq %s)" % (prev["event"], prev["seq"]))
        print("  ledger sha : %s  (unchanged)" % before)
        return 0
    M, GB = frozen_accounting(spec)
    io = LO.LedgerIO(lp, M, GB, frozen_budget(spec, contract))
    st = io.read()
    ops = st[LO.OPS_FIELD]
    eg = contract["execution_generation"]
    LO.append_continuity(rt, "GENESIS", None, {"role": "AWS"})
    extra = {
        "installer": INSTALLER,
        "classification": "GENERATION2_LEDGER_CONTINUITY_RECORD_OMISSION",
        "execution_generation": 2,
        "production_root": spec["production_root"],
        "runtime_dir": spec["runtime_dir"],
        "ledger_path": str(lp),
        "ledger_sha256": before,
        "predecessor_ledger_sha256": tr["predecessor"]["ledger_sha256"],
        "predecessor_finalized_cells": tr["predecessor"]["genuine_finalized_cells"],
        "generation_transition_record_sha256": eg["transition_record_sha256"],
        "imported_science_cpu_h": tr["predecessor"]["science_cpu_h"],
        "generation2_finalized_cells": len(st["completed_cells"]),
        "generation2_open_reservations": len(st["open_reservations"]),
        "generation2_halt": ops["halt"],
        "generation2_torn_attempts": ops["torn_attempts"],
        "pending_domain": contract["parent"]["total_cells"],
        "operational_contract_sha256": contract["_sha256"],
        "halt_supersession": tr["halt_supersession"]["record"],
        "scientific_impact": "NONE",
        "genuine_scientific_cells_admitted": 0,
        "rejected_prior_attempt": {"run_id": "20260912T150615Z-038e77d3",
                                   "disposition": "ARCHIVAL_OPERATIONAL_EVIDENCE_ONLY",
                                   "refusal": "UNSANCTIONED_LEDGER"},
    }
    rec = LO.append_continuity(rt, "GENERATION2_LEDGER_INITIALIZED", st, extra)
    after = sha256_file(lp)
    if after != before:
        raise SystemExit("REFUSED: ledger changed during install %s -> %s" % (before, after))
    print("installed continuity: %s" % rt.continuity)
    print("  seq %s  event %s" % (rec["seq"], rec["event"]))
    print("  record sha256 : %s" % rec["sha256"])
    print("  prev_sha256   : %s" % rec["prev_sha256"])
    print("  bound view    : %s" % json.dumps(rec["view"]))
    print("  ledger sha256 : %s (BYTE-IDENTICAL before/after)" % before)
    return 0


if __name__ == "__main__":
    sys.exit(main())
