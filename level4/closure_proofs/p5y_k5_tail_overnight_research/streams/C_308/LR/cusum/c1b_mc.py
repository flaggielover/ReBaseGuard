"""C1b NON-CERTIFIED context (declaration D5): Monte Carlo of the excursion functionals at declared non-target drifts.

Excursion from a = (0,0) under drift e (z = -e + N(0,1)); sigma = first alarm or first return to a (time >= 1).
Estimates (mean, standard error) of
  tau_a = E sigma,  L1 = E sum_{n<sigma} |M_n|,  L2 = E sum_{n<sigma} |M_n^2 - n|,  S2 = E sum_{n<sigma} M_n^2,
  T_N = E sum_{n<sigma} n,  D = P(alarm before return),  and Lambda = tau_a / D (renewal identity).
N = 200000 excursions per drift, seed 12345.  Output NS/validation/C1B_MC.json.  NON-CERTIFIED.
"""
from __future__ import annotations

import json
import math
import random
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
NS = HERE.parents[3]
sys.path.insert(0, str(NS / "code"))
import ov_quarantine as Q  # noqa: E402

Q.install_import_guard()

K, C = 0.5, 5.5


def run(e: float, N: int, seed: int) -> dict:
    Q.guard_drift(e)
    rng = random.Random(seed)
    acc = {k: [0.0, 0.0] for k in ("sigma", "L1", "L2", "S2", "TN", "alarm")}
    for _ in range(N):
        p = m = 0.0
        M = 0.0
        n = 0
        l1 = l2 = s2 = tn = 0.0
        alarm = 0
        while True:
            # contribution of time n (state alive at time n)
            l1 += abs(M)
            l2 += abs(M * M - n)
            s2 += M * M
            tn += n
            y = rng.gauss(0.0, 1.0)          # y = z + e ~ N(0,1), S = -y
            z = y - e
            if z < m - C or z > C - p:
                alarm = 1
                n += 1
                break
            p, m = max(0.0, p + z - K), max(0.0, m - z - K)
            M += -y
            n += 1
            if p == 0.0 and m == 0.0:
                break
        for k, v in (("sigma", n), ("L1", l1), ("L2", l2), ("S2", s2), ("TN", tn), ("alarm", alarm)):
            acc[k][0] += v
            acc[k][1] += v * v
    out = {}
    for k, (s, ss) in acc.items():
        mu = s / N
        var = max(ss / N - mu * mu, 0.0)
        out[k] = {"mean": mu, "se": math.sqrt(var / N)}
    D = out["alarm"]["mean"]
    out["Lambda_renewal"] = out["sigma"]["mean"] / D
    return out


def main(drifts):
    t0 = time.time()
    res = {"schema": "C1B_MC/1", "label": "NON-CERTIFIED Monte Carlo", "N": 200000, "seed": 12345, "drifts": {}}
    for e in drifts:
        t = time.time()
        r = run(e, 200000, 12345)
        r["seconds"] = round(time.time() - t, 1)
        res["drifts"][str(e)] = r
        print(e, {k: (round(v["mean"], 4), round(v["se"], 4)) if isinstance(v, dict) and "mean" in v else v
                  for k, v in r.items()}, flush=True)
    res["wall_seconds"] = round(time.time() - t0, 1)
    sys.path.insert(0, str(HERE))
    import c1b_prov as PV
    res["provenance"] = PV.provenance({})
    path = NS / "validation" / "C1B_R2_MC.json"
    path.write_text(json.dumps(res, indent=1, sort_keys=True) + "\n")
    Q.log_execution("streams/C_308/LR/cusum/c1b_mc.py", f"C1b NON-CERTIFIED MC excursion functionals e={drifts}",
                    cells_touched=[], klass="NONTARGET_DRIFT_VALIDATION")


if __name__ == "__main__":
    from fractions import Fraction
    main([float(Fraction(x)) for x in sys.argv[1:]] or [0.5, 0.25, 1.0])
