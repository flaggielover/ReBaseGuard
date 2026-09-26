"""C11RD-R1Q-R1 -- the repaired qualification of the C11RD-R1 freeze ce5b8595 (governance addition outside the
frozen scientific object; code/ and every frozen hash are untouched). SUCCESSOR of the rejected qualification
3addf9d3 (qualification_r1/, review 89330534: QUALIFICATION_REJECTED, blocker B-1); those files are
historical and are not modified.

What it does NOT do: compute anything at a cell 306-309 drift (science runs only on the non-target block
[5/2, 3233337/1250000] or on synthetic candidates); run the runner in --mode real; run the comparator's
main; create a grant, a consumed ref or a commit in the real repository (grants, consumed refs and seals
are created ONLY in scratch repositories, with a STUB runner).

    python3 -I -S -B c11rd_qualify.py --out-dir DIR [--write-artifact]
    python3 -I -S -B c11rd_qualify.py --post-write-scan FILE

Writes DIR/C11RD_R1Q_R1_QUALIFICATION_CHECKS.json (every check with its evidence), DIR/validation/ (the
frozen suite's output) and, with --write-artifact, DIR/C11RD_R1Q_R1_QUALIFICATION.json. The leak scans
need the two disclosed original values on stdin (two lines); the tool contains no original value and
writes none (its controls are planted in a temporary directory outside the repository).
"""
import argparse
import ast
import hashlib
import importlib.util
import json
import os
import pathlib
import platform
import random
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from fractions import Fraction as F

HERE = pathlib.Path(__file__).resolve().parent
NS = HERE.parents[1]
REPO = NS.parents[2]
NS_REL = "level4/closure_proofs/p5y_k5_tail_c11rd_d1d2_extension"
CODE = NS / "code"
PRIMARY = pathlib.Path("/Users/suzhe/ReBaseGuard")
FREEZE_COMMIT = "ce5b85959a1693525f9e001e7c191516a4ee7d76"
PRED_FREEZE_COMMIT = "71495747504670dbe90ec0ee2f7dd4702fd47001"
REVIEW_COMMIT = "3c1eff11562638727156f09a9c58b8dc704548a5"
REVIEW_REL = "review/C11RD_R1_PRE_EXECUTION_REVIEW.md"
REVIEW_SHA256 = "dd4ccbda22a4c2fde0c40831202d30850b08a88e023bef04326bcccc48914867"
REJECTED_QUAL_COMMIT = "3addf9d3c72d9274813fb5e06486b633a50a133c"
REJECTION_REVIEW_COMMIT = "8933053406b33cb4cc852dfd5b2231f507a552b3"
REJECTION_REVIEW_REL = "review/C11RD_R1_QUALIFICATION_REVIEW.md"
REJECTION_REVIEW_SHA256 = "d95a2cb62497b7a19aefe1cfd90c23e80230651d9d7aeacc54becf75365baf90"
REJECTED_ARTIFACT_REL = "evidence/qualification_r1/C11RD_R1_QUALIFICATION.json"
REJECTED_LAUNCHER_REL = "qualification_r1/code/c11rd_launch.py"
REJECTED_LAUNCHER_SHA256 = "6771447201b06e98883a90eee813e874fd1ddb139dab111ba6d657e4a4f48dbe"
C11R_FINAL = "7375b9cdb1d770ba836335164f205e26b445035e"
LOCAL_MAIN_REF = "c123b9bb8f15d17650545b3fce4aca8a6b61093b"
REMOTE_MAIN_REF = "1cb453826313c189f0bdafd5b84120c1edb74da9"
R5_REL = "level4/closure_proofs/p5y_k5_tail_c2_closure/evidence/coverage/K5_COVERAGE_MAP_R5.json"
C11R_NS = "level4/closure_proofs/p5y_k5_tail_c11r_n9_statement_alignment"
HISTORICAL_R1_QUAL_PATHS = ("qualification_r1/", "evidence/qualification_r1/", "docs/C11RD_R1_QUALIFICATION.md",
                            "review/C11RD_R1_QUALIFICATION_REVIEW.md")
QUAL_PATHS = ("qualification_r1q_r1/", "evidence/qualification_r1q_r1/", "docs/C11RD_R1Q_R1_QUALIFICATION.md",
              "review/C11RD_R1Q_R1_QUALIFICATION_REVIEW.md")
FORBIDDEN_LIFECYCLE_PATHS = ("evidence/runs", "evidence/comparison", "config", "review/C11RD_EXECUTION_REVIEW.md",
                             "review/C11RD_AUTHORIZATION_REVIEW.md")
NT = (F(5, 2), F(5, 2) + F(108337, 1250000))
LAUNCH_BRANCH = "refs/heads/p5y-k5-tail-c11rd-d1d2-extension"
# launch-time governance limits (NOT scientific parameters; the frozen caps are unchanged): an idle host
# (1-min load <= 2.0 on 6 cores), 2 GiB free disk, 1 GiB available memory = about 5x the largest process-tree
# RSS observed in the frozen runner's rehearsals (about 210 MB), mains power and an open lid (review QR1.N-10)
LAUNCH_LIMITS = {"load1_max": 2.0, "disk_free_min_bytes": 2 * 1024 ** 3, "memory_available_min_kb": 1048576,
                 "require_ac_power": True, "require_lid_open": True}
SANDBOX_LIMITS = {"load1_max": 1000.0, "disk_free_min_bytes": 0, "memory_available_min_kb": 0,
                  "require_ac_power": False, "require_lid_open": False}
SANDBOX_BRANCH = "refs/heads/launch-branch"
FAST_DELAYS = [0.3, 0.3, 0.3, 0.3, 0.3, 0.3]

sys.path.insert(0, str(CODE))
sys.path.insert(0, str(HERE))
import c11rd_runs as RN            # noqa: E402  (its pre-import barrier runs: -I -S -B required)
import c11rd_model as MD           # noqa: E402
import c11rd_certify as CE         # noqa: E402
import c11rd_compare as CM         # noqa: E402
import c11rd_kernel as KR          # noqa: E402
import c11rd_float as FL           # noqa: E402
import c11rd_validate as V         # noqa: E402
import c11rd_launch as LA          # noqa: E402  (the repaired launcher, qualification_r1q_r1/code)

SAFE_GIT_ENV = dict(LA.SAFE_ENV)
LAUNCHER = HERE / "c11rd_launch.py"
REJECTED_LAUNCHER = NS / REJECTED_LAUNCHER_REL
RUNTIME = {}                       # the interpreter runtime binding, computed in Q06 and used by every sandbox


def G(repo, *args, text=True, env=None):
    """Governance git: absolute binary, explicit sanitized environment (the launcher's), replace refs
    ignored, commit-graph not trusted."""
    return subprocess.run(["/usr/bin/git", "--no-replace-objects", "-c", "core.commitGraph=false", "-C", str(repo), *args],
                          capture_output=True, text=text, env=env or SAFE_GIT_ENV)


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def sha256_file(p) -> str:
    return sha256_bytes(pathlib.Path(p).read_bytes())


def check(fn):
    fn.is_check = True
    return fn


def _freeze():
    return json.loads((NS / "protocol/C11RD_FREEZE_R1.json").read_text())


# =====================================================================================================
# Q01 entry identity (the rejected lineage is intact; only this round's paths changed since it)
# =====================================================================================================
@check
def q01_entry_identity():
    out = {}
    anc = lambda c: G(REPO, "merge-base", "--is-ancestor", c, "HEAD").returncode == 0
    out["freeze_commit_exists_and_ancestor"] = G(REPO, "cat-file", "-e", f"{FREEZE_COMMIT}^{{commit}}").returncode == 0 and anc(FREEZE_COMMIT)
    fj = G(REPO, "show", f"{FREEZE_COMMIT}:{NS_REL}/protocol/C11RD_FREEZE_R1.json", text=False).stdout
    fm = G(REPO, "show", f"{FREEZE_COMMIT}:{NS_REL}/protocol/C11RD_FREEZE_R1.md", text=False).stdout
    out["freeze_files_unchanged_on_disk"] = fj == (NS / "protocol/C11RD_FREEZE_R1.json").read_bytes() and \
        fm == (NS / "protocol/C11RD_FREEZE_R1.md").read_bytes()
    out["frozen_object_untouched_since_freeze (code, protocol, theory)"] = G(
        REPO, "diff", "--name-only", FREEZE_COMMIT, "HEAD", "--", f"{NS_REL}/code", f"{NS_REL}/protocol", f"{NS_REL}/theory").stdout.strip() == "" \
        and G(REPO, "status", "--porcelain", "--", f"{NS_REL}/code", f"{NS_REL}/protocol", f"{NS_REL}/theory").stdout.strip() == ""
    rv = G(REPO, "show", f"{REVIEW_COMMIT}:{NS_REL}/{REVIEW_REL}", text=False).stdout
    out["R1_review_commit_ancestor"] = anc(REVIEW_COMMIT)
    out["R1_review_sha256_unchanged"] = sha256_bytes(rv) == REVIEW_SHA256 == sha256_file(NS / REVIEW_REL)
    out["R1_review_verdict_exactly_READY_TO_QUALIFY"] = [ln.strip() for ln in rv.decode().splitlines()
                                                         if ln.strip() in ("READY_TO_QUALIFY", "NOT_READY")] == ["READY_TO_QUALIFY"]
    out["rejected_qualification_commit_ancestor"] = anc(REJECTED_QUAL_COMMIT)
    out["rejection_review_commit_ancestor"] = anc(REJECTION_REVIEW_COMMIT)
    rr = G(REPO, "show", f"{REJECTION_REVIEW_COMMIT}:{NS_REL}/{REJECTION_REVIEW_REL}", text=False).stdout
    out["rejection_review_byte_identical (sha256 d95a2cb6...)"] = sha256_bytes(rr) == REJECTION_REVIEW_SHA256 == \
        sha256_file(NS / REJECTION_REVIEW_REL)
    verdicts = [ln.strip() for ln in rr.decode().splitlines() if ln.strip() in ("QUALIFICATION_ACCEPTED", "QUALIFICATION_REJECTED")]
    out["rejection_review_verdict_exactly_QUALIFICATION_REJECTED"] = verdicts == ["QUALIFICATION_REJECTED"]
    hist = [f"{NS_REL}/{p}" for p in HISTORICAL_R1_QUAL_PATHS]
    out["historical_R1Q_files_unchanged_since_their_commits"] = \
        G(REPO, "diff", "--name-only", REJECTION_REVIEW_COMMIT, "HEAD", "--", *hist).stdout.strip() == "" and \
        G(REPO, "status", "--porcelain", "--untracked-files=all", "--", *hist).stdout.strip() == "" and \
        sha256_file(REJECTED_LAUNCHER) == REJECTED_LAUNCHER_SHA256
    later = G(REPO, "diff", "--name-only", REJECTION_REVIEW_COMMIT, "HEAD", "--", NS_REL).stdout.split()
    pending = [ln[3:] for ln in G(REPO, "status", "--porcelain", "--untracked-files=all", "--", NS_REL).stdout.splitlines()]
    extra = [p for p in later + pending if not any(p.startswith(f"{NS_REL}/{q}") for q in QUAL_PATHS)]
    out["since_the_rejection_only_this_rounds_paths_changed"] = extra == []
    out["nothing_outside_the_namespace_changed_since_the_rejection"] = [
        p for p in G(REPO, "diff", "--name-only", REJECTION_REVIEW_COMMIT, "HEAD").stdout.split() if not p.startswith(NS_REL + "/")] == []
    out["branch"] = G(REPO, "branch", "--show-current").stdout.strip() == "p5y-k5-tail-c11rd-d1d2-extension"
    return {"pass": all(out.values()), "checks": out, "HEAD": G(REPO, "rev-parse", "HEAD").stdout.strip(),
            "unexpected_changes": extra}


# =====================================================================================================
# Q02 history / historical cleanliness
# =====================================================================================================
@check
def q02_history_cleanliness():
    out = {}
    paths = [f"{NS_REL}/{p}" for p in FORBIDDEN_LIFECYCLE_PATHS]
    own = G(REPO, "rev-list", "--all", "--reflog", "--full-history", "--", *paths)
    out["no_run_lock_seal_comparison_grant_authorization_in_any_history (qualification reader)"] = \
        own.returncode == 0 and own.stdout.strip() == ""
    try:
        out["same, by the frozen reader c11rd_model.history_commits"] = MD.history_commits(paths) == []
    except MD.ModelError:
        out["same, by the frozen reader c11rd_model.history_commits"] = False
    out["none_on_disk"] = not any((NS / p).exists() for p in FORBIDDEN_LIFECYCLE_PATHS)
    new_review = f"{NS_REL}/review/C11RD_R1Q_R1_QUALIFICATION_REVIEW.md"
    out["this_rounds_review_not_yet_written"] = not (REPO / new_review).exists() and \
        G(REPO, "rev-list", "--all", "--reflog", "--full-history", "--", new_review).stdout.strip() == ""
    out["no_refs_c11rd"] = G(REPO, "for-each-ref", "refs/c11rd").stdout.strip() == ""
    common = pathlib.Path(G(REPO, "rev-parse", "--path-format=absolute", "--git-common-dir").stdout.strip())
    out["no_launcher_log_dir_in_the_common_dir"] = not (common / LA.LOG_DIR_NAME).exists()
    out["repository_not_shallow"] = G(REPO, "rev-parse", "--is-shallow-repository").stdout.strip() == "false"
    out["no_grafts_or_shallow_file"] = not (common / "info/grafts").exists() and not (common / "shallow").exists()
    out["no_replace_refs"] = G(REPO, "for-each-ref", "refs/replace").stdout.strip() == ""
    out["C11R_namespace_byte_identical_since_7375b9cd"] = G(REPO, "diff", "--name-only", C11R_FINAL, "HEAD", "--",
                                                          C11R_NS).stdout.strip() == ""
    outside = [p for p in G(REPO, "diff", "--name-only", C11R_FINAL, "HEAD").stdout.split() if not p.startswith(NS_REL + "/")]
    out["nothing_outside_the_namespace_changed_since_7375b9cd"] = outside == []
    out["r5_unchanged"] = G(REPO, "rev-parse", f"HEAD:{R5_REL}").stdout.strip() == G(REPO, "rev-parse", f"{C11R_FINAL}:{R5_REL}").stdout.strip()
    out["no_r6_file"] = not any(re.search(r"coverage_map_r6", p, re.I) for p in G(REPO, "ls-tree", "-r", "--name-only", "HEAD").stdout.split())
    out["LOCAL_MAIN_REF"] = G(PRIMARY, "rev-parse", "main").stdout.strip() == LOCAL_MAIN_REF
    out["REMOTE_MAIN_REF (cached origin/main)"] = G(PRIMARY, "rev-parse", "origin/main").stdout.strip() == REMOTE_MAIN_REF
    return {"pass": all(out.values()), "checks": out, "outside_changes": outside}


# =====================================================================================================
# Q03 the frozen scientific object
# =====================================================================================================
@check
def q03_scientific_object():
    fz = _freeze()
    P, lo_hi = fz["frozen_parameters"], MD.cell_block()
    out = {}
    out["target_cell_306_only"] = fz["target"] == {"cell": 306, "drift_block": ["680769/400000", "17885921/10000000"]} \
        and [str(x) for x in lo_hi] == fz["target"]["drift_block"] and fz["Q_target"] == "cell 306 only"
    out["drift_interval_exact"] = lo_hi == (F(680769, 400000), F(17885921, 10000000))
    subs = CE.sub_blocks(lo_hi[0], lo_hi[1], P["sub_blocks"])
    out["four_sub_blocks_exact_tiling"] = P["sub_blocks"] == 4 and \
        fz["D_sub_block_partition"]["sub_blocks"] == [[str(a), str(b)] for a, b in subs] and \
        subs[0][0] == lo_hi[0] and subs[-1][1] == lo_hi[1] and all(subs[i][1] == subs[i + 1][0] for i in range(3))
    nt_boxes = CE.initial_boxes(NT[0], NT[1], P["splits"], P["tm_order"])
    out["168_initial_boxes"] = len(nt_boxes) == 168 == fz["E_state_domain_partition"]["initial_boxes"]["count"]
    out["refinement_rule"] = P["tolerances"] == ["1/100000", "1/20000", "1/2000"] and P["max_depth"] == 2 and \
        P["splits"] == {"s": 4, "theta": [4, 8, 12, 16], "s4": 4}
    out["taylor_order_6"] = P["tm_order"] == 6
    out["moment_terms_34"] = P["moment_terms"] == 34
    out["float_proposal_frozen"] = P["float"] == {"n": 8, "n4": 8, "ns": 11, "nt": 11, "q": 20, "bits": 52}
    Frec = fz["F_derivative_recurrence"]
    out["derivative_recurrence_text"] = Frec["chain"] == ["d = Khat d + h_1", "d' = Khat d' + Khat' d + h_1'",
                                                          "d'' = Khat d'' + 2 Khat' d' + Khat'' d + h_1''"]
    out["D1_formula_text"] = Frec["propagation"]["D1_j"] == "|D1(a)| + |D2(a)| de + |D3(a)| de^2/2 + tau (lam1 + kappa_1 n0)"
    out["D2_formula_text"] = Frec["propagation"]["D2_j"] == "|D2(a)| + |D3(a)| de + tau (lam2 + 2 kappa_1 n1 + kappa_2 n0)"
    rnd = random.Random(306)
    ok = True
    for _ in range(50):
        lam = [F(rnd.randint(1, 10 ** 6), 10 ** rnd.randint(6, 12)) for _ in range(3)]
        CT, tau = F(rnd.randint(1, 10 ** 4), 10 ** 3), F(rnd.randint(1, 10 ** 4), 10 ** 3)
        kap = {1: F(rnd.randint(1, 999), 1000), 2: F(rnd.randint(1, 999), 1000)}
        pr = CE.propagate(lam, CT, tau, kap)
        n0 = CT * lam[0]
        n1 = CT * (lam[1] + kap[1] * n0)
        ok &= pr == {"n0": n0, "n1": n1, "err_D1": tau * (lam[1] + kap[1] * n0),
                     "err_D2": tau * (lam[2] + 2 * kap[1] * n1 + kap[2] * n0)}
        a = [F(rnd.randint(-10 ** 6, 10 ** 6), 10 ** 6) for _ in range(4)]
        de = F(rnd.randint(1, 10 ** 4), 10 ** 6)
        cands = [{0: {(0, 0): a[j]}} for j in range(4)]
        av = CE.atom_values(cands, de)
        ok &= av[1] == abs(a[1]) + abs(a[2]) * de + abs(a[3]) / 2 * de ** 2 and av[2] == abs(a[2]) + abs(a[3]) * de
    out["propagation_and_atom_formulas_exact (50 random rational instances)"] = ok
    src = (CODE / "c11rd_runs.py").read_text()
    fn = next(n for n in ast.parse(src).body if isinstance(n, ast.FunctionDef) and n.name == "certify_block")
    maxcalls = [n for n in ast.walk(fn) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == "max"]
    out["maximum_aggregation (certify_block uses max for D1 and D2; no min)"] = len(maxcalls) == 2 and \
        not any(isinstance(n, ast.Name) and n.id == "min" for n in ast.walk(fn))
    table = MD._load_bound(MD.STATEMENT_TABLE_REL, MD.STATEMENT_TABLE_BLOB)
    out["factor_2_rule"] = CM.FACTOR == 2 and MD.comparison_rule(table)["factor"] == 2 and \
        CM.classify_numeric("UPPER_BOUND", F(3), F(2)) == "AGREES" and CM.classify_numeric("UPPER_BOUND", F(5), F(2)) == "INSUFFICIENT"
    out["one_execution_policy (freeze P = 1; runner grant check; permanent exclusive lock; launcher consumed ref)"] = \
        fz["P_execution_count"] == 1 and 'g.get("max_executions") != 1' in src and "os.O_EXCL" in src and \
        LA.CONSUMED_REF == "refs/c11rd/r1-execution-consumed"
    out["caps_43200_2GiB_5_workers"] = fz["resource_caps"] == {"workers": 5, "wall_seconds": 43200, "rss_kb": 2097152}
    bo = fz["E_state_domain_partition"]["band_ownership"]
    pts = {(F(0), F(0)): 0, (F(1, 2), F(1, 2)): 0, (F(1), F(0)): 0, (F(1), F(1)): 1, (F(3, 2), F(3, 2)): 2,
           (F(2), F(2)): 3, (F(4), F(0)): 3, (F(0), F(9, 2)): 4, (F(5), F(0)): 4, (F(1, 3), F(1, 2)): 0}
    out["upper_closed_band_convention (freeze + production owner_band)"] = bo["convention"].startswith("UPPER-CLOSED") and \
        all(CE.owner_band(p, m) == k for (p, m), k in pts.items())
    out["cover_complete_for_the_convention"] = CE.verify_cover(nt_boxes) == []
    out["original_value_quarantine_bound"] = CM.QUARANTINE_BLOB == "219e0122a7febf4347ce9205e5e5ed9f18b20ffb" == \
        fz["input_bindings"]["comparison_only_c11r_quarantine"]["blob"] and \
        G(REPO, "rev-parse", f"HEAD:{CM.QUARANTINE_REL}").stdout.strip() == CM.QUARANTINE_BLOB
    cm = next(n for n in ast.parse((CODE / "c11rd_compare.py").read_text()).body if isinstance(n, ast.FunctionDef) and n.name == "main")
    order = {}
    for n in ast.walk(cm):
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name):
            order.setdefault(n.func.id, n.lineno)
        if isinstance(n, ast.Name) and n.id == "QUARANTINE_REL":
            order.setdefault("QUARANTINE_REL", n.lineno)
    out["quarantine_read_only_after_run_once_seal_and_recompute"] = \
        order["run_once_problems"] < order["verify_seal"] < order["recompute"] < order["QUARANTINE_REL"]
    out["scientific_identity_vs_71495747 (V29)"] = V.v29_scientific_identity()["pass"]
    return {"pass": all(out.values()), "checks": out}


# =====================================================================================================
# Q04 hashes
# =====================================================================================================
@check
def q04_hashes():
    fz = _freeze()
    out = {}
    disk = {f"code/{f.name}": sha256_file(f) for f in sorted(CODE.glob("c11rd_*.py"))}
    out["frozen_code_sha256_equal"] = disk == fz["code_sha256"] and len(disk) == 8
    out["code_dir_exactly_the_frozen_files"] = {f.name for f in CODE.iterdir()} == {k.split("/")[1] for k in fz["code_sha256"]}
    c7 = fz["input_bindings"]["c7_gaussian"]
    out["c7_sha256_and_blob"] = sha256_file(REPO / c7["path"]) == c7["sha256"] and \
        G(REPO, "rev-parse", f"HEAD:{c7['path']}").stdout.strip() == c7["blob"]
    blobs = {name: G(REPO, "rev-parse", f"HEAD:{b['path']}").stdout.strip() == b["blob"]
             for name, b in fz["input_bindings"].items() if "blob" in b}
    out["all_input_blobs_equal"] = all(blobs.values()) and len(blobs) == 8
    docs = {rel: sha256_file(NS / rel) == h for rel, h in fz["document_sha256"].items()}
    out["frozen_document_hashes_equal"] = all(docs.values()) and len(docs) == 8
    return {"pass": all(out.values()), "checks": out, "input_blobs": blobs, "documents": docs,
            "freeze_json_sha256": sha256_file(NS / "protocol/C11RD_FREEZE_R1.json"),
            "freeze_md_sha256": sha256_file(NS / "protocol/C11RD_FREEZE_R1.md")}


# =====================================================================================================
# Q05 the frozen validation suite
# =====================================================================================================
def q05_validation(out_dir: pathlib.Path):
    d = out_dir / "validation"
    d.mkdir(parents=True, exist_ok=True)
    r = subprocess.run([sys.executable, "-I", "-S", "-B", "c11rd_validate.py", "--out", str(d / "C11RD_VALIDATION.json")],
                       cwd=CODE, capture_output=True, text=True)
    (d / "C11RD_VALIDATION.log").write_text(r.stdout + r.stderr)
    res = json.loads((d / "C11RD_VALIDATION.json").read_text())
    return {"pass": res["VALIDATION_CLASS"] == "PASS" and res["passed"] == res["total"] == 29 and r.returncode == 0,
            "passed": res["passed"], "total": res["total"], "output_sha256": sha256_file(d / "C11RD_VALIDATION.json"),
            "failed": [k for k, v in res["tests"].items() if not v["pass"]]}


# =====================================================================================================
# Q06 host / runtime (and the interpreter runtime binding, review QR1.N-11)
# =====================================================================================================
def _sysctl(name):
    return subprocess.run(["/usr/sbin/sysctl", "-n", name], capture_output=True, text=True).stdout.strip()


RUNTIME_PROBE = r'''
import importlib.util, json, os, sys, time
launcher, code = sys.argv[1], sys.argv[2]
spec = importlib.util.spec_from_file_location("c11rd_launch", launcher)
LA = importlib.util.module_from_spec(spec); spec.loader.exec_module(LA)
sys.path.insert(0, code)

def worker(_):
    time.sleep(1.0)
    import c11rd_runs, c11rd_certify, c11rd_kernel, c11rd_tm, c11rd_float, c11rd_model   # what _worker_box imports
    return {"pid": os.getpid(), "flags": bool(sys.flags.isolated and sys.flags.no_site and sys.flags.dont_write_bytecode),
            "main_image": os.path.realpath(LA.loaded_images()[0]), "files": LA.runtime_files(), "env": sorted(os.environ)}

if __name__ == "__main__":
    import multiprocessing as mp, multiprocessing.pool, socket, argparse, fractions, stat
    import c11rd_runs as RN, c11rd_model as MD, c11rd_certify as CE
    fz = json.loads((RN.NS / RN.FREEZE_REL).read_text())
    host = RN.host_identity(); wt = RN.worktree_identity()
    hist = MD.history_commits([f"{MD.NS_REL}/{RN.RUNS_REL}"])
    MD.c11r_fh_premise(); lo, hi = MD.cell_block(); P = fz["frozen_parameters"]
    cover = CE.verify_cover(CE.initial_boxes(lo, hi, P["splits"], P["tm_order"]))
    mem = RN.memory_status(os.getpid(), fz["resource_caps"]["rss_kb"])[0]
    with mp.get_context("spawn").Pool(5) as pool:
        ws = pool.map(worker, range(15), chunksize=1)
    print(json.dumps({"interpreter": LA.interpreter_identity(), "files": LA.runtime_files(), "workers": ws,
                      "env": sorted(os.environ), "home": os.environ.get("HOME"), "memory_status": mem,
                      "history_reader_ok": hist == [], "cover_ok": cover == [], "worktree": wt, "host": host}))
'''


def _runner_runtime_probe(td) -> dict:
    """The runner's interpreter under the launcher's EXACT environment: a -I -S -B process started the way
    the launcher starts the runner, importing what the runner imports, with a spawn pool of 5 workers
    that import what the workers import."""
    probe = pathlib.Path(td) / "runtime_probe.py"
    probe.write_text(RUNTIME_PROBE)
    r = subprocess.run([sys.executable, "-I", "-S", "-B", str(probe), str(LAUNCHER), str(CODE)], capture_output=True,
                       text=True, env=dict(LA.SAFE_ENV), cwd=str(CODE), timeout=600)
    if r.returncode != 0:
        return {"error": r.stderr[-800:]}
    return json.loads(r.stdout)


@check
def q06_host_runtime():
    host = RN.host_identity()
    interp = LA.interpreter_identity()
    wt = RN.worktree_identity()
    sw = subprocess.run(["/usr/bin/sw_vers"], capture_output=True, text=True).stdout
    mem_total = int(_sysctl("hw.memsize"))
    avail_kb = LA.available_memory_kb()
    disk = shutil.disk_usage(REPO)
    t0 = time.time()
    fails, n = 0, 500
    for _ in range(n):
        if RN.process_tree_rss_kb(os.getpid()) is None:
            fails += 1
    ps_seconds = time.time() - t0
    w0, m0 = time.time(), time.monotonic()
    time.sleep(2)
    drift = abs((time.time() - w0) - (time.monotonic() - m0))
    caff_ok = False
    try:
        c = LA.start_sleep_prevention()
        caff_ok = True
        c.terminate()
    except LA.LaunchRefusal:
        pass
    pmset_custom = subprocess.run([LA.PMSET, "-g"], capture_output=True, text=True).stdout
    power = LA.power_state()
    git_version = subprocess.run(["/usr/bin/git", "--version"], capture_output=True, text=True, env=SAFE_GIT_ENV).stdout.strip()
    with tempfile.TemporaryDirectory() as td:
        probe = _runner_runtime_probe(td)
        discovery = _launcher_runtime_discovery(pathlib.Path(os.path.realpath(td)))
    workers = probe.get("workers", [])
    binding = dict(probe.get("files", {}))
    for w in workers:
        binding.update(w["files"])
    binding.update(discovery.get("runtime", {}))
    RUNTIME.clear()
    RUNTIME.update(binding)
    base = os.path.realpath(sys.base_prefix)
    runner_interp = probe.get("interpreter", {})
    safe_keys = set(LA.SAFE_ENV) | set(LA.RUNTIME_ADDED)
    rec = {"grant_host": host,
           "os": {"sw_vers": dict(re.findall(r"(\w+):\s+(.+)", sw)), "kernel": platform.release(), "machine": platform.machine()},
           "cpu": {"logical": os.cpu_count(), "physical": int(_sysctl("hw.physicalcpu")), "model": _sysctl("machdep.cpu.brand_string")},
           "memory": {"total_bytes": mem_total, "available_kb_now": avail_kb},
           "disk": {"volume_of": str(REPO), "total_bytes": disk.total, "free_bytes_now": disk.free},
           "load_average_now": list(os.getloadavg()),
           "power_now": power,
           "workers_under_the_launcher_environment": {"requested": 5, "distinct_worker_pids": len({w["pid"] for w in workers}),
                                                      "all_isolated_nosite_nobytecode": all(w["flags"] for w in workers)},
           "process_table": {"calls": n, "failures": fails, "seconds": round(ps_seconds, 2), "tool": LA.PS},
           "wall_clock": {"runner_cap_clock": "time.time() (wall clock: it keeps running while the machine sleeps)",
                          "wall_vs_monotonic_drift_over_2s": round(drift, 6)},
           "sleep_prevention": {"tool": LA.CAFFEINATE, "assertion_verified": caff_ok,
                                "mechanism": "caffeinate -i -s -w <launcher pid> in its own session; the launcher verifies "
                                             "PreventUserIdleSystemSleep and PreventSystemSleep in `pmset -g assertions` before consuming",
                                "pmset_sleep_settings_now": dict(re.findall(r"^\s*(sleep|displaysleep|disksleep|standby|powernap)\s+(\d+)",
                                                                            pmset_custom, re.M))},
           "git": {"binary": "/usr/bin/git", "version": git_version},
           "interpreter_finding (QR1.N-11)": {
               "sys_executable": interp["executable_realpath"], "running_main_image": interp["main_image"],
               "libpython": interp["libpython"],
               "note": "sys.executable is the framework stub; the Mach-O image that actually runs (dyld image 0) is "
                       "Resources/Python.app/Contents/MacOS/Python, linked to libpython Versions/3.14/Python; all three, "
                       "every extension module and every stdlib source and cached bytecode loaded by the launcher, the "
                       "runner-like probe and its spawn workers are bound in runtime_files_sha256 and re-hashed at launch"},
           "runtime_binding": {"files": len(binding), "sha256_of_the_binding": sha256_bytes(json.dumps(binding, sort_keys=True).encode()),
                               "mach_o_images": sorted(f for f in binding if f.endswith((".so", "/Python"))),
                               "from": ["runner-like probe (parent)", "its 5 spawn workers", "the launcher after a full sandbox launch"]}}
    out = {"host_identity_complete": bool(host["hostname"]) and len(host["platform_uuid"]) == 36,
           "interpreter_flags": interp["flags_isolated_nosite_nobytecode"],
           "N-11 running image is NOT the stub; stub, image and libpython hashed": interp["main_image"] != interp["executable_realpath"]
               and interp["main_image"].startswith(base + "/") and interp["libpython_loaded"] and bool(interp["libpython_sha256"]),
           "N-11 the runner-like probe and every worker run the same image": runner_interp.get("main_image") == interp["main_image"]
               and bool(workers) and all(w["main_image"] == interp["main_image"] for w in workers)
               and runner_interp == interp,
           "N-11 binding covers images, libpython, stdlib sources and cached bytecode": interp["main_image"] in binding
               and interp["libpython"] in binding and any(f.endswith(".so") for f in binding) and any(f.endswith(".pyc") for f in binding)
               and any(f.endswith("/fractions.py") for f in binding) and bool(discovery.get("runtime")),
           "worktree_canonical": wt["canonical_path"] == os.path.realpath(REPO),
           "ram_at_least_4x_cap": mem_total >= 4 * 2097152 * 1024,
           "disk_free_at_least_min": disk.free >= LAUNCH_LIMITS["disk_free_min_bytes"],
           "five_isolated_workers_under_the_launcher_environment": len({w["pid"] for w in workers}) == 5 and all(w["flags"] for w in workers),
           "N-7 the runner environment is exactly the sanitized set (HOME=/var/empty)": probe.get("home") == "/var/empty"
               and set(probe.get("env", ["?"])) <= safe_keys and all(set(w["env"]) <= safe_keys for w in workers),
           "memory_accounting_and_frozen_readers_work_under_that_environment": probe.get("memory_status") == "OK"
               and probe.get("history_reader_ok") is True and probe.get("cover_ok") is True and probe.get("worktree") == wt
               and probe.get("host") == host,
           "seal_identity_is_repo_local (user.name, user.email; global config ignored)": all(
               LA.git(REPO, "config", "--get", k).stdout.strip() for k in ("user.name", "user.email"))
               and LA.git(REPO, "var", "GIT_COMMITTER_IDENT").returncode == 0,
           "process_table_reliable": fails == 0,
           "wall_clock_sane": drift < 0.05,
           "sleep_prevention_verified (-i and -s)": caff_ok,
           "power_state_readable (N-10)": power["ac_power"] is not None and power["lid_open"] is not None,
           "launcher_discovery_launch_sealed": discovery.get("sealed") is True}
    return {"pass": all(out.values()), "checks": out, "record": rec, "interpreter": interp, "worktree": wt,
            "runtime_files_sha256": binding, "probe_error": probe.get("error"), "discovery_error": discovery.get("error")}


# =====================================================================================================
# scratch repositories, the synthetic lineage and the launcher sandbox
# =====================================================================================================
def _repo(td, name):
    r = pathlib.Path(td) / name
    r.mkdir(parents=True)
    for a in (["init", "-q", "-b", "main"], ["config", "user.email", "q@example.invalid"], ["config", "user.name", "q"],
              ["config", "commit.gpgsign", "false"]):
        G(r, *a)
    if not (r / ".git").is_dir():
        raise RuntimeError("scratch repository not created")
    return r


def _commit(repo, files, msg):
    for rel, content in files.items():
        f = pathlib.Path(repo) / rel
        if content is None:
            G(repo, "rm", "-q", rel)
        else:
            f.parent.mkdir(parents=True, exist_ok=True)
            f.write_bytes(content if isinstance(content, bytes) else content.encode())
            G(repo, "add", "-f", rel)
    G(repo, "commit", "-qm", msg, "--allow-empty")
    return G(repo, "rev-parse", "HEAD").stdout.strip()


def _synthetic_chain(td, fz_bytes, *, mutate=None, stub_src=None):
    """freeze -> qualification -> QUALIFICATION_ACCEPTED -> grant -> AUTHORIZATION_ACCEPTED, in a LINKED
    worktree of a scratch repository (the real layout: the launch worktree is a linked worktree)."""
    td = pathlib.Path(td)
    fz = json.loads(fz_bytes)
    main = _repo(td, "main_repo")
    _commit(main, {"README": "base\n"}, "base")
    G(main, "worktree", "add", "-q", "-b", SANDBOX_BRANCH.rsplit("/", 1)[1], str(td / "wt"))
    repo = td / "wt"
    ns = repo / NS_REL
    stub = ns / "code" / "c11rd_runs.py"                      # named like the runner: the process check sees it
    F0 = _commit(repo, {f"{NS_REL}/{RN.FREEZE_REL}": fz_bytes, f"{NS_REL}/code/c11rd_runs.py": stub_src or "#\n"}, "freeze")
    wt = RN.worktree_identity(repo=repo)
    host = RN.host_identity()
    qualified = {"schema": LA.QUAL_SCHEMA, "freeze_commit": F0, "host": {"grant_host": host},
                 "interpreter": LA.interpreter_identity(), "runtime_files_sha256": dict(RUNTIME), "worktree": wt,
                 "launch_branch": SANDBOX_BRANCH, "launch_limits": dict(SANDBOX_LIMITS),
                 "frozen_code_sha256": {LA.RUNNER_REL: sha256_file(stub)},
                 "qualification_code_sha256": {LA.LAUNCHER_REL: sha256_file(LAUNCHER)}}
    if mutate:
        mutate(qualified)
    Q = _commit(repo, {f"{NS_REL}/{LA.QUAL_ARTIFACT_REL}": json.dumps(qualified, indent=1) + "\n"}, "qualification")
    QR = _commit(repo, {f"{NS_REL}/{LA.QUAL_REVIEW_REL}": "# q review\nQUALIFICATION_ACCEPTED\n"}, "qualification review")
    lo, hi = MD.cell_block()
    grant = {"campaign": "C11RD", "decision": "ALLOW",
             "target": {"cell": 306, "e_lo": str(lo), "e_hi": str(hi), "constants": ["D1", "D2"]},
             "max_executions": 1, "freeze_commit": F0, "freeze_sha256": sha256_bytes(fz_bytes),
             "code_sha256": fz["code_sha256"], "input_bindings": fz["input_bindings"], "host": host, "worktree": wt,
             "qualification": {"commit": Q, "artifact_path": f"{NS_REL}/{LA.QUAL_ARTIFACT_REL}",
                               "artifact_blob": G(repo, "rev-parse", f"{Q}:{NS_REL}/{LA.QUAL_ARTIFACT_REL}").stdout.strip(),
                               "review_commit": QR, "review_path": f"{NS_REL}/{LA.QUAL_REVIEW_REL}"}}
    gbytes = json.dumps(grant, indent=1, sort_keys=True) + "\n"
    _commit(repo, {f"{NS_REL}/{RN.GRANT_REL}": gbytes}, "grant")
    AR = _commit(repo, {f"{NS_REL}/{RN.AUTH_REVIEW_REL}": "# a review\nAUTHORIZATION_ACCEPTED\n"}, "authorization review")
    common = pathlib.Path(G(repo, "rev-parse", "--path-format=absolute", "--git-common-dir").stdout.strip())
    gitdir = pathlib.Path(G(repo, "rev-parse", "--path-format=absolute", "--git-dir").stdout.strip())
    return {"repo": repo, "main": main, "ns": ns, "F0": F0, "Q": Q, "QR": QR, "AR": AR, "grant": grant, "gbytes": gbytes,
            "fz": fz, "host": host, "wt": wt, "qualified": qualified, "stub": stub, "common": common, "gitdir": gitdir}


def _regrant(ch, **changes):
    """Rewrite the chain's grant with `changes` (then a new authorization review commit binds it)."""
    g = json.loads(json.dumps(ch["grant"]))
    for k, v in changes.items():
        if k.startswith("q_"):
            g["qualification"][k[2:]] = v
        else:
            g[k] = v
    gb = json.dumps(g, indent=1, sort_keys=True) + "\n"
    _commit(ch["repo"], {f"{NS_REL}/{RN.GRANT_REL}": gb}, "regrant")
    ch["AR"] = _commit(ch["repo"], {f"{NS_REL}/{RN.AUTH_REVIEW_REL}": "# a review\nAUTHORIZATION_ACCEPTED\n\n"}, "re-authorization")


STUB = r'''
import json, os, pathlib, subprocess, sys, time
mode, marker = sys.argv[1], pathlib.Path(sys.argv[2])
ns = pathlib.Path(__file__).resolve().parents[1]
repo = ns.parents[2]
GENV = {"PATH": "/usr/bin:/bin", "HOME": "/var/empty", "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": "/dev/null"}
def g(*a):
    return subprocess.run(["/usr/bin/git", "-C", str(repo), *a], capture_output=True, text=True, env=GENV)
with open(marker, "a") as f:
    f.write(mode + "\n")
if mode == "env":
    pathlib.Path(sys.argv[3]).write_text(json.dumps(dict(os.environ)))
if mode == "refuse":
    print("REFUSE R2: stub refusal before the lock"); sys.exit(1)
runs = ns / "evidence" / "runs"
runs.mkdir(parents=True, exist_ok=True)
(runs / "C11RD_EXECUTION.lock").write_text("{}\n")
print("stub started", flush=True)
if mode == "crash":
    raise RuntimeError("stub crash after the lock")
if mode == "hang":
    time.sleep(120)
if mode == "slow":
    time.sleep(float(sys.argv[3]))
gd = pathlib.Path(g("rev-parse", "--path-format=absolute", "--git-dir").stdout.strip())
cd = pathlib.Path(g("rev-parse", "--path-format=absolute", "--git-common-dir").stdout.strip())
branch = g("symbolic-ref", "HEAD").stdout.strip()
if mode in ("branch_lock_transient", "branch_lock_permanent"):
    lk = cd / (branch + ".lock")
    lk.write_text("")
    if mode == "branch_lock_transient":
        subprocess.Popen([sys.executable, "-I", "-S", "-B", "-c", f"import os, time; time.sleep({float(sys.argv[3])}); os.unlink({str(lk)!r})"],
                         start_new_session=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
if mode == "move_head":
    g("commit", "-q", "--allow-empty", "-m", "a commit made while the execution ran")
if mode == "index_lock":
    (gd / "index.lock").write_text("")
if mode == "stage_foreign":
    (repo / "elsewhere").mkdir(exist_ok=True)
    (repo / "elsewhere" / "late.txt").write_text("staged while the execution ran\n")
    g("add", "-f", "elsewhere/late.txt")
(runs / "C11RD_RUNS.json").write_text(json.dumps({"status": "NOT_CERTIFIED" if mode == "not_certified" else "CERTIFIED"}) + "\n")
sys.exit(3 if mode == "not_certified" else 0)
'''

DRIVER = r'''
import importlib.util, json, os, pathlib, signal, sys
spec = importlib.util.spec_from_file_location("c11rd_launch", sys.argv[1])
LA = importlib.util.module_from_spec(spec); spec.loader.exec_module(LA)
repo, ns_rel, ar, stub, mode, marker, logdir, hooks = sys.argv[2:10]
extra, hooks = sys.argv[10:], json.loads(hooks)
ar = hooks.get("ar", ar)
cmd = [sys.executable, "-I", "-S", "-B", stub, mode, marker, *extra]
# test hooks: monkeypatching only -- the launcher itself has no test switch
if "delays" in hooks:
    LA.SEAL_RETRY_DELAYS = tuple(hooks["delays"])
if hooks.get("no_runtime_check"):
    LA.runtime_problems = lambda q: []
if hooks.get("ps_fail"):
    LA.PS = "/nonexistent/ps"
if hooks.get("no_seal_safety"):
    LA.seal_safety_problems = lambda *a, **k: []
if "power" in hooks:
    LA.power_state = lambda: dict(hooks["power"])
if "runner_guard_fail" in hooks:
    RN = LA._frozen()
    def boom(*a, **k):
        raise RN.Refusal(hooks["runner_guard_fail"][1])
    setattr(RN, hooks["runner_guard_fail"][0], boom)
def send(names):
    for n in names:
        if n == "GROUP_SIGINT":
            os.killpg(os.getpgrp(), signal.SIGINT)
        else:
            os.kill(os.getpid(), getattr(signal, n))
if "signals_in_gate" in hooks:
    real_gate = LA.final_gate_problems
    def gate(*a, **k):
        send(hooks["signals_in_gate"]); return real_gate(*a, **k)
    LA.final_gate_problems = gate
if "signals_after_consume" in hooks:
    real_consume = LA.consume
    def consume(*a, **k):
        real_consume(*a, **k); send(hooks["signals_after_consume"])
    LA.consume = consume
if "signals_before_seal_ref_update" in hooks:
    real_git, sent = LA.git, []
    def git(repo_, *args, **kw):
        if args[:1] == ("update-ref",) and len(args) > 3 and args[3].startswith("refs/heads/") and not sent:
            sent.append(1); send(hooks["signals_before_seal_ref_update"])
        return real_git(repo_, *args, **kw)
    LA.git = git
if hooks.get("seal_only"):
    q = LA.load_qualified(repo, ns_rel, json.loads((pathlib.Path(repo) / ns_rel / "config/C11RD_GRANT.json").read_text()))
    code, text = LA.execute(LA.seal_only, repo, ns_rel, ar, q, log_dir=logdir)
else:
    code, text = LA.execute(LA.launch, repo, ns_rel, ar, runner_cmd=cmd, runner_path=stub, log_dir=logdir)
print("EXIT " + str(code)); print("TEXT_BEGIN"); print(text); print("TEXT_END")
if hooks.get("print_runtime"):
    print("RUNTIME " + json.dumps(LA.runtime_files()))
if hooks.get("pgid_probe"):
    r = LA._run(["/bin/sh", "-c", "ps -o pgid= -p $$"])
    print("PGID " + json.dumps({"child": int(r.stdout.strip()), "launcher": os.getpgrp()}))
sys.stdout.flush()
'''


def _parse_driver(so: str) -> dict:
    res = {"exit": None, "text": "", "result": None, "unsealed": None, "refused": None, "seal_only_refused": None}
    m = re.search(r"^EXIT (\d+)$", so, re.M)
    res["exit"] = int(m.group(1)) if m else None
    t = re.search(r"TEXT_BEGIN\n(.*?)\nTEXT_END", so, re.S)
    res["text"] = t.group(1) if t else ""
    first = res["text"].splitlines()[0] if res["text"] else ""
    res["first_line"] = first
    if first.startswith("SEALED "):
        res["result"] = json.loads(first[7:])
    elif first == LA.UNSEALED_BANNER:
        u = re.search(r"^UNSEALED_REPORT (.*)$", res["text"], re.M)
        res["unsealed"] = json.loads(u.group(1)) if u else {}
    elif first.startswith("REFUSE"):
        res["refused"] = res["text"]
    elif first.startswith("SEAL-ONLY REFUSED"):
        res["seal_only_refused"] = res["text"]
    rt = re.search(r"^RUNTIME (.*)$", so, re.M)
    res["runtime"] = json.loads(rt.group(1)) if rt else None
    pg = re.search(r"^PGID (.*)$", so, re.M)
    res["pgid"] = json.loads(pg.group(1)) if pg else None
    return res


def _index_state(repo):
    return sha256_bytes(G(repo, "ls-files", "-s", "--debug", text=False).stdout)


def _run_driver(ch, sub, mode, *, env=None, hooks=None, extra=(), signal_after_start=None, new_session=False,
                kill_after_start=None, timeout=600):
    drv = sub / "driver.py"
    if not drv.exists():
        drv.write_text(DRIVER)
    marker = sub / "started.txt"
    cmd = [sys.executable, "-I", "-S", "-B", str(drv), str(LAUNCHER), str(ch["repo"]), NS_REL, ch["AR"], str(ch["stub"]),
           mode, str(marker), str(sub / "logs"), json.dumps(hooks or {}), *extra]
    t0 = time.time()
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env or dict(os.environ),
                         start_new_session=new_session or bool(kill_after_start) or bool(signal_after_start))
    if signal_after_start or kill_after_start:
        lock = ch["ns"] / "evidence/runs/C11RD_EXECUTION.lock"
        while time.time() - t0 < 120 and not lock.exists():
            time.sleep(0.05)
        time.sleep(0.5)
        if kill_after_start:
            p.send_signal(signal.SIGKILL)
        elif signal_after_start == "GROUP_SIGINT":
            os.killpg(p.pid, signal.SIGINT)
        else:
            p.send_signal(signal_after_start)
    so, se = p.communicate(timeout=timeout)
    res = _parse_driver(so)
    res.update(rc=p.returncode, stderr_tail=se[-600:], seconds=round(time.time() - t0, 2))
    return res


def _observe(ch, sub, res, head0, index0):
    repo = ch["repo"]
    marker = sub / "started.txt"
    res["stub_runs"] = marker.read_text().split() if marker.exists() else []
    res["consumed_ref"] = G(repo, "rev-parse", "--verify", "-q", LA.CONSUMED_REF).stdout.strip()
    res["head0"], res["head"] = head0, G(repo, "rev-parse", "HEAD").stdout.strip()
    res["index_unchanged"] = _index_state(repo) == index0
    runs = ch["ns"] / "evidence/runs"
    res["runs_on_disk"] = sorted(f.name for f in runs.iterdir()) if runs.is_dir() else []
    r = res.get("result")
    if r:
        seal = r["seal_commit"]
        res["seal_parent_is_start_head"] = G(repo, "rev-list", "--parents", "-n", "1", seal).stdout.split()[1:] == [head0]
        files = G(repo, "show", "--name-only", "--format=", seal).stdout.split()
        res["seal_only_runs_dir"] = bool(files) and all(f.startswith(f"{NS_REL}/evidence/runs/") for f in files)
        res["sealed_files"] = sorted(f.rsplit("/", 1)[1] for f in files)
        res["seal_message"] = G(repo, "log", "-1", "--format=%s", seal).stdout.strip()
        res["namespace_clean_after_seal"] = G(repo, "status", "--porcelain", "--ignored", "--untracked-files=all", "--",
                                              NS_REL).stdout.strip() == ""
    return res


def _launch_in_sandbox(td, mode, *, mutate=None, pre=None, **kw):
    fz_bytes = (NS / RN.FREEZE_REL).read_bytes()
    sub = pathlib.Path(td) / f"sb_{mode}_{random.randrange(10 ** 9)}"
    sub.mkdir()
    ch = _synthetic_chain(sub, fz_bytes, mutate=mutate, stub_src=STUB)
    if pre:
        pre(ch)
    head0, index0 = G(ch["repo"], "rev-parse", "HEAD").stdout.strip(), _index_state(ch["repo"])
    res = _run_driver(ch, sub, mode, **kw)
    res = _observe(ch, sub, res, head0, index0)
    res["_chain"], res["_sub"] = ch, sub
    return res


def _sealed_ok(r, outcome, files=None):
    return r["exit"] == 0 and bool(r["result"]) and r["result"]["outcome"] == outcome and r.get("seal_parent_is_start_head") \
        and r.get("seal_only_runs_dir") and r.get("namespace_clean_after_seal") and r["consumed_ref"] == r["head0"] \
        and (files is None or r.get("sealed_files") == sorted(files))


def _refused_ok(r, want, ref_preexisting=False):
    ref_ok = r["consumed_ref"] == r["head0"] if ref_preexisting else r["consumed_ref"] == ""
    return r["exit"] == 2 and r["first_line"].startswith("REFUSE") and want in r["text"] and ref_ok \
        and r["stub_runs"] == [] and r["head"] == r["head0"] and r["runs_on_disk"] == [] and r["index_unchanged"]


def _unsealed_ok(r):
    return r["exit"] == 4 and r["first_line"] == LA.UNSEALED_BANNER and not r["text"].startswith("REFUSE") \
        and "REFUSE" not in r["first_line"] and r["unsealed"] is not None and r["consumed_ref"] == r["head0"] \
        and len(r["stub_runs"]) == 1


SEALED_ALL = ["C11RD_EXECUTION.lock", "C11RD_EXECUTION.log", "C11RD_LAUNCH_JOURNAL.jsonl", "C11RD_RUNS.json"]


def _launcher_runtime_discovery(td) -> dict:
    """One full sandbox launch with the runtime-binding check disabled (monkeypatched in the driver), to
    learn every interpreter file the LAUNCHER process loads through a complete launch."""
    try:
        r = _launch_in_sandbox(td, "certified", hooks={"no_runtime_check": True, "print_runtime": True})
        return {"runtime": r["runtime"] or {}, "sealed": bool(r["result"]) and r["exit"] == 0}
    except Exception as exc:                                  # noqa: BLE001
        return {"error": f"{type(exc).__name__}: {exc}"}


# =====================================================================================================
# Q07 git / history hardening (scratch repositories only)
# =====================================================================================================
HOSTILE_ENV = {"GIT_DIR": "/nonexistent/.git", "GIT_WORK_TREE": "/tmp", "GIT_INDEX_FILE": "/nonexistent/index",
               "GIT_OBJECT_DIRECTORY": "/nonexistent/objects", "GIT_ALTERNATE_OBJECT_DIRECTORIES": "/nonexistent/alt",
               "GIT_NAMESPACE": "hidden", "GIT_CONFIG_PARAMETERS": "'core.commitgraph'='true'",
               "GIT_CONFIG_COUNT": "1", "GIT_CONFIG_KEY_0": "core.commitGraph", "GIT_CONFIG_VALUE_0": "true",
               "GIT_REPLACE_REF_BASE": "refs/other/", "GIT_CEILING_DIRECTORIES": "/", "GIT_CONFIG_GLOBAL": "/nonexistent/cfg",
               "GIT_CONFIG_SYSTEM": "/nonexistent/sys", "PATH": "/nonexistent/bin:/usr/bin:/bin"}
FAILING_HOOK = "#!/bin/sh\necho HOOK-RAN >&2\nexit 1\n"


def _lying_commit_graph(r):
    """A commit-graph whose CDAT entry claims c3's parent is c1 (git does not check the file's checksum
    when it loads it): plain git follows the lie, a reader that does not consult the graph does not."""
    import struct
    c1, c2, c3 = G(r, "rev-list", "--reverse", "HEAD").stdout.split()[-3:]
    subprocess.run(["/usr/bin/git", "-C", str(r), "commit-graph", "write", "--reachable"], capture_output=True, env=SAFE_GIT_ENV)
    cg = r / ".git/objects/info/commit-graph"
    b = bytearray(cg.read_bytes())
    chunks = {bytes(b[8 + 12 * i: 12 + 12 * i]): struct.unpack(">Q", b[12 + 12 * i: 20 + 12 * i])[0] for i in range(b[6] + 1)}
    n = struct.unpack(">I", b[chunks[b"OIDF"] + 1020: chunks[b"OIDF"] + 1024])[0]
    oids = [b[chunks[b"OIDL"] + 20 * i: chunks[b"OIDL"] + 20 * (i + 1)].hex() for i in range(n)]
    ent = chunks[b"CDAT"] + oids.index(c3) * 36
    b[ent + 20: ent + 24] = struct.pack(">I", oids.index(c1))
    cg.chmod(0o644)
    cg.write_bytes(bytes(b))
    return c1, c2, c3


@check
def q07_git_history_hardening():
    art = f"{NS_REL}/{CM.OUT_REL}"
    out = {}
    info = {}
    with tempfile.TemporaryDirectory() as td:
        td = pathlib.Path(os.path.realpath(td))
        r = _repo(td, "base")
        _commit(r, {"README": "x\n"}, "base")
        _commit(r, {art: "{}\n"}, "compare")
        _commit(r, {art: None}, "delete")
        found = MD.history_commits([art], repo=r)
        out["deleted_artifact_found"] = len(found) == 2
        # QR1.N-6: a DISCRIMINATING commit-graph test -- the graph lies about a parent
        lg = _repo(td, "lying_graph")
        for i in (1, 2, 3):
            _commit(lg, {f"f{i}": f"{i}\n"}, f"c{i}")
        c1, c2, c3 = _lying_commit_graph(lg)
        plain_path = subprocess.run(["/usr/bin/git", "-C", str(lg), "rev-list", "--all", "--full-history", "--", "f2"],
                                    capture_output=True, text=True, env=SAFE_GIT_ENV).stdout.split()
        plain_parent = subprocess.run(["/usr/bin/git", "-C", str(lg), "log", "-1", "--format=%P", c3],
                                      capture_output=True, text=True, env=SAFE_GIT_ENV).stdout.strip()
        info["lying_graph"] = {"plain_git_commits_touching_f2": plain_path == [c3] and "c3 (wrong)",
                               "plain_git_parent_of_c3_is_c1 (the lie)": plain_parent == c1}
        out["N-6 plain git follows a lying commit-graph (the test can fail)"] = plain_parent == c1 and plain_path != [c2]
        out["N-6 the frozen reader and the launcher's git do not (truth: c2 touches f2; c3's parent is c2)"] = \
            MD.history_commits(["f2"], repo=lg) == [c2] and \
            LA.git(lg, "log", "-1", "--format=%P", c3).stdout.strip() == c2 and \
            LA.git(lg, "rev-list", "--all", "--full-history", "--", "f2").stdout.split() == [c2]
        # replace ref hiding the artifact commit
        base = G(r, "rev-parse", "HEAD~2").stdout.strip()
        G(r, "replace", found[-1] if len(found) > 1 else found[0], base)
        out["replace_ref_ignored"] = set(MD.history_commits([art], repo=r)) == set(found)
        # hostile git environment in THIS process: the frozen reader and the launcher pass explicit environments
        saved = dict(os.environ)
        try:
            os.environ.update(HOSTILE_ENV)
            out["hostile_env_ignored_by_frozen_history_reader"] = set(MD.history_commits([art], repo=r)) == set(found)
            out["hostile_env_ignored_by_comparator_run_once"] = any("reachable history" in x for x in
                                                                   CM.run_once_problems(repo=r, ns=r / NS_REL, ns_rel=NS_REL))
            out["hostile_env_ignored_by_launcher_git"] = LA.git(r, "rev-parse", "HEAD").stdout.strip() == \
                G(r, "rev-parse", "HEAD").stdout.strip()
        finally:
            os.environ.clear()
            os.environ.update(saved)
        # hooks: repository hooks (and a hostile global config) cannot act on the launcher's git
        hk = _repo(td, "hooks")
        _commit(hk, {"a": "a\n"}, "a")
        for h in ("reference-transaction", "pre-commit", "post-index-change", "post-commit"):
            (hk / ".git/hooks" / h).write_text(FAILING_HOOK)
            (hk / ".git/hooks" / h).chmod(0o755)
        plain = subprocess.run(["/usr/bin/git", "-C", str(hk), "update-ref", "refs/x/plain", "HEAD", ""], capture_output=True,
                               text=True, env=SAFE_GIT_ENV)
        out["hooks: plain git runs the failing reference-transaction hook (control)"] = plain.returncode != 0 and "HOOK-RAN" in plain.stderr
        la = LA.git(hk, "update-ref", "refs/x/launcher", "HEAD", "")
        out["hooks: the launcher's git runs no hook (core.hooksPath=/dev/null)"] = la.returncode == 0 and "HOOK-RAN" not in la.stderr
        home = td / "hostile_home"
        (home / ".config/git").mkdir(parents=True)
        (home / ".gitconfig").write_text("[user]\n\tname = hostile\n[commit]\n\tgpgSign = true\n[gpg]\n\tprogram = /nonexistent\n"
                                         f"[core]\n\thooksPath = {hk / '.git/hooks'}\n")
        (home / ".config/git/attributes").write_text("* filter=evil\n")
        saved = dict(os.environ)
        try:
            os.environ.update(HOME=str(home), XDG_CONFIG_HOME=str(home / ".config"))
            henv = {"PATH": "/usr/bin:/bin", "HOME": str(home)}
            plain_gpg = subprocess.run(["/usr/bin/git", "-C", str(hk), "config", "--get", "gpg.program"], capture_output=True,
                                       text=True, env=henv).stdout.strip()
            plain_attr = subprocess.run(["/usr/bin/git", "-C", str(hk), "check-attr", "-a", "--", "x.json"], capture_output=True,
                                        text=True, env=henv).stdout.strip()
            out["N-7 a hostile HOME configures plain git (control: global gpg.program and global attributes apply)"] = \
                plain_gpg == "/nonexistent" and "filter: evil" in plain_attr
            out["N-7 the launcher's git ignores HOME (no global config, no global attributes)"] = \
                LA.git(hk, "config", "--get", "gpg.program").stdout.strip() == "" and \
                LA.git(hk, "config", "--get", "user.name").stdout.strip() == "q" and \
                LA.git(hk, "config", "--get", "commit.gpgSign").stdout.strip() == "false" and \
                LA.git(hk, "check-attr", "-a", "--", "x.json").stdout.strip() == ""
        finally:
            os.environ.clear()
            os.environ.update(saved)
        # grafts / shallow fail closed
        r2 = _repo(td, "grafts")
        _commit(r2, {"a": "a\n"}, "a")
        (r2 / ".git/info").mkdir(exist_ok=True)
        (r2 / ".git/info/grafts").write_text("")
        try:
            MD.history_commits([art], repo=r2)
            out["grafts_fail_closed"] = False
        except MD.ModelError:
            out["grafts_fail_closed"] = True
        sh = td / "shallow"
        subprocess.run(["/usr/bin/git", "clone", "-q", "--depth", "1", f"file://{r}", str(sh)], capture_output=True, env=SAFE_GIT_ENV)
        try:
            MD.history_commits([art], repo=sh)
            out["shallow_fail_closed"] = False
        except MD.ModelError:
            out["shallow_fail_closed"] = True
        r3 = _repo(td, "wt_main")
        _commit(r3, {"a": "a\n"}, "a")
        G(r3, "worktree", "add", "-q", "--detach", str(td / "wt_linked"))
        _commit(td / "wt_linked", {art: "{}\n"}, "compare in linked worktree")
        out["linked_detached_worktree_found"] = len(MD.history_commits([art], repo=r3)) == 1
        alias = td / "alias"
        os.symlink(r, alias)
        out["path_alias_same_history"] = set(MD.history_commits([art], repo=alias)) == set(found)
        out["path_alias_same_worktree_identity"] = RN.worktree_identity(repo=alias) == RN.worktree_identity(repo=r)
    saved = dict(os.environ)
    try:
        os.environ.update(HOSTILE_ENV)
        out["real_repository_clean_under_hostile_env"] = MD.history_commits([f"{NS_REL}/{p}" for p in FORBIDDEN_LIFECYCLE_PATHS]) == []
    finally:
        os.environ.clear()
        os.environ.update(saved)
    return {"pass": all(out.values()), "checks": out, "hostile_variables": sorted(HOSTILE_ENV), "information": info}


# =====================================================================================================
# Q08 execution lifecycle
# =====================================================================================================
def _main_real_branch_order():
    src = (CODE / "c11rd_runs.py").read_text()
    fn = next(n for n in ast.parse(src).body if isinstance(n, ast.FunctionDef) and n.name == "main")
    calls = []
    for n in ast.walk(fn):
        if isinstance(n, ast.Call):
            name = n.func.id if isinstance(n.func, ast.Name) else (n.func.attr if isinstance(n.func, ast.Attribute) else None)
            if name:
                calls.append((n.lineno, n.col_offset, name))
    calls.sort()
    return calls, src


@check
def q08_execution_lifecycle():
    out = {}
    calls, src = _main_real_branch_order()
    lines = {}
    for ln, _, nm in calls:
        lines.setdefault(nm, []).append(ln)
    real_cb = max(lines["certify_block"])
    out["real_mode_order: grant < clean < loaded-modules < lock < certify_block < artifact"] = \
        lines["verify_grant"][0] < lines["verify_clean"][0] < lines["take_lock"][0] < real_cb < lines["replace"][0] and \
        any(lines["verify_clean"][0] < x < lines["take_lock"][0] for x in lines["verify_loaded_modules"])
    out["cover_and_accounting_checked_before_any_mode"] = lines["verify_cover_and_accounting"][0] < min(lines["certify_block"])
    out["certify_block_called_only_in_main"] = sum(1 for n in ast.walk(ast.parse(src)) if isinstance(n, ast.Call)
                                                   and isinstance(n.func, ast.Name) and n.func.id == "certify_block") == 2
    out["lock_never_removed_by_runner"] = not re.search(r"unlink|os\.remove|rmtree|os\.rmdir", src)
    out["not_certified_writes_no_value"] = 'str(res[k]) if res["status"] == "CERTIFIED" else None' in src
    cm_src = (CODE / "c11rd_compare.py").read_text()
    out["comparator_treats_not_certified_as_INSUFFICIENT"] = 'if runs.get("status") != "CERTIFIED":' in cm_src and \
        '"CLASS": "INSUFFICIENT"' in cm_src
    # --- the predecessor matrix, through the frozen runner's grant check, in scratch repositories
    fz_bytes = (NS / RN.FREEZE_REL).read_bytes()
    matrix = {}
    with tempfile.TemporaryDirectory() as td:
        td = pathlib.Path(os.path.realpath(td))
        ch = _synthetic_chain(td, fz_bytes)
        repo, ns, fz = ch["repo"], ch["ns"], ch["fz"]

        def probs(g=None, host=None, wt=None, ar=None):
            return RN.grant_problems(fz, g or ch["grant"], host=host or ch["host"], worktree=wt or ch["wt"],
                                     auth_review_commit=ch["AR"] if ar is None else ar, repo=repo, ns=repo / NS_REL,
                                     code_dir=ns / "code")
        matrix["positive_control_all_predecessors_present"] = probs() == []

        def g_(**kw):
            g = json.loads(json.dumps(ch["grant"]))
            for k, v in kw.items():
                if k.startswith("q_"):
                    g["qualification"][k[2:]] = v
                else:
                    g[k] = v
            return g
        matrix["freeze_commit_missing"] = bool(probs(g=g_(freeze_commit="0" * 40)))
        matrix["qualification_commit_missing"] = bool(probs(g=g_(q_commit="1" * 40)))
        matrix["qualification_review_commit_missing"] = bool(probs(g=g_(q_review_commit="2" * 40)))
        matrix["qualification_review_file_missing"] = bool(probs(g=g_(q_review_path=f"{NS_REL}/review/NOPE.md")))
        matrix["authorization_review_missing"] = bool(probs(ar=""))
        matrix["lineage_out_of_order"] = bool(probs(g=g_(q_commit=ch["QR"], q_review_commit=ch["Q"])))
        matrix["platform_only_deviation"] = bool(probs(host=dict(ch["host"], platform="linux")))
        g2 = g_()
        g2["input_bindings"] = dict(g2["input_bindings"], c7_gaussian=dict(g2["input_bindings"]["c7_gaussian"], sha256="0" * 64))
        matrix["input_bindings_deviation"] = bool(probs(g=g2))
        matrix["git_common_dir_only_deviation"] = bool(probs(wt=dict(ch["wt"], git_common_dir="/elsewhere/.git")))
        QRr = _commit(repo, {f"{NS_REL}/{LA.QUAL_REVIEW_REL}": "QUALIFICATION_REJECTED\n"}, "rejected review")
        matrix["QUALIFICATION_REJECTED"] = bool(probs(g=g_(q_review_commit=QRr), ar=_commit(repo, {}, "noop")))
        QRd = _commit(repo, {f"{NS_REL}/{LA.QUAL_REVIEW_REL}": "QUALIFICATION_ACCEPTED\nQUALIFICATION_ACCEPTED\n"}, "dup review")
        matrix["qualification_review_duplicated"] = bool(probs(g=g_(q_review_commit=QRd), ar=_commit(repo, {}, "noop2")))
        ARr = _commit(repo, {f"{NS_REL}/{RN.AUTH_REVIEW_REL}": "AUTHORIZATION_REJECTED\n"}, "auth rejected")
        matrix["AUTHORIZATION_REJECTED"] = bool(probs(ar=ARr))
        ARn = _commit(repo, {f"{NS_REL}/{RN.GRANT_REL}": None}, "grant removed")
        (ns / RN.GRANT_REL).parent.mkdir(parents=True, exist_ok=True)
        (ns / RN.GRANT_REL).write_text(ch["gbytes"])
        matrix["grant_absent_at_authorization_review"] = any("byte-identical" in x for x in probs(ar=ARn))
        with tempfile.TemporaryDirectory() as td2:
            td2 = pathlib.Path(os.path.realpath(td2))
            alt = json.loads(fz_bytes)
            alt["campaign"] = alt["campaign"] + " (older variant)"
            r2 = _repo(td2, "anc")
            Fold = _commit(r2, {f"{NS_REL}/{RN.FREEZE_REL}": json.dumps(alt) + "\n", f"{NS_REL}/code/c11rd_runs.py": "#\n"}, "old freeze")
            _commit(r2, {f"{NS_REL}/{RN.FREEZE_REL}": fz_bytes}, "new freeze")
            matrix["ancestor_freeze_commit_with_different_freeze_file"] = any(
                "byte-identical" in x for x in RN.grant_problems(fz, g_(freeze_commit=Fold), host=ch["host"],
                                                                 worktree=RN.worktree_identity(repo=r2), auth_review_commit="",
                                                                 repo=r2, ns=r2 / NS_REL, code_dir=r2 / NS_REL / "code"))
    out["predecessor_matrix_all_refused_and_positive_control_passes"] = all(matrix.values())
    # --- attempt semantics of the PRODUCTION runner on the NON-TARGET block (no target science)
    sem = {}
    fz = _freeze()
    premise = MD.c11r_fh_premise()
    quiet = lambda s: None
    real_ms = RN.memory_status
    try:
        RN.memory_status = lambda pid, cap, ps=RN.PS: ("RESOURCE_ACCOUNTING_FAILED", None)
        r = RN.certify_block(NT[0], NT[1], fz, premise, quiet)
        sem["ps_accounting_failure -> NOT_CERTIFIED/RESOURCE_ACCOUNTING_FAILED, nothing computed"] = \
            r == {"status": "NOT_CERTIFIED", "reason": "RESOURCE_ACCOUNTING_FAILED", "sub_blocks_completed": 0}
    finally:
        RN.memory_status = real_ms
    fz_mem = json.loads(json.dumps(fz))
    fz_mem["resource_caps"]["rss_kb"] = 1
    r = RN.certify_block(NT[0], NT[1], fz_mem, premise, quiet)
    sem["memory_cap -> NOT_CERTIFIED/RESOURCE_CAP_MEMORY"] = r.get("reason") == "RESOURCE_CAP_MEMORY" and r["status"] == "NOT_CERTIFIED"
    fz_wall = json.loads(json.dumps(fz))
    fz_wall["resource_caps"]["wall_seconds"] = 1
    r = RN.certify_block(NT[0], NT[1], fz_wall, premise, quiet)
    sem["wall_cap -> NOT_CERTIFIED/RESOURCE_CAP_WALL"] = r.get("reason") == "RESOURCE_CAP_WALL" and r["status"] == "NOT_CERTIFIED"
    out["attempt_semantics_production_runner_non_target"] = all(sem.values())
    # --- the launcher, end to end, with a STUB runner in scratch repositories (linked worktrees)
    L, pre = {}, {}
    with tempfile.TemporaryDirectory() as td:
        td = pathlib.Path(os.path.realpath(td))
        a = _launch_in_sandbox(td, "certified")
        L["success -> COMPLETED_CERTIFIED, sealed at once (lock, artifact, log, journal)"] = \
            _sealed_ok(a, "COMPLETED_CERTIFIED", SEALED_ALL) and a["stub_runs"] == ["certified"] and a["result"]["seal_attempts"] == 1 \
            and a["result"]["index_refreshed"] and "SEAL of the one cell-306" in a["seal_message"]
        again = _run_driver(a["_chain"], a["_sub"], "certified")
        again = _observe(a["_chain"], a["_sub"], again, a["head"], _index_state(a["_chain"]["repo"]))
        L["second launch refused (consumed; HEAD is the seal) and nothing ran"] = again["exit"] == 2 and \
            again["first_line"].startswith("REFUSE") and "consumed" in again["text"] and again["stub_runs"] == ["certified"]
        b = _launch_in_sandbox(td, "not_certified")
        L["cap/accounting outcome -> COMPLETED_NOT_CERTIFIED, sealed"] = _sealed_ok(b, "COMPLETED_NOT_CERTIFIED", SEALED_ALL) \
            and b["result"]["runner_exit"] == 3
        c = _launch_in_sandbox(td, "crash")
        L["process failure -> CONSUMED_NO_RESULT, lock sealed"] = _sealed_ok(c, "CONSUMED_NO_RESULT") and \
            "C11RD_EXECUTION.lock" in c["sealed_files"] and "C11RD_RUNS.json" not in c["sealed_files"]
        d = _launch_in_sandbox(td, "hang", signal_after_start=signal.SIGTERM)
        L["interruption (SIGTERM to the launcher, forwarded) -> CONSUMED_NO_RESULT, sealed"] = _sealed_ok(d, "CONSUMED_NO_RESULT") \
            and any(s["signal"] == "SIGTERM" and s["forwarded"] for s in d["result"]["signals_deferred"])
        e = _launch_in_sandbox(td, "refuse")
        L["runner refusal before its lock -> REFUSED_BEFORE_LOCK, consumed and sealed"] = _sealed_ok(e, "REFUSED_BEFORE_LOCK") \
            and e["sealed_files"] == ["C11RD_EXECUTION.log", "C11RD_LAUNCH_JOURNAL.jsonl"]
        envfile = td / "stub_env.json"
        hostile = dict(os.environ, **HOSTILE_ENV, PYTHONPATH="/nonexistent/py", HOME=str(td))
        f = _launch_in_sandbox(td, "env", env=hostile, extra=(str(envfile),))
        seen = json.loads(envfile.read_text()) if envfile.exists() else {"?": "?"}
        L["hostile environment sanitized for git and runner (HOME=/var/empty, global git config off)"] = \
            _sealed_ok(f, "COMPLETED_CERTIFIED") and set(seen) <= set(LA.SAFE_ENV) | set(LA.RUNTIME_ADDED) and \
            seen.get("HOME") == "/var/empty" and seen.get("GIT_CONFIG_GLOBAL") == "/dev/null"

        def refused_pre(label, want, ref_preexisting=False, **kw):
            r = _launch_in_sandbox(td, "certified", **kw)
            pre[label] = _refused_ok(r, want, ref_preexisting)
            if not pre[label]:
                pre[label + " [detail]"] = r["text"][:300]
        refused_pre("host mismatch", "qualified host",
                    mutate=lambda q: q.update(host={"grant_host": dict(q["host"]["grant_host"], hostname="elsewhere.local")}))
        refused_pre("interpreter mismatch (N-11)", "interpreter",
                    mutate=lambda q: q.update(interpreter=dict(q["interpreter"], main_image_sha256="0" * 64)))
        refused_pre("runtime file mismatch (N-11)", "runtime files",
                    mutate=lambda q: q.update(runtime_files_sha256={k: ("0" * 64 if k.endswith("/Python") else v)
                                                                    for k, v in q["runtime_files_sha256"].items()}))
        refused_pre("worktree mismatch", "worktree identity",
                    mutate=lambda q: q.update(worktree=dict(q["worktree"], canonical_path="/elsewhere")))
        refused_pre("freeze not the qualified one", "qualified freeze", mutate=lambda q: q.update(freeze_commit="f" * 40))
        refused_pre("launcher not the qualified launcher (N-1)", "not the qualified launcher",
                    mutate=lambda q: q.update(qualification_code_sha256={LA.LAUNCHER_REL: "0" * 64}))
        refused_pre("host not idle", "not idle", mutate=lambda q: q["launch_limits"].update(load1_max=-1.0))
        refused_pre("free disk below minimum (N-3)", "free disk", mutate=lambda q: q["launch_limits"].update(disk_free_min_bytes=2 ** 62))
        refused_pre("available memory below minimum (N-3)", "available memory",
                    mutate=lambda q: q["launch_limits"].update(memory_available_min_kb=2 ** 50))
        refused_pre("process table unreadable (N-3)", "process table", hooks={"ps_fail": True})
        refused_pre("not on AC power (N-10)", "AC power", mutate=lambda q: q["launch_limits"].update(require_ac_power=True),
                    hooks={"power": {"ac_power": False, "lid_open": True}})
        refused_pre("lid closed (N-10)", "lid", mutate=lambda q: q["launch_limits"].update(require_lid_open=True),
                    hooks={"power": {"ac_power": True, "lid_open": False}})
        refused_pre("runner not frozen", "not the frozen runner", mutate=lambda q: q.update(frozen_code_sha256={LA.RUNNER_REL: "0" * 64}))
        refused_pre("runner guard R1 fails in advance (N-9)", "runner R1",
                    hooks={"runner_guard_fail": ["verify_code", "REFUSE R1: planted"]})
        refused_pre("runner guard R0 fails in advance (N-9)", "runner R0",
                    hooks={"runner_guard_fail": ["verify_loaded_modules", "REFUSE R0: planted"]})
        refused_pre("runner R4: a lock committed in the past (N-9)", "runner R4",
                    pre=lambda ch: (_commit(ch["repo"], {f"{NS_REL}/evidence/runs/C11RD_EXECUTION.lock": "{}\n"}, "old lock"),
                                    _commit(ch["repo"], {f"{NS_REL}/evidence/runs/C11RD_EXECUTION.lock": None}, "rm lock"),
                                    ch.update(AR=G(ch["repo"], "rev-parse", "HEAD").stdout.strip())))
        refused_pre("already consumed", "already consumed", ref_preexisting=True,
                    pre=lambda ch: G(ch["repo"], "update-ref", LA.CONSUMED_REF, "HEAD", ""))
        refused_pre("dirty namespace", "not clean", pre=lambda ch: (ch["ns"] / "stray.txt").write_text("x"))
        refused_pre("no grant (N-3)", "no grant", pre=lambda ch: (ch["ns"] / RN.GRANT_REL).unlink())
        refused_pre("symlinked grant (N-3)", "no grant", pre=lambda ch: ((ch["ns"] / RN.GRANT_REL).rename(ch["ns"].parent / "g.json"),
                                                                        (ch["ns"] / RN.GRANT_REL).symlink_to(ch["ns"].parent / "g.json")))
        def t1(ch):                     # an alternate ACCEPTED review while the canonical one says REJECTED
            alt = f"{NS_REL}/review/ALT_QUALIFICATION_REVIEW.md"
            x = _commit(ch["repo"], {alt: "QUALIFICATION_ACCEPTED\n", f"{NS_REL}/{LA.QUAL_REVIEW_REL}": "QUALIFICATION_REJECTED\n"}, "alt")
            _regrant(ch, q_review_commit=x, q_review_path=alt)
            ch["frozen_check_T1"] = RN.grant_problems(ch["fz"], json.loads((ch["ns"] / RN.GRANT_REL).read_text()), host=ch["host"],
                                                      worktree=ch["wt"], auth_review_commit=ch["AR"], repo=ch["repo"],
                                                      ns=ch["ns"], code_dir=ch["ns"] / "code")
        refused_pre("non-canonical qualification review path (reviewer T1, N-3)", "qualification paths are not the canonical", pre=t1)

        def t4(ch):                     # another commit carrying the byte-identical freeze (the qualification commit)
            _regrant(ch, freeze_commit=ch["Q"])
        refused_pre("another freeze commit with the same freeze file (reviewer T4, N-3)", "not the qualified freeze", pre=t4)
        decoy = subprocess.Popen([sys.executable, "-I", "-S", "-B", "-c", "import time; time.sleep(60)", "decoy/c11rd_runs.py"])
        try:
            time.sleep(0.3)
            refused_pre("another runner process (reviewer T14)", "other runner")
        finally:
            decoy.kill()
            decoy.wait()
    # the already-consumed case keeps its pre-existing ref: judge it on its own terms
    L["preflight refusals create nothing and run nothing"] = all(v for k, v in pre.items() if not k.endswith("[detail]"))
    out["launcher_lifecycle_with_stub_runner"] = all(L.values())
    return {"pass": all(out.values()), "checks": out, "predecessor_matrix": matrix, "attempt_semantics": sem,
            "launcher": L, "launcher_preflight_cases": pre}


# =====================================================================================================
# Q09 R1 pre-execution review note checks (R1R.N-1 with V07 instrumented too, R1R.N-2, R1R.N-3, R1R.N-13)
# =====================================================================================================
@check
def q09_note_checks():
    out = {}
    seen, cands_ok, ka_calls = [], True, [0]
    real_pb, real_ka = V.point_box, V.kernel_at

    def pb(p, m, e, order=4):
        seen.append((p, m))
        return real_pb(p, m, e, order)

    def ka(cand, p, m, e, orders=(0, 1, 2), order=4):
        nonlocal cands_ok
        ka_calls[0] += 1
        band = [cand[k] for k in range(4)]
        cands_ok &= all(b == band[0] for b in band) and \
            cand[("A", "p")] == {i: c for (i, j), c in band[0].items() if j == 0} and \
            cand[("A", "m")] == {j: c for (i, j), c in band[0].items() if i == 0}
        return real_ka(cand, p, m, e, orders, order)
    V.point_box, V.kernel_at = pb, ka
    tests = (V.v02_kernel_of_one, V.v03_vs_c11_kernel, V.v04_finite_difference, V.v07_atom_distinction, V.v10_zero_cases,
             V.v11_symmetry, V.v12_known_signs, V.v14_tiny_drift)
    try:
        res = {t.__name__: t() for t in tests}
    finally:
        V.point_box, V.kernel_at = real_pb, real_ka
    interior_s4 = [(p, m) for p, m in seen if p > 0 and m > 0 and p + m >= 4]
    out["R1R.N-1 point_box/kernel_at: only continuous candidates, no interior s>=4, the 8 instrumented tests (V07 included) pass"] = \
        cands_ok and not interior_s4 and all(r["pass"] for r in res.values()) and len(seen) > 50
    E = V.E_NT
    boxes = CE.initial_boxes(E, E, V.FROZEN_SPLITS, 4)
    cand = V.jump_candidate()

    def ref(p, m, owner, i):
        K, C = F(1, 2), F(11, 2)
        lo_z, hi_z = m - C, C - p
        cuts = sorted(z for z in ({lo_z, hi_z, K - p, m - K} | {m - K - j for j in range(6)} | {j + K - p for j in range(6)})
                      if lo_z <= z <= hi_z)
        acc = (F(0), F(0))
        for a, b in zip(cuts, cuts[1:]):
            if b <= a:
                continue
            zm = (a + b) / 2
            if p + m < 1 and m - K < zm < K - p:
                continue
            c = V.JUMP[owner(max(F(0), p + zm - K), max(F(0), m - zm - K))]
            if i == 0:
                iv = V.iv_sub(V.c7_Phi(b + E), V.c7_Phi(a + E))
            elif i == 1:
                iv = V.iv_sub(V.c7_phi(b + E), V.c7_phi(a + E))
            else:
                iv = V.iv_sub(V.iv_scale(V.c7_phi(b + E), -(b + E)), V.iv_scale(V.c7_phi(a + E), -(a + E)))
            acc = V.iv_add(acc, V.iv_scale(iv, c))
        return acc
    rows, ok2 = [], True
    for Lv in (2, 3, 4):
        for p, m in ((F(Lv, 2), F(Lv, 2)), (F(Lv) * F(2, 3), F(Lv) / 3), (F(Lv), F(0)), (F(0), F(Lv))):
            own = CE.owning_boxes(boxes, p, m)
            bx, u = V._tiny_box_in(own[0], p, m)
            KD = KR.kernel_box(bx, [cand], orders=(0, 1, 2))
            for i in (0, 1, 2):
                enc = V.tm_at(KD[(i, 0)], u)
                up, rv = ref(p, m, V.frozen_convention_owner, i), ref(p, m, V.reversed_convention_owner, i)
                differs = not V.overlap(up, rv)
                good = V.overlap(enc, up) and (not differs or not V.overlap(enc, rv))
                ok2 &= good
                rows.append({"s": Lv, "point": [str(p), str(m)], "order": i, "reversed_differs": differs, "pass": good})
    out["R1R.N-2 kernel-level exclusion of the reversed convention, orders 0-2, s = 2, 3, 4"] = \
        ok2 and sum(r["reversed_differs"] for r in rows) >= 12
    a, b = CE.sub_blocks(NT[0], NT[1], 4)[0]
    ec = (a + b) / 2
    fp = _freeze()["frozen_parameters"]["float"]
    prop = FL.propose(float(ec), n=fp["n"], n4=fp["n4"], ns=fp["ns"], nt=fp["nt"], q=fp["q"])
    cands = [FL.exact_candidate(prop["basis"], c, bits=fp["bits"]) for c in prop["coeffs"]]
    sharp, worst_ratio = True, 0.0
    tiny = F(1, 2 ** 30)
    for (band, s0, t0, ax) in ((1, F(5, 4), F(1, 8), None), (2, F(9, 4), F(-1, 4), None), (4, F(17, 4), None, "p")):
        bx = KR.Box(band, (s0, s0 + tiny), (a, b), theta=None if ax else (t0, t0 + tiny), axis=ax, order=6)
        R = KR.residuals_box(bx, cands)
        pp, mm = ((s0, F(0)) if ax == "p" else (s0 * (1 + t0) / 2, s0 * (1 - t0) / 2))
        for ue, ee in ((-1, a), (1, b)):
            fr = V.float_residuals(prop, float(pp), float(mm), band, float(ee), float(ec))
            for k, key in enumerate(("r0", "r1", "r2")):
                lo_, hi_ = V.tm_at(R[key], (F(-1), F(-1) if not ax else F(0), F(ue)))
                width = float(hi_ - lo_)
                inside = float(lo_) - 1e-12 <= fr[k] <= float(hi_) + 1e-12
                sharp &= inside and width < 1e-3 * max(abs(fr[k]), 1e-9)
                worst_ratio = max(worst_ratio, width / max(abs(fr[k]), 1e-15))
    out["R1R.N-3 sharp endpoint containment (width < 1e-3 of the residual)"] = sharp
    P = _freeze()["frozen_parameters"]
    lo, hi = MD.cell_block()
    geo_ok, geos = True, []
    for sa, sb in CE.sub_blocks(lo, hi, P["sub_blocks"]):
        bl = CE.initial_boxes(sa, sb, P["splits"], P["tm_order"])
        geo_ok &= CE.verify_cover(bl) == [] and len(bl) == 168
        geos.append([(bb.band, bb.s, bb.theta, bb.axis) for bb in bl])
    nt_geo = [(bb.band, bb.s, bb.theta, bb.axis) for bb in CE.initial_boxes(NT[0], NT[1], P["splits"], P["tm_order"])]
    out["R1R.N-13 every per-sub-block list complete and identical in geometry"] = geo_ok and all(g == nt_geo for g in geos)
    return {"pass": all(out.values()), "checks": out, "instrumented_tests": sorted(res), "point_box_calls": len(seen),
            "kernel_at_calls": ka_calls[0], "n2_rows": len(rows), "n3_worst_width_to_residual_ratio": worst_ratio}


# =====================================================================================================
# Q10 broad leak scan (review QR1.N-4): VALUE-FREE -- renderings are compared by sha256 with the frozen set
# c11rd_validate.ORIGINAL_PATTERN_SHA256 (the renderings of the two disclosed values, >= 4 significant
# digits); the scanner proves it can fire on planted DECOY renderings through the same code path
# =====================================================================================================
DEC = re.compile(r"(?<![0-9A-Za-z.])-?([0-9]*\.[0-9]+)(?:[eE]([+-]?[0-9]{1,3}))?(?![0-9A-Za-z])")
INTSCI = re.compile(r"(?<![0-9A-Za-z.])-?([0-9]+)[eE]([+-]?[0-9]{1,3})(?![0-9A-Za-z])")
RAT = re.compile(r"(?<![0-9A-Za-z/.])-?([0-9]+)/([0-9]+)(?![0-9A-Za-z])")
SCALES = (-3, -2, -1, 0, 1, 2, 3)
LEAK_RULE = ("every decimal (plain, bare-point, scientific with a point or an integer mantissa, JSON floats) and every "
             "rational token of every namespace file and of the namespace's commit messages is taken as a value t; for "
             "each decimal shift 10^j (j = -3..3) its renderings with 4..10 significant digits (truncated, rounded half "
             "up, and Python's %.{k}g for k <= 9) are hashed and compared with the frozen set of the disclosed values' "
             "renderings (c11rd_validate.ORIGINAL_PATTERN_SHA256, built by c11rd_compare.value_patterns): a hit is exactly "
             "a >= 4-significant-digit rendering of a disclosed value at any of seven scales. No value is read, "
             "supplied or stored; positive and negative controls run the same scanner with a DECOY hash set")
DECOYS = ("3.141592653", "0.577215664")            # decoy constants (NOT the disclosed values), same shape


def _exp10(x: F) -> int:
    e = len(str(x.numerator // x.denominator)) - 1 if x >= 1 else -1
    while F(10) ** e > x:
        e -= 1
    while F(10) ** (e + 1) <= x:
        e += 1
    return e


def _digits(x: F, n: int, mode: str) -> str:
    """The first n significant digits of x > 0, truncated or rounded (half up)."""
    e = _exp10(x)
    q = x / F(10) ** (e - n + 1)
    return str(q.__floor__() if mode == "trunc" else (q + F(1, 2)).__floor__())


def _dec_str(x: F, n: int, mode: str) -> str:
    """A plain decimal rendering of x > 0 with n significant digits (truncated or rounded half up)."""
    e = _exp10(x)
    unit = e - n + 1
    N = int(_digits(x, n, mode))
    if len(str(N)) > n:                                    # rounding carried into a new decade
        return _dec_str(F(N) * F(10) ** unit, n, "trunc")
    if unit >= 0:
        return str(N * 10 ** unit)
    s = str(N).rjust(-unit + 1, "0")
    return s[:unit] + "." + s[unit:]


def _rendering_hashes(t: F) -> set:
    out = set()
    for j in SCALES:
        y = t * F(10) ** j
        for k in range(4, 11):
            g = (format(float(y), f".{k}g"),) if k <= 9 and F(1, 10 ** 300) < y < 10 ** 300 else ()
            for r in (_dec_str(y, k, "trunc"), _dec_str(y, k, "round")) + g:
                out.add(hashlib.sha256(r.encode()).hexdigest())
    return out


def _tokens(txt: str) -> list:
    toks = []
    for mnt, ex in DEC.findall(txt):
        toks.append(F(mnt if not mnt.startswith(".") else "0" + mnt) * (F(10) ** int(ex) if ex else 1))
    for mnt, ex in INTSCI.findall(txt):
        toks.append(F(int(mnt)) * F(10) ** int(ex))
    for a, b in RAT.findall(txt):
        if int(b) != 0:
            toks.append(F(int(a), int(b)))
    return [t for t in toks if t > 0]


def _broad_hashed_scan(texts: dict, hashes: frozenset) -> dict:
    hits, n_tok, memo = {}, 0, {}
    for name, txt in texts.items():
        toks = _tokens(txt)
        n_tok += len(toks)
        for t in toks:
            if t not in memo:
                memo[t] = bool(_rendering_hashes(t) & hashes)
            if memo[t]:
                hits[name] = hits.get(name, 0) + 1
    return {"hits": hits, "tokens_checked": n_tok, "distinct_values_checked": len(memo)}


def _decoy_controls() -> dict:
    """Positive (must fire) and negative (must not) plants from DECOY constants, in a temporary directory
    outside the repository, scanned by the same scanner with the decoys' hash set."""
    dh = frozenset(hashlib.sha256(x.encode()).hexdigest() for d in DECOYS for x in CM.value_patterns(d))
    pos, neg = {}, {}
    for idx, ds in enumerate(DECOYS):
        v = F(ds)
        e = _exp10(v)
        t6 = _digits(v, 6, "trunc")
        fr = v.limit_denominator(10 ** 6)
        pos.update({f"d{idx} plain truncated to 4 digits": f"a bound of {_dec_str(v, 4, 'trunc')} here\n",
                    f"d{idx} plain rounded to 4 digits": f"about {_dec_str(v, 4, 'round')}.\n",
                    f"d{idx} plain rounded to 9 digits": f"value={_dec_str(v, 9, 'round')};\n",
                    f"d{idx} scientific with a point": f"x {t6[0]}.{t6[1:]}e{e:+03d} y\n",
                    f"d{idx} scientific with an integer mantissa": f"x {t6[:5]}e{e - 4:+d} y\n",
                    f"d{idx} JSON float": json.dumps({"bound": float(_dec_str(v, 7, 'round'))}) + "\n",
                    f"d{idx} rational": f"ratio {fr.numerator}/{fr.denominator} end\n",
                    f"d{idx} percent (x 100)": f"{_dec_str(v * 100, 6, 'round')}%\n",
                    f"d{idx} bare point (x 10^-(e+1))": " " + _dec_str(v / F(10) ** (e + 1), 5, "trunc").lstrip("0") + " \n",
                    f"d{idx} thousandfold": f"{_dec_str(v * 1000, 5, 'round')} milli\n",
                    f"d{idx} negative sign": f"-{_dec_str(v, 5, 'round')}\n"})
        neg.update({f"d{idx} three significant digits": f"about {_dec_str(v, 3, 'round')} only\n",
                    f"d{idx} off by 2e-3 relative": f"a bound of {_dec_str(v * (1 + F(2, 1000)), 5, 'round')} here\n",
                    f"d{idx} digits inside a long integer": f"id 98765{_digits(v, 8, 'trunc')}4321 end\n",
                    f"d{idx} digits inside a hex digest": f"sha 0e{_digits(v, 8, 'trunc')}ab99 end\n"})
    res = {}
    with tempfile.TemporaryDirectory() as td:
        for kind, group in (("positive", pos), ("negative", neg)):
            for i, (label, text) in enumerate(group.items()):
                f = pathlib.Path(td) / f"{kind}_{i}.txt"
                f.write_text(text)
                res[label] = (kind, bool(_broad_hashed_scan({label: f.read_text()}, dh)["hits"]))
    return {"positive_fired": {k: fired for k, (kind, fired) in res.items() if kind == "positive"},
            "negative_silent": {k: not fired for k, (kind, fired) in res.items() if kind == "negative"}}


def _namespace_texts(exclude=()) -> dict:
    texts = {}
    for f in sorted(x for x in NS.rglob("*") if x.is_file() and x.resolve() not in exclude):
        try:
            texts[str(f.relative_to(NS))] = f.read_text()
        except UnicodeDecodeError:
            continue
    texts["<commit messages of the namespace since 7375b9cd>"] = G(REPO, "log", "--format=%H%n%B", f"{C11R_FINAL}..HEAD", "--", NS_REL).stdout
    return texts


@check
def q10_broad_leak_scan():
    texts = _namespace_texts()
    scan = _broad_hashed_scan(texts, V.ORIGINAL_PATTERN_SHA256)
    ctl = _decoy_controls()
    ctl_ok = all(ctl["positive_fired"].values()) and all(ctl["negative_silent"].values()) and \
        len(ctl["positive_fired"]) == 11 * len(DECOYS) and len(ctl["negative_silent"]) == 4 * len(DECOYS)
    frozen_set_ok = len(V.ORIGINAL_PATTERN_SHA256) == 17
    decoy_set = frozenset(hashlib.sha256(x.encode()).hexdigest() for d in DECOYS for x in CM.value_patterns(d))
    disjoint = not (decoy_set & V.ORIGINAL_PATTERN_SHA256)
    return {"pass": not scan["hits"] and ctl_ok and frozen_set_ok and disjoint, "files": len(texts) - 1, "commit_messages_scanned": True,
            "tokens_checked": scan["tokens_checked"], "distinct_values_checked": scan["distinct_values_checked"],
            "hits": scan["hits"], "rule": LEAK_RULE, "frozen_hash_set_size": len(V.ORIGINAL_PATTERN_SHA256),
            "controls": {"decoy_rendering_hashes_disjoint_from_the_frozen_set": disjoint, "positive_fired": ctl["positive_fired"],
                         "negative_silent": ctl["negative_silent"], "all_as_expected": ctl_ok}}


def post_write_scan(out_file: pathlib.Path) -> dict:
    """After ALL evidence is written: the frozen hashed detector (V18) and the broad hashed scan over every
    namespace file (then again including the scan file itself)."""
    out_file = out_file.resolve()
    files = sorted(f for f in NS.rglob("*") if f.is_file() and f.resolve() != out_file)
    v18 = V.v18_no_original_values_anywhere()
    hashed = V._hashed_leak_scan(files, V.ORIGINAL_PATTERN_SHA256)
    broad = _broad_hashed_scan(_namespace_texts(exclude=(out_file,)), V.ORIGINAL_PATTERN_SHA256)
    ctl = _decoy_controls()
    rec = {"POST_WRITE_LEAK_SCAN": "every file of the namespace and the namespace's commit messages, after all evidence was written",
           "files_scanned": len(files), "frozen_detector_V18": {"pass": v18.get("pass"), "files": v18.get("files_scanned")},
           "hashed_detector_hits": hashed, "broad_hashed_scan": {"hits": broad["hits"], "tokens_checked": broad["tokens_checked"]},
           "decoy_controls_as_expected": all(ctl["positive_fired"].values()) and all(ctl["negative_silent"].values()),
           "detectors": ["c11rd_validate.v18_no_original_values_anywhere (frozen)",
                         "c11rd_validate._hashed_leak_scan with ORIGINAL_PATTERN_SHA256 (frozen)",
                         "c11rd_qualify._broad_hashed_scan (value-free, seven scales, 4-10 digits)"]}
    rec["clean"] = bool(v18.get("pass")) and not hashed and not broad["hits"] and rec["decoy_controls_as_expected"]
    out_file.write_text(json.dumps(rec, indent=1, sort_keys=True) + "\n")
    all_files = sorted(f for f in NS.rglob("*") if f.is_file())
    again = V._hashed_leak_scan(all_files, V.ORIGINAL_PATTERN_SHA256)
    again_b = _broad_hashed_scan(_namespace_texts(), V.ORIGINAL_PATTERN_SHA256)
    rec["second_pass_including_this_file"] = {"files": len(all_files), "clean": not again and not again_b["hits"]}
    out_file.write_text(json.dumps(rec, indent=1, sort_keys=True) + "\n")
    return rec


# =====================================================================================================
# Q11 review QR1.B-1: the seal's preconditions refuse BEFORE consumption (and the historical reproduction)
# =====================================================================================================
R1_DRIVER = r'''
import importlib.util, json, pathlib, sys
spec = importlib.util.spec_from_file_location("c11rd_launch_r1", sys.argv[1])
LA = importlib.util.module_from_spec(spec); spec.loader.exec_module(LA)
repo, ns_rel, ar, qfile, stub, mode, marker, logdir = sys.argv[2:10]
qualified = json.loads(pathlib.Path(qfile).read_text())
cmd = [sys.executable, "-I", "-S", "-B", stub, mode, marker]
try:
    res = LA.launch(repo, ns_rel, ar, qualified, runner_cmd=cmd, runner_path=stub, log_dir=logdir)
    print("RESULT " + json.dumps(res))
except SystemExit as exc:
    print("REFUSED " + str(exc))
'''


def _r1_b1_case(td, name, pre):
    """The REJECTED launcher (qualification_r1, sha256 67714472...) on an r1-style scratch lineage, with the
    reviewer's pre-launch state -- the historical B-1 reproduction (scratch repositories and a STUB only)."""
    spec = importlib.util.spec_from_file_location("c11rd_launch_r1", REJECTED_LAUNCHER)
    L1 = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(L1)
    sub = pathlib.Path(td) / f"r1_{name}"
    sub.mkdir()
    fz_bytes = (NS / RN.FREEZE_REL).read_bytes()
    fz = json.loads(fz_bytes)
    repo = _repo(sub, "chain")
    ns = repo / NS_REL
    stub = ns / "code" / "stub_runner.py"
    F0 = _commit(repo, {f"{NS_REL}/{RN.FREEZE_REL}": fz_bytes, f"{NS_REL}/code/stub_runner.py": STUB}, "freeze")
    wt, host = RN.worktree_identity(repo=repo), RN.host_identity()
    qualified = {"freeze_commit": F0, "host": {"grant_host": host}, "interpreter": L1.interpreter_identity(), "worktree": wt,
                 "launch_limits": {"load1_max": 1000.0, "disk_free_min_bytes": 0, "memory_available_min_kb": 0},
                 "frozen_code_sha256": {L1.RUNNER_REL: sha256_file(stub)}}
    Q = _commit(repo, {f"{NS_REL}/{L1.QUAL_ARTIFACT_REL}": json.dumps(qualified) + "\n"}, "qualification")
    QR = _commit(repo, {f"{NS_REL}/{L1.QUAL_REVIEW_REL}": "QUALIFICATION_ACCEPTED\n"}, "qualification review")
    lo, hi = MD.cell_block()
    grant = {"campaign": "C11RD", "decision": "ALLOW", "target": {"cell": 306, "e_lo": str(lo), "e_hi": str(hi), "constants": ["D1", "D2"]},
             "max_executions": 1, "freeze_commit": F0, "freeze_sha256": sha256_bytes(fz_bytes), "code_sha256": fz["code_sha256"],
             "input_bindings": fz["input_bindings"], "host": host, "worktree": wt,
             "qualification": {"commit": Q, "artifact_path": f"{NS_REL}/{L1.QUAL_ARTIFACT_REL}",
                               "artifact_blob": G(repo, "rev-parse", f"{Q}:{NS_REL}/{L1.QUAL_ARTIFACT_REL}").stdout.strip(),
                               "review_commit": QR, "review_path": f"{NS_REL}/{L1.QUAL_REVIEW_REL}"}}
    _commit(repo, {f"{NS_REL}/{RN.GRANT_REL}": json.dumps(grant, indent=1, sort_keys=True) + "\n"}, "grant")
    AR = _commit(repo, {f"{NS_REL}/{RN.AUTH_REVIEW_REL}": "AUTHORIZATION_ACCEPTED\n"}, "authorization review")
    pre(repo)
    qfile, drv, marker = sub / "q.json", sub / "driver_r1.py", sub / "started.txt"
    qfile.write_text(json.dumps(qualified))
    drv.write_text(R1_DRIVER)
    p = subprocess.run([sys.executable, "-I", "-S", "-B", str(drv), str(REJECTED_LAUNCHER), str(repo), NS_REL, AR, str(qfile),
                        str(stub), "certified", str(marker), str(sub / "logs")], capture_output=True, text=True, timeout=300)
    line = next((ln for ln in p.stdout.splitlines() if ln.startswith(("RESULT ", "REFUSED "))), "")
    runs = ns / "evidence/runs"
    return {"sealed": line.startswith("RESULT "), "message": line[8:180] if line.startswith("REFUSED ") else line[:120],
            "stub_ran": marker.exists() and marker.read_text().split() == ["certified"],
            "consumed": G(repo, "rev-parse", "--verify", "-q", L1.CONSUMED_REF).stdout.strip() == AR,
            "head_unmoved": G(repo, "rev-parse", "HEAD").stdout.strip() == AR,
            "runs_left_on_disk": sorted(f.name for f in runs.iterdir()) if runs.is_dir() else []}


@check
def q11_b1_seal_preconditions():
    out, cases = {}, {}
    with tempfile.TemporaryDirectory() as td:
        td = pathlib.Path(os.path.realpath(td))

        def stage_outside(repo):
            (pathlib.Path(repo) / "elsewhere").mkdir(exist_ok=True)
            (pathlib.Path(repo) / "elsewhere/note.txt").write_text("staged before the launch\n")
            G(repo, "add", "-f", "elsewhere/note.txt")
        hist = {"T2 (rejected launcher)": _r1_b1_case(td, "T2", stage_outside),
                "T11 (rejected launcher)": _r1_b1_case(td, "T11", lambda repo: (pathlib.Path(repo) / ".git/index.lock").write_text(""))}
        out["historical: the REJECTED launcher reproduces B-1 (T2, T11: consumed, ran, NOT sealed; T11 reported under REFUSE)"] = \
            all(not h["sealed"] and h["stub_ran"] and h["consumed"] and h["head_unmoved"] and "C11RD_RUNS.json" in h["runs_left_on_disk"]
                for h in hist.values()) and "unexpected staged paths" in hist["T2 (rejected launcher)"]["message"] \
            and hist["T11 (rejected launcher)"]["message"].startswith("REFUSE: git add -f failed")

        def case(label, want, pre, keep=None):
            r = _launch_in_sandbox(td, "certified", pre=pre)
            ok = _refused_ok(r, want) and (keep is None or keep(r["_chain"]))
            cases[label] = ok
            if not ok:
                cases[label + " [detail]"] = r["text"][:400]
        case("T2 (repaired): a file staged outside the namespace", "index differs from HEAD",
             lambda ch: stage_outside(ch["repo"]),
             keep=lambda ch: G(ch["repo"], "diff", "--cached", "--name-only").stdout.split() == ["elsewhere/note.txt"])
        case("T11 (repaired): a stale index.lock of the launch worktree", "git lock files present",
             lambda ch: (ch["gitdir"] / "index.lock").write_text(""), keep=lambda ch: (ch["gitdir"] / "index.lock").exists())
        case("a stale index.lock of the common dir (the main worktree)", "git lock files present",
             lambda ch: (ch["common"] / "index.lock").write_text(""))
        case("a stale lock of the launch branch ref", "git lock files present",
             lambda ch: (ch["common"] / (SANDBOX_BRANCH + ".lock")).write_text(""))
        case("a stale packed-refs.lock", "git lock files present", lambda ch: (ch["common"] / "packed-refs.lock").write_text(""))
        case("a stale HEAD.lock of the launch worktree", "git lock files present", lambda ch: (ch["gitdir"] / "HEAD.lock").write_text(""))
        case("a stale lock of the consumed ref", "git lock files present",
             lambda ch: ((ch["common"] / "refs/c11rd").mkdir(parents=True, exist_ok=True),
                         (ch["common"] / (LA.CONSUMED_REF + ".lock")).write_text("")))
        case("a merge in progress", "operation is in progress", lambda ch: (ch["gitdir"] / "MERGE_HEAD").write_text(ch["F0"] + "\n"))
        case("a cherry-pick in progress", "operation is in progress",
             lambda ch: (ch["gitdir"] / "CHERRY_PICK_HEAD").write_text(ch["F0"] + "\n"))
        case("a rebase in progress", "operation is in progress", lambda ch: (ch["gitdir"] / "rebase-merge").mkdir())
        case("a detached HEAD (at the authorization commit)", "launch branch", lambda ch: G(ch["repo"], "checkout", "-q", "--detach"))
        case("HEAD after the authorization commit (N-1)", "HEAD is not the authorization review commit",
             lambda ch: _commit(ch["repo"], {"late.txt": "late\n"}, "a commit after the authorization"))
        case("an unmerged index entry", "unmerged",
             lambda ch: subprocess.run(["/usr/bin/git", "-C", str(ch["repo"]), "update-index", "--index-info"], env=SAFE_GIT_ENV,
                                       input=f"100644 {G(ch['repo'], 'rev-parse', 'HEAD:README').stdout.strip()} 1\telsewhere/u.txt\n",
                                       text=True, capture_output=True))
        case("no explicit user.email", "user.email", lambda ch: G(ch["main"], "config", "--unset", "user.email"))
        case("sparse checkout on", "sparse", lambda ch: G(ch["repo"], "config", "core.sparseCheckout", "true"))
        case("a git attribute on the seal paths", "attributes",
             lambda ch: ((ch["common"] / "info").mkdir(exist_ok=True), (ch["common"] / "info/attributes").write_text("*.json filter=evil\n")))
        case("an unstaged modification outside the namespace", "worktree is not clean",
             lambda ch: (ch["repo"] / "README").write_text("changed\n"))
        case("an untracked file outside the namespace", "worktree is not clean", lambda ch: (ch["repo"] / "untracked.txt").write_text("x\n"))
        depth = {}
        d2 = _launch_in_sandbox(td, "certified", pre=lambda ch: stage_outside(ch["repo"]), hooks={"no_seal_safety": True})
        depth["T2 with the preconditions disabled: the private-index seal holds only evidence/runs/, the foreign entry stays staged"] = \
            _sealed_ok(d2, "COMPLETED_CERTIFIED", SEALED_ALL) and \
            G(d2["_chain"]["repo"], "diff", "--cached", "--name-only").stdout.split() == ["elsewhere/note.txt"]
        d11 = _launch_in_sandbox(td, "certified", pre=lambda ch: (ch["gitdir"] / "index.lock").write_text(""),
                                 hooks={"no_seal_safety": True, "delays": FAST_DELAYS})
        depth["T11 with the preconditions disabled: the seal lands anyway (index refresh reported pending)"] = \
            d11["exit"] == 0 and bool(d11["result"]) and d11.get("seal_parent_is_start_head") and d11.get("seal_only_runs_dir") \
            and d11["result"]["index_refreshed"] is False
    out["B-1 regressions and every seal-precondition state refuse before consumption (no ref, no runner, index as found)"] = \
        all(v for k, v in cases.items() if not k.endswith("[detail]"))
    out["defense in depth: even with the preconditions disabled, T2 and T11 are sealed correctly by the private-index seal"] = \
        all(depth.values())
    order_src = (LAUNCHER).read_text()
    fn = next(n for n in ast.parse(order_src).body if isinstance(n, ast.FunctionDef) and n.name == "launch")
    calls = sorted((n.lineno, n.func.id) for n in ast.walk(fn) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name))
    first = {}
    for ln, nm in calls:
        first.setdefault(nm, ln)
    out["ordering invariant in launch(): preflight < sleep prevention < final gate < consume < run_once < seal"] = \
        first["preflight"] < first["start_sleep_prevention"] < first["final_gate_problems"] < first["consume"] < first["run_once"] < first["seal"]
    return {"pass": all(out.values()), "checks": out, "historical_reproduction": hist, "cases": cases, "defense_in_depth": depth}


# =====================================================================================================
# Q12 post-consumption seal failure: bounded retry, the UNSEALED state, the seal-only recovery, launcher death
# =====================================================================================================
def _journal(sub, ar):
    f = sub / "logs" / f"C11RD_LAUNCH_JOURNAL_{ar[:12]}.jsonl"
    return [json.loads(ln) for ln in f.read_text().splitlines()] if f.exists() else []


def _seconds(t):
    return time.mktime(time.strptime(t, "%Y-%m-%dT%H:%M:%SZ"))


def _runner_processes_alive():
    ps = subprocess.run(["/bin/ps", "-A", "-o", "command="], capture_output=True, text=True).stdout
    return [ln for ln in ps.splitlines() if "/code/c11rd_runs.py" in ln and "sb_" in ln]


@check
def q12_post_consumption_seal():
    out, P = {}, {}
    with tempfile.TemporaryDirectory() as td:
        td = pathlib.Path(os.path.realpath(td))
        r1 = _launch_in_sandbox(td, "branch_lock_transient", extra=("0.8",), hooks={"delays": [0.5] * 6})
        P["P1 transient lock contention: only the seal is retried and it lands; the runner ran once"] = \
            _sealed_ok(r1, "COMPLETED_CERTIFIED", SEALED_ALL) and r1["result"]["seal_attempts"] >= 2 and \
            r1["stub_runs"] == ["branch_lock_transient"] and not r1["result"]["attempt_log"][0]["ok"] and \
            not r1["result"]["attempt_log"][0]["permanent"]
        r2 = _launch_in_sandbox(td, "branch_lock_permanent", hooks={"delays": FAST_DELAYS})
        ch, sub = r2["_chain"], r2["_sub"]
        rep_file = sub / "logs" / f"C11RD_UNSEALED_{ch['AR'][:12]}.json"
        P["P2 persistent lock: bounded attempts (1 + 6), then EXECUTION CONSUMED — RESULT UNSEALED (exit 4, not REFUSE)"] = \
            _unsealed_ok(r2) and r2["unsealed"]["seal_attempts"] == 7 and not r2["unsealed"]["permanent"] and \
            r2["head"] == r2["head0"] and {"C11RD_EXECUTION.lock", "C11RD_RUNS.json", "C11RD_EXECUTION.log"} <= set(r2["runs_on_disk"]) \
            and r2["index_unchanged"] and rep_file.exists() and (ch["common"] / (SANDBOX_BRANCH + ".lock")).exists() \
            and "--seal-only" in r2["text"] and "never permits a new D1/D2 execution" in r2["text"]
        idx_before = _index_state(ch["repo"])
        early = _observe(ch, sub, _run_driver(ch, sub, "certified", hooks={"seal_only": True, "delays": FAST_DELAYS}),
                         r2["head0"], idx_before)
        P["seal-only while the blocking lock persists: still UNSEALED, runner not started"] = early["exit"] == 4 and \
            early["first_line"] == LA.UNSEALED_BANNER and early["stub_runs"] == ["branch_lock_permanent"]
        (ch["common"] / (SANDBOX_BRANCH + ".lock")).unlink()
        rec = _observe(ch, sub, _run_driver(ch, sub, "certified", hooks={"seal_only": True}), r2["head0"], _index_state(ch["repo"]))
        P["seal-only recovery after clearing the condition: sealed on the start HEAD, the runner NOT started again"] = \
            rec["exit"] == 0 and bool(rec["result"]) and rec["result"]["recovery"] is True and \
            rec["result"]["outcome"] == "COMPLETED_CERTIFIED" and rec.get("seal_parent_is_start_head") and \
            rec.get("sealed_files") == sorted(SEALED_ALL) and rec["stub_runs"] == ["branch_lock_permanent"] and \
            rec.get("namespace_clean_after_seal") and "SEAL-ONLY RECOVERY" in rec.get("seal_message", "")
        again = _run_driver(ch, sub, "certified", hooks={"seal_only": True})
        P["a second seal-only is refused as SEAL-ONLY REFUSED (exit 5), nothing changed"] = again["exit"] == 5 and \
            again["first_line"].startswith("SEAL-ONLY REFUSED") and "already" in again["text"]
        relaunch = _observe(ch, sub, _run_driver(ch, sub, "certified"), rec["head"], _index_state(ch["repo"]))
        P["a new launch after the recovery is refused and runs nothing"] = relaunch["exit"] == 2 and \
            relaunch["first_line"].startswith("REFUSE") and relaunch["stub_runs"] == ["branch_lock_permanent"]
        fresh = _launch_in_sandbox(td, "certified", hooks={"seal_only": True})
        P["seal-only on an unconsumed lineage: SEAL-ONLY REFUSED, nothing created"] = fresh["exit"] == 5 and \
            "not consumed" in fresh["text"] and fresh["consumed_ref"] == "" and fresh["stub_runs"] == [] and fresh["runs_on_disk"] == []
        r3 = _launch_in_sandbox(td, "move_head", hooks={"delays": FAST_DELAYS})
        P["P3 the branch moved during the run: permanent, UNSEALED after ONE attempt (no retry)"] = _unsealed_ok(r3) and \
            r3["unsealed"]["permanent"] and r3["unsealed"]["seal_attempts"] == 1 and r3["head"] != r3["head0"]
        r4 = _launch_in_sandbox(td, "index_lock", hooks={"delays": FAST_DELAYS})
        P["P4 a stale index.lock appearing during the run: the private-index seal lands; the index refresh is reported pending"] = \
            r4["exit"] == 0 and bool(r4["result"]) and r4["result"]["outcome"] == "COMPLETED_CERTIFIED" and \
            r4.get("seal_parent_is_start_head") and r4.get("seal_only_runs_dir") and r4["result"]["index_refreshed"] is False and \
            (r4["_chain"]["gitdir"] / "index.lock").exists()
        r5 = _launch_in_sandbox(td, "stage_foreign")
        P["P5 a file staged elsewhere during the run: the seal holds only evidence/runs/, the foreign entry stays staged"] = \
            _sealed_ok(r5, "COMPLETED_CERTIFIED", SEALED_ALL) and \
            G(r5["_chain"]["repo"], "diff", "--cached", "--name-only").stdout.split() == ["elsewhere/late.txt"]
        r6 = _launch_in_sandbox(td, "branch_lock_permanent")
        j = _journal(r6["_sub"], r6["_chain"]["AR"])
        t_exit = next((_seconds(e["t"]) for e in j if e["event"] == "runner_exited"), None)
        t_uns = next((_seconds(e["t"]) for e in j if e["event"] == "unsealed"), None)
        elapsed = (t_uns - t_exit) if t_exit is not None and t_uns is not None else None
        P["P6 the PRODUCTION policy (1, 2, 4, 8, 16, 32 s): 7 attempts, UNSEALED about 63 s after the runner exited"] = \
            _unsealed_ok(r6) and r6["unsealed"]["seal_attempts"] == 7 and r6["unsealed"]["policy_delays_seconds"] == [1, 2, 4, 8, 16, 32] \
            and elapsed is not None and 62 <= elapsed <= 90
        r7 = _launch_in_sandbox(td, "slow", extra=("4",), kill_after_start=True)
        ch7, sub7 = r7["_chain"], r7["_sub"]
        while_alive = _run_driver(ch7, sub7, "certified", hooks={"seal_only": True})
        t0 = time.time()
        while _runner_processes_alive() and time.time() - t0 < 60:
            time.sleep(0.2)
        rec7 = _observe(ch7, sub7, _run_driver(ch7, sub7, "certified", hooks={"seal_only": True}), r7["head0"], _index_state(ch7["repo"]))
        P["N-8 launcher death (SIGKILL) mid-run: consumed, nothing sealed; seal-only refuses while the runner lives, then seals only"] = \
            r7["exit"] is None and r7["consumed_ref"] == r7["head0"] and r7["head"] == r7["head0"] and \
            while_alive["exit"] == 5 and "runner process may still be running" in while_alive["text"] and \
            rec7["exit"] == 0 and rec7["result"]["outcome"] == "RECOVERED_ARTIFACT_AND_LOCK" and rec7.get("seal_parent_is_start_head") \
            and rec7["stub_runs"] == ["slow"] and "C11RD_RUNS.json" in rec7.get("sealed_files", [])
        out["post-consumption seal failure, retry, UNSEALED state and seal-only recovery behave as specified"] = all(P.values())
    src = LAUNCHER.read_text()
    tree = ast.parse(src)
    so = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "seal_only")
    so_calls = {n.func.id for n in ast.walk(so) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}
    out["seal_only() cannot start the runner (no run_once, no Popen, no runner command)"] = "run_once" not in so_calls and \
        "Popen" not in ast.unparse(so) and "--mode" not in ast.unparse(so)
    sl = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "seal")
    out["seal() never starts the runner and never reads the runs artifact's content"] = "run_once" not in ast.unparse(sl) and \
        "read_text" not in ast.unparse(sl) and "json.load" not in ast.unparse(sl)
    return {"pass": all(out.values()), "checks": out, "cases": P, "p6_elapsed_seconds": elapsed}


# =====================================================================================================
# Q13 signals around the critical transitions (review QR1.N-8)
# =====================================================================================================
@check
def q13_signals():
    S = {}
    with tempfile.TemporaryDirectory() as td:
        td = pathlib.Path(os.path.realpath(td))
        names = ["SIGINT", "SIGTERM", "SIGHUP", "SIGQUIT", "SIGTSTP"]
        s1 = _launch_in_sandbox(td, "certified", hooks={"signals_before_seal_ref_update": names})
        S["S1 INT, TERM, HUP, QUIT, TSTP at the seal's ref update: deferred and recorded, the seal lands"] = \
            _sealed_ok(s1, "COMPLETED_CERTIFIED", SEALED_ALL) and \
            [d["signal"] for d in s1["result"]["signals_deferred"]] == names and \
            all(d["phase"] == "sealing" and not d["forwarded"] for d in s1["result"]["signals_deferred"])
        s2 = _launch_in_sandbox(td, "certified", hooks={"signals_before_seal_ref_update": ["GROUP_SIGINT"], "pgid_probe": True},
                                new_session=True)
        S["S2 SIGINT to the launcher's whole process group during the seal: the seal lands; git children run in their own group"] = \
            _sealed_ok(s2, "COMPLETED_CERTIFIED", SEALED_ALL) and [d["signal"] for d in s2["result"]["signals_deferred"]] == ["SIGINT"] \
            and bool(s2["pgid"]) and s2["pgid"]["child"] != s2["pgid"]["launcher"]
        s3 = _launch_in_sandbox(td, "certified", hooks={"signals_after_consume": ["SIGINT"]})
        S["S3 SIGINT right after consumption: the runner is NOT started; consumed; log and journal sealed"] = \
            _sealed_ok(s3, "CONSUMED_RUNNER_NOT_STARTED", ["C11RD_EXECUTION.log", "C11RD_LAUNCH_JOURNAL.jsonl"]) and s3["stub_runs"] == []
        s4 = _launch_in_sandbox(td, "certified", hooks={"signals_in_gate": ["SIGTERM"]})
        S["S4 SIGTERM in the final gate (before consumption): REFUSE, nothing consumed, nothing run"] = \
            _refused_ok(s4, "signal(s) received before consumption")
        s5 = _launch_in_sandbox(td, "hang", signal_after_start="GROUP_SIGINT")
        S["S5 terminal Ctrl-C (SIGINT to the process group) during the run: CONSUMED_NO_RESULT, sealed"] = \
            _sealed_ok(s5, "CONSUMED_NO_RESULT")
        s6 = _launch_in_sandbox(td, "hang", signal_after_start=signal.SIGINT, hooks={"signals_before_seal_ref_update": ["SIGINT"]})
        d6 = s6["result"]["signals_deferred"] if s6["result"] else []
        S["S6 a first SIGINT during the run (forwarded) and a second during the seal (deferred): sealed"] = \
            _sealed_ok(s6, "CONSUMED_NO_RESULT") and [(d["phase"], d["forwarded"]) for d in d6] == [("running", True), ("sealing", False)]
    return {"pass": all(S.values()), "checks": S}


# =====================================================================================================
# Q14 the entry point main() on the REAL repository (refusal paths only) and grant commit-id validation
# =====================================================================================================
def _snapshot_real():
    common = pathlib.Path(G(REPO, "rev-parse", "--path-format=absolute", "--git-common-dir").stdout.strip())
    return {"namespace_status": G(REPO, "status", "--porcelain", "--ignored", "--untracked-files=all", "--", NS_REL).stdout,
            "refs_c11rd": G(REPO, "for-each-ref", "refs/c11rd").stdout, "log_dir": (common / LA.LOG_DIR_NAME).exists(),
            "pycache": sorted(str(p) for p in NS.rglob("__pycache__")), "HEAD": G(REPO, "rev-parse", "HEAD").stdout}


@check
def q14_entry_point():
    E = {}
    Z = "0" * 40
    before = _snapshot_real()
    with tempfile.TemporaryDirectory() as td:
        td = pathlib.Path(os.path.realpath(td))

        def main_run(args, env, flags=True):
            r = subprocess.run([sys.executable, *(["-I", "-S", "-B"] if flags else []), str(LAUNCHER), *args], capture_output=True,
                               text=True, env=env, cwd=str(td), timeout=300)
            return r.returncode, r.stdout.strip()
        hostile = dict(HOSTILE_ENV, PYTHONPATH=str(td), HOME=str(td), PYTHONINSPECT="1", GIT_TRACE="1", EXTRA="x")
        E["E1 hostile environment, no flags: one sanitizing re-exec, then REFUSE L2 no grant"] = \
            main_run(["--authorization-review-commit", Z, "--preflight-only"], hostile, flags=False) == \
            (2, "REFUSE L2: no grant at config/C11RD_GRANT.json (or it is a symlink)")
        rc, so = main_run(["--authorization-review-commit", Z], dict(LA.SAFE_ENV, **{LA.MARKER: "1", "EXTRA": "x"}))
        E["E2 preset marker with an extra variable: REFUSE L1"] = rc == 2 and so.startswith("REFUSE L1") and "EXTRA" in so
        rc, so = main_run(["--authorization-review-commit", Z], dict(LA.SAFE_ENV, **{LA.MARKER: "1"}), flags=False)
        E["E3 (N-2) preset marker, exact environment, WITHOUT -I -S -B: REFUSE L1 before any frozen import"] = \
            rc == 2 and so.startswith("REFUSE L1") and "-I -S -B" in so
        E["E4 the exact sanitized state without the marker proceeds (no re-exec needed): REFUSE L2 no grant"] = \
            main_run(["--authorization-review-commit", Z], dict(LA.SAFE_ENV)) == (2, "REFUSE L2: no grant at config/C11RD_GRANT.json (or it is a symlink)")
        pwn = td / "pwn"
        rc, so = main_run([f"--authorization-review-commit=--output={pwn}"], dict(LA.SAFE_ENV))
        E["E5 (N-14) an option-shaped commit id is refused before any git call"] = rc == 2 and "40-hex" in so and not pwn.exists()
        E["E6 --seal-only without a grant: REFUSE L2 no grant (nothing sealed or created)"] = \
            main_run(["--authorization-review-commit", Z, "--seal-only"], dict(LA.SAFE_ENV))[0] == 2
        # grant commit ids (sandbox): an option-shaped id never reaches git
        pw1, pw2 = td / "pwn_q", td / "pwn_f"

        def bad_q(ch):
            _regrant(ch, q_commit=f"--output={pw1}")

        def bad_f(ch):
            _regrant(ch, freeze_commit=f"--output={pw2}")
        r = _launch_in_sandbox(td, "certified", pre=bad_q)
        E["E7 (N-14) grant qualification.commit '--output=...': REFUSE, no file written"] = _refused_ok(r, "40-hex") and not pw1.exists()
        r = _launch_in_sandbox(td, "certified", pre=bad_f)
        E["E8 (N-14) grant freeze_commit '--output=...': REFUSE, no file written"] = _refused_ok(r, "40-hex") and not pw2.exists()
        r = _launch_in_sandbox(td, "certified", hooks={"ar": "HEAD"})
        E["E9 (N-14) a symbolic authorization commit ('HEAD') is refused"] = _refused_ok(r, "40-hex")
    after = _snapshot_real()
    E["the real repository is unchanged (namespace status, refs/c11rd, no log dir, no __pycache__, HEAD)"] = before == after and \
        before["refs_c11rd"] == "" and not before["log_dir"] and before["pycache"] == []
    src = LAUNCHER.read_text()
    mfn = next(n for n in ast.parse(src).body if isinstance(n, ast.FunctionDef) and n.name == "main")
    lists = [ast.unparse(n) for n in ast.walk(mfn) if isinstance(n, ast.List)]
    E["main() builds exactly: sys.executable -I -S -B <ns>/code/c11rd_runs.py --mode real --authorization-review-commit <sha>"] = \
        "[sys.executable, '-I', '-S', '-B', str(NS / RUNNER_REL), '--mode', 'real', '--authorization-review-commit', " \
        "a.authorization_review_commit]" in lists
    first_stmt = mfn.body[1] if len(mfn.body) > 1 else None
    E["main() evaluates the sanitized state before anything else (N-2)"] = "sanitized_state_problems()" in ast.unparse(first_stmt)
    return {"pass": all(E.values()), "checks": E}


# =====================================================================================================
def run(out_dir: pathlib.Path) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    res = {}

    def do(fn, *a):
        t0 = time.time()
        try:
            r = fn(*a)
        except Exception as exc:                              # noqa: BLE001 -- a crashing check FAILS, with its cause
            import traceback
            r = {"pass": False, "crash": f"{type(exc).__name__}: {exc}", "traceback": traceback.format_exc()[-3000:]}
        res[fn.__name__] = dict(r, seconds=round(time.time() - t0, 1))
        print(f"  {'PASS' if res[fn.__name__]['pass'] else 'FAIL'}  {fn.__name__}  ({res[fn.__name__]['seconds']} s)", flush=True)
    for fn in (q01_entry_identity, q02_history_cleanliness, q03_scientific_object, q04_hashes):
        do(fn)
    do(q05_validation, out_dir)
    for fn in (q06_host_runtime, q07_git_history_hardening, q08_execution_lifecycle, q09_note_checks):
        do(fn)
    do(q10_broad_leak_scan)
    for fn in (q11_b1_seal_preconditions, q12_post_consumption_seal, q13_signals, q14_entry_point):
        do(fn)
    for v in res.values():
        v.pop("_chain", None)
    passed = [k for k, v in res.items() if v.get("pass") is True]
    return {"schema": "c11rd.qualification.checks.r1q_r1", "checks": res, "passed": len(passed), "total": len(res),
            "QUALIFICATION_CHECKS": "PASS" if len(passed) == len(res) else "FAIL",
            "tool_sha256": sha256_file(__file__), "launcher_sha256": sha256_file(LAUNCHER)}


# =====================================================================================================
# note dispositions -- UNIQUE identifiers (review QR1.N-12): R1R = the C11RD-R1 pre-execution review
# (3c1eff11); QR1 = the rejected qualification's review (89330534); PRED = the predecessor review (663f8fe7)
# =====================================================================================================
NOTE_ID_MAP = {"R1R": "C11RD-R1 pre-execution review, preserved at 3c1eff11 (READY_TO_QUALIFY)",
               "QR1": "qualification review of 3addf9d3, preserved at 89330534 (QUALIFICATION_REJECTED)",
               "PRED": "predecessor pre-execution review, preserved at 663f8fe7 (NOT_READY)",
               "aliases": {"PRED.N-7": "R1R.N-11 (idle host and sleep prevention; the rejected artifact's "
                                       "authorization_requirements[2] and doc section 3 say 'N-7' meaning PRED.N-7)"}}

NOTE_DISPOSITIONS = {
    "R1R.N-1": ("QUALIFIED", "validation helper point_box reads bands lower-closed; Q09 instruments point_box and kernel_at over 8 "
                "validation tests INCLUDING V07 (QR1.N-5): every call uses a globally continuous candidate or none and no interior "
                "point with s >= 4; c11rd_validate.py is frozen and not edited (erratum recorded)"),
    "R1R.N-2": ("HARDENED_OUTSIDE_FROZEN_SCIENCE", "Q09: kernel-level exclusion of the reversed convention, Khat orders 0-2, s = 2, 3, 4"),
    "R1R.N-3": ("HARDENED_OUTSIDE_FROZEN_SCIENCE", "Q09: sharp endpoint containment, width < 1e-3 of the residual at u_e = -1, +1"),
    "R1R.N-4": ("ACCEPTED_LIMITATION", "nontarget mode trusts the on-disk freeze (changing it needs a new freeze); rule: no rehearsal "
                "after this qualification except on explicit instruction, from a clean tree with the committed freeze; the governed "
                "target path binds the freeze at the freeze commit (R2)"),
    "R1R.N-5": ("HARDENED_OUTSIDE_FROZEN_SCIENCE", "the qualified launcher is the only permitted entry; the sanitized state now also fixes "
                "HOME=/var/empty, GIT_CONFIG_GLOBAL=/dev/null, GIT_CONFIG_NOSYSTEM, GIT_ATTR_NOSYSTEM, core.hooksPath=/dev/null "
                "(Q06-Q08, Q14); residual ACCEPTED_LIMITATION: deliberate forgery by a trusted operator, and interpreter start-up "
                "before any program check when the launcher is started without -I -S -B"),
    "R1R.N-6": ("HARDENED_OUTSIDE_FROZEN_SCIENCE", "consumed ref in the COMMON git dir before the run, and an immediate seal that no "
                "longer depends on the shared index (private index + compare-and-swap ref update, bounded retry, distinct UNSEALED "
                "state, seal-only recovery): QR1.B-1 repaired (Q11-Q13)"),
    "R1R.N-7": ("ACCEPTED_LIMITATION", "reachable history only (inherent; the freeze says 'reachable history')"),
    "R1R.N-8": ("HARDENED_OUTSIDE_FROZEN_SCIENCE", "canonical qualification paths and the exact freeze commit enforced by the launcher; "
                "Q08 now tests it (reviewer T1 and T4: the frozen check alone accepts, the launcher refuses)"),
    "R1R.N-9": ("ACCEPTED_LIMITATION", "stale 'R0-R6' wording and the JSON FORBIDDEN list without the band clause cannot be edited "
                "without a new freeze; errata carried; the convention is immutable through the frozen hashes and guard R6"),
    "R1R.N-10": ("QUALIFIED", "Q10 repaired (QR1.N-4): value-free hashed rendering scan at seven scales, 4-10 digits, with decoy "
                 "positive/negative controls through the same code path: clean"),
    "R1R.N-11": ("QUALIFIED", "fail-closed kept: a failed process-table read ends the run NOT_CERTIFIED and consumes it; Q06 500/500 "
                 "reads; the launcher pre-checks the table and requires an idle host, AC power, open lid and verified sleep "
                 "prevention (= PRED.N-7)"),
    "R1R.N-12": ("HARDENED_OUTSIDE_FROZEN_SCIENCE", "Q08 single-field deviation matrix (platform, input_bindings, git_common_dir, "
                 "QUALIFICATION_REJECTED, ancestor freeze commit with a different freeze file): all refused"),
    "R1R.N-13": ("QUALIFIED", "Q09: each per-sub-block box list is complete (verify_cover) and identical in geometry to the NT list"),
    "QR1.B-1": ("HARDENED_OUTSIDE_FROZEN_SCIENCE", "REPAIRED in the launcher only. Before consumption the preflight AND a final gate "
                "refuse unless HEAD is the authorization commit on the qualified branch, the index equals HEAD with no unmerged entry, "
                "the worktree and namespace are clean, no *.lock exists in the worktree git dir, the common dir or refs/, no "
                "merge/rebase/cherry-pick/revert/bisect is in progress, the ref backend is files, an explicit repo-local identity "
                "exists, sparse checkout is off, no attribute applies to the seal paths and the object store is writable. The seal "
                "itself uses a private index and a compare-and-swap ref update, retries transient failures under a bounded policy "
                "(1+6 attempts in 63 s, seal steps only), and otherwise ends in 'EXECUTION CONSUMED — RESULT UNSEALED' (exit 4, "
                "never REFUSE) whose only continuation is --seal-only. Q11: the rejected launcher reproduces T2/T11, the repaired one "
                "refuses both and 16 more states before consumption; Q12/Q13: post-consumption failure, retry, UNSEALED, recovery, "
                "signals, launcher death"),
    "QR1.N-1": ("HARDENED_OUTSIDE_FROZEN_SCIENCE", "the launcher checks its own sha256 against this artifact and, in main(), its blob "
                "at HEAD; HEAD must equal the authorization review commit (Q08, Q11)"),
    "QR1.N-2": ("HARDENED_OUTSIDE_FROZEN_SCIENCE", "main() first evaluates the sanitized-state predicate (flags, pycache prefix, exact "
                "environment); a preset marker without that state refuses (Q14 E2, E3; no __pycache__ written)"),
    "QR1.N-3": ("HARDENED_OUTSIDE_FROZEN_SCIENCE", "Q08 now tests no grant, symlinked grant, disk, memory, process table, AC power, lid, "
                "canonical paths (T1), another freeze commit (T4), a decoy runner (T14), runner guards; every sandbox launch loads the "
                "qualification through load_qualified; Q14 drives main() (L1 re-exec, refusals)"),
    "QR1.N-4": ("HARDENED_OUTSIDE_FROZEN_SCIENCE", "Q10 rebuilt: value-free, >= 4-digit renderings at seven scales against the frozen "
                "hash set; 22 planted decoy renderings fire and 8 decoy non-renderings stay silent through the same scanner"),
    "QR1.N-5": ("HARDENED_OUTSIDE_FROZEN_SCIENCE", "Q09 instruments V07 as well and reports the instrumented tests and call counts"),
    "QR1.N-6": ("HARDENED_OUTSIDE_FROZEN_SCIENCE", "Q07: a LYING commit-graph (c3's parent recorded as c1): plain git follows the lie, "
                "the frozen reader and the launcher's git return the truth -- the test can fail"),
    "QR1.N-7": ("HARDENED_OUTSIDE_FROZEN_SCIENCE", "HOME=/var/empty, GIT_CONFIG_GLOBAL=/dev/null, GIT_CONFIG_NOSYSTEM=1, "
                "GIT_ATTR_NOSYSTEM=1 in the launcher, the runner and the seal; Q07 control shows a hostile HOME configures plain git "
                "and not the launcher's; Q08 hostile environment reaches neither"),
    "QR1.N-8": ("HARDENED_OUTSIDE_FROZEN_SCIENCE", "signals are recorded (and forwarded only while the runner lives) from the final gate "
                "to the printed report; git children and caffeinate run in their own sessions; Q13 S1-S6. Residual ACCEPTED_LIMITATION: "
                "SIGKILL/power loss of the launcher cannot be intercepted -> the runner may finish unsealed, sleep prevention ends; "
                "recovery = --seal-only after no runner process remains (Q12 launcher-death test)"),
    "QR1.N-9": ("HARDENED_OUTSIDE_FROZEN_SCIENCE", "the preflight runs the frozen runner's R0 (loaded modules), R1 (code, C7), R4 (disk "
                "and history), R5 (premise), R6/R7 (target, cover, accounting) in advance; the runner re-runs all of them"),
    "QR1.N-10": ("HARDENED_OUTSIDE_FROZEN_SCIENCE", "the preflight requires AC power and an open lid; caffeinate -i -s. Residual "
                 "ACCEPTED_LIMITATION: a lid closed DURING the run cannot be prevented; the wall-clock cap then ends the run "
                 "NOT_CERTIFIED (fail-closed)"),
    "QR1.N-11": ("HARDENED_OUTSIDE_FROZEN_SCIENCE", "MECHANICALLY VERIFIED (Q06): sys.executable bin/python3.14 is a stub; the running "
                 "image (dyld image 0) is Resources/Python.app/Contents/MacOS/Python, linked to Versions/3.14/Python; both, every "
                 "extension module and dylib, and every stdlib source and cached bytecode loaded by the launcher, a runner-like probe "
                 "and its 5 spawn workers are bound (runtime_files_sha256) and re-hashed at launch; a mismatch refuses (Q08)"),
    "QR1.N-12": ("HARDENED_OUTSIDE_FROZEN_SCIENCE", "every note here carries its source prefix (R1R, QR1, PRED); PRED.N-7 = R1R.N-11 "
                 "recorded; the historical artifact and review are not edited"),
    "QR1.N-13": ("ACCEPTED_LIMITATION", "fail-closed direction kept: after consumption the science can never be rerun under freeze "
                 "ce5b8595 (consumed ref, runner lock and history R4, max_executions 1); a new execution needs a new freeze or "
                 "namespace AND a new independently reviewed qualification and authorization. Only the SEAL may be retried (see "
                 "retry_semantics)"),
    "QR1.N-14": ("HARDENED_OUTSIDE_FROZEN_SCIENCE", "every commit id reaching git is validated as 40 hex first: the CLI argument, the "
                 "grant's freeze, qualification and qualification-review commits (Q14 E5, E7-E9)"),
    "QR1.N-15": ("QUALIFIED", "carried into authorization_requirements, several now enforced mechanically by the launcher"),
}

RETRY_SEMANTICS = {
    "before_consumption": "any refusal (REFUSE ..., exit 2) consumed nothing and ran nothing; the launch may be retried once the "
                          "cause is fixed",
    "after_consumption_science": "NEVER retried under freeze ce5b8595: the consumed ref, the runner's permanent lock and its "
                                 "history guard R4, and max_executions = 1 all refuse; a new execution needs a new freeze or "
                                 "namespace and a new, independently reviewed qualification and authorization",
    "after_consumption_seal": "the SEAL only: automatically inside the same launcher process (bounded policy, delays 1, 2, 4, 8, "
                              "16, 32 s; a moved branch is permanent and not retried), and after 'EXECUTION CONSUMED — RESULT "
                              "UNSEALED' (exit 4) or a launcher death, only by the seal-only recovery (--seal-only), which "
                              "requires the consumed ref at the start commit, HEAD at it, evidence/runs/ not yet sealed and no "
                              "runner process alive, never starts the runner, never reads a runs value and commits exactly "
                              "evidence/runs/ on top of the start commit",
    "what_a_seal_only_recovery_does_not_mean": "it never permits a new D1/D2 execution, never resets the consumed ref and never "
                                               "changes what the runner produced; the sealed result goes to the execution review",
}


def compose_artifact(checks: dict, out_dir: pathlib.Path) -> dict:
    c = checks["checks"]
    fz = _freeze()
    lo, hi = MD.cell_block()
    q06 = c["q06_host_runtime"]
    rej_blob = G(REPO, "rev-parse", f"{REJECTED_QUAL_COMMIT}:{NS_REL}/{REJECTED_ARTIFACT_REL}").stdout.strip()
    art = {
        "schema": LA.QUAL_SCHEMA, "campaign": "C11RD-R1Q-R1 -- repaired qualification of the C11RD-R1 freeze",
        "CONTAINS_NO_TARGET_MAGNITUDE": True, "target_D1_computed": False, "target_D2_computed": False,
        "QUALIFICATION_CLASS": checks["QUALIFICATION_CHECKS"],
        "successor_of": {"qualification_commit": REJECTED_QUAL_COMMIT, "artifact": f"{NS_REL}/{REJECTED_ARTIFACT_REL}",
                         "artifact_blob": rej_blob, "review_commit": REJECTION_REVIEW_COMMIT,
                         "review": f"{NS_REL}/{REJECTION_REVIEW_REL}", "review_sha256": REJECTION_REVIEW_SHA256,
                         "verdict": "QUALIFICATION_REJECTED", "blockers": ["QR1.B-1"],
                         "superseded_launcher": {"path": f"{NS_REL}/{REJECTED_LAUNCHER_REL}", "sha256": REJECTED_LAUNCHER_SHA256,
                                                 "status": "HISTORICAL -- NOT a permitted entry"},
                         "historical_files_unchanged": c["q01_entry_identity"]["checks"]["historical_R1Q_files_unchanged_since_their_commits"]},
        "freeze_commit": FREEZE_COMMIT,
        "freeze": {"commit": FREEZE_COMMIT, "json_sha256": c["q04_hashes"]["freeze_json_sha256"],
                   "md_sha256": c["q04_hashes"]["freeze_md_sha256"], "predecessor_freeze": PRED_FREEZE_COMMIT},
        "pre_execution_review": {"commit": REVIEW_COMMIT, "path": REVIEW_REL, "sha256": REVIEW_SHA256, "verdict": "READY_TO_QUALIFY"},
        "frozen_code_sha256": fz["code_sha256"], "input_bindings": fz["input_bindings"], "document_sha256": fz["document_sha256"],
        "qualification_code_sha256": {"qualification_r1q_r1/code/c11rd_qualify.py": checks["tool_sha256"],
                                      LA.LAUNCHER_REL: checks["launcher_sha256"]},
        "host": q06["record"], "interpreter": q06["interpreter"], "runtime_files_sha256": q06["runtime_files_sha256"],
        "worktree": q06["worktree"], "launch_branch": LAUNCH_BRANCH, "launch_limits": LAUNCH_LIMITS,
        "canonical_paths": {"qualification_artifact": f"{NS_REL}/{LA.QUAL_ARTIFACT_REL}",
                            "qualification_review": f"{NS_REL}/{LA.QUAL_REVIEW_REL}",
                            "grant": f"{NS_REL}/{LA.GRANT_REL}", "authorization_review": f"{NS_REL}/{RN.AUTH_REVIEW_REL}",
                            "launcher": f"{NS_REL}/{LA.LAUNCHER_REL}", "runner": f"{NS_REL}/{LA.RUNNER_REL}",
                            "runs_directory": f"{NS_REL}/{LA.RUNS_DIR_REL}", "consumed_ref": LA.CONSUMED_REF,
                            "launcher_log_dir": f"<git common dir>/{LA.LOG_DIR_NAME}"},
        "launch_command": f"python3 -I -S -B {NS_REL}/{LA.LAUNCHER_REL} --authorization-review-commit <authorization review commit>",
        "target": {"cell": 306, "constants": ["D1", "D2"], "drift_block": [str(lo), str(hi)],
                   "sub_blocks": fz["D_sub_block_partition"]["sub_blocks"], "initial_boxes": 168,
                   "band_convention": fz["E_state_domain_partition"]["band_ownership"]["convention"]},
        "science": {"frozen_parameters": fz["frozen_parameters"], "recurrence": fz["F_derivative_recurrence"]["chain"],
                    "D1_formula": fz["F_derivative_recurrence"]["propagation"]["D1_j"],
                    "D2_formula": fz["F_derivative_recurrence"]["propagation"]["D2_j"], "aggregation": "maximum"},
        "resource_caps": fz["resource_caps"],
        "execution_count_rule": "exactly ONE target execution: freeze P = 1; the runner's grant binds max_executions 1; the runner's "
                                "exclusive, permanent lock and its history check (R4); the launcher's create-only consumed ref, "
                                "taken after the preflight and the final gate and before the run, consumes the authorization "
                                "whatever happens next",
        "ordering_invariant": "complete preflight -> sleep prevention -> final gate -> consume -> run once -> immediate seal",
        "preflight": ["L1 sanitized state (flags, exact environment incl. HOME=/var/empty and global/system git config off), "
                      "before any frozen import", "commit ids validated (40 hex) before any git call",
                      "qualified host, interpreter (stub, running image, libpython), runtime files re-hashed, worktree",
                      "launcher sha256 = this artifact's; exact freeze commit; canonical qualification paths; runner hash",
                      "frozen grant check (runner R2)", "runner R0, R1, R4 (disk, history), R5, R6/R7 in advance",
                      "seal preconditions (QR1.B-1): HEAD = authorization commit on the launch branch; index = HEAD; no unmerged "
                      "entry; worktree and namespace clean; no *.lock in the worktree git dir, common dir or refs/; no operation in "
                      "progress; files ref backend; explicit repo-local identity; no sparse checkout; no attribute on the seal "
                      "paths; writable object store",
                      "AC power, open lid, idle host, disk, memory, readable process table, no other runner, no consumed ref",
                      "final gate repeats the seal preconditions and the consumed/runs checks immediately before consumption; any "
                      "signal received by then refuses"],
        "seal_policy": {"mechanism": "private index: read-tree <start HEAD>; add -f evidence/runs; write-tree; commit-tree -p <start "
                                     "HEAD>; update-ref <launch branch> <seal> <start HEAD> (compare-and-swap); then the worktree "
                                     "index is refreshed for evidence/runs only",
                        "sealed_paths": "evidence/runs/ only: artifact, .partial, lock (as the runner left them), the runner log "
                                        "and the launch journal",
                        "retry_delays_seconds": list(LA.SEAL_RETRY_DELAYS), "max_attempts": len(LA.SEAL_RETRY_DELAYS) + 1,
                        "retried": "transient seal failures only (lock contention; a failed git step while the branch still equals "
                                   "the start HEAD)", "permanent": "the launch branch moved or HEAD left it; unexpected staged paths",
                        "terminal_state": LA.UNSEALED_BANNER, "exit_codes": {"SEALED": 0, "REFUSE (nothing consumed)": 2,
                                                                             LA.UNSEALED_BANNER: 4, "SEAL-ONLY REFUSED": 5},
                        "recovery": "--seal-only (never starts the runner)"},
        "retry_semantics": RETRY_SEMANTICS,
        "signal_policy": "from the final gate to the printed report SIGINT, SIGTERM, SIGHUP, SIGQUIT are recorded and forwarded to the "
                         "runner while it lives, SIGTSTP is recorded and ignored; a signal before consumption refuses, one after "
                         "consumption and before the start means the runner is not started; none interrupts the seal; git children "
                         "and caffeinate run in their own sessions",
        "launcher_death_recovery": "if the launcher dies after the consumed ref exists (SIGKILL, power loss): do nothing else; wait until "
                                   "no c11rd_runs.py process remains; then --seal-only; never re-run the launcher or the runner",
        "attempt_semantics": {"success": "exit 0, COMPLETED_CERTIFIED, sealed", "resource cap or accounting failure":
                              "exit 3, COMPLETED_NOT_CERTIFIED (targets INSUFFICIENT at comparison), sealed, consumed",
                              "process failure": "lock without artifact, CONSUMED_NO_RESULT, sealed, consumed",
                              "interruption": "signal forwarded; CONSUMED_NO_RESULT, sealed, consumed",
                              "refusal before the lock": "REFUSED_BEFORE_LOCK, sealed (log and journal), consumed by the launcher",
                              "signal after consumption, before the start": "CONSUMED_RUNNER_NOT_STARTED, sealed, consumed",
                              "seal cannot complete": "EXECUTION CONSUMED — RESULT UNSEALED (exit 4), consumed; seal-only recovery"},
        "lifecycle": ["freeze ce5b8595", "qualification (this artifact; successor of 3addf9d3)",
                      "qualification review (QUALIFICATION_ACCEPTED) at the canonical review path",
                      "authorization: grant at the canonical path + authorization review (AUTHORIZATION_ACCEPTED)",
                      "exactly one target execution through THIS launcher at HEAD = the authorization review commit",
                      "immediate seal (automatic; seal-only recovery if needed)", "execution review (EXECUTION_ACCEPTED)",
                      "comparison (c11rd_compare, once)", "adjudication"],
        "authorization_requirements": [
            "the grant equals the qualified values: host (grant_host), worktree, freeze_commit = ce5b8595 exactly, qualification "
            "commit = the commit of this artifact, qualification review = the R1Q-R1 review commit (QUALIFICATION_ACCEPTED), the "
            "canonical r1q_r1 paths, the frozen code and input hashes, target 306 [D1, D2], max_executions 1",
            "the launcher's sha256 at the authorization commit equals this artifact's; the rejected r1 launcher is not permitted; "
            "direct runner invocation is not permitted",
            "the launch is the exact launch_command at HEAD = the authorization review commit, clean index, no lock file (the "
            "launcher enforces these)",
            "no IDE or git client attached to the repository during the run (not mechanically enforceable; the seal survives "
            "index contention and retries ref-lock contention)",
            "an otherwise idle host, AC power, lid open, sleep prevention verified (the launcher enforces all four at launch; "
            "PRED.N-7 = R1R.N-11)",
            "after exit 4 or a launcher death: nothing but the seal-only recovery"],
        "comparator_rule": {"module": "code/c11rd_compare.py", "factor": 2, "steps": fz["U_comparison_procedure"]["steps"],
                            "runs_once": "U0 over reachable history"},
        "original_value_quarantine": {"quarantine_blob": CM.QUARANTINE_BLOB, "opened": False,
                                      "read_only_by": "c11rd_compare.main step U5, after U0-U4"},
        "validation": {"passed": c["q05_validation"]["passed"], "total": c["q05_validation"]["total"],
                       "output_sha256": c["q05_validation"]["output_sha256"]},
        "leak_scans": {"broad": {k: c["q10_broad_leak_scan"].get(k) for k in ("pass", "files", "tokens_checked", "hits")},
                       "rule": LEAK_RULE, "post_write": "evidence/qualification_r1q_r1/POST_WRITE_LEAK_SCAN.json"},
        "history": dict(c["q02_history_cleanliness"]["checks"]),
        "note_id_map": NOTE_ID_MAP,
        "note_dispositions": {k: {"class": v[0], "detail": v[1]} for k, v in NOTE_DISPOSITIONS.items()},
        "requires_new_freeze": [k for k, v in NOTE_DISPOSITIONS.items() if v[0] == "REQUIRES_NEW_FREEZE"],
        "checks_summary": {k: v.get("pass") for k, v in c.items()},
        "checks_file_sha256": sha256_file(out_dir / "C11RD_R1Q_R1_QUALIFICATION_CHECKS.json"),
        "LOCAL_MAIN_REF": LOCAL_MAIN_REF, "REMOTE_MAIN_REF": REMOTE_MAIN_REF,
    }
    return art


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir")
    ap.add_argument("--write-artifact", action="store_true")
    ap.add_argument("--post-write-scan")
    a = ap.parse_args(argv)
    if a.post_write_scan:
        rec = post_write_scan(pathlib.Path(a.post_write_scan))
        print(f"POST_WRITE_LEAK_SCAN clean={rec['clean']} files={rec['files_scanned']} "
              f"second_pass={rec['second_pass_including_this_file']}")
        return 0 if rec["clean"] and rec["second_pass_including_this_file"]["clean"] else 1
    out_dir = pathlib.Path(a.out_dir).resolve()
    res = run(out_dir)
    (out_dir / "C11RD_R1Q_R1_QUALIFICATION_CHECKS.json").write_text(json.dumps(res, indent=1, sort_keys=True, default=str) + "\n")
    print(f"QUALIFICATION_CHECKS = {res['QUALIFICATION_CHECKS']} ({res['passed']}/{res['total']})")
    if a.write_artifact:
        art = compose_artifact(res, out_dir)
        (out_dir / "C11RD_R1Q_R1_QUALIFICATION.json").write_text(json.dumps(art, indent=1, sort_keys=True, default=str) + "\n")
        print("qualification artifact written")
    return 0 if res["QUALIFICATION_CHECKS"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
