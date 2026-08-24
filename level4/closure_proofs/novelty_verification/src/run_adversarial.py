#!/usr/bin/env python3
"""Run the 18 frozen adversarial checks against persisted audit artifacts."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path


BASE = Path(__file__).resolve().parents[1]
ROOT = BASE.parents[2]


def load(relative: str):
    return json.loads((BASE / relative).read_text())


def tree_digest(root: Path) -> tuple[int, str]:
    digest = hashlib.sha256()
    files = [p for p in sorted(root.rglob("*")) if p.is_file() and "__pycache__" not in p.parts and p.suffix != ".pyc"]
    for path in files:
        rel = path.relative_to(ROOT).as_posix().encode()
        data = path.read_bytes()
        digest.update(len(rel).to_bytes(8, "big")); digest.update(rel)
        digest.update(len(data).to_bytes(8, "big")); digest.update(data)
    return len(files), digest.hexdigest()


def protected_ok(name: str) -> bool:
    frozen = load("results/historical_hashes.json")["roots"][name]
    count, digest = tree_digest(ROOT / name)
    return count == frozen["files"] and digest == frozen["sha256"]


def add(checks, check_id, name, passed, detail):
    checks.append({"id": check_id, "name": name, "passed": bool(passed), "detail": detail})


def run() -> dict:
    checks = []
    matrix = load("results/prior_art_matrix.json")
    firewall = load("results/claim_firewall.json")
    decision = load("results/decision.json")
    manifest = load("results/search_manifest.json")
    snowball = load("bibliography/snowball_assessment.json")
    audits = load("bibliography/high_audits.json")
    bibliography = load("results/bibliography.json")

    add(checks, "A1", "historical Stage-F artifacts unchanged", protected_ok("level4/stage_f"), "content hash matches frozen baseline")
    add(checks, "A2", "post-closure re-audit unchanged", protected_ok("level4/re_audit_post_closure"), "content hash matches frozen baseline")
    d4 = protected_ok("level4/closure_proofs/d4_phase_map") and load("../d4_phase_map/results/decision.json")["decision"] == "D4-PHASE-MAP-CLOSED"
    add(checks, "A3", "D4 closure unchanged", d4, "protected D4 hash and scoped decision preserved")

    science_tokens = re.compile(r"numpy\.random|default_rng|monte.?carlo|simulate_cycles|run_campaign", re.I)
    source_text = "\n".join(
        path.read_text(errors="ignore")
        for path in (BASE / "src").rglob("*.py")
        if path.name != "run_adversarial.py"
    )
    add(checks, "A4", "no new scientific simulation", not science_tokens.search(source_text), "audit code contains no simulation/RNG campaign")

    safe_text = "\n".join((BASE / name).read_text() for name in ("PUBLICATION_SAFE_CLAIMS.md", "RESUME_SAFE_CLAIMS.md"))
    add(checks, "A5", "no unsupported first", not re.search(r"\bfirst\b", safe_text, re.I), "current safe outputs contain no priority use of first")
    add(checks, "A6", "no unsupported first-ever", not re.search(r"\bfirst-ever\b", safe_text, re.I), "current safe outputs contain no first-ever")
    add(checks, "A7", "no unsupported unprecedented", not re.search(r"\bunprecedented\b", safe_text, re.I), "current safe outputs contain no unprecedented")

    direct_ids = set(matrix["direct_work_ids"])
    audit_ids = {row["work_id"] for row in audits["audits"]}
    by_id = {row["work_id"]: row for row in bibliography["works"]}
    direct_valid = all(work_id in audit_ids and by_id[work_id]["access_level"] in {"FULL-TEXT", "ABSTRACT"} for work_id in direct_ids)
    add(checks, "A8", "no paper classified DIRECT from title alone", direct_valid, f"DIRECT count={len(direct_ids)}; every DIRECT would require text audit")
    inaccessible = [row for row in bibliography["works"] if row["access_level"] in {"METADATA-ONLY", "ACCESS-UNAVAILABLE"}]
    add(checks, "A9", "inaccessible papers explicitly marked", bool(inaccessible) and all("unavailable" in row["evidence_basis"].lower() or "metadata" in row["evidence_basis"].lower() for row in inaccessible), f"explicitly marked={len(inaccessible)}")
    high_ids = set(matrix["high_partial_work_ids"])
    add(checks, "A10", "threatening prior art preserved", len(high_ids) == 9 and "W08" in high_ids and high_ids <= audit_ids, "nine HIGH-PARTIAL works including W08 are persisted and audited")

    completed = [row for row in manifest["runs"] if row["status"] == "COMPLETED"]
    query_ok = len(completed) == 72 and all(row["query"] and row["request_url"] and row["returned"] == 20 for row in completed)
    add(checks, "A11", "search query provenance complete", query_ok, "36 frozen queries completed in each of two indexes")
    snow_ok = snowball["stopping_rule_satisfied"] and len(snowball["rounds"]) == 2 and all(row["new_direct"] == row["new_high_partial"] == 0 for row in snowball["rounds"])
    add(checks, "A12", "snowball provenance complete", snow_ok, "two backward/forward rounds persisted; stopping rule satisfied")
    matrix_ok = len(matrix["rows"]) == 33 and all(set(row["components"]) == {f"C{i}" for i in range(1, 12)} for row in matrix["rows"])
    add(checks, "A13", "C1-C11 matrix complete", matrix_ok, "33 rows x 11 components")

    generated = subprocess.run([str(ROOT / "level4/.venv/bin/python"), str(BASE / "src/generate_artifacts.py"), "--check"], cwd=ROOT, capture_output=True, text=True)
    add(checks, "A14", "claim firewall generated from canonical JSON", generated.returncode == 0 and "byte-stable" in generated.stdout, generated.stdout.strip() or generated.stderr.strip())
    derived = all(decision["criteria"].values()) and decision["decision"] == "NOVELTY-VERIFICATION-CLOSED" and decision["novelty_position"] == "N2"
    add(checks, "A15", "decision mechanically derived", derived, "NV1-NV12 true => CLOSED; partial overlap => N2")
    external_ok = protected_ok("level4/stage_e") and decision["remaining_fail_open_blockers"] == [{"name": "SEMI-REAL EXTERNAL VALIDATION", "type": "SCIENTIFIC"}]
    add(checks, "A16", "external-validation blocker untouched", external_ok, "Stage E hash preserved; blocker remains explicit")

    verification_path = BASE / "results/verification.json"
    verification = json.loads(verification_path.read_text()) if verification_path.exists() else {}
    verifier_ok = verification.get("status") == "PASS" and verification.get("current_distinct_checks") == 983
    add(checks, "A17", "repository verifier green", verifier_ok, "verification record missing/not final" if not verifier_ok else "983 distinct checks recorded PASS")

    status = subprocess.run(["git", "status", "--porcelain"], cwd=ROOT, capture_output=True, text=True, check=True).stdout.splitlines()
    unauthorized = []
    for line in status:
        path = line[3:]
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        if not path.startswith("level4/closure_proofs/novelty_verification/"):
            unauthorized.append(path)
    all_protected = all(protected_ok(name) for name in load("results/historical_hashes.json")["roots"])
    add(checks, "A18", "clean-tree/hash integrity", not unauthorized and all_protected, f"unauthorized dirty paths={unauthorized}; all protected hashes={all_protected}")

    passed = sum(row["passed"] for row in checks)
    return {"schema": "rebaseguard.novelty-adversarial.v1", "passed": passed, "total": len(checks), "status": "PASS" if passed == len(checks) else "FAIL", "checks": checks}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", help="relative output path under campaign root")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = run()
    if args.output:
        path = BASE / args.output
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(f"adversarial: {result['passed']}/{result['total']} {result['status']}")
    for row in result["checks"]:
        if not row["passed"]:
            print(f"  {row['id']} FAIL: {row['name']} — {row['detail']}")
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
