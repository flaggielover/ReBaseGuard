# Cell-307 RLR formal prospective closure campaign (r1): final report

**Answer to the campaign question, given once.** Under the existing frozen K5 consumer, the prospectively frozen RLR
certificate **closes cell 307**. The accepted adjudication is **CELL307_CLOSED_UNDER_RLR** (its independent review returned ADJUDICATION_ACCEPTED).

**This is scientific closure only.** It is not adoption in r5, not adoption under floor r2, not r6, not K5 CLOSED and
not P5Y CLOSED.

| cell | start state | end scientific state | this campaign |
|---|---|---|---|
| 306 | OPEN / NOT ADOPTED | unchanged | untouched |
| 307 | OPEN | **CELL307_CLOSED_UNDER_RLR (scientific closure only; NOT adopted; r5 still lists it open)** | one sealed evaluation |
| 308 | OPEN | unchanged | untouched |
| 309 | OPEN | unchanged | untouched |

## A. Repository

| item | value |
|---|---|
| worktree / branch | `/Users/suzhe/ReBaseGuard-c307`, branch `p5y-k5-cell307-rlr-r1`, created at the overnight handover `7f45e048` |
| start HEAD | `7f45e048` (overnight handover; base `8b9fc0bb`) |
| end HEAD | the commit adding this report (child of `f3f8d207`) |
| clean | yes: no tracked, untracked or ignored object in the namespace |
| push | **not pushed, not merged.** `main` untouched |
| scope of change | all commits are inside `level4/closure_proofs/p5y_k5_cell307_rlr_r1/`. The overnight namespace and every earlier campaign are untouched, including the rejected closeout freezes `08e9acd1`, `591b4394`, `dfcd8f79`, `0d275038`, `9f702acb` and `8b9fc0bb` |

## B. RLR provenance

See `evidence/provenance/RLR_PROVENANCE_TIMELINE.md`.
* Idea note `cbff958a` (02:49).
* Theorem LR and the first finite-state validation `7e851139` (03:56).
* Real-kernel certifier `2b118e62` (06:15).
* Reviews: R1 incomplete (`8414614f`), R2 ACCEPTED_WITH_CONDITIONS (`1c4b9fca`), R3 CONFIRMED_WITH_NOTES (`7e35b12c`).
* Load-bearing code pinned at `3d13c138`.
* Final two-sided test fix `47933904`.
* FREEZE_READY and the protocol draft {307} at `d3b60795`.

Every load-bearing element predates the handover. No evaluation of cell 307 existed before this campaign.

## C. Incident audit

* **Audit.** `audit/INCIDENT_AUDIT_RLR307.md`, plus `audit/INCIDENT_AUDIT_ADDENDUM_R1.md`; the addendum prevails.
* **Independent review.** `review/INCIDENT_INDEPENDENCE_REVIEW.md` (`c9ff8e3e`): **INCIDENT_AUDIT_ACCEPTED**. All five
  brief-§4 conclusions are accepted, with conditions C1–C6.
* **What the reviewer added.** Two 307-specific exposures that the coordinator's audit had missed:
  * F1(a): an unledgered, uncommitted B_307 draft adjacency;
  * F1(b): the committed HIGHER_ORDER_AUDIT_307 co-location.
* **Corrected overnight count.** 4 ledgered qualitative exposures, 2 rule breaches, and 1 unledgered adjacency of
  unverifiable content.
* **Independence.** Temporal and parametric only. Result-chasing risk is MEDIUM (motivation provenance).
* **Relevance of the individual incidents.** Incidents 02 and 03 and breach L6 do not bear on RLR/307. Incident 01's
  residue does, qualitatively; nothing was ever combined into a number.

## D. Formal theorem

`theory/THEOREM_RLR307.md`, Theorem RLR-307. The certified block supply is D14: the term-level minimum of RLR
(ratio and non-ratio forms) and the Dv′ factors, then the componentwise minimum with Lemma G.
* The ladder composition, the worst-block maximum and the outward 2^-20 hull cover are proved valid.
* S_RLR = (A0_I1, min(A1_I1, A1_cell), min(A2_I1, A2_cell)) is admissible for TC-T (P4).

Proof status: the qualification reviewer checked it (proof completeness: PASS with scope notes). The limits are
stated in §4 of the theorem. The certified inputs come from one implementation, and that surface is disclosed.

## E. Implementation

* **Certifier.** The overnight C1b certifier, executed from its pinned bytes by `code/rlr307_pinned.py`. Its sha256
  values equal `C1B_R2_CODE_PINS.json`; the load-bearing set has not changed since r1.
* **Quarantine binding.** `ov_quarantine` is bound to the campaign guard `code/rlr307_guard.py`.
* **Driver.** `code/rlr307_driver.py`, sha256 `69160c31…`. It uses C12-R2's seal-from-memory exactly-once design.
* **Stage 1.** `code/rlr307_stage1.py`.
* **Independent reconstruction.** `code/rlr307_independent.py`.
* **Consumer.** C2's frozen consumer from pinned bytes.

## F. Qualification cases

`config/QUALIFICATION_CASES.json`, 14 cases, all non-target:
* QC01: committed-block reproduction;
* QC02: decoy cover cell 297, full Stage 1;
* QC03 / QC03_cross_run: determinism;
* QC04: independent Monte Carlo;
* QC05 / QC09: two-sided composition, 6/6 historical mutants plus composition mutants;
* QC06: κ;
* QC07: guard and arming;
* QC08: cell-305 committed-record reproduction;
* QC10: 39 exactly-once sandbox flows;
* QC11: static structure;
* QC12: leak scan;
* QC13: temporal.

No case used cell 306, 307, 308 or 309, or any drift in [6/5, 13/5] or its mirror.

## G. Qualification gates Q1–Q12

**Freeze r2, official run (`978d9965`): PASS on every gate, Q1–Q12.**

**Freeze r1 (`5c6667fd`): FAIL on Q12**, preserved in `qualification/r1_failed/`. The cause was a verifier
aggregation defect: the QC10 summary had no `pass` key. Every case had passed on its own terms. It was repaired by a
stricter-only change to the verifier (r2), before any review.

## H. Freeze

| item | value |
|---|---|
| freeze r2 commit / tree | `cd5016f1d0a9fbb43c900740ee6da9a96f4f1963` / `ef024c70a2c4…` (r1: `5c6667fd…` / `b9fd56dc…`) |
| input manifest | `protocol/RLR307_FREEZE.json`, sha256 `34309e579b7a632386e32929dc894e764216eb4c595b40e1cdc125874c6e854f` (blob `bd53e37cb154`) |
| protocol blob | `4d4a5ce2c0ef` |
| theorem blob | `52ec7d2f5e97` |
| evaluator (driver) blob | `0491045c4263` (sha256 `69160c31…`) |
| helpers | stage1 `cadb9f83d8be`, pinned `21ce4c46401b`, guard `523c4531a03a`, independent `85397b5538bd`, qualify `b45b0a791b97` |
| test blobs | twosided `aca89b40dc03`, mc `b486a5f69588`, flows `1fe3c651da4a` |
| qualification-case manifest | `config/QUALIFICATION_CASES.json` blob `e2b9162295a9` |
| source provenance / zero-target ledger | `evidence/provenance/…`, `ledger/ZERO_TARGET_LEDGER_307.jsonl` |

## I. Qualification review

`review/RLR307_QUALIFICATION_REVIEW.md` at `c91991c6`: **QUALIFICATION_ACCEPTED**.
* The reviewer found no blockers. All 17 checklist items PASS; three carry notes.
* It ran quick and `--heavy` review runs. Both PASS, and its heavy recomputation is bit-identical to r1 and r2.
* Conditions: G1–G3 for the grant, E1–E5 for execution.
* Notes N4–N7 are non-blocking.

## J. Grant

`authorization/RLR307_GRANT.json`, commit `5390b06dc92c2580b92d743ca82629473e28ca90`, committed alone as the direct
child of the review.
* **What it binds:**
  * cell 307, route RLR;
  * the freeze, qualification and review commits;
  * the driver sha256 and the manifest sha256;
  * exactly one execution;
  * CLOSURE_ONLY, with adoption, floor change, r6 and K5/P5Y closure NOT AUTHORIZED.
* **What it carries verbatim:** C1–C6, N4, N7, G1–G3 and E1–E5.
* **Marker:** `refs/p5y-k5-cell307-rlr-r1/target-consumed` → `5390b06d`.

## K. Target execution

| item | value |
|---|---|
| executions | **exactly 1** (`python3.14 -I -S -B …/rlr307_driver.py execute`, launched 08:47:11Z, finished 11:05:42Z; evaluation 8309 s under the 21600 s cap) |
| pre-marker control | cell 307 under C2's committed S_I1 reproduced C2's committed record exactly (7/7 fields). This is a historical reproduction, not new information |
| Stage 1 | 10/10 blocks CERTIFIED, each at degrees 4, 6 and 8 (30/30 rungs; 0 RUNG_EXCEPTION). The independent reconstruction was all equal |
| supply | S_RLR: A0 from I1 (unchanged); A1 and A2 from RLR (the RLR cell values were below the committed I1 values) |
| **result** | **Γ(5, 307; S_RLR) < 0 in exact rationals**: Γ ≈ −0.003070 (between −3071/10⁶ and −3070/10⁶; exact 2588-character rational in the sealed file); consumer `pass` = true |
| for reference | C2's committed Γ(5, 307; S_I1) ≈ +0.0331 (pass false), historical |

## L. Seal

* Result blob `041611126a32d7064f6a9b1dd6a3439c3f3e15e7`, equal to `refs/p5y-k5-cell307-rlr-r1/pending-result`.
* Seal commit `b26c64a74d0ed7a7535259fa058f9ab4a39dedd2`: its parent is the grant, and it adds the result path only.
* Marker `refs/p5y-k5-cell307-rlr-r1/target-consumed` → grant.
* Post-execution checks (`postexec/POSTEXEC_CHECKS.json`, `2c50f534`): all PASS, including:
  * a second `execute` refused before anything;
  * `seal-only` computed nothing;
  * r5 unchanged, no r6.

## M. Execution review

`review/RLR307_EXECUTION_REVIEW.md` at `e68f3d64`: **EXECUTION_ACCEPTED**.
* 11/11 checks pass, plus E3.
* Everything was re-derived exactly from the sealed record without recomputation: 30 rung supplies, 10 ladder
  compositions, the cell maximum and S_RLR.

## N. Cell-307 adjudication

`adjudication/RLR307_CELL307_ADJUDICATION.md` at `12608321`: **CELL307_CLOSED_UNDER_RLR**.
* It applies frozen §8, row 1.
* Its exact-Fraction checks pass 37/37.
* It carries C1–C6, N4 and N7 verbatim.

## O. Adjudication review

`review/RLR307_ADJUDICATION_REVIEW.md` at `f3f8d207`: **ADJUDICATION_ACCEPTED**.
* All eight brief-§28 checks pass, plus G2 and E5, with no blockers:
  * the frozen criterion was applied verbatim;
  * the correct sealed blob was used;
  * the sign was recomputed exactly;
  * no rule has changed since the freeze;
  * scope, the closure/adoption distinction, r5/r6 and the other cells are all correct.

## P. Coverage

r5 is unchanged: blob `f978eeb6…`, union open [306, 309]. **No r6** exists on any ref. The coverage map was not
touched.

## Q. Other cells

306, 308 and 309 are unchanged. Nothing was evaluated on them, and nothing about them is inferred from 307.

## R. Adoption

**Explicitly NOT performed.** Cell 307 remains OPEN in r5 and is not adopted under floor r2. An RLR-bearing supply is
neither a Lemma G nor a Lemma Dv′ r2 supply, and it mixes certifiers.

## S. P5Y

**Not adjudicated here.** K5 remains OPEN (PARTIAL) and P5Y remains NOT_YET_CLOSED.

## T. Target-integrity ledger

| item | count |
|---|---|
| Γ306 new evaluations | 0 |
| Γ307 new evaluations | **1** (the granted execution) |
| Γ308 new evaluations | 0 |
| Γ309 new evaluations | 0 |
| target-equivalent 307 proxies before the grant | 0 |
| post-result tuning runs | 0 |
| historical reproduction controls (cell 307 under C2's committed S_I1, equality only, post-grant and pre-marker) | 1 |
| cell-305 committed-record reproductions (rehearsals: dev, r1, r2, reviewer) | 4 |
| refusal probes naming 307 (qualification reviewer; nothing evaluated) | 2 |

Source: `ledger/ZERO_TARGET_LEDGER_307.jsonl`.

## U. Final recommendation

Cell 307 closes scientifically under the frozen RLR supply.

**Recommendation.** Keep this as closure-only scientific evidence. Consider adoption only through a **separate,
prospective floor-extension study** (U3), designed without reference to this result's margin. Such a study must:
* be frozen before any new evaluation;
* carry this campaign's disclosed liabilities: motivation provenance (MEDIUM), the overnight incidents, and the single
  certifier implementation of the Stage-1 inputs;
* decide whether a mixed-certifier (RLR ∧ Dv′ ∧ Lemma G) supply can ever satisfy an adoption floor, possibly by
  requiring a second, independent RLR implementation.

**Do not:**
* re-run or tune RLR on 307;
* apply RLR to 308 or 309: the committed C3 knockout shows that an A1/A2-only supply cannot close them;
* treat this result as evidence about any other cell.

## Process notes (faithful record)

* **First qualification-review launch was void.** Its brief was an unfilled placeholder; the agent did no work and
  wrote nothing, and was replaced.
* **First qualification launch was refused** by the empty-directory precondition, fail-closed.
* **r1 qualification FAILED**, on a verifier defect. It was repaired as r2, before any review.
* **The post-execution refusal probe** ran `execute` once more. It was refused at the ref check, before anything
  (brief §23). The execution review notes that this is literally in tension with E4 and that it had no effect.
* **A dangling pre-freeze dev snapshot commit** `53f0e890` exists unreferenced in the object store. It is disclosed.
