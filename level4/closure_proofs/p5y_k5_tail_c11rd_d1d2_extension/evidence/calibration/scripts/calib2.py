import sys, time, json
from fractions import Fraction as F
sys.path.insert(0, "/Users/suzhe/ReBaseGuard-k5c11rd/level4/closure_proofs/p5y_k5_tail_c11rd_d1d2_extension/code")
import c11rd_certify as CE, c11rd_model as MD
W = F(108337, 1250000)                                  # cell width (same as C11R's NT block)
blocks = {"NT": F(5, 2), "LOW": F(1)}                    # NON-TARGET: C11R NT block; synthetic low-drift block
lo = blocks[sys.argv[1]]
params = {"float": {"n": int(sys.argv[2]), "n4": int(sys.argv[2]), "ns": 11, "nt": 11, "q": 20, "bits": 52},
          "tm_order": 6, "moment_terms": 34, "splits": {"s": 4, "theta": [4, 8, 12, 16], "s4": 4},
          "tolerances": ["1/100000", "1/20000", "1/2000"], "max_depth": 2}
sizing = {"C_T": F(3429, 500), "tau": F(3429, 500)}      # SIZING ONLY: no premise holds on these blocks
r = CE.certify_subblock(lo, lo + W, params, sizing, MD.kernel_norms(), log=lambda s: print(s, flush=True))
print(json.dumps({"block": sys.argv[1], "lam": [float(x) for x in r["lam"]], "err_D1_sizing": float(r["propagation"]["err_D1"]),
                  "err_D2_sizing": float(r["propagation"]["err_D2"]), "cover": r["cover"],
                  "atom": [float(F(x)) for x in r["atom_candidate_values"]],
                  "float_discrete_residual": r["float_proposal"]["discrete_residual"], "seconds": r["seconds"]}, default=str, indent=1))
