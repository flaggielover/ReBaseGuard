"""Stream A0: NON-CERTIFIED seeded Monte Carlo of Lambda(e) = E_a[tau] at a declared validation drift.

Independent of both certifiers (written from the model): state (p, m) = (0, 0); each step draws y ~ N(0, 1)
(random.Random(seed).gauss), z = y - e; alarm iff z < m - C or z > C - p (C = 11/2); else
(p, m) <- (max(0, p + z - K), max(0, m - z - K)), K = 1/2.  tau counts steps up to and including the alarm step,
so E_a[tau] = sum_{n >= 0} (K_e^n 1)(a).  Reports mean and standard error.  NOTHING here is certified.
"""
from __future__ import annotations

import math
import random
import time

import a0_common as A

K, C = 0.5, 5.5


def mc_lambda(e, n_runs: int, seed: int) -> dict:
    ef = float(A.declared_drift(e))
    rng = random.Random(seed)
    g = rng.gauss
    s = ss = 0
    t0 = time.process_time()
    for _ in range(n_runs):
        p = m = 0.0
        n = 0
        while True:
            n += 1
            z = g(0.0, 1.0) - ef
            if z < m - C or z > C - p:
                break
            p = p + z - K
            if p < 0.0:
                p = 0.0
            m = m - z - K
            if m < 0.0:
                m = 0.0
        s += n
        ss += n * n
    mu = s / n_runs
    var = max(ss / n_runs - mu * mu, 0.0)
    return {"estimator": "MC_NONCERTIFIED", "drift": A.fs(e), "n_runs": n_runs, "seed": seed, "mean": mu,
            "se": math.sqrt(var / n_runs), "sd": math.sqrt(var), "cpu_seconds": round(time.process_time() - t0, 1)}
