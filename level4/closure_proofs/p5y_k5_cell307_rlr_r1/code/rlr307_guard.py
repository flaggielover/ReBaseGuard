"""Cell-307 RLR campaign (r1) -- the drift quarantine bound into the pinned RLR certifier.

The pinned certifier (`c1b_certpw.py`, overnight stream C1b) imports a module named `ov_quarantine` and calls exactly
three names from it: `install_import_guard()`, `guard_drift(lo, hi)` and (only from its file-writing CLI path
`run_point`, which this campaign never calls) `log_execution(...)`. The campaign binds THIS module under that name
(see `rlr307_pinned.py`), so the certifier bytes stay identical to their pins while the drift policy is the campaign's:

  * DECOY (default): every drift interval meeting the quarantined band [6/5, 13/5] or its mirror [-13/5, -6/5] is
    refused (the same band as the overnight QUARANTINE_AMENDMENT_1; cells 305-309 lie inside it).
  * TARGET: only after `arm_target` has verified, from git, that the campaign's exactly-once consumption marker exists
    and names the grant commit that is HEAD. Then exactly the armed hull blocks (compared as exact rationals) are
    allowed, and each must lie inside the outward 2^-20 hull of cell 307's cover interval. Nothing else in the band.
  * `log_execution` always refuses: this campaign keeps no certifier-side ledger and never writes a certifier file.
"""
from __future__ import annotations

import importlib.abc
import subprocess
import sys
from fractions import Fraction as F

BAND = (F(6, 5), F(13, 5))
MIRROR = (-BAND[1], -BAND[0])
# cell 307's cover interval (cells.json / REGISTRY_C2, committed geometry; cross-checked by the driver at run time)
CELL307 = (F(17885921, 10000000), F(1882413, 1000000))
HULL_SLACK = F(1, 1 << 20)
CONSUMED_REF = "refs/p5y-k5-cell307-rlr-r1/target-consumed"
# third-party numerics would make the arithmetic environment-dependent; the certifier is stdlib-only
FORBIDDEN_MODULES = frozenset({"numpy", "scipy", "mpmath", "sympy", "flint", "gmpy2", "numba", "cython"})

_ARMED: frozenset = frozenset()
_ARMED_BY: dict = {}


class QuarantineRefusal(RuntimeError):
    """A drift or import this campaign does not permit here."""


def _meets(lo: F, hi: F, band: tuple) -> bool:
    return not (hi < band[0] or lo > band[1])


def guard_drift(e_lo, e_hi=None) -> None:
    lo = F(e_lo)
    hi = lo if e_hi is None else F(e_hi)
    if hi < lo:
        lo, hi = hi, lo
    if not (_meets(lo, hi, BAND) or _meets(lo, hi, MIRROR)):
        return                                                   # a decoy / validation drift outside the band
    if (lo, hi) in _ARMED:
        return                                                   # exactly one of the armed cell-307 hull blocks
    raise QuarantineRefusal(f"DRIFT_REFUSED [{lo}, {hi}] meets the quarantined band and is not an armed block")


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


def _git(repo: str, *args) -> str:
    p = subprocess.run(["/usr/bin/git", "--no-replace-objects", "-C", repo, *args], capture_output=True, text=True,
                       env={"PATH": "/usr/bin:/bin", "GIT_OPTIONAL_LOCKS": "0", "LC_ALL": "C"},
                       stdin=subprocess.DEVNULL)
    return p.stdout.strip() if p.returncode == 0 else ""


def arm_target(repo: str, grant_commit: str, blocks) -> None:
    """Allow exactly `blocks` (exact (lo, hi) pairs) -- only once the consumption marker exists and names the grant
    commit, which must be HEAD. Called by the driver after the marker, and by each Stage-1 worker process."""
    global _ARMED, _ARMED_BY
    marker = _git(repo, "rev-parse", "-q", "--verify", CONSUMED_REF)
    head = _git(repo, "rev-parse", "HEAD")
    if not marker or marker != grant_commit or head != grant_commit:
        raise QuarantineRefusal("ARM_REFUSED: no consumption marker naming the grant commit at HEAD")
    bs = []
    for lo, hi in blocks:
        lo, hi = F(lo), F(hi)
        if not (CELL307[0] - HULL_SLACK <= lo < hi <= CELL307[1] + HULL_SLACK):
            raise QuarantineRefusal(f"ARM_REFUSED: block [{lo}, {hi}] is not inside cell 307's 2^-20 hull")
        bs.append((lo, hi))
    _ARMED = frozenset(bs)
    _ARMED_BY = {"marker": marker, "head": head, "n_blocks": len(bs)}


def armed() -> dict:
    return {"blocks": sorted((str(a), str(b)) for a, b in _ARMED), **_ARMED_BY}
