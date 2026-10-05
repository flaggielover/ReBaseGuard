"""Independent verification of r2 after the owner's SF1-A incorporation (message 6), from a FRESH clone of origin.

usage: verify_r2_fresh_sf1a.py <origin url> <hardening commit with the review evidence> <session repo> <work dir (new)>
                               <out.json>
The fresh clone fetches only origin's r2 branch.  Reviewed hashes are read from the session repository (the accepted
review's evidence at the given hardening commit, and the reviewed commit 716946e8 itself), never from the clone:
  * HEAD == 716946e8 (no new commit); tree == 3afb045c (the reviewed tree);
  * ancestry: first-parent chain 716946e8 -> b66a45f0 -> a119e978 -> 93d55063 -> 101ef2cb;
  * b66a45f0..HEAD changes exactly the runner; the runner's bytes equal the reviewed bytes (716946e8's blob, the
    AST evidence's new_sha256 and the regression-bound runner_sha256);
  * by AST (computed here) only fs_probe differs from b66a45f0's runner; the 9 pinned runner functions and every
    module-level statement are byte-identical; every other r2 file (driver, gates, config, allowance, pins, tests,
    governance) is the same blob as at b66a45f0;
  * no path outside r2's namespace changed since c902fe2f (QC15 A7); r1 tree ecd1c359; r5 unchanged; no r6;
    no freeze record and no qualification directory in r2.
"""
import ast
import hashlib
import json
import subprocess
import sys
from pathlib import Path

url, hb, repo, work, out = sys.argv[1], sys.argv[2], Path(sys.argv[3]), Path(sys.argv[4]), Path(sys.argv[5])
OLD, NEW = "b66a45f097989764176075802c953df4b72c2aef", "716946e8d9a6744d0b49de6acc802605b6eb1bf8"
TREE = "3afb045cea6b78c708686ecc9108abd6a2d46100"
NS2 = "level4/closure_proofs/p5y_k5_cell309_p309_r2/"
EVD = "level4/closure_proofs/p5y_k5_cell309_p309_r2_hardening/sf1a_review/evidence/"
RUN = NS2 + "code/p309_" + "qualify.py"
R5 = "level4/closure_proofs/p5y_k5_tail_c2_closure/evidence/coverage/K5_COVERAGE_MAP_R5.json"
PINNED = ["git", "mirror", "qc_formal", "qc_research_simple", "qhost_preflight", "research_test", "run",
          "start_qhost_monitor", "stop_qhost_monitor"]


def g(d, *a, check=True):
    return subprocess.run(["git", "-C", str(d), *a], capture_output=True, text=True, check=check).stdout.strip()


def gb(d, *a):
    return subprocess.run(["git", "-C", str(d), *a], capture_output=True, check=True).stdout


work.mkdir()
clone = work / "r2"
subprocess.run(["git", "clone", "-q", "--single-branch", "--branch", "claude/p5y-k5-cell309-p309-r2", "--no-tags", url,
                str(clone)], check=True)
head = g(clone, "rev-parse", "HEAD")
# the base commit is in the clone (an ancestor); read its runner from the clone, the reviewed bytes from the session repo
run_new = (clone / RUN).read_bytes()
run_old = gb(clone, "show", f"{OLD}:{RUN}")
run_reviewed = gb(repo, "show", f"{NEW}:{RUN}")
ast_ev = json.loads(gb(repo, "show", f"{hb}:{EVD}AST_RUNNER_b66a45f0_VS_716946e8.json"))
reg_ev = json.loads(gb(repo, "show", f"{hb}:{EVD}REG_716946e8.json"))
h = lambda b: hashlib.sha256(b).hexdigest()  # noqa: E731
to, tn = ast.parse(run_old), ast.parse(run_new)
DEF = (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)
do = {n.name: n for n in to.body if isinstance(n, DEF)}
dn = {n.name: n for n in tn.body if isinstance(n, DEF)}
changed = sorted(k for k in set(do) | set(dn) if k not in do or k not in dn or ast.dump(do[k]) != ast.dump(dn[k]))
src_o, src_n = run_old.decode(), run_new.decode()
pinned_bytes = {k: ast.get_source_segment(src_o, do[k]) == ast.get_source_segment(src_n, dn[k]) for k in PINNED}
mods_same = ([ast.dump(n) for n in to.body if not isinstance(n, DEF)] == [ast.dump(n) for n in tn.body if not isinstance(n, DEF)])
chain = g(clone, "rev-list", "--first-parent", "--max-count=5", "HEAD").split()
paths = g(clone, "diff", "--name-only", OLD, "HEAD").split()
ls_old = dict(l.split("\t")[::-1] for l in g(clone, "ls-tree", "-r", OLD, NS2).splitlines())
ls_new = dict(l.split("\t")[::-1] for l in g(clone, "ls-tree", "-r", "HEAD", NS2).splitlines())
others_same = {p for p in set(ls_old) | set(ls_new) if p != RUN and ls_old.get(p) != ls_new.get(p)}
groups = {}
for sub in ("code/", "config/", "fc2/", "tests/", "verify/", "governance/", "freeze/"):
    ks = [p for p in ls_new if p.startswith(NS2 + sub) and p != RUN]
    groups[sub] = {"files": len(ks), "all_identical_to_b66a45f0": all(ls_old.get(p) == ls_new[p] for p in ks)}
outside = [p for p in g(clone, "diff", "--name-only", "c902fe2fe33003ac7e4e61f29c10c81682fc940c", "HEAD").split()
           if not p.startswith(NS2)]
checks = {
    "HEAD is 716946e8 (no new commit)": head == NEW,
    "tree is the reviewed tree 3afb045c": g(clone, "rev-parse", "HEAD^{tree}") == TREE,
    "first-parent chain 716946e8 -> b66a45f0 -> a119e978 -> 93d55063 -> 101ef2cb":
        [c[:8] for c in chain] == ["716946e8", "b66a45f0", "a119e978", "93d55063", "101ef2cb"],
    "b66a45f0 is an ancestor of HEAD": subprocess.run(["git", "-C", str(clone), "merge-base", "--is-ancestor", OLD,
                                                       "HEAD"]).returncode == 0,
    "exactly the runner changed since b66a45f0": paths == [RUN],
    "runner bytes equal the reviewed commit's blob byte-for-byte": run_new == run_reviewed,
    "runner sha256 equals the AST evidence (540df055)": h(run_new) == ast_ev["new_sha256"] ==
        "540df0552bfc31512289e30eaf1ead57bf82a4ac806f38080439c05c43f9a3af",
    "runner sha256 equals the regression-bound runner": h(run_new) == reg_ev.get("runner_sha256"),
    "base runner equals the AST evidence's old bytes": h(run_old) == ast_ev["old_sha256"],
    "by AST only fs_probe differs (recomputed)": changed == ["fs_probe"],
    "module-level statements identical": mods_same,
    "the 9 pinned runner functions are byte-identical": all(pinned_bytes.values()) and len(pinned_bytes) == 9,
    "every other r2 file is the same blob as at b66a45f0": not others_same,
    "no path outside r2's namespace changed since c902fe2f (A7)": outside == [],
    "r1 tree is ecd1c359": g(clone, "rev-parse", "HEAD:level4/closure_proofs/p5y_k5_cell309_p309_r1") ==
        "ecd1c359ef0c3e0c9911b014b884376a10f6ed5b",
    "r5 unchanged": g(clone, "rev-parse", f"HEAD:{R5}") == "f978eeb6b41188eabaf3c6d590c9178d711f1ce6",
    "no r6": not [p for p in g(clone, "ls-tree", "-r", "--name-only", "HEAD").split()
                  if "COVERAGE_MAP_R6" in p or p.endswith("_R6.json")],
    "no freeze record": not (clone / NS2 / "ledger" / "FREEZE_RECORD.json").exists(),
    "no qualification directory": not (clone / NS2 / "qualification").exists(),
}
res = {"origin_url": url, "head": head, "tree": g(clone, "rev-parse", "HEAD^{tree}"), "first_parent_chain": chain,
       "paths_since_b66a45f0": paths, "runner_sha256": h(run_new), "base_runner_sha256": h(run_old),
       "ast_changed_definitions": changed, "pinned_functions_byte_identical": pinned_bytes,
       "r2_subtrees_other_than_runner": groups, "evidence_commit": hb, "checks": checks, "ok": all(checks.values())}
out.write_text(json.dumps(res, indent=1) + "\n")
print(json.dumps({"checks": checks, "groups": groups, "ok": res["ok"]}, indent=1))
sys.exit(0 if res["ok"] else 1)
