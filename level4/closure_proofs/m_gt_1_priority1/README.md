# Level-4 Priority 1: general Stage-D `m > 1` derivative closure

This isolated campaign proves the derivative theorem for the ordinary Stage-D
stopping time and exact truncated window `w=min(m,tau)`. It preserves the
historical partial campaign in the parent directory and treats Track 1B as
immutable prior evidence only.

The package contains:

- source-level definition audit;
- standalone theorem and human proof;
- independent frozen Gaussian CUSUM Monte Carlo correspondence;
- an independent compiled Lean proof spine;
- a rigorous Arb certificate for a pre-frozen exact finite-support witness;
- cross-representation and inheritance audits;
- focused regression gates and a five-category closure report.

Run the focused campaign with:

```bash
bash level4/closure_proofs/m_gt_1_priority1/reproduce.sh
```

## Evidence boundary

The frozen Gaussian CUSUM results for `m=1,2,3,5` are empirical numerical
correspondence. Rigorous Arb intervals apply only to the exact finite-support
stopped-process witness. A campaign verdict of `CLOSED` must not be read as
interval certification of frozen Gaussian `GammaTilde_m` values for `m>1`.
