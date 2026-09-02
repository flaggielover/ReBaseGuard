# P9R frozen gates

Frozen at Checkpoint A and hashed into `PROTOCOL_DIGEST.json`.

The integrity gates `I1`-`I15` test **repair integrity**, not desired
scientific outcomes. The scientific gates `S1`-`S5` have several admissible
outcomes on purpose: a conditional or negative resolution is a pass, because the
whole point of the repair is that the honest answer is allowed to be the weaker
one.

`scripts/audit_integrity.py` computes every gate mechanically and writes
`results/integrity/gate_report.json`.

## Integrity gates (all mandatory)

| id | gate | pass condition |
|---|---|---|
| `I1` | temporal anchor valid | the anchor commit exists, is an ancestor of `HEAD`, contains the protocol, gates, source, generators and claim schema, and contains **no** `results/` file other than `results/integrity/protected_tree_manifest_pre.json` |
| `I2` | original P9 immutable | `git diff a3e3cab HEAD -- level4/closure_proofs/p9_final_synthesis` is empty, and the tree hash of that path at `HEAD` equals its tree hash at `a3e3cab` |
| `I3` | source digest locked | every path in `SOURCE_MANIFEST.json` is byte-identical to the anchor commit |
| `I4` | protocol and gates locked | every path in `PROTOCOL_DIGEST.json` is byte-identical to the anchor commit |
| `I5` | correct frozen SR recurrence | `results/sr_recurrence_check.json` reports `all_pass = true`, including the exact `log 2` first-step shift witness and the differing alarm decision |
| `I6` | A5/A6 generator completeness | every file under `results/` carries a `generator` that exists in `SOURCE_MANIFEST.json`, an `argv`, a `git_commit`, an `environment`, a `config` and a `payload_sha256` matching its payload |
| `I7` | claim ledger source-derived | every ledger row cites an existing path and a section; rule `V8` reports no violation |
| `I8` | claim-class firewall passes | rules `V1`-`V5`, `V11`, `V14` report no violation |
| `I9` | dependency graph makes the monotonicity premise explicit | rule `V10` passes: `ASM-DOM` exists, `P9R-T2b` reaches it by an `ASSUMPTION` edge, and no `EXACT_THEOREM` takes `ASM-DOM` or `ASM-MONO` as a premise |
| `I10` | `P3-X1` classification repaired | rule `V12` passes: `P3-X1` is not `FORMALLY_VERIFIED` |
| `I11` | `P7-A` / `P7-D0` split correctly | `P7-A-ID` and `P7-D0-ID` are `EXACT_THEOREM`, `P7-A-MONO` is `NOT_ESTABLISHED`, `P7-A-OP` is `EMPIRICAL_ONLY`, `P7-D0-DEF` is `CONDITIONAL_THEOREM` |
| `I12` | P8 / P8R reconciliation correct | rule `V13` passes; and no premise or assumption path from `P9R-T2a` or `P9R-T2b` reaches any `P8` or `P8R` node |
| `I13` | no hidden novelty inflation | rule `V14` passes and `NOVELTY_STATUS = NOT_ESTABLISHED` in `RESULTS.md` |
| `I14` | protected tree pass | every tracked file outside the P9R namespace is byte-identical to the pre-campaign manifest, except root status files explicitly authorised in `RESULTS.md` |
| `I15` | focused tests pass | `tests/` runs green |

## Scientific gates (multi-outcome by design)

| id | question | admissible outcomes |
|---|---|---|
| `S1` | is the `rho=0` invariant-law / mixture identity exact? | `EXACT` / `NOT_EXACT` |
| `S2` | is the strict stationary ARL deficit exact, conditional, or false? | `EXACT` / `CONDITIONAL` / `FALSE` / `UNKNOWN` |
| `S3` | what is the status of global monotonicity of `A`? | `PROVED` / `EMPIRICALLY_SUPPORTED` / `NOT_ESTABLISHED` / `FALSE` |
| `S4` | does the corrected reproduction agree with authoritative P7? | `MC_CONSISTENT` / `MC_TENSION` / `MC_DISAGREEMENT`, per detector |
| `S5` | does the `log 2` SR defect materially change P9's SR values? | `MATERIAL` / `IMMATERIAL`, with the paired difference reported |

A `CONDITIONAL` `S2` together with `EMPIRICALLY_SUPPORTED` or `NOT_ESTABLISHED`
`S3` is an **expected and passing** outcome. Requiring `S3 = PROVED` would
recreate the pressure that produced the P9 defect, so no gate requires it.

## Verdict rule

`CLOSED_CANDIDATE` requires `I1`-`I15` all `PASS` and every scientific gate
resolved to one of its admissible outcomes with the resulting language obeying
`CLAIM_LANGUAGE_FIREWALL.md`.

Any mandatory `I` gate failing forces at most `PARTIAL_CANDIDATE`; `I1`, `I2` or
`I5` failing forces `FAIL_CANDIDATE`.
