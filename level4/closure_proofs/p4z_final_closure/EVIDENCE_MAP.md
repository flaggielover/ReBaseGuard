# P4Z final closure — evidence map

Where every load-bearing claim lives. All hashes are in `MANIFEST.json`, derived
from the repository by `build_manifest.py`; the short forms below are for
reading, and the manifest is authoritative.

This packet **stores no result data of its own**. It references immutable
evidence by branch, commit, tree object, file SHA-256 and repository-relative
path. Nothing here is a copy.

---

## 1. Frozen theorem — the thing being closed against

```text
namespace     level4/closure_proofs/p4_theory_generalization
tree object   eede90383da44c250871b1bb97d12045c897c8d9
protocol      configs/P4_PROTOCOL.json   sha256 2afa247e986f7c4f...
modification  NOT PERMITTED
```

The tree object is byte-identical on `main`, `codex/presentation-refresh`,
`p4x-feasibility-audit`, every `p4y-*` branch, `p4zb-skewnormal4-k7`,
`p4zr-rng-provenance-repair` and this branch.

The 96-cell grid is a function of that protocol — 2 layers × 2 detectors × 6
theorem-supported families × 4 values of `m` — so no successor could have added,
removed or redefined a cell without changing a hash-pinned frozen file.

## 2. Historical record — preserved, not reinterpreted

| campaign | outcome | where |
|---|---|---|
| **P4** | `PARTIAL`, immutable | `p4_theory_generalization/results/closure_decision.json` |
| **P4X** | governance failure / non-closure, scientific failures **NONE** | branch `p4x-feasibility-audit` @ `19b00645` |
| **P4Y** | `NOT_FEASIBLE`, no checkpoint frozen, no production run | branches `p4y-prefreeze-pilot`, `p4y-pilot2-final`, `p4y-pilot3-heavy-stage1`, `p4y-pilot4-measurement` |

P4X is **not** rehabilitated as a campaign. Rule C is applied only to its
individual obligations C4 and C5, and only on the narrow grounds in
`gate_discharge.json`.

## 3. The successor line

All three campaigns live on `p4zb-skewnormal4-k7` as a single linear commit
chain. Each freeze commit carries **zero** result-bearing blocks; the blocks
appear only at the following commit.

| stage | freeze | result | self-verdict | authored cells |
|---|---|---|---|---|
| **P4Z** | `e29e32a4` | `298d916c` | `P4Z_NUMERICAL_PASS_AWAITING_FORMAL_OR_GOVERNANCE` | 44 |
| **P4ZA** | `5eb7278a` | `a311e440` | `P4ZA_INCONCLUSIVE` | 48 |
| **P4ZB** | `f06fe61f` | `90e03634` | `P4ZB_CLOSED` | 4 |

These are the campaigns' **own** verdicts, retained verbatim. The independent
integrated adjudication `P4Z = CLOSED` is a separate statement made by this
packet, in `final_closure.json`.

### Result artifacts

| artifact | sha256 (short) |
|---|---|
| `p4z_location_family_feasibility/production/adjudication.json` | `fde940761e40b551` |
| `p4z_location_family_feasibility/results/successor_closure.json` | `bd28a361a6dd744f` |
| `p4z_location_family_feasibility/configs/checkpoint_p4z.json` | `c865b8dafde0908c` |
| `p4z_location_family_feasibility/configs/estimand_contract.json` | `e04f5a6be23e3867` |
| `p4za_fullscope_closure/production/adjudication_p4za.json` | `c0c35ccf93bd30c3` |
| `p4za_fullscope_closure/results/p4za_successor_closure.json` | `f69e3901a450106d` |
| `p4za_fullscope_closure/production/p4za_campaign_plan.json` | `49d9836935160418` |
| `p4zb_skewnormal4_k7/production/adjudication_p4zb.json` | `13ecb684ff264574` |
| `p4zb_skewnormal4_k7/results/p4zb_successor_closure.json` | `be201a980f361096` |
| `p4zb_skewnormal4_k7/results/final_coverage.json` | `a9ad4a8f9b06f355` |
| `p4zb_skewnormal4_k7/production/p4zb_campaign_plan.json` | `1daa03bca38ec4e1` |

### Protected trees

```text
p4_theory_generalization           eede90383da44c250871b1bb97d12045c897c8d9
p4z_location_family_feasibility    4f4f5209ea6b9b15ed8c8e0e3f83355007c00e18
p4za_fullscope_closure             478edf02e28a451ae2ea1d830777e049735c28dd
p4zb_skewnormal4_k7                07a56584955cd5c6a94c1ee8a3cd33f4e3ce0ae8
p4zr_rng_provenance_repair         e01164e3d88dc7891cb1275ca4285748ccc3590b
```

## 4. Gate discharge

| original P4 gate | evidence | Rule C |
|---|---|---|
| `all_theorem_supported_cells_pass` | `p4zb_skewnormal4_k7/results/final_coverage.json`, 96/96 `COVERED_PASS` | no |
| `all_outside_assumption_cells_demonstrate_failure` | P4X obligation **C4**, `new_compute: NONE`, analytic + Arb certificate | yes |
| `gaussian_consistency_with_closed_core` | P4X obligation **C5**, arithmetic over frozen published anchors | yes |

Full per-obligation findings: `gate_discharge.json`.

## 5. Adjudication inputs

### B1 — K7 instrument lineage

| item | where |
|---|---|
| K7 as originally defined | `p4z_location_family_feasibility/configs/checkpoint_p4z.json`, kill gate `K7` |
| why the P4Z form was wrong | `p4za_fullscope_closure/K7_DIAGNOSIS.md` |
| the out-of-sample validation | `p4zb_skewnormal4_k7/SKEWNORMAL4_K7_ASYMPTOTICS.md` |
| the bound that makes it non-blocking | `p4zr_rng_provenance_repair/results/strict_gate_reconstruction.json`, sha256 `f385948a4ff5298d` |

K7 appears **nowhere** in `P4_PROTOCOL.json`. Its limit stayed at `0.02`
throughout; only the statistic it was applied to changed, and each change was
frozen before its own run.

### B2 — RNG provenance repair

```text
branch    p4zr-rng-provenance-repair
commit    9a6215d114b2cf182e5aad88b0ac3bef165b9897
tree      e01164e3d88dc7891cb1275ca4285748ccc3590b
```

| artifact | sha256 (short) |
|---|---|
| `RNG_ADDRESS_SEPARATION.md` | `ea8050ef71b97161` |
| `results/rng_collision_disclosure.json` | `a523c5aabdc667f8` |
| `src/rebaseguard_p4zr/rng_address_audit.py` | see `MANIFEST.json` |

The defective historical scripts are **deliberately preserved unedited** as
evidence of the defect: `p4z_location_family_feasibility/micropilots/run_micropilots.py`,
`.../run_fd_ladder.py`, `p4za_fullscope_closure/audit/calibrate_ladder.py`.

### B3 — Rule C on P4X C4/C5

Source obligations: `p4x_generalization_boundary/production/results/production_results.json`
on branch `p4x-feasibility-audit`. Findings recorded in `gate_discharge.json`.

### B4 — public presentation

```text
branch    codex/presentation-refresh
commit    51742dc72848e3d5fcdb7a4740082cb0969d3787
```

## 6. What is NOT in this packet

- No stored result dataset is duplicated here. The 13 448 block files of the
  successor line stay where they were produced.
- No scientific artifact is modified. This packet is purely additive.
- No new numerical computation. Every number is recomputed from stored
  artifacts by scripts in this namespace or in `p4zr_rng_provenance_repair`.

## 7. Reproducing the packet

```bash
cd level4/closure_proofs/p4z_final_closure
python3 build_manifest.py     # re-derives MANIFEST.json + gate_discharge.json
python3 build_closure.py      # re-derives final_closure.json from the manifest
python3 -m pytest tests/ -q   # consistency, pins, and status-string checks
```

A drifted pin fails the build or the tests rather than silently changing the
record.

### Note on the campaign namespace-lock tests

Each campaign carries a test asserting that nothing outside its own namespace
differs from a fixed base commit — `test_p4z_touches_no_historical_namespace`,
`test_p4za_touches_no_path_outside_its_namespace`,
`test_p4zb_touches_no_path_outside_its_namespace`,
`test_p4zr_touches_no_path_outside_its_own_namespace`.

These are **tip-scoped by construction**. Once any later successor exists, an
earlier campaign's lock necessarily sees the successor's namespace in its base
diff and fails, even though nothing protected was modified. The behaviour is
long-standing: P4Z's lock has failed at the P4ZA tip, and P4ZA's at the P4ZB
tip, since those successors were created.

```text
branch tip              locks failing (cumulative, by construction)
p4zb-skewnormal4-k7     p4z, p4za
p4zr-rng-provenance...  p4z, p4za, p4zb
this packet's tip       p4z, p4za, p4zb, p4zr
```

One further harness detail, recorded because it is latent rather than fixed
upstream: `p4zr_rng_provenance_repair`'s lock slices
`git status --porcelain` at a fixed offset, which mis-parses the first line when
that line is an unstaged modification, because the surrounding helper strips the
output. It never triggers there — that suite runs against a clean tree — but the
same flaw was live in this packet's lock and is fixed here by matching the
status field instead of slicing it
(`tests/test_packet.py::test_the_porcelain_parser_handles_every_status_shape`).

Every lock **passes at its own branch tip**. The substantive property those
tests approximate — that no successor modified a protected artifact — is
verified here directly and independently by tree-object equality
(`tests/test_packet.py::test_protected_trees_match_their_pinned_values` and
`::test_successor_trees_match_their_own_branch_tips`), which is exact rather
than base-diff-scoped. No frozen artifact differs by a single byte.
