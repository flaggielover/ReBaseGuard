"""Far field: INHERITED, unchanged, not re-derived.

    CUSUM_FAR_FIELD = PASS
    SR_FAR_FIELD    = PASS
    FAR_FIELD_PRESERVATION = PASS   (adjudication of 70a29436)

There is NO uncovered interval between `c_D` and `e_far`. The claim that there
was, made two namespaces ago, was rejected: a freshly invented crude majorant had
been allowed to override the binding K1/P5X certificate, and failing to prove a
bound is not evidence that the bound is false.

This namespace changes no far-field logic, re-derives nothing, and does not carry
the superseded reading forward. It records the inheritance so that the
preservation is checkable rather than assumed.
"""
from __future__ import annotations

import ancestry

INHERITED = {
    "CUSUM_FAR_FIELD": "PASS",
    "SR_FAR_FIELD": "PASS",
    "FAR_FIELD_PRESERVATION": "PASS",
    "authority": "binding K1/P5X far-field certificate (P5X-T3)",
    "confirmed_by": "independent adjudication of 70a29436",
    "uncovered_interval_between_c_D_and_e_far": None,
    "re_derived_here": False,
    "far_field_logic_changed_here": False,
    "gap_claim_reintroduced": False,
}


def report() -> dict:
    return {"schema": "k1.cusum-aux3.far-field-inherited.v1",
            "inherited": INHERITED,
            "predecessor_commit": ancestry.CUSUM_COMMIT,
            "result_bearing": False}
