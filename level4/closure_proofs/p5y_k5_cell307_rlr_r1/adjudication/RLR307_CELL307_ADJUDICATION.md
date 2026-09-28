# Cell-307 scientific adjudication under the frozen RLR campaign (r1)
CELL307_CLOSED_UNDER_RLR

## Decision
The one sealed evaluation satisfies the frozen closure criterion (TARGET_EVALUATED, Stage 1 CERTIFIED, independent checks all equal, exact Γ(5, 307; S_RLR) < 0); under protocol §8 row 1 cell 307 is scientifically closed under RLR (the line-2 token), and nothing more.

## Adjudicator statement
* I am a fresh, independent, read-only adjudicator. I wrote, froze, qualified, reviewed, granted, ran and sealed
  nothing in this campaign. This file is the only file I wrote in the repository. I created no ref and no commit.
* I ran no driver command (not even `preflight`), no certifier and no consumer, on any cell. I recomputed nothing on
  cell 307. My only computation was exact `fractions.Fraction` comparison of strings already in the sealed record and
  in C2's committed record, by my own script `/private/tmp/rlr307_adjudicator_c307/verify.py`, run as
  `python3.14 -I -S -B` (37/37 checks PASS).
* Basis: worktree `/Users/suzhe/ReBaseGuard-c307`, branch `p5y-k5-cell307-rlr-r1`, HEAD `e68f3d64`. The record was
  read from the object store at the seal `b26c64a74d0ed7a7535259fa058f9ab4a39dedd2` (parent = grant
  `5390b06dc92c2580b92d743ca82629473e28ca90`). NS = `level4/closure_proofs/p5y_k5_cell307_rlr_r1`.
* Prior gates read: execution review line 2 EXECUTION_ACCEPTED (`e68f3d64`); qualification review line 2
  QUALIFICATION_ACCEPTED (`c91991c6`); incident-independence review line 2 INCIDENT_AUDIT_ACCEPTED. I gave their
  conclusions no weight in the table below; except where a line cites a review, each check was made on committed bytes.

## Frozen rule applied
* Source: `git show cd5016f1:NS/protocol/RLR307_PROTOCOL.md` §8, and `RLR307_FREEZE.json` `outcome_table` and
  `stage2.closure_criterion` at `cd5016f1`. Both files are byte-identical at HEAD; no file under `code/`,
  `protocol/`, `theory/`, `tests/` or `config/` of NS has changed since `cd5016f1`.
* Criterion (frozen text): "consumer pass: Gamma(5, 307; S_RLR) < 0 in exact rationals (Gamma = 0 is NOT closed)".
* Supply (frozen text): "S_RLR = (A0_I1, min(A1_I1, A1_cell), min(A2_I1, A2_cell))".
* Applied verbatim: strict `<`, no tolerance, no rounding, no margin, no floor change. A Stage-1 certification
  failure would have mapped to not-closed (RLR_CERTIFICATION_FAILED); any post-marker failure status would have
  mapped to the indeterminate outcome. Neither case arose.

## Verification table
| # | item | finding |
|---|---|---|
| 1 | sealed bytes | worktree copy = sealed blob `04161112` = `refs/p5y-k5-cell307-rlr-r1/pending-result`; the seal adds only the result path; no later commit touches it; the self-hash `sha256` field verifies; `target-consumed` → grant `5390b06d`; no emergency file |
| 2 | status and count | `status` TARGET_EVALUATED; `target_evaluated` true; `target_evaluations` 1; cell 307, m 5, route RLR, scope CLOSURE_ONLY; record binds freeze `cd5016f1` and grant `5390b06d` |
| 3 | control | `field_matches` 7/7 true, `reproduces_C2_exactly` true. My own read of the committed `C2_D5_FORECAST.json` (sha256 = pin `784f25ee…`) cell-307 entry: `A_exact`, `Gamma_exact`, `H_exact`, `M_after_exact`, `pass`, `provenance` equal the control's fields as exact strings |
| 4 | Stage 1 | cell status CERTIFIED; 10/10 blocks CERTIFIED; certified degrees (4, 6, 8) on every block; 30 rungs, one per (block, degree), all `RUNG_RETURNED` with status CERTIFIED; ladder (4, 6, 8), 5 workers, 2^-20 hull, mode `target` |
| 5 | rung exceptions (N4) | zero `RUNG_EXCEPTION` (the token is absent from the record); no rung log contains an error, refusal, traceback, exception or quarantine token |
| 6 | independent checks | `independent_checks` = {all_equal: true, rungs: 30} |
| 7 | cell maxima | `A{0,1,2}_SUPPLY_max` = componentwise max of the 10 block supplies, exact (3/3) |
| 8 | S_RLR, A0 | A0 = the control's A0, byte-identical string (unchanged) |
| 9 | S_RLR, A1/A2 | A1 = min(control A1, A1_cell) and A2 = min(control A2, A2_cell), exact Fraction equality; both cell maxima are strictly below the control's values, so the recorded provenance (A0 I1, A1 RLR, A2 RLR) is the attaining term; S_RLR ≤ S_I1 componentwise |
| 10 | Γ sign | Γ(5, 307; S_RLR) is an exact rational with positive denominator; Γ ≠ 0 and Γ < 0 by Fraction comparison |
| 11 | `pass` | recorded `pass` = True = (Γ < 0) |
| 12 | mechanical outcome | the frozen table row "TARGET_EVALUATED + pass True" gives the line-2 token; it equals the record's top-level `mechanical_outcome` and `target.decision.mechanical_outcome` |
| 13 | governance state | r5 blob `f978eeb6` identical at HEAD and at `7f45e048`; 0 paths outside NS changed since `7f45e048`; no `K5_COVERAGE_MAP_R6` path in any history; status TARGET_EVALUATED, so the evaluation ended inside EVAL_CAP (a timeout is a failure status) |

## Exact sign derivation
* Γ(5, 307; S_RLR) = `target.stage2.evaluated.Gamma_exact`, an exact string p/q: p is a negative integer beginning
  `-26235827040375104158961…`, q is a positive integer. sha256 of the exact string:
  `5bb5d5ca875b519e3f20572b6ae5c4d8d89ec9c3739bdd52dc9878297a506c04`.
* p < 0 and q > 0, so p/q < 0. Confirmed by `Fraction(Gamma_exact) < 0` True and `Fraction(Gamma_exact) != 0` True.
  Exact bracket: −3071/10^6 < Γ(5, 307; S_RLR) < −3070/10^6 (Γ ≈ −3.0701 × 10^-3). The sign is strict and is read
  from exact integers; no rounding is involved.
* The recorded `pass` is True, equal to (Γ < 0).
* Control (historical reproduction under S_I1 of C2's committed cell-307 record; not a new evaluation): committed
  `Gamma` field 0.033132953404317905; the exact committed string (sha256
  `b732230c871351044633dc6b9a44ea391af9a5736eff012226f5338e0d44a63d`) satisfies 331/10^4 < Γ_ctrl < 332/10^4, with
  committed `pass` False. The control reproduced it exactly.
* The target differs from the control in its supply: A0 is held at the I1 value, and A1, A2 are replaced by the
  smaller certified RLR cell maxima, as the frozen supply rule prescribes.

## Closure is not adoption
* This is a **scientific closure result only**: the frozen RLR supply certifies the K5-B inequality for cell 307
  (CUSUM, m = 5) under C2's frozen consumer.
* It is **not** adoption in r5, **not** adoption under floor r2, **not** r6, **not** K5 closed and **not** P5Y closed.
  It changes no floor, threshold or adoption semantics.
* Any adoption path needs a separate, prospective floor-extension campaign with its own freeze, qualification and
  reviews. This document authorizes nothing.

## Scope
* r5 (`K5_COVERAGE_MAP_R5.json`, blob `f978eeb6`) is unchanged and remains authoritative. No r6 exists or is created.
* Cells 306, 308 and 309 are unchanged. Nothing about them is inferred from this result, and no quantity of any
  other cell or of any other m is stated here.
* The closure inherits the protocol §6 shared surface: the certified rung inputs come from one implementation (the
  pinned certifier) and are not independently re-certified; Γ comes from C2's frozen consumer, which is not
  re-implemented (it is validated by the exact control reproduction). This adjudication re-derived every
  composition layer between them that the table lists; it did not re-certify inputs or recompute Γ.
* Per condition E5, no decoy, validation or qualification value is stated in this file, and the record's
  worker-CPU field (N6) is not cited.

## Incident-review conditions C1-C6 (verbatim)
Quoted verbatim from `NS/review/INCIDENT_INDEPENDENCE_REVIEW.md` (the whole section 4), per qualification-review
condition G2:

<!-- BEGIN VERBATIM QUOTE -->
```text
## 4. Disclosure conditions the campaign must carry

The line-2 verdict holds only with these conditions. Each must be satisfied **before the freeze commit** and carried
verbatim into the protocol, the grant and the adjudication.

* **C1, extended incident disclosure.**
  * Carry L1/L4 and audit §3 as proposed, and add F1(a) and F1(b) by path.
  * State that the overnight count of qualitative proxy exposures is 4 ledgered plus 1 unledgered, uncommitted
    B_307 adjacency of unverifiable content.
  * State that "independent of target outcome" means temporal and parametric independence only. The route, its
    channel and its cell were chosen knowing committed 307 facts. Result-chasing risk stays MEDIUM.
* **C2, decoy probe.**
  * Classify every `evidence/explore/TIMING_*` output as a latent proxy (the amendment-2 R2.3 class).
  * Ledger each run at completion.
  * Commit the outputs, or record their sha256 in the ledger, before the freeze.
  * The protocol may use decoy runtime, memory and status only. No decoy certified value may enter any parameter or
    be placed next to a tail number.
  * Any further decoy must be declared in the protocol and must not lie closer to the band than cell 297's hull.
* **C3, latent-proxy list.** Add `streams/C_308/LR/cusum/PROGRESS.md` to the latent-proxy class, as a stricter-only
  amendment in the campaign namespace. Do not edit the overnight files.
* **C4, briefs.** Disclose that the overnight stream briefs (`SCR/PREAMBLE.md`, the C1a/C1b briefs) are not in the
  committed record. If they still exist, commit them or their hashes before the freeze.
* **C5, qualification scope.** The independent qualification review must check the three campaign-added decisions
  (the 2^-20 hull, the D8 block ladder, the exceptions and caps) for target dependence. That includes confirming
  that no cap or ladder choice cites a decoy certified value or a committed tail number.
* **C6, unchanged mechanics.** One sealed Stage-2 evaluation. The Stage-1 stop rule `CERTIFICATION_FAILED` with no
  retry. No post-result tuning. The closure criterion frozen before the grant.
```
<!-- END VERBATIM QUOTE -->

## Qualification-review notes N4 and N7
Notes **N4** and **N7** of `NS/review/RLR307_QUALIFICATION_REVIEW.md`, quoted verbatim:

<!-- BEGIN VERBATIM QUOTE -->
```text
* **N4 (rung-exception scope is wider than protocol §3.7 says).** `_worker_job` classifies *any* `Exception` raised
  inside `S1.certify_rung` as a scientific non-certificate (RUNG_EXCEPTION). That wrapper also covers `_exactify` and
  the guard, so a `QuarantineRefusal` (a `RuntimeError`) or the interpreter's 4300-digit int-to-str limit (`ValueError`,
  fixed under `-I`) would be recorded as "rung not certified" rather than an execution failure. Neither is reachable in
  the frozen design: `Ctx` calls `guard_drift(e - e_r, e + e_r)`, which equals the armed exact hull pair, and the
  largest numerator/denominator in the committed decoy Stage 1 has 808 digits. The direction of any misclassification
  is conservative (it can only yield NOT_CLOSED, never a closure). Condition E3 makes the execution reviewer check it.
* **N7 (incident conditions carried by reference).** Protocol §11 summarizes the liabilities and points to the audit
  and the independent review; it does not restate C1 verbatim (F1(a), F1(b), "4 ledgered + 1 unledgered", "temporal and
  parametric independence only"). The addendum `audit/INCIDENT_AUDIT_ADDENDUM_R1.md` (committed `7d7e9135`, before the
  freeze) meets C1-C4 and is a governance anchor in the grant-bound manifest `RLR307_FREEZE.json`. Documentation gap
  only; condition G2 closes it in the grant.
```
<!-- END VERBATIM QUOTE -->

## Liabilities assessment
Question: does any disclosed liability affect the validity of this one frozen evaluation? Answer: **no**, for the
reasons below. The liabilities stay disclosed and travel with the result.
* **C1 (motivation, F1(a), F1(b), 4 ledgered + 1 unledgered exposures, result-chasing risk MEDIUM).** These bear on
  *why* this test on this cell was chosen, not on whether its output is true. The outcome is a one-sided rigorous
  inequality from a minimum of sound bounds, fixed before the grant and evaluated once (`target_evaluations` 1,
  one seal, one consumed marker); a motivated choice of which rigorous test to run cannot make a false certificate
  pass. "Independent of target outcome" holds in the temporal and parametric sense only, as C1 requires.
* **C2 (decoy probe).** Per protocol §3.2 and the qualification review, the decoys fed only runtime, memory and
  status into the ladder and cap rule. The rule selected the full D8 ladder (4, 6, 8) with no truncation, and the cap
  governs only whether a timeout occurs (none did); neither can alter a certified number.
* **C3, C4.** C3 is a stricter-only quarantine amendment. C4 (uncommitted overnight briefs) leaves the provenance of
  motivation partly unverifiable but touches no pinned byte: the 6 certifier files hash to the frozen pins (fixed
  before the campaign, per the incident review), and these equal the record's `input_sha256.certifier`.
* **C5.** The three campaign-added decisions were checked for target dependence in the qualification review.
* **C6.** Verified here: one sealed Stage-2 evaluation; the Stage-1 stop rule did not fire (10/10 blocks
  certified, no retry); no post-result tuning (no frozen-directory change since `cd5016f1`); criterion frozen at
  `cd5016f1`, before the grant.
* **N4.** Its over-broad exception class could only turn a failure into not-closed, never into closure. It did not
  arise: 0 `RUNG_EXCEPTION`, 30/30 rungs returned CERTIFIED.
* **N7.** A documentation gap only. The grant carries C1-C6, N4 and N7 verbatim (I compared its text with the
  reviews: equal), and so does this file.
* **Residual scope limitation (not a defect).** The closure is exactly as sound as the pinned certifier and C2's
  frozen consumer (protocol §6). That limitation was frozen and disclosed in advance; it is not a new finding.

Next step under protocol §10: independent adjudication review. If it rejects, STOP.
