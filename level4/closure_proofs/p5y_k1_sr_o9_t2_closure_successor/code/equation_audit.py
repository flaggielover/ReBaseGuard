"""Phase 2: final equation / contract audit (+ numerical check of h1 through the const:1 contracts)."""
import glob
import json
import re
from collections import defaultdict
from fractions import Fraction as Fr
from pathlib import Path

import sr_o9_candidates as T
import sr_o9_equations as EQ
import sr_o9_patch_certifier as PC
import t2_final_certifier as FC
from flint import arb

NS = Path(__file__).resolve().parents[1]
T2 = T.CP / "p5y_k1_sr_o9_t2_per_patch_successor"
REP_CELLS = (0, 150, 250, 275, 313, 315)


def dy(enc):
    m, e = enc
    return arb(m) * arb(2) ** e


def main():
    checks, info = {}, {}
    m = EQ.build_map()
    committed = json.loads((T2 / "config/EQUATION_MAP.json").read_text())
    checks["equation_map_equals_committed"] = (m["equation_map_sha256"] == committed["equation_map_sha256"]
                                               and T.canonical(m) == T.canonical(committed))
    info["equation_map_sha256"] = m["equation_map_sha256"]
    census = T.verify_census()
    t1 = json.loads((T.CP / "p5y_k1_sr_o9_executor_t1_successor/config/T1_MANIFEST.json").read_text())
    checks["candidates_46_unique_equal_T1"] = (len(T.BASIS_ORDER) == 46 == len(set(T.BASIS_ORDER))
                                               and T.BASIS_ORDER == t1["candidate_universe"]["basis_order"])
    checks["nodes_45_residual_18_image_63_unique"] = (len(EQ.RESIDUAL_NODES) == 45 and len(EQ.IMAGE_NODES) == 18
                                                      and len(set(FC.NODES)) == 63)
    # operator applications, recorded independently of the Expr merge
    apps = defaultdict(list)
    orig = EQ.op
    current = {"node": None}

    def rec_op(kind, i, cand):
        apps[current["node"]].append((kind, i, cand))
        return orig(kind, i, cand)
    EQ.op = rec_op
    try:
        exprs = {}
        for n in FC.NODES:
            current["node"] = n
            exprs[n] = EQ.image(n) if n in EQ.IMAGE_NODES else EQ.rhs(n)
    finally:
        EQ.op = orig
    census_set = {(c, s) for c, ss in census["shifts"].items() for s in ss}
    used, per_contract = set(), defaultdict(set)
    mism, undeclared = [], []
    for n, ex in exprs.items():
        from_apps = set()
        for kind, i, cand in apps[n]:
            exp = (EQ.K_EXP if kind == "K" else EQ.KZ_EXP)[i]
            for s in exp:
                from_apps.add((cand, s))
                if (cand, s) not in census_set:
                    undeclared.append((n, kind, i, cand, s))
        if from_apps != set(ex.terms):
            mism.append((n, sorted(from_apps ^ set(ex.terms))))
        for k in ex.terms:
            used.add(k)
            per_contract[EQ.contract_id(*k)].add(k)
    ids = [EQ.contract_id(c, s) for c, s in sorted(used)]
    checks["every_operator_use_maps_to_a_declared_contract"] = not undeclared
    checks["node_contracts_equal_operator_applications"] = not mism
    checks["contract_ids_bijective"] = len(ids) == len(set(ids)) and all(len(v) == 1 for v in per_contract.values())
    checks["contracts_used_equal_frozen_census"] = used == census_set
    by_shift = {s: sum(1 for (_, ss) in used if ss == s) for s in range(4)}
    checks["contracts_102_shifts_43_35_20_4"] = len(used) == 102 and by_shift == {0: 43, 1: 35, 2: 20, 3: 4}
    checks["distinct_contract_candidates_46"] = len({c for c, _ in used}) == 46
    info["by_shift"] = by_shift
    info["operator_applications"] = sum(len(v) for v in apps.values())
    shifts_ok = all(set(EQ.K_EXP[i]) == T._SHIFTS[("K", i)] for i in (0, 1, 2))
    kz = [k for k in T._SHIFTS if k[0] != "K"]
    info["T1_shift_table_keys"] = [list(k) for k in T._SHIFTS]
    shifts_ok = shifts_ok and all(set(EQ.KZ_EXP[k[1]]) == T._SHIFTS[k] for k in kz)
    checks["operator_shift_supports_equal_T1_census_rule"] = shifts_ok
    # h1^(k) = delta_k0 - K^(k) 1 through the constant-candidate contracts
    h1 = {}
    for k in (0, 1, 2):
        ex = EQ.h1_image(k)
        want = {("const:1", s): {e: -v for e, v in p.items()} for s, p in EQ.K_EXP[k].items()}
        h1[k] = (ex.terms == want and ex.const == ({0: Fr(1)} if k == 0 else {}) and ex.src == [])
    checks["h1_equals_delta_minus_K1_symbolic"] = all(h1.values())
    checks["h1_nodes_use_only_const1_contracts"] = all(
        {c for c, _ in exprs[n].terms} == {"const:1"} and not exprs[n].src
        for n in FC.NODES if n.startswith("h:1:") or n.startswith("h1img"))
    checks["no_Phi_closed_form_in_equation_map"] = set(EQ.SRC_KINDS) == {"phiU", "phiL", "UphiU", "LphiL", "U2m1phiU", "L2m1phiL"}
    scan = {}
    for mod in (EQ, PC, T.__class__ and FC):
        pass
    for name, mod in (("sr_o9_equations", EQ), ("sr_o9_patch_certifier", PC), ("t2_final_certifier", FC),
                      ("sr_o9_endpoint_strips", FC.ES), ("sr_o9_bint_p1", FC.BP)):
        src = Path(mod.__file__).read_text()
        scan[name] = sorted(set(re.findall(r"gaussian_cdf|\berfc?\(|\bPhi\(|norm\.cdf", src)))
    info["phi_shortcut_token_scan"] = scan
    checks["no_Phi_shortcut_in_certifier_sources"] = not any(scan.values())
    # constant candidate is the exact dyadic 1 in every representative cell
    const_ok = {}
    for c in REP_CELLS:
        built = T.build_cell_candidates(c)["scientific"]
        x = [x for x in built["candidates"] if x["node"] == "const:1"]
        const_ok[c] = len(x) == 1 and x[0]["mantissas"] == T.EXACT_ONE and len(built["candidates"]) == 46
    checks["const1_is_exact_one_46_candidates"] = all(const_ok.values())
    # numerical: certified h1img centre enclosures contain the phi / Phi closed forms (independent check)
    num = []
    with T.scientific_precision():
        for f in sorted(glob.glob(str(NS / "evidence/dag/*.json"))):
            r = json.loads(Path(f).read_text())["scientific"]
            c, (i, j) = r["case"]["cell"], r["case"]["patch"]
            e = T.cell_geometry(T.frozen_cell(c))["e0"]
            g = PC.patch_geometry(i, j, e)
            U, Lw = g["U_c"] + e, g["L_c"] + e
            two_pi = (arb(2) * arb.pi()).sqrt()
            phi = lambda t: (-(t * t) / arb(2)).exp() / two_pi                    # noqa: E731
            closed = {0: arb(1) - (PC.L.gaussian_cdf(U) - PC.L.gaussian_cdf(Lw)),
                      1: phi(Lw) - phi(U), 2: U * phi(U) - Lw * phi(Lw)}
            for k in (0, 1, 2):
                nd = r["nodes"][f"h1img:k{k}"]
                mid, rad = dy(nd["centre_coefficient"]["mid"]), dy(nd["centre_coefficient"]["rad"])
                w = sum(dy(nd["channels"][ch]) for ch in ("trunc", "tail", "end"))
                gap = (closed[k] - mid).abs_upper()
                ok = PC.fr_upper(gap) <= PC.fr_upper(rad + w)
                num.append({"case": [c, i, j], "k": k, "contained": ok, "gap": float(gap),
                            "allowed": float(rad + w)})
    checks["h1_numeric_closed_form_contained_all"] = bool(num) and all(x["contained"] for x in num)
    info["h1_numeric"] = {"checks": len(num), "max_gap": max(x["gap"] for x in num) if num else None,
                          "max_allowed": max(x["allowed"] for x in num) if num else None}
    out = {"schema": "rebaseguard.p5y.k1.sr.o9.t2-equation-audit.v1", "checks": checks,
           "all_pass": all(checks.values()), "info": info, "h1_numeric_rows": num}
    (NS / "evidence/equation_audit.json").write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    print(json.dumps({"checks": checks, "all_pass": out["all_pass"], "info": {k: v for k, v in info.items()
                                                                             if k != "phi_shortcut_token_scan"}}, indent=1))


if __name__ == "__main__":
    main()
