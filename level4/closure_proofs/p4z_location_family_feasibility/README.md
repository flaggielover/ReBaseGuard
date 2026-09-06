# P4Z — general location-family estimator redesign, and its governed campaign

```text
P4 = PARTIAL (untouched)   P4X, P4Y = as their own branches record (untouched)
LEVEL4_GLOBAL_CLOSURE = NO

P4Z_NUMERICAL_HOST  = LOCAL_MAC
AWS_CPU_USED_BY_P4Z = 0
```

P4Z has two phases, and they must not be conflated.

**Phase 1 — feasibility (checkpoint `d46fc68`).**  A governed successor
*design*: estimator redesign, failure taxonomy, cost model and micro-pilots.
It produced no scientific result artifact and shipped no production driver.
Verdict `P4Z_READY_FOR_NUMERICAL_QUALIFICATION`.

**Phase 2 — governed numerical qualification (this tree).**  The local Mac is
promoted to a result-bearing host under a frozen runtime contract, a frozen
worker configuration, a fail-closed producer gate and a non-adaptive 200-block
policy.  The campaign verdict, when the run completes, is in
`SUCCESSOR_CLOSURE.md` and `results/successor_closure.json`.

Neither phase rewrites history, reruns the failed architecture, converts any
historical PARTIAL/FAIL/INCOMPLETE, or relaxes any frozen numerical gate.

## The problem

P4 closed 13 of 16 gates and stopped at `PARTIAL`.  P4X resolved two of the
three failures outright and reduced the third to **8 cells in 4 configurations**
that its own precision precondition could not adjudicate.  P4Y ran four pilots
and concluded `DO_NOT_FREEZE_P4Y`: for the heavy strata, **no affordable
reference can measure the precision scale at all**.

Cost was never the obstacle.  P4X spent 25 of 60 authorised CPU-hours; P4Y-4
found every measurement grid point affordable.  The obstacle is that the
historical Route-A per-path summand `A_m S_tau^psi` has an **infinite second
moment** whenever the innovation law does — which for `t1p5` (Student-`t`,
`nu = 1.5`) it does — so its standard error estimates a quantity that does not
exist.  Five campaigns of allocation-rule redesign could not repair that.

## The fix

Both frozen detectors have a bounded survival set: a residual that does not
alarm satisfies `|Z| < c_D`, with `c_D = h+k` for CUSUM and `1/2 + log A` for
SR — the forcing increment discharge lemma L1 already uses.  So on `{tau = n}`
the **only** unbounded coordinate of `A_m` is the single alarm-causing
increment `Z_tau`.

Integrating `Z_tau` out against the base law over the alarm set is an exact
conditional expectation.  It needs four scalar functionals of the alarm set, of
which three are family free because `psi f = -f'`.  The result is unbiased, has
every moment finite, and changes nothing about the theorem, the conventions,
the detectors, the stopping rule or any threshold.

Measured on the unresolved cells: variance reduction **75x to 10 668x**, tail
index **1.5 → 3.5–4.1**, top-1 share of squared deviation **0.975 → 0.006**.
On the Gaussian control the method is neutral (VRF 1.1), which is the honest
signature of a fix aimed at exactly the diagnosed failure mode.

## Read in this order

| document | phases |
|---|---|
| `PHASE0_HISTORICAL_AUDIT.md` | 0 — the lineage, the 8 unresolved cells, what is binding |
| `FAILURE_TAXONOMY.md`, `results/failure_taxonomy.json` | 1 — 0 theorem failures, 6 architecture failures |
| `GENERAL_LOCATION_THEOREM_AUDIT.md` | 2 — the target from first principles; the bounded-survival lemma |
| `configs/estimand_contract.json` | 3 — the estimand contract, written before any estimator |
| `OLD_ESTIMATOR_DIAGNOSIS.md` | 4 — why it failed, quantified |
| `CANDIDATE_ESTIMATORS.md` | 5–8 — RB-SCORE, RB-MAP, validity audit, why no Candidate C |
| `MICROPILOT_REPORT.md`, `results/estimator_feasibility.json` | 9–10 — cost model and falsification probes |
| `CAMPAIGN_GOVERNANCE.md` | 11–16 — selection, budget, provenance, gate, power, kill gates |
| `CORRESPONDENCE_AND_FORMAL_PLAN.md` | 17–18 — cross-check and what to certify |
| `CHECKPOINT_P4Z.md`, `configs/checkpoint_p4z.json` | 19–20 — feasibility verdict and frozen checkpoint |
| `MAC_RUNTIME.md`, `production/mac_runtime_contract.json` | the result-bearing host contract and the worker freeze |
| `PRODUCTION_GOVERNANCE_NOTES.md` | decisions taken before any result was seen, including three conservative corrections |
| `SUCCESSOR_CLOSURE.md`, `results/successor_closure.json` | the campaign verdict and exactly what it discharges |

## Layout

```text
src/rebaseguard_p4z/analytic.py   the (f, F, Mlow) contract and the alarm-set integrals
src/rebaseguard_p4z/rbscore.py    Candidate A, PRIMARY
src/rebaseguard_p4z/rbmap.py      Candidate B, second official route
lean/                             the bounded-survival lemma and its axiom audit
micropilots/                      falsification probes; NOT result bearing
production/                       the result-bearing layer (see below)
tests/                            analytic contract, estimator identity, governance, gate logic
configs/                          estimand contract and frozen checkpoint
results/                          taxonomy, cost model, Lean audit, successor closure
```

The result-bearing layer:

```text
production/runtime_contract.py    host identity; fail-closed
production/scientific_hash.py     exclusion-based hashing and the path-based TCB
production/run_p4z.py             the ONLY entry point that produces a block
production/adjudicate.py          the frozen gate, applied mechanically
production/replay_check.py        determinism / replay
production/independent_adjudication.py   audits the runner rather than trusting it
production/blocks/                one JSON per (configuration, route, block)
```

`production/` did not exist at the feasibility checkpoint, by design: a
checkpoint that ships a runnable production driver invites the run.  The driver
here was authorised by a later, separate commit.

## Running the lightweight tests

```bash
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 \
  python -m pytest level4/closure_proofs/p4z_location_family_feasibility/tests -q
```

Under a few seconds of CPU.  Everything P4Z ran — micro-pilots and the governed
campaign alike — ran single-threaded on the local Mac.  The AWS CUSUM Aux4
campaign was verified alive read-only before, during and after, its branch head
never moved, and P4Z consumed zero AWS CPU.

The bounded-survival lemma is verified by `lean/verify_lean.sh` against the
prebuilt mathlib in the main worktree, read-only.

## What P4Z does not claim

Historical P4 is not repaired.  P4 is not CLOSED.  P5Y is not CLOSED.  K1 is not
closed.  Level 4 is not closed.  Nothing here is production ready in any sense
unrelated to this theorem.

In particular, discharging the 8-cell historically unadjudicated residue is
**not** a re-adjudication of the frozen 96-cell grid, and the two are reported
separately everywhere.
