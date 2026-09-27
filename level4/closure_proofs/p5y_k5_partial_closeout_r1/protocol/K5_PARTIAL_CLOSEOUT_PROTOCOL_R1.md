# K5 PARTIAL closeout protocol, successor R1: CUSUM K5, m = 5 tail cells 306–309

**Status: FROZEN** by the commit that adds this file; its hash is recorded by the freeze review and the handover.
After freeze neither this file nor `code/closeout_checks_r1.py` is edited; checker outputs go to `evidence/` only.

**This protocol authorizes no scientific computation.** No Γ is evaluated; no target-equivalent proxy, Monte-Carlo
science or interval/certificate science is performed; no supply is searched and no constant optimized; no floor or
adoption limb is created; no cell is adopted; no coverage map is created or modified.

---

## 0. Predecessor rejection (provenance) — carried, not rewritten

* The predecessor closeout protocol, frozen at **08e9acd176aea4351425c169d2eac723d0a2208b**
  (`level4/closure_proofs/p5y_k5_partial_closeout/protocol/K5_PARTIAL_CLOSEOUT_PROTOCOL.md`), was **REJECTED** by
  the independent freeze review committed at **591b43948a07e5fd916de37b3ef4d38830bb7b94**
  (`level4/closure_proofs/p5y_k5_partial_closeout/review/CLOSEOUT_FREEZE_REVIEW.md`, line 2
  `CLOSEOUT_FREEZE_REJECTED`). That review is **authoritative for the predecessor**.
* Under the predecessor freeze **no final K5 adjudication occurred, no publication closeout occurred, and no
  scientific computation occurred.** Both predecessor commits stay immutable (checker H01).
* **R1 is a new prospective repair in a new namespace** (`level4/closure_proofs/p5y_k5_partial_closeout_r1/`), not a
  retroactive rewrite. It is authorized by the user's "K5 PARTIAL Closeout Successor Freeze R1" (2026-09-27).
* Authoritative inputs unchanged: route audit r1 (`level4/closure_proofs/p5y_k5_tail_route_audit/ROUTE_AUDIT_R1.md`,
  802be11e) and its review (`level4/closure_proofs/p5y_k5_tail_route_audit/review/ROUTE_AUDIT_R1_REVIEW.md`,
  2f36352e, ROUTE_AUDIT_ACCEPTED). The route-audit conclusion is fixed: no prospective K5 scientific expansion under
  present governance; no new 306/307/308/309 or joint campaign; no new floor or limb; no r6.

### Repair matrix — every item of the predecessor freeze review

| review item | predecessor issue | successor repair | verification |
|---|---|---|---|
| **B1** | §7/§10 stated a stale cross-ref K1/P5Y picture ("latest SR K1 artifact da79fe1f … K1 not decided"); §14 K4 ref stale; no forcing correction | §5 reconstructs K1, K2/K3, K4, K5, SR K1, SR K5 and P5Y **from current ref tips**; Class A/B separation; binding facts judged by state tokens with a frozen drift rule; mandatory re-reads before adjudication and before publication; K1/K4/P5Y rows required in the adjudication table | checker `--xref` (XB1–XB6) → `evidence/XREF_SNAPSHOT_R1.json`, re-run as `PREADJUDICATION_XREF_R1.json`, `PREPUBLICATION_XREF_R1.json` |
| N1 | decision-rule limbs judgment-based; `K5_CLOSED` ↔ `K5_DECLARED_CLOSED` conflated | §6 makes each limb a lookup of a committed, accepted artifact's own recorded verdict; `K5_CLOSED` (CUSUM-scoped verdict) is distinguished from the K5-wide flag `K5_DECLARED_CLOSED` | §6 text; review |
| N2 | SR-refs pickaxe matched one spelling, missed in-place edits, self-exempted the branch | ERE multi-spelling `-G` over all refs (catches in-place edits); exemption only by exact commit id (a3547b9b, e8680998) or by changed-file path inside the three audit/closeout namespaces; plus per-tip blob identity of both SR-status files | XB5 |
| N3 | SR K5 rationale carried only "needs SR K1 records" | §11 carries both recorded prerequisites, incl. the missing SR order-3 producer (`AUX3_SR_FEASIBILITY_FAIL`) | H03 pins the exact K5_STATUS line |
| N4 | "C4 Condition 2 forbids 'none can' / 'cannot be excluded'" misattributed | §7 (308) attributes each phrase to its source | review |
| N5 | reconstruction omitted C1, Campaign B, C11 negative history | §7 carries them | H02 pins MARGINAL / STOPPED / INFEASIBLE / EXECUTION_INVALID |
| N6 | publication controls thin (no post-publication review; substring blocklist; placement unchecked; README unscanned; P01 namespace-wide; ignored files invisible) | exact per-phase allowlist incl. ignored files (P01); placement (P03); clause-aware scan with fixtures (T01, W01) covering README; a fresh **publication conformance check** before the publication commit (§13 step 7) | checker P01, P03, T01, W01; F01 |
| N7 | "verbatim" helper copies not byte-exact | stated as "code-identical (AST, docstrings ignored)" and verified | L03 |
| N8 | §12 "every role distinct from the author" vs "publication by the author" | §13 distinguishes reviewer/adjudicator roles (fresh, not the author) from the publication author (the closeout author) | text |
| N9 | no PARTIAL / INCONCLUSIVE / OPEN mapping | §6.1 defines each from repository usage and states their relation | text |

### Retained predecessor repairs N4.1–N4.9 (route-audit r1 review)

N4.1 any committed authoritative evidence (§3) · N4.2 administrative checks vs forbidden science (§4) · N4.3
`K5_INCONCLUSIVE` is a CUSUM-K5-level verdict, never per cell (§6) · N4.4 failed/unresolved cells are not by
themselves evidence against H3a, and the P5Y consequence (§8) · N4.5 "No route that closes 307 has been certified."
(§7) · N4.6 C4 Condition 3 verbatim for 308 (§7) · N4.7 seven deferred research directions, real order-3 risk HIGH
(§9) · N4.8 "current authoritative coverage map" (§10, §12) · N4.9 SR K5 across refs, out of scope (§11).

## 1. Scope

* **Object:** the K5 obligation for the CUSUM detector, D = CUSUM, m ∈ {1, 2, 3, 5}, frozen CUSUM K1 cover cells 0–309
  meeting (0, 2] (`level4/closure_proofs/p5y_postk1_precompute_resolution/K5_TARGET_AND_THIRD_ORDER.md` :89), and in
  particular the disposition of m = 5 cells 306–309 (the only open cells of the current authoritative map). Every
  other CUSUM (m, cell) is carried as r5 records it.
* **Out of scope:** SR K5 (carried, not adjudicated, §11); K1, K2, K3, K4 and any P5Y assembly (reported from current
  ref tips, not adjudicated, §5, §8); AWS SR/PS1.

## 2. Question

> Given the current authoritative evidence and the accepted prospective route audit, what is the correct current
> disposition of CUSUM K5 and of each of cells 306–309?

Not "can K5 somehow be closed?". The closeout records the state; it does not improve it.

## 3. Allowed evidence (N4.1) and fact classes

* **Allowed:** any committed artifact on this branch at or before the freeze commit, and committed artifacts on other
  refs read **at their current tips** (§5). Every citation carries its historical governance status and evidence
  type (certified CI/EX, diagnostic NE, uncertified Monte-Carlo / COUNTERFACTUAL_ONLY). No new scientific evidence;
  no uncommitted artifact is load-bearing; uncertified evidence may be reported, never used for an authoritative
  exclusion or closure.
* **Forbidden:** anything under a C11R quarantine directory; any original or independent D1/D2 value; session
  transcripts.
* **Class A — frozen local facts** (pinned normally): K5 historical evidence, r5, cell dispositions, route-audit
  records, the rejected predecessor closeout, this protocol and its checker.
* **Class B — external / cross-ref facts:** everything in §5. Each is classified binding or informational in §5.

## 4. Administrative checks versus scientific computation (N4.2)

**Allowed (administrative / mechanical):** git ancestry, rev-parse, cat-file, diff, log (incl. pickaxe), for-each-ref,
status, reflog; blob/file identity and hashes; grep and `sed -n`; ref enumeration and ref-tip inspection; the
value-free hashed leak scan; JSON/schema structure checks; citation-existence, review-format, allowlist, additive and
placement checks; the clause-aware wording scan; the research-synthesis document verifier
(`docs/research_synthesis/verify_synthesis.py --no-diff-check`, blob `d2411ab805e3bc58ba1d77a6894c3fa67da005fd`) in the
publication phase. **The only code run by this closeout is `code/closeout_checks_r1.py` (stdlib + read-only git, no
campaign import; its scan helpers are code-identical to cited sources, check L03), that verifier, and git.**
Reviewers and the adjudicator may run the checker with `--out` outside the repository.

**Forbidden (scientific):** any Γ evaluation; any target-equivalent proxy (margins, factors, bisections, knockouts, Λ
bounds, replays, calibrations); any new interval/certificate calculation; supply search; constant optimization;
Monte-Carlo science; theorem/proof computation producing new K5 evidence; running any campaign producer, certifier,
verifier or driver.

## 5. Current cross-ref P5Y state — reconstructed from current ref tips (B1)

Observed at freeze time by `code/closeout_checks_r1.py --xref` (`evidence/XREF_SNAPSHOT_R1.json`; observation
timestamp inside). Tips were read with `git for-each-ref` / `git rev-parse <ref>` and each state from the artifact **at
that tip**, never from a remembered commit id or a branch name.

| obligation | ref | current tip (informational) | authoritative artifact at tip | state read | class |
|---|---|---|---|---|---|
| K1 (CUSUM + SR successor line) | `refs/heads/p5y-k1-successor-final-assembly` (= `refs/remotes/origin/…`) | 7d5cf02b7f4b29439c59d803fe90ce62bc0841da (2026-09-27 14:25:06 +0900; reflog: da79fe1f final assembly fetched 14:19:59, adjudication committed 14:25:06) | `level4/closure_proofs/p5y_k1_successor_final_adjudication/evidence/FINAL_ADJUDICATION.json` | `k1_successor_verdict` K1_SUCCESSOR_CLOSED; `k1_scientific_line` CLOSED_BY_LATER_SUCCESSOR_CAMPAIGN; `residual_blockers` NONE; `cusum_successor_science` PASS; `sr_successor_science` PASS; historical P5-K1 verdicts PARTIAL preserved | **binding (XB1)** |
| SR K1 | same K1 successor adjudication (covers SR: `sr_bridge` 6/6, `historical_sr_ps1` 369/369); earlier ref `refs/heads/p5y-k1-final-evidence` 15e70072 (PS1 AWS-only assembly, 2026-09-25) | — | as K1 | CLOSED as part of K1 | binding via XB1; 15e70072 informational |
| K2 / K3 | `refs/heads/p5y-k2-k3-final-closure` (= origin) | df7038374a80cc94d7293ce08195fae21fe8dc0f (15:03:06 +0900) | `level4/closure_proofs/p5y_k2_k3_final_countersignature/FINAL_COUNTERSIGNATURE.json` | independent countersignature K2 PASS, K3 PASS; K2 CLOSED, K3 CLOSED | **binding (XB2)** |
| K4 | `refs/heads/p5y-k4r1-final-closure` (= origin) | e88a288588e08d13c32ed009c8dc42f5982ff8a1 (22:13:19 +0900) | `level4/closure_proofs/p5y_k4r1_final_adjudication/K4R1_FINAL_VERDICT.json` | `K4R1_SUCCESSOR_VERDICT` CLOSED; `K4_SCIENTIFIC_LINE` CLOSED_BY_LATER_SUCCESSOR_CAMPAIGN; `K4_RESIDUAL_BLOCKERS` NONE; historical K4 NOT_CLOSED (K4_INCONCLUSIVE_K1_RECORDS, bc4ba08e) preserved | **binding (XB3)** |
| K4 history | `refs/heads/p5y-k4-frozen-execution-r1` bc4ba08e; `refs/heads/p5y-k4r1-nearzero-successor` b5b4c917 (reflog 0dc949b5 → 93d82c87 20:45:07 → 8928b8f1 FREEZE 21:17:19 → b5b4c917 result 21:17:46; candidate 5d33363c rejected at r4) | — | — | historical / execution refs | informational |
| P5Y (recorded) | K4 tip, field `P5Y_STATE` | e88a2885 | `K4R1_FINAL_VERDICT.json` :51–57 (and README :41) | K1 CLOSED_BY_LATER_SUCCESSOR_CAMPAIGN · K2 CLOSED · K3 CLOSED · K4 CLOSED_BY_LATER_SUCCESSOR_CAMPAIGN · **K5 OPEN** · **P5Y NOT_YET_CLOSED** | **binding (XB4)** |
| SR K5 | all refs (§11) | — | `level4/closure_proofs/p5y_k5_remaining_cell_closure/K5_STATUS.md` :52 (one version, blob d212f0d5, on every ref carrying it); readiness audit :13 (blob 597c9b2d) | **NOT STARTED** | **binding (XB5)** |
| K5 / coverage elsewhere | all refs | — | pickaxe for structured K5-closed / P5Y-closed records (`K5_DECLARED_CLOSED` YES/true, `"K5": "CLOSED…"`, `K5 = CLOSED`, `K5 CLOSED_BY…`) and any `*COVERAGE_MAP_R6*` path | none (a trial with a bare "K5 CLOSED" pattern also hit two meta-mentions — a C2 review sweep list, d6a4def5, and a readiness-audit test's forbidden-string list, e8680998 — inspected and not closure records; the frozen pattern is the structured one) | **binding (XB6)** |
| this branch | `refs/heads/p5y-k5-tail-c11rd-d1d2-extension` | the freeze commit | Class A | — | informational |

**Statement (verified above, not assumed):** K1, K2, K3 and K4 are recorded closed at their current ref tips, and **K5
is the only remaining open P5Y obligation relevant to this closeout.** The predecessor statement that P5Y waits on SR
K1 is withdrawn: SR K1 is closed within the K1 successor adjudication.

### 5.1 Cross-ref drift policy (prospective)

* **Informational (Option 1):** tip ids, dates, subjects and the K4/K1 history refs are an *observed-at-freeze*
  snapshot. Their later movement does not invalidate this closeout.
* **Binding (Option 2): XB1–XB6** — the states the P5Y consequence (§8) and the SR K5 statement (§11) rely on. They are
  compared **by state tokens at the ref's current tip, not by tip id**.
* **Mandatory re-reads:** immediately before the adjudicator starts (`evidence/PREADJUDICATION_XREF_R1.json`) and
  immediately before the publication commit (`evidence/PREPUBLICATION_XREF_R1.json`), by `closeout_checks_r1.py
  --xref`.
* **Outcome:** a moved tip whose artifact yields identical tokens is **COMPATIBLE_DRIFT** — recorded in the re-read
  file and in the adjudication/publication, and the closeout continues. Any token change, a missing ref, a missing or
  unparseable artifact, or any XB5/XB6 finding is **INCOMPATIBLE → STOP** (no adjudication / no publication; a new
  authorization is needed). The CUSUM K5 verdict itself depends on Class A only.

## 6. Vocabulary and the prospective decision rule (N4.3, N1)

### 6.1 OPEN / PARTIAL / K5_INCONCLUSIVE — repository definitions first (N9)

| term | level | repository usage (definition source) | meaning here |
|---|---|---|---|
| **OPEN** | a cell; also a P5Y obligation | coverage maps: `per_m.<m>.open_ranges` (r5); P5Y records: `"K5": "OPEN"` (`K4R1_FINAL_VERDICT.json` :56) | a cell is OPEN iff it is in r5's `open_ranges` (not in the adopted pass set of the current authoritative coverage map); an obligation is OPEN iff not recorded closed |
| **PARTIAL** | coverage status of CUSUM K5 | `K5_STATUS.md` :4–5 (`K5_STATUS (CUSUM) = PARTIAL`, `K5_COVERAGE_COMPLETE = NO`); r5 `K5_COVERAGE_COMPLETE` false | only a subset of the required (m, cell) pairs is established; it describes coverage, not a verdict. (Historical P5/P5X/P5Y-K1 "PARTIAL" verdicts are different objects and are not re-used here.) |
| **K5_INCONCLUSIVE** | adjudicated verdict for the CUSUM K5 object | E01 :91 decision rule ("otherwise unresolved cells ⇒ `K5_INCONCLUSIVE`") | the current framework does not establish the required K5 closure for all required cells, and the evidence does not justify reading unresolved cells as mathematical refutation |

**Relation (not interchangeable):** coverage PARTIAL (some cells OPEN) with no certified counterexample ⇒ the §6.2 rule
yields `K5_INCONCLUSIVE`; the P5Y obligation K5 then remains **OPEN** (recorded vocabulary). No term is applied at
another term's level.

### 6.2 Rule (applied to CUSUM K5, mechanically, in order)

1. **`K5_FAIL_MATHEMATICAL`** iff a committed artifact **whose own recorded verdict is accepted** records either a
   certified `R'''_cell.hi < 0` on a CUSUM cell containing 0 (E01 :91) or a declared refutation of H3a for
   (CUSUM, m) (the counterexample standard of
   `level4/closure_proofs/p5y_k5b_independent_countersignature/README.md` :236–238). Mechanical lookup: no such
   artifact ⇒ the limb does not fire.
2. **else `K5_CLOSED`** iff (a) r5 records `K5_COVERAGE_COMPLETE = true` **and** (b) a committed accepted adjudication
   records CUSUM K5 closed. Mechanical lookup of (a) and (b).
3. **else `K5_INCONCLUSIVE`.**

`K5_CLOSED` here is the CUSUM-scoped verdict token (repository usage: C11R adjudication :144); it is **not** the
K5-wide flag `K5_DECLARED_CLOSED` (countersignature README :20), which covers SR as well and is not set by this
closeout under any outcome. No "failed" verdict is invented; `K5_INCONCLUSIVE` is never applied to a cell.

**Pre-freeze reconstruction (non-binding; the adjudicator re-derives it):** limb 1 does not fire — the only certified
R''' evidence on the CUSUM cell containing 0 is `level4/closure_proofs/p5y_k5_cusum_first_real_probe_result/RESULT.md`
(`FIRST_CELL_SUPPORTED_ALL_M`, certified lower bounds on R'''(0) positive for every m), and no committed artifact
declares H3a refuted; limb 2 does not fire — r5 `K5_COVERAGE_COMPLETE = false`, m = 5 open [[306, 309]]; hence
`K5_INCONCLUSIVE`.

## 7. Cell dispositions (Class A; the adjudicator confirms or corrects)

**Cell 306 — facts coexist; none collapses into one word.**
* Scientific: **closes under I1's supply** — Γ(5, 306; S_I1) = −0.030469257709306738, C2 clause
  (`level4/closure_proofs/p5y_k5_tail_c2_closure/evidence/adjudication/C2_ADJUDICATION.md` :47; C2
  PARTIALLY_ADOPTED [305]; reproduced exactly by the C12-R2 control).
* Scientific: **I2's own supply does not certify closure** — Γ(5, 306; S_I2) = +0.005159101140006536, sealed once
  (276f4d41); `level4/closure_proofs/p5y_k5_tail_c12r2_cell306_adoption/review/C12R2_EXECUTION_REVIEW.md`
  EXECUTION_ACCEPTED (1173670f). Non-certification, not disproof.
* Trust condition: **N9 CLOSED** — `level4/closure_proofs/p5y_k5_tail_c11rd_d1d2_extension/adjudication/ADJUDICATION_C11RD_N9.md`
  (7d67989d), `level4/closure_proofs/p5y_k5_tail_c11rd_d1d2_extension/review/C11RD_ADJUDICATION_REVIEW.md`
  ADJUDICATION_ACCEPTED (fb237288).
* Governance: **floor r2 adoption criterion not met** — base TRUE; F1′ (a)–(c) TRUE, (d) FALSE (closure disagreement);
  F2 FALSE as published by C2 §K (Γ at ×1.25 = +0.029163293; uniform-A margin 1.1277; C2 adjudication :65, :474–478);
  `level4/closure_proofs/p5y_k5_tail_c12r2_cell306_adoption/adjudication/C12R2_ADOPTION_ADJUDICATION.md`
  **CELL306_NOT_ADOPTED** (9c2cbf21); `level4/closure_proofs/p5y_k5_tail_c12r2_cell306_adoption/review/C12R2_ADJUDICATION_REVIEW.md`
  **ADJUDICATION_ACCEPTED** (c5324a78).
* **Disposition: OPEN, NOT ADOPTED.**

**Cell 307 — "No route that closes 307 has been certified."**
* Certified supplies evaluated at 307 did not close it: C2 D4 (C2 adjudication :48, Γ positive) and the C3 D′ mixed
  supply (`level4/closure_proofs/p5y_k5_tail_c3_closure/evidence/adjudication/C3_ADJUDICATION.md` :349; C3 REJECTED
  as a campaign). Earlier failed attempts: C1 deflation registry **MARGINAL** (stopped before freeze), Campaign B
  routes **MARGINAL / INFEASIBLE**, C11's single-e constant for 307 **EXECUTION_INVALID** (a failed corroboration, not
  a certification).
* Blocker structure: second- and third-order terms (A1, A2) are material — with A1 = A2 = 0 it closes at the certified
  A0, so A0 is not its blocker (C3 :349; `level4/closure_proofs/p5y_k5_tail_c4_exhaustion/evidence/adjudication/C4_ADJUDICATION.md`
  :288–290); no committed closing supply; the two-implementation limb F1′ is **unavailable** (no second-implementation
  certification for 307; floor r2 spec :193).
* Reported, not load-bearing: C9's α projection 1.098807×–1.137406× (COUNTERFACTUAL, uncertified; C9
  EXECUTION_BLOCKED_ON_RUNTIME_AND_AUTHORIZATION); C8 factors COUNTERFACTUAL_ONLY (C5-T clause).
* UNKNOWN: every route not certified. No impossibility is claimed. **Disposition: OPEN.**

**Cell 308**
* Ruled out (certified, EX): improving only the second- and third-order terms does not suffice at the certified A0 —
  knockout A1 = A2 = 0 leaves Γ = +0.039568 (C3 :350; C3-N4). Earlier: C1 and Campaign-B routes MARGINAL.
* **C4 Condition 3, verbatim** (C4 adjudication :534–537):

  > at `A0 = 4.311`, the Monte-Carlo value of `Λ₃₀₈`, closing cell 308 still requires an **18.2× reduction of
  > `(A1, A2)`**; at `A0 = 4.375229` it is impossible at any `(A1, A2)`. C4-N3 stands and is binding: nothing licenses
  > "cell 308 is closable".

* C4's status wording (C4 verdict text :510–512): "operator-level route not excluded", not "cannot be excluded".
  (Attribution corrected per the predecessor review N4: C4 Condition 2, :527–533, bars quoting the Phase-3 sentence
  "the honest answer is that none can" and the `E[tau] < infinity (Lemma T)` citation.)
* Uncertified, reported, **not authoritative**: 2,000,000-path Monte-Carlo evidence at ~65 standard errors suggests no
  lower-bound route will exclude 308; not an exclusion. No certified upper bound on Λ₃₀₈ exists.
* UNKNOWN: everything not ruled out. Nothing licenses "308 is closable"; nothing establishes the opposite.
  **Disposition: OPEN.**

**Cell 309**
* Refuted **within scope only** (CI + EX), in C4 Condition 1's words (C4 adjudication :522–524): the uniform-A0
  atom-constant family, at cell 309, at m = 5, against the frozen measurement inputs and the frozen TC-T / K5-B
  consumer; strengthened by C7's certified Λ₃₀₉ ≥ 3.586306094
  (`level4/closure_proofs/p5y_k5_tail_c7_e2_lambda309/README.md`, ACCEPTED_WITH_CONDITIONS), which exceeds the
  C5-T-clause ceiling 3.266416 by 9.79 % (C8 adjudication, ACCEPTED_WITH_CONDITIONS). Earlier: C1/Campaign B
  MARGINAL.
* Not generalized: C4 :503 — not a statement that 309 is unclosable.
* UNKNOWN outside the scope: sup-norm routes; finer cover; real order-3; assembly/clause tightening; residual-specific
  routes; other independently justified future theory. **Disposition: OPEN.**

**Other cells:** CUSUM m ∈ {1, 2, 3} cells 0–309 and m = 5 cells 0–305 as r5 records them; not re-adjudicated.

## 8. H3a and the P5Y consequence (N4.4)

* **H3a:** a failed or unresolved K5 cell is **not, by itself, evidence against H3a**
  (`level4/closure_proofs/p5y_k5b_independent_countersignature/README.md` :236–238: a failed recurrence,
  `K5_INCONCLUSIVE` or a failed cell, "including cell 309 or the m = 5 tail", may not be claimed as evidence against
  H3a; refutation needs an independently proved counterexample, e.g. a certified sup R''' < 0). Theorem K5-B is
  sufficient-only (`level4/closure_proofs/p5y_k5_feasibility/K5_GLOBAL_BRIDGE.md`). Preserved distinction: *evidence
  against a hypothesis* (a certified counterexample — none committed) versus *inability to certify a sufficient
  condition* (the open cells). **No support is claimed either:** this closeout asserts H3a for no (D, m); r5 records all
  CUSUM cells passing for m ∈ {1, 2, 3}, but no accepted artifact assembles the K5-B premise list (countersignature
  README §10) into an H3a claim for any (D, m).
* **P5Y consequence (binding on XB1–XB6 at re-read time):** with K1, K2, K3, K4 recorded closed at current tips, K5 is
  the only remaining open P5Y obligation. A CUSUM verdict of `K5_INCONCLUSIVE` does not close K5; independently, SR K5
  is NOT STARTED, so K5 is not closed on its SR component either (a statement about SR's own record, not an inference
  from CUSUM). The recorded P5Y vocabulary therefore stays **K5 OPEN, P5Y NOT_YET_CLOSED** (`K4R1_FINAL_VERDICT.json`
  `P5Y_STATE`). K5 is upstream of T9/T10 and Level-4 global closure in the recorded dependency DAG
  (`level4/closure_proofs/p5y_postk1_frontier/P5Y_POST_K1_DAG.md` :60, :75, :97–102). This closeout issues **no P5Y
  verdict** and invokes no P5Y assembly rule beyond these recorded states.

## 9. Deferred research (N4.7) — optional, not required for this closeout, neither failed nor completed

Reopenable only under fresh, separately authorized, prospective protocols that freeze any theorem, floor extension or
admissibility ruling before any tail recomputation (C2 Condition 1).

| direction | cells | route-audit r1 label | prerequisites | scientific risk |
|---|---|---|---|---|
| RSO theory (residual-specific order-0 majorant; at most the `A0·f_H` part of `A0·p2`) | 307–309 | DEFER (research item) | theorem; U1 host; U2 admissibility ruling; U3 floor extension for any adoption | HIGH |
| assembly / clause tightening (σ₃, σ₄, env4, f_G) | 307–309 | DEFER (research item) | theorem(s); U3 for adoption | HIGH |
| real order-3 R stage (R-a / R-b) | 307–309 | DEFER | N1, N3, N5, N7; guard DENY; new real addresses; host | **HIGH** (C2 R-stage §2 models realistic reach at 307 only; Campaign B T2 closed 0/5, INFEASIBLE) |
| sup-norm tightening (R5) | 307–309 | DEFER | replay + new sup routine; U1; U2 | HIGH |
| cover refinement (B1) | 309 (+) | DEFER | new K1 addresses; new provenance chain | MEDIUM |
| general operator-tuple search (R-E1g) | 307, 308 | INSUFFICIENT_EVIDENCE | cell-independent certifier strategy; U1 | HIGH |
| two-implementation limb (R-F1′) | 307 | DEFER | I2 six-constant certification for 307 + an I1 that closes | HIGH |

Rejected *as actions* by r1 (not scientific failures), unchanged: R-α, R-I2-alone (needs no host; rejected on
result-chasing and evidence), Floor-307, X308. Carried corrections: C8's factors use the C5-T clause whereas r2's
adoption quantity uses C2's consumer path; U2 is an open admissibility question (C6 Condition 10); U3 is r2's ordinary
prospective path for 307–309 (floor r2 spec :202–203); C8 erratum E1 records rule 1's false premise; stopping preserves
rather than gains information (route-audit r1 review N1a).

## 10. Coverage — no adoption, no mutation

No cell is newly adopted. r5 (`level4/closure_proofs/p5y_k5_tail_c2_closure/evidence/coverage/K5_COVERAGE_MAP_R5.json`,
blob `f978eeb6b41188eabaf3c6d590c9178d711f1ce6`) remains the **current authoritative coverage map**. No r6 is created;
no coverage entry is rewritten. Any step that would mutate coverage ⇒ STOP.

## 11. SR K5 (N4.9, N3)

* **State: NOT STARTED** on every ref: `K5_STATUS.md` :52 records "NOT STARTED: needs SR K1 records, plus an SR
  order-3 producer (`AUX3_SR_FEASIBILITY_FAIL` on record)"; one version of that file (blob d212f0d5) exists on every ref
  carrying it, and one version of the readiness audit (blob 597c9b2d; :13 `K5_SR_K1_INPUTS_EXIST = NO`); no commit on
  any ref adds or edits SR-K5 status text beyond a3547b9b, e8680998 and the audit/closeout namespaces (XB5).
* **Prerequisites as recorded:** (i) SR K1 records — now satisfied in substance by the K1 successor adjudication (XB1),
  so the first recorded rationale is stale; (ii) **an SR order-3 producer — still missing**
  (`level4/closure_proofs/p5y_k1_sr_o9_aux3_successor/config/AUX3_SR_RECORD.json`, `AUX3_SR_FEASIBILITY_FAIL`). SR K5
  therefore remains NOT STARTED for a recorded reason.
* **Scope:** this adjudication concerns the CUSUM K5 disposition only. SR K5 is carried unchanged, is **not**
  adjudicated here, is **not** counted as a CUSUM K5 blocker, and is **not** declared complete. No inference is made
  from CUSUM K5 to SR K5. A contradictory SR K5 state at any re-read ⇒ STOP (XB5).

## 12. Current-versus-final language (N4.8) and the wording scan

Use "current authoritative state" / "current authoritative coverage map". The closeout finalizes the current project
phase under current governance; it does not finalize mathematics and bars no separately authorized research.

Publication-facing text (the `publication/` document, the namespace README, and the lines added to the three public
files) must pass W01: clause-aware detection of banned **positive** assertions (finality, exhaustion, impossibility,
H3a refuted or established, "306 failed", K5/CUSUM-K5/SR-K5/P5Y closed, unscoped refutation of 309), where a match is
allowed only if a negation cue precedes it inside the same clause. T01 regression fixtures (prohibited / negated /
scoped) run in every phase; e.g. "not a statement that 309 is unclosable" and "not evidence against H3a" pass,
"K5 is not closed, and H3a is established" fails.

## 13. Chain, roles, gates, and the exact artifact allowlist

**Roles.** The freeze reviewer, the adjudicator, the adjudication reviewer and the publication-conformance checker are
four distinct fresh contexts, none of them the closeout author; each is read-only on the repository (git, grep,
`sed -n`, and the frozen checker with `--out` outside the repository) and writes its verdict on line 2 exactly. The
**publication author is the closeout author**, writing only from the accepted adjudication. No reviewer output is read
before its completion notification.

1. **Freeze** — one narrow commit adding exactly: `README.md`, `protocol/K5_PARTIAL_CLOSEOUT_PROTOCOL_R1.md`,
   `code/closeout_checks_r1.py`, `evidence/PREFREEZE_CHECKS_R1.json` (all PASS), `evidence/XREF_SNAPSHOT_R1.json`
   (PASS).
2. **Freeze review** → `review/CLOSEOUT_FREEZE_REVIEW_R1.md`, line 2 `CLOSEOUT_FREEZE_ACCEPTED` /
   `CLOSEOUT_FREEZE_REJECTED`; committed verbatim alone. **REJECTED ⇒ preserve and STOP; no repair in this round; no
   adjudication; no publication.**
3. **Pre-adjudication re-read** → `evidence/PREADJUDICATION_XREF_R1.json` (§5.1); INCOMPATIBLE ⇒ STOP.
4. **Final adjudication** → `adjudication/K5_CUSUM_FINAL_ADJUDICATION_R1.md`, line 2 exactly one of `K5_CLOSED`,
   `K5_FAIL_MATHEMATICAL`, `K5_INCONCLUSIVE` per §6.2; must separate scientific non-certification, scientific
   falsification, governance non-adoption and unresolved future research; must contain a findings table
   *item | authoritative finding | evidence | consequence* with rows **306, 307, 308, 309, r5, r6, K1, K4, P5Y, SR K5,
   CUSUM K5, H3a**, the K1/K4/P5Y/SR rows taken from the step-3 re-read (recording any COMPATIBLE_DRIFT); STOP and
   say so if computation would be needed. Committed verbatim alone (with the step-3 file).
5. **Adjudication review** → `review/K5_ADJUDICATION_REVIEW_R1.md`, line 2 `K5_ADJUDICATION_ACCEPTED` /
   `K5_ADJUDICATION_REJECTED`; committed verbatim alone. **REJECTED ⇒ preserve and STOP.**
6. **Pre-publication re-read** → `evidence/PREPUBLICATION_XREF_R1.json`; INCOMPATIBLE ⇒ STOP.
7. **Publication** (only if step 5 ACCEPTED): the author writes the §14 artifacts (uncommitted); the checker
   `--phase publication` must PASS; a fresh **publication-conformance check** reads the uncommitted diff against the
   accepted adjudication and this protocol → `review/PUBLICATION_CONFORMANCE_R1.md`, line 2 `PUBLICATION_CONFORMANT` /
   `PUBLICATION_NONCONFORMANT`. CONFORMANT ⇒ commit the artifacts with the conformance review and
   `evidence/PUBLICATION_CHECKS_R1.json`. NONCONFORMANT ⇒ commit only the conformance review, leave all publication
   files unchanged, STOP.

**Exact allowlist** (checker P01; tracked, untracked and ignored paths; anything else ⇒ failure): the step-1 files;
from the adjudication phase also `review/CLOSEOUT_FREEZE_REVIEW_R1.md`, `evidence/PREADJUDICATION_XREF_R1.json`,
`adjudication/K5_CUSUM_FINAL_ADJUDICATION_R1.md`; from the publication phase also `review/K5_ADJUDICATION_REVIEW_R1.md`,
`evidence/PREPUBLICATION_XREF_R1.json`, `publication/K5_CUSUM_CLOSEOUT_STATUS.md`,
`evidence/PUBLICATION_CHECKS_R1.json`, `review/PUBLICATION_CONFORMANCE_R1.md`, and the three public files of §14 — all
paths relative to `level4/closure_proofs/p5y_k5_partial_closeout_r1/` except the public files.

## 14. Permitted publication artifacts and required wording

| id | path | permitted change |
|---|---|---|
| P-A | `level4/closure_proofs/p5y_k5_partial_closeout_r1/publication/K5_CUSUM_CLOSEOUT_STATUS.md` | new: status brief, coverage explanation, limitations, research outlook, evidence/provenance table, reproducibility index |
| P-B | `README.md` (repository root) | one additive block "Current K5 status (CUSUM, updated 2026-09-27)" between "## Current successor status (PS1)" and "## Limitations and negative results"; zero deleted/modified lines (P02, P03) |
| P-C | `docs/research_synthesis/README.md` | one block "Current K5 successor status (additive update)" appended at the end; zero deleted lines |
| P-D | `docs/research_synthesis/LIMITATIONS_AND_OPEN_ITEMS.md` | one section "P5Y successor: CUSUM K5 open items (additive, 2026-09-27)" appended at the end; zero deleted lines |
| P-E | `level4/closure_proofs/p5y_k5_partial_closeout_r1/README.md` | chain index update |

No historical artifact is edited; no earlier verdict rewritten. Required content: (A) the accepted CUSUM K5 verdict,
exactly, and — if `K5_INCONCLUSIVE` — that it is a certification/adoption conclusion under the current framework,
not proof that a mathematical statement is false; (B) 306: closure certified under I1, adoption not reached under
floor r2 because I2's own supply did not certify closure and F2 had already failed; (C) 307–309 in §7's scoped
wording with the negative history visible; (D) r5 current authoritative map, no r6; (E) K1 and K4 as recorded at the
re-read tips, the resulting recorded P5Y state, SR K5 separate and out of scope; (F) H3a not refuted by unresolved
cells, and no claim of support; (G) deferred research optional and reopenable.

## 15. Historical and forensic preservation

Historical namespaces — C1 and Campaign B, C2–C12-R2 (incl. C11, C11R, C11RD / N9), floor r2, the cell-306
adjudication, route-audit r0/r1 and reviews, **and the rejected predecessor closeout** — stay byte-identical to the
base 591b4394 (H01); pinned verdict tokens stay present (H02). Governance refs `refs/c11rd/r1-execution-consumed`,
`refs/c12r2/cell306-target-consumed`, `refs/c12r2/cell306-pending-result`, seal 276f4d41, blob b83cc6f5 and commit
def4e453 are retained (G01, G02); nothing is garbage-collected. External K4 ref movements are recorded in §5 as
observations of shared-repository activity, not attributed to this closeout.

## 16. Stop conditions

Starting state differs; any checker check fails; freeze review REJECTED; any re-read INCOMPATIBLE; the adjudication
needs computation or its verdict does not follow mechanically from §6.2; adjudication review REJECTED; publication
NONCONFORMANT; any proposed adoption or coverage mutation; contradictory SR K5 state; leak-scan hit; any change to a
historical namespace; any need to push, merge or synchronize main; any AWS/Vultr contact; any nonzero §17 entry.

## 17. Computation declaration (reported at every checkpoint)

New Γ evaluations — 306: **0**, 307: **0**, 308: **0**, 309: **0**; target-equivalent proxy evaluations: **0**; new
scientific Monte-Carlo runs: **0**; new load-bearing intervals/certificates: **0**. Any nonzero ⇒ STOP and report the
contamination.
