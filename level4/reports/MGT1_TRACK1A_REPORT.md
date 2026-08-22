# Proof Track 1A final report

## A. Track verdict

`MGT1-TRACK1A-FAILED`

The actual Stage-A/Stage-D distinction replicated, but the complete frozen
numerical gate failed one independent decomposition cell. The mandatory stop
rule prevented Lean from starting.

## B. Stage-A / Stage-D distinction

`PASS` under the Track 1A rule. At the preselected effect-bearing cells:

- `m=20`: `Gamma_D-Gamma_A=+0.05867 ± 0.00947`, 95% CI
  `[+0.04010,+0.07724]`;
- `m=50`: `Gamma_D-Gamma_A=+0.15321 ± 0.00473`, 95% CI
  `[+0.14394,+0.16248]`.

Both independent replication point estimates were positive in both cells.
The old five-SE-per-cell rule was not reused or changed.

## C. Exact numerical effect by `m`

| `m` | `Gamma_A` | `Gamma_D` | gain effect D−A ± SE | 95% CI | derivative effect D−A | standardized effect |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 15.87283 | 15.91283 | +0.03999 ± 0.04037 | [-0.03913,+0.11911] | -0.03999 | +0.00099 |
| 2 | 13.21935 | 13.28614 | +0.06678 ± 0.03348 | [+0.00115,+0.13241] | -0.06678 | +0.00199 |
| 5 | 10.15767 | 10.21176 | +0.05409 ± 0.02502 | [+0.00504,+0.10313] | -0.05409 | +0.00216 |
| 10 | 7.08479 | 7.10962 | +0.02482 ± 0.01650 | [-0.00751,+0.05715] | -0.02482 | +0.00150 |
| 20 | 4.20764 | 4.26631 | +0.05867 ± 0.00947 | [+0.04010,+0.07724] | -0.05867 | +0.00619 |
| 50 | 2.21270 | 2.36592 | +0.15321 ± 0.00473 | [+0.14394,+0.16248] | -0.15321 | +0.03238 |

## D. `P(tau<m)` by `m`

| `m` | probability |
|---:|---:|
| 1 | 0 |
| 2 | 0.0000005 |
| 5 | 0.0006470 |
| 10 | 0.0073225 |
| 20 | 0.0276720 |
| 50 | 0.0894750 |

## E. Short-cycle correction

| `m` | `C_m ± SE` |
|---:|---:|
| 1 | 0 exactly |
| 2 | 0.00000759 ± 0.00000759 |
| 5 | 0.00251193 ± 0.00008189 |
| 10 | 0.02256694 ± 0.00024308 |
| 20 | 0.07757686 ± 0.00045932 |
| 50 | 0.20146107 ± 0.00073596 |

Every generated correction integrand was nonnegative. At `m=20,50`, the
ordinary-stop/fixed-denominator contribution was negative, while `C_m` was
larger and positive; the two mechanisms were therefore empirically separated.

## F. Decomposition correspondence

The same-path identity held to machine roundoff in both ordinary-stop routes.
The pre-frozen independent-route comparison nevertheless failed at `m=20`:

`|Gamma_D,direct-(Gamma_B+C_m)_independent|=0.02955`, combined SE `0.00944`,
absolute z `3.130`, relative discrepancy `0.693%`.

The frozen pooled limit was three SE. Every other pooled cell was at most
`2.858` SE, and every per-replication cell was at most `2.881` SE. These facts
diagnose rather than waive the failure.

## G. `m=1` control

`PASS`. Stage A and Stage D agreed bit-for-bit on a shared 20,000-path stream;
`C_1=0` exactly. Independent gains agreed within `0.991` combined SE. The new
pooled gain `15.89280 ± 0.02018` agreed with the prior independent
`15.88769 ± 0.02850` within `0.146` combined SE.

## H. Lean status

`NOT STARTED — FROZEN DECOMPOSITION GATE FAILED`.

The human theorem remains

`F'_{rho,m}(0)=rho(1-E_0[A_m^D T_tau])`,

with the nonnegative short-cycle correction. No Track 1A machine-checked
theorem is claimed.

## I. Axiom audit

`NOT RUN`; no Track 1A Lean declaration, placeholder, or scientific axiom was
introduced.

## J. Arb

`NOT REQUIRED`. No new rigorously certified scalar inequality is claimed.

## K. Previously unmet `m>1 derivative theorem` requirement

`PARTIALLY`.

The requirement is not closed: the human theorem, numerical distinction, and
pathwise algebra are supported, but Track 1A failed its independent
decomposition gate and did not reach Lean. This is not an overall Level-4
decision.

## L. Historical Stage-D D2.3

`FAILED`, unchanged. The previous proof track remains
`MGT1-THEOREM-PARTIAL`; Stage F remains `LEVEL-4-PARTIAL`.

## M. Tests

Track 1A adds 32 isolated tests; they pass. The previous 46-test proof track
and authoritative 695-test repository suite await the final clean-worktree
rerun at this report checkpoint.

## N. Artifact entry points

- `level4/closure_proofs/m_gt_1_track1a/REPLICATION_REPORT.md`
- `level4/closure_proofs/m_gt_1_track1a/THEOREM.md`
- `level4/closure_proofs/m_gt_1_track1a/LEAN_CORRESPONDENCE.md`
- `level4/closure_proofs/m_gt_1_track1a/FAILURE_DIAGNOSES.md`
- `level4/closure_proofs/m_gt_1_track1a/results/replication.json`
- `level4/closure_proofs/m_gt_1_track1a/results/decision.json`
- `level4/closure_proofs/m_gt_1_track1a/reproduce.sh`

## O. Git

Protocol freeze commit `13e497564d5440bc5ea0ae528df682653139ec2c` was pushed to
`origin/main`. The final failure-package commit and push are pending clean
verification.

## P. Next proof track

**Proof Track 1B — Correlation-Aware Decomposition Replication + Lean Completion**

