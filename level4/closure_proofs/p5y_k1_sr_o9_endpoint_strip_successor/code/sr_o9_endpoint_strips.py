"""Endpoint-strip successor: CONTRACT the two x-dependent endpoint strips as certified
panels instead of bounding them by the analytic Task1R sliver envelope.

True operator on patch (alpha, beta):  M(a,b) = int_{L_c+b}^{U_c-a} g dz
                                           = core[L_c, U_c] - I_L(b) - I_U(a)
  I_L = int_{L_c}^{L_c+beta} g dz,  I_U = int_{U_c-alpha}^{U_c} g dz,
  g = Y(q_SR(y,z)) z^s phi(z+e).
Each strip is expanded about its centre (z_c = L_c or U_c, zeta = z - z_c, |zeta| <= H)
with the frozen PanelShared Taylor models (half-width H), a certified phi series
weight times (z_c+zeta)^s, and integrated EXACTLY in zeta:
  int_0^beta zeta^m = beta^(m+1)/(m+1),  int_{-alpha}^0 zeta^m = -(-alpha)^(m+1)/(m+1).
Certified strip errors (charged to the endpoint channel, 'end'):
  e1 raised-degree truncation beyond D:      |c| H^pa H^pb
  e2 Taylor-model error:                     H sup|w| (ex_c + ez_c)
  e3 weight-series remainder:                H r_w sup|Y_poly|
D, Z, precision, degree, candidates, contracts, the 1/250 gate and every other channel
are unchanged. The historical sliver method is untouched (predecessor evidence).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import resource
import sys
import time
from fractions import Fraction as Fr
from math import comb

import sr_o9_candidates as T
import sr_o9_equations as EQ
import sr_o9_patch_certifier as PC
from flint import arb, arb_mat, arb_poly, arb_series

D, Z = PC.D, PC.Z
M_W = Z + 3
NN, DP, ZP = T.CAND_DEGREE + 1, D + 1, Z + 1
ARCH = "task1r-span-p1+strip-contract-v3"


# ---------------------------------------------------------------------------
# Predecessor defect superseded HERE (the committed T2 engine is not edited):
# python-flint evaluates arb ** int through a generic exp/log path, which returns NaN
# for a ball containing 0 even for exponent 1 (zero-centred middle panel of symmetric
# patches), and is not bit-identical to repeated multiplication elsewhere (rigorous
# but radius-inflated). Powers of z_c and of the error weight are therefore built by
# exact repeated multiplication from arb(1). Installed for BOTH the historical sliver
# path and the strip path, so comparisons isolate the endpoint treatment only.
# ---------------------------------------------------------------------------
def ipow(x, k):
    out = arb(1)
    for _ in range(k):
        out = out * x
    return out


class FixedRawShiftDrift:
    __slots__ = ("R", "N0", "shared")

    def __init__(self, shared, N, s, z_c, h):
        zp = [ipow(z_c, t) for t in range(s + 1)]
        Ns = []
        for k in range(2 * shared.Z + 1):
            acc = arb(0)
            for t in range(s + 1):
                acc += arb(comb(s, t)) * zp[s - t] * N[k + t]
            Ns.append(acc)
        Hank = arb_mat(shared.Z + 1, shared.Z + 1)
        for k1 in range(shared.Z + 1):
            for k2 in range(shared.Z + 1):
                Hank[k1, k2] = Ns[k1 + k2]
        self.R = shared.P * Hank
        self.N0 = ipow(z_c.abs_upper() + h.abs_upper(), s) * N[0].abs_upper()
        self.shared = shared


def fixed_raw_moments(N, s, z_c):
    zp = [ipow(z_c, t) for t in range(s + 1)]
    return [sum((arb(comb(s, t)) * zp[s - t] * N[k + t] for t in range(s + 1)), arb(0)) for k in range(2 * Z + 1)]


PC.RawShiftDrift = FixedRawShiftDrift
PC.raw_moments = fixed_raw_moments


def strip_ids(i, j):
    return [f"SRstrip:v3:{ARCH}:64:{i}:{j}:{s}" for s in ("L", "U")]


def _coeffs(s, n):
    out = list(s)
    return out + [arb(0)] * (n - len(out)) if len(out) < n else out[:n]


class StripSide:
    def __init__(self, g, z_c, side, shifts):
        T.require_precision()
        Hh = g["H"]
        self.side, self.H, self.z_c = side, Hh, z_c
        ctxt = (Hh, Hh, D, Z, [Hh ** a for a in range(2 * D + 2)], [Hh ** k for k in range(2 * Z + 2)])
        self.sh = PC.OB.PanelShared(g["p_c"], g["m_c"], z_c, g["b"], ctxt)
        self.av = PC.packet().absvecs_of(self.sh)
        self.Pa = []
        for a in range(DP):
            m = arb_mat(NN, ZP)
            for i in range(NN):
                for k in range(ZP):
                    m[i, k] = self.sh.P[i * DP + a, k]
            self.Pa.append(m)
        self.Q = [[arb_poly([self.sh.Q[j * DP + b, k] for k in range(ZP)]) for b in range(DP)] for j in range(NN)]
        centre = z_c + g["e"]
        two_pi = (arb(2) * arb.pi()).sqrt()
        xs = arb_series([centre, arb(1)], M_W + 2)
        phi_c = _coeffs((-(xs * xs) / arb(2)).exp() / two_pi, M_W + 2)[: M_W + 1]
        xi = arb_series([centre + arb(0, Hh.upper()), arb(1)], M_W + 2)
        r_phi = _coeffs((-(xi * xi) / arb(2)).exp() / two_pi, M_W + 2)[M_W + 1].abs_upper() * Hh ** (M_W + 1)
        wiv = centre + arb(0, Hh.upper())
        pm = ((-(wiv * wiv) / arb(2)).exp() / two_pi).abs_upper()
        zsup = z_c.abs_upper() + Hh.abs_upper()
        self.w, self.rw, self.supw = {}, {}, {}
        for s in shifts:
            self.w[s] = arb_poly(phi_c) * (arb_poly([z_c, arb(1)]) ** s)
            self.rw[s] = r_phi * zsup ** s
            self.supw[s] = pm * zsup ** s
        self.Hp = [Hh ** k for k in range(2 * DP + 2 * ZP + M_W + 8)]
        M = PC.L.softplus_derivative_bound_tight(PC.H.SOFTPLUS_DEGREE + 1)
        from math import factorial
        E = M * ((Hh + Hh) ** (PC.H.SOFTPLUS_DEGREE + 1)) / arb(factorial(PC.H.SOFTPLUS_DEGREE + 1))
        self.P1_E_d = E
        self.P1_PASS = PC.fr_upper(E) <= Fr(1, 10 ** 9)

    def contract(self, cand, s):
        Cm, Ca = arb_mat(NN, NN), arb_mat(NN, NN)
        for i in range(NN):
            for j in range(NN):
                Cm[i, j] = cand[i][j]
                Ca[i, j] = arb(cand[i][j].abs_upper())
        Ct = Cm.transpose()
        out = [[arb(0)] * DP for _ in range(DP)]
        e1 = arb(0)
        w = self.w[s]
        for a in range(DP):
            Sa = Ct * self.Pa[a]
            Sp = [arb_poly([Sa[j, k] for k in range(ZP)]) for j in range(NN)]
            for b in range(DP):
                G = arb_poly([])
                for j in range(NN):
                    G = G + Sp[j] * self.Q[j][b]
                for m, gm in enumerate((G * w).coeffs()):
                    val = gm / arb(m + 1)
                    if self.side == "L":
                        pa, pb = a, b + m + 1
                    else:
                        pa, pb = a + m + 1, b
                        if m % 2:
                            val = -val
                    if pa <= D and pb <= D:
                        out[pa][pb] += val
                    else:
                        e1 += val.abs_upper() * self.Hp[pa] * self.Hp[pb]
        magW, exW, ezW = self.av
        t1, t2x, t2z = Ca * magW, Ca * exW, Ca * ezW
        exc = ezc = supY = arb(0)
        sh = self.sh
        for i in range(NN):
            exc += sh.exV[i] * t1[i, 0] + sh.magV[i] * t2x[i, 0]
            ezc += sh.ezV[i] * t1[i, 0] + sh.magV[i] * t2z[i, 0]
            supY += sh.magV[i] * t1[i, 0]
        e2 = self.H.abs_upper() * self.supw[s] * (exc + ezc)
        e3 = self.H.abs_upper() * self.rw[s] * supY
        return out, e1 + e2 + e3, {"e1": float(e1), "e2": float(e2), "e3": float(e3)}


def certify_patch_strips(i, j, e, cands, *, cand_hashes, C_gate: Fr, nodes):
    T.require_precision()
    t0w, t0c = time.perf_counter(), time.process_time()
    g = PC.patch_geometry(i, j, e)
    pan = PC.panelisation(i, j, g)
    if not pan["P1_PASS"]:
        raise T.T1Refusal(f"P1 fails on ({i},{j})")
    ctxt = PC.context(g, pan["h"])
    exprs = {n: EQ.rhs(n) for n in nodes}
    needed = sorted({k for ex_ in exprs.values() for k in ex_.terms},
                    key=lambda k: (T.BASIS_ORDER.index(k[0]), k[1]))
    stats = {"hits": 0, "misses": 0}
    core = PC.contract_all(g, pan, ctxt, cands, needed, None, stats)
    shifts = sorted({s for _, s in needed})
    sides = {"L": StripSide(g, g["L_c"], "L", shifts), "U": StripSide(g, g["U_c"], "U", shifts)}
    acc, end, parts = {}, {}, {}
    for key in needed:
        c, s = key
        pL, eL, dL = sides["L"].contract(cands[c], s)
        pU, eU, dU = sides["U"].contract(cands[c], s)
        coef = [[core[key][0][a][b] - pL[a][b] - pU[a][b] for b in range(DP)] for a in range(DP)]
        acc[key] = (coef, core[key][1], core[key][2])
        end[key] = eL + eU
        parts[EQ.contract_id(c, s)] = {"L": dL, "U": dU}
    srcs = PC.source_tms(g, ctxt)
    pb = PC.PatchBasis(g, ctxt)
    out = {}
    for n in nodes:
        fh, ex_f = PC.candidate_on_patch(pb, cands[n])
        ch, dmid, _ = PC.assemble(exprs[n], g, acc, end, srcs, fh, ex_f)
        delta = ch["eq"] + ch["trunc"] + ch["tail"] + ch["end"] + ch["int"] + ch["round"]
        if not all(v.is_finite() for v in ch.values()):
            out[n] = {"class": EQ.node_class(n), "NON_FINITE": True, "local_gates_all_pass": False,
                      "end_over_gate": float("inf"), "delta_patch": float("inf"), "dominant_channel": "non_finite",
                      "local_gates": {}}
            continue
        rec = {"class": EQ.node_class(n), "delta_patch_upper": PC.enc(delta), "delta_patch": float(delta),
               "channels": {k: PC.enc(v) for k, v in ch.items()},
               "channels_float": {k: float(v) for k, v in ch.items()},
               "dominant_channel": max(ch, key=lambda k: PC.fr_upper(ch[k])),
               "contracts": sorted(EQ.contract_id(c, s) for c, s in exprs[n].terms),
               "candidate_identity_hash": cand_hashes.get(n)}
        if EQ.local_gate(n):
            rec["local_gates"] = PC.gates(ch, C_gate)
            rec["local_gates_all_pass"] = all(v["PASS"] for v in rec["local_gates"].values())
            rec["end_over_gate"] = float(C_gate * PC.fr_upper(ch["end"]) / Fr(1, 250))
        out[n] = rec
    return {"patch": [i, j], "n_z": pan["n_z"], "strip_ids": strip_ids(i, j),
            "strip_P1": {s: {"E_d_upper": PC.enc(v.P1_E_d), "PASS": v.P1_PASS} for s, v in sides.items()},
            "strip_error_parts": parts, "nodes": out,
            "cpu_s": time.process_time() - t0c, "wall_s": time.perf_counter() - t0w}


# ------------------------------------------------------------ validation
def validate(cell_index, i, j, cand_node="F:0:k0", a_frac=0.6, b_frac=0.8, s=0):
    """Independent check: strip polynomial vs high-resolution float Simpson quadrature."""
    import math
    import numpy as np
    built = T.build_cell_candidates(cell_index, nodes=[cand_node])["scientific"]
    mant = built["candidates"][0]["mantissas"]
    cf = np.array(mant, dtype=float) / 2.0 ** T.SCALE_BITS
    with T.scientific_precision():
        e = T.cell_geometry(T.frozen_cell(cell_index))["e0"]
        g = PC.patch_geometry(i, j, e)
        cand = T.to_arb_matrix(mant)
        res = {}
        for side in ("L", "U"):
            st = StripSide(g, g["L_c"] if side == "L" else g["U_c"], side, [s])
            poly, err, _ = st.contract(cand, s)
            Hf = float(g["H"])
            al, be = a_frac * Hf, b_frac * Hf
            val = sum(float(poly[a][b].mid()) * al ** a * be ** b for a in range(DP) for b in range(DP))
            b_f, pc, mc, Lc, Uc, ef = (float(g[k]) for k in ("b", "p_c", "m_c", "L_c", "U_c", "e"))
            sp = lambda u: u + math.log1p(math.exp(-u)) if u > 0 else math.log1p(math.exp(u))   # noqa: E731

            def gfun(z):
                x = 2 * sp(pc + al + z - 0.5) / b_f - 1
                y = 2 * sp(mc + be - z - 0.5) / b_f - 1
                Tx = np.polynomial.chebyshev.chebvander(np.array([x]), 16)[0]
                Ty = np.polynomial.chebyshev.chebvander(np.array([y]), 16)[0]
                return float(Tx @ cf @ Ty) * z ** s * math.exp(-0.5 * (z + ef) ** 2) / math.sqrt(2 * math.pi)
            lo, hi = (Lc, Lc + be) if side == "L" else (Uc - al, Uc)
            nq = 4000
            hq = (hi - lo) / nq
            quad = (gfun(lo) + gfun(hi) + sum((4 if k % 2 else 2) * gfun(lo + k * hq) for k in range(1, nq))) * hq / 3
            res[side] = {"poly": val, "quad": quad, "abs_diff": abs(val - quad), "cert_err": float(err),
                         "consistent": abs(val - quad) <= float(err) + 1e-11 * max(1.0, abs(quad))}
    return res


def run_case(cell_index, i, j, *, reference=False):
    nodes = [f"F:{r}:k0" for r in range(5)]
    if reference:
        mant, _, _ = T.reference_F0()
        C = Fr(json.loads((T.CP / "p5y_k1_task1r_budget_harness/results/task1r_F0_qualification.json").read_text())["amplification"]["C_at_e"])
        with T.scientific_precision():
            cands = {"F:0:k0": T.to_arb_matrix(mant)}
            e = arb(PC.H.E_NUM) / arb(PC.H.E_DEN)
            new = certify_patch_strips(i, j, e, cands, cand_hashes={}, C_gate=C, nodes=["F:0:k0"])
            old = PC.certify_patch(i, j, e, cands, cand_hashes={}, C_gate=C, nodes=["F:0:k0"], include_images=False)
        hashes = {}
    else:
        built = T.build_cell_candidates(cell_index)["scientific"]
        hashes = {x["node"]: x["identity_hash"] for x in built["candidates"]}
        cell = T.frozen_cell(cell_index)
        C = Fr(cell["C_upper"])
        with T.scientific_precision():
            cands = {x["node"]: T.to_arb_matrix(x["mantissas"]) for x in built["candidates"]}
            e = T.cell_geometry(cell)["e0"]
            old = PC.certify_patch(i, j, e, cands, cand_hashes=hashes, C_gate=C, nodes=nodes, include_images=False)
            new = certify_patch_strips(i, j, e, cands, cand_hashes=hashes, C_gate=C, nodes=nodes)
    timing = {"old_cpu_s": old.pop("cpu_s"), "new_cpu_s": new.pop("cpu_s"), "new_wall_s": new.pop("wall_s")}
    old.pop("wall_s")
    sci = {"case": {"cell": "task1r_reference_e=1/4" if reference else cell_index, "patch": [i, j]},
           "C_upper": f"{C.numerator}/{C.denominator}", "old": old, "new": new}
    return {"scientific": sci, "scientific_hash": hashlib.sha256(T.canonical(sci)).hexdigest(),
            "timing": timing, "peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=("case", "validate"))
    ap.add_argument("--cell", type=int, default=150)
    ap.add_argument("--patch", type=int, nargs=2, default=[17, 11])
    ap.add_argument("--reference", action="store_true")
    ap.add_argument("--out")
    a = ap.parse_args(argv)
    T.check_threads()
    if a.cmd == "validate":
        print(json.dumps(validate(a.cell, *a.patch), indent=1))
        return 0
    r = run_case(a.cell, *a.patch, reference=a.reference)
    if a.out:
        open(a.out, "wb").write(T.canonical(r))
    print(json.dumps({"hash": r["scientific_hash"], "timing": r["timing"], "rss_kib": r["peak_rss_kib"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
