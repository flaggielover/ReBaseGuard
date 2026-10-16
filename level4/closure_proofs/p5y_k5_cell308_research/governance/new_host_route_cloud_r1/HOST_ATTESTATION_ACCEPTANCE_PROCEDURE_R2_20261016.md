# Host-attestation acceptance procedure, revision r2 — proposed text for D-HOST-LIFETIME (Cell-308 Cloud route r1)

**Status: PROPOSED · NOT ACCEPTED · NOT IN FORCE.** Revision r2 of `HOST_ATTESTATION_ACCEPTANCE_PROCEDURE_20261016.md`
(sha256 `91e61e8d…0322`, preserved unchanged). That text was **NOT_ACCEPTED** by the formal route review FR1
(`reviews/REVIEW_FORMAL_ROUTE_CLOUD_R1_FR1.md`, sha256 `af150ef4…b6df`). This revision corrects FR1 findings G9, G10,
G11 and G26, and states the circularity named in FR1 F5. A fresh bounded review is still needed, and the owner must
adopt the result, before D-HOST-LIFETIME can be decided. Nothing here decides it, and `DECIDED` stays empty.
`new_target_evaluations = 0` · `cell309_activity = none`.

D-HOST-LIFETIME is a **new rule** with no macOS counterpart. Its carried items are:
* (i) a ledger REVIEW line binding the accepting review;
* (ii) a reviewer who is not the coordinator;
* (iii) blob-level commit order.

FR1 adds a fourth item: (iv) an external anchor, with a check procedure.

## 1. What is read, and at which commit (corrects G9)

Every fact is read from **git objects**, never from a working tree, a checkout, a filesystem path or a caller argument
(supplements r67 T6, r69 §2, r70 §2). Two read bases are used, and each fact has exactly one:

| fact | read basis | how it is read | refuse if |
|---|---|---|---|
| the acceptance commit `C` | the owner's external record (§5), compared with the ledger REVIEW line | a full 40/64-hex commit id | the two ids differ; not a commit; **not an ancestor of HEAD** |
| the attested bytes | **`C`** (it fixes the bytes) | `ls-tree -z C -- <path>`; mode `100644` / `100755`; `cat-file blob <oid>`; sha256 | missing, non-regular, unreadable, sha256 differs from the ledger, invalid JSON, schema wrong |
| the accepting review's bytes | **`C`** | the same, for `reviews/REVIEW_HOST_ATTESTATION_<name>.md`; exact line `HOST_ATTESTATION_ACCEPTED sha256=<sha>`; one verdict line `VERDICT: HOST_ATTESTATION_ACCEPTED` | any L-LIFE rule fails at `C` |
| rejections and veto | **HEAD and HEAD's whole history**, at every check | the L-LIFE history-wide veto (`_historical_review_blobs` in development); any `HOST_ATTESTATION_REJECTED` blob or ledger REJECTED line for the same attestation sha256 anywhere in HEAD's history | any rejection exists, whether committed before or after `C` |
| the history | HEAD | the completeness precondition (no shallow marker; no promisor, partial-clone or `fsck.*` keys; `git fsck --full --strict`) | any precondition fails |
| the review-directory shape | every commit reachable from HEAD | the L-LIFE tree-mode walk | any non-directory review path |

The same rule applies to L-LIFE in amendment r5 (amd L-LIFE row). **`C` fixes the accepted bytes. HEAD's whole history
fixes the veto.** An acceptance commit that is not an ancestor of HEAD refuses.

The development implementation of the in-repository part is `lx_platform.attestation_valid` at `9db01504`
(`lx_platform.py` sha256 `da32ce8c…6389`). It already reads the veto over HEAD's history. It does **not** take `C` as an
input, and it does not implement §3–§5. Taking `C` as an input is an implementation change for the reviewed successor,
not for the development code.

## 2. Who may accept (reviewer independence; corrects G26 / FR1 F6)

| requirement | how recorded |
|---|---|
| not the coordinator of any session that wrote the attestation, the amendment, a disposition supplement or this procedure | identity line in the review and in the ledger REVIEW line |
| not an author of the attestation, and not the owner acting alone | as above |
| not an E1″ holder (governance A1 S13 with erratum E1 D3) | written exposure disclosure in the review, made before the review starts |
| not one of the development-review agents of reviews 59–71, nor reviewerFR1 | disclosure |
| **appointed by the owner, by name, before the review starts.** A coordinator's appointment is not sufficient for this role (FR1 F6) | the owner's appointment, recorded verbatim and committed before the review |

**Identity of an agent reviewer.** An agent has no persistent identity, so "by name" means all three of:
1. the brief text and its sha256;
2. the session id or agent id that ran it;
3. the owner's own record of both.

A human reviewer is named as the owner names them.

**Trust assumption, stated:** the code cannot verify any of this. Independence rests on the owner's appointment record
and the external anchor, not on git metadata.

## 3. Ledger REVIEW line and review-byte integrity (carried item (i); corrects G26)

The reviewer's digest reaches the owner directly. When the review is finished, the reviewer reports the sha256 of its
own review file:
* to the owner, in the channel the owner named in the appointment;
* in the reviewer's own final reply.

The owner records that digest in the owner's own record (§5). The committed review blob must have that digest.

After the review is committed, the ledger gets one append-only line:

```
{"phase": "S4_CLOUD_R1_HOST_ATTESTATION_REVIEW", "class": "REVIEW",
 "review": "reviews/REVIEW_HOST_ATTESTATION_<name>.md", "review_sha256": "<recomputed from the blob at C>",
 "reviewer_reported_sha256": "<the digest the reviewer reported>",
 "review_commit": "<commit that introduced the accepting line>",
 "attestation": "<path>", "attestation_sha256": "<sha256>", "attestation_commit": "<commit that introduced the blob>",
 "acceptance_commit": "<commit C>", "verdict": "HOST_ATTESTATION_ACCEPTED" | "HOST_ATTESTATION_REJECTED",
 "reviewer": "<identity per §2>", "appointment_ref": "<path + sha256 of the owner's appointment>",
 "exposure_disclosure": "<summary>", "machine_identity": {"machine_id_sha256": "…", "product_uuid_sha256": "…"},
 "split": "H1/H3/H6/H7/H8" | "H2/H5", "recomputed_by": "<agent>", "new_target_evaluations": 0}
```

Rules:
* `review_sha256` must equal `reviewer_reported_sha256` and the owner's recorded digest. Any difference refuses.
* A REJECTED line is permanent. It is read over HEAD's whole history (§1).
* **Self-assertion removed.** The owner's attestation must **not** assert its own acceptance. Acceptance lives only in
  the review, the ledger line and the external anchor.
  * The development `lx_platform.attestation_valid` at `9db01504` still requires `reviewed` and `accepted` to be
    `true` in the attestation file. That is the self-assertion FR1 G26 names.
  * The successor schema drops both fields, or requires them absent, and its check must stop requiring them.
  * This is an implementation-review item. The development code is unchanged here.

## 4. Order (carried item (iii)), and the split acceptance (corrects G11)

* Already implemented in development: the commit that first introduces the accepting **line** (repository-wide) is a
  strict descendant of every commit that introduces the attested **blob**, merges included.
* The owner's appointment commit precedes the review commit.
* The ledger line follows the review commit.

**The acceptance is split in two (G11).** The H2 and H5 evidence needs the reviewed implementation, which does not exist
before the implementation review.

| part | items | when | evidence |
|---|---|---|---|
| acceptance part 1 | H1, H3, H6, H7, H8 | after the Phase-1 inventory and the owner's H3 actions; before the successor build is reviewed | inventory, owner attestation, provider terms quoted verbatim |
| acceptance part 2 | H2, H5 | after the implementation review (ROUTE_PREPARATION step 4); before OD-3 | a synthetic dry launch of a non-science service under the reviewed launcher (H2); the reviewed durable-write tests and one owner-scheduled reboot-survival check (H5) |

Each part has its own review file, its own ledger line (`split`), and its own anchor entry. A gate that needs H2 or H5
passes only with both parts accepted.

## 5. External anchor and its check procedure (carried item (iv); corrects G10)

**The anchor.** The owner writes in the owner's own record, in a place the coordinator cannot edit (for example a signed
message, or the owner's own notes outside this repository):
* the full commit id of each acceptance commit `C`;
* the reviewer-reported review sha256;
* the attestation sha256.

The repository, including the ledger, is never the only copy.

**The check.** Before each official step, the owner (or a checker the owner names in the appointment record) compares
the anchor with the repository. The official steps are:
* the L-DET attempt;
* the designated series;
* qualification;
* `execute`;
* each `resume` or `recover`.

The check compares:
1. the anchored `C` with the ledger line's `acceptance_commit`;
2. the anchored review sha256 with the review blob at `C`;
3. the anchored attestation sha256 with the attestation blob at `C`.

It also confirms that `C` is an ancestor of HEAD.

* **Record.** The checker writes `ANCHOR_CHECK <step> <C> <MATCH|MISMATCH> <utc>` in the owner's record. The
  coordinator mirrors that line in the ledger. The mirror is not the evidence; the owner's record is.
* **Fail closed.** The step does not start if:
  * the anchor check is absent for that step;
  * it reads MISMATCH;
  * the owner or the named checker cannot be reached.

  An unreachable owner is a wait, not a pass. Automated preflight cannot read the anchor. Preflight refuses unless
  the mirrored ledger line for that step exists, and that refusal is defence in depth only.

## 6. What in-repository checks cannot establish (stated; FR1 F5)

* Reviews 64–71 found repeated ways for a repository's own files to make git report a false history. Review 67 N7
  concluded the class cannot be closed in-repository. Every in-repository check is defence in depth.
* **Circularity for H1 and H8.** The in-repository check runs on the official host, which is the attested object. A
  host that misreports its own identity or lifetime can also misreport the check. For H1 and H8 the evidence is
  therefore:
  * the owner's statement;
  * the provider's documented terms, quoted verbatim with their URL and retrieval time;
  * an identity reading repeated at every step.

  None of these is a measurement the host cannot falsify.
* **Remaining trust assumptions:**
  * the owner's record of the anchor;
  * the appointed reviewer's honesty and exposure disclosure;
  * git's object hashing on a checked repository;
  * that nothing changes the store between the check and the reads;
  * the owner's statements about the machine.

## 7. Decisions needed

1. A fresh bounded review of this revision, which then needs the owner's adoption.
2. The owner adopts §1–§6 as the D-HOST-LIFETIME mechanism (or amends it).
3. The owner is the appointing authority for the acceptance reviewer and the anchor checker. This revision recommends
   it.
4. Whether the H1–H8 attestation fields of `HOST_EVIDENCE_PLAN_H1_H8_20261016.md` §2 enter the successor schema, and
   whether `reviewed` / `accepted` leave it. Both need an implementation review.
