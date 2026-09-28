# Cell-308 route registry (live)

Rules: route states only (CLOSED is never used for a route); no tail figure; every route here is **closure-only**
(floor r2 binds adoption to C2's consumer path with only S substituted). Columns: A0 = touches A0; ASM = changes the
assembly/consumer; DATA = needs new data; FRZ = eligible for a prospective target freeze.

**Revision r0** (2026-09-28, at the charter; before any stream result).

| id | route | theorem / obligation | status | A0 | ASM | DATA | FRZ | evidence / stream | known weakness |
|---|---|---|---|---|---|---|---|---|---|
| P0 | **Existing consumer, A1/A2 only** (RLR, Dv′, Lemma G A1/A2 alone) | committed C3 knockout (history H1.3) | **PRUNED (G11)** — certified by the committed knockout; reproduction in stream A | no | no | no | no | `history/recon/` (stream A) | — |
| P1 | **Existing consumer, atom constants only** (any admissible uniform triple, frozen direct clause or C5-T) | committed C4 §4 / C8 inversion (history H1.5–H1.7) + SM(d) floor | **PRUNED as a stand-alone route** (evidenced by committed Monte-Carlo; the certified part is stated in `history/recon/PRUNING_308.md`) | yes | no | no | no | stream A | the A0 part rests on an uncertified MC; a component of R-MB below |
| R1 | Theorem-M extremal A0 | Lemma M-U, Lemma A0-M (`theory/THEOREM_MB.md` §2–3) | THEORY_ONLY → component of R-MB | yes | no | no | as component | `theory/THEOREM_MB.md`; stream A0 | needs a tight pointwise certifier |
| R2 | Atom-level exact certificate | pointwise whole-kernel supersolution at one drift, exact rationals (THEOREM_AD §4) | IMPLEMENTED (C1b point mode, C2b) — study running | yes | no | no | as component | stream A0 (`streams/A0/`) | tightness and cost unknown in the relevant regime (measured only off-band) |
| R3 | Resolvent / supersolution certificate | C2b piecewise-linear triangulated certifier | IMPLEMENTED; REVIEW (overnight) ACCEPTED_WITH_CONDITIONS C1–C5 open | yes | no | no | after C1–C5 | overnight `streams/C_308/A0X/gen/`; stream A0 | incident 03 disclosure; float proposal must be persisted |
| R4 | Adaptive certified cover | real refinement needs new K1 records; refinement without records ≡ TPT (overnight identity) | **BLOCKED** (new K1 records: governance + host) | no | yes | yes | no | overnight `COVER_REFINEMENT_309` | smallest blocker: new real K1 records (U1 + governed real compute) |
| R5 | Piecewise / profile A0 | Theorem MB: block-resolved constants inside Lemma TC-P + TPT-B | THEORY_ONLY → component of R-MB | yes | yes | no | as component | `theory/THEOREM_MB.md` §6–7; stream ASSEMBLY | incident-01 liability (profile transport) |
| R6 | Common structural theorem | Lemmas Dv′-M and D14-M: one certified Ā′ tightens A0, A1, A2 together | THEORY_ONLY → component of R-MB | yes | no | no | as component | `theory/THEOREM_MB.md` §4–5 | needs the proof review O1 |
| R7 | Independent second implementation | independent exact verifier of the pointwise certificate; independent composition layer | IMPLEMENTING | yes | — | no | required | stream VERIFY (`streams/VERIFY/`) | shared-surface measurement pending |
| R8 | Assembly tightening | TPT / TPT-B on the frozen TC-T path | theory sound, implementation VALIDATED_NON_TARGET (overnight); tail adapter IMPLEMENTING | no | yes | no | as component | overnight `streams/E_assembly/`; stream ASSEMBLY | incident-01 liability; TC-T tail input path unvalidated by design (decoys only) |
| R9 | Residual-specific structure | RSO (order-0, residual-specific), SC (composite sup) | **BLOCKED** (data: K1 candidate payloads never serialized; U1 host, U2 P3 admissibility) | yes (RSO) | yes | yes | no | overnight `streams/D_309/` | smallest blocker: a certifying host + admissibility ruling to regenerate payloads |
| R10a | Monotone envelope of pointwise certificates | Lemma M-U envelope Ū_j = min_{i≤j} U_i | THEORY_ONLY → component of R-MB | yes | no | no | as component | `theory/THEOREM_MB.md` §2 | — |
| C-RLR | RLR A1/A2 block supply (component only; G11 alone) | THEOREM_RLR307 D14 | REVIEW_ACCEPTED (cell-307 campaign) | via Ā′ | no | no | as component | `p5y_k5_cell307_rlr_r1` | single certifier implementation (disclosed there) |
| X308 | Exclusion (lower bound on Λ₃₀₈ above a threshold) | overnight draft | DEFERRED (zero closure leverage; committed MC says the threshold is above the truth) | — | — | — | no | overnight `FREEZE_308_EXCLUSION_PROTOCOL_DRAFT.md` | incidents 02/03 |

**Composite candidate R-MB** (= R1 + R2/R3 + R5 + R6 + R8 + R10a + C-RLR): the strongest host-free, data-free
combination, formed by logical dominance (every component acts on a different inequality and is taken as a minimum
with the committed supply). Status: **THEORY_ONLY**; obligations O1–O5 of `theory/THEOREM_MB.md` §9.
