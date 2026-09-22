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


def build(tbl: dict) -> dict:
    d = tbl["drift_domain"]
    return {
        "schema": "C11R_GATE/1",
        "campaign": "C11R -- N9 statement-alignment repair",
        "frozen_before": "any target certification run",
        "question": ("can the independent C11 certifier prove the SAME mathematical certification "
                     "statements N9 requires for cell 306?"),
        "governing_principle": "SAME STATEMENT BEFORE SAME NUMBER",

        "NO_EXPECTED_RESULT": (
            "This gate states predicates only. No predicate below names, presupposes or favours any "
            "outcome. Whether each predicate holds is determined by running the campaign, and the "
            "verdict is whatever the predicates yield."),

        "target": {"cell": 306, "constants": list(C.SIX_CONSTANTS),
                   "drift_domain": [d["e_lo"], d["e_hi"]],
                   "drift_domain_float": [d["e_lo_float"], d["e_hi_float"]],
                   "substitutions_forbidden": ["cell 307", "cell 308", "cell 309",
                                               "a scalar drift", "a strict sub-interval",
                                               "Abar in place of tau", "tau in place of Abar",
                                               "fewer than the six constants"]},

        "predicates": {
            "G1_statement_table_complete": (
                "every field of the Phase 1 table is resolved for all six constants: name, "
                "producer, mode, kernel, quantity, state convention, drift domain, norm, "
                "direction, certified value, artifact hash, comparison semantics"),
            "G2_statement_equivalence_exact": (
                "for each target, the independent proposition matches the original on kernel, "
                "quantity, state, direction and bounded object, checked by a comparator that is "
                "demonstrated to reject planted mismatches"),
            "G3_drift_interval_exact": (
                "the drift domain used equals the cell 306 block read from REGISTRY_C2, as exact "
                "rationals, with no rounding of the endpoints"),
            "G4_block_uniformity_rigorous": (
                "the certification encloses the quantity simultaneously for every e in the block. "
                "Endpoint, midpoint or finite-grid evaluation satisfies this predicate only when "
                "accompanied by a proof that those checks bound the whole interval"),
            "G5_independent_K_e_implemented": (
                "the whole kernel is implemented in this programme's independent line and its "
                "identities are exercised"),
            "G6_independent_Khat_e_implemented": (
                "the atom-removed kernel is implemented independently, derived from the frozen "
                "model rather than transcribed from the original"),
            "G7_atom_decomposition_validated": (
                "K_e equals Khat_e plus the atom contribution, under this project's own sign and "
                "normalisation, recovered by test rather than assumed"),
            "G8_six_targets_resolved": (
                "each of the six constants has a recorded disposition: an independent statement "
                "with a value, a recorded refutation, or a recorded absence of any independent "
                "statement"),
            "G9_no_forbidden_reuse": (
                "no module in this campaign imports, calls, wraps or replays the original "
                "certifier's load-bearing graph, and none imports its arithmetic backend"),
            "G10_cheap_screen_before_expensive": (
                "every candidate sent to a certification run has first been screened by the "
                "pointwise necessary condition, and no candidate classified POINTWISE_REFUTED has "
                "been sent to one"),
            "G11_manufactured_validation": (
                "the manufactured identities are exercised by a producer and their outcomes are "
                "recorded, including scalar collapse of the interval-drift layer"),
            "G12_mutations": (
                "each planted violation is classified by a detector that carries a negative "
                "control showing the detector can fail"),
            "G13_runtime_qualified": (
                "producer hashes, imports and deterministic reproduction are recorded from a clean "
                "environment before target execution"),
            "G14_sealed_before_comparison": (
                "every independent output is written and hashed before any original value for the "
                "same constant is read in the same process"),
            "G15_comparison_rule_frozen_before_results": (
                "the per-direction comparison rule is fixed in an artifact whose hash predates "
                "every independent result it is applied to"),
        },

        "comparison_rule": tbl["comparison_semantics_frozen_before_results"],
        "comparison_rule_source": {
            "artifact": "evidence/table/C11R_N9_TABLE.json",
            "sha256": tbl["sha256"],
            "note": "frozen in Phase 1, before any independent value existed"},

        "per_target_classification": ["AGREES", "STRONGER", "INSUFFICIENT", "DISAGREES", "INVALID"],
        "permitted_N9_classifications": ["N9_CLOSED", "AGREEMENT_INSUFFICIENT",
                                         "SCIENTIFIC_DISAGREEMENT", "INDEPENDENCE_VIOLATION",
                                         "EXECUTION_INVALID"],

        "forbidden_conclusions": [
            "that C11 is rewritten as success",
            "that any cell is closed or adopted",
            "that the C2 adoption floor may be replaced",
            "that F1 has lapsed",
            "that r6 may be created",
            "that numerical proximity substitutes for statement equivalence",
            "that a constant certified over a sub-interval of the block corroborates the original",
            "that a constant certified at a scalar drift corroborates a block-uniform statement"],

        "predecessor_state_preserved": {
            "C11_verdict": "EXECUTION_INVALID",
            "N9_entering_C11R": "OPEN",
            "mismatch_A": "scalar drift versus the block-uniform statement",
            "mismatch_B": "one constant for cell 307 versus six for cell 306, and no Khat_e"},

        "guard": "DENY",
        "compute_policy": {"AWS": "FORBIDDEN", "SR_PS1_campaign": "MUST NOT BE TOUCHED",
                           "remote_provisioning": "only if local execution is shown inadequate"},
    }


def main() -> int:
    tbl = C.load(C.NS / "evidence" / "table" / "C11R_N9_TABLE.json")
    gate = build(tbl)

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

    s = C.write_evidence(C.NS / "config" / "N9R_GATE_C11R.json", gate)
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
