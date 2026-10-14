"""For selected committed mutants (tests/run_mutants.py), list which tests fail. Scratch copies only."""
import os, subprocess, sys, tempfile, json
from pathlib import Path
T = Path("/home/user/ReBaseGuard/level4/closure_proofs/p5y_k5_cell308_research/streams/CLOUD_R1_LINUX_DEV/tests")
sys.path.insert(0, str(T))
import run_mutants as RM
src = (Path(__file__).parent / "base" / "lx_platform.py").read_text()
want = sys.argv[1:]
out = {}
for mid, what, edits in RM.MUTANTS:
    if mid not in want: continue
    m = src
    for o, n in edits: m = m.replace(o, n)
    with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as d:
        Path(d, "lx_platform.py").write_text(m)
        p = subprocess.run([sys.executable, "-B", "-m", "unittest", "discover", "-s", str(T)], cwd=T.parent,
                           env=dict(os.environ, LX_PLATFORM_DIR=d, PYTHONDONTWRITEBYTECODE="1"), capture_output=True, text=True)
    out[mid] = [l for l in p.stderr.splitlines() if l.startswith(("FAIL:", "ERROR:"))]
print(json.dumps(out, indent=1))
