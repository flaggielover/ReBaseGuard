# Cell-308 successor MB-S r1: rulings on the open readings of the ratified R-rule text (ratifier2, brief 55)
READINGS_RULED

Ratifier `ratifier2`, a fresh ratifier. Brief: `ledger/briefs/55_ratifier2_rule_readings.txt`, sha256
`d2e55157ffcf9d1a0437c036f387cd4771b3bf6928a01ea9595b3904b7124332`, verified before anything else was read.

I set no number, I change no number and I amend no rule. Each ruling says how the accepted rule text is to be READ
where a function had to choose a reading. Where the text does not decide, I say exactly what it leaves open and who
must decide. The authority is the section "Written rules" of `governance/CONSTANTS_RATIFICATION_MBS308.md`, verbatim.
Its dev-input illustration, its table and its evidence are not rules; where I use them it is as a check on a reading,
and I say so.

## 0. Sources, method, disclosure

| source | what I read | sha256 |
|---|---|---|
| `governance/CONSTANTS_RATIFICATION_MBS308.md` (worktree) | "Written rules" in full (lines 36-84); lines 2-9; table rows 10, 11, 13, 14, 15, 22, 23 (the lines a text search for sampler / growth / D1 / MEM_POLL / roundup returned); evidence lines 106-124 (end of H3, H4, D1, D0, the first lines of Q) | `caa742100ed5362e68d2444e1f4bc4ef2c3aac2084d72f406fa373fb1f2316ae` |
| `reviews/REVIEW_PREFREEZE_TOOLING_MBS308.md` (worktree) | section 1 (all, for (f)); section 7 (all: F-6, G-10, ruling (b), READING-7); line 343 | `789c93489cab9ba1c08597ade695b223fd650ca168ce7ffbf8932404cd4edee1` |
| `reviews/REVIEW_SEQUENCING_DETERMINATION_MBS308.md` (worktree) | sections 1.2 and 2 (a) | `83dc92fec1bf2b7d90aa0a8620925ba945bdce8ae8a3c972a8dec0343f6dc54e` |
| `ledger/USER_RULING_MBS308_OWNER_SUPPLEMENT_1.txt` (worktree) | Part I, sections 1-4, in full (lines 24-174) | `3f7d477b24900b64c7e30b3180ae7114fe642753956e31fe185fc6ef129d33d6` |
| successor `protocol/MBS308_PROTOCOL_DRAFT.md` at `555f4cbf` | section 8 (with 8.1, 8.2) and section 11.3 | `45cb343a581dbab1f2ae3d1897a9b815300cb30263e6e3318ebcca7567bb0cad` |
| successor `code/mbs308_rrules.py` at `555f4cbf` | all 374 lines | `688347d3a00e0317a162ec0cf4f031b4c4757e095f82e01d933e4ab440a60e75` |
| successor `BUILD_REPORT.md` at `555f4cbf` | sections 16.6 and 16.9; in sections 15-16 only the lines a text search for READING / R-MEM / R_RULES / sampler returned | `cc15352800e34e92298a225f3e4337219ba9ee35d9d133204ae2667eec609966` |

Successor bytes were read with `git show 555f4cbf:<path>` only, never from the worktree. Also read: the top-level
names and the `log_event` signature of `code/c308_quarantine.py`; a name listing of `governance/`; the last two lines
of the ledger (to see its format).

**Method.** Reading and text search only. No computation of any campaign quantity (the only things I computed are the
sha256 values above and of this file). No git write. No cell-308 target evaluation; nothing here concerns any
cell-308 outcome. I did not read the sampler's source (`mbs308_state.py` is not among my sources): items 2 and 3 are
ruled on the rule text, on protocol 11.3, on BUILD_REPORT 16.6 / 16.9 and on reviewQ6's description.

**Not opened.** None of: `reviews/REVIEW_EXECUTION_INTERRUPTION*`, `audit/EXECUTION_INTERRUPTION_*`,
`reviews/REVIEW_SUCCESSOR_GOVERNANCE_308*`, `reviews/INCIDENT_INDEPENDENCE_REVIEW_MB308*` or `*_MBS308*`,
`ledger/COORDINATOR_EXPOSURE_DISCLOSURE*`, `ledger/USER_TEXTS_SUCCESSOR_308.md`,
`governance/SUCCESSOR_GOVERNANCE_308.md` (its name appeared in the directory listing; not opened), `history/`, anything
under `p5y_k5_cell308_mb_r1/{review,adjudication,postexec,evidence}/`, successor BUILD_REPORT sections 6 and 9, any
other scratchpad, anything under `/Users/suzhe/.claude/`. No `git log` on the MB r1 branch.

**Disclosure of MB r1 material in my context.**
* The host tool put a memory index (MEMORY.md) into my starting context. It is not a source and I opened none of the
  files it names. It carries no measured quantity of the MB r1 run (no runtime, memory, CPU or timing figure). It
  does carry (i) the outcome label of MB r1 in one line (consumed once, INDETERMINATE, never rerun), (ii) one general
  lesson line, without figures and not attributed there to a named run, that host sleep and thermal slowdown inflate
  wall times and contaminate runtime gates, and (iii) qualitative lesson lines of the successor campaign. Whether (i)
  or (ii) counts as a "run observation" is for the exposure register; I disclose both. Neither bears on any ruling
  below: the rulings concern memory, CPU-share and allow-list rules, and set no number.
* reviewQ6 section 1 (e), which I read for (f), names public verdict labels of MB r1's execution review and
  adjudication (label names only).
* My read of the ratification's evidence ended two lines into its item Q, so I saw one line of resource fields of MB
  r1's official PRE-GRANT qualification decoy (its wall and worker-CPU time), recorded by the first non-holder
  ratifier. It is a qualification-decoy reading, not an observation of the MB r1 run; I did not use it.

## Rulings at a glance

| item | subject | ruling |
|---|---|---|
| 1 | READING-3 (R-MEM step 3) | **CONFIRMED** |
| 2 | READING-6 (step 6, "≤ 0.5 s") | **CORRECTED**: the bound binds the observed spacing; a record whose largest spacing exceeds 0.5 s is not a valid step-6 input; invalid input, fail closed. The set interval is **not fixed by the text** |
| 3 | READING-7 (step 6, first reading of a fresh worker) | **CONFIRMED as written**: the text requires neither growth from zero nor growth from process start. Limitation recorded for the owner |
| 4 | F-6 (step 1, invalid run and clean duplicate) | **CORRECTED**: cell coverage by another clean run is not the text's cure |
| 5 | step 1 under the user's option (a) | (a) pre-freeze: meaning stated, both texts honoured. (b) official run with an event: **the rule text and the user's ruling cannot both be honoured**; reported, not resolved |
| 6 | canonical outputs | defined by the text for MEM_CAP_BYTES, FREE_MEM_MIN_BYTES, EXCL_CPU_PCT, EXCL_ALLOW; for MEM_POLL_S the text **fixes no canonical form** in one branch |
| READING-1, 2, 4, 5 | reviewQ6's confirmations | each **CONFIRMED** (one line each, with one note each where the text is narrower than the line) |

## 1. READING-3 (R-MEM step 3): CONFIRMED

Rule text: "3. s = max over each (kind, rung) that appears in two or more valid runs of (largest peak / smallest peak).
s = 1 if no rung appears twice."

The functions read it correctly: a (kind, rung)'s peak in one run is the largest step-2 job peak of that kind and
rung in that run, and s compares those per-run peaks across the valid runs in which the (kind, rung) appears.

* The unit the text counts is the run. A (kind, rung) qualifies by appearing "in two or more valid runs", and the
  fallback is "if no rung appears twice". An appearance is an appearance in a run; the ratio is over those
  appearances; so each appearance has one peak.
* "Peak" in this rule is always a maximum (step 2: P is a max over jobs; D is "the driver's own peak RSS in those
  runs"). The peak of a (kind, rung) in a run that holds several jobs of it (its blocks) is the largest of them.
* The other reading (every job peak of that kind and rung in the valid runs) makes the text's own condition
  arbitrary: the spread between two blocks inside one run would count when the rung also appears in a second run and
  would not count when it does not. The text gives no ground for that, and "s = 1 if no rung appears twice" excludes
  a ratio taken inside a single run.
* Check against the ratification's stated reason for k (table item 11; not a rule): "the same job varied ≤ 1.09× from
  run to run (D0 vs D1), and 3 leaves ≥ 2× beyond that for decoy-to-target variation at identical rungs". s is a
  run-to-run spread at identical rungs. Differences between blocks inside one run are already in P, which is a
  maximum over every job.

So reviewQ6's probe C (two blocks of one rung in one run, far apart) is read as the function reads it, and the mutant
of G-10 that takes a rung's last job instead of its largest departs from the confirmed reading.

Observation, not one of the six questions (for the reviewer of R_RULES_OFFICIAL): the function silently skips a
(kind, rung) whose smallest per-run peak is 0 (`min(v) > 0`). The text states no such exception. A ratio with a zero
denominator is undefined and a zero peak of a job that ran is not a measurement; a silent skip is not something the
text provides.

## 2. READING-6 (R-MEM step 6, "a ≤ 0.5 s qualification sampler"): CORRECTED

Rule text: "6. *Poll re-check.* g = the highest RSS growth rate seen by a ≤ 0.5 s qualification sampler. Require
g × MEM_POLL_S ≤ 0.1 × MEM_CAP; otherwise MEM_POLL_S = max(0.5 s, 0.1 × MEM_CAP / g)."

**Reading the functions must implement.** The bound "≤ 0.5 s" binds the spacing between the sampler's consecutive
readings as it occurred, not only the interval the sampler was set to. A set interval of at most 0.5 s is necessary
(the function checks it today, `interval_s`) and not sufficient. **A record whose largest observed spacing exceeds
0.5 s is not a valid step-6 input.** A spacing of exactly 0.5 s is within the bound. For such a record the text
states no remedy, no allowance and no re-run: the functions must treat it as an invalid input and fail closed (no g
from it, no MEM_POLL_S, R-MEM not OK). reviewQ6's interim ruling (7 (b): R_RULES_OFFICIAL "must not accept a record
whose largest spacing exceeds 0.5 s silently") becomes: must not accept it.

Reasons.
* The text states one inequality and no allowance. It does not say "nominal".
* g is a rate, and a rate is seen over the time between two readings. The bound limits that time. A reading that
  looks only at the setting puts no limit on the time between readings: a sampler set to 0.5 s that in fact read
  every few seconds would pass. That reading leaves the inequality without content for what was measured.
* To accept a spacing above 0.5 s "by jitter" is to accept spacings up to some larger figure, and no accepted text
  states that figure. The user's ruling (Part I section 2): "If an existing accepted R-rule already defines an
  inequality, tolerance, rounding rule or acceptance interval, retain it exactly." "This ruling creates NO new
  tolerance." "Do not invent a tolerance." The only reading that needs no new number is the inequality applied to
  the observed spacing.
* It is the treatment the functions already give "30 s apart" (READING-1: every observed gap is checked).
* Against, and weighed: in the ratification's own idiom a sampler is named by its setting ("The 2 s ps watchdog";
  evidence D1: "My independent 0.5 s ps sampler"), and the first ratifier's own sampler may well have had spacings
  above 0.5 s. The illustration and the evidence are not the rule (protocol section 8: the "dev-input illustration is
  not part of the rules"); and the idiom says what a sampler is called, not by how much its readings may exceed the
  stated bound. It does not supply the missing allowance.

What follows (stated; none of it decided by me).
* As built the sampler runs on a fixed-rate 0.5 s schedule, "the rule's own bound", and every largest spacing reported
  for it (0.505 s, 0.51 s, 0.555 s; protocol 11.3, BUILD_REPORT 16.6 and 16.9, reviewQ6 7 (b)) exceeds 0.5 s. None
  of those records is a valid step-6 input under this ruling.
* The text's sign is "≤": it admits a sampler set below 0.5 s. **NOT DECIDABLE FROM THE TEXT: the value of the set
  interval.** I set none. Because g depends on it, it must be one value, identical in the pre-freeze series and in
  the official series (user section 1: "in the exact intended official configuration") and carried by the bytes that
  are frozen. Who decides: a non-holder builder (not the coordinator: T6 ruling M4), subject to the fresh independent
  review of Part I section 4, which must verify that "R-MEM's new peak-RSS and <=0.5 s growth-sampler inputs are
  present"; the owner if that reviewer finds the choice needs authority.
* **NOT DECIDABLE FROM THE TEXT: whether a decoy whose sampler record is invalid may be measured again.** Step 1
  provides a re-run for one case only (a watchdog event); step 6 provides none. For a designated pre-freeze run this
  belongs to the designation of the runs (which, how many, replaced when), which reviewSEQ 2 (a) lists as open under
  option (a): it must be fixed before the runs are made and pass the Part I section 4 review; the owner if it needs a
  new rule. For an official qualification run the function fails closed and no text I read provides a second
  measurement.

## 3. READING-7 (R-MEM step 6, a fresh worker's rise before its first reading): CONFIRMED as written

Rule text: "g = the highest RSS growth rate seen by a ≤ 0.5 s qualification sampler."

reviewQ6 7 (b): "the sampler measures growth only for a process it has already seen, so a fresh worker's rise before
its first reading is never counted in g."

**Ruling.** Step 6 covers this as written. g is the highest growth rate "seen by" the sampler, and a growth rate is
seen between two readings of the same process. Of a worker's rise before its first reading the sampler has one
reading; that is not a rate it saw. The text does not make the first reading count as growth from zero, and it does
not reckon growth from process start: neither "zero" nor the start of a process appears in the text, and the sampler
takes no reading at process start. Either construction adds an imputed value to the sampler's readings and makes g
larger or equal. That would be a change to the rule (a stricter g), not a reading of it, and I may not make it.

* The rule defines g through a sampler of stated resolution and so accepts what such a sampler does not resolve. The
  ratification says this of sampling in terms (table item 11: "sampling under-reads"; item 13: "Sampling can only
  under-read a peak") and compensates where it chose to (P also takes ru_maxrss). For g it chose "seen by a ≤ 0.5 s
  … sampler" and the margin 0.1 × MEM_CAP.
* With item 2, the uncounted rise lasts less than one spacing, so at most 0.5 s per worker.

**Limitation recorded for the owner (not a ruling).** Every job runs in a fresh worker, so under the rule as written
the first part of every job's rise, up to one spacing, lies outside g; a job that reaches its peak before its
worker's first reading contributes nothing to g. If the owner wants that rise counted (for instance the first reading
taken as growth from zero over the preceding spacing), that is an amendment. It can only raise g and so can only
lower MEM_POLL_S. It would have to be decided by the owner before the designated pre-freeze measurements, because it
changes g in both series. The functions must not adopt it on a builder's, a reviewer's or the coordinator's
initiative.

## 4. F-6 (R-MEM step 1, an invalid run and a clean duplicate): CORRECTED

Rule text: "A decoy with any memory-watchdog event is **not a valid input**. It is re-run with the provisional cap
doubled, within the step-5 bound."

reviewQ6 1 (f): "a re-run that itself has a watchdog event is silently dropped when another clean run covers its cell
(status OK, its peak ignored; probe C); with one run per cell the same input is INCOMPLETE_INPUT."

Correct as built: the peaks of an event run are never used; an event run that has no re-run gives RERUN_REQUIRED and
no rule is applied. Not a correct reading: letting cell coverage by some other clean run stand in for the re-run.

**Reading the functions must implement.**
1. The text gives one cure for an event: a re-run of that decoy with the cap at twice the provisional cap, within
   the step-5 bound. Coverage of the cell by another clean run is not a cure the text knows. A valid run cures an
   event run only if it is a re-run of it at the doubled cap. An ordinary clean duplicate of the cell, at the
   provisional cap, cures nothing (whether it is itself a valid input is a separate matter).
2. A re-run that itself has an event is "a decoy with any memory-watchdog event". Both sentences apply to it: it is
   not a valid input, and it is to be re-run "with the provisional cap doubled". The provisional cap is the 3 GiB of
   the sentence before, so every re-run has the same cap, 2 × 3 GiB. The text has one doubling, not a ladder.
3. While any event run, original or re-run, has no valid re-run, the functions apply no rule and say that a re-run
   is required: never OK, and not INCOMPLETE_INPUT, which names a different defect. This is protocol 11.3's own
   sentence ("apply no rule until every such run has been re-run"), which the function does not yet honour for a
   re-run with an event.
4. What the text does not state, and I do not add: a limit on the number of re-runs; a further doubling; that an
   event at the doubled cap ends the qualification. An event run stays in the record with its reason whatever
   follows: "not a valid input" is not "not a record".

Scope. The text names one ground on which an official decoy is "not a valid input", the watchdog event, and I rule
on that ground only. The other reasons the function uses (not under the launcher, not the frozen ladder, WORKERS not
5, cap or poll not as ruled, fields unrecorded) test whether a run is an official decoy as step 1 describes it and
whether its record is complete. The text says nothing about dropping such a run in favour of a duplicate. As built, a
run whose peaks are unrecorded is dropped with status OK when a duplicate covers its cell; whether that is acceptable
is for the reviewer of R_RULES_OFFICIAL, not decided by the rule text.

## 5. Step 1 under the user's option (a)

Rule text (step 1): "The OFFICIAL decoy runs of the MB-S qualification: the real driver's `decoy` under the launchd
launcher, frozen ladder, WORKERS 5, the decoy cells of the qualification plan. Each runs with the provisional cap
(3 GiB) and MEM_POLL_S 2 s. A decoy with any memory-watchdog event is **not a valid input**. It is re-run with the
provisional cap doubled, within the step-5 bound."

User's ruling, Part I: section 1, "Before the MB-S freeze, perform the designated target-free measurement runs and
prepared-host readings in the exact intended official configuration. Use those prospective measurements as inputs to
the already-ratified R-rules."; section 3, "Official qualification decoys use the ACTUAL FROZEN VALUES. Do NOT
introduce a separate 3-GiB / 2-second measurement configuration."; and, on option (a), "unless a later independent
review proves option (a) mechanically impossible under the already-ratified rules. If that happens, STOP before
freeze and report the exact incompatibility. Do not silently substitute another option."

**Which runs are step 1's inputs.** In the pre-freeze series the designated runs are the rule's inputs (section 1) and
step 1 applies to them as written, cap 3 GiB and poll 2 s included. In the official series the decoys run with the
frozen values (section 3). The sentence "Each runs with the provisional cap (3 GiB) and MEM_POLL_S 2 s" cannot be
true of them unless the frozen values happen to be those; the user's ruling displaces that sentence for the official
series, and knowingly (section 4: "this resolves a conflict in the previous accepted wording"). Two consequences:
* In the official series the function's cap and poll checks must be against the frozen values. As built
  (`MEASUREMENT_CAP_NOT_AS_RULED`, `MEM_POLL_S_NOT_2`) every official decoy run at frozen values other than 3 GiB and
  2 s would be an invalid input.
* "The exact intended official configuration" of section 1 cannot include the cap and the poll: their official values
  are the outputs being derived. The two series differ in exactly these two values whenever the outputs are not
  3 GiB and 2 s. This follows from the user's own chain in section 3; it is for the section 4 reviewer ("measurement
  configuration is the intended official configuration").

**(a) A designated pre-freeze run with a watchdog event: the rule text and the user's ruling are both honoured.**
* The run is not a valid input. Its peaks are never used. Its record is kept.
* It is re-run: the same decoy (same cell, launcher, frozen ladder, WORKERS 5, MEM_POLL_S 2 s) with the cap at
  exactly 2 × 3 GiB = 6 GiB.
* "Within the step-5 bound": the re-run cap takes MEM_CAP's place in step 5's inequality, that is
  6 GiB + (WORKERS − 1) × P + D ≤ hw.memsize − W_idle. It is a condition on the doubled cap, checked before the
  re-run is made. It is not a licence for a smaller cap: the text names one re-run cap, and step 5 says "k, WORKERS
  and the floor are never reduced silently". If the doubled cap is not within the bound, the text provides no
  re-run; the event decoy has no valid input; R-MEM cannot be applied, nothing can be derived to freeze: stop and
  report to the owner.
* Left open by the text: (i) which P and D stand in the bound when the check is made. Step 2 defines them over
  "every valid official decoy"; the event run is not valid; if no other valid run exists they are undefined. Who
  decides: the owner, if that case arises. (ii) How the pre-freeze driver is made to run a decoy at 6 GiB (reviewSEQ
  1.2: "The CLI has no memory-cap argument"). Whatever the means, it is a driver change needing its own independent
  review (reviewSEQ 2 (a)), and it must not remain in the frozen bytes as a measurement configuration (section 3).
  Who decides: a non-holder builder and the Part I section 4 review.
* Illustration only, no rule input and nothing I computed beyond reading it: table item 10 of the ratification
  prints the same sum for the 3 GiB cap on dev figures with the user's apps open ("3 GiB + 4 × 95.6 MB + 55.5 MiB =
  3.41 GiB ≤ 8 GiB − 1.80 GiB wired = 6.2 GiB"). On those printed figures a 6 GiB cap would not be within the
  bound. The real check needs the recorded prepared-host readings. I mention it so that nobody assumes the re-run
  is available on this host.

**(b) An official qualification run with a watchdog event: the rule text and the user's ruling cannot both be
honoured.**
* What both allow: the event run is not a valid input and is never used.
* The rule then says "It is re-run with the provisional cap doubled". On the text's words that cap is 6 GiB. On any
  other reading of "the provisional cap" in the official series (for instance the cap the decoy ran with) it is still
  a cap other than the frozen one.
* The user's ruling says "Official qualification decoys use the ACTUAL FROZEN VALUES" and forbids a separate
  measurement configuration; and the frozen bytes carry one cap (reviewSEQ 1.2: the re-run "cannot be done on the
  frozen bytes at all without a driver facility").
* So a re-run the rule prescribes is a run the user's ruling forbids, and a re-run the user's ruling allows (at the
  frozen values) is not the re-run the rule prescribes. No reading of "re-run with the provisional cap doubled"
  honours both.
* Therefore the two texts together do not say what the official qualification does after an event in an official
  decoy. That cell has no valid input. Canonical output B is undefined for MEM_CAP and for the two outputs that take
  R-MEM's values (MEM_POLL_S, FREE_MEM_MIN). "A == B" cannot be established for them.
* A consequence of section 3 that bears on the same decision: in the official series the frozen cap is the kill
  line, so a decoy peak above the frozen cap can never be recorded as a larger P. It can only appear as an event.

I do not resolve it. This is the incompatibility to report under the user's ruling ("STOP before freeze and report
the exact incompatibility"). It concerns one branch, an event in an official decoy; in every other case option (a)
runs as the user describes it. But the frozen object must say what the official qualification does in that branch,
and no accepted text says it. Whether that amounts to "mechanically impossible", and what the branch must be, are the
owner's to decide.

## 6. The final canonical output of each rule, as the text defines it

No tolerance is introduced and nothing is said about whether exact agreement is desirable. "Round up to a multiple"
is read in its only ordinary sense: the least multiple that is not below the argument (an exact multiple is
unchanged). The text states no intermediate rounding, so every intermediate quantity (s, k, k × P, the sums) is its
exact value.

* **MEM_CAP_BYTES.** Text: "MEM_CAP = roundup_256MiB(max(k × P, 1 GiB)), k = max(3, 2s)." Type and unit: an integer
  number of bytes. Form: a multiple of 256 MiB, at least 1 GiB. Inputs in bytes (`job_maxrss_bytes`,
  `worker_peak_rss_bytes`); s an exact ratio of two such integers. The text fixes the canonical form: equality is
  equality of integers. Step 5 is a pass / fail condition on each application of the rule ("If violated, the
  qualification **fails on memory**"), retained exactly; it is not part of the value.
* **MEM_POLL_S.** Text: step 1, "MEM_POLL_S 2 s"; step 6, "Require g × MEM_POLL_S ≤ 0.1 × MEM_CAP; otherwise
  MEM_POLL_S = max(0.5 s, 0.1 × MEM_CAP / g)." Type and unit: a duration in seconds. Three cases.
  (i) The inequality holds: the output is the MEM_POLL_S that was re-checked, unchanged. Canonical.
  (ii) It fails and 0.1 × MEM_CAP / g ≤ 0.5 s: the output is 0.5 s. Canonical.
  (iii) It fails and 0.1 × MEM_CAP / g > 0.5 s: the output is that exact quotient. **Here the text does not fix a
  canonical form**: it states no rounding, no grid and no number of digits, and g is itself an unrounded
  measurement (bytes per second, from readings and their times). In this case two series have the same output only
  if they have the same g and the same MEM_CAP. The text also does not say in what form a frozen constant carries a
  quotient that has no finite decimal expansion. This is the output and the text to name under the user's section 2
  ("If exact canonical-output agreement is undefined or inappropriate for any specific output under the accepted
  rule: STOP BEFORE FREEZE and identify exactly which output and which accepted text causes the problem"), should
  case (iii) arise in either series. Who decides: the owner.
  Which value is re-checked: in the text it is the poll the decoys ran with (step 1: 2 s). In the official series the
  decoys run with the frozen value (user section 3) and no 2 s configuration exists, so the value re-checked there is
  the frozen one, and case (i) keeps it unchanged: an inequality the rule already defines (section 2: "retain it
  exactly"). I state this as what the text's structure and section 3 give together; the text predates option (a)
  and does not say it in terms. It is for the Part I section 4 reviewer to check.
  g also depends on two things the text does not fix: the sampler's set interval (item 2) and, by the owner's choice
  only, the treatment of first readings (item 3).
* **FREE_MEM_MIN_BYTES.** Text: "FREE_MEM_MIN = max(2 GiB, roundup_256MiB(MEM_CAP + (WORKERS − 1) × P + D)), with the
  R-MEM values." Type and unit: an integer number of bytes. Form: a multiple of 256 MiB, at least 2 GiB. The text
  fixes the canonical form: equality of integers. Attainability ("At least 3 consecutive readings must reach
  FREE_MEM_MIN. Otherwise it records GATE_UNATTAINABLE … the value is never reduced silently") is a recorded pass /
  fail condition on each series, retained exactly; it does not change the value and is not part of it.
* **EXCL_CPU_PCT.** Text: "EXCL_CPU_PCT = 25. There is exactly one exception. If the hosting app that runs the
  launcher, which cannot be quit, exceeds 25 in any prepared-state reading, then EXCL_CPU_PCT = min(50,
  roundup_5(1.25 × its maximum reading))." Type and unit: an integer, in the percent-of-CPU unit of the `ps` reading
  the gate compares. Form: 25, or a multiple of 5 not above 50 (by the formula, one of 35, 40, 45, 50). "Exceeds" is
  strictly greater. The text fixes the canonical form: equality of integers.
* **EXCL_ALLOW.** Text: "The frozen list = the current 39 names ∪ the basename (`comm.rsplit('/')[-1]`, as
  `busy_processes` computes it) of every process that meets both conditions". Type: a set of names (character
  strings), defined by a union; the 39 names and the additions from "this ratification's H3 readings" are the same in
  every series. The text defines **no ordering** and, being a union, no duplicates; an element is a basename
  exactly as that expression computes it (string identity; the text states no case folding or other normalisation).
  Equality is equality of sets (user section 2: "compare the canonicalized final set exactly"). The text fixes no
  canonical serialisation; set equality needs none, and the sorted list the function emits is the function's own.
  "Each addition is recorded with its path and reading" is a record, not part of the set.

Not outputs, but inputs the text does not fix and on which outputs depend: the sampler's set interval (item 2); the
identification of the hosting app (READING-4 below); the composition of each series (which decoy cells, how many
prepared-state readings beyond the minimum of 10).

## READING-1, 2, 4, 5: reviewQ6's confirmations

* **READING-1: CONFIRMED.** Text: "The qualification records ≥ 10 readings, 30 s apart, of the prepared host (AC
  power, the operator's apps quit, the hosting app idle)." AC power is inside the text's own description of the
  prepared host, so a reading not on AC is not a prepared-state reading; "30 s apart" as every consecutive gap of at
  least 30 s is the reading that needs no allowance (the text gives a number and no tolerance).
* **READING-2: CONFIRMED.** Text: "P = max over every job of every valid official decoy of max(`job_maxrss_bytes` …,
  `worker_peak_rss_bytes` [watchdog ps])." P is a maximum of maxima, so taking the watchdog's peak per run instead of
  per job gives the same P when every worker runs one job, and otherwise can only raise it. Note: step 3's peaks are
  per (kind, rung), and a per-run watchdog peak cannot be attributed to one; there the per-job record governs, which
  the text does not contradict.
* **READING-4: CONFIRMED.** Text: "If the hosting app that runs the launcher, which cannot be quit, exceeds 25 in any
  prepared-state reading, then EXCL_CPU_PCT = min(50, roundup_5(1.25 × its maximum reading))." The gate compares
  processes one by one, so the hosting app's reading is its largest single-process reading; a sum would raise the
  threshold beyond what the exception needs. Note: the text identifies the hosting app only as the one "that runs the
  launcher"; the bundle path given as input must be the same in both series and is recorded.
* **READING-5: CONFIRMED.** Text: "Never added: anything under `/Applications`, `/Users`, `/opt`, `/usr/local`,
  `/Library/Frameworks`, `/usr/bin` or `/bin` (tools a user can invoke), any Python interpreter, or the hosting app."
  The name and `Python.framework` tests are a sound reading of "any Python interpreter" for processes that could
  pass condition (b), and testing (b) on a location as stated is sound because a path under a listed directory lies
  under it whatever follows. Note: the text does not define an interpreter by name; an interpreter under another
  basename is not caught by the test, and the text's safeguard for that is "Each addition is recorded with its path
  and reading".

**G-10 (the four formula details no control pins).** Each is computed by the function as the text says: D is the
largest driver peak ("the driver's own peak RSS in those runs"); the per-run watchdog peak is part of P (READING-2);
a rung's per-run peak is its largest job peak (item 1); the sum of step 5 has (WORKERS − 1) × P, four workers for
WORKERS 5 (table item 14: "one worker at the kill line, four at peak, plus the driver"). The gap is in the controls,
not in the reading.

## What is left open, and who must decide

| open point | left open by | who must decide |
|---|---|---|
| what the official qualification does after a watchdog event in an official decoy (item 5 (b)) | rule step 1 against user Part I section 3 | the owner; STOP before the freeze and report |
| MEM_POLL_S has no canonical form when step 6 fails above the 0.5 s floor (item 6, case (iii)) | rule step 6 (no rounding stated) | the owner, under user Part I section 2, if the case arises |
| the sampler's set interval (item 2) | rule step 6 ("≤", no value) | a non-holder builder, under the Part I section 4 review; the owner if that review requires |
| whether a decoy with an invalid sampler record may be measured again (item 2) | rule step 6 (no remedy stated) | fixed before the runs in the designation of the pre-freeze series and reviewed under Part I section 4; the owner if a new rule is needed |
| which P and D stand in the step-5 bound for a re-run when no other valid run exists (item 5 (a)) | rule steps 1, 2, 5 | the owner, if the case arises |
| the means of a 6 GiB pre-freeze re-run (item 5 (a)) | not a rule matter; driver | a non-holder builder and independent review |
| counting a fresh worker's rise before its first reading (item 3) | not open: the text does not count it | the owner alone, as an amendment, before the pre-freeze measurements |
| number of re-runs at the doubled cap; further doubling (item 4) | rule step 1 states neither | nobody may add them; the owner alone, as an amendment |

## Integrity

Read-only: reading and text search; no git write; no campaign quantity computed; no target evaluation; no file
written other than this one. Scanned with `code/c308_quarantine.py` `_TAIL_RE`: 0 matches. One ledger line recorded
with `log_event` (class REVIEW, agent `ratifier2`, 0 target evaluations) after this file was written. My rulings were
not predetermined by the brief, and they set, change or tolerate no number.
