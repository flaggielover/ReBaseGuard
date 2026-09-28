# Cell-307 RLR formal prospective closure campaign (r1): frozen protocol

**Status at the freeze commit.** FROZEN and prospective.
* Γ(5, 307) under any RLR-bearing supply has been evaluated **0** times, by anyone.
* No marker, grant, result or seal exists.
* The freeze commit is the last commit touching `code/`, `protocol/`, `theory/`, `tests/` or `config/` of this
  namespace. The driver derives it from git and refuses a grant chain that does not start there.

**Question answered by this campaign, once:** does the prospectively frozen RLR certificate close cell 307 under the
existing frozen K5 consumer?

## 1. Scope and authority

| item | value |
|---|---|
| cell | CUSUM, m = 5, cell **307** only. The driver refuses every other target cell. It evaluates nothing on 306, 308 or 309 |
| route | RLR (overnight route, FREEZE_READY closure-only at `d3b60795`), unchanged; §3 lists the additions this campaign needs |
| interpretation | **CLOSURE_ONLY.** It does **not** mean adoption, a floor-r2 change, a floor extension, r6, K5 closure, P5Y closure or a publication update |
| authority | The user's campaign brief ("Cell 307 RLR Formal Prospective Closure Campaign", 2026-09-28). It authorizes this freeze, qualification and an independent qualification review. **After, and only after, QUALIFICATION_ACCEPTED** it authorizes one explicit grant and one execution (brief §§12–21, §36) |
| gate before this freeze | independent incident-independence review `review/INCIDENT_INDEPENDENCE_REVIEW.md` (brief §4): INCIDENT_AUDIT_ACCEPTED, committed before this freeze |

## 2. Scientific object

* **Theorem.** `theory/THEOREM_RLR307.md`, Theorem RLR-307.
* **Certifier.** The overnight C1b certifier, executed from its pinned bytes by `code/rlr307_pinned.py`:
  * files: `c1b_gauss`, `c1b_kernel`, `c1b_float`, `c1b_pw`, `c1b_prov`, `c1b_certpw`;
  * sha256 as in `C1B_R2_CODE_PINS.json`;
  * load-bearing set unchanged since pins r1.
* **Stage 1.** `code/rlr307_stage1.py`, rules P1–P5 (§4).
* **Stage 2.** C2's frozen consumer from pinned bytes: `c2_d5_forecast.py` (blob `18403dbe`), `deflated_consume.py`
  (`a0a836fa`), `tct_rule.py` (`98f6eee4`), `tail_forecast_r2.py`, the consumption adapter, and the K5-B direct
  clause.
* **Driver.** `code/rlr307_driver.py`.
* **Independent reconstruction.** `code/rlr307_independent.py`.

## 3. Decisions this campaign adds

None of these existed overnight, so each is new. Each is fixed before any target computation, and each has a
target-free reason.

| # | decision | value | reason (no target quantity involved) |
|---|---|---|---|
| 3.1 | dyadic hull | each C2 sub-block is certified on its outward hull on the 2^-20 grid | The pinned integer Taylor model (`c1b_kernel.gf_box_int` → `_dy_exp`) accepts only dyadic centres and radii, and the C2 partition endpoints are decimal. 2^-20 is the certifier's own scaling grid (D3). Superset ⇒ valid (Lemma H) |
| 3.2 | degree ladder for blocks | **LADDER** (see §3.2 below) | fixed by the rule below from decoy costs only |
| 3.3 | ladder and cell composition | the pinned CLI's ladder composition (`run_point`: LADDER_KEYS_MIN / MAX, then `assemble`); cell = componentwise max over blocks of A1/A2_SUPPLY | C1B §8 item 6; protocol draft §2 ("componentwise max over the cell's blocks") |
| 3.4 | A0 | the committed I1 value, unchanged | protocol draft §2–§3 |
| 3.5 | consumed supply | S_RLR = (A0_I1, min(A1_I1, A1_cell), min(A2_I1, A2_cell)) | protocol draft §3 |
| 3.6 | flags | TIGHT_CT = BLOCK_LIGHT = True, set explicitly, never read from argv | the pinned, reviewed block rung `C1B_R2_PW_BLOCK_1_2__17_32_d4.json` records exactly these |
| 3.7 | rung exceptions | an exception raised inside the pinned `certify_degree` makes that rung NOT certified (recorded). MemoryError, OSError, worker death, the cap and signals are **execution failures** | a deterministic certifier failure is a scientific non-certificate; infrastructure is not |
| 3.8 | parallelism | 5 spawned worker processes. Results are assembled by (block, degree) key, independent of scheduling | worker count and order cannot change any number (Q3 tests it) |
| 3.9 | caps | pre-marker 1800 s; evaluation after the marker EVAL_CAP (§3.2) | a timeout makes the one evaluation INDETERMINATE, so the cap is set well above the decoy-measured cost |
| 3.10 | keep-awake | `caffeinate -i -w <pid>` | environmental only |

### 3.2 Ladder and cap rule (frozen before any target computation; decoy-cost only)

**Declared rule.**
* The block ladder is the D8 ladder (4, 6, 8), as C1B §8 item 2 binds it ("PW_d … with the degree ladder").
* The one exception: if the decoy-measured Stage-1 cost of cell 307's 10 blocks, projected from the qualification
  decoy blocks at 5 workers, would exceed **4 h** of wall time, the ladder is truncated from the top: (4, 6), then
  (4).
* EVAL_CAP is 2× the projected wall time, rounded up to whole hours, and at least 6 h.

**Measured decoy costs** (pre-freeze exploration, `evidence/explore/TIMING_*.json`, six concurrent jobs):

| decoy block (hull) | degree | status | wall s | CPU s | peak RSS |
|---|---|---|---|---|---|
| cover cell 297, block 0 | 4 | CERTIFIED | 222.3 | 201.4 | 56 MB |
| cover cell 297, block 0 | 6 | CERTIFIED | 1325.8 | 1187.1 | 64 MB |
| cover cell 297, block 0 | 8 | CERTIFIED | 2034.3 | 1787.8 | 70 MB |
| cover cell 316, block 0 | 4 | CERTIFIED | 130.4 | 115.7 | 56 MB |
| cover cell 316, block 0 | 6 | CERTIFIED | 1285.8 | 1149.7 | 65 MB |
| cover cell 316, block 0 | 8 | CERTIFIED | 2311.3 | 2063.6 | 70 MB |

Only runtime, memory and status are used here (latent-proxy rule, review condition C2); no certified value of any decoy
is read by this rule.

**Projection for cell 307** (10 blocks x 3 rungs, per-rung cost = the larger decoy wall time at that degree:
222.3 / 1325.8 / 2311.3 s; 5 workers, longest-first scheduling as in the driver):
* ten degree-8 jobs take 2 rounds x 2311.3 s = 4622.6 s;
* ten degree-6 jobs take 2 x 1325.8 s = 2651.6 s;
* ten degree-4 jobs take 2 x 222.3 s = 444.6 s.

The total is **7718.8 s = 2.14 h**, which is ≤ 4 h.

**Resulting values:** the ladder is the full D8 ladder **(4, 6, 8)**; EVAL_CAP = max(6 h, ⌈2 x 2.14 h⌉ = 5 h) = **6 h = 21600 s**
(`rlr307_driver.EVAL_CAP_S`); pre-marker cap 1800 s; 5 workers. Fixed from the decoy costs above only.

## 4. Stage 1 (rules P1–P5, `code/rlr307_stage1.py`)

* **P1, partition.** The cover interval [x_lo, x_hi] of cell 307 (`cells.json`, cross-checked against REGISTRY_C2's
  e_lo, e_hi and its sub-block count) is split into N = max(1, ⌈(x_hi − x_lo)/(1/100)⌉) equal sub-blocks. This is C2's
  rule; N = 10.
* **P2, hull.** Each sub-block is widened to its outward 2^-20 dyadic hull.
* **P3, rungs.** On every hull block and every ladder degree, the driver runs the pinned `certify_degree(centre, d,
  BW_PW, e_r = radius)`: e-free PW_d candidate, D11 light enclosures, D13 coverage.
* **P4, ladder composition.** Only CERTIFIED rungs count. The block record is the ladder composition, then D14
  `assemble`. A block with no certified rung is NOT_CERTIFIED.
* **P5, cell composition.** If all blocks are certified, A_j^cell = max over blocks of A_j_SUPPLY. Otherwise the
  outcome is **CERTIFICATION_FAILED**, with no retry and no other settings.

## 5. Stage 2 and the control

**Control, before the marker.** Cell 307 under S_I1 = min{G, Dv′(REGISTRY_C1), Dv′(REGISTRY_C2)} through the frozen
consumer must reproduce C2's committed record (`C2_D5_FORECAST.json`, cell 307) **exactly**. The compared fields are
Gamma_exact, A_exact, provenance, H_exact, M_after_exact, pass, and the per-supply records.
* The control recomputes a committed historical record and uses only the equality result, so it creates no new
  target information.
* It is counted separately as a "historical reproduction control". It is **not** a new Γ307 evaluation.
* If it fails, the status is CONTROL_FAILED: sealed, target **not** consumed, campaign stops.

**Target, after the marker.**
1. Stage 1.
2. If the cell is certified: S_RLR (§3.5), then the consumer's `direct` clause, giving Gamma_exact and `pass`
   (Γ < 0, exact rationals).
3. Every composition layer must equal its independent reconstruction exactly (§6). Otherwise the status is
   INDEPENDENT_CHECK_FAILED.

## 6. Independent reconstruction (brief §10) and the shared code surface

`code/rlr307_independent.py` was written from THEOREM_RLR307 §1. It does not import the certifier, Stage 1 or the
driver. It recomputes exactly:
* each rung's D14 supply from that rung's certified inputs;
* each block's ladder composition and block supply;
* the cell maximum;
* S_RLR;
* Lemma Dv′ r2 and Lemma G for the three I1 members, and their componentwise minimum;
* the κ constants (60+-digit decimal proof that κ1 ≥ √(2/π) and κ2 ≥ 4φ(1)).

**Shared surface, stated exactly.** The certified inputs (τ, C_T, Ā, C_R, τ_a,lo, D_lo, D1, D2, L1_up, L2_up) come
from one implementation, the pinned certifier. **They are not independently re-certified.**
* Their soundness rests on THEOREM_LR and THEOREM_AD, on the R2/R3 reviews, and on this campaign's qualification:
  * Q1 reproduction of the committed block record;
  * Q6 independent Monte Carlo consistency and lower-bound checks on decoys;
  * Q5 mutants.
* The consumer is C2's frozen consumer. It is not re-implemented. It is validated by exact reproduction of C2's
  committed records (Q2).

## 7. Exactly-once mechanics (C12-R2's validated seal-from-memory design)

**Names.**
* Marker `refs/p5y-k5-cell307-rlr-r1/target-consumed` → grant commit, created by CAS immediately before Stage 1.
* Pending ref `refs/p5y-k5-cell307-rlr-r1/pending-result`.
* Result `evidence/execution/RLR307_CELL307_RESULT.json`.
* Emergency file `<git dir>/rlr307-cell307-emergency-result.json`.

**Before the marker, the driver refuses if any of the following holds:**
* the identity (worktree, git dir, common dir, branch) or the interpreter flags (`-I -S -B`) are wrong;
* a marker or pending ref exists under `refs/p5y-k5-cell307-rlr-r1/` or `refs/rlr-tail/`;
* a result exists in the tree, on disk or in any history, or the emergency file exists;
* any object (lstat) exists at a guarded path;
* the tree is dirty, or the namespace contains an ignored or untracked object;
* the grant chain is not exactly freeze → qualification → review → grant, the qualification is not an official PASS
  at the freeze, the review verdict is not QUALIFICATION_ACCEPTED, or the grant does not bind the driver sha256 and
  the input manifest sha256;
* any input pin (sha256 and git blob) or any helper pin fails;
* the lineage is wrong, or r5 is not as expected, or r6 exists;
* any seal precondition fails;
* the cell-307 geometry cross-checks fail;
* the κ check fails;
* the control fails.

**After the marker:**
* signals are ignored in the parent and in every worker;
* the evaluation has its own cap;
* every exception becomes sealed evidence;
* the evidence goes to the object store and pending ref, with the fallback file as the second channel, before any
  seal;
* the seal is a commit through a private index;
* the worktree copy is created with O_EXCL|O_NOFOLLOW and read back.

**Worker processes** (spawned) re-verify:
* the driver sha256;
* the helper pins;
* the certifier pins and git blobs;
* the marker, through `rlr307_guard.arm_target`, before they may certify a band drift. Without the marker the guard
  refuses every drift in [6/5, 13/5] (Q9 tests this).

**Retry and recovery.**
* A consumed marker never becomes "safe to rerun".
* `seal-only` never computes.
* If result information is lost after the marker, nothing is recomputed without a new independent governance process.

## 8. Frozen outcome table and closure criterion

| sealed status | condition | cell-307 conclusion (the adjudication applies this table verbatim) |
|---|---|---|
| TARGET_EVALUATED | Stage 1 CERTIFIED, the independent checks all equal, and the consumer's `pass` is True, i.e. **Γ(5, 307; S_RLR) < 0 in exact rationals** | **CELL307_CLOSED_UNDER_RLR** |
| TARGET_EVALUATED | Stage 1 CERTIFIED and Γ(5, 307; S_RLR) ≥ 0, **including Γ = 0 exactly** | **CELL307_NOT_CLOSED_UNDER_RLR** |
| TARGET_EVALUATED | Stage 1 CERTIFICATION_FAILED: some block has no certified rung | **CELL307_NOT_CLOSED_UNDER_RLR** (reason RLR_CERTIFICATION_FAILED; no Γ under S_RLR exists) |
| TARGET_EVALUATION_FAILED, INDEPENDENT_CHECK_FAILED, POST_MARKER_RECORDING_FAILED, or evidence unsealable | any execution failure after the marker | **CELL307_EXECUTION_INDETERMINATE** (target consumed; no rerun) |
| CONTROL_FAILED | the control does not reproduce C2's record | no conclusion. Target not consumed; campaign STOPS |

The following never change after the freeze: strictness (<), tolerance (none), rounding (exact rationals), the sign
rule, the margin (none), the floor and the adoption semantics.

**Closure is not adoption.** Even CELL307_CLOSED_UNDER_RLR means only that the frozen supply certifies the K5-B
inequality for cell 307. It is not adoption in r5, not adoption under floor r2, not r6, not K5 CLOSED and not P5Y
CLOSED.

## 9. Qualification

The qualification cases, frozen before any is run, are in `config/QUALIFICATION_CASES.json`. The gates Q1–Q12 are
evaluated by `code/rlr307_qualify.py` at the freeze commit. The mapping, with details in the cases file:

| gate | meaning | cases |
|---|---|---|
| Q1 | theorem integrity | formulas of THEOREM_RLR307 = independent module = pinned assembly (QC05), plus the independent reviewer's proof check |
| Q2 | implementation identity | QC01 committed-block reproduction; QC08 consumer rehearsal (cell 305); pins; module identities; QC11 static checks |
| Q3 | deterministic reproducibility | QC01 (fresh process = committed bytes); QC03 serial rerun = pooled result, exactly |
| Q4 | exact arithmetic | QC05 type checks (a float reaching an exact layer raises); records carry exact rationals only in consumed fields |
| Q5 | two-sided certificate test | QC05: the six historical mutants rejected (6/6), plus the composition-layer mutants |
| Q6 | non-target soundness | QC02 decoy Stage 1; QC04 independent Monte Carlo consistency and a certified-A1 ≥ \|Λ′\| check |
| Q7 | min-composition soundness | QC05 planted cases (each supply smallest in turn); QC09 S_RLR construction |
| Q8 | provenance | every input pinned by sha256 and git blob; `protocol/RLR307_FREEZE.json` manifest |
| Q9 | target quarantine | QC07 guard and arming controls; QC12 leak scan; ledger classes |
| Q10 | temporal integrity | QC13: HEAD = freeze; no review, grant, marker or result; the incident review is committed before the freeze |
| Q11 | incident independence | `review/INCIDENT_INDEPENDENCE_REVIEW.md` line 2 = INCIDENT_AUDIT_ACCEPTED |
| Q12 | execution safety | QC10 exactly-once flows in a `git clone --shared` sandbox; QC11; costs vs caps |

**No gate may be waived.** Every gate must PASS before the independent qualification review.

**How the verifier runs.**
* The official run writes only `qualification/` files. It computes QC01–QC03 in fresh processes: QC02 through the
  driver's own `decoy-stage1` CLI, and QC03 as a serial rerun.
* The independent reviewer may run `rlr307_qualify.py --review --out <file outside the repository>` at the
  qualification commit. `--heavy` recomputes QC01–QC03, which takes about 1 h. Without it, the committed records are
  re-verified.

## 10. Order of operations and STOP conditions

1. Freeze (this commit).
2. `code/rlr307_qualify.py --out qualification/RLR307_QUALIFICATION.json` at the freeze commit, committed as
   qualification evidence only.
3. A fresh independent qualification review writes `review/RLR307_QUALIFICATION_REVIEW.md`. Line 2 is exactly
   QUALIFICATION_ACCEPTED or QUALIFICATION_REJECTED. The review is committed alone.
   **If REJECTED: STOP. No same-round repair.**
4. The grant, committed alone (`authorization/RLR307_GRANT.json`). It binds:
   * cell 307 and route RLR;
   * the freeze, qualification and review commits;
   * the driver sha256 and the input-manifest sha256;
   * exactly once, closure-only, no adoption, no floor change.
5. `execute`, once, at the grant commit, then the post-execution checks (brief §23).
6. Independent execution review: EXECUTION_ACCEPTED or EXECUTION_REJECTED. **If REJECTED: STOP.**
7. Cell-307 scientific adjudication, applying §8 verbatim.
8. Independent adjudication review: ADJUDICATION_ACCEPTED or ADJUDICATION_REJECTED. **If REJECTED: STOP.**
9. Handover.

**Additional STOP conditions (brief §35):**
* the start state differs;
* the incident review rejects;
* the target appears consumed, or a result exists;
* input or freeze files drift;
* qualification data includes 307 or any equivalent proxy;
* the exactly-once infrastructure is found unsafe.

## 11. Disclosed liabilities (carried into the grant and the adjudication)

* **Overnight incident 01 and its residue (L1, L4).** A qualitative co-location of the LR route's synthetic slack
  factor with committed tail radius structure. No number was combined.
* **Motivation provenance.** The route and cell were chosen knowing the committed C3 knockout. Result-chasing risk
  MEDIUM.
* **Coordinator knowledge.** The campaign coordinator knows the RLR validation-drift values and the committed per-cell
  factors. No combination is written, and the §3 decisions are rule-based.

See `audit/INCIDENT_AUDIT_RLR307.md` and the independent review.

## 12. Ledger and quarantine

* `ledger/ZERO_TARGET_LEDGER_307.jsonl` records every computation. Pre-grant classes only: START_STATE_READ,
  HISTORICAL_READ, NONTARGET_DECOY, SYNTHETIC, GOVERNANCE.
* **Qualification.** The qualification commit may hold qualification files only, so the qualification's ledger lines
  are carried inside `RLR307_QUALIFICATION.json` (`ledger_entries`). They are appended to the ledger after the seal,
  together with the execution's line.
* **Target execution.** It writes no ledger line before its seal. The sealed result is its record, and the ledger line
  follows the seal.
* Drift quarantine: `code/rlr307_guard.py`.
