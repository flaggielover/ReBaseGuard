# C11RD — prospective protocol freeze

The machine-readable freeze is `protocol/C11RD_FREEZE.json`; this page is its human reading. It
was written and committed BEFORE any cell-306 D1/D2 magnitude was computed. The freeze commit is
the commit that adds both files; it is recorded in the handover and must be bound by any later
grant (runner guard R2 compares the freeze file byte-for-byte with the one at that commit).

Entry state: C11R final HEAD `7375b9cd`, branch `p5y-k5-tail-c11rd-d1d2-extension`. N9 OPEN, K5
PARTIAL, r5 authoritative, no r6, no adoption.

## A–B. The statements

For every `e` in cell 306's block `E = [680769/400000, 17885921/10000000]` (= [1.7019225,
1.7885921]):

* **D1**: `|d'_e(a)| <= D1`, **D2**: `|d''_e(a)| <= D2`, upper bounds, where `d_e = Ghat_e h_1`,
  `Ghat_e = (I - Khat_e)^(-1)` on bounded functions on `R`, `Khat_e` the atom-removed kernel
  (density `phi(z + e)` on the alarm-free window `[m - C, C - p]` minus the atom window
  `[m - K, K - p]`), `h_1 = 1 - Phi(C - p + e) + Phi(m - C + e)`, `a = (0, 0)`, `K = 1/2`,
  `C = 11/2`, `' = d/de`.
* Records: kernel `Khat_e`, convention `atom_removed`, direction `UPPER_BOUND`, state set `R` (C11R's
  frozen wording), drift domain exactly `E`, aggregation `max_over_sub_blocks` (4), dependencies
  `C_T_independent`, `tau_independent`, route `independent_derivative_propagation` — the route
  C11R's frozen schema reserved for this work. Equality with C11R's frozen semantics: V19.

## C–E. Target, sub-blocks, state partition

* Target: cell 306 only; block read from C11R's statement table (blob `58b4066f…`), guard R6.
* Sub-blocks: 4 equal closed sub-blocks, exact rationals, tiling `E`:
  `[680769/400000, 17235899/10000000]`, `[17235899/10000000, 17452573/10000000]`,
  `[17452573/10000000, 17669247/10000000]`, `[17669247/10000000, 17885921/10000000]`.
* State cover: bands 0–3 as closed strips in `(s, theta)` (`p = s(1 + theta)/2`,
  `m = s(1 - theta)/2`) split 4 in `s` and 4/8/12/16 in `theta`; band 4 as the two axis segments
  split 4; 168 initial boxes tiling `R` exactly (V22). Refinement: bisection in `(s, theta)` only
  while a residual bound exceeds its tolerance (1/100000, 1/20000, 1/2000), depth at most 2;
  `lam_k` is the maximum over ALL leaves. No box straddles a band line; no box is split in `e`.

## F. The derivative system (theory/D1_D2_DERIVATION.md)

`d = Khat d + h_1`, `d' = Khat d' + Khat' d + h_1'`, `d'' = Khat d'' + 2 Khat' d' + Khat'' d + h_1''`,
`Khat^(i)` with weight `(-1)^i He_i(z + e) phi(z + e)`. Residuals of the e-Taylor candidates
(`h = e - e_c`); Theorem 5: with `n0 = C_T lam0`, `n1 = C_T (lam1 + kappa_1 n0)`:
`D1_j = |D1(a)| + |D2(a)| de + |D3(a)| de^2/2 + tau (lam1 + kappa_1 n0)`,
`D2_j = |D2(a)| + |D3(a)| de + tau (lam2 + 2 kappa_1 n1 + kappa_2 n0)`, `kappa_1 = 2 phi(0)`,
`kappa_2 = 4 phi(1)`. Premise: C11R's ACCEPTED F_H (`Ghat_e 1 <= 3429/500 - (1113/1000) m` on `R`,
whole block), so `C_T = tau = 3429/500` — a DEPENDENCY on an accepted C11R certificate, consumed as a
frozen input, not an independent reproduction and not a recomputation.

## G–I. Backend, rounding, certificate schema

CPython standard library only. Exact rationals everywhere except inside Taylor models (order 6,
three variables, integers at 2^-160, floor rounding with the error added to the remainder, bounds
rounded up). `phi`/`Phi` point values from C7's rational enclosures. The float proposal
(n = 8, 11 x 11 Lobatto nodes per band, 20-point Gauss–Legendre, 52-bit dyadic rounding) is
untrusted. Runs artifact `evidence/runs/C11RD_RUNS.json`, schema `c11rd.runs.v1` (field list in the
JSON), values as exact rational strings.

## J–L. Aggregation, success, agreement

* Aggregation: maximum over the sub-blocks of the per-sub-block bounds; within a sub-block the
  maximum over all leaves; atom bound as the supremum over `h`. Never min, mean or a subset.
* CERTIFIED iff all sub-blocks finish within the caps with R0–R6 passed; no size threshold.
  NOT_CERTIFIED if a cap ends the run (targets INSUFFICIENT). A crash leaves no result and consumes
  the execution.
* Agreement: C11R's factor-2 rule, frozen before any C11R result, unchanged: UPPER_BOUND —
  STRONGER if independent <= original, AGREES if original < independent <= 2 original,
  INSUFFICIENT if independent > 2 original. Statement before number. Exact equality INVALID. N9 is
  reassembled with C11R's accepted C_T, tau, Abar, D_lo classes (read, never recomputed):
  N9_CLOSED iff all six are AGREES or STRONGER; C11R's precedence otherwise.

## Runner guards (docs/C11RD_ARCHITECTURE.md section 4)

R0 pre-import barrier and loaded-module check (`python3 -I -S -B`, exactly the frozen files, no
bytecode, no shadowing), R1 code hashes (and C7's `c7_gaussian.py`), R2 grant (ALLOW, freeze commit, code hashes, cell-306 block,
one execution, host/runtime; freeze file byte-identical at the freeze commit), R3 clean namespace, R4
no lock or runs artifact now or EVER in history, then the exclusive permanent lock, R5 premise, R6
target block.

## M–P. Caps, retry, execution count

Wall 43,200 s (worst case about 7.6 h, docs/C11RD_COST_MODEL.md), 5 workers, resident memory 2 GiB
total. No automatic retry; the lock is taken before any science and never removed; a second
execution only after a host fault that wrote and printed no magnitude, under a new reviewed
authorization. **Exactly one** target execution.

## Q–T. Scope

Cell 306 only. No execution of cells 307–309. No adoption. No coverage-map r6; r5 stays
authoritative; no cell-306 coverage mutation; no automatic K5 or P5Y closure.

## U. Comparison (code/c11rd_compare.py)

U1 seal and review lineage → U2 identity (the comparator's own code and C7 as frozen; the run's
code hashes) → U3 exact recomputation of every bound and the max →
U4 statement equivalence → U5 originals loaded ONLY now (C11R quarantine, blob-bound) and
classified → U6 exact-equality check → U7 post-hoc leak check at the freeze commit → U8 N9
reassembly. The comparison artifact is created exclusively; a refusal before U5 writes nothing.

## V. Reviews

Fresh read-only reviewers for: pre-execution (READY_TO_QUALIFY / NOT_READY), qualification
(QUALIFICATION_ACCEPTED / _REJECTED), authorization (AUTHORIZATION_ACCEPTED / _REJECTED), execution
(EXECUTION_ACCEPTED / _REJECTED), comparison. Each output is read only after its completion
notification and preserved verbatim in its own commit. No target computation while a blocker is
open.

## Forbidden after this freeze

Changing the derivative architecture, the partition, any threshold or tolerance, any safety factor
or the aggregation direction; substituting scalar-drift for block-uniform statements; reading an
original target value in execution logic; rerunning after a valid target execution; starting the
old C11R cell-306 runner in any form; recomputing or replacing C_T, tau, Abar or D_lo.

## Evidence bound by the freeze commit

* Code: the eight `code/c11rd_*.py` files, sha256 in the JSON (`code_sha256`), checked by guard R1.
* Inputs: C11R statement table, sealed runs (F_H), frozen schema, C7 `c7_gaussian`; comparison-only
  inputs (C11R quarantine, C11R comparison) are bound by blob and were not opened by C11RD.
* Documents: statement audit, derivation, architecture, cost model, independence audit, this page,
  calibration (sha256 in JSON).
* Validation: `evidence/validation/C11RD_VALIDATION.json` (23 manufactured tests, run on this code
  and this freeze file).
* Non-target rehearsal of the frozen runner: `evidence/rehearsal/C11RD_REHEARSAL_NT.json`.
