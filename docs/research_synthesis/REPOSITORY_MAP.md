# Reviewer-first repository map

A reviewer can audit the final story by topic rather than by campaign date.

| Question | Start here | Load-bearing detail |
|---|---|---|
| What is the final decision? | `level4/final_level4_closure/FINAL_REPORT.md` | `level4/final_level4_closure/results/final_decision.json`; `level4/final_level4_closure/REQUIREMENT_LEDGER.md` |
| How is protected history preserved? | `level4/final_level4_closure/STATUS_TRANSITIONS.md` | `level4/final_level4_closure/protected_hashes.json`; `level4/final_level4_closure/results/evidence_audit.json` |
| What is the frozen model? | `closure/01_FROZEN_MODEL.md` | `closure/02_THEOREM_MAP.md` |
| What exactly did Lean prove? | `closure/03_LEAN_VERIFICATION.md` | `rebaseguard-lean/RebaseguardLean/ReBaseGuardIdentity.lean`; `rebaseguard-lean/RebaseguardLean/StoppedLikelihood.lean`; `rebaseguard-lean/RebaseguardLean/IntegralBridge.lean` |
| Where is `Gamma_CUSUM>2` certified? | `closure/04_ARB_CERTIFICATE.md` | `rebaseguard-proof/proofs/certificate.json`; `rebaseguard-proof/proofs/enclosure.json` |
| Where is deterministic period two certified? | `level4/reports/STAGE_B_PERIOD2_CERTIFICATE_REPORT.md` | `level4/stage_b/certificate/period2_certificate.json` |
| What is the authoritative `m>1` theorem? | `level4/closure_proofs/m_gt_1_track1b/THEOREM.md` | `level4/closure_proofs/m_gt_1_track1b/LEAN_CORRESPONDENCE.md`; `level4/closure_proofs/m_gt_1_track1b/results/decision.json` |
| Why is Stage A different? | `level4/closure_proofs/d4_phase_map/DEFINITION_AUDIT.md` | `level4/closure_proofs/m_gt_1_track1a/FAILURE_DIAGNOSES.md` |
| Where is the D4 map? | `level4/closure_proofs/d4_phase_map/FINAL_REPORT.md` | `level4/closure_proofs/d4_phase_map/results/decision.json`; `level4/closure_proofs/d4_phase_map/OPERATIONAL_BRIDGE.md` |
| What is the P3 policy? | `level4/closure_proofs/l4r06_policy/POLICY_DEFINITION.md` | `level4/closure_proofs/l4r06_policy/results/scientific_findings.json`; `level4/closure_proofs/l4r06_policy/FAILURE_DIAGNOSES.md` |
| What was proved for SR at Level-4 closure? | `level4/closure_proofs/sr_derivative/FINAL_REPORT.md` | `level4/closure_proofs/sr_derivative/THEOREM.md`; `level4/closure_proofs/sr_derivative/lean/SRDerivative.lean`; `level4/closure_proofs/sr_derivative/ARBITRARY_PRECISION_ATTEMPT.md` |
| Where is the later SR Gamma certificate? | `level4/closure_proofs/sr_derivative/certificate/GAMMA_CERTIFICATE.md` | `level4/closure_proofs/sr_derivative/results/sr_residual_global_a.json`; `level4/closure_proofs/sr_derivative/results/sr_residual_global_b.json`; `level4/closure_proofs/sr_derivative/certificate/reproduce_closed_upgrade.sh` |
| Why does the historical 52-file freeze reject the 92-file current SR tree? | `docs/releases/SR_GAMMA_CERTIFIED_RELEASE_NOTES.md` | `docs/releases/SR_GAMMA_CERTIFIED_ARCHIVE_MANIFEST.md`; `scripts/verify_post_level4_archive.py` |
| What is the location-family theorem? | `level4/closure_proofs/location_family_track3ab/THEOREM.md` | `level4/closure_proofs/location_family_track3ab/PROOF_OBLIGATIONS.md`; `level4/closure_proofs/location_family_track3ab/lean/LocationFamilyTrack3AB.lean` |
| What happened to non-Gaussian robustness? | `level4/final_level4_closure/OPEN_ITEMS.md` | `level4/stage_d/results/d3_nongaussian.json` |
| What did external validation establish? | `level4/closure_proofs/external_validation_v3/CROSS_CAMPAIGN_AGGREGATION.md` | `level4/closure_proofs/external_validation_v3/results/decision.json`; `level4/closure_proofs/external_validation_v3/FAILURE_DIAGNOSES.md` |
| What is the negative crossing result? | `level4/closure_proofs/l4r12_operational_crossing/FINAL_REPORT.md` | `level4/closure_proofs/l4r12_operational_crossing/results/evidence_assessment.json` |
| What is the novelty position? | `level4/closure_proofs/novelty_verification/FINAL_REPORT.md` | `level4/closure_proofs/novelty_verification/results/search_manifest.json`; `level4/closure_proofs/novelty_verification/PRIOR_ART_MATRIX.md`; `level4/closure_proofs/novelty_verification/LIMITATIONS.md` |
| How do I reproduce the terminal state? | `level4/final_level4_closure/README.md` | `level4/final_level4_closure/reproduce.sh`; `scripts/verify_level_1_3.sh`; `scripts/verify_level_4.sh` |
| How do I reproduce the post-Level-4 SR upgrade? | `level4/closure_proofs/sr_derivative/certificate/GAMMA_CERTIFICATE.md` | `level4/closure_proofs/sr_derivative/certificate/reproduce_closed_upgrade.sh` |

Historical reports remain evidence and are not superseded as records of their
own campaign decisions. This synthesis only supplies the reviewer-first route
through them.
