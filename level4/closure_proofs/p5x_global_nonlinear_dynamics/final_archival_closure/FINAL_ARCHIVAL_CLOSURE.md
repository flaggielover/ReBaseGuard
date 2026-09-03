# P5X — Final Archival Closure Record

> **Classification: `FINAL_ARCHIVAL_CLOSURE_RECORD`.**
> This is not a scientific successor and not a repair campaign. It contains no
> new science. It runs no certifier, moves no gate, and changes no verdict.

Authoritative HEAD at closure: `66f9cbad4d638e276aa7d19994ffee4341bd6c1f`.
Machine-readable companions: `commit_ledger.json`, `final_claim_table.json`.

---

## 1. Final governance

```
P5_ORIGINAL_VERDICT       = PARTIAL
P5X_FINAL_VERDICT         = PARTIAL
P5_SCIENTIFIC_LINE_STATUS = PARTIALLY_REPAIRED_BY_SUCCESSOR
```

No other verdict vocabulary is introduced. In particular this record does not
use, and the campaign does not support, `PARTIAL_STRONG`, `CLOSED_IN_SCOPE`,
`EFFECTIVELY_CLOSED`, or `PRACTICALLY_CLOSED`. P5X is `PARTIAL` in the same
plain sense that P5 is `PARTIAL`.

The original P5 record remains immutable and historically `PARTIAL`. P5X does
not supersede, repair, or recolour it; it is a successor that advanced part of
the same scientific line.

---

## 2. Campaign timeline

35 commits, reconstructed from git objects (`commit_ledger.json`): 11 on
`origin/main` (Checkpoint A through R3), 24 on `p5x-compute-opt-r1`
(Checkpoint F through the CUSUM production result), merge-base
`c123b9bb8f15d17650545b3fce4aca8a6b61093b`.

| phase | commit | outcome |
| --- | --- | --- |
| Checkpoint A | `db0781ed` | pre-result temporal anchor for the successor campaign |
| Checkpoint B | `528908ba` | human proofs complete; single-cell certified stop-gate **FAILS** |
| R-A′ | `f2ac22e8` | repaired certified method **PASSES** the stop-gate |
| R1 | `9e19c706` | drift-explicit resolvent reduction **PASSES**, 5.287× CPU speedup |
| R2 | `e22cd0e3` | 14.448× on CUSUM; campaign bottleneck identified as SR |
| R3 | `c123b9bb` | SR local symbolic architecture sound, **fails** the cost gate |
| R4 | `daaabf9e` | ξ reformulation removes the z-panel bottleneck (1255×), gate **FAILS** on conditioning |
| R5 | `d7f436fe` | tail-scaled repair works (2.14e17 → 1.00e2), gate **FAILS** on the erfcx evaluator |
| R6 | `83baefb1` | **GATE PASS** — the conditioning blocker is closed |
| SR prototype | `9d03dc1a` | **FAIL** on two numerical blockers; tractability and science established |
| SR repair-options audit | `1eb19b59` | refinement alone ruled out for B2 |
| R7 | `316642fa` | B1 one-sided reduction **PASSES**; B2-b centred residual **FAILS** |
| Bernstein (B2) basis audit | `3093c588` | Bernstein certification **VIABLE** (CASE 1) |
| R8 | `6c4744aa` | **local certification gate PASSES**; SR full-cell prototype **FAILS** on F3/F7 |
| direct-residual audit | `0a62a160` | feasibility only, no binding gate |
| displacement-correlated audit | `b72955a9` | feasibility only, no binding gate |
| two-sided resolvent audit | `df854a07` | feasibility only, no binding gate |
| F3 provenance audit | `638b62ff` | F3 = 0.2 is a `NON_LOAD_BEARING_ENGINEERING_GATE` |
| G3 consumer audit | `8b412aaf` | locates the true binding region |
| G3 pre-freeze calibration | `68b871db` | retires two caveats; refutes an earlier cost estimate of mine |
| far-field edge audit | `7995ec30` | **STOP** — SR m=1 G3 recorded out-of-budget |
| final scope/disposition audit | `c6a82cc0` | fixes the final scientific and governance scope |
| Checkpoint K | `37049885` | binding pre-result anchor for CUSUM production |
| CUSUM production result | `66f9cbad` | **46/47 cells pass; cell 46 FAILS by certificate width** |

Every repair in this campaign was preceded by a pushed pre-result checkpoint
(A, B, C, D, E, F, G, H, I, J, K). No temporal anchor was squashed and no
failing result commit was amended away.

---

## 3. Final result ledger

See `final_claim_table.json` for the machine-readable form, with `scope`,
`method`, `status`, `strongest_legitimate_claim`, `commit`, and
`reason_if_non_pass` per entry. Status vocabulary is restricted to
`EXACT`, `CERTIFIED`, `EMPIRICAL`, `CONDITIONAL`, `FAIL`, `OUT_OF_BUDGET`,
`NOT_RUN`, `INCOMPLETE`.

Distribution over 19 classified claims: 7 `EXACT`, 4 `CERTIFIED`,
3 `INCOMPLETE`, 2 `NOT_RUN`, 1 `FAIL`, 1 `OUT_OF_BUDGET`, 1 `CONDITIONAL`.

## 4. Final scientific claim table

| claim | status |
| --- | --- |
| 2-D Fredholm reduction, all `m` | `EXACT` |
| second-moment reduction | `EXACT` |
| invariant law | `EXACT` |
| ergodicity | `EXACT` |
| symmetry (`R` odd, `S` even, `R(0)=0`) | `EXACT` |
| finite moments | `EXACT` |
| far-field forgetting | `EXACT` (theorem); certified scalar `NOT_RUN` |
| local derivative at `e=0` | `CERTIFIED` |
| local instability (repulsion at 0) | `CERTIFIED` |
| SR `m=1` local certification | `CERTIFIED` |
| SR `m=1` sign | `CERTIFIED` |
| **CUSUM `m=1` global G3** | **`FAIL`** |
| CUSUM `m>1` global G3 | `INCOMPLETE` (no production certifier) |
| SR `m=1` global G3 | `OUT_OF_BUDGET` |
| SR `m>1` global G3 | `NOT_RUN` |
| second-moment production | `NOT_RUN` |
| stationary nonlinear mechanism (`P5X-T9`) | `CONDITIONAL` |
| detector-general universal claims (8/8) | `INCOMPLETE` |
| novelty | `INCOMPLETE` (`NOT_ESTABLISHED`) |

No claim was upgraded on the basis of numerical intuition. `P5X-T9` is recorded
as `CONDITIONAL` rather than `EXACT` because it is an exact theorem *given*
`P5X-T4` and `P5X-T6`, and both premises need certified scalars (`R_max`,
`s_min`, `M_2`) that were never produced.

---

## 5. The CUSUM negative result, recorded exactly

```
CUSUM_M1_G3             = FAIL
CUSUM_M1_PASS_CELLS     = 46/47
CUSUM_M1_FAILURE_CLASS  = C-F2_CERTIFICATE_WIDTH
TRUE_CUSUM_G3_VIOLATION = NOT_ESTABLISHED
```

**Reason for the FAIL:** the frozen production enclosure is too wide on the
final cell. Cell 46, `e ∈ [10.5441104, 12]`, returned
`R ∈ [-2.336765897, +2.336765896]`, so `ABS_MAX = 2.336766 ≥ 2`.

**Stated separately, because they are different facts:** the failure is
*consistent with* the existing far-field theorem showing the true `|R|` is tiny
in that region. `P5X-T3` supplies a majorant decreasing in `|e|` with
`|R_CUSUM(±10)| ≤ 3.2e-5`. The production enclosure is centred on `4.3e-10`.
The certificate does not claim `R` is large there; it fails to claim anything
useful, being 2.34 wide.

**`TRUE_G3_VIOLATION = NOT_ESTABLISHED`.** Nothing in this campaign shows
`sup|R| ≥ 2` for CUSUM `m=1`.

**And yet `CUSUM_M1_G3` stays `FAIL`.** The gate was frozen over `[0,12]` with
`e_far = 12` before the run. Splicing `P5X-T3` inward to absorb the failing
cell would convert a `FAIL` into a `PASS` after seeing the result. That is
prohibited, and it is not done here. The frozen `e_far = 12` remains unchanged.

Root cause, recorded for the archive: the Checkpoint K cover rule sized the
model radius `h` from the *contraction* condition `C(2a·h + b2·h²) ≤ 1/2`
(`0.499438` on that cell, satisfied) and never bounded the enclosure width,
which grows like `h²·C·e`. Where `C → 1` the rule permits `h ≈ 0.269` and the
enclosure blows up. 80% of the width is the second-order term `(h²/2)·S2`.
This is a design flaw in a rule frozen by the campaign, not a defect in the
certifier and not a property of `R`.

---

## 6. Non-authorized future options

Listed for archival completeness only. **None is authorized, none is
implemented, and none is a commitment.**

| option | marker |
| --- | --- |
| pre-register `e_far ≈ 10` using the existing `P5X-T3` theorem | `FUTURE_OPTION_ONLY` |
| add an explicit enclosure-width cap to the radius rule, beside the contraction cap | `FUTURE_OPTION_ONLY` |
| build `m>1` production machinery | `FUTURE_OPTION_ONLY` |
| enlarge the SR compute envelope | `FUTURE_OPTION_ONLY` |

Each would have to be frozen in a pre-result checkpoint *before* being run, by
a campaign that does not yet exist.

---

## 7. Why P5X is PARTIAL

The smallest complete explanation:

1. P5 required universal-in-`e` evidence across 8/8 (two detectors × `m ∈ {1,2,3,5}`).
2. P5X produced exact structural advances and validated certification machinery.
3. It did not produce universal certified G3 across 8/8.
4. CUSUM `m=1` production — the one pair that reached production — itself has
   one frozen-rule width `FAIL`.
5. No `m>1` production certifier exists.
6. SR global G3 is out-of-budget under the frozen envelope.
7. Second-moment production was not run.

Universal certification was the requirement. It was not met. Therefore
`PARTIAL`.

---

## 8. What P5X did achieve

This is substantial, and it is not the same thing as closure.

**Theorem-level advances.** `P5X-T1` gives an exact two-dimensional Fredholm
reduction of the stopped-selection map for every `m`, replacing a
finite-grid numerical object with an exact one. `P5X-T2` gives the matching
exact second-moment reduction. `P5X-T7`/`T8`/`T9` state the global shape,
skeleton dynamics, and mechanism synthesis. The `D1` erratum corrected a frozen
constant (`b_SR = log(1+A) = 6.25744942922713562368`, not `log A`).

**Exact far-field theorem.** `P5X-T3` proves far-field forgetting with an
explicit majorant `B_D(e)`, decreasing in `|e|` and vanishing
super-exponentially — replacing what had been a numerical observation with a
theorem. This is the single most reusable result of the campaign, and it is
what makes the CUSUM cell-46 failure diagnosable as width rather than
substance.

**R6 conditioning resolution.** The ξ/ζ reformulation plus a regime-split
`erfc` evaluator reduced amplification from `2.1355909533505946e+17` (R4) to
`100.27378582954407`, a factor of `2.13e15`, flat across 192–512 bits, at
`0.3757 ms` per patch against a 2 ms budget. This closed a blocker that had
failed two consecutive gates (R4, R5).

**Certification advances.** R1 delivered a drift-explicit resolvent reduction
(5.287× CPU); R2 delivered dense affine substitution (14.448×, class
`R2_BREAKTHROUGH`). Together these are the machinery that made any production
run affordable at all.

**B1 resolvent result.** Rigorous one-sided SR resolvent constants:
`C_SR = 203.06654369242457` at `e = 1/4` and `1505.820549452426` at `e = 0`,
both converged, with `216.963` cell-valid via the B1-L6 coupling lemma.

**R8 local certification.** The SR local certification gate **passes**, using
Bernstein range certification whose worst residual over a 1024×1024 sweep is
`5.0108623233077534e-3` — a `1.34e7×` improvement over the monomial basis it
replaced.

**Sign certification.** The sign of `R` is certified on the SR probe cell.

**Consumer/provenance clarification.** The F3 provenance audit established that
`F3 = 0.2` is a `NON_LOAD_BEARING_ENGINEERING_GATE`, not the theorem consumer;
the actual consumer is `sup_e |R_{D,m}(e)| ≤ R_max < 2` via `P5X-T4`/`T5`. This
prevented an entire class of misdirected optimization.

**Quantified resource boundary.** SR `m=1` G3 is not merely "hard": the far
field needs `G = 4708` at `e = 3.0` against a frozen cap of `1536` (over by
`3.06×`), with an independent blocker on `[0.072, 0.35]` reaching `G = 2362`.
Six architectures were measured before this was declared. The boundary is a
number, not an impression.

**CUSUM 46/47 production evidence.** A real certified cover over `[0,12]`:
47 cells, 372 sub-cells, exact rational endpoints, zero gaps and zero overlaps,
3.903 CPU-hours. 46 cells satisfy `|R| < 2` strictly, with median margin
`0.7483`. Correspondence holds: production cell 28 contains the independently
recorded R2 benchmark enclosure at `e = 24/100`.

**A preserved negative result.** The campaign ends with a failure it could have
hidden — by moving `e_far` to 10, where an already-proved theorem covers the
gap. It did not. The `FAIL`, its root cause in a rule the campaign itself
froze, and the fix that was deliberately not applied are all in the record.

---

## 9. Level-4 handoff

```
P5X_CAMPAIGN                = ARCHIVALLY_COMPLETE
P5_SCIENTIFIC_LINE_REMAINING = YES
P5_RESIDUAL_STATUS          = DOCUMENTED_LIMITATION
NEXT_ACTIVE_REPAIR_CAMPAIGN = P4X
LEVEL4_GLOBAL_CLOSURE       = NO
```

P4X is **not** claimed to be the only unresolved issue. The formal Level-4
ledger still lists residual P5 items — universal G3, G7, G9, `m>1` machinery,
second-moment production, and the SR compute envelope. The correct statement is:

> Active experimental and theorem work moves to P4X. The P5 residual is frozen
> as a documented limitation, not as a solved problem and not as a closed one.

---

## 10. README wording

> P5 remains historically PARTIAL. P5X materially strengthens the
> nonlinear-dynamics line with exact structural theorems, a certified
> far-field result, and validated CUSUM/SR certification machinery. Universal
> production certification remains incomplete: CUSUM m=1 passes 46/47 frozen
> cover cells with one certificate-width failure, CUSUM m>1 lacks production
> machinery, SR global certification is out of budget, and second-moment
> production was not run.

## 11. Closure-report wording

> The P5X campaign should be read along five distinct axes, which it was
> careful never to conflate.
>
> **Mathematical truth.** P5X established exact structure: a two-dimensional
> Fredholm reduction of the stopped-selection map valid for every `m`, the
> matching second-moment reduction, and a far-field forgetting theorem with an
> explicit super-exponentially decreasing majorant. These are theorems. They do
> not depend on any grid, any tolerance, or any compute budget, and they remain
> true regardless of what the certification effort achieved.
>
> **Certified proof.** A narrower set of statements carries machine-checked
> interval certificates: the local derivative enclosures at `e = 0`, the SR
> local certification gate, the SR sign on the probe cell, the B1 resolvent
> constants, and 46 of the 47 cells of the CUSUM `m=1` cover. Each is an
> enclosure, never an exact value, and each is scoped to the region actually
> certified.
>
> **Numerical evidence.** Monte-Carlo and diagnostic computation guided the
> campaign throughout and at no point established any of its claims. Where
> monotonicity or a profile shape was suggestive but unproved, it was used to
> steer work and explicitly refused as evidence.
>
> **Resource limitation.** SR global G3 is `OUT_OF_BUDGET`: feasible in
> principle, unaffordable under the frozen envelope, with the gap quantified
> (`G = 4708` required against a `1536` cap) after six architectures were
> measured. This is a statement about cost, not about truth, and it must not be
> read as evidence that the bound fails.
>
> **Negative production evidence.** The CUSUM `m=1` cover returned a genuine
> `FAIL` on its final cell, caused by a cover rule the campaign itself froze,
> which bounded contraction but not enclosure width. The true `|R|` there is
> tiny — the far-field theorem says so independently — so no G3 violation is
> established. The `FAIL` is nonetheless preserved, because the alternative was
> to move a frozen boundary after seeing the result. A campaign that edits its
> scope to match its outcome produces no evidence at all.
>
> P5X is therefore `PARTIAL`: materially advanced, honestly bounded, and
> unclosed.
