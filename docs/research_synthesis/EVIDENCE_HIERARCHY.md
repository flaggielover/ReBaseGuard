# Evidence hierarchy

Evidence labels state what supports a claim; they are not interchangeable.

| Label | Meaning in this synthesis |
|---|---|
| HUMAN THEOREM | A mathematical argument with explicit assumptions, not necessarily instantiated end to end in Lean. |
| LEAN-CHECKED | A compiled formal statement with the audited axiom baseline. It proves exactly its encoded conditional or concrete statement. |
| ARB-CERTIFIED | A rigorous numerical enclosure using outward-rounded interval arithmetic and an audited error chain. |
| CONFIRMATORY NUMERICAL | Frozen numerical or Monte Carlo correspondence; not a proof or certificate. |
| SEMI-REAL EMPIRICAL | Evidence from public sequential streams under frozen task protocols; not production validation. |
| NEGATIVE RESULT | A pre-specified scoped hypothesis was not supported or was falsified under an adequate frozen design. |
| INTERPRETATION | A synthesis-level consequence that must remain within the supporting claim scopes. |
| OPEN | An unclosed optional rigor item or future scientific extension. |

## Claim-level classification

| Major claim | Evidence | Scope and boundary | Authority |
|---|---|---|---|
| `m=1` derivative identity | HUMAN THEOREM + LEAN-CHECKED | Frozen Gaussian CUSUM and explicit moment/domination chain | `closure/02_THEOREM_MAP.md`; `rebaseguard-lean/RebaseguardLean/ReBaseGuardIdentity.lean` |
| `Gamma_CUSUM>2` | ARB-CERTIFIED | Frozen `k=1/2,h=5` CUSUM | `rebaseguard-proof/proofs/certificate.json` |
| CUSUM zero locally repelling | HUMAN THEOREM consequence of LEAN-CHECKED + ARB-CERTIFIED components | Deterministic conditional-mean map, local, `m=1,rho=1` | `closure/04_ARB_CERTIFICATE.md`; `closure/02_THEOREM_MAP.md` |
| Deterministic period-two orbit | HUMAN THEOREM + ARB-CERTIFIED | Unique only in stated root interval; deterministic skeleton | `level4/stage_b/certificate/period2_certificate.json` |
| Random-window `m>1` derivative | HUMAN THEOREM + LEAN-CHECKED conditional spine + CONFIRMATORY NUMERICAL | Track-1B Stage-D convention, finite fixed `m` | `level4/closure_proofs/m_gt_1_track1b/results/decision.json` |
| D4 `m`-`rho` map | HUMAN THEOREM consequence + CONFIRMATORY NUMERICAL | Protocol-specific deterministic local stability | `level4/closure_proofs/d4_phase_map/results/decision.json` |
| P3 policy result | CONFIRMATORY NUMERICAL + INTERPRETATION | Frozen CUSUM regimes and primary decision family | `level4/closure_proofs/l4r06_policy/results/scientific_findings.json` |
| SR derivative identity | HUMAN THEOREM + LEAN-CHECKED conditional spine + CONFIRMATORY NUMERICAL correspondence | Authoritative symmetric two-chart SR, `m=1` | `level4/closure_proofs/sr_derivative/results/decision.json` |
| `Gamma_SR>2` | CONFIRMATORY NUMERICAL | Not Arb-certified | `level4/closure_proofs/sr_derivative/FINAL_REPORT.md` |
| Rigorous SR local instability | OPEN | Optional Arb upgrade outside the original 18 rows | `level4/closure_proofs/sr_derivative/ARBITRARY_PRECISION_ATTEMPT.md` |
| Regular location-family derivative | HUMAN THEOREM + LEAN-CHECKED conditional spine + CONFIRMATORY NUMERICAL t3 correspondence | Explicit regularity and stopped analytic hypotheses | `level4/closure_proofs/location_family_track3ab/results/decision.json` |
| Operational-crossing answer | NEGATIVE RESULT | Frozen Gaussian CUSUM, grid, shifts, four metrics, 20,000 replicates | `level4/closure_proofs/l4r12_operational_crossing/results/evidence_assessment.json` |
| External validation | SEMI-REAL EMPIRICAL | Public sequential streams; task-level and regime-dependent | `level4/closure_proofs/external_validation_v3/CROSS_CAMPAIGN_AGGREGATION.md` |
| Novelty position N2 | INTERPRETATION from documented search audit | Search-scope hygiene; no absolute priority claim | `level4/closure_proofs/novelty_verification/results/decision.json` |
| L4R-13 non-Gaussian robustness | OPEN as Level-4+ work; current ledger status PARTIAL | Strong extension, nonmandatory | `level4/final_level4_closure/REQUIREMENT_LEDGER.md` |

## Load-bearing separations

Lean does not certify the value of `Gamma_CUSUM`; Arb does not prove
differentiation under the expectation. SR's numerical lower confidence bound is
not an Arb enclosure. Semi-real task support is not deployment evidence. A
negative operational-crossing result is not a universal impossibility theorem.
