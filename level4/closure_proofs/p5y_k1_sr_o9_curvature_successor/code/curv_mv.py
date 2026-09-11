"""Curvature certification successor: mean-value whole-cell residual extension for the SR DAG.

Frozen construction reused (p5y_k1_cover_ledger_implementation/code/cusum_layer2.py, "WHY delta_cell IS NOT COMPUTED
BY SUBSTITUTING AN INTERVAL e"): every candidate is a state-only dyadic polynomial, constant in e, so for every DAG
node X and every e in the PARENT cell (|e - e0| <= rho)
    r_X(x;e) - r_X(x;e0) = int_{e0}^{e} d_s r_X(x;s) ds   =>   sup_{x, e in cell} |r_X(x;e)| <= delta_mid(X) + rho*Env_X
where d_e r_X contains only e-differentiated OPERATORS applied to fixed candidates, plus the e-derivatives of the exact
const:1 and closed-form source terms. So Env_X = sum |b| * N(T^(i+1)) * sup|c_hat| + (exact-term derivatives), with
certified cell-uniform operator norms (closed-form Gaussian integrals, split at the Hermite roots) and certified candidate
sups (sum |Chebyshev coefficients|). delta_mid(X) is the T3 midpoint certificate over all 3,994 patches.

The new delta_cell = min(T3 interval-e delta_cell, delta_mid + rho*Env). Both are valid, so the min is valid. Parent
cell, e0, rho, STYLE_1, thresholds, candidates, contracts and obligations are unchanged. The frozen t4_cell and
t5_obligations then run unchanged on the resulting T3 view.
"""
from __future__ import annotations

import copy
import hashlib
import json
import sys
from fractions import Fraction as Fr
from pathlib import Path

import sr_o9_candidates as T
import sr_o9_equations as EQ
import sr_o9_patch_certifier as PC
import sr_o9_endpoint_strips as ES
import t2_final_certifier as FC
import t4_cell as T4
from flint import arb

NS = Path(__file__).resolve().parents[1]
EV3 = T.CP / "p5y_k1_sr_o9_t345_successor/evidence"
SRC_ORDER = {"phiU": 0, "phiL": 0, "UphiU": 1, "LphiL": 1, "U2m1phiU": 2, "L2m1phiL": 2}


def phi(w):
    return (-(w * w) / arb(2)).exp() / (arb(2) * arb.pi()).sqrt()


def He(n, w):
    if n == 0:
        return arb(1)
    a, b = arb(1), w
    for k in range(1, n):
        a, b = b, w * b - arb(k) * a
    return b


def roots(n):
    s3, s6 = arb(3).sqrt(), arb(6).sqrt()
    return {0: [], 1: [arb(0)], 2: [arb(-1), arb(1)], 3: [-s3, arb(0), s3],
            4: [-(arb(3) + s6).sqrt(), -(arb(3) - s6).sqrt(), (arb(3) - s6).sqrt(), (arb(3) + s6).sqrt()]}[n]


def A(n, a, b):
    """int_a^b |He_n(w)| phi(w) dw, exact antiderivatives (-He_{n-1} phi, or Phi for n=0) between Hermite roots."""
    a, b = arb(a.lower()), arb(b.upper())                      # widen outward: a bigger window only enlarges the bound
    if n == 0:
        return (PC.L.gaussian_cdf(b) - PC.L.gaussian_cdf(a)).abs_upper()
    pts = [a]
    for r in roots(n):
        if r.upper() < a.lower() or r.lower() > b.upper():
            continue
        if not (r.lower() > a.upper() and r.upper() < b.lower()):
            raise ArithmeticError("Hermite root straddles the window endpoint")
        pts.append(r)
    pts.append(b)
    F = lambda w: -He(n - 1, w) * phi(w)                       # noqa: E731
    return sum(((F(hi) - F(lo)).abs_upper() for lo, hi in zip(pts[:-1], pts[1:])), arb(0))


def sup_He_phi(n):
    """Rigorous sup_w |He_n(w) phi(w)|: ball cover of [-12,12] (radius 1/200) plus the tail bound for |w| >= 12."""
    best = arb(0)
    for k in range(-2400, 2400):
        w = arb(2 * k + 1) / arb(400) + arb(0, (arb(1) / arb(400)).upper())
        v = (He(n, w) * phi(w)).abs_upper()
        if v > best:
            best = v
    tail = (arb(13) ** n) * phi(arb(12))
    return best if best > tail else tail


def norms(e_lo, e_hi):
    _A, _b, c = PC.L.sr_constants()
    a, b = -c + e_lo, c + e_hi
    An = {n: A(n, a, b) for n in range(5)}
    E = arb(max(e_lo.abs_upper(), e_hi.abs_upper()).upper())
    NK = {i: An[i] for i in range(4)}
    NKz = {i: An[i + 1] + (arb(i) * An[i - 1] if i >= 1 else arb(0)) + E * An[i] for i in range(4)}
    # The frozen SR-lane kz (|z| <= |w|+|e|) and kz1 (|z w| <= w^2+|e||w|) are pointwise-valid bounds, evaluated at the
    # cell ball (inclusion isotone). Take the tighter of the two valid values. Its kz2 rests on a pointwise-false
    # inequality, so it is NOT used here; K_z^(2) and K_z^(3) use the closed forms above only.
    sys.path.insert(0, str(T.CP / "p5y_k1_sr_qualification/code"))
    import sr_operators as OPS
    e_ball = (e_lo + e_hi) / arb(2) + arb(0, ((e_hi - e_lo) / arb(2)).abs_upper())
    o = OPS.one_step_norms(e_ball)
    src = {}
    for i, key in ((0, "kz"), (1, "kz1")):
        v = arb(o[key].abs_upper().upper())
        src[i] = "sr_operators" if v.upper() < NKz[i].upper() else "closed_form"
        if v.upper() < NKz[i].upper():
            NKz[i] = v
    return {"K": NK, "Kz": NKz, "window": (a, b), "E": E, "kz_source": src}


def struct_full():
    orig = EQ.op
    EQ.op = lambda kind, i, cand: EQ.Expr({(cand, (kind, i)): {0: Fr(1)}})
    try:
        out = {}
        for n in FC.NODES:
            ex = EQ.image(n) if n in EQ.IMAGE_NODES else EQ.rhs(n)
            out[n] = ({(c, k[0], k[1]): dict(p) for (c, k), p in ex.terms.items()}, dict(ex.const), list(ex.src))
    finally:
        EQ.op = orig
    return out


def psup(p, e):
    acc = arb(0)
    for k, v in p.items():
        acc += (arb(v.numerator) / arb(v.denominator)) * ES.ipow(e, k) if k else arb(v.numerator) / arb(v.denominator)
    return acc.abs_upper()


def dpoly(p):
    return {k - 1: v * k for k, v in p.items() if k >= 1}


def envelopes(struct, sups, nrm, e_ball, SV):
    env = {}
    for n, (terms, const, src) in struct.items():
        tot = arb(0)
        for (c, kind, i), p in terms.items():
            S = arb(1) if c == "const:1" else sups[c]
            dp = dpoly(p)
            if dp:
                tot += psup(dp, e_ball) * nrm[kind][i] * S
            tot += psup(p, e_ball) * nrm[kind][i + 1] * S
        dc = dpoly(const)
        if dc:
            tot += psup(dc, e_ball)
        for kind, p in src:
            q = SRC_ORDER[kind]
            dp = dpoly(p)
            if dp:
                tot += psup(dp, e_ball) * SV[q]
            tot += psup(p, e_ball) * SV[q + 1]
        env[n] = arb(tot.abs_upper().upper())
    return env


def fr(x):
    return PC.fr_upper(x)


def build_view(cell_index, SV=None):
    t3 = json.loads((EV3 / f"t3/t3_c{cell_index}.json").read_text())
    built = T.build_cell_candidates(cell_index)["scientific"]
    mant = {x["node"]: x["mantissas"] for x in built["candidates"]}
    struct = struct_full()
    with T.scientific_precision():
        g = T.cell_geometry(T.frozen_cell(cell_index))
        e0, rho = g["e0"], g["rho"]
        e_ball = e0 + arb(0, rho.abs_upper())
        SV = SV or {q: sup_He_phi(q) for q in range(4)}
        nrm = norms(g["left"], g["right"])
        sups = {n: T4.cand_sup(m) for n, m in mant.items()}
        env = envelopes(struct, sups, nrm, e_ball, SV)
        rho_u = arb(rho.abs_upper())
        view = copy.deepcopy(t3)
        comp = {}
        for n in FC.NODES:
            dcell = t3["delta"]["cell"][n]
            if n in EQ.IMAGE_NODES:
                mid_rec = t3["x0_images"]["mid"][n]
                old = T4.img_x0(t3["x0_images"]["cell"][n])
                mv = T4.img_x0(mid_rec) + arb(0, (rho_u * env[n]).upper())
                pick = mv if mv.rad() < old.rad() else old
                view["x0_images"]["cell"][n] = {"mid": T4.__dict__.get("_enc", None) or _enc(arb(pick.mid())),
                                                "rad": _enc(arb(pick.rad()))}
                comp[n] = {"kind": "image", "Env": float(env[n]), "x0_rad_interval_e": float(old.rad()),
                           "x0_rad_mean_value": float(mv.rad()), "chosen": "mean_value" if pick is mv else "interval_e"}
                continue
            dmid = Fr(t3["delta"]["mid"][n]["delta"])
            dint = Fr(dcell["delta"])
            dmv = fr(T4.exact(dmid) + rho_u * env[n])
            new = min(dint, dmv)
            view["delta"]["cell"][n] = dict(dcell, delta=f"{new.numerator}/{new.denominator}", delta_float=float(new),
                                            curvature_successor_source=("mean_value" if dmv < dint else "interval_e"))
            comp[n] = {"kind": "residual", "delta_mid": float(dmid), "Env": float(env[n]), "rho_Env": float(rho_u * env[n]),
                       "delta_cell_mean_value": float(dmv), "delta_cell_interval_e": float(dint), "delta_cell_new": float(new),
                       "chosen": "mean_value" if dmv < dint else "interval_e"}
    view["curvature_successor"] = {
        "construction": "delta_cell = min(interval-e, delta_mid + rho*Env) (frozen cusum_layer2 mean-value extension)",
        "parent_t3_record_sha256": t3["t3_record_sha256"], "components": comp,
        "norms": {k: {str(i): float(v) for i, v in d.items()} for k, d in nrm.items() if k in ("K", "Kz")},
        "operator_window": [float(nrm["window"][0]), float(nrm["window"][1])], "e_abs_max": float(nrm["E"]),
        "sup_He_phi": {str(q): float(v) for q, v in SV.items()}, "rho_upper": float(rho_u)}
    body = {k: v for k, v in view.items() if k != "t3_record_sha256"}
    view["t3_record_sha256"] = hashlib.sha256(T4.canonical(body)).hexdigest()
    return view, SV


def _enc(x):
    m, e = x.man_exp()
    return [int(m), int(e)]


def run(cell_index, outdir, SV=None):
    import t5_obligations as T5
    out = Path(outdir)
    out.mkdir(parents=True, exist_ok=True)
    view, SV = build_view(cell_index, SV)
    (out / f"t3view_c{cell_index}.json").write_bytes(T4.canonical(view))
    r4 = T4.t4(view)
    (out / f"t4_c{cell_index}.json").write_bytes(T4.canonical(r4))
    ev = {"t3view_record_sha256": view["t3_record_sha256"], "t4_record_sha256": r4["t4_record_sha256"],
          "parent_t3_record_sha256": view["curvature_successor"]["parent_t3_record_sha256"]}
    r5 = T5.obligations(view, r4, ev)
    (out / f"t5_c{cell_index}.json").write_bytes(T4.canonical(r5))
    return view, r4, r5


def main():
    import time
    import resource
    cell, outdir = int(sys.argv[1]), sys.argv[2]
    T.check_threads()
    t0 = time.process_time()
    view, r4, r5 = run(cell, outdir)
    comp = view["curvature_successor"]["components"]
    print(json.dumps({"cell": cell, "status": r4["all_m_status"], "B_cover_ratio": r4["B_cover_ratio"],
                      "T5": [r5["pass_count"], r5["status"]],
                      "mean_value_chosen": sum(1 for v in comp.values() if v["chosen"] == "mean_value"),
                      "F_k2_delta_cell": {n: [comp[n]["delta_cell_interval_e"], comp[n]["delta_cell_new"]] for n in comp if n.startswith("F:") and n.endswith("k2")},
                      "cpu_s": time.process_time() - t0, "rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                      "t4_sha": r4["t4_record_sha256"]}, indent=1))


if __name__ == "__main__":
    main()
