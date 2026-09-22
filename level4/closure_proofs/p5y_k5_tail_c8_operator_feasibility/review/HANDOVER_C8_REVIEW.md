# Handover to the C8 fresh-context reviewer

Campaign **C8 — Operator-Information Feasibility and Route Selection**. Fresh context; assume
nothing. C8 is a DECISION campaign: it closes no cell and executes no route.

Worktree `/Users/suzhe/ReBaseGuard-k5c8`, branch `p5y-k5-tail-c8-operator-feasibility`.
Namespace `level4/closure_proofs/p5y_k5_tail_c8_operator_feasibility`.

## What C8 claims

1. The authoritative `m=5` open set is **{306,307,308,309}**, and C7's prose "[305,309]" is wrong.
2. `Γ` depends on `A0` and never on `Λ`; `Λ` enters only as an admissibility **floor** on `A0`.
   Therefore **R1 and R2 have exactly zero closure leverage**.
3. Cell **306 already passes** the authoritative C5-T clause under committed supplies; its blocker is
   **adoption**, not information.
4. Cell **307** needs a `1.1203×` `A0` tightening — the smallest sufficient fact in the tail.
5. Cell **308** needs `A0` → floor **and** `A1` `1.2927×`.
6. Cell **309** is **MATHEMATICALLY REFUTED** for the whole atom-constant family.
7. Selected route: **R3 / E1 operator certification, cell 307 first**.

## Attack these, A–P

- **A** predecessor integrity; **B** the r5 open-set reconstruction (does it really read per-cell
  verdicts?); **C** the reconstructed equations; **D** the pointwise-vs-uniform distinction;
  **E** the clipping-gap definition; **F** the cell-gap definition; **G** the minimum-information
  inversion; **H** the perfect-information oracles; **I** the analytic route arguments;
  **J** the E1 programme classification; **K** the toolchain reconstruction; **L** the cost
  estimates; **M** the prospective decision gate; **N** mutation adequacy; **O** the zero-new-real
  boundary; **P** that no remote or toolchain activity occurred.

## Highest-value targets

- **The zero-leverage claim for R1/R2 is the load-bearing negative of the whole campaign.** If `Λ`
  can influence `Γ` by ANY route C8 missed, the conclusion collapses. Try to find one.
- **`M = magnitude`.** C8 drops the sealed clause's clip against the R2 interval, arguing the clip is
  unreachable from committed evidence and that dropping it is conservative. Verify both halves:
  that it really is unreachable, and that dropping it can only RAISE `Γ`.
- **The 309 refutation.** C8 calls it MATHEMATICALLY_REFUTED. The gate reserves that word for actual
  impossibility. Is the argument airtight, or is 309 merely BLOCKED?
- **Numbers.** Verify every figure in `README.md` against the JSON, and every baseline against C4's
  certificate, C5's forecast and r5. This programme has shipped that error at least five times.
- **Run things.** `code/*.py` are runnable and regenerate their own evidence; say so if you run one.

## Constraints

No AWS, no Vultr, no SSH, no installs, no numpy/scipy/flint/mpmath/sympy/gmpy2. Modify **no** file
except your report. No state-changing git. Use `PYTHONINTMAXSTRDIGITS=0`.

## Output

`review/REVIEW_C8_PREPUBLICATION.md`. Numbered findings with severity, exact file/line, what is
wrong, what it would take to fix. Distinguish "this is wrong" from "this is unverifiable from the
committed tree". End with exactly one verdict line: `READY_TO_PUBLISH`, `READY_WITH_CONDITIONS`, or
`NOT_READY`. Do not repair anything.
