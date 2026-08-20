# ReBaseGuard Level 1–3 Closure Report

**Date:** 2026-08-20
**Project root:** `/Users/suzhe/ReBaseGuard`
**Decision:** `LEVEL 1–3: CLOSED`

This is the authoritative entry point for the Level 1–3 evidence package.
Supporting documents: [`ARTIFACT_INDEX.md`](ARTIFACT_INDEX.md),
[`01_FROZEN_MODEL.md`](01_FROZEN_MODEL.md), [`02_THEOREM_MAP.md`](02_THEOREM_MAP.md),
[`03_LEAN_VERIFICATION.md`](03_LEAN_VERIFICATION.md), [`04_ARB_CERTIFICATE.md`](04_ARB_CERTIFICATE.md),
[`05_NUMERICAL_VALIDATION.md`](05_NUMERICAL_VALIDATION.md), [`06_CLAIM_LEDGER.md`](06_CLAIM_LEDGER.md),
[`07_REPRODUCIBILITY.md`](07_REPRODUCIBILITY.md), [`08_LIMITATIONS_AND_BOUNDARIES.md`](08_LIMITATIONS_AND_BOUNDARIES.md),
[`ENVIRONMENT_PROOF.md`](ENVIRONMENT_PROOF.md) (verbatim transcripts + falsification test), [`logs/`](logs/).

---

## 1. Executive Summary

ReBaseGuard Level 1–3 is closed. Three independent bodies of evidence, each
verified in this session, now cover the frozen research question end to end:

1. **Machine-checked (Lean 4 / Mathlib).** The analytically delicate step —
   differentiation under the expectation at the *actual* two-sided CUSUM
   stopping time — is accepted by Lean's kernel with no `sorry`, no custom
   axiom, and a statement that matches the frozen model literal-for-literal
   (`k = 1/2`, `h = 5`, `iIndepFun`, `gaussianReal 0 1`). All ten modules
   elaborate from source with exit code 0; all nine principal theorems depend
   only on `[propext, Classical.choice, Quot.sound]`.

2. **Certified (FLINT/Arb interval arithmetic).** `Γ_CUSUM = E₀[Z_τT_τ]` is
   enclosed in `[3.9243482005828971282…, 27.8493821275467032805…]`, so
   `Γ_CUSUM > 2` with margin `> 1.9243`. The certificate was **actually
   re-executed** here — full replay, exit 0, 129 s, `status: PASS`, endpoints
   bit-identical, regenerated audit report byte-identical.

3. **Proved (human mathematics, triple-audited).** The Bellman/Fredholm
   reduction `Γ = b(0,0)`, the reflection and Wald identities, and the score
   identity `F₁'(0) = 1 − Γ` survived a blind independent re-derivation, a
   hostile mathematical audit, and a proof-to-code correspondence audit.

Together these give, for the frozen configuration, `F₁'(0) < −1` and a strictly
interior critical reuse fraction `ρ_c = 1/(Γ−1) ∈ [0.0372, 0.3420] ⊂ (0,1)`.

**No substantive blocker was found.** The model is internally consistent across
all five of its representations; the bypass scan is completely clean; every
numerical result is correctly labelled and none is load-bearing for a rigorous
claim. What remains are documented limitations of *sharpness and engineering
hygiene*, not of mathematics — the widest being that the Lean development
currently has **no git commits at all** (§12).

## 2. Frozen Research Question

> When a control chart's reference level is re-estimated from the same data
> window whose alarm triggered the update, does the selection induced by
> stopping destabilize the reference recursion?

Reduced, for Level 1–3, to a single scalar question about one alarm cycle:

> For the frozen two-sided Gaussian CUSUM, is `Γ = E₀[Z_τ T_τ] > 2`?

`Γ > 2` is exactly the condition `F₁'(0) = 1 − Γ < −1`, i.e. local instability
of the centred reference fixed point under full stopping-selected reuse.

## 3. Frozen Model

```text
Z_t  iid ~ N(0,1)          (mutually independent)

k = 1/2,   h = 5,   m = 1

S₀⁺ = S₀⁻ = 0
S_t⁺ = max(0, S_{t-1}⁺ + Z_t − k)
S_t⁻ = max(0, S_{t-1}⁻ − Z_t − k)

τ   = inf { t ≥ 1 : max(S_t⁺, S_t⁻) ≥ h }      (inclusive, post-update)
T_t = Σ_{s=1}^{t} Z_s                           (T_τ includes Z_τ)

Γ_CUSUM = E₀[ Z_τ · T_τ ]
```

Verified — not assumed — against the human derivation, the Python model, the Arb
certificate and the Lean formalization. The five-way correspondence table is
[`01_FROZEN_MODEL.md`](01_FROZEN_MODEL.md) §8; the audit verdict there is
**no substantive model mismatch**.

## 4. Level 1 — Phenomenon / Computational Evidence

**Label: NUMERICAL EVIDENCE.**

Phase-1.5 (`rebaseguard_phase15.md`) established, by simulation, that the
Phase-1 "stable contractive AR(1)" conclusion was an artifact of measuring a
*secant* slope over `±0.5` instead of the local derivative at the fixed point.
Measured locally, `F'(0) = −4.51` (`m=5`), `−2.98` (`m=10`), `−0.71` (`m=50`).
Three matched-sample signatures distinguish reuse from a fresh control:

| Signature | Reuse | Fresh |
|---|---|---|
| Alarm-direction alternation | 0.94 | 0.50 |
| Reference-error ACF, lags 1–3 | `−0.56, +0.57, −0.47` | ≈ 0 |
| In-control run length | 48% of matched fresh | baseline |
| Invariant density | bimodal (0.38 at 0, ≈0.70 at lobes) | unimodal |

This is the phenomenon that motivated everything downstream. It is **not** part
of the closed claims: sample sizes, seeds and uncertainties are `NOT FOUND` for
these runs, and the multi-cycle recursion itself is Level-4 territory.

Within the frozen single-cycle model, the computational picture is much
stronger: two seeded 200 000-path Monte Carlo runs give `Γ ≈ 15.9619` and
`15.9010` (SE ≈ 0.090), reproduced bit-for-bit in this session.

## 5. Level 2 — Mechanistic Explanation

**Label: PROVED** (with one component correctly downgraded).

The mechanism is a chain of exact identities, not a story:

* `F₁'(0) = 1 − Γ` — the stopped-score identity (`rebaseguard_phase2c.md` §4).
* `F_ρ'(0) = ρ F₁'(0)` — mixed-reuse scaling, unconditional (Prop. 2).
* If `F₁'(0) < −1` then `ρ_c = 1/|F₁'(0)| = 1/(Γ−1) ∈ (0,1)`, stable below,
  unstable above (Prop. 3).

A **rigorous negative result** explains why nothing easier could work: every
mean/variance martingale identity constrains only the path-sum `Σ_{t≤τ} Z_tT_t`
(which equals `E[τ]` in expectation), never the terminal term `Z_τT_τ`.
Attempting to isolate it yields the tautology `0 = 0`, because `τ−1` is not a
stopping time. `E[Z_τT_τ]` is an irreducible boundary functional of the
pre-crossing state — which is precisely why the project moved to a certified
numerical route (`rebaseguard_lemma_handoff.md` §4).

Honest downgrade carried forward: the positivity `Cov₀(Z_{τ−r},T_τ) > 0` for
every `r`, needed only for `m > 1`, is `NUMERICAL EVIDENCE`, not proved
(`rebaseguard_phase2c.md` §4 says so explicitly). It does not touch `m = 1`.

## 6. Level 3 — Rigorous Evidence

### 6.1 Human mathematical derivation — PROVED

The Bellman/Fredholm reduction: with `s = (p,m)`, `x = T_t`,

```text
E[Z_τT_τ | s,x] = a(s)x + b(s),      Γ = b(0,0)
a = Ka + r_a,    b = Kb + K_z a + r_b
r_a = φ(u) − φ(ℓ),   r_b = uφ(u) + 1 − Φ(u) + Φ(ℓ) − ℓφ(ℓ)
ℓ = m − h − k,   u = h + k − p
```

with reflection identities `a(p,m) = −a(m,p)`, `b(p,m) = b(m,p)`.

Audit trail: independently **blind re-derived**
(`Mathematical_proof/blind_rederivation_report.md`); **hostile audit** PASS with
two nonfatal corrections confined to auxiliary one-sided commentary
(`…Step2_Hostile_Mathematical_Audit.md`); **proof-to-code correspondence** PASS
on a 15-item hostile mismatch checklist with all fifteen `NOT FOUND`
(`…Step3_Proof_to_Code_Correspondence_Audit.md`), which declared
`LEVEL-3 MATHEMATICAL BASELINE: FROZEN`.

### 6.2 Lean machine-checked analytic chain — MACHINE-CHECKED

Final theorem, `RebaseguardLean.hasDerivAt_rebaseguard_cusum`:

```text
d/de  E[ Z_τ · exp( −e·T_τ − (e²/2)·τ ) ] |_{e=0}  =  − E[ Z_τ · T_τ ]
```

for `k = 1/2`, `h = 5`, under measurability, `iIndepFun X μ`, and
`μ.map (X j) = gaussianReal 0 1`.

Nine gates, all PASS:

| Gate | Content | Module |
|---|---|---|
| 2 | Pointwise derivative of the stopped likelihood | `StoppedLikelihood.lean` |
| 3 | Differentiation under the integral at `e=0` | `IntegralBridge.lean` |
| 4 | Domination discharged from moment data (4A–4D) | `Domination.lean` |
| 4.5-A | The real two-sided detector; stopping time; forcing bound | `CUSUMBridge.lean` |
| 4.5-B | Independence ⇒ geometric tail ⇒ forcing-time moment | `CUSUMBridge.lean` |
| 4.5-C1 | Stopped quantities `Zτ`, `Tτ`, `τR`, semantically identified | `StoppedQuantities.lean` |
| 4.5-C2.3 | Stopped-walk exponential moment (Cauchy–Schwarz slices) | `StoppedWalkMoment.lean` |
| 4.5-C2.4 | Small-rate existence; Gaussian instantiation | `SmallMoment.lean` |
| 4.5-C3 | Final assembly at the frozen detector | `ReBaseGuardIdentity.lean` |

```text
REBASEGUARD LEAN ANALYTIC CHAIN: CLOSED
```

Verification results in [`03_LEAN_VERIFICATION.md`](03_LEAN_VERIFICATION.md);
summary in §3 below.

What the chain deliberately does **not** contain: optional stopping, Wald
identities, any product-space construction, the Fredholm reduction, and any
statement about the value of `Γ`.

### 6.3 Arb-certified `Γ_CUSUM > 2` — CERTIFIED

```text
Γ_CUSUM ∈ [ 3.9243482005828971281857775466050952672958374023437500…,
           27.849382127546703280529527546605095267295837402343750… ]
```

Method: exact dyadic candidate (degree-12 Chebyshev collocation rounded to
denominator `2^50`, carrying **no** proof weight) → symbolically integrated exact
residual with a degree-100 Maclaurin `φ` plus rigorous Lagrange remainder →
tensor Bernstein convex-hull range bounds over the **complete continuum** of the
reachable set (`sampled_grid_used: false`) → monotone one-sided block contraction
`‖K^250‖ ≤ 0.81` giving `‖(I−K)^{-1}‖ ≤ 1315.79` → error propagation
`Γ ∈ b̂(0,0) ± E_b`. No Gaussian tail truncation anywhere.

One detail worth recording, found by recomputing the endpoint arithmetic
independently in exact decimal during this audit: the stored interval is **not**
`b̂(0,0) ∓ E_b` exactly — the radius is rounded **outward** to the dyadic
`11.962516963481903076171875`, exceeding `E_b` by `5.28e-8`. The stored interval
therefore strictly *contains* `b̂ ± E_b` and is exactly symmetric about `b̂(0,0)`.
That is the conservative direction, so the certified inequality is if anything
marginally stronger than the raw propagation formula implies.

`CERTIFICATE REPRODUCED` — details in [`04_ARB_CERTIFICATE.md`](04_ARB_CERTIFICATE.md) §8, §13.

### 6.4 Independent numerical validation — NUMERICAL EVIDENCE

| Source | Value | Inside certified interval? |
|---|---|---|
| Monte Carlo, seed 1729, n=200 000 | `15.961901323226364` (SE 0.0898) | Yes |
| Monte Carlo, seed 20260818, n=200 000 | `15.900990186311688` (SE 0.0902) | Yes |
| Independent finite cellwise Arb Bellman (12 cells) | `18.7401484450…` | Yes (auditor-enforced) |
| Refined reachable-geometry extrapolation | `≈ 15.8868236` | Yes |
| Certificate's own candidate `b̂(0,0)` | `15.8868651640648…` | Yes |
| Threshold sweep at `h=5` (`gamma_table.csv`) | `15.8851` | Yes |

Proved consistency identities all check out numerically: Wald
(`E[T_τ²] ≈ E[τ]`, gaps `−1.75` and `+0.71` against `E[τ] ≈ 465`), reflection
balance (`up_fraction` 0.4985 / 0.5011), and the exact decomposition
`Γ = E[Z_τ²] + E[Z_τT_{τ−1}]`.

## 7. Theorem / Evidence Dependency Graph

The template graph in the closure brief showed the human derivation and the
numerical machinery as two parallel roots. The **actual** structure has the human
derivation feeding *both* downstream branches, and the two rigorous outputs
meeting only through the human score identity:

```text
                    Frozen two-sided Gaussian CUSUM
                     k = 1/2,  h = 5,  Z_t iid N(0,1)
                                  │
        ┌─────────────────────────┼─────────────────────────┐
        │                         │                         │
        ▼                         ▼                         ▼
 Human derivation          Lean formalization        Numerical machinery
 (blind re-derivation,     (Gates 2 → 4.5-C3)        (Chebyshev candidate,
  hostile audit,                  │                   exact dyadic rounding)
  proof-to-code audit)            ▼                         │
        │                 MACHINE-CHECKED                   ▼
        │                 derivative identity        Arb continuum certificate
        │              hasDerivAt_rebaseguard_cusum   (residual + Bernstein
        │                         │                    + contraction + resolvent,
        ▼                         │                    256-bit outward-rounded)
 PROVED  Γ = b(0,0)               │                         │
 PROVED  Wald / reflection        │                         ▼
 PROVED  a=Ka+r_a, b=Kb+K_z a+r_b │                     CERTIFIED
        │                         │            Γ ∈ [3.9243, 27.8494]  ⇒  Γ > 2
        │                         │                         │
        └───────────┬─────────────┘                         │
                    ▼                                       │
     PROVED  score identity  F₁'(0) = 1 − Γ                  │
     (its delicate differentiation step is exactly           │
      the machine-checked identity above)                    │
                    │                                        │
                    └──────────────────┬─────────────────────┘
                                       ▼
                        CERTIFIED   F₁'(0) < −1
                        CERTIFIED   ρ_c = 1/(Γ−1) ∈ (0,1)
                                       │
                                       ▼
                          Level 1–3 evidence base
                                       │
                    ┌──────────────────┴──────────────────┐
                    ▼                                     ▼
      NUMERICAL EVIDENCE corroboration          OPEN / NOT CLAIMED
      (MC, finite Bellman, sweeps,              (Level 4: multi-cycle,
       Level-1 phenomenon)                       SR detector, global theory)
```

Two structural facts this makes visible, which the template did not:

* the Lean chain and the Arb certificate **never touch each other** — they are
  joined only downstream, by a human theorem;
* the numerical machinery is **downstream of** the human derivation (it
  implements those equations), not parallel to it.

## 8. Claim Ledger Summary

Full ledger with recommended and forbidden wordings:
[`06_CLAIM_LEDGER.md`](06_CLAIM_LEDGER.md).

| ID | Claim | Label |
|---|---|---|
| L-01 | Analytic derivative identity at the frozen detector | **MACHINE-CHECKED** |
| L-02 | `Γ_CUSUM > 2` | **CERTIFIED** |
| L-03 | Bellman/Fredholm reduction `Γ = b(0,0)` | **PROVED** |
| L-04 | `F₁'(0) = 1 − Γ`; `F_ρ'(0) = ρF₁'(0)`; conditional `ρ_c` | **PROVED** |
| L-05 | `F₁'(0) < −1`; `ρ_c ∈ [0.0372, 0.3420]` | **CERTIFIED** |
| L-06 | Local linear instability of the reference fixed point | **CERTIFIED** |
| L-07 | Monte Carlo / independent-solver cross-validation | **NUMERICAL EVIDENCE** |
| L-08 | Phase-1.5 multi-cycle phenomenon | **NUMERICAL EVIDENCE** |
| L-09 | Level-4 multi-cycle dynamics; SR detector; `Γ_SR > 2` | **OPEN** |
| L-10 | Global bifurcation / period-2 / invariant law / ARL theory; other `(k,h,m)` | **NOT CLAIMED** |
| L-11 | Scope of formal verification (exactly one identity + its chain) | **MACHINE-CHECKED** |

Nine specific overclaims were checked for and found absent, including "the
entire ReBaseGuard project is formally verified" and "Lean proves `Γ > 2`".

## 9. Reproducibility

Full instructions: [`07_REPRODUCIBILITY.md`](07_REPRODUCIBILITY.md).

Unified script: `scripts/verify_level_1_3.sh` — six checks (Lean environment,
`lake build`, bypass scan, axiom audit + `#check` + direct elaboration, Arb full
replay, numerical sanity). It fails loudly, exits nonzero on genuine failure,
refuses to report success when a check was skipped (exit `3`,
`RESULT: INCOMPLETE`, overridable only with `--allow-skip`), restores the one
artifact the auditor rewrites, and needs no network.

**Executed in this session:**

```text
$ scripts/verify_level_1_3.sh
[1/6] Lean environment .......... PASS
[2/6] lake build ................ PASS  (exit 0, 8717 jobs, 29 cosmetic warning lines)
[3/6] Lean bypass scan .......... PASS  (0 matches, all five patterns)
[4/6] Lean axiom audit .......... PASS  (9 theorems, baseline axioms only)
[4b]  direct elaboration ........ PASS  (ReBaseGuardIdentity.lean, exit 0)
[5/6] Arb certificate replay .... PASS  (full replay, Gamma_lower > 2, audit report byte-identical)
[6/6] Numerical sanity .......... PASS  (90 tests; interval arithmetic; cross-checks)

RESULT: ALL CHECKS PASSED
exit code: 0        wall time: 543 s
```

The script's own independent recomputation of the interval arithmetic is what
surfaced the outward-rounding detail noted in §6.3 — an earlier draft of the
check asserted exact equality with `b̂ ± E_b` and correctly failed, which is the
behaviour intended: the script is not decorative.

Everything is version-pinned: Lean `v4.34.0-rc1` + Mathlib rev `de5ce8a9…`;
CPython 3.14.5 + python-flint 0.9.0 + FLINT/Arb 3.6.0, with an 11-line fully
pinned `requirements.lock`. Monte Carlo seeds are fixed (`1729`, `20260818`) and
reproduce bit-for-bit.

## 10. Limitations

Full list, including twelve additional limitations found during this audit:
[`08_LIMITATIONS_AND_BOUNDARIES.md`](08_LIMITATIONS_AND_BOUNDARIES.md).

The load-bearing ones:

* `Γ > 2` is **Arb-certified, not Lean-proved**; Arb is not verified by this Lean
  development, and its trusted base (CPython, python-flint, FLINT/Arb, plus the
  project's own symbolic/Bernstein/contraction checkers) is much larger than the
  Lean kernel.
* Lean proves the **derivative identity**, not the value of `Γ`. Even the analytic
  spine is only partly formalized: the step from that identity to
  `F₁'(0) = 1 − Γ` also needs `F(0) = 0` and the change-of-measure setup, which
  are human-proved only.
* Optional stopping, Wald identities and the Bellman/Fredholm analysis are
  **outside** the Lean chain.
* The stopped score is **not** claimed Gaussian; `τ`/`T_τ` independence is **not**
  assumed anywhere.
* Scope is the **frozen single-cycle** model (`k=0.5, h=5, m=1`, Gaussian).
  Multi-cycle recursive reference dynamics are **not** part of this closure. No
  real or semi-real validation is implied.
* The certified interval is **very wide** (`[3.92, 27.85]` around a true value
  near `15.89`); the resolvent bound is known to be ~2.7× lossy (~7.4× in the
  controlling budget line). Valid, not sharp.
* **The entire ReBaseGuard project is NOT claimed formally verified.**

Engineering-hygiene limitations: the Lean repo has no commits (§12);
`rebaseguard-lean/README.md` is still the stock template; its CI workflows have
never run; `results/reproducibility.json` records a stale test count (26 vs the
current 90); all evidence is single-platform (macOS/arm64).

## 11. Closure Decision

| Criterion | Result |
|---|---|
| Frozen model internally consistent | **PASS** — five-way correspondence, no mismatch |
| Lean repository builds | **PASS** — `lake build` exit 0, 8717 jobs |
| Final theorem directly compiles | **PASS** — `ReBaseGuardIdentity.lean` exit 0 (222 s); all 10 modules exit 0 |
| Semantic correspondence passes | **PASS** — 17/17 checklist items |
| Bypass scan clean | **PASS** — 0 matches for `sorry`/`admit`/`axiom`/`unsafe`/`native_decide` |
| Axiom audit acceptable | **PASS** — 9/9 theorems, `[propext, Classical.choice, Quot.sound]` only |
| `Γ > 2` rigorous certificate valid | **PASS** — outward-rounded Arb, lower endpoint `3.9243… > 2` |
| Certificate reproducible | **PASS** — `CERTIFICATE REPRODUCED`, full replay, exit 0, bit-identical |
| Numerical evidence correctly labelled | **PASS** — every non-rigorous result labelled `NUMERICAL EVIDENCE` |
| Major claims mapped to artifacts | **PASS** — `02_THEOREM_MAP.md`, 40 claims |
| No known overclaim in the ledger | **PASS** — nine overclaim patterns checked, all absent |
| Reproduction instructions usable | **PASS** — pinned, executed, script run |
| No substantive Level 1–3 blocker | **PASS** |

Warnings, cosmetic lint and the documented limitations of §10 do not block
closure. No scientific, model, proof or certificate defect was found.

```text
LEVEL 1–3: CLOSED
```

## 12. Repository State and Freeze Recommendation

Recorded rather than acted on — nothing was pushed or tagged.

**Findings**

* `/Users/suzhe/ReBaseGuard` (the project root) is **not** a git repository.
  `Mathematical_proof/`, the phase memos, `closure/` and `scripts/` are therefore
  under no version control at all.
* `rebaseguard-lean/` is a git repository with **zero commits**. Eleven files are
  staged, and — critically — **all seven core proof modules are untracked**
  (`CUSUMBridge`, `Domination`, `IntegralBridge`, `ReBaseGuardIdentity`,
  `SmallMoment`, `StoppedQuantities`, `StoppedWalkMoment`), as are the four gate
  checkpoints. *The machine-checked chain currently exists only as working-tree
  files.* This is the single most urgent item in this report.
* `rebaseguard-proof/` is a healthy repository on branch
  `codex/continuum-certificate`, head `d77953b docs: conclude Phase-4C SR
  feasibility gate`, clean except for an untracked `.DS_Store`.
* Caches and build output are correctly ignored: `.lake/` and `.venv/` are
  untracked in their respective repos (0 tracked files each).
* Three stray `.DS_Store` files (root, `rebaseguard-lean/`, `rebaseguard-proof/`).
* **No secrets or credentials** found by pattern scan (`api_key`, `secret_key`,
  `password`, private-key headers, `aws_access`, `ghp_`). The only `token` match
  is `id-token: write` in a stock GitHub Actions template.
* No temporary or scratch artifacts inside the project tree; all working files
  from this audit were kept in the session scratchpad.

**Files created by this closure**

```text
closure/LEVEL_1_3_CLOSURE_REPORT.md      closure/06_CLAIM_LEDGER.md
closure/ARTIFACT_INDEX.md                closure/07_REPRODUCIBILITY.md
closure/01_FROZEN_MODEL.md               closure/08_LIMITATIONS_AND_BOUNDARIES.md
closure/02_THEOREM_MAP.md                closure/CLOSURE_PROGRESS.md
closure/03_LEAN_VERIFICATION.md          scripts/verify_level_1_3.sh
closure/04_ARB_CERTIFICATE.md            README.md   (new; no prior root README)
closure/05_NUMERICAL_VALIDATION.md
```

No existing file was modified. `rebaseguard-proof/proofs/audit_report.md` and
`rebaseguard-proof/diagnostics/reference.json` were rewritten by reproduction
runs and verified/restored byte-for-byte identical.

**Recommendation (requires explicit authorization; nothing was executed)**

1. **First**, initialize version control where it is missing, and commit the Lean
   sources — they are currently unprotected:
   ```bash
   cd rebaseguard-lean && git add -A && git commit -m "research: Lean analytic chain for ReBaseGuard Level 1-3"
   ```
2. Add `.DS_Store` to the ignore files and remove the three stray copies.
3. Then freeze:
   ```text
   commit:  research: close ReBaseGuard Level 1–3 evidence package
   tag:     level1-3-closure-v1
   ```
4. **Do not push or tag remotely without explicit authorization.** No git history
   was rewritten and nothing was pushed during this closure.

---

```text
REBASEGUARD LEAN ANALYTIC CHAIN: CLOSED
LEVEL 1–3: CLOSED
READY TO ENTER LEVEL 4
```

Level 4 is **not** authorized by this document and has not been started.
