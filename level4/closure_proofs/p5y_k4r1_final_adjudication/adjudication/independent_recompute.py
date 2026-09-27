#!/usr/bin/env python3
"""Independent recomputation of the P5Y-K4R1 route-D3 certificates and assembly.

Written by the final adjudicator. Does NOT import any campaign code. Reads the raw
hash-bound source JSONs from a checkout given on the command line (a fresh
--no-local clone at the result commit), recomputes everything in exact rational
arithmetic (fractions.Fraction) and compares with the committed result file.

usage: python3 independent_recompute.py <checkout_root> <out_json>
"""
import hashlib
import json
import sys
from fractions import Fraction as Q

ROOT = sys.argv[1].rstrip("/") + "/"
OUT = sys.argv[2]
NS = "level4/closure_proofs/p5y_k4r1_nearzero_successor/"
SRC = {
    "historical_report": ("level4/closure_proofs/p5y_k4_frozen_execution_r1/evidence/K4_ASSEMBLY_REPORT.json",
                          "83cabce239630d98a842bd9eec32482c7d0720fc86433ef8ee7c658833aef175"),
    "k1": ("level4/closure_proofs/p5y_k5b_k1_premise_binding_audit/result_r1/records/aux5_CUSUM_0_256.json",
           "4f8df44c956309b109e174f7ea15deee39ffad863c459f1656d6e2470a7ff1fb"),
    "slot1": ("level4/closure_proofs/p5y_k5_cusum_first_real_probe_protocol/evidence/slot-1/SCIENTIFIC_RECORD_SEALED.json",
              "cf90f1ea577c09d718adddab9698f8f03995722dae51f68d1fd767e4339f73ae"),
    "text": ("level4/closure_proofs/p5y_k5_remaining_cell_closure/transport_extension/evidence/qualification_r1/TEXT_RESULT.json",
             "cb97cabcc3b5848665584e33ad4207c6d36ce835729725265d585dc8f3ee4f87"),
    "manifest": ("level4/closure_proofs/p5y_k1_cusum_aux5_composite_closure/evidence/closure_r1/COMPOSITE_EXPORT_MANIFEST.json",
                 "29ad1f9bb8630a5f3f9aab74d400d552516f0774a05e2b219d66f38b2da0d334"),
    "attestation": ("level4/closure_proofs/p5y_k1_cusum_aux5_composite_closure/evidence/closure_r1/K4_COMPOSITE_ATTESTATION.json",
                    "039e2e1cbebb9561c177ddca790dbc2c675eafde15553ad4e1282777d9bd8d2c"),
    "result": (NS + "evidence/execution_r1/K4R1_RESULT.json",
               "cbf1332bdf368ceb747128996d057d7e2acb1017325ec47b67bfba92b15fc7e4"),
}
PRODUCER = "3692d0feeaef71365798cd99399fdb6d744573f38d59dba5cfe2e99294f0ae19"

checks = {}
fail = []


def chk(name, cond, detail=None):
    checks[name] = {"pass": bool(cond), "detail": detail}
    if not cond:
        fail.append(name)


def load(key):
    path, sha = SRC[key]
    raw = open(ROOT + path, "rb").read()
    h = hashlib.sha256(raw).hexdigest()
    chk("sha256:" + key, h == sha, h)

    def no_float(o):
        if isinstance(o, float):
            raise ValueError("float in " + key)
        if isinstance(o, dict):
            for v in o.values():
                no_float(v)
        if isinstance(o, list):
            for v in o:
                no_float(v)
    return json.loads(raw), raw


def q(s):
    assert isinstance(s, str), s
    return Q(s)


hist, _ = load("historical_report")
k1, _ = load("k1")
slot1, _ = load("slot1")
text, _ = load("text")
man, _ = load("manifest")
att, _ = load("attestation")
res, _ = load("result")

# ---------------- K1 record identity ----------------
chk("k1.detector", k1["detector"] == "CUSUM")
chk("k1.cell_index", k1["cell_index"] == 0)
chk("k1.producer_identity", k1["producer_identity_hash"] == PRODUCER)
chk("k1.e0_rho", k1["e0"] == ["5083/20000000", "0/1"] and k1["rho"] == ["5083/20000000", "0/1"])
chk("k1.manifest_entry", man["files"].get("k4_records/aux5_CUSUM_0_256.json") == SRC["k1"][1])
_pair0 = att["production_provenance"]["halves"]["predecessor"]["pairs"]["0"]
chk("k1.attestation_pair0", att["producer_identity_hash"] == PRODUCER and att["cells_verified"] == 326
    and att["all_scientific_hashes_verified"] is True and _pair0["cell"] == 0
    and _pair0["record_sha256"] == SRC["k1"][1], _pair0)
E0 = Q(5083, 20000000)
X1 = Q(5083, 10000000)
for mm in ("1", "2", "3", "5"):
    ent = k1["m"][mm]
    chk("k1.m%s.identity" % mm, ent.get("detector") == "CUSUM" and str(ent.get("m")) == mm and ent.get("cell_index") == 0,
        {"detector": ent.get("detector"), "m": ent.get("m"), "cell_index": ent.get("cell_index")})
    D = ent["D_interval"]
    chk("k1.m%s.D_interval_ordered" % mm, q(D["lo"]) <= q(D["hi"]))

# ---------------- slot-1 binding ----------------
sci = slot1["scientific"]
chk("slot1.binding.record_sha", sci["binding"]["record_sha256"] == SRC["k1"][1])
chk("slot1.binding.cell", sci["binding"]["k1_cell_index"] == 0 and sci["binding"]["detector"] == "CUSUM"
    and sci["binding"]["left"] == "0/1" and q(sci["binding"]["right"]) == X1)
chk("slot1.binding.export_manifest", sci["binding"]["export_manifest_sha256"] == SRC["manifest"][1])
chk("slot1.context.point_e", q(sci["context"]["point_e"]) == 0 and q(sci["context"]["x1"]) == X1)
for mm in ("1", "2", "3", "5"):
    ad = sci["addresses"][mm]["address"]
    chk("slot1.address.m" + mm, ad["k1_record_sha256"] == SRC["k1"][1] and q(ad["point_e"]) == 0
        and q(ad["right"]) == X1 and ad["left"] == "0/1" and ad["m"] == int(mm) and ad["detector"] == "CUSUM")
chk("geometry.e0_le_x1", E0 <= X1 and E0 == X1 / 2)
TF = X1 * X1 / 2
for mm in ("1", "2", "3", "5"):
    p = sci["per_m"][mm]
    tf = q(p["transport_factor"])
    L0, U0, L1, U1, M5s = q(p["L0"]), q(p["U0"]), q(p["L1"]), q(p["U1"]), q(p["M5"])
    chk("slot1.m%s.transport" % mm, tf == TF and M5s >= 0 and L0 <= U0 and L1 == L0 - tf * M5s and U1 == U0 + tf * M5s,
        {"tf_eq_x1sq_over_2": tf == TF, "L1_exact": L1 == L0 - tf * M5s, "U1_exact": U1 == U0 + tf * M5s})

# ---------------- T-EXT binding ----------------
chk("text.sealed_record", text["sealed_record_sha256"] == SRC["slot1"][1])
for mm in ("1", "2", "3", "5"):
    chk("text.L0_matches_slot1.m" + mm, q(text["L0"][mm]) == q(sci["per_m"][mm]["L0"]))
    chk("text.sealed_L1_matches_slot1.m" + mm, q(text["sealed_L1"][mm]) == q(sci["per_m"][mm]["L1"]))
row0 = [r for r in text["rows"] if r["cell"] == 0][0]
for mm in ("1", "2", "3", "5"):
    chk("text.hull0_M5_reproduces_slot1.m" + mm, q(row0["M"]["5"][mm]) == q(sci["per_m"][mm]["M5"]))

# ---------------- historical report ----------------
chk("hist.checkpoint", hist["checkpoint_sha256"] == "95b1fd16ac420d6f545cbb2619a6086ced31c6d748a9c801ca7f7c114e77a1e1")
chk("hist.mode", hist["mode"] == "GENUINE" and hist["domain"] == "(0, 2]")
OK_HOW = ("CHAIN_RPRIME_NEGATIVE", "DIRECT_R_NEGATIVE")
residual = {}
assembly = {}
for key, v in hist["per_Dm"].items():
    cells = v["per_cell"]
    idx = [c["index"] for c in cells]
    contiguous = cells[0]["left"] == "0" and all(q(cells[i]["right"]) == q(cells[i + 1]["left"]) for i in range(len(cells) - 1))
    covers = q(cells[-1]["right"]) >= 2
    ordered = idx == list(range(len(cells))) and all(q(c["left"]) < q(c["right"]) for c in cells)
    hows = [c["how"] for c in cells]
    tl = [c["index"] for c in cells if c["how"] == "CERTIFICATE_TOO_LOOSE"]
    other = [c["how"] for c in cells if c["how"] not in OK_HOW + ("CERTIFICATE_TOO_LOOSE",)]
    # recompute each non-residual label against its own recorded numbers
    label_ok = True
    for c in cells:
        if c["how"] == "DIRECT_R_NEGATIVE" and not q(c["R_cell_hi"]) < 0:
            label_ok = False
        if c["how"] == "CHAIN_RPRIME_NEGATIVE" and not q(c["Rprime_cell_hi"]) < 0:
            label_ok = False
    # chain must be a prefix from 0
    chain = [c["index"] for c in cells if c["how"] == "CHAIN_RPRIME_NEGATIVE"]
    chain_prefix = chain == list(range(len(chain)))
    tl_prefix = tl == list(range(len(tl)))
    chk("hist.%s.structure" % key, contiguous and covers and ordered and not other and label_ok and chain_prefix
        and tl == v["too_loose_cells"] and v["counterexample_cells"] == [] and tl_prefix,
        {"cells": len(cells), "contiguous_from_0": contiguous, "last_right": cells[-1]["right"], "too_loose": tl,
         "counterexamples": v["counterexample_cells"], "n_chain": len(chain), "n_direct": hows.count("DIRECT_R_NEGATIVE"),
         "labels_consistent_with_recorded_bounds": label_ok, "chain_is_prefix": chain_prefix})
    if tl:
        a = q(cells[tl[-1]]["right"])
        nxt = cells[tl[-1] + 1]
        residual[key] = {"cells": tl, "a": a, "next_cell": nxt["index"], "next_left": nxt["left"], "next_how": nxt["how"]}
        chk("hist.%s.handoff" % key, q(nxt["left"]) == a and nxt["how"] == "DIRECT_R_NEGATIVE"
            and all(c["how"] in OK_HOW for c in cells[tl[-1] + 1:]))
    assembly[key] = {"covered_up_to": cells[-1]["right"], "too_loose": tl}

chk("residual.universe", sorted(residual) == ["CUSUM|m=2", "CUSUM|m=3", "CUSUM|m=5"]
    and residual["CUSUM|m=2"]["cells"] == [0, 1] and residual["CUSUM|m=3"]["cells"] == [0, 1, 2]
    and residual["CUSUM|m=5"]["cells"] == [0, 1, 2]
    and residual["CUSUM|m=2"]["a"] == Q(10187, 10000000)
    and residual["CUSUM|m=3"]["a"] == Q(957, 625000) and residual["CUSUM|m=5"]["a"] == Q(957, 625000))

# ---------------- certificates ----------------
BIG = Q(1) + Q(1, 2 ** 200)
recomputed = {}
for key, r in residual.items():
    mm = key.split("=")[1]
    a = r["a"]
    rows = [row for row in text["rows"] if q(row["x_hi"]) == a]
    chk("text.hull_unique.%s" % key, len(rows) == 1, len(rows))
    row = rows[0]
    eta = q(row["hull_norms"]["eta"])
    chk("text.hull_eta.%s" % key, a <= eta <= a * BIG, {"eta_minus_a": str(eta - a)})
    chk("text.hull_is_prefix_0_to_a.%s" % key, row["cell"] == r["cells"][-1])
    # monotone: M_n of this hull >= M_n of hull 0 (sanity, not load-bearing)
    D0hi = q(k1["m"][mm]["D_interval"]["hi"])
    L1 = q(sci["per_m"][mm]["L1"])
    U0 = q(sci["per_m"][mm]["U0"])
    M3 = q(row["M"]["3"][mm])
    M5 = q(row["M"]["5"][mm])
    chk("inputs.nonneg_majorants.%s" % key, M3 >= 0 and M5 >= 0)
    G = D0hi - L1 * E0 * E0 / 2
    Tb = U0 + a * a / 2 * M5
    T = min(M3, Tb)
    branch = "M3" if M3 <= Tb else "U0+a^2/2*M5"
    B = G + a * a / 6 * max(T, Q(0))
    rc = res["certificates"][key]
    inp = rc["inputs"]
    same = (q(rc["G"]) == G and q(rc["T"]) == T and q(rc["B"]) == B and rc["G"] == str(G) and rc["T"] == str(T)
            and rc["B"] == str(B) and q(inp["D0_hi"]) == D0hi and q(inp["L1"]) == L1 and q(inp["U0"]) == U0
            and q(inp["M3"]) == M3 and q(inp["M5"]) == M5 and q(inp["e0"]) == E0 and q(inp["x1"]) == X1
            and q(rc["a"]) == a and rc["cells"] == r["cells"] and rc["hull_cell"] == row["cell"]
            and rc["T_branch"] == branch and rc["PASS"] == (B < 0)
            and rc["outcome"] == ("K4R1_CERTIFIED" if B < 0 else "K4R1_CERTIFICATE_TOO_LOOSE"))
    chk("cert.match_result.%s" % key, same)
    chk("cert.B_negative.%s" % key, B < 0)
    recomputed[key] = {
        "a": str(a), "hull_cell": row["cell"], "eta": str(eta),
        "D0_hi": str(D0hi), "L1": str(L1), "U0": str(U0), "M3": str(M3), "M5": str(M5),
        "G": str(G), "T": str(T), "T_branch": branch, "B": str(B),
        "G_approx": "%.12e" % float(G), "T_approx": "%.12e" % float(T), "B_approx": "%.12e" % float(B),
        "M3_approx": "%.6e" % float(M3), "Tb_approx": "%.6e" % float(Tb),
        "B_margin_rel_to_G": "%.6e" % float((B - G) / G),
        "decision": "K4R1_CERTIFIED" if B < 0 else "K4R1_CERTIFICATE_TOO_LOOSE",
    }

# ---------------- assembly ----------------
all_pass = True
asm_out = {}
for key, v in assembly.items():
    if v["too_loose"]:
        ok = recomputed[key]["decision"] == "K4R1_CERTIFIED"
        src = "K4R1 (0,a] + historical [a, end]"
    else:
        ok = True
        src = "INHERITED"
    ok = ok and q(v["covered_up_to"]) >= 2
    all_pass = all_pass and ok
    ra = res["assembly"]["per_Dm"][key]
    chk("assembly.match_result.%s" % key, ra["status"] == ("PASS" if ok else "FAIL")
        and q(ra["covered_up_to"]) == q(v["covered_up_to"]))
    asm_out[key] = {"status": "PASS" if ok else "FAIL", "covered_up_to": v["covered_up_to"], "source": src}
science = "PASS" if all_pass and all(r["decision"] == "K4R1_CERTIFIED" for r in recomputed.values()) else "NOT_CLOSED"
chk("result.science", res["K4R1_SUCCESSOR_SCIENCE"] == science and res["K4R1_COMPLETE_K4_ASSEMBLY"] == ("PASS" if all_pass else "FAIL")
    and res["residual_remaining"] == {} and res["new_real_addresses"] == 0 and res["assembly"]["complete"] is True)

out = {"schema": "final-adjudicator.k4r1.independent-recompute.v1", "all_checks_pass": not fail, "failed": fail,
       "n_checks": len(checks), "checks": checks, "recomputed": recomputed, "assembly": asm_out,
       "K4R1_SUCCESSOR_SCIENCE": science}
open(OUT, "w").write(json.dumps(out, indent=1, sort_keys=True) + "\n")
print("checks", len(checks), "failed", fail)
for k, v in recomputed.items():
    print(k, v["decision"], "G~", v["G_approx"], "T~", v["T_approx"], "B~", v["B_approx"], v["T_branch"])
print("science", science)
