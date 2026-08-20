# Gate 4.5-C2.4 checkpoint

## Route: elementary CONVEXITY (not dominated convergence, not the crude 2exp bound)

SCALAR FEASIBILITY CHECK (done first, per spec §6):
  H = h+k = 5.5, so 1-q = P(Z>5.5) ~ 1.9e-8, q ~ 1 - 1.9e-8.
  Hence d >= sqrt(q) ~ 1-9.5e-9 and c < 1/d, so we need M(2a) <= 1 + O(1e-8).
  => the crude bound E e^{t|Z|} <= 2 e^{t^2/2} (limit 2) is UNUSABLE. Rejected.

Winning inequality (convexity of exp on [0,u], theta = t/eps, u = eps|z|):
    e^{t|z|} = e^{theta*u + (1-theta)*0} <= theta e^u + (1-theta) <= 1 + (t/eps) e^{eps|z|}
Integrating against a probability measure:
    M_j(t) <= 1 + (t/eps) * M_eps      -> 1 as t -> 0, UNIFORMLY in j.
Only ONE one-step assumption is needed (finite moment at some radius eps>0).

## Explicit witnesses (all real, no rpow needed)
  qr := q.toReal in [0,1)
  dr := (1+qr)/2           -- then qr <= dr^2 (since (1-qr)^2 >= 0) and dr < 1
  cr := (1+dr)/(2*dr)      -- then cr > 1 and cr*dr = (1+dr)/2 < 1
  eta := cr^2 - 1 > 0
  t := min eps (eps*eta/(m+1)) where m := Meps.toReal ;  a := t/2

## Theorems planned
C2.4.1 exp_abs_le_convex, lintegral_expAbsScore_le, exists_rate_lintegral_le
C2.4.2 exists_pos_integrable_exp_abs_walkAt   (invokes frozen C2.3 directly)
C2.4.3 Gaussian: (G1) one-step moment via integrable_exp_mul_gaussianReal
                 (G2) q<1 via full support of gaussianPDF

## Status: GATE 4.5-C2.4 = PASS (fully verified)
C24_EXIT=0 | C23=0 | C1=0 | GATE45AB=0 | GATE4=0 | GATE3=0 | GATE2=0 | BUILD_EXIT=0
bypass scan clean | axioms = [propext, Classical.choice, Quot.sound]
No frozen file modified.
C2.4.1 exp_abs_le_convex, lintegral_expAbsScore_le, exists_rate_lintegral_le  -- DONE
C2.4.2 exists_pos_integrable_exp_abs_walkAt                                  -- DONE
C2.4.3 gaussExpMoment_ne_top, gaussianReal_Ioi_pos, gaussianReal_Iic_lt_one,
       exists_pos_integrable_exp_abs_walkAt_gaussian,
       exists_pos_integrable_exp_abs_walkAt_rebaseguard (k=1/2,h=5)          -- DONE
Gaussian q<1 and one-step moment are DERIVED from mu.map (X j) = gaussianReal 0 1.
Remaining: nothing for C2.4. Next gate would be C3.
