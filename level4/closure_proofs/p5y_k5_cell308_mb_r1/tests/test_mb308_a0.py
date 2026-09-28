"""QC06: the pointwise-ladder certifiers through the FORMAL path (mb308_a0core + pinned C2b / C1b + mb308_guard in
DECOY mode), at declared validation drifts outside the band (3, 27/10, 11/10). REVIEW_A0_CERTIFIER_R1 C1 and C6.

  C1      byte identity. Certificates produced by mb308_a0core must equal, byte for byte (json indent=1,
          sort_keys, as stream A0 wrote them), the persisted stream-A0 certificates in `streams/A0/certs`. Each file
          is first re-hashed against `CERTS_MANIFEST.json`. Cases:
          * e = 3: C2b N = 20 super and sub (detA);
          * e = 3: C1b d = 8 (detA);
          * e = 11/10: C2b N = 20 super and sub (the non-dyadic lattice path).
  C6(i)   FD check of the pinned c2b_exact.hessian_bounds over EVERY cell kind (L, U, AXP, AXM; cells with s < 1
          counted) at the ladder mesh N = 20.
          * Inputs: a ROUGH W (seeded random nodal integers) at drift 27/10.
          * Method: central second differences of Psi(s, y) = (K_e w)(p, m), with s = p + m and y = p - K - e
            (STRATEGY s5), computed by the reviewer's independent FLOAT evaluator. That evaluator is
            reviews/scratch_A0_R1/r_eval.py, executed from its committed bytes (sha256 pinned below).
          * Pass: no FD value exceeds its bound beyond float noise, at both step sizes.
          * Control: the bounds scaled by 1/2 must be exceeded somewhere.
  C6(ii)  err-path controls in BOTH directions (the reviewer's design, r_a2a5.py lines 103-124).
          * Candidate: t * W_sub, with the smallest t (super) or the largest t (sub) whose vertex margins are >= 0.
          * The candidate must be vertex-acceptable, the formal re-check (mb308_a0core.pinned_recheck) must FAIL,
            and the float interior scan must find a negative residual (a confirmed interior violation; float
            evidence only).
  C6(iii) direction swaps.
          * Super W relabelled SUB must FAIL, and sub W relabelled SUPER must FAIL.
          * The N = 40 reference rung proves both invalid: U(20) > U(40) and L(20) < L(40).
  C6(iv)  vertex-enclosure agreement at 27/10.
          * The float evaluator must lie inside the pinned rigorous [K_lo, K_up] at every node.
          * Negative control: the evaluator at drift 3 must lie outside.
Only equality booleans, counts, signs and ratios are returned; no Lambda value is reported.
"""
from __future__ import annotations

import copy
import hashlib
import json
import math
import random
import subprocess
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve()
REPO = HERE.parents[4]
RS = "level4/closure_proofs/p5y_k5_cell308_research/"
A0_CERTS = REPO / RS / "streams/A0/certs"
R_EVAL_PIN = (RS + "reviews/scratch_A0_R1/r_eval.py",
              "2fdfe516ceb137f23658d5b0156ed88bdc41602f268e015923e77514eb8dd789", None)
BYTE_CASES = (("3", "C2B", 20, "C2BX_SUPER_e3_N20_detA.json", "C2BX_SUB_e3_N20_detA.json"),
              ("3", "C1B", 8, "C1B_SUPER_e3_d8_detA.json", None),
              ("11/10", "C2B", 20, "C2BX_SUPER_e11_10_N20.json", "C2BX_SUB_e11_10_N20.json"))


def a0_bytes(obj: dict) -> bytes:
    return (json.dumps(obj, indent=1, sort_keys=True) + "\n").encode()


def byte_identity(A0C, c1b, c2b, guard, set_flags) -> dict:
    man_path = A0_CERTS / "CERTS_MANIFEST.json"
    if not man_path.exists():
        return {"pass": False, "reason": "stream-A0 certificates absent (untracked in git; see N8)"}
    man = json.loads(man_path.read_text())["files"]
    rows = []
    for e, kind, rung, f_sup, f_sub in BYTE_CASES:
        e = F(e)
        if kind == "C2B":
            r = A0C.c2bx_rung(c2b, guard, e, rung)
            got = {f_sup: r["certs"].get("super"), f_sub: r["certs"].get("sub")}
        else:
            set_flags(c1b, True, False)
            r = A0C.c1b_w_rung(c1b, guard, e, rung)
            got = {f_sup: r["cert"]}
        for fname, cert in got.items():
            raw = (A0_CERTS / fname).read_bytes()
            ok_hash = hashlib.sha256(raw).hexdigest() == man[fname]["sha256"]
            rel = str((A0_CERTS / fname).relative_to(REPO))
            head = subprocess.run(["/usr/bin/git", "-C", str(REPO), "rev-parse", f"HEAD:{rel}"], capture_output=True,
                                  text=True).stdout.strip()
            ok_blob = head == hashlib.sha1(b"blob %d\0" % len(raw) + raw).hexdigest()
            rows.append({"file": fname, "manifest_sha256_ok": ok_hash, "committed_blob_ok": ok_blob,
                         "byte_identical": cert is not None and a0_bytes(cert) == raw})
    return {"rows": rows, "pass": bool(rows) and all(x["manifest_sha256_ok"] and x["committed_blob_ok"]
                                                     and x["byte_identical"] for x in rows)}


# ------------------------------------------------------------------ the reviewer's float evaluator (pinned bytes)
def load_r_eval(PIN):
    return PIN.exec_pinned(REPO, "mb308_qc06_r_eval", R_EVAL_PIN, allow_uncommitted=True, register=True)


def fd_check(EX, EV, guard, e: F, N: int = 20, stride: int = 1, seed: int = 20260929, W=None, Qb: int = 20,
             points=("c",)) -> dict:
    """C6(i): |FD second differences| <= hessian_bounds over every cell kind at point drift e. W: nodal integers at
    scale 2^-Qb (default: a ROUGH seeded random W). points: sample points per 2-D cell ('c' centroid, 'v0'..'v2' near
    each vertex)."""
    guard.guard_drift(e)
    S = EX.Setup(N, e)
    rng = random.Random(seed)
    if W is None:
        W = [[rng.randint(0, 10 << Qb) for _ in range(c)] for c in S.mesh.cols]
    Hb = EX.hessian_bounds(S, W, True)
    scale = 2.0 ** -(EX.P + Qb)
    ev = EV.P1([[x * 2.0 ** -Qb for x in col] for col in W], N)
    ef, K, h = float(e), 0.5, 1.0 / N

    def psi(s, y):
        p = y + K + ef
        return ev.Kw(ef, p, s - p)

    counts, exceed, half_flag, worst = {}, 0, 0, 0.0
    for idx, (cell, jj, je, Hss, Hsy, Hyy, err) in enumerate(Hb):
        kind, i, j, n_s = cell[0], cell[1], cell[2], cell[3]
        if stride > 1 and kind in ("L", "U") and idx % stride and n_s >= N:
            continue
        key = kind + ("_s<1" if n_s < N else "")
        counts[key] = counts.get(key, 0) + 1
        B = {"ss": Hss * scale, "sy": Hsy * scale, "yy": Hyy * scale}
        if kind in ("L", "U"):
            vs = cell[8]
            bary = {"c": (1 / 3, 1 / 3, 1 / 3), "v0": (0.7, 0.15, 0.15), "v1": (0.15, 0.7, 0.15), "v2": (0.15, 0.15, 0.7)}
            fds_all = []
            for pt in points:
                lam = bary[pt]
                p0 = sum(l_ * v[0] for l_, v in zip(lam, vs)) * h
                m0 = sum(l_ * v[1] for l_, v in zip(lam, vs)) * h
                s0, y0 = p0 + m0, p0 - K - ef
                fds = []
                for d in (h / 64, h / 128):
                    c = psi(s0, y0)
                    fss = (psi(s0 + d, y0) - 2 * c + psi(s0 - d, y0)) / d ** 2
                    fyy = (psi(s0, y0 + d) - 2 * c + psi(s0, y0 - d)) / d ** 2
                    fsy = (psi(s0 + d, y0 + d) - psi(s0 + d, y0 - d) - psi(s0 - d, y0 + d)
                           + psi(s0 - d, y0 - d)) / (4 * d * d)
                    fds.append({"ss": fss, "sy": fsy, "yy": fyy})
                fds_all.append(fds)
            comps = ("ss", "sy", "yy")
            bound = B
        else:                                            # axis cells: second derivative along the axis
            fds_all, fds = None, []
            for d in (h / 32, h / 64):
                if kind == "AXP":
                    q0 = (i + 0.5) * h
                    g = lambda t: ev.Kw(ef, t, 0.0)      # noqa: E731
                else:
                    q0 = (j + 0.5) * h
                    g = lambda t: ev.Kw(ef, 0.0, t)      # noqa: E731
                fds.append({"ax": (g(q0 + d) - 2 * g(q0) + g(q0 - d)) / d ** 2})
            comps = ("ax",)
            bound = {"ax": B["ss"] + 2 * B["sy"] + B["yy"] if kind == "AXP" else B["ss"]}
            fds_all = [fds]
        for fds in fds_all:
            for c in comps:
                tol = 1e-6 * (1.0 + bound[c])
                val = min(abs(fds[0][c]), abs(fds[1][c]))
                if val > bound[c] + tol:
                    exceed += 1
                if val > 0.5 * bound[c] + tol:
                    half_flag += 1
                if bound[c] > 0:
                    worst = max(worst, val / bound[c])
    kinds_ok = all(k in counts for k in ("L", "U", "AXP", "AXM")) and any(k.endswith("s<1") for k in counts)
    return {"drift": str(e), "N": N, "cells_checked": counts, "points": list(points), "exceedances": exceed,
            "max_fd_over_bound": round(worst, 4), "half_bound_flags": half_flag, "kinds_ok": kinds_ok}


def fd_package(EX, EV, c2b, guard, e: F, N: int = 20, stride: int = 4) -> dict:
    """C6(i): a ROUGH W over every cell (coverage; 0 exceedances), and the SMOOTH proposal W (the pinned C2b
    proposal g at e, where the bounds are sharp) at four points per sampled cell: 0 exceedances, and the x0.5 bound
    control must fire (a check that can fail)."""
    rough = fd_check(EX, EV, guard, e, N, 1)
    CE = c2b["c2b_certify"]
    g, _ = CE.proposal(N, e, e, "whole")
    smooth = fd_check(EX, EV, guard, e, N, stride, W=CE._dyadic(g), Qb=CE.Q, points=("c", "v0", "v1", "v2"))
    return {"rough_W": rough, "smooth_W": smooth,
            "pass": rough["kinds_ok"] and smooth["kinds_ok"] and rough["exceedances"] == 0
            and smooth["exceedances"] == 0 and smooth["half_bound_flags"] > 0}


def _plant(A0C, base: dict, W, Qbits: int, certifier=None) -> dict:
    c = copy.deepcopy(base)
    c["W"] = [[str(x) for x in col] for col in W]
    c["Qbits"] = Qbits
    c["W_sha256"] = A0C.c2b_w_sha256(W)
    c["claim_w_atom"] = A0C.fs(F(W[0][0], 1 << Qbits))
    if certifier:
        c["certifier"] = certifier
    return c


def controls(A0C, EX, EV, c2b, guard, e: F, N: int = 20, refN: int = 40, scan_points: int | None = None) -> dict:
    """C6(ii)-(iv) at drift e (non-dyadic), through mb308_a0core.pinned_recheck (the formal path's checker)."""
    r = A0C.c2bx_rung(c2b, guard, e, N)
    rr = A0C.c2bx_rung(c2b, guard, e, refN)
    sup, sub = r["certs"]["super"], r["certs"]["sub"]
    rsup, rsub = rr["certs"]["super"], rr["certs"]["sub"]
    Ws = [[int(x) for x in col] for col in sup["W"]]
    Wl = [[int(x) for x in col] for col in sub["W"]]
    Qs, Ql = int(sup["Qbits"]), int(sub["Qbits"])
    chk = lambda c: A0C.pinned_recheck(c, None, c2b, guard)["verdict"]   # noqa: E731
    out = {"stored_like_super_PASS": chk(sup) == "PASS", "stored_like_sub_PASS": chk(sub) == "PASS",
           "reference_nested": F(rsup["claim_w_atom"]) < F(sup["claim_w_atom"])
           and F(rsub["claim_w_atom"]) > F(sub["claim_w_atom"]) and chk(rsup) == "PASS" and chk(rsub) == "PASS"}
    out["swap_super_W_as_SUB_FAIL"] = chk(_plant(A0C, sup, Ws, Qs, "C2B_P1_SUB")) == "FAIL"
    out["swap_sub_W_as_SUPER_FAIL"] = chk(_plant(A0C, sub, Wl, Ql, "C2B_P1_SUPER")) == "FAIL"
    P = EX.P
    S = EX.Setup(N, e)
    TB = 24
    one_l = 1 << (P + Ql)
    Kup = EX.kernel_nodes(S, Wl, 0, True, upper=True)
    Klo = EX.kernel_nodes(S, Wl, 0, True, upper=False)
    Dmin_up = min((Wl[x[0]][x[1]] << P) - Kup[x] for x in Kup)
    T_up = -((-(one_l << TB)) // Dmin_up)
    Wsup_e = [[T_up * x for x in col] for col in Wl]
    Kup_e = EX.kernel_nodes(S, Wsup_e, 0, True, upper=True)
    vtx_sup = min((Wsup_e[x[0]][x[1]] << P) - (1 << (P + Ql + TB)) - Kup_e[x] for x in Kup_e) >= 0
    Dmax_lo = max((Wl[x[0]][x[1]] << P) - Klo[x] for x in Klo)
    T_lo = (one_l << TB) // Dmax_lo
    Wsub_e = [[T_lo * x for x in col] for col in Wl]
    Klo_e = EX.kernel_nodes(S, Wsub_e, 0, True, upper=False)
    vtx_sub = min((1 << (P + Ql + TB)) + Klo_e[x] - (Wsub_e[x[0]][x[1]] << P) for x in Klo_e) >= 0
    scan_sup = EV.residual_scan(Wsup_e, Ql + TB, N, e, "super", scan_points)
    scan_sub = EV.residual_scan(Wsub_e, Ql + TB, N, e, "sub", scan_points)
    out["errpath_super"] = {"vertex_only_acceptable": vtx_sup,
                            "recheck_FAIL": chk(_plant(A0C, sup, Wsup_e, Ql + TB)) == "FAIL",
                            "interior_violation_float": scan_sup["n_negative"] > 0, "points": scan_sup["points"]}
    out["errpath_sub"] = {"vertex_only_acceptable": vtx_sub,
                          "recheck_FAIL": chk(_plant(A0C, sub, Wsub_e, Ql + TB, "C2B_P1_SUB")) == "FAIL",
                          "interior_violation_float": scan_sub["n_negative"] > 0, "points": scan_sub["points"]}
    sc = 2.0 ** -(P + Ql)
    ev = EV.P1([[x * 2.0 ** -Ql for x in col] for col in Wl], N)
    n_out = n_out_alt = 0
    e_alt = F(3)
    guard.guard_drift(e_alt)
    for (i, j) in S.mesh.nodes:
        k = ev.Kw(float(e), i / N, j / N)
        lo, hi = Klo[(i, j)] * sc, Kup[(i, j)] * sc
        tol = 1e-12 * max(1.0, abs(k))
        n_out += not (lo - tol <= k <= hi + tol)
        k2 = ev.Kw(float(e_alt), i / N, j / N)
        n_out_alt += not (lo - 1e-9 <= k2 <= hi + 1e-9)
    out["vertex_enclosure"] = {"nodes": len(S.mesh.nodes), "outside": n_out, "negative_control_outside": n_out_alt,
                               "pass": n_out == 0 and n_out_alt > len(S.mesh.nodes) // 2}
    flat = [out[k] for k in ("stored_like_super_PASS", "stored_like_sub_PASS", "reference_nested",
                             "swap_super_W_as_SUB_FAIL", "swap_sub_W_as_SUPER_FAIL")]
    flat += list(out["errpath_super"].values())[:3] + list(out["errpath_sub"].values())[:3]
    out["pass"] = all(x is True for x in flat) and out["vertex_enclosure"]["pass"]
    return out


def verifier_controls(A0C, S1M, vf, c1b, c2b, guard, set_flags) -> dict:
    """D5 through the FORMAL verification path (mb308_stage1.c2b_verify / verify_c1b, fixed budgets) at drift 3:
    valid certificates VERIFIED; planted ones (W x 0.97 with its claim, a changed claim, a sub W relabelled super, a
    changed W without a new sha, a certificate relabelled to the smaller drift 1/2) never accepted, rigorous refutations reported as REFUTED."""
    e = F(3)
    ctx = {"vf": vf}
    r = A0C.c2bx_rung(c2b, guard, e, 20)
    sup, sub = r["certs"]["super"], r["certs"]["sub"]
    W = [[int(x) for x in col] for col in sup["W"]]
    Qb = int(sup["Qbits"])
    v = lambda c: S1M.c2b_verify(ctx, c)                                 # noqa: E731
    out = {"c2b_valid": v(sup)["verdict"] == "VERIFIED"}
    out["c2b_x0.97_refuted"] = v(_plant(A0C, sup, [[x * 97 // 100 for x in c] for c in W], Qb))["verdict"] == "REFUTED"
    bad_claim = dict(sup, claim_w_atom=A0C.fs(F(sup["claim_w_atom"]) * F(99, 100)))
    out["c2b_claim_mismatch_refuted"] = v(bad_claim)["verdict"] == "REFUTED"
    Ws = [[int(x) for x in col] for col in sub["W"]]
    out["c2b_sub_W_as_super_not_accepted"] = not v(_plant(A0C, sub, Ws, int(sub["Qbits"]), "C2B_P1_SUPER"))["accepted"]
    tampered = dict(sup, W=[[str(int(x) + (1 if (i, j) == (0, 0) else 0)) for j, x in enumerate(col)]
                            for i, col in enumerate(sup["W"])])
    out["c2b_sha_mismatch_refused"] = v(tampered)["verdict"] == "REFUSED"
    set_flags(c1b, True, False)
    c1 = A0C.c1b_w_rung(c1b, guard, e, 4)["cert"]
    vc = lambda b, c: S1M.verify_c1b(ctx, b, c)                           # noqa: E731
    out["c1b_d4_valid"] = vc(e, c1)["verdict"] == "VERIFIED"
    out["c1b_claim_mismatch_refuted"] = vc(e, dict(c1, claim_w_atom=A0C.fs(F(c1["claim_w_atom"]) * F(99, 100))))[
        "verdict"] == "REFUTED"
    out["c1b_wrong_drift_refused"] = vc(F(7, 2), c1)["verdict"] == "REFUSED"
    relab = dict(c1, drift="1/2")          # invalid by Theorem M: Lambda(1/2) exceeds the e = 3 claim by far
    out["c1b_relabelled_to_smaller_drift_not_accepted"] = not vc(F(1, 2), relab)["accepted"]
    out["pass"] = all(out.values())
    return out


def run(PIN, A0C, c1b, c2b, guard, fd_stride: int = 4, scan_points: int | None = None, byte: bool = True,
        S1M=None, vf=None) -> dict:
    if guard.mode() != "DECOY":
        return {"pass": False, "reason": "DECOY mode required"}
    EV = load_r_eval(PIN)
    EX = c2b["c2b_exact"]
    res = {"C1_byte_identity": byte_identity(A0C, c1b, c2b, guard, PIN.set_c1b_flags) if byte else
           {"pass": False, "skipped": True},
           "C6i_fd": fd_package(EX, EV, c2b, guard, F(27, 10), 20, fd_stride),
           "C6ii_iv_controls": controls(A0C, EX, EV, c2b, guard, F(27, 10), 20, 40, scan_points),
           "D5_verifier_controls": verifier_controls(A0C, S1M, vf, c1b, c2b, guard, PIN.set_c1b_flags)
           if S1M is not None and vf is not None else {"pass": False, "missing": "S1M / verifier"}}
    res["pass"] = all(v.get("pass") is True for v in res.values())
    return res
