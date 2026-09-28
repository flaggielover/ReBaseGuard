"""Stream E (ASSEMBLY): block-resolved Taylor-profile transport (TPT-B) on the FROZEN TC-T consumer path.

Research code of the cell-308 research namespace. It is exercised ONLY on manufactured TC-T-shaped decoys and on real
non-tail inputs. Every entry point refuses the quarantined labels (CUSUM m=5 cells 305-309) and any geometry or block
meeting the drift band [6/5, 13/5] or its mirror, BEFORE anything is loaded or evaluated (c308_quarantine.guard_*).
These guards are defence in depth only (the enclosure does not depend on e0 and the penalty is affine in e0); the
effective barrier is that this code reads no input file at all: the caller hands it an in-memory input object.

Given one TC-T-shaped input object ("bundle", schema below), the cell-level supply S = (A0, A1, A2) and an optional
list of blocks with per-block triples, ``evaluate_bundle`` computes in exact rationals:

 (a) REPRODUCTION MODE: the frozen direct clause, by calling the frozen ``c2_d5_forecast.direct`` (blob 18403dbe) with
     the frozen ``tct_rule`` (98f6eee4) and the frozen Campaign-A arithmetic ``tc_rule`` (8d402d11) -- the adoption
     quantity path, with S substituted and every other input unchanged. The ``R`` argument of ``direct`` is the frozen
     tc_rule module wrapped by a CAPTURING PROXY that records the arguments and results of every frozen call
     (env4, taylor_bounds, radius, object_half_width, coefficients) and delegates unchanged. The per-r tuple
     (f_F, f_D, f_H, f_G, Env4, H_hat_r(a), |G_hat_r(a)|) is read off those recorded calls: it is exactly what the
     frozen path consumed (freeze design section 2).
 (b) the same quantities re-derived from the extracted per-r tuple at s = rho, with gates
       G-R1  whole-cell enclosure rebuilt from the tuple at s = rho == frozen (lo, hi)   [and == committed H_exact]
       G-R2  frozen-clause Gamma rebuilt from the tuple == frozen Gamma                  [and == committed Gamma_exact]
       G-R3  coefficient level: the extracted tuple == an INDEPENDENT re-derivation of THEOREM_TCT's premise supply
             (own code, no frozen function) [and == committed per-r values where given]; catches rad(rho)-preserving
             mis-shapes of rad(s)
       G-R4  M_consumed == mag(H_final) (tpt N7) and the profile/cap intersection is non-empty at s = 0 (tpt N5),
             for the cell constants AND for every block's constants (narrowest point of each piece)
 (c) TPT with the cell constants (OV tpt.py r2, sha256 05cebc9c, loaded by path and hash-checked by the loader),
 (d) TPT-B with the block constants (tpt.penalty_blocked), after refusing any block list that does not TILE the cell
     exactly or has a constant above the cell supply,
 and two transport cross-checks against an INDEPENDENT integrator (pointwise band evaluation in t + Boole's rule,
 exact for the degree-5 integrands; certified bracket where the K1 cap crosses the profile inside a piece):
       G-T1  tpt P_TPT inside the independent bracket;   G-T2  tpt P_B inside the independent bracket;
       G-D   dominance  P_B <= P_TPT <= P_C5T <= P_frozen.
 Any failed gate is a STOP with no penalty reported (status STOP, code REPRODUCTION_FAILED / BLOCKS_REFUSED /
 TRANSPORT_CHECK_FAILED / GUARD_REFUSED / INPUT_REFUSED / FROZEN_PATH_REFUSED).

Bundle schema (all numbers exact rational strings; floats refused):
  label        {"detector", "m", "cell"}                               (bound to meas.cell and cover.index)
  meas         the TCT_INPUTS schema of tct_inputs.py (rho, e0, left, right, norms.k[5], norms.j[5], sup_S0[5],
               r["0".."4"]{delta_F, delta_D, delta_H, eps_src[4], sup{F,D,H}, H_at_a[2]}, W2["r:j"][2],
               order3_fields_present false)
  aux          the K1 record's auxiliary_evidence: candidate_suprema{h:j:3, Sclosed:0:3, S:r:3}, midpoint_eps{h:j:3,
               Sclosed:3, S:r:3}
  adopted_m5   the adopted extract's m["5"]: R_interval{lo,hi}, D_interval{lo,hi}, R2_interval{lo,hi}, M_R2
  cover        {index, detector, left, right, e0, rho}  (the frozen loader's cover-cell fields; parsed by its rat)
  supply       {A0, A1, A2}  (or supply_sources, combined by the frozen c2_d5_forecast.combine rule)
  blocks       optional [{e_lo, e_hi, A0, A1, A2}]
  committed    optional {H_exact[2], Gamma_exact, M_after_exact, per_r{r: {fF,fD,fH,fG,Env4,H_at_a[2],abs_G}}}
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from fractions import Fraction as F
from math import comb
from pathlib import Path

HERE = Path(__file__).resolve()
NS = HERE.parents[2]


def _load_by_path(name: str, path: Path):
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


Q = _load_by_path("c308E_quarantine", NS / "code" / "c308_quarantine.py")
Q.install_import_guard()
FP = _load_by_path("c308E_frozen_path_loader", HERE.parent / "frozen_path_loader.py")
MODS = FP.load_all()
C2, T, R, DC, KM, TPT = (MODS[k] for k in ("c2_d5", "tctr", "tcr", "dc", "km", "tpt"))

M_FROZEN = 5          # the frozen direct clause consumes m = 5 only (c2_d5_forecast.py:80)
FIELDS = ("A0", "A1", "A2")
TUPLE = ("fF", "fD", "fH", "fG", "Env4")


class Stop(RuntimeError):
    def __init__(self, code: str, reason: str):
        super().__init__(f"{code}: {reason}")
        self.code, self.reason = code, reason


def sha256_file(p: Path) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def q(x) -> F:
    """Exact rational from a string / int / Fraction; floats and bools refused (N6)."""
    if isinstance(x, bool) or isinstance(x, float):
        raise Stop("INPUT_REFUSED", f"non-exact numeric {x!r}")
    if isinstance(x, (F, int)):
        return F(x)
    if isinstance(x, str):
        return F(x)
    raise Stop("INPUT_REFUSED", f"unparseable numeric {x!r}")


def s(x) -> str:
    return str(x)


# ------------------------------------------------------------------ the capturing proxy for the frozen tc_rule
class CapturingR:
    """Passed as ``R`` to the frozen ``direct`` / ``tail_enclosure``. Delegates every call to the frozen tc_rule
    function UNCHANGED and records (args, result). Nothing is recomputed here."""

    NAMES = ("env4", "taylor_bounds", "radius", "object_half_width", "coefficients")

    def __init__(self, frozen):
        self._f = frozen
        self.calls = {n: [] for n in self.NAMES}

    def __getattr__(self, name):
        if name not in self.NAMES:
            raise AttributeError(f"the frozen path asked for an unexpected R.{name}")
        fn = getattr(self._f, name)

        def wrapped(*a, **kw):
            out = fn(*a, **kw)
            self.calls[name].append({"args": a, "kw": kw, "out": out})
            return out
        return wrapped


# ------------------------------------------------------------------ independent re-derivation of the TC-T premise supply
def rederive_tuple(meas: dict, aux: dict) -> dict:
    """THEOREM_TCT's premise supply (P2') + (P3') re-derived in own code (no frozen function): per r the tuple
    (fF, fD, fH, fG, Env4) with |G_hat(a)| = 0. Towers: pure (TC (P3)); midpoint order-3 slot = min(pure, adopted);
    cell order-3 slot = min(pure, adopted + rho * pure order-4); cell order-4 re-derived by Leibniz from the cell
    tower and never widened; sigma3 = min(Leibniz on the midpoint tower, adopted source bound); sigma4 = Leibniz on
    the cell tower (sup_S0[4] for r = 0); f_G = k3 sF + 3 k2 sD + 3 k1 sH + sigma3 + eps_src[3];
    Env4 = sigma4 + sum_{i=1..4} C(4,i) k_i T^(4-i)(rho) with the candidate majorant T(s) = sF + s sD + s^2 sH/2."""
    rho = q(meas["rho"])
    k = [q(v) for v in meas["norms"]["k"]]
    jn = [q(v) for v in meas["norms"]["j"]]
    s0 = [q(v) for v in meas["sup_S0"]]
    cs, me = aux["candidate_suprema"], aux["midpoint_eps"]
    pure = {}
    for n in range(5):
        pure[1, n] = F(1) if n == 0 else s0[n - 1]
    for h in (2, 3, 4):
        pure[h, 0] = F(1)
        for n in range(1, 5):
            pure[h, n] = sum((comb(n, i) * k[i] * pure[h - 1, n - i] for i in range(n + 1)), F(0))
    mid, cell = dict(pure), dict(pure)
    for h in (1, 2, 3, 4):
        adopted = q(cs[f"h:{h}:3"]) + q(me[f"h:{h}:3"])
        mid[h, 3] = min(pure[h, 3], adopted)
        cell[h, 3] = min(pure[h, 3], adopted + rho * pure[h, 4])
    for h in (2, 3, 4):
        cell[h, 4] = min(pure[h, 4], sum((comb(4, i) * k[i] * cell[h - 1, 4 - i] for i in range(5)), F(0)))
    out = {}
    for r in range(5):
        o = meas["r"][str(r)]
        sF, sD, sH = (q(o["sup"][x]) for x in ("F", "D", "H"))
        if r == 0:
            a3 = q(cs["Sclosed:0:3"]) + q(me["Sclosed:3"])
            sig3 = min(s0[3], a3)
            sig4 = s0[4]
        else:
            a3 = q(cs[f"S:{r}:3"]) + q(me[f"S:{r}:3"])
            sig3 = min(sum((comb(3, i) * jn[i] * mid[r, 3 - i] for i in range(4)), F(0)), a3)
            sig4 = sum((comb(4, i) * jn[i] * cell[r, 4 - i] for i in range(5)), F(0))
        eps = [q(v) for v in o["eps_src"]]
        Tn = [sF + rho * sD + rho ** 2 * sH / 2, sD + rho * sH, sH, F(0)]   # T^(n)(rho), n = 0..3 (sG = 0)
        env4 = sig4 + sum((comb(4, i) * k[i] * Tn[4 - i] for i in range(1, 5)), F(0))
        out[r] = {"fF": q(o["delta_F"]) + eps[0], "fD": q(o["delta_D"]) + eps[1], "fH": q(o["delta_H"]) + eps[2],
                  "fG": k[3] * sF + 3 * k[2] * sD + 3 * k[1] * sH + sig3 + eps[3], "Env4": env4,
                  "H_at_a": tuple(q(v) for v in o["H_at_a"]), "abs_G": F(0), "sigma3": sig3, "sigma4": sig4}
    return out


# ------------------------------------------------------------------ own profile arithmetic (independent of tpt.py)
def p_at(t: dict, sv: F) -> tuple:
    """(p0, p1, p2)(s) = (P, P', P'')(s) of the quartic P(s) = fF + s fD + s^2 fH/2 + s^3 fG/6 + s^4 Env4/24."""
    fF, fD, fH, fG, e4 = (t[x] for x in TUPLE)
    p0 = fF + sv * fD + sv ** 2 * fH / 2 + sv ** 3 * fG / 6 + sv ** 4 * e4 / 24
    p1 = fD + sv * fH + sv ** 2 * fG / 2 + sv ** 3 * e4 / 6
    p2 = fH + sv * fG + sv ** 2 * e4 / 2
    return p0, p1, p2


def rad_at(t: dict, A: tuple, sv: F) -> F:
    p0, p1, p2 = p_at(t, sv)
    return A[0] * p2 + 2 * A[1] * p1 + A[2] * p0 + sv * t["abs_G"]


def band_at(ext: dict, A: tuple, sv: F, cap: tuple | None) -> tuple:
    """(L, U) of R''_m at distance sv from e0 with constants A, capped by the consumed enclosure."""
    m = F(len(ext["terms"]))
    lo, hi = ext["W"]
    for t in ext["terms"]:
        rr = rad_at(t, A, sv)
        lo += (t["H_at_a"][0] - rr) / m
        hi += (t["H_at_a"][1] + rr) / m
    if cap is not None:
        lo, hi = max(cap[0], lo), min(cap[1], hi)
    return lo, hi


def whole_cell_from_tuple(ext: dict, A: tuple) -> tuple:
    return band_at(ext, A, ext["rho"], None)


# ------------------------------------------------------------------ independent transport integrator (G-T1, G-T2)
def _boole(f, a: F, b: F) -> F:
    h = (b - a) / 4
    return (b - a) / 90 * (7 * f(a) + 32 * f(a + h) + 12 * f(a + 2 * h) + 32 * f(a + 3 * h) + 7 * f(b))


def _piece_bracket(ext, A, cap, side, sa: F, sb: F, bits: int = 256) -> tuple:
    """Bracket [lo, hi] of int over s in [sa, sb] of t * (-L(t)) (right, t = e0 + s) or t * U(t) (left, t = e0 - s).
    The profile part is a degree-5 polynomial in t, integrated exactly by Boole's rule; a cap crossing inside the
    piece is bracketed to width (sb - sa) / 2^bits with a certified |integrand| bound on that sliver."""
    e0 = ext["e0"]
    tsign = 1 if side == "R" else -1

    def prof(sv):                                   # the uncapped profile value at s
        lo, hi = band_at(ext, A, sv, None)
        return -lo if side == "R" else hi

    capv = None if cap is None else (-cap[0] if side == "R" else cap[1])

    def integrand_prof(sv):
        return (e0 + tsign * sv) * prof(sv)

    def integrand_cap(sv):
        return (e0 + tsign * sv) * capv

    if capv is None or prof(sb) <= capv:            # profile (non-decreasing in s) never exceeds the cap
        v = _boole(integrand_prof, sa, sb)
        return v, v
    if prof(sa) >= capv:                            # the cap binds on the whole piece
        v = _boole(integrand_cap, sa, sb)
        return v, v
    c1, c2 = sa, sb                                 # prof(c1) < capv <= prof(c2)
    for _ in range(bits):
        mid = (c1 + c2) / 2
        if prof(mid) < capv:
            c1 = mid
        else:
            c2 = mid
    core = _boole(integrand_prof, sa, c1) + _boole(integrand_cap, c2, sb)
    tmax = e0 + c2 if side == "R" else e0            # 0 < t <= tmax on the sliver (x_lo > 0 is checked by tpt)
    B = abs(tmax) * max(abs(capv), abs(prof(c1)), abs(prof(c2)))
    return core - (c2 - c1) * B, core + (c2 - c1) * B


def _pieces(ext, blocks, side):
    e0, x_lo, x_hi = ext["e0"], ext["x_lo"], ext["x_hi"]
    if side == "R":
        cuts = sorted({e0, x_hi} | {b[k] for b in blocks for k in (0, 1) if e0 < b[k] < x_hi})
    else:
        cuts = sorted({x_lo, e0} | {b[k] for b in blocks for k in (0, 1) if x_lo < b[k] < e0}, reverse=True)
    out = []
    for a, b in zip(cuts, cuts[1:]):
        mid = (a + b) / 2
        hit = [bl for bl in blocks if bl[0] <= mid <= bl[1]]
        if len(hit) != 1:
            raise Stop("BLOCKS_REFUSED", "a transport piece is not inside exactly one block")
        sa, sb = (a - e0, b - e0) if side == "R" else (e0 - a, e0 - b)
        out.append((sa, sb, hit[0][2]))
    return out


def independent_penalty(ext, blocks, cap, grid_per_piece: int = 0) -> dict:
    """Independent P* bracket for block constants (a single block = the cell gives TPT); optional interior grid scan
    of the running integral (quasi-convexity check: interior values must not exceed the piece-end maximum)."""
    lo_best, hi_best = F(0), F(0)
    interior_max_hi = None
    for side in ("R", "L"):
        run_lo = run_hi = F(0)
        for sa, sb, A in _pieces(ext, blocks, side):
            for g in range(1, grid_per_piece):
                sm = sa + (sb - sa) * g / grid_per_piece
                blo, bhi = _piece_bracket(ext, A, cap, side, sa, sm)
                v = run_hi + bhi
                interior_max_hi = v if interior_max_hi is None else max(interior_max_hi, v)
            blo, bhi = _piece_bracket(ext, A, cap, side, sa, sb)
            run_lo += blo
            run_hi += bhi
            lo_best, hi_best = max(lo_best, run_lo), max(hi_best, run_hi)
    return {"P_lo": lo_best, "P_hi": hi_best, "interior_max_hi": interior_max_hi}


def bl_pieces_hint(ext, blocks) -> list:
    return _pieces(ext, blocks, "R") + _pieces(ext, blocks, "L")


def split_tolerance(ext, S, cap, n_pieces: int) -> F:
    """Upper bound of tpt.py's over-estimate from its 60-bit non-binding-side cap split (T3): per piece at most a
    sliver of width rho/2^60 on which the cap replaces the profile, |t| <= x_hi, |cap - profile| <= |cap| + |band|."""
    if cap is None:
        return F(0)
    lo, hi = band_at(ext, S, ext["rho"], None)
    amp = abs(cap[0]) + abs(cap[1]) + abs(lo) + abs(hi)
    return n_pieces * ext["rho"] / 2 ** 60 * ext["x_hi"] * amp


def transport_gate(P: F, ind: dict, tol: F) -> dict:
    """tpt's penalty P must lie in [P_lo, P_hi + tol]; P >= P_hi certifies P >= the true sup (soundness)."""
    ok = ind["P_lo"] <= P <= ind["P_hi"] + tol
    return {"P": s(P), "indep_lo": s(ind["P_lo"]), "indep_hi": s(ind["P_hi"]), "tol": s(tol), "pass": ok,
            "certified_ge_true_sup": P >= ind["P_hi"], "exact_equal": ind["P_lo"] == ind["P_hi"] == P}


# ------------------------------------------------------------------ blocks
def check_blocks(blocks_in: list, x_lo: F, x_hi: F, S: tuple) -> list:
    """Exact tiling of [x_lo, x_hi] (sorted, first starts at x_lo, last ends at x_hi, consecutive edges equal, each
    non-degenerate) and componentwise A^i <= S; exact rationals only. Returns [(e_lo, e_hi, (A0, A1, A2))]."""
    if not blocks_in:
        raise Stop("BLOCKS_REFUSED", "empty block list")
    bl = []
    for b in blocks_in:
        e_lo, e_hi = q(b["e_lo"]), q(b["e_hi"])
        A = tuple(q(b[x]) for x in FIELDS)
        Q.guard_drift(e_lo, e_hi)
        if min(A) < 0:
            raise Stop("BLOCKS_REFUSED", "negative block constant")
        if any(a > c for a, c in zip(A, S)):
            raise Stop("BLOCKS_REFUSED", "block constant above the cell-level supply (must be min'ed with S)")
        if not e_lo < e_hi:
            raise Stop("BLOCKS_REFUSED", "degenerate or inverted block")
        bl.append((e_lo, e_hi, A))
    bl.sort(key=lambda b: b[0])
    if bl[0][0] != x_lo or bl[-1][1] != x_hi:
        raise Stop("BLOCKS_REFUSED", "blocks do not start at x_lo and end at x_hi exactly")
    for a, b in zip(bl, bl[1:]):
        if b[0] != a[1]:
            raise Stop("BLOCKS_REFUSED", "blocks are not contiguous without overlap (tiling is not exact)")
    return bl


# ------------------------------------------------------------------ supply
def supply_from(bundle: dict, meas: dict) -> tuple:
    if "supply_sources" in bundle:
        sup = {}
        kn = [q(v) for v in meas["norms"]["k"]]
        for name, src in bundle["supply_sources"].items():
            if src["kind"] == "lemma_G":
                sup[name] = T.atom_constants_generic(q(src["C_upper"]), kn[1], kn[2])
            elif src["kind"] == "lemma_Dv_prime":
                args = tuple(q(src[x]) for x in ("Abar", "tau", "C_T", "D_lo", "D1", "D2"))
                frozen = DC.atom_constants_r2(*args)
                if {j: frozen[j] for j in FIELDS} != C2._atom_independent(*args):
                    raise Stop("FROZEN_PATH_REFUSED", f"atom-constant crosscheck disagrees for supply {name}")
                sup[name] = frozen
            else:
                raise Stop("INPUT_REFUSED", f"unknown supply kind {src['kind']}")
        A, prov = C2.combine(sup)
        S = tuple(A[j] for j in FIELDS)
        if "supply" in bundle and tuple(q(bundle["supply"][j]) for j in FIELDS) != S:
            raise Stop("INPUT_REFUSED", "explicit supply differs from the frozen combine of its sources")
        return S, prov
    return tuple(q(bundle["supply"][j]) for j in FIELDS), {j: "given" for j in FIELDS}


# ------------------------------------------------------------------ the pipeline
def _guards(bundle: dict) -> None:
    lab = bundle["label"]
    Q.guard_cell(lab["detector"], lab["m"], lab["cell"])
    cov, meas = bundle["cover"], bundle["meas"]
    Q.guard_cell(cov.get("detector", lab["detector"]), lab["m"], cov["index"])
    Q.guard_cell(lab["detector"], lab["m"], meas["cell"])
    Q.guard_drift(KM.rat(cov["left"]), KM.rat(cov["right"]))
    Q.guard_drift(KM.rat(cov["e0"]) - KM.rat(cov["rho"]), KM.rat(cov["e0"]) + KM.rat(cov["rho"]))
    for key in ("left", "right", "e0"):
        if key in meas:
            Q.guard_drift(q(meas[key]))
    for b in bundle.get("blocks") or []:
        Q.guard_drift(q(b["e_lo"]), q(b["e_hi"]))


def _extract(cap: CapturingR, meas: dict) -> dict:
    c = cap.calls
    if [len(c[n]) for n in ("env4", "taylor_bounds", "radius", "object_half_width")] != [5, 5, 5, 5] \
            or len(c["coefficients"]) != 1:
        raise Stop("REPRODUCTION_FAILED", f"unexpected frozen call pattern {[(n, len(v)) for n, v in c.items()]}")
    terms = []
    for r in range(5):
        fF, fD, fH, fG, e4, rho_tb = c["taylor_bounds"][r]["args"]
        rho_h, aG, rad_in = c["object_half_width"][r]["args"]
        if c["radius"][r]["out"] != rad_in or c["env4"][r]["out"] != e4 or rho_tb != rho_h:
            raise Stop("REPRODUCTION_FAILED", f"frozen call chain inconsistent at r = {r}")
        terms.append({"fF": fF, "fD": fD, "fH": fH, "fG": fG, "Env4": e4, "abs_G": aG,
                      "H_at_a": tuple(q(v) for v in meas["r"][str(r)]["H_at_a"]),
                      "frozen_p": c["taylor_bounds"][r]["out"], "frozen_rad": rad_in,
                      "frozen_half": c["object_half_width"][r]["out"], "rho": rho_tb})
    rows = c["coefficients"][0]["out"]
    m_rows = c["coefficients"][0]["args"][0]
    W = [F(0), F(0)]
    for kind, r, jj, cc in rows:
        if kind == "W":
            a, b = (q(v) for v in meas["W2"][f"{r}:{jj}"])
            W[0] += cc * a
            W[1] += cc * b
        elif cc != F(1, m_rows):
            raise Stop("REPRODUCTION_FAILED", "frozen F-row weight is not 1/m")
    n_f = sum(1 for row in rows if row[0] == "F")
    return {"terms": terms[:n_f], "W": (W[0], W[1]), "m_rows": m_rows}


def evaluate_bundle(bundle: dict, *, mutate=None, tpt_override: dict | None = None, grid_per_piece: int = 0,
                    proxy_factory=None) -> dict:
    """Run (a)-(d) with all gates. ``mutate`` (controls only) edits the extracted object right after capture;
    ``tpt_override`` (controls only) substitutes a planted penalty implementation for tpt.penalty_closed /
    tpt.penalty_blocked; ``proxy_factory`` (controls only) replaces the capturing proxy (e.g. a tampering proxy).
    Refusals are returned as STOP records, never raised."""
    out = {"status": None, "gates": {}, "loader_record": FP.record(), "tpt_sha256": FP.FROZEN_FILES["tpt"][1]}
    try:
        _guards(bundle)
        return _evaluate(bundle, out, mutate, tpt_override or {}, grid_per_piece, proxy_factory or CapturingR)
    except Q.QuarantineRefusal as exc:
        out.update(status="STOP", stop_code="GUARD_REFUSED", stop_reason=str(exc))
    except Stop as exc:
        out.update(status="STOP", stop_code=exc.code, stop_reason=exc.reason)
    except SystemExit as exc:                       # the frozen path's own refusals
        out.update(status="STOP", stop_code="FROZEN_PATH_REFUSED", stop_reason=str(exc))
    except (ValueError, ZeroDivisionError, KeyError, AssertionError) as exc:
        out.update(status="STOP", stop_code="INPUT_REFUSED", stop_reason=f"{type(exc).__name__}: {exc}")
    return out


def _evaluate(bundle, out, mutate, tpt_override, grid_per_piece, proxy_factory) -> dict:  # noqa: C901
    lab, meas, aux, ad, cov = (bundle[k] for k in ("label", "meas", "aux", "adopted_m5", "cover"))
    if int(lab["m"]) != M_FROZEN:
        raise Stop("INPUT_REFUSED", f"label m = {lab['m']}: the frozen direct clause is m = {M_FROZEN} only")
    if meas["cell"] != lab["cell"] or cov["index"] != lab["cell"]:
        raise Stop("INPUT_REFUSED", "label cell is not bound to meas.cell and cover.index")
    if meas.get("order3_fields_present") is not False:
        raise Stop("INPUT_REFUSED", "input object is not an order-3-free TC-T input")
    e0, rho, x_hi = (KM.rat(cov[t]) for t in ("e0", "rho", "right"))
    x_lo = KM.rat(cov["left"])
    if e0 - rho != x_lo or e0 + rho != x_hi or q(meas["rho"]) != rho:
        raise Stop("INPUT_REFUSED", "cover geometry, meas.rho and [left, right] disagree")
    if "e0" in meas and q(meas["e0"]) != e0:
        raise Stop("INPUT_REFUSED", "meas.e0 differs from the cover e0")
    S, prov = supply_from(bundle, meas)
    Sd = dict(zip(FIELDS, S))

    # (a) reproduction mode: the frozen direct clause, through the capturing proxy
    cap = proxy_factory(R)
    res = C2.direct(T, cap, meas, aux, Sd, ad, cov, KM)
    ext = _extract(cap, meas)
    ext.update(e0=e0, rho=rho, x_lo=x_lo, x_hi=x_hi)
    for r, t in enumerate(ext["terms"]):
        o = res["obj"][r]
        if (o["f_G"], o["env4"], o["rad"], o["half"], o["abs_G_at_a"]) != (t["fG"], t["Env4"], t["frozen_rad"],
                                                                          t["frozen_half"], t["abs_G"]):
            raise Stop("REPRODUCTION_FAILED", f"captured tuple differs from the frozen per-r object at r = {r}")
        if t["rho"] != rho:
            raise Stop("REPRODUCTION_FAILED", "frozen path used a different rho")
    R2 = (q(ad["R2_interval"]["lo"]), q(ad["R2_interval"]["hi"]))
    M0 = q(ad["M_R2"])
    g_hi = q(ad["R_interval"]["hi"]) - e0 * q(ad["D_interval"]["lo"])
    frozen = {"lo": res["lo"], "hi": res["hi"], "M": res["M"], "Gamma": res["Gamma"]}
    out["frozen"] = {k: s(v) for k, v in frozen.items()} | {"pass": bool(res["pass"])}
    out["supply"] = {j: s(v) for j, v in Sd.items()} | {"provenance": prov}

    if mutate is not None:                          # controls only
        mutate(ext)
    g = out["gates"]

    # (b) re-derivations and gates
    red = rederive_tuple(meas, aux)
    mism = []
    for r, t in enumerate(ext["terms"]):
        for x in TUPLE + ("abs_G", "H_at_a"):
            if t[x] != red[r][x]:
                mism.append(f"r{r}.{x}")
    com = (bundle.get("committed") or {}).get("per_r")
    if com is not None:
        for r, t in enumerate(ext["terms"]):
            c = com[str(r)]
            for x in TUPLE + ("abs_G",):
                if t[x] != q(c[x]):
                    mism.append(f"committed r{r}.{x}")
            if t["H_at_a"] != tuple(q(v) for v in c["H_at_a"]):
                mism.append(f"committed r{r}.H_at_a")
    if len(ext["terms"]) != M_FROZEN or ext["m_rows"] != M_FROZEN:
        mism.append("m")
    g["G-R3"] = {"pass": not mism, "mismatches": mism[:20],
                 "committed_per_r_checked": com is not None}
    Hx = whole_cell_from_tuple(ext, S)
    g1 = {"rebuilt": [s(Hx[0]), s(Hx[1])], "frozen": [s(res["lo"]), s(res["hi"])]}
    g1["pass"] = Hx == (res["lo"], res["hi"])
    if (bundle.get("committed") or {}).get("H_exact") is not None:
        g1["committed_equal"] = Hx == tuple(q(v) for v in bundle["committed"]["H_exact"])
        g1["pass"] = g1["pass"] and g1["committed_equal"]
    g["G-R1"] = g1
    a_, b_ = max(R2[0], Hx[0]), min(R2[1], Hx[1])
    if a_ > b_:
        g["G-R2"] = {"pass": False, "reason": "empty whole-cell intersection: the consumer falls back to M_R2"}
        raise Stop("REPRODUCTION_FAILED", "empty consumed intersection H_final (TPT not applicable)")
    H_final = (a_, b_)
    mag = max(abs(a_), abs(b_))
    M_ext = min(M0, mag)
    Gam_ext = g_hi + rho * x_hi * M_ext
    g2 = {"rebuilt": s(Gam_ext), "frozen": s(res["Gamma"]), "pass": Gam_ext == res["Gamma"] and M_ext == res["M"]}
    if (bundle.get("committed") or {}).get("Gamma_exact") is not None:
        g2["committed_equal"] = (Gam_ext == q(bundle["committed"]["Gamma_exact"])
                                 and M_ext == q(bundle["committed"]["M_after_exact"]))
        g2["pass"] = g2["pass"] and g2["committed_equal"]
    g["G-R2"] = g2
    M_consumed = res["M"] if "M_consumed_override" not in ext else ext["M_consumed_override"]
    g4 = {"M_consumed": s(M_consumed), "mag_H_final": s(mag), "M_eq_mag": M_consumed == mag}
    lo0, hi0 = band_at(ext, S, F(0), H_final)
    g4["nonempty_s0_cell"] = lo0 <= hi0
    g["G-R4"] = g4
    failed = [k for k in ("G-R1", "G-R2", "G-R3") if not g[k]["pass"]]
    if not g4["M_eq_mag"]:
        failed.append("G-R4(M)")
    if not g4["nonempty_s0_cell"]:
        failed.append("G-R4(N5)")
    if failed:
        g4["pass"] = not any(f.startswith("G-R4") for f in failed)
        raise Stop("REPRODUCTION_FAILED", "gates failed: " + ", ".join(failed))
    g4["pass"] = True

    # (c) TPT with the cell constants (OV tpt.py r2)
    terms = [TPT.SourceTerm(H_at_a=t["H_at_a"], abs_G_at_a=t["abs_G"], fF=t["fF"], fD=t["fD"], fH=t["fH"],
                            fG=t["fG"], Env4=t["Env4"]) for t in ext["terms"]]
    cp = TPT.CellProfile(detector=str(lab["detector"]), m=int(lab["m"]), cell=int(lab["cell"]), e0=e0, rho=rho,
                         g_hi=g_hi, A0=S[0], A1=S[1], A2=S[2], terms=terms, W=ext["W"], H_K1=H_final,
                         M_consumed=M_consumed)
    lo_p, hi_p = TPT.lo_hi_polys(cp)
    if (TPT.peval(lo_p, rho), TPT.peval(hi_p, rho)) != (res["lo"], res["hi"]):
        g["G-R1"]["tpt_profile_at_rho_equal"] = False
        raise Stop("REPRODUCTION_FAILED", "tpt profile at s = rho differs from the frozen enclosure")
    g["G-R1"]["tpt_profile_at_rho_equal"] = True
    pen_closed = tpt_override.get("penalty_closed", TPT.penalty_closed)
    TPT.check_nonempty(cp)
    pc = pen_closed(cp)
    P_tpt = pc["P_star"]
    P_c5t = TPT.penalty_c5t(cp)
    P_fr = TPT.penalty_frozen(cp)
    if g_hi + P_fr != res["Gamma"]:
        raise Stop("REPRODUCTION_FAILED", "tpt frozen penalty does not reproduce the frozen Gamma")
    cell_block = [(x_lo, x_hi, S)]
    ind = independent_penalty(ext, cell_block, H_final, grid_per_piece)
    tol = split_tolerance(ext, S, H_final, 2 * len(bl_pieces_hint(ext, cell_block)))
    g["G-T1"] = transport_gate(P_tpt, ind, tol)
    if ind["interior_max_hi"] is not None:
        g["G-T1"]["interior_scan_le_P"] = ind["interior_max_hi"] <= ind["P_hi"]
        g["G-T1"]["pass"] = g["G-T1"]["pass"] and g["G-T1"]["interior_scan_le_P"]
    if not g["G-T1"]["pass"]:
        raise Stop("TRANSPORT_CHECK_FAILED", "G-T1: tpt P_TPT outside the independent bracket")

    # (d) TPT-B
    if bundle.get("blocks"):
        bl = check_blocks(bundle["blocks"], x_lo, x_hi, S)
    else:
        bl = cell_block
    for side in ("R", "L"):                         # G-R4 for every block: narrowest point of each piece
        for sa, sb, A in _pieces(ext, bl, side):
            L0, U0 = band_at(ext, A, sa, H_final)
            if L0 > U0:
                g["G-R4"]["nonempty_blocks"] = False
                raise Stop("REPRODUCTION_FAILED", "G-R4: block band empty at a piece's narrowest point")
    g["G-R4"]["nonempty_blocks"] = True
    blocks_tpt = [TPT.Block(e_lo=a, e_hi=b, A0=A[0], A1=A[1], A2=A[2]) for (a, b, A) in bl]
    pen_blocked = tpt_override.get("penalty_blocked", TPT.penalty_blocked)
    rb = pen_blocked(cp, blocks_tpt)
    P_B = rb["P_star_B"]
    indB = independent_penalty(ext, bl, H_final, grid_per_piece)
    tolB = split_tolerance(ext, S, H_final, 2 * len(bl_pieces_hint(ext, bl)))
    g["G-T2"] = transport_gate(P_B, indB, tolB)
    if indB["interior_max_hi"] is not None:
        g["G-T2"]["interior_scan_le_P"] = indB["interior_max_hi"] <= indB["P_hi"]
        g["G-T2"]["pass"] = g["G-T2"]["pass"] and g["G-T2"]["interior_scan_le_P"]
    if not g["G-T2"]["pass"]:
        raise Stop("TRANSPORT_CHECK_FAILED", "G-T2: tpt P_B outside the independent bracket")
    dom = P_B <= P_tpt <= P_c5t <= P_fr
    g["G-D"] = {"pass": dom}
    if not dom:
        raise Stop("TRANSPORT_CHECK_FAILED", "G-D: dominance P_B <= P_TPT <= P_C5T <= P_frozen violated")

    # closed form of the binding regime (informational gate; applies when H subset R2, lower end binds, C_lo < 0)
    C_lo = ext["W"][0] + sum(t["H_at_a"][0] for t in ext["terms"]) / len(ext["terms"])
    binding = R2[0] <= Hx[0] and Hx[1] <= R2[1] and abs(Hx[0]) >= abs(Hx[1]) and C_lo < 0
    if binding:
        Pb = [sum(p_at(t, rho)[j] for t in ext["terms"]) / len(ext["terms"]) for j in range(3)]
        cf = g_hi + rho * x_hi * abs(C_lo) + rho * x_hi * (S[0] * Pb[2] + 2 * S[1] * Pb[1] + S[2] * Pb[0])
        g["G-CF"] = {"applies": True, "pass": cf == res["Gamma"]}
        if cf != res["Gamma"]:
            raise Stop("REPRODUCTION_FAILED", "binding-regime closed form differs from the frozen Gamma")
    else:
        g["G-CF"] = {"applies": False}

    out.update(status="OK", values={
        "g_hi": s(g_hi), "e0": s(e0), "rho": s(rho), "H_final": [s(a_), s(b_)],
        "P_B": s(P_B), "P_tpt": s(P_tpt), "P_c5t": s(P_c5t), "P_frozen": s(P_fr),
        "Gamma_B": s(g_hi + P_B), "Gamma_tpt": s(g_hi + P_tpt), "Gamma_c5t": s(g_hi + P_c5t),
        "Gamma_frozen": s(res["Gamma"]), "I_right": s(pc["I_right"]), "I_left": s(pc["I_left"]),
        "split_right": None if pc["split_right"] is None else s(pc["split_right"]),
        "split_left": None if pc["split_left"] is None else s(pc["split_left"]),
        "n_blocks": len(bl), "pieces_B": rb.get("pieces")})
    out["float_view"] = {k: float(F(v)) for k, v in out["values"].items()
                         if isinstance(v, str) and k not in ("split_right", "split_left")}
    out["extracted_tuple"] = [{x: s(t[x]) for x in TUPLE + ("abs_G",)} | {"H_at_a": [s(v) for v in t["H_at_a"]]}
                              for t in ext["terms"]]
    out["W_sum"] = [s(ext["W"][0]), s(ext["W"][1])]
    return out
