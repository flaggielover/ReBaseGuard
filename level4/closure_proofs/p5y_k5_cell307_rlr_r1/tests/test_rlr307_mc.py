"""QC04: independent Monte Carlo consistency of certified block bounds (NON-CERTIFIED; a check that can fail).

An independent implementation of the model by simulation. It shares no code with the certifier: it has its own
update, windows and score. The model is the one of THEOREM_RLR307 section 0:
* K = 1/2 and C = 11/2;
* Z = Y - e with Y ~ N(0, 1), so Z + e ~ N(0, 1);
* alarm iff Z > C - p or Z < m - C;
* update p' = (p + Z - K)+ and m' = (m - Z - K)+;
* atom a = (0, 0); score S = -(Z + e) = -Y.

Taboo excursions from a (until alarm or return to a) estimate:
* tau_a = E sigma;
* D = P(alarm before return);
* L1 = E sum_{n<sigma} |M_n|;
* L2 = E sum_{n<sigma} |M_n^2 - n|.

Whole runs from a (until alarm) estimate:
* Lambda = E tau;
* Lambda' = E sum_{n<tau} M_n and Lambda'' = E sum_{n<tau} (M_n^2 - n). These are the score identities of THEOREM_LR
  LR-1 with f = 1.
* A1_true >= |Lambda'| and A2_true >= |Lambda''|, so the certified supplies must dominate them.

A violation beyond 5 standard errors refutes the certificate at that drift (up to a < 1e-6 false-alarm probability).
Code-path controls re-run the SAME comparator on deliberately wrong bounds and must flag them.
"""
from __future__ import annotations

import math
import random
from fractions import Fraction as F

K, C = 0.5, 5.5
N_EXC, N_WHOLE = 100_000, 50_000
Z = 5.0


def excursion(rng: random.Random, e: float) -> tuple:
    p = m = 0.0
    M, n, s1, s2 = 0.0, 0, 0.0, 0.0
    while True:
        s1 += abs(M)
        s2 += abs(M * M - n)
        y = rng.gauss(0.0, 1.0)
        z = y - e
        n += 1
        M -= y
        if z > C - p or z < m - C:
            return n, 1.0, s1, s2
        p2, m2 = p + z - K, m - z - K
        p, m = (p2 if p2 > 0.0 else 0.0), (m2 if m2 > 0.0 else 0.0)
        if p == 0.0 and m == 0.0:
            return n, 0.0, s1, s2


def whole(rng: random.Random, e: float) -> tuple:
    p = m = 0.0
    M, n, sM, sQ = 0.0, 0, 0.0, 0.0
    while True:
        sM += M
        sQ += M * M - n
        y = rng.gauss(0.0, 1.0)
        z = y - e
        n += 1
        M -= y
        if z > C - p or z < m - C:
            return n, sM, sQ
        p2, m2 = p + z - K, m - z - K
        p, m = (p2 if p2 > 0.0 else 0.0), (m2 if m2 > 0.0 else 0.0)


def _mean_se(xs: list) -> tuple:
    n = len(xs)
    mu = math.fsum(xs) / n
    var = math.fsum((x - mu) ** 2 for x in xs) / (n - 1)
    return mu, math.sqrt(var / n)


def estimate(e: float, seed: int) -> dict:
    rng = random.Random(seed)
    ex = [excursion(rng, e) for _ in range(N_EXC)]
    wh = [whole(rng, e) for _ in range(N_WHOLE)]
    out = {}
    for name, col in (("tau_a", 0), ("D", 1), ("L1", 2), ("L2", 3)):
        out[name] = _mean_se([r[col] for r in ex])
    for name, col in (("Lambda", 0), ("dLambda", 1), ("d2Lambda", 2)):
        out[name] = _mean_se([r[col] for r in wh])
    return out


def check(est: dict, rec: dict) -> dict:
    """The comparator: every certified inequality must survive at Z standard errors."""
    f = {k: float(F(rec[k])) for k in ("tau", "tau_a_lo", "D_lo", "A_bar", "Lambda_lo", "L1_up", "L2_up",
                                       "A1_SUPPLY", "A2_SUPPLY")}
    (t, st), (d, sd), (l1, s1), (l2, s2) = est["tau_a"], est["D"], est["L1"], est["L2"]
    (lam, sl), (dl, sdl), (d2l, sd2l) = est["Lambda"], est["dLambda"], est["d2Lambda"]
    c = {"tau_a_lo <= tau_a": f["tau_a_lo"] <= t + Z * st, "tau_a <= tau": t - Z * st <= f["tau"],
         "D_lo <= D": f["D_lo"] <= d + Z * sd, "Lambda_lo <= Lambda": f["Lambda_lo"] <= lam + Z * sl,
         "Lambda <= A_bar": lam - Z * sl <= f["A_bar"], "L1 <= L1_up": l1 - Z * s1 <= f["L1_up"],
         "L2 <= L2_up": l2 - Z * s2 <= f["L2_up"], "|Lambda'| <= A1_SUPPLY": abs(dl) - Z * sdl <= f["A1_SUPPLY"],
         "|Lambda''| <= A2_SUPPLY": abs(d2l) - Z * sd2l <= f["A2_SUPPLY"]}
    return {"all_hold": all(c.values()), "violations": [k for k, v in c.items() if not v]}


def run(decoy_stage1: dict, seed0: int = 971) -> dict:
    rows, controls = [], {}
    for b in decoy_stage1["blocks"]:
        rec = b["block"]
        if rec.get("status") != "CERTIFIED":
            rows.append({"block": b["index"], "status": rec.get("status"), "all_hold": None})
            continue
        lo, hi = F(b["hull_lo"]), F(b["hull_hi"])
        for tag, e in (("lo", lo), ("mid", (lo + hi) / 2), ("hi", hi)):
            est = estimate(float(e), seed0 + 10 * b["index"] + {"lo": 0, "mid": 1, "hi": 2}[tag])
            res = check(est, rec)
            rows.append({"block": b["index"], "drift_point": tag, **res,
                         "estimates": {k: [round(v[0], 6), round(v[1], 6)] for k, v in est.items()}})
            if b["index"] == 0 and tag == "mid":
                (t, _), (d, _), (l1, _) = est["tau_a"], est["D"], est["L1"]
                dl = est["dLambda"][0]
                planted = {"tau := tau_a,lo/2 (upper bound below the truth)": dict(rec, tau=S(F(rec["tau_a_lo"]) / 2)),
                           "L1_up := L1_hat/3": dict(rec, L1_up=S(F(l1) / 3)),
                           "D_lo := 2 D_hat": dict(rec, D_lo=S(2 * F(d))),
                           "A1_SUPPLY := |Lambda'_hat|/3": dict(rec, A1_SUPPLY=S(abs(F(dl)) / 3))}
                controls = {k: {"flagged": not check(est, v)["all_hold"]} for k, v in planted.items()}
    # symmetry sanity of the simulator (Lemma S): drift -e reproduces tau_a and D at e within 5 SE
    b0 = decoy_stage1["blocks"][0]
    em = float((F(b0["hull_lo"]) + F(b0["hull_hi"])) / 2)
    ep, en = estimate(em, 4242), estimate(-em, 4243)
    sym = all(abs(ep[k][0] - en[k][0]) <= Z * math.hypot(ep[k][1], en[k][1]) for k in ("tau_a", "D", "Lambda"))
    return {"rows": rows, "controls": controls, "symmetry_e_vs_minus_e": sym,
            "n_checked": sum(1 for r in rows if r.get("all_hold") is not None),
            "pass": all(r.get("all_hold") for r in rows) and bool(controls) and all(c["flagged"] for c in controls.values())
            and sym, "latent_proxy": "decoy estimates; never juxtapose with any tail-cell number"}


def S(x) -> str:
    x = F(x).limit_denominator(10 ** 12) if not isinstance(x, F) else x
    return f"{x.numerator}/{x.denominator}"
