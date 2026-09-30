"""Owner procedure step 11: prove there is no unresolved placeholder, mutable scientific decision or post-result choice.

  python3 code/p309_placeholder_check.py     -> evidence/freeze/PLACEHOLDER_CHECK.json; exit 0 iff PASS

Mechanical part: every frozen document and code file of the formal namespace (the FROZEN_DIRS) and the rev. 2b package
documents are scanned for placeholder markers, open-decision phrases and choice phrases.  Every hit must be listed in
the reviewed allowlist below with a reason (for example a phrase that quotes a rule, or a refusal message); anything
else is a FAIL.  The frozen parameter file must contain no null value outside the declared post-grant derivations.
The judgement part (what is a post-grant derivation, why it is not a choice) is in
governance/NO_PLACEHOLDER_STATEMENT_P309.md.
"""
from __future__ import annotations

import datetime
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

FNS = Path(__file__).resolve().parents[1]
REPO = FNS.parents[2]
sys.path.insert(0, str(FNS / "code"))
import p309_env as E  # noqa: E402

FROZEN_DIRS = ("code", "config", "fc2", "freeze", "tests", "verify", "governance")
RNS_DOCS = ["protocol_prep/P309_PROTOCOL.md", "protocol_prep/P309_FORMAL_PACKAGE.md",
            "protocol_prep/P309_REVIEW_BRIEFS.md", "theory/THEOREM_SRK.md"]
MARKERS = re.compile(r"\bTBD\b|\bTODO\b|\bFIXME\b|\bXXX\b|<to be\b|to be decided|to be determined|\bplaceholder\b|"
                     r"\?\?\?|\bPENDING_DECISION\b|\bundecided\b|\bopen question\b", re.I)
CHOICE = re.compile(r"owner (decides|to decide|may choose)|may be chosen|at the coordinator's discretion|"
                    r"after (seeing|inspecting) the result|depending on the result", re.I)
# reviewed allowlist: (file suffix, phrase regex, reason)
ALLOW = [
    ("code/p309_placeholder_check.py", r".*", "this checker names the markers it searches for"),
    ("governance/NO_PLACEHOLDER_STATEMENT_P309.md", r".*", "the statement quotes the markers it rules out"),
    ("code/p309_driver.py", r"placeholder", "none expected"),
    ("code/p309_driver.py", r"TBD|TODO", "PLACEHOLDER_MARKS: the placeholder values the driver REFUSES in a grant's "
                                         "authority before the marker (rev. 2c A21, R4 NB8)"),
    ("code/make_freeze_params.py", r"placeholder", "the frozen rule text: the driver refuses a placeholder authority "
                                                   "(rev. 2c A21)"),
    ("code/make_proposed_authorization.py", r"placeholder", "the grant rules text: the owner's values must not be "
                                                            "placeholders; the driver refuses them (rev. 2c A21)"),
    ("governance/P309_REV2C_AMENDMENTS.md", r"placeholder", "A21 states the rule that refuses placeholder grant values"),
    ("verify/scoped_sandbox.py", r"placeholder", "the verifier author's sandbox builder seeds a TEST_ONLY synthetic "
                                                "guard_id from the bytes 'TEST_ONLY_DO_NOT_EXECUTE guard placeholder' "
                                                "(sandbox grants only; not a campaign value)"),
    ("governance/briefs_recovered/README.md", r"placeholder", "states that a number in brief 1 is an illustrative "
                                                              "placeholder in firewall wording, not a campaign value"),
    ("governance/briefs_recovered/AGENT_BRIEFS_TRANSCRIPT.jsonl", r".*", "verbatim historical briefs (record only; "
                                                                        "they govern nothing)"),
    ("governance/OWNER_DECISIONS_P309_VERBATIM.md", r".*", "the owner's own text, verbatim"),
    ("governance/OWNER_RULINGS_2_P309_VERBATIM.md", r".*", "the owner's own text, verbatim"),
    ("governance/OWNER_D5_RATIFICATION_P309_VERBATIM.md", r".*", "the owner's own text, verbatim"),
    ("protocol_prep/P309_PROTOCOL.md", r"owner (decides|to decide)|open question",
     "rev. 2b text on decisions the owner has since taken (OWNER_DECISIONS_P309_VERBATIM); rev. 2c governs"),
    ("protocol_prep/P309_FORMAL_PACKAGE.md", r"owner (decides|to decide)",
     "rev. 2b text on decisions the owner has since taken; rev. 2c governs"),
]


def files() -> list:
    out = []
    for d in FROZEN_DIRS:
        out += sorted(p for p in (FNS / d).rglob("*") if p.is_file() and "__pycache__" not in p.parts)
    out += [E.RNS / d for d in RNS_DOCS]
    return out


def allowed(rel: str, text: str) -> str | None:
    for suf, pat, why in ALLOW:
        if rel.endswith(suf) and re.search(pat, text, re.I):
            return why
    return None


def run() -> dict:
    hits, allowed_hits = [], []
    for p in files():
        rel = str(p.relative_to(REPO))
        try:
            lines = p.read_text(encoding="utf-8").splitlines()
        except UnicodeDecodeError:
            continue
        for i, line in enumerate(lines, 1):
            for pat, kind in ((MARKERS, "PLACEHOLDER"), (CHOICE, "CHOICE")):
                for m in pat.finditer(line):
                    why = allowed(rel, m.group(0))
                    rec = {"file": rel, "line": i, "kind": kind, "match": m.group(0)}
                    (allowed_hits if why else hits).append(dict(rec, reason=why) if why else rec)
    params = FNS / "freeze" / "P309_FREEZE.json"
    nulls = []
    if params.exists():
        fz = json.loads(params.read_text())
        declared = set(fz.get("post_grant_derivations", {}))

        def walk(x, path):
            if x is None and path.split(".")[0] not in declared:
                nulls.append(path)
            elif isinstance(x, dict):
                for k, v in x.items():
                    walk(v, f"{path}.{k}" if path else k)
            elif isinstance(x, list):
                for j, v in enumerate(x):
                    walk(v, f"{path}[{j}]")
        walk(fz, "")
    return {"pass": not hits and not nulls and params.exists(), "unallowed_hits": hits, "allowed_hits": allowed_hits,
            "nulls_outside_post_grant_derivations": nulls, "freeze_params_present": params.exists()}


if __name__ == "__main__":
    E.log("code/p309_placeholder_check.py", "owner step 11: placeholder / choice scan of the frozen documents",
          klass="GOVERNANCE", notes="static text scan")
    r = run()
    out = {"utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), **r,
           "tool_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
           "head": subprocess.run(["git", "-C", str(REPO), "rev-parse", "HEAD"], capture_output=True,
                                  text=True).stdout.strip()}
    (E.evidence_dir("freeze") / "PLACEHOLDER_CHECK.json").write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    print(json.dumps({"pass": r["pass"], "unallowed": r["unallowed_hits"][:20], "nulls": r["nulls_outside_post_grant_derivations"]},
                     indent=1))
    sys.exit(0 if r["pass"] else 1)
