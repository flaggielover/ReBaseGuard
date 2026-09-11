"""Successor T3 whole-cell record for one successor cell.

MID mode: max over all 3,994 frozen live patches of the certified midpoint patch bounds (same rules as the frozen
t3_aggregate: nothing sampled, a missing or non-finite patch FAILS, never gives a smaller delta).
CELL mode: the governed mean-value successor (p5y_k1_sr_o9_curvature_successor/code/curv_mv.py, frozen cusum_layer2
construction): for every residual node X, delta_cell(X) = delta_mid(X) + rho * Env_X with Env_X the e-uniform bound
of d_e r_X over THIS successor cell (certified cell-uniform operator norms x certified candidate sups + exact-term
derivatives); image x0 values: midpoint ball +- rho * Env. The interval-e mode is not used.
"""
import hashlib
import json
import sys
from fractions import Fraction as Fr
from pathlib import Path

import sr_o9_candidates as T
import sr_o9_equations as EQ
import t2_final_certifier as FC
import t4_cell as T4
import curv_mv as MV
import succ_cells as SC
import succ_t1 as S1
from flint import arb

NS = Path(__file__).resolve().parents[1]
CP = NS.parent
LIVE = CP / "p5y_k1_sr_o9_t345_successor/config/live_patches.txt"
T2U = CP / "p5y_k1_sr_o9_t2_closure_successor/evidence/universe_table.json"


def canonical(o) -> bytes:
    return (json.dumps(o, sort_keys=True, separators=(",", ":"), ensure_ascii=True) + "\n").encode()


def _enc(x: arb):
    m, e = x.man_exp()
    return [int(m), int(e)]


def aggregate(s: int, files) -> dict:
    rec_cell = SC.cell(s)
    live = [tuple(map(int, l.split())) for l in LIVE.read_text().splitlines() if l.strip()]
    uni = json.loads(T2U.read_text())
    urow = {(r[0], r[1]): r for r in uni["rows"]}
    recs, dup = {}, 0
    for f in sorted(files):
        for line in Path(f).read_text().splitlines():
            r = json.loads(line)
            if r["successor_cell"] != s:
                continue
            key = tuple(r["patch"])
            sci = {k: v for k, v in r.items() if k not in ("cpu_seconds", "peak_rss_kib")}
            sci["modes"]["mid"].pop("cache_hits", None), sci["modes"]["mid"].pop("cache_misses", None)
            if key in recs and canonical(recs[key]) != canonical(sci):
                dup += 1
            recs.setdefault(key, sci)
    missing = [p for p in live if p not in recs]
    extra = [p for p in recs if p not in set(live)]
    built = S1.build(rec_cell)["scientific"]
    mant = {x["node"]: x["mantissas"] for x in built["candidates"]}
    hashes = {x["node"]: x["identity_hash"] for x in built["candidates"]}
    want_sha = hashlib.sha256(T.canonical(sorted(hashes.items()))).hexdigest()
    cand_sha = {recs[p]["candidate_identity_list_sha256"] for p in recs}
    checks = {"all_live_patches_present": not missing, "no_extra_patches": not extra, "no_duplicate_conflicts": dup == 0,
              "single_candidate_identity_list": cand_sha == {want_sha},
              "successor_table_hash": {recs[p]["successor_cells_sha256"] for p in recs} == {SC.table_sha256()}}
    nodes = sorted(next(iter(recs.values()))["modes"]["mid"]["nodes"]) if recs else []
    mid, x0, fin_fail, geo_fail, lg_fail = {}, {}, [], [], []
    for n in nodes:
        best, arg, chmax, is_img = Fr(-1), None, {}, None
        for p in live:
            if p not in recs:
                continue
            v = recs[p]["modes"]["mid"]["nodes"][n]
            if not v["fin"]:
                fin_fail.append([n, list(p)])
                continue
            is_img = "w" in v
            q = Fr(v["w"] if is_img else v["d"])
            if q > best:
                best, arg = q, list(p)
            if "ch" in v and v["ch"]:
                for k, x in v["ch"].items():
                    if Fr(x) > chmax.get(k, (Fr(-1), None))[0]:
                        chmax[k] = (Fr(x), list(p))
            if "lg" in v and not (all(v["lg"].values()) and v["eg"]["PASS"] and v["lgb"]):
                lg_fail.append([n, list(p)])
            if "x0" in v:
                x0[n] = v["x0"]
        mid[n] = {"kind": "image" if is_img else "residual", "delta": f"{best.numerator}/{best.denominator}",
                  "delta_float": float(best), "attained_at": arg,
                  "channels_max": {k: {"value": f"{q.numerator}/{q.denominator}", "float": float(q), "attained_at": a}
                                   for k, (q, a) in sorted(chmax.items())} or None}
    for p in live:
        if p not in recs:
            continue
        gg, u = recs[p]["modes"]["mid"]["geo"], urow.get(p)
        if not (u is not None and gg["n_z"] == u[2] and gg["panel_ids_sha256"] == u[9] and gg["strip_ids"] == u[10]
                and gg["P1"]["PASS"] and gg["strip_P1_PASS"] and gg["contracts"] == 102):
            geo_fail.append(list(p))
    # CELL mode by the governed mean-value construction over THIS successor cell
    struct = MV.struct_full()
    with T.scientific_precision():
        g = SC.geometry(rec_cell)
        e_ball = g["e0"] + arb(0, g["rho"].abs_upper())
        SV = {q: MV.sup_He_phi(q) for q in range(4)}
        nrm = MV.norms(g["left"], g["right"])
        sups = {n: T4.cand_sup(m) for n, m in mant.items()}
        env = MV.envelopes(struct, sups, nrm, e_ball, SV)
        rho_u = arb(g["rho"].abs_upper())
        cell, x0c, comp = {}, {}, {}
        for n in nodes:
            if n in EQ.IMAGE_NODES:
                cell[n] = dict(mid[n])
                if n in x0:
                    b = T4.img_x0(x0[n]) + arb(0, (rho_u * env[n]).upper())
                    x0c[n] = {"mid": _enc(arb(b.mid())), "rad": _enc(arb(b.rad()))}
                comp[n] = {"kind": "image", "Env": float(env[n])}
                continue
            d = MV.fr(T4.exact(Fr(mid[n]["delta"])) + rho_u * env[n]) if mid[n]["delta"] != "-1/1" else Fr(-1)
            cell[n] = {"kind": "residual", "delta": f"{d.numerator}/{d.denominator}", "delta_float": float(d),
                       "construction": "delta_mid + rho*Env (mean-value successor)", "channels_max": None}
            comp[n] = {"kind": "residual", "delta_mid": mid[n]["delta_float"], "Env": float(env[n]), "rho_Env": float(rho_u * env[n])}
    checks.update({"all_finite": not fin_fail, "geometry_conforms_T2_universe": not geo_fail,
                   "all_F_local_gates_all_patches": not lg_fail, "x0_values_present_mid": len(x0) == 18, "nodes_63": len(nodes) == 63})
    out = {"schema": "rebaseguard.p5y.k1.sr.partition-successor.t3-cell.v1", "cell": s, "successor_id": rec_cell["id"],
           "successor_cell_identity": SC.identity(rec_cell), "patches": len(recs),
           "candidate_identity_list_sha256": sorted(cand_sha), "checks": checks, "T3_PASS": all(checks.values()),
           "failures": {"non_finite": fin_fail[:50], "geometry": geo_fail[:50], "local_gates": lg_fail[:50],
                        "missing": [list(p) for p in missing[:50]], "extra": [list(p) for p in extra[:50]]},
           "delta": {"mid": mid, "cell": cell}, "x0_images": {"mid": x0, "cell": x0c},
           "mean_value_cell_mode": {"components": comp, "rho_upper": float(rho_u),
                                    "norms": {k: {str(i): float(v) for i, v in d.items()} for k, d in nrm.items() if k in ("K", "Kz")}},
           "input_source_files": sorted(Path(f).name for f in files),
           "consumed_records_sha256": hashlib.sha256(canonical([recs[p] for p in live if p in recs])).hexdigest(),
           "universe_table_sha256": hashlib.sha256(T2U.read_bytes()).hexdigest(), "live_patches_sha256": hashlib.sha256(LIVE.read_bytes()).hexdigest()}
    out["t3_record_sha256"] = hashlib.sha256(canonical(out)).hexdigest()
    return out


def main():
    import glob
    s, pattern, outp = int(sys.argv[1]), sys.argv[2], sys.argv[3]
    r = aggregate(s, glob.glob(pattern))
    Path(outp).write_bytes(canonical(r))
    print(json.dumps({"cell": s, "id": r["successor_id"], "patches": r["patches"], "checks": r["checks"], "T3_PASS": r["T3_PASS"]}, indent=1))


if __name__ == "__main__":
    main()
