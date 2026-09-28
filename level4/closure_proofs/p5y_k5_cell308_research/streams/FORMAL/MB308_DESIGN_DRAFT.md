# MB308 formal campaign — design draft (research-namespace draft; NOT a protocol, NOT frozen, authorizes nothing)

**Status: DRAFT d1 (coordinator; d0 at c8b68d4d).** d1 applies REVIEW_A0_CERTIFIER_R1 (C1–C6), stream F2's and F3's findings (independent bracket; common-mode tuple gate G-R3b; decreasing-constant and r = 0-bound decoy regimes). It turns route R-MB (registry) into a buildable exactly-once design, mirroring the
accepted cell-307 campaign (`p5y_k5_cell307_rlr_r1/protocol/RLR307_PROTOCOL.md`). Every parameter below is fixed by a
target-free rule, stated with its reason. No number of any tail cell appears here. Open items are marked **OPEN**.

## 1. Names and scope

| item | value |
|---|---|
| formal namespace | `level4/closure_proofs/p5y_k5_cell308_mb_r1/` |
| branch / worktree | `p5y-k5-cell308-mb-r1` created from the research tip at freeze time; `/Users/suzhe/ReBaseGuard-c308mb` |
| refs | marker `refs/p5y-k5-cell308-mb-r1/target-consumed` → grant; `refs/p5y-k5-cell308-mb-r1/pending-result` |
| target | CUSUM m = 5 cell 308 only; closure-only; one execution |
| outcome labels | CELL308_CLOSED_UNDER_MB · CELL308_NOT_CLOSED_UNDER_MB · CELL308_EXECUTION_INDETERMINATE |

## 2. Scientific object

Theorem MB r1 (`theory/THEOREM_MB.md`): Γ_MB = g_hi + P*_B is a certified upper bound on sup_{e∈E} g_5(e) for the cover
cell E of cell 308, built from the committed TC-T inputs, block triples S_i on the C2 partition, and the TPT-B
transport. Closure criterion (unchanged K5 criterion: a certified upper bound on sup g that is strictly negative):
**Γ_dec < 0 in exact rationals**, where Γ_dec is defined in §5.4.

## 3. Decisions (each fixed by a target-free rule)

| # | decision | value | reason |
|---|---|---|---|
| D1 | partition | E_i: N = max(1, ⌈(x_hi − x_lo)/(1/100)⌉) equal exact sub-intervals of the cover interval | C2's rule, used unchanged by the 307 campaign |
| D2 | hulls | B_i = outward 2^-20 dyadic hull of E_i; b_i := lo(B_i) (dyadic, ≤ lo(E_i)) | the pinned C1b certifier needs dyadic centres/radii (307 D3.1); Theorem M makes a certificate at b_i ≤ lo(E_i) valid on E_i |
| D3 | RLR block ladder | pinned `certify_degree(centre, d, BW_PW, e_r = radius)` on B_i, d ∈ (4, 6, 8), TIGHT_CT = BLOCK_LIGHT = True, ladder composition by Lemma Lad | identical to the 307 Stage-1 rules P2–P4 (reused, not re-tuned) |
| D4 | pointwise Λ ladder at b_i | stream A0 ladder rules R1–R6 (`streams/A0/a0_ladder.py`): rungs C2b exact-scale N ∈ {20, 40, 80} and C1b pointwise d ∈ {8, 10, 12}; U_i = min over certified upper rungs that pass independent verification (D5); L_i = max over certified lower rungs; L_i ≤ U_i required | chosen from non-target drifts only (A0 study F1–F4); no early stopping |
| D5 | admission of an upper rung | an upper rung's U enters U_i only if (i) its persisted certificate is re-verified by the independent verifier (stream VERIFY; C1b strip format; C2b piecewise-linear format once delivered — until then C2b rungs are UNVERIFIED and not admitted) and (ii) at least one certified lower rung of the OTHER implementation exists with L_other ≤ U. Some L_other > U ⇒ INCONSISTENT (post-marker ⇒ INDETERMINATE); no other-implementation lower rung ⇒ ALARM_UNAVAILABLE, rung not admitted (fail-closed). Within one C2b rung L ≤ U holds by construction and is not an alarm | R7; brief §11; REVIEW_A0_CERTIFIER_R1 C2 |
| D6 | envelope | Ū_i = min_{j ≤ i} U_j over the pre-declared b_j only (Lemma M-U; review N8) | result-free |
| D7 | members of S_i | (1) S_I1 (C2's committed cell supply, reproduced); (2) Dv′-M on REGISTRY_C1's and REGISTRY_C2's committed cell inputs with Abar := min(Abar, Ū_i), through the frozen `deflated_consume.atom_constants_r2`; (3) D14-M on the RLR ladder record of B_i with Ā′ = min(Ā_B, Ū_i), Lemma DM refresh, A0 slot min(Ā′_eff, C_R); (4) Lemma G with C_R of B_i. S_i = componentwise min of the available members | maximal by dominance (charter rule 5); every member is valid on E ∩ B_i (THEOREM_MB r1 §6) |
| D8 | missing certificates | a block without an RLR certificate lacks members (3)/(4); a b_i without a certified-and-verified U rung has Ū_i from the envelope only (or +∞); nothing is retried | fail-safe: every missing member only weakens S_i |
| D9 | consumer | TPT-B on cell 308's committed TC-T inputs (stream ASSEMBLY `tptb_tail`, frozen-path loader), pieces cut at E_i ends and e0; gates C5 (E = [e0 − ρ, e0 + ρ] exactly), C6 (per-piece non-emptiness) and **G-R3b**: the per-r tuple and every profile polynomial (cell constants and every block triple) equal the independent `tuple_independent` exactly (stream INDEP_TUPLE; closes the common-mode blind spot) | Theorem MB r1 §7; F3 |
| D10 | computed on the target | ONLY: the two historical controls (§5.1), Stage 1, S_i, P*_B (primary) and its independent bracket (F2). **Not** computed on the target: P_TPT(S_I1), P_C5T(S_I1) or any other route's value | brief §21 ("do not compare several candidate routes on 308") |
| D11 | workers / caps | 5 spawned workers; pre-marker cap 1800 s; EVAL_CAP from decoy costs by the 307 rule (≥ 2× projection, ≥ 6 h); the ladder refuses to start unless the effective CPU cap equals the declared cap | 307 §3.2 rule; REVIEW_A0 C3 |
| D12 | comparison rule | primary vs independent: exact equality for every composition layer; for P*_B the bracket rule P_lo ≤ P*_B(primary) (never a loose tolerance) | F2 open issue 3 |

## 4. Stage 1 (after the marker)

* S1a: RLR ladder on every B_i (D3).
* S1b: pointwise Λ ladder at every b_i (D4), certificates persisted in memory with sha256.
* S1c: independent verification of every certified upper rung (D5).
* S1d: consistency L_i ≤ U_i (exact); violation ⇒ INDETERMINATE (soundness alarm).
* S1e: envelope (D6); composition of S_i (D7) with the independent reconstruction F2 (`streams/INDEP/mb_independent.py`)
  required to agree exactly on every member and every S_i.

## 5. Controls, Stage 2, decision

### 5.1 Controls (before the marker; historical reproductions only)
* **C-A:** cell 308 under S_I1 through C2's frozen consumer reproduces C2's committed record exactly (Gamma_exact,
  A_exact, provenance, H_exact, M_after_exact, pass, per-supply records) — as the 307 control.
* **C-B:** `tptb_tail` in reproduction mode with S_I1 (constant profile at s = ρ) reproduces the frozen enclosure and
  Γ exactly (gates G-R1, G-R2, G-R4, G-CF) and G-R3 against the independent re-derivation.
* Either failing ⇒ CONTROL_FAILED, sealed, target **not** consumed.

### 5.2 Stage 2
* P*_B by `tptb_tail` (primary, exact rational, a certified upper bound with a 60-bit cap split).
* [P_lo, P_hi] by F2's independent integrator (width < 2^-150).
* Consistency: P_lo ≤ P*_B(primary) (else INDEPENDENT_CHECK_FAILED); P*_B(primary) ≤ P_frozen(S_I1) (dominance
  sanity against the reproduced committed value; else INDEPENDENT_CHECK_FAILED).

### 5.3 Why two upper bounds
Both P*_B(primary) and P_hi are certified upper bounds on the exact P*_B under their own proofs. The decision uses the
larger, so closure requires both implementations to certify it.

### 5.4 Decision (frozen)
Γ_dec := g_hi + max(P*_B(primary), P_hi).

| sealed status | condition | conclusion |
|---|---|---|
| TARGET_EVALUATED | all checks pass and Γ_dec < 0 (exact) | **CELL308_CLOSED_UNDER_MB** |
| TARGET_EVALUATED | all checks pass and Γ_dec ≥ 0 (**Γ = 0 does not close**) | **CELL308_NOT_CLOSED_UNDER_MB** |
| INDEPENDENT_CHECK_FAILED / INCONSISTENT / C6 refusal / TARGET_EVALUATION_FAILED / unsealable | any post-marker failure | **CELL308_EXECUTION_INDETERMINATE** (consumed; no rerun) |
| CONTROL_FAILED | a control fails | no conclusion; target not consumed; STOP |

Strictness, rounding (exact), tolerance (none), members and rules never change after the freeze.

## 6. Qualification (decoys only; no drift in the band; nothing on 305–309 except the committed-305 reproduction)

| case | content |
|---|---|
| QC01 | 305 committed-record reproduction: C-A and C-B on cell 305 (historical equality only; no new-route value on 305) |
| QC02 | decoy cover cell 297 (below the band): full Stage 1 (RLR + pointwise + verification + consistency + envelope + composition with F2 equality), then Stage 2 on manufactured TC-T bundles with 297's geometry, members (3)/(4) only; bundle regimes include decreasing block constants (rise-then-fall running integrals; the endpoint-only mutant must be detected) and the r = 0 adopted order-3 bound binding |
| QC03 | decoy cover cell 316 (above the band): Stage 1 on its first three blocks (cost and soundness above the band) |
| QC04 | determinism: a QC02 block re-run serially in a fresh process equals the pooled result byte for byte |
| QC05 | composition two-sided: primary vs F2 on QC02 plus planted mutants (each member smallest in turn; ±2^-40 perturbations; wrong envelope direction; pointwise τ/C_T/D_lo substituted for block ones must be refused) |
| QC06 | pointwise-certificate controls through the frozen verification path (stream A0 C3 controls; stream VERIFY D4/D6 controls); REVIEW_A0 C6: FD of hessian_bounds over every cell kind with a rough W, err-path controls in both directions with a confirmed interior violation, the two direction-swap controls, a vertex-enclosure agreement test at a non-dyadic drift; determinism pair on the frozen driver (REVIEW_A0 C4) |
| QC07 | TPT-B controls (stream ASSEMBLY E4, 29 cases) regenerated at the freeze commit, plus C5/C6 plants |
| QC08 | independent Monte Carlo at decoy drifts: U_i ≥ MC − 5σ and L_i ≤ MC + 5σ |
| QC09 | guard: band refused in decoy mode; target refused without the grant; authorization-file binding (A0 study C5 design) |
| QC10 | exactly-once flows in a `git clone --shared` sandbox (adapted from the 307 flow suite) |
| QC11 | static structure: pins, module identities, shared-surface measurement, F2 imports stdlib only |
| QC12 | leak scan (c308 scanner with planted controls) |
| QC13 | temporal: HEAD = freeze; no review/grant/marker/result; incident review committed before the freeze |

Gates Q1–Q12 as the 307 protocol (theorem integrity, identity, determinism, arithmetic, negative controls, non-target
soundness, composition, provenance, quarantine, temporal, incident independence, execution safety). Every case
carries a boolean `pass`; the aggregator fails loudly on a missing key (307 lesson).

## 7. Disclosed liabilities (carried into the grant and the adjudication)

* Incident 01 (profile transport) and I-a…I-e of `ledger/COORDINATOR_EXPOSURE_DISCLOSURE.md`: MEDIUM–HIGH
  result-chasing risk, mitigated by dominance-only selection and rule-fixed parameters.
* Incident 03 (C2b brief scale; C2b is on the U path).
* Single-implementation inputs: the RLR block certificates (as in 307).

## 8. OPEN before a freeze

0. The C2b errata file (REVIEW_A0 C5) inside the formal package.

1. D5: the independent verifier's formats, budget rule and verdict mapping (stream VERIFY).
2. Stream A0: C3 controls complete; side-effect-free `a0_core.py`; review of `a0_c2bx` (exact-scale) and `sub_certify`.
3. F2 independent reconstruction complete and compared.
4. Real TC-T input loader for the formal driver (pinned, from the 307 driver's `cell_inputs`).
5. Incident-independence audit and its independent review.
6. Decoy cost measurement ⇒ EVAL_CAP.
