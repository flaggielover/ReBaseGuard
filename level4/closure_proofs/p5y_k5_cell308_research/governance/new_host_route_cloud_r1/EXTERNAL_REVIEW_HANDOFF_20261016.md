# External review handoff B1 / B2 / B3 (Cell-308 Cloud route r1) — prepared for the owner to launch

**Status: PREPARED HANDOFF · NOT LAUNCHED · NO REVIEWER APPOINTED.** The checks below must be done by reviewers outside
the coordinator's reach:
* FR2 K3 and S12 Q8;
* the owner's continuation instruction of 2026-10-16: "An agent you launch inside your own coordinating environment
  does not satisfy a requirement for an owner-launched reviewer outside that environment."

The coordinator therefore prepares each handoff completely, and does not launch any of them.
`new_target_evaluations = 0` · `cell309_activity = none`.

## 1. The three handoffs

| id | purpose | brief (sha256) | pinned commit | runs after |
|---|---|---|---|---|
| **B1** | bounded conformance of the round-2 corrections, matrix R3, the register and the search determination (FR2 §7 conditions 1–9; S12 S1, S2, §5 items 1–14) | `ledger/briefs/B1_EXTERNAL_CONFORMANCE_CHECK_CLOUD_R1.txt` (`732922a543bda0e3be5fb304eaf8a5d751a5975a0fce1e152050473fa60d08e3`) | `f814fe84053bf8df61149e3d07bbc00aea50846c` | statement 1 |
| **B2** | narrowly scoped reading of `reviews/INCIDENT_INDEPENDENCE_REVIEW_MBS308.md`: N1–N4, T1–T6, T6's M1–M6 and Q4 premises, sanitised; whether T1 fires by construction | `ledger/briefs/B2_EXTERNAL_INCIDENT_REVIEW_READING_CLOUD_R1.txt` (`e7b9ca962aa6d2ff90e5b4980852352f3216c07d439bef9a0572e5c40d93c210`) | `f814fe84053bf8df61149e3d07bbc00aea50846c` | statement 1 |
| **B3** | non-holder provenance trace of every new constant and rule (package erratum E1 §3; N1, N2) and the T6 transfer finding | `ledger/briefs/B3_EXTERNAL_PROVENANCE_CHECK_CLOUD_R1.txt` (`222f8e1419055ce8a4ef706795196f6076ac28e72ca5c300a1aa1ae0c7802347`) | `f814fe84053bf8df61149e3d07bbc00aea50846c` | B2's released output |

Three different persons or sessions are needed. B2's reader takes no later role. B3 must not be B2.

## 2. How the owner launches each one (the exact external action)

1. Choose the reviewer: a **human**, or a **Claude session started under an account other than the one running this
   coordinator session**. A session on the same account does not qualify, because the coordinator's tools
   (`list_sessions`, `list_events`) can read it.
2. Give the reviewer only its brief. The text is public at
   `https://raw.githubusercontent.com/flaggielover/ReBaseGuard/<commit of this file>/level4/closure_proofs/p5y_k5_cell308_research/ledger/briefs/<brief>`.
   Record the appointment (identity, brief sha256, date) in the owner's own record.
3. Receive the reviewer's phase-1 eligibility statement, record it, and tell the reviewer to begin phase 2.
4. Receive the output file and its sha256 directly from the reviewer.
5. **B2 only:** check that no quoted passage reports a target-run figure. Only then release it.
6. Release the output: push it to branch `owner-review/cell308-<B1|B2|B3>` as `reviews/external/<file>`, and state
   its sha256 in the owner's record. Or hand it to the coordinator in this session, with its sha256.

## 3. What the coordinator does on release

1. Verify the file's sha256 equals the owner's stated digest. Stop on any difference.
2. For B2: run the tail-figure scan. Any hit means the output goes back to the owner unrecorded.
3. Record the output verbatim under `reviews/external/`, with a ledger line.
4. Make bounded corrections for concrete findings. Ask the same reviewer once, through the owner, to confirm them.
   There is no further round.
5. Update the findings register: VC is reached only for items the reviewer marks MET.

## 4. Pinning

The briefs' allowlists give each file's sha256 at the pinned commit `f814fe84053bf8df61149e3d07bbc00aea50846c`. Reviewers fetch files by raw URL at that
commit only, and never clone or list the repository. The incident review's sha256 in B2 comes from
`ROUTE_PREPARATION.md` line 69; the coordinator has not hashed or opened that file.

## 5. Source bindings for owner package r3 (sha256 at `f814fe84053bf8df61149e3d07bbc00aea50846c`)

| path | sha256 |
|---|---|
| `level4/closure_proofs/p5y_k5_cell308_research/governance/new_host_route_cloud_r1/PROPOSED_ROUTE_AMENDMENT_CLOUD_R1_A1_R5.md` | `d0963b110baab7beb86fa80184b9ebf2aab21362d7c7e35745fc10b06f9ba933` |
| `level4/closure_proofs/p5y_k5_cell308_research/governance/new_host_route_cloud_r1/PROPOSED_ROUTE_AMENDMENT_CLOUD_R1_A1_R5_ERRATUM_E1.md` | `b47286544b7f5c7e45e95b37bd1bdb0c9a6889fae4325cbcf081fe00deaaf41b` |
| `level4/closure_proofs/p5y_k5_cell308_research/governance/new_host_route_cloud_r1/PROPOSED_ROUTE_AMENDMENT_CLOUD_R1_A1_R5_ERRATUM_E2.md` | `a9d616fb84fffefe42ede75c6e90735da23b3c6309463f81d8954ff9f4b26353` |
| `level4/closure_proofs/p5y_k5_cell308_research/governance/new_host_route_cloud_r1/FORMAL_ROUTE_READINESS_PACKET_20261016.md` | `078f2ab2ef68bfc73f0c90862aaadc44ef0983a450b6b691303ebb13e1b17a3b` |
| `level4/closure_proofs/p5y_k5_cell308_research/governance/new_host_route_cloud_r1/LDET_SPECIFICATION_PACKET_20261016.md` | `f0f367a968279d24ac7e6c59e2e1579a4beffb23bc8aff04894cf2a5fa1180e4` |
| `level4/closure_proofs/p5y_k5_cell308_research/governance/new_host_route_cloud_r1/LDET_SPECIFICATION_PACKET_ERRATUM_E1_20261016.md` | `363985444155f05a5e1401bc3f487f3afc9aa2bd9fb29c24417c43e9c706969c` |
| `level4/closure_proofs/p5y_k5_cell308_research/governance/new_host_route_cloud_r1/LDET_SPECIFICATION_PACKET_ERRATUM_E2_20261016.md` | `7ac19ade1c103930264509000d2d81978bf90b3a66face90c7b4cd56d384171b` |
| `level4/closure_proofs/p5y_k5_cell308_research/governance/new_host_route_cloud_r1/PROPOSED_LDET_REFERENCE_ADDENDUM_R1_20261015.md` | `4efcd152127abf18ab9bc412ee2883465cfd841e63ed847e54aef4cc15fc5277` |
| `level4/closure_proofs/p5y_k5_cell308_research/governance/new_host_route_cloud_r1/HOST_EVIDENCE_PLAN_H1_H8_20261016.md` | `901a05d746a5e79daefe2974d76b5dce8306e333b22719a28c32d34355b64ec8` |
| `level4/closure_proofs/p5y_k5_cell308_research/governance/new_host_route_cloud_r1/HOST_EVIDENCE_PLAN_H1_H8_ERRATUM_E1_20261016.md` | `f871b9a28bf7ab7fa288e66a1afd635e71edfd8ab40502b127700f603e47adde` |
| `level4/closure_proofs/p5y_k5_cell308_research/governance/new_host_route_cloud_r1/HOST_EVIDENCE_PLAN_H1_H8_ERRATUM_E2_20261016.md` | `6e9392ac7658f4c4221b9bbb04198e221008ba940255cc8ad8ff98e7c9d2fd28` |
| `level4/closure_proofs/p5y_k5_cell308_research/governance/new_host_route_cloud_r1/HOST_ATTESTATION_ACCEPTANCE_PROCEDURE_20261016.md` | `91e61e8d83710461ae102ac88e98e8a5cc45f0d28ece4d7eff5d823310520322` |
| `level4/closure_proofs/p5y_k5_cell308_research/governance/new_host_route_cloud_r1/HOST_ATTESTATION_ACCEPTANCE_PROCEDURE_R2_20261016.md` | `e0531255309305a65c2fea5d58b946b41bbc4f04d75ba3b3cd6d4b3cabcc9ca5` |
| `level4/closure_proofs/p5y_k5_cell308_research/governance/new_host_route_cloud_r1/HOST_ATTESTATION_ACCEPTANCE_PROCEDURE_R3_20261016.md` | `e4376ee177530eaf45ca784713c660e421d347c39a08430004c2e1ce46954637` |
| `level4/closure_proofs/p5y_k5_cell308_research/governance/new_host_route_cloud_r1/CONSOLIDATED_DSTAR_PACKAGE_R2_20261016.md` | `038278fe77190ff2774404496688bba9bdb1bddc928790722d6e2f9ee50dea5f` |
| `level4/closure_proofs/p5y_k5_cell308_research/governance/new_host_route_cloud_r1/CONSOLIDATED_DSTAR_PACKAGE_R2_ERRATUM_E1_20261016.md` | `a71e277a5a654022318af99f8d6a7c994a36b8885db5420faddf3d0681a50b81` |
| `level4/closure_proofs/p5y_k5_cell308_research/governance/new_host_route_cloud_r1/FR1_DISPOSITION_20261016.md` | `82165a88b8ff02c66229baf433eb8c5f9833c4b2e55e718caf11dcabcdfc0148` |
| `level4/closure_proofs/p5y_k5_cell308_research/governance/new_host_route_cloud_r1/S12_FR2_DISPOSITION_20261016.md` | `c46a4f261985200629686190b018f7fc2b67ddc3dd3a6609acce6ef2f4a11efe` |
| `level4/closure_proofs/p5y_k5_cell308_research/governance/new_host_route_cloud_r1/READINESS_MATRIX_R2_20261016.md` | `3c1345d8d770f43722e45661cc566999a4ea80eba6f61a2454f167aebf8f3648` |
| `level4/closure_proofs/p5y_k5_cell308_research/governance/new_host_route_cloud_r1/READINESS_MATRIX_R3_20261016.md` | `61973f2c0da23d192f939dd31c399030d0ebff6e87f1c39bf779389c1a81f5dd` |
| `level4/closure_proofs/p5y_k5_cell308_research/governance/new_host_route_cloud_r1/FINDINGS_STATUS_REGISTER_20261016.md` | `5aa3e0e1d41bc48ebc953a355323ed5d9cef145b911f1737dc664ae4cc7cb4b4` |
| `level4/closure_proofs/p5y_k5_cell308_research/governance/new_host_route_cloud_r1/REVIEWER_SEARCH_ELIGIBILITY_DETERMINATION_20261016.md` | `b1b4cc102a5844a4eda6876056ad3fe91f8a5877437c2341e1fc55534e9491a6` |
| `level4/closure_proofs/p5y_k5_cell308_research/governance/new_host_route_cloud_r1/NEW_CONSTANT_RECOMMENDATIONS_20261016.md` | `fcac5f09a09ec33518c9940264c00600066afa16068c526526a4e3f9f8eb10fc` |
| `level4/closure_proofs/p5y_k5_cell308_research/governance/new_host_route_cloud_r1/OWNER_DECISION_PACKAGE_R3_20261016.md` | `ef356fdba41857bf86a5c7970232c90f1a26afa8fbe1089e160d794cfb1656d5` |
| `level4/closure_proofs/p5y_k5_cell308_research/governance/new_host_route_cloud_r1/OD1_HOST_RECOMMENDATION_20261016.md` | `6fc4a909af7b1d8d82c22d0a86090aaa144c07e683588415367da1d712fd76cd` |
| `level4/closure_proofs/p5y_k5_cell308_research/governance/new_host_route_cloud_r1/USER_AUTHORIZATION_20261016_OD2.md` | `5fc05b387f76992b0e2a1467d3a15241048898de939bf2f2e9c2d6a17a588fb4` |
| `level4/closure_proofs/p5y_k5_cell308_research/governance/new_host_route_cloud_r1/USER_AUTHORIZATION_20261016_OD2_VERBATIM_SUPPLEMENT.md` | `94a888814896e42e6ad96959285e1af09e8cda1397155c924df006992efbbd88` |
| `level4/closure_proofs/p5y_k5_cell308_research/governance/new_host_route_cloud_r1/ROUTE_PREPARATION.md` | `80c9f5a07191592b0d606cc713708ababd62acd4e8fd7b481ec08411f4b3be99` |
| `level4/closure_proofs/p5y_k5_cell308_research/governance/new_host_route_cloud_r1/OPERATIONAL_WRAPPER_READER_PINPOINT_REQUIREMENTS_20261016.md` | `bea16c62ec907c80d958d49afb5b6ed6ad5fbf4426c4bc83c5e35f2559a16abf` |
| `level4/closure_proofs/p5y_k5_cell308_research/reviews/REVIEW_FORMAL_ROUTE_CLOUD_R1_FR1.md` | `af150ef4493f2601a7a17ecbecebc02ae4f237e3f3fcfe5914d0e11af704b6df` |
| `level4/closure_proofs/p5y_k5_cell308_research/reviews/REVIEW_S12_RISK_CLOUD_R1.md` | `9d549eb2ad8aa9f72f49712961610b6f12b813d33eaa587dfa4f259862b2b55c` |
| `level4/closure_proofs/p5y_k5_cell308_research/reviews/REVIEW_FORMAL_ROUTE_CLOUD_R1_FR2.md` | `1ad769bbd35c1d4f7fbf2a47ba0b7bd907169c962795939613ed03adc9868cac` |
| `level4/closure_proofs/p5y_k5_cell308_research/ledger/briefs/S12_RISK_REVIEW_CLOUD_R1.txt` | `d46c19f7d82905d36f643ac7f003d7130835c4b9868c50ee9939467398a3710d` |
| `level4/closure_proofs/p5y_k5_cell308_research/ledger/briefs/FR2_formalROUTE_CONDITIONS_CHECK_CLOUD_R1.txt` | `77cf992d7d268fc8c9b9169c4051600f5c2ba933bd10dfe512df23e20d2b9589` |
| `level4/closure_proofs/p5y_k5_cell308_research/governance/SUCCESSOR_GOVERNANCE_308.md` | `4e9e6ad414ddcc38b5561f06d13cddc534e2956bb1fbeba46bff9fb23982278e` |
| `level4/closure_proofs/p5y_k5_cell308_research/governance/SUCCESSOR_GOVERNANCE_308_ADDENDUM_A1.md` | `c170c726c43601ee8c3d028a64b0639708c8b5799698aaf1ced62f5a13ee152c` |
| `level4/closure_proofs/p5y_k5_cell308_research/governance/SUCCESSOR_GOVERNANCE_308_ADDENDUM_A1_ERRATUM_E1.md` | `a1972ad3cbd7d59d431724e32fa45ecf3edece36e9251c607b241d7f160c224c` |
| `level4/closure_proofs/p5y_k5_cell308_research/governance/CONSTANTS_RATIFICATION_MBS308.md` | `caa742100ed5362e68d2444e1f4bc4ef2c3aac2084d72f406fa373fb1f2316ae` |
| `level4/closure_proofs/p5y_k5_cell308_research/governance/USER_DECISION_BRIEF_308_SUCCESSOR_R2.md` | `cda3cf4509dcc327cb4ba407c9afd435308f58d085a03aa85296737bc80fad9c` |
| `level4/closure_proofs/p5y_k5_cell308_research/governance/SUCCESSOR_CONDITIONS_REGISTER_308.md` | `a8a278b35791c684dd29a22879276a775cc39f393f2ef5cf74a206a76aea20bb` |
| `level4/closure_proofs/p5y_k5_cell308_research/registry/SUCCESSOR_ROUTE_AUDIT_308_ADDENDUM_A1.md` | `84379c99a25d32cf6232dde185592d274141e7847726c3e167cb61efbb3e5162` |
| `level4/closure_proofs/p5y_k5_cell308_research/registry/SUCCESSOR_ROUTE_AUDIT_308_ADDENDUM_A1_ERRATUM_E1.md` | `173bd4f9cddab7112ad732b0fff19c9250fd151b4329489c60946062f0d277d8` |
| `level4/closure_proofs/p5y_k5_cell308_research/registry/SUCCESSOR_ROUTE_AUDIT_308_ADDENDUM_A1_ERRATUM_E2.md` | `620bfbb946e190102e4f107ef8b666ad5de96bb87ef4064e3a7ce7239367a5c1` |
| `level4/closure_proofs/p5y_k5_cell308_research/streams/CLOUD_R1_LINUX_DEV/lx_platform.py` | `da32ce8c85d4236c33c99a0490a6fd559bbe113fcb7758802d533f4c0c9f6389` |
