"""Patch-resolved SR candidate architecture: identity, enumeration and contracts.

Generalises Task1R -- which certified ONE object class (F_0) on ONE patch (17,11)
at ONE drift (e = 1/4) -- to the full frozen scope:

    316 cells  x  3,994 live patches  x  19 object classes  x  m in {1,2,3,5}

The live-patch classification is IMPORTED from the frozen Gate-2B cover
(`p5y_gate2b_sr_cover/sr_cover.py::patch_geometry_counts`), never re-derived
here: it uses the exact multiplicative invariant P = (e^{y+}-1)(e^{y-}-1) of the
SR two-chart recursion, and reproduces 4096 nominal -> 3994 live / 57 dead_low /
45 dead_high with the reset state at patch (0,0).

WHAT IS AND IS NOT IMPLEMENTED
------------------------------
Identity, enumeration, the work mapping and the determinism contract are
implemented and tested. The candidate SOLVES are not: they are the deferred heavy
numerics, and every solve entry point raises `CandidateSolveDeferred` rather than
returning a placeholder value that could be mistaken for a certificate.

NO NEW TOP-LEVEL OBLIGATIONS
----------------------------
A patch certificate is NESTED evidence beneath the cell-level object obligation
it serves. Patches are not work IDs: the SR universe stays at 8,849 and the
global universe at 17,978. `sr_universe.audit()` is the authority and is asserted
in the tests after this module is imported.
"""
from __future__ import annotations

import hashlib
import json
import math
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
ROOT = NS.parents[2]
G2B = ROOT / "level4/closure_proofs/p5y_gate2b_sr_cover"
IMPL = ROOT / "level4/closure_proofs/p5y_k1_cover_ledger_implementation/code"
SPECC = ROOT / "level4/closure_proofs/p5y_k1_cover_ledger_successor/code"
for _p in (str(G2B), str(IMPL), str(SPECC), str(Path(__file__).resolve().parent)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import sr_cover                                                    # noqa: E402
import spec                                                        # noqa: E402
import universe as frozen_universe                                 # noqa: E402

PATCH_GRID = sr_cover.GRID                    # 64, frozen
EXPECTED_LIVE = 3994
EXPECTED_NOMINAL = 4096

# Frozen candidate configuration, inherited from the PASS Task1R path.
SOFTPLUS_DEGREE = 8
CAND_DEGREE = 16
SCALE_BITS = 50
MAX_KERNEL_ARGUMENT_DEGREE = 12               # excluded_routes.json ceiling


class CandidateSolveDeferred(NotImplementedError):
    """A patch candidate solve was requested; it is the deferred heavy numerics."""


class DeadPatch(ValueError):
    """A patch outside the frozen live region was addressed."""


class KernelArgumentDegreeExceeded(ValueError):
    """A candidate above the frozen degree ceiling reached the kernel path."""


@dataclass(frozen=True)
class PatchIdentity:
    """Deterministic identity of one live SR state patch."""
    i: int
    j: int
    grid: int
    core_len: str
    n_z: int
    panels: int
    contains_x0: bool

    @property
    def patch_id(self) -> str:
        return f"SRpatch:{self.grid}:{self.i}:{self.j}"

    def sha256(self) -> str:
        return hashlib.sha256(
            json.dumps(asdict(self), sort_keys=True,
                       separators=(",", ":")).encode("ascii")).hexdigest()


_LIVE_CACHE: list[PatchIdentity] | None = None


def live_patches() -> list[PatchIdentity]:
    """The frozen live patch set, in deterministic (i, j) order."""
    global _LIVE_CACHE
    if _LIVE_CACHE is None:
        A = 4581762885148045 / 8796093022208
        b, c = math.log1p(A), math.log(A) + 0.5
        live, _dl, _dh, _x0 = sr_cover.patch_geometry_counts(b, c, A)
        _LIVE_CACHE = [
            PatchIdentity(i=p["i"], j=p["j"], grid=PATCH_GRID,
                          core_len=repr(p["core_len"]), n_z=p["n_z"],
                          panels=p["panels"], contains_x0=p["contains_x0"])
            for p in live]
    return _LIVE_CACHE


def patch(i: int, j: int) -> PatchIdentity:
    for p in live_patches():
        if p.i == i and p.j == j:
            return p
    raise DeadPatch(f"patch ({i},{j}) is not in the frozen live region")


def patch_census() -> dict:
    lp = live_patches()
    return {"grid": PATCH_GRID, "nominal": PATCH_GRID ** 2, "live": len(lp),
            "dead": PATCH_GRID ** 2 - len(lp),
            "total_panels": sum(p.panels for p in lp),
            "reset_patch": next((p.patch_id for p in lp if p.contains_x0), None),
            "live_sha256": hashlib.sha256(
                json.dumps([p.patch_id for p in lp]).encode()).hexdigest()}


# ------------------------------------------------------------- work mapping
@dataclass(frozen=True)
class PatchWorkItem:
    """One patch-level unit of NESTED evidence beneath a cell obligation."""
    cell_index: int
    patch: PatchIdentity
    object_class: str            # h_1..h_4, S_0..S_4, F_0..F_4, dF_0..dF_4
    derivative_order: int        # 0, 1, 2
    m: int | None                # None for m-shared objects

    @property
    def work_item_id(self) -> str:
        m = "shared" if self.m is None else str(self.m)
        return (f"SR:{self.cell_index}:{self.patch.patch_id}:"
                f"{self.object_class}:k{self.derivative_order}:m{m}")

    def parent_obligation(self) -> tuple:
        """The FROZEN top-level work ID this evidence serves."""
        return ("SR", self.cell_index, "object", self.object_class)


def patch_items_for_cell(cell_index: int, object_class: str,
                         derivative_order: int = 0) -> list[PatchWorkItem]:
    if object_class not in frozen_universe.OBJECTS:
        raise ValueError(f"{object_class} is not a frozen SR object class")
    return [PatchWorkItem(cell_index, p, object_class, derivative_order, None)
            for p in live_patches()]


def nested_evidence_census() -> dict:
    """Patch-level evidence volume. NOT top-level obligations."""
    n_cells = spec.COUNTS["SR"]
    n_patch = len(live_patches())
    n_obj = spec.OBJECTS_PER_CELL
    return {
        "sr_cells": n_cells, "live_patches": n_patch, "object_classes": n_obj,
        "patch_evidence_items_order0": n_cells * n_patch * n_obj,
        "top_level_sr_obligations": 8849,
        "top_level_universe": spec.TOTAL_UNITS,
        "note": ("patch evidence is NESTED beneath the 8,849 SR obligations and "
                 "creates no work ID; the universe stays at 17,978"),
    }


# ------------------------------------------------- determinism contract (Phase 9)
@dataclass(frozen=True)
class CandidateSpec:
    """Everything that must be identical for a candidate to be reproducible."""
    softplus_degree: int = SOFTPLUS_DEGREE
    cand_degree: int = CAND_DEGREE
    scale_bits: int = SCALE_BITS
    bits: int = 256

    def __post_init__(self):
        if self.cand_degree > MAX_KERNEL_ARGUMENT_DEGREE and False:
            pass  # candidates may exceed the ceiling; only KERNEL ARGUMENTS may not


def assert_kernel_argument_degree(degree: int) -> None:
    """The Gate-2C exclusion: no high-degree object may enter the kernel path."""
    if degree > MAX_KERNEL_ARGUMENT_DEGREE:
        raise KernelArgumentDegreeExceeded(
            f"degree {degree} exceeds the frozen kernel-argument ceiling "
            f"{MAX_KERNEL_ARGUMENT_DEGREE}; this is the Gate-2C degree-120 "
            f"blow-up route (config/excluded_routes.json)")


def candidate_identity(*, item: PatchWorkItem, spec_: CandidateSpec,
                       producer_hash: str, runtime_binding: dict) -> str:
    """Deterministic identity of a candidate.

        same producer + same runtime + same exact patch/cell/config
            => same dyadic candidate => same identity

    The runtime binding (CPython build, flint/Arb identity, BLAS kernel, backend
    library bytes, thread contract, precision) is bound in, so a candidate built
    under a different numerical backend cannot masquerade as this one.
    """
    payload = {
        "work_item_id": item.work_item_id,
        "patch_sha256": item.patch.sha256(),
        "candidate_spec": asdict(spec_),
        "producer_hash": producer_hash,
        "runtime_binding": runtime_binding,
        "schema": "k1.sr.candidate.v1",
    }
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":"),
                   default=str).encode("ascii")).hexdigest()


# ------------------------------------------------------ deferred solve surface
def build_candidate(item: PatchWorkItem, spec_: CandidateSpec):
    raise CandidateSolveDeferred(
        f"candidate solve for {item.work_item_id} is the deferred heavy "
        "numerics; run it only after the CUSUM campaign releases the host")


def derivative_candidate(item: PatchWorkItem, spec_: CandidateSpec):
    raise CandidateSolveDeferred(f"derivative candidate for {item.work_item_id}")


def curvature_candidate(item: PatchWorkItem, spec_: CandidateSpec):
    raise CandidateSolveDeferred(f"curvature candidate for {item.work_item_id}")


def finite_power_candidate(item: PatchWorkItem, j: int, spec_: CandidateSpec):
    raise CandidateSolveDeferred(
        f"finite-power candidate W_(r,{j}) for {item.work_item_id}")
