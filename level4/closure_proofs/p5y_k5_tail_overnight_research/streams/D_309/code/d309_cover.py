"""Cover refinement for the K5-B direct clause: error decomposition in rho, what a REAL refinement (new midpoint records)
buys beyond theorem TPT, and a generic deterministic refinement policy -- validated on synthetic FSM families.

Target-free (no CUSUM cell, no committed tail value, no drift in the quarantined band).

Model of one K1-like record at midpoint e_c with Taylor half-width h (all exact rationals, see COVER_REFINEMENT_309.md):
  * m = 2 sources; R_m(e) := (1/m) sum_r F_r(e)(a) + (1/2) W(e)(a) with W = K_e S_0 (a finite-power term);
  * candidates F^_r, D^_r, H^_r at e_c (perturbed exact derivatives), G^ := 0 (TC-T), Lemma-G constants over the cell;
  * midpoint enclosures R in [R^ +- (1/m) sum A0 f_F], R' in [D^ +- (1/m) sum (A0 f_D + A1 f_F)]  (theorem AD / TC);
  * whole-cell W'' enclosure by a rigorous polynomial range; TC profile rad(s) (Lemma TC-P);
  * clauses: frozen  g_hi + h x_hi M;  C5-T;  TPT (Corollary TPT-M, closed-form polynomial integrals).
Checks (declared rule DECLARED_RULE, fixed before the first run):
  C1  identities: frozen clause = g_hi + h(e_c + h)(|c_lo| + sum_j r_j h^j) as a polynomial in h (premises fixed);
      TPT closed form vs independent Riemann upper/lower sums (bracket);
  C2  soundness: every clause >= the grid maximum of the exact g on the cell (necessary condition; can fail);
  C3  scaling: nested cells rho_k = rho0 / 2^k (k = 0..4, new records each), per-order TPT slack components and their
      log2 ratios (expected j + 1 for the r_j component), total slack slope;
  C4  refinement into N in {2, 3, 4} subcells with NEW records vs the pure-scaling prediction from the parent's own
      premises; the B2 transcription (split with NO new record) equals the parent TPT by construction -- an identity
      of the implementation, NOT evidence for CR-2 (review B3; CR-2 rests on TPT-O alone);
      the C5-style "rho halved" oracle (Taylor rho only) vs a real bisection;
  C5  the one-extra-record anisotropic design (keep the parent record, add one record on the binding quarter);
  C6  policy DRP-1 (dyadic certified branch-and-bound; OUTCOME-ADAPTIVE with a frozen pass predicate, not
      result-free -- review N12) on a fixture-internal synthetic threshold, record counts;
  NC  (repair r1) planted-invalid transports through Record.tpt_parts on every record built (parent, nested, subcells):
      no_rad, flat_rad0, rad_half, no_W, no_midpoint_width; each flagged iff its value < the exact grid max of g on
      that record's cell; plus PROFILE-LEVEL truth checks (L(s) <= exact R''_m <= U(s) on 17 points: genuine must
      pass; no_rad, flat_rad0, rad_half, no_W flagged if they exclude the truth) and a midpoint-level check (g^ with the
      enclosure widths dropped vs the exact g(e_c)); detection POWER reported. midpoint_check has a HARNESS check only.
Writes validation/D309_COVER_FSM.json.
"""
from __future__ import annotations

import json
import math
import random
import sys
import time
from fractions import Fraction as F
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import d309_core as D  # noqa: E402

Q, X = D.Q, D.X

DECLARED_RULE = (
    "Fixtures: seeds 1..10, n = 4 + seed % 3, kernel degree 4 (random_family, kill 1/5, e-range (0, 3/8)), two sources of "
    "degree 5 (make_sources), W = K_e S_0 with coefficient 1/2, candidate perturbation pert = (1e-6, 1e-4, 1e-3)[seed % 3]"
    " (seeded by seed, source index and midpoint), G^ := 0, Lemma-G constants on each (sub)cell. Parent cell e0 = 1/4, "
    "rho0 = 1/8. C3: rho_k = rho0/2^k, k = 0..4, same e0. C4: N in {2, 3, 4} equal subcells of the parent. C5: new "
    "record on the binding quarter. C6: DRP-1 with depth cap 4, synthetic threshold theta = gmax + kappa (Gamma_TPT(parent)"
    " - gmax), kappa in {1/2, 1/4, 1/16}. Truth grid: 65 points per (sub)cell. Riemann: 256 panels. Fixed before the "
    "first run. Repair r1 (declared before the re-run): transport mutants as in the docstring on every record.")

CW = F(1, 2)


class Fix:
    def __init__(self, seed: int):
        self.seed = seed
        self.n = 4 + seed % 3
        self.pert = (F(1, 10 ** 6), F(1, 10 ** 4), F(1, 10 ** 3))[seed % 3]
        self.fam = D.make_family(self.n, seed, F(3, 8), deg=4)
        self.sps = D.make_sources(self.n, 2, seed, deg=5)
        self.famr = [X.DriftFamily(self.fam.kp, sp, (self.fam.e_lo, self.fam.e_hi)) for sp in self.sps]
        # W(e)(a) = sum_y K_ay(e) S0_y(e): an exact polynomial in e
        Wp = [F(0)]
        for y in range(self.n):
            Wp = D.p_add(Wp, D.p_mul(self.fam.kp[0][y], self.sps[0][y]))
        self.Wp = D.p_scale(Wp, CW)
        self._g = {}

    def g(self, e: F) -> F:
        if e not in self._g:
            D.guard_interval(e, e)
            vals = [fr.F_derivs(e, 1) for fr in self.famr]
            R = sum(v[0][0] for v in vals) / 2 + D.p_eval(self.Wp, e)
            R1 = sum(v[1][0] for v in vals) / 2 + D.p_eval(D.p_deriv(self.Wp, 1), e)
            self._g[e] = R - e * R1
        return self._g[e]

    def gmax(self, lo: F, hi: F, pts: int = 65) -> F:
        return max(self.g(lo + (hi - lo) * F(j, pts - 1)) for j in range(pts))


class Record:
    """A synthetic K1-like record + TC-T premises at midpoint ec with Taylor half-width h."""

    def __init__(self, fx: Fix, ec: F, h: F):
        self.fx, self.ec, self.h = fx, F(ec), F(h)
        lo, hi = self.ec - self.h, self.ec + self.h
        D.guard_interval(lo, hi)
        fam = fx.fam
        k = [D.k_cell(fam, i, lo, hi) for i in range(5)]
        C = D.C_cell(fam, self.ec, self.h)
        self.A = A = D.lemma_g(k, C)
        rad = [F(0)]
        Rhat = D.p_eval(fx.Wp, self.ec)
        Dhat = D.p_eval(D.p_deriv(fx.Wp, 1), self.ec)
        dR = dD = F(0)
        cen = F(0)
        for r, (fr, sp) in enumerate(zip(fx.famr, fx.sps)):
            Fd = fr.F_derivs(self.ec, 2)
            rng = random.Random(hash((fx.seed, r, self.ec.numerator, self.ec.denominator)) & 0xFFFFFFFF)
            cand = {"F": D.perturbed(Fd[0], fx.pert, rng), "D": D.perturbed(Fd[1], fx.pert, rng),
                    "H": D.perturbed(Fd[2], fx.pert, rng)}
            tc = D.TCFixture(fam, sp, self.ec, self.h, cand)
            fF, fD, fH = (D.vnorm(tc.phi_leibniz(j)) for j in range(3))
            sH, sD, sF = D.vnorm(tc.Hh), D.vnorm(tc.Dh), D.vnorm(tc.Fh)
            fG = 3 * k[1] * sH + 3 * k[2] * sD + k[3] * sF + D.vnorm(tc.S[3])
            sig4 = D.sigma_cell(sp, 4, lo, hi)
            E0 = sig4 + 6 * k[2] * sH + 4 * k[3] * (sD + self.h * sH) + k[4] * (sF + self.h * sD + self.h ** 2 * sH / 2)
            rad = D.p_add(rad, D.p_scale(D.tc_rad_poly(A, {"F": fF, "D": fD, "H": fH, "G": fG, "Env4": E0}),
                                         F(1, 2)))
            Rhat += cand["F"][0] / 2
            Dhat += cand["D"][0] / 2
            dR += A[0] * fF / 2
            dD += (A[0] * fD + A[1] * fF) / 2
            cen += cand["H"][0] / 2
        self.rad = rad
        W2 = D.p_deriv(fx.Wp, 2)
        self.w_lo = D.min_on(W2, lo, hi)
        self.w_hi = -D.min_on(D.p_scale(W2, F(-1)), lo, hi)
        self.cen = cen
        self.R_iv = (Rhat - dR, Rhat + dR)
        self.D_iv = (Dhat - dD, Dhat + dD)
        self.g_hi = self.R_iv[1] - self.ec * self.D_iv[0]

    # profile: L(s) = c_lo - rad(s), U(s) = c_hi + rad(s)
    @property
    def c_lo(self):
        return self.cen + self.w_lo

    @property
    def c_hi(self):
        return self.cen + self.w_hi

    def H_whole(self, h=None):
        h = self.h if h is None else h
        r = D.p_eval(self.rad, h)
        return self.c_lo - r, self.c_hi + r

    def frozen(self, h=None, rad_h=None) -> F:
        h = self.h if h is None else h
        Hlo, Hhi = self.H_whole(h if rad_h is None else rad_h)
        return self.g_hi + h * (self.ec + h) * max(abs(Hlo), abs(Hhi))

    def c5t(self) -> F:
        Hlo, Hhi = self.H_whole()
        h, ec = self.h, self.ec
        return self.g_hi + max(max(-Hlo, F(0)) * h * (ec + h / 2), max(Hhi, F(0)) * h * (ec - h / 2))

    def tpt_parts(self, hr=None, hl=None, rad=None, clo=None, chi=None) -> dict:
        """closed-form P* pieces for a record at ec with right/left transport lengths hr, hl <= h (TPT-M).
        rad / clo / chi overrides exist ONLY to plant known-invalid profiles (negative controls, repair r1)."""
        hr = self.h if hr is None else hr
        hl = self.h if hl is None else hl
        rad = self.rad if rad is None else rad
        clo = self.c_lo if clo is None else clo
        chi = self.c_hi if chi is None else chi
        ec = self.ec
        negL = D.p_add([-clo], rad)                 # -L(s)
        U = D.p_add([chi], rad)                     # U(s)
        right = D.p_mul([ec, F(1)], negL)           # (ec + s)(-L(s))
        left = D.p_mul([ec, F(-1)], U)              # (ec - s) U(s)

        def integ(p, x):
            return sum((c * x ** (j + 1) / (j + 1) for j, c in enumerate(p)), F(0))
        IR, IL = integ(right, hr), integ(left, hl)
        return {"IR": IR, "IL": IL, "P": max(F(0), IR, IL), "right_poly": right, "left_poly": left}

    def tpt(self, hr=None, hl=None, rad=None) -> F:
        return self.g_hi + self.tpt_parts(hr, hl, rad)["P"]

    def riemann_bracket(self, panels: int = 256) -> tuple:
        parts = self.tpt_parts()
        out = []
        for poly in (parts["right_poly"], parts["left_poly"]):
            hstep = self.h / panels
            vals = [D.p_eval(poly, hstep * j) for j in range(panels + 1)]
            up = sum((max(vals[j], vals[j + 1]) * hstep for j in range(panels)), F(0))
            dn = sum((min(vals[j], vals[j + 1]) * hstep for j in range(panels)), F(0))
            out.append((dn, up))
        # integrands are monotone in s on [0,h] only piecewise; the bracket uses the true min/max of each panel's
        # endpoints, valid for monotone panels; we check dn <= closed <= up
        return out, parts

    def components(self) -> dict:
        """TPT right-side slack components: the r_j part is r_j (ec h^{j+1}/(j+1) + h^{j+2}/(j+2))."""
        h, ec = self.h, self.ec
        comps = {f"r{j}": c * (ec * h ** (j + 1) / (j + 1) + h ** (j + 2) / (j + 2)) for j, c in enumerate(self.rad)}
        comps["centre_W"] = (-self.c_lo) * (ec * h + h * h / 2)
        comps["midpoint_width"] = self.g_hi - self.fx.g(self.ec)
        return comps


def c1_identities(fx: Fix) -> dict:
    rec = Record(fx, F(1, 4), F(1, 8))
    ok_poly = True
    for h in (F(1, 8), F(1, 16), F(3, 64)):
        Hlo, Hhi = rec.H_whole(h)
        lhs = rec.frozen(h)
        clo = abs(Hlo) if abs(Hlo) >= abs(Hhi) else abs(Hhi)
        rhs = rec.g_hi + h * (rec.ec + h) * clo
        ok_poly &= lhs == rhs
    br, parts = rec.riemann_bracket()
    brk = all(dn <= I <= up for (dn, up), I in zip(br, (parts["IR"], parts["IL"])))
    return {"frozen_identity_exact": ok_poly, "tpt_riemann_bracket": brk}


def midpoint_check(Rtrue: F, Dtrue: F, R_iv: tuple, D_iv: tuple) -> bool:
    return R_iv[0] <= Rtrue <= R_iv[1] and D_iv[0] <= Dtrue <= D_iv[1]


def transport_mutants(rec: "Record", gm: F) -> dict:
    """Planted-INVALID transports through Record.tpt_parts (repair r1, review B1/N13). Each is flagged iff its value
    falls below the exact grid maximum gm of g on the record's cell (truth-relative; it can fail to flag)."""
    ghat = (rec.R_iv[0] + rec.R_iv[1]) / 2 - rec.ec * (rec.D_iv[0] + rec.D_iv[1]) / 2
    vals = {
        "no_rad": rec.g_hi + rec.tpt_parts(rad=[F(0)])["P"],
        "flat_rad0": rec.g_hi + rec.tpt_parts(rad=[rec.rad[0]])["P"],
        "rad_half": rec.g_hi + rec.tpt_parts(rad=D.p_scale(rec.rad, F(1, 2)))["P"],
        "no_W": rec.g_hi + rec.tpt_parts(clo=rec.cen, chi=rec.cen)["P"],
        "no_midpoint_width": ghat + rec.tpt_parts()["P"],
    }
    out = {k: bool(v < gm) for k, v in vals.items()}
    # PROFILE-LEVEL truth check (the actual third input of TPT): L(s) <= R''_m(e_c +- s) <= U(s) on 17 points;
    # the genuine profile must pass, planted profiles are flagged if they exclude the exact R''_m somewhere.
    fx = rec.fx
    profiles = {"genuine": (rec.c_lo, rec.c_hi, rec.rad), "no_rad": (rec.c_lo, rec.c_hi, [F(0)]),
                "flat_rad0": (rec.c_lo, rec.c_hi, [rec.rad[0]]),
                "rad_half": (rec.c_lo, rec.c_hi, D.p_scale(rec.rad, F(1, 2))), "no_W": (rec.cen, rec.cen, rec.rad)}
    pviol = {k: False for k in profiles}
    for j in range(17):
        t = rec.ec - rec.h + 2 * rec.h * F(j, 16)
        D.guard_interval(t, t)
        rpp = sum(fr.F_derivs(t, 2)[2][0] for fr in fx.famr) / 2 + D.p_eval(D.p_deriv(fx.Wp, 2), t)
        s_ = abs(t - rec.ec)
        for k, (clo, chi, rad) in profiles.items():
            r_ = D.p_eval(rad, s_)
            if not (clo - r_ <= rpp <= chi + r_):
                pviol[k] = True
    out.update({"profile_" + k: v for k, v in pviol.items()})
    out["midpoint_no_width"] = bool(ghat < fx.g(rec.ec))
    return out


def clause_values(fx: Fix, rec: Record) -> dict:
    lo, hi = rec.ec - rec.h, rec.ec + rec.h
    gm = fx.gmax(lo, hi)
    return {"gmax": gm, "frozen": rec.frozen(), "c5t": rec.c5t(), "tpt": rec.tpt()}


def run_fixture(seed: int) -> dict:
    fx = Fix(seed)
    e0, rho0 = F(1, 4), F(1, 8)
    out = {"seed": seed, "n": fx.n, "pert": str(fx.pert)}
    out["C1"] = c1_identities(fx)
    # midpoint enclosure validity (exact R, R' inside the synthetic record intervals) + NC
    rec0 = Record(fx, e0, rho0)
    vals = [fr.F_derivs(e0, 1) for fr in fx.famr]
    Rtrue = sum(v[0][0] for v in vals) / 2 + D.p_eval(fx.Wp, e0)
    Dtrue = sum(v[1][0] for v in vals) / 2 + D.p_eval(D.p_deriv(fx.Wp, 1), e0)
    out["midpoint_enclosures_valid"] = midpoint_check(Rtrue, Dtrue, rec0.R_iv, rec0.D_iv)
    # HARNESS check of midpoint_check (relabelled, review N13): an interval shifted off the truth by construction
    wR = rec0.R_iv[1] - rec0.R_iv[0] + F(1, 10 ** 12)
    out["harness_midpoint_check_flags_shifted"] = not midpoint_check(Rtrue, Dtrue, (rec0.R_iv[0] + 2 * wR, rec0.R_iv[1] + 2 * wR),
                                                         rec0.D_iv)
    # C2 soundness on the parent
    cv = clause_values(fx, rec0)
    out["C2"] = {"frozen_ge": cv["frozen"] >= cv["gmax"], "c5t_ge": cv["c5t"] >= cv["gmax"],
                 "tpt_ge": cv["tpt"] >= cv["gmax"], "order": cv["tpt"] <= cv["c5t"] <= cv["frozen"],
                 "slack": {k: float(cv[k] - cv["gmax"]) for k in ("frozen", "c5t", "tpt")}}
    # NC: profile with rad(s) := rad(0) (no Taylor growth), evaluated at the WHOLE-cell level
    bad = rec0.g_hi + rec0.tpt_parts(rad=[rec0.rad[0]])["P"]
    out["NC_flat_profile_value_minus_gmax"] = float(bad - cv["gmax"])
    # the arithmetic "half transport" control of r0 is WITHDRAWN (review N13); code-path transport mutants below
    muts = [transport_mutants(rec0, cv["gmax"])]
    # C3 scaling
    sc = []
    for kk in range(5):
        h = rho0 / 2 ** kk
        rec = Record(fx, e0, h)
        comps = rec.components()
        gm = fx.gmax(e0 - h, e0 + h)
        if kk > 0:
            muts.append(transport_mutants(rec, gm))
        sc.append({"h": h, "slack_tpt": rec.tpt() - gm, "slack_frozen": rec.frozen() - gm,
                   "comps": comps, "tpt_ge": rec.tpt() >= gm})
    slopes = []
    for a, b in zip(sc, sc[1:]):
        row = {"h": str(a["h"]),
               "slack_tpt_log2_ratio": math.log2(float(a["slack_tpt"] / b["slack_tpt"])) if b["slack_tpt"] > 0 else None,
               "slack_frozen_log2_ratio": math.log2(float(a["slack_frozen"] / b["slack_frozen"]))}
        for kname in a["comps"]:
            va, vb = a["comps"][kname], b["comps"][kname]
            row[kname] = math.log2(float(va / vb)) if va > 0 and vb > 0 else None
        slopes.append(row)
    out["C3"] = {"sound_all": all(r["tpt_ge"] for r in sc), "log2_ratios": slopes,
                 "parent_components": {kname: float(v) for kname, v in sc[0]["comps"].items()},
                 "parent_slack_tpt": float(sc[0]["slack_tpt"])}
    # C4 refinement
    gm_par = cv["gmax"]
    ref = {}
    parts0 = rec0.tpt_parts()
    right_binds = parts0["IR"] >= parts0["IL"]
    for N in (2, 3, 4):
        hN = rho0 / N
        subs = [Record(fx, e0 - rho0 + hN * (2 * j + 1), hN) for j in range(N)]
        tpt_sub = [s.tpt() for s in subs]
        fro_sub = [s.frozen() for s in subs]
        gm_sub = [fx.gmax(s.ec - s.h, s.ec + s.h) for s in subs]
        muts.extend(transport_mutants(sb, g_) for sb, g_ in zip(subs, gm_sub))
        real_gain = cv["tpt"] - max(tpt_sub)
        # pure-scaling prediction from the PARENT's premises: parent slack function S(h) at the binding end
        par_rad = rec0.rad
        J = N - 1 if right_binds else 0
        ecJ = subs[J].ec

        def slack_model(ec, h):
            negL = D.p_add([-rec0.c_lo], par_rad)
            U = D.p_add([rec0.c_hi], par_rad)
            poly = D.p_mul([ec, F(1)], negL) if right_binds else D.p_mul([ec, F(-1)], U)
            return sum((c * h ** (j + 1) / (j + 1) for j, c in enumerate(poly)), F(0))
        true_inc_par = (fx.g(e0 + rho0) - fx.g(e0)) if right_binds else (fx.g(e0 - rho0) - fx.g(e0))
        endJ = ecJ + hN if right_binds else ecJ - hN
        true_inc_J = fx.g(endJ) - fx.g(ecJ)
        pred_gain = (slack_model(e0, rho0) - true_inc_par) - (slack_model(ecJ, hN) - true_inc_J)
        # B2 TRANSCRIPTION-CONSISTENCY identity (review B3): the record-free split is implemented as the parent's own
        # TPT integrals over sub-lengths, so its max equals the parent TPT BY CONSTRUCTION; not evidence for CR-2
        b2 = max(rec0.g_hi + rec0.tpt_parts(hr=max(F(0), (s.ec + s.h) - e0) if s.ec + s.h > e0 else F(0),
                                           hl=max(F(0), e0 - (s.ec - s.h)) if s.ec - s.h < e0 else F(0))["P"]
                 for s in subs)
        ref[N] = {"real_gain_tpt": float(real_gain), "pred_gain_parent_scaling": float(pred_gain),
                  "pred_rel_err": float((pred_gain - real_gain) / real_gain) if real_gain else None,
                  "gain_fraction_of_parent_slack": float(real_gain / (cv["tpt"] - gm_par)),
                  "frozen_refined_gain": float(cv["frozen"] - max(fro_sub)),
                  "sound_all": all(t >= g for t, g in zip(tpt_sub, gm_sub)),
                  "B2_transcription_identity_diff": float(b2 - cv["tpt"]),
                  "records": N}
    out["C4"] = ref
    # C5-style oracle: Taylor rho halved inside rad only (transport rho, g_hi kept), vs a real bisection
    oracle = rec0.frozen(h=rho0, rad_h=rho0 / 2)
    out["C4_oracle"] = {"frozen": float(cv["frozen"]), "oracle_taylor_rho_halved": float(oracle),
                        "real_bisection_frozen": float(max(Record(fx, e0 - rho0 / 2, rho0 / 2).frozen(),
                                                           Record(fx, e0 + rho0 / 2, rho0 / 2).frozen())),
                        "real_bisection_tpt": float(max(Record(fx, e0 - rho0 / 2, rho0 / 2).tpt(),
                                                        Record(fx, e0 + rho0 / 2, rho0 / 2).tpt()))}
    # C5 one extra record on the binding quarter (anisotropic)
    q = rho0 / 4
    if right_binds:
        newrec = Record(fx, e0 + rho0 - q, q)
        left_part = rec0.g_hi + rec0.tpt_parts(hr=rho0 - 2 * q, hl=rho0)["P"]
    else:
        newrec = Record(fx, e0 - rho0 + q, q)
        left_part = rec0.g_hi + rec0.tpt_parts(hr=rho0, hl=rho0 - 2 * q)["P"]
    one_extra = max(left_part, newrec.tpt())
    out["C5"] = {"one_extra_record": float(one_extra), "parent_tpt": float(cv["tpt"]),
                 "gain_fraction": float((cv["tpt"] - one_extra) / (cv["tpt"] - gm_par)),
                 "N4_gain_fraction": ref[4]["gain_fraction_of_parent_slack"], "records": 1,
                 "sound": one_extra >= gm_par}
    # C6 DRP-1 on synthetic thresholds
    drp = {}
    for kap in (F(1, 2), F(1, 4), F(1, 16)):
        theta = gm_par + kap * (cv["tpt"] - gm_par)
        records, depth_used, status = 0, 0, "PASS"
        stack = [(e0, rho0, 0)]
        leaves_fail = 0
        while stack:
            ec, h, dpt = stack.pop()
            rec = rec0 if dpt == 0 else Record(fx, ec, h)
            if dpt > 0:
                records += 1
            depth_used = max(depth_used, dpt)
            if rec.tpt() < theta:
                continue
            if dpt >= 4:
                leaves_fail += 1
                continue
            stack.append((ec - h / 2, h / 2, dpt + 1))
            stack.append((ec + h / 2, h / 2, dpt + 1))
        if leaves_fail:
            status = "FAIL_AT_DEPTH_CAP"
        drp[str(kap)] = {"status": status, "new_records": records, "depth_used": depth_used,
                         "failing_leaves": leaves_fail}
    out["C6"] = drp
    out["transport_mutants"] = {k: {"records": len(muts), "flagged": sum(1 for mm in muts if mm[k])}
                                for k in muts[0]}
    return out


def main() -> None:
    t0 = time.time()
    out = {"schema": "OV_D309_COVER_FSM/1", "declared_rule": DECLARED_RULE, "fixtures": []}
    for seed in range(1, 11):
        out["fixtures"].append(run_fixture(seed))
    fx = out["fixtures"]
    out["summary"] = {
        "fixtures": len(fx),
        "C1_all": all(f["C1"]["frozen_identity_exact"] and f["C1"]["tpt_riemann_bracket"] for f in fx),
        "midpoint_enclosures_valid_all": all(f["midpoint_enclosures_valid"] for f in fx),
        "C2_sound_all": all(f["C2"]["frozen_ge"] and f["C2"]["c5t_ge"] and f["C2"]["tpt_ge"] for f in fx),
        "C2_order_all": all(f["C2"]["order"] for f in fx),
        "NC_flat_profile_violations": sum(1 for f in fx if f["NC_flat_profile_value_minus_gmax"] < 0),
        "harness_midpoint_check_flags_shifted": sum(1 for f in fx if f["harness_midpoint_check_flags_shifted"]),
        "profile_genuine_violations": sum(f["transport_mutants"]["profile_genuine"]["flagged"] for f in fx),
        "transport_mutant_power": {k: {"records": sum(f["transport_mutants"][k]["records"] for f in fx),
                                       "flagged": sum(f["transport_mutants"][k]["flagged"] for f in fx)}
                                   for k in fx[0]["transport_mutants"]},
        "C3_sound_all": all(f["C3"]["sound_all"] for f in fx),
        "C4_sound_all": all(v["sound_all"] for f in fx for v in f["C4"].values()),
        "C4_B2_transcription_identity_diff_max": max(abs(v["B2_transcription_identity_diff"]) for f in fx
                                                     for v in f["C4"].values()),
        "C4_gain_fraction": {N: [min(f["C4"][N]["gain_fraction_of_parent_slack"] for f in fx),
                                 max(f["C4"][N]["gain_fraction_of_parent_slack"] for f in fx)] for N in (2, 3, 4)},
        "C4_pred_rel_err": {N: [min(f["C4"][N]["pred_rel_err"] for f in fx),
                                max(f["C4"][N]["pred_rel_err"] for f in fx)] for N in (2, 3, 4)},
        "C5_one_extra_gain_fraction": [min(f["C5"]["gain_fraction"] for f in fx),
                                       max(f["C5"]["gain_fraction"] for f in fx)],
        "C5_sound_all": all(f["C5"]["sound"] for f in fx),
        "C6_records": {k: [f["C6"][k]["new_records"] for f in fx] for k in ("1/2", "1/4", "1/16")},
        "C6_status": {k: [f["C6"][k]["status"] for f in fx] for k in ("1/2", "1/4", "1/16")},
        "wall_s": round(time.time() - t0, 1),
    }
    p = D.NS / "validation" / "D309_COVER_FSM.json"
    p.write_text(json.dumps(out, indent=1, sort_keys=True, default=lambda o: float(o) if isinstance(o, F) else str(o)))
    Q.log_execution("streams/D_309/code/d309_cover.py",
                    "cover refinement: clause decomposition in rho, TPT vs real refinement, B2, oracle, DRP-1 on FSM",
                    cells_touched=[], klass="SYNTHETIC_VALIDATION")
    print(json.dumps(out["summary"], indent=1))


if __name__ == "__main__":
    main()
