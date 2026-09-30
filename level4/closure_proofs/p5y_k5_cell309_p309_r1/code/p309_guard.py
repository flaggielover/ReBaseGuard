"""Band-scoped producer-side guard for P309 (FC2(a); spec fc2/FC2_SPEC_R2.md; formal campaign p5y_k5_cell309_p309_r1).

Written by the coordinator (producer side).  The independent verifier variant implements the same admission rules
separately, from the spec only; neither reads the other.

WHAT THIS FILE IS AUTHORIZED TO DO (owner rulings 2, 2026-09-30): define and test the admission mechanism.  It issues
no grant, lifts no quarantine, writes no grant, creates/moves/deletes no ref, and evaluates nothing.  Until the
owner's later explicit grant exists in this repository, every REAL-band interval is refused.

  admission_decision(item, *, ctx=PRODUCTION, mode="official") -> (decision, reason)
      item = {"geometry": (h, k), "lo": ..., "hi": ...};  decision in {"ADMIT", "REFUSE", "NOT_BANDED"}
  guard_interval(geometry, lo, hi, *, ctx=PRODUCTION)       -> None, or raises QuarantineRefusal
  producer_adapter(ctx=PRODUCTION)                          -> object with the q309_guard API used by srk_certify
  TestContext(sandbox_root)                                 -> the synthetic test context (spec section 2.2)

Fail closed: every check is inside one try-block; any exception is a REFUSE.  There is no default ADMIT.
"""
from __future__ import annotations

import datetime
import hashlib
import json
import os
import platform
import socket
import subprocess
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve()

# ---- spec section 1: band tables (compiled constants) ---------------------------------------------------------
REAL_BAND = ((F(6, 5), F(13, 5)), (F(-13, 5), F(-6, 5)))   # q309: literal-ok (quarantine band definition; refusal)
REAL_GEOMETRY = (F(5), F(1, 2))
TEST_BAND = ((F(341, 1024), F(201, 512)), (F(-201, 512), F(-341, 1024)))   # hull of the declared synthetic h3 decoy cell
TEST_GEOMETRY = (F(3), F(1, 2))

# ---- spec section 2.1: production context (hard-coded; the only occurrence of the marker literal) ---------------
PRODUCTION_MARKER = "refs/p5y-k5-cell309-p309-r1/target-consumed"  # q309: literal-ok (inert marker NAME; read-only use)
PENDING_REF = "refs/p5y-k5-cell309-p309-r1/pending-result"  # q309: literal-ok (inert pending-ref NAME; read-only here)
_PROD_NAMESPACE = "refs/p5y-k5-cell309-p309-r1/"  # q309: literal-ok (ref namespace, read-only use)
_FNS_REL = "level4/closure_proofs/p5y_k5_cell309_p309_r1/"
_PROD_GRANT_PATH = _FNS_REL + "authorization/P309_GRANT.json"
_PROD_MANIFEST_PATH = _FNS_REL + "freeze/P309_FREEZE_MANIFEST.json"
_PROD_CELL = 309  # q309: literal-ok (the grant's cell field must equal this; comparison only)

# ---- spec section 2.2: test context constants ---------------------------------------------------------------------
TEST_MARKER = "refs/p309-test/TEST_ONLY_DO_NOT_EXECUTE_P309_MARKER"
TEST_PENDING_REF = "refs/p309-test/TEST_ONLY_DO_NOT_EXECUTE_P309_PENDING"
_TEST_NAMESPACE = "refs/p309-test/"
_TEST_GRANT_PATH = "TEST_ONLY/P309_TEST_GRANT.json"
_TEST_MANIFEST_PATH = "TEST_ONLY/P309_TEST_FREEZE_MANIFEST.json"
_TEST_CELL = "TEST_ONLY_DO_NOT_EXECUTE"

_HEX40 = frozenset("0123456789abcdef")


class QuarantineRefusal(RuntimeError):
    """Raised by guard_interval when a band-meeting interval is not admitted."""


def _git(repo: Path, *args: str) -> str:
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env["LC_ALL"] = "C"
    r = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, env=env)
    if r.returncode != 0:
        raise RuntimeError(f"git {args[0]} failed")
    return r.stdout


def _git_bytes(repo: Path, *args: str) -> bytes:
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    r = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, env=env)
    if r.returncode != 0:
        raise RuntimeError(f"git {args[0]} failed")
    return r.stdout


def _git_ok(repo: Path, *args: str) -> bool:
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, env=env).returncode == 0


def _toplevel(p: Path) -> Path:
    return Path(_git(p, "rev-parse", "--show-toplevel").strip()).resolve()


def _common_dir(p: Path) -> Path:
    c = _git(p, "rev-parse", "--git-common-dir").strip()
    cp = Path(c)
    return (cp if cp.is_absolute() else (p / cp)).resolve()


def own_repo() -> Path:
    return _toplevel(HERE.parent)


def own_relpath() -> str:
    return str(HERE.relative_to(own_repo()))


def own_id() -> str:
    return "sha256:" + hashlib.sha256(HERE.read_bytes()).hexdigest()


def host_id() -> str:
    mid = Path("/etc/machine-id").read_bytes().strip()
    return hashlib.sha256(b"machine-id:" + mid + b"\nhostname:" + socket.gethostname().encode()).hexdigest()


def outward_hull(lo: F, hi: F, bits: int = 10) -> tuple:
    s = 1 << bits
    return (F((lo * s).__floor__(), s), F(-((-hi * s).__floor__()), s))


# ---- contexts --------------------------------------------------------------------------------------------------
class _Production:
    kind = "PRODUCTION"
    schema = "P309_GRANT/1"
    campaign = "p5y_k5_cell309_p309_r1"
    cell = _PROD_CELL
    geometry = REAL_GEOMETRY
    band = REAL_BAND
    marker_ref = PRODUCTION_MARKER
    pending_ref = PENDING_REF
    ref_namespace = _PROD_NAMESPACE
    grant_path = _PROD_GRANT_PATH
    manifest_path = _PROD_MANIFEST_PATH

    def __init__(self):
        if globals().get("PRODUCTION") is not None:
            raise RuntimeError("the production context is a singleton")

    @property
    def repo(self) -> Path:
        return own_repo()

    def __setattr__(self, *_):
        raise AttributeError("the production context is immutable")


PRODUCTION = None
PRODUCTION = _Production()


class TestContext:
    kind = "TEST"
    schema = "P309_TEST_GRANT/1"
    campaign = _TEST_CELL
    cell = _TEST_CELL
    geometry = TEST_GEOMETRY
    band = TEST_BAND
    marker_ref = TEST_MARKER
    pending_ref = TEST_PENDING_REF
    ref_namespace = _TEST_NAMESPACE
    grant_path = _TEST_GRANT_PATH
    manifest_path = _TEST_MANIFEST_PATH
    __test__ = False                  # not a pytest class

    def __init__(self, sandbox_root):
        sb = _toplevel(Path(sandbox_root).resolve())
        own = own_repo()
        if sb == own:
            raise ValueError("TestContext refused: the sandbox is this repository")
        if _common_dir(sb) == _common_dir(own):
            raise ValueError("TestContext refused: the sandbox is a worktree of this repository")
        prod_refs = _git(sb, "for-each-ref", "--format=%(refname)", _PROD_NAMESPACE).split()
        if prod_refs:
            raise ValueError("TestContext refused: the sandbox holds a production-namespace ref")
        object.__setattr__(self, "_repo", sb)

    @property
    def repo(self) -> Path:
        return self._repo

    def __setattr__(self, *_):
        raise AttributeError("a test context is immutable")


# ---- band classification ---------------------------------------------------------------------------------------
def _meets(ranges, lo: F, hi: F) -> bool:
    return any(not (hi < a or lo > b) for a, b in ranges)


def classify(geometry, lo, hi) -> str:
    """'REAL' (geometry-blind), 'TEST' (geometry (3, 1/2) only) or 'NONE'."""
    g = (F(geometry[0]), F(geometry[1]))
    lo, hi = F(lo), F(hi)
    if hi < lo:
        lo, hi = hi, lo
    if _meets(REAL_BAND, lo, hi):
        return "REAL"
    if g == TEST_GEOMETRY and _meets(TEST_BAND, lo, hi):
        return "TEST"
    return "NONE"


# ---- grant checks (spec section 3) ------------------------------------------------------------------------------
def _rat(s) -> F:
    if not isinstance(s, str) or not s.strip() or any(c in s for c in ".eE"):
        raise ValueError("not an exact rational string")
    return F(s)


def _hexs(s, n: int) -> bool:
    return isinstance(s, str) and len(s) == n and set(s) <= _HEX40


def _parse_grant(ctx, raw: bytes) -> dict:
    g = json.loads(raw.decode("utf-8"))
    if not isinstance(g, dict):
        raise ValueError("grant is not an object")
    need = ("schema", "campaign", "cell", "geometry", "cell_interval", "drift_hull_Ew", "frozen_commit",
            "frozen_manifest_sha256", "verifier_id", "guard_id", "execution_host", "runtime", "marker_ref",
            "not_after_utc")
    miss = [k for k in need if k not in g]
    if miss:
        raise ValueError(f"grant misses {miss}")
    if g["schema"] != ctx.schema or g["campaign"] != ctx.campaign:
        raise ValueError("grant schema/campaign is not this context's")
    if type(g["cell"]) is not type(ctx.cell) or g["cell"] != ctx.cell:
        raise ValueError("grant cell is not this context's")
    geo = g["geometry"]
    if not isinstance(geo, dict) or set(geo) != {"h", "k"} or (_rat(geo["h"]), _rat(geo["k"])) != ctx.geometry:
        raise ValueError("grant geometry is not this context's")
    for key in ("cell_interval", "drift_hull_Ew"):
        v = g[key]
        if not (isinstance(v, list) and len(v) == 2 and _rat(v[0]) < _rat(v[1])):
            raise ValueError(f"grant {key} malformed")
    if not _hexs(g["frozen_commit"], 40) or not _hexs(g["frozen_manifest_sha256"], 64):
        raise ValueError("grant frozen identity malformed")
    for key in ("verifier_id", "guard_id"):
        v = g[key]
        if not (isinstance(v, str) and v.startswith("sha256:") and _hexs(v[7:], 64)):
            raise ValueError(f"grant {key} malformed")
    eh, rt = g["execution_host"], g["runtime"]
    if not (isinstance(eh, dict) and _hexs(eh.get("host_id_sha256"), 64)):
        raise ValueError("grant execution_host malformed")
    if not (isinstance(rt, dict) and isinstance(rt.get("python"), str)):
        raise ValueError("grant runtime malformed")
    if g["marker_ref"] != ctx.marker_ref:
        raise ValueError("grant marker_ref is not this context's marker")
    if not isinstance(g["not_after_utc"], str):
        raise ValueError("grant not_after_utc malformed")
    datetime.datetime.strptime(g["not_after_utc"], "%Y-%m-%dT%H:%M:%SZ")
    return g


def _check_ew(g: dict) -> tuple:
    c_lo, c_hi = (_rat(x) for x in g["cell_interval"])
    ew = tuple(_rat(x) for x in g["drift_hull_Ew"])
    if outward_hull(c_lo, c_hi) != ew:                                                          # 3 Ew binding
        raise ValueError("Ew is not the outward 2^-10 hull of cell_interval")
    return ew


def _check_frozen_identity(ctx, g: dict, anchor: str) -> None:
    """checks 5 and 6; anchor is the grant commit, or (candidate_check) the would-be parent of the grant commit."""
    repo = ctx.repo
    fc = g["frozen_commit"]                                                                     # 5 frozen identity
    if not _git_ok(repo, "merge-base", "--is-ancestor", fc, anchor):
        raise ValueError("frozen_commit is not an ancestor of the grant commit")
    man = _git_bytes(repo, "show", f"{fc}:{ctx.manifest_path}")
    if hashlib.sha256(man).hexdigest() != g["frozen_manifest_sha256"]:
        raise ValueError("frozen manifest sha256 mismatch")
    pins = {p["path"]: p.get("sha256") for p in json.loads(man.decode("utf-8"))["code_pins"]}
    if pins.get(own_relpath()) != own_id()[7:]:
        raise ValueError("this guard is not pinned (with this sha256) by the frozen manifest")
    if g["guard_id"] != own_id():                                                               # 6 own identity
        raise ValueError("guard_id is not this file")


def _check_expiry_host(g: dict) -> None:
    now = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)                    # 8 expiry
    if now > datetime.datetime.strptime(g["not_after_utc"], "%Y-%m-%dT%H:%M:%SZ"):
        raise ValueError("grant expired")
    if g["execution_host"]["host_id_sha256"] != host_id():                                     # 9 host, runtime
        raise ValueError("execution host mismatch")
    if g["runtime"]["python"] != platform.python_version():
        raise ValueError("runtime mismatch")


def _check_official(ctx, geometry, lo: F, hi: F, *, premarker: bool = False) -> str:
    """Raises on any failed check; returns the grant commit on success.  Order: spec section 3, checks 2-10.
    premarker=True (R4 B3, the driver's dry admission before the marker): check 7 requires an EMPTY marker namespace
    instead of the marker, and the item checks (10, geometry) are not reached; nothing is admitted."""
    repo = ctx.repo
    try:
        raw = _git_bytes(repo, "show", f"HEAD:{ctx.grant_path}")                              # 2 present
    except RuntimeError:
        raise ValueError("no grant at HEAD") from None
    g = _parse_grant(ctx, raw)                                                                 # 2 well formed
    ew = _check_ew(g)                                                                           # 3 Ew binding
    adds = _git(repo, "log", "--format=%H", "--diff-filter=A", "HEAD", "--", ctx.grant_path).split()
    if len(adds) != 1:                                                                          # 4 grant commit
        raise ValueError(f"{len(adds)} commits add the grant")
    gc = adds[0]
    touched = _git(repo, "diff-tree", "--no-commit-id", "--name-only", "-r", gc).split()
    if touched != [ctx.grant_path]:
        raise ValueError("the grant commit touches other paths")
    if _git(repo, "rev-parse", "HEAD").strip() != gc:
        raise ValueError("HEAD is not the grant commit")
    _check_frozen_identity(ctx, g, gc)                                                          # 5, 6
    ns = _git(repo, "for-each-ref", "--format=%(refname)", ctx.ref_namespace).split()          # 7 marker
    if premarker:
        if ns:
            raise ValueError("the marker namespace is not empty before the marker")
    else:
        mk = _git(repo, "rev-parse", "--verify", "--quiet", f"{ctx.marker_ref}^{{commit}}").strip()
        if mk != gc:
            raise ValueError("marker does not name the grant commit")
        if ns != [ctx.marker_ref]:
            raise ValueError("the marker namespace holds other refs (recording begun or consumed)")
    cur = _git(repo, "symbolic-ref", "-q", "HEAD").strip()
    for line in _git(repo, "for-each-ref",
                     "--format=%(refname) %(objectname) %(objecttype) %(*objectname) %(*objecttype)").splitlines():
        parts = line.split()
        name, obj, typ = parts[0], parts[1], parts[2]
        if typ == "tag" and len(parts) == 5:
            obj, typ = parts[3], parts[4]                      # peel annotated tags
        if name in (ctx.marker_ref, cur) or typ != "commit" or obj == gc:
            continue
        if _git_ok(repo, "merge-base", "--is-ancestor", gc, obj):
            raise ValueError(f"a strict descendant of the grant commit exists ({name})")
    _check_expiry_host(g)                                                                       # 8, 9
    if premarker:
        return gc
    if not (ew[0] <= lo and hi <= ew[1]):                                                       # 10 inside Ew
        raise ValueError("interval not inside Ew")
    if (F(geometry[0]), F(geometry[1])) != ctx.geometry:
        raise ValueError("geometry is not the grant's")
    return gc


def admission_decision(item: dict, *, ctx=None, mode: str = "official") -> tuple:
    ctx = PRODUCTION if ctx is None else ctx
    try:
        geometry = (F(item["geometry"][0]), F(item["geometry"][1]))
        lo, hi = F(item["lo"]), F(item["hi"])
        if hi < lo:
            lo, hi = hi, lo
        band = classify(geometry, lo, hi)
        if band == "NONE":
            return "NOT_BANDED", "item meets no band; not an admission question"
        if mode != "official":
            return "REFUSE", "quarantine: the guard has no review mode"
        # 1 band <-> context (structural separation)
        if band == "REAL":
            if ctx is not PRODUCTION:
                return "REFUSE", "quarantine: the REAL band is admissible only in the production context"
            if geometry != REAL_GEOMETRY:
                return "REFUSE", "quarantine: the REAL band is admissible only for geometry (5, 1/2)"
        else:
            if not isinstance(ctx, TestContext) or type(ctx) is not TestContext:
                return "REFUSE", "quarantine: the TEST band is admissible only in a test context"
        gc = _check_official(ctx, geometry, lo, hi)
        return "ADMIT", f"admitted under grant commit {gc[:12]} ({ctx.kind})"
    except Exception as exc:  # noqa: BLE001 - fail closed
        return "REFUSE", f"quarantine: {type(exc).__name__}: {str(exc)[:160]}"


def premarker_check(ctx=None) -> tuple:
    """R4 B3: the official checks that do not need the marker (2-6, 8, 9, and 7 with an empty namespace), for the
    driver's dry admission before the marker.  Returns (ok, reason).  It examines no band item and admits nothing."""
    ctx = PRODUCTION if ctx is None else ctx
    try:
        if ctx is not PRODUCTION and type(ctx) is not TestContext:
            return False, "not a guard context"
        gc = _check_official(ctx, None, None, None, premarker=True)
        return True, f"grant commit {gc[:12]} passes the pre-marker checks ({ctx.kind})"
    except Exception as exc:  # noqa: BLE001 - fail closed
        return False, f"{type(exc).__name__}: {str(exc)[:160]}"


def candidate_check(ctx, raw: bytes, parent: str) -> tuple:
    """R4F F2: the official checks 2, 3, 5, 6, 8 and 9 on an UNCOMMITTED candidate grant (bytes), with `parent` the
    would-be parent of the grant commit, plus check 7 in its pre-marker form (empty namespace).  Checks 4 and 10 need
    the grant commit or an item and are not reached.  Read-only; returns (ok, reason); admits nothing."""
    try:
        if ctx is not PRODUCTION and type(ctx) is not TestContext:
            return False, "not a guard context"
        g = _parse_grant(ctx, raw)                                                             # 2
        _check_ew(g)                                                                           # 3
        _check_frozen_identity(ctx, g, parent)                                                 # 5, 6
        if _git(ctx.repo, "for-each-ref", "--format=%(refname)", ctx.ref_namespace).split():   # 7 (pre-marker form)
            raise ValueError("the marker namespace is not empty before the marker")
        _check_expiry_host(g)                                                                  # 8, 9
        return True, f"the candidate grant passes checks 2, 3, 5-9 on parent {parent[:12]} ({ctx.kind})"
    except Exception as exc:  # noqa: BLE001 - fail closed
        return False, f"{type(exc).__name__}: {str(exc)[:160]}"


def guard_interval(geometry, lo, hi=None, *, ctx=None) -> None:
    hi = lo if hi is None else hi
    d, reason = admission_decision({"geometry": geometry, "lo": lo, "hi": hi}, ctx=ctx)
    if d == "NOT_BANDED":
        return
    if d != "ADMIT":
        raise QuarantineRefusal(f"DRIFT_BAND_REFUSED [{float(F(lo))}, {float(F(hi))}]: {reason}")


class _ProducerAdapter:
    """The q309_guard API the pinned producer calls (srk_certify: guard_drift, log_execution, install_import_guard).
    Installed by the driver in execute mode only, after check_grant.  Log lines are kept in memory (the driver seals
    them with the result; protocol section 6: TARGET_EXECUTION lines are appended to the ledger after the seal)."""

    def __init__(self, ctx):
        import q309_guard as research_q                      # the research guard: everything not overridden
        object.__setattr__(self, "_ctx", ctx)
        object.__setattr__(self, "_q", research_q)
        object.__setattr__(self, "records", [])
        object.__setattr__(self, "QuarantineRefusal", QuarantineRefusal)

    def guard_drift(self, e_lo, e_hi=None) -> None:
        guard_interval(self._ctx.geometry, e_lo, e_hi, ctx=self._ctx)

    def log_execution(self, script: str, purpose: str, *, klass: str, drifts=None, cells_touched=None,
                      notes: str = "") -> dict:
        for d in drifts or []:
            lo, hi = (d[0], d[-1]) if isinstance(d, (list, tuple)) else (d, d)
            self.guard_drift(lo, hi)
        rec = {"utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
               "script": script, "purpose": purpose, "class": klass, "context": self._ctx.kind,
               "drifts": [[str(x) for x in (d if isinstance(d, (list, tuple)) else [d])] for d in drifts or []],
               "cells_touched": cells_touched or [], "notes": notes}
        self.records.append(rec)
        return rec

    def install_import_guard(self) -> None:
        self._q.install_import_guard()

    def __getattr__(self, name):
        return getattr(self._q, name)

    def __setattr__(self, *_):
        raise AttributeError("the producer adapter is immutable")


def producer_adapter(ctx=None):
    return _ProducerAdapter(PRODUCTION if ctx is None else ctx)
