# Erratum E1 to host-attestation acceptance procedure r3 (Cell-308 Cloud route r1): recording every verdict, and the machine-wide refusal

**Status: PROPOSED · NOT ACCEPTED · NOT IN FORCE.** This erratum corrects
`HOST_ATTESTATION_ACCEPTANCE_PROCEDURE_R3_20261016.md` (r3, `e4376ee1…4637`), which is preserved unchanged. Its source is
external B1 finding X4 (`reviews/external/REVIEW_EXTERNAL_B1_CONFORMANCE.md`, `cf1a4b18…8e41`, lines 174–184), which
applies FR2 §7 conditions 2 and 4 (`reviews/REVIEW_FORMAL_ROUTE_CLOUD_R1_FR2.md`, lines 283–291).

**Precedence.** Where r3 and this erratum differ, this erratum governs. Everything in r3 that this erratum does not
change stands. Nothing here decides D-HOST-LIFETIME. `DECIDED` stays empty. `new_target_evaluations = 0` ·
`cell309_activity = none`.

**Not weakened.** The external refusal of r3 §5 stays exactly as broad as FR2 condition 2 requires: any REJECTED
outcome, or any appointment without an outcome, for this attestation **or any earlier attestation of the same machine**,
refuses. Every change below either defines a term that r3 left undefined or makes a rule stricter.

## E1.1 — Review commit `R` for every verdict; `C` only for acceptance (replaces r3 §1.1 and the ledger rules of §3)

* **`R`, the review commit:** the commit that first introduces a review file
  `reviews/REVIEW_HOST_ATTESTATION_<part>_<name>.md`, **whatever its verdict**. The file holds exactly one verdict line:
  * `HOST_ATTESTATION_ACCEPTED_<PART> sha256=<attestation sha256>`, or
  * `HOST_ATTESTATION_REJECTED_<PART> sha256=<attestation sha256>`.
* **`C`, the acceptance commit:** defined **only for an accepting review**. `C` = `R` of that review. A rejecting
  review has an `R` and no `C`. Recording a rejection never needs an accepting line.
* **Ledger line, every verdict.** In r3 §3's schema:
  * `"review_commit"` is `R`, for every verdict;
  * a new field `"acceptance_commit"` is `C` for `HOST_ATTESTATION_ACCEPTED` and `null` for every other verdict;
  * the ledger line is committed in a strict descendant of `R`.
* **Digest rule, every verdict.** `review_sha256` is recomputed from the blob at `R`. It must equal
  `reviewer_reported_sha256`, which must equal the digest in the owner's record. Any difference refuses, for a
  rejecting review as for an accepting one.
* **Order, every verdict.** The owner's appointment entry (E1.2), and its commit, precede `R`. `R` precedes the ledger
  line. For an accepting review, r3 §4's stricter blob-level order rule also applies.
* **The owner's record is authoritative for rejections.** The reviewer reports its verdict, digest, attestation sha256
  and part to the owner directly (r3 §3). If the rejecting review file is never committed, the owner's record still holds
  the REJECTED outcome, and the r3 §5 check refuses. The in-repository record is defence in depth only.

## E1.2 — "Appointment" defined; every appointment ends in a recorded outcome

* **Appointment entry:** an entry in the owner's record, made **before the review starts**, binding together:
  * the reviewer's identity (r3 §2);
  * the part (P1 or P2);
  * the attestation sha256;
  * the brief sha256.

  Each review has exactly one appointment entry.
* **Designations are not appointments.** Owner statement 3 may name, in advance, who will review P1 and P2. That names
  people. It creates no appointment entry, because the attestation does not exist yet. The entry is made when that
  part's review is commissioned on a specific attestation sha256.
* **Every appointment entry ends in exactly one recorded outcome:**
  * `ACCEPTED`;
  * `REJECTED`;
  * `NOT_COMPLETED`: the review ended without a review file (the reviewer withdrew, became unreachable or was found
    ineligible).

  `NOT_COMPLETED` is mirrored as a ledger line with `"verdict": "HOST_ATTESTATION_NOT_COMPLETED"`, with `review`,
  `review_sha256`, `reviewer_reported_sha256`, `review_commit` and `acceptance_commit` all `null`. **For refusal it
  counts exactly as REJECTED.** An entry with no outcome yet also refuses (r3 §5). No outcome, and no withdrawal of an
  entry, ever lifts a refusal.

## E1.3 — The machine-wide refusal governs every official step (replaces r3 §4 "Rejection effects")

**Rule.** The owner's record may hold, for this attestation or any earlier attestation of the same machine (same
`machine_identity`), any of:
* a `REJECTED` outcome, of either part;
* a `NOT_COMPLETED` outcome;
* an appointment entry with no outcome.

If it does, the r3 §5 check **refuses every official step on that machine**, whichever part the step requires.

**The steps that stop** (r3 §5's list, in full):
1. the L-DET interpreter build;
2. the L-DET attempt;
3. the official decoy runs used for caps;
4. the designated series;
5. qualification;
6. the marker and `execute`;
7. each `resume` / `recover`;
8. the grant.

OD-3 is not put to the owner while the refusal holds.

**Historical P1 acceptance.** A P1 acceptance recorded before a later rejection, or before an open appointment entry,
stays in the record: its `R` = `C`, its ledger line and its anchor entry are never edited or deleted. It **authorizes
no official step** after that rejection, or while that entry is open. "P1 remains historically accepted" never means
"P1-only steps may still run".

**An open P2 appointment.** The P2 entry is made when the P2 review starts, after the L-DET interpreter build (matrix
R4, rows B10–B11; plan erratum E2 order). From then until its outcome is `ACCEPTED`, every official step on the machine
refuses. The order schedules no official step in that interval. This is intended and fail-closed.

**Effect on the route.** A refusal under this rule before the marker is a gate failure on the named host. Amendment
erratum E2.7 then applies: the route stops, and a restart needs a new owner ruling, a fresh S12 rating and a formal
review. After the marker, a refused step does not start, and r3 §5's after-marker rules apply unchanged.

**Re-attestation.** The refusal reaches every earlier attestation of the same machine. A new attestation of a machine
whose record holds any refusing outcome or open entry can therefore **never** pass. r3 §3's
`prior_rejected_attestations` (extended to `NOT_COMPLETED` outcomes) is disclosure only. It lifts nothing.

## E1.4 — The in-repository veto stays whole-history and all-part (replaces the last bullet of r3 §4, and amends r3 §1.2 and §7)

* The in-repository veto stays the L-LIFE veto over HEAD's whole history, across **all** parts and attestations.
  Ledger lines with `"verdict"` `HOST_ATTESTATION_REJECTED` **or** `HOST_ATTESTATION_NOT_COMPLETED`, for the same
  attestation sha256 or the same machine identity, are added to it.
* r3 §4's implementation item "scope the veto per part and per attestation sha256" is **withdrawn**. Under E1.3, a
  narrower in-repository scope could never let a step run that the external check refuses. It would only weaken the
  defence in depth.
* r3 §7 item 4 (implementation-review items) reads:
  * an `R` input and a `C` input, with `C` = `R` of the accepting review;
  * the per-part acceptance **and rejection** lines;
  * a whole-history, all-part veto that reads ledger `REJECTED` and `NOT_COMPLETED` lines;
  * the schema without `reviewed` / `accepted`.

## E1.5 — The owner's record (amends r3 §1.3 and §5)

For each appointment entry the owner's record holds:
* the entry (E1.2);
* its outcome;
* the reviewer-reported digest and `R`, for every outcome that has a review file;
* `C` (= `R`), the attestation sha256 and the review sha256, for an accepted part.

The five comparisons of r3 §5 are unchanged for every part that a step requires. The refusal of E1.3 is checked at
every official step, before those comparisons.

## E1.6 — Not changed

r3 §2 (who may accept, and the reporting channel), §5's before-marker and after-marker rules, §6 and every other part
of r3 stand.
