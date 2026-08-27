# ReBaseGuard Lean verification

## Scope

This Lean project kernel-checks the critical analytic proof spine for the
frozen two-sided Gaussian CUSUM used by ReBaseGuard. Its final imported theorem
checks differentiation under the stopped expectation at `k=1/2`, `h=5`, after
deriving the required stopped-score, stopped-walk, and alarm-time moments from
measurability, mutual independence, and standard-Gaussian marginal laws.

This is not a formalization of the entire research repository. In particular,
Lean does not compute or certify the numerical stopped gain `Gamma_CUSUM`; the
Arb certificate is a separate evidence layer.

## Environment

| Component | Pinned configuration | Source |
|---|---|---|
| Lean | `leanprover/lean4:v4.34.0-rc1` | [`lean-toolchain`](lean-toolchain) |
| Lake | `5.0.0-src+3447a66` with Lean `v4.34.0-rc1` | `lake --version` |
| Mathlib | tag `v4.34.0-rc1`, revision `de5ce8a9a66a4aa68a9bdbb35b63a06d34d9ca11` | [`lakefile.toml`](lakefile.toml), [`lake-manifest.json`](lake-manifest.json) |
| Library target | `RebaseguardLean` | [`lakefile.toml`](lakefile.toml) |
| Root import | nine modules, including `Basic` | [`RebaseguardLean.lean`](RebaseguardLean.lean) |

The project sets `relaxedAutoImplicit = false` and uses the dependency lock in
`lake-manifest.json`.

## Build

From the repository root:

```bash
cd rebaseguard-lean
lake build
```

Current verified result: **exit 0; 8717 jobs completed successfully**. The
build emits cosmetic lint and deprecation warnings recorded in the
[closure audit](../closure/03_LEAN_VERIFICATION.md); no warning changes the
kernel result. Frozen Lean sources are not edited merely to remove them.

## Formalized statements

All names below are exact declarations in namespace `RebaseguardLean` unless
the table says otherwise.

| Human result or proof step | Lean declaration | Source | Status |
|---|---|---|---|
| Pointwise stopped-likelihood derivative | `stoppedIntegrand_hasDerivAt` | [`StoppedLikelihood.lean`](RebaseguardLean/StoppedLikelihood.lean) | Kernel-checked |
| Differentiation under the integral, given domination | `hasDerivAt_integral_stoppedIntegrand_zero` | [`IntegralBridge.lean`](RebaseguardLean/IntegralBridge.lean) | Kernel-checked under explicit hypotheses |
| CUSUM alarm is a stopping time | `isStoppingTime_cusumTau` | [`CUSUMBridge.lean`](RebaseguardLean/CUSUMBridge.lean) | Kernel-checked |
| Stopped-walk exponential moment from moment/tail bounds | `integrable_exp_abs_walkAt_of_moment_tail` | [`StoppedWalkMoment.lean`](RebaseguardLean/StoppedWalkMoment.lean) | Kernel-checked under stated bounds |
| Frozen Gaussian stopped-walk moment existence | `exists_pos_integrable_exp_abs_walkAt_rebaseguard` | [`SmallMoment.lean`](RebaseguardLean/SmallMoment.lean) | Kernel-checked |
| Three stopped-moment inputs derived for the detector | `rebaseguard_separate_moments` | [`ReBaseGuardIdentity.lean`](RebaseguardLean/ReBaseGuardIdentity.lean) | Kernel-checked |
| Gaussian derivative identity for general `k,h` | `hasDerivAt_integral_rebaseguard_gaussian` | [`ReBaseGuardIdentity.lean`](RebaseguardLean/ReBaseGuardIdentity.lean) | Kernel-checked |
| Frozen `k=1/2,h=5` derivative identity | `hasDerivAt_rebaseguard_cusum` | [`ReBaseGuardIdentity.lean`](RebaseguardLean/ReBaseGuardIdentity.lean) | Kernel-checked final theorem |

The final theorem states, for measurable mutually independent scores with
standard-Gaussian marginals,

```text
d/de E[Z_tau exp(-e T_tau - (e^2/2) tau)] at e=0
  = -E[Z_tau T_tau]
```

at the genuine inclusive alarm time of the frozen two-sided CUSUM. The exact
elaborated statement and detector/indexing correspondence are retained in
[`closure/03_LEAN_VERIFICATION.md`](../closure/03_LEAN_VERIFICATION.md).

## Sorry, bypass, and axiom audit

The zero-bypass claim is deliberately limited to the **primary imported proof
path**: [`RebaseguardLean.lean`](RebaseguardLean.lean) and the modules it
imports from `RebaseguardLean/`. A case-insensitive audit of that path finds
zero occurrences of:

- `sorry`;
- `admit`;
- a project `axiom` declaration;
- `unsafe`;
- `native_decide`.

There is a deliberate, unimported negative fixture at
[`closure/ENVIRONMENT_PROOF/logs/EnvProof.lean`](../closure/ENVIRONMENT_PROOF/logs/EnvProof.lean).
It contains `sorry` specifically to demonstrate that the audit detects and
rejects `sorryAx`. It is not imported by `RebaseguardLean.lean` and is not part
of the scientific proof path. Consequently, this README does **not** claim
that every `.lean` file in the repository is `sorry`-free.

The audited headline declarations depend only on:

```text
propext
Classical.choice
Quot.sound
```

These are the recorded Lean/Mathlib logical baseline. The primary path has no
project-specific scientific axiom and no `sorryAx`; see the
[axiom audit](../closure/03_LEAN_VERIFICATION.md#6-axiom-audit).

To repeat the textual bypass scan from this directory:

```bash
rg -n -i --glob '*.lean' '\b(sorry|admit|axiom|unsafe|native_decide)\b' \
  RebaseguardLean RebaseguardLean.lean
```

No output is the expected result for the primary imported path.

## Human to Lean correspondence

A reviewer can follow the proof without relying on filenames:

1. Read the human/Lean/Arb separation and claim inventory in
   [`closure/02_THEOREM_MAP.md`](../closure/02_THEOREM_MAP.md).
2. Locate the exact declaration in the table above and inspect its linked
   source module.
3. Check the elaborated final theorem and model audit in
   [`closure/03_LEAN_VERIFICATION.md`](../closure/03_LEAN_VERIFICATION.md).
4. Run `lake build` in this directory.
5. Audit the independent numerical inequality separately through
   [`closure/04_ARB_CERTIFICATE.md`](../closure/04_ARB_CERTIFICATE.md).

The human theorem is load-bearing: it connects the formal stopped-expectation
identity and detector correspondence to the conditional-mean reference map.
Lean and Arb do not supply that bridge by themselves.

## Related conditional and separate formalizations

The following Lean sources live outside the primary imported library. They are
related formalizations with their own boundaries and reproduction records:

| Topic | Lean source | Correspondence or report |
|---|---|---|
| Random-window `m>1` Track 1B | [`MGtOneTrack1B.lean`](../level4/closure_proofs/m_gt_1_track1b/lean/MGtOneTrack1B.lean) | [`LEAN_CORRESPONDENCE.md`](../level4/closure_proofs/m_gt_1_track1b/LEAN_CORRESPONDENCE.md) |
| Symmetric two-chart SR | [`SRDerivative.lean`](../level4/closure_proofs/sr_derivative/lean/SRDerivative.lean) | [`LEAN_CORRESPONDENCE.md`](../level4/closure_proofs/sr_derivative/LEAN_CORRESPONDENCE.md) and [current Arb certificate](../level4/closure_proofs/sr_derivative/certificate/GAMMA_CERTIFICATE.md) |
| Regular location family | [`LocationFamilyTrack3AB.lean`](../level4/closure_proofs/location_family_track3ab/lean/LocationFamilyTrack3AB.lean) | [`LEAN_CORRESPONDENCE.md`](../level4/closure_proofs/location_family_track3ab/LEAN_CORRESPONDENCE.md) |
| Deterministic period-two skeleton | [`Period2Skeleton.lean`](../level4/stage_b/lean/Period2Skeleton.lean) | [Stage-B certificate report](../level4/reports/STAGE_B_PERIOD2_CERTIFICATE_REPORT.md) |

The existence or successful compilation of one of these files does **not** by
itself establish scientific closure of its theorem or campaign. Compilation
checks exactly the encoded statement; human analytic obligations, model
correspondence, numerical premises, frozen decision rules, and historical
failures remain governed by each topic's authoritative reports. In particular,
historical Stage-D D2.3 and Track 1A remain failed despite the separate Track
1B result.

## What Lean does not prove

The primary Lean project does **not** prove or certify:

- the numerical inequality `Gamma_CUSUM > 2` or its Arb interval enclosure;
- the later `Gamma_SR > 2` Arb interval enclosure;
- the full human bridge from the stopped expectation derivative to every
  conditional-mean-map conclusion;
- Monte Carlo estimates, numerical correspondence, or experimental outputs;
- all concrete infinite-process measurability, tail, integrability, and
  domination obligations for the separate conditional `m>1`, SR, or
  location-family spines;
- the Arb certificate implementation, simulator correctness, policy
  performance, semi-real validation, or the operational-crossing result;
- a stochastic invariant law, production behavior, detector-independent or
  distribution-free validity, or a universal phase transition;
- every Stage A--F result or repository-wide scientific conclusion.

Accordingly, the accurate description is **Lean-checked proof spine**, not
“full formal verification of ReBaseGuard.” Human mathematics, Lean, Arb,
confirmatory numerics, empirical validation, and negative results remain
distinct evidence layers.

## Further audit material

- [Complete theorem/claim map](../closure/02_THEOREM_MAP.md)
- [Lean verification and model-correspondence audit](../closure/03_LEAN_VERIFICATION.md)
- [Research-synthesis evidence hierarchy](../docs/research_synthesis/EVIDENCE_HIERARCHY.md)
- [Main theorem architecture](../docs/research_synthesis/MAIN_THEOREM_ARCHITECTURE.md)
