"""R2 real CUSUM front-end for the graded method: primitives, governance gates, and the explicit unbuilt remainder.

NOT EXECUTED ON ANY CUSUM CELL. `certify_real_cell_r2` refuses, in order:
    1. no real-cell authorization in the pinned EMPTY registry          (config/REAL_CELL_AUTHORIZATION_REGISTRY.json)
    2. no certified odd-subspace resolvent operator certificate C_o0    (config/OPERATOR_CERTIFICATE_REGISTRY.json, EMPTY)
    3. cell outside the graded method's domain (the resolvent perturbation needs eta small; cells not touching 0 use R1)
    4. GRADED_REAL_WIRING_NOT_BUILT: the graded residual certification of every DAG equation (h, S, F, W, orders 0..3)
       with graded envelopes from symmetrized candidate ranges is specified (R2_DESIGN.md section 6) but not built.

Built and qualified here (non-scientific, synthetic polynomials only): the sigma action on the frozen bivariate
Pair representation and the graded reachable-set range

    swap(poly)(p, m) = poly(m, p)      P_e res = (res + swap(res)) / 2,   P_o res = (res - swap(res)) / 2

valid because the Pair branch regions (p + m <= 1, p + m >= 1) and the tail union are sigma-invariant, so swap(res)
evaluated at x encloses res(sigma x) wherever res's enclosure is valid at sigma x.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
CP = NS.parents[0]
R1_CODE = CP / "p5y_k5_cusum_order3_real_producer/code"
for _p in (str(NS / "code"), str(R1_CODE), str(CP / "p5y_k1_cusum_aux5_successor/code")):
    if _p not in sys.path:
        sys.path.append(_p)

AUTH_REGISTRY = NS / "config/REAL_CELL_AUTHORIZATION_REGISTRY.json"
OPERATOR_CERT_REGISTRY = NS / "config/OPERATOR_CERTIFICATE_REGISTRY.json"
AUTH_REGISTRY_SHA256 = "eca47a0bb97d08c9e4ea3c20fd36b6f0f90857b401448c2163a5938a458cf174"
OPERATOR_CERT_REGISTRY_SHA256 = "a3ae20df41dcce78fafae55a77927b538a3cba94baa3c7904c7cc95bdbb8ce2e"


class R2Refusal(RuntimeError):
    pass


def swap_poly(poly: dict) -> dict:
    return {(j, i): c for (i, j), c in poly.items()}


def graded_range(cert, pair):
    """(range P_e res, range P_o res, range res) on the reachable set, with the frozen Bernstein range."""
    from flint import arb
    from cusum_layer2 import Pair
    sw = Pair(swap_poly(pair.lo), swap_poly(pair.hi))
    half = arb(1) / arb(2)
    even = (pair + sw).scale(half)
    odd = (pair - sw).scale(half)
    return cert._range(even), cert._range(odd), cert._range(pair)


def _pinned(path: Path, sha: str, what: str) -> dict:
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != sha:
        raise R2Refusal(f"{what} bytes differ from the pinned registry")
    return json.loads(raw)


def certify_real_cell_r2(cell_index: int, *, authorization: dict | None, operator_certificate: dict | None,
                         record_bytes: bytes):
    reg = _pinned(AUTH_REGISTRY, AUTH_REGISTRY_SHA256, "authorization registry")          # FIRST
    digest = None if authorization is None else hashlib.sha256(
        json.dumps(authorization, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    if not any(e.get("authorization_sha256") == digest and cell_index in e.get("cells", [])
               for e in reg.get("authorizations", [])):
        raise R2Refusal(f"REAL_CELL_NOT_AUTHORIZED: cell {cell_index}")
    ops = _pinned(OPERATOR_CERT_REGISTRY, OPERATOR_CERT_REGISTRY_SHA256, "operator certificate registry")
    odigest = None if operator_certificate is None else hashlib.sha256(
        json.dumps(operator_certificate, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    if not any(e.get("certificate_sha256") == odigest for e in ops.get("certificates", [])):
        raise R2Refusal("NO_CERTIFIED_ODD_SUBSPACE_RESOLVENT: C_o0 operator certificate absent")
    raise R2Refusal("GRADED_REAL_WIRING_NOT_BUILT (R2_DESIGN.md section 6)")
