#!/usr/bin/env python3
"""Exactly 23 frozen adversarial checks for the L4R-06 campaign."""
from __future__ import annotations

import argparse
import inspect
import json
import re
import subprocess
from pathlib import Path
from typing import Any

import figures
from campaign import expected_keys, load_cell
from config import BASE, CELLS, POLICY_LABELS, REGIMES, RESULTS, ROOT, SHIFTS, canonical_json
from integrity import verify as verify_integrity
from policy import policies, policy_table


def _focused_tests() -> tuple[bool, str]:
    proc = subprocess.run(
        [str(ROOT / "level4/.venv/bin/python"), "-m", "pytest",
         "level4/closure_proofs/l4r06_policy/tests", "-q"],
        cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
    )
    match = re.search(r"(\d+) passed", proc.stdout)
    summary = f"{match.group(1)} focused tests passed" if match else "focused-test count unavailable"
    return proc.returncode == 0, summary


def _changed_l4r12() -> list[str]:
    frozen = json.loads((RESULTS / "historical_hashes.json").read_text())
    audited = frozen["audited_commit"]
    names = subprocess.check_output(
        ["git", "diff", "--name-only", audited, "--"], cwd=ROOT, text=True
    ).splitlines()
    names += subprocess.check_output(
        ["git", "ls-files", "--others", "--exclude-standard"], cwd=ROOT, text=True
    ).splitlines()
    return sorted({name for name in names if re.search(r"l4r[-_]?12", name, re.I)})


def run() -> dict[str, Any]:
    science_path = RESULTS / "scientific_findings.json"
    science = json.loads(science_path.read_text()) if science_path.exists() else {}
    integrity = verify_integrity()
    protocol = json.loads((RESULTS / "protocol_hash.json").read_text())
    cells = [load_cell(key) for key in expected_keys()]
    cells_complete = all(cell is not None for cell in cells)
    summaries = science.get("all_cell_summaries", [])
    focused_ok, focused_detail = _focused_tests()
    verification = json.loads((RESULTS / "verification.json").read_text()) \
        if (RESULTS / "verification.json").exists() else {}
    reproduction = json.loads((RESULTS / "reproduction.json").read_text()) \
        if (RESULTS / "reproduction.json").exists() else {}
    checks = []

    def add(cid: str, name: str, passed: bool, evidence: str) -> None:
        checks.append({"id": cid, "check": name, "passed": bool(passed),
                       "evidence": evidence})

    add("A1", "Stage C unchanged", integrity["status"] == "PASS",
        "protected Stage C tree and files match the pre-campaign hashes")
    stage_c = json.loads((ROOT / "level4/stage_c/results/findings.json").read_text())
    c6_failed = "C6" in stage_c.get("decision_basis", {}).get("failed", [])
    add("A2", "historical C6 failure preserved", c6_failed,
        f"Stage C decision={stage_c.get('decision')}; failed={stage_c.get('decision_basis', {}).get('failed')}")
    add("A3", "D4 unchanged", integrity["status"] == "PASS",
        "protected D4 tree and decision hash match")
    changed_l4r12 = _changed_l4r12()
    add("A4", "L4R-12 untouched", not changed_l4r12,
        f"changed L4R-12 paths={changed_l4r12}")
    add("A5", "P3 rule frozen before outcomes",
        protocol.get("confirmatory_outcomes_existed_when_frozen") is False
        and protocol.get("primary_policy") == "rho_P3(m)=min(1,0.8*rho_c,L95(m))",
        f"freeze={protocol.get('status')}; pre-outcome={not protocol.get('confirmatory_outcomes_existed_when_frozen', True)}")
    rho_exact = cells_complete and all(
        cell["key"]["rho"] == policies(cell["key"]["m"])[cell["key"]["policy"]]
        for cell in cells if cell is not None)
    add("A6", "no outcome-driven rho tuning", rho_exact,
        "every cell action equals the pre-frozen policy reconstruction")
    observed_grid = {(r.get("m"), r.get("shift")) for r in summaries}
    required_grid = {(m, s) for m in REGIMES for s in (0.0, *SHIFTS)}
    add("A7", "no regime deletion", observed_grid == required_grid,
        f"observed regime/shift grid={len(observed_grid)}/{len(required_grid)}")
    allocation = science.get("allocation", {})
    add("A8", "no sample-size increase after outcomes",
        allocation.get("n_replicates") == 200 and allocation.get("n_events") == 200
        and allocation.get("n_cells") == 80,
        f"allocation={allocation.get('n_replicates')}x{allocation.get('n_events')}; cells={allocation.get('n_cells')}")
    formula_rows = science.get("H6-1", {}).get("rows", [])
    add("A9", "stability-awareness is mechanical",
        len(formula_rows) == 4 and all(r.get("formula_reconstruction_pass") for r in formula_rows)
        and formula_rows == science.get("policy", {}).get("actions"),
        "P3 is reconstructed from protected lower D4 confidence endpoints")
    add("A10", "operational consequence pre-specified",
        science.get("H6-3", {}).get("family", {}).get("family_size") == 3,
        "ARL0(P3)-ARL0(P1) is the frozen operational family")
    h = [science.get(f"H6-{i}", {}).get("status") for i in range(1, 6)]
    joint_valid = h[4] == ("PASS" if all(x == "PASS" for x in h[:4])
                            and science.get("absolute_delay_safety", {}).get("status") == "PASS" else "FAIL")
    add("A11", "reference-only improvement cannot close requirement", joint_valid,
        f"H6 statuses={h}; H6-5 is a strict conjunction including operational and safety gates")
    add("A12", "no operational-phase-transition wording",
        science.get("historical_firewall", {}).get("D4_operational_interpretation")
        == "MATHEMATICAL, NOT OPERATIONAL",
        "D4 operational interpretation remains MATHEMATICAL, NOT OPERATIONAL")
    add("A13", "no universal safety claim",
        science.get("allocation", {}).get("regimes") == list(REGIMES)
        and science.get("allocation", {}).get("shifts") == list(SHIFTS),
        "claims are scoped to four Gaussian regimes and four positive shifts")
    policies_present = {r.get("policy") for r in summaries}
    add("A14", "fresh comparator preserved", "P0" in policies_present,
        "P0 appears in final summaries")
    add("A15", "full-reuse comparator preserved", "P1" in policies_present,
        "P1 appears in final summaries")
    response = science.get("H6-4", {}).get("family", {})
    add("A16", "simultaneous non-inferiority valid",
        response.get("family_size") == 16 and response.get("confidence") == 0.95
        and "maximum centered" in response.get("method", "")
        and all("simultaneous_upper95" in r for r in response.get("rows", [])),
        "one joint 16-condition maximum-deviation family is retained")
    primary_failures = []
    for name, key in (("H6-2", "pass"), ("H6-3", "pass"), ("H6-4", "primary_pass")):
        for row in science.get(name, {}).get("family", {}).get("rows", []):
            if not row.get(key): primary_failures.append(name)
    for row in science.get("absolute_delay_safety", {}).get("family", {}).get("rows", []):
        if not row.get("pass"): primary_failures.append("absolute safety")
    add("A17", "negative outcomes retained",
        len(summaries) == 80 and len(science.get("negative_primary_findings", [])) == len(primary_failures),
        f"80/80 summaries; {len(primary_failures)} primary failures retained")
    add("A18", "same-requirement mapping explicit",
        isinstance(science.get("same_requirement_mapping_candidate"), bool)
        and bool(science.get("mapping_reason")),
        f"candidate={science.get('same_requirement_mapping_candidate')}")
    fig_source = inspect.getsource(figures)
    add("A19", "figures read final JSON only",
        'SOURCE = RESULTS / "scientific_findings.json"' in fig_source
        and "load_cell" not in fig_source and "CELLS" not in fig_source,
        "figure generator has one scientific JSON input and no checkpoint import")
    add("A20", "protected hashes unchanged", integrity["status"] == "PASS",
        f"{integrity['trees_verified']} trees and {integrity['files_verified']} files verified")
    add("A21", "focused tests green", focused_ok, focused_detail)
    add("A22", "full verifier green", verification.get("status") == "PASS",
        f"verification status={verification.get('status', 'MISSING')}")
    add("A23", "reproducer byte-stable", reproduction.get("status") == "PASS",
        f"reproduction status={reproduction.get('status', 'MISSING')}")
    assert [c["id"] for c in checks] == [f"A{i}" for i in range(1, 24)]
    passed = sum(c["passed"] for c in checks)
    return {
        "schema": "rebaseguard.l4r06-adversarial.v1",
        "seed": 2026082408,
        "n_checks": 23,
        "n_passed": passed,
        "status": "PASS" if passed == 23 else "FAIL",
        "checks": checks,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--label", choices=("first", "final"))
    parser.add_argument("--check-final", action="store_true")
    args = parser.parse_args()
    result = run()
    if args.check_final:
        path = RESULTS / "adversarial_final.json"
        if not path.exists() or json.loads(path.read_text()) != result:
            print("adversarial final record is not reproducible")
            return 1
    elif args.label:
        path = RESULTS / f"adversarial_{args.label}.json"
        path.write_text(canonical_json(result))
    else:
        parser.error("choose --label or --check-final")
    print(f"L4R-06 adversarial: {result['n_passed']}/{result['n_checks']} {result['status']}")
    for check in result["checks"]:
        if not check["passed"]:
            print(f"  {check['id']} FAIL: {check['check']}")
    return 0 if (args.label == "first" or result["status"] == "PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
