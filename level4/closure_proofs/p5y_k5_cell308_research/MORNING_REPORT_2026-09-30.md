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
* **DEF-2** (the launcher could boot out a live job): repair R2 is committed in `35cabb50`; its independent delta review is running (§20).

## 12. Crash-safe persistence design

The durable path for a complete result: O_EXCL tmp → fsync → rename → dir fsync / F_FULLFSYNC → read-back and
self-hash verification → journal RESULT_DURABLE → `hash-object` (fsync) → pending ref (CAS) → seal (private index) →
materialize. A checkpoint is never a result. **DEF-1** (stale git ref locks after a mid-write reset): repair R1 is committed
in `35cabb50`; its independent delta review is running.

## 13. Crash and mutant test results

**Build `afba20e5`**, all independently re-run:
* static 9/9, state 34/34, crash 36/36 (F1–F12 by real `os._exit` and SIGKILL, plus 12 simulations), launch 6/6, dev
  decoy 2/2;
* mutants **33/33 killed**.

**Resume check.** Resumed equals uninterrupted over 643 Stage-1 and 883 Stage-2 certified leaves (dev decoy 297 block 0).

**Repairs `35cabb50`** (builder2's run; not yet independently re-run):
* static 9/9, launch 8/8, state 44/44, crash 47/47 (planted-lock cases L01–L11 added), dev decoy 2/2;
* mutants **46/47 killed**. M33, which predates the repairs, survives non-deterministically: its kill depends on timing. The
  deterministic test is part of the unapplied R3 work (§16).

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
* the implementation delta review (R1/R2/R4 at `35cabb50`) is **running**;
* **R3 is ratified but not applied.** The non-holder ratification is recorded (`3c2a7854`, CONSTANTS_RATIFIED_WITH_CHANGES). The
  ratifier could not apply it: an auto-mode safety check blocked one of its read-only commands, and it stopped without
  changing anything (worktree verified clean; ledger correction `3d08f981`). I have **not** applied the edits myself, and I
  did not hand them to another agent, because that would route around the block. They need you (§33).

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
* repairs and constants: `50afc064` (briefs 40–41), `3c2a7854` (constants ratification + this report's draft), `023a287d`
  (brief 42), `d9078876` (brief 43), `3d08f981` (ledger correction + brief 43 erratum E1);
* this report's final version: the commit after `3d08f981`.

**Formal `p5y-k5-cell308-mb-r1`:** `21e99cf0`, `a40211cc`, `9ad632c9`, `e451e634`.

**Successor `p5y-k5-cell308-mbs-r1`:** `afba20e5` (pre-freeze build), `35cabb50` (repairs R1/R2/R4).

## 20. Every rejection or failure, and its disposition

| rejection or failure | disposition |
|---|---|
| RECOVERY_ASSESSMENT_REJECTED | A1 |
| its DELTA_REJECTED | E1, then accepted |
| GOVERNANCE_REJECTED | A1, then delta accepted |
| route DELTA_REJECTED | E1, then accepted |
| **IMPLEMENTATION_REJECTED** (`6d3a44cd`; DEF-1 to DEF-4) | R1/R2/R4 repaired by builder2 at the non-holder reviewer's request (M4), `35cabb50`; delta review running. R3 ratified (`3c2a7854`) but **not applied** (see the next row) |
| the constants ratifier stopped by an auto-mode safety check | nothing changed; ledger correction `3d08f981`; not worked around; needs you |

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
* a reader-check file committed a few seconds before its completion notification (bytes verified identical);
* the ratifier's INFRASTRUCTURE ledger line (23:34:16Z) announced an edit that never happened; corrected at 23:36:04Z.

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

1. **Applying R3** (the ratified constants, the protocol-draft §8 text and a deterministic M33 test). The ratifier was blocked,
   so this needs you (§33). The implementation delta review (R1/R2/R4) is running.
2. The verifier, manifest writer and leak scanner are not built.
3. **Your freeze decision** (§14 / G2; the caps option; finality; the member decision).
4. Qualification on an awake, cool host with automatic updates disabled.
5. **Your S1 ruling.**
6. For adoption: a floor extension.

## 32. Strongest legitimate state reached

* MB r1 is fully closed out as INDETERMINATE.
* Successor governance, route and incident re-rating are all accepted.
* A crash-safe successor build exists (`35cabb50`). It is pre-freeze. R1/R2/R4 are repaired and under delta review; R3 is
  ratified but not applied.
* The decision brief is ready and passed its non-holder reader check.

## 33. Exact next action requiring your authorization

1. **How R3 gets applied.** The ratifier's edits are listed in its hand-back. There are three: comments only on `MEM_CAP_BYTES`
   and `FREE_MEM_MIN_BYTES`; four names added to `EXCL_ALLOW`; the launcher's `pre_launch` timeout becomes `PRE_CAP_S + 100`, with
   a re-pinned launcher hash. There is also the protocol §8 text and the M33 test. It needs a non-holder with edit access. The
   ratifier suggested a session outside auto mode, or a fresh session. I am a holder, so I may not apply them myself.
2. The freeze decision in `governance/USER_DECISION_BRIEF_308_SUCCESSOR.md` §A (`03ca1bcf`): grant or withhold, caps
   option (i) or (ii), finality (i) or (ii), members (i) or (ii). The S1 ruling comes later.

## 34. Update after delivery (2026-09-30 00:16Z): implementation delta review

**DELTA_REJECTED** (`reviews/REVIEW_IMPLEMENTATION_MBS308_DELTA.md`, `99185dcb`; non-holder reviewIMPL). The reviewer's own
re-runs at `35cabb50`: static 9/9, launch 8/8, state 44/44, crash 47/47, mutants 46/47.

| condition | ruling |
|---|---|
| R1 (stale locks, CAS) | **MET**, plus a required correction **C-1**: drop `packed-refs.lock` from the campaign's lock set. The campaign never owns it, and a live git holder is invisible to `lsof`, so moving it aside could lose refs in the shared repository |
| R2 (launcher boot-out) | **MET**; note N-2: an identity recorded while `ps` failed reads DEAD (safe by timing, not by design) |
| R4 (gate tests) | **MET**; the earlier escapes X2 and X3 now die |
| R3 (constants) | **NOT MET**: ratified, but not applied, and M33 is still non-deterministic. The proposed M33 run kills it (9.6 s vs 98.4 s against the 60 s bound) |
| M4 | **PASS**: builder2 changed no operational number |

**Reviewer's disclosed deviation.** Two synthetic-payload LaunchAgents ran under the builder's test label prefix, not the
review prefix. Both were booted out; their 0-byte logs remain in `~/Library/Logs/ReBaseGuard/mbs308-test/`.

**Afterwards (coordinator check):** no launchd job remains, the successor worktree is clean at `35cabb50`, MB r1's marker is
still `afa93072`, and no successor ref exists.

**Next.** A bounded application of R3 and C-1 by a non-holder, then an R3-only delta, would make the build
IMPLEMENTATION_ACCEPTED as a pre-freeze candidate. The same pass should take N-1 to N-3 (recommended, not gating).

## Final block

```
CELL 308 RECOVERY
-----------------
MB308 r1 target count: 1
target-consumed: YES (refs/p5y-k5-cell308-mb-r1/target-consumed -> afa93072, unchanged)
complete result: NONE
pending-result: NONE
seal: NONE
same-grant re-execution: NONE (not attempted; forbidden)
execution verdict: CELL308_EXECUTION_INDETERMINATE (9ad632c9; ADJUDICATION_ACCEPTED e451e634)
scientific status: OPEN (not closed; not a scientific negative)

CELL 308 SUCCESSOR
------------------
governance: SUCCESSOR_ALLOWED_WITH_CONDITIONS (e5871aa6; A1 ce145e51; E1 a7c969e8)
independent governance review: GOVERNANCE_REJECTED (e3c60491), then DELTA_ACCEPTED => GOVERNANCE_ACCEPTED (00a432df)
route: MB-S (MB r1 science byte-identical; infrastructure only)
independent scientific review: ROUTE_ACCEPTED under RC1-RC6 (a1d1c7d4); delta REJECTED (fc723105); R3 DELTA_ACCEPTED (87d0b2b9)
protocol: DRAFT only (not frozen)
detachment: launchd launcher proven by test; DEF-2 repaired (35cabb50), R2 MET in the delta (99185dcb)
persistence: crash-safe spool -> CAS -> seal built; DEF-1 repaired (35cabb50), R1 MET in the delta, correction C-1 (packed-refs.lock) open
crash tests: crash 47/47, state 44/44, mutants 46/47 (M33 timing-dependent) at 35cabb50, independently re-run; implementation delta DELTA_REJECTED on R3 only (99185dcb)
freeze: NOT FROZEN
qualification: NOT STARTED
independent qualification review: NONE
new target authorization: NONE
new target evaluations: 0
remaining blocker: R3 + C-1 application (ratifier blocked; needs you) and an R3-only delta; your freeze decision (brief §A); verifier/manifest/leak scanner; qualification; your S1 ruling

K5
---
306: OPEN (CELL306_NOT_ADOPTED)
307: CLOSED_UNDER_RLR (scientific closure only; NOT adopted)
308: OPEN (MB r1 INDETERMINATE; successor MB-S pre-freeze)
309: EXTERNALLY_IN_PROGRESS
r5: unchanged, authoritative
r6: NONE
K5: PARTIAL
P5Y: NOT CLOSED
```
