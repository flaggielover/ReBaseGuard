# P5 -> P6 dependency audit

```text
P5_FINAL_VERDICT            = PARTIAL
P5_ADJUDICATION             = level4/closure_proofs/p5_nonlinear_dynamics/INDEPENDENT_ADJUDICATION.md
P5_CHECKPOINT               = bb03c0ea9ea34060c992b6d7f0390de6a3cf8108
BRANCH_IN_FORCE             = B  (CLOSED-but-narrowed content; campaign verdict PARTIAL)
P6_ENTRY_GATE_ITEMS_1_2_3   = CLEARED BY THIS DOCUMENT
```

This executes step 2 and step 4 of `P5_ADJUDICATION_CONTINGENCIES.md` section 5
against the **final** adjudication, and clears entry-gate items 1-3. It is the
entry audit before campaign execution, not a new planning phase.

Every `PROVISIONAL_P5` row of the pre-design ledger (`DEPENDENCY_LEDGER.md`
section 5) is re-tiered below. **No row is left at `PROVISIONAL_P5`.**

---

## 0. Which branch is in force

`P5_ADJUDICATION_CONTINGENCIES.md` keys its branches on the fate of **T7**, not
on the campaign verdict:

* Branch C's trigger is "T7's two-step Doeblin construction is rejected or
  materially narrowed". It was **not**: the adjudication states the whole-space
  two-step minorisation, unique invariant law, uniform geometric TV convergence,
  symmetry and *all positive moments* are established for each fixed
  `(D, m, rho)`, and independently reproduces the raw-mean identity to
  `6.66e-16` across 48 configurations.
* Branch A's trigger requires T8-T10 accepted as conditional theorems **as
  stated**. They were narrowed: the attracting-supercritical-flip
  classification, global 2-cycle uniqueness and the inference from `SNR -> 0` to
  operational featurelessness were all rejected or demoted to numerical
  evidence.

So **Branch B is in force**: the T1/T2/T5/T7/T11 distribution-control programme
is intact; every bifurcation-derived idea is discarded (there were none, by
construction, `X2`); `P7`/`P8`'s optimum values lose their status as prior
information and the `rho` grid rests on the *closed* P7 facts `S12`/`E2`.

Branch B was predicted to be "the cheapest branch for P6", and it is: no P6
design object is deleted, and no formulation changes.

**Two campaign-level qualifications that Branch B does not cover.**

1. P5's campaign verdict is `PARTIAL`, so under the ledger's own tier scheme
   every P5 fact is `AUTHORITATIVE_PARTIAL`, not `AUTHORITATIVE_CLOSED` --
   usable "with the narrowing recorded inline; never as the sole support for a
   headline". The adjudication explicitly licenses T1, T2, T3, T4/T5, T7 and
   T11 as P6 premises inside the frozen constant-policy Gaussian convention-A
   model, so the licence is direct rather than inferred. P6 complies with the
   headline rule structurally: **every P6 headline is a measured monitoring
   quantity**, and P5 premises appear only in the derivation of the method and
   in the theory chapter, each with its narrowing stated.
2. The adjudication's own "P6 must not" list is reproduced verbatim in section 3
   below and is enforced item by item.

---

## 1. Re-tiering of the pre-design ledger, section 5

Classification per the campaign brief: `SAFE` (usable as written),
`NARROWED` (usable in a restricted form, stated), `INVALID` (may not be used),
`REQUIRES_NEW_PROOF` (P6 must prove it itself before using it),
`EMPIRICAL_ONLY` (motivation and grid design only, never a premise).

| row | claim | adjudicated status | **P6 classification** | what P6 does |
|---|---|---|---|---|
| `P1` | **T7** unique invariant law, uniform geometric ergodicity, symmetry, all positive moments | EXACT THEOREM, **per fixed `(D,m,rho)`** | **NARROWED** for fixed-`rho` baselines; **REQUIRES_NEW_PROOF** for any adaptive policy | stationary language is used only for `B0`-`B4`; for SAW, `THEORY.md` **T6-B** proves the closed-loop analogue from scratch. `H7` is untouched by the verdict |
| `P2` | **T1** raw-mean identity `e_{j+1} = rho Rbar_j + (1-rho) fresh_j` | EXACT THEOREM; independently reproduced, max gap `6.66e-16`, 48 configurations | **SAFE** | it is the *derivation* of the method (`METHOD.md` section 3) and of `T6-A`/`T6-C` |
| `P3` | **T2** `E[e_{j+1}|e] = rho R(e)`, `Var = rho^2 S(e) + (1-rho)^2/m` | EXACT (given T1) | **SAFE** | the one-step quadratic `Q(rho) = rho^2 V + (1-rho)^2 nu` is exactly this, taken w.r.t. the *observable* sigma-field instead of `e` |
| `P4` | **T5** state-independent one-step moment bound | EXACT; constants "extremely loose", explicitly *not* uniform in `m`, `rho` simultaneously | **SAFE (structure) / EMPIRICAL_ONLY (constants)** | `T6-A` uses the *structure* (state-independence, uniformity over the decision box). The theorem constant is reported as `sup_x E_x[tau]` and the **measured** constant is reported beside it |
| `P5` | **T9/T10** flip bifurcation, `SNR -> 0` | branch existence/uniqueness CONDITIONAL on H2/H3; attraction, nondegeneracy and global-cycle claims **not proved**; inference from `SNR->0` to featurelessness **REJECTED** | **INVALID as a premise** (and unused: `X2`) | nothing in P6 references it. `rho_c` remains a figure annotation only (`X1`, `F15`) |
| `P6` | **T11** `ACF1 = rho(1 - Gamma_eff)` | EXACT THEOREM; the `0.0174` residual isolated as a gridded-map/PCHIP plug-in error, not a theory error | **SAFE, diagnostic tier only** | reported in Tier 3. Note it is *meaningless* under SAW, where `rho_j` is random -- stated in `LIMITATIONS.md` |
| `P7` | interior stationary-RMS optimum `rho* = 1.5x..4.9x rho_c` | NUMERICAL EVIDENCE, finite grid; near-ties in 3 of 8 cells; ratio range corrected to `1.5x-4.9x` | **EMPIRICAL_ONLY** | motivates nothing; the `rho` grid is justified by the *closed* `S12`/`E2`. `X9` still forbids the values as constants |
| `P8` | RMS/ARL co-optimality | "descriptive co-location, not a theorem"; P5 asks P6 to re-verify | **EMPIRICAL_ONLY, re-verified by P6** | `RESULTS.md` section 7 reports `argmin_rho Rms` and `argmax_rho Arl0` on P6's own grid and states whether they coincide |
| `P9` | `m` monotonicity | NUMERICAL EVIDENCE, `m <= 5`, listed metrics only; measured SNR *increases* with `m` | **EMPIRICAL_ONLY** | `m` stays a design variable; no direction is assumed. `X7`/`X8` (the `S14`/`P9` resolution) is restated wherever `m` is discussed |
| `P10` | one-step forgetting; bounded stress trajectories | **exact finite-`e` reset REJECTED**; T7 rules out divergence but **not** bounded sample paths | **NARROWED** | P6 keeps defensive guards: `RHO_MAX < 1` and a positive variance floor are *structural constants of the method*, not tuning knobs, and they are exactly what T6-B's minorisation needs |
| `P11` | `S(e)` varies ~8x | NUMERICAL EVIDENCE | **EMPIRICAL_ONLY -- and superseded** | P6 does not import `S`; it **re-measures its own** conditional-second-moment surface on `TUNE` seeds (`calibrate.py`), which is what `P5_ADJUDICATION_CONTINGENCIES.md` Branch A already advised even on a strong verdict |
| `P12` | deterministic flip / exact 2-cycle branch | CONDITIONAL on H2/H3; uniqueness among *all* cycles unproved; asymmetric cycles not excluded | **INVALID as a premise** | unused by construction (`X2`) |
| `P13` | platykurtic / bimodal stationary law | NUMERICAL EVIDENCE, four cells; onset interpolation has no interval | **EMPIRICAL_ONLY** | affects nothing; `X3` (no heavy-tail assumption) is not relied on either -- P6's tail metrics are empirical quantiles and exceedance counts |
| `P14` | detector-agnosticism of the map | "too strong"; finite-grid Monte Carlo with a systematic local linearisation difference | **EMPIRICAL_ONLY** | P6 **calibrates and evaluates each detector separately** and requires the effect to reproduce in each; no transfer is assumed |
| `P15` | T1 fails under a fixed-`m` denominator | EXACT (asserted by test) | **SAFE (a limitation)** | convention A is asserted by `tests/test_correspondence.py`; `X4` holds |

## 2. Consequences for P6-owned design objects

| P6 object | pre-design P5 dependence | status after the verdict |
|---|---|---|
| Method families **A, B, C, D, E** | none | **unchanged** (invariant `V5`) |
| Method family **F** (one-step risk control) | `P2`, `P3` | **PROMOTED TO DERIVED.** Both are EXACT, so the greedy inverse-variance rule is a derivation, not an empirical rule. This is the single most consequential effect of the verdict on P6, and it is why the campaign's candidate method is the *implementable* member of Family F rather than a Family A heuristic |
| **T6-A** one-step reference-risk bound | `P3`, `P4` | **REACHABLE, EXACT.** Proved in `THEORY.md` |
| **T6-B** closed-loop stationarity | `P2`, `P4`, and the *architecture* of `P1` | **REQUIRES_NEW_PROOF.** T7 is per fixed `(D,m,rho)` and does not transfer (`H7`, and the adjudication's "must not" item 1). `THEORY.md` proves it independently for memoryless policies with `rho <= rho_max < 1`; the memory-carrying case is left open |
| **T6-C** fresh-injection monotonicity | `P3` (one-step), `P1` + T6-B (stationary) | one-step half **EXACT**; the stationary half is folded into `T6-B` and the *dominance* statement replaces it as the campaign's headline theorem |
| **T6-D** tail bound | `P2`/`P3` | routes 1 and 3 available; route 2 (a sharp sub-Gaussian bound on the selected mean) remains **open** |
| **T6-E** Pareto statement | none for existence | unchanged; reported empirically |
| `OBSERVABILITY_AUDIT.md` in full | none (`V3`) | **unchanged**, including the `-GammaTilde` sensor gain, the increment-observability result and the `e_0` leak of section 4a |
| Baselines `B0`-`B11`, oracles `Z1`-`Z6` | none (`V4`) | **unchanged**; `Z1`/`Z2` are re-specified in `METHOD.md` as the oracle members of the SAW ladder, which is a strengthening, not a substitution |
| `EVALUATION_PROTOCOL.md` R1-R4 | none (`V6`) | **unchanged and mandatory** |
| `SAFETY_OBJECTIVES.md` tiers | none (`V2`) | **unchanged**; `S18`/`X6` still forbid concluding a monitoring gain from a reference-state gain |
| Stationary vs finite-horizon language | `P1` | **finite-horizon everywhere for SAW until T6-B is read as proved**; `T6-B` is proved in `THEORY.md`, so stationary language becomes legitimate for SAW *conditional on that proof surviving adjudication*. Every stationary claim in `RESULTS.md` is therefore double-labelled with its finite-horizon estimator, which is what the code computes in any case |

The `V1`-`V9` branch invariants of `P5_ADJUDICATION_CONTINGENCIES.md` section 0
were re-read after the verdict and **all nine still hold**.

## 3. The adjudication's "P6 must not" list, enforced

| # | prohibition (verbatim, abridged) | how P6 complies |
|---|---|---|
| 1 | T7 for state-dependent/adaptive policies without a new proof | `THEORY.md` T6-B is a new proof with its own hypotheses; the P5 architecture is cited, the P5 *result* is not transferred. The two places the new proof genuinely differs from T7 are named in `THEORY.md` section 4.3 |
| 2 | H2/H3, global one-crossing, global 2-cycle uniqueness, attraction, supercritical flip as exact premises | none appears anywhere in the campaign |
| 3 | T10 as proof that no statistic changes at `rho_c`, or as a causal proof of P7 | not used; `rho_c` appears only as a figure annotation |
| 4 | `rho* = 0.15-0.30`, `rho*/rho_c`, bimodality onset, `Gamma_eff`, detector transfer as design constants or safety thresholds | no P6 constant is taken from P5. The method's four constants are fitted by least squares on `TUNE` seeds inside P6; `c_beta` is derived from **P7's** closed response curve; `rho_max` and the variance floor are structural |
| 5 | exact RMS/ARL co-optimality, or a universal "larger `m` is better" theorem | neither is assumed; both are re-measured and reported with the `S14`/`P9` resolution attached |
| 6 | exact one-cycle reset at finite `|e|`, guaranteed bounded sample paths, or "guards can never be useful" | P6 keeps `rho_max < 1` and a positive variance floor as structural guards, and states that T7/T6-B rule out divergence but **not** unbounded excursions |
| 7 | any statement that P6's full campaign has started | superseded: this document is the entry audit, and the campaign is executed under it |

## 4. Entry-gate items cleared here

| item | status |
|---|---|
| 1 P5 verdict known | **MET** -- recorded verbatim in `results/p5_verdict.json` |
| 2 allowed premises listed | **MET** -- section 1 above; no row left at `PROVISIONAL_P5` |
| 3 rejected/narrowed material removed | **MET** -- sections 1-2; nothing needed deletion because nothing was built on `P5`, `P12` (the payoff of `X2`) |
| 4 primary objective selected | **MET** -- `EXPERIMENT_PROTOCOL.md` section 1 |
| 5 baselines frozen | **MET** -- `EXPERIMENT_PROTOCOL.md` section 3 |
| 7 metrics frozen | **MET** -- `EXPERIMENT_PROTOCOL.md` section 4 |
| 8 success criteria frozen | **MET** -- `CLOSURE_GATES.md` section 1 (C1-C10 verbatim; G-A..G-E options chosen) |
| 11 compute budget approved | **MET** -- `EXPERIMENT_PROTOCOL.md` section 7 |
| 12 correspondence X1-X5 at scale | **MET** -- `results/correspondence.json` |
| 13 fresh-sample cost model decided | **MET** -- primary `C_fresh = k_j 1{rho_j < 1}`; blind window; proportional variant as sensitivity (`EXPERIMENT_PROTOCOL.md` section 5) |
| 14 `c_beta` re-derived | **MET** -- `results/c_beta.json`, with the bracket width as the interpolation budget |
| 15 burn-in re-established per policy class | **MET** -- `results/burnin.json`, from the R3 curves |

## 5. One P6-owned artifact was edited, and why

`p6_safe_rebaselining_predesign/tests/test_scope.py` asserted that no worktree
change lies outside the *pre-design* namespace. The campaign namespace
`p6_safe_rebaselining/` is a legitimate P6 write, so the constant `NS` was
widened from one P6 namespace to the two P6 namespaces. **The semantics of the
assertion -- "P6 writes stay inside P6" -- are unchanged**, and the edit is
recorded here rather than made silently. No other pre-design artifact, and no
frozen P1-P5/P7 or Stage A-F artifact, was modified; `results/protected_tree.json`
records the check.

Note for the adjudicator: P5's own frozen gate **G20** (a conjunctive criterion
requiring the worktree scope to be P5-only) was already `FAIL` at P5
adjudication because the root `README.md` modification and the P6 pre-design
existed. The P6 campaign namespace adds a third item to the same, already-failed
conjunct. It does not change G20's verdict and it is not a new P5 regression.
