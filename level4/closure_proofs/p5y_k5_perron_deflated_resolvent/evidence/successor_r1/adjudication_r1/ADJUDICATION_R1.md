# Independent adjudication r1 of the sealed Perron-deflated consumption

```text
SEAL_COMMIT          = 2e9b1585ec6f56b4a347d2aa00287b37cc3e1dd2
FREEZE_COMMIT        = 730d6e8398499f7e5d5da0fb5e494616c65d1e22   (protocol sha256 ef6c1d14…, 42 pins)
QUALIFICATION_COMMIT = 1f5edae9d1ead04e0aaa7461a475288755ad2e28   (QUALIFICATION_RESULT sha256 90446aa6…)
SEALED_RESULT        = evidence/successor_r1/DEFLATED_CONSUMPTION.json sha256 5dcc9b7d26c92babbf1b19ad064b29969ea7bd829ea9629004e312520123274a
ADJUDICATION         = ADOPTED   (18 checks: 17 PASS, 1 informational; 3 non-blocking notes)
ADJUDICATOR          = a separate Claude session with a fresh context, briefed only with review/ADJUDICATION_BRIEF.md
                       (independent by session only: not a human, not a different model family)
UTC                  = 2026-09-19 (≈15:18–17:05)
```

The adjudicator reproduced the evidence rather than trusting it. It worked in its own full-history clones from GitHub,
both at the seal: the Mac scratchpad `adjudication/repo`, and `/root/work/k5p-adjudication` on rebaseguard-vultr-02
(still clean). All outputs went to `/var/tmp/k5p-adj/`. It made no commits or pushes and edited no frozen file. The
outputs are copied byte-for-byte into `vultr/` (`vultr/SHA256SUMS` is the sha256 list computed on the host). The one
exception is `R.json`, the 5.7 MB re-evaluation output, which is recorded by its hash: it equals the sealed result,
5dcc9b7d…. The adjudicator's crude float Markov-chain check is `mac/arl_check.py`.

## Checklist

| # | Check | Verdict | Evidence |
|---|-------|---------|----------|
| 1 | Commit order 5a8c194d → freeze 730d6e83 → 2bbe80a1 → qualification 1f5edae9 → seal 2e9b1585, checked with `git merge-base --is-ancestor` on both hosts; the seal is the tip of `origin/p5y-postk1-frontier` | PASS | `vultr/clone.log`, `mac/clone.log` |
| 2 | Namespace confinement: `git diff --name-only 5a8c194d 2e9b1585` touches 371 files, all inside the namespace. From the freeze to the seal nothing outside `evidence/successor_r1/` changes, both as one diff and commit by commit; the freeze commit adds only the protocol and `PREFREEZE_REFUSAL.json` | PASS | adjudicator git checks |
| 3 | Protocol pins and runtime: protocol sha ef6c1d14 equals the freeze-commit copy; 42/42 pins recomputed on the Mac and on vultr-02; runtime rebaseguard-vultr-02, Python 3.12.3, numpy 2.5.2, python-flint 0.9.0, venv `/root/work/rbg-cusum-aux5-venv` | PASS | adjudicator pin recomputation |
| 4 | Seal integrity: result sha 5dcc9b7d; `SEAL.json` evaluations equal the 2 `EVAL_LEDGER.jsonl` lines (head 1f5edae9, freeze 730d6e83); run1 and run2 stdout identical; both stderr empty | PASS | `SEAL.json`, `eval_r1/` |
| 5 | Qualification: QUALIFIED true, S00.head = 730d6e83, protocol sha ef6c1d14, result sha 90446aa6 | PASS | `QUALIFICATION_RESULT.json` |
| 6 | Seeded Arb sample (`random.Random(int(seal_hash, 16))`): blocks 0, 1, 9 and cells 11, 12, 24, 38, 40, 41, 80, 104, 132, 133, 144, 148, each through its `arl_cell` and `taboo_cell` artifact (27 artifacts); all identical, certified and hash-matching `REGISTRY.json` | PASS | `vultr/SAMPLE_VERIFY.json`, `vultr/sample_verify.py` |
| 7 | Full registry (beyond the brief): `build_registry.py verify --workers 7` over 310 artifacts; hash_mismatch, not_identical and not_certified all empty; registry_reassembled_identical true | PASS | `vultr/full_verify.log` |
| 8 | X-B in full: pass, no flags, 149 cells, max relative deviation 8.77e-8; `XB.json` byte-identical to the qualification's | PASS | `vultr/XB.json` |
| 9 | Falsification gate at GL64 on the sample: pass, planted bugs P1–P6 all flagged; all 300 compared values equal the qualification's `FALSIFY.json` exactly (relative difference 0) | PASS | `vultr/FALSIFY_GL64_sample.json`, `vultr/cmp_falsify.py` |
| 10 | Falsification gate at GL128 (a wrapper rebinds only `GL_N`, `GN`, `GW`; the frozen file is untouched): pass, P1–P6 flagged; max relative difference from GL64 8.08e-13 | PASS | `vultr/FALSIFY_GL128_sample.json`, `vultr/falsify_gl128.py` |
| 11 | Other qualification gates re-run: S04 `QUALIFICATION_AD.json` byte-identical (Q_PASS, MUTATION_PASS); S06 `GATE_RESULT.json` byte-identical (USEFUL at 1.6); S08 prefreeze output at 43c5b56e byte-identical to `PREFREEZE_REFUSAL.json`, and consume refused there; S09 with its own code, 0 violations; S11 in Decimal/scipy, κ₁ = 0.797884560802865… < 0.7978846 and κ₂ = 0.967882898076573… < 0.9678830; S03 verdicts identical (see note 1) | PASS | `vultr/QUALIFICATION_AD.json`, `vultr/GATE_RESULT.json`, `vultr/PREFREEZE.json`, `vultr/PROBE.json` |
| 12 | T-EXT replay: pass ranges and rows sha equal for m = 1, 2, 3, 5; `REPLAY.json` byte-identical to the qualification's; its own-code replay of the C2 consumption also matches | PASS | `vultr/REPLAY.json` |
| 13 | Re-evaluation at head 2e9b1585: `R.json` sha 5dcc9b7d, `cmp`-identical to the sealed result; the ledger line records head 2e9b1585 and freeze 730d6e83 | PASS | `vultr/consume.log`, `vultr/L.jsonl`, `vultr/SHA256SUMS` |
| 14 | Independent re-derivation (`indep.py`, no producer code imported), cells 0–148 for every m, from the raw records, `cells.json`, the registry and TEXT_RESULT: 0 mismatches in exact rationals across all 160 sealed per-cell entries (R, D, H, M) and in A0/A1/A2 and the new radii; its runs of the frozen `k5b_literal` reproduce every sealed pass/open range | PASS | `vultr/INDEP.json`, `vultr/indep.py` |
| 15 | Premise binding: recorded eps_mid[F:r] / (C_upper·(δ_mid + ε_source)) = 1.0000000 on cells 11, 45, 100, 148; D and cell-wide H at 0.9999996–0.9999997 (exact κ₁ = 2φ(0) against the rational upper bound); the Aux5 chain records eps as exactly the zero-radius node values `enclose` uses | PASS | adjudicator audit |
| 16 | Theorem audit: Lemmas K, T, SM, Dv, Dv′ and the AD error identities against ERROR_ALGEBRA §1/§3; the certifier's affine-in-e block check and its d, d′, d″ taboo propagation; Corollary T (F coefficient exactly 1/m, outward rational endpoints, used radius ≥ recorded eps); the T-EXT C2 intersection (mag(H ∩ [−b, b]) = min(mag H, b)); K5-B monotone in tighter valid enclosures | PASS | adjudicator audit |
| 17 | Monotone against coverage map r2 (ec5c3926): r2 passes 188/176/175/167 are a subset of the sealed passes 285/279/278/271; new passes 97/103/103/104 | PASS | `../K5_COVERAGE_MAP_R3.json` |
| 18 | Crude float Markov-chain sanity check (uncertified): E_a[τ] ≈ 444–467 against Ā 500.9 near e ≈ 0.006, ≈ 313–323 against 371.3 at e ≈ 0.115; τ_a ≈ 6.77 (certified 8.15); max Ĝ1 ≈ 15.9 (C_T 19.07); D ≈ 0.0145–0.0152 (D_lo 0.01228), all on the valid side | INFO | `mac/arl_check.py` |

Selected re-derived values:
- **Cell 11:** OPEN for every m (Γ = +2.62e-3, +4.30e-3, +4.19e-3, +4.08e-3).
- **Cell 45:** passes by the direct route (Γ = −4.9e-3, −1.5e-3, −1.1e-3, −3.3e-4).
- **Cells 100 and 148:** pass by the chain route for every m.

## Sealed per-m ranges (verbatim from `DEFLATED_CONSUMPTION.json`)

| m | pass_ranges | pass | open_ranges | open |
|---|---|---|---|---|
| 1 | [[0, 10], [36, 309]] | 285 | [[11, 35]] | 25 |
| 2 | [[0, 10], [42, 309]] | 279 | [[11, 41]] | 31 |
| 3 | [[0, 10], [43, 309]] | 278 | [[11, 42]] | 32 |
| 5 | [[0, 10], [45, 304]] | 271 | [[11, 44], [305, 309]] | 39 |

## Notes (non-blocking) and producer disposition

1. **S03 probe output is not byte-reproducible.**
   - The re-run `PROBE.json` differs from the qualification copy (dc76f68f…). 128 of 441 float-proposal coefficients
     differ by at most 4 units at the 2⁻⁵⁰ scale; the verdicts are identical (correct certifier refused, mutant
     certified, pass true).
   - Disposition: the frozen S03 gate is the probe's exit status. `qualify_successor.py` records `pass = returncode == 0`
     and only records the file's hash. The protocol requires byte identity only of the Arb artifacts (S01), the
     registry, the replay and the two evaluations (S07). This is therefore not a failed identity check. The float
     proposal is an uncertified numpy input to the Arb check, which is what decides.
2. **The spec's S07 row says the ledger shows both evaluations "at the freeze head".**
   - The ledger shows head 1f5edae9 with freeze_commit 730d6e83. That is necessarily so, since `consume` refuses to run
     without a committed QUALIFIED result, which first exists at 1f5edae9.
   - Disposition: a wording slip in a pinned file. It is left unchanged, because the file is frozen.
3. **Status labels in pinned files are stale:** the spec header reads "draft r1 — not frozen" and `THEOREM_AD.md` reads
   "Status: DRAFT r1".
   - Disposition: left unchanged, because the files are frozen. The authoritative status is the protocol pin, together
     with this record.

## Consequence

The sealed consumption is ADOPTED. Coverage map r3 (`../K5_COVERAGE_MAP_R3.json`) composes the adopted map r2 with the
sealed result. The union of open CUSUM cells across m is [[11, 44], [305, 309]] (39 cells), so
K5_COVERAGE_COMPLETE = false and **K5 remains PARTIAL**.
