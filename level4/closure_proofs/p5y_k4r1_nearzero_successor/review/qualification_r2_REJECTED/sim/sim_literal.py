"""Literal GATE.execution command, run from (a) repo root and (b) namespace dir, output dir PRE-CREATED; SYNTHETIC sources."""
import importlib.util, os, subprocess, sys, shutil
from pathlib import Path
S = Path(sys.argv[1])
NSC = S / "ns/level4/closure_proofs/p5y_k4r1_nearzero_successor"
os.environ["K4R1_CODE_PATH"] = str(NSC / "code/k4r1_certificate.py")
spec = importlib.util.spec_from_file_location("t", NSC / "tests/test_k4r1.py"); T = importlib.util.module_from_spec(spec); spec.loader.exec_module(T)
for where in ("repo_root", "namespace_dir"):
    tmp = S / "sim" / ("literal_" + where)
    if tmp.exists(): shutil.rmtree(tmp)
    tmp.mkdir()
    repo, ns, mod = T.build_repo(tmp)       # pre-creates evidence/execution_r1
    cwd = repo if where == "repo_root" else ns
    cmd = [sys.executable, "code/k4r1_certificate.py", "execute", "--out",
           "level4/closure_proofs/p5y_k4r1_nearzero_successor/evidence/execution_r1/K4R1_RESULT.json"]
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
    print(where, "rc", r.returncode, "| stderr tail:", r.stderr.strip().splitlines()[-1] if r.stderr.strip() else "", "| stdout:", r.stdout.strip())
