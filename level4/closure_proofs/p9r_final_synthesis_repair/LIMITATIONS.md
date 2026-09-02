# P9R limitations

Written to be read *against* `RESULTS.md`. Everything here is a real
restriction on what the repaired synthesis may be used for.

## 1. The one premise P9R did not discharge

`ASM-DOM` — `A(e) <= A(0)` for `N(0,1/m)`-a.e. `e` — is **not established**.

* It is the sole gap between `P9R-T2b` and an exact theorem.
* It is weaker than global monotonicity of `A` in `|e|`, which is also not
  established. Proving either would close `P9R-T2b`; only the weaker one is
  needed.
* Grid evidence (`P9R-E3`) supports it and cannot discharge it. The audit has
  essentially no power near `e = 0` — the smallest increase it could detect
  there at 3 SE is about 13.8 cycles — which is exactly the region where a
  violation would matter most.
* Every sentence in this campaign that asserts the strict deficit carries the
  hypothesis. If a future campaign proves `ASM-DOM`, `P9R-T2b` becomes exact
  with no other change.

## 2. What `P9R-T2a` does not say

* It says nothing about the **size** of the degradation. That is measured
  (`P9R-E1`, `P7-E1`), not proved.
* It says nothing about `rho > 0`.
* It says nothing about other detectors, other conventions, non-Gaussian
  innovations, adaptive kernels, or out-of-control delay.
* "Maximally locally stable at `rho = 0`" is a statement about the first-order
  multiplier of the deterministic conditional-mean map. It is not a statement
  about the stochastic chain and not a statement about monitoring performance.
* It does **not** make `rho_c` meaningless. `rho_c` remains the exact local
  boundary of `P3-T1`.

## 3. What `P9R-T3` does not say

`P9R-T3` is a negative result about the frozen tested models under P7's frozen
criterion. It does not prove that no `rho`-based operational boundary, no
tolerance-based safety definition, no other metric and no other detector or
model class could admit one. P9's universal phrasing is explicitly retired.

## 4. Monte Carlo and numerical limitations

* All reproduction figures are Monte Carlo at `n_rep = 5000` with the replicate
  as the statistical unit. `MC_CONSISTENT` means `|z| <= 3` on the combined SE;
  it never means exact agreement.
* The mixture quadrature carries a three-part error budget. Its truncation term
  is a rigorous bound (Lemma L2) but its constants `C_CUSUM = 9.9e8`,
  `C_SR = 1.4e11` are extremely loose; they are useful only because the tail
  mass beyond `8 sigma` is smaller still.
* The `log 2` SR defect is `IMMATERIAL` for the post-burn-in ARL estimand at
  this sample size (pooled `+0.402 ± 0.200`), but its sign is systematic and it
  is *not* immaterial for per-path, first-step or short-horizon quantities.
  P9's SR numbers were close to right for the wrong reason.
* The response grid resolves `[0, 8]` at step `0.025`. Behaviour of `A` between
  nodes is not observed.

## 5. Inherited discrepancies, all open

| id | classification | why it stays open |
|---|---|---|
| `D-09` | `BLOCKS_GLOBAL_LEVEL4_CLOSURE`; `DOES_NOT_BLOCK_P9R` | the root `CURRENT LEVEL-4 CAMPAIGN: CLOSED` line contradicts mandatory rows `L4R-11` `FAIL`, `L4R-06`/`L4R-12` `PARTIAL`, `L4R-15` `FAIL`, `L4R-16` `OPEN`. A governance audit, not a P9R deliverable |
| `D-13` | `SCOPE_LIMITING`; `DOES_NOT_BLOCK_P9R` | `P5-T11` is exact; its gridded-map/PCHIP plug-in lacks a valid uncertainty budget and leaves a residual up to ~16 chain SE. May not be summarised as "within 3.5% agreement" |
| `D-15` | `PROVENANCE_LIMITATION`; `DOES_NOT_BLOCK_P9R` | P3's 49 files arrived in one uncommitted intake; preregistration cannot be authenticated and the evidence to do so does not exist |

None of the three is resolved by wording, and none is a `P9R` closure
prerequisite because no P9R theorem consumes any of them.

## 6. Repository-level limitations P9R does not repair

* **P4** — three frozen preregistered numerical closure gates remain literally
  false; `P4-T2` is not an iff characterisation.
* **P5** — attraction, flip type, global uniqueness, optima, bimodality onset
  and `m` trends remain conditional or finite-grid empirical.
* **P6** — calibration is 6/8 converged with sparse cells and a final refit that
  is not a verified fixed point; the missing independent Gate-9 review inside the
  P6 namespace is a traceability gap; production validation and transfer to
  detector-state-reading or adaptive kernels are not established.
* **P7** — `P7-B/C/D` retain their conditions; `P7-D` is a plug-in diagnostic,
  not certified.
* **P8** — `FAIL` stands. Window law rejected, literal `G7` fails, detector
  transfer measured absent, `G14` temporal integrity fails, no certified
  numerical result.
* **P8R** — `CLOSED` closes the repair lineage only. `P8R-T1` is conditional,
  `S15` is empirically suggestive and statistically fragile, novelty is
  not established, and none of it implies model-class transfer.
* **Historical suite failures** — `novelty_verification` (1 failure),
  `external_validation_v2` (2), `final_global_reaudit` (3),
  `final_level4_closure` (4) predate P9R and are unchanged by it. They must be
  compared against the authoritative baseline and not attributed to P9R.
* **`P9R-D04` — one new failure in the P8R suite, from an addition, not a
  mutation.** `p8r .../test_digests_and_protected_tree.py::
  test_only_authorised_files_outside_p8r_differ` compares the *set* of tracked
  files outside the P8R namespace against P8R's pre-campaign manifest and
  authorises only root `README.md`. Adding any new namespace fails it, whether
  or not that namespace touches anything. P9R changed zero protected bytes:
  gate `I14` compares 3428 files pre versus final with a zero difference count,
  and the per-tree aggregates for `p9_final_synthesis` and
  `p8r_temporal_integrity_repair` are identical. Classification:
  `PROVENANCE_LIMITATION`; `DOES_NOT_BLOCK_P9R`. It is a property of that test's
  design, and any future repair lineage will hit it too.
* **`P9R-D05` — `DISCREPANCY_REGISTER.md` is inside the frozen protocol digest.**
  Its closing table invites rows to be "appended during production", but gate
  `I4` forbids changing it after the anchor. The freeze wins: `P9R-D04` and
  `P9R-D05` are recorded here, in an unfrozen document, rather than by editing
  an anchored file. A future repair should keep the discrepancy register outside
  the frozen set, or make it append-only by construction.
* **Formal layer** — the strongest formal statement anywhere in the chain is a
  Lean proof spine under the standard `propext` / `Classical.choice` /
  `Quot.sound` axioms. Concrete stopped-model hypotheses remain human
  obligations. No Lean declaration in this repository proves `ASM-DOM`,
  `P9R-T2a`, or any numerical value.
* **Certified layer** — one interval, `Gamma_SR in [5.800391799508442,
  28.781285803081492]` for the frozen `m=1` SR. It certifies a number.

## 7. Novelty

```text
NOVELTY_STATUS = NOT_ESTABLISHED
```

P9R ran no new literature search. The earlier finite search of 2445 works with
zero `DIRECT` hits is prior-art evidence; it is not proof of novelty, and no
P9R document treats it as such.

## 8. Global closure

```text
LEVEL4_GLOBAL_CLOSURE = NO
```

`P9R = CLOSED_CANDIDATE`, if adjudicated, would close the Priority-9 **repair**
lineage. It would not repair P4, P5, P8, the mandatory global requirement
ledger, or `D-09`. Global Level-4 closure remains a separate, later audit.
