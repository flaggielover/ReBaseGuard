# Cell 308: overnight report (2026-09-29 15:00Z → 2026-09-30 morning JST)

**Scope.** Cell 308 only. 309 is EXTERNALLY_IN_PROGRESS and untouched.

**New cell-308 target evaluations tonight: 0.** No authorization, grant, marker or Γ(5,308) evaluation was made tonight.

All branches are local only: nothing pushed or merged; `main`, the README, r5 and floor r2 untouched.

## 1. Final Cell-308 recovery state (MB308 r1): **RECOVERY_ASSESSMENT_ACCEPTED**

* **Formal branch** `p5y-k5-cell308-mb-r1`:
  * postexec `21e99cf0`;
  * EXECUTION_ACCEPTED `a40211cc` (adapted sense: the record is accurate, and no scientific result exists);
  * adjudication **CELL308_EXECUTION_INDETERMINATE** `9ad632c9`;
  * ADJUDICATION_ACCEPTED `e451e634`.
* **Research recovery chain** `8b64d989` → `98118e22` (§2).

## 2. The original recovery rejection and its disposition

| step | commit | verdict |
|---|---|---|
| assessment | `8b64d989` | — |
| independent review | `ef29bc2b` | **RECOVERY_ASSESSMENT_REJECTED** as submitted: conclusions A–E right; the factual record omitted the 23:29 Force Quit |
| addendum A1 | `e681d16f` | — |
| delta review | `0b9020af` | **DELTA_REJECTED** (R1: driver survival overstated; R2: object count) |
| erratum E1 | `c5f7c857` | — |
| R3 re-check | `98118e22` | **DELTA_ACCEPTED**, which makes it RECOVERY_ASSESSMENT_ACCEPTED |

Every rejection is preserved. The original texts are byte-unchanged.

## 3. Corrected timeline (JST)

| time | event | strength |
|---|---|---|
| 20:57:58 | launch | coordinator-reported |
| 20:58:00 | pre-marker probes | ids recomputed |
| 20:58:01 | marker → `afa93072` | the target is consumed |
| 23:10 | coordinator read-only audit: the run was alive | — |
| **23:29:00.047** | **the user's Force Quit of the hosting Claude desktop app**; both caffeinate processes died (the launcher's and the driver's `keep_awake`); the run was orphaned | logged |
| to at least 23:40:48 | the Stage-1 pool load continued | qualitative; powerlog |
| 23:40:35 / 23:41:09 | last power-log / unified-log entries | logged |
| 00:00:15 | boot after a **forced power-button reset** (PMU `btn_rst,btn_seq_reset`) | kernel boot log |

**Driver death:** most probably after 23:29:00, at the latest 00:00:15. The cause of the hang after 23:41 is unknown.
Nothing was persisted after the marker.

## 4. Final MB308 r1 execution verdict

**CELL308_EXECUTION_INDETERMINATE**: the §8 row "any post-marker failure … unsealable", target consumed, no rerun. The
state is equivalent to CONSUMED_UNRECORDED. The driver never returned, so no exit code exists.

## 5. Cell-308 scientific status

**OPEN.** Not closed, and not a scientific negative. No Γ value exists. MB r1's target count is 1, and its single
authorization is exhausted.

## 6. Successor-governance verdict

**SUCCESSOR_ALLOWED_WITH_CONDITIONS** (determination `e5871aa6`, addendum A1 `ce145e51`, erratum E1 `a7c969e8`).
* Target-free preparation is permitted up to, but not including, the freeze.
* A **user decision** is required before the freeze (§14 / G2, same caps).
* A **user ruling (S1)** is required before any grant, notwithstanding brief §21 and mitigation 5.

## 7. Independent governance review

**GOVERNANCE_REJECTED** as submitted (`e3c60491`), for record defects O1–O5 and unrecorded user texts. Then **DELTA_ACCEPTED,
which makes it GOVERNANCE_ACCEPTED** (`00a432df`), with errata D1–D3 applied (`a7c969e8`).

## 8. Chosen successor route

**MB-S**: MB308 r1's science (Theorem MB r1), byte-identical; only the infrastructure changes.
* Audit `bddd85f8`, A1 `ce145e51`, E1 `a7c969e8`, E2 `6a33f22d`.
* Route review: **ROUTE_ACCEPTED** under RC1–RC6 (`a1d1c7d4`). Delta **DELTA_REJECTED** (`fc723105`; DR1–DR3). R3
  re-check **DELTA_ACCEPTED** (`87d0b2b9`).

## 9. Alternative route matrix

| status | routes |
|---|---|
| PRUNED | P0 (certified in full); P1 (evidenced) |
| components of R-MB | R1, R2 (alarm only), R3, R5, R6, R7, R8, R10a, C-RLR; TPT / C5-T / LR / B2c included |
| DEFERRED | C11R-I2 and COR-T (the member decision is yours, MBS-7); X308; the catch-all (no instrument) |
| NOT SELECTED | R-MB parameter variants (D1, D3, D4, D5, D14 budgets, the RLR slot rule, extra drifts) |
| BLOCKED | R4, R9, C9-E1, RO3 |
| EXCLUDED | CHAIN; another host (unless the RC2 pin is discharged there) |

## 10. Successor architecture

`governance/SUCCESSOR_ARCHITECTURE_308.md` (`8a4a02b4`) and A1 (`87d0b2b9`). Its elements:
* a durable journal (CAS ref), with states NO_TARGET_CONSUMED, CONSUMED_COMPUTING, CONSUMED_INTERRUPTED,
  RESULT_DURABLE_UNSEALED, PENDING_RESULT, SEALED, CONSUMED_UNRECORDED and INDETERMINATE, and a frozen `recover`
  action for each;
* governed checkpoints (never results) with mandatory resume: 3 attempts, 7 days;
* a platform pin at execute and at every resume;
* a no-update window;
* checkpoint quarantine.

## 11. Process-detachment evidence

* **launchd launcher.** In a real launchd job with a synthetic payload, the job survived the kill of the launching
  shell's process group **and** session. Detachment is proven by test, not by PPID=1.
* **caffeinate supervisor.** caffeinate was re-spawned after it was killed.
* **Stale pidfile.** Detected.
* **Re-run by the independent reviewer:** 6/6.
* **DEF-2** (the launcher could boot out a live job) is **under repair R2** (§20).

## 12. Crash-safe persistence design

The durable path for a complete result: O_EXCL tmp → fsync → rename → dir fsync / F_FULLFSYNC → read-back and
self-hash verification → journal RESULT_DURABLE → `hash-object` (fsync) → pending ref (CAS) → seal (private index) →
materialize. A checkpoint is never a result. **DEF-1** (stale git ref locks after a mid-write reset) is **under repair R1**.

## 13. Crash and mutant test results

**Build `afba20e5`**, all independently re-run:
* static 9/9, state 34/34, crash 36/36 (F1–F12 by real `os._exit` and SIGKILL, plus 12 simulations), launch 6/6, dev
  decoy 2/2;
* mutants **33/33 killed**.

**Resume check.** Resumed equals uninterrupted over 643 Stage-1 and 883 Stage-2 certified leaves (dev decoy 297 block 0).

**Gaps** (DEF-1, DEF-4) are under repair (§20).

## 14. Independent verifier status

The same as MB r1: F2 `mb_independent`, F3 `tuple_independent`, VERIFY `vd_pl` / `vd_verify`, `rlr307_independent`.
All are loaded by pin and byte-identical. Science identity is AST-verified by the non-holder reviewer. The tiny
MBR1_REPRO matches MB r1's committed QC02 records.

## 15. Decoy / non-target validation

* Dev decoy 297 (block 0, dev ladder): resumed equals uninterrupted.
* Tiny MBR1_REPRO: exact.
* Full MBR1_REPRO, QS-RESUME-DECOY and the real driver under launchd are **not yet run**. They belong to qualification.

## 16. Freeze status

**NOT FROZEN.** The gates:
* the user decision under §14 / G2 (S16(c)) and MBS-6/7/8 are **open (user)**;
* S16(b) (RC1/RC2 as facts) awaits qualification;
* the implementation delta (R1–R4) is PENDING.

## 17. Qualification status

**Not started.** It needs a freeze. The verifier, manifest writer and leak scanner are not yet built.

## 18. Independent qualification-review verdict

**None.** There is no qualification yet.

## 19. Every commit created overnight

**Research `p5y-k5-cell308-research`:**
* the recovery chain: `8b64d989` `ef29bc2b` `e681d16f` `0b9020af` `c5f7c857` `98118e22`;
* briefs and ledger: `7a02607b`, `f131e95a`, `7dfe617f`, `83e60aa2`, `03fc1f0a`, `e084b70a`, `50afc064`;
* governance: `e5871aa6`, `e3c60491`, `ce145e51`, `00a432df`, `a7c969e8`;
* route: `bddd85f8`, `a1d1c7d4`, `fc723105`, `87d0b2b9`;
* architecture: `8a4a02b4`;
* K5 audit: `7da9e03e`;
* incident re-rating: `b7e62dec`, `6a33f22d`, `ff2280e9`, `bae2945d`;
* decision brief: `60af17dd`, `21a86b43`, `03ca1bcf`, `751babc2`;
* implementation review: `6d3a44cd`;
* the rest: (PENDING).

**Formal `p5y-k5-cell308-mb-r1`:** `21e99cf0`, `a40211cc`, `9ad632c9`, `e451e634`.

**Successor `p5y-k5-cell308-mbs-r1`:** `afba20e5` (PENDING: repairs).

## 20. Every rejection or failure, and its disposition

| rejection or failure | disposition |
|---|---|
| RECOVERY_ASSESSMENT_REJECTED | A1 |
| its DELTA_REJECTED | E1, then accepted |
| GOVERNANCE_REJECTED | A1, then delta accepted |
| route DELTA_REJECTED | E1, then accepted |
| **IMPLEMENTATION_REJECTED** (`6d3a44cd`; DEF-1 to DEF-4) | repairs R1/R2/R4 by builder2 at the non-holder reviewer's request (M4); R3 by a non-holder ratifier. PENDING delta |

## 21. Every incident

**The four research-ledger INCIDENT lines:**
1. 2026-09-29T15:22:45Z: the consumed, unrecorded MB r1 evaluation (count 1).
2. 17:40:48Z: its supplementary correction (count 0).
3. 19:14:45Z: the successor sandboxes freshened the mtime of MB r1's probe blob (count 0; nothing created).
4. 21:05:13Z: the builder's exposure. **T6_FIRED_MITIGATED** (`ff2280e9`; rating MEDIUM–HIGH only under M1–M8,
   otherwise HIGH).

**Also:**
* an accidental HISTORICAL_READ by the coordinator (BRIEF_CHECK.json);
* the coordinator's unreliable "~HH:MMZ" time annotations (errata);
* a reader-check file committed a few seconds before its completion notification (bytes verified identical).

## 22. Exact new Cell-308 target-evaluation count

**0 tonight.** The ledger total is 1 (MB r1's consumed evaluation).

## 23. 306

OPEN. The I1 historical closure stands. The replacement I2 evaluation was positive: CELL306_NOT_ADOPTED (`9c2cbf21`,
`c5324a78`). There is no rerun and no current path.

## 24. 307

CLOSED_UNDER_RLR (scientific closure only; not adopted). Floor r2 puts 307 out of scope, so adoption needs a
prospective floor extension.

## 25. 308

OPEN. MB r1 is INDETERMINATE. The successor MB-S is prepared, and its freeze and grant are gated on your decisions.

## 26. 309

**EXTERNALLY_IN_PROGRESS**, untouched.

## 27–30. r5, r6, K5, P5Y

| item | status |
|---|---|
| r5 | unchanged, authoritative; open [306, 309] |
| r6 | none |
| K5 | PARTIAL |
| P5Y | not closed (K5 is its only open item; K1–K4 are closed) |

## 31. Remaining blockers

1. The implementation delta (R1–R4) and the constants ratification: PENDING.
2. The verifier, manifest writer and leak scanner are not built.
3. **Your freeze decision** (§14 / G2; the caps option; finality; the member decision).
4. Qualification on an awake, cool host with automatic updates disabled.
5. **Your S1 ruling.**
6. For adoption: a floor extension.

## 32. Strongest legitimate state reached

* MB r1 is fully closed out as INDETERMINATE.
* Successor governance, route and incident re-rating are all accepted.
* A crash-safe successor build exists. It is pre-freeze, and its implementation is under bounded repair.
* The decision brief is ready and passed its non-holder reader check.

## 33. Exact next action requiring your authorization

The freeze decision in `governance/USER_DECISION_BRIEF_308_SUCCESSOR.md` §A (`03ca1bcf`): grant or withhold, caps
option (i) or (ii), finality (i) or (ii), members (i) or (ii). The S1 ruling comes later.
