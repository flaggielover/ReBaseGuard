# P6 continuation handoff

For whoever picks this up — Codex, a later Claude session, or a human.

```text
PRE-DESIGN_STATUS = COMPLETE
FULL_P6_CAMPAIGN  = BLOCKED_WAITING_FOR_P5_ADJUDICATION
NOVELTY           = NOT_ADJUDICATED
```

---

## 1. State of the world

| campaign | verdict | how P6 treats it |
|---|---|---|
| P1, P2, P3 | CLOSED | frozen semantics and local theory; premises |
| P4 | PARTIAL | **unused** — P6 stays inside the Gaussian core, deliberately |
| P7 | CLOSED | the source of every quantitative premise P6 relies on |
| P5 | **CLOSED_CANDIDATE / PENDING_CODEX** | **provisional; used as a premise nowhere** |

The critical path is a single item: **P5's verdict**. Nothing else in the gate
is blocked by anything outside this repository.

## 2. Do these in this order

1. **Run the novelty audit now.** `NOVELTY_AUDIT_PLAN.md` depends on no P5
   claim, takes literature search rather than compute, and is on the critical
   path for closure but not for the verdict. Doing it first removes it from the
   critical path, and — more important — if queries 6, 7 or 18 turn up prior art
   for the recursive stopping-time-selected reuse mechanism, the campaign should
   be *reframed before it runs*, not after.
2. **Decide the two modelling questions that are not P5-dependent.**
   * the fresh-sample cost model (`SAFETY_OBJECTIVES.md` §3.3: monitored vs
     blind window; step vs proportional cost). It changes every efficiency
     number and there is no precedent in P5/P7 to inherit.
   * the `e_0 = 0` regime question raised by `OBSERVABILITY_AUDIT.md` §4a: do
     R1–R3 gain an `e_0 ~ N(0, 1/m_0)` variant, or are history-using policies
     reported in R4 only?
3. **Re-derive `c_beta`** from `p7_statistical_consequences/results/response_curves.json`
   with an interpolation error budget. The indicative `c_{0.5} ~ 0.16` in the
   documents is not a design constant.
4. **Run correspondence check X3 at full precision** — the P7 `Arl0`
   reproduction in all 8 families. `results/smoke.json` shows the harness lands
   on P7's published values at 200 replicates; the real check is the same thing
   at campaign scale, and it must pass before any policy number is believed.
5. **When Codex reports on P5**, execute `P5_ADJUDICATION_CONTINGENCIES.md` §5
   in order — verdict recorded, ledger §5 rewritten with no row left at
   `PROVISIONAL_P5`, rejected material *deleted*, `V` invariants re-checked —
   and only then open `FULL_CAMPAIGN_ENTRY_GATE.md`.
6. **Do not start the campaign** until every gate item is met.

## 3. The five things most likely to go wrong

Ordered by how easy they are to do without noticing.

1. **Reintroducing `rho_c`.** It is the most natural-sounding rule in the
   repository and it is wrong (`X1`, `F15`). It creeps back as a plotting
   convention, then a default, then a threshold.
2. **Concluding a monitoring gain from a reference-state gain.** This is exactly
   the inference P7's candidate P7-E was rejected for (`S18`, `F2`). Surrogates
   may be optimised; monitoring metrics must be measured.
3. **Applying P5's T7 to a state-dependent policy.** Even under a *strong* P5
   verdict, T7 is proved for **fixed** `(D, m, rho)`. A closed-loop policy makes
   the chain policy-dependent and non-homogeneous (`H7`), and T6-B is exactly
   the request to extend it. This is the most likely over-claim on good news.
4. **Comparing against full reuse.** `B3` is the known-worst case. The bar is
   the best fixed `rho` **at matched sample cost** (`B2*`, with `Z5` as its
   oracle version).
5. **Validating on one cycle.** Cycle 1 looks nominal while cycle 2 collapses by
   `98%` (`S8`, `F14`).

## 4. What is genuinely new in this pre-design

Recorded so the next session does not have to re-derive it — and flagged as
`DESIGN_HYPOTHESIS`, not as a result. None of it is a novelty claim
(`NOVELTY = NOT_ADJUDICATED`).

* **The selection effect is also a sensor.** `E[zbar | e] = R(e) - e`, so the
  observable window mean responds to the latent reference error with gain
  `R'(0) - 1 = -GammaTilde ∈ [-17.3, -11.8]` near the origin. The mechanism that
  causes the damage is a `12x`–`17x` amplifier for measuring it. This rests only
  on `L1`/`L2`/`L4`, all closed, so it survives every P5 branch.
* **Differences of the latent state are observable.** `e_{j+1} - e_j =
  mu_{j+1} - mu_j` exactly, so the filtering problem is one-dimensional in the
  single unknown `e_0`, and readings from different cycles can be *aligned* and
  pooled rather than each estimating a fresh unknown.
* **…and that channel leaks whenever `e_0` is known** (`OBSERVABILITY_AUDIT.md`
  §4a) — found while writing the harness, fixed structurally. The general lesson:
  an information channel can be legal in the model and leaky in the simulation,
  so the audit must be re-run against the code.
* **`k` should be decoupled from `m`** (`H4`): how many past observations are
  reused and how many new ones are collected are different quantities, and the
  frozen model conflates them. This is the smallest generalisation that creates
  a real trade-off surface.
* **Full reuse is free in samples** (`H5`): at `rho_j = 1` the fresh term has
  zero weight, so no fresh observation need be collected. That asymmetry is the
  tension P6 exists to resolve and neither P5 nor P7 modelled it.
* **The blind spot has no implementable proxy** (`H8`): `Delta` is unknown in
  direction as well as magnitude, so `S10` cannot be targeted directly. The
  honest surrogate is reference-tail mass, and the gap is exactly what oracle
  `Z4` measures.
* **A greedy one-step rule exists and never recommends full reuse.**
  `rho_opt = (1/k)/(R^2 + S + 1/k) < 1` strictly, an inverse-variance weighting
  (`P6_THEORY_TARGETS.md` §7). Conditional on P5; carries no closure weight; and
  it is one-step-myopic, which is not stationary optimality.

## 5. What a successful P6 might look like — including the negative case

`METHOD_NOVELTY_SEPARATION.md` §4 states the floor deliberately: if the audit
finds prior art for every mechanism and no adaptive policy beats the
matched-cost fixed `rho`, then P6's contribution is a precise problem
formulation with an explicit cost model, an observability audit with two
positive results and one negative one, an oracle ceiling quantifying how much
adaptive control could ever be worth, and a reproduced negative result.

That is a complete campaign and a legitimate `CLOSED (negative)`. It is written
into `PREREGISTRATION_OPTIONS.md` §3 in advance, so that the search for a
positive result does not become the objective.

## 6. Repository hygiene

* Everything written by this pre-design is under
  `level4/closure_proofs/p6_safe_rebaselining_predesign/`.
* `results/tracked_index_before.txt` holds the SHA-256 of `git ls-files -s`
  taken before any write; `results/worktree_baseline.txt` records the worktree
  state at the same moment (note: `README.md` at the repository root was
  **already modified** before this work began — that change is not ours).
* `tests/test_scope.py` asserts no write outside the namespace, against that
  baseline.
* `tests/test_scope.py::test_predesign_does_not_import_p5` asserts the harness
  does not import the unadjudicated campaign.
* **Nothing has been committed or pushed.**
