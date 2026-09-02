# P5X proof obligations and lemma dependency graph

Frozen at Checkpoint A. Every node names what discharges it and what fails if
it cannot be discharged.

## 1. Dependency graph

```text
              [P5-T1] [P5-T2] [P5-T3]           (imported, exact)
                  |       |       |
                  v       v       v
   L1 ---------> P5X-T1 (reduction, all m, all e)
   |               |
   |               +--> L2 ---------> P5X-T2 (second moments)
   |               |
   L4 <------------+                 L3 ---------> P5X-T3 (far field)
   |                                  |
   v                                  v
  C1 (certified R enclosures on the cover) <----- L5 (analyticity in e)
   |          |               |
   v          v               v
 P5X-T4    C2 (certified S,  C3 (certified R'
 (R_max)      M_2, s_min)        enclosures)
   |          |                    |
   v          v                    v
 P5X-T5    P5X-T6 <--- L6 --- [P5-T7]        P5X-T7 (shape; discharges H2,H3a,H3b)
   |          |                                   |
   |          |                                   v
   |          |                              P5X-T8 (skeleton dynamics; + C4 rho-cover)
   |          |                                   |
   +----------+--------> P5X-T9 <-----------------+   (T8 optional: T9 does not use it)
                            ^
                            |
                    [P3 lambda] + [existing Gamma certificates]
```

## 2. Analytical lemmas

| id | statement | discharge route | if it fails |
|---|---|---|---|
| `L1` | the pre-alarm detector state is Markov on `E_D`; the alarm set from `x` is the complement of `(l(x), u(x))`; the reset state is `x_0 = (0,0)`; first-step conditioning gives `P5X-T1(b)` and the convention-A bookkeeping of `P5X-T1(c)` | elementary; write out the first-step conditioning for `g_r`, `h_j` and the short-`tau` terms, and verify the `w = min(m,tau)` split `{tau >= m}` / `{tau = t < m}` term by term | the whole campaign is void; this is the falsifiable core, and the probe is its first test |
| `L2` | pair recursion for `E_e[ Z_{tau-r} Z_{tau-r'} ; tau >= m ]` on the same square, `O(m^2)` backward functions | same first-step conditioning, carried on a pair index | `S_{D,m}` for `m >= 2` is not certifiable; `P5X-T6` retreats to `m = 1` (still a real theorem) |
| `L3` | far-field forgetting with an explicit decreasing majorant `B_D(e)`, valid for every `m` simultaneously | on `{|z_1| >= c_D}` the alarm is immediate and `w = 1` for every `m`; Cauchy–Schwarz on the complement with `P5-T5` | the cover must be extended outward; `e_far` grows; cost only |
| `L4` | `‖(I-K_e)^{-1}‖_inf = sup_x E_{x,e}[tau] <= C_D(e) < infinity` for every `e`; and the monotone Bellman minorant used for the `e = 0` certificates extends to interval-valued `e`, with the worst case at the endpoint of the interval nearest `0` | the existing monotone one-sided block argument (`closure/04_ARB_CERTIFICATE.md` §3.6, `N-01`) plus the elementary observation that the arm aligned with the drift alarms *faster* as `\|e\|` grows | error propagation loses its constant; enclosures widen; possibly fatal to `P5X-T4`'s margin |
| `L5` | `e -> R_{D,m}(e)` and `e -> S_{D,m}(e)` are real-analytic; hence interval-valued `e` is admissible and no separate modulus of continuity is required | `phi(z+e)` is entire; the Neumann series converges uniformly on compact `e`-sets by `L4` | a modulus-of-continuity lemma must be proved separately, which is strictly more work |
| `L6` | `E_pi[e^2] = rho^2 E_pi[R^2 + S] + (1-rho)^2/m` | invariance plus `P5-T2` and finiteness of `E_pi[e^2]` (`P5-T7`) | `P5X-T6` fails; only the one-step bound survives |
| `L7` | anti-concentration `pi(|e| > r) >= (E_pi[e^2] - r^2)_+^2 / E_pi[e^4]` with certified `M_4` | Paley–Zygmund / Cauchy–Schwarz | `P5X-T6b` is dropped; `P5X-T6`'s corollary is unaffected |
| `L8` | flip nondegeneracy at `rho_c` for an odd `R`: the branch is supercritical iff the coefficient built from `R'''(0)` has the right sign | third-derivative system on the same square | `P5X-T8` cannot be extended toward `rho_c`; `eta` stays larger |

## 3. Certified inequality obligations

| id | inequality | domain | consumed by |
|---|---|---|---|
| `C1` | enclosure of `R_{D,m}(e)` on every cell of a finite adaptive cover of `[0, 12]`, interval-valued `e` | 2 detectors × 4 windows | `P5X-T4`, `T7` |
| `C2` | enclosure of `E_e[Rbar^2]` on the same cover, plus `S = E[Rbar^2] - R^2` | same | `P5X-T6` (`s_min`, `M_2`) |
| `C3` | enclosure of `R'_{D,m}(e)` on a cover of `[0, 2]`, and on `[0, e_0]` for the sign-near-zero argument | same | `P5X-T7` |
| `C4` | enclosure of `f_rho`, `f_rho'` on a cover of `I_rho` × a cover of `[ (1+eta) rho_c, 1 ]` | same | `P5X-T8` |
| `C5` | per-cell resolvent bound from `L4` | every cell | error propagation for `C1`–`C4` |
| `C6` | (optional) enclosure of `E_e[Rbar^4]` | same | `P5X-T6b` |

`C1` and `C2` are mandatory. `C3` is required for Level C. `C4` and `C6` are
optional and their absence does not fail the campaign.

## 4. Order of work (frozen)

1. Write the human proofs of `L1`, `L2`, `L3`, `L5`, `L6` in full, with
   constants, before any certified code is written.
2. Prove `L4` and state the resolvent bound as an explicit function of the
   `e`-interval.
3. Build `C1` for **one** cell of **one** detector at **one** `m`, and publish
   its achieved width, before scaling. If the achieved width exceeds `0.2` the
   campaign re-plans rather than scaling a losing method.
4. Scale `C1`, `C2`; establish `P5X-T4`, `T5`, `T6`.
5. Attempt `C3` and `P5X-T7`.
6. Attempt `C4`, `L8` and `P5X-T8` only if 4 and 5 succeed.
7. Assemble `P5X-T9`; run the empirical correspondence plan; adjudicate.

Step 3 is a deliberate stop-gate: it is the cheapest possible falsification of
the campaign's central engineering assumption.
