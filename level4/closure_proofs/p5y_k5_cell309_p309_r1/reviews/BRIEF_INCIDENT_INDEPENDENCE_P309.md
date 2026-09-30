# Brief: independent incident-independence review of P309 (formal campaign p5y_k5_cell309_p309_r1; before the freeze)

This review instantiates `research/protocol_prep/P309_REVIEW_BRIEFS.md` §1. You are an **independent reviewer**. You
have not produced or coordinated this campaign and you are not an earlier reviewer (R1, R2, R3). Your task is to
decide whether P309 package 1 (candidate rev. 2b) is **temporally and parametrically independent** of the exposed
information recorded in the campaign history. Your verdict gates the freeze.

Paths: FNS = `level4/closure_proofs/p5y_k5_cell309_p309_r1/` (the formal campaign); RNS =
`level4/closure_proofs/p5y_k5_cell309_research_r1/` (the research campaign). Branch: `claude/p5y-k5-cell309-p309-r1`.

## Firewall

* **Allowed reading:**
  * all of FNS;
  * all of RNS, **including** `ledger/EXPOSURE_LEDGER.jsonl` and `ledger/INCIDENT_*`, which this review must read,
    and the preserved drafts in `ledger/incident_309R1_04_drafts/`;
  * the overnight-research incident files and their audit under `level4/closure_proofs/p5y_k5_tail_overnight_research/`
    (`ledger/INCIDENT_*`, any `audit/` or incident review there);
  * `git log`/`git show` metadata of both branches.
* **Exposure.** The incident files may carry numbers for cells 305–309. You may read them for classification. **Never
  reproduce any such number in your review**; disclose only the class of each exposure.
* **Forbidden:**
  * THEOREM_TCT.md lines 12 and 39;
  * any file of the cell-307 or cell-308 campaigns other than their git metadata;
  * any evaluation for cells 305–309;
  * any real-kernel run at drifts in [6/5, 13/5] or its mirror;
  * git writes;
  * modifying anything except your review file `FNS/reviews/REVIEW_INCIDENT_INDEPENDENCE_P309.md`.
* **Executions.** Read-only analysis is expected. If you run anything else, declare it in the review first and ledger
  it to a scratch file.

## Inputs

* `FNS/governance/OWNER_DECISIONS_P309_VERBATIM.md`: the owner decisions (no grant).
* `FNS/governance/INCIDENT_AUDIT_P309_COORDINATOR.md`: the coordinator's audit (not independent).
* `FNS/governance/U2_FACTUAL_RECONSTRUCTION.md`.
* `FNS/start_state/`: the independent reconstruction of research HEAD eb9a9c22.
* `RNS/protocol_prep/`: package rev. 2b (P309_PROTOCOL.md, P309_FORMAL_PACKAGE.md, P309_REVIEW_BRIEFS.md,
  P309_OWNER_DECISIONS.md, P309_CANDIDATE_FREEZE_MANIFEST.json).
* `RNS/ledger/INCIDENT_309R1_0{1,2,3,4}*.md`, `RNS/ledger/INCIDENT_309R1_04_ADDENDUM_DRAFTS.md`, and
  `RNS/ledger/incident_309R1_04_drafts/`.
* `RNS/ERRATA.md` (E-1..E-18), `RNS/reviews/` (R1, R2, R3), `RNS/dossier/` (incl. §G/H), and
  `RNS/registry/ROUTE_SELECTION_RULE.md`.

## Tasks

1. **Each incident.** Cover:
   * overnight 01–03 and residues;
   * 309R1-01, 309R1-02, 309R1-03, 309R1-04;
   * E-3; E-17(a); E-18;
   * the manifest-generator runs;
   * the ledgered necessary reads.

   For each, decide whether P309's design, parameters and route choice are temporally and parametrically
   independent of the exposed information. Use git commit order, not prose.
2. **Result-chasing.** Rate it yourself. The coordinator's MEDIUM-HIGH rating (G1, accepted by the owner) is an input,
   not a bound.
3. **The three rev. 2 rule choices.** Assess each for target independence:
   * the Stage-1a failure mapping (protocol §2.5);
   * the 48 CPU-h budget and its mechanics;
   * the Stage-1b fallback to S_I1 (protocol §3), which the owner adopted under G3.

   The coordinator's adversarial reading is in its audit.
4. **Direct comparison of drafts and package.** Diff the preserved pre-FREEZE_READY drafts against the committed
   package rev. 2b. Say what changed, whether any change could reflect target information, and whether 309R1-04
   (LOW) is correctly classified.
5. **Brief integrity.** Check that every firewalled-reader and reviewer brief is committed or hashed.
6. **U2.** Assess `U2_FACTUAL_RECONSTRUCTION.md`. Is its fact table correct, as far as you can check it inside the
   firewall? Under U2's committed definition, does P309 derive any new quantity from P3 records? Is the owner's
   literal wording ("uses no P3-derived quantity") satisfied, or is it the discrepancy the reconstruction describes?

## Verdict (line 2 of your review file, exactly one of)

* `INCIDENT_AUDIT_ACCEPTED`: list any conditions C1…. The standard wording is "temporal and parametric independence
  only".
* `INCIDENT_AUDIT_REJECTED`: list the reasons.

Line 3 of your review file must be exactly one of:
* `U2_FINDING: NOT_TRIGGERED_CONFIRMED`: no new quantity derived from P3 records, and the owner's ruling is satisfied
  on the facts, including its wording;
* `U2_FINDING: NOT_TRIGGERED_WORDING_DISCREPANCY`: no new P3 quantity, but the owner's literal wording is not
  satisfied; owner confirmation is needed before the freeze;
* `U2_FINDING: TRIGGERED`: a new P3-derived quantity exists; STOP before the freeze.
