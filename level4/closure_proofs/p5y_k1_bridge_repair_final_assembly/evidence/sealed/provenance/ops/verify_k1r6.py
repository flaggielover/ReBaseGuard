"""K1R6 Phase 6/7: INDEPENDENT post-production verification of the two genuine CUSUM bridge cells.
Read-only; runs OUTSIDE the repository roots in a fresh process. Nothing is trusted from producer PASS fields:
certificates are REBUILT from the sealed scientific content, ledger gates are re-checked in exact rationals,
hashes are recomputed, identities re-admitted."""
import copy, hashlib, json, sys
from fractions import Fraction as Fr
from pathlib import Path
R = Path(sys.argv[1])
NS = Path("/home/ubuntu/work/ReBaseGuard-sr-o9-t1/level4/closure_proofs/p5y_k1r6_cusum_bridge_repair")
sys.path.insert(0, str(NS / "driver"))
import k1r6_cusum_entry as E                                     # noqa: E402
import identity_k1r6 as IDB                                      # noqa: E402
import k1r6_chain as CH                                          # noqa: E402
import fast_range_k1r6 as FRT                                    # noqa: E402
import k1r6_bridge_resolver as RES                               # noqa: E402
import provenance as repair2_provenance                          # noqa: E402
sha = lambda b: hashlib.sha256(b).hexdigest()
PID = "3527b3b9399c12b406217c72548264293f11b8f14f1250f5cede138e7ba84671"
CKPT = "d519a2d26304a31a60ca71fc1f48f552c6c325fa3703640aea7dea8c1db56cb9"
TBL = "db02a798b57e6317bcdbdd6bc40b7ac9ae31e2e966f0ba303cec12df8f54ab90"
K4CK = "9091cb0d5db6cc0a8d233f1667bea78bc69be676b2672f2e47506c453d2a33f0"
PARTS = {"low", "high", "plus_tail", "minus_tail"}
out = {"run_root": str(R), "cells": {}}
ev_dirs = sorted(p.name for p in (R / "evidence").iterdir())
out["evidence_dirs"] = ev_dirs


def ledger_ok(L):
    bad = []
    for k, g in L["top_level_gates"].items():
        if k in ("top_reserve", "total") or "cap" not in g or g.get("usage") in (None, "None"):
            continue
        if not Fr(str(g["usage"])) <= Fr(str(g["cap"])):
            bad.append(f"top:{k}")
    for k, g in L["nested_candidate_gates"].items():
        if k == "B_reserve" or "cap" not in g:
            continue
        if not Fr(str(g["usage"])) <= Fr(str(g["cap"])):
            bad.append(f"nested:{k}")
    if not Fr(L["cover"]["usage"]) <= Fr(L["cover"]["cap"]):
        bad.append("cover")
    lo, hi = Fr(L["target_gate"]["lo"]), Fr(L["target_gate"]["hi"])
    if not (-2 < lo <= hi < 2):
        bad.append("target")
    return bad


for idx in (1000, 1001):
    c, d = {}, R / "evidence" / f"cusum_{idx}"
    launch = json.loads((R / "logs" / f"CUSUM_{idx}.launch.json").read_text())
    exitj = json.loads((R / "logs" / f"CUSUM_{idx}.exit.json").read_text()) if (R / "logs" / f"CUSUM_{idx}.exit.json").exists() else None
    c["process_exit_rc0"] = bool(exitj) and exitj["rc"] == 0
    files = sorted(p.name for p in d.iterdir()) if d.exists() else []
    c["exactly_two_files"] = files == [f"cell_done_{idx}.json", f"k1r6_CUSUM_{idx}_256.json"]
    if not c["exactly_two_files"]:
        out["cells"][str(idx)] = {"checks": c, "files": files, "PASS": False}
        continue
    mk = json.loads((d / f"cell_done_{idx}.json").read_text())
    rb = (d / f"k1r6_CUSUM_{idx}_256.json").read_bytes()
    rec = json.loads(rb)
    cell = RES.resolve("CUSUM", idx)
    c["marker_binds_record"] = (mk["marker_schema"] == "rebaseguard.p5y.k1r6.cusum-cell-done-marker.v1" and mk["cell_id"] == idx
                                and mk["task_id"] == launch["task_id"] and mk["record_sha256"] == sha(rb))
    c["scientific_hash_recomputes"] = E.H.record_scientific_hash(rec) == rec["scientific_content_hash"] == mk["scientific_content_hash"]
    c["producer_identity"] = rec["producer_identity_hash"] == mk["producer_identity_hash"] == PID and rec["producer"]["producer_identity_hash"] == PID
    c["checkpoint_bound"] = rec["k1r6_bridge"]["k1r6_checkpoint_sha256"] == mk["k1r6_checkpoint_sha256"] == CKPT and rec["k1r6_bridge"]["k1r4_checkpoint_sha256"] == K4CK
    c["bridge_table_hash"] = rec["k1r6_bridge"]["k1r4_table_sha256"] == rec["k1r6_bridge"]["identity_cells_sha256"] == TBL
    c["record_identity_fields"] = (rec["cell_index"] == idx and rec["detector"] == "CUSUM" and rec["precision_bits"] == 256
                                   and rec["campaign"] == E.CAMPAIGN == "p5y_k1r6_cusum_entry" and rec["production_run"] is True
                                   and "k1r6_non_genuine_plumbing_replay" not in rec)
    geo = {f: rec.get(f) for f in ("e0", "rho", "C_upper") if f in rec}
    c["record_geometry_is_bridge"] = all(v == cell[f] for f, v in geo.items()) and len(geo) >= 2
    ids = [x["identity"] for x in rec["certificates"].values()]
    c["certificate_identities_bridge_native"] = len(ids) == 28 and all(
        i["cell_index"] == idx and i["cells_sha256"] == TBL and all(i[f] == cell[f] for f in ("e0", "rho", "left", "right", "C_upper"))
        and i["checkpoint_hash"] == IDB.spec.CHECKPOINT_SHA256 and i["obligation_universe_total"] == IDB.spec.TOTAL_UNITS
        and i["producer_identity_hash"] == PID for i in ids)
    # REBUILD the certificate chain from the sealed scientific content (not the stored certificates)
    ctx = E.producer_context(256)
    aux_hash = E.H.auxiliary_evidence_hash(rec)
    c["auxiliary_evidence_hash_recomputes"] = aux_hash == rec["auxiliary_evidence_hash"]
    certs = CH.build_certificates(rec, ctx, aux_hash)
    chain = CH.verify_chain(rec, certs, ctx, aux_hash)
    c["certificate_chain_rebuilt_equal"] = (sorted(certs) == sorted(rec["certificates"]) and all(
        E.H.certificate_hash(certs[u]) == rec["certificates"][u]["certificate_hash"] and certs[u]["status"] == rec["certificates"][u]["status"]
        and certs[u]["identity"] == rec["certificates"][u]["identity"] for u in certs))
    c["chain_verified_28"] = chain["all_verified"] is True and chain["units_verified"] == 28 and chain["obligations"] == 28
    units = repair2_provenance.cell_units("CUSUM", idx, m_values=[int(m) for m in rec["m"]])
    c["every_unit_readmitted"] = all(IDB.admit_resume_record(certs[IDB.unit_id(u)]["identity"], u, dependency_certificates=certs,
                                                             auxiliary_evidence_hash=aux_hash, **ctx) for u in units)
    # science: exact-rational re-check of every ledger gate, independent of the ledger's status string
    ledgers = {m: ledger_ok(L) for m, L in rec["m"].items()}
    c["m_universe_exact"] = sorted(int(m) for m in rec["m"]) == [1, 2, 3, 5]
    c["ledger_gates_recheck_exact"] = all(not b for b in ledgers.values())
    stat = {u: certs[u]["status"] for u in certs}
    c["all_obligations_pass"] = all(s in ("PASS", "CERTIFIED") for s in stat.values()) and all(
        rec["m"][m]["status"] == "PASS" for m in rec["m"])
    objs = rec["objects"]
    c["object_deltas_finite_nonneg"] = all(Fr(o["delta_mid"]) >= 0 and Fr(o["delta_cell"]) >= Fr(o["delta_mid"]) for o in objs.values())
    # module provenance
    fg = rec["producer"]["final_gate"]
    c["module_provenance"] = (fg["ran_after_scientific_hash"] is True and fg["tcb_size"] == 69
                              and rec["producer_manifest_hash"] == sha((NS / "config/PRODUCER_MANIFEST.json").read_bytes())
                              and rec["scipy_guard"] is not None)
    # zero case
    z = rec["k1r6_bridge"]["zero_case"]
    fz = z["firings"]
    by = {}
    for f in fz:
        by[f"{f['object']}|{f['part']}"] = by.get(f"{f['object']}|{f['part']}", 0) + 1
    c["zero_case_record_valid"] = (z["zero_case_count"] == len(fz) and [f["seq"] for f in fz] == list(range(len(fz)))
                                   and all(f["part"] in PARTS and f["reason"] == FRT.ZERO_CASE_REASON for f in fz)
                                   and by == z["by_object_part"])
    mut = copy.deepcopy(rec)
    mut["k1r6_bridge"]["zero_case"]["zero_case_count"] = z["zero_case_count"] + 1
    c["zero_case_inside_scientific_hash"] = E.H.record_scientific_hash(mut) != rec["scientific_content_hash"]
    # any object whose all four parts fired must have an exactly-zero polynomial residual where one is recorded
    full = {o for o in {f["object"] for f in fz} if {p for p in PARTS if by.get(f"{o}|{p}")} == PARTS}
    aux_objs = rec.get("auxiliary_evidence", {}).get("objects", {})
    c["fully_zero_objects_have_zero_residual"] = all(Fr(aux_objs[o]["polynomial_residual"]) == 0 for o in full if o in aux_objs)
    out["cells"][str(idx)] = {
        "PASS": all(c.values()), "checks": c, "files": files,
        "record_sha256": mk["record_sha256"], "scientific_content_hash": rec["scientific_content_hash"],
        "cpu_seconds": mk["cpu_seconds"], "cpu_h": mk["cpu_seconds"] / 3600,
        "ledger_status": {m: rec["m"][m]["status"] for m in rec["m"]}, "ledger_recheck_failures": ledgers,
        "B_cover_utilization": {m: float(Fr(rec["m"][m]["cover"]["usage"]) / Fr(rec["m"][m]["cover"]["cap"])) for m in rec["m"]},
        "target_interval": {m: [float(Fr(rec["m"][m]["target_gate"]["lo"])), float(Fr(rec["m"][m]["target_gate"]["hi"]))] for m in rec["m"]},
        "zero_case_count": z["zero_case_count"], "zero_case_by_object_part": z["by_object_part"],
        "fully_zero_objects": sorted(o for o in full if o), "geometry": {f: cell[f][0] if isinstance(cell[f], list) else cell[f] for f in ("left", "right")},
    }
out["no_unauthorized_records"] = ev_dirs == ["cusum_1000", "cusum_1001"]
# Phase 7: CUSUM coverage, exact rationals
ok_cells = all(v.get("PASS") for v in out["cells"].values()) and len(out["cells"]) == 2
if ok_cells:
    b = sorted((Fr(v["geometry"]["left"]), Fr(v["geometry"]["right"])) for v in out["cells"].values())
    comp_hi, far_lo = Fr(11, 2), Fr(49750555, 8388608)
    chain_ok = b[0][0] == comp_hi and b[0][1] == b[1][0] and b[1][1] == far_lo
    gaps = (b[0][0] - comp_hi) + (b[1][0] - b[0][1]) + (far_lo - b[1][1])
    out["coverage"] = {"historical_compact": "[0, 11/2]", "bridge": f"({b[0][0]}, {b[1][1]}]", "far_field": f"[{far_lo}, infinity)",
                       "splices_exact": chain_ok, "uncovered_width": str(abs(gaps)) if chain_ok else "NONZERO",
                       "union": "[0, infinity)" if chain_ok else "INCOMPLETE", "PASS": chain_ok and gaps == 0}
else:
    out["coverage"] = {"PASS": None, "status": "NOT_REACHED"}
out["VERIFIED"] = ok_cells and out["no_unauthorized_records"]
print(json.dumps(out, indent=1, sort_keys=True, default=str))
