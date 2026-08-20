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
| [`scripts/`](scripts/) | `verify_level_1_3.sh` |
| `rebaseguard_phase*.md` | Historical phase memos (Level 1 phenomenon, Level 2 mechanism) |
| `rebaseguard_lemma_handoff.md` | The lemma attack that motivated the certificate route |

---

## Level 4

Not started, and **not authorized by this closure**. Preparatory material for a
second detector (symmetric two-chart Shiryaev–Roberts) lives in
`rebaseguard-proof/proofs/phase4b/`, `phase4c/` and `rebaseguard_phase4d_audit.md`;
all of it is `OPEN` or `NOT CLAIMED`. See
[`closure/08_LIMITATIONS_AND_BOUNDARIES.md`](closure/08_LIMITATIONS_AND_BOUNDARIES.md).
