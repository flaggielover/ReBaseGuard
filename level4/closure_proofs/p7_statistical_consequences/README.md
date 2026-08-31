# Level-4 Priority 7 — statistical consequences of recursive re-baselining

**Independent scientific verdict: `CLOSED`.
Repository integration: ready for the adjudicated checkpoint.**

P7 asks whether the recursive reference-state distortion established by the
closed P1/P2/P3 theorems has a measurable, practically meaningful consequence
for sequential monitoring. It does — a large one — but **not the one the local
stability boundary suggests**.

## The result in four lines

1. Re-baselining on stopping-selected data costs 83%–90% of the calibrated
   in-control ARL and inflates the mean detection delay for a unit shift by
   360%–540%; 40%–51% of the ARL loss is attributable to *reuse* specifically,
   measured against a fresh-reference control at the same window length.
2. The damage is a **tail**: the median delay is at or below nominal, but about
   one cycle in nine starts with a pre-shift dispersed reference that happens to
   lie near the post-change mean and is effectively blind to the shift.
3. The P3 critical reuse fraction `rho_c` has **no observable statistical
   signature**. The pre-committed boundary test returns
   `LOCAL-MATHEMATICAL, NOT OPERATIONAL`, extending Stage-D D2.5's verdict from
   the `m` direction to the `rho` direction.
4. The observed chains leave the grid-defined local neighbourhood by factors of
   roughly 8–19 at `rho=rho_c`. Conditional P7-C is consistent with escape into
   dispersion, but does not prove global stability or causally explain the
   negative boundary result.

## Reading order

| file | contents |
|---|---|
| `DEFINITION_AUDIT.md` | correspondence with the closed P1--P3 objects; every metric defined |
| `EXPERIMENT_DESIGN.md` | factors, controls, CRN policy, uncertainty method, and the pre-committed verdict criteria |
| `THEORY_BRIDGE.md` | the theory-to-consequence chain, statement by statement, with statuses |
| `STATISTICAL_CONSEQUENCES.md` | all measured evidence (generated) |
| `EVIDENCE_BOUNDARY.md` | what is and is not established, in P3's evidence hierarchy |
| `ADVERSARIAL_REVIEW.md` | the attacks run against these conclusions and what survived |
| `P6_HANDOFF.md` | what a mitigation must control, and what it must not target |
| `PROVENANCE.md` | seeds, sizes, inputs, file inventory |
| `CLOSURE_REPORT.md` | verdict against the P7 closure standard |
| `CODEX_HANDOFF.md` | independent-adjudication instructions |
| `INDEPENDENT_ADJUDICATION.md` | final independent verdict, corrections, and integration evidence |

## Reproducing

```bash
./reproduce.sh          # ~15 minutes; regenerates every result and figure
```

## Scope

P7 owns statistical monitoring consequences. It does **not** own period-2
orbits, attractors, basins, hysteresis or any global nonlinear dynamics (P5); it
does **not** design the safe re-baselining algorithm (P6); it does **not** run
the detector-family, distribution-family or drift-pattern robustness matrix
(P8). Observations touching those areas are recorded as handoffs.

Nothing in `m_gt_1_priority1`, `sr_derivative_priority2`,
`m_rho_stability_priority3` or the `PARTIAL` `p4_theory_generalization` is
read-write from here. P4's adjudicated SR replay is supplementary diagnosis
only; P7's conclusions rest on the closed P1--P3 alone.
