#!/usr/bin/env python3
"""Compute the P9R frozen gates I1-I15 mechanically.

Nothing here trusts P9R prose.  ``I1``-``I4`` and ``I2`` in particular are
computed by running git against the anchor commit, so an adjudicator can
re-run this program and get the same answer without reading a word of
``TEMPORAL_ANCHOR.md``.

Usage: audit_integrity.py --anchor <sha>
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

P9R = Path(__file__).resolve().parents[1]
ROOT = P9R.parents[2]
REL = "level4/closure_proofs/p9r_final_synthesis_repair"
P9_NS = "level4/closure_proofs/p9_final_synthesis"
P9_ADJ_COMMIT = "a3e3cabc30c4508b866736aeede54db17e5e1fcc"

sys.path.insert(0, str(P9R / "src"))
sys.path.insert(0, str(P9R / "experiments"))


def git(*args) -> str:
    return subprocess.run(["git", "-C", str(ROOT), *args],
                          capture_output=True, text=True).stdout.strip()


def git_ok(*args) -> bool:
    return subprocess.run(["git", "-C", str(ROOT), *args],
                          capture_output=True, text=True).returncode == 0


def blob_at(commit: str, path: str) -> bytes | None:
    r = subprocess.run(["git", "-C", str(ROOT), "show", f"{commit}:{path}"],
                       capture_output=True)
    return r.stdout if r.returncode == 0 else None


def load(rel: str):
    p = P9R / rel
    return json.loads(p.read_text()) if p.exists() else None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--anchor", required=True)
    args = ap.parse_args()
    anchor = args.anchor
    g: dict[str, dict] = {}

    def gate(gid, ok, detail):
        g[gid] = {"pass": bool(ok), "detail": detail}

    # ---- I1 temporal anchor -------------------------------------------
    anchor_exists = git_ok("cat-file", "-e", f"{anchor}^{{commit}}")
    is_ancestor = git_ok("merge-base", "--is-ancestor", anchor, "HEAD")
    tree = git("ls-tree", "-r", "--name-only", anchor, "--", REL).splitlines()
    results_at_anchor = [p for p in tree if p.startswith(f"{REL}/results/")]
    allowed = {f"{REL}/results/integrity/protected_tree_manifest_pre.json"}
    stray = sorted(set(results_at_anchor) - allowed)
    required = ["FROZEN_PROTOCOL.md", "FROZEN_GATES.md", "THEORY.md",
                "COMMAND_MANIFEST.json", "SOURCE_MANIFEST.json",
                "PROTOCOL_DIGEST.json", "experiments/ledger_schema.py",
                "experiments/claims_source.py",
                "experiments/run_response_grid.py",
                "experiments/run_burnin_sensitivity.py",
                "src/rebaseguard_p9r/detectors.py"]
    missing = [r for r in required if f"{REL}/{r}" not in tree]
    gate("I1", anchor_exists and is_ancestor and not stray and not missing,
         {"anchor": anchor, "exists": anchor_exists,
          "ancestor_of_head": is_ancestor,
          "results_files_at_anchor": sorted(results_at_anchor),
          "stray_result_files": stray, "missing_required": missing,
          "n_p9r_files_at_anchor": len(tree)})

    # ---- I2 original P9 immutable -------------------------------------
    diff = git("diff", "--stat", P9_ADJ_COMMIT, "HEAD", "--", P9_NS)
    t_now = git("rev-parse", f"HEAD:{P9_NS}")
    t_adj = git("rev-parse", f"{P9_ADJ_COMMIT}:{P9_NS}")
    commits = git("log", "--format=%H", "--", P9_NS).split()
    gate("I2", diff == "" and t_now == t_adj and commits == [P9_ADJ_COMMIT],
         {"diff_empty": diff == "", "tree_at_head": t_now,
          "tree_at_adjudication": t_adj,
          "commits_touching_p9": commits})

    # ---- I3 / I4 digests locked ---------------------------------------
    sm = load("SOURCE_MANIFEST.json") or {"files": {}}
    pd = load("PROTOCOL_DIGEST.json") or {"files": {}}
    for gid, man, label in (("I3", sm, "source"), ("I4", pd, "protocol")):
        drift = []
        for rel, digest in man["files"].items():
            at_anchor = blob_at(anchor, f"{REL}/{rel}")
            now = (P9R / rel).read_bytes() if (P9R / rel).exists() else None
            if at_anchor is None:
                drift.append(f"{rel}: absent at anchor")
            elif now != at_anchor:
                drift.append(f"{rel}: bytes differ from anchor")
        gate(gid, not drift, {"n_files": len(man["files"]),
                              "aggregate_sha256": man.get("aggregate_sha256"),
                              "drift": drift, "manifest": label})

    # ---- I5 SR recurrence ---------------------------------------------
    sr = load("results/sr_recurrence_check.json")
    p = sr and sr["payload"]
    gate("I5", bool(p and p.get("all_pass")
                    and p["C5_log2_shift"]["first_step_shift_is_exactly_log2"]
                    and p["C6_alarm_witness"]["decisions_differ"]),
         {"all_pass": p and p.get("all_pass"),
          "first_step_shift": p and p["C5_log2_shift"]["first_step_shift"],
          "alarm_decisions_differ": p and p["C6_alarm_witness"]["decisions_differ"]})

    # ---- I6 generator completeness ------------------------------------
    from rebaseguard_p9r.provenance import canonical_digest  # noqa: E402
    src_files = set((load("SOURCE_MANIFEST.json") or {"files": {}})["files"])
    bad = []
    checked = []
    for f in sorted((P9R / "results").rglob("*.json")):
        rel = str(f.relative_to(P9R / "results"))
        if rel.startswith("integrity/"):
            continue
        rec = json.loads(f.read_text())
        checked.append(rel)
        gen = (rec.get("generator") or "").replace(f"{REL}/", "")
        for field in ("generator", "argv", "git_commit", "environment",
                      "config", "payload_sha256", "payload"):
            if field not in rec:
                bad.append(f"{rel}: missing {field}")
        if gen not in src_files:
            bad.append(f"{rel}: generator {gen!r} not in SOURCE_MANIFEST")
        if rec.get("payload_sha256") != canonical_digest(rec.get("payload")):
            bad.append(f"{rel}: payload digest mismatch")
    gate("I6", not bad and checked,
         {"artifacts_checked": checked, "problems": bad})

    # ---- I7 - I13 from the ledger --------------------------------------
    ledger = load("results/claim_ledger.json")
    val = ledger["payload"]["validation"] if ledger else None
    viol = (val or {}).get("violations", {})
    rows = {r["id"]: r for r in ledger["payload"]["nodes"]} if ledger else {}

    gate("I7", bool(val) and "V8" not in viol,
         {"V8": viol.get("V8", []), "n_nodes": ledger and ledger["payload"]["n_nodes"]})
    firewall = [k for k in ("V1", "V2", "V3", "V4", "V5", "V11", "V14") if k in viol]
    gate("I8", bool(val) and not firewall,
         {"failing_rules": {k: viol[k] for k in firewall}})
    gate("I9", bool(val) and "V10" not in viol,
         {"V10": viol.get("V10", []),
          "asm_dom_present": "ASM-DOM" in rows,
          "t2b_assumptions": rows.get("P9R-T2b", {}).get("assumptions")})
    gate("I10", bool(val) and "V12" not in viol,
         {"p3_x1_class": rows.get("P3-X1", {}).get("claim_class")})
    expected = {"P7-A-ID": "EXACT_THEOREM", "P7-A-MONO": "NOT_ESTABLISHED",
                "P7-A-OP": "EMPIRICAL_ONLY", "P7-D0-ID": "EXACT_THEOREM",
                "P7-D0-DEF": "CONDITIONAL_THEOREM"}
    actual = {k: rows.get(k, {}).get("claim_class") for k in expected}
    gate("I11", actual == expected, {"expected": expected, "actual": actual})

    # I12: P8/P8R reconciliation and core independence
    edges = ledger["payload"]["graph"] if ledger else []
    parents: dict[str, list] = {}
    for e in edges:
        parents.setdefault(e["child"], []).append(e)
    reach, stack = set(), ["P9R-T2a", "P9R-T2b"]
    while stack:
        nid = stack.pop()
        for e in parents.get(nid, []):
            if e["type"] in ("LOGICAL_PREMISE", "ASSUMPTION") \
                    and e["parent"] not in reach:
                reach.add(e["parent"])
                stack.append(e["parent"])
    p8_touch = sorted(n for n in reach
                      if rows.get(n, {}).get("priority") in ("P8", "P8R"))
    gate("I12", "V13" not in viol and not p8_touch,
         {"V13": viol.get("V13", []),
          "p8_status": rows.get("P8-STATUS", {}).get("priority_status"),
          "p8r_status": rows.get("P8R-STATUS", {}).get("priority_status"),
          "core_premise_closure": sorted(reach),
          "p8_or_p8r_in_core_closure": p8_touch})

    results_md = (P9R / "RESULTS.md")
    novelty_ok = (results_md.exists()
                  and "NOVELTY_STATUS = NOT_ESTABLISHED" in results_md.read_text())
    gate("I13", "V14" not in viol and novelty_ok,
         {"V14": viol.get("V14", []),
          "results_declares_not_established": novelty_ok,
          "p9r_n1_class": rows.get("P9R-N1", {}).get("claim_class")})

    # ---- I14 protected tree --------------------------------------------
    pre = load("results/integrity/protected_tree_manifest_pre.json")
    fin = load("results/integrity/protected_tree_manifest_final.json")
    if pre and fin:
        a, b = pre["files"], fin["files"]
        changed = sorted(k for k in set(a) & set(b) if a[k] != b[k])
        added = sorted(set(b) - set(a))
        removed = sorted(set(a) - set(b))
        authorised = {"README.md"}
        unauthorised = [k for k in changed + added + removed
                        if k not in authorised]
        gate("I14", not unauthorised,
             {"n_pre": len(a), "n_final": len(b), "changed": changed,
              "added": added, "removed": removed,
              "authorised_root_status_files": sorted(authorised),
              "unauthorised": unauthorised,
              "p9_tree_pre": pre["trees"].get(P9_NS),
              "p9_tree_final": fin["trees"].get(P9_NS)})
    else:
        gate("I14", False, {"error": "protected manifests missing"})

    # ---- I15 focused tests ---------------------------------------------
    r = subprocess.run([sys.executable, "-m", "pytest", str(P9R / "tests"), "-q"],
                       capture_output=True, text=True, cwd=str(ROOT))
    tail = r.stdout.strip().splitlines()[-1] if r.stdout.strip() else ""
    gate("I15", r.returncode == 0, {"pytest_returncode": r.returncode,
                                    "summary": tail})

    n_pass = sum(1 for v in g.values() if v["pass"])
    report = {"schema": "rebaseguard.p9r.gate-report.v1",
              "anchor_commit": anchor,
              "head": git("rev-parse", "HEAD"),
              "gates": g, "n_gates": len(g), "n_pass": n_pass,
              "all_pass": n_pass == len(g)}
    out = P9R / "results" / "integrity" / "gate_report.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=1, default=str) + "\n")
    for gid in sorted(g, key=lambda x: int(x[1:])):
        print(f"{gid:4s} {'PASS' if g[gid]['pass'] else 'FAIL'}")
    print(f"{n_pass}/{len(g)} integrity gates pass")
    return 0 if report["all_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
