# P9 closure gates

**All gates are `P9_ORIGINAL`.** No historical gate was overwritten, weakened,
or reused: the repository contains **no** frozen P9 gate
(`P9_DEFINITION_AUDIT.md` §6 `C3`).

**Disclosure.** These gates were written **after** the reproduction anchors ran
(`EXPERIMENT_PROTOCOL.md` §0). They are therefore deliberately restricted to
**properties an adjudicator can verify by inspecting the artifacts**, not
numerical thresholds P9 could have tuned to its own results. A post-hoc
numerical gate would be worthless here, so none is written.

| # | gate | type | how it is checked | result |
|---|---|---|---|---|
| G1 | The P9 definition audit is derived from a reproducible repository search, and reports the `P9`-as-priority hit count literally | correctness | `P9_DEFINITION_AUDIT.md` §1 commands re-run | **PASS** (0 hits) |
| G2 | `CLAIM_LEDGER.json` validates: unique ids, statuses drawn only from the declared vocabulary, all parents resolvable | schema | `tests/test_claim_ledger.py` | **PASS** |
| G3 | The claim graph is acyclic over **all** edge types | correctness | `tests/test_dependency_graph.py` | **PASS** (0 cycles) |
| G4 | No claim exceeds the weakest rank among its **premise** parents (`P9-T1`) | correctness | `tests/test_dependency_graph.py` | **PASS** (0 violations) |
| G5 | No non-P8 claim has a premise edge from a `PROVISIONAL_P8_PENDING_CODEX` claim; no P8 node has any outgoing edge | quarantine | `tests/test_p8_quarantine.py` | **PASS** |
| G6 | Every P4/P5/P6 claim is carried at a status consistent with its priority being `PARTIAL` — no P4/P5/P6 claim is presented as closure | correctness | `tests/test_partial_priorities.py` | **PASS** |
| G7 | `CLAIM_LEDGER.md`, `THEOREM_DEPENDENCY_GRAPH.md` and the two JSON files are byte-consistent with a fresh run of the generator | consistency | `tests/test_generator_consistency.py` | **PASS** |
| G8 | Reproduction anchors A1–A3 meet the tolerances **hard-coded before execution** (`1e-9`, `1e-12`, exact) | reproduction | `tests/test_reproduction_anchors.py` against `results/reproduction_anchors.json` | **PASS** |
| G9 | Every `OPEN` / `CONTRADICTION` discrepancy in `DISCREPANCY_REGISTER.md` is also surfaced in `LIMITATIONS.md` | honesty | `tests/test_document_consistency.py` | **PASS** |
| G10 | Every status in the ledger's vocabulary has a row in `CLAIM_LANGUAGE_POLICY.md` §1 | honesty | `tests/test_document_consistency.py` | **PASS** |
| G11 | No protected file (2217 at the anchor) deviates except where the **authoritative** `ffe23a6..HEAD` P8 integration touched it — sole deviation `README.md`, Codex's own commit | integrity | `tests/test_protected_scope.py` | **PASS** |
| G12 | All P9 writes are confined to `level4/closure_proofs/p9_final_synthesis/`; no tracked file is modified | integrity | `tests/test_protected_scope.py` (`git status`, `git diff HEAD`) | **PASS** |
| G13 | `MODEL_SCOPE_MAP.md` contains no filled non-Gaussian cell that depends on P8 | quarantine | inspection + `tests/test_document_consistency.py` | **PASS** |
| G14 | **Authoritative P8 reconciliation has occurred** and `P8_TO_P9_RECONCILIATION.md` exists | dependency | `p8/INDEPENDENT_ADJUDICATION.md` present and read; `P8 = FAIL` applied under the rule pre-committed in `P8_DEPENDENCY_GATE.md` §4 | **PASS** |

## Verdict rule, fixed here

* `P9 = CLOSED_CANDIDATE` iff **every** gate `G1`–`G14` passes.
* `P9 = PARTIAL_CANDIDATE` iff `G1`–`G13` pass and only `G14` is unmet.
* `P9 = FAIL_CANDIDATE` if any of `G1`–`G13` fails.

**Current state: `G1`–`G14` PASS (14/14).**

The authoritative verdict `P8 = FAIL` arrived during the campaign and was
reconciled under the rule pre-committed in `P8_DEPENDENCY_GATE.md` §4
(`P8_TO_P9_RECONCILIATION.md`). Because P9 held **no** P8 premise, no P9
conclusion changed; the reconciliation removed 6 graph edges and withdrew one
provisional row.

The verdict rule above was fixed **before** the P8 outcome was known and has not
been adjusted since.
