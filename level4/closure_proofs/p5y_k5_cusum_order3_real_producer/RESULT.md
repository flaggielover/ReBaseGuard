# Real CUSUM signed order-3 producer: qualification r1 result

**Run.**
- The protocol, gates and bound code were frozen in `e69a0224`, a fast-forward on `p5y-postk1-frontier` over `aca34248`.
- The qualification ran after that commit on `rebaseguard-vultr-02` in venv `/root/work/rbg-cusum-aux5-venv`, from a
  clean checkout of exactly `e69a0224` (`evidence/qualification_r1/RUN_PROVENANCE.json`: 0 porcelain lines, DEV
  override unset).
- 62 parts ran, each in a fresh process, with 0 runner failures.
- `qualify_order3.py check` re-verified the bound code, the protocol hash and every part hash, recomputed all verdicts,
  and reported `problems: []`.

`QUALIFICATION_RESULT.json` sha256 is `34932e3db94e24ee…`; protocol sha256 is `f2c52ce329a031d2…`.

## Gates (frozen in `config/PRE_RESULT_GATES.json`)

| Gate | Verdict | Gate | Verdict |
|---|---|---|---|
| G01 input identity | PASS | G09 no finite-difference substitution | PASS |
| G02 producer identity | PASS | G10 precision escalation consistency | PASS |
| G03 exact derivative order 3 | PASS | G11 deterministic serialization | PASS |
| G04 finite interval | PASS | G12 deterministic scientific hash | PASS |
| G05 lo ≤ hi | PASS | G13 runtime/dependency identity | PASS |
| G06 signed interval semantics | PASS | G14 fail-closed | PASS |
| G07 whole-cell soundness | PASS | G15 K1 record provenance | PASS |
| G08 no unsigned magnitude substitution | PASS | G16 no scientific-probe contamination | PASS |

## Questions

| id | Verdict | Evidence |
|---|---|---|
| QS manufactured soundness | **PASS** | 24 fixtures, **0 containment violations** at `e0` plus 17 exact grid points (objects, midpoint and signed export, m = 1, 2, 3, 5). Signs certified both ways; the zero-`R'''`, sign-crossing and wide-cell exports are SIGN_INDETERMINATE, and every export contains the exact truth. |
| QC residual consistency | **PASS** | On every noise-0 fixture the certified `G_r` residual is below 10⁻⁶⁰. |
| QM mutation sensitivity | **FAIL** | **20 / 21** required mutations detected. `R05_RESIDUAL_R0_USES_CANDIDATE_SOURCE` was not detected on any of the 13 trials. |
| QR reference-kernel differential | **PASS** | 15 / 15 frozen QN1 trials. The engine equals the exact-rational reference on `F:3` midpoint and cascade and on `W:3` cascade and Taylor (relative excess ≤ 2⁻²⁰⁰). The engine's Taylor bound and export lie inside the reference's. |
| QX independent cross-check | **PASS** | 8 fixtures × 4 m. The independent rational-function enclosure intersects the engine's, both contain the sampled truth, and there is no sign contradiction. Engine/independent width ratio is 1.05–14.3. |
| QO real-operator integration (synthetic) | **PASS** | 3 synthetic drifts, 34 reachable states each. The Arb residual branch agrees with independent float quadrature to ≤ 8.0·10⁻¹⁰ beyond its radius. `delta_mid` 6.91 / 7.37 / 6.59 dominates the sampled max 6.54 / 7.31 / 6.51. |
| QP precision behavior | **STAGNATING** | See below. |

**The undetected mutation.**
- R05 makes the `r = 0` residual subtract the candidate `Ŝ_0'''` instead of the closed form. That drops a
  `C·‖Ŝ_0''' − S_0'''‖` charge, which is unsound.
- During DEV calibration it was caught only incidentally, by one noisy random trial. No frozen fixture isolates that
  edge, so the r1 mutation matrix lacks power there.
- It is not a producer defect: the producer's `r = 0` branch uses `Sclosed_3` (`rung3_residual.py`), and the soundness
  gates G03–G07 and G14 pass.
- **Post-result diagnostic, not part of r1** (`evidence/postresult_diagnostic/`): on a `controlled_K3` system with
  only the `S_0'''` candidate offset, the unmutated producer has 0 violations and the R05 mutant has 5. An r2
  protocol with this isolating fixture would detect R05.
- **QM r1 stays FAIL.**

**Precision** (whole-cell width is the binding label; the midpoint interval is reported, non-binding):

| Fixture | whole cell | midpoint | whole-cell width 128→512 | midpoint width 128 → 512 |
|---|---|---|---|---|
| T01 random, exact candidates | STAGNATING | CONTRACTING | 0.0494 (constant) | 5.9e−38 → 1.5e−153 |
| T11 tiny positive constant R''' | CONTRACTING | CONTRACTING | 6.1e−50 → 1.2e−165 | same |
| T15 ill-conditioned C = 1000 | STAGNATING | STAGNATING | 0.0787 | 3.3e−6 |
| T16 near-singular C = 10⁶ | STAGNATING | CONTRACTING | 0.0745 | 5.3e−27 → 1.3e−142 |
| T17 CUSUM-like C = 1233, Cρ = 0.3133 | STAGNATING | STAGNATING | 1.0957 | 2.7e−6 |
| T18 same, candidate noise 10⁻⁶ | STAGNATING | STAGNATING | 1.0982 | 2.5e−3 |

Across all fixtures there was no sign flip and no pair of disjoint intervals. CPU was ≤ 0.03 s per fixture and peak RSS
36 MiB at every precision.
- Wherever candidates are exact, the certified width contracts like 2⁻ᵇⁱᵗˢ.
- Wherever it cannot contract, the width is a mathematical floor set by candidate error and ρ-terms times `C`, not by
  rounding.
- T17/T18 show `C ≈ 1233` turning 10⁻⁹ candidate error into an O(1) whole-cell width.

**Fail-closed.** All 18 controls pass: precision 64 and 200; truncated record; tampered manifest; wrong cell; m = 4
(engine and record); tampered coefficient table; inf enclosure; NaN candidate; huge-C finite and sound;
sign-indeterminate not fabricated; singular resolvent; `C = 0`; near-singular sound; runtime mismatch; missing input;
negative ρ.

All 6 real-cell gate controls pass: no authorization; forged authorization; gate before record validation; empty
registry; manifest verifies; subclass surface. In the gate and operator parts, zero repository calls reached
collocation, `prepare`, residuals, propagation, the engine or record validation.

**K1 provenance.** The committed copies of cells 0 and 309 validate V01–V10: manifest `29ad1f9b`, identity
`3692d0fe`, frozen hash recomputes. `target_gate` is PASS for m = 1, 2, 3, 5 on both; cell 309 is flagged
`endpoint_region`.

## Verdict

`REAL_ORDER3_PRODUCER = PARTIALLY_QUALIFIED`

**What passes.**
- A real implementation exists and is wired to the frozen CUSUM chain.
- Whole-cell soundness is proved (`DESIGN_REAL.md` §4), and every soundness gate passes.
- Certified signed intervals are demonstrated on manufactured systems with exact truth, as is agreement with the frozen
  reference kernel and with an independent method.
- The new rung's residual is verified on the real CUSUM Arb kernels against independent quadrature.
- Fail-closed behavior and determinism hold, and the governance registry is frozen empty.

**Blockers to scientific probe authorization.**
1. **QM r1 = FAIL** (R05 undetected). An r2 protocol with an isolating `r = 0` source fixture is required.
2. **REAL_CELL_QUALIFICATION = NOT_AUTHORIZED.** The real end-to-end path (`Order3Certifier.prepare`,
   `collect_inputs`, `cross_check_k1`, Aux5 gates) has never executed, and L4 host determinism is unmeasured.
3. **Cell-0 width** (`DESIGN_REAL.md` §6, from committed magnitudes only).
   - The frozen midpoint rule forces a certified `R'''` radius ≥ `C·3k₁·ε_H,mid` ≈ **2.7·10⁷** (r = 0) and up to
     7.3·10⁷ (r = 1) at CUSUM cell 0.
   - The H3a sign test there is therefore expected SIGN_INDETERMINATE, which the frozen oracle's Q2 turns into STOP.
   - The driver is `C ≈ 1233` acting on the frozen midpoint curvature error, not the order-4 tower. Precision does not
     help (see QP).

B1 stays **OPEN**. No future probe packet is prepared, because the producer is not QUALIFIED. No cell set is proposed,
since blocker 3 must be resolved before a probe can be informative.

```text
REAL_ORDER3_PRODUCER                = PARTIALLY_QUALIFIED
SIGNED_R3_CERTIFICATION             = POSSIBLE            (demonstrated on manufactured systems; not on a real cell)
WHOLE_CELL_R3_CERTIFICATION         = PASS                (proof + manufactured evidence; no real cell run)
AUX3_FAILURE_RELEVANCE_TO_R3        = MEDIUM
C_RHO_AMPLIFICATION                 = UNRESOLVED
PRECISION_BEHAVIOR                  = STAGNATING          (width floor is mathematical; exact-candidate intervals contract)
REAL_CELL_QUALIFICATION             = NOT_AUTHORIZED
REAL_K5_SCIENTIFIC_CELL_EVALUATED   = NO
SCIENTIFIC_K5_PROBE_RUN             = NO
FULL_K5_PRODUCTION_RUN              = NO
B1_NO_CERTIFIED_ORDER3_PRODUCER     = OPEN
CUSUM_CLOSURE_MODIFIED = NO   K1_RECORDS_MODIFIED = NO   K5B_MODIFIED = NO   AWS_PS1_TOUCHED = NO
ORIGIN_MAIN_TOUCHED = NO      K5_DECLARED_CLOSED = NO    P5Y_DECLARED_CLOSED = NO
NEXT_STEP = REPAIR_REAL_ORDER3_PRODUCER
```

**Repair scope, stated and not started.**
- (a) An r2 protocol adding the isolating `r = 0` source fixture.
- (b) A producer-owned, higher-accuracy base solve near `e = 0`, or a point-certificate anchoring, that shrinks
  `ε_H,mid`, `ε_D,mid` and `ε_F,mid` at `C ≈ 1233`. It must be governed as a successor, because the order-3 producer
  cannot reuse sealed K1 candidates anyway.
- (c) An owner decision on L4 real-cell qualification.
