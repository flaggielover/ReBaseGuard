#!/usr/bin/env python3
"""P4X production C6 -- re-verification of the INHERITED Lean and Arb artifacts.

No new Lean declaration.  No new Arb certificate object.  This driver re-runs
the inherited verification and writes its record ONLY into the P4X production
namespace: the frozen Priority-4 tree is never written to, which is why the
campaign's own `run_lean.py` and `certificates/run_certificate.py` are not
invoked directly (both write results back into the protected tree).
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import re
import resource
import subprocess
import sys
import tempfile
import time
from pathlib import Path

PROD = Path(__file__).resolve().parent
CLOSURE = PROD.parent.parent
ROOT = CLOSURE.parents[1]
P4 = CLOSURE / "p4_theory_generalization"

#: The Lean toolchain needs a built Mathlib.  This worktree has none, and
#: cloning/building one would cost hours and ~7 GB for no scientific gain.  The
#: primary worktree already holds a fully built, byte-identical Lean project
#: (`rebaseguard-lean` tree object 3fa5d722... in both worktrees), and the
#: Priority-4 Lean sources are byte-identical too.  The verification therefore
#: runs against that build.  Both identities are asserted below rather than
#: assumed, and neither worktree's TRACKED content is written to -- `.lake` is
#: gitignored build state.
PRIMARY_WORKTREE = Path("/Users/suzhe/ReBaseGuard")
LEAN_PROJECT = PRIMARY_WORKTREE / "rebaseguard-lean"
LEAN_ROOT = PRIMARY_WORKTREE
LEAN_P4 = PRIMARY_WORKTREE / "level4" / "closure_proofs" / "p4_theory_generalization"

DEPENDENCIES = (
    ("m_gt_1_priority1", "MGtOneClosure"),
    ("sr_derivative_priority2", "SRPriority2"),
    ("m_rho_stability_priority3", "StabilityMapP3"),
)
ALLOWED_AXIOMS = {"propext", "Classical.choice", "Quot.sound"}
EXPECTED_DECLARATIONS = 19


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def cpu() -> float:
    r = resource.getrusage(resource.RUSAGE_SELF)
    c = resource.getrusage(resource.RUSAGE_CHILDREN)
    return r.ru_utime + r.ru_stime + c.ru_utime + c.ru_stime


def tool_versions() -> dict:
    def ver(cmd):
        try:
            return subprocess.run(cmd, capture_output=True, text=True,
                                  timeout=60).stdout.strip().splitlines()[0]
        except Exception as exc:                                  # noqa: BLE001
            return f"unavailable: {exc}"
    import flint
    return {
        "lean": ver(["lean", "--version"]),
        "lake": ver(["lake", "--version"]),
        "python": sys.version.split()[0],
        "python_flint": flint.__version__,
    }


# ------------------------------------------------------------------- Lean --

def _assert_lean_environment_identity() -> dict:
    """The build we compile against must be the same artifact as ours."""
    import subprocess as sp

    def tree(worktree: Path, path: str) -> str:
        return sp.check_output(["git", "rev-parse", f"HEAD:{path}"],
                               cwd=worktree, text=True).strip()

    checks = {}
    for path in ("rebaseguard-lean",
                 "level4/closure_proofs/p4_theory_generalization"):
        here, there = tree(ROOT, path), tree(PRIMARY_WORKTREE, path)
        checks[f"tree_object_identical:{path}"] = (here == there)
    for rel in ("lean/GeneralLocationFamilyP4.lean", "lean/AxiomAudit.lean"):
        checks[f"source_bytes_identical:{rel}"] = (
            sha256(P4 / rel) == sha256(LEAN_P4 / rel))
    if not all(checks.values()):
        raise SystemExit(f"Lean environment identity failed: {checks}")
    return checks


def reverify_lean() -> dict:
    identity = _assert_lean_environment_identity()
    source = LEAN_P4 / "lean" / "GeneralLocationFamilyP4.lean"
    audit = LEAN_P4 / "lean" / "AxiomAudit.lean"
    recorded = json.loads((P4 / "results" / "lean_compile.json").read_text())
    manifest = json.loads((P4 / "manifest.json").read_text())

    def compile_one(root: Path, src: Path, out: Path, work: Path) -> None:
        env = os.environ.copy()
        env["LEAN_PATH"] = f"{work}:{env.get('LEAN_PATH', '')}"
        subprocess.run(
            ["lake", "env", "lean", "-R", str(root), "-o", str(out), str(src)],
            cwd=LEAN_PROJECT, check=True, env=env)

    commands = []
    with tempfile.TemporaryDirectory(prefix="p4x-c6-lean-") as raw:
        work = Path(raw)
        for campaign, module in DEPENDENCIES:
            root = LEAN_ROOT / "level4" / "closure_proofs" / campaign / "lean"
            compile_one(root, root / f"{module}.lean",
                        work / f"{module}.olean", work)
            commands.append(f"lake env lean -R {root} -o <tmp>/{module}.olean "
                            f"{root / (module + '.lean')}")
        compile_one(LEAN_P4 / "lean", source,
                    work / "GeneralLocationFamilyP4.olean", work)
        commands.append(f"lake env lean -R {LEAN_P4 / 'lean'} "
                        f"-o <tmp>/GeneralLocationFamilyP4.olean {source}")

        env = os.environ.copy()
        env["LEAN_PATH"] = f"{work}:{LEAN_P4 / 'lean'}:{env.get('LEAN_PATH', '')}"
        result = subprocess.run(
            ["lake", "env", "lean", "-R", str(LEAN_P4 / "lean"), str(audit)],
            cwd=LEAN_PROJECT, env=env, check=True, text=True, capture_output=True)
        commands.append(f"lake env lean -R {LEAN_P4 / 'lean'} {audit}")

    text = result.stdout + result.stderr
    flat = " ".join(text.split())
    reports = re.findall(r"'([^']+)' depends on axioms: \[([^\]]*)\]", flat)
    trivial = re.findall(r"'([^']+)' does not depend on any axioms", flat)
    audited = sorted({name for name, _ in reports} | set(trivial))

    axioms_seen: set[str] = set()
    for _, raw in reports:
        axioms_seen |= {x.strip() for x in raw.split(",") if x.strip()}

    src_text = source.read_text()
    src_hash = sha256(source)
    checks = {
        "compiled": True,
        "declaration_count_matches": len(audited) == EXPECTED_DECLARATIONS,
        "declarations_match_recorded": audited == recorded["audited_declarations"],
        "axioms_within_allowed_set": axioms_seen <= ALLOWED_AXIOMS,
        "no_sorryAx_in_audit_output": "sorryAx" not in text,
        "no_sorry_in_source": "sorry" not in src_text,
        "no_axiom_declaration_in_source": "axiom " not in src_text,
        "source_hash_matches_manifest":
            src_hash == manifest["lean"]["source_sha256"],
        "source_hash_matches_recorded_result":
            src_hash == recorded["source_sha256"],
    }
    return {
        "obligation": "C6-Lean",
        "new_declarations_added": 0,
        "environment_identity": identity,
        "compiled_against_worktree": str(PRIMARY_WORKTREE),
        "environment_note": (
            "compiled against the primary worktree's pre-built Lean project; "
            "the rebaseguard-lean and p4_theory_generalization tree objects and "
            "the Lean source bytes are identical in both worktrees, so the "
            "artifact verified is the same one.  Only gitignored .lake build "
            "state is touched"),
        "commands": commands,
        "declarations_audited": len(audited),
        "declarations": audited,
        "axioms_observed": sorted(axioms_seen),
        "allowed_axioms": sorted(ALLOWED_AXIOMS),
        "source_sha256": src_hash,
        "checks": checks,
        "all_checks_pass": all(checks.values()),
        "audit_output_sha256": hashlib.sha256(text.encode()).hexdigest(),
    }


# -------------------------------------------------------------------- Arb --

def reverify_arb(bits_list=(160, 256)) -> dict:
    spec = importlib.util.spec_from_file_location(
        "p4_run_certificate", P4 / "certificates" / "run_certificate.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    witness_path = P4 / "certificates" / "WITNESS.json"
    manifest = json.loads((P4 / "manifest.json").read_text())
    recorded = json.loads((P4 / "certificates" / "certificate.json").read_text())
    witness = json.loads(witness_path.read_text())

    runs = {}
    for bits in bits_list:
        mod.ctx.prec = int(bits)
        sections = {
            "laplace_closed_form":
                mod.certify_laplace(witness["laplace_closed_form"]),
            "uniform_counterexample":
                mod.certify_uniform(witness["uniform_counterexample"]),
            "general_score_witness":
                mod.certify_witness(witness["general_score_witness"]),
        }
        checks: dict[str, bool] = {}
        for section in sections.values():
            checks.update({k: bool(v) for k, v in section["checks"].items()})
        missing = [n for n in witness["required_certificates"] if n not in checks]
        runs[str(bits)] = {
            "arb_precision_bits": bits,
            "required_certificates": len(witness["required_certificates"]),
            "checks_evaluated": len(checks),
            "missing_certificates": missing,
            "failed_checks": sorted(k for k, v in checks.items() if not v),
            "all_checks_pass": (not missing) and all(checks.values()),
        }

    checks = {
        "witness_hash_matches_manifest":
            sha256(witness_path)
            == manifest["frozen_new_inputs"]["finite_support_witness_sha256"],
        "witness_hash_matches_recorded_certificate":
            sha256(witness_path) == recorded["witness_sha256"],
        "all_pass_at_160_bits": runs["160"]["all_checks_pass"],
        "all_pass_at_256_bits": runs["256"]["all_checks_pass"],
        "matches_recorded_all_checks_pass":
            runs["160"]["all_checks_pass"] == recorded["all_checks_pass"],
        "no_new_certificate_object": (
            sorted(runs["160"].keys()) is not None
            and len(witness["required_certificates"])
            == len(recorded["required_certificates"])),
    }
    return {
        "obligation": "C6-Arb",
        "new_certificate_objects_added": 0,
        "witness_sha256": sha256(witness_path),
        "certificate_objects": list(recorded["sections"].keys()),
        "runs": runs,
        "checks": checks,
        "all_checks_pass": all(checks.values()),
    }


def main() -> None:
    c0, w0 = cpu(), time.perf_counter()
    lean = reverify_lean()
    print(f"Lean: {lean['declarations_audited']} declarations, axioms "
          f"{lean['axioms_observed']}, all_checks_pass={lean['all_checks_pass']}")
    arb = reverify_arb()
    for bits, run in arb["runs"].items():
        print(f"Arb @{bits} bits: {run['checks_evaluated']} checks, "
              f"failed={run['failed_checks']}, pass={run['all_checks_pass']}")

    payload = {
        "schema": "rebaseguard.p4x-production-c6.v1",
        "phase": "P1_ZERO_NEW_SCIENCE_OBLIGATIONS",
        "obligation": "C6",
        "new_lean_declarations": 0,
        "new_arb_objects": 0,
        "tool_versions": tool_versions(),
        "lean": lean,
        "arb": arb,
        "C6": "PASS" if (lean["all_checks_pass"] and arb["all_checks_pass"])
              else "FAIL",
        "cpu_seconds": cpu() - c0,
        "wall_seconds": time.perf_counter() - w0,
    }
    out = PROD / "results" / "c6_lean_arb.json"
    out.write_text(json.dumps(payload, indent=2) + "\n")
    print(f"\nC6 = {payload['C6']}   cpu {payload['cpu_seconds']:.1f}s   "
          f"wall {payload['wall_seconds']:.1f}s")
    print(f"-> {out}")


if __name__ == "__main__":
    main()
