"""EXPLORATORY: functional form for Vhat = E[Rbar^2 | observables]."""
import sys, pathlib
import numpy as np
R = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(R / "src")); sys.path.insert(0, str(R.parent / "p7_statistical_consequences" / "src"))
from rebaseguard_p6c.chain import simulate_policy_chain
from rebaseguard_p6c.policy import ConstantPolicy

def report(det, m, rho):
    res = simulate_policy_chain(detector=det, policy=ConstantPolicy(rho=rho, m=m),
                                n_rep=600, n_cycles=300, burn_in=20, e0=0.0,
                                rng=np.random.default_rng(101))
    e = res.post(res.e_start).ravel(); zb = res.post(res.zbar).ravel()
    tau = res.post(res.tau).ravel().astype(float); w = np.minimum(m, tau)
    rbar = e + zb
    # linear-through-origin
    g = (zb*rbar).sum()/(zb*zb).sum(); r1 = rbar - g*zb
    # + cubic
    X = np.column_stack([zb, zb**3]); b = np.linalg.lstsq(X, rbar, rcond=None)[0]
    r2 = rbar - X@b
    # + 1/tau interaction on the linear term
    X3 = np.column_stack([zb, zb/np.sqrt(tau)]); b3 = np.linalg.lstsq(X3, rbar, rcond=None)[0]
    r3 = rbar - X3@b3
    # residual variance model
    y = r1**2
    Z = np.column_stack([np.ones_like(w), 1.0/w]); c = np.linalg.lstsq(Z, y, rcond=None)[0]
    Z2 = np.column_stack([np.ones_like(w), 1.0/w, 1.0/tau]); c2 = np.linalg.lstsq(Z2, y, rcond=None)[0]
    # how much does Vhat vary?  Jensen gap at nu = 1/m
    nu = 1.0/m
    V = (g*zb)**2 + np.maximum(c[0] + c[1]/w, 1e-6)
    Q = nu*V/(V+nu); Vbar = V.mean()
    gap = nu*Vbar/(Vbar+nu) - Q.mean()
    print(f"{det} m={m} rho={rho}: g={g:.4f} var(r1)={r1.var():.4f} var(r2)={r2.var():.4f} "
          f"var(r3)={r3.var():.4f} | s=({c[0]:.4f},{c[1]:.4f}) MSE={np.mean((y-Z@c)**2):.4f} "
          f"MSE3={np.mean((y-Z2@c2)**2):.4f}")
    print(f"    E[V]={Vbar:.4f} sd(V)={V.std():.4f} Q*(Vbar)={nu*Vbar/(Vbar+nu):.4f} "
          f"E[Q*(V)]={Q.mean():.4f} JensenGap={gap:.4f} ({100*gap/(nu*Vbar/(Vbar+nu)):.1f}%) "
          f"rho range=[{(nu/(V+nu)).min():.3f},{(nu/(V+nu)).max():.3f}] mean={(nu/(V+nu)).mean():.3f}")

for det in ("cusum","sr"):
    for m in (1,3,5):
        report(det,m,0.2)
    print()
