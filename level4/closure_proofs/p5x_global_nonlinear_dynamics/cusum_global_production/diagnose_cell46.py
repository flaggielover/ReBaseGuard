"""DIAGNOSTIC ONLY - root-cause attribution of the cell-46 width. NOT a result."""
import sys; sys.path.insert(0,'.')
import run_cover as RC
from flint import arb
from rebaseguard_certify.arb_backend import rational, workprec
import ra_certifier as RA

cells = RC.build_cover()
lo,hi,cball,hnum,n_sub = cells[46]
print(f"cell 46: e=[{lo/RC.DEN},{hi/RC.DEN}] n_sub={n_sub} C={float(arb(cball).mid()):.6f}")
print(f"  frozen model radius h_sub = hnum/DEN = {hnum/RC.DEN:.7f}")
print(f"  sub-cell half-width       = (hi-lo)/n_sub/2 = {(hi-lo)/n_sub/2/RC.DEN:.7f}")
step=(hi-lo)//n_sub
recs=[RC._worker((j, lo+step*j+step//2, hi/RC.DEN, cball)) for j in range(n_sub)]
with workprec(RA.BITS):
    a,b2 = RC._consts(); C=arb(cball); h=arb(rational(hnum,RC.DEN))
    c2 = arb(rational(113788,100000)) + b2*arb(rational(hi,RC.DEN))
    for j,rec in enumerate(recs):
        delta=arb(rec["delta"]["ball"]); delta_d=arb(rec["delta_derivative"]["ball"])
        G0=arb(rec["sup_chebyshev_g"]["ball"])+C*delta
        G1=arb(rec["sup_chebyshev_dg"]["ball"])+C*delta_d
        S2=arb(2)*C*(arb(2)*a*G1 + b2*G0 + b2*h*G1 + c2)
        t_e   = float(((arb(rational(lo+step*(j+1),RC.DEN))-arb(rational(lo+step*j,RC.DEN)))/arb(2)).upper())
        t_g   = float((C*delta).upper())
        t_dg  = float((arb(0,h.upper())*(arb(rec["dghat_origin"]["ball"])+arb(0,(C*delta_d).upper()))).upper())
        t_2nd = float(((h*h/arb(2))*S2).upper())
        if j==0:
            print(f"\n  WIDTH ATTRIBUTION (sub-cell 0), total half-width = {t_e+t_g+t_dg+t_2nd:.6f}:")
            print(f"    e-range      +/- {t_e:.6f}   ({100*t_e/(t_e+t_g+t_dg+t_2nd):5.1f}%)")
            print(f"    C*delta      +/- {t_g:.6f}   ({100*t_g/(t_e+t_g+t_dg+t_2nd):5.1f}%)")
            print(f"    h*dg         +/- {t_dg:.6f}   ({100*t_dg/(t_e+t_g+t_dg+t_2nd):5.1f}%)")
            print(f"    (h^2/2)*S2   +/- {t_2nd:.6f}   ({100*t_2nd/(t_e+t_g+t_dg+t_2nd):5.1f}%)  <-- dominant")
            print(f"      with G0={float(G0.mid()):.4f} (~ e_max, grows linearly in e), G1={float(G1.mid()):.4f}, S2={float(S2.mid()):.4f}")
            print(f"\n  the contraction rule that fixed h: C*(2*a*h + b2*h^2) = {float((C*(arb(2)*a*h+b2*h*h)).mid()):.6f} <= 0.5  (satisfied, but it bounds CONTRACTION, not WIDTH)")
