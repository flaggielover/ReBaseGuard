"""C11R Phases 11-12 -- qualification from a clean environment, and the resource estimate.

Runs BEFORE any target execution and produces no target constant. The cost probe deliberately uses
a NON-TARGET weight (w = 1), so that measuring how expensive certification will be does not itself
certify anything about cell 306. Timing a target candidate "just to see how long it takes" would be
target science wearing a stopwatch.

If any mandatory item fails, the artifact records NO_TARGET_EXECUTION and the campaign stops here.
"""
from __future__ import annotations

import ast
import os
import pathlib
import platform
import resource
import shutil
import subprocess
import sys
import time
from fractions import Fraction as F

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import c11r_common as C
import c11r_idrift as I

items = []


def item(iid, name, ok, detail, mandatory=True):
    items.append({"id": iid, "name": name, "pass": bool(ok), "mandatory": mandatory,
                  "detail": detail})


def main() -> int:
    t0 = time.time()
    tbl = C.load(C.NS / "evidence" / "table" / "C11R_N9_TABLE.json")
    e_lo, e_hi = F(tbl["drift_domain"]["e_lo"]), F(tbl["drift_domain"]["e_hi"])
    BLOCK = I.Blk(e_lo, e_hi)

    # Q1 -- producer hashes
    mods = sorted((C.NS / "code").glob("*.py"))
    hashes = {m.name: C.sha256_file(m) for m in mods}
    item("Q1", "every producer module is hashed", len(hashes) >= 8,
         {"modules": len(hashes), "sha256": {k: v[:16] for k, v in hashes.items()}})

    # Q2 -- imports, by AST, with the original's graph and backend both forbidden
    forbidden = {"taboo_certify", "resolvent_certificate", "opnorms", "ra_certifier",
                 "fast_range", "intervals", "rebaseguard_certify", "rung3_engine", "spec"}
    backend = {"numpy", "scipy", "flint", "mpmath", "sympy", "gmpy2"}
    roots = set()
    for m in mods:
        for n in ast.walk(ast.parse(m.read_text())):
            if isinstance(n, ast.Import):
                roots |= {a.name.split(".")[0] for a in n.names}
            elif isinstance(n, ast.ImportFrom) and n.level == 0 and n.module:
                roots.add(n.module.split(".")[0])
    item("Q2", "no forbidden import and no forbidden arithmetic backend",
         not (roots & forbidden) and not (roots & backend),
         {"imported_roots": sorted(roots), "forbidden_hits": sorted(roots & forbidden),
          "backend_hits": sorted(roots & backend)})

    # Q3 -- the forbidden backend is genuinely absent from the environment
    tc = C.toolchain_present()
    item("Q3", "the original certifier's backend is absent from this environment",
         not tc["numpy"] and not tc["flint"], {"importlib_find_spec": tc})

    # Q4 -- manufactured validation passed
    val = C.load(C.NS / "evidence" / "validation" / "C11R_VALIDATION.json")
    item("Q4", "manufactured validation passed", val["VALIDATION_CLASS"] == "PASS",
         {"class": val["VALIDATION_CLASS"], "failed": val["failed"],
          "checks": len(val["checks"])})

    # Q5 -- scalar collapse, re-exercised here rather than read from the artifact
    sys.path.insert(0, str(C.C11 / "code"))
    import c11_certifier as X  # noqa: E402
    e = F(18355, 10000)
    PT = I.Blk(e, e)
    probes, ok5 = [], True
    for w in ({(0, 0): F(9)}, {(0, 0): F(99, 10), (0, 1): F(-3, 2)}):
        for p, m in ((F(0), F(0)), (F(3), F(1))):
            a, b = X.kernel_apply(w, p, m, e), I.kernel_apply_iv(w, p, m, PT)
            same = (a.lo, a.hi) == (b.lo, b.hi)
            ok5 = ok5 and same
            probes.append({"state": [str(p), str(m)], "bit_equal": same})
    item("Q5", "scalar collapse re-verified in this environment", ok5, {"probes": probes})

    # Q6 -- the atom decomposition, re-exercised
    one = {(0, 0): F(1)}
    full = I.kernel_apply_iv(one, F(0), F(0), BLOCK)
    hat = I.kernel_apply_iv(one, F(0), F(0), BLOCK, atom_removed=True)
    at = I.atom_contribution_iv(one, F(0), F(0), BLOCK)
    sep = max(full.lo - (hat + at).hi, (hat + at).lo - full.hi)
    item("Q6", "K_e = Khat_e + atom re-verified in this environment", sep <= 0,
         {"separation": float(sep), "K_e": [float(full.lo), float(full.hi)],
          "Khat_e": [float(hat.lo), float(hat.hi)], "atom": [float(at.lo), float(at.hi)]})

    # Q7 -- mutations
    mut = C.load(C.NS / "evidence" / "mutations" / "C11R_MUTATIONS.json")
    item("Q7", "no mutant survived", not mut["survivors"],
         {"class": mut["MUTATION_CLASS"], "survivors": mut["survivors"],
          "undetermined": mut["undetermined"],
          "note": ("UNDETERMINED entries depend on the runs artifact and are resolved after "
                   "execution; they are not counted as passes")})

    # Q8 -- deterministic reproduction: a deterministic producer twice, byte-identical
    eqp = C.NS / "evidence" / "equivalence" / "C11R_EQUIVALENCE.json"
    before = C.sha256_file(eqp)
    subprocess.run([sys.executable, "-B", str(C.NS / "code" / "c11r_equiv.py")],
                   capture_output=True, cwd=str(C.NS), env={**os.environ,
                                                            "PYTHONINTMAXSTRDIGITS": "0"})
    after = C.sha256_file(eqp)
    item("Q8", "a deterministic producer reproduces byte-identically", before == after,
         {"sha256_before": before[:16], "sha256_after": after[:16]})

    # Q9 -- the gate is frozen in git and its predicates carry no result language
    gate_rel = str((C.NS / "config" / "N9R_GATE_C11R.json").relative_to(C.REPO))
    gate_commits = C.git("log", "--format=%H", "--", gate_rel).splitlines()
    gate_dirty = bool(C.git("status", "--porcelain", "--", gate_rel))
    item("Q9", "the prospective gate is committed and unmodified",
         bool(gate_commits) and not gate_dirty,
         {"frozen_at": gate_commits[-1][:12] if gate_commits else None,
          "uncommitted_changes": gate_dirty})

    # ---------------- Phase 12: resource estimate -------------------------------------------
    # cost probe on a NON-TARGET weight, so measuring cost certifies nothing about cell 306
    probe_w = {(0, 0): F(1)}
    costs = {}
    for depth in (1, 2, 3):
        t = time.time()
        r = I.supersolution_margin_iv(probe_w, BLOCK, depth=depth, panels=16)
        costs[depth] = {"boxes": r["boxes"], "seconds": round(time.time() - t, 1)}
    growth = (costs[3]["seconds"] / costs[2]["seconds"]) if costs[2]["seconds"] else None
    est_d4 = round(costs[3]["seconds"] * growth, 0) if growth else None
    screen = C.load(C.NS / "evidence" / "screen" / "C11R_SCREEN.json")

    ru = resource.getrusage(resource.RUSAGE_SELF)
    du = shutil.disk_usage(str(C.REPO))
    estimate = {
        "candidates_to_certify": 2,
        "which": ["one K_e supersolution -> Abar",
                  "one Khat_e supersolution -> tau and C_T from the same certificate"],
        "screen_cost_measured_seconds": screen["seconds"],
        "cost_probe_non_target_weight": {"w": "1", "panels": 16, "by_depth": costs,
                                         "growth_per_level": round(growth, 2) if growth else None},
        "estimated_seconds_per_candidate_at_depth_4": est_d4,
        "estimated_total_wall_seconds": (est_d4 * 2) if est_d4 else None,
        "estimated_cpu_hours": round((est_d4 * 2) / 3600, 3) if est_d4 else None,
        "peak_rss_mb_so_far": round(ru.ru_maxrss / (1024 * 1024 if sys.platform == "darwin"
                                                    else 1024), 1),
        "disk_free_gb": round(du.free / 1024 ** 3, 1),
        "environment": {"python": platform.python_version(), "platform": platform.platform(),
                        "machine": platform.machine()},
        "smallest_adequate_environment": "this laptop",
        "remote_provisioning": "NOT REQUIRED; AWS is forbidden and Vultr is not authorised",
        "retry_policy": ("a candidate that fails to certify is recorded as it stands. Deepening is "
                         "permitted only after re-screening, and a POINTWISE_REFUTED candidate is "
                         "never retried at greater depth"),
        "resource_cap": {"wall_seconds": 5400, "candidates": 4, "max_depth": 5},
    }

    mand_fail = [i["id"] for i in items if i["mandatory"] and not i["pass"]]
    out = {"schema": "C11R_QUALIFICATION/1",
           "runs_before": "any target execution",
           "produces_target_constants": False,
           "items": items, "mandatory_failures": mand_fail,
           "QUALIFICATION_CLASS": "PASS" if not mand_fail else "NO_TARGET_EXECUTION",
           "resource_estimate": estimate,
           "seconds": round(time.time() - t0, 1)}
    s = C.write_evidence(C.NS / "evidence" / "qualification" / "C11R_QUALIFICATION.json", out)
    for i in items:
        print(f"  {'PASS' if i['pass'] else 'FAIL'}  {i['id']}  {i['name'][:66]}")
    print(f"\ncost probe (non-target w = 1, panels 16): " +
          ", ".join(f"d{d}={v['seconds']}s/{v['boxes']}boxes" for d, v in costs.items()))
    print(f"growth per level {estimate['cost_probe_non_target_weight']['growth_per_level']}; "
          f"depth 4 estimated {est_d4}s per candidate, "
          f"{estimate['estimated_cpu_hours']} CPU-hours total")
    print(f"\nQUALIFICATION_CLASS = {out['QUALIFICATION_CLASS']}  failures={mand_fail}")
    print(f"wrote evidence/qualification/C11R_QUALIFICATION.json sha256 {s[:16]}...")
    return 0 if not mand_fail else 1


if __name__ == "__main__":
    raise SystemExit(main())
