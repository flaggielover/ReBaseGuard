# Cell-308 MB formal prospective closure campaign (r1): protocol

**Status: PRE-FREEZE DRAFT p0.** Becomes the frozen protocol at the freeze commit. Nothing in it authorizes a
target evaluation; only the grant (§10 step 4) does.

## 1. Scope and authority

* One exactly-once, **closure-only** evaluation of CUSUM K5 cell 308 (m = 5) under route R-MB (Theorem MB r1), after
  freeze → official qualification → independent qualification review (QUALIFICATION_ACCEPTED) → grant.
* **Closure is not adoption.** No floor r2 change, no r6, no adoption, no K5 or P5Y closure, no main-branch
  integration, no push.
* **User ruling (incident review C4).** The grant must record the user's explicit CLOSURE_ONLY ruling for a
  profile-transport consumer on cell 308, taken with incidents 01–03, H4.3b, the coordinator disclosures I-a…I-e and
  E1′, and the incident-independence review in view. Without that record the grant is not written and the campaign
  STOPS before the grant.
* Research provenance: `level4/closure_proofs/p5y_k5_cell308_research/` (theory, streams, reviews, audit, ledger).

## 2. Scientific object and closure criterion

* **Theorem MB r1** (`theory/THEOREM_MB.md`, a byte copy of the research file reviewed by REVIEW_THEOREM_MB_R1 and
  corrected per its C1–C6): Γ_MB = g_hi + P*_B is a certified upper bound on sup_{e∈E} g_5(e) on the cover cell E of
  cell 308, from the committed TC-T inputs, block triples S_i on the C2 partition, and the TPT-B transport.
* **Criterion (the K5 criterion, unchanged):** a certified upper bound on sup_cell g that is strictly negative.
  Frozen form: **Γ_dec := g_hi + max(P*_B(primary), P_hi(independent)) < 0 in exact rationals.** Γ_dec = 0 does not
  close.
* **Independence wording (incident review C3):** "independent of target outcome" means temporal and parametric
  independence only. Motivational independence is not claimed. Result-chasing risk: MEDIUM–HIGH.

## 3. Decisions (each fixed by a target-free rule; design d1, research `streams/FORMAL/MB308_DESIGN_DRAFT.md`)

| # | decision | frozen value | reason |
|---|---|---|---|
| D1 | partition | N = max(1, ⌈(x_hi − x_lo)/(1/100)⌉) equal exact sub-intervals E_i of cell 308's cover interval (N = 11) | C2's rule, reused by the cell-307 campaign |
| D2 | hulls, pointwise drifts | B_i = outward 2^-20 dyadic hull of E_i; b_i = lo(B_i) ≤ lo(E_i), dyadic | pinned C1b needs dyadic drifts; Theorem M makes b_i valid on E_i |
| D3 | RLR block ladder | pinned `certify_degree(centre, d, BW_PW, e_r = radius)` on B_i, d ∈ (4, 6, 8), TIGHT_CT = BLOCK_LIGHT = True; Lemma Lad | the cell-307 Stage-1 rules P2–P4, unchanged |
| D4 | pointwise Λ ladder at b_i | C2b exact-scale N ∈ {20, 40, 80} (pinned `c2b_exact.certify`, persisted W) and C1b pointwise d ∈ {8, 10, 12}; U-candidates from certified upper rungs, L-candidates from certified lower rungs | stream A0 findings F1–F4 at non-target drifts; REVIEW_A0_CERTIFIER_R1 |
| D5 | admission of an upper rung into U_i | (i) its persisted certificate is VERIFIED by the independent verifier (C2b: `vd_pl`; C1b: `vd_verify`) within the frozen operation budget, and (ii) a certified lower rung of the **other** implementation exists with L_other ≤ U. REFUTED, or L_other > U for **any** certified upper rung (verified or not), ⇒ INCONSISTENT. No other-implementation lower rung ⇒ ALARM_UNAVAILABLE (rung not admitted). UNDECIDED ⇒ rung not admitted. C1b upper rungs with d > 6 are NOT_INDEPENDENTLY_VERIFIED and never admitted (verification infeasible in budget, VERIFIER_REPORT D7); they are computed for their Λ_lo only | R7; REVIEW_A0 C2; builder decision 1 (stricter reading accepted) |
| D6 | envelope | Ū_i = min_{j ≤ i} U_j over the pre-declared b_j only; a b_i without an admitted rung contributes nothing | Lemma M-U; review N8 |
| D7 | members of S_i | (1) S_I1, reproduced by the frozen consumer; (2) Dv′-M on REGISTRY_C1's and REGISTRY_C2's committed cell inputs with Abar := min(Abar, Ū_i), through the frozen `deflated_consume.atom_constants_r2`; (3) D14-M on the RLR ladder record of B_i with Ā′ = min(Ā_B, Ū_i), Lemma DM (D_lo′), A0 slot min(Ā′_eff, C_R); (4) Lemma G with C_R of B_i. S_i = componentwise min of the available members | dominance (charter rule 5); THEOREM_MB r1 §6 |
| D8 | missing certificates | absent members only weaken S_i; nothing is retried | fail-safe |
| D9 | consumer | TPT-B via `tptb_tail` on cell 308's committed TC-T inputs; pieces cut at every E_i end and at e0; gates C5 (E = [e0 − ρ, e0 + ρ] exactly), C6 (per-piece non-emptiness), G-R3b (per-r tuple and every block's profile polynomials equal `tuple_independent` exactly) | Theorem MB r1 §7; stream F3 |
| D10 | computed on the target | only: controls C-A and C-B (historical reproduction), Stage 1, the members and S_i, P*_B (primary) and [P_lo, P_hi] (independent), P*_B ≤ P_frozen(S_I1). **Never** P_TPT(S_I1), P_C5T(S_I1) or any other route value | brief §21; incident review C9 |
| D11 | workers, caps | 5 spawned workers; pre-marker cap 1800 s; per-job CPU caps and EVAL_CAP per §3.2; a job refuses unless its effective cap equals the declared cap | 307 rule; REVIEW_A0 C3 |
| D12 | primary vs independent | exact equality for every composition layer (F2); for P*_B the bracket rule P_lo ≤ P*_B(primary) (never a loose tolerance) | F2 open issue 3 |
| D13 | kernel drift map | kernel e = cover e (identity); all constants even (Lemma S, Theorem M) | THEOREM_MB r1 N6 |
| D14 | verification budgets | `vd_pl`: max_depth 12, max_boxes 10^6 per column job; `vd_verify`: max_boxes 200 000 per initial box, min_width 2^-40 (the verifiers' own defaults) | fixed before any target use |

### 3.2 Cap rule (frozen before any target computation; decoy runtime and status only)

**To be completed from the pre-freeze exploration** (decoy 297 full ladder, decoy 316 first three blocks; runtimes and
statuses only, incident review C7(b)). Rule (the 307 rule, extended): project cell 308's Stage-1 cost from the larger
decoy wall time per job kind and rung (RLR d4/d6/d8; C2b N20/40/80 including `vd_pl`; C1b d8/10/12), for 11 blocks and
11 pointwise drifts at 5 workers with longest-first scheduling; EVAL_CAP = max(6 h, ⌈2 × projection⌉); per-job CPU cap
= max(3 × largest decoy job CPU of that kind and rung, 1800 s).

## 4. Stage 1 (after the marker)

* S1a: RLR ladder on every B_i (D3).
* S1b: pointwise Λ ladder at every b_i (D4); every certificate persisted in memory with its sha256.
* S1c: independent verification of certified upper rungs (D5).
* S1d: admission and alarm (D5); INCONSISTENT ⇒ INDETERMINATE.
* S1e: envelope (D6), members and S_i (D7), each layer equal to the independent reconstruction F2
  (`streams/INDEP/mb_independent.py`) exactly; the RLR ladder also against `rlr307_independent`.
* A rung exception inside a pinned certifier is a non-certificate (recorded). MemoryError, OSError, worker death, a
  cap hit, a guard refusal and signals are execution failures (INDETERMINATE).

## 5. Controls, Stage 2 and decision

**Controls (before the marker; historical reproductions only; tripwires verified armed).**
* C-A: cell 308 under S_I1 through C2's frozen consumer reproduces C2's committed record exactly (Gamma_exact,
  A_exact, provenance, H_exact, M_after_exact, pass, per-supply records).
* C-B: `tptb_tail` reproduction gates with S_I1 at s = ρ (G-R1, G-R2, G-R4, G-CF) and G-R3b; no penalty other than the
  frozen one is computed.
* Either failing ⇒ CONTROL_FAILED, sealed, target **not** consumed, campaign STOPS.
* No file of this namespace reads anything under the research `history/recon/` (incident review C2).

**Stage 2.** TPT-B (D9) with the S_i; [P_lo, P_hi] by F2; P_lo ≤ P*_B(primary) and P*_B(primary) ≤ P_frozen(S_I1)
(else INDEPENDENT_CHECK_FAILED); Γ_dec (§2).

## 6. Independent reconstruction and shared code surface

| layer | primary | independent | relation |
|---|---|---|---|
| pointwise upper certificates (C2b) | pinned `c2b_exact.certify` via `mb308_a0core` | `vd_pl` (stream VERIFY) | verification of the same persisted W; shared: the kernel model and the P1 layout (by construction) |
| C1b lower bounds Λ_lo | pinned C1b | — (alarm only) | single implementation, used only as an alarm |
| RLR block certificates (τ, C_T, Ā_B, C_R, D_lo, D1, D2, L1, L2, τ_a,lo) | pinned C1b | — | **single implementation** (as in the cell-307 campaign; disclosed) |
| ladder / D14-M / Dv′-M / G / envelope / min | `mb308_stage1`, `mb308_supply` | F2 `mb_independent` (+ `rlr307_independent` for Lemma Lad) | exact equality |
| TC-T per-r tuple and profile polynomials | frozen consumer via `tptb_tail` | F3 `tuple_independent` | exact equality (G-R3b) |
| TPT-B integral | overnight `tpt.py` r2 `penalty_blocked` + C6 wrapper | F2 exact bracket | P_lo ≤ P*_B; decision uses max(P*_B, P_hi) |
| consumer reproduction | C2 frozen consumer | — | exact reproduction of committed records (C-A) |

Measured shared surfaces: F2 boilerplate only; F3 boilerplate only; VERIFY boilerplate plus the layout-fixed mesh loops.

## 7. Exactly-once mechanics

The accepted cell-307 driver's design, re-targeted (`code/mb308_driver.py`): identity (worktree, git dir, common dir,
branch), interpreter flags `-I -S -B`, no prior evaluation (marker, pending ref, result anywhere, emergency file),
lstat of guarded paths, clean tree including ignored files in the namespace, derived grant chain
(freeze → qualification → review → grant), pins (sha256 + git blob), lineage, r5 as expected and no r6, seal
preconditions, geometry cross-checks, controls; then the marker `refs/p5y-k5-cell308-mb-r1/target-consumed` → grant
by CAS; after the marker nothing escapes; seal from memory (object store, pending ref
`refs/p5y-k5-cell308-mb-r1/pending-result`, private-index commit, O_EXCL|O_NOFOLLOW materialization); `seal-only`
never computes. Guard arming: marker names the grant commit at HEAD and the admitted set equals the 37 pairs the
guard derives from `CELL308` by D1/D2 (disclosed deviation from the A0 C5 design's hash-bound authorization file:
the set is a pure function of the pinned guard bytes).

## 8. Frozen outcome table

| sealed status | condition | conclusion (applied verbatim by the adjudication) |
|---|---|---|
| TARGET_EVALUATED | all checks pass and **Γ_dec < 0** (exact) | **CELL308_CLOSED_UNDER_MB** |
| TARGET_EVALUATED | all checks pass and Γ_dec ≥ 0 (including Γ_dec = 0) | **CELL308_NOT_CLOSED_UNDER_MB** |
| INDEPENDENT_CHECK_FAILED, INCONSISTENT, C6 refusal, TARGET_EVALUATION_FAILED, POST_MARKER_RECORDING_FAILED, unsealable | any post-marker failure | **CELL308_EXECUTION_INDETERMINATE** (target consumed; no rerun) |
| CONTROL_FAILED | a control fails | no conclusion; target not consumed; STOP |

Strictness, rounding (exact), tolerance (none), members, rules and caps never change after the freeze.

## 9. Qualification (`config/QUALIFICATION_CASES.json`; `code/mb308_qualify.py`)

| case | gates | content |
|---|---|---|
| QC01 | Q2 | committed-record rehearsal on cell 305 (C-A, C-B; equality only) |
| QC02 | Q2, Q6, Q7, Q12 | full Stage 1 + Stage 2 on decoy cover cell 297 through the driver's decoy mode (incl. decreasing-constant and r = 0-bound bundles) |
| QC03 | Q6 | Stage 1 on the first three blocks of decoy cover cell 316 (above the band) |
| QC04 | Q3 | determinism (incl. REVIEW_A0 C4 pair on the frozen driver) |
| QC05 | Q1, Q4, Q5, Q7 | two-sided composition with mutants (primary vs F2) |
| QC06 | Q2, Q4 | pointwise-certificate package through the formal path (REVIEW_A0 C1, C6) |
| QC07 | Q5 | TPT-B controls (incl. endpoint-only and common-mode G-R3b plants) |
| QC08 | Q6 | independent Monte Carlo at decoy drifts |
| QC09 | Q9, Q12 | guard |
| QC10 | Q12 | exactly-once flows in `git clone --shared` sandboxes |
| QC11 | Q2, Q12 | static structure |
| QC12 | Q9 | leak scans (patterns from the pinned sanctioned file; neutral planted controls) |
| QC13 | Q10, Q11 | temporal and governance state; incident review conditions C1–C8 checked by path |
| Q8 | Q8 | freeze manifest |

Every case carries a boolean `pass`; the aggregator fails loudly on a missing key. No gate may be waived.

## 10. Order of operations and STOP conditions

1. Freeze (a commit on branch `p5y-k5-cell308-mb-r1`, worktree `/Users/suzhe/ReBaseGuard-c308mb`).
2. Official qualification at the freeze commit; committed as qualification evidence only.
3. Fresh independent qualification review: line 3 exactly QUALIFICATION_ACCEPTED or QUALIFICATION_REJECTED.
   **REJECTED ⇒ STOP** (no same-round repair; a successor campaign only).
4. The grant, committed alone, binding cell 308, route MB, the freeze/qualification/review commits, the driver
   sha256, the manifest sha256, exactly once, CLOSURE_ONLY, **and the user's C4 ruling**.
5. `execute`, once, at the grant commit; post-execution checks.
6. Fresh independent execution review: EXECUTION_ACCEPTED or EXECUTION_REJECTED (**REJECTED ⇒ STOP**, no rerun).
7. Scientific adjudication applying §8 verbatim.
8. Fresh independent adjudication review: ADJUDICATION_ACCEPTED or ADJUDICATION_REJECTED.
9. Handover.

Additional STOP conditions: the start state differs; the target appears consumed or a result exists; freeze inputs
drift; qualification data includes 305–309 values beyond the committed-305 reproduction or any target proxy; the
exactly-once infrastructure is found unsafe; the user's C4 ruling is absent at step 4.

## 11. Disclosed liabilities (carried verbatim into the grant and the adjudication)

* Incident 01 and residue (profile transport; the route family was chosen knowing committed tail structure).
* Incidents 02 and 03 (incident 03's sentence was read by stream A0; audit a1 C1(a)).
* H4.3b (historical route-audit juxtaposition).
* Coordinator disclosures I-a…I-e and E1′ (the coordinator holds every ingredient of an incident-01-class estimate of
  R-MB's outcome and has not formed it).
* Exposures of streams F2/F3 through theorem texts (a1 C1(b)); the quarantine rule breach of stream A's R1/R4
  (amendment 1).
* Single-implementation inputs: the RLR block certificates.
* Result-chasing risk MEDIUM–HIGH.
* Incident-independence review conditions C1–C9 (`research/reviews/INCIDENT_INDEPENDENCE_REVIEW_MB308.md`).

## 12. Ledger and quarantine

* Research ledger `p5y_k5_cell308_research/ledger/TARGET_INTEGRITY_LEDGER.jsonl` records every pre-freeze run.
* The qualification carries its ledger entries inside its report; they are appended after the seal together with the
  execution's line (307 precedent). The execution writes no ledger line before its seal.
* Guard: `code/mb308_guard.py`; quarantine config: research `config/TARGET_QUARANTINE_308.json` and amendment 1.
