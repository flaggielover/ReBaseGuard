"""Stream A0 task C3: negative / positive controls THROUGH the one verification function a0_verify.verify_certificate.

  python3 -I -B -S a0_controls.py c2b E N E_LOWER E_HIGHER [PREFIX]  controls on {PREFIX}_SUPER/SUB_e{E}_N{N}.json
                                                                  (PREFIX C2B = pinned selection, C2BX = exact scale)
  python3 -I -B -S a0_controls.py c1b E d N_REF E_LOWER [PREFIX [REF]]   controls on {PREFIX}_SUPER_e{E}_d{d}.json
                                                                  (PREFIX C1B or C1BH; REF = C2B or C2BX certs)

Every planted-INVALID control is invalid BY PROOF, established before verification from certified facts only:
  * scaled / atom-node plants: the planted w(a) lies strictly outside a certified bracket [L, U] of Lambda(e) at the
    same drift (L, U themselves re-verified first), so the plant cannot be a supersolution (resp. subsolution);
  * interior-node plant (C2b): an exact LOWER bound of (K_e w)(v) at the planted node v gives w(v) - 1 - K_e w(v) < 0
    rigorously (a pointwise violation witness at a state of R);
  * drift-changed plant: the stored W is re-labelled with another declared drift e' whose certified bracket excludes
    the stored claim (L(e') > U(e) for an upper certificate, U(e') < L(e) for a lower one).
Integrity plants (claim tampered, W changed without re-hashing) must fail on the integrity clauses.
The err-path control (C2b SUPER) is a SENSITIVITY control, not a proven-invalid plant: a candidate accepted by a
vertex-only check (err ignored) that the exact certificate must reject because of its interpolation term.
Output: results/C3_CONTROLS_<certifier>_e<E>_<rung>.json.
"""
from __future__ import annotations

import copy
import json
import sys
import time
from fractions import Fraction as F
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import a0_common as A  # noqa: E402
import a0_verify as V  # noqa: E402


def _load(name):
    return json.loads((A.CERTS / name).read_text())


def _run(label, cert, expect, proof):
    t0 = time.process_time()
    r = V.verify_certificate(cert)
    ok = r["verdict"] == expect
    return {"control": label, "expected": expect, "verdict": r["verdict"], "reason": r.get("reason"),
            "detected_as_expected": ok, "invalidity_proof": proof, "cpu_seconds": round(time.process_time() - t0, 2)}


def _rehash_c2b(cert):
    import a0_c2b as C2
    W = [[int(x) for x in col] for col in cert["W"]]
    cert["W_sha256"] = C2.w_sha256(W)
    cert["claim_w_atom"] = A.fs(F(W[0][0], 1 << int(cert["Qbits"])))
    return cert


def _set_W(cert, W):
    cert["W"] = [[str(x) for x in col] for col in W]
    return _rehash_c2b(cert)


def controls_c2b(e, N, e_lower, e_higher, prefix="C2B"):
    import a0_c2b as C2
    e, e_lower, e_higher = (A.declared_drift(F(x)) for x in (e, e_lower, e_higher))
    t = A.tag
    sup, sub = _load(f"{prefix}_SUPER_e{t(e)}_N{N}.json"), _load(f"{prefix}_SUB_e{t(e)}_N{N}.json")
    rows = [_run("V0_valid_super", sup, "PASS", None), _run("V0_valid_sub", sub, "PASS", None)]
    if not (rows[0]["verdict"] == "PASS" and rows[1]["verdict"] == "PASS"):
        return {"rows": rows, "aborted": "stored certificates do not re-verify"}
    U, L = F(sup["claim_w_atom"]), F(sub["claim_w_atom"])
    Qs, Ql = int(sup["Qbits"]), int(sub["Qbits"])
    Ws = [[int(x) for x in col] for col in sup["W"]]
    Wl = [[int(x) for x in col] for col in sub["W"]]
    # V1 scaled
    s = F(97, 100)
    assert s * U < L, "precondition: 0.97 U < L (certified bracket narrower than 3%)"
    rows.append(_run("V1_super_scaled_0.97", _set_W(copy.deepcopy(sup), [[x * 97 // 100 for x in c] for c in Ws]),
                     "FAIL", "planted w(a) <= 0.97 U < L <= Lambda(e)"))
    s2 = F(103, 100)
    assert s2 * L > U, "precondition: 1.03 L > U"
    rows.append(_run("V1_sub_scaled_1.03", _set_W(copy.deepcopy(sub), [[-((-x * 103) // 100) for x in c] for c in Wl]),
                     "FAIL", "planted w(a) >= 1.03 L > U >= Lambda(e)"))
    # V2 atom node
    W2 = copy.deepcopy(Ws)
    W2[0][0] = (L.numerator << Qs) // L.denominator - 1
    assert F(W2[0][0], 1 << Qs) < L
    rows.append(_run("V2_super_atom_node_lowered_below_L", _set_W(copy.deepcopy(sup), W2), "FAIL",
                     "planted w(a) < L <= Lambda(e)"))
    W2 = copy.deepcopy(Wl)
    W2[0][0] = -((-U.numerator << Ql) // U.denominator) + 1
    assert F(W2[0][0], 1 << Ql) > U
    rows.append(_run("V2_sub_atom_node_raised_above_U", _set_W(copy.deepcopy(sub), W2), "FAIL",
                     "planted w(a) > U >= Lambda(e)"))
    # V2b interior node (N, N) of the super certificate, lowered until an exact pointwise violation witness exists
    EX = A.load_c2b()["c2b_exact"]
    S = EX.Setup(N, e)
    v = (N, N)
    witness = None
    for frac in (F(1, 20), F(1, 10), F(1, 5), F(2, 5)):
        W3 = copy.deepcopy(Ws)
        W3[v[0]][v[1]] = int(W3[v[0]][v[1]] * (1 - frac))
        Klo = EX.kernel_nodes(S, W3, 0, True, upper=False)[v]
        r_up = (W3[v[0]][v[1]] << EX.P) - (1 << (EX.P + Qs)) - Klo       # upper bound of w - 1 - K w at v
        if r_up < 0:
            witness = {"node": list(v), "state_p_m": [A.fs(F(v[0], N)), A.fs(F(v[1], N))], "lowered_by": A.fs(frac),
                       "residual_upper_bound": float(F(r_up, 1 << (EX.P + Qs)))}
            break
    if witness:
        rows.append(_run("V2b_super_interior_node_lowered", _set_W(copy.deepcopy(sup), W3), "FAIL",
                         f"exact witness: w - 1 - K_e w <= {witness['residual_upper_bound']:.3e} < 0 at {witness['state_p_m']}"))
    else:
        rows.append({"control": "V2b_super_interior_node_lowered", "skipped": "no exact witness within the declared fractions"})
    # V3 drift changed (needs certified brackets at the other drifts, re-verified here first)
    lo_sub = _load(f"{prefix}_SUB_e{t(e_lower)}_N{N}.json")
    hi_sup = _load(f"{prefix}_SUPER_e{t(e_higher)}_N{N}.json")
    r_lo, r_hi = V.verify_certificate(lo_sub), V.verify_certificate(hi_sup)
    assert r_lo["verdict"] == "PASS" and r_hi["verdict"] == "PASS"
    L_lower, U_higher = F(lo_sub["claim_w_atom"]), F(hi_sup["claim_w_atom"])
    assert L_lower > U, "precondition: L(e_lower) > U(e)"
    assert U_higher < L, "precondition: U(e_higher) < L(e)"
    c = copy.deepcopy(sup)
    c["drift"] = A.fs(e_lower)
    rows.append(_run(f"V3_super_relabelled_to_e={A.fs(e_lower)}", c, "FAIL",
                     "stored claim U(e) < L(e') <= Lambda(e')"))
    c = copy.deepcopy(sub)
    c["drift"] = A.fs(e_higher)
    rows.append(_run(f"V3_sub_relabelled_to_e={A.fs(e_higher)}", c, "FAIL",
                     "stored claim L(e) > U(e') >= Lambda(e')"))
    # V4 claim tampered, V5 hash tampered
    c = copy.deepcopy(sup)
    c["claim_w_atom"] = A.fs(U - F(1, 1 << Qs))
    rows.append(_run("V4_super_claim_tampered", c, "FAIL", "integrity: claim != exact w(a)"))
    c = copy.deepcopy(sup)
    c["W"][1][0] = str(int(c["W"][1][0]) + 1)
    rows.append(_run("V5_super_W_changed_without_rehash", c, "FAIL", "integrity: sha256"))
    # err-path sensitivity control: t * W_sub with t minimal for vertex-only acceptance
    Mg = EX.margins(S, Wl, Ql, True)[0]          # (W<<P) - one - K_up W  at scale 2^-(P+Ql)
    one = 1 << (EX.P + Ql)
    Dmin = min(m + one for m in Mg.values())      # min_v (W<<P - K_up W)
    TB = 20
    T = -((-(one << TB)) // Dmin)                 # t = T / 2^TB >= one / Dmin
    We = [[T * x for x in col] for col in Wl]
    ce = _set_W(copy.deepcopy(sup), We)
    ce["Qbits"] = Ql + TB
    ce = _rehash_c2b(ce)
    Mv = EX.margins(S, We, Ql + TB, True)[0]
    vertex_only_accepts = min(Mv.values()) >= 0
    row = _run("ERRPATH_vertex_only_acceptable_candidate", ce, "FAIL",
               "SENSITIVITY control (not a proven-invalid plant): vertex margins >= 0, err term must reject")
    row["vertex_only_check_accepts"] = vertex_only_accepts
    row["detected_as_expected"] = row["detected_as_expected"] and vertex_only_accepts
    rows.append(row)
    return {"rows": rows}


def controls_c1b(e, d, N_ref, e_lower, prefix="C1B", ref_prefix="C2B"):
    import a0_c1b as C1
    import a0_c1bh as H
    e, e_lower = A.declared_drift(F(e)), A.declared_drift(F(e_lower))
    t = A.tag
    sup = _load(f"{prefix}_SUPER_e{t(e)}_d{d}.json")
    rows = [_run("V0_valid_super", sup, "PASS", None)]
    if rows[0]["verdict"] != "PASS":
        return {"rows": rows, "aborted": "stored certificate does not re-verify"}
    subref = _load(f"{ref_prefix}_SUB_e{t(e)}_N{N_ref}.json")
    assert V.verify_certificate(subref)["verdict"] == "PASS"
    U, L = F(sup["claim_w_atom"]), F(subref["claim_w_atom"])
    M = A.load_c1b()
    cp = M["c1b_certpw"]
    W = [C1.poly_de(Lp) for Lp in sup["W"]]

    def planted(Wn):
        c = copy.deepcopy(sup)
        c["W"] = [C1.poly_ser(P) for P in Wn]
        c["W_sha256"] = C1.w_sha256(c["W"])
        c["claim_w_atom"] = A.fs(cp.at_atom(Wn))
        return c

    s = min(F(int(F(97, 100) * (1 << 20)), 1 << 20), F(int(L / U * (1 << 20)) - 1, 1 << 20))   # dyadic (C1b grid)
    assert s * U < L
    rows.append(_run(f"V1_super_scaled_{float(s):.6f}", planted(cp.wscale(W, s)), "FAIL",
                     "planted w(a) = s U < L (C2b subsolution, re-verified) <= Lambda(e)"))
    W2 = copy.deepcopy(W)
    W2[0][(0, 0, 0)] = W2[0].get((0, 0, 0), F(0)) - (U - L) - F(1, 1 << 20)
    assert cp.at_atom(W2) < L
    rows.append(_run("V2_super_constant_coefficient_strip1_lowered", planted(W2), "FAIL",
                     "planted w(a) < L <= Lambda(e)"))
    lo_sub = _load(f"{ref_prefix}_SUB_e{t(e_lower)}_N{N_ref}.json")
    assert V.verify_certificate(lo_sub)["verdict"] == "PASS"
    assert F(lo_sub["claim_w_atom"]) > U, "precondition: L(e_lower) > U(e)"
    c = copy.deepcopy(sup)
    c["drift"] = A.fs(e_lower)
    try:
        c["hull"] = [A.fs(x) for x in H.hull_of(e_lower)]
        c["certifier"] = "C1B_PW_W_SUPER_HULL"
    except ValueError:                       # dyadic e_lower: pointwise format
        c.pop("hull", None)
        c["certifier"] = "C1B_PW_W_SUPER"
    rows.append(_run(f"V3_super_relabelled_to_e={A.fs(e_lower)}", c, "FAIL", "stored claim U(e) < L(e') <= Lambda(e')"))
    c = copy.deepcopy(sup)
    c["claim_w_atom"] = A.fs(U - F(1, 1 << 40))
    rows.append(_run("V4_super_claim_tampered", c, "FAIL", "integrity: claim != exact w(a)"))
    c = copy.deepcopy(sup)
    c["W"][0][0][3] = A.fs(F(c["W"][0][0][3]) + F(1, 1 << 30))
    rows.append(_run("V5_super_W_changed_without_rehash", c, "FAIL", "integrity: sha256"))
    return {"rows": rows}


def main(argv):
    which = argv[1]
    t0 = time.time()
    if which == "c2b":
        e, N, el, eh = argv[2], int(argv[3]), argv[4], argv[5]
        prefix = argv[6] if len(argv) > 6 else "C2B"
        out = controls_c2b(e, N, el, eh, prefix)
        name = f"C3_CONTROLS_{prefix}_e{A.tag(F(e))}_N{N}.json"
    else:
        e, d, Nref, el = argv[2], int(argv[3]), int(argv[4]), argv[5]
        prefix = argv[6] if len(argv) > 6 else "C1B"
        refp = argv[7] if len(argv) > 7 else "C2B"
        out = controls_c1b(e, d, Nref, el, prefix, refp)
        name = f"C3_CONTROLS_{prefix}_e{A.tag(F(e))}_d{d}.json"
    rows = [r for r in out["rows"] if "skipped" not in r]
    out.update({"schema": "A0_C3_CONTROLS/1", "argv": argv[1:], "n_controls": len(rows),
                "all_as_expected": bool(rows) and all(r["detected_as_expected"] for r in rows) and "aborted" not in out,
                "wall_seconds": round(time.time() - t0, 1), "code": {"a0": A.own_code_sha256()}})
    A.write_json(A.RESULTS / name, out)
    A.ledger("a0_controls.py", f"stream C C3 controls {' '.join(argv[1:])}",
             notes="re-verification controls on stored validation-drift certificates; declared drifts only")
    print(name, "all_as_expected", out["all_as_expected"], flush=True)


if __name__ == "__main__":
    main(list(sys.argv))
