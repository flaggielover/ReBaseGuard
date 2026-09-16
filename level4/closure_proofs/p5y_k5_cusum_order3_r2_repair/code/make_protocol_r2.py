"""Emit config/QUALIFICATION_PROTOCOL_R2.json (frozen) or a seed-disjoint DEV protocol.

    python3 -B code/make_protocol_r2.py             -> config/QUALIFICATION_PROTOCOL_R2.json
    python3 -B code/make_protocol_r2.py --dev OUT   -> DEV: R1 fixtures from R1's own DEV builder, sigma seeds + 900000,
                                                       a different R05 fixture geometry; calibration only

R1 is retained verbatim: every R1 fixture, all 21 mutations, the mutation trial order, precision, cross-check,
operator integration, fail-closed and fence settings come from R1's frozen QUALIFICATION_PROTOCOL.json. R2 appends
the R05 isolating fixture T25 (last in the mutation trials, so R1 detections are unchanged) and the graded-method
sections.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
REPO = NS.parents[2]
CP = NS.parents[0]
R1_NS = CP / "p5y_k5_cusum_order3_real_producer"
REL = "level4/closure_proofs/"

R2_BOUND = ["graded_dag.py", "sigma_systems.py", "r05_fixture.py", "cusum_graded.py", "operator_parity_integration.py",
            "cell0_forecast.py", "e0_operator_estimate.py", "qualify_r2.py", "make_protocol_r2.py",
            "make_manifest_r2.py"]


def r1_bound() -> dict:
    files = sorted(p for p in R1_NS.rglob("*") if p.is_file() and "__pycache__" not in p.parts)
    return {str(p.relative_to(REPO)): hashlib.sha256(p.read_bytes()).hexdigest() for p in files}


def sigma_fixtures(dev: bool) -> list[dict]:
    s = 900000 if dev else 0
    crho = "3133/12330000"                     # 0.3133 / 1233
    crho100 = "3133/1000000"
    odd = lambda x: ["0", x, "-" + x]
    even = lambda x: [x, x, x]
    return [
        {"id": "S01_cell0_like_C4", "seed": 2001 + s, "C_target": 4, "e0": "1/20", "rho": "1/20", "noise": "1/1000000"},
        {"id": "S02_cusum_cell0_analogue_C1233", "seed": 2002 + s, "C_target": 1233, "e0": crho, "rho": crho,
         "noise": "1/1000000"},
        {"id": "S03_cusum_cell0_analogue_C1233_exactish", "seed": 2003 + s, "C_target": 1233, "e0": crho, "rho": crho,
         "noise": "1/1000000000"},
        {"id": "S04_far_cell_fallback", "seed": 2004 + s, "C_target": 5, "k_scale": "1/20", "e0": "1/4", "rho": "1/50",
         "noise": "1/100000"},
        {"id": "S05_perturb_F_odd_C50", "seed": 2005 + s, "C_target": 50, "e0": "1/400", "rho": "1/400", "noise": "0",
         "perturb": [0, odd("1/1000")]},
        {"id": "S06_perturb_D_even_C50", "seed": 2006 + s, "C_target": 50, "e0": "1/400", "rho": "1/400", "noise": "0",
         "perturb": [1, even("1/1000")]},
        {"id": "S07_perturb_F_even_C50", "seed": 2007 + s, "C_target": 50, "e0": "1/400", "rho": "1/400", "noise": "0",
         "perturb": [0, even("1/1000")]},
        {"id": "S08_perturb_H_odd_C50", "seed": 2008 + s, "C_target": 50, "e0": "1/400", "rho": "1/400", "noise": "0",
         "perturb": [2, odd("1/1000")]},
        {"id": "S09_perturb_D_odd_C50", "seed": 2009 + s, "C_target": 50, "e0": "1/400", "rho": "1/400", "noise": "0",
         "perturb": [1, odd("1/1000")]},
        {"id": "S10_cell_centred_at_zero", "seed": 2010 + s, "C_target": 10, "e0": "0", "rho": "1/50",
         "noise": "1/1000000"},
        {"id": "S11_negative_side_cell", "seed": 2011 + s, "C_target": 10, "e0": "-1/40", "rho": "1/40",
         "noise": "1/1000000"},
        {"id": "S12_wide_cell_deg3", "seed": 2012 + s, "C_target": 3, "deg": 3, "k_scale": "1/4", "e0": "1/10",
         "rho": "1/10", "noise": "1/10000"},
        {"id": "S13_small_odd_eigen_C100", "seed": 2013 + s, "C_target": 100, "c": "1/5", "e0": crho100,
         "rho": crho100, "noise": "1/10000000"},
        {"id": "S14_cusum_analogue_perturb_F_odd", "seed": 2014 + s, "C_target": 1233, "e0": crho, "rho": crho,
         "noise": "0", "perturb": [0, odd("1/1000000")]},
        {"id": "S15_leakage_probe_odd_C4", "seed": 2015 + s, "C_target": 4, "e0": "3/40", "rho": "3/40", "noise": "0",
         "perturb": [0, odd("1/1000")]},
        {"id": "S16_perturb_H_even_C50", "seed": 2016 + s, "C_target": 50, "e0": "1/400", "rho": "1/400", "noise": "0",
         "perturb": [2, even("1/1000")]},
    ]


def graded_mutations() -> list[dict]:
    T = "graded_dag.py"
    M = [
        ("GM01_OPERATOR_PARITY_RULE_INVERTED", "    if (i + flip_base) % 2 == 0:       # parity preserving at e = 0",
         "    if (i + flip_base) % 2 == 1:       # parity preserving at e = 0"),
        ("GM02_LEAKAGE_DROPPED", '    leak = _up(eta * hull[i + 1], "leak")', '    leak = _up(arb(0) * hull[i + 1], "leak")'),
        ("GM03_RESOLVENT_PERTURBATION_DROPPED", '    M = {"ee": Ce0 * a, "eo": Ce0 * b, "oe": Co0 * b, "oo": Co0 * a}',
         '    M = {"ee": Ce0 * a * 0, "eo": Ce0 * b * 0, "oe": Co0 * b * 0, "oo": Co0 * a * 0}'),
        ("GM04_EVEN_ODD_RESOLVENT_SWAPPED",
         '    out = {"ee": inv["ee"] * Ce0, "eo": inv["eo"] * Co0, "oe": inv["oe"] * Ce0, "oo": inv["oo"] * Co0}',
         '    out = {"ee": inv["ee"] * Co0, "eo": inv["eo"] * Ce0, "oe": inv["oe"] * Co0, "oo": inv["oo"] * Ce0}'),
        ("GM05_EXPORT_USES_ODD_COMPONENT", "            rad = rad + R1E.exact(abs(c)) * (v.e if parity else v.t)",
         "            rad = rad + R1E.exact(abs(c)) * (v.o if parity else v.t)"),
        ("GM06_J_PARITY_AS_K",
         '                acc = acc + apply_op(jn, jh, i, N[f"h:{rr}:{kk - i}"], eta, 1, parity).scale(comb(kk, i))',
         '                acc = acc + apply_op(jn, jh, i, N[f"h:{rr}:{kk - i}"], eta, 0, parity).scale(comb(kk, i))'),
        ("GM07_TOTAL_CAPPED_BY_MIN", '        s = _up(e + o, "e+o")',
         '        s = _up(e if e.upper() <= o.upper() else o, "e+o")'),
        ("GM08_TRUE_SUP_PARITY_SWAPPED",
         "    return V(right, wrong, right) if parity_at_0 == 1 else V(wrong, right, right)",
         "    return V(wrong, right, right) if parity_at_0 == 1 else V(right, wrong, right)"),
        ("GM09_ENVELOPE_OPERATOR_ORDER_SHIFT",
         "        acc = acc + apply_op(norms, hull, order, sv, eta, base, True).scale(coef)",
         "        acc = acc + apply_op(norms, hull, order - 1, sv, eta, base, True).scale(coef)"),
        ("GM10_RESOLVENT_CROSS_TERMS_DROPPED",
         '    return V(R["ee"] * v.e + R["eo"] * v.o, R["oe"] * v.e + R["oo"] * v.o, _up(C, "C") * v.t)',
         '    return V(R["ee"] * v.e, R["oo"] * v.o, _up(C, "C") * v.t)'),
        ("GM11_CELL_USES_MIDPOINT_ETA", '    eta = _up(inp["eta_mid"] if which == "mid" else inp["eta_cell"], "eta")',
         '    eta = _up(inp["eta_mid"], "eta")'),
    ]
    return [{"id": i, "target": T, "old": o, "new": n} for i, o, n in M]


# Required flags were fixed from the seed-disjoint DEV calibration BEFORE the freeze: the DEV run detected all 11
# graded mutations, so every graded mutation is required (no exemption).
REQUIRED_GRADED = {}


def build(dev: bool) -> dict:
    r1 = json.loads((R1_NS / "config/QUALIFICATION_PROTOCOL.json").read_text())
    if dev:
        sys.path.insert(0, str(R1_NS / "code"))
        import make_protocol as R1MP  # noqa: E402
        r1_fixtures = R1MP.fixtures(True)
    else:
        r1_fixtures = r1["fixtures"]
    t25 = ({"id": "T25_r05_isolating_closed_source", "kind": "r05_isolating", "base_kind": "controlled_K3",
            "e0": "3/10", "rho": "1/120", "source_offset": "1/300"} if dev else
           {"id": "T25_r05_isolating_closed_source", "kind": "r05_isolating", "base_kind": "controlled_K3",
            "e0": "13/40", "rho": "1/80", "source_offset": "1/500"})
    gm = graded_mutations()
    for m in gm:
        m["required"] = REQUIRED_GRADED.get(m["id"], True)
    proto = {k: v for k, v in r1.items() if k not in ("schema", "status", "frozen_utc", "scope", "execution_rule",
                                                       "bound_code_sha256", "fixtures", "mutation_trials", "gates")}
    proto.update({
        "schema": "rebaseguard.p5y.k5.order3-r2.qualification-protocol.v1",
        "status": "DEV_CALIBRATION_ONLY" if dev else "FROZEN_PRE_RESULT",
        "frozen_utc": "2026-09-16",
        "scope": ("NON-SCIENTIFIC R2 qualification. R1 producer re-qualified with the R05 isolating fixture (all 21 "
                  "R1 mutations retained). The graded (sigma-parity) error propagation is qualified on manufactured "
                  "sigma-symmetric systems with exact truth, the CUSUM Arb kernels are checked for the parity structure "
                  "on synthetic polynomials at e = 0, and a cell-0 radius forecast is computed from committed K1 "
                  "magnitudes only. No real CUSUM cell is evaluated; no R''' of any (D,m); no probe; no authorization."),
        "execution_rule": ("Development used a DEV protocol (seed-disjoint, different R05 geometry). The parts below "
                           "run only after the commit freezing this file, the gates, the feasibility criterion and the "
                           "bound code. R1 remains byte-identical (r1_bound_sha256)."),
        "fixtures": r1_fixtures + [t25],
        "mutation_trials": r1["mutation_trials"] + ["T25_r05_isolating_closed_source"],
        "r05_fixture": "T25_r05_isolating_closed_source",
        "r05_invariants": {"FIXTURE:unmutated": "zero", "FIXTURE:R05": "positive",
                           "ABL_ZERO_OFFSET:unmutated": "zero", "ABL_ZERO_OFFSET:R05": "zero",
                           "ABL_RESOLVE_CLOSED:unmutated": "zero", "ABL_RESOLVE_CLOSED:R05": "zero"},
        "sigma_fixtures": sigma_fixtures(dev),
        "graded_mutations": gm,
        "graded_mutation_trials": ["S05_perturb_F_odd_C50", "S09_perturb_D_odd_C50", "S08_perturb_H_odd_C50",
                                   "S06_perturb_D_even_C50", "S07_perturb_F_even_C50", "S16_perturb_H_even_C50",
                                   "S15_leakage_probe_odd_C4", "S14_cusum_analogue_perturb_F_odd",
                                   "S01_cell0_like_C4", "S02_cusum_cell0_analogue_C1233", "S10_cell_centred_at_zero",
                                   "S11_negative_side_cell", "S12_wide_cell_deg3", "S04_far_cell_fallback"],
        "graded_precision_fixtures": ["S02_cusum_cell0_analogue_C1233", "S03_cusum_cell0_analogue_C1233_exactish"],
        "stress_fixtures": ["S02_cusum_cell0_analogue_C1233", "S03_cusum_cell0_analogue_C1233_exactish",
                            "S13_small_odd_eigen_C100", "S01_cell0_like_C4"],
        "graded_failclosed_base": "S01_cell0_like_C4",
        "operator_parity_seeds": [11, 12] if not dev else [911, 912],
        "feasibility_criterion": json.loads((NS / "config/FEASIBILITY_CRITERION.json").read_text()),
        "r2_pure_modules": ["graded_dag.py", "sigma_systems.py", "r05_fixture.py"],
        "r2_forbidden_imports_pure": ["cusum_layer1", "cusum_layer2", "aux_certifier", "aux_collocation",
                                      "aux_propagate", "aux_refine", "order2", "refine2", "spec", "ancestry5",
                                      "cusum_order3", "subprocess", "socket", "urllib", "requests", "sharp_norms"],
        "r1_bound_sha256": r1_bound(),
        "bound_code_sha256": {REL + "p5y_k5_cusum_order3_r2_repair/code/" + f:
                              hashlib.sha256((NS / "code" / f).read_bytes()).hexdigest() for f in R2_BOUND},
        "gates": "config/PRE_RESULT_GATES_R2.json",
    })
    return proto


if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "--dev":
        Path(sys.argv[2]).write_text(json.dumps(build(True), indent=1) + "\n")
    else:
        (NS / "config/QUALIFICATION_PROTOCOL_R2.json").write_text(json.dumps(build(False), indent=1) + "\n")
