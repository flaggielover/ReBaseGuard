"""C11R errata -- defects in this campaign's own conduct, recorded as they were found.

C8's recorded defect class is a SILENT deviation from a frozen gate, in the campaign's own favour.
The remedy is not to avoid ever deviating; it is to record every deviation where a reader will find
it, with enough detail to judge whether the correction was adequate.

REVISION 2 follows the independent pre-freeze review of 2026-09-23 (review/REVIEW_C11R_PREFREEZE.md,
verdict NOT_READY, preserved verbatim at 6d7cd546). Revision 1 is at 38f59993. Revision 2 does not
soften any revision-1 entry. It corrects one false sentence in E2 -- which is RETRACTED, not left
live -- and adds the defects the review found, including three in this campaign's own reporting.
"""
from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import c11r_common as C

ERRATA = {
    "E1_PHASE_ORDER_TARGET_EXECUTION_BEFORE_PREFREEZE_REVIEW": {
        "rule": "Phase 9: 'Do not execute target science before READY_TO_FREEZE.'",
        "what_happened": ("c11r_runs.py -- the module that certifies the cell 306 targets -- was "
                          "started before the pre-freeze review was requested. It ran for about "
                          "two minutes on its first candidate, the K_e one."),
        "correction": ("killed before it wrote anything. No evidence/runs/ directory was created "
                       "and no C11R_RUNS.json exists in any commit. Target execution has been "
                       "withheld since."),
        "independent_check": ("the pre-freeze reviewer verified the absence itself: "
                              "`git log --all -- '*C11R_RUNS.json'` empty, no evidence/runs/ on "
                              "disk. It also noted that a depth-4 K_e run could not have printed a "
                              "certified value, which is consistent with 'no target value was "
                              "observed'."),
        "what_was_NOT_out_of_order": ("the Phase 6 refutation screen. Phase 6 precedes Phase 9, "
                                      "and a necessary-condition screen is not a certification."),
        "two_further_defects_the_review_found_in_this_entry": [
            ("revision 1 of this entry said 'Verified: ... the worktree is clean'. That was FALSE "
             "at the moment it was written: the errata file carrying the sentence was itself "
             "untracked."),
            ("the campaign record moved during the review. The review was requested against "
             "49b17ab4; 38f59993 (this module's revision 1 and c11r_qualify.py) was committed "
             "while it ran. A campaign that asks for review of a fixed state must hold that state "
             "until the review returns. The fresh review for this repair is requested only "
             "against a committed, clean tree, which is then not modified until it returns."),
        ],
        "found_by": "the author (the lapse); the independent pre-freeze review (the two defects)",
    },

    "E2_CANDIDATE_CHANGED_AFTER_SCREEN_WITH_ORIGINAL_VALUES_IN_VIEW": {
        "status": "REVISED in revision 2. The revision-1 version contained a false sentence.",
        "factual_sequence": [
            ("Phase 1 wrote the original values of all six constants into "
             "evidence/table/C11R_N9_TABLE.json, so they were known to the author from then on."),
            ("the Phase 6 screen printed 'original Abar 7.9124, tau 5.1698, C_T 5.8299' in the "
             "same output as the candidate margins (c11r_screen.py lines 112-115, revision 1)."),
            ("before changing the candidate, the author wrote to the user: 'Against the originals "
             "that would be 8/5.1698 = 1.547 and 8/5.8299 = 1.372, both inside the frozen factor "
             "of 2.' Ratios against the original values were therefore explicitly computed before "
             "the change."),
            ("the atom-removed candidate was then changed from w = 12 - 3/2 m to w = 8 - m."),
            ("under the frozen factor-2 rule that change moves C_T from 2.058x to 1.372x and tau "
             "from 2.321x to 1.547x -- from INSUFFICIENT to AGREES for both."),
        ],
        "the_stated_rationale_does_not_discriminate": (
            "revision 1 justified the change as 'w = 8 - m yields BOTH atom-removed constants from "
            "one certification run'. That is equally true of the dropped w = 12 - 3/2 m, which is "
            "also a Khat_e supersolution read at the atom and as a sup over R. The rationale "
            "therefore does not explain why one was replaced by the other."),
        "finding": ("post-screen candidate selection with the original answers in view occurred. "
                    "No inference about motive is needed or made beyond that factual sequence."),
        "consequence": ("w = 8 - m is NOT grandfathered as prospectively clean merely because it "
                        "was committed. It is discarded. The replacement is selected by the frozen "
                        "rule in config/C11R_POLICY.json, which consumes no original magnitude and "
                        "leaves no candidate to a human choice."),
        "RETRACTED_sentence_from_revision_1": {
            "status": "RETRACTED -- false; do not rely on it",
            "text": ("this is NOT fitting to the original's value -- the screen reports only this "
                     "campaign's own margins"),
            "why_false": ("the screen output did include the original values, and ratios to them "
                          "were computed before the change"),
            "revision_1_location": "38f59993:evidence/errata/C11R_ERRATA.json",
        },
        "found_by": "the independent pre-freeze review (finding 13(c)), confirmed by the author",
    },

    "E3_INSTRUCTION_QUOTED_THE_WRONG_DRIFT_BLOCK": {
        "rule": "the campaign instruction states the drift interval as [1.7885921, 1.882413].",
        "what_happened": ("that is CELL 307's block. Cell 306's block, read from REGISTRY_C2, is "
                          "[680769/400000, 17885921/10000000] = [1.7019225, 1.7885921]. The two are "
                          "adjacent; cell 307's lower endpoint IS cell 306's upper endpoint."),
        "resolution": ("cell 306 is named as the target throughout and substituting 307 is "
                       "forbidden, so cell 306's own registry block governs. Not a hard stop: no "
                       "constant is ambiguous, only a quoted interval disagrees with the registry "
                       "the instruction points at."),
        "independent_check": "confirmed by the pre-freeze reviewer (item 2), including that cell "
                             "307 has 10 sub-blocks to cell 306's 9.",
        "found_by": "Phase 1 reconstruction",
    },

    "E4_STALE_MUTATION_EVIDENCE_FROZEN_BESIDE_THE_GATE": {
        "what_happened": ("at 49b17ab4 -- the commit submitted as the freeze -- the committed "
                          "evidence/mutations/C11R_MUTATIONS.json recorded MUTATION_CLASS = REFUSE, "
                          "with M29 SURVIVED on 'scalar collapse is bit-for-bit: 9 mismatches' and "
                          "M28 UNDETERMINED on 'no screen artifact exists yet'. The committed "
                          "evidence/validation/C11R_VALIDATION.json in the same commit recorded V6 "
                          "PASS with 0 mismatches, and the committed screen artifact existed."),
        "cause": ("the mutation suite was run while an earlier c11r_idrift.py produced 9 V6 "
                  "mismatches. _piece_integral was then repaired and validation and the screen "
                  "were re-run -- but the mutation suite was not. 38f59993 carried the same stale "
                  "artifact forward."),
        "why_it_was_undetectable_from_the_evidence": ("no validation, mutation or screen artifact "
                                                      "recorded the code hash that produced it, so "
                                                      "which code generated the stale file could "
                                                      "not be reconstructed from the artifacts."),
        "prevention": ("every artifact now binds the sha256 of its producer and of every campaign "
                       "module it imports, plus the sha256 of each input artifact "
                       "(c11r_common.provenance). code/c11r_status.py recomputes all of them and "
                       "REFUSES if any artifact's recorded producer hash differs from the current "
                       "code, if any recorded input hash differs from the current input, or if two "
                       "artifacts contradict each other -- a validation reporting 0 V6 mismatches "
                       "beside a mutation record citing 9 is an automatic REFUSE."),
        "found_by": "the independent pre-freeze review (items 11 and 14)",
    },

    "E5_THIS_CAMPAIGNS_OWN_STATUS_REPORTING_MISSTATED_THE_MUTATION_STATE": {
        "what_happened": [
            ("the author's status table to the user listed Phase 8 as 'M01-M29, M26/M28 "
             "UNDETERMINED pending runs'. The committed class was REFUSE with M29 SURVIVED."),
            ("the 49b17ab4 commit message said 'Phase 8 mutations M01-M29, each with a negative "
             "control', which a reader takes to mean a passing suite. It was not passing."),
            ("the brief sent to the pre-freeze reviewer described M26 and M28 as undetermined "
             "'because the runs artifact does not exist yet'. That was accurate for M26 only; "
             "M28's recorded reason was the absent screen, and the brief omitted M29 SURVIVED and "
             "the class REFUSE."),
        ],
        "cause": "status was typed from memory rather than generated from the artifacts.",
        "prevention": ("the status report for this repair is generated by code/c11r_status.py "
                       "from the committed artifacts. No status line is typed by hand."),
        "found_by": "the independent pre-freeze review (item 11); confirmed by the author",
    },

    "E6_THE_COMPARATOR_COULD_ONLY_RETURN_EQUIVALENT": {
        "what_happened": ("revision 1 of c11r_compare.py built the 'independent' proposition as "
                          "dict(orig_props[name]) and overwrote only its drift domain -- with a "
                          "value identical to the original's. EQ.check therefore compared the "
                          "original against a copy of itself and could only return EQUIVALENT. No "
                          "field of the runs artifact was ever read."),
        "aggravating": [
            ("the same module carried pre-written result prose -- 'agreement is established with "
             "statements equal to the original's', 'No target is INVALID and none DISAGREES' -- "
             "the C11 result-in-the-gate defect, moved into a module the result-language scanner "
             "never read."),
            ("its artifact claimed the DISAGREES branch was 'implemented and exercised by a "
             "negative control'. classify() contained no DISAGREES return at all."),
            ("with n_invalid structurally 0 and D_lo/D1/D2 hard-coded to no value, "
             "AGREEMENT_INSUFFICIENT was the only reachable verdict."),
        ],
        "repair": ("code/c11r_compare.py is rebuilt. The independent proposition is reconstructed "
                   "solely from the runs artifact's own fields; the original proposition is "
                   "loaded only afterwards; no result prose exists before classification; "
                   "DISAGREES is a real return, exercised by an executed control."),
        "found_by": "the independent pre-freeze review (items 4 and 9)",
    },

    "E7_DEAD_AND_MIS_SCOPED_MUTANTS": {
        "what_happened": [
            ("M26 tested runs.get('sealed_sha256'). The runs producer wrote that key zero times, "
             "so once a runs artifact existed M26 was guaranteed to report SURVIVED."),
            ("M28 read 'depth' from a 'certification' sub-dict. The runs producer wrote 'depth' "
             "at the candidate's top level and never wrote a 'certification' key, so M28 could "
             "never fire."),
            ("M03 fired only on the literal 'REGISTRY_C2.json' inside a call. c11r_screen.py read "
             "the original certified constants through the Phase 1 table and was not caught."),
            "M29's negative control was a transcribed historical number, not an executed check.",
        ],
        "repair": ("the target run schema is defined once, in code/c11r_schema.py, and imported by "
                   "both the runs producer and every verifier, so a producer/verifier path "
                   "mismatch cannot arise. Every mutant executes against an artifact built by the "
                   "producer's own emission function, records the exact mutated JSON path and "
                   "value, and carries an executed control. M03 is replaced by the AST firewall "
                   "scanner, which covers every path to an original magnitude."),
        "found_by": "the independent pre-freeze review (item 11)",
    },

    "E8_ORIGINAL_MAGNITUDES_REACHED_A_PRE_RESULT_MODULE": {
        "what_happened": ("c11r_screen.py -- a module that influenced candidate selection -- "
                          "loaded tbl['constants'][k]['value_float'] and printed the original "
                          "Abar, tau and C_T. This is the path by which E2 happened."),
        "repair": ("the Phase 1 table is split. The statement table (semantics: kernel, quantity, "
                   "state, direction, drift block, aggregation, dependencies, artifact hashes) "
                   "carries NO magnitude. The six original magnitudes live only in a quarantine "
                   "artifact that exactly two modules may load: the table producer, which "
                   "extracts them, and the post-seal comparator. code/c11r_firewall.py proves "
                   "this by AST with planted positive and negative controls."),
        "found_by": "the independent pre-freeze review (items 10, 11 and 13(c))",
    },

    "E9_THE_WHOLE_FIRST_CANDIDATE_SET_WAS_WRITTEN_WITH_ORIGINALS_KNOWN": {
        "what_happened": ("E2 concerns one change, but every one of the seven screened candidates "
                          "(K_e 12/20/40/100 and Khat 8/12/20) was written after Phase 1 had put "
                          "the six original values in the table. None of them can be shown to be "
                          "free of that knowledge."),
        "disposition": ("the entire first candidate set, and the revision-1 screen evidence built "
                        "on it, are superseded -- not re-used, not re-ranked. No candidate is "
                        "hand-picked in revision 2: the frozen rule selects by optimisation."),
        "found_by": "the author, extending the review's finding 13(c) to its full scope",
    },

    "E10_ELIGIBILITY_WAS_READ_AS_EVIDENCE_OF_CERTIFIABILITY": {
        "what_happened": ("the screen found both frozen candidates ELIGIBLE, and the author "
                          "described that as the candidates 'surviving' and certification as "
                          "'looking reachable'. At depth 4 and 16 panels both fail: box margins "
                          "down to -0.40723 on boxes that lie in X.cover(4) and meet R."),
        "rule_from_now_on": ("a screen pass is a NECESSARY condition only. It is never again "
                             "described as evidence that a particular depth or panel count will "
                             "certify."),
        "found_by": "the independent pre-freeze review (finding 13(a)), reproduced to 5 decimals",
    },
}


def main() -> int:
    out = {"schema": "C11R_ERRATA/2",
           "supersedes": "C11R_ERRATA/1 at 38f59993",
           "policy": ("defects in this campaign's own conduct, recorded where a reader will find "
                      "them. A deviation that is recorded can be judged; one that is not, cannot."),
           "review_answered": {"path": "review/REVIEW_C11R_PREFREEZE.md", "verdict": "NOT_READY",
                               "preserved_at": "6d7cd546"},
           "errata": ERRATA,
           "count": len(ERRATA)}
    s = C.write_evidence(C.NS / "evidence" / "errata" / "C11R_ERRATA.json", out,
                         producer=__file__)
    for k in ERRATA:
        print(f"  {k}")
    print(f"\nwrote evidence/errata/C11R_ERRATA.json sha256 {s[:16]}...")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
