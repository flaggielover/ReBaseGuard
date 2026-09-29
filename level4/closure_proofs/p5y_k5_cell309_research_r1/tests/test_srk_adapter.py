"""SRK adapter on MANUFACTURED TC-T-shaped inputs (no tail file is read; no frozen consumer is imported).
A stub of the frozen tail_enclosure is re-derived here from THEOREM_TC / THEOREM_TCT formulas (independent of
tct_rule.py).  Checks: reproduction gate passes on genuine stub output and refuses tampered frozen objects; the SRK
enclosure lies inside the TC-T enclosure; Gamma = None everywhere reproduces the frozen enclosure; a manufactured
Gamma that is large leaves the enclosure unchanged (min construction).  Every Gamma-bar reaches the adapter through
srk_gate.gate on manufactured certificate objects (review R2 P-1: no raw-dict bypass exists any more), and the binding
negatives of review R2 RD2-2 must refuse: another cell, another geometry, another verifier identity, taboo/min sources,
a hand-built result, an EMPTY result for another cell, a float cell, a rho/cell mismatch."""
import random
import sys
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "impl"))
import srk_adapter as AD  # noqa: E402
import srk_certify as S  # noqa: E402
import srk_gate as GT  # noqa: E402

VID = "sha256:test-verifier"
E0 = F(1, 2)                                   # manufactured decoy drift centre (not a tail cell)


def gate_for(cell, gam, geometry=None, kernel="whole", d_lo=None, vid=VID):
    geometry = dict(AD.REAL_GEOMETRY if geometry is None else geometry)
    wb, subs = S.cell_blocks(*cell)
    certs, verd = [], {}
    for i, g in gam.items():
        for b in subs:
            c = {"schema": "SRK_CERT/1", "status": "CERTIFIED", "geometry": geometry,
                 "block": [S.fstr(b[0]), S.fstr(b[1])], "weight_block": [S.fstr(wb[0]), S.fstr(wb[1])],
                 "e_c": S.fstr((b[0] + b[1]) / 2), "hermite_index": i, "degree": 8, "kernel": kernel,
                 "Gamma": S.fstr(g), "V0": {}, "V1": {}, "W0": {}, "W1": {}}
            c["sha256"] = GT.canonical_sha(c)
            certs.append(c)
            verd[c["sha256"]] = "ACCEPT"
    return GT.gate(cell[0], cell[1], geometry, kernel, certs, verd, d_lo=d_lo, verdict_source=vid)


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
    keys = ["repro_empty", "inside", "big_gamma_unchanged", "tamper_refused", "Gneq0_refused", "wrongcoef_refused",
            "raw_dict_refused", "other_cell_refused", "other_geometry_refused", "other_verifier_refused",
            "taboo_source_refused", "min_source_refused", "empty_other_cell_refused", "float_cell_refused",
            "rho_mismatch_refused", "hand_built_refused", "partial_gate_is_safe", "geometry_override_impossible",
            "real_geometry_immutable"]
    res = {k: 0 for k in keys}
    res["cases"] = 0
    for seed in range(1, 21):
        meas, k, A, sig = manufactured(seed)
        lo, hi, obj = stub_tail_enclosure(meas, k, A, sig, 5)
        cell = (E0 - meas["rho"], E0 + meas["rho"])
        res["cases"] += 1

        def enc(gr, o=obj, coef=coefficients, c=cell, vid=VID):
            return AD.srk_enclosure(meas, A, 5, c, gr, o, (lo, hi), coef, verifier_id=vid)
        e = enc(GT.GateResult.empty(*cell, AD.REAL_GEOMETRY))
        res["repro_empty"] += (e["lo"], e["hi"]) == (lo, hi)
        gam = {i: A["A0"] * k[i] * F(random.Random(seed * 7 + i).randint(30, 99), 100) for i in (1, 2, 3, 4)}
        gr = gate_for(cell, gam)
        out = enc(gr)
        res["inside"] += (out["lo"] >= lo and out["hi"] <= hi and (out["lo"], out["hi"]) != (lo, hi))
        outb = enc(gate_for(cell, {i: A["A0"] * k[i] * 10 ** 6 for i in (1, 2, 3, 4)}))
        res["big_gamma_unchanged"] += (outb["lo"], outb["hi"]) == (lo, hi)
        bad = {r: dict(v) for r, v in obj.items()}
        bad[2]["rad"] = bad[2]["rad"] * F(99, 100)
        res["tamper_refused"] += refuses(lambda: enc(gr, o=bad))
        badg = {r: dict(v) for r, v in obj.items()}
        badg[0]["abs_G_at_a"] = F(1, 10)
        res["Gneq0_refused"] += refuses(lambda: enc(gr, o=badg))
        wrong = lambda m: [(a, b, c, d * (F(11, 10) if a == "W" else 1)) for a, b, c, d in coefficients(m)]  # noqa
        res["wrongcoef_refused"] += refuses(lambda: enc(gr, coef=wrong))
        res["raw_dict_refused"] += refuses(lambda: enc(gam))
        other = (cell[0] + F(1, 1024), cell[1] + F(1, 1024))
        res["other_cell_refused"] += refuses(lambda: enc(gate_for(other, gam)))
        res["other_geometry_refused"] += refuses(lambda: enc(gate_for(cell, gam, geometry={"h": "3/1", "k": "1/2"})))
        # review R2 C1 (reviewer probe b1-triple-prime): a caller can no longer override the geometry
        try:
            AD.srk_enclosure(meas, A, 5, cell, gate_for(cell, gam, geometry={"h": "3/1", "k": "1/2"}), obj, (lo, hi),
                             coefficients, verifier_id=VID, geometry={"h": "3/1", "k": "1/2"})
        except TypeError:
            res["geometry_override_impossible"] += 1
        except AD.AdapterRefusal:
            pass
        try:
            AD.REAL_GEOMETRY["h"] = "3/1"
        except TypeError:
            res["real_geometry_immutable"] += 1
        res["other_verifier_refused"] += refuses(lambda: enc(gr, vid="sha256:another-verifier"))
        dl = {"value": "1/2", "domain": [S.fstr(cell[0]), S.fstr(cell[1])]}
        tab = gate_for(cell, gam, kernel="taboo", d_lo=dl)
        res["taboo_source_refused"] += refuses(lambda: enc(tab))
        res["min_source_refused"] += refuses(lambda: enc(GT.combine(gr, tab)))
        res["empty_other_cell_refused"] += refuses(lambda: enc(GT.GateResult.empty(*other, AD.REAL_GEOMETRY)))
        res["float_cell_refused"] += refuses(lambda: enc(gr, c=(float(cell[0]), cell[1])))
        wide = (cell[0] - F(1, 1024), cell[1])
        res["rho_mismatch_refused"] += refuses(lambda: enc(gate_for(wide, gam), c=wide))
        try:
            GT.GateResult(object(), gamma=gam, cell=cell, geometry=AD.REAL_GEOMETRY, kernel="whole", source="GATE",
                          admitted=(), verdict_source=VID, d_lo=None, report={})
        except TypeError:
            res["hand_built_refused"] += 1
        # a gate result with a missing index value (None) is safe: that index falls back to TC-T
        gp = gate_for(cell, {1: gam[1], 2: gam[2], 3: gam[3]})          # no certificate for index 4
        part = enc(gp)
        res["partial_gate_is_safe"] += (gp.gamma[4] is None and part["lo"] >= lo and part["hi"] <= hi
                                        and all(part["per_r"][r]["branch4"] == "TCT" for r in range(5)))
    ok = all(v == res["cases"] for kk, v in res.items() if kk != "cases")
    return ok, res


if __name__ == "__main__":
    ok, res = run()
    print(res)
    sys.exit(0 if ok else 1)
