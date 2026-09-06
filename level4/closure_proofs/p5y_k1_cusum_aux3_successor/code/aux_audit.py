"""PHASE 14: adversarial self-audit of the aux3 successor.

Written to attack this namespace's own claims. Every check either produces
evidence or reports the failure; nothing is inherited except the facts
independent adjudication upheld (`ancestry.INHERITED_FACTS`).

The verdict is drawn from the four values the task allows:

    CUSUM_AUX3_READY_FOR_INDEPENDENT_ADJUDICATION
    CUSUM_AUX3_INCOMPLETE_CERTIFICATE
    CUSUM_AUX3_UNSOUND
    CUSUM_AUX3_IMPLEMENTATION_INCOMPLETE
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

import aux_certhash as CH
import aux_universe as SU
import far_field_inherited
import manifest
import no_monkeypatch

CELLS_DIR = ancestry.NS / "diagnostics" / "cells"
BLOCK = tuple(range(318, 325))          # 28 obligations
CONTROL = 325                           # with 325: 32 obligations
PREVIOUSLY_FAILING = [(319, "5"), (320, "5"), (321, "5"), (322, "5"), (323, "5")]


def records() -> dict[int, dict]:
    out = {}
    for p in sorted(CELLS_DIR.glob("aux3_CUSUM_*.json")):
        r = json.loads(p.read_text())
        out[r["cell_index"]] = r
    return out


def _git(*args) -> str:
    return subprocess.run(["git", *args], cwd=ancestry.ROOT,
                          capture_output=True, text=True).stdout


def certifying_process_probe(source: str) -> dict:
    """Answer a question inside a fresh certifying process, not this one."""
    preamble = (
        "import os, sys, json\n"
        "for v in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS',"
        "'NUMEXPR_NUM_THREADS'):\n    os.environ[v] = '1'\n"
        "os.environ['K1_THREADS_PINNED'] = '1'\n"
        f"sys.path.insert(0, {str(ancestry.NS / 'code')!r})\n")
    with tempfile.TemporaryDirectory() as d:
        script = Path(d) / "probe.py"
        script.write_text(preamble + source)
        out = subprocess.run([sys.executable, str(script)], cwd=ancestry.ROOT,
                             capture_output=True, text=True)
    if out.returncode != 0:
        return {"ok": False, "error": out.stderr[-500:]}
    return json.loads(out.stdout.strip().splitlines()[-1])


# ------------------------------------------------------------- governance
def audit_governance() -> dict:
    findings, ok = [], True

    untouched = {}
    for name, (ns, commit) in ancestry.PREDECESSOR_NAMESPACES.items():
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
        "m_scope": spec.M_VALUES == (1, 2, 3, 5),
        "detector_scope": spec.COUNTS == {"CUSUM": 326, "SR": 316},
        "cover_geometry": spec.CELLS_SHA256 == spec.CHECKPOINT["geometry"]["cells_sha256"],
        "frozen_spec_hashes": spec.verify_frozen_spec() == spec.FROZEN_HASHES,
        "obligation_universe": len(reviewed.work_ids()) == 17978 == spec.TOTAL_UNITS,
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
    if ff["re_derived_here"] or ff["gap_claim_reintroduced"]:
        ok = False
        findings.append("far-field preservation broken")

    return {"ok": ok,
            "predecessor_namespaces_untouched": untouched,
            "frozen_invariants": invariants,
            "obligation_universe": SU.universe_unchanged(),
            "sr_implemented_here": bool(sr_modules),
            "production_run": False,
            "far_field": ff,
            "findings": findings}


# --------------------------------------------------------- no patching
def audit_architecture() -> dict:
    findings, ok = [], True
    scan = no_monkeypatch.scan_namespace()
    if not scan["clean"]:
        ok = False
        findings.append(f"monkey-patching present: {scan['findings'][:3]}")
    predecessor = no_monkeypatch.scan_predecessor()

    wired = certifying_process_probe(
        "import aux_qualify, propagate, refine\n"
        "print(json.dumps({'reviewed_refine_intact': propagate.refine is refine}))\n")
    if not wired.get("reviewed_refine_intact"):
        ok = False
        findings.append("a reviewed module was redirected at runtime")

    src = (ancestry.NS / "code" / "aux_qualify.py").read_text()
    explicit = ("whole_cell_refinement=refine2.refine" in src
                and "node_refinement_factory=make_backend" in src)
    if not explicit:
        ok = False
        findings.append("refinement backends are not passed explicitly")

    return {"ok": ok, "this_namespace_clean": scan["clean"],
            "predecessor_defect_reproduced": not predecessor["clean"],
            "predecessor_findings": predecessor["findings"],
            "reviewed_module_intact_in_certifying_process":
                bool(wired.get("reviewed_refine_intact")),
            "explicit_injection": explicit,
            "findings": findings}


# --------------------------------------------------------------- provenance
def audit_provenance(recs: dict[int, dict]) -> dict:
    findings, ok = [], True
    state = manifest.verify()
    if not state["ok"]:
        ok = False
        findings.append(f"committed manifest does not verify: {state['problems'][:3]}")
    if manifest.build() != manifest.load():
        ok = False
        findings.append("committed manifest is stale against the working tree")

    coverage = certifying_process_probe(
        "import aux_qualify, manifest\n"
        "print(json.dumps(manifest.loaded_module_coverage()))\n")
    if not coverage.get("ok"):
        ok = False
        findings.append(f"uncovered certifying modules: "
                        f"{coverage.get('uncovered_loaded_modules')}")

    mhash = manifest.manifest_hash()
    rejected = SU.rejected_producer_identities()
    if mhash in rejected.values():
        ok = False
        findings.append("producer identity collides with a rejected lineage")

    per_cell = {}
    for idx, r in sorted(recs.items()):
        chain = r["provenance_chain"]
        stored = r["scientific_content_hash"]
        good = (chain["all_verified"] and chain["obligations"] == 28
                and chain["leaf_maps_empty"] and chain["auxiliary_evidence_bound"]
                and stored == CH.record_scientific_hash(r)
                and r["producer"]["producer_manifest_hash"] == mhash
                and r["producer"]["producer_manifest_schema"] == manifest.SCHEMA
                and r["producer"]["implementation_hash_kind"] == SU.IDENTITY_KIND
                and r["producer"]["loaded_module_coverage_strict"]
                and r["auxiliary_evidence_hash"] == CH.auxiliary_evidence_hash(r)
                and r["threading"]["pinned_before_numpy_import"])
        per_cell[idx] = {"chain_verified": chain["all_verified"],
                         "obligations": chain["obligations"],
                         "auxiliary_bound": chain["auxiliary_evidence_bound"],
                         "scientific_hash": stored,
                         "producer_resolves": r["producer"]["producer_manifest_hash"] == mhash,
                         "ok": good}
        if not good:
            ok = False
            findings.append(f"cell {idx}: provenance binding incomplete")

    return {"ok": ok,
            "producer_manifest_hash": mhash,
            "producer_manifest_schema": manifest.SCHEMA,
            "producer_manifest_path": str(manifest.ARTIFACT.relative_to(ancestry.ROOT)),
            "manifest_files": state["files"],
            "manifest_verifies": state["ok"],
            "strict_coverage_in_certifying_process": bool(coverage.get("ok")),
            "runtime_contract": manifest.load()["runtime"],
            "rejected_identities": rejected,
            "per_cell": per_cell, "findings": findings}


# --------------------------------------------------------------- determinism
def audit_determinism() -> dict:
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
            findings.append(f"cell {cell}: repeat produced a different hash")
        elif not v["runtime_fields_differed"]:
            findings.append(f"cell {cell}: repeat does not evidence a fresh run")
    return {"ok": not findings, "checked": True,
            "cells": sorted(int(c) for c in rep["cells"]),
            "all_identical": rep["all_identical"], "findings": findings}


# ------------------------------------------------------------------ science
def classify(level: dict) -> str:
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
            levels[m] = {"status": L["status"], "classification": classify(L),
                         "utilization": L["cover"]["utilization"],
                         "M_R2": float(F(L["M_R2"]))}
        cells[idx] = {"rho": float(F(r["rho"][0])), "levels": levels,
                      "all_pass": all(v["status"] == "PASS" for v in levels.values()),
                      "nodes_tightened": r["node_refinement"]["nodes_tightened"],
                      "cpu_seconds": r["cpu_seconds_including_dependencies"],
                      "scientific_hash": r["scientific_content_hash"]}

    missing_block = [c for c in BLOCK if c not in cells]
    if missing_block:
        findings.append(f"block cells not certified: {missing_block}")
    if CONTROL not in cells:
        findings.append("cell 325 regression control missing")
    elif not cells[CONTROL]["all_pass"]:
        findings.append("REGRESSION: cell 325 no longer passes every m")

    block_obligations = sum(len(c["levels"]) for i, c in cells.items() if i in BLOCK)
    total_obligations = sum(len(c["levels"]) for c in cells.values())
    block_pass = sum(1 for i, c in cells.items() if i in BLOCK
                     for v in c["levels"].values() if v["status"] == "PASS")
    total_pass = sum(1 for c in cells.values()
                     for v in c["levels"].values() if v["status"] == "PASS")

    scientific = [(i, m) for i, c in cells.items() for m, v in c["levels"].items()
                  if v["classification"] == "SCIENTIFIC_FAILURE"]
    loose = [(i, m) for i, c in cells.items() for m, v in c["levels"].items()
             if v["classification"] == "CERTIFICATE_TOO_LOOSE"]

    resolved = [(i, m) for i, m in PREVIOUSLY_FAILING
                if i in cells and cells[i]["levels"].get(m, {}).get("status") == "PASS"]
    still_open = [(i, m) for i, m in PREVIOUSLY_FAILING if (i, m) not in resolved]

    all_pass = (not missing_block and CONTROL in cells
                and all(c["all_pass"] for c in cells.values()))
    status = "PASS_CANDIDATE" if all_pass else (
        "SCIENTIFIC_FAILURE" if scientific else "INCOMPLETE")

    return {"cells": cells,
            "block_318_324_obligations": block_obligations,
            "block_318_324_pass": block_pass,
            "with_control_318_325_obligations": total_obligations,
            "with_control_318_325_pass": total_pass,
            "previously_failing": [list(x) for x in PREVIOUSLY_FAILING],
            "previously_failing_now_pass": [list(x) for x in resolved],
            "still_open": [list(x) for x in still_open],
            "scientific_failures": scientific,
            "certificate_too_loose": loose,
            "control_regression_clean": CONTROL in cells and cells[CONTROL]["all_pass"],
            "cusum_compact_cover": "PASS_CANDIDATE" if all_pass else "INCOMPLETE",
            "cusum_far_field": "PASS",
            "status": status,
            "findings": findings}


# --------------------------------------------------------------------- cost
def audit_cost(recs: dict[int, dict]) -> dict:
    det_path = ancestry.NS / "diagnostics" / "determinism.json"
    clean = {}
    if det_path.exists():
        det = json.loads(det_path.read_text())
        clean = {int(c): v["repeat_cpu_seconds"] for c, v in det["cells"].items()}
    measured = {c: r["cpu_seconds_including_dependencies"] for c, r in recs.items()}
    aux = {c: r["cpu_seconds_auxiliary"] for c, r in recs.items()}
    total = sum(measured.values())
    return {
        "cost_cap_status": "NOT_ESTABLISHED",
        "hard_cap_cpu_hours": spec.HARD_CAP_CPU_H,
        "cap_changed": False,
        "reserve_redistributed": False,
        "measured_cells": len(measured),
        "measured_cpu_seconds_contended": round(total, 1),
        "measured_cpu_hours_contended": round(total / 3600, 3),
        "auxiliary_cpu_seconds": {c: round(v, 1) for c, v in sorted(aux.items())},
        "auxiliary_share": (round(sum(aux.values()) / total, 4) if total else None),
        "clean_uncontended_cpu_seconds": clean,
        "contention_note": "the block ran 8 workers on 8 cores; per-cell CPU "
                           "seconds are inflated by memory-bandwidth stalls. "
                           "Only the repeat runs, at 2 workers, are clean "
                           "measurements, and even those are not a cost model.",
        "why_not_established": [
            "8 of 326 CUSUM cells were certified here and 0 of 316 SR cells",
            "SR has no implementation, so its cost is unmeasured, not estimated",
            "the 435.8 CPU-hour figure from two namespaces ago was adjudicated "
            "NOT a rigorous lower bound and is not carried forward",
            "per-cell cost varies with rho and with how many nodes take the "
            "auxiliary path, so these cells do not extrapolate",
        ],
    }


# ------------------------------------------------------------------ verdict
def verdict(arch, gov, prov, det, sci, tests_ok) -> dict:
    reasons = []
    reasons += [f"architecture: {f}" for f in arch["findings"]]
    reasons += [f"governance: {f}" for f in gov["findings"]]
    reasons += [f"provenance: {f}" for f in prov["findings"]]
    reasons += [f"determinism: {f}" for f in (det.get("findings") or [])]
    reasons += [f"science: {f}" for f in sci["findings"]]
    for cell, m in sci["certificate_too_loose"]:
        reasons.append(f"science: cell {cell} m={m} is CERTIFICATE_TOO_LOOSE")

    if sci["scientific_failures"] or not gov["ok"]:
        v = "CUSUM_AUX3_UNSOUND"
    elif not arch["ok"] or not prov["ok"] or det.get("ok") is False:
        v = "CUSUM_AUX3_IMPLEMENTATION_INCOMPLETE"
    elif sci["certificate_too_loose"] or sci["status"] != "PASS_CANDIDATE":
        v = "CUSUM_AUX3_INCOMPLETE_CERTIFICATE"
    elif tests_ok is False:
        v = "CUSUM_AUX3_IMPLEMENTATION_INCOMPLETE"
    else:
        v = "CUSUM_AUX3_READY_FOR_INDEPENDENT_ADJUDICATION"
    return {"verdict": v, "reasons": reasons,
            "not_claimed": ["K1 CLOSED", "SR complete", "production ready",
                            "cost-cap PASS", "P5Y closed"]}


def run(tests_ok: bool | None = None) -> dict:
    recs = records()
    arch = audit_architecture()
    gov = audit_governance()
    prov = audit_provenance(recs)
    det = audit_determinism()
    sci = audit_science(recs)
    cost = audit_cost(recs)
    return {"schema": "k1.cusum-aux3.audit.v1",
            "campaign": "P5Y-K1",
            "namespace": str(ancestry.NS.relative_to(ancestry.ROOT)),
            "predecessor": ancestry.CUSUM_COMMIT,
            "inherited_facts": ancestry.INHERITED_FACTS,
            "repaired_here": ancestry.REPAIRED_HERE,
            "architecture": arch, "governance": gov, "provenance": prov,
            "determinism": det, "science": sci, "cost": cost,
            "sr_status": "NOT_IMPLEMENTED_IN_THIS_TASK",
            "k1_state": "K1_INCOMPLETE_IMPLEMENTATION",
            "result_bearing": False,
            **verdict(arch, gov, prov, det, sci, tests_ok)}


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
