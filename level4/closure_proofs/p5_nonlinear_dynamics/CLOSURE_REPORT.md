# P5 closure report

```text
SCIENTIFIC_VERDICT             = PARTIAL
REPOSITORY_INTEGRATION_VERDICT = APPROVED_PARTIAL_CHECKPOINT
PROTECTED_TREE                 = IDENTICAL (294 files, SHA-256)
FOCUSED_TESTS                  = 44 passed, 1 failed (G20 worktree scope)
LEAN_SPINE                     = 12 declarations, sorry-free, 3 standard axioms
```

## 1. The contribution

P5 was asked what nonlinear stochastic mechanism converts P1–P3's local
repulsion into P7's bounded high-dispersion regime. The answer is a single
exact identity and everything that follows from it.

**The mechanism.** The frozen Stage-D update collapses identically to

```
e_{j+1} = rho * (mean of the last min(m, tau) RAW N(0,1) observations)
        + (1-rho) * N(0, 1/m) .
```

The entering reference error cancels. It influences the future **only** by
selecting which observations land in the terminal reuse window. That selection
channel is maximal *per unit of e* at `e = 0` — where the alarm is rare and
therefore exquisitely selective, giving the gain `GammaTilde ~ 9-17` that P1/P2
computed — and it *vanishes* once `|e|` is large enough that the alarm is
immediate, because a certain event selects nothing. Local repulsion and global
boundedness are the same channel evaluated at opposite ends of its dynamic
range. The chain does not "return" from a large excursion; it is **reset**.

**The reconciliation of P3 with P7.** Because the conditional-mean map is
`rho * R(e)` for one fixed odd `R`, symmetric 2-cycles are exactly the roots of
`s(e) = 1/rho`. Under measured H2/H3 assumptions, a symmetric branch emerges
at `rho_c` with amplitude tending to zero against an `O(1)` noise floor. This
conditional asymptotic is consistent with P7's negative result; it does not
prove attraction or the absence of every operational feature.

## 2. Closure standard, item by item

| # | requirement | status | where |
|---:|---|---|---|
| 1 | exact audited stochastic recursion | **met** — T1, verified bit-identical `tau` and `8.9e-16` state agreement against the frozen P7/Stage-D chain in 12 configurations | `DEFINITION_AUDIT.md`, `tests/test_correspondence.py` |
| 2 | independently reproduced nonlinear drift structure | **met** — 49+20 point map on 2 detectors x 4 windows, full independent seed-family replication (`sd z = 1.04` over 392 paired cells) | `NONLINEAR_MAP.md` §1–2, `NUMERICAL_CORRESPONDENCE.md` §6 |
| 3 | explains P3 local repulsion vs P7 dispersion | **met** — T1 (mechanism), T9/T10 (why `rho_c` is invisible), T11 (why `Gamma_eff << GammaTilde`) | `THEOREM.md`, `PROOF.md` |
| 4 | at least one theorem beyond local derivative analysis | **exceeded** — T7 proves unique invariant law, uniform ergodicity and *all* moments finite for both detectors, every `m`, every `rho in [0,1]` including full reuse | `PROOF.md` |
| 5 | not a finite-simulation artifact | **met** — independent seed family; 3 initial-condition groups in all 176 chain cells (552 `z` statistics, median `1.11`, max `3.88` against a null 95th percentile of `4.17`); stress test from `e_0 = 10^6`; deterministic skeleton scan with no algebraic input | `ADVERSARIAL_REVIEW.md` A6–A8 |
| 6 | explicit stationary-law theorem/evidence boundary | **met** — existence/uniqueness/ergodicity/moments are EXACT; shape, dispersion, modes and mixing are NUMERICAL EVIDENCE; constants are declared vacuous | `LIMITATIONS.md` §2–3 |
| 7 | explicit support/rejection of bifurcation and multiple attractors | **met** — flip bifurcation at `rho_c` **supported** (T9 + independent scan); saddle-node/pitchfork/transcritical, cascades, chaos, asymmetric cycles, multiple attractors and metastability all **rejected** | `THEOREM.md` T8/T12, `ADVERSARIAL_REVIEW.md` A4/A9/A10/A17 |
| 8 | detector/window comparison | **met** — all 8 cells everywhere; the nonlinear regime is detector-independent to MC precision while the linearisation differs by ~9% | `NONLINEAR_MAP.md` §7 |
| 9 | uncertainty-aware long-run statistics | **met** — replicate chain is the statistical unit throughout; batch s.e. for the map; per-replicate histograms for the mode test | `STATIONARY_DYNAMICS.md` §1 |
| 10 | adversarial review | **met** — 17 attacks, 3 of which changed the campaign (one overturned a published claim) | `ADVERSARIAL_REVIEW.md` |
| 11 | P6 handoff | **met** — with a concrete new operating-point result | `P6_HANDOFF.md` |
| 12 | protected-tree integrity | **met** — 294 files byte-identical; worktree touches only the P5 directory | `results/protected_hashes_{before,after}.txt`, `tests/test_protected_tree.py` |
| 13 | focused tests | **met** — 45 tests, every headline claim asserted against a produced artifact | `tests/` |

## 3. Pre-committed claims and their outcomes

| claim | outcome |
|---|---|
| **C1** the reference-error chain is bounded in distribution at every admissible `rho` | **confirmed, and proved** (T5/T7): all moments finite, uniformly; from `e_0 = 10^6` the mean `|e_1|` is `0.83` |
| **C2** a stationary law exists, is unique and is ergodic | **confirmed, and proved** (T7) — closing all five gaps P7 left open |
| **C3** local repulsion at `0` is globally destabilising | **rejected** — `M(e) -> 0`; the map saturates at `sup|R| <= 1.59` and decays to `<0.002` beyond `|e| = 10` |
| **C4** a genuine bifurcation exists in `rho` | **confirmed, but only in the deterministic skeleton** — supercritical flip at exactly `rho_c`, verified independently; **no operational bifurcation** |
| **C5** `rho_c` has an observable signature in the chain | **rejected**, and now *explained* (T10). An independent curvature probe ranks `rho_c` first in **0 of 40** detector x window x metric combinations |
| **C6** the stationary law is unimodal at every `rho` | **rejected by P5's own experiment** — it becomes genuinely bimodal, but only at `4.1x`–`9.8x rho_c`. The original draft claim was corrected, not defended (`ADVERSARIAL_REVIEW.md` A9) |
| **C7** multiple attractors / metastable regimes exist | **rejected** — uniqueness by theorem; residence time `1.08`–`1.46` cycles with alternation rate up to `0.93`, i.e. the opposite of metastability |
| **C8** `Gamma_eff` in P7's `ACF1 = rho(1 - Gamma_eff)` is identifiable | **confirmed and proved** (T11): `Gamma_eff = 1 + E_pi[e^2 s(e)]/E_pi[e^2]`; measured `1.48–2.19` against a tangent gain of `11.8–17.3` |

## 4. The result P5 did not set out to find

Stationary reference dispersion is **non-monotone in `rho` with an interior
minimum at `1.5x`–`4.5x rho_c`**, in all eight cells, and the in-control ARL is
maximised at the same place (7/8 cells exactly, 1/8 one grid point away).
Operating there instead of at full reuse cuts reference RMS by 39%–47% and
roughly doubles the in-control ARL. This is P5's most directly actionable
output and the substance of the P6 handoff.

## 5. Independent adjudication

Independent adjudication preserves the exact structural identity, T7's
stationary-law theorem, T11's ACF identity, and the core numerical mechanism.
It narrows the flip/attraction and T10 operational claims. The final verdict is
`PARTIAL`: frozen G20 fails because the known root README and P6 pre-design are
outside P5, and the universal wording of G3/G4/G7/G9 is not established by a
finite measured grid. See `INDEPENDENT_ADJUDICATION.md` for the authoritative
20-gate and theory-status tables.

## 6. Honest limitations carried forward

* (H2) `R(e) < 0` on `e > 0` and (H3) monotonicity of `s` on `(0,2]` are
  **measured, not proved**; T8–T10 are conditional on them.
* T4/T7's explicit constants are vacuous as rates (`C_CUSUM <= 9.9e8` against a
  measured `465`). The qualitative content is unaffected.
* The T11 cross-campaign check agrees to `<= 0.018` absolute but not within the
  chain's replicate standard error; the prediction's own error budget is not
  quantified.
* `R'(0)` sits `0.14%–1.6%` below P3's `1 - GammaTilde` in 8/8 cells, a
  reproducible finite-difference bias, not chased to ground.
* No interval certification; the probabilistic theorems are not formalised.
* `Delta = 0` throughout; delay tails are P7's object, not re-derived here.
