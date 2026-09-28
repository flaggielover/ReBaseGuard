# A0_CERTIFIER_STUDY — pointwise order-0 / ARL certifier study (stream C, cell-308 research campaign)

> **LATENT-PROXY NOTICE (quarantine T1/T2).** Every Λ value, bound, bracket and slack in this file, in
> `A0_C1_TABLES.md`, `results/` and `certs/` is at a declared validation drift e ∈ {1/2, 1, 11/10, 27/10, 3, 7/2}.
> By Theorem M these are latent proxies. They stay inside `streams/A0/`. They are never put next to any tail-cell
> number, and no transfer into [6/5, 13/5] or its mirror is derived or stated. No cell id is used anywhere in this
> stream. Target evaluations: 0. Band evaluations: 0.

Status: C1, C2, C4, C5 complete; C3 controls 60/60 as expected and bulk re-verification 16/16 PASS; only the 27/10 hull control was still running at hand-back (§8).

## 0. Scope, governance, what was run

**Object.** This study is about the pointwise quantity Λ(e) = E_a[τ](e) = ((I − K_e)^{-1} 1)(a) of the CUSUM kernel
(THEOREM_AD Lemma K). It uses:
* the whole-kernel supersolution lemma, which gives an upper bound U;
* a P1 subsolution lemma, new here (§1.2), which gives a lower bound L;
* the C1b tame lower bound Λ_lo.

**Guards** (`a0_common.py`).
* `c308_quarantine.py` is loaded by path and its import guard is installed.
* The name `ov_quarantine`, imported by the overnight certifiers, is bound to a shim. The shim's `guard_drift` calls
  BOTH the campaign guard and the real overnight guard, which is loaded by path under a private name. Its
  `log_execution` always refuses, so no certifier can write into OV.
* Every entry point calls `declared_drift`, which checks the declared set and then both guards, before any
  evaluation.
* The C1b hull variant also guards its 2^-20 hull interval.
* Smoke test: 19/10 and 9/5 were refused by `declared_drift`, and e = 2 was refused by the shim, by C1b `Ctx` and by
  C2b `Setup`, before any evaluation (ledger INFRASTRUCTURE line).

**Pinned code.**
* C1b is loaded from the sha256 pins in `OV/validation/C1B_R2_CODE_PINS.json` and checked against the git blob at
  HEAD. The six load-bearing modules all match.
* C2b and `c7_gaussian` have no pins file. `A0_CODE_PINS.json` pins their committed bytes (written before the first
  run; git blob match checked at load).
* Modules are executed from verified bytes. There is no filesystem import and no `.pyc`, the same method as
  `rlr307_pinned`. A module identity check (every internal binding is the verified module, `Q` is the shim) is
  asserted at load.

**Ledger.** Every job appends one line with agent `streamC`, class NONTARGET_DRIFT_VALIDATION and
`cells_touched = []`; the setup has one INFRASTRUCTURE line. There are 0 LEAK_FLAGs. Jobs that fail with an exception
write no ledger line; the queue logs in `logs/` record them.

**OV.** OV was never written: the overnight CLI mains were never run, and only functions were imported.
`git status --short level4/closure_proofs/p5y_k5_tail_overnight_research` prints nothing (§8).

**Execution.**
* Queue: `a0_queue.py` with at most 4 processes, each under RLIMIT_CPU (3000 s in batch 1, 3600 s in batches 2–3),
  at nice 5.
* The machine was shared with other streams (load average up to about 80 on 6 cores). CPU seconds are
  `process_time` of the job.

## 1. C1 — measured U, L, estimate, slack, bracket, cost

### 1.1 Reference (NON-CERTIFIED)

**Nystrom estimate.** Λ_ref is the Richardson O(h²) extrapolation of the pinned C2b Nystrom values Λ_h at
N = 40 and N = 80. The three-mesh ratio (Λ_40 − Λ_20)/(Λ_80 − Λ_40) is 3.98–4.002 at every drift, which is clean
O(h²).

**Monte Carlo.** `a0_mc.py` is written independently from the model: 10^6 runs per drift, seed 20260928. It agrees
with Λ_ref at every drift with |z| ≤ 0.35.

The exact figures are in `A0_C1_TABLES.md`. Slack means bound / Λ_ref − 1.

### 1.2 The certifiers measured

| id | statement | family / selection | checker (trust) |
|---|---|---|---|
| **C2B_P1** | U ≥ Λ(e) | pinned `c2b_certify.run` verbatim: Nystrom P1 proposal V_h, float (α, β) selection, α on the grid 1 + k·2^-12 | pinned `c2b_exact.certify` (reviewed) |
| **C2B_P1 sub** | L ≤ Λ(e) | w = c·V_h, with c = a/2^40 chosen exactly (integer arithmetic) | **new**: `a0_c2b.sub_certify` |
| **C2B_P1_EXACT_SCALE** (`a0_c2bx`) | U, L | same proposal; w = a·V_h/2^40 with the smallest (U) or largest (L) a allowed by exact per-cell linear constraints | U: pinned `c2b_exact.certify`; L: `sub_certify` |
| **C1B_PW** (`a0_c1b`) | U = Ā, L = Λ_lo | pinned C1b whole-kernel W path (float LS candidate of strip-piecewise degree d, D1 scaling, S2 check, Λ_lo formula), composed from the pinned functions | pinned `c1b_certpw.check_supersolution` (reviewed) |
| **C1B_PW_HULL** (`a0_c1bh`) | U, L on the 2^-20 dyadic hull of e | same, through the pinned block path (e_r = 2^-21) | same |

**Subsolution lemma (new; used only for L).**
1. On each simplex, 1 + Ψ − w ≥ (1 + IΨ − w) − |Ψ − IΨ|. The first term is affine. At a vertex it is at least
   1 + (K_e w)_lower(v) − w(v). The second term is bounded by the reviewed C2b interpolation bound, which is
   sign-free. So the per-cell condition min_v[1 + (Kw)_lo − w] ≥ err(T) gives w ≤ 1 + K_e w on R.
2. Then u = G1 − w satisfies u ≥ K_e u. Hence u ≥ K_e^n u, and |K_e^n u| ≤ ‖u‖ sup_x P_x(τ > n) → 0. G1 is bounded:
   for example, the certified supersolution at the same drift bounds it.
3. So w(a) ≤ Λ(e).

`sub_certify` reuses the pinned `kernel_nodes(upper=False)` and `hessian_bounds`. The review confirmed that both are
rigorous for any sign of W.

**Cross-check of the W-only C1b composition.** It agrees with the pinned `certify_degree` in exact rational equality
of A_bar, Λ_lo and η_W: at e = 1, d = 4 (52.3 s versus 5.9 s) and at e = 3, d = 6 (132.1 s versus 10.8 s).
Files: `results/C1BX_*.json`.

### 1.3 Findings (validation drifts only)

* **F1 — the pinned α grid binds.**
  * At N ∈ {40, 80} and every e ≥ 1, the pinned C2b U slack is 2.44e-4 to 2.48e-4. That is the α step 2^-12, not the
    certificate: `alpha = 4097/4096`, `beta = 0`, and the certified interpolation term max_err is ≤ 8e-5.
  * At e = 1/2 the slack is 1.2e-3 (N = 40) and 4.7e-4 (N = 80).
  * The C2b author recorded the same effect at N = 40, e = 3.
* **F2 — exact-scale selection removes it.**
  * With the same proposal and the same pinned checker, U slack at N = 80 falls to about the certified interpolation
    term.
  * The exact figures per drift are in the table of §1.4. For example, at 27/10: U slack +3.35e-5,
    L slack −3.18e-5, bracket 6.5e-5.
  * No bump or decrement was ever needed: the exact selection is feasible for the pinned checker at the first try.
* **F3 — P1 subsolution brackets tightly.**
  * At N = 80, L slack is −2.7e-5 to −1.0e-4 for e ≥ 1, and −4.3e-4 at e = 1/2.
  * Together with F2, the certified bracket U/L − 1 at N = 80 is about twice the interpolation term. The Nystrom
    value sits inside it.
* **F4 — C1b PW is competitive for U but not monotone in d; its Λ_lo is loose at high d.**
  * The best degree varies:
    * d = 8 at e = 1 (U +1.8e-4) and at e = 3 (+1.9e-4);
    * d = 10 at e = 1/2 (+1.5e-4);
    * d = 12 at e = 7/2 (+3.5e-4).
  * d = 10 and d = 12 are often worse than d = 8: the float LS candidate gets worse at high degree.
  * Λ_lo at d = 12 is −1e-3 to −7e-3, because the residual *upper* enclosure is loose.
  * d = 4 is 1–8 % loose.
* **F5 — pointwise C1b fails closed at non-dyadic drifts.**
  * At e ∈ {11/10, 27/10}, every pointwise C1b rung (d = 4…12) raised `ValueError: G-form coefficient not on the
    2^-SC grid` in the pinned integer Taylor model. This is an exception with no value, so it is sound.
  * The 2^-20 dyadic-hull variant works, at about 3–6× the pointwise cost at the same degree.
  * **Consequence for any formal use:** C1b needs either a frozen hull rule (as in the cell-307 campaign) or a
    frozen *dyadic-down* certification point b′ = ⌊b·2^20⌋/2^20 ≤ b. The latter is valid by Theorem M T-UP, because
    an upper bound at the smaller |e| transfers upward. C2b has no such restriction; its lattices take any rational e.
* **F6 — cost.**
  * The exact part of a C2b rung is nearly drift-independent: about 130–150 s at N = 80, of which Setup (Gaussian
    lattices) is 27–32 s.
  * The float proposal (pinned Jacobi, tol 1e-13) dominates at small |e|: at N = 80 it takes about 50–60 s at
    e ≥ 27/10, about 420 s at 11/10 and about 1400 s at 1/2 (pinned run).
  * C1b pointwise d = 8: 19–70 s; d = 12: 140–190 s. Hull variant: ×3–6.

### 1.4 Per-drift summary at the declared rungs

Best certified bracket per drift over all certified rungs (min U, max L). Slack = bound / Λ_ref − 1. Every drift
passes the exact consistency check L ≤ U. Full per-rung tables are in `A0_C1_TABLES.md`, generated by
`a0_report.py --md`.

| e | deciding U rung | U slack | L slack | U/L − 1 | C2b exact-scale N = 80 CPU s |
|---|---|---|---|---|---|
| 1/2 | C1b d = 10 (C2b N = 80: +3.9e-4) | +1.5e-4 | −4.3e-4 | 5.1e-4 | 1301 |
| 1 | C2b exact-scale N = 80 | +9.7e-5 | −9.8e-5 | 2.0e-4 | 640 |
| 11/10 | C2b exact-scale N = 80 | +7.9e-5 | −7.9e-5 | 1.6e-4 | 533 |
| 27/10 | C2b exact-scale N = 80 | +3.4e-5 | −3.2e-5 | 6.5e-5 | 164 |
| 3 | C2b exact-scale N = 80 | +3.2e-5 | −3.0e-5 | 6.2e-5 | 157 |
| 7/2 | C2b exact-scale N = 80 | +2.9e-5 | −2.7e-5 | 5.6e-5 | 147 |

Hull C1b at the two drifts next to the band:

| e | d = 4 | d = 10 | d = 12 |
|---|---|---|---|
| 11/10 | U +8.0e-3 (31 s) | U +2.8e-4, L −4.4e-4 (1141 s) | U +8.1e-4, L −1.7e-3 (1550 s) |
| 27/10 | U +9.2e-3 (17 s) | U +6.6e-4, L −1.6e-3 (998 s) | U +3.4e-4, L −1.2e-3 (1464 s) |

## 2. C2 — the deterministic pointwise ladder (research declaration)

The ladder is implemented in `a0_ladder.py`. Rules R1–R6 are in its docstring.

| rule | content | reason (validation-drift evidence only) |
|---|---|---|
| R1 rung set | fixed rung set, no early stopping: **C2b exact-scale P1 at N ∈ {20, 40, 80}**, plus **C1b PW W-only at d ∈ {8, 10, 12}** (pointwise at a dyadic e, 2^-20 hull otherwise) | N = 80 gives U slack ≈ interpolation term (F2) at an affordable cost (F6). N = 20 and 40 are cheap fail-closed backups. N = 160 is projected at ×8 and was not run. C1b is non-monotone in d (F4), so all three degrees are kept and the minimum is taken. It is an independent second implementation (a Taylor-model enclosure of a polynomial family, versus a P1 Hessian bound), which feeds R4. |
| R2 operation bounds | every loop has a declared bound: Jacobi maxit 20000 / tol 1e-13 (pinned), BUMP_MAX 64, sub decrements ≤ 64, C1b enclosure extra_levels 4 (pinned default), hull bits 20 | there is no wall-clock or CPU rule anywhere in the value path (fixes REVIEW_C2B C2) |
| R3 composition | U = min over CERTIFIED upper rungs; L = max over CERTIFIED lower rungs | every rung is a proof, so a min of proofs is a proof |
| R4 consistency | L ≤ U is required, exactly, across both implementations. L > U gives INCONSISTENT and no value | a soundness alarm that can fire. It held at every drift (§1.4) |
| R5 fail-closed | no certified upper rung means NOT_CERTIFIED, with no U | — |
| R6 CPU cap | per process, RLIMIT_CPU = Σ per-rung caps (C2b 300/900/3600 s at N = 20/40/80, C1b 900/1800/3600 s at d = 8/10/12). A cap hit kills the process and writes no file (void run); a run never falls back to fewer rungs | a cap that dropped rungs would make the value depend on machine speed. The caps are about 2.5× the worst measured rung cost under heavy load (N = 80 at e = 1/2: 1575 s; C1b d = 12: 190 s pointwise) |

**Selection rule.** The ladder was fixed after batch 1 and before any exact-scale or hull result, in two steps. The
C2b part was changed to exact-scale because of F1. The C1b degrees were widened from {10, 12} to {8, 10, 12} because
of F4. The C4 runs had already started with C1b {10, 12}; C1b d = 8 determinism is shown separately (§4).

**Recommended cost at the two drifts nearest the band** (the drifts of interest lie between them). This is the full
recommended ladder, one process:
* e = 27/10: C2b exact-scale N = 20/40/80 in about 7.5 / 28 / 160 s; C1b hull d = 8/10/12 (§1.4).
* e = 11/10: C2b N = 80 is proposal-dominated, about 520 s (§1.4).

## 3. C3 — persistence and re-verification

**Stored object** (`certs/*.json`, schema `A0_CERT/1`):
* the certifier kind and the declared drift, with the hull for the C1b hull variant;
* C2b: the mesh N, `Qbits` and the full nodal integer vector W (exact; w = W·2^-Qbits);
* C1b: the strip polynomials as exact dyadic coefficients `[i, j, k, "p/q"]` and BW;
* `W_sha256` over the canonical serialisation, and the claimed exact w(a).

**Verifier.** `a0_verify.verify_certificate` is the ONE verification function. It uses no float and no proposal. It
first validates the drift, then:
1. checks the sha256;
2. checks the declared shape (mesh columns, BW, the hull equal to the declared 2^-20 hull);
3. runs the exact checker: pinned `c2b_exact.certify`, `a0_c2b.sub_certify`, or pinned
   `c1b_certpw.check_supersolution`;
4. requires exact equality of w(a) with the claim.

**Controls** (`a0_controls.py`, all through `verify_certificate`). Every planted-invalid control is invalid **by
proof**, established from re-verified certified facts before verification:
* **V1** scaled (×0.97 for U, ×1.03 for L): the planted w(a) lies outside a certified bracket [L, U].
* **V2** atom node or constant coefficient moved outside the bracket.
* **V2b** interior node (N, N) lowered: an exact lower bound of (K_e w)(v) gives an exact pointwise violation witness.
* **V3** drift relabelled to another declared drift whose certified bracket excludes the claim.
* **V4** claim tampered.
* **V5** W changed without re-hashing.
* **ERRPATH** (C2b): a candidate accepted by the vertex-only check but rejected by the interpolation term. This is a
  sensitivity control, not a proven-invalid plant.

Results are in §8.

## 4. C4 — determinism

* `a0_ladder.py run E detA|detB` runs the ladder in two separate processes at e ∈ {3, 7/2} (C2b exact-scale N = 20,
  40, 80 and C1b d = 10, 12).
* `a0_ladder.py compare` requires three things: byte-identical certificate files, an identical exact projection
  (U, L, status, deciding rungs, consistency), and identical exact rung fields.
* C1b d = 8 is shown the same way with `a0_run.py … --out-suffix detA|detB` and `a0_c4extra.py`.

Results are in §8.

## 5. C5 — governed execution (design only)

See `A0_C5_GOVERNED_EXECUTION_DESIGN.md`.

The design is a formal-namespace guard bound as `ov_quarantine`, DECOY by default. It is armed only by a frozen
`AUTHORIZATION.json`:
* The file's sha256 is a constant in the guard's source.
* It lists the exact rational drifts and the pins of every executing module.
* Arming also requires the git exactly-once marker naming the grant commit at HEAD, as in the cell-307
  `rlr307_guard`.

After arming, `admit(b)` opens exactly one armed point at a time. Every other band drift or interval is still refused.

Before any freeze, a side-effect-free `a0_core.py` must be extracted, because the research modules import
`a0_common`, which hard-binds the research guards. No bypass exists in this stream's code.

## 6. Recommendation

**Pointwise upper bound.** Recommended: **C2b P1 with exact-scale selection** (`a0_c2bx`):
* the pinned C2b proposal V_h at N ∈ {20, 40, 80};
* w = a·V_h/2^40 with the smallest a allowed by exact per-cell constraints;
* certified by the **pinned, reviewed** `c2b_exact.certify`;
* U = min over certified rungs.

The upper-bound path contains **no new certification code**. The exact selection is only a proposal, so soundness
rests entirely on the reviewed checker.

**Lower bound and consistency.** Use the A0 P1 subsolution (`sub_certify`, new, needs review) together with C1b PW
d ∈ {8, 10, 12}, which is an independent implementation. R4 (L ≤ U across implementations) is the consistency alarm.

**Persistence.** Persist every certificate and re-verify with `verify_certificate` before any use (C3).

**By Theorem M.** A single U(b) at the smaller-|e| end b of a block is a valid Ā for the whole block. The C1b cross
rung then needs a dyadic b (dyadic-down rounding is allowed by Theorem M) or the hull rule.

## 8. Completion state (hand-back)

**C1 — done.** Tables are in §1.4 and `A0_C1_TABLES.md`; exact values in `results/A0_C1_TABLE.json`.
* The reference is non-certified: Nystrom Richardson with ratio 3.98–4.00, and Monte Carlo agrees at |z| ≤ 0.35.

**C2 — done** (`a0_ladder.py`, rules R1–R6).
* The ladder at e = 3 and e = 7/2 took about 440–475 CPU s. C2b at N = 80 decided both drifts.

**C3 — controls and re-verification** (all through `verify_certificate`).

| file | rung | controls as expected |
|---|---|---|
| `C3_CONTROLS_C2B_e11_10_N40` | C2b, N = 40 | 12 / 12 |
| `C3_CONTROLS_C2B_e27_10_N40` | C2b, N = 40 | 12 / 12 |
| `C3_CONTROLS_C2BX_e11_10_N40` | C2b exact-scale, N = 40 | 12 / 12 |
| `C3_CONTROLS_C2BX_e27_10_N40` | C2b exact-scale, N = 40 | 12 / 12 |
| `C3_CONTROLS_C1B_e1_d12` | C1b pointwise, d = 12 | 6 / 6 |
| `C3_CONTROLS_C1BH_e11_10_d12` | C1b hull, d = 12 | 6 / 6 |

* Every planted-invalid case failed on the certificate inequality, and every integrity plant failed on its
  integrity clause (claim, or sha256).
* The C2b err-path control was accepted by the vertex-only check and rejected by the interpolation term.
* **Two fixes made along the way.**
  * First C1b control: the 0.97 scaling produced non-dyadic coefficients and the pinned checker raised an exception.
    The scaling factor is now dyadic, and `verify_certificate` maps a checker `ValueError` to FAIL
    `CHECKER_REFUSED_INPUT` (fail-closed).
  * Batch-3 queue: it crashed on an over-long per-job log name. `a0_queue` now truncates long names with a hash.
* **Bulk re-verification without the proposal: 16 / 16 PASS.**
  * `C3_REVERIFY_FINAL_C2BX_N80`: 12 / 12. These are the C2b exact-scale upper and lower certificates at N = 80 for
    e = 1/2, 1, 11/10 and 27/10, plus the ladder detA certificates at 3 and 7/2.
  * `C3_REVERIFY_FINAL_C1B_d12`: 3 / 3.
  * `C3_REVERIFY_FINAL_C1BH_d12_27_10`: 1 / 1.
* **Still running at hand-back:** `C3_CONTROLS_C1BH_e27_10_d12`, the 27/10 hull control, left over from the first
  batch-4 launch.
* **Persistence manifest.** `certs/CERTS_MANIFEST.json` gives, for every certificate: file name, sha256, size,
  certifier, drift, rung and exact claim. It can be committed without the ~50 MB of certificate files.

**C4 — PASS.**
* The ladder was run twice at e = 3 and e = 7/2 in separate processes. All 8 of 8 certificate files are
  byte-identical, and the exact projection and the rung fields are identical.
* C1b d = 8 file pairs are byte-identical: `C4_FILEPAIRS_C1B_d8`.
* The comparator's planted negative control was detected.

**C5 — design done** (`A0_C5_GOVERNED_EXECUTION_DESIGN.md`). Nothing is implemented.

**Governance.**
* OV is untouched: `git status --short` on OV is empty.
* 0 band evaluations and 0 target evaluations.
* Ledger: NONTARGET_DRIFT_VALIDATION and INFRASTRUCTURE only, with 0 LEAK_FLAGs.
* The quarantine scan finds 0 A0 findings.

## 7. Open issues

1. **`sub_certify` is new and unreviewed.**
   * Its proof is in §1.2. It reuses the reviewed vertex evaluator (lower mode) and the reviewed sign-free
     interpolation bound.
   * It is not load-bearing for Ā (an upper bound), but it is load-bearing for R4 and for the proofs of invalidity of
     the C3 plants.
   * It needs an independent review before any freeze.
2. **The ERRPATH control is sensitivity only.** No rigorous off-node violation witness is produced here; the C2b
   review produced such witnesses with its own evaluator.
3. **`a0_core` extraction** is needed before a freeze (C5 §6), followed by re-validation with byte-identical
   certificates.
4. **C1b high-degree non-monotonicity** (F4) is a float LS conditioning effect. It is a tightness issue only. The
   minimum over d handles it.
5. **Proposal cost at small |e|.** The pinned Jacobi with tol 1e-13 dominates. A warm-started proposal (N/2 → N
   prolongation) would cut it. It would be a new untrusted proposal, so soundness would be unaffected, but it would
   need re-declaration.
6. **N = 160 was not measured.** Projected ×8 of N = 80, which is beyond the declared caps.
7. **Timing.** CPU numbers were taken on a heavily shared machine and are indicative. Nothing in the value path
   depends on them (R2, R6).
8. **C2b block certification** (non-pointwise) was not studied here. By Theorem M it is not needed for Ā.
