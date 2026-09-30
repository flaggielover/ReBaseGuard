# Follow-up brief 1: band-scoped verifier variant (committed before issue)

**Recipient:** the verifier's author. **Basis:** `fc2/FC2_SPEC_R2_ERRATUM_1.md`. All rules of
`reviews/BRIEF_FC2_VERIFIER_VARIANT_AUTHOR.md` still apply, including the firewall, "never create any ref under
refs/p5y-k5-cell309-p309-r1/", "REAL-band tests are dry", "no git writes" and "ledger every execution".

## Changes requested (minimal)

1. **E1-1, strict descendant.** In official-mode check 7, allow refs that point at the grant commit itself. Refuse only
   refs that point at a commit having the grant commit as a proper ancestor, other than the marker and the current
   branch. Update your N7 test:
   * a ref at G itself must now ADMIT, when everything else is valid;
   * a ref at a child of G must still REFUSE.
2. **E1-5, `--out`.** Give `verify/run_verify_all_scoped.py` an `--out PATH` option. The default stays
   `verify/VERIFY_RESULTS_SCOPED.json`.

Change nothing else.

## Then

* Re-run the self-tests and the FC2 tests (`tests/test_verify_scoped.py`), and I1 if the admission code changed.
* Update `verify/README_VERIFY_SCOPED.md` with the new sha256 values and results.

Report:
* the new sha256 of every changed file;
* the diff summary;
* the test and I1 results.
