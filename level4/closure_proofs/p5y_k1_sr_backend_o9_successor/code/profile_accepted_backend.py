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
cand=rnd_cand(1)
def T(fn,reps=20):
    for _ in range(3): fn()
    ts=[]
    for _ in range(reps):
        t=time.process_time(); fn(); ts.append(time.process_time()-t)
    ts.sort(); return ts[len(ts)//2]

# --- decompose contract() into its stages
def s_Cbuild():
    C=arb_mat(n,n)
    for i in range(n):
        for j in range(n): C[i,j]=cand[i][j]
    return C
C=s_Cbuild(); Ct=C.transpose()
def s_transpose(): return C.transpose()
def s_Ragather():
    out=[]
    for a in range(Dp):
        Ra=arb_mat(n,Zp)
        for i in range(n):
            row=i*Dp+a
            for k in range(Zp): Ra[i,k]=pd.R[row,k]
        out.append(Ra)
    return out
Ras=s_Ragather()
def s_SaMul():
    return [Ct*Ras[a] for a in range(Dp)]
Sas=s_SaMul()
def s_flatgather():
    out=[]
    for a in range(Dp):
        flat=arb_mat(1,n*Zp)
        Sa=Sas[a]
        for j in range(n):
            for k in range(Zp): flat[0,j*Zp+k]=Sa[j,k]
        out.append(flat)
    return out
flats=s_flatgather()
def s_Qmul(): return [flats[a]*sh.Qflat for a in range(Dp)]
def s_errchannel():
    ex=ez=arb(0)
    for i in range(n):
        ai,ei,zi=sh.magV[i],sh.exV[i],sh.ezV[i]
        for j in range(n):
            c=cand[i][j].abs_upper()
            if c.is_zero(): continue
            ex+=c*(sh.magW[j]*ei+ai*sh.exW[j]); ez+=c*(sh.magW[j]*zi+ai*sh.ezW[j])
    return ex,ez
def s_absbuild():
    Ca=arb_mat(n,n)
    for i in range(n):
        for j in range(n): Ca[i,j]=arb(cand[i][j].abs_upper())
    return Ca
tot=T(lambda: OB.contract(pd,cand),15)
stages=[("C build (candidate-only)",s_Cbuild),("transpose (candidate-only)",s_transpose),
        ("Ra gather (panel-only)",s_Ragather),("Ct*Ra matmuls",s_SaMul),
        ("flat gather",s_flatgather),("flat*Qflat matmuls",s_Qmul),
        ("error channel (289-loop)",s_errchannel),("|C| build (candidate-only)",s_absbuild)]
print(f"TOTAL contract(): {tot*1000:.4f} ms   [dense candidate, shift 0]\n")
print(f"{'stage':<34}{'ms':>9}{'% of total':>12}  {'depends on'}")
acc=0
dep={"C build (candidate-only)":"CANDIDATE only","transpose (candidate-only)":"CANDIDATE only",
     "Ra gather (panel-only)":"panel/drift only","Ct*Ra matmuls":"both",
     "flat gather":"both","flat*Qflat matmuls":"both",
     "error channel (289-loop)":"CANDIDATE + panel scalars","|C| build (candidate-only)":"CANDIDATE only"}
for name,fn in stages:
    t=T(fn,15); acc+=t
    print(f"{name:<34}{t*1000:>9.4f}{100*t/tot:>11.1f}%  {dep[name]}")
print(f"{'sum of stages':<34}{acc*1000:>9.4f}{100*acc/tot:>11.1f}%")
# how much is candidate-only (hoistable out of the ~21-panel loop)?
condonly=T(s_Cbuild,15)+T(s_transpose,15)
print(f"\n  candidate-only work (C build + transpose) : {condonly*1000:.4f} ms = {100*condonly/tot:.1f}% of a contract")
print(f"  panels per patch (this patch)             : {n_z}")
