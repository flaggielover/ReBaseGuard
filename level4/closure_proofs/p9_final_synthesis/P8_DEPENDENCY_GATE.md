# P8 dependency gate — what P9 may finish now, and what must wait for Codex

> **RESOLVED.** The authoritative verdict is **`P8 = FAIL`** (16 PASS / 5 FAIL;
> `G14` temporal integrity fails). Claude's `PARTIAL_CANDIDATE` did not survive.
> The `FAIL` branch of §4 was applied literally — see
> `P8_TO_P9_RECONCILIATION.md`. This file is retained **unedited below** as the
> record of what P9 committed to *before* the outcome was known.

**P8 status at the time of writing:** `UNDER_CODEX_ADJUDICATION`.
Claude-side discovery reported `P8 = PARTIAL_CANDIDATE`. That is **not
authoritative** and is not used as a premise anywhere in P9.

**Verified at campaign start:** `level4/closure_proofs/p8_model_class_robustness/`
is untracked in the `main` worktree and contains **no**
`INDEPENDENT_ADJUDICATION.md`. P9 therefore proceeded with P8-independent work
only, and read the P8 tree **read-only** for contingency design.

---

## 1. Isolation actually performed

| control | what was done |
|---|---|
| worktree | P9 runs in `/Users/suzhe/ReBaseGuard-p9` on branch `p9-research`, created from the anchor commit `ffe23a6`. No P9 write ever touches the `main` worktree. |
| P8 artifacts | never copied, merged, cherry-picked, or absorbed. The untracked P8 tree stays in `main` where Codex can work on it. |
| contamination | P9's branch does **not** contain the P8 tree at all (it was untracked at branch point), so no provisional P8 artifact can be mistaken for a P9 premise. |
| reads | P8 files were read from the `main` worktree path for §4 contingency design only, and every derived item is labelled `PROVISIONAL_P8_PENDING_CODEX`. |
| polling | P8 status was checked **twice** in the whole campaign (start, and before the verdict step). No watcher, no waiter, no poll loop. |

---

## 2. Classification of every P9 component

| # | component | class | rationale |
|---|---|---|---|
| 1 | `P9_DEFINITION_AUDIT.md` | `P8_INDEPENDENT` | recovers P9's definition from repository authority; P8's existence is recorded as a status, not used |
| 2 | `CLAIM_LEDGER.{md,json}` P1–P7 + PROJECT rows | `P8_INDEPENDENT` | every row is sourced to a P1–P7 artifact at the anchor commit |
| 3 | `CLAIM_LEDGER` P8 rows (`P8-P1`…`P8-P5`) | `BLOCKED_PENDING_P8` | carried at rank 0, `p9_may_use = NO_UNTIL_CODEX`; no other claim has a premise edge from them |
| 4 | `THEOREM_DEPENDENCY_GRAPH.{md,json}` | `P8_INDEPENDENT` | P8 nodes are leaves; **no** outgoing premise edge from any P8 node exists (test-enforced) |
| 5 | `DEFINITION_CROSSWALK.md` rows X-01…X-08 | `P8_INDEPENDENT` | P1–P7 estimand comparisons only |
| 6 | `DEFINITION_CROSSWALK.md` row X-09 (Stage-D `Gamma_psi` vs P4) | `P8_OPTIONAL` | P8 provisionally reports this gap is definitional; P9 records the row as `UNRESOLVED` **without** P8 and would narrow it to `DIFFERENT_BY_CONVENTION` only if Codex confirms |
| 7 | `DISCREPANCY_REGISTER.md` D-01…D-13 | `P8_INDEPENDENT` | all are P1–P7 tensions |
| 8 | `DISCREPANCY_REGISTER.md` D-14 (SR gain offset, model-class transfer) | `BLOCKED_PENDING_P8` | left `OPEN`; explicitly not resolved by Claude's P8 discovery |
| 9 | `CLAIM_LANGUAGE_POLICY.md` | `P8_INDEPENDENT` | a policy over evidence classes; independent of which claims exist |
| 10 | `CROSS_PRIORITY_REPRODUCTION.md` | `P8_INDEPENDENT` | reproduces P3/P5/P7 anchors with an independent implementation; **no P8 anchor is run** |
| 11 | `MODEL_SCOPE_MAP.md` Gaussian columns | `P8_INDEPENDENT` | P1–P7 evidence |
| 12 | `MODEL_SCOPE_MAP.md` non-Gaussian / heavy-tail / contaminated columns | `P8_REQUIRED` | left `UNKNOWN` except where P4's location-family theorem or Stage-D calibration already speaks; P8 would fill them |
| 13 | `THEORY.md` (`P9-T1` no-inflation theorem) | `P8_INDEPENDENT` | a theorem about the evidence graph; holds for whatever the graph contains |
| 14 | `RESULTS.md`, `STATISTICAL_AUDIT.md` | `P8_INDEPENDENT` | reports P9's own reproduction only |
| 15 | `NOVELTY_AUDIT.md` | `P8_OPTIONAL` | P9's novelty position is conservative and does not improve if P8 survives; P8 could only *narrow* it |
| 16 | `ADVERSARIAL_REVIEW.md` | `P8_INDEPENDENT` | attacks P9's own synthesis |
| 17 | `LIMITATIONS.md`, `CLOSURE_GATES.md` | `P8_INDEPENDENT` | P9-owned |
| 18 | **final `P9 = *_CANDIDATE` verdict** | `P8_REQUIRED` | **withheld**. Prompt §27 forbids issuing it before authoritative P8 reconciliation. |
| 19 | `P8_TO_P9_RECONCILIATION.md` | `BLOCKED_PENDING_P8` | not written; the procedure is preregistered in §4 below |

**Counts:** `P8_INDEPENDENT` 12 · `P8_OPTIONAL` 2 · `P8_REQUIRED` 3 ·
`BLOCKED_PENDING_P8` 3.

---

## 3. The quarantine invariant, stated so it can be tested

> **No claim whose `p9_may_use` is not `NO_UNTIL_CODEX` may have a premise edge
> from a claim whose status is `PROVISIONAL_P8_PENDING_CODEX`.**

This is enforced by `tests/test_p8_quarantine.py`, not by prose. It is the one
invariant that makes the rest of P9 safe to read while P8 is unresolved.

A weaker corollary, also tested: **no P8 node has any outgoing edge at all.**

---

## 4. Preregistered reconciliation procedure (written before the verdict is known)

Freezing this now is the point: it removes P9's discretion to reinterpret P8
favourably after seeing the outcome.

1. Fetch authoritative `main`; record the P8 commit and read
   `p8_model_class_robustness/INDEPENDENT_ADJUDICATION.md`.
2. Write `P8_TO_P9_RECONCILIATION.md` listing, per provisional row `P8-P1`…
   `P8-P5`, the authoritative surviving classification.
3. Replace every `PROVISIONAL_P8_PENDING_CODEX` status with that
   classification, then **re-run** `experiments/build_ledger.py`. Any inflation
   introduced by the promotion is caught by the validator, not by review.
4. Fill `MODEL_SCOPE_MAP.md`'s `P8_REQUIRED` cells **only** from surviving
   claims; leave `UNKNOWN` wherever a gate failed.
5. Re-run only the affected focused tests. Do not re-run the reproduction
   anchors — they contain no P8 input.

**Verdict-conditional rules, fixed in advance:**

| Codex P8 verdict | what P9 does |
|---|---|
| `CLOSED` | use only the explicitly surviving scoped claims. A `CLOSED` P8 still does **not** license a universal model-class statement; the scope map is filled cell by cell. |
| `PARTIAL` | use only explicitly surviving claims. **Failed gates may never be used as positive premises** — a rejected window-separability law is a negative result, not evidence of a weaker law. |
| `FAIL` | quarantine P8 entirely from P9 premises. It may still appear in `LIMITATIONS.md` and `DISCREPANCY_REGISTER.md` as history and as a negative result. |

In all three cases, `P9`'s own conclusions about **P1–P7** are unchanged,
because no P8 premise edge exists. The reconciliation can only add scope, or
add limitations — it cannot retract a P9 finding. That is the design intent of
the quarantine.
