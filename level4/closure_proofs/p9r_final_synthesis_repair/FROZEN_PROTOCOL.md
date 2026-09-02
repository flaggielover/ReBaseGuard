# P9R frozen protocol

Frozen at Checkpoint A. Hashed into `PROTOCOL_DIGEST.json`. No line below may
change after the anchor; gate `I4` compares bytes against the anchor commit.

## 1. Repair question

> What is the strongest globally defensible ReBaseGuard synthesis after
> repairing P9's theorem-scope inflation, SR recurrence defect, missing
> generators, and claim-ledger dependency semantics?

## 2. Theorem claims and assumptions, frozen

| id | claim | class it may hold | assumptions |
|---|---|---|---|
| `P9R-L1` | `A(e) = A(-e)` | `EXACT_THEOREM` | none beyond the frozen model |
| `P9R-L2` | `sup_e A(e) <= C_D < inf`; integrability; truncation bound | `EXACT_THEOREM` | none beyond the frozen model |
| `P9R-L3` | `A(0) > 1` | `EXACT_THEOREM` | none beyond the frozen model |
| `P9R-L4` | `A(e) -> 1`; strict set has positive measure | `EXACT_THEOREM` | none beyond the frozen model |
| `P9R-T2a` | `rho=0` invariant law `N(0,1/m)`, unique; `ARL_0 = E[A(e)]`; multiplier exactly `0` | `EXACT_THEOREM` | none beyond the frozen model |
| `P9R-T2b` | `E[A(e)] < A(0)` strictly | `CONDITIONAL_THEOREM` unless `ASM-DOM` is proved | `ASM-DOM` |
| `P9R-T3` | `rho < rho_c` does not guarantee nominal-ARL preservation in the frozen tested models | `NEGATIVE_RESULT` | none |

`P9R-T2b` may be promoted to `EXACT_THEOREM` **only** if `ASM-DOM` is proved
within this campaign, in a proof written out in `THEORY.md`. Numerical evidence
may not promote it. If `ASM-DOM` is not proved, the conditional class is the
**correct** outcome and no gate penalises it.

## 3. Reproduction targets, frozen

Source of truth:
`level4/closure_proofs/p7_statistical_consequences/results/consequences.json`,
read at run time. Nothing is transcribed by hand.

* cells: `detector in {cusum, sr}` x `m in {1,2,3,5}` x `rho in {0.0, 1.0}` = 16;
* `n_rep`, `n_cycles`, `burn_in` are taken **from the matching P7 cell**
  (5000, 50, 12 at the anchor);
* quantities compared: post-burn-in ARL (primary), cycle-1 mean (the nominal
  `A(0)` control) and cycle-2 mean (the collapse);
* estimator: per-replicate mean cycle length after `burn_in`; replicate is the
  statistical unit;
* comparison: `z = (a-b)/sqrt(se_a^2 + se_b^2)`; `MC_CONSISTENT` `|z|<=3`,
  `MC_TENSION` `|z|<=4`, `MC_DISAGREEMENT` otherwise;
* CUSUM and SR are reported and summarised **separately**;
* every SR cell is additionally replayed with the defective P9 update on the
  **same seed**, and the paired difference is reported.

Full-reuse (`rho=1`) is in frozen P9R scope; other `rho` values are not.

## 4. Detector recurrences, frozen

CUSUM: `S+_t = max(0, S+_{t-1} + Z_t - 1/2)`, `S-_t = max(0, S-_{t-1} - Z_t - 1/2)`,
`S+_0 = S-_0 = 0`, alarm iff `max >= 5` tested after the update, inclusive.

SR: stored state `y = log(1 + R)` with `y_0 = 0` (no headstart);
`ell_t = y_{t-1} + Z_t - 1/2`; alarm iff `max(ell+, ell-) >= log A` tested after
the update, inclusive; `y_t = logaddexp(0, ell_t)`;
`A = 520.886133602749`.

Chain: convention A as defined in `DEFINITION_AUDIT.md` §3; detector state reset
to the no-headstart initial state at every cycle boundary.

## 5. Estimands, frozen

`A(e) = E_e[tau]`; `ARL_0 = E_pi[A]`; nominal `A(0)`; cycle-2 mean;
`E_{e~N(0,1/m)}[A(e)]` by quadrature; per-cycle mean cycle length by index.

## 6. Response grid and quadrature, frozen

* half-grid `e in [0, 8]`, `320` intervals (`321` nodes, step `0.025`), per
  detector; `A` does not depend on `m`, so one grid serves every window;
* `20000` paths per node; seed `SHA-256(namespace | "response" | detector |
  n_intervals | n_paths | node_index)`;
* mixture `= 2 * int_0^8 A(e) phi_{1/sqrt(m)}(e) de` by composite Simpson,
  doubled by the exact evenness lemma `L1`;
* error budget, three parts, all reported:
  1. Monte Carlo — node SEs propagated through the Simpson weights;
  2. discretisation — Richardson estimate `|I_h - I_2h| / 15` from the
     half-resolution grid;
  3. truncation — **rigorously** bounded by `C_D * 2 * P(e > 8)` using `L2`;
* monotonicity audit: for every adjacent node pair report the difference, the
  combined SE, the minimum detectable increase at `3` SE, and whether an
  increase is detected; additionally report `argmax` and the maximum
  standardised excess over `A(0)`;
* evenness check at every 40th node against an independently seeded `A(-e)`.

## 7. Burn-in sensitivity, frozen

`detector x m in {1,5}`, `rho = 1`, `n_rep = 5000`, `n_cycles = 50`;
report the mean cycle length by cycle index with SEs, and the ARL under
`discard in {0,1,3,6,10,12,20}`. `discard = 12` is P7's authoritative convention.

## 8. Source classification rules, claim classes, edge types

Frozen in `experiments/ledger_schema.py`: ten claim classes, eleven edge types,
one rank table, fifteen rules `V1`-`V15`. Frozen in `experiments/claims_source.py`:
the node table, each row citing an authoritative path and section.

## 9. Verdict semantics, frozen

`CLOSED_CANDIDATE` — every identified P9 defect is repaired; the exact/conditional
split is clean; the corrected SR recurrence is used; the missing generators are
supplied or explicitly retired; the ledger and graph are source-derived and
non-inflating; the temporal anchor is valid; no mandatory unresolved repair
defect remains.

`PARTIAL_CANDIDATE` — the synthesis survives but one or more repair obligations
remain unresolved.

`FAIL_CANDIDATE` — temporal integrity fails, original P9 history is mutated, the
recurrence remains wrong, claim inflation persists, or required reproducibility
remains broken.

P9R may not self-promote to `CLOSED`. The verdict recorded in `RESULTS.md` is a
candidate; Codex adjudicates.

## 10. Production scripts intended for use

Exactly the five programs listed in `COMMAND_MANIFEST.json`, in that order. Any
program added after the anchor is a protocol violation and must be declared.

## 11. If a bug is found after the anchor

Stop. Preserve the invalid artifacts. Classify the impact in
`DISCREPANCY_REGISTER.md`. If a rerun is required, create a new documented
anchor commit rather than silently patching anchored scientific source.
