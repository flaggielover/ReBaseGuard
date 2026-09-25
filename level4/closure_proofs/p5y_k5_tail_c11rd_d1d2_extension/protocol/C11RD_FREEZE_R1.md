# C11RD-R1 — successor prospective freeze

The machine-readable successor freeze is `protocol/C11RD_FREEZE_R1.json` (schema `c11rd.freeze.r1`);
this page is its human reading. It was written and committed BEFORE any cell-306 D1/D2 magnitude was
computed. Its commit is the freeze commit any later grant must bind (runner guard R2 compares this
JSON file byte-for-byte at that commit and binds its sha256).

## Predecessor binding and why this successor exists

* Predecessor freeze: `71495747504670dbe90ec0ee2f7dd4702fd47001` (`protocol/C11RD_FREEZE.json`,
  sha256 recorded in the JSON's `successor_of`). It is HISTORICAL and is not rewritten.
* Repair review: `663f8fe7cd20c609850481ee26554aaa3a7589e3` (`review/C11RD_PRE_EXECUTION_REVIEW.md`),
  verdict NOT_READY with one blocker, B-1.
* Reasons: (1) B-1 — the written proof stated the lower-closed band-line convention, under which the
  frozen cover is incomplete on the interior line `s = 4`; the proof now states the UPPER-closed
  convention the cover and code actually certify (theory section 1, Proposition 1), and production
  code implements and checks it. (2) Pre-result hardening of non-blocking notes N-1, N-2, N-3, N-4,
  N-5, N-6, N-9, N-10, N-11, N-12 (docs/C11RD_R1_REPAIR.md; N-7 and N-8 are accepted limitations).
* No scientific parameter changed (section "Unchanged").

## Unchanged (copied verbatim from the predecessor; validation V29 checks equality)

Target cell 306 only; drift block `[680769/400000, 17885921/10000000]`; 4 equal closed sub-blocks
(exact rationals as before); the state cover (168 initial boxes: `s` split 4, `theta` split
4/8/12/16, band-4 axes split 4; bisection in `(s, theta)` only; tolerances 1/100000, 1/20000, 1/2000;
depth 2); the derivative recurrence and the D1/D2 propagation formulas (Theorem 5, `kappa_1 = 2 phi(0)`,
`kappa_2 = 4 phi(1)`, premise C11R F_H with `C_T = tau = 3429/500` as a dependency); Taylor-model
order 6 with 34 moment terms, C7 Gaussian point values, the untrusted float proposal (n = 8, 11 x 11
nodes, q = 20, 52-bit dyadics); rounding policy; certificate schema (with declared bookkeeping
additions); aggregation = maximum; success/failure criterion (plus the declared fail-closed reason
RESOURCE_ACCOUNTING_FAILED); C11R's factor-2 agreement rule and statement-first precedence; the
original-value quarantine; caps 43,200 s wall, 2 GiB resident, 5 workers; no automatic retry;
exactly one execution; no cells 307–309, no adoption, no r6; input bindings (statement table,
C11R sealed runs, C11R schema, C7, and the comparison-only quarantine and C11R comparison, not opened).

## New or clarified in R1

* **Band ownership (E):** band 0 = `s in [0, 1]`, band `k` = `s in (k, k + 1]` (k = 1, 2, 3, axis
  points included), band 4 = axis points with `s in (4, 5]`; `c11rd_certify.owner_band`;
  completeness proved exactly by `c11rd_certify.verify_cover`; runner guard R6 refuses without it.
  The geometry is unchanged.
* **Proof:** theory Proposition 1 (cover and ownership) and the repaired Lemma 4 (endpoints of E and
  of every sub-block: geometric rate on E, the same Neumann series on an open neighbourhood, two-sided
  derivatives at `e_lo`, `e_hi`, closed sub-blocks with `u_e = +-1`).
* **Execution boundary (runner guards R0–R7):** grant at the fixed path `config/C11RD_GRANT.json`,
  bound to the host (hostname, IOPlatformUUID, platform, Python), the canonical worktree (realpath,
  git common dir), the freeze commit and freeze sha256, the code and input hashes, the target
  {306, block, [D1, D2]}, one execution, the qualification commit/artifact/QUALIFICATION_ACCEPTED
  review; plus `--authorization-review-commit` with exactly one AUTHORIZATION_ACCEPTED line and the
  byte-identical grant; lineage freeze <= qualification <= its review <= authorization review <= HEAD.
  No grant exists or is created in this round.
* **History (R4, U0):** one fail-closed reader (`c11rd_model.history_commits`) for the runs artifact,
  the lock and the comparison artifact: all refs and reflogs, full history, replace refs ignored,
  commit-graph not trusted, shallow or grafted history refused.
* **Resources:** memory accounted every 30 s over the live process tree (late and replacement workers
  included); unaccountable -> NOT_CERTIFIED (RESOURCE_ACCOUNTING_FAILED); guard R7 before the lock.
  Load averages at start are recorded.
* **Comparison:** step U0 (run once over history); U7 leak check normalises bare-point and
  scientific-notation renderings. Everything else in U1–U8 is unchanged.
* **Validation:** 29 manufactured tests (`evidence/validation_r1/`), including V24 band-line jumps
  with the reversed-convention negative control, V25 endpoints, V26 execution binding, V27 comparison
  history, V28 live-tree memory, V29 scientific identity. The manifest records a post-write leak scan
  over every file of the namespace.
* **Rehearsal:** the frozen runner on the non-target block (`evidence/rehearsal_r1/`), whose science
  must equal the predecessor rehearsal exactly.

## Forbidden after this freeze

Everything the predecessor forbade (architecture, partition, thresholds, safety factors, aggregation
direction, scalar-drift substitution, reading original values in execution logic, rerunning after a
valid execution, starting the old C11R cell-306 runner, recomputing or replacing C_T, tau, Abar or
D_lo), and additionally any change of the band-ownership convention.

## Reviews

A fresh read-only pre-execution reviewer returns READY_TO_QUALIFY or NOT_READY; its output is read
only after its completion notification and preserved verbatim in its own commit
(`review/C11RD_R1_PRE_EXECUTION_REVIEW.md`). Qualification, authorization, execution and comparison
are later phases, each on explicit instruction and each with its own review.
