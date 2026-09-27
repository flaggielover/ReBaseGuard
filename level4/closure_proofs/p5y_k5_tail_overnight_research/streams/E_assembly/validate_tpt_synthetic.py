"""V1/V2/V4 for theorem TPT on exact finite-state drift families (no CUSUM cell is touched).

For each fixture (random sub-Markov drift family, several sources r < m, one cell with x_lo > 0):
  1. build the theorem-TC pipeline with PERTURBED candidates F^, D^, H^ (and G^ = 0 or ~F'''),
     exact midpoint residual norms f_F..f_G, certified whole-cell k_i, sigma4 and C >= sup||R_e||,
     Lemma-G atom constants, Env4 from (P3);
  2. check Lemma TC-P pointwise against the exact F_r''(t)(a) on a rational grid;
  3. check the truth  sup_C g  <=  g_hi + P_tpt <= g_hi + P_c5t <= g_hi + P_frozen, with sup_C g
     bounded ABOVE rigorously (grid max + h/2 * certified sup|g'|);
  4. negative control: a profile shrunk below the truth must be DETECTED by step 2.
Writes validation/TPT_SYNTHETIC.json.
"""
from __future__ import annotations

import json
import sys
import time
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve().parent
NS = HERE.parents[1]
sys.path.insert(0, str(NS / "code"))
sys.path.insert(0, str(HERE))
import ov_fixtures as X  # noqa: E402
import ov_quarantine as Q  # noqa: E402
import tpt  # noqa: E402

Q.install_import_guard()


def poly_abs_bound(c: list, emax: F) -> F:
    return sum((abs(a) * emax ** d for d, a in enumerate(c)), F(0))


def sup_Ki(fam: X.DriftFamily, i: int, emax: F) -> F:
    return max(sum(poly_abs_bound(X.poly_deriv(p, i), emax) for p in row) for row in fam.kp)


def sup_Si(spolys: list, i: int, emax: F) -> F:
    return max(poly_abs_bound(X.poly_deriv(p, i), emax) for p in spolys)


def sup_R_bound(fam: X.DriftFamily, e0: F, rho: F) -> F:
    """certified C >= sup_{|e-e0|<=rho} ||R_e||:  ||R_e|| <= ||R0|| / (1 - ||R0|| * d), d >= ||K(e)-K(e0)||."""
    R0 = X.op_norm(fam.R(e0))
    emax = e0 + rho
    d = F(0)
    for row in fam.kp:
        tot = F(0)
        for p in row:
            # |p(e) - p(e0)| <= sum_k |c_k| |e^k - e0^k| <= sum_k |c_k| k emax^(k-1) rho
            tot += sum((abs(c) * k * emax ** (k - 1) * rho for k, c in enumerate(p) if k >= 1), F(0))
        d = max(d, tot)
    if R0 * d >= 1:
        raise ValueError("Neumann bound fails; shrink rho")
    return R0 / (1 - R0 * d)


def build_fixture(seed: int, n: int, m: int, e0: F, rho: F, pert: F, G_mode: str) -> tuple:
    import random
    rng = random.Random(10_000 + seed)
    fam = X.random_family(n, seed=seed, e_range=(F(0), e0 + rho))
    # m sources: each a random polynomial source vector
    sources = [[[F(rng.randint(-10, 10), 10) for _ in range(4)] for _ in range(n)] for _ in range(m)]
    emax = e0 + rho
    k = [sup_Ki(fam, i, emax) for i in range(5)]
    C = sup_R_bound(fam, e0, rho)
    A0, A1, A2 = C, k[1] * C * C, k[2] * C * C + 2 * k[1] ** 2 * C ** 3
    Ks = [fam.K(e0, i) for i in range(4)]
    I_K = X.mat_add(X.mat_id(n), Ks[0], F(-1))
    terms, truth = [], []
    for r, sp in enumerate(sources):
        famr = X.DriftFamily(fam.kp, sp, (fam.e_lo, fam.e_hi))
        Fd = famr.F_derivs(e0, 3)
        noise = lambda: [pert * F(rng.randint(-100, 100), 100) for _ in range(n)]  # noqa: E731
        Fh = X.vec_add(Fd[0], noise())
        Dh = X.vec_add(Fd[1], noise())
        Hh = X.vec_add(Fd[2], noise())
        Gh = [F(0)] * n if G_mode == "zero" else X.vec_add(Fd[3], noise())
        Sd = [famr.S(e0, i) for i in range(4)]
        phi0 = X.vec_add(Sd[0], X.mat_vec(I_K, Fh), F(-1))
        phi1 = X.vec_add(X.vec_add(Sd[1], X.mat_vec(Ks[1], Fh)), X.mat_vec(I_K, Dh), F(-1))
        phi2 = X.vec_add(X.vec_add(X.vec_add(Sd[2], X.mat_vec(Ks[2], Fh)), X.mat_vec(Ks[1], Dh), F(2)),
                         X.mat_vec(I_K, Hh), F(-1))
        phi3 = Sd[3]
        phi3 = X.vec_add(phi3, X.mat_vec(Ks[3], Fh))
        phi3 = X.vec_add(phi3, X.mat_vec(Ks[2], Dh), F(3))
        phi3 = X.vec_add(phi3, X.mat_vec(Ks[1], Hh), F(3))
        phi3 = X.vec_add(phi3, X.mat_vec(I_K, Gh), F(-1))
        sF, sD, sH, sG = (X.sup_norm(v) for v in (Fh, Dh, Hh, Gh))
        sigma4 = sup_Si(sp, 4, emax)  # polynomial sources of degree 3: S'''' = 0, kept general
        Env4 = (sigma4 + 4 * k[1] * sG + 6 * k[2] * (sH + rho * sG)
                + 4 * k[3] * (sD + rho * sH + rho ** 2 * sG / 2)
                + k[4] * (sF + rho * sD + rho ** 2 * sH / 2 + rho ** 3 * sG / 6))
        st = tpt.SourceTerm(H_at_a=(Hh[0], Hh[0]), abs_G_at_a=abs(Gh[0]),
                            fF=X.sup_norm(phi0), fD=X.sup_norm(phi1), fH=X.sup_norm(phi2),
                            fG=X.sup_norm(phi3), Env4=Env4)
        terms.append(st)
        truth.append((famr, Hh[0], Gh[0]))
    # R_m(e) := (1/m) sum_r F_r(e)(a); midpoint g_hi = exact g(e0) (a sealed midpoint enclosure's hi)
    def Rm_derivs(e: F) -> tuple:
        vals = [famr.F_derivs(e, 2) for famr, _, _ in truth]
        return tuple(sum((v[j][0] for v in vals), F(0)) / m for j in range(3))
    R0, R1, _ = Rm_derivs(e0)
    g_hi = R0 - e0 * R1
    cp = tpt.CellProfile(detector="SYNTH", m=m, cell=seed, e0=e0, rho=rho, g_hi=g_hi,
                         A0=A0, A1=A1, A2=A2, terms=terms, label=f"fsm n={n} m={m} seed={seed} G={G_mode}")
    return cp, truth, Rm_derivs, k, C


def third_derivative_bound(cp, truth, k, emax, C):
    """certified B3 >= sup over the cell of |R_m'''(t)|, from the Leibniz tower
    ||F^(n)|| <= C (sigma_n + sum_i binom(n,i) k_i ||F^(n-i)||)."""
    from math import comb
    tot = F(0)
    for famr, _, _ in truth:
        sig = [sup_Si(famr.sp, i, emax) for i in range(4)]
        nF = []
        for n in range(4):
            acc = sig[n] + sum((comb(n, i) * k[i] * nF[n - i] for i in range(1, n + 1)), F(0))
            nF.append(C * acc)
        tot += nF[3]
    return tot / len(truth)


def check_fixture(cp, truth, Rm_derivs, k, C, grid: int = 400, plant: bool = False) -> dict:
    """Pointwise Lemma TC-P and whole-transport soundness.

    plant=True is the NEGATIVE CONTROL: every radius is replaced by half the largest TRUE deviation
    observed for that source, which is invalid by construction at the worst grid point, so the
    pointwise check MUST report a violation."""
    e0, rho, m = cp.e0, cp.rho, len(cp.terms)
    pts = [e0 - rho + 2 * rho * i / grid for i in range(grid + 1)]
    devs = [[] for _ in cp.terms]
    rads = [[] for _ in cp.terms]
    gvals, Rpp = [], []
    for t in pts:
        s = abs(t - e0)
        for j, ((famr, Hh_a, Gh_a), st) in enumerate(zip(truth, cp.terms)):
            Fpp = famr.F_derivs(t, 2)[2][0]
            devs[j].append(abs(Fpp - Hh_a - (t - e0) * Gh_a))
            rads[j].append(tpt.peval(tpt.rad_poly(cp, st), s) - s * st.abs_G_at_a)
        R0, R1, R2 = Rm_derivs(t)
        gvals.append(R0 - t * R1)
        Rpp.append(abs(R2))
    if plant:
        rads = [[max(d) / 2] * len(d) for d in devs]
    viol = sum(1 for j in range(m) for d, r in zip(devs[j], rads[j]) if d > r)
    worst = max((d / r for j in range(m) for d, r in zip(devs[j], rads[j]) if r > 0), default=F(0))
    B3 = third_derivative_bound(cp, truth, k, cp.x_hi, C)
    res = tpt.evaluate(cp)
    target = res["Gamma_tpt"]

    def gpt(t):
        R0, R1, R2 = Rm_derivs(t)
        return R0 - t * R1, abs(R2)

    def ub(a, b, ga, gb, ra, rb):
        h = b - a
        return max(ga, gb) + h / 2 * cp.x_hi * (max(ra, rb) + h / 2 * B3)

    # rigorous sup of g: interval bound per grid piece; pieces whose bound exceeds the TPT bound are
    # bisected (exact midpoint evaluation) up to depth 16 -- refinement only ever tightens the bound
    stack = [(pts[i], pts[i + 1], gvals[i], gvals[i + 1], Rpp[i], Rpp[i + 1], 0) for i in range(grid)]
    sup_upper = None
    refinements = 0
    while stack:
        a, b, ga, gb, ra, rb, dpt = stack.pop()
        u = ub(a, b, ga, gb, ra, rb)
        if u > target and dpt < 16:
            mid = (a + b) / 2
            gm, rm = gpt(mid)
            refinements += 1
            stack.append((a, mid, ga, gm, ra, rm, dpt + 1))
            stack.append((mid, b, gm, gb, rm, rb, dpt + 1))
            continue
        sup_upper = u if sup_upper is None else max(sup_upper, u)
    return {
        "label": cp.label,
        "grid_points": grid + 1,
        "adaptive_refinements": refinements,
        "pointwise_violations": viol,
        "worst_dev_over_rad": float(worst),
        "true_sup_g_lower": float(max(gvals)),
        "true_sup_g_upper_certified": float(sup_upper),
        "g_hi": float(cp.g_hi),
        "P_tpt": float(res["P_tpt"]), "P_riemann64": float(res["P_riemann"]),
        "P_c5t": float(res["P_c5t"]), "P_frozen": float(res["P_frozen"]),
        "tpt_over_c5t": float(res["P_tpt"] / res["P_c5t"]) if res["P_c5t"] else None,
        "true_excess_over_c5t": (float((max(gvals) - cp.g_hi) / res["P_c5t"]) if res["P_c5t"] else None),
        "sound_transport": bool(max(gvals) <= res["Gamma_tpt"]),
        "sound_transport_certified": bool(sup_upper <= res["Gamma_tpt"]),
        "_exact": res,
    }


def main() -> None:
    t0 = time.time()
    out = {"schema": "OV_TPT_SYNTHETIC/1", "fixtures": [], "negative_controls": []}
    cfgs = []
    for seed in range(1, 13):
        n = 4 + seed % 3
        m = 1 + seed % 3
        rho = [F(1, 64), F(1, 32), F(1, 16)][seed % 3]
        pert = [F(1, 10 ** 6), F(1, 10 ** 4), F(1, 10 ** 3)][seed % 3]
        G_mode = "zero" if seed % 2 == 0 else "real"
        cfgs.append((seed, n, m, F(1, 8), rho, pert, G_mode))
    for (seed, n, m, e0, rho, pert, G_mode) in cfgs:
        cp, truth, Rmd, k, C = build_fixture(seed, n, m, e0, rho, pert, G_mode)
        r = check_fixture(cp, truth, Rmd, k, C)
        r.pop("_exact")
        r["config"] = {"seed": seed, "n": n, "m": m, "e0": str(e0), "rho": str(rho), "pert": str(pert),
                       "G_mode": G_mode}
        out["fixtures"].append(r)
        # negative control on the same fixture: radius planted at half the largest TRUE deviation
        nc = check_fixture(cp, truth, Rmd, k, C, grid=40, plant=True)
        out["negative_controls"].append({"label": cp.label, "plant": "rad := max_true_dev / 2",
                                         "pointwise_violations_detected": nc["pointwise_violations"]})
    fx = out["fixtures"]
    out["summary"] = {
        "fixtures": len(fx),
        "pointwise_violations_total": sum(r["pointwise_violations"] for r in fx),
        "transport_sound_all": all(r["sound_transport"] for r in fx),
        "transport_sound_certified_all": all(r["sound_transport_certified"] for r in fx),
        "riemann_ge_closed_all": all(r["P_riemann64"] >= r["P_tpt"] for r in fx),
        "negative_controls_detected": sum(1 for c in out["negative_controls"] if c["pointwise_violations_detected"] > 0),
        "negative_controls_total": len(out["negative_controls"]),
        "tpt_over_c5t_range": [min(r["tpt_over_c5t"] for r in fx if r["tpt_over_c5t"] is not None),
                               max(r["tpt_over_c5t"] for r in fx if r["tpt_over_c5t"] is not None)],
        "wall_s": round(time.time() - t0, 2),
    }
    p = NS / "validation" / "TPT_SYNTHETIC.json"
    p.write_text(json.dumps(out, indent=1, sort_keys=True))
    Q.log_execution("streams/E_assembly/validate_tpt_synthetic.py", "TPT V1/V2/V4 on exact FSM fixtures",
                    cells_touched=[], klass="SYNTHETIC_VALIDATION")
    print(json.dumps(out["summary"], indent=1))


if __name__ == "__main__":
    main()
