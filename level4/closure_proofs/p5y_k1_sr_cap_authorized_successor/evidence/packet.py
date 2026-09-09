"""FROZEN benchmark packet for the SR worker-count scaling study.

Representative of the accepted O9 production hot path:
  * real patch geometry from the three FROZEN benchmark cells of
    p5y_k1_sr_backend_cost_audit/config/frozen_audit.json
      A_reference (17,11), B_max_span (0,0), C_sliver_heavy (63,63)
  * real panels from each patch's frozen p1 panel rule
  * the GENUINE production F_0 candidate (task1_f0.build_candidate): a
    collocation solve rounded to exact dyadic Chebyshev coefficients --
    not a random synthetic matrix
  * real Rbig (= P . Hankel(N)) and real Qflat
  * all relevant moment shifts 0,1,2,3
  * accepted O9 contraction ordering, 256-bit certified interval arithmetic
  * production inner loop: build Rbig once per panel, then contract the
    certified contract count against it (Rbig is panel-only work)

Nothing here changes scope, degree, precision, thresholds or semantics.
"""
import sys, json
from pathlib import Path
ROOT = Path("/home/ubuntu/work/ReBaseGuard")
NS   = ROOT/"level4/closure_proofs/p5y_k1_sr_backend_cost_audit"
T1R  = ROOT/"level4/closure_proofs/p5y_k1_task1r_budget_harness"
BIND = ROOT/"level4/closure_proofs/p5y_k1_binding_campaign/task1"
for p in (str(NS/"code"), str(T1R/"code"), str(BIND),
          str(ROOT/"level4/closure_proofs/p5x_global_nonlinear_dynamics/compute_optimization_r3_sr_symbolic"),
          str(ROOT/"rebaseguard-proof/src")):
    if p not in sys.path: sys.path.insert(0, p)

from flint import arb, arb_mat, ctx
import harness as H, sr_local as L, opt_backend as OB
from rebaseguard_certify.arb_backend import rational

par = json.loads((T1R/"config/frozen_parameters.json").read_text())["selection"]
D, Z = par["D_selected"], par["Z_selected"]
ctx.prec = H.PROD_BITS

PATCHES  = [(17,11), (0,0), (63,63)]     # frozen benchmark cells
N_PANELS = 4                              # distinct real panels per patch
SHIFTS   = [0,1,2,3]                      # all relevant moment shifts
CONTRACTS_PER_PANEL = 102                 # certified contract count per panel
n, Dp, Zp = H.CAND_DEGREE+1, D+1, Z+1

def geom_for(patch, e):
    A,b,c = L.sr_constants(); geo = L.patch_geometry(*patch, grid=H.GRID)
    p_c=(geo["yp"][0]+geo["yp"][1])/arb(2); m_c=(geo["ym"][0]+geo["ym"][1])/arb(2)
    Hh=(geo["yp"][1]-geo["yp"][0])/arb(2); U_c,L_c = c-p_c, m_c-c
    return dict(A=A,b=b,c=c,e=e,geo=geo,p_c=p_c,m_c=m_c,H=Hh,U_c=U_c,L_c=L_c,span=U_c-L_c)

class ShiftedDrift:
    """PanelDrift with the Hankel moment block shifted by m. Same build,
    same dimensions, same semantics -- only the moment index moves."""
    __slots__=("R","N0","shared")
    def __init__(self, shared, N, m):
        Zl = shared.Z
        Hank = arb_mat(Zl+1, Zl+1)
        for k1 in range(Zl+1):
            for k2 in range(Zl+1):
                Hank[k1,k2] = N[k1+k2+m]
        self.R = shared.P*Hank
        self.N0 = N[m].abs_upper()
        self.shared = shared

def real_candidate():
    """The GENUINE production F_0 candidate: exact dyadic Chebyshev coefficients."""
    A,b,c = L.sr_constants()
    e = rational(H.E_NUM, H.E_DEN)
    from task1_f0 import build_candidate
    return build_candidate(float(b), float(c), float(e))[0]

def dense_random_candidate(s=1):
    """The protocol's declared DENSE control candidate (seeds 0-5)."""
    import random; random.seed(s)
    return [[arb(random.randint(-50,50))/arb(97) for _ in range(n)] for _ in range(n)]

def build_contexts():
    """The frozen list of (patch, panel, shift) drift contexts."""
    e = rational(H.E_NUM, H.E_DEN)
    out = []
    for patch in PATCHES:
        g = geom_for(patch, e)
        p1 = H.p1_rule(g["H"], g["span"]); n_z = p1["n_panels"]
        Hh = g["H"]; h = g["span"]/(arb(2)*arb(n_z))
        ctxt = (Hh,h,D,Z,[Hh**a for a in range(2*D+2)],[h**k for k in range(2*Z+2)])
        L_c = g["L_c"]
        # 4 real panels spread across the patch's real panel range
        idxs = sorted({int(round(t*(n_z-1)/(N_PANELS-1))) for t in range(N_PANELS)})
        for kp in idxs:
            z_lo = L_c + arb(2)*h*arb(kp); z_hi = z_lo + arb(2)*h
            z_c  = (z_lo+z_hi)/arb(2)
            sh = OB.PanelShared(g["p_c"], g["m_c"], z_c, g["b"], ctxt)
            Nf = H.panel_moments(z_lo, z_hi, z_c, e, 2*Z+4, h)
            for m in SHIFTS:
                pd = OB.PanelDrift(sh,Nf) if m==0 else ShiftedDrift(sh,Nf,m)
                out.append(dict(patch=patch, panel=kp, shift=m, pd=pd, sh=sh, n_z=n_z))
    return out

def build_Rbig(pd):
    Rb = arb_mat(n, Dp*Zp)
    for i in range(n):
        base = i*Dp
        for a in range(Dp):
            for k in range(Zp): Rb[i, a*Zp+k] = pd.R[base+a, k]
    return Rb

def absvecs_of(shx):
    mW=arb_mat(n,1); eW=arb_mat(n,1); zW=arb_mat(n,1)
    for j in range(n): mW[j,0]=shx.magW[j]; eW[j,0]=shx.exW[j]; zW[j,0]=shx.ezW[j]
    return mW,eW,zW

def contract_O9(pd, cand, Rbig, absvecs):
    """ACCEPTED O9 ordering, verbatim from the accepted successor."""
    s = pd.shared
    C=arb_mat(n,n); Ca=arb_mat(n,n)
    for i in range(n):
        for j in range(n):
            C[i,j]=cand[i][j]; Ca[i,j]=arb(cand[i][j].abs_upper())
    Ct=C.transpose()
    Sbig=Ct*Rbig
    SA=arb_mat(Dp,n*Zp)
    for j in range(n):
        for a in range(Dp):
            off=a*Zp
            for k in range(Zp): SA[a,j*Zp+k]=Sbig[j,off+k]
    OUT=SA*s.Qflat
    coef=[[OUT[a,bq] for bq in range(Dp)] for a in range(Dp)]
    magW,exW,ezW=absvecs
    t1=Ca*magW; t2x=Ca*exW; t2z=Ca*ezW
    ex=ez=arb(0)
    for i in range(n):
        ex+=s.exV[i]*t1[i,0]+s.magV[i]*t2x[i,0]
        ez+=s.ezV[i]*t1[i,0]+s.magV[i]*t2z[i,0]
    return coef, ex*pd.N0, ez*pd.N0
