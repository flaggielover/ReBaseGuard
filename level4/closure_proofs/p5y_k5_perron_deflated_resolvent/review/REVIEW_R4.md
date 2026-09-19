# Independent review r4 (freeze readiness of 296c0853)

**Verdict: NOT_READY for one procedural reason with a one-line fix; READY_TO_FREEZE once fixed, no further review needed.**
Nothing affects soundness.

- Blocking: `consume` wrote `evaluation_head` into the hashed result, so the adjudicator's byte-identity re-run at the seal
  head could never match, and after the freeze (F1) the brief could no longer be changed.
- B1 RESOLVED (falsification gate r2 extremes match the reviewer's independent dense scans: block slack +0.00204 at
  (0.8985, 0.1015); λ ratio 0.95039 at (0.901, 0.099); ARL slack +3.3e-5); F1, F2, F3, F4 RESOLVED; F5 resolved apart
  from the step-6 wording.
- Notes: P5/P6 were tautologies (relabel or run the job functions on mutated artifacts); qualification and adjudication
  clones need full history; after vultr-02 is restored, confirm the runtime strings still match `certifier_runtime`.

## Disposition (before the freeze)

| item | disposition |
|---|---|
| blocking (evaluation head in the hashed result) | removed from the result; the head is recorded only in the ledger; the result is a pure function of the frozen inputs; the brief says so |
| P5/P6 tautologies | P5 and P6 now run `_block_job` / `_cell_job` on mutated artifacts (C_T = 0.999 max w; Ā = 0.9999 W(a)); both are flagged (`evidence/precheck_r1/FALSIFY_R2b_cells0_148.json`) |
| full-history clones | qualification and adjudication use full clones from GitHub |
| runtime strings | S00 checks them; if they drift, the protocol is regenerated under a new freeze, never edited |
