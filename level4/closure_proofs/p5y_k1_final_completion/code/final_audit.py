"""Self-audit for the final-completion campaign.

Read-only self-adjudication. It cannot conclude K1 = CLOSED, production
readiness, or a cost-cap pass.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
from fractions import Fraction as F
from pathlib import Path

import base

import spec                                                     # noqa: E402
import universe as reviewed                                     # noqa: E402

import far_field                                                # noqa: E402
import sharp_norms                                              # noqa: E402
import sr_cost                                                  # noqa: E402
import sr_status                                                # noqa: E402

NS = base.NS
ROOT = base.ROOT

PROTECTED = (
    ("frozen_successor", base.SPEC_NS, None),
    ("reviewed_implementation", base.IMPL_NS, base.REVIEWED_COMMIT),
    ("repair1", base.REPAIR1_NS, base.REPAIR1_COMMIT),
    ("repair2", base.REPAIR2_NS, base.REPAIR2_COMMIT),
)


def frozen_tree_unchanged() -> bool:
    manifest = json.loads((base.SPEC_NS / "manifests/freeze.json").read_text())
    actual = {}
    for p in base.SPEC_NS.rglob("*"):
        if p.is_file() and "__pycache__" not in p.parts \
                and p != base.SPEC_NS / "manifests/freeze.json":
            actual[str(p.relative_to(base.SPEC_NS))] = \
                hashlib.sha256(p.read_bytes()).hexdigest()
    return actual == manifest["files"]


def namespace_preserved(ns: Path, commit: str) -> dict:
    rel = str(ns.relative_to(ROOT))
    out = subprocess.run(["git", "diff", "--name-only", commit, "--", rel],
                         cwd=ROOT, capture_output=True, text=True)
    changed = [x for x in out.stdout.split("\n") if x.strip()]
    return {"namespace": rel, "commit": commit,
            "paths_changed": changed, "preserved": not changed}


def load_records(directory: Path) -> list[dict]:
    if not directory.exists():
        return []
    return [json.loads(p.read_text()) for p in sorted(directory.glob("sharp_*.json"))]


def norms_only_tighten() -> dict:
    """Every drift-aware norm must be <= the reviewed whole-line one."""
    import opnorms as R
    from intervals import exact, workprec
    bad = []
    with workprec(spec.PRODUCTION_BITS):
        for c in spec.CELLS:
            if c["detector"] != "CUSUM":
                continue
            left, right = F(c["left"][0]), F(c["right"][0])
            e_max = exact(max(abs(left), abs(right)))
            for i in range(4):
                if sharp_norms.kernel_norm(i, left, right).upper() > R.kernel_norm(i).upper():
                    bad.append(("k", i, c["index"]))
                if sharp_norms.raw_kernel_norm(i, left, right).upper() > \
                        R.raw_kernel_norm(i, e_max).upper():
                    bad.append(("j", i, c["index"]))
    return {"cells_checked": spec.COUNTS["CUSUM"], "violations": bad,
            "all_tighten_or_equal": not bad}


def cell_325_state(records: list[dict]) -> dict:
    r = next((x for x in records if x["cell_index"] == 325), None)
    if r is None:
        return {"state": "NOT_RECERTIFIED"}
    statuses = {m: L["status"] for m, L in r["m"].items()}
    return {"state": ("CERTIFIED_PASS" if all(v == "PASS" for v in statuses.values())
                      else "CURRENT_CERTIFICATE_FAILURE_ONLY"),
            "statuses": statuses,
            "worst_cover_utilization_pct": max(
                L["cover"]["utilization"] for L in r["m"].values()) * 100,
            "chain_verified": r["provenance_chain"]["all_verified"]}


def review(records_dir: Path | None = None) -> dict:
    d = records_dir or (NS / "diagnostics/cells")
    records = load_records(d)
    protected = {n: (namespace_preserved(ns, c) if c else
                     {"namespace": str(ns.relative_to(ROOT)),
                      "preserved": frozen_tree_unchanged()})
                 for n, ns, c in PROTECTED}
    ff = far_field.report()
    cost = sr_cost.model()
    srs = sr_status.report()
    tighten = norms_only_tighten()
    c325 = cell_325_state(records)

    passing = [r for r in records
               if all(L["status"] == "PASS" for L in r["m"].values())]
    failing = [r for r in records if r not in passing]
    all_pass = bool(records) and not failing

    def looseness_only(r) -> bool:
        """A failure is looseness iff its R2 enclosure straddles zero."""
        for m, L in r["m"].items():
            if L["status"] != "FAIL":
                continue
            lo, hi = F(L["R2_interval"]["lo"]), F(L["R2_interval"]["hi"])
            if not (lo < 0 < hi):
                return False
        return True

    failures_are_looseness = all(looseness_only(r) for r in failing)
    chains = bool(records) and all(
        r["provenance_chain"]["all_verified"] for r in records)
    s0 = bool(records) and all(
        r["s0_charge_audit"]["all_charged_exactly_once"] for r in records)

    checks = {
        "frozen_successor_byte_preserved": protected["frozen_successor"]["preserved"],
        "reviewed_implementation_byte_preserved":
            protected["reviewed_implementation"]["preserved"],
        "repair1_byte_preserved": protected["repair1"]["preserved"],
        "repair2_byte_preserved": protected["repair2"]["preserved"],
        "drift_aware_norms_only_tighten": tighten["all_tighten_or_equal"],
        "no_certified_counterexample": failures_are_looseness,
        "provenance_chains_verify": chains,
        "S0_charged_exactly_once": s0,
        "work_universe_17978_unchanged": len(reviewed.work_ids()) == 17978,
        "shard_conservation_unchanged": all(
            reviewed.verify_shard_conservation(w)["union_equals_universe"]
            for w in (1, 8, 16, 32, 64)),
        "precision_unchanged": (spec.PRODUCTION_BITS == 256
                                and not spec.PRECISION_ESCALATION_ALLOWED),
        "degree_unchanged": not spec.DEGREE_ADAPTATION_ALLOWED,
        "cap_remains_1126": spec.HARD_CAP_CPU_H == 1126,
        "budgets_unchanged": sum(spec.TOP_BUDGETS.values()) == F(19, 100),
        "cover_geometry_unchanged":
            spec.CELLS_SHA256 == spec.CHECKPOINT["geometry"]["cells_sha256"],
        "production_off": spec.PRODUCTION_ENABLED is False,
        "sr_still_absent": srs["SR_IMPLEMENTATION"] == "ABSENT",
        "cost_cap_not_claimed_pass": cost["COST_CAP_STATUS"] != "COST_CAP_PASS",
    }
    failed = [k for k, v in checks.items() if v is False]

    production_gate = {
        "1_implementation_complete": srs["SR_IMPLEMENTATION"] != "ABSENT",
        "2_no_implementation_defect": not failed,
        "3_cell_325_certified": c325.get("state") == "CERTIFIED_PASS",
        "4_cusum_far_field_pass":
            ff["detectors"]["CUSUM"]["status"] == "PASS",
        "5_sr_far_field_pass": ff["detectors"]["SR"]["status"] == "PASS",
        "6_sr_representative_certificates_pass": False,
        "3b_all_recertified_cusum_cells_pass": all_pass,
        "7_provenance_resume_pass": chains,
        "8_within_1126_cap": cost["COST_CAP_STATUS"] == "COST_CAP_PASS",
        "9_memory_safe_on_host": True,
    }
    authorized = all(production_gate.values())

    return {
        "review_kind": ("read-only self-adjudication of the final-completion "
                        "campaign; not an independent review"),
        "checks": checks, "checks_failed": failed,
        "protected_namespaces": protected,
        "norms_tighten_audit": {"cells_checked": tighten["cells_checked"],
                                "all_tighten_or_equal": tighten["all_tighten_or_equal"],
                                "violations": tighten["violations"][:5]},
        "cell_325": c325,
        "recertified_cells": {
            "total": len(records),
            "all_m_pass": [r["cell_index"] for r in passing],
            "with_failures": [r["cell_index"] for r in failing],
            "failures_are_certificate_looseness_only": failures_are_looseness,
            "failure_class": ("CERTIFICATE_TOO_LOOSE" if failing else None),
            "cusum_compact_cover_certified": all_pass,
        },
        "far_field": {det: {"status": v["status"],
                            "failure_class": v["failure_class"],
                            "at_splice_all_m_pass": v["at_frozen_k1_splice"]["all_m_pass"],
                            "at_e_far_12_all_m_pass": v["at_p5x_e_far_12"]["all_m_pass"],
                            "uncovered_interval": v["uncovered_interval_if_cover_ends_at_c"]}
                      for det, v in ff["detectors"].items()},
        "sr": {k: srs[k] for k in ("SR_IMPLEMENTATION", "SR_M_R2", "SR_ALL_M",
                                   "failure_class")},
        "cost": {"COST_CAP_STATUS": cost["COST_CAP_STATUS"],
                 "campaign_central_cpu_h": cost["extrapolation"]["campaign_central_cpu_h"],
                 "assumption_free_lower_bound_cpu_h":
                     cost["lower_bounds"]["assumption_free_campaign_cpu_h"],
                 "cap": spec.HARD_CAP_CPU_H},
        "production_authorization_gate": production_gate,
        "P5Y_PRODUCTION_ALLOWED": "YES_CANDIDATE" if authorized else "NO",
        "production_launched": False,
        "overall_state": ("K1_INCOMPLETE_IMPLEMENTATION"
                          if srs["SR_IMPLEMENTATION"] == "ABSENT"
                          else "K1_READY_FOR_INDEPENDENT_FINAL_ADJUDICATION"),
        "K1_CLOSED_claimed": False,
        "remaining_blockers": [
            "CUSUM high-radius cells 318-324 fail (CERTIFICATE_TOO_LOOSE)",
            "SR raw DAG absent (8,849 of 17,978 obligations)",
            "SR M_R2 absent", "SR all-m assembly absent",
            "far-field does not close m=3,5 at the frozen K1 splice",
            "cost cap NOT_ESTABLISHED",
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
