# 256 / 384 / 512-bit numerical diagnostic

The frozen successor recorded that a prior 256/384/512-bit comparison
existed only as narrative in committed inputs. This makes it concrete
for a small representative set.

DIAGNOSTIC ONLY. Production precision remains frozen at 256 bits.
Nothing here promotes, escalates or redefines it.

| cell | m | bits | mag D_interval | M_R2 | B_cover | worst top-level util |
|---:|---:|---:|---|---|---|---:|
| 0 | 1 | 256 | 19.4594215403 | 18099.1452056 | 0.00553014399156 | 11.3734% |
| 0 | 1 | 384 | 19.4594215403 | 18099.1452056 | 0.00553014399156 | 11.3734% |
| 0 | 1 | 512 | 19.4594215403 | 18099.1452056 | 0.00553014399156 | 11.3734% |
| 221 | 1 | 256 | 0.490988804903 | 354.110668235 | 0.00114094579842 | 6.71951% |
| 221 | 1 | 384 | 0.490988804903 | 354.110668235 | 0.00114094579842 | 6.71951% |
| 221 | 1 | 512 | 0.490988804903 | 354.110668235 | 0.00114094579842 | 6.71951% |

## Interpretation

The certified outputs are IDENTICAL at 256, 384 and 512 bits: same
`mag(D_interval)`, same `M_R2`, same `B_cover`, and the higher-precision
`R` and `D` enclosures are contained in the 256-bit ones. The
underlying local residual certificates DO move with precision, but only
at relative 1e-45 (384) and 1e-26 (512) -- twenty or more orders of
magnitude below the certificate values themselves (1e-6 to 1e-4).

So at the frozen production precision the certificate is
RESIDUAL-LIMITED, not rounding-limited: what bounds `M_R2` is the
quality of the candidate and of the whole-cell envelope, not the
arithmetic. Raising precision buys nothing here.

This concretely replaces the prior 256/384/512 comparison, which the
frozen successor recorded as existing only as narrative in committed
inputs, and it archives the per-precision records rather than asserting
them. It independently agrees with the committed near-zero diagnosis,
which reported the `dF_0` defect as bit-invariant across the same three
precisions.

No 256-bit certification failed while a higher precision succeeded.
PRODUCTION PRECISION REMAINS 256 BITS. Nothing here promotes it, and
`PRECISION_ESCALATION_ALLOWED` remains false.

Scope note: these runs certify the m=1 obligation, which the frozen
assembly makes exactly `R_1^(k) = F_0^(k)(x0)` with no finite-power
part, so the three equations F_0, D_0, H_0 plus the closed-form sources
are the whole of that obligation. m = 2, 3, 5 are certified at 256 bits
in the representative ledger, not at three precisions.
