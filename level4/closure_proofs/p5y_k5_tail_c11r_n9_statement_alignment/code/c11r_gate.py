"""C11R Phase 5 -- the prospective gate, frozen BEFORE target certification.

THE GATE CONTAINS NO EXPECTED RESULT. C11's gate said of its own central criterion "this is the
criterion C11 must and does fail", and that single clause is the proximate cause of its campaign
error: having written the outcome into the gate, it treated its failing candidate as confirmation
rather than as something to falsify. This gate states predicates only.

That is not left to good intentions. This module carries a scanner for result-dependent language
and refuses to emit a gate that contains any. The scanner's own vocabulary lives here, in the
producer, and only the emitted JSON is scanned -- a scanner that reads its own forbidden list
matches itself and always fires (the C10 self-scan lesson, reproduced in C11R's own B0).
"""
from __future__ import annotations

import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import c11r_common as C

# Phrases that assert an outcome rather than state a test. Kept as fragments so that tense and
# subject do not matter: "must fail", "does fail", "will fail" all reduce to the same stem.
RESULT_LANGUAGE = [
    r"\bmust fail\b", r"\bdoes fail\b", r"\bwill fail\b", r"\bwill pass\b", r"\bdoes pass\b",
    r"\bmust pass\b", r"\bexpected to (close|fail|pass|succeed)\b", r"\bshould certify\b",
    r"\bshould close\b", r"\bwill certify\b", r"\bwill close\b", r"\bcannot succeed\b",
    r"\bis expected\b", r"\bwe expect\b", r"\banticipate[ds]? (failure|success)\b",
    r"\bthe answer is\b", r"\bknown to (fail|pass)\b",
]


def scan_for_result_language(obj) -> list[dict]:
    """Walk a JSON structure and report any string asserting an outcome."""
    hits = []

    def walk(o, path):
        if isinstance(o, dict):
            for k, v in o.items():
                walk(v, f"{path}.{k}")
        elif isinstance(o, list):
            for i, v in enumerate(o):
                walk(v, f"{path}[{i}]")
        elif isinstance(o, str):
            for pat in RESULT_LANGUAGE:
                m = re.search(pat, o, re.I)
                if m:
                    hits.append({"path": path, "phrase": m.group(0),
                                 "context": o[max(0, m.start() - 40):m.end() + 40]})
    walk(obj, "$")
    return hits


def build(tbl: dict, policy: dict) -> dict:
    d = tbl["drift_domain"]
    return {
        "schema": "C11R_GATE/2",
        "supersedes": ("C11R_GATE/1 (49b17ab4), reviewed NOT_READY. Four of its predicates -- G8, "
                       "G11, G12, G13 -- were satisfied by merely RECORDING an outcome, including a "
                       "failing one, so they could not fail on substance (review item 9)."),
        "campaign": "C11R -- N9 statement-alignment repair",
        "frozen_before": "any target certification run",
        "question": ("can the independent C11 certifier prove the SAME mathematical certification "
                     "statements N9 requires for cell 306?"),
        "governing_principle": "SAME STATEMENT BEFORE SAME NUMBER",
        "statements_sha256": tbl["sha256"],
        "policy_sha256": policy["sha256"],

        "NO_EXPECTED_RESULT": (
            "This gate states predicates only. No predicate names, presupposes or favours any "
            "outcome, and each can fail on substance. The verdict is whatever they yield."),

        "target": {"cell": 306, "constants": list(C.SIX_CONSTANTS),
                   "drift_domain": [d["e_lo"], d["e_hi"]],
                   "drift_domain_float": [d["e_lo_float"], d["e_hi_float"]],
                   "substitutions_forbidden": ["cell 307", "cell 308", "cell 309",
                                               "a scalar drift", "a strict sub-interval",
                                               "Abar in place of tau", "tau in place of Abar",
                                               "the original's C_T or tau as a premise"]},

        "predicates": {
            "G1_statement_table_complete": (
                "C11R_N9_STATEMENTS reports TABLE_CLASS = RESOLVED with no unresolved field for "
                "any of the six constants"),
            "G2_statement_equivalence_exact": (
                "for each target, the independent proposition is reconstructed ONLY from the runs "
                "artifact's own record and is EQUIVALENT or STRONGER than the original's under "
                "c11r_equiv.compare, whose self-test rejects every planted mismatch and accepts "
                "every honest control"),
            "G3_drift_interval_exact": (
                "every independent statement's drift domain, compared as exact rationals, equals "
                "or contains [680769/400000, 17885921/10000000]"),
            "G4_block_uniformity_rigorous": (
                "certification encloses the quantity simultaneously for every e in the block by "
                "carrying e as an interval; no endpoint, midpoint or grid of drifts is used"),
            "G5_independent_K_e_implemented": (
                "the whole-kernel certificate is produced by the reviewed "
                "c11r_idrift.supersolution_margin_iv, and c11r_idrift.py is byte-identical to the "
                "version the first pre-freeze review found sound"),
            "G6_independent_Khat_e_implemented": (
                "the atom-removed certificates are produced by the same reviewed module with "
                "atom_removed=True, and by c11r_boxdata for the sub-solution route"),
            "G7_atom_decomposition_validated": (
                "validation V4 passes: K_e = Khat_e + atom for four weights at seven states"),
            "G8_six_targets_dispositioned_consistently": (
                "the runs artifact assigns each of the six constants exactly one of CERTIFIED, "
                "NOT_CERTIFIED or NOT_IMPLEMENTED, and NOT_IMPLEMENTED appears only for constants "
                "the frozen policy lists as not implemented"),
            "G9_no_forbidden_reuse": (
                "no module in the campaign's code closure imports, calls, wraps or replays the "
                "original certifier's load-bearing graph or its arithmetic backend"),
            "G10_cheap_screen_before_expensive": (
                "every selected member is checked against the pointwise necessary condition "
                "before certification, and a member failing it is recorded POINTWISE_INFEASIBLE "
                "and not certified"),
            "G11_manufactured_validation_passes": "VALIDATION_CLASS = PASS",
            "G12_mutations_pass": ("MUTATION_CLASS = PASS: no survivor and no undetermined "
                                   "mutant, every detector carrying an executed negative control"),
            "G13_evidence_fresh_and_consistent": (
                "c11r_status reports STATUS_CLASS = CONSISTENT: every artifact's producer, code "
                "closure and inputs match the committed tree, and no two artifacts contradict "
                "each other"),
            "G14_sealed_before_comparison": (
                "the runs artifact is committed, unmodified, schema-valid and bound to the "
                "committed runs producer before any original magnitude is loaded"),
            "G15_comparison_rule_frozen_before_results": (
                "the direction-aware comparison rule is fixed in the statement table, whose hash "
                "this gate binds, before any independent result exists"),
            "G16_original_value_firewall": (
                "FIREWALL_CLASS = PASS: only c11r_table.py and c11r_compare.py can load an original "
                "magnitude, proved by AST with planted positive and negative controls"),
            "G17_policy_prospective": (
                "the frozen policy references no original magnitude and no comparison threshold, "
                "chooses no candidate by hand, and fixes its configuration before target "
                "execution"),
        },

        "comparison_rule": tbl["comparison_semantics_frozen_before_results"],
        "comparison_rule_source": {"artifact": "evidence/table/C11R_N9_STATEMENTS.json",
                                   "sha256": tbl["sha256"]},
        "per_target_classification": ["AGREES", "STRONGER", "INSUFFICIENT", "DISAGREES", "INVALID"],
        "permitted_N9_classifications": ["N9_CLOSED", "AGREEMENT_INSUFFICIENT",
                                         "SCIENTIFIC_DISAGREEMENT", "INDEPENDENCE_VIOLATION",
                                         "EXECUTION_INVALID"],
        "N9_classification_precedence": ["INDEPENDENCE_VIOLATION", "SCIENTIFIC_DISAGREEMENT",
                                         "EXECUTION_INVALID", "N9_CLOSED",
                                         "AGREEMENT_INSUFFICIENT"],

        "SCOPE": {
            "N9_closure_requires": ("all six constants for cell 306 classified AGREES or "
                                    "STRONGER, each with an EQUIVALENT or STRONGER statement"),
            "consequence_stated_conditionally": (
                "if D1 and D2 are not independently certified, N9 remains OPEN whatever the other "
                "four constants yield"),
            "what_a_subset_would_mean": (
                "independent same-statement certification of a SUBSET of the six is scientific "
                "and governance evidence. It is not N9 closure."),
            "D1_D2": ("a later prospective derivative-system extension would be needed; the D_lo "
                      "sub-solution route does not establish D1 or D2"),
        },

        "forbidden_conclusions": [
            "that C11 is rewritten as success",
            "that any cell is closed or adopted",
            "that the C2 adoption floor may be replaced",
            "that F1 has lapsed",
            "that r6 may be created",
            "that N9 is closed while any of the six constants lacks an independent statement",
            "that numerical proximity substitutes for statement equivalence",
            "that a constant certified over a sub-interval of the block corroborates the original",
            "that a constant certified at a scalar drift corroborates a block-uniform statement"],

        "predecessor_state_preserved": {
            "C11_verdict": "EXECUTION_INVALID",
            "C2_to_C10": "historical verdicts immutable",
            "N9_entering_C11R": "OPEN",
            "coverage": "r5 authoritative; open m=5 cells {306, 307, 308, 309}; K5 PARTIAL"},

        "guard": "DENY",
        "compute_policy": {"AWS": "FORBIDDEN", "SR_PS1_campaign": "MUST NOT BE TOUCHED",
                           "remote_provisioning": "not required; the policy's cap is local"},
    }


def main() -> int:
    tbl = C.load(C.NS / "evidence" / "table" / "C11R_N9_STATEMENTS.json")
    policy = C.load(C.NS / "config" / "C11R_POLICY.json")
    gate = build(tbl, policy)

    hits = scan_for_result_language(gate)
    # negative control: the scanner must fire on a gate that DOES contain result language
    probe = dict(gate)
    probe["predicates"] = dict(gate["predicates"])
    probe["predicates"]["G_probe"] = "SEE BELOW -- this is the criterion C11R must and does fail"
    control = scan_for_result_language(probe)
    control_fires = len(control) > len(hits)

    if hits:
        print("REFUSE: the gate contains result-dependent language")
        for h in hits:
            print(f"  {h['path']}: {h['phrase']!r}  ...{h['context']}...")
        return 1
    if not control_fires:
        print("REFUSE: the result-language scanner did not fire on its own negative control, "
              "so it proves nothing")
        return 1

    gate["result_language_scan"] = {
        "patterns": len(RESULT_LANGUAGE),
        "hits_in_this_gate": 0,
        "negative_control": {
            "scanner_can_fire": True,
            "control_phrase_count": len(control),
            "where_the_control_text_lives": (
                "code/c11r_mutations.py, deliberately NOT here. Recording the planted phrase in "
                "the gate would put result-dependent language into the gate, and the scanner would "
                "then flag the gate on account of its own audit record -- which is exactly what "
                "happened on the first attempt.")},
        "note": ("the scanner reads only the emitted gate, never this module, because a scanner "
                 "that reads its own forbidden list matches itself and always fires")}

    s = C.write_evidence(C.NS / "config" / "N9R_GATE_C11R.json", gate, producer=__file__)
    print(f"predicates: {len(gate['predicates'])}")
    for k in gate["predicates"]:
        print(f"  {k}")
    print(f"\nresult-language scan: 0 hits; negative control caught "
          f"{control[0]['phrase']!r}")
    print(f"target cell {gate['target']['cell']}, drift "
          f"[{gate['target']['drift_domain_float'][0]:.7f}, "
          f"{gate['target']['drift_domain_float'][1]:.7f}]")
    print(f"wrote config/N9R_GATE_C11R.json sha256 {s[:16]}...")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
