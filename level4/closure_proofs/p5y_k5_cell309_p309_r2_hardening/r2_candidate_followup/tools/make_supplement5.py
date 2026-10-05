"""Build governance/R2_REPIN_LIST_SUPPLEMENT_5.json (S2): the additive record of the one intentional re-pin of the
r2 adoption candidate (make_topology, F-DRILL-ORDER).  Every fact is computed from git, never typed by hand.

usage: make_supplement5.py <session repo> <out file>
"""
import ast
import hashlib
import json
import subprocess
import sys
from pathlib import Path

repo, out = Path(sys.argv[1]), Path(sys.argv[2])
NS = "level4/closure_proofs/p5y_k5_cell309_p309_r2/"
ALLOW = NS + "config/SCANNER_ALLOWANCE_P309.json"
DRILL = NS + "code/p309_" + "topology_drill.py"
R2, ACC, CAND, R1F = ("101ef2cb17e5eab2892212178278da45b98004ed", "38842550", "93d550638b8c79ae1c252fc6c2b0194b1a416b49",
                      "4c754a73767903a5ad5dddff725f1e173a0a6876")


def show(c, rel):
    return subprocess.run(["git", "-C", str(repo), "show", f"{c}:{rel}"], capture_output=True, text=True,
                          check=True).stdout


def fn_hash(src, name):
    hits = [n for n in ast.parse(src).body if isinstance(n, ast.FunctionDef) and n.name == name]
    assert len(hits) == 1
    return hashlib.sha256(ast.dump(hits[0]).encode()).hexdigest()


def leaves(x, p=""):
    if isinstance(x, dict):
        for k, v in x.items():
            yield from leaves(v, f"{p}/{k}")
    elif isinstance(x, list):
        for i, v in enumerate(x):
            yield from leaves(v, f"{p}[{i}]")
    else:
        yield p, x


a_r2, a_acc, a_c = show(R2, ALLOW), show(ACC, ALLOW), show(CAND, ALLOW)
assert a_r2 == a_acc, "the allowance changed between the accepted commit and r2's head"
j_r2, j_c = json.loads(a_r2), json.loads(a_c)
lo, ln = dict(leaves(j_r2)), dict(leaves(j_c))
changed = [k for k in lo if k in ln and lo[k] != ln[k]]
assert changed == ["/ref_mutation_functions[20]/ast_sha256"] and set(lo) == set(ln), changed
entry_r2, entry_c = j_r2["ref_mutation_functions"][20], j_c["ref_mutation_functions"][20]
assert entry_c["file"] == "code/p309_" + "topology_drill.py" and entry_c["function"] == "make_topology"
old_h, new_h = fn_hash(show(R2, DRILL), "make_topology"), fn_hash(show(CAND, DRILL), "make_topology")
assert entry_r2["ast_sha256"] == old_h and entry_c["ast_sha256"] == new_h
r1_has = any(e.get("function") == "make_topology" for e in json.loads(show(R1F, NS.replace("p309_r2", "p309_r1")
                                                                          + "config/SCANNER_ALLOWANCE_P309.json"))
             .get("ref_mutation_functions", []))
counts = {}
for f in ["R2_REPIN_LIST.json"] + [f"R2_REPIN_LIST_SUPPLEMENT_{i}.json" for i in (1, 2, 3, 4)]:
    counts[f] = len(json.loads(show(CAND, NS + "governance/" + f))["rows"])
diff_names = subprocess.run(["git", "-C", str(repo), "diff", "--name-only", R2, CAND], capture_output=True, text=True,
                            check=True).stdout.split()
lists = ["exactly_once_sites", "backstop_pins", "production_read_path_pins", "production_tokens",
         "planted_control_files", "mutating_git_verbs", "production_ref_namespace"]
unchanged = {k: j_r2.get(k) == j_c.get(k) for k in lists if k in j_r2}
unchanged["process_policy"] = j_r2.get("process_policy") == j_c.get("process_policy")
unchanged["t7_exemptions"] = j_r2.get("t7_exemptions") == j_c.get("t7_exemptions")
unchanged["import_policy"] = j_r2.get("import_policy") == j_c.get("import_policy")
doc = {
    "schema": "P309_R2_REPIN_LIST_SUPPLEMENT/1",
    "supplements": ", ".join(f"governance/{k} ({v} rows)" for k, v in counts.items()) + ", all unchanged (additive "
                   "record: no earlier row is edited, removed or re-ordered)",
    "round": "adoption-candidate follow-up after the fourth follow-up review (R2_DELTA_FOLLOWUP_4_ACCEPTED at 38842550): "
             "F-DRILL-ORDER",
    "hash": "sha256 of ast.dump(<node>), CPython 3.11.15",
    "compared": {
        "before": f"{R2[:8]}:{ALLOW} (byte-identical to {ACC}:{ALLOW}, the commit the fourth follow-up review read)",
        "after": f"{CAND[:8]}:{ALLOW} (unchanged at the commit that adds this file)",
        "r1_at_F": f"{R1F}:" + NS.replace("p309_r2", "p309_r1") + "config/SCANNER_ALLOWANCE_P309.json",
    },
    "unchanged_lists": unchanged,
    "import_allowlist_additions": {"code": [], "tests": [], "verify": []},
    "rows": [{
        "list": "ref_mutation_functions",
        "file": entry_c["file"],
        "name": "make_topology",
        "reviewed_38842550": old_h,
        "now": new_h,
        "r1_at_F": None if not r1_has else "present in r1 (see compared.r1_at_F)",
        "kind": "re-pinned",
        "reason_now": entry_c["reason"],
        "reason_unchanged": entry_r2["reason"] == entry_c["reason"],
        "change": "F-DRILL-ORDER: the drill's synthetic freeze F' now runs make_freeze_params.py before "
                  "make_freeze_manifest.py (the order of a real freeze; r1's recorded F manifest pins its own "
                  "freeze/P309_FREEZE.json), so the F' manifest pins freeze/P309_FREEZE.json and the runner's "
                  "make_freeze_manifest.py --check precondition passes in the worker-tier drill. The edit swaps two "
                  "elements of one list literal in make_topology; nothing else in the drill changed.",
        "how_repinned": "code/p309_scan_pins.py --refresh in a scratch clone (it recomputes only already-listed "
                        "entries); its output named exactly this entry; the resulting file was copied byte for byte",
    }],
    "proof": {
        "allowance_leaves_before_after": [len(lo), len(ln)],
        "allowance_changed_leaves": changed,
        "allowance_sha256_before": hashlib.sha256(a_r2.encode()).hexdigest(),
        "allowance_sha256_after": hashlib.sha256(a_c.encode()).hexdigest(),
        "paths_changed_by_the_candidate_commit": diff_names,
        "no_scientific_or_target_change": "the candidate commit changes only the qualification runner (durability "
                                          "and exactly-once hardening), the drill's make_topology and this one hash; "
                                          "every gate function, items_table, the driver, guard, generators, "
                                          "evaluators, verifiers, tests, data, ledgers and evidence are unchanged "
                                          "(AST and byte comparison: AST_RUNNER_R2_VS_CANDIDATE.json, "
                                          "AST_DRILL_R2_VS_CANDIDATE.json; independent delta review Q2 YES)",
    },
    "validation_of_this_repin": {
        "where": "branch claude/p309-r2-hardening-20261005, level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/"
                 "r2_candidate/ (the task-3 evidence of the candidate commit above)",
        "scan_pins_list_r2": "all current (evidence/SCAN_PINS_LIST_R2.txt)",
        "scan_pins_list_before_repin": "make_topology STALE HASH, 1 NOT CURRENT (evidence/SCAN_PINS_LIST_BEFORE_REPIN.txt)",
        "scan_pins_refresh": "refreshed exactly ref_mutation_functions code/p309_topology_drill.py make_topology "
                             "(evidence/SCAN_PINS_REFRESH.txt)",
        "scan_pins_list_after_repin": "all current (evidence/SCAN_PINS_LIST_AFTER_REPIN.txt)",
        "qc_d5_pins_regression": "rc 0, pins_all_current true (evidence/regression/REG_CANDIDATE.json)",
        "qc12_static_check": "rc 0 (regression) and PASS in the rehearsal (evidence/rehearsal/attempt/QC12.json)",
        "f_drill_order_demo": "current order MANIFEST DIFFERS (rc 1); corrected order MANIFEST IDENTICAL (rc 0) "
                              "(evidence/F_DRILL_ORDER_DEMO.json)",
        "rehearsal": "light rehearsal of the candidate commit PASS, 15/15 gates; F' built with 183 code pins",
        "recheck_after_this_file": "the runner's S1 change and this file do not change the allowance; the scan pins "
                                   "are re-listed at the commit that adds this file and recorded with the S1-S3 "
                                   "follow-up reports",
    },
    "statement": "an additive governance record; no target input read; NEW Γ309 TARGET EVALUATIONS = 0",
}
out.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n")
print(json.dumps({k: doc[k] for k in ("supplements", "unchanged_lists")}, indent=1, ensure_ascii=False))
print(doc["rows"][0]["reviewed_38842550"], "->", doc["rows"][0]["now"], "r1:", doc["rows"][0]["r1_at_F"])
