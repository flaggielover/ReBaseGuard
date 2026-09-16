"""R3 Part C: sigma-graded residual / error wiring on the REAL frozen CUSUM Arb operator stack.

Not executed on any real CUSUM cell here: `certify_real_cell_r3` refuses first (empty pinned authorization
registry), then requires the certified operator constants (pinned certificate artifacts), then the K1 record.

Wiring (explicit subclassing, no module assignment):
    GradedRealCertifier(R1 Order3Certifier)
        certify(...)         frozen certify, plus capture of the residual Pair by name
        graded_mid(name)     (range P_e res, range P_o res, range res) + FINAL truncation allowance of that entry
                             (Repair1 rewrites the r = 0 F/D/H allowances after certify; the final entry is used)
    graded_envelope(name)    parity-aware sup_cell ||d_e res||: operator terms via graded_dag.graded_env on the graded
                             candidate suprema; closed-form leaves via graded_dag.graded_true_sup
    graded_inputs(...)       engine inputs for graded_dag.certify_graded (R2 method, unchanged)

Exact parity table at e = 0 (sigma(p, m) = (m, p)); derivative n of an object of parity s has parity s (-1)^n:
    h_1  even   h_j even   S_0 odd   S_r odd (J_0 odd)   F_r odd   W_(r,j) odd
    => h^(n): (-1)^n;  S^(n), F^(n), W^(n): (-1)^(n+1);  K_i(0): (-1)^i;  J_i(0): (-1)^(i+1)
Residual derivative terms (candidates are constant in e; the fixed source's variation lives in its own leaf):
    h_j:k   sum_i C(k,i) K_(i+1) hhat_(j-1)^(k-i)        S_r:k   sum_i C(k,i) J_(i+1) hhat_r^(k-i)
    F_r:n   K_1 Xhat_n + sum_(i>=1) C(n,i) K_(i+1) Xhat_(n-i)      W_r_j:k  sum_i C(k,i) K_(i+1) What_(j-1)^(k-i)
    leaves  h_1:k -> sup ||h_1^(k+1)|| = sup ||S_0^(k)||;  S_0:k, Sclosed_k -> sup ||S_0^(k+1)||
"""
from __future__ import annotations

import hashlib
import json
import sys
from fractions import Fraction as F
from math import comb
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
CP = NS.parents[0]
R1_CODE = CP / "p5y_k5_cusum_order3_real_producer/code"
R2_CODE = CP / "p5y_k5_cusum_order3_r2_repair/code"
for _p in (str(NS / "code"), str(R2_CODE), str(R1_CODE)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import cusum_order3 as R1C  # noqa: E402  (R1 real front-end: frozen chain, Order3Certifier)

from flint import arb  # noqa: E402

import cusum_graded as R2CG  # noqa: E402
import graded_dag as G  # noqa: E402
import hermite6_ext as H6  # noqa: E402
from cusum_layer2 import Pair  # noqa: E402
from intervals import exact  # noqa: E402

AUTH_REGISTRY = NS / "config/REAL_CELL_AUTHORIZATION_REGISTRY_R3.json"
AUTH_REGISTRY_SHA256 = "add0c941ce2267088a24c0e26080e5ebc93e50c7bc2bad3fc8c71390c2dd258e"
CERT_REGISTRY = NS / "config/OPERATOR_CERTIFICATES_R3.json"
CERT_REGISTRY_SHA256 = "cc1e17a9bfdab1ced498d650b86cbcb1967e1f388c0fd18ba4283f0d559374a8"

PARITY_BASE = {"h": 1, "S": -1, "F": -1, "W": -1}          # parity of the object itself at e = 0


class R3Refusal(RuntimeError):
    pass


def derivative_parity(family: str, n: int) -> int:
    return PARITY_BASE[family] * (-1) ** n


# ------------------------------------------------------------------ certified operator constants
def load_certificates() -> dict:
    raw = CERT_REGISTRY.read_bytes()
    if hashlib.sha256(raw).hexdigest() != CERT_REGISTRY_SHA256:
        raise R3Refusal("operator certificate registry bytes differ from the pinned registry")
    reg = json.loads(raw)
    out = {}
    for name in ("C_o0", "C_e0"):
        entry = next((e for e in reg.get("certificates", []) if e.get("name") == name), None)
        if entry is None:
            raise R3Refusal(f"MISSING_OPERATOR_CERTIFICATE {name}")
        art = NS / entry["artifact"]
        if not art.exists() or hashlib.sha256(art.read_bytes()).hexdigest() != entry["artifact_sha256"]:
            raise R3Refusal(f"operator certificate artifact {name} missing or altered")
        out[name] = F(entry["value_upper"])
    return out


# ------------------------------------------------------------------ the certifier
class GradedRealCertifier(R1C.Order3Certifier):
    """R1 Order3Certifier plus residual-Pair capture for the graded ranges."""

    provides_graded_r3 = True

    def certify(self, name, residual, extra, envelope):
        out = super().certify(name, residual, extra, envelope)
        if not hasattr(self, "graded_pairs"):
            self.graded_pairs = {}
        self.graded_pairs[name] = residual
        return out


def parity_ranges(cert, key, pair):
    """(range P_e pair, range P_o pair) on the reachable set, cached ON THE CERTIFIER (so every consumer of the same
    certifier, including qualification mutants, reuses the expensive Bernstein ranges; the ranges are data, the
    graded logic below is not cached)."""
    cache = cert.__dict__.setdefault("_parity_range_cache", {})
    if key not in cache:
        sw = Pair(R2CG.swap_poly(pair.lo), R2CG.swap_poly(pair.hi))
        half = arb(1) / arb(2)
        cache[key] = (cert._range((pair + sw).scale(half)), cert._range((pair - sw).scale(half)))
    return cache[key]


def graded_sup(cert, key) -> "G.V":
    """(sup ||P_e X||, sup ||P_o X||, sup ||X||) for a candidate polynomial; the total is the frozen certified sup."""
    poly = cert.P[key]
    e, o = parity_ranges(cert, ("cand",) + tuple(key), Pair(poly, poly))
    return G.V(e, o, cert.sup[key])


def graded_mid(cert, name: str, entry: dict) -> "G.V":
    allow = entry["truncation_allowance"]
    pair = cert.graded_pairs[name]
    e, o = parity_ranges(cert, ("res", name), pair)
    return G.V(e + allow, o + allow, entry["delta_mid"])          # t is the frozen certified delta_mid, exactly


def envelope_terms(cert, name: str):
    """(kind, payload): ('ops', terms) or ('leaf', (parity, n_right)) for the frozen residual name."""
    if name.startswith("h_1:"):
        k = int(name.split(":")[1])
        return "leaf_h1", (derivative_parity("h", k + 1), k)                  # sup ||h_1^(k+1)|| = sup ||S_0^(k)||
    if name.startswith("S_0:") or name.startswith("Sclosed_"):
        k = int(name.split(":")[1]) if ":" in name else int(name.split("_")[1])
        return "leaf_S0", (derivative_parity("S", k + 1), k + 1)
    if name.startswith("h_"):
        j, k = map(int, name[2:].split(":"))
        return "ops", [(comb(k, i), "K", i + 1, ("h", j - 1, k - i)) for i in range(k + 1)]
    if name.startswith("S_"):
        r, k = map(int, name[2:].split(":"))
        return "ops", [(comb(k, i), "J", i + 1, ("h", r, k - i)) for i in range(k + 1)]
    if name.startswith("W_"):
        rj, k = name[2:].split(":")
        r, j = map(int, rj.split("_"))
        k = int(k)
        return "ops", [(comb(k, i), "K", i + 1, ("W", (r, j - 1), k - i)) for i in range(k + 1)]
    fam = {"F": 0, "dF": 1, "H": 2, "G": 3}
    head, r = name.split("_")
    n = fam[head]
    keys = [("F", int(r), 0), ("D", int(r), 0), ("H", int(r), 0), ("G", int(r), 0)]
    terms = [(1, "K", 1, keys[n])] + [(comb(n, i), "K", i + 1, keys[n - i]) for i in range(1, n + 1)]
    return "ops", terms


def graded_envelope(cert, name, norms, hull, eta, cell_lr, hull_lr) -> "G.V":
    kind, payload = envelope_terms(cert, name)
    if kind == "ops":
        terms = [(c, fam, order, graded_sup(cert, key)) for c, fam, order, key in payload]
        return G.graded_env(terms, norms["k"], norms["j"], hull["k"], hull["j"], eta)
    parity, n = payload
    right = H6.sup_S0_on(n, *cell_lr)
    nxt = H6.sup_S0_on(n + 1, *hull_lr)
    return G.graded_true_sup(parity, right, nxt, eta)


ENGINE_NAME = {"F": 0, "dF": 1, "H": 2, "G": 3}


def engine_name(name: str) -> str:
    head = name.split("_")[0]
    if head in ENGINE_NAME and ":" not in name:
        return f"F_{name.split('_')[1]}:{ENGINE_NAME[head]}"
    return name


def graded_inputs(cert, residuals: dict, *, left: F, right: F, certificates: dict) -> dict:
    """All graded engine inputs from a certifier whose residuals (orders 0..2, aux order 3, G) are computed."""
    lo_h, hi_h = min(F(0), left), max(F(0), right)
    norms = H6.norm_table(left, right)
    hull = H6.norm_table(lo_h, hi_h)
    eta_cell = exact(max(abs(left), abs(right)))
    rho = exact(cert.rho)
    res = {}
    for name, entry in residuals.items():
        if name.startswith("Sclosed_"):
            a = entry["delta_mid"]
            mid = G.V(a, a, a)
        else:
            mid = graded_mid(cert, name, entry)
        env = graded_envelope(cert, name, norms, hull, eta_cell, (left, right), (lo_h, hi_h))
        res[engine_name(name)] = {"mid": (mid.e, mid.o, mid.t),
                                  "cell": (mid.e + rho * env.e, mid.o + rho * env.o, mid.t + rho * env.t)}
    a3 = cert.reward_allow[3]
    env3 = graded_envelope(cert, "Sclosed_3", norms, hull, eta_cell, (left, right), (lo_h, hi_h))
    res["Sclosed_3"] = {"mid": (a3, a3, a3), "cell": (a3 + rho * env3.e, a3 + rho * env3.o, a3 + rho * env3.t)}
    return {"C": exact(cert.C), "C_e0": exact(certificates["C_e0"]), "C_o0": exact(certificates["C_o0"]),
            "k": norms["k"], "j": norms["j"], "k_hull": hull["k"], "j_hull": hull["j"],
            "eta_mid": exact(abs(F(cert.e0))), "eta_cell": eta_cell, "x0_sigma_fixed": True, "res": res}


def all_residuals_for_graded(cert) -> dict:
    """Frozen order 0..2 residuals, Aux3 order-3 source residuals and the R1 rung residuals, in one dict."""
    import rung3_residual as RR
    out = dict(cert.all_residuals())
    out.update(cert.aux_residuals())
    for r in range(5):
        out[f"G_{r}"] = RR.g_residual(cert, r)
    return out


# ------------------------------------------------------------------ real entry (gated; never entered here)
def certify_real_cell_r3(cell_index: int, *, authorization: dict | None, record_bytes: bytes, point: bool = False):
    raw = AUTH_REGISTRY.read_bytes()                                                     # FIRST
    if hashlib.sha256(raw).hexdigest() != AUTH_REGISTRY_SHA256:
        raise R3Refusal("authorization registry bytes differ from the pinned registry")
    reg = json.loads(raw)
    digest = None if authorization is None else hashlib.sha256(
        json.dumps(authorization, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    if not any(e.get("authorization_sha256") == digest and cell_index in e.get("cells", [])
               for e in reg.get("authorizations", [])):
        raise R3Refusal(f"REAL_CELL_NOT_AUTHORIZED: cell {cell_index}")
    certificates = load_certificates()
    import k1_inputs
    sealed = k1_inputs.validate(record_bytes, cell_index=cell_index)
    raise R3Refusal(f"authorized real evaluation is out of R3 scope (certificates {sorted(certificates)}, "
                    f"record {sealed['record_sha256'][:12]})")
