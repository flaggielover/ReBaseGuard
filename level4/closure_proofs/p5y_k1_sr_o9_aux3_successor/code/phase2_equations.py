"""Phase 2: exact third-order SR equations, minimal auxiliary candidate set, contract census and dependency DAG.

Differentiating the frozen raw-variable system (SR_DERIVATION ss1-6; frozen map sr_o9_equations) once more in e.
Continuation limits l(y), u(y) are e-free, so every derivative falls on phi(z+e):
    d^i/de^i phi(z+e) = (-1)^i He_i(z+e) phi(z+e)
    K^(i) f = int f(q) (-1)^i He_i(z+e) phi(z+e) dz,  K_z^(i) f = int z f(q) (-1)^i He_i(z+e) phi(z+e) dz,
expanded into raw moments M_s(f) = int f(q) z^s phi(z+e) dz with exact polynomial coefficients in e (checked
against the frozen K_EXP/KZ_EXP for i <= 2). Order-3 equations (Leibniz):
    h_1''' = -K''' 1
    h_j''' = sum_i C(3,i) K^(i) h_{j-1}^(3-i)                               (j = 2..4)
    S_0''' = [-He_3(U)phi(U) + He_3(L)phi(L)] - 3 h_1'' - e h_1'''         (S_0 = phi(U)-phi(L) - e h_1)
    S_r''' = sum_i C(3,i) K_z^(i) h_r^(3-i)                                 (r = 1..4)
    W_(r,j)''' = sum_i C(3,i) K^(i) W_(r,j-1)^(3-i),   W_(r,0) = S_r
    (I-K) F_r''' = K''' F_r + 3 K'' F_r' + 3 K' F_r'' + f_r'''
       f_0''' = -He_3(U)phi(U) + He_3(L)phi(L);   f_r''' = S_r''' + 3 h_1'' + e h_1'''   (r >= 1)
The candidate rule is the frozen O9 one: a node is a candidate iff it is a resolvent unknown or the argument of an
operator in another equation; everything else is an image node (operator images of candidates at x0).
"""
import hashlib
import json
from fractions import Fraction as Fr
from math import comb
from pathlib import Path

import sr_o9_candidates as T
import sr_o9_equations as EQ

NS = Path(__file__).resolve().parents[1]


def expansion(kind, i):
    """{s: {t: coef}} with (-1)^i He_i(z+e) [times z for K_z] = sum_s sum_t coef z^s e^t."""
    he = [{(0, 0): Fr(1)}, {(1, 0): Fr(1), (0, 1): Fr(1)}]
    for n in range(1, i):
        nxt = {}
        for (a, b), v in he[n].items():
            for (da, db) in ((1, 0), (0, 1)):
                nxt[a + da, b + db] = nxt.get((a + da, b + db), Fr(0)) + v
        for (a, b), v in he[n - 1].items():
            nxt[a, b] = nxt.get((a, b), Fr(0)) - n * v
        he.append({k: v for k, v in nxt.items() if v})
    out = {}
    for (a, b), v in he[i].items():
        s = a + (1 if kind == "Kz" else 0)
        out.setdefault(s, {})[b] = out.get(s, {}).get(b, Fr(0)) + (-1) ** i * v
    return {s: {t: c for t, c in p.items() if c} for s, p in out.items()}


def check_frozen():
    for i in range(3):
        assert expansion("K", i) == EQ.K_EXP[i], i
        assert expansion("Kz", i) == EQ.KZ_EXP[i], i


def node_order3():
    """(operator kind, operator order, argument, integer multiplier, power of e) per order-3 equation."""
    eqs = {"h:1:k3": {"ops": [("K", 3, "const:1", -1, 0)], "src": []}}
    for j in range(2, 5):
        eqs[f"h:{j}:k3"] = {"ops": [("K", i, f"h:{j-1}:k{3-i}", comb(3, i), 0) for i in range(4)], "src": []}
    eqs["S:0:k3"] = {"ops": [("K", 2, "const:1", 3, 0), ("K", 3, "const:1", 1, 1)],
                     "src": [("He3phiU", -1), ("He3phiL", 1)]}
    for r in range(1, 5):
        eqs[f"S:{r}:k3"] = {"ops": [("Kz", i, f"h:{r}:k{3-i}", comb(3, i), 0) for i in range(4)], "src": []}
    for r in range(4):
        for j in range(1, 4 - r):
            prev = [f"S:{r}:k{q}" if j == 1 else f"W:{r},{j-1}:k{q}" for q in range(4)]
            eqs[f"W:{r},{j}:k3"] = {"ops": [("K", i, prev[3 - i], comb(3, i), 0) for i in range(4)], "src": []}
    for r in range(5):
        ops = [("K", 0, f"F:{r}:k3", 1, 0), ("K", 3, f"F:{r}:k0", 1, 0), ("K", 2, f"F:{r}:k1", 3, 0),
               ("K", 1, f"F:{r}:k2", 3, 0)]
        src = []
        if r == 0:
            src = [("He3phiU", -1), ("He3phiL", 1)]
        else:
            ops += [("Kz", i, f"h:{r}:k{3-i}", comb(3, i), 0) for i in range(4)]
            ops += [("K", 2, "const:1", -3, 0), ("K", 3, "const:1", -1, 1)]
        eqs[f"F:{r}:k3"] = {"ops": ops, "src": src}
    return eqs


def main():
    check_frozen()
    census = T.derive_census()
    assert census["distinct_candidates"] == 46 and census["certified_contracts"] == 102, census
    frozen_shifts = {k: set(v) for k, v in census["shifts"].items()}
    eqs = node_order3()
    uses = {}
    for n, q in eqs.items():
        for kind, i, a, mult, ep in q["ops"]:
            uses.setdefault(a, set()).update(expansion(kind, i).keys())
    cands = sorted({n for n in eqs if n.startswith("F:")}
                   | {a for n, q in eqs.items() for _, _, a, _, _ in q["ops"] if a.endswith(":k3") and a != n})
    images = sorted(n for n in eqs if n not in cands)
    new_contracts = []
    for a, ss in sorted(uses.items()):
        for s in sorted(ss):
            if s not in frozen_shifts.get(a, set()):
                new_contracts.append({"argument": a, "moment_shift": s, "contract_id": EQ.contract_id(a, s),
                                      "argument_is_new_order3_candidate": a.endswith(":k3")})
    nodes = {}
    for n, q in eqs.items():
        nodes[n] = {"derivative_order": 3, "class": "auxiliary_candidate" if n in cands else "image_at_x0",
                    "defining_equation": " + ".join(f"({m})*e^{ep}*{k}^({i})[{a}]" for k, i, a, m, ep in q["ops"])
                                         + "".join(f" + ({c})*{s}" for s, c in q["src"]),
                    "dependencies": sorted({a for _, _, a, _, _ in q["ops"] if a != n}),
                    "operator_orders": sorted({f"{k}^({i})" for k, i, _, _, _ in q["ops"]}),
                    "moment_shifts": sorted({s for k, i, _, _, _ in q["ops"] for s in expansion(k, i)}),
                    "source_closed_forms": [s for s, _ in q["src"]],
                    "candidate_identity": (f"aux3 order-3 candidate {n} (state-only dyadic, degree 16, SCALE_BITS 50, at e0)"
                                           if n in cands else None),
                    "contract_identity": ([EQ.contract_id(n, s) for s in sorted(uses.get(n, set()))] if n in cands else None),
                    "evaluation": "MIDPOINT_ONLY (exact frozen e0); never cell-uniform",
                    "self_resolvent": n.startswith("F:")}
    out = {"schema": "rebaseguard.p5y.k1.sr.o9.aux3-equations.v1", "frozen_census": {"candidates": 46, "contracts": 102},
           "expansions": {f"{k}^({i})": {str(s): {str(t): str(c) for t, c in p.items()} for s, p in expansion(k, i).items()}
                          for k in ("K", "Kz") for i in range(5)},
           "order3_nodes": nodes, "auxiliary_candidates": cands, "image_nodes": images,
           "n_auxiliary_candidates": len(cands), "n_image_nodes": len(images),
           "new_contracts": new_contracts, "n_new_contracts": len(new_contracts),
           "n_new_contracts_on_frozen_candidates": sum(1 for c in new_contracts if not c["argument_is_new_order3_candidate"]),
           "new_raw_moment_shifts": sorted({c["moment_shift"] for c in new_contracts} - {0, 1, 2, 3})}
    out["dag_sha256"] = hashlib.sha256(json.dumps(nodes, sort_keys=True).encode()).hexdigest()
    (NS / "evidence/phase2_equations.json").write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    print("candidates", len(cands), cands)
    print("images", images)
    print("new contracts", len(new_contracts), "on frozen candidates", out["n_new_contracts_on_frozen_candidates"],
          "new raw shifts", out["new_raw_moment_shifts"])


if __name__ == "__main__":
    main()
