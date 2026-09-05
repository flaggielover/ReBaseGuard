# Binding error algebra and ledger ownership

This is a NEW governed specification, not a finding that the old checkpoint
already prescribed this mapping. Numerical allocations, scope and thresholds
are preserved. Exclusive ownership below supersedes ambiguous ownership only
for this namespace. No historical failure is converted to a pass.

## 1. Objects, norms and exact residual identities

All state norms below are sup norms on a certified invariant reachable domain
containing x0 and all continuation images. Patch bounds must exhaust this domain;
a certificate on patch (17,11) alone does not bound the resolvent source globally.
C is a proven UPPER bound on ||(I-K_e)^-1|| for every e in the declared cell,
computed using its left endpoint. K and its derivatives use the raw-variable
Gaussian kernel on e-free state limits; there are no omitted e-boundary terms.
Use K_j = d_e^j K, k_j >= sup_cell ||K_j||. k0 <= 1, k1 <= 2 phi(0),
k2 <= 4 phi(1) follow by integrating |phi|, |phi'|, |phi''| over the whole real
line, which bounds the killed integral. These are bounds, not empirical fits.

Choose exact dyadic candidate functions Fhat_r, Dhat_r and source candidates
Shat_r, S1hat_r. Do not identify a float collocation vector with any of these
certified functions. With true F_r=(I-K)^-1 S_r and D_r=F'_r,

    rF_r = (I-K)Fhat_r - Shat_r
    rD_r = (I-K)Dhat_r - K_1 Fhat_r - S1hat_r
    (I-K)(Fhat_r-F_r) = rF_r + (Shat_r-S_r)
    (I-K)(Dhat_r-D_r) = rD_r + K_1(Fhat_r-F_r) + (S1hat_r-S'_r).

Let deltaF_r, deltaD_r bound the COMPLETE indicated residuals, including
operator evaluation, tails, endpoint slivers, polynomial range errors and
arithmetic already inside the residual enclosure. Source errors are epsS_r and
epsS1_r. Then

    epsF_r = C*(deltaF_r + epsS_r)
    epsD_r = C*(deltaD_r + k1*epsF_r + epsS1_r).

These follow by applying the resolvent and triangle inequalities to the exact
identities. Bounds are inequalities, not equalities for the unknown true errors.
An interval may be tighter only if a proved enclosure of the same expression
preserves every dependency. No source uncertainty may silently become zero.
For r=0, S0=phi(u+e)-phi(l+e), S0'=- (u+e)phi(u+e)+(l+e)phi(l+e) are closed
forms; their numerical enclosures still have arithmetic/tail radii.

A residual with the TRUE interval source already incorporated may instead use
C*delta_complete. It must carry inclusion evidence for each source dependency,
and the corresponding separate epsS term MUST be zero in the accounting DAG
because it is INCLUDED, not because the error vanishes. This does not change
STYLE_1 below: it is merely a residual certificate representation with the same
canonical expanded dependency expression. The implementation must normalize
back to the expanded dependency provenance before accepting the record.

## 2. Source and finite-power dependencies (orders zero through two)

Define J_e=K_raw,e=K_z,e+e K_e. As an operator under fixed limits,

    J_0 f = integral f(q(x,z)) (z+e) phi(z+e) dz
    J_1 f = integral f(q(x,z)) (1-(z+e)^2) phi(z+e) dz
    J_2 f = integral f(q(x,z)) ((z+e)^3-3(z+e)) phi(z+e) dz.

Use certified operator norm bounds j_k over the whole cell; rigorous whole-line
absolute Gaussian moments are admissible. Do not use sampled operator norms.
Freeze the following exact Leibniz recurrences:

    h_1 = 1-K 1;  h_1'=-S0; h_1''=-S0'
    h_r^(k) = sum_{i=0}^k binom(k,i) K_i h_(r-1)^(k-i), r=2..4
    S_r^(k) = sum_{i=0}^k binom(k,i) J_i h_r^(k-i), r=1..4
    W_(r,0)^(k) = S_r^(k)
    W_(r,j+1)^(k) = sum_{i=0}^k binom(k,i) K_i W_(r,j)^(k-i).

Here k=0,1,2; W_(r,j)=K^j S_r. Only j<=3 and r+j<=3 are needed in finite
all-m sums. The source bundle also computes h derivatives and S derivatives
needed by all five resolvent objects. It cannot substitute finite differences.

For any such operator sum Y=sum_i b_i T_i X_i, with approximate inputs and a
certificate lY for ||Yhat-sum_i b_i T_i Xhat_i||, propagate

    epsY <= lY + sum_i |b_i| ||T_i|| epsX_i.

The local certificate lY includes approximation to the TRUE operator applied to
the chosen input candidates. If an implementation instead certifies a numerical
operator That, it MUST include ||(T-That)Xhat|| in lY. Do not subsequently add
that same operator error again. Each edge has a source id, destination id,
derivative order, coefficient, norm bound, local-certificate ids and owner.

For a finite-power step this gives explicitly

    epsW_next,0 <= l0 + k0*epsW0
    epsW_next,1 <= l1 + k0*epsW1 + k1*epsW0
    epsW_next,2 <= l2 + k0*epsW2 + 2*k1*epsW1 + k2*epsW0.

This includes all finite kernel-power uncertainties, not merely F and dF.
Shared h/S/F certificates are computed once. Reuse does not erase a distinct
mathematical propagation path. Adding a tagged edge twice is forbidden.

## 3. Curvature obligation, distinct from the source object S_2

M_R2(D,cell,m) must be a NONNEGATIVE certified upper bound for
sup_{e in cell}|R''_(D,m)(e)|. It is not a stochastic second moment (K3 remains
out of scope), not the DAG object S_2, and not a pointwise second derivative.
No finite-difference estimate or historical g-variable curvature certificate
can substitute for this current raw-variable, all-m, whole-cell obligation.

A fixed sufficient certificate construction is differentiation twice:

    (I-K) F_r'' = K_2 F_r + 2 K_1 D_r + S_r''.

For a candidate Hhat_r, the complete second-derivative residual rH_r is
(I-K)Hhat_r-K_2 Fhat_r-2 K_1 Dhat_r-S2hat_r. On the WHOLE CELL,

    epsH_r <= C*(deltaH_r+k2*epsF_r+2*k1*epsD_r+epsS2_r).

All quantities on this right-hand side must be uniform cell bounds, not the
midpoint versions used for R_interval and D_interval. A state-only dyadic
candidate may be constant in e over the cell; its interval-e residual must
bound the true operator throughout the cell. This fixes an admissible
construction without requiring an unproved bootstrap closure condition.
No candidate degree increase or precision escalation is licensed. A loose bound
may fail .050; the geometry rule alone does not promise a successful certificate.

Let H_r_interval(cell) enclose F_r''(x0,e) uniformly, and let W2_(r,j)_interval
be the second-order finite-power enclosures above. Assemble their exact positive
coefficients (§4) to an R2_interval(cell); take M_R2=mag(R2_interval(cell)).
Rounding in these intervals is included in M_R2 and must not be charged again.
A failed or unaffordable curvature construction stops qualification; replacing
this scientific construction requires a new governed disposition.

CURRENT IMPLEMENTATION: neither the CUSUM raw kernel nor the SR production
kernel emits these whole-cell raw-variable certificates. The order-2 source,
resolvent and finite-power machinery is an IMPLEMENTATION_DEPENDENCY, and its
cost is unmeasured. The reference algebra in code/algebra.py is not that kernel.

## 4. Exact all-m assembly and correspondence

Set c_(m,t)=1/t-1/m and W_(r,j)=K^j S_r. For derivative order k=0,1,2,

    R_m^(k) = (1/m) sum_(r=0)^(m-1) F_r^(k)(x0)
               + sum_(t=1)^(m-1) c_(m,t) sum_(r=0)^(t-1) W_(r,t-r-1)^(k)(x0).

This comes from the parent raw-variable formula: -1/m from removing short
stopping times plus +1/t from their convention-A restoration. Coefficients
are e-independent exact rationals, so differentiation changes only objects.

| m | Resolvent part, each order k | Finite part, each order k |
|---|---|---|
| 1 | F_0^(k) | 0 |
| 2 | (F_0^(k)+F_1^(k))/2 | W_(0,0)^(k)/2 |
| 3 | (F_0^(k)+F_1^(k)+F_2^(k))/3 | 2 W_(0,0)^(k)/3 + (W_(0,1)^(k)+W_(1,0)^(k))/6 |
| 5 | sum_(r=0)^4 F_r^(k)/5 | 4 W_(0,0)^(k)/5 + 3(W_(0,1)^(k)+W_(1,0)^(k))/10 + 2(W_(0,2)^(k)+W_(1,1)^(k)+W_(2,0)^(k))/15 + (W_(0,3)^(k)+W_(1,2)^(k)+W_(2,1)^(k)+W_(3,0)^(k))/20 |

k=0 at e0 produces R_interval; k=1 at e0 produces D_interval; k=2 on the cell
produces R2_interval and M_R2. For scalar symmetric candidate errors,

    epsR_m <= sum_r epsF_r/m + sum_(t,r) c_(m,t)*epsW_(r,t-r-1),0 + etaR
    epsD_m <= sum_r epsD_r/m + sum_(t,r) c_(m,t)*epsW_(r,t-r-1),1 + etaD.

etaR and etaD are any arithmetic/candidate-evaluation errors not yet included.
Interval addition and scaling use outward arithmetic; shared-source dependency
may widen a result but never licenses deleting a summand. Per-m gates are
independent: budgets are neither pooled over m nor multiplied by four. No sum
of 19 standalone percentages is a valid all-m ledger.

## 5. Exactly one Taylor representation: STYLE_1

For the EXACT cell midpoint e0 and actual radius rho, put Delta=cell-e0.
R_interval and D_interval already contain ALL their certified uncertainty:

    R(cell) subset R_interval + Delta*D_interval
                   + [-rho^2*M_R2/2, +rho^2*M_R2/2].
    W_cover_exact = rho*mag(D_interval) + rho^2*M_R2/2
    W_cover = outward_upper(W_cover_exact).

Any final rounding introduced by evaluating this scalar upper bound belongs
inside W_cover (cover_arithmetic). No independent rho*epsD charge is allowed.
Likewise R_interval already includes epsR: never add epsR to it a second time.
With exact rational endpoints, reference interval arithmetic is exact; a real
Arb implementation must preserve containment when exporting its endpoints.

For explanatory reporting ONLY, choose D_center=mid(D_interval), radius d:
nominal first order = rho*|D_center|; derivative uncertainty = rho*d; curvature
= rho^2*M_R2/2. Their sum is exactly W_cover_exact for a symmetric interval.
These are child breakdowns of ONE cover charge, not extra top-level charges.
F uncertainty through K', derivative source error, all-m derivative arithmetic,
and derivative endpoint error all live inside D_interval. Curvature uncertainty
lives inside M_R2. There is no additional interpolation error: the full cell
is enclosed by Taylor's theorem; endpoints, final clipping and rational flooring
are exact geometry operations. If an implementation adds interpolation, it is
outside this frozen method and must STOP.

The .050 allocation covers BOTH nominal variation and Taylor uncertainty.
This intent is explicit in parent §6's h|R'|+(h^2/2)S_2 description. This
successor makes it binding without claiming actual utilization <= .050 has
been verified. A small derivative share does not prove the total passes.

## 6. Top-level ownership: absolute units of R, no borrowing

Let deltaF_r be the F-equation local certificate decomposed into Task1R-style
channels q in {eq,trunc,tail,end,int,round}. Propagate each to R with C/m.
Source dependency errors epsS_r are kept separate. Define exact ledger usage:

    U_candidate,q = sum_(r<m) C*deltaF_(r,q)/m
    U_candidate = sum_q U_candidate,q
    U_kernel = sum_(r<m) C*epsS_r/m + sum_(t,r) c_(m,t)*epsW_(r,t-r-1),0
    U_rounding = etaR_round
    U_interval = etaR_interval
    U_other = 0
    U_cover = W_cover.

R_interval must enclose the assembled candidate center with uncertainty no
larger than the computed value-channel sum (or report and bound all widening
inside its designated channel). The full cell radius is bounded by
U_candidate+U_kernel+U_rounding+U_interval+U_other+U_cover, without adding
R_interval.radius again. A final outward addition radius not included earlier
belongs to U_interval. The cover upper-bound arithmetic belongs to U_cover.

| Line | Cap | Allowed claimants | Forbidden claimants |
|---|---:|---|---|
| B_candidate | .040 | F-equation local certificate's value contribution, including its nested harness errors | any dF, Taylor variation, external source dependency, reserve |
| B_kernel | .040 | h/S source-error recursion into F; complete value finite-power errors, including local kernel arithmetic already absorbed there | F-equation local certificate again; any derivative/curvature term |
| B_cover | .050 | complete STYLE_1 Taylor charge: nominal drift, all derivative uncertainty, curvature, cover arithmetic | a second derivative-radius charge; center-value uncertainty again; reserve |
| B_other | .040 | no nonzero claimant in this exact finite assembly; frozen unused | derivative equations (resolved to B_cover here), reserve transfer, unproved assembly remainder |
| B_rounding | .010 | value export/candidate evaluation rounding not already inside another value certificate | residual dyadic error already in B_candidate/B_kernel; derivative rounding |
| B_interval | .010 | value assembly/final addition arithmetic not already in input certificates | existing certificate radii; derivative or curvature arithmetic |
| B_resolvent | 0 | none; C is only multiplicative | additive resolvent charge |
| top reserve | .010 | none | every draw/redistribution |

Unused B_other is NOT made available to any other channel. This choice resolves
rather than hides the old 'assembly, derivative equation, hull' overlap: exact
finite assembly has no mathematical remainder, all numerical assembly error
has an explicit destination, and a hull across e-cells is an outer interval
union, never an independent error allowance or extra B_cover charge.

B_end is NOT a top-level allocation. Preserve the full nested B_candidate
partition: eq .018, trunc .006, tail .006, end .004, int .002, round .002,
reserve .002. The sum including unavailable reserve is .040. For every m,
U_candidate,q must pass its own cap, and U_candidate must pass .040. Additionally
the inherited SR per-(cell,patch) F-object endpoint gate C*deltaF_end<=.004
remains in force; no cross-patch borrowing. Other nested local F gates remain
at their Task1R cap too. All global residual norms must be certified over the
full reachable state set. Taking maxima of patch bounds is legitimate for a
sup norm; averaging different patches' budget excess is not.

The newly specified derivative channels do not inherit a fictional historical
Task1R dF qualification: Task1R certified only F_0. Their endpoint uncertainty
is within the .050 complete cover gate, with no claim on B_candidate/B_end.
No historical numerical threshold is increased. The new ownership is an
explicit prospective governance amendment, not a repair of a frozen ledger.

A primitive can influence R(e0) and its derivative. Those are DISTINCT Taylor
terms, so their propagated bounds may both occur legitimately. Unique ownership
applies to a contribution identified by (primitive certificate, propagation
path, destination quantity, derivative order), not to the primitive id alone.
This does not assume statistical independence; every inequality is deterministic.

The inherited LOCAL_GATE_BUDGET=.100 is retained as an additional local
constraint: delta_max=.100/C_cell_left and w_panel_max=.100/(C_cell_left*n_panels_patch),
using the worst assembly coefficient 1 attained at m=1. Local panels must
satisfy this gate and all stricter top/nested gates; local allowance never
licenses exceeding a final R-unit channel. P1 remains independently required.

## 7. Gating and incomplete evidence

Every nonnegative usage above must be <= its exact rational cap, all nested
gates must pass, and the final certified interval must lie strictly in (-2,2).
Failure to enclose the target inside (-2,2) is certificate failure unless a
separate bound proves a true violation; a wide interval alone is no scientific
counterexample. Missing dependency, curvature, cost or provenance gives
NOT_COMPUTED / IMPLEMENTATION_DEPENDENCY, not zero and not PASS.
The sum of allocated caps remains .190; .010 top reserve and .002 nested
reserve remain unavailable. No degree, precision, scope, P1, complexity,
CPU-limit or cell-splitting relaxation is permitted after freeze.
