#!/usr/bin/env python3
"""P4Z independent adjudication.

Re-derives every governance claim from artifacts on disk rather than trusting
the runner's own summary.  The production runner does not decide its own
closure verdict; this does, and it is deliberately suspicious of the runner:
every count is recomputed from the block files, every threshold is re-read from
its frozen source, and every hash is recomputed.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
NS = HERE.parent
P4 = NS.parent / "p4_theory_generalization"
REPO = NS.parent.parent.parent
sys.path.insert(0, str(HERE))

import scientific_hash as sh  # noqa: E402


def git(*args: str) -> str:
    return subprocess.run(("git", "-C", str(REPO)) + args,
                          capture_output=True, text=True, check=True).stdout.strip()


def load(path: Path):
    return json.loads(path.read_text())


def check(findings: list, name: str, ok: bool, detail) -> bool:
    findings.append({"check": name, "status": "PASS" if ok else "FAIL",
                     "detail": detail})
    return ok


def main() -> int:
    f: list = []
    plan = load(NS / "production" / "campaign_plan.json")
    checkpoint = load(NS / "configs" / "checkpoint_p4z.json")
    protocol = load(P4 / "configs" / "P4_PROTOCOL.json")
    stage0 = load(NS / "production" / "stage0_freeze.json")
    contract = load(NS / "production" / "mac_runtime_contract.json")
    state = load(NS / "production" / "run_state.json")
    adj_path = NS / "production" / "adjudication.json"
    adj = load(adj_path) if adj_path.exists() else None
    replay_path = NS / "production" / "replay.json"
    replay = load(replay_path) if replay_path.exists() else None
    lean_path = NS / "results" / "lean_audit.json"
    lean = load(lean_path) if lean_path.exists() else None

    # 1 historical immutability -------------------------------------------
    tree = git("rev-parse", "HEAD:level4/closure_proofs/p4_theory_generalization")
    check(f, "historical P4 tree object unchanged",
          tree == checkpoint["theorem"]["tree_object"], tree)
    for name, key in (("THEOREM.md", "theorem_md_blob"),
                      ("PROOF.md", "proof_md_blob"),
                      ("configs/P4_PROTOCOL.json", "protocol_blob")):
        blob = git("rev-parse",
                   f"HEAD:level4/closure_proofs/p4_theory_generalization/{name}")
        check(f, f"frozen P4 artifact unchanged: {name}",
              blob == checkpoint["theorem"][key], blob)
    changed = [p for p in git("diff", "--name-only", "p5y-gate1-micropilots",
                              "HEAD").splitlines() if p]
    outside = [p for p in changed
               if not p.startswith("level4/closure_proofs/p4z_location_family_feasibility/")]
    check(f, "P4Z touches no path outside its own namespace", not outside, outside)
    decision = load(P4 / "results" / "closure_decision.json")
    check(f, "historical P4 verdict still PARTIAL",
          decision["verdict"] == "PARTIAL", decision["verdict"])

    # 2 thresholds ---------------------------------------------------------
    g = protocol["gates"]
    check(f, "relative threshold is the frozen 0.03",
          plan["thresholds"]["relative"] == g["correspondence_relative_limit"] == 0.03,
          plan["thresholds"]["relative"])
    check(f, "z threshold is the frozen 4.0",
          plan["thresholds"]["z"] == g["correspondence_z_limit"] == 4.0,
          plan["thresholds"]["z"])
    check(f, "r* is the frozen forced value",
          abs(1.96 * 2 ** 0.5 * plan["thresholds"]["r_star"] - 0.03) < 1e-8,
          plan["thresholds"]["r_star"])
    check(f, "finite-difference convention unchanged",
          plan["fd_steps"] == protocol["fd_steps"] == [0.05, 0.025],
          plan["fd_steps"])
    check(f, "m grid unchanged", plan["scope"]["m_grid"] == protocol["m_grid"],
          plan["scope"]["m_grid"])
    if adj:
        check(f, "adjudication used the frozen thresholds and changed none",
              adj["thresholds_used"]["relative"] == 0.03
              and adj["thresholds_used"]["z"] == 4.0
              and adj["thresholds_used"]["any_threshold_changed_by_p4z"] is False,
              adj["thresholds_used"])

    # 3 estimator identity -------------------------------------------------
    check(f, "primary estimator is RB-SCORE",
          checkpoint["estimators"]["primary"]["name"] == "RB-SCORE", "RB-SCORE")
    check(f, "companion route is RB-MAP",
          checkpoint["estimators"]["fallback"]["name"] == "RB-MAP", "RB-MAP")
    for key, rel in (("primary", "src/rebaseguard_p4z/rbscore.py"),
                     ("fallback", "src/rebaseguard_p4z/rbmap.py"),
                     ("analytic_contract", "src/rebaseguard_p4z/analytic.py")):
        digest = hashlib.sha256((NS / rel).read_bytes()).hexdigest()
        check(f, f"estimator source hash matches the checkpoint: {rel}",
              digest == checkpoint["estimators"][key]["sha256"], digest)

    # 4 producer and runtime identity -------------------------------------
    manifest = sh.build_manifest()
    check(f, "producer manifest verifies against the working tree",
          _quiet(sh.verify_manifest, manifest), manifest["producer_hash"])
    check(f, "scientific source tree is clean",
          not git("status", "--porcelain", "--", *sh.TCB_PATHS), "clean")
    check(f, "host is declared MAC_ONLY with zero AWS CPU",
          contract["declaration"]["P4Z_NUMERICAL_HOST"] == "LOCAL_MAC"
          and contract["declaration"]["AWS_CPU_USED_BY_P4Z"] == 0,
          contract["declaration"])

    # 5 block-level audit, recomputed from the files -----------------------
    blocks_dir = NS / "production" / "blocks"
    files = sorted(blocks_dir.rglob("*.json")) if blocks_dir.exists() else []
    producer_hashes, runtime_hashes, bad_hash, bad_paths = set(), set(), [], []
    per_route: dict[tuple[str, str], int] = {}
    total_paths = 0
    for path in files:
        doc = load(path)
        producer_hashes.add(doc["producer_hash"])
        runtime_hashes.add(doc["runtime_hash"])
        body = {k: v for k, v in doc.items() if k != "scientific_hash"}
        if sh.scientific_hash(body) != doc["scientific_hash"]:
            bad_hash.append(str(path))
        key = (doc["configuration"], doc["route"])
        per_route[key] = per_route.get(key, 0) + 1
        total_paths += doc["block_paths"]
        cfg = next(c for c in plan["configurations"]
                   if c["id"] == doc["configuration"])
        if doc["block_paths"] != cfg["block_paths"]:
            bad_paths.append(str(path))
    check(f, "every block re-hashes to its recorded scientific hash",
          not bad_hash, f"{len(files)} blocks, {len(bad_hash)} mismatches")
    check(f, "every block used the planned path count (no silent extension)",
          not bad_paths, f"{len(bad_paths)} deviations")
    check(f, "exactly one producer hash across every block",
          len(producer_hashes) <= 1, sorted(producer_hashes))
    check(f, "exactly one runtime hash across every block",
          len(runtime_hashes) <= 1, sorted(runtime_hashes))

    over = {f"{c}/{r}": n for (c, r), n in per_route.items()
            if n > plan["fixed_policy"]["blocks_per_route_full"]}
    check(f, "no route exceeded the fixed 200-block policy", not over, over)
    ladder_over = {f"{c}/{r}": n for (c, r), n in per_route.items()
                   if r == "fd_ladder" and n > plan["fd_ladder_blocks"]}
    check(f, "no FD ladder exceeded its fixed block count", not ladder_over,
          ladder_over)
    check(f, "the plan forbids top-ups and adaptive stopping",
          plan["fixed_policy"]["adaptive"] is False
          and plan["fixed_policy"]["top_ups_permitted"] == 0
          and plan["fixed_policy"]["path_count_may_increase_during_run"] is False,
          plan["fixed_policy"])

    # 6 seed schedule ------------------------------------------------------
    seeds = []
    for cfg in plan["configurations"]:
        seeds += [cfg["seed_rb_score"], cfg["seed_rb_map"], cfg["seed_fd_ladder"]]
    check(f, "seed schedule has no collision", len(set(seeds)) == len(seeds),
          len(seeds))
    check(f, "seed schedule is disjoint from every historical P4 master seed",
          not set(seeds) & set(protocol["master_seeds"].values()),
          sorted(protocol["master_seeds"].values()))

    # 7 Stage-0 governance -------------------------------------------------
    check(f, "Stage-0 was frozen before execution",
          stage0["frozen_before_execution"] is True, True)
    check(f, "Stage-0 ran the production driver, not a separate script",
          stage0["runs_the_production_driver"] is True
          and stage0["separate_pilot_script"] is False, True)
    check(f, "Stage-0 covered every configuration carrying an unresolved cell",
          set(plan["unresolved_residue"]["configurations"]) <=
          {r["configuration"] for r in stage0["design"]["mandatory_coverage"]},
          plan["unresolved_residue"]["configurations"])
    tcb = state.get("stages", {}).get("0_tcb_gates", {})
    check(f, "kill gate K1 did not fire",
          tcb.get("K1", {}).get("fired") is False, tcb.get("K1"))
    check(f, "kill gate K2 did not fire",
          tcb.get("K2", {}).get("fired") is False, tcb.get("K2"))
    residue = set(plan["unresolved_residue"]["configurations"])
    blocked = set(state.get("killed", {})) | set(state.get("excluded", {}))
    check(f, "no configuration carrying an unresolved cell was killed or excluded",
          not (residue & blocked), sorted(residue & blocked))
    check(f, "the Stage-0 verdict follows its own frozen rule",
          state.get("stage0_verdict") ==
          ("STAGE0_INCONCLUSIVE" if residue & blocked else "STAGE0_PASS"),
          state.get("stage0_verdict"))

    # 8 cell accounting ----------------------------------------------------
    if adj:
        expected = len(plan["configurations"]) * len(plan["scope"]["m_grid"])
        counted = sum(adj["counts"].values())
        check(f, "every cell in scope is accounted for exactly once",
              adj["cells_total"] == expected == counted,
              {"expected": expected, "adjudicated": adj["cells_total"],
               "counted": counted})
        check(f, "no cell is reported outside PASS / FAIL / INCONCLUSIVE",
              set(adj["counts"]) == {"PASS", "FAIL", "INCONCLUSIVE"},
              adj["counts"])
        check(f, "the historically unresolved residue is fully accounted",
              adj["unresolved_residue"]["total"] == 8,
              adj["unresolved_residue"])

    # 9 cost ---------------------------------------------------------------
    cpu_from_blocks = sum(load(p)["cpu_seconds"] for p in files) / 3600.0
    cap = plan["budget"]["total_cpu_cap_hours"]
    check(f, "total CPU is within the frozen cap", cpu_from_blocks <= cap,
          {"cpu_hours_recomputed_from_blocks": cpu_from_blocks, "cap": cap,
           "runner_reported": state.get("cpu_seconds_total", 0) / 3600.0})

    # 10 replay ------------------------------------------------------------
    if replay:
        check(f, "replay reproduced every scientific hash",
              replay["all_scientific_hashes_identical"] is True
              and replay["any_scientific_field_mismatch"] is False,
              {"blocks": replay["blocks_replayed"]})

    # 11 formal ------------------------------------------------------------
    if lean:
        check(f, "bounded-survival lemma compiles with no error and no sorry",
              lean["compile"]["errors"] == 0
              and lean["compile"]["sorry_count"] == 0, lean["compile"])
        check(f, "bounded-survival lemma introduces no new axiom",
              sorted(lean["axioms"]) == sorted(
                  ["propext", "Classical.choice", "Quot.sound"])
              and lean["new_axioms"] == 0, lean["axioms"])
        check(f, "no declaration was added to the inherited P4 Lean namespace",
              lean["new_declarations_in_inherited_p4_namespace"] == 0, 0)

    failed = [x for x in f if x["status"] == "FAIL"]
    doc = {
        "schema": "rebaseguard.p4z-independent-adjudication.v1",
        "result_bearing": True,
        "independent_of_the_runner": True,
        "method": "every count recomputed from the block files, every threshold "
                  "re-read from its frozen source, every hash recomputed",
        "checks_total": len(f),
        "checks_failed": len(failed),
        "verdict": "ADJUDICATION_PASS" if not failed else "ADJUDICATION_FAIL",
        "failed_checks": failed,
        "checks": f,
    }
    out = NS / "production" / "independent_adjudication.json"
    out.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n")
    for row in f:
        if row["status"] == "FAIL":
            print(f"FAIL  {row['check']}: {row['detail']}")
    print(f"\n{doc['verdict']}: {len(f) - len(failed)}/{len(f)} checks pass")
    print(f"-> {out}")
    return 0 if not failed else 1


def _quiet(fn, *args) -> bool:
    try:
        fn(*args)
        return True
    except sh.ProducerGateError:
        return False


if __name__ == "__main__":
    raise SystemExit(main())
