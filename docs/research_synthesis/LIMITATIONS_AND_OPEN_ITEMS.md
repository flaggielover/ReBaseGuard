# Limitations and open items

## Limitations of the closed result

| Item | Classification | Current boundary | Evidence |
|---|---|---|---|
| L4R-13 non-Gaussian robustness | Limitation; Level-4+ future work | Remains nonmandatory `PARTIAL`; the t3 frozen and stability-normalized estimands disagree and neither was selected post hoc. | `level4/final_level4_closure/REQUIREMENT_LEDGER.md`; `level4/stage_d/results/d3_nongaussian.json` |
| P2/P3 regime dependence | Limitation | P2 has descriptive advantages at `m=70,100`; external P2 safety varies by task; P3=P1 at saturated `m=100`. | `level4/closure_proofs/l4r06_policy/results/scientific_findings.json`; `level4/closure_proofs/external_validation_v3/CROSS_CAMPAIGN_AGGREGATION.md` |
| No universal operational phase transition | Limitation supported by a negative result | The D4 boundary is local and deterministic; 0/4 monitored metrics peaked at the crossing under the frozen protocol. | `level4/closure_proofs/l4r12_operational_crossing/results/evidence_assessment.json` |
| No production deployment | Limitation | External work uses semi-real/public sequential streams and frozen research protocols. | `level4/closure_proofs/external_validation_v3/FINAL_REPORT.md` |
| No detector independence | Limitation | CUSUM and one authoritative symmetric two-chart SR detector are treated; this is scoped cross-detector replication. | `level4/closure_proofs/sr_derivative/FINAL_REPORT.md` |
| No distribution-free theorem | Limitation | The general theorem requires regular one-dimensional location families, common-support behavior, and explicit stopped analytic hypotheses. | `level4/closure_proofs/location_family_track3ab/THEOREM.md` |
| Novelty scope | Limitation | N2 reflects documented sources and unavailable-index constraints; it is not absolute novelty or priority. | `level4/closure_proofs/novelty_verification/LIMITATIONS.md`; `level4/closure_proofs/novelty_verification/FINAL_REPORT.md` |
| Deterministic/stochastic gap | Limitation | Local multipliers and the period-2 certificate concern a conditional-mean skeleton, not the noisy chain's invariant law. | `level4/reports/STAGE_B_LEDGER.md`; `level4/closure_proofs/d4_phase_map/OPERATIONAL_BRIDGE.md` |

## Completed optional rigor upgrade

### Rigorous SR local-instability Arb certificate — `SR-GAMMA-CERTIFIED`

At terminal Level-4 closure, the SR derivative theorem was closed,
`Gamma_SR>2` had confirmatory numerical support, and the optional Arb upgrade
remained `OPEN`. The later additive upgrade closed the global degree-16 patch
covers, residual suprema, resolvent bound, and propagated enclosure. It now
certifies `Gamma_SR in [5.800391799508442,28.781285803081492]` for the
authoritative symmetric two-chart SR model. This changes no original ledger row
and does not broaden the detector or operational scope.

Historical sources: `level4/closure_proofs/sr_derivative/ARBITRARY_PRECISION_ATTEMPT.md`
and `level4/final_level4_closure/OPEN_ITEMS.md`. Current certificate:
`level4/closure_proofs/sr_derivative/certificate/GAMMA_CERTIFICATE.md`.

## Level-4+ future work

- Resolve L4R-13 with a precommitted estimand and rigorous or independently
  replicated non-Gaussian program; do not retrospectively select between the
  existing conflicting t3 quantities.
- Instantiate the concrete infinite-process analytic obligations in Lean for
  the regular location-family theorem: residual-path measurability and
  parameter independence, almost-sure finiteness/geometric tails, stopped
  change of measure, event-slice summability, integrability, and domination.
- Study stochastic-chain invariant laws and operational behavior directly if a
  future protocol asks that question; deterministic local theory alone cannot
  answer it.
- Test other detectors, thresholds, window conventions, and deployment
  settings only as new, explicitly scoped science.

These are future tracks, not unfinished mandatory Level-4 requirements.
