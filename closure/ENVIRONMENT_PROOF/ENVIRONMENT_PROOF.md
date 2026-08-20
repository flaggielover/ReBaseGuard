# Environment Proof — Falsification Test and Raw Transcripts

**Purpose.** A reviewer cannot distinguish "the build succeeded" from "the agent
wrote that the build succeeded" by reading prose. This document answers that with
(a) verbatim terminal output, (b) an environment fingerprint a third party can
independently check, and (c) a **falsification test**: the same toolchain, in the
same session, from a single source file, *accepting* the real theorem and
*rejecting* three deliberately broken ones.

The falsification test is the load-bearing item. A verifier that says PASS to
everything proves nothing; the value of a clean `#print axioms` on
`hasDerivAt_rebaseguard_cusum` comes entirely from the fact that the same command
reports `sorryAx` on a `sorry`, and errors on a false statement and on a sign flip.

Raw logs: [`logs/`](logs/). Every block below is copied verbatim, unedited.

---

## 1. Why this is checkable by a third party

| Fact | Value | How anyone can verify it independently |
|---|---|---|
| Lean commit | `3447a668783dbce1a8fdb97101dd067687b2b418` | Published `leanprover/lean4` release `v4.34.0-rc1` |
| Mathlib commit | `de5ce8a9a66a4aa68a9bdbb35b63a06d34d9ca11` | `git clone leanprover-community/mathlib4 && git rev-parse v4.34.0-rc1` |
| Mathlib checkout modified files | **0** | `git status --porcelain` — rules out a doctored mathlib |
| Mathlib `.olean` count | `8323` | matches a stock `lake exe cache get` |
| ReBaseGuard source hashes | see §2 | `shasum -a 256` on the same files |
| Falsification file hash | `83317bec1d663194f5166a904a0ab1105644bc884c235ae489c7684e7ecaa88d` | `shasum -a 256 logs/EnvProof.lean` |

The mathlib point deserves emphasis. The sharpest attack on any Lean claim is
"the library was edited to make the theorem provable." A pristine `git status`
against a *published upstream commit hash* forecloses it: the axioms and lemmas
used are the ones the Lean community ships, byte for byte.

---

## 2. Environment fingerprint (verbatim)

```text
### CAPTURED: 2026-08-20T09:20:09Z (UTC)
### host: Darwin 25.5.0 arm64 / Apple A18 Pro
### cwd: /Users/suzhe/ReBaseGuard/rebaseguard-lean

$ elan --version
elan 4.2.3 (b6cec7e10 2026-06-08)

$ elan show
installed toolchains
--------------------

leanprover/lean4:v4.33.0 (resolved from default 'leanprover/lean4:stable')
leanprover/lean4:v4.34.0-rc1

active toolchain
----------------

leanprover/lean4:v4.34.0-rc1 (overridden by '/Users/suzhe/ReBaseGuard/rebaseguard-lean/lean-toolchain')
Lean (version 4.34.0-rc1, arm64-apple-darwin24.6.0, commit 3447a668783dbce1a8fdb97101dd067687b2b418, Release)


$ which lake lean
/Users/suzhe/.elan/bin/lake
/Users/suzhe/.elan/bin/lean

$ lake --version
Lake version 5.0.0-src+3447a66 (Lean version 4.34.0-rc1)

$ lean --version
Lean (version 4.34.0-rc1, arm64-apple-darwin24.6.0, commit 3447a668783dbce1a8fdb97101dd067687b2b418, Release)

$ cat lean-toolchain
leanprover/lean4:v4.34.0-rc1

$ git -C .lake/packages/mathlib rev-parse HEAD
de5ce8a9a66a4aa68a9bdbb35b63a06d34d9ca11
$ git -C .lake/packages/mathlib describe --tags
v4.34.0-rc1
$ git -C .lake/packages/mathlib status --porcelain | wc -l  # 0 => pristine checkout
       0

$ find .lake/packages/mathlib/.lake/build -name '*.olean' | wc -l
    8323

$ shasum -a 256 RebaseguardLean.lean RebaseguardLean/*.lean
b5689d4b400e7a4b7fd1553604747359b4a3a6a9a96dd17104e64c0efb48c095  RebaseguardLean.lean
a88fef4d3efa63c9f9f5c948dd5ba1de3ea09d828ce8388ee83fa3d039e734a4  RebaseguardLean/Basic.lean
fbc0df7c87b38d67ace6c05329f8f988a55071577c0f3abc2460b7dd888a07ad  RebaseguardLean/CUSUMBridge.lean
4b93d117071c50f0bd571f125a7b865eea3285c800c80bc2ca5161b59e364df6  RebaseguardLean/Domination.lean
668be6875628425e603f1882b84192d65fab17f6c9603eccef8225fc63d06ab2  RebaseguardLean/IntegralBridge.lean
be969b313f68feb6b947ad163d040f40758258bb92ad40535a751c66e9edf2ca  RebaseguardLean/ReBaseGuardIdentity.lean
3df27a00478c079b3ea24335706c68959c1409a716fc68af2c6555f17cb0fa81  RebaseguardLean/SmallMoment.lean
6324b34ff0f751b8ce4b4ad17c61d4ccc3300d0997b8b1eb07ccaf319d870655  RebaseguardLean/StoppedLikelihood.lean
bb29e46638fd9eaee67ffafbf1d615b0b91923328ffcda74103fe379016332f5  RebaseguardLean/StoppedQuantities.lean
404402ae56fcbbb1b59ecd800f967d51da3d4dfcc87ab92aaba6daf919f76d51  RebaseguardLean/StoppedWalkMoment.lean
```

---

## 3. The falsification test

### 3.1 Source (`logs/EnvProof.lean`, sha256 `83317bec…aa88d`)

```lean
/-
  ENVIRONMENT PROOF / FALSIFICATION TEST
  Blocks A,B  must SUCCEED.   Blocks C,D,E  must FAIL (or expose sorryAx).
  A toolchain that "passes" everything is broken; this file proves it discriminates.
-/
import RebaseguardLean
open MeasureTheory ProbabilityTheory RebaseguardLean

-- ══ A. POSITIVE: the real theorem's axiom footprint ══════════════════════════
#print axioms RebaseguardLean.hasDerivAt_rebaseguard_cusum

-- ══ B. POSITIVE: restate the theorem verbatim and discharge it by the theorem ══
--    If this elaborates, the statement below IS the theorem (no paraphrase drift).
example {Ω : Type*} [MeasurableSpace Ω] {μ : Measure Ω} (X : ℕ → Ω → ℝ)
    (hX : ∀ (n : ℕ), Measurable (X n))
    (hindep : iIndepFun X μ)
    (hlaw : ∀ (j : ℕ), μ.map (X j) = gaussianReal 0 1) :
    HasDerivAt
      (fun e => ∫ (ω : Ω), scoreAt X (cusumTau (1 / 2) 5 X) ω *
        Real.exp (-e * walkAt X (cusumTau (1 / 2) 5 X) ω
          - e ^ 2 / 2 * cusumTauReal (1 / 2) 5 X ω) ∂μ)
      (-∫ (ω : Ω), scoreAt X (cusumTau (1 / 2) 5 X) ω
            * walkAt X (cusumTau (1 / 2) 5 X) ω ∂μ) 0 :=
  hasDerivAt_rebaseguard_cusum X hX hindep hlaw

-- ══ C. NEGATIVE: the SIGN is load-bearing — identical to B but "+" not "−" ════
example {Ω : Type*} [MeasurableSpace Ω] {μ : Measure Ω} (X : ℕ → Ω → ℝ)
    (hX : ∀ (n : ℕ), Measurable (X n))
    (hindep : iIndepFun X μ)
    (hlaw : ∀ (j : ℕ), μ.map (X j) = gaussianReal 0 1) :
    HasDerivAt
      (fun e => ∫ (ω : Ω), scoreAt X (cusumTau (1 / 2) 5 X) ω *
        Real.exp (-e * walkAt X (cusumTau (1 / 2) 5 X) ω
          - e ^ 2 / 2 * cusumTauReal (1 / 2) 5 X ω) ∂μ)
      (∫ (ω : Ω), scoreAt X (cusumTau (1 / 2) 5 X) ω
            * walkAt X (cusumTau (1 / 2) 5 X) ω ∂μ) 0 :=
  hasDerivAt_rebaseguard_cusum X hX hindep hlaw

-- ══ D. NEGATIVE: a `sorry` IS caught by the very audit used on the real chain ══
theorem envproof_via_sorry : ∀ n : ℕ, n = n := by sorry
#print axioms envproof_via_sorry

-- ══ E. NEGATIVE: the kernel rejects a false statement ═════════════════════════
theorem envproof_false : (1 : ℕ) = 2 := by rfl
```

### 3.2 Verbatim output

```text
$ lake env lean EnvProof.lean
'RebaseguardLean.hasDerivAt_rebaseguard_cusum' depends on axioms: [propext, Classical.choice, Quot.sound]
EnvProof.lean:37:2: error: Type mismatch
  hasDerivAt_rebaseguard_cusum X hX hindep hlaw
has type
  HasDerivAt
    (fun e =>
      ∫ (ω : Ω),
        scoreAt X (cusumTau (1 / 2) 5 X) ω *
          Real.exp (-e * walkAt X (cusumTau (1 / 2) 5 X) ω - e ^ 2 / 2 * cusumTauReal (1 / 2) 5 X ω) ∂μ)
    (-∫ (ω : Ω), scoreAt X (cusumTau (1 / 2) 5 X) ω * walkAt X (cusumTau (1 / 2) 5 X) ω ∂μ) 0
but is expected to have type
  HasDerivAt
    (fun e =>
      ∫ (ω : Ω),
        scoreAt X (cusumTau (1 / 2) 5 X) ω *
          Real.exp (-e * walkAt X (cusumTau (1 / 2) 5 X) ω - e ^ 2 / 2 * cusumTauReal (1 / 2) 5 X ω) ∂μ)
    (∫ (ω : Ω), scoreAt X (cusumTau (1 / 2) 5 X) ω * walkAt X (cusumTau (1 / 2) 5 X) ω ∂μ) 0
EnvProof.lean:40:8: warning: declaration uses `sorry`
'envproof_via_sorry' depends on axioms: [sorryAx]
EnvProof.lean:44:43: error: Tactic `rfl` failed: The left-hand side
  1
is not definitionally equal to the right-hand side
  2

⊢ 1 = 2
lake env lean $SP/envproof/EnvProof.lean  4.66s user 47.52s system 11% cpu 7:40.23 total
EXIT=1
```

### 3.3 What each block proves

| Block | Expected | Observed | Reading |
|---|---|---|---|
| **A** `#print axioms` on the real theorem | baseline axioms | `[propext, Classical.choice, Quot.sound]` | No `sorryAx`, no custom axiom. |
| **B** restate the theorem verbatim, discharge it *by* the theorem | silent success | **no diagnostic at all** | The statement written in the closure documents **is** the theorem — no paraphrase drift between what was proved and what is reported. |
| **C** identical to B but `+∫` instead of `−∫` | **error** | `error: Type mismatch` — printing both types, differing exactly in the leading `-` | The **sign is load-bearing**. The theorem really does say `= −E[Z_τT_τ]`; the elaborator will not accept the flipped claim. |
| **D** `theorem envproof_via_sorry := by sorry` | `sorryAx` | `warning: declaration uses 'sorry'` **and** `'envproof_via_sorry' depends on axioms: [sorryAx]` | The exact audit applied to the real chain **does** detect a `sorry`. Block A's clean result is therefore informative, not vacuous. |
| **E** `theorem envproof_false : (1:ℕ) = 2 := by rfl` | **error** | `Tactic 'rfl' failed: 1 is not definitionally equal to 2` | The kernel rejects falsehoods. |
| — | overall exit code | `EXIT=1` | Correct: the file *should* fail, because C and E are meant to fail. A clean exit here would have been the alarming outcome. |

Blocks A/B succeeding while C/D/E fail **in the same file, in the same
invocation, against the same oleans** is the part that cannot be faked by
narration. Wall time `7m40s`, `11% CPU` — I/O-bound loading 8323 mathlib
`.olean` files, which is what genuine elaboration against full Mathlib costs on
this machine.

---

## 4. `lake build` (verbatim, fresh capture)

Full log: [`logs/03_lake_build_raw.txt`](logs/03_lake_build_raw.txt) — 128 lines,
**0 occurrences of "error"**, all output being deprecation/style lint.

```text
### 2026-08-20T09:29:04Z UTC
$ lake build
...
⚠ [8710/8717] Replayed RebaseguardLean.Domination
⚠ [8711/8717] Replayed RebaseguardLean.CUSUMBridge
⚠ [8712/8717] Replayed RebaseguardLean.StoppedQuantities
⚠ [8713/8717] Replayed RebaseguardLean.StoppedWalkMoment
⚠ [8714/8717] Replayed RebaseguardLean.SmallMoment
⚠ [8715/8717] Replayed RebaseguardLean.ReBaseGuardIdentity
...
Build completed successfully (8717 jobs).
EXIT=0
```

---

## 5. Per-module direct elaboration (verbatim)

`lake build` replays cached artifacts, so it was **not** relied on alone. Every
module was re-elaborated from source with `lake env lean`, which ignores the
replay cache:

```text
Basic exit=0 seconds=5
StoppedLikelihood exit=0 seconds=261
IntegralBridge exit=0 seconds=246
Domination exit=0 seconds=222
CUSUMBridge exit=0 seconds=259
StoppedQuantities exit=0 seconds=213
StoppedWalkMoment exit=0 seconds=217
SmallMoment exit=0 seconds=211
ReBaseGuardIdentity exit=0 seconds=222
RebaseguardLean(root) exit=0 seconds=238
ALL_DONE
```

Total ≈ 36 minutes of genuine elaboration. `Basic.lean` takes 5 s because it is a
21-byte placeholder with no imports; every other module pays the full Mathlib
load, which is the expected signature of real work.

---

## 6. Axiom audit, all nine principal theorems (verbatim)

```text
$ lake env lean AxFull.lean
@hasDerivAt_rebaseguard_cusum : ∀ {Ω : Type u_1} [mΩ : MeasurableSpace Ω] {μ : MeasureTheory.Measure Ω} (X : ℕ → Ω → ℝ),
  (∀ (n : ℕ), Measurable (X n)) →
    ProbabilityTheory.iIndepFun X μ →
      (∀ (j : ℕ), MeasureTheory.Measure.map (X j) μ = ProbabilityTheory.gaussianReal 0 1) →
        HasDerivAt
          (fun e =>
            ∫ (ω : Ω),
              scoreAt X (cusumTau (1 / 2) 5 X) ω *
                Real.exp (-e * walkAt X (cusumTau (1 / 2) 5 X) ω - e ^ 2 / 2 * cusumTauReal (1 / 2) 5 X ω) ∂μ)
          (-∫ (ω : Ω), scoreAt X (cusumTau (1 / 2) 5 X) ω * walkAt X (cusumTau (1 / 2) 5 X) ω ∂μ) 0
'stoppedIntegrand_hasDerivAt' depends on axioms: [propext, Classical.choice, Quot.sound]
'RebaseguardLean.hasDerivAt_integral_stoppedIntegrand_zero' depends on axioms: [propext, Classical.choice, Quot.sound]
'RebaseguardLean.hasDerivAt_integral_stoppedIntegrand_zero_of_expMoment' depends on axioms: [propext,
 Classical.choice,
 Quot.sound]
'RebaseguardLean.isStoppingTime_cusumTau' depends on axioms: [propext, Classical.choice, Quot.sound]
'RebaseguardLean.integrable_exp_forcingNat' depends on axioms: [propext, Classical.choice, Quot.sound]
'RebaseguardLean.ae_stopped_quantities_eq' depends on axioms: [propext, Classical.choice, Quot.sound]
'RebaseguardLean.integrable_exp_abs_walkAt_of_moment_tail' depends on axioms: [propext, Classical.choice, Quot.sound]
'RebaseguardLean.exists_pos_integrable_exp_abs_walkAt_rebaseguard' depends on axioms: [propext,
 Classical.choice,
 Quot.sound]
'RebaseguardLean.hasDerivAt_rebaseguard_cusum' depends on axioms: [propext, Classical.choice, Quot.sound]
```

---

## 7. Arb certificate replay (verbatim)

```text
$ .venv/bin/python -m rebaseguard_certify.audit proofs/certificate.json
{
  "Gamma_lower": "3.9243482005828971281857775466050952672958374023437500000000000000000000000000000",
  "Gamma_lower_gt_2": true,
  "Gamma_upper": "27.849382127546703280529527546605095267295837402343750000000000000000000000000000",
  "artifact_hashes_verified": true,
  "bellman_crosscheck_consistent": true,
  "block_contraction_replayed": true,
  "continuum_residual_replayed": true,
  "mode": "full replay",
  "model_verified": true,
  "resolvent_propagation_replayed": true,
  "schema": "rebaseguard.audit-report.v1",
  "status": "PASS"
}
ARB_AUDIT_EXIT=0 SECONDS=129
AUDIT_DONE
```

---

## 8. Unified verification script (verbatim)

```text
============================================================
ReBaseGuard Level 1-3 verification
root: /Users/suzhe/ReBaseGuard
date: 2026-08-20T08:58:00Z
============================================================
------------------------------------------------------------
[1/6] Lean environment
      toolchain: leanprover/lean4:v4.34.0-rc1
      Lake version 5.0.0-src+3447a66 (Lean version 4.34.0-rc1)
      mathlib rev: de5ce8a9a66a4aa68a9bdbb35b63a06d34d9ca11
PASS  Lean environment identified
------------------------------------------------------------
[2/6] lake build
PASS  lake build exit 0
      29 warning lines (cosmetic lint; see 08_LIMITATIONS)
      Build completed successfully (8717 jobs).
------------------------------------------------------------
[3/6] Lean bypass scan (case-insensitive)
PASS  no sorry / admit / axiom / unsafe / native_decide anywhere in the Lean sources
------------------------------------------------------------
[4/6] Lean axiom audit
9 theorems, all with axioms [propext, Classical.choice, Quot.sound]
PASS  axiom audit clean; final theorem elaborates
      @hasDerivAt_rebaseguard_cusum : ∀ {Ω : Type u_1} [mΩ : MeasurableSpace Ω] {μ : MeasureTheory.Measure Ω} (X : ℕ → Ω → ℝ),
        (∀ (n : ℕ), Measurable (X n)) →
          ProbabilityTheory.iIndepFun X μ →
[4b] direct source elaboration of the final module (slow)
PASS  ReBaseGuardIdentity.lean elaborates from source, exit 0
------------------------------------------------------------
[5/6] Arb certificate full-replay audit
      python 3.14.5
      python-flint 0.9.0
PASS  certificate full replay: status PASS, Gamma_lower > 2, continuum residual replayed
        "Gamma_lower": "3.9243482005828971281857775466050952672958374023437500000000000000000000000000
        "Gamma_upper": "27.849382127546703280529527546605095267295837402343750000000000000000000000000
      regenerated audit_report.md is byte-identical to the stored one
------------------------------------------------------------
[6/6] Numerical sanity checks
PASS  regression suite: 90 passed in 3.32s
PASS  certificate arithmetic and cross-check consistency
      certified interval [3.9243482005828971281857775466050952672958374023437500000000000000000000000000000, 27.849382127546703280529527546605095267295837402343750000000000000000000000000000]
      b_hat(0,0) = 15.886865164064800204357652546605095267295837402343750000000000000000000000000000
      E_b = 11.962516910658127710605800149323439675621476278236166886898187888236062501199
      stored radius (hi-lo)/2 = 11.9625169634819030761718750000000000000000000000000000000000000000000000000000000  (outward by 5.28237753655660748506765603243785237217638331131018121117639374988010000E-8)
      margin above 2: 1.9243482005828971281857775466050952672958374023437500000000000000000000000000000
      Monte Carlo, Bellman cross-check and decomposition identity all consistent
------------------------------------------------------------
RESULT: ALL CHECKS PASSED (0 skipped, explicitly allowed)
VERIFY_EXIT=0 SECONDS=543
VERIFY_DONE
```

---

## 9. What this does and does not settle

**Settled.**
* The toolchain exists, runs, and is the pinned one (`v4.34.0-rc1`, commit `3447a66…`).
* Mathlib is the unmodified published `v4.34.0-rc1` (`de5ce8a9…`, 0 dirty files).
* The toolchain **discriminates**: it accepts the real theorem and rejects a
  `sorry`, a false statement, and a sign flip — verified in one invocation.
* The theorem statement quoted throughout the closure package is the theorem the
  kernel accepted (Block B).
* `lake build` exits 0; all ten modules elaborate from source; nine principal
  theorems carry only `[propext, Classical.choice, Quot.sound]`.
* The Arb certificate replays to a bit-identical interval.

**Not settled by any log, including this one.** A transcript is still text. The
only fully adversarial resolution is for the reviewer to run it themselves:

```bash
curl -sSf https://elan.lean-lang.org/elan-init.sh | sh   # needs release.lean-lang.org
cd rebaseguard-lean && lake exe cache get && lake build
lake env lean closure/logs/EnvProof.lean     # must print sorryAx for D, errors for C and E
```

If `release.lean-lang.org` is blocked in the reviewer's environment — which is
the *specific, checkable* reason their own attempt failed — then that reviewer
cannot close the loop themselves, and the falsification test above is the
strongest available substitute. It is worth being explicit that this is a
substitute and not the real thing.

**Also not settled, and not a verification problem.** None of this shows that the
*author* can explain why `iIndepFun` rather than pairwise independence is the
right hypothesis, why the natural filtration of the detector statistic suffices
when no optional-stopping theorem is invoked, or what the Cauchy–Schwarz slice
decomposition over `{τ = m}` is doing that a naive factorization could not. Those
are answerable from the sources — `StoppedWalkMoment.lean` and
`03_LEAN_VERIFICATION.md` §"Model Correspondence Audit" set them out — but
answering them is a different activity from producing more logs, and no amount of
additional tooling substitutes for it.
