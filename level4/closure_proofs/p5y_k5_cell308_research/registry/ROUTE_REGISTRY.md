# Cell-308 route registry (live)

Rules: route states only (CLOSED is never used for a route); no tail figure; every route here is **closure-only**
(floor r2 binds adoption to C2's consumer path with only S substituted). Columns: A0 = touches A0; ASM = changes the
assembly/consumer; DATA = needs new data; FRZ = eligible for a prospective target freeze.

**Revision r2** (2026-09-29): adds the absent route families (incident review C6). **Revision r1** (2026-09-29): streams A (history), A0, VERIFY, ASSEMBLY, INDEP and the Theorem MB review have reported; r0 was at the charter.

| id | route | theorem / obligation | status | A0 | ASM | DATA | FRZ | evidence / stream | known weakness |
|---|---|---|---|---|---|---|---|---|---|
| P0 | **Existing consumer, A1/A2 only** (RLR, Dv′, Lemma G A1/A2 alone) | committed C3 knockout (history H1.3) | **PRUNED (G11)** — certified by the committed knockout; reproduction in stream A | no | no | no | no | `history/recon/` (stream A) | — |
| P1 | **Existing consumer, atom constants only** (any admissible uniform triple, frozen direct clause or C5-T) | committed C4 §4 / C8 inversion (history H1.5–H1.7) + SM(d) floor | **PRUNED as a stand-alone route** (evidenced by committed Monte-Carlo; the certified part is stated in `history/recon/PRUNING_308.md`) | yes | no | no | no | stream A | the A0 part rests on an uncertified MC; a component of R-MB below |
| R1 | Theorem-M extremal A0 | Lemma M-U, Lemma A0-M (`theory/THEOREM_MB.md` §2–3) | **REVIEW_ACCEPTED** (REVIEW_THEOREM_MB_R1, corrections applied in r1) → component of R-MB | yes | no | no | as component | `theory/THEOREM_MB.md`; stream A0 | needs a tight pointwise certifier |
| R2 | Atom-level exact certificate | pointwise whole-kernel supersolution at one drift, exact rationals (THEOREM_AD §4) | **VALIDATED_NON_TARGET** (stream A0: deterministic ladder, certified brackets at six non-target drifts, 60/60 controls, 16/16 re-verification); certifier review REVIEW_PENDING | yes | no | no | as component | stream A0 (`streams/A0/`) | tightness and cost unknown in the relevant regime (measured only off-band) |
| R3 | Resolvent / supersolution certificate | C2b piecewise-linear triangulated certifier (+ exact-scale selection) | VALIDATED_NON_TARGET; overnight review conditions C1/C2 met by stream A0, C3–C5 under review | yes | no | no | after C1–C5 | overnight `streams/C_308/A0X/gen/`; stream A0 | incident 03 disclosure; float proposal must be persisted |
| R4 | Adaptive certified cover | real refinement needs new K1 records; refinement without records ≡ TPT (overnight identity) | **BLOCKED** (new K1 records: governance + host) | no | yes | yes | no | overnight `COVER_REFINEMENT_309` | smallest blocker: new real K1 records (U1 + governed real compute) |
| R5 | Piecewise / profile A0 | Theorem MB: block-resolved constants inside Lemma TC-P + TPT-B | **REVIEW_ACCEPTED** (theory) → component of R-MB | yes | yes | no | as component | `theory/THEOREM_MB.md` §6–7; stream ASSEMBLY | incident-01 liability (profile transport) |
| R6 | Common structural theorem | Lemmas Dv′-M, D14-M and DM: one certified Ā′ tightens A0, A1, A2 (and D_lo) together | **REVIEW_ACCEPTED** (theory) → component of R-MB | yes | no | no | as component | `theory/THEOREM_MB.md` §4–5 | needs the proof review O1 |
| R7 | Independent second implementation | independent exact verifier (stream VERIFY; C1b format done, C2b format in progress); independent composition + exact TPT-B bracket (stream INDEP, VALIDATED_SYNTHETIC); independent TC-T tuple (in progress) | IMPLEMENTED (partly) | yes | — | no | required | stream VERIFY (`streams/VERIFY/`) | shared-surface measurement pending |
| R8 | Assembly tightening | TPT / TPT-B on the frozen TC-T path | theory sound; `tptb_tail` VALIDATED_SYNTHETIC (18 decoys, 29/29 controls) and lower front 136/136 (degenerate blocks) | no | yes | no | as component | overnight `streams/E_assembly/`; stream ASSEMBLY | incident-01 liability; TC-T tail input path unvalidated by design (decoys only) |
| R9 | Residual-specific structure | RSO (order-0, residual-specific), SC (composite sup) | **BLOCKED** (data: K1 candidate payloads never serialized; U1 host, U2 P3 admissibility) | yes (RSO) | yes | yes | no | overnight `streams/D_309/` | smallest blocker: a certifying host + admissibility ruling to regenerate payloads |
| R10a | Monotone envelope of pointwise certificates | Lemma M-U envelope Ū_j = min_{i≤j} U_i | REVIEW_ACCEPTED (theory) → component of R-MB | yes | no | no | as component | `theory/THEOREM_MB.md` §2 | — |
| C-RLR | RLR A1/A2 block supply (component only; G11 alone) | THEOREM_RLR307 D14 | REVIEW_ACCEPTED (cell-307 campaign) | via Ā′ | no | no | as component | `p5y_k5_cell307_rlr_r1` | single certifier implementation (disclosed there) |
| X308 | Exclusion (lower bound on Λ₃₀₈ above a threshold) | overnight draft | DEFERRED (zero closure leverage; committed MC says the threshold is above the truth) | — | — | — | no | overnight `FREEZE_308_EXCLUSION_PROTOCOL_DRAFT.md` | incidents 02/03 |

**Composite candidate R-MB** (= R1 + R2/R3 + R5 + R6 + R8 + R10a + C-RLR): the strongest host-free, data-free
combination, formed by logical dominance (every component acts on a different inequality and is taken as a minimum
with the committed supply). Status: **IMPLEMENTED (research components) → formal build in progress**
(`streams/FORMAL/MB308_DESIGN_DRAFT.md`). O1 discharged; O2 validated non-target, certifier review pending; O3 done on
decoys; O4 done (INDEP) pending the formal primary; O5 incident review pending. **Not FREEZE_READY.**

## Completeness rows (r2; incident review C6)

Every known tail route family, including those absent from r0/r1, with a **target-free** status (toolchain, host,
data, governance, or logical position). **None was pruned by H4.3b or by any estimated effect on 308.**

| id | route family | status | target-free reason |
|---|---|---|---|
| C9-E1 | α-ladder lever (re-certify the registry's taboo/whole-kernel supersolutions at an α below the C2 first rung) | **BLOCKED (toolchain/host)** | needs the registry certifier `taboo_certify` (numpy + python-flint); neither exists on this host (stdlib Python only) and host provisioning is a user decision (U1). Its logical position: it would tighten the registry inputs of member (2) of R-MB; R-MB's Theorem-M order-0 certificate already replaces its Ā channel |
| C11R-I2 | the I2 certifier family (C11R constants + C11RD D1/D2) as an additional member at 308's blocks | **DEFERRED (implementation scope)** | the certifier exists (stdlib, reviewed for N9 at cell 306) but has never been run at any block of this cell and is not wired into R-MB; adding it is a successor-campaign item. Not excluded by estimated effect |
| COR-T | AD Corollary T for g_hi (atom-functional midpoint eps) | **DEFERRED (implementation scope)** | not implemented on the TC-T path; would add a new trust surface to g_hi; not excluded by estimated effect |
| CHAIN | the K5-B chain clause (γ_k over adjacent cells) | **EXCLUDED (logical position + quarantine)** | not part of the per-cell closure quantity; needs certificates of the adjacent tail cells, which are quarantined |
| RO3 | real order-3 candidate Ĝ (R-stage) | **BLOCKED (governance)** | new real K1 addresses; guard DENY; N1/N5/N7 open |
| TPT, C5-T | single-profile transports | **INCLUDED as special cases** | TPT-B with one block equals TPT; C5-T ≤ frozen clause; dominance chain (THEOREM_MB r1 §7) |
| LR | plain score-level atom constants | **INCLUDED** | as the non-ratio/ratio terms inside D14 (min) |
| B2c | constants re-certified on sub-segments without new records | **INCLUDED** | this is R-MB's block resolution |
