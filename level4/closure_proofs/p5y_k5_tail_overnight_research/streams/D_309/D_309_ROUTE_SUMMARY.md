# Stream D (cell 309: leave the exhausted constant family) — route summary

**Status.** Research, target-free, overnight 2026-09-28.

| quarantine item | tally |
|---|---|
| new target evaluations | 0 |
| target-equivalent proxies | 0 |
| target-informed optimisation | 0 |
| drifts touched | synthetic FSM parameters ≤ 3/8, and the CUSUM kernel at e ∈ {0, 1/4, 1/2, 1, 3} ± 2·10⁻⁴ |
| static scan | 0 findings in the seven `code/*.py` files |

Ledger entries are `SYNTHETIC_VALIDATION` and `NONTARGET_DRIFT_VALIDATION` only.

**Rule S8.** No route factor appears next to a committed tail-cell share, factor or margin in any file of this stream.
Committed history lives only in `SCOPED_NEGATIVE_FAMILIES_309.md` §1, `COVER_REFINEMENT_309.md` §9 and
`RESIDUAL_SPECIFIC_309.md` §1.

## 1. Route rows

Gate values: P = PASS, p = PARTIAL (internal dual paths, no external review).

| route | document | state | G1 | G2 | G3 | G4 | G5 | G6 | G7 | G8 | G9 | G10 | floor r2 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **SC** composite-sup premise supply (SC-3, SC-4w, TC⁺; SC-T; SC-S1) | SUPNORM_THEOREM.md | VALIDATED_NON_TARGET; real use BLOCKED | P | P | P | P | P | P¹ | P | P | P | P for exact sups³ | CLOSURE-ONLY |
| **CR** real cover refinement (CR-1..3, DRP-0/1) | COVER_REFINEMENT_309.md | VALIDATED_NON_TARGET (algebra); DRP-1 IMPLEMENTED (outcome-adaptive); real use BLOCKED (NEW_REAL) | P | P | P | P | P | P¹ | P | P | P | P | CLOSURE-ONLY |
| **B2** split without new records, fixed `(g_hi, L, U)` | COVER_REFINEMENT_309.md §4 | REFUTED **within the fixed-(g_hi, L, U) family** (CR-2 via TPT-O) | — | P | P | P | identity only² | P¹ | P | P | — | **fails within that family**: cosmetic | — |
| **B2c** record-free split with operator constants re-certified on sub-segments | COVER_REFINEMENT_309.md §4 | THEORY_ONLY (unevaluated) | P | — | P | — | — | — | P | P | — | not assessed | CLOSURE-ONLY |
| **RSO-C4** (original definition, `A0 f_H` only) | RESIDUAL_SPECIFIC_309.md | VALIDATED_NON_TARGET; structurally narrow | P | P | P | P | P | p | P | P | P | P for non-constant ψ | CLOSURE-ONLY |
| **RSO-P** (+ RSO-PM, needs SC for order 3) | RESIDUAL_SPECIFIC_309.md | VALIDATED_NON_TARGET; real use BLOCKED | P | P | P | P | P | P¹ | P | P | P | P iff ψ ≠ ‖ψ‖ μ-a.e. | CLOSURE-ONLY |
| **RSO-LR**, order 1 | RESIDUAL_SPECIFIC_309.md §3.2 | VALIDATED_NON_TARGET (single drift) | P | P | P | P | P | p | P | P | P | P | CLOSURE-ONLY |
| **RSO-LR**, order 2 | RESIDUAL_SPECIFIC_309.md §3.2 | THEORY_ONLY | P | sketch | P | — | — | — | P | P | — | — | CLOSURE-ONLY |
| **Assembly** (TPT) | `streams/E_assembly/THEOREM_TPT.md` (E stream) | referenced, not restated | | | | | | | | | | | CLOSURE-ONLY |

Footnotes (repair r1):
1. G6 upgraded from PARTIAL to PASS **for the mathematics** only: `reviews/REVIEW_STREAM_D_R1.md` §1–§3 re-derived
   the theorems independently, and its own quadrature confirmed Lemma HC.
2. "B2 − TPT = 0" is a transcription identity of the implementation, not validation evidence (review B3).
3. SC-S1 is strictness of the **exact** sup. A certified gain is not guaranteed (review N3).

**Common blockers for every real-use row.**
* **Payloads:** K1 candidate payloads were never serialized. No real cell, target or not, has them (checked:
  SUPNORM §8).
* **U1 (host):** the host needs numpy and python-flint. They are absent locally, and absent on the permitted worker
  (C6-N1).
* **U2 (admissibility):** new quantities derived from P3 records fall under C6 Condition 10.
* **U3 (floor):** a floor extension, frozen before any evaluation.
* **CR additionally:** new real K1 addresses (NEW_REAL, guard DENY).

## 2. Per-cell deliverable for 309

| item | result |
|---|---|
| scoped negative families | `SCOPED_NEGATIVE_FAMILIES_309.md`: F1 uniform-A0 (C4 / C5-T restatement), F2 two-input transport (C5), F3 C7 E2 ceiling, F4 C1 MARGINAL, F5 Campaign-B T2, F6 C8 R1/R2, F7 C5 B2/D2/A4. Each new route is shown to lie outside them on structural grounds (§2 there). |
| sup-norm result | Theorem SC is general. It does **not** reproduce the existing bound in other notation: SC-T shows the composite measures `‖(I−K)F_r'''(e0)‖` up to candidate errors, while the surrogate is its Leibniz triangle bound. SC-S1 proves strict submultiplicativity slack for continuous candidates on the Gaussian kernel. Validated exactly on FSM; the Hermite machinery and a stdlib Taylor-form certificate are validated on the real kernel at non-target drifts. **Not killed.** |
| cover result | Exact ρ-decomposition of the clause (CR-1). Within the fixed-(g_hi, L, U) family a record-free split is dominated by TPT (CR-2, via TPT-O). Lever B2c (constants re-certified on sub-segments) is outside that family and unevaluated. A real refinement removes `1−1/N` of the order-1 slack that TPT cannot touch, `1−1/N²` of the remaining order-2 slack and `1−1/N³` of order-3 (CR-3, leading order). The C5 "ρ halved" oracle is not a refinement model. DRP-0 (result-free) / DRP-1 (outcome-adaptive, frozen predicate) policies with a cost model. |
| residual-specific result | RSO-0 with the occupation-measure characterization (the shape factor `‖ψ‖/μ(ψ)`) and the collapse lemma: with constant ψ it is F1. RSO-PM and RSO-LR derivative extensions. RSO-P assembly. As originally defined (RSO-C4) the reach is structurally narrow; with SC's pointwise profile (RSO-P) the reach covers every order. |
| assembly result | `streams/E_assembly/THEOREM_TPT.md` (E stream). This stream relies on TPT for transport and on TPT-O for CR-2. |
| strongest surviving route | see §3 |
| **FREEZE_READY** | **no** |

## 3. Strongest surviving route (ranked by theoretical avoidable slack only)

**Criteria (S1).** The ranking uses only structure and asymptotic order:
* which terms of the clause a route acts on (`COVER_REFINEMENT_309.md` §2 table);
* whether its gain is proven strict;
* whether it needs new real objects.

No committed per-cell number and no synthetic ratio is used, per S1 and S8.

**1. SC + TPT: strongest route that creates no new real K1 object.**
* SC acts on the order-2 (`f_G`) and order-3 (`Env4`) channels of the clause. These are the channels that dominate the
  slack of any **wide** cell (`ρ r1 ≫ r0 + W`, §5 of COVER).
* The gain is strict for **exact** sups with continuous candidates on the Gaussian kernel (SC-S1). A certified
  gain is not guaranteed: certificate overhead 1.2–1.44× on the test functions.
* It is exactly the Leibniz gap between the surrogate and the true `‖(I−K)F'''‖` (SC-T).
* It composes with every atom-constant supply and with TPT.
* Its blocker is **data** (payloads + U1/U2), not mathematics or NEW_REAL.

**2. Real cover refinement: structurally the most powerful.**
* It acts on **every** ρ-order with factors `N^{−j}`, including the order-1 slack that SC and TPT cannot remove.
* It re-certifies the constants over a smaller cell.
* It changes the cell over which the uniform quantifiers of F1 are stated.
* Blocker: NEW_REAL addresses, plus U1/U3.

**3. RSO-P (∘ SC): a multiplicative refinement of SC.**
* It contributes the occupation shape factor on every term.
* On its own (RSO-C4) it is structurally narrow: it acts only on the order-0 residual term.
* Its blockers are those of SC plus a supersolution certificate per term.

## 4. FREEZE_READY: no

**Why not:**
1. **No payloads.** No payload exists on which any frozen stage could run. Regeneration needs a host (U1), and the
   derived quantity faces the P3 admissibility rule (U2).
2. **Closure-only.** Every route is closure-only under floor r2 (U3).
3. **Cover refinement** needs new real addresses under guard DENY.
4. **Review conditions.** An independent review exists (`reviews/REVIEW_STREAM_D_R1.md`, ACCEPTED_WITH_CONDITIONS).
   Its conditions are repaired in §7. It agrees that no route could honestly be FREEZE_READY.

**What could be frozen now, prospectively (G9):**
* the theorem statements;
* the certificate formats;
* the declared calibration rule for the SC certificate configuration (Taylor-form ranges, cover depth ≥ 5, panel 1/16;
  calibrated on synthetic degree-matched functions);
* DRP-0 / DRP-1 with a fixed depth and budget.

## 5. Negative results and limits recorded

**Negative results.**
* **B2 within the fixed-(g_hi, L, U) family is cosmetic** (CR-2 via TPT-O). The r0 "30/30" figure was an
  implementation identity and is withdrawn as evidence.
* **RSO-C4 barely moves the radius** on FSM: rad ratio 0.957–1.000.
* **RSO without SC** (normonly34): 0.80–1.00.
* **Constant ψ gives no gain.** `N0/(Λ‖ψ‖) ≥ 1` with a small certificate overhead.
* **SC equality case.** Sign-aligned discontinuous candidates on a general FSM kernel reach `S3 = S1`.
* **Naive interval certificates are vacuous** for a degree-9 function: about 10⁴× the grid lower bound.
* **The pure-scaling refinement prediction** errs by up to 37 %.

**Coverage limits.**
* **H1 kink control** misses 24 of 960 cases (all `w_bump` at one state, below tolerance). The independent
  quadrature comparator H1b misses 5 of 960.
* **Transport-level soundness checks are weak necessary conditions.** Examples:
  * FSM enclosure check: `Env4 := 0` detected 0/60, halved A0 1/60;
  * cover transport check: `rad_half` 0/140.
  The load-bearing checks are the premise-level and profile-level truth checks (§7).

## 6. Quarantine observations

* `ov_quarantine --scan` reports one finding in **another stream's** file, `streams/A_306/a306_reproduce_A.py`
  (`TARGET_INPUT_PATH`). It was not touched; it is flagged for the coordinator.
* `d309_hermite.py` memoises `c7_gaussian.sqrt_two_pi`, `phi` and `Phi` **in-process**, for speed. The values are
  identical, checked at run time (`_memo_selftest`), and no file of that library was modified.
* Rule S8 arrived after all computation and before any document was written. No correction was needed.


## 7. Repair r1 — conditions of `reviews/REVIEW_STREAM_D_R1.md` (ACCEPTED_WITH_CONDITIONS)

No theorem changed. All six D309_*.json files were regenerated by the repaired scripts (re-run log in `PROGRESS.md`).
No target cell, no drift in the band, and no committed tail number was touched. Rule S8 and quarantine amendment 2 are
respected: no validation-drift Λ or supersolution value appears anywhere in this stream.

### B1 — controls that could not fail

**Withdrawn** (arithmetic on constructed values). Each is replaced by a control through the code path under test,
with its measured power:

| r0 control | replaced by (planted invalid input → checker) | power |
|---|---|---|
| `d309_hermite.py` H3 "planted-too-small" | defects **inside** `box_upper_composite` → per-box containment of exact values | drop_sign 2/4 runs, collapse 4/4, shrink_half 0/4, drop_hull 2/4; genuine 0/2996 |
| `d309_hermite_tf.py` "planted" | defects **inside** `box_upper_tf` → per-box containment | zero_remainder 6/6, half_remainder 4/6, drop_sign 6/6, drop_hull 2/6; genuine 0/9028 |
| `d309_supnorm_fsm.py` NC1 | relabelled **comparator control** (tests the identity comparator only) | differs 60/60 |
| `d309_supnorm_fsm.py` NC2 (rad := max dev/2) | planted-invalid premise supplies → `premise_truth` and `enclosure_check` | premise check: Env4 := 0 60/60, A0 halved 60/60, A0 × 0.99 20/60; enclosure check: 0/60, 1/60, 0/60 |
| `d309_rso.py` NC (a) | invalid ψ through `cert_chain` → truth check | a1 (ψ := 0 at the most-occupied state) N0 44/48; a2 (ψ/2) N0 48/48 |
| `d309_rso.py` NC (c) | invalid LR certificates through `lr_certificate` → exact lower bound | drop_cross 4/12, drop_KS2 12/12, drop_psi 12/12 |
| `d309_cover.py` "half transport" | transport / profile / midpoint mutants through `Record.tpt_parts` on 140 records | profile level: no_rad 136/140, flat 130/140, no_W 140/140, rad_half 0/140; transport level: no_rad 32/140, rad_half 0/140 |

The genuine controls NC (b) (`check_cert_taylor`) and NC (d) (score through the kernel builder) are kept. The
`midpoint_check` shifted-interval check is relabelled a **harness** check.

**Documents corrected:** SUPNORM §3 and §7, RESIDUAL §6, COVER §8, PROGRESS.

### Test power (review §4.1)

**Premise-level and profile-level truth checks** are added:
* SC: `premise_truth` (`d309_supnorm_fsm.py:119-153`);
* cover: the profile check in `transport_mutants`.

**The FSM enclosure / transport soundness checks are downgraded** to weak necessary conditions:
* they miss `Env4 := 0` (0/60) and a halved `A0` (1/60);
* cover `rad_half` is missed (0/140 transport, 0/140 profile).
  The TC radius overestimates the true deviation by more than 2× on these fixtures, so a halved radius is still valid
  there, not a missed invalid input.

The premise-level checks carry the SC evidence: genuine 0/300 violations.

### B2 and B3

* **B2.** Route B2 is now "REFUTED **within the fixed-(g_hi, L, U) family**" (COVER §4; SCOPED §2; row above). CR-2's
  proof uses TPT-O's **supremum** wording (N10).
* **B2c.** The record-free lever that re-certifies operator constants on sub-segments is recorded separately as
  THEORY_ONLY, unevaluated.
* **B3.** "B2 − TPT = 0, 30/30" is relabelled a transcription-consistency **identity**, not evidence
  (`B2_transcription_identity_diff`).

### Guards (N8)

`Q.guard_drift` was added inside:
* `box_upper_composite` (`d309_hermite.py:251`) and `box_upper_tf` (`d309_hermite_tf.py:69`);
* `abs_sup_matrix`, `check_cert_taylor` and `check_cert_grid`;
* `LRFamily.kernel` and `LRFamily.kernel_deriv` (`d309_rso.py`).

### Wording and notes

| note | repair |
|---|---|
| N1 | the TC⁺ variable is `s = |e − e0|` |
| N2 | the SC-S1 root condition is `|e| < C − 1` for all i = 1..5 |
| N3 | "strict" means strict for **exact** sups; a certified gain is not guaranteed (SUPNORM §4, G10; this file §3) |
| N4 | exact-source idealization labelled (SUPNORM §7; `d309_supnorm_fsm.py` docstring) |
| N5 | per-box containment replaces the grid-lower necessary check |
| N6 | stated |
| N7 | independent float quadrature H1b: 1200/1200, max gap 2e-13 |
| N9 | CR-3 uses a transport slack T without `w_g`; the `e_J/e0` factor is shown |
| N10 | "attained" → "supremum" |
| N11 | DRP-0 uses the certified `s_1^cert` |
| N12 | DRP-0 result-free; DRP-1 **outcome-adaptive**, frozen predicate |
| N13 | harness labels |
| N14 | RSO non-cosmetic iff `ψ ≠ ‖ψ‖` μ-a.e. |
| N15 | `sup_e μ_{a,e}(ψ)` |
| N17 | re-run log in PROGRESS |
| N18 | the pointer to a committed per-cell share was removed from RESIDUAL §1 |

The commit subject of 6d0f0615 ("strictly positive", "result-free policies DRP-0/1") cannot be edited without a git
write. **It is superseded by the wording above.**

### Route states after repair

States are unchanged, except:
* B2 is narrowed to its true scope;
* B2c is added as THEORY_ONLY;
* G6 is PASS for the mathematics, via the independent review.

**FREEZE_READY: no**, for every route.
