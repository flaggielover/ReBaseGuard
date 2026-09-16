"""Emit config/QUALIFICATION_PROTOCOL.json (frozen) or a seed-disjoint DEV protocol (development only).

    python3 -B code/make_protocol.py            -> config/QUALIFICATION_PROTOCOL.json
    python3 -B code/make_protocol.py --dev OUT  -> a DEV protocol: identical structure, every seed + 900000 and
                                                   e0 shifted by 1/1000, used only to calibrate before the freeze
"""
from __future__ import annotations

import hashlib
import json
import sys
from fractions import Fraction as Fr
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
REPO = NS.parents[2]

BOUND_CODE = ["rung3_engine.py", "rung3_residual.py", "cusum_order3.py", "k1_inputs.py", "manufactured_chain.py",
              "fixtures.py", "soundness.py", "run_fixture.py", "independent_crosscheck.py",
              "reference_differential.py", "real_operator_integration.py", "qualify_order3.py", "make_protocol.py",
              "make_manifest.py"]


def fixtures(dev: bool) -> list[dict]:
    s = 900000 if dev else 0
    sh = Fr(1, 1000) if dev else Fr(0)

    def e(x):
        return str(Fr(x) + sh)

    F = [
        {"id": "T01_random_n1_exact", "kind": "random", "n": 1, "seed": 1001 + s, "e0": e("1/10"), "rho": "1/50",
         "noise": "0"},
        {"id": "T02_random_n1_noise6", "kind": "random", "n": 1, "seed": 1002 + s, "e0": e("1/3"), "rho": "1/20",
         "noise": "1/1000000"},
        {"id": "T03_random_n3_noise3", "kind": "random", "n": 3, "seed": 1003 + s, "e0": e("1"), "rho": "1/50",
         "noise": "1/1000"},
        {"id": "T04_random_n3_exact", "kind": "random", "n": 3, "seed": 1004 + s, "e0": e("19/10"), "rho": "1/20",
         "noise": "0"},
        {"id": "T05_wide_cell_n3", "kind": "random", "n": 3, "seed": 1005 + s, "e0": e("1/10"), "rho": "1/4",
         "noise": "1/1000000", "k0": "1/8"},
        {"id": "T06_narrow_cell_n1", "kind": "random", "n": 1, "seed": 1006 + s, "e0": e("1/2"),
         "rho": "1/1000000", "noise": "1/1000000000"},
        {"id": "T07_positive_R3", "kind": "target_R3_m1", "n": 3, "seed": 1007 + s, "e0": e("1/5"), "rho": "1/100",
         "target": "2", "noise": "1/1000000"},
        {"id": "T08_negative_R3", "kind": "target_R3_m1", "n": 3, "seed": 1008 + s, "e0": e("1/5"), "rho": "1/100",
         "target": "-2", "noise": "1/1000000"},
        {"id": "T09_sign_crossing_at_e0", "kind": "target_R3_m1", "n": 1, "seed": 1009 + s, "e0": e("2/5"),
         "rho": "1/20", "target": "0", "noise": "0"},
        {"id": "T10_identically_zero_R3", "kind": "identically_zero_R3_m1", "e0": e("1/7"), "rho": "1/30",
         "noise": "0"},
        {"id": "T11_tiny_positive_R3", "kind": "constant_R3_m1", "value": "1/1000000000000", "e0": e("1/9"),
         "rho": "1/40", "noise": "0"},
        {"id": "T12_tiny_negative_R3", "kind": "constant_R3_m1", "value": "-1/1000000000000", "e0": e("1/9"),
         "rho": "1/40", "noise": "0"},
        {"id": "T13_tiny_positive_R3_noisy", "kind": "constant_R3_m1", "value": "1/1000000000000", "e0": e("1/9"),
         "rho": "1/40", "noise": "1/1000000000000000", "seed": 1013 + s},
        {"id": "T14_parity_near_zero", "kind": "parity_near_zero", "e0": "1/40", "rho": "1/40",
         "noise": "1/1000000", "seed": 1014 + s},
        {"id": "T15_ill_conditioned_C1000", "kind": "ill_conditioned", "C_target": 1000, "seed": 1015 + s,
         "e0": e("1/2"), "rho": "3133/10000000", "noise": "1/1000000000"},
        {"id": "T16_near_singular_C1e6", "kind": "ill_conditioned", "C_target": 1000000, "seed": 1016 + s,
         "e0": e("1/2"), "rho": "3133/10000000000", "noise": "0"},
        {"id": "T17_cusum_like_crho_C1233", "kind": "cusum_like_crho", "C_target": 1233, "e0": e("1/4000"),
         "rho": "0", "noise": "1/1000000000", "seed": 1017 + s},
        {"id": "T18_cusum_like_crho_noise6", "kind": "cusum_like_crho", "C_target": 1233, "e0": e("1/4000"),
         "rho": "0", "noise": "1/1000000", "seed": 1018 + s},
        {"id": "T19_inflated_dependencies_n3", "kind": "random", "n": 3, "seed": 1003 + s, "e0": e("1"),
         "rho": "1/50", "noise": "1/1000", "inflate": "10000"},
        {"id": "T20_inflated_dependencies_crho", "kind": "cusum_like_crho", "C_target": 1233, "e0": e("1/4000"),
         "rho": "0", "noise": "1/1000000000", "seed": 1017 + s, "inflate": "1000"},
        {"id": "T22_perturb_F0_controlled_K3", "kind": "controlled_K3", "e0": e("3/10"), "rho": "1/100",
         "noise": "0", "perturb_F": [0, "1/1000"]},
        {"id": "T23_perturb_H_controlled_K1", "kind": "controlled_K1", "e0": e("3/10"), "rho": "1/100",
         "noise": "0", "perturb_F": [2, "1/1000"]},
        {"id": "T24_perturb_D_controlled_K1", "kind": "controlled_K1", "e0": e("3/10"), "rho": "1/100",
         "noise": "0", "perturb_F": [1, "1/1000"]},
        {"id": "T21_random_n3_deg4", "kind": "random", "n": 3, "deg": 4, "seed": 1021 + s, "e0": e("3/2"),
         "rho": "1/25", "noise": "1/10000"},
    ]
    return F


def mutations() -> list[dict]:
    E, R = "rung3_engine.py", "rung3_residual.py"
    M = [
        ("M01_G_MID_DROP_K3_F", E, 'delta_mid") + k[3] * M(f"F:{r}")', 'delta_mid") + 0 * M(f"F:{r}")', True),
        ("M02_G_MID_LEIBNIZ_3K1H_TO_2", E, '+ arb(3) * k[1] * M(f"H:{r}") + src_mid)',
         '+ arb(2) * k[1] * M(f"H:{r}") + src_mid)', True),
        ("M03_G_MID_DROP_SOURCE", E, '+ arb(3) * k[1] * M(f"H:{r}") + src_mid)', '+ arb(3) * k[1] * M(f"H:{r}"))',
         True),
        ("M04_G_CASCADE_DROP_3K1_REFH", E, "+ arb(3) * k[1] * refH + src_cell)", "+ src_cell)", True),
        ("M05_G_CASCADE_MIDPOINT_RESIDUAL", E, '_up(g[r]["delta_cell"], f"g_{r} delta_cell")',
         '_up(g[r]["delta_mid"], f"g_{r} delta_cell")', True),
        ("M06_G_TAYLOR_DROPS_TOWER", E, 'keep(f"F:{r}:3", casc, gm + rho * tf4[r], gm)',
         'keep(f"F:{r}:3", casc, gm, gm)', True),
        ("M07_TF4_DROPS_K1_TERM", E, "for i in range(1, 5):", "for i in range(2, 5):", True),
        ("M08_TF_CANDIDATE_SUP_WITHOUT_ERROR", E, '_up(sh[n] + ex[n], "sup F")', '_up(sh[n], "sup F")', True),
        ("M09_SCLOSED_CELL_DROPS_DRIFT", E, 'M("Sclosed:3") + rho * s0_4, M("Sclosed:3")',
         'M("Sclosed:3") + 0 * s0_4, M("Sclosed:3")', True),
        ("M10_S_CASCADE_DROPS_J0", E, "casc = casc + arb(comb(3, i)) * jn[i] * cellx_h(r, 3 - i)",
         "casc = casc + arb(comb(3, i)) * jn[i] * cellx_h(r, 3 - i) * (1 if i else 0)", True),
        ("M11_W_TAYLOR_DROPS_TOWER", E, 'keep(node, casc, M(node) + rho * _up(T[("W", (r, j), 4)], "tower"), M(node))',
         "keep(node, casc, M(node), M(node))", True),
        ("M12_H_TAYLOR_WRONG_TOWER_ORDER", E, 'M(f"h:{j}:3") + rho * _up(T[("h", j, 4)], "tower")',
         'M(f"h:{j}:3") + rho * _up(T[("h", j, 3)], "tower")', True),
        ("M13_ASSEMBLY_DROPS_W", E,
         'rows += [("W", r, t - r - 1, Fr(1, t) - Fr(1, m)) for t in range(1, m) for r in range(t)]', "rows += []",
         True),
        ("M14_COEFFICIENT_1_OVER_T", E, "Fr(1, t) - Fr(1, m)) for t", "Fr(1, t)) for t", True),
        ("M15_EXPORT_USES_MID_RADIUS", E, "r_cell = (c_lo - fraction_of(rad_cell), c_hi + fraction_of(rad_cell))",
         "r_cell = (c_lo - fraction_of(rad_mid), c_hi + fraction_of(rad_mid))", True),
        ("M16_RHO_ZERO", E, 'rho = _up(inp["rho"], "rho")', 'rho = arb(0) * _up(inp["rho"], "rho")', True),
        ("R01_RESIDUAL_LEIBNIZ_COEFFICIENTS", R, "TERMS = tuple((comb(RUNG, i), i,", "TERMS = tuple((1, i,", True),
        ("R02_RESIDUAL_ENVELOPE_DROPS_SHIFT", R, "env = env + arb(c) * k_[i + 1] * s", "env = env + arb(c) * k_[i] * s",
         True),
        ("R03_RESIDUAL_OPERATOR_ORDER_REVERSED", R, "res = res - cert.K(poly, i).scale(arb(c))",
         "res = res - cert.K(poly, 3 - i).scale(arb(c))", True),
        ("R04_RESIDUAL_SOURCE_SIGN", R, "res = res - cert.vec(src)", "res = res + cert.vec(src)", True),
        ("R05_RESIDUAL_R0_USES_CANDIDATE_SOURCE", R,
         'src = cert.P["Sclosed", 0, 3] if r == 0 else cert.P["S", r, 3]', 'src = cert.P["S", r, 3]', True),
    ]
    return [{"id": i, "target": t, "old": o, "new": n, "required": req} for i, t, o, n, req in M]


def build(dev: bool) -> dict:
    code = NS / "code"
    rel = "level4/closure_proofs/p5y_k5_cusum_order3_real_producer/code/"
    return {
        "schema": "rebaseguard.p5y.k5.order3-real-producer.qualification-protocol.v1",
        "status": "DEV_CALIBRATION_ONLY" if dev else "FROZEN_PRE_RESULT",
        "frozen_utc": "2026-09-16",
        "scope": ("NON-SCIENTIFIC qualification of the real CUSUM signed order-3 producer: Arb engine and rung-3 "
                  "residual on manufactured chain systems with exact derivatives; differential against the frozen "
                  "reference kernel (10911e51); independent rational-function cross-check; CUSUM Arb kernels on "
                  "SYNTHETIC polynomials; fail-closed controls; K1 record validation on committed copies. No real "
                  "CUSUM cell is evaluated, no R''' of any (D,m) is computed, no K5 probe, no authorization."),
        "execution_rule": ("Development used a DEV protocol (seeds + 900000, e0 shifted). The trials below run only "
                           "after the commit that freezes this file, the gates and the bound code. Any bound-code "
                           "change after that commit invalidates this protocol."),
        "real_cell_qualification": "NOT_AUTHORIZED: no pre-result mechanism permits a real CUSUM cell to be used "
                                   "for producer qualification and excluded from K5 (design DESIGN.md section 6 "
                                   "leaves L4 to the owner; the frozen feasibility oracle requires probe cells be "
                                   "fixed before any R''' value exists). No real cell is run.",
        "runtime_contract": {"python": "3.12.3", "python_flint": "0.9.0", "numpy": "2.5.2",
                             "host": "rebaseguard-vultr-02", "prefix": "/root/work/rbg-cusum-aux5-venv",
                             "machine": "x86_64"},
        "assembly_table": {"path": "level4/closure_proofs/p5y_k1_cover_ledger_successor/config/checkpoint.json",
                           "key": "assembly",
                           "sha256": "1c2a6825f19e19de6fb588647ca3fc4618068087ef0976292ca7bbeca701f13f"},
        "fixtures": fixtures(dev),
        "mutations": mutations(),
        "mutation_trials": ["T22_perturb_F0_controlled_K3", "T23_perturb_H_controlled_K1",
                            "T24_perturb_D_controlled_K1", "T01_random_n1_exact", "T09_sign_crossing_at_e0", "T11_tiny_positive_R3",
                            "T04_random_n3_exact", "T07_positive_R3", "T15_ill_conditioned_C1000",
                            "T17_cusum_like_crho_C1233", "T02_random_n1_noise6", "T21_random_n3_deg4",
                            "T14_parity_near_zero"],
        "mutation_rule": ("A mutation is DETECTED iff some mutation trial (in the listed order, stopping at the first "
                          "detection) shows a containment violation against exact truth, or, on a noise-0 trial, "
                          "the max certified G-residual delta_mid exceeds residual_consistency_threshold. Refusals "
                          "and crashes are recorded and never count. QM PASS iff every required mutation is "
                          "detected."),
        "whole_cell_mutations": ["M05_G_CASCADE_MIDPOINT_RESIDUAL", "M06_G_TAYLOR_DROPS_TOWER",
                                 "M09_SCLOSED_CELL_DROPS_DRIFT", "M11_W_TAYLOR_DROPS_TOWER", "M16_RHO_ZERO"],
        "residual_consistency_threshold": "1/1000000000000000000000000000000000000000000000000000000000000",
        "precision": {"bits": [128, 192, 256, 384, 512],
                      "fixtures": ["T01_random_n1_exact", "T11_tiny_positive_R3", "T16_near_singular_C1e6",
                                   "T17_cusum_like_crho_C1233", "T18_cusum_like_crho_noise6", "T15_ill_conditioned_C1000"],
                      "classification": ("per fixture: UNSTABLE if a violation/refusal occurs, a sign flips "
                                         "POSITIVE<->NEGATIVE, or two intervals are disjoint across precisions; "
                                         "INCONCLUSIVE if the max width is not nonincreasing (tolerance 2^-64); "
                                         "CONTRACTING if width(512) < width(128)/2; else STAGNATING. Overall: the "
                                         "first label present in UNSTABLE > INCONCLUSIVE > STAGNATING > CONTRACTING. "
                                         "The binding label is on the WHOLE-CELL interval width; the same rule is "
                                         "also reported, non-binding, on the midpoint interval width")},
        "crosscheck_fixtures": ["T01_random_n1_exact", "T02_random_n1_noise6", "T09_sign_crossing_at_e0",
                                "T10_identically_zero_R3", "T11_tiny_positive_R3", "T14_parity_near_zero",
                                "T17_cusum_like_crho_C1233", "T15_ill_conditioned_C1000"],
        "crosscheck_pieces": 32,
        "operator_integration": [{"seed": 1, "e0": "1/3", "rho": "1/1000"},
                                 {"seed": 2, "e0": "3/2", "rho": "1/1000"},
                                 {"seed": 3, "e0": "1/20", "rho": "1/1000"}],
        "failclosed_base_fixture": "T01_random_n1_exact",
        "failclosed_huge_C_fixture": "T16_near_singular_C1e6",
        "failclosed_sign_fixture": "T10_identically_zero_R3",
        "failclosed_near_singular_fixture": "T16_near_singular_C1e6",
        "k1_validation_cells": [0, 309],
        "pure_modules": ["rung3_engine.py", "rung3_residual.py", "manufactured_chain.py", "fixtures.py",
                         "soundness.py", "run_fixture.py", "independent_crosscheck.py", "k1_inputs.py"],
        "forbidden_imports_pure": ["cusum_layer1", "cusum_layer2", "aux_certifier", "aux_collocation",
                                   "aux_propagate", "aux_refine", "order2", "refine2", "spec", "ancestry5",
                                   "cusum_order3", "subprocess", "socket", "urllib", "requests"],
        "producer_modules": ["rung3_engine.py", "rung3_residual.py", "cusum_order3.py"],
        "forbidden_producer_tokens": ["mag_fraction(", "finite_difference", "true_R(", ".truth(", "expand(",
                                      "abs(centre", "abs(r_cell", "abs(v[\"R3_cell\"]"],
        "forbidden_function_names": ["prepare", "collocation", "collocation_order3", "build_objects",
                                     "objects_order3", "_candidates_rung3", "all_residuals", "aux_residuals",
                                     "cell_obligations", "certify_order3", "validate"],
        "forbidden_loaded_modules": ["cusum_layer1", "cusum_layer2", "aux_collocation", "aux_certifier",
                                     "aux_propagate", "refine2", "cusum_order3", "spec"],
        "forbidden_loaded_modules_operator": ["aux_collocation", "aux_certifier", "aux_propagate", "refine2",
                                              "cusum_order3", "k1_inputs"],
        "bound_code_sha256": {rel + f: hashlib.sha256((code / f).read_bytes()).hexdigest() for f in BOUND_CODE},
        "gates": "config/PRE_RESULT_GATES.json",
    }


if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "--dev":
        Path(sys.argv[2]).write_text(json.dumps(build(True), indent=1) + "\n")
    else:
        (NS / "config/QUALIFICATION_PROTOCOL.json").write_text(json.dumps(build(False), indent=1) + "\n")
