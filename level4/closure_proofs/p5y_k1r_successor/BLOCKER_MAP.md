# Blocker map

## B1 — CUSUM compact-cover admission (cells 319–323, m=5)

The K1-cited lineage `p5y_k1_cusum_completion_successor` (commit `f8e6f758`) failed exactly
five obligations. The failing gate was `B_cover` only; every other top-level and nested gate
passed.

| cell | e interval | m=5 utilisation | ‖R‖ enclosure | M_R2 |
| ---: | --- | ---: | ---: | ---: |
| 319 | (3.567738000, 3.813341500] | 1.152916 | 0.099099 | 7.3311 |
| 320 | (3.813341500, 4.086346400] | 1.257775 | 0.098707 | 6.4771 |
| 321 | (4.086346400, 4.379488500] | 1.335284 | 0.110159 | 5.3630 |
| 322 | (4.379488500, 4.684480300] | 1.238998 | 0.133963 | 4.1011 |
| 323 | (4.684480300, 4.994980200] | 1.042928 | 0.163646 | 3.1094 |

Mechanism: `curvature = M_R2 · w² / 8` crossed the frozen `1/20` cover cap at m=5, where the
curvature majorant is largest and the cells widest. **Not** a target-bound violation — the
enclosures sit at 0.099–0.164 against target 2.

## B2 / B3 — the two splice bridges

Both compact covers end exactly at their frozen splice constant (CUSUM cell 325 → `11/2`;
SR terminal cell 368 → `c_SR`). The inherited P5X-T3 majorant is monotone decreasing in e
and at the splice is too loose: m=5 gives 2.4495 > 2, m=3 sits at exactly 2.0. The first e₀
where every m closes is `49750555/8388608` (CUSUM) and `1883835/262144` (SR), both driven by
m=5. The intervals between are uncertified — a certificate-coverage gap, not an observed
scientific failure. `e_far = 12` evidence certifies only `[12, ∞)`: monotonicity gives no
backward extension, so it cannot be reused here.
