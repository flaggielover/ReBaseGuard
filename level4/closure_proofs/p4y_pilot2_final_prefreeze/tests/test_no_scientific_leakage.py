"""Brief section 14: scientific outcome fields must be unreachable.

An allocation decision may read route-local precision and frozen constants.
It may not read the correspondence discrepancy, its sign, z, theorem
agreement, the Route-Q value, the Gaussian consistency result, whether a cell
historically failed, or any desired verdict.

Enforcement here is structural rather than advisory: the rule's only input is
a callable returning a float, so there is no parameter, attribute or closure
through which those quantities could arrive.  These tests hold that shut.
"""

import inspect

import pytest

from p4y_pilot2 import rule as R
from p4y_pilot2.audit import audit


def test_the_rules_entire_input_surface_is_precision_only():
    params = set(inspect.signature(R.trace).parameters)
    assert params == {"measure", "b1", "target", "kappa", "max_cap"}
    assert set(inspect.signature(R.next_allocation).parameters) == {
        "current", "target", "kappa"}
    assert R.Precision.__slots__ == R.PRECISION_FIELDS


def test_precision_carries_nothing_but_blocks_and_relative_se():
    p = R.Precision(48, 0.02)
    assert set(R.Precision.__slots__) == {"blocks", "relative_se"}
    for banned in R.FORBIDDEN_FIELDS:
        assert not hasattr(p, banned)
    with pytest.raises((AttributeError, TypeError)):
        p.discrepancy = 0.5          # frozen dataclass with slots


def test_a_measure_returning_a_rich_object_cannot_smuggle_fields_in():
    """The rule compares the measurement to a float target; anything that is
    not a plain number fails loudly rather than being partly consumed."""

    class Poisoned(float):
        discrepancy = 0.021
        z = 3.4
        passed = True

    seen = []

    def measure(blocks):
        seen.append(blocks)
        return Poisoned(0.005)

    traj = R.trace(measure=measure, b1=48, target=0.01, kappa=0.5,
                   max_cap=1000)
    o = R.terminate(traj, 576)
    # the rule used the numeric value and nothing else
    assert o.status == R.ATTAINED
    assert seen == [48]
    assert not any(hasattr(s, "discrepancy") and s.next_blocks
                   for s in traj.stages if not isinstance(s.relative_se, float))


def test_next_allocation_is_a_pure_function_of_the_two_numbers():
    a = R.next_allocation(R.Precision(100, 0.05), 0.01, 0.5)
    b = R.next_allocation(R.Precision(100, 0.05), 0.01, 0.5)
    assert a == b
    src = inspect.getsource(R.next_allocation)
    for banned in ("discrepancy", "z_", "sign", "gate", "verdict", "passed"):
        assert banned not in src


def test_the_auditor_rejects_a_run_that_saw_a_forbidden_field():
    traj = R.trace(measure=lambda b: 0.005, b1=48, target=0.01, kappa=0.5,
                   max_cap=1000)
    o = R.terminate(traj, 576)
    clean = audit(o, traj, cap_blocks=576)
    assert clean.valid
    dirty = audit(o, traj, cap_blocks=576,
                  measure_inputs_seen=("blocks", "relative_discrepancy"))
    assert not dirty.valid
    assert any("scientific outcome fields" in r for r in dirty.reasons)


@pytest.mark.parametrize("field", R.FORBIDDEN_FIELDS)
def test_every_named_forbidden_field_is_rejected_by_the_auditor(field):
    traj = R.trace(measure=lambda b: 0.005, b1=48, target=0.01, kappa=0.5,
                   max_cap=1000)
    o = R.terminate(traj, 576)
    assert not audit(o, traj, cap_blocks=576,
                     measure_inputs_seen=(field,)).valid


def test_the_runner_never_passes_a_scientific_field_to_the_rule():
    from pathlib import Path

    src = (Path(__file__).resolve().parents[1] / "run_phase.py").read_text()
    body = src[src.index("def replicate("):src.index("def run_phase(")]
    for banned in ("discrepancy", "gate", "verdict", "z=", "pass_fail",
                   "correspondence", "route_q"):
        assert banned not in body, f"{banned!r} appears in the replicate body"
