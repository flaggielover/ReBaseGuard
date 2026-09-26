"""K1R6 Part F: NON-GENUINE post-science plumbing replay on the two bridge indices.

ops/qualify_k1r6.py copies this file OUT of the repository roots and runs it in a fresh process, so the
production TCB gates see exactly the production import closure. The scientific content is the HISTORICAL
aux4 cell-325 record relabelled onto the bridge index: it is NOT a bridge certificate. Every sealed record
carries k1r6_non_genuine_plumbing_replay.genuine = False, the task id says NONGENUINE, and all seals go to a
temporary directory that is deleted before this process exits. Only hashes/booleans are printed.

Path exercised: certificate construction -> bridge identity -> chain verification -> assemble ->
scientific hash -> final TCB gate + SciPy guard + module binding -> seal -> independent re-verification.
"""
import copy
import hashlib
import json
import sys
import tempfile
import time
from pathlib import Path

DRIVER, AUX4REC = sys.argv[1], sys.argv[2]
sys.path.insert(0, DRIVER)
import k1r6_cusum_entry as E                                     # noqa: E402
import identity_k1r6 as IDB                                      # noqa: E402
import fast_range_k1r6 as FRT                                    # noqa: E402
import k1r6_bridge_resolver as RES                               # noqa: E402
from qualify4 import scipy_guard                                 # noqa: E402
import provenance as repair2_provenance                          # noqa: E402

# keys written by the certify tail / assemble(); removed so no historical value can survive the replay
ASSEMBLE_KEYS = ("campaign", "changes", "s0_charge_audit", "tightening_report", "auxiliary_evidence_hash",
                 "producer_manifest_hash", "producer_manifest_schema", "producer_manifest_path",
                 "producer_manifest_version", "runtime_contract_hash", "producer_identity_hash",
                 "implementation_hash_kind", "obligation_universe_total", "producer", "certificates",
                 "provenance_chain", "cpu_seconds_including_dependencies", "cpu_seconds_auxiliary", "wall_seconds",
                 "cpu_seconds_prepare", "peak_rss_kib", "precision_bits", "threading", "production_run",
                 "result_bearing", "scientific_certification_of_full_cover", "universe", "scientific_content_hash",
                 "scipy_guard")
hist = json.loads(Path(AUX4REC).read_text())
out = {"non_genuine_plumbing_replay": True, "scientific_content_source": Path(AUX4REC).name, "cells": {}}
with tempfile.TemporaryDirectory(prefix="k1r6-NONGENUINE-replay-") as td:
    for idx in E.BRIDGE_INDICES:
        cell = E.bridge_cell(idx)
        resolved = RES.resolve("CUSUM", idx) == cell
        E.verify_tcb("initial")
        E.verify_k1r6_modules()
        FRT.reset_zero_case()
        rec = {k: copy.deepcopy(v) for k, v in hist.items() if k not in ASSEMBLE_KEYS}
        rec["cell_index"] = idx
        for f in ("e0", "rho", "C_upper", "left", "right"):
            if f in rec:
                rec[f] = copy.deepcopy(cell[f])
        rec["k1r6_non_genuine_plumbing_replay"] = {
            "genuine": False, "scientific_content_source": "aux4_CUSUM_325_256.json (historical; relabelled)",
            "purpose": "exercise certificate -> identity -> chain -> hash -> seal on a bridge index"}
        threading = E.pin_flint()
        t0, w0 = time.process_time(), time.time()
        guard = scipy_guard.ScipyGuard()
        with guard:
            aux_hash = E.H.auxiliary_evidence_hash(rec)
            ctx = E.producer_context(256)
            certs = E.build_certificates(rec, ctx, aux_hash)
            chain = E.verify_chain(rec, certs, ctx, aux_hash)
        o = {"record": rec, "guard": guard, "ctx": ctx, "certificates": certs, "chain": chain,
             "charge": hist.get("s0_charge_audit"), "tightening": hist.get("tightening_report"), "aux_hash": aux_hash,
             "threading": threading, "t0": t0, "w0": w0, "t_prep": 0.0, "cpu_aux": 0.0}
        record = E.assemble(idx, o, 256)
        ev = Path(td) / f"replay_{idx}"
        marker = E.seal(ev, idx, record, f"K1R6-QUAL-NONGENUINE-REPLAY-{idx}")
        rb = (ev / f"k1r6_CUSUM_{idx}_256.json").read_bytes()
        r2 = json.loads(rb)
        units = repair2_provenance.cell_units("CUSUM", idx, m_values=[int(m) for m in rec["m"]])
        readmit = all(IDB.admit_resume_record(certs[IDB.unit_id(u)]["identity"], u, dependency_certificates=certs,
                                              auxiliary_evidence_hash=aux_hash,
                                              **{k: v for k, v in ctx.items()}) for u in units)
        ids = [c["identity"] for c in certs.values()]
        checks = {
            "bridge_identity_resolves_and_equals_certified_cell": resolved,
            "28_units_certificates_built": len(certs) == 28 == len(units),
            "every_identity_is_the_bridge_cell": all(i["cell_index"] == idx and i["detector"] == "CUSUM" for i in ids),
            "cells_sha256_is_the_k1r4_bridge_table": all(i["cells_sha256"] == RES.BRIDGE_CELLS_SHA256 for i in ids),
            "identity_geometry_from_bridge_record": all(all(i[f] == cell[f] for f in ("e0", "rho", "left", "right", "C_upper")) for i in ids),
            "inherited_regime_fields_preserved": all(i["checkpoint_hash"] == IDB.spec.CHECKPOINT_SHA256
                                                     and i["obligation_universe_total"] == IDB.spec.TOTAL_UNITS
                                                     and i["implementation_hash_kind"] == IDB.IDENTITY_KIND for i in ids),
            "chain_verified": chain["all_verified"] is True and chain["units_verified"] == 28,
            "every_unit_readmitted_independently": readmit,
            "record_sha256_matches_marker": hashlib.sha256(rb).hexdigest() == marker["record_sha256"],
            "scientific_hash_recomputes": E.H.record_scientific_hash(r2) == r2["scientific_content_hash"] == marker["scientific_content_hash"],
            "k1r6_producer_identity_bound": r2["producer_identity_hash"] == marker["producer_identity_hash"] == ctx["producer_identity_hash"],
            "bridge_block_bound": (r2["k1r6_bridge"]["index"] == idx and r2["k1r6_bridge"]["identity_cells_sha256"] == RES.BRIDGE_CELLS_SHA256
                                   and "zero_case" in r2["k1r6_bridge"]),
            "final_gate_ran_after_hash": r2["producer"]["final_gate"]["ran_after_scientific_hash"] is True,
            "non_genuine_flag_sealed": r2["k1r6_non_genuine_plumbing_replay"]["genuine"] is False,
            "exactly_two_files_sealed": sorted(p.name for p in ev.iterdir()) == [f"cell_done_{idx}.json", f"k1r6_CUSUM_{idx}_256.json"],
        }
        out["cells"][str(idx)] = {"accepted": all(checks.values()), "checks": checks, "units": len(certs),
                                  "record_sha256": marker["record_sha256"],
                                  "scientific_content_hash": marker["scientific_content_hash"],
                                  "final_gate": r2["producer"]["final_gate"],
                                  "zero_case_count": r2["k1r6_bridge"]["zero_case"]["zero_case_count"]}
out["temporary_seals_deleted"] = not Path(td).exists()
print(json.dumps(out, sort_keys=True))
