# Fresh-context authorization review — theorem-TC successor (CUSUM K5 lower front, cells 11–44)

Reviewer: fresh context. I did not write the successor, the theorem, the protocol or any of the pre-freeze reviews
r1–r3, and I have no stake in the outcome. Brief followed: `review/AUTHORIZATION_BRIEF.md`
(sha256 `486c5099…`, pinned by the protocol). Worktree `/Users/suzhe/ReBaseGuard-k5lf`, HEAD `2be00ddc`
(= `origin/p5y-postk1-frontier`).

Nothing was run on any remote host, no CUSUM computation was run, nothing was committed, and no file was modified.
Everything below was checked locally with `git` and pure `python3`.

## Commits and confinement (verified myself)

| commit | role | verified |
|---|---|---|
| `7cb01e38` | adopted parent (coverage map r3) | ancestor of `2be00ddc`; nothing outside the namespace changed since it |
| `e89b33f2` | gates `config/FEASIBILITY_GATES_A.json` + Phase A blocker map | the only commit that ever touched the gates file; precedes the first forecast commit `38c74494` (02:48 vs 03:39 JST) |
| `73ebd3ef` | pre-freeze state (code, spec, theorem, reviews r1–r3 + dispositions, CP_002) | parent of the freeze |
| `3f540a33` | **FREEZE** | adds **exactly two** files: `config/TC_PROTOCOL.json` and `evidence/tc_r1/PREFREEZE_REFUSAL.json` |
| `2be00ddc` | qualification | adds only `evidence/tc_r1/QUALIFICATION_RESULT.json`, `qualification_r1/*` and `checkpoints/CP_003_frozen.json` (all inside the post-freeze-allowed prefix) |

`git diff --name-status 7cb01e38 2be00ddc` is 54 additions, all under
`level4/closure_proofs/p5y_k5_lower_front_order3/`; there are no modifications or deletions anywhere. Each commit is an
ancestor of the next (`merge-base --is-ancestor`).

## 1. (A) Deterministic reuse is insufficient — SOUND

- The gates (`FEASIBILITY_GATES_A.json`) define the classes, the scenarios, the closure rule (a pair counts as closed
  only if the frozen K5-B `k5b_literal`, `ddd54dc4`, passes it), the selection rule and the stop rule. They have a
  single commit, `e89b33f2`, which precedes every forecast artifact; `no_redefinition` is therefore checkable and holds.
- `ROUTE_FORECAST.json` totals: D 42/5 of 122 (NOMINAL/CONSERVATIVE), G 0/0, H 0/0, TC 122/122. Classes: D MARGINAL,
  G INFEASIBLE, H INFEASIBLE, TC STRONG, exactly as the frozen class definitions produce them from those counts.
- The two zero-new-real routes are the relevant ones for (A): G (midpoint R″ by theorem AD + best certified M3) closes
  **0** pairs; D (deflated order-5 tower) closes 0 with the M5 it would actually have, and only 42/122 under an
  idealised M5 that does not exist (`ROUTE_COMPARISON.md`: the certified M5 at the required hull is 1.7e8 … 8e11× too
  large; even at hull 0 with no growth it is 2.5–4.7× too large). Under the frozen selection rule a route below USEFUL
  is never executed, so neither may be run at all.
- The blocker audit independently supports this: the obstruction is the same predicate pair at every open cell, and the
  whole-cell R″ radius (122–336) is dominated by ρ-terms of the e-constant candidates — which is precisely what one new
  order-3 midpoint candidate per (cell, r) removes.
- I accept the demonstration. The case does not rest on the new object being good: it rests on the certified inputs the
  zero-new-real routes would actually use, and those are two to eleven orders of magnitude short.

## 2. (B)(C) Pre-registration and freeze — SOUND

- `sha256(config/TC_PROTOCOL.json)` = `10ff7e37e9b6e9ad1c39be4f32cceeeb7c413e50319efea4d0c7aa12ca76924f`, identical at
  the freeze commit and in the working tree (recomputed).
- Addresses: `cells` is exactly `[11..44]` (34), `count` 34, m ∈ {1,2,3,5}, midpoint `e0` only, r = 0..4, no other cell,
  order, drift or detector. Producer, runtime (host, venv, python 3.12.3, numpy 2.5.2, scipy 1.18.1, python-flint
  0.9.0), precision 256 bits, 1 thread/process, 4 workers, per-cell field list, expected outputs, the five acceptance
  items, the stopping rule, the seal rule, the governance schema and the 34 K1 record sha256 values are all in the
  frozen protocol.
- **84 pins recomputed by me**: every pin matches byte-for-byte at `3f540a33`, at `2be00ddc`, at `73ebd3ef` and in the
  working tree — 0 mismatches. All 41 `loaded_repository_modules` are a subset of the pins. The pins cover the producer,
  consumer, rule, cross-check, qualification, run, lifecycle-sim and prefreeze code, the theorem, the spec, the gates,
  the forecast, the cost note, **all six review documents plus both briefs**, the adopted predecessors (Perron
  consumption/registry/coverage map/adjudication, T-EXT, slot-1, K5-B, adapter, cells.json, composite export manifest)
  and both frozen producer manifests.
- The freeze commit contains exactly the protocol and the pre-freeze refusal, with the code, spec and reviews already
  committed in its parent and pinned by the protocol — i.e. the r3 disposition's N-R3-5 plan was executed literally.
- The pre-freeze refusal is real and correctly ordered: `PREFREEZE_REFUSAL.json` records mode `real` on cell 11 at head
  `73ebd3ef` with `protocol_tracked: false`, refusal `TCProducerRefusal: … TC_PROTOCOL.json is not committed`, at
  2026-09-19T21:07:42Z, 24 s before the freeze commit (21:08:06Z). The refusal precedes any chain import or record read
  (`compute()` calls `require_authorized` first), so nothing was computed.
- Budget: forecast 16.3 CPU-h; **protocol cap 30 CPU-h**; campaign hard cap 40; workers 4 (no CLI override). See
  Note A below on the 24 vs 30 discrepancy.
- Stopping rule: each address once, plus the pre-registered 2-cell reproduction; no re-run, no extra address, no
  adaptive choice; any producer refusal or failed acceptance item ⇒ VOID, no consumption, Campaign A execution stops; a
  `tc_run` PREFLIGHT refusal (nothing computed, no ledger) is not a run.

## 3. (D) Qualification — PASSED AS THE FROZEN GATES REQUIRE

`QUALIFICATION_RESULT.json`: `QUALIFIED: true`, `protocol_sha256` = `10ff7e37…`, `S00.head` = `S00.freeze_commit` =
`3f540a33…` = the commit that adds the protocol (I checked that this is the only such commit), namespace clean.

I re-evaluated the recorded gate data against the frozen gate definitions in `code/tc_qualify.py`:

- S01 pins 84, mismatch `[]` (≥ 60 required) — and I recomputed all 84 pins myself.
- S02 runtime equals the protocol exactly; thread environment pinned before numpy import (`K1_THREADS_PINNED = 1`, all
  four BLAS variables "1"); order-3 producer manifest problems `[]`; Aux5 `manifest_v3.verify()` ok.
- S03 the 34 K1 records equal both the composite export manifest and the protocol pins.
- S04 manufactured suite: 0 correct-violations, 20/20 mutants detected; its `sha256` equals the committed
  `qualification_r1/MANUFACTURED.json` (`2bdaaa6d…`) and the dev run, so the suite is deterministic.
- S05 `tc_rule` = `tc_crosscheck` on 48 fixtures and 80 synthetic all-m records, 0 mismatches.
- S06 replay of cells 11 and 44: identity gate identical (262 fields each), `has_scientific_fields` false, extraction
  code path complete with non-negative residuals, runtime equal to the protocol, module set 40 before and 40 after.
- S07 consumer replay reproduces the adopted open set `{1:[11,35], 2:[11,41], 3:[11,42], 5:[11,44]+[305,309]}`; its
  sha equals the committed `CONSUMER_REPLAY.json`.
- S08 all 20 refusal cases true, the no-op positive path leaves every pass set unchanged, `check_index` positive control
  accepted, and the full lifecycle simulation (`l_lifecycle_simulation`) passes including the four tamper cases and the
  preflight positive/negative.
- S09 recorded (replay CPU 2795.7 s for the two cells, consistent with COST_NOTE's 1398.97 + 1406.14).

I recomputed the aggregate pass rules of S06, S08 and the overall verdict from the recorded fields: they reproduce
`pass: true` and `QUALIFIED: true`. `SHA256SUMS.host` matches every committed qualification file, and
`QUALIFICATION_RESULT.json` hashes to `f95da15f9cda7688b1a503a83476291d10de5d3523b3d6671987eeb63f7c6c98`.

Trust boundary I cannot close (and must not, per the brief): the qualification ran on `rebaseguard-vultr-02` and its
evidence is self-reported. What I can check — internal consistency, the sha manifest, the gate logic, the freeze
identity, the pin set — is consistent throughout. Every gate is also re-enforced at run time by the producer and again
at consumption, and the adjudicator re-verifies the seal, so a false S0x claim would have to survive three independent
later checks.

## 4. Reviews r1–r3, and the residual risks

- **r1 (NOT_READY)**: B1 (acceptance items 1–3 not checked by frozen code) and B2 (consumer not bound to the protocol)
  are both fixed in `tc_consume.py` — I read `check_index`, `crosscheck`, `rule_modules`, `committed_bytes`. N1–N11 are
  dispositioned; the load-bearing N1 (parallel channel, uncertified order-3 value) is fixed by removing `G_at_a` from
  the record, declaring the channel in the protocol, and binding AUTHORIZATION→QUALIFICATION and GUARD→AUTHORIZATION
  with an enforced commit order.
- **r2 (NOT_READY)**: B-R2-1 (consumer bound to *a* protocol, not *the frozen* one) is fixed — `load_protocol` reads the
  protocol as committed bytes, requires equality with `git show <freeze>:…`, requires the namespace clean and unchanged
  outside `evidence/tc_r1/`, and checks all pins; records carry `protocol_sha256`. B-R2-2 (S02 could not pass because
  numpy was imported before the thread pin) is fixed at the top of `tc_qualify.py` and demonstrably passes in the frozen
  qualification (S02 environment all "1").
- **r3 (PASS_WITH_NOTES)**: no BLOCKING finding; the three load-bearing notes were resolved before the freeze and are
  visible in the frozen code: N-R3-1 `tc_run.preflight` runs before any write (evidence dir outside the checkout and
  non-existent, runtime equality, all 34 K1 record shas, and `require_authorized` for all 34 addresses in a subprocess
  that computes nothing; exit 2 with no directory and no ledger); N-R3-2 `checkpoint.py` writes under
  `evidence/tc_r1/checkpoints/` once the protocol exists (CP_003 is there, confirming it works); N-R3-5 the freeze was
  taken from exactly the published pre-freeze commit. N-R3-3/4/6 are implemented as described (`--out` outside the
  checkout, one START/one ok OUTPUT per address, single run head, no RUN_VOID/CAP_STOP, byte-vs-byte comparison).

Every BLOCKING and every load-bearing finding was resolved **before** the freeze, in the commit that the protocol pins.

### Residual risks — explicit decision

**N-R3-7 (CPU-cap headroom not measured at 4 concurrent workers) — ACCEPTED.**
I re-derived the binding condition from `tc_run` (cap = 30 × 3600 s; last launch reserves `(running+1)·est + 2·est`):
CAP_STOP binds at a uniform ≈ 3000 CPU-s per cell, i.e. 1.9× the measured 1575 CPU-s forecast (measured at 2 concurrent
processes). A 4-way concurrency inflation would have to exceed ~90 % to trip it. A CAP_STOP is VOID, hence fail-closed:
no consumption, no scientific effect. This is a cost/availability risk of at most one wasted run. Accepted.

**N-R3-8 (first real exercise of the order-3 candidate path on cells 11–44) — ACCEPTED.**
Soundness does not depend on the quality of the new candidate: `rung3_residual.g_residual` certifies the residual of
whatever `Ĝ_r` the float layer proposes, and theorem TC charges `f_G = δ_mid(G_r) + ε_mid(src(r,3))` (for r = 0 this
double-counts `reward_allow[3]`, i.e. it is conservative — and it is exactly the charge whose omission the order-3
producer's own undetected mutation R05 would have represented, so the TC consumption is insensitive to that gap in the
order-3 mutation matrix). A bad candidate only widens the enclosure; a wide enclosure fails to close cells, it cannot
close them wrongly. An exception or refusal on the real path is a VOID (fail-closed). The identity gate re-binds every
order 0–2 object of every cell to the sealed K1 record exactly at 256 bits (262 fields), and `module_check` runs before
and after each computation. Accepted.

**N-R3-10 (host drift during a ~4 h run) — ACCEPTED, with an operational condition (C4 below).**
Drift in the Aux5 host contract refuses the remaining cells → VOID → no consumption. Fail-closed, cost only. Note that
`tc_run.preflight` checks the runtime dict but **not** `manifest_v3.verify()` or the order-3 manifest (those live inside
the per-cell `runtime_checks`), so drift produces a VOID rather than a cheap preflight refusal; hence condition C4.
Accepted.

## 5. The parallel channel — ACCEPTED as the governing gate for these 34 addresses

The TC producer calls the frozen `cusum_order3.Order3Certifier` (and `rung3_residual.g_residual`) directly, while the
order-3 producer's own `REAL_CELL_AUTHORIZATION_REGISTRY.json` stays `FROZEN_EMPTY`. I accept this protocol's
authorization as the governing gate, for these reasons:

1. `certify_real_cell` and `rung3_engine.certify_order3` are **not** executed; no signed whole-cell `R‴` interval is
   produced. The registry gates that entry point, whose emptiness is justified in the registry itself by a
   *producer-qualification* problem ("no mechanism permits a real cell to be used for producer qualification while being
   excluded from scientific K5 evidence"). That obstacle does not apply here: this is a scientific use, fully inside
   K5 evidence, under the complete section-5 lifecycle.
2. The governance actually applied is not lighter in substance: gates frozen before any forecast, pre-registration of
   addresses/producer/runtime/pins/fields/outputs/acceptance/budget/stopping rule, a freeze whose identity is a sha256
   over 84 pins, an independent qualification at the freeze commit, three independent pre-freeze reviews, this
   fresh-context authorization, a guard that must be ALLOW for exactly these 34 addresses and DENY again at
   consumption, a one-time seal, and an independent adjudication that must recompute the theorem from scratch.
   Relative to the slot-1 precedent it lacks a launch notice/slot binding and a countersignature; in exchange the
   addresses are exhaustively pre-registered (no slot choice exists to bind), the run is one-shot and fail-closed, and
   the adjudication is stronger.
3. The order-3 producer identity is verified at run time on every call (`producer_manifest_problems()` plus the pinned
   manifest inside `module_check`), so the frozen object is the one that runs.
4. No uncertified order-3 value is recorded: `extract` writes only `delta_G` (a certified residual bound), `sup.G` (the
   certified candidate supremum, needed by Env4) and `abs_G_at_a` (a certified magnitude upper bound). I verified this
   against the code, and against the protocol's `published_order3` text.

Condition C7 below records the one thing this must not be allowed to blur: after the run, the order-3 namespace's
"not executed on any CUSUM cell" wording must not be readable as "no real order-3 candidate was ever computed for cells
11–44".

## 6. Temporal integrity — NO REAL TC VALUE EXISTS

- `evidence/tc_r1/` exists on exactly two commits (`3f540a33`, `2be00ddc`) and contains only the pre-freeze refusal, the
  qualification result, `qualification_r1/*` and CP_003. There is no `TC_CELL_*`, `TC_INDEX.json`, `RUN_LEDGER.jsonl`,
  `TC_CONSUMPTION.json`, `AUTHORIZATION.json` or `GUARD.json` anywhere in the repository.
- `REPLAY_11.json` / `REPLAY_44.json` contain only geometry, the identity-gate report, runtime checks and a shape
  summary (`objects: 5`, `W2: 10`, `rational_fields: 110`, `residuals_nonnegative: true`) — no scientific field, and the
  replay path uses a synthetic `G := Ĥ`, so no order-3 candidate of F was proposed.
- `sim_consume.json` (S08(l)) is built from synthetic no-op records: the TC enclosure at cell 11, m = 1 is
  ±5.0e11 and every pass set is unchanged (`newly_passing` empty for all m; open ranges identical to the adopted ones).
- `CONSUMER_REPLAY.json` is the empty-TC replay: `tc_cells: []`, open ranges equal to the adopted ones.
- `evidence/dev/` holds the superseded draft protocol, the manufactured dev suite and two rehearsals; `evidence/dev/
  README.md` annotates them, and none contains a TC cell value.
- `theorem/`, `phase_a/`, `phase_b/`, `config/FEASIBILITY_GATES_A.json`, `tc_rule.py` and `tc_crosscheck.py` have not
  changed since they were first committed (single-commit histories at `38c74494`/`e89b33f2`), so nothing was tuned after
  seeing a result.

## Independent checks I ran myself

- Recomputed the protocol sha256 and all 84 pins at four tree states (0 mismatches), and the sha256 of every committed
  qualification artifact against `SHA256SUMS.host` (all match).
- `tc_rule.cell_enclosure` vs `tc_crosscheck.enclosure` on 500 fresh random all-m records × 4 m = **2000 comparisons,
  0 mismatches** (independent seed, wide random ranges).
- `tc_rule.coefficients(m)` equals the adopted frozen `assembly.coefficients(m)` source (`F_r`: 1/m for r < m;
  `W_(r,t−r−1)`: 1/t − 1/m) for m ∈ {1,2,3,5}.
- Re-derived theorem TC's premise-to-formula chain against `rung3_residual.TERMS` ((1,0,G),(3,1,H),(3,2,D),(1,3,F),
  source `Sclosed_3` for r = 0 with `reward_allow[3]`), the Taylor factorials (ρ⁴/24, ρ³/6, ρ²/2), the Env4 Leibniz
  expansion with F̃⁗ = 0, and `rad = A0·p2 + 2A1·p1 + A2·p0`. All consistent.
- Read the consumer end to end: the replay gate (rows sha, pass ranges, and per-cell R, D, H, M and `via` for cells
  0–159, per m), the empty-intersection refusal, the monotonicity refusal, the A-constant equality with the adopted
  audit, the cross-check equality per cell and m, the governance context and the sealed-once/ledger checks.

Residual soundness dependence I want on the record: `tc_rule` and `tc_crosscheck` are two implementations of the *same*
theorem text, and the truth-based fixtures do not cover the r ≥ 1 source tower or the W assembly (r1 N7, r2 N-R2-6,
accepted before the freeze). The real backstop is the adjudication brief's item 4 — an independent reimplementation
from `THEOREM_TC.md` by a fresh adjudicator. Condition C6 makes that explicit.

## Conditions of this authorization

None of these requires changing a frozen file; all are inside the frozen lifecycle.

- **C1 — governance files.** `AUTHORIZATION.json` exactly per `governance_schema`: `verdict: "AUTHORIZED"`,
  `protocol_sha256: "10ff7e37e9b6e9ad1c39be4f32cceeeb7c413e50319efea4d0c7aa12ca76924f"`,
  `qualification_result_sha256: "f95da15f9cda7688b1a503a83476291d10de5d3523b3d6671987eeb63f7c6c98"`, `addresses` the
  exact int list `[11,…,44]`, `review: "evidence/tc_r1/AUTHORIZATION_REVIEW.md"`; LF endings, no CR, UTF-8. It must be
  committed in a commit **after and different from** `2be00ddc` (the producer refuses `q_add == a_add`). This review
  file must be committed no later than that commit — an untracked file anywhere in the namespace makes every producer
  call refuse. `GUARD.json`: `state: "ALLOW"`, the same address list, the same protocol sha, and
  `authorization_sha256` = sha256 of the committed `AUTHORIZATION.json`, in the same or a later commit; back to `DENY`
  immediately after the run and before the seal.
- **C2 — scope.** Exactly the 34 pre-registered addresses (CUSUM cells 11–44, cell midpoint only, r = 0..4, orders ≤ 3),
  one evaluation each plus the pre-registered 2-cell reproduction. No other address, no re-run, no adaptive choice, no
  inspection of pass/open before the seal.
- **C3 — invocation.** `tc_run --protocol-sha256 10ff7e37… --evidence DIR` with `DIR` outside the checkout and
  non-existent, run with the frozen venv interpreter, from a full (non-shallow) fast-forwarded clone at the ALLOW
  commit, with a clean namespace (no untracked files, including `nohup.out`). Run `--preflight-only` first; a preflight
  refusal is not a run.
- **C4 — pre-launch host check (because the preflight does not cover it).** Immediately before `tc_run`, read-only and
  computing nothing: confirm `manifest_v3.verify()["ok"]` and `cusum_order3.producer_manifest_problems() == []` in the
  frozen venv, and confirm that no unattended upgrade is scheduled inside the run window (the r3 disposition records
  `apt-daily-upgrade.timer` next firing 2026-09-20 06:41 UTC; forecast wall ≈ 4–4.5 h, so leave ≥ 5 h of margin or wait
  until after it and re-check the contract). If any of these fails, do not launch — that is not a run.
- **C5 — budget.** The authorized cap is the protocol's enforced **30 CPU-h** (see Note A), inside the campaign hard cap
  of 40 with Campaign B's ≈ 3.6 CPU-h. If the actual new-real CPU exceeds the gates' preferred budget of 20 CPU-h, the
  excess must be recorded and justified in the seal and at adjudication.
- **C6 — VOID handling and adjudication.** Any producer refusal, failed acceptance item, CAP_STOP or non-identical
  reproduction ⇒ VOID: no consumption, Campaign A execution stops, and the evidence directory of the void run must be
  preserved and disclosed (not deleted, not reused, not re-run under this protocol). On success: seal first (cells,
  repro, index, ledger committed once, GUARD DENY), then consume twice with `--out` outside the checkout and compare
  byte-identically, then independent adjudication, whose item 4 must be an *independently written* recomputation of
  `H_TC,m(k)` from `THEOREM_TC.md` — not a re-run of `tc_rule`/`tc_crosscheck`.
- **C7 — disclosure of the parallel channel.** The seal and the adjudication must state that the frozen
  `Order3Certifier` was executed on real cells 11–44 under this protocol while the order-3 producer's own registry
  remains `FROZEN_EMPTY`, that `certify_real_cell` and `rung3_engine.certify_order3` were not executed, and that the
  order-3 namespace's "no real CUSUM cell is evaluated" wording refers to that producer's gated entry point only.
- **C8 — scope of any claim.** K5 remains PARTIAL regardless of the outcome: this successor does not touch the m = 5
  tail 305–309, and only the frozen K5-B on the sealed consumption decides pass/open.

## Notes (non-blocking, for the record)

- **Note A — cap discrepancy in the frozen pre-registration.** `TC_SUCCESSOR_SPEC.md` §7, `evidence/forecast_r1/
  COST_NOTE.md` and `review/AUTHORIZATION_BRIEF.md` item 2 all say "protocol cap 24 CPU-h"; the machine-readable,
  enforced `TC_PROTOCOL.json` says `protocol_cap_new_real_cpu_hours: 30`. The change from 24 to 30 is deliberate and
  documented with its rationale in `review/REVIEW_R3_DISPOSITION.md` (N-R3-7, to buy 1.9× headroom against a spurious
  CAP_STOP), but the three prose documents were not updated before the freeze and can no longer be. The binding
  pre-registration is the protocol, so I authorize the enforced 30 CPU-h; the forecast (16.3) is unchanged and remains
  under the gates' preferred budget of 20, and 30 + Campaign B ≈ 3.6 stays under the hard cap of 40. This is a
  documentation defect, not a governance or soundness defect; it must be recorded at adjudication (C5).
- **Note B — `tc_run` does not drain the queue on failure.** After a failed cell the loop keeps launching the remaining
  addresses; the run is only declared VOID at the end. Consequence: a mid-run failure can still spend CPU (inside the
  cap) and produce records that are never consumed. Fail-closed, but it is the reason C6 requires the void evidence to
  be preserved and disclosed.
- **Note C — self-reported qualification.** S00–S09 are the run host's own report; the brief forbids remote checks. I
  verified everything checkable locally (see §3). The producer re-enforces the same gates at run time and the consumer
  and the adjudicator re-verify the seal, so this is an acceptable trust boundary under this campaign's model.
- **Note D — unpinned namespace files.** `code/route_forecast.py`, `code/extract_record_fields.py`,
  `phase_a/LOWER_FRONT_BLOCKER_AUDIT.md`, `phase_a/SHA256SUMS`, `README.md`, `checkpoints/*` and the dev artifacts are
  not in the pin list. None of them executes or is read during the governed run or the consumption, and any change to
  them after the freeze would void the run anyway (the namespace diff check covers the whole namespace). No action.

## Verdict

The section-5 preconditions are met: (A) deterministic reuse is demonstrably insufficient under gates frozen before any
forecast; (B) the addresses, producer, runtime, dependencies, fields, outputs, acceptance, budget and stopping rule are
exhaustively pre-registered; (C) the producer and protocol are frozen, with 84 pins I recomputed and a pre-freeze
refusal exercised before the freeze; (D) the successor is independently qualified at the freeze commit with every
frozen gate passing; (E) this is the fresh-context authorization; and (F) the guard is still DENY and may be switched
to ALLOW only for these exact 34 addresses. The three residual risks are cost/availability risks of a fail-closed VOID
run, not soundness risks, and I accept all three. The parallel order-3 channel is acceptable, governed by this protocol,
subject to condition C7.

AUTHORIZATION_VERDICT = AUTHORIZED
