"""Stream E (ASSEMBLY): manufactured TC-T-shaped DECOY input objects (seeded, reproducible, synthetic numbers only).

Every decoy is an in-memory bundle in the exact schema consumed by the frozen C2 consumer path (see tptb_tail.py):
the TCT_INPUTS field set of tct_inputs.py, the K1 record's auxiliary_evidence families, the adopted extract's m["5"]
intervals, a cover cell, a supply and optional blocks. Nothing is read from any cell file; no number of any CUSUM
cell is used. Labels are detector "DECOY", m = 5, cell 9000 + i (never a CUSUM index), and every geometry lies
outside the drift band and its mirror (guard_drift is called on each).

Regimes (chosen by construction, and MEASURED on each decoy through the radius decomposition at s = rho):
  "taylor"    order-3 / order-4 profile terms (s f_G, s^2 Env4 and their p1/p0 analogues) dominate the radius;
  "midpoint"  the midpoint residual terms (A0 f_H + 2 A1 f_D + A2 f_F) dominate the radius;
  "mixed"     comparable.
Centre sign: sign of C = W + (1/5) sum H_hat_r(a) (which side of the transport binds). Cap modes: "loose" (the K1
cap R2_interval never binds), "cut" (binds inside the cell on the binding side), "cut_both".
Decoy "committed" record: H_exact from the frozen independent crosscheck (tct_rule.tail_enclosure_crosscheck),
Gamma_exact / M_after_exact from own exact arithmetic, per-r values from tptb_tail.rederive_tuple (own code).
"""
from __future__ import annotations

import importlib.util
import random
import sys
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve()


def _load(name, path):
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


TB = _load("c308E_tptb_tail", HERE.parent / "tptb_tail.py")
Q = TB.Q
Q.install_import_guard()

GEOMS = [(F(1, 4), F(1, 64)), (F(1, 2), F(1, 50)), (F(3, 4), F(1, 32)), (F(1), F(1, 40)),
         (F(11, 10), F(1, 50)), (F(3), F(1, 32)), (F(7, 2), F(1, 25)), (F(4), F(1, 64))]


def U(rng, lo, hi, den=1000) -> F:
    """a rational uniformly-ish in [lo, hi] (lo, hi Fractions/ints) on a grid of 1/den of the range."""
    lo, hi = F(lo), F(hi)
    return lo + (hi - lo) * F(rng.randint(0, den), den)


def sc(rng, mant_lo, mant_hi, exp) -> F:
    return U(rng, mant_lo, mant_hi) * F(10) ** exp


def _meas(rng, regime: str, e0: F, rho: F, cell: int) -> tuple[dict, dict]:
    if regime == "taylor":
        k = [U(rng, F(3, 10), F(9, 10))] + [U(rng, F(1, 2), 3) for _ in range(4)]
        jn = [U(rng, F(3, 10), F(9, 10))] + [U(rng, F(1, 2), 3) for _ in range(4)]
        s0 = [U(rng, F(1, 2), 5) for _ in range(5)]
        dl = (sc(rng, 1, 9, -7), sc(rng, 1, 9, -7), sc(rng, 1, 9, -7))
        eps = lambda: [sc(rng, 1, 9, -8), sc(rng, 1, 9, -8), sc(rng, 1, 9, -8), sc(rng, 1, 9, -6)]  # noqa: E731
        sup = lambda: {x: U(rng, F(1, 2), 20) for x in ("F", "D", "H")}  # noqa: E731
        cs_v, me_v = (lambda: U(rng, 1, 50)), (lambda: sc(rng, 1, 9, -6))
    elif regime == "midpoint":
        k = [sc(rng, 1, 9, -4) for _ in range(5)]
        jn = [sc(rng, 1, 9, -4) for _ in range(5)]
        s0 = [sc(rng, 1, 9, -4) for _ in range(5)]
        dl = (sc(rng, 1, 9, -3), sc(rng, 1, 9, -2), sc(rng, 1, 9, -1))
        eps = lambda: [sc(rng, 1, 9, -6) for _ in range(4)]  # noqa: E731
        sup = lambda: {x: sc(rng, 1, 9, -3) for x in ("F", "D", "H")}  # noqa: E731
        cs_v, me_v = (lambda: sc(rng, 1, 9, -3)), (lambda: sc(rng, 1, 9, -7))
    else:  # mixed
        k = [U(rng, F(1, 10), F(1, 2)) for _ in range(5)]
        jn = [U(rng, F(1, 10), F(1, 2)) for _ in range(5)]
        s0 = [U(rng, F(1, 10), 1) for _ in range(5)]
        dl = (sc(rng, 1, 9, -4), sc(rng, 1, 9, -3), sc(rng, 1, 9, -2))
        eps = lambda: [sc(rng, 1, 9, -6) for _ in range(4)]  # noqa: E731
        sup = lambda: {x: U(rng, F(1, 10), 2) for x in ("F", "D", "H")}  # noqa: E731
        cs_v, me_v = (lambda: U(rng, F(1, 10), 5)), (lambda: sc(rng, 1, 9, -6))
    meas = {"schema": "rebaseguard.p5y.k5.m5-tail.tct-inputs.v1", "mode": "decoy", "cell": cell,
            "k1_record_sha256": "decoy", "identity_gate": {"identical": True},
            "e0": str(e0), "rho": str(rho), "left": str(e0 - rho), "right": str(e0 + rho),
            "norms": {"k": [str(v) for v in k], "j": [str(v) for v in jn]}, "sup_S0": [str(v) for v in s0],
            "r": {}, "W2": {}, "order3_fields_present": False}
    for r in range(5):
        meas["r"][str(r)] = {"delta_F": str(dl[0] * U(rng, F(1, 2), 2)), "delta_D": str(dl[1] * U(rng, F(1, 2), 2)),
                             "delta_H": str(dl[2] * U(rng, F(1, 2), 2)), "eps_src": [str(v) for v in eps()],
                             "sup": {x: str(v) for x, v in sup().items()}, "H_at_a": ["0", "0"]}
    aux = {"candidate_suprema": {}, "midpoint_eps": {}}
    for h in range(1, 5):
        aux["candidate_suprema"][f"h:{h}:3"] = str(cs_v())
        aux["midpoint_eps"][f"h:{h}:3"] = str(me_v())
    aux["candidate_suprema"]["Sclosed:0:3"] = str(cs_v())
    aux["midpoint_eps"]["Sclosed:3"] = str(me_v())
    for r in range(1, 5):
        aux["candidate_suprema"][f"S:{r}:3"] = str(cs_v())
        aux["midpoint_eps"][f"S:{r}:3"] = str(me_v())
    return meas, aux


def _supply(rng, meas, with_sources: bool):
    if not with_sources:
        return {"supply": {"A0": str(U(rng, 2, 8)), "A1": str(U(rng, 1, 10)), "A2": str(U(rng, 1, 30))}}
    tau = U(rng, 1, 6)
    return {"supply_sources": {
        "G": {"kind": "lemma_G", "C_upper": str(U(rng, 2, 8))},
        "X": {"kind": "lemma_Dv_prime", "Abar": str(U(rng, 1, 5)), "tau": str(tau), "C_T": str(tau + U(rng, 0, 4)),
              "D_lo": str(U(rng, F(1, 5), 1)), "D1": str(U(rng, 0, F(1, 2))), "D2": str(U(rng, 0, F(1, 2)))}}}


def radius_decomposition(tup: dict, S: tuple, rho: F) -> dict:
    """Split rad_r(rho) = A0 p2 + 2 A1 p1 + A2 p0 into the midpoint part (the s^0 coefficients f_H, f_D, f_F) and
    the Taylor-growth part (everything carrying s). Averaged over r. Decoy diagnostics only."""
    mid = tay = F(0)
    for t in tup.values():
        r0 = S[0] * t["fH"] + 2 * S[1] * t["fD"] + S[2] * t["fF"]
        full = TB.rad_at(t, S, rho)
        mid += r0
        tay += full - r0
    tot = mid + tay
    return {"midpoint_share": float(mid / tot), "taylor_share": float(tay / tot)}


def make_decoy(i: int, seed: int, regime: str, centre_sign: int, cap_mode: str, nblocks: int,
               with_sources: bool = False, e0_edge: bool = False) -> dict:
    rng = random.Random(1_000_003 * seed + 17 * i)
    e0, rho = GEOMS[rng.randrange(len(GEOMS))]
    Q.guard_drift(e0 - rho, e0 + rho)
    cell = 9000 + i
    meas, aux = _meas(rng, regime, e0, rho, cell)
    bundle = {"label": {"detector": "DECOY", "m": 5, "cell": cell}, "meas": meas, "aux": aux,
              "cover": {"index": cell, "detector": "DECOY", "left": str(e0 - rho), "right": str(e0 + rho),
                        "e0": str(e0), "rho": str(rho)}}
    bundle.update(_supply(rng, meas, with_sources))
    S, _ = TB.supply_from(bundle, meas)
    tup = TB.rederive_tuple(meas, aux)
    radm = sum(TB.rad_at(t, S, rho) for t in tup.values()) / 5
    # centres: sign-controlled, of the order of the radius; widths small
    for r in range(5):
        c = centre_sign * U(rng, F(3, 10), 3) * radm
        w = U(rng, F(1, 100), F(1, 5)) * radm
        meas["r"][str(r)]["H_at_a"] = [str(c - w), str(c + w)]
    for r in range(4):
        for jj in range(4 - r):
            wc = U(rng, -1, 1) * radm / 10
            wd = U(rng, F(1, 100), F(1, 10)) * radm / 10
            meas["W2"][f"{r}:{jj}"] = [str(wc - wd), str(wc + wd)]
    tup = TB.rederive_tuple(meas, aux)
    ext = {"terms": [dict(tup[r]) for r in range(5)], "W": None}
    Wlo = Whi = F(0)
    for kind, r, jj, cc in TB.R.coefficients(5):
        if kind == "W":
            a, b = (F(v) for v in meas["W2"][f"{r}:{jj}"])
            Wlo += cc * a
            Whi += cc * b
    ext["W"] = (Wlo, Whi)
    ext["rho"] = rho
    lo, hi = TB.band_at(ext, S, rho, None)
    lo0, hi0 = TB.band_at(ext, S, F(0), None)
    d = U(rng, F(1, 10), 1) * (hi - lo)
    lower_binds = abs(lo) >= abs(hi)
    R2lo, R2hi = lo - d, hi + d
    if cap_mode in ("cut", "cut_both"):
        th = U(rng, F(1, 5), F(4, 5))
        if lower_binds or cap_mode == "cut_both":
            R2lo = lo + th * (lo0 - lo)
        if (not lower_binds) or cap_mode == "cut_both":
            R2hi = hi - th * (hi - hi0)
    a_, b_ = max(R2lo, lo), min(R2hi, hi)
    magH = max(abs(a_), abs(b_))
    M0 = max(abs(R2lo), abs(R2hi))
    Dlo = U(rng, F(1, 10), 1)
    g_hi = -U(rng, F(1, 2), F(3, 2)) * rho * (e0 + rho) * magH  # c308-quarantine: literal-ok (g_hi scale factor, not a drift)
    Rhi = g_hi + e0 * Dlo
    bundle["adopted_m5"] = {"R_interval": {"lo": str(Rhi - F(1, 1000)), "hi": str(Rhi)},
                            "D_interval": {"lo": str(Dlo), "hi": str(Dlo + F(1, 1000))},
                            "R2_interval": {"lo": str(R2lo), "hi": str(R2hi)}, "M_R2": str(M0)}
    # blocks: an exact tiling of the cell, each triple = S * u (componentwise u in [1/4, 1])
    x_lo, x_hi = e0 - rho, e0 + rho
    if nblocks > 0:
        edges = set()
        if e0_edge and nblocks > 1:
            edges.add(e0)
        while len(edges) < nblocks - 1:
            edges.add(x_lo + 2 * rho * F(rng.randint(1, 999), 1000))
        ed = [x_lo] + sorted(edges) + [x_hi]
        bl = []
        for a, b in zip(ed, ed[1:]):
            u = [U(rng, F(1, 4), 1) for _ in range(3)]
            if rng.random() < 0.25:
                u = [F(1)] * 3
            bl.append({"e_lo": str(a), "e_hi": str(b), "A0": str(S[0] * u[0]), "A1": str(S[1] * u[1]),
                       "A2": str(S[2] * u[2])})
        bundle["blocks"] = bl
    # decoy "committed" record
    Hx = TB.T.tail_enclosure_crosscheck(meas, aux, dict(zip(TB.FIELDS, S)), 5, None)
    Hf = (max(R2lo, Hx[0]), min(R2hi, Hx[1]))
    Mc = min(M0, max(abs(Hf[0]), abs(Hf[1])))
    bundle["committed"] = {"H_exact": [str(Hx[0]), str(Hx[1])], "M_after_exact": str(Mc),
                           "Gamma_exact": str(g_hi + rho * (e0 + rho) * Mc),
                           "per_r": {str(r): {x: str(tup[r][x]) for x in TB.TUPLE + ("abs_G",)}
                                     | {"H_at_a": [str(v) for v in tup[r]["H_at_a"]]} for r in range(5)}}
    C = Wlo + sum(tup[r]["H_at_a"][0] + tup[r]["H_at_a"][1] for r in range(5)) / 10
    bundle["decoy_meta"] = {"seed": seed, "index": i, "regime": regime, "centre_sign_requested": centre_sign,
                            "centre_sign_realized": (1 if C > 0 else -1), "cap_mode": cap_mode,
                            "nblocks": nblocks, "with_supply_sources": with_sources, "e0_edge": e0_edge,
                            "lower_end_binds": lower_binds,
                            "radius_decomposition": radius_decomposition(tup, S, rho)}
    return bundle


def decoy_set(seed: int = 20260928) -> list:
    """The validation set: regimes x centre signs x cap modes, with varied block counts."""
    out, i = [], 0
    for regime in ("taylor", "midpoint", "mixed"):
        for sign in (1, -1):
            for cap_mode in ("loose", "cut", "cut_both"):
                nb = (1, 2, 3, 4, 6)[i % 5]
                out.append(make_decoy(i, seed, regime, sign, cap_mode, nb, with_sources=(i % 2 == 1),
                                      e0_edge=(i % 3 == 0)))
                i += 1
    return out


if __name__ == "__main__":
    import json
    ds = decoy_set()
    print(json.dumps([d["decoy_meta"] for d in ds], indent=1))
