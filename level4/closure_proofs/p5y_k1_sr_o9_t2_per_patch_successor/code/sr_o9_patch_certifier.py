"""T2 generalized SR per-patch certified residual engine (O9 backend).

STATUS: T2_PER_PATCH_CERTIFICATION_ONLY. For one cell drift e0 and one live patch it
certifies, on the task1r-span-p1-v1 panelisation, the local residual hat(X) - rhs(X) of
every frozen SR node (sr_o9_equations), at e = e0, with the Task1R channel structure:
eq, trunc, tail, end, int, round. It performs NO whole-cell aggregation, refinement,
B_cover or obligation closure.

Frozen machinery reused verbatim: harness TM2 / cheb_tm2 / gauss_tm2 / candidate_sup /
panel_moments / p1_rule / geometry conventions (Task1R), opt_backend.PanelShared /
PanelDrift (accepted O1-O3), committed packet contract_O9 / build_Rbig / absvecs_of (O9).
New and exact: raw z^s drift tensors N^(s)_k = sum_t C(s,t) z_c^(s-t) N_(k+t) and the
matching error weight (|z_c|+h)^s N_0; slivers carry sup|z|^s. All scientific
comparisons are exact rationals on outward upper bounds.
"""
from __future__ import annotations

import time
from fractions import Fraction as Fr
from math import comb

import sr_o9_candidates as T
import sr_o9_equations as EQ
import t1_reference as TR

import sys
for _p in (T.CP / "p5y_k1_task1r_budget_harness/code", T.CP / "p5y_k1_sr_backend_cost_audit/code"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))
import harness as H                                                 # noqa: E402
import opt_backend as OB                                            # noqa: E402
import sr_local as L                                                # noqa: E402
from flint import arb, arb_mat                                      # noqa: E402

D, Z = T.FROZEN_D, T.FROZEN_Z
KMAX = 2 * Z + 3
RULE = "task1r-span-p1-v1"
LINES = (("eq", "B_eq"), ("trunc", "B_trunc"), ("tail", "B_tail"), ("end", "B_end"),
         ("int", "B_int"), ("round", "B_round"))
_P = None


def packet():
    global _P
    if _P is None:
        T.require_precision()
        _P, _ = TR.load_cap_packet()
    return _P


def fr_upper(x: arb) -> Fr:
    q = x.upper().fmpq()
    return Fr(int(q.p), int(q.q))


def enc(x: arb):
    """Exact dyadic encoding of an outward upper bound."""
    m, e = x.upper().man_exp()
    return [int(m), int(e)]


# ------------------------------------------------------------------ geometry
def patch_geometry(i: int, j: int, e: arb) -> dict:
    T.require_precision()
    _A, b, c = L.sr_constants()
    geo = L.patch_geometry(i, j, grid=64)
    p_c = (geo["yp"][0] + geo["yp"][1]) / arb(2)
    m_c = (geo["ym"][0] + geo["ym"][1]) / arb(2)
    Hh = (geo["yp"][1] - geo["yp"][0]) / arb(2)
    U_c, L_c = c - p_c, m_c - c
    return dict(b=b, c=c, e=e, geo=geo, p_c=p_c, m_c=m_c, H=Hh, U_c=U_c, L_c=L_c, span=U_c - L_c)


def panelisation(i: int, j: int, g: dict) -> dict:
    p1 = H.p1_rule(g["H"], g["span"])
    n = p1["n_panels"]
    h = g["span"] / (arb(2) * arb(n))
    return {"p1": p1, "n_z": n, "h": h, "P1_PASS": p1["PASS"],
            "panel_ids": [f"SRpanel:v2:{RULE}:64:{i}:{j}:{k}/{n}" for k in range(n)],
            "sliver_ids": [f"SRsliver:v2:{RULE}:64:{i}:{j}:{s}" for s in ("L", "U")]}


def context(g, h):
    Hh = g["H"]
    return (Hh, h, D, Z, [Hh ** a for a in range(2 * D + 2)], [h ** k for k in range(2 * Z + 2)])


# --------------------------------------------------------- raw-shift drift
class RawShiftDrift:
    __slots__ = ("R", "N0", "shared")

    def __init__(self, shared, N, s, z_c, h):
        Ns = []
        for k in range(2 * shared.Z + 1):
            acc = arb(0)
            for t in range(s + 1):
                acc += arb(comb(s, t)) * z_c ** (s - t) * N[k + t]
            Ns.append(acc)
        Hank = arb_mat(shared.Z + 1, shared.Z + 1)
        for k1 in range(shared.Z + 1):
            for k2 in range(shared.Z + 1):
                Hank[k1, k2] = Ns[k1 + k2]
        self.R = shared.P * Hank
        self.N0 = (z_c.abs_upper() + h.abs_upper()) ** s * N[0].abs_upper()
        self.shared = shared


def raw_moments(N, s, z_c):
    return [sum((arb(comb(s, t)) * z_c ** (s - t) * N[k + t] for t in range(s + 1)), arb(0))
            for k in range(2 * Z + 1)]


# ---------------------------------------------------------------- contracts
def contract_all(g, pan, ctxt, cands, needed, shared_cache, stats):
    """Accumulate every needed (cand, s) contract over the panels, ascending kp."""
    P = packet()
    acc = {k: [[[arb(0)] * (D + 1) for _ in range(D + 1)], arb(0), arb(0)] for k in needed}
    shifts = sorted({s for _, s in needed})
    evals = 0
    for kp in range(pan["n_z"]):
        h = pan["h"]
        z_lo = g["L_c"] + arb(2) * h * arb(kp)
        z_hi = z_lo + arb(2) * h
        z_c = (z_lo + z_hi) / arb(2)
        key = (pan["panel_ids"][kp], D, Z)
        if shared_cache is not None and key in shared_cache:
            sh = shared_cache[key]
            stats["hits"] += 1
        else:
            sh = OB.PanelShared(g["p_c"], g["m_c"], z_c, g["b"], ctxt)
            stats["misses"] += 1
            if shared_cache is not None:
                shared_cache[key] = sh
        N = H.panel_moments(z_lo, z_hi, z_c, g["e"], KMAX, h)
        av = P.absvecs_of(sh)
        for s in shifts:
            pd = OB.PanelDrift(sh, N) if s == 0 else RawShiftDrift(sh, N, s, z_c, h)
            Rb = P.build_Rbig(pd)
            for (c, ss) in needed:
                if ss != s:
                    continue
                coef, ex, ez = P.contract_O9(pd, cands[c], Rb, av)
                A = acc[(c, s)]
                for a in range(D + 1):
                    for bq in range(D + 1):
                        A[0][a][bq] += coef[a][bq]
                A[1] += ex
                A[2] += ez
                evals += 1
    stats["contract_evaluations"] = stats.get("contract_evaluations", 0) + evals
    return acc


def sliver_pair(g, cand, s):
    """Task1R endpoint slivers (verbatim arithmetic) with the raw-weight factor sup|z|^s."""
    Hh, b, e, half = g["H"], g["b"], g["e"], arb(1) / arb(2)

    def one(z_mid):
        ziv = z_mid + arb(0, Hh.upper())
        ap = L.softplus(g["p_c"] + arb(0, Hh.upper()) + ziv - half)
        am = L.softplus(g["m_c"] + arb(0, Hh.upper()) - ziv - half)
        t_lo = min((arb(2) * ap / b - arb(1)).lower(), (arb(2) * am / b - arb(1)).lower())
        t_hi = max((arb(2) * ap / b - arb(1)).upper(), (arb(2) * am / b - arb(1)).upper())
        w = ziv + e
        two_pi = arb(2) * arb.pi()
        pm = ((-(w * w) / arb(2)).exp() / two_pi.sqrt()).abs_upper()
        v = Hh.abs_upper() * H.candidate_sup(cand, arb(t_lo), arb(t_hi)) * pm
        return v if s == 0 else v * ziv.abs_upper() ** s
    return one(g["U_c"]) + one(g["L_c"])


# -------------------------------------------------------- candidate on patch
class PatchBasis:
    def __init__(self, g, ctxt):
        tp = H.TM2.zero(ctxt)
        tp.c[0][0] = arb(2) * g["p_c"] / g["b"] - arb(1)
        tp.c[1][0] = arb(2) / g["b"]
        tmn = H.TM2.zero(ctxt)
        tmn.c[0][0] = arb(2) * g["m_c"] / g["b"] - arb(1)
        tmn.c[1][0] = arb(2) / g["b"]
        self.TVx, self.TWx, self.ctxt = H.cheb_tm2(tp, T.CAND_DEGREE), H.cheb_tm2(tmn, T.CAND_DEGREE), ctxt


def candidate_on_patch(pb, cand):
    fh = [[arb(0)] * (D + 1) for _ in range(D + 1)]
    ex_f = arb(0)
    for i in range(T.CAND_DEGREE + 1):
        inner = H.TM2.zero(pb.ctxt)
        for j in range(T.CAND_DEGREE + 1):
            if not cand[i][j].is_zero():
                inner = inner + pb.TWx[j].scaled(cand[i][j])
        P_, Q = pb.TVx[i], inner
        ex_f += P_.mag() * Q.ex + Q.mag() * P_.ex
        for a in range(D + 1):
            if P_.c[a][0].is_zero():
                continue
            for bq in range(D + 1):
                fh[a][bq] += P_.c[a][0] * Q.c[bq][0]
    return fh, ex_f


def source_tms(g, ctxt):
    up = H.gauss_tm2(g["U_c"] + g["e"], ctxt, -1)
    lo = H.gauss_tm2(g["L_c"] + g["e"], ctxt, +1)
    Ua = H.TM2.zero(ctxt); Ua.c[0][0] = g["U_c"] + g["e"]; Ua.c[1][0] = arb(-1)
    Lb = H.TM2.zero(ctxt); Lb.c[0][0] = g["L_c"] + g["e"]; Lb.c[1][0] = arb(1)
    U2 = Ua * Ua; L2 = Lb * Lb
    return {"phiU": ("a", up), "phiL": ("b", lo), "UphiU": ("a", Ua * up), "LphiL": ("b", Lb * lo),
            "U2m1phiU": ("a", U2 * up - up), "L2m1phiL": ("b", L2 * lo - lo)}


def peval(p, e):
    acc = arb(0)
    for k, v in sorted(p.items()):
        acc += (arb(v.numerator) / arb(v.denominator)) * e ** k
    return acc


def _is_one(p):
    return p == {0: Fr(1)}


def _is_minus_one(p):
    return p == {0: Fr(-1)}


# --------------------------------------------------------------- residuals
def assemble(ex_: EQ.Expr, g, acc, sliv, srcs, fh=None, ex_f=None):
    """Residual hat - rhs (or the image rhs when fh is None) with every channel."""
    e = g["e"]
    Tm = [[arb(0)] * (D + 1) for _ in range(D + 1)]
    ex_t = ez_t = end = arb(0)
    for key in sorted(ex_.terms, key=lambda k: (T.BASIS_ORDER.index(k[0]), k[1])):
        p = ex_.terms[key]
        coef, ex, ez = acc[key]
        if _is_one(p):
            for a in range(D + 1):
                for bq in range(D + 1):
                    Tm[a][bq] += coef[a][bq]
            ex_t += ex; ez_t += ez; end += sliv[key]
        else:
            c = peval(p, e)
            ca = c.abs_upper()
            for a in range(D + 1):
                for bq in range(D + 1):
                    Tm[a][bq] += c * coef[a][bq]
            ex_t += ca * ex; ez_t += ca * ez; end += ca * sliv[key]
    s0 = [[arb(0)] * (D + 1) for _ in range(D + 1)]
    ex_s = ez_s = arb(0)
    for kind, p in ex_.src:
        axis, tm = srcs[kind]
        for a in range(D + 1):
            if _is_one(p):
                v = tm.c[a][0]
            elif _is_minus_one(p):
                v = None
            else:
                v = peval(p, e) * tm.c[a][0]
            if axis == "a":
                if v is None:
                    s0[a][0] -= tm.c[a][0]
                else:
                    s0[a][0] += v
            else:
                if v is None:
                    s0[0][a] -= tm.c[a][0]
                else:
                    s0[0][a] += v
        if _is_one(p) or _is_minus_one(p):
            ex_s += tm.ex
            ez_s += tm.ez
        else:
            pa = peval(p, e).abs_upper()
            ex_s += pa * tm.ex
            ez_s += pa * tm.ez
    if ex_.const:
        s0[0][0] += peval(ex_.const, e)
    Hp = [g["H"] ** k for k in range(2 * D + 2)]
    eq = itv = arb(0)
    dmid = [[arb(0)] * (D + 1) for _ in range(D + 1)]
    for a in range(D + 1):
        for bq in range(D + 1):
            d = (fh[a][bq] - Tm[a][bq] - s0[a][bq]) if fh is not None else (Tm[a][bq] + s0[a][bq])
            dmid[a][bq] = d
            eq += arb(d.mid()).abs_upper() * Hp[a + bq]
            itv += arb(d.rad()) * Hp[a + bq]
    trunc = (ex_t + ex_f + ex_s) if fh is not None else (ex_t + ex_s)
    tail = ez_t + ez_s
    ch = {"eq": eq.abs_upper(), "trunc": trunc.abs_upper(), "tail": tail.abs_upper(),
          "end": end, "int": itv.abs_upper(), "round": arb(0)}
    return ch, dmid, (ex_t, ex_f, ex_s, ez_t, end)


def gates(ch, C: Fr) -> dict:
    nested = T.spec.NESTED_CANDIDATE
    out = {}
    for c, line in LINES:
        allow = Fr(nested[line]) / C
        v = fr_upper(ch[c])
        out[c] = {"line": line, "allowance": f"{allow.numerator}/{allow.denominator}",
                  "value_upper": enc(ch[c]), "PASS": v <= allow}
    return out


def certify_patch(i, j, e, cands, *, cand_hashes, C_gate: Fr, nodes=None, shared_cache=None,
                  include_images=True):
    """Certify the frozen SR nodes on patch (i, j) at drift e. O9 evidence mode."""
    T.require_precision()
    t0w, t0c = time.perf_counter(), time.process_time()
    stats = {"hits": 0, "misses": 0}
    g = patch_geometry(i, j, e)
    pan = panelisation(i, j, g)
    if not pan["P1_PASS"]:
        raise T.T1Refusal(f"P1 check failed on patch ({i},{j}); executable universe violated")
    ctxt = context(g, pan["h"])
    want = list(EQ.RESIDUAL_NODES if nodes is None else nodes)
    imgs = list(EQ.IMAGE_NODES) if include_images and nodes is None else []
    exprs = {n: EQ.rhs(n) for n in want}
    exprs.update({n: EQ.image(n) for n in imgs})
    needed = sorted({k for ex_ in exprs.values() for k in ex_.terms},
                    key=lambda k: (T.BASIS_ORDER.index(k[0]), k[1]))
    acc = contract_all(g, pan, ctxt, cands, needed, shared_cache, stats)
    sliv = {k: sliver_pair(g, cands[k[0]], k[1]) for k in needed}
    srcs = source_tms(g, ctxt)
    pb = PatchBasis(g, ctxt)
    out = {}
    for n in want + imgs:
        if n in imgs:
            ch, dmid, parts = assemble(exprs[n], g, acc, sliv, srcs)
            width = ch["trunc"] + ch["tail"] + ch["end"] + ch["int"]
            rec = {"class": "OPERATOR_IMAGE", "enclosure_width_upper": enc(width),
                   "enclosure_width": float(width),
                   "channels": {k: enc(v) for k, v in ch.items() if k != "eq"}}
        else:
            fh, ex_f = candidate_on_patch(pb, cands[n])
            ch, dmid, parts = assemble(exprs[n], g, acc, sliv, srcs, fh, ex_f)
            delta = ch["eq"] + ch["trunc"] + ch["tail"] + ch["end"] + ch["int"] + ch["round"]
            dom = max(ch, key=lambda k: fr_upper(ch[k]))
            rec = {"class": EQ.node_class(n), "delta_patch_upper": enc(delta), "delta_patch": float(delta),
                   "channels": {k: enc(v) for k, v in ch.items()},
                   "channels_float": {k: float(v) for k, v in ch.items()},
                   "dominant_channel": dom, "candidate_identity_hash": cand_hashes.get(n)}
            if EQ.local_gate(n):
                rec["local_gates"] = gates(ch, C_gate)
                rec["local_gates_all_pass"] = all(v["PASS"] for v in rec["local_gates"].values())
        rec["contracts"] = sorted(EQ.contract_id(c, s) for c, s in exprs[n].terms)
        rec["dependency_identity_hashes"] = {c: cand_hashes.get(c) for c, _ in exprs[n].terms}
        rec["finite_nonnegative"] = all(fr_upper(v) >= 0 for v in ch.values()) and all(
            v.is_finite() for v in ch.values())
        out[n] = rec
    return {"patch": [i, j], "n_z": pan["n_z"], "panel_ids_first_last": [pan["panel_ids"][0], pan["panel_ids"][-1]],
            "sliver_ids": pan["sliver_ids"], "P1_headroom_rel": pan["p1"]["HEADROOM_REL"],
            "contracts_evaluated": sorted(EQ.contract_id(c, s) for c, s in needed),
            "contract_evaluations": stats["contract_evaluations"],
            "cache": {"hits": stats["hits"], "misses": stats["misses"]},
            "nodes": out, "cpu_s": time.process_time() - t0c, "wall_s": time.perf_counter() - t0w}


# ---------------------------------------------------- Task1R baseline (A4)
def task1r_report(cand, C_SR: float, mode: str, cinfo: dict) -> dict:
    """F_0 at the Task1R reference (patch (17,11), e = 1/4): the generic residual
    assembler with the contraction supplied by the frozen harness.run_panels (baseline,
    A4) or by the O9 path (A5.3); output fields as frozen harness.certify."""
    T.require_precision()
    e = arb(H.E_NUM) / arb(H.E_DEN)
    g = patch_geometry(*H.PATCH, e)
    pan = panelisation(*H.PATCH, g)
    key = ("F:0:k0", 0)
    if mode == "task1r_baseline":
        coef, ex, ez, h, ctxt = H.run_panels(cand, D, Z, dict(g, **{"H": g["H"]}), pan["p1"])
    elif mode == "o9":
        ctxt = context(g, pan["h"])
        stats = {"hits": 0, "misses": 0}
        coef, ex, ez = contract_all(g, pan, ctxt, {"F:0:k0": cand}, [key], None, stats)[key]
    else:
        raise ValueError(mode)
    acc = {key: (coef, ex, ez)}
    sliv = {key: sliver_pair(g, cand, 0)}
    fh, ex_f = candidate_on_patch(PatchBasis(g, ctxt), cand)
    ch, dmid, _ = assemble(EQ.rhs("F:0:k0"), g, acc, sliv, source_tms(g, ctxt), fh, ex_f)
    comp = {"equation_defect_polynomial": float(ch["eq"]), "truncation_patch_local": float(ch["trunc"]),
            "tail_zeta_and_moments": float(ch["tail"]), "endpoint_slivers": float(ch["end"]),
            "interval_arithmetic": float(ch["int"]), "rounding_exact_dyadic": 0.0}
    delta = sum(comp.values())
    bud = H.budget()["absolute"]
    lines = {"equation_defect_polynomial": "B_eq", "truncation_patch_local": "B_trunc",
             "tail_zeta_and_moments": "B_tail", "endpoint_slivers": "B_end",
             "interval_arithmetic": "B_int", "rounding_exact_dyadic": "B_round"}
    per = {}
    for k, v in comp.items():
        allow = bud[lines[k]] / C_SR
        per[k] = {"value": v, "budget_line": lines[k], "allowance_delta_units": allow,
                  "fraction_of_line": v / allow if allow > 0 else float("inf"), "PASS": v <= allow}
    return {"delta_F0": delta, "components": comp, "per_line": per,
            "all_lines_pass": all(x["PASS"] for x in per.values()),
            "defect_constant_term": float(dmid[0][0].mid()), "defect_constant_radius": float(dmid[0][0].rad()),
            "n_panels": pan["n_z"], "exact_channels": {k: enc(v) for k, v in ch.items()},
            "exact_gates": gates(ch, Fr(C_SR))}
