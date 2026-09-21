# K5 Campaign C2 — two-stage tail closure (CUSUM m = 5, cells 305–309)

Additive namespace. Start: `p5y-postk1-frontier` at `5289b6ce`. Nothing outside this namespace is modified; AWS
SR/PS1 untouched; `main` untouched.

C2 is the successor to two complete negative/partial feasibility campaigns, and it does not reopen either:

- **Campaign B** (`p5y_k5_m5_tail_closure`) stopped before freeze; route T2 invalidated; cell 305 soundly closed
  under repaired TC-T arithmetic and **not adopted**.
- **Campaign C1** (`p5y_k5_tail_operator_registry`) stopped before freeze at MARGINAL; the tail operator registry
  certified 5/5 but atom deflation bought only 1.10–1.13× on A0 and made A2 **worse** by 1.25–1.36×; cells 305 and
  306 closed and **not adopted**.

C2 runs two stages, and the second is reachable only through its own separately frozen sub-gate:

| stage | what it does | new real addresses |
|---|---|---|
| **D** — deterministic | finer taboo partition, per-sub-block denominator certification, and a *pre-registered* componentwise minimum over every valid certified supply | 0 |
| **R** — real order-3 | the minimum address set the D-stage residual analysis supports, only if D leaves cells open and the residual is order-3-attributable | forecast-gated, capped |

## The governance lesson C2 encodes

Each predecessor lost its campaign to a gate defect, and C2's gate is written against both:

- Campaign C1 measured progress as a fraction of the raw residual requirement. C2 measures it as a fraction of the
  **gap above 1**, because a cell closes when its requirement reaches 1 — that is the scale-correct quantity, and
  C1's 10 % threshold is deliberately **not** inherited.
- Campaign C1 declined the componentwise minimum of two valid certified supplies because its gate specified one
  supply. C2 **pre-registers the minimum**, which is the legitimate way to obtain it.
- Both campaigns computed a sound closure of cell 305 and adopted nothing, because each gate demanded more than one
  cell. C2's `D_PARTIAL` rule states in advance that a non-empty closed subset is **always** adopted when the
  adjudication chain completes: an adopted cell is permanent progress that costs no new real compute.

| phase | where | state |
|---|---|---|
| B0. read-only verification | `code/c2_b0_verify.py`, `evidence/phase_b0/` | 7/7 PASS |
| gate (frozen **before** any forecast) | `config/FEASIBILITY_GATES_C2.json` | frozen at `87309610`, sha `098dd7f5…`, never modified |
| D1–D5 | `phase_d/` | **complete — `D_PARTIAL`** |
| R-stage design | `phase_r/` | complete, **design only**, blocked on a precondition |
| independent pre-freeze review r1 | `review/REVIEW_C2_PREFREEZE.md` | NOT_READY — **6 FAIL** |
| independent pre-freeze review r2 | `review/REVIEW_C2_PREFREEZE_R2.md` | NOT_READY — **3 FAIL** |
| independent pre-freeze review r3 | `review/REVIEW_C2_PREFREEZE_R3.md` | NOT_READY — **1 FAIL** |
| independent pre-freeze review r4 | `review/REVIEW_C2_PREFREEZE_R4.md` | NOT_READY — **3 FAIL** |
| independent pre-freeze review r5 | `review/REVIEW_C2_PREFREEZE_R5.md` | NOT_READY — **2 FAIL** |
| independent pre-freeze review r6 | `review/REVIEW_C2_PREFREEZE_R6.md` | NOT_READY — **1 FAIL** |
| independent pre-freeze review r7 | `review/REVIEW_C2_PREFREEZE_R7.md` | NOT_READY — **2 FAIL** |
| independent pre-freeze review r8 | `review/REVIEW_C2_PREFREEZE_R8.md` | NOT_READY — **3 FAIL** |
| independent pre-freeze review r9 | `review/REVIEW_C2_PREFREEZE_R9.md` | NOT_READY — **3 FAIL** |
| independent pre-freeze review r10 | `review/REVIEW_C2_PREFREEZE_R10.md` | NOT_READY — **3 FAIL** |
| independent pre-freeze review r11 | `review/REVIEW_C2_PREFREEZE_R11.md` | NOT_READY — **2 FAIL** |
| independent pre-freeze review r12 | `review/REVIEW_C2_PREFREEZE_R12.md` | NOT_READY — **2 FAIL** |
| independent pre-freeze review r13 | `review/REVIEW_C2_PREFREEZE_R13.md` | NOT_READY — **3 FAIL** |
| erratum and review disposition | `ERRATUM_C2.md` | every FAIL from every round dispositioned |

*FAIL counts only. Each review's PASS/NOTE/INFO breakdown is in its own file and is deliberately not transcribed
here: a previous version did transcribe them, and one was wrong — not through miscounting but by faithfully
copying a self-report that did not reconcile with its own stated total. See `ERRATUM_C2.md`, r5 FAIL 2. The FAIL
counts are the ones that reconcile against the disposition rows in the erratum.*

*(This README was first written as a pre-registration and committed with the gate at `87309610`; it has been
edited since. The phase table's D1–D5 and R-stage rows read "—" in that version, its B0 and gate rows already read
`7/7 PASS` and `frozen at this commit`, and its closing line is unchanged from it. The review rows, the Result
section and these notes were added after C2's numbers existed. To see exactly what was pre-registered, read
`git show 87309610:…/README.md` rather than trusting a description of it here.)*

## Result

| cell | Γ | margin | gap fall vs the C1 baseline | outcome |
|---|---|---|---|---|
| 305 | **−0.088029** | 1.353× | — | **closes**, survives ×1.25 degradation |
| 306 | **−0.030469** | 1.112× | — | **closes**, does *not* survive ×1.25 |
| 307 | +0.033133 | 0.891× | 46.29 % | open, materially tightened |
| 308 | +0.102700 | 0.705× | 24.59 % | open, materially tightened |
| 309 | +0.162249 | 0.579× | **18.39 %** | open, **misses** the frozen 20 % bar |

`D_STAGE_CLASS = D_PARTIAL`, closed = {305, 306}, still open = {307, 308, 309}. `D_USEFUL` requires every
still-open cell to be materially tightened and fails on one cell by 1.6 percentage points. 2.69 CPU-h of
deterministic operator certification; **0 new real scientific addresses**; guard DENY.

**Read `ERRATUM_C2.md` before relying on anything here.** Every independent pre-freeze review so far has returned
NOT_READY; they are listed in the table above, and `ERRATUM_C2.md` carries the same list with each round's
disposition.
Between them they reproduced every decision-relevant number bit-exactly and found **no arithmetic error in the
D-stage result** — the class, the closed subset and the gap falls have never moved. What they found was a
critical-ratio column labelled with the wrong campaign (overstating C2's own contribution ~2×), a diagnosis
document contradicting its own evidence file, a directionally inverted sentence in the frozen gate, cell 306 being
adopted on a margin judged sufficient after it was seen, a registry verifier that could never pass, sensitivity
figures computed outside the Lemma Dv′ hypotheses, and — repeatedly — an error introduced by a *repair* to a
previous round. That last is a documented failure mode of this campaign's authorship; its anatomy and its running
tally are in `ERRATUM_C2.md` §"The pattern, named".

Nineteen leaves of committed evidence have been replaced, across three files, and they divide 9 + 4 + 6. The
**nine** are the one scientific correction: the C_T sensitivity row for cells 307/308/309 of the D1 diagnosis,
brought inside the Lemma Dv′ admissibility premise. The **four** are the adversarial suite's own counts after it
was extended at the first review's request. The **six** are free text and wall-clock timings in
`C2_RECERTIFY_306.json`. A published **table** was separately corrected against evidence that never changed — D1
§1's ranking of the three negligible blocker terms. The full ledger, and the command to rebuild it rather than
trust it, are in `ERRATUM_C2.md` § "Replacement ledger".

**No Γ, magnitude, margin, requirement, gap fall, class or adopted-subset value has changed at any point** — four
independent reviews (r5, r6, r7, r8) each confirmed this by diffing every leaf of the D1 evidence across its whole
commit history.

**The R stage is blocked, and not by C2's own finding.** A sound operator-level combination C2 did not pre-register
clears the gate's own 20 % bar on all three still-open cells at zero cost — so "the deterministic direction is
exhausted" is not established. See `phase_d/D_PRIME_OPPORTUNITY.md`.

K5 remains **PARTIAL** (m = 5 open on 305–309); coverage map r4 (`a3bddd83…`) is authoritative and no r5 exists.
