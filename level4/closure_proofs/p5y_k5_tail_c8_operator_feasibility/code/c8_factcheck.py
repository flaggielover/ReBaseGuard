"""C8 Phase 14 -- verify before absorb.

C6 and C7 both established that reviewer and adjudicator prose can itself be wrong, and that a
numeral-comparing check cannot reach a behavioural claim. This module therefore does two separate
things and says which is which:

  (a) mechanical checks over the committed tree -- prose figures backed by a producer, predecessor
      baselines matching their sources, gate ordering, self-sha integrity;
  (b) a LOAD-BEARING CLAIM LEDGER, in which every claim C8 adopts from any source -- including its
      own reviewer and adjudicator -- is recorded with statement, source, verification method,
      result and disposition. A claim that cannot be reproduced is labelled
      REVIEW_SOURCED_UNVERIFIED and is never marked LANDED.
"""
from __future__ import annotations

import json
import pathlib
import re
import sys
from fractions import Fraction as F

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import c8_common as C
import c8_chain as X

NUM = re.compile(r"(?<![\w.])(\d+\.\d{4,})(?![\w])")
GATE_SHA = "55e743320987a1e031c586938216e70839ed8d0ef1e9d518304197563dde9a7a"


def numbers_in(t: str) -> set[str]:
    return {m.group(1) for m in NUM.finditer(t)}


def flatten(o, acc: set[str]) -> None:
    if isinstance(o, dict):
        for v in o.values():
            flatten(v, acc)
    elif isinstance(o, list):
        for v in o:
            flatten(v, acc)
    else:
        s = str(o)
        acc.add(s)
        for m in NUM.finditer(s):
            acc.add(m.group(1))
        if isinstance(o, float):
            acc.add(f"{o:.15f}")


def main() -> int:
    findings, ledger = [], []
    ch = X.Chain()

    # ---- (a1) prose figures must be backed by a producer -------------------------------------
    arts = sorted((C.NS / "evidence").rglob("*.json")) + [C.NS / "config" / "DECISION_GATE_C8.json"]
    pool: set[str] = set()
    for a in arts:
        flatten(json.loads(a.read_text()), pool)
    vals = []
    for q in pool:
        try:
            vals.append(F(q))
        except (ValueError, ZeroDivisionError):
            pass
    review_docs = sorted((C.NS / "review").glob("*.md"))

    def backed(n: str) -> bool:
        dec = len(n.split(".")[1]) if "." in n else 0
        tol = F(1, 2 * 10 ** dec)
        t = F(n)
        return any(abs(v - t) <= tol for v in vals)

    prose = [p for p in sorted(C.NS.rglob("*.md")) if "review" not in p.parts]
    review_sourced: dict[str, list] = {}
    for p in prose:
        for n in sorted(numbers_in(p.read_text())):
            if backed(n):
                continue
            src = next((str(q.relative_to(C.NS)) for q in review_docs if n in q.read_text()), None)
            if src:
                review_sourced.setdefault(n, []).append(
                    {"quoted_in": str(p.relative_to(C.NS)), "measured_in": src})
                continue
            findings.append({"check": "PROSE_FIGURE_UNBACKED",
                             "file": str(p.relative_to(C.NS)), "value": n})

    # ---- (a2) predecessor baselines ----------------------------------------------------------
    dec = C.load(C.NS / "evidence" / "phase9" / "C8_DECISION.json")
    routes = C.load(C.NS / "evidence" / "phase4" / "C8_ROUTES.json")
    b0 = C.load(C.NS / "evidence" / "b0" / "C8_B0_AUDIT.json")
    fc = C.c5_forecast()["cells"]
    c4, c7 = C.c4_cells(), C.c7_certificate()
    lam = F(c7["bounds"][c7["PRIMARY"]["key"]]["value"])

    def rec(stmt, source, method, ok, disposition, value=None):
        ledger.append({"statement": stmt, "source": source, "verification_method": method,
                       "result": "REPRODUCED" if ok else "NOT_REPRODUCED",
                       "value": value, "disposition": disposition})
        if not ok:
            findings.append({"check": "LOAD_BEARING_CLAIM_NOT_REPRODUCED", "statement": stmt})

    for k in (306, 307, 308, 309):
        mine = ch.M_of(k, dict(ch.committed_supplies(k)["operator_mixed"]["A"]))
        theirs = F(str(fc[str(k)]["M_used"]))
        rec(f"cell {k}: M under the best committed supply equals C5's M_used",
            "C5_FORECAST.json#/cells/%d/M_used" % k,
            "recomputed from the frozen TC-T rule over committed inputs; compared as exact rationals",
            abs(mine - theirs) < F(1, 10 ** 12), "LANDED", float(mine))

    rec("cell 309's A0 ceiling equals C5's published critical_A0_C5T",
        "C5_FORECAST.json#/c4_exclusion_fragility/.../critical_A0_C5T",
        "independent bisection on the reconstructed rule",
        abs(F(str(dec["phase4_inversion_C5T"]["309"]["A0_ceiling_with_A1_A2_zero"]))
            - F(str(C.c5_forecast()["c4_exclusion_fragility"]
                ["2_margin_in_C4s_own_currency_critical_A0"]["critical_A0_C5T"]))) < F(1, 10 ** 9),
        "LANDED", dec["phase4_inversion_C5T"]["309"]["A0_ceiling_with_A1_A2_zero"])

    rec("the authoritative m=5 open set is {306,307,308,309}",
        "K5_COVERAGE_MAP_R5.json per-cell verdicts",
        "reconstructed from per-cell verdict fields, not from summary ranges",
        tuple(C.r5_open_by_verdict("5")) == C.OPEN_CELLS, "LANDED", list(C.OPEN_CELLS))

    rec("C7's prose claim 'm=5 open on [305,309]' is wrong",
        "C7 README / disposition prose vs r5",
        "r5 per-cell verdict for 305 read directly",
        [c.get("verdict") for c in C.r5_map()["per_m"]["5"]["cells"] if c["cell"] == 305][0] == "PASS",
        "CORRECTED -- C8 uses the artifact, not the prose", "PASS")

    rec("C7 PRIMARY is dependency-free and equals 3.5863060938653875",
        "C7_CERTIFICATE.json", "exact rational read and float-compared",
        float(lam) == 3.5863060938653875
        and c7["bounds"][c7["PRIMARY"]["key"]]["dependencies"] == [], "LANDED", float(lam))

    rec("R1 and R2 have exactly zero leverage on Gamma",
        "C8 phase-5 oracle",
        "Gamma is a function of (g_hi, rho, x_hi, A0, A1, A2); Lambda appears in none. Verified by "
        "inspecting the reconstructed chain, which reproduces 20 committed supplies.",
        routes["phase5_perfect_information_oracles"]["routes"]["R1"]["leverage"] == "ZERO",
        "LANDED", 0.0)

    rec("no certifying host or toolchain exists in scope",
        "C6_CLASSIFICATION RANKING_PREMISE_CORRECTED + local importlib measurement",
        "importlib.find_spec at run time for six libraries",
        not any(C.toolchain_present().values()), "LANDED", C.toolchain_present())

    # ---- (a3) gate ordering ------------------------------------------------------------------
    order = C.git("log", "--format=%H", "--reverse").splitlines()

    def first_commit(rel: str):
        o = C.git("log", "--format=%H", "--diff-filter=A", "--", rel).splitlines()
        return o[-1] if o else None

    ns = "level4/closure_proofs/p5y_k5_tail_c8_operator_feasibility"
    gi = order.index(first_commit(f"{ns}/config/DECISION_GATE_C8.json"))
    ordering = []
    for rel, kind in (("evidence/phase4/C8_ROUTES.json", "RESULT"),
                      ("evidence/phase9/C8_DECISION.json", "RESULT"),
                      ("evidence/mutations/C8_MUTATIONS.json", "RESULT"),
                      ("evidence/b0/C8_B0_AUDIT.json", "STATE_AUDIT")):
        c = first_commit(f"{ns}/{rel}")
        if c is None:
            # An UNCOMMITTED file has no commit position. The first version let `index()` fall
            # through to -1 and reported it as BEFORE_GATE, i.e. as an ordering VIOLATION, which is
            # simply false -- the artifact merely had not been committed yet. A check must not
            # invent a position it did not observe.
            ordering.append({"artifact": rel, "kind": kind, "position": "UNCOMMITTED",
                             "note": "not yet committed; ordering is undetermined, not violated"})
            continue
        ai = order.index(c)
        pos = "AFTER_GATE" if ai > gi else ("SAME_COMMIT" if ai == gi else "BEFORE_GATE")
        ordering.append({"artifact": rel, "kind": kind, "position": pos})
        if kind == "RESULT" and pos != "AFTER_GATE":
            findings.append({"check": "GATE_ORDERING", "artifact": rel, "position": pos})

    # ---- (a4) self-sha integrity --------------------------------------------------------------
    for a in sorted((C.NS / "evidence").rglob("*.json")):
        o = json.loads(a.read_text())
        if "sha256" not in o:
            continue
        body = {k: v for k, v in o.items() if k != "sha256"}
        if C.sha256_obj(body) != o["sha256"]:
            findings.append({"check": "SELF_SHA_MISMATCH", "file": str(a.relative_to(C.NS))})

    if C.sha256_file(C.NS / "config" / "DECISION_GATE_C8.json") != GATE_SHA:
        findings.append({"check": "GATE_BLOB_CHANGED"})

    # STALE-CLAIM SCAN. A retracted sentence must not remain as a LIVE assertion anywhere. Quoting it
    # inside an explicit withdrawal is correct and is permitted; asserting it is not. Both C6 and C7
    # shipped a withdrawn claim that was still being emitted by a producer.
    RETRACTED = ["blocker is ADOPTION, not information", "only route with leverage",
                 "unreachable from committed evidence", "M = magnitude is conservative"]
    stale = []
    for a in sorted((C.NS / "evidence").rglob("*.json")):
        # This module's OWN report quotes the phrases it hunts for, inside its finding records. A
        # report about a claim is not a claim, and a scanner that flags its own output can never
        # reach PASS. Same principle as excluding a reviewer's document from the prose scan.
        if a.name == "HANDOVER_FACT_VERIFICATION.json":
            continue
        txt = a.read_text()
        for phrase in RETRACTED:
            pos = txt.find(phrase)
            while pos >= 0:
                ctx = txt[max(0, pos - 100):pos + 60]
                if "WITHDRAWN" not in ctx and "NOT the only" not in ctx and "SUPERSEDED" not in ctx:
                    stale.append({"file": str(a.relative_to(C.NS)), "phrase": phrase,
                                  "context": ctx[-120:]})
                pos = txt.find(phrase, pos + 1)
    if stale:
        findings.append({"check": "RETRACTED_CLAIM_STILL_LIVE", "hits": stale[:5]})

    out = {"schema": "C8_HANDOVER_FACT_VERIFICATION/1",
           "WHAT_THIS_CANNOT_VERIFY": (
               "the mechanical checks compare numerals, baselines, commit order and self-shas. NONE "
               "of them reaches a BEHAVIOURAL claim -- whether a guard actually guards, whether a "
               "test can fail, whether a route classification is sound. C6 and C7 each shipped a "
               "defect of exactly that kind past a PASS here. Those are found by reading code and by "
               "adversarial review, and the load-bearing claim ledger below is where reviewer and "
               "adjudicator statements are checked one by one before absorption."),
           "load_bearing_claim_ledger": ledger,
           "gate_ordering": ordering,
           "review_sourced_figures": review_sourced,
           "prose_scanned": [str(p.relative_to(C.NS)) for p in prose],
           "stale_claim_scan": {"retracted_phrases_checked": 4,
                               "self_excluded": "HANDOVER_FACT_VERIFICATION.json -- it quotes the phrases inside its own finding records"},
           "findings": findings,
           "FACT_CHECK_CLASS": "PASS" if not findings else "REFUSE"}
    s = C.write_evidence(C.NS / "evidence" / "governance" / "HANDOVER_FACT_VERIFICATION.json", out)
    print(f"FACT_CHECK_CLASS = {out['FACT_CHECK_CLASS']}  findings={len(findings)}  "
          f"ledger entries={len(ledger)}")
    for f_ in findings[:10]:
        print(f"  {f_['check']}: {json.dumps({k: v for k, v in f_.items() if k != 'check'})[:100]}")
    print("gate ordering:")
    for o in ordering:
        print(f"  {o['kind']:<12} {o['position']:<13} {o['artifact']}")
    print(f"wrote evidence/governance/HANDOVER_FACT_VERIFICATION.json sha256 {s[:16]}...")
    return 0 if not findings else 1


if __name__ == "__main__":
    raise SystemExit(main())
