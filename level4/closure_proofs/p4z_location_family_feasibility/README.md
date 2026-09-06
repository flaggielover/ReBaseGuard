# P4Z — general location-family estimator redesign and feasibility adjudication

```text
P4Z_VERDICT = P4Z_READY_FOR_NUMERICAL_QUALIFICATION
P4Z_PRODUCTION_RUN = NOT LAUNCHED       P4Z_SCIENTIFIC_RESULTS = NONE
P4 = PARTIAL (untouched)   P4X, P4Y = as their own branches record (untouched)
LEVEL4_GLOBAL_CLOSURE = NO
```

P4Z is a governed successor **design**.  It rewrites no history, reruns no
failed architecture, converts no historical PARTIAL/FAIL/INCOMPLETE, and relaxes
no frozen numerical gate.  It produces no scientific result artifact.

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
| `CHECKPOINT_P4Z.md`, `configs/checkpoint_p4z.json` | 19–20 — verdict and frozen checkpoint |

## Layout

```text
src/rebaseguard_p4z/analytic.py   the (f, F, Mlow) contract and the alarm-set integrals
src/rebaseguard_p4z/rbscore.py    Candidate A, PRIMARY
src/rebaseguard_p4z/rbmap.py      Candidate B, second official route
micropilots/                      falsification probes; NOT result bearing
tests/                            analytic contract, estimator identity, governance locks
configs/                          estimand contract and frozen checkpoint
results/                          taxonomy and cost model; every file carries result_bearing:false
```

`production/` is deliberately absent.  A checkpoint that ships a runnable
production driver invites the run.

## Running the lightweight tests

```bash
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 \
  python -m pytest level4/closure_proofs/p4z_location_family_feasibility/tests -q
```

Under a second of CPU.  The micro-pilots are ~133 CPU-seconds, single threaded,
and were run on a host the CUSUM Aux4 campaign does not use.

## What P4Z does not claim

Historical P4 is not repaired.  P4 is not CLOSED.  P5Y is not CLOSED.  Level 4
is not closed.  Nothing here is production ready.  READY means the architecture
can now *decide* the frozen gate — not that the gate will pass.
