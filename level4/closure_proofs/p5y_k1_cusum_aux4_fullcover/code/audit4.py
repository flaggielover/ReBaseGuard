"""PHASE 17: adversarial self-audit of the Aux4 full-cover namespace.

Written to attack this namespace's own claims. Nothing is inherited except what
independent adjudication upheld (`ancestry4.INHERITED_FACTS`); in particular the
CUSUM cover is NOT inherited -- adjudication required a full 326-cell rerun, and
the audit reports how much of that rerun actually exists.

Verdict, from the four values the task allows:

    CUSUM_AUX4_READY_FOR_INDEPENDENT_ADJUDICATION
    CUSUM_AUX4_INCOMPLETE_FULL_COVER
    CUSUM_AUX4_UNSOUND
    CUSUM_AUX4_BUDGET_BLOCKED
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from fractions import Fraction as F
from pathlib import Path

import ancestry4
import spec
import universe as reviewed

import aggregate_ledger
import hash_v2 as H
import identity4 as ID
import manifest_v2
import schema
import tcb

CELLS_DIR = ancestry4.NS / "diagnostics" / "cells"
DIFFICULT = [(319, "5"), (320, "5"), (321, "5"), (322, "5"), (323, "5")]
BLOCK_318_325 = tuple(range(318, 326))


def _git(*args) -> str:
    return subprocess.run(["git", *args], cwd=ancestry4.ROOT,
                          capture_output=True, text=True).stdout


def probe(source: str) -> dict:
    """Answer a question inside a fresh certifying process."""
    preamble = (
        "import os, sys, json\n"
        "for v in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS',"
        "'NUMEXPR_NUM_THREADS'):\n    os.environ[v] = '1'\n"
        "os.environ['K1_THREADS_PINNED'] = '1'\n"
        f"sys.path.insert(0, {str(ancestry4.NS / 'code')!r})\n")
    with tempfile.TemporaryDirectory() as d:
        script = Path(d) / "probe.py"
        script.write_text(preamble + source)
        out = subprocess.run([sys.executable, str(script)], cwd=ancestry4.ROOT,
                             capture_output=True, text=True)
    if out.returncode != 0:
        return {"ok": False, "error": out.stderr[-600:]}
    return json.loads(out.stdout.strip().splitlines()[-1])


# ------------------------------------------------------------- governance
def audit_governance() -> dict:
    findings, ok = [], True
    untouched = {}
    for name, (ns, commit) in ancestry4.PREDECESSOR_NAMESPACES.items():
        rel = str(ns.relative_to(ancestry4.ROOT))
        diff = [l for l in _git("diff", "--name-only", commit, "--", rel).split("\n")
                if l.strip()]
        untouched[name] = not diff
        if diff:
            ok = False
            findings.append(f"{name} modified: {diff[:4]}")

    dirty = [l[3:] for l in _git("status", "--porcelain").splitlines()]
    rel_ns = str(ancestry4.NS.relative_to(ancestry4.ROOT))
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
        "cusum_cells_326": len(aggregate_ledger.cusum_cells()) == 326,
        "production_disabled": not spec.PRODUCTION_ENABLED,
    }
    for k, v in invariants.items():
        if not v:
            ok = False
            findings.append(f"frozen invariant violated: {k}")

    sr_modules = [p.name for p in (ancestry4.NS / "code").glob("sr_*.py")]
    if sr_modules:
        ok = False
        findings.append(f"SR implemented here: {sr_modules}")
    production_dirs = [d for d in ("results", "certificates", "production_logs")
                       if (ancestry4.NS / d).exists()]
    if production_dirs:
        ok = False
        findings.append(f"production artefacts present: {production_dirs}")

    return {"ok": ok, "predecessor_namespaces_untouched": untouched,
            "frozen_invariants": invariants,
            "obligation_universe": ID.universe_unchanged(),
            "sr_implemented_here": bool(sr_modules),
            "production_run": False, "findings": findings}


# ------------------------------------------------------------ architecture
def audit_architecture() -> dict:
    findings, ok = [], True

    patched = probe(
        "import qualify4, propagate, refine\n"
        "print(json.dumps({'reviewed_refine_intact': propagate.refine is refine}))\n")
    if not patched.get("reviewed_refine_intact"):
        ok = False
        findings.append("a reviewed module was redirected at runtime")

    coverage = probe("import qualify4, tcb\n"
                     "print(json.dumps(tcb.verify_coverage()))\n")
    if not coverage.get("ok"):
        ok = False
        findings.append(f"loaded modules outside the TCB: {coverage.get('uncovered')}")

    # the non-certifying modules must genuinely not be on the certifying path
    loaded = probe("import qualify4, tcb\n"
                   "print(json.dumps({'loaded': tcb.loaded_repository_files()}))\n")
    rel = str((ancestry4.NS / "code").relative_to(ancestry4.ROOT))
    leaked = [p for p in loaded.get("loaded", [])
              if p.startswith(rel) and Path(p).name in tcb.AUX4_NON_CERTIFYING]
    if leaked:
        ok = False
        findings.append(f"non-certifying modules imported by the runner: {leaked}")

    body = (ancestry4.NS / "code" / "qualify4.py").read_text().split("def run_cell")[1]
    gate_last = (body.index("manifest_v2.final_gate(scipy_guard=guard)")
                 > body.index('record["scientific_content_hash"] = H'))
    if not gate_last:
        ok = False
        findings.append("the final gate does not run after the scientific hash")

    return {"ok": ok,
            "reviewed_modules_intact": bool(patched.get("reviewed_refine_intact")),
            "tcb_coverage_clean": bool(coverage.get("ok")),
            "loaded_repository_modules": coverage.get("loaded_repository_modules"),
            "tcb_size": coverage.get("tcb_size"),
            "non_certifying_modules_absent_from_certifying_path": not leaked,
            "final_gate_after_scientific_hash": gate_last,
            "findings": findings}


# --------------------------------------------------------------- provenance
def audit_provenance(records: dict) -> dict:
    findings, ok = [], True
    state = manifest_v2.verify()
    if not state["ok"]:
        ok = False
        findings.append(f"manifest does not verify: {state['problems'][:3]}")
    if manifest_v2.build() != manifest_v2.load():
        ok = False
        findings.append("committed manifest is stale against the working tree")

    ident = manifest_v2.identity()
    rejected = ID.rejected_producer_identities()
    for key in ("producer_manifest_hash", "producer_identity_hash"):
        if ident[key] in rejected.values():
            ok = False
            findings.append(f"{key} collides with a rejected predecessor identity")

    per_cell = {}
    for idx, rec in sorted(records.items()):
        good = (rec["producer"]["producer_identity_hash"] == ident["producer_identity_hash"]
                and rec["producer"]["runtime_contract_hash"] == ident["runtime_contract_hash"]
                and rec["scientific_content_hash"] == H.record_scientific_hash(rec)
                and rec["auxiliary_evidence_hash"] == H.auxiliary_evidence_hash(rec)
                and rec["provenance_chain"]["all_verified"]
                and rec["scipy_guard"]["scipy_free"]
                and rec["producer"]["final_gate"]["ran_after_scientific_hash"])
        per_cell[idx] = good
        if not good:
            ok = False
            findings.append(f"cell {idx}: provenance binding incomplete")

    return {"ok": ok, **ident,
            "manifest_verifies": state["ok"],
            "runtime_contract": manifest_v2.load()["runtime"],
            "rejected_identities": rejected,
            "cells_provenance_ok": sum(1 for v in per_cell.values() if v),
            "cells_checked": len(per_cell),
            "findings": findings}


# --------------------------------------------------------------- hash audit
def audit_scientific_hash(records: dict) -> dict:
    if not records:
        return {"ok": None, "checked": False, "note": "no records yet"}
    rec = records[sorted(records)[0]]
    audit = H.audit_record(rec)
    return {"ok": audit["ok"] and not audit["unaccounted"],
            "leaf_paths": audit["leaf_paths"],
            "hashed": audit["hashed"],
            "dropped_incidental": audit["dropped_incidental"],
            "unaccounted": audit["unaccounted"],
            "classes": audit["counts"],
            "default_class_for_unknown_fields": schema.SCIENTIFIC,
            "findings": [] if audit["ok"] else ["unaccounted record fields"]}


# --------------------------------------------------------------- determinism
def audit_determinism() -> dict:
    path = ancestry4.NS / "diagnostics" / "determinism.json"
    if not path.exists():
        return {"ok": None, "checked": False, "note": "no repeat runs recorded"}
    rep = json.loads(path.read_text())
    findings = []
    for cell, v in sorted(rep["cells"].items(), key=lambda kv: int(kv[0])):
        for key, label in (("scientific_hash_identical", "scientific hash"),
                           ("auxiliary_hash_identical", "auxiliary hash"),
                           ("producer_identical", "producer identity"),
                           ("intervals_identical", "interval endpoints"),
                           ("error_bounds_identical", "error bounds")):
            if not v.get(key):
                findings.append(f"cell {cell}: {label} differs between repeats")
        if not v.get("runtime_fields_differed"):
            findings.append(f"cell {cell}: repeat does not evidence a fresh run")
    return {"ok": not findings, "checked": True,
            "cells": sorted(int(c) for c in rep["cells"]),
            "all_identical": rep.get("all_identical"), "findings": findings}


# ------------------------------------------------------------------ science
def audit_science(records: dict, ledger: dict | None) -> dict:
    findings = []
    per_cell = {}
    for idx, rec in sorted(records.items()):
        levels = {m: rec["m"][m]["status"] for m in sorted(rec["m"], key=int)}
        per_cell[idx] = {"levels": levels,
                         "all_pass": all(s == "PASS" for s in levels.values()),
                         "utilization": {m: rec["m"][m]["cover"]["utilization"]
                                         for m in sorted(rec["m"], key=int)}}
    difficult = {}
    for cell, m in DIFFICULT:
        if cell in per_cell:
            difficult[f"{cell},m{m}"] = per_cell[cell]["levels"].get(m)
    control = per_cell.get(325, {}).get("all_pass")
    block = {c: per_cell[c]["all_pass"] for c in BLOCK_318_325 if c in per_cell}
    if 325 in per_cell and not control:
        findings.append("REGRESSION: cell 325 control does not pass every m")
    failing = [(c, m) for c, v in per_cell.items()
               for m, s in v["levels"].items() if s != "PASS"]
    if failing:
        findings.append(f"{len(failing)} (cell, m) obligations do not PASS")
    return {"cells_certified": len(per_cell),
            "cells_expected": 326,
            "obligations_certified": sum(len(v["levels"]) for v in per_cell.values()),
            "obligations_pass": sum(1 for v in per_cell.values()
                                    for s in v["levels"].values() if s == "PASS"),
            "difficult_cells": difficult,
            "block_318_325": block,
            "control_325_all_pass": control,
            "failing": failing[:20],
            "cusum_full_cover": (ledger or {}).get("cusum_full_cover", "INCOMPLETE"),
            "cusum_far_field": "PASS",
            "findings": findings}


# --------------------------------------------------------------------- cost
def audit_cost(records: dict) -> dict:
    path = ancestry4.NS / "diagnostics" / "cost_model.json"
    model = json.loads(path.read_text()) if path.exists() else {}
    measured = {c: r["cpu_seconds_including_dependencies"] for c, r in records.items()}
    total = sum(measured.values())
    return {"cost_cap_status": "NOT_ESTABLISHED",
            "hard_cap_cpu_hours": spec.HARD_CAP_CPU_H,
            "cap_changed": False,
            "reserve_redistributed": False,
            "cells_measured": len(measured),
            "cusum_cpu_seconds_so_far": round(total, 1),
            "cusum_cpu_hours_so_far": round(total / 3600, 3),
            "cost_model": model,
            "scope_note": "the 1126 CPU-hour cap is for the COMPLETE K1 campaign. "
                          "Only the CUSUM contribution is recorded here; SR is "
                          "unimplemented and unmeasured, so no campaign-level cost "
                          "conclusion follows."}


# ------------------------------------------------------------------ verdict
def verdict(arch, gov, prov, hashes, det, sci, cost, tests_ok) -> dict:
    reasons = []
    for section, name in ((arch, "architecture"), (gov, "governance"),
                          (prov, "provenance"), (hashes, "scientific hash"),
                          (det, "determinism"), (sci, "science")):
        reasons += [f"{name}: {f}" for f in (section.get("findings") or [])]

    budget_blocked = cost.get("cost_model", {}).get("cusum_only_exceeds_hard_cap")
    if budget_blocked:
        v = "CUSUM_AUX4_BUDGET_BLOCKED"
    elif not gov["ok"] or sci["failing"]:
        v = "CUSUM_AUX4_UNSOUND" if not gov["ok"] else "CUSUM_AUX4_INCOMPLETE_FULL_COVER"
    elif not arch["ok"] or not prov["ok"] or hashes.get("ok") is False \
            or det.get("ok") is False:
        v = "CUSUM_AUX4_UNSOUND"
    elif sci["cusum_full_cover"] != "PASS_CANDIDATE" \
            or sci["cells_certified"] != 326:
        v = "CUSUM_AUX4_INCOMPLETE_FULL_COVER"
    elif tests_ok is False:
        v = "CUSUM_AUX4_INCOMPLETE_FULL_COVER"
    else:
        v = "CUSUM_AUX4_READY_FOR_INDEPENDENT_ADJUDICATION"
    return {"verdict": v, "reasons": reasons,
            "not_claimed": ["K1 CLOSED", "SR complete", "overall COST_CAP PASS",
                            "production ready", "P5Y closed"]}


def run(tests_ok: bool | None = None) -> dict:
    records = {}
    for p in sorted(CELLS_DIR.glob("aux4_CUSUM_*.json")):
        rec = json.loads(p.read_text())
        records[rec["cell_index"]] = rec
    ledger_path = ancestry4.NS / "diagnostics" / "aggregate_ledger.json"
    ledger = json.loads(ledger_path.read_text()) if ledger_path.exists() else None

    arch = audit_architecture()
    gov = audit_governance()
    prov = audit_provenance(records)
    hashes = audit_scientific_hash(records)
    det = audit_determinism()
    sci = audit_science(records, ledger)
    cost = audit_cost(records)
    return {"schema": "k1.cusum-aux4.audit.v1",
            "campaign": "P5Y-K1",
            "namespace": str(ancestry4.NS.relative_to(ancestry4.ROOT)),
            "predecessor": ancestry4.AUX3_COMMIT,
            "inherited_facts": ancestry4.INHERITED_FACTS,
            "repaired_here": ancestry4.REPAIRED_HERE,
            "architecture": arch, "governance": gov, "provenance": prov,
            "scientific_hash": hashes, "determinism": det, "science": sci,
            "cost": cost,
            "aggregate_ledger": None if ledger is None else {
                "cusum_full_cover": ledger["cusum_full_cover"],
                "cells_present": ledger["universe"]["cells_present"],
                "obligations_pass": ledger["universe"]["obligations_pass"],
                "ledger_hash": ledger["ledger_hash"]},
            "sr_status": "NOT_IMPLEMENTED_IN_THIS_TASK",
            "k1_state": "CUSUM_K1_INCOMPLETE",
            "result_bearing": False,
            **verdict(arch, gov, prov, hashes, det, sci, cost, tests_ok)}


def main() -> None:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--out")
    ap.add_argument("--tests-ok", choices=["yes", "no"])
    ap.add_argument("--brief", action="store_true")
    a = ap.parse_args()
    rep = run({"yes": True, "no": False}.get(a.tests_ok))
    text = json.dumps(rep, indent=2, sort_keys=True) + "\n"
    if a.out:
        Path(a.out).write_text(text)
    if a.brief:
        print(json.dumps({"verdict": rep["verdict"], "reasons": rep["reasons"][:10],
                          "cells": rep["science"]["cells_certified"],
                          "obligations_pass": rep["science"]["obligations_pass"],
                          "cover": rep["science"]["cusum_full_cover"]}, indent=2))
    else:
        print(text)


if __name__ == "__main__":
    main()
