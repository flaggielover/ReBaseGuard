# First governed real CUSUM signed-R''' probe: preregistered protocol (Option B), revision r4

**r4 supersedes r3 (`38234751`), r2 (`c4716a88`) and r1 (`dbbd405a`) before any authorization or execution.**
- **Authoritative files:**
  - `protocol/SCIENCE_PREREGISTRATION_R4.json`;
  - the r4 `code/probe_rules.py`, `code/prelaunch_verify.py` and `tests/test_probe_protocol.py` (hash-bound);
  - `protocol/AUTHORIZATION_TEMPLATE_R4.json` and `protocol/EXECUTION_BINDING_R4.json` (introduced by the freeze
    commit);
  - `protocol/FREEZE_RECORD_R4.json` (published after the freeze).
- **Science is unchanged since r1:** cell 0 = C₁, m ∈ {1, 2, 3, 5}, point enclosure plus (x₁²/2)·M5 transport, the
  three-way verdict with POINT_NEGATIVE, the K5-B consumption map keyed on the H3a consequence, a single 256-bit rung,
  and the cost basis.
- **Why each re-freeze.** Every re-freeze answers an independent static review that failed the governance machinery
  (`review/STATIC_REVIEW_R1.md`, `R2`, `R3`).

**r4 changes from r3.**
1. **Publication anchor.**
   - The ref `origin/p5y-postk1-frontier` is pinned, with no CLI override.
   - It must equal `git ls-remote` of an allow-listed origin (GitHub, or the host mirror `/root/work/postk1.git`).
   - The freeze commit's first parent is the literal `5da170db`.
2. **Freeze-time files.** The template and binding are introduced by the freeze commit and never change, so a
   drifted template is refused.
3. **No symlinks.** No governed path may be a symlink; git must store regular files.
4. **Review file.** It needs exactly one `REVIEW_VERDICT` line and exactly one `REVIEWED_AMENDMENT_SOURCES_SHA256` line.
5. **The committed ledger governs host files.**
   - OUTCOME entries carry `arithmetic_started`, `failure_class`, `run_failed_sha256` and `sealed_record_sha256`.
   - Host `RUN_FAILED.json` must match them.
   - A non-null `sealed_record_sha256` blocks further launches even if the host seal is deleted.
6. **Failure class.** A hard-limit kill is CPU_RLIMIT whenever child CPU time reaches the soft limit; wall time works
   the same way.
7. **Executor obligations.** The executor calls the verifier with its defaults only. The supervisor recovery mode
   writes RUN_FAILED after a reboot. No qualification fixture may use sealed-record names.
8. **Tests.** A git-repo harness covers F1 (the r2 forgery), F2 (a genuine activation, with P02/P03/P04/P06/P09/P11/P12
   passing) and the r3 bypasses V05, V12, V21, V22, V23, S1 and S2, all refused.

---

**Status: FROZEN PRE-RESULT. NOT AUTHORIZED. NOT EXECUTED.**
- **Route:** `SCIENTIFIC_PROBE_PLUS_REAL_QUALIFICATION`, i.e. one computation with two predeclared, logically
  separate roles:
  - real end-to-end qualification of the R4 producer;
  - a preregistered K5 scientific probe.
- **Machine-readable authority:** `protocol/SCIENCE_PREREGISTRATION.json` (sha256 `3d2eab4c…`), plus the frozen rule code
  `code/probe_rules.py` and the read-only `code/prelaunch_verify.py`.
- **Precedence:** where this text and the JSON differ, the JSON governs.

## 0. Temporal and identity audit (at preparation)

**Refs.**

| ref | commit |
|---|---|
| HEAD = origin/p5y-postk1-frontier | `dcca5c46` |
| origin/main (untouched, not an ancestor of the frontier) | `1cb45382` |

**Ancestry.** All of the following are ancestors of the frontier, and R1–R4 protected files are byte-identical to the
R4 protocol pins (checked by prelaunch check P04):
- R1 `e69a0224` / `4a1b20a8`
- R2 `a1dcf1e8` / `327e0e13`
- R3 `1089ea1e` / `57cbc249`
- R4 `0a7ce2fd` / `dcca5c46`

**Prior exposure.** No real signed `R'''` or `R⁽⁵⁾` value, interval or sign exists for any real CUSUM cell in the
lineage:
- K1 records carry only unsigned order-3 magnitudes.
- R2–R4 cell-0 numbers are radius forecasts (no centre, no sign).
- The GammaTilde point certificate (`84aaa6a5`) holds only `R` and `R'` at e = 0.

So there is no contamination and no retrospective construction.

## 1. Cell selection (pre-result evidence only): **K1 CUSUM cell 0 = theorem cell C₁ = [0, 5083/10⁷]**

**Why cell 0 is objectively the most informative, not merely the engineering target:**
1. **Bridge.** In the K5-B bridge (`K5_GLOBAL_BRIDGE.md` lines 30–33 and 56; countersignature README lines 69–70), `C₁` passes **only** through
   `L₁ > 0`. `Γ₁ < 0` is impossible because `Γ₁ ≥ g(0) = 0`, and no restart covers `C₁`. Every m requires it.
2. **Lemma K5-L.** `R'''(0) > 0` is the only generic way H3a holds at 0, and a certified `R'''(0) < 0` refutes H3a.
   Cell 0 is decisive in **both** directions; every other cell is at most conditionally informative.
3. **Other candidates** (details in the JSON `cell_selection.candidates`):
   - **Transition cells (132/144/145/148):** have value only after `C₁` passes. A restart from `H_k.lo ≈ −2.6e3`
     cannot give `U_k < 0`, and the following cells already close by `Γ_k < 0`.
   - **Tail 305–309 (m = 5):** could close by restart, but H3a for m = 5 still needs 0–148. There is no σ-symmetry at
     e ≈ 1.7 (Strategy B does not apply), and cell 309 contains e = 2.
4. **R4 fit.** R4's qualified method (σ-odd `C_o0`, point `R'''(0)`, local M5 on `[0, x₁]`) exists only for this cell.
   Its pre-result forecast is MARGINAL, and it is not a result.

## 2–3. Scientific object and hypothesis (per m)

**Objects.**
- `I₀ = [L0, U0] ∋ R'''_m(0)`: point run at e = 0 on the degenerate cell {0}.
- `M5_m ≥ sup_[0,x₁] |R_m⁽⁵⁾|`: R4 `local_r5`.
- `L1 = L0 − (x₁²/2)·M5_m` and `U1 = U0 + (x₁²/2)·M5_m`, with `x₁ = 5083/10⁷`.

**Relationship.** `R` is odd and C⁵ (L5, reviewed at `879792d0`), so `R'''` is even and `R''''(0) = 0`. Hence
`L1 ≤ inf_{C₁} R'''` and `sup_{C₁} R''' ≤ U1`.

**Rules.** No midpoint substitutes for an endpoint. **Primary question:** is `L1_m > 0`? The comparison is strict,
exact and rational.

## 4. Scientific verdict (per m, frozen code `probe_rules.scientific_verdict`)

| condition | verdict |
|---|---|
| `L1 > 0` | SUPPORTS_K5B_FIRST_CELL |
| `L1 ≤ 0 ≤ U1` (including touching 0) | INCONCLUSIVE |
| `U1 < 0` | CONTRADICTS_REQUIRED_POSITIVE_SIGN |
| any integrity gate in `science_requires` fails | VOID_PRODUCER_INTEGRITY_FAILURE |

**Secondary (frozen).**
- The point sign is `L0 > 0` POSITIVE, or `U0 < 0` NEGATIVE, or otherwise UNDETERMINED.
- POINT_NEGATIVE certifies `a3 < 0`, so H3a is false for that m, even when the transported verdict is INCONCLUSIVE.

**Never allowed:** converting INCONCLUSIVE with midpoints or estimates, reinterpreting a negative result, or dropping
an m.

## 5. Real producer qualification (sign-independent)

- **Gates.** Q01–Q16 (JSON): input binding, exact cell, runtime and Aux5 gates, source and manifest hashes, certificate
  replay, interval consistency, graded/scalar consistency, R⁽⁵⁾ certificate validity, order-2 cross-replay against
  `84aaa6a5`, deterministic serialization, address uniqueness, no mutation, fail-closed, cost ceiling, temporal
  integrity.
- **Outcome.** `REAL_PRODUCER_QUALIFICATION = PASS` iff all pass. It is computed without reading any sign, and it may
  PASS whether the science is positive, inconclusive or negative.
- **Science usability.** Science is usable only if the integrity subset (`science_requires`) passes; the cost gate is
  excluded.

## 6–7. Precision and retry

**Precision ladder: {256} only, no escalation.**
- The R1 real front-end refuses other precisions.
- R1 and R2 precision studies are STAGNATING (the width floors are mathematical).
- The R4 certificates are frozen at 256.
- So a 256-bit result is final whatever its verdict.

**Retry policy.**
- **When a retry is allowed:** at most 3 attempts, only for the enumerated transient classes (host reboot, external
  kill or OOM, disk full before the seal, a refusal before arithmetic), with identical inputs and code, and only while
  no sealed record exists.
- **Finality:** the sealed record (all m, written atomically) is final.
- **Not transient:** any integrity refusal (FAIL + VOID, successor required) and ceiling overrun.
- **No early output:** no endpoint, sign or majorant may be emitted before the seal.

## 8–9. Scientific address and m values

**Address.** One address per m, with sha256 of canonical JSON over:
- detector CUSUM, k 1/2, h 5, m;
- theorem cell C₁, K1 index 0, endpoints, point e = 0, object;
- K1 record sha256, producer identity sha256, protocol sha256;
- precision bits, attempt id.

A finalized record for an address blocks every later attempt.

**m values:** {1, 2, 3, 5}.
- Each m is its own H3a / K5-B obligation and needs `C₁`.
- All m share one point run (per-m marginal cost < 1 CPU-s). A subset would force a second exposure of cell 0 for no
  saving.

## 10–11. K5-B consumption and negative results (frozen map in JSON `k5b_consumption_map`)

**POSITIVE (for that m).**
- **K5-B step:** k = 1 passes with `L_1 := L1_m`.
- **Closed cells:** exactly the cells the frozen `k5b_check.py` (countersignature, sha256 pinned) marks pass on K1
  records 0–309 with `L_1 := L1_m` and `L_k := −∞` otherwise.
- **Still open:** everything else, so H3a is not yet established.
- **Restart:** as defined in the countersignature.
- **Next order-3 cells:** the next ones are informative, each under its own new preregistration.

**INCONCLUSIVE.**
- No K5-B step and no new closure.
- A restart cannot help `C₁`.
- No other cell is informative for that m until a **new** successor method passes `C₁`.
- H3a remains viable.

**NEGATIVE** (`U1 < 0` or POINT_NEGATIVE).
- H3a is false for (CUSUM, m) by Lemma K5-L. Since K5 requires all eight (D, m), the H3a route is refuted:
  SEEK_ALTERNATE_K5_ROUTE.
- The result is published in full, as valid evidence.
- The producer is not failed because of the sign, and there is no rerun under another method.

**VOID.**
- No scientific consequence; a successor protocol is required.

## 12–13. Cost and host

**Estimate:** about 3,060 CPU-s per attempt for all m together (1 rung, about 600 MiB). It is built from committed
measurements only:
- GammaTilde point run 1,160 CPU-s;
- Aux3 auxiliary evidence 171 CPU-s;
- order-3 candidates ~170 CPU-s;
- graded ranges ~1,271 CPU-s;
- certificate replays ~234 CPU-s.

**Ceilings.**
- Per attempt: RLIMIT_CPU 10,800 s, wall 14,400 s.
- Campaign: 3 attempts, hard ceiling 32,400 CPU-s.

**Intended host: rebaseguard-vultr-02**, checked read-only at preparation, with no host modification:
- x86_64, AMD EPYC-Milan;
- kernel 6.12.107+deb13-amd64;
- glibc 2.41-12+deb13u4, libc sha256 `9792e3cb…` (equal to the composite-closure binding);
- venv `/root/work/rbg-cusum-aux5-venv`: python 3.12.3, python-flint 0.9.0 (`.so` sha256 `1f7ef1f5…`), numpy 2.5.2,
  scipy 1.18.1;
- 97 GB free;
- no conflicting worker.

## 14. Completion and waiter

- **Files:** `RUN_STATE.json` (pid, argv) → `ATTEMPT_LOG.jsonl` (gate events only, no numbers) →
  `SCIENTIFIC_RECORD_SEALED.json` (atomic) → `RUN_COMPLETE.json`, or `RUN_FAILED.json`.
- **Waiter:** watches those files plus exact `/proc/<pid>/cmdline` equality; never `pgrep -f`.

## 15–17. Freeze, authorization, prelaunch

- **Freeze commit:** the commit introducing `SCIENCE_PREREGISTRATION.json`. It predates all real output; any later
  change to that file voids this preregistration.
- **Authorization template:** `protocol/AUTHORIZATION_TEMPLATE.json` has `EXECUTION_AUTHORIZED = false` and binds:
  - freeze commit, protocol sha256;
  - producer identity and executor binding;
  - K1 input identity;
  - cell set, m set, precision policy, CPU ceiling;
  - host runtime identity.

  Only a separate explicit authorization may produce an activated copy in a successor commit.
- **Prelaunch verifier:** `code/prelaunch_verify.py` runs P01–P11 read-only and fails closed. The first failing check
  in the frozen order is the primary reason.

## Executor status (explicit scope limitation)

**No qualified real-cell Strategy-B executor exists in R1–R4** (`protocol/EXECUTION_BINDING.json`,
status PENDING):
- R1's real entry is the whole-cell scalar producer at the record midpoint.
- R3 and R4 real entries refuse as out of scope.
- The R4 components were qualified on manufactured systems and on the real Arb path with synthetic candidates, never
  composed as a point run at e = 0 on the real certifier.

**Consequences.**
- Check P05 refuses launch until a successor implements the executor (E1–E2) and qualifies it non-scientifically
  (E3).
- The successor then binds the executor by `EXECUTION_BINDING_AMENDMENT.json` (E4), leaving the science file
  byte-identical, and re-runs the verifier and the static review (E5).
- This task does not implement or run that executor, because only design, preregistration and freeze are authorized.
