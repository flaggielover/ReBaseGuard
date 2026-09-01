# P9 → Codex handoff

Written so P9 can be adjudicated **without trusting Claude**. Every number below
is recomputable from the commands in §10.

```text
CLAUDE_SIDE_VERDICT   = P9 = CLOSED_CANDIDATE
GATES                 = 14 PASS / 0 FAIL
FOCUSED_TESTS         = 37 passed
PROTECTED_TREE        = 2217 files; sole deviation is Codex's own
                        authoritative P8 integration commit (README.md)
P8_RECONCILIATION     = DONE (authoritative P8 = FAIL applied)
NOVELTY               = NOT_ESTABLISHED (no new search run)
OPEN_DISCREPANCIES    = 3
```

---

## 1. The exact P9 question — and the fact that nothing froze it

**There is no frozen P9 question.** At the anchor commit
`ffe23a63181e2ff11380768d3c73980de80f94fb`, the repository contained **zero**
statements defining, scoping, naming or assigning deliverables to a Level-4
Priority 9. All 11 `\bP9\b` hits are P5's *premise* label for `m`-monotonicity.

This is the first thing to attack, and P9 says so itself
(`ADVERSARIAL_REVIEW.md` A12, `LIMITATIONS.md` §1). The question P9 actually
answered, from the prompt's §3 fallback:

> What is the strongest globally defensible ReBaseGuard story after P1–P8 —
> what is exactly proved, what is conditional, what is certified, what is
> empirical, what was falsified, and what cannot be generalized?

During the campaign the authoritative `p8/INDEPENDENT_ADJUDICATION.md` §16
("Exact P9 handoff boundary") appeared. It constrains one *input* and is
honoured in full; it does not define P9's question.

## 2. Final claim ledger

`CLAIM_LEDGER.md` / `.json` — **65 claims, 64 typed edges, 0 validation
findings, 0 cycles, 0 inflation violations.**

| status | n |
|---|---:|
| `EXACT_THEOREM` | 16 |
| `CONDITIONAL_THEOREM` | 9 |
| `FORMALLY_VERIFIED` | 3 |
| `CERTIFIED_NUMERICAL` | 3 |
| `EMPIRICAL_REPRODUCED` | 9 |
| `EMPIRICAL_ONLY` | 7 |
| `NEGATIVE_RESULT` | 11 |
| `NOT_ESTABLISHED` | 5 |
| `PARTIAL_PRIORITY_RESULT` | 2 |

## 3. Strongest theorem — `P9-T2`

> For each frozen detector and each `m >= 1`: at `rho = 0` the invariant law is
> exactly `N(0,1/m)`, the stationary in-control ARL equals `E[A(e)]`, and that
> is **strictly** less than `A(0)`. Since `rho = 0` lies strictly below `rho_c`
> for every supported `(D,m)` — and is where the local map is *maximally*
> stable — **no threshold in `rho` is an operational safety boundary.**

**Assumptions:** frozen two-sided CUSUM (`k=1/2, h=5`) or frozen symmetric
two-chart SR (`A = 520.886133602749`); `A` even and non-increasing in `|e|`
(`P7-A`); `A(0) > 1` and `A(e) -> 1` as `|e| -> inf`, both **proved** from the
frozen recurrences rather than assumed.

**Premises:** `P5-T1`, `P5-T7`, `P7-A` — all `EXACT_THEOREM`. **No new premise.**

**What it does not say:** nothing about the *size* of degradation, nothing about
`rho > 0`, nothing outside the two frozen Gaussian detectors, and **not** that
`rho_c` is meaningless — `P3-T1` remains exact.

## 4. Strongest conditional theorem carried

`P4-T1` (location-family derivative under (A1)–(A7)), carried at
`CONDITIONAL_THEOREM` inside a `PARTIAL` priority, with `P4-T2` in narrowed
form only — **not** an iff characterisation.

## 5. Strongest certified result carried

`CORE-C2`: Arb certifies `Gamma_SR in [5.800391799508442, 28.781285803081492]`,
lower endpoint exceeding two by `3.800391799508442`. **P8 created no certified
result.**

## 6. Strongest empirical result

`P7-E1`, independently reproduced by P9: fresh `rho=0` ARL `78.84–162.11`
against a published `79.91–162.03`; **cycle-2 collapse `5.63–8.83` against a
published `5.6–9.4`**.

## 7. Exact negative results

* `P7-R1` — `rho_c` is a local mathematical boundary only.
* `P7-R2` — crossing hypothesis rejected: 0/4 metrics peaked, 4/4 monotone in `log m`.
* `P4-F1/F2/F3`, `P5-F1` — literal frozen gate failures, not weakened.
* `P8-S4` — cross-family window-separability law and both sub-gates **rejected**;
  literal `G7` fails; **detector transfer measured absent**.
* `P8-V` — **`P8 = FAIL`** on temporal integrity (`G14`).
* `PROJ-L4R11` — the mandatory `m`–`rho` phase map was never run.

## 8. Unresolved discrepancies (3)

* **`D-09`** — `final_level4_closure` records the campaign `CLOSED` while
  `LEVEL_4_CURRENT_LEDGER.md:19` keeps `L4R-11` a MANDATORY `FAIL`. Governance,
  not science; not P9's to close.
* **`D-13`** — `P5-T11`'s map-vs-chain `ACF1` agrees to `<= 3.5%` but **up to 16
  chain SE**; attack `A13` was "overturned as unresolved".
* **`D-15`** — P3's grid preregistration cannot be independently authenticated.

## 9. P8 reconciliation

Authoritative `P8 = FAIL`. Claude's `PARTIAL_CANDIDATE` did **not** survive:
`G14` (temporal integrity) failed in addition to the four scientific gates.

P9 held **no** P8 premise, so **no P9 conclusion changed**; reconciliation
removed 6 edges and withdrew one row (`P8-P5`, the "factor-3.35 gap is
definitional" claim, which §16 does not list — `DEFINITION_CROSSWALK.md` X-09
therefore stays `UNRESOLVED`). §16 *permits* four tiers; **P9 declines**, keeping
the stricter rule pre-committed in `P8_DEPENDENCY_GATE.md` §4.
Enforced: `tests/test_p8_quarantine.py` asserts no P8 node has any outgoing edge.

## 10. Exact replay commands

```bash
git worktree list   # expect /Users/suzhe/ReBaseGuard-p9 on branch p9-research
```

The P9 worktree was fast-forwarded onto authoritative main `5411e2c`
("adjudicate Level-4 Priority 8 model-class robustness as failed") **after** the
reconciliation, so P9 is reviewable against current main. `p9-research` carries
**no commits of its own**; the namespace is left untracked for review.

```bash
cd /Users/suzhe/ReBaseGuard-p9/level4/closure_proofs/p9_final_synthesis && P9_EMIT_MD=1 python3 experiments/build_ledger.py
```

```bash
cd /Users/suzhe/ReBaseGuard-p9/level4/closure_proofs/p9_final_synthesis && python3 -m pytest tests/ -q
```

```bash
cd /Users/suzhe/ReBaseGuard-p9/level4/closure_proofs/p9_final_synthesis && /Users/suzhe/ReBaseGuard/level4/.venv/bin/python experiments/reproduce_anchors.py
```

The last command takes several minutes and rewrites
`results/reproduction_anchors.json`. Anchors A1–A3 are deterministic given the
derived seeds; A4 is Monte Carlo and will move within its reported SEs.

To re-verify the definition finding:

```bash
grep -rIn --exclude-dir=.git --exclude-dir=.pytest_cache -E "Priority 9|PRIORITY 9|priority_9|priority9" . | wc -l
```

## 11. High-risk artifacts — attack these first

| artifact | why it is high risk |
|---|---|
| `CLAIM_LEDGER.json` | it is **one agent's reading** of the adjudication records. A different reader could tier a borderline claim differently. Every row carries a `source` so disagreement can be localised — check `P4-T2`, `P5-T10`, `P6-T6C`, `P7-B`. |
| `THEORY.md` §2.2 | `P9-T2`'s strictness argument. If `A(e) -> 1` fails for SR under some reachable state, strictness weakens. |
| `THEOREM_DEPENDENCY_GRAPH.json` edge types | retyping any `verifies` edge to `premise` changes the bound. The three `verifies` edges on `P1-L1`, `CORE-C1/C2`, `P4-C1`, `P4-L1` are the load-bearing ones. |
| `CLOSURE_GATES.md` | written **after** the reproductions ran (`EXPERIMENT_PROTOCOL.md` §0). Judge whether the restriction to inspection-verifiable properties is an adequate response. |
| `results/reproduction_anchors.json` | A4's SEs are across-path on per-path cycle means. If pooled-cycle SEs were used instead they would be too small. |
| `P6-F1` | P6's closure rests on the root `README.md` status table; the P6 namespace's own last record still says `PARTIAL`. |
| `tests/test_protected_scope.py` | it *permits* deviations attributable to the authoritative `ffe23a6..HEAD` range. Confirm that permission is not laundering a P9 write — the only deviation is `README.md`, which is Codex's own commit. |

## 12. Recommended independent attacks, in priority order

1. **Temporal integrity.** P8 died on exactly this. P9's gates postdate its
   experiments and P9 discloses it — verify the disclosure is complete, and that
   the A1–A3 tolerances really were in `reproduce_anchors.py` before it ran.
2. **Claim-class inflation.** Re-run the validator with all edges forced to
   `premise` and confirm P9's claim that the graph is then unsound. Then judge
   whether the `verifies` type is a legitimate distinction or an escape hatch.
3. **Partial-premise propagation.** Trace every path from `P4-*` / `P5-N*` to any
   P9 sentence. `P9-T2` should touch none.
4. **Cross-priority estimand mismatch.** Check `DEFINITION_CROSSWALK.md` X-02
   (local `GammaTilde` vs stationary `Gamma_eff`) and X-05 (three ARLs) against
   the sources; these are where a wrong chain would be invisible.
5. **P8 reconciliation.** Confirm no P8 premise leaked in, and that P9's refusal
   of §16's permission is consistent rather than selective.
6. **The `D-13` SR/ACF1 residual.** P9 left it `OPEN`. Judge whether that is
   correct or whether P9 should have attacked it.
7. **Local-vs-operational conflation.** `P9-T2` is the sharpest claim P9 makes.
   Attack the claim that it "upgrades" `P7-R1` rather than restating it.
8. **Novelty overstatement.** P9 ran no search and claims nothing. Verify it
   nowhere implies novelty by omission.
9. **Protected-tree integrity.** 2217 files; confirm P9 wrote only inside its
   own namespace and did not disturb the concurrent P8 work in `main`.

## 13. What P9 asks you not to conclude on its behalf

P9 does **not** claim Level-4 is closed, does not adjudicate any other
priority, and does not claim novelty for itself or the project. Its
`CLOSED_CANDIDATE` is a statement about **its own 14 gates only**, and the
strongest objection to it — that P9 was never a frozen priority — is recorded by
P9 itself as `OPEN`.
