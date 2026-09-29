"""A2 cell family end to end (THEOREM_SRK section 11 A3, section 12; review R1 B1/B2 positive control).

For each declared cell of config/SRK_DECOY_DECLARATION_A2.json (non-dyadic endpoints):
  1. sub-block certificates from evidence/srk_decoys_cell/ (weight block = the cell's outward dyadic hull, which is
     STRICTLY larger than each check sub-block: the case review R1 found unverified);
  2. independent-verifier verdicts from verify/VERIFY_RESULTS.json, matched by sha256 (run the verifier first:
     python3 verify/run_verify_all.py --files evidence/srk_decoys_cell/*.json);
  3. srk_gate.gate -> Gamma-bar_i; must be non-None for every declared index and equal max_b of the per-block values;
  4. gate negatives on the REAL certificates: a missing sub-block, a weight block narrowed to the check block (re-hashed
     and given a forged ACCEPT), a REJECT verdict, the wrong kernel, a shifted cell -> each must refuse / give None;
  5. Monte Carlo positive control of the cell-level claim sup_{e in C} (R_e kbar_i^{Ew})(a) <= Gamma-bar_i at
     e in {cell_lo, cell_mid, cell_hi}, weight = 1/32-grid upper envelope of kbar_i^{Ew} (conservative):
     mc - 5 se <= Gamma-bar_i.  Tightness Gamma-bar_i / mc is reported (decoy-only ratio).
Decoy drifts only; the real-geometry cell is far below the band and passes the campaign guard.
"""
import copy
import json
import math
import random
import sys
import zlib
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve().parent
NS = HERE.parent
for p_ in (NS / "impl", NS / "code", HERE):
    sys.path.insert(0, str(p_))
import q309_guard as Q  # noqa: E402
import srk_certify as S  # noqa: E402
import srk_gate as GT  # noqa: E402
from srk_mc_control import he_abs_int, simulate  # noqa: E402


def load(cell_decl):
    h, k = cell_decl["h"], cell_decl["k"]
    c0, c1 = cell_decl["cell"]
    certs = []
    for j in range(S.N_SUB):
        name = f"cell_h{h.replace('/', '_')}_k{k.replace('/', '_')}_C{c0.replace('/', '_')}_{c1.replace('/', '_')}_S{j}.json"
        fp = NS / "evidence" / "srk_decoys_cell" / name
        if fp.exists():
            d = json.loads(fp.read_text())
            certs += [c for c in d["certificates"].values() if c.get("status") == "CERTIFIED"]
    return certs


def verdicts_from_results() -> dict:
    fp = NS / "verify" / "VERIFY_RESULTS.json"
    out = {}
    if not fp.exists():
        return out
    res = json.loads(fp.read_text())
    for rel, fres in res.get("files", {}).items():
        if not rel.startswith("evidence/srk_decoys_cell/"):
            continue
        for label, e in fres.items():
            if isinstance(e, dict) and "verdict" in e and e.get("sha256"):
                out[e["sha256"]] = e["verdict"]
    return out


def mc_cell(geom, cell, wb, gamma, n_paths):
    hh, kk = float(F(geom["h"])), float(F(geom["k"]))
    c = hh + kk
    rows = []
    for i, G in gamma.items():
        step = 1 / 32
        nb = int(round(hh / step)) + 1
        grid = {}

        def wbar(p, m, i=i):
            a, b = min(int(p / step), nb - 1), min(int(m / step), nb - 1)
            if (a, b) not in grid:
                grid[(a, b)] = he_abs_int(i, b * step - c + float(wb[0]), c - a * step + float(wb[1]))
            return grid[(a, b)]
        rng = random.Random(zlib.crc32(f"cell:{geom['h']}:{cell[0]}:{i}".encode()))
        ests = [simulate(hh, kk, float(e), wbar, n_paths, rng) for e in (cell[0], (cell[0] + cell[1]) / 2, cell[1])]
        mmax, se = max(ests, key=lambda t: t[0])
        rows.append({"i": i, "Gamma_bar": float(G), "mc_max": mmax, "se": se, "control_pass": mmax - 5 * se <= float(G),
                     "tightness": float(G) / mmax if mmax > 0 else None})
    return rows


def run(n_paths=10000):
    fam = json.loads((NS / "config" / "SRK_DECOY_DECLARATION_A2.json").read_text())["cell_family"]
    Q.log_execution("tests/e2e_cell_family.py", "A2 cell family end to end (verifier -> gate -> MC)",
                    klass="NONTARGET_DECOY", drifts=[[F(c["cell"][0]), F(c["cell"][1])]
                                                     for c in fam["cells"] if F(c["h"]) == 5 and F(c["k"]) == F(1, 2)],
                    notes=f"declared A2 cells; real-kernel cell far below the band; n_paths={n_paths}")
    verd = verdicts_from_results()
    out, ok = [], True
    for cd in fam["cells"]:
        geom = {"h": S.fstr(F(cd["h"])), "k": S.fstr(F(cd["k"]))}
        cell = (F(cd["cell"][0]), F(cd["cell"][1]))
        if F(cd["h"]) == 5 and F(cd["k"]) == F(1, 2):
            Q.guard_drift(*cell)
        wb, subs = S.cell_blocks(*cell)
        certs = load(cd)
        idx = tuple(fam["indices"])
        chk = {}
        chk["certificates_present"] = len(certs) == len(idx) * len(subs)
        chk["weight_block_strictly_larger_than_blocks"] = all(
            tuple(F(x) for x in c["weight_block"]) == wb and tuple(F(x) for x in c["block"]) != wb for c in certs)
        chk["all_verifier_ACCEPT"] = len(certs) > 0 and all(verd.get(c["sha256"]) == "ACCEPT" for c in certs)
        r = GT.gate(*cell, geom, "whole", certs, verd, indices=idx)
        direct = {i: max(F(c["Gamma"]) for c in certs if c["hermite_index"] == i) for i in idx} if certs else {}
        chk["gate_all_indices"] = all(r.gamma[i] is not None for i in idx) and not r.report["refused"]
        chk["gate_equals_max_over_blocks"] = chk["gate_all_indices"] and all(r.gamma[i] == direct[i] for i in idx)
        # negatives on real certificates
        s1 = S.fstr(subs[1][0])
        r_miss = GT.gate(*cell, geom, "whole", [c for c in certs if c["block"][0] != s1], verd, indices=idx)
        chk["neg_missing_subblock_None"] = all(r_miss.gamma[i] is None for i in idx)
        if certs:
            m = copy.deepcopy(certs[0])
            m["weight_block"] = list(m["block"])
            m["sha256"] = GT.canonical_sha(m)
            forged = dict(verd, **{m["sha256"]: "ACCEPT"})
            r_nw = GT.gate(*cell, geom, "whole", [m] + [c for c in certs if c is not certs[0]], forged, indices=idx)
            chk["neg_narrow_weight_refused"] = (r_nw.gamma[m["hermite_index"]] is None
                                                and any("hull" in x["reason"] for x in r_nw.report["refused"]))
            rej = dict(verd, **{certs[0]["sha256"]: "REJECT"})
            r_rej = GT.gate(*cell, geom, "whole", certs, rej, indices=idx)
            chk["neg_REJECT_refused"] = r_rej.gamma[certs[0]["hermite_index"]] is None
        r_tab = GT.gate(*cell, geom, "taboo", certs, verd, indices=idx, d_lo={"value": "1/1", "domain": [
            S.fstr(cell[0]), S.fstr(cell[1])]})
        chk["neg_wrong_kernel_refused"] = all(r_tab.gamma[i] is None for i in idx)
        shifted = (cell[0] + F(1, 1024), cell[1] + F(1, 1024))
        r_sh = GT.gate(*shifted, geom, "whole", certs, verd, indices=idx)
        chk["neg_shifted_cell_refused"] = all(r_sh.gamma[i] is None for i in idx)
        mc = mc_cell(geom, cell, wb, r.gamma, n_paths) if chk["gate_all_indices"] else []
        chk["mc_control_pass"] = bool(mc) and all(x["control_pass"] for x in mc)
        ok = ok and all(chk.values())
        out.append({"geometry": geom, "cell": [S.fstr(cell[0]), S.fstr(cell[1])],
                    "weight_block": [S.fstr(x) for x in wb], "sub_blocks": [[S.fstr(a), S.fstr(b)] for a, b in subs],
                    "checks": chk, "gamma_bar": {i: (S.fstr(v) if v is not None else None) for i, v in r.gamma.items()},
                    "mc": mc, "producer": sorted({c.get("producer_sha256") for c in certs})})
    return ok, out


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 10000
    ok, out = run(n)
    (NS / "evidence" / "SRK_CELL_FAMILY_E2E.json").write_text(json.dumps({"ok": ok, "n_paths": n, "cells": out},
                                                                         indent=1, default=str))
    for c in out:
        print(c["geometry"], c["cell"], c["checks"])
        for x in c["mc"]:
            print("   i", x["i"], "Gamma_bar", round(x["Gamma_bar"], 4), "mc", round(x["mc_max"], 4), "+-",
                  round(x["se"], 4), "PASS" if x["control_pass"] else "FAIL", "tight", round(x["tightness"] or 0, 4))
    print("E2E_PASS" if ok else "E2E_FAIL")
    sys.exit(0 if ok else 1)
