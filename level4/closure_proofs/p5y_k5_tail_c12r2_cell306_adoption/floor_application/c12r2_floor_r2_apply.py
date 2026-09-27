"""C12-R2 -- mechanical application of the frozen K5 tail adoption floor r2 to the SEALED cell-306 evidence.

Governance only. It computes no Gamma, no atom constant and no supply, and imports no scientific consumer: every
load-bearing number is READ from committed bytes (the sealed C12-R2 result, C2's committed forecast, the floor r2
rule, the N9 comparison records, C2's and C10's published F2 evidence). The only arithmetic is reading the sign of an
exact rational string. It decides no adoption either: it prepares the mechanical table for the independent
adjudicator, who must verify it and write the adjudication.

    python3.14 -I -S -B c12r2_floor_r2_apply.py --out-json FILE --out-md FILE
"""
import argparse
import hashlib
import json
import subprocess
import sys
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve()
REPO = HERE.parents[4]
CP = "level4/closure_proofs/"
NS = CP + "p5y_k5_tail_c12r2_cell306_adoption"
CHAIN = [("freeze", "11f91daf50a077999023f733d8e870ad3813923a", None),
         ("qualification", "107a8b362e572eeab5c630e838edbe012cd3ae85", "evidence/qualification/"),
         ("qualification review", "e19f4edd06ef2152d8285996db6d60b664c40f7d", "review/C12R2_QUALIFICATION_REVIEW.md"),
         ("grant", "dec92e0983fe39bcf9834e62216daeab09f823a4", "authorization/C12R2_GRANT.json"),
         ("seal", "276f4d416175086640c982ac4cda7c9cf703fccb", "evidence/execution/C12R2_CELL306_RESULT.json"),
         ("execution review", "1173670f04771e9d099182c519fc9a715aa89548", "review/C12R2_EXECUTION_REVIEW.md")]
RESULT = NS + "/evidence/execution/C12R2_CELL306_RESULT.json"
RESULT_BLOB = "0ac46b3d2abe497084ddf7631d894bb819e6ddc6"
MARKER, PENDING = "refs/c12r2/cell306-target-consumed", "refs/c12r2/cell306-pending-result"
FLOOR_RULE = CP + "p5y_k5_tail_floor_r2/config/K5_TAIL_ADOPTION_FLOOR_R2.json"
FLOOR_RULE_SHA = "eb2b4196dd23a8353e25093ff6bfa30d18634dd7f52968ec3c7000ea9b624238"
FLOOR_GATE = CP + "p5y_k5_tail_floor_r2/config/CELL306_ADOPTION_GATE_R2.json"
FLOOR_REVIEW = CP + "p5y_k5_tail_floor_r2/review/FLOOR_R2_REVIEW.md"
C2_FORECAST = CP + "p5y_k5_tail_c2_closure/evidence/phase_d5/C2_D5_FORECAST.json"
C2_FORECAST_SHA = "784f25eecd65bad3bf687727590a0c0e91a683c5d30817c3bda80d6f373fe983"
C2_ADJ = CP + "p5y_k5_tail_c2_closure/evidence/adjudication/C2_ADJUDICATION.md"
C10_GOV = CP + "p5y_k5_tail_c10_governance_provenance/evidence/phase5/C10_GOVERNANCE.json"
N9_ADJ = CP + "p5y_k5_tail_c11rd_d1d2_extension/adjudication/ADJUDICATION_C11RD_N9.md"
N9_REV = CP + "p5y_k5_tail_c11rd_d1d2_extension/review/C11RD_ADJUDICATION_REVIEW.md"
C11R_CMP = CP + "p5y_k5_tail_c11r_n9_statement_alignment/evidence/comparison/C11R_COMPARISON.json"
C11R_CMP_REV = CP + "p5y_k5_tail_c11r_n9_statement_alignment/review/REVIEW_C11R_COMPARISON.md"
C11RD_CMP = CP + "p5y_k5_tail_c11rd_d1d2_extension/evidence/comparison/C11RD_COMPARISON.json"
C11RD_CMP_REV = CP + "p5y_k5_tail_c11rd_d1d2_extension/review/C11RD_COMPARISON_REVIEW.md"
C11RD_RUNS = CP + "p5y_k5_tail_c11rd_d1d2_extension/evidence/runs/C11RD_RUNS.json"
FREEZE_REC = NS + "/protocol/C12R2_FREEZE.json"
R5 = CP + "p5y_k5_tail_c2_closure/evidence/coverage/K5_COVERAGE_MAP_R5.json"


def git(*a, text=True):
    return subprocess.run(["/usr/bin/git", "--no-replace-objects", "-C", str(REPO), *a], capture_output=True,
                          text=text, stdin=subprocess.DEVNULL, env={"PATH": "/usr/bin:/bin", "LC_ALL": "C",
                                                                    "GIT_OPTIONAL_LOCKS": "0"})


def committed(rel: str, rev: str = "HEAD") -> bytes:
    p = git("show", f"{rev}:{rel}", text=False)
    if p.returncode:
        raise SystemExit(f"{rel} is not committed at {rev}")
    return p.stdout


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def sign(rational: str) -> int:
    """Read the sign of an exact rational string (no evaluation of any scientific quantity)."""
    q = Fraction(rational)
    return (q > 0) - (q < 0)


def line2(rel: str) -> str:
    lines = committed(rel).decode().splitlines()
    return lines[1].strip() if len(lines) > 1 else ""


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-json", required=True)
    ap.add_argument("--out-md", required=True)
    a = ap.parse_args(argv)
    ck, ev = {}, {}

    # ---- the chain (as committed; temporal order and file sets)
    for i, (name, c, only) in enumerate(CHAIN):
        parent = git("rev-parse", f"{c}^").stdout.strip()
        files = git("diff-tree", "--no-commit-id", "--name-only", "-r", c).stdout.split()
        ok = git("merge-base", "--is-ancestor", c, "HEAD").returncode == 0
        if i:
            ok = ok and parent == CHAIN[i - 1][1]
        if only:
            ok = ok and files and all(f.startswith(f"{NS}/{only}") for f in files)
        ck[f"chain: {name} {c[:8]} (parent and file set)"] = bool(ok)
    ck["chain: the qualification review is QUALIFICATION_ACCEPTED"] = line2(NS + "/review/C12R2_QUALIFICATION_REVIEW.md") == "QUALIFICATION_ACCEPTED"
    ck["chain: the execution review is EXECUTION_ACCEPTED"] = line2(NS + "/review/C12R2_EXECUTION_REVIEW.md") == "EXECUTION_ACCEPTED"

    # ---- floor r2: authoritative, frozen before the result, unchanged since
    rule_raw = committed(FLOOR_RULE)
    rule = json.loads(rule_raw)
    body = {k: v for k, v in rule.items() if k != "sha256"}
    touched = git("log", "--format=%H", "--", CP + "p5y_k5_tail_floor_r2").stdout.split()
    ck["floor r2: rule bytes are the bound ones and the self-hash verifies"] = sha(rule_raw) == FLOOR_RULE_SHA and \
        sha(json.dumps(body, sort_keys=True).encode()) == rule["sha256"]
    ck["floor r2: acceptance review line 2 is REPLACEMENT_FLOOR_ACCEPTED"] = line2(FLOOR_REVIEW) == "REPLACEMENT_FLOOR_ACCEPTED"
    ck["floor r2: touched only by a15d083b and 3fadb422, both ancestors of the C12-R2 freeze (frozen before the result)"] = \
        [t[:8] for t in touched] == ["3fadb422", "a15d083b"] and all(
            git("merge-base", "--is-ancestor", t, CHAIN[0][1]).returncode == 0 for t in touched)
    ev["floor_rule"] = {"base": rule["rule"]["base"], "F1_prime": rule["rule"]["limbs"]["F1_prime"]["text"],
                        "F2": rule["rule"]["limbs"]["F2"]["text"], "criterion": rule["quantity_compared"]["criterion"],
                        "closure_disagreement": rule["disagreement"]["closure"],
                        "cell_306_criterion": rule["cell_306_future_adoption_criterion"]["criterion"],
                        "known_historically": rule["cell_306_future_adoption_criterion"]["known_historically"],
                        "fail_closed_last": rule["fail_closed"][-1]}

    # ---- the sealed record: the unique authorized execution
    blob_bytes = git("cat-file", "blob", RESULT_BLOB, text=False).stdout
    rec = json.loads(blob_bytes)
    rbody = {k: v for k, v in rec.items() if k != "sha256"}
    worktree = (REPO / RESULT).read_bytes()
    ck["seal: the pending ref, the committed result and the worktree copy are the same bytes (blob 0ac46b3d)"] = \
        git("rev-parse", PENDING).stdout.strip() == RESULT_BLOB == git("rev-parse", f"HEAD:{RESULT}").stdout.strip() and \
        committed(RESULT) == blob_bytes == worktree and \
        hashlib.sha1(b"blob %d\0" % len(blob_bytes) + blob_bytes).hexdigest() == RESULT_BLOB
    ck["seal: the result's self-hash verifies"] = sha(json.dumps(rbody, sort_keys=True).encode()) == rec["sha256"]
    ck["exactly once: the marker points at the grant; status TARGET_EVALUATED; target_evaluations == 1; one result commit"] = \
        git("rev-parse", MARKER).stdout.strip() == CHAIN[3][1] == rec["grant"]["grant_commit"] and \
        rec["status"] == "TARGET_EVALUATED" and rec["target_evaluations"] == 1 and \
        git("log", "--all", "--format=%H", "--", RESULT).stdout.split() == [CHAIN[4][1]]
    ck["exactly once: no other ref under refs/c12r2, refs/c12r1, refs/c12"] = sorted(
        git("for-each-ref", "--format=%(refname)", "refs/c12r2", "refs/c12r1", "refs/c12").stdout.split()) == sorted([MARKER, PENDING])
    freeze = json.loads(committed(FREEZE_REC))
    pins = {k: v["sha256"] for k, v in freeze["input_pins_sha256"].items()}
    ck["seal: every input hash in the record equals the frozen pins (incl. the I2 comparison files)"] = rec["input_sha256"] == pins

    # ---- I1 (historical, committed) and the control
    fc_raw = committed(C2_FORECAST)
    c2 = json.loads(fc_raw)["cells"]["306"]
    i1_exact = rec["control"]["evaluated"]["Gamma_exact"]
    ck["I1: C2's committed forecast is the bound file (a191557f)"] = sha(fc_raw) == C2_FORECAST_SHA and \
        git("rev-parse", f"HEAD:{C2_FORECAST}").stdout.strip().startswith("a191557f")
    ck["I1: the sealed control equals C2's committed Gamma_exact string exactly; reproduces_C2_exactly"] = \
        i1_exact == c2["Gamma_exact"] and rec["control"]["reproduces_C2_exactly"] is True and \
        all(rec["control"]["field_matches"].values())
    ck["I1: the control supply is I1 only (S_I1 = min{G, C1, C2}; provenance C2 on A0/A1/A2)"] = \
        rec["control"]["supply"] == "S_I1 = min{G, C1, C2}" and set(rec["control"]["provenance"].values()) <= {"G", "C1", "C2"}
    i1_sign = sign(i1_exact)

    # ---- I2 (the unique sealed execution)
    t = rec["target"]
    i2_exact = t["evaluated"]["Gamma_exact"]
    ck["I2: the target supply is I2 only (S_I2 = min{G, I2}; provenance I2 on A0/A1/A2)"] = \
        t["supply"] == "S_I2 = min{G, I2}" and set(t["provenance"].values()) <= {"G", "I2"}
    ck["I2: the sealed pass flag agrees with the sign of the sealed exact rational"] = t["evaluated"]["pass"] == (sign(i2_exact) < 0)
    i2_sign = sign(i2_exact)

    # ---- F1' (a)-(c): committed N9 evidence (classes and statuses only; no constant value is read)
    c11r = json.loads(committed(C11R_CMP))
    c11rd = json.loads(committed(C11RD_CMP))
    runs = json.loads(committed(C11RD_RUNS))
    pt = c11r["result"]["per_target"]
    four = {x: pt[x] for x in ("C_T", "tau", "Abar", "D_lo")}
    two = {x: c11rd["per_target"][x] for x in ("D1", "D2")}
    a_ok = all(v["target_status"] == "CERTIFIED" for v in four.values()) and (runs.get("status") or runs.get("state")) == "CERTIFIED" and \
        runs.get("cell") == 306 and all(v["statement"]["domain"] == "EQUAL" for v in [*four.values(), *two.values()])
    b_ok = all(v["CLASS"] in ("AGREES", "STRONGER") for v in [*four.values(), *two.values()]) and \
        all(v["statement"]["STATUS"] in ("EQUIVALENT", "STRONGER") for v in [*four.values(), *two.values()]) and \
        c11r["result"]["independence_violations"] == [] and c11rd["independence_violations"] == [] and \
        c11rd["N9_VERDICT"] == "N9_CLOSED" and line2(C11RD_CMP_REV) == "COMPARISON_ACCEPTED" and \
        "VERDICT: COMPARISON_ACCEPTED" in committed(C11R_CMP_REV).decode() and \
        line2(N9_ADJ) == "N9_CLOSED" and line2(N9_REV) == "ADJUDICATION_ACCEPTED"
    soundness = {k: v for k, v in freeze["input_pins_sha256"].items() if k.startswith("soundness_")}
    c_ok = len(soundness) == 5 and all(sha(committed(v["path"])) == v["sha256"] for v in soundness.values())
    ev["F1_prime_classes"] = {x: {"CLASS": v["CLASS"], "statement": v["statement"]["STATUS"], "domain": v["statement"]["domain"]}
                              for x, v in {**four, **two}.items()}

    # ---- F2: historical, frozen evidence only (never re-run)
    c2adj = committed(C2_ADJ).decode()
    c10 = json.loads(committed(C10_GOV))["Q2_phase11_cell306"]
    f2_hist = "+0.029163 → does **not** close. **FAILS F2**" in c2adj and "| uniform-A margin | **1.4053** | 1.1277 |" in c2adj \
        and c10["F2_passes"] is False and c10["uniform_A_margin"] < 1.25 and \
        "C2 published that F2 fails for cell 306 on S_I1" in rule["cell_306_future_adoption_criterion"]["known_historically"] and \
        freeze["decision_table"]["F2"].startswith("NOT_SATISFIED") and rec["floor_r2_table"]["F2"].startswith("NOT_SATISFIED")
    ev["F2_historical"] = {"C2_adjudication_306": "Gamma at every atom constant x1.25 = +0.029163 -> does not close -> FAILS F2; "
                                                  "uniform-A margin 1.1277 < 1.25 (C2_ADJUDICATION.md, section K, 'Applying it')",
                           "C10_Q2_phase11_cell306": {"F2_passes": c10["F2_passes"], "uniform_A_margin": c10["uniform_A_margin"],
                                                      "note": "C10 imports C8's margin (README caveat); also < 1.25"},
                           "floor_r2": rule["cell_306_future_adoption_criterion"]["known_historically"],
                           "C12R2_freeze_decision_table": freeze["decision_table"]["F2"]}

    # ---- the mechanical table
    base = i1_sign < 0
    f1p_abc = bool(a_ok and b_ok and c_ok)
    f1p_d_i1, f1p_d_i2 = i1_sign < 0, i2_sign < 0
    f1p = f1p_abc and f1p_d_i1 and f1p_d_i2
    f2 = False if f2_hist else None
    criterion = bool(base and (f1p or (f2 is True)))
    table = [
        {"requirement": "F1'(a) six constants certified on the whole block", "I1": "certified (REGISTRY_C1/C2, C2 two-pass re-certification)",
         "I2": "certified (C11R 4 targets CERTIFIED, C11RD runs CERTIFIED)", "result": "PASS" if a_ok else "FAIL",
         "evidence": f"{C11R_CMP}; {C11RD_RUNS}; floor r2 soundness_evidence"},
        {"requirement": "F1'(b) constant classes AGREES/STRONGER; statements EQUIVALENT/STRONGER; accepted comparisons",
         "I1": "-", "I2": "-", "result": "PASS" if b_ok else "FAIL",
         "evidence": f"{C11R_CMP} (7375b9cd COMPARISON_ACCEPTED); {C11RD_CMP} (90265349 COMPARISON_ACCEPTED); N9 7d67989d/fb237288"},
        {"requirement": "F1'(c) soundness evidence per implementation", "I1": "pinned", "I2": "pinned",
         "result": "PASS" if c_ok else "FAIL", "evidence": "C12R2_FREEZE.json soundness_* pins, sha256 verified at HEAD"},
        {"requirement": "own-supply Gamma(5,306; S_I) < 0", "I1": f"TRUE (sign {i1_sign})", "I2": f"FALSE (sign {i2_sign})",
         "result": "I1 PASS, I2 FAIL", "evidence": f"{C2_FORECAST} cells['306'].Gamma_exact = sealed control; {RESULT} target (blob {RESULT_BLOB[:8]})"},
        {"requirement": "F1' = (a) and (b) and (c) and (d: both own-supply Gamma < 0)", "I1": "-", "I2": "-",
         "result": "PASS" if f1p else "FAIL", "evidence": "floor r2 rule.limbs.F1_prime; disagreement.closure"},
        {"requirement": "F2 (uniform-A margin >= 1.25 on S_I1), historical, not re-run", "I1": "-", "I2": "-",
         "result": "FAIL" if f2 is False else "UNDETERMINED", "evidence": "C2_ADJUDICATION.md section K; C10 Q2_phase11_cell306; floor r2 known_historically"},
        {"requirement": "base clause: Gamma(5,306; chosen supply S_I1) < 0", "I1": "TRUE", "I2": "-",
         "result": "PASS" if base else "FAIL", "evidence": "sealed control = C2 committed Gamma_exact"},
        {"requirement": "adoption criterion: base AND (F1' OR F2)", "I1": "-", "I2": "-",
         "result": "MET" if criterion else "NOT_MET", "evidence": "floor r2 rule.base; gate G12; fail_closed"},
    ]
    out = {"schema": "rebaseguard.p5y.k5.tail-c12r2.floor-r2-application.v1",
           "nature": "mechanical application prepared for the independent adjudicator; decides nothing; computes no Gamma",
           "HEAD": git("rev-parse", "HEAD").stdout.strip(), "checks": ck, "all_checks_pass": all(ck.values()),
           "I1": {"Gamma_exact": i1_exact, "Gamma_float_as_sealed": rec["control"]["evaluated"]["Gamma"], "sign": i1_sign,
                  "source": f"{C2_FORECAST} (blob a191557f) cells['306'].Gamma_exact == sealed control"},
           "I2": {"Gamma_exact": i2_exact, "Gamma_exact_sha256": sha(i2_exact.encode()),
                  "Gamma_float_as_sealed": t["evaluated"]["Gamma"], "sign": i2_sign, "pass_as_sealed": t["evaluated"]["pass"],
                  "source": f"{RESULT} (blob {RESULT_BLOB}, seal {CHAIN[4][1]})"},
           "evidence": ev, "table": table,
           "mechanical_outcome": {"base_clause": base, "F1_prime_a": a_ok, "F1_prime_b": b_ok, "F1_prime_c": c_ok,
                                  "F1_prime_d_I1": f1p_d_i1, "F1_prime_d_I2": f1p_d_i2, "F1_prime": f1p, "F2": f2,
                                  "adoption_criterion": "MET" if criterion else "NOT_MET",
                                  "implication_checked": "Gamma(5,306;S_I2) > 0 in exact rationals and floor r2 requires < 0 "
                                                         "under I2's own supply -> F1' cannot pass (rule disagreement.closure)"},
           "not_used": "no evidence of cells 307-309; no consumer module; no supply construction; no F2 re-run"}
    Path(a.out_json).write_text(json.dumps(out, indent=1, sort_keys=True, ensure_ascii=False) + "\n")
    md = ["# C12-R2 — mechanical application of floor r2 to the sealed cell-306 evidence", "",
          "Prepared for the independent adoption adjudicator. **It decides nothing and computes no Γ**: every value below is "
          "read from committed bytes, and the only arithmetic is the sign of an exact rational string.", "",
          f"All {len(ck)} provenance checks pass: **{all(ck.values())}** (HEAD `{out['HEAD'][:8]}`).", "",
          "| requirement | I1 | I2 | result | evidence |", "|---|---|---|---|---|"]
    md += [f"| {r['requirement']} | {r['I1']} | {r['I2']} | **{r['result']}** | {r['evidence']} |" for r in table]
    md += ["", f"- Γ(5,306; S_I1) = {out['I1']['Gamma_float_as_sealed']} (sealed exact rational, sign {i1_sign}); equals C2's committed record.",
           f"- Γ(5,306; S_I2) = {out['I2']['Gamma_float_as_sealed']} (sealed exact rational, sign {i2_sign}; "
           f"sha256 of the exact string {out['I2']['Gamma_exact_sha256'][:16]}…); pass as sealed: {out['I2']['pass_as_sealed']}.",
           "- The strict criterion Γ < 0 is applied with no tolerance, as the frozen rule states "
           "(`Gamma = 0 or an incomplete evaluation fails`).",
           f"- Mechanical outcome: base **{base}**, F1′ **{f1p}**, F2 **{f2}** (historical), adoption criterion "
           f"**{'MET' if criterion else 'NOT_MET'}**.", ""]
    Path(a.out_md).write_text("\n".join(md))
    print(f"FLOOR-R2 APPLICATION: checks {sum(ck.values())}/{len(ck)}; base {base}; F1' {f1p}; F2 {f2}; "
          f"criterion {'MET' if criterion else 'NOT_MET'}")
    return 0 if all(ck.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
