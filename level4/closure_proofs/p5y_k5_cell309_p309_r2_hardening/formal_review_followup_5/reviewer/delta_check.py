#!/usr/bin/env python3
"""Independent recomputation for formal delta follow-up review 5 (read-only: `git show` only; nothing imported from r2).
- AST comparison of every top-level node of the runner and the drill, r2 101ef2cb vs candidate a119e978;
- sha256(ast.dump(make_topology)) at both commits (the scanner's definition, re-implemented here);
- allowance leaf diff and file hashes; byte identity of R2_REPIN_LIST.json and supplements 1-4;
- every allowance pin that names a runner/drill function, recomputed at the candidate."""
import ast
import hashlib
import json
import subprocess

REPO = "/home/user/ReBaseGuard"
R2 = "101ef2cb17e5eab2892212178278da45b98004ed"
CA = "a119e9789e2a1d42b584fff8a2301946a37f1bcb"
FU4 = "38842550f7a3bcfc264bef954cd60861704c9ece"
T3 = "93d550638b8c79ae1c252fc6c2b0194b1a416b49"
NS = "level4/closure_proofs/p5y_k5_cell309_p309_r2"
RUNNER = "code/" + "p309_" + "qualify.py"
DRILL = "code/" + "p309_" + "topology_drill.py"


def show(commit, rel, binary=False):
    r = subprocess.run(["git", "-C", REPO, "show", f"{commit}:{NS}/{rel}"], capture_output=True)
    if r.returncode != 0:
        return None
    return r.stdout if binary else r.stdout.decode()


def sha(b):
    return hashlib.sha256(b).hexdigest()


def node_name(n):
    if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
        return n.name
    if isinstance(n, ast.Assign):
        return "assign:" + ",".join(ast.unparse(t) for t in n.targets)
    if isinstance(n, ast.AnnAssign):
        return "annassign:" + ast.unparse(n.target)
    return type(n).__name__ + ":" + ast.unparse(n)[:60]


def top(src):
    out = {}
    for i, n in enumerate(ast.parse(src).body):
        k = node_name(n)
        if k in out:
            k = f"{k}#{i}"
        out[k] = (sha(ast.dump(n).encode()), ast.get_source_segment(src, n))
    return out


def ast_compare(rel, a=R2, b=CA):
    A, B = top(show(a, rel)), top(show(b, rel))
    added = [k for k in B if k not in A]
    removed = [k for k in A if k not in B]
    changed = [k for k in A if k in B and A[k][0] != B[k][0]]
    same = [k for k in A if k in B and A[k][0] == B[k][0]]
    order_same = [k for k in A if k in B] == [k for k in B if k in A]
    return {"file": rel, "nodes_before": len(A), "nodes_after": len(B), "added": added, "removed": removed,
            "changed": changed, "unchanged_count": len(same), "relative_order_unchanged": order_same}


def func_hash(src, name):
    hits = [n for n in ast.walk(ast.parse(src)) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
            and n.name == name]
    return [sha(ast.dump(h).encode()) for h in hits]


def leaves(x, p=""):
    if isinstance(x, dict):
        for k, v in x.items():
            yield from leaves(v, f"{p}/{k}")
    elif isinstance(x, list):
        for i, v in enumerate(x):
            yield from leaves(v, f"{p}[{i}]")
    else:
        yield p, x


res = {}
res["ast_runner_r2_vs_candidate"] = ast_compare(RUNNER)
res["ast_runner_93d55063_vs_candidate"] = ast_compare(RUNNER, T3, CA)
res["ast_drill_r2_vs_candidate"] = ast_compare(DRILL)
res["make_topology_ast_sha256"] = {"r2": func_hash(show(R2, DRILL), "make_topology"),
                                   "candidate": func_hash(show(CA, DRILL), "make_topology")}

al_a, al_b = show(R2, "config/SCANNER_ALLOWANCE_P309.json", True), show(CA, "config/SCANNER_ALLOWANCE_P309.json", True)
al_fu4 = show(FU4, "config/SCANNER_ALLOWANCE_P309.json", True)
la, lb = dict(leaves(json.loads(al_a))), dict(leaves(json.loads(al_b)))
res["allowance"] = {"sha256_r2": sha(al_a), "sha256_candidate": sha(al_b), "r2_equals_38842550": al_a == al_fu4,
                    "leaves": [len(la), len(lb)],
                    "changed_leaves": {k: [la.get(k), lb.get(k)] for k in sorted(set(la) | set(lb))
                                       if la.get(k) != lb.get(k)}}

gov = {}
for n in ["R2_REPIN_LIST.json"] + [f"R2_REPIN_LIST_SUPPLEMENT_{i}.json" for i in range(1, 6)]:
    a, b, f = show(R2, "governance/" + n, True), show(CA, "governance/" + n, True), show(FU4, "governance/" + n, True)
    rows = None
    if b is not None:
        d = json.loads(b)
        rows = len(d.get("rows", d if isinstance(d, list) else [])) if isinstance(d, (dict, list)) else None
    gov[n] = {"in_r2": a is not None, "in_candidate": b is not None, "byte_identical_r2_candidate": a == b,
              "byte_identical_38842550_candidate": f == b, "sha256_candidate": sha(b) if b else None, "rows": rows}
res["repin_lists"] = gov

# every allowance entry that names a function in the runner or the drill: recompute at the candidate
cfg = json.loads(al_b)
pins = []
for key, val in cfg.items():
    if not isinstance(val, list):
        continue
    for e in val:
        if isinstance(e, dict) and e.get("file") in (RUNNER, DRILL) and e.get("function"):
            fn = e["function"].split(".")[-1]
            hs_c = func_hash(show(CA, e["file"]), fn)
            hs_r = func_hash(show(R2, e["file"]), fn)
            pins.append({"list": key, "file": e["file"], "function": e["function"], "pinned": e.get("ast_sha256"),
                         "candidate": hs_c, "r2": hs_r, "current": e.get("ast_sha256") in hs_c,
                         "unchanged_since_r2": hs_c == hs_r})
res["runner_drill_pins"] = pins

# the runner's gate machinery: every function used by items_table, unchanged?
gate_fns = ["items_table", "run", "mirror", "research_test", "qc_research_simple", "qc05", "qc06", "qc07",
            "decoy_stage1a", "qc08", "qc09", "qc10", "git", "qc_formal", "ledger_append_only", "qc13",
            "single_run_since_freeze", "qc16", "qc_u2", "qc17", "qc_d5", "qhost_preflight", "start_qhost_monitor",
            "stop_qhost_monitor", "_under", "utc", "sha_file", "git_show"]
src_r, src_c = show(R2, RUNNER), show(CA, RUNNER)
res["gate_functions_unchanged"] = {f: func_hash(src_r, f) == func_hash(src_c, f) and bool(func_hash(src_c, f))
                                   for f in gate_fns}
print(json.dumps(res, indent=1, sort_keys=True))
