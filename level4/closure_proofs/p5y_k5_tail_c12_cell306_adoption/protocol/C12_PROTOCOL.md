# C12 — cell-306 adoption campaign under K5 tail adoption floor r2 (prospective freeze)

**Status at this commit:** FROZEN, prospective. Nothing about Γ under any supply that contains an I2 constant has been
computed, estimated or inspected. The freeze commit holds `code/` and `protocol/`. Everything after it is evidence and
may not change them (the driver refuses to execute if they differ from the freeze commit).

**Authority.**
- Floor r2 (rule `a15d083b`, review `3fadb422` REPLACEMENT_FLOOR_ACCEPTED) and its gate G00–G14.
- N9 CLOSED (`7d67989d` / `fb237288`).
- The user's overnight campaign instruction of 2026-09-26: Phase A, cell 306 first. It authorizes this campaign to run
  through its chain without waiting, but never past a blocking verdict.

**Scope.**
- Cell 306 at m = 5 only.
- Cell 305 appears only as a historical I1 control rehearsal (already adopted by C2; nothing is decided about it).
- Cells 307–309 are refused by the driver, and nothing in this campaign evaluates them.
- r5 is read, never written.

## 1. What is computed, and by what

| item | definition | binding |
|---|---|---|
| consumer | C2's frozen path, reused verbatim from pinned bytes: `c2_d5_forecast.direct` (K5-B direct clause), `combine` (the D4 rule), `_atom_independent`; `deflated_consume.atom_constants_r2`; `tct_rule` (Lemma G, TC-T enclosure and its crosscheck, the derived identity gate, `load_frozen('tc_rule')`); `tail_forecast_r2.module` for the E6 adapter (frozen loader, `cells.json`) | `code/c12_cell306.py` `PINS` (sha256 of every file) and `BLOBS` (git blob ids). All unchanged since C2's forecast commit `5a94568a`. |
| non-supply inputs | `TCT_INPUTS_306.json`; `ADOPTED_TAIL_INPUTS.json` (C_upper, auxiliary_evidence, eps_cell_refined, per-m intervals), bound to the K1 record sha256 = the adopted composite export manifest entry for cell 306; the cover cell from `cells.json` | pinned |
| S_I1 | min componentwise {G, Dv′(REGISTRY_C1 block 306), Dv′(REGISTRY_C2 block 306)}. This is C2's adopted supply, the chosen supply fixed by floor r2. | pinned registries |
| S_I2 | min componentwise {G, Dv′(I2)}. I2 = C_T, τ, Ā, D_lo from `C11R_COMPARISON.json` `result.per_target[k].independent_value` plus D1, D2 from `C11RD_COMPARISON.json` `per_target[k].independent_value`, which must equal `C11RD_RUNS.json` `targets[k].value`. | pinned |
| Γ(5, 306; S) | exact rational from `direct`; pass iff Γ < 0 | — |

**Substitution disclosed.**
- **What changed.** C2 read C_upper, auxiliary_evidence and the m = 5 intervals from the off-host K1 record store.
  The driver reads the identical fields from the committed `ADOPTED_TAIL_INPUTS.json`, which Campaign B extracted from
  that record under a manifest check.
- **How it is checked.** The G10 control is an exact reproduction, string for string, of C2's committed cell-306 record:
  Γ, the atom constants, per-field provenance, the enclosure, M, and the pass flag. That control is the end-to-end proof
  that the substitution is exact for this quantity.
- **What is not reproduced.** C2's 310-cell replay gate needs the full record store. It is not re-run here. It is a
  property of the whole adopted state, not of cell 306's Γ, and C2 recorded it as PASS.

## 2. Order of operations (exactly as the driver enforces it)

1. **Freeze** (this commit): the driver, verifier, r6 generator and this protocol.
2. **Qualification** (`code/c12_verify.py`, at the freeze commit), covering:
   - static structure;
   - temporal integrity;
   - real-repository read-only runs: preflight, plus the I1 control for 306 and for the non-target 305;
   - CLI negative controls in a sparse sandbox, whose baseline must pass first;
   - function-level negative controls;
   - the r6 generator on synthetic data;
   - leak scans.

   The verifier evaluates no target.
3. **Qualification review.** A fresh read-only reviewer writes `review/C12_QUALIFICATION_REVIEW.md` with line 2 exactly
   `QUALIFICATION_ACCEPTED` or `QUALIFICATION_REJECTED`, and it is preserved in its own commit. A rejection stops Phase A.
4. **Grant.** `authorization/C12_GRANT.json`, alone in its own commit, binds:
   - the freeze commit, the qualification commit and the review commit;
   - the driver sha256;
   - the user's authorization.
5. **Execute.** `c12_cell306.py execute`, at HEAD = the grant commit, with a clean tree, runs these steps in order:
   1. grant, bindings and governance state;
   2. **G10 control** on S_I1, which must reproduce C2 exactly. Otherwise it seals CONTROL_FAILED and the target is never
      touched;
   3. every I2 check: classes, statements, domain = cell 306's cover cell exactly, validation, and the atom crosscheck;
   4. create `refs/c12/cell306-target-consumed` (CAS on non-existence);
   5. **one** evaluation of Γ(5, 306; S_I2);
   6. write `evidence/execution/C12_CELL306_RESULT.json` and **seal** it: a commit through a private index with CAS on the
      branch. The driver prints only the status and the seal commit.
6. **Execution review.** A fresh reviewer writes `review/C12_EXECUTION_REVIEW.md`, line 2 `EXECUTION_ACCEPTED` or
   `EXECUTION_REJECTED`, and independently re-derives Γ under both supplies from the committed inputs.
7. **Adoption adjudication.** A fresh, independent adjudicator writes `adjudication/C12_ADOPTION_ADJUDICATION.md`, line 2
   `CELL306_ADOPTED` or `CELL306_NOT_ADOPTED`. If adopting, it includes a block `## ADOPTED CELL SET` with `[306]`. It
   applies floor r2 only.
8. **Adjudication review.** A fresh reviewer writes `review/C12_ADJUDICATION_REVIEW.md`, line 2 `ADJUDICATION_ACCEPTED` or
   `ADJUDICATION_REJECTED`.
9. **Coverage.** Only if 7 is `CELL306_ADOPTED` and 8 is `ADJUDICATION_ACCEPTED`:
   `code/c12_r6_from_adjudication.py` mechanically generates r6 as a successor of r5. The only change is that (5, 306)
   moves OPEN → PASS, with lineage. It refuses otherwise, and it never writes r5.

## 3. Decision table (floor r2, frozen)

| quantity | rule |
|---|---|
| base clause | Γ(5, 306; S_I1) < 0 (S_I1 is the chosen supply) |
| F1′ (a)–(c) | I1 and I2 each certified all six constants on the whole block; six AGREES/STRONGER with EQUIVALENT/STRONGER statements in accepted comparisons; soundness evidence per implementation (floor r2 §6). Checked by the driver's bindings and I2 checks (G05–G07). |
| F1′ (d) | Γ(5, 306; S_I1) < 0 **and** Γ(5, 306; S_I2) < 0, separately; never a mixed supply |
| F2 | NOT_SATISFIED. C2 published the F2 failure on S_I1 for 306. Floor r2 does not revisit it, and this campaign does not re-evaluate it. |
| floor r2 satisfied | base AND (F1′ or F2), i.e. base AND F1′ |
| adoption | floor r2 satisfied AND G13: EXECUTION_ACCEPTED, then an independent adjudication applying r2, then ADJUDICATION_ACCEPTED |
| closure disagreement | Γ(S_I1) < 0 but Γ(S_I2) ≥ 0: F1′ fails, the cell is NOT adopted, and the disagreement is recorded. No re-evaluation. |

STRONGER is not evidence of soundness. Soundness rests on each implementation's own evidence (floor r2 §6), and F1′ is
correct if either implementation is sound.

**Scientific closure versus the other layers.**
- Scientific closure (Γ < 0 under a supply) is a fact about the cell.
- Floor satisfaction is the table above.
- Adoption is the adjudication.
- Coverage publication is r6.

These four are recorded separately and never conflated.

## 4. Gate G00–G14 → where each is enforced

| gate | enforced by |
|---|---|
| G00 floor r2 in force | `LINEAGE` (a15d083b, 3fadb422); `PINS` floor rule, gate and review; the rule's self-hash; exactly one `REPLACEMENT_FLOOR_ACCEPTED` on line 2 |
| G01 N9 CLOSED | `N9_CLOSED` / `ADJUDICATION_ACCEPTED` line-2 checks on pinned bytes |
| G02 entry state | r5 pinned, union open exactly [[306, 309]], 306–309 not PASS; no r6 (tree, history, working tree) |
| G03 prospective freeze | this commit; the driver refuses if code/ or protocol/ changed after it; the verifier evaluates no target |
| G04 I1 inputs | `registry_c1`, `registry_c2` and the consumer path, pinned |
| G05 I2 inputs | C11R and C11RD comparisons and C11RD runs pinned; D1/D2 value identity with the sealed runs; statements; domain equal to the cover cell |
| G06 per-constant agreement | classes in {AGREES, STRONGER}; statements in {EQUIVALENT, STRONGER}; accepted reviews' verdict lines |
| G07 soundness and residuals | floor r2 §6, carried into the adjudication's disclosure |
| G08 no mixing | `supply()` refuses any set of another implementation; S_I1 and S_I2 are built separately |
| G09 validation and κ | `validate_set`; the atom crosscheck; κ equal between the consumer and C2's local copy |
| G10 control | `control()` exact field-by-field reproduction, before anything about I2 |
| G11 one sealed evaluation | consumed ref (CAS); the result is written and sealed before any interpretation |
| G12 decision table | §3 |
| G13 review and adjudication | §2 steps 6–8; r6 only by `c12_r6_from_adjudication.py` after them |
| G14 scope | cells 307–309 refused; r5 never written; historical verdicts untouched |

## 5. Stopping rules and caps

**Stop Phase A, preserve the evidence and do not improvise** if any of these occurs:
- any refusal before consumption;
- CONTROL_FAILED;
- TARGET_EVALUATION_FAILED;
- UNSEALED, in which case run `seal-only` only;
- a REJECTED qualification, execution or adjudication review.

**Caps and exactly-once rules.**
- **Wall-clock cap:** 900 s per driver invocation.
- **Expected execution:** a few seconds, with zero new real scientific addresses and no host other than this machine.
- **The exactly-once ref is never deleted.** The target is never evaluated twice.

## 6. Prospective coverage table (at freeze)

| cell | scientific closure | floor r2 eligibility | adoption adjudication | authoritative coverage |
|---|---|---|---|---|
| 306 | S_I1: Γ < 0 (C2, historical). S_I2: not evaluated. | pending G11 | none | OPEN (r5) |
| 307 | not closed (historical) | F1′ unavailable (no I2); out of this campaign's scope | none | OPEN (r5) |
| 308 | not closed (historical) | out of scope | none | OPEN (r5) |
| 309 | not closed (historical) | out of scope | none | OPEN (r5) |

## 7. Statement at freeze

- No Γ, atom constant, margin or F2 value has been computed, estimated or inspected for any supply containing a C11R or
  C11RD constant.
- The only Γ evaluations run while building this freeze were the I1 controls for cells 306 and 305. Both reproduce C2's
  committed, pre-N9 records exactly.
- Nothing in this protocol depends on any post-N9 magnitude.
