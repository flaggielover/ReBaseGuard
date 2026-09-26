# DECOY-ONLY probe: sandbox B built exactly as the frozen verifier builds it (freeze commit + synthetic I2 decoys),
# identity pointed at the sandbox in-process, as the verifier's X flows do. Never touches the real repository.
import importlib.util, json, os, subprocess, sys, traceback
from pathlib import Path
SCR = Path(sys.argv[1]).resolve()
V_PATH = "/Users/suzhe/ReBaseGuard-k5c11rd/level4/closure_proofs/p5y_k5_tail_c12r1_cell306_adoption/code/c12r1_verify.py"
spec = importlib.util.spec_from_file_location("v_probe", V_PATH); V = importlib.util.module_from_spec(spec); spec.loader.exec_module(V)
D0 = V.load_driver("c12r1_pre")
fz = D0.freeze_commit()
assert fz.startswith("5cfe336a"), fz
root = SCR / "sbx"; root.mkdir(parents=True, exist_ok=True)
sb, pins, blobs = V.make_decoy_sandbox(root, fz)
assert all(json.loads(sb.p(r).read_text()).get("DECOY") is True for r in (V.C11R_CMP, V.C11RD_CMP, V.C11RD_RUNS))
drv_sha = V.sha_b(V.DRIVER.read_bytes())

def fresh(tag):
    sb.reset(); V.build_state(sb, "G", drv_sha)
    D = V.load_driver("probe_" + tag)
    D.REPO = sb.root; D.QUALIFIED_WORKTREE = str(sb.root)
    D.QUALIFIED_GIT_DIR = D.QUALIFIED_COMMON_DIR = str((sb.root / ".git").resolve())
    D.QUALIFIED_BRANCH = "refs/heads/campaign"
    D.PINS = {**D.PINS, **pins}; D.BLOBS = {**D.BLOBS, **blobs}
    calls = {"evaluate": 0}
    orig = D.evaluate_target
    def ev(con, p):
        calls["evaluate"] += 1
        return orig(con, p)
    return D, calls, ev

def state(D):
    res = sb.p(D.RESULT_REL)
    return {"marker": bool(sb.g("for-each-ref", "refs/c12r1").stdout.strip()),
            "result_is_symlink": res.is_symlink(), "result_exists": res.exists() or res.is_symlink(),
            "result_in_HEAD": sb.g("ls-tree", "HEAD", "--", D.RESULT_REL).stdout.split()[:1],
            "status_porcelain": sb.g("status", "--porcelain", "--untracked-files=all").stdout.splitlines()}

out = {}
# (a) an IGNORED directory planted at the result's temp path (*.tmp is gitignored, so check_clean cannot see it)
D, calls, ev = fresh("a")
tmpp = sb.p(D.RESULT_REL).with_suffix(".tmp"); tmpp.mkdir(parents=True)
pre_status = sb.g("status", "--porcelain", "--untracked-files=all").stdout
try:
    rc = D.run_execute(drv_sha, None, ev); err = None
except BaseException as e:
    rc, err = None, f"{type(e).__name__}"
st = state(D)
try:
    so = D.run_seal_only(); so_err = None
except D.Refusal as e:
    so, so_err = None, e.code
out["a_ignored_dir_at_tmp"] = {"status_before_execute_was_clean": pre_status == "", "rc": rc, "uncaught": err,
                               "decoy_evaluations": calls["evaluate"], **st, "seal_only_rc": so, "seal_only_refusal": so_err}
# (b) an IGNORED symlink planted at the temp path, pointing outside the repository
D, calls, ev = fresh("b")
outside = SCR / "outside_sink.json"
if outside.exists(): outside.unlink()
tmpp = sb.p(D.RESULT_REL).with_suffix(".tmp"); tmpp.parent.mkdir(parents=True, exist_ok=True)
os.symlink(outside, tmpp)
pre_status = sb.g("status", "--porcelain", "--untracked-files=all").stdout
try:
    rc = D.run_execute(drv_sha, None, ev); err = None
except BaseException as e:
    rc, err = None, f"{type(e).__name__}"
st = state(D)
mode = sb.g("ls-tree", "HEAD", "--", D.RESULT_REL).stdout.split()[:1]
sink = json.loads(outside.read_text()) if outside.exists() else {}
out["b_ignored_symlink_at_tmp"] = {"status_before_execute_was_clean": pre_status == "", "rc": rc, "uncaught": err,
                                   "decoy_evaluations": calls["evaluate"], **st, "sealed_entry_mode": mode,
                                   "outside_file_has_full_result": sink.get("status") == "TARGET_EVALUATED" and "target" in sink}
sb.reset()
print(json.dumps(out, indent=1))
