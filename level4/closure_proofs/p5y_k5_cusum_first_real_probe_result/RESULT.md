# K5 CUSUM first real probe (slot-1): result

**Status**

| key | value |
|---|---|
| `SCIENTIFIC_PROBE` | `FIRST_CELL_SUPPORTED_ALL_M` |
| `ADOPTION_STATUS` | `ADOPTED` (independent adjudication) |
| `REAL_PRODUCER_QUALIFICATION` | `PASS` |
| `SCIENCE_USABLE` | true |

One governed attempt of the frozen protocol `p5y_k5_cusum_first_real_probe_protocol` r4 ran on rebaseguard-vultr-02 under
the published, countersigned external authorization (`b2bc93d5` / `dd750286` / LAUNCH_NOTICE `93a73313`). It sealed a
scientific record. For every m in {1, 2, 3, 5}, the certified enclosure of R'''(0) is positive and the transported
lower bound L1 on the theorem cell C_1 = [0, x1] is positive. So the preregistered verdict is
`SUPPORTS_K5B_FIRST_CELL` for all four m.

## Per-m results

The table rounds to 13 significant digits. The exact rationals are in the sealed record and in
`interpretation/STAGE_BC_REPORT.json`.

| m | L0 | U0 | M5 | penalty (x1²/2)·M5 | L1 | U1 | verdict | point |
|---|---|---|---|---|---|---|---|---|
| 1 | 1801.434727921 | 2790.362876472 | 1.061360489928e8 | 13.71112658363 | **1787.723601338** | 2804.074003056 | SUPPORTS_K5B_FIRST_CELL | POINT_POSITIVE |
| 2 | 1461.592374121 | 2410.418561002 | 9.164814988466e7 | 11.83951537813 | **1449.752858743** | 2422.258076380 | SUPPORTS_K5B_FIRST_CELL | POINT_POSITIVE |
| 3 | 1307.107127538 | 2200.973144784 | 8.367296396924e7 | 10.80924541187 | **1296.297882126** | 2211.782390196 | SUPPORTS_K5B_FIRST_CELL | POINT_POSITIVE |
| 5 | 1073.994985367 | 1930.974900716 | 7.340440809230e7 | 9.482707719957 | **1064.512277647** | 1940.457608436 | SUPPORTS_K5B_FIRST_CELL | POINT_POSITIVE |

**How the table is defined.**
- x1 = 5083/10^7, so x1²/2 = 25836889/2·10^14 ≈ 1.29184445e-7.
- [L0, U0] is the certified enclosure of R'''_m(0).
- M5 ≥ sup over [0, x1] of |R_m^(5)|.
- L1 = L0 − (x1²/2)·M5 and U1 = U0 + (x1²/2)·M5, recomputed exactly by the frozen `probe_rules.transport`.

**Verdicts and route.**
- Each m has consequence `K5B_CELL_1_PASSES_FOR_THIS_M` and consumption key POSITIVE.
- The aggregate is `FIRST_CELL_SUPPORTED_ALL_M`, and the frozen route is
  `CONSUME_IN_FROZEN_K5B_CHECKER_THEN_PREREGISTER_NEXT_ORDER3_CELLS`.

## K5-B consumption (accepted E6 adapter, POSITIVE m only)

**Inputs.**
- The adapter is `p5y_k5b_consumption_adapter/code/consumption_adapter.py` (`fbad7d33…`).
- For each m it takes L_1 := L1_m exactly and L_k := None for k ≥ 2, on the certified K1 CUSUM records 0–309.
- The output sha256 is `89017388681e05ec9b8e63ef8e22305af8bd7cf76d5ab1b571a7c948afcafb6a` (canonical JSON). The operator and the
  adjudicator computed it independently and got the same value.

| m | cells closed by the frozen theorem | newly closed vs L = None | still open |
|---|---|---|---|
| 1 | 0, 133–309 (178) | cell 0 | 1–132 |
| 2 | 0, 145–309 (166) | cell 0 | 1–144 |
| 3 | 0, 146–309 (165) | cell 0 | 1–145 |
| 5 | 0, 149–304 (157) | cell 0 | 1–148, 305–309 |

**What follows, under the frozen `k5b_consumption_map.POSITIVE` entry.**
- Cell C_1 (K1 cell 0) now passes K5-B for every m.
- **H3a is not yet established for any m.** That needs every cell meeting (0,2] to pass.
- As the preregistration disclosed, the chain does not reach cell 1: μ_2 = H_2.lo < 0 with L_2 = −∞.
- The next informative cells are the first failing ones after C_1: cell 1 for every m, and the m = 5 tail 305–309. Each
  needs its own new preregistration.
- This protocol is now exhausted. The sealed record blocks every further launch (frozen P09), and no rerun or
  alternative method is permitted under it.

## Independent adjudication: ADOPTED

`adjudication/ADJUDICATION.md` and `.json` come from a fresh-context session using its own GitHub clones on the host and on
the Mac. It applied `independent_adjudication.rule` and ran 72 checks with no failures:
- **Record integrity.** The sealed sha256 equals the ledger OUTCOME and the seal event, and `lifecycle.reconcile`
  returns [].
- **Q07.** Recomputed exactly.
- **Q11.** `scientific_hash` and the four address hashes recomputed from committed inputs.
- **Verdicts.** Every verdict replayed with the frozen `probe_rules`, and equal to the frozen `consumer.interpret`.
- **Logs and gates.** The attempt log and gate evidence were reviewed. Q01–Q16 and QE01–QE12 are all true, the
  temporal order holds, and publication is confirmed on the GitHub frontier.
- **E6.** The consumption was re-run.

`probe_rules.adoption_status(sealed=True, science_usable_=True, independent_replay_pass=True,
independent_review_pass=True)` returns **ADOPTED**.

**Independence limits.** The adjudicator is a separate session and process of the same model (claude-opus-5), not a human
and not a different model family.

**Observation.** The certified M5 (penalty 13.7 for m = 1) is about 24 times tighter than the pre-result forecast
(330.1). It equals the last value of the executor's non-increasing 12-iteration local_r5 trace. The verdicts would change
only if M5 were about 113–131 times larger. No certificate was recomputed.

## Attempt record

**Launch.** 2026-09-18T16:36:58Z on vultr-02, from a fresh full GitHub checkout
`/root/work/k5-real-launch-69a162d0` at `69a162d0`. The argv was exactly:

    /root/work/rbg-cusum-aux5-venv/bin/python -B …/p5y_k5_cusum_real_point_executor/code/supervisor.py launch --namespace /root/work/k5-first-real-probe --slot 1 --mode real

The cwd was the executor namespace.
- The supervisor was pid 512067 (RUN_STATE and RUN_COMPLETE), and the executor child was pid 512745.
- `launch/SUPERVISOR_PID` holds 512063. That is the pid of the operator's wrapper shell, not the supervisor, and no gate
  reads it.

**Final preflight** (`launch/PREFLIGHT_*.json`). The unmodified frozen verifier returned LAUNCH_PERMITTED, P01–P12. Also:
- the runtime contract matched;
- K1 records 326/326;
- canonical slot `slot-1`;
- no namespace;
- no conflicting producer;
- the upgrade windows fell after the wall limit.

**Guard.**
- Set host-only to `{"policy": "EXTERNAL_AUTHORIZATION"}` at 16:32Z, as `TRUST_MODEL.md` step 4 specifies. The executor
  identity was unchanged.
- Restored to the committed DENY bytes at 17:29:56Z. It was never committed.

**Timeline.**

| time (UTC) | event |
|---|---|
| 16:36:59 | prelaunch decision LAUNCH_PERMITTED, in process |
| 16:37:00 | VALIDATED, then ARITHMETIC_STARTED |
| 17:27:28 | SEALED |

- RUN_COMPLETE: failure class none.
- Child CPU was about 3.0e3 s, within the 9000/10800 CPU-s ceilings. The preregistered estimate was 3060 CPU-s.

**Ledger** (`44088f14`). OUTCOME COMPLETED and SCIENTIFIC_RECORD_SEALED `cf90f1ea…`. Both were committed and published
before anyone interpreted the record.

**Operator notes** (none affected the attempt).
- Two pre-launch aborts came from the operator's own guard script, both before any launch: a self-matching process check,
  and an argv index off by one. Each stopped fail-closed.
- The launch wrapper held the remote exec session open, so it reported a timeout after 120 s. The supervisor had been
  started with setsid/nohup and ran unaffected.

## Files

| path | content |
|---|---|
| `p5y_k5_cusum_first_real_probe_protocol/evidence/slot-1/` | `SCIENTIFIC_RECORD_SEALED.json` (`cf90f1ea…`), `RUN_STATE.json`, `RUN_COMPLETE.json`, `ATTEMPT_LOG.jsonl`, byte-identical to the host slot |
| `adjudication/` | the independent adjudication |
| `interpretation/` | stage A (ledger derivation without reading values) and stage B/C (frozen `consumer.interpret` plus E6), both run on the host |
| `consumption/E6_POSITIVE_CONSUMPTION_OUTPUT.json` | the full adapter output |
| `launch/` | argv, UTC, preflight reports, supervisor stdout/stderr, the pre-transition guard, the post-run scripts |

Nothing frozen changed: the science preregistration, the R1–R5 executor, the E6 adapter, `k5_minimality`,
`k5b_check`, the K1 records, K5-B and the CUSUM closure. The host slot `/root/work/k5-first-real-probe/slot-1` is
preserved.

`REAL_CELL_EXECUTED = YES (once, slot-1)` · `REAL_INPUT_ARITHMETIC_GUARD = DENY (restored)` ·
`NEXT = PREREGISTER_NEXT_ORDER3_CELLS (cell 1 per m, m = 5 tail 305–309), each under a new protocol`
