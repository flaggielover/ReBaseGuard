"""Cell-308 MB campaign (r1) -- the formal drift / cell guard (B1). DECOY by default.

It is bound under the name `ov_quarantine` for every pinned overnight module (C1b, C2b, tpt.py), under
`c308E_quarantine` for the stream-ASSEMBLY module tptb_tail, and as the `Q` attribute of the pinned independent
verifier vd_verify (see mb308_pinned). Those modules call guard_drift / guard_cell / guard_path /
install_import_guard / log_execution; the policy is this module's:

  * DECOY (default): every drift point or interval meeting the band [6/5, 13/5] or its mirror is refused, and so is
    every CUSUM m = 5 cell 305-309 label (the quarantine of config/TARGET_QUARANTINE_308.json).
  * REPRODUCTION context (`reproduction(cell, cover)`), cells 305 (rehearsal) and 308 (control C-B, before the marker):
    admits ONLY the label (CUSUM, 5, cell), the cover interval and its end / centre points, for the duration of a
    reproduction-only computation. The consumer installs tripwires on every transport penalty while it is open.
  * TARGET: only after `arm_target` has verified from git that the exactly-once consumption marker exists and names
    the grant commit that is HEAD, and that the admitted set passed by the caller EQUALS the set this module derives
    itself from CELL308 by the frozen rules D1/D2 (tiles E_i, dyadic hulls B_i, pointwise drifts b_i = lo(B_i), the
    cover interval and its end / centre points). Then exactly that set and the label (CUSUM, 5, 308) are admitted.
    Nothing else in the band, and no other quarantined label.
  * `log_execution` always refuses: no pinned module writes a file in this campaign.
"""
from __future__ import annotations

import contextlib
import importlib.abc
import math
import re
import subprocess
import sys
from fractions import Fraction as F

BAND = (F(6, 5), F(13, 5))
MIRROR = (-BAND[1], -BAND[0])
# cell 308's cover interval (cells.json CUSUM index 308 == TARGET_QUARANTINE_308.json primary_target.cover_interval;
# cross-checked against cells.json and REGISTRY_C2 by the driver at run time)
CELL308 = (F(1882413, 1000000), F(19839101, 10000000))
TARGET_LABEL = ("CUSUM", 5, 308)
QUARANTINED_CELLS = frozenset({305, 306, 307, 308, 309})
REPRODUCTION_CELLS = frozenset({305, 308})
SUB_BLOCK_MAX_WIDTH = F(1, 100)          # D1 (C2's rule, as the 307 campaign)
HULL_BITS = 20                           # D2
CONSUMED_REF = "refs/p5y-k5-cell308-mb-r1/target-consumed"
FORBIDDEN_MODULES = frozenset({"numpy", "scipy", "mpmath", "sympy", "flint", "gmpy2", "numba", "cython"})
FORBIDDEN_PATHS = (re.compile(r"RLR307_CELL307_RESULT"), re.compile(r"C12R[12]_CELL306_RESULT"),
                   re.compile(r"-emergency-result\.json"))

_S: dict = {"mode": "DECOY", "armed": frozenset(), "armed_by": {}, "repro": None}


class QuarantineRefusal(RuntimeError):
    """A drift, label, path or import this campaign does not permit here."""


# ------------------------------------------------------------------ the frozen geometry rules (D1, D2)
def partition(x_lo, x_hi) -> list:
    x_lo, x_hi = F(x_lo), F(x_hi)
    n = max(1, math.ceil((x_hi - x_lo) / SUB_BLOCK_MAX_WIDTH))
    w = (x_hi - x_lo) / n
    return [(x_lo + i * w, x_lo + (i + 1) * w) for i in range(n)]


def hull(lo, hi, bits: int = HULL_BITS) -> tuple:
    s = 1 << bits
    return F(math.floor(F(lo) * s), s), F(math.ceil(F(hi) * s), s)


def geometry(x_lo, x_hi) -> list:
    """[{index, tile (E_i), hull (B_i), b (= lo(B_i))}] for a cover interval (the rule the driver also uses)."""
    out = []
    for i, (lo, hi) in enumerate(partition(x_lo, x_hi)):
        hlo, hhi = hull(lo, hi)
        out.append({"index": i, "tile": (lo, hi), "hull": (hlo, hhi), "b": hlo})
    return out


def admitted_set(x_lo, x_hi, e0) -> frozenset:
    """Every (lo, hi) pair the target path may present to the guard: tiles, hulls, points b_i (as (b, b)), the cover
    interval and its three points. Derived from the cover only."""
    x_lo, x_hi, e0 = F(x_lo), F(x_hi), F(e0)
    s = {(x_lo, x_hi), (x_lo, x_lo), (x_hi, x_hi), (e0, e0)}
    for g in geometry(x_lo, x_hi):
        s |= {g["tile"], g["hull"], (g["b"], g["b"])}
    return frozenset(s)


def target_admitted_set() -> frozenset:
    return admitted_set(CELL308[0], CELL308[1], (CELL308[0] + CELL308[1]) / 2)


# ------------------------------------------------------------------ the ov_quarantine interface
def _meets(lo: F, hi: F, band: tuple) -> bool:
    return not (hi < band[0] or lo > band[1])


def _norm(e_lo, e_hi=None) -> tuple:
    lo = F(e_lo)
    hi = lo if e_hi is None else F(e_hi)
    return (hi, lo) if hi < lo else (lo, hi)


def guard_drift(e_lo, e_hi=None) -> None:
    lo, hi = _norm(e_lo, e_hi)
    if not (_meets(lo, hi, BAND) or _meets(lo, hi, MIRROR)):
        return                                                   # a decoy / validation drift outside the band
    if _S["mode"] == "TARGET" and (lo, hi) in _S["armed"]:
        return                                                   # one pre-declared cell-308 object
    rp = _S["repro"]
    if rp is not None and (lo, hi) in rp["pairs"]:
        return                                                   # reproduction-only geometry of the declared cell
    raise QuarantineRefusal(f"DRIFT_REFUSED [{lo}, {hi}] meets the quarantined band and is not admitted")


def guard_cell(detector, m, cell) -> None:
    if str(detector).upper() != "CUSUM" or int(m) != 5 or int(cell) not in QUARANTINED_CELLS:
        return
    if _S["mode"] == "TARGET" and int(cell) == TARGET_LABEL[2]:
        return
    rp = _S["repro"]
    if rp is not None and int(cell) == rp["cell"]:
        return
    raise QuarantineRefusal(f"CELL_REFUSED CUSUM m=5 cell {int(cell)}")


def guard_path(path) -> None:
    s = str(path)
    for pat in FORBIDDEN_PATHS:
        if pat.search(s):
            raise QuarantineRefusal(f"PATH_REFUSED {s}")


def log_execution(*_a, **_k) -> None:
    raise QuarantineRefusal("log_execution is never called in this campaign (no certifier-side files)")


class _ImportGuard(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):  # noqa: D401
        if fullname.split(".", 1)[0] in FORBIDDEN_MODULES:
            raise QuarantineRefusal(f"FORBIDDEN_MODULE_IMPORT {fullname}")
        return None


def install_import_guard() -> None:
    if not any(isinstance(f, _ImportGuard) for f in sys.meta_path):
        sys.meta_path.insert(0, _ImportGuard())


# ------------------------------------------------------------------ reproduction context (controls only)
@contextlib.contextmanager
def reproduction(cell: int, cover: tuple, e0):
    """Admit (CUSUM, 5, cell) and exactly the cover interval / its end and centre points, for a reproduction-only
    computation of a COMMITTED record. Cell 308's cover must equal CELL308 exactly."""
    cell = int(cell)
    lo, hi = F(cover[0]), F(cover[1])
    e0 = F(e0)
    if cell not in REPRODUCTION_CELLS:
        raise QuarantineRefusal(f"REPRODUCTION_REFUSED cell {cell}")
    if cell == TARGET_LABEL[2] and (lo, hi) != CELL308:
        raise QuarantineRefusal("REPRODUCTION_REFUSED: cover differs from the guard's CELL308")
    if not (lo < e0 < hi and e0 - lo == hi - e0):
        raise QuarantineRefusal("REPRODUCTION_REFUSED: e0 is not the centre of the cover")
    if _S["repro"] is not None:
        raise QuarantineRefusal("REPRODUCTION_REFUSED: nested reproduction context")
    _S["repro"] = {"cell": cell, "pairs": frozenset({(lo, hi), (lo, lo), (hi, hi), (e0, e0)})}
    try:
        yield
    finally:
        _S["repro"] = None


def in_reproduction() -> bool:
    return _S["repro"] is not None


# ------------------------------------------------------------------ arming (the only way into TARGET mode)
def _git(repo: str, *args) -> str:
    p = subprocess.run(["/usr/bin/git", "--no-replace-objects", "-C", repo, *args], capture_output=True, text=True,
                       env={"PATH": "/usr/bin:/bin", "GIT_OPTIONAL_LOCKS": "0", "LC_ALL": "C"},
                       stdin=subprocess.DEVNULL)
    return p.stdout.strip() if p.returncode == 0 else ""


def arm_target(repo: str, grant_commit: str, admitted) -> None:
    """Enter TARGET mode for exactly `admitted` ((lo, hi) pairs), which must equal target_admitted_set(). Only when
    the consumption marker exists, names the grant commit, and the grant commit is HEAD."""
    marker = _git(repo, "rev-parse", "-q", "--verify", CONSUMED_REF)
    head = _git(repo, "rev-parse", "HEAD")
    if not marker or not grant_commit or marker != grant_commit or head != grant_commit:
        raise QuarantineRefusal("ARM_REFUSED: no consumption marker naming the grant commit at HEAD")
    got = frozenset((F(a), F(b)) for a, b in admitted)
    if got != target_admitted_set():
        raise QuarantineRefusal("ARM_REFUSED: the admitted set is not the frozen cell-308 set (D1/D2)")
    _S["mode"] = "TARGET"
    _S["armed"] = got
    _S["armed_by"] = {"marker": marker, "head": head, "n_pairs": len(got)}


def mode() -> str:
    return _S["mode"]


def armed() -> dict:
    return {"mode": _S["mode"], "pairs": sorted((str(a), str(b)) for a, b in _S["armed"]), **_S["armed_by"]}
