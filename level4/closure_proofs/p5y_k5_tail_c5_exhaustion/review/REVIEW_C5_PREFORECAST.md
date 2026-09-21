# Independent fresh-context pre-forecast review — P5Y / K5 Campaign C5

Reviewer: fresh context, no prior programme knowledge. Adversarial posture: nothing asserted by C5 was accepted
without recomputation.

Tree reviewed: `/Users/suzhe/ReBaseGuard-k5c5`, branch `p5y-k5-tail-c5`, HEAD `cd4a72d3`,
namespace `level4/closure_proofs/p5y_k5_tail_c5_exhaustion`. Read-only throughout: nothing in the repository was
created, edited or committed. No remote host contacted, no AWS/Vultr tool used, no Order3Certifier / R-stage /
kernel certification run. `c5_forecast.py` was **not** executed — instead every quantity it will emit was
recomputed by independent scripts under the scratch directory, which do not import `c5_transport`.

Host confirmed: `python3` 3.14.5, `import numpy` → ModuleNotFoundError, `import flint` → ModuleNotFoundError.

---

## A. Predecessor integrity and the two main refs — **PASS_WITH_NOTES**

`code/c5_b0_audit.py` emits 17 boolean checks (`B0_01`…`B0_16`, with `13a`/`13b` split); the module docstring says
"sixteen checks" and the campaign instruction says 17. Cosmetic.

**No check asserts `LOCAL_MAIN_REF == REMOTE_MAIN_REF`.** I read every line of the audit. Line 114 records
`git rev-parse main` → `c123b9bb…`; line 115 records `git ls-remote --heads origin main` → `1cb45382…`; 13a and 13b
compare each **against its own pinned expected value only**. There is no cross-comparison anywhere. Confirmed.

`git remote -v` in this tree is `https://github.com/flaggielover/ReBaseGuard.git`, and the tree is a linked worktree
of `/Users/suzhe/ReBaseGuard` (`.git` → `gitdir: …/worktrees/ReBaseGuard-k5c5`). So the known scratch-clone
`ls-remote` trap (origin resolving to a local repository) does **not** apply here; `REMOTE_MAIN_REF` is genuinely
read from GitHub.

C5 modifies neither ref: `git diff --name-only e12a09e8 HEAD` returns only paths under
`p5y_k5_tail_c5_exhaustion` (recomputed independently; `paths_changed_outside_c5` is `[]` and is correct).

Two real defects in the audit:

1. **`B0_02_worktree_clean_at_audit` is hardcoded `True`** (line 59, `# recorded, not asserted`) while the **same
   JSON records `"uncommitted": 1`**. A check whose name contains `worktree_clean` reporting `true` beside
   `uncommitted: 1` is misleading on its face to anyone reading the JSON rather than the source. Rename it
   `B0_02_worktree_state_recorded` or make it assert.
2. **`B0_14_neither_main_ref_touched_by_C4` tests only the local ref.** Its body is
   `len(git("rev-list", "c123b9bb..main")) == 0` — a purely local statement that says nothing about the remote. The
   remote is covered separately by 13b, so the substance is sound, but the check **name asserts more than the check
   body verifies**, which is exactly the conflation this audit exists to prevent. Rename to
   `B0_14_local_main_not_advanced`.

`B0_16` is also hardcoded `True` (delegation to phase 2), but that is disclosed in the adjacent note and phase 2
does execute it (verified: all three anchors reproduce, §I below).

Predecessor artifacts: I re-hashed C4's four pinned artifacts and the C2/C3 seal manifests are reported at 156/0 and
21/0 deviations. C4's adjudication sha `5bd5d7b3…` and the `[309]` excluded set parse correctly out of the
adjudication text.

---

## B. Blocker decomposition — **PASS**

Independently re-derived from `R.coefficients(5)`, the committed `TCT_INPUTS_*.json` and the frozen `tail_enclosure`,
without reading `C5_DECOMPOSITION.json` first. Every published figure reproduces to all printed digits.

| cell | `A0·p2` | `2A1·p1` | `A2·p0` | `A0·f_H` | `A0·ρ·f_G` | `A0·ρ²·env4/2` | **`A0·(ρf_G+ρ²env4/2)`** |
|---|---|---|---|---|---|---|---|
| 307 | 81.5611 % | 16.7714 % | 1.6675 % | **0.1126 %** | 61.5884 % | 19.8601 % | **81.4485 %** |
| 308 | 81.6585 % | 16.7267 % | 1.6148 % | **0.1019 %** | 60.0415 % | 21.5151 % | **81.5566 %** |
| 309 | 81.9465 % | 16.5127 % | 1.5408 % | **0.0854 %** | 58.7975 % | 23.0637 % | **81.8612 %** |

Structural identities I checked rather than assumed, all exact in rationals:

* `S == tot` exactly (the denominator of every percentage is the radius sum, not an approximation) — **True** on all cells;
* `lo == C_lo − S` and `hi == C_hi + S` exactly — **True**; and `M == |lo|` — **True** on all four cells.

The last identity matters: because the negative end binds and `M = −C_lo + S`, the claim "`S` must fall by
`(M − M_needed)/S`" is **exact, not first-order**. Reproduced: 10.0692 % / 31.5376 % / 45.8837 % at 307/308/309,
byte-matching the published values.

The README's "82 %" is 81.45–81.86 % and the "0.1 %" residual is 0.085–0.113 %. Both are accurate.

One wording defect: §2 of `C5_BLOCKER_DECOMPOSITION.md` writes "`M = |centre| + S`". The centre is an **interval**
`[C_lo, C_hi]` (e.g. `[−0.377967, 0.204985]` at 309), not a point; the correct statement is `M = |C_lo| + S` given
that the lower end binds. The arithmetic downstream is right; the sentence is not.

The conclusion drawn is warranted, with one caveat worth stating: `A0` multiplies **all** of `p2`, so reducing `A0`
also reduces the 81.9 % — the ledger's own route E1 is exactly that, and it is ranked second. The claim "the
dominant channel is not `A0`'s *level* but what `A0` is multiplied by" is defensible but is a framing choice, not a
derived fact.

---

## C. Route-search completeness and kill honesty — **FAIL**

**The DATA kill of A1 is TRUE.** Verified directly: `TCT_INPUTS_309.json` carries per-`r` only `sup`, `delta_F`,
`delta_D`, `delta_H`, `eps_src`, `H_at_a`, plus `W2`, `norms`, and an explicit `"order3_fields_present": false`.
No candidate polynomial payload is present. A repository-wide search for `numerators` returns only
`p5y_k5_tail_operator_registry/evidence/registry_c1/{taboo,arl}_*.json` and Perron probe files — operator
taboo/arl candidates, a different object, exactly as the kill_reason states. Honest.

**The MATH kill of D2 is TRUE and properly general.** I proved the identity
`max(|H_lo|, |H_hi|) = max((H_hi)⁺, (−H_lo)⁺)` by exhaustive case analysis on `H_lo ≤ H_hi` (both positive, both
negative, straddling). It holds identically. Sign-awareness alone buys exactly zero. Correct.

**The MATH kills of A5 and A6 are mislabelled, and the mislabel is machine-readable.** The ledger defines
`MATH` as "oracle-perfect tightening of the route's target still does not close the cell → **the route is
refuted**". By the ledger's own kill-gate numbers:

* A5, `σ₃ → 0`: 307 **Γ = −0.049946, CLOSES**; 308 +0.007722; 309 +0.055204.
* A6, `σ₄ → 0`: 307 **Γ = −0.027574, CLOSES**; 308 +0.027307; 309 +0.072506.

So at cell 307 the MATH gate is **not satisfied** and the route is **not refuted**. Nevertheless both rows carry
`"kill_kind": "MATH"` and `"closure_possible": false` — and `closure_possible: false` is **flatly false for A5 at
307**, where `inputs_exist: true` and `new_real_required: false`. A5 is therefore recorded as a mathematically
refuted route when it is in fact a **zero-new-real route with committed inputs that the oracle closes at the one
still-open cell nearest closure**. The prose kill_reason does disclose "the oracle closes 307 only", so this is a
labelling failure rather than concealment — but the structured fields and the phase-3 headline ("Only **five**
routes are refuted on mathematics") both propagate the overstatement. Kill kinds must be **cell-scoped**.

**E2's MATH kill is partly grounded in uncertified evidence, and is now internally inconsistent with C5's own
result.** Two problems:

* Its 308 leg rests on the C4 adjudicator's 2,000,000-path Monte-Carlo (`Λ₃₀₈ = 4.30910 ± 0.00102` vs threshold
  4.375229). C4 itself labels that "**corroboration, not proof**". A MATH kill — defined as an oracle-perfect gate
  computation — may not rest on an uncertified Monte-Carlo.
* Its 309 leg says "a better floor only widens a margin that is already positive", i.e. **zero verdict value**.
  That was written in the same commit (`27a12bef`) in which C5-T shrank that margin from +0.004661130 to
  +0.001708896 — from 2.58 % to **0.94 %** in C4's own critical-`A0` currency (§"matters most"). A sharper certified
  lower bound on `Λ₃₀₉` is now the **only** route that restores the exclusion's margin. Killing it as "no verdict
  change" while simultaneously consuming 63 % of the margin it protects is an internal contradiction.

A2/A3/B1/B2/D3/D4/E1 kills are honest and correctly kinded (I checked each reason against the gate table and the
compute policy). The kill-kind taxonomy itself — MATH / DATA / NEW_REAL, with only MATH counted as refutation — is
a good and unusually honest design. It is the application to A5/A6/E2 that fails.

---

## D. Theorem C5-T — **PASS_WITH_NOTES** (the mathematics is correct)

I checked the proof line by line against `code/c5_transport.py` and re-derived every step.

**(i) `g'(e) = −e·R''(e)`** — correct. `g = R − eR'` ⇒ `g' = R' − R' − eR'' = −eR''`. ✔

**(ii) rightward weight** — `∫_{e0}^{e0+ρ} t dt = ((e0+ρ)² − e0²)/2 = ρ(e0 + ρ/2)`, and `x_hi − ρ/2 = e0 + ρ/2`,
so `w_R = ρ(x_hi − ρ/2)`. ✔ The extension of the upper limit from `e` to `e0+ρ` is legitimate because the integrand
`t(−R'')⁺` is non-negative on `t > 0`. The step `(−R''(t))⁺ ≤ (−H_lo)⁺` follows from `R'' ≥ H_lo` by monotonicity of
the positive part. ✔

**(iii) leftward weight** — `∫_{e0−ρ}^{e0} t dt = (e0² − (e0−ρ)²)/2 = ρ(e0 − ρ/2)`, and `x_lo + ρ/2 = e0 − ρ/2`,
so `w_L = ρ(x_lo + ρ/2)`. ✔ Derived independently; matches.

**(iv) `x_lo > 0`** — the proof needs `t > 0` (strictly, `t ≥ 0` suffices) to drop `|t|` and to sign the integrand.
`weights()` refuses `x_lo ≤ 0` (line 57-58) and `ρ ≤ 0` (line 54-55), and `penalty()` refuses an inverted enclosure
(line 65-66). Enforced, and slightly more conservative than the proof strictly requires. ✔ The forecast also
records `cell_strictly_in_e_gt_0` per cell; I verified `e0 − ρ > 0` on all four (x_lo = 1.7885921 … 1.9839101),
and that `cov["left"] == e0 − ρ` and `cov["right"] == e0 + ρ` **exactly** in rationals on all four cells.

**(v) never worse than the frozen clause** — `P = max(a·w_R, b·w_L) ≤ max(a,b)·max(w_R,w_L)`, `max(a,b) = M` by the
D2 identity, and `w_R > w_L` since `ρ > 0`, so `P ≤ M·ρ·(x_hi − ρ/2) < M·ρ·x_hi` whenever `M > 0`. ✔ Enforced at
runtime as a tripwire (line 73-74). On all four cells the negative end binds, so the gain is exactly `ρ/(2·x_hi)`:
1.211422 / 1.246019 / 1.279003 / 1.294912 %, which I reproduce to nine digits.

**(vi) sign-awareness alone buys nothing** — correct, see §C.

**Notes.**

* The docstring sentence "The improvement factor on the penalty is **at least** `(x_hi − ρ/2)/x_hi`" has the
  inequality **backwards** for the quantity the code names `improvement_factor` (`P/frozen`), which is **at most**
  that ratio. The proof line immediately above it is right; only the prose is wrong. Fix before publication.
* `penalty()` computes `frozen = ρ·x_hi·M` with `x_hi = e0 + ρ` from `weights()`, whereas the frozen consumer uses
  `cov["right"]`. The forecast's guard `t5["Gamma_frozen"] != d["Gamma"] → SystemExit` (line 52-53) closes this: it
  simultaneously verifies `cov["right"] == e0 + ρ` and `max(|H_lo|,|H_hi|) == d["M"]`. I confirmed both hold
  exactly on all four cells. This is a well-designed check and it is load-bearing — keep it.

**Reproduction of every C5-T number** (independent script, no `c5_transport` import):

| cell | Γ frozen | Γ C5-T | penalty frozen | penalty C5-T | gain | binding |
|---|---|---|---|---|---|---|
| 306 | −0.036197780 | **−0.039425934** | 0.266476376 | 0.263248222 | 1.211422 % | rightward |
| 307 | +0.026354631 | **+0.022641576** | 0.297993422 | 0.294280367 | 1.246019 % | rightward |
| 308 | +0.094564145 | **+0.090222449** | 0.339459316 | 0.335117620 | 1.279003 % | rightward |
| 309 | +0.153019689 | **+0.148146343** | 0.376345734 | 0.371472388 | 1.294912 % | rightward |

Identical to the gate's `prior_evidence_known_at_freeze` disclosure. No cell newly closes.

---

## E. Zero-new-real compliance — **PASS_WITH_NOTES**

Static import audit of all seven modules: stdlib only (`argparse, copy, hashlib, importlib.util, json, re,
subprocess, sys, fractions, pathlib`) plus intra-namespace imports. **No `flint`, no `arb`, no `numpy`, no
`requests`/`urllib`/`socket`/`http`/`paramiko`.** The only occurrences of the strings `flint`/`Arb` are inside
kill_reason *text* in `c5_ledger.py`. Host confirmed to lack both numpy and flint.

No kernel evaluation: every scientific quantity is a read of a committed artifact or a re-evaluation of the frozen
`FC.direct` / `T.tail_enclosure` on committed inputs. No new scientific address is formed.

Note: `c5_b0_audit.py` uses `subprocess` to run `git ls-remote --heads origin …` twice, which **does** make an
HTTPS request to github.com. That is not a compute worker and is plainly within the gate's intent ("AWS SR/PS1 must
not be contacted; no compute worker may be used"), but the flat `"remote_hosts_contacted": 0` in the emitted JSON
is imprecise. Say "no compute host contacted; two read-only `git ls-remote` calls to the code host".

---

## F. Whole-cell vs midpoint scopes — **PASS**

Checked at the source rather than taking C5's `whole_cell_valid: true` on trust.

* **The `R''` enclosure is genuinely whole-cell.** `THEOREM_TCT.md` §4 states it explicitly: "**for every `e` in the
  cell** … `R''_m(e) ∈ 𝓗_m`". The (P3′) construction is built precisely to keep the two scopes apart — `σ₃` feeds
  `f_G`, a **midpoint** premise, while `σ₄` feeds `Env4`, a **whole-cell** premise, and r1's defect (substituting a
  midpoint bound into the order-4 recursion) was found and repaired as note N1. This is exactly the error class the
  item asks about, and the predecessor already caught it.
* **`g_hi` is genuinely a midpoint quantity.** `g_hi = R.hi − e0·D.lo` with `R_interval`, `D_interval` certified at
  `e0` (`cusum_layer2: delta_mid`; route B2's kill_reason states it and the K5-B literal requires `e0 ≥ 0` for the
  corner choice `hi(R − e0 D) = R.hi − e0·D.lo`, which holds since `e0 ≈ 2`).
* **No silent mixing.** The enclosure C5-T consumes is `signed_enclosure(d, ad5)` = `R2_interval ∩ [lo, hi]` further
  clamped to `[−M_R2, M_R2]`. I verified numerically that on all four cells `M_R2 == −R2_interval.lo` exactly, so
  the clamp is a **no-op**, and that the TC-T enclosure is strictly inside `R2_interval` on all four, so
  `H_lo, H_hi` **are** the TC-T whole-cell endpoints verbatim (e.g. 309: `[−3.319524453, 3.146542969]` inside
  `[−5.269941292, 5.096959808]`). Both inputs are therefore in the scope C5-T's proof assumes.

---

## G. Dependency and independence — **PASS**

C5-T consumes four inputs per cell: `g_hi` (sealed `R_interval`/`D_interval` at `e0`), `[H_lo, H_hi]` (sealed
`R2_interval` ∩ frozen TC-T whole-cell enclosure), and `e0`, `ρ` (cover ledger). No quantity is consumed twice in
the same role.

`ρ` appears in two places — inside the TC-T radii (`p2 = f_H + ρ f_G + ρ² env4/2`) and in the transport weights —
but these are genuinely the same cell half-width playing two distinct and both-correct roles, not a double count.

No cross-cell mixing: `evaluate()` builds `meas, aux, ad5, cov` inside one per-cell loop from `cell_supply(k, …)`,
and the `Gamma_frozen == d["Gamma"]` guard would catch a substituted `g_hi`, `e0` or `ρ` (mutant M06 demonstrates
the value shift; the guard is what actually detects it in production). The cover is filtered on
`detector == "CUSUM"` in `c5_common.committed_inputs`, avoiding the documented `index`-collision trap that would
silently load the SR cell.

Correlation between `g_hi` and the enclosure (both derive from the same cell record) costs tightness, never
soundness, since both are valid one-sided bounds. Route D4 kills the correlation route on DATA, correctly.

---

## H. Gate prospective integrity — **PASS_WITH_NOTES**

**No forecast artifact at the freeze commit.** `git ls-tree -r d2426c03` under the namespace returns 13 files:
README, six `phase_1`/`phase_3`/evidence artifacts, `config/FEASIBILITY_GATES_C5.json`, and
`code/{c5_analysis, c5_b0_audit, c5_common, c5_ledger, c5_transport}.py`. **`c5_forecast.py`, `c5_mutations.py`,
`C5_MUTATIONS.json` and any `evidence/forecast/` are all absent.** `d2426c03` changes exactly one file
(117 insertions). The gate's sha at `d2426c03` is `d0deada6…`, byte-identical to the working-tree copy and to the
pin in `c5_forecast.GATE_SHA`. Verified.

**The disclosure is adequate, and unusually so.** `c5_transport.py` and `C5_DECOMPOSITION.json` (which already
carried the C5-T numbers) were committed at `27a12bef`, **before** the freeze, and `c5_transport.py` is byte-
identical between `27a12bef` and `cd4a72d3`. So the theorem and its result were fully known at freeze — and the
gate says so, listing the selected route, the per-cell gains, the per-cell `Γ`, the expected class, the expected
exhaustion verdict and the effect on C4. Every disclosed number reproduces exactly. The gate even invites the
finding against itself (`what_the_disclosure_does_not_excuse`). This is the right way to freeze a gate after a
scouting phase.

**Are the classes/thresholds fitted?** Largely no, and I tested it rather than accepting the assertion:

* **The 20 % threshold is genuinely inherited.** Verified at source:
  `p5y_k5_tail_c2_closure/config/FEASIBILITY_GATES_C2.json` → `"threshold": 0.20`;
  `p5y_k5_tail_c3_closure/config/FEASIBILITY_GATES_C3.json` → `"threshold": 0.2`, justification "**inherited
  unchanged from C2's frozen gate rather than chosen for C3**". C5's claim "carried unchanged through C3" is TRUE.
* **But the *metric* changed, undisclosed.** C2 and C3 measure the gap as `requirement − 1` where `requirement` is
  the uniform **atom-constant** reduction factor (bisected through `c2_d5_forecast.requirement`). C5 measures the
  gap of the **M-reduction** factor. The gate inherits the number and silently substitutes the metric. I computed
  both under C5-T:

  | cell | gap fall, C5's M metric | gap fall, C2/C3's atom-constant metric |
  |---|---|---|
  | 307 | 14.088 % | 14.253 % |
  | 308 | 4.591 % | 4.826 % |
  | 309 | 3.186 % | 3.482 % |

  The two metrics agree to within 0.3 percentage points here, the class is **MARGINAL under either**, and the
  substituted metric is very slightly **harsher**. So the swap is **not outcome-fitting** — but it is undisclosed
  and the gate's `inherited_from` sentence implies more continuity than exists. Say plainly: "the threshold value
  is inherited; the metric is the M-factor gap, not C2/C3's atom-constant gap".
* The gate stores `M_reduction_factor_needed` rounded to 5 dp (e.g. 1.68519 vs exact 1.6851851451…), and
  `c5_forecast` uses those rounded values as the denominator of `gap_fall`. Relative error ≈ 7·10⁻⁶; immaterial at
  a 20 % threshold, but the baseline should be exact rationals or the rounding should be declared.
* **Class `INVALID` is unreachable.** The gate lists it first in `primary_order`, but a premise failure raises
  `TransportRefusal` / `SystemExit`, which propagates uncaught out of `main()` — so no artifact is written at all
  and the class can never be emitted. Fail-closed, which is the right default, but then the gate should say that
  an INVALID outcome is signalled by refusal-without-artifact, not by a class.

---

## I. Mutation adequacy — **FAIL**

The classifications are individually honest and the suite is better than most: it separates
DETECTED_BY_GUARD / _RULE / VALUE_ONLY, it explicitly records M01/M05/M06 as VALUE_ONLY (i.e. **not** caught by any
production guard) rather than inflating them, and M08's note candidly explains why scaling the enclosure cannot
trip the tripwire. I verified M03 (inverted enclosure → `TransportRefusal`), M07 (`e0 = 1/100, ρ = 1/10` ⇒
`x_lo = −0.09 ≤ 0` → refusal) and M08 (inflated `w_R` ⇒ `P > frozen` → refusal) all fire as claimed.

**Is the independent reproduction genuinely independent?** Partially. `brute_max` integrates directly
(`g_hi − H(e²−e0²)/2`) and shares no code with `c5_transport`, so the *arithmetic* is independent. But it only
searches **constant** selections of `R''`. That constants are the worst case is exactly the content of the theorem
being validated, so part (1) verifies attainment, not optimality. Say so.

**A mutant the suite misses — constructed and confirmed.** The suite contains **no mutant of `w_L`**, and on all
four tail cells the **leftward branch never binds**: `(H_hi)⁺·w_L / (−H_lo)⁺·w_R` = 0.8529 / 0.8775 / 0.9020 /
0.9230. I monkey-patched `TR.weights` to return `w_L := 0` — an unsound leftward weight — and ran the campaign's own
checks:

```
mutant w_L := 0
  cell 306  Gamma_mut=-0.039425934  identical to true=True | part1_sound=True | forecast_xcheck=True
  cell 307  Gamma_mut=+0.022641576  identical to true=True | part1_sound=True | forecast_xcheck=True
  cell 308  Gamma_mut=+0.090222449  identical to true=True | part1_sound=True | forecast_xcheck=True
  cell 309  Gamma_mut=+0.148146343  identical to true=True | part1_sound=True | forecast_xcheck=True
  => mutant survives EVERY C5 check: True
```

It survives all ten mutants, the independent reproduction's soundness test (`worst ≤ Γ_C5T` still holds, because
`H_hi·w_L_true = 0.342936 < (−H_lo)·w_R = 0.371472` at 309), and the forecast's `Gamma_frozen == d["Gamma"]`
cross-check (which never touches `w_L`). `w_L` could equally be set to `ρ(x_lo − ρ/2)` — the mirror of the M02
unsoundness — with the same result.

I verified by hand that the shipped `w_L` is **correct**, so this is not a live unsoundness today. It is a genuine
hole in the *assurance*: the headline "10 mutants, 0 undetected" is true only of the mutation set actually applied,
and the branch it fails to cover is precisely the one carrying the theorem's novel sign-awareness. The gate's
MARGINAL permitted conclusion allows C5-T to be "adopted into the authoritative clause" — i.e. applied to cells
where the leftward branch *can* bind (the current ratios are already 0.85–0.92, not far from crossing). Required
fix: add (a) an unsound-`w_L` mutant and (b) a synthetic leftward-binding cell (e.g. `H_lo` small, `H_hi` large) on
which the C5-T value and the brute-force maximum are both exercised.

Two lesser problems:

* **M02 and M04 are classified `DETECTED_BY_RULE` on an argued, not exercised, mechanism.** Both `how` fields say
  "the brute-force attainment check of part (1) exceeds this bound", but part (1) is never run against the m02/m04
  formulas — the code merely tests `got[k] < base[k]["Gamma"]` and calls that the detection. The reasoning is
  correct (a bound below the attained maximum must fail part (1)), but the label claims a demonstration that did
  not happen. Either run part (1) against the mutant, or relabel `DETECTED_BY_ARGUMENT`.
* **M10 emits `PROVED_EQUIVALENT`, an outcome class the phase's own stated rule does not admit.** The docstring
  says "a mutant in none of those [four] is an undetected defect and fails the phase", but the code fails only on
  the literal string `NOT_DETECTED`. M10 genuinely is equivalent (the min-selector is identically C5-T by the
  theorem), so nothing is concealed — but the enforced rule is not the stated rule.

Minor: `exhaustion_argument()` computes `Hlo, Hhi` from the float-rounded `R2_enclosure_signed` and never uses
them. Dead code; delete it (and note that re-parsing rationals out of floats is a bad habit to leave lying around).

---

## J. Exhaustion semantics — **PASS**

The family is defined precisely — "every bound on `max_e g(e)` derivable from exactly (i) `g(e0) ≤ g_hi` and
(ii) `H_lo ≤ R'' ≤ H_hi` whole-cell, given the cell lies in `e > 0`" — and the gate's `does_not_cover` list names
the three obvious escapes (improving `g_hi`, improving the enclosure, adding a third input).

**The attainment argument is valid.** Take `R'' ≡ H_lo` (constant) and `g(e0) = g_hi`. Both premises hold with
equality, so the pair is an admissible member of the input set; the transport integral is then exact and
`g(e0+ρ) = g_hi + (−H_lo)·w_R = g_hi + P` when the rightward branch binds. A quadratic `R` realises it. Hence the
supremum over the family equals C5-T's bound and no member can do better. This is genuinely constructive and
genuinely different from "our implementation cannot do better" — which is exactly what the gate's
`not_sufficient` clause demands, and C5 meets it.

**The scope_limits are adequate and honest**: they say it exhausts the transport and not the cell, that a
third-input transport is outside the family, and that it is not exhaustion of 309, of the tail, or of K5. The
classification machinery keeps the exhaustion verdict in its own field and out of the primary class.

Two remarks I checked independently, which *strengthen* the result and should be recorded:

* A "third input" of the kind the gate leaves open — a **tighter midpoint enclosure of `R''(e0)`** — is provably
  worthless for this transport: the adversary may take `R'' = H_lo` off a set of measure zero, so a midpoint
  enclosure constrains nothing about `sup_e g`. Only a bound on `R'''` (route D3, NEW_REAL, circular) would open
  the family. The gate is being conservative, not evasive.
* The obvious alternative of bounding `R` and `R'` separately over the cell rather than transporting `g` is
  **worse**: I computed it at 309 and it gives roughly `+0.163` against C5-T's `+0.1481`.

---

## K. Scoping of impossibility claims — **PASS_WITH_NOTES**

The MATH/DATA/NEW_REAL taxonomy is the right instrument and the ledger is explicit that only MATH refutes and that
DATA/NEW_REAL routes stay live (`future_routes_ranked` lists B1, E1, A1, A2). The phase-3 closing paragraph is
appropriately deflationary: "Only five routes are refuted on mathematics."

But: that count is wrong by two (A5 and A6 are not refuted at 307 — §C), and `closure_possible: false` on A5 is a
machine-readable falsehood. D2's impossibility claim is the one that is fully general, and it is correctly proved.
E1's "**provably useless for 309**" is scoped to the C4 exclusion — but see §"matters most": under C5-T the
exclusion it leans on has lost 63 % of its margin, so that phrase now inherits a much thinner premise and should be
re-qualified rather than repeated.

---

## L. Main-ref distinction across the namespace — **PASS**

Exhaustive grep of the whole namespace for `main`, `MAIN_REF`, `c123b9bb`, `1cb45382`. Every substantive mention is
qualified — README line 10, the gate's `LOCAL_MAIN_REF`/`REMOTE_MAIN_REF`/`main_ref_note`, the B0 audit's three
fields and note, and the audit source comments. The only bare `main` tokens are Python `def main()` entry points
and the two git invocations, both explicitly local. **Nothing anywhere conflates the two, and nothing asserts
equality.** The single defect is the *name* of check `B0_14` (§A), not any claim about the refs themselves.

---

## THE RULING THAT MATTERS MOST — the C4 cell-309 exclusion

**Both numbers verified independently, to all nine digits.** At cell 309 with `A0 = B = 3.297250281519544`,
`A1 = A2 = 0`:

* `Γ` under the frozen clause = **+0.004661130** (exactly reproduces C4's `+0.004661129657978107`);
* `Γ` under C5-T = **+0.001708896**;
* margin retained = **36.6627 %** ("about 36.7 %" — correct);
* `g_hi = −0.223326045`, penalty `0.227987175 → 0.225034942`, a 1.294912 % cut.

At cell 308 the same test gives `Γ = −0.040467543 < 0` under both clauses, so 308 was never excluded and
`margin_retained_percent` is correctly `None`. The `HARD_STOP` logic is correct: it fires only on
`held_before and not held_after`, and it will not fire.

**Is C5's handling correct? Yes in mechanism, incomplete in disclosure.** Recomputing the predecessor's
load-bearing test under the new clause is exactly right, it is what the gate demanded in advance, and the gate
disclosed the outcome before it could be produced. But C4's adjudicated verdict is scoped, verbatim, as holding
"against the **frozen measurement inputs** and the **frozen theorem TC-T / K5-B direct clause**" (C4 verdict, and
binding Condition 1). **C5-T changes that clause.** So adopting C5-T does not merely move a number — it moves the
adjudicated result outside the scope sentence under which it was adjudicated. Nothing in C5's committed artifacts
requires that sentence to be restated, and the permitted_conclusions do not mention it.

**Is there a risk the exclusion actually FAILS? No — but the margin is now thin enough that the campaign is
under-reporting it.** Three numbers C5 does not state and must:

1. **In C4's own currency the margin collapses from 2.58 % to 0.94 %.** Critical `A0` at `A1 = A2 = 0`, cell 309:
   **3.214236023** under the frozen clause (C4 published 3.214236 — reproduced) → **3.266415728** under C5-T,
   against `B = 3.297250282`. C4's Condition 5 already warned that the same route **at the cell midpoint** falls
   **0.71 % below** threshold and that "the published margin exists only by virtue of the sup-over-closed-cell
   quantifier". The surviving margin, 0.94 %, is now the same order as that known fragility.
2. **A further 0.759392 % cut in the transport penalty would void the exclusion** (`0.001708896 / 0.225034942`).
   C5-T itself took 1.294912 %. The campaign has consumed 63 % of C4's margin and left 0.76 %.
3. **The buffer against C4's own top-ranked sensitivity shrinks 2.7×.** DIAGNOSTIC (crosscheck aligned), bisected
   at the C4 floor: the candidate sup norms `sup{F,D,H}` must be tightened by **5.536 %** to void the exclusion
   under the frozen clause, but only **2.056 %** under C5-T. A 1 % tightening already leaves
   `Γ_C5T = +0.000878`. Route A1 — the route that would deliver exactly this — is **DATA-blocked, not refuted**,
   and the ledger itself ranks it third among live future routes.

**Could a still-tighter transport overturn it? Within the named family, no — and I am satisfied the family is
correctly drawn.** C5-T is attained by an admissible member (§J), the midpoint-`R''` escape is provably worthless,
the separate-bounding alternative is worse, and the only remaining opening is a bound on `R'''`, which the
programme does not have and cannot obtain without the R-stage. So the 0.76 % is **not** reachable by a smarter
transport on the present inputs. **But it is comfortably reachable by an enclosure improvement** — 2.06 % on the
candidate sup norms, or any of `σ₃`, `env4`, or `ρ`, each of which voids the exclusion outright at the C4 floor in
the diagnostic sweep. The exclusion of cell 309 is now a **~1 % result resting on the current measurement supply**,
not a structural one, and it should be stated that way everywhere it is restated.

**And the campaign kills the one route that would repair it.** Ledger row E2 — "certify a sharper lower bound on
`E_a[τ]` than C4's" — is marked `KILLED / MATH / "zero verdict value … a better floor only widens a margin that is
already positive"`. After C5-T that margin is 0.94 %, and E2 is the only lever that restores it. E2 must be
re-opened as a live route, or the ledger must explain why a 0.94 % margin needs no defence.

---

## Summary

| item | verdict |
|---|---|
| A predecessor integrity / main refs | PASS_WITH_NOTES |
| B blocker decomposition | PASS |
| C route-search completeness and kill honesty | **FAIL** |
| D theorem C5-T | PASS_WITH_NOTES |
| E zero-new-real compliance | PASS_WITH_NOTES |
| F whole-cell vs midpoint scopes | PASS |
| G dependency / independence | PASS |
| H gate prospective integrity | PASS_WITH_NOTES |
| I mutation adequacy | **FAIL** |
| J exhaustion semantics | PASS |
| K scoping of impossibility claims | PASS_WITH_NOTES |
| L main-ref distinction across namespace | PASS |

**The mathematics of C5-T is correct and every number C5 has published reproduces exactly.** The theorem is valid,
strictly tighter, genuinely zero-new-real, correctly scoped to whole-cell and midpoint inputs, and its family
exhaustion argument meets the gate's constructive standard. The freeze is clean: `d2426c03` contains the gate and
nothing else, and the disclosure of what was known at freeze is complete and accurate. The 20 % threshold really is
inherited unchanged from C2 and C3.

Two blocking failures, both cheap to fix and neither touching a forecast number:

1. **(C)** `evidence/ledger/C5_ROUTE_LEDGER.json` records `closure_possible: false` and `kill_kind: MATH` for
   routes A5 and A6, when the ledger's own kill gate shows both oracles **close cell 307**. Kill kinds must be
   cell-scoped, the phase-3 count "five routes refuted on mathematics" corrected, and E2's MATH kill re-grounded
   (its 308 leg rests on uncertified Monte-Carlo, and its 309 leg is contradicted by C5-T's own result).
2. **(I)** The adversarial suite's "0 undetected" does not cover the leftward weight. I exhibited `w_L := 0`, an
   unsound mutant that survives all ten mutants, the independent reproduction and the forecast cross-check,
   because the leftward branch binds on none of the four cells (ratios 0.85–0.92). Add a `w_L` mutant and a
   synthetic leftward-binding cell.

And one thing that must land **before** the forecast is adjudicated, because the forecast's `predecessor_recheck`
is where it belongs: the C4 cell-309 exclusion survives C5-T, but it now stands on **0.94 %** of critical-`A0`
margin rather than 2.58 %, **0.759392 %** of further penalty tightening would void it, and a **2.056 %** tightening
of the candidate sup norms — a live, DATA-blocked, non-refuted route — would void it, against 5.536 % before C5-T.
C5 discloses two of those five numbers. State all of them, restate C4's Condition 1 scope sentence to name the
clause C5-T replaces, and re-open route E2.

Fix those three and the forecast will, on my independent recomputation, emit exactly:
`C5_PRIMARY_CLASS = MARGINAL`, `closed = [306]`, `newly_closed = []`, `still_open = [307, 308, 309]`,
`materially_tightened = {307: false, 308: false, 309: false}` (gap falls 14.088 % / 4.591 % / 3.186 % against the
inherited 20 % threshold), `exhaustion = EXHAUSTED`, `c4_still_excluded = {308: false, 309: true}`, no HARD_STOP,
`adopted_cells = []`, `coverage_map_revision = null`.

HANDOVER: NOT_READY
