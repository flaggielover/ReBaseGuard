"""Deploy-time: initialize the generation-2 ledger. Idempotent and fail-closed.

Refuses if a generation-2 ledger already exists (never re-initializes over live state) and
refuses if the target resolves anywhere inside the generation-1 production root.
"""
import hashlib, json, sys
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(NS / "ops"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import make_generation2 as G2                                       # noqa: E402
from opscommon import host_spec, ledger_path, load_contract, frozen_accounting  # noqa: E402
import ledger_ops as LO                                             # noqa: E402
import runtime_state as RS                                          # noqa: E402


def main() -> int:
    contract = load_contract(None)
    spec = host_spec(contract, "AWS")
    tr = G2.transition_record()
    pred_root = Path(tr["predecessor"]["production_root"]).resolve()
    target = ledger_path(spec).resolve()

    # fail closed on cross-generation aliasing
    if pred_root == Path(spec["production_root"]).resolve() or pred_root in target.parents:
        raise SystemExit(f"REFUSED: generation-2 ledger would land inside generation 1: {target}")
    if target.exists():
        got = hashlib.sha256(target.read_bytes()).hexdigest()
        if got == tr["predecessor"]["ledger_sha256"]:
            raise SystemExit("REFUSED: target IS the generation-1 ledger")
        print(f"generation-2 ledger already present: {target}")
        print(f"  sha256: {got}")
        return 0

    M, GB = frozen_accounting(spec)
    st = G2.initial_ledger(GB.GlobalBudget.SCHEMA, LO.OPS_SCHEMA, "AWS")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes((json.dumps(st, indent=1, sort_keys=True) + "\n").encode())
    print(f"initialized generation-2 ledger: {target}")
    print(f"  sha256                 : {hashlib.sha256(target.read_bytes()).hexdigest()}")
    print(f"  imported committed CPU-h: {st['committed_cpu_h_by_role']}")
    print(f"  halt                   : {st['operational_lifecycle']['halt']}")
    print(f"  torn_attempts          : {st['operational_lifecycle']['torn_attempts']}")
    print(f"  completed_cells        : {len(st['completed_cells'])}")
    print(f"  open_reservations      : {len(st['open_reservations'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
