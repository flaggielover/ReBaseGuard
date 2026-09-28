"""Stream E (ASSEMBLY), task E5: TPT-B with COMMITTED block constants on real, non-tail lower-front cells (TC path).

Class NONTARGET_REAL_VALIDATION. Addresses: CUSUM cells 11..44, m in {1, 2, 3, 5} (136 pairs), e in [0.0057, 0.0253],
far below the drift band. guard_cell / guard_drift / guard_path run on every pair, block and file.

Data read (and nothing else): p5y_k5_lower_front_order3/evidence/tc_r1/cells/TC_CELL_{11..44}.json,
TC_CONSUMPTION.json (restricted to cells 11..44 in the statement that loads it, as V3 did; its per-cell dicts hold
cells 0..159 only), and the committed operator registry p5y_k5_perron_deflated_resolvent/evidence/registry_r1/
REGISTRY.json (per-block Abar, tau, C_T, D_lo, D1, D2 on e in [0, 0.1147]).

Per pair:
  * committed blocks = the registry blocks meeting the open cell (the r2 rule of the frozen deflated_consume.block_for);
    each block triple = frozen deflated_consume.atom_constants_r2 of that block's constants (min'ed with the cell
    supply); the cell supply S = atom_constants_r2 of the frozen block_for worst case, which must equal the committed
    tc_audit A exactly;
  * reproduction: frozen tc_rule.cell_enclosure(rec, S, m) == committed H_TC, and the profile rebuilt at s = rho from
    the frozen per-r tuple (tc_rule.per_r) == H_TC (G-R1 analogue); M_consumed == mag(H_final) (G-R4);
  * TPT (tpt.py r2), TPT-B with the committed blocks (tptb_tail.check_blocks: exact tiling, A^b <= S), and TPT-B with a
    3-way split of the cell carrying the committed cell triple on every piece (a real-data exercise of the piece logic;
    its P_B must equal P_TPT exactly); independent-integrator gates G-T1/G-T2 and dominance G-D, as in tptb_tail.
Writes validation/LOWER_FRONT_TPTB.json.
"""
from __future__ import annotations

import importlib.util
import json
import sys
import time
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve()


def _load(name, path):
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


TB = _load("c308E_tptb_tail", HERE.parent / "tptb_tail.py")
Q, R, DC, TPT = TB.Q, TB.R, TB.DC, TB.TPT
Q.install_import_guard()
CP = TB.FP.REPO / "level4" / "closure_proofs"
LF = CP / "p5y_k5_lower_front_order3" / "evidence" / "tc_r1"
REG = CP / "p5y_k5_perron_deflated_resolvent" / "evidence" / "registry_r1" / "REGISTRY.json"
CELLS = tuple(range(11, 45))
MS = (1, 2, 3, 5)
OUT = HERE.parent / "validation" / "LOWER_FRONT_TPTB.json"


def load_inputs():
    files, recs = {}, {}
    for k in CELLS:
        Q.guard_cell("CUSUM", 5, k)
        p = LF / "cells" / f"TC_CELL_{k}.json"
        Q.guard_path(p)
        raw = p.read_bytes()
        files[str(p.relative_to(CP))] = TB.hashlib.sha256(raw).hexdigest()
        rec = json.loads(raw)
        if rec.get("cell") != k or rec.get("mode") != "real" or not rec.get("identity_gate", {}).get("identical"):
            raise RuntimeError(f"cell record {k} is not the gated real record of that cell")
        recs[k] = rec
    p = LF / "TC_CONSUMPTION.json"
    Q.guard_path(p)
    raw = p.read_bytes()
    files[str(p.relative_to(CP))] = TB.hashlib.sha256(raw).hexdigest()
    full = json.loads(raw)
    del raw
    cons = {m: {k: {f: full["consumptions"][str(m)]["cells"][str(k)][f] for f in ("R", "D", "H", "M")}
                for k in CELLS} for m in MS}
    audit = {k: {m: full["tc_audit"][str(k)][str(m)] for m in MS} for k in CELLS}
    tc_cells = full["tc_cells"]
    del full
    if sorted(tc_cells) != list(CELLS):
        raise RuntimeError("TC consumption does not list exactly the lower-front cells")
    Q.guard_path(REG)
    raw = REG.read_bytes()
    files[str(REG.relative_to(CP))] = TB.hashlib.sha256(raw).hexdigest()
    reg = json.loads(raw)
    if reg.get("rule") != "r2" or not reg.get("certified"):
        raise RuntimeError("registry r1 is not the certified r2-rule registry")
    return recs, cons, audit, reg, files


def committed_blocks(reg, x_lo, x_hi, S):
    hit = [b for b in reg["blocks"] if F(b["e_lo"]) < x_hi and x_lo < F(b["e_hi"])]
    out = []
    for b in hit:
        lo, hi = max(F(b["e_lo"]), x_lo), min(F(b["e_hi"]), x_hi)
        Q.guard_drift(F(b["e_lo"]), F(b["e_hi"]))
        A = DC.atom_constants_r2(*(F(b[x]) for x in ("Abar", "tau", "C_T", "D_lo", "D1", "D2")))
        out.append({"e_lo": lo, "e_hi": hi, **{j: min(A[j], S[i]) for i, j in enumerate(TB.FIELDS)},
                    "registry_edges_equal_cell": (F(b["e_lo"]), F(b["e_hi"])) == (x_lo, x_hi),
                    "registry_cell": b.get("cell")})
    return out


def run_pair(rec, cons_km, aud_km, reg, k, m) -> dict:
    Q.guard_cell("CUSUM", m, k)
    e0, rho, x_lo, x_hi = (F(rec[x]) for x in ("e0", "rho", "left", "right"))
    Q.guard_drift(x_lo, x_hi)
    if not (e0 - rho == x_lo and e0 + rho == x_hi and x_lo > 0):
        raise RuntimeError("geometry")
    blk = DC.block_for(reg, x_lo, x_hi)
    Sd = DC.atom_constants_r2(blk["Abar"], blk["tau"], blk["C"], blk["Dlo"], blk["D1"], blk["D2"])
    S = tuple(Sd[j] for j in TB.FIELDS)
    row = {"cell": k, "m": m, "S_equals_committed_A": all(Sd[j] == F(aud_km["A"][j]) for j in TB.FIELDS)}
    # frozen TC per-r tuple
    terms = []
    for r in range(m):
        qd = R.per_r(rec, r, Sd)
        o = rec["r"][str(r)]
        terms.append({"fF": qd["fF"], "fD": qd["fD"], "fH": qd["fH"], "fG": qd["fG"], "Env4": qd["env4"],
                      "abs_G": F(o["abs_G_at_a"]), "H_at_a": tuple(F(v) for v in o["H_at_a"]), "half": qd["half"]})
    W = [F(0), F(0)]
    for kind, r, jj, c in R.coefficients(m):
        if kind == "W":
            a, b = (F(v) for v in rec["W2"][f"{r}:{jj}"])
            W[0] += c * a
            W[1] += c * b
    ext = {"terms": terms, "W": tuple(W), "e0": e0, "rho": rho, "x_lo": x_lo, "x_hi": x_hi}
    H_TC = tuple(F(v) for v in aud_km["H_TC"])
    H_fin = tuple(F(v) for v in aud_km["H_final"])
    H_frozen = R.cell_enclosure(rec, Sd, m)
    H_tuple = TB.band_at(ext, S, rho, None)
    row["G-R1"] = H_frozen == H_TC and H_tuple == H_TC and all(
        t["half"] == TB.rad_at(t, S, rho) for t in terms)
    Rr = [F(v) for v in cons_km["R"]]
    Dd = [F(v) for v in cons_km["D"]]
    M_cons = F(cons_km["M"])
    g_hi = Rr[1] - e0 * Dd[0]
    mag = max(abs(H_fin[0]), abs(H_fin[1]))
    row["G-R4"] = M_cons == mag and TB.band_at(ext, S, F(0), H_fin)[0] <= TB.band_at(ext, S, F(0), H_fin)[1]
    if not (row["G-R1"] and row["G-R4"] and row["S_equals_committed_A"]):
        row["status"] = "STOP"
        return row
    cp = TPT.CellProfile(detector="CUSUM", m=m, cell=k, e0=e0, rho=rho, g_hi=g_hi, A0=S[0], A1=S[1], A2=S[2],
                         terms=[TPT.SourceTerm(H_at_a=t["H_at_a"], abs_G_at_a=t["abs_G"], fF=t["fF"], fD=t["fD"],
                                               fH=t["fH"], fG=t["fG"], Env4=t["Env4"]) for t in terms],
                         W=ext["W"], H_K1=H_fin, M_consumed=M_cons)
    P_t = TPT.penalty_closed(cp)["P_star"]
    P_c = TPT.penalty_c5t(cp)
    P_f = TPT.penalty_frozen(cp)
    row["P_frozen_equals_consumed_clause"] = P_f == rho * x_hi * M_cons
    cell_block = [(x_lo, x_hi, S)]
    tol = TB.split_tolerance(ext, S, H_fin, 2)
    row["G-T1"] = TB.transport_gate(P_t, TB.independent_penalty(ext, cell_block, H_fin, 4), tol)["pass"]
    # committed blocks
    cb = committed_blocks(reg, x_lo, x_hi, S)
    row["registry_blocks_hit"] = len(cb)
    row["registry_block_edges_equal_cell"] = all(b["registry_edges_equal_cell"] for b in cb)
    bl = TB.check_blocks([{x: b[x] for x in ("e_lo", "e_hi") + TB.FIELDS} for b in cb], x_lo, x_hi, S)
    P_B = TPT.penalty_blocked(cp, [TPT.Block(e_lo=a, e_hi=b, A0=A[0], A1=A[1], A2=A[2]) for a, b, A in bl])["P_star_B"]
    tolB = TB.split_tolerance(ext, S, H_fin, 2 * len(TB.bl_pieces_hint(ext, bl)))
    row["G-T2_committed"] = TB.transport_gate(P_B, TB.independent_penalty(ext, bl, H_fin, 4), tolB)["pass"]
    row["PB_committed_equals_Ptpt"] = P_B == P_t
    # 3-way split carrying the committed cell triple (valid on every sub-block): piece logic on real data
    ed = [x_lo, x_lo + 2 * rho / 3, x_lo + 4 * rho / 3, x_hi]
    bl3 = TB.check_blocks([{"e_lo": a, "e_hi": b, "A0": S[0], "A1": S[1], "A2": S[2]} for a, b in zip(ed, ed[1:])],
                          x_lo, x_hi, S)
    P_B3 = TPT.penalty_blocked(cp, [TPT.Block(e_lo=a, e_hi=b, A0=A[0], A1=A[1], A2=A[2]) for a, b, A in bl3])["P_star_B"]
    row["G-T2_split3"] = TB.transport_gate(P_B3, TB.independent_penalty(ext, bl3, H_fin, 4),
                                           TB.split_tolerance(ext, S, H_fin, 8))["pass"]
    row["PB_split3_equals_Ptpt"] = P_B3 == P_t
    row["G-D"] = P_B <= P_t <= P_c <= P_f
    row["ratios"] = {"PB_over_Ptpt": float(P_B / P_t), "Ptpt_over_Pc5t": float(P_t / P_c)}
    row["status"] = "OK"
    return row


def main() -> None:
    t0 = time.time()
    recs, cons, audit, reg, files = load_inputs()
    rows = [run_pair(recs[k], cons[m][k], audit[k][m], reg, k, m) for k in CELLS for m in MS]
    ok = [r for r in rows if r["status"] == "OK"]
    summ = {
        "pairs": len(rows), "status_ok": len(ok),
        "S_equals_committed_A": sum(1 for r in rows if r["S_equals_committed_A"]),
        "G-R1_reproduction": sum(1 for r in rows if r["G-R1"]),
        "G-R4": sum(1 for r in rows if r["G-R4"]),
        "P_frozen_equals_consumed_clause": sum(1 for r in ok if r["P_frozen_equals_consumed_clause"]),
        "G-T1": sum(1 for r in ok if r["G-T1"]),
        "registry_blocks_hit_histogram": {str(n): sum(1 for r in ok if r["registry_blocks_hit"] == n)
                                          for n in sorted({r["registry_blocks_hit"] for r in ok})},
        "registry_block_edges_equal_cell": sum(1 for r in ok if r["registry_block_edges_equal_cell"]),
        "G-T2_committed": sum(1 for r in ok if r["G-T2_committed"]),
        "PB_committed_equals_Ptpt": sum(1 for r in ok if r["PB_committed_equals_Ptpt"]),
        "G-T2_split3": sum(1 for r in ok if r["G-T2_split3"]),
        "PB_split3_equals_Ptpt": sum(1 for r in ok if r["PB_split3_equals_Ptpt"]),
        "G-D": sum(1 for r in ok if r["G-D"]),
        "Ptpt_over_Pc5t_range": [min(r["ratios"]["Ptpt_over_Pc5t"] for r in ok),
                                 max(r["ratios"]["Ptpt_over_Pc5t"] for r in ok)],
        "files_sha256": files, "loader_record": TB.FP.record(),
        "code_sha256": {"lower_front_tptb.py": TB.sha256_file(HERE), "tptb_tail.py": TB.sha256_file(HERE.parent / "tptb_tail.py")},
        "wall_s": round(time.time() - t0, 1),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"schema": "C308_STREAM_E_LOWER_FRONT_TPTB/1", "class": "NONTARGET_REAL_VALIDATION",
                               "summary": summ, "rows": rows}, indent=1, default=str))
    Q.log_event("streams/ASSEMBLY/lower_front_tptb.py",
                "E5: TPT-B with committed registry-r1 block constants on lower-front cells 11-44 (TC path)",
                klass="NONTARGET_REAL_VALIDATION", agent="streamE",
                cells_touched=[{"detector": "CUSUM", "m": m, "cell": k} for k in (11, 44) for m in (1, 5)],
                notes="cells 11..44 x m in {1,2,3,5}; e in [0.0057, 0.0253]; no tail cell; cells_touched lists range ends")
    print(json.dumps({k: v for k, v in summ.items() if k not in ("files_sha256", "loader_record")}, indent=1))


if __name__ == "__main__":
    main()
