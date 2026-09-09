# P5Y K1 SR — compute-cap-authorized successor

**Status: FROZEN PRE-RESULT CHECKPOINT. PRODUCTION IS OFF.**

Binding machine-readable protocol: `config/protocol.json`
Protocol hash: see `config/PROTOCOL_HASH`.

## What this campaign is

A **new** governed campaign that runs the *already-qualified, unchanged* frozen
scientific scope under a **pre-authorized compute budget**. It is additive. It is
not a repair, and it overturns nothing.

The only governance change is the compute cap. Every scientific quantity is
inherited verbatim.

## What is NOT changed

| | |
|---|---|
| SR scope | 316 cells, m ∈ {1,2,3,5}, 3994 live patches, 83452 panels |
| executable cover | the exact 316-cell cover, nothing added/removed/reordered |
| census | 46 distinct candidates, 102 certified contracts, shifts {0:43,1:35,2:20,3:4} |
| obligation universe | 8849 |
| degrees | D = 11, Z = 20, cand_degree = 16 |
| precision | 256 bits |
| backend | O9 accepted (baseline routes O4, O5, O7; O6 rejected) |
| certificate semantics | unchanged |
| thresholds | unchanged |
| K1 meaning | unchanged |
| historical verdicts | P5 = PARTIAL, P5X = PARTIAL, K1_INCOMPLETE_BUDGET — all stand |

The prior cost-blocked successor remains historically true: *under the 1126 CPU-h
cap*, SR backend optimization was exhausted. This campaign does not dispute that.
It authorises a different budget.

## The one governance change

```
superseded, immutable, never reused :  1848 CPU-h  ->  1126 CPU-h
this campaign's pre-authorized cap  :  4500 CPU-h
```

Derived quantitatively in `evidence/cap_derivation.json`, **before any production
result was observed**:

| step | CPU-h | rationale |
|---|---|---|
| cost basis (dense-random candidate, 16 workers) | 2946.95 | conservative over the candidate mix |
| + CUSUM cover allowance | 3153.04 | inheritable, but budgeted so a re-run is never budget-blocked |
| × 1.15 frozen campaign overhead | 3625.99 | certificate emission + per-cell setup; the frozen factor, reused |
| × 1.05 timing variance | 3807.29 | measured replicate variance ≤ 0.44% CPU / ≤ 3.03% throughput |
| + retry / bounded resume (2 events × 16 in-flight cells) | 4174.48 | resume granularity is one cell |
| × 1.02 assembly / verification | 4257.97 | ledger, manifest, re-hash, audit |
| **selected clean cap** | **4500** | 5.7% above the derived requirement |

Expected utilisation: **60.6%** on the real-candidate basis, **94.6%** on the
adversarial dense basis. The cap binds only in the adversarial case.

### Why the basis is the *dense* candidate

The census has 46 distinct candidates; only two candidate types were measured.
The genuine production F_0 candidate is **1.360× cheaper** than the protocol's own
declared dense-random benchmark, because its Chebyshev coefficients decay and FLINT
does less limb work. Basing a cap on the cheaper of the two is exactly how the
previous cap became insufficient, so the conservative basis is used.

## Execution contract

- **16 workers**, one per distinct physical core (`taskset -c 0..15`)
- SMT is **not qualified**: 24 workers is dominated by 16 on both axes; 32 workers
  costs +80.5% CPU-hours for only 9.2% less wall time
- nested threading forced to 1 for all six of OMP / OPENBLAS / MKL / NUMEXPR /
  BLIS / VECLIB; every worker verifies this and refuses to certify otherwise
- FLINT threads = 1
- projected: **5.67 d / 2166.5 CPU-h** (real basis), **7.70 d / 2946.95 CPU-h** (dense basis)
- 16-worker parallel efficiency 90.5%

Production refuses to start unless the live runtime contract hash equals
`d49f043755ef658a60e3c4017022ddecf0642a087a6e5bb0c1f2aefbe9721191`
(OpenBLAS runtime kernel SkylakeX, FLINT 3.6.0, python-flint 0.9.0, 256 bits, and
the four backend library sha256s). The kernel binds because SkylakeX vs Haswell
changes 62 of 240 certified dyadic candidates on one host.

## Disclosed before results: the O9 error-channel observation

O9's error channel is **smaller** than the accepted baseline's by at most
`1.25e-75` relative (≈ 2⁻²⁴⁸), measured exactly via dyadic mantissa/exponent over
88 comparisons on both candidate types.

This is a **tightening, not a loosening** — matrix products perform fewer rounding
steps than long scalar accumulation chains, the same effect already adjudicated in
`p5y_k1_sr_backend_cost_audit/adjudication/AUDIT_ADJUDICATION.json`. 256-bit unit
roundoff is 2⁻²⁵⁶ and the smallest governing threshold is 4.0e-2, so the effect is
~73 orders of magnitude below anything that binds.

Consequence, stated plainly: the predecessor protocol's literal criterion
`error_channel >= predecessor` holds only **up to 256-bit rounding**, not strictly.
It is recorded here rather than smoothed over, and **no threshold, bound or
semantic is changed to accommodate it**.

## Stop conditions

Cumulative CPU-hours reach the cap (the cap is never raised mid-campaign);
runtime contract mismatch; any thread variable ≠ 1; **any scientific obligation
failure — stop, never retry, never adjust a threshold**; any protected predecessor
tree hash change; producer-identity disagreement; wall clock > 14 days; free disk
< 5 GiB.

## Resume

Granularity is **one cell**. A cell is re-run from scratch unless a complete record
exists whose producer identity *and* runtime contract hash match the current
process. Partial cell state is never composed. Infrastructure failures retry at
most twice per cell; a scientific failure is never retried.
