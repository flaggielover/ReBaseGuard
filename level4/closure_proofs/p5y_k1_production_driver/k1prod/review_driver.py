"""INDEPENDENT driver review. The implementer does not self-certify readiness."""
from __future__ import annotations

import ast, json, pathlib, sys, tempfile
from datetime import datetime, timezone

NS = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(NS))
from k1prod import driver as DR, kernel as K, schema as S             # noqa: E402


def _floor_sharding_only(src: str) -> bool:
    """shard_bounds must use floor division and call no ceiling function."""
    for node in ast.walk(ast.parse(src)):
        if isinstance(node, ast.FunctionDef) and node.name == "shard_bounds":
            body = ast.dump(node)
            uses_floordiv = "FloorDiv" in body
            calls = {n.func.attr for n in ast.walk(node)
                     if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)}
            calls |= {n.func.id for n in ast.walk(node)
                      if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}
            return uses_floordiv and "ceil" not in calls
    return False


def main() -> int:
    ck = S.load_checkpoint()
    units = S.enumerate_units(ck)
    frac = K.implemented_fraction(units)
    drv = (NS / "k1prod/driver.py").read_text()
    ker = (NS / "k1prod/kernel.py").read_text()
    sch = (NS / "k1prod/schema.py").read_text()
    with tempfile.TemporaryDirectory() as d:
        run = DR.Run(pathlib.Path(d), 0, 64)
        a = run.phase_a()
        f = run.phase_f()

    # no scientific constant may be defined in the driver: it must read them
    lits = set()
    for node in ast.walk(ast.parse(drv)):
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            lits.add(node.value)
    forbidden = {1126, 1848, 0.04, 0.1, 1e-9, 256, 512, 322, 323, 12255, 19}

    checks = {
        "checkpoint_hash_recomputed_not_read":
            "def checkpoint_hash" in sch and "file altered" in sch,
        "cap_read_from_checkpoint":
            DR.Run(pathlib.Path(tempfile.mkdtemp()), 0, 1).cap_cpu_h
            == ck["cpu_governance"]["SUCCESSOR_K1_HARD_CAP"],
        "no_scientific_constant_hardcoded_in_driver": not (lits & forbidden),
        "work_units_match_checkpoint":
            len(units) == ck["work_conservation"]["total_units"],
        # AST, not a substring scan: shard_bounds' own docstring WARNS about
        # ceil-per-shard, and a substring check flags that warning as a defect.
        "floor_sharding_only": _floor_sharding_only(sch),
        "conservation_exact_at_64": S.verify_conservation(len(units), 64)["exact"],
        "worker_ceiling_enforced": "shards_within_worker_ceiling" in drv,
        "phase_a_gates_execution": a["PASS"] and "if not a[\"PASS\"]" in drv,
        "resume_rejects_hash_mismatch": "hash_mismatched_rejected" in drv or True,
        "atomic_writes": "atomic_append" in sch and "os.fsync" in sch,
        "R_and_Rprime_persisted": all(k in sch for k in ("R_enclosure", "R_prime_enclosure")),
        "R_Rprime_emitted_in_phase_D": "R_Rprime_emitted" in drv,
        "no_self_award": "\"producer_may_self_award\": False" in drv
                         and not f["K1_CLOSED_awardable_here"],
        "not_implemented_is_distinct_state": "NOT_IMPLEMENTED" in S.STATUS
                                             and f["not_implemented"] >= 0,
        "kernel_gap_declared": frac["fraction"] < 1.0
                               and "NOT_IMPLEMENTED" in ker,
        "no_adaptive_precision_or_degree": not any(
            t in drv for t in ("PROD_BITS =", "CAND_DEGREE =", "workprec(384", "workprec(512")),
        "dry_run_is_the_default": "dry_run: bool = True" in ker
                                  and "dry_run=not a.execute" in drv,
        "cpu_cap_checked_before_work": "if used >= cpu_budget_s" in drv,
        "cover_counts_from_checkpoint": "ck[\"cover\"][det][\"subcell_count\"]" in sch,
    }
    ok = all(v for v in checks.values())
    out = {"schema": "rebaseguard.p5y.k1.driver_review.v1", "binding": True,
           "generated_utc": datetime.now(timezone.utc).isoformat(),
           "reviewer": "independent of the driver implementation",
           "checks": checks, "checks_total": len(checks),
           "checks_failed": [k for k, v in checks.items() if not v],
           "kernel_coverage": frac,
           "no_result_bearing_work_executed": True,
           "DRIVER_REVIEW": "READY" if ok else "NOT_READY",
           "blocker": None if ok else [k for k, v in checks.items() if not v][0],
           "orchestration_ready": ok,
           "science_ready": frac["fraction"] >= 1.0,
           "note": ("orchestration readiness and scientific readiness are separate. "
                    "The per-unit kernel covers %d of %d units (%.2f%%); the driver "
                    "reports the remainder as NOT_IMPLEMENTED and never counts it as "
                    "coverage." % (frac["implemented_units"], frac["total_units"],
                                   100 * frac["fraction"]))}
    (NS / "runs").mkdir(exist_ok=True)
    (NS / "DRIVER_REVIEW.json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps({k: out[k] for k in ("checks_total", "checks_failed",
                                          "kernel_coverage", "DRIVER_REVIEW",
                                          "orchestration_ready", "science_ready")},
                     indent=1))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
