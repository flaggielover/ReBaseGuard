"""Cell-308 MB campaign (r1) -- the side-effect-free core of the stream-A0 pointwise ladder (design D4).

EXTRACTED (refactor, no change of statement) from the research stream A0. The files were uncommitted at extraction
time; they have since been committed at 646e7e18 with EXACTLY these blob ids. Sources below by sha256 and git-blob id
of the bytes read, with line ranges. Differences from the sources, all non-numeric:
  * no module-level guard installation, no `declared_drift` (that research function accepts only validation drifts):
    each entry calls the guard passed in by the caller (the formal guard), and the pinned Setup / Ctx call the guard
    bound as `ov_quarantine` again;
  * the pinned modules are passed in (mb308_pinned), not loaded here; C1b flags are asserted, not set;
  * informational float fields of the research records (U_float, residuals as floats, ...) are dropped; every exact
    field, every certificate object and every computation order is unchanged (certificate bytes identical: QC06 checks
    this against the persisted stream-A0 certificates at validation drifts).
The functions return exact records and never write a file or print.

  source (stream A0)          sha256 (prefix)   blob id of the bytes read   lines   extracted as
  a0_c2bx.py  c2bx_rung        12c3ca45f809      b1068e0bacb2               29-109  c2bx_rung
  a0_c2b.py   sub_certify      4134797cf3d4      a18e091484c7               88-113  sub_certify
  a0_c2b.py   w_sha256/make_cert                                            164-173 c2b_w_sha256 / c2b_make_cert
  a0_c1b.py   c1b_w_rung       9efbc0d3927d      599827ff6db0               26-64   c1b_w_rung
  a0_c1b.py   poly_ser/de, w_sha256, make_cert                              84-101  poly_ser / poly_de / c1b_*
  a0_ladder.py compose         7717639f170a      17974e1c25d2               85-96   compose (rules R3-R5)
  a0_verify.py verify_certificate 5fb8a9d6601f   7ca1bc915bdc               34-99   pinned_recheck
  a0_common.py canon / fs / sha256_bytes  5df43fd12cd7  32c8a37225de        114-116, 125-126, 226-227
"""
from __future__ import annotations

import hashlib
import json
import time
from fractions import Fraction as F

CBITS = 40                     # a0_c2bx.CBITS == a0_c2b.CBITS
BUMP_MAX = 64                  # a0_c2bx.BUMP_MAX
A0_LATENT = "validation-drift certificate; keep inside streams/A0 (T1/T2)"
EXTRACTION_SOURCES = {
    "a0_c2bx.py": {"sha256": "12c3ca45f8097478532f1e6473d69ff155645c21f5d4897baf165d4670781c84",
                   "blob": "b1068e0bacb21a598e78991f295d0d28f5f6564c", "lines": "29-109"},
    "a0_c2b.py": {"sha256": "4134797cf3d46b784d9c2ebc35d5bf43a7554d456695aa21092ac84c931cd925",
                  "blob": "a18e091484c7948060d248be075416630afdda96", "lines": "88-113, 164-173"},
    "a0_c1b.py": {"sha256": "9efbc0d3927d0c599b696af9a2683081e66096a1e04be07c838ae8e25619c054",
                  "blob": "599827ff6db0cbd41daf66d8d29aaa8fb292cdab", "lines": "26-64, 84-101"},
    "a0_ladder.py": {"sha256": "7717639f170a75ee5c326743601e5de1fbee0850d8cd205e0b862e0da90cc36f",
                     "blob": "17974e1c25d23357ae170fd5a2906ad4dbf9e2ed", "lines": "85-96"},
    "a0_verify.py": {"sha256": "5fb8a9d6601f8fb5c3f8602ecb8aef657f0c2fbbeb8af5e0ac3895486e0e981b",
                     "blob": "7ca1bc915bdcbf7433deccd677b194e38f8e0c95", "lines": "34-99"},
    "a0_common.py": {"sha256": "5df43fd12cd74a94e611550b209656c561bc9f80b8600ac193c430b0b7646c91",
                     "blob": "32c8a37225de97a73c57f7395a194efe626d5466", "lines": "114-116, 125-126, 226-227"},
}


def fs(x) -> str:
    x = F(x)
    return f"{x.numerator}/{x.denominator}"


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def canon(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()


def _exact(x) -> F:
    if isinstance(x, (float, bool)):
        raise TypeError("a float reached an exact layer")
    return F(x)


# ------------------------------------------------------------------ C2b: P1 subsolution check (a0_c2b.sub_certify)
def sub_certify(EX, S, Wint, Qb: int, full: bool = True) -> dict:
    """Exact P1 SUBSOLUTION check; w = Wint * 2^-Qb; pointwise (S.J == 0) only. Lemma in a0_c2b's docstring."""
    P = EX.P
    if S.J != 0:
        raise ValueError("sub_certify: pointwise drift only")
    if any(Wint[i][j] < 0 for (i, j) in S.mesh.nodes):
        return {"certified": False, "reason": "negative nodal value"}
    one = 1 << (P + Qb)
    Kw = EX.kernel_nodes(S, Wint, 0, full, upper=False)
    defect = {x: one + Kw[x] - (Wint[x[0]][x[1]] << P) for x in Kw}
    Hb = EX.hessian_bounds(S, Wint, full)
    fails, worst, cells = 0, None, 0
    for (cell, jj, je, Hss, Hsy, Hyy, err) in Hb:
        cells += 1
        vmin = min(defect[v] for v in cell[8])
        slack = vmin - err
        if slack < 0:
            fails += 1
        if worst is None or slack < worst:
            worst = slack
    scale = F(1, 1 << (P + Qb))
    return {"certified": fails == 0, "failing_cells": fails, "cells_checked": cells,
            "min_slack": fs(worst * scale), "w_atom": fs(F(Wint[0][0], 1 << Qb))}


def c2b_w_sha256(W) -> str:
    return sha256_bytes(canon([[str(x) for x in col] for col in W]))


def c2b_make_cert(kind: str, e, N: int, Qb: int, W, claim: F, latent: str = A0_LATENT) -> dict:
    return {"schema": "A0_CERT/1", "certifier": kind, "drift": fs(e), "N": N, "kind": "whole", "Qbits": Qb,
            "W": [[str(x) for x in col] for col in W], "W_sha256": c2b_w_sha256(W), "claim_w_atom": fs(claim),
            "statement": ("E_a[tau](e) <= claim_w_atom (P1 supersolution, C2b)" if kind == "C2B_P1_SUPER" else
                          "E_a[tau](e) >= claim_w_atom (P1 subsolution, stream A0)"),
            "latent_proxy": latent}


# ------------------------------------------------------------------ C2b rung with exact-scale selection (a0_c2bx)
def c2bx_rung(c2b: dict, guard, e, N: int, latent: str = A0_LATENT) -> dict:
    e = _exact(e)
    guard.guard_drift(e)
    CE, EX = c2b["c2b_certify"], c2b["c2b_exact"]
    P, Q = EX.P, CE.Q
    t0 = time.process_time()
    g, sols = CE.proposal(N, e, e, "whole")
    g_int = CE._dyadic(g)
    S = EX.Setup(N, e)
    Hb = EX.hessian_bounds(S, g_int, True)
    Kup = EX.kernel_nodes(S, g_int, 0, True, upper=True)
    Klo = EX.kernel_nodes(S, g_int, 0, True, upper=False)
    eight_n2 = 8 * N * N
    one_big = 1 << (P + Q + CBITS)
    a_up, a_lo = 1 << CBITS, 1 << CBITS
    for (cell, jj, je, Hss, Hsy, Hyy, err) in Hb:
        ry = (cell[5] - cell[4]) + je
        E = Hss + 2 * ry * Hsy + ry * ry * Hyy
        verts = cell[8]
        Dmin = min((g_int[v[0]][v[1]] << P) - Kup[v] for v in verts)
        den = eight_n2 * Dmin - E
        if den <= 0:
            a_up = None
            break
        a_c = -((-(eight_n2 * (one_big + 1))) // den)
        a_up = max(a_up, a_c)
    for (cell, jj, je, Hss, Hsy, Hyy, err) in Hb:
        ry = (cell[5] - cell[4]) + je
        E = Hss + 2 * ry * Hsy + ry * ry * Hyy
        dmin = min(Klo[v] - (g_int[v[0]][v[1]] << P) for v in cell[8])
        den = E - eight_n2 * dmin
        if den > 0:
            a_lo = min(a_lo, ((one_big - 1) * eight_n2) // den)
    res_u, bumps = None, 0
    if a_up is not None:
        while bumps <= BUMP_MAX:
            Wu = [[a_up * x for x in col] for col in g_int]
            res_u = EX.certify(S, Wu, Q + CBITS, True)
            if res_u["certified"]:
                break
            a_up += 1 + (a_up >> 30)
            bumps += 1
    res_l, dec = None, 0
    while a_lo > 0 and dec <= BUMP_MAX:
        Wl = [[a_lo * x for x in col] for col in g_int]
        res_l = sub_certify(EX, S, Wl, Q + CBITS, True)
        if res_l["certified"]:
            break
        a_lo -= 1 + (a_lo >> 30)
        dec += 1
    up_ok = bool(res_u and res_u["certified"])
    lo_ok = bool(res_l and res_l["certified"])
    rec = {"certifier": "C2B_P1_EXACT_SCALE", "drift": fs(e), "N": N, "cbits": CBITS,
           "status_U": "CERTIFIED" if up_ok else "NOT_CERTIFIED", "status_L": "CERTIFIED" if lo_ok else "NOT_CERTIFIED",
           "alpha_up": fs(F(a_up, 1 << CBITS)) if a_up else None, "bumps_up": bumps,
           "c_lo": fs(F(a_lo, 1 << CBITS)), "decrements_lo": dec,
           "cpu_seconds": round(time.process_time() - t0, 2)}
    certs = {}
    if up_ok:
        rec.update({"U": res_u["w_atom"], "min_slack_U": res_u["min_slack"], "cells_checked": res_u["cells_checked"]})
        cu = c2b_make_cert("C2B_P1_SUPER", e, N, Q + CBITS, Wu, F(res_u["w_atom"]), latent)
        cu["selection"] = "A0_EXACT_SCALE"
        certs["super"] = cu
    if lo_ok:
        rec.update({"L": res_l["w_atom"], "min_slack_L": res_l["min_slack"]})
        cl = c2b_make_cert("C2B_P1_SUB", e, N, Q + CBITS, Wl, F(res_l["w_atom"]), latent)
        cl["selection"] = "A0_EXACT_SCALE"
        certs["sub"] = cl
    return {"record": rec, "certs": certs}


# ------------------------------------------------------------------ C1b pointwise W-only rung (a0_c1b.c1b_w_rung)
def poly_ser(P: dict) -> list:
    return [[i, j, k, fs(v)] for (i, j, k), v in sorted(P.items())]


def poly_de(L: list) -> dict:
    return {(int(i), int(j), int(k)): F(v) for i, j, k, v in L}


def c1b_w_sha256(Wser) -> str:
    return sha256_bytes(canon(Wser))


def c1b_make_cert(e, d: int, BW, W, claim: F, latent: str = A0_LATENT) -> dict:
    Wser = [poly_ser(P) for P in W]
    return {"schema": "A0_CERT/1", "certifier": "C1B_PW_W_SUPER", "drift": fs(e), "degree": d, "BW": list(BW),
            "W": Wser, "W_sha256": c1b_w_sha256(Wser), "claim_w_atom": fs(claim),
            "statement": "E_a[tau](e) <= claim_w_atom (strip-piecewise polynomial whole-kernel supersolution, C1b S2)",
            "latent_proxy": latent}


def c1b_w_rung(c1b: dict, guard, e, d: int, latent: str = A0_LATENT) -> dict:
    """Needs the C1b flags TIGHT_CT = True, BLOCK_LIGHT = False (set by the caller; asserted here) and a dyadic e."""
    e = _exact(e)
    guard.guard_drift(e)
    cp, PW, FL = c1b["c1b_certpw"], c1b["c1b_pw"], c1b["c1b_float"]
    if not (cp.TIGHT_CT is True and cp.BLOCK_LIGHT is False):
        raise RuntimeError("c1b_w_rung needs TIGHT_CT = True, BLOCK_LIGHT = False")
    BW = PW.BW_PW
    lines: list = []
    t0 = time.process_time()
    cx = cp.Ctx(e, BW, lines.append)
    D = PW.DiscPW(float(e), d, BW)                      # untrusted float candidate (proposal only)
    qw = FL.QR(D.matrix(True))
    Wf = D.split(qw.solve([1.0] * len(D.pts)))
    cW = PW.to_exact_pw(Wf, D.idx)
    res = PW.tadd(PW.tadd(cx.P(cW), cx.P(cp.wconst(1, cx.S)), -1), cx.K(cW, 0, True), -1)
    encW = cx.enc(res, "W")
    rWlo, rWhi = encW["lo"], encW["hi"]
    rec = {"certifier": "C1B_PW_W_SUPER", "drift": fs(e), "degree": d, "BW": list(BW),
           "flags": {"TIGHT_CT": cp.TIGHT_CT, "BLOCK_LIGHT": cp.BLOCK_LIGHT}, "residual_boxes": encW["boxes"]}
    if rWlo <= -1:
        rec.update({"status": "SCALING_RULE_INAPPLICABLE", "cpu_seconds": round(time.process_time() - t0, 2)})
        return {"record": rec, "cert": None}
    etaW = F(0) if rWlo >= 0 else cp.dyadic_up(-rWlo / (1 + rWlo))
    W = cp.wscale(cW, 1 + etaW)
    sW = cp.check_supersolution(cx, W, True, "W")
    cpu = time.process_time() - t0
    Abar, Wa = cp.at_atom(W), cp.at_atom(cW)
    zW = F(0) if rWhi <= 0 else cp.dyadic_up(rWhi / (1 + rWhi))
    Lam_lo = max(Wa - Abar * max(rWhi, F(0)), (1 - zW) * Wa)
    rec.update({"status": "CERTIFIED" if sW["certified"] else "SUPERSOLUTION_NOT_CERTIFIED", "eta_W": fs(etaW),
                "check_boxes": sW["boxes"], "cpu_seconds": round(cpu, 2)})
    cert = None
    if sW["certified"]:
        rec.update({"U": fs(Abar), "L": fs(Lam_lo), "C_R_sup_W": fs(sW["w_max_hi"])})
        cert = c1b_make_cert(e, d, BW, W, Abar, latent)
    return {"record": rec, "cert": cert}


# ------------------------------------------------------------------ ladder composition (a0_ladder.compose, R3-R5)
def compose(rungs: list) -> dict:
    """U = min over CERTIFIED upper rungs, L = max over CERTIFIED lower rungs; L > U => INCONSISTENT (no value);
    no certified upper rung => NOT_CERTIFIED. `rungs`: [{certifier, rung, U, L, status_U, status_L}]."""
    Us = [(F(r["U"]), r["rung"], r["certifier"]) for r in rungs if r.get("status_U") == "CERTIFIED" and r.get("U")]
    Ls = [(F(r["L"]), r["rung"], r["certifier"]) for r in rungs if r.get("status_L") == "CERTIFIED" and r.get("L")]
    if not Us:
        return {"status": "NOT_CERTIFIED", "U": None, "L": None, "U_rungs": [], "L_rungs": [], "consistent": None}
    u = min(x[0] for x in Us)
    lo = max(x[0] for x in Ls) if Ls else None
    consistent = (lo is None) or (lo <= u)
    return {"status": "CERTIFIED" if consistent else "INCONSISTENT", "U": fs(u) if consistent else None,
            "L": (fs(lo) if lo is not None else None) if consistent else None,
            "U_rungs": [f"{c}:{r}" for (v, r, c) in Us if v == u], "L_rungs": [f"{c}:{r}" for (v, r, c) in Ls if v == lo],
            "consistent": consistent}


# ------------------------------------------------------------------ in-process re-check by the PINNED checkers
def pinned_recheck(cert: dict, c1b: dict | None, c2b: dict | None, guard) -> dict:
    """a0_verify.verify_certificate without the research drift declaration (the guard is the formal one). NOT the
    independent verification (that is vd_verify, D5); a same-implementation re-check of a stored certificate."""
    kind = cert.get("certifier")
    e = F(cert["drift"])
    guard.guard_drift(e)
    claim = F(cert["claim_w_atom"])
    if kind in ("C2B_P1_SUPER", "C2B_P1_SUB"):
        try:
            W = [[int(x) for x in col] for col in cert["W"]]
        except (TypeError, ValueError):
            return {"verdict": "FAIL", "reason": "W_NOT_INTEGER"}
        if c2b_w_sha256(W) != cert["W_sha256"]:
            return {"verdict": "FAIL", "reason": "W_SHA256_MISMATCH"}
        if cert.get("kind") != "whole":
            return {"verdict": "FAIL", "reason": "KIND_NOT_WHOLE"}
        EX = c2b["c2b_exact"]
        S = EX.Setup(int(cert["N"]), e)
        if len(W) != len(S.mesh.cols) or any(len(W[i]) != c for i, c in enumerate(S.mesh.cols)):
            return {"verdict": "FAIL", "reason": "W_SHAPE_MISMATCH"}
        Qb = int(cert["Qbits"])
        res = EX.certify(S, W, Qb, True) if kind == "C2B_P1_SUPER" else sub_certify(EX, S, W, Qb, True)
        if not res["certified"]:
            return {"verdict": "FAIL", "reason": "CERTIFICATE_INEQUALITY_NOT_CERTIFIED"}
        if F(res["w_atom"]) != claim:
            return {"verdict": "FAIL", "reason": "CLAIM_MISMATCH"}
        return {"verdict": "PASS", "certifier": kind, "drift": fs(e), "bound": fs(claim),
                "direction": "upper" if kind == "C2B_P1_SUPER" else "lower"}
    if kind == "C1B_PW_W_SUPER":
        Wser = cert["W"]
        if c1b_w_sha256(Wser) != cert["W_sha256"]:
            return {"verdict": "FAIL", "reason": "W_SHA256_MISMATCH"}
        cp, PW = c1b["c1b_certpw"], c1b["c1b_pw"]
        if tuple(cert["BW"]) != tuple(PW.BW_PW) or len(Wser) != len(PW.BW_PW) - 1:
            return {"verdict": "FAIL", "reason": "BW_OR_SHAPE_MISMATCH"}
        W = [poly_de(L) for L in Wser]
        lines: list = []
        cx = cp.Ctx(e, PW.BW_PW, lines.append)
        try:
            sW = cp.check_supersolution(cx, W, True, "W")
        except ValueError:
            return {"verdict": "FAIL", "reason": "CHECKER_REFUSED_INPUT"}
        if not sW["certified"]:
            return {"verdict": "FAIL", "reason": "CERTIFICATE_INEQUALITY_NOT_CERTIFIED"}
        if cp.at_atom(W) != claim:
            return {"verdict": "FAIL", "reason": "CLAIM_MISMATCH"}
        return {"verdict": "PASS", "certifier": kind, "drift": fs(e), "bound": fs(claim), "direction": "upper"}
    return {"verdict": "FAIL", "reason": "UNKNOWN_CERTIFIER"}
