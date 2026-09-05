# `dF_0` near-zero budget failure — diagnosis

Diagnostic only. No checkpoint, budget, threshold, cover or precision changed;
no production run; no verdict changed.

## What was measured

Six drifts, full certification of `F_0` and `dF_0` at each:

| e | C(e) | `F_0` defect | `F_0` util | `dF_0` defect | `dF_0` util (as charged) |
|---|---|---|---|---|---|
| 0 | 1232.84 | 3.698e-06 | 11.40% | 7.916e-05 | **244.00%** |
| 1/100 | 1136.84 | 3.763e-06 | 10.69% | 7.878e-05 | 223.92% |
| 1/40 | 1008.05 | 3.927e-06 | 9.90% | 7.681e-05 | 193.61% |
| 1/20 | 828.09 | 5.489e-06 | 11.36% | 7.051e-05 | 146.00% |
| 1/10 | 567.16 | 8.144e-06 | 11.55% | 5.318e-05 | 75.42% |
| 1/4 | 207.75 | 1.289e-05 | 6.70% | 3.241e-05 | 16.84% |

## What is actually growing

```text
sup|dF_0|              1.3835 -> 14.8869     10.76x
sup|source|            0.7389 ->  0.6137      0.83x
cond(I - K)             644.4 ->  2319.6      3.60x
dF_0 certified defect  3.24e-5 -> 7.92e-5     2.44x
```

The **object** grows 10.76x; the **certified defect** grows only 2.44x. In
relative terms the certifier gets **4.41x better** as `e -> 0`
(2.34e-05 -> 5.32e-06 of `sup|dF_0|`). So this is not representation loss and
not a certifier breakdown.

`dF_0(x0)` is `R'(e)`, and it runs `+0.0202` at `e = 1/4` to `-14.8869` at
`e = 0`. That is `R'(0) = 1 - GammaTilde`, giving
`GammaTilde_{CUSUM,m=1} = 15.887` — inside the certified-but-wide `Gamma_CUSUM`
enclosure the feasibility audit records (width 23.9). The object is behaving
exactly as the theory says it must.

Precision is not the cause: the defect is **bit-invariant** at 256, 384 and 512
bits (7.915965e-05 at all three), and the truncation+tail term is 0.011% of the
total. Residual-limited, not rounding-limited.

## The actual cause — a ledger operation, and it is mine

I charged the `dF_r` objects as

```text
C(e) * delta_dF   against  B_candidate
```

That is dimensionally wrong. `delta_dF` is an error in `dR/de`. To become an
error in `R` it must be multiplied by a length in `e`. The frozen ledger says so
explicitly: `B_cover` covers "the e-cell Taylor model `h|R'| + (h^2/2) S_2`" —
the `R'` contribution enters `R` weighted by the cell half-width `h`.

The correct charge is

```text
h(e) * C(e) * delta_dF   against  B_cover
```

and the frozen step rule makes this **C-independent by construction**:

```text
h(e) = 1/(4 a C(e))   =>   h(e) * C(e) = 1/(4a) = 0.313329   for every e
```

| e | as charged (`C·δ / B_candidate`) | correct (`h·C·δ / B_cover`) |
|---|---|---|
| 0 | 244.00% | **0.0496%** |
| 1/100 | 223.92% | 0.0494% |
| 1/40 | 193.61% | 0.0481% |
| 1/20 | 146.00% | 0.0442% |
| 1/10 | 75.42% | 0.0333% |
| 1/4 | 16.84% | 0.0203% |

Under the correct mapping the term is flat across the whole approach to zero and
sits ~2000x below its line. The blow-up was an artifact of applying the full
resolvent amplification with no cell-width weighting — which is precisely what
the `h = 1/(4aC)` step rule exists to cancel.

## What this does NOT license

The corrected mapping is a **reading** of the frozen ledger, not a frozen
assignment: `B_cover`'s description names `|R'|`, which is the strongest
available evidence, but no frozen artifact states "dF_r charges to B_cover".
Adopting it in production is a governance step and is not taken here. The
`F_r` objects are unaffected — they enter `R` directly and remain on
`B_candidate`, where they pass at 6.70%–11.55% across all six drifts.

## Symmetry

At `e = 0` the state-swap `sigma: (x+,x-) -> (x-,x+)` with `z -> -z` commutes
with the dynamics, making `S_0` and `F_0` sigma-odd and `dF_0` sigma-even. This
is real structure and could halve the derivative work, but it is **not** the
`P5-T3` symmetry, which is parity in `e` (`R(-e) = -R(e)`), not a state swap.
It is therefore not traceable to an already-authoritative theorem and is not
used.

## Cover count

The 326-vs-323 inconsistency is untouched here and remains an independent
downstream governance issue.
