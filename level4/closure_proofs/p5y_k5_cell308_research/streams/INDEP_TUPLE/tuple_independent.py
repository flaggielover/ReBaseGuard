"""Stream F3 (INDEP_TUPLE): an independent, standard-library-only re-derivation of the theorem TC-T per-r
Taylor-profile tuple that the block-resolved transport (TPT-B) consumes.

Sources (theorem TEXT only; no implementation of the primary or of any frozen rule was read before the freeze):
  * LP/p5y_k5_m5_tail_closure/theorem/THEOREM_TCT.md sections 0-4: Lemma G (A0, A1, A2 from C_upper and k),
    premise (P2') (zero order-3 candidate, f_G, s_G = 0, |G_hat(a)| = 0, and the stated implementation convention
    "fG = delta_G + eps_src[3]"), premise (P3') (the pure J/h Leibniz tower, the midpoint tower -> sigma3 only,
    the cell tower with the rho mean-value correction -> sigma4 only) and statement section 4 (p0, p1, p2, rad_r and
    Env4 at s_G = 0). Its section 5 was not read.
  * LP/p5y_k5_lower_front_order3/theorem/THEOREM_TC.md: (P2) f_F, f_D, f_H from the midpoint residuals and the
    midpoint source-node errors (src(0,k) = Sclosed:k, src(r,k) = S:r:k), (P3) the general Env4, section 3 (p0, p1,
    p2, rad_r and the whole-cell enclosure with the assembly coefficients c(m): F_r -> 1/m for r < m,
    W_(r, t-r-1) -> 1/t - 1/m for 1 <= t < m).
  * OV/streams/E_assembly/THEOREM_TPT.md section 2: Lemma TC-P (p_j(s), rad_r(s)) and the profile enclosure
    R''_m(t) in sum_r (1/m)[H_hat_r(a) -+ (rad_r(s) + s|G_hat_r(a)|)] + sum c W_(r,j).
Input format learned from NS/streams/ASSEMBLY/decoy_gen.py and the output-schema lines of the tail replay measurement
module in LP/p5y_k5_m5_tail_closure/code (docstring, _src and the emitted dict only).

Everything is exact (fractions.Fraction). Floats are refused. Profiles are returned as ascending coefficient lists in
s = |t - e0|. The module computes nothing for any real CUSUM cell: it refuses the quarantined cell labels and any cell
geometry that meets the quarantined drift band or its mirror, and it opens no file.

Public API
  parse(meas, aux, m=5)                 -> strict exact view of the inputs (refuses malformed / unsafe input)
  towers(k, j, sup_S0, aux, rho)        -> pure, midpoint and cell h-towers, sigma3 / sigma4 per r
  tuple_tct(meas, aux, S, m=5)          -> per r: fF fD fH fG Env4, the centre interval, abs_G (= 0), sigma3,
                                           sigma4, delta_G, fG_theorem, and the profiles p0 p1 p2 rad (for S)
  lemma_G(C_upper, k)                   -> (A0, A1, A2) of Lemma G
  w_enclosure(meas, aux, m=5)           -> sum_(r,j) c(m) W_(r,j) (exact interval)
  profile_band(res, s)                  -> [lo(s), hi(s)] of the profile enclosure
  whole_cell(res)                       -> the whole-cell enclosure H_m at s = rho
  canonical(res), digest(res)           -> canonical JSON text / sha256 of a result
"""
from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from math import comb

SCHEMA_OUT = "p5y.k5.c308-research.indep-tuple.v1"
NORDERS = 5            # k_0..k_4, j_0..j_4, sup_S0[0..4]
NR = 5                 # sources r = 0..4 in the measurement record
NH = 4                 # h_1..h_4

# Quarantine (governance boilerplate, restated from config/TARGET_QUARANTINE_308.json; stdlib only).
_BAND = (Fraction(6, 5), Fraction(13, 5))  # c308-quarantine: literal-ok (quarantined drift band, a guard)
_QUARANTINED_LABELS = frozenset(range(305, 310))  # c308-quarantine: literal-ok (guard set, refused)


class TupleRefusal(ValueError):
    """Fail-closed refusal of malformed, inexact or out-of-scope input."""


# ------------------------------------------------------------------------------------------------ exact parsing

def q(x, what: str = "value") -> Fraction:
    """Exact rational from int / Fraction / exact numeric string. Floats, bools, NaN/inf are refused."""
    if isinstance(x, bool):
        raise TupleRefusal(f"{what}: bool is not a number")
    if isinstance(x, Fraction):
        return x
    if isinstance(x, int):
        return Fraction(x)
    if isinstance(x, str):
        try:
            return Fraction(x.strip())
        except (ValueError, ZeroDivisionError) as exc:
            raise TupleRefusal(f"{what}: not an exact rational string {x!r}") from exc
    raise TupleRefusal(f"{what}: inexact or unsupported type {type(x).__name__}")


def qn(x, what: str) -> Fraction:
    v = q(x, what)
    if v < 0:
        raise TupleRefusal(f"{what}: must be >= 0, got {v}")
    return v


def qi(pair, what: str) -> tuple[Fraction, Fraction]:
    if not isinstance(pair, (list, tuple)) or len(pair) != 2:
        raise TupleRefusal(f"{what}: interval must be a pair")
    lo, hi = q(pair[0], what + ".lo"), q(pair[1], what + ".hi")
    if lo > hi:
        raise TupleRefusal(f"{what}: unordered interval [{lo}, {hi}]")
    return lo, hi


def _guard(label, left: Fraction, right: Fraction) -> None:
    try:
        lab = int(label)
    except (TypeError, ValueError):
        lab = None
    if lab is not None and lab in _QUARANTINED_LABELS:
        raise TupleRefusal("QUARANTINED_CELL_LABEL refused")
    a, b = _BAND
    for lo_b, hi_b in ((a, b), (-b, -a)):
        if not (right < lo_b or left > hi_b):
            raise TupleRefusal("QUARANTINED_DRIFT_BAND refused")


def w_keys(m: int) -> list[tuple[int, int, int]]:
    """(r, j, t) with t = r + j + 1, 1 <= t < m, r < t: the W_(r, t-r-1) terms of the assembly (THEOREM_TC s3)."""
    return [(r, t - r - 1, t) for t in range(1, m) for r in range(t)]


def parse(meas: dict, aux: dict, m: int = 5) -> dict:
    """Strict exact view of one measurement record plus its auxiliary evidence."""
    if not isinstance(meas, dict) or not isinstance(aux, dict):
        raise TupleRefusal("meas and aux must be dicts")
    if not (isinstance(m, int) and not isinstance(m, bool) and 1 <= m <= NR):
        raise TupleRefusal(f"m must be an int in 1..{NR}")
    if meas.get("order3_fields_present") is not False:
        raise TupleRefusal("TC-T requires G_hat := 0: order3_fields_present must be exactly False")
    e0, rho = q(meas["e0"], "e0"), q(meas["rho"], "rho")
    left, right = q(meas["left"], "left"), q(meas["right"], "right")
    if rho <= 0:
        raise TupleRefusal("rho must be > 0")
    if left != e0 - rho or right != e0 + rho:
        raise TupleRefusal("cell geometry: need left = e0 - rho and right = e0 + rho exactly")
    _guard(meas.get("cell"), left, right)
    norms = meas["norms"]
    k = [qn(v, f"k[{i}]") for i, v in enumerate(norms["k"])]
    jn = [qn(v, f"j[{i}]") for i, v in enumerate(norms["j"])]
    s0 = [qn(v, f"sup_S0[{i}]") for i, v in enumerate(meas["sup_S0"])]
    if len(k) != NORDERS or len(jn) != NORDERS or len(s0) != NORDERS:
        raise TupleRefusal("norms.k, norms.j and sup_S0 must each have 5 entries")
    rr = meas["r"]
    if sorted(rr) != [str(r) for r in range(NR)]:
        raise TupleRefusal("meas.r must have exactly the keys '0'..'4'")
    per = {}
    for r in range(NR):
        d = rr[str(r)]
        for key in d:
            if key.startswith("G") or key in ("delta_G", "abs_G_at_a", "abs_G", "fG"):
                raise TupleRefusal(f"order-3 field of F {key!r} present at r={r}; TC-T has G_hat := 0")
        eps = [qn(v, f"r{r}.eps_src[{i}]") for i, v in enumerate(d["eps_src"])]
        if len(eps) != 4:
            raise TupleRefusal(f"r{r}.eps_src must have 4 entries (k = 0..3)")
        sup = d["sup"]
        if sorted(sup) != ["D", "F", "H"]:
            raise TupleRefusal(f"r{r}.sup must have exactly F, D, H")
        per[r] = {"delta_F": qn(d["delta_F"], f"r{r}.delta_F"), "delta_D": qn(d["delta_D"], f"r{r}.delta_D"),
                  "delta_H": qn(d["delta_H"], f"r{r}.delta_H"), "eps_src": eps,
                  "sF": qn(sup["F"], f"r{r}.sup.F"), "sD": qn(sup["D"], f"r{r}.sup.D"),
                  "sH": qn(sup["H"], f"r{r}.sup.H"), "H_at_a": qi(d["H_at_a"], f"r{r}.H_at_a")}
    W2 = meas["W2"]
    want = sorted(f"{r}:{j}" for r, j, _t in w_keys(NR))
    if sorted(W2) != want:
        raise TupleRefusal(f"W2 keys must be exactly {want}")
    W = {(int(key.split(":")[0]), int(key.split(":")[1])): qi(v, f"W2[{key}]") for key, v in W2.items()}
    cs, me = aux.get("candidate_suprema", {}), aux.get("midpoint_eps", {})

    def ev(fam, key):
        if key not in fam:
            raise TupleRefusal(f"auxiliary evidence key {key!r} missing")
        return qn(fam[key], key)

    # (P3'): adopted order-3 midpoint bounds. r = 0 is the closed-form source: candidate key 'Sclosed:0:3' and the
    # midpoint-DAG node name of src(0,3) = 'Sclosed:3' (the '_src' convention); 'Sclosed:0:3' accepted as an alias.
    if "Sclosed:3" in me and "Sclosed:0:3" in me and q(me["Sclosed:3"]) != q(me["Sclosed:0:3"]):
        raise TupleRefusal("conflicting midpoint_eps entries for the r = 0 order-3 source")
    me0 = ev(me, "Sclosed:3") if "Sclosed:3" in me else ev(me, "Sclosed:0:3")
    adopted3 = {0: ev(cs, "Sclosed:0:3") + me0}
    for r in range(1, NR):
        adopted3[r] = ev(cs, f"S:{r}:3") + ev(me, f"S:{r}:3")
    adoptedh = {jj: ev(cs, f"h:{jj}:3") + ev(me, f"h:{jj}:3") for jj in range(1, NH + 1)}
    return {"m": m, "e0": e0, "rho": rho, "left": left, "right": right, "k": k, "j": jn, "sup_S0": s0,
            "per": per, "W": W, "adopted3": adopted3, "adoptedh": adoptedh, "cell": meas.get("cell")}


# ------------------------------------------------------------------------------------------------ (P3') towers

def towers(k, jn, s0, adopted3: dict, adoptedh: dict, rho: Fraction) -> dict:
    """THEOREM_TC (P3) / THEOREM_TCT (P3') r2.

    pure tower   T[1,0] = 1, T[1,n] = sup_S0[n-1] (h_1' = -S_0);  T[j,0] = 1, T[j,n] = sum_{i=0..n} C(n,i) k_i T[j-1,n-i]
    midpoint     Tm[j,n] = T[j,n] (n <= 2),  Tm[j,3] = min(T[j,3], adoptedh(j))                       -> sigma3 only
    cell         Tc[j,n] = T[j,n] (n <= 2),  Tc[j,3] = min(T[j,3], adoptedh(j) + rho T[j,4]),
                 Tc[1,4] = T[1,4],  Tc[j,4] = min(sum_i C(4,i) k_i Tc[j-1,4-i], T[j,4]) (j >= 2)        -> sigma4 only
    sigma3(0) = min(sup_S0[3], adopted3(0));  sigma3(r) = min(sum_{i=0..3} C(3,i) j_i Tm[r,3-i], adopted3(r))
    sigma4(0) = sup_S0[4];                    sigma4(r) = sum_{i=0..4} C(4,i) j_i Tc[r,4-i]
    """
    T: dict = {}
    for n in range(5):
        T[1, n] = Fraction(1) if n == 0 else s0[n - 1]
    for jj in range(2, NH + 1):
        T[jj, 0] = Fraction(1)
        for n in range(1, 5):
            T[jj, n] = sum((comb(n, i) * k[i] * T[jj - 1, n - i] for i in range(n + 1)), Fraction(0))
    Tm = {key: v for key, v in T.items() if key[1] <= 2}
    Tc = dict(Tm)
    for jj in range(1, NH + 1):
        Tm[jj, 3] = min(T[jj, 3], adoptedh[jj])
        Tc[jj, 3] = min(T[jj, 3], adoptedh[jj] + rho * T[jj, 4])
    Tc[1, 4] = T[1, 4]
    for jj in range(2, NH + 1):
        Tc[jj, 4] = min(sum((comb(4, i) * k[i] * Tc[jj - 1, 4 - i] for i in range(5)), Fraction(0)), T[jj, 4])
    sig3 = {0: min(s0[3], adopted3[0])}
    sig4 = {0: s0[4]}
    sig3_pure = {0: s0[3]}
    sig4_pure = {0: s0[4]}
    for r in range(1, NR):
        sig3[r] = min(sum((comb(3, i) * jn[i] * Tm[r, 3 - i] for i in range(4)), Fraction(0)), adopted3[r])
        sig4[r] = sum((comb(4, i) * jn[i] * Tc[r, 4 - i] for i in range(5)), Fraction(0))
        sig3_pure[r] = sum((comb(3, i) * jn[i] * T[r, 3 - i] for i in range(4)), Fraction(0))
        sig4_pure[r] = sum((comb(4, i) * jn[i] * T[r, 4 - i] for i in range(5)), Fraction(0))
    return {"T": T, "Tm": Tm, "Tc": Tc, "sigma3": sig3, "sigma4": sig4,
            "sigma3_pure": sig3_pure, "sigma4_pure": sig4_pure}


# ------------------------------------------------------------------------------------------------ envelopes

def env4_general(sigma4, k, rho, sF, sD, sH, sG) -> Fraction:
    """THEOREM_TC (P3): sigma4 + 4k1 sG + 6k2(sH + rho sG) + 4k3(sD + rho sH + rho^2 sG/2)
    + k4(sF + rho sD + rho^2 sH/2 + rho^3 sG/6)."""
    return (sigma4 + 4 * k[1] * sG + 6 * k[2] * (sH + rho * sG) + 4 * k[3] * (sD + rho * sH + rho ** 2 * sG / 2)
            + k[4] * (sF + rho * sD + rho ** 2 * sH / 2 + rho ** 3 * sG / 6))


def env4_tct(sigma4, k, rho, sF, sD, sH) -> Fraction:
    """THEOREM_TCT s4: Env4 = sigma4 + 6k2 sH + 4k3(sD + rho sH) + k4(sF + rho sD + rho^2 sH/2)  (s_G = 0)."""
    return sigma4 + 6 * k[2] * sH + 4 * k[3] * (sD + rho * sH) + k[4] * (sF + rho * sD + rho ** 2 * sH / 2)


# ------------------------------------------------------------------------------------------------ polynomials

def padd(*ps) -> list:
    n = max(len(p) for p in ps)
    return [sum((p[i] for p in ps if i < len(p)), Fraction(0)) for i in range(n)]


def pscale(c, p) -> list:
    return [c * a for a in p]


def peval(p, s) -> Fraction:
    s = q(s, "s")
    acc = Fraction(0)
    for a in reversed(p):
        acc = acc * s + a
    return acc


def profiles(t: dict, S) -> dict:
    """Lemma TC-P: p0(s) = fF + s fD + s^2 fH/2 + s^3 fG/6 + s^4 Env4/24, p1(s) = fD + s fH + s^2 fG/2 + s^3 Env4/6,
    p2(s) = fH + s fG + s^2 Env4/2, rad_r(s) = A0 p2(s) + 2 A1 p1(s) + A2 p0(s)."""
    A0, A1, A2 = S
    p0 = [t["fF"], t["fD"], t["fH"] / 2, t["fG"] / 6, t["Env4"] / 24]
    p1 = [t["fD"], t["fH"], t["fG"] / 2, t["Env4"] / 6]
    p2 = [t["fH"], t["fG"], t["Env4"] / 2]
    rad = padd(pscale(A0, p2), pscale(2 * A1, p1), pscale(A2, p0))
    return {"p0": p0, "p1": p1, "p2": p2, "rad": rad}


# ------------------------------------------------------------------------------------------------ supply

def lemma_G(C_upper, k) -> tuple[Fraction, Fraction, Fraction]:
    """THEOREM_TCT Lemma G: A0 = C, A1 = k1 C^2, A2 = k2 C^2 + 2 k1^2 C^3."""
    C = qn(C_upper, "C_upper")
    k1, k2 = qn(k[1], "k1"), qn(k[2], "k2")
    return C, k1 * C ** 2, k2 * C ** 2 + 2 * k1 ** 2 * C ** 3


def supply_triple(S) -> tuple[Fraction, Fraction, Fraction]:
    if isinstance(S, dict):
        S = (S["A0"], S["A1"], S["A2"])
    if len(S) != 3:
        raise TupleRefusal("supply must be (A0, A1, A2)")
    return tuple(qn(v, f"A{i}") for i, v in enumerate(S))


# ------------------------------------------------------------------------------------------------ the tuple

def tuple_tct(meas: dict, aux: dict, S, m: int = 5, *, fG_adds_eps_src3: bool = True) -> dict:
    """Per r in 0..m-1 the TC-T tuple and profiles.

    f_F = delta_F + eps_src[0], f_D = delta_D + eps_src[1], f_H = delta_H + eps_src[2]           (THEOREM_TC (P2))
    delta_G = 3 k1 sH + 3 k2 sD + k3 sF + sigma3;  f_G = delta_G + eps_src[3]                    (THEOREM_TCT (P2'))
      (fG_theorem = delta_G is the bare premise; the '+ eps_src[3]' allowance is the implementation convention the
       theorem text states, 'fG = delta_G + eps_src[3]', and is the default here)
    Env4 = env4_tct(sigma4, ...)                                                                   (THEOREM_TCT s4)
    centre = H_at_a interval (H_hat_r(a)), abs_G = 0                                              (P2')
    """
    P = parse(meas, aux, m)
    A = supply_triple(S)
    tw = towers(P["k"], P["j"], P["sup_S0"], P["adopted3"], P["adoptedh"], P["rho"])
    k, rho = P["k"], P["rho"]
    per = {}
    for r in range(m):
        d = P["per"][r]
        sF, sD, sH = d["sF"], d["sD"], d["sH"]
        dG = 3 * k[1] * sH + 3 * k[2] * sD + k[3] * sF + tw["sigma3"][r]
        t = {"fF": d["delta_F"] + d["eps_src"][0], "fD": d["delta_D"] + d["eps_src"][1],
             "fH": d["delta_H"] + d["eps_src"][2],
             "fG": dG + d["eps_src"][3] if fG_adds_eps_src3 else dG, "fG_theorem": dG, "delta_G": dG,
             "Env4": env4_tct(tw["sigma4"][r], k, rho, sF, sD, sH),
             "sigma3": tw["sigma3"][r], "sigma4": tw["sigma4"][r],
             "H_at_a": d["H_at_a"], "abs_G": Fraction(0)}
        t.update(profiles(t, A))
        per[r] = t
    return {"schema": SCHEMA_OUT, "m": m, "e0": P["e0"], "rho": rho, "S": A, "per_r": per,
            "W": w_enclosure_parsed(P, m), "towers": tw}


def w_enclosure_parsed(P: dict, m: int) -> tuple[Fraction, Fraction]:
    lo = hi = Fraction(0)
    for r, jj, t in w_keys(m):
        c = Fraction(1, t) - Fraction(1, m)
        a, b = P["W"][r, jj]
        lo += c * a
        hi += c * b
    return lo, hi


def w_enclosure(meas: dict, aux: dict, m: int = 5) -> tuple[Fraction, Fraction]:
    """sum_{1<=t<m} sum_{r<t} (1/t - 1/m) W_(r, t-r-1) with nonnegative coefficients (THEOREM_TC s3)."""
    return w_enclosure_parsed(parse(meas, aux, m), m)


def profile_band(res: dict, s) -> tuple[Fraction, Fraction]:
    """[lo(s), hi(s)] = W + sum_{r<m} (1/m)[H_lo_r - rad_r(s) - s|G_r(a)|, H_hi_r + rad_r(s) + s|G_r(a)|]."""
    s = q(s, "s")
    if s < 0 or s > res["rho"]:
        raise TupleRefusal("s must lie in [0, rho]")
    m = res["m"]
    lo, hi = res["W"]
    for r in range(m):
        t = res["per_r"][r]
        half = peval(t["rad"], s) + s * t["abs_G"]
        lo += (t["H_at_a"][0] - half) / m
        hi += (t["H_at_a"][1] + half) / m
    return lo, hi


def whole_cell(res: dict) -> tuple[Fraction, Fraction]:
    """H_m of THEOREM_TC s3 / THEOREM_TCT s4: the profile enclosure at s = rho."""
    return profile_band(res, res["rho"])


def rad_at(res: dict, r: int, s) -> Fraction:
    return peval(res["per_r"][r]["rad"], s)


# ------------------------------------------------------------------------------------------------ canonical form

TUPLE_FIELDS = ("fF", "fD", "fH", "fG", "Env4")


def canonical(res: dict) -> str:
    def fs(x):
        return str(x)
    out = {"schema": res["schema"], "m": res["m"], "e0": fs(res["e0"]), "rho": fs(res["rho"]),
           "S": [fs(v) for v in res["S"]], "W": [fs(v) for v in res["W"]], "per_r": {}}
    for r, t in res["per_r"].items():
        out["per_r"][str(r)] = {
            **{f: fs(t[f]) for f in TUPLE_FIELDS + ("fG_theorem", "delta_G", "sigma3", "sigma4", "abs_G")},
            "H_at_a": [fs(v) for v in t["H_at_a"]],
            **{p: [fs(v) for v in t[p]] for p in ("p0", "p1", "p2", "rad")}}
    wc = whole_cell(res)
    out["whole_cell_at_rho"] = [fs(wc[0]), fs(wc[1])]
    return json.dumps(out, sort_keys=True, separators=(",", ":"))


def digest(res: dict) -> str:
    return hashlib.sha256(canonical(res).encode()).hexdigest()


# ------------------------------------------------------------------------------------------------ self-test

def _fixture(seed: int = 7):
    """A tiny hand-made TC-T-shaped fixture (synthetic numbers; geometry outside the band; label not a CUSUM cell)."""
    import random
    rng = random.Random(seed)

    def u(lo, hi, den=97):
        return Fraction(lo) + (Fraction(hi) - Fraction(lo)) * Fraction(rng.randint(0, den), den)
    e0, rho = Fraction(1, 2), Fraction(1, 40)
    meas = {"cell": 90001, "e0": str(e0), "rho": str(rho), "left": str(e0 - rho), "right": str(e0 + rho),
            "norms": {"k": [str(u(0, 1)) for _ in range(5)], "j": [str(u(0, 1)) for _ in range(5)]},
            "sup_S0": [str(u(0, 3)) for _ in range(5)], "r": {}, "W2": {}, "order3_fields_present": False}
    for r in range(NR):
        c = u(-1, 1)
        meas["r"][str(r)] = {"delta_F": str(u(0, Fraction(1, 100))), "delta_D": str(u(0, Fraction(1, 50))),
                             "delta_H": str(u(0, Fraction(1, 10))), "eps_src": [str(u(0, Fraction(1, 1000)))
                                                                                  for _ in range(4)],
                             "sup": {"F": str(u(0, 2)), "D": str(u(0, 2)), "H": str(u(0, 2))},
                             "H_at_a": [str(c - Fraction(1, 64)), str(c + Fraction(1, 64))]}
    for r, jj, _t in w_keys(NR):
        c = u(-1, 1) / 10
        meas["W2"][f"{r}:{jj}"] = [str(c - Fraction(1, 128)), str(c + Fraction(1, 128))]
    aux = {"candidate_suprema": {"Sclosed:0:3": str(u(0, 5))}, "midpoint_eps": {"Sclosed:3": str(u(0, 1) / 10**6)}}
    for x in range(1, 5):
        aux["candidate_suprema"][f"S:{x}:3"] = str(u(0, 5))
        aux["midpoint_eps"][f"S:{x}:3"] = str(u(0, 1) / 10**6)
        aux["candidate_suprema"][f"h:{x}:3"] = str(u(0, 5))
        aux["midpoint_eps"][f"h:{x}:3"] = str(u(0, 1) / 10**6)
    return meas, aux


def _selftest() -> dict:
    import copy
    checks = {}
    meas, aux = _fixture()
    k = [q(v) for v in meas["norms"]["k"]]
    S = lemma_G(Fraction(5, 2), k)  # c308-quarantine: literal-ok (a C_upper constant, not a drift)
    res = tuple_tct(meas, aux, S)
    rho = res["rho"]
    grid = [Fraction(i, 7) * rho for i in range(8)]
    # 1. rad polynomial = A0 p2 + 2A1 p1 + A2 p0 pointwise; p_j have the Taylor coefficients
    ok = True
    for t in res["per_r"].values():
        for s in grid:
            direct = S[0] * peval(t["p2"], s) + 2 * S[1] * peval(t["p1"], s) + S[2] * peval(t["p0"], s)
            ok &= direct == peval(t["rad"], s)
    checks["rad_is_A0p2_2A1p1_A2p0"] = ok
    # 2. Taylor tightness: phi(x) = fF + fD x + fH x^2/2 + fG x^3/6 + Env4 x^4/24 has phi'''' = Env4 and
    #    phi^(j)(s) = p_{2-j}(s) exactly for j = 0, 1, 2 (the Lemma TC-P bound is attained)
    ok = True
    for t in res["per_r"].values():
        phi = [t["fF"], t["fD"], t["fH"] / 2, t["fG"] / 6, t["Env4"] / 24]
        d1 = [i * phi[i] for i in range(1, 5)]
        d2 = [i * d1[i] for i in range(1, 4)]
        ok &= phi == t["p0"] and d1 == t["p1"] and d2 == t["p2"]
    checks["taylor_coefficients_attained"] = ok
    # 3. Lemma G is the generic K1 DAG rule at s = 0: C f_H + C k2 C f_F + 2 k1 C (C f_D + C k1 C f_F)
    C = S[0]
    ok = True
    for t in res["per_r"].values():
        epsF = C * t["fF"]
        epsD = C * (t["fD"] + k[1] * epsF)
        epsH = C * (t["fH"] + k[2] * epsF + 2 * k[1] * epsD)
        ok &= epsH == t["rad"][0]
    checks["lemmaG_equals_K1_DAG_at_s0"] = ok
    # 4. Env4 of TC-T is TC (P3) at s_G = 0; a positive s_G strictly enlarges it when some k_i > 0
    P = parse(meas, aux)
    ok = True
    for r, t in res["per_r"].items():
        d = P["per"][r]
        g0 = env4_general(t["sigma4"], k, rho, d["sF"], d["sD"], d["sH"], Fraction(0))
        ok &= g0 == t["Env4"]
        ok &= env4_general(t["sigma4"], k, rho, d["sF"], d["sD"], d["sH"], Fraction(1)) > t["Env4"]
    checks["env4_tct_is_tc_at_sG0"] = ok
    # 5. hand tower on a small exact example
    kk = [Fraction(1, 2), Fraction(1), Fraction(0), Fraction(0), Fraction(0)]
    jj = [Fraction(1), Fraction(0), Fraction(0), Fraction(0), Fraction(0)]
    s0 = [Fraction(1), Fraction(2), Fraction(3), Fraction(4), Fraction(5)]
    big = {r: Fraction(10**6) for r in range(5)}
    tw = towers(kk, jj, s0, big, {x: Fraction(10**6) for x in range(1, 5)}, Fraction(1, 10))
    # h1: [1, 1, 2, 3, 4]; h2^(n) = 1/2 h1^(n) + n h1^(n-1): [1, 3/2, 3, 15/2, 14]
    exp_h2 = [Fraction(1), Fraction(3, 2), Fraction(3), Fraction(15, 2), Fraction(14)]  # c308-quarantine: literal-ok (tower values)
    checks["hand_tower_h2"] = [tw["T"][2, n] for n in range(5)] == exp_h2
    checks["hand_sigma_r2_is_h2"] = tw["sigma3"][2] == exp_h2[3] and tw["sigma4"][2] == exp_h2[4]
    tw2 = towers(kk, jj, s0, big, {1: Fraction(1), 2: Fraction(1), 3: Fraction(1), 4: Fraction(1)},
                 Fraction(1, 10))
    # midpoint: Tm[2,3] = min(15/2, 1) = 1 -> sigma3(2) = 1; cell: Tc[2,3] = min(15/2, 1 + 14/10) = 12/5,
    # Tc[1,3] = min(3, 1 + 4/10) = 7/5, Tc[1,4] = T[1,4] = 4, Tc[2,4] = min(1/2*4 + 4*1*7/5, 14) = 38/5
    checks["hand_mid_cell_towers"] = (tw2["sigma3"][2] == 1 and tw2["Tc"][2, 3] == Fraction(12, 5)  # c308-quarantine: literal-ok (tower value)
                                      and tw2["Tc"][1, 3] == Fraction(7, 5) and tw2["Tc"][2, 4] == Fraction(38, 5)  # c308-quarantine: literal-ok (tower value)
                                      and tw2["sigma4"][2] == Fraction(38, 5))
    # 6. whole cell = profile band at rho and profile band is nested (monotone) in s
    wc = whole_cell(res)
    bands = [profile_band(res, s) for s in grid]
    checks["band_monotone_in_s"] = all(a[0] >= b[0] and a[1] <= b[1] for a, b in zip(bands, bands[1:]))
    checks["whole_cell_is_band_at_rho"] = wc == bands[-1]
    # 7. refusals (fail closed)
    ref = {}

    def refused(fn):
        try:
            fn()
        except TupleRefusal:
            return True
        return False
    bad = copy.deepcopy(meas)
    bad["norms"]["k"][1] = 0.5
    ref["float"] = refused(lambda: tuple_tct(bad, aux, S))
    bad = copy.deepcopy(meas)
    bad["norms"]["k"][2] = "-1/3"
    ref["negative_norm"] = refused(lambda: tuple_tct(bad, aux, S))
    bad = copy.deepcopy(meas)
    bad["r"]["3"]["H_at_a"] = ["1", "0"]
    ref["unordered_centre"] = refused(lambda: tuple_tct(bad, aux, S))
    bad = copy.deepcopy(meas)
    bad["r"]["1"]["delta_G"] = "0"
    ref["order3_field"] = refused(lambda: tuple_tct(bad, aux, S))
    bad = copy.deepcopy(meas)
    bad["order3_fields_present"] = True
    ref["order3_flag"] = refused(lambda: tuple_tct(bad, aux, S))
    bad = copy.deepcopy(meas)
    e0b = Fraction(2)  # inside the band: must be refused
    bad.update({"e0": str(e0b), "left": str(e0b - rho), "right": str(e0b + rho)})
    ref["band_geometry"] = refused(lambda: tuple_tct(bad, aux, S))
    bad = copy.deepcopy(meas)
    bad.update({"e0": str(-e0b), "left": str(-e0b - rho), "right": str(-e0b + rho)})
    ref["mirror_band_geometry"] = refused(lambda: tuple_tct(bad, aux, S))
    bad = copy.deepcopy(meas)
    bad["cell"] = min(_QUARANTINED_LABELS) + 3
    ref["quarantined_label"] = refused(lambda: tuple_tct(bad, aux, S))
    bad = copy.deepcopy(meas)
    del bad["W2"]["0:0"]
    ref["W_keys"] = refused(lambda: tuple_tct(bad, aux, S))
    bad = copy.deepcopy(meas)
    bad["left"] = str(q(bad["left"]) + Fraction(1, 10**9))
    ref["geometry_mismatch"] = refused(lambda: tuple_tct(bad, aux, S))
    bada = copy.deepcopy(aux)
    del bada["candidate_suprema"]["h:2:3"]
    ref["aux_missing"] = refused(lambda: tuple_tct(meas, bada, S))
    ref["s_outside"] = refused(lambda: profile_band(res, rho * 2))
    ref["accepts_clean"] = not refused(lambda: tuple_tct(meas, aux, S))
    checks["refusals"] = all(ref.values())
    checks["refusal_detail"] = ref
    checks["ALL"] = all(v for key, v in checks.items() if key != "refusal_detail")
    return checks


if __name__ == "__main__":
    import sys
    out = _selftest()
    print(json.dumps(out, indent=1, default=str))
    sys.exit(0 if out["ALL"] else 1)
