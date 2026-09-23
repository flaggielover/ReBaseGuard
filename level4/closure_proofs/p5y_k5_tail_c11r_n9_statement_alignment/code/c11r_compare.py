"""C11R Phase 15 -- the sealed comparison. Rebuilt in revision 2 (erratum E6).

ONE OF EXACTLY TWO MODULES PERMITTED TO LOAD AN ORIGINAL MAGNITUDE, and it does so only inside
`load_original_magnitudes`, which only `main` calls, and only after `verify_seal` has passed.

ORDER OF OPERATIONS IN `main`, and why it cannot be reordered silently:
  1. verify the seal -- the runs artifact is committed, the file on disk is the committed blob, it
     has no uncommitted change, it has exactly the frozen run schema, its producer hash equals the
     committed c11r_runs.py at the seal commit, and it declares and contains no original magnitude;
  2. build every INDEPENDENT statement from the runs artifact's own target records;
  3. only then load the ORIGINAL statements (semantics) and the ORIGINAL magnitudes (quarantine);
  4. classify each target -- statement first, number second;
  5. derive the N9 classification by a frozen precedence, and only then render any prose.

NOTHING HERE IS A PRE-WRITTEN CONCLUSION. Revision 1 carried "agreement is established" and "No
target is INVALID and none DISAGREES" before any run existed. Every sentence this module emits is
rendered from computed fields by `render`, and the mutation suite scans this module's own string
constants for result-dependent language.

DISAGREES IS A REAL RETURN. It arises when an independent rigorous bound EXCLUDES the original's
claim on the same quantity -- an independent upper bound below an original lower bound, or an
independent lower bound above an original upper bound. Two bounds in the same direction cannot
contradict. Whether any such opposite-direction pair exists in a given runs artifact is COMPUTED
here (`opposite_direction_pairs`), not asserted.
"""
from __future__ import annotations

import pathlib
import sys
from fractions import Fraction as F

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import c11r_common as C
import c11r_equiv as EQ
import c11r_schema as S

RUNS_REL = "evidence/runs/C11R_RUNS.json"
FACTOR = 2
PRECEDENCE = ("INDEPENDENCE_VIOLATION", "SCIENTIFIC_DISAGREEMENT", "EXECUTION_INVALID",
              "N9_CLOSED", "AGREEMENT_INSUFFICIENT")


# ---------------------------------------------------------------------------------------------
# 1. the seal
# ---------------------------------------------------------------------------------------------
def verify_seal_bytes(disk: bytes | None, committed: bytes | None, dirty: bool) -> list[str]:
    """Pure seal check, testable without any runs artifact existing."""
    p = []
    if disk is None:
        p.append("no runs artifact on disk")
    if committed is None:
        p.append("the runs artifact was never committed, so no ordering can be established")
    if disk is not None and committed is not None and disk != committed:
        p.append("the file on disk differs from the committed blob")
    if dirty:
        p.append("the runs artifact has uncommitted changes")
    return p


def verify_seal() -> dict:
    import json
    path = C.NS / RUNS_REL
    rel = str(path.relative_to(C.REPO))
    disk = path.read_bytes() if path.exists() else None
    commits = C.git("log", "--format=%H", "--", rel).splitlines() if disk is not None else []
    seal_commit = commits[-1] if commits else None
    committed = C.blob_at(seal_commit, rel) if seal_commit else None
    dirty = bool(C.git("status", "--porcelain", "--", rel)) if disk is not None else False
    problems = verify_seal_bytes(disk, committed, dirty)
    runs = None
    if not problems:
        runs = json.loads(disk)
        problems += S.validate_runs(runs)
        runs_code = str((C.NS / "code" / "c11r_runs.py").relative_to(C.REPO))
        at_seal = C.sha256_bytes(C.blob_at(seal_commit, runs_code))
        if runs.get("provenance", {}).get("producer_sha256") != at_seal:
            problems.append("producer hash differs from c11r_runs.py as committed at the seal")
        for key in ("magnitudes", "value_float", "original_value", "original_values"):
            if key in disk.decode():
                problems.append(f"the runs artifact contains a {key!r} field")
    return {"problems": problems, "seal_commit": seal_commit, "runs": runs,
            "runs_sha256": C.sha256_bytes(disk) if disk else None}


# ---------------------------------------------------------------------------------------------
# 3. the ONLY magnitude load in the campaign outside the table producer
# ---------------------------------------------------------------------------------------------
def load_original_magnitudes() -> dict:
    q = C.load(C.NS / "evidence" / "quarantine" / "C11R_ORIGINAL_MAGNITUDES.json")
    return {k: F(v["value"]) for k, v in q["magnitudes"].items()}


# ---------------------------------------------------------------------------------------------
# 4. classification -- pure functions of their arguments
# ---------------------------------------------------------------------------------------------
def classify_numeric(direction: str, indep: F, orig: F, factor: int = FACTOR) -> str:
    if direction == "UPPER_BOUND":
        if indep <= orig:
            return "STRONGER"
        return "AGREES" if indep <= factor * orig else "INSUFFICIENT"
    if direction == "LOWER_BOUND":
        if indep >= orig:
            return "STRONGER"
        return "AGREES" if indep * factor >= orig else "INSUFFICIENT"
    raise ValueError(f"unknown direction {direction!r}")


def opposite_direction_pairs(runs: dict, stmt_table: dict) -> list[dict]:
    """Independent bounds whose quantity the original bounds from the OTHER side."""
    orig_by_q = {v["quantity"]: (k, v["direction"]) for k, v in
                 stmt_table["original_statements"].items()}
    pairs = []
    for k, t in S.targets(runs).items():
        st = t.get("statement")
        if not st or t.get("value") is None:
            continue
        hit = orig_by_q.get(st["quantity"])
        if hit and hit[1] != st["direction"]:
            pairs.append({"independent": k, "original": hit[0], "quantity": st["quantity"],
                          "independent_direction": st["direction"],
                          "original_direction": hit[1]})
    return pairs


def disagreement(pair: dict, indep_value: F, orig_value: F) -> bool:
    if pair["independent_direction"] == "UPPER_BOUND":     # independent says X <= v
        return indep_value < orig_value                    # original says X >= orig
    return indep_value > orig_value                        # independent X >= v, original X <= orig


def run_comparison(runs: dict, stmt_table: dict, mags: dict) -> dict:
    """Everything after the seal, as a pure function. main() and self_test() both call this."""
    per = {}
    violations = []
    for k in S.SIX_CONSTANTS:
        t = S.targets(runs)[k]
        indep_st = EQ.independent_statement(runs, k)
        orig_st = EQ.original_statement(stmt_table, k)
        cmp = EQ.compare(orig_st, indep_st)
        if cmp.get("independence_violation"):
            violations.append(k)
        rec = {"target_status": t["status"], "statement": cmp,
               "independent_value": t.get("value"), "original_value": str(mags[k])}
        if t["status"] != "CERTIFIED" or t.get("value") is None:
            rec["CLASS"] = "INSUFFICIENT"
            rec["why"] = f"no independent certified value (status {t['status']})"
        elif cmp["STATUS"] not in ("EQUIVALENT", "STRONGER"):
            rec["CLASS"] = "INVALID"
            rec["why"] = f"statement is {cmp['STATUS']}; its number is not compared"
        else:
            v, o = F(t["value"]), mags[k]
            rec["numeric"] = classify_numeric(orig_st["direction"], v, o)
            rec["ratio"] = str(v / o)
            rec["CLASS"] = rec["numeric"]
            rec["why"] = f"statement {cmp['STATUS']}; {orig_st['direction']} ratio {float(v / o):.6f}"
        per[k] = rec

    pairs = opposite_direction_pairs(runs, stmt_table)
    for pr in pairs:
        iv = F(S.targets(runs)[pr["independent"]]["value"])
        pr["disagrees"] = disagreement(pr, iv, mags[pr["original"]])
        if pr["disagrees"]:
            per[pr["independent"]]["CLASS"] = "DISAGREES"
            per[pr["independent"]]["why"] = (f"its {pr['independent_direction']} excludes the "
                                              f"original's {pr['original_direction']}")

    classes = {k: v["CLASS"] for k, v in per.items()}
    if violations:
        verdict = "INDEPENDENCE_VIOLATION"
    elif any(c == "DISAGREES" for c in classes.values()):
        verdict = "SCIENTIFIC_DISAGREEMENT"
    elif any(c == "INVALID" for c in classes.values()):
        verdict = "EXECUTION_INVALID"
    elif all(c in ("AGREES", "STRONGER") for c in classes.values()):
        verdict = "N9_CLOSED"
    else:
        verdict = "AGREEMENT_INSUFFICIENT"
    return {"per_target": per, "classes": classes, "opposite_direction_pairs": pairs,
            "independence_violations": violations, "N9_VERDICT": verdict,
            "precedence": list(PRECEDENCE)}


def render(result: dict) -> list[str]:
    """Prose, rendered ONLY from computed fields, after classification."""
    lines = []
    for k in S.SIX_CONSTANTS:
        r = result["per_target"][k]
        lines.append(f"{k}: {r['CLASS']} -- {r['why']}")
    counts = {}
    for c in result["classes"].values():
        counts[c] = counts.get(c, 0) + 1
    lines.append(f"class counts: {dict(sorted(counts.items()))}")
    lines.append(f"opposite-direction pairs found: {len(result['opposite_direction_pairs'])}")
    lines.append(f"N9 classification by frozen precedence {result['precedence']}: "
                 f"{result['N9_VERDICT']}")
    return lines


# ---------------------------------------------------------------------------------------------
# self-test -- SYNTHETIC runs and SYNTHETIC magnitudes only; never loads the quarantine
# ---------------------------------------------------------------------------------------------
def synthetic_runs(stmt_table: dict, values: dict, status: dict | None = None,
                   statements: dict | None = None) -> dict:
    d = stmt_table["drift_domain"]
    drift = (d["e_lo"], d["e_hi"])
    status = status or {}
    routes = {"Abar": "independent_supersolution", "tau": "independent_supersolution",
              "C_T": "independent_supersolution", "D_lo": "independent_subsolution",
              "D1": "independent_derivative_propagation",
              "D2": "independent_derivative_propagation"}
    deps = {"D1": ("C_T_independent", "tau_independent"),
            "D2": ("C_T_independent", "tau_independent")}
    tg = {}
    for k in S.SIX_CONSTANTS:
        stt = status.get(k, "CERTIFIED")
        st = (statements or {}).get(k) or EQ.honest_independent(k, drift, routes[k],
                                                                deps.get(k, ()))
        tg[k] = S.target(k, status=stt, value=values.get(k) if stt == "CERTIFIED" else None,
                         stmt=st if stt == "CERTIFIED" else None,
                         reason=None if stt == "CERTIFIED" else "synthetic",
                         certificate_id=None)
    return S.emit_runs(policy_sha256="0" * 64, statements_sha256="0" * 64,
                       drift_block=drift, certificates={}, targets=tg)


def self_test(stmt_table: dict) -> dict:
    """Exercise every branch of run_comparison on synthetic inputs. Loads no real magnitude."""
    fake = {k: F(10) for k in S.SIX_CONSTANTS}             # synthetic magnitudes, deliberately
    fake["D_lo"] = F(1, 2)                                 # round and meaningless
    cases = []

    def case(label, runs, expect_verdict, expect_classes=None):
        r = run_comparison(runs, stmt_table, fake)
        ok = r["N9_VERDICT"] == expect_verdict and all(
            r["classes"][k] == v for k, v in (expect_classes or {}).items())
        cases.append({"case": label, "verdict": r["N9_VERDICT"], "classes": r["classes"],
                      "expected_verdict": expect_verdict, "ok": ok,
                      "render": render(r)})

    good = {"Abar": F(12), "tau": F(11), "C_T": F(9), "D_lo": F(2, 5), "D1": F(15),
            "D2": F(5)}
    case("all six within factor 2", synthetic_runs(stmt_table, good), "N9_CLOSED",
         {"Abar": "AGREES", "C_T": "STRONGER", "D_lo": "AGREES", "D2": "STRONGER"})
    case("D1 and D2 not implemented", synthetic_runs(stmt_table, good,
                                                     {"D1": "NOT_IMPLEMENTED",
                                                      "D2": "NOT_IMPLEMENTED"}),
         "AGREEMENT_INSUFFICIENT", {"D1": "INSUFFICIENT", "D2": "INSUFFICIENT"})
    far = dict(good, Abar=F(25))
    case("Abar outside factor 2", synthetic_runs(stmt_table, far), "AGREEMENT_INSUFFICIENT",
         {"Abar": "INSUFFICIENT"})
    low = dict(good, D_lo=F(1, 5))
    case("D_lo LOWER bound below half the original", synthetic_runs(stmt_table, low),
         "AGREEMENT_INSUFFICIENT", {"D_lo": "INSUFFICIENT"})
    hi = dict(good, D_lo=F(3, 4))
    case("D_lo LOWER bound above the original is STRONGER, not INSUFFICIENT",
         synthetic_runs(stmt_table, hi), "N9_CLOSED", {"D_lo": "STRONGER"})
    d = stmt_table["drift_domain"]
    mid = str((F(d["e_lo"]) + F(d["e_hi"])) / 2)
    bad_st = EQ.honest_independent("Abar", (mid, mid), "independent_supersolution")
    case("a midpoint statement is INVALID whatever its number",
         synthetic_runs(stmt_table, good, statements={"Abar": bad_st}), "EXECUTION_INVALID",
         {"Abar": "INVALID"})
    viol = EQ.honest_independent("D1", (d["e_lo"], d["e_hi"]),
                                 "independent_derivative_propagation",
                                 ("C_T", "tau", "C_T_independent", "tau_independent"))
    case("consuming the original C_T/tau is an INDEPENDENCE_VIOLATION",
         synthetic_runs(stmt_table, good, statements={"D1": viol}), "INDEPENDENCE_VIOLATION")
    # DISAGREES: an independent UPPER bound on d(atom) below the original's LOWER bound
    ub = EQ.honest_independent("D_lo", (d["e_lo"], d["e_hi"]), "independent_subsolution")
    ub["direction"] = "UPPER_BOUND"
    ub["aggregation"] = {"method": "single_certificate_whole_block", "sub_blocks": 1}
    ub["proposition"] = S.PROPOSITION["D_lo"]
    dis_runs = synthetic_runs(stmt_table, dict(good, D_lo=F(1, 10)), statements={"D_lo": ub})
    r = run_comparison(dis_runs, stmt_table, fake)
    cases.append({"case": "an independent UPPER bound below the original LOWER bound DISAGREES",
                  "verdict": r["N9_VERDICT"], "classes": r["classes"],
                  "expected_verdict": "SCIENTIFIC_DISAGREEMENT",
                  "ok": r["N9_VERDICT"] == "SCIENTIFIC_DISAGREEMENT"
                  and r["classes"]["D_lo"] == "DISAGREES",
                  "render": render(r)})
    # the same opposite-direction pair, but compatible, must NOT disagree
    ok_runs = synthetic_runs(stmt_table, dict(good, D_lo=F(9, 10)), statements={"D_lo": ub})
    r2 = run_comparison(ok_runs, stmt_table, fake)
    cases.append({"case": "an independent UPPER bound ABOVE the original LOWER bound is compatible",
                  "verdict": r2["N9_VERDICT"], "classes": r2["classes"],
                  "expected_verdict": "not SCIENTIFIC_DISAGREEMENT",
                  "ok": r2["N9_VERDICT"] != "SCIENTIFIC_DISAGREEMENT",
                  "render": render(r2)})

    seal = {
        "absent": verify_seal_bytes(None, None, False),
        "never_committed": verify_seal_bytes(b"x", None, False),
        "edited_after_commit": verify_seal_bytes(b"new", b"old", False),
        "uncommitted_change": verify_seal_bytes(b"x", b"x", True),
        "sealed": verify_seal_bytes(b"x", b"x", False),
    }
    seal_ok = all(seal[k] for k in ("absent", "never_committed", "edited_after_commit",
                                    "uncommitted_change")) and not seal["sealed"]
    renders_differ = len({tuple(c["render"]) for c in cases}) == len(cases)
    return {"cases": cases, "seal_controls": seal, "seal_controls_ok": seal_ok,
            "renders_depend_on_inputs": renders_differ,
            "used_real_magnitudes": False,
            "PASS": all(c["ok"] for c in cases) and seal_ok and renders_differ}


# ---------------------------------------------------------------------------------------------
def main() -> int:
    seal = verify_seal()
    if seal["problems"]:
        print("REFUSE: the independent outputs are not sealed, so no original value is loaded.")
        for p in seal["problems"]:
            print(f"  - {p}")
        return 2
    runs = seal["runs"]
    stmt_table = C.load(C.NS / "evidence" / "table" / "C11R_N9_STATEMENTS.json")
    mags = load_original_magnitudes()                     # only now, only here
    result = run_comparison(runs, stmt_table, mags)
    out = {"schema": "C11R_COMPARISON/2",
           "seal": {"commit": seal["seal_commit"], "runs_sha256": seal["runs_sha256"]},
           "comparison_rule_source": {"artifact": "evidence/table/C11R_N9_STATEMENTS.json",
                                      "sha256": stmt_table["sha256"]},
           "result": result,
           "rendered": render(result)}
    s = C.write_evidence(C.NS / "evidence" / "comparison" / "C11R_COMPARISON.json", out,
                         producer=__file__)
    for line in out["rendered"]:
        print(line)
    print(f"wrote evidence/comparison/C11R_COMPARISON.json sha256 {s[:16]}...")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
