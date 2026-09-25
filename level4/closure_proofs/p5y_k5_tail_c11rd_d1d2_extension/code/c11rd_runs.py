"""C11RD -- the runner: the ONE cell-306 D1/D2 execution, and the non-target rehearsal of the same code.

Nothing runs at import. Every parameter comes from the successor freeze protocol/C11RD_FREEZE_R1.json;
there are no CLI overrides of science parameters.

    python3 -I -S -B c11rd_runs.py --mode nontarget --out PATH
        Rehearsal on the freeze's non-target block (C11R's NT block; no grant, no lock; refuses to
        write inside the namespace).
    python3 -I -S -B c11rd_runs.py --mode real --authorization-review-commit SHA
        The target execution. The grant is ALWAYS config/C11RD_GRANT.json of this namespace. Refuses
        unless (freeze sections P / V and runner_guards):
          R0 the pre-import barrier (below) and the loaded-module check;
          R1 every frozen code file's sha256, and C7's c7_gaussian.py's, equals the freeze's;
          R2 the grant says ALLOW for C11RD's cell-306 D1/D2, max_executions = 1, and binds EXACTLY:
             this host (hostname + hardware UUID + platform + Python), this canonical worktree
             (realpath; git common dir), the freeze commit and the freeze file's sha256 (the freeze
             file byte-identical at that commit), the frozen code and input hashes, the qualification
             commit, artifact blob and QUALIFICATION_ACCEPTED review; the authorization review commit
             holds exactly one AUTHORIZATION_ACCEPTED line and the byte-identical grant; lineage
             freeze <= qualification <= its review <= authorization review <= HEAD; full history;
          R3 the namespace has no uncommitted, untracked or ignored file;
          R4 no execution lock and no runs artifact exist, and none was EVER in reachable history
             (c11rd_model.history_commits, fail-closed) -- the lock is created EXCLUSIVELY before any
             science and is never removed: a started execution is consumed whatever its outcome;
          R5 the premise loader verifies C11R's accepted F_H certificate (blob-bound);
          R6 the drift block read from C11R's frozen statement table equals the freeze's target, and
             the frozen cover is complete for the upper-closed band convention (c11rd_certify.verify_cover);
          R7 the live process tree's memory can be accounted (fail-closed) before the lock.
The log carries progress counters and timings only -- never a residual, a lambda or a bound.
"""
# ---- PRE-IMPORT BARRIER (must stay the first statements; builtin modules only: `sys` and `posix`
# are built into the interpreter and cannot be shadowed from any path). Before ANY other import it
# refuses unless: the interpreter runs isolated (-I), without site (-S), without writing bytecode
# (-B) and without a pycache prefix; this code directory holds exactly the frozen files (no
# __pycache__, no .pyc, nothing else); and C7's code directory (which c11rd_tm puts on sys.path)
# holds no __pycache__, no .pyc and no file or directory named like a standard-library module. With
# no bytecode anywhere on those two directories, every module they supply runs from its source.
import sys
import posix

CODE_FILES = frozenset({"c11rd_certify.py", "c11rd_compare.py", "c11rd_float.py", "c11rd_kernel.py",
                        "c11rd_model.py", "c11rd_runs.py", "c11rd_tm.py", "c11rd_validate.py"})


def _preimport_barrier(main_file: str) -> tuple:
    f = main_file if main_file.startswith("/") else posix.getcwd() + "/" + main_file
    code_dir = f.rpartition("/")[0]
    c7_dir = code_dir.rpartition("/")[0].rpartition("/")[0] + "/p5y_k5_tail_c7_e2_lambda309/code"
    problems = []
    fl = sys.flags
    if not (fl.isolated and fl.no_site and fl.dont_write_bytecode) or sys.pycache_prefix is not None:
        problems.append("the interpreter must run as `python3 -I -S -B` without a pycache prefix")
    have = set(posix.listdir(code_dir))
    if have != CODE_FILES:
        problems.append(f"code directory entries differ from the frozen files: extra {sorted(have - CODE_FILES)}, "
                        f"missing {sorted(CODE_FILES - have)}")
    std = sys.stdlib_module_names
    for name in posix.listdir(c7_dir):
        stem = name[:-3] if name.endswith(".py") else name
        if name == "__pycache__" or name.endswith(".pyc") or stem in std:
            problems.append(f"C7 code directory holds {name!r}")
    if problems:
        raise SystemExit("REFUSE R0 (pre-import barrier): " + "; ".join(problems))
    return code_dir, c7_dir


_CODE_DIR, _C7_DIR = _preimport_barrier(__file__)
# ---- end of the barrier; ordinary imports follow
import argparse
import hashlib
import json
import os
import stat
import pathlib
import subprocess
import sys
import time
from fractions import Fraction as F

HERE = pathlib.Path(__file__).resolve().parent
_CODE_DIR, _C7_DIR = str(pathlib.Path(_CODE_DIR).resolve()), str(pathlib.Path(_C7_DIR).resolve())
if str(HERE) != _CODE_DIR:
    raise SystemExit("REFUSE R0: the code directory resolved differently after the barrier")
sys.path.insert(0, str(HERE))
import c11rd_certify as CE  # noqa: E402
import c11rd_float as FL  # noqa: E402
import c11rd_kernel as KR  # noqa: E402
import c11rd_model as MD  # noqa: E402

NS = HERE.parent
FREEZE_REL = "protocol/C11RD_FREEZE_R1.json"
FREEZE_SCHEMA = "c11rd.freeze.r1"
GRANT_REL = "config/C11RD_GRANT.json"
QUAL_TOKENS = ("QUALIFICATION_ACCEPTED", "QUALIFICATION_REJECTED")
AUTH_TOKENS = ("AUTHORIZATION_ACCEPTED", "AUTHORIZATION_REJECTED")
AUTH_REVIEW_REL = "review/C11RD_AUTHORIZATION_REVIEW.md"
PS = "/bin/ps"
IOREG = "/usr/sbin/ioreg"
RUNS_REL = "evidence/runs/C11RD_RUNS.json"
LOCK_REL = "evidence/runs/C11RD_EXECUTION.lock"


class Refusal(SystemExit):
    pass


def sha256(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


GIT = ("git", "--no-replace-objects", "-c", "core.commitGraph=false")      # replace refs / a forged
                                                                           # commit-graph cannot hide history


def git_run(*args, repo=None) -> subprocess.CompletedProcess:
    return subprocess.run([*GIT, "-C", str(repo or MD.REPO), *args], capture_output=True, text=True)


def git(*args) -> str:
    r = git_run(*args)
    if r.returncode != 0:
        raise Refusal(f"REFUSE: git {' '.join(args[:2])} failed: {r.stderr.strip()}")
    return r.stdout.strip()


def ever_committed(rels: list, repo=None) -> list:
    """Commits on ANY ref or reflog entry that ever touched one of the paths (full history), by the
    campaign's one hardened history reader; an incomplete or unreadable history REFUSES."""
    try:
        return MD.history_commits(rels, repo=repo)
    except MD.ModelError as exc:
        raise Refusal(f"REFUSE R4: {exc}")


def verify_loaded_modules() -> None:
    """Every loaded module that comes from the C11RD or C7 code directory is a frozen SOURCE file,
    and no bytecode cache of it exists (the barrier refused any; this re-checks after the imports)."""
    bad = []
    for name, mod in list(sys.modules.items()):
        spec = getattr(mod, "__spec__", None)
        raw = getattr(spec, "origin", None)
        if not isinstance(raw, str) or not os.path.isabs(raw):      # 'built-in', 'frozen', namespace pkgs
            continue
        origin = os.path.realpath(raw)
        for d, allowed in ((_CODE_DIR, CODE_FILES), (_C7_DIR, frozenset({"c7_gaussian.py"}))):
            if origin.startswith(d + "/"):
                leaf = origin[len(d) + 1:]
                cached = getattr(spec, "cached", None)
                if leaf not in allowed or (cached and os.path.exists(cached)):
                    bad.append(f"{name} from {leaf}")
    if bad:
        raise Refusal(f"REFUSE R0: modules not loaded from frozen sources: {bad}")


def load_freeze() -> dict:
    fz = json.loads((NS / FREEZE_REL).read_text())
    if fz.get("schema") != FREEZE_SCHEMA:
        raise Refusal("REFUSE: not the C11RD successor (R1) freeze")
    return fz


def verify_code(fz: dict) -> None:
    """R1: the eight C11RD files AND C7's c7_gaussian.py (the only other code the certifier runs)
    have their frozen sha256."""
    bad = {rel: sha256(NS / rel) for rel, h in fz["code_sha256"].items() if sha256(NS / rel) != h}
    c7 = fz["input_bindings"]["c7_gaussian"]
    if sha256(MD.REPO / c7["path"]) != c7["sha256"] or pathlib.Path(_C7_DIR) != (MD.REPO / c7["path"]).parent.resolve():
        bad["c7_gaussian"] = "changed or relocated"
    if set(fz["code_sha256"]) != {f"code/{n}" for n in CODE_FILES}:
        bad["file_set"] = "the frozen file set is not the barrier's"
    if bad:
        raise Refusal(f"REFUSE R1: frozen code changed: {sorted(bad)}")


def host_identity() -> dict:
    """This machine: hostname, macOS hardware UUID (IOPlatformUUID), platform, Python. Fails closed."""
    import re
    import socket
    hn = socket.gethostname()
    try:
        r = subprocess.run([IOREG, "-rd1", "-c", "IOPlatformExpertDevice"], capture_output=True, text=True, timeout=60)
    except (OSError, subprocess.SubprocessError):
        raise Refusal("REFUSE R2: this host's identity cannot be established")
    mt = re.search(r'"IOPlatformUUID" = "([0-9A-Fa-f-]{36})"', r.stdout)
    if r.returncode != 0 or not mt or not hn:
        raise Refusal("REFUSE R2: this host's identity cannot be established")
    return {"hostname": hn, "platform_uuid": mt.group(1).upper(), "platform": sys.platform,
            "python": sys.version.split()[0]}


def worktree_identity(repo=None) -> dict:
    """The canonical (symlink-free) path of the worktree that holds this code, and its git common
    directory. Any alias resolves to the real directory it names, so a path alias cannot make a
    different checkout look like the bound one. Fails closed."""
    repo = str(repo or MD.REPO)
    top = git_run("rev-parse", "--show-toplevel", repo=repo)
    cd = git_run("rev-parse", "--path-format=absolute", "--git-common-dir", repo=repo)
    if top.returncode != 0 or cd.returncode != 0:
        raise Refusal("REFUSE R2: the worktree identity cannot be established")
    return {"canonical_path": os.path.realpath(top.stdout.strip()),
            "git_common_dir": os.path.realpath(cd.stdout.strip())}


def review_verdict_problems(commit: str, rel: str, tokens: tuple, repo=None) -> list:
    """The file `rel` at `commit` must hold exactly one line equal to tokens[0] and none equal to
    tokens[1]."""
    r = subprocess.run([*GIT, "-C", str(repo or MD.REPO), "show", f"{commit}:{rel}"], capture_output=True)
    if r.returncode != 0:
        return [f"{rel} is not present at {commit[:12]}"]
    lines = [ln.strip() for ln in r.stdout.decode("utf-8", "replace").splitlines()]
    if lines.count(tokens[0]) != 1 or tokens[1] in lines:
        return [f"{rel} at {commit[:12]} does not hold exactly one {tokens[0]} verdict line"]
    return []


def is_ancestor(a: str, b: str, repo=None) -> bool:
    return len(a) == 40 and git_run("merge-base", "--is-ancestor", a, b, repo=repo).returncode == 0


def grant_problems(fz: dict, g: dict, *, host: dict, worktree: dict, auth_review_commit: str | None,
                   repo=None, ns=None, code_dir=None) -> list:
    """Every reason the grant `g` does not authorize THIS execution (empty = authorized). `host` and
    `worktree` are this machine's and this checkout's identities (host_identity(), worktree_identity())."""
    repo, ns = pathlib.Path(repo or MD.REPO), pathlib.Path(ns or NS)
    ns_rel = str(ns.relative_to(repo)) if ns.is_relative_to(repo) else MD.NS_REL
    lo, hi = MD.cell_block()
    p = []
    if g.get("decision") != "ALLOW" or g.get("campaign") != "C11RD":
        p.append("the grant is not an ALLOW for C11RD")
    if g.get("target") != {"cell": 306, "e_lo": str(lo), "e_hi": str(hi), "constants": ["D1", "D2"]}:
        p.append("the grant's target is not cell 306's D1/D2 on the frozen block")
    if g.get("max_executions") != 1:
        p.append("the grant does not bind exactly one execution")
    if g.get("code_sha256") != fz["code_sha256"] or g.get("input_bindings") != fz["input_bindings"]:
        p.append("the grant does not bind the frozen code and input hashes")
    if g.get("host") != host:
        p.append("host identity differs from the grant's")
    gw = g.get("worktree") or {}
    gp = gw.get("canonical_path", "")
    if not os.path.isabs(gp) or os.path.realpath(gp) != gp:
        p.append("the grant's worktree path is not canonical (absolute, symlink-free)")
    if gw != worktree or os.path.realpath(repo) != worktree.get("canonical_path") \
            or not str(pathlib.Path(code_dir or HERE).resolve()).startswith(worktree.get("canonical_path", "\0") + "/"):
        p.append("canonical worktree differs from the grant's")
    shallow = git_run("rev-parse", "--is-shallow-repository", repo=repo).stdout.strip()
    if shallow != "false":
        p.append("the repository is shallow (history incomplete)")
    fc = g.get("freeze_commit", "")
    if not is_ancestor(fc, "HEAD", repo=repo):
        p.append("the freeze commit is not an ancestor of HEAD")
    else:
        at_fc = subprocess.run([*GIT, "-C", str(repo), "show", f"{fc}:{ns_rel}/{FREEZE_REL}"], capture_output=True)
        disk = (ns / FREEZE_REL).read_bytes() if (ns / FREEZE_REL).exists() else b""
        if at_fc.returncode != 0 or at_fc.stdout != disk:
            p.append("the freeze file is not byte-identical to the one at the freeze commit")
        if hashlib.sha256(disk).hexdigest() != g.get("freeze_sha256"):
            p.append("freeze identity differs from the grant's (freeze file sha256)")
    q = g.get("qualification") or {}
    qc, qr = q.get("commit", ""), q.get("review_commit", "")
    if not (is_ancestor(fc, qc, repo=repo) and is_ancestor(qc, qr, repo=repo) and is_ancestor(qr, "HEAD", repo=repo)):
        p.append("the qualification lineage (freeze <= qualification <= its review <= HEAD) does not hold")
    else:
        blob_q = git_run("rev-parse", f"{qc}:{q.get('artifact_path', '')}", repo=repo).stdout.strip()
        blob_h = git_run("rev-parse", f"HEAD:{q.get('artifact_path', '')}", repo=repo).stdout.strip()
        if not blob_q or blob_q != q.get("artifact_blob") or blob_h != blob_q:
            p.append("the qualification artifact is not the bound blob (at its commit and at HEAD)")
        p += review_verdict_problems(qr, q.get("review_path", ""), QUAL_TOKENS, repo=repo)
    ar = auth_review_commit or ""
    if not (is_ancestor(qr, ar, repo=repo) and is_ancestor(ar, "HEAD", repo=repo)):
        p.append("the authorization review commit is not between the qualification review and HEAD")
    else:
        p += review_verdict_problems(ar, f"{ns_rel}/{AUTH_REVIEW_REL}", AUTH_TOKENS, repo=repo)
        at_ar = subprocess.run([*GIT, "-C", str(repo), "show", f"{ar}:{ns_rel}/{GRANT_REL}"], capture_output=True)
        if at_ar.returncode != 0 or at_ar.stdout != (ns / GRANT_REL).read_bytes():
            p.append("the grant is not byte-identical to the one the authorization review accepted")
    return p


def verify_grant(fz: dict, auth_review_commit: str | None) -> dict:
    gp = NS / GRANT_REL
    if not gp.is_file() or gp.is_symlink():
        raise Refusal(f"REFUSE R2: no grant at {GRANT_REL}")
    g = json.loads(gp.read_text())
    problems = grant_problems(fz, g, host=host_identity(), worktree=worktree_identity(),
                              auth_review_commit=auth_review_commit)
    if problems:
        raise Refusal("REFUSE R2: " + "; ".join(problems))
    return g


def verify_clean() -> None:
    dirty = git("status", "--porcelain", "--ignored", "--untracked-files=all", "--", MD.NS_REL)
    if dirty:
        raise Refusal(f"REFUSE R3: uncommitted changes in the namespace:\n{dirty}")


def take_lock(meta: dict, *, repo=None) -> None:
    if (NS / RUNS_REL).exists():
        raise Refusal("REFUSE R4: a runs artifact exists -- the execution is consumed")
    hist = ever_committed([f"{MD.NS_REL}/{RUNS_REL}", f"{MD.NS_REL}/{LOCK_REL}"], repo=repo)
    if hist:
        raise Refusal(f"REFUSE R4: a runs artifact or lock was committed before ({hist[:3]}) -- consumed")
    (NS / LOCK_REL).parent.mkdir(parents=True, exist_ok=True)
    try:
        fd = os.open(NS / LOCK_REL, os.O_CREAT | os.O_EXCL | os.O_WRONLY,
                     stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)
    except FileExistsError:
        raise Refusal("REFUSE R4: the execution lock exists -- the execution is consumed")
    os.write(fd, (json.dumps(meta, sort_keys=True) + "\n").encode())
    os.close(fd)


# ---------------------------------------------------------------------------------------------
# the parallel cover (workers see one initial box each; the refinement subtree stays in the worker)
# ---------------------------------------------------------------------------------------------
_W = {}


def _worker_init(cands, params):
    _W["cands"], _W["params"] = cands, params


def _worker_box(args):
    band, s, e, theta, axis, order = args
    bx = KR.Box(band, s, e, theta=theta, axis=axis, order=order)
    return CE.refine_box(bx, _W["cands"], _W["params"])


def _box_args(bx: KR.Box):
    return (bx.band, bx.s, bx.e, bx.theta, bx.axis, bx.N)


def process_tree_rss_kb(root_pid: int, ps: str = PS):
    """(total resident KiB, sorted pids) of root_pid and ALL its live descendants, from ONE snapshot
    of the whole process table -- so workers started after monitoring began, replacements of crashed
    workers, changed PIDs and briefly overlapping old/new workers are all counted (overlap is
    counted twice: conservative). None (accounting impossible) if the table cannot be read, a line
    cannot be parsed, or root_pid is absent."""
    try:
        r = subprocess.run([ps, "-A", "-o", "pid=,ppid=,rss="], capture_output=True, text=True, timeout=60)
    except (OSError, subprocess.SubprocessError):
        return None
    if r.returncode != 0:
        return None
    kids, rss = {}, {}
    for line in r.stdout.splitlines():
        parts = line.split()
        if len(parts) != 3 or not all(x.isdigit() for x in parts):
            return None
        pid, ppid, kb = (int(x) for x in parts)
        rss[pid] = kb
        kids.setdefault(ppid, []).append(pid)
    if root_pid not in rss:
        return None
    seen, stack = set(), [root_pid]
    while stack:
        q = stack.pop()
        if q not in seen:
            seen.add(q)
            stack.extend(kids.get(q, []))
    return sum(rss[q] for q in seen), sorted(seen)


def memory_status(root_pid: int, cap_kb: int, ps: str = PS) -> tuple:
    """('OK' | 'RESOURCE_CAP_MEMORY' | 'RESOURCE_ACCOUNTING_FAILED', accounting or None)."""
    acct = process_tree_rss_kb(root_pid, ps)
    if acct is None:
        return "RESOURCE_ACCOUNTING_FAILED", None
    return ("RESOURCE_CAP_MEMORY" if acct[0] > cap_kb else "OK"), acct


def parallel_cover(e_lo: F, e_hi: F, cands: list, params: dict, caps: dict, t_start: float, log) -> dict:
    import multiprocessing as mp
    boxes = CE.initial_boxes(e_lo, e_hi, params["splits"], params["tm_order"])
    ctx = mp.get_context("spawn")
    acc, done = None, 0
    mem = {"samples": 0, "max_rss_kb": 0, "pids_seen": set()}
    with ctx.Pool(caps["workers"], initializer=_worker_init, initargs=(cands, params)) as pool:
        it = pool.imap_unordered(_worker_box, [_box_args(b) for b in boxes], chunksize=1)
        last_mem = 0.0
        while done < len(boxes):
            if time.time() - last_mem > 30:        # the LIVE process tree, every 30 s (and at start)
                last_mem = time.time()
                status, acct = memory_status(os.getpid(), caps["rss_kb"])
                if status != "OK":
                    pool.terminate()
                    return {"status": status}
                mem["samples"] += 1
                mem["max_rss_kb"] = max(mem["max_rss_kb"], acct[0])
                mem["pids_seen"].update(acct[1])
            try:
                r = it.next(timeout=30)
            except mp.TimeoutError:
                r = None
            if time.time() - t_start > caps["wall_seconds"]:
                pool.terminate()
                return {"status": "RESOURCE_CAP_WALL"}
            if r is None:
                continue
            done += 1
            acc = CE.merge(acc, r)
            if done % 20 == 0 or done == len(boxes):
                log(f"    initial boxes {done}/{len(boxes)}, boxes evaluated {acc['evaluated']}, "
                    f"{time.time() - t_start:.0f}s")
    return {"status": "COMPLETE", "lam": acc["lam"], "leaves": acc["leaves"], "boxes_evaluated": acc["evaluated"],
            "leaves_over_tolerance": acc["unmet"], "worst_box": acc["worst"], "initial_boxes": len(boxes),
            "resource_accounting": {"memory_samples": mem["samples"], "max_tree_rss_kb": mem["max_rss_kb"],
                                    "distinct_pids_seen": len(mem["pids_seen"])}}


def verify_cover_and_accounting(fz: dict) -> None:
    """R6 (cover) and R7 (accounting), before any science: the frozen initial cover is complete for
    the upper-closed band convention, and the live process tree's memory can be read."""
    P = fz["frozen_parameters"]
    lo, hi = MD.cell_block()
    problems = CE.verify_cover(CE.initial_boxes(lo, hi, P["splits"], P["tm_order"]))
    if problems:
        raise Refusal(f"REFUSE R6: the frozen cover is not complete: {problems}")
    if memory_status(os.getpid(), fz["resource_caps"]["rss_kb"])[0] != "OK":
        raise Refusal("REFUSE R7: memory accounting of the process tree is not available (or over cap)")


def certify_block(lo: F, hi: F, fz: dict, premise: dict, log) -> dict:
    """The frozen pipeline over [lo, hi]: n_sub equal sub-blocks, each with its own float proposal at
    its centre, exact candidates, the parallel cover, the atom bounds and the propagation; the cell
    bounds are the MAXIMA over the sub-blocks (which tile [lo, hi] exactly)."""
    P, caps = fz["frozen_parameters"], fz["resource_caps"]
    kappa = MD.kernel_norms()
    t_start = time.time()
    subs, D1, D2 = [], None, None
    for idx, (a, b) in enumerate(CE.sub_blocks(lo, hi, P["sub_blocks"])):
        log(f"  sub-block {idx + 1}/{P['sub_blocks']}: proposal")
        ec, de = (a + b) / 2, (b - a) / 2
        fp = P["float"]
        t0 = time.time()
        prop = FL.propose(float(ec), n=fp["n"], n4=fp["n4"], ns=fp["ns"], nt=fp["nt"], q=fp["q"])
        cands = [FL.exact_candidate(prop["basis"], c, bits=fp["bits"]) for c in prop["coeffs"]]
        log(f"  sub-block {idx + 1}: cover ({time.time() - t0:.0f}s proposal)")
        cov = parallel_cover(a, b, cands, P, caps, t_start, log)
        if cov["status"] != "COMPLETE":
            return {"status": "NOT_CERTIFIED", "reason": cov["status"], "sub_blocks_completed": idx}
        av = CE.atom_values(cands, de)
        pr = CE.propagate(cov["lam"], premise["C_T"], premise["tau"], kappa)
        d1, d2 = av[1] + pr["err_D1"], av[2] + pr["err_D2"]
        D1 = d1 if D1 is None else max(D1, d1)
        D2 = d2 if D2 is None else max(D2, d2)
        subs.append({"e_lo": str(a), "e_hi": str(b), "D1": str(d1), "D2": str(d2),
                     "abs_D1e_atom_bound": str(av[1]), "abs_D2e_atom_bound": str(av[2]),
                     "atom_candidate_values": [str(x) for x in av[0]],
                     "lam": [str(x) for x in cov["lam"]],
                     "propagation": {k: str(v) for k, v in pr.items()},
                     "cover": {k: cov[k] for k in ("initial_boxes", "leaves", "boxes_evaluated",
                                                   "leaves_over_tolerance", "worst_box")},
                     "resource_accounting": cov["resource_accounting"],
                     "float_proposal": {"discrete_residual": prop["discrete_residual"],
                                        "nodes": prop["nodes"], "unknowns": prop["unknowns"]},
                     "candidates": {f"D{j}": {str(k): {",".join(map(str, e)) if isinstance(e, tuple) else str(e): str(c)
                                                      for e, c in pol.items()}
                                              for k, pol in cand.items()} for j, cand in enumerate(cands)}})
    return {"status": "CERTIFIED", "D1": D1, "D2": D2, "sub_blocks": subs,
            "seconds": time.time() - t_start}


def statements(lo: F, hi: F, premise: dict, P: dict) -> dict:
    """The propositions this run proves, built from the N9 semantics (c11rd_model) and this run's own
    identity -- never from the original's record."""
    out = {}
    for k in ("D1", "D2"):
        out[k] = {"constant": k, "quantity": MD.QUANTITY[k], "kernel": "Khat_e", "convention": "atom_removed",
                  "direction": "UPPER_BOUND", "state_set": MD.STATE_SET_R, "proposition": MD.PROPOSITION[k],
                  "drift_domain": [str(lo), str(hi)],
                  "aggregation": {"method": "max_over_sub_blocks", "sub_blocks": P["sub_blocks"]},
                  "dependencies": list(MD.DEPENDENCIES),
                  "dependency_provenance": {
                      d: {"kind": "DEPENDENCY_ON_ACCEPTED_C11R_CERTIFICATE (not an independent reproduction)",
                          "certificate": "C11R F_H", "value": str(premise["C_T"] if d.startswith("C_T") else premise["tau"]),
                          "source": premise["source"]} for d in MD.DEPENDENCIES},
                  "producer": {"module": "c11rd_runs.py", "route": MD.ROUTE,
                               "file_sha256": sha256(HERE / "c11rd_runs.py"),
                               "certificate_id": "C11RD_D1D2"}}
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=("real", "nontarget"), required=True)
    ap.add_argument("--authorization-review-commit")
    ap.add_argument("--out")
    a = ap.parse_args(argv)
    if a.mode == "nontarget":                    # checked before anything is loaded
        if not a.out:
            raise Refusal("REFUSE: --out is required in nontarget mode")
        if NS.resolve() in pathlib.Path(a.out).resolve().parents:
            raise Refusal("REFUSE: a rehearsal never writes inside the C11RD namespace")
    fz = load_freeze()
    verify_code(fz)
    verify_loaded_modules()
    log = lambda s: print(time.strftime("%H:%M:%S"), s, flush=True)
    premise = MD.c11r_fh_premise()
    verify_cover_and_accounting(fz)
    if a.mode == "nontarget":
        out = pathlib.Path(a.out).resolve()
        lo, hi = (F(x) for x in fz["nontarget_rehearsal_block"])
        tlo, thi = MD.cell_block()
        if not (lo > thi or hi < tlo):
            raise Refusal("REFUSE: the rehearsal block meets cell 306's block")
        res = certify_block(lo, hi, fz, premise, log)
        rec = {"schema": "c11rd.rehearsal.v1", "mode": "nontarget", "block": [str(lo), str(hi)],
               "NOT_A_CERTIFICATE": "the C11R F_H premise is cell 306's; on this block the propagation "
                                    "is a sizing exercise of the frozen code path only",
               "result": res, "code_sha256": fz["code_sha256"]}
        out.write_text(json.dumps(rec, indent=1, sort_keys=True, default=str) + "\n")
        log(f"rehearsal written: {out}")
        return 0
    # ---- real ----
    g = verify_grant(fz, a.authorization_review_commit)
    verify_clean()
    lo, hi = MD.cell_block()
    if [str(lo), str(hi)] != fz["target"]["drift_block"] or fz["target"]["cell"] != 306:
        raise Refusal("REFUSE R6: the statement table's block is not the frozen target")
    head = git("rev-parse", "HEAD")
    started = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    verify_loaded_modules()
    load_at_start = list(os.getloadavg())
    take_lock({"started_utc": started, "head": head, "grant_sha256": sha256(NS / GRANT_REL),
               "freeze_commit": g["freeze_commit"], "host": g["host"], "loadavg_at_start": load_at_start})
    log(f"C11RD execution started at HEAD {head}; the execution is now consumed")
    res = certify_block(lo, hi, fz, premise, log)
    rec = {"schema": "c11rd.runs.v1", "campaign": "C11RD", "cell": 306, "mode": "real",
           "started_utc": started, "finished_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "head": head, "freeze_commit": g["freeze_commit"], "code_sha256": fz["code_sha256"],
           "premise": {k: (str(v) if isinstance(v, F) else v) for k, v in premise.items()},
           "kernel_norms": {str(k): str(v) for k, v in MD.kernel_norms().items()},
           "status": res["status"],
           "targets": {k: {"status": res["status"], "value": (str(res[k]) if res["status"] == "CERTIFIED" else None),
                           "statement": st} for k, st in statements(lo, hi, premise, fz["frozen_parameters"]).items()},
           "execution": res, "host": dict(g["host"], loadavg_at_start=load_at_start),
           "worktree": g["worktree"], "grant_sha256": sha256(NS / GRANT_REL),
           "authorization_review_commit": a.authorization_review_commit}
    verify_loaded_modules()
    tmp = NS / (RUNS_REL + ".partial")
    tmp.write_text(json.dumps(rec, indent=1, sort_keys=True, default=str) + "\n")
    os.replace(tmp, NS / RUNS_REL)
    log(f"runs artifact written ({res['status']}); seal it BEFORE any interpretation")
    return 0 if res["status"] == "CERTIFIED" else 3


if __name__ == "__main__":
    sys.exit(main())
