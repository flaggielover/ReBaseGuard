"""reviewA0 tests for A2 (sub_certify) and A5 (controls through the one verification path).

  python3 -I -B r_a2a5.py E N REF_N [BOUNDARY]
E in the reviewer's declared set; N the rung under test (stored C2BX certificates); REF_N a finer rung whose
re-verified certificates supply the invalidity proofs of the direction-swap plants.  Output: t_a2a5_e<E>_N<N>.json
(pass/fail, counts, signs and relative sizes only).
"""
from __future__ import annotations

import copy
import json
import sys
import time
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import r_common as R  # noqa: E402

sys.path.insert(0, str(R.A0))
import a0_common as A  # noqa: E402
import a0_verify as V  # noqa: E402
import a0_c2b as C2  # noqa: E402
import r_eval as EV  # noqa: E402


def load(name):
    return json.loads((A.CERTS / name).read_text())


def Wof(c):
    return [[int(x) for x in col] for col in c["W"]]


def plant(base, W, Qbits, certifier=None):
    c = copy.deepcopy(base)
    c["W"] = [[str(x) for x in col] for col in W]
    c["Qbits"] = Qbits
    c["W_sha256"] = C2.w_sha256(W)
    c["claim_w_atom"] = A.fs(F(W[0][0], 1 << Qbits))
    if certifier:
        c["certifier"] = certifier
    return c


def main(e_s, N, refN, boundary):
    e = R.rv_drift(e_s)
    t0 = time.time()
    tg = A.tag(e)
    out = {"drift_declared": True, "N": N, "ref_N": refN, "rows": []}

    def row(label, cert, expect, proof):
        r = V.verify_certificate(cert)
        out["rows"].append({"control": label, "expected": expect, "verdict": r["verdict"], "reason": r.get("reason"),
                            "as_expected": r["verdict"] == expect, "invalidity_proof": proof})
        return r

    sup, sub = load(f"C2BX_SUPER_e{tg}_N{N}.json"), load(f"C2BX_SUB_e{tg}_N{N}.json")
    Ws, Wl = Wof(sup), Wof(sub)
    Qs, Ql = int(sup["Qbits"]), int(sub["Qbits"])
    U, L = F(sup["claim_w_atom"]), F(sub["claim_w_atom"])
    # ---- A5: stored certificates re-verify
    row("stored_super_reverify", sup, "PASS", None)
    row("stored_sub_reverify", sub, "PASS", None)
    # ---- reference rung (finer), re-verified, for the invalidity proofs
    rsup, rsub = load(f"C2BX_SUPER_e{tg}_N{refN}.json"), load(f"C2BX_SUB_e{tg}_N{refN}.json")
    r1, r2 = V.verify_certificate(rsup), V.verify_certificate(rsub)
    Uref, Lref = F(rsup["claim_w_atom"]), F(rsub["claim_w_atom"])
    out["ref_reverified"] = [r1["verdict"], r2["verdict"]]
    out["ref_brackets_nested"] = {"U_ref < U": Uref < U, "L_ref > L": Lref > L, "L <= U": L <= U}
    assert r1["verdict"] == "PASS" and r2["verdict"] == "PASS" and Uref < U and Lref > L
    # ---- A5: planted scaled (x 0.97) super, and x 1.03 sub
    row("planted_super_x0.97", plant(sup, [[x * 97 // 100 for x in c] for c in Ws], Qs), "FAIL",
        "0.97 U < L <= Lambda")
    row("planted_sub_x1.03", plant(sub, [[-((-x * 103) // 100) for x in c] for c in Wl], Ql), "FAIL",
        "1.03 L > U >= Lambda")
    # ---- A2: direction swaps (a sign slip in sub_certify that made it a supersolution check would PASS these)
    row("swap_super_W_labelled_SUB", plant(sup, Ws, Qs, "C2B_P1_SUB"), "FAIL",
        "claim U(N) > U(ref) >= Lambda, so w cannot be a subsolution")
    row("swap_sub_W_labelled_SUPER", plant(sub, Wl, Ql, "C2B_P1_SUPER"), "FAIL",
        "claim L(N) < L(ref) <= Lambda, so w cannot be a supersolution")
    # ---- exact vertex data of the pinned evaluator
    M = A.load_c2b()
    EX = M["c2b_exact"]
    P = EX.P
    S = EX.Setup(N, e)
    # ---- err-path controls, both directions (family t * W_sub = t * c * g, vertex residual ~ 0)
    TB = 24
    one_l = 1 << (P + Ql)
    Kup = EX.kernel_nodes(S, Wl, 0, True, upper=True)
    Klo = EX.kernel_nodes(S, Wl, 0, True, upper=False)
    Dmin_up = min((Wl[x[0]][x[1]] << P) - Kup[x] for x in Kup)            # min_v (W - K_up W)
    T_up = -((-(one_l << TB)) // Dmin_up)                               # smallest t = T/2^TB with vertex margins >= 0
    Wsup_e = [[T_up * x for x in col] for col in Wl]
    Kup_e = EX.kernel_nodes(S, Wsup_e, 0, True, upper=True)
    vtx_sup_ok = min((Wsup_e[x[0]][x[1]] << P) - (1 << (P + Ql + TB)) - Kup_e[x] for x in Kup_e) >= 0
    Dmax_lo = max((Wl[x[0]][x[1]] << P) - Klo[x] for x in Klo)            # max_v (W - K_lo W)
    T_lo = (one_l << TB) // Dmax_lo                                     # largest t with vertex defects >= 0
    Wsub_e = [[T_lo * x for x in col] for col in Wl]
    Klo_e = EX.kernel_nodes(S, Wsub_e, 0, True, upper=False)
    vtx_sub_ok = min((1 << (P + Ql + TB)) + Klo_e[x] - (Wsub_e[x[0]][x[1]] << P) for x in Klo_e) >= 0
    r_sup_e = row("ERRPATH_super_vertex_only_acceptable", plant(sup, Wsup_e, Ql + TB), "FAIL",
                  "sensitivity (interior violation checked below by the independent float scan)")
    r_sub_e = row("ERRPATH_sub_vertex_only_acceptable", plant(sub, Wsub_e, Ql + TB, "C2B_P1_SUB"), "FAIL",
                  "sensitivity (interior violation checked below by the independent float scan)")
    out["errpath_vertex_only_accepts"] = {"super": vtx_sup_ok, "sub": vtx_sub_ok}
    # ---- selection boundary (exactness of the a0_c2bx selections against the checkers)
    if boundary:
        rec = json.loads((A.RESULTS / f"C2BX_e{tg}_N{N}.json").read_text())["rung"]
        a_up = F(rec["alpha_up"]) * (1 << 40)
        a_lo = F(rec["c_lo"]) * (1 << 40)
        assert a_up.denominator == 1 and a_lo.denominator == 1
        a_up, a_lo = int(a_up), int(a_lo)
        g = [[x // a_up for x in col] for col in Ws]
        exact_family = all(a_up * gx == wx for cg, cw in zip(g, Ws) for gx, wx in zip(cg, cw)) and \
            all(a_lo * gx == wx for cg, cw in zip(g, Wl) for gx, wx in zip(cg, cw))
        rb_u = EX.certify(S, [[(a_up - 1) * x for x in col] for col in g], Qs, True)
        rb_l = C2.sub_certify(S, [[(a_lo + 1) * x for x in col] for col in g], Ql, True)
        out["selection_boundary"] = {"W_super = a_up g and W_sub = a_lo g exactly": exact_family,
                                     "a_lo <= 2^40 <= a_up": a_lo <= (1 << 40) <= a_up,
                                     "certify(a_up - 1) certified": rb_u["certified"],
                                     "sub_certify(a_lo + 1) certified": rb_l["certified"]}
    # ---- independent float evaluator: node agreement with the pinned rigorous vertex enclosures
    sc = 2.0 ** -(P + Ql)
    ev = EV.P1([[x * 2.0 ** -Ql for x in col] for col in Wl], N)
    ef = float(e)
    worst_rel, n_out = 0.0, 0
    for (i, j) in S.mesh.nodes:
        k = ev.Kw(ef, i / N, j / N)
        lo, hi = Klo[(i, j)] * sc, Kup[(i, j)] * sc
        tol = 1e-12 * max(1.0, abs(k))
        if not (lo - tol <= k <= hi + tol):
            n_out += 1
        worst_rel = max(worst_rel, abs(k - 0.5 * (lo + hi)) / max(1.0, abs(k)))
    # negative control of the node test: my evaluator at a different declared drift
    e_alt = R.rv_drift("3" if e != 3 else "27/10")
    n_out_alt = sum(1 for (i, j) in S.mesh.nodes
                    if not (Klo[(i, j)] * sc - 1e-9 <= ev.Kw(float(e_alt), i / N, j / N) <= Kup[(i, j)] * sc + 1e-9))
    out["node_test"] = {"nodes": len(S.mesh.nodes), "outside_enclosure": n_out, "max_rel_dev_from_mid": worst_rel,
                        "neg_control_other_drift_outside": n_out_alt}
    # ---- independent interior scans
    scans = {}
    scans["stored_super"] = EV.residual_scan(Ws, Qs, N, e, "super")
    scans["stored_sub"] = EV.residual_scan(Wl, Ql, N, e, "sub")
    scans["errpath_super"] = EV.residual_scan(Wsup_e, Ql + TB, N, e, "super")
    scans["errpath_sub"] = EV.residual_scan(Wsub_e, Ql + TB, N, e, "sub")
    for k, v in scans.items():
        v.pop("worst_at", None)
    out["interior_scans"] = scans
    out["all_rows_as_expected"] = all(r["as_expected"] for r in out["rows"])
    out["wall_seconds"] = round(time.time() - t0, 1)
    R.dump(f"t_a2a5_e{tg}_N{N}.json", out)
    R.rv_log("r_a2a5.py", f"REVIEW_A0_CERTIFIER_R1 A2/A5: re-verify, planted, direction-swap, err-path (both "
             f"directions), selection boundary, independent float node/interior scans at e={A.fs(e)} N={N} "
             f"(ref N={refN})", notes="declared reviewer drift; stored A0 certificates read, none written in A0")
    print(json.dumps({k: out[k] for k in ("all_rows_as_expected", "errpath_vertex_only_accepts", "node_test")}
                     | {"selection_boundary": out.get("selection_boundary")}, default=str))
    for k, v in scans.items():
        print(k, v)
    for r in out["rows"]:
        print(r["control"], r["verdict"], r["reason"], r["as_expected"])


if __name__ == "__main__":
    main(sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), len(sys.argv) > 4)
