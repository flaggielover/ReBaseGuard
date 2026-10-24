# Host-attestation acceptance procedure, revision r3 — proposed text for D-HOST-LIFETIME (Cell-308 Cloud route r1)

**Status: PROPOSED · NOT ACCEPTED · NOT IN FORCE.** This revision replaces revision r2
(`HOST_ATTESTATION_ACCEPTANCE_PROCEDURE_R2_20261016.md`, sha256 `e0531255…c9ca5`). Revision r1 and r2 are preserved
unchanged.

Its sources:
* fresh bounded check FR2 (`reviews/REVIEW_FORMAL_ROUTE_CLOUD_R1_FR2.md`, sha256 `1ad769bb…8cac`; on r2
  ACCEPTED_WITH_CONDITIONS), conditions 2–5 and findings K2–K6, K10 and K17–K20;
* S12 review (`reviews/REVIEW_S12_RISK_CLOUD_R1.md`, sha256 `9d549eb2…b55c`), finding S5.

K1 (the amendment's L-LIFE row) is corrected in amendment erratum E2. Nothing here decides D-HOST-LIFETIME, and
`DECIDED` stays empty. `new_target_evaluations = 0` · `cell309_activity = none`.

Carried items:
* (i) ledger REVIEW line;
* (ii) non-coordinator reviewer;
* (iii) blob-level order;
* (iv) external anchor, including rejections.

## 1. Facts and their read basis

### 1.1 Definitions (K5)

* **`C`, the acceptance commit:** the commit that first introduces the accepting review file
  `reviews/REVIEW_HOST_ATTESTATION_<part>_<name>.md` (§4) with its acceptance line. `review_commit` in the ledger line
  equals `C`. The ledger line is committed in a strict descendant of `C`.
* **HEAD:** the commit checked at the time of a gate.

### 1.2 In-repository facts (read from git objects only; K20)

| fact | read basis | refuse if |
|---|---|---|
| `C` is an ancestor of HEAD | HEAD | not a commit, or not an ancestor |
| the attested bytes | the blob at `C`; mode `100644` / `100755` | missing, non-regular, sha256 differs from the ledger and anchor, invalid JSON, schema wrong |
| **unchanged at HEAD** | the attestation and accepting-review blob ids at HEAD equal those at `C` | changed or deleted after `C` (as the development code, which requires both at HEAD) |
| the accepting review | the blob at `C`; exact line `HOST_ATTESTATION_ACCEPTED_<PART> sha256=<sha>` (§4); one verdict line | any L-LIFE rule fails |
| **veto (K17)** | HEAD's whole history: the **L-LIFE veto as implemented** (a negative word, or any verdict-like line other than the acceptance line, in any blob under `reviews/` in HEAD's history), **plus** any ledger line with `"verdict": "HOST_ATTESTATION_REJECTED"` for the same attestation sha256 or the same machine identity | any hit |
| the history | HEAD: the completeness precondition (not shallow; no promisor, partial-clone or `fsck.*` keys; `git fsck --full --strict`) | any failure |
| the review-directory shape | every commit reachable from HEAD (tree-mode walk) | any non-directory review path |

**Implementation state, stated (K17).** The development code (`9db01504`) reads the `reviews/` veto over HEAD's history.
It does **not** read ledger lines and does not take `C`. Both are successor implementation items.

### 1.3 Owner-check facts (read from the owner's record, not from git; K20)

* the anchored `C` for each part;
* the reviewer-reported verdict and review sha256;
* the attestation sha256;
* the list of every appointment and its outcome (§5).

## 2. Who may accept (K3, K18)

| requirement | how recorded |
|---|---|
| not the coordinator of any session that wrote the attestation, the amendment, a disposition or this procedure | identity in the review and the ledger line |
| not an author of the attestation, and not the owner acting alone | as above |
| not an E1″ holder (governance A1 S13 with erratum E1 D3) | written disclosure before the review |
| not a development-review agent of reviews 59–71, and not reviewerFR1, reviewerFR2 or reviewerS12 | disclosure |
| **appointed by the owner, by name, before the review starts** | the owner's appointment, recorded verbatim and committed before the review |
| **the acceptance reviewer's brief is written or approved by the owner**; its sha256 is in the appointment | appointment record |

**Reporting channel (K3).** The reviewer must report to the owner **directly**, through a channel the coordinator
cannot read or write. Therefore:
* the reviewer is a **human** named by the owner; or
* the reviewer is an **agent launched by the owner** in a session or account the coordinator cannot access, and it
  reports to the owner there.

An agent launched by the coordinator **cannot** be the acceptance reviewer, because its reply and its agent id pass
through the coordinator. If the owner nonetheless chooses one, the owner's record must say so, and the G26
digest-channel control does **not** hold. Acceptance then rests on the owner's adoption alone.

**Identity of an agent reviewer** means all three of:
1. the brief and its sha256;
2. the owner's session or agent id;
3. the owner's own record of both.

## 3. Ledger REVIEW line and review-byte integrity (carried item (i); K2)

When the reviewer finishes, it reports to the owner, in the §2 channel:
* its **verdict**;
* the sha256 of its review file;
* the attestation sha256;
* the part.

The owner records all four. One append-only ledger line is then committed in a strict descendant of `C`:

```
{"phase": "S4_CLOUD_R1_HOST_ATTESTATION_REVIEW", "class": "REVIEW", "part": "P1" | "P2",
 "review": "reviews/REVIEW_HOST_ATTESTATION_<part>_<name>.md", "review_sha256": "<recomputed from the blob at C>",
 "reviewer_reported_sha256": "<as reported to the owner>", "review_commit": "<C>",
 "attestation": "<path>", "attestation_sha256": "<sha256>", "attestation_commit": "<commit that introduced the blob>",
 "verdict": "HOST_ATTESTATION_ACCEPTED" | "HOST_ATTESTATION_REJECTED",
 "reviewer": "<identity per §2>", "appointment_ref": "<path + sha256>", "prior_rejected_attestations": ["<sha256>", …],
 "exposure_disclosure": "<summary>", "machine_identity": {"machine_id_sha256": "…", "product_uuid_sha256": "…"},
 "recomputed_by": "<agent>", "new_target_evaluations": 0}
```

Rules:
* `review_sha256` = `reviewer_reported_sha256` = the owner's recorded digest. Any difference refuses.
* A REJECTED outcome is permanent. It is held in the repository, in the ledger **and in the owner's record**.
* **No self-assertion.** The owner's attestation must not assert its own acceptance. The development
  `attestation_valid` still requires `reviewed` / `accepted` = `true` (FR1 G26). The successor drops that requirement
  (implementation item).
* **Re-attestation (K2).** A new attestation for the same machine (same `machine_identity`) lists in
  `prior_rejected_attestations` every earlier rejected or abandoned attestation sha256 of that machine.

## 4. Order (carried item (iii)), and the split acceptance (K4)

**Order (K19).** The development rule is stricter than r2 described it: **every** commit that adds or removes the
accepting line follows **every** commit that adds or removes the attested blob (merges included). The owner's
appointment commit precedes `C`. The ledger line follows `C`.

**Split.** There are two parts, each with its own review file, acceptance line, ledger line and anchor entry:

| part | items | acceptance line | when |
|---|---|---|---|
| P1 | H1, H3, H4 (the owner's exclusivity arrangement), H6, H7, H8 | `HOST_ATTESTATION_ACCEPTED_P1 sha256=<sha>` | after the Phase-1 inventory and the owner's H3 actions; **before the L-DET interpreter build** |
| P2 | H2, H5 | `HOST_ATTESTATION_ACCEPTED_P2 sha256=<sha>` | after the implementation review; before OD-3 |

H4 is in P1 as the owner's arrangement. Its measured part stays a live gate (`host_exclusive`) at every step.

**Gate mapping.**

| gate | requires |
|---|---|
| L-LIFE, L-UPD, L-FREE (H6 numeric), identity | P1 |
| L-LAUNCH on the official host, L-FSYNC / L-DISK | P1 and P2 |
| OD-3 and every computing step after it | P1 and P2 |

**Rejection effects.**
* A P2 rejection refuses every gate that needs P2. It does not void P1 by itself.
* A P1 rejection refuses every gate.
* Because the history veto reads any negative word under `reviews/`, the successor must scope the veto **per part and
  per attestation sha256** (implementation item). Until then, any rejection blocks both parts, which is fail-closed.

## 5. External anchor and its check procedure (carried item (iv); K2, K6; S12 S5)

**The owner's record** holds, outside this repository, in a place the coordinator cannot edit:
* every **appointment** (part, reviewer identity, brief sha256);
* its **outcome**, ACCEPTED or REJECTED, with the reviewer-reported digest;
* for each accepted part: `C`, the attestation sha256 and the review sha256.

**The check, before each official step.** The official steps are:
* the **L-DET interpreter build** (it starts the H8 window);
* the L-DET attempt;
* the official decoy runs used for caps;
* the designated series;
* qualification;
* the **marker** and `execute`;
* each `resume` / `recover`;
* the grant.

At each step the owner, or the checker named in advance (below), compares for **every part the step requires**:
1. the anchored `C` with the ledger;
2. the anchored review sha256 with the blob at `C`;
3. the anchored attestation sha256 with the blob at `C`;
4. that `C` is an ancestor of HEAD;
5. that the blobs at HEAD are unchanged from `C`.

It **refuses** if the record holds a REJECTED outcome, or an appointment without an outcome, for this attestation or
for any earlier attestation of the same machine.

* **Record.** The checker writes `ANCHOR_CHECK <step> <part> <C> <MATCH|MISMATCH> <utc>` in the owner's record. The
  coordinator mirrors it in the ledger. Preflight refuses without the mirrored line, as defence in depth only.
* **Before the marker:** an absent check, a MISMATCH, or an unreachable checker means the step does not start. A wait
  never extends any deadline.
* **After the marker (S5).** A lapse caused by non-action must not be a free non-completion. Therefore:
  * Before the Phase-1 inventory of the named machine the owner names an **anchor checker for the post-marker steps** (the owner or a named delegate), and a
    binding **response time** for H7 and the anchor check. The number is fixed by the owner at the same time; it is a new
    constant and goes into the new-constant trace.
  * A `resume`, `recover` or deadline lapse caused by owner, checker or operator non-action is recorded as an
    **INCIDENT** that fires T4 (MBS-5(a), stop outside the frozen rules). It is not a pre-declared outcome.
  * A wait that reaches the 7-day deadline ends the run as that INCIDENT. The deadline is never extended.

## 6. What in-repository checks cannot establish (K10)

* Every in-repository check is defence in depth. Reviews 64–71 and review 67 N7 show the false-history class cannot be
  closed in-repository.
* **Circularity applies to every H item.** Every inventory reading (H1–H8) is taken on the attested host by its own
  software. A host that misreports can misreport any reading. The evidence for every H item is therefore:
  * the owner's statements;
  * the provider's documented terms, quoted verbatim with their URL and retrieval time;
  * identity readings repeated at every step.

  None of these is a measurement the host cannot falsify.
* **Remaining trust assumptions:**
  * the owner's record;
  * the reviewer's honesty and disclosure;
  * git object hashing on a checked repository;
  * no change to the store between check and read;
  * the owner's statements about the machine.

## 7. Decisions needed

1. A bounded conformance check of r3 against FR2 §7 conditions 2–5 and S12 S5. Because of K3, it should be done by a
   reviewer the owner launches outside the coordinator's environment.
2. The owner adopts §1–§6 as the D-HOST-LIFETIME mechanism, or amends it.
3. The owner appoints the acceptance reviewer(s) and the anchor checkers, and fixes the response-time constant
   before the Phase-1 inventory.
4. Implementation-review items:
   * a `C` input;
   * the per-part acceptance lines;
   * the per-part, per-sha veto scope;
   * reading ledger REJECTED lines;
   * the schema without `reviewed` / `accepted`.
