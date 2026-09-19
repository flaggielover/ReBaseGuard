# Independent pre-freeze review r2 — theorem-TC successor (CUSUM K5 lower front)

Reviewer: fresh context. I did not write the code, and I did not write review r1. Worktree `p5y-k5-lower-front-order3`
@ `2664bec2`, which was clean when the review started.

During the review an untracked file, `review/AUTHORIZATION_BRIEF.md` (mtime 04:39), appeared in the working tree. It is
not part of the reviewed commit. I read it only for its lifecycle implications (N-R2-8).

## Scope and method

Read in full:
- `TC_SUCCESSOR_SPEC.md`, `README.md`, `review/REVIEW_BRIEF_R1.md`, `review/REVIEW_R1.md`, `review/REVIEW_R1_DISPOSITION.md`,
  `theorem/THEOREM_TC.md`;
- every file in `code/` used by the TC chain: `tc_rule`, `tc_crosscheck`, `tc_manufactured`, `tc_producer`, `tc_consume`,
  `tc_run`, `tc_qualify`, `make_tc_protocol`;
- `evidence/dev/MANUFACTURED_DEV.json`, `evidence/dev/TC_PROTOCOL_DRAFT.json`, `evidence/forecast_r1/COST_NOTE.md`;
- `git diff 945dbdb9 2664bec2`.

`theorem/`, `phase_a/`, `phase_b/` and `config/` are unchanged since r1.

Frozen code read where the new checks depend on it:
- `cusum_order3.py` (Order3Certifier, `_candidates_rung3`, `producer_manifest_problems`, `certify_real_cell`);
- `rung3_residual.py`;
- Aux5 `manifest_v3.py`, `runtime_identity5.py`, `tcb5.py`, `ancestry5.py`;
- Aux4 `scipy_guard.py`, `ancestry4.py`;
- `intervals.pin_single_thread`, `cusum_layer2.certify`;
- `deflated_consume.atom_constants_r2` / `block_for`;
- the point executor's `backends.production_gate`, for comparison.

Run locally. All runs were pure Python in the scratchpad; nothing ran remotely, no CUSUM value was computed, and no
repository file was touched except this one:
1. **Rule versus cross-check.** `tc_rule.cell_enclosure` vs `tc_crosscheck.enclosure` on 300 random all-m records
   (random k, j, sup_S0, W, A, rho, centres), m = 1, 2, 3, 5: **0 mismatches in 1200**.
2. **Extra rule mutants.** I ran nine mutants that are not in the frozen harness against the cross-check (E1–E9, listed
   under check 7).
3. **Consumer checks on synthetic inputs.** I ran `tc_consume.check_index` and `check_binding` with synthetic data. A good
   index is accepted. Extra reproduction cells and non-`True` flags are refused. A null binding is refused.
4. **Lifecycle simulation.** I built a throwaway git repository with the real `tc_producer.py` and `tc_consume.py` at
   their repository-relative paths. It carries a synthetic protocol and walks the §8 lifecycle: freeze → QUALIFICATION
   commit → AUTHORIZATION + GUARD ALLOW commit → synthetic records with the exact binding `main()` writes → GUARD DENY →
   seal.
   - `require_authorized` refuses at the freeze and accepts at the authorization commit.
   - `load_sealed_tc` accepts the sealed evidence (34/34).
   - The legitimate lifecycle is therefore not blocked by the new governance code.
   - The same simulation demonstrates B-R2-1.

## Summary

The mathematics is unchanged and remains sound. My structural re-derivation agrees with r1:
- P2's Leibniz forms against `rung3_residual.TERMS`;
- the P3 envelope and the r ≥ 1 tower `h_j = K_e h_{j−1}`, `h_1' = −S_0`.

Most r1 fixes are real code fixes, not prose:
- B1 is resolved.
- N1 is resolved: the producer no longer writes `G_at_a`, and it enforces qualification → authorization → guard
  commit order.
- N2 is resolved: runtime, both manifests, the K1 record sha and the module set are now checked in mode real.
- N3, N4, N6 and N11 are resolved.

Two defects remain that must be fixed before the freeze, because neither can be fixed afterwards:

- **B-R2-1 (residual of r1 B2).** The consumer is bound to *a* protocol, not to *the frozen* protocol. It never compares
  the protocol and code it executes with the freeze commit, and the only link from the sealed records to a protocol is
  `TC_INDEX.json`, which is in the post-freeze-writable prefix.
- **B-R2-2 (new, introduced with the N2 fix).** Qualification gate S02 cannot pass as invoked. `tc_qualify.py` imports
  numpy before the thread environment is pinned, so the Aux5 `manifest_v3.verify()` it now calls fails on
  `thread_environment`. Under "nothing is patched under this protocol", that would spend a freeze.

## Status of the r1 findings (verified in code)

| r1 | status | evidence |
|---|---|---|
| B1 | RESOLVED | See the note below the table. Residual: the output does not record what was verified (N-R2-4). |
| B2 | PARTIAL | See the note below the table. Not resolved: the protocol and code actually executed are not tied to the freeze commit, and records carry no protocol sha (B-R2-1). S08 lacks the requested "wrong tc_rule sha" and "null binding" cases (N-R2-7). |
| N1 | RESOLVED | `G_at_a` removed from `extract` (`tc_producer.py:227`). AUTHORIZATION must carry the committed QUALIFICATION sha, and GUARD the AUTHORIZATION sha (`:112-120`). Order is enforced with `merge-base --is-ancestor` (`:121-128`, simulated). The parallel channel is declared in the protocol. The binding of AUTHORIZATION to the review document, requested in r1, is not implemented (the authorization brief puts the review in `evidence/tc_r1/`; acceptable). Text residue: N-R2-3. |
| N2 | RESOLVED in code | `runtime_checks` (`tc_producer.py:256-287`) covers runtime equality, `producer_manifest_problems`, `manifest_v3.verify`, the pre-registered K1 sha and the module subset. It is never executed before the governed run (N-R2-1), and its S02 counterpart is broken (B-R2-2). |
| N3 | RESOLVED | Protocol `producer.identity_gate` states the 53-bit rule. |
| N4 | RESOLVED | 16.3 / 24 / 4 / 40 agree in the spec, `make_tc_protocol.py:131-133` and COST_NOTE, and `tc_run` defaults the worker count to the protocol's. The CLI can still override it (N-R2-9). |
| N5 | accepted | Disclosed in the disposition only (THEOREM_TC P2 unchanged). Conservative, so no action needed. |
| N6 | RESOLVED | Replay docstring reworded (`tc_producer.py:13-16`). |
| N7 | PARTIAL | SRC0/SRC1/SRC3 were added, and M15–M17 are caught by truth containment. There is still no truth fixture for the r ≥ 1 J-source tower, `j_i`, `sup_S0[0..3]` or the W assembly (N-R2-6). |
| N8 | NOT AS REQUESTED | The module check runs only before the computation; nothing is re-checked after it (N-R2-2). |
| N9 | accepted | — |
| N10 | PARTIAL | The index lists exactly one record per address. Producer invocations are not counted and the ledger is never read (N-R2-11). Harmless: the outputs are deterministic. |
| N11 | RESOLVED | README updated. |

**B1 evidence.**
- `check_index` (`tc_consume.py:105-117`) requires:
  - exactly the protocol addresses in the index and in the loaded cells;
  - reproduction keys exactly {11, 44}, all `True`;
  - reproduction file sha equal to the first-run sha.
- `crosscheck` (`:135-138`) is called for every TC cell and every m (`:208`), with `tc_crosscheck` loaded from the
  protocol pin.
- The evidence is read through `committed_bytes` (`:239-250`).
- S08(f) and S08(h) exercise these refusals.

**B2 evidence.**
- `--protocol-sha256` is required, and the tc_rule and tc_crosscheck pins come from the protocol (`:89-102`).
- The index protocol sha is compared.
- `check_binding` (`:120-132`) checks the freeze commit, the authorization sha, the guard sha (against committed ALLOW
  versions), the run head in the history, and the K1 sha against the protocol.
- S08(g) exercises these refusals.

## Checks 1–8 of the brief

1. **Theorem.** Unchanged since r1. The G residual is `Ĝ − K_0Ĝ − 3K_1Ĥ − 3K_2D̂ − K_3F̂ − Ŝ'''` (TERMS
   (1,0,G), (3,1,H), (3,2,D), (1,3,F)), which matches P2. `certify` returns the residual without storing it, so running
   `g_residual` after `identity_gate` cannot perturb the gate. The P3 Leibniz factors and the Taylor factorials are
   correct.
2. **Regularity.** Unchanged. I agree with r1.
3. **Enclosure and assembly.** The `tc_rule` sha is `8d402d11…`, unchanged, and equal to `rule_sha256` in the dev result.
   The cross-check equality held in 1200 of 1200 random all-m cases. The W coefficients 1/t − 1/m are ≥ 0, so mutant E6
   (abs of c) is equivalent.
4. **Consumer.**
   - The replay gate is unchanged and strong.
   - Acceptance items 1–3 are now enforced.
   - The positive path of the governance code works in the linear §8 lifecycle (simulated).
   - Remaining gap: B-R2-1.
5. **Producer.**
   - In mode real, `main()` runs `require_authorized` before reading the record or importing the chain.
   - Replay proposes no G (ReplayAux3Certifier) and writes only the shape summary.
   - Real mode writes no uncertified G value.
   - `compute(mode="real")` itself has no gate (N-R2-9).
6. **Temporal integrity.**
   - `evidence/tc_r1/` has no history on any ref.
   - `TC_PROTOCOL_DRAFT.json` and `MANUFACTURED_DEV.json` contain no real TC value.
   - All 72 draft pins equal this worktree, so the draft was generated from exactly this state.
   - COST_NOTE uses replay CPU only.
7. **Mutation coverage.** Dev: 48 fixtures, 0 violations, 20/20 mutants detected. Tightness is 0.99996 (SRC0), 0.999996
   (SRC1) and 0.9991 (SRC3), so the order-0, order-1 and order-3 source terms are necessary. My extra mutants:

   | mutant | change | result |
   |---|---|---|
   | E1 | drop ρ·s_G in the k₂ term | detected by cross-check, 160/160 |
   | E2 | ρ³/6 → ρ³/2 in the k₄ term | detected, 160/160 |
   | E3 | σ4(r=0) uses sup_S0[3] | detected, 148/160 |
   | E4 | h₁ tower index shift | detected, 120/160 |
   | E5 | σ4 drops the J₀ term | detected, 120/160 |
   | E7 | ρ⁴/24 → ρ⁴/120 | detected, 160/160 |
   | E8 | centre motion ρ/2 | detected, 160/160 |
   | E6 | abs of c | equivalent mutant (c ≥ 0) |
   | E9 | remove the `_nonneg` refusal | survives, as in r1; harmless on producer output |

   E3–E5, M18, M19 and M20 are caught only by the cross-check (N-R2-6).
8. **Pins and provenance.**
   - The draft has 72 pins and 41 loaded modules.
   - In the real run, `sys.modules` at `runtime_checks` holds the same `_import_chain()` closure. `__main__` is
     `tc_producer.py`, which is listed; the protocol list additionally contains `make_tc_protocol.py`. So the subset test
     should pass.
   - It is checked only before the computation (N-R2-2).

## Findings

| id | severity | file:line | finding | required fix |
|---|---|---|---|---|
| B-R2-1 | BLOCKING | `code/tc_consume.py:89-102, 253-283`; `code/tc_producer.py:131-132`; `TC_SUCCESSOR_SPEC.md:69-72` | **The consumer is still not bound to the frozen protocol (residual of r1 B2).** See "Detail of B-R2-1" below the table. | See "Detail of B-R2-1" below the table. |
| B-R2-2 | BLOCKING | `code/tc_qualify.py:23-43, 73-85`; `../p5y_k1_cusum_aux5_successor/code/runtime_identity5.py:172, 189`; `manifest_v3.py:176` | **S02 cannot pass as the lifecycle invokes it (introduced with the N2 fix).** See "Detail of B-R2-2" below the table. | Put the same pin block as `tc_producer.py:30-33` at the top of `tc_qualify.py`, before anything can import numpy (set the four variables and `K1_THREADS_PINNED`). Have S02 record the variables and require `K1_THREADS_PINNED == "1"`. Alternatively, write the environment prefix into the frozen invocation line, but the in-file pin is the robust fix. |
| N-R2-1 | NOTE (load-bearing for the run) | `code/tc_producer.py:256-294`; `code/tc_consume.py:239-283`; `code/tc_qualify.py:135-155, 165-263` | Several code paths execute for the first time inside the one-shot governed run or its consumption: `runtime_checks` (runtime equality, both manifests, K1 sha, module subset), the positive path of `require_authorized`, and `governance_context` / `committed_bytes` / `load_sealed_tc`. Under the stopping rule, any spurious refusal voids the run and stops Campaign A. My reading and simulation say they pass, but the qualification does not show it. | Let replay mode take the protocol, run `runtime_checks` in S06 (for cells 11 and 44), and require its result. Add an S08 case that builds a throwaway git repository in `--out-dir` and runs `require_authorized` and `load_sealed_tc` positively over the §8 commit sequence, plus the tamper case of B-R2-1 negatively. The scratch simulation for this review is about 150 lines. |
| N-R2-2 | NOTE | `code/tc_producer.py:275-285, 294`; `REVIEW_R1_DISPOSITION.md` N8 | The loaded-module check runs before the computation only. Aux5's own `manifest_v3.py:28-35` documents why the check that authorises the output must come last (a lazy import after the initial gate). Lazily imported modules would be neither pinned nor detected. The disposition says the two producer manifests cover this, but the TC producer never calls a coverage check. | Repeat the subset check (or `tcb5.verify_coverage` over the pinned set) after the computation, before writing. Record the post-compute module count. |
| N-R2-3 | NOTE (load-bearing for the authorization review) | `code/make_tc_protocol.py:115-116, 119-121`; `review/AUTHORIZATION_BRIEF.md` item 5 | The protocol text says the published order-3 information is only δ_mid(G_r) and \|Ĝ_r(a)\|, and the authorization brief repeats this. The record also carries `sup.G`, the certified supremum of the real candidate Ĝ_r, which Env4 needs. The protocol `fields` list still names `G_at_a`, which the producer no longer writes. | List `sup.G` in `published_order3` and in the brief, and remove `G_at_a` from `fields`. |
| N-R2-4 | NOTE | `code/tc_consume.py:228-231, 296` | The consumption output does not record what it verified (r1 B1 asked to "record (a)–(c) in the output"). It omits the TC_INDEX sha (so the output is not bound to the sealed evidence it consumed), the freeze commit, the authorization and guard shas, the run heads and the cross-check count. | Add `tc_index_sha256`, a `governance` block (the ctx) and an `acceptance` block (index, reproduction, cross-check comparisons) to the output. |
| N-R2-5 | NOTE | `code/tc_consume.py:120-132, 253-266` | The binding checks are loose: `head` may be any commit of the history (including pre-freeze commits), the guard may be any ALLOW version ever committed, GUARD = DENY is not required at consumption, and the seal is not checked (cell, repro and index files could be modified in later commits in the allowed prefix; RUN_LEDGER is ignored). | Require that the binding head descends from the AUTHORIZATION add-commit. Require that `git show <head>:…/GUARD.json` and `…/AUTHORIZATION.json` have the bound shas. Require GUARD = DENY at HEAD. Require that each sealed file was added once and never modified. Require that each ledger OUTPUT sha equals the index sha. |
| N-R2-6 | NOTE | `code/tc_manufactured.py:258-261, 317-346` | N7 is partially addressed. The r ≥ 1 σ4 tower (J-structured sources), `j_i`, `sup_S0[0..3]` and the W assembly (m > 1) have no truth fixture. M18–M20 and E3–E5 are caught only by `tc_crosscheck`, written from the same theorem text. The tower is mathematically correct (checked here and in r1), so this is not blocking. The malformed-record refusal fixture was not added. | Optional before the freeze: add a J-source family (S_r = J_e K_e^{r−1}(1 − K_e 1) on the finite chain) and a two-object W truth fixture. |
| N-R2-7 | NOTE | `code/tc_qualify.py:11, 15-18, 190, 208-261` | S08 lacks three cases: the two r1 asked for (tc_rule bytes ≠ protocol pin refused; `binding: null` refused) and a positive control for `check_index`. The docstring is stale: S04 "all 14 mutants" (the code requires 20), S08 lists only (a)–(e), and (e) claims "passes every binding check" although `compose` does not run `check_binding`. The authorization review is told to check the gates "as the frozen gate definitions … require". | Add the three cases and correct the docstring. |
| N-R2-8 | NOTE | `code/tc_producer.py:85-94`; `code/make_tc_protocol.py:23-27, 122-138` | Lifecycle hygiene. After the freeze, any namespace change outside `evidence/tc_r1/`, and any untracked file in the namespace, makes the producer refuse. So `review/AUTHORIZATION_BRIEF.md` (currently untracked), this review and any r2 disposition must be in the freeze commit, and the authorization review output must go to `evidence/tc_r1/`. `expected_outputs` and `seal_rule` omit `repro/TC_CELL_{11,44}.json`, which the consumer requires. | Commit all review documents with the freeze. Add `repro/` to `expected_outputs` and `seal_rule`. Optionally pin the disposition and review r2 in OWN. |
| N-R2-9 | NOTE | `code/tc_run.py:4, 53, 59-60`; `code/tc_producer.py:290-294` | `--workers` can still override the protocol's 4; per COST_NOTE, SMT sharing inflates per-process CPU and hence the cap accounting. `compute(mode="real")` has no gate of its own, so importing `tc_producer` and calling it bypasses `require_authorized`. The frozen `certify_real_cell`, by contrast, puts the gate inside the function. | Refuse a worker count different from the protocol's. Move the gate, or a gate-issued token, into `compute` for mode real. |
| N-R2-10 | NOTE | `../p5y_k1_cusum_aux5_successor/manifests/producer_manifest_v3.json` (runtime) | S02 and `runtime_checks` now depend on the full Aux5 host contract: `platform.libc_ver()` "2.41", OpenBLAS corename, backend library bytes, the uv interpreter path. The Aux5 glibc-successor audit records an unattended libc6 upgrade on vultr-02 (2026-09-14). A patch-level update still reports "2.41", but any contract drift between qualification and the run refuses every cell, which voids the run. | Operational: confirm host containment for the campaign window, and run S02 immediately before the authorization. |
| N-R2-11 | NOTE | `REVIEW_R1_DISPOSITION.md` N10 | "The consumer now enforces exactly-once per address" overstates it: the consumer enforces one indexed record per address, not one producer invocation. | Reword, or check RUN_LEDGER (see N-R2-5). |

### Detail of B-R2-1

**Finding.**
- `load_protocol` reads `config/TC_PROTOCOL.json` from the working tree. `rule_modules` loads `tc_rule.py` and
  `tc_crosscheck.py` from the working tree. Each is checked only for mutual consistency: CLI sha, protocol pins, and the
  index's `protocol_sha256`.
- The consumer computes the freeze commit (`governance_context`), but it never checks:
  - that the protocol equals `git show <freeze>:config/TC_PROTOCOL.json`;
  - that the namespace is unchanged since the freeze outside `evidence/tc_r1/` (the producer's `frozen_guard` does
    this);
  - that the protocol is committed at all;
  - `AUTHORIZATION.json["protocol_sha256"]`.
- The record binding has no protocol sha.

So the only link from the sealed records to a protocol is `TC_INDEX.json`, which is post-freeze writable.

**Demonstration** (throwaway repository, real `tc_consume.py`):
1. After a legitimate seal, I made uncommitted edits to `TC_PROTOCOL.json` (new tc_rule pin) and `tc_rule.py`
   (p_j halved), and committed one change to `TC_INDEX.json` in the allowed prefix.
2. `load_protocol`, `load_sealed_tc` (34/34) and `rule_modules` all accept, and the modified rule is the one executed.
   The cross-check stops this only if `tc_crosscheck.py` is left unmodified; it is pinned by the same working-tree
   protocol.
3. I found no honest-mistake path to this state. It is nevertheless exactly the invariant that spec §7a claims ("the
   consumer is bound to the frozen protocol"), it is the one frozen-side invariant the consumer can verify itself
   (evidence is writable by design), and it cannot be added after the freeze.

**Required fix.** In `tc_consume`:
1. Read the protocol with `committed_bytes`, and refuse unless its bytes equal `git show <freeze>:<PROTOCOL_REL>`.
2. Refuse unless `git diff --name-only <freeze> -- <NS_REL>` (working tree against the freeze) lists only
   `evidence/tc_r1/` paths. Reuse the producer's `frozen_guard` logic.
3. Refuse unless the committed `AUTHORIZATION.json` has `protocol_sha256 ==` the given sha. This binds every record to
   the protocol through the `authorization_sha256` it carries.
4. Recommended: add `protocol_sha256` to the producer binding and check it.
5. Add an S08 case: a pin-consistent working-tree edit of tc_rule and the protocol must be refused.

### Detail of B-R2-2

**Finding.**
- `tc_qualify.py` sets no thread environment. `s02` runs `import numpy` first.
- Then `import tc_producer` and `_import_chain()` both skip their `_PINNED` blocks, because numpy is already in
  `sys.modules`.
- S02 then calls `manifest_v3.verify()`, whose `runtime_identity5.compare` checks `thread_environment` (every
  OMP/OPENBLAS/MKL/NUMEXPR variable) against the committed Aux5 contract, where all four are `"1"`.
- Unless the invoking shell happens to export all four, which no frozen text requires (the lifecycle invocation is
  `python -B tc_qualify.py --protocol-sha256 SHA --out-dir DIR`), `mv["ok"]` is false.
- S02 then fails, QUALIFIED is false, and "nothing is patched under this protocol" forces a re-freeze.

Nothing in the dev evidence ran S02. The real run is not affected, because `tc_producer.py` pins at the top as
`__main__`. The failure is fail-closed, so there is no soundness issue, but it deterministically prevents qualification
of the frozen state.

VERDICT = NOT_READY
