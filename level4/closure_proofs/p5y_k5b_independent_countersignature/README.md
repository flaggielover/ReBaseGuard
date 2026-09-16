# Independent review and countersignature of Theorem K5-B

**Verdict: `K5_B_INDEPENDENT_REVIEW = PASS_WITH_SCOPE_LIMITATION`.** Theorem K5-B
(`p5y_k5_feasibility/K5_GLOBAL_BRIDGE.md`, sha256 `c1c62346…339d3f`) is mathematically valid as a **sufficient**
bridge from certified K1 enclosures plus certified per-cell lower bounds on `R'''` to H3a. It is not complete.

This namespace is additive. It changes no existing artifact, runs no scientific computation, reads no K1 record,
produces no order-3 object, and issues no K5, P5Y or P5Z verdict. It closes the readiness blocker
`B3_BRIDGE_NOT_INDEPENDENTLY_COUNTERSIGNED` and nothing else.

```text
K5_B_INDEPENDENT_REVIEW  = PASS_WITH_SCOPE_LIMITATION
K5_B_LOGICAL_STATUS      = SUFFICIENT_ONLY
ENDPOINT_ARGUMENT        = PASS
INTERIOR_CHAIN           = PASS
STRICTNESS_PRESERVED     = YES
CIRCULARITY              = NONE
M5_TAIL_CLASSIFICATION   = BOTH
TEMPORAL_INTEGRITY       = PASS
K5_DECLARED_CLOSED       = NO
P5Y_DECLARED_CLOSED      = NO
```

## 0. Independence and lineage

| Item | Value |
|---|---|
| Theorem | `level4/closure_proofs/p5y_k5_feasibility/K5_GLOBAL_BRIDGE.md`, introduced in `6f1d351b` (2026-09-13 16:30 +09), never modified |
| Binding target | `p5y_postk1_precompute_resolution/K5_TARGET_AND_THIRD_ORDER.md`, `e5cc5a90` (2026-09-13 15:53 +09), never modified |
| Original authorship | Same agent session as the K2/K3 packet (`p5y_k5_feasibility/RESULT.md`) |
| Readiness audit | `e8680998`, which cites K5-B as PASS but not countersigned |
| Review base | `origin/p5y-postk1-frontier` = `e8680998`; `origin/main` = `1cb45382` (untouched); clean worktree |
| This review | A separate Claude Code session (Claude Opus 5), 2026-09-16, with no access to the authoring session's context. The theorem was re-derived from the text, and the recurrences were re-implemented from the text before the readiness code was imported for comparison. |

**Scope limitation on independence.** This review is independent of the original construction by session and by
implementation. It is **not** independent by agent family or by human review: reviewer and author are both
Claude agents. A human or differently-sourced review would strengthen the countersignature, and this record does
not claim that level.

## 1. Definitions, reconstructed

- `R = R_{D,m}`. It is odd (P5-T3, exact) and holomorphic on a strip `|Im e| ≤ θ₀` (P5X L5), so it is C^∞ on every
  cover cell, including the cell that extends past `e = 2`.
- `R'(0) = 1 − Γ̃`, from the local derivative correspondence (P5 THEOREM.md).
- `s(e) = −R(e)/e` and `g(e) = R(e) − e·R'(e)`.
- `g' = R' − R' − eR'' = −eR''`, and `g(0) = R(0) = 0`.
- `s' = (−eR' + R)/e² = g/e²` for `e > 0`, so `sign s' = sign g`. The repository uses the same convention.
- Parity: `R` odd ⇒ `R'` even ⇒ `R''` odd (`R''(0) = 0`) ⇒ `R'''` even.
- H3a (P5 THEOREM.md, verbatim): `s` continuous and strictly decreasing on `(0,2]`, `s(0+) = Γ̃ − 1 = 1/ρ_c`, `s(2) < 1`.
- K1 objects (`p5y_k1_cover_ledger_implementation/code/assembly.py`):
  - `R_interval ∋ R(e0)` and `D_interval ∋ R'(e0)`;
  - `R2_interval ⊇ R''(cell)`, uniform on the cell;
  - `M_R2 = mag(R2_interval) ≥ sup_cell |R''|`.
- New input: `L_k ≤ inf_{C_k} R'''`, or `−∞`.

## 2. Endpoint analysis — PASS

- `R = a1 e + a3 e³ + …` with `a3 = R'''(0)/3! = R'''(0)/6`.
- `g = Σ (1−k) r_k e^k = −2a3 e³ − 4a5 e⁵ − …`, so `g = O(e³)` and `g ~ −R'''(0)e³/3`. Also `s' ~ −2a3 e`.
- **The theorem does not rest on Taylor notation.**
  - Cell 1 uses the MVT for `R''` with `R''(0) = 0`: `R''(t) ≥ L₁t`, hence `g(e) = −∫₀ᵉ tR'' ≤ −L₁e³/3`.
  - This needs only `R ∈ C³` on `[0, x₁]`, which analyticity supplies. There is no remainder term to control.
- Necessity and sufficiency of `R'''(0) > 0`:
  - `L₁ > 0` ⇒ `R'''(0) ≥ L₁ > 0`. So `R'''(0) > 0` is **necessary for this route**.
  - It is **not sufficient for the route**: `R'''` must be certified positive on all of `C₁`.
  - It is **not necessary for H3a**: with `a3 = 0` and `a5 > 0`, H3a still holds near 0.
- A certified `sup_{C₁} R''' < 0` gives `R'' < 0` on `(0, x₁]`, so `g > 0` and `s` increases there, which refutes
  H3a (adversarial A1).
- Stronger than the text states: `Γ₁ < 0` is not merely "structurally hopeless" but **impossible** for any valid
  enclosure, because `Γ₁ ≥ g(0) = 0`. Cell 1 can pass only through `L₁ > 0`.

## 3. Interior chain — PASS

| Step | Propagates | Why valid | Direction and sign checks |
|---|---|---|---|
| `μ_k = max(H.lo, ℓ_{k−1} + min(0, 2ρL))` | lower bound on `R''` over `C_k` | MVT: `R''(t) ≥ R''(x_{k−1}) + L(t − x_{k−1})`, with `t − x_{k−1} ∈ [0, 2ρ]` | `min(0, ·)` is the worst endpoint for either sign of `L`; `ρ > 0` |
| `ℓ_k = max(H.lo, ℓ_{k−1} + 2ρL)` | lower bound on `R''(x_k)` | the same MVT at `t = x_k` | uses only point `x_k`, shared exactly with the next cell (contiguity is checked exactly; no overlap is needed) |
| `U_k`, `γ_k` | upper bound on `g` over `C_k` and at `x_k` | `g(e) = g(x_{k−1}) − ∫ tR'' ≤ γ_{k−1} − μ(e² − x²_{k−1})/2` because `t ≥ 0` | monotone in `e²`, so the sup is at an endpoint for either sign of `μ` |
| `Γ_k = hi(R − e0·D) + ρ·x_k·M` | upper bound on `g` over `C_k` | MVT for `g` about `e0`: `\|g(e) − g(e0)\| ≤ ρ·sup\|t R''\| ≤ ρ·x_k·M` | `e0 ≥ 0`, so `hi = R.hi − e0·D.lo` (A8 shows the other corner is unsound) |
| `γ₁ = −L₁x₁³/3` | bound on `g(x₁)` | cell-1 integral | valid for any sign of `L₁`; undefined for `L₁ = −∞`, read as `+∞` |

- **Monotonicity.** `ℓ`, `μ` and `γ` are monotone in every input: tighter inputs never loosen outputs. Any *valid*
  enclosure therefore yields valid bounds.
- **Strictness.** Every pass test is a strict inequality between exact rationals. Each bound holds on the
  **closed** cell, so `g ≤ bound < 0` gives `g < 0`. Then `s' < 0` on `(0,2]`, and MVT gives `s` strictly
  decreasing.
- **Exact verification.** Every one of 3,479 synthetic cell passes, and 157 full-theorem passes, was confirmed
  exactly (Sturm sequences, exact rationals). There were 0 violations over 7,229 cells.
- **Mutation sensitivity.** The fuzz provably detects breakage. Four deliberate mutations are each caught:
  `≤` for `<`, the wrong interval corner, the wrong sign of `γ₁`, and `μ` using the endpoint instead of
  `min(0, ·)`.

**Readiness-scan semantics.** `k5_minimality.py` starts the chain at `γ₀ = 0` and runs the general step on cell 1:
`γ₁ = min(−H₁.lo·x₁²/2, Γ₁)`.
- This is a valid bound, but it is not the literal `γ₁` (which is `+∞` when `L₁ = −∞`).
- **Lemma.** If every `H_k.lo ≤ 0`, both chains give identical pass sets.
  - *Proof.* Every step `s_k = −H_k.lo·Δ_k/2 ≥ 0`, and both chains start `≥ 0`, since `H₁.lo ≤ 0` and `Γ₁ ≥ 0`.
  - By induction, at each `k` the two `γ_k` are either equal or both `≥ 0`.
  - A chain pass needs `γ_{k−1} < 0`, so the chains can differ only where they are equal. ∎
- `CUSUM_MINIMALITY_R1.json` records zero cells with `R2_interval.lo > 0` for every m, so the lemma applies there.
- The scan therefore did **not** change K5-B's pass semantics on the committed data. That conclusion relies on
  those counts, which the scan itself reported.
- Checks: the lemma held on 980 fuzz configurations. The committed scan agrees with the independent variant on
  40/40 synthetic record sets, and with the literal theorem on 14/14 of those where all `H.lo ≤ 0`. 207 divergences
  appear only when some `H.lo > 0`.

## 4. Sufficiency vs necessity — `SUFFICIENT_ONLY`

**Guaranteed.** For a fixed `(D,m)`, suppose all of the following hold:
- the premises hold: `R` odd, `R ∈ C³`, `R'(0) = 1 − Γ̃`;
- the inputs are valid enclosures on the frozen contiguous cover;
- every cell meeting `(0,2]` passes;
- the K1 gate certifies `R(2) > −2`.

Then `s` is continuous and strictly decreasing on `(0,2]`, with `s(0+) = Γ̃ − 1` and `s(2) < 1`.

**Not guaranteed.**
- **A failed cell or chain says nothing against H3a.** A2, A3, A5 and A9 give functions where H3a holds but valid
  inputs fail. Refutation needs a separate argument, such as a certified `sup_{C₁} R''' < 0` (A1).
- **Degenerate truths are uncertifiable.**
  - `a3 = 0`.
  - `g` touching 0 at an isolated point: A4 shows `g = −e³(e²−1)²`, where H3a holds but both cells adjacent to
    `e = 1` must fail.
  - The reduction H3a ⇐ `g < 0` is itself only sufficient.
- **`= 1/ρ_c` is not proved by K5-B.** It is P3's definition `ρ_c = 1/|1 − Γ̃|` and requires `Γ̃ > 1`, which is
  certified outside K5-B.
- **No statement about realised widths**, and so none about which cells will pass.
- **Overshoot past 2.** The cell containing 2 must satisfy `g < 0` on the whole closed cell, including the part
  beyond `e = 2` (A10: H3a holds, `g > 0` on `(2, 2.11]`, and the last cell fails even with near-exact inputs).
- **Fixed-cell granularity.** On a frozen coarse cover, the direct bound's slack `ρ·x·sup|R''|` and the chain's
  slack from `min_cell R''` can exceed a true negative `g` even with exact inputs (A11).

In 103 synthetic configurations the exact `g < 0` held on `(0,2]` while the theorem failed.

## 5. The m = 5 tail — `BOTH`

What K5-B permits:

| Route | Permitted? |
|---|---|
| Accumulated order-3 propagation over a long run | yes |
| Local or piecewise restart | **yes**: `ℓ_k` restarts from `H_k.lo` and `γ_k` from `Γ_k` |
| Tighter valid enclosures `R`, `D`, `H`, `M` on the same frozen cells | yes |
| Stronger `R''` evidence (`H.lo`, `M`) instead of `R'''` | yes |
| Refining cells, testing only `cell ∩ (0,2]`, or a sharper signed direct bound | **no**: that needs a successor theorem |

**Numerical-input component (certain).** The recorded failure on CUSUM m = 5 cells 305–309 is computed with
`L_k = −∞` everywhere and with K1 curvature enclosures that are not sign-determinate. On cell 305:
- `H.lo ≈ −5.50` and `M_R2 ≈ 5.50`;
- `Γ = g_mid_hi + ρ·x·M ≈ −0.337 + 0.379 > 0`;
- `U ≈ 0.70`.

Order-3 bounds and tighter `R''` enclosures are admissible inputs that could change this.

**Theorem component (real, magnitude on 305–309 undetermined).**
- The theorem is tied to the frozen cells, so its slack does not vanish with exact inputs.
  - A11 exhibits an H3a-true function whose coarse interior cells fail with near-exact inputs.
  - A10 exhibits the overshoot limitation on the cell containing 2. That matters for CUSUM cell 309
    (`[1.98391, 2.092283]`), which the m = 5 tail includes.
- Whether the true `sup|R''|`, `R'''` and `g` on 305–309 put these cells inside or outside the intrinsic slack
  cannot be decided from committed data. The records carry only magnitudes, and `M_R2 ≈ |H.lo|` is consistent with
  either a genuine curvature of ~5.5 or pure enclosure width.

**Correction to the readiness record, not an edit of it.** The readiness README (§3 caveat 3) says *"an order-3
island buys nothing downstream — only an unbroken run from cell 0 propagates"*. The readiness record's
`m5_tail_note` says closing 305–309 *"needs an unbroken order-3 run 0–309"*. **Neither is a property of K5-B.**
A9 shows a non-contiguous island closing a tail cell by restarting from `H_{k−1}.lo`. Whether a restart helps on the
realised CUSUM data depends on how negative the realised `H.lo` are, which is a numerical question.

## 6. Circularity — NONE

See `evidence/DEPENDENCY_DAG.json`. The DAG is acyclic, and a test checks it.
- The theorem's ancestors are calculus, P5-T3, P5X L5 (via L1, P5-T1, P5-T4) and the local derivative
  correspondence.
- H3a, K5, P5Z, T9/T10, K1 records and order-3 inputs are not ancestors of the theorem. The numerical inputs feed
  only per-instance verdicts, as premises.
- No `p5y_k1_*` producer uses H3a or any monotonicity of `s`. H3a appears there only as the downstream K5 label.

## 7. Symbolic cross-check

`code/k5b_check.py` uses only the standard library and exact `Fraction` arithmetic. sympy is not installed, and no
Mathlib project exists for this line, so Lean was not used. It checks:
- `g' = −eR''`, `e²s' = g`, `g_k = (1−k)r_k`, `g₃ = −R'''(0)/3` and `s'₁ = −2a3` on 200 random odd polynomials;
- the parity of `R''` and `R'''`, with each identity also proved in closed form in the evidence;
- soundness, with every pass confirmed exactly by Sturm sequences;
- the per-cell bound invariants;
- mutation sensitivity;
- the readiness-scan cross-check.

## 8. Adversarial record (`evidence/ADVERSARIAL_TESTS.json`)

| Case | Premise or property probed | Outcome |
|---|---|---|
| A1 | wrong `R'''` sign near 0 | cannot pass; `sup R''' < 0` ⇒ `g > 0` ⇒ H3a false |
| A2 | `R'''` unavailable, `R'' ≥ 0` | cell 1 cannot pass (`Γ₁ ≥ 0`), although H3a holds |
| A3 | chain lower bound too weak | same function: tight inputs pass, loose valid inputs fail at cell 2 |
| A4 | strictness | `R = −e/2` (H3a false) would pass under `≤` but fails under `<`; a touching `g` (H3a true) cannot pass |
| A5 | local `g < 0`, failed propagated bound | wide `H` and no `L`: `U`, `Γ > 0` although `g < 0` exactly |
| A6 | differentiability violated | `R''` jumps; with `L_k` taken over smooth pieces every cell "passes" while `g(2) = 449/24 > 0` |
| A7 | parity violated (`R''(0) = −1`) | `L₁ > 0` "passes" cell 1 while `g(1/16) > 0` |
| A8 | interval direction | the wrong corner of `hi(R − e0·D)` gives `Γ < 0` where the correct bound is `> 0` |
| A9 | m = 5-style tail | a non-contiguous order-3 island closes a tail cell |
| A10 | cell containing 2 extends past 2 | H3a true; `g > 0` on `(2, 2.11]`; the last cell fails with near-exact inputs (theorem limitation) |
| A11 | fixed-cell granularity | cover ends at 2, near-exact inputs, H3a true; coarse cells 3–4 fail (theorem limitation) |

A6 and A7 show that analyticity (C³) and oddness are genuinely load-bearing. Both are discharged analytically
upstream.

## 9. Governance and temporal integrity — PASS

- **Theorem bytes are frozen.** The theorem, the target, and every premise file were each introduced in one commit
  and never modified. `git diff 6f1d351b e8680998` on these files is empty. `config/THEOREM_HASH_INVENTORY.json`
  records sha256, blob and commits.
- **The theorem predates dependent results.** `6f1d351b` is an ancestor of every CUSUM Aux5 production commit
  (first `54b77949`, 2026-09-13 18:28 +09) and of the composite closure `ce7fb933`. Earlier Aux3/Aux4 qualification
  records (2026-09-06) predate it, but the theorem names no cell outcome and has no tunable choice. Its universe is
  frozen geometry, and it states that no cell subset is predeclared.
- **The readiness audit changed no theorem semantics** on committed data (§3 lemma). Two statements in it are
  stronger than the theorem (§5). They are recorded here, not edited there.
- **The countersignature is additive.** This namespace only adds files, and no history is rewritten.

## 10. What this countersignature allows

Future K5 numerical evidence may claim:

> H3a holds for `(D,m)`, **by Theorem K5-B as independently countersigned**, provided the evidence supplies, on the
> frozen contiguous K1 cover from `x₀ = 0`:
> - certified outward exact-rational `R(e0)`, `R'(e0)` and whole-cell `R''` enclosures with `M ≥ sup|R''|`;
> - certified `L_k ≤ inf R'''` where used;
> - the K1 gate `R(2) > −2`;
> - every cell meeting `(0,2]` passing, over the whole closed cell, the strict exact recurrences exactly as written,
>   or the γ₀ = 0 variant where every `H_k.lo ≤ 0`.
>
> The `= 1/ρ_c` clause additionally needs certified `Γ̃ > 1`.

It may **not** claim that a failed recurrence, `K5_INCONCLUSIVE`, or a failed cell (including cell 309 or the
m = 5 tail) is evidence against H3a. Refuting H3a needs an
independently proved counterexample, such as a certified `sup_{C₁} R''' < 0`.

## Commands

```bash
python -B tests/test_k5b_countersignature.py
python -B code/k5b_check.py verify-hashes
python -B code/k5b_check.py run --out evidence/INDEPENDENT_VERIFICATION.json --adversarial-out evidence/ADVERSARIAL_TESTS.json
```
