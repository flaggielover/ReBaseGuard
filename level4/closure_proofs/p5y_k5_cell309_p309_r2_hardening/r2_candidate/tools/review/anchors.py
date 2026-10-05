"""Reviewer helper: count every MUTANTS anchor of tests/test_p309_static_controls.py in the files of a given commit
(read with git show from the session repo), without running the test.  The MUTANTS list is taken from the test
module's AST: module-level string constants are evaluated with ast.literal_eval in a tiny namespace."""
import ast, subprocess, sys

REPO = "/home/user/ReBaseGuard"
NS = "level4/closure_proofs/p5y_k5_cell309_p309_r2/"


def show(rev, rel):
    r = subprocess.run(["git", "-C", REPO, "show", f"{rev}:{NS}{rel}"], capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else ""


def mutants(rev):
    tree = ast.parse(show(rev, "tests/test_p309_static_controls.py"))
    env = {}

    def ev(node):
        if isinstance(node, ast.Name):
            return env[node.id]
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
            return ev(node.left) + ev(node.right)
        if isinstance(node, ast.Tuple):
            return tuple(ev(e) for e in node.elts)
        if isinstance(node, ast.List):
            return [ev(e) for e in node.elts]
        return ast.literal_eval(node)

    for n in tree.body:
        if isinstance(n, ast.Assign) and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name):
            try:
                env[n.targets[0].id] = ev(n.value)
            except Exception:
                pass
    return env["MUTANTS"]


for rev in sys.argv[1:]:
    print("==", rev)
    for name, check, rel, old, new in mutants(rev):
        c = show(rev, rel).count(old)
        print(f"  {name:48s} {rel:34s} anchor_count={c} {'OK' if c == 1 else 'FAIL'}")
