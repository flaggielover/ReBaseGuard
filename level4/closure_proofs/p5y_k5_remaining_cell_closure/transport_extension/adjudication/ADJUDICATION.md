# T-EXT independent adjudication

```text
VERDICT = ADOPTED        (37 checks, 37 pass, 0 fail)
```

**What is adopted.** The T-EXT C2 pass set may enter the CUSUM K5 open-cell map: cells 0–10 pass the frozen Theorem
K5-B for every m ∈ {1, 2, 3, 5}.

**What is not claimed.** H3a/K5 is **not** established for any m. These cells stay open:

| m | open before (adopted E6) | open after (T-EXT C2) |
|---|---|---|
| 1 | 1–132 | **11–132** |
| 2 | 1–144 | **11–144** |
| 3 | 1–145 | **11–145** |
| 5 | 1–148, 305–309 | **11–148, 305–309** |

**Object.**
- Repository: `flaggielover/ReBaseGuard`, branch `p5y-postk1-frontier`.
- Freeze: `d91bc7de`.
- Seal: `20dc6b98`, with `TEXT_RESULT` sha256 `cb97cabc…`.
- Consumption: `f6540638`, with `TEXT_CONSUMPTION` `9562eda8…` and `XB` `e656a445…`.
- Protocol: `ffe108e0…`, 55 pins.

Machine-readable form: `ADJUDICATION.json` in this directory.

## 0. Method and independence

**Clones.** I made my own fresh GitHub clones:
- Mac: `…/scratchpad/adj-clone` at `f6540638`.
- vultr-02: `/var/tmp/k5c-adjudication-a1/repo` at `f6540638`.
- vultr-02, detached worktree at the freeze commit: `/var/tmp/k5c-adjudication-a1/freeze` at `d91bc7de`.

**Runs.** On vultr-02 I ran the frozen code from my own worktree with the frozen venv (python-flint 0.9.0, Python 3.12.3):
- `replay` and `evaluate`;
- X-A;
- `consume`;
- X-B;
- the static tests;
- `host_smoke_consume`;
- `text_fixtures`;
- `text_mutants`.

Mutant and smoke temp directories were redirected into my scratch directory.

**Own code.** I wrote, stdlib only:
- `/var/tmp/k5c-adjudication-a1/own/adj_check.py`: a Λ recomputation, a K5-B chain written from `K5_GLOBAL_BRIDGE.md`, a fed-object comparison, and falsification checks against K1;
- `/var/tmp/k5c-adjudication-a1/own/margins.py`.

**Cost.** About 160 CPU-s of frozen-code runs, plus read-only scans. There was no model solve, executor, supervisor or
launch, and no AWS access. I read the K1 records only.

**Independence limits.**
- I am a fresh-context, separate process of the same model family (Claude Opus 5), spawned as a subagent by the
  orchestrating session. I am not a human and not a different model family.
- The Mac scratchpad I share with that session already held Phase A analysis files (`an1.py`, `cells_min.json`). I did
  not use them.
- I did not reimplement the frozen tower (`local_r5`, `r5_majorant`, `hermite6_ext`, `graded_dag`). I judged it by a
  rule-by-rule reading, and I re-ran it.
- I read the inherited premises but did not re-prove them: P1a, P1b, K1 record semantics, C_upper drift-monotonicity,
  and Theorem K5-B.

## 1. Temporal integrity

### T01 — Freeze precedes every evaluation: PASS

| event | time (UTC) | source |
|---|---|---|
| freeze commit `d91bc7de` | 19:42:52 | commit date |
| freeze pushed | 19:43:04 | GitHub activity API |
| qualification `RUN_STATE` (head `d91bc7de`) | 19:43:55 | host |
| first `EVALUATE_START` | 19:45:42 | host |

- The tree at `d91bc7de` contains no evidence files.
- The vultr-02 clock and GitHub's `Date` header agree to within seconds.

### T02 — The ledger shows only freeze-head evaluations: PASS

`EVAL_LEDGER.jsonl` has exactly two START/OUTPUT pairs:
- both START lines carry head `d91bc7de`, protocol `ffe108e0` and code `273a682a`;
- both OUTPUT lines carry sha `cb97cabc`;
- the evaluations ran 19:45:42–19:45:45 and 19:46:26–19:46:29.

The host evidence directory `/root/work/k5c-text-evidence/r1` has mtimes from 19:43:55 to 19:46:29.

### T03 — TEXT_RESULT sealed before consumption: PASS

1. `20dc6b98` commits `TEXT_RESULT.json` and the ledger. It contains no `consumption_r1` files. It was pushed at 19:49:58.
2. The host consumption outputs were written after the push: `TEXT_CONSUMPTION.json` at 19:50:15 and `XB.json` at 19:50:16.
3. `f6540638` was pushed at 19:51:02.

### T04 — Commit and push order: PASS

- Pushes: `84299314→d91bc7de→20dc6b98→f6540638`, each a fast-forward.
- Linear single-parent ancestry, checked on the Mac clone.

### T05 — No pre-freeze wide-hull evaluation found: PASS (with a limit)

I scanned 22,381 json/jsonl/log/txt/out files under `/root`, `/var/tmp` and `/tmp` modified between 16:00Z and the freeze.

**Hits:**
- `/var/tmp/k5c-analysis/dev/REPLAY_dev{,2}.json`: η = x1 only, which is allowed. `REPLAY_dev2` is byte-identical to the
  sealed `REPLAY.json`.
- `/var/tmp/text-smoke-zrwlrjvw/PLACEHOLDER_TEXT_RESULT.json` (19:42:00): the smoke placeholder. Every M_n = 10³⁰, and it
  has no scientific content.

**Other pre-freeze files:**
- `extract.py` and `cells_min.json`: a K1 extract.
- The Phase A map builder.
- `horizon.py`: graded-resolvent mode and det from operator constants only. It computes no M_n and no Λ.
- Dev fixtures: manufactured systems only, 0 violations in every dev run, including seed offsets 800000 and 900000.

**TEXT_RESULT-like files.** The only ones on the host are the post-freeze r1 outputs and checkout copies of them.

**`/root/work/k5c-dev`.** Its T-EXT files have mtime 19:41 and are byte-identical to the frozen files. It has no
protocol file, so `evaluate` would refuse there, and it has no `__pycache__`.

**Limit.** A stdout-only run of an earlier draft would leave no trace. Phase C saw drafts dated 19:01. This limit is
governance-only: T-EXT is a deterministic certificate with no adaptation.

### T06 — The pre-freeze guard works: PASS

In my worktree:
- With the protocol modified against HEAD, `evaluate` raises `PRE_FREEZE: … differs from HEAD` and X-A refuses.
- With the protocol untracked, `evaluate` raises `PRE_FREEZE: … is not committed`.

I restored both afterwards; the worktree is clean and the protocol sha is `ffe108e0`.

## 2. Reproduction

| id | check | result |
|---|---|---|
| R01 | 55 pins | 55/55 match, on both the Mac and vultr clones |
| R02 | replay | sha `3446a76e…`, byte-identical. Hull norms equal the sealed ones; M5 relative error 0; trace and L1 within 2⁻¹⁶⁰; mode graded; CRAMER pass |
| R03 | TEXT_RESULT | **sha `cb97cabcc3b5848665584e33ad4207c6d36ce835729725265d585dc8f3ee4f87`, byte-identical**. From `d91bc7de`; 3 s wall; my own ledger |
| R04 | X-A | PASS `[]` on 41 hulls; `XA.json` identical |
| R05 | consumption | sha `9562eda8…`, byte-identical. 310 manifest-bound records; records_sha `76fc2af5` is the E6 set |
| R06 | X-B | PASS `[]`; `XB.json` identical (`e656a445`) |
| R07 | static tests | `ok 4` on the Mac and on vultr |
| R08 | host smoke | C1/C2 equal E6; X-B pass |
| R09 | fixtures | ran 176, wide 170, **0 violations**. Max η·C_e0 19.98; 4 cases ≥ 4; 5 graded with 0 < det ≤ 0.1 (min 0.0211); 12 scalar fallback. Minimum M5 / true max\|R⁽⁵⁾\| is 1.093. Identical to the committed file except `cpu_s` |
| R10 | mutations | 19/19 detected; shams reproduce; identical to the committed file |
| R11 | determinism | 3 evaluations, all `cb97cabc` |

## 3. Mathematics

### M01 — Evenness transport and weights: PASS

**Derivation.** R is odd, so R''' is even and R⁽⁴⁾(0) = 0. Then

```text
R'''(e) = R'''(0) + ∫₀ᵉ (e−t) R⁽⁵⁾(t) dt
```

**Hull bound.** For t ∈ C_j ⊂ [0, x_hi(j)], |R⁽⁵⁾(t)| ≤ M5(x_hi(j)).

**Weights.** The weight is ∫_{C_j∩[0,e]} (e−t) dt.

**Worst point.** d/de of the penalty is Σ_j M5_j·|C_j∩[0,e]| ≥ 0. So the worst point of C_k is X = x_hi(k).

**Own recomputation.** My own code recomputed Λ(k) for k = 1..40 and every m from the TEXT_RESULT M5/M3:
- it matches exactly;
- the weights sum to X²/2 exactly;
- Λ ≥ L_simple everywhere.

### M02 — Tower valid on [0, η]: PASS

Each rule is a valid inequality on the hull:

- **Operator rule.** For the parity-forbidden block, ‖P_x K_i(e) P_y‖ ≤ η·k_{i+1} by the mean value theorem from 0, with
  k = `norm_table(0, η)`.
- **Graded resolvent.** Write Δ = K(e) − K(0).
  - The diagonal block is ≤ η²k₂/2, because P_x K₁(0) P_x = 0.
  - The off-diagonal block is ≤ η·k₁, because K₀(0) commutes with σ.
  - For the nonnegative 2×2 M, 1 − M_xx > 0 and det > 0 imply ρ(M) < 1. So (I−M)⁻¹·diag(C_e0, C_o0) bounds the block
    norms for |e| ≤ η.
  - Each entry is capped by C, which is valid. Otherwise the scalar C applies.
- **`graded_true_sup`.** The wrong-parity part vanishes at 0 and moves by at most η·sup‖X⁽ⁿ⁺¹⁾‖, with
  S0 = `sup_S0_on(n, 0, η)`.
- **Resolvent identity.** The differentiated identity is exact.
- **Local anchoring (a)–(c).** It uses only e = 0 objects plus η × the order-(n+1) tower on the hull.
- **Export.** At the σ-fixed x0 the odd part vanishes.
- **Norm windows.** The `sharp_norms` window [left − 11/2, right + 11/2] is valid for any window.

### M03 — C on the hull: PASS

- C_upper decreases along the cells, so the hull C is C_upper(cell 0) ≈ 1232.84 for every hull.
- C_upper is `drift_monotone_resolvent` evaluated at the cell's smallest |e|.
- The P5X R1 lemma (M2) makes that bound valid for every larger |e|, so it covers the whole hull.

### M04 — The sealed e = 0 anchors do not depend on the hull: PASS

- The executor's point cell is `point_cell(frozen_cell(0), 0)`, with `eta_mid` asserted to be 0.
- The candidate sups and point errors are therefore e = 0 objects.
- Hull 0 reproduces the sealed M5 exactly.

### M05 — Indexing: Λ(k) is fed as L_{k+1}: PASS

- `k5b_literal` reads `cells[i]` as theorem cell i+1.
- `text_consume` sets `cells[k].L = Λ(k)`, with `cover[k].index == k` checked.
- Λ(k) bounds R''' on K1 cell k, which is C_{k+1}.
- My own chain uses the same mapping.
- CM01 (feeding the previous cell's L) is detected.

### M06 — The −M3 floor: PASS

|R'''| ≤ M3(X) on [0, X] ⊇ C_k. The floor is active only for cells 30–40, which are not load-bearing.

### M07 — C2 curvature tightening: PASS

- The bridge needs H_k ⊇ R''(C_k), and M_k ≥ sup_{C_k}|R''| (M_k enters Γ_k).
- M2(x_hi(k)) bounds |R''| on [0, x_hi(k)]. So H' = H ∩ [−M2, M2] and M' = min(M_R2, M2) are still valid inputs.
- No intersection was empty.
- M_R2 ≥ max|H| for all 310 records × 4 m.
- The C2 pass sets equal the C1 pass sets, so the tightening is not load-bearing.

### M08 — The consumed objects are exactly those in TEXT_RESULT: PASS

For both variants and every m:
- `L_used[0]` is the sealed L1;
- `L_used[1..40]` equals Λ(k) from TEXT_RESULT;
- `L_used[41]` is None;
- `H_lo_used` and `M_used` equal max(H.lo, −M2(k)) and min(M_R2, M2(k)).

The consumption is bound to TEXT_RESULT sha `cb97cabc`.

### M09 — My own K5-B chain: PASS

My chain is written from the bridge text. It is neither `k5b_literal` nor X-B.
- It reproduces the E6 open sets.
- It reproduces the claimed C1 and C2 open sets.
- Cells 1–10 pass `via chain`; cell 11 fails.
- U₁₀ is −1.28·10⁻⁵ (m1), −1.00·10⁻⁵ (m2), −1.00·10⁻⁵ (m3) and −7.35·10⁻⁶ (m5).
- For comparison, U₁₁ is +9.0·10⁻⁵ (m1).
- The arithmetic is exact rational, so these small margins do not affect validity.

Λ(k) for cells 1–10 (rounded):

| m | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 1746 | 1673 | 1567 | 1419 | 1205 | 822 | −77 | −2408 | −7716 | −18890 |
| 2 | 1413 | 1351 | 1259 | 1131 | 948 | 627 | −105 | −1974 | −6204 | −15000 |
| 3 | 1263 | 1206 | 1122 | 1005 | 839 | 552 | −91 | −1721 | −5402 | −13000 |
| 5 | 1035 | 985 | 912 | 810 | 665 | 419 | −115 | −1451 | −4457 | −10610 |

Cells 7–10 pass through the accumulated ℓ, not through a positive Λ.

### M10 — Falsification and consistency: PASS (low power)

**Against K1, cells 0–40.** I found no contradiction in any of these comparisons:
- pairwise D-interval differences against M2 and M3;
- the channel-implied lower bound of R'' against H.hi;
- the (U0 + M5) upper bound against H.lo;
- the channel-implied increase of R' against D.

These checks have low power: near 0, the K1 H widths are about 2·10⁴–6·10⁴ and the D widths about 7–17.

**Across orders.** The channel-implied lower bound of R''(x_hi(k)) is ≤ M2(k) everywhere, with minimum relative
slack 0.37 (m1). L0 ≤ M3.

### M11 — Load-bearing regime: PASS

- The claimed consequence depends only on hulls 0–10, because the K5-B chain is causal.
- In hulls 0–10:
  - det lies in [0.940, 0.9995];
  - η·C_e0 lies in [0.24, 2.68];
  - no entry is capped at C.
- 160 fixtures that ran have η·C_e0 in [0.2, 3.0].
- The regimes that fixtures do not cover (the ee cap at hulls 33–40, small det) are not load-bearing.

## 4. Qualification adequacy

### Q01 — Fixtures: PASS

- The fixtures use the unmodified `first_cell_r4.run` on exact-truth manufactured σ-systems at widened hulls.
- Every tower node and anchor is checked, plus Strategy B and M5 ≥ max|R⁽⁵⁾|.
- Every frozen Q03 threshold is met.
- The dev calibration runs used disjoint seeds and also had 0 violations.

### Q02 — Mutations: PASS

19/19 detected. The caveat is in N4.

### Q03 — Replay and determinism: PASS

### Q04 — Sign-blind verdict: PASS

- The verdict uses pass flags only.
- Q04 reads the resolvent mode.
- Q05 reads equality and M_n monotonicity, which is direction-neutral.
- No gate reads Λ.

## 5. Scope and non-amendment

### S01 — The diff touches only the new namespace: PASS

`git diff 84299314..f6540638` lists 40 files. All are additions (`A`), all are under `p5y_k5_remaining_cell_closure/`,
and none is modified, deleted or renamed.

### S02 — Frozen dependencies are unmodified: PASS

| object | hash |
|---|---|
| slot-1 sealed record | `cf90f1ea…` |
| E6 output | file `8b150a51…`, canonical `89017388…` (both last touched at `84299314`) |
| E6 adapter | `fbad7d33` |
| `k5b_check` | `ddd54dc4` |
| `K5_GLOBAL_BRIDGE` | `c1c62346` |

The K1 records were sha-verified against manifest `29ad1f9b` and read only.

### S03 — No new scientific address and no solve: PASS

## 6. Consequence

### C01 — Claimed open sets: CONFIRMED

See the table at the top.

### C02 — H3a/K5 is not established: CONFIRMED

The cells listed above remain open for every m.

## 7. Non-blocking observations

- **N1 — Guard scope.** The `text_transport.py` docstring says any tower with η ≠ x1 is guarded. In the code only
  `evaluate()` and X-A call `require_frozen`, not `tower()`. I found no evidence of misuse.
- **N2 — X-A shares the tower.** X-A calls the same frozen tower code. The tower has no second implementation, and its
  wide-hull validity rests on the rule-wise proof, the premises and the fixtures.
- **N3 — Spec wording.** The spec says no gate reads an M_n value. Q05 monotonicity does read the ordering of M_n, which
  is direction-neutral.
- **N4 — Mutant detection.** Transport mutants are "detected" by output difference. That is a load-bearing-site test,
  not a semantic oracle.
- **N5 — Weak K1 cross-checks.** The K1-based falsification checks have low power.
- **N6 — Drafts not auditable.** The Phase C drafts dated 19:01 were overwritten with the frozen bytes at 19:41. A
  stdout-only run of them cannot be audited. This is governance-only.
- **N7 — C2 adds nothing.** C2 = C1. The M2–M4 values for hulls 11–40 are sealed but not load-bearing here.
- **N8 — Uncommitted producer files.** The producer worktree `/Users/suzhe/ReBaseGuard-k5c` has uncommitted
  interpretation files:
  - `transport_extension/RESULT.md`;
  - `K5_STATUS.md`;
  - `code/k5_coverage_map.py`;
  - `phase_b/PERRON_FLOAT_DIAGNOSTIC.json`;
  - a modified `phase_b/FRONT_BLOCKER.md`.

  They are not adjudicated here. Adoption covers only the objects committed at `f6540638`.
