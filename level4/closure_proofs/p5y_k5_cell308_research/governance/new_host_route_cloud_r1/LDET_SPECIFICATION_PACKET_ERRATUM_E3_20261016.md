# Erratum E3 to the L-DET specification packet (Cell-308 Cloud route r1): a deterministic, exhaustive exactness-control selection

**Status: PROPOSED · NOT ACCEPTED · NOT IN FORCE · NOT EXECUTED.** This erratum corrects erratum E2
(`LDET_SPECIFICATION_PACKET_ERRATUM_E2_20261016.md`, `7ac19ade…171b`), erratum E1
(`LDET_SPECIFICATION_PACKET_ERRATUM_E1_20261016.md`, `36398544…969c`) and the packet (`f0f367a9…80e4`). All three are
preserved unchanged. Its source is external B1 finding X6 (`reviews/external/REVIEW_EXTERNAL_B1_CONFORMANCE.md`,
`cf1a4b18…8e41`, lines 196–206), on FR2 K14.

**Precedence.** E3 governs over E2, then E1, then the packet. **E2.2 is replaced in whole** by E3.1–E3.4. Nothing else
in E1 or E2 changes.

To write this erratum, no reference record was opened, parsed, listed by content or typed. The order below uses only
the record list and the view-function names already published in the reference addendum
(`PROPOSED_LDET_REFERENCE_ADDENDUM_R1_20261015.md`, `4efcd152…5277`, §1–§2). `new_target_evaluations = 0` ·
`cell309_activity = none`.

## E3.1 — The declared search order

The search walks one fixed sequence of leaves. It is fully determined before OD-3, and does not depend on any record's
content.

1. **Records (cases), in this order:** the order of the reference addendum §1 table.

   | ordinal | case | candidate key |
   |---|---|---|
   | 1 | QC02 (decoy 297) | `decoy297` |
   | 2 | QC03 (decoy 316, blocks 0–2) | `decoy316` |
   | 3 | QC04 serial block 0 of decoy 297 | `serial` |
   | 4 | QC04 ladder-determinism record A | `det_a` |
   | 5 | QC04 ladder-determinism record B | `det_b` |

2. **Views, within each record:** the view or views that the reviewed comparator applies to that record. They are
   built from the pinned view functions of the addendum §2 (bound by `source_sha256`), in the order the reviewed
   comparator declares them. That declaration is part of the reviewed successor build. It is fixed by the implementation
   review and named in the OD-3 record, before OD-3. It is a list of function names per record ordinal: value-free.
3. **Leaves, within each view:** depth-first pre-order. An object's members go in canonical key order (code-point order,
   the same order the (b) writer uses). An array's elements go in index order.

Records, then views, then leaves: this gives one total order over every compared leaf.

## E3.2 — Which leaf is eligible, and the two passes

The search reads the **successor side**: the parsed view of the successor's records, which the control mutates on a
copy. It never reads the reference side.

* **Eligible Decimal leaf.** A leaf of type `Decimal` that is finite and non-zero, and for which the mutation
  `d′ = d + sign(d) · 10^(adjusted(d) − 40)` gives `d′ ≠ d` exactly, while `float(d′) == float(d)`.
  * `adjusted(d)` is the exponent of the leading digit (`Decimal.adjusted()`).
  * The sum is computed **exactly**: with `Fraction` arithmetic, or in a `Decimal` context whose precision exceeds the
    leaf's digit count plus 41, so that no rounding occurs.
  * This makes E1 §2 exact: "a decimal digit appended beyond the precision a double can hold" now means one unit, 40
    places below the leading digit.
  * The mutated leaf is written by the (b) writer in exact plain decimal text with no exponent.
* **Eligible `fs` leaf.** A string leaf that matches the E1 §2 grammar `^-?(0|[1-9][0-9]*)/[1-9][0-9]*$` with gcd = 1,
  whose numerator is non-zero, and for which the E2.2 mutation `(n · 10^40 + 1) / (d · 10^40)`, re-normalised to
  gcd = 1, satisfies `float(mutated) == float(original)`.
* **The float test is part of eligibility, never an exception.** For both kinds, `float()` of the original and of the
  mutated value must each be finite and non-zero. If either is infinite or zero, or if `float()` raises (for example,
  `OverflowError` on a very large `Fraction`), the leaf is **ineligible** and the walk moves on. Such a leaf never makes
  the attempt INCOMPLETE.
* **Pass 1.** Walk the whole order of E3.1, over **every** record and view. Select the first eligible Decimal leaf.
* **Pass 2**, only if pass 1 found no eligible Decimal leaf **anywhere**. Walk the same whole order and select the first
  eligible `fs` leaf.
* **No eligible leaf in either pass.** The exactness control is recorded as **NOT_APPLICABLE**. This outcome is fixed
  now, in advance. The other rules are unchanged:
  * the planted control (E1 §2 control 1) is still required;
  * (a) ∧ (b) equality and the structural non-vacuity floor still decide MATCH.

  NOT_APPLICABLE is never turned into INCOMPLETE, and INCOMPLETE is never turned into NOT_APPLICABLE.
* **The mixed case.** Suppose record 1 has no eligible Decimal leaf but record 3 has one. Pass 1 continues past record 1
  and selects record 3's first eligible Decimal leaf. An `fs` leaf in record 1 is **not** selected, because pass 2 runs
  only when pass 1 finds nothing anywhere.
* **Detection.** On the mutated successor copy, (a) **and** (b) must both report a difference, exactly as in E1 §2. If
  either does not, the attempt is INCOMPLETE.

## E3.3 — Authority, timing, bounded output, and no extra trial

* **Authority.** The rule is part of the L-DET comparison rule. It comes into force only with the owner's adoption of
  the L-DET packet with errata E1–E3 (statement 2). It is bound into the OD-3 record by this file's sha256. It runs
  only inside the **one L-DET attempt that OD-3 authorizes**. No other authority to read, parse or type any record is
  given or needed.
* **Timing.** The search runs inside that attempt, once, after both sides are parsed and viewed, and before the
  comparison outcome is written.
* **No reading of the reference side before OD-3.** E2.2's "fixed before OD-3 and decided on the reference side by type
  only" is **withdrawn**. No person, agent or process parses a reference record, or determines the type of any leaf in
  one, before OD-3. The type is determined during the attempt, on the successor side, by the rule above (B1 X6 asked
  for this option).
* **Bounded output.** The attempt record holds only:
  * `exactness_control_kind`: one of `DECIMAL`, `FS`, `NOT_APPLICABLE`;
  * the record ordinal (1–5), the view ordinal and the leaf ordinal in E3.1's order (null for `NOT_APPLICABLE`);
  * two booleans: (a) detected and (b) detected.

  No leaf value, number token, key name or path string is written. These ordinals and booleans are E8-neutral: they sit
  next to no cell-308 quantity.
* **No extra trial or retry.** The search is deterministic and runs once. Its result cannot be re-run to choose
  another leaf, and no other rule may be substituted after the attempt starts. An exception inside the search is
  INCOMPLETE, fail closed. Under D-LDET-REPEAT ("no repeat") that consumes the one attempt: it never creates a second
  attempt.

## E3.4 — Implementation and provenance

* **Implementation item** for the reviewed successor comparator: E3.1–E3.3, with tests on **synthetic** fixtures only.
  The fixtures cover:
  * a Decimal leaf in record 1;
  * a Decimal leaf only in a later record (the mixed case);
  * `fs` leaves only;
  * no eligible leaf;
  * a zero leaf, and a leaf whose float changes under the mutation (both ineligible).

  No test reads a reference record.
* **Provenance (B3).** This erratum introduces two rules: the declared order, and the offset of 40 decimal places
  (`10^(adjusted − 40)`, mirroring the 10^40 of E2.2). Both are on the allowlist of the B3 provenance brief r2
  (`ledger/briefs/B3_EXTERNAL_PROVENANCE_CHECK_CLOUD_R1_R2.txt`) as rules this route introduces.
  * The order is copied from the addendum's published list.
  * The offset 40 is a free choice: any offset large enough to keep `float()` unchanged for normal doubles (more than
    17 significant digits) would do. 40 matches E2.2's existing choice. It is stated here for the provenance check.
