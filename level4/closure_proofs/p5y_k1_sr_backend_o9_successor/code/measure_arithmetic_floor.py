import sys, time, json
from pathlib import Path
ROOT=Path("/home/ubuntu/work/ReBaseGuard")
NS=ROOT/"level4/closure_proofs/p5y_k1_sr_backend_cost_audit"
T1R=ROOT/"level4/closure_proofs/p5y_k1_task1r_budget_harness"
for p in (str(NS/"code"),str(T1R/"code"),
          str(ROOT/"level4/closure_proofs/p5x_global_nonlinear_dynamics/compute_optimization_r3_sr_symbolic"),
          str(ROOT/"rebaseguard-proof/src")):
    if p not in sys.path: sys.path.insert(0,p)
from flint import arb, arb_mat, ctx
import harness as H, sr_local as L, opt_backend as OB
from rebaseguard_certify.arb_backend import rational
par=json.loads((T1R/"config/frozen_parameters.json").read_text())["selection"]
D,Z=par["D_selected"],par["Z_selected"]; ctx.prec=H.PROD_BITS
def geom_for(patch,e):
    A,b,c=L.sr_constants(); geo=L.patch_geometry(*patch,grid=H.GRID)
    p_c=(geo["yp"][0]+geo["yp"][1])/arb(2); m_c=(geo["ym"][0]+geo["ym"][1])/arb(2)
    Hh=(geo["yp"][1]-geo["yp"][0])/arb(2); U_c,L_c=c-p_c,m_c-c
    return dict(A=A,b=b,c=c,e=e,geo=geo,p_c=p_c,m_c=m_c,H=Hh,U_c=U_c,L_c=L_c,span=U_c-L_c)
def rnd_cand(s):
    import random; random.seed(s); n=H.CAND_DEGREE+1
    return [[arb(random.randint(-50,50))/arb(97) for _ in range(n)] for _ in range(n)]
patch=(17,11); e=rational(H.E_NUM,H.E_DEN)
g=geom_for(patch,e); p1=H.p1_rule(g["H"],g["span"]); n_z=p1["n_panels"]
Hh=g["H"]; h=g["span"]/(arb(2)*arb(n_z))
ctxt=(Hh,h,D,Z,[Hh**a for a in range(2*D+2)],[h**k for k in range(2*Z+2)])
L_c=g["L_c"]
sh=OB.PanelShared(g["p_c"],g["m_c"],L_c+h,g["b"],ctxt)
Nf=H.panel_moments(L_c,L_c+arb(2)*h,L_c+h,e,2*Z+4,h); pd=OB.PanelDrift(sh,Nf)
n=H.CAND_DEGREE+1; Dp=D+1; Zp=Z+1
cand=rnd_cand(1)
# REAL matrices
C=arb_mat(n,n)
for i in range(n):
    for j in range(n): C[i,j]=cand[i][j]
Ct=C.transpose()
Rbig=arb_mat(n,Dp*Zp)
for i in range(n):
    for a in range(Dp):
        for k in range(Zp): Rbig[i,a*Zp+k]=pd.R[i*Dp+a,k]
Sbig=Ct*Rbig
SA=arb_mat(Dp,n*Zp)
for j in range(n):
    for a in range(Dp):
        for k in range(Zp): SA[a,j*Zp+k]=Sbig[j,a*Zp+k]
def T(fn,reps=25):
    for _ in range(5): fn()
    ts=[]
    for _ in range(reps):
        t=time.process_time(); fn(); ts.append(time.process_time()-t)
    ts.sort(); return ts[len(ts)//2]
t1=T(lambda: Ct*Rbig); t2=T(lambda: SA*sh.Qflat)
floor=t1+t2
print("ARITHMETIC FLOOR WITH THE *REAL* MATRICES (256 bits, FLINT C-level):")
print(f"  Ct*Rbig   : {t1*1000:8.4f} ms")
print(f"  SA*Qflat  : {t2*1000:8.4f} ms")
print(f"  FLOOR     : {floor*1000:8.4f} ms per contract")
base=4.8594e-3; o9=3.9425e-3
print(f"\n  accepted baseline : {base*1000:.4f} ms")
print(f"  O9 (bit-exact)    : {o9*1000:.4f} ms   ({base/o9:.3f}x)")
print(f"  Python overhead in O9 : {(o9-floor)*1000:.4f} ms  ({100*(o9-floor)/o9:.1f}%)")
print(f"\n  MAX speedup with a PERFECT zero-overhead compiled kernel : {base/floor:.3f}x")
print(f"  REQUIRED                                                 : 3.75x")
PAN=83452; CELLS=316; OVER=1.15; CU=206.086; CAP=1126; NC=102
resid=CAP/OVER-CU
sr=NC*floor*CELLS*PAN/3600
print(f"\n  SR cost at the arithmetic floor : {sr:8.1f} CPU-h")
print(f"  residual SR allowance           : {resid:8.1f} CPU-h")
print(f"  shortfall AT THE FLOOR          : {sr/resid:8.2f}x")
print(f"\n  => even an infinitely fast interpreter leaves a {sr/resid:.2f}x deficit;")
print(f"     the binding constraint is FLINT 256-bit interval arithmetic itself.")
json.dump(dict(t1=t1,t2=t2,floor=floor,sr_floor=sr,resid=resid),open('/tmp/floor2.json','w'))
