"""G7 - published artifacts equal a fresh generator run."""
import json, os, subprocess, sys, tempfile, shutil

def test_regenerating_reproduces_published_artifacts(root):
    files = ["CLAIM_LEDGER.json", "THEOREM_DEPENDENCY_GRAPH.json",
             "CLAIM_LEDGER.md", "THEOREM_DEPENDENCY_GRAPH.md"]
    before = {f: open(os.path.join(root, f), "rb").read() for f in files}
    env = dict(os.environ, P9_EMIT_MD="1", PYTHONDONTWRITEBYTECODE="1")
    r = subprocess.run([sys.executable, os.path.join(root, "experiments", "build_ledger.py")],
                       capture_output=True, text=True, env=env, cwd=root)
    assert r.returncode == 0, r.stderr
    for f in files:
        assert open(os.path.join(root, f), "rb").read() == before[f], f
