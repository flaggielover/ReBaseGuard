# 08 — Limitations and Claim Boundaries

What Level 1–3 closure does **not** cover. Every item here is a genuine
limitation found in the artifacts, not a defensive disclaimer.

---

## 1. The mandated boundary statements

### 1.1 `Γ_CUSUM > 2` is Arb-certified, not Lean-proved

`Γ_CUSUM > 2` carries the label `CERTIFIED`. It rests on outward-rounded
interval arithmetic, not on a proof assistant. It is **not** `MACHINE-CHECKED`
and must never be described as formally verified. Lean contains no statement
about the value of `Γ` anywhere.

### 1.2 Arb is not formally verified by this Lean development

The two bodies of evidence are disjoint. Nothing in `rebaseguard-lean` verifies
FLINT, Arb, python-flint or CPython. The certificate's trusted computing base is
declared in `certificate.json`:

```json
"trusted_computing_base": [
  "CPython exact integer serialization",
  "python-flint bindings",
  "FLINT/Arb outward-rounded arithmetic and transcendental functions",
  "rebaseguard_certify.audit replay logic"
]
```

and in practice also includes the project's own symbolic-polynomial, Bernstein
range-enclosure and monotone-contraction checkers. That is a substantially
larger trusted base than the Lean kernel.

### 1.3 Lean proves the analytic derivative identity, not the numerical value of `Γ`

The final Lean theorem is a statement about a **derivative**:

```text
d/de E[Z_τ·exp(−e·T_τ − (e²/2)·τ)]|₀ = −E[Z_τ·T_τ]
```

Both sides mention `E[Z_τ T_τ]`; neither side evaluates it. Lean establishes
that the differentiation is legitimate (measurability, integrability, domination,
the exponential moments of `T_τ` and `τ`, `L²` control of `Z_τ`) — it does not
and cannot tell you that the number exceeds 2.

### 1.4 Optional stopping and Wald identities are outside the Lean chain

The Lean development uses **no** optional stopping theorem and **no** Wald
identity; `CUSUMBridge.lean` states this explicitly under "Explicitly NOT done
here". The martingale identities `M1`, `M2` (`E[T_τ²] = E[τ]`) and `M3` are
human `PROVED` results in `rebaseguard_lemma_handoff.md` §3, corroborated
numerically but not formalized.

### 1.5 Bellman/Fredholm numerical analysis remains outside Lean

The state reduction `Γ = b(0,0)`, the Fredholm system `a = Ka+r_a`,
`b = Kb+K_z a+r_b`, the reachable-domain argument, the Neumann-series
existence/uniqueness, the Bernstein range enclosures and the residual
propagation are **not** formalized. They are `PROVED` (human, triple-derived) and
`CERTIFIED` (Arb), respectively.

### 1.6 The stopped score is not claimed to remain Gaussian

`Z_τ = X_{τ−1}` is **not** asserted to be `N(0,1)`. The Lean source says so in as
many words (`ReBaseGuardIdentity.lean`: *"the stopped score `Zτ = X_{τ-1}` is not
asserted to be `N(0,1)`. Only the one-step law is used, through the
Cauchy–Schwarz slice bound."*). Selecting an increment by a stopping rule biases
its law; the proof is built to avoid needing that law at all.

### 1.7 Independence of `τ` and `T_τ` is not claimed

Nowhere is `τ` assumed independent of the walk. This is the exact step the slice
decomposition over `{τ = m}` exists to avoid — `StoppedWalkMoment.lean` calls it
out: *"`τ` is nowhere assumed independent of the walk: the decomposition over the
events `{τ = m}` is exactly what avoids that false step."* No factorization over
`{τ = m}` is performed; the events are handled by Cauchy–Schwarz.

### 1.8 The closure concerns the frozen single-cycle CUSUM model

`k = 0.5`, `h = 5`, `m = 1`, Gaussian innovations, one alarm cycle from the reset
state. Nothing is claimed for other `(k, h)`, other `m`, other noise families, or
other detectors.

### 1.9 Multi-cycle recursive reference-state dynamics are NOT part of Level 1–3 closure

The recursive reuse chain `e_{j+1} = F(e_j) + ε_j` is what motivated the project
and is documented in `rebaseguard_phase15.md`, but only its **local linearization
at the fixed point** enters Level 1–3 (through `F₁'(0) = 1 − Γ`). The chain's
global behaviour — bimodality, period-2-like orbits, invariant law, ARL
degradation — is `NUMERICAL EVIDENCE` at best and `NOT CLAIMED` as theory.

### 1.10 Real or semi-real Level-4 validation is not implied

No real data, no semi-synthetic validation, no deployment evidence exists
anywhere in the project. The entire evidence base is mathematical and
computational on the frozen synthetic model.

### 1.11 The entire ReBaseGuard project is NOT claimed formally verified

One step is machine-checked. The certificate is interval-certified. The
surrounding theory is human-proved. The phenomenon is simulated. These are four
different strengths of evidence and the package keeps them separate.

---

## 2. Additional genuine limitations found during this closure

### 2.1 The certified interval is very wide

`[3.9243, 27.8494]` has width ≈ 23.9 around a true value near `15.89` — a
relative half-width of ~75%. The certificate answers exactly one question
(`> 2`) and answers it with a factor-of-two margin, but it does **not** locate
`Γ` usefully. Anyone wanting a tight enclosure would have to redo the error
budget.

### 2.2 The resolvent bound is known to be ~2.7× lossy

`rebaseguard_phase4d_audit.md` (Finding 1) establishes the exact identity
`‖(I−K)^{-1}‖_∞ = sup_y E_y[τ]`, whose true value is ≈ 465, against the
certificate's block bound `C = 1315.79`. Since `C` enters the dominant error term
squared, ~7.4× of margin is being discarded. The certificate is **valid but
wasteful**. This is a limitation of sharpness, not of correctness.

### 2.3 `make audit` is not read-only

The auditor rewrites `proofs/audit_report.md` in place. In this session the
rewrite was byte-identical, but a reader running the audit on a dirty tree should
know it mutates a tracked artifact.

### 2.4 The Lean chain re-proves regularity but does not re-prove `F(0) = 0`

The step from the Lean derivative identity to `F₁'(0) = 1 − Γ` additionally needs
the change-of-measure setup and `F(0) = 0` (reflection symmetry). Those are human
`PROVED` and are **not** in Lean. So even the analytic spine is only partly
machine-checked — the delicate part is, the bookkeeping around it is not.

### 2.5 `results/reproducibility.json` records a stale test count

It states `"tests": "26 passed"`; the suite now collects **90** (44 core + 20
`phase4b` + 26 `phase4c`). The figure is a snapshot from before the Level-4
preparatory suites existed. It is documentation drift, not a defect, and was
deliberately left unedited to preserve the historical record.

### 2.6 `rebaseguard-lean/README.md` is an unmodified project template

It still contains the stock "GitHub configuration" boilerplate and says nothing
about the formalization. The three GitHub Actions workflows are likewise stock
templates that have never been exercised — there is no CI evidence for the Lean
build, only local builds.

### 2.7 Lean build warnings

`lake build` emits deprecation and style warnings (`push_neg` deprecated in
favour of `push Not`, `Set.mem_setOf_eq` → `Set.mem_ofPred_eq`, `show` used where
`change` is meant, short copyright headers, `haveI` where `have` suffices). None
affects soundness; all are cosmetic lint and are recorded rather than fixed, to
avoid touching accepted proofs.

### 2.8 Phase-1.5 numerical evidence is undocumented at the artifact level

`rebaseguard_phase15.md` reports point estimates with no machine-readable output,
no seeds, no sample sizes and no uncertainties. It is the weakest evidence in the
project. Level-1 claims should be worded accordingly.

### 2.9 No Monte Carlo convergence study

Only two fixed-`n` runs exist. There is no sample-size sweep demonstrating
stability of the MC estimate. (This matters little, since MC plays no rigorous
role.)

### 2.10 The candidate solver is not replayed by the audit

`make audit` replays from the stored `candidates.json`. Regenerating the
candidate itself requires `make proof`, which additionally depends on NumPy and
SciPy. This is sound — the candidate carries no proof weight — but it means the
cheap verification path trusts a stored file (whose hash is, however, checked).

### 2.11 Single-platform evidence

Every run of record, including this session's, is on macOS/arm64 (Apple A18 Pro)
with CPython 3.14.5. The certificate should be platform-independent (Arb is
deterministic), but no cross-platform reproduction has been performed.

### 2.12 The Lean development has never been built in CI

The build is reproducible locally and the toolchain is pinned exactly, but no
independent machine has verified it.

---

## 3. What would invalidate the closure

Recorded from `rebaseguard_phase4d_audit.md` and this audit, so a future reader
knows what to re-test:

* any patch-cover gap in the Bernstein coverage;
* omission of the reset state `(0,0)` from the residual supremum;
* any non-outward-rounded step in the Arb chain;
* row masses not verified to contain 1;
* use of a floating-point residual in place of a certified bound;
* asserting `L > 2` non-strictly;
* the symmetry reduction applied without proof;
* modification of any pinned Level-3 artifact without a new certificate;
* introduction of any `sorry`, custom `axiom`, or `native_decide` into the Lean chain;
* any change to `cusumTau`, `cusumPair`, `scoreAt`, `walkAt` or `cusumTauReal`
  that breaks the correspondence checked in `03_LEAN_VERIFICATION.md` §Model
  Correspondence Audit.
