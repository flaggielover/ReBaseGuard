"""Lightweight tests for SR refinement, the patch architecture and the M_R2 lock.

Sub-second and single-threaded: safe while the CUSUM campaign holds the cores.
"""
from __future__ import annotations

import ast
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
import universe as frozen_universe                                 # noqa: E402
import sr_operators as OPS                                         # noqa: E402
import sr_patch as SP                                              # noqa: E402
import sr_provenance as PR                                         # noqa: E402
import sr_refine as RF                                             # noqa: E402
import sr_universe as SU                                           # noqa: E402
import sr_width as SW                                              # noqa: E402

SR_COMPACT = [c for c in spec.CELLS
              if c["detector"] == "SR" and F(c["e0"][1]) == 0]


def _A(f):
    f = F(f)
    return arb(f.numerator) / arb(f.denominator)


def _inputs(cell, **over):
    e0 = F(cell["e0"][0])
    rho = abs(F(cell["rho"][0]))
    C = _A(F(cell["C_upper"]))
    n = OPS.one_step_norms(_A(e0))
    base = dict(rho=_A(rho), C=C, k1=n["k1"], k2=n["k2"], e_abs=_A(e0),
                eps_F_mid=arb(10) ** -20, eps_D_mid=arb(10) ** -20,
                eps_F_crude=C, eps_D_crude=C * C, eps_H_crude=C * C * C,
                delta_H_cell=arb(10) ** -20, eps_S2_cell=arb(10) ** -20,
                sup_D_hat=arb(1), sup_H_hat=arb(1),
                eps_h1_d1=arb(10) ** -20, eps_h1_d2=arb(10) ** -20)
    base.update(over)
    return RF.RefinementInputs(**base)


# ------------------------------------------------------------ contraction
def test_refinement_contracts_on_every_compact_sr_cell():
    """kappa' = C rho (2 k1 + k2 rho/2) < 1 on all 315 compact cells."""
    worst = 0.0
    for cell in SR_COMPACT:
        k = float(_inputs(cell).contraction().abs_upper().mid())
        worst = max(worst, k)
        assert k < 1.0, cell["index"]
    assert worst < 0.52, worst


def test_contraction_is_capped_at_one_half_by_the_frozen_step_rule():
    """rho*C_upper*2*k1 <= 1/2 because a_upper = k1 = sqrt(2/pi)."""
    for cell in SR_COMPACT[::40]:
        rho = abs(F(cell["rho"][0]))
        C = F(cell["C_upper"])
        k1 = float(OPS.one_step_norms(_A(F(cell["e0"][0])))["k1"].mid())
        assert float(rho * C) * 2 * k1 <= 0.5000001


def test_rho_times_C_upper_invariant_holds_on_compact_cells():
    prods = [float(abs(F(c["rho"][0])) * F(c["C_upper"])) for c in SR_COMPACT]
    assert max(prods) / min(prods) < 1.0002


# --------------------------------------------------- disabled == crude exactly
def test_disabled_refinement_reproduces_crude_bounds_exactly():
    cell = SR_COMPACT[150]
    inp = _inputs(cell)
    off = RF.refine_cell(inp, enabled=False)
    assert off.eps_F_cell.mid() == inp.eps_F_crude.mid()
    assert off.eps_D_cell.mid() == inp.eps_D_crude.mid()
    assert off.eps_H_cell.mid() == inp.eps_H_crude.mid()
    assert off.refinement_enabled is False
    assert off.tightening_factor_H == 1.0


def test_refinement_never_loosens():
    for cell in SR_COMPACT[::60]:
        inp = _inputs(cell)
        r = RF.refine_cell(inp)
        assert r.eps_F_cell.upper() <= inp.eps_F_crude.upper()
        assert r.eps_D_cell.upper() <= inp.eps_D_crude.upper()
        assert r.eps_H_cell.upper() <= inp.eps_H_crude.upper()


def test_refinement_reaches_the_same_fixed_point_from_different_seeds():
    """Seed-independence, to within the relative stopping tolerance.

    The iteration contracts to a seed-independent fixed point, so a 10x looser
    crude seed must NOT give a materially different refined bound -- it only
    costs more sweeps. Exact monotonicity in the seed does not hold and is not
    claimed: the stop rule is relative (1 part in 1e6), so the two runs halt at
    slightly different points on the same geometric sequence. Both remain valid
    bounds, which is what the next assertion checks.
    """
    cell = SR_COMPACT[150]
    C = _A(F(cell["C_upper"]))
    a = RF.refine_cell(_inputs(cell, eps_H_crude=C * C * C))
    b = RF.refine_cell(_inputs(cell, eps_H_crude=C * C * C * arb(10)))
    fa = float(a.eps_H_cell.abs_upper().mid())
    fb = float(b.eps_H_cell.abs_upper().mid())
    assert abs(fa - fb) / max(fa, fb) < 1e-5
    # each is a valid bound for its own seed
    assert a.eps_H_cell.upper() <= (C * C * C).upper()
    assert b.eps_H_cell.upper() <= (C * C * C * arb(10)).upper()
    assert b.iterations >= a.iterations


def test_refinement_terminates():
    r = RF.refine_cell(_inputs(SR_COMPACT[0]))
    assert 0 < r.iterations <= RF.MAX_ITERATIONS


# -------------------------------------------- SR raw-variable terms mandatory
def test_missing_raw_variable_terms_are_refused():
    cell = SR_COMPACT[150]
    e0 = F(cell["e0"][0])
    n = OPS.one_step_norms(_A(e0))
    common = dict(rho=_A(abs(F(cell["rho"][0]))), C=_A(F(cell["C_upper"])),
                  k1=n["k1"], k2=n["k2"], e_abs=_A(e0),
                  eps_F_mid=arb(0), eps_D_mid=arb(0), eps_F_crude=arb(1),
                  eps_D_crude=arb(1), eps_H_crude=arb(1),
                  delta_H_cell=arb(0), eps_S2_cell=arb(0),
                  sup_D_hat=arb(1), sup_H_hat=arb(1))
    with pytest.raises(RF.MissingRawVariableTerm):
        RF.RefinementInputs(**common)
    with pytest.raises(RF.MissingRawVariableTerm):
        RF.RefinementInputs(**common, eps_h1_d1=arb(0))


def test_raw_variable_terms_actually_enter_the_iteration():
    cell = SR_COMPACT[150]
    small = RF.refine_cell(_inputs(cell))
    large = RF.refine_cell(_inputs(cell, eps_h1_d1=arb(1), eps_h1_d2=arb(1)))
    assert large.eps_H_cell.upper() > small.eps_H_cell.upper()


def test_sr_closure_equation_has_the_extra_raw_terms():
    body = (CODE / "sr_refine.py").read_text().split("def refine_cell")[1]
    assert "arb(2) * inp.eps_h1_d1 + inp.e_abs * inp.eps_h1_d2" in body


# ------------------------------------------------------------ order-3 algebra
def test_order3_binomial_coefficients_and_raw_term():
    """(I-K)F''' = 3K'F'' + 3K''F' + K'''F + S''' + 3h_1'' + e h_1'''."""
    from math import comb
    assert [comb(3, k) for k in range(4)] == [1, 3, 3, 1]
    doc = (NS / "SR_MIDPOINT_REFINEMENT.md").read_text()
    assert "3 K' F_r'' + 3 K'' F_r' + K''' F_r" in doc
    assert "3 h_1''" in doc
    assert "w^3 - 3w" in doc          # He_3


def test_hermite_identity_for_the_third_operator_derivative():
    """He_3(w) = w^3 - 3w, and d^3/de^3 phi = -He_3 phi."""
    import sr_sources as SRC
    h = arb(2) ** -20
    for w0 in (arb(0), arb(1), arb("-1.5")):
        d3 = ((SRC.phi(w0 + arb(2) * h) - arb(2) * SRC.phi(w0 + h)
               + arb(2) * SRC.phi(w0 - h) - SRC.phi(w0 - arb(2) * h))
              / (arb(2) * h ** 3))
        he3 = -(w0 ** 3 - arb(3) * w0) * SRC.phi(w0)
        assert abs(float(d3.mid()) - float(he3.mid())) < 1e-6


# ------------------------------------------------------------ width attribution
def test_width_attribution_is_exact():
    d = SW.cover_decomposition(SR_COMPACT[150], m=2, grid=4)
    total = sum(float(v.abs_upper().mid()) for _o, _p, v, _f in d["ranked"])
    assert abs(total / float(d["W_cover"].abs_upper().mid()) - 1.0) < 1e-12


def test_linear_term_dominates_curvature_on_small_rho_cells():
    """Confirms the claim, and records that it is NOT universal."""
    small = SW.cover_decomposition(SR_COMPACT[150], m=2, grid=4)
    assert float(small["linear_over_curvature"].mid()) > 3.5
    large = SW.cover_decomposition(SR_COMPACT[313], m=2, grid=4)
    assert float(large["linear_over_curvature"].mid()) < 2.0


def test_uninstrumented_width_sources_are_declared():
    assert len(SW.NOT_INSTRUMENTED) >= 4
    assert any("candidate" in s for s in SW.NOT_INSTRUMENTED)


# ------------------------------------------------------------ patch architecture
def test_live_patch_census_matches_the_frozen_gate2b_cover():
    c = SP.patch_census()
    assert c["nominal"] == 4096 and c["live"] == 3994 and c["dead"] == 102
    assert c["grid"] == 64
    assert c["reset_patch"] == "SRpatch:64:0:0"
    assert c["total_panels"] == 83452


def test_patch_identity_is_deterministic():
    a = SP.patch(17, 11)
    b = SP.patch(17, 11)
    assert a == b and a.sha256() == b.sha256()
    assert a.patch_id == "SRpatch:64:17:11"
    assert SP.patch(17, 11).sha256() != SP.patch(18, 11).sha256()


def test_task1r_patch_is_live():
    assert SP.patch(17, 11).contains_x0 is False


def test_dead_patch_is_refused():
    live = {(p.i, p.j) for p in SP.live_patches()}
    dead = next((i, j) for i in range(64) for j in range(64)
                if (i, j) not in live)
    with pytest.raises(SP.DeadPatch):
        SP.patch(*dead)


def test_patch_work_items_map_to_frozen_parent_obligations():
    items = SP.patch_items_for_cell(150, "F_0")
    assert len(items) == 3994
    assert len({i.work_item_id for i in items}) == 3994
    parents = {i.parent_obligation() for i in items}
    assert parents == {("SR", 150, "object", "F_0")}
    assert ("SR", 150, "object", "F_0") in set(frozen_universe.work_ids())


def test_patch_class_must_be_a_frozen_object():
    with pytest.raises(ValueError):
        SP.patch_items_for_cell(150, "not_an_object")


def test_patch_evidence_adds_no_top_level_obligations():
    a = SU.audit()
    assert a["n_sr_obligations"] == 8849
    assert a["total_universe"] == 17978
    c = SP.nested_evidence_census()
    assert c["top_level_sr_obligations"] == 8849
    assert c["top_level_universe"] == 17978


def test_shard_conservation_survives_the_new_architecture():
    for n in (1, 4, 64, 317):
        s = SU.shard_conservation(n)
        assert s["exact_partition"] and s["no_overlap"] and s["covered"] == 8849


# ------------------------------------------------- candidate determinism contract
def test_candidate_identity_is_deterministic_and_discriminating():
    p = SP.patch(17, 11)
    item = SP.PatchWorkItem(150, p, "F_0", 0, None)
    spec_ = SP.CandidateSpec()
    rb = {"flint": "0.9.0", "threads": "1", "bits": 256}
    a = SP.candidate_identity(item=item, spec_=spec_, producer_hash="p", runtime_binding=rb)
    b = SP.candidate_identity(item=item, spec_=spec_, producer_hash="p", runtime_binding=rb)
    assert a == b
    other_patch = SP.PatchWorkItem(150, SP.patch(18, 11), "F_0", 0, None)
    other_cell = SP.PatchWorkItem(151, p, "F_0", 0, None)
    other_rt = dict(rb, flint="0.9.1")
    for v in (SP.candidate_identity(item=other_patch, spec_=spec_, producer_hash="p", runtime_binding=rb),
              SP.candidate_identity(item=other_cell, spec_=spec_, producer_hash="p", runtime_binding=rb),
              SP.candidate_identity(item=item, spec_=spec_, producer_hash="q", runtime_binding=rb),
              SP.candidate_identity(item=item, spec_=spec_, producer_hash="p", runtime_binding=other_rt),
              SP.candidate_identity(item=item, spec_=SP.CandidateSpec(bits=384),
                                    producer_hash="p", runtime_binding=rb)):
        assert v != a


def test_kernel_argument_degree_ceiling_is_enforced():
    SP.assert_kernel_argument_degree(12)
    for d in (13, 120, 121):
        with pytest.raises(SP.KernelArgumentDegreeExceeded):
            SP.assert_kernel_argument_degree(d)


def test_candidate_solves_are_deferred_not_stubbed():
    """A solve must raise, never return a placeholder that could be certified."""
    item = SP.PatchWorkItem(150, SP.patch(17, 11), "F_0", 0, None)
    s = SP.CandidateSpec()
    for fn in (SP.build_candidate, SP.derivative_candidate, SP.curvature_candidate):
        with pytest.raises(SP.CandidateSolveDeferred):
            fn(item, s)
    with pytest.raises(SP.CandidateSolveDeferred):
        SP.finite_power_candidate(item, 1, s)


# --------------------------------------------------------- M_R2 semantics lock
def test_M_R2_semantics_lock_holds():
    assert PR.assert_M_R2_semantics()
    assert "M_R2" in PR.SCIENTIFIC_FIELDS


@pytest.mark.parametrize("bad", PR.FORBIDDEN_FIELD_NAMES)
def test_P5X_M2_may_not_appear_in_a_K1_record(bad):
    rec = {k: "x" for k in PR.SCIENTIFIC_FIELDS}
    rec[bad] = "leak"
    with pytest.raises(PR.M_R2SemanticsViolation):
        PR.assert_M_R2_semantics(rec)


def test_final_gate_rejects_an_M2_leak():
    rec = {k: "x" for k in PR.SCIENTIFIC_FIELDS}
    rec["M_2"] = "leak"
    with pytest.raises(PR.M_R2SemanticsViolation):
        PR.final_gate(rec, tcb=PR.tcb_from_execution())


def test_no_module_names_a_variable_after_the_P5X_scalar():
    for p in sorted(CODE.glob("*.py")):
        if p.name == "sr_provenance.py":
            continue                    # defines the forbidden-name list itself
        tree = ast.parse(p.read_text())
        names = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)}
        names |= {t.attr for t in ast.walk(tree) if isinstance(t, ast.Attribute)}
        assert not (names & set(PR.FORBIDDEN_FIELD_NAMES)), p.name


def test_M_R2_is_still_the_curvature_bound():
    src = (CODE / "sr_propagate.py").read_text()
    assert "assembly.curvature_bound(R2_int)" in src


# --------------------------------------------------------------- cost model
def test_cost_categories_cover_the_new_architecture():
    import sr_cost as CO
    for c in ("candidate", "midpoint", "refinement", "order3", "assembly"):
        assert c in CO.COST_CATEGORIES
    f = CO.cost_formulas()
    assert "NOT" not in f["cap_rule"].upper() or "adjudicated ONCE" in f["cap_rule"]
    assert CO.campaign_projection([])["cap_verdict"] == "NOT_ESTABLISHED"


# ----------------------------------------------------------- frozen scope
def test_frozen_scope_unchanged():
    assert len(frozen_universe.work_ids()) == spec.TOTAL_UNITS == 17978
    assert spec.COUNTS == {"CUSUM": 326, "SR": 316}
    assert spec.M_VALUES == (1, 2, 3, 5)
    assert spec.HARD_CAP_CPU_H == 1126
    assert not spec.PRODUCTION_ENABLED
    assert spec.verify_frozen_spec() == spec.FROZEN_HASHES
    assert assembly.check_frozen_coefficient_table()
