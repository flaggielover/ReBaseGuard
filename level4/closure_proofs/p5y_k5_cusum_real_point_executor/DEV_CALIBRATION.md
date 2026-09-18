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

**Note on the DEV cost numbers above** (review r2, D12): 6413.9 / 19241.7 / 2433.0 / 221.2 are from the r2 DEV run.
The committed r2 frozen evidence reports 6403.2 / 19209.5 / 2424.8 / 222.3. They are two different runs.

# r3 DEV calibration (after the r2 static review FAIL, D1–D4)

**Host and data.** Same discipline: rebaseguard-vultr-02, an untracked DEV clone, manufactured fixtures and
qualification backends (burn, disk-full) only, and synthetic verifier reports and countersignatures in the pure
layers. The real frozen verifier was called only on this host, where no `AUTHORIZATION_ACTIVE.json` exists.
REAL_INPUT_ARITHMETIC_GUARD was DENY and EXECUTION_AUTHORIZED false throughout.

## Findings while building r3

1. **The r2 authorization model was parallel to the frozen one.** The protocol's authority is
   `protocol/AUTHORIZATION_ACTIVE.json` (r4 template, no extra keys), identified by its file bytes and bound to the
   executor through `EXECUTION_BINDING_AMENDMENT.json`. r2's own countersigned object could never pass the frozen
   verifier's P02, which is the root of D1. r3 uses the frozen objects and keeps the countersignature only as a second
   requirement naming the same file bytes.
2. **The frozen verifier raises, rather than returning REFUSED, when `AUTHORIZATION_ACTIVE.json` is absent.** It cannot
   read the file. The executor treats any raise as a refusal. The suite also feeds a *genuine* frozen-verifier REFUSED
   object (the verifier run read-only on the committed r4 template) to the decision, which refuses it.
3. **r2 sealed VOID on any post-arithmetic exception, including disk-full.** `void_after_arithmetic` limits VOID to
   INTEGRITY_REFUSAL, CPU_RLIMIT and WALL_TIMEOUT, and a transient kill leaves no sealed record. r3 follows it: a
   disk-full error seals nothing and is classified DISK_FULL_BEFORE_SEAL.
4. **The watchdog signal was indistinguishable from an external SIGTERM.** r3's watchdog sends SIGUSR1 (WALL_TIMEOUT,
   VOID); SIGTERM keeps its external-kill meaning.
5. **Supervisor diagnostics must stay outside the namespace root,** because P11 admits only `slot-N` directories. They
   now go to a private temporary directory.
6. **RUN_STATE argv must be the kernel's exact cmdline** (interpreter included) so that the waiter's `/proc` equality
   holds.

## Harness defects fixed during r3 DEV (qualification code only; no executor change)

- A copied-verifier fixture lacked enough parent directories for the verifier's own `REPO` computation.
- The mutant loader did not register the module in `sys.modules`, so the dataclass in a mutated `executor_core`
  crashed. Crashes count as NOT detected, so L02 and L03 first showed as undetected.
- The "admits its own RUN_STATE" test wrote the test's pid, where the rule requires the parent's.
- A sentinel bug made the "malformed None" case reuse the valid report.
- One live row expected REFUSED only; see item 2.

- **First full r3 DEV run: 20/21 gates.** EG11 failed because the inherited no-monkeypatch fence flagged the mutant loader's explicit `sys.modules[...]` assignment. The fence is right and load-bearing. Mutants are now imported normally from a private temporary directory with `importlib.import_module`, with path constants pinned, as in the r2 mutant-dir harness. The complete DEV run was repeated from a clean output directory.

**Mutation group L is L01–L04** (the spec named L01–L03). L04, ledger disagreement ignored, was added and is required.

**Final r3 DEV state** (clean run, 0 runner failures): 21/21 gates PASS,
REAL_POINT_EXECUTOR = QUALIFIED_AWAITING_EXTERNAL_AUTHORIZATION.
- **Mutations:** E 16/16, P 4/4, D01–D04 + A01–A03 7/7, L01–L04 + V01 5/5, R01–R02 2/2, C01 1/1.
- **Suites:** D1 50/50, D2 35/35, D3 33/33 rows.
- **Replay:** payload cb28b972… twice with 0 scientific leaf differences. This is byte-identical to the r2 payload, so
  r3 changed no scientific leaf.
- **Order-2 replay:** identical to RUNG_256.
- **Cost:** 6418.4 CPU-s per attempt and 19255.3 for the campaign, within the frozen 9000 / 32400 ceilings.
- These are DEV numbers; the frozen evidence is a separate run.

