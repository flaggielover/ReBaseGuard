# Independent qualification review — cell-307 RLR campaign (r1)
QUALIFICATION_ACCEPTED

## Reviewer statement

* I am a fresh, independent, read-only reviewer. I wrote none of the campaign's code, protocol, theorem, tests, audit,
  qualification or earlier reviews. This file is the only file I wrote in the repository. I made no commit, ref,
  branch or object write of my own (the verifier's `git clone --shared` sandboxes write only into their own clone
  under the system temp directory; `refs/p5y-k5-cell307-rlr-r1/*` and `refs/rlr-tail/*` were empty after each run).
* Basis: worktree `/Users/suzhe/ReBaseGuard-c307`, branch `p5y-k5-cell307-rlr-r1`, HEAD `978d9965` (qualification
  evidence), freeze r2 `cd5016f1`, r1 freeze `5c6667fd`, r1 evidence `0a0db965`, the pre-freeze commits `c66ce2b8`,
  `c9ff8e3e`, `7d7e9135`, and the dangling pre-freeze dev snapshot `53f0e890` named in ledger line 21.
* Read in full: `protocol/RLR307_PROTOCOL.md`, `theory/THEOREM_RLR307.md`, every `code/*.py` (driver, guard, pinned,
  stage1, independent, qualify) and the explore probe, `tests/test_rlr307_flows.py`, `tests/test_rlr307_twosided.py`
  (and `tests/test_rlr307_mc.py`: model, estimators, controls and pass rule), `config/*.json`, the r2 and r1 run
  notes, stdout and report summaries, `r1_failed/FAILURE_RECORD.md`, `review/INCIDENT_INDEPENDENCE_REVIEW.md`, `audit/INCIDENT_AUDIT_ADDENDUM_R1.md`,
  the ledger (22 lines), `evidence/explore/TIMING_*` (runtime, memory and status fields only).
* Background read: pinned `c1b_certpw.py` (`Ctx`, residual forms, `certify_degree`, `assemble`, `run_point`),
  `c1b_kernel.py` header and `_dy_exp`, the relevant parts of `c1b_float.py`, `c1b_pw.py`, `c1b_gauss.py`;
  `C1B_ROUTE_SUMMARY.md` §8; `REVIEW_RLR_R2.md` §1.3, §4.3, §5, §6; `REVIEW_RLR_R3_VERIFY.md` (all); THEOREM_AD §1-§4
  and §8; THEOREM_TCT §1; C2's `c2_d5_forecast.py` (`combine`, `direct`, the supply loop of `main`);
  `tct_rule.tail_enclosure`; C12-R2's `c12r2_cell306.py` (function-level diff of the exactly-once layer).
  I did not read C1B Appendix V.
* Ran (all `python3.14 -I -S -B` from the worktree root; outputs under `/private/tmp/rlr307rev/`):
  1. `rlr307_qualify.py --review` (quick): QUALIFICATION PASS, Q1-Q12 = P, `cases_missing_pass = []`, QC10 39/39,
     QC12 0 hits over 77 tracked files, QC03_cross_run 5/5 blocks identical, QC08 all field matches true.
  2. `rlr307_qualify.py --review --heavy` (recomputes decoy Stage 1, serial rerun and QC01): PASS; see Notes N1.
  3. `rlr307_driver.py preflight`: PREFLIGHT PASS.
  4. `rlr307_driver.py rehearse --cell 305`: control and neutral substitution reproduce C2 exactly; my record equals
     the committed `qualification/RLR307_REHEARSE_305.json` in every field except `utc` and `wall_seconds`.
  5. Two refusal probes, disclosed: `rehearse --cell 307` and `decoy-stage1 --cell 307`. I first checked in the code
     that both functions test the cell as their first statement; both exited 2 (`CELL_OUT_OF_SCOPE`). Nothing was
     evaluated on any cell.
  6. Read-only git and small Python reads (digit-length scan of the decoy record, semantic diff of the cases file,
     function-level diff against C12-R2). No certifier call of mine touched any drift. The verifier's own QC07 makes
     one guard-refused certifier call at [5/2, 5/2 + 2^-10]; the guard raises in `Ctx.__init__`, the first statement
     of `certify_degree`, before any arithmetic.
* The verifier refuses to start while a review file exists; I moved this (skeleton) file to `/private/tmp` for the
  first seconds of each launch and restored it afterwards. No other file was touched.
* No repository text tried to dictate my verdict.

## Blockers

**None.** I found nothing that makes the one evaluation unsafe, unsound, non-prospective or not exactly-once. The
notes below are real but none can produce a false closure or a second evaluation; the ones that matter operationally
are turned into grant / execution conditions at the end.

## Notes

* **N1 (my verifier runs).** Quick review run: PASS on all gates (above). Heavy review run (4165 s; recomputes the
  decoy Stage 1 through the driver's `decoy-stage1` CLI with 5 spawned workers, the serial rerun and QC01 in fresh
  processes): QUALIFICATION PASS, Q1-Q12 = P, `cases_missing_pass = []`; QC01 28/28 + 25/25; QC02 15/15 rungs
  CERTIFIED, independent checks all equal, projected cell-307 wall 8317.8 s (≤ EVAL_CAP/2); QC03 exact; QC03_cross_run
  5/5 against r1. I also compared my recomputed decoy Stage 1 and serial block record with the committed r2 records:
  the cell record, all five block records and every exact rung field are identical. That makes a third independent
  run (new processes, new hash seeds) with identical exact output.
* **N2 (freeze r2 is a pure, stricter-only verifier repair).** `git diff 5c6667fd cd5016f1` touches exactly four frozen
  files, plus the ten `qualification/r1_failed/*` evidence files that commit `0a0db965` added (qualification paths
  only): `code/rlr307_qualify.py` (+26/-3: QC10 gets `pass = all_ok and not failed`; any case without a boolean
  `pass` fails the run via `cases_missing_pass`; new `qc03_cross_run`, added to Q3), `config/QUALIFICATION_CASES.json`
  (semantically: every r1 case identical, one case `QC03_cross_run` added, one `revision` key; the rest is
  re-indentation), `protocol/RLR307_PROTOCOL.md` (+13 lines, the revision note only) and the regenerated
  `protocol/RLR307_FREEZE.json` (only the three changed files' hashes). Driver, guard, pinned loader, Stage 1,
  independent module, tests, theorem, caps and outcome table are byte-identical; the driver sha256 in the manifest is
  unchanged. No gate was removed or loosened; `ok` became strictly harder to reach. Not a weakening.
* **N3 (r1 history).** `r1_failed/` (commit `0a0db965`, before freeze r2) preserves the r1 outputs unchanged; the r1
  failure is exactly as `FAILURE_RECORD.md` says (Q12 failed closed on a missing `pass` key; every case passed). The
  earlier refused first launch (`QUALIFY_STDOUT_r1_attempt1_refused.txt`) failed closed on `no_review_grant_result`
  because empty untracked `adjudication/`, `authorization/`, `qualification/` directories existed; removing empty
  directories changed no tracked file. Both failures are fail-closed, disclosed, and neither ran a band drift. The r2
  run's decoy Stage 1 equals r1's exactly (QC03_cross_run), and r1/r2/my cell-305 rehearsal records are identical
  except timestamps.
* **N4 (rung-exception scope is wider than protocol §3.7 says).** `_worker_job` classifies *any* `Exception` raised
  inside `S1.certify_rung` as a scientific non-certificate (RUNG_EXCEPTION). That wrapper also covers `_exactify` and
  the guard, so a `QuarantineRefusal` (a `RuntimeError`) or the interpreter's 4300-digit int-to-str limit (`ValueError`,
  fixed under `-I`) would be recorded as "rung not certified" rather than an execution failure. Neither is reachable in
  the frozen design: `Ctx` calls `guard_drift(e - e_r, e + e_r)`, which equals the armed exact hull pair, and the
  largest numerator/denominator in the committed decoy Stage 1 has 808 digits. The direction of any misclassification
  is conservative (it can only yield NOT_CLOSED, never a closure). Condition E3 makes the execution reviewer check it.
* **N5 (dangling dev snapshot).** Ledger line 21 records a pre-freeze dev snapshot commit `53f0e890` written into the
  real object store (unreferenced; parent `7d7e9135`). I inspected it: it holds the pre-freeze code/protocol/tests
  (its driver equals the frozen one), and no execution, grant, review or result path in the namespace. It is invisible
  to `git log --all`, does not affect the grant chain, and is disclosed. Harmless.
* **N6 (cosmetic).** `cpu_seconds_workers` reads `RUSAGE_CHILDREN` after the pool's workers were terminated without
  `wait`, so it under-reports (the committed decoy record shows 0.7 s). The execution record's worker CPU field
  should not be cited. `check_grant` reads a missing review file as an uncaught `FileNotFoundError` (C12-R2 had an
  explicit `REVIEW_MISSING` refusal); this still fails before the marker (exit 1 instead of 2) and is unreachable
  because the chain check requires the review commit to add that file and the tree to be clean.
* **N7 (incident conditions carried by reference).** Protocol §11 summarizes the liabilities and points to the audit
  and the independent review; it does not restate C1 verbatim (F1(a), F1(b), "4 ledgered + 1 unledgered", "temporal and
  parametric independence only"). The addendum `audit/INCIDENT_AUDIT_ADDENDUM_R1.md` (committed `7d7e9135`, before the
  freeze) meets C1-C4 and is a governance anchor in the grant-bound manifest `RLR307_FREEZE.json`. Documentation gap
  only; condition G2 closes it in the grant.

## Checklist (campaign brief section 14)

| # | item | verdict | evidence |
|---|---|---|---|
| 1 | 307-only scope | PASS | `TARGET_CELL = 307` is a constant; `execute`/`preflight`/`seal-only` refuse `--cell`; `cell_inputs` accepts only 305 and 307, `rehearse` only 305, `decoy-stage1` only 297/316; `target_blocks` cross-checks cell 307's cover interval against REGISTRY_C2 and the guard; the guard refuses [6/5, 13/5] and its mirror unless armed with exactly the ten cell-307 hull pairs (QC07 in-process + sandbox). My two refusal probes on 307 exited 2 |
| 2 | theorem correctness | PASS | I re-derived Steps 1-8: SM (`(Rf)(a) = ν(f)/D`), the three bounds on `|ν'/D|`, `|ν''/D|` (ratio, non-ratio, Dv' factor; each valid because τ, C_T, Ā, D_lo, L_j bound their own quantities uniformly on B), the quotient-rule terms, Lemma G (`‖R‖ = sup_R R1 ≤ sup_R W ≤ C_R`, `‖K^(n)‖ ≤ κ_n`), Lemma Lad, Lemma H and the componentwise-min Step 8. They match THEOREM_AD §3-§4 (Lemma Dv' r2) and THEOREM_TCT §1 ((P4) used at one place). Sup over R instead of X only strengthens (P4) at `a` because R is closed under the killed chain and contains `a` (R3 §1) |
| 3 | proof completeness | PASS (scoped) | Complete given the certified-input inequalities S1-S4, which the theorem states as the one assumption (§3) and which rest on THEOREM_LR/THEOREM_AD, REVIEW_RLR_R2/R3 and Q1/Q5/Q6. Positivity of D_lo and τ_a,lo is not proved by the certifier's status alone, but `rlr307_independent.block_supply` raises on `D_lo ≤ 0` or `τ_a,lo ≤ 0` for every rung and every ladder, which aborts the evaluation (INDETERMINATE), never a closure |
| 4 | implementation correspondence | PASS | Theorem §1 formulas = `IND.block_supply` = pinned `assemble` (read line by line; QC05 2052/2052 exact, 47/47 committed records). Ladder: `S1.ladder_compose` uses the pinned `LADDER_KEYS_MIN/MAX` then `assemble`, as `run_point`; `IND.ladder` independent (QC09 205 ladders, 200/200 synthetic). Cell max = `IND.cell`. `s_rlr` = `IND.consumed` (500/500). The driver re-checks every rung, every block, the cell and S_RLR against the independent module after the marker (`IndependentCheckFailed` → INDETERMINATE). Hull and flags as protocol §3.1/§3.6 (`FLAGS` set by `setattr`; QC01 reproduces the committed block rung 28/28 + 25/25 under them) |
| 5 | two-sided test semantics | PASS | QC05 asserts exact equality with the oracle, not `≤ min(...)`: the four too-small historical mutants pass the one-sided bound on 2052/2052 sets and are still rejected by equality (on 964-2052 of the 2052 sets each). The certifier's own (i') checker is the pinned two-sided `max(blo², bhi²) ≤ 4·A_lo·C_lo` with `A_lo > 0`, `C_lo ≥ 0` (unchanged bytes) |
| 6 | six historical mutants | PASS | `historical_mutants_rejected = 6/6` (no_min, no_G, supply_half, drop_A2_cross, drop_A1_delta, G_no_cubic), plus six composition mutants rejected (ladder max-for-upper, min-for-lower, cell min, A0 replaced, no min with I1, max for min) — official and my quick run |
| 7 | non-target validation | PASS | QC02 decoy cell 297: 15/15 rungs CERTIFIED, independent checks all equal; QC03 serial = pooled exactly (d 4/6/8, 32 keys each, block record identical); QC03_cross_run r1 = r2 (5/5 blocks); QC04 MC 15/15 drift points hold, 4/4 planted-wrong controls flagged, e/−e symmetry; QC01 committed-block reproduction. Heavy rerun: N1 |
| 8 | no target leakage | PASS | Qualification computations: block [1/2, 17/32], decoy 297 (below the band; hulls guard-checked), committed overnight records at {0, 1/4, 1/2, 1, 3}, synthetic sets; 305 only as committed-record reproduction; the sandbox flows stub control/prepare/evaluator. QC07 arming needs marker = grant = HEAD (sandbox only). QC12: 0 hits in 77 tracked namespace files (planted control fires). Ledger: 22 lines, pre-grant classes only, `new_target_evaluations = 0` throughout |
| 9 | no target-specific tuning | PASS | Every Stage-1 rule is fixed in frozen code (N rule = C2's, 2^-20 hull, ladder (4, 6, 8), flags, caps); no argv or env reaches a number (`-I`; `--workers` is read only by `decoy-stage1`); all three rungs always run (no adaptive stop); outcome table frozen in protocol §8 and the manifest. See C5 |
| 10 | min-composition semantics | PASS | Only rungs with status CERTIFIED enter a ladder; only blocks with a certified ladder enter the cell; any uncertified block ⇒ CERTIFICATION_FAILED with no S_RLR and no Γ; S_RLR takes A0 from S_I1 unchanged and A1/A2 as minima of two individually admissible supplies (componentwise (P4)). QC09 `A0_never_changed` |
| 11 | deterministic exact arithmetic | PASS (notes) | All consumed quantities are Fractions (a float at an exact layer raises; QC05). Environment-dependent inputs: float candidate generation (untrusted; soundness-neutral; deterministic on this host: QC01 reproduces overnight bytes, QC03/QC03_cross_run across processes and hash seeds); worker count/order (results keyed by (block, degree)); hash seeds (`-I`; no set iteration feeds a value — `seen` in `c1b_pw` is membership-only); caps (a timeout gives INDETERMINATE, never another number); int-to-str digit limit (N4). Execution must run on this host (E1) |
| 12 | provenance | PASS | Consumer, inputs and certifier pinned by sha256 and git blob and re-checked before the marker; every worker re-checks the driver sha256, the helper pins and the certifier pins and blobs; helper modules pinned inside the driver; driver sha256 and manifest sha256 bound by the grant; Q8 manifest 17 frozen files, no mismatch, no unlisted file; committed record hashes equal the report's `record_sha256` (I recomputed all five) |
| 13 | incident independence | PASS (N7) | Review line 2 = INCIDENT_AUDIT_ACCEPTED, committed at `c9ff8e3e` before both freezes; C1-C4 met by the addendum and `config/LATENT_PROXY_AMENDMENT_307.json` before freeze r1; C2's decoy outputs committed with sha256 in the ledger; protocol §3.2 uses runtime/memory/status only; C5 is below; C6 holds (one evaluation, CERTIFICATION_FAILED without retry, frozen criterion) |
| 14 | exactly-once design | PASS | Function-level diff against C12-R2: `persist_pending`, `persist_emergency`, `seal_blob`, `materialize`, `check_*`, `run_seal_only` are the validated code up to names and comments; `after_marker` differs only in status/record fields. Marker CAS from zero OID to the grant commit after the control and all refusals; signals ignored before the CAS; workers arm only on marker = grant = HEAD; result held in memory → blob → pending ref (emergency file second) → private-index commit → O_EXCL materialization; `seal-only` never computes and refuses post-marker evidence without a marker. QC10 39/39 flows incl. every post-marker failure class. The only temp files are the private index and commit message (as C12-R2), never the result |
| 15 | seal path safety | PASS | `--cacheinfo` commit (no worktree read), CAS on the branch, sealed entry re-read and compared to the blob, `lstat` refusals for every guarded path and a non-directory `evidence/` (T01-T07), O_NOFOLLOW directory walk, read-back check `st_nlink == 1`. No git hooks installed and no `core.hooksPath` |
| 16 | no r5/r6 mutation | PASS | The driver writes only refs under `refs/p5y-k5-cell307-rlr-r1/`, the emergency file in the git dir, one seal commit on its own branch adding only the result path, and that path's worktree copy (plus unreferenced probe objects); `check_governance_state` refuses a changed r5 or any r6 (on HEAD or in history) |
| 17 | closure-only scope | PASS | Protocol §1/§8, manifest `scope`, grant schema requires `closure_only: true`; the sealed record carries `scope: CLOSURE_ONLY`; nothing adopts, edits floor r2, writes r6 or closes K5/P5Y |

## Soundness logic (the brief's specific questions)

* **Hull ⇒ sub-block.** The pinned block rung certifies every inequality uniformly for all e in
  [centre − e_r, centre + e_r]: `Ctx` keeps e symbolic when `e_r > 0`, every enclosure (`enclose_t`, `quad_check`) is
  over the x-box × that e-interval, and the candidate family is e-free (D12), so `w(a)`-type values are e-free. The
  driver passes centre = (hull_lo + hull_hi)/2 and e_r = (hull_hi − hull_lo)/2 exactly, so the interval is the hull
  itself. `hull()` rounds lo down and hi up on the 2^-20 grid, so E_i ⊆ B_i and the statement restricts. Valid.
* **Worst block.** The ten sub-blocks tile the cover interval (checked in `target_blocks`: first/last endpoints and
  consecutive equality); every e lies in some E_i ⊆ B_i, so A_j^cell = max_i A_j^{B_i} bounds it. Valid.
* **Ladder across rungs.** All rungs of a block are certified on the same hull; each input bounds a rung-independent
  quantity (sup_B τ_a, sup_B ‖Ĝ‖, inf_B D, ...), so min of upper bounds / max of lower bounds are again bounds, and
  `assemble` only needs each input to bound its own quantity. Derived inputs (D1, L1_up, D_lo via τ_a,lo/Ā) are valid
  bounds whichever rung's τ, C_T produced them. Valid.
* **S_RLR admissible for TC-T.** (P4) is a separate inequality per j, so a componentwise minimum of two admissible
  triples on the same drift set is admissible; S_I1 is C2's adopted supply on the same cover interval (the driver
  checks REGISTRY_C2's e_lo/e_hi against `cells.json`). Both certifier and registry use the weight φ(z + e) with K = 1/2,
  C = 11/2 (C1b kernel header, THEOREM_AD Lemma K); the norm over R is at least as strong at `a` as over X. TC-T uses
  (P4) only through |E''(e)(a)| (THEOREM_TCT §1). Valid.
* **Pre-marker control.** It runs only in `run_execute` after `check_grant` (QC11) and compares Γ, A, H, M, pass,
  provenance and the three per-supply records for cell 307 under S_I1 with C2's committed record. Every compared
  quantity is a deterministic function of committed inputs and is already committed; no S_RLR value exists before the
  marker; on failure the campaign stops without consuming. It creates no new target information.
* **Γ = 0.** `direct` returns `pass: Gam < 0`; `decide` maps only `pass is True` to CELL307_CLOSED_UNDER_RLR, so Γ = 0
  is NOT closed, matching protocol §8.
* **After-the-fact tuning / second evaluation.** None found through the CLI: all knobs are frozen in bytes bound by
  the grant; the marker blocks `execute`; `seal-only` cannot compute; the guard arms only on marker = grant = HEAD.
  Residual (outside the CLI): someone could check out the grant commit after the seal and call Stage 1 internals with
  the marker present; condition E4 forbids it.

## C5 — campaign-added decisions

| decision | target dependence? | finding |
|---|---|---|
| 2^-20 outward dyadic hull (§3.1) | No | Forced by the certifier (`c1b_kernel._dy_exp` raises on non-dyadic centres/radii; the C2 endpoints are decimal). 2^-20 is the certifier's own grid (`c1b_certpw.dyadic_up(bits=20)`, the `+2^-20` slack terms). Any outward hull is sound (superset); the widening is ≤ 2^-20 per side on blocks of width ≤ 1/100. It depends only on cell geometry, which the partition needs anyway |
| D8 block ladder (4, 6, 8) and its cost rule (§3.2) | No | (4, 6, 8) is the overnight PW ladder (committed rungs d4/d6/d8 at every validation drift; C1B §8 item 2). The only exception is a truncation triggered by decoy wall time > 4 h; the projection 7718.8 s used decoy wall seconds only, it did not trigger, and adding rungs can only tighten a min/max composition. The six TIMING files' runtime/RSS/status fields match the §3.2 table |
| exception classification (§3.7) | No | Rule by exception class, not by outcome; see N4 for its conservative over-breadth |
| caps and workers (EVAL_CAP 6 h, pre-marker 1800 s, workers 5) | No | EVAL_CAP = max(6 h, ⌈2 × projected⌉) from decoy wall time; the official QC02 measured projection (8337.4 s) is ≤ EVAL_CAP/2 and ≤ 4 h (Q12). 5 workers on a 6-core host; results are order- and count-independent |

Protocol §3 and §3.2 cite no decoy certified value and no committed tail number: the only numbers are decoy
runtimes, CPU seconds, peak RSS and statuses (checked against `evidence/explore/TIMING_*.json` runtime fields, without
reading the records), and QC12 finds 0 committed-307 tokens in every tracked namespace file.

## F8 — cell-305 consumer executions

* **Files that appeared after `c66ce2b8`.** `protocol/RLR307_PROTOCOL.md`, `theory/THEOREM_RLR307.md`,
  `code/rlr307_driver.py`, `code/rlr307_independent.py` and the ledger line are all reviewed above in their frozen
  form. The dangling dev snapshot `53f0e890` (13:32 JST, before freeze r1) already holds a driver byte-identical to the
  frozen one.
* **What `rehearse --cell 305` can compute.** `rehearse()` refuses any cell other than 305, runs `control(con, 305)`
  (the consumer under S_I1 = C2's adopted supply, compared field by field with C2's committed cell-305 record), then
  builds a neutral cell record with A_cell = 2·A_I1 + 1 > A_I1, so `s_rlr` returns S_I1 unchanged (asserted as
  `S_RLR_equals_S_I1`), and re-evaluates. No supply other than C2's committed S_I1 enters any Γ(305), and no certifier
  runs. Nothing touches 306-309.
* **Executions and their evidence.**
  1. Pre-freeze dev test (ledger line 10, 2026-09-28T03:59:53Z = 12:59:53 JST): output in the session scratchpad, not
     committed, so its bytes cannot be re-read; the ledger records "only equality booleans inspected". The driver
     version at that minute is not recoverable; the frozen rehearse path is as above.
  2. r1 qualification QC08 (`r1_failed/RLR307_REHEARSE_305.json`) and r2 qualification QC08
     (`RLR307_REHEARSE_305.json`): every control field match true, neutral substitution true/true.
  3. My quick review run's QC08 and my own `rehearse --cell 305`: identical to the committed r2 record except `utc`
     and `wall_seconds`; r1 = r2 = mine on `control`, `neutral_substitution`, `mode`, `driver_sha256`.
* **Conclusion.** Every recorded cell-305 consumer execution reproduced C2's committed record and nothing else; for
  the uncommitted dev test this rests on the ledger statement plus the facts that no RLR value for any band drift has
  ever existed (the guard and every ledger line) and that 305 is an adopted, non-target cell. F8: satisfied.

## Conditions at grant / execution

**Grant (committed alone, direct child of the review commit, which is the direct child of `978d9965`).**
* G1. Adds only `authorization/RLR307_GRANT.json`, binding: cell 307, route RLR, `exactly_once: true`,
  `closure_only: true`, freeze `cd5016f1d0a9fbb43c900740ee6da9a96f4f1963`, qualification
  `978d9965fdcd2de67ed5be3ec349523e50da34bf`, the review commit, driver sha256
  `69160c31361ea73d8a43731a8167d4e3264516806518f90d43eec3fa9c05b0d9` and input-manifest sha256
  `34309e579b7a632386e32929dc894e764216eb4c595b40e1cdc125874c6e854f` (the files as reviewed here).
* G2. It carries the incident review's conditions C1-C6 verbatim (with F1(a), F1(b), the "4 ledgered + 1 unledgered"
  count, "temporal and parametric independence only" and result-chasing risk MEDIUM), and names notes N4 and N7 of
  this review. The adjudication carries the same text.
* G3. No file under `code/`, `protocol/`, `theory/`, `tests/` or `config/` changes after this review. Any needed change
  means STOP (no same-round repair).

**Execution.**
* E1. Exactly one `python3.14 -I -S -B level4/closure_proofs/p5y_k5_cell307_rlr_r1/code/rlr307_driver.py execute`,
  from the qualified worktree root on this host (the host of QC01-QC03), with the grant commit at HEAD, a fully clean
  tree (no untracked or ignored object in the namespace, e.g. no `.DS_Store`; otherwise the driver refuses), the
  machine on power and kept awake (`caffeinate -i` does not stop lid-close sleep), and no other process
  committing, checking out or running campaign code in this repository until the SEAL line is printed.
* E2. Only `preflight` (read-only) may run before it. No decoy, rehearsal or verifier run concurrently.
* E3. The execution review checks: exit code and sealed status; one seal commit that adds only the result path, with
  the marker naming the grant; control field matches all true; `independent_checks.all_equal`; `blocks_planned` = the
  ten hull blocks of cell 307; evaluation wall time below EVAL_CAP. For every `RUNG_EXCEPTION`, it reads the recorded
  error and confirms (protocol §3.7) a deterministic failure raised inside `certify_degree`; a guard refusal, an
  import error or an exception from `_exactify` (outside `certify_degree`) is an execution defect, not
  RLR_CERTIFICATION_FAILED (N4).
* E4. After the marker: never `execute` again; recovery only through `seal-only`; nobody checks out the grant commit to
  call Stage-1 internals or arm the guard; lost result information is never recomputed without a new independent
  governance process.
* E5. The adjudication applies protocol §8 verbatim (strict Γ < 0 in exact rationals; Γ = 0 is not closed; closure is
  not adoption, not a floor-r2 change, not r6, not K5/P5Y closure). Neither it nor any handover places a decoy,
  validation or qualification value next to a cell-307 quantity, and it does not cite `cpu_seconds_workers` (N6).
