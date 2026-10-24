# Host-attestation acceptance procedure — proposed text for D-HOST-LIFETIME (Cell-308 Cloud route r1)

**Status: PROPOSED · NOT ACCEPTED · NOT IN FORCE.** This is draft text for the formal route / governance review to fix
the carried items of **D-HOST-LIFETIME** (amendment r5 §4: (i) a ledger REVIEW line binding the accepting review, (ii)
a reviewer who is not the coordinator, (iii) blob-level commit order). D-HOST-LIFETIME is a **new rule**: it has no
macOS counterpart. Nothing here decides it, and `DECIDED` stays empty. `new_target_evaluations = 0` ·
`cell309_activity = none`.

## 1. What the acceptance reads: git tree paths and blob contents only

Every fact the procedure uses is read from **git objects of one named commit**, never from a working tree, a checkout,
a filesystem path or a caller argument (supplements r67 T6, r69 §2, r70 §2).

| fact | how it is read | refuse if |
|---|---|---|
| the acceptance commit `C` | a 40/64-hex commit id written in the ledger REVIEW line (§3) and recorded outside the repository (§5) | not a commit; not an ancestor of HEAD |
| the attestation | `ls-tree -z C -- <path>` gives the entry; mode must be `100644` or `100755`; `cat-file blob <oid>`; sha256 of the bytes | missing, non-regular, unreadable, sha256 differs from the ledger, invalid JSON, deeply nested, schema fields wrong |
| the accepting review | the direct child of `reviews/` named `REVIEW_HOST_ATTESTATION_*.md`, read the same way; exact line `HOST_ATTESTATION_ACCEPTED sha256=<sha>`; exactly one verdict-like line, `VERDICT: HOST_ATTESTATION_ACCEPTED` | any rule of L-LIFE fails (fixed set, verdict, veto, order) |
| the history | the completeness precondition (shallow / promisor / `fsck.*` keys / strict fsck) and the history scans of `lx_platform` at the reviewed revision | any precondition fails |

The development implementation of the in-repository part is `lx_platform.attestation_valid` at
`9db01504` (`lx_platform.py` sha256 `da32ce8c…6389`; native run 38848711278: 230 tests, 207/207 mutants). It is
**development only** and not yet implementation-reviewed. It does not implement §3–§5.

## 2. Who may accept (reviewer independence)

| requirement | why | how recorded |
|---|---|---|
| not the coordinator of any session that wrote the attestation, the amendment, a disposition supplement or this procedure | carried item (ii); a coordinator's own acceptance is a self-acceptance (governance S8: "fresh reviewers") | identity line in the review and in the ledger REVIEW line |
| not an author of the attestation, and not the owner acting alone | the attestation is the owner's statement; acceptance checks it | as above |
| not an E1″ holder (governance A1 S13 with erratum E1 D3: reviewGOV, reviewADJ and any other listed holder) | S13: holders take no route, implementation, caps or qualification role; acceptance is a qualification-path role | written exposure disclosure in the review |
| not one of the development-review agents of reviews 59–71 for the attestation it accepts | those agents reviewed the development code; they were never appointed as acceptance reviewers, and their verdicts were bounded development reviews | disclosure |
| appointed by the owner, by name, before the review starts | gives the authority the code cannot check | the owner's appointment, recorded verbatim and committed before the review |

**Remaining trust assumption, stated:** the code cannot verify any of this. A commit can carry any author name. The
independence rests on the owner's appointment record and on the external anchor (§5), not on git metadata.

## 3. Ledger REVIEW line (carried item (i))

After the accepting review is committed, the ledger gets one append-only line in this proposed form:

```
{"phase": "S4_CLOUD_R1_HOST_ATTESTATION_REVIEW", "class": "REVIEW",
 "review": "reviews/REVIEW_HOST_ATTESTATION_<name>.md", "review_sha256": "<sha256 of the review blob, recomputed>",
 "review_commit": "<commit that introduced the accepting line>",
 "attestation": "<path>", "attestation_sha256": "<sha256>", "attestation_commit": "<commit that introduced the blob>",
 "acceptance_commit": "<commit C>", "verdict": "HOST_ATTESTATION_ACCEPTED" | "HOST_ATTESTATION_REJECTED",
 "reviewer": "<appointed identity>", "appointment_ref": "<path + sha256 of the owner's appointment>",
 "exposure_disclosure": "<summary>", "machine_identity": {"machine_id_sha256": "…", "product_uuid_sha256": "…"},
 "recomputed_by": "<agent>", "new_target_evaluations": 0}
```

Rules:
* The recomputation of `review_sha256` and `attestation_sha256` is done from the blobs at `acceptance_commit`, by an
  agent other than the reviewer, and recorded in the same line.
* A REJECTED line is permanent, like a committed rejection (L-LIFE).
* A gate passes only if all three agree:
  * the in-repository check (§1);
  * the ledger line;
  * the external anchor (§5).

## 4. Order (carried item (iii))

Already implemented in development: the commit that first introduces the accepting **line** (repository-wide) is a strict
descendant of every commit that introduces the attested **blob**, merges included. Added by this procedure: the owner's
appointment commit precedes the review commit, and the ledger line follows the review commit.

## 5. External anchor, and what in-repository checks cannot establish

Reviews 64–71 found mechanism after mechanism by which a repository's own files make git report a false history.
Review 67 N7 concluded the class **cannot be closed by in-repository checks**, and supplements r67–r70 state the
precondition as defence in depth.

The procedure therefore requires one fact recorded **outside** the repository: the full commit id of the acceptance
commit, written by the owner in a place the coordinator cannot edit. That place is the owner's own decision record, for
example a signed message or the owner's own notes. The repository (including the ledger) is never the only copy.

**Trust assumptions that remain:**
* the owner's record of the anchor;
* the appointed reviewer's honesty and exposure disclosure;
* git's object hashing on a checked repository;
* that nothing changes the store between the check and the reads;
* that the check runs on a host the owner controls.

## 6. Decision needed (formal route / governance review, then owner)

* Accept §1–§5 as the D-HOST-LIFETIME mechanism, or amend it.
* Name the appointing authority. Recommended: the owner.
* Decide whether the new attestation fields of `HOST_EVIDENCE_PLAN_H1_H8_20261016.md` §2 enter the schema. That
  change would need an implementation review.
