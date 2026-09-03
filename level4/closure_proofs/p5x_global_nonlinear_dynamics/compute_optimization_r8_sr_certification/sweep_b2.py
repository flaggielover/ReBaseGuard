"""B2 binding gate: full frozen 1024x1024 certification sweep, 6 workers."""
import json, os, sys, time
from multiprocessing import Pool
from pathlib import Path
NS = Path(__file__).resolve().parents[1]
for p in (str(NS/"sr_full_cell_prototype"), str(NS/"compute_optimization_r6_minimal_evaluator"),
          str(NS/"compute_optimization_r4_xi_reformulation"), str(NS/"b2_basis_feasibility_audit"),
          str(Path(__file__).resolve().parents[5]/"rebaseguard-proof"/"src"), str(Path(__file__).parent)):
    if p not in sys.path: sys.path.insert(0, p)
GRID = 1024
_S = {}
def _init():
    from flint import arb, ctx
    import r8_certify as R8, sr_prototype as SP
    ctx.prec = 256
    A, b, c = SP.sr_constants()
    coef, _ = SP.solve_candidate_cheb(0.25, float(A.mid()), float(c.mid()))
    n = coef.shape[0]-1
    ca = [[arb(float(coef[i][j])) for j in range(n+1)] for i in range(n+1)]
    _S.update(pre=R8.precompute(ca), A=A, e=SP.rational(1,4), R8=R8)
def _row(i):
    R8 = _S["R8"]
    w = 0.0; arg = None; tot = 0.0
    for j in range(GRID):
        b, _ = R8.certify_cell(_S["pre"], i, j, _S["e"], _S["A"], GRID)
        tot += b
        if b > w: w, arg = b, (i, j)
    return w, arg, tot
if __name__ == "__main__":
    t0 = time.time()
    with Pool(6, initializer=_init) as pool:
        out = pool.map(_row, range(GRID), chunksize=4)
    worst = max(out, key=lambda r: r[0])
    mean = sum(r[2] for r in out)/(GRID*GRID)
    wall = time.time()-t0
    json.dump({"grid":GRID,"worst":worst[0],"worst_cell":list(worst[1]),
               "mean_bound":mean,"wall_s":wall,"cells":GRID*GRID,
               "ms_per_cell_effective":wall/(GRID*GRID)*1000*6},
              open(str(Path(__file__).parent/"b2_sweep.json"),"w"), indent=1)
    print(f"worst={worst[0]:.6e} at {worst[1]}  mean={mean:.4e}  wall={wall/60:.1f} min")
