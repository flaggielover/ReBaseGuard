"""Independent, target-free Linux validation of the development platform layer.

Read only the named development files. Write complete evidence outside the source
tree. This is neither official qualification nor a test of the scientific model.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import subprocess
import sys
import tempfile


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_suite(tests: Path, cwd: Path, module: Path | None = None) -> dict:
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    env.pop("LX_PLATFORM_DIR", None)
    if module is not None:
        env["LX_PLATFORM_DIR"] = str(module)
    command = [sys.executable, "-B", "-W", "error::ResourceWarning", "-m", "unittest",
               "discover", "-s", str(tests), "-v"]
    try:
        p = subprocess.run(command, cwd=cwd, env=env, capture_output=True, text=True,
                           stdin=subprocess.DEVNULL, timeout=120)
    except subprocess.TimeoutExpired as exc:
        return {"returncode": None, "tests": None, "failures": [], "errors": [],
                "timed_out": True, "stdout": str(exc.stdout), "stderr": str(exc.stderr)}
    count = re.search(r"^Ran (\d+) tests? in ", p.stderr, re.M)
    headings = re.findall(r"^(FAIL|ERROR): (\S+) \(([^)]+)\)", p.stderr, re.M)
    return {"returncode": p.returncode, "tests": int(count[1]) if count else None,
            "failures": [list(x[1:]) for x in headings if x[0] == "FAIL"],
            "errors": [list(x[1:]) for x in headings if x[0] == "ERROR"],
            "timed_out": False, "stdout": p.stdout, "stderr": p.stderr}


def classify(run: dict, baseline_count: int) -> str:
    if run["timed_out"] or run["tests"] != baseline_count:
        return "ERROR"
    if run["returncode"] == 0 and not run["failures"] and not run["errors"]:
        return "SURVIVED"
    if run["errors"]:
        return "ERROR_REQUIRES_REVIEW"
    if run["returncode"] != 0 and run["failures"]:
        return "KILLED_ASSERTION_REQUIRES_PROPERTY_REVIEW"
    return "ERROR"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    repo, output = args.repo.resolve(), args.output.resolve()
    if output == repo or repo in output.parents:
        parser.error("evidence must be outside the reviewed source tree")
    if platform.system() != "Linux":
        parser.error("the complete development suite requires a Linux host")
    stream = repo / "level4/closure_proofs/p5y_k5_cell308_research/streams/CLOUD_R1_LINUX_DEV"
    source, tests = stream / "lx_platform.py", stream / "tests"
    paths = {"source": source, "tests": tests / "test_lx_platform.py", "harness": tests / "run_mutants.py"}
    hashes = {key: digest(path) for key, path in paths.items()}
    revision = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo, capture_output=True,
                              text=True, check=True).stdout.strip()
    output.mkdir(parents=True, exist_ok=True)
    record = {"class": "SYNTHETIC_VALIDATION", "dev_only": True, "source_revision": revision,
              "python": sys.version, "kernel": platform.release(), "input_hashes": hashes,
              "new_target_evaluations": 0, "baseline": run_suite(tests, stream), "mutants": []}
    baseline = record["baseline"]
    (output / "baseline.json").write_text(json.dumps(record, indent=2) + "\n")
    if baseline["returncode"] != 0 or baseline["tests"] is None or baseline["errors"]:
        print("BASELINE FAILED; mutations not run", flush=True)
        return 1
    print(f"BASELINE PASS: {baseline['tests']} tests at {revision}", flush=True)
    sys.path.insert(0, str(tests))
    from run_mutants import MUTANTS

    original = source.read_text()
    for mid, description, edits in MUTANTS:
        mutated = original
        for old, new in edits:
            if mutated.count(old) != 1:
                result = {"id": mid, "property": description, "status": "NOT_APPLIED"}
                break
            mutated = mutated.replace(old, new)
        else:
            with tempfile.TemporaryDirectory(prefix="platform-mutant-") as directory:
                Path(directory, "lx_platform.py").write_text(mutated)
                run = run_suite(tests, stream, Path(directory))
            result = {"id": mid, "property": description,
                      "status": classify(run, baseline["tests"]), "run": run}
        record["mutants"].append(result)
        (output / f"{mid}.json").write_text(json.dumps(result, indent=2) + "\n")
        print(f"{mid}: {result['status']}", flush=True)
    record["final_input_hashes"] = {key: digest(path) for key, path in paths.items()}
    record["inputs_unchanged"] = record["final_input_hashes"] == hashes
    record["counts"] = {status: sum(x["status"] == status for x in record["mutants"])
                        for status in sorted({x["status"] for x in record["mutants"]})}
    (output / "validation.json").write_text(json.dumps(record, indent=2) + "\n")
    print(json.dumps({"inputs_unchanged": record["inputs_unchanged"], "counts": record["counts"]}), flush=True)
    invalid = any(x["status"] in ("SURVIVED", "NOT_APPLIED", "ERROR") for x in record["mutants"])
    return 1 if invalid or not record["inputs_unchanged"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
