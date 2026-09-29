"""SRK certificate producer (primary implementation; stdlib only; exact rationals).

For a geometry (h, k), a DYADIC drift block E = [e_lo, e_hi] and a Hermite index i in {0,..,4}:

  (W) certify W >= 0 and W >= 1 + K_e W on X for all e in E      (whole kernel; multiplicative repair (1+eta))
  (V) certify V' = V + lam W with V' >= Psi_i + K_e V' on X for all e in E, Psi_i := kbar_i^E (THEOREM_SRK s.1)
      by the additive rule lam = max(0, -r_min) + mu*max(1, sup Psi)   (THEOREM_SRK section 7)

and return Gamma_i^E := V'(a) >= sup_{e in E} (R_e kbar_i^E)(a)  (Lemma SV).  i = 0 gives Psi = k_0 <= 1, the
constant-weight control.  All parameters follow THEOREM_SRK section 7; nothing is tuned per cell.

Every new entry point calls the campaign guard: quarantined cells and the drift band [6/5, 13/5] (and its mirror)
are refused for the REAL geometry.  Synthetic geometries (h, k) != (5, 1/2) are decoys and are not band-guarded
(their operators do not transfer to the target kernel), but they are logged.
"""
from __future__ import annotations

import hashlib
import json
import math
import sys
import time
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve().parent
NS = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(NS / "code"))
import q309_guard as Q  # noqa: E402

Q.install_import_guard()
import srk_kernel as KX  # noqa: E402
import srk_float as FL  # noqa: E402
import srk_envelope as EN  # noqa: E402

MU = F(1, 1 << 20)
PRODUCER_FILES = ("srk_kernel.py", "srk_float.py", "srk_envelope.py", "srk_certify.py")


def producer_fingerprint() -> dict:
    """sha256 of every producer source file (and of the pinned c1b_gauss it imports): binds evidence to a code state."""
    out = {f: hashlib.sha256((HERE / f).read_bytes()).hexdigest() for f in PRODUCER_FILES}
    out["c1b_gauss.py"] = hashlib.sha256(Path(KX.G.__file__).read_bytes()).hexdigest()
    out["combined"] = hashlib.sha256(json.dumps(out, sort_keys=True).encode()).hexdigest()
    return out


def _log_call(g, what: str, e_lo, e_hi, klass: str = "NONTARGET_DECOY") -> None:
    real = (g.h == 5 and g.k == F(1, 2))
    Q.log_execution("impl/srk_certify.py", f"{what} {g.key()} E=[{e_lo},{e_hi}]", klass=klass,
                    drifts=[[e_lo, e_hi]] if real else [],
                    notes="real kernel, out-of-band decoy drift" if real else "synthetic decoy geometry")


# THEOREM_SRK section 7 / amendment A3: the drift-block rule (fixed, target-free)
GRID_BITS = 10
N_SUB = 4


def cell_blocks(e_lo, e_hi, grid_bits: int = GRID_BITS, n_sub: int = N_SUB) -> tuple:
    """(weight_block, check_sub_blocks): the weight block is the OUTWARD dyadic hull of the cell [e_lo, e_hi] on the
    2^-grid_bits grid; the check sub-blocks are its n_sub equal parts (dyadic since n_sub is a power of two).
    Every sub-block certificate uses the WHOLE weight block as its weight block (THEOREM_SRK s.7, A3)."""
    e_lo, e_hi = F(e_lo), F(e_hi)
    if e_hi < e_lo:
        raise ValueError("empty cell")
    if n_sub < 1 or n_sub & (n_sub - 1):
        raise ValueError("n_sub must be a power of two")
    s = 1 << grid_bits
    lo = F(math.floor(e_lo * s), s)
    hi = F(math.ceil(e_hi * s), s)
    if hi == lo:
        hi = lo + F(1, s)
    w = (hi - lo) / n_sub
    subs = [(lo + j * w, lo + (j + 1) * w) for j in range(n_sub)]
    assert lo <= e_lo and e_hi <= hi and subs[0][0] == lo and subs[-1][1] == hi
    return (lo, hi), subs
DEFAULT_LADDER = (8, 10, 12)


def fstr(x: F) -> str:
    x = F(x)
    return f"{x.numerator}/{x.denominator}"


def dyadic_up(x: F, bits: int = 24) -> F:
    x = F(x)
    n = -((-x.numerator * (1 << bits)) // x.denominator)
    return F(n, 1 << bits)


def is_dyadic(x: F) -> bool:
    d = F(x).denominator
    return d & (d - 1) == 0


def guard_geometry_block(g: KX.Geom, e_lo: F, e_hi: F) -> None:
    if g.h == 5 and g.k == F(1, 2):
        Q.guard_drift(e_lo, e_hi)


def at_atom(P: dict) -> F:
    return KX.peval(P, F(0), F(0), F(0))


# ------------------------------------------------------------------------------------------ e-affine families
def eaff_pair(g: KX.Geom, P0: dict, P1: dict, e_c: F, whole: bool = True) -> tuple:
    """(P_e - K_e P_e) as a region pair with e symbolic, P_e = P0 + (e - e_c) P1 (THEOREM_SRK Lemma SV')."""
    lin = KX.aff(-e_c, 0, 0, 1)                                 # (e - e_c)
    P1e = KX.pmul(P1, lin) if P1 else {}
    Pe = KX.padd(P0, P1e)
    K0 = KX.kernel_gf(g, P0, 0, whole)
    out = KX.pair_add(KX.poly_pair(Pe), K0, -1)
    if P1:
        K1 = KX.kernel_gf(g, P1, 0, whole)
        K1e = tuple({k: KX.pmul(v, lin) for k, v in gg.items()} for gg in K1)
        out = KX.pair_add(out, K1e, -1)
    return out


def eaff_at(P0: dict, P1: dict, e_c: F, e: F, p=F(0), m=F(0)) -> F:
    return KX.peval(P0, p, m, F(0)) + (F(e) - e_c) * (KX.peval(P1, p, m, F(0)) if P1 else F(0))


def cover_check(g: KX.Geom, res_pair: tuple, rhs, e_lo: F, e_hi: F, hstep: F = F(1, 4), extra_levels: int = 4,
                KT: int = 10) -> dict:
    """certified lower bound r_min of [res - rhs] over X x E (rhs(b) = upper bound of the right-hand side on box b).
    Refinement by the C1b tightness rule (amendment A1): after a pass, a box is halved iff its certified lower margin
    is below m_c - |m_c|/4 - 2^-40 (m_c = min centre margin), at most extra_levels times."""
    e_c, e_r = (e_lo + e_hi) / 2, (e_hi - e_lo) / 2
    Ai = KX.pair_to_int(res_pair)
    results = {}
    work = [(b, 0) for b in KX.base_cover(g, hstep)]
    rhs_max = F(0)
    while True:
        for b, lev in work:
            los, mids = [], []
            for reg in KX.regions_of_box(g, b):
                lo, _hi, mid = KX.gf_box_int(g, Ai[reg], (b[0], b[1], e_c), (b[2], b[3], e_r), KT)
                los.append(lo)
                mids.append(mid)
            rv = rhs(b)
            rhs_max = max(rhs_max, rv)
            results[b] = (min(los) - rv, min(mids) - rv, lev)
        m_c = min(v[1] for v in results.values())
        lim = m_c - abs(m_c) / 4 - F(1, 1 << 40)
        new = []
        for b, (ml, mc, lev) in list(results.items()):
            if ml < lim and lev < extra_levels:
                del results[b]
                new.extend((cb, lev + 1) for cb in KX.split_box(b) if KX.box_in_X_nonempty(g, cb))
        if not new:
            break
        work = new
    worst = min(results.items(), key=lambda kv: kv[1][0])
    return {"r_min": worst[1][0], "centre_min": m_c, "worst_box": [fstr(x) for x in worst[0]],
            "boxes": len(results), "max_level": max(v[2] for v in results.values()), "rhs_max": rhs_max}


def poly_min_X(g: KX.Geom, P0: dict, P1: dict, e_c: F, e_r: F) -> F:
    """certified lower bound of P0 + (e - e_c) P1 over X x [e_c - e_r, e_c + e_r]."""
    lin = KX.aff(-e_c, 0, 0, 1)
    Pe = KX.padd(P0, KX.pmul(P1, lin) if P1 else {})
    chk = cover_check(g, KX.poly_pair(Pe), lambda b: F(0), e_c - e_r, e_c + e_r, extra_levels=3)
    return chk["r_min"]


# ------------------------------------------------------------------------------------------ float proposals
def _float_solve(g: KX.Geom, e: F, d: int, rhs_fn, whole: bool = True) -> dict:
    fg = FL.FGeom(g.h, g.k)
    D = FL.Disc(fg, float(e), d)
    qr = FL.QR(D.matrix(whole))
    rhs = [rhs_fn(p, m) for (p, m) in D.pts]
    coef = qr.solve(rhs)
    return KX.dyadic_round_poly(FL.to_exact_poly(coef, D.idx, g.h), 96)


def _eaff_proposal(g: KX.Geom, e_lo: F, e_hi: F, d: int, rhs_fn, whole: bool = True) -> tuple:
    Pl = _float_solve(g, e_lo, d, rhs_fn, whole)
    Ph = _float_solve(g, e_hi, d, rhs_fn, whole)
    P0 = KX.dyadic_round_poly({k: v / 2 for k, v in KX.padd(Pl, Ph).items()}, 96)
    P1 = KX.dyadic_round_poly({k: v / (e_hi - e_lo) for k, v in KX.padd(Ph, Pl, -1).items()}, 96) \
        if e_hi > e_lo else {}
    return P0, P1


def _kbar_float(g: KX.Geom, i: int, e_lo: F, e_hi: F):
    c = float(g.c)
    el, eh = float(e_lo), float(e_hi)

    def f(p, m):
        return FL.he_abs_integral_float(i, m - c + el, c - p + eh, 200)
    return f


# ------------------------------------------------------------------------------------------ certificates
def certify_W(g: KX.Geom, e_lo: F, e_hi: F, d: int, log=print, whole: bool = True) -> dict:
    """(W): e-affine supersolution on E (whole kernel K_e, or taboo kernel K^_e when whole=False, amendment A2),
    multiplicative repair (1 + eta) (C1b rule; amendment A1)."""
    guard_geometry_block(g, e_lo, e_hi)
    _log_call(g, f"certify_W d={d} {'whole' if whole else 'taboo'}", e_lo, e_hi)
    t0 = time.time()
    e_c, e_r = (e_lo + e_hi) / 2, (e_hi - e_lo) / 2
    W0, W1 = _eaff_proposal(g, e_lo, e_hi, d, lambda p, m: 1.0, whole)
    res = KX.pair_add(eaff_pair(g, W0, W1, e_c, whole), KX.poly_pair({(0, 0, 0): F(1)}), -1)
    chk = cover_check(g, res, lambda b: F(0), e_lo, e_hi)
    rlo = chk["r_min"]
    if rlo <= -1:
        return {"status": "W_REPAIR_INAPPLICABLE", "r_lo": rlo, "degree": d}
    eta = F(0) if rlo >= 0 else dyadic_up(-rlo / (1 + rlo))
    W0, W1 = KX.pscale(W0, 1 + eta), KX.pscale(W1, 1 + eta)
    wmin = poly_min_X(g, W0, W1, e_c, e_r)
    ok = wmin >= 0
    Wa = max(eaff_at(W0, W1, e_c, e_lo), eaff_at(W0, W1, e_c, e_hi))
    rec = {"status": "CERTIFIED" if ok else "W_NEGATIVE", "degree": d, "eta": eta, "r_lo": rlo, "W_min": wmin,
           "W_at_atom_max": Wa, "boxes": chk["boxes"], "seconds": round(time.time() - t0, 1), "_W": (W0, W1),
           "e_c": e_c, "whole": whole}
    log(f"  W{'' if whole else '^'} d={d}: {rec['status']} max_E W(a)={float(Wa):.6g} eta={float(eta):.3g} "
        f"boxes={chk['boxes']} lev={chk['max_level']} {rec['seconds']}s")
    return rec


def certify_weight(g: KX.Geom, i: int, e_lo: F, e_hi: F, d: int, Wrec: dict, log=print, mutant: str = "",
                   weight_block=None) -> dict:
    """(V) for Psi = kbar_i over the WEIGHT block Ew = weight_block (default: the check block), with the supersolution
    inequality checked for e in the CHECK block [e_lo, e_hi] (e-affine family, additive lambda W' repair; THEOREM_SRK
    s.7, A1, A3).  mutant (tests only): 'shrink_window' (window narrowed by 1/4) or 'quarter_weight' (Psi/4), both
    invalid, too-small weights."""
    whole = Wrec.get("whole", True)
    w_lo, w_hi = (e_lo, e_hi) if weight_block is None else (F(weight_block[0]), F(weight_block[1]))
    if not (w_lo <= e_lo and e_hi <= w_hi):
        raise ValueError("the check block must lie inside the weight block")
    guard_geometry_block(g, w_lo, w_hi)
    guard_geometry_block(g, e_lo, e_hi)
    _log_call(g, f"certify_weight i={i} d={d} {'whole' if whole else 'taboo'} weight=[{w_lo},{w_hi}] mutant={mutant!r}",
              e_lo, e_hi)
    t0 = time.time()
    e_c = (e_lo + e_hi) / 2
    V0, V1 = _eaff_proposal(g, e_lo, e_hi, d, _kbar_float(g, i, w_lo, w_hi), whole)
    res = eaff_pair(g, V0, V1, e_c, whole)
    if mutant == "quarter_weight":
        rhs = lambda b: EN.box_envelope(g, i, b, w_lo, w_hi) / 4  # noqa: E731  (invalid: Psi/4)
    elif mutant == "shrink_window":
        rhs = lambda b: EN.abs_integral_upper(i, b[1] - b[3] - g.c + w_lo + F(1, 4), g.c - (b[0] - b[2]) + w_hi)  # noqa
    elif mutant == "":
        rhs = lambda b: EN.box_envelope(g, i, b, w_lo, w_hi)  # noqa: E731
    else:
        raise ValueError(f"unknown mutant {mutant!r}")
    chk = cover_check(g, res, rhs, e_lo, e_hi)
    sup_psi = chk["rhs_max"]
    lam = dyadic_up(max(F(0), -chk["r_min"]) + MU * max(F(1), sup_psi), 40)
    W0, W1 = Wrec["_W"]
    V0p, V1p = KX.padd(V0, W0, lam), KX.padd(V1, W1, lam)
    bound = max(eaff_at(V0p, V1p, e_c, e_lo), eaff_at(V0p, V1p, e_c, e_hi))
    raw = max(eaff_at(V0, V1, e_c, e_lo), eaff_at(V0, V1, e_c, e_hi))
    rec = {"status": "CERTIFIED", "i": i, "degree": d, "r_min": chk["r_min"], "lam": lam, "sup_psi": sup_psi,
           "V_at_atom_raw": raw, "Gamma": bound, "boxes": chk["boxes"], "max_level": chk["max_level"],
           "worst_box": chk["worst_box"], "seconds": round(time.time() - t0, 1), "_V": (V0p, V1p), "e_c": e_c,
           "whole": whole, "weight_block": (w_lo, w_hi)}
    log(f"  V[k{i}] d={d}: Gamma={float(bound):.6g} (raw {float(raw):.6g}, lam={float(lam):.3g}, "
        f"r_min={float(chk['r_min']):.3g}) boxes={chk['boxes']} lev={chk['max_level']} {rec['seconds']}s")
    return rec


def run_block(g: KX.Geom, e_lo: F, e_hi: F, indices=(1, 2, 3, 4), ladder=DEFAULT_LADDER, log=print,
              klass: str = "NONTARGET_DECOY", whole: bool = True, weight_block=None) -> dict:
    """Full ladder on one block.  Gamma_i := min over certified rungs (a min of valid bounds is valid)."""
    e_lo, e_hi = F(e_lo), F(e_hi)
    if not (is_dyadic(e_lo) and is_dyadic(e_hi)) or e_hi < e_lo:
        raise ValueError("drift block endpoints must be dyadic with e_lo <= e_hi")
    guard_geometry_block(g, e_lo, e_hi)
    real = (g.h == 5 and g.k == F(1, 2))
    Q.log_execution("impl/srk_certify.py", f"SRK block certificates {g.key()} E=[{e_lo},{e_hi}] i={indices}",
                    klass=klass, drifts=[[e_lo, e_hi]] if real else [],
                    notes="real kernel, out-of-band decoy drift" if real else "synthetic decoy geometry")
    rungs = []
    for d in ladder:
        Wr = certify_W(g, e_lo, e_hi, d, log, whole)
        rung = {"degree": d, "W": Wr, "V": {}}
        if Wr["status"] == "CERTIFIED":
            for i in indices:
                rung["V"][i] = certify_weight(g, i, e_lo, e_hi, d, Wr, log, weight_block=weight_block)
        rungs.append(rung)
    gam = {}
    for i in indices:
        vals = [r["V"][i]["Gamma"] for r in rungs if i in r["V"] and r["V"][i]["status"] == "CERTIFIED"]
        gam[i] = min(vals) if vals else None
    Wa = [r["W"]["W_at_atom_max"] for r in rungs if r["W"]["status"] == "CERTIFIED"]
    return {"geometry": {"h": fstr(g.h), "k": fstr(g.k)}, "block": [fstr(e_lo), fstr(e_hi)], "rungs": rungs,
            "Gamma": gam, "Abar_W": min(Wa) if Wa else None, "whole": whole, "producer": producer_fingerprint()}


def run_cell(g: KX.Geom, cell_lo, cell_hi, indices=(1, 2, 3, 4), ladder=DEFAULT_LADDER, log=print,
             whole: bool = True) -> dict:
    """THEOREM_SRK amendment A3: certificates for one cell = one run_block per check sub-block, each with the WHOLE
    outward-dyadic hull as weight block.  The cell-level Gamma_i is formed only by impl/srk_gate.py."""
    wb, subs = cell_blocks(cell_lo, cell_hi)
    blocks = [run_block(g, lo, hi, indices, ladder, log, whole=whole, weight_block=wb) for lo, hi in subs]
    return {"cell": [fstr(F(cell_lo)), fstr(F(cell_hi))], "weight_block": [fstr(x) for x in wb],
            "sub_blocks": [[fstr(a), fstr(b)] for a, b in subs], "blocks": blocks}


# ------------------------------------------------------------------------------------------ serialization
def _poly_json(P: dict) -> dict:
    return {f"{a},{b}": fstr(v) for (a, b, _), v in sorted(P.items())}


def poly_from_json(d: dict) -> dict:
    out = {}
    for k, v in d.items():
        a, b = (int(t) for t in k.split(","))
        out[(a, b, 0)] = F(v)
    return out


def certificate_json(blk: dict, i: int) -> dict:
    """the minimal, self-contained certificate for Gamma_i on a block (best rung), for independent verification."""
    best = None
    for r in blk["rungs"]:
        v = r["V"].get(i)
        if v and v["status"] == "CERTIFIED" and (best is None or v["Gamma"] < best[1]["Gamma"]):
            best = (r, v)
    if best is None:
        return {"schema": "SRK_CERT/1", "status": "NO_CERTIFIED_RUNG", "i": i}
    r, v = best
    whole = v.get("whole", True)
    K = "K_e" if whole else "K^_e"
    concl = ("sup_E (R_e kbar_i^Ew)(a) <= max(V_{e_lo}(a), V_{e_hi}(a)) = Gamma (THEOREM_SRK Lemma SV')" if whole else
             "sup_E (G^_e kbar_i^Ew)(a) <= max(V_{e_lo}(a), V_{e_hi}(a)) = Gamma (THEOREM_SRK Lemma SV-T)")
    out = {"schema": "SRK_CERT/1", "status": "CERTIFIED", "geometry": blk["geometry"], "block": blk["block"],
           "hermite_index": i, "degree": r["degree"], "kernel": "whole" if whole else "taboo",
           "producer_sha256": blk.get("producer", {}).get("combined"),
           "claim": f"for every e in E (check block), with V_e = V0 + (e - e_c) V1 and W_e = W0 + (e - e_c) W1: "
                    f"V_e >= kbar_i^Ew + {K} V_e and W_e >= 0, W_e >= 1 + {K} W_e on X, Ew = weight_block; hence {concl}",
           "e_c": fstr(v["e_c"]), "weight_block": [fstr(x) for x in v.get("weight_block", (F(blk["block"][0]), F(blk["block"][1])))],
           "V0": _poly_json(v["_V"][0]), "V1": _poly_json(v["_V"][1]),
           "W0": _poly_json(r["W"]["_W"][0]), "W1": _poly_json(r["W"]["_W"][1]),
           "Gamma": fstr(v["Gamma"]), "W_at_atom_max": fstr(r["W"]["W_at_atom_max"]), "lam": fstr(v["lam"]),
           "eta_W": fstr(r["W"]["eta"])}
    body = json.dumps(out, sort_keys=True).encode()
    out["sha256"] = hashlib.sha256(body).hexdigest()
    return out


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--h", default="5")
    ap.add_argument("--k", default="1/2")
    ap.add_argument("--elo", required=True)
    ap.add_argument("--ehi", required=True)
    ap.add_argument("--idx", default="1,2,3,4")
    ap.add_argument("--ladder", default="8,10,12")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    g = KX.Geom(F(a.h), F(a.k))
    blk = run_block(g, F(a.elo), F(a.ehi), tuple(int(x) for x in a.idx.split(",")),
                    tuple(int(x) for x in a.ladder.split(",")))
    certs = {i: certificate_json(blk, i) for i in blk["Gamma"]}
    summary = {"geometry": blk["geometry"], "block": blk["block"],
               "Gamma": {i: (fstr(v) if v is not None else None) for i, v in blk["Gamma"].items()},
               "Abar_W": fstr(blk["Abar_W"]) if blk["Abar_W"] is not None else None,
               "rungs": [{"degree": r["degree"], "W_status": r["W"]["status"],
                          "W_at_atom_max": fstr(r["W"]["W_at_atom_max"]) if "W_at_atom_max" in r["W"] else None,
                          "V": {i: {"Gamma": fstr(v["Gamma"]), "lam": fstr(v["lam"]), "r_min": fstr(v["r_min"]),
                                    "boxes": v["boxes"], "seconds": v["seconds"]} for i, v in r["V"].items()}}
                         for r in blk["rungs"]],
               "certificates": certs}
    Path(a.out).write_text(json.dumps(summary, indent=1, sort_keys=True))
    print("wrote", a.out)
