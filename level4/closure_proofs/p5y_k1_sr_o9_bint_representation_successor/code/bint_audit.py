"""B_int representation audit (read-only; NO certifier change adopted).
(1) predicted separate-remainder bound (the requested P_mid + R_sp representation,
    same frozen Lagrange ball) -- a LOWER bound on what that implementation reports;
(2) DIAGNOSTIC of an alternative NOT adopted: unchanged representation with the
    Lagrange factor A_9 = [-M/9!, M/9!], M = softplus_derivative_bound_tight(9)
    (the frozen P1 bound; rigorous by L-R3.1, but a governance decision)."""
import hashlib, json, time, resource
from fractions import Fraction as Fr
from math import factorial
import sr_o9_candidates as T, sr_o9_patch_certifier as PC, sr_o9_endpoint_strips as ES
from flint import arb
L, H = PC.L, PC.H
trace = json.load(open(__file__.rsplit("/code/", 1)[0] + "/evidence/bint_dependency_trace.json"))
frozen = L.softplus_local_enclosure
M9 = None
def p1_ball(centre, half_width, degree):
    a, E, a_next = frozen(centre, half_width, degree)
    A = arb(0, (M9 / arb(factorial(degree + 1))).upper())
    return a, arb(0, (A.abs_upper() * half_width ** (degree + 1)).upper()), A
out = {"predicted_separate_remainder": [], "alternative_diagnostic_NOT_ADOPTED": []}
for c in trace["cases"]:
    out["predicted_separate_remainder"].append({"cell": c["cell"], "patch": c["patch"], "old_int": c["old_int_channel_F0"],
        "predicted_new_int_lower_bound": c["predicted_new_int_core_F0"], "allowance": c["B_int_allowance"],
        "ratio": c["predicted_ratio_to_allowance"], "old_ratio": c["old_int_channel_F0"] / c["B_int_allowance"],
        "source_eps_max": max(max(p["V"]["eps_rad_times_rho9"], p["W"]["eps_rad_times_rho9"]) for p in c["panels"]),
        "a_next_radius_range": [min(p[s]["a_next_radius"] for p in c["panels"] for s in "VW"), max(p[s]["a_next_radius"] for p in c["panels"] for s in "VW")]})
for ci, (i, j) in ((0, (51, 63)), (0, (63, 54)), (150, (51, 63)), (150, (17, 11))):
    built = T.build_cell_candidates(ci)["scientific"]
    cell = T.frozen_cell(ci); C = Fr(cell["C_upper"]); nodes = [f"F:{r}:k0" for r in range(5)]
    with T.scientific_precision():
        M9 = L.softplus_derivative_bound_tight(H.SOFTPLUS_DEGREE + 1)
        cands = {x["node"]: T.to_arb_matrix(x["mantissas"]) for x in built["candidates"]}
        e0 = T.cell_geometry(cell)["e0"]
        g = PC.patch_geometry(i, j, e0); pan = PC.panelisation(i, j, g)
        res = {}
        for tag, fn in (("frozen_ball", frozen), ("p1_bound_ball", p1_ball)):
            L.softplus_local_enclosure = fn
            t0 = time.process_time()
            try:
                r = ES.certify_patch_strips(i, j, e0, cands, cand_hashes={}, C_gate=C, nodes=nodes)
            finally:
                L.softplus_local_enclosure = frozen
            n = r["nodes"]
            res[tag] = {"int_F0": n["F:0:k0"]["channels_float"]["int"],
                        "worst_int_over_allowance": max(n[k]["channels_float"]["int"] for k in n) / float(Fr(1, 500) / C),
                        "all_F_r_k0_gates_pass": all(n[k]["local_gates_all_pass"] for k in n),
                        "failing": sorted({g_ for k in n for g_, v in n[k]["local_gates"].items() if not v["PASS"]}),
                        "worst_endpoint_ratio": max(n[k]["end_over_gate"] for k in n), "cpu_s": time.process_time() - t0,
                        "hash": hashlib.sha256(T.canonical(n)).hexdigest()}
        p1_E = pan["p1"]["E_d"]
    out["alternative_diagnostic_NOT_ADOPTED"].append({"cell": ci, "patch": [i, j], "B_int_allowance": float(Fr(1, 500) / C),
        "P1_E_d_frozen_check": p1_E, "M9_over_9fact": float(M9 / arb(factorial(9))), **res})
out["peak_rss_kib"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
print(json.dumps(out, indent=1, sort_keys=True))
