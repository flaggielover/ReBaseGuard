# P5X — `F3` Provenance and Theorem-Consumer Requirement Audit

`GOVERNANCE_PROVENANCE_AUDIT`. **No binding checkpoint created, no gate changed,
no historical artifact edited, no expensive certification rerun.**
`R8 SR full-cell prototype = FAIL` stands exactly as recorded.

```text
VERDICT   CASE B -- F3 IS OVER-SPECIFIED
          0.2 was self-described at Checkpoint A as "the campaign's central
          engineering bet", a method-viability stop-gate.  The actual theorem
          consumer (G3 / P5X-T4) needs half-width < 0.4096577169 at the audited
          cell -- 2.048x looser.
GOVERNANCE  G2 -- permissible successor re-specification, never retroactive
```

---

## 1. First appearance — pre-result, and self-labelled

`0.2` enters at **`db0781e`, Checkpoint A, the very first P5X commit**, before
any production result existed. Three files carry it:

**`CERTIFICATE_PLAN.md` §3** — the origin and rationale, quoted exactly:

> Against the `e = 0` precedent (`delta_a <= 8.46e-6`, `C = 1315.79`, giving
> `E_a ~ 0.011`), the required half-width for `P5X-T4` is `< 0.2`. **That margin
> is the campaign's central engineering bet**, and step 3 of
> `PROOF_OBLIGATIONS.md` §4 tests it on a single cell before any scaling.

**`PROOF_OBLIGATIONS.md` §4 step 3:**

> Build `C1` for **one** cell ... and publish its achieved width, before
> scaling. If the achieved width exceeds `0.2` the campaign re-plans rather than
> scaling a losing method. ... Step 3 is a deliberate stop-gate: it is the
> cheapest possible falsification of the campaign's central engineering
> assumption.

**`CODEX_HANDOFF.md` §3 step 3:** "If it exceeds `0.2`, **stop and re-plan**;
do not scale."

So `0.2` was a **method-viability stop-gate**: a pre-registered, honestly
labelled engineering margin whose stated purpose was to stop the campaign
cheaply if the certification method was losing. It did exactly that.

**One inaccuracy in the prose.** `CERTIFICATE_PLAN.md` says "the required
half-width for `P5X-T4` is `< 0.2`". That overstates necessity: `P5X-T4`'s
frozen pass condition requires only `< 0.4096577169` at the binding cell (§3).
The *gate* was stated correctly; only the planning prose overstated it.

## 2. The actual consumer chain

`FROZEN_GATES.md` `G3`, frozen at Checkpoint A:

> `P5X-T4` certified in every frozen cell (`sup_e |R| <= R_max < 2`), and
> `P5X-T5` stated as its corollary with the explicit trapping interval

`FROZEN_THEOREM.md`:

```text
P5X-T4:  sup_{e in R} | R_{D,m}(e) |  <=  R_max(D,m)  <  2
P5X-T5:  for |e| > rho R_max,  sign(e)(E[e_{j+1}|e] - e) <= rho R_max - |e| < 0,
         so I_rho = [-rho R_max, rho R_max] subset [-2,2] is forward invariant
```

**`R_max < 2` is the entire first-moment requirement.** The `2` is itself
flexible: `FEASIBILITY_AUDIT.md` `H3b` records "the constant `2` may be replaced
by any certified `E` with `s(E) < 1`".

What does **not** consume this cell's enclosure: `G2` (local `P3`
correspondence) uses `R'(0)`, a derivative at `e = 0`; `rho_c = 1/|1 -
GammaTilde|` likewise depends on the slope at `0`; `G4` needs `s_min > 0` and
`M_2 < infinity`, which are second-moment quantities. None is affected by the
first-moment half-width at `e in [0.24, 0.26]`.

The audited cell **is** the binding cell for `R_max`: `FEASIBILITY_AUDIT.md`
records `sup |R|` on the scan at `SR 1.591 (m=1, e = 0.25)`.

## 3. Consumer-derived maximum half-widths (centre `R = -1.5903422831`)

| consumer | requirement | max admissible half-width |
|---|---|---|
| sign only | enclosure stays negative | `< 1.5903422831` |
| `R < -1` | — | `< 0.5903422831` |
| **`G3` / `P5X-T4`** | **`|R| < 2`** | **`< 0.4096577169`** |
| `|R| < 1.8` (a tighter `E`) | hypothetical | `< 0.2096577169` |
| `F3` as frozen | engineering bet | `<= 0.2` |

`F3` is **2.048x stricter** than the strongest load-bearing consumer, and
`F3 => G3` uniformly (at small `e`, `|R| -> 0`, so `G3`'s tolerance approaches
`2`). `F3` is sufficient, not necessary.

## 4. What R8's enclosure already certifies

R8: `[-2.6875142831, -0.4931702831]`, half-width `1.097172`.

| claim | verdict |
|---|---|
| `R_{SR,1} < 0` (sign) | **CERTIFIED** (upper `-0.493170`) |
| `|R| < 2` (`G3` / `P5X-T4`) | **NOT certified** (`|R|max = 2.687514`) |
| `R < -1` | NOT certified |
| separation from the R2 CUSUM enclosure `[-1.584952, -1.567644]` | NOT certified |

So R8 already certifies the **sign** of the SR selection map on this cell. It
does not certify the load-bearing saturation claim.

## 5. Hypothetical outcomes (DIAGNOSTIC, not rigorous)

| construction | half-width | `|R|max` | `G3` | `F3` |
|---|---|---|---|---|
| pointwise-best `C = 141.361` x direct-residual@1024 | `0.235980` | `1.826322` | **PASS** | FAIL |
| **current certified `C = 216.963`** x direct-residual@1024 | `0.356837` | `1.947179` | **PASS** | FAIL |
| pointwise-best `C` x R8 B2@1024 | `0.718341` | `2.308683` | FAIL | FAIL |

**Two constructions that fail `F3` would satisfy the actual theorem consumer**,
including one needing *no* improvement to `C_SR` at all.

## 6. A qualification that must not be skipped

`G3` requires `|R(e)| < 2` at **every** cell, and `C_SR(e)` is certified at only
two drifts: `203.067` at `e = 1/4` and `1505.821` at `e = 0`.

| `e` | `C_SR` | `|R(e)|` | half-width | `|R|max` | `G3` |
|---|---|---|---|---|---|
| `0.25` | `203.067` | `1.5903` | `0.334623` | `1.924923` | PASS |
| `0.24` | `216.963` | `1.5903` | `0.356837` | `1.947137` | PASS |
| **`0`** | **`1505.821`** | `0` (oddness) | `2.417205` | `2.417205` | **FAIL** |

At the `|R|` argmax `G3` would be met with `~13%` margin, but near `e = 0` the
same certifier gives `|R|max = 2.417 > 2` and `G3` **fails**. A `G3`-based gate
is therefore **not** automatically satisfied campaign-wide: the binding region
moves from the `|R|` argmax to small `e`, where `C_SR` is large even though
`|R|` is small. That per-cell analysis is outside this audit's scope and is
recorded as an open item.

## 7. Governance

**`G2` — permissible successor-campaign re-specification** based on a
newly audited theorem-consumer requirement. Not `G1`: nothing historical is
changed and `R8` remains `FAIL`. Not `G3` (specification defect): the frozen
gate `G3` was stated correctly at Checkpoint A; only `CERTIFICATE_PLAN.md`'s
prose overstated `0.2` as "required", and that prose is not a gate.

**Historical `R8` is untouched and remains `FAIL` against `F3 = 0.2`.** Any new
threshold belongs to a future successor checkpoint only, frozen before any
result.

## 8. Drafted successor gate — NOT created

The cleanest successor design replaces the proxy with the consumer itself:

```text
F3'  (successor, to be frozen BEFORE any result)
     The certified enclosure of R_{D,m}(e) on every accepted cell of the
     frozen cover satisfies  |R| < 2  strictly, i.e. G3's own pass condition
     verbatim from Checkpoint A.
     The achieved half-width is REPORTED, not gated.
```

*Exact consumer:* `G3` / `P5X-T4` / `P5X-T5`.
*Exact inequality:* `sup_e |R_{D,m}(e)| <= R_max < 2`.
*Derived half-width at the binding cell:* `< 0.4096577169`.
*Safety margin:* none is invented — the inequality is used as written, and the
strictness is enforced by requiring the enclosure's upper magnitude to be
strictly below `2`.

*Why this is not post-result gate weakening:* the condition is quoted verbatim
from `FROZEN_GATES.md` `G3`, written at Checkpoint A before any result existed;
it is not a number chosen to admit a known outcome; and it demonstrably retains
teeth — R8's actual enclosure **fails** it (`|R|max = 2.688`), and so does the
`e -> 0` region under every certifier measured so far.

*Why historical R8 remains FAIL:* R8 was adjudicated against `F3 = 0.2`, which
was frozen pre-result and correctly applied. A successor gate does not
retroactively change what R8 measured or how it was judged.
