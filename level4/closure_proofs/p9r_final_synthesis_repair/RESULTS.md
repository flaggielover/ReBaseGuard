# P9R results

```text
P9_ORIGINAL_VERDICT = PARTIAL
P9R_VERDICT = CLOSED_CANDIDATE          (candidate only; Codex adjudicates)
TEMPORAL_REPAIR_ANCHOR = c1e8f98bb908aff095814f3c45994ecc0f0846ed  (VALID)
P9_T2A = EXACT
P9_T2B = CONDITIONAL_ON_ASM_DOM
GLOBAL_MONOTONICITY = EMPIRICALLY_SUPPORTED
SR_RECURRENCE = REPAIRED
A5_A6_REPRODUCIBILITY = REPAIRED
CLAIM_INFLATION = ABSENT
DEPENDENCY_GRAPH = TYPED_AND_EXPLICIT
P3_X1_CLASS = CERTIFIED_NUMERICAL
P7_MONOTONICITY_CLASS = NOT_ESTABLISHED
P8_ORIGINAL_VERDICT = FAIL
P8R_VERDICT = CLOSED
P8R_REQUIRED_FOR_P9R_CORE = NO
D09 = BLOCKS_GLOBAL_LEVEL4_CLOSURE; DOES_NOT_BLOCK_P9R
D13 = SCOPE_LIMITING; DOES_NOT_BLOCK_P9R
D15 = PROVENANCE_LIMITATION; DOES_NOT_BLOCK_P9R
PROTECTED_TREE = PASS
NOVELTY_STATUS = NOT_ESTABLISHED
SCIENTIFIC_CORE = EXACT_AT_RHO_ZERO_PLUS_ONE_NAMED_CONDITIONAL
LEVEL4_GLOBAL_CLOSURE = NO
AUTHORITATIVE_STATUS_RECOMMENDATION = AWAIT_CODEX_ADJUDICATION
```

P9R does **not** self-promote. `CLOSED_CANDIDATE` is a submission, not a status.

---

## 1. Integrity gates

`results/integrity/gate_report.json`, recomputed by
`scripts/audit_integrity.py --anchor c1e8f98bb908aff095814f3c45994ecc0f0846ed`.
Its `head` field records the commit the audit ran at, which is the anchor:
Checkpoint B did not exist yet when the report was written. Re-running the
same command at Checkpoint B reproduces all fifteen passes.

| gate | verdict | evidence |
|---|---|---|
| `I1` temporal anchor valid | `PASS` | anchor `c1e8f98`, ancestor of `HEAD`, 34 P9R files, exactly one `results/` file (`protected_tree_manifest_pre.json`), all required protocol/source/generator files present |
| `I2` original P9 immutable | `PASS` | one commit ever touched `p9_final_synthesis` (`a3e3cab`); its tree hash at `HEAD` equals its tree hash at `a3e3cab`; `git diff` empty |
| `I3` source digest locked | `PASS` | 20 files byte-identical to the anchor |
| `I4` protocol and gates locked | `PASS` | 9 frozen prose files byte-identical to the anchor |
| `I5` correct frozen SR recurrence | `PASS` | six deterministic checks; first-step shift bitwise `= log 2`; alarm decisions differ on the witness |
| `I6` A5/A6 generator completeness | `PASS` | all six artifacts carry generator, argv, git commit, environment, config and a payload digest that verifies |
| `I7` claim ledger source-derived | `PASS` | rule `V8`: every cited path exists; every claim cites a section |
| `I8` claim-class firewall | `PASS` | rules `V1`-`V5`, `V11`, `V14` clean |
| `I9` monotonicity premise explicit | `PASS` | `ASM-DOM` present, reached by `P9R-T2b` via an `ASSUMPTION` edge, premise of no exact theorem |
| `I10` `P3-X1` repaired | `PASS` | class is `CERTIFIED_NUMERICAL` |
| `I11` `P7-A`/`P7-D0` split | `PASS` | five nodes at their required classes |
| `I12` P8/P8R reconciliation | `PASS` | `P8 = FAIL`, `P8R = CLOSED`, and the premise closure of `P9R-T2a`/`T2b` contains no P8 or P8R node |
| `I13` no novelty inflation | `PASS` | `P9R-N1` is `NOT_ESTABLISHED`; this file declares it |
| `I14` protected tree | `PASS` | 3428 tracked files outside the P9R namespace, zero differences pre vs final; no root status file changed |
| `I15` focused tests | `PASS` | see §8 |

## 2. Scientific gates

| gate | question | resolution |
|---|---|---|
| `S1` | is the `rho=0` invariant-law / mixture identity exact? | **`EXACT`** — `P9R-T2a`, `THEORY.md` §2 |
| `S2` | is the strict stationary ARL deficit exact, conditional, or false? | **`CONDITIONAL`** on `ASM-DOM` — `P9R-T2b` |
| `S3` | status of global monotonicity of `A`? | **`EMPIRICALLY_SUPPORTED`** — 0 increases detected at 3 SE over 640 adjacent-node comparisons; not proved |
| `S4` | does the corrected reproduction agree with authoritative P7? | **`MC_CONSISTENT`** for both detectors — CUSUM 8/8 (max `\|z\|` 2.36), SR 8/8 (max `\|z\|` 1.73) |
| `S5` | does the `log 2` SR defect materially change the ARL values? | **`IMMATERIAL`** for the ARL estimand (pooled paired `+0.402 ± 0.200`, `\|z\| = 2.01 < 3`) — with the caveat in `REPRODUCTION.md` §5 that it is nevertheless a real correctness defect with a systematic sign |

A `CONDITIONAL` `S2` with an `EMPIRICALLY_SUPPORTED` `S3` is the outcome the
frozen gates were written to accept. No gate required `S3 = PROVED`, precisely
so that closure pressure could not manufacture one.

## 3. The theorem, repaired

**Exact (`P9R-T2a`).** For either frozen Gaussian detector, convention A, fixed
`m >= 1`, `rho = 0`: `e_{j+1} ~ N(0,1/m)` independently of the state, so
`N(0,1/m)` is the unique invariant law; the stationary in-control ARL is exactly
`E_{e~N(0,1/m)}[A(e)]`, finite by Lemma L2; and the first-order local multiplier
is exactly `0`. `hypotheses = NONE_BEYOND_MODEL`; every logical premise is an
`EXACT_THEOREM`.

**Conditional (`P9R-T2b`).** *If* `A(e) <= A(0)` for `N(0,1/m)`-a.e. `e`
(`ASM-DOM`), *then* `E[A(e)] < A(0)` strictly. Strictness costs nothing extra:
Lemmas L3 (`A(0)>1`) and L4 (`A(e)->1`) already put `A` strictly below `A(0)` on
a positive-measure set. The single open premise is the a.e. **upper bound**.

**Why this is stronger than relabelling P9's proof.** P9 needed global
monotonicity. `P9R-T2b` needs only global maximality at `0`, which is strictly
weaker, so the conditional theorem is strictly stronger and the residual gap is
strictly smaller.

**Four exact lemmas** (`THEORY.md` §1) carry what P9 tried to carry with
monotonicity: `L1` evenness, `L2` uniform boundedness `sup_e A(e) <= C_D`
(`C_CUSUM = 9.9e8`, `C_SR = 1.4e11`) giving unconditional integrability *and* a
rigorous quadrature-truncation bound, `L3` `A(0)>1`, `L4` `A(e)->1`.

**Operational corollary, narrowed (`P9R-T3`).** `rho < rho_c` does not, in the
frozen tested models, guarantee nominal-ARL preservation. P9's universal
formulation — that no threshold in `rho` can be an operational safety boundary —
is not claimed.

## 4. Monotonicity audit

| detector | `A(0)` | grid | pairs | increases at 3 SE | argmax | median min-detectable increase | max min-detectable increase |
|---|---:|---|---:|---:|---:|---:|---:|
| CUSUM | 473.12 ± 3.31 | `[0,8]`, 321 nodes, 20000 paths/node | 320 | **0** | `e = 0.000` | 0.0147 | 13.80 |
| SR | 466.10 ± 3.22 | same | 320 | **0** | `e = 0.000` | 0.0150 | 13.49 |

Evenness (`L1`) is corroborated independently: max `\|z\|` between `A(e)` and an
independently seeded `A(-e)` is `2.22` (CUSUM) and `1.96` (SR) over nine nodes
each.

**The audit's power is reported, not implied.** Near `e = 0`, where `A ~ 470` and
the node SE is `~3.3`, the smallest increase this grid could detect at 3 SE is
about `13.8` cycles — so the audit has essentially no power there. It is strong
in the tail, where `A -> 1` and SEs are tiny. This is why the status is
`EMPIRICALLY_SUPPORTED` and not `PROVED`:

```text
GLOBAL_MONOTONICITY = EMPIRICALLY_SUPPORTED     (not proved; P9R-T2b stays conditional)
```

P9 reported "0/320 violations at 3 SE" without its power. The same finding,
with its power stated, cannot be mistaken for a proof.

## 5. Reproduction

Full tables in `REPRODUCTION.md`. Sixteen authoritative P7 cells, reproduced
under P7's own `n_rep = 5000`, `n_cycles = 50`, `burn_in = 12`, read from P7's
artifact at run time.

```text
CUSUM   8/8 MC_CONSISTENT   max |z| = 2.36
SR      8/8 MC_CONSISTENT   max |z| = 1.73     (corrected recurrence)
```

The `log 2` defect, replayed on identical seeds, biases SR ARL downward by
`0.402 ± 0.200` cycles pooled — a systematic sign, below the 3-SE materiality
threshold, and not a licence to keep the defective recurrence.

The mixture quadrature and the recursive `rho = 0` chain agree to
`0.15–1.81` cycles across eight cells, with a three-part error budget whose
truncation term is rigorously bounded by Lemma L2.

## 6. Ledger, graph, and the repaired classifications

```text
nodes 75 (4 DEFINITION, 4 ASSUMPTION, 57 CLAIM, 10 STATUS)
edges 108 across 11 typed edge types
typed-graph validator violations       0 / 15 rules
collapsed-graph validator violations  36
```

Class distribution: `EXACT_THEOREM` 15, `FORMALLY_VERIFIED` 4,
`CERTIFIED_NUMERICAL` 2, `CONDITIONAL_THEOREM` 8, `EMPIRICAL_REPRODUCED` 5,
`EMPIRICAL_ONLY` 5, `NEGATIVE_RESULT` 6, `PARTIAL_PRIORITY_RESULT` 4,
`PROVENANCE_LIMITATION` 2, `NOT_ESTABLISHED` 6.

* `P3-X1` — `FORMALLY_VERIFIED` -> **`CERTIFIED_NUMERICAL`**. Its evidence is
  exact `Fraction` arithmetic plus an Arb 128-bit enclosure; P3's own
  `LEAN_CORRESPONDENCE.md` says the Priority-3 Lean file makes no numerical
  claim.
* `P7-A` -> **`P7-A-ID`** (`EXACT_THEOREM`, identity only), **`P7-A-MONO`**
  (`NOT_ESTABLISHED`), **`P7-A-OP`** (`EMPIRICAL_ONLY`).
* `P7-D0` -> **`P7-D0-ID`** (`EXACT_THEOREM`) and **`P7-D0-DEF`**
  (`CONDITIONAL_THEOREM`, on `ASM-DOM`).
* `P1-T1` — `EXACT_THEOREM` -> **`CONDITIONAL_THEOREM`** (a further, unrequested
  downgrade, on the authority of P1's own definition audit; not load-bearing for
  any P9R theorem).
* `ASM-DOM` and `ASM-MONO` exist as explicit `ASSUMPTION` nodes.

The collapsed-edge diagnostic (36 violations against 0) is the concrete
demonstration that an untyped dependency graph of this project is unsound.

## 7. Statuses reconstructed and propagated

| priority | status | what P9R uses |
|---|---|---|
| P1 | `CLOSED` | `P1-T1` at `CONDITIONAL` strength; not used by any P9R theorem |
| P2 | `CLOSED` | `P2-T1` exact (8/8 obligations discharged); `P2-C1` certified `m=1` SR interval |
| P3 | `CLOSED` | `P3-T1` exact local boundary — a premise of `P9R-T2a`(iii); `P3-X1` certified; `D-15` open |
| P4 | `PARTIAL` | conditional content only; not used by any P9R theorem |
| P5 | `PARTIAL` | `P5-T1` and `P5-T7` exact — both premises of `P9R-T2a`; `P5-T11` exact with `D-13` open |
| P6 | `CLOSED` | nothing; P6's kernel is different and its limitations are carried |
| P7 | `CLOSED` | `P7-A-ID` exact — premise of `P9R-T2a`; `P7-E1`/`P7-E2` reproduced; `P7-R1` negative |
| P8 | `FAIL` | surviving exact/conditional/negative tiers only, cited as P8 |
| P8R | `CLOSED` | cited as P8R evidence; **not** required by the P9R core |
| P9 | `PARTIAL` | the surviving retrospective synthesis, at partial strength |

`PARTIAL` does not invalidate a priority's claims and `FAIL` does not delete its
surviving evidence — both are asserted as validator rules (`V9a`, `V9c`) and
tested. `CLOSED` does not auto-validate (`V9b`).

**P8/P8R.** `P8R = CLOSED` closes the Priority-8 *repair* lineage. It does not
convert `P8 = FAIL`, does not imply universal model-class transfer, and is not
required by `P9R-T2a` or `P9R-T2b`: gate `I12` computes the premise/assumption
closure of both theorems and finds no P8 or P8R node in it. P8R's own
limitations are preserved — `P8R-T1` conditional, window law rejected, detector
transfer measured absent, `S15` empirically suggestive only and statistically
fragile, novelty not established.

## 8. Tests and regression

```text
focused suite   level4/closure_proofs/p9r_final_synthesis_repair/tests   110 passed
```

The suite checks anchor authenticity against git, original-P9 immutability,
the SR first step, the reset first step, the absence of the `log 2` shift, the
exact `log 2` shift in the P9 form, generator/provenance completeness, reduced
deterministic regeneration of A5 and A6, claim-class correctness, the `P3-X1`
reclassification, that no exact theorem carries monotonicity wording or an
assumption edge, the explicit `ASM-DOM` edge, the P8/P8R distinction, retention
of `D-09`/`D-13`/`D-15`, the `NOT_ESTABLISHED` novelty status, and the
protected tree. They are
implementation checks, not scientific adjudication.

Repository regression, measured against the baseline P8R recorded:

```text
level4/tests                              290 passed,  0 failed
p7_statistical_consequences/tests          31 passed,  0 failed
novelty_verification/tests                 17 passed,  1 failed   (baseline 17/1)
external_validation_v2/tests               43 passed,  2 failed   (baseline 43/2)
final_global_reaudit/tests                 33 passed,  3 failed   (baseline 33/3)
final_level4_closure/tests                 32 passed,  4 failed   (baseline 32/4)
p8r_temporal_integrity_repair/tests        71 passed,  1 failed   (baseline 72/0)
p9_final_synthesis/tests                   44 passed,  0 failed
```

(The `p9_final_synthesis` suite is measured at the Checkpoint B commit. Run
against an uncommitted working tree it reports two failures, because both of its
protected-scope checks call `git diff` and therefore see any uncommitted file,
including P9R's own.)

Every historical failure matches its baseline exactly. Two suites need an
explicit ruling, and P9R states both rather than filing them under "historical":

* **`p8r .../test_only_authorised_files_outside_p8r_differ` — one new failure,
  caused by P9R's existence, not by any byte P9R changed.** That test compares
  the *set* of tracked files outside the P8R namespace against P8R's
  pre-campaign manifest and authorises only root `README.md`. It therefore fails
  for **any** namespace added after P8R, including one that touches nothing.
  P9R changed zero bytes in `p8r_temporal_integrity_repair` and zero bytes in
  any protected tree — `I14` verifies this over all 3428 files with a zero
  difference count, and the per-tree aggregate hash for both
  `p9_final_synthesis` and `p8r_temporal_integrity_repair` is unchanged. This is
  an additive-detection test meeting an addition, and it is recorded as
  `P9R-D04` in `LIMITATIONS.md` §6.
* **`p9_final_synthesis/tests/test_protected_scope.py` — green.** Verified at the
  Checkpoint B commit: 44 passed, 0 failed. Its two protected-scope checks call
  `git diff` against the working tree, so they report any uncommitted file; that
  is why they must be measured at a commit, not mid-campaign.

## 9. What is still open

See `LIMITATIONS.md`. In short: `ASM-DOM` itself; global monotonicity;
`D-09`, `D-13`, `D-15`; P4/P5 literal failed gates; P6 calibration and
traceability; non-Gaussian, detector and window transfer;
novelty (NOT_ESTABLISHED); and Level-4 global closure.

```text
LEVEL4_GLOBAL_CLOSURE = NO
AUTHORITATIVE_STATUS_RECOMMENDATION = AWAIT_CODEX_ADJUDICATION
```
