"""Independent reviewer re-derivation of K4 (NOT the frozen tool). Exact Fractions only.

Reads: frozen tables (pristine e5cc5a90 archive), SR sealed cells -> T4 evidence (read-only),
CUSUM k4_records (reviewer's own copy), frozen assembly report (for comparison only).
"""
import hashlib, json, sys, glob
from fractions import Fraction as F
from pathlib import Path

SRC, SR_CELLS, CUSUM_DIR, REPORT, OUT = map(Path, sys.argv[1:6])
L = SRC / "level4/closure_proofs"
TAB_C = L / "p5y_k1_cover_ledger_successor/config/cells.json"
TAB_S = L / "p5y_k1_sr_o9_partition_successor/config/successor_cells.json"
MS = ("1", "2", "3", "5")
PID = "3692d0feeaef71365798cd99399fdb6d744573f38d59dba5cfe2e99294f0ae19"
out = {"problems": []}
P = out["problems"].append


def sha(b):
    return hashlib.sha256(b).hexdigest()


def pair(x):
    return (F(x[0]), F(x[1]))


out["table_sha256"] = {"cusum": sha(TAB_C.read_bytes()), "sr": sha(TAB_S.read_bytes())}
tc = [c for c in json.loads(TAB_C.read_text()) if c["detector"] == "CUSUM"]
ts = json.loads(TAB_S.read_text())["cells"]
out["table_counts"] = {"cusum_rows": len(tc), "sr_rows": len(ts)}


def domain(tab):
    d = []
    for c in tab:
        l, r, e0, rho = pair(c["left"]), pair(c["right"]), pair(c["e0"]), pair(c["rho"])
        if l[1] or r[1] or e0[1] or rho[1]:
            continue  # symbolic c_SR-dependent cell
        if e0[0] - rho[0] != l[0] or e0[0] + rho[0] != r[0]:
            P(f"table geometry inconsistent at {c['index']}")
        if l[0] < 2 and r[0] > 0:
            d.append((c["index"], l[0], r[0], e0[0], rho[0]))
        elif l[0] == 2:
            out.setdefault("cells_with_left_eq_2", []).append(c["index"])
    d.sort(key=lambda t: t[1])
    idx = [t[0] for t in d]
    contig = d[0][1] == 0 and all(a[2] == b[1] for a, b in zip(d, d[1:])) and d[-1][2] >= 2
    return d, {"n": len(d), "indices_min_max": [min(idx), max(idx)], "contiguous_indices": idx == list(range(len(idx))),
               "geometric_contiguous_0_to_ge2": contig, "last_right": str(d[-1][2])}


dc, out["domain_cusum"] = domain(tc)
ds, out["domain_sr"] = domain(ts)


def canon(o):
    return (json.dumps(o, sort_keys=True, separators=(",", ":"), ensure_ascii=True) + "\n").encode()


# ---- SR records through sealed cells
sr = {}
for p in sorted(SR_CELLS.glob("[0-9][0-9][0-9][0-9].json")):
    s = json.loads(p.read_bytes())
    ev = s["evidence"]["t4"]
    b = Path(ev["path"]).read_bytes()
    if sha(b) != ev["sha256"]:
        P(f"SR {p.name} t4 file hash drift")
    t = json.loads(b)
    if t["cell"] != s["cell_id"] or int(p.stem) != s["cell_id"]:
        P(f"SR {p.name} identity")
    body = {k: v for k, v in t.items() if k != "t4_record_sha256"}
    if sha(canon(body)) != t["t4_record_sha256"]:
        P(f"SR {p.name} t4_record_sha256")
    sr[t["cell"]] = t
out["sr_records"] = len(sr)
# ---- CUSUM records
cu = {}
names = sorted(x.name for x in CUSUM_DIR.iterdir())
out["cusum_dir_entries"] = len(names)
out["cusum_hidden_or_nonjson"] = [n for n in names if n.startswith(".") or not n.endswith(".json")]
for n in names:
    r = json.loads((CUSUM_DIR / n).read_bytes())
    if r.get("producer_identity_hash") != PID or r.get("producer", {}).get("producer_identity_hash") != PID:
        P(f"CUSUM {n} producer identity")
    if r["detector"] != "CUSUM":
        P(f"CUSUM {n} detector")
    cu[r["cell_index"]] = r
out["cusum_records"] = len(cu)
out["cusum_indices_exact_0_325"] = sorted(cu) == list(range(326))
out["sr_indices_exact_0_368"] = sorted(sr) == list(range(369))


def enc(e, rho):
    Rl, Rh = F(e["R_interval"]["lo"]), F(e["R_interval"]["hi"])
    Dl, Dh = F(e["D_interval"]["lo"]), F(e["D_interval"]["hi"])
    M = F(e["M_R2"])
    assert Rl <= Rh and Dl <= Dh and M >= 0
    mag = max(-Dl, Dh, Dl, -Dh)
    rem = rho * mag + rho * rho * M / 2
    return {"Rl": Rl, "Rh": Rh, "Dl": Dl, "Dh": Dh, "M": M, "Rc_hi": Rh + rem, "Rc_lo": Rl - rem,
            "Rp_hi": Dh + rho * M, "Rp_lo": Dl - rho * M, "rhoM": rho * M}


rep = json.loads(REPORT.read_text())
res = {}
aux = {"M_R2_ne_R2mag": 0, "Dmag_field_ne_max_abs": 0, "floats_in_certified_fields": 0}
for det, dom, recs in (("CUSUM", dc, cu), ("SR", ds, sr)):
    for (i, l, r, e0, rho) in dom:
        rec = recs.get(i)
        if rec is None:
            P(f"{det} missing record {i}")
            continue
        if pair(rec["e0"]) != (e0, 0) or pair(rec["rho"]) != (rho, 0):
            P(f"{det} {i} e0/rho differs from frozen table")
        if set(rec["m"]) != set(MS):
            P(f"{det} {i} m scope {sorted(rec['m'])}")
        for m in MS:
            if rec["m"][m].get("detector") != det:
                P(f"{det} {i} m={m} detector {rec['m'][m].get('detector')}")
    for m in MS:
        cells = []
        for (i, l, r, e0, rho) in dom:
            e = recs[i]["m"][m]
            for k in ("R_interval", "D_interval"):
                for s in ("lo", "hi"):
                    if isinstance(e[k][s], float):
                        aux["floats_in_certified_fields"] += 1
            if isinstance(e["M_R2"], float):
                aux["floats_in_certified_fields"] += 1
            if "R2_interval" in e and F(e["M_R2"]) != F(e["R2_interval"]["mag"]):
                aux["M_R2_ne_R2mag"] += 1
            if "mag" in e["D_interval"] and F(e["D_interval"]["mag"]) != max(abs(F(e["D_interval"]["lo"])), abs(F(e["D_interval"]["hi"]))):
                aux["Dmag_field_ne_max_abs"] += 1
            cells.append((i, l, r, rho, enc(e, rho)))
        # chain length = number of leading cells with Rprime_cell.hi < 0
        k = 0
        while k < len(cells) and cells[k][4]["Rp_hi"] < 0:
            k += 1
        hows, loose, cex = [], [], []
        for j, (i, l, r, rho, c) in enumerate(cells):
            if j < k:
                h = "CHAIN_RPRIME_NEGATIVE"
            elif c["Rl"] > 0:
                h = "MATHEMATICAL_COUNTEREXAMPLE"; cex.append(i)
            elif c["Rc_hi"] < 0:
                h = "DIRECT_R_NEGATIVE"
            else:
                h = "CERTIFICATE_TOO_LOOSE"; loose.append(i)
            hows.append((i, h, c))
        any_Rlo_pos = [i for (i, l, r, rho, c) in cells if c["Rl"] > 0]
        outcome = ("K4_MATHEMATICAL_COUNTEREXAMPLE" if cex else "K4_CERTIFICATE_TOO_LOOSE" if loose
                   else "K4_CELLWISE_ALL_CERTIFIED")
        key = f"{det}|m={m}"
        fr_ = rep["per_Dm"][key]
        same_cells = [(pc["index"], pc["how"], pc["R_cell_hi"], pc["Rprime_cell_hi"]) for pc in fr_["per_cell"]] == \
                     [(i, h, str(c["Rc_hi"]), str(c["Rp_hi"])) for (i, h, c) in hows]
        chain_end = cells[k - 1][2] if k else F(0)
        direct = [(i, c) for (i, h, c) in hows if h == "DIRECT_R_NEGATIVE"]
        worst_direct = max(direct, key=lambda t: t[1]["Rc_hi"]) if direct else None
        cross2 = [x for x in cells if x[1] < 2 <= x[2]]
        det_cells = {}
        pick = {0, 1, 2, 3, max(k - 1, 0), k, k + 1, len(cells) - 1}
        for j in sorted(p for p in pick if 0 <= p < len(cells)):
            i, l, r, rho, c = cells[j]
            det_cells[str(i)] = {"left": str(l), "right": str(r), "how": hows[j][1],
                                 "R_lo": str(c["Rl"]), "R_hi": str(c["Rh"]), "D_lo": str(c["Dl"]), "D_hi": str(c["Dh"]),
                                 "M_R2": str(c["M"]), "rho": str(rho), "rho_M": float(c["rhoM"]),
                                 "Rprime_cell_hi": str(c["Rp_hi"]), "Rprime_cell_hi_float": float(c["Rp_hi"]),
                                 "R_cell_hi": str(c["Rc_hi"]), "R_cell_hi_float": float(c["Rc_hi"]),
                                 "Rprime_cell_strictly_negative": c["Rp_hi"] < 0, "R_cell_strictly_negative": c["Rc_hi"] < 0,
                                 "R_lo_positive": c["Rl"] > 0}
        res[key] = {"outcome": outcome, "frozen_report_outcome": fr_["outcome"], "outcome_agrees": outcome == fr_["outcome"],
                    "per_cell_byte_agreement_how_Rcellhi_Rprimehi": same_cells, "cells": len(cells),
                    "chain_cells": k, "chain_certifies_up_to": str(chain_end),
                    "chain_agrees": str(chain_end) == fr_["chain_certifies_up_to"],
                    "too_loose_cells": loose, "counterexample_cells": cex, "cells_with_R_lo_gt_0_anywhere": any_Rlo_pos,
                    "worst_direct_cell": worst_direct and {"index": worst_direct[0], "R_cell_hi": float(worst_direct[1]["Rc_hi"])},
                    "cell_crossing_e2": [{"index": x[0], "left": str(x[1]), "right": str(x[2]), "how": hows[cells.index(x)][1],
                                          "R_cell_hi": float(x[4]["Rc_hi"])} for x in cross2],
                    "sampled_cells": det_cells}
out["per_Dm"] = res
out["aux_field_checks"] = aux
out["all_outcomes_agree"] = all(v["outcome_agrees"] and v["per_cell_byte_agreement_how_Rcellhi_Rprimehi"] and v["chain_agrees"]
                                for v in res.values())
OUT.write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
print(json.dumps({"problems": out["problems"][:20], "n_problems": len(out["problems"]), "domain_cusum": out["domain_cusum"],
                  "domain_sr": out["domain_sr"], "all_outcomes_agree": out["all_outcomes_agree"], "aux": aux,
                  "outcomes": {k: (v["outcome"], v["chain_cells"], v["too_loose_cells"], v["counterexample_cells"],
                                   v["cells_with_R_lo_gt_0_anywhere"]) for k, v in res.items()},
                  "left_eq_2": out.get("cells_with_left_eq_2"), "sr": out["sr_records"], "cu": out["cusum_records"],
                  "cu_idx": out["cusum_indices_exact_0_325"], "sr_idx": out["sr_indices_exact_0_368"],
                  "hidden": out["cusum_hidden_or_nonjson"], "tables": out["table_sha256"]}, indent=1))
