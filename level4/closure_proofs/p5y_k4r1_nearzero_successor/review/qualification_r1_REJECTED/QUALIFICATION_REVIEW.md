# P5Y-K4R1 pre-result qualification review

**Verdict: QUALIFICATION_REJECTED**

| Item | Value |
|---|---|
| Candidate | `81f5195a` on `p5y-k4r1-nearzero-successor` |
| Reviewer | Independent, adversarial, fresh context |
| Machine-readable review | `QUALIFICATION_REVIEW.json` |

## Summary

The science is sound and the provenance is complete. The residual universe is exact, and the implementation is correct on line-by-line inspection.

The qualification evidence does not cover the value-wiring path from the real sources into the certificate. Six unsound single-edit mutants survive the frozen suite, plus one weakening mutant of an assembly check that the universe check already enforces. The gate claims all 32 of its mutants are killed, but that set does not include these seven, so the gate's adequacy claim does not hold for this path.

## Checks

| # | Check | Result |
|---|---|---|
| 1 | No target result computed | PASS |
| 2 | Universe equals historical K4 residual (report 83cabce2) | PASS |
| 3 | Inheritance and assembly (handoff at a exact, no gap) | PASS, with a note |
| 4 | Mathematical soundness (oddness, G, T transport, Taylor, max(T,0), strictness, input semantics, same R, L5 qualitative) | PASS |
| 5 | Endpoint e = 0 semantics | PASS |
| 6 | No scope narrowing or tuning | PASS |
| 7 | Provenance (16/16 hashes; slot-1 and T-EXT ADOPTED; K1 cell-0 equals manifest entry) | PASS, with a note on T-EXT adoption scope |
| 8 | Implementation matches the specification | PASS, with a note on freeze-gate strength |
| 9 | Tests and mutation | **FAIL** |
| 10 | Leakage | PASS, with a note: not disqualifying, but "blinded" is overstated |

### Check 9 in detail

I reproduced both committed results:
- pytest: 36/36 pass.
- Mutation harness: 32/32 killed, and my report is byte-identical to the committed one.

I then ran 12 extra single-edit mutants; 7 survived:
- `D0_lo_instead_of_hi`
- `M5_from_order4`
- `L1_U0_swapped`
- `exec_g_uses_x1`
- `exec_t_args_swapped`
- `exec_science_or`
- `assembly_residual_how_unchecked`

## Blocking defect

**Q1.** The load-bearing value-wiring path is not covered by the tests:
- the field selection in `extract_inputs`;
- the composition in the `execute` branch.

**Repair:**
1. Add a test that asserts the exact values `extract_inputs` returns, using synthetic sources with a distinct value for every field.
2. Add an end-to-end synthetic `execute` test with its own repo, `FREEZE.json` and `FREEZE_HASH`, asserting the exact expected G, T and B.
3. Add the surviving mutants to the harness and re-run it.

## Non-blocking notes

- **N1.** `verify_freeze` should require a minimum set of bound files and check that HEAD is the clean freeze commit.
- **N2.** Exact-once is enforced per output path only; there is no ledger.
- **N3.** State the T-EXT adoption scope and its inherited premise P1b accurately.
- **N4.** Correct the blinding claim in FEASIBILITY.md.
- **N5.** Add structural checks on the per-m K1 entry metadata and on slot-1 L1 = L0 − (x1²/2)·M5.
- **N6.** `test_extract_refusals` should not accept `KeyError` as a refusal.

## Reviewer disclosures

- **No target value computed.** I computed no G, T or B.
- **Procedural breach.** I ran `execute` once to confirm the lock, against the instruction not to. It refused at `verify_freeze` before any source was read, and wrote no output.
- **Exposure to blinded values:**
  - The system-provided memory contained slot-1 L1 decimals.
  - A faulty redaction printed the exact slot-1 per_m L0, U0, M5, L1 and U1 from the slot-1 adjudication.
  - I never read the T-EXT hull M3 or M5 values for rows 1–2.
- **No repository changes.** No repository file was modified.
