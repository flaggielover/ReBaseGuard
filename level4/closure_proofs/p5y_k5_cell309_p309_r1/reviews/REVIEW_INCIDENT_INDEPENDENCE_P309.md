# Independent incident-independence review of P309 package 1 (candidate rev. 2b), formal campaign p5y_k5_cell309_p309_r1
INCIDENT_AUDIT_ACCEPTED
U2_FINDING: NOT_TRIGGERED_WORDING_DISCREPANCY

**Reviewer.** I am an independent reviewer. I did not produce or coordinate this campaign or the research campaign, and I
am not R1, R2 or R3. I have no stake in the outcome.

**Scope.** Brief: `reviews/BRIEF_INCIDENT_INDEPENDENCE_P309.md` (committed at f15fad90, blob abac4884, sha256 91e11f0d…).
* Reviewed state: branch `claude/p5y-k5-cell309-p309-r1`, HEAD `4754ac16` when I started (remote tip `4754ac16`).
* One commit landed while I was reviewing: `2f1b6073` (01:49:34Z, `fc2/FC2_SPEC.md`). I read it for classification
  only (see §9, O5).
* Research namespace (RNS): unchanged since `eb9a9c22` (`git diff --stat eb9a9c22 HEAD -- RNS` is empty).
* Written 2026-09-30, about 01:48–02:10Z.
* All times below are git author/committer times (UTC, identical for every commit here), unless marked "prose".

**Standard.** The standard is **temporal and parametric independence only**. The verdict does not claim that the route
choice is independent of exposed information, and it could not: see §4.

---

## 0. Execution declaration and ledger

* I ran only read-only analysis:
  * `git log` / `git show` / `git diff` / `git rev-parse`;
  * `sha256sum` of committed files;
  * short Python scripts over committed JSON metadata:
    * decoy runtime fields;
    * manifest pins (outside-RNS pins by blob id only, no content read);
    * ledger drift fields and counters.
* I made no producer, verifier, kernel, test or driver call.
* Git package blobs were extracted to my scratch directory for diffing.
* Ledger: `/tmp/claude-0/-home-user-ReBaseGuard/ea54e9f6-e828-5447-be15-220ef2c329fd/scratchpad/iir/REVIEWER_EXEC_LEDGER.jsonl`
  (4 lines, all class READ_ONLY_ANALYSIS; cells_touched [], drifts [], kernel_runs 0, new_target_evaluations 0).
* **Honesty note.** These analyses were read-only, so the brief did not require declaring them in advance. This section
  was written after they ran.
* Nothing beyond read-only analysis was run. No git write. The only repository file written is this one.

---

## 1. Verdict in brief

* **Temporal independence: yes.**
  * Every exposure of the coordinator to a 305–309 value that is on record happened on 09-29 between 12:58:44Z and the
    commit of 309R1-02 at 13:06:42Z (`daa1bd64`). All of them precede the first route commit, THEOREM_SRK `3df7a1a5` at
    13:15:54Z.
  * After 13:06:42Z the exposure ledger records no coordinator row that carries a 305–309 value. Research ledger
    rows 21 and 54 carry none; the formal ledger row is a governance grep with no match.
  * No 309 Stage-1 quantity exists. Both execution ledgers show 0 target evaluations, 0 proxies, and no ledgered drift
    meeting |e| ≥ 6/5 (maximum |e| = 37/32). The self-audit A1/A2/A10 at eb9a9c22 passes.
  * So no P309 decision was taken after, or revised in response to, any new target-information event.
* **Parametric independence: yes.** No Stage-1 parameter is a function of an exposed value. All were fixed by
  written, target-free rules:
    * THEOREM_SRK §7 at 13:15:54Z;
    * amendments A1 (decoy-driven, synthetic h = 3), A3 at `5f41d8a9` and A4 at `61a65003`, all C1b-inherited or
      generic;
    * the RLR307 rules verbatim.
  * The producer code is frozen at lock `2a03e838`, and THEOREM_SRK last changed at `cfb88c69` (16:42:28Z on 09-29).
  * All 25 code pins of the preserved pre-FREEZE_READY draft manifest keep **identical** blob ids in the rev. 2b
    manifest (§6).
  * The package-level rule choices of rev. 2/2b (§5) are structural mappings and resource limits with target-free
    justifications. None was chosen by reference to a 309 quantity.
* **Route-choice / motivational independence: no.** This is the disclosed MEDIUM-HIGH liability (§4).
  * SRK attacks exactly the order-0 channel terms that committed tail dominance knowledge, including 309, identifies
    as dominant (`theory/PHASE1_RESULTS.md:28-40`).
  * It was conceived right after 309R1-01, 309R1-02 and the graph-A §2 read.
* **Conditions C1–C8** are in §10. None of them requires target information. C5 and C7 must be met **before** the
  freeze.

---

## 2. Git commit order used as primary evidence (research branch, then formal branch)

| time (UTC) | commit | event |
|---|---|---|
| 09-27 19:09 / 20:13 / 21:06 | 2f0fb5e1 / 07ab6b94 / 4d64e2b0 | overnight incidents 01 / 02 / 03 committed (overnight namespace) |
| 09-29 12:58:44 | 52e00290 | charter, `TARGET_QUARANTINE_309.json`, exposure ledger rows 1–5 |
| 13:02:26 | 1f6b724a | 309R1-01; exposure row 6 (graph A §0,2,3: 309 values, coordinator) and row 7 |
| 13:06:42 | daa1bd64 | 309R1-02 (exposure row 8) |
| 13:15:54 | 3df7a1a5 | THEOREM_SRK incl. §7 target-free parameter rules |
| 13:17:07 / 13:49:38 | 23e66ba7 / cc8e5e7f | reader A report, reader B/C exposure rows (numbers not relayed), sanitized digests |
| 13:44:15 | f0dbaa79 | implementation; decoy declaration |
| 13:52:08 | 7f1eb363 | dossier, route matrix, **rule S** (C1–C5) |
| 13:58:56 | d627960b | Phase-3 comparison: "around an hour for a 4-sub-block cell ladder (decoy estimate)" |
| (prose) 14:11:58 | scratchpad | protocol draft born (309R1-04) |
| 15:48:31 | fae64157 | R1: NOT_READY |
| 15:55:20 / 16:07:36 / 16:11:12 | 5f41d8a9 / 2a03e838 / 61a65003 | A3 (2⁻¹⁰ hull, gate) / producer lock / A4 constants |
| 16:12:58 | a748ac49 | SRK-T OUT (rule S C5); R2 brief |
| 16:42:28 | cfb88c69 | last change to THEOREM_SRK and srk_gate |
| 23:09:22 | 142fe64e | qualification evidence complete (decoys only) |
| 23:27:12 / 23:28:40 | b7f05327 / b5ad2372 | R2 FREEZE_READY_WITH_CONDITIONS / adapter geometry fix, E-15 |
| 23:59:53 | 426461c8 | 309R1-03 and E-17 recorded |
| 09-30 00:06:01 | f026c80b | R2 FREEZE_READY |
| 00:08:58 | ce829bb4 | package committed: **Stage 1a ≤ 6 CPU-h; Stage-1b CERTIFICATION_FAILED ⇒ NOT_CLOSED** |
| 00:33:57 | 814ff984 | R3 preserved + rev. 2: §2.5 mapping, **48 CPU-h, budget → fallback**, **Stage-1b → S_I1** |
| 00:41:11 | 36e672be | rev. 2b budget mechanics; Stage-1b budget → S_I1 |
| 00:46:17 | eb3b3432 | 309R1-04, E-18 |
| 00:50:18 | 1671f0a3 | drafts preserved (sha256 recorded in the same commit); R3 COMPLETE |
| 00:51:16 | eb9a9c22 | research HEAD |
| 01:42:12 | 47b55d00 | formal campaign; owner decisions verbatim (fenced body sha256 re-verified: bc4cdb48…) |
| 01:47:05 | f15fad90 | coordinator audit, U2 reconstruction, this brief; formal exposure row (307 grep, no match) |
| 01:49:34 | 2f1b6073 | FC2 spec (during this review) |

**Checks I ran on this order.**
* Incident files 309R1-01..04 and `TARGET_QUARANTINE_309.json` each have exactly one commit.
* `ERRATA.md` and `EXPOSURE_LEDGER.jsonl` are append-only: every change adds lines and deletes none.
* All 48 code and 7 data pins of the rev. 2b manifest match by blob at eb9a9c22 and at HEAD. The sha256 matches for
  all 40 RNS code pins.

---

## 3. Task 1: each incident

Classes of information only; no value is reproduced.

| item | information class exposed (to whom) | position in git order | could it set a P309 parameter, rule or route choice? | finding |
|---|---|---|---|---|
| **Overnight 01** + residue (global-integrity F13) | Committed tail radius-sum per-order shares for 306–309 and a TPT generic-factor combination, i.e. a qualitative TPT gain proxy. Reached this coordinator only through 309R1-01 and, qualitatively, through reader A §G ("A0·P̄2 dominates; order-3 first, order-4 second; f_H negligible; A1, A2 small", `PHASE1_RESULTS.md:28-40`) | 09-27, before everything | **Route choice: yes** (it tells which channel dominates; SRK attacks it). **Parameters: no**; nothing in §7/A1–A4 refers to a share | Independent temporally and parametrically; motivational dependence disclosed (G1). TPT stays OUT (rule S C4) |
| **Overnight 02** + residue (F12) | A committed Λ certificate attributed to 309 and its endpoint drift, re-attributed to 308 (reader-level; not relayed) | 09-27 | No. P309 uses no Λ/E_a[τ] floor; A0 comes from S_I1. The incident produces the non-re-attribution rule (`P309_PROTOCOL.md:36-39`, grant field), which is enforced by the gate/adapter cell binding | Independent |
| **Overnight 03** | A C2b brief scale from 308 figures | 09-27 | No. P309 does not use C2b | Not applicable |
| **309R1-01** | Qualitative proxy (mental) of TPT factors against the committed 309 gap; incident-01 shares; a sealed 306 Γ | 1f6b724a 13:02:26, before THEOREM_SRK | Route choice: indirectly (dominance). Parameters: no | Independent temporally/parametrically; part of G1 |
| **309R1-02** | The coordinator's mental in-band estimate of k₁(x; e) along paths (a new-route operator quantity at a band drift) | daa1bd64 13:06:42, before THEOREM_SRK | It bears on the belief that SRK "could matter at 309". It set no parameter: ladder {8, 10, 12}, cover 1/4, levels, μ, KT, rounding and N_E = 4 are in §7 (13:15:54, before any decoy result) or in A1/A3/A4 with generic, decoy-driven or C1b-inherited bases (`THEOREM_SRK.md:200-211, 239-266, 303-393`) | Independent temporally/parametrically; the root of MEDIUM-HIGH |
| **309R1-03** | None: a harness-v1 probe shifted a decoy block into the band and was refused at parse time; nothing evaluated | 426461c8 23:59:53 | No. It changed only in-band verification to genuine-only (safety-increasing) | Independent; liability NONE concurred |
| **309R1-04** | None (the drafts carry no 305–309 value; §6) | eb3b3432 / 1671f0a3 | See §6 | Independent; LOW correctly classified |
| **E-3** | None: a real-kernel decoy probe at [1/2, 17/32] (out of band) whose order relative to the declaration is unverifiable | f0dbaa79 / 5f41d8a9 | No; out of band and declared | Independent |
| **E-17(a)** | None known: unrecorded pre-commit verifier self-test runs. The committed self-tests reach \|e\| ≤ 1.05, and the band refusal is in the verifier's first commit (5e96041f, `srk_verify_indep.py` QUARANTINE_BANDS) | 426461c8 | Only if an unrecorded run had evaluated in band, which the committed refusal code makes implausible and which I cannot verify. The verifier settings (N = 8, max_depth = 24, width 1/4) are generic | Independent, with residual unverifiability, as disclosed |
| **E-18 / manifest-generator runs** (prose times 23:11:03Z and 23:47:29Z; ledger rows 536–542 with two append-only corrections) | Git blob ids of the 309 input files (metadata); sha256 of committed code bytes, including `RLR307_FREEZE.json` and `C1B_R2_CODE_PINS.json` (hashed, never parsed) | Before R2's final verdict (00:06:01) | No. A hash carries no value; the manifest lists pins, it chooses none | Independent |
| **Ledgered necessary reads**: coordinator row 6 (graph A §0,2,3) | 309 values: the clause-tolerated A0 ceiling versus the Λ floor; a C5-T ceiling string; σ3 pure-tower versus adopted at 309 | 1f6b724a, before THEOREM_SRK | Motivational only. σ3 is the part of B3 that SRK cannot reduce, so knowing its size bears on SRK's potential. σ3 enters P309 only through the frozen adopted inputs; no choice was made from it | Independent temporally/parametrically; part of G1 (aggravation named in 309R1-02) |
| Reader A/B/C rows 9–53 | Numerous 305–309 values seen by firewalled readers; **not relayed** (reports and digests committed, redacted, with a post-write grep) | 13:11–13:46 | Only through qualitative relays: dominance, the C3 knockout, route statuses | Independent; see brief-integrity gap (§7) |
| Reviewer R1 row 55 | THEOREM_TCT lines 12/39 classes (tail drift domain; atom-constant ranges) | 15:48 | R1's B1 asked for a target-free drift-block rule. The coordinator chose the generic 2⁻¹⁰ grid and N_E = 4 (N_E was already in §7 at 13:15). The 2⁻¹⁰ outward hull adds at most 2⁻¹⁰ per side, so there is no plausible parametric channel | Independent |
| Formal row 1 (01:45:01Z) | A grep for "U2" in the cell-307 campaign's governance files; no match, nothing displayed | f15fad90 | No | Permitted under the inherited research allowance (history reconstruction, ledgered). It is outside the formal quarantine's three enumerated necessary reads. I cannot verify it without breaching my firewall |

**RLR-specific knowledge.** The C3 knockout (A1 = A2 = 0 still leaves Γ > 0 at 309) and "A1, A2 small" are known
qualitatively. They are target-derived facts about the value of RLR at 309, and they bear on the Stage-1b rule (§5.3).
They do not set any RLR parameter: the RLR307 rules are reused verbatim, with the C1B_R2 pins.

---

## 4. Task 2: result-chasing, my own rating

**My rating: MEDIUM-HIGH** (upper end), concurring with G1. I do not raise it to HIGH, and I do not lower it.

* **Why not lower.**
  * The route was selected with qualitative target structure in hand: dominance at the tail including 309, the 309 gap
    from graph A, σ3 at 309, and the in-band mental estimate 309R1-02. Its conception immediately follows those
    exposures (13:02–13:06, then 13:15).
  * Rule S's "BLOCKED-only" C4 threshold (13:52) was set by the exposed coordinator, and it admits SRK while
    excluding TPT.
  * Phase-4 drafting began at 14:11 (prose), before any review, which shows orientation toward the endpoint.
  * Every package-level efficacy rule changed after R3 (§5) moved in the closure-favouring direction relative to the
    earlier text or to R3's minimal fix. The exception mapping is the one that moved the other way.
  * 309R1-02 is classified as a rule breach "without a Γ-proxy". Its own text concedes that the impression "bears on
    whether the route could matter at 309". It is of the same kind as the TPT proxy that made TPT HIGH/BLOCKED.
* **Why not HIGH.**
  * The TPT proxy combined committed shares with TPT's **fixed generic constants**, so it was close to quantitative.
    SRK's leverage at 309 depends on certified supersolution values Γ̄ that nobody has computed, so the mental estimate
    carries much less information.
  * No SRK or RLR quantity exists at any band drift (ledgers; A10).
  * No parameter is a function of an exposed value (§3).
  * Min-composition dominance and a single, pre-registered, exact, strict evaluation mean that motivation can affect
    only **whether** the attempt is made, never the validity of its result.
* **Components.**
  * Route choice / motivation: MEDIUM-HIGH.
  * Parameters: LOW.
  * The rev. 2/2b rule choices: LOW–MEDIUM (closure-favouring, target-free justified, reviewed by R3 F3, adopted by
    the owner).
  * 309R1-04 as a separate item: LOW (§6).

---

## 5. Task 3: the three rev. 2 rule choices

All three were made in commits `814ff984` (00:33:57Z) and `36e672be` (00:41:11Z). They come after every exposure and
before any 309 Stage-1 number. R3's text containing N2 and N12 lands in the same commit as rev. 2; its WIP `1d8efbbb`
held only the declaration. So git cannot order R3's notes against the edits. R3's follow-up F3 (`REVIEW_P309_PACKAGE_R3.md:516-542`)
then reviewed the edits.

1. **Stage-1a failure mapping (protocol §2.5, `P309_PROTOCOL.md:69-95`).**
   * **Exceptions → EXECUTION_INDETERMINATE.** This is R3's minimal fix (`REVIEW_P309_PACKAGE_R3.md:315-316`), and it
     reduces the chance of closure. It is target-independent.
   * **Budget exhaustion → fallback** is **not** R3's minimal fix. R3 proposed "any exception or **cap overrun** is
     EXECUTION_INDETERMINATE" (:316). The coordinator chose fallback, which **raises** the chance of closure relative
     to that fix.
   * Target-independence: the justification is target-free. A pre-declared resource stop is not a malfunction, and a
     missing certificate only removes a min component, so validity is unaffected. It applies identically to every
     possible outcome, and no 309 cost or Stage-1 information exists.
   * **Finding:** target-independent in the required sense. The coordinator audit's statement that rule 1 "was
     proposed by R3 … It reduces the chance of a closure" (`INCIDENT_AUDIT_P309_COORDINATOR.md:52-54`) is **inaccurate
     for the budget branch** (C6(a)).
2. **The 48 CPU-h budget and its mechanics.**
   * The pre-review text had **6 CPU-h**:
     * `P309_FORMAL_PACKAGE_DRAFT.md:21`;
     * ce829bb4 `P309_FORMAL_PACKAGE.md:23`.
   * Rev. 2 raised it 8× to 48 CPU-h. The coordinator's timeline does not mention the change.
   * Target-free basis, which I verified from committed decoy evidence:
     * the qualified real-kernel decoy cell (h5, e ≤ 527/1024) costs about 4.4 CPU-h (V ≈ 15 940 s plus W);
     * the synthetic h3 decoy cell costs about 7.2 CPU-h. **The old 6 CPU-h cap would have bound on a qualified decoy
       cell**;
     * the Phase-3 estimate at 13:58 ("around an hour", `PHASE3_ROUTE_COMPARISON.md:17-18`) was about 5× too low, which
       explains the stale 6.
   * The mechanics are generic: (b_j, d) jobs, rung-major order, a 12 CPU-h per-job limit, and stop without raising.
   * No 309 SRK cost exists anywhere. The only tail cost the programme records is a K1-replay cost, which a reader saw
     and which is redacted in the digest (`dossier/digests/COVER.md:215`). It concerns a different computation.
   * **Finding:** target-independent. The decoy-cost basis is resource sizing, not a Γ prediction (C3).
3. **Stage-1b fallback to S_I1 (protocol §3, `P309_PROTOCOL.md:104-116`).**
   * The drafts and ce829bb4 had the RLR307 rule, CERTIFICATION_FAILED ⇒ NOT_CLOSED (`P309_PROTOCOL_DRAFT.md:84`,
     `P309_FORMAL_PACKAGE_DRAFT.md:152`).
   * R3 N12 only asked that the asymmetry be made visible, and it called NOT_CLOSED "a legitimate frozen choice". The
     switch to fallback was the **coordinator's** choice, flagged to the owner and adopted under G3.
   * **Adversarial reading, confirmed.** The coordinator knew:
     * the C3 knockout (RLR alone cannot close 309);
     * qualitatively, that A1 and A2 are small at the tail.

     Under NOT_CLOSED, a failure of an optional, low-value component would forfeit the single evaluation. The
     fallback therefore strictly raises P(closure), and the coordinator knew it would.
   * **Why it is still target-independent in the required sense.**
     * (i) It is fixed before any 309 Stage-1 number, and none exists.
     * (ii) It is not a parameter, and it is not tuned to any value.
     * (iii) Its justification holds for every cell and every outcome: S_I1 is a valid supply without RLR (min
       composition, THEOREM_SRK §3, rule S C2).
     * (iv) It mirrors the Stage-1a fallback that the drafts already contained by 16:13Z on 09-29.
     * (v) Validity cannot be affected. Closure still requires an exact, strict Γ < 0 on valid supplies.
     * (vi) It is disclosed with its direction, reviewed (R3 F3) and adopted explicitly by the owner (G3).
   * What it does **not** have is motivational independence. That is covered by the standard wording.

---

## 6. Task 4: preserved pre-FREEZE_READY drafts against the committed package rev. 2b

**Integrity.**
* The three drafts hash to the sha256 values in `INCIDENT_309R1_04_ADDENDUM_DRAFTS.md:19-21`. But those values were
  committed together with the drafts (1671f0a3, 00:50:18Z), after the package. They prove content, not timing.
* Content-to-git consistency (my check): each draft references only committed items that precede its claimed
  last-modify time, and nothing later:
  * **Protocol draft** (claimed 16:13:32Z): it cites A3, A4 and SRK-T OUT at a748ac49 (16:12:58). It has no FC2 and
    no genuine-only rule (both from R2 at 16:25 or later).
  * **Formal-package draft** (claimed 23:29:12Z): it cites "post-R2-C1 state" and E-15 (b5ad2372, 23:28:40). It has
    no 309R1-03, no harness v2, no 21 self-tests and no 1868/1868 (all 23:36 or later).
  * **Manifest draft:** its `repository_head` is 1a6735b4 (23:46:59), against a claimed 23:47:29Z.

  This corroborates the claimed times. It cannot exclude the possibility that an earlier state (from 14:11) differed.

**Diff (draft → ce829bb4 → rev. 2 → rev. 2b), classified.**

| change | origin | direction | could it reflect target information? |
|---|---|---|---|
| Status headers, owner wording | R3 N11/N16 | neutral | no |
| FC2 (a)–(d), grant-scoped guard/verifier, **genuine-only in-band verification**, adapter bound to cell/geometry/verifier_id | R2 (C1, P-1, FC2), 309R1-03 | safety (can only refuse more) | no |
| Per-rung serialization; seal all certificates, verdicts and the GateResult report | R3 N1 | neutral / auditability | no |
| Exceptions → EXECUTION_INDETERMINATE; adapter refusal is an exception | R3 N2 | against closure | no |
| **Budget exhaustion → fallback; 6 → 48 CPU-h**; (b_j, d) jobs, rung-major order, per-job limit | coordinator (after R3 N2, F2.1–F2.3) | toward closure | no (§5.1–5.2) |
| **Stage-1b CERTIFICATION_FAILED: NOT_CLOSED → fallback to S_I1**; Stage-1b budget → S_I1 | coordinator (after R3 N12, F2.3) | toward closure | no (§5.3) |
| In-run checks named; post-seal review mode; historical-control digest | R3 N3, N9, N10 | against closure (more INDETERMINATE paths) | no |
| QC15–QC17, Q01–Q17, QC10 on host, sandbox positive path | R3 N4, N6, N14; F2.4 | neutral | no |
| Non-re-attribution; Ew overlap statement | R3 N15, overnight 02 | safety | no |
| Liability lists (309R1-03, 309R1-04, E-3, E-17(a), E-18, generator runs) | R3 N11, D1 | disclosure | no |
| Pins 25 → 48 code, 6 → 7 data | R3 N13 | neutral | no. **All 25 draft code pins keep identical blobs**, so no producer, verifier, gate, adapter, theorem or declaration byte changed between the draft manifest (1a6735b4) and rev. 2b |
| Science constants (ladder, cover, levels, μ, KT, rounding, 2⁻¹⁰ hull, N_E = 4, verifier N / max_depth) | — | unchanged | — |

**Is 309R1-04 (LOW) correctly classified? Yes.**
* The drafts contain no 305–309 value. I read all three in full: symbols, generic constants, the band literal, code-hash
  prefixes and a Python version string only.
* No draft parameter survived into rev. 2b without being either already committed before the draft's last
  modification (the science constants) or reviewed by R3 (package mechanics).
* The drafts are evidence that the pre-review intent was **more conservative** (6 CPU-h; Stage-1b NOT_CLOSED). The
  relaxations were made later, in committed text, and flagged.
* The motivational aspect (early orientation toward the endpoint) is real. It is subsumed in G1's MEDIUM-HIGH and does
  not need a higher separate rating.
* **Documentary error:** the incident file says "found ~01:1xZ" (`INCIDENT_309R1_04_PREMATURE_PHASE4_DRAFTING.md:5`),
  but its commit is eb3b3432 at 00:46:17Z (C6(b)).

---

## 7. Task 5: brief integrity

| brief | committed or hashed? | evidence |
|---|---|---|
| Route review R1 | committed before the review | `reviews/BRIEF_SRK_ROUTE_REVIEW_R1.md` at 464494e8 (13:56:21), before the R1 WIP (15:41:08) |
| Route review R2 | committed before the review | at a748ac49 (16:12:58), before the R2 WIP (16:25:16) |
| Package review R3 | committed before the review | at b48a1fa2 (00:09:48), before the R3 WIP (00:26:44) |
| This review | committed before the review | f15fad90 (blob abac4884) |
| Candidate briefs (qualification, execution, adjudication) | committed (template) | `P309_REVIEW_BRIEFS.md` (blob dadbf178), pinned in the manifest |
| **Firewalled readers A, B, C** | **NO**, neither committed nor hashed | Only their outputs are committed (`dossier/sources/READER_*`, `dossier/digests/*`, labelled "condensed layout"). The research record never states the reader briefs; the quarantine describes the practice only generically (`TARGET_QUARANTINE_309.json` firewall_practice) |
| **Independent verifier's author** (original verifier and the C3/self-test repairs) | **NO** | No brief or prompt text in RNS |
| **Follow-up prompts** (R2 phases B–D; R3 follow-ups 1–3) | **NO** (the reviews state that they worked under their committed briefs) | `REVIEW_SRK_R2.md` phase headers; `REVIEW_P309_PACKAGE_R3.md:421` |

**Finding.** The 307-pattern requirement ("briefs hashed or committed", `READER_B_GOVERNANCE_REPORT.md:60, :125`),
the draft package's own G.1, and `P309_REVIEW_BRIEFS.md:47` are **not met for the reader and verifier-author briefs**.
* What was actually relayed is committed and sanitized, so this gap opens no demonstrated channel for target
  information into P309.
* It does leave the readers' instructions unauditable. For example, a reader brief could have asked for a targeted
  qualitative comparison, and the record could not show it. The dominance relays in `PHASE1_RESULTS.md:28-40` are
  exactly such qualitative target structure.
* This is a documentary condition (C5), not a rejection reason.

---

## 8. Task 6: U2

**Fact table (`U2_FACTUAL_RECONSTRUCTION.md`).** Checked inside my firewall.
* **Citations: correct.** READER_B:43, SC_SUPNORM:252, RSO:229, COVER:226, CELL309_DOSSIER:43 and READER_A:25 say what
  the reconstruction attributes to them.
* **Stage 1a / 1b rows: correct.** Γ̄ and A1_RLR/A2_RLR are operator-only.
* **Stage-2 input rows: correct.** The adapter reads exactly the TC-T scalars listed (`impl/srk_adapter.py:30-36`:
  sup F/D/H, the deltas, eps_src[0..3], plus f_G, Env4, σ3 and σ4 from the frozen `tct_rule` object). It re-derives
  the TC-T radius from them and requires exact equality with the frozen output (`:103-114`), so those scalars enter
  in their frozen roles.
* **The rad_r^SRK row is imprecise, in two ways.**
  * **rad_r^SRK is a new formula.** It calls rad_r^SRK "outputs of the frozen consumer with the operator-only
    substitutions S1 and S2 … frozen formulas". S1 (the supply) is a pure substitution into the frozen formula, as in
    307. S2 is not: rad_r^SRK comes from a **new formula**, THEOREM_SRK §3 (`THEOREM_SRK.md:101-106`;
    `srk_assemble.rad_srk`, called at `srk_adapter.py:116-118`). The formula **recombines** the P3-provenance scalars
    s_F, s_D, s_H, σ3, σ4, ε3 and f_H with the operator certificates Γ̄_i, which replace the frozen drift-aware norms
    k_i as their multipliers. It is "frozen" only in the sense that the P309 freeze will pin it. The 307 precedent
    (supply-only change) is therefore not an exact analogue for S2.
  * **The nearest committed U2 case is not addressed.** The same committed record classes R10 Corollary T as needing
    U2 (`ROUTE_SELECTION_RULE.md:29`; `PHASE1_RESULTS.md:169`; `ROUTE_MATRIX.md:69`). Corollary T is also a new formula
    that combines record fields with non-record factors. The record's stated reason is that it "tightens a recorded
    interval with a new quantity derived from the record".
* **The 307 governance grep: unverifiable by me** (firewall).

**Does P309 derive a new quantity from P3 records under U2's committed definition? No, on my reading.**
* The committed definition is "admissibility of new quantities derived from P3 tail records (C6 Condition 10: No P3
  object may be adopted as new scientific evidence)". The committed record operationalizes it in rule S C3
  (`ROUTE_SELECTION_RULE.md:15`, fixed at 13:52 on 09-29, before any decoy comparison) and its examples:
  * SC: a new statistic recomputed from candidate payloads;
  * RSO: regeneration;
  * COVER: new K1 records;
  * Corollary T: a re-derived, tightened **record-level** interval.
* P309 creates no such object:
  * no record field or record interval is re-derived or tightened;
  * no payload or statistic of the record is formed;
  * its new evidence objects are operator-only.
* Its derived outputs (rad^SRK, 𝓗_SRK, M, Γ) are consumer-level enclosures built from the committed record scalars.
  Those scalars keep their established premise roles: SRK's premises on s_F, s_D, s_H, σ3 and σ4 are exactly TC-T's
  (`THEOREM_SRK.md:85-95`). These outputs are the same category as C2's own TC-T enclosure and Γ, which the programme
  accepted.
* The line between SRK (consumer enclosure) and Corollary T (record interval) is defensible, but it is not
  self-evident. It is the owner's to confirm.

**Is the owner's literal wording satisfied? No.**
* "The authorized route uses no P3-derived quantity" is false word for word:
  * Stage 2 consumes P3-provenance inputs (TCT_INPUTS_309, ADOPTED_TAIL_INPUTS, K1 record fields);
  * S2 recombines several of them in a new formula.
* The wording **originated in the research package**, not with the owner:
  * `P309_FORMAL_PACKAGE_DRAFT.md:196` ("no P3-derived quantity is used");
  * ce829bb4 `P309_OWNER_DECISIONS.md:17`;
  * HEAD `P309_OWNER_DECISIONS.md:21`;
  * R2 relayed the claim at `REVIEW_SRK_R2.md:44`.

  The owner ruled on the package's own premise. The correction is a correction of that premise. It does not reinterpret
  U2.
* Option (b) of the reconstruction ("the ruling as worded is satisfied") is therefore **not available** from this
  review. Owner confirmation on an accurate premise is required before the freeze (C7).

---

## 9. Other findings (documentary; no target dependence)

* **O1. The coordinator audit's timeline is incomplete, and its dates are wrong in places.**
  * It omits the pre-rev.-2 state: 6 CPU-h, and Stage-1b NOT_CLOSED in the drafts and ce829bb4.
  * It misattributes the budget branch to R3 (§5.1).
  * It dates the overnight incidents "09-28"; git shows 09-27 (19:09–21:06Z).
  * It dates 309R1-03 "00:1x on 09-30"; the recording commit 426461c8 is at 23:59:53Z on 09-29.
  * These go into C6.
* **O2. Two immutable incident files give "found" times after the commits that record them.**
  * 309R1-03 says "~00:1xZ", against a commit at 23:59:53Z.
  * 309R1-04 says "~01:1xZ", against a commit at 00:46:17Z.

  Prose times in this record are therefore weaker evidence than git times. That includes the scratch-draft times,
  which I corroborated by content (§6).
* **O3. The proxy counters conflict.** The research README (`README.md:27`), MORNING_HANDOFF item 23 and the
  ZERO_TARGET_LEDGER (0 proxies) say "no target-equivalent proxy". But 309R1-01 records its mental impression as "a
  qualitative target-equivalent proxy" (`INCIDENT_309R1_01_TPT_SHARES.md:7,10`; exposure row 7), and the overnight
  campaign counted the analogous event as 1. The owner-facing endpoint statement needs the qualifier (C6(d)).
* **O4. The formal push-record commits carry a research-campaign subject.** Commits 0e4849a7 and 4754ac16 have the
  subject "p5y: K5 cell-309 research r1 — ledger: …" (template at `code/checkpoint_push_p309.py:133`), yet touch only
  the formal namespace. This can mislead any audit that works from git logs.
* **O5. FC2 work started while this review was open.** `2f1b6073` (FC2_SPEC) was committed before this verdict, ahead
  of the owner's listed order (step 3 before steps 4–5).
  * It is target-free. It carries only the real band literal and a synthetic h = 3 test band.
  * It changes no P309 rule.
  * I do not treat it as an incident. It should be recorded as a process note, and FC2 is subject to C2/C4 like
    everything else.
* **O6. No latent-proxy addendum.** The 307 anatomy item "addendum, latent-proxy amendment" (READER_B §3.5) has no
  P309 counterpart. C3 below serves as the latent-proxy rule.

---

## 10. Conditions (for `incident_review_conditions_verbatim`)

* **C1 (wording).**
  * Independence is stated as **"temporal and parametric independence only"**.
  * No record, grant or handoff may claim route-choice or motivational independence.
  * SRK's MEDIUM-HIGH and RLR's MEDIUM liabilities stay in `disclosed_liabilities`. This review rates them MEDIUM-HIGH
    (upper end) and MEDIUM respectively.
* **C2 (freeze exactly as reviewed).**
  * The freeze commits the rev. 2b rules unchanged: the §2.5 mapping, the 48 CPU-h start threshold with its mechanics
    (12 CPU-h per job, (b_j, d) jobs, rung-major order, ≤ 4 workers), the Stage-1b fallback to S_I1 including its
    budget mapping, the outcome table, and every Stage-1 parameter.
  * The package documents must equal these blobs, apart from documented freeze fields: `P309_PROTOCOL.md` 5ac10d01,
    `P309_FORMAL_PACKAGE.md` 0867df9d, `P309_REVIEW_BRIEFS.md` dadbf178, `P309_OWNER_DECISIONS.md` 613b2949.
  * Any change to a rule or parameter after this review needs a new incident-independence review of the delta.
  * No change is permitted once any 309 Stage-1 quantity exists.
* **C3 (decoy latent proxies).**
  * No decoy output (Γ̄, tightness ratios, costs) may be juxtaposed with any 305–309 figure, or used to predict Γ309
    or SRK's efficacy at 309.
  * The decoy-cost basis of the budget is recorded as resource sizing only.
  * FC2 re-qualification and QC runs use decoys, synthetic geometries and the test band only.
* **C4 (no new exposure; necessary reads).**
  * Until the seal, any new exposure to a 305–309 value by the coordinator, the FC2 authors or the driver author is an
    incident, and before the freeze it triggers re-review of the delta. This includes exposure through the cell-307
    RLR code read for FC5.
  * The cells.json read of the 309 interval to name Ew is ledgered, and it happens only after the freeze has pinned
    every rule.
* **C5 (brief integrity; before the freeze).**
  * Commit verbatim, or hash, the briefs or prompts given to firewalled readers A, B and C and to the independent
    verifier's author, plus the R2 phase B–D and R3 follow-up prompts, from the session transcripts if they are
    recoverable. State that a post-hoc commitment evidences content, not timing.
  * If they are not recoverable, record that as an append-only disclosure in the formal namespace, and carry it in
    `disclosed_liabilities`.
  * Every future brief is committed before it is issued: FC2 verifier-variant author, qualification, execution and
    adjudication.
* **C6 (record corrections; append-only in the formal namespace; research files untouched).**
  * (a) Correct the coordinator audit: rule-choice 1's budget branch and the 6 → 48 CPU-h change are coordinator
    choices, closure-favouring relative to R3's minimal fix. The pre-rev.-2 Stage-1b NOT_CLOSED rule also belongs in
    the timeline.
  * (b) Record the 309R1-03 and 309R1-04 "found"-time discrepancies against git.
  * (c) The overnight incidents are dated 09-27.
  * (d) Qualify every "no target-equivalent proxy" and zero-proxy counter statement in the owner-facing handoff and
    grant: 0 computed proxies; one recorded qualitative (mental) proxy exposure, 309R1-01 (TPT at 309; TPT OUT); one
    mental in-band estimate, 309R1-02 (SRK).
  * (e) Fix the push-record subject template (O4) and note the two mislabelled commits.
* **C7 (U2; before the freeze).**
  * The freeze proceeds only after the owner confirms the U2 ruling on an accurate premise. That premise is the
    reconstruction's option (a), amended to state explicitly that:
    * S2 applies a new enclosure formula (THEOREM_SRK §3) that recombines P3-provenance scalars (s_F, s_D, s_H, σ3,
      σ4, ε3, f_H) with operator-only certificates, in their established premise roles, and re-derives no record-level
      quantity;
    * the committed record classes R10 Corollary T, which tightens a recorded interval, as needing U2.
  * Option (b) is not satisfied (§8).
* **C8 (grant disclosures).**
  * `disclosed_liabilities` adds E-18 and the manifest-generator runs.
  * It also adds the three rev. 2/2b rule choices, each with its direction (exceptions against closure; budget
    fallback, 48 CPU-h and the Stage-1b fallback toward closure).
  * It adds the reader-brief gap (C5).
  * C1–C8 are reproduced verbatim.

---

## 11. Reviewer disclosures

**Exposures (classes only; no value reproduced here).** Reading the brief-sanctioned incident files and ledgers, I saw:
* the committed tail radius-sum per-order share percentages for cells 306–309, including the midpoint-residual share
  (overnight `INCIDENT_01_TPT_GRAPH_PROXY.md`);
* one committed Λ (E_a[τ]) certificate value attributed to cell 309, with its exact endpoint drift at the 308/309
  boundary (overnight `INCIDENT_02_C2A_CROSS_CELL_FLOOR.md`);
* a numeric union drift range of the 305–309 tail band (content-class text of research exposure-ledger row 4);
* the content classes of all 55 research and 1 formal exposure rows, which name value classes only;
* a synthetic in-band probe block (309R1-03), the real band literal, and a synthetic h = 3 test band (FC2 spec). None
  of these is a cell quantity;
* git blob ids and paths of the 309 input files (metadata);
* qualitative tail-dominance statements (PHASE1 Q2).

I saw no Γ, margin, critical-A0, floor, ceiling or σ value for any cell 305–309. I did not open THEOREM_TCT.md (lines 12
and 39 included), any file of the cell-307 or cell-308 campaigns (git metadata only: the blob id of `RLR307_FREEZE.json`
by `rev-parse`), or any file outside FNS, RNS and the overnight incident, ledger and review files.

**Executions.** Read-only analysis only (§0); ledgered in the scratch file named there.
* No evaluation for any cell 305–309.
* No real-kernel run at any drift.
* No git write; no branch switch.

**Writes.** Only this file.
