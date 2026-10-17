# Dependency and evidence handoff after the B3 confirmation (Cell-308 Cloud route r1)

**Status: PREPARED HANDOFF · NOTHING APPOINTED, COMMISSIONED, ADOPTED OR EXECUTED.** This file names the first
remaining external requirement on the path to the T6 ruling and the D-* decisions, together with its exact permitted
scope, bindings, eligibility and authority, and then the steps that follow it. Every binding is at commit `58769a0f39014a43be984773de0f39f9fc8d469d`.

Missing facts are marked **MISSING**. None of them is invented here. `new_target_evaluations = 0` ·
`cell309_activity = none`.

## 1. Where the route stands

| item | state |
|---|---|
| B3 round | **complete**: report `16188ffd…e96a`; one confirmation `6a721ada…253c` (CONFIRMED_WITH_EXCEPTIONS / PARTLY / TRANSFERS_UNMET). No further B3 round |
| open findings | YC1, YC2 (BLOCKING); YC3 (MAJOR); YC4 (MINOR). Author corrections only (matrix R4 erratum E5, row A9a) |
| T6 | transfer **UNMET**; applicability **undecided**; role-holder status **UNVERIFIED** |
| owner statements | statement 1 (rows A3, A10) is **open** and may issue at any time; statement 1B (owner package R4 erratum E2 §E2.1) is ready to issue |
| formal operation | **not ready.** No host, implementation, OD-3, S1 or grant exists |

## 2. The dependency chain (first item first)

| step | requirement | actor | blocked on |
|---|---|---|---|
| **1** | **ER-T6 r2: a bounded register lookup per individual identifier** (row A14a) | **the owner personally, or an existing listed holder the owner specifically authorizes** | the owner fixing the sources' bindings (§3) |
| 2 | the owner's eligibility determination (row A14b), weighing Q1–Q5 of ER-T6 r2 §2 | owner | step 1 |
| 3 | the policy-provenance trace (row A6b) of the NT / NV items in the policy inventory | an eligible non-holder, appointed by the owner, outside the coordinator's reach; their own register lookup comes first (step 1's reader, same form) | steps 1–2 (the reviewer's standing) |
| 4 | statement 1A (material change; S12X if "material") | owner (and the external rater, if one runs) | B3's corrections being recorded (done) |
| 5 | statement 2: the T6 ruling items 3–4, adoption, D-*, N1 / N2, MBS-6/7/8 | owner | steps 1–4; A14p if the prospective package is adopted |
| 6 | statement 3, then OD-1 and the host stage | owner | step 5 |

Statements 1 and 1B can be issued in parallel with step 1.

## 3. Step 1 in full: ER-T6 r2

**Governing requirement.** T6 and S13: no E1″ holder may hold a successor route, implementation, caps or
qualification role. Every non-holder requirement on this route rests on knowing what the register says. B3 YC2
requires that this be a bounded lookup with explicit identity limits.

**Recommended resolution.** The owner performs the lookup personally, against the E1″ register and the MBS-1 location
list, and records one result per row of ER-T6 r2 §3. The owner is the register's authority. Doing it personally avoids
exposing a fresh reader to the register to create eligibility.

**Exact artifacts and scope.**

| artifact | binding |
|---|---|
| the request | ER-T6 r2 (row below) |
| the E1″ register (governance A1 S13: `ledger/COORDINATOR_EXPOSURE_DISCLOSURE.md`) | path as stated in S13. Commit pin: **MISSING**. Raw-byte sha256: **MISSING**. The owner fixes both in their own record before reading. The coordinator side does not hash or read it |
| the MBS-1 location list | path: **MISSING**; pin: **MISSING**; sha256: **MISSING** (whether it is part of the register is unknown to the coordinator side) |
| identifiers | ER-T6 r2 §3, individually. R1b and R3c are CANNOT_TELL in their mapping by construction |

**What the reader must not do:**
* read anything else;
* quote any observation, value or figure;
* report group results;
* use NOT_LISTED as a default for an unmatched row.

**Output.** `READING_EXTERNAL_ER_T6_ROLE_HOLDERS.md`, as ER-T6 r2 §4 specifies. The owner releases it with its sha256.
The coordinator side records it verbatim after its tail-figure scan.

**What it establishes.** A bounded register result only. It **clears nothing** by itself (ER-T6 r2 §5).

| binding (step 1) | bytes | sha256 |
|---|---|---|
| `level4/closure_proofs/p5y_k5_cell308_research/governance/new_host_route_cloud_r1/EVIDENCE_REQUEST_ER_T6_ROLE_HOLDER_CHECK_R2_20261017.md` | 6868 | `fac34cb9cc3dcd52745ebb50a81dfc64d33ab27c3c54a89cecf00b704d3acf0a` |
| `level4/closure_proofs/p5y_k5_cell308_research/governance/new_host_route_cloud_r1/OWNER_DECISION_PACKAGE_R4_ERRATUM_E2_20261017.md` | 4339 | `311fd91233125ed3370a61dcf8b7c427e57182c57f388e4c9366586b12977c15` |
| `level4/closure_proofs/p5y_k5_cell308_research/governance/new_host_route_cloud_r1/READINESS_MATRIX_R4_ERRATUM_E5_20261017.md` | 4821 | `0d8a129c9489694b11e5302426290be58bac84b3cbe79415deafae9614790067` |

## 4. Step 3's scope, prepared but not commissioned (A6b: policy-provenance trace)

**Governing requirement.** S12 §5 item 8 and B3 YC1: provenance before the D-* decisions, for every new policy number,
threshold, limit or rule.

**Task.**
* Trace each NT / NV item of the policy inventory §2 (a6–a14, a16, a20–a23, and the untraced parts of a17–a19) to its
  stated origin, or record it as a free choice.
* Identify any policy choice the inventory missed in the allowlisted texts.
* Report missing primary sources as missing. This is not a review of the D-* merits.

**Eligibility.** All of the following:
* fresh;
* outside the coordinator's session, account and control;
* not B1, B2 or B3, and not any coordinator session;
* the step-1 register lookup run on them before they start;
* the owner's eligibility determination for that appointment;
* appointed by the owner.

**Allowlist** (fetch by raw URL at `58769a0f39014a43be984773de0f39f9fc8d469d` only, and verify each hash first):

| path | bytes | sha256 |
|---|---|---|
| `level4/closure_proofs/p5y_k5_cell308_research/governance/new_host_route_cloud_r1/POLICY_PROVENANCE_INVENTORY_YC1_20261017.md` | 8684 | `c69ba89d815727a5f8117a1a5974f6185efad4f6b9bda1f59405171eb5ca300d` |
| `level4/closure_proofs/p5y_k5_cell308_research/governance/new_host_route_cloud_r1/OPERATIONAL_WRAPPER_READER_PINPOINT_REQUIREMENTS_20261016.md` | 8250 | `bea16c62ec907c80d958d49afb5b6ed6ad5fbf4426c4bc83c5e35f2559a16abf` |
| `level4/closure_proofs/p5y_k5_cell308_research/streams/CLOUD_R1_LINUX_DEV/lx_platform.py` | 88838 | `da32ce8c85d4236c33c99a0490a6fd559bbe113fcb7758802d533f4c0c9f6389` |
| `level4/closure_proofs/p5y_k5_cell308_research/governance/new_host_route_cloud_r1/PROVENANCE_DISPOSITION_RECORD_B3_20261016.md` | 14529 | `f8987a938a80dd0189ab1af7fc4f80ed01cae02f6d20dff39b3416eae8012046` |
| `level4/closure_proofs/p5y_k5_cell308_research/governance/new_host_route_cloud_r1/PROVENANCE_DISPOSITION_RECORD_B3_ERRATUM_E1_20261017.md` | 4155 | `c1bcc142c309929026cdc22c63806b47078c7cd843461000fd93f0a8580ba008` |
| `level4/closure_proofs/p5y_k5_cell308_research/governance/new_host_route_cloud_r1/CONSOLIDATED_DSTAR_PACKAGE_R2_ERRATUM_E2_20261016.md` | 7261 | `95d4581c2ccf3245aac47012b582e1f80c909f525cad9e38fbbd74b7a8362252` |
| `level4/closure_proofs/p5y_k5_cell308_research/governance/CONSTANTS_RATIFICATION_MBS308.md` | 22783 | `caa742100ed5362e68d2444e1f4bc4ef2c3aac2084d72f406fa373fb1f2316ae` |
| `level4/closure_proofs/p5y_k5_cell308_research/governance/SUCCESSOR_GOVERNANCE_308_ADDENDUM_A1.md` | 11627 | `c170c726c43601ee8c3d028a64b0639708c8b5799698aaf1ced62f5a13ee152c` |
| `level4/closure_proofs/p5y_k5_cell308_research/governance/SUCCESSOR_GOVERNANCE_308_ADDENDUM_A1_ERRATUM_E1.md` | 2946 | `a1972ad3cbd7d59d431724e32fa45ecf3edece36e9251c607b241d7f160c224c` |
| `level4/closure_proofs/p5y_k5_cell308_research/registry/SUCCESSOR_ROUTE_AUDIT_308_ADDENDUM_A1.md` | 7696 | `84379c99a25d32cf6232dde185592d274141e7847726c3e167cb61efbb3e5162` |
| `level4/closure_proofs/p5y_k5_cell308_research/reviews/external/REVIEW_EXTERNAL_B3_PROVENANCE.md` | 50890 | `16188ffd92313f661dbd5c33d72b831af11a41d0c5a93877736e8896d88ce96a` |
| `level4/closure_proofs/p5y_k5_cell308_research/reviews/external/CONFIRMATION_EXTERNAL_B3_CORRECTIONS.md` | 25507 | `6a721adaff4bc38de9d67ea8fac96e42c340479056f466d9cd47035f46fe253c` |

The development source is listed for reading only: no import, no execution.

## 5. Not in this handoff

* A review of the prospective package (A14p). It would be a separate appointment and a separate authority question,
  and is not prepared as a brief here.
* Any further B3 or B2 contact.
* Any L-DET, decoy, caps, qualification, marker or formal-run step.
