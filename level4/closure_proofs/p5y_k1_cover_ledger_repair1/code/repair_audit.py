"""Repair-specific self-audit.

A read-only self-adjudication of repair1. Not an independent review, and it
cannot conclude production readiness.
"""
from __future__ import annotations

import copy
import json
import subprocess
from fractions import Fraction as F
from pathlib import Path

import prior

import spec                                                     # noqa: E402
import universe as reviewed_universe                            # noqa: E402

import repair_layer2                                            # noqa: E402
import repair_universe as RU                                    # noqa: E402

NS = prior.NS
ROOT = prior.ROOT
IMPL_NS = prior.IMPL_NS
SPEC_NS = prior.SPEC_NS

MUTATIONS = {
    "detector": ("detector", "SR"),
    "cell": ("cell_index", 137),
    "unit_kind": ("unit_kind", "curvature"),
    "function": ("function_or_m", "dF_4"),
    "e0": ("e0", ["1/3", "0/1"]),
    "rho": ("rho", ["1/7", "0/1"]),
    "unit_hash": ("unit_hash", "0" * 64),
    "checkpoint_hash": ("checkpoint_hash", "1" * 64),
    "implementation_hash": ("implementation_hash", "2" * 64),
    "precision": ("precision_bits", 384),
    "dependency_hash": ("source_certificate_hashes", {"bogus": "0" * 64}),
    "source_certificate_hash": ("source_certificate_hashes", {}),
}


def frozen_tree_unchanged() -> bool:
    import hashlib
    manifest = json.loads((SPEC_NS / "manifests/freeze.json").read_text())
    actual = {}
    for p in SPEC_NS.rglob("*"):
        if p.is_file() and "__pycache__" not in p.parts \
                and p != SPEC_NS / "manifests/freeze.json":
            actual[str(p.relative_to(SPEC_NS))] = \
                hashlib.sha256(p.read_bytes()).hexdigest()
    return actual == manifest["files"]


def reviewed_namespace_preserved() -> dict:
    """The reviewed implementation must be byte-identical to c0a1f40."""
    rel = str(IMPL_NS.relative_to(ROOT))
    out = subprocess.run(["git", "diff", "--name-only",
                          prior.REVIEWED_COMMIT, "--", rel],
                         cwd=ROOT, capture_output=True, text=True)
    changed = [x for x in out.stdout.split("\n") if x.strip()]
    return {"reviewed_commit": prior.REVIEWED_COMMIT,
            "paths_changed": changed, "preserved": not changed}


def resume_negative_controls() -> dict:
    # dF_2 is used as the probe because it HAS dependencies (F_2 and the
    # bundle). h_1 is a leaf whose correct dependency set is empty, so
    # emptying `source_certificate_hashes` would not be a mutation at all.
    unit = ("CUSUM", 0, "object", "dF_2")
    ctx = RU.context(backend_hash="B")
    good = RU.canonical_identity(unit, **ctx)
    results = {"valid_record_admitted": RU.admits(good, unit, **ctx)}
    for name, (field, bad) in MUTATIONS.items():
        rec = copy.deepcopy(good)
        rec[field] = bad
        results[f"rejects_{name}"] = not RU.admits(rec, unit, **ctx)
    rec = copy.deepcopy(good)
    rec["obligation_universe_total"] = 12255
    results["rejects_old_12255_universe"] = not RU.admits(rec, unit, **ctx)
    units = reviewed_universe.work_ids()
    other = units[reviewed_universe.shard_bounds(len(units), 5, 8)[0]]
    results["rejects_cross_shard_substitution"] = not RU.admits(good, other, **ctx)
    # A leaf obligation must also be exactly identified, and its empty
    # dependency set must not be forgeable into a non-empty one.
    leaf = ("CUSUM", 0, "object", "h_1")
    leaf_rec = RU.canonical_identity(leaf, **ctx)
    results["leaf_record_admitted"] = RU.admits(leaf_rec, leaf, **ctx)
    forged = copy.deepcopy(leaf_rec)
    forged["source_certificate_hashes"] = {"CUSUM|0|object|S_0": "0" * 64}
    results["rejects_forged_leaf_dependency"] = not RU.admits(forged, leaf, **ctx)
    results["rejects_leaf_as_other_unit"] = not RU.admits(leaf_rec, unit, **ctx)
    results["all_negative_controls_rejected"] = all(
        v for k, v in results.items() if k.startswith("rejects_"))
    return results


def s0_charge_status(records: list[dict]) -> dict:
    if not records:
        return {"status": "NOT_COMPUTED", "charged_exactly_once": None}
    ok = all(r["s0_charge_audit"]["all_charged_exactly_once"] for r in records)
    reps = {r["s0_charge_audit"]["representation"] for r in records}
    return {"status": "COMPUTED", "records": len(records),
            "charged_exactly_once": ok, "representations": sorted(reps),
            "duplicate_absent": ok and reps == {
                "A: residual against fixed candidate + separate epsS"}}


def sr_and_far_field_still_absent() -> dict:
    import qualify
    sr = qualify.run_cell("SR", 0)
    status = (IMPL_NS / "IMPLEMENTATION_STATUS.md").read_text()
    return {
        "sr_reports_not_implemented": sr["status"] == "NOT_IMPLEMENTED",
        "sr_never_reports_pass": "PASS" not in json.dumps(sr),
        "far_field_declared_not_implemented":
            "far-field certificates" in status and "NOT_IMPLEMENTED" in status,
        "repair_did_not_implement_sr": not any(
            "SR" in p.name for p in (NS / "code").glob("*.py")),
    }


def cell_325_untouched() -> dict:
    rec = json.loads((IMPL_NS / "diagnostics/representatives/CUSUM_325_256.json"
                      ).read_text())
    failing = [m for m, L in rec["m"].items() if L["status"] == "FAIL"]
    produced = sorted(p.name for p in (NS / "diagnostics").glob("*325*")) \
        if (NS / "diagnostics").exists() else []
    return {"reviewed_failures_preserved": sorted(failing) == ["2", "3", "5"],
            "state": "CURRENT_CERTIFICATE_FAILURE_ONLY",
            "repair_produced_no_325_record": produced == [],
            "repair_refuses_325": 325 in __import__(
                "repair_qualify").FORBIDDEN_CELLS}


def review(records_dir: Path | None = None) -> dict:
    records = []
    d = records_dir or (NS / "diagnostics/regression")
    if d.exists():
        for p in sorted(d.glob("repaired_*.json")):
            records.append(json.loads(p.read_text()))

    neg = resume_negative_controls()
    s0 = s0_charge_status(records)
    preserved = reviewed_namespace_preserved()
    srff = sr_and_far_field_still_absent()
    c325 = cell_325_untouched()

    checks = {
        "frozen_successor_untouched": frozen_tree_unchanged(),
        "reviewed_implementation_commit_preserved": preserved["preserved"],
        "duplicate_S0_charge_absent": s0.get("duplicate_absent") is True,
        "S0_uncertainty_present_exactly_once": s0.get("charged_exactly_once") is True,
        "exact_resume_identity_enforced": neg["valid_record_admitted"],
        "all_single_field_mutations_rejected": neg["all_negative_controls_rejected"],
        "source_certificate_hashes_bound": "source_certificate_hashes"
                                           in RU.IDENTITY_FIELDS,
        "work_universe_17978_unchanged": len(reviewed_universe.work_ids()) == 17978,
        "shard_conservation_unchanged": all(
            reviewed_universe.verify_shard_conservation(w)["union_equals_universe"]
            for w in (1, 8, 16, 32, 64)),
        "cpu_cap_1126_unchanged": spec.HARD_CAP_CPU_H == 1126,
        "precision_256_unchanged": (spec.PRODUCTION_BITS == 256
                                    and not spec.PRECISION_ESCALATION_ALLOWED),
        "budgets_unchanged": sum(spec.TOP_BUDGETS.values()) == F(19, 100),
        "production_disabled": spec.PRODUCTION_ENABLED is False,
        "SR_still_unimplemented": (srff["sr_reports_not_implemented"]
                                   and srff["sr_never_reports_pass"]),
        "far_field_still_unimplemented": srff["far_field_declared_not_implemented"],
        "cell_325_still_unresolved": (c325["reviewed_failures_preserved"]
                                      and c325["repair_refuses_325"]),
    }
    failed = [k for k, v in checks.items() if v is False]
    return {
        "review_kind": ("read-only self-adjudication of repair1; not an "
                        "independent human or agent review"),
        "reviewed_commit": prior.REVIEWED_COMMIT,
        "checks": checks,
        "checks_failed": failed,
        "resume_negative_controls": neg,
        "s0_charge": s0,
        "reviewed_namespace": preserved,
        "sr_and_far_field": srff,
        "cell_325": c325,
        "verdict": ("REPAIR_READY_FOR_INDEPENDENT_ADJUDICATION" if not failed
                    else "REPAIR_FAILED"),
        "production_ready": False,
        "implementation_complete": False,
        "cost_cap_status": "NOT_ESTABLISHED",
        "scientific_verdict_changed": False,
        "remaining_unresolved": [
            "SR raw DAG absent",
            "SR M_R2 absent",
            "SR all-m absent",
            "far-field not implemented",
            "cell 325 CURRENT_CERTIFICATE_FAILURE_ONLY",
            "full cost cap NOT_ESTABLISHED",
        ],
    }


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--records")
    ap.add_argument("--out")
    args = ap.parse_args()
    result = review(Path(args.records) if args.records else None)
    text = json.dumps(result, indent=2, sort_keys=True)
    if args.out:
        Path(args.out).write_text(text + "\n")
    print(text)
    raise SystemExit(bool(result["checks_failed"]))
