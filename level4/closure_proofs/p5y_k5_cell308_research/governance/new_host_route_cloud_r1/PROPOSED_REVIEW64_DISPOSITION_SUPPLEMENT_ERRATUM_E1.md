# Erratum E1 to the proposed review-64 disposition supplement

**PROPOSED_NOT_ACCEPTED_NOT_IN_FORCE · DEVELOPMENT ONLY.** This erratum corrects
`PROPOSED_REVIEW64_DISPOSITION_SUPPLEMENT_20261015.md`, which is not edited. It accepts and decides nothing. All 21 D-*
decisions remain undecided, and A1, A2 and A5 remain unmet.

## E1.1 The K1 row's shallow-clone statement was false

The supplement's K1 row said: "In a shallow clone the boundary commit is shown as introducing every file it holds, so
an order hidden by the cut refuses and is never accepted. A separate shallow check would have been an equivalent
mutant, so it was dropped."

* That reasoning covered only the **order rule** (`_ordered`).
* It did not cover the **history-wide veto** (`_historical_review_blobs`). In a shallow clone, `rev-list --full-history`
  cannot reach commits before the boundary.
* **Reproduction**, owner-reported and confirmed by the coordinator at `68a38c64`, with `lx_platform.py` sha256
  `f4d7f2c9…`, byte-identical to `b23ee7dd`:
  1. Commit a valid synthetic attestation.
  2. Commit a rejecting review.
  3. Delete that review.
  4. Commit a valid acceptance.
* **Result:** the full repository refuses through the historical rejection. A depth-2 clone has the identical HEAD tree
  (`rev-parse HEAD^{tree}` equal) but hides the deleted rejection, so it **accepted**.
* The dropped check was therefore **not** equivalent. Removing it reopened a bypass of the permanent-rejection rule
  (review 63 H3) in shallow clones. Review 64 K1 had recommended refusing in a shallow repository. The coordinator's
  removal contradicted that recommendation and was wrong.

## E1.2 Repair (development source after `68a38c64`)

* `_history_complete(repo_root)` is True **only** when `git rev-parse --is-shallow-repository` prints exactly `false`.
  A shallow clone, a failed call, or any other output is not evidence of a complete history.
* `_acceptances` refuses first, with `UNAVAILABLE: history completeness not established (shallow clone or
  unreadable)`, when completeness is not established.
* The git isolation is unchanged: `log.showRoot` is forced, global and system configuration, attributes, replace refs
  and grafts are excluded, and the pickaxe runs without textconv or ext-diff.
* **Test** `test_review64_shallow_history_refuses_deleted_preboundary_rejection`:
  * a full history with a deleted rejection refuses, and the reasons name the historical rejection;
  * a valid full-history acceptance is accepted (positive control);
  * a genuine depth-2 clone with an identical HEAD tree refuses as unavailable;
  * an unreadable completeness answer refuses as unavailable.
* **Mutants:**
  * RV29 removes the guard: the shallow clone accepts.
  * RV30 counts an unreadable answer as complete.
  * Both are KILLED under the harness's strict criteria.

## E1.3 Restated L-LIFE side effect (replaces the K1 row's shallow sentence)

Acceptance requires positive evidence that the reading repository's history is complete (not a shallow clone). A
shallow clone refuses as unavailable evidence, whatever its HEAD tree. Other means of truncating or rewriting history
are outside what the code can see: grafts and replace refs are disabled, but a rewritten or force-pushed history is
not detected. The ledger binding (D-HOST-LIFETIME item (i)) remains the carried remedy.
