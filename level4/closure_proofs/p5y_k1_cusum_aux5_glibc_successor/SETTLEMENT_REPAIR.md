# End-of-campaign settlement repair: CUSUM Aux5 new-glibc successor

**Status: pre-launch repair. Production has not been launched. No successor runtime root, ledger or scientific result exists.**

The independent pre-launch review of checkpoint `51df2186…` and run authorization `03b9ca80…` returned `BLOCKED`. This file records the defect, the repair and the supersession. It does not change any frozen predecessor namespace. It also leaves unchanged every file pinned by the carry-over countersignature `e1ee7fb1…` or by the proposal manifest `964dc969…`.

## 1. The defect

- **The final run is never settled.** The frozen supervisor ends a campaign with `DISPOSITION_<X>` and marks its own run `EXITED`. It never settles that run:
  - frozen `prod_ledger.reconcile` skips the current run;
  - a terminal ledger is never reopened, because the frozen supervisor returns `TERMINAL` before reconciling and preflight G17 refuses a terminal ledger.
- **So the successor is never ready.** Frozen `prov_integrity.audit` reports `D_unsettled_supervisor_runs` on every COMPLETE successor ledger. The composite audit stays `INCOMPLETE`, and `attest` and `export` refuse.
- **The predecessor shows the same state.** Its terminal ledger ends with run `R20260913T115713Z-103963`, `end: EXITED`, `settled: false`.
- **The predecessor lineages had a command for it.** They settle through `prod_entry.py settle` and `prov_entry.py settle`. `gs_entry.py` had no equivalent.
- **Acceptance r3 hid it.** It reached COMPLETE composites by calling the frozen harness helper `Campaign.settle()` directly. No operator can run that helper against production.

## 2. The repair: `gs_entry.py settle`

`code/gs_settle.py`, reached only as `gs_entry.py settle`, follows the frozen `prov_entry.py settle` model. Only two things write:
- the campaign flock and the authorization-bound ledger open;
- the frozen `prod_ledger.reconcile` (`RUN_SETTLED`) and the frozen `unmatched_overhead` / `op_charge_overhead` (`OVERHEAD_CHARGED`).

All preconditions are checked read-only before the first ledger write, and every refusal writes nothing.

| Precondition | Refusal |
|---|---|
| Target is a successor universe (128–325), outside every predecessor, blocked, qualification and repository root | `REFUSED_ROOT`, `QUALIFICATION_ROOT`, `REPOSITORY_ROOT`, `RECOMPUTATION_OF_CARRYOVER_CELL`, `SYNTHETIC_PRODUCTION_MIX`, `PREDECESSOR_RUNTIME_REFUSED` |
| A ledger exists | `NO_LEDGER` (ABSENT), `PRE_GENESIS` |
| No campaign process on the host; campaign flock free | `HOST_NOT_IDLE`, `ANOTHER_SUPERVISOR_LIVE` |
| Ledger continuous or journal-behind-one, validates, born under this authorization | `LEDGER_ROLLBACK_OR_MUTATION`, `ACCOUNTING_CORRUPT`, `CAP_CHANGE_FORBIDDEN`, `NO_PRE_RESULT_AUTHORIZATION`, `AUTHORIZATION_MISMATCH` |
| Terminal disposition (COMPLETE, HALTED, INCOMPLETE_BUDGET_EXHAUSTED); no open attempt; no sealed-but-unbound attempt; sealed record and bound envelope bytes unchanged | `NOT_TERMINAL`, `TERMINAL_LEDGER_WITH_OPEN_ATTEMPT`, `TERMINAL_LEDGER_WITH_UNBOUND_SEAL`, `SEALED_EVIDENCE_CORRUPT`, `ENVELOPE_EVIDENCE_CORRUPT` |
| Reaper evidence (see below) | `REAPER_UNREADABLE`, `SETTLEMENT_EVIDENCE_MISSING`, `SETTLEMENT_EVIDENCE_AMBIGUOUS`, `SETTLEMENT_EVIDENCE_CONTRADICTORY` |

What the reaper evidence must show:
- every reaper line verifies;
- the one unsettled run is the latest run and ended `EXITED`;
- exactly one keeper reap record matches it;
- that record's exit code equals the disposition's exit code (0, 20 or 40);
- it was taken after the run ended;
- its rusage is not smaller than the CPU already charged to the run;
- an uncharged keeper-exit record follows it.

**What settlement never touches.** It never writes a scientific record, a provenance envelope, a cell, an attempt, the disposition, the halt, the cap or a predecessor file. It never admits.

**What it charges.** Exactly the frozen rules: the final run's `REAPER_RUSAGE` extra (reap − children − self), plus each uncharged keeper exit once. The supervisor bucket is the only one that moves. The cap stays the residual cap.

**Idempotence.** A settled ledger returns `ALREADY_SETTLED` and writes nothing. After a crash between the two transitions, or inside one (journal behind one), the frozen ledger open repairs the ledger. The next call then completes the settlement, charging each run and each reaper record once.

**HALTED and budget-exhausted ledgers.** They are settled for accounting only. They keep their disposition and halt, and are never adjudication-ready.

**Operator sequence after production.**

```text
python -B code/gs_entry.py settle
python -B code/gs_entry.py composite-audit --out COMPOSITE_AUDIT.json
python -B code/gs_entry.py attest --out K4_COMPOSITE_ATTESTATION.json
python -B code/gs_entry.py export --out K4_EXPORT_DIR
```

## 3. Acceptance

- **The helper bypass is gone.** `tests/gs_fixtures.py` routes every settlement through `gs_entry.py settle` in a fresh interpreter. The frozen harness helper `settle()` now raises. A source scan refuses any direct settlement call in the successor tests.
- **Existing scenarios.** a01, b01, b02, b05, b06 and b07 settle through the command.
- **b07 end to end.** It proves that a COMPLETE successor fails to reach K4 *before* settlement, then passes each stage in order: COMPLETE → `settle` → frozen integrity audit → composite COMPLETE → K4 attestation (and the frozen K4 gate) → export.
- **New scenarios c01–c13** cover:
  - settle to audit-ready;
  - idempotence;
  - two crash points;
  - absent, pre-genesis, lock-held, crashed-OPEN and DRAINED refusals;
  - a busy host;
  - missing, malformed and ambiguous reaper evidence;
  - altered run identity;
  - altered CPU accounting;
  - predecessor roots;
  - qualification roots;
  - HALTED and budget-exhausted ledgers staying terminal;
  - cap continuity;
  - the production command refusing without a ledger.

## 4. Supersession

- **Superseded objects.** Checkpoint `51df21860139554ee38874c3578cfcafdf7949cd3916897a129d29467891ab16` and authorization `03b9ca8085a93a1a54d567f2efacf6fddfcd4f142c900735ea973a9269f87b2f` are superseded.
- **Why.** They were valid pre-launch candidates. They were never used for a production genesis, and no result-bearing compute was produced under them.
- **Guard.** `gs_entry.py` refuses both hashes by name.
- **Record.** The details are in `evidence/supersession_r1/SUPERSESSION_RECORD.json`. Byte copies of the superseded checkpoint, authorization and freeze record are kept beside it.

## 5. What did not change

- The scientific executor (`qualify5.py`), the producer identity and the runtime contract.
- Every predecessor namespace.
- The countersignature and every file it pins.
- The proposal and its governance artifacts.
- Q6.
- The carry-over set 0–127 and the production universe 128–325.
- The absolute cap (1,080,000,000,000 µs), the predecessor settled CPU (262,686,610,580 µs), the residual cap (817,313,389,420 µs) and the 115/100 invariant.
- The composite audit logic and the K4 attestation schema.
