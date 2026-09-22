"""C11R Phase 2 -- the statement-equivalence checker.

SAME STATEMENT BEFORE SAME NUMBER. A second certifier corroborates the first only if it proves the
same proposition, or a strictly stronger one. Numerical similarity is not evidence of anything if
the two sides are bounding different quantities, on different kernels, at different states, over
different drift domains, or in different directions.

A proposition is recorded as a tuple of fields that must MATCH EXACTLY:

    kernel          K_e or Khat_e        -- C11 proved K_e and compared against a Khat_e constant
    quantity        w(atom) or sup_R w   -- tau and C_T come from the SAME certificate
    state           the atom, or a set
    direction       UPPER_BOUND or LOWER_BOUND   -- D_lo is the only lower bound of the six
    bounds          the object being bounded

and one field that must match OR IMPROVE:

    drift_domain    the independent domain must CONTAIN the original's; a proper superset is
                    STRONGER, a proper subset is WEAKER, anything else is NOT_COMPARABLE.

Every comparison here is computed, and the checker is exercised against planted mismatches so that
it is shown to be able to fail.
"""
from __future__ import annotations

import pathlib
import sys
from fractions import Fraction as F

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import c11r_common as C

EXACT_FIELDS = ("kernel", "quantity", "state", "direction", "bounds")


def _interval(d) -> tuple[F, F]:
    return F(d[0]), F(d[1])


def compare_domains(orig, indep) -> tuple[str, str]:
    (olo, ohi), (ilo, ihi) = _interval(orig), _interval(indep)
    if (ilo, ihi) == (olo, ohi):
        return "EQUAL", "the independent domain is exactly the original's"
    if ilo <= olo and ihi >= ohi:
        return "SUPERSET", "the independent domain strictly contains the original's"
    if ilo >= olo and ihi <= ohi:
        return "SUBSET", ("the independent domain is contained in the original's, so it proves "
                          "strictly less and cannot corroborate the original's statement")
    return "INCOMPARABLE", "the domains overlap partially or not at all"


def check(name: str, orig: dict, indep: dict | None) -> dict:
    """Compare one target's two propositions. Returns a status and the reasons for it."""
    if indep is None:
        return {"target": name, "STATUS": "NO_INDEPENDENT_STATEMENT",
                "reason": ("this campaign produced no independent proposition for this constant, "
                           "so there is nothing to compare; it cannot contribute to N9 closure"),
                "field_mismatches": None, "domain": None}
    mism = [{"field": f, "original": orig.get(f), "independent": indep.get(f)}
            for f in EXACT_FIELDS if orig.get(f) != indep.get(f)]
    dom, dom_why = compare_domains(orig["drift_domain"], indep["drift_domain"])
    if mism:
        status = "NOT_EQUIVALENT"
    elif dom == "EQUAL":
        status = "EQUIVALENT"
    elif dom == "SUPERSET":
        status = "STRONGER"
    elif dom == "SUBSET":
        status = "WEAKER"
    else:
        status = "NOT_COMPARABLE"
    return {"target": name, "STATUS": status,
            "field_mismatches": mism,
            "domain": {"comparison": dom, "why": dom_why,
                       "original": orig["drift_domain"], "independent": indep["drift_domain"]},
            "reason": ("every exact field matches and " + dom_why) if not mism else
                      f"{len(mism)} exact field(s) differ: {[m['field'] for m in mism]}"}


def original_propositions(tbl: dict) -> dict:
    """The original's six propositions, from the Phase 1 table -- not restated by hand."""
    # The quantity field must DISTINGUISH the six. An earlier draft derived it from the state
    # convention, which collapsed D_lo, D1 and D2 onto one label -- so swapping D1 for D2 would
    # have passed the exact-field check on quantity and been caught only by direction. The
    # quantity is now the constant's own name plus what it bounds, which cannot collide.
    QUANTITY = {
        "C_T": "sup_over_R of w",
        "tau": "w(atom), atom-removed supersolution",
        "Abar": "w(atom), whole-kernel supersolution",
        "D_lo": "d(atom) = P_a(tau < T_a)",
        "D1": "|d'(atom)|, first drift derivative",
        "D2": "|d''(atom)|, second drift derivative",
    }
    out = {}
    for k, v in tbl["constants"].items():
        q = QUANTITY.get(k)
        if q is None:
            raise SystemExit(f"REFUSE: no distinct quantity label for constant {k!r}")
        out[k] = {"kernel": v["kernel"],
                  "quantity": q,
                  "state": "atom" if "atom" in v["state_convention"] else "reachable_set",
                  "direction": v["direction"],
                  "bounds": v["bounds"],
                  "drift_domain": v["drift_domain_float"]}
    if len({v["quantity"] for v in out.values()}) != len(out):
        raise SystemExit("REFUSE: quantity labels are not distinct across the six constants")
    return out


def self_test(orig: dict) -> dict:
    """Negative controls. A checker that cannot fail proves nothing (C8/C11 lesson)."""
    base = dict(orig["Abar"])
    cases = []

    def case(label, mutate, expect_not):
        m = dict(base)
        mutate(m)
        r = check("Abar", orig["Abar"], m)
        cases.append({"planted": label, "status": r["STATUS"],
                      "caught": r["STATUS"] != expect_not})

    case("identical proposition", lambda m: None, None)
    case("Khat_e swapped for K_e", lambda m: m.update(kernel="Khat_e"), "EQUIVALENT")
    case("tau's quantity swapped in", lambda m: m.update(quantity="sup_R_w"), "EQUIVALENT")
    case("direction flipped to LOWER_BOUND",
         lambda m: m.update(direction="LOWER_BOUND"), "EQUIVALENT")
    case("state moved off the atom", lambda m: m.update(state="reachable_set"), "EQUIVALENT")
    case("drift narrowed to the midpoint",
         lambda m: m.update(drift_domain=[1.7452573, 1.7452573]), "EQUIVALENT")
    case("drift narrowed to one endpoint",
         lambda m: m.update(drift_domain=[1.7019225, 1.7019225]), "EQUIVALENT")
    case("drift replaced by cell 307's block",
         lambda m: m.update(drift_domain=[1.7885921, 1.882413]), "EQUIVALENT")

    # the six must also be distinguishable FROM EACH OTHER, not merely from a mutated Abar
    for a, b in (("D1", "D2"), ("D_lo", "D1"), ("tau", "Abar"), ("tau", "C_T")):
        r = check(a, orig[a], orig[b])
        cases.append({"planted": f"{b} substituted for {a}", "status": r["STATUS"],
                      "caught": r["STATUS"] != "EQUIVALENT"})
    identical_ok = cases[0]["status"] == "EQUIVALENT"
    all_caught = all(c["caught"] for c in cases[1:])
    return {"identical_case_is_EQUIVALENT": identical_ok,
            "all_planted_mismatches_caught": all_caught,
            "cases": cases,
            "PASS": identical_ok and all_caught}


def main() -> int:
    tbl = C.load(C.NS / "evidence" / "table" / "C11R_N9_TABLE.json")
    orig = original_propositions(tbl)
    st = self_test(orig)
    out = {"schema": "C11R_EQUIVALENCE/1",
           "principle": "SAME STATEMENT BEFORE SAME NUMBER",
           "exact_match_fields": list(EXACT_FIELDS),
           "domain_rule": ("the independent drift domain must contain the original's; "
                           "EQUAL -> EQUIVALENT, SUPERSET -> STRONGER, SUBSET -> WEAKER"),
           "original_propositions": orig,
           "checker_self_test": st,
           "EQUIV_CLASS": "READY" if st["PASS"] else "REFUSE"}
    s = C.write_evidence(C.NS / "evidence" / "equivalence" / "C11R_EQUIVALENCE.json", out)
    print("original propositions:")
    for k, v in orig.items():
        print(f"  {k:5s} kernel={v['kernel']:7s} quantity={v['quantity']:11s} "
              f"state={v['state']:13s} dir={v['direction']}")
    print("\nchecker self-test (negative controls):")
    for c in st["cases"]:
        print(f"  {'OK ' if c['caught'] else 'MISS'}  {c['planted']:38s} -> {c['status']}")
    print(f"\nEQUIV_CLASS = {out['EQUIV_CLASS']}")
    print(f"wrote evidence/equivalence/C11R_EQUIVALENCE.json sha256 {s[:16]}...")
    return 0 if st["PASS"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
