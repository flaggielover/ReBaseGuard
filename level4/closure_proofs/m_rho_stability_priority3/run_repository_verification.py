#!/usr/bin/env python3
"""Run and classify the repository regression suites required by Priority 3.

Three protected suites are sensitive to `rg` availability or collation.  The
original closure contract is enforced literally: all three must pass in the
current verification environment.  Controlled pass/fail replays on the
working tree and a pristine `git archive HEAD` extraction establish the causal
environment diagnostics, but those replays never substitute for a required
passing suite.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

CAMPAIGN = Path(__file__).resolve().parent
ROOT = CAMPAIGN.parents[2]
PY_BIN = ROOT / "level4" / ".venv" / "bin" / "python"
CAMPAIGN_RELATIVE = "level4/closure_proofs/m_rho_stability_priority3"

REQUIRED = (
    "priority3_focused", "level_1_3_full", "priority2", "d4_phase_map",
    "external_validation_v3", "l4r06_policy", "l4r12_operational",
    "priority1", "historical_sr", "track1b",
)
ENVIRONMENT_DIAGNOSTIC_SUITES = {
    "priority1": "level4/closure_proofs/m_gt_1_priority1/tests",
    "historical_sr": "level4/closure_proofs/sr_derivative/tests",
    "track1b": "level4/closure_proofs/m_gt_1_track1b/tests",
}


def _summarise(output: str) -> str:
    matches = re.findall(r"(?:=+ )?(\d+ (?:passed|failed)[^\n]*)(?: =+)?", output)
    tail = output.strip().splitlines()
    return matches[-1] if matches else (tail[-1] if tail else "")


def run(label: str, command: list[str], cwd: Path = ROOT,
        env: dict[str, str] | None = None) -> dict:
    result = subprocess.run(
        command, cwd=cwd, env=env, text=True, capture_output=True
    )
    output = result.stdout + result.stderr
    return {
        "label": label,
        "command": " ".join(command),
        "exit_code": result.returncode,
        "summary": _summarise(output),
        "failing_node_ids": sorted(set(re.findall(r"^FAILED (\S+)", output, re.M))),
        "output_tail": "\n".join(output.strip().splitlines()[-30:]),
    }


def pytest_suite(label: str, path: str, cwd: Path = ROOT,
                 env: dict[str, str] | None = None) -> dict:
    return run(label, [str(PY_BIN), "-m", "pytest", path, "-q",
                       "-p", "no:cacheprovider"], cwd=cwd, env=env)


def pristine_head(work: Path) -> Path:
    """Materialise HEAD with no working-tree additions, Priority 3 included."""
    target = work / "pristine"
    target.mkdir(parents=True, exist_ok=True)
    archive = subprocess.run(["git", "archive", "HEAD"], cwd=ROOT, check=True,
                             capture_output=True)
    subprocess.run(["tar", "-x", "-C", str(target)], input=archive.stdout, check=True)
    assert not (target / CAMPAIGN_RELATIVE).exists(), \
        "the pristine HEAD extraction must not contain any Priority-3 file"
    return target


def environment_probes() -> dict:
    """Identify the host conditions behind the non-passing protected suites."""
    hash_source = (ROOT / "level4" / "closure_proofs" / "m_gt_1_priority1"
                   / "tests" / "test_integrity.py")
    recorded = json.loads(
        (ROOT / "level4" / "closure_proofs" / "m_gt_1_priority1"
         / "manifest.json").read_text()
    )["immutable_prior_evidence"]["track1b_tree_sha256"]
    snippet = (
        "import sys; sys.path.insert(0, %r)\n"
        "from test_integrity import track1b_tree_hash\n"
        "print(track1b_tree_hash())\n" % str(hash_source.parent)
    )
    hashes = {}
    for label, collation in (
        ("host_default", None), ("C", "C"),
        ("en_US.UTF-8", "en_US.UTF-8"),
    ):
        env = os.environ.copy()
        if collation is not None:
            env["LANG"] = collation
            env["LC_ALL"] = collation
            env["LC_COLLATE"] = collation
        result = subprocess.run([str(PY_BIN), "-c", snippet], cwd=ROOT, env=env,
                                text=True, capture_output=True, check=True)
        hashes[label] = result.stdout.strip()

    track1b_worktree_clean = subprocess.run(
        ["git", "diff", "--quiet", "HEAD", "--",
         "level4/closure_proofs/m_gt_1_track1b"], cwd=ROOT).returncode == 0
    track1b_untracked = subprocess.check_output(
        ["git", "ls-files", "--others", "--exclude-standard",
         "level4/closure_proofs/m_gt_1_track1b"], cwd=ROOT, text=True).split()

    return {
        "ripgrep_binary_on_path": shutil.which("rg"),
        "ripgrep_available": shutil.which("rg") is not None,
        "track1b_tree_hash_recorded_by_priority1": recorded,
        "track1b_tree_hash_by_collation": hashes,
        "track1b_tree_hash_is_collation_dependent":
            len(set(hashes.values())) > 1,
        "track1b_tree_hash_matches_under_en_US_UTF_8":
            hashes["en_US.UTF-8"] == recorded,
        "track1b_worktree_clean_against_head": track1b_worktree_clean,
        "track1b_untracked_files": track1b_untracked,
    }


CONTROLLED_NODES = {
    "priority1_locale": (
        "level4/closure_proofs/m_gt_1_priority1/tests/test_integrity.py::"
        "test_immutable_prior_evidence_hashes"
    ),
    "historical_sr_rg": (
        "level4/closure_proofs/sr_derivative/tests/test_integrity.py::"
        "test_fresh_master_seed_is_confined_to_design_and_track2"
    ),
    "track1b_rg": (
        "level4/closure_proofs/m_gt_1_track1b/tests/test_integrity.py::"
        "test_fresh_seed_exists_only_inside_track1b"
    ),
}


def _controlled_env(locale_name: str, include_rg: bool) -> dict[str, str]:
    env = os.environ.copy()
    env["LANG"] = locale_name
    env["LC_ALL"] = locale_name
    env["LC_COLLATE"] = locale_name
    minimal = [str(PY_BIN.parent), "/usr/bin", "/bin", "/usr/sbin", "/sbin"]
    rg_binary = shutil.which("rg")
    if include_rg and rg_binary is not None:
        minimal.insert(0, str(Path(rg_binary).parent))
    env["PATH"] = os.pathsep.join(minimal)
    return env


def controlled_environment_matrix(pristine: Path) -> dict:
    """Prove the locale and PATH causes positively in both repository states."""
    runs = []
    for scope, cwd in (("worktree", ROOT), ("pristine_head", pristine)):
        cases = (
            ("priority1_en_us_with_rg", CONTROLLED_NODES["priority1_locale"],
             _controlled_env("en_US.UTF-8", True), 0),
            ("priority1_c_with_rg", CONTROLLED_NODES["priority1_locale"],
             _controlled_env("C", True), 1),
            ("historical_sr_en_us_with_rg", CONTROLLED_NODES["historical_sr_rg"],
             _controlled_env("en_US.UTF-8", True), 0),
            ("historical_sr_en_us_without_rg", CONTROLLED_NODES["historical_sr_rg"],
             _controlled_env("en_US.UTF-8", False), 1),
            ("track1b_en_us_with_rg", CONTROLLED_NODES["track1b_rg"],
             _controlled_env("en_US.UTF-8", True), 0),
            ("track1b_en_us_without_rg", CONTROLLED_NODES["track1b_rg"],
             _controlled_env("en_US.UTF-8", False), 1),
        )
        for case, node, env, expected in cases:
            row = pytest_suite(f"{scope}_{case}", node, cwd=cwd, env=env)
            row["scope"] = scope
            row["case"] = case
            row["expected_exit_code"] = expected
            row["matches_expected_causal_outcome"] = row["exit_code"] == expected
            runs.append(row)
    rg_available = shutil.which("rg") is not None
    checks = {
        "rg_available_for_positive_control": rg_available,
        "all_controlled_outcomes_match": all(
            row["matches_expected_causal_outcome"] for row in runs
        ),
        "both_scopes_covered": {row["scope"] for row in runs}
            == {"worktree", "pristine_head"},
    }
    return {"runs": runs, "checks": checks, "all_checks_pass": all(checks.values())}


def main() -> None:
    suites = [
        pytest_suite("priority3_focused", f"{CAMPAIGN_RELATIVE}/tests"),
        run("level_1_3_full", ["bash", "scripts/verify_level_1_3.sh"]),
        run("level_4_aggregate", ["bash", "scripts/verify_level_4.sh"]),
        pytest_suite("priority1", ENVIRONMENT_DIAGNOSTIC_SUITES["priority1"]),
        pytest_suite("priority2", "level4/closure_proofs/sr_derivative_priority2/tests"),
        pytest_suite("historical_sr", ENVIRONMENT_DIAGNOSTIC_SUITES["historical_sr"]),
        pytest_suite("d4_phase_map", "level4/closure_proofs/d4_phase_map/tests"),
        pytest_suite("external_validation_v2",
                     "level4/closure_proofs/external_validation_v2/tests"),
        pytest_suite("external_validation_v3",
                     "level4/closure_proofs/external_validation_v3/tests"),
        pytest_suite("final_global_reaudit", "level4/final_global_reaudit/tests"),
        pytest_suite("l4r06_policy", "level4/closure_proofs/l4r06_policy/tests"),
        pytest_suite("l4r12_operational",
                     "level4/closure_proofs/l4r12_operational_crossing/tests"),
        pytest_suite("final_level4_closure", "level4/final_level4_closure/tests"),
        pytest_suite("track1b", ENVIRONMENT_DIAGNOSTIC_SUITES["track1b"]),
        run("post_level4_archive",
            [str(PY_BIN), "scripts/verify_post_level4_archive.py"]),
    ]
    by_name = {row["label"]: row for row in suites}
    required_pass = all(by_name[name]["exit_code"] == 0 for name in REQUIRED)

    with tempfile.TemporaryDirectory(prefix="rebaseguard-p3-pristine-") as raw:
        pristine = pristine_head(Path(raw))
        replays = {
            label: pytest_suite(f"{label}_pristine_head", path, cwd=pristine)
            for label, path in ENVIRONMENT_DIAGNOSTIC_SUITES.items()
        }
        controlled = controlled_environment_matrix(pristine)

    environment = {}
    for label, replay in replays.items():
        observed = by_name[label]
        in_repo = set(observed["failing_node_ids"])
        at_head = set(replay["failing_node_ids"])
        environment[label] = {
            "observed_failures": sorted(in_repo),
            "pristine_head_failures": sorted(at_head),
            "every_observed_failure_reproduces_without_priority3":
                bool(in_repo) and in_repo <= at_head,
            "priority3_introduced_no_new_failure": in_repo <= at_head,
            "pristine_head_summary": replay["summary"],
            "classification": "ENVIRONMENT_DIAGNOSTIC",
        }
    environment_clean = all(
        row["priority3_introduced_no_new_failure"] for row in environment.values())

    historical = {
        "old_52_file_guard_against_92_file_sr_tree": {
            "observed": by_name["level_4_aggregate"]["exit_code"] != 0,
            "also_observed_in": [
                name for name in ("external_validation_v2", "final_global_reaudit",
                                  "final_level4_closure")
                if by_name[name]["exit_code"] != 0
            ],
            "predates_priority3": True,
            "recorded_by": [
                "level4/closure_proofs/m_gt_1_priority1/results/verification.json",
                "level4/closure_proofs/sr_derivative_priority2/results/verification.json",
            ],
            "classification": "HISTORICAL_DIAGNOSTIC",
        },
        "post_archive_readme_hash_drift": {
            "observed": by_name["post_level4_archive"]["exit_code"] != 0
                and "README.md" in by_name["post_level4_archive"]["output_tail"],
            "predates_priority3": True,
            "recorded_by": [
                "level4/closure_proofs/sr_derivative_priority2/CLOSURE_REPORT.md",
            ],
            "classification": "HISTORICAL_DIAGNOSTIC",
        },
    }
    historical_unchanged = all(row["observed"] for row in historical.values())

    payload = {
        "schema": "rebaseguard.p3-verification.v3",
        "required_suites": list(REQUIRED),
        "required_regressions_pass": required_pass,
        "suites": suites,
        "environment_diagnostics": environment,
        "environment_probes": environment_probes(),
        "controlled_environment_matrix": controlled,
        "environment_diagnostics_reproduce_without_priority3": environment_clean,
        "historical_diagnostics": historical,
        "historical_diagnostics_unchanged": historical_unchanged,
        "diagnostics_not_counted_as_priority3_passes": True,
        "gate": "all named required suites literally pass in the current intended "
                "environment; controlled worktree/pristine replays prove the "
                "locale/PATH diagnostics; no observed failure is new to Priority 3; "
                "and the two grandfathered historical diagnostics are unchanged",
        "all_gates_pass": required_pass and environment_clean
            and controlled["all_checks_pass"] and historical_unchanged,
    }
    (CAMPAIGN / "results" / "verification.json").write_text(
        json.dumps(payload, indent=2) + "\n"
    )
    print(json.dumps({
        "required_regressions_pass": required_pass,
        "environment_diagnostics_reproduce_without_priority3": environment_clean,
        "controlled_environment_causality_pass": controlled["all_checks_pass"],
        "historical_diagnostics_unchanged": historical_unchanged,
        "all_gates_pass": payload["all_gates_pass"],
        "suites": [{"label": r["label"], "exit_code": r["exit_code"],
                    "summary": r["summary"]} for r in suites],
    }, indent=2))
    if not payload["all_gates_pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
