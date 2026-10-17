# S12 incident-independence (result-chasing risk) review — Cell-308 MB-S new-host route, Cloud r1

## 1. Header

- Reviewer: reviewerS12 (fresh agent, brief S12)
- Date: 2026-10-16
- Pinned commit: `6d5f9a63816ad9294afc85b17df0e49e0dec8bf3` (detached worktree `S12/tree_6d5f9a63`; `git rev-parse HEAD`
  confirmed; branch `codex/cell308-claude-r5-integration`, draft PR flaggielover/ReBaseGuard#3)
- Brief: `ledger/briefs/S12_RISK_REVIEW_CLOUD_R1.txt`, read in the shared checkout as instructed.
- Abbreviations. NS = `level4/closure_proofs/p5y_k5_cell308_research/`; G = `NS/governance/new_host_route_cloud_r1/`.
  - amd = G/`PROPOSED_ROUTE_AMENDMENT_CLOUD_R1_A1_R5.md` (sha256 prefix `d0963b11`); amdE1 = its `_ERRATUM_E1.md` (`b4728654`)
  - obr5 = G/`OWNER_DECISION_BRIEF_CLOUD_R1_R5.md`; pkt = G/`FORMAL_ROUTE_READINESS_PACKET_20261016.md`
  - dpk = G/`CONSOLIDATED_DSTAR_PACKAGE_R2_20261016.md`
  - hep / hepE1 = G/`HOST_EVIDENCE_PLAN_H1_H8_20261016.md` and its erratum
  - lsp / lspE1 = G/`LDET_SPECIFICATION_PACKET_20261016.md` and its erratum
  - hap2 = G/`HOST_ATTESTATION_ACCEPTANCE_PROCEDURE_R2_20261016.md`
  - fr1d = G/`FR1_DISPOSITION_20261016.md`; s12d = G/`S12_RISK_REVIEW_BRIEF_DRAFT_20261016.md`
  - prep = G/`ROUTE_PREPARATION.md`; od2 = G/`USER_AUTHORIZATION_20261016_OD2.md`
  - FR1 = NS/`reviews/REVIEW_FORMAL_ROUTE_CLOUD_R1_FR1.md`
  - gov = NS/`governance/SUCCESSOR_GOVERNANCE_308.md`; gA1 = its addendum A1; bR2 = NS/`governance/USER_DECISION_BRIEF_308_SUCCESSOR_R2.md`
  - reg = NS/`governance/SUCCESSOR_CONDITIONS_REGISTER_308.md`
  - rA1 = NS/`registry/SUCCESSOR_ROUTE_AUDIT_308_ADDENDUM_A1.md`; rE1 / rE2 = its errata
  - Line numbers refer to the pinned tree.

## 2. Eligibility and exposure

**Phase-1 statement** (`scratch/ELIGIBILITY_AND_EXPOSURE_S12.md`; per the coordinator it was committed at `45a52623`,
which is after the pinned commit, so I have not verified that commit). In summary:
- role reviewerS12;
- no prior reading of E1″ material, of the excluded files, or of MB r1 target-run observations; a fresh context;
- no earlier role in this project;
- the restrictions accepted.

**Actual contact during the review:**
- **Opened, pinned tree.** In full:
  - amd and amdE1, obr5, pkt, dpk;
  - hep with hepE1, lsp with lspE1, hap2;
  - fr1d, s12d, prep, od2, FR1.
  - The accepted sources gA1, rA1, rE1, rE2 and reg.

  In part:
  - gov lines 85–131;
  - bR2 lines 1–160, 195–450;
  - `CONSTANTS_RATIFICATION_MBS308.md` and `…_ADDENDUM_A1_ERRATUM_E1.md` through grep hits only.

  Also the last 6 lines of `ledger/TARGET_INTEGRITY_LEDGER.jsonl`, each cut to 600 characters.
- **Grep hits seen** from files outside the materials list but inside G: the amendment drafts r2–r4, hap r1, and the
  r70 disposition supplement. The hits were trigger-label and phrase searches only.
- **Accidental contact (disclosed).** One recursive search, `grep -rn "Complete the fresh S12" governance reviews
  ledger/briefs`, ran over all of NS/`reviews/`.
  - That directory includes the excluded files `REVIEW_EXECUTION_INTERRUPTION*` and
    `INCIDENT_INDEPENDENCE_REVIEW_MBS308.md`, so their contents were scanned by grep for that one literal string.
  - No line from any excluded file matched, and nothing from them was printed.
  - The only information gained is that they do not contain that sentence. I made no other contact with them.
- **Name-level contact.** A listing of NS/`ledger/` showed file names, including `COORDINATOR_EXPOSURE_DISCLOSURE.md`
  and owner-ruling files (`USER_RULING_MBS308_OWNER_DECISIONS.*`). I did not open, grep or hash any of them.
- **Git.**
  - The commands were `git rev-parse HEAD` and `git status`, with HOME and GNUPGHOME under `S12/home` and `S12/gnupg`.
  - The worktree's git directory is `/home/user/ReBaseGuard/.git/worktrees/tree_6d5f9a63`, so those commands used the
    shared repository's object store.
  - I made no clone and ran no `ls-remote`. No other git or Python process ran.
- **sha256sum** of eight permitted files (prefixes above). No excluded file was hashed.
- **Not run:** no scientific, candidate, decoy, qualification, L-DET or test code.
- **Harness side effect.** One long tool output (the second half of FR1) was saved by the harness to a file under
  `/root/.claude/projects/…/tool-results/`. That was not my action, and it holds FR1 text only.
- **Not seen:** no MB r1 postexec or target-run record, no qualification-record content, and no Cell-309 content.
- **Not verifiable by me:** E1″ holder status of anyone, including me against the holder list in the excluded
  disclosure file (FR1 F6 says the same of itself).

## 3. Rating

S12_RATING: HIGH

This rating is advice to the owner. It accepts no amendment, host or decision. It stands only if the owner adopts this
reviewer's appointment and the rating. It is **conditional**:
- HIGH holds only if the BLOCKING findings S1 and S2 are corrected, and the mitigations of §5 are adopted, before OD-3.
- If the route proceeds without them, my rating is VERY-HIGH, and continuation is not acceptable from the
  result-chasing standpoint.

## 4. Questions

### Q1. Rating

**Floor.** I checked both governing quotations against the accepted sources:
- **S12:** gA1:145–147. Verbatim, except that the source uses an en dash in "MEDIUM–HIGH" and bold emphasis.
- **MBS-5(b):** bR2:146–147 ("any evaluation of cell 308 after the MB-S marker, of any route, starts at a risk rating
  not lower than HIGH"). The same in substance at rE2:18.

**HIGH is the correct floor, but not for the reasons the texts give.**
1. **MBS-5(b) does not literally apply to this route.** It binds evaluations "after the MB-S marker". No MB-S marker
   exists: prep:13 says "No old marker or target was created", and MB-S r1 stopped at NOT_DERIVED (obr5:16). MBS-5(b)
   therefore binds evaluations *after* this route's own marker, not this route itself (S10).
2. **T1's "fires by construction" (amdE1:87–90) is not established.**
   - T1's condition, as amd:243–244 quotes it, is "Any of N1–N4 fails at qualification or at any resume". The
     parenthetical "(the science is then 'changed' under S4)" states a consequence.
   - amdE1 E1.6 reads the consequence as the condition, which is affirming the consequent.
   - N1–N4 are in the excluded incident review and are UNVERIFIED by me. amd:353 says N3 includes MBR1_REPRO's exact
     reproduction. If so, an L-DET match plus a qualification MBR1_REPRO match could leave N3 unfailed. In that case T1
     fires by construction only if some N_i is "same platform" itself, which I cannot see.
   - So "T1 fires by construction on a platform change" is UNVERIFIED (S6).
3. **The floor holds independently of T1**, on accepted text:
   - rA1:22–24: "The value of MB-S equals the value the lost MB r1 run would have produced only on the same platform …
     Off that platform the S4 'changed' branch applies".
   - gA1:15–17: the decisive argument is the reason "No selection on an outcome is possible".
   - bR2:208–209 (a reader-checked brief citing reviewINC2 `b7e62dec`): the MEDIUM–HIGH rating is "conditional on
     byte-identical science on the pinned platform and on the T6 conditions M1–M6; otherwise HIGH".
   - prep:21 (preparation class, not accepted): "Existing escalation rules identify changed-platform conditions as
     HIGH".

   The premise that carried the accepted MEDIUM–HIGH, the decisive argument, is lost here by construction, so the
   MEDIUM–HIGH basis does not exist on this route.

**A rating below HIGH** is not possible on any written finding I can make. It would need all three of:
- a finding that the decisive argument survives off-platform, which rA1:22–24 forbids;
- an accepted reading of D-RC2-SCOPE that restores it, which amdE1:39–41 expressly rules out;
- verification that T1 has not fired.

I find the opposite on the first two.

**Above HIGH.** The accepted escalation vocabulary ends at HIGH (rE2:17–18). Several features of this route are new
compared with every earlier rated state:
- the value becomes a platform-dependent draw;
- the host is a new discretionary choice, made by a decider whom rA1:98–100 places with E1″ in view;
- most host gates become owner statements;
- the cross-host exactly-once mechanism is undefined;
- every reviewer is an agent in the coordinator's environment.

Taken together, and with no mitigation, they warrant VERY-HIGH. With the §5 mitigations, the one channel that turns
these into selection on the *value* (a further draw after an outcome) is closed ex ante. The residual channels are then
completion-probability levers bounded by mechanical rules. On that basis I rate HIGH, conditional.

### Q2. Premises of the accepted Q4 that change

Q4's premises are "one sealed evaluation; only R-MB on 308" (gA1:145–147). Q4 relied on "There is exactly one sealed
evaluation, and NOT_CLOSED and INDETERMINATE are pre-declared outcomes" (gA1:41–43).

| premise item | change on this route | evidence |
|---|---|---|
| platform | Determinism no longer ties the value to the lost run. The value is "a second, different draw". For the first time in this lineage, selection on the value becomes structurally possible: across platforms, after an outcome. The "different platform" fact also gives a ready-made argument for yet another draw | rA1:22–24; amd:246–248; amdE1:39–41; gA1:15–17 |
| host | A new owner-chosen machine. The choice of host (CPU speed, cores, memory) is a new discretionary decision. Under fixed caps it moves the completion probability. It is taken by a decider whose go / no-go decisions are taken "with the lost run's runtime-only observations in view" (rA1:98–100, risk (e)), while gov S3 and gA1 S13 exclude those observations from "any successor decision" and from "every successor design and caps decision" | gov:101–103; gA1:148–153; rA1:98–100; obr5:37–47 |
| caps (D-CAPS-CPU / MBS-8) | (i) keeps macOS-sized caps on a different CPU (thin Q12 margins, rA1:86). (ii) re-derives new values. The texts sequence the choice **after** L-DET and ask the owner to see "Q12's result under option (i) on that host" first: a look-then-choose on a qualification outcome. bR2 itself notes that recording MBS-8 before any official decoy run avoids choosing "with its resulting values in view" | dpk:46; pkt:179–180; FR1:410; bR2:70–72 |
| L-DET | An added non-target pre-gate with one attempt, no repeat, and stop on mismatch. It consumes nothing of 308. It does produce new-host decoy runtimes before MBS-8 under the current ordering, and its outcome feeds owner continuation rulings (amd:228–229) | amd:205–232; amdE1:55–63; lspE1:25–27 |
| second consumption | The count becomes 2 at this route's marker (bR2:335, 366). "Exactly one sealed evaluation" is false for cell 308, and only S1 can lift mitigation 5. Unchanged from MB-S, but now combined with a new draw | gA1:41–47, 120–121; amd:286–287 |
| members (MBS-7) | The route presupposes (i). (ii) would change the science. The owner records MBS-7 before OD-3 (amdE1:14–17). Still open | reg:34; amdE1:14–17 |
| owner-statement substitutions | Measured gates become statements by the party that chose to continue. The listed ones are LPM, AC power, pause, S15 store state, H1, H3 image, H6 and H7 (dpk:54–62). Unlisted ones are in S7 of §6. The premise that a frozen host contract enforces host health "separate from scientific validity" (gov S6) is weakened to trust in the owner | dpk:54–62; hap2:145–162; FR1 G20 |
| only R-MB on 308 | Unchanged (D10), provided MBS-7 (i) | gA1:49–57 |

### Q3. Mitigations required before any freeze

| mitigation | present in the texts | sufficient? |
|---|---|---|
| L-DET exact match | (a)∧(b), strict `fs` grammar, two controls, structural floor (lspE1:15–27); a pre-gate plus MBR1_REPRO at qualification (amdE1:55–63) | Sufficient **for its purpose** (non-target reproduction). Not a risk reduction for the value (Q4) |
| no host shopping | Only after an L-DET mismatch (amd:228–229) | **Insufficient.** It does not cover: candidates inventoried and dropped before L-DET; a designated-series or qualification failure on the named host; and above all a further platform **after an outcome** (S1, S12) |
| no repeat | D-LDET-REPEAT "no repeat"; a later same-platform ruling is post-result and needs fresh S12 and formal review (dpk:33) | Sufficient for L-DET |
| E8 | No L-DET record next to a cell-308 quantity (amd:230) | Should be extended to new-host decoy and L-DET runtimes versus any MB r1 runtime or cell-308 projection, in every decision document (S18) |
| caps from decoys only | gA1:153; amd:231–232 (L-DET runtimes excluded) | **Insufficient**: the source is decoys, but the *choice* is sequenced after new-host results (S2) |
| exactly-once marker | gov S7; S15 for MB r1's marker | **Insufficient across hosts.** The new marker would live only on the new host, and the route "never pushes formal refs" (dpk:49). Nothing lets a later campaign anywhere assert it (S4). MBS-6 finality is still open and sequenced after L-DET (S1, S2) |
| platform window from the L-DET build | amdE1:67–70; hepE1:43–44 | Necessary. Unbounded in length; there is no pre-registered rule for a forced update (S13) |
| anchor check | hap2:110–143 | Good before the marker. After the marker, "An unreachable owner is a wait, not a pass" (hap2:142), combined with operator-launched resumes, reopens L5 selective non-completion without firing T4 (S5) |

**Missing:** cross-platform and cross-outcome finality (S1); MBS-6 and MBS-8 before OD-3 (S2); OD-1 hygiene for E1″
(S3); a cross-host marker record (S4); a post-marker non-action rule (S5); a complete SUBST list with cross-checks (S7);
an M1-style non-holder trace of the route's new constants (S8); D-* decided before any named-host reading (S11).

### Q4. Does an L-DET exact match change the rating?

No. Under amdE1:39–41, discharging RC2 "establishes reproduction of MB r1's non-target records only. It does not
restore the decisive argument … its value is a second, different draw".

The match covers four records on decoys 297 and 316. It gives no bound on whether the cell-308 computation's float
proposals, which use libm (rA1:23), take the same path on the new platform. The certified outcome may therefore still
differ. MB r1 itself recorded "only its Python version" (bR2:433), so even "same platform" was never fully pinned for
the reference run.

A match is a necessary gate, and a mismatch is a correct stop. Neither lowers the rating. **A mismatch must not be
read as information that steers a later host choice** without the fresh review amd:228–229 requires. The rating stays
not lower than HIGH either way.

### Q5. Triggers

From the texts I may read:

| trigger | text available | on this route |
|---|---|---|
| T1 | "Any of N1–N4 fails at qualification or at any resume" (amd:243–244, quoted from the excluded review) | **UNVERIFIED whether it fires by construction** (Q1 item 2; S6). It fires later on any MBR1_REPRO mismatch at qualification, any pin mismatch at a resume, or any science change (MBS-7 (ii)). Treat it as fired by default; the HIGH floor does not depend on it |
| T2 | not stated in any permitted text | UNVERIFIED |
| T3 | "A breach fires T3": in-run observation, MBS-3 / L6 (rE2:13–14) | Can fire later. V-A raises the risk (agent sessions on the host; amdE1:94–99) |
| T4 | any stop outside the frozen rules (MBS-5(a); rE2:10–12) | Can fire later. The post-marker anchor "wait" lets a lapse happen **inside** the rules, so T4 would *not* fire (S5) |
| T5 | not stated in any permitted text | UNVERIFIED |
| T6 | "T6_FIRED_MITIGATED", MEDIUM–HIGH "only under M1–M6, otherwise HIGH" (bR2:45); M1 itemised provenance trace, M4 exposed parties out (bR2:4, 29) | Already fired for MB-S. Its mitigation does not obviously cover the route's **new constants**, drafted by a self-declared non-holder coordinator (S8). Whether M1–M6 transfer is UNVERIFIED (T6 text unavailable; bR2:372) |

The governance S9 quarantine also uses labels "T1–T4" (gov:123). That is a different trigger set and must not be
conflated (S17).

### Q6. What the S1 brief must state about the risk

At minimum:
1. The S12 rating (HIGH, conditional), its advisory standing and adoption status, and the conditions on which it holds.
2. The decisive argument is **lost**. The value is a second, different draw. An L-DET or MBR1_REPRO match shows
   non-target reproduction only (amdE1:39–41).
3. The count becomes 2 at this marker. MB r1 stays INDETERMINATE and "not scientifically negative". MB-S r1 stopped
   pre-marker at NOT_DERIVED.
4. An explicit treatment of gA1:122 / bR2:310 ("a new governance decision, not a rerun on host grounds"). The route's
   stated motivation is a host gate failure (prep:19), so the brief must explain why it is not a rerun or
   reinterpretation on host grounds (S14).
5. The finality rule of S1 below, verbatim. Then MBS-6, MBS-7 and MBS-8 as recorded, with their recording dates
   relative to OD-1, OD-3 and every new-host run.
6. Every host candidate inventoried, every L-DET attempt (start, end, outcome, pins), and every gate or qualification
   failure on this route (amd:221–223).
7. The complete SUBST list (S7). Every rule for which prep:19 is set aside (dpk:64–65). Every new constant, with its
   provenance trace (S8).
8. Route risk (e) for this route. OD-1, MBS-8 and S1 are taken by a decider who may hold E1″ (names, never values).
   The OD-1 record's statement under S3.
9. The reviewers' standing: agents in the coordinator's environment, not human, freshness self-declared (od2:25–27).
10. No outcome expectation, no E1″ figure, and no L-DET or new-host runtime next to a cell-308 quantity (MBS-10, S13,
    E8).
11. The trigger table (Q5), with T1–T6 quoted verbatim by an eligible reader of the incident review.

### Q7. Continuation versus closure

**V-C (close; MB-S r1 at NOT_DERIVED) carries the lower result-chasing risk.**
- It adds no consumption, no draw and no new decision point.
- No Γ308 exists, so closing cannot be a selection on a value.
- Cell 308 stays OPEN, and any later route starts its own governance (MBS-5(b) would not even be triggered, since no
  MB-S marker exists).

**Continuation** (one owner-named persistent machine; V-B, or V-A under amdE1:94–99) adds a second consumption *and*
a platform-dependent draw. Its risk is acceptable at HIGH only if **all** of these hold before OD-3:
1. S1's finality rule is adopted: one outcome on this route, of any class, ends route MB on 308 on every platform.
2. MBS-6 (i), MBS-7 (i) and MBS-8 are recorded before OD-3, with no new-host runtime in view (S2).
3. The OD-1 record meets S3, and architecture is fixed in it.
4. The cross-host marker record of S4 is in place, and so is the post-marker non-action rule of S5.
5. The SUBST list is completed with cross-checks (S7). The new constants are traced by a non-holder (S8). All D-* items
   are decided before any named-host reading (S11).
6. Every V-A runner is stopped and disabled for the window (S16). V-B is preferred.

If any one of these is missing, I advise V-C.

### Q8. Process

**Yes, the appointment limits the weight of the rating.**
1. The coordinator appointed me in the coordinator's own session. I share its environment and model family. The
   coordinator wrote the brief that frames my questions, including the list of mitigations to consider. My freshness
   and non-holder status are self-declared and cannot be checked by any reviewer barred from the disclosure file.
2. The brief (lines 3–4) and fr1d:56, 92 quote the owner as saying "Complete the fresh S12 review using an eligible
   reviewer". **That sentence is not in the committed verbatim record** (od2:6–16, which has "Select fresh, eligible
   independent reviewers" and a summarised work list). The delegation relied on for S12 is therefore UNVERIFIED in the
   repository (S9).
3. FR1 condition 14 (FR1:490–491) says "the owner names the S12 reviewer". Condition 1, the owner's adoption, was to
   be met **before** S12 was commissioned (FR1:462–463). fr1d:88–93 records it as met only as to text.
4. The corrected texts I reviewed (amdE1, dpk, hepE1, lspE1, hap2) have not had their fresh bounded check (FR2,
   fr1d:95–102).

**For full standing the owner would need to:**
- record, in the owner's own record, adoption of this appointment, naming the brief's sha256 and the agent or session
  id (the hap2:49–52 identity definition);
- obtain this review's sha256 directly from the reviewer's reply channel and bind it there;
- confirm or withdraw the quoted OD-2 sentence;
- adopt FR1's standing first;
- treat this rating as provisional until FR2 completes, and re-commission S12 if FR2 changes anything material.

For weight beyond advice, the owner would also commission a second rating from a reviewer outside the coordinator's
environment (a human, or an agent in a separate owner-started context).

## 5. Required mitigations (checkable)

1. **Cross-outcome finality (S1).** The accepted amendment and the S1 ruling state verbatim that after this route's
   marker, any outcome (CLOSED, NOT_CLOSED or any INDETERMINATE class) ends route MB on cell 308 on every platform and
   host. The loss of the decisive argument ("a different draw") is never a ground for a further route. Any other route
   on 308 starts at not lower than HIGH (MBS-5(b)) and discloses this outcome.
2. **Pre-OD-3 decisions (S2).**
   - The owner records MBS-6 (i), MBS-7 (i) and the MBS-8 option before OD-3 and before the L-DET interpreter build.
   - The record states that no new-host runtime, inventory timing or Q12 result existed when it was made.
   - "Q12's result under option (i) on that host" is deleted as an input to the MBS-8 choice (dpk:46).
3. **OD-1 hygiene (S3).**
   - The OD-1 record names one machine and its architecture.
   - It cites only the hepE1 §1.1–1.2 criteria.
   - It states in writing that no MB r1 target-run observation informed the choice.
   - Any property beyond those criteria has a written target-free reason, checked by a non-holder.
4. **Cross-host marker (S4).**
   - When this route's marker is written, its ref name and id (value-free) are recorded in the owner's external record
     and mirrored in the canonical ledger.
   - Every later cell-308 preflight on any host asserts both markers as named exceptions (an S15 analogue).
5. **Post-marker non-action (S5).**
   - The post-marker anchor checks are performed or delegated in advance to a named checker.
   - H7's response time is a binding number.
   - Any resume, recover or deadline lapse caused by owner or operator non-action is an INCIDENT that fires T4.
6. **Floor basis (S6).**
   - The floor text cites rA1:22–24, bR2:208–209 and rE2:17–18, and holds whether or not T1 fires.
   - An eligible reader of the incident review records N1–N4 and T1–T6 verbatim, and whether T1 fires by construction.
7. **SUBST completeness (S7).**
   - All owner-statement gates are listed: H2, H4, H5, the H8 substitute, the D-S15 (b) listing and the anchor, in
     addition to dpk:54–62.
   - Each names its measured cross-check, or "none".
   - H8 and the S15 assertion may not rest on a statement alone.
8. **New-constant provenance (S8).** A non-holder M1-style trace covers every number or rule the route introduces. It
   is recorded before the owner decides the D-* items. Whether T6's M1–M6 transfer is ruled on.
9. **D-* timing (S11).**
   - All 21 D-* items are decided before the Phase-1 inventory of the named machine.
   - A later change needs a fresh S12 and a formal review with the readings in view.
10. **Host-attempt disclosure (S12).**
    - Every machine inventoried is recorded.
    - A designated-series, gate or qualification failure on the named host stops the route unless a new owner ruling
      is made with a fresh S12 and a formal review.
11. **Window bound (S13).** A maximum interval from the L-DET interpreter build to the marker is pre-registered. Its
    lapse, or a forced update, stops the route.
12. **E8 extended (S18).**
13. **V-A (S16).** No runner is installed, or it is stopped and disabled, from the L-DET build to the seal, with a
    measured process list. Its updates count under H3.
14. **Standing (S9).** The owner completes the steps of Q8.

## 6. Findings

| id | severity | location | finding | required correction |
|---|---|---|---|---|
| S1 | BLOCKING | amd:43–46, 228–229, 246–248; amdE1:39–41; bR2:134–135; reg:33; gov:118–120 | Off-platform the value is "a second, different draw". Nothing in the texts forecloses a further platform or host after an **outcome** on this route. "No host shopping" covers only an L-DET mismatch. MBS-6 (i) is open, is phrased for an INDETERMINATE only, and S7 keeps "a further successor" governable. A NOT_CLOSED or INDETERMINATE here could be followed by another draw elsewhere, with the platform difference itself as the rationale. That is selection on the value | Adopt §5 item 1 in the accepted amendment, the MBS-6 record and the S1 ruling, before OD-3 |
| S2 | BLOCKING | pkt:179–180; dpk:46 (row 17), dpk:79; FR1:410; bR2:70–72 | MBS-6 and MBS-8 are sequenced "Only after a match". D-CAPS-CPU makes "Q12's result under option (i) on that host" an input to the owner's MBS-8 choice: look at whether fixed caps pass, then pick the option. bR2 itself notes that recording MBS-8 before official decoys avoids choosing with the values in view. With E1″ held by the decider (rA1:98–100), this choice can be informed by the target run's runtime | §5 item 2 |
| S3 | MAJOR | obr5:37–47; pkt:187; rA1:98–100; gov:101–103; gA1:153 | OD-1 is both a go / no-go and a design decision (host class, speed, cores, memory). No text requires the OD-1 record to disclose the decider's E1″ status, to limit itself to pre-registered target-free criteria, or to state that no target-run observation informed it. Under MBS-8 (i), host speed is a direct lever on completion probability | §5 item 3. Prefer MBS-8 (ii), whose caps scale with the host, or record MBS-8 before OD-1 |
| S4 | MAJOR | gov:118–120; gA1:157–162; dpk:49 (row 20, "The route never pushes formal refs") | Exactly-once is enforced per store. This route's marker would exist only on the new host, and nothing records it where a later campaign on another host could assert it. Cross-host exactly-once then rests on recollection or owner statements | §5 item 4 |
| S5 | MAJOR | hap2:120–143 (esp. 142); hep:46; rE2:10–12 | After the marker, each resume or recover needs an owner anchor check and an operator launch. "An unreachable owner is a wait, not a pass." A lapse of a resume or of the 7-day deadline through owner non-action is then *inside* the frozen rules, so MBS-5(a) / T4 does not fire. This reopens L5 (selective non-completion at no cost) | §5 item 5 |
| S6 | MAJOR | amdE1:84–90; amd:243–244, 353; s12 brief Q1 | E1.6 says T1's condition "holds by construction". T1's condition is "Any of N1–N4 fails at qualification or at any resume", and the quoted parenthetical is a consequence. N1–N4 are UNVERIFIED (excluded file). If N3 is MBR1_REPRO, a double match may leave T1 unfired. E1.6's own escape clause ("No rating below HIGH … without a written S12 finding that T1 has not fired") then invites a sub-HIGH rating on a literal reading. The floor rests on the wrong text | §5 item 6. Restate E1.6 so the floor rests on rA1:22–24 (decisive argument platform-bound), bR2:208–209 and rE2:17–18, independently of T1 |
| S7 | MAJOR | dpk:54–62; hep:41–47; amd:83; hepE1:25; dpk:49 (b), (e); hap2:110–118, 149–156 | The SUBST list omits several owner statements: H2's supervision statement, H4's exclusivity statement, H5's storage statement, H8's "or an owner attestation" / "stated substitute", D-S15 (b)'s owner-supplied ref listing (which makes the whole S15 assertion owner-supplied), and the anchor record itself. Nearly every host fact on which a gate depends is attested by the party that chose to continue. hap2 says none of H1 / H8's evidence is "a measurement the host cannot falsify" | §5 item 7. Require DMI identity (no substitute) for H8, and a non-owner-produced or pre-OD-3-anchored listing for S15 |
| S8 | MAJOR | dpk rows 7, 8, 13, 16 (lines 36–37, 42, 45); amdE1:77–80; pkt:204–217; bR2:4, 29, 45 | The route introduces new constants and rules: 30 s window; N = 3; `avg10 = 0.00`; at most 3 re-reads; ≥ 6 physical cores; the lowest-trip thermal rule; and MBS-8 (ii) values. They were drafted by a coordinator whose non-holder status is self-declared. MB-S's MEDIUM–HIGH depended on T6 mitigations M1 (itemised provenance trace) and M4 (exposed parties out). No text requires M1 for these | §5 item 8 |
| S9 | MAJOR | S12 brief lines 2–4; fr1d:56, 88–93; od2:6–16; FR1:462–463, 490–491 | This review's appointment relies on an owner sentence ("Complete the fresh S12 review using an eligible reviewer") that is not in the committed verbatim OD-2 record. FR1 required the owner to name the S12 reviewer, and required FR1 condition 1 before S12 was commissioned; both are owner-reserved. The texts reviewed have not had FR2. The rating has no standing beyond advice | Q8 steps. Commit the verbatim sentence or withdraw the quote. Re-commission after FR2 if material changes follow |
| S10 | MINOR | S12 brief "GOVERNING TEXT"; amd:36–37, 249; obr5:31–33 | MBS-5(b) is presented as governing this route's floor. It binds evaluations "after the MB-S marker", and none exists (prep:13). Its real effect here is on routes *after* this route's marker | State this. Cite the S6 texts for the current floor |
| S11 | MINOR | dpk:75–79 ("can be decided"); gov:104–108 ("never tuned toward a threshold"); prep:53 | Nothing forbids deciding the D-* measurement definitions (D-MEM-FREE, D-EXCL-WINDOW, D-THERMAL and others) after Phase-1 readings on the named machine. The first host failed R-FREE. Choosing definitions with the second host's readings in view is outcome-driven re-selection of gate rules | §5 item 9 |
| S12 | MINOR | amd:228–229; prep:53; hep:57–64 | The "no host shopping" scope leaves out candidates inventoried and dropped before L-DET, and failures after L-DET (designated series, gates, qualification) on the named host. The number of host attempts need not be disclosed | §5 item 10 |
| S13 | MINOR | amdE1:67–70; hepE1:43–44; prep:47–55 | The no-update window runs from the L-DET build through build review, designated series, qualification, freeze, S1 and grant to the 7-day deadline, with no maximum. A forced security update voids L-DET and stops the route. A restart would then be a post-result ruling taken under time pressure | §5 item 11 |
| S14 | MINOR | gA1:23–34, 122; bR2:310, 446; prep:19 | S1 must state the successor is "not a rerun on host grounds" (E3). This route exists because a host gate failed. The statement may still be true relative to MB r1, but no text explains it for this route | The S1 brief addresses it explicitly (Q6 item 4) |
| S15 | MINOR | obr5:31–33 | The owner brief r5 still says "HIGH, unless reviewers and you decide otherwise (D-RC2-SCOPE)", a downgrade path that amdE1 E1.6 withdrew. amdE1 E1.7 corrects V-A only | An owner brief revision stating "not lower than HIGH" and the conditions of §5 |
| S16 | MINOR | pkt:187; obr5:41; amdE1:94–99; hepE1:49–50 | V-A puts provider-updated runner software on the official host. That software is an S17 compute load, an H3 update vector and a T3 observation path. E1.7 forbids sessions in the window but says nothing about the runner's process or its updates | §5 item 13. Prefer V-B |
| S17 | NOTE | gov:123; amd:239–244; rE2:12–17 | T2 and T5 are not stated in any permitted text. Governance S9's "T1–T4" are a different set with the same labels | An eligible reader lists T1–T6 verbatim for the S1 brief and disambiguates the labels |
| S18 | NOTE | amd:230; rA1:67–68 | E8 covers L-DET records next to a cell-308 quantity. New-host decoy and L-DET runtimes next to MB r1 runtimes, or next to a cell-308 projection, are the S13 channel on this route | Extend E8 to every decision document (OD-1, MBS-8, S1 brief) |
| S19 | NOTE | amdE1:39–41; lspE1:15–27; bR2:433 | An L-DET MATCH must not be described to the owner as risk-reducing for the value. It covers four decoy records. MB r1 pinned only its Python version, so "same platform" was never fully defined for the reference run | Wording in the S1 brief and the owner briefs |

Findings by severity: BLOCKING 2 · MAJOR 7 · MINOR 7 · NOTE 3.
