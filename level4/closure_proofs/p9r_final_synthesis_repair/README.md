# Level-4 Priority-9 repair (P9R) — final-synthesis repair

**Status of this namespace: candidate. It is not adjudicated.**

```text
P9_ORIGINAL_VERDICT = PARTIAL          (a3e3cabc30c4508b866736aeede54db17e5e1fcc)
P8_ORIGINAL_VERDICT = FAIL             (5411e2c7c5ff9af2fb983a5b5a48c1e360bca2e8)
P8R_VERDICT         = CLOSED           (dc8516732c2c5672987a6a5a22c1ce023c77f68f)
P9R_VERDICT         = see RESULTS.md   (candidate; Codex adjudicates)
```

P9R exists to repair the defects that the **authoritative independent
adjudication of Priority 9** recorded. It does not rewrite P9 and it does not
convert `P9 = PARTIAL` into `CLOSED` retroactively. The original namespace
`level4/closure_proofs/p9_final_synthesis/` is protected historical evidence;
integrity gate `I2` asserts, against git, that not one of its bytes changed.

## The repair question

> What is the strongest globally defensible ReBaseGuard synthesis after
> repairing P9's theorem-scope inflation, its SR recurrence defect, its missing
> A5/A6 generators, and its claim-ledger dependency semantics?

The target is a **sound** final synthesis hierarchy, not a stronger story. A
narrower exact theorem plus an explicit conditional theorem is the intended
outcome, not a fallback.

## The six defects and where each is repaired

| # | defect found by P9 adjudication | repaired in |
|---|---|---|
| 1 | temporal class `RETROSPECTIVE_SYNTHESIS / TEMPORAL_INTEGRITY_PARTIAL`; gates called "preregistered" were post hoc | `TEMPORAL_ANCHOR.md`, Checkpoint A, gate `I1` |
| 2 | `P9-T2` overclaimed: exact identity plus an unproved strict deficit | `THEORY.md` §2-§3 — split into `P9R-T2a` (exact) and `P9R-T2b` (conditional on `ASM-DOM`) |
| 3 | P7 monotonicity promoted to an exact premise | `claims_source.py` — `P7-A` split into `P7-A-ID` / `P7-A-MONO` / `P7-A-OP`; gate `I9`, rules `V1`/`V10`/`V11` |
| 4 | SR replay shifted by `log 2` on the first update of every cycle | `src/rebaseguard_p9r/detectors.py`, `THEORY.md` §5, `experiments/run_sr_recurrence_check.py`, gate `I5` |
| 5 | `burnin_sensitivity.json` and `p9t2_mixture_check.json` had no supplied generator | `experiments/run_burnin_sensitivity.py`, `experiments/run_response_grid.py`, gate `I6` |
| 6 | claim-ledger inflation (`P7-A`, `P7-D0`, `P9-T2`) and `P3-X1` misclassified `FORMALLY_VERIFIED` | `experiments/claims_source.py`, `experiments/ledger_schema.py`, gates `I7`/`I8`/`I10`/`I11` |

`D-09`, `D-13` and `D-15` are carried forward unresolved and explicitly
classified in `DISCREPANCY_REGISTER.md`. They are not resolved by wording.

## Layout

| path | role | present at Checkpoint A |
|---|---|---|
| `README.md`, `DEFINITION_AUDIT.md`, `REPAIR_RATIONALE.md` | framing | yes |
| `FROZEN_PROTOCOL.md`, `FROZEN_GATES.md` | the frozen protocol and gates | yes |
| `CLAIM_LANGUAGE_FIREWALL.md`, `DISCREPANCY_REGISTER.md` | wording rules, inherited discrepancies | yes |
| `THEORY.md` | lemmas L1-L4, `P9R-T2a`, `P9R-T2b`, `P9R-T3`, the SR algebra | yes |
| `COMMAND_MANIFEST.json` | the exact production commands | yes |
| `SOURCE_MANIFEST.json`, `PROTOCOL_DIGEST.json` | frozen digests | yes |
| `src/`, `experiments/`, `scripts/`, `tests/` | the complete executable surface | yes |
| `results/integrity/protected_tree_manifest_pre.json` | pre-campaign provenance | yes (the only permitted `results/` file) |
| `RESULTS.md`, `REPRODUCTION.md`, `SCOPE_MAP.md`, `LIMITATIONS.md`, `CODEX_HANDOFF.md` | findings | **no** — Checkpoint B |
| `CLAIM_LEDGER.md`, `results/claim_ledger.json`, `results/dependency_graph.json` | generated ledger and graph | **no** — Checkpoint B |
| every other `results/*.json` | production artifacts | **no** — Checkpoint B |

## Reading order for a reviewer

1. `TEMPORAL_ANCHOR.md` — then check it against git, not against its prose.
2. `THEORY.md` §1-§3 — the exact/conditional split and the one missing premise.
3. `THEORY.md` §5 and `results/sr_recurrence_check.json` — the recurrence repair.
4. `REPRODUCTION.md` — corrected reproduction against authoritative P7 cells.
5. `CLAIM_LEDGER.md` and `results/dependency_graph.json` — source-derived, typed.
6. `LIMITATIONS.md` and `CODEX_HANDOFF.md` — what is still open, and how to attack it.
