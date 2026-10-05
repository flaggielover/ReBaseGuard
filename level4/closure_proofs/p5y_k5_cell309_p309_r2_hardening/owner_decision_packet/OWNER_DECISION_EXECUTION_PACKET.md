# P309-r2 owner decision execution packet

**Nothing in this packet is a decision.** Every "Recommendation" is a recommendation only, and is labelled so. No answer
is inferred from any instruction, earlier recommendation or review. Every item stays exactly as the repository records
it (§0) until the owner answers it in their own words, through `OWNER_REPLY_FORM.md`.

This packet authorizes nothing. In particular it does not authorize incorporation, the freeze, the qualification, a
grant, Γ(309), or any change of scientific status.

## 0. Sources and current classification

Every source is located by commit, path, sha256 and line in `OWNER_DECISION_EVIDENCE_MAP.json`, computed from git.

| id | source | commit | sha256 (first 12) |
|---|---|---|---|
| R2_PACKET | `level4/closure_proofs/p5y_k5_cell309_p309_r2/governance/OWNER_DECISION_PACKET_R2.md` (5th revision) | r2 `101ef2cb` (last changed `2fc6c130`) | `9be65aa61625` |
| MSG_1_3 | `…_p309_r2/governance/OWNER_INSTRUCTIONS_R2_VERBATIM.md` (owner messages 1–3) | r2 `101ef2cb` | `05b88579fc6f` |
| MSG_4 | `…_p309_r2/governance/OWNER_INSTRUCTIONS_R2_MSG4_VERBATIM.md` (owner message 4) | r2 `101ef2cb` | `75bccb12d705` |
| R2_AMENDMENTS | `…_p309_r2/governance/P309_R2_AMENDMENTS.md` (§A provisional names, §C execute on a shared host) | r2 `101ef2cb` | `908da234d61d` |
| R2_HOST_SESSION | `…_p309_r2/governance/` host-side session instructions (steps 8a–8d; §7 "what remains owner-gated after 8d") | r2 `101ef2cb` | `5cdaee7a2506` |
| R2_FREEZE_PARAMS | `…_p309_r2/code/make_freeze_params.py` (reads `governance/OWNER_OD_R2_6_ANSWER.json` if present) | r2 `101ef2cb` | `e9ebd875bdf9` |
| FORMAL_RECORD / FORMAL_REVIEW | `…_p309_r2_hardening/formal_review_followup_5/` (record; verbatim review) | hardening `bbe0b253` | `17083865b767` / `9b1c2eaa7498` |
| AID_TASK2 | `…_p309_r2_hardening/OWNER_DECISIONS_OD_R2.md` (decision aid, recommendations only; it defines the proposed OD-R2-H and F-DRILL-ORDER items) | hardening (last changed `ae7db324`) | `c78406114c21` |
| DURABLE_HOST_PACKET | `…_p309_r2_hardening/DURABLE_HOST_EXECUTION_PACKET.md` (prerequisites P0.1–P0.5) | hardening (`ae7db324`) | `0475777259c5` |

**Repository classification of every item: OPEN.**
- r2 holds **no owner answer file**. A `git ls-tree` of r2's `governance/` finds no `*ANSWER*` or `OWNER_OD*` file;
  in particular `governance/OWNER_OD_R2_6_ANSWER.json` (read by `make_freeze_params.py`, l.201) is absent.
- R2_PACKET says "Nothing in it is decided" (l.3–4).
- Message 4 "decides none of OD-R2-0 … OD-R2-6" (MSG_4 l.11) and reserves them to the owner (item 7, l.90).
- OD-R2-H, the F-DRILL-ORDER action and SF1 are defined outside r2 (AID_TASK2; FORMAL_REVIEW) and have no answer
  anywhere.
- No item is ANSWERED, DEFERRED or SUPERSEDED in the repository.
- **One textual staleness, disclosed.** AID_TASK2's OD-R2-H text, written before the candidate existed, speaks of the
  hardening "on `claude/p309-r2-hardening-20261005`" as a single-file delta. The formal review has since accepted the
  concrete candidate `a119e978`, so §1.12 presents OD-R2-H against that candidate, under the review's condition C1.

**Binding constraints from the owner's verbatim texts** (they apply to every option):
- message 1 §5B: no retry or resume "merely for convenience" (MSG_1_3 l.225);
- message 1 §10: stop at `READY_FOR_OWNER_GRANT_DECISION` (l.342);
- message 3 §3, §6, §8: exclusive heavy compute; do not alter cell 308; never interrupt cell 308 (MSG_1_3 l.424, 440, 447);
- message 4 item 13: the cloud session is not an official durable host (MSG_4 l.107).

**State of the work** (§8 confirms it):
- r1 `c902fe2f`, r2 `101ef2cb` and main `1cb45382` are unchanged;
- the candidate `a119e978` is formally accepted (`FORMAL_DELTA_REVIEW_ACCEPTED_WITH_NONBLOCKING_FOLLOWUPS`), but **not
  incorporated**;
- there is no freeze and no qualification;
- NEW Γ309 TARGET EVALUATIONS = 0; no grant;
- r5 is unchanged and there is no r6; Cell 309 is OPEN.

## 1. Decision inventory

The fields follow the brief: (1) ID, (2) exact question, (3) why it exists, (4) options, (5) existing recommendation,
(6) evidence per option, (7) consequences, (8) decidable now?, (9) what it authorizes, (10) what it does not authorize,
(11) what it gates, (12) dependencies, (13) required owner wording.

"Gates" uses six columns: **Inc**orporation, **Frz** (freeze), **Drl** (worker-tier drill), **Q**ualification,
**Gr**ant, **Tgt** (target evaluation). ● means gates, ○ means does not.

---

### 1.1 OD-R2-0(A): confirm the record

1. **ID:** OD-R2-0(A) (R2_PACKET l.35).
2. **Question (packet):** confirm that `OWNER_INSTRUCTIONS_R2_VERBATIM.md` records messages 1–3 verbatim, with one
   disclosed redaction (the retired worker's IP), and that message 4 is recorded verbatim in its own file,
   `OWNER_INSTRUCTIONS_R2_MSG4_VERBATIM.md` (sha256 `de3c8e44…`).
3. **Why:** r2's authority rests on these texts, and they are immutable under self-audit A3.
4. **Options:** CONFIRM, or CORRECT (name the discrepancy).
5. **Existing recommendation (AID_TASK2):** confirm.
6. **Evidence:**
   - both files carry per-message sha256 values (message 3 `78cd27da…`, message 4 `de3c8e44…`);
   - QC15 A3 keeps them byte-identical.
7. **Consequences:**
   - CONFIRM settles the record; nothing runs.
   - CORRECT requires an additive correction record (the files are immutable).
8. **Decidable now:** yes.
9. **Authorizes:** nothing operational. It settles the record.
10. **Does not authorize:** anything else.
11. **Gates:** Inc ○ · Frz ● (OD-R2-0 is "needed before the r2 freeze") · Drl ○ · Q ● · Gr ○ · Tgt ○.
12. **Dependencies:** none.
13. **Owner wording:** `OD-R2-0(A): CONFIRM` or `OD-R2-0(A): CORRECT — <discrepancy>`.

### 1.2 OD-R2-0(B): confirm the carry-over

1. **ID:** OD-R2-0(B) (R2_PACKET l.43; table l.61).
2. **Question:** confirm each row of the carry-over table, which maps r1's owner decisions to their proposed r2 status
   (17 rows).
3. **Why:** r1's owner decisions were made for r1, and r2 inherits only what the owner confirms.
4. **Options:** CONFIRM ALL ROWS, or CONFIRM WITH AMENDMENTS (row by row).
   - Two rows are routed elsewhere by the table itself: EXECUTION HOST → OD-R2-6, and the D5 names → OD-R2-2.
   - P0-1 / G2 is "not carried" and is replaced by (D).
5. **Existing recommendation (AID_TASK2):** confirm.
6. **Evidence:** the table's sources for each row (messages 1, 3 and 4; owner rulings 2; r1's owner decisions, all
   verbatim in r2).
7. **Consequences:**
   - CONFIRM: the inherited rules bind r2 as listed.
   - Amending a row: that rule changes for r2, which may need code or review depending on the row.
8. **Decidable now:** yes.
9. **Authorizes:** the inherited rules apply to r2.
10. **Does not authorize:** the freeze or qualification (that is (D)); any host (OD-R2-3/4/6).
11. **Gates:** Inc ○ · Frz ● · Drl ○ · Q ● · Gr ○ · Tgt ○.
12. **Dependencies:** none. Rows deferring to OD-R2-2 and OD-R2-6 are answered there.
13. **Owner wording:** `OD-R2-0(B): CONFIRM ALL ROWS`, or `OD-R2-0(B): CONFIRM EXCEPT <row> → <amendment>`.

### 1.3 OD-R2-0(C): acknowledge the r1-era events

1. **ID:** OD-R2-0(C) (R2_PACKET l.44; liabilities l.84).
2. **Question:** acknowledge the listed events "for the purpose of proceeding with r2":
   - r1's failed qualification;
   - the P309F-01 incident and errata FE-1 to FE-11;
   - r1's unreviewed allowlist entries;
   - the 22:41:12Z reboot;
   - the postmortem reviewer's firewall departure;
   - brief timing;
   - r2's development history.
3. **Why:** r2 proceeds on a record that contains known departures.
4. **Options:**
   - ACKNOWLEDGE (as listed);
   - ACKNOWLEDGE WITH ADDITIONS (AID_TASK2 proposes adding the post-packet events below);
   - DECLINE (r2 does not proceed).
5. **Existing recommendation (AID_TASK2):** acknowledge, adding the recovery-session events. This packet adds the
   later development-only events listed in point 6, as a recommendation.
6. **Evidence for the additions** (all development-only; none was an official attempt):
   - the r1 Q11 recovery (recovery branch `290b6c10`);
   - three cloud-session interruptions in task 1;
   - r2's baseline durability defects (`R2_FAILURE_MATRIX.json`);
   - two later development-host interruptions, both preserved as INTERRUPTED and never resumed: a rehearsal that died
     on disk exhaustion (task 3), and a container reboot during validation runs (task 4).
7. **Consequences:**
   - ACKNOWLEDGE: r2 may proceed on this record.
   - DECLINE: r2 stops.
8. **Decidable now:** yes.
9. **Authorizes:** proceeding with r2 on the acknowledged record.
10. **Does not authorize:** any execution step.
11. **Gates:** Inc ○ · Frz ● · Drl ○ · Q ● · Gr ○ · Tgt ○.
12. **Dependencies:** none.
13. **Owner wording:** `OD-R2-0(C): ACKNOWLEDGE`, `OD-R2-0(C): ACKNOWLEDGE WITH ADDITIONS (§1.3 item 6)`, or
    `OD-R2-0(C): DECLINE`.

### 1.4 OD-R2-0(D): authorize, or decline, the r2 stage (the freeze and the single official qualification)

1. **ID:** OD-R2-0(D) (R2_PACKET l.46).
2. **Question, with the packet's proposed text verbatim:**

   > "Authorize, for the successor campaign p5y_k5_cell309_p309_r2:
   > * the formal freeze and the single official qualification (QC01–QC17, QC-U2, QC-D5, Q-HOST; started only through
   >   code/p309_launch.py; no retry, no resumption), both on the **qualification host** approved under OD-R2-3 and
   >   OD-R2-4;
   > * the independent qualification review;
   > * the preparation of the grant package.
   >
   > This names and approves no **target-execution host**; that is OD-R2-6, decided separately. It does NOT issue the
   > target execution grant, does not arm or consume a marker, and does not authorize any Γ309 evaluation."

3. **Why:** r1's P0-1 / G2 is not carried, and r2's freeze and its one attempt need their own authority. Under P23 a
   failed or interrupted r2 ends r2; any r3 is a new owner decision.
4. **Options (packet):** AUTHORIZE (the text above), or DECLINE.
   - Leaving it unanswered keeps it OPEN. That is the absence of an answer, not a third option.
5. **Existing recommendation (AID_TASK2, and this packet):** **do not answer AUTHORIZE yet.** The prerequisites below
   are outstanding.
6. **Evidence:**
   - the formal review accepted the candidate, with C1 (incorporation form), C2 (SF1 before the freeze) and C3 (the
     worker-tier drill on the incorporated bytes);
   - DURABLE_HOST_PACKET P0.1–P0.5;
   - R2_HOST_SESSION §7: after 8d, a pre-freeze follow-up review (gate step 9), then the freeze on the worker.
7. **Consequences:**
   - AUTHORIZE: the next official run is r2's only attempt. Any interruption ends r2 (P23; message 1 §5B).
   - DECLINE: r2 stays pre-freeze; drills and development may continue.
8. **Decidable now:** **no.** The prerequisites are outstanding:

   | # | prerequisite | source | state |
   |---|---|---|---|
   | P-1 | the candidate incorporated into r2 under C1 (needs OD-R2-H = H-A, then the owner's fast-forward) | FORMAL_RECORD C1 | outstanding |
   | P-2 | SF1 resolved (SF1-A reviewed and incorporated, or SF1-B recorded on the qualification host) | FORMAL_RECORD C2 | outstanding |
   | P-3 | the worker-tier drill (8d) PASS on the incorporated (and, if SF1-A, re-incorporated) bytes | FORMAL_RECORD C3; R2_HOST_SESSION §4 | outstanding |
   | P-4 | OD-R2-3 and OD-R2-4 answered; 8a audit and 8b verdict `HOST_SUITABLE` on the qualification host; 8c bootstrap of the consented items only | R2_PACKET OD-R2-3/4; R2_HOST_SESSION §1–3; msg 1 §4 | outstanding (host status HOST_SUITABILITY_PENDING) |
   | P-5 | OD-R2-5 answered, and the exclusive windows agreed with every non-root workload on the host | R2_PACKET OD-R2-5; R2_HOST_SESSION §4.1 | outstanding |
   | P-6 | the cell-308 operator's `foreign_uids` and heavy-job patterns (the gate refuses an empty list) | R2_PACKET OD-R2-4/5; DURABLE_HOST_PACKET P0.5 | outstanding |
   | P-7 | the host provides IMDS, or a reviewed host-portability change exists | DURABLE_HOST_PACKET P0.4 | open until the host is known |
   | P-8 | the pre-freeze follow-up review (gate step 9) on the drilled bytes | R2_HOST_SESSION §7 | outstanding |
   | P-9 | OD-R2-0(A)–(C), OD-R2-1/1b and OD-R2-2 answered (the names are frozen) | R2_PACKET | open |
   | P-10 | OD-R2-6(iii) settled (may the freeze name a host?), so the frozen `proposed_execution_host` is intended | R2_PACKET l.314; R2_FREEZE_PARAMS l.201–213 | open (default: no host named) |
   | P-11 | governance records filed in r2 after incorporation: the follow-up-5 brief/review, supplement 5 (already in the candidate), and the owner's recorded answers | FORMAL_RECORD l.14; §5 below | outstanding |

9. **Authorizes (if AUTHORIZE):** exactly the quoted text: the freeze, the single official qualification on the
   approved qualification host, the independent qualification review, and grant-package preparation.
10. **Does not authorize:**
    - a target-execution host;
    - a grant, a marker, or consumption;
    - any Γ309 evaluation;
    - any retry or resumption;
    - any change to r5 or r6, or to scientific status.
11. **Gates:** Inc ○ · Frz ● · Drl ○ (the drill is development) · Q ● · Gr ○ (preparation only) · Tgt ○.
12. **Dependencies:** P-1 to P-11 above.
13. **Owner wording:**
    - `OD-R2-0(D): AUTHORIZE — "<the packet text verbatim>" — package: r2 at <commit>` (a recommended clarification:
      name the exact r2 commit that will be frozen, so the authorization cannot attach to other bytes);
    - or `OD-R2-0(D): DECLINE`;
    - or leave it OPEN.

### 1.5 OD-R2-1: the r2 production namespace

1. **ID:** OD-R2-1 (R2_PACKET l.103).
2. **Question:** which production names r2 uses.
3. **Why:** r2 must not share r1's forbidden namespace, and the names must be fixed before the freeze.
4. **Options (packet):**
   - **(b)** each campaign its own names (`refs/p5y-k5-cell309-p309-r2/` etc.); r1's namespace stays forbidden
     everywhere; any `refs/p5y-k5-cell309*` ref refuses execution;
   - **(a)** keep r1's names;
   - **(c)** other names named by the owner.
5. **Existing recommendation:** (b), which the packet recommends and which is implemented provisionally
   (R2_AMENDMENTS §A).
6. **Evidence:**
   - (b) is implemented, reviewed (delta review and follow-ups 1–4) and checked statically by QC12 T12;
   - the candidate's validation passed QC12 on `a119e978`.
7. **Consequences:**
   - (b): no code change.
   - (a): lifts r1's "forbidden everywhere" rule, plus code, a delta review and a re-drill.
   - (c): code, a delta review and a re-drill.
8. **Decidable now:** yes.
9. **Authorizes:** the names that will be frozen.
10. **Does not authorize:** creating any ref (no ref exists, and none may be created before a grant).
11. **Gates:** Inc ○ · Frz ● · Drl ○ · Q ● · Gr ● · Tgt ●.
12. **Dependencies:** none. (a) or (c) would add a code delta before the drill.
13. **Owner wording:** `OD-R2-1: (b)` / `OD-R2-1: (a)` / `OD-R2-1: (c) — <names>`.

### 1.6 OD-R2-1b: the four bindings

1. **ID:** OD-R2-1b (R2_PACKET l.125).
2. **Question:** confirm the four bindings (grant path; grant `campaign`; result path; result SCHEMA), as listed in
   R2_PACKET's table, or name others.
3. **Why:** the driver and the grant check read them.
4. **Options:** CONFIRM, or NAME OTHERS.
5. **Existing recommendation (AID_TASK2):** confirm.
6. **Evidence:** they are implemented and reviewed with OD-R2-1 (b).
7. **Consequences:**
   - CONFIRM: no change.
   - NAME OTHERS: as OD-R2-1 (a) or (c) (code, review, re-drill).
8. **Decidable now:** yes.
9. **Authorizes:** the frozen bindings.
10. **Does not authorize:** writing any grant or result.
11. **Gates:** Inc ○ · Frz ● · Drl ○ · Q ● · Gr ● · Tgt ●.
12. **Dependencies:** consistent with OD-R2-1.
13. **Owner wording:** `OD-R2-1b: CONFIRM` / `OD-R2-1b: NAME OTHERS — <bindings>`.

### 1.7 OD-R2-2: marker and pending-result names; the D5 extension

1. **ID:** OD-R2-2 (R2_PACKET l.129).
2. **Question:** ratify for r2 the marker `refs/p5y-k5-cell309-p309-r2/target-consumed` and the pending-result name
   `refs/p5y-k5-cell309-p309-r2/pending-result`. Extend owner D5 (exception 2) to r2's two exactly-once sites,
   `_arm_marker` and `_persist_pending`.
3. **Why:** owner D5 ratified r1's names and sites only.
4. **Options:** RATIFY (names and extension); OTHER NAMES; DECLINE THE EXTENSION.
5. **Existing recommendation (AID_TASK2):** ratify.
6. **Evidence:**
   - the sites' AST pins are unchanged from r1's ratified values (`1ee764b7…`, `13ee3ec3…`), and the A38 backstop pins
     are unchanged;
   - the candidate leaves the driver byte-identical, and the formal review confirmed the exactly-once sites untouched;
   - QC-D5 pins are current on `a119e978`.
7. **Consequences:**
   - RATIFY: no change.
   - OTHER NAMES: code, allowance, review, re-drill.
   - DECLINE THE EXTENSION: r2 cannot pass QC-D5 / QC12 as built.
8. **Decidable now:** yes.
9. **Authorizes:** the names and pins that will be frozen.
10. **Does not authorize:** arming the marker or creating the pending ref (only a granted execute does).
11. **Gates:** Inc ○ · Frz ● · Drl ○ · Q ● · Gr ● · Tgt ●.
12. **Dependencies:** consistent with OD-R2-1.
13. **Owner wording:** `OD-R2-2: RATIFY` / `OD-R2-2: OTHER NAMES — <names>` / `OD-R2-2: DECLINE EXTENSION`.

### 1.8 OD-R2-3: the qualification host's access path, session and windows

1. **ID:** OD-R2-3 (R2_PACKET l.152).
2. **Question:** approve a separate P309 session on the shared worker (message 3) with:
   - its own access path and a P309-only credential;
   - never cell 308's session, user, terminal or credential;
   - no self-hosted runner unless the owner chooses one;
   - following steps 8a → 8b → STOP → 8c → 8d;
   - exclusive windows of about 9 h for the drill and about 9 h for the qualification, each starting with cell 308
     idle.
3. **Why:**
   - the qualification needs a durable host;
   - message 4 item 13 excludes the cloud session;
   - message 3 chose the shared worker.
4. **Options:**
   - APPROVE (as specified in the packet);
   - APPROVE AUDIT ONLY (8a read-only audit and 8b verdict only; the windows to be agreed after 8b; AID_TASK2);
   - DECLINE.
   - Implied by AID_TASK2, not in R2_PACKET: ask whether a **dedicated** host is available. That would amend message 3,
     and needs a reviewed portability change if the host has no IMDS (AF-2).
5. **Existing recommendation (AID_TASK2):** **APPROVE AUDIT ONLY**, and ask about a dedicated host.
6. **Evidence:**
   - R2_HOST_SESSION §1–4;
   - the durability preflight requires IMDS (DURABLE_HOST_PACKET P0.4);
   - measured gate durations;
   - under OD-R2-5 (i) any non-root workload on a shared host can end the single attempt.
7. **Consequences:**
   - APPROVE AUDIT ONLY: the 8a/8b audit may run (read-only); nothing is frozen, qualified or granted in that session.
   - APPROVE: the windows are also accepted now, without the 8a evidence.
   - DECLINE: no qualification host, so r2 cannot proceed.
8. **Decidable now:** yes, for audit access. The windows follow the 8b verdict.
9. **Authorizes:** the P309 session's access path and the read-only audit (and the windows, if APPROVE).
10. **Does not authorize:**
    - host mutations (OD-R2-4);
    - the freeze, the qualification, or a grant;
    - touching cell 308.
11. **Gates:** Inc ○ · Frz ● · Drl ● · Q ● · Gr ○ · Tgt ○.
12. **Dependencies:** none for audit access. The windows depend on 8b and OD-R2-5.
13. **Owner wording:** `OD-R2-3: APPROVE AUDIT ONLY` / `OD-R2-3: APPROVE` / `OD-R2-3: DECLINE`, plus optionally
    `dedicated host available: YES <host> / NO`.

### 1.9 OD-R2-4: host changes that need consent (the owner's and the cell-308 operator's)

1. **ID:** OD-R2-4 (R2_PACKET l.174).
2. **Question:** consent to each host mutation, and to the unit limits:
   1. creating the P309 Unix user;
   2. a P309 volume or quota (≥ 40 GB);
   3. a polkit rule for `p309-r2-*` units;
   4. holding automatic reboots and upgrades per window (**host-wide**);
   5. a private CPython 3.11.15.

   The unit limits are `MemoryMax`, `OOMScoreAdjust`, `CPUWeight`/`IOWeight`, `KillSignal`, `ProtectSystem`, etc.
   Also obtain the cell-308 operator's `foreign_uids` and heavy patterns.
3. **Why:** a durable, isolated run on a host shared with cell 308 (message 3 §6).
4. **Options:** CONSENT or DECLINE for each of mutations 1–5 and for the limit values.
5. **Existing recommendation (AID_TASK2):** consent to 1, 2, 3 and 5; consent to 4 only together with the cell-308
   operator, per agreed window; request the operator's data now.
6. **Evidence:** R2_PACKET l.174–215; R2_HOST_SESSION §3.1; the isolation rule (a world-readable cell-308 checkout
   fails isolation, l.211).
7. **Consequences:**
   - Declining 3: the launcher cannot start its unit.
   - Declining 4: the r1 failure class (a reboot during QC-D5) stays open.
   - Without the uids and patterns: detection relies on command lines and the unattributable rule.
8. **Decidable now:** **no**: it is informed by the 8a audit (world-readability, updater configuration, capacity).
   The request to the cell-308 operator can be made now.
9. **Authorizes:** the 8c bootstrap of the consented items only.
10. **Does not authorize:** anything touching cell 308; the freeze; the qualification.
11. **Gates:** Inc ○ · Frz ● · Drl ● · Q ● · Gr ○ · Tgt ○.
12. **Dependencies:** OD-R2-3 (audit access), the 8a/8b result, the cell-308 operator, and AF-1 if the checkout is
    world-readable.
13. **Owner wording:** `OD-R2-4: M1 CONSENT|DECLINE; M2 …; M3 …; M4 CONSENT WITH OPERATOR <windows> |DECLINE; M5 …;
    LIMITS CONSENT <values> |DECLINE`.

### 1.10 OD-R2-5: interference policy

1. **ID:** OD-R2-5 (R2_PACKET l.219).
2. **Question:** what happens when other heavy work appears during the single attempt.
3. **Why:** message 3 §3 and §8.
4. **Options (packet):**
   - **(i)** a cell-308 or foreign heavy start makes Q-HOST record FAIL, and the attempt ends with no retry. This is
     what the code implements.
   - **(ii)** r2 continues at idle priority. This conflicts with message 3 §3 unless amended, and needs code and a
     re-review.
5. **Existing recommendation (AID_TASK2):** (i), with windows agreed for the whole host, and preferably a dedicated
   host.
6. **Evidence:**
   - the threshold table;
   - detection takes about 80–90 s; termination is immediate;
   - the unattributable rule covers every other non-root uid;
   - the candidate makes the abort durable and classifiable (crash cases C13 and C14).
7. **Consequences:**
   - (i): a third party can consume the attempt, so windows must be agreed for the whole host.
   - (ii): fewer lost attempts, but an owner amendment plus code and review.
8. **Decidable now:** yes, for the policy. The windows follow the 8a audit.
9. **Authorizes:** the run-time policy that will be frozen.
10. **Does not authorize:** starting any run.
11. **Gates:** Inc ○ · Frz ● · Drl ● · Q ● · Gr ○ · Tgt ○.
12. **Dependencies:** (ii) depends on a message-3 amendment.
13. **Owner wording:** `OD-R2-5: (i)` / `OD-R2-5: (ii) — amend message 3 §3 as: <text>`.

### 1.11 OD-R2-6: the target-execution host, as three distinct sub-questions

R2_PACKET l.295 (sub-questions at l.314 and l.328) asks three things. They are listed separately here because they gate different steps, but they are
**sub-questions of the repository's OD-R2-6**, not new decisions.

**OD-R2-6(i): which host executes the target, if ever**
1. **ID:** OD-R2-6(i).
2. **Question:** is the execution host (a) the qualification host, (b) a dedicated host, or (c) the shared worker
   with the reviewed amendment that R2_AMENDMENTS §C requires?
3. **Why:** a qualification-host approval must not imply execution-host approval. Execution is about 31.5 h at 4
   workers, and after the marker any host loss means `EXECUTION_INDETERMINATE`, consuming the evaluation (A22).
4. **Options:** (a); (b); (c) (amendment, code, delta review, re-drill).
5. **Existing recommendation (AID_TASK2):** defer the choice until after a passed qualification; lean to (b).
6. **Evidence:**
   - execute and seal-only are not gated by the launcher, gate or Q-HOST (§C);
   - the runtime pin (interpreter sha256 and glibc must match the freeze host);
   - the 48 QC10 certificates reproduce across hosts (recovery evidence).
7. **Consequences:**
   - (a) on a shared worker: a 31.5 h exclusive window and host-wide reboot holds.
   - (b): an identical interpreter and glibc, and a QC10 re-run there.
   - (c): code, review and re-drill.
8. **Decidable now:** no (Phase E).
9. **Authorizes:** naming an execution host. If recorded before the freeze, it is recorded as
   `governance/OWNER_OD_R2_6_ANSWER.json` (`description`, `host_id_sha256`, `shared_host`; R2_FREEZE_PARAMS l.201–213).
10. **Does not authorize:** the grant; execute; Γ(309).
11. **Gates:** Inc ○ · Frz ○ · Drl ○ · Q ○ · Gr ● · Tgt ●.
12. **Dependencies:** a passed qualification and its review; OD-R2-6(ii).
13. **Owner wording:** `OD-R2-6(i): DEFER` / `(a)` / `(b) <host>` / `(c)`.

**OD-R2-6(ii): repeat QC10's host re-run immediately before any grant?**
1. **ID:** OD-R2-6(ii).
2. **Question (packet, "Also to decide"):** whether QC10's host re-run is repeated immediately before any grant
   (rev. 2c A14).
3. **Why:** it shows the execution host reproduces the decoy certificates.
4. **Options:** REQUIRE, or DO NOT REQUIRE.
5. **Existing recommendation (AID_TASK2):** REQUIRE.
6. **Evidence:**
   - the host re-run is gated by the launcher (`--mode host-rerun`);
   - the candidate's S1 probe also guards it;
   - QC10 certificates were reproducible in four runs on two hosts.
7. **Consequences:** REQUIRE adds one gated run on the named host before any grant.
8. **Decidable now:** yes.
9. **Authorizes:** nothing now. It sets a rule for later.
10. **Does not authorize:** any grant.
11. **Gates:** Gr ● only.
12. **Dependencies:** none.
13. **Owner wording:** `OD-R2-6(ii): REQUIRE` / `DO NOT REQUIRE`.

**OD-R2-6(iii): may the frozen parameter file name an execution host before OD-R2-6(i) is answered?**
1. **ID:** OD-R2-6(iii).
2. **Question (packet):** "whether the frozen field may name any host before OD-R2-6 is answered".
3. **Why:** the freeze binds `proposed_execution_host`.
4. **Options:**
   - NO HOST AT FREEZE: the code default ("no execution host is proposed … the owner names the host in the grant").
   - NAME A HOST AT FREEZE: requires the OD-R2-6(i) answer file before the freeze.
5. **Existing recommendation (AID_TASK2):** freeze with no host proposed.
6. **Evidence:** R2_FREEZE_PARAMS l.201–213.
7. **Consequences:**
   - NO HOST: no file is written, and the grant later names the host.
   - NAME: OD-R2-6(i) must be answered first (Phase E moves earlier).
8. **Decidable now:** yes.
9. **Authorizes:** the content of one frozen field.
10. **Does not authorize:** any host or execution.
11. **Gates:** Frz ● (the field's content).
12. **Dependencies:** NAME depends on OD-R2-6(i).
13. **Owner wording:** `OD-R2-6(iii): NO HOST AT FREEZE` / `NAME A HOST AT FREEZE`.

### 1.12 OD-R2-H: incorporation of the formally reviewed candidate `a119e978` into r2

1. **ID:** OD-R2-H (proposed in AID_TASK2 l.219; named by the formal review as the step that incorporation rests on,
   FORMAL_RECORD C1).
2. **Question:** may the formally reviewed candidate `a119e978` be incorporated into r2?
3. **Why:**
   - r2 as shipped can lose an attempt's evidence to a torn write, and can start a second run over an orphan RUN START
     (R2_FAILURE_MATRIX: R01, R05, R07, R09);
   - its worker-tier drill would refuse at launch (F-DRILL-ORDER);
   - the candidate fixes these, and has passed r2's formal delta follow-up review.
4. **Options:**
   - **H-A** Approve incorporation strictly under formal-review condition C1: fast-forward r2 `101ef2cb` → `a119e978`,
     and make no other change in the same step (no hardening-branch file, tool or test; R18; QC15 A7).
   - **H-B** Do not incorporate yet. r2 stays at `101ef2cb`.
   - AID_TASK2's original options also included freezing r2 as shipped and commissioning a different hardening. In
     effect these are H-B followed by another route; they are listed for completeness and are not recommended.
5. **Existing recommendation:** the formal review found the candidate "acceptable for incorporation into r2" (Q14
   YES) and had no blockers. AID_TASK2 recommended adoption via review. **Recommendation (this packet): H-A.**
6. **Evidence:**
   - FORMAL_REVIEW (14 answers, rulings, conditions C1–C5);
   - the S1–S3 follow-up evidence (crash matrix, unit tests, S1 tests, regression, rehearsal);
   - R2_FAILURE_MATRIX.
7. **Consequences:**
   - H-A: r2's head becomes `a119e978`, a pure fast-forward with no new commit. Then:
     - the follow-up-5 records are filed in a separate governance-only commit (AF-3);
     - SF1 is resolved (C2);
     - the worker-tier drill runs on these bytes (C3).
   - H-B: r2 keeps the known durability and exactly-once gaps, and its 8d drill refuses at the manifest precondition.
     The candidate stays available.
8. **Decidable now:** yes.
9. **Authorizes (H-A):** one act. Fast-forward `origin/claude/p5y-k5-cell309-p309-r2` from `101ef2cb` to `a119e978`,
   performed by or for the owner, and nothing else in that step.
10. **H-A does NOT authorize:**
    - the freeze;
    - the qualification;
    - any grant;
    - Γ(309);
    - any scientific-status change, or r5/r6 change;
    - merging the hardening branch;
    - any other commit in the incorporation step;
    - resolving SF1;
    - filing governance records (AF-3, a separate act).
11. **Gates:** Inc ● · Frz ● (via C1–C3) · Drl ● (C3 needs the incorporated bytes) · Q ● · Gr ○ · Tgt ○.
12. **Dependencies:** none (the formal review is complete). F-DRILL-ORDER is bound to it (§1.13).
13. **Owner wording:** `OD-R2-H: H-A — fast-forward claude/p5y-k5-cell309-p309-r2 from 101ef2cb to a119e978 under
    formal-review condition C1, nothing else in the same step` / `OD-R2-H: H-B`.

### 1.13 F-DRILL-ORDER owner action

1. **ID:** F-DRILL-ORDER (AID_TASK2 l.244, "proposed owner action, not an OD in the packet").
2. **Question:** what action the owner takes on the drill-order defect.
3. **The defect:**
   - r2's `code/p309_topology_drill.py` `make_topology` built the synthetic F′ with the manifest **before** the
     parameter file (manifest → params → placeholder check);
   - so the F′ manifest lacked `freeze/P309_FREEZE.json`;
   - so the runner's `make_freeze_manifest --check` precondition refuses in a worker-tier drill.

   Demonstrated: current order `MANIFEST DIFFERS`, corrected order `MANIFEST IDENTICAL` (F_DRILL_ORDER_REVIEW).
4. **The correction:**
   - in commit `93d55063` (part of `a119e978`), the order is params → manifest → placeholder check, matching r1's real
     freeze;
   - the one consequent scanner re-pin (`make_topology` `9b59c12f…` → `8af1bb78…`) is recorded additively in
     `R2_REPIN_LIST_SUPPLEMENT_5.json`.
5. **Formal review:** Q6 YES ("corrected to match the intended freeze sequence"); `RE-PIN: ACCEPTED`.
6. **Options (repository):** AID_TASK2 offered "fix via review", now done and accepted, or "leave".
   - Under C1 the fix is **inseparable** from the candidate: incorporation is exactly the two reviewed commits. So:
     - "leave" is possible only with H-B, or with a new candidate that omits the fix (a new review);
     - with H-A the fix enters r2.
   - Is it subsumed by OD-R2-H? Technically its adoption follows OD-R2-H (FORMAL_RECORD). But the repository records it
     as a **separate proposed owner action**, so this packet asks for a distinct line of the owner's reply, giving a
     distinct governance record.
7. **Owner options:**
   - **FD-A** accept the reviewed fix: it is adopted by the H-A incorporation, and the action is recorded as closed at
     that incorporation;
   - **FD-B** leave the defect (compatible only with H-B; the 8d drill then refuses at launch).
8. **Recommendation:** FD-A, recorded as a separate line.
9. **Decidable now:** yes, together with OD-R2-H.
10. **Authorizes:** nothing beyond OD-R2-H. It records closure of the defect upon incorporation.
11. **Does not authorize:** running the drill; the freeze.
12. **Gates:** Drl ● (until incorporated, the 8d drill refuses). Frz and Q via the drill.
13. **Dependencies:** OD-R2-H (FD-A requires H-A).
14. **Owner wording:** `F-DRILL-ORDER: FD-A` / `F-DRILL-ORDER: FD-B`.

### 1.14 SF1: the pre-freeze disposition

1. **ID:** SF1 (FORMAL_REVIEW should-fix SF1; condition C2, **before-freeze**; ruled `SF1: NON_BLOCKING` for
   incorporation).
2. **Question:** how SF1 is resolved before the freeze.
3. **Why:**
   - `fs_probe` does not prove the two ledgers are **appendable**;
   - RUN START, r2's pre-existing first ledger append, follows the attempt mkdir;
   - so an unwritable ledger is discovered only after `attempt_1/` exists, which consumes the single attempt
     (fail-closed; no target evaluation).
4. **Options:** exactly the two that the review permits; it "does not choose between the two".
   - **SF1-A** extend the pre-launch probe: both ledgers must exist and open `O_WRONLY|O_APPEND`, with no write (about
     3 lines in `fs_probe`; FORMAL_PACKET §5). This happens under its **own scoped delta review**, then incorporation
     into r2 by the same C1-style fast-forward discipline.
   - **SF1-B** a **recorded host-preparation check**: on the qualification host, the unit's user can append to both
     ledgers. It is recorded before the freeze, without changing the candidate.
5. **Recommendation:** SF1-A, sequenced **before** the 8d drill so that the drill runs on the final bytes. SF1-B is an
   acceptable alternative.
6. **Tradeoffs:**

   | | SF1-A (probe extension) | SF1-B (recorded host check) |
   |---|---|---|
   | code change | yes (about 3 lines; no gate, pin or scientific change expected) | none |
   | review | its own scoped delta review and re-validation (fast checks, S1 tests, crash matrix; light rehearsal) | the check's record is reviewed with the pre-freeze follow-up (gate step 9) |
   | coverage | automatic at **every** launch, incl. `host_rerun` on another host (OD-R2-6(ii)) | binds the qualification to the host state **at the time of the check**. A later permission change, or a different host (QC10 re-run, execution host), needs its own check |
   | timing | before 8d, so no extra drill | at 8c, or immediately before the freeze |
   | residual risk | none for appendability | the state can drift between check and launch |
7. **Decidable now:** yes, the path can be chosen now. It must be **resolved** before the freeze.
8. **Authorizes:**
   - SF1-A: preparing and reviewing a scoped delta. It does not incorporate it; that needs its own owner act (§2,
     C-phase).
   - SF1-B: a host check during 8c or before the freeze.
9. **Does not authorize:** the freeze or the qualification.
10. **Gates:** Inc ○ (NON_BLOCKING) · Frz ● · Drl ○ (sequencing only) · Q ● · Gr ○ · Tgt ○.
11. **Dependencies:**
    - SF1-A: after H-A (it applies on top of the incorporated r2), before 8d;
    - SF1-B: after OD-R2-3/4 (host access).
12. **Owner wording:** `SF1: SF1-A` / `SF1: SF1-B`.

---

## 2. Additional findings: other owner decisions or acts the repository shows as gating

These are **not** in the original list. They are reported as findings, and the owner may answer them in the form's
"additional" section.

| id | finding | source | phase | gates |
|---|---|---|---|---|
| AF-1 | **Message 3 §6 amendment, conditional.** If the 8a audit finds the cell-308 checkout world-readable, the isolation check fails. Proceeding then needs the owner to amend message 3 §6, with the cell-308 operator's consent | R2_PACKET l.211 | C (only if 8a finds it) | Drl, Frz, Q |
| AF-2 | **Host-portability change, conditional.** If the qualification host has no cloud metadata service (IMDS), `durability_preflight` fails closed. A reviewed portability change, or an IMDS host, is needed | DURABLE_HOST_PACKET P0.4 | C (only if the host lacks IMDS) | Drl, Frz, Q |
| AF-3 | **Governance-only filing in r2 after incorporation.** Two items: the follow-up-5 brief, review (+ sha256, execution ledger) and record, copied into r2's `governance/` as `BRIEF_/REVIEW_R2_DELTA_FOLLOWUP_5.*` in a **separate** commit after the fast-forward (C1 forbids it in the same step); and the owner's verbatim answers to this packet, recorded in an immutable verbatim file as r2's owner messages are | FORMAL_RECORD l.14; MSG_1_3/MSG_4 conventions | C | Frz (P-11), Q |
| AF-4 | **The grant decision** (`READY_FOR_OWNER_GRANT_DECISION`): after a passed qualification and its independent review, the owner decides whether to grant the single target execution | MSG_1_3 l.342; R2_HOST_SESSION §7 | E | Gr, Tgt |
| AF-5 | **An r3 decision, conditional.** If r2's single qualification fails or is interrupted, r2 ends (P23), and any r3 is a new owner decision | R2_PACKET carry-over row "QUALIFICATION FAILURE" | E (only on failure) | everything after |

**Prerequisites that are not owner decisions** (listed so that none is mistaken for one):
- the 8a audit and 8b verdict (`HOST_SUITABLE`);
- the cell-308 operator's data (P-6);
- the worker-tier drill (C3);
- the pre-freeze follow-up review (gate step 9);
- SF1-A's scoped review, if chosen.

## 3. Phases (each decision appears in exactly one)

| phase | meaning | decisions |
|---|---|---|
| **A** | can be decided now, before incorporation, and needs no later evidence | OD-R2-0(A), OD-R2-0(B), OD-R2-0(C), OD-R2-1, OD-R2-1b, OD-R2-2, OD-R2-3 (audit access), OD-R2-5, OD-R2-6(ii), OD-R2-6(iii), SF1 (choice of path) |
| **B** | authorizes incorporation | OD-R2-H, F-DRILL-ORDER |
| **C** | after incorporation (or after the 8a audit), before the freeze | OD-R2-4; AF-1 (conditional); AF-2 (conditional); AF-3; the incorporation of SF1-A's reviewed delta, if SF1-A |
| **D** | authorizes the freeze and the single official qualification | OD-R2-0(D) |
| **E** | after the qualification, or when new evidence exists | OD-R2-6(i); AF-4 (grant); AF-5 (r3, only on failure) |

Notes:
- **SF1** is placed in A because its *path* can be chosen now. Its *resolution* is a C-phase prerequisite of D.
- **OD-R2-3** is placed in A because audit access can be approved now. Its windows are agreed in C, after 8b.

The ordered dependency table and the DAG are in `OWNER_DECISION_DEPENDENCY_TABLE.md`.

## 4. Owner-facing recommendation table (recommendations only)

| ID | Decide now? | Recommended owner answer (recommendation) | Why | What it authorizes | What still remains |
|---|---|---|---|---|---|
| OD-R2-0(A) | yes | CONFIRM | the records are verbatim and hashed, and A3 keeps them immutable | settles the record | — |
| OD-R2-0(B) | yes | CONFIRM ALL ROWS | the rows reflect messages 1–4 and the inherited rulings | the inherited rules bind r2 | rows routed to OD-R2-2 / OD-R2-6 |
| OD-R2-0(C) | yes | ACKNOWLEDGE WITH ADDITIONS (§1.3 item 6) | complete record of departures | proceeding on that record | — |
| OD-R2-0(D) | **no** | **leave OPEN** (do not AUTHORIZE yet) | P-1 to P-11 are outstanding | — | all prerequisites; then AUTHORIZE naming the exact r2 commit |
| OD-R2-1 | yes | (b) | implemented and reviewed; keeps r1 forbidden | the frozen names | — |
| OD-R2-1b | yes | CONFIRM | implemented and reviewed | the frozen bindings | — |
| OD-R2-2 | yes | RATIFY | pins unchanged; QC-D5 current | the frozen marker / pending names and D5 sites | — |
| OD-R2-3 | yes (access) | APPROVE AUDIT ONLY (+ ask about a dedicated host) | the 8a evidence is needed before windows and consents | the read-only 8a/8b audit | windows after 8b |
| OD-R2-4 | no (after 8a) | after 8a: M1, M2, M3, M5 CONSENT; M4 only with the cell-308 operator per window; request the operator's uids and patterns now | host-wide effect of M4; isolation | the 8c bootstrap of consented items | the operator's data and consent |
| OD-R2-5 | yes | (i) | matches message 3 as written; no amendment or code | the frozen run-time policy | whole-host window agreement |
| OD-R2-6(i) | no | DEFER (lean (b), dedicated) | 31.5 h single shot; execution ungated on a shared host | — | after a passed qualification |
| OD-R2-6(ii) | yes | REQUIRE | reproducibility on the named host before any grant | a rule for later | — |
| OD-R2-6(iii) | yes | NO HOST AT FREEZE | the code default; avoids implying an execution host | the frozen field's content | — |
| OD-R2-H | yes | H-A | formal review: acceptable, no blockers; fixes reproduced defects | one fast-forward `101ef2cb` → `a119e978`, nothing else | AF-3 filing; SF1; C3 drill |
| F-DRILL-ORDER | yes | FD-A | reviewed and accepted; inseparable from the candidate | closure upon incorporation | — |
| SF1 | yes (path) | SF1-A, before the 8d drill | automatic at every launch and on every host | preparing and reviewing a scoped delta | its review and incorporation |

## 5. How the answers will be recorded (so that they are unambiguous)

1. The owner fills in `OWNER_REPLY_FORM.md` and sends it as a message.
2. With the owner's authorization (AF-3), the message is recorded **verbatim** in r2's `governance/` as a new immutable
   file, with its sha256. This follows the convention of `OWNER_INSTRUCTIONS_R2_VERBATIM.md` and
   `OWNER_INSTRUCTIONS_R2_MSG4_VERBATIM.md`. It is never appended to an existing immutable file.
3. Only an OD-R2-6(i) answer naming a host, given before the freeze, is also written as
   `governance/OWNER_OD_R2_6_ANSWER.json`, the only answer file the code reads (`description`, `host_id_sha256`,
   `shared_host`). Under the recommended OD-R2-6(iii) = NO HOST AT FREEZE, it is not written.
4. Each answered item's classification changes from OPEN only through that record. Nothing is inferred from this packet
   or from any recommendation.

## 6. What this packet does not do

- It does not answer, record, or simulate any answer into the repository.
- It does not incorporate, fast-forward or merge anything.
- It does not freeze, qualify or grant.
- It does not evaluate Γ(309) or any target quantity.
- It does not touch r5 or r6, or Cell 309's status.

The dry simulation of the recommended answers is in `OWNER_DECISION_SIMULATION.md`, and changes nothing.

## 7. Evidence map

`OWNER_DECISION_EVIDENCE_MAP.json` gives, for every source, the commit, path, sha256, git blob, last commit touching it
and anchor line numbers. For every decision it gives its sources, phase, repository status, options, recommendation and
gates.

## 8. Integrity (checked independently before this packet was finalized)

The results are in `OWNER_DECISION_SIMULATION.md` §5 and `integrity/`.
