"""Signed certified order-3 ENGINE: whole-cell R''' enclosure from certified inputs, in Arb.

Detector-agnostic. It implements DESIGN.md section 3 of the frozen design namespace
(p5y_k5_cusum_order3_producer_design, commit 10911e51) plus the source chain one order further, over Arb balls:

    inputs (every scalar a certified UPPER bound, radius-zero Arb, unless stated)
      C >= sup_cell ||(I-K_e)^-1||,  k[i] >= sup_cell ||K_i||,  j[i] >= sup_cell ||J_i||,   i = 0..4
      rho = cell half width (a ball; its certified upper endpoint is used)
      mid[node]    midpoint error bounds    ||Xhat - X(e0)||       F:r D:r H:r, h:j:n S:r:n W:r:j:n (n <= 3),
                                                                    Sclosed:3
      cell[node]   whole-cell error bounds  sup_cell ||Xhat - X(e)||   h:j:n S:r:n W:r:j:n (n <= 2)
      refined[F:r|D:r|H:r]                  whole-cell error bounds of the resolvent objects, orders 0..2
      aux[name]    {delta_mid, delta_cell}  certified order-3 source-chain residuals  h_j:3 S_r:3 W_r_j:3
      g[r]         {delta_mid, delta_cell}  certified residual of the NEW rung  F_r:3  (candidate G_r)
      towers[(family, index, n)]           sup_cell ||X^(n)(e)|| of the TRUE objects, n <= 4 (h, S, W)
      sup_S0_4     sup_cell ||S_0^(4)||
      sup_hat[("F"|"D"|"H"|"G", r)]        certified sup of the candidate polynomial
      origin[("G", r)], origin[("W", (r, j))]   candidate value at the origin state x0 (Arb ball)

    rules (each term bounds a distinct piece of an exact identity; proofs in ../DESIGN_REAL.md section 4)
      source chain, n = 3, whole cell, min(cascade, Taylor):
        h_1:3     min(delta_cell, mid + rho T[h,1,4])
        h_j:3     cascade  delta_cell + sum_(i=0..3) C(3,i) k_i  cellx(h_(j-1), 3-i)
                  Taylor   mid + rho T[h,j,4]
        S_0:3     min(delta_cell, mid + rho sup_S0_4);   Sclosed:3  mid + rho sup_S0_4
        S_r:3     cascade  delta_cell + sum_(i=0..3) C(3,i) j_i  cellx(h_r, 3-i);   Taylor  mid + rho T[S,r,4]
        W_(r,j):3 cascade  delta_cell + sum_(i=0..3) C(3,i) k_i  cellx(W_(r,j-1), 3-i); Taylor mid + rho T[W,(r,j),4]
      new rung  F_r''' = (I-K)^-1 [K_3 F + 3 K_2 F' + 3 K_1 F'' + S_r''']
        midpoint  eps_mid  = C (g.delta_mid  + k_3 mid F + 3 k_2 mid D + 3 k_1 mid H + mid src)
        cascade   eps_casc = C (g.delta_cell + k_3 refF  + 3 k_2 refD  + 3 k_1 refH  + cellx src)
        Taylor    eps_tay  = eps_mid + rho TF_4
                  TF_n  = min( C (sum_(i=1..n) C(n,i) k_i TF_(n-i) + T[S,r,n]),  sup_hat_n + cellx_n ),  n = 0..3
                          cellx_0..3 = refF, refD, refH, eps_casc      (cascade only: no circularity)
                  TF_4  = C (sum_(i=1..4) C(4,i) k_i TF_(4-i) + T[S,r,4])
        cell      eps_x    = min(eps_casc, eps_tay)
      assembly  frozen c_(m,t) = 1/t - 1/m table, m in {1,2,3,5}
        centre = sum c * origin;  R3_mid = centre +/- sum |c| eps_mid;  R3_cell = centre +/- sum |c| eps_x
      export    L = lo(centre) - rad_cell,  U = hi(centre) + rad_cell   (exact dyadic rationals, no re-rounding)

Every stored bound goes through `_up` (finite, radius-zero upper endpoint); a non-finite input or intermediate is
a REFUSAL, never a number. There is no mutation hook, no sign threshold and no tuning parameter.
"""
from __future__ import annotations

import hashlib
import json
from contextlib import contextmanager
from fractions import Fraction as Fr
from math import comb

from flint import arb, ctx

ENGINE_SCHEMA = "rebaseguard.p5y.k5.order3-engine.v1"
EXPORT_SCHEMA = "rebaseguard.p5y.k5.order3-export.v2"
DERIVATIVE_ORDER = 3
M_VALUES = (1, 2, 3, 5)
W_INDICES = tuple((r, j) for r in range(4) for j in range(1, 4 - r))
ALLOWED_BITS = (128, 192, 256, 384, 512)
PRODUCTION_BITS = 256


class ProducerRefusal(RuntimeError):
    """Fail-closed refusal: the producer emits no enclosure."""


@contextmanager
def precision(bits: int):
    if bits not in ALLOWED_BITS:
        raise ProducerRefusal(f"precision {bits} bits is outside the frozen escalation set {ALLOWED_BITS}")
    with ctx.workprec(bits):
        yield


# ------------------------------------------------------------------ scalar discipline
def _finite(x: arb, what: str) -> arb:
    if not isinstance(x, arb):
        raise ProducerRefusal(f"{what}: not an Arb ball ({type(x).__name__})")
    if not x.is_finite():
        raise ProducerRefusal(f"{what}: non-finite enclosure")
    return x


def _up(x: arb, what: str) -> arb:
    """Radius-zero certified upper bound of |x|; refuses non-finite values."""
    return _finite(_finite(x, what).abs_upper(), what)


def _min(a: arb, b: arb) -> arb:
    return a if a.upper() <= b.upper() else b


def exact(q) -> arb:
    q = Fr(q)
    return arb(q.numerator) / arb(q.denominator)


def _dyadic(x: arb) -> Fr:
    q = x.fmpq()
    return Fr(int(q.p), int(q.q))


def ball_fractions(x: arb) -> tuple[Fr, Fr]:
    """Exact rational endpoints mid -/+ rad of an Arb ball.

    Independent of the ambient precision: `arb.upper()` / `lower()` round at the CURRENT context precision, so an
    export taken outside the certifying context would silently round outward at 53 bits. Midpoint and radius of an
    Arb ball are exact dyadics, so their difference and sum are the ball's exact endpoints.
    """
    _finite(x, "export")
    m, r = _dyadic(x.mid()), _dyadic(x.rad())
    return m - r, m + r


def fraction_of(x: arb) -> Fr:
    """x must be radius zero (an exact dyadic)."""
    if not x.rad() == 0:
        raise ProducerRefusal("export of a non-exact endpoint")
    return _dyadic(x.mid())


def lower_fraction(x: arb) -> Fr:
    return ball_fractions(x)[0]


def upper_fraction(x: arb) -> Fr:
    return ball_fractions(x)[1]


def coefficients(m: int) -> list[tuple[str, int, int, Fr]]:
    """Frozen ERROR_ALGEBRA section 4 table: F_r with 1/m (r < m); W_(r, t-r-1) with 1/t - 1/m."""
    if m not in M_VALUES:
        raise ProducerRefusal(f"m={m} outside the frozen scope {M_VALUES}")
    rows = [("F", r, 0, Fr(1, m)) for r in range(m)]
    rows += [("W", r, t - r - 1, Fr(1, t) - Fr(1, m)) for t in range(1, m) for r in range(t)]
    return rows


# ------------------------------------------------------------------ input validation
REQUIRED_SCALARS = ("C", "rho", "sup_S0_4")


def _validate(inp: dict) -> None:
    for key in REQUIRED_SCALARS + ("k", "j", "mid", "cell", "refined", "aux", "g", "towers", "sup_hat", "origin"):
        if key not in inp:
            raise ProducerRefusal(f"missing input {key}")
    for i in range(5):
        _up(inp["k"][i], f"k_{i}")
        _up(inp["j"][i], f"j_{i}")
    rho = _finite(inp["rho"], "rho")
    if not rho.lower() >= 0:
        raise ProducerRefusal("rho must be a nonnegative half width")
    if not _up(inp["C"], "C") > 0:
        raise ProducerRefusal("resolvent bound C must be positive")
    for name, v in inp["origin"].items():
        _finite(v, f"origin {name}")


# ------------------------------------------------------------------ the engine
def certify_order3(inp: dict, *, bits: int = PRODUCTION_BITS) -> dict:
    """All order-3 midpoint and whole-cell bounds, and the signed per-m export. Arb values."""
    with precision(bits):
        _validate(inp)
        C = _up(inp["C"], "C")
        rho = _up(inp["rho"], "rho")          # upper endpoint: every rule is monotone nondecreasing in rho
        k = {i: _up(inp["k"][i], f"k_{i}") for i in range(5)}
        jn = {i: _up(inp["j"][i], f"j_{i}") for i in range(5)}
        mid, cell, ref = inp["mid"], inp["cell"], inp["refined"]
        aux, g, T = inp["aux"], inp["g"], inp["towers"]

        def M(node):
            return _up(mid[node], f"mid {node}")

        comp: dict = {}

        def keep(node, cascade, taylor, eps_mid=None):
            cascade = _up(cascade, f"cascade {node}") if cascade is not None else None
            taylor = _up(taylor, f"taylor {node}")
            kept = taylor if cascade is None else _min(cascade, taylor)
            comp[node] = {"eps_mid": eps_mid, "cascade": cascade, "taylor": taylor, "kept": kept,
                          "bound": "taylor" if cascade is None or taylor.upper() < cascade.upper() else "cascade"}
            return kept

        # ---- source chain h_j^(3)
        hx: dict = {}

        def cellx_h(j, n):
            return hx[j] if n == 3 else _up(cell[f"h:{j}:{n}"], f"cell h:{j}:{n}")

        hx[1] = keep("h:1:3", aux["h_1:3"]["delta_cell"], M("h:1:3") + rho * T[("h", 1, 4)], M("h:1:3"))
        for j in range(2, 5):
            casc = _up(aux[f"h_{j}:3"]["delta_cell"], f"aux h_{j}:3")
            for i in range(4):
                casc = casc + arb(comb(3, i)) * k[i] * cellx_h(j - 1, 3 - i)
            hx[j] = keep(f"h:{j}:3", casc, M(f"h:{j}:3") + rho * _up(T[("h", j, 4)], "tower"), M(f"h:{j}:3"))

        # ---- source chain S_r^(3)
        s0_4 = _up(inp["sup_S0_4"], "sup_S0_4")
        sx: dict = {}
        sx[0] = keep("S:0:3", aux["S_0:3"]["delta_cell"], M("S:0:3") + rho * s0_4, M("S:0:3"))
        sclosed_x = keep("Sclosed:3", None, M("Sclosed:3") + rho * s0_4, M("Sclosed:3"))
        for r in range(1, 5):
            casc = _up(aux[f"S_{r}:3"]["delta_cell"], f"aux S_{r}:3")
            for i in range(4):
                casc = casc + arb(comb(3, i)) * jn[i] * cellx_h(r, 3 - i)
            sx[r] = keep(f"S:{r}:3", casc, M(f"S:{r}:3") + rho * _up(T[("S", r, 4)], "tower"), M(f"S:{r}:3"))

        # ---- finite kernel powers W_(r,j)^(3)
        wx = {(r, 0): sx[r] for r in range(4)}

        def cellx_w(r, j, n):
            return wx[(r, j)] if n == 3 else _up(cell[f"W:{r}:{j}:{n}"], f"cell W:{r}:{j}:{n}")

        for (r, j) in W_INDICES:
            casc = _up(aux[f"W_{r}_{j}:3"]["delta_cell"], f"aux W_{r}_{j}:3")
            for i in range(4):
                casc = casc + arb(comb(3, i)) * k[i] * cellx_w(r, j - 1, 3 - i)
            node = f"W:{r}:{j}:3"
            wx[(r, j)] = keep(node, casc, M(node) + rho * _up(T[("W", (r, j), 4)], "tower"), M(node))

        # ---- the new rung F_r^(3)
        gmid, gx, tf4 = {}, {}, {}
        for r in range(5):
            src_mid = M("Sclosed:3") if r == 0 else M(f"S:{r}:3")
            src_cell = sclosed_x if r == 0 else sx[r]
            gm = C * (_up(g[r]["delta_mid"], f"g_{r} delta_mid") + k[3] * M(f"F:{r}")
                      + arb(3) * k[2] * M(f"D:{r}") + arb(3) * k[1] * M(f"H:{r}") + src_mid)
            gm = _up(gm, f"F:{r}:3 mid")
            refF, refD, refH = (_up(ref[f"{x}:{r}"], f"refined {x}:{r}") for x in ("F", "D", "H"))
            casc = _up(C * (_up(g[r]["delta_cell"], f"g_{r} delta_cell") + k[3] * refF + arb(3) * k[2] * refD
                            + arb(3) * k[1] * refH + src_cell), f"F:{r}:3 cascade")
            sh = [_up(inp["sup_hat"][(x, r)], f"sup {x}_{r}") for x in ("F", "D", "H", "G")]
            ex = [refF, refD, refH, casc]
            TS = [_up(T[("S", r, n)], f"tower S:{r}:{n}") for n in range(5)]
            TF: list = []
            for n in range(4):
                acc = TS[n]
                for i in range(1, n + 1):
                    acc = acc + arb(comb(n, i)) * k[i] * TF[n - i]
                TF.append(_min(_up(C * acc, "tower F"), _up(sh[n] + ex[n], "sup F")))
            acc = TS[4]
            for i in range(1, 5):
                acc = acc + arb(comb(4, i)) * k[i] * TF[4 - i]
            tf4[r] = _up(C * acc, f"TF_4 r={r}")
            gmid[r] = gm
            gx[r] = keep(f"F:{r}:3", casc, gm + rho * tf4[r], gm)

        # ---- signed all-m assembly
        def obj(kind, r, j):
            if kind == "F":
                return _finite(inp["origin"][("G", r)], "origin G"), gmid[r], gx[r]
            return (_finite(inp["origin"][("W", (r, j))], "origin W"), M(f"W:{r}:{j}:3"), wx[(r, j)])

        per_m = {}
        for m in M_VALUES:
            centre, rad_mid, rad_cell = arb(0), arb(0), arb(0)
            for kind, r, j, c in coefficients(m):
                o, em, ec = obj(kind, r, j)
                centre = centre + o * exact(c)
                rad_mid = rad_mid + exact(abs(c)) * em
                rad_cell = rad_cell + exact(abs(c)) * ec
            rad_mid, rad_cell = _up(rad_mid, "radius"), _up(rad_cell, "radius")
            c_lo, c_hi = ball_fractions(_finite(centre, "centre"))
            r_mid = (c_lo - fraction_of(rad_mid), c_hi + fraction_of(rad_mid))
            r_cell = (c_lo - fraction_of(rad_cell), c_hi + fraction_of(rad_cell))
            per_m[m] = {"centre": centre, "R3_mid": r_mid, "R3_cell": r_cell, "L": r_cell[0], "U": r_cell[1]}
        return {"components": comp, "tf4": tf4, "m": per_m, "bits": bits}


# ------------------------------------------------------------------ deterministic scientific serialization
def _q(x: Fr) -> str:
    return f"{x.numerator}/{x.denominator}"


def sign_status(L: Fr, U: Fr) -> str:
    if L > 0:
        return "CERTIFIED_POSITIVE"
    if U < 0:
        return "CERTIFIED_NEGATIVE"
    return "SIGN_INDETERMINATE"


def scientific_payload(result: dict, binding: dict) -> dict:
    """The scientific content only: exact rationals, the binding, no runtime metadata."""
    per_m = {}
    for m, v in sorted(result["m"].items()):
        L, U = v["R3_cell"]
        lo_mid, hi_mid = v["R3_mid"]
        if not L <= U:
            raise ProducerRefusal("reversed whole-cell interval")
        per_m[str(m)] = {
            "R3_interval": {"lo": _q(L), "hi": _q(U), "width": _q(U - L)},
            "R3_signed_lower_bound_L": _q(L),
            "R3_signed_upper_bound_U": _q(U),
            "R3_mid_interval": {"lo": _q(lo_mid), "hi": _q(hi_mid)},
            "sign_status": sign_status(L, U),
            "semantics": "for every e in the closed cell: L <= R'''_(D,m)(e) <= U",
        }
    components = {
        node: {"eps_mid": None if c["eps_mid"] is None else _q(upper_fraction(c["eps_mid"])),
               "cascade": None if c["cascade"] is None else _q(upper_fraction(c["cascade"])),
               "taylor": _q(upper_fraction(c["taylor"])),
               "kept": _q(upper_fraction(c["kept"])), "bound": c["bound"]}
        for node, c in sorted(result["components"].items())}
    return {"schema": EXPORT_SCHEMA, "engine_schema": ENGINE_SCHEMA, "derivative_order": DERIVATIVE_ORDER,
            "precision_bits": result["bits"], "binding": binding, "m": per_m, "components": components,
            "towers_TF4": {str(r): _q(upper_fraction(v)) for r, v in sorted(result["tf4"].items())},
            "certification_status": "CERTIFIED_WHOLE_CELL_SIGNED_INTERVAL"}


def canonical(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()


def scientific_hash(payload: dict) -> str:
    return hashlib.sha256(canonical(payload)).hexdigest()
