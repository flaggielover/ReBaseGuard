# C2b certifier: claim errata carried by the MB308 formal package

**Why this file exists.** REVIEW_C2B_STRATEGY_R1 (overnight namespace, preserved at `1ee93ac5`) condition C4 lists
six claim corrections to the C2b design documents. REVIEW_A0_CERTIFIER_R1 (research namespace) condition C5 notes
that stream A0 did not address them. The overnight namespace is immutable, so the formal package records them here.
The certificate code is unchanged. None of these errata changes a certified value, the checker, or its soundness
argument.

Sources: `OV = level4/closure_proofs/p5y_k5_tail_overnight_research`, `GEN = OV/streams/C_308/A0X/gen`.

| # | where (as cited by the review) | the claim as written | correction binding on this package |
|---|---|---|---|
| E1 | `GEN/STRATEGY.md:153-155` | a "w ≡ const" sanity check was run | No committed run of that check exists. The claim is **withdrawn**. The package relies on the FD, err-path, direction-swap and vertex-enclosure evidence of qualification case QC06 instead. |
| E2 | `GEN/STRATEGY.md` (the brute-force check) | a "5e-9 brute-force" quadrature check was run | `direct_quadrature` has no committed caller. The claim is **withdrawn**. |
| E3 | `GEN/C2B_ROUTE_SUMMARY.md:131` | "no bumps beyond 3" | The recorded maximum is **5 bumps**. The formal ladder does not use this path: its exact-scale selection bounds bumps by BUMP_MAX = 64. |
| E4 | `GEN/STRATEGY.md` §5.2 | the vertex values of K_e w are computed "exactly" | They are **rigorous enclosures**: lower and upper bounds at scale 2^-(P+Q). They are not exact values. |
| E5 | `GEN/STRATEGY.md:112` | the cross term of the interpolation bound, as written | Read it as **∑ λ_i \|d_s\| \|d_y\| ≤ r_s r_y / 4**, with absolute values. The code (`c2b_exact.hessian_bounds`: `err = ceil((Hss + 2 ry Hsy + ry^2 Hyy)/(8 N^2))`) already implements the corrected bound. |
| E6 | `GEN/A0_TIGHTNESS.md` §1 | the definition of W*_E | Define **W*_E as the minimal fixed point** of w = 1 + K_E w, which is the value-iteration limit from w = 0. |

**Scope.**
* These are statements about documents only.
* The formal campaign pins the C2b code by sha256 and git blob (`code/mb308_pinned.py`).
* Its Stage-1 pointwise ladder runs the C2b checker only through `code/mb308_a0core.py`.
