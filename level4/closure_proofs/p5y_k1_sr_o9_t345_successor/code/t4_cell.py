"""T4: frozen whole-cell error propagation, SR refinement, all-m assembly, M_R2, STYLE_1 cover and ledger.

Consumes ONE T3 whole-cell record (t3_aggregate.py) and the frozen T1 candidates of the cell.  Frozen machinery,
imported unchanged:
  * depgraph.ErrorDAG  (ERROR_ALGEBRA 1-2: operator-sum edge rule, resolvent value/derivative/curvature rules,
                        ownership, no-double-counting)  -- traversed twice: 'mid' (delta at e0) and 'cell'
                        (uniform-in-e deltas and cell-uniform operator norms), exactly as propagate.py does;
  * sr_operators.one_step_norms  (SR operator norms k_i = ||K^(i)||, kz_i = ||K_z^(i)||);
  * sr_refine.refine_cell        (SR midpoint/whole-cell refinement, SR_MIDPOINT_REFINEMENT.md);
  * assembly.assemble / curvature_bound / assembly_arithmetic_excess (exact all-m coefficients);
  * ledger.cell_ledger           (STYLE_1 cover, top-level and nested gates, target gate).
The DAG topology is read from the frozen SR equation map (sr_o9_equations) with every operator application
resolved: each rhs term is (candidate, operator K^(i) or K_z^(i), exact coefficient).  const:1 terms (h_1 and
the raw-variable e*h_1 terms) and the r=0 closed forms carry NO input error: their TRUE values are inside the
certified residual (ERROR_ALGEBRA 1, 'INCLUDED, not because the error vanishes').
"""
from __future__ import annotations

import hashlib
import json
import sys
from fractions import Fraction as Fr
from pathlib import Path

import sr_o9_candidates as T
import sr_o9_equations as EQ
import t2_final_certifier as FC

for _p in (T.CP / "p5y_k1_cover_ledger_implementation/code", T.CP / "p5y_k1_sr_qualification/code"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))
import assembly                                                     # noqa: E402
import depgraph                                                     # noqa: E402
import ledger                                                       # noqa: E402
import spec                                                         # noqa: E402
import sr_operators as OPS                                          # noqa: E402
import sr_refine                                                    # noqa: E402
from intervals import exact, mag_fraction, outward_upper, record, tight_upper    # noqa: E402
from flint import arb                                               # noqa: E402

NS = Path(__file__).resolve().parents[1]
ORDER_OWNER = {0: "source_dependency_value", 1: "derivative_source_dependency", 2: "curvature_envelope"}
W_OWNER = {0: "finite_kernel_chain_value", 1: "finite_derivative_chain", 2: "curvature_envelope"}
TOPO = ([f"h:1:k{k}" for k in range(3)] + [f"h:{j}:k{k}" for j in range(2, 5) for k in range(3)]
        + [f"S:{r}:k{k}" for r in range(5) for k in range(3)]
        + [f"W:{rj}:k{k}" for rj in ("0,1", "0,2", "0,3", "1,1", "1,2", "2,1") for k in range(3)]
        + [f"h1img:k{k}" for k in range(3)]
        + [f"F:{r}:k{k}" for k in range(3) for r in range(5)])


def canonical(o) -> bytes:
    return (json.dumps(o, sort_keys=True, separators=(",", ":"), ensure_ascii=True, default=str) + "\n").encode()


def op_structure() -> dict:
    """{node: {(cand, kind, i): coefficient poly}} -- the frozen equation map with operators resolved."""
    orig = EQ.op
    EQ.op = lambda kind, i, cand: EQ.Expr({(cand, (kind, i)): {0: Fr(1)}})
    try:
        out = {}
        for n in FC.NODES:
            ex = EQ.image(n) if n in EQ.IMAGE_NODES else EQ.rhs(n)
            out[n] = {(c, k[0], k[1]): dict(p) for (c, k), p in ex.terms.items()}
    finally:
        EQ.op = orig
    return out


def wnode(r, j, k):
    return f"S:{r}:k{k}" if j == 0 else f"W:{r},{j}:k{k}"


def build_dag(mode, t3, C, norms, struct):
    dag = depgraph.ErrorDAG(C=exact(C), norms=norms)
    delta = {n: exact(Fr(v["delta"])) for n, v in t3["delta"][mode].items()}
    nrm = lambda kind, i: norms["k"][i] if kind == "K" else norms["kz"][i]          # noqa: E731
    for n in TOPO:
        k = int(n[-1])
        ins = [(c, kind, i, p) for (c, kind, i), p in sorted(struct[n].items()) if c != "const:1"]
        for c, kind, i, p in ins:
            if set(p) != {0}:
                raise ValueError(f"{n}: non-constant operator coefficient on {c}")
        if n.startswith("F:"):
            r = int(n.split(":")[1])
            fam = {c for c, *_ in ins if c.startswith("F:")}
            want_self = {(n, "K", 0): {0: Fr(1)}}
            if struct[n].get((n, "K", 0)) != {0: Fr(1)}:
                raise ValueError(f"{n}: resolvent self-term not K^(0) with coefficient 1")
            if k >= 1 and struct[n].get((f"F:{r}:k0", "K", k)) != {0: Fr(1)}:
                raise ValueError(f"{n}: K^({k}) F_r term missing or not coefficient 1")
            if k == 2 and struct[n].get((f"F:{r}:k1", "K", 1)) != {0: Fr(2)}:
                raise ValueError(f"{n}: 2 K' D_r term missing")
            if not fam <= {f"F:{r}:k{q}" for q in range(k + 1)}:
                raise ValueError(f"{n}: unexpected F dependencies {fam}")
            src = [(c, kind, i, p) for c, kind, i, p in ins if not c.startswith("F:")]
            sid = f"Ssrc:{r}:k{k}"
            dag.local("local:" + sid, arb(0), owner=ORDER_OWNER[k], order=k)
            dag.operator_sum(sid, k, "local:" + sid, [(p[0], nrm(kind, i), c) for c, kind, i, p in src], owner=ORDER_OWNER[k])
            lid = "local:" + n
            if k == 0:
                dag.local(lid, delta[n], owner="F_equation_certificate_value", order=0)
                dag.resolvent_value(n, lid, [sid])
            elif k == 1:
                dag.local(lid, delta[n], owner="dF_equation_certificate", order=1)
                dag.resolvent_derivative(n, lid, f"F:{r}:k0", [sid])
            else:
                dag.local(lid, delta[n], owner="curvature_envelope", order=2)
                dag.resolvent_curvature(n, lid, f"F:{r}:k0", f"F:{r}:k1", [sid])
            continue
        owner = W_OWNER[k] if n.startswith("W:") else ORDER_OWNER[k]
        img = n in EQ.IMAGE_NODES
        dag.local("local:" + n, arb(0) if img else delta[n], owner=owner, order=k)
        if not ins:
            dag.set(n, dag._locals["local:" + n])
        else:
            dag.operator_sum(n, k, "local:" + n, [(p[0], nrm(kind, i), c) for c, kind, i, p in ins], owner=owner)
    return dag


def cand_x0(mant) -> arb:                    # t = 2*0/b - 1 = -1: T_i(-1) = (-1)^i, exact dyadic
    s = sum(((-1) ** (i + j)) * mant[i][j] for i in range(len(mant)) for j in range(len(mant[i])))
    return exact(Fr(s, 2 ** T.SCALE_BITS))


def cand_sup(mant) -> arb:                   # |T_i| <= 1 on [-1,1]^2  =>  sup |hat| <= sum |c_ij|
    return exact(Fr(sum(abs(x) for row in mant for x in row), 2 ** T.SCALE_BITS))


def img_x0(rec) -> arb:
    m, e = rec["mid"]
    rm, re_ = rec["rad"]
    return exact(Fr(m) * Fr(2) ** e) + arb(0, exact(Fr(rm) * Fr(2) ** re_).abs_upper())


def norms_at(e) -> dict:
    n = OPS.one_step_norms(e)
    return {"k": [tight_upper(n["k0"]), tight_upper(n["k1"]), tight_upper(n["k2"])],
            "kz": [tight_upper(n["kz"]), tight_upper(n["kz1"]), tight_upper(n["kz2"])]}


def arb_rho_ledger(*, m, cell, rho, R_interval, D_interval, M_R2, usage, candidate_channels):
    """cell_ledger for the terminal cell whose rho = p + s*c_SR (SR_terminal_exception): identical formulas and
    gates, with rho carried as its 256-bit Arb enclosure (upper endpoint used for every charge)."""
    rho_u = arb(rho.abs_upper())
    first = rho_u * D_interval.abs_upper()
    curv = rho_u * rho_u * M_R2 / arb(2)
    exact_total = first + curv
    u_cover = outward_upper(exact_total, bits=spec.PRODUCTION_BITS)
    full = dict(usage, B_cover=u_cover)
    full.setdefault("B_other", Fr(0))
    enclosure = R_interval + arb(0, rho_u.abs_upper()) * D_interval + arb(0, curv.abs_upper())
    gates = ledger.top_level_gates(full)
    return {"detector": "SR", "cell_index": cell["index"], "m": m, "e0": cell["e0"], "rho": cell["rho"],
            "rho_enclosure_upper": str(mag_fraction(rho_u)), "C_upper": cell["C_upper"],
            "R_interval_mag": str(mag_fraction(R_interval)), "D_interval_mag": str(mag_fraction(D_interval)),
            "M_R2": str(mag_fraction(M_R2)),
            "cover": {"usage": str(u_cover), "cap": str(spec.TOP_BUDGETS["B_cover"]),
                      "utilization": float(Fr(u_cover) / spec.TOP_BUDGETS["B_cover"]),
                      "children": {"nominal_first_order": str(mag_fraction(rho_u * arb(D_interval.mid()).abs_upper())),
                                   "derivative_uncertainty": str(mag_fraction(rho_u * arb(D_interval.rad()))),
                                   "curvature": str(mag_fraction(curv))},
                      "style": "STYLE_1_COMPLETE_D_INTERVAL"},
            "top_level_gates": gates, "nested_candidate_gates": ledger.nested_candidate_gates(candidate_channels),
            "local_gates": ledger.local_gates(cell["C_upper"]), "target_gate": ledger.target_gate(enclosure),
            "status": gates["total"]["status"],
            "note": "terminal cell: rho carried as Arb enclosure (SR_terminal_exception); formulas identical to cell_ledger"}


def t4(t3: dict, *, crude_only=False) -> dict:
    cell_index = t3["cell"]
    cell = T.frozen_cell(cell_index)
    built = T.build_cell_candidates(cell_index)["scientific"]
    mant = {x["node"]: x["mantissas"] for x in built["candidates"]}
    hashes = {x["node"]: x["identity_hash"] for x in built["candidates"]}
    if hashlib.sha256(T.canonical(sorted(hashes.items()))).hexdigest() not in t3["candidate_identity_list_sha256"]:
        raise T.T1Refusal("T3 record was produced from a different candidate set")
    struct = op_structure()
    C = Fr(cell["C_upper"])
    terminal = Fr(cell["rho"][1]) != 0
    with T.scientific_precision():
        g = T.cell_geometry(cell)
        e0, rho = g["e0"], g["rho"]
        e_cell = e0 + arb(0, rho.abs_upper())
        rho_x = rho if terminal else exact(Fr(cell["rho"][0]))
        n_mid, n_cell = norms_at(e0), norms_at(e_cell)
        mid = build_dag("mid", t3, C, n_mid, struct)
        cel = build_dag("cell", t3, C, n_cell, struct)
        refined, trails = {}, {}
        for r in range(5):
            inp = sr_refine.RefinementInputs(
                rho=rho_x, C=exact(C), k1=n_cell["k"][1], k2=n_cell["k"][2], e_abs=arb(e_cell.abs_upper()),
                eps_F_mid=mid.get(f"F:{r}:k0"), eps_D_mid=mid.get(f"F:{r}:k1"),
                eps_F_crude=cel.get(f"F:{r}:k0"), eps_D_crude=cel.get(f"F:{r}:k1"), eps_H_crude=cel.get(f"F:{r}:k2"),
                delta_H_cell=exact(Fr(t3["delta"]["cell"][f"F:{r}:k2"]["delta"])),
                eps_S2_cell=cel.get(f"Ssrc:{r}:k2"),
                sup_D_hat=cand_sup(mant[f"F:{r}:k1"]), sup_H_hat=cand_sup(mant[f"F:{r}:k2"]),
                eps_h1_d1=arb(0), eps_h1_d2=arb(0))
            res = sr_refine.refine_cell(inp, enabled=not crude_only)
            refined[r] = res
            trail = []
            if not crude_only:
                for it in range(1, res.iterations + 1):
                    x = sr_refine.refine_cell(inp, iterations=it)
                    trail.append({"iteration": it, "eps_F_cell": str(mag_fraction(x.eps_F_cell)),
                                  "eps_D_cell": str(mag_fraction(x.eps_D_cell)), "eps_H_cell": str(mag_fraction(x.eps_H_cell)),
                                  "sup_H": str(mag_fraction(x.sup_H))})
            trails[r] = {"summary": res.as_dict(), "sequence": trail,
                         "inputs": {k: str(mag_fraction(getattr(inp, k))) for k in (
                             "rho", "C", "k1", "k2", "e_abs", "eps_F_mid", "eps_D_mid", "eps_F_crude", "eps_D_crude",
                             "eps_H_crude", "delta_H_cell", "eps_S2_cell", "sup_D_hat", "sup_H_hat", "eps_h1_d1", "eps_h1_d2")}}
        x0i = t3["x0_images"]

        def value(node, mode):
            return cand_x0(mant[node]) if node in mant else img_x0(x0i[mode][node])
        enc = {"F": {r: assembly.enclose(value(f"F:{r}:k0", "mid"), mid.get(f"F:{r}:k0")) for r in range(5)},
               "D": {r: assembly.enclose(value(f"F:{r}:k1", "mid"), mid.get(f"F:{r}:k1")) for r in range(5)},
               "H": {r: assembly.enclose(value(f"F:{r}:k2", "mid"), refined[r].eps_H_cell) for r in range(5)},
               "H_crude": {r: assembly.enclose(value(f"F:{r}:k2", "mid"), cel.get(f"F:{r}:k2")) for r in range(5)},
               "W": {}}
        for k, dag, mode in ((0, mid, "mid"), (1, mid, "mid"), (2, cel, "cell")):
            enc["W"][k] = {(r, j): assembly.enclose(value(wnode(r, j, k), mode), dag.get(wnode(r, j, k)))
                           for r in range(4) for j in range(0, 4 - r)}
        per_m = {}
        chmax = {q: {r: Fr(t3["delta"]["mid"][f"F:{r}:k0"]["channels_max"][q]["value"]) for r in range(5)}
                 for q in ("eq", "trunc", "tail", "end", "int", "round")}
        for m in spec.M_VALUES:
            R_int = assembly.assemble(m, enc["F"], enc["W"][0])
            D_int = assembly.assemble(m, enc["D"], enc["W"][1])
            R2_int = assembly.assemble(m, enc["H"], enc["W"][2])
            R2_crude = assembly.assemble(m, enc["H_crude"], enc["W"][2])
            M_R2 = assembly.curvature_bound(R2_int)
            u_cand = sum(C * Fr(t3["delta"]["mid"][f"F:{r}:k0"]["delta"]) / m for r in range(m))
            channels = {q: sum(C * chmax[q][r] / m for r in range(m)) for q in chmax}
            u_kernel = sum(C * mag_fraction(mid.get(f"Ssrc:{r}:k0")) / m for r in range(m))
            for t in range(1, m):
                for r in range(t):
                    u_kernel += (Fr(1, t) - Fr(1, m)) * mag_fraction(mid.get(wnode(r, t - r - 1, 0)))
            eta_i = mag_fraction(assembly.assembly_arithmetic_excess(m, enc["F"], enc["W"][0], R_int))
            usage = {"B_candidate": u_cand, "B_kernel": u_kernel, "B_interval": eta_i, "B_rounding": Fr(0), "B_other": Fr(0)}
            if terminal:
                led = arb_rho_ledger(m=m, cell=cell, rho=rho, R_interval=R_int, D_interval=D_int, M_R2=M_R2,
                                     usage=usage, candidate_channels=channels)
            else:
                led = ledger.cell_ledger(m=m, cell=cell, R_interval=R_int, D_interval=D_int, M_R2=M_R2,
                                         usage=usage, candidate_channels=channels)
            rho_u = arb(rho_x.abs_upper())
            crude_cover = rho_u * D_int.abs_upper() + rho_u * rho_u * assembly.curvature_bound(R2_crude) / arb(2)
            led.update({"R_interval": record(R_int), "D_interval": record(D_int), "R2_interval": record(R2_int),
                        "R2_interval_unrefined": record(R2_crude),
                        "W_cover_unrefined_upper": str(mag_fraction(crude_cover)),
                        "B_cover_ratio": float(Fr(led["cover"]["usage"]) / spec.TOP_BUDGETS["B_cover"]),
                        "channel_provenance": {"B_rounding": "0: candidate values at x0 are exact dyadics; image values "
                                                            "at x0 are outward Arb balls (rounding inside the ball)",
                                               "nested_channels": "sum_(r<m) C * max_patch(channel q of F_r at e0) / m"}})
            per_m[m] = led
    out = {"schema": "rebaseguard.p5y.k1.sr.o9.t4-cell.v1", "cell": cell_index, "terminal_cell": terminal,
           "t3_record_sha256": t3["t3_record_sha256"], "C_upper": cell["C_upper"], "e0": cell["e0"], "rho": cell["rho"],
           "rho_upper": str(mag_fraction(rho_x)),
           "norms": {"mid": {k: [str(mag_fraction(x)) for x in v] for k, v in n_mid.items()},
                     "cell": {k: [str(mag_fraction(x)) for x in v] for k, v in n_cell.items()}},
           "dag_audit": {"mid": mid.audit(), "cell": cel.audit()},
           "eps_mid": {k: str(mag_fraction(v)) for k, v in sorted(mid.nodes.items())},
           "eps_cell": {k: str(mag_fraction(v)) for k, v in sorted(cel.nodes.items())},
           "refinement": {str(r): v for r, v in trails.items()},
           "x0_enclosures": {"F": {r: record(v) for r, v in enc["F"].items()}, "D": {r: record(v) for r, v in enc["D"].items()},
                             "H": {r: record(v) for r, v in enc["H"].items()},
                             "W": {k: {f"{r},{j}": record(v) for (r, j), v in d.items()} for k, d in enc["W"].items()}},
           "local_gates_all_patches": t3["checks"]["all_F_local_gates_all_patches"],
           "m": {str(m): v for m, v in per_m.items()}}
    out["all_m_status"] = {str(m): v["status"] for m, v in per_m.items()}
    out["B_cover_ratio"] = {str(m): v["B_cover_ratio"] for m, v in per_m.items()}
    out["t4_record_sha256"] = hashlib.sha256(canonical(out)).hexdigest()
    return out


def main():
    t3 = json.loads(Path(sys.argv[1]).read_text())
    T.check_threads()
    r = t4(t3)
    Path(sys.argv[2]).write_bytes(canonical(r))
    print(json.dumps({"cell": r["cell"], "status": r["all_m_status"], "B_cover_ratio": r["B_cover_ratio"],
                      "dag_audit": r["dag_audit"], "sha": r["t4_record_sha256"]}, indent=1, default=str))


if __name__ == "__main__":
    main()
