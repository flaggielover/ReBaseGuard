"""P5Y K1 SR O9 executor -- T1: Layer-1 candidate construction ONLY.

STATUS: T1_CANDIDATE_CONSTRUCTION_ONLY. This module builds the frozen SR O9
minimal candidate basis for one cell. It certifies NOTHING: no patch residual,
no B_cover, no obligation. A candidate is not evidence; the certificate built on
it later (T2+) is what bounds the truth.

WHAT IS FROZEN AND WHERE IT IS READ FROM
    bidegree (16,16)        checkpoint complexity.hard_bidegree.SR (binding)
    precision 256 bits      checkpoint precision.SR_production_bits (spec.PRODUCTION_BITS)
    D = 11, Z = 20          checkpoint backend (T2 parameters; recorded, unused here)
    construction method     p5y_k1_binding_campaign/task1/task1_f0.py::build_candidate
                            (the Task1R-adjudicated PASS path): 17x17 Chebyshev-Lobatto
                            collocation, 220-point Gauss-Legendre Nystrom quadrature,
                            float solve, DCT, exact-dyadic rounding at 2^-50
    candidate universe      the O9 minimal basis (46 candidates / 102 contracts,
                            shifts {0:43,1:35,2:20,3:4}), DERIVED here from the frozen
                            SR DAG and asserted against p5y_k1_sr_backend_o9_successor
    cell geometry           spec.CELLS, exact affine [p, s] = p + s*c_SR encodings

FLOAT CONSTRUCTION vs AUTHORITATIVE REPRESENTATION
    float (non-authoritative, exactly as Task1R): Nystrom matrices, closed-form nodal
        values, forward chains, linear solves, DCT. A float construction need not be
        certified; it only proposes a candidate.
    authoritative: the exact integer mantissas m_ij of every candidate
        (coefficient = m_ij * 2^-50, Chebyshev product basis on [0,b_SR]^2), the
        exact affine cell geometry evaluated in Arb at 256 bits, the candidate
        identities and content hashes. Nothing authoritative depends on the ambient
        flint precision: every Arb evaluation runs inside scientific_precision(256)
        and re-verifies ctx.prec where the work is done.

NODE CLASSES (46)
    EXACT                   const:1                        (h_1^(k) = -K^(k) 1)
    CLOSED_FORM_INTERPOLANT h:1:k0..2, S:0:k0..2           (nodal closed form)
    FORWARD_OPERATOR        h:2..4, S:1..2, W:(0,1),(0,2),(1,1)   (Leibniz chains)
    RESOLVENT_SOLVE         F:r:k0   (I-K)F_r = S_r + e h_1
    DERIVATIVE_SOLVE        F:r:k1   (I-K)D_r = K'F_r + S_r' + h_1 + e h_1'
    CURVATURE_SOLVE         F:r:k2   (I-K)H_r = K''F_r + 2K'D_r + S_r'' + 2h_1' + e h_1''
S_3, S_4 and the leaf W are computed as nodal intermediates only: they are never
kernel arguments, so they are not basis candidates.

The frozen `sr_patch.build_candidate` family is left untouched (predecessors are
immutable); this module is the executor's candidate-construction path. The CUSUM
degree-12 kernel helper (`sr_patch.assert_kernel_argument_degree`) is deliberately
NOT applied: the binding SR bidegree is (16,16) (M0 ruling DEGREE16_CONFORMANT).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import platform
import re
import sys
import time
from contextlib import contextmanager
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve().parent
NS = HERE.parent
ROOT = NS.parents[2]
CP = ROOT / "level4/closure_proofs"
IMPL = CP / "p5y_k1_cover_ledger_implementation/code"
QUAL = CP / "p5y_k1_sr_qualification/code"
TASK1 = CP / "p5y_k1_binding_campaign/task1"
O9_PROTOCOL = CP / "p5y_k1_sr_backend_o9_successor/config/protocol.json"
for _p in (str(QUAL), str(IMPL)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

THREAD_VARS = ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
               "NUMEXPR_NUM_THREADS", "BLIS_NUM_THREADS", "VECLIB_MAXIMUM_THREADS")
THREAD_ENV_AT_IMPORT = {v: os.environ.get(v) for v in THREAD_VARS}

import flint                                                        # noqa: E402
from flint import arb, ctx                                          # noqa: E402

import spec                                                         # noqa: E402
import sr_dag                                                       # noqa: E402

SCHEMA = "k1.sr.o9.t1.candidate.v1"
CELL_SET_SCHEMA = "k1.sr.o9.t1.cell-candidate-set.v1"
STATUS = "T1_CANDIDATE_CONSTRUCTION_ONLY"

# ------------------------------------------------------------ frozen parameters
FROZEN_BITS = int(spec.PRODUCTION_BITS)
FROZEN_BIDEGREE = tuple(spec.CHECKPOINT["complexity"]["hard_bidegree"]["SR"])
FROZEN_D = int(spec.CHECKPOINT["backend"]["D"])
FROZEN_Z = int(spec.CHECKPOINT["backend"]["Z"])
CAND_DEGREE = 16
SCALE_BITS = 50
COLLOC_QUAD = 220
N = CAND_DEGREE + 1
if FROZEN_BITS != 256 or FROZEN_BIDEGREE != (16, 16) or (FROZEN_D, FROZEN_Z) != (11, 20):
    raise RuntimeError(f"frozen checkpoint drift: bits={FROZEN_BITS} "
                       f"bidegree={FROZEN_BIDEGREE} D,Z={FROZEN_D},{FROZEN_Z}")

FROZEN_O9_CENSUS = {"distinct_candidates": 46, "certified_contracts": 102,
                    "by_moment_shift": {"0": 43, "1": 35, "2": 20, "3": 4}}


class T1Refusal(RuntimeError):
    """Base class: T1 refuses rather than guesses."""


class PrecisionRefused(T1Refusal):
    """The effective flint precision is not the frozen 256 bits."""


class BidegreeRefused(T1Refusal):
    """A candidate bidegree other than the frozen SR (16,16) was requested."""


class CellRefused(T1Refusal):
    """The cell is not byte-identical to a frozen SR cell, or its affine encoding is illegal."""


class UnsupportedCandidate(T1Refusal):
    """The node is not a member of the frozen O9 minimal candidate basis."""


class NonFiniteCandidate(T1Refusal):
    """A construction produced a non-finite value; no candidate is emitted."""


class ThreadContractRefused(T1Refusal):
    """The frozen one-thread numerical contract is not in force."""


class ConstructionFailure(T1Refusal):
    """The frozen construction failed. There is no refit, retry or fallback."""


def canonical(obj) -> bytes:
    return (json.dumps(obj, sort_keys=True, separators=(",", ":"),
                       ensure_ascii=True) + "\n").encode("ascii")


def sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


# ------------------------------------------------------------------- precision
def require_precision() -> None:
    """Called INSIDE every function that performs authoritative Arb work."""
    if ctx.prec != FROZEN_BITS:
        raise PrecisionRefused(f"effective flint precision {ctx.prec} != frozen {FROZEN_BITS}")


def check_bits(bits: int) -> None:
    if bits != FROZEN_BITS:
        raise PrecisionRefused(f"requested precision {bits} != frozen {FROZEN_BITS}; "
                               "no precision change is admissible")


@contextmanager
def scientific_precision(bits: int = FROZEN_BITS):
    """Explicit, scoped 256-bit context. Never relies on the ambient precision."""
    check_bits(bits)
    with ctx.workprec(bits):
        require_precision()
        yield


def check_bidegree(bidegree) -> None:
    if tuple(bidegree) != FROZEN_BIDEGREE:
        raise BidegreeRefused(f"bidegree {tuple(bidegree)} != frozen SR {FROZEN_BIDEGREE}")


def check_threads() -> None:
    bad = {v: (THREAD_ENV_AT_IMPORT[v], os.environ.get(v)) for v in THREAD_VARS
           if THREAD_ENV_AT_IMPORT[v] != "1" or os.environ.get(v) != "1"}
    if bad:
        raise ThreadContractRefused(
            f"one-thread contract not in force at import/now: {bad}; the frozen "
            "construction is only deterministic under OMP/OPENBLAS/... = 1")


def _numpy():
    check_threads()
    import numpy as np
    return np


# ------------------------------------------------------------------- constants
_SPLICE = re.compile(r"^log\((\d+)/(\d+)\)\+1/2$")


def _A_exact() -> tuple[int, int]:
    m = _SPLICE.match(spec.SPLICE_EXACT["SR"])
    if not m or spec.SPLICE_EXACT["SR"] != spec.SR_TERMINAL_EXPR:
        raise CellRefused(f"frozen SR splice expression unreadable: {spec.SPLICE_EXACT['SR']!r}")
    return int(m.group(1)), int(m.group(2))


def sr_constants() -> tuple[arb, arb, arb]:
    """(A, b_SR = log(1+A), c_SR = log A + 1/2) as Arb balls at the frozen precision."""
    require_precision()
    p, q = _A_exact()
    A = arb(p) / arb(q)
    return A, (arb(1) + A).log(), A.log() + arb(1) / arb(2)


def nearest_double(x: arb) -> float:
    """The unique double nearest to EVERY point of x, or refuse.

    The float construction consumes doubles (exactly as Task1R). This proves the
    double is unambiguous: the whole enclosure lies strictly inside the rounding
    interval of the returned value, so no ambient precision can change it.
    """
    require_precision()
    d = float(x)
    if not math.isfinite(d):
        raise ConstructionFailure(f"non-finite construction input {x}")
    half = arb(math.ulp(d)) / arb(2)
    if not ((x - arb(d)).abs_upper() < half):
        raise ConstructionFailure(f"ambiguous double rounding for {x}")
    return d


# -------------------------------------------------------------------- geometry
def frozen_cell(index: int) -> dict:
    hits = [c for c in spec.CELLS if c["detector"] == "SR" and c["index"] == index]
    if isinstance(index, bool) or not isinstance(index, int) or len(hits) != 1:
        raise CellRefused(f"no unique frozen SR cell with index {index!r}")
    return json.loads(json.dumps(hits[0]))


def last_sr_index() -> int:
    return max(c["index"] for c in spec.CELLS if c["detector"] == "SR")


def validate_cell(cell: dict) -> dict:
    """The cell must be byte-identical (canonically) to its frozen record, and its
    affine encodings must obey the frozen SR_terminal_exception."""
    if not isinstance(cell, dict) or cell.get("detector") != "SR":
        raise CellRefused("not an SR cell record")
    frozen = frozen_cell(cell.get("index"))
    if canonical(cell) != canonical(frozen):
        raise CellRefused(f"cell {cell.get('index')} differs from its frozen record "
                          "(tampered, decimalised or malformed)")
    last = last_sr_index()
    for field in ("left", "right", "e0", "rho", "C_evaluation"):
        pair = cell[field]
        if not (isinstance(pair, list) and len(pair) == 2
                and all(isinstance(s, str) for s in pair)):
            raise CellRefused(f"{field}: affine encoding must be a [p, s] pair of strings")
        try:
            F(pair[0]), F(pair[1])
        except (ValueError, ZeroDivisionError) as exc:
            raise CellRefused(f"{field}: non-exact affine part: {exc}") from exc
        if F(pair[1]) != 0 and not (cell["index"] == last and field in ("right", "e0", "rho")):
            raise CellRefused(f"{field}: a c_SR component is admissible only for the last "
                              "cell's right/e0/rho (frozen SR_terminal_exception)")
    if cell["index"] == last and [F(x) for x in cell["right"]] != [F(0), F(1)]:
        raise CellRefused("the last SR cell's right endpoint must be EXACTLY c_SR "
                          "(no decimal substitution, no splice movement)")
    return cell


def affine(pair, c: arb) -> arb:
    require_precision()
    p, s = F(pair[0]), F(pair[1])
    return arb(p.numerator) / arb(p.denominator) + (arb(s.numerator) / arb(s.denominator)) * c


def cell_geometry(cell: dict) -> dict:
    """Exact affine geometry, rigorously enclosed at 256 bits, with the frozen
    identities e0 = (L+R)/2 and rho = (R-L)/2 checked, never assumed."""
    require_precision()
    validate_cell(cell)
    A, b, c = sr_constants()
    L, R = affine(cell["left"], c), affine(cell["right"], c)
    e0, rho = affine(cell["e0"], c), affine(cell["rho"], c)
    tol = arb(2) ** -(FROZEN_BITS - 8)
    if not (e0 - (L + R) / arb(2)).abs_upper() < tol:
        raise CellRefused("e0 != (left+right)/2")
    if not (rho - (R - L) / arb(2)).abs_upper() < tol:
        raise CellRefused("rho != (right-left)/2")
    if not (rho > 0 and R > L):
        raise CellRefused("degenerate cell")
    return {"A": A, "b": b, "c": c, "left": L, "right": R, "e0": e0, "rho": rho}


def legacy_rational_reading(cell: dict) -> dict:
    """The DEFECTIVE predecessor reading F(pair[0]) that silently drops c_SR
    (sr_pilot / executor_adapter / ResolventCertificate.from_frozen_cell). Kept
    only so the regression test can prove this module never reproduces it."""
    return {k: F(cell[k][0]) for k in ("left", "right", "e0", "rho")}


def cell_identity(cell: dict) -> dict:
    return {"detector": "SR", "index": cell["index"], "left": cell["left"],
            "right": cell["right"], "e0": cell["e0"], "rho": cell["rho"],
            "C_upper": cell["C_upper"], "C_evaluation": cell["C_evaluation"],
            "cells_sha256": spec.CELLS_SHA256, "checkpoint_sha256": spec.CHECKPOINT_SHA256}


# ---------------------------------------------------------------------- census
_SHIFTS = {("K", 0): {0}, ("K", 1): {0, 1}, ("K", 2): {0, 1, 2},
           ("Kz", 0): {1}, ("Kz", 1): {1, 2}, ("Kz", 2): {1, 2, 3}}
# K' = -(Kz + eK), K'' = Kz2 + 2e Kz + (e^2-1)K, Kz' = -(Kz2 + e Kz),
# Kz'' = Kz3 + 2e Kz2 + (e^2-1)Kz   (SR_DERIVATION s3); moment shift s = z^s weight.
ORDERS = (0, 1, 2)
R_MAX, H_MAX = 5, 4


def _alias(nid: str) -> str:
    """W_(r,0) is the frozen alias of S_r (sr_dag: 'W_(r,0) = S_r')."""
    m = re.match(r"^W:(\d+),0:k(\d)$", nid)
    return f"S:{m.group(1)}:k{m.group(2)}" if m else nid


def derive_census() -> dict:
    """Derive the O9 minimal basis and contract census from the frozen DAG."""
    dag = sr_dag.build()
    audit = sr_dag.audit(dag)
    if not audit["ok"]:
        raise ConstructionFailure(f"frozen SR DAG audit failed: {audit['findings']}")
    nodes, W = dag["nodes"], [tuple(x) for x in dag["w_indices"]]
    uses: dict[str, set] = {}
    edges: list[tuple[str, str]] = []            # (argument, consumer) for DAG checking

    def use(arg, op, i, consumer=None):
        uses.setdefault(arg, set()).update(_SHIFTS[(op, i)])
        if consumer is not None:
            edges.append((arg, consumer))

    for k in ORDERS:
        use("const:1", "K", k)                                  # h_1^(k) = -K^(k) 1
    for j in range(2, H_MAX + 1):
        for k in ORDERS:
            for i in range(k + 1):
                use(f"h:{j-1}:k{k-i}", "K", i, f"h:{j}:k{k}")
    for r in range(1, R_MAX):
        for k in ORDERS:
            for i in range(k + 1):
                use(f"h:{r}:k{k-i}", "Kz", i, f"S:{r}:k{k}")
    for (r, j) in W:
        if j == 0:
            continue
        for k in ORDERS:
            for i in range(k + 1):
                use(_alias(f"W:{r},{j-1}:k{k-i}"), "K", i, f"W:{r},{j}:k{k}")
    for r in range(R_MAX):
        use(f"F:{r}:k0", "K", 0)                                # own residual F - K F
        use(f"F:{r}:k1", "K", 0)                                # own residual D - K D
        use(f"F:{r}:k0", "K", 1, f"F:{r}:k1")                   # K' F_r
        use(f"F:{r}:k2", "K", 0)                                # own residual H - K H
        use(f"F:{r}:k0", "K", 2, f"F:{r}:k2")                   # K'' F_r
        use(f"F:{r}:k1", "K", 1, f"F:{r}:k2")                   # 2 K' D_r
    for arg, consumer in edges:                                 # every use is a frozen DAG edge
        deps = {_alias(d) for d in nodes[consumer]["dependencies"]}
        if arg not in deps:
            raise ConstructionFailure(f"derived use {arg} -> {consumer} is not a frozen DAG edge")
    for arg in uses:
        if arg != "const:1" and arg not in nodes:
            raise ConstructionFailure(f"basis member {arg} is not a frozen DAG node")
    by_shift = {str(s): sum(1 for v in uses.values() if s in v) for s in range(4)}
    return {"basis": sorted(uses), "shifts": {k: sorted(v) for k, v in uses.items()},
            "distinct_candidates": len(uses),
            "certified_contracts": sum(len(v) for v in uses.values()),
            "by_moment_shift": by_shift, "dag_audit_ok": audit["ok"],
            "dag_nodes": audit["n_nodes"]}


def frozen_o9_census() -> dict:
    return json.loads(O9_PROTOCOL.read_text())["census"]


BASIS_ORDER = (["const:1"]
               + [f"h:{j}:k{k}" for j in range(1, H_MAX + 1) for k in ORDERS]
               + [f"S:{r}:k{k}" for r in range(3) for k in ORDERS]
               + [f"W:{r},{j}:k{k}" for (r, j) in ((0, 1), (0, 2), (1, 1)) for k in ORDERS]
               + [f"F:{r}:k{k}" for r in range(R_MAX) for k in ORDERS])


def node_class(nid: str) -> str:
    if nid not in BASIS_ORDER:
        raise UnsupportedCandidate(f"{nid!r} is not a member of the frozen O9 minimal basis")
    if nid == "const:1":
        return "EXACT"
    if nid.startswith("h:1:") or nid.startswith("S:0:"):
        return "CLOSED_FORM_INTERPOLANT"
    if nid.startswith("F:"):
        return {"k0": "RESOLVENT_SOLVE", "k1": "DERIVATIVE_SOLVE",
                "k2": "CURVATURE_SOLVE"}[nid.split(":")[2]]
    return "FORWARD_OPERATOR"


def verify_census() -> dict:
    derived = derive_census()
    frozen = frozen_o9_census()
    want = {"distinct_candidates": frozen["distinct_candidates"],
            "certified_contracts": frozen["certified_contracts"],
            "by_moment_shift": {str(k): v for k, v in frozen["by_moment_shift"].items()}}
    got = {k: derived[k] for k in want}
    if got != want or want != FROZEN_O9_CENSUS:
        raise ConstructionFailure(f"O9 census mismatch: derived {got} frozen {want}")
    if sorted(BASIS_ORDER) != derived["basis"] or len(set(BASIS_ORDER)) != len(BASIS_ORDER):
        raise ConstructionFailure("construction order is not exactly the derived basis")
    return derived


# ------------------------------------------------------- float construction
class NodalSystem:
    """Nystrom discretisation at one drift, IDENTICAL to task1_f0.build_candidate for
    M0 and the F_0 source; M1..M3 add the frozen z^s moment weights (s = 1, 2, 3).
    FLOAT, non-authoritative: it only proposes candidates."""

    def __init__(self, b_f: float, c_f: float, e_f: float):
        np = _numpy()
        self.np, self.b_f, self.c_f, self.e_f = np, b_f, c_f, e_f
        n = CAND_DEGREE
        t0 = time.process_time()
        nodes = 0.5 * b_f * (np.cos(np.pi * np.arange(n + 1) / n)[::-1] + 1.0)
        wt = np.array([0.5 if k in (0, n) else 1.0 for k in range(n + 1)]) * (-1.0) ** np.arange(n + 1)

        def bary(x):
            x = np.atleast_1d(np.asarray(x, float))
            d = x[:, None] - nodes[None, :]
            hit = np.isclose(d, 0.0, atol=1e-300)
            q = np.where(hit, 1.0, d)
            num = wt[None, :] / q
            out = num / num.sum(axis=1, keepdims=True)
            for r in np.where(hit.any(axis=1))[0]:
                out[r] = hit[r].astype(float)
            return out

        def sp(u):
            return np.where(u > 0, u + np.log1p(np.exp(-np.abs(u))), np.log1p(np.exp(u)))

        def phi(t):
            return np.exp(-0.5 * t * t) / math.sqrt(2 * math.pi)

        self.phi = phi
        t_gl, w_gl = np.polynomial.legendre.leggauss(COLLOC_QUAD)
        NN = N * N
        M = [np.zeros((NN, NN)) for _ in range(4)]
        s0raw, U, L = np.zeros(NN), np.zeros(NN), np.zeros(NN)
        for i, yp in enumerate(nodes):
            for j, ym in enumerate(nodes):
                lo, hi = ym - c_f, c_f - yp
                z = 0.5 * (hi - lo) * t_gl + 0.5 * (hi + lo)
                jac = 0.5 * (hi - lo)
                Bp = bary(sp(yp + z - 0.5))
                Bm = bary(sp(ym - z - 0.5))
                base = w_gl * jac * phi(z + e_f)
                M[0][i * N + j] = np.einsum('q,qa,qb->ab', base, Bp, Bm).ravel()
                for s in (1, 2, 3):
                    M[s][i * N + j] = np.einsum('q,qa,qb->ab', base * z ** s, Bp, Bm).ravel()
                s0raw[i * N + j] = phi(hi + e_f) - phi(lo + e_f)
                U[i * N + j] = hi + e_f
                L[i * N + j] = lo + e_f
        self.nodes, self.M, self.s0raw, self.U, self.L = nodes, M, s0raw, U, L
        self.A = np.eye(NN) - M[0]
        self.assembly_cpu_s = time.process_time() - t0

    # operator applications (SR_DERIVATION s3), deterministic evaluation order
    def K(self, k, v):
        M, e = self.M, self.e_f
        if k == 0:
            return M[0] @ v
        if k == 1:
            return -(M[1] @ v + e * (M[0] @ v))
        return M[2] @ v + 2.0 * e * (M[1] @ v) + (e * e - 1.0) * (M[0] @ v)

    def Kz(self, k, v):
        M, e = self.M, self.e_f
        if k == 0:
            return M[1] @ v
        if k == 1:
            return -(M[2] @ v + e * (M[1] @ v))
        return M[3] @ v + 2.0 * e * (M[2] @ v) + (e * e - 1.0) * (M[1] @ v)

    def leibniz(self, op, args):
        C = ((1,), (1, 1), (1, 2, 1))
        out = []
        for k in ORDERS:
            acc = op(0, args[k])
            for i in range(1, k + 1):
                acc = acc + float(C[k][i]) * op(i, args[k - i])
            out.append(acc)
        return out

    def solve(self, rhs):
        return self.np.linalg.solve(self.A, rhs)

    def closed_forms(self):
        np, U, L, e = self.np, self.U, self.L, self.e_f
        Phi = np.vectorize(lambda x: 0.5 * math.erfc(-x / math.sqrt(2.0)))
        pU, pL, PU, PL = self.phi(U), self.phi(L), Phi(U), Phi(L)
        h1 = [1.0 - PU + PL, pL - pU, U * pU - L * pL]
        tail = 1.0 - PU + PL
        S0 = [pU - pL - e * tail,
              -U * pU + L * pL - tail - e * (-pU + pL),
              (U * U - 1.0) * pU - (L * L - 1.0) * pL + 2.0 * (pU - pL) - e * (U * pU - L * pL)]
        return h1, S0


def construct_nodal(sysn: NodalSystem) -> tuple[dict, dict]:
    """All nodal values in frozen DAG order. Returns (values, per-node cpu seconds)."""
    e = sysn.e_f
    t = {}
    val = {}

    def timed(nid, fn):
        t0 = time.process_time()
        v = fn()
        t[nid] = time.process_time() - t0
        return v

    h1, S0 = timed("closed_forms", sysn.closed_forms)
    h = {1: h1}
    for j in range(2, H_MAX + 1):
        h[j] = timed(f"h:{j}", lambda j=j: sysn.leibniz(sysn.K, h[j - 1]))
    S = {0: S0}
    for r in range(1, R_MAX):
        S[r] = timed(f"S:{r}", lambda r=r: sysn.leibniz(sysn.Kz, h[r]))
    Wv = {}
    for r, j in ((0, 1), (0, 2), (1, 1)):
        prev = S[r] if j == 1 else Wv[(r, j - 1)]
        Wv[(r, j)] = timed(f"W:{r},{j}", lambda prev=prev: sysn.leibniz(sysn.K, prev))
    for r in range(R_MAX):
        rhsF = sysn.s0raw if r == 0 else S[r][0] + e * h1[0]
        Fr = timed(f"F:{r}:k0", lambda rhsF=rhsF: sysn.solve(rhsF))
        rhsD = sysn.K(1, Fr) + S[r][1] + h1[0] + e * h1[1]
        Dr = timed(f"F:{r}:k1", lambda rhsD=rhsD: sysn.solve(rhsD))
        rhsH = sysn.K(2, Fr) + 2.0 * sysn.K(1, Dr) + S[r][2] + 2.0 * h1[1] + e * h1[2]
        Hr = timed(f"F:{r}:k2", lambda rhsH=rhsH: sysn.solve(rhsH))
        val[f"F:{r}:k0"], val[f"F:{r}:k1"], val[f"F:{r}:k2"] = Fr, Dr, Hr
    for k in ORDERS:
        for j in range(1, H_MAX + 1):
            val[f"h:{j}:k{k}"] = h[j][k]
        for r in range(3):
            val[f"S:{r}:k{k}"] = S[r][k]
        for (r, j) in ((0, 1), (0, 2), (1, 1)):
            val[f"W:{r},{j}:k{k}"] = Wv[(r, j)][k]
    return val, t


def quantize(vec) -> tuple[list[list[int]], dict]:
    """Task1R's exact nodal -> Chebyshev -> 2^-50 dyadic rounding. Returns the EXACT
    integer mantissas (the authoritative candidate) plus float diagnostics."""
    np = _numpy()
    vec = np.asarray(vec, dtype=float)
    if vec.shape != (N * N,) or not np.all(np.isfinite(vec)):
        raise NonFiniteCandidate("nodal values are not a finite 289-vector")
    n = CAND_DEGREE
    Fm = vec.reshape(N, N)

    def dct(v):
        out = []
        for jj in range(N):
            acc = 0.0
            for k in range(N):
                ww = 0.5 if k in (0, n) else 1.0
                acc += ww * v[k] * math.cos(math.pi * jj * k / n)
            cc = 2.0 * acc / n
            out.append(cc / 2.0 if jj in (0, n) else cc)
        return np.array(out)

    Fdesc = Fm[::-1, ::-1]
    step = np.array([dct(Fdesc[i]) for i in range(N)])
    cheb = np.array([dct(step[:, j]) for j in range(N)]).T
    if not np.all(np.isfinite(cheb)):
        raise NonFiniteCandidate("Chebyshev coefficients are not finite")
    scale = 2.0 ** SCALE_BITS
    dyadic = np.round(cheb * scale) / scale
    mant = [[int(round(float(dyadic[i][j] * scale))) for j in range(N)] for i in range(N)]
    diag = {"node_min": float(Fm.min()), "node_max": float(Fm.max()),
            "cheb_coeff_max": float(abs(cheb).max()),
            "cheb_coeff_abs_sum": float(abs(cheb).sum()),
            "dyadic_rounding_max": float(abs(cheb - dyadic).max()),
            "dyadic_rounding_abs_sum": float(abs(cheb - dyadic).sum())}
    return mant, diag


EXACT_ONE = [[(1 << SCALE_BITS) if (i, j) == (0, 0) else 0 for j in range(N)] for i in range(N)]


def to_arb_matrix(mant) -> list[list[arb]]:
    """Authoritative Arb form of a candidate (exact at the frozen precision)."""
    require_precision()
    den = arb(2) ** SCALE_BITS
    return [[arb(m) / den for m in row] for row in mant]


# ----------------------------------------------------------- identity binding
BOUND_SOURCES = (
    "level4/closure_proofs/p5y_k1_sr_o9_executor_t1_successor/code/sr_o9_candidates.py",
    "level4/closure_proofs/p5y_k1_binding_campaign/task1/task1_f0.py",
    "level4/closure_proofs/p5y_k1_sr_qualification/code/sr_dag.py",
    "level4/closure_proofs/p5y_k1_cover_ledger_implementation/code/assembly.py",
    "level4/closure_proofs/p5y_k1_cover_ledger_implementation/code/spec.py",
    "level4/closure_proofs/p5y_k1_sr_backend_o9_successor/config/protocol.json",
)


def producer_identity() -> dict:
    files = {rel: sha256((ROOT / rel).read_bytes()) for rel in BOUND_SOURCES}
    blob = "".join(f"{k}:{v}\n" for k, v in sorted(files.items())).encode()
    return {"files": files, "producer_hash": sha256(blob)}


def runtime_binding() -> dict:
    np = _numpy()
    try:
        cfg = np.show_config(mode="dicts")
    except Exception as exc:                                        # noqa: BLE001
        cfg = {"unavailable": type(exc).__name__}
    return {"python": sys.version.split()[0], "numpy": np.__version__,
            "python_flint": flint.__version__, "machine": platform.machine(),
            "numpy_config_sha256": sha256(canonical(json.loads(json.dumps(cfg, default=str)))),
            "thread_env": {v: os.environ.get(v) for v in THREAD_VARS}}


def construction_spec(b_f, c_f, e_f) -> dict:
    return {"bidegree": list(FROZEN_BIDEGREE), "scale_bits": SCALE_BITS,
            "collocation_nodes": "Chebyshev-Lobatto 17x17 on [0,b_SR]^2",
            "quadrature": f"Gauss-Legendre {COLLOC_QUAD}", "basis": "Chebyshev product",
            "float_inputs_hex": {"b_SR": b_f.hex(), "c_SR": c_f.hex(), "e0": e_f.hex()},
            "method_source": "task1_f0.build_candidate (Task1R PASS path)",
            "precision_bits": FROZEN_BITS}


# -------------------------------------------------------------- public builder
def float_inputs(geo: dict) -> tuple[float, float, float]:
    require_precision()
    return nearest_double(geo["b"]), nearest_double(geo["c"]), nearest_double(geo["e0"])


def build_cell_candidates(cell_index: int, *, bits: int = FROZEN_BITS,
                          bidegree=FROZEN_BIDEGREE, cell: dict | None = None,
                          nodes=None) -> dict:
    """Construct the frozen O9 minimal candidate basis for one frozen SR cell."""
    check_bits(bits)
    check_bidegree(bidegree)
    check_threads()
    want = list(BASIS_ORDER) if nodes is None else list(nodes)
    for nid in want:
        node_class(nid)                                   # refuses unsupported kinds
    census = verify_census()
    rec = frozen_cell(cell_index) if cell is None else cell
    if rec.get("index") != cell_index:
        raise CellRefused("cell index mismatch")
    t_wall, t_cpu = time.perf_counter(), time.process_time()
    with scientific_precision(bits):
        geo = cell_geometry(rec)
        b_f, c_f, e_f = float_inputs(geo)
    sysn = NodalSystem(b_f, c_f, e_f)
    values, node_cpu = construct_nodal(sysn)
    prod, rt = producer_identity(), runtime_binding()
    cid = cell_identity(rec)
    cspec = construction_spec(b_f, c_f, e_f)
    cands, quant_cpu = [], {}
    with scientific_precision(bits):
        for nid in want:
            t0 = time.process_time()
            if nid == "const:1":
                mant, diag = [row[:] for row in EXACT_ONE], {"exact": True}
            else:
                mant, diag = quantize(values[nid])
            to_arb_matrix(mant)                           # exact conversion at 256 bits
            quant_cpu[nid] = time.process_time() - t0
            identity = {"schema": SCHEMA, "cell": cid, "node": nid,
                        "node_class": node_class(nid), "construction": cspec,
                        "producer_hash": prod["producer_hash"], "runtime_binding": rt}
            ident_hash = sha256(canonical(identity))
            content_hash = sha256(canonical({"identity_hash": ident_hash, "mantissas": mant,
                                             "scale_bits": SCALE_BITS}))
            cands.append({"node": nid, "node_class": node_class(nid),
                          "identity_hash": ident_hash, "content_hash": content_hash,
                          "mantissas": mant, "construction_diagnostics": diag})
    if len({c["identity_hash"] for c in cands}) != len(cands):
        raise ConstructionFailure("candidate identities are not unique")
    scientific = {"schema": CELL_SET_SCHEMA, "status": STATUS, "cell": cid,
                  "construction": cspec, "producer": prod, "runtime_binding": rt,
                  "census": {k: census[k] for k in ("distinct_candidates",
                                                    "certified_contracts",
                                                    "by_moment_shift")},
                  "node_order": [c["node"] for c in cands], "candidates": cands}
    scientific["cell_scientific_hash"] = sha256(canonical(
        [[c["node"], c["identity_hash"], c["content_hash"]] for c in cands]))
    np = sysn.np
    cache_bytes = int(sum(m.nbytes for m in sysn.M) + sysn.A.nbytes
                      + sum(v.nbytes for v in values.values()))
    measurement = {
        "cell": cell_index, "wall_s": time.perf_counter() - t_wall,
        "cpu_s": time.process_time() - t_cpu,
        "system_assembly_cpu_s": sysn.assembly_cpu_s,
        "per_node_construction_cpu_s": node_cpu, "per_node_quantize_cpu_s": quant_cpu,
        "cond_I_minus_M0": float(np.linalg.cond(sysn.A)),
        "candidate_bytes_canonical": len(canonical([c["mantissas"] for c in cands])),
        "cache_bytes": cache_bytes, "n_candidates": len(cands)}
    return {"scientific": scientific, "measurement": measurement}


def reference_F0(e: F = F(1, 4)) -> tuple[list[list[int]], dict, float]:
    """Task1R reference: F_0 at the frozen e = 1/4 (no cell), same machinery."""
    check_threads()
    with scientific_precision(FROZEN_BITS):
        _A, b, c = sr_constants()
        b_f, c_f = nearest_double(b), nearest_double(c)
        e_f = nearest_double(arb(e.numerator) / arb(e.denominator))
    sysn = NodalSystem(b_f, c_f, e_f)
    vals, _ = construct_nodal(sysn)
    mant, diag = quantize(vals["F:0:k0"])
    return mant, diag, float(sysn.np.linalg.cond(sysn.A))


# ------------------------------------------------------------------------- CLI
def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build")
    b.add_argument("--cell", type=int, required=True)
    b.add_argument("--out", required=True)
    b.add_argument("--measure")
    sub.add_parser("census")
    a = ap.parse_args(argv)
    if a.cmd == "census":
        print(json.dumps({k: v for k, v in verify_census().items() if k != "shifts"}, indent=1))
        return 0
    import resource
    res = build_cell_candidates(a.cell)
    Path(a.out).write_bytes(canonical(res["scientific"]))
    if a.measure:
        m = dict(res["measurement"])
        m["peak_rss_kib"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        Path(a.measure).write_text(json.dumps(m, indent=1, sort_keys=True) + "\n")
    print(json.dumps({"cell": a.cell, "n": len(res["scientific"]["candidates"]),
                      "cell_scientific_hash": res["scientific"]["cell_scientific_hash"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
