"""Synthetic simulation of the planned freeze+execute flow (CLI, relative --out from repo root), SYNTHETIC sources only."""
import importlib.util, json, os, subprocess, sys, shutil
from pathlib import Path
S = Path(sys.argv[1]); case = sys.argv[2]
NSC = S / "ns/level4/closure_proofs/p5y_k4r1_nearzero_successor"
os.environ["K4R1_CODE_PATH"] = str(NSC / "code/k4r1_certificate.py")
spec = importlib.util.spec_from_file_location("t", NSC / "tests/test_k4r1.py"); T = importlib.util.module_from_spec(spec); spec.loader.exec_module(T)
tmp = S / "sim" / case
if tmp.exists(): shutil.rmtree(tmp)
tmp.mkdir()
repo, ns, mod = T.build_repo(tmp)
# planned flow: evidence/execution_r1 must not pre-exist (build_repo pre-creates it as an untracked empty dir)
if case != "dir_precreated":
    (ns / "evidence/execution_r1").rmdir()
print("git status porcelain:", repr(subprocess.run(["git","-C",str(repo),"status","--porcelain"],capture_output=True,text=True).stdout))
out_rel = str(T.NSREL / "evidence/execution_r1/K4R1_RESULT.json")
r = subprocess.run([sys.executable, str(T.NSREL / "code/k4r1_certificate.py"), "execute", "--out", out_rel], cwd=repo,
                   capture_output=True, text=True, env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
print("rc", r.returncode); print("stdout", r.stdout[-400:]); print("stderr", r.stderr[-600:])
print("output exists:", (repo / out_rel).exists())
