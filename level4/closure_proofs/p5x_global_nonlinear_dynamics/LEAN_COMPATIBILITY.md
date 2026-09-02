# P5X Lean spine — compatibility check against the completed human proofs

Scope discipline for this stage: **no Lean is written**. The only question asked
here is whether the `X1`–`X6` spine frozen in `LEAN_PLAN.md` §2 still states the
right abstract facts now that `L1`, `L2`, `L3`, `L5`, `L6` are proved. Full
implementation waits until the certified scalar route survives the stop-gate.

| id | frozen abstract statement | the P5X theorem it is the spine of | compatible? | note |
|---|---|---|---|---|
| `X1` | odd `M` with `\|M\| <= B`; then `[-c,c]` (`c > B`) is forward invariant and `sign(x)(M(x)-x) <= B - \|x\| < 0` for `\|x\| > B` | `P5X-T5` | **yes** | instantiate `M = rho R`, `B = rho R_max`. Oddness is `P5-T3` and is used only for the symmetry of the trapping interval, not for the drift inequality; the frozen statement is therefore slightly stronger in hypothesis than needed, which is harmless |
| `X2` | `E[V(next) \| x] = alpha g(x) + beta` with `g_min <= g <= g_max`, `p` invariant, `E_p[V] < infinity`; then `alpha g_min + beta <= E_p[V] <= alpha g_max + beta` | `P5X-T6` via `L6` | **yes** | `L6` proves exactly `E[e'^2 \| e] = rho^2 (R^2 + S)(e) + (1-rho)^2/m`, so `alpha = rho^2`, `g = R^2 + S`, `beta = (1-rho)^2/m`. The lower constant is supplied as `g_min = s_min` using `R^2 + S >= S >= s_min`; that inequality is discharged **outside** Lean, which only consumes `g_min` |
| `X3` | `sqrt(alpha g_min + beta) > r` implies the invariant law's RMS strictly exceeds `r` | `P5X-T6` corollary | **yes** | direct from `X2`; `r` is instantiated with P7's frozen `r_lin` |
| `X4` | `E[Y] = mu`, `E[Y^2] <= M`, `Y >= 0` imply `P(Y > r) >= (mu - r)_+^2 / M` | `P5X-T6b` | **yes, but** | the *theorem* it serves needs `L7` and a certified `M_4`; `L7` was not in the Phase-1 mandate and is not proved. `X4` may be written, but nothing may cite `P5X-T6b` until `L7` is discharged |
| `X5` | continuous `s > 0` on `(0,E]` attaining each level `L >= 1` exactly once, with `\|R\| <= B < E`; then the level set `{s = 1/rho}` is a singleton for `rho in (rho_c, 1]` and empty for `rho <= rho_c` | `P5X-T7` → the algebra of `P5-T9` | **yes** | note that `X5` takes the shape facts as *hypotheses*; the frozen wording "attains each level exactly once" is the weakened form `P5X-T7`(2) states, not strict monotonicity, so the spine already matches the weaker certified target |
| `X6` | odd `C^1` map on `[-c,c]` with `\|f'\| <= L < 1` off a neighbourhood of a hyperbolic 2-cycle and no other periodic points has that cycle as a global attractor of `[-c,c] \ {0}` | `P5X-T8` | **yes**, optional | unchanged; written only if `P5X-T8` is attempted |

## Findings

1. **No incompatibility.** Nothing proved in Phase 1 contradicts or outdates the
   frozen spine, and no frozen `X` needs restating.
2. **One hypothesis is looser than the proof needs** (`X1`'s oddness). Harmless;
   left as frozen.
3. **One spine element is ahead of its theorem** (`X4` vs the unproved `L7`).
   Recorded so that `X4` compiling is never read as `P5X-T6b` holding.
4. **The spine consumes exactly three certified scalars** — `R_max`, `s_min`,
   `M_2` — matching `DEPENDENCY_AUDIT.md` §4. Lean asserts no numerical value,
   in keeping with `LEAN_PLAN.md` §3 and with the Level-1..3 separation between
   `T-19` (machine-checked) and `N-03` (certified).

`FROZEN_GATES.md` `G7` remains testable as written.


---

## Re-check after the R-A′ repair (certified-method change only)

The certified **scalar interface** the spine consumes is unchanged by R-A′:
`X1` still consumes a bound `B` on `|M|`, `X2`/`X3` still consume
`alpha, beta, g_min, g_max`, and `X4`-`X6` are untouched. R-A′ altered how those
scalars are *obtained* (recentred representation, exact-centre Taylor model in
`e`, sub-cell hull), never what they are.

One addition is worth recording for the eventual `LEAN_CORRESPONDENCE.md`: R-A′
produces enclosures **per sub-cell**, and the cover-level scalar is the hull.
`X1`-`X3` take a single scalar, so the hull step happens outside Lean, in the
same layer that already takes the sup over the cover. No `X` statement changes.

`FROZEN_GATES.md` `G7` remains testable as written. Full Lean implementation
still waits, per the staging discipline: the certified scalar route has now
survived a stop-gate, but no cover exists yet.

---

## Re-check after Compute Optimization R1 (bound refactor, no interface change)

R1 replaced one rigorous upper bound on `||(I - K_e)^{-1}||_inf` by a tighter
one. That scalar is **internal to the certifier**: it never reaches Lean. The
spine still consumes exactly `R_max`, `s_min`, `M_2` (and, for `X1`, a bound `B`
on `|M|`), and `X1`-`X6` are unchanged word for word.

The only observable difference at the interface is that the certified scalars
arrive with **smaller radii** — `X2`/`X3` take `g_min`, `g_max` as hypotheses and
are indifferent to how tight they are. No `X` statement, hypothesis or
conclusion is affected, and `FROZEN_GATES.md` `G7` remains testable as written.

`LEAN_INTERFACE_CHANGED = NO`.
