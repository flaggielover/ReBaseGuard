# C11 — N9 independent second-certifier closure

**Verdict: `AGREEMENT_INSUFFICIENT`. N9 remains OPEN.**

No cell closed, no cell adopted, no coverage change, no r6, guard **DENY** throughout. Zero new-real,
zero AWS, zero Vultr, zero toolchain provisioned.

## What N9 asks

From `OPEN_NOTES_DISPOSITION_C2.md`: *"the Arb/FLINT supersolutions remain the residual trust
surface … this is still **one implementation**. A second, independently written certifier is the real
answer, and C2 has not built one."* The adjudication sharpens the risk: *"a possible systematic error
in a single implementation … of unknown magnitude. No percentage protects against an
unknown-magnitude logic error. What does protect against it is a second, structurally independent
route to the same conclusion."*

Two things are **not stated anywhere** and are recorded as interpretation rather than promoted into
requirements: whether arithmetic-**backend** independence is required as well as implementation
independence, and any numeric agreement tolerance.

## What C11 built

A second certifier, written from the frozen model's own mathematical specification.

**Independence.** It imports nothing from the original's load-bearing graph — the forbidden set,
derived mechanically, is `taboo_certify, resolvent_certificate, opnorms, ra_certifier, fast_range,
intervals, rebaseguard_certify, rung3_engine, spec`. The original's backend is `numpy + flint.arb`;
this one uses **exact rational arithmetic from the standard library**, so the independence is both
implementational and arithmetic-backend — strictly stronger than N9 asks. The only shared surfaces
are **data**: the frozen constants, the reachable set, the cell geometry. Both certifiers must agree
about the *problem* or they would be answering different questions.

**The mathematics, re-derived.** From `(p,m)` the alarm-free window is `z ∈ [m−C, C−p]` and the next
state is `(max(0,p+z−K), max(0,m−z−K))`. Both are piecewise linear in `z` with kinks at `z = K−p` and
`z = m−K`, so splitting the window there makes the integrand a polynomial times `φ(z+e)`, and every
integral reduces to Gaussian moments under
`M_j = (j−1)M_{j−2} + A^{j−1}φ(A) − B^{j−1}φ(B)`. Exact throughout.

**It is sound**, by identities it could not satisfy by accident:

| check | result |
|---|---|
| standard-normal moments | `1, 0, 1, 0, 3` exactly |
| `(K_e 1) = 1 − h₁` at five states | rigorous intervals intersect; separation < 1e-60 |
| box bound vs pointwise kernel | dominates on every box tested |
| constant supersolution | certifies at 9000, fails at 6000 — straddling the theoretical `1/min h₁ ≈ 8070` |

## Why N9 does not close

| | |
|---|---|
| original `τ` (cell 307) | **4.952056205** |
| independent certified bound | **9000** |
| ratio | **1817×** against a frozen criterion of ≤ 2 |

The drift-aware family `w = A − B(p+m)` **fails outright**, and the margin *worsens* as the candidate
grows. The cause is identified and is an **engineering limit, not a soundness problem**: the
box-uniform kernel bound takes the widest alarm-free window over each box, so at affordable
subdivision depth it over-counts mass faster than the drift gain recovers. Depth 3 already costs
110–120 s per candidate and each level is 4× more boxes.

**There is no scientific disagreement.** The independent bound is a valid upper bound and is
consistent with the original's — it is simply far weaker.

Two further criteria fail independently of the numbers:

- **N10 (seal before compare)** — a blinded comparison was never available: the original's `τ` is
  committed and was read in phase B0 before implementation began. C11 does not claim one. What was
  maintained is the discipline that matters: **no candidate was chosen by fitting to the original's
  value** — the constant comes from the theoretical threshold, the drift-aware family from the
  structure of the chain.
- **N7 (precision escalation)** — only partially exercised; deeper subdivision was not affordable.

The gate's N6 explicitly **rejects** the weaker rule "both bounds are valid", which the constant
supersolution already satisfies trivially and which would let N9 close without any evidence of
implementation agreement — precisely the hole N9 exists to close.

## What this leaves the programme

N9 is **open**, F1 remains live, the C2 adoption floor stands, and no successor may yet freeze a
replacement floor. But the position is materially better than before: **a second implementation now
exists, is independent on both axes, and is validated.** What remains is tightness — a sharper
uniform bound that tracks how the alarm-free window varies across a box rather than taking the
union, or enough compute to subdivide far deeper.

## Layout

    code/c11_common.py      process identity by executable, committed-fact readers
    code/c11_b0_n9.py       B0 (16 checks), the N9 dossier, the forbidden-reuse list
    code/c11_certifier.py   THE SECOND CERTIFIER — exact rational, zero forbidden imports
    code/c11_result.py      the N9 verdict under the frozen criterion
    code/c11_mutations.py   12 planted independence and soundness violations
    config/N9_GATE_C11.json frozen criteria, with the ordering defect disclosed
