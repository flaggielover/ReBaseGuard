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
Nf=H.panel_moments(L_c,L_c+arb(2)*h,L_c+h,e,2*Z+4,h)
pd=OB.PanelDrift(sh,Nf)
n=H.CAND_DEGREE+1; Dp=D+1; Zp=Z+1

def build_Rbig(pd):
    """PANEL-ONLY re-layout of pd.R: Rbig[i, a*Zp+k] = R[i*Dp+a, k]. Pure copy."""
    Rb=arb_mat(n, Dp*Zp)
    for i in range(n):
        base=i*Dp
        for a in range(Dp):
            for k in range(Zp): Rb[i, a*Zp+k]=pd.R[base+a, k]
    return Rb

def contract_O9(pd, cand, Rbig, absvecs):
    """O9: batch the 'a' axis. Each output entry is the SAME inner product
    sum_i C[i,j]*R[i*Dp+a,k] as the accepted order -- the i-sum is untouched,
    so cancellation is preserved. Only the loop over 'a' is batched."""
    s=pd.shared
    C=arb_mat(n,n); Ca=arb_mat(n,n)
    for i in range(n):
        for j in range(n):
            C[i,j]=cand[i][j]; Ca[i,j]=arb(cand[i][j].abs_upper())
    Ct=C.transpose()
    Sbig = Ct * Rbig                      # ONE matmul: (n x n)(n x Dp*Zp)
    SA = arb_mat(Dp, n*Zp)                # re-layout: SA[a, j*Zp+k] = Sbig[j, a*Zp+k]
    for j in range(n):
        for a in range(Dp):
            off=a*Zp
            for k in range(Zp): SA[a, j*Zp+k]=Sbig[j, off+k]
    OUT = SA * s.Qflat                    # ONE matmul: (Dp x n*Zp)(n*Zp x Dp)
    coef=[[OUT[a,bq] for bq in range(Dp)] for a in range(Dp)]
    magW,exW,ezW=absvecs
    t1=Ca*magW; t2x=Ca*exW; t2z=Ca*ezW
    ex=ez=arb(0)
    for i in range(n):
        ex+=s.exV[i]*t1[i,0]+s.magV[i]*t2x[i,0]
        ez+=s.ezV[i]*t1[i,0]+s.magV[i]*t2z[i,0]
    return coef, ex*pd.N0, ez*pd.N0

def absvecs_of(sh):
    mW=arb_mat(n,1); eW=arb_mat(n,1); zW=arb_mat(n,1)
    for j in range(n): mW[j,0]=sh.magW[j]; eW[j,0]=sh.exW[j]; zW[j,0]=sh.ezW[j]
    return mW,eW,zW

Rbig=build_Rbig(pd); AV=absvecs_of(sh)
cands=[rnd_cand(s) for s in range(6)]
print("VALIDATION O9 vs accepted baseline:")
bitexact=True; overlap=True; maxrat=0.0; cons=True
for cd in cands:
    b,bex,bez=OB.contract(pd,cd); o,oex,oez=contract_O9(pd,cd,Rbig,AV)
    for a in range(Dp):
        for bq in range(Dp):
            x,y=b[a][bq],o[a][bq]
            if not(x.mid()==y.mid() and x.rad()==y.rad()): bitexact=False
            if x.lower()>y.upper() or y.lower()>x.upper(): overlap=False
            rb=float(x.rad())
            if rb>0: maxrat=max(maxrat,float(y.rad())/rb)
    if not(oex.abs_upper()>=bex.abs_upper()): cons=False
print(f"  Taylor coefficients bit-for-bit identical : {bitexact}")
print(f"  enclosures overlap                        : {overlap}")
print(f"  max radius ratio O9/baseline              : {maxrat:.6f}   (O6 was 23.549)")
print(f"  error channel conservative                : {cons}")
def T(fn,reps=15):
    for _ in range(3): fn()
    ts=[]
    for _ in range(reps):
        t=time.process_time(); fn(); ts.append(time.process_time()-t)
    ts.sort(); return ts[len(ts)//2]
tb=T(lambda:[OB.contract(pd,c) for c in cands],9)/len(cands)
t9=T(lambda:[contract_O9(pd,c,Rbig,AV) for c in cands],9)/len(cands)
tR=T(lambda: build_Rbig(pd),9)
print(f"\n  baseline per contract : {tb*1000:8.4f} ms")
print(f"  O9 per contract       : {t9*1000:8.4f} ms")
print(f"  Rbig build (panel-only, amortized over candidates): {tR*1000:.4f} ms")
for nc in (10,46,102):
    print(f"    amortized over {nc:>3} contracts/panel: {(t9+tR/nc)*1000:7.4f} ms -> speedup {tb/(t9+tR/nc):5.3f}x")
json.dump(dict(tb=tb,t9=t9,tR=tR,bitexact=bitexact,maxrat=maxrat),open('/tmp/o9.json','w'))
