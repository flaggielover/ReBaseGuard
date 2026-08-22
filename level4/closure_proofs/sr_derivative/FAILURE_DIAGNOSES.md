# Failure and obstruction diagnoses

## Arb rigor upgrade — OPEN, non-blocking

The authoritative-threshold Arb attempt did not fail because the numerical
candidate approached two; the fresh candidate remained near `17.29`.  It
remains open because the proof-critical global continuum error chain is not
implemented.

The precise obstruction is dependency loss in raw interval residual cells.
At width `1/32`, representative residual-`b` enclosures remain as wide as
`2.91`, despite a float point residual near `8e-6`.  Refining raw boxes would
need an impractical number of two-dimensional patches and still requires an
exact cover proof.

The known viable remedy is local Taylor/Chebyshev composition followed by
symbolic coefficient cancellation and Bernstein range bounds with certified
remainders.  That is substantial new proof engineering, not a permissible
post hoc widening or midpoint shortcut.  Until it exists, these are all
forbidden conclusions:

- `Gamma_SR>2` certified;
- rigorous SR local instability;
- `SR-GAMMA-CERTIFIED`; and
- transfer of the historical `A=520.3125` feasibility work.

The derivative theorem is unaffected because Arb is explicitly non-blocking
for `SR-DERIVATIVE-CLOSED`.

