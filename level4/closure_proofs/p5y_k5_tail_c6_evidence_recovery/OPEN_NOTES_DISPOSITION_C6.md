# Disposition of the C6 review and adjudication conditions

Forensic review: `review/REVIEW_C6_FORENSIC.md` — `READY_TO_ADJUDICATE_WITH_NOTES`, seven required corrections.
Adjudication: `evidence/adjudication/C6_ADJUDICATION.md` — **ACCEPTED_WITH_SCOPE_LIMITATION**, fourteen
conditions, eleven findings. Every adjudicator finding was **re-measured by C6 before being acted on**.

## The fourteen conditions

| # | condition | disposition |
|---|---|---|
| 1 | do not read A1 as replayable; record it in E1's class gap | **Done at source.** `A1.C6_CLASSIFICATION = GATE_CLASS_GAP__inputs_regenerable_result_never_derived`, with `replayable_scope: "the INPUTS only. Never the gain."` and the rejection recorded. |
| 2 | strike C5's Condition 11(b) as falsified | **Binding, and recorded.** *"Retrieve the K1 object candidate payloads from the external record store"* directs a successor at payloads that do not exist — 0/326 under twelve alternatives, longest JSON array 10, 0/10 in git. C5's A1 `kill_reason` is likewise false. **This is C6's principal result.** |
| 3 | correct C5's A1 `new_real_required: false` | **Recorded** in the B0 audit as `c5_A1_new_real_required_is_contradicted_by_C6`. Binding on the successor: C6 does not edit C5. |
| 4 | correct the `subdivision_depth` statement | **Done, re-measured.** Integer `0` at `/producer/runtime/subdivision_depth` in all four. Erratum E4 records that C6 had adopted the reviewer's "null" unverified. |
| 5 | finish corrections 6 and 7 in the classification | **Done.** A1's `ever_serialized` qualified to the polynomials; B1's flat "24-iteration" replaced by the per-cell counts. |
| 6 | carry C5's two exhaustion scope limits alongside any ranking | **Done** — see the note below; `x_lo > 0` fails at cell 0, and C5's exhaustion is of the transport family only. |
| 7 | host provisioning is a separately governed prerequisite | **Done, and it changed the ranking.** Re-measured: the worker lacks the entire stack. No certifying host exists in scope. Recorded as requiring the **user's** decision, not a campaign's. |
| 8 | sequence a C7 as E2 first | **Done.** The ranking is re-ordered: E2, then host provisioning, then E1, then A1. |
| 9 | successor gate must add the missing class and freeze before the evidence phases | **Binding on the successor.** The gate is frozen and not amended; the defect is erratum E1. |
| 10 | no P3 object may be adopted as new scientific evidence | **Binding, already satisfied.** All four are P3 with `admissible_for_NEW_scientific_reuse: false`; the two failing links are now computed and the anomaly localised in the manifest. |
| 11 | no cell closed, no r6, no exhaustion, no R-stage | **Binding, satisfied.** All four withheld; verified independently by the adjudicator. |
| 12 | do not cite the recovery as a scientific gain | **Binding, and C6 says so itself** in erratum E3. Cite the falsification, the D4 repair and the B1 proof. |
| 13 | verify reviewer findings before absorbing them | **Adopted immediately.** Every one of the adjudicator's eleven findings was re-measured before being acted on — including N1 and N9, both confirmed. |
| 14 | no hard-coded conclusions in a forensic artifact | **Done.** `all_committed` checks `git ls-files`; the audit-link verdicts compute; external observations moved to the inventory with their command; `B0_18` asserts an independent property. |

## Notes carried to a successor

* **C6-N1.** There is **no certifying host in scope**. Local and `rebaseguard-vultr-02` both lack numpy, scipy,
  flint, mpmath, sympy and gmpy2; AWS is forbidden. A1 and E1 are blocked on **every permitted host**, not on one.
* **C6-N2.** **A1 is harder than C5 believed.** Not a retrieval: the payloads never existed, a faithful
  regeneration returns the adopted numbers exactly, and the tightening has never been computed. It needs a host,
  a producer protocol permitting a non-identical sup, and unknown slack in the certifier's sup routine against a
  known 2.0562 % (C5-T) requirement.
* **C6-N3.** Carry C5's scope limits with any ranking derived from C6: C5-T's premise `x_lo > 0` **fails at cell
  0** of both detectors, and C5's exhaustion is of the **transport family only** and may never be restated as
  deterministic exhaustion.
* **C6-N4.** The provenance anomaly is **localised in the export manifest**: the committed and external
  `COMPOSITE_AUDIT.json` agree at `2ec4dcbb…` and the manifest names a third value, `fa1d79b5…`. That manifest
  carries all 326 record hashes. Treat it as a standing provenance risk, not a curiosity.
* **C6-N5.** Raising the four records above P3 requires first establishing the semantics of `production_run` and
  `result_bearing` in the Aux5 schema. C6 records them verbatim and refuses to interpret them.
