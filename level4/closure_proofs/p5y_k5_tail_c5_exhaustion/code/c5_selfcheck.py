"""Condition 6: the mechanical replacement for a control that has now failed four times.

This campaign line has, four times, recorded a repair or a state as landed when it had not:

  1-2. C4's adjudicator found two "Fixed at source" claims that landed in the theorem module and nowhere else;
  3.   C5's ERRATUM E7 asserted a withdrawn phrase was confined to `withdrawn_phrase` while the phase-3 table
       still carried it verbatim;
  4.   C5's forecast commit asserted a round-3 READY clearance while the committed review artifact was the
       round-2 report, ending NOT_READY.

Each time the response was a note to the author. Notes to the author have a demonstrated failure rate of 100%.
This is the check instead, and it REFUSES rather than reporting.

    python3 -B c5_selfcheck.py --out OUT.json
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from c5_common import CP, NS                                                    # noqa: E402

REPO = CP.parents[1]

WITHDRAWN = {
    "provably useless for 309":
        "withdrawn in the route ledger (E1): it leaned on the C4 exclusion, which under C5-T retains only 0.94% "
        "of critical-A0 margin",
    "zero verdict value":
        "withdrawn in the route ledger (E2): written in the same commit in which C5-T consumed 63% of the margin "
        "it claimed needed no defence",
}
# A withdrawal notice always PRECEDES the quoted phrase, so the window is asymmetric: a generous look-back and a
# short look-ahead. A marker appearing only after the phrase does not retract it.
WITHDRAWAL_MARKERS = ("withdraw", "WITHDRAWN", "Withdrawn", "retract", "RETRACTED", "erratum", "ERRATUM",
                      "no longer", "was itself wrong", "condemned", "re-open", "RE_OPENED", "reopened",
                      "v1 killed", "v1 recorded", "first version", "killed it as")
LOOKBACK, LOOKAHEAD = 900, 150
CLEARING = ("READY_TO_FORECAST", "READY_TO_FORECAST_WITH_NOTES")
BLOCKING = ("NOT_READY",)


def tracked_text_files():
    out = subprocess.run(["git", "-C", str(REPO), "ls-files", str(NS.relative_to(REPO))],
                         capture_output=True, text=True, check=True).stdout.split()
    return [REPO / p for p in out if p.endswith((".md", ".json", ".py"))]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    files = tracked_text_files() + [p for p in NS.rglob("*")
                                    if p.suffix in (".md", ".json", ".py") and p.is_file()]
    files = sorted(set(files))
    findings, checks = [], {}

    live = []
    for f in files:
        if f.name.startswith("REVIEW_") or f.name == "C5_ADJUDICATION.md" or f.name == "c5_selfcheck.py":
            continue                       # a reviewer quoting the defect is evidence; this file defines them
        txt = f.read_text(errors="ignore")
        for phrase in WITHDRAWN:
            for m in re.finditer(re.escape(phrase), txt, re.I):
                ctx = txt[max(0, m.start() - LOOKBACK): m.end() + LOOKAHEAD]
                if not any(w in ctx for w in WITHDRAWAL_MARKERS):
                    live.append({"file": f.relative_to(NS).as_posix(), "phrase": phrase,
                                 "context": " ".join(ctx.split())[:200]})
    checks["a_no_live_withdrawn_string"] = not live
    findings += live

    fdir = NS / "evidence/forecast"
    forecasts = sorted(fdir.glob("*.json")) if fdir.exists() else []
    handovers = {}
    for r in sorted((NS / "review").glob("*.md")):
        lines = [ln.strip() for ln in r.read_text(errors="ignore").rstrip().splitlines() if ln.strip()]
        handovers[r.name] = lines[-1] if lines else ""
    cleared = [n for n, h in handovers.items() if any(c in h for c in CLEARING)]
    blocked = [n for n, h in handovers.items() if any(b in h for b in BLOCKING)]
    checks["b_forecast_has_a_clearing_review_in_the_tree"] = (not forecasts) or bool(cleared)
    if forecasts and not cleared:
        findings.append({"file": "review/", "phrase": "CLEARING HANDOVER",
                         "context": f"a forecast artifact exists but no reviewer artifact in the tree carries a "
                                    f"clearing handover; handovers found: {handovers}"})

    readme = (NS / "README.md").read_text()
    advertised = sorted(set(re.findall(r"`([A-Za-z0-9_./]+\.(?:md|json|py))`", readme)))
    missing = [p for p in advertised if "/" in p and not (NS / p).exists()]
    checks["c_readme_advertises_only_existing_paths"] = not missing
    findings += [{"file": "README.md", "phrase": p, "context": "advertised but absent"} for p in missing]

    out = {"schema": "rebaseguard.p5y.k5.tail-c5.selfcheck.v1",
           "why": "four instances in this line of a repair or state recorded as landed when it had not; this "
                  "refuses instead of noting",
           "files_scanned": len(files), "withdrawn_strings": WITHDRAWN,
           "review_handovers_in_tree": handovers, "clearing": cleared, "blocking": blocked,
           "forecast_artifacts": [p.name for p in forecasts],
           "checks": checks, "findings": findings,
           "SELFCHECK": "PASS" if all(checks.values()) else "FAIL"}
    Path(a.out).write_text(json.dumps(out, sort_keys=True, indent=1) + "\n")
    print(json.dumps({"SELFCHECK": out["SELFCHECK"], "checks": checks, "handovers": handovers,
                      "findings": findings[:6]}, indent=1))
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
