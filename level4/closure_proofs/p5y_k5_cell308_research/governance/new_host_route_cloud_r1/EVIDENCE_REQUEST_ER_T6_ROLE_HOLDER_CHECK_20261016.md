# Evidence request ER-T6: role-holder check against the E1″ register (Cell-308 Cloud route r1) — prepared for the owner

**Status: PREPARED REQUEST · NOT COMMISSIONED · NO READER APPOINTED.** T6's trigger depends on a fact nobody permitted
has checked: whether any role holder on this route is an E1″ holder (T6 disposition §4, K-T6-4; external B3 M5 and
Y8). The holder list lives in records the coordinator side may not read. This file defines the narrowest reading that
answers the question.

**Limits of this request:**
* It does **not** expand the coordinator side's access.
* The coordinator side does not commission it, appoint its reader or receive the source.
* It asks for no transfer ruling, no provenance review and no risk rating.
* It must not be given to the retired B2 reader.

`new_target_evaluations = 0` · `cell309_activity = none`.

## 1. The question

For each role holder listed in §2, is that holder named as an E1″ holder? Specifically:
* in the formal exposure addendum E1″ (governance A1 S13: `ledger/COORDINATOR_EXPOSURE_DISCLOSURE.md`), as extended by
  governance A1 erratum E1 D3;
* or in the MBS-1 location list that M5 refers to.

## 2. Roles to check (identifiers only)

| # | role identifier | role on this route |
|---|---|---|
| R1 | `claude_cloud_coordinator_20261014`: the coordinating Claude session (ledger label; sessions carrying this label include `session_01S66r3p84SFdY6Vc4RchSWr`) | route drafts, amendment r1–r5, all errata and dispositions, the development layer, the D-* package, N1 / N2 (**route; implementation**) |
| R2 | `claude_cloud_worker_20261016_b1corr` (`session_01VGbYdSMrEaoYpdb386rCWk`) | B1 / B2 correction rounds; matrix R4; owner package R4 (**route**) |
| R3 | `codex_cell308_r5_integration_coordinator`; `fresh_codex_r5_sync_independent_code` | the Codex integration work on PR2 / PR3 (**implementation**) |
| R4 | development review agents of briefs 59–71 (`reviewCLOUD_R1*`, `reviewREVIEW63_REPAIR` … `reviewREVIEW70_REPAIR`) | development reviews (**implementation review, development only**) |
| R5 | reviewerFR1, reviewerFR2, reviewerS12 | formal and risk review (advisory) |
| R6 | B1-External (Codex); B3-External | external conformance and provenance checks |

B2-External is excluded from the check. It already treats itself as an E1″ holder and is retired.

## 3. Who may read, and what

* **Reader:** a person or agent the **owner appoints by name** who is **permitted to read the E1″ register**. Under S13
  that is an existing holder or the owner. The reader:
  * holds, or takes, no route, implementation, caps or qualification role on this route;
  * is not the coordinator side, nor any identifier in §2;
  * makes a phase-1 eligibility statement to the owner first.
* **Allowed reads:** only the E1″ register file and the MBS-1 location list, at a pinned commit and sha256 the owner
  gives. Nothing else. No search of the research namespace.
* **Forbidden:** quoting or paraphrasing any observation, value, time or figure from those records.

## 4. Output (to the owner only)

One Markdown file, `READING_EXTERNAL_ER_T6_ROLE_HOLDERS.md`, containing:
* a header: the reader's identity as recorded, the date, the pinned commit and the sources' sha256 values;
* exposure: actual contact;
* one line per role identifier:
  `R<n>: HOLDER | NOT_LISTED | CANNOT_TELL — <register entry id or line number only>`

  `NOT_LISTED` means not named in the register. It is **not** a certification that the role holder saw nothing.
  `CANNOT_TELL` is used where an identifier cannot be matched;
* no other content.

**Release.** The owner checks the file and releases it with its sha256. The coordinator side records it verbatim after
its tail-figure scan. Any hit returns the file to the owner, unrecorded.

## 5. Effect (prepared in matrix R4 erratum E4; nothing decided)

* **A HOLDER result on R1, R2 or R3** means T6 has fired for this route, and S13 is breached for the texts that role
  produced. Those texts cannot be adopted (A15) or decided on (A17) until a non-holder re-derives them. Re-deriving the
  route would be a new owner process.
* **A HOLDER result on R4 or R5** reduces that review to non-standing for any non-holder requirement.
* **A HOLDER result on R6** means that check does not satisfy its non-holder requirement.
* **CANNOT_TELL on R1–R3** is treated as unresolved. A15 and A17 do not proceed on it.
* **NOT_LISTED on all rows** lets A15 and A17 proceed on this point. It does not certify absence of exposure beyond the
  register (M5's limit).
