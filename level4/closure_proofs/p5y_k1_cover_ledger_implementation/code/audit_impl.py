"""Read-only self-audit of the implementation namespace against the frozen spec.

This is a self-adjudication program, NOT an independent human or agent review.
It cannot produce READY_FOR_PRODUCTION: production readiness is reserved for the
later independent Codex adjudication.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from fractions import Fraction as F
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
ROOT = NS.parents[2]
SPEC_NS = ROOT / "level4/closure_proofs/p5y_k1_cover_ledger_successor"
sys.path[:0] = [str(NS / "code"), str(SPEC_NS / "code")]

import assembly                                                    # noqa: E402
import depgraph                                                    # noqa: E402
import ledger                                                      # noqa: E402
import spec                                                        # noqa: E402
import universe                                                    # noqa: E402
from flint import arb                                              # noqa: E402
from intervals import exact, workprec                              # noqa: E402

import algebra as FROZEN                                           # noqa: E402


def frozen_tree_unchanged() -> bool:
    manifest = json.loads((SPEC_NS / "manifests/freeze.json").read_text())
    actual = {}
    for p in SPEC_NS.rglob("*"):
        if p.is_file() and "__pycache__" not in p.parts \
                and p != SPEC_NS / "manifests/freeze.json":
            actual[str(p.relative_to(SPEC_NS))] = \
                hashlib.sha256(p.read_bytes()).hexdigest()
    return actual == manifest["files"]


def frozen_guard_conflict() -> dict:
    """Why the frozen successor's own protected_check() now fails.

    It is not a mutation. Evidence, recomputed here rather than asserted:
      * the frozen tree is byte-identical to its own freeze manifest;
      * the START_HEAD git object manifest is unchanged;
      * every path it objects to is inside THIS namespace, which the frozen
        CHECKPOINT authorises ("Implementations may consume these immutable
        contracts in a NEW implementation namespace").
    """
    baseline = json.loads((SPEC_NS / "manifests/protected_start.json").read_text())
    start = baseline["start_head"]
    changed = subprocess.check_output(
        ["git", "diff", "--name-only", start, "--"], cwd=ROOT).decode().splitlines()
    spec_rel = str(SPEC_NS.relative_to(ROOT)) + "/"
    impl_rel = str(NS.relative_to(ROOT)) + "/"
    objected = [p for p in changed if not p.startswith(spec_rel)]
    actual = {}
    for r in subprocess.check_output(["git", "ls-tree", "-rz", start],
                                     cwd=ROOT).split(b"\0"):
        if not r:
            continue
        meta, name = r.split(b"\t", 1)
        mode, typ, oid = meta.decode().split()
        actual[name.decode()] = {"mode": mode, "type": typ, "git_oid": oid}
    return {
        "frozen_successor_start_head": start,
        "frozen_tree_byte_identical_to_freeze_manifest": frozen_tree_unchanged(),
        "start_head_git_object_manifest_unchanged": actual == baseline["entries"],
        "paths_objected_to": len(objected),
        "all_objected_paths_are_this_namespace": all(
            p.startswith(impl_rel) for p in objected),
        "frozen_tests_failing": ["GovernanceTests::test_protected_tree",
                                 "GovernanceTests::test_read_only_adjudication"],
        "cause": ("audit.protected_check() diffs START_HEAD against the WORKTREE "
                  "and rejects any differing path outside its own namespace, so "
                  "it fails for ANY commit made anywhere in the repository after "
                  "the freeze commit, including the implementation namespace the "
                  "frozen CHECKPOINT authorises"),
        "is_a_frozen_namespace_mutation": False,
        "resolution": ("surfaced for the independent adjudicator; the frozen "
                       "namespace is immutable and was NOT edited to satisfy "
                       "its own guard"),
    }


def only_new_namespace_touched() -> bool:
    changed = subprocess.check_output(["git", "status", "--porcelain"],
                                      cwd=ROOT).decode().splitlines()
    rel = str(NS.relative_to(ROOT))
    return all(rel in line for line in changed)


def _cover_refuses_second_derivative_charge() -> bool:
    with workprec(256):
        try:
            ledger.cover_charge(arb(1), F(1, 10), arb(1),
                                separate_derivative_charge=F(1, 5))
        except ledger.SeparateDerivativeCharge:
            return True
    return False


def _value_style_charge_refused() -> bool:
    with workprec(256):
        d = depgraph.ErrorDAG(C=exact(1), norms={"k": {1: arb(1), 2: arb(1)}})
        try:
            d.local("x", arb(1), owner="F_equation_certificate_value", order=1)
        except depgraph.ValueStyleDerivativeCharge:
            return True
    return False


def load_representatives(directory: Path) -> list[dict]:
    if not directory.exists():
        return []
    out = []
    for p in sorted(directory.glob("*.json")):
        rec = json.loads(p.read_text())
        if "m" in rec:
            out.append(rec)
    return out


def review(diagnostics: Path | None = None) -> dict:
    diagnostics = diagnostics or (NS / "diagnostics/representatives")
    reps = load_representatives(diagnostics)
    ids = universe.work_ids()
    shards = {w: universe.verify_shard_conservation(w, ids)
              for w in (1, 8, 16, 32, 64)}

    checks = {
        # ---- protected / frozen state
        "frozen_spec_hashes_unchanged": spec.verify_frozen_spec() == spec.FROZEN_HASHES,
        "frozen_successor_tree_unchanged": frozen_tree_unchanged(),
        "frozen_guard_conflict_is_not_a_mutation": (
            frozen_guard_conflict()["frozen_tree_byte_identical_to_freeze_manifest"]
            and frozen_guard_conflict()["start_head_git_object_manifest_unchanged"]
            and frozen_guard_conflict()["all_objected_paths_are_this_namespace"]),
        "only_new_namespace_written": only_new_namespace_touched(),
        "historical_verdicts_unchanged": (
            spec.CHECKPOINT["history"]["P5"] == "PARTIAL"
            and spec.CHECKPOINT["history"]["P5X"] == "PARTIAL"
            and spec.CHECKPOINT["history"]["historical_K1"] == "K1_INCOMPLETE_BUDGET"
            and spec.CHECKPOINT["LEVEL4_GLOBAL_CLOSURE"] == "NO"
            and spec.CHECKPOINT["scientific_verdict"] == "NOT_RUN"),
        # ---- frozen numbers preserved
        "budgets_preserved": spec.TOP_BUDGETS == FROZEN.TOP_BUDGETS,
        "nested_partition_preserved": sum(spec.NESTED_CANDIDATE.values()) == F(1, 25),
        "reserve_not_drawable": not (spec.RESERVE_DRAWABLE
                                     or spec.REDISTRIBUTION_ALLOWED),
        "cap_not_increased": spec.HARD_CAP_CPU_H == 1126,
        "precision_preserved": (spec.PRODUCTION_BITS == 256
                                and not spec.PRECISION_ESCALATION_ALLOWED
                                and not spec.DEGREE_ADAPTATION_ALLOWED),
        # ---- work universe
        "work_universe_exact_17978": len(ids) == 17978 == spec.TOTAL_UNITS,
        "work_ids_match_frozen_reference": ids == FROZEN.work_ids(spec.CELLS),
        "base_objects_12198": universe.unit_kind_counts()["object"] == 12198,
        "shard_conservation_all_worker_counts": all(
            s["union_equals_universe"] and s["no_overlap"] and s["no_dropped_work"]
            for s in shards.values()),
        "old_universe_and_checkpoints_rejected": _resume_rejection_works(),
        # ---- error algebra
        "derivative_dependency_complete": _dependency_complete(),
        "one_taylor_charge_style_1": _cover_refuses_second_derivative_charge(),
        "value_style_derivative_charge_refused": _value_style_charge_refused(),
        "all_m_coefficients_match_frozen": assembly.check_frozen_coefficient_table(),
        "no_leading_e_term": _no_leading_e(),
        # ---- evidence discipline
        "production_off": (spec.PRODUCTION_ENABLED is False
                           and all(not (NS / d).exists()
                                   for d in ("results", "certificates",
                                             "production_logs"))),
        "missing_certificates_not_passed": _missing_not_passed(reps),
        "curvature_is_whole_cell": _curvature_whole_cell(reps),
        "no_double_counting_in_measured_dags": all(
            r["dag_audit_mid"]["duplicate_edges"] == 0
            and r["dag_audit_cell"]["duplicate_edges"] == 0
            and r["dag_audit_mid"]["derivative_edges_all_cover"]
            for r in reps) if reps else None,
    }
    failed = [k for k, v in checks.items() if v is False]
    incomplete = [k for k, v in checks.items() if v is None]

    dependencies = {
        "derivative_dependency_propagation": "PASS",
        "whole_cell_M_R2": "PASS (CUSUM) / NOT_IMPLEMENTED (SR)",
        "all_m_certified_interval_assembly": "PASS (CUSUM) / NOT_IMPLEMENTED (SR)",
        "work_universe_17978": "PASS",
        "sharding_and_resume": "PASS",
        "representative_full_ledger": "PASS (CUSUM)" if reps else "NOT_COMPUTED",
        "precision_diagnostic_256_384_512": "see diagnostics/PRECISION.md",
        "cost_and_memory_model": "see benchmarks/",
        "complete_SR_raw_DAG": "NOT_IMPLEMENTED",
        "far_field_certificates": "NOT_IMPLEMENTED",
    }
    verdict = ("IMPLEMENTATION_INCOMPLETE" if failed or
               "NOT_IMPLEMENTED" in json.dumps(dependencies)
               else "READY_FOR_INDEPENDENT_ADJUDICATION")
    return {
        "review_kind": ("read-only self-adjudication of the implementation "
                        "namespace; not an independent human or agent review"),
        "checks": checks, "checks_failed": failed, "checks_incomplete": incomplete,
        "implementation_dependencies": dependencies,
        "frozen_successor_guard_conflict": frozen_guard_conflict(),
        "verdict": verdict,
        "production_ready": False,
        "scientific_verdict_changed": False,
        "frozen_scope_narrowed": False,
        "representative_records": len(reps),
    }


def _resume_rejection_works() -> bool:
    good = {"checkpoint_hash": spec.CHECKPOINT_SHA256,
            "cells_sha256": spec.CELLS_SHA256,
            "error_algebra_sha256": spec.ERROR_ALGEBRA_SHA256,
            "backend_hash": "B",
            "implementation_hash": universe.implementation_hash(),
            "precision_bits": 256, "obligation_universe_total": 17978}
    if not universe.admit_resume_record(good, backend_hash="B"):
        return False
    for field, bad in (("obligation_universe_total", 12255),
                       ("checkpoint_hash",
                        "a5d09f83078bf02ae5d015bfb08eb35429190f646cc51260f6ca72fce6e325ec"),
                       ("implementation_hash", "0" * 64),
                       ("backend_hash", "WRONG")):
        r = dict(good); r[field] = bad
        try:
            universe.admit_resume_record(r, backend_hash="B")
            return False
        except universe.ResumeRejected:
            pass
    return True


def _dependency_complete() -> bool:
    full = depgraph.reference_resolvent_errors(3, F(1, 100), F(2, 100),
                                               F(4, 5), F(1, 1000), F(1, 50))[1]
    omit_kf = 3 * (F(1, 1000) + F(1, 50))
    omit_s1 = 3 * (F(1, 1000) + F(4, 5) * F(9, 100))
    return full > omit_kf and full > omit_s1 and full == F(279, 1000)


def _no_leading_e() -> bool:
    with workprec(256):
        try:
            assembly.assemble(1, {0: arb(1)}, {}, leading_e=arb(1))
        except ValueError:
            return True
    return False


def _missing_not_passed(reps) -> bool:
    """Nothing unimplemented may report PASS."""
    import qualify
    sr = qualify.run_cell("SR", 0)
    if sr["status"] != "NOT_IMPLEMENTED" or "PASS" in json.dumps(sr):
        return False
    for r in reps:
        for m, led in r["m"].items():
            for name, gate in led["top_level_gates"].items():
                if name == "total" or not isinstance(gate, dict):
                    continue
                # A budget LINE with no computed usage must never read PASS.
                if "cap" in gate and gate.get("usage") is None \
                        and gate.get("status") == "PASS":
                    return False
    return True


def _curvature_whole_cell(reps) -> bool:
    """delta_cell must dominate delta_mid for every object with a live envelope."""
    if not reps:
        return None
    for r in reps:
        for name, meta in r["objects"].items():
            if F(meta["delta_cell"]) < F(meta["delta_mid"]):
                return False
            if F(meta["envelope"]) > 0 and \
                    F(meta["delta_cell"]) <= F(meta["delta_mid"]):
                return False
    return True


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--diagnostics", default=str(NS / "diagnostics/representatives"))
    ap.add_argument("--out")
    args = ap.parse_args()
    result = review(Path(args.diagnostics))
    text = json.dumps(result, indent=2, sort_keys=True)
    if args.out:
        Path(args.out).write_text(text + "\n")
    print(text)
    raise SystemExit(bool(result["checks_failed"]))
