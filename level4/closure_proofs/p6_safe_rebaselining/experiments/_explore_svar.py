"""EXPLORATORY: does the residual variance scale like 1/w?  Fixed-point trace."""
import sys, pathlib
import numpy as np
R = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(R/"src")); sys.path.insert(0, str(R.parent/"p7_statistical_consequences"/"src"))
from rebaseguard_p6c.chain import simulate_policy_chain
from rebaseguard_p6c.policy import ConstantPolicy

for det in ("cusum",):
    for m in (3, 5):
        res = simulate_policy_chain(detector=det, policy=ConstantPolicy(rho=0.25, m=m),
                                    n_rep=800, n_cycles=250, burn_in=20, e0=0.0,
                                    rng=np.random.default_rng(5))
        e = res.post(res.e_start).ravel(); zb = res.post(res.zbar).ravel()
        tau = res.post(res.tau).ravel().astype(float)
        w = np.minimum(m, res.post(res.tau).ravel()).astype(float)
        rbar = e + zb
        X = np.column_stack([zb, zb/np.sqrt(tau)])
        b = np.linalg.lstsq(X, rbar, rcond=None)[0]
        r = rbar - X@b
        print(f"{det} m={m}: coef={b.round(4)}")
        for wv in sorted(set(w.tolist())):
            s = w == wv
            print(f"    w={int(wv)}: n={s.sum():7d} frac={s.mean():.4f} E[r^2]={np.mean(r[s]**2):.4f} "
                  f"(m/w)*E[r^2|w=m]={(m/wv)*np.mean(r[w==m]**2):.4f}")
