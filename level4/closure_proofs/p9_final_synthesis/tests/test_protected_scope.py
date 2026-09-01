"""G11/G12 - P1-P8 historical artifacts unchanged BY P9.

The P9 worktree was fast-forwarded onto authoritative main after the P8
adjudication landed, so the anchor manifest may legitimately deviate for files
touched by that authoritative integration - and ONLY for those. Anything else
would be a P9 write outside its namespace.
"""
import hashlib, json, os, subprocess

ANCHOR = "ffe23a63181e2ff11380768d3c73980de80f94fb"
NS = "level4/closure_proofs/p9_final_synthesis"

def repo_root(root): return os.path.dirname(os.path.dirname(os.path.dirname(root)))

def manifest(root):
    return json.load(open(os.path.join(root, "results",
                                       "protected_tree_manifest_pre.json")))

def test_manifest_is_substantial(root):
    man = manifest(root)
    assert man["n_files"] > 2000
    assert man["anchor_commit"] == ANCHOR

def test_deviations_are_only_authoritative_integration(root):
    man, repo = manifest(root), repo_root(root)
    deviated = []
    for rel, want in man["files"].items():
        p = os.path.join(repo, rel)
        if not os.path.exists(p) or \
           hashlib.sha256(open(p, "rb").read()).hexdigest() != want:
            deviated.append(rel)
    # files the authoritative commit range legitimately touched
    out = subprocess.run(["git", "diff", "--name-only", ANCHOR, "HEAD"],
                         cwd=repo, capture_output=True, text=True)
    assert out.returncode == 0, out.stderr
    authorised = set(out.stdout.split())
    unexplained = [f for f in deviated if f not in authorised]
    assert not unexplained, f"P9 modified protected files: {unexplained}"

def test_p9_wrote_only_inside_its_namespace(root):
    repo = repo_root(root)
    out = subprocess.run(["git", "status", "--porcelain"],
                         cwd=repo, capture_output=True, text=True)
    assert out.returncode == 0, out.stderr
    for line in out.stdout.splitlines():
        path = line[3:].strip().strip('"')
        assert path.startswith(NS), f"P9 touched {path} outside its namespace"

def test_no_tracked_file_is_modified(root):
    repo = repo_root(root)
    out = subprocess.run(["git", "diff", "--name-only", "HEAD"],
                         cwd=repo, capture_output=True, text=True)
    assert out.returncode == 0, out.stderr
    assert not out.stdout.strip(), f"tracked files modified: {out.stdout}"
