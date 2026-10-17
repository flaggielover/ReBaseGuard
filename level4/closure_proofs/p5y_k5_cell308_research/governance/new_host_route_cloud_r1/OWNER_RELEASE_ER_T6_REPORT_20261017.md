# Owner release and receipt: ER-T6 r2 bounded register-metadata lookup (Cell-308 Cloud route r1), 2026-10-17

**Status: RECEIPT OF AN OWNER-RELEASED EXTERNAL READING · RECORDED VERBATIM · BRINGS NOTHING INTO FORCE.**

Neither the report nor its release does any of the following:
* make an owner eligibility determination (row A14b);
* adopt ER-T6 r2 or any rule;
* find that anyone has no exposure, or that anyone is a non-holder;
* rule on T6 applicability;
* accept the reader's infrastructure or control isolation;
* authorize any scientific or formal step.

`new_target_evaluations = 0` · `cell309_activity = none`.

## 1. The released file

| item | value |
|---|---|
| recorded at | `reviews/external/READING_EXTERNAL_ER_T6_ROLE_HOLDERS.md`. Byte-identical to the decoded bytes (`cmp`). Not previously present in the repository |
| required length and sha256 (owner) | 16,213 bytes; `e2bcb40660129665ed1ad5b45b80e578168ed5904c4e12a17d3ee2f2f68dcbc4` |
| recomputed (raw bytes) | 16,213 bytes; `e2bcb40660129665ed1ad5b45b80e578168ed5904c4e12a17d3ee2f2f68dcbc4`: **MATCH**. One final LF |
| transmission | The owner's release message, committed unchanged as `OWNER_TRANSMISSION_ER_T6_REPORT_20261017.txt` (18,132 bytes, sha256 `c559f67bd204fb836cf8819dc222a309af0cb3ea897557ce110fb6a0c6db70f1`). The fenced block was extracted programmatically from the uploaded file. Nothing was retyped. It was decoded in fresh scratch as data only (Python standard-library `base64` and `gzip`, run with `-I`). Nothing was run |
| tail-figure check | Run by process before reading, counting hits only (`ledger/TAIL_FIGURE_PATTERNS.json`). **0 hits** in the report and **0** in the transmission. A scan pass does not verify any quotation |
| reader | **ER-T6-Metadata-Reader.** By its own account (report §1), a Claude Code cloud session `session_01RQPL4w9cd4o1evySZeqLTq`, environment `env_01GTgmTdDaUY28GtoGZVi3QY`, launched by the owner. It is a delegated AI reader, not the owner personally. **Its role ended with the report.** It takes no later role |
| index | The external-evidence convention has no index file beyond the ledger. The ledger entry is the index row |
| repository state at recording | integration head `00d4df454f67dd1c26f34d68c14296f67896010b` (no newer commits on the remote); PR3 open, **draft, unmerged**; PR2 `3b244277`; base `37c62102` |

## 2. Result, recorded as the report states it (report lines 3–4 and 129–156)

* **The bounded lookup is COMPLETE.**
* **24 subject rows: all CANNOT_TELL.** The two R3c sublabels are also CANNOT_TELL.
* **0 HOLDER. 0 NOT_LISTED.**

The report gives the basis codes (§5):

| code | meaning |
|---|---|
| [N] | no literal name match in L1–L128 |
| [K] | two **conduct-defined** holder classes: L92, "later readers of the chain", and L122, "every agent that read one of the locations above". Because of them, the absence of a name does not show that a subject is outside the holder list |
| [U] | the register's holder "coordinator" is defined only as "the main agent of this session" (L3). It is not mapped to any participant |
| [A] | `reviewerS12` vs. `reviewINC2` (L118): a possible alias, not matched |
| [M] | R1b and R3c are unresolved upstream |

**What this result is not:**
* It is not an empty holder register. The register names nine holder identifiers or roles and two classes (report
  §3.3).
* It is not proof that no current participant is a holder.
* It is not clearance for adoption.
* CANNOT_TELL is not proof that anyone is a holder, or is ineligible.
* The register's word "coordinator" is **not** mapped here to this session, or to any other session, on the strength
  of the shared role name.

## 3. Reported bindings: recorded as reported, not upgraded

| item | as reported by the reader (report §3.1, §3.2) | status on the coordinator side |
|---|---|---|
| register snapshot | commit `00d4df454f67dd1c26f34d68c14296f67896010b`, path `level4/closure_proofs/p5y_k5_cell308_research/ledger/COORDINATOR_EXPOSURE_DISCLOSURE.md` (selected by the owner) | — |
| register bytes and digest | 10,275 bytes; sha256 `cc0b0be8c3d989bbe0105ad9660706b459c443a0374bef726191e1dc93e9d53f` (computed by the reader; no expected digest was supplied); blob `a4def0a8da563cff84d98f360ea464a60b1aeb29` (computed from the bytes; not cross-checked against a tree) | **REPORTED.** Not verified by the coordinator side. The coordinator does not fetch, read, grep, hash or list the register (exclusion unchanged) |
| MBS-1 location list | contained in the register, L110–L124; no separate document bound; no location followed | **REPORTED** |
| request and governance files A–D at `58769a0f` | blob, length and sha256 for each (report §2) | **CORROBORATED.** These are permitted files. The coordinator recomputed blob, length and sha256 for all four at `58769a0f`. All four equal the reader's values |

**Disclosure.** Before writing this receipt, the coordinator attempted a counts-only check of whether its own ledger
already records the register's digest or blob id. That would have checked a reported register binding against a
second source, which this release does not permit. The session's permission system refused the command, and it did
not run. It was not retried and no other method was used. Nothing about the register was learned.

## 4. The reader's boundary, and the reader's disclosures, preserved

* **Q5 (platform / control independence): UNVERIFIED** (report §1). The coordinator side adds one fact from its own
  session metadata: **this coordinator session runs in the same environment, `env_01GTgmTdDaUY28GtoGZVi3QY`**.
  * The coordinator does **not** assume it cannot reach the reader. Its session tools can list same-account sessions.
  * Since the reader was launched, the coordinator has made **no** cross-session call about it (no list, describe,
    event read or message). The released report is the only evidence used.
* **Automatic contact** (report §7):
  * the repository was cloned automatically when the reader's session started;
  * the checkout was unread by the reader;
  * what the harness itself read from it is UNVERIFIED.
* **What the reader holds.** The register's names and locations; two clock-time anchors of audit and logging events
  (L89, L91, L126); and one committed historical figure (L37), which is not an MB r1 target-run observation.
  * These are not reproduced anywhere here.
  * "No target runtime or host values were reported" is **not** read as "no exposure occurred". The reader states it
    cannot assert that.

## 5. Finality

ER-T6 r2's bounded lookup is done. **It is not repeated**, no replacement reader is sought, and no review is opened to
seek a NOT_LISTED result. The reader stays retired from every later role. The B3 round stays closed.
