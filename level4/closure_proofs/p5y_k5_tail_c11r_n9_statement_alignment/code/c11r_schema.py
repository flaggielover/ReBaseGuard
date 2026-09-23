"""C11R shared schema -- the ONE definition of a statement record and of the target run artifact.

WHY THIS MODULE EXISTS (erratum E7). Revision 1's runs producer wrote `depth` at a candidate's top
level and never wrote `sealed_sha256`, while mutants M26 and M28 read `certification.depth` and
`sealed_sha256`. The producer and its verifiers spelled their paths independently, so each
verifier checked a structure that would never exist. Here the paths are defined once. The runs
producer builds its artifact with `emit_runs`, and every verifier reads it with the accessors
below, so a producer/verifier path mismatch cannot arise. `validate_runs` rejects any artifact that
does not have exactly this shape.

This module holds SEMANTICS only. It contains no original magnitude and loads no artifact.
"""
from __future__ import annotations

from fractions import Fraction as F

SIX_CONSTANTS = ("C_T", "tau", "Abar", "D_lo", "D1", "D2")

# ---------------------------------------------------------------------------------------------
# The state set. C_T is a supremum over it, so it is part of the statement, not background.
# The pre-freeze reviewer verified (item 13(d)) that the original's X -- the union of
# resolvent_certificate.reachable_pieces -- equals this set.
# ---------------------------------------------------------------------------------------------
STATE_SET_R = ("R = {(p, m) in [0,5]^2 : p + m <= 4 or p = 0 or m = 0}; "
               "atom a = (0, 0); certified over a box cover that is a superset of R")

# ---------------------------------------------------------------------------------------------
# A statement record. EXACT fields must match between the two sides. The drift domain is compared
# as exact rationals. Dependencies are compared as sets, with the rule that FEWER premises is a
# logically STRONGER statement.
# ---------------------------------------------------------------------------------------------
EXACT_FIELDS = ("constant", "quantity", "kernel", "convention", "direction", "state_set",
                "proposition")
STATEMENT_FIELDS = EXACT_FIELDS + ("drift_domain", "aggregation", "dependencies", "producer")

QUANTITY = {
    "C_T": "sup over R of w, for a Khat_e supersolution w",
    "tau": "w(atom), for a Khat_e supersolution w",
    "Abar": "w(atom), for a K_e supersolution w",
    "D_lo": "d(atom), where d = Ghat_e h_1 = P_x(alarm before reaching the atom)",
    "D1": "|d'(atom)|, the first drift derivative of d",
    "D2": "|d''(atom)|, the second drift derivative of d",
}
KERNEL = {"C_T": "Khat_e", "tau": "Khat_e", "Abar": "K_e",
          "D_lo": "Khat_e", "D1": "Khat_e", "D2": "Khat_e"}
CONVENTION = {"K_e": "full", "Khat_e": "atom_removed"}
DIRECTION = {"C_T": "UPPER_BOUND", "tau": "UPPER_BOUND", "Abar": "UPPER_BOUND",
             "D_lo": "LOWER_BOUND", "D1": "UPPER_BOUND", "D2": "UPPER_BOUND"}
PROPOSITION = {
    "C_T": "for every e in the block: ||Ghat_e|| <= value",
    "tau": "for every e in the block: (Ghat_e 1)(atom) <= value",
    "Abar": "for every e in the block: E_atom[tau] <= value",
    "D_lo": "for every e in the block: D_e >= value",
    "D1": "for every e in the block: |D_e'| <= value",
    "D2": "for every e in the block: |D_e''| <= value",
}

# How a block-level statement may be assembled from pieces. An UPPER bound over a block is the MAX
# of the pieces' upper bounds and a LOWER bound is the MIN; anything else does not preserve the
# quantifier "for every e in the block". A single certificate over the whole block needs no
# aggregation at all.
VALID_AGGREGATION = {"UPPER_BOUND": {"max_over_sub_blocks", "single_certificate_whole_block"},
                     "LOWER_BOUND": {"min_over_sub_blocks", "single_certificate_whole_block"}}

# Which premises each ROUTE necessarily consumes. A statement whose declared dependencies omit one
# its route requires is internally inconsistent. The independent line never consumes an ORIGINAL
# constant: its C_T and tau are its own.
ROUTE_REQUIRED_DEPENDENCIES = {
    "original_certify_block": frozenset(),
    "original_certify_cell": frozenset({"C_T", "tau"}),
    "independent_supersolution": frozenset(),
    "independent_subsolution": frozenset(),
    "independent_derivative_propagation": frozenset({"C_T_independent", "tau_independent"}),
}
# Which constants a route can PRODUCE at all. A supersolution bounds w(atom) and sup w; it cannot
# bound a drift DERIVATIVE, so a D1 or D2 claimed through it is internally inconsistent even when
# every declared field is honest.
ROUTE_CAN_PRODUCE = {
    "original_certify_block": frozenset({"C_T", "tau", "Abar"}),
    "original_certify_cell": frozenset({"D_lo", "D1", "D2"}),
    "independent_supersolution": frozenset({"C_T", "tau", "Abar"}),
    "independent_subsolution": frozenset({"D_lo"}),
    "independent_derivative_propagation": frozenset({"D_lo", "D1", "D2"}),
}
INDEPENDENT_ROUTES = frozenset({"independent_supersolution", "independent_subsolution",
                                "independent_derivative_propagation"})
FORBIDDEN_PRODUCERS = frozenset({"taboo_certify", "resolvent_certificate", "opnorms",
                                 "ra_certifier", "fast_range", "intervals", "rebaseguard_certify",
                                 "rung3_engine", "spec"})


def statement(constant: str, *, drift_domain: tuple[str, str], aggregation: dict,
              dependencies, producer: dict) -> dict:
    """Build a statement record for one of the six constants, from its semantic identity."""
    k = KERNEL[constant]
    return {"constant": constant, "quantity": QUANTITY[constant], "kernel": k,
            "convention": CONVENTION[k], "direction": DIRECTION[constant],
            "state_set": STATE_SET_R, "proposition": PROPOSITION[constant],
            "drift_domain": [str(F(drift_domain[0])), str(F(drift_domain[1]))],
            "aggregation": dict(aggregation),
            "dependencies": sorted(dependencies),
            "producer": dict(producer)}


# ---------------------------------------------------------------------------------------------
# The target run artifact. Paths are constants; producer and verifiers share them.
# ---------------------------------------------------------------------------------------------
RUNS_SCHEMA = "C11R_RUNS/2"
P_CERTS = "certificates"
P_TARGETS = "targets"
P_SEAL = "seal"
CERT_FIELDS = ("route", "kernel", "family", "screen_classification", "sent_to_box_pass",
               "ladder_level", "depth", "panels", "boxes", "selected", "certified",
               "margin_lower_bound", "w_min_lower_bound", "seconds")
TARGET_STATUS = ("CERTIFIED", "NOT_CERTIFIED", "NOT_IMPLEMENTED")
SCREEN_CLASSES = ("POINTWISE_FEASIBLE", "POINTWISE_INFEASIBLE")


def emit_runs(*, policy_sha256: str, statements_sha256: str, drift_block: tuple[str, str],
              certificates: dict, targets: dict, extra: dict | None = None) -> dict:
    """The ONLY constructor of a runs artifact. c11r_runs.py emits through it; mutants build
    synthetic artifacts through it; so both see exactly one shape."""
    obj = {"schema": RUNS_SCHEMA,
           "policy_sha256": policy_sha256,
           "statements_sha256": statements_sha256,
           "drift_block": [str(F(drift_block[0])), str(F(drift_block[1]))],
           P_CERTS: certificates,
           P_TARGETS: targets,
           P_SEAL: {"sealed_before_comparison": True,
                    "contains_original_magnitudes": False}}
    if extra:
        obj.update(extra)
    problems = validate_runs(obj, check_provenance=False)
    if problems:
        raise ValueError(f"emit_runs would produce an invalid artifact: {problems}")
    return obj


def certificate(**kw) -> dict:
    missing = [f for f in CERT_FIELDS if f not in kw]
    if missing:
        raise ValueError(f"certificate record missing {missing}")
    return {f: kw[f] for f in CERT_FIELDS}


def target(constant: str, *, status: str, value, stmt: dict | None, reason: str | None,
           certificate_id: str | None) -> dict:
    if status not in TARGET_STATUS:
        raise ValueError(f"unknown target status {status!r}")
    return {"constant": constant, "status": status,
            "value": None if value is None else str(F(value)),
            "statement": stmt, "reason": reason, "certificate_id": certificate_id}


# ---------------------------------------------------------------------------------------------
# accessors -- verifiers read ONLY through these
# ---------------------------------------------------------------------------------------------
def certificates(runs: dict) -> dict:
    return runs[P_CERTS]


def targets(runs: dict) -> dict:
    return runs[P_TARGETS]


def cert_depth(cert: dict):
    return cert["depth"]


def cert_sent_to_box_pass(cert: dict) -> bool:
    return bool(cert["sent_to_box_pass"])


def cert_screen_class(cert: dict) -> str:
    return cert["screen_classification"]


def seal_record(runs: dict) -> dict:
    return runs[P_SEAL]


def validate_runs(obj: dict, *, check_provenance: bool = True) -> list[str]:
    """Return a list of structural problems; empty means the artifact has exactly this shape."""
    p = []
    if obj.get("schema") != RUNS_SCHEMA:
        p.append(f"schema is {obj.get('schema')!r}, expected {RUNS_SCHEMA!r}")
    for key in ("policy_sha256", "statements_sha256", "drift_block", P_CERTS, P_TARGETS, P_SEAL):
        if key not in obj:
            p.append(f"missing top-level {key!r}")
    if p:
        return p
    for cid, c in obj[P_CERTS].items():
        for f in CERT_FIELDS:
            if f not in c:
                p.append(f"certificate {cid!r} missing {f!r}")
        if c.get("screen_classification") not in SCREEN_CLASSES:
            p.append(f"certificate {cid!r} has screen class {c.get('screen_classification')!r}")
    if set(obj[P_TARGETS]) != set(SIX_CONSTANTS):
        p.append(f"targets are {sorted(obj[P_TARGETS])}, expected all six")
    for k, t in obj[P_TARGETS].items():
        if t.get("status") not in TARGET_STATUS:
            p.append(f"target {k!r} status {t.get('status')!r}")
        if t.get("status") == "CERTIFIED" and (t.get("value") is None or not t.get("statement")):
            p.append(f"target {k!r} CERTIFIED without a value and statement")
        if t.get("certificate_id") and t["certificate_id"] not in obj[P_CERTS]:
            p.append(f"target {k!r} cites unknown certificate {t['certificate_id']!r}")
    seal = obj[P_SEAL]
    if seal.get("contains_original_magnitudes") is not False:
        p.append("seal does not declare the artifact free of original magnitudes")
    if check_provenance:
        prov = obj.get("provenance")
        if not prov or not prov.get("producer_sha256"):
            p.append("missing provenance.producer_sha256")
        if not obj.get("sha256"):
            p.append("missing sha256")
    return p
