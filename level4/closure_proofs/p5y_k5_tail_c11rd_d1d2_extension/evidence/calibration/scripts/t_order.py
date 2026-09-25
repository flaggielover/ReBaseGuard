import sys, time
from fractions import Fraction as F
sys.path.insert(0, "/Users/suzhe/ReBaseGuard-k5c11rd/level4/closure_proofs/p5y_k5_tail_c11rd_d1d2_extension/code")
import c11rd_float as FL, c11rd_kernel as KR
E_LO = F(5, 2); E_HI = F(5, 2) + F(108337, 1250000)     # NON-TARGET
prop = FL.propose(float((E_LO + E_HI) / 2), n=8, n4=8, ns=11, nt=11)
cands = [FL.exact_candidate(prop["basis"], c) for c in prop["coeffs"]]
for N in (4, 5, 6):
    for (s, th, lab) in (((F(31, 8), F(4)), (F(3, 4), F(1)), "depth1-worst"), ((F(15, 4), F(4)), (F(7, 8), F(1)), "uniform 1/4x1/8"),
                         ((F(15, 4), F(31, 8)), (F(15, 16), F(1)), "uniform 1/8x1/16")):
        bx = KR.Box(3, s, (E_LO, E_HI), theta=th, order=N)
        t = time.time(); R = KR.residuals_box(bx, cands); dt = time.time() - t
        print(f"N={N} {lab:18s} {dt:5.1f}s  r0 {float(R['r0'].abs_upper()):.2e} r1 {float(R['r1'].abs_upper()):.2e} r2 {float(R['r2'].abs_upper()):.2e}", flush=True)
