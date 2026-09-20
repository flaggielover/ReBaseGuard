# Replay measurement of the theorem-TC input fields at the m = 5 tail (cells 305–309)

Producer `code/tct_inputs.py`, host `rebaseguard-vultr-02`, frozen Aux5 venv
(python 3.12.3, numpy 2.5.2, scipy 1.18.1, python-flint 0.9.0), 256 bits, one thread per process, 2026-09-20.

**Not a new real scientific evaluation.** Every emitted field is a recomputation of an adopted K1 / Aux3 quantity;
no order-3 candidate of F is proposed and no order-3 field of F is written. The gated order-3 entry points
(`certify_real_cell`, `rung3_engine.certify_order3`, `rung3_residual.g_residual`) are never reached. The guard was
DENY throughout and no authorization exists. The `order3_fields_present: false` flag and the producer's `G`-key
refusal are true **by construction** — the per-object dict is a fixed literal with no order-3 key — so they record
the design, they do not test it (review r1 note N10).

Why a replay is needed at all: `cert.norms.k/j`, `sup_S0`, `sup.{F,D,H}`, the order-2 candidate at the atom
`H_at_a` and the whole-cell `W2` enclosures are **not stored** in the adopted K1 record, although the record's
`R2_interval` and `M_R2` are built from the last two. The replay reproduces them through the frozen chain.

| cell | K1 record sha256 | output sha256 | producer identity gate | CPU s |
|---|---|---|---|---|
| 305 | `585f56c2…` | `e1390b42…` | identical, 262 fields | not captured (see below) |
| 306 | `9c9da15b…` | `57ff9280…` | identical, 262 fields | 1359.6 |
| 307 | `28bacf0a…` | `8212a263…` | identical, 262 fields | 1351.3 |
| 308 | `e8d7a412…` | `386f4a77…` | identical, 262 fields | 1350.2 |
| 309 | `95be4c65…` | `57306bf5…` | identical, 262 fields | 1357.5 |

Cell 305's own CPU counter was lost: its reporting stream went with an ssh session that dropped while the process
ran (the process itself survived and wrote its output). Its wall clock was 04:43:24 → 05:05 UTC, i.e. ≈ 1320 s at
99.9 % of one core. Measured total for 306–309 is 5418.6 CPU-s, so the replay cost **≈ 6740 CPU-s ≈ 1.87 CPU-h**
(Campaign A's own qualification replay of two cells cost 2795.7 CPU-s, the same ≈ 1400 CPU-s per cell).
**New real CPU-hours: 0.000.**

## What each replayed field is gated by

| field | gate |
|---|---|
| every object `delta_mid`, every `eps_mid` / `eps_cell` node, the Aux3 midpoint eps, Aux3 object residuals and Aux3 **order-3** candidate suprema | the frozen producer's 262-field identity gate, exact against the sealed record |
| `H_at_a`, `W2` | the **derived identity gate** (`tct_rule.derived_identity_gate`): the record's `R2_interval` is rebuilt for every m from them and the record's own `eps_cell_refined` and must be contained in the record interval with both endpoints within 10⁻⁶ (normalised by max(1, \|endpoint\|)). Worst observed gap 3.63 · 10⁻⁸ across 20 comparisons |
| `norms.k/j`, `sup_S0`, `sup.{F,D,H}` (order 0) | **neither gate directly.** They are covered only indirectly: they feed the gated residual and Aux3-eps computations, so an error in them perturbs gated fields. This is the residual trust surface of the measurement and it is exactly the family that dominates f_G (review r1 note N41/N5) |

`ADOPTED_TAIL_INPUTS.json` (sha256 `485fb125…`) carries, verbatim and manifest-checked, the adopted record fields the
tail arithmetic consumes that are not in the measurement records — the Aux3 order-3 candidate suprema and midpoint
errors (premise (P3′)), `eps_cell_refined`, `C_upper` and the per-m `R`/`D`/`R2` intervals and `M_R2`. With it every
published tail number can be **re-derived** from committed files alone, which review r2 did independently. It does not
make the generator **re-runnable** off-host: `tail_forecast_r2.py` still reads the live sealed records and uses this
extract only as a field-by-field checker — the safe direction, but a distinction worth keeping (review r2 note M9).
Anyone re-deriving from `cells.json` must filter on `detector == "CUSUM"` first: its `index` field collides across
detectors, and SR `index = 305` is a different cell entirely (note M6).

## What the numbers say

Ranges over the 25 objects (5 cells × r = 0…4), recomputed from the committed measurement records:

| quantity | tail (305–309) | adopted lower front (11–44) |
|---|---|---|
| `sup.F` | 0.1843 – 1.0789 | 0.0603 – 1.2222 |
| `sup.D` | 0.2981 – 0.6952 | 8.281 – 21.635 |
| `sup.H` | 0.5723 – 1.3345 | 18.526 – 80.436 |
| `H_at_a` (order-2 candidate at the atom) | −0.8171 … **+0.0897** (4 of the 25 centres are positive) | +6.103 … +53.885 |
| `sup.H / sup.D` | 1.113 – 4.464 | 2.006 – 4.326 |
| `sup.D / sup.F` | 0.532 – 1.805 | 16.92 – 144.40 |
| `norms.k` | k₀ 0.99978–0.99995, k₁ 0.79706–0.79767, k₂ 0.96498–0.96705, k₃ 1.50064–1.50699, k₄ 2.77345–2.79053 | [1, 0.79788, 0.96788, 1.510, 2.801] |
| `sup_S0` | 0.41719–0.44103, 0.28729–0.33123, 0.49327–0.54617, 0.69424–0.70015, 1.33595–1.35489 | [0.7042, 0.4839, 0.5283, 1.101, 1.48] |
| `C_upper` (frozen block resolvent bound) | 5.782 – 7.733 | 1011.2 – 1177.0 |

The tail is a different regime, but the difference is not uniform: the resolvent amplification is ≈ 150× smaller and
the order-0→1 growth `sup.D / sup.F` is 10–100× smaller, whereas the order-1→2 growth `sup.H / sup.D` **overlaps**
the front's range. Whether the order-2→3 growth behaves like the first or the second is precisely the unmeasured
quantity on which route T2 turns.
