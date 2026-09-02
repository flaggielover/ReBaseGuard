"""How does the certified residual degrade as the e-cell widens?"""
import sys, time
NS="/Users/suzhe/ReBaseGuard/level4/closure_proofs/p5x_global_nonlinear_dynamics"
sys.path.insert(0, NS+"/certificate")
from flint import arb
from rebaseguard_certify.arb_backend import workprec, rational
from rebaseguard_certify.polynomial import chebyshev_payload_to_power, bi_add, bi_scale
from rebaseguard_certify.residual import _max_abs_on_reachable, _phi_coefficients, _chebyshev_sup
from drift_certificate import solve_candidate, kernel_polynomials, reward_rho1

cand = solve_candidate(drift=0.25, degree=12, quadrature_order=400)
payload = cand.to_chebyshev_dyadic(scale_bits=50)
for rad_num, rad_den in ((0,1), (1,10**8), (1,10**6), (1,10**5), (1,10**4), (1,10**3), (1,100)):
    t=time.time()
    with workprec(256):
        ph=_phi_coefficients(50)
        g=chebyshev_payload_to_power(payload)
        eb=arb(rational(1,4), rational(rad_num,rad_den))
        kl,kh=kernel_polynomials(g, ph, eb, z_weight=0)
        rw=reward_rho1(ph, eb)
        rl=bi_add(bi_add(g,bi_scale(kl,-arb(1))),bi_scale(rw,-arb(1)))
        rh=bi_add(bi_add(g,bi_scale(kh,-arb(1))),bi_scale(rw,-arb(1)))
        mx,_=_max_abs_on_reachable(rl,rh,subdivision_depth=3)
    print(f"zeta-form  e = 1/4 +/- {rad_num}/{rad_den}  residual = {mx.str(6)}   [{time.time()-t:.0f}s]", flush=True)
