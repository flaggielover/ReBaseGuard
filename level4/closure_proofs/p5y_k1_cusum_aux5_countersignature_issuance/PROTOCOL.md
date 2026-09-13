# CUSUM Aux5 production-provenance successor: countersignature issuance protocol

**Scope.** This namespace resolves only the self-referential deadlock in issuing the independent countersignature for the successor checkpoint `dd4c89d7…` (namespace `p5y_k1_cusum_aux5_production_provenance_successor`).

It does **not** change:
- production governance;
- the Aux5 scientific producer;
- the provenance semantics;
- the frozen successor code, config, tests or evidence.

It adds no file to any hash-bound or executor-globbed directory, so P02 and P06 are unaffected.

## 0. Historical verdict (preserved)

The prior reviewer applied the mandate "every gate must pass before signing" to the frozen P01–P10 preflight. P07 failed with `COUNTERSIGNATURE_MISSING`, so that reviewer refused to countersign. The refusal was relayed by the user; no artifact of it was committed. It is recorded here as:

```text
PRIOR_COUNTERSIGNATURE_REVIEW = BLOCKED_BY_COUNTERSIGNATURE_ISSUANCE_DEADLOCK
cause: no countersignature -> P07 FAIL -> reviewer may not countersign -> no countersignature
substantive gates at that time: P01-P06, P08-P10 PASS (evidence/preflight_postfreeze_r1 of the successor)
```

The block was procedural. It was not a substantive finding against the successor.

## 1. What a countersignature is: frozen precedents

| Precedent | Where the approval artifact sits |
|---|---|
| K1 `adjudication/ADJUDICATION_CONTRACT.md` | "an adjudicator that is **not** the producer verifies every item below and **writes** `adjudication/ADJUDICATION_VERDICT.json`". The verdict file is written after verification; no checked item requires it to exist. |
| PS1 `evidence/PS1_AUTHORIZATION_ADJUDICATION.json` | Substantive `checks` all true → `AWS_GENUINE_PS1_SR_PRODUCTION_AUTHORIZED_TO_START = YES`, `started_in_this_round: false`. The `operator_preconditions_before_start` (live acceptance, `prodctl verify`) are listed separately and run after the authorization. |
| PS1 `config/LAUNCH_AUTHORIZATION.json` + `driver/ps1_cellseq_launcher.py production_preflight` | `make_authorization.py` issues the authorization after qualification. `production_preflight` then consumes it as a launch gate (`load_production_authorization`, producer-commit ancestry). It does not gate its own issuance. |
| K1 cover-ledger `adjudication/REVIEW.json` | The review verdict object is the output of its `checks`. |
| Successor `config/FREEZE_RECORD.json` `launch_requires` (frozen) | Ordered: (1) "an independent reviewer commits config/COUNTERSIGNATURE.json…", (2) "prov_entry.py preflight prints READY (P01-P10)", (3) the operator launch command. The frozen text puts the countersignature **before** the full P01–P10 READY. |
| Successor `REVIEW_PACKET.md` header, `RESULT.md` | "Production stays unlaunchable until the reviewer commits `config/COUNTERSIGNATURE.json`, **then** `prov_entry.py preflight` prints READY, and then an operator runs the launch command." |
| Successor acceptance `t19` | Before the freeze, "only freeze/countersignature-dependent checks may fail". P07 is treated as a signature-dependent check, not a substantive one. |

```text
COUNTERSIGNATURE_ROLE = OUTPUT_OF_SUCCESSFUL_REVIEW
```

**Pre-signature review gates** are the substantive properties of the object under review:
- checkpoint/freeze identity (P01);
- bound sources (P02);
- predecessor fenced (P03);
- inherited sections (P04);
- schemas (P05);
- pre-result authorization (P06);
- acceptance (P08);
- pristine run state (P09);
- idle host (P10);
- plus the temporal preconditions in §6.

**Post-signature launch gates** are all of P01–P10, including P07. They also include the issuance bindings in §5 and "not yet started".

## 2. Two-phase state machine

```text
            review-preflight                               launch-preflight
 FROZEN ──────────────────────────► READY_FOR_COUNTERSIGNATURE ──(reviewer commits)──► COUNTERSIGNED ──────────────────► READY_TO_LAUNCH_PRODUCTION
   │   P01-P06,P08-P10 PASS             (signing permitted,         config/COUNTERSIGNATURE.json    P01-P10 PASS (frozen,          │
   │   P07 FAIL == COUNTERSIGNATURE_    launch NOT authorized)                                        unmodified) + issuance       ▼
   │   MISSING, root absent, no                                                                     bindings + root absent    operator launch
   │   process, 0 cells, clean,                                                                                               (NOT in this protocol)
   │   temporal PASS
   └─ anything else ──► BLOCKED
```

**Phase A**: `issuance.py review-preflight`, over the unmodified `prov_entry.preflight()`.
- It returns `READY_FOR_COUNTERSIGNATURE` iff:
  - every frozen check except P07 PASSes;
  - P07 FAILs with **exactly** `COUNTERSIGNATURE_MISSING`;
  - the signing guard passes;
  - the temporal checks pass.
- A present but invalid countersignature is `BLOCKED`, not "absent".
- If P07 already PASSes it returns `REVIEW_PASS_COUNTERSIGNED`, with signing refused because nothing is ever issued twice.
- It can never return a launch state, and it always sets `launch_authorized: false`.

**Phase B**: `issuance.py launch-preflight`.
- It returns `READY_TO_LAUNCH_PRODUCTION` iff:
  - the unmodified frozen preflight reports `ready: true` with all ten checks PASS in order;
  - the committed countersignature passes frozen `verify_countersignature`;
  - it passes `check_issuance_binding` (§5);
  - the production root, processes and result-bearing cells are still absent.

There is no route from Phase A to launch. `READY_FOR_COUNTERSIGNATURE` is not an input to any launch predicate. The only launch predicate contains P07, and P07 cannot pass without a committed countersignature file. `tests/test_issuance.py::test_no_route_from_review_to_launch` enumerates 2048 P01–P10 outcome combinations.

## 3. P07 classification

P07 (`prov_entry.py` `p07`) calls `verify_countersignature`. That function checks presence, schema, `APPROVED_FOR_PRODUCTION_LAUNCH`, the bindings to authorization / checkpoint / run / mode / freeze record, `synthetic` false, and the reviewer declaration; P07 then checks `git ls-files`. Every substantive object P07 compares against is already verified in its own right:
- the authorization, by P06;
- the checkpoint and freeze record, by P01.

P07's sole additional content is the existence and integrity of the countersignature artifact.

```text
P07_CLASSIFICATION = POST_SIGNATURE_ONLY
```

P07 is **not weakened**. The frozen entrypoint and the frozen launch path are byte-identical:
- `prov_entry.py launch` → `_supervise` → full P01–P10 → `production_authz()`;
- genesis still refuses without a verified countersignature.

P07 is only excluded from the review-eligibility predicate, and only in its `COUNTERSIGNATURE_MISSING` form.

## 4. Repair (additive)

| File | Role |
|---|---|
| `code/issuance.py` | `review_eligibility`, `signing_guard`, `review_decision`, `launch_eligibility`, `check_issuance_binding` (pure), plus the `review-preflight` / `launch-preflight` CLIs. Read-only. Never writes a countersignature. |
| `tests/test_issuance.py` | Adversarial self-reference tests, using the real frozen authorization and the real `verify_countersignature` on temporary copies |
| `evidence/` | Review-preflight evidence (pre-signature) and launch-preflight evidence (post-signature) |

**Residual.** The frozen `prov_entry.py launch` enforces P01–P10 but not the additional issuance bindings of §5, because editing it would break P02/P06. The launch gate is exactly as strong as it was frozen. The issuance bindings are an additional operator-side check (`launch-preflight`), which the operator runs immediately before launch.

## 5. Countersignature content

`config/COUNTERSIGNATURE.json` in the successor namespace carries the frozen-required fields that `verify_countersignature` reads. It also carries an `issuance` block (schema `…countersignature-issuance.v1`), which binds:
- authorization and freeze commits;
- authorization id, ledger id, runtime root;
- producer identity (equal to the authorization's);
- host facts (equal to the authorization's);
- runtime contract;
- the exact 326-cell universe (equal to the authorization's);
- the cap `300 CPU-h = 1.08e12 µs`;
- the review verdict and state;
- the reviewed branch and tip;
- the review evidence path, sha256 and commit;
- the reviewer and review session;
- statements that no production result existed, no AWS resource was touched, and no result-bearing compute ran.

`check_issuance_binding` refuses when any of these conditions holds:
- any bound value differs from the live authorization;
- the reviewed tip does not contain the freeze commit, or HEAD does not descend from it (stale base);
- any successor `code/config/tests/evidence` path or issuance `code/tests` path changed between the reviewed tip and HEAD, the countersignature itself excepted;
- the review evidence is not committed between the reviewed tip and HEAD, is not byte-identical, does not state `READY_FOR_COUNTERSIGNATURE` for the same three hashes at the reviewed tip, or recorded a non-pristine production state.

No field is an unbound reference. Every checkpoint- or authorization-identifying value must equal the live, hash-verified object.

## 6. Temporal integrity

Before signing:
- `review-preflight` records that the production root, production processes, result-bearing cells and the predecessor ledger are all absent;
- the checkout is clean;
- the authorization commit → freeze commit → HEAD ancestry holds;
- the authorization, freeze record and checkpoint at their commits equal the live bytes;
- the commit times are ordered before now.

The review evidence is committed before the countersignature commit. After signing, `launch-preflight` re-verifies the same absence facts on the host.
