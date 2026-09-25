# C11RD — implementation architecture

Scope: the independent certifier of the N9 constants D1 and D2 for cell 306 (statements in
`docs/D1_D2_STATEMENT_AUDIT.md`, mathematics in `theory/D1_D2_DERIVATION.md`), the one-execution
runner, the comparator, and the manufactured validation. Nothing here reruns or recomputes C11R's
C_T, tau, Abar or D_lo; C_T and tau enter as the frozen premise of C11R's ACCEPTED F_H certificate.

## 1. Modules (`code/`)

| module | role | trusted for soundness? |
|---|---|---|
| `c11rd_tm.py` | Taylor models in `(u_s, u_theta, u_e)`: integer coefficients scaled by 2^-160, floor rounding with the error added to the remainder; products with truncation + cross remainder; `phi`/`Phi` composition with Lagrange remainder; centred Gaussian moment series (Lemma 6). Point values of `phi`, `Phi` from C7's `c7_gaussian` (rational, proved remainders). | yes |
| `c11rd_model.py` | model constants; blob-bound loaders for C11R's statement table (`58b4066f…`) and sealed runs (`a5351603…`); the F_H premise check; kernel norms `kappa_1 = 2 phi(0)`, `kappa_2 = 4 phi(1)` (upper ends of C7 enclosures); the N9 statement strings. | yes |
| `c11rd_float.py` | UNTRUSTED float proposal: band-piecewise Chebyshev basis, Gauss–Legendre kernel rows, Householder least squares for D0..D3 at the sub-block centre; conversion to EXACT dyadic power-basis candidates. | no — affects tightness only |
| `c11rd_kernel.py` | boxes (one closed band each, refused otherwise), piece structure (Lemma 1) with TM endpoints, all `Khat^(i) D_j` over a box as TMs, the sources `h_1, h_1', h_1''`, the residual TMs `r0, r1, r2`. | yes |
| `c11rd_certify.py` | initial cover (band-aligned; tiles R exactly), `refine_box` (bisection in `(s, theta)` only), `merge` (max of lam, order-free), exact atom bounds, propagation (Theorem 5), sub-block tiling. | yes |
| `c11rd_runs.py` | the runner: `--mode real` (the one target execution, guards R0–R6) and `--mode nontarget` (rehearsal of the same code on the freeze's non-target block). Parallel cover over initial boxes (spawn pool), wall/memory caps, exclusive permanent lock, runs artifact. | yes (orchestration) |
| `c11rd_compare.py` | the comparator, steps U1–U8; the only module that ever loads an original magnitude (step U5). | governance |
| `c11rd_validate.py` | manufactured validation V01–V23. | test |

Import graph of the certifier (`c11rd_runs` and everything it loads): `c11rd_runs → c11rd_certify →
{c11rd_float, c11rd_kernel, c11rd_model, c11rd_tm}`, `c11rd_tm → c7_gaussian` (which imports only
`fractions`). Standard library only: no numpy, flint, mpmath, sympy. No module of the original
load-bearing graph (`taboo_certify`, `resolvent_certificate`, `opnorms`, `ra_certifier`,
`fast_range`, `intervals`, `rebaseguard_certify`, `rung3_engine`, `spec`, `cusum_layer1/2`,
`ancestry5`) is imported, statically or at runtime (V16).

## 2. One sub-block, end to end

1. Float proposal at the sub-block centre `e_c`: collocation on Chebyshev–Lobatto nodes of every band,
   one Householder factorisation, four solves (D0..D3: `d`, `d'`, `d''`, `d'''` at `e_c`).
2. Exact candidates: every float coefficient rounded to a dyadic (52 bits), converted exactly to the
   power basis in `(p, m)` (bands 0–3) or `s` (band-4 axes).
3. Cover: the frozen initial boxes; each box and its bisection subtree is evaluated by `refine_box`
   in a worker. Per box: the Taylor models of `p, m, e`; the pieces; `Khat^(i) D_j` for `i = 0..2`,
   `j = 0..3` by exact Taylor shifts and the moment series; the sources; `r0, r1, r2` built from the
   `e`-Taylor candidates; `lam_k` = max over leaves of the rigorous `|r_k|` bound.
4. Atom bounds: `|D1(e)(a)| <= |D1(a)| + |D2(a)| de + |D3(a)| de^2 / 2`, `|D2(e)(a)| <= |D2(a)| + |D3(a)| de`,
   exact rationals.
5. Propagation (Theorem 5) with `C_T = tau = 3429/500` from F_H and the kernel norms.
6. The cell bounds are the maxima over the sub-blocks, which tile the cell block exactly.

## 3. Arithmetic backend and rounding

* Exact `fractions.Fraction` for every constant, candidate coefficient, box coordinate, atom bound,
  propagation and aggregate.
* Taylor-model coefficients are Python integers at scale 2^-160; each product/rounding is a floor with
  its error bounded and added to the remainder; the final `|r_k|` bound is rounded UP.
* `phi`, `Phi` point values: C7's rational enclosures (outward rounded, proved series remainders).
* The float proposal (IEEE double) is never trusted: only its dyadic-rounded coefficients are used, as
  exact numbers, and their quality only changes the size of `lam_k`.

## 4. Lifecycle (one execution)

| phase | artifact | gate |
|---|---|---|
| freeze (this turn) | `protocol/C11RD_FREEZE.json` + `.md`, committed | freeze commit recorded |
| pre-execution review (this turn) | `review/C11RD_PRE_EXECUTION_REVIEW.md` | `READY_TO_QUALIFY` |
| qualification (later, on instruction) | qualification record | `QUALIFICATION_ACCEPTED` |
| authorization (later) | `config/C11RD_GRANT.json` | `AUTHORIZATION_ACCEPTED` |
| execution (once) | `evidence/runs/C11RD_RUNS.json` + lock | seal commit |
| execution review | `review/C11RD_EXECUTION_REVIEW.md` | `EXECUTION_ACCEPTED` |
| comparison | `evidence/comparison/C11RD_COMPARISON.json` | classes for D1, D2 |
| N9 reassembly / adjudication | adjudication record | `N9_CLOSED` or `N9_REMAINS_OPEN` |

Runner guards (`--mode real`): R0 a PRE-IMPORT BARRIER (the first statements of the runner and the
comparator, using only the built-in modules `sys` and `posix`): the interpreter must be
`python3 -I -S -B` without a pycache prefix, the code directory must hold exactly the eight frozen
files (no `__pycache__`, no `.pyc`, nothing else) and C7's code directory no `__pycache__`, no `.pyc`
and nothing named like a standard-library module — so no stale or forged bytecode and no shadowing
module can run; after the imports every module loaded from either directory must be a frozen source
with no cache (checked again before the lock and before the artifact is written); R1 frozen code hashes
(the eight C11RD files and C7's `c7_gaussian.py`); R2 grant (ALLOW, binds freeze commit, code
hashes, cell-306 block, `max_executions = 1`, host/runtime; freeze commit an ancestor of HEAD; freeze file
byte-identical to the freeze commit's; not a shallow repository); R3 clean namespace (untracked and
ignored files included); R4 no lock and no runs artifact on disk, and neither was EVER committed on any
ref or reflog entry (full history), then the lock is created EXCLUSIVELY and never removed; R5 the F_H premise verifies; R6 the statement table's
block equals the frozen target. Every git call runs with `--no-replace-objects` and
`core.commitGraph=false`, so replace refs or a forged commit-graph cannot hide history.

One-execution rule. The lock is taken before any science, after R0–R6 pass: from then on the
execution is consumed, whatever happens next. The log prints progress counters and timings only
(never a residual, lam or bound). Retry policy: none automatic. A run that ends by a resource cap
writes a `NOT_CERTIFIED` runs artifact (targets INSUFFICIENT at comparison). A run that dies before
writing its artifact (host fault) leaves the lock; a second run needs a new, independently reviewed
authorization that addresses the fault — and is permitted only if no magnitude was ever written.

## 5. Where originals may appear

The comparator first checks its own code, the other C11RD files and C7's `c7_gaussian.py`
against the freeze (U2). Originals appear only in `c11rd_compare.py` step U5, from C11R's quarantine (blob `219e0122…`), after the seal, the
execution review, the exact recomputation (U3) and the statement comparison (U4). No certifier
module, document, protocol file or evidence file of this namespace contains an original value: V18
scans every file for all renderings (4–9 significant digits) of both disclosed values by hash, and
the comparator repeats the scan at the freeze commit (U7).
