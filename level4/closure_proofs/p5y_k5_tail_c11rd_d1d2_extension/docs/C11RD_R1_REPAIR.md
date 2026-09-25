# C11RD-R1 — pre-result proof-convention and execution-boundary repair

Entry: HEAD `663f8fe7` (the preserved NOT_READY review of freeze `71495747`). No cell-306 D1/D2
magnitude has been computed before or during this round. The predecessor freeze
`protocol/C11RD_FREEZE.json` is historical and unchanged; the successor is
`protocol/C11RD_FREEZE_R1.json` / `.md`.

## 1. B-1 — band-line ownership (the one blocker)

**What was wrong.** `theory/D1_D2_DERIVATION.md` section 1 said a band line `s' = j` belongs to band
`j` (lower-closed). Under that reading the interior line `s = 4` would be owned by a band 4 that
exists only on the axes, and the only boxes containing those points (band 3) use band 2's polynomial
on the middle piece: the frozen cover would not enclose the candidate's residual there.

**What the cover and the code actually certify (derived, not reworded).** The certifier evaluates,
on a closed box of band `k`, the state value with band `k`'s polynomial, the middle piece (image on
`s' = s - 1`) with band `k - 1`'s, and each arm piece with the band of its image segment. Mechanically:

1. every point of R lies in a closed box: `c11rd_certify.verify_cover` proves EXACTLY that the band-`k`
   boxes partition the closed strip `[k, k+1] x [-1, 1]` in `(s, theta)` (k = 0..3) and that the
   band-4 boxes partition `[4, 5]` on each axis (the frozen 168-box cover passes; removing one box
   fails, V24);
2. ownership is UPPER-CLOSED: band 0 = `[0, 1]`, band `k` = `(k, k+1]` (k = 1, 2, 3, axis points
   included), band 4 = axis points with `s in (4, 5]` — `c11rd_certify.owner_band`;
3. the interior lines `s = 1, 2, 3, 4` belong to bands 0, 1, 2, 3 (the band BELOW), axis points on
   the same lines likewise, axis points with `s in (4, 5]` to band 4;
4. the closed-box enclosure holds at the line itself: Taylor models hold for `u in [-1, 1]^3`,
   edges included;
5. no gap: (1) + (2) — every owned point lies in a box of its owner's band (`verify_ownership`);
6. no double-valued candidate: the candidate is the single function `x -> band own(x)'s polynomial`;
   a box of the band above that also contains a line point computes a DIFFERENT quantity there, which
   only enlarges `lam_k` (Proposition 1(c));
7. correspondence: on a box of band `own(x)` the certifier's formula is exactly the candidate's
   residual at `x` (Proposition 1(b)); V24 confirms it numerically through the production owner,
   cover and kernel code with a candidate that JUMPS at every line.

**Repairs.** `theory/D1_D2_DERIVATION.md` section 1: the upper-closed convention and Proposition 1
(statement and proof), replacing the lower-closed paragraph. `code/c11rd_float.py`: docstring and
`nodes` comment describe fitting only (the proposal never assigns ownership); the dead
`Basis.band_of` (lower-closed, never called — V29 shows it had no call site) is removed.
`code/c11rd_certify.py`: `owner_band`, `box_contains`, `owning_boxes`, `verify_cover`,
`verify_ownership` (additions; no existing function changed). Runner guard R6 refuses to start
unless `verify_cover` passes for the frozen cover.

## 2. Other repairs

| note | repair | control |
|---|---|---|
| N-1 | Lemma 4 proof (a) geometric rate `||Khat^N|| <= q^N C_T`, `q = 1 - 1/C_T`, on E; (b) the same Neumann series converges on an OPEN neighbourhood `U = E + (-rho, rho)`, `rho = 1/(4 N kappa_1)`; (c) differentiability on U, so the derivatives at `e_lo`, `e_hi` are two-sided; (d) the closed sub-blocks, `u_e = +-1`, the closed-block premise and pointwise Theorem 5 cover every endpoint | V25 |
| N-2 | V15 judges every invalid claim through the production recomputation `c11rd_compare.recompute` (step U3); the validation-local `verify_claim` is removed | V15 |
| N-6 | the grant is the fixed file `config/C11RD_GRANT.json` and binds host (hostname, IOPlatformUUID, platform, Python), canonical worktree (realpath, git common dir), freeze commit + freeze sha256, code and input hashes, target {306, block, [D1, D2]}, one execution, qualification {commit, artifact blob, QUALIFICATION_ACCEPTED review}; the runner also requires `--authorization-review-commit` holding exactly one AUTHORIZATION_ACCEPTED line and the byte-identical grant, and the lineage freeze <= qualification <= review <= authorization review <= HEAD. No grant is created in this round | V26 (full synthetic lineage accepted; 21 single deviations refused) |
| N-10 | comparator step U0: no comparison artifact on disk AND none in reachable history (`c11rd_model.history_commits`: all refs, reflogs, full history; replace refs ignored; commit-graph not trusted; shallow / grafts / git errors refuse). The runner's R4 uses the same reader | V27 (13 cases) |
| N-11 | `c11rd_runs.process_tree_rss_kb` / `memory_status`: every 30 s (and at pool start) RSS of the parent and ALL live descendants from one process-table snapshot; unreadable or malformed table, or a missing root -> RESOURCE_ACCOUNTING_FAILED; guard R7 checks accountability before the lock | V28 (replacing workers, 40 MB each) |

## 3. Disposition of the review's notes N-1 .. N-12

| note | disposition | detail |
|---|---|---|
| N-1 Lemma 4 endpoints | REPAIRED_NOW | section 2 above; V25 |
| N-2 V15 uses a validation helper | REPAIRED_NOW | production path `c11rd_compare.recompute`; V15 |
| N-3 no band-discontinuous test | REPAIRED_NOW | V24 (jumps at s = 1, 2, 3, 4; reversed convention fails) |
| N-4 float module's lower-closed wording | REPAIRED_NOW | docstring/comment corrected; dead `band_of` removed (no call site; V29) |
| N-5 "Theorem 4" citation | REPAIRED_NOW | `c11rd_certify.py` now cites Theorem 5 |
| N-6 lock/grant not bound to worktree and host | REPAIRED_NOW | section 2; V26 |
| N-7 thin LOW margin vs the 12 h cap | ACCEPTED_LIMITATION | the scientific parameters and the cap are NOT changed (this round's hard boundary). The runner records the load averages at start; the future authorization must require an otherwise idle host and `caffeinate -i` (docs/C11RD_COST_MODEL.md). A cap hit remains NOT_CERTIFIED and consumes the execution |
| N-8 REGISTRY_C2 read for structural facts | ACCEPTED_LIMITATION | disclosed in the audits; the certifier never reads it (V16); the equal tiling cannot use per-sub-row information; later campaigns take structure from the statement table only |
| N-9 U7 matched decimal tokens only | REPAIRED_NOW | U7 and V18 now normalise bare-point and scientific-notation renderings (controls in V18). Residual, accepted: exact rational strings are not value-scanned, because the evidence holds thousands of machine-generated dyadic coefficients and a 4-digit value coincidence would make U7 invalidate an honest run |
| N-10 comparator run-once on disk only | REPAIRED_NOW | step U0; V27 |
| N-11 memory monitor fixed at pool start | REPAIRED_NOW | live process tree; V28 |
| N-12 committed V18 scanned 28 of 31 files | REPAIRED_NOW | the validation manifest now records a post-write leak scan over EVERY file of the namespace, the validation evidence included |

## 4. Scientific identity (V29 and the rehearsal)

Unchanged against `71495747`, checked mechanically by V29: every load-bearing freeze field (target,
drift block, sub-block partition, derivative recurrence, D1/D2 formulas, backend, rounding,
certificate schema, aggregation, success criterion, factor-2 rule, caps, retry, execution count,
scope, input bindings) and every pre-existing function, method and constant of `c11rd_tm`,
`c11rd_kernel`, `c11rd_float`, `c11rd_model`, `c11rd_certify` (syntax trees, docstrings ignored),
except the removed dead `band_of`; `c11rd_runs.certify_block` is identical up to the added
bookkeeping key `resource_accounting`. The successor rehearsal on the non-target block must reproduce
the predecessor rehearsal's science exactly (`evidence/rehearsal_r1/MANIFEST.json`). This round is
therefore NOT docs-only: it adds production functions, guards and a monitor, and removes one dead
method; it changes no scientific parameter, no computation and no cover geometry.
