"""Generation-2 execution namespace: transition record + deterministic initial ledger.

DEFECT REPAIRED: EXECUTION_GENERATION_LEDGER_NAMESPACE_DEFECT. The portable-recovery
generation declared a new execution generation but still resolved PARENT_NS_REL to the
generation-1 namespace, so it read generation-1's ledger and inherited its active
HALTED/RETRY_LIMIT. supervisor.prestart then correctly refused.

NARROWEST CORRECT REPAIR: generation 2 gets its own production_root and runtime_dir. The
PRODUCTION_LEDGER is runtime state (.git/info/exclude), never tracked, so a fresh clone of
the SAME frozen code commit carries no ledger -- generation 2 therefore starts from a
deterministic initial ledger and cannot touch generation 1's. No scientific code, no
durability semantics and no checkpoint semantics change; prod_ns() itself is untouched.

Generation 1 stays HALTED forever. Its halt is neither cleared nor reclassified; it is
SUPERSEDED FOR A NEW EXECUTION GENERATION, which is an additive, pre-result record.
"""
import hashlib
import json
import sys
from pathlib import Path

NS = Path(__file__).resolve().parents[1]

PREDECESSOR = {
    "generation": 1,
    "namespace": "level4/closure_proofs/p5y_k1_ps1_production",
    "production_root": "/home/ubuntu/work/ReBaseGuard-ps1-prod",
    "ledger_sha256": "0557bc229c3fcdb10cb0dd0b5836fa62a6b0e6c2512656e6ec7e49294b4d6cab",
    "run_id": "20260912T041203Z-962132d3",
    "final_phase": "HALTED",
    "halt_reason": "RETRY_LIMIT",
    "halt_cells": "0..63",
    "science_cpu_h": 92.32,
    "genuine_finalized_cells": 0,
    "committed_scientific_results": 0,
    "archival_patch_records": 24610,
    "archival_patch_records_status": "ARCHIVAL_ONLY_NEVER_SCIENTIFICALLY_ADMISSIBLE",
    "torn_attempt_lineage": {"cells_0_to_63": 3},
    "forensic_incident": "HOST_OR_SYSTEMD_INFRASTRUCTURE_EVENT "
                         "(apt-daily-upgrade re-executed systemd 255.4-1ubuntu8.17; the service "
                         "restart cascade tore the transient unit at 06:01:57Z and 06:02:07Z)",
    "immutability": "generation 1 remains HALTED forever; this record imports facts only and "
                    "never mutates, clears or reclassifies it",
}

GEN2 = {
    "generation": 2,
    "namespace": "level4/closure_proofs/p5y_k1_ps1_production",
    "production_root": "/home/ubuntu/work/ReBaseGuard-ps1-prod-gen2",
    "runtime_dir": "/home/ubuntu/rbg-runtime/p5y_k1_ps1_generation2",
    # SYSTEMD_RECOVERY_EXECUTABLE_BINDING_DEFECT: render_start() builds BOTH ExecStart
    # (ops/supervisor.py) and ExecStopPost (ops/prodctl.py settle-fallback) from
    # spec["ops_root"]. That field was inherited from the frozen adapter, so the unit ran
    # the ADAPTER's ops against the RECOVERY contract; the adapter's opscommon.CONTRACT_PATH
    # is its own contract, so load_contract took the non-frozen branch and demanded
    # SYNTHETIC_CONTROL. The recovery ops/ is complete (3 generated + 4 byte-identical
    # inherited, per OPS_SOURCE_MANIFEST), so it is the correct and only executable root.
    "ops_root": "/home/ubuntu/work/ReBaseGuard-ps1-ops/level4/closure_proofs/p5y_k1_ps1_portable_recovery",
    "separation": ["ledger", "lock", "open reservations", "work dir", "durable markers",
                   "finalized cell evidence", "checkpoint state", "drain flag",
                   "settlement state"],
}

SUPERSESSION = {
    "record": "PREDECESSOR_HALT_SUPERSEDED_FOR_NEW_EXECUTION_GENERATION",
    "not_a_clear": "the generation-1 halt is NOT cleared and NOT reclassified; it remains "
                   "authoritative for generation 1",
    "grounds": [
        "RETRY_LIMIT is an infrastructure/lifecycle counter, not a scientific counterexample "
        "(ledger_ops.MAX_INFRA_TEARS_PER_CELL; protocol retry_and_halt.infrastructure_tear)",
        "root cause established as a host/systemd maintenance event, not science",
        "scientific failure: none; 0 finalized cells, 0 committed scientific results",
        "execution architecture repaired: per-cell durable finalization, supervisor-owned "
        "marker reconciliation, GRACEFUL_DRAIN",
        "operator explicitly authorized creation of a successor generation",
    ],
    "pre_result": True,
    "immutable": True,
}

RETRY_ACCOUNTING = {
    "generation_1_torn_counters": "preserved verbatim in the generation-1 ledger; never "
                                  "overwritten, never reset, never imported as active state",
    "generation_2_torn_counters": "start empty and are governed independently",
    "max_infra_tears_per_cell_generation_2": 3,
    "graceful_drain_is_a_tear": False,
    "reporting": "predecessor lineage and current-generation lineage are reported separately",
}


def transition_record() -> dict:
    return {"schema": "rebaseguard.p5y.k1.ps1.generation-transition.v1",
            "defect_classification": "EXECUTION_GENERATION_LEDGER_NAMESPACE_DEFECT",
            "scientific_impact": "NONE",
            "historical_results_affected": "NONE",
            "genuine_production_launched_under_defective_generation": False,
            "predecessor": PREDECESSOR,
            "generation_2": GEN2,
            "halt_supersession": SUPERSESSION,
            "retry_accounting": RETRY_ACCOUNTING,
            "accounting_import": {
                "predecessor_science_cpu_h": 92.32,
                "seeded_into_generation_2_as": "committed_cpu_h_by_role.AWS",
                "invariant": "cumulative accounting can never report below 92.32 CPU-h",
                "global_cpu_cap": 6600.0}}


def initial_ledger(ledger_schema: str, ops_schema: str, role: str = "AWS") -> dict:
    """EXACT LedgerIO.fresh() + new_ops(role) shape, with the predecessor's science CPU
    imported as already-committed so the cap can never be re-granted."""
    return {"schema": ledger_schema,
            "committed_cpu_h_by_role": {role: PREDECESSOR["science_cpu_h"]},
            "open_reservations": {},
            "completed_cells": {},
            "remote_completed_cells": {},
            "operational_lifecycle": {"schema": ops_schema, "role": role, "runs": {},
                                      "settlements": [], "releases": [],
                                      "torn_attempts": {}, "halt": None}}


def main() -> int:
    rec = transition_record()
    out = NS / "config" / "GENERATION_TRANSITION.json"
    payload = (json.dumps(rec, indent=1, sort_keys=True) + "\n").encode()
    assert b'"_sha256"' not in payload, "record must never embed its own hash"
    out.write_bytes(payload)
    digest = hashlib.sha256(out.read_bytes()).hexdigest()
    (NS / "config" / "GENERATION_TRANSITION_HASH").write_text(digest + "\n")
    print(f"wrote {out}")
    print(f"  transition record sha256 : {digest}")
    print(f"  predecessor ledger       : {PREDECESSOR['ledger_sha256']}")
    print(f"  gen-2 production_root    : {GEN2['production_root']}")
    print(f"  gen-2 runtime_dir        : {GEN2['runtime_dir']}")
    print(f"  imported CPU-h           : {PREDECESSOR['science_cpu_h']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
