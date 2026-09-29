# Cell-308 successor route audit: addendum A1 (coordinator; route review RC1 to RC6)

**Why.** The independent review `reviews/REVIEW_SUCCESSOR_ROUTE_308.md` (research `a1d1c7d4`, sha256
`47bbd9b7…8c230be`) returned ROUTE_ACCEPTED under RC1 to RC6.

**Status of the original.** The audit `registry/SUCCESSOR_ROUTE_AUDIT_308.md` (`bddd85f8`) stays byte-unchanged. A1
prevails where they differ.

**The selected route is unchanged: MB-S**, meaning MB308 r1's science byte-identical, with new infrastructure only.
New cell-308 target evaluations: 0.

## 1. Corrections (RC4)

* **P1** (existing consumer, atom constants only) is relabelled **PRUNED**: evidenced from committed facts, not
  certified. PRUNING_308 states that its A0 part is certified-undecided; only P0 is certified. P1 is the only family
  on C2's consumer path, which is floor r2's adoption path, so the distinction matters.
* **R2 (C1b) is an alarm only.** Under the frozen admission rule D5, C1b upper rungs with d > 6 are never admitted.
  In MB r1's ladder (d 8/10/12), C1b therefore supplies no upper bound. It serves as the cross-implementation alarm
  (L_C1b ≤ U_C2b). C2b (R3) supplies the admitted upper rungs, each independently verified.
* **"Strongest"** is scoped to *among components implemented, reviewed and qualified at this cell*. C11R-I2 or
  COR-T, if added, could only strengthen R-MB.
* **Determinism is conditional on RC2.** The value of MB-S equals the value the lost MB r1 run would have produced
  only **on the same platform**: interpreter, libpython, OS build and architecture. The A0 certifier review's N2 says
  the float proposals use libm. Off that platform the S4 "changed" branch applies.
* **The C11R-I2 / COR-T deferral** is a preference under S4 for the unchanged science, and it is the anti-chasing
  direction. "Not tonight" is withdrawn: it was a scheduling remark, not a reason.
  * **The foreclosure consequence.** Once MB-S has an observed outcome, adding either member would be a variant
    selected after a result, which the grant, U6, the brief's §26 and the floor r2 / cell-306 precedent forbid.
    Choosing MB-S therefore **forecloses** those members for cell 308 unless they are adopted **before** the MB-S
    freeze.
  * The user should see this trade before the S1 ruling (successor-governance addendum A1 §3).
* **The catch-all row** ("sharper sup / operator norms, other A1/A2 improvements") gets the status **DEFERRED (no
  instrument)**. No committed, reviewed instrument exists beyond R6 and C-RLR.

## 2. Completeness rows (RC5)

| id | route family | status | target-free reason |
|---|---|---|---|
| MB-VAR | R-MB parameter variants: partition (D1), RLR ladder (D3), pointwise ladder (D4), admission rule (D5), D14 slot rule, extra pointwise drifts | **NOT SELECTED** | Each is a change of science, so S4's changed branch would apply. None has a non-target motivation fixed before the MB r1 freeze. D1/D2 are fixed by rule from the committed cover geometry; D3/D4 were chosen on non-target findings and cost; D5 was fixed by the reviews. Any variant chosen now would be chosen after the MB r1 loss, without prospective provenance |
| HOST | moving the successor to another host | **EXCLUDED unless RC2 is discharged there** | the determinism argument binds the platform. A different host means the S4 changed branch, and its own exact reproduction of MB r1's r3 records would be required |

## 3. The science/infrastructure boundary (RC1) and platform pinning (RC2)

These are binding on the successor build (the builder was instructed on 2026-09-29 at about 20:40Z) and are checked at
the successor's qualification.

* **Unchanged science, listed by path, sha256 and git blob at `c46434a3`:**
  * THEOREM_MB r1;
  * `mb308_stage1`, `mb308_supply`, `mb308_consumer`, `mb308_a0core`, `mb308_pinned`;
  * the 25 `module_pins`, the 15 `consumer_and_input_pins`, and the F2, F3, `vd_pl` and `vd_verify` pins;
  * the rules D1–D10, D12–D14 and the §8 mapping.

  The successor protocol carries this list.
* **Driver science functions.** The science functions of `mb308_driver.py`, carried into `mbs308_driver.py`, are
  **text-identical**. A function-level AST source-equality test against the MB r1 driver at `c46434a3` runs in
  qualification. Any change is listed with an equivalence argument and falls under RC2.
* **The guard** differs from `mb308_guard.py` only in namespace, ref and marker constants. A test asserts that, and
  the diff is independently reviewed.
* **D11** (workers, caps) is infrastructure. It is re-derived only by the frozen §3.2 rule from decoy runtimes (S3,
  S13).
* **Platform pinning before the marker.** The successor refuses on any mismatch of: the interpreter path and
  sha256, the libpython sha256, `sys.version`, the OS build, the architecture. There is no OS or Python update
  between the successor's qualification and its execution.
* **The MBR1_REPRO qualification case.** It re-runs MB r1's committed non-target r3 cases through the successor's
  code: QC02 (decoy 297), QC03 (decoy 316, blocks 0–2), and the QC04 validation-drift ladder pair. It requires exact
  equality of every certified leaf, timing stripped, with MB r1's committed r3 records. Any mismatch means STOP and
  the S4 changed branch. Qualification review E8 applies: these records are never placed next to a cell-308
  quantity.

## 4. Governance dependency (RC3)

* **MB-S takes effect only with accepted governance.** The successor-governance determination was REJECTED as
  submitted (`e3c60491`, classification confirmed). Its addendum A1 is under delta review. Until it is accepted,
  MB-S is a candidate only.
* **Cited texts.** This audit cites incident-review C9 ("one sealed execution, with no retry and no post-result
  tuning") and qualification review E7 ("Never `execute` again; recovery goes through `seal-only` only … Lost result
  information is never recomputed without a new independent governance process").
* **MB-S is a second consumption of cell 308.** It is admissible only through S1 (a new user ruling, lifting
  mitigation 5) and S7. The successor's adjudication discloses it.

## 5. Risk register (RC6), carried into the successor charter and grant

1. The incident-01 liability (profile transport). The result-chasing risk is not lower than MEDIUM–HIGH and is
   re-rated by a fresh reviewer (S12).
2. The RLR block certificates have a single implementation.
3. The Q12 margins are thin on this host (about 6 % and 9 % in MB r1 r3). Q12 is **re-measured on decoys under the
   successor's own launcher**.
4. The long runtime (a Stage-1 projection of about 4.9 h from decoy runtimes) is a crash-exposure window.
5. **(a) Platform dependence** of the determinism argument (RC2).
6. **(b) A second consumption** of cell 308 (C9, E7). It is admissible only via S1.
7. **(c) Host reset or lid sleep mid-run.** **Decided in advance, target-free: sealed per-job checkpoints with frozen,
   mandatory resume semantics and a read-before-seal prohibition** (architecture §4), rather than accepting the
   residual reset window.
   * Why: MB r1 showed that a mid-run host failure otherwise wastes the evaluation.
   * Because of determinism, a resumed evaluation equals an uninterrupted one.
   * The mandatory-continuation rules remove any discretionary abandonment.
8. **(d) The new launcher may shift runtimes.** Q12 is re-measured under it (item 3).
9. **(e) The go / no-go decisions** (the S1 ruling, and the freeze decision under §14 / G2) are taken with the lost
   run's runtime-only observations in view. They are named in exposure addendum E1″. S13 excludes them from every
   successor design and caps decision.
