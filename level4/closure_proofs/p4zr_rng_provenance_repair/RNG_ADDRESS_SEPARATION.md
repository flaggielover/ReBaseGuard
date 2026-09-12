# P4ZR — calibration/production RNG address separation in the P4Z successor line

```text
RECORD_TYPE       additive successor governance disclosure
RESULT_BEARING    NO
SCOPE             B2 only -- disclosure and future-audit protection
NOT_PERFORMED     B1 (K7 instrument adjudication), B3 (Rule-C ruling on P4X C4/C5)
DECLARES_CLOSED   nothing
P4_VERDICT        PARTIAL, unchanged, immutable
```

Every structural claim below is rebuilt from frozen artifacts on every test run
by `audit/build_rng_manifests.py` and checked by
`tests/test_p4z_line_rng_findings.py`. Nothing is hand-copied. The defective
historical scripts are left exactly as they are, as evidence of the defect.

---

## 1. The intended separation, and where it comes from

The repository already carries the correct standard. `P8R`
(`p8r_temporal_integrity_repair/RNG_ADDRESS_PLAN.md` §4) established four
disjoint RNG address classes and the required property

> calibration addresses cannot overlap production addresses

after the P8 adjudication failed gate `G14` in part because a calibration search
was rerun and then re-verified *at the same address the first verification had
used*. P8R makes that impossible **by construction**, for campaigns written
against its tag discipline.

The P4Z line predates that discipline and draws directly on the frozen
`p4_theory_generalization` addressing, so P8R's constructive guarantee does not
reach it. What the P4Z line also lacks is a **detective** equivalent. Every
`independent_closure_audit.py` in the line checks seed disjointness only
against *predecessor* campaigns and against history, by comparing bare seed
integers — for example P4ZB's check
*"seeds disjoint from P4Z, P4ZA, the ladder study and history"*. No campaign in
the line ever checked itself against its own calibration.

That is the gap this record closes, and `src/rebaseguard_p4zr/rng_address_audit.py`
is the check that was missing.

## 2. Address semantics

Fixed by `p4_theory_generalization/src/rebaseguard_p4_general/simulate.py` and
by the two frozen runners:

| route | construction | address |
|---|---|---|
| `rb_score` | `np.random.Generator(np.random.PCG64([seed, block]))` | `PCG64(key, batch)` |
| `rb_map` | `np.random.Philox(key=seed, counter=stream_counter(block, step))` | `PHILOX(key, batch, step)` |
| `fd_ladder` | same as `rb_map` | `PHILOX(key, batch, step)` |

`stream_counter(batch, step) = ((batch << 32) | step) * 2**64`. The `2**64`
stride reserves a full counter block per `(batch, step)`, so distinct
`(batch, step)` pairs never overlap and two programs collide **iff** they share
`(key, batch)` — at which point they share the whole step-indexed family. The
step axis therefore collapses exactly; it is not an approximation.

Three consequences the audit depends on:

- **A shared integer across different generators is not a shared stream.**
  `Philox(key=k, ...)` and `PCG64([k, b])` are different algorithms.
- **Draw length is irrelevant to collision.** Both generators deliver a prefix
  of one stream, so a program drawing 3 942 paths and one drawing 40 000 from
  the same address share 3 942 innovations *exactly*. A shorter draw is not a
  weaker collision.
- **A same-key, disjoint-batch partition is legitimate** — it is how P8R
  separates purposes inside one class — and is recorded, not flagged.

## 3. What was found

```text
P4Z    RNG_ADDRESS_SEPARATION_FAIL    5 overlaps, 25 shared addresses
P4ZA   RNG_ADDRESS_SEPARATION_PASS    0 overlaps; 1 seed-namespace reuse
P4ZB   RNG_ADDRESS_SEPARATION_PASS    0 overlaps, 0 namespace reuse
```

### 3.1 P4Z — five genuine address overlaps

| # | calibration program | address | batches | production configuration / route | same family? |
|---|---|---|---|---|---|
| 1 | `micropilots/run_micropilots.py` RB-SCORE candidate | `PCG64(4090001)` | 0–7 | `frozen/cusum@5/gaussian` `rb_score` | **yes** |
| 2 | `micropilots/run_micropilots.py` historical Route-A tail check | `PCG64(4090001)` | 0 | `frozen/cusum@5/gaussian` `rb_score` | **yes** |
| 3 | `micropilots/run_micropilots.py` RB-MAP candidate | `PHILOX(4090002)` | 0–3 | `frozen/cusum@5/gaussian` `rb_map` | **yes** |
| 4 | `micropilots/run_fd_ladder.py` RB-SCORE reference | `PCG64(4090101)` | 0–5 | `frozen/cusum@5/laplace` `rb_score` | no |
| 5 | `micropilots/run_fd_ladder.py` FD ladder | `PHILOX(4090102)` | 0–5 | `frozen/cusum@5/laplace` `rb_map` | no |

On rows 1–3 the calibration also ran the `gaussian` family, so the *values*
delivered to production were identical, not merely the underlying stream.
`tests/test_p4z_line_rng_findings.py::test_a_shared_address_delivers_identical_innovations`
demonstrates this rather than arguing it: production's step-1 draw is a
byte-exact prefix of the calibration's, on both bit generators.

On rows 4–5 the calibration ran `t1p5` against a `laplace` production
configuration, so the same stream was consumed through a different transform.
The address is still shared; the delivered values are not identical.

### 3.2 Root cause

`run_micropilots.py` defaults `--seed 4_090_001` and passes `seed + 1` to the
Philox-keyed route. `run_fd_ladder.py` hard-codes `seed = 4_090_101` and again
uses `seed + 1`. The frozen production plan derives its seeds as
`base + 100 * configuration_index` with bases `rb_score 4090001`,
`rb_map 4090002`, `fd_ladder 4090004`.

So the diagnostics did not pick arbitrary integers — they picked the *base* of
the production seed schedule. Configuration 0 is `frozen/cusum@5/gaussian` and
configuration 1 is `frozen/cusum@5/laplace`, and the diagnostics landed exactly
on their addresses. There was no separate calibration namespace at all.

### 3.3 Temporal chronology

All four P4Z pre-run commits carry **zero** result-bearing blocks; the 7 200
production blocks appear only at the result commit `298d916c`. The ordering
protocol-before-result is intact. The defect is not a temporal one: the
diagnostics ran *before* production, as intended — they simply ran in the
address space production would later use.

```text
d46fc684  estimator redesign; micropilot + fd-ladder diagnostics       0 blocks
e29e32a4  pre-run freeze (checkpoint_p4z.json)                         0 blocks
1a9a23df  pre-run correction: K5/K6 at their specified block count     0 blocks
f07021d3  producer-hash and TCB-scope invariants pinned                0 blocks
a134895f  bounded-survival lemma formalised                            0 blocks
31e1291e  Stage-0                                                      0 blocks
298d916c  result-bearing checkpoint                                7 200 blocks
```

### 3.4 P4ZA — seed-namespace reuse, not a collision

`audit/calibrate_ladder.py` uses `SEED = 4_190_001` for 60 blocks through the
Philox-keyed `rb_map_batch`. P4ZA production uses `4190001 + 100k` as
**`PCG64`** `rb_score` keys and `4190002/4190003 + 100k` as its Philox keys.
The integer `4190001` therefore appears in both roles, but never as a Philox key
in production, so **no innovation is shared**.

This corrects a stronger claim made in an earlier read-only audit, which
compared seed integers without separating the bit generators. Under the actual
address semantics P4ZA has no overlap. The reuse is still recorded: it removes
the margin that would have made a later same-generator reuse obvious, and it is
precisely the bookkeeping ambiguity that let the P4Z defect go unnoticed.

### 3.5 P4ZB — clean

`audit/ladder_study.py` uses `SEED = 4_290_001`; production uses
`4390001/4390002/4390003`. Disjoint on both the key axis and the generator axis.
P4ZB is the only campaign in the line that separated its study decade from its
production decade, and its own plan says so.

## 4. Why this violates the intended separation

A calibration program exists to choose a design parameter. If it inspects an
outcome at address `X` and production then evaluates at `X`, the chosen
parameter is correlated with the particular noise realisation production will be
scored on. The holdout is no longer a holdout. That is the mechanism P8R's
`G14` failure named, and the P4Z micropilots reproduce its address half.

What the P4Z calibrations actually fed:

| program | inspected | fed |
|---|---|---|
| `run_micropilots.py` | per-path sd, relative SE, Hill index, top-1/top-5 share, **point estimates**, and a two-sample `z` of the new estimators against the **P4X historical record** (`MICROPILOT_REPORT.md` §3.2) | `block_paths` per configuration, the K3 variance regime envelope, estimator choice |
| `run_fd_ladder.py` | central differences and Richardson values per `h`, **and an RB-MAP-versus-RB-SCORE offset** (`MICROPILOT_REPORT.md` §3.6) | the FD ladder design, the decision to keep the frozen `(0.05, 0.025)` pair, the rejection of a finer step |

This is recorded in full because two of those entries are stronger than
"precision only": the micropilots recorded **means**, and the FD-ladder
diagnostic recorded an **inter-route offset**. A disclosure that described the
calibration as having read only precision statistics would be inaccurate.

What no calibration program read, at any address:

- the correspondence gate statistic `z = |e_A − e_B| / sqrt(SE_A² + SE_B²)`;
- any cell's PASS / FAIL / INCONCLUSIVE disposition.

## 5. Bounded scientific impact

Four facts bound the exposure. None of them is a proof that the overlap changed
nothing.

**(a) The gate statistic was never read at a shared address.** The two quantities
the frozen gate decides on were not inspected by any calibration program.

**(b) The cells the calibration inspected and the cells whose addresses it
collided with are disjoint.** The micropilots ran `gaussian/cusum@2`,
`t1p5/cusum@5`, `t1p5/sr@520.886`, `t1p5/sr@20` and `t3/cusum@5`; the collisions
are with `frozen/cusum@5/gaussian` and `frozen/cusum@5/laplace`.

**(c) Neither affected configuration authors a final disposition.** Both were
left `INCONCLUSIVE` by P4Z — `frozen/cusum@5/gaussian` under K7,
`frozen/cusum@5/laplace` under K3 — and all eight of their cells are authored by
**P4ZA** in `final_coverage.json`. P4ZA drew from disjoint seeds and reports
`RNG_ADDRESS_SEPARATION_PASS`. The P4Z blocks at the overlapping addresses were
superseded and confer nothing. This is checked, per cell, by
`test_no_overlapping_address_confers_a_final_disposition`.

**(d) The strict-gate reconstruction leaves margin.** Re-deciding all 96
authoritative cells under the frozen gate with **every** successor-added
uncertainty allowance removed — `z` on Monte Carlo error alone, the `T_B`
truncation term excluded, which can only *raise* `|z|`:

```text
96 / 96 cells pass
worst |z|                    = 1.788    frozen limit 4.0
worst relative discrepancy   = 0.0095   frozen limit 0.03
```

Reproduce with `audit/strict_gate_recheck.py`. This bounds the exposure of any
convention dispute in the line; it is **not** the outstanding K7 adjudication.

### The residual dependence channel, stated rather than dismissed

P4ZA sized its blocks from *"P4Z Stage-0 measured per-path relative sd"*, and
P4Z Stage-0 for the two affected configurations spans blocks 0–19, which include
the blocks whose innovations the micropilot had already inspected. A path
therefore exists from the overlapping addresses to a P4ZA design parameter.

The transmitted quantity is a scalar precision statistic, which the frozen K3
trigger discipline explicitly permits a sizing rule to read
(`checkpoint_p4z.json`: *"K3, K5, K6 and K7 read precision and stability
statistics only"*), and P4ZA drew its own innovations from disjoint seeds. The
channel is real, narrow, and carries no discrepancy, no `z` and no gate outcome.

### Summary

```text
1. RNG/provenance defect exists                 YES -- 25 shared addresses in P4Z
2. Scientific bias risk                         bounded by (a)-(d) above
3. Any final disposition depends on it          no observed dependence
4. Residual uncertainty                         section 6
```

## 6. Residual governance risk

- The bound in §5 is an argument from what the calibrations recorded and from
  which campaign authored each cell. It is **not** a reconstruction of the
  counterfactual campaign that would have run on disjoint addresses, and no such
  reconstruction is offered.
- `micropilots/diagnostics/fd_ladder.json` records no seed. Its addresses are
  recoverable only from the source of `run_fd_ladder.py`. Provenance that lives
  only in a script is weaker than provenance recorded in the artifact.
- The P4Z and P4ZA independent closure audits checked seed disjointness only
  against predecessors and history, so this defect class was structurally
  invisible to them at the time. They are historical artifacts and are not
  modified here.
- P4ZA's seed-namespace reuse shares no innovation but removes the margin that
  would make a later same-generator reuse obvious.
- This record is authored inside the successor lineage it describes and has
  **not** been independently adjudicated.

## 7. What this record does not do

It does not close anything. It performs neither the independent adjudication of
the K7 instrument lineage (**B1**) nor the Rule-C ruling on whether P4X's C4 and
C5 obligations survive P4X's governance `FAIL` (**B3**), both of which remain
outstanding. It asserts no verdict of the form `P4Z = CLOSED`, and it leaves

```text
P4 = PARTIAL
```

exactly as it stands.

## 8. Future audit protection

`src/rebaseguard_p4zr/rng_address_audit.py` is reusable by any successor
campaign:

```bash
python -m rebaseguard_p4zr.rng_address_audit <campaign>_rng_manifest.json
```

It exits non-zero on `RNG_ADDRESS_SEPARATION_FAIL`. A future campaign declares
its calibration and production streams in a manifest of the shape in
`results/rng_manifests/`, and the audit proves same-campaign disjointness at
real address semantics — generator family, key, and batch range — rather than by
comparing bare integers against predecessor campaigns.
`tests/test_rng_address_audit.py::test_predecessor_only_check_misses_a_same_campaign_collision`
shows, on P4Z's own numbers, that the pre-existing check cannot substitute for
it.
