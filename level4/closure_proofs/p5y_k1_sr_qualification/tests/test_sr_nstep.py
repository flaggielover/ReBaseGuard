"""Lightweight tests for the n-step resolvent, its governance and the SR work universe.

Sub-second and single-threaded: safe to run while the CUSUM campaign holds the
four physical cores. No test performs a representative cell certification.
"""
from __future__ import annotations

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

import spec                                                        # noqa: E402
import universe as frozen_universe                                 # noqa: E402
import sr_nstep as NST                                             # noqa: E402
import sr_operators as OPS                                         # noqa: E402
import sr_propagate as P                                           # noqa: E402
import sr_provenance as PR                                         # noqa: E402
import sr_universe as SU                                           # noqa: E402

SR_CELLS = [c for c in spec.CELLS if c["detector"] == "SR"]


def _arb(f):
    f = F(f)
    return arb(f.numerator) / arb(f.denominator)


# ------------------------------------------------- Lemma 1: positivity identity
def test_positivity_identity_norm_equals_norm_of_one():
    """||K||_inf = ||K 1||_inf. K 1 is the survival mass, so this is exact."""
    for e in (arb(0), arb(1) / arb(4), arb(1)):
        n = OPS.one_step_norms(e)
        L, U = n["w_interval"]
        from sr_sources import Phi
        k1_of_one = Phi(U) - Phi(L)          # (K 1)(y_0), the widest patch
        assert abs(float(n["k0"].mid()) - float(k1_of_one.mid())) < 1e-30


def test_survival_interpretation_is_a_probability():
    """(K^n 1) must lie in [0,1]: it is P_y(tau > n)."""
    for e in (arb(0), arb(1)):
        k0 = OPS.one_step_norms(e)["k0"]
        assert k0 >= 0 and k0 <= arb(1)


# ------------------------------------------------ Theorem: geometric decomposition
def test_finite_geometric_identity_scalar_case():
    """P_n (1-k) = 1 - k^n, the scalar shadow of P_n (I-K) = I - K^n."""
    for k in (F(1, 3), F(9, 10), F(1, 2)):
        for n in (1, 2, 5, 8):
            Pn = sum(k ** j for j in range(n))
            assert Pn * (1 - k) == 1 - k ** n


def test_nstep_bound_dominates_the_true_scalar_resolvent():
    for k in (F(1, 3), F(9, 10)):
        for n in (2, 4, 8):
            Pn = sum(k ** j for j in range(n))
            assert Pn / (1 - k ** n) >= 1 / (1 - k)


def test_one_step_bound_is_the_n_equals_one_special_case():
    k = F(9, 10)
    assert sum(k ** j for j in range(1)) / (1 - k ** 1) == 1 / (1 - k)


# -------------------------------------------------------- one-step fallback ban
def test_naive_one_step_constant_refuses_by_default():
    with pytest.raises(NST.OneStepFallbackRefused):
        NST.naive_one_step_constant(arb(0))


def test_naive_one_step_constant_available_only_for_diagnostics():
    v = NST.naive_one_step_constant(arb(0), diagnostics_only=True)
    assert float(v.mid()) > 1e9          # the useless 7.03e10


def _executable_source(path: Path) -> str:
    """Module source with every docstring removed, so prose that CITES a banned
    construction is not mistaken for using it."""
    import ast as _ast
    tree = _ast.parse(path.read_text())
    for node in _ast.walk(tree):
        if isinstance(node, (_ast.Module, _ast.FunctionDef, _ast.AsyncFunctionDef,
                             _ast.ClassDef)) and _ast.get_docstring(node) is not None:
            node.body = node.body[1:] or [_ast.Pass()]
    return _ast.unparse(tree)


def test_no_module_silently_uses_one_over_one_minus_k0():
    """No certifying module may compute 1/(1-k0) outside the guarded helper.

    Checked over executable code only: the useless one-step constant is named in
    several docstrings precisely because it is forbidden.
    """
    for p in sorted(CODE.glob("*.py")):
        if p.name == "sr_nstep.py":
            continue                      # the guarded diagnostics helper lives here
        body = _executable_source(p).replace(" ", "")
        assert "arb(1)/(arb(1)-" not in body, p.name
        assert "1/(1-k0)" not in body, p.name


def test_the_guarded_helper_is_the_only_place_the_one_step_constant_is_built():
    body = _executable_source(CODE / "sr_nstep.py")
    assert "def naive_one_step_constant" in body
    assert "OneStepFallbackRefused" in body


# --------------------------------------------------------- ResolventCertificate
def test_propagation_refuses_a_bare_number_resolvent():
    with pytest.raises(P.UncertifiedResolvent):
        P.cell_certificate(resolvent=arb(127), e_lo=arb(0), e_hi=arb(1),
                           rho=_arb(F(1, 1000)), cell_e=(F(0), F(1)))


def test_propagation_refuses_none_resolvent():
    with pytest.raises(P.UncertifiedResolvent):
        P.cell_certificate(resolvent=None, e_lo=arb(0), e_hi=arb(1),
                           rho=_arb(F(1, 1000)), cell_e=(F(0), F(1)))


def test_propagation_requires_exact_cell_endpoints():
    c = NST.ResolventCertificate.from_frozen_cell(SR_CELLS[292])
    with pytest.raises(P.MissingCertifiedInput):
        P.cell_certificate(resolvent=c, e_lo=arb(2), e_hi=arb(3),
                           rho=_arb(F(1, 1000)))


def test_certificate_refuses_a_cell_it_does_not_cover():
    c = NST.ResolventCertificate.from_frozen_cell(SR_CELLS[292])
    lo, hi = F(SR_CELLS[0]["left"][0]), F(SR_CELLS[0]["right"][0])
    with pytest.raises(NST.CellMismatch):
        P.cell_certificate(resolvent=c, e_lo=_arb(lo), e_hi=_arb(hi),
                           rho=_arb(F(1, 1000)), cell_e=(lo, hi))


def test_certificate_covers_its_own_cell_exactly():
    for i in (0, 100, 292, 315):
        c = NST.ResolventCertificate.from_frozen_cell(SR_CELLS[i])
        lo, hi = F(SR_CELLS[i]["left"][0]), F(SR_CELLS[i]["right"][0])
        assert c.covers(lo, hi), i


# --------------------------------------------- C is frozen cover geometry
def test_C_comes_from_the_frozen_cell_C_upper():
    for i in (0, 150, 313):
        c = NST.ResolventCertificate.from_frozen_cell(SR_CELLS[i])
        assert F(c.C_n) == F(SR_CELLS[i]["C_upper"])
        assert c.method == "frozen-cover-geometry-C_upper"


def test_cusum_reads_C_upper_the_same_way():
    """The rule SR follows is the validated CUSUM one, not an SR invention."""
    src = (IMPL / "cusum_layer2.py").read_text()
    assert 'self.C = F(cell["C_upper"])' in src


def test_C_upper_is_per_cell_and_varies_by_orders_of_magnitude():
    vals = [F(c["C_upper"]) for c in SR_CELLS]
    assert len(set(vals)) > 300
    assert max(vals) / min(vals) > 500


def test_rho_times_C_upper_is_invariant_across_the_cover():
    """The geometry balances rho against C_upper; a fixed rho would mislead."""
    prods = [float(F(c["rho"][0]).__abs__() * F(c["C_upper"]))
             for c in SR_CELLS[:314]]
    assert max(prods) / min(prods) < 1.05


def test_corroboration_is_one_sided_and_cannot_falsify_frozen():
    frozen = NST.ResolventCertificate.from_frozen_cell(SR_CELLS[292])
    loose = NST.ResolventCertificate(
        n=6, q_n="0.5", finite_sum_bound="6", C_n="1000",
        e_lo=frozen.e_lo, e_hi=frozen.e_hi, domain="[0,b_SR]^2",
        method="interval-DP-upper-envelope", partition=8, z_panels=8, bits=256)
    r = frozen.corroborate(loose)
    assert r["status"] == "INCONCLUSIVE"
    assert r["can_falsify_frozen"] is False
    tight = NST.ResolventCertificate(**{**loose.to_json(), "C_n": "1"})
    assert frozen.corroborate(tight)["status"] == "CORROBORATED"


# ------------------------------------------------------------ SR work universe
def test_sr_universe_audit_passes():
    a = SU.audit()
    assert a["ok"], a["findings"]
    assert a["n_sr_obligations"] == 8849
    assert a["n_cells"] == 316
    assert a["obligations_per_cell"] == 28
    assert a["far_field_units"] == 1
    assert a["total_universe"] == 17978


def test_sr_work_ids_are_unique_and_deterministic():
    ids = SU.work_ids()
    strs = [SU.work_id_str(w) for w in ids]
    assert len(set(strs)) == len(strs) == 8849
    assert SU.work_ids() == ids           # deterministic


@pytest.mark.parametrize("n_shards", [1, 2, 4, 7, 64, 317, 8849])
def test_shards_partition_the_sr_universe_exactly(n_shards):
    c = SU.shard_conservation(n_shards)
    assert c["exact_partition"] and c["no_overlap"]
    assert c["covered"] == 8849


def test_shard_rejects_out_of_range_index():
    with pytest.raises(ValueError):
        SU.shard(4, 4)


# ------------------------------------------------------------ resume admission
def _rec():
    return {k: "x" for k in PR.SCIENTIFIC_FIELDS}


def test_resume_identity_separates_cells_and_m():
    ids = SU.work_ids()
    tcb = PR.tcb_from_execution()
    a = SU.resume_identity(ids[0], _rec(), tcb)
    b = SU.resume_identity(ids[1], _rec(), tcb)
    assert a != b


def test_resume_rejects_superseded_universe():
    ids = SU.work_ids()
    tcb = PR.tcb_from_execution()
    ident = SU.resume_identity(ids[0], _rec(), tcb)
    for bad in sorted(frozen_universe.SUPERSEDED_UNIVERSES):
        with pytest.raises(SU.InadmissibleRecord):
            SU.admit(ids[0], _rec(), tcb, claimed_identity=ident,
                     claimed_universe_size=bad)


def test_resume_rejects_superseded_checkpoint_hash():
    ids = SU.work_ids()
    tcb = PR.tcb_from_execution()
    rec = _rec()
    rec["checkpoint_sha256"] = sorted(frozen_universe.SUPERSEDED_CHECKPOINT_HASHES)[0]
    ident = SU.resume_identity(ids[0], rec, tcb)
    with pytest.raises(SU.InadmissibleRecord):
        SU.admit(ids[0], rec, tcb, claimed_identity=ident,
                 claimed_universe_size=spec.TOTAL_UNITS)


def test_resume_rejects_stale_producer_identity():
    ids = SU.work_ids()
    tcb = PR.tcb_from_execution()
    with pytest.raises(SU.InadmissibleRecord):
        SU.admit(ids[0], _rec(), tcb, claimed_identity="0" * 64,
                 claimed_universe_size=spec.TOTAL_UNITS)


def test_resume_accepts_a_matching_record():
    ids = SU.work_ids()
    tcb = PR.tcb_from_execution()
    ident = SU.resume_identity(ids[0], _rec(), tcb)
    assert SU.admit(ids[0], _rec(), tcb, claimed_identity=ident,
                    claimed_universe_size=spec.TOTAL_UNITS)


# --------------------------------------------------- frozen scope still intact
def test_universe_and_scope_unchanged_by_this_lane():
    assert len(frozen_universe.work_ids()) == spec.TOTAL_UNITS == 17978
    assert spec.COUNTS == {"CUSUM": 326, "SR": 316}
    assert spec.M_VALUES == (1, 2, 3, 5)
    assert spec.HARD_CAP_CPU_H == 1126
    assert not spec.PRODUCTION_ENABLED
    assert spec.verify_frozen_spec() == spec.FROZEN_HASHES
