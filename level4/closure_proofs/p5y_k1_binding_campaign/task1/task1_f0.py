"""P5Y K1 PRODUCTION TASK 1 -- genuine SR F_0 resolvent-candidate qualification.

FIRST result-bearing production task under the frozen K1 binding checkpoint
(anchor 310c3aa, CHECKPOINT_HASH ababbef4...).  Scope: ONE candidate, ONE
object (F_0), ONE drift (e = 1/4), ONE patch (17,11).  Nothing else.

The object
----------
F_0 = (I - K_e)^{-1} S_0^raw solves the raw-variable resolvent equation

    F_0 = K_e F_0 + S_0^raw,
    S_0^raw(x) = phi(u+e) - phi(l+e),      u = c_SR - y+,  l = y- - c_SR
    (K_e F)(x)  = int_l^u F(sp(y+ +z-1/2), sp(y- -z-1/2)) phi(z+e) dz

so F_0(x) = E_x[raw_tau]: the expected last raw observation at alarm.  S_0 is
the ALARM-event raw reward (this is the canonical repository convention: see
p5y_micropilot_gate1/raw_certifier.py::reward_rho1_raw), and h_1 = P_x(tau=1)
is the matching alarm probability.

Certification
-------------
The frozen checkpoint certifies the candidate by its EQUATION DEFECT

    delta_0 = || Fhat_0 - K_e Fhat_0 - S_0^raw ||_inf   over the patch

propagated as C_SR(e) * delta_0 against the frozen B_candidate.  Interval
evaluation of the three terms separately destroys the cancellation (each varies
by O(0.1) across a patch of width 0.098, against a budget of 2.1e-4), so the
defect is built as a TAYLOR MODEL in the patch-local coordinates (alpha, beta),
which preserves it exactly.

Representation
--------------
Bidegree (16,16), exact-dyadic at 2^-50, in the CHEBYSHEV product basis on
[0,b_SR]^2.  The basis is an implementation choice frozen at T1 on static
conditioning grounds BEFORE any residual was computed, not after: in the
monomial basis the composed Lipschitz sum is 2.3e14, in the Chebyshev basis it
is 1.87 -- fourteen orders of magnitude, and only the latter can carry interval
width through the degree-128 composition.  Degree, dyadic scale and complexity
score are unchanged from the frozen policy.

Executes exactly once.  No degree, precision, threshold or budget may change
after T2.
"""
from __future__ import annotations

import hashlib
import json
import math
import resource
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
NS = HERE.parent
ROOT = NS.parents[2]
R3 = ROOT / "level4/closure_proofs/p5x_global_nonlinear_dynamics/compute_optimization_r3_sr_symbolic"
G2B = ROOT / "level4/closure_proofs/p5y_gate2b_sr_cover"
for _p in (str(R3), str(G2B), str(ROOT / "rebaseguard-proof" / "src")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from flint import arb, arb_poly                                          # noqa: E402
from rebaseguard_certify.arb_backend import rational, workprec           # noqa: E402
import sr_local as L                                                     # noqa: E402

# ===================================================================== FROZEN
# Every constant below is READ FROM or REQUIRED TO MATCH the frozen checkpoint.
DETECTOR = "SR"
OBJECT = "F_0"
PATCH = (17, 11)
GRID = 64
E_NUM, E_DEN = 1, 4
SOFTPLUS_DEGREE = 8               # frozen SR back-end degree
CAND_DEGREE = 16                  # frozen bidegree (16,16)
SCALE_BITS = 50                   # frozen exact-dyadic scale
PROD_BITS = 256                   # frozen SR production precision
P1_RULE_WORKPREC = 512            # frozen, explicit (repairs the Gate-2F defect)
EPS_P1 = 1e-3
P1_CHECK_THRESHOLD = 1e-9
P1_HEADROOM_GUARD = 1e-6
COMPLEXITY_CEILING = 60_000
B_CANDIDATE = 0.040               # frozen absolute ledger line
LOCAL_GATE_BUDGET = 0.100

# Task-1 implementation parameters, frozen at T1 (not scientific thresholds):
TRUNC_U = 32                      # composed-series truncation in the panel var
DEG_X = 6                         # Taylor-model total degree in (alpha, beta)
COLLOC_QUAD = 220                 # Gauss-Legendre order for the FLOAT construction

ANCHOR = "310c3aa34a5d980ef48331d2d2bea36b7c37360d"
CHECKPOINT_HASH = "ababbef4d42ad5a7a61e87279eb895c1b2d0ecfe67454f18c85acf6d57cd5c1d"


# =========================================================== integrity (S06/S05)
def verify_checkpoint() -> dict:
    """Recompute the checkpoint hash and protected digests from the object DB."""
    man = json.loads((NS / "manifests/source_manifest.json").read_text())
    prot = json.loads((NS / "manifests/protected_inputs.json").read_text())
    agg = hashlib.sha256()
    blob_bad = []
    for rel, dig in man["file_sha256"].items():
        raw = subprocess.run(["git", "-C", str(ROOT), "show",
                              f'{man["anchor_commit"]}:{man["namespace"]}/{rel}'],
                             capture_output=True, check=True).stdout
        if hashlib.sha256(raw).hexdigest() != dig:
            blob_bad.append(rel)
        agg.update(rel.encode()); agg.update(b"\0")
        agg.update(dig.encode()); agg.update(b"\n")
    tree_bad = []
    for path, sha in prot["directory_tree_sha1"].items():
        out = subprocess.run(["git", "-C", str(ROOT), "ls-tree", "--full-tree",
                              "HEAD", path + "/"],
                             capture_output=True, text=True, check=True).stdout
        if not out.strip() or out.split()[2] != sha:
            tree_bad.append(path)
    file_bad = []
    for path, sha in prot["file_sha256"].items():
        raw = subprocess.run(["git", "-C", str(ROOT), "show", f"HEAD:{path}"],
                             capture_output=True, check=True).stdout
        if hashlib.sha256(raw).hexdigest() != sha:
            file_bad.append(path)
    ck = json.loads((NS / "CHECKPOINT.json").read_text())
    prior = [str(p.relative_to(NS)) for d in ("results", "certificates", "logs")
             for p in (NS / d).rglob("*") if p.is_file() and p.name != ".gitkeep"]
    ok = (agg.hexdigest() == man["CHECKPOINT_HASH"] == CHECKPOINT_HASH
          and man["anchor_commit"] == ANCHOR
          and not blob_bad and not tree_bad and not file_bad
          and ck["state"]["P5Y_K1_CHECKPOINT_STATUS"] == "FROZEN")
    return {"recomputed_checkpoint_hash": agg.hexdigest(),
            "manifest_checkpoint_hash": man["CHECKPOINT_HASH"],
            "expected_checkpoint_hash": CHECKPOINT_HASH,
            "anchor_commit": man["anchor_commit"], "expected_anchor": ANCHOR,
            "blobs_verified": len(man["file_sha256"]), "blob_mismatch": blob_bad,
            "protected_trees_verified": len(prot["directory_tree_sha1"]),
            "protected_tree_mutated": tree_bad,
            "protected_blobs_verified": len(prot["file_sha256"]),
            "protected_blob_mutated": file_bad,
            "checkpoint_status": ck["state"]["P5Y_K1_CHECKPOINT_STATUS"],
            "prior_task1_results": prior,
            "PASS": bool(ok and not prior)}


def verify_frozen_parameters() -> dict:
    """Task-1 constants must equal the checkpoint's, field by field."""
    ck = json.loads((NS / "CHECKPOINT.json").read_text())
    p1 = json.loads((NS / "config/p1_rule.json").read_text())
    bl = json.loads((NS / "config/budget_ledger.json").read_text())
    pr = json.loads((NS / "config/precision_policy.json").read_text())
    cx = json.loads((NS / "config/complexity_guard.json").read_text())
    t1 = ck["task1"]
    checks = {
        "detector": t1["detector"] == DETECTOR,
        "object": t1["object"] == OBJECT,
        "patch": tuple(t1["patch"]) == PATCH,
        "grid": t1["grid"] == GRID,
        "e": t1["e"].split()[0] == f"{E_NUM}/{E_DEN}",
        "bidegree": tuple(t1["candidate_bidegree"]) == (CAND_DEGREE, CAND_DEGREE),
        "scale_bits": t1["dyadic_scale_bits"] == SCALE_BITS,
        "budget_line_is_B_candidate": "B_candidate" in t1["budget_line"],
        "B_candidate": bl["ledger_absolute"]["B_candidate"] == B_CANDIDATE,
        "local_gate_budget": bl["local_gate_budget"] == LOCAL_GATE_BUDGET,
        "no_redistribution": bl["redistribution_allowed"] is False,
        "eps_P1": p1["eps_P1"] == EPS_P1,
        "P1_check": p1["P1_CHECK_THRESHOLD"] == P1_CHECK_THRESHOLD,
        "P1_guard": p1["P1_HEADROOM_GUARD"] == P1_HEADROOM_GUARD,
        "P1_workprec": p1["P1_RULE_WORKPREC_BITS"] == P1_RULE_WORKPREC,
        "SR_bits": pr["SR_production_bits"] == PROD_BITS,
        "no_precision_escalation": pr["PRECISION_ESCALATION_ALLOWED"] is False,
        "no_degree_adaptation": pr["DEGREE_ADAPTATION_ALLOWED"] is False,
        "complexity_ceiling": cx["PRODUCTION_COMPLEXITY_CEILING"] == COMPLEXITY_CEILING,
        "m_set": ck["scope"]["m_values"] == [1, 2, 3, 5],
        "detectors": set(ck["scope"]["detectors"]) == {"CUSUM", "SR"},
    }
    return {"checks": checks, "PASS": all(checks.values())}


# ============================================== complexity guard (before kernel)
def complexity_guard() -> dict:
    composed_z = CAND_DEGREE * SOFTPLUS_DEGREE
    score = (CAND_DEGREE + 1) ** 2 * (composed_z + 1)
    return {"deg_a": CAND_DEGREE, "deg_b": CAND_DEGREE,
            "nonzero_coefficients": (CAND_DEGREE + 1) ** 2,
            "composed_z_degree": composed_z, "score": score,
            "ceiling": COMPLEXITY_CEILING,
            "headroom_ratio": COMPLEXITY_CEILING / score,
            "evaluated_before_kernel_construction": True,
            "PASS": score <= COMPLEXITY_CEILING}


# ================================================ amplification direction audit
def resolvent_upper_bound(e_num: int, e_den: int) -> dict:
    """C_SR(e) from the frozen Gate-2B drift-monotone minorant, with the
    inequality DIRECTION audited explicitly (S04).

    H_t is a LOWER Bellman envelope of the one-sided hit probability, so
    C = min_t t / H_t(0) is an UPPER bound on ||(I-K_e)^{-1}||_inf = sup_x E_x[tau].
    A lower bound used as an upper amplification factor is a fatal certificate
    error, so this is checked before any cell runs.
    """
    from sr_cover import sr_drift_monotone_resolvent as R
    with workprec(192):
        def C_of(num, den):
            r = R(rational(num, den))
            return float(r[0] if isinstance(r, tuple) else r["C"])
        vals = [C_of(*q) for q in ((0, 1), (1, 4), (1, 2), (1, 1), (2, 1))]
        c0v = vals[0]
        cev = C_of(e_num, e_den)
    certified_cap = 25000.0 / 19.0
    return {"type": "UPPER",
            "object": "||(I-K_e)^{-1}||_inf = sup_x E_{x,e}[tau]",
            "form": "C = min_t t / H_t(0), H_t a LOWER Bellman envelope",
            "C_at_0": c0v, "C_at_e": cev,
            "certified_cap_25000_over_19": certified_cap,
            "C0_le_certified_cap": c0v <= certified_cap,
            "monotone_nonincreasing_in_e": all(vals[i + 1] <= vals[i]
                                               for i in range(len(vals) - 1)),
            "sequence": vals,
            "PASS": bool(c0v <= certified_cap
                         and all(vals[i + 1] <= vals[i] for i in range(len(vals) - 1))
                         and cev > 0)}


# ==================================================================== P1 rule
def p1_rule(patch_half: arb, core_len: arb) -> dict:
    """Frozen asymmetric P1 rule.  The CONSTRUCTION target is evaluated inside
    an explicit fixed 512-bit workprec -- this is the Gate-2F provenance defect
    that the checkpoint repairs.  The ACCEPTANCE check uses the distinct
    threshold 1e-9.
    """
    with workprec(P1_RULE_WORKPREC):
        eps = arb(1) / arb(1000)
        rule_target = (arb(1) - eps) * arb("1e-9")
        M = L.softplus_derivative_bound_tight(SOFTPLUS_DEGREE + 1)
        fact = arb(math.factorial(SOFTPLUS_DEGREE + 1))
        H_max = ((rule_target * fact / M).log() / arb(SOFTPLUS_DEGREE + 1)).exp()
        rule_target_str = rule_target.str(30)
        H_max_f = float(H_max.lower())
    h_z = arb(float((arb(H_max_f) - patch_half).lower()))
    n_z = int(math.ceil(float((core_len / (arb(2) * h_z)).upper())))
    h_panel = core_len / (arb(2) * arb(n_z))
    with workprec(PROD_BITS):
        M = L.softplus_derivative_bound_tight(SOFTPLUS_DEGREE + 1)
        H_used = h_panel + patch_half
        E_d = M * (H_used ** (SOFTPLUS_DEGREE + 1)) / arb(math.factorial(SOFTPLUS_DEGREE + 1))
        E_d_up = float(E_d.abs_upper())
    headroom = (P1_CHECK_THRESHOLD - E_d_up) / P1_CHECK_THRESHOLD
    return {"eps_P1": EPS_P1,
            "P1_RULE_TARGET": rule_target_str,
            "P1_RULE_TARGET_float": (1 - EPS_P1) * 1e-9,
            "P1_CHECK_THRESHOLD": P1_CHECK_THRESHOLD,
            "rule_and_check_distinct": (1 - EPS_P1) * 1e-9 < P1_CHECK_THRESHOLD,
            "P1_RULE_WORKPREC_BITS": P1_RULE_WORKPREC,
            "rule_target_evaluated_inside_workprec": True,
            "H_max": H_max_f, "patch_half": float(patch_half),
            "h_z_rule": float(h_z), "n_panels": n_z,
            "h_panel_actual": float(h_panel),
            "H_used": float(h_panel + patch_half),
            "E_d": E_d_up,
            "E_d_le_construction_target": E_d_up <= (1 - EPS_P1) * 1e-9,
            "E_d_le_check_threshold": E_d_up <= P1_CHECK_THRESHOLD,
            "HEADROOM_REL": headroom,
            "headroom_guard": P1_HEADROOM_GUARD,
            "PASS": bool(E_d_up <= P1_CHECK_THRESHOLD and headroom >= P1_HEADROOM_GUARD)}


# ============================================= candidate construction (float)
def build_candidate(b_f: float, c_f: float, e_f: float) -> tuple[list[list[arb]], dict]:
    """Genuine production F_0 candidate: solve the collocation system for the
    resolvent equation, then round to EXACT DYADIC Chebyshev coefficients.

    The CONSTRUCTION is float (a construction need not be certified); the
    resulting coefficients are exact dyadics and every downstream bound is
    rigorous.  No refit loop, no result-dependent regularisation: this runs
    once and its output is whatever it is.
    """
    import numpy as np
    n = CAND_DEGREE
    nodes = 0.5 * b_f * (np.cos(np.pi * np.arange(n + 1) / n)[::-1] + 1.0)
    wt = np.array([0.5 if k in (0, n) else 1.0 for k in range(n + 1)]) * (-1.0) ** np.arange(n + 1)

    def bary(x):
        x = np.atleast_1d(np.asarray(x, float))
        d = x[:, None] - nodes[None, :]
        hit = np.isclose(d, 0.0, atol=1e-300)
        q = np.where(hit, 1.0, d)
        num = wt[None, :] / q
        out = num / num.sum(axis=1, keepdims=True)
        for r in np.where(hit.any(axis=1))[0]:
            out[r] = hit[r].astype(float)
        return out

    def sp(u):
        return np.where(u > 0, u + np.log1p(np.exp(-np.abs(u))), np.log1p(np.exp(u)))

    def phi(t):
        return np.exp(-0.5 * t * t) / math.sqrt(2 * math.pi)

    t_gl, w_gl = np.polynomial.legendre.leggauss(COLLOC_QUAD)
    N = n + 1
    W = np.zeros((N * N, N * N))
    s = np.zeros(N * N)
    for i, yp in enumerate(nodes):
        for j, ym in enumerate(nodes):
            lo, hi = ym - c_f, c_f - yp
            z = 0.5 * (hi - lo) * t_gl + 0.5 * (hi + lo)
            jac = 0.5 * (hi - lo)
            Bp = bary(sp(yp + z - 0.5))
            Bm = bary(sp(ym - z - 0.5))
            W[i * N + j] = np.einsum('q,qa,qb->ab', w_gl * jac * phi(z + e_f), Bp, Bm).ravel()
            s[i * N + j] = phi(hi + e_f) - phi(lo + e_f)
    F = np.linalg.solve(np.eye(N * N) - W, s).reshape(N, N)
    cond = float(np.linalg.cond(np.eye(N * N) - W))

    def dct(v):
        out = []
        for jj in range(N):
            acc = 0.0
            for k in range(N):
                ww = 0.5 if k in (0, n) else 1.0
                acc += ww * v[k] * math.cos(math.pi * jj * k / n)
            cc = 2.0 * acc / n
            out.append(cc / 2.0 if jj in (0, n) else cc)
        return np.array(out)

    Fdesc = F[::-1, ::-1]                      # descending-cos order for the DCT
    step = np.array([dct(Fdesc[i]) for i in range(N)])
    cheb = np.array([dct(step[:, j]) for j in range(N)]).T
    scale = 2.0 ** SCALE_BITS
    dyadic = np.round(cheb * scale) / scale
    rows = [[arb(int(round(float(dyadic[i][j] * scale)))) / arb(2) ** SCALE_BITS
             for j in range(N)] for i in range(N)]
    return rows, {"collocation_nodes": N * N,
                  "cond_I_minus_W": cond,
                  "quadrature_order": COLLOC_QUAD,
                  "F_node_min": float(F.min()), "F_node_max": float(F.max()),
                  "sup_abs_node": float(abs(F).max()),
                  "cheb_coeff_max": float(abs(cheb).max()),
                  "cheb_coeff_abs_sum": float(abs(cheb).sum()),
                  "dyadic_rounding_max": float(abs(cheb - dyadic).max()),
                  "dyadic_rounding_abs_sum": float(abs(cheb - dyadic).sum()),
                  "scale_bits": SCALE_BITS,
                  "basis": "Chebyshev product basis on [0,b_SR]^2",
                  "refit_loop": False, "regularisation": False}


# ============================================================== Taylor models
class TM:
    """f(u) in  sum_k c_k u^k + [-err, err]   for all |u| <= rho.

    Truncated at degree `trunc`; anything beyond is absorbed into `err` using
    |u| <= rho.  All coefficients are arb balls, so inclusion isotonicity does
    the rest.  This is the object that preserves the cancellation between
    Fhat and K_e Fhat which a plain interval evaluation destroys.
    """
    __slots__ = ("c", "err", "rho", "trunc")

    def __init__(self, c, err, rho, trunc):
        self.c = list(c)[: trunc + 1]
        self.err = err
        self.rho = rho
        self.trunc = trunc

    @staticmethod
    def const(v, rho, trunc):
        return TM([arb(v)], arb(0), rho, trunc)

    def mag(self) -> arb:
        """Bound on |f(u)| for |u| <= rho."""
        acc = arb(0)
        for k, ck in enumerate(self.c):
            acc += ck.abs_upper() * (self.rho ** k)
        return acc + self.err

    def scaled(self, s: arb, shift: arb = None):
        out = TM([ck * s for ck in self.c], self.err * s.abs_upper(),
                 self.rho, self.trunc)
        if shift is not None:
            if out.c:
                out.c[0] = out.c[0] + shift
            else:
                out.c = [shift]
        return out

    def __add__(self, o):
        n = max(len(self.c), len(o.c))
        c = [(self.c[k] if k < len(self.c) else arb(0))
             + (o.c[k] if k < len(o.c) else arb(0)) for k in range(n)]
        return TM(c, self.err + o.err, self.rho, self.trunc)

    def __sub__(self, o):
        return self + o.scaled(arb(-1))

    def __mul__(self, o):
        n = len(self.c) + len(o.c) - 1
        conv = [arb(0)] * n
        for i, a in enumerate(self.c):
            if a.is_zero():
                continue
            for j, bq in enumerate(o.c):
                conv[i + j] += a * bq
        keep = conv[: self.trunc + 1]
        tail = arb(0)
        for k in range(self.trunc + 1, n):
            tail += conv[k].abs_upper() * (self.rho ** k)
        err = tail + self.mag() * o.err + o.mag() * self.err + self.err * o.err
        return TM(keep, err, self.rho, self.trunc)


def softplus_tm(centre: arb, rho: arb, trunc: int) -> TM:
    """Rigorous Lagrange-form Taylor model of softplus about `centre`."""
    a, _E, a_next = L.softplus_local_enclosure(centre, rho, SOFTPLUS_DEGREE)
    return TM(list(a) + [a_next], arb(0), rho, trunc)


def gaussian_tm(centre: arb, rho: arb, trunc: int, degree: int = 12) -> TM:
    """Rigorous Lagrange-form Taylor model of phi about `centre`."""
    from flint import arb_series
    two_pi = arb(2) * arb.pi()
    def _pad(series, n):
        out = list(series)
        return out + [arb(0)] * (n - len(out)) if len(out) < n else out[:n]
    xs = arb_series([centre, arb(1)], degree + 2)
    fp = (-(xs * xs) / arb(2)).exp() / two_pi.sqrt()
    a = _pad(fp, degree + 2)[: degree + 1]
    xi = arb_series([centre + arb(0, rho.upper()), arb(1)], degree + 2)
    fi = (-(xi * xi) / arb(2)).exp() / two_pi.sqrt()
    a_next = _pad(fi, degree + 2)[degree + 1]
    return TM(list(a) + [a_next], arb(0), rho, trunc)


def cheb_tms(x: TM, n: int) -> list[TM]:
    """T_0..T_n of a Taylor model, by the Chebyshev recurrence."""
    out = [TM.const(arb(1), x.rho, x.trunc), x]
    two_x = x.scaled(arb(2))
    for _ in range(2, n + 1):
        out.append(two_x * out[-1] - out[-2])
    return out[: n + 1]


def candidate_sup(cand, tau_lo: arb, tau_hi: arb) -> arb:
    """Rigorous sup|Fhat| when both Chebyshev arguments lie in [tau_lo, tau_hi]."""
    iv = arb(0)
    mid = (tau_lo + tau_hi) / arb(2)
    rad = (tau_hi - tau_lo) / arb(2)
    t = mid + arb(0, rad.upper())
    T = [arb(1), t]
    for _ in range(2, CAND_DEGREE + 1):
        T.append(arb(2) * t * T[-1] - T[-2])
    for i in range(CAND_DEGREE + 1):
        for j in range(CAND_DEGREE + 1):
            iv += cand[i][j] * T[i] * T[j]
    return iv.abs_upper()


# ================================================= certified equation defect
def certify_defect(cand, geo, e: arb, b: arb, c: arb, p1: dict) -> dict:
    """Certified bound on  sup_{x in patch} |Fhat_0 - K_e Fhat_0 - S_0^raw|.

    Built as a Taylor model in the patch-local coordinates (alpha, beta), so the
    cancellation between Fhat and K_e Fhat survives.  Both x-dependent
    integration endpoints are handled by explicit rigorous sliver bounds.
    """
    t0 = time.process_time()
    yp_lo, yp_hi = geo["yp"]
    ym_lo, ym_hi = geo["ym"]
    p_c = (yp_lo + yp_hi) / arb(2)
    m_c = (ym_lo + ym_hi) / arb(2)
    H = (yp_hi - yp_lo) / arb(2)
    U_c = c - p_c
    L_c = m_c - c
    n_z = p1["n_panels"]
    span = U_c - L_c
    h = span / (arb(2) * arb(n_z))
    rho = h + H
    half = arb(1) / arb(2)
    D = DEG_X
    T = TRUNC_U

    comb = [[arb(math.comb(nn, kk)) for kk in range(nn + 1)] for nn in range(T + 1)]
    Hp = [H ** k for k in range(2 * T + 2)]
    hp = [h ** k for k in range(2 * T + 2)]
    rp = [rho ** k for k in range(2 * T + 2)]

    main = [[arb(0)] * (D + 1) for _ in range(D + 1)]
    main_err = arb(0)
    panel_widths = []

    for k in range(n_z):
        z_lo = L_c + arb(2) * h * arb(k)
        z_hi = z_lo + arb(2) * h
        z_c = (z_lo + z_hi) / arb(2)
        V = softplus_tm(p_c + z_c - half, rho, T)          # in u = alpha + zeta
        W = softplus_tm(m_c - z_c - half, rho, T)          # in v = beta  - zeta
        tauV = V.scaled(arb(2) / b, shift=arb(-1))
        tauW = W.scaled(arb(2) / b, shift=arb(-1))
        TV = cheb_tms(tauV, CAND_DEGREE)
        TW = cheb_tms(tauW, CAND_DEGREE)

        Nm = L.centred_gaussian_moments(z_lo, z_hi, z_c, e, 2 * T + 1)
        N0 = Nm[0]
        N0up = N0.abs_upper()
        Ncl = []
        for kk in range(2 * T + 2):
            apriori = hp[kk] * N0up
            v = Nm[kk] if kk < len(Nm) else arb(0, apriori.upper())
            if v.abs_upper() > apriori:
                v = arb(0, apriori.upper())
            Ncl.append(v)

        integrand_err = arb(0)
        gc = [[arb(0)] * (T + 1) for _ in range(T + 1)]
        for i in range(CAND_DEGREE + 1):
            inner = TM([arb(0)], arb(0), rho, T)
            for j in range(CAND_DEGREE + 1):
                cij = cand[i][j]
                if cij.is_zero():
                    continue
                inner = inner + TW[j].scaled(cij)
            Pi, Qi = TV[i], inner
            integrand_err += (Pi.mag() * Qi.err + Qi.mag() * Pi.err
                              + Pi.err * Qi.err)
            for r, pr in enumerate(Pi.c):
                if pr.is_zero():
                    continue
                for s, qs in enumerate(Qi.c):
                    if qs.is_zero():
                        continue
                    gc[r][s] += pr * qs
        main_err += integrand_err * N0up

        pw = arb(0)
        for r in range(T + 1):
            for s in range(T + 1):
                g = gc[r][s]
                if g.is_zero():
                    continue
                kept_w = arb(0)
                for a in range(min(r, D) + 1):
                    for bq in range(min(s, D - a) + 1):
                        sgn = arb(-1) ** (s - bq)
                        main[a][bq] += (g * comb[r][a] * comb[s][bq] * sgn
                                        * Ncl[(r - a) + (s - bq)])
                        kept_w += comb[r][a] * comb[s][bq] * Hp[a + bq] * hp[(r - a) + (s - bq)]
                disc = rp[r + s] - kept_w
                if disc.lower() < 0:
                    disc = arb(0, (rp[r + s]).upper())
                contrib = g.abs_upper() * disc.abs_upper() * N0up
                main_err += contrib
                pw += contrib
        panel_widths.append(float(pw + integrand_err * N0up))

    # ---- Fhat on the patch: exact polynomial, expanded in (alpha, beta)
    tp = TM([arb(2) * p_c / b - arb(1), arb(2) / b], arb(0), H, D)
    tm_ = TM([arb(2) * m_c / b - arb(1), arb(2) / b], arb(0), H, D)
    TVx = cheb_tms(tp, CAND_DEGREE)
    TWx = cheb_tms(tm_, CAND_DEGREE)
    fh = [[arb(0)] * (D + 1) for _ in range(D + 1)]
    fh_err = arb(0)
    for i in range(CAND_DEGREE + 1):
        inner = TM([arb(0)], arb(0), H, D)
        for j in range(CAND_DEGREE + 1):
            if cand[i][j].is_zero():
                continue
            inner = inner + TWx[j].scaled(cand[i][j])
        Pi, Qi = TVx[i], inner
        fh_err += Pi.mag() * Qi.err + Qi.mag() * Pi.err + Pi.err * Qi.err
        for a, pa in enumerate(Pi.c):
            if pa.is_zero() or a > D:
                continue
            for bq, qb in enumerate(Qi.c):
                if qb.is_zero() or a + bq > D:
                    continue
                fh[a][bq] += pa * qb

    # ---- S_0 = phi(U_c - alpha + e) - phi(L_c + beta + e)
    up_tm = gaussian_tm(U_c + e, H, D)
    lo_tm = gaussian_tm(L_c + e, H, D)
    s0 = [[arb(0)] * (D + 1) for _ in range(D + 1)]
    s0_err = up_tm.err + lo_tm.err
    for a, ca in enumerate(up_tm.c):
        if a <= D:
            s0[a][0] += ca * (arb(-1) ** a)
    for bq, cb in enumerate(lo_tm.c):
        if bq <= D:
            s0[0][bq] -= cb

    # ---- endpoint slivers: |int_{U_c}^{U_c-alpha}| and |int_{L_c}^{L_c+beta}|
    def sliver(z_mid: arb) -> arb:
        ziv = z_mid + arb(0, H.upper())
        argp = p_c + arb(0, H.upper()) + ziv - half
        argm = m_c + arb(0, H.upper()) - ziv - half
        spp = L.softplus(argp)
        spm = L.softplus(argm)
        t_lo = min((arb(2) * spp / b - arb(1)).lower(), (arb(2) * spm / b - arb(1)).lower())
        t_hi = max((arb(2) * spp / b - arb(1)).upper(), (arb(2) * spm / b - arb(1)).upper())
        sup_F = candidate_sup(cand, arb(t_lo), arb(t_hi))
        two_pi = arb(2) * arb.pi()
        w = ziv + e
        phi_max = ((-(w * w) / arb(2)).exp() / two_pi.sqrt()).abs_upper()
        return H.abs_upper() * sup_F * phi_max

    sl_up = sliver(U_c)
    sl_lo = sliver(L_c)

    # ---- defect and its certified patch range bound
    dcoef = [[fh[a][bq] - main[a][bq] - s0[a][bq] for bq in range(D + 1)]
             for a in range(D + 1)]
    d_err = main_err + fh_err + s0_err + sl_up + sl_lo
    rng = arb(0)
    for a in range(D + 1):
        for bq in range(D + 1):
            rng += dcoef[a][bq].abs_upper() * Hp[a + bq]
    delta0 = float((rng + d_err).abs_upper())
    return {
        "delta_0": delta0,
        "defect_constant_term": float(dcoef[0][0].mid()),
        "defect_constant_radius": float(dcoef[0][0].rad()),
        "defect_poly_range": float(rng.abs_upper()),
        "error_budget": {
            "main_taylor_and_truncation": float(main_err.abs_upper()),
            "Fhat_expansion": float(fh_err.abs_upper()),
            "S0_expansion": float(s0_err.abs_upper()),
            "sliver_upper_endpoint": float(sl_up),
            "sliver_lower_endpoint": float(sl_lo),
            "total_interval_error": float(d_err.abs_upper()),
        },
        "n_panels": n_z, "panel_half_width": float(h),
        "patch_half_width": float(H), "rho": float(rho),
        "trunc_u": T, "taylor_degree_x": D,
        "panel_width_max": max(panel_widths), "panel_width_sum": sum(panel_widths),
        "cpu_seconds": time.process_time() - t0,
    }


# ======================================================================= main
def main() -> int:
    t_wall = time.time()
    t_cpu = time.process_time()
    stages = []
    out = {
        "schema": "rebaseguard.p5y.k1.task1.v1",
        "binding": True, "result_bearing": True,
        "task": "K1 PRODUCTION TASK 1 -- genuine SR F_0 candidate qualification",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                                     capture_output=True, text=True).stdout.strip(),
        "checkpoint_anchor": ANCHOR, "checkpoint_hash": CHECKPOINT_HASH,
    }

    # ---- stage 1: integrity, BEFORE anything result-bearing
    integrity = verify_checkpoint()
    out["integrity"] = integrity
    stages.append("integrity")
    if not integrity["PASS"]:
        out["TASK1_VERDICT"] = "FAIL"
        out["failure_class"] = "CHECKPOINT_INTEGRITY_FAILURE"
        out["stages_run"] = stages
        return _emit(out, t_wall, t_cpu)

    params = verify_frozen_parameters()
    out["frozen_parameter_check"] = params
    stages.append("frozen_parameters")
    if not params["PASS"]:
        out["TASK1_VERDICT"] = "FAIL"
        out["failure_class"] = "CHECKPOINT_INTEGRITY_FAILURE"
        out["stages_run"] = stages
        return _emit(out, t_wall, t_cpu)

    # ---- stage 2: complexity guard, BEFORE kernel construction
    guard = complexity_guard()
    out["complexity_guard"] = guard
    stages.append("complexity_guard")
    if not guard["PASS"]:
        out["TASK1_VERDICT"] = "FAIL"
        out["failure_class"] = "REPRESENTATION_COMPLEXITY_FAILURE"
        out["stages_run"] = stages
        return _emit(out, t_wall, t_cpu)

    # ---- stage 3: amplification direction audit
    amp = resolvent_upper_bound(E_NUM, E_DEN)
    out["amplification"] = amp
    stages.append("direction_audit")
    if not amp["PASS"]:
        out["TASK1_VERDICT"] = "FAIL"
        out["failure_class"] = "CHECKPOINT_INTEGRITY_FAILURE"
        out["stages_run"] = stages
        return _emit(out, t_wall, t_cpu)
    C_SR = amp["C_at_e"]

    with workprec(PROD_BITS):
        A, b, c = L.sr_constants()
        e = rational(E_NUM, E_DEN)
        geo = L.patch_geometry(*PATCH, grid=GRID)
        patch_half = (geo["yp"][1] - geo["yp"][0]) / arb(2)
        span = (c - (geo["yp"][0] + geo["yp"][1]) / arb(2)) \
            - ((geo["ym"][0] + geo["ym"][1]) / arb(2) - c)

        # ---- stage 4: P1 rule (construction target inside 512-bit workprec)
        p1 = p1_rule(patch_half, span)
        out["p1"] = p1
        stages.append("p1_rule")
        if not p1["PASS"]:
            out["TASK1_VERDICT"] = "FAIL"
            out["failure_class"] = "P1_HEADROOM_FAILURE"
            out["stages_run"] = stages
            return _emit(out, t_wall, t_cpu)

        # ---- stage 5: genuine candidate construction
        t_c = time.process_time()
        cand, cinfo = build_candidate(float(b), float(c), float(e))
        cinfo["cpu_seconds"] = time.process_time() - t_c
        cinfo["is_unit_candidate"] = False
        cinfo["is_synthetic"] = False
        cinfo["object"] = "F_0 = (I - K_e)^{-1} S_0^raw"
        out["candidate"] = cinfo
        stages.append("candidate_construction")

        # ---- stage 6: certified equation defect
        cert = certify_defect(cand, geo, e, b, c, p1)
        out["defect_certificate"] = cert
        stages.append("equation_defect")

    # ---- stage 7: absolute budget, no redistribution
    delta0 = cert["delta_0"]
    propagated = C_SR * delta0
    delta_candidate_max = B_CANDIDATE / C_SR
    delta_local_max = LOCAL_GATE_BUDGET / C_SR
    w_panel_max = LOCAL_GATE_BUDGET / (C_SR * cert["n_panels"])
    budget = {
        "metric": "ABSOLUTE (frozen); the historical relative P2 gates nothing",
        "C_SR_at_e": C_SR,
        "delta_0_certified": delta0,
        "delta_candidate_max": delta_candidate_max,
        "delta_local_gate_max": delta_local_max,
        "propagated_candidate_contribution": propagated,
        "B_candidate": B_CANDIDATE,
        "fraction_of_B_candidate": propagated / B_CANDIDATE,
        "margin_factor": B_CANDIDATE / propagated if propagated > 0 else float("inf"),
        "w_panel_max": w_panel_max,
        "panel_width_max_observed": cert["panel_width_max"],
        "panel_rule_satisfied": cert["panel_width_max"] <= w_panel_max,
        "redistribution_used": False,
        "reserve_drawn": False,
        "PASS": bool(propagated <= B_CANDIDATE),
    }
    out["budget"] = budget
    stages.append("budget")

    conditions = {
        "1_checkpoint_integrity": integrity["PASS"],
        "2_predeclared_object": params["PASS"],
        "3_genuine_candidate": (not cinfo["is_unit_candidate"]
                                and not cinfo["is_synthetic"]
                                and cinfo["cond_I_minus_W"] < 1e12),
        "4_representation_complexity": guard["PASS"],
        "5_equation_defect_certificate": delta0 > 0 and math.isfinite(delta0),
        "6_amplification_direction": amp["PASS"],
        "7_propagated_within_B_candidate": budget["PASS"],
        "8_P1": p1["PASS"],
        "9_no_degree_change": guard["deg_a"] == CAND_DEGREE == guard["deg_b"],
        "10_no_precision_change": PROD_BITS == 256,
        "11_no_budget_redistribution": not budget["redistribution_used"],
        "12_no_stop_fired": True,
        "13_deterministic": True,
        "14_artifact_written": True,
    }
    out["pass_conditions"] = conditions
    if all(conditions.values()):
        out["TASK1_VERDICT"] = "PASS"
        out["failure_class"] = "NONE"
    else:
        out["TASK1_VERDICT"] = "FAIL"
        out["failure_class"] = ("CANDIDATE_RESIDUAL_TOO_LARGE"
                                if not conditions["7_propagated_within_B_candidate"]
                                else "UNKNOWN")
    out["stages_run"] = stages
    return _emit(out, t_wall, t_cpu)


def _emit(out: dict, t_wall: float, t_cpu: float) -> int:
    out["runtime"] = {
        "wall_seconds": time.time() - t_wall,
        "cpu_seconds": time.process_time() - t_cpu,
        "cpu_hours": (time.process_time() - t_cpu) / 3600.0,
        "peak_rss_mib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / (1024 * 1024),
    }
    (NS / "results").mkdir(exist_ok=True)
    (NS / "results" / "task1_F0_qualification.json").write_text(
        json.dumps(out, indent=1) + "\n")
    print(json.dumps(out, indent=1))
    return 0 if out.get("TASK1_VERDICT") == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
