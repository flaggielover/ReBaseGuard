"""Build and check the frozen C2 protocol: the pin set that makes the campaign reproducible and adjudicable.

The protocol records WHAT was frozen, not what the campaign believes about it. Every hash here is computed from a
file in this repository at build time; nothing is transcribed and nothing is asserted that was not measured. Where
a provenance fact was never recorded — notably the host that built the refined registry — the protocol says so in
`unrecorded_provenance` rather than supplying a value (see OPEN_NOTES_DISPOSITION_C2.md N10).

Fields are separated into three classes, because they carry different weight for an adjudicator:

  * `scientific_load_bearing` — inputs and outputs the D-stage result depends on. A change to any of these changes
    the science, and the qualifier treats a mismatch as fatal.
  * `governance_provenance`   — the gate, the frontier, the review chain, the guard policy, the lifecycle order.
    A mismatch means the governance record is wrong even if the arithmetic is not.
  * `incidental_runtime`      — wall-clock timings and recorded host descriptions. These differ between honest
    runs; the qualifier records them and does not require identity.

    python3 -B c2_protocol.py build --out ../config/C2_PROTOCOL.json
    python3 -B c2_protocol.py check --protocol ../config/C2_PROTOCOL.json [--expect-bound]

`build` emits an UNBOUND protocol: `freeze.commit` is null, because a file cannot contain the hash of the commit
that introduces it. The commit that adds the protocol IS the freeze commit; `evidence/freeze/C2_FREEZE_RECORD.json`
binds the two afterwards. `check --expect-bound` fails while that binding is absent, which is the pre-freeze
refusal the lifecycle depends on.
"""
import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve()
NS = HERE.parents[1]
CP = HERE.parents[4] / "level4/closure_proofs"
REPO = HERE.parents[4]

SCHEMA = "rebaseguard.p5y.k5.tail-c2.protocol.v1"
FRONTIER = "5289b6ce"
GATE_COMMIT = "87309610"
GATE_SHA256 = "098dd7f5c3cf31fbbbc6987f887f25866cddb978e4caf6ece52ea0db797db28f"


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def git(*a) -> str:
    return subprocess.run(["git", *a], capture_output=True, text=True, cwd=str(REPO)).stdout.strip()


ROOTS = {"namespace": NS, "closure_proofs": CP}


def pins(paths, root_name: str) -> dict:
    """A pin table tags the root its paths resolve against, so a checker never has to infer it."""
    root = ROOTS[root_name]
    files = {}
    for rel in sorted(paths):
        p = root / rel
        if not p.is_file():
            raise SystemExit(f"protocol input missing: {p}")
        files[rel] = sha(p)
    return {"root": root_name, "files": files}


def build() -> dict:
    code = sorted(p.name for p in (NS / "code").glob("*.py"))
    registry_dir = NS / "evidence/registry_c2"
    registry_artifacts = sorted(p.name for p in registry_dir.glob("*.json") if p.name != "REGISTRY_C2.json")

    forecast = json.loads((NS / "evidence/phase_d5/C2_D5_FORECAST.json").read_bytes())
    mutations = json.loads((NS / "evidence/prefreeze/C2_MUTATIONS.json").read_bytes())
    recert = json.loads((NS / "evidence/prefreeze/C2_RECERTIFY_306.json").read_bytes())
    regver = json.loads((NS / "evidence/prefreeze/C2_REGISTRY_VERIFY.json").read_bytes())

    return {
        "schema": SCHEMA,
        "campaign": "p5y_k5_tail_c2_closure",
        "freeze": {
            "commit": None,
            "state": "UNBOUND",
            "note": "bound by evidence/freeze/C2_FREEZE_RECORD.json after the commit that introduces this file",
        },

        # ---------------------------------------------------------------- scientific, load-bearing
        "scientific_load_bearing": {
            "result": {
                "D_STAGE_CLASS": forecast["D_STAGE_CLASS"],
                "closed": forecast["closed"],
                "still_open": forecast["still_open"],
                "gap_fall_fraction": {k: forecast["cells"][k]["gap_fall_fraction"] for k in forecast["cells"]},
                "Gamma": {k: forecast["cells"][k]["Gamma"] for k in forecast["cells"]},
                "materially_tightened": forecast["materially_tightened"],
            },
            "evidence": pins([
                "evidence/phase_d5/C2_D5_FORECAST.json",
                "evidence/phase_d5/C2_ROBUSTNESS_AND_R_ATTRIBUTION.json",
                "evidence/phase_d5/C2_CRITICAL_RATIOS.json",
                "evidence/phase_d1/C2_D1_BLOCKER.json",
                "evidence/registry_c2/REGISTRY_C2.json",
                "evidence/prefreeze/C2_MUTATIONS.json",
                "evidence/prefreeze/C2_RECERTIFY_306.json",
                "evidence/prefreeze/C2_REGISTRY_VERIFY.json",
                "evidence/phase_b0/C2_B0_VERIFICATION.json",
            ], "namespace"),
            "registry_artifacts": pins([f"evidence/registry_c2/{n}" for n in registry_artifacts], "namespace"),
            "producers": pins([f"code/{n}" for n in code], "namespace"),
            "consumed_theorem_and_consumer_modules": pins([
                "p5y_k5_m5_tail_closure/code/tct_rule.py",
                "p5y_k5_m5_tail_closure/code/tail_forecast_r2.py",
                "p5y_k5_lower_front_order3/code/tc_rule.py",
                "p5y_k5_perron_deflated_resolvent/code/deflated_consume.py",
                "p5y_k5_perron_deflated_resolvent/code/taboo_certify.py",
                "p5y_k1_cover_ledger_successor/config/cells.json",
            ], "closure_proofs"),
            "adopted_predecessor_inputs": pins([
                "p5y_k5_m5_tail_closure/evidence/measurement_r1/ADOPTED_TAIL_INPUTS.json",
                "p5y_k5_tail_operator_registry/evidence/registry_c1/REGISTRY_C1.json",
            ] + [f"p5y_k5_m5_tail_closure/evidence/measurement_r1/TCT_INPUTS_{k}.json" for k in range(305, 310)],
                "closure_proofs"),
            "expected_verdicts": {
                "mutations": {"applied": mutations["applied"], "detected": mutations["detected"],
                              "undetected": mutations["undetected"], "pass": mutations["pass"]},
                "registry_verify": {"pass": regver["pass"], "artifacts_rechecked": regver["artifacts_rechecked"],
                                    "cells_checked": regver["cells_checked"]},
                "recertify_306": {"verdict": recert["verdict"],
                                  "passes": {k: v["all_ok"] for k, v in recert["passes"].items()}},
            },
        },

        # ---------------------------------------------------------------- governance and provenance
        "governance_provenance": {
            "frontier_commit": FRONTIER,
            "gate": {"commit": GATE_COMMIT, "sha256": GATE_SHA256,
                     "path": "config/FEASIBILITY_GATES_C2.json",
                     "frozen_before_any_forecast": True},
            "authoritative_input_coverage_map": pins(
                ["p5y_k5_lower_front_order3/evidence/tc_r1/K5_COVERAGE_MAP_R4.json"], "closure_proofs"),
            "pre_freeze_reviews": pins(
                [f"review/{p.name}" for p in sorted((NS / "review").glob("*.md"))], "namespace"),
            "ready_review": {"file": "review/REVIEW_C2_PREFREEZE_R16.md",
                             "verdict": "READY_TO_FREEZE_WITH_NOTES"},
            "guard": "REAL_SCIENTIFIC_COMPUTE = DENY",
            "new_real_scientific_addresses_authorized": 0,
            "prohibition": ("no new real scientific address may be evaluated under this protocol. The R stage is "
                            "DESIGN ONLY and is additionally blocked: see phase_d/D_PRIME_OPPORTUNITY.md."),
            "cell_306_margin_floor": ("NOT decided by this campaign. Referred to the adjudicator with both branches "
                                      "pre-committed in phase_d/CELL_306_ADOPTION.md."),
            "lifecycle_order": ["protocol", "freeze", "qualification", "authorization", "execution", "seal",
                                "consumption", "adjudication", "coverage_map_r5"],
            "unrecorded_provenance": {
                "registry_build_host": ("not recorded anywhere under this campaign's evidence/ or config/; the "
                                        "registry builder did not record its host, toolchain or precision. See N10."),
            },
        },

        # ---------------------------------------------------------------- incidental runtime
        "incidental_runtime": {
            "note": "recorded, not required to reproduce; honest re-runs differ here",
            "recertify_306_host": recert["host"],
            "recertify_306_cpu_seconds": {k: v["cpu_seconds"] for k, v in recert["passes"].items()},
            "registry_verify_host": regver["host"],
            "registry_cpu_seconds_total": json.loads(
                (NS / "evidence/registry_c2/REGISTRY_C2.json").read_bytes())["cpu_seconds_total"],
        },
    }


def check(proto: dict, expect_bound: bool) -> tuple[bool, list]:
    bad = []
    if proto.get("schema") != SCHEMA:
        bad.append("schema mismatch")
    fr = proto.get("freeze", {})
    if expect_bound:
        if fr.get("state") != "BOUND" or not fr.get("commit"):
            bad.append("REFUSED: protocol is not bound to a freeze commit; "
                       "evidence/freeze/C2_FREEZE_RECORD.json must bind it before frozen production may run")
    for group in ("scientific_load_bearing", "governance_provenance"):
        for key, table in proto.get(group, {}).items():
            if not (isinstance(table, dict) and "root" in table and "files" in table):
                continue
            base = ROOTS[table["root"]]
            for rel, want in table["files"].items():
                p = base / rel
                if not p.is_file():
                    bad.append(f"missing pinned input: {rel}")
                elif sha(p) != want:
                    bad.append(f"pin mismatch: {rel}")
    # Binding may change only the freeze block. Compare the bound protocol against the UNBOUND one the freeze
    # commit actually contains, so a binding cannot smuggle any other edit past the checker.
    fr_rec = NS / "evidence/freeze/C2_FREEZE_RECORD.json"
    if expect_bound and fr_rec.is_file():
        rec = json.loads(fr_rec.read_bytes())
        frozen = subprocess.run(["git", "show", f"{rec['freeze_commit']}:level4/closure_proofs/"
                                 "p5y_k5_tail_c2_closure/config/C2_PROTOCOL.json"],
                                capture_output=True, text=True, cwd=str(REPO))
        if frozen.returncode != 0:
            bad.append("cannot read the protocol at the freeze commit")
        else:
            raw = frozen.stdout.encode()
            if hashlib.sha256(raw).hexdigest() != rec.get("protocol_sha256_unbound_at_freeze"):
                bad.append("protocol at the freeze commit does not match its recorded unbound hash")
            a_, b_ = json.loads(raw), dict(proto)
            a_.pop("freeze", None); b_.pop("freeze", None)
            if a_ != b_:
                bad.append("bound protocol differs from the frozen one outside the freeze block")
            if rec.get("freeze_commit") != fr.get("commit"):
                bad.append("freeze record and protocol disagree on the freeze commit")
    g = proto.get("governance_provenance", {}).get("gate", {})
    if g.get("sha256") != GATE_SHA256 or sha(NS / "config/FEASIBILITY_GATES_C2.json") != GATE_SHA256:
        bad.append("frozen gate identity mismatch")
    if proto.get("governance_provenance", {}).get("new_real_scientific_addresses_authorized") != 0:
        bad.append("protocol authorizes new real scientific addresses; refusing")
    return (not bad), bad


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=("build", "check"))
    ap.add_argument("--out")
    ap.add_argument("--protocol")
    ap.add_argument("--expect-bound", action="store_true")
    a = ap.parse_args()
    if a.mode == "build":
        data = json.dumps(build(), sort_keys=True, indent=1) + "\n"
        Path(a.out).write_text(data)
        print(json.dumps({"written": a.out, "sha256": hashlib.sha256(data.encode()).hexdigest(),
                          "freeze_state": "UNBOUND"}))
        return 0
    proto = json.loads(Path(a.protocol).read_bytes())
    ok, bad = check(proto, a.expect_bound)
    print(json.dumps({"protocol_sha256": sha(Path(a.protocol)), "expect_bound": a.expect_bound,
                      "pass": ok, "problems": bad[:10]}, indent=1))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
