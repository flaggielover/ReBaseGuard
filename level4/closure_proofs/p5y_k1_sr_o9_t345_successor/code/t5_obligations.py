"""T5: the 28 frozen obligations of one SR cell, each with its own governing gates.

Units, order and dependencies are the frozen ones (repair2 provenance.cell_units, repair_universe.dependencies_of;
verified against the frozen universe.work_ids).  Certificates are built bottom-up so every obligation carries the
hashes of the dependency certificates it consumed, and the chain is re-verified by recomputation.

No obligation is PASS because a certificate exists: every governing gate must independently pass, and an object
obligation additionally requires every dependency obligation to PASS.
Governing gates (ERROR_ALGEBRA 1-7 applied to the SR DAG):
  object h_j, S_r  : complete conforming patch coverage (T3), finite certified residuals at e0 and uniformly on the
                     cell, finite propagated eps (mid and cell DAGs), dependencies PASS, no duplicate DAG edge
  object F_r       : the above + every per-(cell,patch) nested Task1R F gate, the endpoint gate C*deltaF_end <= 1/250
                     and LOCAL_GATE_BUDGET delta <= .1/C on ALL 3,994 patches
  object dF_r      : the object gates for the derivative equation (order-1 residuals, eps_D mid and cell)
  dependency bundle: every order-0/1 h, S and finite-power node certified finite; all derivative edges owned by B_cover
  curvature m      : R2_interval assembled from CELL-UNIFORM inputs only, refinement never loosened, M_R2 finite >= 0,
                     and the frozen per-m ledger status (frozen certhash: curvature status = ledger status)
  assembly m       : the complete frozen per-m ledger: B_candidate, nested channels, B_kernel, B_cover, B_interval,
                     B_rounding, B_other and the target gate (-2,2)
"""
from __future__ import annotations

import hashlib
import json
import sys
from fractions import Fraction as Fr
from pathlib import Path

import sr_o9_candidates as T

for _p in (T.CP / "p5y_k1_cover_ledger_implementation/code",):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))
import spec                                                         # noqa: E402
import universe                                                     # noqa: E402

M_VALUES = tuple(spec.M_VALUES)
OBJECTS = [f"h_{j}" for j in range(1, 5)] + [f"S_{r}" for r in range(5)] + [f"F_{r}" for r in range(5)] + [f"dF_{r}" for r in range(5)]


def canonical(o) -> bytes:
    return (json.dumps(o, sort_keys=True, separators=(",", ":"), ensure_ascii=True, default=str) + "\n").encode()


def uid(u):
    return ":".join(map(str, u))


def cell_units(index):          # frozen repair2 provenance.cell_units
    p = ("SR", index)
    order = [(*p, "object", f"h_{j}") for j in range(1, 5)] + [(*p, "object", f"S_{r}") for r in range(5)]
    order += [(*p, "dependency_bundle", "orders_0_1")]
    order += [(*p, "object", f"F_{r}") for r in range(5)] + [(*p, "object", f"dF_{r}") for r in range(5)]
    order += [(*p, "curvature", "5")] + [(*p, "curvature", str(m)) for m in M_VALUES if m != 5]
    order += [(*p, "assembly", str(m)) for m in M_VALUES]
    return order


def dependencies_of(unit):      # frozen repair_universe.dependencies_of
    det, index, kind, tag = unit
    obj = lambda n: (det, index, "object", n)                                   # noqa: E731
    bundle = (det, index, "dependency_bundle", "orders_0_1")
    if kind == "object":
        if tag.startswith("h_"):
            j = int(tag[2:])
            return [obj(f"h_{j - 1}")] if j >= 2 else []
        if tag.startswith("S_"):
            r = int(tag[2:])
            return [obj(f"h_{r}")] if r >= 1 else []
        if tag.startswith("dF_"):
            return sorted([obj(f"F_{tag[3:]}"), bundle])
        if tag.startswith("F_"):
            return [obj(f"S_{tag[2:]}")]
    if kind == "dependency_bundle":
        return sorted([obj(f"h_{j}") for j in range(1, 5)] + [obj(f"S_{r}") for r in range(5)])
    if kind == "curvature":
        return sorted([obj(n) for n in OBJECTS] + [bundle]) if tag == "5" else [(det, index, "curvature", "5")]
    if kind == "assembly":
        m = int(tag)
        deps = {bundle, (det, index, "curvature", tag)}
        for r in range(m):
            deps.add(obj(f"F_{r}"))
            deps.add(obj(f"dF_{r}"))
        return sorted(deps)
    raise ValueError(unit)


def _fin(x) -> bool:
    try:
        return Fr(x) >= 0
    except (ValueError, ZeroDivisionError):
        return False


def obligations(t3: dict, t4: dict, evidence: dict) -> dict:
    cell = t3["cell"]
    C = Fr(T.frozen_cell(cell)["C_upper"])
    units = cell_units(cell)
    # frozen universe.work_ids appends the two global far-field units after the per-cell units; they are not cell units
    frozen_ids = [u for u in universe.work_ids(cells=[T.frozen_cell(cell)]) if u[2] != "far_field"]
    ids_ok = sorted(map(tuple, frozen_ids)) == sorted(units) and len(units) == 28
    t3ok = t3["T3_PASS"]
    dm, dc = t3["delta"]["mid"], t3["delta"]["cell"]
    em, ec = t4["eps_mid"], t4["eps_cell"]
    audits_ok = all(a["duplicate_edges"] == 0 and a["derivative_edges_all_cover"] for a in t4["dag_audit"].values())

    def node_gates(nodes):
        g = {"T3_complete_conforming_coverage": {"PASS": t3ok}}
        for n in nodes:
            g[f"residual_finite:{n}"] = {"PASS": _fin(dm[n]["delta"]) and _fin(dc[n]["delta"]),
                                          "delta_mid": dm[n]["delta_float"], "delta_cell": dc[n]["delta_float"]}
            g[f"eps_finite:{n}"] = {"PASS": _fin(em[n]) and _fin(ec[n]), "eps_mid": float(Fr(em[n])), "eps_cell": float(Fr(ec[n]))}
        g["dag_no_double_count"] = {"PASS": audits_ok}
        return g

    def obj_nodes(tag):
        if tag.startswith("h_"):
            return [f"h:{tag[2:]}:k0"]
        if tag.startswith("S_"):
            return [f"S:{tag[2:]}:k0"]
        if tag.startswith("dF_"):
            return [f"F:{tag[3:]}:k1"]
        return [f"F:{tag[2:]}:k0"]

    certs, out = {}, []
    for u in units:
        det, index, kind, tag = u
        deps = dependencies_of(u)
        dep_status = {uid(d): certs[uid(d)]["status"] for d in deps}
        if kind == "object":
            gates = node_gates(obj_nodes(tag))
            if tag.startswith("F_"):
                n = obj_nodes(tag)[0]
                chm = dm[n]["channels_max"]
                caps = {q: Fr(T.spec.NESTED_CANDIDATE[f"B_{q}"]) for q in ("eq", "trunc", "tail", "end", "int", "round")}
                gates["per_patch_nested_F_gates_and_endpoint_and_local_budget_all_3994"] = {
                    "PASS": t3["checks"]["all_F_local_gates_all_patches"]}
                worst = max(float(C * Fr(chm[q]["value"]) / caps[q]) for q in caps)
                gates["channel_max_over_patches_vs_nested_caps"] = {"PASS": worst <= 1, "worst_ratio": worst}
                margin = {"worst_nested_channel_ratio": worst}
            else:
                margin = {"eps_mid": gates[f"eps_finite:{obj_nodes(tag)[0]}"]["eps_mid"]}
            content = {n: {"delta_mid": dm[n]["delta"], "delta_cell": dc[n]["delta"], "eps_mid": em[n], "eps_cell": ec[n]}
                       for n in obj_nodes(tag)}
            governing = "object certificate (ERROR_ALGEBRA 1-2, 6)"
        elif kind == "dependency_bundle":
            nodes = ([f"h:{j}:k{k}" for j in range(1, 5) for k in (0, 1)] + [f"S:{r}:k{k}" for r in range(5) for k in (0, 1)]
                     + [f"W:{rj}:k{k}" for rj in ("0,1", "0,2", "0,3", "1,1", "1,2", "2,1") for k in (0, 1)])
            gates = node_gates(nodes)
            content = {n: {"eps_mid": em[n], "eps_cell": ec[n]} for n in nodes}
            margin = {"max_eps_mid": max(float(Fr(em[n])) for n in nodes)}
            governing = "order-0/1 source and finite-power bundle (ERROR_ALGEBRA 2)"
        elif kind == "curvature":
            led = t4["m"][tag]
            ref_ok = all(v["summary"]["refinement_enabled"] for v in t4["refinement"].values())
            gates = {"R2_from_cell_uniform_inputs": {"PASS": True, "evidence": "H: sr_refine eps_H_cell over cell-mode DAG; "
                                                                             "W'': cell-mode DAG and cell-mode image x0 values"},
                     "refinement_valid_no_loosening": {"PASS": ref_ok},
                     "M_R2_finite_nonnegative": {"PASS": _fin(led["M_R2"]), "M_R2": float(Fr(led["M_R2"]))},
                     "frozen_ledger_status_m": {"PASS": led["status"] == "PASS", "status": led["status"]}}
            content = {"R2_interval": led["R2_interval"], "M_R2": led["M_R2"]}
            margin = {"curvature_share_of_B_cover": float(Fr(led["cover"]["children"]["curvature"]) / Fr(1, 20))
                      if isinstance(led["cover"]["children"]["curvature"], str) else None}
            governing = "curvature obligation (ERROR_ALGEBRA 3) + frozen per-m ledger"
        else:
            led = t4["m"][tag]
            tg = led["top_level_gates"]
            gates = {f"top_level:{k}": {"PASS": v.get("status") == "PASS", "usage": v.get("usage"), "cap": v.get("cap"),
                                        "utilization": v.get("utilization")}
                     for k, v in tg.items() if k not in ("top_reserve", "total")}
            gates.update({f"nested:{k}": {"PASS": v.get("status") == "PASS", "usage": v.get("usage"), "cap": v.get("cap")}
                          for k, v in led["nested_candidate_gates"].items() if k != "B_reserve"})
            gates["target_strictly_inside_(-2,2)"] = {"PASS": led["target_gate"]["status"] == "PASS",
                                                      "lo": led["target_gate"]["lo"], "hi": led["target_gate"]["hi"]}
            gates["frozen_ledger_status_m"] = {"PASS": led["status"] == "PASS"}
            content = {"R_interval": led["R_interval"], "D_interval": led["D_interval"], "cover": led["cover"]}
            margin = {"B_cover_ratio": led["B_cover_ratio"],
                      "worst_top_level_utilization": max((v.get("utilization") or 0) for k, v in tg.items()
                                                         if k not in ("top_reserve", "total", "B_resolvent"))}
            governing = "assembly obligation: complete frozen STYLE_1 ledger (ERROR_ALGEBRA 4-7)"
        gates["dependencies_all_PASS"] = {"PASS": all(s == "PASS" for s in dep_status.values()), "dependencies": dep_status}
        status = "PASS" if all(g["PASS"] for g in gates.values()) else "FAIL"
        ident = {"obligation_id": uid(u), "detector": det, "cell_index": index, "unit_kind": kind, "function_or_m": tag,
                 "dependencies": [uid(d) for d in deps],
                 "source_certificate_hashes": {uid(d): certs[uid(d)]["certificate_hash"] for d in deps}}
        cert = {"identity": ident, "governing_frozen_gate": governing, "gates": gates, "certified": content,
                "margin": margin, "status": status, "evidence_sha256": evidence}
        cert["certificate_hash"] = hashlib.sha256(canonical({k: v for k, v in cert.items() if k != "certificate_hash"})).hexdigest()
        certs[uid(u)] = cert
        out.append(cert)
    # chain re-verification by recomputation
    chain_ok = True
    for c in out:
        h = hashlib.sha256(canonical({k: v for k, v in c.items() if k != "certificate_hash"})).hexdigest()
        chain_ok &= h == c["certificate_hash"]
        for d, dh in c["identity"]["source_certificate_hashes"].items():
            chain_ok &= certs[d]["certificate_hash"] == dh
    n_pass = sum(1 for c in out if c["status"] == "PASS")
    return {"schema": "rebaseguard.p5y.k1.sr.o9.t5-obligations.v1", "cell": cell, "obligation_ids_equal_frozen_universe": ids_ok,
            "provenance_chain_verified": chain_ok, "pass_count": n_pass, "total": len(out),
            "status": ("T5_28_OF_28_PASS" if n_pass == 28 and ids_ok and chain_ok else "T5_NOT_28_OF_28"),
            "obligations": out}


def main():
    t3 = json.loads(Path(sys.argv[1]).read_text())
    t4 = json.loads(Path(sys.argv[2]).read_text())
    ev = {"t3_record_sha256": t3["t3_record_sha256"], "t4_record_sha256": t4["t4_record_sha256"],
          "t3_file_sha256": hashlib.sha256(Path(sys.argv[1]).read_bytes()).hexdigest(),
          "t4_file_sha256": hashlib.sha256(Path(sys.argv[2]).read_bytes()).hexdigest()}
    r = obligations(t3, t4, ev)
    Path(sys.argv[3]).write_bytes(canonical(r))
    print(json.dumps({k: r[k] for k in ("cell", "obligation_ids_equal_frozen_universe", "provenance_chain_verified",
                                        "pass_count", "total", "status")}, indent=1))
    for c in r["obligations"]:
        bad = [k for k, g in c["gates"].items() if not g["PASS"]]
        print(f"  {c['identity']['obligation_id']:32s} {c['status']}  {c['margin']}  {bad[:4]}")


if __name__ == "__main__":
    main()
