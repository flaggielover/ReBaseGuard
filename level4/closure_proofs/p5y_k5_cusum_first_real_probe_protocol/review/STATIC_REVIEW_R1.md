# Independent static review of the r1 packet (freeze dbbd405a): FAIL

**Reviewer.** A separate read-only agent session. It modified no repository file and ran no real computation.

**What it checked.**
- Unit tests: 11/11 pass.
- Local prelaunch run: REFUSED, primary reason P01.
- `git log --all`: no sealed record or probe result anywhere in history.

## Findings

| # | finding | summary |
|---|---|---|
| R1 temporal integrity | PASS | Freeze commit adds only the packet; no real signed R'''/R⁽⁵⁾ exists |
| R2 cell selection | PASS_WITH_NOTES | Cell 0 is forced (only `L₁ > 0` passes C₁). Bridge citation lines were wrong. A POSITIVE unlocks only C₁ (cell 2 still fails with `L = −∞`), and this was undisclosed |
| R3 result-driven gates | PASS | Strict 0 comparisons, single rung |
| R4 qualification/science separation | PASS_WITH_NOTES | Sign-independent. Q02–Q13 self-attested by an executor that does not exist; the Q16 authorization commit is unverified |
| R5 object / transport | PASS_WITH_NOTES | Maths correct; C⁵ covered by L5; M5 semantics valid on the hull. `transport` did not pin x1 |
| R6 verdict / POINT_NEGATIVE | PASS_WITH_NOTES | Correctly sourced. The oracle's independent-adjudication rule was dropped; the SEEK_ALTERNATE label hides that the target is refuted |
| R7 precision / retry | PASS_WITH_NOTES | Single rung justified. The transient "refusal before arithmetic" class overlapped the integrity-VOID rule; SIGXCPU was unspecified |
| R8 K5-B consumption | **FAIL** | Consumption keyed on the verdict alone: INCONCLUSIVE + POINT_NEGATIVE gave `h3a_viable: yes`. The records → `k5b_literal` adapter was unpinned |
| R9 negative results | PASS_WITH_NOTES | Handling of numbers from an attempt voided after arithmetic was undefined |
| R10 address uniqueness | **FAIL** | `attempt_id` inside the hashed address; uniqueness was only a filename search over an unchecked namespace |
| R11 authorization fail-closed | **FAIL** | Forgeable (truthy fields, uncommitted path, epoch UTC); P10 empty namespace vs retries; code pinned only by a mutable manifest; P05 trusted a self-declared status |
| R12 executor scope limitation | PASS_WITH_NOTES | Correct. The executor bypasses the real-entry registries, and executor parameters are hard-coded in the science file |
| R13 cost / host | PASS_WITH_NOTES | Estimate composed from unrelated runs; the flint `.so` hash had no committed evidence |
| R14 other | NOTES | A refutation would rest on the first run of an unreviewed executor; tests never exercised a complete forged authorization |

## Required repairs

1. Hash-bind the rule and verifier code to the freeze.
2. Verifiable committed authorization at a fixed path, with pinned namespace.
3. Address without attempt id, plus per-attempt directories.
4. Consumption keyed on the H3a consequence.
5. Pinned K1-record adapter.
6. VOID-after-arithmetic rule, and resolve the retry overlap.
7. Strict amendment requirements.
8. Independent adjudication before adoption, and disclose the oracle divergence.

**Disposition.** Addressed by the r2 re-freeze: `protocol/SCIENCE_PREREGISTRATION_R2.json`, `code/*` r2 and
`protocol/R1_SUPERSEDED.json`. r1 was never authorized or executed.
