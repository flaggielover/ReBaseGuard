# Cell-308 successor MB-S r1: delta review of the pre-freeze tooling, T1 cc723527 + T2 555f4cbf (reviewQ6, brief 53)
DELTA_REJECTED

Reviewer `reviewQ6`, fresh and independent of builder4, builder5, the coordinator editorR3C1 and every earlier reviewer.
Brief 53 (`ledger/briefs/53_reviewQ6_prefreeze_tooling.txt`, sha256 `67bbd5d0…2cdd`, verified before anything else).
Object: successor branch `p5y-k5-cell308-mbs-r1`, T1 `cc723527f63f4e69bfe36f86680d8fdaf481900e` (builder4) and T2
`555f4cbf89663cb32d2e246c7f37ff527d99a8ff` (builder5) on `216c465f`. The verdict was not predetermined.

**The rejection is narrow.** Two of the six sections are not satisfied on the committed bytes, each on one point:
section 1 on (e) (one governance record of QC13-S carries a verdict token that is not on line 2 of the file it names,
so QC13-S cannot pass as configured: finding F-1), section 3 on the base-store rule (a base store that a live sandbox
in another scratch root borrows from is deleted, against the protocol's own sentence "a store still borrowed is kept",
and the rule has no test that can fail: findings F-2, G-3) with two smaller points (F-3, G-4). Everything else was
independently reproduced: 162 / 162 tests, the full matrix 136 / 136 killed by assertion, reviewB5's Y5 / Y6 now die, no operational
number changed, 0 target evaluations. Sections 2, 4, 5 and 6 are MET. The repair set is R1-R4 of section 8 below and
needs no user decision; a narrow re-check of exactly those items suffices.

## 0. Reviewer, exposure, method

* **Exposure (MBS-2).** I hold no MB r1 run observation from any file I opened. My starting context carried the host
  tool's memory index (MEMORY.md; not a source; I opened none of its files). It **does carry MB r1 material**: the
  outcome label of MB r1's one execution with "consumed once, never rerun"; a lesson line that lid-close sleep and
  fanless thermal slowdown inflate wall times (provenance unknown to me); a successor-lessons line (packed-refs.lock,
  timing-dependent kills, positive evidence for liveness). No per-job, progress, CPU, memory, host or science figure
  and no clock time. The same outcome label also appeared once in my own output, in a one-line context of the allowed
  `governance/USER_DECISION_BRIEF_308_SUCCESSOR.md` (a token search for QC13-S, section 1 (e)). Nothing here uses it.
* **Not opened:** REVIEW_EXECUTION_INTERRUPTION*, audit/EXECUTION_INTERRUPTION_*, REVIEW_SUCCESSOR_GOVERNANCE_308*,
  INCIDENT_INDEPENDENCE_REVIEW_MBS308* (T6 included), COORDINATOR_EXPOSURE_DISCLOSURE*, anything under
  `p5y_k5_cell308_mb_r1/{review,adjudication,postexec,evidence}/`, BUILD_REPORT sections 6 and 9,
  `governance/SUCCESSOR_GOVERNANCE_308.md`, `ledger/USER_TEXTS_SUCCESSOR_308.md`, the owner-decision files, any other
  agent's scratchpad, anything under `/Users/suzhe/.claude/`. No `git log` on MB r1's branch; no commit subject of
  21e99cf0 / afa93072 printed (hashes and blob ids only). The host power log was read only inside the builders' and my
  own run windows (event type and power source, nothing else).
* **Read:** briefs 53, 46, 49, 50, 50-N; BUILD_REPORT sections 15 and 16 (other sections: headings only); protocol
  sections 8, 8.1, 8.2, 11, 11.1-11.3 and T2's diff of section 4; `git diff 216c465f..T1`, `T1..T2`; in full:
  `code/mbs308_scratch.py`, `mbs308_qualify.py`, `mbs308_rrules.py`, `mbs308_manifest.py`, `mbs308_repin.py`,
  `tests/mbs308_resume_decoy.py`, `tests/mbs308_testlib.py`, `tests/test_mbs308_mutants.py`, `tests/test_mbs308_disk.py`,
  most of `tests/test_mbs308_qualify.py`; the T2 diffs of host / state / driver and of the launch, state, child, synth and
  decoy tests; research `ledger/enospc_2026-09-30/ENOSPC_AUDIT.md`; the finding lines of
  `reviews/REVIEW_OPTIONB_LIVENESS_MBS308.md`; `code/c308_quarantine.py`; the ledger lines of builder4, builder5 and the
  coordinator's lines naming T1 / T2; for section 1 (e) only: lines 11 and 25-30 of the conditions register, two
  one-line contexts each of the decision brief and of MB r1's protocol, and lines 1-2 of the three route reviews.
* **Method.** Committed bytes only: `git show` / `git archive` of 216c465f, T1 and T2 into my scratch, and my own
  checkout of T2 (a `--shared` clone of my own `git clone --bare --no-local` base store). Nothing was edited or run in
  the successor worktree (builder6 was editing it). No git write in any real repository, no real ref, no freeze
  manifest, no marker, grant, pending result or seal, no official qualification run, no system setting changed.

### Re-run on the committed bytes of T2 (host on AC throughout, lid open, 90-102 GiB free by `df -k`)

| run | result | peak scratch | wall |
|---|---|---|---|
| `tests/test_mbs308_static.py` | 10 / 10 PASS | one sandbox | 4 s |
| `tests/test_mbs308_launch.py` | 12 / 12 PASS (synthetic payload; no job or plist left) | < 1 MB | 15 s |
| `tests/test_mbs308_qualify.py` | 23 / 23 PASS | 6 MB | 17 s |
| `tests/test_mbs308_disk.py` | 17 / 17 PASS | 2.128 GiB | 106 s |
| `tests/test_mbs308_state.py` | 50 / 50 PASS | 0.844 GiB | 336 s |
| `tests/test_mbs308_crash.py` | 50 / 50 PASS | 0.849 GiB | 788 s |
| `tests/test_mbs308_decoy.py t_qs_resume_decoy_dev` (decoy 297 block 0, dev ladder; NONTARGET_DRIFT_VALIDATION) | PASS | 0.835 GiB | 336 s |
| `tests/test_mbs308_mutants.py`, full matrix, one run | **136 / 136 KILLED, all 136 by the target's own assertion** (test failed, no error, exit 1, result verified); unmutated 87 / 87 target runs PASS; 224 disk checks passed against 7 GiB; 223 phases cleaned, 140 sandboxes deleted (95.2 GiB in total); M33 killed by its deterministic run (206 s) | 0.907 GiB | 3619 s |
| my own 50 mutants through the namespace's `run_matrix` | 31 KILLED by assertion, 19 SURVIVED (section 7); 28 unmutated targets PASS | 0.966 GiB | 296 s |

No timing-sensitive test failed, so none had to be repeated (load averages 3.2-6.6 while builder6 worked; the host
report inside the disk suite read thermal, memory pressure and free memory NOT_READY during my run).
Power log for my whole window (12:41-14:31Z): no Sleep, Wake or DarkWake entry and AC at every reading; the lid read open before and after. Afterwards I cleaned my own finished suite roots with the namespace's tool (dry run: nothing deleted; `--execute`: 15 units, 4.2 GiB; the only refusals were the disk suite's four planted ACTIVE roots).

## 1. Qualification framework (T1): NOT MET (on (e) only)

* **(a) satisfied.** `aggregate` lists and prints every case whose summary is not a dict with a boolean `pass`, every
  configured case that did not run (official / review) and every unknown case, and fails; `ok` begins with
  `mode != "dev"` and `main` returns 0 for dev without a PASS. Tests `t_aggregator_boolean_pass_and_dev`; MQ01, MQ02,
  MQ04, MQ05 and my YQ1 (unknown case ignored) killed.
* **(b) satisfied on the committed configuration.** 13 cases are PENDING_USER_DECISION at T2 (14 at T1): each returns
  `pass: false`, its status and its `depends_on`; none carries a guessed value (QC13-S's two un-named records are
  `null` and fail closed). With every BUILT case passing, only gates Q8, Q10, Q11 pass and the qualification fails (my
  probe B). Hardening required (R5): a case that names **no gate** is ignored by the aggregate (a failing or a pending
  case with `gates: []` leaves `pass` true and `config_consistency` true: probe B); the committed file gives every case
  a gate, so nothing is wrong today, but the rule "a PENDING case never passes a qualification" rests on the
  configuration alone.
* **(c) satisfied.** Each BUILT case does what protocol 11.1 says and has planted failures that flip it (suites: failing
  / erroring / empty / lying counts; QS-MUTANTS: error, timeout, invalid, survivor, missing, extra; QC09-S: marker
  reverted, label dropped; QC11-S: seven planted breaks and a planted byte change; QC12-S: planted patterns, tokens, a
  wrong pin; QC13-S: thirteen record cases; Q8-S: ten planted faults; R_RULES_CONTROLS: 37 controls). Two sub-checks have
  no planted failure (G-8: Q8-S's commit-pin mismatch; G-9: QC12-S's raw-text-only match).
* **(d) satisfied; the 22 findings are benign.** I reproduced them with the research scanner on 216c465f and T1:
  exactly 22 new, none a tail figure, a band drift, a forbidden import or a forbidden subprocess. Eleven are identity
  strings (schema, ref and branch names and docstrings containing the campaign's own name); five belong to the
  guard-diff check (the two expected diff lines, the QC09 child's text, MQ20's two fragments); six are
  `record_tokens` / `geometry_tokens` selecting cell 308's committed input rows through the driver's pinned reads for
  QC12-S's token scan (two literals, two strings, two matches of one docstring). That scan returns counts and file
  names only, runs only in official / review mode or with `--record-scan`, and nobody ran it on the real records in
  this delta (the tests plant tokens). T2 adds three more identity strings. QC12-S reads the patterns at run time
  through the pin (sha256 and blob at HEAD), builds its planted controls in memory from them, and returns counts and
  file names. The scanner finds no tail figure in the namespace at 216c465f, T1 or T2.
* **(e) NOT satisfied: finding F-1.** Without opening any MBS-2 file I checked every named record by blob id
  (`rev-parse`), ancestry on its ref and the commit's changed paths: all ten resolve, are on their branch, and their
  commit adds or changes the path. For the four records whose files are not MBS-2 files I ran the verifier's own
  `check_record` (status only): M4_USER_RULING_OPTION_B OK, CONSTANTS_RATIFICATION OK, LIVENESS_DELTA_ACCEPTED OK,
  **ROUTE_ACCEPTED: VERDICT_MISMATCH**. The file it names (`reviews/REVIEW_SUCCESSOR_ROUTE_308_R3.md` at 87d0b2b9)
  has `DELTA_ACCEPTED` on line 2; the words ROUTE_ACCEPTED occur once, inside a sentence. QC13-S therefore fails on
  three records, not two, and cannot pass once the two un-named records are named. It fails closed, and builder4 had
  stated that only LIVENESS was checked; but the committed table is wrong and must be corrected in the object (R1).
  **builder4's open point (a40211cc):** the token EXECUTION_ACCEPTED is corroborated by three allowed texts and no
  MBS-2 file: MB r1's protocol section 10 step 6 (the verdict on line 2 is EXECUTION_ACCEPTED or EXECUTION_REJECTED,
  REJECTED stops, and steps 7-8 exist), the register's S14 "met (a40211cc, 9ad632c9, e451e634)", and one research
  ledger line that names a40211cc with that token (counted, not printed); ADJUDICATION_ACCEPTED for e451e634 likewise
  (protocol step 8, the decision brief, one ledger line). Whether line 2 of those files is exactly the token, once, I
  **cannot** check without opening an MBS-2 file, and I did not. The same holds for GOVERNANCE_ACCEPTED,
  INCIDENT_AUDIT_ACCEPTED and T6_FIRED_MITIGATED. After F-1 that is not a formality: the ROUTE token was inferred
  from the register in the same way, and the governance record is likewise a file named `…_DELTA.md`.
* **(f) satisfied, with three readings for the ratifier.** Against protocol section 8 verbatim, by reading and through
  the 37 planted controls (my YR1-YR5, YR9 killed): R-MEM steps 1-6, R-FREE and its attainability, R-EXCL-PCT with its
  single exception and ceiling, R-ALLOW (a), (b) and every never-added class; every number is the ratification's
  (`t_rrules_numbers_are_the_ratifications`); the H3 readings reproduce the item-16 list (4 additions over 39 names).
  READING-1 **confirmed** (AC is part of the rule's prepared host; a gap under 30 s is refused, the strict reading).
  READING-2 **confirmed** (the per-run watchdog peak can only raise P). READING-4 **confirmed** (the gate compares
  processes one by one, so the largest process of the bundle is the quantity the threshold meets). READING-5
  **confirmed** (under condition (b) an interpreter could only sit in a SIP path, which the name and framework tests
  cover; the campaign's own interpreter is excluded by path). READING-3 **needs the ratifier**: "largest peak /
  smallest peak" can equally mean every job peak of that kind and rung in the valid runs; the two readings give
  different k (probe C: two blocks of one rung at 100 and 400 MiB in one run give s = 40/39, k = 3 here, and s = 4,
  k = 8 under the other reading). Also for whoever builds R_RULES_OFFICIAL (F-6): a re-run that itself has a watchdog
  event is silently dropped when another clean run covers its cell (status OK, its peak ignored; probe C); with one
  run per cell the same input is INCOMPLETE_INPUT. Four formula details are not pinned by any control (G-10).
* **(g) satisfied.** The writer runs only with `--freeze` or `--out` outside the repository (MQ34; `t_cli_refusals`);
  the tests run it only inside sandboxes; no `MBS308_FREEZE.json` and no post-freeze directory exists in the tree at
  T1 or T2 or anywhere in the branch's history. Q8-S checks every namespace file (sha256 and blob at HEAD), unlisted
  and absent files, the external and commit-pin key sets, the recorded driver / verifier / configuration hashes, helper
  and platform pins, constants, the guard field, the governance record blobs, required files and `check_bindings`.

## 2. Builder5's repairs (T2): MET

* **(a) O-1.** `process_start` reads `ps -o lstart=` through `_run_ps`, whose environment sets `TZ=UTC0`; it is the only
  reader of a start time (identity, identity_state, identity_alive), so the recorded and the current reading are the
  same function of the same instant whatever the system zone or the caller's TZ. A failed reading is still None, so
  UNKNOWN: no positive-evidence property is lost. `t_identity_state_time_zone_independent` has a real control (raw
  readings under two zones differ) and keeps ALIVE; M62 and my YO1 (the call site reverted) are killed.
* **(b) O-2, O-3, O-4 repaired.** The lock record is staged, fsync'd and linked, so the name never exists without its
  record; the put-back leaves one name; `lock_read` (every reader of the lock) accepts a second name. My YS1 (the link
  turned into a replace: both acquirers hold the lock) and YS2 (no put-back) are killed, as are M64-M66. O-4: a
  whole-output `(name)` is a failed reading; M63 and my YO4 (only `()` matched) are killed. The two leftovers builder5
  lists (a staged file of a process killed before its link; a fully parenthesised real command reads UNKNOWN) are
  accepted: neither can read a live process dead.
* **(c) K-1.** Both single-failure cases exist. My Y5 (failed boot read alone returns DEAD), Y5b (the failed boot read
  made a value and compared) and Y6 (failed command read alone returns DEAD) are all killed by
  `launch::t_identity_state_positive_evidence`. One variant survives every launch test and the ps-failure tests of the
  state and crash suites (G-1): the command case is planted by replacing `process_command_sha256` itself, so the guard
  inside it that turns an empty reading into None is not exercised.

## 3. Disk-safety and scratch-lifecycle gate (T2): NOT MET (on the base-store rule; two smaller points)

Satisfied, by reading, by the suite, by builder5's mutants and by my probes D:

* the three classes (no record, an empty record directory, an invalid record, an unfinished record, a live or UNKNOWN
  owner are ACTIVE; my YD5 killed); cleanup lists only sandbox clones of bare stores and bare stores, never a file;
  look-alikes stay; evidence beside a sandbox stays byte for byte; dry run is the default (MD10); a root that is, lies
  under or contains a worktree or the common dir is refused before any walk (refs, marker, pending, spool, seals; the
  real common dir and the campaign's qualified paths are in the set even from a copy); an unreadable repository refuses
  (probe D2); a root or unit reached through a symlink, `/tmp` included, is refused (YD1 killed; probes D6);
* free space: a failed, planted-failed or raising probe is None and never passes; an empty probe list never passes; a
  planted reading can only lower; the driver's gate requires an int at or above the ratified 2 GiB and execute and
  resume refuse before any ref, spool result or attempt-counter move; the verifier refuses before its preconditions
  and writes nothing; the runner refuses at its start;
* the runner cleans each phase after its verified result: my matrix and my own mutant run never held more than about
  one sandbox (0.907 GiB and 0.966 GiB).

Not satisfied:

* **F-2 (blocking).** A bare base store inside a FINISHED root is deleted while a sandbox of an ACTIVE root elsewhere
  borrows its objects (probe D15 ii: the live sandbox's HEAD is unreadable afterwards). The test library takes the
  scratch root and the base store as two independent variables and records a process only in its scratch root, so a
  store reused from an earlier run's directory has no record of its live users; `in_use` sees only clones under the
  cleaned root. Protocol 8.2 says "a store still borrowed is kept". The wired uses are safe (the verifier's store sits
  in its own ACTIVE work root; the runner's phases are under the root that is cleaned: probe D15 i), and by the letter
  of brief 50's class definition that store is disposable; but the effect is exactly what the gate exists to prevent,
  a cleaner pulling state from under a live run, and the user's requirement is "NEVER". If the coordinator or the user
  holds that the class definition governs, this point becomes a hardening item and the text of 8.2 must still be made
  true.
* **G-3.** The rule "a store still borrowed is kept" has no test that can fail: with `in_use` returning False the whole
  disk suite passes (YD4).
* **F-3.** A deletion is logged after it happens: when the deletions log cannot be opened (planted: a symlink) the unit
  is gone, no record is written, the report is lost in the exception (probe D3). Abnormal and loud, and only a
  disposable unit goes, but "every deletion recorded" does not hold on that path.
* **G-4.** The verifier's own per-phase wiring has no test that can fail: with its gate replaced by a constant pass
  (YD9), or with a refused phase mapped to `pass: true` (YD11), the disk suite passes. The start gates (MD26, the runner
  test) and `run_gated` itself (MD22-MD25) are covered; the runner's per-phase check is exercised only with a passing
  reading.

Observations, not blocking: the nearest recorded root governs even when the root being cleaned is ACTIVE (probe D1:
a nested FINISHED root's units go while the outer root's live owner is recorded; requiring every recorded root between
the unit and the cleaned root to be FINISHED would cost the wired uses nothing); a record's `root` field is not
compared with the root it lies in (D12: a copied scratch directory inherits FINISHED); a bare store is judged by shape,
not by reconstructability (D5); a short window remains between the re-verification and the end of a deletion, and the
re-verification has no test (YD2).

**Thresholds.** QUAL_MIN_FREE_BYTES is derived from recorded measurements plus a written margin: roundup_GiB(2 x
(2171 + 459) MiB + 1 GiB) = 7 GiB, bound in code and protocol (`t_thresholds_derived`; MD27 and my YD12 killed). I
re-measured three inputs: one sandbox 0.835 GiB (896,765,952 bytes deleted per phase), QS-DISK's peak 2.128 GiB (2.119
recorded), my base store 465 MiB (458.4 recorded two days earlier; "grows with the repository"); with my figures the
formula still gives 7 GiB. The execution threshold is the ratified 2 GiB, unchanged; no amendment is proposed and
none is needed (the execution's own writes are MB-scale); nothing was made looser. No portion is left
PENDING_USER_DECISION, and I accept the reasoning for sandbox-sized cases, with one condition: P_max and B are
measured constants, so they are re-measured on the final pre-freeze bytes once the decision-dependent cases exist.
**Note (c):** QUAL_MIN_FREE_BYTES is bound by the frozen hash of `code/mbs308_scratch.py`; adding it to the manifest's
recorded constants is a recommendation, not a requirement. **Note (d):** roots without a record stay ACTIVE and are
never cleaned: correct, the safe side.

## 4. Re-pin tooling, R-MEM inputs, QS-RESUME-DECOY (T2): MET

* **(a)** Dry-run by default (MR01, MR02, MR04); `platform --write` is refused, only `--write-platform` writes;
  PLATFORM_PINS are unchanged from 216c465f (AST comparison) and equal this host's readings (dry run, nothing written).
  The generator reproduces the committed DRIVER_DIFF.md byte for byte at 216c465f, at T1 and at T2, and T2's file is
  its output for T2's driver with T1's classes (22 hunks; probe A; `check` in my checkout: nothing stale). **F-4:** the
  stated refusal "a hunk touching a carried definition is SCIENCE-GLUE and the tool fails" cannot fire for a change in
  a function body: the carried set is recomputed from the same two files, so a changed function simply leaves it. In
  my probe such a change is refused as HUNK_WITHOUT_CLASS, and with `--classes` it is accepted as LIFECYCLE and the
  function silently drops out of the header's carried list (YRP3 survives). RC1 itself is safe: QS-STATIC compares a
  fixed list of 34 names. Repair the check (compare against the committed header's list) or withdraw the claim.
  The refusal of `--write-platform` on a failed reading is untested (YRP1).
* **(b)** Only `main()`'s decoy branch and the helper pins changed in the driver; no carried function changed (RC1 /
  MBS-9 pass); the sampler is a reading thread that signals nothing; my dev decoy's certified output is byte-identical
  between the uninterrupted run, which samples, and the resumed run. Recorded on real decoy science in my run: D 57.5
  MiB, 274 readings, 0 failed, largest spacing 0.51 s; synthetic: 21 readings, largest spacing 0.51 s. Two recorded
  fields are not protected by any test (G-2): the ladder (a dev-ladder run recorded as "frozen" would satisfy R-MEM
  step 1) and D's source.
* **(c)** QS-RESUME-DECOY is decision-independent and correct; BUILT stands. Its definition (a decoy uninterrupted
  against the same decoy SIGKILLed after k = n // 2 checkpoints and resumed; every non-provenance key equal, timing
  stripped) reads the job set, n, k and the keys from the runs, so it is the same case under MBS-7 (i) and (ii); MBS-8
  changes only caps, and a cap hit fails closed; it feeds no constant. Two maintenance dependencies fail closed (the
  `decoy()` signature; a new timing or provenance key name). My dev run: PASS, n = 4, k = 2, signal 9, 2 checkpoints,
  served 2, computed 2, rejected 0, 643 + 883 leaves equal, 1548 certified leaves, host CLEAN. A dev-form record never
  passes the case (MQ35, MQ36 and my YQ10 killed).

## 5. Host-readiness checklist: MET

Every item the user listed is in protocol 8.1 and in the read-only report: automatic macOS and critical-update
installation, automatic restart, AC, sleep prevention and the lid, thermal, the two disk thresholds, memory pressure
and free memory, boot identity, host identity (platform pins); also low-power mode, exclusivity, no other campaign job
and no concurrent sandbox-heavy work. Each gated item names a gate that exists in `preflight_gates` / `host_preflight`
/ `check_platform`; every gate behind an item of the user's list fails closed on an unreadable reading (the two gates
that do not, exclusivity and the pidfile gate, are note (a) in section 7). No setting is ever changed: no command that
writes a setting occurs in `code/` or `tests/` (the host readings are `pmset -g`, `defaults read`, `ioreg -r`,
`sysctl`, `notifyutil -g`, `launchctl print`; the launcher's `bootstrap` / `bootout` act on the campaign's own job);
the report's own code holds two query vectors and no write call, and the settings it reads were equal before and
after it ran.
**Note (e), ruled:** a report that is not a gate is acceptable, because every required item is either gated or a
stated user action. Two corrections (R7): `automatic_restart` reads RECORDED even when `pmset` could not be read
(it should be UNKNOWN), and "recorded" items are recorded nowhere unless someone runs and keeps the report, so the
official qualification record should embed it, and the place where the user's actions (lid, quitting apps, no
concurrent heavy work) are recorded should be named.

## 6. Integrity and scope: MET

* T1 is insertions only (8 files, 0 deleted lines); T2 touches 20 files, all inside the namespace. Module constants by
  AST: driver, only HELPER_SHA256; host, + PS_TZ; state, + RssSampler.INTERVAL_S (0.5, the rule's own bound); launch,
  guard, rrules, manifest unchanged; MEM_CAP, MEM_POLL_S, FREE_MEM_MIN, EXCL_CPU_PCT, WORKERS, the caps, MIN_FREE_DISK
  and MAX_RESUMES are as before. The one new number is QUAL_MIN_FREE_BYTES, which the brief allows. T2 removed from the
  protocol only the old QS-RESUME-DECOY text and one sentence of 11.2; no rule text changed. M01-M57 and MQ01-MQ34 are
  unchanged at both steps. Every sha256 prefix in BUILD_REPORT 15.1 (5, against T1) and 16.1 (19, against T2) matches.
* No ref under `refs/p5y-k5-cell308-mbs-r1/` in the real repository. Ledger: builder4 6 lines, builder5 10 lines, all
  pre-grant classes, 0 target evaluations, no LEAK_FLAG; the verifier's `ledger_check` passes on today's ledger.
* **Host events.** The power log shows the clamshell sleep on battery at 14:07Z on 2026-09-30 (battery from 14:06:55Z,
  AC again at 14:28:49Z) and nothing else in builder4's window; the broken crash run was replaced by a re-run on AC,
  and the matrix ran after 14:28Z with no sleep event. builder4's scratch-copy results of that morning lay inside the
  low-disk interval of the ENOSPC audit; they are superseded by the integrated runs (free >= 112 GiB), by the
  coordinator's reproduction and by mine. builder5's final run (11:15-12:35Z on 2026-10-01): AC, no sleep event.
  **No evidence the delta relies on was produced during a sleep, on battery or under low disk.**
* **Exposure statements.** builder5's is the memory index only. builder4 also displayed the subject line of MB r1's
  postexec commit, which it says carries a qualitative chronology with clock times. I find no path from it into T1:
  every rule number is checked against the ratification text, no cap, timeout or threshold was chosen, the case table
  comes from MB r1's configuration and the briefs. Whether M4's "non-holder" tolerates that display is for the
  authority of the T6 / M4 ruling, which I may not read; it should be stated at the freeze.

## 7. Findings, coverage gaps, rulings

**Findings in the delta**

| id | where | what | effect |
|---|---|---|---|
| F-1 | T1 config, QC13-S | ROUTE_ACCEPTED expects a token that is not line 2 of the named file (line 2 is DELTA_ACCEPTED) | QC13-S cannot pass; fails closed |
| F-2 | T2 `mbs308_scratch.cleanup` | a base store borrowed by a live sandbox outside the cleaned root is deleted | a live run loses its objects |
| F-3 | T2 `cleanup` | the deletion precedes its log record | an unrecorded deletion when the log cannot be opened |
| F-4 | T2 `mbs308_repin` | the SCIENCE-GLUE refusal cannot fire for a body change | a stated check is vacuous (RC1 itself is gated by QS-STATIC) |
| F-5 | T1 `aggregate` / `config_consistency` | a case naming no gate is ignored | latent (the committed configuration is sound) |
| F-6 | T1 `r_mem` | an invalid re-run is dropped when a clean duplicate covers its cell | latent, for R_RULES_OFFICIAL |
| F-7 | T2 host report | RECORDED on an unreadable reading; READY when the pidfile or `ps` reading is not positive | a report, not a gate |

**Coverage gaps (my surviving mutants; the code is right in each case).** Each was also run against the whole suite
or the further tests named, where that could change the answer (the whole qualify suite with YQ7, YQ9, YR6, YR7, YR8, YR10 one at a time, 23 / 23 each; the whole launch suite with Y6b, 12 / 12; the whole disk suite with YD2 + YD4 + YD10, with YD9, with YD11 and with YRP1 + YRP3, 17 / 17 each; Y6b against ten ps-failure, pidfile and lock tests of the state and crash suites, YS3 against five lock tests, YM2 + YM6 against the one test that reads those fields: all pass).

| id | mutants | no test fails when … |
|---|---|---|
| G-1 | Y6b, Y6c | an empty `ps -o command=` reading is hashed instead of read as failed (a live process then reads DEAD) |
| G-2 | YM2, YM6 | a dev-ladder decoy is recorded as "frozen"; D is taken from the children instead of the driver |
| G-3 | YD4a, YD4b | a base store still borrowed by a kept clone is deleted |
| G-4 | YD9, YD11 | the verifier skips its per-phase disk check; a disk-refused phase passes |
| G-5 | YD2 | a unit is not re-verified just before its deletion |
| G-6 | YD10 | the verifier does not check the repository volume (same volume here) |
| G-7 | YS3 | `lock_read` follows a symlink |
| G-8 | YQ7 | Q8-S ignores a commit-pin mismatch |
| G-9 | YQ9 | QC12-S drops a raw-text-only match in post-freeze JSON |
| G-10 | YR6, YR7, YR8, YR10 | D is the smallest driver peak; the per-run watchdog peak is left out of P (READING-2); a rung's per-run peak is its last job's (READING-3); the step-5 sum counts one worker fewer |
| G-11 | YRP1, YRP3 | PLATFORM_PINS are written after a failed reading; a SCIENCE-GLUE hunk does not fail the generator |

Killed by assertion (31): Y5, Y5b, Y6, YO1, YO4, YS1, YS2, YM1, YM3, YM4, YD1, YD3, YD5, YD7, YD12, YQ1-YQ6, YQ8,
YQ10, YQ11, YMF, YR1-YR5, YR9.

**Rulings on builder5's notes**

* **(a) `busy_processes` fails open on a failed `ps`: confirmed, and the fix is required before the freeze (R6).** A
  failed reading yields no rows, so `host_exclusive` is true. It predates the delta (not a ground against T1 / T2) and
  needs no number. The proposed line needs `busy_processes` to return None on a failed reading; add a planted test and
  a mutant. Same class, for the coordinator: the start gate `no_other_campaign_job` reads the pidfile through
  `identity_alive`, so a failed `ps` on a live recorded driver reads STALE and the gate passes.
* **(b) READING-6: needs the ratifier.** The rule's words bound the sampler; the function checks only the nominal
  interval. The largest spacing was 0.51 s in both of my runs, under load. Until it is ruled, R_RULES_OFFICIAL must
  not accept a record whose largest spacing exceeds 0.5 s silently. A second reading for the same ruling (READING-7,
  mine): the sampler measures growth only for a process it has already seen, so a fresh worker's rise before its first
  reading is never counted in g.
* **(c), (d), (e):** ruled in sections 3 and 5.
* builder4's open questions: 1 is the user's (reviewSEQ: not determined by accepted governance); 2 is closed by T2
  subject to READING-6 / 7; 3 is section 1 (f); 4 is F-1; 5 (the named exception of QC11-S) is accepted: it exempts
  only occurrences inside the one function and a hit anywhere else fails (tested); 6 is covered by 8.1.

## 8. Is T2 IMPLEMENTATION_ACCEPTED as a pre-freeze candidate? What remains before any freeze

**Not as committed.** T2 is a sound base: the repairs are local, and nothing else in sections 1-6 needs to be reviewed
again unless it is touched. After R1-R4 and a narrow re-check of exactly those items, with the affected suites and
mutants re-run, it can be accepted as a pre-freeze candidate with its decision-independent qualification tooling.

**Needs no user decision**

* R1 (F-1): correct the ROUTE record, and have every named governance record checked against the real repository by
  the verifier's `check_record`, status only, by a party allowed to let a program open the MBS-2 files; correct any
  other mismatch; record the result.
* R2 (F-2, G-3): make "a store still borrowed is kept" true (for example, record each user of a base store where the
  store lives, so that its root is ACTIVE while a user is alive) or refuse what cannot be protected, and state the
  rule exactly in 8.2; a test and a mutant for the in-root rule and for the cross-root case.
* R3 (F-3): open the deletions log before the first deletion, or write the record first.
* R4 (G-4): a test in which the reading falls after the start, for the verifier and for the runner, and a mutant on
  the verifier's wiring.
* R5 (F-5), R6 (note (a)), R7 (F-7, note (e)), F-4, and the tests for G-1, G-2, G-5 to G-11: before the freeze; they
  can ride with builder6's delta and its review.
* The ratifier: READING-3, READING-6, READING-7, and the re-run case F-6.
* Freeze preparation: the implementation review that accepts the bytes to be frozen, named in QC13-S; every later
  build agent added to the configuration's ledger agents (builder6 is not in the list); HELPER_SHA256 and
  PLATFORM_PINS re-pinned on the qualification host and DRIVER_DIFF.md regenerated with the tool; P_max and B
  re-measured on the final bytes; the host prepared (the report in my run: automatic installation USER_ACTION,
  exclusivity USER_ACTION, thermal, memory pressure and free memory NOT_READY); the M4 authority's word on builder4's
  disclosed display.

**Needs the user's decisions**

* MBS-7: QC01-QC08, Q1_theory, QC09-SCI, MBR1_REPRO (11 cases).
* MBS-8 and the sequencing question of protocol 11.2: Q12_caps, R_RULES_OFFICIAL; how the frozen code comes to carry
  the rule outputs.
* S16(c) and MBS-6: the user's freeze decision record, named in QC13-S (it fails closed until then).
* S1: the user's ruling the grant must carry; before any target step, not before the freeze.

(The brief notes that owner decisions have since been recorded and that another builder is implementing what depends
on them; those files and that work are not part of this object and I did not open them.)

## 9. Integrity of this review

**New cell-308 target evaluations: 0.** Nothing evaluated a cell 305-309 or a drift in the band or its mirror; cell
309 untouched. The only science was one run of the dev decoy on cell 297 block 0 (`t_qs_resume_decoy_dev`); its values
stay in my scratch, unread. Every other run used the synthetic evaluator or the synthetic launchd payload in sandboxes
on my own base store. Ledger (agent `reviewQ6`, `c308_quarantine.log_event`, target_evaluations 0, no LEAK_FLAG):
INFRASTRUCTURE and SYNTHETIC_VALIDATION 2026-10-01T12:44:38Z; SYNTHETIC_VALIDATION, NONTARGET_DRIFT_VALIDATION and
SYNTHETIC_VALIDATION 13:04:46Z; REVIEW at the end. My sandboxes were deleted after the runs; my checkout and my base store were
deleted at the end; the JSON reports, logs, probes and my mutant definitions stay in
`scratchpad/reviewQ6/{reports,logs,probes}`.
