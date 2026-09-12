# P4Z final adjudication

```text
P4                      PARTIAL                        historical, immutable
P4Z                     CLOSED                         successor closure
P4_SCIENTIFIC_LINE      CLOSED_BY_LATER_SUCCESSOR

NEW_NUMERICAL_COMPUTE   NONE
```

`final_closure.json` is the machine-readable form of this document and wins if
the two ever disagree. Every pin is in `MANIFEST.json`, derived from the
repository by `build_manifest.py` rather than hand-copied.

---

## 1. Three statuses that must never be conflated

This packet asserts three different things about three different objects. Any
reading that collapses them is wrong.

| object | status | what it means |
|---|---|---|
| **P4**, the historical campaign | `PARTIAL` | P4's own frozen `closure_decision.json` records `PARTIAL` with three named gates false. That record is immutable and is not touched here. |
| **P4Z**, the successor line | `CLOSED` | The P4Z → P4ZA → P4ZB line is closed on its own terms: 96/96 cells governed under the unchanged frozen gate, and its outstanding governance questions independently adjudicated as admissible. |
| **the P4 scientific line** | `CLOSED_BY_LATER_SUCCESSOR` | All three of P4's originally failed gates are discharged by admissible later evidence. The *science* is closed; the *historical verdict* is not rewritten. |

**`P4 = CLOSED` is not asserted and is not implied.** A successor continues a
line; it never converts an earlier campaign's recorded verdict into a pass.

A fourth distinction matters just as much. `P4ZB_CLOSED` in
`p4zb_skewnormal4_k7/results/p4zb_successor_closure.json` is the **campaign's
own self-recorded verdict**. `P4Z = CLOSED` above is the **independent
integrated adjudication**. Both are retained; they are different statements by
different authors, and the record keeps them apart.

## 2. The three originally failed gates, and what discharges each

P4's `results/closure_decision.json` records `all_required_gates_pass = false`
with exactly three gates false. The discharge map is exact:

| # | original P4 gate | discharged by | Rule C? |
|---|---|---|---|
| 1 | `all_theorem_supported_cells_pass` | P4Z → P4ZA → P4ZB successor evidence, **96/96 PASS** | no |
| 2 | `all_outside_assumption_cells_demonstrate_failure` | P4X obligation **C4**, admitted obligation-locally | **yes** |
| 3 | `gaussian_consistency_with_closed_core` | P4X obligation **C5**, admitted obligation-locally | **yes** |

Machine-readable detail, including the per-obligation Rule-C findings, is in
`gate_discharge.json`.

### 2.1 Gate 1 — new measurement, no composition

The 96 cells are the exact Cartesian product fixed by the frozen
`P4_PROTOCOL.json`: 2 layers × 2 detectors × 6 theorem-supported families × 4
values of `m`. Every cell carries exactly one authoritative source — P4Z 44,
P4ZA 48, P4ZB 4 — with zero `COVERED_FAIL` and zero `INCONCLUSIVE`. Historical
P4X evidence appears as `corroborating_evidence` with
`confers_disposition: false` on every entry and is never a cell's sole
authority.

### 2.2 Gates 2 and 3 — obligation-local Rule C

A sub-obligation may survive a campaign-level governance failure only when its
evidence is independently identifiable, predates or does not traverse the
defective path, uses no tainted result-bearing computation, is reconstructible
without the defect, and has intact frozen provenance.

P4X's governance failure is the stage-2 top-up sharding, which touched the
single configuration `frozen/cusum@5/t1p5`.

- **C4** records `new_compute: NONE`. Its load-bearing evidence is analytic —
  the proved failure mode for a law without a first moment is *non-existence of
  the estimand*, not a Monte Carlo disagreement signature — supported by the Arb
  certificate. The defective path is not traversed.
- **C5** is arithmetic over frozen published anchors, using the correctly
  specified two-sample statistic `z = |e₁−e₂| / √(SE₁² + SE₂²)`. Its eight cells
  are Gaussian under `cusum@5` and `sr@520.886`; the sharded configuration is
  not among them. The anchor phase reproduced the frozen Route-A Gaussian
  estimates bitwise.

**P4X is not rehabilitated as a campaign.** Rule C is applied per obligation and
nowhere else. P4X's campaign-level governance outcome stands exactly as
recorded.

## 3. The numerical basis, at its strictest

The successor line adds a finite-difference truncation term `T_B` to the
uncertainty used by the `|z|` gate. Because `T_B` enters as
`SE_B = hypot(SE_B_mc, T_B)`, it *inflates* the z denominator and therefore
makes the frozen gate **easier**. Removing it entirely is the strictest reading
available from the stored artifacts:

```text
96 / 96 cells pass the frozen gate on Monte Carlo error alone
worst |z|                     1.787674614076624   frozen limit 4.0
worst relative discrepancy    0.009499604379      frozen limit 0.03
cells exceeding either gate   0
```

Reproduce with
`p4zr_rng_provenance_repair/audit/strict_gate_recheck.py`.

**No final disposition depends on the successor-added `T_B` convention.** This
is what makes the K7 question disclosure-worthy rather than closure-blocking.

## 4. The four adjudication inputs

### B1 — K7: `PASS_ADMISSIBLE`

K7 is a **successor-added precondition**. It does not appear in the frozen
`P4_PROTOCOL.json`; P4Z invented it, and the frozen gate it sits on top of is
unchanged. Its definition then changed across the line:

```text
P4Z    T_B = |R(0.2, 0.1)   - R(0.05, 0.025)|     non-adjacent pairs
P4ZA   T_B = |R(0.1, 0.05)  - R(0.05, 0.025)|     coarser adjacent neighbour
P4ZB   T_B = |R(0.05,0.025) - R(0.025,0.0125)|    finer adjacent neighbour
```

Each version was frozen **before its own result-bearing run** — verified at the
git object level: each freeze commit carries zero result blocks, and the blocks
appear only at the following commit. No original frozen P4 threshold changed at
any point; the K7 limit itself stayed at 0.02 throughout. P4ZB's reference pair
`(0.025, 0.0125)` is the frozen protocol's own `fd_ladder_fine`.

The adaptive diagnostic-development history is **deliberately preserved**, not
erased: `checkpoint_p4z.json`, `p4za_fullscope_closure/K7_DIAGNOSIS.md` and
`p4zb_skewnormal4_k7/SKEWNORMAL4_K7_ASYMPTOTICS.md` remain exactly as written,
including P4ZA's own record that it refused to widen the limit to admit the four
cells it could not clear.

### B2 — RNG provenance: `PASS`

Branch `p4zr-rng-provenance-repair`; full record in
`p4zr_rng_provenance_repair/RNG_ADDRESS_SEPARATION.md`.

```text
P4Z    RNG_ADDRESS_SEPARATION_FAIL   5 overlaps, 25 shared addresses
P4ZA   RNG_ADDRESS_SEPARATION_PASS   0 overlaps; 1 seed-namespace reuse
P4ZB   RNG_ADDRESS_SEPARATION_PASS   clean on both axes
```

P4Z carries a real same-campaign provenance defect: its pre-run diagnostics
seeded from the base of the production seed schedule, and on three of the five
overlaps the delivered innovations were byte-identical to production's.

P4ZA has **no** innovation-address collision. The same integer keys Philox in
calibration and PCG64 in production — different bit generators share no stream.
That is namespace and bookkeeping reuse, not an address collision.

Admissibility rests on a checked fact, not an argument from size: **zero
disposition-bearing final cells rely on overlapped P4Z evidence.** Both affected
configurations — `frozen/cusum@5/gaussian` and `frozen/cusum@5/laplace` — have
all eight of their cells authored by **P4ZA**, at disjoint addresses. The P4Z
blocks at the overlapping addresses were superseded and confer nothing.

The language is deliberate: **no observed disposition dependence**, and
**scientific impact bounded by** the facts in §3 and above. Not "harmless". Not
"no impact". Residual uncertainty is carried forward in §5 rather than
discharged.

### B3 — Rule C on P4X C4/C5: `PASS_ADMISSIBLE`

See §2.2. Obligation-local only.

### B4 — public presentation: `PASS`

Branch `codex/presentation-refresh`. The public surface now separates each
campaign's self-verdict from the independent closure status.

## 5. Residual uncertainty, carried forward

Closure does not mean the record is free of open questions. These remain on the
record and are not discharged by this packet:

1. The bound on the P4Z RNG overlap is an argument from what the calibrations
   recorded and from which campaign authored each cell. It is **not** a
   reconstruction of the counterfactual campaign that would have run on disjoint
   addresses, and no such reconstruction is offered.
2. P4Z's `fd_ladder` diagnostic records no seed in its artifact; its addresses
   are recoverable only from the source of `run_fd_ladder.py`.
3. The P4Z and P4ZA independent closure audits compared seed integers against
   predecessors and history only, so this defect class was structurally
   invisible to them at the time.
4. P4ZA's seed-namespace reuse shares no innovation but removes the margin that
   would make a later same-generator reuse obvious.
5. P4ZA relaxed its precision target from P4Z's self-imposed `0.0025` to the
   frozen `r*`, which makes the `z` gate easier. Disclosed in
   `CHECKPOINT_P4ZA.md` §5; achieved relative SE is about `r*/2`, and the
   strict-gate reconstruction shows nothing rides on it.
6. Closure is scoped to the frozen P4 theorem and its 96 theorem-supported
   cells, and says nothing about any wider claim.

## 6. Scope

```text
IN SCOPE      the frozen P4 theorem G1a, its 96 theorem-supported cells,
              and P4's three originally failed gates

OUT OF SCOPE  P5, P5Y, K1, PS1, Level-4 global closure, novelty,
              production readiness, and any claim beyond the frozen scope
```

No new numerical computation was performed for this adjudication. Every number
in this packet is recomputed from stored artifacts.
