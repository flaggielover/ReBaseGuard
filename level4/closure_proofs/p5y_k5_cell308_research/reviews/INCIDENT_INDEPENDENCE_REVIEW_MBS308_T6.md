# Bounded ruling on trigger T6: the successor builder's pre-rule reading of the MB r1 postexec record (reviewINC2)
T6_FIRED_MITIGATED

**Ruling.** T6 fired. The rating stays **MEDIUM–HIGH (upper end), not lowered**, conditional on M1–M8 below. If any
of M1–M6 fails, the rating is **HIGH**.

**This is an explicit amendment of T6's consequence for this one instance.** The review said any trigger makes the
rating HIGH. The text of T6 is unchanged, and it is not reinterpreted. This is not the silent narrowing of a gate: the
consequence is replaced here, on the record, for this case only. The reasons are in section 3.

## 1. Facts verified (read-only)

* **The build.** Commit `afba20e5` on `p5y-k5-cell308-mbs-r1` is a single-parent child of `21e99cf0`. It adds
  `BUILD_REPORT.md`, the successor code, the tests and the protocol draft (20 files).
* **The disclosure.** `BUILD_REPORT.md` §9 says that, before its GC-6 instruction (2026-09-29T18:39:04Z per governance
  erratum E1 D2), builder2:
  * read `NSF/postexec/MB308_RECOVERY_RECORD.md` in full;
  * listed the other `postexec/` file names with line counts only;
  * saw the governance and route reviews only as 22- and 15-line headers.

  It says builder2 did not open the recovery chain, the execution review, the adjudication or its review. The record's
  items it names are: the run chronology, the coordinator-reported launch host readings, the qualitative pool-load
  continuation, the caffeinate PIDs and the probe and trial ids.
* **The incident.** The ledger line of 2026-09-29T21:05:13Z (coordinator, INCIDENT, count 0) records it. It is
  committed in `e084b70a`, which also records brief 37 (the non-holder implementation review) and brief 38 (this
  ruling).
* **My review.** It is committed at `b7e62dec`, byte-identical to what I wrote (sha256 `89a2b6ae…1562b`).
* **E1″ erratum 2** (`6a33f22d`) adds `NSF/postexec/*` in the successor worktree as a location. Its holders include
  "every agent that read one of the locations above", which covers builder2, but it does not name builder2.
* **Caps.** The build's CPU caps and wall caps are MB r1's frozen values. The rung CPU-cap table is textually
  identical, and PRE_CAP, EVAL_CAP and DECOY_CAP are equal constants.
* **Values builder2 set.** These are new and provisional (`BUILD_REPORT` §5 GC-10 and §10 item 2):
  * the memory-cap rule (a multiplier of the largest official decoy per-job peak RSS, with a floor);
  * the free-memory headroom;
  * the exclusivity CPU threshold and the allow-list.
* **Not verified by me.** I did not read the content of the postexec record; it is forbidden to me. I rely on:
  * builder2's enumeration;
  * E1″'s location table, which places the 23:10 per-worker audit in the session transcript and the per-coalition CPU
    values in REVIEW_EXECUTION_INTERRUPTION §4b, and puts only qualitative content in `postexec`;
  * the adjudication's statement that the 23:10 audit is reported in the recovery assessment.

## 2. Does T6 fire?

**Yes.** `NSF/postexec/*` is an E1″ location (the main table, and erratum 2), so builder2 is an E1″ holder. Builder2
held the successor implementation role. T6 depends on the state, not on when the reading happened, so reading before
the rule does not stop it firing. T6_NOT_FIRED is not available.

## 3. Why mitigated rather than HIGH

* **What was read.** It falls in the two classes that my review's Q1 table rated "No" and "Barely" informative about
  the value: host state, and aggregate runtime given as event times. It contains none of the per-job runtime class,
  the only class I rated weakly target-informative in principle: no 23:10 per-worker observation and no per-coalition
  CPU value.
* **What the role could touch.** Under N1–N4 the implementation role cannot move Γ. T6 guards two things: the
  operational numbers that set completion probability, and the truth of S13's promise.
  * The CPU and wall caps are MB r1's frozen values, so builder2 made no caps choice.
  * The resume and deadline constants come from the architecture.
  * The only values builder2 set itself are the provisional memory, headroom and exclusivity values. They are
    completion-probability parameters, still to be frozen from official decoys, and they can be re-derived
    independently (M3).
* **Pre-rule, and disclosed.** The reading came before any rule reached the builder. It was disclosed plainly, as
  S13 and E1″ required ("disclose any earlier reading"). Governance chose disclosure as the remedy for exactly this
  case. My T6 did not carve that case out; this ruling does, for this case only.
* **HIGH would add nothing here.** HIGH changes only what the S1 ruling is taken in view of. M1–M6 remove the channel
  itself. The rating should track the risk that remains, and after M1–M6 that is the MEDIUM–HIGH risk the review
  already rated.

## 4. Conditions (before the MB-S freeze unless stated)

* **M1. Non-dependence, itemised.** Brief 37's item 10 must return a trace for every constant, cap, limit, timeout,
  threshold, interval, budget and allow-list in the successor code and protocol draft. Each is traced to one of:
  * an MB r1 frozen value, byte-equal;
  * the architecture or review text, cited;
  * recorded decoy, synthetic or host evidence, with a stated rule and a ledger line.

  A non-holder re-derives any item it cannot trace. If that is impossible, the rating is HIGH.
* **M2. The content, confirmed.** An agent that already holds `postexec` confirms in one REVIEW ledger line that
  `MB308_RECOVERY_RECORD.md` holds only the kinds of item BUILD_REPORT §9 lists. The agent is neither the coordinator
  nor builder2; reviewADJ or reviewEXEC would do, and neither becomes a new holder. The record must hold no per-job
  runtime, 23:10 per-worker observation, per-coalition CPU value, in-run thermal reading or memory event. If it holds
  any of these, this ruling is re-opened.
* **M3. Builder-set values replaced or confirmed.** Before the freeze a non-holder confirms or replaces the memory-cap
  rule (multiplier and floor), the free-memory headroom, the exclusivity threshold and the allow-list, with a written
  rationale from decoy or host evidence only. Their frozen values come from official decoy runs that a non-holder
  executes.
* **M4. builder2's roles from now on.**
  * The exposure record names builder2 as an E1″ holder, with what it read (named, never valued).
  * builder2 takes no caps, qualification (official runs, verifier, manifest, scanner), qualification-review or
    S1-brief role.
  * Bounded code repairs are allowed only on a non-holder reviewer's request. They never set or change an operational
    number, and a non-holder reviews each repair diff.
* **M5. Non-holders verified.** Every later implementation, caps and qualification agent is checked against the full
  MBS-1 location list. Brief 37's forbidden list covers it; I checked this.
* **M6. No precedent beyond this case.** This mitigation covers builder2's pre-instruction reading only. The following
  fires T6 at HIGH, unmitigated: any agent that reads an MBS-1 location after the rule reached it, and holds or takes a
  route, implementation, caps or qualification role. For builder2 the rule arrived at 2026-09-29T18:39:04Z; for every
  other agent, with governance A1 (`ce145e51`).
* **M7. The S1 brief discloses:**
  * that T6 fired and was ruled mitigated (this file: path, sha256, line 2);
  * that the successor builder read the MB r1 postexec recovery record in full before its exposure instruction, with
    the items named (the chronology, the launch host readings, the qualitative pool-load continuation, the caffeinate
    PIDs, the probe and trial ids) and no values;
  * the M1 verdict (brief 37) and the M2 confirmation;
  * that the rating stays MEDIUM–HIGH only under M1–M6, and is HIGH otherwise.
* **M8. The grant and the adjudication** carry this ruling verbatim and the outcomes of M1–M6 (extending MBS-13 and
  MBS-14).

## 5. Resulting rating

**MEDIUM–HIGH (upper end), unchanged**, now stated as: "result-chasing risk MEDIUM–HIGH (MB-S, byte-identical
science; re-rated after a second consumption; T6 fired and mitigated per `..._T6.md`; escalates to HIGH on T1–T6 or on
failure of M1–M6)". Every other condition of the review (MBS-1 to MBS-14) stands.

## 6. Checks

* Read-only: no driver mode, no git write, no forbidden file read (the postexec record was not opened). Nothing
  computed for cells 305–309 or the band; cell 309 untouched.
* No tail figure, no cap value and no run-time value of the MB r1 run appears here. Line 2 is the only whole-line
  ruling token.
* One REVIEW ledger line (agent reviewINC2). New target evaluations: 0.
