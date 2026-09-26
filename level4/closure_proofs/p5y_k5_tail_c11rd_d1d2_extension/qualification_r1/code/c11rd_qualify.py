"""C11RD-R1Q -- qualification of the C11RD-R1 freeze ce5b8595 (governance addition outside the frozen
scientific object; code/ and every frozen hash are untouched).

What it does NOT do: compute anything at a cell 306-309 drift (science runs only on the non-target
block [5/2, 3233337/1250000] or on synthetic candidates); run the runner in --mode real; run the
comparator's main; create a grant or a consumed ref in the real repository (grants, consumed refs and
seals are created ONLY in scratch repositories, with a STUB runner).

    python3 -I -S -B c11rd_qualify.py --out-dir DIR [--leak-values-from-stdin]

Writes DIR/C11RD_R1_QUALIFICATION_CHECKS.json (every check with its evidence),
DIR/validation/ (the frozen suite's output) and, with --write-artifact, DIR/C11RD_R1_QUALIFICATION.json
(the qualification artifact). The broad leak scan needs the two disclosed original values on stdin
(two lines); the tool itself contains no original value.
"""
import argparse
import ast
import hashlib
import json
import math
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
C11R_FINAL = "7375b9cdb1d770ba836335164f205e26b445035e"
LOCAL_MAIN_REF = "c123b9bb8f15d17650545b3fce4aca8a6b61093b"
REMOTE_MAIN_REF = "1cb453826313c189f0bdafd5b84120c1edb74da9"
R5_REL = "level4/closure_proofs/p5y_k5_tail_c2_closure/evidence/coverage/K5_COVERAGE_MAP_R5.json"
C11R_NS = "level4/closure_proofs/p5y_k5_tail_c11r_n9_statement_alignment"
QUAL_PATHS = ("qualification_r1/", "evidence/qualification_r1/", "docs/C11RD_R1_QUALIFICATION.md",
              "review/C11RD_R1_QUALIFICATION_REVIEW.md")
FORBIDDEN_LIFECYCLE_PATHS = ("evidence/runs", "evidence/comparison", "config", "review/C11RD_EXECUTION_REVIEW.md",
                             "review/C11RD_AUTHORIZATION_REVIEW.md")
NT = (F(5, 2), F(5, 2) + F(108337, 1250000))
# launch-time governance limits (NOT scientific parameters; the frozen caps are unchanged): an idle host
# (1-min load <= 2.0 on 6 cores), 2 GiB free disk, and 1 GiB available memory = about 5x the largest
# process-tree RSS observed in the frozen runner's rehearsals (about 210 MB)
LAUNCH_LIMITS = {"load1_max": 2.0, "disk_free_min_bytes": 2 * 1024 ** 3, "memory_available_min_kb": 1048576}
SAFE_GIT_ENV = {"PATH": "/usr/bin:/bin", "HOME": os.environ.get("HOME", "/var/empty"), "LANG": "C",
                "GIT_NO_REPLACE_OBJECTS": "1"}

sys.path.insert(0, str(CODE))
sys.path.insert(0, str(HERE))
import c11rd_runs as RN            # noqa: E402  (its pre-import barrier runs: -I -S -B required)
import c11rd_model as MD           # noqa: E402
import c11rd_certify as CE         # noqa: E402
import c11rd_compare as CM         # noqa: E402
import c11rd_kernel as KR          # noqa: E402
import c11rd_float as FL           # noqa: E402
import c11rd_tm as T               # noqa: E402
import c11rd_validate as V         # noqa: E402
import c11rd_launch as LA          # noqa: E402


def G(repo, *args, text=True):
    """Governance git: absolute binary, explicit sanitized environment, replace refs ignored,
    commit-graph not trusted."""
    return subprocess.run(["/usr/bin/git", "--no-replace-objects", "-c", "core.commitGraph=false", "-C", str(repo), *args],
                          capture_output=True, text=text, env=SAFE_GIT_ENV)


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def sha256_file(p) -> str:
    return sha256_bytes(pathlib.Path(p).read_bytes())


def check(fn):
    fn.is_check = True
    return fn


# =====================================================================================================
# Q01 entry identity
# =====================================================================================================
@check
def q01_entry_identity():
    out = {}
    out["freeze_commit_exists"] = G(REPO, "cat-file", "-e", f"{FREEZE_COMMIT}^{{commit}}").returncode == 0
    out["freeze_ancestor_of_HEAD"] = G(REPO, "merge-base", "--is-ancestor", FREEZE_COMMIT, "HEAD").returncode == 0
    fj = G(REPO, "show", f"{FREEZE_COMMIT}:{NS_REL}/protocol/C11RD_FREEZE_R1.json", text=False).stdout
    fm = G(REPO, "show", f"{FREEZE_COMMIT}:{NS_REL}/protocol/C11RD_FREEZE_R1.md", text=False).stdout
    out["freeze_files_unchanged_on_disk"] = fj == (NS / "protocol/C11RD_FREEZE_R1.json").read_bytes() and \
        fm == (NS / "protocol/C11RD_FREEZE_R1.md").read_bytes()
    out["freeze_protocol_untouched_since_freeze"] = G(REPO, "diff", "--name-only", FREEZE_COMMIT, "HEAD", "--",
                                                      f"{NS_REL}/protocol").stdout.strip() == ""
    rv = G(REPO, "show", f"{REVIEW_COMMIT}:{NS_REL}/{REVIEW_REL}", text=False).stdout
    out["review_commit_ancestor_of_HEAD"] = G(REPO, "merge-base", "--is-ancestor", REVIEW_COMMIT, "HEAD").returncode == 0
    out["review_sha256_unchanged"] = sha256_bytes(rv) == REVIEW_SHA256 == sha256_file(NS / REVIEW_REL)
    verdicts = [ln.strip() for ln in rv.decode().splitlines() if ln.strip() in ("READY_TO_QUALIFY", "NOT_READY")]
    out["review_verdict_exactly_READY_TO_QUALIFY"] = verdicts == ["READY_TO_QUALIFY"]
    later = G(REPO, "diff", "--name-only", REVIEW_COMMIT, "HEAD", "--", NS_REL).stdout.split()
    pending = [ln[3:] for ln in G(REPO, "status", "--porcelain", "--untracked-files=all", "--", NS_REL).stdout.splitlines()]
    extra = [p for p in later + pending if not any(p.startswith(f"{NS_REL}/{q}") for q in QUAL_PATHS)]
    out["since_review_only_qualification_paths_changed"] = extra == []
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
    out["no_refs_c11rd"] = G(REPO, "for-each-ref", "refs/c11rd").stdout.strip() == ""
    out["repository_not_shallow"] = G(REPO, "rev-parse", "--is-shallow-repository").stdout.strip() == "false"
    common = pathlib.Path(G(REPO, "rev-parse", "--path-format=absolute", "--git-common-dir").stdout.strip())
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
def _freeze():
    return json.loads((NS / "protocol/C11RD_FREEZE_R1.json").read_text())


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
    runs_src = (CODE / "c11rd_runs.py").read_text()
    out["one_execution_policy (freeze P = 1; runner grant check; permanent exclusive lock; launcher consumed ref)"] = \
        fz["P_execution_count"] == 1 and 'g.get("max_executions") != 1' in runs_src and "os.O_EXCL" in runs_src and \
        'CONSUMED_REF = "refs/c11rd/r1-execution-consumed"' in (HERE / "c11rd_launch.py").read_text()
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
    v29 = V.v29_scientific_identity()
    out["scientific_identity_vs_71495747 (V29)"] = v29["pass"]
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
    blobs = {}
    for name, b in fz["input_bindings"].items():
        if "blob" in b:
            blobs[name] = G(REPO, "rev-parse", f"HEAD:{b['path']}").stdout.strip() == b["blob"]
    out["all_input_blobs_equal"] = all(blobs.values()) and len(blobs) == 8
    docs = {rel: sha256_file(NS / rel) == h for rel, h in fz["document_sha256"].items()}
    out["frozen_document_hashes_equal"] = all(docs.values())
    out["freeze_json_sha256_recorded"] = True
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
# Q06 host / runtime
# =====================================================================================================
def _worker_probe(_):
    time.sleep(1.0)            # long enough that all five spawned workers take tasks: a trivial task lets the
    # first worker to start finish every task before the others are up (seen in the first full run)
    return os.getpid(), bool(sys.flags.isolated and sys.flags.no_site and sys.flags.dont_write_bytecode)


def _sysctl(name):
    return subprocess.run(["/usr/sbin/sysctl", "-n", name], capture_output=True, text=True).stdout.strip()


@check
def q06_host_runtime():
    import multiprocessing as mp
    host = RN.host_identity()
    interp = LA.interpreter_identity()
    wt = RN.worktree_identity()
    sw = subprocess.run(["/usr/bin/sw_vers"], capture_output=True, text=True).stdout
    mem_total = int(_sysctl("hw.memsize"))
    avail_kb = LA.available_memory_kb()
    disk = shutil.disk_usage(REPO)
    with mp.get_context("spawn").Pool(5) as pool:
        probes = pool.map(_worker_probe, range(20), chunksize=1)
    pids = {p for p, _ in probes}
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
    except SystemExit:
        pass
    pmset_custom = subprocess.run([LA.PMSET, "-g"], capture_output=True, text=True).stdout
    batt = subprocess.run([LA.PMSET, "-g", "batt"], capture_output=True, text=True).stdout
    probe_mods = subprocess.run([sys.executable, "-I", "-S", "-B", "-c",
                                 "import sys, hashlib, json; sys.path.insert(0, %r); import c11rd_runs, multiprocessing.pool, "
                                 "socket, argparse\nout = {}\nfor n, m in sorted(sys.modules.items()):\n"
                                 "    f = getattr(m, '__file__', None)\n"
                                 "    if f and '/lib/python3' in f and f.endswith('.py'):\n"
                                 "        out[n] = hashlib.sha256(open(f, 'rb').read()).hexdigest()\n"
                                 "print(json.dumps(out))" % str(CODE)], capture_output=True, text=True)
    stdlib = json.loads(probe_mods.stdout) if probe_mods.returncode == 0 else {}
    git_version = subprocess.run(["/usr/bin/git", "--version"], capture_output=True, text=True, env=SAFE_GIT_ENV).stdout.strip()
    rec = {"grant_host": host,
           "os": {"sw_vers": dict(re.findall(r"(\w+):\s+(.+)", sw)), "kernel": platform.release(), "machine": platform.machine()},
           "cpu": {"logical": os.cpu_count(), "physical": int(_sysctl("hw.physicalcpu")), "model": _sysctl("machdep.cpu.brand_string")},
           "memory": {"total_bytes": mem_total, "available_kb_now": avail_kb},
           "disk": {"volume_of": str(REPO), "total_bytes": disk.total, "free_bytes_now": disk.free},
           "load_average_now": list(os.getloadavg()),
           "workers": {"requested": 5, "distinct_worker_pids": len(pids), "all_workers_isolated_nosite_nobytecode": all(f for _, f in probes)},
           "process_table": {"calls": n, "failures": fails, "seconds": round(ps_seconds, 2), "tool": LA.PS},
           "wall_clock": {"runner_cap_clock": "time.time() (wall clock: it keeps running while the machine sleeps)",
                          "wall_vs_monotonic_drift_over_2s": round(drift, 6)},
           "sleep_prevention": {"tool": LA.CAFFEINATE, "assertion_verified": caff_ok,
                                "mechanism": "the launcher runs /usr/bin/caffeinate -i -w <launcher pid> and verifies the "
                                             "PreventUserIdleSystemSleep assertion in `pmset -g assertions` before consuming",
                                "pmset_sleep_settings_now": dict(re.findall(r"^\s*(sleep|displaysleep|disksleep|standby|powernap)\s+(\d+)",
                                                                            pmset_custom, re.M)),
                                "power_source_now": (re.search(r"Now drawing from '([^']+)'", batt) or [None, None])[1]},
           "git": {"binary": "/usr/bin/git", "version": git_version},
           "stdlib_modules_of_the_runner_sha256": stdlib}
    out = {"host_identity_complete": bool(host["hostname"]) and len(host["platform_uuid"]) == 36,
           "interpreter_flags": interp["flags_isolated_nosite_nobytecode"],
           "worktree_canonical": wt["canonical_path"] == os.path.realpath(REPO),
           "ram_at_least_4x_cap": mem_total >= 4 * 2097152 * 1024,
           "disk_free_at_least_min": disk.free >= LAUNCH_LIMITS["disk_free_min_bytes"],
           "five_isolated_workers": len(pids) == 5 and all(f for _, f in probes),
           "process_table_reliable": fails == 0,
           "wall_clock_sane": drift < 0.05,
           "sleep_prevention_verified": caff_ok,
           "stdlib_identity_recorded": len(stdlib) > 20 and "fractions" in stdlib}
    return {"pass": all(out.values()), "checks": out, "record": rec, "interpreter": interp, "worktree": wt}


# =====================================================================================================
# Q07 git / history hardening (scratch repositories only)
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


HOSTILE_ENV = {"GIT_DIR": "/nonexistent/.git", "GIT_WORK_TREE": "/tmp", "GIT_INDEX_FILE": "/nonexistent/index",
               "GIT_OBJECT_DIRECTORY": "/nonexistent/objects", "GIT_ALTERNATE_OBJECT_DIRECTORIES": "/nonexistent/alt",
               "GIT_NAMESPACE": "hidden", "GIT_CONFIG_PARAMETERS": "'core.commitgraph'='true'",
               "GIT_CONFIG_COUNT": "1", "GIT_CONFIG_KEY_0": "core.commitGraph", "GIT_CONFIG_VALUE_0": "true",
               "GIT_REPLACE_REF_BASE": "refs/other/", "GIT_CEILING_DIRECTORIES": "/", "GIT_CONFIG_GLOBAL": "/nonexistent/cfg",
               "GIT_CONFIG_SYSTEM": "/nonexistent/sys", "PATH": "/nonexistent/bin:/usr/bin:/bin"}


@check
def q07_git_history_hardening():
    art = f"{NS_REL}/{CM.OUT_REL}"
    out = {}
    with tempfile.TemporaryDirectory() as td:
        td = pathlib.Path(os.path.realpath(td))
        # a history with the artifact committed then deleted
        r = _repo(td, "base")
        _commit(r, {"README": "x\n"}, "base")
        _commit(r, {art: "{}\n"}, "compare")
        _commit(r, {art: None}, "delete")
        found = MD.history_commits([art], repo=r)
        out["deleted_artifact_found"] = len(found) == 2
        # corrupted commit-graph is not trusted
        subprocess.run(["/usr/bin/git", "-C", str(r), "commit-graph", "write", "--reachable"], capture_output=True,
                       env=SAFE_GIT_ENV)                       # a plain git writes the graph ...
        cg = r / ".git/objects/info/commit-graph"
        written = cg.exists()
        if written:                                            # ... which is then corrupted
            b = bytearray(cg.read_bytes())
            for i in range(64, min(len(b), 256)):
                b[i] ^= 0xFF
            cg.chmod(0o644)                                    # git writes the graph read-only
            cg.write_bytes(bytes(b))
        plain = subprocess.run(["/usr/bin/git", "-C", str(r), "rev-list", "--all", "--full-history", "--", art],
                               capture_output=True, text=True, env=SAFE_GIT_ENV)
        out["corrupted_commit_graph_ignored"] = written and MD.history_commits([art], repo=r) == found
        plain_git_with_corrupt_graph = {"returncode": plain.returncode, "commits": len(plain.stdout.split()),
                                        "stderr_head": plain.stderr.strip()[:160]}
        # replace ref hiding the artifact commit
        base = G(r, "rev-parse", "HEAD~2").stdout.strip()
        G(r, "replace", found[-1] if len(found) > 1 else found[0], base)
        out["replace_ref_ignored"] = set(MD.history_commits([art], repo=r)) == set(found)
        # hostile git environment in THIS process: the frozen reader passes an explicit environment
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
        # an alternate (linked) worktree with the artifact committed on a DETACHED head
        r3 = _repo(td, "wt_main")
        _commit(r3, {"a": "a\n"}, "a")
        G(r3, "worktree", "add", "-q", "--detach", str(td / "wt_linked"))
        _commit(td / "wt_linked", {art: "{}\n"}, "compare in linked worktree")
        out["linked_detached_worktree_found"] = len(MD.history_commits([art], repo=r3)) == 1
        # a path alias resolves to the same repository and history
        alias = td / "alias"
        os.symlink(r, alias)
        out["path_alias_same_history"] = set(MD.history_commits([art], repo=alias)) == set(found)
        out["path_alias_same_worktree_identity"] = RN.worktree_identity(repo=alias) == RN.worktree_identity(repo=r)
    # the real repository, with the frozen reader and a hostile environment
    saved = dict(os.environ)
    try:
        os.environ.update(HOSTILE_ENV)
        paths = [f"{NS_REL}/{p}" for p in FORBIDDEN_LIFECYCLE_PATHS]
        out["real_repository_clean_under_hostile_env"] = MD.history_commits(paths) == []
    finally:
        os.environ.clear()
        os.environ.update(saved)
    return {"pass": all(out.values()), "checks": out, "hostile_variables": sorted(HOSTILE_ENV),
            "plain_git_with_the_corrupted_graph (information)": plain_git_with_corrupt_graph}


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


def _synthetic_chain(td, fz_bytes, *, qualified_extra=None, stub_src=None):
    """freeze -> qualification -> QUALIFICATION_ACCEPTED -> grant -> AUTHORIZATION_ACCEPTED, in a
    scratch repository (never the real one)."""
    fz = json.loads(fz_bytes)
    repo = _repo(td, "chain")
    ns = repo / NS_REL
    stub = ns / "code" / "stub_runner.py"
    F0 = _commit(repo, {f"{NS_REL}/{RN.FREEZE_REL}": fz_bytes, f"{NS_REL}/code/stub_runner.py": stub_src or "#\n"}, "freeze")
    wt = RN.worktree_identity(repo=repo)
    host = RN.host_identity()
    qualified = {"freeze_commit": F0, "host": {"grant_host": host}, "interpreter": LA.interpreter_identity(),
                 "worktree": wt, "launch_limits": {"load1_max": 1000.0, "disk_free_min_bytes": 0, "memory_available_min_kb": 0},
                 "frozen_code_sha256": {LA.RUNNER_REL: sha256_file(stub)}}
    qualified.update(qualified_extra or {})
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
    return {"repo": repo, "ns": ns, "F0": F0, "Q": Q, "QR": QR, "AR": AR, "grant": grant, "gbytes": gbytes,
            "fz": fz, "host": host, "wt": wt, "qualified": qualified, "stub": stub}


STUB = r'''
import os, pathlib, sys, time, json
mode, marker = sys.argv[1], pathlib.Path(sys.argv[2])
ns = pathlib.Path(__file__).resolve().parents[1]
with open(marker, "a") as f:
    f.write(mode + "\n")
if mode == "env":
    pathlib.Path(sys.argv[3]).write_text(json.dumps(sorted(os.environ)))
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
(runs / "C11RD_RUNS.json").write_text(json.dumps({"status": "CERTIFIED" if mode in ("certified", "env") else "NOT_CERTIFIED"}) + "\n")
sys.exit(0 if mode in ("certified", "env") else 3)
'''

DRIVER = r'''
import importlib.util, json, pathlib, sys
spec = importlib.util.spec_from_file_location("c11rd_launch", sys.argv[1])
LA = importlib.util.module_from_spec(spec); spec.loader.exec_module(LA)
repo, ns_rel, ar, qfile, stub, mode, marker, logdir = sys.argv[2:10]
extra = sys.argv[10:]
qualified = json.loads(pathlib.Path(qfile).read_text())
cmd = [sys.executable, "-I", "-S", "-B", stub, mode, marker, *extra]
try:
    res = LA.launch(repo, ns_rel, ar, qualified, runner_cmd=cmd, runner_path=stub, log_dir=logdir)
    print("RESULT " + json.dumps(res))
except SystemExit as exc:
    print("REFUSED " + str(exc))
'''


def _launch_in_sandbox(td, mode, *, env=None, signal_after_start=None, pre=None, extra=()):
    fz_bytes = (NS / RN.FREEZE_REL).read_bytes()
    sub = pathlib.Path(td) / f"sb_{mode}_{random.randrange(10 ** 9)}"
    sub.mkdir()
    ch = _synthetic_chain(sub, fz_bytes, stub_src=STUB)
    if pre:
        pre(ch)
    qfile = sub / "qualified.json"
    qfile.write_text(json.dumps(ch["qualified"]))
    drv = sub / "driver.py"
    drv.write_text(DRIVER)
    marker = sub / "started.txt"
    logdir = sub / "logs"
    head0 = G(ch["repo"], "rev-parse", "HEAD").stdout.strip()
    cmd = [sys.executable, "-I", "-S", "-B", str(drv), str(HERE / "c11rd_launch.py"), str(ch["repo"]), NS_REL, ch["AR"],
           str(qfile), str(ch["stub"]), mode, str(marker), str(logdir), *extra]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env or dict(os.environ))
    if signal_after_start:
        t0 = time.time()
        while time.time() - t0 < 60 and not (ch["repo"] / NS_REL / "evidence/runs/C11RD_EXECUTION.lock").exists():
            time.sleep(0.1)
        time.sleep(0.5)
        p.send_signal(signal_after_start)
    so, se = p.communicate(timeout=300)
    res = {"stdout": so.strip().splitlines()[-1:] if so.strip() else [], "stderr_tail": se[-400:], "rc": p.returncode}
    line = next((ln for ln in so.splitlines() if ln.startswith(("RESULT ", "REFUSED "))), "")
    res["result"] = json.loads(line[7:]) if line.startswith("RESULT ") else None
    res["refused"] = line[8:] if line.startswith("REFUSED ") else None
    res["stub_runs"] = marker.read_text().split() if marker.exists() else []
    res["consumed_ref"] = G(ch["repo"], "rev-parse", "--verify", "-q", LA.CONSUMED_REF).stdout.strip()
    res["head0"] = head0
    res["head"] = G(ch["repo"], "rev-parse", "HEAD").stdout.strip()
    if res["result"]:
        seal = res["result"]["seal_commit"]
        res["seal_parent_is_start_head"] = G(ch["repo"], "rev-parse", f"{seal}^").stdout.strip() == head0
        files = G(ch["repo"], "show", "--name-only", "--format=", seal).stdout.split()
        res["seal_only_runs_dir"] = bool(files) and all(f.startswith(f"{NS_REL}/evidence/runs/") for f in files)
        res["sealed_files"] = [f.rsplit("/", 1)[1] for f in files]
        res["seal_message"] = G(ch["repo"], "log", "-1", "--format=%s", seal).stdout.strip()
        res["tree_clean_after_seal"] = G(ch["repo"], "status", "--porcelain", "--untracked-files=all").stdout.strip() == ""
    res["_chain"] = ch
    return res


@check
def q08_execution_lifecycle():
    out = {}
    calls, src = _main_real_branch_order()
    names = [c[2] for c in calls]
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

        def probs(g=None, host=None, wt=None, ar=None, repo_=None, code_dir=None):
            return RN.grant_problems(fz, g or ch["grant"], host=host or ch["host"], worktree=wt or ch["wt"],
                                     auth_review_commit=ch["AR"] if ar is None else ar, repo=repo_ or repo,
                                     ns=(repo_ or repo) / NS_REL, code_dir=code_dir or ns / "code")
        matrix["positive_control_all_predecessors_present"] = probs() == []

        def g_(**kw):
            g = json.loads(json.dumps(ch["grant"]))
            for k, v in kw.items():
                if k.startswith("q_"):
                    g["qualification"][k[2:]] = v
                elif k.startswith("host_"):
                    g["host"][k[5:]] = v
                elif k.startswith("wt_"):
                    g["worktree"][k[3:]] = v
                else:
                    g[k] = v
            return g

        def refused(p):
            return bool(p)
        matrix["freeze_commit_missing"] = refused(probs(g=g_(freeze_commit="0" * 40)))
        matrix["qualification_commit_missing"] = refused(probs(g=g_(q_commit="1" * 40)))
        matrix["qualification_review_commit_missing"] = refused(probs(g=g_(q_review_commit="2" * 40)))
        matrix["qualification_review_file_missing"] = refused(probs(g=g_(q_review_path=f"{NS_REL}/review/NOPE.md")))
        matrix["authorization_review_missing"] = refused(probs(ar=""))
        matrix["lineage_out_of_order"] = refused(probs(g=g_(q_commit=ch["QR"], q_review_commit=ch["Q"])))
        matrix["platform_only_deviation (N-12)"] = refused(probs(host=dict(ch["host"], platform="linux")))
        g2 = g_()
        g2["input_bindings"] = dict(g2["input_bindings"], c7_gaussian=dict(g2["input_bindings"]["c7_gaussian"], sha256="0" * 64))
        matrix["input_bindings_deviation (N-12)"] = refused(probs(g=g2))
        matrix["git_common_dir_only_deviation (N-12)"] = refused(probs(wt=dict(ch["wt"], git_common_dir="/elsewhere/.git")))
        QRr = _commit(repo, {f"{NS_REL}/{LA.QUAL_REVIEW_REL}": "QUALIFICATION_REJECTED\n"}, "rejected review")
        matrix["QUALIFICATION_REJECTED (N-12)"] = refused(probs(g=g_(q_review_commit=QRr), ar=_commit(repo, {}, "noop")))
        QRd = _commit(repo, {f"{NS_REL}/{LA.QUAL_REVIEW_REL}": "QUALIFICATION_ACCEPTED\nQUALIFICATION_ACCEPTED\n"}, "dup review")
        matrix["qualification_review_duplicated"] = refused(probs(g=g_(q_review_commit=QRd), ar=_commit(repo, {}, "noop2")))
        ARr = _commit(repo, {f"{NS_REL}/{RN.AUTH_REVIEW_REL}": "AUTHORIZATION_REJECTED\n"}, "auth rejected")
        matrix["AUTHORIZATION_REJECTED"] = refused(probs(ar=ARr))
        ARn = _commit(repo, {f"{NS_REL}/{RN.GRANT_REL}": None}, "grant removed")
        (ns / RN.GRANT_REL).parent.mkdir(parents=True, exist_ok=True)
        (ns / RN.GRANT_REL).write_text(ch["gbytes"])            # the disk grant stays; it is absent at ARn
        matrix["grant_absent_at_authorization_review"] = any("byte-identical" in x for x in probs(ar=ARn))
        # an ancestor freeze commit whose freeze file differs from the one on disk (N-12)
        with tempfile.TemporaryDirectory() as td2:
            td2 = pathlib.Path(os.path.realpath(td2))
            alt = json.loads(fz_bytes)
            alt["campaign"] = alt["campaign"] + " (older variant)"
            r2 = _repo(td2, "anc")
            Fold = _commit(r2, {f"{NS_REL}/{RN.FREEZE_REL}": json.dumps(alt) + "\n", f"{NS_REL}/code/stub_runner.py": "#\n"}, "old freeze")
            _commit(r2, {f"{NS_REL}/{RN.FREEZE_REL}": fz_bytes}, "new freeze")
            g3 = g_(freeze_commit=Fold)
            matrix["ancestor_freeze_commit_with_different_freeze_file (N-12)"] = any(
                "byte-identical" in x for x in RN.grant_problems(fz, g3, host=ch["host"], worktree=RN.worktree_identity(repo=r2),
                                                                 auth_review_commit="", repo=r2, ns=r2 / NS_REL,
                                                                 code_dir=r2 / NS_REL / "code"))
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
    # --- the launcher, end to end, with a STUB runner in scratch repositories
    L = {}
    with tempfile.TemporaryDirectory() as td:
        td = pathlib.Path(os.path.realpath(td))
        a = _launch_in_sandbox(td, "certified")
        L["success -> COMPLETED_CERTIFIED, sealed at once"] = bool(a["result"]) and a["result"]["outcome"] == "COMPLETED_CERTIFIED" \
            and a["seal_parent_is_start_head"] and a["seal_only_runs_dir"] and a["tree_clean_after_seal"] \
            and sorted(a["sealed_files"]) == ["C11RD_EXECUTION.lock", "C11RD_EXECUTION.log", "C11RD_RUNS.json"] \
            and a["consumed_ref"] == a["head0"] and a["stub_runs"] == ["certified"]
        # a second launch on the same repository is refused and runs nothing
        ch = a["_chain"]
        qfile = td / "q2.json"
        qfile.write_text(json.dumps(ch["qualified"]))
        drv = td / "driver2.py"
        drv.write_text(DRIVER)
        mk = td / "second_marker.txt"
        p = subprocess.run([sys.executable, "-I", "-S", "-B", str(drv), str(HERE / "c11rd_launch.py"), str(ch["repo"]), NS_REL,
                            ch["AR"], str(qfile), str(ch["stub"]), "certified", str(mk), str(td / "logs2")],
                           capture_output=True, text=True)
        L["second launch refused (consumed) and nothing ran"] = "REFUSED" in p.stdout and "consumed" in p.stdout and not mk.exists()
        b = _launch_in_sandbox(td, "not_certified")
        L["cap/accounting outcome -> COMPLETED_NOT_CERTIFIED, sealed"] = bool(b["result"]) and \
            b["result"]["outcome"] == "COMPLETED_NOT_CERTIFIED" and b["result"]["runner_exit"] == 3 and b["seal_parent_is_start_head"]
        c = _launch_in_sandbox(td, "crash")
        L["process failure -> CONSUMED_NO_RESULT, lock sealed"] = bool(c["result"]) and c["result"]["outcome"] == "CONSUMED_NO_RESULT" \
            and "C11RD_EXECUTION.lock" in c["sealed_files"] and "C11RD_RUNS.json" not in c["sealed_files"]
        d = _launch_in_sandbox(td, "hang", signal_after_start=signal.SIGTERM)
        L["interruption (SIGTERM forwarded) -> CONSUMED_NO_RESULT, sealed"] = bool(d["result"]) and \
            d["result"]["outcome"] == "CONSUMED_NO_RESULT" and d["seal_parent_is_start_head"] and d["consumed_ref"] == d["head0"]
        e = _launch_in_sandbox(td, "refuse")
        L["runner refusal before lock -> REFUSED_BEFORE_LOCK, still consumed and sealed"] = bool(e["result"]) and \
            e["result"]["outcome"] == "REFUSED_BEFORE_LOCK" and e["consumed_ref"] == e["head0"] and \
            e["sealed_files"] == ["C11RD_EXECUTION.log"]
        envfile = td / "stub_env.json"
        hostile = dict(os.environ, **HOSTILE_ENV)
        hostile["PYTHONPATH"] = "/nonexistent/py"
        f = _launch_in_sandbox(td, "env", env=hostile, extra=(str(envfile),))
        seen = json.loads(envfile.read_text()) if envfile.exists() else ["?"]
        L["hostile environment sanitized for git and runner"] = bool(f["result"]) and \
            set(seen) <= set(LA.SAFE_ENV_KEYS) | set(LA.RUNTIME_ADDED_KEYS)
        # preflight refusals: nothing consumed, nothing run
        pre = {}

        def refused_pre(mut, label, want, ref_preexisting=False):
            r = _launch_in_sandbox(td, "certified", pre=mut)
            ref_ok = (r["consumed_ref"] == r["head0"]) if ref_preexisting else (r["consumed_ref"] == "")
            pre[label] = r["result"] is None and bool(r["refused"]) and want in r["refused"] and ref_ok \
                and r["stub_runs"] == [] and r["head"] == r["head0"]
        refused_pre(lambda ch: ch["qualified"].update(host={"grant_host": dict(ch["host"], hostname="elsewhere.local")}),
                    "host mismatch", "qualified host")
        refused_pre(lambda ch: ch["qualified"].update(interpreter=dict(ch["qualified"]["interpreter"], executable_sha256="0" * 64)),
                    "interpreter mismatch", "interpreter")
        refused_pre(lambda ch: ch["qualified"].update(worktree=dict(ch["wt"], canonical_path="/elsewhere")),
                    "worktree mismatch", "worktree identity")
        refused_pre(lambda ch: ch["qualified"].update(freeze_commit="f" * 40), "freeze not the qualified one", "qualified freeze")
        refused_pre(lambda ch: ch["qualified"].update(launch_limits=dict(ch["qualified"]["launch_limits"], load1_max=-1.0)),
                    "host not idle", "not idle")
        refused_pre(lambda ch: ch["qualified"].update(frozen_code_sha256={LA.RUNNER_REL: "0" * 64}), "runner not frozen",
                    "not the frozen runner")
        refused_pre(lambda ch: G(ch["repo"], "update-ref", LA.CONSUMED_REF, "HEAD", ""), "already consumed", "already consumed",
                    ref_preexisting=True)
        refused_pre(lambda ch: (ch["ns"] / "stray.txt").write_text("x"), "dirty namespace", "not clean")
        L["preflight refusals create nothing and run nothing"] = all(pre.values())
        L["_preflight_cases"] = pre
    lc = {k: v for k, v in L.items() if not k.startswith("_")}
    out["launcher_lifecycle_with_stub_runner"] = all(lc.values())
    return {"pass": all(out.values()), "checks": out, "predecessor_matrix": matrix, "attempt_semantics": sem,
            "launcher": lc, "launcher_preflight_cases": L["_preflight_cases"]}


# =====================================================================================================
# Q09 reviewer-note specific checks (N-1, N-2, N-3, N-13)
# =====================================================================================================
@check
def q09_note_checks():
    out = {}
    # N-1: every point_box call of the validation uses a globally continuous candidate or none, and
    # no interior point with s >= 4 reaches it
    seen, cands_ok = [], True
    real_pb, real_ka = V.point_box, V.kernel_at

    def pb(p, m, e, order=4):
        seen.append((p, m))
        return real_pb(p, m, e, order)

    def ka(cand, p, m, e, orders=(0, 1, 2), order=4):
        nonlocal cands_ok
        band = [cand[k] for k in range(4)]
        cands_ok &= all(b == band[0] for b in band) and \
            cand[("A", "p")] == {i: c for (i, j), c in band[0].items() if j == 0} and \
            cand[("A", "m")] == {j: c for (i, j), c in band[0].items() if i == 0}
        return real_ka(cand, p, m, e, orders, order)
    V.point_box, V.kernel_at = pb, ka
    try:
        res = [V.v02_kernel_of_one(), V.v03_vs_c11_kernel(), V.v04_finite_difference(), V.v10_zero_cases(),
               V.v11_symmetry(), V.v12_known_signs(), V.v14_tiny_drift()]
    finally:
        V.point_box, V.kernel_at = real_pb, real_ka
    interior_s4 = [(p, m) for p, m in seen if p > 0 and m > 0 and p + m >= 4]
    out["N-1 point_box: only continuous candidates, no interior s>=4, tests still pass"] = \
        cands_ok and not interior_s4 and all(r["pass"] for r in res) and len(seen) > 50
    # N-2: kernel-level exclusion of the reversed convention, orders 0, 1, 2, on-line points s = 2, 3, 4
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
    for L in (2, 3, 4):
        for p, m in ((F(L, 2), F(L, 2)), (F(L) * F(2, 3), F(L) / 3), (F(L), F(0)), (F(0), F(L))):
            own = CE.owning_boxes(boxes, p, m)
            bx, u = V._tiny_box_in(own[0], p, m)
            KD = KR.kernel_box(bx, [cand], orders=(0, 1, 2))
            for i in (0, 1, 2):
                enc = V.tm_at(KD[(i, 0)], u)
                up, rv = ref(p, m, V.frozen_convention_owner, i), ref(p, m, V.reversed_convention_owner, i)
                differs = not V.overlap(up, rv)
                good = V.overlap(enc, up) and (not differs or not V.overlap(enc, rv))
                ok2 &= good
                rows.append({"s": L, "point": [str(p), str(m)], "order": i, "reversed_differs": differs, "pass": good})
    out["N-2 kernel-level exclusion of the reversed convention, orders 0-2, s = 2, 3, 4"] = \
        ok2 and sum(r["reversed_differs"] for r in rows) >= 12
    # N-3: a SHARP endpoint containment (tiny state boxes, order 6, the frozen proposal)
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
    out["N-3 sharp endpoint containment (width < 1e-3 of the residual)"] = sharp
    # N-13: the cover of EACH target sub-block list as parallel_cover builds it (geometry only)
    P = _freeze()["frozen_parameters"]
    lo, hi = MD.cell_block()
    geo_ok, geos = True, []
    for sa, sb in CE.sub_blocks(lo, hi, P["sub_blocks"]):
        bl = CE.initial_boxes(sa, sb, P["splits"], P["tm_order"])
        geo_ok &= CE.verify_cover(bl) == [] and len(bl) == 168
        geos.append([(b.band, b.s, b.theta, b.axis) for b in bl])
    nt_geo = [(b.band, b.s, b.theta, b.axis) for b in CE.initial_boxes(NT[0], NT[1], P["splits"], P["tm_order"])]
    out["N-13 every per-sub-block list complete and identical in geometry"] = geo_ok and all(g == nt_geo for g in geos)
    return {"pass": all(out.values()), "checks": out, "point_box_calls": len(seen), "n2_rows": len(rows),
            "n3_worst_width_to_residual_ratio": worst_ratio}


# =====================================================================================================
# Q10 broad leak scan (the two disclosed values on stdin; nothing embedded)
# =====================================================================================================
def q10_broad_leak_scan(values):
    if not values:
        return {"pass": None, "skipped": "values not supplied on stdin"}
    vals = [F(v) for v in values]
    files = sorted(f for f in NS.rglob("*") if f.is_file())
    hits = {}
    # tokens must stand alone (no letter or digit around them: hex digests such as ...0e8761... are
    # not numbers) and exponents are bounded, so no token can force a huge power of ten
    dec = re.compile(r"(?<![0-9A-Za-z.])([0-9]*\.[0-9]+)(?:[eE]([+-]?[0-9]{1,3}))?(?![0-9A-Za-z])")
    intsci = re.compile(r"(?<![0-9A-Za-z.])([0-9]+)[eE]([+-]?[0-9]{1,3})(?![0-9A-Za-z])")
    rat = re.compile(r"(?<![0-9A-Za-z/])(-?[0-9]+)/([0-9]+)(?![0-9A-Za-z])")
    n_rat = 0
    for f in files:
        try:
            txt = f.read_text()
        except UnicodeDecodeError:
            continue
        cands = []
        for mnt, ex in dec.findall(txt):
            cands.append(F(mnt if not mnt.startswith(".") else "0" + mnt) * (F(10) ** int(ex) if ex else 1))
        for mnt, ex in intsci.findall(txt):
            cands.append(F(int(mnt)) * F(10) ** int(ex))
        for a, b in rat.findall(txt):
            if int(b) != 0:
                cands.append(F(int(a), int(b)))
                n_rat += 1
        for x in cands:
            for v in vals:
                if x != 0 and abs(x - v) / v < F(1, 10 ** 4):
                    hits.setdefault(str(f.relative_to(NS)), 0)
                    hits[str(f.relative_to(NS))] += 1
    ctrl = F(123456789, 10 ** 9)
    control = abs(F("0.12345") - ctrl) / ctrl < F(1, 10 ** 4)
    return {"pass": not hits and control, "files": len(files), "rationals_checked": n_rat, "hits": hits,
            "rule": "any decimal (plain, bare-point, scientific), integer-mantissa scientific or rational token within "
                    "1e-4 relative of either disclosed value", "positive_control": control}


# =====================================================================================================
def run(out_dir: pathlib.Path, values) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    res = {}
    for fn in (q01_entry_identity, q02_history_cleanliness, q03_scientific_object, q04_hashes):
        t0 = time.time()
        res[fn.__name__] = dict(fn(), seconds=round(time.time() - t0, 1))
        print(f"  {'PASS' if res[fn.__name__]['pass'] else 'FAIL'}  {fn.__name__}", flush=True)
    t0 = time.time()
    res["q05_validation"] = dict(q05_validation(out_dir), seconds=round(time.time() - t0, 1))
    print(f"  {'PASS' if res['q05_validation']['pass'] else 'FAIL'}  q05_validation", flush=True)
    for fn in (q06_host_runtime, q07_git_history_hardening, q08_execution_lifecycle, q09_note_checks):
        t0 = time.time()
        res[fn.__name__] = dict(fn(), seconds=round(time.time() - t0, 1))
        print(f"  {'PASS' if res[fn.__name__]['pass'] else 'FAIL'}  {fn.__name__}", flush=True)
    res["q10_broad_leak_scan"] = q10_broad_leak_scan(values)
    print(f"  {res['q10_broad_leak_scan']['pass']}  q10_broad_leak_scan", flush=True)
    for v in res.values():
        v.pop("_chain", None)
    passed = [k for k, v in res.items() if v.get("pass") is True]
    return {"schema": "c11rd.qualification.checks.r1", "checks": res, "passed": len(passed), "total": len(res),
            "QUALIFICATION_CHECKS": "PASS" if len(passed) == len(res) else "FAIL",
            "tool_sha256": sha256_file(__file__), "launcher_sha256": sha256_file(HERE / "c11rd_launch.py")}


NOTE_DISPOSITIONS = {
    "N-1": ("QUALIFIED", "validation helper point_box reads bands lower-closed; Q09 shows every call uses a globally "
            "continuous candidate (or none) and no interior point with s >= 4, so no validation outcome depends on it; "
            "c11rd_validate.py is frozen and is not edited (wording defect recorded as an erratum)"),
    "N-2": ("HARDENED_OUTSIDE_FROZEN_SCIENCE", "Q09 adds kernel-level exclusion of the reversed convention for Khat "
            "orders 0, 1, 2 at the lines s = 2, 3, 4 (interior and axes)"),
    "N-3": ("HARDENED_OUTSIDE_FROZEN_SCIENCE", "Q09 adds a sharp endpoint containment (tiny state boxes, order 6, the "
            "frozen proposal): enclosure width below 1e-3 of the residual at u_e = -1, +1"),
    "N-4": ("ACCEPTED_LIMITATION", "nontarget mode trusts the on-disk freeze; changing it needs a new freeze. Rule bound "
            "here: no rehearsal may be run after this qualification except on explicit instruction, from a clean tree "
            "whose freeze file equals the committed blob; the governed target path is unaffected (R2 binds the freeze "
            "at the freeze commit)"),
    "N-5": ("HARDENED_OUTSIDE_FROZEN_SCIENCE", "the qualified launcher is the only permitted entry: it re-executes with a "
            "sanitized environment, replaces os.environ before any frozen call, and uses /usr/bin/git; Q07/Q08 show "
            "hostile GIT_* / PATH / PYTHONPATH variables do not reach git or the runner. Residual ACCEPTED_LIMITATION: "
            "deliberate forgery by a trusted operator"),
    "N-6": ("HARDENED_OUTSIDE_FROZEN_SCIENCE", "the launcher creates the create-only ref refs/c11rd/r1-execution-consumed "
            "in the COMMON git dir before the run (survives worktree removal/re-add) and seals immediately and "
            "automatically after it"),
    "N-7": ("ACCEPTED_LIMITATION", "reachable history only (inherent; the freeze says 'reachable history')"),
    "N-8": ("HARDENED_OUTSIDE_FROZEN_SCIENCE", "the qualification fixes the canonical paths and the exact freeze commit; "
            "the launcher refuses a grant with other qualification paths or another freeze commit; the authorization "
            "review must check the same"),
    "N-9": ("ACCEPTED_LIMITATION", "stale 'R0-R6' wording in hash-bound documents and the JSON FORBIDDEN list without the "
            "band-convention clause cannot be edited without a new freeze; recorded as errata in "
            "docs/C11RD_R1_QUALIFICATION.md. The band convention is nevertheless immutable: it is fixed by the frozen "
            "code hash of c11rd_certify.py (owner_band, verify_cover), the frozen theory hash, E.band_ownership in the "
            "freeze JSON and runner guard R6"),
    "N-10": ("QUALIFIED", "Q10 scans decimal, bare-point, scientific (point and integer mantissa) and rational tokens of "
             "every namespace file against both disclosed values (within 1e-4): clean"),
    "N-11": ("QUALIFIED", "fail-closed by design and NOT weakened: a failed process-table read ends the run "
             "NOT_CERTIFIED and consumes it. Q06: 500 consecutive reads, 0 failures; the launcher pre-checks the table; "
             "the authorization must require an idle host and sleep prevention (the launcher enforces both)"),
    "N-12": ("HARDENED_OUTSIDE_FROZEN_SCIENCE", "Q08 adds the missing single-field deviations (platform, input_bindings, "
             "git_common_dir, QUALIFICATION_REJECTED, ancestor freeze commit with a different freeze file): all refused"),
    "N-13": ("QUALIFIED", "Q09: each of the four per-sub-block box lists as parallel_cover builds them is complete "
             "(verify_cover) and identical in geometry to the non-target list"),
}


def compose_artifact(checks: dict, out_dir: pathlib.Path) -> dict:
    c = checks["checks"]
    fz = _freeze()
    lo, hi = MD.cell_block()
    q06 = c["q06_host_runtime"]
    art = {
        "schema": "c11rd.qualification.r1", "campaign": "C11RD-R1Q -- qualification of the C11RD-R1 freeze",
        "CONTAINS_NO_TARGET_MAGNITUDE": True, "target_D1_computed": False, "target_D2_computed": False,
        "QUALIFICATION_CLASS": checks["QUALIFICATION_CHECKS"],
        "freeze_commit": FREEZE_COMMIT,
        "freeze": {"commit": FREEZE_COMMIT, "json_sha256": c["q04_hashes"]["freeze_json_sha256"],
                   "md_sha256": c["q04_hashes"]["freeze_md_sha256"], "predecessor_freeze": PRED_FREEZE_COMMIT},
        "pre_execution_review": {"commit": REVIEW_COMMIT, "path": REVIEW_REL, "sha256": REVIEW_SHA256,
                                 "verdict": "READY_TO_QUALIFY"},
        "frozen_code_sha256": fz["code_sha256"], "input_bindings": fz["input_bindings"],
        "document_sha256": fz["document_sha256"],
        "qualification_code_sha256": {"qualification_r1/code/c11rd_qualify.py": checks["tool_sha256"],
                                      "qualification_r1/code/c11rd_launch.py": checks["launcher_sha256"]},
        "host": q06["record"], "interpreter": q06["interpreter"], "worktree": q06["worktree"],
        "launch_limits": LAUNCH_LIMITS,
        "canonical_paths": {"qualification_artifact": f"{NS_REL}/evidence/qualification_r1/C11RD_R1_QUALIFICATION.json",
                            "qualification_review": f"{NS_REL}/review/C11RD_R1_QUALIFICATION_REVIEW.md",
                            "grant": f"{NS_REL}/config/C11RD_GRANT.json",
                            "authorization_review": f"{NS_REL}/review/C11RD_AUTHORIZATION_REVIEW.md",
                            "launcher": f"{NS_REL}/qualification_r1/code/c11rd_launch.py",
                            "runner": f"{NS_REL}/code/c11rd_runs.py", "runs_artifact": f"{NS_REL}/evidence/runs/C11RD_RUNS.json",
                            "consumed_ref": "refs/c11rd/r1-execution-consumed"},
        "target": {"cell": 306, "constants": ["D1", "D2"], "drift_block": [str(lo), str(hi)],
                   "sub_blocks": fz["D_sub_block_partition"]["sub_blocks"], "initial_boxes": 168,
                   "band_convention": fz["E_state_domain_partition"]["band_ownership"]["convention"]},
        "science": {"frozen_parameters": fz["frozen_parameters"], "recurrence": fz["F_derivative_recurrence"]["chain"],
                    "D1_formula": fz["F_derivative_recurrence"]["propagation"]["D1_j"],
                    "D2_formula": fz["F_derivative_recurrence"]["propagation"]["D2_j"], "aggregation": "maximum"},
        "resource_caps": fz["resource_caps"],
        "execution_count_rule": "exactly ONE target execution: freeze P = 1; the runner's grant must bind max_executions 1; "
                                "the runner's exclusive, permanent lock and its history check (R4); the launcher's create-only "
                                "consumed ref, taken after preflight and before the run, consumes the authorization whatever "
                                "happens next; a new execution needs a new, independently reviewed authorization",
        "immediate_seal_rule": "the launcher's next repository action after the runner exits commits evidence/runs/ "
                               "(artifact, .partial, lock, log -- whatever exists) on top of the start HEAD, touching nothing "
                               "else, without reading any value; if the automatic seal fails, nothing else may be done before "
                               "a manual seal of exactly those paths",
        "attempt_semantics": {"success": "exit 0, COMPLETED_CERTIFIED, sealed", "resource cap or accounting failure":
                              "exit 3, NOT_CERTIFIED (targets INSUFFICIENT at comparison), sealed, consumed",
                              "process failure": "lock without artifact, CONSUMED_NO_RESULT, sealed, consumed",
                              "interruption": "signal forwarded; lock without artifact, CONSUMED_NO_RESULT, sealed, consumed",
                              "refusal before the lock": "REFUSED_BEFORE_LOCK, sealed (log only), consumed by the launcher"},
        "lifecycle": ["freeze ce5b8595", "qualification (this artifact)", "qualification review (QUALIFICATION_ACCEPTED)",
                      "authorization: grant at the canonical path + authorization review (AUTHORIZATION_ACCEPTED)",
                      "exactly one target execution through the qualified launcher", "immediate seal (automatic)",
                      "execution review (EXECUTION_ACCEPTED)", "comparison (c11rd_compare, once)", "adjudication"],
        "authorization_requirements": [
            "the grant equals the qualified values: host (grant_host), worktree, freeze_commit = ce5b8595, canonical "
            "qualification artifact and review paths, the frozen code and input hashes, target 306 [D1, D2], max_executions 1",
            "the launch goes ONLY through qualification_r1/code/c11rd_launch.py (sanitized environment, preflight, "
            "sleep prevention, consumed ref, immediate seal); direct runner invocation is not permitted",
            "an otherwise idle host (1-min load <= 2.0 at launch), mains power, lid open, sleep prevented by the launcher's "
            "caffeinate -i assertion (review N-7 accepted limitation)",
            "the launcher's hash and this artifact's blob are bound by the authorization review"],
        "comparator_rule": {"module": "code/c11rd_compare.py", "factor": 2, "steps": fz["U_comparison_procedure"]["steps"],
                            "runs_once": "U0 over reachable history"},
        "original_value_quarantine": {"quarantine_blob": CM.QUARANTINE_BLOB, "opened": False,
                                      "read_only_by": "c11rd_compare.main step U5, after U0-U4"},
        "validation": {"passed": c["q05_validation"]["passed"], "total": c["q05_validation"]["total"],
                       "output_sha256": c["q05_validation"]["output_sha256"]},
        "leak_scans": {"broad": {k: c["q10_broad_leak_scan"].get(k) for k in ("pass", "files", "rationals_checked", "hits")},
                       "post_write": "evidence/qualification_r1/POST_WRITE_LEAK_SCAN.json"},
        "history": {k: v for k, v in c["q02_history_cleanliness"]["checks"].items()},
        "note_dispositions": {k: {"class": v[0], "detail": v[1]} for k, v in NOTE_DISPOSITIONS.items()},
        "checks_summary": {k: v.get("pass") for k, v in c.items()},
        "checks_file_sha256": sha256_file(out_dir / "C11RD_R1_QUALIFICATION_CHECKS.json"),
        "LOCAL_MAIN_REF": LOCAL_MAIN_REF, "REMOTE_MAIN_REF": REMOTE_MAIN_REF,
    }
    return art


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--leak-values-from-stdin", action="store_true")
    ap.add_argument("--write-artifact", action="store_true")
    a = ap.parse_args(argv)
    values = [ln.strip() for ln in sys.stdin.read().splitlines() if ln.strip()] if a.leak_values_from_stdin else []
    out_dir = pathlib.Path(a.out_dir).resolve()
    res = run(out_dir, values)
    (out_dir / "C11RD_R1_QUALIFICATION_CHECKS.json").write_text(json.dumps(res, indent=1, sort_keys=True, default=str) + "\n")
    print(f"QUALIFICATION_CHECKS = {res['QUALIFICATION_CHECKS']} ({res['passed']}/{res['total']})")
    if a.write_artifact:
        art = compose_artifact(res, out_dir)
        (out_dir / "C11RD_R1_QUALIFICATION.json").write_text(json.dumps(art, indent=1, sort_keys=True, default=str) + "\n")
        print("qualification artifact written")
    return 0 if res["QUALIFICATION_CHECKS"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
