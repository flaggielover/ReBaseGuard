# Owner decision E-5: the A14b consequence, option (a) (Cell-308 Cloud route r1), 2026-10-22

**Status: OWNER DECISION (the owner's words recorded verbatim in §1) · RECORDED BY claude_cloud_recorder_20261022.**
§1 is the governing text. §2 and §3 apply it, and §1 prevails over them if they differ. §3's file-level
identification is the recorder's application, and the owner may amend it. `new_target_evaluations = 0` ·
`cell309_activity = none`.

## 1. The owner's decision (verbatim, as the owner issued it on 2026-10-22)

> The owner chooses to continue Cloud route r1 and selects A14b consequence option (a).
>
> Record the owner decision that the A6b trace is input only and does not adopt any item. Because the trace returned MISSING_PRIMARY_SOURCE, FREE_CHOICE, and NOT_DETERMINABLE results, and because T2 identified omitted policy rules, no affected output authored by R1a, R2, or R3a in a covered function may be adopted yet.
>
> Require an eligible non-holder outside the coordinator's reach to independently re-derive or confirm the affected texts before adoption. Define the scope explicitly, including the YC1 inventory, the D-* package, the development/integration layer, and the L-DET reference list if A16 applies. Preserve the rule that re-derivation does not cure any later-proven role or exposure violation.

## 2. The decision, item by item

1. **Continuation.** Cloud route r1 continues. V-C stays available, and stays deferred.
2. **The A6b trace is input only.** `reviews/external/TRACE_EXTERNAL_A6B_POLICY_PROVENANCE.md` (sha256
   `c91c7ff9…4b7`) adopts no item, consistent with owner statement 7 item 5. It returned 0 TRACED, 2 FREE_CHOICE,
   14 MISSING_PRIMARY_SOURCE and 1 NOT_DETERMINABLE results. Its T2 list names policy rules the inventory omits.
3. **The consequence (option (a)).** No output authored by R1a, R2 or R3a in a covered function (route, implementation
   or caps; statement 4 MA3) may be adopted until the condition in item 4 is met. Rows R1a, R2 and R3a remain
   UNRESOLVED (statement 5). This decision makes no HOLDER finding.
4. **The condition for adoption.** Before any such text is adopted, an **eligible non-holder outside the coordinator's
   reach** must independently re-derive or confirm it.
   * Eligibility is determined individually by the owner under statement 4 MA2, on a disclosure, as for A6b
     (statement 7).
   * This decision names no re-deriver.
5. **Scope:** the texts listed in §3.
6. **No cure.** Re-derivation or confirmation does **not** cure any role or exposure violation that is later proven.
   This preserves `reviews/external/CONFIRMATION_EXTERNAL_B3_CORRECTIONS.md` line 72, ER-T6 r2 §5 and statement 5.
7. **Non-effects.** This decision does none of the following:
   * issue statement 1, 1B, 1A or 2;
   * make the T6 ruling (A14);
   * adopt any D-* item, route text or traced result;
   * rerun A6b;
   * read the register;
   * appoint a re-deriver;
   * name a host;
   * create a grant;
   * freeze the route;
   * begin execution.

## 3. Scope of the re-derivation or confirmation (recorder's application of §1)

### 3a. Named by the owner

| # | scope item | files (paths under `G/` = `level4/closure_proofs/p5y_k5_cell308_research/governance/new_host_route_cloud_r1/` unless shown) | why it is affected |
|---|---|---|---|
| S1 | **the YC1 inventory** | `POLICY_PROVENANCE_INVENTORY_YC1_20261017.md` | coordinator-authored and unconfirmed (inventory lines 3, 34–36). Trace T2 lists omissions, and they must be added and traced or confirmed |
| S2 | **the D-* package** | `CONSOLIDATED_DSTAR_PACKAGE_R2_20261016.md` with errata E1 and E2 | R1a route design (`A14B_ROW_DISPOSITIONS_R1_20261017.md` line 54) |
| S3 | **the development / integration layer** | `NS/streams/CLOUD_R1_LINUX_DEV/` (`lx_platform.py` sha256 `da32ce8c…6389`, plus `lx_inventory.py`, `lx_verified.py`, `lx_portmap.py`, tests and results, `INTEGRATION_DEV_STATUS_CODEX_20261015.md`) | R1a dev implementation and R3a integration (A14b r1 lines 54, 57). The code-level constants a13–a23 are in it (trace T1) |
| S4 | **the L-DET reference list, if A16 applies** | `PROPOSED_LDET_REFERENCE_ADDENDUM_R1_20261015.md`, with `LDET_SPECIFICATION_PACKET_ERRATUM_E1_20261016.md` §5 and erratum E2 §E2.5 | compiled by R1a (L-DET packet lines 81–84). FR1's earlier re-derivation (erratum E1 line 83) does not meet item 4, because FR1 (R5a) is excluded for uses that need a reviewer outside the coordinator's reach (statement 5 line 19) |

### 3b. Further affected texts identified under item 3

These are the remaining texts that statement 2 would adopt (owner package R4 lines 97–103, as amended by erratum E1
lines 65–69 and erratum E2) and whose author is R1a or R2 in a route or implementation function:

| # | text | author basis |
|---|---|---|
| S5 | `PROPOSED_ROUTE_AMENDMENT_CLOUD_R1_A1_R5.md` with errata E1 and E2 | R1a route design (A14b r1 line 54) |
| S6 | `OPERATIONAL_WRAPPER_READER_PINPOINT_REQUIREMENTS_20261016.md` | R1a implementation design. Trace items a6–a12 are in it |
| S7 | `NEW_CONSTANT_RECOMMENDATIONS_20261016.md` with erratum E1 (N1, N2) | R1a route numbers |
| S8 | `LDET_SPECIFICATION_PACKET_20261016.md` with errata E1–E3 | R1a route design. Erratum E3 came in the B1 correction round, in which R2 changed route texts (A14b r1 line 56). Which errata R2 wrote is not established here |
| S9 | `HOST_EVIDENCE_PLAN_H1_H8_20261016.md` with errata E1 and E2 | R1a route design |
| S10 | `HOST_ATTESTATION_ACCEPTANCE_PROCEDURE_R3_20261016.md` with errata E1 and E2 | R1a route design. Erratum E1 came in the B1 correction round (as for S8) |
| S11 | the route-level rule texts B3 traced (T01–T11, N1–N2, X01–X09, Z01–Z06, O01–O30), with the concrete subrules from trace T2 | B3's trace is advisory and was done by B3, not by an eligible re-deriver under item 4 |

### 3c. Not treated as covered-function outputs (the owner may reclassify)

These are records, not route design:
* receipts;
* releases;
* transmissions;
* dispositions;
* the readiness matrix and its errata;
* the findings registers;
* owner packages and briefs;
* the OD-1 recommendation, which is advice.

They are not re-derived. Any rule, number or sequence in them that statement 2 would adopt falls back under §3b,
item S11.

### 3d. What each re-derivation or confirmation must supply (from the trace results; application only)

* **MISSING_PRIMARY_SOURCE** items: the named primary source, or the re-deriver's own independent derivation, cited
  (trace T3).
* **FREE_CHOICE** items (a12, a20): the re-deriver's independent confirmation of the choice, or its replacement.
* **NOT_DETERMINABLE** (a19): a classification as policy or as implementation artifact, then confirmation.
* **T2 omissions:** each added to the inventory and treated as above.
* The re-deriver's brief, allowlist and appointment are **not** prepared or issued by this decision.
