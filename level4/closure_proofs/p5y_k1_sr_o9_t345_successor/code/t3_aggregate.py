"""T3 whole-cell aggregation from certified T3 patch records (sup-norm: maxima over ALL live patches).

Consumes ONLY the certified per-patch records produced by t3_patch.py. For each DAG node and drift mode it takes
delta = max over the 3,994 frozen live patches of the certified patch residual bound (exact rationals of the
outward-exported upper bounds; max is order-independent, patches are still visited in canonical order), records
the attaining patch, the per-channel maxima of the F-equation certificates, the per-patch local gates, the x0
values of the operator images, and the geometry/identity conformance against the T2-closed universe.
Nothing is sampled; a missing or non-finite patch record makes the aggregation FAIL, never a smaller delta.
"""
import glob
import hashlib
import json
import sys
from fractions import Fraction as Fr
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
CP = NS.parent
T2U = CP / "p5y_k1_sr_o9_t2_closure_successor/evidence/universe_table.json"
MODES = ("mid", "cell")


def canonical(o) -> bytes:
    return (json.dumps(o, sort_keys=True, separators=(",", ":"), ensure_ascii=True) + "\n").encode()


def aggregate(cell: int, files) -> dict:
    live = [tuple(map(int, l.split())) for l in (NS / "config/live_patches.txt").read_text().splitlines() if l.strip()]
    uni = json.loads(T2U.read_text())
    urow = {(r[0], r[1]): r for r in uni["rows"]}
    # Provenance = the records CONSUMED for this cell (canonical, runtime fields removed), never whole-file hashes:
    # chunk files are shared by several cells and may still be growing while another cell's batch runs.
    recs, dup_conflicts = {}, 0
    for f in sorted(files):
        for line in Path(f).read_text().splitlines():
            r = json.loads(line)
            if r["cell"] != cell:
                continue
            key = tuple(r["patch"])
            sci = {k: v for k, v in r.items() if k not in ("cpu_seconds", "peak_rss_kib")}
            for m in sci["modes"].values():
                m.pop("cache_hits", None), m.pop("cache_misses", None)
            if key in recs and canonical(recs[key]) != canonical(sci):
                dup_conflicts += 1
            recs.setdefault(key, sci)
    missing = [p for p in live if p not in recs]
    extra = [p for p in recs if p not in set(live)]
    checks = {"all_live_patches_present": not missing, "no_extra_patches": not extra, "no_duplicate_conflicts": dup_conflicts == 0}
    cand_sha = {recs[p]["candidate_identity_list_sha256"] for p in recs}
    checks["single_candidate_identity_list"] = len(cand_sha) == 1
    nodes = sorted(next(iter(recs.values()))["modes"]["mid"]["nodes"]) if recs else []
    agg = {m: {} for m in MODES}
    fin_fail, geo_fail, lg_fail = [], [], []
    x0 = {}
    for mode in MODES:
        for n in nodes:
            best, arg, chmax = Fr(-1), None, {}
            is_img = None
            for p in live:
                if p not in recs:
                    continue
                v = recs[p]["modes"][mode]["nodes"][n]
                if not v["fin"]:
                    fin_fail.append([mode, n, list(p)])
                    continue
                is_img = "w" in v
                q = Fr(v["w"] if is_img else v["d"])
                if q > best:
                    best, arg = q, list(p)
                if "ch" in v and v["ch"]:
                    for k, x in v["ch"].items():
                        if Fr(x) > chmax.get(k, (Fr(-1), None))[0]:
                            chmax[k] = (Fr(x), list(p))
                if mode == "mid" and "lg" in v:
                    if not (all(v["lg"].values()) and v["eg"]["PASS"] and v["lgb"]):
                        lg_fail.append([n, list(p)])
                if "x0" in v:
                    x0.setdefault(mode, {})[n] = v["x0"]
            agg[mode][n] = {"kind": "image" if is_img else "residual", "delta": f"{best.numerator}/{best.denominator}",
                            "delta_float": float(best), "attained_at": arg,
                            "channels_max": {k: {"value": f"{q.numerator}/{q.denominator}", "float": float(q), "attained_at": a}
                                             for k, (q, a) in sorted(chmax.items())} or None}
    for p in live:
        if p not in recs:
            continue
        for mode in MODES:
            gg = recs[p]["modes"][mode]["geo"]
            u = urow.get(p)
            ok = (u is not None and gg["n_z"] == u[2] and gg["panel_ids_sha256"] == u[9] and gg["strip_ids"] == u[10]
                  and gg["P1"]["PASS"] and gg["strip_P1_PASS"] and gg["contracts"] == 102)
            if not ok:
                geo_fail.append([mode, list(p)])
    evals = sum(recs[p]["modes"]["mid"]["geo"]["contract_evaluations"] for p in recs)
    checks.update({"all_finite": not fin_fail, "geometry_conforms_T2_universe": not geo_fail,
                   "all_F_local_gates_all_patches": not lg_fail,
                   "x0_values_present_both_modes": all(len(x0.get(m, {})) == 18 for m in MODES),
                   "nodes_63": len(nodes) == 63})
    out = {"schema": "rebaseguard.p5y.k1.sr.o9.t3-whole-cell.v1", "cell": cell, "patches": len(recs),
           "candidate_identity_list_sha256": sorted(cand_sha), "checks": checks, "T3_PASS": all(checks.values()),
           "failures": {"non_finite": fin_fail[:50], "geometry": geo_fail[:50], "local_gates": lg_fail[:50],
                        "missing": [list(p) for p in missing[:50]], "extra": [list(p) for p in extra[:50]]},
           "contract_evaluations_mid": evals, "delta": agg, "x0_images": x0,
           "input_source_files": sorted(Path(f).name for f in files),
           "consumed_records_sha256": hashlib.sha256(canonical([recs[p] for p in live if p in recs])).hexdigest(),
           "universe_table_sha256": hashlib.sha256(T2U.read_bytes()).hexdigest()}
    out["t3_record_sha256"] = hashlib.sha256(canonical(out)).hexdigest()
    return out


def main():
    cell, pattern, out = int(sys.argv[1]), sys.argv[2], sys.argv[3]
    r = aggregate(cell, glob.glob(pattern))
    Path(out).write_bytes(canonical(r))
    print(json.dumps({"cell": cell, "patches": r["patches"], "checks": r["checks"], "T3_PASS": r["T3_PASS"],
                      "t3_record_sha256": r["t3_record_sha256"]}, indent=1))


if __name__ == "__main__":
    main()
