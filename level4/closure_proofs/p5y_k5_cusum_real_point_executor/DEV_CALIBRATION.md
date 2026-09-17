# DEV calibration before the executor freeze (manufactured and synthetic only)

**Host and data.** Every DEV run executed on rebaseguard-vultr-02 in an untracked clone, using manufactured
σ-systems, synthetic candidates and operator certificates only. REAL_INPUT_ARITHMETIC_GUARD was DENY throughout, and no
real K1 cell was executed.

## Fixture selection (exact truth known; fixtures were selected by truth class, which is legitimate for manufactured systems)

- **Scan 1** (60 systems) and **scan 2** (23 systems):
  - qualification PASS in every case;
  - 0 truth-containment violations;
  - about 1 s per execution.
- **Selected fixtures:** XF01–XF09, with the per-m expected verdicts recorded in the protocol.
- **M5-ratio limits** (`config/FIXTURE_LIMITS.json`):
  - tight fixture ≤ 15× truth for every m (observed ≤ 12.65);
  - loose fixture m = 1 ≥ 1000× (observed 1669).

## Defects found and fixed before the freeze

1. **Refusal harness parents.** The refusal tests shared one parent directory, so the executor's own
   FINALIZED_ADDRESS_EXISTS refusal fired on a later legitimate test and crashed the part. Each test now has its own
   parent. The executor was unchanged.
2. **Crashes counted as detections.** A mutant check that crashed was counted as detected. Now an unmutated control
   must pass first, and a crash counts as NOT detected. With that fix, the first honest count was 14/16.
3. **E04 not load-bearing.** The wrong-K1-identity fixture also mismatched the manifest and cells hashes, so the
   record-hash check did not decide the refusal. The fixture now differs only in the record hash, and E04 is
   detected.
4. **E06 undetected.** Two causes:
   - the truth gate checked only the final objects, so tower-node truth checks were added (every tower and anchor
     component against the exact graded suprema on the 17-point grid);
   - on these systems (source degree 2, so S₀⁽ⁿ⁾ = 0 for n ≥ 3), zeroing orders n ≥ 4 was an equivalent mutation.

   E06 now omits S₀′, which is nonzero there, keeping the same intent, and it is detected.

**Final DEV state.**
- Fixtures 9/9; refusals all pass; mutations 16/16 with a clean control.
- Smoke PASS (no enclosure, 0 float violations, 2474.6 CPU-s real Arb stages).
- Inherited R4 gates, separation, cross-check, runtime identity, fences and replay all PASS.
