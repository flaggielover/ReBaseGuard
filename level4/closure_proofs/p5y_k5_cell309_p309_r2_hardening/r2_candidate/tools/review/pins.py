"""Independent reviewer helper: recompute AST pins; compare allowance leaves; function-level AST diff.
Reads blobs with git show only (read-only on the session repo)."""
import ast, hashlib, json, subprocess, sys

REPO = "/home/user/ReBaseGuard"
NS = "level4/closure_proofs/p5y_k5_cell309_p309_r2/"
OLD, NEW, HARD = "101ef2cb17e5eab2892212178278da45b98004ed", "93d550638b8c79ae1c252fc6c2b0194b1a416b49", "3c191ac2"
sys.path.insert(0, "/tmp/claude-0/-home-user-ReBaseGuard/ede4e097-f9ec-54f5-9e84-81294f8ad688/scratchpad/t3/review/cand/" + NS + "code")
import p309_scan as S  # noqa


def blob(rev, rel):
    r = subprocess.run(["git", "-C", REPO, "show", f"{rev}:{NS}{rel}"], capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else None


def owner_hash(src, qual):
    tree = ast.parse(src)
    hits = {id(o[1]): o[1] for o in S.owners(tree).values() if o is not None and o[0] == qual}
    return S.ast_sha(next(iter(hits.values()))) if len(hits) == 1 else None


def toplevel(src):
    tree = ast.parse(src)
    out = {}
    for n in tree.body:
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            out[n.name] = hashlib.sha256(ast.dump(n).encode()).hexdigest()
        elif isinstance(n, (ast.Assign, ast.AnnAssign)):
            tg = n.targets if isinstance(n, ast.Assign) else [n.target]
            for t in tg:
                for nm in ast.walk(t):
                    if isinstance(nm, ast.Name):
                        out["=" + nm.id] = hashlib.sha256(ast.dump(n).encode()).hexdigest()
        else:
            out.setdefault("#other", [])
    return out


def leaves(x, p=""):
    if isinstance(x, dict):
        for k, v in x.items():
            yield from leaves(v, f"{p}/{k}")
    elif isinstance(x, list):
        for i, v in enumerate(x):
            yield from leaves(v, f"{p}[{i}]")
    else:
        yield p, x


cfg_old = json.loads(blob(OLD, "config/SCANNER_ALLOWANCE_P309.json"))
cfg_new = json.loads(blob(NEW, "config/SCANNER_ALLOWANCE_P309.json"))
lo, ln = dict(leaves(cfg_old)), dict(leaves(cfg_new))
print("== allowance leaves: old", len(lo), "new", len(ln))
for k in sorted(set(lo) | set(ln)):
    if lo.get(k, "<absent>") != ln.get(k, "<absent>"):
        print("  DIFF", k, lo.get(k, "<absent>"), "->", ln.get(k, "<absent>"))

changed = ["code/p309_" + "qualify.py", "code/p309_" + "topology_drill.py"]
print("== every pinned entry whose file is a changed file (recomputed at NEW and OLD)")


def all_entries(cfg):
    for lst in ("ref_mutation_functions", "exactly_once_sites"):
        for r in cfg[lst]:
            yield lst, r["file"], r.get("function") or r.get("name"), r["ast_sha256"]
    for r in cfg["process_policy"]["reviewed_functions"]:
        yield "reviewed_functions", r["file"], r["function"], r["ast_sha256"]
    for r in cfg["backstop_pins"]:
        yield "backstop_pins", r["file"], r.get("name") or r.get("function"), r["ast_sha256"]
    for r in cfg["production_read_path_pins"]["entries"]:
        yield "production_read_path_pins", r["file"], r.get("name") or r.get("function"), r["ast_sha256"]
    for r in cfg["production_read_path_constant_pins"]["entries"]:
        yield "production_read_path_constant_pins", r["file"], r.get("name") or r.get("function"), r.get("ast_sha256") or r.get("sha256")
    for r in cfg.get("t7_exemptions", []):
        yield "t7_exemptions(module)", r["file"], "<module>", r.get("ast_sha256")
    for r in cfg.get("import_policy", {}).get("module_level_exemptions", []):
        yield "module_level_exemptions(module)", r["file"], "<module>", r.get("ast_sha256")


files_seen = set()
for lst, f, fn, pin in all_entries(cfg_new):
    files_seen.add(f)
    if f not in changed:
        continue
    srcn, srco = blob(NEW, f), blob(OLD, f)
    if fn == "<module>":
        hn, ho = S.ast_sha(ast.parse(srcn)), S.ast_sha(ast.parse(srco))
    else:
        hn, ho = owner_hash(srcn, fn), owner_hash(srco, fn)
    print(f"  {lst:34s} {f:28s} {fn:28s} pin={pin[:12]} new={str(hn)[:12]} old={str(ho)[:12]} "
          f"{'MATCH' if hn == pin else 'MISMATCH'} {'unchanged' if hn == ho else 'CHANGED'}")
print("== files in allowance:", sorted(files_seen))

for f in changed:
    o, n, h = toplevel(blob(OLD, f)), toplevel(blob(NEW, f)), toplevel(blob(HARD, f) or "")
    print("== top-level AST diff", f)
    for k in sorted(set(o) | set(n)):
        if o.get(k) != n.get(k):
            print("  ", k, "added" if k not in o else "removed" if k not in n else "changed")
    if f.endswith("qualify.py"):
        print("  NEW vs 3c191ac2 module AST equal:", S.ast_sha(ast.parse(blob(NEW, f))) == S.ast_sha(ast.parse(blob(HARD, f))))
        print("  NEW vs 3c191ac2 bytes equal:", blob(NEW, f) == blob(HARD, f))
        for k in sorted(set(h) | set(n)):
            if h.get(k) != n.get(k):
                print("   vs-hard", k)
