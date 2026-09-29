# Incident-independence re-rating of the cell-308 successor MB-S (fresh reviewer reviewINC2; S12 / GC-5)
INCIDENT_AUDIT_ACCEPTED

**Rating: result-chasing risk of MB-S = MEDIUM–HIGH, not lowered, at the upper end of that class.** It holds only for
MB-S with MB r1's science byte-identical on the pinned platform, and only with conditions MBS-1 to MBS-14 (section
"Conditions"). Each escalation trigger in Q4 moves the rating to HIGH automatically. Any evaluation of cell 308 after
the MB-S marker, of any route and whatever MB-S's outcome, starts at **not lower than HIGH** (MBS-5).

The acceptance covers the successor record's incident-independence position: no target value exists; the lost run
left runtime observations only; determinism under byte identity removes a second draw of Γ. There are no blockers. The
defects found are disclosure gaps and one new exposure class created by the successor's own checkpoint design. All
are bounded and must be closed before the MB-S freeze.

## 0. Reviewer, basis, method (work log, written incrementally)

* **Reviewer.** reviewINC2. I am fresh: I wrote none of the material reviewed and reviewed none of it before. I hold
  no successor route, implementation, caps or qualification role, and may not take one (MBS-1).
* **Basis.** Research branch `p5y-k5-cell308-research`, HEAD `03fc1f0a` when I read it, which includes the route
  re-check R3 (`87d0b2b9`, DELTA_ACCEPTED; route audit as amended = ROUTE_ACCEPTED) and the ledger record that MB r1's
  §10 steps 6–8 are complete (ADJUDICATION_ACCEPTED at formal `e451e634`). My brief is brief 36 (`83e60aa2`).
* **Read in full.** The original review `INCIDENT_INDEPENDENCE_REVIEW_MB308.md` (Q1–Q6, C1–C9); the incident audit a0
  and addendum a1; `COORDINATOR_EXPOSURE_DISCLOSURE.md` (E1, E2, E3, E1′, E1″ and its erratum); the successor-governance
  determination, A1 and erratum E1; its review and delta review; the successor route audit, A1 and erratum E1; its
  review, delta review and re-check R3; the architecture and its addendum A1; `USER_RULING_C4.md`;
  `USER_TEXTS_SUCCESSOR_308.md`; the formal MB r1 adjudication (`9ad632c9`); briefs 30 and 36 and the brief index.
* **Read in part (target-free, read-only).** The successor namespace in `/Users/suzhe/ReBaseGuard-c308mbs`
  (untracked): file list, the checkpoint writer and reader in `code/mbs308_state.py`, and the print statements of
  `code/mbs308_driver.py`. `BUILD_REPORT.md` does not exist yet.
* **Not read, by rule.** `REVIEW_EXECUTION_INTERRUPTION*.md`, `audit/EXECUTION_INTERRUPTION_*.md`, the formal
  `review/MB308_EXECUTION_REVIEW.md`, the formal `postexec/*`, and any checkpoint, journal or spool content.
* **Ran.** A stdlib parse of the research ledger: 253 lines, `new_target_evaluations` sums to 1 (the MB r1 INCIDENT
  line), proxies 0, target-informed optimisation 0. `grep` over the successor namespace. One start ledger line
  (2026-09-29T19:14:41Z, class REVIEW, agent reviewINC2).
* **Hard rules kept.** No driver mode, no git write, nothing computed for cells 305–309 or in the drift band or its
  mirror, no effect estimate of any route on 308, cell 309 untouched. No tail figure and no runtime number of the MB r1
  run appears in this file. Observations are named, never valued.
* **My own exposure (disclosed).** Two of the files my brief assigns carry some of the E1″ observations in
  qualitative or partly quantitative form (Q1, finding X1): the successor-governance review §4 and the formal
  adjudication §6. I read both. I therefore now hold, in named form, the thermal-level history, the pool-load
  continuation, the memory events, the other-application activity and the "Stage 1 probably not finished" inference.
  I do not hold the 23:10 audit figures or the run's own per-coalition CPU.

## Q1. Did the loss of MB r1 create any new target exposure?

**Answer: no target value and no numeric target proxy. It did create a new class of latent runtime proxies, which are
weakly target-informative in principle, and the record of where they sit is incomplete.**

**No value.** I accept the recovery chain's and the adjudication's facts as accepted (I did not re-verify them, and by
rule could not read their sources). Nothing after the marker was persisted, printed or read. The adjudication (§1, §3)
states that no Γ_dec, Γ_MB, P*_B, P_hi, S_i, Ū_i or bound of the evaluation exists. The ledger carries the count 1 on
one line only, and no proxy on any line.

**The observations E1″ names, classed by how much they can say about the target.**

| E1″ item | class | can it inform the value? |
|---|---|---|
| host readings at launch; thermal level during the run; memory events; other applications | host state | No. They depend on the host, not on the cell's values. They inform reliability design (S6, S17) only |
| per-coalition CPU and the pool-load continuation | aggregate runtime | Barely. They say how long Stage 1 ran, not what it produced. They inform caps and completion probability |
| the 23:10 JST read-only audit: worker ages, per-worker CPU times, and job completions inferable from pid succession | **per-job runtime** | **Weakly, in principle.** With one fresh worker per job and longest-first scheduling, per-job durations are latent proxies for rung behaviour (reviewGOV §4). A job that ran long or short at a given rung can reflect whether its certificate came easily |

**The one real new exposure is the per-job runtime held by the coordinator.** It is not a value. It becomes a
target-equivalent proxy only if calibrated, for example against the committed per-job decoy runtimes of MB r1's r3
qualification (QC02, QC03). The coordinator therefore holds the ingredients of a *runtime-calibrated* proxy of rung
behaviour at 308, in addition to the incident-01-class estimator it already holds (E1′). The record shows no one has
formed either. E1″ says the items are "latent runtime proxies with no value content". It does not make E1′'s
statement: that the ingredients are held, have not been combined, and will not be (MBS-1).

**Finding X1. E1″'s "where recorded" column is incomplete.** Committed files outside its list carry the same
observations:
* `reviews/REVIEW_SUCCESSOR_GOVERNANCE_308.md` §4 names the thermal level with its onset, the existence of short load
  dips, the memory events, the "mid-Stage-1 / most probably never finished Stage 1" inference, and the fact that the
  23:10 audit reveals completed jobs by pid succession;
* its delta review §5 repeats the Stage-1 inference;
* the formal adjudication `9ad632c9` §6 carries the host disclosures of the execution review: the thermal timeline,
  the other applications with their CPU totals, the pool-load continuation window and the memory-event times. The
  adjudication review (`e451e634`), which re-checks it, presumably does too;
* the successor worktree itself (branch `p5y-k5-cell308-mbs-r1`, from `21e99cf0`) contains MB r1's `postexec/*`, one
  of the listed locations, next to the files the builder is told to read.

**Finding X2. The holder list is incomplete.** E1″ and its erratum list the coordinator, reviewINT, reviewEXEC,
reviewGOV, the adjudicator and reviewADJ. They do not list me (reviewINC2), or any other reader of the governance
review §4 or the adjudication §6. S14 obliges the successor to cite the adjudication. Citing it by commit and verdict
line is harmless; reading its §6 makes the reader a holder.

**Finding X3. Brief 30 put the builder in a tree that contains `postexec/*`.** The brief does not point to it, and
the GC-6 instruction (ledger: 2026-09-29 about 18:39Z) told the builder not to read "the recovery chain or the
execution review". Whether `postexec/*` counts as the recovery chain is not stated. `BUILD_REPORT.md` does not exist
yet, so the builder's disclosure cannot be checked.

**None of X1–X3 is a new numeric exposure,** and none reaches a science choice, because the science is fixed
byte-identical. They matter for the non-value choices (caps, timing, go/no-go, members) and for the S13 promise that
successor route, implementation and caps agents have not seen the observations.

## Q2. Do determinism, byte-identical science and a pinned platform neutralise the multiplicity of a second evaluation?

**Answer: they neutralise the multiplicity of the *value*, not the multiplicity of the *procedure*.** Two
consumptions of cell 308 under route MB are one draw of Γ, provided all of N1–N7 below hold. They are still two
chances to *complete*, one more go/no-go decision, and a new layer of infrastructure between the certified job records
and the decision. Those are not neutralised by determinism. Q3 lists what remains.

**Why the value is one draw.** MB r1's science is exact and deterministic: verification budgets are operation counts,
a cap hit or an exception is an execution failure and never a dropped rung, and serial equals pooled (QC04). The value
of MB-S is therefore a fixed function of the frozen bytes, the pinned inputs and the platform. The lost run would have
produced the same function value. No outcome exists to select on. Whoever ended the lost run, and why, cannot have
moved Γ (governance A1, "decisive argument"; review N2, N3).

**The conditions (all needed).**
* **N1. Byte identity of the whole evaluation path** (S11, RC1). The science modules, pins, theory, D1–D10, D12–D14
  and §8 are sha256- and blob-identical to `c46434a3`. The driver's science functions are text-identical, and the AST
  test also covers the module-level names they bind (route delta N3). The guard differs in its constants only.
* **N2. The resume path is part of the evaluation path.** Stage-1 job records now reach the aggregation either from
  memory or from a checkpoint blob decoded by the successor's own code (`Checkpointer.verified_records`, `dec`). That
  path is new code. Brief 30 even allowed the aggregation to be refactored "byte-equivalent in behaviour". Determinism
  holds only if a resumed evaluation's certified bytes equal an uninterrupted one's. That must be shown on a complete
  decoy cell, not only on the development decoy's block 0, and checkpoint mis-binding must be caught by mutants (MBS-9).
* **N3. The platform pin at `execute` and at every `resume`** (RC2 as extended by route erratum E1 DR2): interpreter
  path and sha256, libpython sha256, `sys.version`, OS build and architecture. No update from qualification to the
  resume deadline. The MBR1_REPRO case reproduces MB r1's committed r3 non-target records exactly.
* **N4. Identical inputs.** Every research pin (certifiers, verifiers, F2, F3, TC-T inputs, the C2 consumer, the
  registries) is re-hashed at `execute` and at each `resume`.
* **N5. The value is computed once.** A sealed MB-S value is the only route-MB value of cell 308 that will ever
  exist. No third consumption under route MB follows a sealed MB-S (S7).
* **N6. Completion is not steerable by anyone holding outcome-correlated information** (Q3, L5–L6). Without this,
  determinism fixes the value but not *whether it is recorded*. Suppression of an unwanted outcome, by ensuring the run
  never completes, is the one selection effect left.
* **N7. Nothing from the lost run enters any successor choice** (S3, S13). Under N1–N4 it cannot enter the value
  anyway; the rule protects the non-value choices.

**If any of N1–N4 fails,** the successor is on S4's changed branch. Its value is then a second, different draw, the
decisive argument is lost, and this rating does not apply (trigger T1 in Q4).

**What determinism does not reach.**
* **The decision to consume 308 again.** It is taken by people who hold the committed 308 structure (E1, I-a…I-e), a
  near-complete incident-01-class estimator (E1′) and the lost run's runtime observations (E1″). No outcome is observed,
  but beliefs about the outcome can be formed, and the decision can follow them.
* **Implementation risk.** The one thing that is *not* identical between the two consumptions is the infrastructure.
  A defect in checkpointing, decoding, resume or the state machine is a fresh chance of a wrong aggregate, and a wrong
  aggregate could in principle lower a block constant. So the original Q4 premise "a result-chaser cannot manufacture a
  false closure" now depends on N2 as well as on the certified components.
* **Later routes on 308.** Route erratum E1 (DR1) records that brief §26 gives C11R-I2 and COR-T a governed path after
  an MB-S outcome. That makes cell 308 a cell on which more than one route may eventually be evaluated. Determinism of
  MB-S says nothing about that sequence.

## Q3. What residual liberty remains?

None of these liberties can move Γ under N1–N4. Each can move whether 308 is evaluated, when, under which science,
and whether the value is ever recorded.

| # | liberty | who holds it, and with what in view | effect | how far it is closed |
|---|---|---|---|---|
| L1 | **whether to run the successor at all** | the user (S1), on a brief written by the coordinator; both hold E1″, and the coordinator also holds E1′ | a second consumption happens only if someone decides it is worth it. That decision can follow a belief about the outcome, even though no outcome exists | irreducible. It can only be disclosed, and the brief must not carry an outcome expectation (MBS-10) |
| L2 | **timing** of the freeze, the grant, the launch and each resume (a 7-day window) | the coordinator and the user | none on Γ under N3. It chooses host conditions, and whether an OS update can land inside the window | the pin and the no-update rule close the value channel. An update the operator allowed becomes an engineered INDETERMINATE (L5) unless treated as a deviation (MBS-5) |
| L3 | **members: the C11R-I2 / COR-T trade** | the user, before the freeze, on the coordinator's statement of the trade (governance erratum E1 D1; route re-check R3-N2) | the one liberty that touches the science. Either member could only lower Γ given completion | see below |
| L4 | **caps** (keep MB r1's, or re-derive by the frozen §3.2 rule from successor decoys) | the user under §14 / G2; the justification must be decoy-only (S13) | changes only the probability of completion. Tight caps make INDETERMINATE more likely; loose caps lengthen the crash window | narrowed to two mechanical options, with Q12 re-measured under the new launcher (MBS-8) |
| L5 | **completion: abandonment, non-resume, a lapsed deadline, an allowed update** | whoever operates the host during the window | a stop outside the frozen rules is "disclosed as a deviation and classified INDETERMINATE" (architecture §4). An INDETERMINATE leaves 308 formally unobserved, which keeps later routes looking prospective. That is an incentive to prefer INDETERMINATE over NOT_CLOSED | **open.** Mandatory continuation removes the permission but not the ability, and the consequence is costless. MBS-5 removes the incentive |
| L6 | **observation during the run** | anyone with access to the shared object store | new with MB-S: the checkpoint tree names completed jobs (`kind.block.rung`), the journal records the checkpoint count, and loose-object times give per-job completion times. That is the same class of information as the 23:10 audit, available at will for up to 7 days, and it is exactly what would inform L5 | **open.** The architecture's quarantine covers checkpoint *content* only (MBS-3) |
| L7 | **what happens to partial target data** | the campaign, after `close-indeterminate` | new with MB-S: an INDETERMINATE after some checkpoints leaves certified Stage-1 job records of cell 308 on disk. They are target intermediates, which MB r1 never left. Any later route would be designed in a repository holding them | **open.** No disposition is frozen (MBS-4) |
| L8 | **finality** of a successor INDETERMINATE for route MB (S1 item 6) | the user | if it is not final, L5 plus a third consumption rebuilds "run until it completes", with suppression available at each round | open until S1; MBS-5 and MBS-6 bound it |
| L9 | **framing** of the S1 brief and of the go/no-go text | the coordinator | how the trade and the risks are presented can steer L1, L3 and L4 | MBS-10 |

**On L3, the trade.**
* **MB-S unchanged** (the route audit's selection). This is the conservative direction for the science: it gives up
  two monotone improvements for the determinism argument. It is not purely anti-chasing, though. Someone who expected
  MB r1's science to close would also choose it, since it is the most defensible route to that closure. It forgoes
  the members for 308 unless they later take the §26 path, which would then be post-result.
* **Members adopted before the MB-S freeze.** Temporally they are pre-registered: registry r2 (`8da57f89`) named
  C11R-I2 "a successor-campaign item" before the MB r1 freeze. But the decision to build and add closure-favouring
  members would be taken after a consumed evaluation, by people who hold E1′ and E1″. It also loses the decisive
  argument (N1–N4 fail by construction). It is S4's changed branch.
* **I give no rating to the changed branch,** because it does not exist yet. It is **presumptively HIGH**: both
  premises that keep MB-S at MEDIUM–HIGH (a single draw, and no science choice after the loss) are absent. Only a fresh
  re-rating before that freeze can rebut this (MBS-7).
* I make no estimate of either option's effect on 308, and none is needed to rate them.

## Q4. Rating

**MEDIUM–HIGH, not lowered, at the upper end of the class.** Stated as: "result-chasing risk MEDIUM–HIGH (MB-S,
byte-identical science; re-rated after a second consumption; escalates to HIGH on T1–T6)".

**The original Q4's premises, re-checked for MB-S.**

| original premise ("why not HIGH") | for MB-S |
|---|---|
| no parameter is free after the freeze | **holds for the science** (N1). New pre-freeze choices exist (L2–L4, L8), and none touches Γ under N1–N4 |
| every component is a certified bound, so no false closure can be manufactured | **holds, weakened.** It now also depends on the new resume and decoding path being exact (N2) |
| D10 forbids any other route on 308 | **holds inside MB-S** (MB-S is R-MB). It **no longer holds for the cell**: route erratum E1 records a governed §26 path for C11R-I2 / COR-T after an MB-S outcome |
| exactly one sealed evaluation; NOT_CLOSED and INDETERMINATE pre-declared | **holds as "one value"**: one draw, at most one sealed route-MB value (N5). **Fails as "one consumption"**: the count becomes 2, and the user's "execute cell 308 exactly once" (§21) and mitigation 5 must be lifted |

**Why not lower.**
* Everything that made MB r1 MEDIUM–HIGH is still present: the family, the consumer and the cell were chosen knowing
  committed 308 structure (C3), and the incident-01 liability of the profile transport is unchanged.
* The coordinator now holds more: E1′'s near-complete estimator, and E1″'s per-job runtime observations with the
  committed decoy runtimes that could calibrate them (Q1).
* The count of consumptions rises to 2, and the exactly-once commitment has been renegotiated once. A precommitment
  that has been lifted once deters less the next time.
* The successor's own design adds an observation channel (L6) and a way to leave partial target data behind (L7).

**Why not HIGH (today).**
* **No outcome exists.** Nothing can be selected on a value, and nothing was tuned.
* **No second draw.** Under N1–N4 MB-S computes the value the lost run would have computed.
* **No science choice after the loss,** as long as MB-S stays byte-identical. The route selection rests on registry r2,
  which predates the MB r1 freeze. The route reviewer found no dependence on the lost run.
* **The remaining liberties are procedural** (L1–L9), and each has a bounded closure in MBS-1 to MBS-14.

**Escalation triggers.** Any one makes the rating **HIGH** for MB-S, and the S1 ruling or the grant must then be taken
with HIGH in view:
* **T1.** Any of N1–N4 fails at qualification or at any resume (the science is then "changed" under S4).
* **T2.** Members are added, or any MB-VAR variant is adopted (then the changed-branch rule of Q3 applies).
* **T3.** Any agent reads or lists checkpoint, journal or spool state, or inspects per-job progress, between the
  MB-S marker and the seal, outside the driver itself.
* **T4.** A stop, lapse or allowed update outside the frozen rules (L5).
* **T5.** A successor brief, protocol text or S1 brief carries an expectation of the outcome, or an E1″ observation
  or pointer is given to a route, implementation, caps or qualification agent.
* **T6.** A successor route, implementation, caps or qualification role is held by an E1″ holder, including me.

**Any evaluation of cell 308 after the MB-S marker,** of any route and whatever MB-S's outcome (CLOSED, NOT_CLOSED or
INDETERMINATE), starts at **not lower than HIGH**. After CLOSED or NOT_CLOSED it would be post-result. After
INDETERMINATE it would be a third consumption, possibly with partial target data on disk. The rule also removes the
incentive in L5: engineering an INDETERMINATE no longer buys a "prospective" later route.

## Q5. Required conditions on the successor

The conditions are listed in section "Conditions" (MBS-1 to MBS-14). By stage:

| stage | conditions |
|---|---|
| **before the MB-S freeze** (with S16's gates; S12 is discharged by this file only together with these) | MBS-1 to MBS-12 |
| **at the grant** | MBS-13, plus a check at grant time that no trigger T1–T6 has fired |
| **at the adjudication** | MBS-14 |

## Q6. Is anything in the successor record inconsistent with the original C1–C9?

| condition | finding |
|---|---|
| **C1** (audit a1) | Consistent. E1″ follows the C1(c) pattern, but it lacks the C1(c)-style statement "holds the ingredients, has not formed, will not" for the runtime-calibrated proxy (Q1; MBS-1) |
| **C2** (quarantine record) | Consistent so far. The successor namespace does not reference `C3_KNOCKOUT_RECONSTRUCTION.json` (grep, today). The rule must be restated for the successor's formal namespace and checked at its qualification (MBS-12) |
| **C3** (independence statement; risk stays MEDIUM–HIGH) | Consistent: S12 says "not lower than MEDIUM–HIGH", and route A1 risk 1 carries it. **One overstatement:** the route audit §2 item 2 says "No selection effect is possible". It holds for the value only. A selection effect on *whether the value is recorded* remains (L5). The sentence should read "no selection on the value", and the risk register should name L5–L7 (MBS-12) |
| **C4** (user ruling taken with the incidents in view) | **Gap.** Governance A1 §3 asks the S1 ruling to re-affirm U1–U8, but it does not restate C4's "taken with … in view" list (incidents 01–03 and residue, H4.3b, I-a…I-e, E1′, the review). For S1 that list must be carried, plus E1″ and this review (MBS-10) |
| **C5** (briefs) | Consistent in form: briefs 24–36 are indexed. The index times needed two errata; the ledger UTC is authoritative. C5's incident rule must extend to E1″ observations and to pointers to their locations (MBS-11). Brief 30 placed the builder in a tree holding `postexec/*` without an explicit exclusion (X3) |
| **C6** (registry completeness) | Consistent. The successor route matrix keeps C9-E1 (α lever) BLOCKED on toolchain and host, and adds MB-VAR and HOST rows, with target-free reasons |
| **C7** (rehearsal; decoys) | Consistent in intent. The successor keeps `rehearse --cell 305` and uses decoy 297. S13 keeps caps decoy-only. The caps *decider* holds E1″ (the user, the coordinator), so the options must be mechanical (MBS-8) |
| **C8** (scanner) | Not yet shown. The successor package has no scanner of its own today. C8 applies to it (MBS-12) |
| **C9** (unchanged mechanics) | **Partly inconsistent, and reconciled only through S1.** §5.4 (criterion) is unchanged: consistent. "One sealed execution, with no retry": governance A1 O3 scopes it to MB r1. That is acceptable only because the S1 ruling expressly lifts mitigation 5 and §21 for MB-S, and because under N1–N4 MB-S is one value. **D10** was read by the original Q4 as "forbids evaluating any other route on 308". Route erratum E1's governed §26 path for C11R-I2 / COR-T after an MB-S outcome contradicts that reading at cell level. The record must state that D10 binds per campaign, and that any later route on 308 starts at not lower than HIGH (MBS-5) |

**No other inconsistency found.** The successor record changes no status, authorises nothing and does not touch cell
309. Every successor record carries count 0 on its ledger lines.

## Conditions

MBS-1 to MBS-12 must be met **before the MB-S freeze**. MBS-13 binds the grant and MBS-14 the adjudication. All are
carried verbatim into the successor protocol, the grant and the adjudication.

**Before the freeze**

* **MBS-1. Exposure record (a second E1″ erratum, additive).**
  * Add the missing locations (X1): the successor-governance review §4, its delta review §5, the formal adjudication
    §6, the adjudication review, this file, and `NSF/postexec/*` as present in the successor worktree.
  * Add the missing holders (X2): reviewINC2, and every agent that read one of those locations.
  * Add the C1(c)-style statement: the coordinator holds the ingredients of a runtime-calibrated proxy of rung
    behaviour at 308 (the 23:10 per-worker observations and the committed decoy per-job runtimes). It has not formed
    it, has written no such combination, and will not.
  * No holder takes a successor route, implementation, caps or qualification role (T6).
* **MBS-2. Reading restrictions, extended.**
  * No successor brief, protocol reading list or test for a route, implementation, caps or qualification agent points
    to any MBS-1 location.
  * The adjudication and its review are cited by commit and verdict line only.
  * `BUILD_REPORT.md` states whether the builder opened anything under `NSF/postexec/` in the successor worktree, or
    any other MBS-1 location (X3). The qualification reviewer checks this.
* **MBS-3. No observation during the run (L6).** Between the MB-S marker and the seal:
  * no agent and no process other than the driver lists the checkpoint ref or tree, reads the journal blob, inspects
    loose-object times or counts in the shared object store, or reads the durable logs beyond a state name;
  * `status` prints the state name only (as designed), and `execute` and `resume` print nothing per job before the
    seal. A test checks this;
  * the host contract records host readings only, never per-job progress;
  * no sandbox or other git-writing process uses the shared object store (S17). The ledger incident of 2026-09-29
    19:14:45Z shows that `--shared` sandboxes do touch the real store;
  * object accounting for the window is done after the seal, by count and type only.

  A breach fires T3.
* **MBS-4. Frozen disposition of checkpoints (L7).** Whatever the outcome, checkpoint blobs are quarantined target
  intermediates. They are never read after the run ends, never used by any other campaign or any later resume, and
  recorded by count and tree hash only. They are not deleted (evidence is kept). Their existence is named in the
  incident audit of any later route on 308.
* **MBS-5. Deviations and later evaluations.**
  * (a) Any stop, non-resume, lapsed deadline, operator-allowed update or kill outside the frozen rules is ledgered as
    an INCIDENT, classified INDETERMINATE, and fires T4.
  * (b) The protocol pre-declares that any evaluation of cell 308 after the MB-S marker, of any route and whatever
    MB-S's outcome, is rated not lower than HIGH.
* **MBS-6. Finality before the freeze.** The user's recorded decision before the freeze (S16(c)) also settles S1
  item 6. That INDETERMINATE-class outcomes of MB-S are final for route MB on cell 308 is frozen into the successor's
  outcome table. This review recommends "final". If the user decides otherwise, MBS-5(b) still applies.
* **MBS-7. The member trade before the freeze.**
  * If members are adopted, this rating is void. A fresh incident-independence re-rating, presumptively HIGH, precedes
    that freeze.
  * If MB-S stays unchanged, the S1 record states that any later use of C11R-I2 or COR-T on 308 is post-result and
    starts at not lower than HIGH.
* **MBS-8. Caps, mechanically.**
  * The §14 / G2 decision chooses between exactly two options: MB r1's r3 caps, or the frozen §3.2 rule applied to the
    successor's official decoy runtimes under its own launcher. No value is set by hand.
  * A non-holder drafts the justification from decoy and qualification evidence only.
  * Q12 passes under the chosen caps.
  * The per-attempt EVAL_CAP rule (architecture §8) is frozen and independently reviewed.
* **MBS-9. The determinism premises as facts at qualification (N1–N4).**
  * The AST equality test covers module-level names (N1).
  * Resumed equals uninterrupted, byte for byte in every certified leaf, on a complete decoy cell covering every job
    kind (N2).
  * Mutants must fail: a checkpoint for job A served as job B; a wrong grant; a wrong driver sha; a wrong or future
    sequence number; a record from another attempt; a checkpoint written under a different pin.
  * The pin is re-verified at `execute` and at every `resume`, and MBR1_REPRO is exact (N3).
  * The research pins are re-hashed at `execute` and at every `resume` (N4).

  Any failure fires T1.
* **MBS-10. The S1 brief.**
  * **It carries:** this review (path, sha256, verdict, rating, T1–T6, MBS-1 to MBS-14); E1″ with both errata; O1–O5;
    brief §20, §21 and §23 verbatim; the member trade with R3-N2's meaning; the finality and caps questions.
  * **The ruling is taken with** C4's list in view (incidents 01–03 and residue, H4.3b, I-a…I-e, E1′, the original
    review), plus E1″ and this review.
  * **It contains no expectation** of MB-S's outcome: no statement, estimate or hint of margin or closure likelihood,
    and no "worth running" argument drawn from 308's structure. Before it reaches the user it is checked for this by
    the research scanner and by a non-holder reading.
  * **The ruling is recorded verbatim** before the freeze (§14 / G2, finality, trade, caps) and before the grant (S1).
* **MBS-11. Briefs (C5 extended).** Every successor brief is committed, or its sha256 ledgered, before the freeze. A
  brief that gives an E1″ observation, or a pointer to an MBS-1 location, to a route, implementation, caps or
  qualification role is recorded as an INCIDENT and fires T5.
* **MBS-12. C1–C9 carried into the successor.**
  * C2: no successor formal file reads `C3_KNOCKOUT_RECONSTRUCTION.json`; C-A recomputes from committed inputs.
    Checked at qualification.
  * C7(a): the successor's `rehearse --cell 305` gives reproduction values and equality booleans only, with tripwires
    armed.
  * C7(b): no decoy nearer the band than 297 and 316.
  * C8: the successor package's scanner builds its planted strings at run time, with no gain-beside-threshold phrase.
  * C9: §5.4 is unchanged; MB-S has one sealed execution, no retry, no post-result tuning.
  * The route audit's "No selection effect is possible" is corrected to "no selection on the value". The risk register
    adds L5–L7.

**At the grant**

* **MBS-13.** The grant records:
  * this review (path, blob, sha256, commit), its verdict, the rating string of Q4, T1–T6 and MBS-1 to MBS-14 verbatim;
  * the S1 ruling verbatim, with count 2, mitigation 5 and §21 lifted for MB-S only, "not a host-grounds rerun", the
    caps option, U1–U8, finality and the member decision;
  * C1–C9 verbatim with governance A1's O3 reconciliation, and S11–S17;
  * a statement, checked at grant time, that no trigger T1–T6 has fired;
  * the launch conditions: S17; no in-run audit beyond the frozen host contract; the coordinator does no process, log
    or checkpoint inspection during the run. MB r1's 23:10 audit is the precedent this rule exists to prevent.

**At the adjudication**

* **MBS-14.** The adjudication records:
  * cell 308 consumed twice (MB r1 INDETERMINATE, and MB-S), with the route-MB value computed at most once;
  * the rating and the liabilities verbatim: C4's list, E1″ and this review;
  * the resume history after the seal, by count and class only: attempts, the cause class of each interruption, the
    pin status at each resume, and the deadline;
  * from the ledger and the reflogs, that no T3 access occurred, or its disclosure and the rating HIGH;
  * every fired trigger;
  * closure-only (U4, U5);
  * E8, extended: no decoy value, QC value or MBR1_REPRO record, and no runtime observation of MB r1 or MB-S, placed
    next to a cell-308 quantity; no comparison with any forecast or estimate;
  * the MBS-4 disposition of the checkpoints, and MBS-5(b) for any later route on 308.

## Blockers

None. The successor record's incident-independence position is not falsified by anything I found:
* no target value exists;
* the lost run left runtime and host observations only;
* the science selection predates the loss;
* MB-S under N1–N4 is one draw.

X1–X3, the C4 gap, the C9 / D10 reading and the new L5–L7 exposure class are bounded. Each is closed by MBS-1 to
MBS-12 before the freeze. That is the same class of defect as the original review accepted with C1–C9.

## Notes

* **Note 1. S12 and S16.** This file supplies S12's re-rating (governance delta review N4: a freeze prerequisite).
  S12 counts as discharged only together with MBS-1 to MBS-12.
  * S16(a) is closed (governance delta review).
  * S14 = S16(d) now holds: ADJUDICATION_ACCEPTED at formal `e451e634`, line 2, verified read-only.
  * S16(b) is accepted in text (route re-check R3). It becomes fact only at the successor qualification.
  * S16(c), the user decision, is open.
* **Note 2. Event times.** "23:10" and "23:29" are used here as the names that E1″ and the accepted chain use for
  events. No runtime quantity of the MB r1 run is stated.
* **Note 3. The user holds E1″ too.** The user issued the Force Quit and knows the run's duration. This cannot be
  undone and is not a defect. It is why MBS-8 makes the caps choice mechanical, and why MBS-10 keeps outcome
  expectations out of the S1 brief.
* **Note 4. The adjudication's accounting method** (the mtime and birth time of every loose object) would, applied to
  an MB-S window before the seal, be exactly the L6 observation channel. MBS-3 therefore moves any such accounting to
  after the seal.
* **Note 5. Not checked.** I did not check the builder's untracked tests beyond the checkpoint code and print
  statements. I did not check brief sha256 values against `BRIEF_CHECK.json`, or the transcript. The recovery facts
  are taken as accepted.

## Post-write checks

* **Research scanner** (`code/c308_quarantine.py --scan`, read-only), run after this file was written: PASS, 0
  findings over 381 text and 51 Python files, with both negative controls detected.
* **Own check of this file.** None of the 72 pattern strings in `ledger/TAIL_FIGURE_PATTERNS.json` occurs in it. It
  has no fraction literal and no drift. Line 2 is the only whole-line verdict token.
* **Writes.** Nothing was written outside this file, two REVIEW ledger lines (agent reviewINC2) and the scratchpad.
  New cell-308 target evaluations: 0. Proxies: 0. Band drifts: 0. Cell 309: untouched.
