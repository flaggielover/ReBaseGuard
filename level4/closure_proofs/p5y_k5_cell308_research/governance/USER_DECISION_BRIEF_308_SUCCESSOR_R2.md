# Decision brief r2 for the user: the cell-308 successor MB-S (freeze decisions S16(c), MBS-6, MBS-7, MBS-8; grant ruling S1)

**Revision r2.** Drafted by `briefer2`, a fresh drafter who holds no MB r1 run observation (brief 48, research
`5fdbddaf`). The T6 ruling's M4 keeps exposed parties out of this role. A research scanner and a separate fresh
non-holder reader check this draft (MBS-10) before you receive it.

**Relation to r1.** r1 (`governance/USER_DECISION_BRIEF_308_SUCCESSOR.md`, last committed `03ca1bcf`) stays unchanged
and is not withdrawn. r2 restates the same five decisions in more detail and updates the facts. Where the two differ on
a fact, r2 is the later statement; §0 lists every such change. r1's verbatim sections D (the governing texts O1–O5) and
E (your own words) remain the reference texts; §10 below points to them without re-quoting them.

**What this brief contains.** The decisions the governance leaves to you, option by option. **It contains no
expectation of MB-S's outcome**: no margin, estimate or likelihood of MB-S closing or not closing cell 308, no "worth
running" argument, nothing about the lost MB r1 result, and no observation of the lost MB r1 run (MBS-10, S13).

**What it authorises.** Nothing: no freeze, no qualification run, no grant, no target step. New cell-308 target
evaluations: **0**. MB308 r1: CELL308_EXECUTION_INDETERMINATE (ADJUDICATION_ACCEPTED `e451e634`), consumed, never
re-run. Cell 308: OPEN.

**Not proceeding is always available.** At every decision below, withholding or deferring is an option on the same
footing as proceeding, wherever the texts allow it. A "default" is shown only where an option has an engineering reason
independent of any scientific outcome, and it is labelled so; otherwise the decision says "no default".

## 0. What changed since r1

| # | r1 said | now | evidence |
|---|---|---|---|
| 1 | implementation review pending | IMPLEMENTATION_REJECTED at `afba20e5` (DEF-1 to DEF-4) → repairs R1, R2, R4 at `35cabb50` → DELTA_REJECTED (R1, R2, R4 met; R3 open; correction C-1) → R3 + C-1 at `191ce4a9` → **DELTA_ACCEPTED: IMPLEMENTATION_ACCEPTED as a pre-freeze candidate**, subject to your ruling on one M4 point (row 3) | reviews `6d3a44cd`, `99185dcb`, `58cfe66b` |
| 2 | T6 condition M1 (itemised provenance trace) pending | the non-holder implementation reviewer traced every constant: none traces to the MB r1 target run, and none can affect Γ; 20 a-priori items were ratified or set by rule by a non-holder ratifier (CONSTANTS_RATIFIED_WITH_CHANGES); R3 ruled MET. Whether the T6 reviewer has recorded M1 as discharged is not in a file available to me | reviewIMPL §10; `3c2a7854`; `58cfe66b` |
| 3 | — | **your T6/M4 ruling: option B.** A genuine non-holder (builder3) withdrew the exposed editor's application of ratification items 16 and 31 (step W, `4a960e06`) and re-applied them from the ratification text (step N, `b0dd8e93`); the coordinator's mechanical byte-level re-check is PASS | ledger 2026-09-30T05:52:05Z (research `5e7b8cdc`); `b3cc9675`, `ledger/OPTION_B_RECHECK.json` |
| 4 | — | **liveness delta (step L, `216c465f`)**: a recorded process now counts as alive unless there is positive evidence of its death; a failed `ps` or boot-UUID reading never counts as death (fail closed, no timeout) | BUILD_REPORT §14; protocol draft §4 |
| 5 | — | a fresh narrow independent review of W, N and L, including the disk incident (brief 47): **pending** | brief 47 (`3ac53e11`, corrected `324ba37f`) |
| 6 | — | **ENOSPC incident (2026-09-30)**: the data volume ran nearly full during sandbox-heavy test runs; one test run was contaminated, preserved and superseded; a clean-disk re-run on the committed bytes of L was identical; a disk-space and scratch-lifecycle gate is to be designed and reviewed before the freeze (your instruction of 2026-09-30) | `ledger/enospc_2026-09-30/ENOSPC_AUDIT.md` (`3ac53e11`) |
| 7 | — | **qualification framework under construction** (non-holder builder4, brief 46): built in scratch, not yet integrated into the successor worktree; the cases that depend on your decisions fail closed as PENDING_USER_DECISION | brief 46 (`e2d2b026`); status as reported by the coordinator, not seen by me |
| 8 | — | four operational constants (MEM_CAP, FREE_MEM_MIN, EXCL_CPU_PCT, EXCL_ALLOW) are now **set by written rules at the freeze** from official qualification evidence (R-MEM, R-FREE, R-EXCL-PCT, R-ALLOW). This opens a sequencing question (§8) | ratification `3c2a7854`; protocol draft §8 |
| 9 | caps: two options | unchanged, but the reviews ask that your MBS-8 record state the **per-attempt, awake-time EVAL_CAP** semantics and show the **worker-death trade** (§6) | reviewIMPL D5 and D10 notes |
| 10 | host readiness relayed from the builder's BUILD_REPORT | the builder was an exposed party, and the r1 reader left that open (Q-4). **r2 cites only non-holder host readings** (§9) | reader check `READER_CHECK_USER_DECISION_BRIEF_308_R2.md` Q-4 |

## 1. Where the successor stands (as of drafting, 2026-09-30)

| item | status | commits |
|---|---|---|
| governance | GOVERNANCE_ACCEPTED (SUCCESSOR_ALLOWED_WITH_CONDITIONS; preparation permitted up to, not including, the freeze) | determination `e5871aa6`; A1 `ce145e51`; E1 `a7c969e8`; accepted `00a432df` |
| route | ROUTE_ACCEPTED: MB-S, MB r1's science byte-identical, new lifecycle only | audit `bddd85f8`; A1 `ce145e51`; E1 `a7c969e8`; E2 `6a33f22d`; accepted `87d0b2b9` |
| incident re-rating | INCIDENT_AUDIT_ACCEPTED; T6_FIRED_MITIGATED; rating MEDIUM–HIGH (upper end) only under M1–M6, otherwise HIGH | `b7e62dec`; `ff2280e9` |
| MB r1 closeout (S14) | met | `a40211cc`, `9ad632c9`, `e451e634` |
| pre-freeze build | branch `p5y-k5-cell308-mbs-r1`, head `216c465f` (after `191ce4a9`, W, N, L) | see §0 |
| narrow review of W, N, L | pending | brief 47 |
| qualification framework | built in scratch, not integrated; option-dependent cases PENDING_USER_DECISION | brief 46 |
| disk-space / scratch-lifecycle gate | to be designed and reviewed before the freeze | ENOSPC audit |
| still open before any freeze (review `58cfe66b`, updated) | qualification verifier, manifest writer and leak scanner (the framework); the official decoys under the launchd launcher with the R-rule inputs; re-pinning HELPER_SHA256 and PLATFORM_PINS; full MBR1_REPRO and QS-RESUME-DECOY; your disabling of automatic macOS / critical-update installation; your decisions S16(c), MBS-6, MBS-7, MBS-8; S1 before any grant | — |
| cell-308 target evaluations | 0 new; cell 308 OPEN; MB r1 INDETERMINATE for ever | — |

## 2. The order of decisions

| decision | binds at | must exist before | can be recorded |
|---|---|---|---|
| S16(c) freeze permission | freeze | the freeze **and** the official qualification (governance A1 S16) | now or later |
| MBS-6 finality | freeze | the freeze (it becomes frozen protocol text) | now or later |
| MBS-7 members | freeze | the freeze; under (ii) also before any new build work | now or later |
| MBS-8 caps | freeze | the freeze; under (ii) its values also need the official decoy runs | now or later |
| S1 grant ruling | grant | any grant, which needs QUALIFICATION_ACCEPTED first | any time before the grant |

Mechanical dependencies, stated without preference:

* **MBS-7 comes first in effect.** Option (ii) changes the object everything else applies to: the science, the
  qualification cases, and the decoy runtimes that feed MBS-8 (ii) and the R-rules.
* **S16(c) and MBS-8 travel together.** Governance A1 §1 (O4 reconciliation) says the freeze decision "must also
  settle the caps question".
* **MBS-8 and the official decoys.** If MBS-8 is recorded before any official decoy run, neither cap option is chosen
  with its resulting values in view. The texts do not require this order; it is a mechanical observation.
* **S1 last, or earlier.** The protocol draft's order is freeze → official qualification → independent qualification
  review → your S1 ruling → grant (protocol draft §1). Your C4 ruling for MB r1 was given while a qualification was
  still running and entered the grant only after the review was accepted (`ledger/USER_RULING_C4.md`). Either way the
  grant needs QUALIFICATION_ACCEPTED (your U7).
* **Now versus after the official qualification.** All four freeze-time decisions can be recorded now. None of them
  causes a freeze by itself: S16(b) and the open items of §1 remain. Known only after the official qualification: whether
  it passed, the R-rule values, the MBS-8 (ii) values if chosen, and the result of the Q12 cap check.

## 3. Decision S16(c): permission to freeze MB-S (it also gates the official qualification)

1. **The exact question.** Do you record a decision that covers the MB-S freeze under MB r1's protocol §14 and its
   qualification review G2 ("no r4 with the same caps … without a new explicit user decision recorded before it";
   r1 §D, O4)? Governance A1 S16 makes this condition (c) of four before any successor freeze and any official
   qualification (GC-9).
2. **Options.** (A) give the permission; (B) withhold it (this includes "not now"). **No default.**
3. **What changes mechanically.**
   * (A) S16(c) is met, and nothing else. The freeze still needs S16(a) (met, `00a432df`), S16(d) (met, S14) and
     S16(b): route conditions RC1, RC2 and RC6 established as facts, which the register places at the qualification.
     It also needs the open items of §1. A freeze is then a commit on `p5y-k5-cell308-mbs-r1` binding the frozen
     protocol, a freeze manifest (Q8-S), the re-pinned helper and platform pins, the R-rule constants and your MBS-6,
     MBS-7 and MBS-8 choices. The official qualification runs at that commit. In the framework under construction,
     QC13-S checks that your freeze decision record exists and fails closed while it is absent (brief 46).
   * (B) No freeze and no official qualification. MB-S stays an unfrozen, target-free pre-freeze candidate at
     `216c465f`. Preparation continues only up to the freeze (governance A1 classification).
4. **Scientific consequence.** None. This decision does not touch the science; Decision MBS-7 (§5) decides whether it
   stays MB r1's, byte-identical.
5. **Governance consequence.** (A) S16(c) met, and O4 / G2 answered for MB-S. The S1 ruling is still required before
   any grant. The result-chasing rating is not changed by this decision. (B) S16(c) stays open in the register. Under
   either option MB r1 stays INDETERMINATE for ever (O1 reconciliation) and cell 308 stays OPEN.
6. **Runtime / resource consequence.**
   * (A) The official qualification: the namespace's test suites and full mutant matrix (a full matrix leaves about
     0.8 GB of sandbox per mutant, about 40 GB per run, unless cleaned: ENOSPC audit); the official decoy runs with the
     real science on decoy cells 297 and 316 under the launchd launcher (hours-long computations); and at least 10
     prepared-state host readings 30 s apart (R-FREE, R-ALLOW). The host must be prepared (§9), and the platform must
     not change from the qualification to the end of any execution window (RC2).
   * (B) Nothing beyond continuing target-free preparation. The platform question of §9 still applies if MB-S is to
     stay on the unchanged-science branch later.
7. **Qualification consequence.** (A) The official qualification can start once all of S16 holds and the framework
   is integrated and reviewed. Cases that depend on MBS-7 and MBS-8 stay PENDING_USER_DECISION until those are
   recorded. (B) No official qualification; QC13-S fails closed.
8. **Failure / recovery consequence.** (A) A qualification failure or a QUALIFICATION_REJECTED stops the campaign
   before the target (your U7). MB-S's own stop rule is not frozen yet; MB r1's precedent is "STOP (no same-round
   repair; a successor campaign only)" (MB r1 protocol §10 step 3), and a code change needed after the qualification
   review meant STOP (G2). Nothing is consumed by any of these. (B) Nothing can fail. The accepted pre-freeze status
   holds only while its inputs (MB r1's bytes, the pins, the platform) stay unchanged.
9. **Target exposure.** Neither option evaluates cell 308 or changes the count. The official qualification uses decoy
   cells and committed-record reproduction only (MBS-12). A target step still needs QUALIFICATION_ACCEPTED, your S1
   ruling and a grant: (A) makes those steps reachable; (B) keeps them unreachable.
10. **Reversible before the freeze?** Yes. The texts I read contain no rule on withdrawing a recorded decision before
    the freeze, and nothing is frozen before the freeze commit, so a new recorded decision can replace (A) or (B).
    After the freeze, changing a frozen item means a new freeze (MB r1's G2 precedent).
11. **Existing evidence.** Governance A1 §1 (O4, G2 reconciliation) and §4 S16; erratum E1; register rows S16 and
    RC2; r1 §A.1; review `58cfe66b` ("Remaining before any freeze"); brief 46 (QC13-S); ENOSPC audit.
12. **Unresolved uncertainty.** The narrow review of W, N, L is pending. The framework's integration and its protocol
    §11.2 are pending. The disk gate is not designed yet. The sequencing question (§8) is open. S16 gates the official
    qualification on S16(b), while the register places RC1, RC2 and RC6 "as facts at qualification"; the protocol text
    that orders these is not written yet.

## 4. Decision MBS-6: finality of an MB-S INDETERMINATE

1. **The exact question.** If MB-S ends in an INDETERMINATE-class outcome, is that final for route MB on cell 308?
   (Register MBS-6; S1 item 6; decided before the freeze.)
2. **Options.** (i) **final**: an INDETERMINATE-class outcome of MB-S ends route MB on cell 308; (ii) **not final**: a
   further successor may be governed after an MB-S INDETERMINATE, through its own process and ruling.
   **Default: (i), as recorded by the successor incident re-rating** (reviewINC2, `b7e62dec`, condition MBS-6; register:
   "recommended: final"). I label it an **engineering default (not a scientific recommendation)**: it fixes in advance,
   before any MB-S outcome exists, how many times route MB may consume cell 308. The re-rating's own reasoning is in a
   file that is not available to me (MBS-2 reading restriction), so I cannot state it. (ii) is equally available.
3. **What changes mechanically.** No code. The frozen protocol carries the choice where the draft now carries S7's text
   (outcome table, protocol draft §10: "any further successor needs a further governance process and user ruling").
   (i) replaces that with the end of route MB on cell 308; (ii) keeps it. The S1 ruling records the choice (item 6), and
   the MB-S adjudication applies it (MBS-14).
4. **Scientific consequence.** None. The value path and the determinism argument are the same under both options. An
   INDETERMINATE carries no value.
5. **Governance consequence.** Under both options, any evaluation of cell 308 after the MB-S marker, of any route,
   starts at a risk rating not lower than HIGH (MBS-5(b), route E2).
   * (i) After an MB-S INDETERMINATE there is no further route-MB evaluation of cell 308. Cell 308 stays OPEN. Any
     other route on 308 follows the path of your brief's §26 (r1 §E).
   * (ii) A further successor, and so a further consumption of cell 308, becomes governable, but only through a
     further governance process and a new ruling (S7).
6. **Runtime / resource consequence.** None for MB-S. Under (ii), a possible later campaign would need its own host time.
7. **Qualification consequence.** Brief 46 names no qualification case that depends on MBS-6. The frozen protocol text
   must carry the choice, and QC13-S checks that your freeze decision record exists.
8. **Failure / recovery consequence.** The INDETERMINATE class (protocol draft §6, §10) includes:
   * an EVAL_CAP hit or a per-job CPU-cap hit;
   * a memory-watchdog kill, and **any worker death, including a transient OS kill of one worker**: MB-S treats it as
     an execution failure, not as a resumable interruption (deviation D5, accepted; the implementation review asked
     that this trade be shown to you with MBS-6 and MBS-8);
   * a platform change found at a resume;
   * the resume budget (3 resumes) or the 7-day deadline exhausted;
   * two consecutive verification failures of one checkpoint;
   * a control failure at a resume;
   * any stop outside the frozen rules (MBS-5(a)).

   Under (i) any of these ends route MB on cell 308; under (ii) any of these leaves a further successor governable. A
   host interruption (a reset, a power loss, the hosting app's death) is not INDETERMINATE by itself: it leads to a
   mandatory resume within the budget and the deadline.
9. **Target exposure.** Neither option changes the current count or when a target step becomes possible. (i) bounds
   route MB's consumptions of cell 308 at two (MB r1 and MB-S). (ii) leaves that bound to a later process and ruling.
10. **Reversible before the freeze?** Yes, by a new recorded decision; after the freeze it is frozen protocol text.
11. **Existing evidence.** Register row MBS-6; r1 §A.3; governance S7 and A1 §3 item 6; route E2 (MBS-5(a), (b));
    protocol draft §6, §10; implementation review D5 note; ratification item 18.
12. **Unresolved uncertainty.** The re-rating's reasoning for (i) is not available to me. The texts I read do not say
    whether a later route carrying the C11R-I2 / COR-T members (§5) would count as "route MB" for option (i). They also
    do not say how §26 applies when MB-S ends INDETERMINATE, with no observed outcome.

## 5. Decision MBS-7: the C11R-I2 / COR-T members

1. **The exact question.** Before the freeze, do you keep MB-S's science unchanged (MB r1's, byte-identical), or add
   the two further members C11R-I2 and COR-T? (Register MBS-7; route E1 DR1; route re-check R3-N2. Governance E1 D1
   requires this trade to be put to you.)
2. **Options.** (i) keep MB-S unchanged; (ii) add the members before the freeze.
   **Default: (i), an engineering default (not a scientific recommendation).** Engineering reason: (i) is the object
   that has been built, reviewed and accepted as a pre-freeze candidate; (ii) needs new code, a theorem revision, new
   reviews, a new qualification and a fresh re-rating. Separately, the accepted route audit records keeping the science
   unchanged as a *preference* under S4, not a prohibition (route A1 §1 as corrected by E1; route review check 3). S4
   admits changed science that has a written non-target motivation fixed in advance. (ii) is equally available.
3. **What changes mechanically.**
   * (i) Nothing. The build stays as reviewed. RC1 byte identity is checked at the qualification: 45 pinned files,
     the 46 carried driver definitions text-identical to MB r1's, and a one-line guard diff.
   * (ii) MB-S is left for a route on S4's changed branch (R3-N2), which needs:
     * a written non-target motivation (both members were recorded in registry r2, `8da57f89`, before the MB r1
       freeze);
     * a route amendment and its review;
     * a theorem revision for COR-T, which changes g_hi, an input that THEOREM_MB §8 lists as unchanged;
     * implementing and wiring C11R-I2, which has never run at any block of this cell;
     * new code reviews, a new qualification and a fresh incident re-rating.

     The science pins, the RC1 identity test and MBR1_REPRO would not apply as now written.
4. **Scientific consequence.** No statement is made here about what either member would do on cell 308 (MBS-10).
   * (i) MB r1's science, byte-identical. The determinism argument applies: *if* MB-S completes and the platform pin
     holds at every resume, its certified value equals the value the lost run would have produced (governance A1
     "decisive argument", E1 note; route E1 DR2). Determinism covers the value only. It does not cover the go / no-go
     decision, the new infrastructure or later routes on 308 (route E2).
   * (ii) The science is changed (S4's changed branch). The determinism argument does not apply.
5. **Governance consequence.**
   * (i) Rating: MEDIUM–HIGH at the upper end, conditional on byte-identical science on the pinned platform and on the
     T6 conditions M1–M6; otherwise HIGH (r1 §G; `b7e62dec`; `ff2280e9`). Deferring the members "*may* foreclose them
     for cell 308, or at least makes any later use post-result, exposed and governed" (route E1 DR1). Any later use
     follows §26's path (temporal evidence plus independent governance review) and starts at not lower than HIGH
     (MBS-5(b)).
   * (ii) A fresh re-rating, presumptively HIGH (r1 §A.4). The members are included, so their later use does not arise.
6. **Runtime / resource consequence.** (i) Nothing extra. (ii) Development and review time, and new decoy measurements
   with the changed science. The runtimes feeding MBS-8 and the R-rules therefore change. C11R-I2's cost at this cell
   has never been measured.
7. **Qualification consequence.** (i) The cases the framework declares dependent on MBS-7 (QC01–QC08, MBR1_REPRO,
   QS-RESUME-DECOY; brief 46) are built as designed. MBR1_REPRO requires exact equality with MB r1's committed r3
   non-target records. (ii) Those cases must be redefined for the changed science, MBR1_REPRO's exact-equality premise
   no longer holds for the changed parts, and the qualification is re-derived.
8. **Failure / recovery consequence.** (i) An MBR1_REPRO mismatch means STOP and S4's changed branch (RC2). (ii) The
   new reviews may reject, as for any new build. The post-marker INDETERMINATE semantics are the same under both (§4).
9. **Target exposure.** The count is unchanged under both. (ii) moves the earliest possible target step later, behind
   the new work.
10. **Reversible before the freeze?** Yes. Work started under (ii) can be abandoned, and the reviewed build remains at
    its commits. After the freeze, no.
11. **Existing evidence.** Registry r2 (`8da57f89`); route review check 3 and RC4; route E1 DR1; route re-check R3-N2;
    governance E1 D1; r1 §A.4; protocol draft §2 (the 45-file list).
12. **Unresolved uncertainty.** Whether a later governed route carrying these members would count as "route MB" for
    MBS-6 (i). How §26's path would apply if MB-S ends INDETERMINATE, with no observed outcome. The size of the (ii)
    effort, which no text estimates.

## 6. Decision MBS-8: the caps

1. **The exact question.** Which caps does MB-S freeze? You choose the option; the values then follow mechanically and
   no cap is set by hand (r1 §A.2). The record must also state the per-attempt, awake-time EVAL_CAP semantics
   (implementation review D10 note).
2. **Options.**
   * (i) **MB r1's r3 caps.** EVAL_CAP 8 h. Per-job CPU caps as frozen (MB r1 protocol §3.2): RLR 1800 / 4200 / 8700 s
     by rung; C2b 1800 / 1800 / 2700 s; C1b 1800 s; VER 1800 s. PRE_CAP 1800 s and WORKERS 5 as frozen.
   * (ii) **MB r1's frozen §3.2 rule, applied to MB-S's own official decoy runtimes under its launchd launcher.**
     EVAL_CAP = max(6 h, ⌈2 × projection⌉ h), where the projection is the Stage-1 makespan of the cell-308 job set at 5
     workers, longest-first, built from the larger decoy wall time per job kind and rung. Per-job CPU cap = max(3 × that
     wall time rounded up to 300 s, 1800 s). The rule reads runtimes and statuses only, never a decoy value (incident
     review C7(b)). PRE_CAP and WORKERS are not outputs of the rule.

   **Default: (i), an engineering default (not a scientific recommendation).** Engineering reason: it adds no newly
   derived operational value and no non-holder cap-derivation step, and it keeps the caps out of the sequencing question
   of §8. (ii) has its own engineering reason: its caps are sized from runtimes measured under the launcher MB-S
   actually uses. (Route review check 5(d) requires that re-measurement for Q12 under either option.) (ii) is equally
   available.

   **Common to both options; your MBS-8 record should state this:**
   * EVAL_CAP applies **per attempt, on awake time** (CLOCK_UPTIME_RAW), from the marker or from the resume start.
     Sleep does not count. A hit is an execution failure, INDETERMINATE (ratification item 4; implementation review D10).
   * With at most 3 resumes, the total awake budget is up to **4 × EVAL_CAP** (32 h under (i)), inside the 7-day
     deadline.
   * A per-job CPU-cap hit is a failure, never a dropped rung.
   * **A worker death is an execution failure, not a resumable interruption** (D5), including a transient OS kill of
     one worker. Making it resumable would turn a frozen cap into a budget (implementation review D5).
   * Caps change only whether, and for how long, the one evaluation runs. They never change Γ (review N3).
   * MEM_CAP and the start gates are not part of MBS-8. They are set by the R-rules at the freeze under both options.
3. **What changes mechanically.**
   * (i) No code value changes: EVAL_CAP_S and RUNG_CPU_CAP_S already hold MB r1's frozen values (implementation review
     §10 rows 3 and 8, source (a)). Q12 checks them against the official decoys under the launcher. It requires
     EVAL_CAP ≥ ⌈1.5 × projection⌉ and every per-job cap ≥ 2 × the official maximum wall time of its kind and rung
     (MB r1 protocol §3.2).
   * (ii) A non-holder computes the values from the official decoy records (S3, S13, M4), and they are frozen in the
     code. This needs the answer to §8. Arithmetic of the two texts: if the rule and Q12 read the same runs, Q12's two
     inequalities hold by construction.
4. **Scientific consequence.** None under either option. Caps are infrastructure (D11) and never enter a value (route
   review check 6; QC04: serial equals pooled). The science's byte identity is unaffected.
5. **Governance consequence.**
   * (i) The caps trace to MB r1's frozen values, so T6 M1 needs nothing new for them. This is the "r4 with the same
     caps" case that S16(c) answers.
   * (ii) New operational values, derived by a non-holder from decoy evidence only (S3, S13, M4). No cap may come from
     the MB r1 target run.
   * Both options need S16(c): the texts make no exception for (ii).
6. **Runtime / resource consequence.** Both options use the same official decoy runs, which Q12 needs anyway. Under
   (i) the maximum awake budget is fixed now (4 × 8 h). Under (ii) it is 4 × the derived EVAL_CAP, which may be above
   or below 8 h (its floor is 6 h), so planning the host window waits for the derivation.
7. **Qualification consequence.** Q12 and the official decoy measurement records are PENDING_USER_DECISION in the
   framework until MBS-8 is recorded (brief 46). Under (i), Q12 is a pass / fail test of fixed caps. Under (ii), Q12
   becomes a consistency check of the derived caps, and the derivation record is a qualification input.
8. **Failure / recovery consequence.** (i) If Q12 fails under the new launcher, the qualification fails: STOP before
   the target (U7). MB-S's repair rule is not frozen yet; MB r1's precedent is no same-round repair. (ii) A failure of
   the derivation's inputs (for example a decoy that does not complete) fails the qualification in the same way. After
   the marker, under both options, a cap hit makes the evaluation INDETERMINATE and is not resumable (then §4 applies).
9. **Target exposure.** None. The count is unchanged. Depending on the answer to §8, (ii) may add steps before the
   freeze.
10. **Reversible before the freeze?** Yes. See §2 on recording it before any official decoy run.
11. **Existing evidence.** MB r1 protocol §3.2 (freeze r3 `c46434a3`); governance A1 §1 (O4 reconciliation) and §3
    item 4; route E1 note N5; route review checks 5(d) and 6; implementation review §10 rows 1–3, 6 and 8, D5 and D10;
    ratification items 4 and 18; protocol draft §8 ("Caps"); register row MBS-8.
12. **Unresolved uncertainty.** The sequencing question (§8). MB-S's own Q12 definition, pending integration of the
    framework. Whether the (ii) values would differ from (i), which is unknown until measured. The sleep exclusion rests
    on the documented clock semantics and is not exercised by a test (implementation review D10 (ii)). As in MB r1, a
    cap firing in the instant between the evaluator's return and the alarm's disarming records a failure (D10 (iii)).

## 7. Decision S1: the grant ruling

1. **The exact question.** Do you give the ruling that authorises a second consumed evaluation of cell 308 under MB-S
   (governance S1; A1 §3 with E1 D1)? It is required before any grant. The protocol draft places the grant after the
   official qualification and its independent QUALIFICATION_ACCEPTED review.
2. **Options.** (A) give the ruling with the required content; (B) withhold it. **No default.** A ruling that lacks a
   required element does not meet S1. **The required content**:
   1. authorise a **second consumed evaluation** of cell 308 (count 2) under MB-S only, **notwithstanding** your
      brief's §21 ("execute cell 308 exactly once") and mitigation 5;
   2. lift mitigation 5 for MB-S, and confirm that your §20–§21 and §23 continue to bind MB r1 unchanged;
   3. state that MB-S is a new governance decision, not a rerun on host grounds (E3); MB r1 stays INDETERMINATE;
   4. confirm the caps option (§6);
   5. re-affirm U1–U8 of your C4 ruling;
   6. record your decisions on finality (§4) and on the members (§5).

   **U1–U8, in short** (`ledger/USER_RULING_C4.md`, `0aeaec23`; the verbatim text governs):
   * U1: incidents 01–03 stay disclosed.
   * U2: the route-selection / result-chasing risk stays an explicit limitation.
   * U3: the pre-existing provenance of TPT and of sub-segment re-certification stays part of the justification.
   * U4: a CELL308_CLOSED verdict is scientific closure only.
   * U5: no adoption, floor-r2 change, r6, K5 or P5Y closure, or publication-status rewrite.
   * U6: exactly one authorised target evaluation under the frozen protocol, with no tuning or successor variant
     selected from its result.
   * U7: a qualification failure or review rejection stops before the target.
   * U8: the ruling substitutes for no gate.
3. **What changes mechanically.**
   * (A) The ruling is recorded verbatim. The grant (`NSS/authorization/MBS308_GRANT.json`) must carry it as
     `user_ruling_s1`: the verbatim text, its sha256 and `reaffirms_c4: true`. The driver's `check_grant` refuses
     otherwise (protocol draft §1; BUILD_REPORT §8 D12).
   * (A) The grant also binds the freeze, qualification and qualification-review commits, the driver sha256 and the
     manifest (protocol draft §3), plus the MBS-13 contents: the review, the triggers, S1 verbatim, C1–C9, S11–S17, a
     no-trigger statement and the launch conditions. No code or protocol change.
   * (B) No grant, no marker, no target step. MB-S stays frozen-but-unexecuted if it was frozen, or pre-freeze if not.
4. **Scientific consequence.** None. The science is fixed at the freeze by §5.
5. **Governance consequence.**
   * (A) Mitigation 5 is lifted for MB-S. The count becomes 2 when the MB-S marker is written, and the adjudication must
     record that cell 308 was consumed twice (MBS-14).
   * (A) The rating stays as §5 describes. The ruling is taken with in view the items r1 §C lists: incidents 01–03,
     H4.3b, I-a…I-e, E1′, E1″ with its errata, the incident reviews and the T6 ruling.
   * (A) It is also taken with in view route risk (e): the go / no-go decision is taken with the lost run's
     runtime-only observations in view. These are named, never valued, in E1″, and this brief contains none of them.
   * (A) Per U7 and U8, the ruling replaces no gate.
   * (B) S1 stays open, cell 308 stays OPEN and MB r1 stays INDETERMINATE.
6. **Runtime / resource consequence.**
   * (A) The execution window runs from the marker for up to 7 days: up to 4 attempts, each limited to EVAL_CAP of
     awake time.
   * (A) The host stays prepared and exclusive until the seal (S17), and automatic installation stays disabled for the
     whole window (§9).
   * (A) An operator must launch any resume (ratification item 19). After the marker the only permitted actions are
     `recover` and `resume`, and `status` prints the state name only (MBS-3).
   * (A) The execution review, the adjudication and the adjudication review follow.
   * (B) None.
7. **Qualification consequence.** None changes. The grant needs QUALIFICATION_ACCEPTED, and a qualification failure or
   rejection stops before the target whatever the ruling says (U7).
8. **Failure / recovery consequence (A)** (protocol draft §4–§6):
   * A host reset, the hosting app's death or a power loss gives CONSUMED_INTERRUPTED and a mandatory resume, launched
     by the operator. Verified checkpoints are served and only the rest is recomputed. At most 3 resumes, within 7 days.
   * A platform change gives close-indeterminate.
   * Stale campaign git lockfiles are moved aside by `recover` (recorded, never deleted). `packed-refs.lock` is never
     touched.
   * A recorded process that is not positively dead (for example while `ps` fails) keeps the run CONSUMED_COMPUTING,
     with no timeout.
   * Sleep pauses the computation, does not count toward EVAL_CAP and is recorded.
   * Every failure in the §4 list is INDETERMINATE, with no rerun under MB-S.
   * Host provenance never changes a status or an outcome (E3).
9. **Target exposure.** (A) is the only decision that authorises a cell-308 target evaluation: one, under MB-S,
   possible only after the grant. The count becomes 2 at the MB-S marker. (B) authorises none.
10. **Reversible?** S1 is not a freeze-time decision; it binds at the grant. I found no text on withdrawing it before
    the grant. After the marker it cannot be reversed: the marker stays consumed for ever.
11. **Existing evidence.** Governance §4 question 8 and S1; A1 §3; E1 D1; register rows S1, MBS-13 and MBS-14;
    protocol draft §1, §3 and §10; `ledger/USER_RULING_C4.md`; r1 §B and §C.
12. **Unresolved uncertainty.**
    * The rating at grant time depends on M1–M6. The T6 text is not available to me; §0 row 2 gives what is.
    * U6 speaks of "exactly one authorized target evaluation under the frozen protocol". The texts I read do not spell
      out how U6 reads when it is re-affirmed for MB-S.
    * The MBS-13 grant contents are still to be drafted.
    * The host's state at execution time is unknown.

## 8. The open sequencing question (R-rules; MBS-8 option (ii))

* **The texts.** Protocol draft §8 (at `216c465f`) freezes MEM_CAP_BYTES, FREE_MEM_MIN_BYTES, EXCL_CPU_PCT and
  EXCL_ALLOW "as the outputs of the four rules … computed from the official qualification evidence and never from any
  target run". R-MEM takes as inputs "the OFFICIAL decoy runs of the MB-S qualification". R-FREE and R-ALLOW take at
  least 10 prepared-state readings, 30 s apart, from the qualification. Under MBS-8 (ii), EVAL_CAP and the per-job CPU
  caps come in the same way from official decoy runtimes.
* **The order the texts give.** Freeze, then the official qualification at the freeze commit, then its review
  (protocol draft §1; MB r1 protocol §10). The freeze binds the code by manifest and helper pins. After the
  qualification review no code or configuration may change (MB r1's G2 precedent).
* **The question.** The frozen code must already carry the values, but the runs that produce their inputs are defined
  as part of a qualification that runs on the frozen code.
* **The options.** The qualification framework's protocol §11.2 (builder4, brief 46) is to state the question and list
  the options. It is built in scratch and not yet integrated, and I have not seen it. **The options list is therefore
  pending integration**, and none is presented or preferred here. **No default.**
* **Existing evidence relevant to any option.** MB r1's own sequence for its caps: decoy costs were measured in a
  pre-freeze exploration with the pre-freeze build (MB r1 protocol §3.2; `evidence_prefreeze/DECOY_TIMING_PREFREEZE.json`),
  the values were frozen, and Q12 then re-derived the projection from the official runtimes as a check. The texts I read
  do not settle whether that pattern satisfies the R-rules' "OFFICIAL decoy runs" wording.
* **What depends on the answer.** The four R-rule values (under both MBS-8 options); the MBS-8 (ii) values; the official
  decoy measurement records, which are PENDING in the framework; and possibly the number of decoy runs and freeze steps.

## 9. The host before official qualification and before any execution

Sources: protocol draft §4–§8 (at `216c465f`), the ratified constants (`3c2a7854`), governance S17 and route E1 DR2.
**User action** marks what the campaign cannot do itself; the campaign never changes a system setting.

| requirement | before the official qualification | before and during any execution | who |
|---|---|---|---|
| **Platform unchanged**: interpreter path and sha256, libpython sha256, `sys.version`, OS build, architecture (now 3.14.5, 25F84, arm64) | the pins are taken from the qualification host at the freeze | re-verified at `execute`, at every resume and in every computing mode; a mismatch before the marker refuses (nothing consumed); at a resume it gives close-indeterminate | **user action** (no OS or Python update from the qualification to the end of the window, RC2); campaign gate |
| **Automatic macOS / critical-update installation disabled** (AutomaticallyInstallMacOSUpdates = 0 and CriticalUpdateInstall = 0; a missing key counts as enabled) | needed for RC2's no-update period, which starts at the qualification | preflight refuses otherwise; it must stay disabled from the marker to the 7-day deadline | **user action**. The implementation review recommends reading all four update keys; that option is not applied. The security trade-off of a long no-update period is yours; the texts say only that the campaign never changes settings |
| **Automatic restart** (after a power failure, or for updates) | not gated | not gated. A restart mid-run gives CONSUMED_INTERRUPTED and an operator-launched resume; with a platform change it gives close-indeterminate | **user's setting**; no text I read gates it |
| **AC power** | part of the prepared state for the R-FREE / R-ALLOW readings | start gate; after the marker only recorded | **user action** |
| **Low Power Mode off** | — | start gate | **user action** |
| **Sleep prevention** | — | the driver runs `caffeinate -i -m -s -w <driver pid>` under a supervisor that re-spawns it and records every death | campaign |
| **The lid** | — | lid-close sleep is outside caffeinate's reach (ratification item 28). Sleep is recorded (channels K/S/L) and never gates. It does not count toward EVAL_CAP, but the 7-day deadline runs in wall time | **user action** (keep the lid open, or accept pauses) |
| **Thermal pressure level 0** | — | start gate; after the marker only recorded | **user action** (host idle and cool at start) |
| **Disk** | the qualification's sandboxes need far more than the execution (about 0.8 GB per mutant per matrix run unless cleaned); a disk-space / scratch-lifecycle gate is pending | at least 2 GiB free on the repository volume at preflight; the campaign's own writes are MB-scale (ratification item 23) | **user action** (free space); campaign gate |
| **Memory**: pressure level normal (1), and free memory ≥ FREE_MEM_MIN (R-FREE; provisional 2 GiB) | attainability: at least 3 consecutive readings of at least 10 (30 s apart) in the prepared state (AC, your apps quit, the hosting app idle); otherwise GATE_UNATTAINABLE and `execute` cannot start on this host | start gate; the per-worker watchdog enforces MEM_CAP (R-MEM) after the marker | **user action** (quit apps) |
| **Exclusivity**: no process above EXCL_CPU_PCT (25 %, R-EXCL-PCT) besides the campaign's tree and EXCL_ALLOW (R-ALLOW) | prepared-state readings feed R-EXCL-PCT and R-ALLOW | start gate; nothing else heavy runs until the seal, including any other session's compute (S17) | **user action**, arranged by you without inspecting the other session (cell 309's session is out of scope, S10) |
| **Boot identity** | — | the boot UUID is recorded at preflight; a change is a reboot, giving CONSUMED_INTERRUPTED | campaign |
| **Host identity** | this host only: another host means S4's changed branch (route A1, HOST row) | R-MEM's feasibility check uses this host's memory (8 GiB) and wired memory; WORKERS 5 on 6 cores | — |
| **Launch and observation** | — | `execute` and `resume` run only under the launchd launcher (preflight timeout PRE_CAP_S + 100 s). No other campaign job may be live. After the marker the operator may run `status`, `recover` and `resume` only; there is no in-run observation (MBS-3) | operator |

**The last non-holder host readings available to me** (ratifier H1–H3, 2026-09-29 22:02–22:08Z; implementation
reviewer, 21:34Z; readings at those times only):
* all four SoftwareUpdate keys were 1, so `execute` would have refused;
* memory pressure read level 2, then level 1 six minutes later;
* free memory was 1.54–1.70 GiB, below the provisional 2 GiB;
* four OS daemons were above 25 %; they have since been provisionally allow-listed under option B;
* AC power, Low Power Mode off, 170 GB free on the data volume.

At that time the host would have refused. The ENOSPC audit later records a nearly full volume on 2026-09-30, and about
110 GiB free after the cleanup of 08:59:48Z. I have no newer non-holder reading.

**The platform and the unchanged-science branch.** MB r1 recorded only its Python version (route review check 4). The
route review found no OS or Python installation since 2026-09-20 at its reading. If the OS or Python changes before
the freeze, the texts diverge:
* RC2's test is exact equality in MBR1_REPRO under the new pins;
* route A1 §1 says the successor's value equals the lost run's value "only on the same platform".

Which of the two governs is not settled in the texts I read.

## 10. The governing texts, by reference

The verbatim texts are in r1 §D (O1–O5, from governance A1 §1) and r1 §E (your brief's §20, §21, §23 and §26, from
`ledger/USER_TEXTS_SUCCESSOR_308.md`). In one line each:
* **O1** (qualification review E3; protocol §14): host provenance never changes the status, the outcome or
  exactly-once. MB-S is therefore not a rerun on host grounds.
* **O2** (mitigation 5: at most one target evaluation, of one frozen route): only your S1 ruling can lift it for MB-S.
* **O3** (incident review C9): only R-MB on cell 308, the frozen criterion, and one sealed execution without retry.
  MB-S keeps D10 and §5.4 unchanged.
* **O4** (MB r1 protocol §14; qualification review G2): no r4 with the same caps without a new recorded user decision.
  This is S16(c).
* **O5** (recovery chain C6 / E7): lost information is recomputed only through a new independent governance process
  and a new user decision. MB-S is that process.
* **Your §20, §21 and §23**: an explicit grant; exactly one execution, whose consumed marker makes a second refuse; no
  rerun on rejection. They bind MB r1 unchanged.
* **Your §26**: a successor route needs an independently defensible, prospective motivation; temporal evidence and
  independent governance review.

## 11. Drafter statement (briefer2)

* **Read.** The files listed in brief 48 under SOURCES. Also: the route audit A1 and its errata E1 and E2
  (`registry/`); `ledger/USER_RULING_C4.md`; the two ledger lines recording your option-B ruling and the coordinator's
  later ledger lines; MB r1 protocol §3.2, §9 and §10 (formal namespace, frozen text); the head of
  `ledger/OPTION_B_RECHECK.json`; the signature of `code/c308_quarantine.log_event`.
* **Not opened.** Every file brief 48 excludes, the narrow review of W, N and L (in progress), builder4's scratch, and
  the coordinator's morning report.
* **What my context held.**
  * My session began with an auto-loaded memory index; I opened none of its files. Three of its lines touch MB r1: an
    outcome label that the governance texts also carry; a lesson line about host behaviour, of unknown provenance; and a
    successor-lessons line matching committed review conclusions.
  * Allowed governance and build texts I read name clock times of the MB r1 run chronology.
  * None of this is reproduced here, and nothing in this brief depends on it.
* **What I did.** No computation beyond reading and the tail-figure scan. No git write. I wrote this file and one
  research-ledger line (class REVIEW, 0 target evaluations), and nothing else.
