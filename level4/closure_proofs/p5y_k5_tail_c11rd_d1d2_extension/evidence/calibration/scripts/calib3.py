"""NON-TARGET calibration, parallel: one sub-block [lo, lo + W/nsub] at a non-target drift.
usage: calib3.py LABEL LO_NUM LO_DEN NSUB N_DEGREE WORKERS"""
import json
import multiprocessing as mp
import sys
import time
from fractions import Fraction as F

CODE = "/Users/suzhe/ReBaseGuard-k5c11rd/level4/closure_proofs/p5y_k5_tail_c11rd_d1d2_extension/code"
sys.path.insert(0, CODE)
import c11rd_certify as CE  # noqa: E402
import c11rd_float as FL  # noqa: E402
import c11rd_kernel as KR  # noqa: E402
import c11rd_model as MD  # noqa: E402

W = F(108337, 1250000)
_W = {}


def init(c, p):
    _W["c"], _W["p"] = c, p


def work(a):
    band, s, e, th, ax, N = a
    return CE.refine_box(KR.Box(band, s, e, theta=th, axis=ax, order=N), _W["c"], _W["p"])


if __name__ == "__main__":
    label, lo = sys.argv[1], F(int(sys.argv[2]), int(sys.argv[3]))
    nsub, n, workers = int(sys.argv[4]), int(sys.argv[5]), int(sys.argv[6])
    hi = lo + W / nsub
    params = {"float": {"n": n, "n4": n, "ns": 11, "nt": 11, "q": 20, "bits": 52},
              "tm_order": 6, "moment_terms": 34, "splits": {"s": 4, "theta": [4, 8, 12, 16], "s4": 4},
              "tolerances": ["1/100000", "1/20000", "1/2000"], "max_depth": 2}
    t0 = time.time()
    ec = (lo + hi) / 2
    prop = FL.propose(float(ec), n=n, n4=n, ns=11, nt=11, q=20)
    cands = [FL.exact_candidate(prop["basis"], c, bits=52) for c in prop["coeffs"]]
    tp = time.time() - t0
    boxes = CE.initial_boxes(lo, hi, params["splits"], params["tm_order"])
    acc = None
    with mp.get_context("spawn").Pool(workers, initializer=init, initargs=(cands, params)) as pool:
        for i, r in enumerate(pool.imap_unordered(work, [(b.band, b.s, b.e, b.theta, b.axis, b.N) for b in boxes]), 1):
            acc = CE.merge(acc, r)
            if i % 40 == 0:
                print(f"  {i}/{len(boxes)} evaluated {acc['evaluated']} {time.time() - t0:.0f}s", flush=True)
    sizing = CE.propagate(acc["lam"], F(3429, 500), F(3429, 500), MD.kernel_norms())   # SIZING ONLY
    av = CE.atom_values(cands, (hi - lo) / 2)
    print(json.dumps({"label": label, "block": [str(lo), str(hi)], "nsub": nsub, "n": n,
                      "lam": [float(x) for x in acc["lam"]], "leaves": acc["leaves"], "evaluated": acc["evaluated"],
                      "unmet": acc["unmet"], "worst": acc["worst"],
                      "err_D1_sizing": float(sizing["err_D1"]), "err_D2_sizing": float(sizing["err_D2"]),
                      "atom": [float(x) for x in av[0]], "proposal_seconds": tp,
                      "discrete_residual": prop["discrete_residual"], "seconds": time.time() - t0}, indent=1, default=str))
