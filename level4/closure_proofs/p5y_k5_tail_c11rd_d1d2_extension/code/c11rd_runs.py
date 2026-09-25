"""C11RD -- the runner: the ONE cell-306 D1/D2 execution, and the non-target rehearsal of the same code.

Nothing runs at import. Every parameter comes from protocol/C11RD_FREEZE.json; there are no CLI
overrides of science parameters.

    python3 -I -S -B c11rd_runs.py --mode nontarget --out PATH
        Rehearsal on the freeze's non-target block (C11R's NT block; no grant, no lock; refuses to
        write inside the namespace).
    python3 -I -S -B c11rd_runs.py --mode real --grant config/C11RD_GRANT.json
        The target execution. Refuses unless (freeze section P / V):
          R1 every frozen code file's sha256, and C7's c7_gaussian.py's, equals the freeze's;
          R2 the grant exists, says ALLOW, binds the freeze commit, the frozen code hashes, cell 306's
             block, max_executions = 1 and this host/runtime, and the freeze commit is an ancestor of
             HEAD with a byte-identical freeze file;
          R3 the namespace has no uncommitted change;
          R0 the pre-import barrier (below) and the loaded-module check;
          R4 no execution lock and no runs artifact exist, and none was EVER committed on any ref or
             reflog entry -- the lock is created EXCLUSIVELY before any science and is never removed:
             a started execution is consumed whatever its outcome;
          R5 the premise loader verifies C11R's accepted F_H certificate (blob-bound);
          R6 the drift block read from C11R's frozen statement table equals the freeze's target.
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
FREEZE_REL = "protocol/C11RD_FREEZE.json"
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
    """Commits on ANY ref or reflog entry that ever touched one of the paths (full history)."""
    r = git_run("rev-list", "--all", "--reflog", "--full-history", "--", *rels, repo=repo)
    if r.returncode != 0:
        raise Refusal(f"REFUSE R4: cannot read the history: {r.stderr.strip()}")
    return r.stdout.split()


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
    if fz.get("schema") != "c11rd.freeze.v1":
        raise Refusal("REFUSE: not a C11RD freeze")
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


def verify_grant(fz: dict, grant_path: pathlib.Path) -> dict:
    g = json.loads(grant_path.read_text())
    lo, hi = MD.cell_block()
    problems = []
    if g.get("decision") != "ALLOW" or g.get("campaign") != "C11RD":
        problems.append("the grant is not an ALLOW for C11RD")
    if g.get("code_sha256") != fz["code_sha256"]:
        problems.append("the grant does not bind the frozen code hashes")
    if g.get("target") != {"cell": 306, "e_lo": str(lo), "e_hi": str(hi)}:
        problems.append("the grant's target is not cell 306's frozen block")
    if g.get("max_executions") != 1:
        problems.append("the grant does not bind exactly one execution")
    if g.get("host") != {"platform": sys.platform, "python": sys.version.split()[0]}:
        problems.append("the grant's host/runtime is not this one")
    fc = g.get("freeze_commit", "")
    if git_run("rev-parse", "--is-shallow-repository").stdout.strip() != "false":
        problems.append("the repository is shallow (history incomplete)")
    if len(fc) != 40 or git_run("merge-base", "--is-ancestor", fc, "HEAD").returncode != 0:
        problems.append("the freeze commit is not an ancestor of HEAD")
    else:
        at_fc = subprocess.run([*GIT, "-C", str(MD.REPO), "show", f"{fc}:{MD.NS_REL}/{FREEZE_REL}"],
                               capture_output=True)
        if at_fc.returncode != 0 or at_fc.stdout != (NS / FREEZE_REL).read_bytes():
            problems.append("the freeze file is not byte-identical to the one at the freeze commit")
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


def _rss_kb(pids) -> int:
    if not pids:
        return 0
    out = subprocess.run(["ps", "-o", "rss=", "-p", ",".join(map(str, pids))], capture_output=True, text=True)
    return sum(int(x) for x in out.stdout.split() if x.isdigit())


def parallel_cover(e_lo: F, e_hi: F, cands: list, params: dict, caps: dict, t_start: float, log) -> dict:
    import multiprocessing as mp
    boxes = CE.initial_boxes(e_lo, e_hi, params["splits"], params["tm_order"])
    ctx = mp.get_context("spawn")
    acc, done = None, 0
    with ctx.Pool(caps["workers"], initializer=_worker_init, initargs=(cands, params)) as pool:
        it = pool.imap_unordered(_worker_box, [_box_args(b) for b in boxes], chunksize=1)
        pids = [p.pid for p in pool._pool]
        last_mem = 0.0
        while done < len(boxes):
            try:
                r = it.next(timeout=30)
            except mp.TimeoutError:
                r = None
            if time.time() - t_start > caps["wall_seconds"]:
                pool.terminate()
                return {"status": "RESOURCE_CAP_WALL"}
            if time.time() - last_mem > 30:
                last_mem = time.time()
                if _rss_kb(pids + [os.getpid()]) > caps["rss_kb"]:
                    pool.terminate()
                    return {"status": "RESOURCE_CAP_MEMORY"}
            if r is None:
                continue
            done += 1
            acc = CE.merge(acc, r)
            if done % 20 == 0 or done == len(boxes):
                log(f"    initial boxes {done}/{len(boxes)}, boxes evaluated {acc['evaluated']}, "
                    f"{time.time() - t_start:.0f}s")
    return {"status": "COMPLETE", "lam": acc["lam"], "leaves": acc["leaves"], "boxes_evaluated": acc["evaluated"],
            "leaves_over_tolerance": acc["unmet"], "worst_box": acc["worst"], "initial_boxes": len(boxes)}


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
    ap.add_argument("--grant")
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
    if not a.grant:
        raise Refusal("REFUSE R2: --grant is required")
    g = verify_grant(fz, (MD.REPO / a.grant) if not os.path.isabs(a.grant) else pathlib.Path(a.grant))
    verify_clean()
    lo, hi = MD.cell_block()
    if [str(lo), str(hi)] != fz["target"]["drift_block"] or fz["target"]["cell"] != 306:
        raise Refusal("REFUSE R6: the statement table's block is not the frozen target")
    head = git("rev-parse", "HEAD")
    started = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    verify_loaded_modules()
    take_lock({"started_utc": started, "head": head, "grant_sha256": sha256(pathlib.Path(a.grant)
                                                                           if os.path.isabs(a.grant) else MD.REPO / a.grant),
               "freeze_commit": g["freeze_commit"]})
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
           "execution": res, "host": {"python": sys.version.split()[0], "platform": sys.platform}}
    verify_loaded_modules()
    tmp = NS / (RUNS_REL + ".partial")
    tmp.write_text(json.dumps(rec, indent=1, sort_keys=True, default=str) + "\n")
    os.replace(tmp, NS / RUNS_REL)
    log(f"runs artifact written ({res['status']}); seal it BEFORE any interpretation")
    return 0 if res["status"] == "CERTIFIED" else 3


if __name__ == "__main__":
    sys.exit(main())
