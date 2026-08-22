# Final report — Proof Track 3A/3B

## A. Exact verdict

```text
LOCATION-FAMILY-TRACK3AB-CLOSED
```

A later independently frozen variance-aware t3 replication and conditional
Lean completion closed the scoped general location-family theorem requirement.
Historical Track 3 did not pass and remains permanently partial.

## B. Exact diagnosis of the historical 4.605351% discrepancy

The historical result was

```text
Route-B replication relative discrepancy: 4.605351% > 3% — FAILED
combined-SE |z|: 1.3182 — passed its separate limit
```

Exact retained-seed replay recovered the missing path-level variance.  At
equality, the old relative discrepancy had delta-method SE `3.4936%`, so the
observed 4.605351% was only `1.3182` null standard errors.  The t3 score itself
is bounded, `psi(z)=4z/(1+z^2)` and `|psi|<=2`; the variance amplification came
from the heavy-tailed product `Z_tau sum psi`, whose path excess kurtosis was
about `265.8`.  The largest 1% of absolute Route-A gains contributed `39.17%`
of variance.

CRN worked correctly: primary `+h/-h` correlations were about `0.967--0.968`,
and paired variance was only about `3.2--3.3%` of an independence calculation.
The denominator was stable near `7.63`; exact batch replay, operating-point,
source-separation, reflection, seed, and tie checks rejected an implementation
mismatch.  The h ladder showed no stable finite-difference bias pattern.

The best-supported diagnosis is ordinary sampling variance amplified by a
heavy-tailed stopped-gain integrand—not unbounded score variance, denominator
instability, or code mismatch.

## C. Sizing rule and selected N

No fresh pilot was used.  Historical replay fixed

```text
sd_A=290.7695853130,
sd_B=98.8310787880,
derivative scale=7.6337631328.
```

The pre-outcome rule required

```text
sqrt(sd_A^2/N_A + sd_B^2/N_B) / scale <= 1%.
```

Per independent replication, the selected design was

```text
Route A: 192 × 200,000 = 38,400,000 paths
Route B: 192 × 25,000 = 4,800,000 paired streams
predicted relative SE: 0.8526542%
```

The historical 3% decision limit was retained unchanged.

## D--E. Pooled Route A and Route B

```text
Route-A Gamma_f:     8.6607571455 ± 0.0322677793
Route-A derivative: -7.6607571455 ± 0.0322677793
Route-B derivative: -7.6750754440 ± 0.0323163590
```

These are ordinary batch estimators.  Robust and tail summaries remained
diagnostic only.

## F--G. Independent replications

| replication | Route-A derivative | Route-B derivative | relative | `|z|` | result |
|---:|---:|---:|---:|---:|---|
| 1 | `-7.6395620 ± 0.0454570` | `-7.7056999 ± 0.0470133` | `0.8620%` | `1.0114` | PASS |
| 2 | `-7.6819523 ± 0.0458770` | `-7.6444510 ± 0.0443650` | `0.4894%` | `0.5876` | PASS |

Route-A replications agreed at `0.5533%`, `|z|=0.6564`; Route-B replications
agreed at `0.7980%`, `|z|=0.9475`.  Neither result is hidden by pooling.

## H--J. Pooled correspondence and frozen gate

```text
pooled relative discrepancy: 0.1867299794%
pooled |z|:                  0.3135309498
frozen relative limit:       3%
```

Both pooled and per-replication 3% criteria passed.  All statistical,
source-separation, CRN, seed, batch-identity, ARL, protocol, historical-hash,
and zero-tie gates passed.  The exact numerical decision is
`T3A-NUMERICAL-PASS`.

## K. Human theorem status

The historical human theorem remains proved under explicit regularity and
stopped differentiation hypotheses:

```text
Gamma_f = E_0[Z_tau sum_{t<=tau} psi(Z_t)],
F'_rho(0) = rho(1-Gamma_f).
```

The sign convention is `Z_t=epsilon_t-e`, parameter score `s=-psi`.  Gaussian
specialization gives `psi(z)=z` and `Gamma_f=E[Z_tau T_tau]`.  Symmetry is used
for oddness and the fixed point, not for the derivative bridge or rho scaling.
The theorem-relevant gain remains distinct from historical Stage-D
terminal-score-only quantities outside Gaussian equality.

## L--M. Lean status and exact declarations

```text
Lean status: COMPILED
classification: conditional algebraic/stopped-score proof spine
concrete infinite t3 process instantiated end to end: NO
```

The Lean file contains these 16 theorem declarations:

1. `parameterScoreSum_eq_neg_conventional`
2. `stoppedScore_derivative_bridge`
3. `reuseMean_apply`
4. `rho_scaling`
5. `locationFamily_derivative_spine`
6. `reflectPath_involutive`
7. `conventionalScoreSum_reflection`
8. `reflected_stopped_gain`
9. `reuseMean_odd`
10. `gaussian_score_specialization`
11. `gaussian_score_sum_specialization`
12. `gaussian_gain_specialization`
13. `gamma_threshold_derivative_lt_neg_one`
14. `gamma_gt_two_full_reuse_derivative_lt_neg_one`
15. `raw_gain_ne_terminal_score_gain`
16. `gaussian_terminal_gain_eq_raw`

## N. Axiom audit

Every theorem received `#print axioms`.  The exact union is

```text
propext
Classical.choice
Quot.sound
```

There is no `sorry`, `admit`, `sorryAx`, or project-specific axiom.

## O. Analytic obligations remaining human-proved

For the concrete infinite t3 CUSUM process, the following are not instantiated
end to end in Lean:

- residual-path measurability and detector-functional parameter independence;
- almost-sure finiteness and geometric stopping tails;
- finite-prefix likelihood differentiation and stopped change of measure;
- integrability and absolute event-slice summability; and
- domination of the stopped likelihood difference quotient.

The Lean theorem explicitly consumes the stopped-score derivative bridge and
visible measurability/integrability hypotheses.  It is not presented as a full
machine construction of the infinite stochastic process.

## P. Stage-F requirement status

```yaml
general location-family theorem: CLOSED
human conditional theorem: PROVED
variance-aware t3 correspondence: PASS
conditional Lean spine: COMPILED
axiom audit: CLEAN
```

This is a scoped requirement decision.  No overall Level-4 re-audit was
performed, and overall Level 4 remains historically `LEVEL-4-PARTIAL` pending
that separate re-audit.

## Q. Historical Track-3 status

```text
Track 3: LOCATION-FAMILY-THEOREM-PARTIAL — UNCHANGED
historical t3 gate: 4.605351% > 3% — FAILED — UNCHANGED
historical Track-3 Lean: NOT AUTHORIZED / NOT RUN — UNCHANGED
```

The new Track 3A/3B result does not say “Track 3 passed.”

## R. Verification count

The clean final verification target and achieved count is:

```text
historical closure-track tests: 205
Track-3A/3B focused tests:       29
authoritative repository tests: 695
combined:                       929 / 929
```

Expected historical partial/failure decisions remain asserted by their tests.
The 37 historical Track-3 tests run in frozen commit `1110065`, whose Git tree
is byte-identical to original closing commit `ba45ac3`.  This preserves its
freeze-scoped seed-confinement assertion without weakening the test to permit
future namespaces.  All other historical and new suites run from the current
tree.

## S. Reproduction command

```bash
bash level4/closure_proofs/location_family_track3ab/reproduce.sh
```

The reproducer verifies immutable hashes, independently replays all 768 batch
summaries and the gate, compiles Lean, reproduces the exact axiom inventory,
runs historical and new focused suites (using the byte-identical frozen tree
for the old Track-3 freeze-scoped suite), runs the authoritative repository
verifier once at the end, and checks the final scoped decision.

## T. Artifact entry points

- `VARIANCE_DIAGNOSIS.md` — historical mechanism;
- `PROTOCOL.md` and `results/sizing_decision.json` — frozen design;
- `REPLICATION_REPORT.md` and `results/numerical_decision.json` — new evidence;
- `lean/LocationFamilyTrack3AB.lean` and `LEAN_CORRESPONDENCE.md` — formal spine;
- `results/axiom_audit.txt` — exact inventory;
- `PROOF_OBLIGATIONS.md` — human/machine boundary;
- `results/decision.json` — final machine-readable verdict; and
- `reproduce.sh` — clean reproduction.

## U. Git checkpoints

Reachable pushed checkpoints are:

```text
eae29b26549e67b1cccbcb7dbe668c5e4efeb178  frozen protocol tree
15fdd43c6d0ac12afe319649dcf3ca737b673cc4  numerical PASS
cace80b                                      Lean spine and initial clean audit
```

The protocol was originally pushed as `96bc371` before `origin/main` was
externally force-rewritten to the content-equivalent `eae29b2` history.  Our
later integration used a safe rebase and fast-forward push, never a force push.
The closing commit is recorded by repository history and the completion
response.

## V. Next recommended action

The scoped theorem requirement is CLOSED.  The next action is:

```text
GLOBAL LEVEL-4 RE-AUDIT
```

That re-audit is not started in this campaign.  Arb or a rigorous t3 gain
inequality, if desired, remains a separate future proof track.
