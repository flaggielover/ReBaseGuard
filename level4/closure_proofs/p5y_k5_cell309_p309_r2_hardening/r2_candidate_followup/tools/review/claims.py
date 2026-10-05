"""G: claims of R2_REPIN_LIST_SUPPLEMENT_5.json"""
import ast
import hashlib
import json
import subprocess

REPO = "/home/user/ReBaseGuard"
NS = "level4/closure_proofs/p5y_k5_cell309_p309_r2/"
RUNNER = "code/p309_" + "qualify.py"


def show(rev, rel, ns=NS):
    r = subprocess.run(["git", "-C", REPO, "show", f"{rev}:{ns}{rel}"], capture_output=True)
    return r.stdout.decode() if r.returncode == 0 else None


def h(node):
    return hashlib.sha256(ast.dump(node).encode()).hexdigest()


def funcs(src):
    return {n.name: n for n in ast.parse(src).body if isinstance(n, (ast.FunctionDef, ast.ClassDef))}


out = {}
a, b = funcs(show("101ef2cb", RUNNER)), funcs(show("93d55063", RUNNER))
out["runner_changed_101_vs_93d"] = sorted(k for k in set(a) | set(b) if (k in a) != (k in b) or h(a[k]) != h(b[k]))
a101 = json.loads(show("101ef2cb", "config/SCANNER_ALLOWANCE_P309.json"))
e101 = [e for e in a101["ref_mutation_functions"] if e["function"] == "make_topology"][0]
a93 = json.loads(show("93d55063", "config/SCANNER_ALLOWANCE_P309.json"))
e93 = [e for e in a93["ref_mutation_functions"] if e["function"] == "make_topology"][0]
out["reason_unchanged"] = e101["reason"] == e93["reason"]
out["index_101"] = [i for i, e in enumerate(a101["ref_mutation_functions"]) if e["function"] == "make_topology"]
r1 = show("4c754a73767903a5ad5dddff725f1e173a0a6876", "config/SCANNER_ALLOWANCE_P309.json",
          "level4/closure_proofs/p5y_k5_cell309_p309_r1/")
out["r1_has_make_topology"] = None if r1 is None else any(
    e.get("function") == "make_topology" for e in json.loads(r1).get("ref_mutation_functions", []))
s5 = json.loads(show("a119e978", "governance/R2_REPIN_LIST_SUPPLEMENT_5.json"))
s4 = json.loads(show("a119e978", "governance/R2_REPIN_LIST_SUPPLEMENT_4.json"))
out["s4_keys"] = list(s4)
out["s5_keys"] = list(s5)
out["s4_row_keys"] = sorted({k for r in s4["rows"] for k in r})
out["s5_row_keys"] = sorted({k for r in s5["rows"] for k in r})
for i in (1, 2, 3):
    s = json.loads(show("a119e978", f"governance/R2_REPIN_LIST_SUPPLEMENT_{i}.json"))
    out[f"s{i}_keys"] = list(s)
print(json.dumps(out, indent=1))
