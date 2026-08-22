# Stage B — optional Lean spine

**Status: not required for Stage B closure, and not wired into the build.**

`Period2Skeleton.lean` formalises only the elementary dynamical step that turns
the numerical certificate into the sentence "locally attracting nonzero
symmetric period-2 orbit":

| Formalised | Assumed (supplied by the certificate) |
|---|---|
| odd `F` with `F e = −e` ⟹ `F(F e) = e` | existence of the root |
| `e ≠ 0` ⟹ `F e ≠ e` (period exactly 2) | uniqueness in `I` |
| `F` odd and differentiable ⟹ `F'` even | the enclosure of `F'` on `I` |
| multiplier `= (F' e)²` | |
| certified enclosure of `F' e` inside `(−1,1)` ⟹ `|multiplier| < 1` | |

It deliberately does **not** attempt the Fredholm/Arb pipeline. Per the Stage B
brief, rigorous validated numerics plus written human mathematics is sufficient
for closure; Lean here is a readability aid for the dynamical skeleton only.

The frozen Level 1–3 Lean development in `rebaseguard-lean/` is **untouched**.
This file lives outside it precisely so that it cannot affect that build or its
axiom audit. It has not been compiled against a Mathlib toolchain in this
session, so it is offered as a proof sketch in Lean syntax rather than as a
machine-checked artifact — that distinction is exactly the one Stage B insists
on everywhere else, and it applies to this file too.
