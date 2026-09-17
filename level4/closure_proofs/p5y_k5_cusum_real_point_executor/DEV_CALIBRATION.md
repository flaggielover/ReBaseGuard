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

# r2 DEV calibration (after the r1 static review FAIL)

**Host and data.** Same discipline: rebaseguard-vultr-02, an untracked clone, manufactured systems, synthetic
candidates and operator certificates only. REAL_INPUT_ARITHMETIC_GUARD was DENY and EXECUTION_AUTHORIZED false
throughout; no real K1 cell was executed and no real R''', R⁽⁵⁾, L1 or U1 was formed.

## Defects found and fixed before the r2 freeze

1. **Q07 evaluated the frozen transport rule at a fixture's x1.** `probe_rules.transport` refuses an x1 other than the
   preregistered one, so every manufactured fixture failed Q07. The gate now applies the frozen rule at the
   preregistered x1 and the same exact formula at a fixture's x1, and a real record must carry the preregistered x1.
2. **ScipyGuard and the order-2 certifier were imported without the Aux5 ancestry** (ModuleNotFoundError). Both now go
   through `backends.scipy_guard_module()`, the 84aaa6a5 point_eval pattern.
3. **The Aux5 producer identity was read from the wrong key** of the preregistration (`producer_identity.aux5_producer_identity`).
4. **The hull-base check compared a binary ball to an exact rational.** x1 = 5083/10⁷ is not a dyadic, so the shared
   check now requires the ball to contain x1 with a radius below x1·2⁻²⁰⁰. P02 is still detected.
5. **The order-2 comparator mutant was not load bearing.** The published RUNG_256 enclosures are wide enough that
   relabelling m still intersects; the mutant now flips the sign of R', which is refused.
6. **Q06 replay was not byte-identical (the CRAMER compatibility contract).** The frozen `ra_certifier` builds
   `CRAMER = arb(1086) / arb(1000)` at IMPORT time, so its ball, and every Taylor remainder, allowance and certificate
   endpoint downstream, depends on the precision at which the module is first imported. The C_o0 / C_e0 artifacts and
   the K1 records were generated with it first imported at python-flint's default 53-bit context; the executor imported
   it lazily inside the 256-bit certifying context, which gave a tighter ball and endpoints that still certify but are
   not byte-identical.

   A zero-change diagnostic in two fresh processes established this before any repair: with the stack first imported at
   53 bits both certificates replay identically, and with it first imported at 256 bits the C_o0 margin differs by
   +9.85e-26, the C_e0 margin by +3.06e-24 and the C_e0 allowance export by −6.62e-24, while C_upper_bound and w_min are
   unchanged and both remain certified. The repair states that 53-bit construction as an inherited compatibility
   contract (`backends.CRAMER_CONTRACT`, sha256 b472beac1e241ef27cecf8b1536fa19618b49d1f47223d4538fac49ac6b49831),
   initialises the certificate stack under an explicit 53-bit context, and refuses any other construction in both
   `certificate_replay` (Q06) and `production_gate` (Q04), so no sealable result can be produced under a violated
   contract. Mutation C01 (first import at 256 bits) must be detected, and the qualification requires byte-identical
   replay from a default-precision caller AND from a 256-bit caller in fresh processes.
7. **Harness only:** the qualification child environments did not set `NUMEXPR_NUM_THREADS`, which the Aux5 runtime
   contract requires, so the production gate reported a thread-environment mismatch in a standalone run. The production
   supervisor always set all four variables.

## Known non-functional wording (NOT a qualification defect)

A comment above `CRAMER_CONTRACT` in `code/backends.py` reads `require/check_cramer_contract`, but only
`check_cramer_contract()` exists. It is a comment typo with no effect on execution, certification or the actual
`check_cramer_contract()` calls in `certificate_replay` and `production_gate`, both exercised by the qualification. The
file is pinned and its bytes are the DEV-qualified bytes, so it is recorded here rather than edited.

**Final r2 DEV state** (clean run, 0 runner failures): 17/17 gates PASS,
REAL_POINT_EXECUTOR = QUALIFIED_AWAITING_EXTERNAL_AUTHORIZATION; mutations E 16/16, P 4/4, A 3/3, V 1/1, C 1/1;
replay payload cb28b972… twice with 0 scientific leaf differences; smoke formed no enclosure (2433.0 CPU-s real Arb
stages, 221.2 CPU-s certificate replay); order-2 replay identical to RUNG_256; projected 6413.9 CPU-s per attempt and
19241.7 for the campaign, within the frozen 9000 / 32400 ceilings.

