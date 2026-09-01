"""EXPLORATORY (not a result): what does E[Rbar^2 | observables] look like?"""
import sys, pathlib
import numpy as np
R = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(R / "src"))
sys.path.insert(0, str(R.parent / "p7_statistical_consequences" / "src"))
from rebaseguard_p6c.chain import simulate_policy_chain
from rebaseguard_p6c.policy import ConstantPolicy

for det in ("cusum", "sr"):
    for m in (1, 3, 5):
        for rho in (0.2, 0.5, 1.0):
            res = simulate_policy_chain(
                detector=det, policy=ConstantPolicy(rho=rho, m=m),
                n_rep=400, n_cycles=200, burn_in=20, e0=0.0,
                rng=np.random.default_rng(11))
            e = res.post(res.e_start).ravel()
            zb = res.post(res.zbar).ravel()
            tau = res.post(res.tau).ravel()
            w = np.minimum(m, tau)
            rbar = e + zb
            # regression of rbar on zbar (through origin) and residual variance
            g = float((zb * rbar).sum() / (zb * zb).sum())
            resid = rbar - g * zb
            print(f"{det} m={m} rho={rho}: E[e^2]={np.mean(e**2):.3f} "
                  f"E[Rbar^2]={np.mean(rbar**2):.3f} g={g:.3f} "
                  f"Var(resid)={resid.var():.3f} corr(rbar,zb)={np.corrcoef(rbar,zb)[0,1]:.3f} "
                  f"sd(zb)={zb.std():.3f} P(tau<m)={np.mean(tau<m):.3f}")
        print()
