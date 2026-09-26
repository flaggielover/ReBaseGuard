# C11RD — authoritative N9 adjudication (cell 306, six operator constants)
N9_CLOSED

| item | value |
|---|---|
| adjudicated evidence | frozen comparison `evidence/comparison/C11RD_COMPARISON.json`, committed alone in `8e2defab13451654a87a859e1b24fb1b28dc9494` (file sha256 `8a9637b6…`, embedded body sha256 `f69c2bf0…`), COMPARISON_ACCEPTED at `902653493dfd75d2075a7ed9373919a600c9dbcd` |
| C11RD chain | freeze `ce5b85959a1693525f9e001e7c191516a4ee7d76` (READY_TO_QUALIFY `3c1eff11`) → qualification `e627d4ec` (QUALIFICATION_ACCEPTED `e27c2ffd`; the rejected `3addf9d3`/`89330534` historical) → authorization A `6bab71b9` (AUTHORIZATION_ACCEPTED R `e320d8f5`) → grant G `4b716d43` → sealed execution `4547bcd4` (EXECUTION_ACCEPTED `db1c6118`) → comparison `8e2defab` (COMPARISON_ACCEPTED `90265349`) |
| C11R chain (historical, immutable) | comparison `2c24a989` (AGREEMENT_INSUFFICIENT; blob `5269c2aa…`), COMPARISON_ACCEPTED at `7375b9cd` (`VERDICT: COMPARISON_ACCEPTED`), N9 adjudication `118008f5` (N9_REMAINS_OPEN); sealed F_H runs blob `a5351603…` (EXECUTION_ACCEPTED `22537709`) |
| C11 (historical, immutable) | `README.md` and `evidence/n9/C11_N9_RESULT.json`: `EXECUTION_INVALID`, N9 OPEN; `review/ADJUDICATION_C11.md` |
| frozen authorities | N9 wording: C2 adjudication `p5y_k5_tail_c2_closure/evidence/adjudication/C2_ADJUDICATION.md:501`, frozen verbatim in C11R's statement table (blob `58b4066f…`, `N9_wording`); C11R's gate `config/N9R_GATE_C11R.json` (`SCOPE`, `forbidden_conclusions`); C11RD freeze `protocol/C11RD_FREEZE_R1.json` (`L_agreement_criterion.n9`, `U_comparison_procedure`, `FORBIDDEN`, `R/S/T`); C10 governance on the C2 floor |
| adjudicator | the C11RD campaign author (Claude Opus 5.5 via Claude Code), on the user's explicit instruction, 2026-09-26, after a read-only mechanical audit of the C11 → C11R → C11RD chain; a fresh read-only adjudication review follows. |
| scope | adjudication only: no science was run, no comparator was re-run, no value was recomputed by any new formula, no historical verdict was edited, no cell adopted, no coverage map created or changed. This document states classes and ratios only, no D1/D2 magnitude. |

## 1. The frozen definition of N9

* **Wording** (C2 adjudication, line 501; frozen in C11R's statement table as `N9_wording.text`):
  *"a second, independently written certifier reproducing the six operator constants for cell 306
  (closing N9)"*. The table records `constant_count` 6 and `target_cell` 306, and that the
  adjudicator's "six" governs closure (wider than the supersolution surface named in
  `OPEN_NOTES_DISPOSITION_C2.md`, N9).
* **Closure criterion** (C11R gate, `SCOPE.N9_closure_requires`, frozen before any target run):
  *"all six constants for cell 306 classified AGREES or STRONGER, each with an EQUIVALENT or STRONGER
  statement"*; *"if D1 and D2 are not independently certified, N9 remains OPEN whatever the other four
  constants yield"*; D1/D2 need *"a later prospective derivative-system extension"*.
* **Agreement rule** (C11R statement table, `comparison_semantics_frozen_before_results`, factor 2,
  unchanged in the C11RD freeze `L_agreement_criterion`): UPPER_BOUND — STRONGER if independent ≤
  original, AGREES if original < independent ≤ 2 × original, else INSUFFICIENT; LOWER_BOUND — the
  mirror; SAME STATEMENT BEFORE SAME NUMBER; an exactly equal value is INVALID (copied).
* **Independence** (C11R statement table, `DEPENDENCY_FINDING`): D_lo, D1 and D2 are conditional on
  C_T and tau; an independent certifier must not consume the ORIGINAL's C_T and tau, but must first
  certify its own via Khat_e and then propagate with those.
* **Reassembly** (C11RD freeze `L_agreement_criterion.n9`, frozen before any target magnitude):
  *"N9_CLOSED iff all six constants (C_T, tau, Abar, D_lo from C11R's accepted comparison, read not
  recomputed; D1, D2 from C11RD) are AGREES or STRONGER"*; precedence INDEPENDENCE_VIOLATION >
  SCIENTIFIC_DISAGREEMENT > EXECUTION_INVALID > N9_CLOSED > AGREEMENT_INSUFFICIENT.

## 2. Five layers, kept separate

| layer | record | result |
|---|---|---|
| **A. Historical C11** | `p5y_k5_tail_c11_n9_independent_certifier` (unchanged) | **EXECUTION_INVALID**; N9 OPEN. Its adjudication: the certifier was independent and sound, but the comparison was void (wrong constant, a scalar drift, cell 307 and one constant, no blinded comparison). |
| **B. Historical C11R** | comparison `2c24a989`, review `7375b9cd`, adjudication `118008f5` (unchanged) | frozen comparison **AGREEMENT_INSUFFICIENT**; adjudication **N9_REMAINS_OPEN**. C_T AGREES, tau AGREES, Abar STRONGER, D_lo AGREES; D1 and D2 INSUFFICIENT with `NO_INDEPENDENT_STATEMENT` (NOT_IMPLEMENTED by design). |
| **C. C11RD successor evidence** | freeze → qualification → authorization → one execution → seal → execution review → one comparison → comparison review | one CERTIFIED execution (COMPLETED_CERTIFIED, sealed `4547bcd4`), EXECUTION_ACCEPTED; D1 and D2 statements EQUIVALENT (domain EQUAL, premises SAME) |
| **D. Mechanical comparator result** | `8e2defab`, COMPARISON_ACCEPTED `90265349` | D1 **STRONGER** (ratio 0.45362884480385873), D2 **STRONGER** (ratio 0.0557333083728129), factor 2; six classes C_T AGREES, tau AGREES, Abar STRONGER, D_lo AGREES, D1 STRONGER, D2 STRONGER; no independence violation; U7 leak check 42 files, 0 hits; the comparator's field `N9_VERDICT` = N9_CLOSED |
| **E. Authoritative N9 adjudication** | this document | **N9_CLOSED** (section 4), reached independently of layer D's token by checking every frozen condition (section 3) |

## 3. The fourteen questions

1. **Why N9 stayed OPEN after C11 and C11R.** C11: no valid comparison of the six cell-306 constants
   existed (EXECUTION_INVALID; single drift, wrong cell, one constant). C11R: four of the six were
   independently certified with EQUIVALENT/STRONGER statements and AGREES/STRONGER classes, but D1
   and D2 had no independent statement (NOT_IMPLEMENTED: they need drift-derivative kernels and a
   residual-to-error propagation theorem), so the gate's clause *"if D1 and D2 are not independently
   certified, N9 remains OPEN"* applied. **The single missing requirement after C11R was an
   independent, statement-equivalent certification of D1 and D2 for cell 306 on the frozen block,
   agreeing under the factor-2 rule.**
2. **C11RD addresses exactly that, without changing N9.** C11RD's target is cell 306, D1 and D2 only
   (`Q_target`, grant target, runs artifact); its statements are C11R's frozen original statements
   (freeze A/B records; validation V19 equality with C11R's schema; the comparator's statement check
   EQUIVALENT, domain EQUAL, premises SAME). The N9 wording, the six-constant count, the factor 2, the
   directions and the precedence are unchanged (statement table blob `58b4066f` unchanged; C11R gate
   and C2/C10 records unchanged since `7375b9cd`). C11RD is exactly the *"later prospective
   derivative-system extension"* C11R's gate names.
3. **C11R's four constants remain valid and in scope.** C11R's comparison artifact is the frozen blob
   `5269c2aa` (unchanged); its classes C_T AGREES, tau AGREES, Abar STRONGER, D_lo AGREES with
   statements EQUIVALENT, EQUIVALENT, EQUIVALENT, STRONGER and no independence violation; its
   comparison review is `VERDICT: COMPARISON_ACCEPTED`; its execution review `VERDICT:
   EXECUTION_ACCEPTED`. C11R's own adjudication records these four as achieved and names only D1/D2
   as missing. Nothing later touched them: the C11R and C11 namespaces have zero changed files since
   `7375b9cd`, and the C11RD freeze forbids *"recomputing or replacing C_T, tau, Abar or D_lo"* — the
   comparator read the classes blob-bound, it did not recompute them.
4. **D1/D2 statements before numbers.** The frozen `compare_statement` (C11R's semantics, V19/V20)
   returns EQUIVALENT (domain EQUAL, premises SAME) for both, and the comparison review reproduced it
   with its own implementation; the numbers were compared only after (comparator U4 before U5).
5. **Factor-2 rule.** Both are UPPER_BOUND with independent ≤ original and not equal: STRONGER, the
   ratios as in layer D; the comparison review recomputed the exact rational ratios and their floats
   bit for bit. For same-direction bounds no DISAGREES class is reachable; a markedly stronger
   independent upper bound implies the original's statement rather than contradicting it.
6. **All six satisfy the N9 criterion.** C_T AGREES, tau AGREES, Abar STRONGER, D_lo AGREES (C11R,
   accepted), D1 STRONGER, D2 STRONGER (C11RD, accepted): all six AGREES or STRONGER, each with an
   EQUIVALENT or STRONGER statement — exactly the gate's `N9_closure_requires`.
7. **Independence.** C11R: the original's load-bearing graph is absent (its adjudication and review).
   C11RD: the runner's transitive import graph is `c11rd_runs, c11rd_certify, c11rd_float,
   c11rd_kernel, c11rd_model, c11rd_tm` plus C7's `c7_gaussian` and the standard library — no module
   of the original chain, no numpy/flint (V16, re-checked by an import scan in this audit; C11's
   `c11_certifier` appears only in the validation module, V03). D1/D2 are propagated from **C11R's
   independently certified** C_T = tau (F_H, `C_T_independent`, `tau_independent`), never from the
   original's C_T or tau — the ordering the `DEPENDENCY_FINDING` requires. The comparator's
   independence predicate recorded no violation. **Disclosure:** the two original D1/D2 values were
   known to the C11RD author before the freeze (disclosed in C11R Phase 15 and in the C11RD
   instruction; recorded in `docs/C11RD_INDEPENDENCE_AUDIT.md`). They appear in no pre-comparison
   file (V18; U7 0 hits), no design parameter was chosen with reference to them (non-target
   calibration only), and a certified bound's validity does not depend on its author's knowledge — so
   the disclosure does not compromise independence of implementation or the certificates.
8. **Exactly once.** Execution: one consumed ref (`refs/c11rd/r1-execution-consumed` → G), one lock,
   one runner start and exit (exit 0), one seal on attempt 1; the runs artifact first appears in the
   seal commit. Comparison: one invocation (exit 0), one artifact (exclusive create), present in
   exactly one commit in all history; the frozen U0 now refuses.
9. **Reviews accepted.** C11RD: READY_TO_QUALIFY (`3c1eff11`), QUALIFICATION_ACCEPTED (`e27c2ffd`),
   AUTHORIZATION_ACCEPTED (`e320d8f5`), EXECUTION_ACCEPTED (`db1c6118`), COMPARISON_ACCEPTED
   (`90265349`), each a single verdict line, each preserved verbatim in its own commit. C11R:
   EXECUTION_ACCEPTED and COMPARISON_ACCEPTED.
10. **No invalidating violation.** Temporal: the whole C11RD lineage is strictly ordered (each commit
    an ancestor of the next), the freeze declares `FROZEN_BEFORE_ANY_TARGET_MAGNITUDE`, the runs
    artifact first appears in the seal, the originals were loaded only at U5 from the quarantine blob
    `219e0122` (unchanged since C11R). Provenance and freeze: code, protocol and theory unchanged since
    `ce5b8595`; every bound input blob equal to the freeze. Authorization: the A → R → G chain and HEAD
    == G at launch (execution review). Sealing: exactly the four runs files on top of G. Leakage: V18
    before the run, U7 at the freeze commit, the post-write scans, all clean. Scope: nothing outside
    the C11RD namespace changed since `7375b9cd`. The only historical defects in the chain — the
    rejected qualification (B-1) — were repaired prospectively before any execution and are recorded.
11. **Cells 307–309.** Never executed by this campaign: grant, lock and runs artifact name cell 306
    only; no file of theirs changed; the freeze forbids them.
12. **No adoption, no r6.** r5 (`K5_COVERAGE_MAP_R5.json`, blob `f978eeb6`) unchanged; no r6 file; no
    adoption record.
13. **Historical verdicts immutable.** C11 remains `EXECUTION_INVALID`; C11R's comparison remains
    `AGREEMENT_INSUFFICIENT` and its adjudication `N9_REMAINS_OPEN`, both true statements about the
    evidence each campaign had. Their files are byte-identical since `7375b9cd`; this document edits
    none of them.
14. **No retroactive change.** N9 closes by the LATER successor evidence (C11RD's D1/D2, combined with
    C11R's accepted four as C11RD's freeze prescribed before any target magnitude). C11 and C11R are
    not re-labelled: neither campaign's own evidence closed N9, and nothing here says otherwise.

## 4. Authoritative verdict

**N9_CLOSED.**

Every frozen condition holds: six constants for cell 306; each with an EQUIVALENT or STRONGER
statement on the frozen block; each AGREES or STRONGER under the factor-2 rule frozen before any
result; independently written relative to the original certifier (with C11RD depending only on C11R's
independent C_T and tau); no violation that the precedence ranks above N9_CLOSED; every execution and
comparison exactly once and accepted. This verdict is reached from those conditions, not copied from
the comparator's `N9_VERDICT` field, which it agrees with.

**What closed the previously missing requirement:** C11RD's sealed, accepted execution
(`4547bcd4`/`db1c6118`) and its single accepted comparison (`8e2defab`/`90265349`): independent,
statement-EQUIVALENT D1 and D2 for cell 306, both STRONGER than the originals. **Preserved:** C11
`EXECUTION_INVALID`; C11R `AGREEMENT_INSUFFICIENT` and `N9_REMAINS_OPEN` (historical, true of their
own evidence).

## 5. Consequences — and what this adjudication does not decide

* **K5 remains PARTIAL.** N9 is a trust condition on the constants, not a closure criterion for any
  cell; N9_CLOSED does not close K5, adopt cell 306 or change coverage.
* **r5 remains authoritative; no r6; no adoption; cells 306–309 remain open in r5.**
* **The C2 adoption floor.** By C2's own frozen wording, limb F1 is *"available for as long as N9 …
  remains open, and lapses when N9 is closed"*, and C2 and C10 name the route that N9 closure unlocks:
  a successor freezes, prospectively and before any recomputation, a **replacement floor requiring
  agreement between two independent certifier implementations** (C2 verdict Condition 1; C10). This
  adjudication neither applies F1's lapse to any cell nor freezes, replaces or applies any floor; that
  is the separate, prospective adoption/governance step, to be instructed separately.
* **No further science is implied.** Cells 307–309 have no independent certification of their own;
  N9 as worded concerns cell 306 only.
