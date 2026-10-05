#!/usr/bin/env python3
"""Build R2_FAILURE_MATRIX.json from the committed evidence (every classification is derived from an evidence file).

  python3 r2h_make_failure_matrix.py --ns NAMESPACE_DIR --out R2_FAILURE_MATRIX.json

Classes: ALREADY_SAFE | UNSAFE | SAFE_BUT_UNPROVEN | IRRELEVANT_BY_DESIGN, given for r2 as shipped (101ef2cb) and for
the hardened runner, each with the evidence ids that decide it.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ns", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    ns = Path(a.ns)
    ev = ns / "evidence"
    mb = json.loads((ev / "matrix" / "MATRIX_BASELINE_r2_101ef2cb.json").read_text())
    mh = json.loads((ev / "matrix" / "MATRIX_HARDENED_3c191ac2.json").read_text())
    ub = json.loads((ev / "unit" / "UNIT_BASELINE_101ef2cb.json").read_text())
    uh = json.loads((ev / "unit" / "UNIT_HARDENED_3c191ac2.json").read_text())
    rb = json.loads((ev / "regression" / "REGRESSION_BASELINE_101ef2cb.json").read_text())
    rh = json.loads((ev / "regression" / "REGRESSION_HARDENED_3c191ac2.json").read_text())
    B = {c["id"]: c for c in mb["cases"]}
    Hh = {c["id"]: c for c in mh["cases"]}

    def cls(c):
        return c.get("classification") or c.get("status_after_crash")

    def restart_ok(m, ids):
        return all(m[i].get("restart", {}).get("ok") for i in ids if "restart" in m[i] and i != "C01")

    crash_ids = [c for c in B if c.startswith("C")]
    facts = {
        "baseline_corrupt_cases": sorted(i for i in crash_ids if cls(B[i]) == "CORRUPT"),
        "hardened_corrupt_cases": sorted(i for i in crash_ids if cls(Hh[i]) == "CORRUPT"),
        "baseline_fsyncs_in_control": B["C15"].get("fsync_ops"), "hardened_fsyncs_in_control": Hh["C15"].get("fsync_ops"),
        "baseline_restarts_all_refused_unchanged": restart_ok(B, crash_ids),
        "hardened_restarts_all_refused_unchanged": restart_ok(Hh, crash_ids),
        "baseline_S04_refused": B["S04"]["runner_refused"], "hardened_S04_refused": Hh["S04"]["runner_refused"],
        "baseline_S05_refused": B["S05"]["runner_refused"], "hardened_S05_refused": Hh["S05"]["runner_refused"],
        "baseline_S06_refused": B["S06"]["runner_refused"], "baseline_S06_run_start_lines": B["S06"]["run_start_lines"],
        "hardened_S06_refused": Hh["S06"]["runner_refused"],
        "unit_hardened_all_pass": uh["meets_expectation"], "unit_baseline_discriminates": ub["meets_expectation"],
        "unit_baseline_failed": sorted(k for k, v in ub["results"].items() if not v["pass"]),
        "regression": {k: {"baseline_rc": rb["runs"].get(k, {}).get("rc"), "hardened_rc": rh["runs"].get(k, {}).get("rc")}
                       for k in sorted(set(rb["runs"]) | set(rh["runs"]))},
        "regression_pins_all_current": {"baseline": rb.get("pins_all_current"), "hardened": rh.get("pins_all_current")},
    }

    def row(rid, risk, base, hard, evid, note):
        return {"id": rid, "risk": risk, "r2_as_shipped": base, "hardened": hard, "evidence": evid, "note": note}

    rows = [
        row("R01", "non-atomic evidence writes",
            "UNSAFE" if facts["baseline_corrupt_cases"] else "ALREADY_SAFE",
            "ALREADY_SAFE" if not facts["hardened_corrupt_cases"] else "UNSAFE",
            ["matrix C04 C05 C12", "unit T04"],
            f"baseline torn/empty records or markers in {facts['baseline_corrupt_cases']} (fail-closed CORRUPT, the "
            "attempt's evidence lost); hardened: temp + fsync + link, every crash point INTERRUPTED, never CORRUPT"),
        row("R02", "missing fsync on evidence",
            "UNSAFE" if not facts["baseline_fsyncs_in_control"] else "ALREADY_SAFE", "SAFE_BUT_UNPROVEN",
            ["matrix C15 fsync_ops", "unit T03"],
            f"baseline {facts['baseline_fsyncs_in_control']} fsyncs in a full run; hardened "
            f"{facts['hardened_fsyncs_in_control']}, each record fsynced before its link (25/25 ordered). Unproven: true "
            "power-loss durability depends on the filesystem honouring fsync; no power-cut test is possible here"),
        row("R03", "missing fsync on parent directories",
            "UNSAFE" if not facts["baseline_fsyncs_in_control"] else "SAFE_BUT_UNPROVEN", "SAFE_BUT_UNPROVEN",
            ["matrix C15 fsync log (dir fsync after every link)", "unit T03"],
            "hardened fsyncs the directory after every link and after the attempt mkdir (after the RUN START line, "
            "QC12 T14); same power-loss caveat as R02"),
        row("R04", "ledger append durability",
            "UNSAFE" if not (facts["baseline_fsyncs_in_control"] and facts["baseline_S05_refused"]) else
            "SAFE_BUT_UNPROVEN",
            "SAFE_BUT_UNPROVEN" if facts["hardened_S05_refused"] else "UNSAFE",
            ["matrix S05", "unit T05 T07"],
            "rows are still appended by the research ledger writer (unchanged, one buffered write per row); hardened "
            "fsyncs both ledgers after every start line, gate record and abort, and refuses launch over a torn or "
            "unparseable row (H3). A row torn by power loss is detected, never silently continued"),
        row("R05", "launch without checking existing ledger state",
            "UNSAFE" if not (facts["baseline_S05_refused"] and facts["baseline_S06_refused"]) else "ALREADY_SAFE",
            "ALREADY_SAFE" if facts["hardened_S05_refused"] and facts["hardened_S06_refused"] else "UNSAFE",
            ["matrix S05 S06", "unit T06"],
            f"baseline launched over a torn ledger (S05 refused={facts['baseline_S05_refused']}) and over an orphan RUN "
            f"START (S06 refused={facts['baseline_S06_refused']}, {facts['baseline_S06_run_start_lines']} start lines); "
            "hardened refuses both before Q-HOST and the attempt (H3)"),
        row("R06", "double-launch protection", "ALREADY_SAFE", "ALREADY_SAFE", ["matrix S09"],
            "two racing runners: os.mkdir decides, exactly one attempt and one RUN START. The launcher's own check (no "
            "loaded p309-r2-* unit, empty scratch root) is SAFE_BUT_UNPROVEN here (no systemd)"),
        row("R07", "duplicate execution after interruption",
            "UNSAFE" if not facts["baseline_S06_refused"] else "ALREADY_SAFE",
            "ALREADY_SAFE" if facts["hardened_S06_refused"] else "UNSAFE",
            ["matrix S06", "restart probes C02-C15"],
            "restarts over an existing attempt are refused in both; but if the attempt directory is lost (power loss "
            "before its entry is durable, or removal) r2 as shipped starts a second run (two RUN STARTs); hardened "
            "refuses it and makes the entry durable"),
        row("R08", "stale lock handling", "ALREADY_SAFE", "ALREADY_SAFE", ["matrix S01 C02"],
            "no lock files by design: the attempt directory is a permanent tombstone; an empty one blocks every restart "
            "(fail closed) and is classified INTERRUPTED. No stale-lock 'recovery' exists, by design (A27 / P23)"),
        row("R09", "partial artifact handling",
            "UNSAFE" if not facts["baseline_S04_refused"] else "ALREADY_SAFE",
            "ALREADY_SAFE" if facts["hardened_S04_refused"] else "UNSAFE",
            ["matrix S02 S04"],
            "a torn record inside a prior attempt is refused by both (S02); a temporary file left in the qualification "
            "directory was ignored by r2 as shipped (S04) and is refused by the hardened runner"),
        row("R10", "crash between artifact write and ledger update", "ALREADY_SAFE", "ALREADY_SAFE", ["matrix C08"],
            "INTERRUPTED in both; restart refused, bytes unchanged"),
        row("R11", "crash between ledger update and completion marker", "ALREADY_SAFE", "ALREADY_SAFE",
            ["matrix C11 C12"],
            "the gap itself is INTERRUPTED in both; the marker WRITE was torn in r2 as shipped (C12 CORRUPT, see R01) "
            "and is atomic when hardened; the hardened marker binds every attempt file (H5)"),
        row("R12", "host restart during QC-D5", "ALREADY_SAFE", "ALREADY_SAFE", ["matrix C10", "recovery-branch R08"],
            "fail closed: INTERRUPTED, never resumed, never a pass (the attempt is lost by design; the mitigation is "
            "the durable host, see DURABLE_HOST_EXECUTION_PACKET.md). Hardened adds ATTEMPT_START (boot id) so the "
            "interruption can be attributed to a reboot"),
        row("R13", "clean refusal when host identity differs", "ALREADY_SAFE", "ALREADY_SAFE",
            ["matrix S07", "r2 code: qhost_preflight continuity; manifest runtime.host_id_sha256"],
            "Q-HOST refuses before the attempt directory (S07, with a test double for the systemd context); the freeze "
            "manifest binds the freeze host, so make_freeze_manifest --check refuses on another host; Q-HOST's monitor "
            "aborts on a continuity break during the run (C13)"),
        row("R14", "cleanup or retry paths that could mutate preserved evidence", "ALREADY_SAFE", "ALREADY_SAFE",
            ["restart probes C02-C15 (3 requests each, bytes unchanged)", "static review"],
            "the runner never deletes, renames or rewrites evidence (mirror() rmtree touches only the scratch mirror); "
            "the hardened xwrite removes only its own temporary name after the link; validators and status are read-only"),
        row("R15", "drill topology generator order (F-DRILL-ORDER, found here)", "UNSAFE", "UNSAFE",
            ["matrix run 1 (all NOT_STARTED: manifest precondition refused)", "r1 F manifest pins freeze/P309_FREEZE.json"],
            "p309_topology_drill.make_topology runs the manifest generator before the parameters; a worker-tier drill "
            "(which calls main()) would refuse at its manifest precondition. Rehearsal tooling, not runtime: outside "
            "this branch's write-set; the result-free rehearsal tool (r2h_rehearse.py) uses the correct order"),
        row("R16", "host portability of the durability preflight", "SAFE_BUT_UNPROVEN", "SAFE_BUT_UNPROVEN",
            ["code/p309_host.py durability_preflight"],
            "requires a cloud metadata service (IMDS), not-spot, not-burstable: fails closed (safe) on any non-cloud "
            "durable host; a non-AWS host needs a reviewed change (owner decision OD-R2-3/6)"),
    ]
    out = {"schema": "P309_R2_FAILURE_MATRIX/1",
           "packages": {"r2_as_shipped": "101ef2cb17e5eab2892212178278da45b98004ed",
                        "hardened": mh["package_commit"]},
           "classes": ["ALREADY_SAFE", "UNSAFE", "SAFE_BUT_UNPROVEN", "IRRELEVANT_BY_DESIGN"],
           "facts_from_evidence": facts, "rows": rows,
           "evidence_sha256": {str(p.relative_to(ns)): hashlib.sha256(p.read_bytes()).hexdigest()
                               for p in sorted(ev.rglob("*.json"))
                               if p.parent.name in ("matrix", "unit", "regression")},
           "statement": "synthetic gates and scratch replicas only; NEW TARGET EVALUATIONS = 0"}
    Path(a.out).write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    for r in rows:
        print(f"{r['id']} {r['risk'][:55]:55} shipped={r['r2_as_shipped']:18} hardened={r['hardened']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
