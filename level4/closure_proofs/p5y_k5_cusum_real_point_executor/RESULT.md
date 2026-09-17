# Real point executor r2: result

**Status: `REAL_POINT_EXECUTOR = PARTIALLY_QUALIFIED`.** The frozen qualification is green (17/17 gates), and the
independent static review returned **FAIL** on one load-bearing fidelity defect plus two governance defects. No
external authorization may be sought until they are repaired.

`EXECUTION_AUTHORIZED = false` · `REAL_INPUT_ARITHMETIC_GUARD = DENY` · `REAL_CELL_EXECUTED = NO` ·
`SCIENTIFIC_K5_PROBE_RUN = NO`

## Commits and hashes

| item | value |
|---|---|
| executor freeze commit | `52769488` |
| qualification evidence commit | `57b51a6f` |
| executor identity sha256 | `2bd98fde6bba1e2252b31c28a108c76b112f9924bd1b94a6f8fd237cc53a50f3` |
| qualification protocol sha256 | `f82ae62b2afe4dfadcc73e92d463e33502b719e0077eedfebc6d4eb97c005e17` |
| qualification result sha256 | `884bebe0b6836105df25d64ce1e7d5f9ce12a94fdcb42e801ff3805c9767ab2b` |
| CRAMER compatibility contract sha256 | `b472beac1e241ef27cecf8b1536fa19618b49d1f47223d4538fac49ac6b49831` |
| science preregistration sha256 | `9ace6896d70b7a17225c03cd6d8092e3d33089d001dd3e2736894dd866f3780a` (unchanged) |
| predecessors preserved | r1 freeze `8ffcfaff`, r1 evidence `80a3ab2b`, r1 review + r2 spec `6a1adbfe` |

## Frozen qualification (clean detached checkout of `52769488` on rebaseguard-vultr-02)

All 17 gates PASS → the runner's own verdict was `QUALIFIED_AWAITING_EXTERNAL_AUTHORIZATION`, with 0 runner failures;
the read-only `check` replay reported 0 problems.

- **Mutations:** executor E01–E16 **16/16**, production stack P01–P04 **4/4**, authorization validator A01–A03
  **3/3**, VOID sealing V01 **1/1**, CRAMER import precision C01 **1/1**. Unmutated control first; a crash counts as
  **not** detected.
- **Determinism:** replay payload `cb28b972…` twice, **0** scientific leaf differences.
- **Fixtures:** 9/9 with exact manufactured truth, 0 containment violations, expected three-way verdicts and point
  signs, M5/truth ratios inside the DEV-calibrated limits.
- **Real-stage smoke:** formed no enclosure (2424.8 CPU-s Arb stages), 0 float-containment violations, Q04 both gate
  stages with the SciPy guard, Q06 certificate replay (222.3 CPU-s), Q08 origin-free graded/scalar consistency.
- **Order-2 cross replay:** reproduced the committed GammaTilde `RUNG_256` enclosures **identically**, and refused a
  sign-flipped comparator.
- **Supervision:** CPU-limit and wall-watchdog VOID seals, external kill classified, real mode refused before
  arithmetic, VOID address refused — all through the frozen `probe_rules.failure_class`.
- **Cost:** 6403.2 CPU-s projected per attempt, 19209.5 for the campaign, inside the frozen 9000 / 32400 ceilings.
- **Runtime identity:** rebaseguard-vultr-02, AMD EPYC-Milan, python 3.12.3, python-flint 0.9.0, FLINT 3.6.0, glibc
  2.41-12+deb13u4, libc `9792e3cb…`; no drift from the frozen host contract.

Nothing real was computed: no real K1 cell was executed and no real R‴, R⁽⁵⁾, L1 or U1 was formed. The one real-input
arithmetic anywhere in the qualification is the order-2 reference replay of R(0) and R′(0), quantities already
published by the `84aaa6a5` point certificate, which it reproduced byte for byte.

## Independent static review: FAIL

`review/EXECUTOR_STATIC_REVIEW_R2.md`. Passed: the R2/R3/R4 mathematics, certification, preregistration preservation
and qualification/science separation, the guard, the Q-gate implementation (bar Q01), serialization and determinism,
cost credibility and the CRAMER contract, and the trust model. The reviewer independently recomputed all 276 pins, the
executor identity, the science hash and the result hash.

Blocking and load-bearing:

- **D1 — the in-process prelaunch obligation is not implemented.** The preregistration requires the executor to call
  `prelaunch_verify.verify` with its defaults and refuse in-process unless the result is LAUNCH_PERMITTED for the same
  HEAD and authorization. The r2 executor imports that module only for `live_host_facts()`, and real-mode Q01 instead
  trusts an operator-supplied report dict, checking three fields. Worse, the hash Q01 demands cannot be produced by
  the frozen verifier: the executor compares a canonical hash of its own countersigned object, while a genuine
  `prelaunch-report.v4` carries the file-bytes hash of the *protocol's* authorization, and the verifier's P02 cannot
  accept the executor's object. This is a fidelity defect against frozen text that may not be amended away.
- **D2 — the `completion_semantics` marker-file contract is not met.** `RUN_STATE.json` lacks `argv` and the
  authorization sha256; `RUN_COMPLETE.json` lacks the pid, the sealed-record sha256 (which prelaunch P09 and the
  ledger OUTCOME need) and the gates; `RUN_FAILED.json` lacks the pid and traceback.
- **D3 — no supervisor reboot-recovery mode.** `HOST_REBOOT_OR_BOOT_ID_CHANGE` is a transient class on which a retry
  depends, yet a reboot leaves no marker for the interrupted slot.
- **D4 (medium) — `evidence/qualification_r2/` has no `RUN_PROVENANCE.json`,** so the run's commit and worktree
  cleanliness are not recorded in the evidence a countersigner reads. Partly compensated: `part_fence` re-verified all
  276 pins and the 19 qualification sources at run time.

Lower, not load-bearing: a `README.md` reference to this file before it existed (now resolved), the near-tautological
Q11 implementation, Q10's intersection-only rule, gate *evidence* living outside the scientific hash, directory-level
fsync, refusal strings not mechanically guaranteed number-free, and three informational notes (the `certify_graded`
default precision, the "science unchanged since `dbbd405a`" wording, and DEV-versus-evidence cost numbers).

Accepted scope limitations, per the review: the local host is **not** an independent trust root and no further on-host
anti-tamper machinery is requested; the real-mode Q01/Q14/Q16 assembly cannot be executed end to end under a DENY
guard and is reviewed statically with its components exercised on the real stack; reviews are not proofs; Arb
correctness and the inherited 53-bit CRAMER construction are stated assumptions; and the order-2 reference replay
touches real inputs outside the guard for two already-published quantities.

## Known non-functional wording

A comment in `code/backends.py` reads `require/check_cramer_contract`, but only `check_cramer_contract()` exists. It is
a comment typo with no effect on execution, certification or the calls in `certificate_replay` (Q06) and
`production_gate` (Q04), both exercised by the qualification. The file is pinned and its bytes are the DEV-qualified
bytes, so it is recorded rather than edited (`DEV_CALIBRATION.md`).

## Next step

`REPAIR_REAL_POINT_EXECUTOR` — an additive r3 addressing D1–D4, then a fresh freeze, frozen qualification and
independent review. **Do not seek or activate external authorization** while the review verdict is FAIL. The r1 and r2
freezes, evidence and reviews stay in history unchanged.
