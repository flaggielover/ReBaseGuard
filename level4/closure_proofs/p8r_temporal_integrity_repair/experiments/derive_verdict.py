"""Apply the frozen P8R closure rule and emit the candidate verdict.

The rule, frozen in ``FROZEN_GATES.md`` §4 before any result existed:

``CLOSED_CANDIDATE``
    every integrity gate ``I1``-``I13`` is ``PASS``, **and** every mandatory
    scientific question is resolved to an admissible status.
``PARTIAL_CANDIDATE``
    every integrity gate passes but at least one mandatory question is
    unresolved (missing, or not one of the four admissible statuses).
``FAIL_CANDIDATE``
    any integrity gate is ``FAIL`` or ``UNVERIFIABLE``.

Note what the rule does **not** say: it never requires a hypothesis to be true.
``S7 = REJECTED`` is a resolved question.  Forcing it to ``SUPPORTED`` by moving
a threshold would fail ``I7``, not help.

The verdict is a **candidate**.  It is not authoritative and must not be
promoted to ``CLOSED`` without independent adjudication.

Usage:  derive_verdict.py
"""
from __future__ import annotations

import json

import _common as C                                              # noqa: E402
from rebaseguard_p8r.config import RESULTS                       # noqa: E402

ADMISSIBLE = ("SUPPORTED", "REJECTED", "INCONCLUSIVE", "OUT_OF_SCOPE")
INTEGRITY_GATES = tuple(f"I{i}" for i in range(1, 14))
MANDATORY_QUESTIONS = ("S1", "S2", "S3", "S4", "S5", "S6", "S7", "S7D", "S7F",
                       "S7X", "S8", "S9", "S10", "S11", "S12", "S13", "S14",
                       "S15", "S16", "S17")

#: hypotheses P8 rejected.  P8R must not silently convert one into a PASS; if a
#: P8R rerun resolves one differently, that is a finding to be stated, not a
#: repair target.  Recorded here so the claim-class firewall test can check it.
P8_NEGATIVE_RESULTS = {
    "S7": "P8 G4: the cross-family window-separability law was REJECTED",
    "S7D": "P8 G4-D: detector invariance of K was REJECTED",
    "S7F": "P8 G4-F: family invariance of K was REJECTED",
    "S10": "P8 G7: literal P7-boundary transfer FAILED (4/6 families)",
    "S12": "P8 G9/adjudication: detector transfer was measured ABSENT",
    "S15": "P8: t3/m=20 attraction was NOT certified (EMPIRICAL only)",
}


def main() -> None:
    audit = json.loads((RESULTS / "integrity" / "integrity_audit.json")
                       .read_text())
    res = C.load_payload(RESULTS / "scientific_resolution.json")

    integrity = {g: audit["summary"].get(g, "MISSING") for g in INTEGRITY_GATES}
    integrity_ok = all(v == "PASS" for v in integrity.values())
    questions = {q: res["summary"].get(q, "MISSING") for q in MANDATORY_QUESTIONS}
    resolved_ok = all(v in ADMISSIBLE for v in questions.values())

    if not integrity_ok:
        verdict = "FAIL_CANDIDATE"
    elif not resolved_ok:
        verdict = "PARTIAL_CANDIDATE"
    else:
        verdict = "CLOSED_CANDIDATE"

    comparison = {}
    for q, note in P8_NEGATIVE_RESULTS.items():
        comparison[q] = {"p8_outcome": note, "p8r_status": questions.get(q),
                         "p8r_also_negative":
                             questions.get(q) in ("REJECTED", "INCONCLUSIVE")}

    payload = {
        "verdict": verdict,
        "authoritative": False,
        "authoritative_status_recommendation": "AWAIT_CODEX_ADJUDICATION",
        "integrity_gates": integrity,
        "integrity_all_pass": integrity_ok,
        "scientific_questions": questions,
        "all_questions_resolved": resolved_ok,
        "n_supported": sum(v == "SUPPORTED" for v in questions.values()),
        "n_rejected": sum(v == "REJECTED" for v in questions.values()),
        "n_inconclusive": sum(v == "INCONCLUSIVE" for v in questions.values()),
        "n_out_of_scope": sum(v == "OUT_OF_SCOPE" for v in questions.values()),
        "p8_negative_result_comparison": comparison,
        "novelty_status": "NOT_ESTABLISHED",
        "novelty_note": ("P8R is a repair campaign.  No independent novelty "
                         "review was run, so no novelty is claimed.  Zero "
                         "direct hits, the absence of a known transfer law, a "
                         "new negative result and a new empirical matrix are "
                         "explicitly NOT evidence of novelty."),
        "closure_rule": ("CLOSED_CANDIDATE iff every integrity gate passes AND "
                         "every mandatory question is resolved admissibly; "
                         "PARTIAL_CANDIDATE iff integrity passes but a "
                         "question is unresolved; FAIL_CANDIDATE iff any "
                         "integrity gate is FAIL or UNVERIFIABLE.  A REJECTED "
                         "hypothesis is a resolved question, not a failure."),
    }
    C.write(RESULTS / "verdict.json",
            C.envelope(generator="derive_verdict.py",
                       schema="rebaseguard.p8r.verdict.v1", tags=[],
                       payload=payload))
    print(json.dumps({k: payload[k] for k in
                      ("verdict", "integrity_all_pass",
                       "all_questions_resolved", "n_supported", "n_rejected",
                       "n_inconclusive", "n_out_of_scope", "novelty_status")},
                     indent=1))
    print(json.dumps(payload["scientific_questions"], indent=1))


if __name__ == "__main__":
    main()
