# P6 — Safe re-baselining: pre-design

```text
PRE-DESIGN_STATUS  = COMPLETE
FULL_P6_CAMPAIGN   = BLOCKED_WAITING_FOR_P5_ADJUDICATION
NOVELTY            = NOT_ADJUDICATED
```

This directory contains **only** the research design for P6. No campaign has
been run, no method has been selected, no numerical P6 result exists. The one
thing that has been executed is a smoke-scale harness sanity check
(`results/smoke.json`), which is labelled as such and is not a result.

---

## 1. Why a pre-design exists at all

P6 is the first ReBaseGuard campaign that will *recommend an action*. Every
previous campaign described the system; P6 will tell someone what to do with it.
Two things follow.

* **The premises must be adjudicated.** P5 is `CLOSED_CANDIDATE / PENDING_CODEX`
  and cannot be used as a theorem premise. So the design has to be written to
  survive P5 being closed, narrowed, or reduced to partial —
  `P5_ADJUDICATION_CONTINGENCIES.md` shows that it does, and lists the nine
  invariants that hold in every branch.
* **The design must be fixed before the data.** P4 and P7 both demonstrated the
  value of frozen gates: P4's three failed gates are informative *because* they
  were written first and left unedited, and P7's boundary verdict is credible
  *because* its threshold was pre-committed.

## 2. The primary P6 question

> Can we design a post-alarm re-baselining policy that reduces reference-state
> distortion and catastrophic monitoring degradation while preserving as much
> data reuse / sample efficiency as possible?

with two refusals built in from the start:

* **not** "enforce `rho < rho_c`" — P7 established that the P3 critical fraction
  is a local mathematical boundary with no operational signature, and the
  measured in-control ARL optimum lies `1.25x`–`4.1x` *above* it (`X1`);
* **not** "reduce mean delay" — the closed failure mode is a right tail: at
  CUSUM `m=1, rho=1, Delta=1` the *median* delay (`7`) is better than nominal
  while `q95 = 275` and `P(delay > 100) = 11.4%` (`S9`).

The control variable is deliberately left open: `rho_j`, `m_j`, the fresh count
`k_j`, partial reuse, state-dependent reuse and confidence-gated reuse are all
in scope, and only the reference-update line may change — the detector is frozen.

## 3. Documents

| file | what it fixes |
|---|---|
| `DEPENDENCY_LEDGER.md` | **read this first.** Every fact P6 might use, tiered `AUTHORITATIVE_CLOSED` / `AUTHORITATIVE_PARTIAL` / `PROVISIONAL_P5` / `EMPIRICAL_HINT` / `DESIGN_HYPOTHESIS` / `NOT_ALLOWED_AS_PREMISE`, with a P6-exposure column and twelve explicitly forbidden premises |
| `SAFETY_OBJECTIVES.md` | what "safe" may and may not mean; the three-layer discipline (cost / observable / latent); constraint vs objective vs reporting |
| `OPTIMIZATION_FORMULATIONS.md` | five explicit formulations (A–E), each in stationary and finite-horizon versions |
| `P6_METHOD_CANDIDATES.md` | baselines `B0`–`B11`, method families A–F, oracle ceilings `Z1`–`Z6` |
| `OBSERVABILITY_AUDIT.md` | feature-by-feature legality; the two implementable sensors; the increment-observability result; the `e_0` leak found in the harness |
| `EVALUATION_PROTOCOL.md` | cells, metrics, the mandatory R1–R4 regimes, correspondence checks |
| `STATISTICAL_DESIGN.md` | unit, pairing, intervals, tail-event sizing, frontier uncertainty, seeds |
| `COMPUTE_PLAN.md` | five stages, early-stop rules, budget shape |
| `PREREGISTRATION_OPTIONS.md` | ten structural criteria plus options for each numeric gate |
| `NOVELTY_AUDIT_PLAN.md` | 14 literature classes, 7 comparison dimensions, 18 queries |
| `METHOD_NOVELTY_SEPARATION.md` | four kinds of novelty, the bar, and the honest floor |
| `P6_THEORY_TARGETS.md` | targets T6-A…T6-E with their exact P5 dependence; one feasibility lemma |
| `P5_ADJUDICATION_CONTINGENCIES.md` | branch-invariant core plus branches A/B/C (and D, the halt case) |
| `FAILURE_MODE_REGISTER.md` | 16 registered failure modes with detectors, plus four with none |
| `FULL_CAMPAIGN_ENTRY_GATE.md` | the 15 gate items and the current status of each |
| `CODEX_OR_CLAUDE_CONTINUATION_HANDOFF.md` | what to do next, in order |

## 4. Harness

`src/rebaseguard_p6/` is a small policy-driven chain over the **frozen** core.
It exists so that three disciplines are structural rather than aspirational:

* **the detector is untouched** — a constant policy reproduces
  `rebaseguard_p7.chain.simulate_chain` with **bit-identical `tau`**, asserted
  over four `(detector, m, rho)` cells;
* **an implementable policy cannot read the latent error** — the object it is
  handed has no such field, and the field set is asserted against the audit;
* **tuning and evaluation seeds cannot collide** — three families, asserted
  disjoint.

```
src/rebaseguard_p6/
  __init__.py   constants; policy classes; seed families
  seeds.py      deterministic TUNE / EVAL / REPLAY derivation
  policy.py     CycleObservation (audited field set), OracleObservation,
                Decision, BasePolicy, baselines, one oracle, one Family-E sketch
  chain.py      policy-driven chain; frozen detector semantics
  metrics.py    per-replicate metrics, tagged latent / observable / cost
  stats.py      paired bootstrap, P7 verdict labels, tail-event check
tests/          32 focused tests, all passing
configs/        P6_PREDESIGN_PROTOCOL.json — the design skeleton, PENDING fields marked
results/        worktree_baseline.txt, tracked_index_before.txt, smoke.json
```

```bash
/Users/suzhe/ReBaseGuard/level4/.venv/bin/python -m pytest \
  level4/closure_proofs/p6_safe_rebaselining_predesign/tests -q
```

## 5. What this pre-design deliberately does not do

* It selects **no** winning method and ranks **no** family.
* It uses **no** P5 claim as a premise; the nine `V` invariants of
  `P5_ADJUDICATION_CONTINGENCIES.md` §0 hold in every branch.
* It sets **no** numerical gate threshold; `PREREGISTRATION_OPTIONS.md` offers
  options with arguments, for approval.
* It claims **no** novelty.
* It runs no campaign, and commits nothing.
