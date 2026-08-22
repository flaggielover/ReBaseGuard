# ReBaseGuard

Research project on **stopping-selected recursive reference reuse** in
sequential change detection: when a control chart's reference level is
re-estimated from the very data window that triggered its alarm, the selection
induced by stopping makes the reference recursion locally unstable.

---

## Level 1–3 Research Closure

**Status: `LEVEL 1–3: CLOSED` (2026-08-20).**

The authoritative entry point is:

### → [`closure/LEVEL_1_3_CLOSURE_REPORT.md`](closure/LEVEL_1_3_CLOSURE_REPORT.md)

Supporting evidence documents:

| Document | Contents |
|---|---|
| [`closure/ARTIFACT_INDEX.md`](closure/ARTIFACT_INDEX.md) | Every artifact, its role, evidence type and reproduction status |
| [`closure/01_FROZEN_MODEL.md`](closure/01_FROZEN_MODEL.md) | The authoritative frozen model and the five-way correspondence table |
| [`closure/02_THEOREM_MAP.md`](closure/02_THEOREM_MAP.md) | Every claim mapped to its formal name, artifact and evidence label |
| [`closure/03_LEAN_VERIFICATION.md`](closure/03_LEAN_VERIFICATION.md) | Build, bypass scan, axiom audit, and the Lean ↔ model semantic audit |
| [`closure/04_ARB_CERTIFICATE.md`](closure/04_ARB_CERTIFICATE.md) | The `Γ_CUSUM > 2` certificate and its reproduction record |
| [`closure/05_NUMERICAL_VALIDATION.md`](closure/05_NUMERICAL_VALIDATION.md) | All non-rigorous computational evidence |
| [`closure/06_CLAIM_LEDGER.md`](closure/06_CLAIM_LEDGER.md) | Recommended wording and forbidden overclaims |
| [`closure/07_REPRODUCIBILITY.md`](closure/07_REPRODUCIBILITY.md) | Clean-checkout reproduction instructions |
| [`closure/08_LIMITATIONS_AND_BOUNDARIES.md`](closure/08_LIMITATIONS_AND_BOUNDARIES.md) | What is **not** claimed |
| [`closure/ENVIRONMENT_PROOF/ENVIRONMENT_PROOF.md`](closure/ENVIRONMENT_PROOF/ENVIRONMENT_PROOF.md) | Verbatim transcripts + falsification test proving the toolchain discriminates |
| [`closure/ENVIRONMENT_PROOF/logs/`](closure/ENVIRONMENT_PROOF/logs/) | Raw, unedited terminal output |
| [`closure/CLOSURE_PROGRESS.md`](closure/CLOSURE_PROGRESS.md) | Audit checkpoint / resumption record |

Unified verification:

```bash
scripts/verify_level_1_3.sh          # full
scripts/verify_level_1_3.sh --quick  # skips the ~4-minute direct elaboration
```

### The one-paragraph summary

For the frozen two-sided Gaussian CUSUM (`k = 1/2`, `h = 5`, alarm
`max(S⁺,S⁻) ≥ 5`, `Z_t` i.i.d. `N(0,1)`), the differentiation-under-the-expectation
identity `d/de E[Z_τ e^{−eT_τ−(e²/2)τ}]|₀ = −E[Z_τT_τ]` is **machine-checked in
Lean**, and the bound `Γ_CUSUM = E₀[Z_τT_τ] > 2` is **certified by outward-rounded
Arb interval arithmetic** (enclosure `[3.9243, 27.8494]`). Together with the
proved score identity `F₁'(0) = 1 − Γ` this gives `F₁'(0) < −1` and a strictly
interior critical reuse fraction `ρ_c = 1/(Γ−1) ∈ (0,1)`.

**Not claimed:** that the project as a whole is formally verified; that Lean
proves `Γ > 2`; any global bifurcation, period-2, invariant-law or ARL theorem;
anything about other `(k, h, m)`; anything at Level 4.

---

## Repository layout

| Path | Contents |
|---|---|
| [`closure/`](closure/) | **The Level 1–3 evidence package** (start here) |
| [`rebaseguard-lean/`](rebaseguard-lean/) | Lean 4 / Mathlib formalization of the analytic chain (9 modules, Gates 2 → 4.5-C3) |
| [`rebaseguard-proof/`](rebaseguard-proof/) | Python + FLINT/Arb continuum certificate, diagnostics, and Level-4 preparatory work |
| [`Mathematical_proof/`](Mathematical_proof/) | Blind re-derivation, hostile mathematical audit, proof-to-code correspondence audit |
| [`level4/`](level4/) | **Level 4 Gates 4.1–4.2** — Multi-Cycle Oracle and conditional-map estimator (Monte Carlo only) |
| [`scripts/`](scripts/) | `verify_level_1_3.sh`, `verify_level_4.sh` |
| `rebaseguard_phase*.md` | Historical phase memos (Level 1 phenomenon, Level 2 mechanism) |
| `rebaseguard_lemma_handoff.md` | The lemma attack that motivated the certificate route |

---

## Repository provenance

This is a single ordinary Git repository — clone it normally, no submodules.

Before publication the project consisted of a non-versioned root plus two nested
repositories. They were normalised as follows:

- **`rebaseguard-proof/`** — had 26 commits on `codex/continuum-certificate`
  (tip `d77953b`, with `main` at `eb8af8d` as an ancestor). That history was
  **imported in full** with `git subtree add --prefix=rebaseguard-proof`, so
  every original commit and SHA remains reachable from `main`.
  Use `git log -- rebaseguard-proof` on the merge commit's second parent
  (or plain `git log`) to read it.
- **`rebaseguard-lean/`** — contained a Git repository with **zero commits and
  no refs** (only a staged index identical to the working tree). There was no
  history to preserve; it became an ordinary directory.
- No license file has been chosen for this project, so none is included.

---

## Level 4 — Gates 4.1 and 4.2

**Everything at Level 4 is non-rigorous Monte Carlo.** It does not modify,
reinterpret or extend the Level 1–3 closure above, and the closure's scope
statement still governs what may be claimed.

The Level 4 work lives in [`level4/`](level4/) and builds a reproducible
**Multi-Cycle Experimental Oracle** for the frozen CUSUM, together with an
independent estimator of the conditional map
`F_rho(e) = E[E_{j+1} | E_j = e]`.

| Entry point | Contents |
|---|---|
| [`level4/README.md`](level4/README.md) | layout, environment, conventions, how to reproduce |
| [`level4/reports/GATE_4_1_REPORT.md`](level4/reports/GATE_4_1_REPORT.md) | Gate 4.1 — the Multi-Cycle Oracle |
| [`level4/reports/GATE_4_2_REPORT.md`](level4/reports/GATE_4_2_REPORT.md) | Gate 4.2 — the conditional nonlinear map |
| [`level4/reports/LEDGER.md`](level4/reports/LEDGER.md) | every Level 4 Stage A statement with its evidence status |
| [`level4/stage_b/README.md`](level4/stage_b/README.md) | **Stage B** — rigorous period-2 certificate at `rho = 1` |
| [`level4/reports/STAGE_B_PERIOD2_CERTIFICATE_REPORT.md`](level4/reports/STAGE_B_PERIOD2_CERTIFICATE_REPORT.md) | the Stage B certificate report |
| [`level4/stage_c/README.md`](level4/stage_c/README.md) | **Stage C** — stability-aware reuse policy and the reuse-performance tradeoff |
| [`level4/reports/STAGE_C_METHOD_REPORT.md`](level4/reports/STAGE_C_METHOD_REPORT.md) | the Stage C method report |
| [`level4/stage_c1/README.md`](level4/stage_c1/README.md) | **Stage C.1** — confirmatory sensitivity evaluation |
| [`level4/stage_d/README.md`](level4/stage_d/README.md) | **Stage D** — generalisation: second detector, `m > 1`, non-Gaussian |
| [`level4/reports/STAGE_D_REPORT.md`](level4/reports/STAGE_D_REPORT.md) | the Stage D report |
| [`level4/reports/STAGE_C1_CONFIRMATORY_REPORT.md`](level4/reports/STAGE_C1_CONFIRMATORY_REPORT.md) | the Stage C.1 confirmatory report |

```bash
bash scripts/verify_level_4.sh
```

Level 4 uses its own virtual environment; the frozen `rebaseguard-proof`
environment and every frozen artifact are left untouched, and
`verify_level_4.sh` runs the frozen Level 1–3 suite as regression protection
before it runs anything of its own.

**Stage A** (Gates 4.1–4.2) is Monte Carlo throughout. **Stage B** is not: it
certifies, for the frozen CUSUM at `k = 1/2`, `h = 5`, `m = 1`, `rho = 1`, that
the deterministic conditional-mean map `F_1` has a unique nonzero root of
`F_1(e) + e` in `[1.028724, 1.044724]` and that the resulting symmetric
period-2 orbit is locally attracting, with multiplier enclosed in
`[0.1081, 0.8325] ⊂ (−1,1)`. It concerns the deterministic skeleton only; the
noisy recursion's invariant law remains `OPEN`.

```bash
bash level4/stage_b/reproduce.sh
```

**Stage C** asks whether the certified boundary can be turned into a monitoring
method. It defines a stability-aware reuse policy `rho_safe(delta) =
(1-delta)/(Gamma-1)`, evaluates it against fresh, full-reuse, fixed-partial and
oracle baselines over a 23-point `rho` grid, and reports `STAGE-C-PARTIAL`: the
policy is well-defined and safe, but one pre-specified criterion failed and was
left failed, and a fixed `rho` well above the stability boundary dominates it on
in-control performance.

```bash
bash level4/stage_c/reproduce.sh
```

**Stage C.1** is a separate confirmatory experiment, not a revision of Stage C.
Stage C's preregistered criterion C6 compared *raw* detection delays across
policies with in-control run lengths differing by 1.7x; it failed and stays
failed. Stage C.1 preregistered a baseline-normalised response metric, froze and
hashed it before generating any data, used entirely new seed families, and found
that the certificate-aware policy is non-inferior to fresh-only at every tested
shift: `STAGE-C1-CLOSED-CONFIRMED-SENSITIVITY`. It makes no sample-efficiency
claim and does not make C6 pass.

```bash
bash level4/stage_c1/reproduce.sh
```

**Stage D** asks whether the mechanism generalises, and answers *partly*:
`STAGE-D-PARTIAL`. An ARL0-matched Shiryaev–Roberts chart replicates the effect
with a larger stopped gain (`17.32` vs `15.85`); the gain falls with the window
length and crosses the `rho_c = 1` boundary inside `m* in [50, 75]`; and the
score-based gain exceeds 2 for all six non-Gaussian families tested. But the
derivative correspondence at `m > 1` **failed** its pre-specified test, the
crossing has **no observable operational counterpart** — the monitoring metrics
pass through it smoothly and alarm alternation persists above it — and the
`t(3)` result is **ambiguous** between two estimands. Two detectors is
replication, not detector-independence; six families is not distribution-free.

```bash
bash level4/stage_d/reproduce.sh
```

### A separate, still-unstarted track

Preparatory material for the Shiryaev–Roberts chart lives in
`rebaseguard-proof/proofs/phase4b/`, `phase4c/` and
`rebaseguard_phase4d_audit.md`. Stage D uses that detector numerically, but a
**rigorous SR certificate remains `OPEN`** — nothing in Stage D extends the
Stage B certificate to it. See
[`closure/08_LIMITATIONS_AND_BOUNDARIES.md`](closure/08_LIMITATIONS_AND_BOUNDARIES.md).
