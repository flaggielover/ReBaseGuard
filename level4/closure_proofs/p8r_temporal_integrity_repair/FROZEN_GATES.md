# P8R frozen gates

**Frozen at the temporal anchor, before any production result existed.** Every
threshold is quoted from `src/rebaseguard_p8r/config.py`; this file states no
number that module does not own. `I7` checks that module byte-for-byte against
the anchor blob, so a threshold cannot move after a result is seen.

There are two gate classes and they behave differently on purpose.

* **Integrity gates `I1`–`I13` must pass.** They are the repair. A `FAIL` or an
  `UNVERIFIABLE` in this class is fatal.
* **Scientific resolution questions `S1`–`S17` must be *resolved*, not true.**
  Each carries a frozen rule and a frozen set of admissible outcomes. A
  `REJECTED` question is a negative scientific result and is a perfectly good
  outcome for this campaign.

---

## 1. Integrity gates

| gate | statement | how it is checked |
|---|---|---|
| **I1** | A commit exists carrying the frozen prose, the complete executable surface and the tests, and carrying **no** production result. | `git ls-tree` of the anchor; fails if any `results/` path other than `results/integrity/protected_tree_manifest_pre.json` is present |
| **I2** | Every frozen prose artifact is byte-identical to the digest recorded at the anchor. | recompute SHA-256, compare to `PROTOCOL_DIGEST.json` |
| **I3** | Every file under `src/`, `experiments/`, `scripts/`, `tests/` is byte-identical to the digest recorded at the anchor. | recompute SHA-256, compare to `SOURCE_MANIFEST.json` |
| **I4** | No calibration-search evaluation ever read a calibration-verification address. | the executed trace's classes and batches, plus the class tag digests |
| **I5** | No production address coincides with any calibration address. | pairwise tag digests over the frozen tag inventory |
| **I6** | No frozen prose artifact changed after the anchor commit. | `git show <anchor>:<path>` vs the working tree |
| **I7** | No frozen threshold, budget or grid changed after the anchor: `config.py` is byte-identical to its anchor blob. | `git show` vs the working tree |
| **I8** | Every production command is recorded verbatim, before production, and its script exists. | `COMMAND_MANIFEST.json` |
| **I9** | Every primitive value is a pure function of its address. | the six independent checks in `scripts/rng_identity.py` |
| **I10** | Every result artifact carries a working generator, a verbatim `argv`, a git commit, an environment record and a matching payload digest. No orphans. | walk `results/**`, recompute payload digests |
| **I11** | Every protected tree is byte-identical to its pre-campaign manifest; only the authorised root status file may differ. | recompute the manifest, compare per-tree aggregates |
| **I12** | The P8R focused test suite passes in full. | recorded pytest outcome |
| **I13** | The executed calibration budget, re-derived from the stored trace, equals the single declared budget. | `calibrate.executed_budget` vs `calibrate.declared_budget` |

`I13` is the gate that exists because P8's protocol said 250,000/2,048,000 while
its executable used 163,840/1,024,000 and nothing compared them.

## 2. Scientific resolution questions

Admissible outcomes: `SUPPORTED`, `REJECTED`, `INCONCLUSIVE`, `OUT_OF_SCOPE`.
Every rule below is applied literally by `experiments/derive_resolution.py`,
which contains no threshold literal of its own.

| id | question | frozen rule | admissible |
|---|---|---|---|
| **S1** | Does P8R reproduce P3's `CLOSED` Gaussian `GammaTilde` for both detectors at `m in {1,2,3,5}`? | `SUPPORTED` iff ≥7 of 8 cells agree within `COMBINED_Z_TOLERANCE = 3` combined SE; `REJECTED` iff ≤4; else `INCONCLUSIVE` | S/R/I |
| **S2** | Does P8R reproduce P4's `m=1` CUSUM `Gamma_f`, and does its independent family implementation match P4's scores? | `SUPPORTED` iff ≥5 of 6 families within 3 combined SE **and** max score difference ≤ `S2_SCORE_TOL = 1e-12` | S/R |
| **S3** | Do the frozen thresholds achieve the frozen in-control target? | `SUPPORTED` iff relative error ≤ `S3_ARL0_REL_MAX = 1%` in every cell with a threshold | S/R |
| **S4** | Do the exact regularity identities hold for all six families? | `SUPPORTED` iff `|E[eps psi] - 1| ≤ 1e-4`, `|E[psi]| ≤ 1e-8`, `|I - E[psi']| ≤ 1e-6` | S/R |
| **S5** | Does every non-Gaussian SR threshold reach the target on a genuinely held-out sample? | `SUPPORTED` iff no family ends `CALIBRATION_FAILED` under the frozen ladder, i.e. each is accepted within `CAL_TOLERANCE = 0.5%` on `CAL_VERIFY_1` or `CAL_VERIFY_2` | S/R |
| **S6** | **Regime survival.** Is full reuse locally repelling in every eligible cell? | `SUPPORTED` iff the lower 95% bound of `Gamma_A` exceeds `S6_LOWER_BOUND = 2` in all 40 eligible cells. The 8 `t3` cells are reported in full and **never counted** either way. | S/R |
| **S7** | **`H1`, the window-separability law.** | `SUPPORTED` iff the relative spread `max/min - 1` of `K` across the 10 eligible `(D,f)` cells is ≤ `S7_SPREAD_MAX = 0.10` for **every** `m in {2,3,5}` | S/R |
| **S7D** | **`H1-D`, detector invariance of `K`.** | `SUPPORTED` iff `|K(cusum,f,m)/K(sr,f,m) - 1| ≤ S7D_RESIDUAL_MAX = 0.03` for all 5 eligible `f` and all `m in {2,3,5}` | S/R |
| **S7F** | **`H1-F`, family invariance of `K`.** | `SUPPORTED` iff, per detector, the spread of `K` across the 5 eligible families is ≤ `S7F_SPREAD_MAX = 0.10` for every `m in {2,3,5}` | S/R |
| **S7X** | The same three quantities at `m in {10,20}`. | `OUT_OF_SCOPE` by construction: outside P3's supported grid, reported and never gated | O |
| **S8** | **`H3`, the decomposition identity.** | `SUPPORTED` iff `max_batch \|Gamma_A(m) - (1/m) sum_r gamma_r - R_m\| ≤ S8_ABS_TOL = 1e-9` in every cell. This is an **exact** identity summed in two different orders, so the test is absolute, not statistical: the residual and its batch SE are both floating-point noise of order `1e-16`, and a `k × SE` rule would compare noise to noise. | S/R |
| **S9** | **`H4`, the convention identity.** | `SUPPORTED` iff `|(Gamma_A - Gamma_B) - R_m| ≤ S9_EXACT_TOL = 1e-12` in every cell and `P(tau<m)` is present | S/R |
| **S10** | **`H6`, P7 boundary transfer.** | `SUPPORTED` iff P7's criterion reproduces in ≥ `S10_FAMILIES_REQUIRED = 5` of 6 families on the declared sub-family grid (`detector x m in {1,5}`, metrics `{arl, ref_mse, fap100, e_acf1}`). **This is P7's criterion on a declared subset of P7's coverage, not verbatim P7 coverage.** The subset is frozen here and may not be widened afterwards. | S/R |
| **S11** | **`H5`, operational degradation.** | `SUPPORTED` iff the chain `ARL` at `rho=1` is below `S11_ARL_FRACTION = 50%` of the same-cell nominal `ARL_0` in every declared cell | S/R |
| **S12** | **`H7`, detector transfer.** | `SUPPORTED` iff the paired 95% CI of `Gamma_A(cusum)/Gamma_A(sr)` contains 1 in ≥90% of the `(f,m)` comparisons; `REJECTED` iff it excludes 1 in ≥90%; else `INCONCLUSIVE`. Intervals use the CRN-paired linearised SE. | S/R/I |
| **S13** | **`H8`, seed sensitivity.** | `SUPPORTED` iff `E1` and `E5` agree within 3 combined SE in ≥ `S13_CELL_FRACTION = 90%` of all 72 cells **and** ≥ `S13_NON_T3_FRACTION = 95%` of the 60 non-`t3` cells | S/R |
| **S14** | **Drift-pattern reporting completeness.** | `SUPPORTED` iff every declared drift cell is reported with `q50`, `q95`, `P(delay>100)` and an explicit tail label | S/R |
| **S15** | **`H9`, heavy-tail attraction at `t3`, `m=20`.** | `SUPPORTED` iff the upper 95% bound of `Gamma_A` lies below 2 in `E1` **and** `E5` **and** the independent reimplementation. Anything else is `INCONCLUSIVE`. Deliberately conservative: a point estimate below 2 is not evidence of attraction, the theorem hypotheses are not established for `t3`, and `m=20` is outside P3's grid in any case. | S/I |
| **S16** | **The Gaussian SR anchor against P3 and P7.** | Frozen decision table: agreeing with P7 within 3 combined SE at every `m` while sitting systematically below P3 ⇒ `KNOWN_PREEXISTING_DISCREPANCY`; agreeing with P7 only ⇒ `AGREES_WITH_P7`; agreeing with P3 only ⇒ `AGREES_WITH_P3`; agreeing with neither ⇒ `NEW_DEFECT_CANDIDATE`, which `REJECTS` the question. P8R owns and resolves neither set of numbers. | S/R |
| **S17** | **Independent reimplementation.** | `SUPPORTED` iff at most `S17_MAX_OUTLIERS = 1` of the 18 representative cells of the independently coded simulator exceeds 3 combined SE against production. One allowance absorbs ordinary multiplicity over 18 comparisons without absorbing a real defect. | S/R |

## 3. What a resolution does and does not license

* A `REJECTED` question is a **negative scientific result**. It is reported as
  such, in the exact wording the rule supports, and it does not fail the
  campaign.
* A `REJECTED` `S7` does **not** license describing `H1` as "approximately
  holding", "holding up to a scale factor", or "holding for most cells".
* A `REJECTED` `S6` does not license dropping a cell; it licenses applying P3's
  regime-audit table to it.
* An `INCONCLUSIVE` `S12` does not license assuming transfer anywhere.
* An `INCONCLUSIVE` `S15` does not license reporting attraction at `t3`/`m=20`
  as a finding, a theorem or a certified numerical result.
* **No question may be re-thresholded, re-scoped, split, or re-run at a
  different sample size in order to change its resolution.** Doing so changes
  `config.py` and fails `I7`.

## 4. The closure rule, frozen

```
CLOSED_CANDIDATE   iff every I1..I13 is PASS
                   and every mandatory S-question is resolved to an
                   admissible status

PARTIAL_CANDIDATE  iff every I1..I13 is PASS
                   but at least one mandatory S-question is unresolved

FAIL_CANDIDATE     iff any I1..I13 is FAIL or UNVERIFIABLE
```

Mandatory questions: `S1 S2 S3 S4 S5 S6 S7 S7D S7F S7X S8 S9 S10 S11 S12 S13 S14
S15 S16 S17`.

Note what the rule does **not** contain: any requirement that a hypothesis be
true. `S7 = REJECTED` with every integrity gate passing is `CLOSED_CANDIDATE`.
That is the whole point of separating the two classes — P8's evidence was sound
and its procedure was not, and a repair should be judged on the procedure.

**The verdict is a candidate.** It is not authoritative and must not be promoted
to `CLOSED` without independent adjudication.
`results/verdict.json` records `AUTHORITATIVE_STATUS_RECOMMENDATION =
AWAIT_CODEX_ADJUDICATION`.

## 5. Novelty

`NOVELTY_STATUS = NOT_ESTABLISHED`, fixed before results and not revisable by
any outcome of this campaign. A repair campaign does not generate novelty, and
none of the following is evidence of it: zero direct literature hits, the
absence of a known transfer law, a new negative result, a new empirical matrix.
