# P5X Lean plan

## 1. Principle

Lean formalises the **logical spine that consumes certified scalars**, at the
point where an "obvious" algebraic step is most likely to hide an error. It
does not formalise the stochastic monitoring process, the Fredholm reduction,
or any interval computation. This is the same division of labour P5 used
(`p5_nonlinear_dynamics/lean/NonlinearSkeletonP5.lean`, 12 declarations,
sorry-free) and the same one `closure/02_THEOREM_MAP.md` enforces between
Lean (`T-19`) and Arb (`N-03`).

Toolchain: `rebaseguard-lean/`, mathlib `v4.34.0-rc1`, `Mathlib` import,
axioms restricted to `propext`, `Classical.choice`, `Quot.sound` and audited by
an axiom-audit run.

## 2. What is formalised

| id | statement, abstractly | consumes | corresponds to |
|---|---|---|---|
| `X1` | for an odd map `M` with `|M(x)| <= B` for all `x`, and any `c > B`, the interval `[-c, c]` is forward invariant and `sign(x)(M(x) - x) <= B - |x| < 0` for `|x| > B` | a bound `B` | `P5X-T5` |
| `X2` | if `V(x) = x^2`, `E[V(next) | x] = alpha g(x) + beta` with `g_min <= g <= g_max`, and a probability measure `p` is invariant for the kernel with `E_p[V] < infinity`, then `alpha g_min + beta <= E_p[V] <= alpha g_max + beta` | invariance, finiteness, two scalar bounds | `P5X-T6` |
| `X3` | `sqrt(alpha g_min + beta) > r` implies the invariant law's RMS strictly exceeds `r` | `X2` | `P5X-T6` corollary |
| `X4` | Paley–Zygmund style: `E[Y] = mu`, `E[Y^2] <= M`, `Y >= 0` implies `P(Y > r) >= (mu - r)_+^2 / M` | — | `P5X-T6b` |
| `X5` | for a continuous `s > 0` on `(0,E]` attaining each level `L >= 1` exactly once, and `|R| <= B < E`: the level set `{ s = 1/rho }` is a singleton for `rho in (rho_c, 1]` and empty for `rho <= rho_c` | shape hypotheses as *hypotheses* | `P5X-T7` → `P5-T9`'s algebra |
| `X6` | an odd `C^1` map on `[-c,c]` with `|f'| <= L < 1` off a neighbourhood of a hyperbolic 2-cycle, and no other periodic points, has that 2-cycle as a global attractor of `[-c,c] \ {0}` | interval-dynamics outputs as hypotheses | `P5X-T8`, optional |

`X1`–`X3` are the spine of the campaign's primary claim and are mandatory.
`X4` and `X5` are cheap. `X6` is written only if `P5X-T8` is attempted.

## 3. What is deliberately **not** formalised

* the frozen detector recursions and the stopping time as measurable objects
  (P5 made the same call; Level 1–3 formalised only the differentiation and
  moment spine, `closure/02_THEOREM_MAP.md` §A);
* `P5X-T1`/`T2`/`T3` — the reduction and the far-field lemma, which are
  human-proved and checked by the correspondence tests;
* any interval arithmetic. Lean says nothing about the value of `R_max`,
  `s_min` or `M_2`, exactly as it says nothing about the value of `Gamma`.

`LIMITATIONS.md` states this boundary in the same words, and gate `G7` checks
only that the spine compiles sorry-free with the audited axiom set — never that
Lean has certified a number.

## 4. Correspondence obligation

Each Lean declaration carries a docstring naming the P5X theorem it is the
spine of, and `LEAN_CORRESPONDENCE.md` (written at Checkpoint B) must map every
`X`-id to a `P5X-T` id and to the certified scalars it consumes, with the
mapping asserted by a test. An unmapped declaration is a gate failure.
