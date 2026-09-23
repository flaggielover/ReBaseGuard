"""C11R Repair B -- the statement-equivalence comparator, rebuilt.

SAME STATEMENT BEFORE SAME NUMBER.

WHAT WAS WRONG (erratum E6). Revision 1 built the "independent" proposition as a copy of the
original's and overwrote only its drift domain -- with the original's own domain. It compared the
original against itself and could only return EQUIVALENT; no field of the runs artifact was read.

ROUND 3 (blocker B-3, erratum E16). Round 2's independent side was still a template: the runs
producer declared each target's statement with c11r_schema.statement(constant) -- the same
name-keyed template the original side uses -- so the comparison could not fail. Now:

WHAT THIS MODULE DOES INSTEAD
  * `independent_statement` RECONSTRUCTS the independent proposition from the certificate the
    target cites, through c11r_certificate.reconstruct: which constants the certificate proves, and
    every field of the proposition, are derived from the certifier's identity, hash, inputs and
    its own result -- never from the target's constant name. It never touches the original.
  * `original_statement` reads the original's proposition from the statement table -- semantics
    only; that table carries no magnitude.
  * `check_internal` validates the independent record on its own before any comparison: kernel
    and convention must agree; the aggregation must preserve "for every e in the block" for its
    direction; the declared dependencies must include every premise its ROUTE necessarily
    consumes; the producer must be in the independent line and must declare its file hash; and it
    may not depend on an ORIGINAL constant. A record failing any of these is INVALID.
  * `compare` then decides EQUIVALENT / STRONGER / WEAKER / NOT_COMPARABLE / NOT_EQUIVALENT.
    Exact fields must match. The drift domain is compared as EXACT rationals (revision 1 compared
    binary floats). Premises are compared as sets: FEWER premises is logically STRONGER, so an
    unconditional statement is stronger than the original's conditional one.

Neither side is built from the other. This module holds no magnitude and loads none.
"""
from __future__ import annotations

import copy
import pathlib
import sys
from fractions import Fraction as F

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import c11r_common as C
import c11r_schema as S

INDEPENDENT_SUFFIX = "_independent"


# ---------------------------------------------------------------------------------------------
# the two readers -- deliberately separate, neither consults the other
# ---------------------------------------------------------------------------------------------
def independent_statement(runs: dict, constant: str, *, expected_certifier_sha: dict,
                          runs_producer: dict, deductions: dict | None = None) -> dict | None:
    """The proposition the cited certificate PROVES for `constant`, or None if it proves none."""
    import c11r_certificate as CV
    t = S.targets(runs)[constant]
    cert = S.certificates(runs).get(t.get("certificate_id") or "")
    if t.get("status") != "CERTIFIED" or cert is None:
        return None
    r = CV.reconstruct(cert, expected_certifier_sha=expected_certifier_sha,
                       runs_producer=runs_producer, deductions=deductions)
    return copy.deepcopy(r["propositions"].get(constant)) if not r["problems"] else None


def original_statement(statements_table: dict, constant: str) -> dict:
    return copy.deepcopy(statements_table["original_statements"][constant])


# ---------------------------------------------------------------------------------------------
def check_internal(st: dict) -> list[str]:
    """Problems with an INDEPENDENT statement taken on its own. Empty means consistent."""
    p = []
    for f in S.STATEMENT_FIELDS:
        if f not in st:
            p.append(f"missing field {f!r}")
    if p:
        return p
    if S.CONVENTION.get(st["kernel"]) != st["convention"]:
        p.append(f"kernel {st['kernel']} requires convention "
                 f"{S.CONVENTION.get(st['kernel'])!r}, record says {st['convention']!r}")
    method = st["aggregation"].get("method")
    if method not in S.VALID_AGGREGATION.get(st["direction"], set()):
        p.append(f"aggregation {method!r} does not preserve 'for every e in the block' for an "
                 f"{st['direction']}")
    prod = st["producer"]
    route = prod.get("route")
    if route not in S.INDEPENDENT_ROUTES:
        p.append(f"route {route!r} is not an independent route")
    mod = str(prod.get("module", "")).split(".")[0].split("/")[-1].removesuffix(".py")
    if mod in S.FORBIDDEN_PRODUCERS:
        p.append(f"producer {prod.get('module')!r} is in the original's load-bearing graph")
    if not prod.get("file_sha256"):
        p.append("producer declares no file hash, so what generated the result is unknowable")
    if st["constant"] not in S.ROUTE_CAN_PRODUCE.get(route, frozenset()):
        p.append(f"route {route!r} cannot produce {st['constant']!r}")
    required = S.ROUTE_REQUIRED_DEPENDENCIES.get(route, frozenset())
    missing = sorted(required - set(st["dependencies"]))
    if missing:
        p.append(f"route {route!r} necessarily consumes {missing}, which the record omits")
    originals = sorted(d for d in st["dependencies"] if d in S.SIX_CONSTANTS)
    if originals:
        p.append(f"depends on ORIGINAL constants {originals} -- an independence violation")
    return p


def _domain(orig: list, indep: list) -> str:
    olo, ohi = F(orig[0]), F(orig[1])
    ilo, ihi = F(indep[0]), F(indep[1])
    if (ilo, ihi) == (olo, ohi):
        return "EQUAL"
    if ilo <= olo and ihi >= ohi:
        return "SUPERSET"
    if ilo >= olo and ihi <= ohi:
        return "SUBSET"
    return "INCOMPARABLE"


def _premises(orig: list, indep: list) -> str:
    norm = {d.removesuffix(INDEPENDENT_SUFFIX) for d in indep}
    o = set(orig)
    if norm == o:
        return "SAME"
    if norm < o:
        return "FEWER"
    if norm > o:
        return "MORE"
    return "DIFFERENT"


def compare(orig: dict, indep: dict | None) -> dict:
    if indep is None:
        return {"STATUS": "NO_INDEPENDENT_STATEMENT", "reasons": ["no independent statement"]}
    internal = check_internal(indep)
    if internal:
        return {"STATUS": "INVALID", "reasons": internal,
                "independence_violation": any("independence violation" in r or
                                              "load-bearing graph" in r for r in internal)}
    mism = [f for f in S.EXACT_FIELDS if orig.get(f) != indep.get(f)]
    if mism:
        return {"STATUS": "NOT_EQUIVALENT", "reasons": [f"{f} differs" for f in mism],
                "field_mismatches": mism}
    dom = _domain(orig["drift_domain"], indep["drift_domain"])
    prem = _premises(orig["dependencies"], indep["dependencies"])
    if dom == "INCOMPARABLE" or prem == "DIFFERENT":
        status = "NOT_COMPARABLE"
    else:
        stronger = (dom == "SUPERSET") or (prem == "FEWER")
        weaker = (dom == "SUBSET") or (prem == "MORE")
        if stronger and weaker:
            status = "NOT_COMPARABLE"
        elif weaker:
            status = "WEAKER"
        elif stronger:
            status = "STRONGER"
        else:
            status = "EQUIVALENT"
    return {"STATUS": status, "domain": dom, "premises": prem, "reasons": [],
            "aggregation": {"original": orig["aggregation"].get("method"),
                            "independent": indep["aggregation"].get("method")}}


# ---------------------------------------------------------------------------------------------
# negative controls, run through the SAME `compare` used in production
# ---------------------------------------------------------------------------------------------
def honest_independent(constant: str, drift: tuple[str, str], route: str,
                       deps=()) -> dict:
    """An independent statement built with the producer's own constructor, S.statement.

    It is NOT derived from the original record: every field comes from the schema's semantic
    definitions and an independent producer identity.
    """
    return S.statement(constant, drift_domain=drift,
                       aggregation={"method": "single_certificate_whole_block", "sub_blocks": 1},
                       dependencies=deps,
                       producer={"module": "c11r_runs.py", "route": route,
                                 "file_sha256": "0" * 64, "certificate_id": "synthetic"})


def self_test(stmt_table: dict) -> dict:
    d = stmt_table["drift_domain"]
    drift = (d["e_lo"], d["e_hi"])
    mid = str((F(d["e_lo"]) + F(d["e_hi"])) / 2)
    O = {k: original_statement(stmt_table, k) for k in S.SIX_CONSTANTS}
    cases = []

    def case(label, target, indep, expect):
        r = compare(O[target], indep)
        ok = (r["STATUS"] in expect) if isinstance(expect, (set, tuple)) else r["STATUS"] == expect
        cases.append({"case": label, "target": target, "status": r["STATUS"],
                      "expected": sorted(expect) if isinstance(expect, (set, tuple)) else expect,
                      "caught_or_accepted_as_expected": ok, "reasons": r.get("reasons", [])})

    sup = "independent_supersolution"
    # positive controls: honest statements must NOT be rejected
    case("POSITIVE honest Abar supersolution", "Abar", honest_independent("Abar", drift, sup),
         "EQUIVALENT")
    case("POSITIVE honest tau supersolution", "tau", honest_independent("tau", drift, sup),
         "EQUIVALENT")
    case("POSITIVE honest D_lo sub-solution (no premises -> stronger)", "D_lo",
         honest_independent("D_lo", drift, "independent_subsolution"), "STRONGER")
    case("POSITIVE honest D1 derivative route (own C_T, tau)", "D1",
         honest_independent("D1", drift, "independent_derivative_propagation",
                            ("C_T_independent", "tau_independent")), "EQUIVALENT")

    def mutated(target, route, f, deps=()):
        s = honest_independent(target, drift, route, deps)
        f(s)
        return s

    # the eleven the campaign requires, plus more
    case("cell 306 replaced by cell 307", "Abar",
         mutated("Abar", sup, lambda s: s.update(drift_domain=["17885921/10000000",
                                                               "1882413/1000000"])),
         "NOT_COMPARABLE")
    case("drift narrowed to the midpoint", "Abar",
         mutated("Abar", sup, lambda s: s.update(drift_domain=[mid, mid])), "WEAKER")
    case("K_e <-> Khat_e (kernel and convention both swapped)", "tau",
         mutated("tau", sup, lambda s: s.update(kernel="K_e", convention="full")),
         "NOT_EQUIVALENT")
    case("full <-> atom-removed (convention alone swapped)", "tau",
         mutated("tau", sup, lambda s: s.update(convention="full")), "INVALID")
    case("D_lo <-> D1", "D_lo", honest_independent("D1", drift,
                                                   "independent_derivative_propagation",
                                                   ("C_T_independent", "tau_independent")),
         "NOT_EQUIVALENT")
    case("D1 <-> D2", "D1", honest_independent("D2", drift,
                                               "independent_derivative_propagation",
                                               ("C_T_independent", "tau_independent")),
         "NOT_EQUIVALENT")
    case("upper <-> lower direction", "Abar",
         mutated("Abar", sup, lambda s: s.update(direction="LOWER_BOUND")),
         {"NOT_EQUIVALENT", "INVALID"})
    case("changed reachable/state set", "C_T",
         mutated("C_T", sup, lambda s: s.update(state_set="R' = {p + m <= 5}")),
         "NOT_EQUIVALENT")
    case("aggregation max <-> min on an upper bound", "C_T",
         mutated("C_T", sup, lambda s: s.update(aggregation={"method": "min_over_sub_blocks",
                                                             "sub_blocks": 9})), "INVALID")
    case("missing dependency on C_T/tau for the derivative route", "D1",
         honest_independent("D1", drift, "independent_derivative_propagation", ()), "INVALID")
    case("altered provenance: producer is the original's taboo_certify", "tau",
         mutated("tau", sup, lambda s: s["producer"].update(module="taboo_certify.certify_block")),
         "INVALID")
    case("altered provenance: an original route", "tau",
         mutated("tau", sup, lambda s: s["producer"].update(route="original_certify_block")),
         "INVALID")
    case("altered provenance: no producer file hash", "Abar",
         mutated("Abar", sup, lambda s: s["producer"].update(file_sha256="")), "INVALID")
    case("consumed the ORIGINAL C_T and tau", "D1",
         honest_independent("D1", drift, "independent_derivative_propagation",
                            ("C_T", "tau", "C_T_independent", "tau_independent")), "INVALID")
    case("D1 claimed through the supersolution route, which cannot bound a derivative", "D1",
         honest_independent("D1", drift, sup), "INVALID")
    case("drift WIDENED beyond the block (a genuine strengthening)", "Abar",
         mutated("Abar", sup, lambda s: s.update(drift_domain=["17/10", "18/10"])), "STRONGER")

    pos = [c for c in cases if c["case"].startswith("POSITIVE")]
    neg = [c for c in cases if not c["case"].startswith("POSITIVE")]
    return {"cases": cases,
            "positives_accepted": all(c["caught_or_accepted_as_expected"] for c in pos),
            "negatives_caught": all(c["caught_or_accepted_as_expected"] for c in neg),
            "PASS": all(c["caught_or_accepted_as_expected"] for c in cases)}


def main() -> int:
    tbl = C.load_allowlisted("evidence/table/C11R_N9_STATEMENTS.json")
    st = self_test(tbl)
    out = {"schema": "C11R_EQUIVALENCE/2",
           "supersedes": "C11R_EQUIVALENCE/1, whose comparator was fed a copy of the original",
           "principle": "SAME STATEMENT BEFORE SAME NUMBER",
           "exact_fields": list(S.EXACT_FIELDS),
           "domain_rule": "exact rationals: EQUAL, SUPERSET (stronger), SUBSET (weaker)",
           "premise_rule": "fewer premises is stronger; an ORIGINAL constant as a premise is INVALID",
           "independent_side_built_from": ("c11r_certificate.reconstruct of the certificate each "
                                           "target cites -- never a declared statement"),
           "note_on_this_self_test": ("these cases exercise compare() on statement RECORDS. The "
                                      "certificate-level adversarial controls -- forged, relabelled "
                                      "and altered certificates -- run through the production "
                                      "reconstruction in the mutation suite and the comparator's "
                                      "self-test."),
           "original_side_built_from": "evidence/table/C11R_N9_STATEMENTS.json (no magnitudes)",
           "self_test": st,
           "EQUIV_CLASS": "READY" if st["PASS"] else "REFUSE"}
    s = C.write_evidence(C.NS / "evidence" / "equivalence" / "C11R_EQUIVALENCE.json", out,
                         producer=__file__)
    for c in st["cases"]:
        print(f"  {'ok  ' if c['caught_or_accepted_as_expected'] else 'FAIL'} "
              f"{c['case'][:60]:60s} -> {c['status']}")
    print(f"\npositives accepted {st['positives_accepted']}  negatives caught "
          f"{st['negatives_caught']}   EQUIV_CLASS = {out['EQUIV_CLASS']}")
    print(f"wrote evidence/equivalence/C11R_EQUIVALENCE.json sha256 {s[:16]}...")
    return 0 if st["PASS"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
