"""SRK adapter on MANUFACTURED TC-T-shaped inputs (no tail file is read; no frozen consumer is imported).
A stub of the frozen tail_enclosure is re-derived here from THEOREM_TC / THEOREM_TCT formulas (independent of
tct_rule.py).  Checks: reproduction gate passes on genuine stub output and refuses tampered frozen objects; the SRK
enclosure lies inside the TC-T enclosure; Gamma = None everywhere reproduces the frozen enclosure; a manufactured
Gamma that is large leaves the enclosure unchanged (min construction)."""
import random
import sys
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "impl"))
import srk_adapter as AD  # noqa: E402


def coefficients(m):
    rows = [("F", r, 0, F(1, m)) for r in range(m)]
    rows += [("W", r, t - r - 1, F(1, t) - F(1, m)) for t in range(1, m) for r in range(t)]
    return rows


def manufactured(seed):
    rng = random.Random(seed)
    R = lambda lo=1, hi=1000: F(rng.randint(lo, hi), rng.randint(1, 1000))  # noqa: E731
    meas = {"rho": F(rng.randint(1, 50), 1000), "r": {}, "W2": {}}
    for r in range(5):
        a = R(-5000, 5000)
        meas["r"][str(r)] = {"sup": {"F": R(), "D": R(), "H": R()}, "delta_F": R(1, 10) / 10 ** 6,
                             "delta_D": R(1, 10) / 10 ** 6, "delta_H": R(1, 10) / 10 ** 6,
                             "eps_src": [R(1, 10) / 10 ** 7 for _ in range(4)], "H_at_a": [a, a]}
    for t in range(1, 5):
        for r in range(t):
            a = R(-100, 100)
            meas["W2"][f"{r}:{t - r - 1}"] = [a, a + R(1, 10) / 10 ** 5]
    k = {i: R(1, 3) for i in range(5)}
    A = {"A0": R(1, 50), "A1": R(1, 200), "A2": R(1, 2000)}
    sig = {r: {"sigma3": R(), "sigma4": R()} for r in range(5)}
    return meas, k, A, sig


def stub_tail_enclosure(meas, k, A, sig, m):
    rho = meas["rho"]
    obj = {}
    for r in range(5):
        o = meas["r"][str(r)]
        sF, sD, sH = (o["sup"][x] for x in "FDH")
        fF = o["delta_F"] + o["eps_src"][0]
        fD = o["delta_D"] + o["eps_src"][1]
        fH = o["delta_H"] + o["eps_src"][2]
        fG = k[3] * sF + 3 * k[2] * sD + 3 * k[1] * sH + sig[r]["sigma3"] + o["eps_src"][3]
        e4 = sig[r]["sigma4"] + 6 * k[2] * sH + 4 * k[3] * (sD + rho * sH) + k[4] * (sF + rho * sD + rho ** 2 * sH / 2)
        p2 = fH + rho * fG + rho ** 2 * e4 / 2
        p1 = fD + rho * fH + rho ** 2 * fG / 2 + rho ** 3 * e4 / 6
        p0 = fF + rho * fD + rho ** 2 * fH / 2 + rho ** 3 * fG / 6 + rho ** 4 * e4 / 24
        rad = A["A0"] * p2 + 2 * A["A1"] * p1 + A["A2"] * p0
        obj[r] = {"f_G": fG, "env4": e4, "rad": rad, "half": rad, "abs_G_at_a": F(0), "sup_G": F(0), **sig[r]}
    lo = hi = F(0)
    for kind, r, jj, c in coefficients(m):
        if kind == "F":
            a, b = meas["r"][str(r)]["H_at_a"]
            lo += c * (a - obj[r]["half"])
            hi += c * (b + obj[r]["half"])
        else:
            a, b = meas["W2"][f"{r}:{jj}"]
            lo += c * a
            hi += c * b
    return lo, hi, obj


def refuses(fn):
    try:
        fn()
        return False
    except AD.AdapterRefusal:
        return True


def run():
    res = {"repro_none": 0, "inside": 0, "big_gamma_unchanged": 0, "tamper_refused": 0, "Gneq0_refused": 0,
           "wrongcoef_refused": 0, "cases": 0}
    for seed in range(1, 21):
        meas, k, A, sig = manufactured(seed)
        lo, hi, obj = stub_tail_enclosure(meas, k, A, sig, 5)
        res["cases"] += 1
        none = AD.srk_enclosure(meas, A, 5, {1: None, 2: None, 3: None, 4: None}, obj, (lo, hi), coefficients, allow_test_gamma=True)
        res["repro_none"] += (none["lo"], none["hi"]) == (lo, hi)
        gam = {i: A["A0"] * k[i] * F(random.Random(seed * 7 + i).randint(30, 99), 100) for i in (1, 2, 3, 4)}
        out = AD.srk_enclosure(meas, A, 5, gam, obj, (lo, hi), coefficients, allow_test_gamma=True)
        res["inside"] += (out["lo"] >= lo and out["hi"] <= hi and (out["lo"], out["hi"]) != (lo, hi))
        big = {i: A["A0"] * k[i] * 10 ** 6 for i in (1, 2, 3, 4)}
        outb = AD.srk_enclosure(meas, A, 5, big, obj, (lo, hi), coefficients, allow_test_gamma=True)
        res["big_gamma_unchanged"] += (outb["lo"], outb["hi"]) == (lo, hi)
        bad = {r: dict(v) for r, v in obj.items()}
        bad[2]["rad"] = bad[2]["rad"] * F(99, 100)
        res["tamper_refused"] += refuses(lambda: AD.srk_enclosure(meas, A, 5, gam, bad, (lo, hi), coefficients, allow_test_gamma=True))
        badg = {r: dict(v) for r, v in obj.items()}
        badg[0]["abs_G_at_a"] = F(1, 10)
        res["Gneq0_refused"] += refuses(lambda: AD.srk_enclosure(meas, A, 5, gam, badg, (lo, hi), coefficients, allow_test_gamma=True))
        wrong = lambda m: [(a, b, c, d * (F(11, 10) if a == "W" else 1)) for a, b, c, d in coefficients(m)]  # noqa
        res["wrongcoef_refused"] += refuses(lambda: AD.srk_enclosure(meas, A, 5, gam, obj, (lo, hi), wrong, allow_test_gamma=True))
        res.setdefault("raw_dict_refused_without_flag", 0)
        res["raw_dict_refused_without_flag"] += refuses(lambda: AD.srk_enclosure(meas, A, 5, gam, obj, (lo, hi),
                                                                                  coefficients))
        res.setdefault("gate_empty_reproduces", 0)
        e = AD.srk_enclosure(meas, A, 5, AD.GT.GateResult.empty(), obj, (lo, hi), coefficients)
        res["gate_empty_reproduces"] += (e["lo"], e["hi"]) == (lo, hi)
    ok = all(v == res["cases"] for kk, v in res.items() if kk != "cases")
    return ok, res


if __name__ == "__main__":
    ok, res = run()
    print(res)
    sys.exit(0 if ok else 1)
