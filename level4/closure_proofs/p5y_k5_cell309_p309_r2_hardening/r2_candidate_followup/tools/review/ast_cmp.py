"""E and G: AST comparison of the runner across 93d55063 -> a119e978, pinned functions, make_topology hashes,
allowance and prior re-pin files (read via git show; nothing imported or executed)"""
import ast
import hashlib
import json
import subprocess

REPO = "/home/user/ReBaseGuard"
NS = "level4/closure_proofs/p5y_k5_cell309_p309_r2/"
RUNNER = "code/p309_" + "qualify.py"
DRILL = "code/p309_" + "topology_drill.py"


def show(rev, rel, binary=False):
    r = subprocess.run(["git", "-C", REPO, "show", f"{rev}:{NS}{rel}"], capture_output=True, check=True)
    return r.stdout if binary else r.stdout.decode()


def h(node):
    return hashlib.sha256(ast.dump(node).encode()).hexdigest()


def toplevel(src):
    tree = ast.parse(src)
    funcs, other = {}, []
    for i, n in enumerate(tree.body):
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            funcs[n.name] = n
        else:
            other.append(ast.dump(n))
    return funcs, other


out = {}
a_f, a_o = toplevel(show("93d55063", RUNNER))
b_f, b_o = toplevel(show("a119e978", RUNNER))
out["runner_added"] = sorted(set(b_f) - set(a_f))
out["runner_removed"] = sorted(set(a_f) - set(b_f))
out["runner_changed"] = sorted(k for k in set(a_f) & set(b_f) if h(a_f[k]) != h(b_f[k]))
out["runner_unchanged_count"] = sum(1 for k in set(a_f) & set(b_f) if h(a_f[k]) == h(b_f[k]))
out["runner_module_level_statements_identical"] = a_o == b_o
out["runner_module_level_statement_count"] = [len(a_o), len(b_o)]
# order of top-level defs
out["runner_def_order_same_for_common"] = [k for k in a_f] == [k for k in b_f if k in a_f]

allow_a = json.loads(show("93d55063", "config/SCANNER_ALLOWANCE_P309.json"))
allow_b_bytes = show("a119e978", "config/SCANNER_ALLOWANCE_P309.json", True)
out["allowance_identical_93d55063_a119e978"] = show("93d55063", "config/SCANNER_ALLOWANCE_P309.json", True) == allow_b_bytes
out["allowance_sha256_a119e978"] = hashlib.sha256(allow_b_bytes).hexdigest()
out["allowance_sha256_101ef2cb"] = hashlib.sha256(show("101ef2cb", "config/SCANNER_ALLOWANCE_P309.json", True)).hexdigest()
out["allowance_sha256_38842550"] = hashlib.sha256(show("38842550", "config/SCANNER_ALLOWANCE_P309.json", True)).hexdigest()
pinned = {}
for e in allow_a["process_policy"]["reviewed_functions"]:
    if e["file"] == RUNNER:
        fn = b_f.get(e["function"])
        pinned[e["function"]] = {"pinned": e["ast_sha256"][:16], "at_a119e978": h(fn)[:16] if fn else None,
                                 "match": fn is not None and h(fn) == e["ast_sha256"]}
out["runner_reviewed_functions"] = pinned
# every other allowance list entry naming the runner
other = []
for key, val in allow_a.items():
    if isinstance(val, list):
        for e in val:
            if isinstance(e, dict) and e.get("file") == RUNNER and "ast_sha256" in e:
                fn = b_f.get(e.get("function"))
                other.append([key, e.get("function"), fn is not None and h(fn) == e["ast_sha256"]])
out["runner_entries_any_list"] = other

# make_topology
mt = {}
for rev in ("101ef2cb", "38842550", "93d55063", "a119e978"):
    f, _ = toplevel(show(rev, DRILL))
    mt[rev] = h(f["make_topology"])
out["make_topology_sha256"] = mt
r101 = json.loads(show("101ef2cb", "config/SCANNER_ALLOWANCE_P309.json"))
out["allowance_101ef2cb_make_topology"] = [e["ast_sha256"] for e in r101["ref_mutation_functions"]
                                          if e["function"] == "make_topology"]
out["allowance_a119e978_make_topology"] = [(i, e["ast_sha256"]) for i, e in enumerate(allow_a["ref_mutation_functions"])
                                           if e["function"] == "make_topology"]


def leaves(x, p=""):
    if isinstance(x, dict):
        r = {}
        for k, v in x.items():
            r.update(leaves(v, f"{p}/{k}"))
        return r
    if isinstance(x, list):
        r = {}
        for i, v in enumerate(x):
            r.update(leaves(v, f"{p}[{i}]"))
        return r
    return {p: x}


la, lb = leaves(r101), leaves(allow_a)
out["allowance_leaves_101_vs_93d"] = [len(la), len(lb)]
out["allowance_changed_leaves_101_vs_93d"] = sorted(k for k in set(la) | set(lb) if la.get(k, object) != lb.get(k, object))
# which top-level allowance keys changed between 101ef2cb and 93d55063
out["allowance_keys_changed_101_vs_93d"] = sorted(k for k in set(r101) | set(allow_a) if r101.get(k) != allow_a.get(k))

# prior re-pin files byte-identical
rp = {}
for name in ["R2_REPIN_LIST.json"] + [f"R2_REPIN_LIST_SUPPLEMENT_{i}.json" for i in range(1, 5)]:
    bs = [hashlib.sha256(show(rev, "governance/" + name, True)).hexdigest() for rev in ("101ef2cb", "93d55063", "a119e978")]
    d = json.loads(show("a119e978", "governance/" + name))
    rp[name] = {"identical": len(set(bs)) == 1, "rows": len(d.get("rows", [])) if isinstance(d, dict) else None}
out["prior_repin_files"] = rp

# paths changed 101ef2cb..93d55063
out["paths_101_to_93d"] = subprocess.run(["git", "-C", REPO, "diff", "--name-only", "101ef2cb", "93d55063"],
                                         capture_output=True, text=True).stdout.split()
out["paths_93d_to_a119"] = subprocess.run(["git", "-C", REPO, "diff", "--name-only", "93d55063", "a119e978"],
                                          capture_output=True, text=True).stdout.split()
# drill diff: only make_topology changed?
d1, o1 = toplevel(show("101ef2cb", DRILL))
d2, o2 = toplevel(show("93d55063", DRILL))
out["drill_changed_funcs_101_vs_93d"] = sorted(k for k in set(d1) | set(d2) if (k in d1) != (k in d2) or h(d1[k]) != h(d2[k]))
out["drill_module_level_identical"] = o1 == o2
print(json.dumps(out, indent=1))
