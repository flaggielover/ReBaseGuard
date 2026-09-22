# C11 — N9 independent second-certifier closure

**Verdict: `EXECUTION_INVALID`. N9 remains OPEN.**

No cell closed, no cell adopted, no coverage change, no r6, guard **DENY** throughout. Zero new-real,
zero AWS, zero Vultr, zero toolchain provisioned.

> **This campaign was adjudicated REJECTED and repaired before publication.** Its first verdict —
> `AGREEMENT_INSUFFICIENT`, on the ground that the independent route is 1817× too weak and the gap is
> an engineering limit — was **wrong**, and wrong in the way the brief warned about: it declared a
> route dead on a blocker it manufactured. Every adjudicator finding was verified mechanically before
> absorption (`evidence/handover/HANDOVER_FACT_VERIFICATION.json`, 15 facts, all CONFIRMED). The
> corrections are recorded as errata E1–E10 in the frozen gate. **What the first draft said about
> *why* N9 stays open should not be carried forward; what it said about independence and soundness
> should.**

## What N9 asks

From `OPEN_NOTES_DISPOSITION_C2.md`: *"the Arb/FLINT supersolutions remain the residual trust
surface … this is still **one implementation**. A second, independently written certifier is the real
answer, and C2 has not built one."* The C2 adjudication is more specific about the target: *"a
**second, independently written certifier** reproducing the six operator constants for cell 306
(closing N9)."*

## What C11 built

A second certifier, written from the frozen model's own mathematical specification.

**Independence — established.** It imports nothing from the original's load-bearing graph — the
forbidden set, derived mechanically, is `taboo_certify, resolvent_certificate, opnorms, ra_certifier,
fast_range, intervals, rebaseguard_certify, rung3_engine, spec`. The original's backend is
`numpy + flint.arb`; this one uses **exact rational arithmetic from the standard library**, so the
independence is both implementational and arithmetic-backend. The only shared surfaces are **data**:
the frozen constants, the reachable set, the cell geometry.

One qualification the first draft omitted: this is independence of *implementation and backend*, not
of *authorship*. The comparator error below is a live demonstration of what that distinction costs —
a same-author second implementation did not catch a same-author misconception about which of two
published constants the machinery computes.

**The mathematics, re-derived.** From `(p,m)` the alarm-free window is `z ∈ [m−C, C−p]` and the next
state is `(max(0,p+z−K), max(0,m−z−K))`. Both are piecewise linear in `z` with kinks at `z = K−p` and
`z = m−K`, so splitting the window there makes the integrand a polynomial times `φ(z+e)`, and every
integral reduces to Gaussian moments under
`M_j = (j−1)M_{j−2} + A^{j−1}φ(A) − B^{j−1}φ(B)`. Exact throughout.

**Soundness — established**, by identities it could not satisfy by accident, each now with a producer
(`code/c11_runs.py`; previously they were asserted in prose with nothing to run):

| check | result |
|---|---|
| standard-normal moments | `1, 0, 1, 0, 3` exactly |
| `(K_e 1) = 1 − h₁` at six states | rigorous intervals intersect |
| box bound vs pointwise kernel | dominates at **interior** points for a **non-constant** `w` |
| constant supersolution | certifies at 9000, refuted at 6000 — straddling `1/min h₁ = 8070.30` |
| vacuous-enclosure guard | refuses out of range (erratum E5) |

## The agreement criterion is met

**Against the correct comparator.** `taboo_certify.certify_block` proves two different statements
(lines 202–203): `full=False` gives `(C_T, tau)` against the **atom-removed** kernel `Khat_e`;
`full=True` gives `Abar` against the **whole** kernel `K_e`. C11's certifier proves the `full=True`
statement word for word, so the constant it produces is `Abar`. The first draft divided by `tau`.

| | value |
|---|---|
| `Abar` (whole kernel — what C11 proves) | **7.5556132** |
| `tau` (atom-removed — what C11 compared to) | 4.9520562 |

| independent certified bound | depth | margin | vs `Abar` | vs `tau` |
|---|---|---|---|---|
| **`w = 9.9 − 1.5·m`** | 4 | **+0.08406** | **1.310 ≤ 2** ✓ | **1.999 ≤ 2** ✓ |
| `w = 12 − 1.5·m` | 4 | +0.09043 | 1.588 ≤ 2 ✓ | 2.423 ✗ |

190 seconds of laptop time. **The frozen factor-of-2 criterion is satisfied against either
comparator** — so the first draft's negative verdict does not survive even on its own terms.

## What the first draft got wrong

Its family `w = A − B(p+m)` fails **pointwise** — exact kernel, no box bound, no subdivision:

| candidate | first draft's box margin | rigorous pointwise margin | binding |
|---|---|---|---|
| A=9, B=1.3 | −4.5243 *(unreproducible)* | **−2.2328** | (65/14, 0) |
| A=12, B=2.0 | −6.4251 | **−2.9033** | (65/14, 0) |
| A=20, B=3.0 | −9.1343 | **−3.8477** | (65/14, 0) |

Minimising the required `A` over the **whole family** gives `A = 8070.30 at B = 0` — exactly the
constant-family threshold. The "drift-aware" family is provably **never better than a constant**, at
any depth, with any box bound. The recorded blocker — *"the box-uniform kernel bound is too loose …
needs a sharper bound or more compute"* — is false, and it was the instruction the successor would
have inherited.

The signature was there and was misread: *"the margin worsens as the candidate grows"* is the mark of
a **structurally infeasible ansatz**, not of a loose bound — a loose bound gets relatively *cheaper*
as the candidate grows. The check that refutes it costs **0.4 s per state** against 190 s for one
certification run. A negative verdict owes that check before it blames its own machinery.

The ansatz decreased in `p`. The true solution of `v = 1 + K_e v` is **4.445 at the atom, flat in `p`
(spread 0.044) and decreasing in `m` (drop 3.33)**. Deleting the `p` term was the whole fix.

## Why N9 still does not close

Not tightness, and not compute. Two reasons, neither identified by the first draft:

1. **Statement.** The original certifies *"for every e in [e_lo, e_hi]"* — for cell 307 that block is
   `[1.7885921, 1.882413]`. C11 certifies at the single rational `e = 1.8355`, and every drift
   parameter in the certifier is a scalar with no interval path. C11 solves a **strictly easier
   problem**; a certifier that cannot express block-uniformity cannot corroborate the original's
   statement however close its number lands. This is the real remaining engineering work.
2. **Scope.** N9 is worded about **six operator constants for cell 306**. C11 produced **one**, for
   **cell 307**, and has never implemented `Khat_e` at all — so it cannot produce two of the six.

`C11-N10` (seal before compare) also fails, but is now booked honestly as a **process omission that
was available and simply not arranged**, not an inherent limitation: `REGISTRY_C2` is read in one
module, and the two documents phase B0 reads contain **zero** occurrences of `tau`, `Abar`, `4.95` or
`7.555`. The verdict does not lean on it.

## What this leaves the programme

N9 is **open**, F1 remains live, the C2 adoption floor stands, and no successor may yet freeze a
replacement floor. The position is materially better than before: a second implementation exists, is
independent on both axes, is validated, and **agrees with the original to within 31%** on the
constant it actually produces. What remains is an interval drift and the other five constants — a
defined engineering task, not an open research question.

## Layout

    code/c11_common.py      process identity by executable, committed-fact readers
    code/c11_b0_n9.py       B0 (16 checks), the N9 dossier, the forbidden-reuse list
    code/c11_certifier.py   THE SECOND CERTIFIER — exact rational, zero forbidden imports
    code/c11_runs.py        every certifier number, measured; pointwise refutation first
    code/c11_crosscheck.py  float shadow: true value function, family feasibility (NOT load-bearing)
    code/c11_result.py      the N9 verdict under the frozen criterion
    code/c11_mutations.py   15 planted violations, incl. comparator and unproduced-margin mutants
    code/c11_handover.py    mechanical verification of every adjudicator claim
    config/N9_GATE_C11.json frozen criteria, plus errata E1–E10
    review/ADJUDICATION_C11.md  the independent adjudication (REJECTED)
