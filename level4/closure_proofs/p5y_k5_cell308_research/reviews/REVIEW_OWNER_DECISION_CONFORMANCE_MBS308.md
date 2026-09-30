# Conformance review of the recorded owner decisions for MB-S (S16(c), MBS-6, MBS-7, MBS-8, S1) — reviewS1T
DECISIONS_DO_NOT_CONFORM

**Brief.** Brief 52, recorded at research `3e3bf601`. I rule on the conformance of the text only, never on whether the
decisions are wise.

**Object.** `ledger/USER_RULING_MBS308_OWNER_DECISIONS.txt` (commit `5c2394ba`). I re-hashed it at `3e3bf601` and in
the working tree: sha256 `34eb1d41b56742fda2ba7fb7b70a46de5e0219ba324aa510437cc6c6d1065ad1`, 17291 bytes, 633 lines
(all LF-terminated, 33 non-ASCII UTF-8 bytes). The clerical index `ledger/USER_RULING_MBS308_OWNER_DECISIONS.md` is
read as an index only; the .txt is authoritative. Line numbers "L*n*" below refer to the .txt.

**Rulings at a glance.**

| check | subject | ruling |
|---|---|---|
| 1 | S1 content (A1 §3 as read by E1 D1, items 1–6; register S1, MBS-13, MBS-14; grant fields) | **DOES NOT CONFORM** on one element of item 1 (the express "notwithstanding the brief's §21"); **NEEDS A RULING** on the byte range the grant carries (items 3, 4 and 6 depend on it); items 2–6 otherwise CONFORM; conditional form compatible; no conflict in §§6, 15–18 |
| 2 | S16(c) against MB r1 protocol §14 / qualification review G2 (A1 §1, O4) | **CONFORMS** |
| 3 | MBS-6, MBS-7, MBS-8 option selection; MBS-8 (i) values | **CONFORMS** (all three); every cap value is equal on all three sides; see the note on the semantics row |
| 4 | Contradictions with accepted governance if applied | **CONFORMS**: no contradiction found; readings noted |

## 1. S1 (the grant ruling)

**Required content.** Governance addendum A1 §3: "The ruling put to the user must expressly:" items 1–6. Erratum E1
D1 re-reads items 1–2 (item 1 now includes "**notwithstanding the brief's §21 ("execute cell 308 exactly once") and
mitigation 5**"). E1 D1's reconciliation: "The successor therefore needs the user's ruling expressly
**notwithstanding** §21 and mitigation 5." Register row S1: "count 2; notwithstanding brief §21 and mitigation 5;
U1–U8; finality; caps; trade".

### 1.1 Item by item

| item (A1 §3 as read by E1 D1) | the user's words that meet it | ruling |
|---|---|---|
| 1a. a second consumed evaluation of cell 308 (count 2) | "I authorize exactly ONE MB-S consumed evaluation of Cell 308, which would be the second consumed evaluation of Cell 308 overall." (L145–146); "Cell 308's overall consumed count becomes 2." (L197–198) | express; meets it |
| 1b. under MB-S only | "This authorization applies to MB-S only." (L148) | express; meets it |
| 1c. notwithstanding mitigation 5 | "I lift mitigation 5 for MB-S only." (L150) | express; meets it |
| 1d. notwithstanding the brief's §21 ("execute cell 308 exactly once") | **absent as words.** The nearest words are "Sections 20, 21 and 23 remain binding on MB r1." (L152). They answer item 2's confirmation. They say that §21 binds MB r1; they do not say that the MB-S authorisation is given notwithstanding §21, or that §21 does not bar MB-S. The override follows only by inference, from 1a together with L152 | **only implicit**. Accepted texts require it to be express: A1 §3 ("must expressly") and E1 D1 ("needs the user's ruling expressly notwithstanding §21 and mitigation 5"). **DOES NOT CONFORM** |
| 2. lift mitigation 5 for MB-S; confirm that the brief's §20–§21 and §23 continue to bind MB r1 unchanged | L150 (lift); L152 (confirmation). "unchanged" is not written, but L152 states no change to them | meets it (see §5 item 3 on the unqualified word "Sections") |
| 3. a new governance decision, not a rerun on host grounds; MB r1 stays INDETERMINATE | "MB-S is a NEW GOVERNANCE DECISION." (L154); "It is NOT a rerun justified on host grounds." (L156); "Preserve historical MB r1 = INDETERMINATE." (L519, section 19 only) | meets it **if** the S1 text includes section 19. The "MB r1 stays INDETERMINATE" half is outside sections 5–6 (see 1.3) |
| 4. decide the §14 / G2 same-caps question | "MBS-8 = OPTION (i): MB r1 r3 CAPS" (L89) with the values (L93–105); "MBS-8 = (i)" (L165) | express; meets it. Section 5 carries the label only; the meaning is in section 4 (see 1.3) |
| 5. re-affirm U1–U8 of the C4 ruling | "I reaffirm U1-U8 for MB-S under the interpretation already established by the accepted successor governance." (L158–159) | express; meets it (see §5 item 4 on the qualifier). It supports `reaffirms_c4: true` |
| 6. whether a successor INDETERMINATE is final for route MB | "MBS-6 = OPTION (i): FINAL" (L48); L50–53; "MBS-6 = (i)" (L163); L459 | express; meets it. Section 5 carries the label only |
| register "trade" (C11R-I2 / COR-T) | "MBS-7 = OPTION (i)" (L68); "Do NOT add C11R-I2 or COR-T to MB-S." (L70); "MBS-7 = (i)" (L164) | express; meets it |

**Selecting "OPTION (A)" does not supply 1d.** Brief r2 §7 defines (A) as "give the ruling with the required content"
and says that "A ruling that lacks a required element does not meet S1". The recorded ruling neither cites that list
nor incorporates it by reference. The grant carries the ruling's bytes, not the brief's.

**MBS-13** (grant contents: "S1 verbatim", the review, triggers, C1–C9, S11–S17, no-trigger statement, launch
conditions; status "future"). The ruling's own list of what the grant binds (L371–381) is not stated to be exhaustive.
L167–169 defer to "the exact binding mechanism required by the frozen governance". No conflict.
**MBS-14** (adjudication contents). Nothing in the ruling excludes an item. Section 18 L503 ("Do not change the
criterion after observing Γ") and L505 ("Do not manufacture CELL308_CLOSED") agree with closure-only.

### 1.2 Grant fields, `check_grant`, and the conditional form

* **Fields.** The protocol draft at `cc723527` (§1, lines 14–16) and `mbs308_driver.py` `check_grant` (def at line
  851; the S1 test at lines 867–870) require `user_ruling_s1` = {`verbatim`: non-empty str, `sha256` = sha256 of
  `verbatim.encode()`, `reaffirms_c4`: true}. The text supplies what the fields need: a verbatim text exists, and
  `reaffirms_c4` is supported by L158. The UTF-8 bytes of any range round-trip, so the sha256 is well defined.
* **What `check_grant` does not check.** It tests only that the carried text agrees with its own digest. It does not
  test that the text is (part of) the ledger record `34eb1d41…` at `5c2394ba`. Provenance fields beyond the digest
  are not yet defined (MBS-13 "future"). The C4 precedent's grant recorded the ruling file's path, git blob and
  research commit (`ledger/USER_RULING_C4.md`, "How the campaign binds it"). The user's L168–169 ask for "its required
  digest/provenance fields".
* **Conditional form: compatible.** The chain at L137–143 (valid freeze → official qualification →
  QUALIFICATION_ACCEPTED independent review → valid grant bound to those exact artifacts) is the chain `check_grant`
  already enforces:
  * HEAD^^^ = freeze, HEAD^^ = qualification-only commit with an official PASS, HEAD^ = review-only commit with
    verdict QUALIFICATION_ACCEPTED, HEAD = grant-only commit;
  * the driver sha256 and the input manifest are bound.

  The further conditions at L171–180 (U7, U8, host preflight, grant validation, exactly-once controls) are pre-marker
  gates of the draft. A text given in advance whose conditions coincide with the mechanical checks is carried
  unchanged; `check_grant` does not interpret it. There is a precedent: the C4 ruling was given before its review and
  entered the grant only afterwards.
* **Order, a text point for the freeze.** The draft's §1 order reads "independent qualification review → the user's
  explicit S1 ruling → grant". This ruling is recorded before the freeze, with conditions. The accepted texts require
  only "before any grant" (A1, classification). This is not a non-conformance of the user's text. A frozen protocol
  that copies the draft's order would describe a sequence other than the one on record.

### 1.3 Which bytes are "the S1 text": NEEDS A RULING

No accepted text fixes the range:
* register MBS-13 says "S1 verbatim";
* the protocol draft says "the user's explicit ruling …";
* the user's L167 says "this ruling";
* the index `.md` (note 1: clerical, by a holder, not a ruling) proposes sections 5 and 6 and leaves the exact range
  to grant construction.

The options, each as whole lines with their newlines:

| option | lines | bytes [start, end) | length | sha256 | carries | lacks |
|---|---|---|---|---|---|---|
| R1 whole record | L1–L633 | [0, 17291) | 17291 | `34eb1d41b56742fda2ba7fb7b70a46de5e0219ba324aa510437cc6c6d1065ad1` (= the ledger record) | every item, including L519 and the meanings of the labels | nothing; but it also carries non-S1 instructions, and its own headings "20." (L522), "21." (L533) and "23." (L607) sit beside L152's unqualified "Sections 20, 21 and 23" |
| R2 section 5 | L127–L183 | [3624, 5006) | 1382 | `a04a0255fe19d5368eb4483a9d560c6ba25ac98c8139fd618c86efd700866e9d` | items 1a–1c, 2, 3 (first half), 5; items 4, 6 and the trade as labels only (L163–165) | item 3's "MB r1 stays INDETERMINATE" (L519); count 2 (L197–198); the meanings of "(i)" |
| R3 sections 5–6 (the index's proposal) | L127–L208 | [3624, 5736) | 2112 | `ff2878dae97ba1df8b6673244d8ae2d4f0bb4626c2059def54b0e6904ecdb56c` | as R2 plus the exactly-once limit and count 2 | L519; the meanings of "(i)" |
| R4 R3 plus sections 2–4, 15 and 19 | non-contiguous | — | — | — | every item | a concatenation rule, which no text defines |

**Who rules.** The user's L167–169 place the mechanism in "the frozen governance". The protocol draft at `cc723527`
does not fix a range. So the range is to be fixed either in the frozen MB-S protocol text (reviewed at the freeze) or
by the user. Under R2 or R3, item 3 is not fully present in the carried text.

### 1.4 Sections 6 and 15–18 against the accepted frozen-to-be rules

No conflict found.
* **Exactly-once.** Section 6 (L189–208): at most one new evaluation, count 0 → 2, no second `execute`, "A resume … is
  not a new evaluation", nothing replenishes. This agrees with U6 read for MB-S, with protocol draft §2 ("one
  evaluation, not a rerun") and with §6.
* **Recovery.** Section 16: "UNKNOWN is never DEAD." (L453); "At most 3 resumes are permitted within the frozen 7-day
  window." (L457); every INDETERMINATE final (L459). This matches:
  * `mbs308_state.py` at `cc723527`: MAX_RESUMES = 3 (line 64), DEADLINE_S = 7 days (line 65);
  * protocol draft §6 (b)–(c) and the liveness rule of §4;
  * MBS-3 (only `status` / `recover` / `resume` after the marker).
* **Execution.** Section 15 authorises execution only "If and only if every preceding gate succeeds" (L420). This is
  consistent with U7 and U8.
* **Persistence and seal.** Section 17 follows the frozen persistence and seal order and forbids selecting among
  outputs.
* **Review and adjudication.** Section 18 requires the execution review before the adjudication.
* **Readings (not conflicts).**
  * Sections 18 and 21 name no adjudication review, although U8 and protocol draft §1 name one. U8 is re-affirmed, and
    section 19's "accepted adjudication" presupposes acceptance, so nothing is waived.
  * "A valid negative scientific result" (L507): under the frozen outcome table the only valid non-closing result is
    CELL308_NOT_CLOSED_UNDER_MB. L501 ("Report the result exactly as established") pins it there.

## 2. S16(c): CONFORMS

* **The texts.**
  * MB r1 protocol §14 (worktree bytes verified identical to freeze r3 `c46434a3`, lines 361–362): "Freeze r3 is
    **never re-run**, and **no r4 with the same caps** is made, without a new explicit user decision recorded before
    it."
  * Qualification review G2, as quoted in A1 §1 (I did not open MB r1's review directory).
  * A1 §1, O4 reconciliation: MB-S's "freeze needs a new explicit user decision recorded before it (GC-9). That
    decision must also settle the caps question: keep MB r1's caps, or re-derive them from decoy runtimes under the
    new launcher".
* **Explicit.** "S16(c) = OPTION (A): GIVE PERMISSION" (L19); "I authorize the MB-S successor freeze …" (L21–22).
* **Recorded before.**
  * `5c2394ba` is an ancestor of `3e3bf601`.
  * The successor branch tip is `cc723527`. It has no freeze manifest, grant or qualification file, and there is no
    ref under `refs/p5y-k5-cell308-mbs-r1/`.
* **Covers the official qualification.** A1 S16 requires (c) before the official qualification too. L32 covers it.
* **Settles the caps question.** L31 brings the MBS-8 decision into the permission. Section 4 keeps MB r1's caps
  (L89) and forbids the other branch: "Do NOT derive MBS-8 option-(ii) caps from MB-S official decoy runtimes." (L114)
* **Conditional.** L21–22, L40 and sections 7–8 make the freeze wait for the other gates. A conditional permission
  still covers the freeze.
* **Note (reach).** "the MB-S successor freeze" is singular. The text does not say whether it covers a second MB-S
  freeze:
  * a constants-only second freeze (protocol §11.2 option (b));
  * a re-freeze after a repairable failure (section 22 B).

  This matters only if one is proposed (§5 item 5).

## 3. MBS-6, MBS-7, MBS-8: CONFORM

**Option wording.** From brief r2 (unchanged between `59dc1ada` and `3e3bf601`) and the register.

* **MBS-6.** Register: "finality … (recommended: final)". Brief r2 §4 (i): "an INDETERMINATE-class outcome of MB-S ends
  route MB on cell 308". The user: "OPTION (i): FINAL" (L48) and L50–53. One option, unambiguous. L59–60 ("Any
  scientifically distinct future route …") restate §26's path and do not qualify (i). Brief r2 §4 item 12 left open
  whether a later route carrying the members counts as "route MB". The text does not settle that, and no accepted
  text requires it to.
* **MBS-7.** Brief r2 §5 (i): "keep MB-S unchanged". The user: "OPTION (i): KEEP MB-S SCIENCE UNCHANGED" (L68) and
  "Do NOT add C11R-I2 or COR-T" (L70). One option, unambiguous. On L81, see §4.
* **MBS-8.** Brief r2 §6 (i): "MB r1's r3 caps", then the listed values. The user: "OPTION (i): MB r1 r3 CAPS" (L89)
  with the same values. One option, unambiguous. Section 10 (L306–312) repeats them.

**MBS-8 (i), mechanical comparison.**
* MB r1: the freeze r3 bytes `c46434a3` (the worktree driver and protocol blobs equal them).
* Successor: `git show cc723527:…`.
* The Python constants were read by AST, not by import.

| name | user (.txt) | MB r1 frozen r3 | successor `cc723527` | equal |
|---|---|---|---|---|
| EVAL_CAP | 8 h (L93) = 28 800 s | `code/mb308_driver.py:102` `8 * 3600`; `protocol/MB308_PROTOCOL.md:85` "8 h = 28 800 s" | `code/mbs308_driver.py:190` `8 * 3600`; protocol draft line 298 | yes |
| RLR per-job | 1800 / 4200 / 8700 s (L97) | `mb308_driver.py:126` {d4: 1800, d6: 4200, d8: 8700}; protocol:86 | `mbs308_driver.py:228`, same | yes |
| C2b per-job | 1800 / 1800 / 2700 s (L98) | `mb308_driver.py:126` {N20: 1800, N40: 1800, N80: 2700}; protocol:86 | `mbs308_driver.py:228`, same | yes |
| C1b per-job | 1800 s (L99) | `mb308_driver.py:127` {4, 8, 10, 12: 1800}; protocol:86 {d8, d10, d12: 1800} | `mbs308_driver.py:229`, same | yes |
| VER per-job | 1800 s (L100) | `mb308_driver.py:128` {4, 6, 8, 10, 12: 1800}; protocol:86–87 | `mbs308_driver.py:230`, same | yes |
| PRE_CAP | 1800 s (L104) | `mb308_driver.py:101`; protocol:85 | `mbs308_driver.py:189`; protocol draft 297 | yes |
| WORKERS | 5 (L105) | `mb308_driver.py:100`; protocol:85 | `mbs308_driver.py:188` | yes |
| EVAL_CAP semantics | "per attempt, awake time" (L93, L107); "Sleep does not count." (L109) | one execution, no resume; EVAL_CAP a wall-clock limit (protocol:367–368; `signal.alarm(EVAL_CAP_S)` at `mb308_driver.py:764`) | per attempt on CLOCK_UPTIME_RAW (`mbs308_driver.py:1113` `AwakeCap(EVAL_CAP_S)`; `mbs308_state.py:917–948`; protocol draft 298–299) | user = successor: **yes**; user = MB r1: **no (the MB r1 side differs)** |

The full RUNG_CPU_CAP_S tables are identical between the two drivers.

**The semantics row.** Under a literal reading of brief 52's rule ("any difference is DOES NOT CONFORM"), this row
would read DOES NOT CONFORM on the MB r1 side. I do not rule it so, for three reasons:
* No cap value differs.
* MB r1 has no attempts, so it has no per-attempt semantics to match.
* The option wording itself carries the successor's semantics under both options. Brief r2 §6 item 2, "Common to both
  options; your MBS-8 record should state this: EVAL_CAP applies per attempt, on awake time". Ratification item 4
  (ratified) says the same, and so does the implementation review, D10: "the user's MBS-8 decision must name this
  semantics explicitly".

The user's text names it (L93, L107–109). If the caller applies the rule literally, only this row changes, no word
of the user's text is at issue, and the verdict line is unchanged (check 1 decides it).

**The awake budget.** The implementation review (closing, "User decisions") adds "(up to 4 x 8 h awake within 7
days)". That total is not written as a number. It follows from L93 together with L457.

## 4. Contradictions with accepted governance: none found

* **r5, r6, K5, P5Y** (section 19, L513–519). The condition is conjunctive: "the accepted adjudication and existing
  governance explicitly authorize them". U5 (re-affirmed) is part of existing governance, so it authorises no
  adoption, no r6 and no K5 or P5Y closure. MB r1 stays INDETERMINATE (L519). Consistent with A1 §5 and S2.
* **Cell 309** (section 20). The section directs no action on 309 and forbids use of 309 work. Consistent with S10.
* **MB r1.** The text changes nothing in MB r1 (L152, L519). Consistent with S2 and E1 D1.
* **"Do not reopen the changed-science branch." (L81).** Its reach is ambiguous (§5 item 6). It may mean MBS-7
  option (ii). It may also mean S4's "changed" branch, the one that RC2, S11 and the route HOST row name after an
  MBR1_REPRO mismatch or a host change. On the second reading it turns "STOP and S4's changed branch" into STOP.
  Neither reading weakens a gate, and no accepted text obliges taking the changed branch.
* **Section 14.** It asks to "verify all frozen requirements, including" two items that the draft does not gate:
  "required lid/sleep state" (L395) and "restart hazards controlled" (L398). Draft §8 records sleep and lid state and
  never gates them; brief r2 §9 says restart is "not gated". Read as "verify the frozen requirements", nothing
  conflicts. A stop before the marker consumes nothing. Building a new gate into frozen code after the freeze would
  change the frozen object, which L319 itself forbids.
* **Section 21's repair loop and section 11's STOP.** Read together, a qualification-gate failure stops before the
  target (L343–347); the repair loop applies to defects that "can legally be repaired prospectively" (L594–595). MB-S's
  own repair rule is not frozen yet.
* **Other sections.**
  * Section 22 D ties any post-marker stop to the frozen state machine. Consistent with L5 / MBS-5(a).
  * Section 7 makes no choice among §11.2 (a)–(d). Consistent with draft §11.2 and brief r2 §8 ("No default").

## 5. For the user: the words that are missing or ambiguous

Stated neutrally. This section gives no advice on what to decide.

1. **Missing (S1, item 1).** The ruling has no words saying that the MB-S authorisation is given notwithstanding your
   brief's §21 ("execute cell 308 exactly once"). Present are:
   * "which would be the second consumed evaluation of Cell 308 overall" (L146);
   * "I lift mitigation 5 for MB-S only" (L150);
   * "Sections 20, 21 and 23 remain binding on MB r1" (L152).

   A1 §3 and E1 D1 require the §21 element expressly.
2. **Not fixed (S1 text for the grant).** "The grant must carry this ruling verbatim or by the exact binding mechanism
   required by the frozen governance" (L167–169). The text does not state which bytes "this ruling" is. The options
   are R1–R4 in §1.3. Under R2 or R3, "MB r1 stays INDETERMINATE" (L519) and the meanings of "(i)" are outside the
   carried text.
3. **Ambiguous on its face.** "Sections 20, 21 and 23" (L152) does not name the document. This record has its own
   sections numbered 20, 21 and 23 (L522, L533, L607). The only coherent referent is your earlier brief's §20, §21 and
   §23.
4. **Ambiguous reference.** "under the interpretation already established by the accepted successor governance"
   (L158–159). The accepted texts I read state no reading of U1–U8 for MB-S, in particular of U6's "exactly one
   authorized target evaluation under the frozen protocol". Route erratum E1 reads U6's "its result" as MB r1's
   result. Brief r2 §7 item 12 records the same gap.
5. **Ambiguous reach.** "the MB-S successor freeze" (L21) is singular. The text does not say whether the permission
   covers a second MB-S freeze (protocol §11.2 option (b), or a re-freeze under section 22 B).
6. **Ambiguous reach.** "Do not reopen the changed-science branch" (L81) may mean MBS-7 option (ii), or S4's
   changed-science path after an MBR1_REPRO mismatch or a host change (§4).
7. **Beyond the draft's gates.** "required lid/sleep state" (L395) and "restart hazards controlled" (L398) are listed
   under "verify all frozen requirements". The protocol draft does not gate either.

## Reviewer statement (reviewS1T)

* **Independence.** I am not a holder of any MB r1 run observation. I am independent of the coordinator, the builders,
  the ratifier and every earlier reviewer.
* **Starting context.** My session began with a host-supplied memory index (MEMORY.md). I did not use it or open any
  of its files. It carries no clock time, runtime, progress figure or host reading of the MB r1 run. It carries an MB
  r1 outcome label (also in the governance texts) and generic lessons without values.
* **What I read, and an observation I keep out.** Governance A1 (read in full, as the brief directs) contains in §2 a
  qualitative, host-log-based attribution of how the MB r1 run was interrupted. It has no clock time, runtime or
  progress. I do not reproduce it, and nothing here depends on it. The other texts I read name clock times only of
  governance events and host readings, never of the MB r1 run. None is reproduced here.
* **Files read.** The object (.txt, .md); governance A1 (full); E1 D1 and its closing note (lines 1–30, 50–54; not D2
  or D3); the register; brief r2; `ledger/USER_RULING_C4.md`; the ratification (header and items 4, 18, 19); the
  implementation review (D5, D10 and the closing lines only); route erratum E1 (DR1) and E2; `code/c308_quarantine.py`
  (structure and `log_event`).
  * MB r1: `code/mb308_driver.py` and `protocol/MB308_PROTOCOL.md` at `c46434a3` (the cap passages, §7, and §14
    lines 356–372).
  * Successor, by `git show cc723527:…` only: the driver, `mbs308_state.py` and the protocol draft. I also ran
    read-only ref queries on the successor branch (tip = `cc723527`).
* **Not opened.** Everything brief 52 excludes. I read "*_MBS308*" as the incident-independence reviews, since the
  object itself matches the broader pattern. I also did not open `TAIL_FIGURE_PATTERNS.json` (used only through
  `_TAIL_RE`).
* **Actions.** Reading and text search only. No git write. No target evaluation, direct or indirect: 0 target
  evaluations, and no Γ(5,308; ·) and no cell 305–309 computed. Cell 309 out of scope. I wrote this file and one
  research-ledger line. Tail-figure scan of this file with `code/c308_quarantine.py` `_TAIL_RE`: 0 hits.
