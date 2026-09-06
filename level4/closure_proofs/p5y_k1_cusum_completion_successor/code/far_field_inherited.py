"""Far field: INHERITED from the authoritative binding K1/P5X certificate.

Independent adjudication of f8e6f758 concluded:

    CUSUM_FAR_FIELD = PASS
    SR_FAR_FIELD    = PASS
    FAR_FIELD_GOVERNANCE = IMPLEMENTATION_GAP
    "there is NO uncovered interval between c_D and e_far"

and directed that the predecessor's contrary reading not be preserved.

WHAT THE PREDECESSOR GOT WRONG
------------------------------
`p5y_k1_final_completion/code/far_field.py` re-derived its own majorant

    B(e) = sqrt(2m+2) * sqrt(Phi(c_D - e))

found it did not close m=3,5 at e = c_D, and concluded there was an uncovered
interval `(c_D, ~c_D+0.43]`. That conclusion was wrong. The error was one of
authority, not arithmetic: a freshly invented, deliberately crude majorant was
allowed to override the binding certificate rather than being recognised as a
weaker sufficient condition. A bound that fails to prove something proves
nothing about whether it holds; the authoritative certificate already
establishes the far-field PASS for both detectors.

THIS SUCCESSOR THEREFORE
------------------------
  * inherits CUSUM_FAR_FIELD = PASS and SR_FAR_FIELD = PASS unchanged;
  * changes no far-field logic and re-derives no replacement;
  * does not carry forward the "uncovered interval" claim;
  * records the predecessor's superseded reading so the correction is auditable
    rather than silently dropped.

The `FAR_FIELD_GOVERNANCE = IMPLEMENTATION_GAP` finding is an implementation
matter for a future task (the K1 namespace holds no executable far-field
certificate of its own), not a scientific gap in the cover.
"""
from __future__ import annotations

import ancestry

INHERITED = {
    "CUSUM_FAR_FIELD": "PASS",
    "SR_FAR_FIELD": "PASS",
    "authority": "binding K1/P5X far-field certificate (P5X-T3)",
    "confirmed_by": "independent adjudication of f8e6f758",
    "uncovered_interval_between_c_D_and_e_far": None,
    "re_derived_here": False,
    "far_field_logic_changed_here": False,
    "governance_note": "FAR_FIELD_GOVERNANCE = IMPLEMENTATION_GAP: the K1 "
                       "namespace carries no executable far-field certificate "
                       "of its own; that is an implementation task, not a gap "
                       "in the cover",
}

SUPERSEDED_PREDECESSOR_READING = {
    "namespace": "p5y_k1_final_completion",
    "module": "code/far_field.py",
    "claim": "far field NOT_ESTABLISHED at the frozen K1 splice; uncovered "
             "interval (5.5, 5.9307] for CUSUM and (6.7555, 7.1863] for SR",
    "status": "SUPERSEDED — rejected by independent adjudication",
    "why_it_was_wrong": "a freshly invented crude majorant was allowed to "
                        "override the binding certificate; failing to prove a "
                        "bound is not evidence the bound is false",
    "predecessor_bytes_preserved": True,
}


def report() -> dict:
    return {"schema": "k1.cusum-successor.far-field-inherited.v1",
            "inherited": INHERITED,
            "superseded_predecessor_reading": SUPERSEDED_PREDECESSOR_READING,
            "predecessor_commit": ancestry.FINAL_COMMIT,
            "result_bearing": False}
