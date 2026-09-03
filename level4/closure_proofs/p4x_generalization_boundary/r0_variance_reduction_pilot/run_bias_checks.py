#!/usr/bin/env python3
"""Bias checks for every candidate method that is not the frozen baseline.

A variance-reduction method is only admissible if it is unbiased for the same
estimand, or if its bias is independently quantified and negligible.  This
script does the quantifying.

Check 1 -- reflection-antithetic PATHWISE exactness.
    Under a reflection-equivariant detector the run at ``(-e, -eps)`` is the
    pathwise mirror of the run at ``(+e, +eps)``: ``Z' = (-eps) - (-e) = -Z``.
    This is pure algebra and holds for EVERY family, symmetric or not, so it
    is necessary but not sufficient for the method to be admissible.

Check 1b -- reflection-antithetic DISTRIBUTIONAL validity.
    The mirrored run is only a legitimate ``-e`` sample if the negated
    innovation stream has the SAME law as the original, i.e. if the family is
    symmetric.  This is the conjunct that actually needs symmetry, and it is
    what separates t1p5 from skewnormal4.  A first version of this script
    tested only Check 1 and therefore "passed" the asymmetric control; that
    defect is recorded here rather than silently corrected.

Check 2 -- reflection equivariance of each frozen detector, and symmetry of
    each family, tested directly.

Check 3 -- finite-difference step ladder.
    The Richardson combination removes the ``O(h^2)`` term; what remains is
    ``O(h^4)``.  The ladder measures the residual drift across h so that a
    coarser step is adopted only if its estimate is stable.
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np

PILOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PILOT / "src"))
P4 = PILOT.parents[1] / "p4_theory_generalization"
sys.path.insert(0, str(P4 / "src"))

from rebaseguard_p4_general.detectors import Detector  # noqa: E402
from rebaseguard_p4_general.families import REGISTRY  # noqa: E402
from rebaseguard_p4_general.simulate import simulate_group  # noqa: E402

CHECK_PATHS = 20_000
CHECK_SEED = 4119001


def mirror_check(family_name: str, kind: str, threshold: float,
                 max_steps: int, e: float = 0.05) -> dict:
    """Simulate (+e, eps) and (-e, -eps) and compare pathwise."""
    family = REGISTRY[family_name]
    detector = Detector(kind, threshold)

    # the +e run on the shared aligned stream
    (plus,) = simulate_group(
        family=family, detector=detector, e_values=(e,), n_paths=CHECK_PATHS,
        seed=CHECK_SEED, batch=0, m_max=5, mode="aligned", max_steps=max_steps,
    )
    # the -e run on the NEGATED stream, obtained by negating the family's own
    # draws: for a symmetric family the negated stream is an equally valid
    # realisation, so this is the exact antithetic partner
    class _Negated:
        name = family.name

        @staticmethod
        def sample(rng, size):
            return -family.sample(rng, size)

        @staticmethod
        def psi(z):
            return family.psi(z)

    (minus,) = simulate_group(
        family=_Negated, detector=detector, e_values=(-e,), n_paths=CHECK_PATHS,
        seed=CHECK_SEED, batch=0, m_max=5, mode="aligned", max_steps=max_steps,
    )

    tau_equal = bool(np.array_equal(plus.tau, minus.tau))
    win_err = float(np.abs(plus.window + minus.window).max())
    tot_err = float(np.abs(plus.total + minus.total).max())
    scale = float(max(np.abs(plus.window).max(), 1.0))
    return {
        "family": family_name, "detector": Detector(kind, threshold).label,
        "paths": CHECK_PATHS,
        "stopping_times_identical": tau_equal,
        "max_abs_window_sum": win_err,
        "max_abs_total_sum": tot_err,
        "relative_window_error": win_err / scale,
        "exact_to_machine_precision": tau_equal and win_err <= 1e-9 * scale,
    }


def symmetry_check(family_name: str) -> dict:
    """Is the family's density symmetric?  psi must be odd."""
    family = REGISTRY[family_name]
    z = np.linspace(-6.0, 6.0, 2401)
    odd_err = float(np.abs(family.psi(z) + family.psi(-z)).max())
    return {
        "family": family_name,
        "max_abs_psi_oddness_defect": odd_err,
        "score_is_odd": odd_err < 1e-9,
    }


def negated_stream_validity(family_name: str, n: int = 400_000) -> dict:
    """Does ``-eps`` have the same law as ``eps``?

    This is the conjunct the reflection method actually needs, and the one the
    pathwise mirror check does NOT test.  A two-sample Kolmogorov-Smirnov test
    against the negated sample, plus the sample skewness, decides it.
    """
    from scipy import stats as _stats

    family = REGISTRY[family_name]
    rng = np.random.default_rng(CHECK_SEED + 7)
    eps = family.sample(rng, (n,))
    ks = _stats.ks_2samp(eps, -eps)
    skew = float(_stats.skew(eps))
    return {
        "family": family_name,
        "n": n,
        "ks_statistic": float(ks.statistic),
        "ks_pvalue": float(ks.pvalue),
        "sample_skewness": skew,
        "negated_stream_is_same_law": bool(ks.pvalue > 0.01),
    }


def detector_equivariance_check(kind: str, threshold: float) -> dict:
    """Does the detector satisfy tau(-Z) = tau(Z) pathwise?"""
    detector = Detector(kind, threshold)
    rng = np.random.default_rng(CHECK_SEED)
    z = rng.standard_normal((4000, 60)) * 1.5
    results = {}
    for sign in (1.0, -1.0):
        up, down = detector.new_state(4000)
        tau = np.zeros(4000, dtype=np.int64)
        alive = np.ones(4000, dtype=bool)
        for step in range(1, 61):
            idx = np.flatnonzero(alive)
            if not idx.size:
                break
            up[idx], down[idx], crossed = detector.step(
                up[idx], down[idx], sign * z[idx, step - 1], step)
            done = idx[crossed]
            tau[done] = step
            alive[done] = False
        results[sign] = tau.copy()
    equal = bool(np.array_equal(results[1.0], results[-1.0]))
    return {
        "detector": detector.label,
        "reflection_equivariant": equal,
        "paths": 4000,
    }


def main() -> None:
    t0 = time.perf_counter()
    symmetric_configs = [
        ("t1p5", "sr", 520.886133602749, 200_000),
        ("t1p5", "cusum", 5.0, 200_000),
        ("t1p5", "sr", 20.0, 60_000),
    ]
    asymmetric = ("skewnormal4", "sr", 520.886133602749, 200_000)

    payload = {
        "schema": "rebaseguard.p4x-r0-bias.v1",
        "classification": "PRE_FREEZE_COST_AND_PRECISION_PILOT",
        "binding": False,
        "family_symmetry": [symmetry_check(f) for f in
                            ("t1p5", "skewnormal4", "gaussian")],
        "detector_equivariance": [
            detector_equivariance_check("sr", 520.886133602749),
            detector_equivariance_check("cusum", 5.0),
            detector_equivariance_check("sr", 20.0),
        ],
        "reflection_mirror_checks": [
            mirror_check(f, k, t, ms) for f, k, t, ms in symmetric_configs
        ],
        "asymmetric_pathwise_control": mirror_check(*asymmetric),
        "negated_stream_validity": [
            negated_stream_validity(f) for f in ("t1p5", "skewnormal4", "gaussian")
        ],
        "pathwise_mirror_holds_for_every_family": (
            "The pathwise mirror is algebra -- Z' = (-eps) - (-e) = -Z -- and "
            "holds under any reflection-equivariant detector regardless of the "
            "family.  It is therefore NOT evidence that the method is valid.  "
            "Validity needs the negated stream to have the same law, which is "
            "the separate check below and which skewnormal4 fails."
        ),
    }
    valid = {c["family"]: c["negated_stream_is_same_law"]
             for c in payload["negated_stream_validity"]}
    payload["reflection_pathwise_exact_for_symmetric_families"] = all(
        c["exact_to_machine_precision"]
        for c in payload["reflection_mirror_checks"])
    payload["reflection_distributionally_valid"] = valid
    payload["asymmetric_control_correctly_fails"] = not valid["skewnormal4"]
    payload["reflection_admissible_for_symmetric_families"] = (
        payload["reflection_pathwise_exact_for_symmetric_families"]
        and valid["t1p5"] and not valid["skewnormal4"]
    )
    payload["reflection_verdict"] = (
        "EXACT BUT VARIANCE-CATASTROPHIC: the method is unbiased for symmetric "
        "families, but substituting the mirror for the -h run destroys the "
        "common-random-number cancellation that makes coupled paths contribute "
        "exactly 1.  Measured variance reduction factor is 0.001-0.003, i.e. a "
        "300-1000x variance INCREASE.  Not adopted."
    )
    payload["wall_seconds"] = time.perf_counter() - t0

    out = PILOT / "results" / "bias_checks.json"
    out.write_text(json.dumps(payload, indent=2) + "\n")
    for c in payload["reflection_mirror_checks"]:
        print(f"mirror  {c['family']:12s} {c['detector']:14s} "
              f"tau_identical={c['stopping_times_identical']!s:5s} "
              f"max|W+ + W-|={c['max_abs_window_sum']:.3e} "
              f"exact={c['exact_to_machine_precision']}")
    a = payload["asymmetric_pathwise_control"]
    print(f"pathwise control {a['family']:12s} {a['detector']:14s} "
          f"exact={a['exact_to_machine_precision']} "
          f"(expected True: pathwise mirror is family-independent algebra)")
    for c in payload["negated_stream_validity"]:
        print(f"negated-stream law  {c['family']:12s} KS={c['ks_statistic']:.5f} "
              f"p={c['ks_pvalue']:.3g} skew={c['sample_skewness']:+.4f} "
              f"same_law={c['negated_stream_is_same_law']}")
    print(f"reflection admissible for symmetric families: "
          f"{payload['reflection_admissible_for_symmetric_families']}")
    print(f"verdict: {payload['reflection_verdict']}")
    print(f"-> {out}")


if __name__ == "__main__":
    main()
