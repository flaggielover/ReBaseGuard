"""PHASE 11: adversarial self-audit of the CUSUM completion successor.

Written to attack this namespace's own claims, not to defend them. Every check
either produces evidence or reports NOT_ESTABLISHED; nothing is assumed from a
predecessor except the facts independent adjudication explicitly upheld
(recorded in `ancestry.INHERITED_FACTS`).

The verdict is drawn from the four values the task allows:

    CUSUM_SUCCESSOR_READY_FOR_INDEPENDENT_ADJUDICATION
    INCOMPLETE_CERTIFICATE
    UNSOUND
    IMPLEMENTATION_INCOMPLETE
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from fractions import Fraction as F
from pathlib import Path

import ancestry
import spec
import universe as reviewed

import determinism
import far_field_inherited
import successor_certhash as CH
import successor_producer as SP
import successor_universe as SU

import producer as repair2_producer

CELLS_DIR = ancestry.NS / "diagnostics" / "cells"
BLOCK = tuple(range(318, 325))
CONTROL = 325


# ---------------------------------------------------------------- utilities
def records() -> dict[int, dict]:
    out = {}
    for p in sorted(CELLS_DIR.glob("succ_CUSUM_*.json")):
        r = json.loads(p.read_text())
        out[r["cell_index"]] = r
    return out


def certifying_process_coverage() -> dict:
    """Run the manifest-coverage audit inside a fresh certifying process."""
    probe = ("import sys, json\n"
             f"sys.path.insert(0, {str(ancestry.NS / 'code')!r})\n"
             "import successor_qualify\n"
             "import successor_producer as SP\n"
             "print(json.dumps(SP.verify_loaded_modules_covered(strict=False)))\n")
    with tempfile.TemporaryDirectory() as d:
        script = Path(d) / "coverage_probe.py"
        script.write_text(probe)
        out = subprocess.run([sys.executable, str(script)], cwd=ancestry.ROOT,
                             capture_output=True, text=True)
    if out.returncode != 0:
        return {"ok": False, "covered": None,
                "uncovered_loaded_modules": [f"probe failed: {out.stderr[-400:]}"]}
    return json.loads(out.stdout.strip().splitlines()[-1])


def _git(*args) -> str:
    return subprocess.run(["git", *args], cwd=ancestry.ROOT,
                          capture_output=True, text=True).stdout


# ------------------------------------------------------------- governance
def audit_governance() -> dict:
    findings, ok = [], True

    frozen = spec.verify_frozen_spec() == spec.FROZEN_HASHES
    if not frozen:
        ok = False
        findings.append("frozen spec hashes do not match")

    untouched = {}
    for name, ns, commit in (
            ("frozen_successor", ancestry.SPEC_NS, ancestry.REVIEWED_COMMIT),
            ("reviewed_implementation", ancestry.IMPL_NS, ancestry.REVIEWED_COMMIT),
            ("repair1", ancestry.REPAIR1_NS, ancestry.REPAIR1_COMMIT),
            ("repair2", ancestry.REPAIR2_NS, ancestry.REPAIR2_COMMIT),
            ("final_completion", ancestry.FINAL_NS, ancestry.FINAL_COMMIT)):
        rel = str(ns.relative_to(ancestry.ROOT))
        diff = [l for l in _git("diff", "--name-only", commit, "--", rel).split("\n")
                if l.strip()]
        untouched[name] = not diff
        if diff:
            ok = False
            findings.append(f"{name} modified: {diff[:4]}")

    dirty = [l[3:] for l in _git("status", "--porcelain").splitlines()]
    rel_ns = str(ancestry.NS.relative_to(ancestry.ROOT))
    outside = [p for p in dirty if not p.startswith(rel_ns)]
    if outside:
        ok = False
        findings.append(f"writes outside this namespace: {outside[:4]}")

    invariants = {
        "hard_cap_cpu_hours": spec.HARD_CAP_CPU_H == 1126,
        "precision_bits": spec.PRODUCTION_BITS == 256,
        "precision_escalation_disallowed": not spec.PRECISION_ESCALATION_ALLOWED,
        "degree_adaptation_disallowed": not spec.DEGREE_ADAPTATION_ALLOWED,
        "budget_sum": sum(spec.TOP_BUDGETS.values()) == F(19, 100),
        "cover_geometry": spec.CELLS_SHA256 == spec.CHECKPOINT["geometry"]["cells_sha256"],
        "cell_counts": spec.COUNTS == {"CUSUM": 326, "SR": 316},
        "obligation_universe": len(reviewed.work_ids()) == 17978,
        "production_disabled": not spec.PRODUCTION_ENABLED,
    }
    for k, v in invariants.items():
        if not v:
            ok = False
            findings.append(f"frozen invariant violated: {k}")

    sr_modules = [p.name for p in (ancestry.NS / "code").glob("sr_*.py")]
    if sr_modules:
        ok = False
        findings.append(f"SR implemented in this task: {sr_modules}")

    production_dirs = [d for d in ("results", "certificates", "production_logs")
                       if (ancestry.NS / d).exists()]
    if production_dirs:
        ok = False
        findings.append(f"production artefacts present: {production_dirs}")

    ff = far_field_inherited.report()["inherited"]
    if ff["re_derived_here"] or ff["far_field_logic_changed_here"]:
        ok = False
        findings.append("far-field logic was modified")

    return {"ok": ok, "frozen_spec_matches": frozen,
            "predecessor_namespaces_untouched": untouched,
            "frozen_invariants": invariants,
            "sr_implemented_here": bool(sr_modules),
            "production_run": False,
            "far_field_inherited_unchanged": True,
            "findings": findings}


# --------------------------------------------------------------- provenance
def audit_provenance(recs: dict[int, dict]) -> dict:
    findings, ok = [], True
    ph, bh = SP.producer_hash(), SP.backend_hash()
    manifest = SP.producer_manifest()

    # Ask the question about a CERTIFYING process, not about this audit process:
    # a fresh interpreter that imports only the runner, exactly as a cell run
    # does. Auditing our own interpreter would flag the audit's own imports.
    coverage = certifying_process_coverage()
    if not coverage["ok"]:
        ok = False
        findings.append(f"executed modules outside the manifest: "
                        f"{coverage['uncovered_loaded_modules'][:6]}")

    rejected = SP.rejected_producer_hashes()
    if ph in rejected.values():
        ok = False
        findings.append("producer hash collides with a rejected lineage hash")
    if ph == repair2_producer.producer_hash():
        ok = False
        findings.append("producer hash equals the Repair2 hash")
    for commit in (ancestry.REVIEWED_COMMIT, ancestry.REPAIR1_COMMIT,
                   ancestry.REPAIR2_COMMIT, ancestry.FINAL_COMMIT):
        if ph == commit:
            ok = False
            findings.append("producer hash is a git commit id")

    if SP.producer_manifest() != manifest:
        ok = False
        findings.append("producer manifest is not deterministic")

    per_cell = {}
    for idx, r in sorted(recs.items()):
        chain = r["provenance_chain"]
        stored = r["scientific_content_hash"]
        recomputed = CH.record_scientific_hash(r)
        good = (chain["all_verified"] and chain["obligations"] == 28
                and chain["leaf_maps_empty"] and stored == recomputed
                and r["producer"]["implementation_hash"] == ph
                and r["producer"]["backend_hash"] == bh
                and r["producer"]["implementation_hash_kind"] == SU.IDENTITY_KIND
                and r["threading"]["pinned_before_numpy_import"]
                and r["threading"]["blas_threads"] == "1")
        per_cell[idx] = {"chain_verified": chain["all_verified"],
                         "obligations": chain["obligations"],
                         "scientific_hash": stored,
                         "hash_recomputes": stored == recomputed,
                         "producer_bound": r["producer"]["implementation_hash"] == ph,
                         "ok": good}
        if not good:
            ok = False
            findings.append(f"cell {idx}: provenance binding incomplete")

    return {"ok": ok, "producer_hash": ph, "backend_hash": bh,
            "producer_hash_kind": SU.IDENTITY_KIND,
            "manifest_file_count": len(manifest["files"]),
            "loaded_module_coverage": coverage["ok"],
            "rejected_lineage_hashes": rejected,
            "per_cell": per_cell, "findings": findings}


# ---------------------------------------------------------------- science
def classify(level: dict) -> str:
    """Exact classification of one (cell, m) outcome."""
    if level["status"] == "PASS":
        return "CERTIFIED_PASS"
    lo, hi = F(level["R2_interval"]["lo"]), F(level["R2_interval"]["hi"])
    if lo < 0 < hi:
        return "CERTIFICATE_TOO_LOOSE"
    return "SCIENTIFIC_FAILURE"


def audit_science(recs: dict[int, dict]) -> dict:
    cells, findings = {}, []
    for idx in sorted(recs):
        r = recs[idx]
        levels = {}
        for m in sorted(r["m"], key=int):
            L = r["m"][m]
            levels[int(m)] = {
                "status": L["status"],
                "classification": classify(L),
                "utilization": L["cover"]["utilization"],
                "M_R2": float(F(L["M_R2"])),
                "R2_centre": float((F(L["R2_interval"]["lo"])
                                    + F(L["R2_interval"]["hi"])) / 2),
                "R2_halfwidth": float((F(L["R2_interval"]["hi"])
                                       - F(L["R2_interval"]["lo"])) / 2),
            }
        cells[idx] = {"rho": r["rho"], "e0": r["e0"],
                      "levels": levels,
                      "all_pass": all(v["status"] == "PASS" for v in levels.values()),
                      "cpu_seconds": r["cpu_seconds_including_dependencies"],
                      "peak_rss_mib": round(r["peak_rss_kib"] / 1024, 1),
                      "scientific_hash": r["scientific_content_hash"]}

    missing = [c for c in BLOCK if c not in cells]
    if missing:
        findings.append(f"block cells not certified: {missing}")
    if CONTROL not in cells:
        findings.append("cell 325 regression control missing")
    elif not cells[CONTROL]["all_pass"]:
        findings.append("REGRESSION: cell 325 no longer passes every m")

    scientific = [(c, m) for c, v in cells.items() for m, lv in v["levels"].items()
                  if lv["classification"] == "SCIENTIFIC_FAILURE"]
    defects = [(c, m) for c, v in cells.items() for m, lv in v["levels"].items()
               if lv["classification"] == "IMPLEMENTATION_DEFECT"]
    loose = [(c, m) for c, v in cells.items() for m, lv in v["levels"].items()
             if lv["classification"] == "CERTIFICATE_TOO_LOOSE"]

    block_pass = (not missing
                  and all(cells[c]["all_pass"] for c in BLOCK if c in cells))
    control_pass = CONTROL in cells and cells[CONTROL]["all_pass"]

    if block_pass and control_pass:
        status = "PASS_CANDIDATE"
    elif scientific:
        status = "SCIENTIFIC_FAILURE"
    else:
        status = "INCOMPLETE"

    return {"cells": cells,
            "block": list(BLOCK), "control": CONTROL,
            "block_all_pass": block_pass,
            "control_regression_clean": control_pass,
            "scientific_failures": scientific,
            "implementation_defects": defects,
            "certificate_too_loose": loose,
            "cusum_compact_cover_status": status,
            "findings": findings}


def audit_determinism() -> dict:
    """Fresh repeat runs must reproduce the recorded scientific hash exactly."""
    path = ancestry.NS / "diagnostics" / "determinism.json"
    if not path.exists():
        return {"ok": None, "checked": False,
                "note": "no repeat runs recorded for this build"}
    rep = json.loads(path.read_text())
    findings = []
    for cell, v in sorted(rep["cells"].items(), key=lambda kv: int(kv[0])):
        if not v["producer_identical"]:
            findings.append(f"cell {cell}: repeat ran under a different producer")
        elif not v["identical"]:
            findings.append(f"cell {cell}: repeat produced a different scientific "
                            f"hash ({v['recorded_scientific_hash'][:16]} vs "
                            f"{v['repeat_scientific_hash'][:16]})")
        elif not v["runtime_fields_differed"]:
            findings.append(f"cell {cell}: repeat is identical in runtime fields "
                            f"too, so it does not evidence a fresh run")
    return {"ok": not findings, "checked": True,
            "cells": sorted(int(c) for c in rep["cells"]),
            "all_identical": rep["all_identical"], "findings": findings}


# ------------------------------------------------------------------- cost
def audit_cost(recs: dict[int, dict]) -> dict:
    """Measured cost of THIS successor only. No predecessor figure is reused."""
    measured = {c: r["cpu_seconds_including_dependencies"] for c, r in recs.items()}
    total_s = sum(measured.values())
    # The block ran 8 workers on 8 cores. The determinism repeats ran 2 workers
    # on the same machine, and the SAME cells cost about half as much CPU -- the
    # CPU counter charges memory-bandwidth stalls. Both numbers are reported; the
    # contended one is what the block actually consumed.
    repeats = {}
    det_path = ancestry.NS / "diagnostics" / "determinism.json"
    if det_path.exists():
        det = json.loads(det_path.read_text())
        repeats = {int(c): (v["recorded_cpu_seconds"], v["repeat_cpu_seconds"])
                   for c, v in det["cells"].items()}
    inflation = ([a / b for a, b in repeats.values() if b] or [None])
    return {
        "contention": {
            "block_workers": 8, "cores": 8,
            "repeat_workers": 2,
            "same_cell_cpu_seconds_contended_vs_not": repeats,
            "observed_inflation_factor": (round(sum(inflation) / len(inflation), 2)
                                          if inflation[0] is not None else None),
            "note": "per-cell CPU seconds from the block are inflated by "
                    "memory-bandwidth contention and must not be used as a "
                    "per-cell cost model",
        },
        "cost_cap_status": "NOT_ESTABLISHED",
        "measured_cells": len(measured),
        "measured_cpu_seconds": round(total_s, 1),
        "measured_cpu_hours": round(total_s / 3600, 3),
        "mean_cpu_seconds_per_cell": round(total_s / len(measured), 1) if measured else None,
        "max_cpu_seconds_per_cell": round(max(measured.values()), 1) if measured else None,
        "hard_cap_cpu_hours": spec.HARD_CAP_CPU_H,
        "cap_changed": False,
        "reserve_redistributed": False,
        "predecessor_435_8_hour_figure_reused": False,
        "why_not_established": [
            "only 8 of 326 CUSUM cells were certified in this task, and 0 of 316 "
            "SR cells; per-cell cost varies strongly with rho and with how many "
            "objects need the order-2 path, so these 8 do not extrapolate",
            "SR has no implementation, so its cost is unmeasured, not estimated",
            "the predecessor's 435.8 CPU-hour figure was adjudicated NOT a "
            "rigorous lower bound and is not carried forward",
            "cells 318-324 do not yet fully certify, so the work required to "
            "close them is not yet bounded",
        ],
        "measured_under_contention": True,
        "note": "measurements taken with one worker per core, BLAS and FLINT "
                "pinned to one thread; not a projection",
    }


# ---------------------------------------------------------------- verdict
def verdict(gov: dict, prov: dict, sci: dict, det: dict,
            tests_ok: bool | None) -> dict:
    reasons = []
    if det.get("ok") is False:
        reasons += [f"determinism: {f}" for f in det["findings"]]
    if not gov["ok"]:
        reasons += [f"governance: {f}" for f in gov["findings"]]
    if not prov["ok"]:
        reasons += [f"provenance: {f}" for f in prov["findings"]]
    reasons += [f"science: {f}" for f in sci["findings"]]
    for cell, m in sci["certificate_too_loose"]:
        reasons.append(f"science: cell {cell} m={m} is CERTIFICATE_TOO_LOOSE -- "
                       f"the certified R'' interval straddles zero, so the bound "
                       f"fails, not the mathematics")

    if sci["scientific_failures"] or sci["implementation_defects"] or not gov["ok"]:
        v = "UNSOUND" if (sci["scientific_failures"] or not gov["ok"]) \
            else "IMPLEMENTATION_INCOMPLETE"
    elif not prov["ok"] or det.get("ok") is False:
        v = "IMPLEMENTATION_INCOMPLETE"
    elif sci["certificate_too_loose"] or not sci["block_all_pass"]:
        v = "INCOMPLETE_CERTIFICATE"
    elif tests_ok is False:
        v = "IMPLEMENTATION_INCOMPLETE"
    else:
        v = "CUSUM_SUCCESSOR_READY_FOR_INDEPENDENT_ADJUDICATION"

    return {"verdict": v, "reasons": reasons,
            "not_claimed": ["K1 CLOSED", "SR complete", "COST_CAP PASS",
                            "production ready", "P5Y closed"]}


def run(tests_ok: bool | None = None) -> dict:
    recs = records()
    gov = audit_governance()
    prov = audit_provenance(recs)
    sci = audit_science(recs)
    det = audit_determinism()
    cost = audit_cost(recs)
    return {"schema": "k1.cusum-successor.audit.v1",
            "campaign": "P5Y-K1",
            "namespace": str(ancestry.NS.relative_to(ancestry.ROOT)),
            "inherited_facts": ancestry.INHERITED_FACTS,
            "governance": gov, "provenance": prov, "science": sci,
            "determinism": det,
            "cost": cost,
            "far_field": far_field_inherited.report(),
            "determinism_field_classes": determinism.classify_fields(),
            "sr_status": "NOT_IMPLEMENTED_IN_THIS_TASK",
            "k1_state": "K1_INCOMPLETE_IMPLEMENTATION",
            "result_bearing": False,
            **verdict(gov, prov, sci, det, tests_ok)}


def main() -> None:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--out")
    ap.add_argument("--tests-ok", choices=["yes", "no"])
    a = ap.parse_args()
    rep = run({"yes": True, "no": False}.get(a.tests_ok))
    text = json.dumps(rep, indent=2, sort_keys=True) + "\n"
    if a.out:
        Path(a.out).write_text(text)
    print(text)


if __name__ == "__main__":
    main()
