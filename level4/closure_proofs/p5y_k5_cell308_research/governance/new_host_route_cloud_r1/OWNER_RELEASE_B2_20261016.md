# Owner release and receipt: external B2 reading of the incident review (Cell-308 Cloud route r1), 2026-10-16

**Status: RECEIPT OF AN OWNER-RELEASED, SANITISED EXTERNAL READING · BRINGS NOTHING INTO FORCE.** The release certifies
no infrastructure isolation, adopts no route or D-* item, issues no risk rating and authorizes no run.
`new_target_evaluations = 0` · `cell309_activity = none`.

## 1. The released file

| item | value |
|---|---|
| recorded at | `reviews/external/READING_EXTERNAL_B2_INCIDENT_REVIEW.md` (immutable; byte-identical to the decoded bytes, `cmp`) |
| sha256 stated by the owner | `201aa5af49da3c0d3a9b4a13bc4b356fb4f42c59fde86c780d123b0d3930f9b2`, 11,579 bytes |
| sha256 recomputed (raw bytes) | `201aa5af49da3c0d3a9b4a13bc4b356fb4f42c59fde86c780d123b0d3930f9b2`, 11,579 bytes: **MATCH** |
| this is | the **complete** sanitised report, per the owner, not an excerpt |
| transmission | `OWNER_TRANSMISSION_B2_READING_20261016.txt`, committed verbatim (sha256 `85b37506ce567469e3f36323b50b50ae553a696881a07482e6b3ad7c261c0c35`, 10,444 bytes). The report is carried as a base64-encoded gzip payload, decoded as data with `base64 -d` and `gunzip`. The transmission contains no program, and none was run |
| tail-figure check (handoff §3 step 2) | Run before reading, by process only (counts, no patterns or matches printed); patterns sha256 `0dc2addc…cbf5`. **0 hits**, in the report and in the transmission |
| reader | **B2-External**, an owner-appointed Codex conversation (report line 5). Brief sha256 `e7b9ca96…c210`; evidence pin `f814fe84053bf8df61149e3d07bbc00aea50846c` |
| incident-review digest, as B2 reports it | `89a2b6ae…562b`. It equals B2's brief allowlist and `ROUTE_PREPARATION.md` line 69. The coordinator side has not opened or hashed the incident review |

## 2. Its conclusions, recorded exactly

* **Quotations (report lines 36–107):** N1–N4, T1–T6 and the Q4 premise table, verbatim with source lines. No
  `[WITHHELD]` substitution was needed (line 132).
* **Amendment r5 §6 quotation comparisons (lines 109–118):** both **MATCH**. That is:
  * amendment r5 lines 239–241 against incident review lines 129–130;
  * amendment r5 lines 243–244 against incident review line 207 (T1).
* **`T1_ON_PLATFORM_CHANGE: CANNOT_TELL`** (line 122). It is **not** converted into FIRED or NOT_FIRED. The risk floor
  stays **not lower than HIGH** on trigger-independent accepted text (amendment erratum E2.3). B2 says the same at line
  128: its reading is not a finding that T1 is unfired, not a rating, and not permission to lower one.
* **M1–M6: NOT EXTRACTABLE from B2's four authorized source files** (lines 91–95). Nothing is substituted for them:
  not MBS-1…MBS-6, not S12's numbered mitigations, and not S12's partial summaries of M1 and M4.

## 3. Limits that stay attached (from the report)

* **B2 treats itself as an E1″ holder** for every later-role exclusion (line 26). It takes no later role, including
  B3 or S12X (line 138).
* B2 cannot certify account ownership, platform-level access isolation, or involvement outside its available context.
  The owner's acknowledgement does not certify those either (line 30).
* B2 did not run the tail-figure scan. That check was run here (§1).

## 4. Source lead for the missing M1–M6 (metadata only; not read)

From the owner's transmission (lines 79–85):
* Brief R2 line 45 cites `b7e62dec` and `ff2280e9` for the incident re-rating and the T6 mitigation. The coordinator
  side confirmed that line, a permitted governance file.
* Full introducing commit: `ff2280e92fff3a76651bde9c6b5744c07b7334f8`.
* Named source: `level4/closure_proofs/p5y_k5_cell308_research/reviews/INCIDENT_INDEPENDENCE_REVIEW_MBS308_T6.md`.
* At pin `f814fe84`, GitHub metadata gives blob `d3d1ef537df47cc08dcfd981b6b9635319b9438a` and byteSize 8745.

**This is a lead, not a verified source.** Whether the file holds all six definitions is not established. The
coordinator side has **not** opened, searched, hashed or otherwise read it, and treats it as excluded material. Only an
owner-authorized supplemental extraction by the **original isolated B2 reader** may read it.

A message carrying exactly that supplemental authorization reached this coordinator-side session by mistake, during
this recording. The coordinator side is not the B2 reader. It **did not act on it** and fetched nothing.

## 5. Missing-source status, and its effect

| item | status |
|---|---|
| M1–M6 definitions | **MISSING** until an owner-released, sanitised B2 supplement (`READING_EXTERNAL_B2_T6_MITIGATIONS_SUPPLEMENT.md`) arrives with its sha256, and is verified and tail-scanned |
| B3 task item 3 (T6 transfer) | **cannot be supported** without the actual definitions. B3 must not claim a supported T6 transfer finding (handoff addendum A2) |
| T6 transfer ruling and D-* adoption | the prerequisite is **not discharged** (matrix R4 erratum E2) |
| B3's non-holder requirement | unchanged. B3 must not be B2, and must not read the incident review or its T6 supplement |
