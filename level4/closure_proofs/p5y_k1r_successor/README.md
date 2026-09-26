# P5Y-K1R successor

Additive successor to the adjudicated **K1 = PARTIAL** result. It exists to close exactly
three residual certificate gaps and nothing else:

| blocker | what it is | route |
| --- | --- | --- |
| **B1** | CUSUM compact-cover admission, original cells 319–323 at m=5 | admission decision tree (Aux5 composite, or a preregistered 10-child recompute) |
| **B2** | CUSUM bridge `(11/2, 49750555/8388608]` | 2 new compact cells |
| **B3** | SR bridge `(c_SR, 1883835/262144]` | 6 new compact cells, AWS only |

`c_SR = 3803026123175981/562949953421312`.

Nothing historical is touched: P5, P5X and P5Y-K1 stay PARTIAL; the 369-cell SR PS1
campaign, its 10,332 obligations and its final assembly are inherited PASS and immutable;
the historical CUSUM completion records (including the five m=5 failures) stay exactly as
they are; P5X-T3 is not modified.

## Layout

    config/DOMAIN_COVER.json          gap-free composition + endpoint ownership
    config/B1_ADMISSION_CONTRACT.json outcome-independent admission tree + frozen fallback
    config/CUSUM_BRIDGE_PLAN.json     exact 2-cell partition, gates, host contract
    config/SR_BRIDGE_PLAN.json        exact 6-cell partition, rho cap, AWS-only contract
    config/COST_CAP.json              150 CPU-h cap, zero consumed
    config/CHECKPOINT.json(+_HASH)    binds every artifact, identity and kill gate
    config/SOURCE_MANIFEST.json(+_HASH)
    code/make_k1r_frozen.py           deterministic generator for all of the above
    tests/test_k1r_preregistration.py 12 self-checks
    ops/preflight.py                  cheap read-only preflight

## Status

Preregistration only. No production has run: `production_started = false`,
`consumed_new_cpu_h = 0.0`, and the namespace holds no results. K1 remains PARTIAL.
