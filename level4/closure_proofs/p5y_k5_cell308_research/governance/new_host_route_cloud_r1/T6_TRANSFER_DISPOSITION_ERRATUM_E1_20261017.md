# Erratum E1 to the T6 transfer disposition (Cell-308 Cloud route r1) — after the B3 confirmation (Y5, YC1–YC3)

**Status: AUTHOR CORRECTION · NOT INDEPENDENTLY CONFIRMED · NOTHING RULED.** This erratum corrects
`T6_TRANSFER_DISPOSITION_20261016.md` (`57821984…53ec`), which is preserved unchanged. Where they differ, this erratum
governs. Its source is the B3 confirmation (`reviews/external/CONFIRMATION_EXTERNAL_B3_CORRECTIONS.md`,
`6a721ada…253c`): the Y5 row (line 60), the K-T6 assessment (lines 65–72), YC1–YC3 (lines 76–102), and clarification 1
(line 114). `new_target_evaluations = 0` · `cell309_activity = none`.

## E1.1 — What the correction did and did not do (Y5 PARTLY; clarification 1)

* **Supported.** No transfer is claimed. Owner package R4's T6 item was a placeholder, not a `TRANSFERS_MET` verdict.
  Withdrawing an automatic-transfer position is a **prospective guard**.
* **Corrected scope of the earlier claim.** §2's "a search of the route governance texts finds no statement …" was the
  coordinator side's own search. B3 could verify only the placeholder within its allowlist, and the search is **not
  independently reproduced**.
* **Not resolved by the correction:** T6 applicability, satisfaction of any historical condition, role-holder
  eligibility, and whether any continuation route is permissible. **Y5's block on any `TRANSFERS_MET` claim
  remains.**

## E1.2 — K-T6-1 … K-T6-4 are proposed analyses (YC1–YC3)

| # | correction |
|---|---|
| K-T6-1 (M3) | The cycle exists only **if** M3's satisfaction were required at A14. The transfer question is answered **UNMET**, which needs no pretence that M3 is met. C1-M3 is a **proposed prospective check**. It neither satisfies historical M3 now nor validates the package |
| K-T6-2 (code-level trace) | **Withdrawn.** The split moved a governing pre-decision requirement to B9-T without an inventory. Replaced by `POLICY_PROVENANCE_INVENTORY_YC1_20261017.md`: policy items are traced before their decision, and later artifacts are checked later. B9-T is only an additional conformance check |
| K-T6-3 (M2) | "Later stages cannot produce it" means only that M2 is a **historical** timing condition of the original case. It does **not** claim that relevant historical evidence can never be found or assessed by an appropriately authorized reader. Later discovery of evidence would not retroactively satisfy a historical timing condition. The current record establishes neither satisfaction nor failure |
| K-T6-4 (holder status) | As ER-T6 r2: a register lookup gives a bounded register result only. NOT_LISTED is register absence, not verified non-holder status. Grouped and unmapped identities stay explicit. Re-deriving text does not undo a role / exposure combination |

## E1.3 — §5's scoped determination: what each item is (YC3)

| item | what it is | what it is not |
|---|---|---|
| 1. No automatic historical transfer | an owner choice **not to claim** something | evidence that T6 does not apply; validation of any continuation path |
| 2. T6 and S13 unamended | keeps accepted text as it is | a qualification of any role holder |
| 3. Role-holder status per ER-T6 | ER-T6 r2's bounded register result | a clearance for adoption (ER-T6 r2 §5) |
| 4. The prospective package | a **new** proposal. It needs a separate eligible external review, the applicable material-change determination (statement 1A), and the owner's adoption | confirmed or reviewed by B3. The B3 confirmation is **not** that review |

The continuation wording ("the route continues on one owner-controlled host …") is a **proposed direction**. Every
unresolved gate still applies to it.
