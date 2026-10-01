# FC2(b): the band-scoped verifier variant

This directory holds the band-scoped variant of the independent SRK verifier and its qualification. They were written
by the independent verifier's author from `fc2/FC2_SPEC_R2.md` (protocol rev. 2b §7(b); owner rulings 2) and the
committed brief `reviews/BRIEF_FC2_VERIFIER_VARIANT_AUTHOR.md`.

**This work writes and tests the admission mechanism only.** It issues no grant and lifts no quarantine. No production
marker and no production grant was created anywhere, and no REAL-band quantity was computed. NEW Γ309 TARGET
EVALUATIONS = 0.

## Identities (sha256)

| file | sha256 |
|---|---|
| `verify/srk_verify_indep_scoped.py` (the variant; its `verifier_id` is `sha256:` + this) | `9d9f8cec52cfd49ab146a45c44e03fde493614f81551af584317ab7d3545498f` |
| `verify/run_verify_all_scoped.py` (I1 harness) | `45902e30cb59db718c2a133fa321e30ee183a3fa18781c3698a11ce7f48b90d8` |
| `verify/scoped_sandbox.py` (sandbox helper, light sandboxes per erratum E1-6) | `6faef6168f1f8fa6337545c710a7003a35e975b6c62829ebeae5d830d51db097` |
| `tests/test_verify_scoped.py` (21 ported self-tests plus D1, N1–N13, P1, P2) | `1483d6c2f5c9d8d3a469915fe6ab85d0cb27f3abdfcac53b168ff6754a64a10c` |
| original verifier `RNS/verify/srk_verify_indep.py` (unchanged) | `a32d5d397893a1fc698d3609f59cb65aab3bc4fe1445c51c676fd9ad54652333` |

Superseded identities (commit 6522db10, before erratum 1):
* variant `52c84ec22c4396d07019cf1f783355c014f258d1d0611fc522562b0104d2b278`;
* harness `e27dba41c1c61d5d771d383c2951602509e212e0832540c55a1a8dccd4c09430`;
* tests `e17c01566ee1f08b18515ee40f94e5ca4e691088bdfee41a56f2675662aae8c8`.

Superseded by follow-up 2 (the erratum-1 state):
* harness `2dc92f5697a52e71ec05fe047b51267258f5975ba61dc34f3f17a3f596605d76`;
* sandbox helper `71458b156a8d9418f229e84ff017a258ee8b37e5f0aa888c6df9fcfea70a9a00`.

## Follow-up 2 (review R4 NB3, NB12, NB9; `reviews/BRIEF_FC2_VERIFIER_VARIANT_AUTHOR_FOLLOWUP_2.md`)

The variant and the tests are unchanged, and no admission rule or review-mode behaviour changed.
* **NB3, harness (4 lines).** The prepare-tripwire classifies certificates with the harness's **own** band table
  (`own_bands`), not with the variant's `cert.bands`. Behaviour on every current input is unchanged (see below).
* **NB12, sandbox helper.** Sandboxes are now light (erratum E1-6):
  * `git init`, a read-only `objects/info/alternates` link to this repository's object store, and a copy of its
    `shallow` file;
  * branch `refs/heads/fc2-sandbox` at this repository's HEAD commit, `gc.auto` 0 in the sandbox's own config, and
    no remote.

  The own ref checks, the refusal of any production-namespace ref, the path guards and the teardown are unchanged.
  A sandbox is now about 2 MB and builds in under 0.5 s, instead of about 445 MB and 14 s. Peak sandbox disk use
  during the full re-run was 2 MB, sampled every second. This repository's object store was verified unchanged
  (`count-objects`) around a light-sandbox build.
* **NB9, README.** §9 now states the shared top-level session.
* **Re-run.** The re-run wrote to the scratchpad with `--out` (37 tests plus I1). Its counts are identical to the
  previous run, and all 2369 genuine and mutant entries have identical verdict, reason and rule. The committed
  `verify/VERIFY_RESULTS_SCOPED.json` was then refreshed from that run.

## Erratum 1 (`fc2/FC2_SPEC_R2_ERRATUM_1.md`; follow-up brief 1)

The only changes against commit 6522db10 are these; nothing else changed.
* **E1-1, variant (2 lines).** Official-mode check 7 now uses the **strict-descendant** reading. A ref pointing at the
  grant commit itself is allowed, for example the remote-tracking ref after the grant commit is pushed and fetched.
  Only refs at a commit that has the grant commit as a **proper** ancestor, other than the marker and the current
  branch, are refused. This corrects a real defect: under the old reading, the production remote-tracking ref would
  have made every in-band certificate REFUSE.
* **E1-1, test N7 (5 lines).** A ref at G itself must ADMIT when everything else is valid, and a ref at a child of G
  must REFUSE ("strict descendant").
* **E1-5, harness (5 lines).** `--out PATH` was added. The default stays `verify/VERIFY_RESULTS_SCOPED.json`.
* **E1-2 to E1-4** record documented differences from the guard that need no code change:
  * NOT_BANDED versus ADMIT "meets no band";
  * exact grant geometry strings;
  * `frozen_commit` a proper ancestor.

`verify/VERIFY_RESULTS_SCOPED.json` records the variant and harness sha of the run, the expectation rule, both I1
passes and the unit-test outcomes.

## What changed against the original verifier (diff summary)

`diff -u` against the original: 510 lines added (441 of them non-blank; the earlier 441 counted non-blank lines only) and 14 removed, in 9 hunks. Erratum 1 changed 2 of these lines in place.
* **Module docstring:** a new header describing the variant. The original documentation is kept below it.
* **Imports:** `datetime`, `platform`, `socket`, `subprocess` and `types`.
* **Compiled band tables (§1):**
  * `REAL_BAND` [6/5, 13/5] + mirror, which now applies to **every** geometry (the original checked only (5, 1/2));
  * `TEST_BAND` [341/1024, 201/512] + mirror, for geometry (3, 1/2);
  * `QUARANTINE_BANDS` kept as an alias of `REAL_BAND`.
* **Admission block (new, §§2–3):**
  * the constants: `PRODUCTION_MARKER` (the single occurrence of the literal, scanner allowance §7), `TEST_MARKER`, and
    the production and test field tables;
  * `bands_met`, the `PRODUCTION` singleton, `TestContext(sandbox_root)` and `TestContextRefused`;
  * grant validation (check 2), the outward 2⁻¹⁰ hull (check 3), grant-commit analysis (4), frozen identity (5), own
    identity (6), marker binding (7; strict-descendant reading per erratum E1-1), expiry (8), host and runtime (9), the
    item inside Ew (10), and review mode;
  * `admission_decision(item, *, ctx=PRODUCTION, mode="official")`.
  * **Fail closed:** any exception is returned as REFUSE. The git calls are read-only: `show`, `log`, `rev-parse`,
    `diff-tree`, `merge-base`, `for-each-ref`, `symbolic-ref`, `rev-list`, `cat-file`.
* **`Cert`:** records `bands` and `sha256`; `quarantined` means "meets a band".
* **`verify_cert`:** gains keyword-only `ctx=PRODUCTION, mode="official"`. A band-meeting certificate is refused with
  the admission reason (nothing evaluated) unless it is admitted; an admitted one is verified by the unchanged
  mathematics.
* **CLI:** `--mode` and `--test-sandbox`.
* **Unchanged:** every mathematical routine (enclosures, kernel closed form, Taylor models, κ̄, cover, disproof,
  driver).

## Results

### Self-tests and N/P/D tests (run first)

After follow-up 2: `37` tests, **all pass** (100 s), recorded by the I1
invocation. Each FC2 test builds and tears down its own light sandbox under `…/scratchpad/fc2_sandbox_verifier/`
(`git init` plus a read-only alternates link and the `shallow` file; no remote; never pushed; erratum E1-6). Only the TEST marker
`refs/p309-test/TEST_ONLY_DO_NOT_EXECUTE_P309_MARKER` is ever created. A tripwire on the variant's `prepare` fails the
run if a REAL-band certificate, of any geometry, or a TEST-band certificate outside an admitting test, reaches
evaluation.

| test | result |
|---|---|
| `TestFC2Scoped.test_D1_real_band_production_context_dry` | pass |
| `TestFC2Scoped.test_N01_no_grant` | pass |
| `TestFC2Scoped.test_N02_malformed_grant` | pass |
| `TestFC2Scoped.test_N03_wrong_cell` | pass |
| `TestFC2Scoped.test_N04_wrong_Ew` | pass |
| `TestFC2Scoped.test_N05_wrong_verifier_id` | pass |
| `TestFC2Scoped.test_N06_wrong_frozen_identity` | pass |
| `TestFC2Scoped.test_N07_marker_and_grant_commit` | pass |
| `TestFC2Scoped.test_N08_wrong_host_or_runtime` | pass |
| `TestFC2Scoped.test_N09_test_authorization_cannot_admit_real_band` | pass |
| `TestFC2Scoped.test_N10_production_cannot_be_synthesized` | pass |
| `TestFC2Scoped.test_N11_synthetic_marker_not_production` | pass |
| `TestFC2Scoped.test_N12_review_mode_refusals` | pass |
| `TestFC2Scoped.test_N13_fail_closed` | pass |
| `TestFC2Scoped.test_P1_test_band_positive_path` | pass |
| `TestFC2Scoped.test_P2_review_mode_listed_subset` | pass |
| `TestGaussianEnclosures.test_G_value_vs_quadrature` | pass |
| `TestGaussianEnclosures.test_Phi_monotone_consistent` | pass |
| `TestGaussianEnclosures.test_absHephi_bounds_contain_samples` | pass |
| `TestGaussianEnclosures.test_he_roots` | pass |
| `TestGaussianEnclosures.test_phi_Phi_contain_math` | pass |
| `TestGaussianEnclosures.test_pi` | pass |
| `TestKernelClosedForm.test_closed_form_vs_quadrature` | pass |
| `TestRequiredRejections.test_0_genuine_accepted` | pass |
| `TestRequiredRejections.test_0b_taboo_positive_control` | pass |
| `TestRequiredRejections.test_1_gamma` | pass |
| `TestRequiredRejections.test_2_scaled_V0` | pass |
| `TestRequiredRejections.test_3_drop_lambda` | pass |
| `TestRequiredRejections.test_4_widened_block` | pass |
| `TestRequiredRejections.test_5_hermite_plus_one` | pass |
| `TestRequiredRejections.test_6_sha` | pass |
| `TestRequiredRejections.test_7_malformed` | pass |
| `TestRequiredRejections.test_7_non_dyadic_drift_no_crash` | pass |
| `TestRequiredRejections.test_quarantine_refused` | pass |
| `TestRequiredRejections.test_weight_block_is_used` | pass |
| `TestTaylorModels.test_containment` | pass |
| `TestTaylorModels.test_lower_bound_below_samples` | pass |

The FC2 tests check the following. REAL-band items are dry throughout.
* **D1:** a REAL-band item with the production context is refused with "no grant". So is a verify_cert on an h5 decoy
  moved into the band.
* **N1:** no grant is refused, in both contexts.
* **N2:** a malformed grant is refused: invalid JSON, a missing field, a wrong type, an unknown schema, Ew lo ≥ hi, a
  non-rational.
* **N3:** a wrong cell is refused: another string, an int, a list.
* **N4:** a wrong Ew is refused: block outside Ew; weight block ≠ Ew; Ew not the outward hull.
* **N5:** a wrong verifier_id is refused.
* **N6:** a wrong frozen identity is refused: manifest sha; frozen_commit not an ancestor; own file missing from the
  manifest, or pinned with another sha.
* **N7:** each of these is refused:
  * the marker absent, or pointing elsewhere;
  * an extra ref in the namespace;
  * another ref at a **strict** descendant of the grant commit. Per erratum E1-1, a ref at the grant commit itself is
    ADMITted when everything else is valid;
  * HEAD ≠ the grant commit;
  * a grant commit touching another file;
  * two commits adding the grant;
  * an expired grant.
* **N8:** a wrong host or a wrong runtime is refused.
* **N9:** a valid test context cannot admit REAL-band items, whether (5, 1/2), (3, 1/2) or an interval.
* **N10:** a production-shaped file at the TEST grant path is refused with the production and with the test context;
  a REAL-band item under a test context is refused. `TestContext` raises when pointed at this repository or at a
  worktree of it.
* **N11:** the TEST marker at the production-shaped commit is refused in both contexts, including a production call
  while the only marker anywhere is the TEST marker.
* **N12:** review-mode refusals: an unlisted sha, a seal parent ≠ G, a two-parent seal, a seal touching another file,
  a result changed after the seal, an interval.
* **N13:** fail-closed: simulated unreadable git in both contexts, and a missing `.git/HEAD`.
* **P1:** all 16 committed h3 decoy-cell certificates are ADMITted under a valid sandbox test context, then verified
  **identically** to the committed results (verdict, reason and cell count).
* **P2:** in review mode a seal lists 2 of 4 shas: the listed ones are ADMITted (one is fully verified, identical to
  the committed result); the unlisted ones are refused, and official mode is then refused.

### I1: identity outside every band

The expectation rule was recorded before the run: in the harness docstring, in `VERIFY_RESULTS_SCOPED.json`
(`expectation_rule`) and in the pre-run ledger line.
* **R0:** a non-parsing object gives the committed result.
* **R1:** an object meeting no band (harness's own compiled table) gives a result identical in verdict and reason to
  the committed result.
* **R2:** an object meeting a band gets an admission prediction made independently of the variant. The prediction is
  ADMIT iff all of these hold:
  * the pass is the test-context pass;
  * the geometry is (3, 1/2);
  * TEST is the only band met;
  * the block lies inside Ew;
  * the weight block equals Ew.

  Predicted ADMIT means identical to the committed result. Otherwise the object must be REFUSEd with a "quarantine:"
  reason and nothing evaluated.

Wherever the committed result is the expectation, the probe's harness-v2 reason-specific check must also hold.

The run covered every certificate in `RNS/evidence/srk_decoys/` and `RNS/evidence/srk_decoys_cell/`: genuine, plus the
v2 batteries, plus probe 7r (a geometry-blind REAL-band parse-time refusal for non-(5, 1/2) geometries). It used 3 processes and took 492 s (re-run after follow-up 2).

| pass | certificates | genuine: expectation met / identical | mutants | mutants: expectation met / identical |
|---|---|---|---|---|
| production (no grant) | 87 | 87 / 71 | 1914 | 1914 / 1595 |
| test context (P1 sandbox) | 16 | 16 / 16 | 352 | 352 / 240 |

**Every expectation is met, and every non-identical result is an R2 refusal the rule predicts.**
* **Production pass.** Everything outside every band is identical in verdict and reason, and the R0 and R1 items are
  all identical. The non-identical results are:
  * the 16 h3 decoy-cell certificates, and their TEST-band mutants: REFUSE, TEST band without a test context;
  * the h3 whole-kernel mutants whose widened block reaches the TEST band: 5× 4L,
    5× 4R and 10× 4B, each also with Gamma recomputed.
    These are REFUSE, with nothing evaluated;
  * 41× 7q: REFUSE as committed, with the reason now the admission reason (…"no
    grant"…), as §4 prescribes;
  * 46× 7r (new, no committed counterpart): REFUSE.

  Per mutant type, the differences are: {'1_gamma_minus_1e-6': 16, '2_V0_scaled_1-2^-8': 16, '2x_V0_scaled_3/4': 16, '3_V0_minus_lam_W0': 16, '4B_block_widened_1/8': 26, '4B_block_widened_1/8+Gamma_recomputed': 26, '4L_block_widened_1/8': 21, '4L_block_widened_1/8+Gamma_recomputed': 21, '4R_block_widened_1/8': 21, '4R_block_widened_1/8+Gamma_recomputed': 21, '5_hermite_index_plus_1': 16, '6_sha256_altered': 16, '7q_quarantine_band_refused': 41, '7r_real_band_geometry_blind': 46, 'genuine': 16}.
* **Test-context pass.** All 16 genuine results are identical to the committed results (ADMIT, then the same verdict
  and reason). So are all R2-admit mutants (1, 2, 2x, 3, 5, 6), all R0 (item-7 malformed) and all R1 (7h) results. The
  only non-identical results are the widened blocks, whose block is no longer inside Ew (6 kinds × 16 = 96, REFUSE),
  and 7r (16, REFUSE).

### Formal scan

`code/p309_scan.py` gives PASS. The variant's single `PRODUCTION_MARKER` finding is allowed under
`config/SCANNER_ALLOWANCE_P309.json`, conditions (a)–(e). My files have no other finding; their CELL/BAND literals
carry `q309: literal-ok` markers and are listed.

## Ambiguities resolved (all fail closed)

1. **`verify_cert` reason.** It uses the admission reason verbatim. That reason already starts with "quarantine:", so it
   is not prefixed a second time.
2. **An item meeting no band.** `admission_decision` returns ADMIT with the reason "meets no band: not an admission
   question". `verify_cert` never asks it for such items. Erratum E1-2 records this convention.
3. **An item meeting both bands** is refused.
4. **Grant `geometry`** must be exactly the strings "5"/"1/2" (production) or "3"/"1/2" (test). Rational equivalents
   such as "5/1" are refused. Erratum E1-3 makes the stricter reading govern the grant text.
5. **Grant fields.** Unlisted extra fields are ignored. Hex fields must be lowercase. `not_after_utc` must carry a UTC
   designator (Z or +00:00), and expiry is inclusive (now ≤ not_after).
6. **`frozen_commit`** must be a **proper** ancestor of the grant commit; equality is refused. Erratum E1-4 records
   that there is no conflict in practice.
7. **`code_pins` format** (not fixed by the spec). Accepted are a list of `{"path", "sha256"}` objects or an object
   `path → sha256`, with the sha as 64 hex or `sha256:`+hex. The implementing file's repository-relative path must
   appear exactly once, with its sha.
8. **Check 7, now settled by erratum E1-1.**
   * Strict descendant: a ref pointing **at** the grant commit is allowed, and a ref at a commit having the grant commit
     as a proper ancestor is refused. My original reading (a ref at the grant commit counts as a descendant) was
     stricter than intended and would have refused all production admissions once the grant commit is fetched.
   * Refs are peeled to commits, and refs to non-commit objects are ignored.
   * A detached HEAD exempts no branch.
9. **Review mode, additional requirements:**
   * the marker's commit G changes only the grant path;
   * G and S are ancestors of HEAD;
   * "exactly one commit S whose only parent is G" is taken over all commits reachable from any ref that descend from
     G. G must have exactly one child, whose only parent is G; a merge child or a second child is refused.
10. **Test context re-validation.** The constructor conditions (not this repository, not a worktree, no
    production-namespace ref) are re-checked at every admission.
11. **Certificate descriptors** must carry a 64-hex sha256, in both modes.
12. **Probe guard (§4 / protocol §7(c)).** The harness and tests use their **own** compiled copy of §1. The harness only
    checks at start that the variant's tables are equal, and aborts otherwise. No probe decision reads the variant's
    tables.
13. **N10(c) "a worktree of this repository".** A real `git worktree add` would write into this repository's `.git`,
    which is forbidden. It is emulated read-only by a scratchpad directory whose `.git` file points at this
    repository's git dir, giving the same common dir; the constructor refuses it.
14. **Harness probe 7r** was added to show geometry-blind REAL-band refusals. It has no committed counterpart and is
    judged by R2.

## §9 Evidence of independence (protocol §7(b); R3 N18)

* **Session (review R4 NB9).** This agent (the verifier's author) and the coordinator run under the **same top-level
  session**, `session_01RiV5bfPm5GJ4GcvoBrCC3p`, as separate subagents. This is the agent that wrote the research
  verifier `srk_verify_indep.py` and its harness v1/v2.
  * I have no separate agent identifier available to me. The scratchpad directory uuid
    `ea54e9f6-e828-5447-be15-220ef2c329fd` is shared with the coordinator, so it identifies the top-level session, not
    this agent.
  * Independence therefore rests on three things:
    * subagent separation;
    * the declared list of sources read below, which contains no guard, producer or driver code;
    * the independent divergences found when the two implementations were compared (erratum 1, E1-1 to E1-4),
      including a real defect in this variant (E1-1) that the comparison caught.
* **Sources read for this work:**
  * `fc2/FC2_SPEC.md` (rev. 1), `fc2/FC2_SPEC_R2.md` and `reviews/BRIEF_FC2_VERIFIER_VARIANT_AUTHOR.md`;
  * `fc2/FC2_SPEC_R2_ERRATUM_1.md` and `reviews/BRIEF_FC2_VERIFIER_VARIANT_AUTHOR_FOLLOWUP_1.md`;
  * `governance/OWNER_RULINGS_2_P309_VERBATIM.md` (full; fenced-body sha256 verified), and
    `governance/OWNER_DECISIONS_P309_VERBATIM.md` lines 240–275 plus a keyword search;
  * protocol rev. 2b §6 and §7 (`RNS/protocol_prep/P309_PROTOCOL.md`);
  * `config/FORMAL_QUARANTINE_P309.json` and the band clauses of `RNS/config/TARGET_QUARANTINE_309.json`;
  * `code/p309_env.py`, the header of `code/p309_scan.py`, and `tests/planted_control_p309.py`;
  * my own research verifier, harness and tests;
  * the decoy certificate JSON files (as data), and the committed `RNS/verify/VERIFY_RESULTS.json`.

  Disclosure: during the first attempt (rev. 1, stopped by a tooling denial) I inspected the source of the **research**
  quarantine guard's helper functions `q309_guard.log_execution`, `guard_drift`, `scan`, `_scan_file` and `_in_band`,
  and its pattern constants. The purpose was to learn the ledger API and the scanner rules. These are research
  quarantine utilities, not the producer and not the FC2 guard.
* **Statement.** No producer code was consulted: `RNS/impl/srk_*.py` and the overnight `c1b_*`/`d309_*` modules were
  never opened, imported or run. The FC2 guard `code/p309_guard.py`, its tests and the coordinator's other FC2 code
  were never opened; only their file names appeared in `git status` and the scanner output. No number of cells 305–309
  was read.
* **Variant sha256:** `9d9f8cec52cfd49ab146a45c44e03fde493614f81551af584317ab7d3545498f` (after erratum 1).

Every execution of this work is ledgered in `ledger/ZERO_TARGET_LEDGER.jsonl` through `code/p309_env.py`: one line per
test execution, the harness start and end, the sandbox smoke test, the sanity run, the scan and the governance
reads. Every line has 0 target evaluations and declares only decoy or TEST-band drifts. No git write was made in this
repository.

## P309-r2: the verifier author's changes (gate step 3; `governance/BRIEF_R2_VERIFIER_AUTHOR_1.md`)

This section is appended for r2. The r1 text above is unchanged and describes r1's variant (`9d9f8cec…`). At step 3a
(`e07e3ee8`) the six verifier-side files were copied byte for byte from r1's freeze F (`4c754a73`). The changes below
were made by the verifier author in FNS2 only. The full account (diff summary, re-pin list, controls, and every read,
run and write) is `verify/R2_VERIFIER_CHANGES_REPORT.md`, and the per-command ledger is
`verify/R2_VERIFIER_EXEC_LEDGER.jsonl`.

**Where the runs happened.** Every test, control and regeneration ran in a scratch clone of the r2 branch, under the
author's scratchpad, with its remote removed and no ref in either production namespace. The reason: the tests and the
harness ledger every execution through `code/p309_env.py`, which writes `<FNS>/ledger/ZERO_TARGET_LEDGER.jsonl`. FNS2
has no `ledger/` before step 4 (its genesis line is the coordinator's), and this step may write only the six files and
its two outputs. The clone's bytes of the six files were checked equal to FNS2's before each run.

### V1: literals (`governance/R2_LITERAL_DISPOSITION.json`; OD-R2-1 option (b), provisional)

| file | line (r1) | r1 | r2 | disposition |
|---|---|---|---|---|
| variant | 163 | `refs/p5y-k5-cell309-p309-r1/target-consumed` | `refs/p5y-k5-cell309-p309-r2/target-consumed` | owner |
| variant | 170 | `_FNS_REL = …/p5y_k5_cell309_p309_r1/` | `…/p5y_k5_cell309_p309_r2/` (grant, manifest and result paths) | rename |
| variant | 175 | `campaign: p5y_k5_cell309_p309_r1` | `p5y_k5_cell309_p309_r2` | binding |
| tests | 791, 815 | production-shaped `campaign` (N10, N11) | `p5y_k5_cell309_p309_r2` | binding |

Kept unchanged: every schema-format name (`P309_GRANT/1`, `P309_TEST_GRANT/1`, …), the verifier history commit
`6522db10` in this README, and the variant's research-namespace reads.

### V2: both production namespaces forbidden (addendum 2, F1)

* **Variant.** `PRIOR_PRODUCTION_REF_NAMESPACE = 'refs/p5y-k5-cell309-p309-r1/'` and
  `FORBIDDEN_REF_NAMESPACES = (PRIOR_PRODUCTION_REF_NAMESPACE, PRODUCTION_REF_NAMESPACE)`. `_validated_sandbox` (the
  `TestContext` refusal) loops over that tuple, so a sandbox with a ref under either namespace is refused.
* **Sandbox helper.** `_FORBIDDEN_REF_PREFIX = (_FORBIDDEN_REF_PREFIX_R1, _FORBIDDEN_REF_PREFIX_R2)`. `_assert_ref`, used
  by every ref-moving method, refuses either. The new `assert_no_production_refs()` checks both, at construction and on
  leaving the context.
* Each literal is the value of its own module-level constant because the scanner accepts a production-token literal
  only as the `Constant` value of a reviewed `token_definitions` home. A tuple of literals would be a `MARKER_TOKEN`
  finding.
* **Static check:** `TestR2Verifier.test_V2_both_namespaces_forbidden`. No test or control creates a ref in either
  namespace. The TEST-only prior-marker name was not needed, so `_ALLOWED_REF_PREFIXES` is unchanged.

### V3: the sandbox base rule (P6(b), P6(e))

* `sandbox_base_commit()` reads this repository's HEAD history for `<FNS>/ledger/FREEZE_RECORD.json`. The path is
  derived from the helper's own location, so r1's record at r1's path is not this namespace's record.
  * No commit touches it: the base is HEAD (development).
  * Exactly one commit touches it, that commit touches only the record, and its only parent equals the record's
    `freeze_commit` (40-hex): the base is F (post-freeze).
  * Any other shape raises `FreezeRecordError`. That is loud, and never a refusal.
* It is implemented in `verify/` only, with nothing imported from `code/` or `tests/`.
* **Pre- and postconditions.**
  * The base's history must hold 0 record commits.
  * A new sandbox holds 0, checked again by `build_valid` and on leaving the context. A flow that builds records
    deliberately declares them with `Sandbox(tag, expect_freeze_records=n)`.
* **History walk.** Commits "touching" the record are found with `git rev-list <rev> -- <record>`, git's default
  history simplification for a path, as `git log -- <path>`.
  * The scanner's option allowlist does not include `--full-history`.
  * In a linear history the two are the same.
* **Static check (P6(e)):** `TestR2Verifier.test_V3_base_rule_static`. Every git `HEAD` operand in this author's four
  Python files is accounted for by owner and by the repository it names. The only read of the real repository's HEAD
  that is used as a sandbox base is in `sandbox_base_commit`.
* **Shapes:** `TestR2Verifier.test_V3_base_rule_shapes`, with a TEST-named record path inside a sandbox: development,
  F′/FR′, a checkpoint commit after FR′, and nine malformed shapes.

### V4: `P309_SCRATCH_ROOT` (P7)

* `scratch_sandbox_base()` returns `<P309_SCRATCH_ROOT>/fc2_sandbox_verifier`. It raises `ScratchRootError`, with no
  fallback, if the root is:
  * unset or empty;
  * not absolute;
  * different from its own realpath;
  * not an existing directory;
  * inside the repository;
  * overlapping (equal to, containing or inside) any entry of `P309_FOREIGN_ROOTS`, which is optional,
    `os.pathsep`-separated, and must contain only absolute entries.
* `Sandbox.__init__` calls it first, on every construction.
* The hard-coded session path (r1 `SANDBOX_BASE`) is gone. So are the session id in the ledger purpose string and the
  scratchpad path in a ledger note.
* **Controls:** `TestR2Verifier.test_V4_scratch_root_refusals` (18 negative cases and 2 positive),
  `test_V4_no_session_path_in_code`, and constructor-level controls in the report.

### V5: `VERIFY_RESULTS_SCOPED.json`

**Regenerated** (the recommended option) for r2's variant bytes. It ran with the unchanged harness (`45902e30…`) as
`run_verify_all_scoped.py --jobs 3 --unit-tests`: decoy-only and FC2 admission only, in the scratch clone in this
cloud session, with `P309_SCRATCH_ROOT` a fresh scratchpad directory.

* **Wall time:** 594.7 s, from 2026-10-01T12:36:58Z to 12:46:53Z (I1 493.0 s; unit tests 101.1 s).
* **New file sha256:** `404e3c3cb3323865fee80e6c91573506df1c4db83e1c6968487357f0a4c2cafe`.
* **Against r1's file** (`bad3ffa7…`, at F), over all 2369 certificate entries (103 genuine, 2266 mutants):
  * verdicts, expectation rules, expectation flags and identity-to-committed flags are all identical;
  * 41 entries differ in bytes, only by the declared namespace substitution (`…_p309_r1` → `…_p309_r2`), in the grant
    path inside "no grant" refusal reasons;
  * the summaries are identical: the same counts, and `differences` lists that are equal as multisets. Their order
    follows worker completion.
* **No finding.**

### Identities and counts (sha256)

| file | r1 (F) | r2 |
|---|---|---|
| `verify/srk_verify_indep_scoped.py` (variant; `verifier_id` = `sha256:` + this) | `9d9f8cec52cfd49ab146a45c44e03fde493614f81551af584317ab7d3545498f` | `e82d68121ecd0003c61ed304d57e65f8ef7cda1aa9aad1c1ea08b8c01336aebf` |
| `verify/scoped_sandbox.py` | `58d15e632511af18c3ce4397a22ea8722a094f423ff468c67274ceefcdf21159` | `5fff1ba8c671af77d04dfcad3ef6d8f993db8d50ea46e995214d07fd218fd0d2` |
| `tests/test_verify_scoped.py` | `1483d6c2f5c9d8d3a469915fe6ab85d0cb27f3abdfcac53b168ff6754a64a10c` | `94db67d47ea30f2cfdbdd4a1ecc0ff039f775f887f155dca57887334e06c7ad3` |
| `verify/run_verify_all_scoped.py` | `45902e30cb59db718c2a133fa321e30ee183a3fa18781c3698a11ce7f48b90d8` | unchanged |

**Test counts.** 42 = 21 ported self-tests + 16 FC2 tests (D1, N01–N13, P1, P2) + 5 r2 tests (`TestR2Verifier`):

| run | topology | tests | result |
|---|---|---|---|
| A: after V1, V2 and V4, **before V3** | development | 40 | OK (99.1 s) |
| B: **after V3** | development | 42 | OK (101.2 s) |
| V5 harness `--unit-tests` | development | 42 | OK (101.1 s) |
| C: after V3 | post-freeze (synthetic F′, record-only FR′, then a checkpoint commit; sandboxes based on F′) | 42 | OK (103.1 s) |

**Independence (r2).**
* No producer, guard, driver or overnight code was opened. Neither was the coordinator's `sandbox_base()` or
  `p309_driver.recorded_freeze`: V3 was implemented from the brief's statement of their semantics.
* For V7 and for the scanner's rules, the author read parts of `code/p309_scan.py` and all of `code/p309_scan_pins.py`.
  Their hash functions were imported read-only in the scratch clone.
