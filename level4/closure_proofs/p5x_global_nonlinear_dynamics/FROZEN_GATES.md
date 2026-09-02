# P5X frozen gates

Frozen at Checkpoint A, hashed into `PROTOCOL_DIGEST.json`, and chosen **before**
any production result exists. They test the P5X theorem honestly; they are not
inherited from P5 and they are not P5's gates renamed. P5's gates `G1`–`G20`
remain exactly as adjudicated and are neither re-run nor reinterpreted here.

Several gates admit more than one passing outcome on purpose. A campaign whose
gates can only be satisfied by the hoped-for answer is not a test.

| id | gate | pass condition | admissible outcomes |
|---|---|---|---|
| `G1` | **exact theorem statement frozen pre-result** | every path in `PROTOCOL_DIGEST.json` is byte-identical to the anchor commit, the anchor is an ancestor of `HEAD`, and the anchor commit contains no file under `results/` other than `results/integrity/protected_tree_manifest_pre.json` | pass / fail |
| `G2` | **local P3 correspondence correct** | the certified `R'_{D,m}(0)` enclosure contains `1 - GammaTilde_{D,m}`; for `(CUSUM, m=1)` and `(SR, m=1)` the certified enclosure of `1 - R'(0)` intersects the existing certified `Gamma` intervals `[3.9243482…, 27.8493821…]` and `[5.8003917…, 28.7812858…]` | pass / fail |
| `G3` | **global restoring/drift theorem proved** | `P5X-T4` certified in every frozen cell (`sup_e \|R\| <= R_max < 2`), and `P5X-T5` stated as its corollary with the explicit trapping interval | `PROVED_ALL_CELLS` / `PROVED_SOME_CELLS` (reported per cell) / `NOT_PROVED` |
| `G4` | **invariant-law linkage valid** | `P5X-T6` holds: the exact identity `L6` is written out, `s_min > 0` and `M_2 < infinity` are certified, and the two-sided bound on `E_pi[e^2]` is stated per `(D,m,rho)`; `P5-T7` is cited, never restated | `TWO_SIDED` / `UPPER_ONLY` / `NOT_ESTABLISHED` |
| `G5` | **detector-specific assumptions proved / certified** | for each detector separately: the accepted cover tiles `[0,12]`, every cell carries an enclosure and an acceptance reason, and the far-field lemma closes the tail | per detector: `CERTIFIED` / `PARTIAL(scope reported)` / `FAILED` — asymmetric outcomes are admissible |
| `G6` | **no hidden global monotonicity assumption** | no P5X proof path uses monotonicity of `\|R\|` in `\|e\|`, monotone drift, `sup_e E[tau\|e] = E[tau\|0]`, or global monotonicity of `s`; the secondary lobe is exhibited in the certified cover; any reported `eta` for `P5X-T8` is the first one obtained | pass / fail |
| `G7` | **Lean spine compiles** | `X1`–`X3` (and any further `X` written) compile sorry-free against the pinned toolchain with the audited axiom set, every declaration maps to a `P5X-T` id, and no Lean statement asserts a numerical value | pass / fail |
| `G8` | **certified interval checks pass** | every proof-path inequality is re-checkable by an independent auditor script from the stored artifact alone; no accepted cell is justified by a point evaluation; no proof-path artifact cites a Monte Carlo or floating-point-grid number | pass / fail |
| `G9` | **independent numerical correspondence agrees** | `E1`–`E3` of `EMPIRICAL_PLAN.md` run on a seed family disjoint from P5's, and every measured interval intersects the corresponding certified interval | `AGREE` / `TENSION(reported)` / `DISAGREE` — `DISAGREE` fails the campaign |
| `G10` | **no contradiction with P5 / P7 / P9R** | no P5X statement contradicts an adjudicated P5, P7 or P9R result; no P5 gate is re-run, reworded or reinterpreted; P5 remains `PARTIAL` in every P5X document and in the root status table | pass / fail |
| `G11` | **protected tree intact** | every tracked file outside the P5X namespace is byte-identical to `results/integrity/protected_tree_manifest_pre.json`; the two pre-existing untracked audit namespaces are listed with their content hashes and are unchanged; the P5 tree hash at `HEAD` equals its tree hash at `bb03c0e` | pass / fail |
| `G12` | **novelty not overclaimed** | `NOVELTY_STATUS = NOT_ESTABLISHED` appears in the results document; no document asserts E-strong (that the flip bifurcation causes the stationary dispersion), asserts that the skeleton 2-cycle is the measured bimodality, calls a certified enclosure an exact value, or describes far-field forgetting as a restoring drift | pass / fail |
| `G13` | **independent adjudication ready** | a single results document states, per `(D,m)` and per `rho` band, which of `P5X-T4`–`T9` hold, with tier labels, certified constants, the cover, the failure modes actually encountered, and an explicit `P5X_VERDICT in {CLOSED_CANDIDATE, PARTIAL_CANDIDATE, FAILED}` derived mechanically from `G1`–`G12` | pass / fail |

## Verdict semantics (frozen)

```text
P5X = CLOSED_CANDIDATE     iff G1,G2,G6,G7,G8,G10,G11,G12,G13 pass
                            and G3 = PROVED_ALL_CELLS
                            and G4 = TWO_SIDED
                            and G5 = CERTIFIED for at least one detector,
                                     and not FAILED for the other
                            and G9 = AGREE
P5X = PARTIAL_CANDIDATE    iff the integrity gates pass but a scientific gate
                            lands on an admissible weaker outcome
P5X = FAILED               iff any integrity gate fails, or G9 = DISAGREE
```

`G3 = PROVED_ALL_CELLS` with `G4 = TWO_SIDED` is the minimum that can be called
a global mechanism. `P5X-T7` (Level C) and `P5X-T8` (Level D) are **not** in the
`CLOSED_CANDIDATE` condition: they strengthen the result and are reported, but
the campaign deliberately does not make its verdict hostage to the optional
skeleton work.

## What no P5X outcome may do

Even `P5X = CLOSED_CANDIDATE` and a later `CLOSED` adjudication may **not**
change original P5's colour. The only admissible final synthesis is

```text
P5  = PARTIAL   (unchanged, permanent)
P5X = CLOSED
P5 scientific line = CLOSED_BY_SUCCESSOR_CAMPAIGN
```
