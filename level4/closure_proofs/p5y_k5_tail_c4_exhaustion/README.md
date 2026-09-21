# P5Y / K5 Campaign C4 — can deterministic operator-level exhaustion be established?

C4 answers one question left open by the independent C3 adjudicator: is there a certified **lower** bound on
`E_a[tau]` strong enough to prove that no certificate *of the admissible family* can ever close the remaining tail
cells? The family is defined in `config/FEASIBILITY_GATES_C4.json` — every supply whose `A0` is a valid *uniform*
order-0 bound on the cell. A route that bounded the order-0 point value for a *particular* residual rather than
uniformly over the unit ball would sit outside it, and C4 claims nothing about such a route.

It is a successor, not a continuation. C2 and C3 are complete and immutable; this namespace adds files and changes
none. `main` and the coverage maps r4 and r5 are unchanged, and Phase 0 checks all three. C4 contacted no remote
host at all, so it neither changed nor observed the AWS SR/PS1 estate — a statement about C4's actions, not a
claim about the estate's state, which C4 cannot make because the gate forbids it from looking.
`NEW_REAL_SCIENTIFIC_ADDRESSES = 0`; guard `REAL_SCIENTIFIC_COMPUTE = DENY`; no kernel is evaluated and no
operator certification is run.

| phase | artifact |
|---|---|
| 0 read-only audit | `evidence/phase0/C4_PHASE0_AUDIT.json` |
| 1 target reconstruction | `phase_1/C4_TARGET_RECONSTRUCTION.md`, `evidence/phase1/C4_THRESHOLDS.json` |
| 2 prior-evidence search | `phase_2/C4_PRIOR_EVIDENCE_SEARCH.md`, `evidence/phase2/C4_PRIOR_EVIDENCE.json` |
| 3 candidate routes | `phase_3/C4_CANDIDATE_ROUTES.md`, `evidence/phase3/C4_ROUTES.json` |
| 4 frozen gate | `config/FEASIBILITY_GATES_C4.json`, `evidence/freeze/C4_FREEZE_RECORD.json` |
| 5 pre-result review | `review/REVIEW_C4_PRERESULT.md` |
| 6 certificate | `evidence/certificate/C4_CERTIFICATE.json` |
| 7 adversarial check | `evidence/mutations/C4_MUTATIONS.json` |
| 8 adjudication | `evidence/adjudication/C4_ADJUDICATION.md` |

Post-freeze corrections live in `ERRATUM_C4_GATE.md`; the pre-result review and what was done about every one of
its notes are in `review/REVIEW_C4_PRERESULT.md` and `OPEN_NOTES_DISPOSITION_C4.md`.

Reproduce any number by running its producer in `code/`. Three producers carry pins and refuse without them:
`c4_model_identity.py` (the frozen CUSUM source sha plus the literal model-defining lines), `c4_certificate.py`
and `c4_mutations.py` (the frozen gate sha). `c4_lower_bound.py` refuses on a cover-ledger/registry disagreement
about the cell endpoints, and `c4_certificate.py` also refuses a (K, H) pair inconsistent with the frozen
`C_CUSUM = H + K`. The remaining producers — `c4_thresholds.py`, `c4_prior_evidence.py`, `c4_routes.py` — carry no
pin of their own and read committed evidence directly. `c4_phase0_audit.py` audits the *starting* state.
