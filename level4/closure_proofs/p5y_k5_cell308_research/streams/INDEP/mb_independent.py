"""mb_independent.py -- Stream F2: independent reconstruction of the composition layers of Theorem MB (r1).

Written from the THEOREM TEXT only (THEOREM_MB r1 in full; THEOREM_RLR307 section 1: declaration D14 and Lemma Lad;
THEOREM_AD section 4: Lemma Dv and Lemma Dv' r2; THEOREM_TPT sections 1, 2, 2b: Theorem TPT, Lemma TC-P, Theorem
TPT-B; THEOREM_TCT (P2'), (P3') and section 4 definitions of f_G, Env4 and the profile polynomials). No other
implementation of these layers was read before this module was written. It imports ONLY the Python standard library
(``fractions``, ``re``), and all exact layers use ``fractions.Fraction``; floats are refused everywhere.

Layers
------
L1  dv_prime(Abar, tau, C_T, D_lo, D1, D2, kappa1, kappa2) -> (A0, A1, A2)                 Lemma Dv' r2
L2  dv_prime_M(registry_inputs, Ubar, kappa1, kappa2, dlo_refresh=False) -> (A0, A1, A2)   Lemma Dv'-M (+ Lemma DM)
L3  d14_M(rlr_block, Ubar, kappa1, kappa2, dlo_refresh) -> (A0, A1, A2)                   D14 with Abar', C3 slot, DM
L4  lemma_g(C_R, kappa1, kappa2) -> (A0, A1, A2)                                          Lemma G
L5  envelope(U_list, drifts=None) -> [Ubar_0, ...]                                         Lemma M-U monotone envelope
L6  block_supply(members) -> {"A0","A1","A2","provenance"}                                 MB section 6
L7  ladder(rungs) -> composed record                                                        Lemma Lad
L8  tptb(profile, blocks) -> {"P_lo","P_hi",...}                                            Theorem TPT-B / MB section 7
L9  gamma_mb(g_hi, P_bracket) -> {"Gamma_lo","Gamma_hi","decision"}                         MB section 7 item 4
The ``*_detail`` variants return every intermediate as exact Fractions.

Exact scalar ("Q")
------------------
int, fractions.Fraction, or a string "p" / "p/q" (integers only). float, bool, Decimal and decimal strings are
refused (``Refusal``). "No bound" (+infinity) is ``None`` or the singleton ``INF`` where stated.

Input schema
------------
registry_inputs (L2)  {"A_bar": Q | None | INF, "tau": Q, "C_T": Q, "D_lo": Q, "D1": Q, "D2": Q,
                        optional "tau_a_lo": Q (required when dlo_refresh=True)}; all certified uniformly on the block.
rlr_block (L3)        {"A_bar": Q | None | INF, "tau", "C_T", "C_R", "tau_a_lo", "D_lo", "D1", "D2", "L1_up", "L2_up"}
                        (all Q, B-uniform certified; exact).
Ubar                  Q (certified U_Lambda >= Lambda(b) at the block drift b, via the envelope) or None / INF.
members (L6)          {name: (A0, A1, A2) | None}; "S_I1" is required and never None. Canonical provenance order:
                        S_I1, DvM, D14M, G, then any other names in sorted order.
rungs (L7)            list of {"status": "CERTIFIED" | other, optional metadata "degree"/"d"/"rung"/"name"/"id"/"note",
                        upper keys C_R, tau, C_T, A_bar, tau_a_up, S2hat_up, T_N_up, D1, D2, L1_up, L2_up,
                        lower keys tau_a_lo, D_lo, Lambda_lo}. Any other key is refused.
profile (L8)          {"e0": Q, "rho": Q, "x_lo": Q, "x_hi": Q, "m": int >= 1,
                        "sources": [m records {"f_F","f_D","f_H","f_G","Env4": Q >= 0,
                                               "Hhat": [lo, hi] or Q, "G_abs": Q >= 0 (default 0)}],
                        "W": [lo, hi]   or   "W_terms": [[c, lo, hi], ...] (interval sum of c*[lo, hi]),
                        "H_final": [lo, hi],
                        optional "M_consumed": Q (must equal mag(H_final) = max(|lo|, |hi|))}
                      Premises (refused otherwise): x_lo = e0 - rho and x_hi = e0 + rho EXACTLY, rho > 0, x_lo > 0,
                      ordered intervals, len(sources) == m, all profile coefficients >= 0.
blocks (L8)           list of {"lo": Q, "hi": Q, "A0": Q, "A1": Q, "A2": Q} (or (lo, hi, (A0, A1, A2))),
                      consecutive exact sub-intervals E_i tiling [x_lo, x_hi] (E_0.lo = x_lo, E_i.hi = E_{i+1}.lo,
                      E_last.hi = x_hi, lo < hi), each triple >= 0 and admissible on E cap B_i (caller's premise).

Mathematics of L8 (THEOREM_TPT Lemma TC-P, section 2 profile enclosure; THEOREM_MB section 7)
-------------------------------------------------------------------------------------------
For a source r and a triple (A0, A1, A2), with s = |t - e0|:
    p0(s) = f_F + s f_D + s^2 f_H/2 + s^3 f_G/6 + s^4 Env4/24
    p1(s) = f_D + s f_H + s^2 f_G/2 + s^3 Env4/6
    p2(s) = f_H + s f_G + s^2 Env4/2
    rad_r(s) = A0 p2(s) + 2 A1 p1(s) + A2 p0(s),   half_r(s) = rad_r(s) + s |Ghat_r(a)|
    lo_i(s) = W.lo + (1/m) sum_r (Hhat_r.lo - half_r(s)),   hi_i(s) = W.hi + (1/m) sum_r (Hhat_r.hi + half_r(s))
    L(t) = max(H_final.lo, lo_i(s)),   U(t) = min(H_final.hi, hi_i(s))
Pieces: [x_lo, e0] and [e0, x_hi] cut at every end of every E_i. Right side (t = e0 + s): running integral of
(e0 + s) * min(-H_final.lo, -lo_i(s)); left side (t = e0 - s): running integral of (e0 - s) * min(H_final.hi, hi_i(s)).
P*_B = max(0, running integrals at all piece ends). On each piece g = -lo_i (right) or hi_i (left) is a polynomial
with nonnegative coefficients of s^1..s^4, hence nondecreasing for s >= 0; the cap crossing g(s*) = c is unique and is
isolated by exact bisection (width <= 2^-K, K >= 200); on the isolating interval [alpha, beta] the integrand is
bracketed by w * g(alpha) <= w * min(g, c) <= w * c (w > 0 because t >= x_lo > 0). The result is an exact rational
bracket P_lo <= P*_B <= P_hi with P_hi - P_lo < 2^-150 (refined further if needed).
C6: refuse when max(H_final.lo, lo_i(s_a)) > min(H_final.hi, hi_i(s_a)) at the inner end s_a of any piece.

Research-namespace band guard
-----------------------------
``tptb`` and ``envelope`` refuse any drift point or block meeting [6/5, 13/5] or its mirror unless the caller passes
``research_band_guard=False`` explicitly (reserved for a separately granted formal namespace; never used here).
"""
from __future__ import annotations

import re
from fractions import Fraction

__all__ = [
    "Refusal", "INF", "dv_prime", "dv_prime_detail", "dv_prime_M", "dv_prime_M_detail", "d14_M", "d14_M_detail",
    "lemma_g", "envelope", "block_supply", "ladder", "tptb", "gamma_mb", "dyadic_hull", "check_kappas",
    "p5_c5t_closed_form", "tpt_endpoint_only",
]

MODULE_REVISION = "F2-r1"


class Refusal(ValueError):
    """A premise of the theorem is violated or an input is not exact: no value is produced (fail closed)."""


class _Inf:
    """+infinity for 'no certified bound' (Abar absent, U_Lambda absent)."""
    _inst = None

    def __new__(cls):
        if cls._inst is None:
            cls._inst = super().__new__(cls)
        return cls._inst

    def __repr__(self):
        return "INF"


INF = _Inf()

_RAT_STR = re.compile(r"^\s*[+-]?\d+\s*(/\s*\d+\s*)?$")

# Research-namespace quarantine band (config/TARGET_QUARANTINE_308.json drift_band); guard only, never evaluated.
_BAND = (Fraction(6, 5), Fraction(13, 5))  # c308-quarantine: literal-ok


# ------------------------------------------------------------------ exact scalars

def _q(x, name="value", *, allow_inf=False):
    """Convert an exact scalar to Fraction; refuse floats, bools, decimals and anything inexact."""
    if x is None or x is INF:
        if allow_inf:
            return INF
        raise Refusal(f"{name}: +inf / None not allowed here")
    if isinstance(x, bool):
        raise Refusal(f"{name}: bool is not an exact rational")
    if isinstance(x, Fraction):
        return x
    if isinstance(x, int):
        return Fraction(x)
    if isinstance(x, str):
        if not _RAT_STR.match(x):
            raise Refusal(f"{name}: string {x!r} is not an integer ratio 'p/q'")
        return Fraction(x.replace(" ", ""))
    raise Refusal(f"{name}: type {type(x).__name__} refused (exact int / Fraction / 'p/q' only)")


def _qpos(x, name, *, strict=True, allow_inf=False):
    v = _q(x, name, allow_inf=allow_inf)
    if v is INF:
        return v
    if strict and not v > 0:
        raise Refusal(f"{name} must be > 0 (got {v})")
    if not strict and v < 0:
        raise Refusal(f"{name} must be >= 0 (got {v})")
    return v


def _min_inf(a, b):
    if a is INF:
        return b
    if b is INF:
        return a
    return a if a <= b else b


def _interval(x, name):
    if isinstance(x, (list, tuple)):
        if len(x) != 2:
            raise Refusal(f"{name}: interval must have 2 endpoints")
        lo, hi = _q(x[0], name + ".lo"), _q(x[1], name + ".hi")
    elif isinstance(x, dict):
        lo, hi = _q(x["lo"], name + ".lo"), _q(x["hi"], name + ".hi")
    else:
        lo = hi = _q(x, name)
    if lo > hi:
        raise Refusal(f"{name}: unordered interval [{lo}, {hi}]")
    return lo, hi


def _band_guard(lo, hi, enabled):
    if not enabled:
        return
    lo, hi = (lo, hi) if lo <= hi else (hi, lo)
    for a, b in (_BAND, (-_BAND[1], -_BAND[0])):
        if not (hi < a or lo > b):
            raise Refusal("RESEARCH_BAND_GUARD: drift set meets the quarantine band or its mirror")


# ------------------------------------------------------------------ kappa premise check (optional)

# Rational LOWER bounds used only to CHECK caller-supplied kappas (20 decimals, truncated):
# pi = 3.14159265358979323846264..., e = 2.71828182845904523536028...
_PI_LO = Fraction(314159265358979323846, 10 ** 20)
_E_LO = Fraction(271828182845904523536, 10 ** 20)


def check_kappas(kappa1, kappa2):
    """Exact check kappa1 >= sqrt(2/pi) and kappa2 >= 4 phi(1) = 4 exp(-1/2)/sqrt(2 pi) (sufficient conditions)."""
    k1, k2 = _qpos(kappa1, "kappa1"), _qpos(kappa2, "kappa2")
    ok1 = k1 * k1 * _PI_LO >= 2                  # k1^2 >= 2/pi_lo >= 2/pi
    ok2 = k2 * k2 * _PI_LO * _E_LO >= 8          # k2^2 >= 16/(2 pi e) = 8/(pi e)
    return {"kappa1_ge_sqrt_2_over_pi": ok1, "kappa2_ge_4_phi_1": ok2}


# ------------------------------------------------------------------ L1 Lemma Dv' r2

def dv_prime_detail(Abar, tau, C_T, D_lo, D1, D2, kappa1, kappa2):
    """Lemma Dv' r2 (THEOREM_AD section 4) with Abar_eff = min(Abar, tau/D_lo); Abar may be None/INF (no bound)."""
    Ab = _qpos(Abar, "Abar", allow_inf=True)
    tau = _qpos(tau, "tau")
    C = _qpos(C_T, "C_T", strict=False)
    Dlo = _qpos(D_lo, "D_lo")
    d1, d2 = _qpos(D1, "D1", strict=False), _qpos(D2, "D2", strict=False)
    k1, k2 = _qpos(kappa1, "kappa1", strict=False), _qpos(kappa2, "kappa2", strict=False)
    A_eff = _min_inf(Ab, tau / Dlo)
    dl1, dl2 = d1 / Dlo, d2 / Dlo
    A0 = A_eff
    A1 = A_eff * (k1 * C + dl1)
    A2 = A_eff * (2 * k1 * k1 * C * C + k2 * C + 2 * k1 * C * dl1 + 2 * dl1 * dl1 + dl2)
    return {"A0": A0, "A1": A1, "A2": A2, "A_eff": A_eff, "delta1": dl1, "delta2": dl2, "D_lo_used": Dlo,
            "Abar_used": Ab}


def dv_prime(Abar, tau, C_T, D_lo, D1, D2, kappa1, kappa2):
    d = dv_prime_detail(Abar, tau, C_T, D_lo, D1, D2, kappa1, kappa2)
    return d["A0"], d["A1"], d["A2"]


# ------------------------------------------------------------------ Lemma DM (declared D_lo refresh)

def dlo_refresh_value(D_lo, tau_a_lo, Abar_prime):
    """Lemma DM: D_lo' = max(D_lo, tau_a_lo / Abar'); Abar' = INF gives D_lo' = D_lo. D_lo' >= D_lo always."""
    Dlo = _qpos(D_lo, "D_lo")
    tal = _qpos(tau_a_lo, "tau_a_lo")
    Ap = _qpos(Abar_prime, "Abar_prime", allow_inf=True)
    if Ap is INF:
        return Dlo
    cand = tal / Ap
    return cand if cand > Dlo else Dlo


# ------------------------------------------------------------------ L2 Lemma Dv'-M

_REG_KEYS = {"A_bar", "tau", "C_T", "D_lo", "D1", "D2", "tau_a_lo"}


def dv_prime_M_detail(registry_inputs, Ubar, kappa1, kappa2, dlo_refresh=False):
    extra = set(registry_inputs) - _REG_KEYS
    if extra:
        raise Refusal(f"dv_prime_M: unknown keys {sorted(extra)}")
    Ab = _qpos(registry_inputs.get("A_bar"), "A_bar", allow_inf=True)
    U = _qpos(Ubar, "Ubar", allow_inf=True)
    Ap = _min_inf(Ab, U)
    Dlo = _qpos(registry_inputs["D_lo"], "D_lo")
    if dlo_refresh:
        if "tau_a_lo" not in registry_inputs:
            raise Refusal("dv_prime_M: dlo_refresh requires tau_a_lo")
        Dlo = dlo_refresh_value(Dlo, registry_inputs["tau_a_lo"], Ap)
    d = dv_prime_detail(Ap, registry_inputs["tau"], registry_inputs["C_T"], Dlo, registry_inputs["D1"],
                        registry_inputs["D2"], kappa1, kappa2)
    d["Abar_prime"] = Ap
    return d


def dv_prime_M(registry_inputs, Ubar, kappa1, kappa2, dlo_refresh=False):
    d = dv_prime_M_detail(registry_inputs, Ubar, kappa1, kappa2, dlo_refresh)
    return d["A0"], d["A1"], d["A2"]


# ------------------------------------------------------------------ L3 declaration D14 with Abar' (D14-M)

_RLR_KEYS = ("A_bar", "tau", "C_T", "C_R", "tau_a_lo", "D_lo", "D1", "D2", "L1_up", "L2_up")


def d14_M_detail(rlr_block, Ubar, kappa1, kappa2, dlo_refresh):
    extra = set(rlr_block) - set(_RLR_KEYS)
    if extra:
        raise Refusal(f"d14_M: unknown keys {sorted(extra)}")
    missing = [k for k in _RLR_KEYS if k not in rlr_block and k != "A_bar"]
    if missing:
        raise Refusal(f"d14_M: missing B-uniform inputs {missing}")
    if not isinstance(dlo_refresh, bool):
        raise Refusal("d14_M: dlo_refresh must be a bool")
    Ab = _qpos(rlr_block.get("A_bar"), "A_bar", allow_inf=True)
    tau = _qpos(rlr_block["tau"], "tau")
    C_T = _qpos(rlr_block["C_T"], "C_T", strict=False)
    C_R = _qpos(rlr_block["C_R"], "C_R")
    tal = _qpos(rlr_block["tau_a_lo"], "tau_a_lo")
    Dlo0 = _qpos(rlr_block["D_lo"], "D_lo")
    D1 = _qpos(rlr_block["D1"], "D1", strict=False)
    D2 = _qpos(rlr_block["D2"], "D2", strict=False)
    L1 = _qpos(rlr_block["L1_up"], "L1_up", strict=False)
    L2 = _qpos(rlr_block["L2_up"], "L2_up", strict=False)
    k1 = _qpos(kappa1, "kappa1", strict=False)
    k2 = _qpos(kappa2, "kappa2", strict=False)
    U = _qpos(Ubar, "Ubar", allow_inf=True)

    Ap = _min_inf(Ab, U)                                   # Abar' = min(A_bar, Ubar)
    Dlo = dlo_refresh_value(Dlo0, tal, Ap) if dlo_refresh else Dlo0   # Lemma DM
    A_eff = _min_inf(Ap, tau / Dlo)                        # Abar'_eff
    dl1, dl2 = D1 / Dlo, D2 / Dlo
    r1, r2 = L1 / tal, L2 / tal
    r1dv = k1 * C_T
    r2dv = 2 * k1 * k1 * C_T * C_T + k2 * C_T
    c1 = min(A_eff * r1, L1 / Dlo, A_eff * r1dv)
    c2 = min(A_eff * r2, L2 / Dlo, A_eff * r2dv)
    g1 = k1 * C_R * C_R
    g2 = k2 * C_R * C_R + 2 * k1 * k1 * C_R ** 3
    A1 = min(c1 + A_eff * dl1, g1)
    A2 = min(c2 + 2 * c1 * dl1 + A_eff * (2 * dl1 * dl1 + dl2), g2)
    A0 = min(A_eff, C_R)                                   # C3 A0 slot
    return {"A0": A0, "A1": A1, "A2": A2, "Abar_prime": Ap, "A_eff": A_eff, "D_lo_used": Dlo, "D_lo_cert": Dlo0,
            "delta1": dl1, "delta2": dl2, "rho1": r1, "rho2": r2, "rho1_Dv": r1dv, "rho2_Dv": r2dv,
            "c1": c1, "c2": c2, "G1": g1, "G2": g2}


def d14_M(rlr_block, Ubar, kappa1, kappa2, dlo_refresh):
    d = d14_M_detail(rlr_block, Ubar, kappa1, kappa2, dlo_refresh)
    return d["A0"], d["A1"], d["A2"]


# ------------------------------------------------------------------ L4 Lemma G

def lemma_g(C_R, kappa1, kappa2):
    c = _qpos(C_R, "C_R")
    k1 = _qpos(kappa1, "kappa1", strict=False)
    k2 = _qpos(kappa2, "kappa2", strict=False)
    return c, k1 * c * c, k2 * c * c + 2 * k1 * k1 * c ** 3


# ------------------------------------------------------------------ L5 Lemma M-U envelope and hulls

def dyadic_hull(lo, hi, bits=20):
    """Outward 2^-bits dyadic hull of [lo, hi] (THEOREM_RLR307 Lemma H / MB section 6); exact floor/ceil."""
    lo, hi = _q(lo, "lo"), _q(hi, "hi")
    if lo > hi:
        raise Refusal("dyadic_hull: unordered")
    d = 2 ** bits
    return Fraction((lo * d).__floor__(), d), Fraction((hi * d).__ceil__(), d)


def envelope(U_list, drifts=None, *, research_band_guard=True):
    """Running minimum Ubar_j = min_{i <= j} U_i over pre-declared block drifts b_0 < b_1 < ... (all >= 0).

    Entries may be None (no certificate at that drift); the envelope is None (= +inf) until the first certificate.
    """
    Us = [None if u is None else _qpos(u, f"U[{i}]") for i, u in enumerate(U_list)]
    if drifts is not None:
        bs = [_q(b, f"b[{i}]") for i, b in enumerate(drifts)]
        if len(bs) != len(Us):
            raise Refusal("envelope: drifts and U_list lengths differ")
        for i, b in enumerate(bs):
            if b < 0:
                raise Refusal("envelope: block drifts must be >= 0 (read in |e|)")
            if i and not bs[i - 1] < b:
                raise Refusal("envelope: block drifts must be strictly increasing")
            _band_guard(b, b, research_band_guard)
    out, cur = [], None
    for u in Us:
        if u is not None and (cur is None or u < cur):
            cur = u
        out.append(cur)
    return out


# ------------------------------------------------------------------ L6 block supply

_ORDER = ("S_I1", "DvM", "D14M", "G")


def block_supply(members):
    if "S_I1" not in members or members["S_I1"] is None:
        raise Refusal("block_supply: the committed cell-level supply S_I1 must be present")
    names = [n for n in _ORDER if n in members] + sorted(n for n in members if n not in _ORDER)
    trip = {}
    for n in names:
        t = members[n]
        if t is None:
            continue
        if len(t) != 3:
            raise Refusal(f"block_supply: member {n} is not a triple")
        trip[n] = tuple(_qpos(v, f"{n}.A{j}", strict=False) for j, v in enumerate(t))
    out = {"provenance": {}, "attaining": {}}
    for j, key in enumerate(("A0", "A1", "A2")):
        best = min(trip[n][j] for n in trip)
        att = [n for n in names if n in trip and trip[n][j] == best]
        out[key] = best
        out["provenance"][key] = att[0]
        out["attaining"][key] = att
    return out


# ------------------------------------------------------------------ L7 Lemma Lad

_UPPER = ("C_R", "tau", "C_T", "A_bar", "tau_a_up", "S2hat_up", "T_N_up", "D1", "D2", "L1_up", "L2_up")
_LOWER = ("tau_a_lo", "D_lo", "Lambda_lo")
_META = {"status", "degree", "d", "rung", "name", "id", "note"}


def ladder(rungs):
    """Compose certified rungs: upper keys by min, lower keys by max, each over the CERTIFIED rungs that carry it.

    Returns None when no rung is CERTIFIED (the theorem then asserts nothing for the block).
    """
    cert = []
    for i, r in enumerate(rungs):
        extra = set(r) - set(_UPPER) - set(_LOWER) - _META
        if extra:
            raise Refusal(f"ladder: rung {i} has unknown keys {sorted(extra)}")
        if r.get("status") == "CERTIFIED":
            cert.append(r)
    if not cert:
        return None
    out = {"n_certified": len(cert), "from": {}}
    for k in _UPPER + _LOWER:
        vals = [(_q(r[k], f"rung.{k}"), idx) for idx, r in enumerate(cert) if k in r and r[k] is not None]
        if not vals:
            continue
        v, idx = (min if k in _UPPER else max)(vals, key=lambda p: p[0])
        out[k] = v
        out["from"][k] = cert[idx].get("degree", cert[idx].get("d", cert[idx].get("rung", idx)))
    return out


# ------------------------------------------------------------------ polynomial helpers (exact)

def _padd(a, b):
    n = max(len(a), len(b))
    return [(a[i] if i < len(a) else 0) + (b[i] if i < len(b) else 0) for i in range(n)]


def _pscale(a, c):
    return [c * x for x in a]


def _pmul(a, b):
    out = [Fraction(0)] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        if x:
            for j, y in enumerate(b):
                out[i + j] += x * y
    return out


def _peval(a, s):
    v = Fraction(0)
    for c in reversed(a):
        v = v * s + c
    return v


def _pint(a, s0, s1):
    """Exact integral of polynomial a over [s0, s1]."""
    anti = [Fraction(0)] + [c / (i + 1) for i, c in enumerate(a)]
    return _peval(anti, s1) - _peval(anti, s0)


# ------------------------------------------------------------------ L8 Theorem TPT-B

def _parse_profile(profile, research_band_guard):
    e0 = _q(profile["e0"], "e0")
    rho = _q(profile["rho"], "rho")
    x_lo = _q(profile["x_lo"], "x_lo")
    x_hi = _q(profile["x_hi"], "x_hi")
    if not rho > 0:
        raise Refusal("rho must be > 0")
    if x_lo != e0 - rho or x_hi != e0 + rho:
        raise Refusal("CELL_IDENTITY: E = [e0 - rho, e0 + rho] does not hold as an exact rational identity (C5)")
    if not x_lo > 0:
        raise Refusal("x_lo must be > 0")
    _band_guard(x_lo, x_hi, research_band_guard)
    m = profile["m"]
    if isinstance(m, bool) or not isinstance(m, int) or m < 1:
        raise Refusal("m must be an int >= 1")
    srcs = profile["sources"]
    if len(srcs) != m:
        raise Refusal(f"m = {m} does not match the number of source terms ({len(srcs)})")
    sources = []
    for r, sr in enumerate(srcs):
        rec = {k: _qpos(sr[k], f"src[{r}].{k}", strict=False) for k in ("f_F", "f_D", "f_H", "f_G", "Env4")}
        rec["Hhat"] = _interval(sr["Hhat"], f"src[{r}].Hhat")
        rec["G_abs"] = _qpos(sr.get("G_abs", 0), f"src[{r}].G_abs", strict=False)
        extra = set(sr) - {"f_F", "f_D", "f_H", "f_G", "Env4", "Hhat", "G_abs", "r"}
        if extra:
            raise Refusal(f"src[{r}] unknown keys {sorted(extra)}")
        sources.append(rec)
    if ("W" in profile) == ("W_terms" in profile):
        raise Refusal("give exactly one of W / W_terms")
    if "W" in profile:
        W = _interval(profile["W"], "W")
    else:
        wl = wh = Fraction(0)
        for k, term in enumerate(profile["W_terms"]):
            c = _q(term[0], f"W_terms[{k}].c")
            lo, hi = _interval(term[1:3], f"W_terms[{k}]")
            if c >= 0:
                wl, wh = wl + c * lo, wh + c * hi
            else:
                wl, wh = wl + c * hi, wh + c * lo
        W = (wl, wh)
    H = _interval(profile["H_final"], "H_final")
    if "M_consumed" in profile and profile["M_consumed"] is not None:
        M = _q(profile["M_consumed"], "M_consumed")
        if M != max(abs(H[0]), abs(H[1])):
            raise Refusal("M_consumed != mag(H_final) (N7 / C2 dominance premise)")
    known = {"e0", "rho", "x_lo", "x_hi", "m", "sources", "W", "W_terms", "H_final", "M_consumed", "label"}
    extra = set(profile) - known
    if extra:
        raise Refusal(f"profile unknown keys {sorted(extra)}")
    return {"e0": e0, "rho": rho, "x_lo": x_lo, "x_hi": x_hi, "m": m, "sources": sources, "W": W, "H": H}


def _parse_blocks(blocks, x_lo, x_hi):
    out = []
    for i, b in enumerate(blocks):
        if isinstance(b, dict):
            extra = set(b) - {"lo", "hi", "A0", "A1", "A2", "label"}
            if extra:
                raise Refusal(f"block {i} unknown keys {sorted(extra)}")
            lo, hi, t = b["lo"], b["hi"], (b["A0"], b["A1"], b["A2"])
        else:
            lo, hi, t = b
        lo, hi = _q(lo, f"block[{i}].lo"), _q(hi, f"block[{i}].hi")
        if not lo < hi:
            raise Refusal(f"block {i}: empty or unordered sub-interval")
        A = tuple(_qpos(v, f"block[{i}].A{j}", strict=False) for j, v in enumerate(t))
        out.append((lo, hi, A))
    if not out:
        raise Refusal("no blocks")
    if out[0][0] != x_lo or out[-1][1] != x_hi:
        raise Refusal("blocks do not tile [x_lo, x_hi] (ends)")
    for i in range(len(out) - 1):
        if out[i][1] != out[i + 1][0]:
            raise Refusal(f"blocks do not tile [x_lo, x_hi] (gap/overlap between {i} and {i + 1})")
    return out


def _half_poly(src, A):
    """half_r(s) = rad_r(s) + s |Ghat_r(a)| as an exact polynomial in s (coefficients index = power)."""
    A0, A1, A2 = A
    fF, fD, fH, fG, E4 = src["f_F"], src["f_D"], src["f_H"], src["f_G"], src["Env4"]
    p0 = [fF, fD, fH / 2, fG / 6, E4 / 24]
    p1 = [fD, fH, fG / 2, E4 / 6]
    p2 = [fH, fG, E4 / 2]
    rad = _padd(_padd(_pscale(p2, A0), _pscale(p1, 2 * A1)), _pscale(p0, A2))
    return _padd(rad, [Fraction(0), src["G_abs"]])


def profile_polys(P, A):
    """(lo_poly, hi_poly) in s for one triple A."""
    m = P["m"]
    lo = [P["W"][0]]
    hi = [P["W"][1]]
    for src in P["sources"]:
        h = _half_poly(src, A)
        lo = _padd(lo, _pscale(_padd([src["Hhat"][0]], _pscale(h, -1)), Fraction(1, m)))
        hi = _padd(hi, _pscale(_padd([src["Hhat"][1]], h), Fraction(1, m)))
    return lo, hi


def _check_nondecreasing(g, what):
    # g(s) = g0 + g1 s + ... with g_j >= 0 for j >= 1 is nondecreasing on s >= 0.
    for j, c in enumerate(g[1:], 1):
        if c < 0:
            raise Refusal(f"internal: {what} has a negative s^{j} coefficient (profile not monotone)")


def _piece_bracket(w, g, c, sa, sb, K):
    """Bracket of the exact integral over [sa, sb] of w(s) * min(g(s), c); w > 0 linear, g nondecreasing poly."""
    wg = _pmul(w, g)
    qa = _peval(g, sa) - c
    qb = _peval(g, sb) - c
    if qa >= 0:          # g >= c on the whole piece: the cap binds everywhere
        v = c * _pint(w, sa, sb)
        return v, v, {"regime": "cap", "root": None}
    if qb <= 0:          # g <= c on the whole piece: the profile binds everywhere
        v = _pint(wg, sa, sb)
        return v, v, {"regime": "profile", "root": None}
    a, b = sa, sb        # unique root of g - c in (sa, sb): q(a) < 0 < q(b)
    tol = Fraction(1, 2 ** K)
    exact = None
    while b - a > tol:
        mid = (a + b) / 2
        qm = _peval(g, mid) - c
        if qm == 0:
            exact = mid
            break
        if qm < 0:
            a = mid
        else:
            b = mid
    if exact is not None:
        v = _pint(wg, sa, exact) + c * _pint(w, exact, sb)
        return v, v, {"regime": "split_exact", "root": (exact, exact)}
    base = _pint(wg, sa, a) + c * _pint(w, b, sb)
    mid_w = _pint(w, a, b)
    ga = _peval(g, a)
    lo = base + ga * mid_w
    hi = base + c * mid_w
    return lo, hi, {"regime": "split", "root": (a, b)}


def _side_pieces(P, blk, side):
    """Pieces on one side as (s_a, s_b, block_index), ordered by s from 0 to rho."""
    e0, rho = P["e0"], P["rho"]
    cuts = set()
    for lo, hi, _ in blk:
        for t in (lo, hi):
            s = (t - e0) if side == "R" else (e0 - t)
            if 0 < s < rho:
                cuts.add(s)
    pts = [Fraction(0)] + sorted(cuts) + [rho]
    out = []
    for sa, sb in zip(pts, pts[1:]):
        ta, tb = (e0 + sa, e0 + sb) if side == "R" else (e0 - sb, e0 - sa)
        idx = [i for i, (lo, hi, _) in enumerate(blk) if lo <= ta and tb <= hi]
        if len(idx) != 1:
            raise Refusal(f"internal: piece [{ta}, {tb}] not inside exactly one block ({idx})")
        out.append((sa, sb, idx[0]))
    return out


def tptb(profile, blocks, *, K=200, target_width_bits=150, research_band_guard=True, _mutant=None):
    """Theorem TPT-B / MB section 7 item 3: exact certified bracket [P_lo, P_hi] of P*_B (piece-end rule)."""
    P = _parse_profile(profile, research_band_guard)
    blk = _parse_blocks(blocks, P["x_lo"], P["x_hi"])
    Hlo, Hhi = P["H"]
    e0 = P["e0"]
    polys = [profile_polys(P, A) for _, _, A in blk]
    target = Fraction(1, 2 ** target_width_bits)
    while True:
        sides = {}
        for side in ("R", "L"):
            pieces = _side_pieces(P, blk, side)
            if _mutant == "drop_piece_end" and len(pieces) > 1:
                # mutant: merge the first two pieces, keeping the inner piece's triple (a missing piece end)
                pieces = [(pieces[0][0], pieces[1][1], pieces[0][2])] + pieces[2:]
            run_lo = run_hi = Fraction(0)
            recs = []
            for sa, sb, i in pieces:
                lo_p, hi_p = polys[i]
                # C6: the capped band must be non-empty at the piece's inner end s_a
                if max(Hlo, _peval(lo_p, sa)) > min(Hhi, _peval(hi_p, sa)):
                    raise Refusal(f"C6_EMPTY_BAND: side {side} piece s in [{sa}, {sb}] (block {i}) at inner end")
                if side == "R":
                    w = [e0, Fraction(1)]            # t = e0 + s
                    g = _pscale(lo_p, -1)            # -lo_i(s)
                    c = -Hlo
                else:
                    w = [e0, Fraction(-1)]           # t = e0 - s
                    g = list(hi_p)                   # hi_i(s)
                    c = Hhi
                if _mutant == "flip_t":
                    w = _pscale(w, -1)
                _check_nondecreasing(g, f"side {side} block {i}")
                if not (_peval(w, sa) > 0 and _peval(w, sb) > 0) and _mutant != "flip_t":
                    raise Refusal("internal: weight t must be > 0 on the piece")
                plo, phi, info = _piece_bracket(w, g, c, sa, sb, K)
                run_lo += plo
                run_hi += phi
                recs.append({"s_a": sa, "s_b": sb, "block": i, "piece_lo": plo, "piece_hi": phi,
                             "run_lo": run_lo, "run_hi": run_hi, "regime": info["regime"], "root": info["root"]})
            sides[side] = recs
        ends = [(r["run_lo"], r["run_hi"], side, k) for side in ("R", "L") for k, r in enumerate(sides[side])]
        if _mutant == "endpoint_only":
            ends = [(sides[s][-1]["run_lo"], sides[s][-1]["run_hi"], s, len(sides[s]) - 1) for s in ("R", "L")]
        P_lo = max([Fraction(0)] + [e[0] for e in ends])
        P_hi = max([Fraction(0)] + [e[1] for e in ends])
        if P_hi - P_lo < target:
            break
        K += 64
        if K > 2000:
            raise Refusal("could not reach the target bracket width")
    arg = max(ends, key=lambda e: e[1]) if P_hi > 0 else None
    return {"P_lo": P_lo, "P_hi": P_hi, "width": P_hi - P_lo, "K_bits": K, "pieces": sides,
            "argmax": None if arg is None else {"side": arg[2], "piece": arg[3],
                                                "s_end": sides[arg[2]][arg[3]]["s_b"]},
            "n_pieces": {s: len(sides[s]) for s in sides}, "revision": MODULE_REVISION}


def tpt_endpoint_only(profile, blocks, **kw):
    """The INVALID endpoint-only rule max(0, I(rho)) of Corollary TPT-M applied to block constants (C4); for controls."""
    return tptb(profile, blocks, _mutant="endpoint_only", **kw)


def p5_c5t_closed_form(profile, *, research_band_guard=True):
    """C5-T value (TPT with the constant profile H_final): max(0, -H.lo (x_hi^2 - e0^2)/2, H.hi (e0^2 - x_lo^2)/2)."""
    P = _parse_profile(profile, research_band_guard)
    e0, xl, xh = P["e0"], P["x_lo"], P["x_hi"]
    Hlo, Hhi = P["H"]
    return max(Fraction(0), -Hlo * (xh * xh - e0 * e0) / 2, Hhi * (e0 * e0 - xl * xl) / 2)


# ------------------------------------------------------------------ L9 Gamma_MB

def gamma_mb(g_hi, P_bracket):
    g = _q(g_hi, "g_hi")
    if isinstance(P_bracket, dict):
        plo, phi = P_bracket["P_lo"], P_bracket["P_hi"]
    else:
        plo, phi = P_bracket
    plo, phi = _q(plo, "P_lo"), _q(phi, "P_hi")
    if plo > phi or plo < 0:
        raise Refusal("P bracket must satisfy 0 <= P_lo <= P_hi")
    G_lo, G_hi = g + plo, g + phi
    if G_hi < 0:
        dec = "CLOSED"
    elif G_lo >= 0:
        dec = "NOT_CLOSED"
    else:
        dec = "UNDECIDED"
    return {"Gamma_lo": G_lo, "Gamma_hi": G_hi, "decision": dec}
