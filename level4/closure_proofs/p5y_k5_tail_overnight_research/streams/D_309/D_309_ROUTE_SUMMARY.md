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
| **SC** composite-sup premise supply (SC-3, SC-4w, TC⁺; SC-T; SC-S1) | SUPNORM_THEOREM.md | VALIDATED_NON_TARGET; real use BLOCKED | P | P | P | P | P | p | P | P | P | P | CLOSURE-ONLY |
| **CR** real cover refinement (CR-1..3, DRP-0/1) | COVER_REFINEMENT_309.md | VALIDATED_NON_TARGET (algebra); DRP-1 IMPLEMENTED; real use BLOCKED (NEW_REAL) | P | P | P | P | P | p | P | P | P | P | CLOSURE-ONLY |
| **B2** split without new records | COVER_REFINEMENT_309.md §4 | REFUTED (dominated by TPT, Prop. CR-2) | — | P | P | P | P | p | P | P | — | **fails**: cosmetic, gain ≡ 0 | — |
| **RSO-C4** (original definition, `A0 f_H` only) | RESIDUAL_SPECIFIC_309.md | VALIDATED_NON_TARGET; structurally narrow | P | P | P | P | P | p | P | P | P | P for non-constant ψ | CLOSURE-ONLY |
| **RSO-P** (+ RSO-PM, needs SC for order 3) | RESIDUAL_SPECIFIC_309.md | VALIDATED_NON_TARGET; real use BLOCKED | P | P | P | P | P | p | P | P | P | P for non-constant ψ | CLOSURE-ONLY |
| **RSO-LR**, order 1 | RESIDUAL_SPECIFIC_309.md §3.2 | VALIDATED_NON_TARGET (single drift) | P | P | P | P | P | p | P | P | P | P | CLOSURE-ONLY |
| **RSO-LR**, order 2 | RESIDUAL_SPECIFIC_309.md §3.2 | THEORY_ONLY | P | sketch | P | — | — | — | P | P | — | — | CLOSURE-ONLY |
| **Assembly** (TPT) | `streams/E_assembly/THEOREM_TPT.md` (E stream) | referenced, not restated | | | | | | | | | | | CLOSURE-ONLY |

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
| cover result | Exact ρ-decomposition of the clause (CR-1). B2 is dominated by TPT (CR-2, 0 gain exactly). A real refinement removes `1−1/N` of the order-1 slack that TPT cannot touch, `1−1/N²` of the remaining order-2 slack and `1−1/N³` of order-3 (CR-3, leading order). The C5 "ρ halved" oracle is not a refinement model. DRP-0 / DRP-1 policies with a cost model. |
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
* The gain is strict for continuous candidates on the Gaussian kernel (SC-S1).
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
4. **No external review.** No independent fresh-context review of these theorems exists yet (G6 is PARTIAL).

**What could be frozen now, prospectively (G9):**
* the theorem statements;
* the certificate formats;
* the declared calibration rule for the SC certificate configuration (Taylor-form ranges, cover depth ≥ 5, panel 1/16;
  calibrated on synthetic degree-matched functions);
* DRP-0 / DRP-1 with a fixed depth and budget.

## 5. Negative results and limits recorded

**Negative results.**
* **B2 is cosmetic:** gain exactly 0 against TPT, in 30/30 splits.
* **RSO-C4 barely moves the radius** on FSM: rad ratio 0.957–1.000.
* **RSO without SC** (normonly34): 0.80–1.00.
* **Constant ψ gives no gain.** `N0/(Λ‖ψ‖) ≥ 1` with a small certificate overhead.
* **SC equality case.** Sign-aligned discontinuous candidates on a general FSM kernel reach `S3 = S1`.
* **Naive interval certificates are vacuous** for a degree-9 function: about 10⁴× the grid lower bound.
* **The pure-scaling refinement prediction** errs by up to 37 %.

**Coverage limits.**
* The kink negative control misses 24 of 960 cases (all `w_bump` at one state, below tolerance).
* The flat-profile control is caught in only 3/10 fixtures.

## 6. Quarantine observations

* `ov_quarantine --scan` reports one finding in **another stream's** file, `streams/A_306/a306_reproduce_A.py`
  (`TARGET_INPUT_PATH`). It was not touched; it is flagged for the coordinator.
* `d309_hermite.py` memoises `c7_gaussian.sqrt_two_pi`, `phi` and `Phi` **in-process**, for speed. The values are
  identical, checked at run time (`_memo_selftest`), and no file of that library was modified.
* Rule S8 arrived after all computation and before any document was written. No correction was needed.
