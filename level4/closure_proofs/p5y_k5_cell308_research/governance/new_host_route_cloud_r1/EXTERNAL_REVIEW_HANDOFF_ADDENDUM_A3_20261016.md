# External review handoff, addendum A3 (Cell-308 Cloud route r1): B3 inputs after B2's supplement

**Status: HANDOFF METADATA · NOTHING LAUNCHED OR APPOINTED BY THE COORDINATOR SIDE.** This addendum adds to the external
handoff and its addenda A1 and A2 (`EXTERNAL_REVIEW_HANDOFF_ADDENDUM_A2_20261016.md`, `22b7a4bb…f676`), all preserved
unchanged. Where they differ, this addendum governs. `new_target_evaluations = 0` · `cell309_activity = none`.

## 1. State

| id | state |
|---|---|
| B2 | **Complete.** Original report `201aa5af…f9b2` (immutable) and supplement `0c385ebd…2ce1` (`M1_M6_EXTRACTION: COMPLETE`). B2 is retired: it takes no later role, including B3 or S12X |
| B3 | To be commissioned **by the owner**, in a **separate, fresh external context**, under brief r2 (`ledger/briefs/B3_EXTERNAL_PROVENANCE_CHECK_CLOUD_R1_R2.txt`, `af626fd5…2dee`, pin `f9b28704`). B3 must not be B2, must be a non-holder, and must not read the incident review or its T6 supplement source |

## 2. What the owner supplies to B3 explicitly (each with its sha256, which B3 verifies)

| input | where | sha256 | how B3 uses it |
|---|---|---|---|
| B2's original report | `reviews/external/READING_EXTERNAL_B2_INCIDENT_REVIEW.md` at `0db0e5e67102329c2567463932184953733fbeac` | `201aa5af49da3c0d3a9b4a13bc4b356fb4f42c59fde86c780d123b0d3930f9b2` | T6's quotation (its lines 87–89) |
| B2's supplement | `reviews/external/READING_EXTERNAL_B2_T6_MITIGATIONS_SUPPLEMENT.md`, at the commit of this addendum | `0c385ebd82ae1164701e8b8a069f5ed9a373488610b6bc6331fe644f62df2ce1` | **only** its quoted M1–M6 and their stated qualifications (lines 30–103) |
| procedure r3 erratum E2 (Z1, author-proposed) | `governance/new_host_route_cloud_r1/HOST_ATTESTATION_ACCEPTANCE_PROCEDURE_R3_ERRATUM_E2_20261016.md` at `d4bdf26aa03b50b8644e349237dd9eb9f4db336c` | `48fd52494b39cfc483a589b2cff80cdd8ad47d9d3889371db47249193110b4c5` | as an additional rule source for task items 1a and 2 (it states refusal-duration rules). It is not confirmed by any reviewer |

Raw URLs follow the pattern
`https://raw.githubusercontent.com/flaggielover/ReBaseGuard/<commit>/level4/closure_proofs/p5y_k5_cell308_research/<path>`.

## 3. Note for the owner to give B3 (this replaces addendum A2 §2's conditional)

> The M1–M6 definitions are now available in B2's supplement. Use only its quotations; do not substitute MBS-1…MBS-6,
> S12's numbered mitigations or summaries.
> Keep the source's qualifications in view:
> * the original ruling covered one instance only;
> * it was conditional on M1–M8;
> * M6 says "No precedent beyond this case";
> * M7 and M8 were not extracted.
>
> Task item 3 asks for your advice on whether those mitigations apply to this route's new constants and rules, and
> which are met. Give your T6_TRANSFER line on that basis. Where the missing M7 and M8 matter, say so explicitly.
> Your advice is not the owner's T6 ruling.

## 4. Unchanged

* B3's non-holder requirement and exclusions.
* Its reporting channel to the owner only.
* The rule that nothing is decided before the owner's T6 ruling in statement 2.
