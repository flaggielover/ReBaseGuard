import sys, time, json
from fractions import Fraction as F
sys.path.insert(0, "/Users/suzhe/ReBaseGuard-k5c11rd/level4/closure_proofs/p5y_k5_tail_c11rd_d1d2_extension/code")
import c11rd_certify as CE, c11rd_model as MD
E_LO = F(5, 2); E_HI = F(5, 2) + F(108337, 1250000)     # NON-TARGET block (C11R NT)
params = {"float": {"n": 8, "n4": 8, "ns": 11, "nt": 11, "q": 20, "bits": 52},
          "tm_order": 4, "moment_terms": 34, "splits": {"s": 4, "theta": 4, "s4": 4},
          "tolerances": ["1/100000", "1/10000", "1/1000"], "max_depth": int(sys.argv[1])}
sizing = {"C_T": F(3429, 500), "tau": F(3429, 500)}      # SIZING ONLY: no premise holds on NT
kappa = MD.kernel_norms()
r = CE.certify_subblock(E_LO, E_HI, params, sizing, kappa, log=lambda s: print(s, flush=True))
print(json.dumps({"lam": [float(x) for x in r["lam"]], "err_D1_sizing": float(r["propagation"]["err_D1"]),
                  "err_D2_sizing": float(r["propagation"]["err_D2"]), "cover": r["cover"],
                  "atom": [float(F(x)) for x in r["atom_candidate_values"]],
                  "float": r["float_proposal"], "seconds": r["seconds"]}, default=str, indent=1))
