# ReBaseGuard Level 4 — Stage B Result Ledger

Statuses are defined in `level4/src/rebaseguard_level4/ledger.py`.
`NEW-NUMERICAL` and `CANDIDATE` entries are Monte Carlo findings and
are **not** proofs. `FROZEN-*` entries are Level 1–3 results quoted
here unchanged. `RIGOROUS-CERTIFIED` means the analytic lemmas are
proved and **every** approximation between the true mathematical
object and the computed one is explicitly bounded — not merely that
interval arithmetic was used somewhere.


> **Stage A is untouched.** The Gate 4.1 and Gate 4.2 ledger in
> `level4/reports/LEDGER.md` is not rewritten by Stage B. Stage A
> recorded the `rho = 1` root as `CANDIDATE` (STRONG-CANDIDATE, Monte
> Carlo); `SB-C3` and `SB-C4` below are the Stage B upgrades of
> exactly that claim, recorded here rather than in place.

| ID | Status | Statement | Evidence |
|---|---|---|---|
| `SB-F1` | **FROZEN-CERTIFIED** | Frozen Level 1-3 remains unchanged: the Lean derivative identity and the Arb enclosure of Gamma are quoted, not re-derived, and no frozen artifact was modified. | `closure/04_ARB_CERTIFICATE.md` |
| `SB-L1` | **RIGOROUS-CERTIFIED** | Live-region enclosure: every reachable pre-alarm state lies on the two axes or in the open triangle p+m < h-2k, and the region is forward invariant. | `level4/stage_b/theorem.md` |
| `SB-L2` | **RIGOROUS-CERTIFIED** | Uniform killing: P_s(tau <= n) >= q_n(e) for every live s, hence sup_s E_s[tau] <= n/q_n and the resolvent bound \|\|(I-K_e)^-1\|\| <= 18.5782. | `level4/stage_b/src/killing.py` |
| `SB-L3` | **RIGOROUS-CERTIFIED** | Odd symmetry F_1(-e) = -F_1(e) is proved analytically by the innovation-negation / arm-swap involution, not assumed and not merely observed numerically. | `level4/stage_b/theorem.md` |
| `SB-C1` | **RIGOROUS-CERTIFIED** | G(e) = E_e[z_tau] is rigorously enclosed at every mesh point; at the mesh the bracket width on G is at most 0.023029. | `level4/stage_b/certificate/period2_certificate.json` |
| `SB-C2` | **RIGOROUS-CERTIFIED** | F_1'(e) is rigorously enclosed over the certified interval: F_1'(I) in [0.32886, 0.91243]. | `level4/stage_b/certificate/period2_certificate.json` |
| `SB-C3` | **RIGOROUS-CERTIFIED** | H(e) = F_1(e) + e has exactly one zero in I = [1.028724, 1.044724], and 0 is not in I. | `level4/stage_b/certificate/period2_certificate.json` |
| `SB-C4` | **RIGOROUS-CERTIFIED** | The period-2 multiplier satisfies lambda_2 in [0.10815, 0.83253], so \|lambda_2\| < 1 and the orbit is locally attracting. | `level4/stage_b/certificate/period2_certificate.json` |
| `SB-SCOPE-NOISE` | **OPEN** | Nothing here concerns the stochastic recursion E_{j+1} = F_1(E_j) + noise: its invariant law, bimodality and any period-2 behaviour of the noisy chain remain untouched. | — |
| `SB-SCOPE-RHO` | **OPEN** | Only rho = 1 is treated. The rho < 1 branch, the approach to rho_c, m > 1, other (k,h) and non-Gaussian innovations are all untouched. | — |
| `SB-SCOPE-GLOBAL` | **OPEN** | Uniqueness is asserted only inside the stated interval I. No global uniqueness of the period-2 orbit is asserted. | — |

## Notes

- **`SB-L1`** — Elementary proof; identical to the frozen certificate's reachable_domain. Also checked on the actual grid: the builder raises if a continuation segment escapes.
- **`SB-L3`** — This is what makes lambda_2 = [F_1'(e*)]^2 legitimate rather than requiring two independent derivative enclosures.
