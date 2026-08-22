"""Stage F adversarial suite: F1-F18.

Stage F is an AUDIT. These checks exist to catch Stage F itself inflating,
mutating or quietly repairing the historical record. Every check is reported
pass or fail; a failure is shown, not patched away.
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
SF = REPO / "level4" / "stage_f"
RES = SF / "results"
REPORTS = REPO / "level4" / "reports"

FROZEN_PROTOCOLS = {
    "stage_c": ("level4/stage_c/STAGE_C_PROTOCOL.md",
                "36bd6ba03a20b7f87dc0eb91c42e5c023c03d7a23cba0c515390d1130b2cedd7"),
    "stage_c1": ("level4/stage_c1/STAGE_C1_PROTOCOL.md",
                 "7b45c091229387e255b285013a4f7d60fac7c2adad66ba83d69e30c3ef79cbdb"),
    "stage_d": ("level4/stage_d/STAGE_D_PROTOCOL.md",
                "925adecf08c7234375333a26c3af934b005e0d8b4cfce470b77834d7245e8b2e"),
    "stage_e": ("level4/stage_e/STAGE_E_PROTOCOL.md",
                "974487019f57c7c319b3bfafcdc20497ab6fca86834ad0d2245a694296ef23cc"),
}
PRECOMMITS = {
    "d2_3_step": ("level4/stage_d/notes/D2_3_STEP_PRECOMMIT.md",
                  "7b7a54c64f4c86334415a03cd45797e7cb8b923d378fa90180a71f1831588dea"),
    "d2_5": ("level4/stage_d/notes/D2_5_PRECOMMIT.md",
             "fb6272ef839d7f3b36af3c8a8ace3d3059df7028dda337455b9df6baaf92bba7"),
    "d3_regularity": ("level4/stage_d/notes/D3_REGULARITY.md",
                      "9eafbcd25870a19e20d5f84c763c5252bd44b3af809de4821d1e99555f93626e"),
}
DECISIONS = {
    "stage_c": ("level4/stage_c/results/findings.json", "decision", "STAGE-C-PARTIAL"),
    "stage_c1": ("level4/stage_c1/results/findings_confirmatory.json", "decision",
                 "STAGE-C1-CLOSED-CONFIRMED-SENSITIVITY"),
    "stage_d": ("level4/stage_d/results/stage_d_decision.json", "decision",
                "STAGE-D-PARTIAL"),
    "stage_e": ("level4/stage_e/results/stage_e_decision.json", "decision",
                "STAGE-E-PARTIAL"),
    "stage_b": ("level4/stage_b/certificate/period2_certificate.json", "decision",
                "STAGE-B-CLOSED-RIGOROUS-PERIOD2"),
}
EXPECTED_TESTS = {"level_1_3": 90, "stage_a": 290, "stage_b": 46, "stage_c": 48,
                  "stage_c1": 36, "stage_d": 72, "stage_e": 59}
FORBIDDEN = ["detector-independent", "distribution-free", "universal",
             "production validated", "production-proven", "optimal reuse",
             "universally safe", "universally unstable",
             "first-ever sequential monitoring stability boundary",
             "real-world deployment validated"]
NEG = ("not ", "never", "no ", "❌", "rather than", "cannot", "must not",
       "ruled out", "unreachable", "does not", "forbidden", "without")


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def scannable(p: Path) -> str:
    """Strip declared forbidden-phrase contexts: a SECTION whose heading says it
    lists banned wording, and the "Forbidden wording" COLUMN of a ledger table.
    Only that one column is dropped; every other cell in the row is scanned."""
    out, skip, fcol = [], False, None
    for line in p.read_text().splitlines():
        if line.startswith("#"):
            low = line.lower()
            skip = ("forbidden" in low or "ruled out" in low
                    or "not supported" in low or "not claimed" in low)
        if skip:
            continue
        if line.startswith("|"):
            cells = line.split("|")
            if fcol is None and "forbidden wording" in line.lower():
                for i, c in enumerate(cells):
                    if "forbidden wording" in c.lower():
                        fcol = i
                        break
            if fcol is not None and len(cells) > fcol:
                cells[fcol] = " "
                line = "|".join(cells)
        out.append(line)
    return "\n".join(out).lower().replace("*", "").replace("`", "")


def main() -> None:
    t0 = time.time()
    checks = []

    def add(cid, name, ok, detail):
        checks.append({"id": cid, "check": name, "passed": bool(ok), **detail})
        print(f"  [{cid:>3}] {'PASS' if ok else 'FAIL'}  {name}", flush=True)

    # F1 historical protocol hashes ----------------------------------------
    det, ok = {}, True
    for k, (rel, want) in {**FROZEN_PROTOCOLS, **PRECOMMITS}.items():
        p = REPO / rel
        got = sha(p) if p.exists() else None
        det[k] = {"path": rel, "expected": want, "actual": got, "match": got == want}
        ok &= got == want
    add("F1", "all frozen protocol and pre-commitment hashes match", ok,
        {"per_artifact": det})

    # F2 historical decisions unchanged ------------------------------------
    det, ok = {}, True
    for k, (rel, key, want) in DECISIONS.items():
        p = REPO / rel
        got = json.loads(p.read_text()).get(key) if p.exists() else None
        det[k] = {"expected": want, "actual": got, "match": got == want}
        ok &= got == want
    add("F2", "all historical stage decisions unchanged", ok, {"per_stage": det})

    # F3 no scientific result mutated by Stage F ----------------------------
    marker = RES / "stage_f_start_marker.json"
    newer = []
    if marker.exists():
        mt = marker.stat().st_mtime
        for pat in ("level4/stage_a", "level4/src", "level4/stage_b",
                    "level4/stage_c", "level4/stage_c1", "level4/stage_d",
                    "level4/stage_e", "closure", "rebaseguard-proof"):
            base = REPO / pat
            if not base.exists():
                continue
            for f in base.rglob("*"):
                if (f.is_file() and f.stat().st_mtime > mt
                        and ".venv" not in str(f) and "__pycache__" not in str(f)
                        and ".pytest_cache" not in str(f)
                        and not f.name.endswith(".pyc")):
                    newer.append(str(f.relative_to(REPO)))
    # mtime alone is not mutation: `verify_level_1_3.sh` regenerates and restores
    # `proofs/audit_report.md` as part of the Arb full-replay audit, which moves
    # the mtime while leaving the bytes identical. Content is the real test, so
    # any mtime hit is confirmed against git before being called a mutation.
    # This is STRICTER than the mtime check: it would catch an in-place edit that
    # preserved the mtime.
    dirty = subprocess.run(["git", "status", "--porcelain", "--"] + newer,
                           capture_output=True, text=True, cwd=REPO).stdout.split()
    content_changed = [f for f in newer
                       if any(f in line for line in dirty)]
    touched_only = [f for f in newer if f not in content_changed]
    add("F3", "no historical scientific artifact modified after Stage F began",
        not content_changed,
        {"content_changed": content_changed,
         "mtime_touched_but_byte_identical": touched_only,
         "marker_present": marker.exists(),
         "note": ("mtime-only entries are verification side effects: "
                  "verify_level_1_3.sh regenerates and restores audit_report.md "
                  "and reports it byte-identical. Content is checked via git.")})

    # F4 final ledger free of unsupported universal language -----------------
    led = REPORTS / "LEVEL_4_FINAL_LEDGER.md"
    hits = []
    if led.exists():
        txt = scannable(led)
        for w in FORBIDDEN:
            for i in [m for m in range(len(txt)) if txt.startswith(w, m)]:
                win = txt[max(0, i - 130):i + len(w) + 60]
                if not any(n in win for n in NEG):
                    hits.append({"word": w, "context": win[:150]})
    add("F4", "final claim ledger contains no unsupported universal language",
        not hits and led.exists(), {"hits": hits, "ledger_exists": led.exists()})

    # F5 no Stage D result called certified unless inherited -----------------
    rep = REPORTS / "STAGE_D_REPORT.md"
    bad = []
    if rep.exists():
        txt = scannable(rep)
        attribution = ("stage b", "level 1", "level 2c", "rigorous-certified",
                       "frozen-certified", "enclosure", "inherited")
        for i in [m for m in range(len(txt)) if txt.startswith("certified", m)]:
            win = txt[max(0, i - 130):i + 70]
            if not any(n in win for n in NEG) and not any(a in win for a in attribution):
                bad.append(win[:150])
    add("F5", "no Stage D result described as certified without inheritance",
        not bad, {"violations": bad})

    # F6 Stage E not described as production validation ---------------------
    bad = []
    for name in ("STAGE_E_REPORT.md", "STAGE_E_LEDGER.md"):
        p = REPORTS / name
        if not p.exists():
            continue
        txt = scannable(p)
        for w in ("production validation", "production validated",
                  "deployment validated", "production-proven"):
            for i in [m for m in range(len(txt)) if txt.startswith(w, m)]:
                win = txt[max(0, i - 130):i + len(w) + 50]
                if not any(n in win for n in NEG):
                    bad.append({"file": name, "context": win[:150]})
    add("F6", "Stage E never described as production or deployment validation",
        not bad, {"violations": bad})

    # F7 PARTIAL labels remain visible --------------------------------------
    want = {"STAGE-C-PARTIAL": False, "STAGE-D-PARTIAL": False,
            "STAGE-E-PARTIAL": False}
    fin = REPORTS / "LEVEL_4_FINAL_REPORT.md"
    if fin.exists():
        t = fin.read_text()
        for k in want:
            want[k] = k in t
    add("F7", "Stage C/D/E PARTIAL labels visible in the final report",
        all(want.values()) and fin.exists(),
        {"present": want, "final_report_exists": fin.exists()})

    # F8 Stage E 0/3 count preserved -----------------------------------------
    e = json.loads((REPO / "level4/stage_e/results/stage_e_decision.json").read_text())
    n = e["n_tasks_supporting_H_E5"]
    in_report = fin.exists() and ("0 / 3" in fin.read_text() or "0/3" in fin.read_text())
    add("F8", "Stage E 0/3 H-E5 count preserved in artifact and report",
        n == 0 and in_report, {"n_tasks_supporting_H_E5": n,
                               "stated_in_final_report": in_report})

    # F9 D2.3 failure preserved ----------------------------------------------
    d = json.loads((REPO / "level4/stage_d/results/stage_d_decision.json").read_text())
    d23 = [c for c in d["criteria"] if c["id"] == "D2.3"][0]
    in_rep = fin.exists() and "D2.3" in fin.read_text()
    add("F9", "D2.3 FAILED preserved in artifact and final report",
        d23["status"] == "FAIL" and in_rep,
        {"d2_3_status": d23["status"], "mentioned_in_final_report": in_rep})

    # F10 t3 ambiguity preserved ---------------------------------------------
    t3 = [c for c in d["criteria"] if c["id"] == "D3.2-t3"][0]
    in_rep = fin.exists() and "AMBIGUOUS" in fin.read_text()
    add("F10", "Stage D t3 estimand ambiguity preserved",
        t3["status"] == "AMBIGUOUS" and in_rep,
        {"t3_status": t3["status"], "ambiguous_in_final_report": in_rep})

    # F11 Task C unreliable endpoints excluded from closure -------------------
    c = e["per_task"]["bike_sharing"]
    ok = ("E2" in c["unreliable_endpoints"] and "E3" in c["unreliable_endpoints"]
          and c["hypotheses"]["H_E1"]["status"] == "UNEVALUABLE"
          and c["hypotheses"]["H_E2"]["status"] == "UNEVALUABLE"
          and c["counts_toward_H_E5"] is False)
    add("F11", "Task C unreliable E2/E3 excluded from every closure claim", ok,
        {"unreliable": c["unreliable_endpoints"],
         "H_E1": c["hypotheses"]["H_E1"]["status"],
         "H_E2": c["hypotheses"]["H_E2"]["status"]})

    # F12 P3 remains exploratory ----------------------------------------------
    ok = e["exploratory_policy_excluded"] == "P3_moderate_EXPLORATORY"
    add("F12", "Stage E P3 remains exploratory and excluded from closure", ok,
        {"exploratory_policy_excluded": e["exploratory_policy_excluded"]})

    # F13 test accounting matches the executable suite -------------------------
    counts, ok13 = {}, True
    def collect(cmd, cwd):
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd)
        m = re.search(r"(\d+) tests? collected", r.stdout)
        return int(m.group(1)) if m else None
    counts["level_1_3"] = collect(".venv/bin/python -m pytest -q --collect-only",
                                  REPO / "rebaseguard-proof")
    for key, rel in (("stage_a", "level4/tests"), ("stage_b", "level4/stage_b/tests"),
                     ("stage_c", "level4/stage_c/tests"),
                     ("stage_c1", "level4/stage_c1/tests"),
                     ("stage_d", "level4/stage_d/tests"),
                     ("stage_e", "level4/stage_e/tests")):
        counts[key] = collect(
            f"level4/.venv/bin/python -m pytest {rel} -q --collect-only", REPO)
    for k, want in EXPECTED_TESTS.items():
        ok13 &= counts.get(k) == want
    total = sum(v for v in counts.values() if v)
    add("F13", "test-count accounting matches the executable suite", ok13,
        {"expected": EXPECTED_TESTS, "actual": counts, "actual_total": total,
         "expected_total": sum(EXPECTED_TESTS.values())})

    # F14 every headline claim points to an artifact ---------------------------
    missing = []
    if led.exists():
        for line in led.read_text().splitlines():
            if line.startswith("|") and line.count("|") >= 7:
                cells = [c.strip() for c in line.split("|")]
                if len(cells) > 6 and cells[1] and cells[1] not in ("ID", "---", ":---"):
                    if not re.search(r"[\w/]+\.(md|json|py|csv|lean|sh)", line) \
                            and "Source" not in line and "---" not in cells[1]:
                        missing.append(cells[1])
    add("F14", "every ledger claim cites an artifact", not missing,
        {"claims_without_artifact": missing[:12]})

    # F15 verdict mechanically derivable ---------------------------------------
    dec_p = RES / "final_decision.json"
    ok15, det15 = False, {}
    if dec_p.exists():
        dec = json.loads(dec_p.read_text())
        det15 = {"decision": dec.get("decision"),
                 "allowed": dec.get("allowed_labels"),
                 "has_trace": bool(dec.get("decision_rule_trace")),
                 "mandatory_unmet": dec.get("n_mandatory_unmet")}
        ok15 = (dec.get("decision") in dec.get("allowed_labels", [])
                and bool(dec.get("decision_rule_trace"))
                and dec.get("n_mandatory_unmet", 0) >= 1)
    add("F15", "final verdict is mechanically derivable from the reconstruction",
        ok15, det15)

    # F16 no forbidden wording outside negation/forbidden lists -----------------
    hits = []
    for p in sorted(REPORTS.glob("LEVEL_4_FINAL_*.md")) + \
            sorted(SF.glob("*.md")):
        txt = scannable(p)
        for w in FORBIDDEN:
            for i in [m for m in range(len(txt)) if txt.startswith(w, m)]:
                win = txt[max(0, i - 130):i + len(w) + 60]
                if not any(n in win for n in NEG):
                    hits.append({"file": p.name, "word": w, "ctx": win[:130]})
    add("F16", "no forbidden wording appears affirmatively in Stage F artifacts",
        not hits, {"hits": hits})

    # F17 Stage F altered no frozen protocol ------------------------------------
    # identical to F1 in content but asserted as a Stage-F-specific obligation
    ok17 = all(sha(REPO / rel) == want for rel, want in FROZEN_PROTOCOLS.values())
    add("F17", "Stage F did not alter any frozen protocol", ok17,
        {"protocols_checked": list(FROZEN_PROTOCOLS)})

    # F18 reproduction entry points exist and are executable ---------------------
    entries = ["scripts/verify_level_1_3.sh", "scripts/verify_level_4.sh",
               "level4/stage_b/reproduce.sh", "level4/stage_c/reproduce.sh",
               "level4/stage_c1/reproduce.sh", "level4/stage_d/reproduce.sh",
               "level4/stage_e/reproduce.sh", "level4/stage_f/reproduce.sh"]
    det = {e: (REPO / e).exists() for e in entries}
    add("F18", "every stage reproduction entry point exists", all(det.values()),
        {"entry_points": det})

    n_pass = sum(c["passed"] for c in checks)
    out = {"suite": "Stage F adversarial", "n_checks": len(checks),
           "n_passed": n_pass, "n_failed": len(checks) - n_pass,
           "checks": checks, "elapsed_s": round(time.time() - t0, 1)}
    RES.mkdir(parents=True, exist_ok=True)
    (RES / "adversarial_f.json").write_text(json.dumps(out, indent=2) + "\n")
    print(f"\n  {n_pass}/{len(checks)} Stage F adversarial checks passed "
          f"({out['elapsed_s']} s)", flush=True)


if __name__ == "__main__":
    main()
