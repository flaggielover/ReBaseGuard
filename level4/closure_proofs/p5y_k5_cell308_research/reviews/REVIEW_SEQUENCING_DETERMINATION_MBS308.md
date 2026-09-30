# MB-S R-rule sequencing (successor protocol draft §11.2): determination review (reviewSEQ, brief 51)
SEQUENCING_NOT_DETERMINED

Reviewer: **reviewSEQ**, a fresh reviewer and not a holder of any MB r1 run observation. Brief 51 was recorded at
research `3e3bf601`. Written 2026-09-30 UTC (2026-10-01 JST); the ledger line's UTC timestamp is authoritative. The review is read-only: I made no git write, ran no computation beyond reading
and text search, and wrote only this file and one ledger line. **New cell-308 target evaluations: 0.** No cell 305-309
was evaluated, directly or indirectly. Cell 309 is out of scope. Nothing below depends on, or speculates about, any
cell-308 result.

**The question.** MBS-8 = (i) is recorded. Does already-accepted governance **uniquely** determine a prospective,
target-free resolution of the sequencing question for MEM_CAP_BYTES, FREE_MEM_MIN_BYTES, EXCL_CPU_PCT and EXCL_ALLOW,
and for MEM_POLL_S, which R-MEM step 6 can change?

**Answer.** No. The conflict is real. Q12 under MBS-8 (i) does not cause it. It comes from the four written rules
themselves. Each of options (a), (b) and (c) meets some accepted texts word for word and departs from others. Each
also leaves at least one sub-choice open that no accepted text settles. Option (d) is not a complete resolution. No
accepted text rules out all options but one. The one remaining question for the owner is in section 4.

## Sources read (committed bytes)

* **Research namespace** (`/Users/suzhe/ReBaseGuard-c308/.../p5y_k5_cell308_research`, HEAD `3e3bf601`):
  * `governance/CONSTANTS_RATIFICATION_MBS308.md` (`3c2a7854`);
  * `governance/SUCCESSOR_CONDITIONS_REGISTER_308.md`;
  * `governance/SUCCESSOR_GOVERNANCE_308_ADDENDUM_A1.md` and `_ERRATUM_E1.md`;
  * `governance/SUCCESSOR_ARCHITECTURE_308.md` and `_ADDENDUM_A1.md`;
  * `governance/USER_DECISION_BRIEF_308_SUCCESSOR_R2.md`, a DRAFT, read for the option wording only and relied on for
    nothing;
  * `reviews/REVIEW_IMPLEMENTATION_MBS308.md`, `_DELTA.md` and `_DELTA_R3.md`;
  * `reviews/REVIEW_OPTIONB_LIVENESS_MBS308.md`;
  * `reviews/REVIEW_SUCCESSOR_ROUTE_308.md`, `_DELTA.md` and `_R3.md`;
  * `ledger/USER_RULING_MBS308_OWNER_DECISIONS.txt` (`5c2394ba`), all 23 sections, including 4 and 7 in full, and its
    `.md` index;
  * `ledger/briefs/BRIEF_INDEX.md` and briefs 44-50 (46 and 50 in full; the others by search).
* **Successor at `cc723527`**, read through `git show` only:
  * `protocol/MBS308_PROTOCOL_DRAFT.md`, all sections;
  * `BUILD_REPORT.md` sections 13-15 only, cut out of the file without reading sections 1-12;
  * `config/MBS308_QUALIFICATION_CASES.json`;
  * `code/mbs308_driver.py`, searched only for the memory-cap, gate constants and CLI lines cited in 1.2.
* **MB r1:** the frozen protocol `protocol/MB308_PROTOCOL.md`. I read it from the freeze-r3 commit `c46434a3`, and it is
  byte-identical to the worktree copy. I read sections 1-3 (3.2 in full), 9, 10, 13 and 14. I did not open
  `evidence_prefreeze/DECOY_TIMING_PREFREEZE.json`; I only listed it.

**Not opened:**
* every file excluded by brief 51;
* BUILD_REPORT sections 6 and 9;
* anything under MB r1's `review/`, `adjudication/`, `postexec/` or `evidence/`.

I ran no `git log` on the MB r1 branch.

**Exposure statement.**
* **Host memory index.** My starting context held the host tool's memory index (MEMORY.md). It is not a source here,
  and I opened none of its files. It carries **no clock time, runtime, progress figure or host reading of the MB r1
  run**. It does carry MB r1's recorded terminal status label, which the successor protocol draft §1 also states, and
  some generic lesson titles on host sleep and timing that name no run.
* **Governance addendum A1.** This is a required source. It carries a qualitative statement of the attributed cause of
  MB r1's interruption, with no clock time, runtime, progress or host figure.
* **Use.** Neither item is used in this determination, and neither is repeated here beyond this statement.
* **Qualification figures.** Two sources contain figures from MB r1's pre-grant qualification: the ratification's
  evidence Q and MB r1 §3.2's pre-freeze decoy costs. These are not observations of the consumed run. No figure from
  them is used or repeated.

## 1. The premise: is there a genuine sequencing conflict once MBS-8 = (i)?

### 1.1 The texts that produce it

**What the rules take as inputs, and when the values are set** (ratification `3c2a7854`; carried verbatim into
protocol draft §8, which reviewR3C1 found MET as R3 (c)):
* The heading of the rules section: "Written rules (to be applied at the freeze from the official qualification
  evidence; never from any target run)".
* Item 10: "set-by-rule-at-freeze (R-MEM); provisional 3 GiB ratified only for the pre-freeze build and as the
  *measurement* cap of the official decoys" and "Frozen value = R-MEM output."
* Items 14 and 16: "set-by-rule-at-freeze (R-FREE)" and "set-by-rule-at-freeze (R-ALLOW)".
* Item 15: EXCL_CPU_PCT is "ratified as the frozen value, with the single bounded exception of R-EXCL-PCT".
* Item 13, MEM_POLL_S: "ratified (re-checked by R-MEM step 6 at qualification)".
* Change requested 1: "Freeze MEM_CAP_BYTES, FREE_MEM_MIN_BYTES, EXCL_CPU_PCT and EXCL_ALLOW as the rule outputs, with
  the inputs recorded in the qualification."
* R-MEM step 1: "*Inputs.* The OFFICIAL decoy runs of the MB-S qualification … Each runs with the provisional cap
  (3 GiB) and MEM_POLL_S 2 s. A decoy with any memory-watchdog event is **not a valid input**. It is re-run with the
  provisional cap doubled, within the step-5 bound."
* R-MEM step 5 is a "Feasibility (host readings at qualification)" check. Step 6 may reset MEM_POLL_S to
  "max(0.5 s, 0.1 × MEM_CAP / g)".
* R-FREE: "The qualification records ≥ 10 readings, 30 s apart, of the prepared host". R-ALLOW (a): "any
  prepared-state qualification reading". R-EXCL-PCT: "any prepared-state reading".
* Protocol draft §8: the four constants "are frozen as the outputs of the four rules below, computed from the official
  qualification evidence … The values in the code are provisional (ratified for the pre-freeze build only)". The
  memory cap in particular is "derived at qualification from the official decoy runs only".

**Where the official qualification sits, and what binds the code:**
* Protocol draft §1: "Order: freeze → official qualification → independent qualification review → … → grant".
* Protocol draft §3: the grant is bound through the chain "freeze → qualification → review → grant, binding the driver
  sha256 and the manifest".
* Protocol draft §11.1, preconditions: "HEAD = freeze (review: the qualification commit on it)".
* MB r1 protocol §10 step 2 (the precedent the draft follows): "Official qualification at the freeze commit".
* Owner decisions §1: the freeze permission covers "R-rule constants" and "official target-free qualification at the
  frozen commit".
* Owner decisions §10: "create the MB-S freeze. Bind exactly: … R-rule constants; …" and "Do not mutate the frozen
  scientific object after acceptance."
* Owner decisions §11: "Run the complete official target-free qualification only against the exact frozen object",
  including "official decoy runs; host readings; R-rule checks". Also: "Do not tune against the failure inside the
  frozen campaign."
* Owner decisions §12: the reviewer verifies "absence of post-freeze tuning". §13: the grant binds "freeze;
  qualification; qualification review; driver digest; manifest".

### 1.2 A code fact that makes the conflict concrete (driver at `cc723527`)

* `MEM_CAP_BYTES = 3 * 1024 ** 3` and `MEM_POLL_S = 2.0` are module constants.
* The `decoy` branch of `main()` builds its context with `STATE.Ctx(mem_cap_bytes=MEM_CAP_BYTES,
  mem_poll_s=MEM_POLL_S)`. That is the same constant that `execute` and `resume` pass.
* The CLI has no memory-cap argument.
* So, at the frozen bytes, an official decoy runs under whatever cap the freeze carries. The same holds for the poll.

**Consequence.** Suppose the freeze commit carries the rule outputs, as the ratification's "Freeze … as the rule
outputs" and owner §10's "Bind exactly: … R-rule constants" read.
* The official decoys at that commit have not run yet, so the outputs cannot have been computed from them.
* Those decoys then run under the output cap, not "the provisional cap (3 GiB)" of R-MEM step 1.
* R-MEM step 1's re-run "with the provisional cap doubled" cannot be done on the frozen bytes at all without a
  driver facility.

Builder5's in-progress R-MEM input recording (brief 50 task 3) may change the decoy path. These statements are about
`cc723527` only.

### 1.3 Conclusion on the premise

**The conflict is genuine, and MBS-8 does not create it.** Three sets of texts cannot all be met by one freeze with
one qualification at it and unchanged driver bytes:
* the rules take their inputs from the official qualification (R-MEM step 1, run with the provisional 3 GiB and 2 s;
  the R-FREE, R-ALLOW and R-EXCL-PCT readings);
* the constants are frozen at the freeze as the rule outputs (heading, items 10/14/16, change 1, owner §10);
* the official qualification runs only against the exact frozen object, which the grant binds (protocol §1/§3/§11.1,
  owner §§1, 11, 13).

**Scope.** All four constants are in scope, and so is MEM_POLL_S, because R-MEM step 6 can change it.
* FREE_MEM_MIN depends on R-MEM's MEM_CAP, P and D, so it inherits R-MEM's sequencing.
* EXCL_CPU_PCT is in scope only conditionally: its frozen value is 25 unless the single R-EXCL-PCT exception fires on
  a prepared-state reading. But that reading is itself qualification evidence.

### 1.4 Does any accepted text already order the freeze and the rule application differently? No.

**The implementation reviews' to-do lists.** Two lists place the official decoys "before any freeze":
* reviewR3C1 (`REVIEW_IMPLEMENTATION_MBS308_DELTA_R3.md`, DELTA_ACCEPTED), "Remaining before any freeze": "Official
  decoys. Run under the launchd launcher, with the R-MEM, R-FREE, R-EXCL-PCT and R-ALLOW inputs recorded as the rules
  require … The four constants are then frozen as the rules' outputs. Protocol section 11 should list these
  qualification records."
* reviewIMPL's delta, which is DELTA_REJECTED as a verdict: "Still before any freeze (unchanged): … the official
  decoys under the launchd launcher (Q12 re-measured; the R-MEM / R-FREE / R-ALLOW inputs); full MBR1_REPRO and
  QS-RESUME-DECOY; … the user decisions S1, …".

Read literally, these put the rule application before the freeze commit. But neither list orders anything:
* Both lists also put "Full MBR1_REPRO and QS-RESUME-DECOY" before any freeze. Owner §11 places those in the official
  qualification, against the exact frozen object.
* Both also put the S1 ruling there. The conditions register binds S1 "at grant".
* reviewR3C1 itself calls the decoy records "qualification records" and says "I choose no freeze parameter".

The lists therefore use "before any freeze" to mean "still to be done", not as a sequence. They do not override owner
§§1, 10 and 11 or protocol §§1 and 11.1.

**Other texts:**
* The architecture addendum A1 says of the build requirements that "They become facts only at the successor
  qualification and freeze". Route re-check R3 says of RC1, RC2 and RC6 that they are "satisfied as facts only at the
  successor's qualification and freeze". The conditions register (S16 row) says "(b) as facts at qualification". These
  name the two events together and do not order them.
* Governance A1 S16, "There is no successor freeze and no official qualification until all four hold", gates both
  events and does not order them either.
* The ratification's "applied at the freeze from the official qualification evidence" states both ends of the
  conflict. It does not locate the qualification.

### 1.5 Does Q12 under MBS-8 (i) still raise a sequencing question? Not of its own.

**Owner §4:** the caps are fixed; "Do NOT derive MBS-8 option-(ii) caps from MB-S official decoy runtimes"; "Q12 must
therefore remain a genuine prospective pass/fail check of these fixed caps, not a consistency check whose values are
derived from the same official runs".

**Why this is MB r1's pattern:**
* The fixed caps and Q12's thresholds are in the frozen code before the official runs.
* Architecture §8, "What stays of MB r1", keeps "Q12 with host provenance". MB r1 §3.2 gives the thresholds: "EVAL_CAP
  ≥ ⌈1.5 × projection⌉ and every per-job cap ≥ 2 × the official maximum wall time of its kind and rung".
* The official runtimes are measured at the frozen commit, as route review RC6 requires ("Re-measure Q12 on decoys
  under the successor's own launcher").
* No value flows from those runs into the frozen code. This is MB r1's pattern, which ran without a sequencing
  conflict.

**Three couplings remain.** They are not conflicts:
* Q12 and R-MEM read the same official decoy runs. So how those runs are configured and counted depends on the R-rule
  resolution: which memory cap and poll they run under, whether an R-MEM step-1 re-run happens, and, under (b),
  which qualification's runs Q12 reads.
* Under any resolution in which the official decoys run with the provisional MEM_POLL_S, a step-6 change means the
  runtimes Q12 checks were measured at a different poll than the one executed. This applies to (c), and to the first
  round of (b).
* The owner's "genuine prospective pass/fail check" holds under every option below.

## 2. The options, against the accepted texts

### (a) Pre-freeze measurement runs; the frozen code carries their outputs; the official qualification recomputes and compares

**What it satisfies literally:**
* Owner §10 "Bind exactly: … R-rule constants", since the constants are in the freeze commit.
* Owner §11: one official qualification against the exact frozen object, with "R-rule checks".
* Protocol §1/§3/§11.1: a single freeze, with the qualification at it.
* The ratification's "applied at the freeze", in its first half.

**What it departs from:**
* The ratification heading, "… from the official qualification evidence".
* R-MEM step 1: the inputs are "The OFFICIAL decoy runs of the MB-S qualification", and pre-freeze runs are not runs
  of a qualification that owner §11 confines to the frozen object.
* R-FREE and R-ALLOW (a): their readings are "qualification" readings.
* Change 1: "the inputs recorded in the qualification".
* Protocol draft §8: "computed from the official qualification evidence", and "derived at qualification from the
  official decoy runs only".
* R-MEM step 1 at the official qualification itself: at `cc723527` the official decoys would run under the frozen
  output cap, not "the provisional cap (3 GiB)" (1.2).

**What it leaves open:**
* **The comparison.** Is the check exact equality with the frozen values, or a stated tolerance? If a tolerance, what
  is its value, and who sets it? The T6 ruling's M4 reserves operational numbers to non-holders (briefs 46 and 50). The draft itself says
  a tolerance "would itself need a ruling". No accepted text states the comparison. The pending case `R_RULES_OFFICIAL`
  says only "compared with the constants the frozen code carries".
* **The memory cap and poll of the official decoys.** Either the frozen values, which departs from step 1, or a
  separate 3 GiB / 2 s measurement setting in decoy mode, which is a driver change needing its own independent review.
* **The designated runs and readings.** Which decoy cells and blocks, how many readings, and when.
* A failed comparison is **not** open: owner §11 makes it a qualification failure, STOP before the target, with no
  tuning.

**The MB r1 precedent.** MB r1 §3.2 used this shape for its **caps**: a pre-freeze exploration, frozen values, and a
Q12 sufficiency check whose thresholds are part of the same frozen rule. No accepted text extends that pattern to the
R-rules. The ratification, the later and more specific text, names the official qualification as the source of the
inputs. The route review's RC1 ("re-derived only by the frozen §3.2 rule from decoy runtimes") concerns the caps,
which MBS-8 (i) now fixes. So the precedent illustrates (a) but does not bind it.

### (b) Two-step freeze: provisional values → official qualification → constants-only successor freeze → second qualification

**What it satisfies literally:**
* R-MEM step 1: the official decoys of the first qualification run at a frozen commit with the provisional 3 GiB and
  2 s, and a step-1 re-run is still possible there only if a cap facility is added (1.2).
* R-FREE, R-EXCL-PCT and R-ALLOW take qualification readings.
* The ratification heading, read as: applied at the second freeze from the first qualification's evidence.
* Change 1 and items 10, 14 and 16: "frozen as the rule outputs".
* Protocol §1's order within each round.

**What it departs from:**
* Owner §10 describes one freeze that binds the R-rule constants. Under (b) the first freeze binds provisional values.
* Owner §21's chain has a single "freeze -> official qualification -> independent qualification review".
* Owner §1 grants permission for "creation of the MB-S freeze commit", in the singular. Governance A1 §1 O4 holds that
  a same-caps freeze "needs a new explicit user decision recorded before it". So whether S16(c) covers a second freeze
  commit is not stated.
* Owner §12's "absence of post-freeze tuning": whether a pre-declared rule applied in a second freeze counts as
  "tuning" would need a reviewer's ruling. The constants cannot change Γ (ratification header), and owner §10's
  "scientific object" is untouched, but the texts do not say that this suffices.

**What it leaves open:**
* **Full or delta second qualification.** Owner §11's "complete official … qualification only against the exact frozen
  object" points to a full one against the final object.
* **The R-rule check of the second qualification.** A full second qualification has its own official decoys and
  prepared-state readings. R-ALLOW (a) adds "any prepared-state qualification reading", and those decoys no longer run
  at the provisional cap. So its outputs can differ from those the second freeze carries. Whether the second round
  re-derives with equality, applies a tolerance, or only runs the in-rule checks (step 5 feasibility, step 6 poll,
  R-FREE attainability) is not stated anywhere.
* Whether the first qualification needs its own independent review before the second freeze.

**Precedent.** MB r1 had successive freezes, r1 → r2 → r3. r2 and r3 each followed a failed official qualification,
and r3 had an explicit user authorization. None was a planned constants step. So they illustrate (b) but do not bind it.

### (c) The frozen code carries the rules; `execute` reads the values from the committed qualification evidence that the grant binds

**What it satisfies literally:**
* R-MEM step 1: the official decoys run at the frozen commit with the code's provisional 3 GiB / 2 s as the
  measurement setting, which fits item 10's "measurement cap of the official decoys".
* R-FREE, R-EXCL-PCT and R-ALLOW take qualification readings.
* The ratification heading's "from the official qualification evidence".
* Change 1's "inputs recorded in the qualification".
* Protocol §1/§11.1 and owner §11: one official qualification against the exact frozen object.
* Owner §13: the grant binds the qualification.

**What it departs from:**
* The ratification heading's "applied at the freeze": here the values are applied after the qualification.
* Item 10 ("Frozen value = R-MEM output") and change 1 ("Freeze MEM_CAP_BYTES, … as the rule outputs"): the driver
  constants are no longer the frozen values.
* Owner §§1 and 10: "R-rule constants" are bound at the freeze.
* Protocol draft §8: the four constants "are frozen as the outputs"; the text would need rewording.

**What it leaves open:**
* **Does "fixed by a frozen rule on committed, grant-bound evidence" count as "frozen"** for the ratification and for
  owner §10? That is a reading which only the owner, or a new ratification, can give.
* **The engineering.** This is a lifecycle driver change outside the RC1 text-identical science functions. It must say:
  * which evidence file is read, and which digest the grant carries;
  * that preflight, `execute` and `resume` refuse on a missing or mismatched value;
  * that the values are recorded in the journal so that resumes use the same ones;
  * that decoy and qualification modes keep the provisional values.

  It needs tests, mutants and its own independent review before the freeze. No such implementation exists or has been
  accepted at `cc723527`: `R_RULES_OFFICIAL` and `Q12_caps` are `PENDING_USER_DECISION`.

### (d) Host-state rules only: re-read the prepared host at a pre-grant step

**Why it is not a complete resolution:**
* It covers R-FREE's attainability, R-EXCL-PCT and R-ALLOW only.
* It leaves R-MEM, MEM_POLL_S (step 6) and R-FREE's **value**, which needs R-MEM's MEM_CAP, P and D, to one of (a),
  (b) or (c).

**What it departs from.** R-FREE's "The qualification records ≥ 10 readings" and R-ALLOW (a)'s "prepared-state
qualification reading". The protocol draft §11.2 itself notes that "the rule text places them in the qualification".

**What it leaves open:**
* which of (a), (b) or (c) covers R-MEM;
* where the pre-grant outputs live: in code, meaning another freeze, or as evidence read by `execute`, which is (c)'s
  mechanism;
* the step's placement relative to the qualification review.

### Other resolutions the texts suggest, and why they are excluded

* **(e) Qualify the unfrozen candidate, then freeze with the outputs.** Excluded by owner §1 ("official target-free
  qualification at the frozen commit"), owner §11 ("only against the exact frozen object"), protocol §11.1 ("HEAD =
  freeze") and MB r1 §10 step 2.
* **(f) One freeze, then edit the constants in or after the qualification commit, before the grant.** Excluded:
  * the executed driver would not be the qualified one (owner §11);
  * the grant's driver digest and manifest would not match the freeze (protocol §3, owner §13);
  * the Q8 manifest check (every namespace file must match the freeze manifest) would fail on any post-freeze change
    to a namespace file;
  * owner §12 requires the "absence of post-freeze tuning".
* **(g) Freeze the provisional values as final and use the rules as checks only.** Excluded by item 10 ("provisional 3
  GiB ratified only for the pre-freeze build and as the measurement cap"), item 16 ("Provisional for tonight's build")
  and change 1 ("as the rule outputs").
* **(h) "MB r1 did it this way."** Not a resolution by itself: see (a) and (b). No accepted text makes MB r1's sequence
  binding for the R-rules.

**A fact common to every option.** At `cc723527` the driver cannot run a decoy with a cap other than MEM_CAP_BYTES
(1.2). So R-MEM step 1's re-run "with the provisional cap doubled" needs a driver facility in every option in which
frozen bytes run the official decoys: (a)'s official check, (b)'s first round and (c). Only (a)'s pre-freeze runs
could use a pre-freeze build instead. R-MEM's D and g also have to be recorded (§11.2's last paragraph; builder5's
task 3) under every option.

## 3. Determination

**The test** (brief 51 point 3), and why it fails:
1. **Exactly one resolution follows mechanically.** No. (a), (b) and (c) each meet a different subset of the accepted
   texts word for word:
   * (a) meets owner §§10-11's single freeze that binds constants;
   * (b) meets the ratification's official inputs **and** its frozen outputs, but with two freezes;
   * (c) meets the official inputs and the single frozen object, but the values are not in the freeze commit.
2. **Every other resolution is ruled out by an accepted text.** No.
   * (a), (b) and (c) each **depart** from an accepted text, but no accepted text forbids any of them outright. Each
     departure turns on a reading: pre-freeze runs verified at the qualification; a second freeze under one S16(c)
     permission; values fixed by rule on grant-bound evidence.
   * (d) is incomplete.
   * (e), (f) and (g) are ruled out (section 2).
3. **Applying it needs no further owner choice.** No. Every live option carries at least one open sub-choice:
   * (a): equality or a tolerance, and who sets it; and the official decoys' cap and poll;
   * (b): full or delta; the second round's R-rule check; whether S16(c) covers two freeze commits;
   * (c): whether rule-on-evidence counts as "frozen".

**The owner's second route** (owner §7 item 4, "an independently accepted engineering implementation that does not
require another owner scientific-policy choice") is not available:
* no implementation of any option exists or has been accepted at `cc723527`;
* picking one to build would itself be the choice among (a)-(d) that owner §7 withholds from the campaign.

Owner §7: "If §11.2 still requires an explicit owner choice among (a)-(d), and no already-ratified prospective rule
uniquely determines it: STOP BEFORE FREEZE and ask me only that remaining question." Owner §22 A says the same.

**Verdict: not determined (line 2).** No freeze follows from this review.

## 4. The remaining question for the owner (self-contained)

**Background (facts only).**
* The ratified rules R-MEM, R-FREE, R-EXCL-PCT and R-ALLOW fix four MB-S constants: MEM_CAP_BYTES, FREE_MEM_MIN_BYTES,
  EXCL_CPU_PCT and EXCL_ALLOW. MEM_POLL_S is a fifth, because R-MEM step 6 can change it.
* The rules compute these values from the **official qualification's** decoy runs and prepared-host readings. R-MEM
  says those decoys run with the provisional 3 GiB memory cap and a 2 s poll.
* Your decisions §§1, 10 and 11 say:
  * the freeze binds the "R-rule constants";
  * the official qualification runs "only against the exact frozen object";
  * the grant binds the driver digest.
* The driver reads one memory-cap constant in both decoy and execute modes.
* So the constants cannot both sit in the frozen code and be computed from runs made on that frozen code. Every option
  below departs from at least one accepted text, named in each entry.
* Your MBS-8 (i) settles the caps. Q12 is a pass/fail check of those fixed caps under every option, and raises no
  question of its own.
* No accepted text states a default.

**Question.** Which sequencing do you choose for the R-rule constants? For the option you choose, please also answer
its sub-question(s).

**(a) Measure before the freeze, then check at the qualification.**
* *What happens:* designated decoy runs and host readings, in the official configuration, are made before the freeze
  and committed as pre-freeze evidence. The frozen code carries the rule outputs. The official qualification
  recomputes the rules from its own runs and compares.
* *Departs from:* the rules' wording that the inputs are the official qualification's runs and readings.
* *Sub-questions:*
  * (a-1) Is the comparison exact equality, or a stated tolerance? If a tolerance, what value, and who sets it?
  * (a-2) At the official qualification, do the decoys run with the frozen values, or with a separate 3 GiB / 2 s
    measurement setting? The second needs a reviewed driver change.
* *Precedent:* MB r1 used this shape for its caps, with the check thresholds written into the same frozen rule.

**(b) Two freezes.**
* *What happens:* the first freeze carries the provisional values, and the official qualification runs at it. A
  constants-only second freeze then carries the rule outputs, followed by a second qualification.
* *Departs from:* the single freeze of your §§1 and 10.
* *Sub-questions:*
  * (b-1) Is the second qualification full or delta? If delta, which cases?
  * (b-2) What R-rule check does the second qualification apply to its own runs and readings: re-derive and require
    equality, a tolerance, or only the rules' built-in checks?
  * (b-3) Does your freeze permission (S16(c)) cover both freeze commits?
* *Precedent:* MB r1's later freezes came only after failed qualifications.

**(c) The frozen code carries the rules, not the values.**
* *What happens:* the official qualification at the single freeze produces the values. `execute` (and `resume`) read
  them from the committed qualification evidence that the grant binds.
* *Departs from:* "frozen as the rule outputs" and "applied at the freeze", and your §10's binding of the constants at
  the freeze.
* *Sub-question:* (c-1) Do values fixed by the frozen rule on committed, grant-bound qualification evidence count as
  "frozen" for this purpose?
* *Needs:* a driver change, with tests, mutants and an independent review before the freeze.
* *Precedent:* none in the texts I read.

**(d) Host-state rules only.**
* *What happens:* R-FREE's attainability, R-EXCL-PCT and R-ALLOW are read at a pre-grant step instead of in the
  qualification.
* *Departs from:* the rule text, which places these readings in the qualification.
* *Sub-question:* (d-1) Which of (a), (b) or (c) then governs R-MEM, MEM_POLL_S and FREE_MEM_MIN's value?
* *Precedent:* none in the texts I read.

**If no option is chosen:** per your §§7 and 22 A, MB-S stays unfrozen and no official qualification runs.

---
**Leak scan:** after writing, this file was scanned with the research namespace's `code/c308_quarantine.py`
`_TAIL_RE`: **0 hits**. **Ledger:** one REVIEW line (agent `reviewSEQ`,
target_evaluations 0). **New cell-308 target evaluations: 0.**
