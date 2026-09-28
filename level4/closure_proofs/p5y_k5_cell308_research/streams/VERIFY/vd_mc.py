"""Stream D, D5 supplement: NON-RIGOROUS Monte-Carlo of E_a[tau] straight from the CUSUM definition.

This checks the kernel MODEL shared by vd_verify, vd_point and vd_float (window, clipping, alarm semantics, atom) at
the level of the stochastic process itself: p <- max(0, p + z - K), m <- max(0, m - z - K), z + e ~ N(0,1), alarm
at the first step whose UNCLIPPED update exceeds H on either arm; tau counts the steps up to and including the alarm.
Fixed seeds; mean and standard error.  Output: results/D5_MC.json (validation-drift values: latent proxies, kept here).
"""
from __future__ import annotations

import json
import math
import random
import sys
import time
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import vd_float as FL  # noqa: E402  (quarantine loader only)
import vd_adapt as AD  # noqa: E402

Q = FL.Q
K, H = 0.5, 5.0


def mc(e: float, n: int, seed: int) -> dict:
    rng = random.Random(seed)
    g = rng.gauss
    s = s2 = 0.0
    for _ in range(n):
        p = m = 0.0
        t = 0
        while True:
            t += 1
            z = g(0.0, 1.0) - e
            up, um = p + z - K, m - z - K
            if up > H or um > H:
                break
            p, m = (up if up > 0 else 0.0), (um if um > 0 else 0.0)
        s += t
        s2 += t * t
    mean = s / n
    var = s2 / n - mean * mean
    return {"n": n, "seed": seed, "mean": mean, "se": math.sqrt(var / n)}


def work(arg):
    e_str, n, seed = arg
    Q.guard_drift(F(e_str))
    return e_str, mc(float(F(e_str)), n, seed)


if __name__ == "__main__":
    import multiprocessing as mp
    plan = [("3", 400000, 11), ("7/2", 400000, 12), ("1", 200000, 13), ("1/2", 100000, 14)]
    for e, _, _ in plan:
        Q.guard_drift(F(e))
    Q.log_event("streams/VERIFY/vd_mc.py", "D5 supplement: Monte-Carlo of E_a[tau] from the CUSUM definition at declared "
                "non-target drifts 3, 7/2, 1, 1/2", klass="NONTARGET_DRIFT_VALIDATION", agent="streamD")
    t0 = time.time()
    with mp.get_context("spawn").Pool(3) as pool:
        outs = pool.map(work, plan)
    doc = {"schema": "VD_MC/1", "non_rigorous": True, "results": []}
    for e_str, r in outs:
        e = F(e_str)
        certs = []
        for d in (4, 6):
            path = HERE / "certs" / f"CERT_e{e.numerator}_{e.denominator}_d{d}.json"
            if path.exists():
                Wa = float(AD.from_c1b_raw(json.loads(path.read_text())["c1b_raw"]).at_atom())
                certs.append({"certificate": path.name, "W_at_atom": Wa,
                              "z_score_(W(a)-mean)/se": (Wa - r["mean"]) / r["se"],
                              "W_at_atom_ge_mean_minus_4se": Wa >= r["mean"] - 4 * r["se"]})
        doc["results"].append({"drift": e_str, **r, "certificates": certs})
    doc["all_consistent"] = all(c["W_at_atom_ge_mean_minus_4se"] for x in doc["results"] for c in x["certificates"])
    doc["seconds"] = round(time.time() - t0, 1)
    (HERE / "results" / "D5_MC.json").write_text(json.dumps(doc, indent=1) + "\n")
    print(json.dumps(doc, indent=1))
