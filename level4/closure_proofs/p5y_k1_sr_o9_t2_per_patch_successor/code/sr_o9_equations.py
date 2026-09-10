"""T2 frozen SR equation map: every node's defining equation as an exact linear
combination of raw-moment-shift contracts M_s(Y) = int Y(q_SR(y,z)) z^s phi(z+e) dz,
constants, and phi-only closed forms. Coefficients are exact polynomials in e.

Sources of truth: SR_DERIVATION ss1-6 (operator identities, raw-variable equations),
the frozen error algebra (depgraph: one local residual per node), the frozen SR DAG and
the T1-derived 102-contract census. No Phi closed form is used: h_1^(k) = delta_k0 -
K^(k) 1 is carried by the three constant-candidate contracts (shifts 0, 1, 2).

r = 0 sources reduce EXACTLY to phi-only closed forms (U = u+e, L = l+e):
  S_0 + e h_1             = phi(U) - phi(L)                       (Task1R form)
  S_0' + h_1 + e h_1'     = -U phi(U) + L phi(L)
  S_0'' + 2h_1' + e h_1'' = (U^2-1) phi(U) - (L^2-1) phi(L)
using rho_1^(k) (sr_sources) and h_1' = phi(L) - phi(U), h_1'' = U phi(U) - L phi(L).
For r >= 1 the source S_r^(k) is the operator image sum_i C(k,i) K_z^(i) h_r^(k-i) of
basis candidates (S_3, S_4 are not basis candidates).
"""
from __future__ import annotations

import hashlib
import json
from fractions import Fraction as Fr
from math import comb

import sr_o9_candidates as T

# M_s coefficient polynomials in e for K^(i) and K_z^(i)  (SR_DERIVATION s3)
K_EXP = {0: {0: {0: Fr(1)}},
         1: {1: {0: Fr(-1)}, 0: {1: Fr(-1)}},
         2: {2: {0: Fr(1)}, 1: {1: Fr(2)}, 0: {2: Fr(1), 0: Fr(-1)}}}
KZ_EXP = {0: {1: {0: Fr(1)}},
          1: {2: {0: Fr(-1)}, 1: {1: Fr(-1)}},
          2: {3: {0: Fr(1)}, 2: {1: Fr(2)}, 1: {2: Fr(1), 0: Fr(-1)}}}
SRC_KINDS = ("phiU", "phiL", "UphiU", "LphiL", "U2m1phiU", "L2m1phiL")
ORD = (0, 1, 2)


def padd(p, q, s=Fr(1)):
    out = dict(p)
    for k, v in q.items():
        out[k] = out.get(k, Fr(0)) + s * v
    return {k: v for k, v in out.items() if v != 0}


def pmul(p, q):
    out = {}
    for a, x in p.items():
        for b, y in q.items():
            out[a + b] = out.get(a + b, Fr(0)) + x * y
    return {k: v for k, v in out.items() if v != 0}


class Expr:
    """terms {(cand, s): poly}, const poly, src [(kind, poly)] (order preserved)."""

    def __init__(self, terms=None, const=None, src=None):
        self.terms = dict(terms or {})
        self.const = dict(const or {})
        self.src = list(src or [])

    def __add__(self, o):
        t = dict(self.terms)
        for k, v in o.terms.items():
            t[k] = padd(t.get(k, {}), v)
        src = list(self.src)
        for kind, p in o.src:
            for i, (k2, p2) in enumerate(src):
                if k2 == kind:
                    src[i] = (kind, padd(p2, p))
                    break
            else:
                src.append((kind, dict(p)))
        return Expr({k: v for k, v in t.items() if v}, padd(self.const, o.const),
                     [(k, p) for k, p in src if p])

    def scale(self, poly):
        return Expr({k: pmul(v, poly) for k, v in self.terms.items()}, pmul(self.const, poly),
                    [(k, pmul(p, poly)) for k, p in self.src])


ONE, E1 = {0: Fr(1)}, {1: Fr(1)}


def op(kind, i, cand):
    exp = (K_EXP if kind == "K" else KZ_EXP)[i]
    return Expr({(cand, s): dict(c) for s, c in exp.items()})


def h1_image(k):
    e = op("K", k, "const:1").scale({0: Fr(-1)})
    return e + Expr(const=ONE) if k == 0 else e


def leibniz(kind, args, k):
    acc = Expr()
    for i in range(k + 1):
        acc = acc + op(kind, i, args[k - i]).scale({0: Fr(comb(k, i))})
    return acc


def s_op(r, k):
    return leibniz("Kz", [f"h:{r}:k{j}" for j in ORD], k)


def src(pairs):
    return Expr(src=[(kind, {0: Fr(c)}) for kind, c in pairs])


def rho1(k):
    if k == 0:
        return src([("phiU", 1), ("phiL", -1)]) + h1_image(0).scale({1: Fr(-1)})
    if k == 1:
        return (src([("UphiU", -1), ("LphiL", 1)]) + h1_image(0).scale({0: Fr(-1)})
                + h1_image(1).scale({1: Fr(-1)}))
    return (src([("U2m1phiU", 1), ("L2m1phiL", -1)]) + h1_image(1).scale({0: Fr(-2)})
            + h1_image(2).scale({1: Fr(-1)}))


def f_source(r, k):
    if r == 0:
        return src({0: [("phiU", 1), ("phiL", -1)], 1: [("UphiU", -1), ("LphiL", 1)],
                    2: [("U2m1phiU", 1), ("L2m1phiL", -1)]}[k])
    if k == 0:
        return s_op(r, 0) + h1_image(0).scale(E1)
    if k == 1:
        return s_op(r, 1) + h1_image(0) + h1_image(1).scale(E1)
    return s_op(r, 2) + h1_image(1).scale({0: Fr(2)}) + h1_image(2).scale(E1)


def prev_w(r, j, k):
    return f"S:{r}:k{k}" if j - 1 == 0 else f"W:{r},{j-1}:k{k}"


def rhs(node: str) -> Expr:
    """Right-hand side of the defining equation node = rhs(node)."""
    kind = node.split(":")[0]
    if kind == "h":
        j, k = int(node.split(":")[1]), int(node.split(":")[2][1])
        return h1_image(k) if j == 1 else leibniz("K", [f"h:{j-1}:k{q}" for q in ORD], k)
    if kind == "S":
        r, k = int(node.split(":")[1]), int(node.split(":")[2][1])
        return rho1(k) if r == 0 else s_op(r, k)
    if kind == "W":
        rj, k = node.split(":")[1], int(node.split(":")[2][1])
        r, j = map(int, rj.split(","))
        return leibniz("K", [prev_w(r, j, q) for q in ORD], k)
    if kind == "F":
        r, k = int(node.split(":")[1]), int(node.split(":")[2][1])
        own = op("K", 0, node)
        if k == 0:
            return own + f_source(r, 0)
        if k == 1:
            return own + op("K", 1, f"F:{r}:k0") + f_source(r, 1)
        return (own + op("K", 2, f"F:{r}:k0") + op("K", 1, f"F:{r}:k1").scale({0: Fr(2)})
                + f_source(r, 2))
    raise ValueError(f"no frozen equation for {node!r}")


RESIDUAL_NODES = [n for n in T.BASIS_ORDER if n != "const:1"]
IMAGE_NODES = ([f"h1img:k{k}" for k in ORD] + [f"S:{r}:k{k}" for r in (3, 4) for k in ORD]
               + [f"W:{r},{j}:k{k}" for (r, j) in ((0, 3), (1, 2), (2, 1)) for k in ORD])


def image(node: str) -> Expr:
    if node.startswith("h1img"):
        return h1_image(int(node[-1]))
    return rhs(node)


def local_gate(node: str) -> str | None:
    return ("nested B_candidate lines / C_upper and C*delta_end <= 1/250 (checkpoint ledger)"
            if node.startswith("F:") and node.endswith(":k0") else None)


def node_class(node: str) -> str:
    if node in IMAGE_NODES:
        return "OPERATOR_IMAGE"
    return T.node_class(node)


def pstr(p):
    return " + ".join(f"({v})*e^{k}" for k, v in sorted(p.items())) or "0"


def contract_id(cand, s):
    return f"C:{cand}:s{s}"


def build_map() -> dict:
    census = T.verify_census()
    nodes, used = [], set()
    for n in RESIDUAL_NODES + IMAGE_NODES:
        ex = image(n) if n in IMAGE_NODES else rhs(n)
        used |= set(ex.terms)
        nodes.append({
            "node": n, "class": node_class(n),
            "derivative_order": int(n[-1]),
            "defining_equation": (f"{n} = " if n not in IMAGE_NODES else f"{n} := ")
                                 + " + ".join(f"[{pstr(p)}] M_{s}({c})" for (c, s), p in sorted(ex.terms.items()))
                                 + (f" + [{pstr(ex.const)}]" if ex.const else "")
                                 + "".join(f" + [{pstr(p)}] {k}" for k, p in ex.src),
            "contracts": sorted(contract_id(c, s) for c, s in ex.terms),
            "operator_shifts": sorted({s for _, s in ex.terms}),
            "dependencies": sorted({c for c, _ in ex.terms}),
            "closed_form_sources": [k for k, _ in ex.src],
            "local_residual": ("none: exact operator image of certified candidates (l = 0)"
                               if n in IMAGE_NODES else f"hat({n}) - rhs({n}) on each patch"),
            "local_gate": local_gate(n),
            "candidate_identity": ("T1 identity_hash of candidate " + n) if n not in IMAGE_NODES else None,
        })
    shifts = {c: sorted({s for (cc, s) in used if cc == c}) for c in sorted({c for c, _ in used})}
    derived = {k: sorted(v) for k, v in census["shifts"].items()}
    by_shift = {str(s): sum(1 for (_, ss) in used if ss == s) for s in range(4)}
    out = {"schema": "rebaseguard.p5y.k1.sr.o9.t2.equation-map.v1",
           "operator_expansions": {"K": {i: {s: pstr(p) for s, p in v.items()} for i, v in K_EXP.items()},
                                   "Kz": {i: {s: pstr(p) for s, p in v.items()} for i, v in KZ_EXP.items()}},
           "moment_shift_semantics": "raw weight: M_s f = int f(q_SR) z^s phi(z+e) dz; drift tensor from "
                                     "N^(s)_k = sum_t C(s,t) z_c^(s-t) N_(k+t) (exact identity)",
           "nodes": nodes, "n_residual_nodes": len(RESIDUAL_NODES), "n_image_nodes": len(IMAGE_NODES),
           "contracts_used": sorted(contract_id(c, s) for c, s in used),
           "contract_census_used": {"distinct_candidates": len(shifts), "contracts": len(used),
                                    "by_moment_shift": by_shift},
           "contract_set_equals_frozen_census": shifts == derived,
           "frozen_census": {k: census[k] for k in ("distinct_candidates", "certified_contracts",
                                                    "by_moment_shift")}}
    out["equation_map_sha256"] = hashlib.sha256(T.canonical(out)).hexdigest()
    return out
