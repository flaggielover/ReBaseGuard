"""Frozen vocabularies and validator rules for the P9R evidence graph.

Everything in this module is fixed at Checkpoint A, **before** any P9R
production result exists.  ``build_ledger.py`` may not add a class, an edge
type, a rank or a rule after results are seen.
"""
from __future__ import annotations

#: the frozen claim classes.  No class may be added to dodge a downgrade.
CLAIM_CLASSES = (
    "EXACT_THEOREM",
    "CONDITIONAL_THEOREM",
    "FORMALLY_VERIFIED",
    "CERTIFIED_NUMERICAL",
    "EMPIRICAL_REPRODUCED",
    "EMPIRICAL_ONLY",
    "NEGATIVE_RESULT",
    "NOT_ESTABLISHED",
    "PARTIAL_PRIORITY_RESULT",
    "PROVENANCE_LIMITATION",
)

#: licensed-strength ranks.  FORMALLY_VERIFIED sits at 6 as a fact about an
#: artifact (a kernel really did check it); that is why formal support is a
#: separate edge type and never a logical premise.
RANK = {
    "EXACT_THEOREM": 6,
    "FORMALLY_VERIFIED": 6,
    "CERTIFIED_NUMERICAL": 5,
    "CONDITIONAL_THEOREM": 4,
    "EMPIRICAL_REPRODUCED": 3,
    "EMPIRICAL_ONLY": 2,
    "NEGATIVE_RESULT": 2,
    "PARTIAL_PRIORITY_RESULT": 1,
    "PROVENANCE_LIMITATION": 1,
    "NOT_ESTABLISHED": 0,
}

CONDITIONAL_RANK = RANK["CONDITIONAL_THEOREM"]

#: the frozen edge types.
EDGE_TYPES = (
    "LOGICAL_PREMISE",            # the child's proof consumes the parent
    "ASSUMPTION",                 # an undischarged hypothesis the child needs
    "SCOPE_RESTRICTION",          # the parent fixes the child's model scope
    "FORMAL_SUPPORT",             # a kernel check ABOUT the parent
    "CERTIFIED_SUPPORT",          # an interval certificate ABOUT the parent
    "EMPIRICAL_SUPPORT",          # measurement consistent with the parent
    "REPRODUCTION",               # an independent replay of the parent
    "CONSISTENCY_CHECK",          # a cross-check, neither premise nor proof
    "NEGATIVE_RESULT_CONSTRAINT", # the parent bounds what the child may claim
    "PROVENANCE",                 # a process fact about the parent
    "STATUS_PROPAGATION",         # adjudicated priority status
)

#: only these edge types constrain licensed strength.
STRENGTH_EDGES = ("LOGICAL_PREMISE", "ASSUMPTION")

NODE_KINDS = ("DEFINITION", "ASSUMPTION", "CLAIM", "STATUS")

HYPOTHESES = (
    "NONE_BEYOND_MODEL",
    "DISCHARGED_FOR_FROZEN_MODEL",
    "STATED_NOT_DISCHARGED",
    "NOT_APPLICABLE",
)

#: classes that may never be a LOGICAL_PREMISE parent of an EXACT_THEOREM.
NON_EXACT_PREMISE_CLASSES = (
    "CONDITIONAL_THEOREM",
    "CERTIFIED_NUMERICAL",
    "EMPIRICAL_REPRODUCED",
    "EMPIRICAL_ONLY",
    "NEGATIVE_RESULT",
    "NOT_ESTABLISHED",
    "PARTIAL_PRIORITY_RESULT",
    "PROVENANCE_LIMITATION",
)

#: wording that may not appear in the statement of an EXACT_THEOREM claim.
FORBIDDEN_EXACT_WORDING = (
    "non-increasing", "nonincreasing", "monotone", "monotonic",
    "monotonicity", "decreasing in",
)

PARTIAL_OR_FAIL_PRIORITIES = ("P4", "P5", "P8", "P9")
CLOSED_PRIORITIES = ("P1", "P2", "P3", "P6", "P7", "P8R")

RULES = {
    "V1": "no EXACT_THEOREM has a LOGICAL_PREMISE parent that is empirical, "
          "conditional, certified, negative, partial or not-established",
    "V2": "no EXACT_THEOREM carries an ASSUMPTION edge",
    "V3": "FORMALLY_VERIFIED requires formal_evidence naming a kernel; "
          "CERTIFIED_NUMERICAL requires certified_evidence; no certified or "
          "empirical edge may substitute for formal support",
    "V4": "every CONDITIONAL_THEOREM declares hypotheses=STATED_NOT_DISCHARGED",
    "V5": "every EXACT_THEOREM declares hypotheses in {NONE_BEYOND_MODEL, "
          "DISCHARGED_FOR_FROZEN_MODEL}",
    "V6": "no STATUS node is the parent of a LOGICAL_PREMISE or ASSUMPTION edge",
    "V7": "the graph is acyclic",
    "V8": "every node's cited source path exists in the repository",
    "V9a": "a PARTIAL or FAIL priority does not invalidate all of its claims",
    "V9b": "a CLOSED priority does not automatically validate all of its claims",
    "V9c": "a FAIL priority does not delete its surviving evidence",
    "V10": "the dominance premise ASM-DOM exists, is reached by an ASSUMPTION "
           "edge from P9R-T2b, and is a LOGICAL_PREMISE of no EXACT_THEOREM",
    "V11": "no EXACT_THEOREM statement contains monotonicity wording",
    "V12": "P3-X1 is not classified FORMALLY_VERIFIED",
    "V13": "P8 status is FAIL, P8R status is CLOSED, and no P8R evidence is "
           "attributed to P8",
    "V14": "every novelty statement is classified NOT_ESTABLISHED",
    "V15": "licensed strength equals the declared rank for every claim "
           "(no inflation along premise or assumption edges)",
}
