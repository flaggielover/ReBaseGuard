# Replay measurement of the theorem-TC input fields at the m = 5 tail (cells 305–309)

Producer `code/tct_inputs.py`, host `rebaseguard-vultr-02`, frozen Aux5 venv
(python 3.12.3, numpy 2.5.2, scipy 1.18.1, python-flint 0.9.0), 256 bits, one thread per process, 2026-09-20.

**Not a new real scientific evaluation.** Every emitted field is a recomputation of an adopted K1 / Aux3 quantity;
no order-3 candidate of F is proposed and no order-3 field of F is written (`order3_fields_present: false`, and the
producer refuses if any `G`-family key appears). The guard was DENY throughout and no authorization exists.

Why a replay is needed at all: `cert.norms.k/j`, `sup_S0`, `sup.{F,D,H}`, the order-2 candidate at the atom
`H_at_a` and the whole-cell `W2` enclosures are **not stored** in the adopted K1 record, although the record's
`R2_interval` and `M_R2` are built from the last two. The replay reproduces them through the frozen chain.

| cell | K1 record sha256 | output sha256 | identity gate | CPU s |
|---|---|---|---|---|
| 305 | `585f56c2…` | `e1390b42…` | identical, 262 fields | not captured (see below) |
| 306 | `9c9da15b…` | `57ff9280…` | identical, 262 fields | 1359.6 |
| 307 | `28bacf0a…` | `8212a263…` | identical, 262 fields | 1351.3 |
| 308 | `e8d7a412…` | `386f4a77…` | identical, 262 fields | 1350.2 |
| 309 | `95be4c65…` | `57306bf5…` | identical, 262 fields | 1357.5 |

Cell 305's own CPU counter was lost: its reporting stream went with an ssh session that dropped while the process
ran (the process itself survived and wrote its output). Its wall clock was 04:43:24 → 05:05:xx UTC, i.e. ≈ 1320 s at
99.9% of one core. Measured total for 306–309 is 5418.6 CPU-s, so the replay cost **≈ 6740 CPU-s ≈ 1.87 CPU-h**
(Campaign A's own qualification replay of two cells cost 2795.7 CPU-s, the same ≈ 1400 CPU-s per cell).
**New real CPU-hours: 0.000.**

A second gate covers the two fields the 262-field gate does not reach — see `code/tct_rule.py`
`derived_identity_gate` and `evidence/forecast_r2/TAIL_FORECAST_R2.json` `derived_identity_gate`: the adopted
record's `R2_interval` is rebuilt for every m from `H_at_a`, `W2` and the record's own `eps_cell_refined` and must be
contained in the record interval within 10^-6 relative. Worst observed gap 3.63 · 10^-8 across 20 comparisons.

## What the numbers say

| quantity (range over the 25 objects of the 5 cells) | tail | adopted lower front (cells 11–44) |
|---|---|---|
| `sup.H` | 0.572 – 1.334 | 18.5 – 80.4 |
| `sup.D` | 0.298 – 0.782 | 8.3 – 21.6 |
| `sup.F` | 0.258 – 1.079 | 0.06 – 1.22 |
| `H_at_a` (order-2 candidate at the atom) | −0.817 – −0.032 | +6.10 – +53.9 |
| `norms.k` | [0.99995, 0.79767, 0.96705, 1.507, 2.7905] | [1, 0.79788, 0.96788, 1.510, 2.801] |
| `C_upper` (frozen block resolvent bound) | 5.782 – 7.733 | 1011 – 1177 |

The tail is a different regime: the per-order growth of the candidate suprema is ≈ 1.1× (H/D) and ≈ 0.6× (D/F),
against ≈ 2–4× and ≈ 20× on the front, and the resolvent amplification is ≈ 150× smaller.
