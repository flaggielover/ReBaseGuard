# Erratum E1 to the dependency and evidence handoff (Cell-308 Cloud route r1): after the ER-T6 lookup

**Status: PREPARED HANDOFF · AUTHOR CORRECTION · NOTHING APPOINTED, COMMISSIONED, ADOPTED OR EXECUTED.** This erratum
amends `DEPENDENCY_EVIDENCE_HANDOFF_20261017.md` (`ac98ab91…05a1`), which is preserved unchanged. Where they differ,
this erratum governs. `new_target_evaluations = 0` · `cell309_activity = none`.

## E1.1 — The chain, updated (replaces handoff §2)

| step | requirement | actor | state |
|---|---|---|---|
| 1 | ER-T6 r2 bounded register lookup (A14a) | dedicated reader appointed by the owner | **done** (`e2bcb406…dcbc4`). Not repeated |
| **2** | **owner statement 4: the A14b criterion** (MA1–MA4 of `A14B_ELIGIBILITY_EVIDENCE_TABLE_20261017.md`), with the owner's Q1 identity facts | **owner** | **next.** No accepted text supplies the criterion |
| 3 | A14b applied per row, under that criterion | owner | blocked on step 2 |
| 4 | A6b policy-provenance trace | an eligible appointee (E1.3) | blocked on steps 2–3 for the appointee, and on an appointment |
| 5 | statement 1A (material change; S12X if "material") | owner | open; no verdict prepared |
| 6 | statement 2 (T6 ruling items 3–4, adoption, D-*, N1 / N2, MBS-6/7/8) | owner | steps 3–5; A14p if the package is adopted |
| 7 | statement 3, then OD-1 and the host stage | owner | step 6 |

Statement 1 and statement 1B (items 1–3 and 5, and item 4 as E1.4) may issue in parallel.

## E1.2 — Handoff §3 is closed

The register's path and snapshot were fixed by the owner's appointment (commit `00d4df45…`). The digest and blob were
computed by the reader and are recorded as **reported** (receipt §3). Handoff §3's "MISSING" entries are superseded on
that basis. The coordinator side has not verified the register binding, and does not.

## E1.3 — A6b eligibility (replaces handoff §4 "Eligibility")

All of the following:
* fresh;
* not B1, B2, B3, the ER-T6 reader or any coordinator session;
* appointed by the owner;
* a C2 disclosure, plus whatever the owner's MA2 standard requires, **before** starting;
* the owner's A14b determination for that appointment.

**"Outside the coordinator's session, account and control"** stays a requirement. The ER-T6 reader shows that a Claude
Code cloud session the owner launches on this account runs in the coordinator's own environment
(`env_01GTgmTdDaUY28GtoGZVi3QY`). Such a session does not meet the requirement. A launch on a different platform or
account, as for B1 and B3, is the form consistent with it. Its isolation is still not certified.

**"The step-1 register lookup run on them before they start" is withdrawn.** Because of the register's
conduct-defined classes ([K], L92 and L122), a lookup on a new name returns CANNOT_TELL by construction, and would
only expose another reader to the register. The appointee's standing is decided under MA2 instead.

The A6b scope and its allowlist at `58769a0f` (handoff §4) are **unchanged**. The policy inventory has not changed
since that pin.

## E1.4 — Replacement text for statement 1B item 4 (owner package R4 erratum E2 §E2.1)

> 4. **ER-T6 r2.** I appointed a dedicated metadata reader for the bounded lookup, against source snapshot
>    `00d4df454f67dd1c26f34d68c14296f67896010b`. Its report (`e2bcb40660129665ed1ad5b45b80e578168ed5904c4e12a17d3ee2f2f68dcbc4`)
>    is recorded. It is a bounded register result per individual identifier, and clears nothing by itself. I do not
>    certify the reader's isolation.

This is a factual update for the owner to issue or amend. It is not issued here.
