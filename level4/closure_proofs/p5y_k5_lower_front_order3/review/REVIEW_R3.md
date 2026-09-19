# Independent pre-freeze review r3 — theorem-TC successor (CUSUM K5 lower front)

Reviewer: fresh context. I did not write the code, review r1 or review r2. Worktree `p5y-k5-lower-front-order3` @
`87c0fd5d`.

**Working-tree changes not in the reviewed commit.** When this review started, the working tree was not clean:
- `code/make_tc_protocol.py` is modified: `OWN` gains `code/tc_prefreeze.py` and `review/ADJUDICATION_BRIEF.md`.
- `code/tc_prefreeze.py`, `review/ADJUDICATION_BRIEF.md` and `checkpoints/CP_002_prefreeze.json` are untracked
  (mtimes 05:40–05:41).

These files will enter the freeze, so I read them too. They are reviewed only as far as N-R3-5 says. Nothing else was
touched.

## Method

Read in full:
- `review/REVIEW_BRIEF_R1.md`, `REVIEW_R2.md`, `REVIEW_R2_DISPOSITION.md`, `REVIEW_R1_DISPOSITION.md`,
  `AUTHORIZATION_BRIEF.md`, `ADJUDICATION_BRIEF.md` (working tree);
- `TC_SUCCESSOR_SPEC.md`, `theorem/THEOREM_TC.md`;
- `code/tc_consume.py`, `tc_producer.py`, `tc_qualify.py`, `tc_lifecycle_sim.py`, `tc_run.py`, `make_tc_protocol.py`
  (both versions), `tc_rule.py`, `tc_crosscheck.py`, `checkpoint.py`, `tc_prefreeze.py`;
- `evidence/dev/QUALIFICATION_REHEARSAL.json`, `MANUFACTURED_DEV.json` (summary), `TC_PROTOCOL_DRAFT.json`,
  `evidence/forecast_r1/COST_NOTE.md`;
- `git diff 2664bec2 de94e8b3` (the r2 fixes) and `git show 87c0fd5d`.

Frozen code read where the new checks depend on it:
- `cusum_order3.py` (Order3Certifier, `_candidates_rung3`, `certify_real_cell`);
- `aux_collocation.collocation_order3` / `objects_order3`;
- `cusum_layer2.all_residuals`, `aux_certifier.aux_residuals`, `aux_propagate.cell_obligations`;
- Aux5 `manifest_v3.verify` / `_gate`, `runtime_identity5.contract` / `compare` / `backend_libraries`;
- `k5_minimality.rat`, `spec` (cells source).

Run locally. Everything was pure Python in the scratchpad. Nothing ran remotely, no CUSUM value was computed, and no
repository file was touched except this one.
1. **Rule versus cross-check.** `tc_rule.cell_enclosure` against `tc_crosscheck.enclosure` on 400 fresh random all-m
   records (new seed): **1600 comparisons, 0 mismatches**.
2. **Governance edge cases.** I built a throwaway git repository holding the committed (`87c0fd5d`) `tc_producer.py`,
   `tc_consume.py`, `tc_rule.py` and `tc_crosscheck.py` at their repository-relative paths, with a synthetic protocol.
   The producer gate and the consumer's `load_protocol` / `load_sealed_tc` / `check_binding` ran on it:

   | case | setup | result |
   |---|---|---|
   | A | AUTHORIZATION and GUARD = ALLOW in the **same** commit (S08(l) only covers separate commits) | `require_authorized` passes; the consumer accepts 34/34 |
   | B | first consumption writes `evidence/tc_r1/TC_CONSUMPTION.json`, then a second consumption runs | **refused**: "namespace has uncommitted or untracked changes" |
   | C | a checkpoint (`checkpoints/CP_003.json`) committed after the freeze | **refused**: "namespace changed after the freeze outside …/evidence/tc_r1" (the producer uses the same logic) |
   | D | two ALLOW commits; records alternately bound to either head | **accepted** (2 run heads) |
   | E | ledger: cell 12 STARTed twice with one failed OUTPUT, cell 13 never STARTed | **accepted** |

3. **Temporal integrity via git.**
   - `config/` and `phase_a/` are unchanged since `e89b33f2`.
   - Nothing outside the namespace changed since `7cb01e38`.
   - `evidence/tc_r1/` and `config/TC_PROTOCOL.json` have no history on any ref.
   - `tc_rule.py` sha is `8d402d11…`. `tc_rule`, `tc_crosscheck`, `tc_manufactured` and `theorem/` are unchanged since
     `2664bec2`.

## Summary

Both r2 blockers are resolved in code.

- **B-R2-1: the consumer is now bound to the freeze.**
  - The protocol is read as committed bytes and must equal its bytes at the freeze commit.
  - The namespace must be clean and unchanged since the freeze outside `evidence/tc_r1/`.
  - QUALIFICATION → AUTHORIZATION are bound to this protocol, and AUTHORIZATION is committed once.
  - Every record carries `protocol_sha256`. Its run head must be on the ancestry path from the AUTHORIZATION commit, with
    the bound ALLOW guard and the same AUTHORIZATION.
  - GUARD must be DENY again, and every sealed file is added once.
- **B-R2-2: the qualification pins threads before any numpy import.** S02 requires `K1_THREADS_PINNED`. The dress
  rehearsal shows S02 passing with all four variables equal to "1".

Every r2 NOTE is implemented or explicitly accepted (table below). The mathematics is unchanged since r2 and remains
sound (checks 1–3).

I found **no soundness defect** and **no way to consume a record that the frozen producer did not write under the frozen
protocol**, short of hand-forgery, which no consumer can detect.

What remains is operational robustness of the one-shot run. The frozen stopping rule says any refusal makes the run VOID
and stops Campaign A (`make_tc_protocol.py:138-140`). Several states that are easy to reach make every producer
invocation refuse *before computing anything*, and `tc_run` checks none of them before writing `RUN_START`. The worst is
deterministic: `tc_run --evidence` pointed into the namespace, which the protocol's own `expected_outputs` suggest
(N-R3-1).

The campaign's checkpoint tool writes into the frozen part of the namespace (N-R3-2). Neither `tc_run` nor
`checkpoint.py` can be changed after the freeze, so both must be fixed before it. The fixes are small, and the preflight
can be qualified by S08(l). I therefore rate them load-bearing NOTEs rather than blockers.

## Status of the r2 findings (verified in code)

| r2 | status | evidence |
|---|---|---|
| B-R2-1 | RESOLVED | See the note below the table. Consumer-side gaps that remain are in N-R3-4. |
| B-R2-2 | RESOLVED | `tc_qualify.py:36-39` pins the four thread variables and `K1_THREADS_PINNED` before any import that can load numpy (no import on lines 41–51 loads numpy). S02 records the environment and requires `K1_THREADS_PINNED == "1"` (`:100-101`). Rehearsal: S02 pass, environment all "1", `aux5_manifest_ok` true. |
| N-R2-1 | RESOLVED | See the note below the table. |
| N-R2-2 | RESOLVED | `module_check` (`tc_producer.py:257-277`) runs before (`:299`) and after (`:355-356`) the computation. Frozen set: protocol pins ∪ Aux5 manifest ∪ order-3 manifest, each with a recomputed sha. The real-only path (`_candidates_rung3` → `aux_collocation`) imports no new repository module (`aux_collocation` and `order2` are already loaded by `cusum_order3`), so the "after" check should equal the replay's 40. |
| N-R2-3 | RESOLVED | `published_order3` names `sup.G`; `fields` no longer lists `G_at_a` (`make_tc_protocol.py:117-124`). Authorization brief item 5 updated. |
| N-R2-4 | RESOLVED | Output carries `verified` (`tc_index_sha256`, `governance`, `acceptance`), `freeze_commit`, `crosscheck_comparisons` (`tc_consume.py:356-359, 376-378, 258`). |
| N-R2-5 | MOSTLY | Head ancestry, guard/AUTHORIZATION at the head, GUARD DENY, sealed-once and ledger OUTPUT sha = index sha are implemented. "Exactly one START and one ok OUTPUT per address" is not (case E), and records bound to different ALLOW heads are accepted (case D). See N-R3-4. |
| N-R2-6 | accepted | Disclosed; the tower is protected by the exact cross-check. I agree. |
| N-R2-7 | RESOLVED | S08(i), (j), (k) were added (`tc_qualify.py:285-305`). The docstring lists 20 mutants and every S08 case. |
| N-R2-8 | PARTIAL | See the note below the table. |
| N-R2-9 | RESOLVED | `tc_run` has no `--workers` (`tc_run.py:58`). The gate is inside `compute(mode="real")` (`tc_producer.py:307-311`), before `_import_chain`. |
| N-R2-10 | accepted (operational) | See N-R3-10. |
| N-R2-11 | reworded | The code does not fully match the new wording (N-R3-4). |

**B-R2-1 evidence.**
- `load_protocol` (`tc_consume.py:90-119`):
  - `committed_bytes`;
  - protocol equal to `git show <freeze>:…`;
  - `status --untracked-files=all` empty;
  - `diff freeze HEAD` only under `evidence/tc_r1/`;
  - all pins match;
  - the tc_rule and tc_crosscheck pins are present.
- `governance_context` (`:293-320`):
  - QUALIFIED at the freeze for this sha;
  - AUTHORIZATION bound to the protocol, addresses and qualification sha, and committed once;
  - GUARD = DENY at HEAD;
  - run heads = commits on `a_add..HEAD --ancestry-path` with the bound ALLOW guard and an identical AUTHORIZATION.
- `check_binding` (`:142-160`) compares the protocol sha, freeze, authorization, head ∈ run heads and the guard sha at
  that head.
- The r2 demonstration is refused as S08(l)T1. The committed tampers T2 (index) and T4 (rule) are refused, and so is T3
  (GUARD back to ALLOW). All four pass in the rehearsal.

**N-R2-1 evidence.**
- S06 runs the replay with `--protocol-sha256`, which executes `runtime_checks` (`tc_producer.py:312-319`). S06
  requires `runtime == proto["runtime"]` and a non-zero "after" module count (`tc_qualify.py:171-175`). Rehearsal:
  before and after are both 40.
- S08(l) (`tc_lifecycle_sim.py`) runs, in a clone:
  - `require_authorized` positively and negatively;
  - the non-replay consumer on 34 no-op records (136 cross-check comparisons, rows sha unchanged);
  - four tamper cases.
- All pass in the rehearsal.
- The real-mode branch of `compute` (Order3Certifier plus real `extract`) necessarily stays unexercised before the run
  (N-R3-8).

**N-R2-8 evidence.**
- `expected_outputs` and `seal_rule` now include `repro/` and the ledger.
- The review documents are committed and pinned.
- Not done:
  - this review and its disposition are not in `OWN`;
  - three namespace files are untracked (N-R3-5);
  - the checkpoint tool still writes outside `evidence/tc_r1/` (N-R3-2).

## Checks 1–8 of the brief

1. **Theorem.** Unchanged since r1/r2. I re-checked the P2 Leibniz forms against the rung-3 right-hand side actually
   proposed by `Order3Certifier._candidates_rung3`: `(I−K)G = K'''F + 3K''D + 3K'H + S'''`. That is the bracket in P2 with
   the correct binomial coefficients. The P3 envelope factors and the Taylor factorials also hold: ρ⁴/24, ρ³/6 and ρ²/2
   for the order-3, order-2 and order-1 expansions of φ, φ′ and φ″. So does E″ = Rφ″ + 2(∂R)φ′ + (∂²R)φ. The A0, A1, A2
   pairing matches `rad = A0 p2 + 2A1 p1 + A2 p0`.
2. **Regularity.** Unchanged; I agree with r1.
3. **Enclosure and assembly.** `tc_rule` = `tc_crosscheck` exactly in 1600/1600 fresh random cases. Every rational
   field written by `extract` has the key and shape that `tc_rule` reads (norms, `sup_S0`, `r.*`, `W2` keys `r:j` with
   r + j ≤ 3). `extract` writes only nonnegative mags and ordered intervals, so neither `_nonneg` nor the inverted-interval
   refusal can trigger spuriously.
   Geometry: the producer writes `e0 = F(cell["e0"][0])` from `spec.CELLS`, which is the same file as the adapter's
   `cells.json` (sha `341eb5e9…`). The consumer compares against `rat = e0[0] + e0[1]`. `e0[1]` and `rho[1]` are `0/1`
   for cells 11–44 (checked), so the geometry check cannot refuse spuriously.
4. **Consumer.** The replay gate is unchanged and strong. The freeze binding is now real (see above). Monotonicity is
   enforced. The remaining gaps are exactness items (N-R3-4) and output placement (N-R3-3).
5. **Producer.**
   - The gate precedes every import and computation in mode real, now inside `compute`.
   - Replay proposes no G and writes no scientific field; S06 checks `has_scientific_fields` is false.
   - `identity_gate` is unchanged. It has been exercised on cells 11 and 44 only (N-R3-8).
   - The real path cannot put a G residual into the identity comparison: `all_residuals` uses explicit names, and
     `objects_order3` / `collocation_order3` are pure.
6. **Feasibility gate / temporal integrity.**
   - The gates are unchanged since `e89b33f2`.
   - No real TC value exists: no `tc_r1` history, and the rehearsal has no scientific field.
   - The rehearsal's S07 output shows only the adopted open ranges; the S08(e) no-op is synthetic.
   - COST_NOTE uses replay CPU plus the order-3 producer's own +170 CPU-s note. My check of `collocation_order3`'s loop
     count (13²·400 quadrature steps) is consistent with that.
7. **Mutation coverage.** Unchanged since r2: 48 fixtures, 20/20 mutants. The rehearsal's S04 sha equals
   `MANUFACTURED_DEV.json` (`2bdaaa6d…`), so the suite is deterministic.
   Any single change to `tc_rule` that alters a value on generic inputs is caught at consumption by the exact
   cross-check (1600/1600 agreement). I found no unsound `tc_rule` mutant that survives both.
8. **Pins / provenance.**
   - At `87c0fd5d` the rehearsal gives 78 pins = 22 OWN + 16 predecessors + 41 modules − 1 overlap. With the working-tree
     `OWN` it will be 80.
   - The loaded-module set is checked before and after the computation.
   - Nothing that the producer or consumer executes is left unpinned, apart from what r1 and r2 already accepted: the
     adopted modules' own imports, via the adapter.

## Findings

No BLOCKING findings. Three NOTEs are load-bearing and must be resolved **before the freeze**, because `tc_run.py`,
`checkpoint.py` and the protocol text are frozen with the namespace: N-R3-1, N-R3-2 and N-R3-5.

| id | severity | file:line | finding | required fix |
|---|---|---|---|---|
| N-R3-1 | NOTE (load-bearing; pre-freeze) | `code/tc_run.py:59-68, 24, 38-41`; `code/tc_producer.py:85-86, 106-128`; `code/make_tc_protocol.py:125-129, 138-140` (@87c0fd5d) | **The one-shot run can be voided before any computation by states that `tc_run` never checks.** See "Detail of N-R3-1" below the table. | See "Detail of N-R3-1" below the table. |
| N-R3-2 | NOTE (load-bearing; pre-freeze) | `code/checkpoint.py:45` | **The checkpoint tool writes into the frozen part of the namespace.** `checkpoint.py` always writes `NS/checkpoints/<name>.json`, which is outside `evidence/tc_r1/`. Once the freeze exists:<br>- any committed checkpoint makes every producer invocation refuse (`tc_producer.py:91-94`) and every consumption refuse (case C);<br>- an untracked checkpoint on the run host makes the producer refuse.<br>The campaign writes a checkpoint at every stage: CP_000 and CP_001 were committed, and CP_002 appeared during this review. `checkpoint.py` itself is frozen with the namespace. | Before the freeze, make `checkpoint.py` write under `evidence/tc_r1/checkpoints/` (or outside the repository) whenever `config/TC_PROTOCOL.json` exists. Commit CP_002 before generating the protocol. |
| N-R3-3 | NOTE (new with the B-R2-1 fix) | `code/tc_consume.py:105-106, 380`; `code/make_tc_protocol.py:129` | **A second consumption refuses if the first wrote its output into the namespace.** `load_protocol` refuses any untracked file in the namespace, including under `evidence/tc_r1/`. The protocol names `evidence/tc_r1/TC_CONSUMPTION.json` as the output. If the first consumption writes there, the second one ("twice, byte-identical", spec §8) refuses (case B). This is recoverable, because consumption can be repeated, but it will surprise the operator. | Document that both consumption runs write `--out` outside the checkout; compare the two outputs, then copy and commit one. Alternatively, refuse an `--out` inside the repository, or exempt only that path. |
| N-R3-4 | NOTE | `code/tc_consume.py:343-352, 142-160, 311-317` | **The consumer's exactness checks are weaker than spec §7a and the r2 disposition (N-R2-5, N-R2-11) state.** See "Detail of N-R3-4" below the table. | Before the freeze, if you want the claims to hold:<br>- per address, exactly one START and exactly one OUTPUT line, with `ok` true;<br>- every record's `binding.head` = `TC_INDEX.head` = `RUN_START.head`, or exactly one ALLOW run head;<br>- `RUN_END.index_sha256` = sha(TC_INDEX);<br>- record `schema` = tc-cell.v1 and `runtime_checks.runtime` = `proto["runtime"]`;<br>- optionally, `tc_run` refuses to start when a fixed-path run marker outside the checkout exists.<br>Otherwise, reword spec §7a and the disposition. |
| N-R3-5 | NOTE (load-bearing; pre-freeze) | `code/make_tc_protocol.py:23-31` (working tree); `review/AUTHORIZATION_BRIEF.md:21` | **The reviewed commit is not the freezable commit.** See "Detail of N-R3-5" below the table. | In the published pre-freeze commit:<br>- commit `tc_prefreeze.py`, `ADJUDICATION_BRIEF.md`, CP_002, this review and its disposition;<br>- add `review/REVIEW_R3.md` and the r3 disposition to `OWN`;<br>- extend authorization brief item 4 to r3.<br>Then generate the protocol from a clean checkout of exactly that commit, run `tc_prefreeze.py`, and commit only the protocol and `PREFREEZE_REFUSAL.json`. |
| N-R3-6 | NOTE | `code/tc_producer.py:63-64, 74` | **The producer compares governance files in text mode; the consumer compares bytes.** `committed_json` decodes `git show HEAD:<rel>` as text (universal newlines, locale codec) and re-encodes it as UTF-8. It then compares the result with the raw disk bytes, whereas the consumer compares bytes with bytes. A hand-written AUTHORIZATION or GUARD containing `\r` (or bytes that are not UTF-8) makes the producer refuse ("differs from its committed bytes"), which is VOID. | Read with `capture_output=True` and no `text`, as `tc_consume.committed_bytes` does. This is a one-line change. |
| N-R3-7 | NOTE | `code/tc_run.py:69-79`; `evidence/forecast_r1/COST_NOTE.md` | **Cap headroom has not been measured under the frozen worker count.** With 4 workers, the last launch requires 30c + 4c + 2c ≤ 86 400, so CAP_STOP (which is VOID) binds at a uniform per-cell compute cost of about **2400 CPU-s**. That is 1.52× the forecast 1575 CPU-s. Per-process CPU has been measured only with **2** concurrent processes (COST_NOTE, S06), never with the 4 frozen workers. | Optional: before authorization, measure one batch of 4 concurrent replays (replay mode, no new real value) and record it under `evidence/tc_r1/`. Otherwise, accept the risk explicitly in the authorization. |
| N-R3-8 | NOTE (residual, informational) | `code/tc_producer.py:323-346` | **Parts of the real path run for the first time in the governed run.** The identity gate and `extract` have been exercised on cells 11 and 44 only. `Order3Certifier._candidates_rung3` and the real `extract` have run only in the slot-1 probe (cell 0, through `certify_real_cell`). My reading finds no cell-dependent branch:<br>- `eps_cell` comes from the same `RefinedCellValues` path in the adopted `cell_obligations` for every cell;<br>- the real path adds no lazy repository import;<br>- no G residual enters `cert.residuals`;<br>- float solves are single-threaded and deterministic, so the reproduction should be byte-identical. | None required. A replay of all 34 cells would retire this risk at about 13 CPU-h of K1-only computation. That is optional and not recommended against the budget. |
| N-R3-9 | NOTE (operational) | `code/tc_consume.py:96-99, 305, 312`; `code/tc_producer.py:87-90, 121-123` | **History discipline.** Every record binds the freeze commit and run-head shas, and both sides find the freeze as the oldest add of the protocol. Consumption therefore refuses if any freeze→seal commit is rebased, cherry-picked or squashed, for example when moving these commits onto `p5y-postk1-frontier` (currently `e89b33f2` on origin). A shallow clone also breaks the `--diff-filter=A` lookup and the ancestry checks. | Fast-forward only, full clones. State it in the authorization and seal runbook. |
| N-R3-10 | NOTE (operational; r2 N-R2-10 residual) | Aux5 runtime contract | The run checks the host contract for each cell (libc "2.41", backend library bytes, interpreter path) across roughly 4 h of wall time. Unattended package updates on vultr-02 can change it; project memory records that apt containment was restored after the Aux5 HOST_DRIFT halt. Drift during the run refuses the remaining cells, which is VOID. | Operational: before launch, check that no unattended-upgrade run falls in the run window (no system setting needs to change). Run S02 and the N-R3-1 preflight immediately before `tc_run`. |
| N-R3-11 | NOTE (minor) | `evidence/dev/TC_PROTOCOL_DRAFT.json:81, 248`; `evidence/dev/QUALIFICATION_REHEARSAL.json` | **The dev artifacts are stale or unverifiable.**<br>- The r1-era draft still lists `G_at_a` in `fields` and uses the old `published_order3` text.<br>- The rehearsal ran at dev commit `02d6a93a`, which is not in this repository, and does not record its base code commit (from the pin count, the `de94e8b3` code plus a dev protocol).<br>Neither artifact is evidence for the freeze, but the authorization reviewer will read `evidence/dev/`. | Annotate, for example in the README or a checkpoint: "draft superseded; rehearsal = de94e8b3 code + dev protocol 30922c24, not published". |

### Detail of N-R3-1

**Finding.** Each of the following makes every producer call refuse in `require_authorized` or `runtime_checks`. `tc_run`
then logs RUN_VOID. Under the frozen stopping rule ("any refusal … makes the run VOID … and stops Campaign A
execution"), that ends Campaign A with nothing computed.

- **(a) `--evidence` inside the checkout. Deterministic.**
  - `tc_run` creates `cells/` and `repro/` and appends `RUN_START` to `RUN_LEDGER.jsonl` before launching the first
    producer. That file is untracked in the namespace.
  - `frozen_guard` refuses on any `git status --porcelain` output in the namespace.
  - The protocol's `expected_outputs` literally name `evidence/tc_r1/cells/…`, `RUN_LEDGER.jsonl` and so on, so this
    invocation is the natural one.
- **(b) Any other untracked file in the namespace.** This includes the allowed prefix: `nohup.out`, an uncommitted
  `AUTHORIZATION_REVIEW.md`, or a checkpoint (N-R3-2).
- **(c) Wrong interpreter.** If `tc_run` is started with a python other than the venv python, the children inherit
  `sys.executable` and `runtime_checks` refuses.
- **(d) Hand-written AUTHORIZATION or GUARD that deviates from a schema fixed only in code.** Examples:
  - key names;
  - `addresses` must be the exact int list;
  - QUALIFICATION and AUTHORIZATION must be separate commits, because `q_add == a_add` refuses;
  - `\r` in the file (N-R3-6).

**Required fix.**
1. In `tc_run`, before any write and before `RUN_START`:
   - refuse an evidence directory inside `REPO`;
   - run the producer gate for every address without computing, for example a subprocess
     `python -B -c "import tc_producer as T; T.require_authorized(k, SHA)"` as the S08(l) probe does;
   - check `sys.executable`, `sys.prefix` and the python, numpy, scipy and flint versions against `proto["runtime"]`;
   - check each K1 record file against its pre-registered sha;
   - on any failure, exit without writing a ledger.
2. Add to the protocol's `stopping_rule`: a `tc_run` preflight refusal, where no producer was invoked, nothing was
   computed and no ledger was written, is not a run.
3. Exercise the preflight in S08(l): positively after the ALLOW commit, and negatively with case (a).
4. Put the exact AUTHORIZATION and GUARD schema in the protocol, or ship a frozen writer.
5. Optionally, let `frozen_guard` ignore untracked files under `evidence/tc_r1/`. The governance files are already checked
   one by one via `committed_json`.

### Detail of N-R3-4

**Finding.**
- `load_sealed_tc` counts START lines (34) and collapses OUTPUT lines into a dict where the last line wins. A ledger in
  which cell 12 was started twice, once with a failed OUTPUT, and cell 13 never started is **accepted** (case E).
- `check_binding` accepts records bound to **different** ALLOW heads (case D).
- `TC_INDEX.head`, the `RUN_START` head and the `RUN_END` `index_sha256` are never compared with the records or the
  index.
- The consumer does not re-check the commit order QUALIFICATION → AUTHORIZATION, or GUARD's `addresses` /
  `protocol_sha256`. It relies on the producer for these.

**Impact.** The producer is deterministic, so this cannot be used to select results. It does make the stopping rule
invisible to the consumer: a VOID first run, whose evidence directory lives outside git, followed by a second run at a
later ALLOW head would be consumed.

### Detail of N-R3-5

**Finding.**
- At `87c0fd5d`, `make_tc_protocol.py` has 22 `OWN` entries (the rehearsal's 78 pins). The working tree adds
  `code/tc_prefreeze.py` and `review/ADJUDICATION_BRIEF.md`. Both are untracked, and so is
  `checkpoints/CP_002_prefreeze.json`.
- I read the two new files:
  - `tc_prefreeze.py` exercises the pre-freeze refusal correctly. The producer refuses at `committed_json` ("…
    TC_PROTOCOL.json is not committed"). It has to run on vultr, because `main()` reads the K1 record before the gate. It
    writes `evidence/tc_r1/PREFREEZE_REFUSAL.json`, which the freeze commit must contain.
  - `ADJUDICATION_BRIEF.md` is consistent with the lifecycle. The `SEAL.json` it names is produced by no code.
- This review and any r3 disposition are not in `OWN`.
- Any namespace file committed after the freeze outside `evidence/tc_r1/` voids the run and the consumption.

## Additional task items

1. **The r2 fixes are implemented as claimed.** The only exception is the exactness wording of N-R2-5 and N-R2-11
   (N-R3-4).
2. **New defects introduced by the fixes.** Two:
   - the consumer's untracked-file refusal makes a second consumption refuse when the first wrote into the namespace
     (N-R3-3, recoverable);
   - the stricter ledger claims are not fully enforced (N-R3-4).
   The fixes introduced no path to a spurious refusal *inside* the governed computation. `module_check` "after" should
   pass on the real path, and case A shows the same-commit AUTHORIZATION + GUARD variant works. The spurious-VOID risks
   are all pre-computation environment states that `tc_run` does not preflight (N-R3-1, N-R3-2, N-R3-10).
3. **No remaining way to consume records not produced under the frozen protocol, short of forgery.**
   - A pin-consistent edit of the protocol and rule, committed or not, is refused.
   - Records must bind this protocol sha, the freeze, the committed authorization and an ALLOW head that descends from
     it.
   - `tc_rule` and `tc_crosscheck` are loaded from freeze-bound pins.

## Dev evidence

- **Rehearsal.** All gates S00–S09 are QUALIFIED at a dev freeze. It shows:
  - S02 with the pinned environment;
  - S06 with runtime checks and module counts 40/40;
  - S07 reproducing the adopted open ranges;
  - S08 (a)–(l) all true.

  The pin count (78) matches the committed `OWN` list. It does not verify the working-tree additions (N-R3-5); those
  will first be qualified at the real freeze.
- **Manufactured suite.** Deterministic (same sha in the dev run and the rehearsal).
- **COST_NOTE.** Consistent with the protocol's 16.3 / 24 / 40 / 4. See N-R3-7 for headroom.

VERDICT = PASS_WITH_NOTES
