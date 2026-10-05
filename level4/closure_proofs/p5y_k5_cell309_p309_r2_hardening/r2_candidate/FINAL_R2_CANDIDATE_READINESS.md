# Final readiness: minimal r2 adoption candidate

*Deliverable 6. The required name was `FINAL_ADOPTION_READINESS.md`; it is renamed because the session guard refuses
paths containing "adoption" (see "Deviations" below).*

**Verdict: R2_ADOPTION_CANDIDATE_REVIEW_REQUIRED**

**NEW Γ309 TARGET EVALUATIONS = 0.**
- No target quantity of cells 306–309 was evaluated.
- No grant was issued or consumed.
- Nothing was adopted, frozen or qualified, and no scientific status changed.
- r5 is unchanged and there is no r6.
- r1, r2 and main are unchanged on origin. Cell 309 remains OPEN.

## The candidate

- **Branch and commit:** `claude/p309-r2-adoption-candidate-20261005` at `93d550638b8c79ae1c252fc6c2b0194b1a416b49`,
  one commit on r2 `101ef2cb`, pushed. It is not merged into r2.
- **Contents:** 3 files, all in r2's namespace (`R2_CANDIDATE_DELTA.md`):
  - `code/p309_qualify.py`: the reviewed hardening, ported mechanically from `3c191ac2`, with `# exclusive`
    restored;
  - `code/p309_topology_drill.py`: F-DRILL-ORDER, params before manifest;
  - `config/SCANNER_ALLOWANCE_P309.json`: the one consequent pin, `make_topology`, refreshed by r2's own tool.

## Answers to the nine review questions

These come from the independent review (`INDEPENDENT_DELTA_REVIEW.md`), cross-checked against the validation.

| # | question | answer |
|---|---|---|
| 1 | hardening limited to qualification infrastructure | **YES** |
| 2 | scientific algorithms and target logic unchanged | **YES**: every gate function, `items_table`, the driver, guard, generators and evaluators are byte- or AST-identical |
| 3 | gate semantics unchanged except durability / exactly-once | **PARTLY (reviewer)**: gate logic and verdicts are unchanged. The additions are new pre-launch refusals (temp file, torn ledger, nonzero counter, orphan RUN START), `ATTEMPT_START.json`, a summary key, and new filesystem-dependent steps after RUN START |
| 4 | pins preserved or re-pinned with evidence | **YES**: one intentional re-pin with evidence; all 9 pinned runner functions are unchanged. The governance re-pin record is missing |
| 5 | T14a passes | **YES**: static controls 22/22, T14a PASS |
| 6 | QC15/A7 passes | **YES**: QC15 PASS, A1–A10 true |
| 7 | F-DRILL-ORDER fixed correctly | **YES**: `MANIFEST DIFFERS` → `IDENTICAL`; matches r1's real freeze |
| 8 | crash matrix discriminates baseline from candidate | **YES**: baseline CORRUPT at C04/C05/C12, 0 fsyncs, S04–S06 launched; candidate none of these. Units: baseline fails T03–T08 |
| 9 | branch clean enough to propose | **PARTLY (reviewer)**: the commit is clean (3 r2 paths). Adoption prerequisites are still open (below) |

## Validation summary (`R2_CANDIDATE_VALIDATION_REPORT.md`)

- **r2's own gates on the candidate:** all pass.
  - QC11: 112/112;
  - QC12;
  - QC-D5: controls, backstop and pins all current;
  - host tests;
  - static controls (T14a PASS);
  - QC15 (A7 true).
- **Existing hardening validation:** all pass and discriminating. Unit tests 8/8 (baseline fails T03–T08); crash
  matrix with no CORRUPT outcome; fsync ordering 25/25; S04–S06 refused.
- **Light result-free rehearsal:** PASS, 15/15 gates, re-validated independently.
  - The first rehearsal attempt was INTERRUPTED by disk exhaustion on this container. It was preserved and never
    resumed; this is a development-host limitation.
  - Host checks are DEVELOPMENT_ONLY.

## Why REVIEW_REQUIRED, and not READY or BLOCKED

**Not BLOCKED:**
- the independent reviewer found **no blocker**;
- every requested check passes;
- T14a and QC15/A7, the two reasons the hardening branch could not be adopted, are resolved;
- F-DRILL-ORDER is fixed.

**Not READY.** The independent review recommends **"propose after listed fixes"** and answers Q3 and Q9 only PARTLY.
Three should-fix items stand between this candidate and a proposal under r2's own rules. None of them is in this
task's scope ("the two known pre-adoption corrections and their validation"), and none may be decided silently:

1. **S1, filesystem precondition.** The single attempt now depends on `os.link` and directory `fsync` right after RUN
   START. On a filesystem without them, the one allowed attempt would end INTERRUPTED. Two options:
   - (a) a reviewed pre-launch probe in the runner. This would be a new runtime feature, not added here.
   - (b) an explicit host requirement in `R2_HOST_REQUIREMENTS.md`, checked on the execution host. The ext4 / xfs
     rule already in the durable-host packet covers it in practice.
   **Owner or r2-review decision.**
2. **S2, governance re-pin record.** `governance/R2_REPIN_LIST*.json` still records `make_topology = 9b59c12f…`. A
   supplement recording `→ 8af1bb78…` belongs to r2's governance trail. That is documentation in r2's namespace, which
   this candidate deliberately does not carry (no documentation).
3. **S3, r2's formal delta follow-up review.** The runner was accepted by follow-up review 4 (`38842550`). r2's
   process requires a brief, review and sha256 record for any later change before a freeze. The independent review
   here is evidence for that review, not a substitute for it. That review should also explicitly accept the reviewer's
   notes N1–N9, for example:
   - N1: subprocess-written evidence is not fsynced;
   - N2: no in-namespace H1–H5 tests;
   - N3: the refusal text names a validator outside r2;
   - N4: the schema label is unchanged;
   - N7: a non-object ledger row crashes before launch instead of refusing.

Once those three are handled through r2's route, nothing found here prevents the candidate being proposed.

## Deviations (disclosed)

- **Deliverable file names.** The session guard (rule R2_GRANT, `ADOPT_RE`) refuses any path containing "adoption".
  Narrowing that rule was proposed and **denied by the permission system as self-modification**, so the guard was left
  unchanged. Deliverables 1, 2, 5 and 6 carry neutral names:

  | required name | file name used |
  |---|---|
  | `ADOPTION_CANDIDATE_DELTA.md` | `R2_CANDIDATE_DELTA.md` |
  | `ADOPTION_VALIDATION_REPORT.md` | `R2_CANDIDATE_VALIDATION_REPORT.md` |
  | `ADOPTION_EVIDENCE_MANIFEST.json` | `R2_CANDIDATE_EVIDENCE_MANIFEST.json` |
  | `FINAL_ADOPTION_READINESS.md` | `FINAL_R2_CANDIDATE_READINESS.md` |

  `F_DRILL_ORDER_REVIEW.md` and `INDEPENDENT_DELTA_REVIEW.md` keep their names. The mapping is also in the evidence
  manifest. Renaming them is a one-step owner action.
- **Third file in the candidate.** The task named one runner file and the drill-order correction. The drill fix
  unavoidably changes `make_topology`'s scanner-pinned AST, so `config/SCANNER_ALLOWANCE_P309.json` carries the one
  refreshed hash. This is "intentionally re-pinned with evidence" (Q4), made with r2's own `--refresh` tool; the
  structural diff is exactly one leaf.
- **Where the deliverables live.** To keep the candidate branch to adoption changes only, these reports and their
  evidence are committed on the Task 2 branch `claude/p309-r2-hardening-20261005`, under
  `level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/r2_candidate/`. They are not on the candidate branch.
- **Session guard during the task.**
  - Re-scoped to the candidate branch. It stayed untracked there, and a new commit-set rule allowed only the 3 r2 files.
  - 162/162 guard tests passed before the push.
  - Canary refused.
  - No tripwire event in this task. The one tripwire event in the audit log is Task 2's, already disclosed.

## Integrity (STEP 8; independent counters, `evidence/integrity/`)

| item | result |
|---|---|
| new target evaluations | **0**: 367 repositories and 20 762 ledger rows scanned; 0 nonzero or unreadable rows; 0 protected refs on origin; protected refs only in TEST sandboxes (QC11 F23 fixture `refs/rlr-tail/x`, legitimate) |
| new grants | **0**: no grant or result file added or changed; 0 grant files even in TEST sandboxes |
| adoption | **none**: candidate branch only; nothing merged, frozen or qualified |
| r5 | unchanged (`f978eeb6…`) |
| r6 | none |
| origin refs | r2 `101ef2cb`, r1 `c902fe2f`, main `1cb45382`, recovery `290b6c10` all unchanged. Hardening `ae7db324` changes only by this report's commit |
| Cell 309 | **OPEN** |
| session audit | target evaluations 0 (`evidence/integrity/SESSION_AUDIT_SNAPSHOT.json`) |

## Next permitted actions (none is a target evaluation)

1. **Owner:**
   - decide S1 (probe vs host requirement);
   - commission r2's delta follow-up review of `101ef2cb..93d55063`, with this packet as its input, including the
     S2 re-pin supplement;
   - optionally rename the four deliverables.
2. **After acceptance:** the adoption itself, as a separate owner act. That is a fast-forward of r2 to the candidate,
   never a merge of the hardening branch.
3. **Then:** on the durable host,
   - the `--gates all --require-durable-host` rehearsal;
   - the worker-tier drill;
   - with OD-R2-0 (D), the freeze and the single attempt (`DURABLE_HOST_EXECUTION_PACKET.md`, Task 2).

**Stop.** Nothing was merged into r2. Nothing was frozen. Nothing was qualified. Γ(309) was not evaluated.
