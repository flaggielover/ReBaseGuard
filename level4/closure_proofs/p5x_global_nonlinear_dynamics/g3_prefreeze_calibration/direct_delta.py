"""Direct-residual delta, as measured in the B2 direct-residual audit.

delta(G) = sup|r| + (1/G) * (w_plus + w_minus),  w = Bernstein-bounded gradient.
Diagnostic calibration only; no new architecture.
"""
from __future__ import annotations
import sys
from pathlib import Path
from flint import arb
NS = Path(__file__).resolve().parents[1]
for p in (NS/"sr_full_cell_prototype", NS/"compute_optimization_r6_minimal_evaluator",
          NS/"compute_optimization_r4_xi_reformulation", NS/"b2_basis_feasibility_audit",
          NS/"compute_optimization_r8_sr_certification",
          Path(__file__).resolve().parents[5]/"rebaseguard-proof"/"src"):
    if str(p) not in sys.path: sys.path.insert(0, str(p))
import bernstein as BB, sr_prototype as SP, r8_certify as R8
from minimal_evaluator import live_limits
from rebaseguard_certify.arb_backend import gaussian_cdf

def hull(M):
    return (min(float(v.lower()) for r in M for v in r),
            max(float(v.upper()) for r in M for v in r))

def prep(coef):
    n = len(coef)-1
    beta = BB.mono_to_bern_2d(coef)
    bN = R8.elevate2d(beta, n, 32)
    gxh = hull([[arb(32)*(bN[i+1][j]-bN[i][j]) for j in range(33)] for i in range(32)])
    gyh = hull([[arb(32)*(bN[i][j+1]-bN[i][j]) for j in range(32)] for i in range(33)])
    gh = hull(beta)
    ep = (min(float(beta[n][j].lower()) for j in range(n+1)),
          max(float(beta[n][j].upper()) for j in range(n+1)))
    em = (min(float(beta[i][n].lower()) for i in range(n+1)),
          max(float(beta[i][n].upper()) for i in range(n+1)))
    return {"beta":beta,"gxh":gxh,"gyh":gyh,"gh":gh,"ep":ep,"em":em,"n":n}

def grad_widths(pre, i, j, e, A, G):
    n = pre["n"]
    x0,x1 = arb(i)/arb(G), arb(i+1)/arb(G)
    y0,y1 = arb(j)/arb(G), arb(j+1)/arb(G)
    zp = (x0+x1)/arb(2) + ((x1-x0)/arb(2))*arb(0,1)
    zm = (y0+y1)/arb(2) + ((y1-y0)/arb(2))*arb(0,1)
    l,u = live_limits(zp,zm,A); wp,wm = arb(1)/A+zp, arb(1)/A+zm
    TP = (arb(2)*arb.pi()).sqrt()
    IEp = (-e).exp()*(gaussian_cdf(u+e-arb(1))-gaussian_cdf(l+e-arb(1)))
    IEm = ( e).exp()*(gaussian_cdf(u+e+arb(1))-gaussian_cdf(l+e+arb(1)))
    sub = BB.restrict_cell(pre["beta"], x0,x1,y0,y1)
    sdx = [[arb(n)*(sub[a+1][b]-sub[a][b]) for b in range(n+1)] for a in range(n)]
    sdy = [[arb(n)*(sub[a][b+1]-sub[a][b]) for b in range(n)] for a in range(n+1)]
    gxw = hull(sdx)[1]-hull(sdx)[0]; gyw = hull(sdy)[1]-hull(sdy)[0]
    Kxw = pre["gxh"][1]*float(IEp.upper()) - pre["gxh"][0]*float(IEp.lower())
    Kyw = pre["gyh"][1]*float(IEm.upper()) - pre["gyh"][0]*float(IEm.lower())
    fu = (-(u+e)*(u+e)/arb(2)).exp()/TP/wp
    fl = (-(l+e)*(l+e)/arb(2)).exp()/TP/wm
    bv = lambda hl, lim, f: [(hl[k]-x)*ff for k in (0,1)
                             for x in (float(lim.lower()), float(lim.upper()))
                             for ff in (float(f.lower()), float(f.upper()))]
    bu = bv(pre["ep"], u, fu); bl = bv(pre["em"], l, fl)
    return gxw+Kxw+(max(bu)-min(bu)), gyw+Kyw+(max(bl)-min(bl))
