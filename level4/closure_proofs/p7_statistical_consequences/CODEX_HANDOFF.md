# P7 Codex handoff

> **Historical candidate handoff, superseded by `INDEPENDENT_ADJUDICATION.md`.**
> The candidate theory statuses below are not final: independent adjudication
> narrowed P7-B/C/D, rejected P7-E, and removed "certified" wording from the
> Monte Carlo plug-in diagnostic.

> **DO NOT TRUST THE CLAUDE VERDICT.
> INDEPENDENTLY RECOMPUTE AND ADJUDICATE.**

```text
SCIENTIFIC_VERDICT             = CLOSED_CANDIDATE
REPOSITORY_INTEGRATION_VERDICT = PENDING_CODEX
REPOSITORY_VERIFICATION        = PENDING_FOR_CODEX
```

Nothing was committed, staged or pushed. No tracked file in the repository was
modified. `git status --short` shows exactly two untracked directories:
`level4/closure_proofs/p4_theory_generalization/` (pre-existing, **not touched
by P7**) and `level4/closure_proofs/p7_statistical_consequences/` (this
campaign). `git diff --check` is clean.

---

## 1. Strongest statistical consequence established

Reuse-attributable, measured against a fresh-reference control at the same
window length, at full reuse `rho = 1`:

| consequence | nominal | fresh (`rho=0`) | full reuse (`rho=1`) | reuse-attributable |
|---|---|---|---|---|
| in-control ARL | 465 | 80–162 | 48–80 | **−39.5% to −50.6%**, `PRACTICALLY_MATERIAL` 8/8 families |
| mean delay, `Delta=1` | 10.4 / 11.0 | 28.3–54.0 | 52.8–66.1 | **+360% to +540%** vs nominal |
| `R_Delta = E[tau_Delta]/E[tau_0]` | 0.022 | 0.18–0.65 | 0.77–1.06 | at `m=1, rho=1` the shifted cycle is **longer** than the in-control cycle |
| cycle right after the first re-baselining | 465 | 81–171 | **5.6–9.4** | a 98% collapse in one cycle |
| `FAP(100)` | ~0.19 | 0.62–0.82 | 0.82–0.90 | |

And the pre-committed negative result: **the P3 critical reuse fraction has no
observable statistical signature** — `LOCAL-MATHEMATICAL, NOT OPERATIONAL`.

## 2. Exact P1–P3 dependencies

| what | from | how |
|---|---|---|
| `rho_c(D,m)`, `GammaTilde_{D,m}` and their standard errors | `m_rho_stability_priority3/results/boundary_table.json` | **loaded at run time** by `src/rebaseguard_p7/config.py::load_p3_boundaries`; never transcribed. A test compares the loaded values against the file. |
| the multiplier `lambda = rho(1 - GammaTilde)` and the classification | P1/P2/P3 `THEOREM.md` | used as closed hypotheses; not re-derived |
| CUSUM recurrence | `level4/src/rebaseguard_level4/frozen.py::cusum_update` | **imported**, never re-implemented |
| SR recurrence, window convention A, alarm/stopping conventions | `level4/stage_d/src/stopped.py`, `STAGE_D_PROTOCOL.md` | restated verbatim and pinned by bit-identity tests |
| reference-update rule | `level4/stage_d/src/chain.py` | reproduced bit-identically |

**P4 was not read, imported or relied on.** Every conclusion rests on closed
P1–P3 alone (`PROVENANCE.json::p4_used = false`).

## 3. Experiment matrix

| experiment | matrix | size |
|---|---|---|
| chain sweep (E2/E6) | 2 detectors × `m in {1,2,3,5}` × 13 reuse fractions = **104 cells** | 5,000 replicates × 50 cycles, burn-in 12 |
| response curves (E3/E4) | 2 detectors × 34 grid points of `x in [0, 12]`, all four `m` on one shared stream | 4×10⁵ paths for `\|x\| <= 0.15`, 2×10⁵ to 0.5, 10⁵–2×10⁵ beyond |
| delay validation (E5) | 4 cells × 2 shifts = 8 | 40,000 replicates, shift at cycle 25 |
| gain correspondence | 2 detectors × 4 `m` | 20 batches × 100,000 cycles |
| adversarial replication | 6 cells | 5,000 replicates, independent seed family |

Reuse grid per cell: `{0.25, 0.5, 0.8, 1.0, 1.25, 1.5, 2, 4} x rho_c` plus
absolute anchors `{0, 0.25, 0.5, 0.75, 1}`, clipped to `[0,1]`.

## 4. Seeds and reproducibility

Seed family **`20260831`** (Stage D uses `20261001`; no overlap). Adversarial
replication deliberately uses **`20260901`**. Derivation is documented in
`PROVENANCE.md`; `DETECTOR_CODE = {"cusum": 11, "sr": 13}` — fixed integers,
because Python salts `hash(str)` per process. **This was a real defect in the
first pass and every production artifact was regenerated after the fix**
(`ADVERSARIAL_REVIEW.md` F1). `tests/test_reproducibility.py` forbids `hash()`
in campaign code via the AST and asserts same-seed bit-identity.

## 5. Uncertainty method

* Statistical unit = **replicate** (Stage-D protocol §6), so every standard
  error is across replicates and absorbs within-replicate serial dependence.
* Every ARL carries both a normal-theory interval and a 10,000-resample
  replicate bootstrap percentile interval. Max disagreement in width: **2.9%**.
* Ratios against the fresh control resample the numerator's replicates and draw
  the independent denominator from its own sampling law.
* Pre-committed three-way labelling: `INCONCLUSIVE` /
  `STATISTICALLY_RESOLVED` / `PRACTICALLY_MATERIAL` (`EXPERIMENT_DESIGN.md` §7).
* No censoring: `max_steps` raises rather than truncates (asserted by a test).

## 6. Key numerical results to recompute

| quantity | value |
|---|---|
| `A(0)` | CUSUM `465.12 ± 0.73`, SR `464.86 ± 0.72` (calibration says `465.50` / `465.29`) |
| `A''(0)` | CUSUM `-28,392`; SR `-31,945` |
| linearisation radius `r_lin` | `0.05` for every detector and `m` |
| `sup abs h_m` (selection bias) | `1.58, 1.26, 1.10, 0.91` for `m = 1,2,3,5`; both detectors agree to ~1% |
| dispersion / `r_lin` | **8.1 to 27.4** over all 104 cells; **8.2 to 18.9** at `rho=rho_c` |
| `ACF1` identity, max abs gap over 104 cells | **0.0071** |
| P3 multiplier vs measured `ACF1` | overshoots by **5x to 25x** |
| boundary criterion | max **3 of 8** families, threshold 4 |
| burn-in shift (cycles 12–49 vs 30–49) | max **1.4%**, 0 cells above 2% |
| seed replication | max `\|z\| = 1.62` over 6 cells |
| delay identity vs direct simulation | max `\|z\| = 2.36`, max gap 2.9%, over 8 tests |
| certified deficit (Prop. P7-D) | up to **21.5%**, never violated, conservative by ~10x |

## 7. Theory-bridge status

`THEORY_BRIDGE.md`, statuses as written there:

| statement | status |
|---|---|
| **P7-A** entering reference error is a sufficient statistic for the cycle; `ARL_0 = E_pi[A(e)]`, `E[delay] = E_pi[A(e-Delta)]` | **THEOREM**, exact, proved from the frozen semantics; validated in 8 cells |
| `g_m(x) = -x + h_m(x)`; `GammaTilde = 1 - h'(0)`, `lambda = rho h'(0)` | exact algebra + P1/P2 |
| **P7-B** `ACF1 = rho(1 - Gamma_eff)`, `Gamma_eff -> GammaTilde` as dispersion `-> 0` | **PROPOSITION**, exact given stationarity and two moments |
| **P7-C** `\|ACF1\| <= 1` forces second-moment mass outside `r` when `rho beta_r > 1` | **PROPOSITION**, exact |
| **P7-D** certified in-control ARL deficit | **PROPOSITION** + Monte Carlo inputs, evidence rank 4 |
| **P7-E** one-cycle first-order transfer `M'(0) lambda` | first-order expansion; needs differentiability of `A`, **not proved** |
| linear-response pole at `rho_c` | **HEURISTIC, EXPLICITLY REJECTED** on the evidence |

## 8. Focused-test status

**28 tests pass** (`level4/.venv/bin/python -m pytest tests -q`). They cover
bit-identity with Stage D (chain and `Gamma_m`, both detectors), the
`w = min(m, tau)` short-cycle branch, shift/reference-error equivalence,
absence of censoring, evenness of `A` and oddness of `g`, seed reproducibility,
namespace isolation (AST-level import ban including P4), the effective-multiplier
identity, the variance floor, the delay identity, and non-violation of the
certified bound.

## 9. Files created (all inside the P7 namespace)

49 files under `level4/closure_proofs/p7_statistical_consequences/`, hashed in
`PROVENANCE.json`. Documents: `README`, `DEFINITION_AUDIT`,
`EXPERIMENT_DESIGN`, `THEORY_BRIDGE`, `STATISTICAL_CONSEQUENCES` (generated),
`EVIDENCE_BOUNDARY`, `ADVERSARIAL_REVIEW`, `P6_HANDOFF`, `PROVENANCE(.md/.json)`,
`CLOSURE_REPORT`, `CODEX_HANDOFF`. Code: `src/rebaseguard_p7/` (6 modules),
`experiments/` (8 scripts), `derive_closure.py`, `reproduce.sh`, `tests/`
(5 files). Data: `results/` (8 JSON + one 21 MB `.npz`), `figures/` (4 PNG).

**Files modified outside the namespace: none.**

## 10. Commands Codex should rerun

```bash
cd /Users/suzhe/ReBaseGuard
./level4/closure_proofs/p7_statistical_consequences/reproduce.sh   # ~15 min end to end
level4/.venv/bin/python level4/closure_proofs/p7_statistical_consequences/derive_closure.py
git status --short && git diff --check
```

## 11. Expensive repository checks NOT run

* The repository-wide regression suite (Stage A–F, Level 1–3 frozen
  correspondence, the closed-campaign test packages, the Lean spines and axiom
  audits). P7 touches none of them, but that is an assertion Codex should
  verify rather than accept.
* Any re-verification of P1, P2, P3 or P4. P7 read P1–P3 read-only and never
  opened P4.
* Independent recomputation of the P3 boundary table.

## 12. Exact attack targets for independent adjudication

Ranked by how much of P7 falls if they fail.

1. **`THEOREM P7-A`** — that the entering reference error is a sufficient
   statistic for the cycle. *Everything* rests on it. Attack it by simulating
   shifted chains directly in more cells and comparing against
   `E_pi[A(e-Delta)]`; P7 validated only 8 cells, and one showed `z = 2.36`.
2. **The two controls.** Confirm that the reuse-attributable claims are quoted
   against `rho = 0` at the same `m`, and that the absolute 83%–90% loss is
   never attributed to reuse. This is the easiest place for the campaign to
   have overclaimed.
3. **The boundary criterion.** It was adapted from D2.5 and pre-committed, but
   it is one criterion among many. Re-derive with a different bracket
   definition, a different metric set, or a finer `rho` ladder around `rho_c`,
   and check the verdict is stable. P7's own robustness check says it flips only
   at a threshold below half.
4. **The delay identity route.** The full delay grid is computed through
   `E_pi[A(e-Delta)]` rather than simulated. If P7-A or the `A` interpolation is
   wrong, §4 of `STATISTICAL_CONSEQUENCES.md` is wrong. Note that grid
   truncation already biased this once (`ADVERSARIAL_REVIEW.md` F2).
5. **The SR gain discrepancy.** P7 measures `GammaTilde^SR` 0.9%–1.1% below
   P3/P2 at every `m` and agrees with Stage-D `d1_gamma` instead. Decide who is
   right. P7 did not, does not depend on it, and modified nothing.
6. **`Gamma_eff` and the interpolated `h_m`.** The `ACF1` identity is checked
   using an interpolant of `h_m` over the empirical reference law. Confirm the
   interpolation error is negligible, and that the out-of-grid fractions
   reported per cell are honest.
7. **Stationarity.** P7-B/C/D assume a stationary law with finite fourth
   moment. P7 evidences fast mixing (burn-in shift `<= 1.4%`) but proves
   nothing. If the chain has no stationary law in some cell, those propositions
   do not apply there.
8. **Scope leakage.** Verify that no P5 claim (period-2, attractors, basins,
   hysteresis, bifurcation) and no P6 claim (a mitigation) appears anywhere,
   including in the exploratory non-monotonicity result, which P7 states only
   as a negative instruction to P6.

## 13. If Codex integrates

Suggested commit scope: the whole
`level4/closure_proofs/p7_statistical_consequences/` directory. Note
`results/chain_sweep_arrays.npz` is ~21 MB (per-replicate arrays and reference
samples needed for the bootstrap and for `Gamma_eff`); drop it and re-derive
from `reproduce.sh` if the repository prefers not to carry it, but then
`experiments/analyze.py` cannot be rerun without first rerunning the sweep.
