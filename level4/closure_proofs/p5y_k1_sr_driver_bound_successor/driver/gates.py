"""Pre-production gates for the SR cap-authorized, driver-bound successor.

Every gate FAILS CLOSED: it raises GateFailure unless it can positively verify
its property. Nothing here performs scientific computation.
"""
from __future__ import annotations

import hashlib
import json
import os
import platform
import subprocess
import sys
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
ROOT = NS.parents[2]
CHECKPOINT_PATH = NS / "config/PRE_RESULT_CHECKPOINT.json"

THREAD_VARS = ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
               "NUMEXPR_NUM_THREADS", "BLIS_NUM_THREADS", "VECLIB_MAXIMUM_THREADS")


class GateFailure(RuntimeError):
    """A pre-production gate refused to admit the run."""


def sha256_file(p) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def canonical(obj) -> bytes:
    return (json.dumps(obj, sort_keys=True, separators=(",", ":"),
                       ensure_ascii=True) + "\n").encode("ascii")


def load_checkpoint(path=None) -> dict:
    path = Path(path) if path else CHECKPOINT_PATH
    if not path.exists():
        raise GateFailure(f"checkpoint absent: {path}")
    cp = json.loads(path.read_text())
    stored = cp.get("checkpoint_sha256")
    body = {k: v for k, v in cp.items() if k != "checkpoint_sha256"}
    actual = hashlib.sha256(canonical(body)).hexdigest()
    if stored != actual:
        raise GateFailure(
            f"checkpoint self-hash mismatch: stored {stored} != actual {actual}")
    return cp


# ----------------------------------------------------------------- A. repository
def gate_repository(cp: dict, *, repo=None) -> dict:
    repo = Path(repo) if repo else ROOT
    def git(*a):
        return subprocess.check_output(["git", "-C", str(repo)] + list(a)).decode().strip()
    head = git("rev-parse", "HEAD")
    branch = git("rev-parse", "--abbrev-ref", "HEAD")
    dirty = [l for l in git("status", "--porcelain").splitlines() if l.strip()]
    exp = cp["repository_identity"]
    if branch != exp["branch"]:
        raise GateFailure(f"branch {branch} != {exp['branch']}")
    # The producer commit is recorded AFTER the freeze commit exists, so a
    # checkpoint may legitimately declare it as null until bound by the tag.
    if exp.get("producer_commit") and head != exp["producer_commit"]:
        raise GateFailure(f"HEAD {head} != producer_commit {exp['producer_commit']}")
    for rel, want in cp["bound_artifact_sha256"].items():
        got = sha256_file(NS / rel)
        if got != want:
            raise GateFailure(f"bound artifact {rel}: {got} != {want}")
    allowed = set(exp.get("allowed_dirty_paths", []))
    offending = [l for l in dirty
                 if not any(l[3:].startswith(a) for a in allowed)]
    if offending:
        raise GateFailure(f"worktree not clean enough: {offending[:5]}")
    return {"branch": branch, "head": head, "dirty_entries": len(dirty),
            "bound_artifacts_verified": len(cp["bound_artifact_sha256"])}


# -------------------------------------------------------------------- B. runtime
def venv_root() -> Path:
    """The worktree root that actually holds the live venv.

    The runtime contract hashes the backend libraries by a path relative to that
    root. This driver's own worktree need not contain the venv (a git worktree
    for a parallel branch typically does not), so the root is derived from the
    LOADED numpy rather than from this file's location. Getting this wrong makes
    the contract hash over an EMPTY backend-library set, which would silently
    weaken the strongest runtime check.
    """
    import numpy
    marker = "/level4/.venv/"
    real = os.path.realpath(numpy.__file__)
    if marker not in real:
        raise GateFailure(f"cannot locate the level4 venv from numpy at {real}")
    return Path(real.split(marker)[0])


def gate_runtime(cp: dict) -> dict:
    req = cp["runtime_identity"]
    vroot = venv_root()
    sys.path.insert(0, str(vroot / "level4/closure_proofs/"
                           "p5y_k1_cusum_aux4_fullcover/code"))
    import runtime_identity as RI                                   # noqa: E402
    live = RI.contract()
    live_hash = RI.contract_hash(live)
    if live_hash != req["required_runtime_contract_hash"]:
        raise GateFailure(
            f"runtime contract {live_hash} != required "
            f"{req['required_runtime_contract_hash']}")
    for key in ("cpython_version", "numpy_version", "python_flint_version",
                "openblas_runtime_corename"):
        if live.get(key) != req[key]:
            raise GateFailure(f"runtime {key}: {live.get(key)} != {req[key]}")
    for rel, want in req["backend_libraries"].items():
        got = live["backend_libraries"].get(rel)
        if got != want:
            raise GateFailure(f"backend library {rel}: {got} != {want}")
    import flint                                                     # noqa: E402
    if flint.__FLINT_VERSION__ != req["flint_version"]:
        raise GateFailure(f"FLINT {flint.__FLINT_VERSION__} != {req['flint_version']}")
    if int(flint.ctx.threads) != 1:
        raise GateFailure(f"flint.ctx.threads={flint.ctx.threads} != 1")
    host = cp["host_scope"]
    if host["scope"] != "AWS_ONLY":
        raise GateFailure(f"host scope {host['scope']} is not AWS_ONLY")
    vendor = Path("/sys/class/dmi/id/sys_vendor")
    v = vendor.read_text().strip() if vendor.exists() else ""
    if v not in host["accepted_sys_vendor"]:
        raise GateFailure(f"AWS_ONLY violated: sys_vendor {v!r} not in "
                          f"{host['accepted_sys_vendor']}")
    return {"runtime_contract_hash": live_hash, "sys_vendor": v,
            "venv_root": str(vroot),
            "flint_version": flint.__FLINT_VERSION__,
            "openblas_runtime_corename": live["openblas_runtime_corename"]}


# -------------------------------------------------------------------- C. threads
def gate_threads(cp: dict, env=None) -> dict:
    env = os.environ if env is None else env
    req = cp["thread_contract"]
    if tuple(req["variables"]) != THREAD_VARS:
        raise GateFailure("thread variable set drifted from the frozen six")
    bad = {v: env.get(v) for v in THREAD_VARS if env.get(v) != req["required_value"]}
    if bad:
        raise GateFailure(f"thread contract violated: {bad}")
    return {"variables_enforced": list(THREAD_VARS), "value": req["required_value"]}


# ------------------------------------------------------------------- D. topology
def physical_cores(sysfs="/sys/devices/system/cpu") -> list[int]:
    """One representative CPU per physical core, ascending. SMT siblings excluded."""
    base = Path(sysfs)
    seen, out = set(), []
    for d in sorted(base.glob("cpu[0-9]*"), key=lambda p: int(p.name[3:])):
        sib = d / "topology/thread_siblings_list"
        if not sib.exists():
            continue
        members = []
        for part in sib.read_text().strip().split(","):
            if "-" in part:
                a, b = part.split("-")
                members += list(range(int(a), int(b) + 1))
            else:
                members.append(int(part))
        key = tuple(sorted(members))
        if key in seen:
            continue
        seen.add(key)
        out.append(min(members))
    return sorted(out)


def gate_topology(cp: dict, *, cores=None) -> dict:
    top = cp["worker_topology"]
    cores = physical_cores() if cores is None else cores
    if len(cores) < top["workers"]:
        raise GateFailure(
            f"only {len(cores)} physical cores for {top['workers']} workers")
    assign = cores[:top["workers"]]
    if top["deterministic_core_assignment"] and assign != top["core_assignment"]:
        raise GateFailure(
            f"core assignment {assign} != frozen {top['core_assignment']}")
    if top["use_smt_siblings"]:
        raise GateFailure("checkpoint would permit SMT siblings; not qualified")
    # every assigned cpu must be a distinct physical core
    if len(set(assign)) != len(assign):
        raise GateFailure("duplicate core in assignment")
    return {"workers": top["workers"], "core_assignment": assign,
            "physical_cores_available": len(cores), "smt_used": False}


# ---------------------------------------------------------------------- E. scope
def gate_scope(cp: dict) -> dict:
    want = cp["frozen_scope"]
    qual = ROOT / "level4/closure_proofs/p5y_k1_sr_qualification"
    sys.path.insert(0, str(qual / "code"))
    import sr_universe as U                                          # noqa: E402
    a = U.audit()
    if not a["ok"]:
        raise GateFailure(f"SR universe audit failed: {a['findings']}")
    if a["n_sr_obligations"] != want["obligations"]:
        raise GateFailure(f"obligations {a['n_sr_obligations']} != {want['obligations']}")
    if a["n_cells"] != want["sr_cells"]:
        raise GateFailure(f"cells {a['n_cells']} != {want['sr_cells']}")
    ids = [U.work_id_str(w) for w in U.work_ids()]
    import sr_provenance as PR                                       # noqa: E402
    got = PR.sha256_bytes(PR.canonical(ids))
    if got != want["ordered_obligation_ids_sha256"]:
        raise GateFailure(
            f"ordered obligation ids sha256 {got} != {want['ordered_obligation_ids_sha256']}")
    t1r = ROOT / "level4/closure_proofs/p5y_k1_task1r_budget_harness"
    sel = json.loads((t1r / "config/frozen_parameters.json").read_text())["selection"]
    if sel["D_selected"] != want["D"]:
        raise GateFailure(f"D {sel['D_selected']} != {want['D']}")
    if sel["Z_selected"] != want["Z"]:
        raise GateFailure(f"Z {sel['Z_selected']} != {want['Z']}")
    sys.path.insert(0, str(t1r / "code"))
    import harness as H                                              # noqa: E402
    if H.CAND_DEGREE != want["cand_degree"]:
        raise GateFailure(f"cand_degree {H.CAND_DEGREE} != {want['cand_degree']}")
    if H.PROD_BITS != want["precision_bits"]:
        raise GateFailure(f"precision {H.PROD_BITS} != {want['precision_bits']}")
    o9 = json.loads((ROOT / "level4/closure_proofs/p5y_k1_sr_backend_o9_successor"
                     "/config/protocol.json").read_text())
    fs, cen = o9["frozen_scope"], o9["census"]
    for k_live, k_want in (("live_patches", "live_patches"), ("panels", "panels")):
        if fs[k_live] != want[k_want]:
            raise GateFailure(f"{k_want} {fs[k_live]} != {want[k_want]}")
    c = cp["census"]
    if cen["distinct_candidates"] != c["distinct_candidates"]:
        raise GateFailure("candidate census drift")
    if cen["certified_contracts"] != c["certified_contracts"]:
        raise GateFailure("contract census drift")
    if cen["by_moment_shift"] != c["by_moment_shift"]:
        raise GateFailure("moment-shift census drift")
    if sum(c["by_moment_shift"].values()) != c["certified_contracts"]:
        raise GateFailure("moment shifts do not sum to the contract census")
    if cp["backend"]["accepted"] != "O9":
        raise GateFailure(f"backend {cp['backend']['accepted']} != O9")
    return {"cells": a["n_cells"], "obligations": a["n_sr_obligations"],
            "obligations_per_cell": a["obligations_per_cell"],
            "D": sel["D_selected"], "Z": sel["Z_selected"],
            "cand_degree": H.CAND_DEGREE, "precision_bits": H.PROD_BITS,
            "live_patches": fs["live_patches"], "panels": fs["panels"],
            "census": c, "backend": "O9"}
