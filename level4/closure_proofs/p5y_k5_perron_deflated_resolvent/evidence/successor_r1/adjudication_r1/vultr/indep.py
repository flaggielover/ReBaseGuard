"""Adjudicator's independent re-derivation (own code) of the theorem-AD r2 tightened enclosures and the K5-B verdicts.
Uses only: raw K1 records (+ manifest), cells.json, registry_r1 REGISTRY.json, adopted TEXT_RESULT, sealed slot-1 L1,
the frozen k5b_literal (loaded from its pinned bytes). No producer code (deflated_consume / adapter) is imported."""
import hashlib, importlib.util, json, sys
from fractions import Fraction as Fr
from pathlib import Path

REPO = Path("/root/work/k5p-adjudication")
CP = REPO / "level4/closure_proofs"
NS = CP / "p5y_k5_perron_deflated_resolvent"
RECS = Path("/root/work/postk1-runs/closure-r1/COMPOSITE_EXPORT/k4_records")
MS = ("1", "2", "3", "5")
K1B, K2B = Fr(7978846, 10**7), Fr(9678830, 10**7)

def sha(b): return hashlib.sha256(b).hexdigest()
def load(p, pin):
    b = Path(p).read_bytes(); assert sha(b) == pin, (p, sha(b)); return b
def rat(x): return Fr(x) if isinstance(x, str) else Fr(x[0]) + Fr(x[1])

manifest = json.loads(load(CP / "p5y_k1_cusum_aux5_composite_closure/evidence/closure_r1/COMPOSITE_EXPORT_MANIFEST.json",
                           "29ad1f9bb8630a5f3f9aab74d400d552516f0774a05e2b219d66f38b2da0d334"))
cj = json.loads(load(CP / "p5y_k1_cover_ledger_successor/config/cells.json",
                     "341eb5e95161bbdc2d15c1dca72eb8c4565982fab562e1c5a337139375b67c2f"))
reg = json.loads(load(NS / "evidence/registry_r1/REGISTRY.json",
                      "1b7f5da743a2ce0d7f557c2dae054ab358a9175212eaa1fa29dea63a25780cb5"))
text = json.loads(load(CP / "p5y_k5_remaining_cell_closure/transport_extension/evidence/qualification_r1/TEXT_RESULT.json",
                       "cb97cabcc3b5848665584e33ad4207c6d36ce835729725265d585dc8f3ee4f87"))
slot1 = json.loads(load(CP / "p5y_k5_cusum_first_real_probe_protocol/evidence/slot-1/SCIENTIFIC_RECORD_SEALED.json",
                        "cf90f1ea577c09d718adddab9698f8f03995722dae51f68d1fd767e4339f73ae"))
sealed = json.loads(load(NS / "evidence/successor_r1/DEFLATED_CONSUMPTION.json",
                         "5dcc9b7d26c92babbf1b19ad064b29969ea7bd829ea9629004e312520123274a"))
tcons = json.loads(load(CP / "p5y_k5_remaining_cell_closure/transport_extension/evidence/consumption_r1/TEXT_CONSUMPTION.json",
                        "9562eda87a36d22838c65eb281210938e234a8c930e04a946aaf43a5876aa33d"))
kbp = CP / "p5y_k5b_independent_countersignature/code/k5b_check.py"
load(kbp, "ddd54dc469375a2d64352782add8573231be07b94f7246dad83c4e55a2bf35a6")
spec = importlib.util.spec_from_file_location("k5b_frozen_adj", kbp); KB = importlib.util.module_from_spec(spec)
spec.loader.exec_module(KB)

cover = sorted([c for c in cj if c["detector"] == "CUSUM"], key=lambda c: c["index"])
cover = [c for c in cover if rat(c["left"]) < 2]
assert [c["index"] for c in cover] == list(range(310)), len(cover)
assert rat(cover[0]["left"]) == 0 and all(rat(a["right"]) == rat(b["left"]) for a, b in zip(cover, cover[1:]))

records = {}
for c in cover:
    k = c["index"]; name = f"aux5_CUSUM_{k}_256.json"
    b = (RECS / name).read_bytes()
    assert manifest["files"][f"k4_records/{name}"] == sha(b), k
    records[k] = json.loads(b); assert records[k]["cell_index"] == k and records[k]["detector"] == "CUSUM"

L1 = {m: Fr(slot1["scientific"]["per_m"][m]["L1"]) for m in MS}
rows = {int(r["cell"]): r for r in text["rows"]}
def tv(x):  # TEXT_RESULT nested fields may be dicts or python-repr strings
    return x if isinstance(x, dict) else eval(x)
LAM = {m: {k: Fr(tv(rows[k]["Lambda"])[m]) for k in range(1, 41)} for m in MS}
M2 = {m: {k: Fr(tv(tv(rows[k]["M"])["2"])[m]) for k in range(0, 41)} for m in MS}

def src(r, k): return f"Sclosed:{k}" if r == 0 else f"S:{r}:{k}"

def constants(k, x_lo, x_hi):
    bl = [b for b in reg["blocks"] if b["cell"] == k]
    assert len(bl) == 1 and (Fr(bl[0]["e_lo"]), Fr(bl[0]["e_hi"])) == (x_lo, x_hi), k
    b = bl[0]
    # own worst-block rule over the taboo e-blocks meeting the open cell
    hit = [t for t in reg["taboo_blocks"].values() if Fr(t["e_lo"]) < x_hi and x_lo < Fr(t["e_hi"])]
    assert min(Fr(t["e_lo"]) for t in hit) <= x_lo and max(Fr(t["e_hi"]) for t in hit) >= x_hi
    assert Fr(b["tau"]) == max(Fr(t["tau"]) for t in hit) and Fr(b["C_T"]) == max(Fr(t["C_T"]) for t in hit), k
    Ab, tau, C, Dlo, D1, D2 = (Fr(b[x]) for x in ("Abar", "tau", "C_T", "D_lo", "D1", "D2"))
    assert Dlo > 0 and Ab >= 1
    Ae = min(Ab, tau / Dlo); d1, d2 = D1 / Dlo, D2 / Dlo
    A0 = Ae
    A1 = Ae * (K1B * C + d1)
    A2 = Ae * (2 * K1B**2 * C**2 + K2B * C + 2 * K1B * C * d1 + 2 * d1**2 + d2)
    return {"A0": A0, "A1": A1, "A2": A2, "Abar": Ab, "tau_over_Dlo": tau / Dlo, "C": C, "Dlo": Dlo, "D1": D1, "D2": D2}

def radii(rec, A, r):
    o, em, ec = rec["objects"], rec["eps_mid"], rec["eps_cell"]
    fFm = Fr(o[f"F_{r}"]["delta_mid"]) + Fr(em[src(r, 0)])
    fDm = Fr(o[f"dF_{r}"]["delta_mid"]) + Fr(em[src(r, 1)])
    fFc = Fr(o[f"F_{r}"]["delta_cell"]) + Fr(ec[src(r, 0)])
    fDc = Fr(o[f"dF_{r}"]["delta_cell"]) + Fr(ec[src(r, 1)])
    fHc = Fr(o[f"H_{r}"]["delta_cell"]) + Fr(ec[src(r, 2)])
    return {"F": A["A0"] * fFm, "D": A["A0"] * fDm + A["A1"] * fFm,
            "H": A["A0"] * fHc + 2 * A["A1"] * fDc + A["A2"] * fFc, "fFm": fFm, "fDm": fDm}

def build(m, deflate=True, text_c2=True, notes=None):
    mi = int(m); cells = []
    for c in cover:
        k = c["index"]; rec = records[k]; rm = rec["m"][m]
        x_lo, x_hi, e0, rho = rat(c["left"]), rat(c["right"]), rat(c["e0"]), rat(c["rho"])
        assert rat(rm["e0"]) == e0 and rat(rm["rho"]) == rho
        R = [Fr(rm["R_interval"]["lo"]), Fr(rm["R_interval"]["hi"])]
        D = [Fr(rm["D_interval"]["lo"]), Fr(rm["D_interval"]["hi"])]
        H = [Fr(rm["R2_interval"]["lo"]), Fr(rm["R2_interval"]["hi"])]
        M = Fr(rm["M_R2"])
        if deflate and k <= 148:
            A = constants(k, x_lo, x_hi)
            rad = [radii(rec, A, r) for r in range(mi)]
            for X, key, src_eps in ((R, "F", "eps_mid"), (D, "D", "eps_mid"), (H, "H", "eps_cell_refined")):
                erec = [Fr(rec[src_eps][f"{key}:{r}"]) for r in range(mi)]
                need = sum(erec, Fr(0)) / mi
                assert (X[1] - X[0]) / 2 >= need, ("assembly assumption", k, m, key)
                delta = sum((max(Fr(0), erec[r] - rad[r][key]) for r in range(mi)), Fr(0)) / mi
                X[0] += delta; X[1] -= delta
                assert X[0] <= X[1], ("empty", k, m, key)
                if notes is not None:
                    notes.setdefault(k, {})[key] = {"delta": delta, "need": need}
            M = min(M, max(abs(H[0]), abs(H[1])))
            if notes is not None:
                notes[k]["A"] = A; notes[k]["rad"] = rad
        L = L1[m] if k == 0 else None
        if text_c2:
            if 1 <= k <= 40:
                L = LAM[m][k]
            if 0 <= k <= 40:
                b = M2[m][k]
                H = [max(H[0], -b), min(H[1], b)]; assert H[0] <= H[1]
                M = min(M, b)
        cells.append({"x_lo": x_lo, "x_hi": x_hi, "rho": rho, "e0": e0, "R": tuple(R), "D": tuple(D), "H": tuple(H),
                      "M": M, "L": L})
    return cells

def ranges(xs):
    out = []
    for x in xs:
        if out and out[-1][1] == x - 1: out[-1][1] = x
        else: out.append([x, x])
    return out

rep = {"per_m": {}, "compare": {}, "focus": {}, "replay_T_EXT_C2": {}}
FOCUS = (11, 45, 100, 148)
for m in MS:
    # own replay of the adopted T-EXT C2 (no deflation)
    base = KB.k5b_literal(build(m, deflate=False))
    bpass = [i for i, r in enumerate(base) if r["pass"] is True]
    rep["replay_T_EXT_C2"][m] = ranges(bpass) == tcons["consumptions"]["C2"][m]["pass_ranges"]
    notes = {}
    cells = build(m, notes=notes)
    rows_ = KB.k5b_literal(cells)
    passed = [i for i, r in enumerate(rows_) if r["pass"] is True]
    opened = [i for i in range(310) if i not in set(passed)]
    S = sealed["consumptions"][m]
    rep["per_m"][m] = {"pass_ranges": ranges(passed), "open_ranges": ranges(opened),
                       "pass_ranges_equal_sealed": ranges(passed) == S["pass_ranges"],
                       "open_ranges_equal_sealed": ranges(opened) == S["open_ranges"]}
    # per-cell exact comparison with the sealed per-cell enclosures, cells 0..159
    mism = []
    maxrel = Fr(0)
    for i in range(160):
        sc = S["cells"][str(i)]
        mine = {"R": cells[i]["R"], "D": cells[i]["D"], "H": cells[i]["H"]}
        for key in ("R", "D", "H"):
            for j in range(2):
                a, b = mine[key][j], Fr(sc[key][j])
                if a != b:
                    mism.append([i, key, j]); 
                    maxrel = max(maxrel, abs(a - b) / max(abs(a), abs(b)))
        if cells[i]["M"] != Fr(sc["M"]):
            mism.append([i, "M"])
        if i <= 148:
            au = S["audit"][str(i)]
            for key in ("A0", "A1", "A2"):
                if Fr(au[key]) != notes[i]["A"][key]:
                    mism.append([i, "audit", key])
            for r in range(int(m)):
                for t in "FDH":
                    if Fr(au["eps_new"][str(r)][t]) != notes[i]["rad"][r][t]:
                        mism.append([i, "eps_new", r, t])
    rep["compare"][m] = {"mismatches": mism[:20], "n_mismatch": len(mism), "max_rel": float(maxrel)}
    for k in FOCUS:
        rec = records[k]; mi = int(m)
        rm = rec["m"][m]
        n = notes[k]
        rep["focus"].setdefault(str(k), {})[m] = {
            "A0": float(n["A"]["A0"]), "A1": float(n["A"]["A1"]), "A2": float(n["A"]["A2"]),
            "Abar": float(n["A"]["Abar"]), "tau/Dlo": float(n["A"]["tau_over_Dlo"]),
            "rec_R": [float(Fr(rm["R_interval"]["lo"])), float(Fr(rm["R_interval"]["hi"]))],
            "new_R": [float(x) for x in cells[k]["R"]],
            "rec_D": [float(Fr(rm["D_interval"]["lo"])), float(Fr(rm["D_interval"]["hi"]))],
            "new_D": [float(x) for x in cells[k]["D"]],
            "rec_H": [float(Fr(rm["R2_interval"]["lo"])), float(Fr(rm["R2_interval"]["hi"]))],
            "new_H": [float(x) for x in cells[k]["H"]],
            "rec_M": float(Fr(rm["M_R2"])), "new_M": float(cells[k]["M"]),
            "sealed_equal": all(cells[k][key] == tuple(Fr(x) for x in S["cells"][str(k)][key]) for key in ("R", "D", "H"))
                            and cells[k]["M"] == Fr(S["cells"][str(k)]["M"]),
            "Gamma": float(rows_[k]["Gamma"]), "verdict": rows_[k]["pass"], "via": rows_[k]["via"],
            "sealed_via": S["via"][str(k)],
            "sealed_pass": any(a <= k <= b for a, b in S["pass_ranges"]),
            "eps_ratio_F_over_C_fF": [float(Fr(rec["eps_mid"][f"F:{r}"]) / (Fr(rec["C_upper"]) * n["rad"][r]["fFm"])) for r in range(mi)],
            "shrink_share": {key: float(n[key]["delta"] / n[key]["need"]) if n[key]["need"] else None for key in ("F", "D", "H")}}
Path("/var/tmp/k5p-adj/INDEP.json").write_text(json.dumps(rep, indent=1, sort_keys=True, default=str) + "\n")
print(json.dumps({"per_m": rep["per_m"], "compare": rep["compare"], "replay": rep["replay_T_EXT_C2"]}, indent=1))
