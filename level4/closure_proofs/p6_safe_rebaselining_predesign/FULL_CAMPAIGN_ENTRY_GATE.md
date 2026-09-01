# P6 full-campaign entry gate

```text
FULL_P6_CAMPAIGN = BLOCKED_WAITING_FOR_P5_ADJUDICATION
```

This is the current status and it does not change until every item below is
satisfied and recorded. The gate exists because the failure it guards against —
starting a prescriptive campaign on a premise that is later withdrawn — is not
recoverable by re-running anything.

---

## 1. Gate items

| # | requirement | status | evidence required to clear it |
|---:|---|---|---|
| 1 | **P5 final verdict known** | **BLOCKED** | Codex's adjudication recorded verbatim in `results/p5_verdict.json` with adjudicator and date |
| 2 | **Exact P5 claims allowed as premises listed** | BLOCKED (depends on 1) | `DEPENDENCY_LEDGER.md` §5 rewritten: every row promoted, narrowed, or moved to `NOT_ALLOWED_AS_PREMISE`. No row may remain `PROVISIONAL_P5` |
| 3 | **Rejected/narrowed P5 claims removed from P6 assumptions** | BLOCKED (depends on 2) | the deletions of `P5_ADJUDICATION_CONTINGENCIES.md` §5 step 4 applied to `P6_METHOD_CANDIDATES.md` and `P6_THEORY_TARGETS.md`, committed separately. If the verdict is Branch D, P6 halts instead |
| 4 | **P6 primary safety objective selected** | READY — awaiting approval | one of `O1`–`O5` (`SAFETY_OBJECTIVES.md` §4 Tier 2), with the primary `(D, m, Delta)` cell named. Pre-design recommendation: `O1` primary, `O5` reported, `O2` declared surrogate |
| 5 | **Baselines frozen** | READY — awaiting approval | `B0`–`B11` as written, with the `rho` grid and `m` set fixed. Frozen means: not extended after results are seen |
| 6 | **Practical vs oracle policies separated** | **MET** | `OBSERVABILITY_AUDIT.md` §7; enforced by `src/rebaseguard_p6/policy.py` and asserted by `tests/test_observability.py` |
| 7 | **Evaluation metrics frozen** | READY — awaiting approval | `EVALUATION_PROTOCOL.md` §2–§5, including the mandatory R1–R4 regimes and the mandatory `Dmed`/`Dq95`/`Dtail` triple |
| 8 | **Success criteria frozen** | READY — awaiting approval | `PREREGISTRATION_OPTIONS.md`: C1–C10 plus one option chosen for each of G-A..G-D; G-E deferred to post-pilot **by prior agreement**, which is itself recorded here |
| 9 | **Tuning/evaluation split frozen** | **MET (mechanism)** — awaiting sizing | `TUNE`/`EVAL`/`REPLAY` implemented in `src/rebaseguard_p6/seeds.py`, asserted disjoint by `tests/test_seeds.py`. Sizing follows the pilot |
| 10 | **Novelty audit plan ready** | **MET** | `NOVELTY_AUDIT_PLAN.md` (14 literature classes, 7 comparison dimensions, 18 queries); status `NOVELTY = NOT_ADJUDICATED` |
| 11 | **Compute budget approved** | READY — awaiting approval | `COMPUTE_PLAN.md`: five stages, early-stop rules `ES1`–`ES5`, budget shape |

Additional items this pre-design adds, because the work surfaced them:

| # | requirement | status | evidence |
|---:|---|---|---|
| 12 | **Correspondence checks X1–X5 pass at campaign scale** | partially met | `tests/test_correspondence.py` passes the bit-identity check at smoke scale; X3 (P7 `Arl0` reproduction in all 8 families) must run at full precision before any policy result is believed |
| 13 | **Fresh-sample cost model decided** | **BLOCKED — needs a decision** | `SAFETY_OBJECTIVES.md` §3.3 sub-decisions (C-a) monitored vs blind fresh window, (C-b) step vs proportional cost. Pre-design proposal: blind, step-shaped. This is a *modelling* choice with no precedent in P5/P7 and it changes every efficiency number |
| 14 | **`c_beta` re-derived from P7's response curves** | not started | with an interpolation error budget; the indicative `c_{0.5} ~ 0.16` is not a design constant |
| 15 | **Burn-in re-established per policy class** | not started | `EVALUATION_PROTOCOL.md` §5; P7's 12 cycles may not transfer to a closed-loop policy (`H7`) |

## 2. Reading of the current state

Items 6, 9 (mechanism) and 10 are **met**. Items 4, 5, 7, 8, 11 are **ready and
awaiting approval** — they need a decision, not more work. Items 1, 2, 3 are
**blocked on Codex** and cannot be advanced from inside this repository. Items
12–15 are **campaign-start tasks**, none of which is blocked by P5.

The critical path is therefore item 1, and nothing else.

## 3. What is explicitly permitted while blocked

* Reading P1–P5/P7 artifacts (read-only).
* Extending the pre-design documents.
* Extending the harness, its configs and its focused tests.
* Running the novelty audit of `NOVELTY_AUDIT_PLAN.md` — it depends on no P5
  claim, and running it early removes it from the critical path.
* Smoke-scale runs sufficient to test harness code.

## 4. What is forbidden while blocked

* Any screening, shortlist, confirmation or replay stage of `COMPUTE_PLAN.md`.
* Any Monte Carlo run whose purpose is to compare policies.
* Selecting a winning method, or ranking method families.
* Publishing any numerical P6 result.
* Promoting any `PROVISIONAL_P5` row in `DEPENDENCY_LEDGER.md`.
* Committing or pushing this namespace without explicit instruction.

## 5. Status line

```text
FULL_P6_CAMPAIGN = BLOCKED_WAITING_FOR_P5_ADJUDICATION
```
