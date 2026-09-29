# Cell-308 MB formal prospective closure campaign (r1): protocol

**Status: FROZEN (r3)** at the r3 freeze commit on branch `p5y-k5-cell308-mb-r1` (the last commit touching
the frozen directories; it regenerates `protocol/MB308_FREEZE.json`). Freeze r1 was `a7fe3028`; its official
qualification FAILED on two verifier defects and is preserved in `qualification/r1_failed/` (§13). Freeze r2 was
`29b68d5e`; its official qualification FAILED on Q12 alone, on runtimes measured across two host sleeps, and is
preserved in `qualification/r2_failed/` (§14). Nothing in this protocol authorizes a target evaluation; only the
grant (§10 step 4) does.

## 1. Scope and authority

* One exactly-once, **closure-only** evaluation of CUSUM K5 cell 308 (m = 5) under route R-MB (Theorem MB r1), after
  freeze → official qualification → independent qualification review (QUALIFICATION_ACCEPTED) → grant.
* **Closure is not adoption.** No floor r2 change, no r6, no adoption, no K5 or P5Y closure, no main-branch
  integration, no push.
* **User ruling (incident review C4).** The grant must record the user's explicit CLOSURE_ONLY ruling for a
  profile-transport consumer on cell 308, taken with incidents 01–03, H4.3b, the coordinator disclosures I-a…I-e and
  E1′, and the incident-independence review in view. Without that record the grant is not written and the campaign
  STOPS before the grant.
* Research provenance: `level4/closure_proofs/p5y_k5_cell308_research/` (theory, streams, reviews, audit, ledger).

## 2. Scientific object and closure criterion

* **Theorem MB r1** (`theory/THEOREM_MB.md`, a byte copy of the research file reviewed by REVIEW_THEOREM_MB_R1 and
  corrected per its C1–C6): Γ_MB = g_hi + P*_B is a certified upper bound on sup_{e∈E} g_5(e) on the cover cell E of
  cell 308, from the committed TC-T inputs, block triples S_i on the C2 partition, and the TPT-B transport.
* **Criterion (the K5 criterion, unchanged):** a certified upper bound on sup_cell g that is strictly negative.
  Frozen form: **Γ_dec := g_hi + max(P*_B(primary), P_hi(independent)) < 0 in exact rationals.** Γ_dec = 0 does not
  close.
* **Independence wording (incident review C3):** "independent of target outcome" means temporal and parametric
  independence only. Motivational independence is not claimed. Result-chasing risk: MEDIUM–HIGH.

## 3. Decisions (each fixed by a target-free rule; design d1, research `streams/FORMAL/MB308_DESIGN_DRAFT.md`)

| # | decision | frozen value | reason |
|---|---|---|---|
| D1 | partition | N = max(1, ⌈(x_hi − x_lo)/(1/100)⌉) equal exact sub-intervals E_i of cell 308's cover interval (N = 11) | C2's rule, reused by the cell-307 campaign |
| D2 | hulls, pointwise drifts | B_i = outward 2^-20 dyadic hull of E_i; b_i = lo(B_i) ≤ lo(E_i), dyadic | pinned C1b needs dyadic drifts; Theorem M makes b_i valid on E_i |
| D3 | RLR block ladder | pinned `certify_degree(centre, d, BW_PW, e_r = radius)` on B_i, d ∈ (4, 6, 8), TIGHT_CT = BLOCK_LIGHT = True; Lemma Lad | the cell-307 Stage-1 rules P2–P4, unchanged |
| D4 | pointwise Λ ladder at b_i | C2b exact-scale N ∈ {20, 40, 80} (pinned `c2b_exact.certify`, persisted W) and C1b pointwise d ∈ {8, 10, 12}; U-candidates from certified upper rungs, L-candidates from certified lower rungs | stream A0 findings F1–F4 at non-target drifts; REVIEW_A0_CERTIFIER_R1 |
| D5 | admission of an upper rung into U_i | (i) its persisted certificate is VERIFIED by the independent verifier (C2b: `vd_pl`; C1b: `vd_verify`) within the frozen operation budget, and (ii) a certified lower rung of the **other** implementation exists with L_other ≤ U. REFUTED, or L_other > U for **any** certified upper rung (verified or not), ⇒ INCONSISTENT. No other-implementation lower rung ⇒ ALARM_UNAVAILABLE (rung not admitted). UNDECIDED ⇒ rung not admitted. C1b upper rungs with d > 6 are NOT_INDEPENDENTLY_VERIFIED and never admitted (verification infeasible in budget, VERIFIER_REPORT D7); they are computed for their Λ_lo only | R7; REVIEW_A0 C2; builder decision 1 (stricter reading accepted) |
| D6 | envelope | Ū_i = min_{j ≤ i} U_j over the pre-declared b_j only; a b_i without an admitted rung contributes nothing | Lemma M-U; review N8 |
| D7 | members of S_i | (1) S_I1, reproduced by the frozen consumer; (2) Dv′-M on REGISTRY_C1's and REGISTRY_C2's committed cell inputs with Abar := min(Abar, Ū_i), through the frozen `deflated_consume.atom_constants_r2`; (3) D14-M on the RLR ladder record of B_i with Ā′ = min(Ā_B, Ū_i), Lemma DM (D_lo′), A0 slot min(Ā′_eff, C_R); (4) Lemma G with C_R of B_i. S_i = componentwise min of the available members | dominance (charter rule 5); THEOREM_MB r1 §6 |
| D8 | missing certificates | absent members only weaken S_i; nothing is retried | fail-safe |
| D9 | consumer | TPT-B via `tptb_tail` on cell 308's committed TC-T inputs; pieces cut at every E_i end and at e0; gates C5 (E = [e0 − ρ, e0 + ρ] exactly), C6 (per-piece non-emptiness), G-R3b (per-r tuple and every block's profile polynomials equal `tuple_independent` exactly) | Theorem MB r1 §7; stream F3 |
| D10 | computed on the target | only: controls C-A and C-B (historical reproduction), Stage 1, the members and S_i, P*_B (primary) and [P_lo, P_hi] (independent), P*_B ≤ P_frozen(S_I1). **Never** P_TPT(S_I1), P_C5T(S_I1) or any other route value | brief §21; incident review C9 |
| D11 | workers, caps | 5 spawned workers; pre-marker cap 1800 s; per-job CPU caps and EVAL_CAP per §3.2; a job refuses unless its effective cap equals the declared cap | 307 rule; REVIEW_A0 C3 |
| D12 | primary vs independent | exact equality for every composition layer (F2); for P*_B the bracket rule P_lo ≤ P*_B(primary) (never a loose tolerance) | F2 open issue 3 |
| D13 | kernel drift map | kernel e = cover e (identity); all constants even (Lemma S, Theorem M) | THEOREM_MB r1 N6 |
| D14 | verification budgets | `vd_pl`: max_depth 12, max_boxes 10^6 per column job; `vd_verify`: max_boxes 200 000 per initial box, min_width 2^-40 (the verifiers' own defaults) | fixed before any target use |

### 3.2 Cap rule (frozen before any target computation; decoy runtime and status only)

**Rule (frozen; the 307 rule, extended).** Project cell 308's Stage-1 cost from the larger decoy wall time per job
kind and rung (C2b including its in-job verification) for 11 blocks and 11 pointwise drifts at 5 workers with
longest-first scheduling; EVAL_CAP = max(6 h, ⌈2 × projection⌉ in hours); per-job CPU cap = max(3 × the larger decoy
wall time of that kind and rung rounded up to 300 s, 1800 s). Only runtime and status are used (incident review
C7(b)); no certified value of any decoy is read by this rule.

**Measured decoy costs** (pre-freeze exploration with the pre-freeze build `55d3719c`, full ladder, 5 workers, no
other campaign job running to the coordinator's knowledge; record `evidence_prefreeze/DECOY_TIMING_PREFREEZE.json`; full outputs kept outside the
repository with their sha256 recorded there). Every job CERTIFIED; every C2b rung VERIFIED by `vd_pl` and admitted;
no alarm.

| job kind, rung | decoy 297 (5 blocks) max wall s | decoy 316 (blocks 0–2) max wall s | used |
|---|---|---|---|
| RLR d4 | 276.5 | 139.6 | 276.5 |
| RLR d6 | 1379.1 | 1327.8 | 1379.1 |
| RLR d8 | 2236.0 | 2816.6 | 2816.6 |
| C2b N20 (+ verification) | 43.4 (+3.3) | 40.3 (+2.8) | 46.7 |
| C2b N40 (+ verification) | 144.6 (+19.7) | 96.7 (+14.8) | 164.3 |
| C2b N80 (+ verification) | 759.2 (+136.0) | 342.0 (+88.9) | 895.2 |

The C2b job wall times already include their in-job verification; the "used" column adds the verification seconds
once more. The double count is conservative, and Q12 uses the same convention.
| C1b d8 | 34.3 | 32.2 | 34.3 |
| C1b d10 | 148.1 | 137.4 | 148.1 |
| C1b d12 | 184.5 | 194.0 | 194.0 |

Stage-1 wall: 297 all blocks 5142.1 s; 316 blocks 0–2 3055.8 s.

**Projection for cell 308:** 99 jobs, 65 502.8 job-seconds; longest-first on 5 workers gives a makespan of
**13 110.8 s = 3.64 h**.

**Frozen values:** EVAL_CAP = max(6 h, ⌈7.28 h⌉) = **8 h = 28 800 s**; pre-marker cap 1800 s; workers 5; per-job CPU caps
RLR {d4: 1800, d6: 4200, d8: 8700} s; C2b {N20: 1800, N40: 1800, N80: 2700} s; C1b {d8, d10, d12: 1800} s; VER (unused
in the frozen ladder) 1800 s. Q12 re-derives the projection from the official QC02/QC03 runtimes and requires
EVAL_CAP ≥ ⌈1.5 × projection⌉ and every per-job cap ≥ 2 × the official maximum wall time of its kind and rung.

## 4. Stage 1 (after the marker)

* S1a: RLR ladder on every B_i (D3).
* S1b: pointwise Λ ladder at every b_i (D4); every certificate persisted in memory with its sha256.
* S1c: independent verification of certified upper rungs (D5).
* S1d: admission and alarm (D5); INCONSISTENT ⇒ INDETERMINATE.
* S1e: envelope (D6), members and S_i (D7), each layer equal to the independent reconstruction F2
  (`streams/INDEP/mb_independent.py`) exactly; the RLR ladder also against `rlr307_independent`.
* A rung exception inside a pinned certifier is a non-certificate (recorded). MemoryError, OSError, worker death, a
  cap hit, a guard refusal and signals are execution failures (INDETERMINATE).

## 5. Controls, Stage 2 and decision

**Controls (before the marker; historical reproductions only; tripwires verified armed).**
* C-A: cell 308 under S_I1 through C2's frozen consumer reproduces C2's committed record exactly (Gamma_exact,
  A_exact, provenance, H_exact, M_after_exact, pass, per-supply records).
* C-B: `tptb_tail` reproduction gates with S_I1 at s = ρ (G-R1, G-R2, G-R4, G-CF) and G-R3b; no penalty other than the
  frozen one is computed.
* Either failing ⇒ CONTROL_FAILED, sealed, target **not** consumed, campaign STOPS.
* No file of this namespace reads anything under the research `history/recon/` (incident review C2).

**Stage 2.** TPT-B (D9) with the S_i; [P_lo, P_hi] by F2; P_lo ≤ P*_B(primary) and P*_B(primary) ≤ P_frozen(S_I1)
(else INDEPENDENT_CHECK_FAILED); Γ_dec (§2).

## 6. Independent reconstruction and shared code surface

| layer | primary | independent | relation |
|---|---|---|---|
| pointwise upper certificates (C2b) | pinned `c2b_exact.certify` via `mb308_a0core` | `vd_pl` (stream VERIFY) | verification of the same persisted W; shared: the kernel model and the P1 layout (by construction) |
| C1b lower bounds Λ_lo | pinned C1b | — (alarm only) | single implementation, used only as an alarm |
| RLR block certificates (τ, C_T, Ā_B, C_R, D_lo, D1, D2, L1, L2, τ_a,lo) | pinned C1b | — | **single implementation** (as in the cell-307 campaign; disclosed) |
| ladder / D14-M / Dv′-M / G / envelope / min | `mb308_stage1`, `mb308_supply` | F2 `mb_independent` (+ `rlr307_independent` for Lemma Lad) | exact equality |
| TC-T per-r tuple and profile polynomials | frozen consumer via `tptb_tail` | F3 `tuple_independent` | exact equality (G-R3b) |
| TPT-B integral | overnight `tpt.py` r2 `penalty_blocked` + C6 wrapper | F2 exact bracket | P_lo ≤ P*_B; decision uses max(P*_B, P_hi) |
| consumer reproduction | C2 frozen consumer | — | exact reproduction of committed records (C-A) |

Measured shared surfaces: F2 boilerplate only; F3 boilerplate only; VERIFY boilerplate plus the layout-fixed mesh loops.

## 7. Exactly-once mechanics

The accepted cell-307 driver's design, re-targeted (`code/mb308_driver.py`): identity (worktree, git dir, common dir,
branch), interpreter flags `-I -S -B`, no prior evaluation (marker, pending ref, result anywhere, emergency file),
lstat of guarded paths, clean tree including ignored files in the namespace, derived grant chain
(freeze → qualification → review → grant), pins (sha256 + git blob), lineage, r5 as expected and no r6, seal
preconditions, geometry cross-checks, controls; then the marker `refs/p5y-k5-cell308-mb-r1/target-consumed` → grant
by CAS; after the marker nothing escapes; seal from memory (object store, pending ref
`refs/p5y-k5-cell308-mb-r1/pending-result`, private-index commit, O_EXCL|O_NOFOLLOW materialization); `seal-only`
never computes. Guard arming: marker names the grant commit at HEAD and the admitted set equals the 37 pairs the
guard derives from `CELL308` by D1/D2 (disclosed deviation from the A0 C5 design's hash-bound authorization file:
the set is a pure function of the pinned guard bytes).

## 8. Frozen outcome table

| sealed status | condition | conclusion (applied verbatim by the adjudication) |
|---|---|---|
| TARGET_EVALUATED | all checks pass and **Γ_dec < 0** (exact) | **CELL308_CLOSED_UNDER_MB** |
| TARGET_EVALUATED | all checks pass and Γ_dec ≥ 0 (including Γ_dec = 0) | **CELL308_NOT_CLOSED_UNDER_MB** |
| INDEPENDENT_CHECK_FAILED, INCONSISTENT, C6 refusal, TARGET_EVALUATION_FAILED, POST_MARKER_RECORDING_FAILED, unsealable | any post-marker failure | **CELL308_EXECUTION_INDETERMINATE** (target consumed; no rerun) |
| CONTROL_FAILED | a control fails | no conclusion; target not consumed; STOP |

Strictness, rounding (exact), tolerance (none), members, rules and caps never change after the freeze.

## 9. Qualification (`config/QUALIFICATION_CASES.json`; `code/mb308_qualify.py`)

| case | gates | content |
|---|---|---|
| QC01 | Q2 | committed-record rehearsal on cell 305 (C-A, C-B; equality only) |
| QC02 | Q2, Q6, Q7, Q12 | full Stage 1 + Stage 2 on decoy cover cell 297 through the driver's decoy mode (incl. decreasing-constant and r = 0-bound bundles) |
| QC03 | Q6 | Stage 1 on the first three blocks of decoy cover cell 316 (above the band) |
| QC04 | Q3 | determinism (incl. REVIEW_A0 C4 pair on the frozen driver) |
| QC05 | Q1, Q4, Q5, Q7 | two-sided composition with mutants (primary vs F2) |
| QC06 | Q2, Q4 | pointwise-certificate package through the formal path (REVIEW_A0 C1, C6) |
| QC07 | Q5 | TPT-B controls (incl. endpoint-only and common-mode G-R3b plants) |
| QC08 | Q6 | independent Monte Carlo at decoy drifts |
| QC09 | Q9, Q12 | guard |
| QC10 | Q12 | exactly-once flows in `git clone --shared` sandboxes |
| QC11 | Q2, Q12 | static structure |
| QC12 | Q9 | leak scans (patterns from the pinned sanctioned file; neutral planted controls) |
| QC13 | Q10, Q11 | temporal and governance state; incident review conditions C1–C8 checked by path |
| Q8 | Q8 | freeze manifest |

Every case carries a boolean `pass`; the aggregator fails loudly on a missing key. No gate may be waived.

## 10. Order of operations and STOP conditions

1. Freeze (a commit on branch `p5y-k5-cell308-mb-r1`, worktree `/Users/suzhe/ReBaseGuard-c308mb`).
2. Official qualification at the freeze commit; committed as qualification evidence only.
3. Fresh independent qualification review: line 2 (line 1 is the title) exactly QUALIFICATION_ACCEPTED or
   QUALIFICATION_REJECTED, appearing exactly once as a whole line (the driver's `verdict_ok`).
   **REJECTED ⇒ STOP** (no same-round repair; a successor campaign only).
4. The grant, committed alone, binding cell 308, route MB, the freeze/qualification/review commits, the driver
   sha256, the manifest sha256, exactly once, CLOSURE_ONLY, **and the user's C4 ruling**.
5. `execute`, once, at the grant commit; post-execution checks.
6. Fresh independent execution review (verdict on line 2): EXECUTION_ACCEPTED or EXECUTION_REJECTED (**REJECTED ⇒ STOP**, no rerun).
7. Scientific adjudication applying §8 verbatim.
8. Fresh independent adjudication review (verdict on line 2): ADJUDICATION_ACCEPTED or ADJUDICATION_REJECTED.
9. Handover.

Additional STOP conditions: the start state differs; the target appears consumed or a result exists; freeze inputs
drift; qualification data includes 305–309 values beyond the committed-305 reproduction or any target proxy; the
exactly-once infrastructure is found unsafe; the user's C4 ruling is absent at step 4.

## 11. Disclosed liabilities (carried verbatim into the grant and the adjudication)

* Incident 01 and residue (profile transport; the route family was chosen knowing committed tail structure).
* Incidents 02 and 03 (incident 03's sentence was read by stream A0; audit a1 C1(a)).
* H4.3b (historical route-audit juxtaposition).
* Coordinator disclosures I-a…I-e and E1′ (the coordinator holds every ingredient of an incident-01-class estimate of
  R-MB's outcome and has not formed it).
* Exposures of streams F2/F3 through theorem texts (a1 C1(b)); the quarantine rule breach of stream A's R1/R4
  (amendment 1).
* Single-implementation inputs: the RLR block certificates.
* Result-chasing risk MEDIUM–HIGH.
* Incident-independence review conditions C1–C9 (`research/reviews/INCIDENT_INDEPENDENCE_REVIEW_MB308.md`).

## 12. Ledger and quarantine

* Research ledger `p5y_k5_cell308_research/ledger/TARGET_INTEGRITY_LEDGER.jsonl` records every pre-freeze run.
* The qualification carries its ledger entries inside its report; they are appended after the seal together with the
  execution's line (307 precedent). The execution writes no ledger line before its seal.
* Guard: `code/mb308_guard.py`; quarantine config: research `config/TARGET_QUARANTINE_308.json` and amendment 1.

## 13. Freeze r2: verifier-only repair (after the r1 official qualification FAILED)

**r1** (freeze `a7fe3028`; qualification evidence `3a05aef7`, moved unchanged to `qualification/r1_failed/`): FAIL on
QC04 and QC12, i.e. gates Q3 and Q9. Both were defects of the qualification verifier `code/mb308_qualify.py`, not of
the science or the exactly-once machinery; 0 target evaluations.

* **QC04 (determinism).** The comparison included nondeterministic timing fields nested inside the records (the RLR
  certifier's `residual_enclosures/*/seconds` and `seconds/*`; the ladder's `verification/seconds`, `wall_seconds`,
  `record/cpu_seconds`). Every non-timing field was identical. **Repair:** strip exactly the keys `seconds`,
  `wall_seconds`, `cpu_seconds` at every depth (and `cpu_cap` at the job level, as before); pass both sides through the
  driver's own publication step `jsonable` (which drops in-memory `_`-prefixed fields that no published record
  carries); require more than 0 compared leaf fields per job; a planted control mutates one non-timing leaf per pair
  and must be detected by the same comparison. This is a defect repair, **not** stricter-only: the r1 comparison could
  never pass.
* **QC12 (leak scans).** (a) The record-token scan hit only the freeze manifest's `guard.cell308_cover` field, i.e.
  cell 308's committed cover interval from `cells.json`, which the design permits as the guard's constant.
  **Repair:** the 8 tokens derived from cell 308's cells.json geometry are exempt only when every occurrence in a file
  lies inside that manifest field or in the guard source; exemptions are reported (file, field, count, never the
  value); planted controls (a non-geometry record token, and a geometry token outside the guard field) must fire.
  (b) After the r1 evidence moved into the scanned tree, one runtime value inside a timing key of an r1 record matched
  a short tail pattern. **Repair:** in JSON files under the post-freeze directories, a tail-pattern match is exempt
  only when it lies inside a timing key (`seconds`, `wall_seconds`, `cpu_seconds`, at any depth); exemptions are
  reported by file and count; planted controls (a tail value in a non-timing field fires; one in a timing field is
  exempted and counted) go through the same function.
* **Other verifier changes:** `--records DIR` (review/dev re-verification of committed heavy records, read-only);
  `--record-scan` (dev only); the QC08 Monte-Carlo child runs only in heavy mode (a review run can no longer overwrite
  the committed QC08 record). The official mode refuses both new flags.
* **Unchanged (sha256 as at r1):** every other file of `code/`, `tests/`, `config/`, `theory/`, `errata/`,
  `evidence_prefreeze/`; in particular the driver (`965a2a30…`), the guard, Stage 1, the supply, the consumer, the
  pinned loader, the A0 core and the manifest writer. The science, the criterion, the caps and every rule of §3–§8 are
  unchanged.

## 14. Freeze r3: host-environment repair (after the r2 official qualification FAILED)

**r2** (freeze `29b68d5e`): official qualification 2026-09-29 00:11:03Z–04:54:07Z.

* **Evidence.** Commit `d031dad8`, moved unchanged to `qualification/r2_failed/`.
* **Result.** FAIL on `Q12_caps` only. Every other case and gate passed. 0 target evaluations.
* **Assessment** (coordinator, not independent). The research file `audit/QUALIFICATION_R2_FAIL_ASSESSMENT.md`
  (`2fa80954`) and its addendum a1 (`64dc4cce`).
  * **Two host sleeps.** The host slept twice while the Q12 runtimes were measured: lid closed, 01:31–01:58Z and
    03:51–04:42Z; the host also ran on battery during the second sleep. These sleeps inflate the C1b d10, RLR d6 and
    316-block-1 RLR d8 walls.
  * **A sleep-free slowdown as well.** About 15 % against r1, during the concurrent heavy-case window, on a fanless
    2P + 4E host. By itself this makes RLR d8 on block 0 of 316 (sleep-free) fail the per-job check.
  * **The failure is purely execution-environment.** The code is identical to r1, the certificates are identical
    (QC04), and every non-timing gate passed.

**The user's r3 authorization (2026-09-29, in chat).** The r3 repair covers the execution environment and sleep
contamination only:

* **Unchanged:** the scientific route, the theorem, the parameters, the consumer, the criterion and the
  exactly-once semantics.
* **No change to the caps:** the caps are neither raised nor recomputed from the contaminated r2 runtimes, and Q12
  is not weakened.
* **What the repair adds:**
  * whole-run sleep prevention;
  * AC power required at preflight;
  * sleep / wake and relevant thermal provenance;
  * fail closed on sleep during a load-bearing timing interval, or on ambiguous timing provenance;
  * same-path planted controls, under which genuine runtime / cap violations stay detectable;
  * an independent review of the repair.
* **Run conditions:** a fresh official qualification on an awake machine. After learning that the failure was not
  sleep-only, the user chose "r3 as specified, cool host": caps, Q12 and the qualification's concurrency are
  unchanged, and the official run happens only on a cool, awake host (lid open, on AC, no other heavy work).

**What r3 changes (environment only):**

* **`code/mb308_host.py` (new, pinned in the driver's helper table).** It provides:
  * three independent sleep channels:
    * **K**: CLOCK_MONOTONIC_RAW − CLOCK_UPTIME_RAW over the interval (both unadjusted);
    * **S**: `kern.sleeptime` / `kern.waketime`;
    * **L**: `pmset -g log` entries of type Sleep, Wake or DarkWake in the interval;
  * power (`pmset -g batt`), read at the start, every 60 s and at the end;
  * thermal and load, **recorded and never part of any pass**:
    * the OS thermal-pressure level (`notifyutil -g com.apple.system.thermalpressurelevel`; 0 = nominal) at every
      snapshot and sample;
    * the power log's ThermalEvent entries;
    * the load average;
    * `pmset -g therm`, kept for the record only. It is **not** a cool-host check: on this host it reports
      "no warning" while the thermal-pressure level is 1;
  * `assess()`, which is **fail-closed**. The only CLEAN outcome requires all of the following:
    * every channel available;
    * samples at most 180 s apart;
    * no channel reporting a sleep;
    * every power reading AC.

    Any other outcome is CONTAMINATED or AMBIGUOUS.
  * `keep_awake()`, which runs `caffeinate -i -m -s`. That is best effort: lid-close sleep cannot be prevented by an
    assertion, and detection is what binds.
* **Driver.**
  * `execute` and `preflight` refuse before the marker unless on AC (`HOST_NOT_ON_AC`, exit 2, nothing consumed).
  * `keep_awake` uses `-i -m -s`.
  * The evaluation interval (marker → record) and every decoy run carry host provenance.
  * No other line changes. Unchanged: EVAL_CAP, PRE_CAP, DECOY_CAP, every per-job CPU cap, the ladder, the
    workers, the order of operations, the marker, the seal, the exit codes and every scientific function.
* **Qualification verifier.**
  * **Official-run preconditions:** AC, **thermal-pressure level 0 at start**, sleep channels available. The
    qualification process itself keeps the host awake and records its own provenance.
  * **Q12 reads the QC02 / QC03 runtimes only if both conditions hold for each decoy run:**
    * its host provenance, re-assessed from the stored raw readings, is CLEAN (a stored assessment that the raw
      readings contradict is AMBIGUOUS);
    * its host interval covers the run's recorded Stage-1 (+ Stage-2) walls.

    Otherwise Q12 fails **closed**, whatever the caps. The cap computation, the thresholds (EVAL_CAP ≥
    ⌈1.5 × projection⌉; per-job cap ≥ 2 × official max wall) and §3.2 are unchanged.
  * **Fourteen planted controls through `_q12_core`**, Q12's own decision function:
    * a clean host within the caps passes;
    * each of the following fails, with the caps passing:
      * K;
      * S (parsed from real-format `sysctl` text);
      * L (real-format log lines; the parser must count exactly Sleep, DarkWake and Wake, and skip Assertions and
        Wake Requests);
      * battery;
      * an unavailable log;
      * missing clocks;
      * uncovered samples;
      * a record without provenance;
      * a stored assessment contradicted by the raw readings;
      * a host interval shorter than the run;
    * a genuine **per-job** violation on a CLEAN host fails with EVAL_CAP passing and exactly {RLR:8} failing;
    * a genuine **EVAL_CAP** violation on a CLEAN host fails with every per-job cap passing;
    * both at once report both.
  * **QC11:** branch-exact static checks of the host guards.
  * **QC10 (test file):** T23 (a planted battery reading at the `pmset` text layer → `HOST_NOT_ON_AC` before the
    marker) and host provenance in the success flow's sealed record.
* **Config and protocol.** `config/QUALIFICATION_CASES.json` (the Q12_caps, QC10 and QC11 entries), this section and
  the header.

**Independent review of the repair (before the freeze).**

* **First review:** research `reviews/REVIEW_R3_HOST_REPAIR.md`, commit `4b38eef2`, sha256
  `d39e25ef2e0adf3db9f4a32c870417c1e58b9b138386929f8a7b613441b4f491`, REPAIR_REJECTED as submitted. The core repair
  was sound, with two defects:
  * **F1:** the per-job control was not specific; it also broke EVAL_CAP.
  * **F2:** `pmset -g therm` was blind to thermal pressure.

  Conditions F3–F6 also applied. The present text applies:
  * F1, F2 and F3;
  * notes N1 (raw clock for K), N2 (interval coverage), N3 (the stored-vs-raw control, S parsed from text, exact
    fixture counts) and N6 (branch-exact QC11).
* **Delta review:** research `reviews/REVIEW_R3_HOST_REPAIR_DELTA.md` — commit 1571040d0af44c76606befffc85defce1e79a71c, sha256 2afbbf4cf608e26dfad41ab4e4d90acd0930050fd44606823c9b4e752ead8fd6, DELTA_ACCEPTED.

**Pre-declared consequences (review F3; binding).**

* r3 does **not** address the sleep-free slowdown. The headroom r1 left is the whole allowance: RLR d8 may run at most
  about 4.8 % slower than r1, and the EVAL_CAP projection at most about 6.2 % higher.
* **Any r3 official Q12 FAIL is a qualification FAIL that stops the campaign before the target (C4 point 7).** That
  holds whether the timing was CLEAN (a genuine cap failure) or CONTAMINATED / AMBIGUOUS.
* Freeze r3 is **never re-run**, and **no r4 with the same caps** is made, without a new explicit user decision
  recorded before it.

**Why the execution is fail-closed without a new rule.** The verdict is exact arithmetic and never depends on time:

* the per-job caps are CPU-time limits, which a sleep does not consume;
* the only wall-clock limits are PRE_CAP, before the marker (a hit is a refusal: nothing consumed), and EVAL_CAP,
  after it (a hit is INDETERMINATE, never a closure).

A sleep during the evaluation can therefore only waste the evaluation, never produce a wrong verdict. **Host
provenance never changes the status, the outcome or exactly-once**: there is no re-run and no re-interpretation on
host grounds. The provenance is recorded in the sealed record's `host`, and the execution review must report and
disclose it. The execution runs under the qualification's host conditions: AC (enforced), lid open, thermal-pressure
level 0 at start, no other heavy work, low-power mode off.

**Order after r3.** First the delta review of the repair, then the freeze. Then: the official qualification on a
cool, awake host; its evidence committed on its own; a fresh independent qualification review; and, only on
QUALIFICATION_ACCEPTED and every frozen prerequisite, the grant. The grant carries the user's C4 ruling (research
`ledger/USER_RULING_C4.md`, `0aeaec23`). Γ308 stays 0 until the grant.
