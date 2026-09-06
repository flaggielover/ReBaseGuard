"""Deterministic, lightweight structural tests for the SR qualification lane.

Every test here is sub-second and single-threaded: this suite is designed to run
while the CUSUM Aux4 full-cover campaign occupies the four physical cores, and
must not compete with it. No test performs a representative cell certification.
"""
from __future__ import annotations

import ast
import json
import sys
from fractions import Fraction as F
from pathlib import Path

import pytest
from flint import arb, ctx

NS = Path(__file__).resolve().parents[1]
ROOT = NS.parents[2]
CODE = NS / "code"
IMPL = ROOT / "level4/closure_proofs/p5y_k1_cover_ledger_implementation/code"
SPECC = ROOT / "level4/closure_proofs/p5y_k1_cover_ledger_successor/code"
for _p in (str(CODE), str(IMPL), str(SPECC)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

ctx.prec = 256

import assembly                                                    # noqa: E402
import spec                                                        # noqa: E402
import universe                                                    # noqa: E402
import sr_dag                                                      # noqa: E402
import sr_operators as OPS                                         # noqa: E402
import sr_propagate as P                                           # noqa: E402
import sr_sources as SRC                                           # noqa: E402

EXCLUDED = json.loads((NS / "config/excluded_routes.json").read_text())


# ------------------------------------------------- frozen scope preservation
def test_top_level_universe_unchanged():
    assert len(universe.work_ids()) == spec.TOTAL_UNITS == 17978


def test_detector_scope_and_m_unchanged():
    assert spec.COUNTS == {"CUSUM": 326, "SR": 316}
    assert spec.M_VALUES == (1, 2, 3, 5)


def test_precision_cap_budgets_reserve_unchanged():
    assert spec.PRODUCTION_BITS == 256
    assert not spec.PRECISION_ESCALATION_ALLOWED
    assert not spec.DEGREE_ADAPTATION_ALLOWED
    assert spec.HARD_CAP_CPU_H == 1126
    assert sum(spec.TOP_BUDGETS.values()) == F(19, 100)
    assert spec.TOP_RESERVE == F(1, 100)


def test_production_still_disabled():
    assert not spec.PRODUCTION_ENABLED


def test_frozen_spec_hashes_intact():
    assert spec.verify_frozen_spec() == spec.FROZEN_HASHES


def test_sr_obligation_count_is_8849():
    sr = [w for w in universe.work_ids() if w[0] == "SR"]
    assert len(sr) == 8849
    assert len({w[1] for w in sr if w[1] >= 0}) == 316


def test_sr_splice_point_unchanged():
    assert spec.SPLICE_EXACT["SR"] == "log(4581762885148045/8796093022208)+1/2"


# --------------------------------------------------------------- DAG completeness
def test_dag_audit_passes():
    a = sr_dag.audit(sr_dag.build())
    assert a["ok"], a["findings"]
    assert a["universe_preserved"]
    assert a["sr_top_level_obligations"] == 8849


def test_dag_covers_every_frozen_obligation_class():
    a = sr_dag.audit(sr_dag.build())
    covered = {tuple(x) for x in a["obligation_classes_covered"]}
    expect = {("object", n) for n in universe.OBJECTS}
    expect |= {("dependency_bundle", "orders_0_1")}
    expect |= {("curvature", str(m)) for m in spec.M_VALUES}
    expect |= {("assembly", str(m)) for m in spec.M_VALUES}
    assert covered == expect


def test_dag_is_acyclic_and_derivative_ordered():
    d = sr_dag.build()
    a = sr_dag.audit(d)
    assert a["topological_order_len"] == a["n_nodes"]
    for nid, n in d["nodes"].items():
        for dep in n["dependencies"]:
            assert d["nodes"][dep]["derivative_order"] <= n["derivative_order"], (nid, dep)


# --------------------------------------------------- exact assembly coefficients
def test_assembly_coefficients_match_frozen_table():
    assert assembly.check_frozen_coefficient_table()


def test_c_m_t_is_one_over_t_minus_one_over_m():
    for m in spec.M_VALUES:
        for kind, r, j, c in assembly.coefficients(m):
            if kind == "F":
                assert c == F(1, m)
            else:
                t = r + j + 1
                assert c == F(1, t) - F(1, m), (m, r, j, c)


def test_m1_specialisation_is_F0_only():
    terms = assembly.coefficients(1)
    assert terms == [("F", 0, 0, F(1, 1))]


def test_m2_matches_the_frozen_gate2c_assembly():
    """R_2 = (F_0 + F_1 + S_0)/2, byte-checked against the Gate-2C artifact."""
    terms = sorted(assembly.coefficients(2))
    assert terms == sorted([("F", 0, 0, F(1, 2)), ("F", 1, 0, F(1, 2)),
                            ("W", 0, 0, F(1, 2))])
    g2c = (ROOT / "level4/closure_proofs/p5y_gate2c_m2_assembly/m2_assembly.py").read_text()
    assert g2c.split("R2e = ")[1].split("\n")[0].strip() == "(F0e + F1e + S0) / arb(2)"


def test_raw_variable_assembly_refuses_a_leading_e():
    with pytest.raises(ValueError):
        assembly.assemble(1, {0: arb(1)}, {}, leading_e=arb(1))


# ------------------------------------------------------- derivative identities
@pytest.mark.parametrize("l,u", [(-3, 2), (-6, 0.49), (1, 4)])
@pytest.mark.parametrize("e", [0, 0.25, -0.3, 2])
def test_rho1_derivatives_match_difference_quotients(l, u, e):
    ctx.prec = 400
    try:
        L, U, E = arb(str(l)), arb(str(u)), arb(str(e))
        h = arb(2) ** -30
        d1 = (SRC.rho1(L, U, E + h) - SRC.rho1(L, U, E - h)) / (arb(2) * h)
        d2 = (SRC.rho1_d1(L, U, E + h) - SRC.rho1_d1(L, U, E - h)) / (arb(2) * h)
        assert abs(float(SRC.rho1_d1(L, U, E).mid()) - float(d1.mid())) < 1e-14
        assert abs(float(SRC.rho1_d2(L, U, E).mid()) - float(d2.mid())) < 1e-14
    finally:
        ctx.prec = 256


def test_rho2_derivative_matches_difference_quotient():
    ctx.prec = 400
    try:
        L, U, E = arb(-3), arb(2), arb(1) / arb(4)
        h = arb(2) ** -30
        d = (SRC.rho2(L, U, E + h) - SRC.rho2(L, U, E - h)) / (arb(2) * h)
        assert abs(float(SRC.rho2_d1(L, U, E).mid()) - float(d.mid())) < 1e-14
    finally:
        ctx.prec = 256


def test_operator_norms_match_known_analytic_constants():
    """Over the near-full line, k1 -> sqrt(2/pi) and k2 -> 4 phi(1)."""
    n = OPS.one_step_norms(arb(0))
    assert abs(float(n["k1"].mid()) - (2 / 3.141592653589793) ** 0.5) < 1e-9
    four_phi1 = 4 * float(SRC.phi(arb(1)).mid())
    assert abs(float(n["k2"].mid()) - four_phi1) < 1e-9


def test_one_step_norm_is_not_contractive_for_SR():
    """The finding that forces an n-step resolvent bound: k0 = 1 - 1.4e-11."""
    n = OPS.one_step_norms(arb(0))
    assert n["k0"] < arb(1)
    assert float((arb(1) - n["k0"]).mid()) < 1e-10


# ------------------------------------------------------ raw-variable source terms
def test_raw_variable_source_terms_are_present():
    """+ e h_1 in F, the bare + h_1 in D, and + 2 h_1' in H.

    These three are absent from the g-variable formulation; dropping any one is
    the most likely silent SR defect.
    """
    src = (CODE / "sr_propagate.py").read_text()
    body = src.split("def resolvent_system")[1]
    assert "s[(r, 0)] + e_abs * h[(1, 0)]" in body, "F_r lost the + e h_1 source"
    assert "+ h[(1, 0)] + e_abs * h[(1, 1)]" in body, "D_r lost the bare + h_1"
    assert "arb(2) * h[(1, 1)] + e_abs * h[(1, 2)]" in body, "H_r lost the + 2 h_1'"


def test_resolvent_system_matches_the_frozen_error_algebra():
    """epsD_r = C(deltaD + k1 epsF + epsS1), epsH_r = C(deltaH + k2 epsF + 2 k1 epsD + epsS2)."""
    body = (CODE / "sr_propagate.py").read_text().split("def resolvent_system")[1]
    assert "k1 * Fr" in body
    assert "k2 * Fr" in body and "arb(2) * k1 * Dr" in body


def test_M_R2_is_the_curvature_bound_not_the_P5X_M2():
    """M_R2 must come from assembly.curvature_bound(order-2 assembly)."""
    body = (CODE / "sr_propagate.py").read_text()
    assert "assembly.curvature_bound(R2_int)" in body
    assert "assemble_order(m, fdh, w, 2)" in body
    forbidden = ("E_e[Rbar^2]", "pair_function", "G_rr")
    code_only = "\n".join(l for l in body.splitlines()
                          if not l.strip().startswith("#"))
    for f in forbidden:
        assert f not in code_only or "NOT" in body


# ---------------------------------------------- historical route exclusion (AST)
def _sr_module_sources():
    return {p.name: p.read_text() for p in CODE.glob("*.py")}


def test_no_banned_symbol_appears_in_the_sr_kernel():
    banned = {s for r in EXCLUDED["routes"] for s in r["banned_symbols"]}
    assert banned, "exclusion list lost its banned symbols"
    for name, src in _sr_module_sources().items():
        tree = ast.parse(src)
        used = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)}
        used |= {n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute)}
        used |= {n.name for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef,))}
        assert not (used & banned), (name, used & banned)


def test_exclusion_list_is_well_formed():
    classes = set(EXCLUDED["classes"])
    ids = [r["id"] for r in EXCLUDED["routes"]]
    assert len(ids) == len(set(ids))
    for r in EXCLUDED["routes"]:
        assert r["class"] in classes
        assert r["evidence"] and r["why_invalid" if "why_invalid" in r else "why_valid"]
        assert r["correct_route"]


def test_degree_ceiling_for_kernel_arguments_is_recorded():
    r = next(x for x in EXCLUDED["routes"] if x["id"] == "degree120_closed_form_into_kernel")
    assert r["max_kernel_argument_degree"] <= 12
    assert r["class"] == "GOVERNANCE_PROHIBITED"


def test_M2_substitution_is_governance_prohibited():
    r = next(x for x in EXCLUDED["routes"] if x["id"] == "M2_substituted_for_M_R2")
    assert r["class"] == "GOVERNANCE_PROHIBITED"


# --------------------------------------------------------- resolvent governance
def test_naive_power_norm_is_rejected():
    n = OPS.one_step_norms(arb(0))
    with pytest.raises(OPS.NaivePowerNormRejected):
        OPS.resolvent_bound({8: n["k0"] ** 8}, k0=n["k0"])


def test_non_contractive_power_norm_is_rejected():
    with pytest.raises(OPS.ResolventNotContractive):
        OPS.resolvent_bound({4: arb(1)})


def test_certified_n_step_bound_is_accepted():
    C = OPS.resolvent_bound({0: arb(1), 1: arb(1), 2: arb(1) / arb(2)})
    assert C > 0


# ------------------------------------------------------------ end-to-end wiring
def test_cell_certificate_produces_all_m_and_M_R2():
    cert = P.cell_certificate(C=arb(600), e_lo=arb(1) / arb(4),
                              e_hi=arb(3) / arb(10), rho=arb(1) / arb(1000), grid=4)
    assert set(cert["per_m"]) == set(spec.M_VALUES)
    for m, d in cert["per_m"].items():
        assert d["M_R2"] >= 0
        assert d["W_cover_exact"] >= 0


def test_cell_certificate_requires_a_certified_C():
    with pytest.raises(P.MissingCertifiedInput):
        P.cell_certificate(C=600, e_lo=arb(0), e_hi=arb(1),
                           rho=arb(1) / arb(1000), grid=2)


# --------------------------------------------------------------- provenance
import sr_cost as CO                                               # noqa: E402
import sr_provenance as PR                                         # noqa: E402


def _full_record():
    return {k: "x" for k in PR.SCIENTIFIC_FIELDS}


def test_no_lazy_imports_on_the_certifying_path():
    assert PR.assert_no_lazy_imports() == []


def test_no_bare_or_broad_except_on_the_certifying_path():
    assert PR.assert_no_bare_except() == []


def test_tcb_is_execution_derived_and_path_based():
    tcb = PR.tcb_from_execution()
    assert tcb
    assert all(p.startswith("/") and p.endswith(".py") for p in tcb)
    assert all(len(h) == 64 for h in tcb.values())
    names = {Path(p).name for p in tcb}
    assert {"sr_propagate.py", "sr_operators.py", "sr_sources.py"} <= names


def test_scientific_hash_covers_every_schema_field():
    rec = _full_record()
    h1 = PR.scientific_hash(rec)
    for k in PR.SCIENTIFIC_FIELDS:
        moved = dict(rec)
        moved[k] = "different"
        assert PR.scientific_hash(moved) != h1, f"{k} escapes the scientific hash"


def test_missing_scientific_field_fails_closed():
    rec = _full_record()
    del rec["M_R2"]
    with pytest.raises(PR.ProducerGateFailure):
        PR.scientific_hash(rec)


def test_final_gate_rejects_empty_tcb():
    with pytest.raises(PR.ProducerGateFailure):
        PR.final_gate(_full_record(), tcb={})


def test_final_gate_rejects_missing_certifying_module():
    tcb = {p: h for p, h in PR.tcb_from_execution().items()
           if Path(p).name != "sr_propagate.py"}
    with pytest.raises(PR.ProducerGateFailure):
        PR.final_gate(_full_record(), tcb=tcb)


def test_final_gate_rejects_stale_producer():
    """A TCB hash that drifts from the pinned manifest must fail closed."""
    tcb = PR.tcb_from_execution()
    pinned = dict(tcb)
    k = next(iter(pinned))
    pinned[k] = "0" * 64
    with pytest.raises(PR.ProducerGateFailure):
        PR.final_gate(_full_record(), tcb=tcb, expected_tcb=pinned)


def test_resume_identity_binds_the_frozen_checkpoint():
    tcb = PR.tcb_from_execution()
    rec = _full_record()
    a = PR.resume_identity(rec, tcb)
    b = dict(rec)
    b["cell_index"] = "different"
    assert PR.resume_identity(b, tcb) != a


def test_cross_cell_and_cross_m_records_hash_differently():
    a = _full_record()
    b, c = dict(a), dict(a)
    b["cell_index"] = "7"
    c["m"] = "5"
    assert len({PR.scientific_hash(a), PR.scientific_hash(b),
                PR.scientific_hash(c)}) == 3


def test_cost_module_makes_no_cap_claim_without_measurements():
    p = CO.campaign_projection([])
    assert p["cap_verdict"] == "NOT_ESTABLISHED"
    assert p["modeled_campaign_cpu_hours"] is None


def test_cost_module_does_not_reuse_historical_extrapolation():
    """The Gate-2F figures may be CITED as excluded, never used as values.

    Checked over numeric literals in the AST, so a docstring naming them as
    non-reusable is fine while an actual constant is not.
    """
    src = (CODE / "sr_cost.py").read_text()
    banned = {1868, 3092, 3697, 4597}
    lits = {n.value for n in ast.walk(ast.parse(src))
            if isinstance(n, ast.Constant) and isinstance(n.value, (int, float))}
    assert not (lits & banned), lits & banned
    assert "NOT_ESTABLISHED" in src
