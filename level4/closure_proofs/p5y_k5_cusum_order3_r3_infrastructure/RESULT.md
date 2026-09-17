# R3 result: PARTIALLY_QUALIFIED (non-scientific)

**Run.**
- Frozen protocol at `1089ea1e`, run once on rebaseguard-vultr-02 from a clean clone (0 porcelain lines),
  venv `/root/work/rbg-cusum-aux5-venv`.
- Started 2026-09-16T14:48:55Z, `QUALIFICATION_RESULT_R3.json` written 15:31:30Z, 0 runner failures.
- `qualify_r3.py check` reproduces the stored result with no problems.
- Evidence: `evidence/qualification_r3/` (with `RUN_PROVENANCE.json`).

**Scope.** No real cell was evaluated, no `R'''` of any `(D,m)` was computed, no probe was run, and the
authorization registry is empty.

## Gates

| gate | result |
|---|---|
| R01 R1/R2 preserved | PASS |
| R02 / R03 C_o0 / C_e0 certificate replay | PASS / PASS |
| R04 registry consistent | PASS |
| R05 σ-invariance of real kernels | PASS |
| R06 scalar equivalence + Leibniz structure (C1 0, C7 0) | PASS |
| R07 graded residual + candidate containment (C2/C3 0, C6 0) | PASS |
| R08 graded never looser | PASS |
| R09 He₆ / j₅ | PASS |
| R10 first-cell manufactured soundness (FC1–FC5, 0 violations) | PASS |
| R11 evenness lemma (odd holds, non-odd control fails) | PASS |
| **R12 mutation suites** | **FAIL**: wiring 12/12, certificate 3/3, R⁽⁵⁾ **5/6** |
| R13 determinism | PASS |
| R14 fail-closed | PASS |
| R15 fences and registries | PASS |
| R16 runtime identity | PASS |
| R17 R2 graded regression | PASS |

**R12 failure.** `B01_M5_USES_ODD_COMPONENT` was not detected on any of the 5 frozen trials; DEV detected it.
- The anchored tower majorant is 13–600× the exact `max|R⁽⁵⁾|` on the frozen fixtures (FC1: 4.48·10⁸ vs
  3.53·10⁶).
- So summing the odd component instead of the even one still dominates the truth. The fixtures lack the power to
  show that the even-component rule is load-bearing.
- This is a test-power gap, not a soundness violation. Per the frozen rule, every soundness gate passes, so the
  verdict is **PARTIALLY_QUALIFIED**. Nothing was repaired or rerun after the result.

## Certified constants

- `C_o0 ≤ 20.4322` (margin ≥ 0.0205).
- `C_e0 ≤ 469.7697` (margin ≥ 0.00409).
- Exact upper endpoints are in `config/OPERATOR_CERTIFICATES_R3.json`.

## First-cell strategies (manufactured, m = 1)

| fixture | radius A | radius B (point + penalty) | M5 / true max\|R⁽⁵⁾\| |
|---|---:|---:|---:|
| FC1 C1233 analogue | 5445 | 60.7 | 4.5·10⁸ / 3.5·10⁶ |
| FC2 C50 | 1326 | 829 | 4.1·10⁶ / 4.1·10⁵ |
| FC3 C4 wide | 16.5 | 12.8 | 2556 / 78 |
| FC4 C100 small odd eigen | 111.7 | 4.64 | 2.4·10⁵ / 384 |
| FC5 C10, x₁ = 1/20 | 25.4 | 13.3 | 10637 / 444 |

Strategy B is tighter on every fixture.

## Cell-0 forecast (committed magnitudes + certified constants; G factor 1, m = 1)

`S* = 33.41`, `x₁²/2 = 25836889/200000000000000`.

**Certified constants:**
- **Strategy A:** radius 2.58·10⁵, UNINFORMATIVE.
- **Strategy B:**
  - point radius (A1) 2493;
  - M5 = 4.71·10¹⁰, penalty 6079;
  - radius 8572, UNINFORMATIVE (proxy 1.86·10⁵).
- G factors 10 and 100 do not change either class.

**Best case with the non-certified float estimate `C_o0 = 4.68` (next-step input only):**
- A: 3.28·10⁴, UNINFORMATIVE.
- B: 427 + 439 = 865, **MARGINAL**.

**Attribution** (A cell radius, other constants certified):

| variant | A cell radius |
|---|---:|
| baseline | 2.58·10⁵ |
| C_o0 = 4.68 | 3.28·10⁴ |
| C_e0 = C_upper | 2.61·10⁶ |
| no leakage (invalid diagnostic) | 1.79·10⁵ |
| residuals ×0.1 | 2.58·10⁴ |
| midpoint at e0 | 2945 |

M5: unanchored 2.8·10¹³ → anchored 4.7·10¹⁰ → 9.8·10⁹ with C_o0 = 4.68.

**Reading.**
- The certified odd bound `E_x[τ ∧ T_0] ≤ 20.4` is a coupling bound, 4.4× the float odd-resolvent norm. This slack,
  not the polynomial supersolution (float `E τ∧T_0` ≈ 16.6), is the binding lever.
- With a sharper certified odd constant, Strategy B moves from UNINFORMATIVE to MARGINAL.

## Final status

- **Verdict:** PARTIALLY_QUALIFIED.
- **B1:** OPEN.
- **Preferred first-cell strategy:** B.
- **R⁽⁵⁾ majorant source:** CHEAP_SUCCESSOR (the anchored graded tower).
- **REAL_CELL_QUALIFICATION:** NOT_AUTHORIZED.
- **NEXT_STEP:** REPAIR_GRADED_OPERATOR_CERTIFICATE (frozen rule: preferred class UNINFORMATIVE with certified
  constants, MARGINAL for the same strategy with the non-certified operator estimate).
- **Carry-over:** a successor should also give B01 a fixture with a tight R⁽⁵⁾ majorant.

**Operational note.** The local completion waiter polled `pgrep -f "qualify_r3.py run"` over ssh. The remote
`bash -c` command line itself contains that string, so the waiter matched itself and never exited. The qualification
had finished at 15:31:30Z, and the evidence is unaffected.
