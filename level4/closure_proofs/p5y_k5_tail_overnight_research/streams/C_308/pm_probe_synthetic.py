import sys
import pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / 'code'))
from fractions import Fraction as F
import ov_fixtures as X
def absm(A): return [[abs(a) for a in r] for r in A]
def rowsum_at(A,a=0): return sum(abs(x) for x in A[a])
for seed in range(1,9):
    n=6+seed%4
    fam=X.random_family(n,seed,e_range=(F(0),F(1,4)),kill=F(1,20))
    e=F(1,8)
    R=fam.R(e); K1=fam.K(e,1); K2=fam.K(e,2)
    one=[F(1)]*n
    C=X.op_norm(R); k1=X.op_norm(K1); k2=X.op_norm(K2)
    Lam=sum(R[0])
    dR=X.mat_mul(X.mat_mul(R,K1),R)
    d2R=X.mat_add(X.mat_scale(X.mat_mul(X.mat_mul(dR,K1),R),2), X.mat_mul(X.mat_mul(R,K2),R))
    A1true=rowsum_at(dR); A2true=rowsum_at(d2R)
    w=X.mat_vec(R,one)
    pm1=X.mat_vec(R,X.mat_vec(absm(K1),w))[0]
    v=X.mat_vec(R,X.mat_vec(absm(K1),w))
    pm2=2*X.mat_vec(R,X.mat_vec(absm(K1),v))[0]+X.mat_vec(R,X.mat_vec(absm(K2),w))[0]
    print(f"seed{seed} n={n} A0: true={float(Lam):.3f} G={float(C):.3f} (x{float(C/Lam):.2f}) | A1: true={float(A1true):.3f} PM={float(pm1):.3f} mid(Lam*k1*C)={float(Lam*k1*C):.3f} G={float(k1*C*C):.3f} | A2: true={float(A2true):.3f} PM={float(pm2):.3f} G={float(k2*C*C+2*k1*k1*C**3):.3f}")
