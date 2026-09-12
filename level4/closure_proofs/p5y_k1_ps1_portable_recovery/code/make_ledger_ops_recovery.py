"""Generate ops/ledger_ops.py for the recovery successor: adds the GRACEFUL_DRAIN kind.

Phase J mandate: the new generation must distinguish SCIENTIFIC FAILURE / INFRASTRUCTURE TEAR /
OPERATOR EMERGENCY STOP / GRACEFUL DRAIN, and "graceful drain is NOT a tear".

The frozen taxonomy has only three release kinds, all of which either HALT
(WORKER_FAILURE, MALFORMED, UNCLASSIFIED) or tear (ABORT + orphans). A cell that was admitted
but never started because the worker drained at a cell boundary is neither: it is simply
PENDING again. Without a fourth kind it is released through `finally` as ABORT and wrongly
increments torn_attempts -- observed live in acceptance A (cell 15).

GRACEFUL_DRAIN is deliberately NOT in HALTING and NOT in the `infra` set that increments
torn_attempts, so a drained cell returns to pending with its history untouched.
"""
import hashlib
import sys
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
SRC = Path("/home/ubuntu/work/ReBaseGuard-ps1-ops/level4/closure_proofs/"
           "p5y_k1_ps1_lifecycle_adapter/ops/ledger_ops.py")
OUT = NS / "ops" / "ledger_ops.py"

KIND_OLD = 'UNCLASSIFIED = "UNCLASSIFIED_RELEASE"\n'
KIND_NEW = ('UNCLASSIFIED = "UNCLASSIFIED_RELEASE"\n'
            'DRAIN = "GRACEFUL_DRAIN"          # recovery successor: a boundary drain is NOT a tear\n')

SITES_OLD = '''RELEASE_SITES = {"budget.release(key); continue": WORKER_FAILURE,
                 "budget.release(key)": MALFORMED,
                 "budget.release(k)": ABORT}'''
SITES_NEW = '''RELEASE_SITES = {"budget.release(key); continue": WORKER_FAILURE,
                 "budget.release(key)": MALFORMED,
                 "budget.release(k)": ABORT,
                 "budget.release(dkey)": DRAIN}'''

# torn_attempts must not count a graceful drain
INFRA_OLD = '        infra = sorted(set(orphans) | set(torn.get(ABORT, [])))\n'
INFRA_NEW = ('        # GRACEFUL_DRAIN is excluded by construction: a cell that never started\n'
             '        # because the worker drained at a boundary is pending, not torn.\n'
             '        infra = sorted(set(orphans) | set(torn.get(ABORT, [])))\n')


def main() -> int:
    src = SRC.read_text()
    for name, blk in (("KIND", KIND_OLD), ("SITES", SITES_OLD), ("INFRA", INFRA_OLD)):
        if src.count(blk) != 1:
            raise SystemExit(f"{name} anchor not found exactly once ({src.count(blk)})")
    out = (src.replace(KIND_OLD, KIND_NEW, 1)
              .replace(SITES_OLD, SITES_NEW, 1)
              .replace(INFRA_OLD, INFRA_NEW, 1))
    if "DRAIN" in out.split("HALTING =")[1].split("\n")[0]:
        raise SystemExit("GRACEFUL_DRAIN must NOT be in HALTING")
    OUT.write_text(out)
    print(f"wrote {OUT}")
    print(f"  frozen ledger_ops sha256 : {hashlib.sha256(SRC.read_bytes()).hexdigest()}")
    print(f"  generated sha256         : {hashlib.sha256(OUT.read_bytes()).hexdigest()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
