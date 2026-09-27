"""Administrative / mechanical checks for the K5 PARTIAL closeout, successor R2 (CUSUM m = 5).

Successor of the rejected R1 checker (`p5y_k5_partial_closeout_r1/code/closeout_checks_r1.py`, freeze dfcd8f79,
rejected by review 0d275038) and of the rejected predecessor checker (`p5y_k5_partial_closeout/code/
closeout_checks.py`, freeze 08e9acd1, rejected by 591b4394). Both stay untouched.

NO scientific computation: no Gamma, no TCT input / registry constant / certificate value read into any calculation,
no campaign module imported. Standard library plus read-only `git` only. Rule tables live in `../config/*.json`.

Modes (run from anywhere; paths resolve from this file; interpreter flags -I -S -B are required):
  --snapshot --out F        repository-wide, content-based discovery of every ref carrying K1..K5 / P5Y / SR-K5
                            state; writes the machine-readable relevant-ref snapshot (slow: one history pass)
  --diff SNAPSHOT --out F   re-enumerate all refs, diff against the frozen snapshot, classify every difference,
                            recompute the obligation table; verdict CONTINUE or a STOP class (fail-closed)
  --phase P --out F         administrative checks for phase P in {prefreeze, freeze, adjudication, publication}
"""

from __future__ import annotations

import argparse
import ast
import datetime
import difflib
import hashlib
import json
import pathlib
import re
import subprocess
import sys
from fractions import Fraction as F

HERE = pathlib.Path(__file__).resolve().parent
NS = HERE.parent
REPO = NS.parents[2]
NS_REL = "level4/closure_proofs/p5y_k5_partial_closeout_r2"
CP = "level4/closure_proofs"


def _cfg(name):
    return json.loads((NS / "config" / name).read_text())


REF_RULES = _cfg("REF_RULES_R2.json")
WORDING = _cfg("WORDING_RULES_R2.json")
FIXTURES = _cfg("WORDING_FIXTURES_R2.json")
ALLOW = _cfg("PUBLICATION_ALLOWLIST_R2.json")

BASE = ALLOW["base_commit"]
BRANCH = "refs/heads/p5y-k5-tail-c11rd-d1d2-extension"
LOCAL_MAIN = "c123b9bb8f15d17650545b3fce4aca8a6b61093b"
REMOTE_MAIN = "1cb453826313c189f0bdafd5b84120c1edb74da9"
R5_PATH = f"{CP}/p5y_k5_tail_c2_closure/evidence/coverage/K5_COVERAGE_MAP_R5.json"
R5_BLOB = "f978eeb6b41188eabaf3c6d590c9178d711f1ce6"
GOVERNANCE_REFS = {
    "refs/c11rd/r1-execution-consumed": "4b716d43ce8c48fb52dd320b91c33d2379cce410",
    "refs/c12r2/cell306-pending-result": "0ac46b3d2abe497084ddf7631d894bb819e6ddc6",
    "refs/c12r2/cell306-target-consumed": "dec92e0983fe39bcf9834e62216daeab09f823a4",
}
FORENSIC_OBJECTS = {"b83cc6f5": "blob", "def4e453": "commit", "276f4d41": "commit"}
LOCAL_CHAIN = ["d52cec02", "1667ea88", "27e259f4", "802be11e", "4a4b1392", "2f36352e", "08e9acd1", "591b4394",
               "dfcd8f79ee90ffbb5d04ada43eb7ffd10b44013d", "0d275038fe60252915691df45a31904b27f34c0f"]
PRED_NS = f"{CP}/p5y_k5_partial_closeout"
R1_NS = f"{CP}/p5y_k5_partial_closeout_r1"
PRED_CHECKER_BLOB = "fb297cf2b91b3d685a0aa29c3f6d20b23ff6e547"
R1_CHECKER_BLOB = "aa856b1bc985f17040bfedbb6a16982c734a10e7"
K5_STATUS_PATH = f"{CP}/p5y_k5_remaining_cell_closure/K5_STATUS.md"
K5_STATUS_BLOB = "d212f0d52126cd4c7d062fc11c335484482903b0"
READINESS_PATH = f"{CP}/p5y_k5_order3_readiness_audit/README.md"
READINESS_BLOB = "597c9b2d2fc5370d0ec40e55b3cc546b3f299837"

HISTORICAL_PATHS = [
    f"{CP}/p5y_postk1_precompute_resolution", f"{CP}/p5y_k5_feasibility", f"{CP}/p5y_k5_order3_readiness_audit",
    f"{CP}/p5y_k5b_independent_countersignature", f"{CP}/p5y_k5_remaining_cell_closure",
    f"{CP}/p5y_k5_perron_deflated_resolvent", f"{CP}/p5y_k5_lower_front_order3",
    f"{CP}/p5y_k5_m5_tail_closure", f"{CP}/p5y_k5_tail_operator_registry", f"{CP}/p5y_k5_tail_c2_closure",
    f"{CP}/p5y_k5_tail_c3_closure", f"{CP}/p5y_k5_tail_c4_exhaustion", f"{CP}/p5y_k5_tail_c5_exhaustion",
    f"{CP}/p5y_k5_tail_c6_evidence_recovery", f"{CP}/p5y_k5_tail_c7_e2_lambda309",
    f"{CP}/p5y_k5_tail_c8_operator_feasibility", f"{CP}/p5y_k5_tail_c9_e1_cell307",
    f"{CP}/p5y_k5_tail_c10_governance_provenance", f"{CP}/p5y_k5_tail_c11_n9_independent_certifier",
    f"{CP}/p5y_k5_tail_c11r_n9_statement_alignment", f"{CP}/p5y_k5_tail_c11rd_d1d2_extension",
    f"{CP}/p5y_k5_tail_floor_r2", f"{CP}/p5y_k5_tail_c12_cell306_adoption",
    f"{CP}/p5y_k5_tail_c12r1_cell306_adoption", f"{CP}/p5y_k5_tail_c12r2_cell306_adoption",
    f"{CP}/p5y_k5_tail_route_audit", PRED_NS, R1_NS, f"{CP}/p5y_k5_cusum_first_real_probe_result",
    f"{CP}/p5y_postk1_frontier", "docs/research_synthesis/PS1_CURRENT_STATUS.md",
]

VERDICT_PINS = [
    (f"{CP}/p5y_k5_tail_operator_registry/README.md", "MARGINAL"),
    (f"{CP}/p5y_k5_m5_tail_closure/README.md", "STOPPED"),
    (f"{CP}/p5y_k5_m5_tail_closure/README.md", "INFEASIBLE"),
    (f"{CP}/p5y_k5_tail_c2_closure/evidence/adjudication/C2_ADJUDICATION.md", "PARTIALLY_ADOPTED"),
    (f"{CP}/p5y_k5_tail_c3_closure/evidence/adjudication/C3_ADJUDICATION.md", "VERDICT: REJECTED"),
    (f"{CP}/p5y_k5_tail_c4_exhaustion/evidence/adjudication/C4_ADJUDICATION.md", "ACCEPTED_WITH_SCOPE_LIMITATION"),
    (f"{CP}/p5y_k5_tail_c5_exhaustion/evidence/adjudication/C5_ADJUDICATION.md", "ACCEPTED_WITH_SCOPE_LIMITATION"),
    (f"{CP}/p5y_k5_tail_c6_evidence_recovery/evidence/adjudication/C6_ADJUDICATION.md", "ACCEPTED_WITH_SCOPE_LIMITATION"),
    (f"{CP}/p5y_k5_tail_c7_e2_lambda309/review/ADJUDICATION_C7.md", "ACCEPTED_WITH_CONDITIONS"),
    (f"{CP}/p5y_k5_tail_c8_operator_feasibility/review/ADJUDICATION_C8.md", "ACCEPTED_WITH_CONDITIONS"),
    (f"{CP}/p5y_k5_tail_c9_e1_cell307/STOP_RECORD_C9.md", "EXECUTION_BLOCKED_ON_RUNTIME_AND_AUTHORIZATION"),
    (f"{CP}/p5y_k5_tail_c10_governance_provenance/review/ADJUDICATION_C10.md", "ACCEPTED_WITH_CONDITIONS"),
    (f"{CP}/p5y_k5_tail_c11_n9_independent_certifier/README.md", "EXECUTION_INVALID"),
    (f"{CP}/p5y_k5_tail_c11r_n9_statement_alignment/review/REVIEW_C11R_COMPARISON.md", "AGREEMENT_INSUFFICIENT"),
    (f"{CP}/p5y_k5_tail_c11rd_d1d2_extension/review/C11RD_R1_QUALIFICATION_REVIEW.md", "QUALIFICATION_REJECTED"),
    (f"{CP}/p5y_k5_tail_c11rd_d1d2_extension/adjudication/ADJUDICATION_C11RD_N9.md", "N9_CLOSED"),
    (f"{CP}/p5y_k5_tail_c11rd_d1d2_extension/review/C11RD_ADJUDICATION_REVIEW.md", "ADJUDICATION_ACCEPTED"),
    (f"{CP}/p5y_k5_tail_floor_r2/review/FLOOR_R2_REVIEW.md", "REPLACEMENT_FLOOR_ACCEPTED"),
    (f"{CP}/p5y_k5_tail_c12_cell306_adoption/review/C12_QUALIFICATION_REVIEW.md", "QUALIFICATION_REJECTED"),
    (f"{CP}/p5y_k5_tail_c12r1_cell306_adoption/review/C12R1_QUALIFICATION_REVIEW.md", "QUALIFICATION_REJECTED"),
    (f"{CP}/p5y_k5_tail_c12r2_cell306_adoption/review/C12R2_EXECUTION_REVIEW.md", "EXECUTION_ACCEPTED"),
    (f"{CP}/p5y_k5_tail_c12r2_cell306_adoption/adjudication/C12R2_ADOPTION_ADJUDICATION.md", "CELL306_NOT_ADOPTED"),
    (f"{CP}/p5y_k5_tail_c12r2_cell306_adoption/review/C12R2_ADJUDICATION_REVIEW.md", "ADJUDICATION_ACCEPTED"),
    (f"{CP}/p5y_k5_tail_route_audit/review/ROUTE_AUDIT_REVIEW.md", "ROUTE_AUDIT_REJECTED"),
    (f"{CP}/p5y_k5_tail_route_audit/review/ROUTE_AUDIT_R1_REVIEW.md", "ROUTE_AUDIT_ACCEPTED"),
    (f"{PRED_NS}/review/CLOSEOUT_FREEZE_REVIEW.md", "CLOSEOUT_FREEZE_REJECTED"),
    (f"{R1_NS}/review/CLOSEOUT_FREEZE_REVIEW_R1.md", "CLOSEOUT_FREEZE_REJECTED"),
]

VERDICT_FILES = {
    f"{NS_REL}/review/CLOSEOUT_FREEZE_REVIEW_R2.md": {"CLOSEOUT_FREEZE_ACCEPTED", "CLOSEOUT_FREEZE_REJECTED"},
    f"{NS_REL}/adjudication/K5_CUSUM_FINAL_ADJUDICATION_R2.md": {"K5_CLOSED", "K5_FAIL_MATHEMATICAL", "K5_INCONCLUSIVE"},
    f"{NS_REL}/review/K5_ADJUDICATION_REVIEW_R2.md": {"K5_ADJUDICATION_ACCEPTED", "K5_ADJUDICATION_REJECTED"},
    f"{NS_REL}/review/PUBLICATION_CONFORMANCE_R2.md": {"PUBLICATION_CONFORMANT", "PUBLICATION_NONCONFORMANT"},
}

C11RD = f"{CP}/p5y_k5_tail_c11rd_d1d2_extension"
VALIDATE_PATH, VALIDATE_BLOB = f"{C11RD}/code/c11rd_validate.py", "22293e05417132b4b0e1693126df343e14418a26"
RUNS_PATH, RUNS_BLOB = f"{C11RD}/evidence/runs/C11RD_RUNS.json", "30e2dfd0ac87aad74f8a9490fee99623cbdf151d"
QUALIFY_PATH, QUALIFY_BLOB = f"{C11RD}/qualification_r1q_r1/code/c11rd_qualify.py", "9a55edf196887b62f0e249578a682116b52c364b"
COMPARE_PATH, COMPARE_BLOB = f"{C11RD}/code/c11rd_compare.py", "e536605b0ff9e411483a819433ffb9d34fc6e652"

GIT_ENV = {"PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin", "HOME": "/var/empty",
           "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": "/dev/null", "LC_ALL": "C"}


def git(*args, check=True, stdin_text=None) -> str:
    r = subprocess.run(["git", *args], cwd=REPO, env=GIT_ENV, capture_output=True, text=True,
                       input=stdin_text, stdin=None if stdin_text is not None else subprocess.DEVNULL, timeout=3600)
    if check and r.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)[:160]} failed: {r.stderr.strip()[:300]}")
    return r.stdout


def git_ok(*args) -> bool:
    return subprocess.run(["git", *args], cwd=REPO, env=GIT_ENV, capture_output=True,
                          stdin=subprocess.DEVNULL, timeout=3600).returncode == 0


# ================================================================ hashed-scan helpers (code-identical copies) =====
DEC = re.compile(r"(?<![0-9A-Za-z.])-?([0-9]*\.[0-9]+)(?:[eE]([+-]?[0-9]{1,3}))?(?![0-9A-Za-z])")
INTSCI = re.compile(r"(?<![0-9A-Za-z.])-?([0-9]+)[eE]([+-]?[0-9]{1,3})(?![0-9A-Za-z])")
RAT = re.compile(r"(?<![0-9A-Za-z/.])-?([0-9]+)/([0-9]+)(?![0-9A-Za-z])")
SCALES = (-3, -2, -1, 0, 1, 2, 3)
DECOYS = ("3.141592653", "0.577215664")


def _exp10(x: F) -> int:
    e = len(str(x.numerator // x.denominator)) - 1 if x >= 1 else -1
    while F(10) ** e > x:
        e -= 1
    while F(10) ** (e + 1) <= x:
        e += 1
    return e


def _digits(x: F, n: int, mode: str) -> str:
    e = _exp10(x)
    q = x / F(10) ** (e - n + 1)
    return str(q.__floor__() if mode == "trunc" else (q + F(1, 2)).__floor__())


def _dec_str(x: F, n: int, mode: str) -> str:
    e = _exp10(x)
    unit = e - n + 1
    N = int(_digits(x, n, mode))
    if len(str(N)) > n:
        return _dec_str(F(N) * F(10) ** unit, n, "trunc")
    if unit >= 0:
        return str(N * 10 ** unit)
    s = str(N).rjust(-unit + 1, "0")
    return s[:unit] + "." + s[unit:]


def _rendering_hashes(t: F) -> set:
    out = set()
    for j in SCALES:
        y = t * F(10) ** j
        for k in range(4, 11):
            g = (format(float(y), f".{k}g"),) if k <= 9 and F(1, 10 ** 300) < y < 10 ** 300 else ()
            for r in (_dec_str(y, k, "trunc"), _dec_str(y, k, "round")) + g:
                out.add(hashlib.sha256(r.encode()).hexdigest())
    return out


def _tokens(txt: str) -> list:
    toks = []
    for mnt, ex in DEC.findall(txt):
        toks.append(F(mnt if not mnt.startswith(".") else "0" + mnt) * (F(10) ** int(ex) if ex else 1))
    for mnt, ex in INTSCI.findall(txt):
        toks.append(F(int(mnt)) * F(10) ** int(ex))
    for a, b in RAT.findall(txt):
        if int(b) != 0:
            toks.append(F(int(a), int(b)))
    return [t for t in toks if t > 0]


def value_patterns(s: str) -> set:
    first = next(i for i, ch in enumerate(s) if ch not in "0.")
    out = set()
    for end in range(first + 1, len(s) + 1):
        if s[end - 1].isdigit() and sum(ch.isdigit() for ch in s[first:end]) >= 4:
            out.add(s[:end])
    for n in range(4, 10):
        out.add(format(float(s), f".{n}g"))
    return out


HELPER_SOURCES = {"_exp10": QUALIFY_PATH, "_digits": QUALIFY_PATH, "_dec_str": QUALIFY_PATH,
                  "_rendering_hashes": QUALIFY_PATH, "_tokens": QUALIFY_PATH, "value_patterns": COMPARE_PATH,
                  "DEC": QUALIFY_PATH, "INTSCI": QUALIFY_PATH, "RAT": QUALIFY_PATH, "SCALES": QUALIFY_PATH,
                  "DECOYS": QUALIFY_PATH}


def _defs(src: str) -> dict:
    out = {}
    for n in ast.parse(src).body:
        if isinstance(n, ast.FunctionDef):
            out[n.name] = n
        elif isinstance(n, ast.Assign) and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name):
            out[n.targets[0].id] = n
    return out


def _strip(node):
    node = ast.parse(ast.unparse(node)).body[0]
    if isinstance(node, ast.FunctionDef) and node.body and isinstance(node.body[0], ast.Expr) \
            and isinstance(getattr(node.body[0], "value", None), ast.Constant) \
            and isinstance(node.body[0].value.value, str):
        node.body = node.body[1:]
    return ast.dump(node, include_attributes=False)


def helper_identity() -> dict:
    mine = _defs(pathlib.Path(__file__).read_text())
    src = {p: _defs(git("show", f"HEAD:{p}")) for p in {QUALIFY_PATH, COMPARE_PATH}}
    diff = [n for n, p in HELPER_SOURCES.items() if n not in src[p] or _strip(mine[n]) != _strip(src[p][n])]
    return {"compared": sorted(HELPER_SOURCES), "different": diff}


def _scan(texts: dict, hashes: frozenset) -> dict:
    hits, memo = {}, {}
    for name, txt in texts.items():
        for t in _tokens(txt):
            if t not in memo:
                memo[t] = bool(_rendering_hashes(t) & hashes)
            if memo[t]:
                hits[name] = hits.get(name, 0) + 1
    return hits


def _literal_from_blob(blob: str, name: str):
    for node in ast.parse(git("cat-file", "-p", blob)).body:
        if isinstance(node, ast.Assign) and any(getattr(t, "id", None) == name for t in node.targets):
            return ast.literal_eval(node.value) if not isinstance(node.value, ast.Call) else \
                frozenset(e.value for e in node.value.args[0].elts)
    raise RuntimeError(f"{name} not found in blob {blob}")


def _original_hashes() -> frozenset:
    return _literal_from_blob(git("rev-parse", f"HEAD:{VALIDATE_PATH}").strip(), "ORIGINAL_PATTERN_SHA256")


def _independent_hashes() -> frozenset:
    runs = json.loads(git("show", f"HEAD:{RUNS_PATH}"))
    return frozenset(hashlib.sha256(x.encode()).hexdigest() for k in ("D1", "D2")
                     for x in value_patterns(format(float(F(runs["targets"][k]["value"])), ".12f")))


# ================================================================ wording scan (R2) ==============================
PRED_PHRASES = tuple(_literal_from_blob(PRED_CHECKER_BLOB, "BANNED_PUBLICATION_PHRASES"))
R1_BANNED = _literal_from_blob(R1_CHECKER_BLOB, "BANNED_ASSERTIONS")
R1_NEG = _literal_from_blob(R1_CHECKER_BLOB, "NEGATION_CUES")
R1_SPLIT = _literal_from_blob(R1_CHECKER_BLOB, "CLAUSE_SPLIT")
R1_FIXTURES = _literal_from_blob(R1_CHECKER_BLOB, "WORDING_FIXTURES")
TIER_P = tuple(dict.fromkeys(list(PRED_PHRASES) + list(WORDING["tier_P_additions"])))
TIER_L = {**R1_BANNED, **WORDING["tier_L_additions"]}
CUE = re.compile(r"\b(not|no|never|without)\b")
NEUTRAL = re.compile(WORDING["neutral_insertion_regex"])


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.replace("*", "").replace("`", "")).lower()


def pred_rejects(text: str) -> bool:                       # the predecessor W01, reproduced exactly
    t = re.sub(r"\s+", " ", text).lower()
    return any(b in t for b in PRED_PHRASES)


def r1_rejects(text: str) -> bool:                         # the R1 W01, reproduced exactly
    for clause in re.split(R1_SPLIT, text.lower()):
        for pat in R1_BANNED.values():
            for m in re.finditer(pat, clause):
                if not re.search(R1_NEG, clause[:m.start()]):
                    return True
    return False


def _licensed(n: str, start: int) -> bool:
    cues = list(CUE.finditer(n, 0, start))
    if not cues:
        return False
    between = n[cues[-1].end():start]
    return not re.search(r"[.;:!?]", between) and bool(NEUTRAL.fullmatch(between))


def r2_findings(text: str) -> list:
    n = normalize(text)
    out = [("P", p) for p in TIER_P if p in n]
    for label, pat in TIER_L.items():
        for m in re.finditer(pat, n):
            if not _licensed(n, m.start()):
                out.append(("L", label))
    return out


def predecessor_corpus() -> list:
    out = []
    for p in PRED_PHRASES:
        w = p.replace(" ", "\n", 1)
        for t in FIXTURES["predecessor_corpus_templates"]:
            out.append(t.format(p=p, wrapped=w))
            out.append(t.format(p=p.capitalize(), wrapped=w.capitalize()))
    return out


def wording_selftest() -> dict:
    res = {"fixtures": len(FIXTURES["fixtures"]), "fixture_failures": [], "r1_probe_misses": [],
           "monotonicity_vs_predecessor_violations": [], "monotonicity_vs_r1_violations": []}
    for fx in FIXTURES["fixtures"]:
        got = "REJECT" if r2_findings(fx["text"]) else "ACCEPT"
        if got != fx["expect"]:
            res["fixture_failures"].append({"cat": fx["cat"], "text": fx["text"], "expect": fx["expect"], "got": got})
    res["r1_probe_misses"] = [s for s in FIXTURES["r1_review_probes"] if not r2_findings(s)]
    corpus = predecessor_corpus() + [f["text"] for f in FIXTURES["fixtures"]] + FIXTURES["r1_review_probes"] + \
        [s for v in R1_FIXTURES.values() for s in v]
    res["corpus_size"] = len(corpus)
    res["predecessor_rejects"] = sum(pred_rejects(s) for s in corpus)
    res["r1_rejects"] = sum(r1_rejects(s) for s in corpus)
    res["r2_rejects"] = sum(bool(r2_findings(s)) for s in corpus)
    res["monotonicity_vs_predecessor_violations"] = [s for s in corpus if pred_rejects(s) and not r2_findings(s)]
    res["monotonicity_vs_r1_violations"] = [s for s in corpus if r1_rejects(s) and not r2_findings(s)]
    res["tier_P_size"], res["tier_L_size"], res["predecessor_phrases"] = len(TIER_P), len(TIER_L), len(PRED_PHRASES)
    res["pass"] = not (res["fixture_failures"] or res["r1_probe_misses"] or res["monotonicity_vs_predecessor_violations"]
                       or res["monotonicity_vs_r1_violations"]) and set(PRED_PHRASES) <= set(TIER_P)
    return res


# ================================================================ stale current-state K1 wording ================
STALE_RE = re.compile(ALLOW["stale_detection_regex"])


def stale_status(line: str) -> str:
    low = re.sub(r"\s+", " ", line).lower().strip()
    if not STALE_RE.search(low):
        return "CLEAN"
    n = normalize(line)
    return "MARKED" if "historical status (as recorded " in n and "superseded (" in n else "STALE"


def stale_inventory(files: list, rev: str = None) -> list:
    out = []
    for f in files:
        txt = git("show", f"{rev}:{f}") if rev else (REPO / f).read_text()
        for i, l in enumerate(txt.splitlines(), 1):
            s = stale_status(l)
            if s != "CLEAN":
                out.append({"file": f, "line": i, "text": l, "status": s})
    return out


def correction_ok(new_line: str, stale: dict) -> bool:
    n = normalize(new_line)
    req = ALLOW["correction_form"]["required_substrings_normalized"]
    marker_ok = (not stale["text"].startswith("- ")) or new_line.startswith("- ")
    return marker_ok and all(r in n for r in req) and normalize(stale["claim"]) in n \
        and f"(as recorded {stale['recorded']})" in n


def public_file_check(f: str) -> dict:
    base = git("show", f"{BASE}:{f}").splitlines()
    new = (REPO / f).read_text().splitlines()
    spec = ALLOW["public_files"][f]["insertion"]
    stale = {s["line"]: s for s in ALLOW["stale_lines"] if s["file"] == f}
    problems, inserts, replaced = [], [], set()
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(a=base, b=new, autojunk=False).get_opcodes():
        if tag == "equal":
            continue
        if tag == "insert":
            inserts.append((i1, j1, j2))
            continue
        if tag == "replace" and (i2 - i1) == (j2 - j1) and all((i + 1) in stale and base[i] == stale[i + 1]["text"]
                                                            for i in range(i1, i2)):
            for k in range(i2 - i1):
                if correction_ok(new[j1 + k], stale[i1 + k + 1]):
                    replaced.add(i1 + k + 1)
                else:
                    problems.append(f"bad correction form at new line {j1 + k + 1}")
            continue
        problems.append(f"{tag} base {i1 + 1}-{i2} new {j1 + 1}-{j2} not permitted")
    if set(stale) - replaced:
        problems.append(f"stale lines not superseded: {sorted(set(stale) - replaced)}")
    if len(inserts) != 1:
        problems.append(f"expected exactly one inserted block, found {len(inserts)}")
    else:
        i1, j1, j2 = inserts[0]
        if new[j1].strip() != spec["block_first_line"]:
            problems.append("inserted block does not start with the frozen first line")
        if spec.get("append_at_end"):
            if i1 != len(base):
                problems.append("block not appended at the end")
        else:
            a = next(i for i, l in enumerate(base) if l.startswith(spec["after_heading"]))
            b = next(i for i, l in enumerate(base) if l.startswith(spec["before_heading"]))
            if not (a < i1 <= b):
                problems.append("block not between the frozen headings")
    return {"ok": not problems, "problems": problems, "stale_replaced": sorted(replaced)}


def stale_selftest() -> dict:
    bad = [fx for fx in FIXTURES["stale_line_fixtures"] if stale_status(fx["text"]) != fx["expect"]]
    return {"fixtures": len(FIXTURES["stale_line_fixtures"]), "failures": bad, "pass": not bad}


# ================================================================ repository-wide ref discovery =================
CARRIER_RE = REF_RULES["carrier_regex_ere"]
SCOPE = REF_RULES["search_scope_pathspec"]
OWNERS = REF_RULES["owner_record_types"]
FLAG_RE = re.compile(REF_RULES["positive_closure_flag_regex"])
EXEMPT = tuple(REF_RULES["exempt_prefixes_this_branch"])
_BLOB_CACHE = {}


def blob_text(b: str) -> str:
    if b not in _BLOB_CACHE:
        _BLOB_CACHE[b] = git("cat-file", "-p", b)
    return _BLOB_CACHE[b]


def enumerate_refs() -> list:
    fmt = "%(refname)%09%(objecttype)%09%(objectname)%09%(*objecttype)%09%(*objectname)"
    out = []
    for line in git("for-each-ref", f"--format={fmt}").splitlines():
        name, typ, obj, ptyp, pobj = (line.split("\t") + [""] * 5)[:5]
        peeled_type, peeled = (ptyp, pobj) if typ == "tag" else (typ, obj)
        out.append({"ref": name, "type": typ, "object": obj, "peeled_type": peeled_type, "peeled": peeled})
    return out


def _parse_log(text: str) -> list:
    out, cur = [], None
    for line in text.splitlines():
        if line.startswith("@@"):
            h, date = line[2:].split(" ", 1)
            cur = {"commit": h, "date": date, "files": []}
            out.append(cur)
        elif line.strip() and cur is not None:
            cur["files"].append(line.strip())
    return out


def carrier_history(extra_args=(), stdin_text=None) -> list:
    return _parse_log(git("log", *extra_args, "-G", CARRIER_RE, "--format=@@%H %cI", "--name-only", "--", *SCOPE,
                          stdin_text=stdin_text))


def tip_inventory(commit: str, paths: list) -> dict:
    inv = {}
    for i in range(0, len(paths), 300):
        for line in git("ls-tree", "-r", commit, "--", *paths[i:i + 300]).splitlines():
            meta, path = line.split("\t", 1)
            _, typ, blob = meta.split()
            if typ == "blob":
                inv[path] = blob
    return inv


def tree_carriers(tree: str) -> dict:
    paths = [l.split(":", 1)[1] for l in git("grep", "-l", "-E", CARRIER_RE, tree, "--", *SCOPE, check=False).splitlines()
             if ":" in l]
    return tip_inventory(tree, paths) if paths else {}


def introducing(path: str, blob: str) -> dict:
    lines = git("log", "--all", "--format=%H %cI", f"--find-object={blob}", "--", path).splitlines()
    if not lines:
        return {"commit": None, "date": None}
    h, d = lines[-1].split(" ", 1)
    return {"commit": h, "date": d}


def _is_desc(a: str, b: str) -> bool:        # a descends from (or equals) b
    return a == b or git_ok("merge-base", "--is-ancestor", b, a)


def _json_or_none(blob):
    try:
        return json.loads(blob_text(blob))
    except Exception:                         # noqa: BLE001  (unparseable -> recorded, fail-closed upstream)
        return None


def parse_owner(kind: str, blob: str) -> dict:
    if kind in ("SRK5_OWNER",):
        m = re.search(r"^\| SR K5 \| ([^:|]+)", blob_text(blob), re.M)
        return {"SR_K5": m.group(1).strip() if m else None,
                "CUSUM_K5_STATUS": (re.search(r"K5_STATUS \(CUSUM\)\s*=\s*(\S+)", blob_text(blob)) or [None, None])[1]}
    d = _json_or_none(blob)
    if d is None:
        return {"PARSE_ERROR": True}
    if kind == "K1_OWNER":
        s = d.get("scientific_verdict", {})
        return {k: s.get(k) for k in ("k1_successor_verdict", "k1_scientific_line", "residual_blockers",
                                      "sr_successor_science", "cusum_successor_science")}
    if kind == "K2K3_OWNER":
        return {"countersig": d.get("independent_countersignature", {}).get("K2"),
                "countersig_K3": d.get("independent_countersignature", {}).get("K3"),
                "status": d.get("status")}
    if kind == "K4_OWNER":
        return {k: d.get(k) for k in ("K4R1_SUCCESSOR_VERDICT", "K4_SCIENTIFIC_LINE", "K4_RESIDUAL_BLOCKERS",
                                      "HISTORICAL_K4_COMMIT", "P5Y_STATE")}
    if kind == "K4_HISTORICAL":
        return {"K4_FINAL_VERDICT": d.get("K4_FINAL_VERDICT"), "p5y_state": d.get("p5y_state")}
    if kind == "CUSUMK5_MAP":
        return {"K5_COVERAGE_COMPLETE": d.get("K5_COVERAGE_COMPLETE"), "union_open_ranges": d.get("union_open_ranges")}
    return {}


def _closed(tok) -> bool:
    return isinstance(tok, str) and (tok == "CLOSED" or tok.startswith("CLOSED_BY"))


def reconstruct(tip_inv: dict) -> dict:
    """Owner-record versions over all live commit tips -> current versions -> obligation table (computed)."""
    stops, versions = [], {}
    for kind, spec in OWNERS.items():
        blobs = {}
        for tip, inv in tip_inv.items():
            if spec["path"] in inv:
                blobs.setdefault(inv[spec["path"]], []).append(tip)
        vers = []
        for b, tips in blobs.items():
            vers.append({"blob": b, "live_tips": sorted(tips), "introduced": introducing(spec["path"], b)})
        current = None
        if len(vers) == 1:
            current = vers[0]
        elif len(vers) > 1:
            cands = [v for v in vers if v["introduced"]["commit"] and all(
                w is v or (w["introduced"]["commit"] and _is_desc(v["introduced"]["commit"], w["introduced"]["commit"]))
                for w in vers)]
            if len(cands) == 1:
                current = cands[0]
            else:
                stops.append(("STOP_CONFLICTING_LIVE_RECORDS", kind, [v["blob"] for v in vers]))
        versions[kind] = {"path": spec["path"], "versions": vers, "current": current["blob"] if current else None,
                          "parsed": parse_owner(kind, current["blob"]) if current else None,
                          "introduced": current["introduced"] if current else None}
        if current and versions[kind]["parsed"].get("PARSE_ERROR"):
            stops.append(("STOP_DISCOVERY_ERROR", kind, "unparseable current owner record"))
    for kind in ("K1_OWNER", "K2K3_OWNER", "K4_OWNER", "SRK5_OWNER", "CUSUMK5_MAP"):
        if not versions[kind]["current"]:
            stops.append(("STOP_MISSING_BINDING_RECORD", kind, "no live version"))
    obl = {}
    p = {k: (v["parsed"] or {}) for k, v in versions.items()}
    k1 = p["K1_OWNER"]
    obl["K1"] = "CLOSED" if k1.get("k1_successor_verdict") == "K1_SUCCESSOR_CLOSED" and \
        k1.get("residual_blockers") == "NONE" else k1.get("k1_successor_verdict")
    obl["SR_K1"] = "CLOSED" if obl["K1"] == "CLOSED" and k1.get("sr_successor_science") == "PASS" else \
        k1.get("sr_successor_science")
    st = p["K2K3_OWNER"].get("status") or {}
    obl["K2"] = st.get("K2") if p["K2K3_OWNER"].get("countersig") == "PASS" else "COUNTERSIGNATURE_NOT_PASS"
    obl["K3"] = st.get("K3") if p["K2K3_OWNER"].get("countersig_K3") == "PASS" else "COUNTERSIGNATURE_NOT_PASS"
    k4, k4h = p["K4_OWNER"], p["K4_HISTORICAL"]
    hist_ok = True
    if versions["K4_HISTORICAL"]["current"]:
        hc = versions["K4_HISTORICAL"]["introduced"]["commit"]
        hist_ok = bool(k4.get("HISTORICAL_K4_COMMIT")) and hc is not None and _is_desc(k4.get("HISTORICAL_K4_COMMIT"), hc)
    obl["K4"] = "CLOSED" if k4.get("K4R1_SUCCESSOR_VERDICT") == "CLOSED" and k4.get("K4_RESIDUAL_BLOCKERS") == "NONE" \
        and hist_ok else (k4.get("K4R1_SUCCESSOR_VERDICT") or k4h.get("K4_FINAL_VERDICT"))
    summaries = []
    if versions["K2K3_OWNER"]["current"] and isinstance(st, dict) and "P5Y" in st:
        summaries.append(("K2K3_OWNER", versions["K2K3_OWNER"]["introduced"]["date"], st))
    if versions["K4_HISTORICAL"]["current"] and isinstance(k4h.get("p5y_state"), dict):
        summaries.append(("K4_HISTORICAL", versions["K4_HISTORICAL"]["introduced"]["date"], k4h["p5y_state"]))
    if versions["K4_OWNER"]["current"] and isinstance(k4.get("P5Y_STATE"), dict):
        summaries.append(("K4_OWNER", versions["K4_OWNER"]["introduced"]["date"], k4["P5Y_STATE"]))
    summaries.sort(key=lambda s: datetime.datetime.fromisoformat(s[1]))
    newest = summaries[-1] if summaries else None
    if newest and len(summaries) > 1 and summaries[-2][1] == newest[1] and summaries[-2][2] != newest[2]:
        stops.append(("STOP_CONFLICTING_LIVE_RECORDS", "P5Y_SUMMARY", "two newest summaries disagree"))
    if not newest:
        stops.append(("STOP_MISSING_BINDING_RECORD", "P5Y_SUMMARY", "no live summary"))
    else:
        s = newest[2]
        for ob in ("K1", "K2", "K3", "K4"):
            if _closed(obl[ob]) != _closed(s.get(ob)):
                stops.append(("STOP_CONFLICTING_LIVE_RECORDS", "P5Y_SUMMARY", f"{ob}: owner {obl[ob]} vs summary {s.get(ob)}"))
        obl["K5"], obl["P5Y"] = s.get("K5"), s.get("P5Y")
    obl["SR_K5"] = p["SRK5_OWNER"].get("SR_K5")
    obl["CUSUM_K5_COVERAGE_COMPLETE"] = p["CUSUMK5_MAP"].get("K5_COVERAGE_COMPLETE")
    obl["CUSUM_K5_UNION_OPEN"] = p["CUSUMK5_MAP"].get("union_open_ranges")
    return {"versions": versions, "summary_used": newest[0] if newest else None,
            "summaries": [(s[0], s[1]) for s in summaries], "obligations": obl, "stops": stops}


def _exempt(path: str, commit: str, phase: str) -> bool:
    if path.startswith(EXEMPT) and git_ok("merge-base", "--is-ancestor", commit, "HEAD"):
        return True
    return phase == "publication" and path in REF_RULES["exempt_publication_files_in_phase_publication"] \
        and git_ok("merge-base", "--is-ancestor", commit, "HEAD")


def flag_hits(tip_inv: dict, tree_inv: dict) -> list:
    seen, hits = set(), []
    for inv in list(tip_inv.values()) + list(tree_inv.values()):
        for path, b in inv.items():
            if (path, b) in seen or path.startswith(EXEMPT):
                continue
            seen.add((path, b))
            m = FLAG_RE.search(blob_text(b))
            if m:
                hits.append({"path": path, "blob": b, "match": m.group(0)[:60]})
    return hits


def build_snapshot() -> dict:
    now = datetime.datetime.now(datetime.timezone.utc).astimezone().isoformat(timespec="seconds")
    refs = enumerate_refs()
    hist = carrier_history(("--all",))
    paths = sorted({f for c in hist for f in c["files"]} | {s["path"] for s in OWNERS.values()})
    commit_tips = sorted({r["peeled"] for r in refs if r["peeled_type"] == "commit"})
    tip_inv = {t: tip_inventory(t, paths) for t in commit_tips}
    tree_inv = {r["object"]: tree_carriers(r["object"]) for r in refs if r["type"] == "tree"}
    rec = reconstruct(tip_inv)
    current_blobs = {v["current"] for v in rec["versions"].values() if v["current"]}
    ref_rows = []
    for r in refs:
        if r["ref"] in GOVERNANCE_REFS:
            cls, carriers, owners = "governance (pinned by G01)", 0, []
        elif r["peeled_type"] == "commit":
            inv = tip_inv[r["peeled"]]
            owners = sorted(k for k, s in OWNERS.items() if s["path"] in inv)
            cur = [k for k in owners if inv[OWNERS[k]["path"]] in current_blobs and OWNERS[k]["binding"]]
            carriers = len(inv)
            cls = "binding" if cur else ("informational" if carriers else "unrelated")
        elif r["type"] == "tree":
            inv = tree_inv[r["object"]]
            owners = sorted(k for k, s in OWNERS.items() if s["path"] in inv)
            carriers = len(inv)
            cls = "informational" if carriers else "unrelated"
        else:
            cls, carriers, owners = "unrelated", 0, []
        ref_rows.append({**r, "carrier_files": carriers, "owner_records": owners,
                         "obligations": sorted({o for k in owners for o in OWNERS[k]["obligations"]}),
                         "classification": cls})
    known = sorted({(p, b) for inv in list(tip_inv.values()) + list(tree_inv.values()) for p, b in inv.items()})
    flags = flag_hits(tip_inv, tree_inv)
    stops = list(rec["stops"]) + ([("STOP_POSITIVE_CLOSURE_FLAG", h["path"], h["match"]) for h in flags])
    return {"schema": "rebaseguard.p5y.k5.partial-closeout-r2.ref-snapshot.v1", "observed_at": now,
            "head": git("rev-parse", "HEAD").strip(), "refs_enumerated": len(refs),
            "refs": ref_rows, "commit_tips": commit_tips, "tree_refs": {k: sorted(v.items()) for k, v in tree_inv.items()},
            "carrier_history_commits": len(hist), "carrier_paths": paths, "known_carriers": known,
            "reconstruction": rec, "positive_closure_flags": flags,
            "stops": stops, "verdict": "CONTINUE" if not stops else sorted({s[0] for s in stops})[0],
            "method": "content-based: one `git log --all -G <carrier_regex> --name-only` pass gives every path that ever "
                      "carried or lost status text; every ref (heads, remotes, tags peeled, tree refs, governance refs) is "
                      "enumerated; commit tips are inventoried with `git ls-tree` over those paths; tree refs with "
                      "`git grep`; owner records are parsed and the obligation table is computed from them"}


def diff_snapshot(snap: dict, phase: str) -> dict:
    now = datetime.datetime.now(datetime.timezone.utc).astimezone().isoformat(timespec="seconds")
    out = {"schema": "rebaseguard.p5y.k5.partial-closeout-r2.ref-diff.v1", "observed_at": now, "phase": phase,
           "head": git("rev-parse", "HEAD").strip(), "snapshot_observed_at": snap["observed_at"]}
    stops = []
    try:
        refs = enumerate_refs()
        old = {r["ref"]: r for r in snap["refs"]}
        cur = {r["ref"]: r for r in refs}
        rows = []
        frozen_tips = set(snap["commit_tips"])
        for name in sorted(set(old) | set(cur)):
            o, c = old.get(name), cur.get(name)
            if o and c and o["object"] == c["object"]:
                kind = "unchanged"
            elif o and c:
                kind = "moved"
            elif c:
                twin = [n for n, r in old.items() if n not in cur and r["object"] == c["object"]]
                kind = "renamed-equivalent" if twin else "new"
            else:
                kind = "deleted"
            rows.append({"ref": name, "change": kind, "old": o and o["object"], "new": c and c["object"],
                         "old_class": o and o["classification"]})
        out["ref_changes"] = [r for r in rows if r["change"] != "unchanged"]
        neg = "".join(f"^{t}\n" for t in sorted(frozen_tips))
        new_commits = [l for l in git("rev-list", "--all", "--stdin", stdin_text=neg).splitlines() if l]
        out["new_commits"] = len(new_commits)
        touched = carrier_history(("--all", "--stdin"), stdin_text=neg) if new_commits else []
        known_paths = set(snap["carrier_paths"])
        by_path = _parse_log(git("log", "--all", "--stdin", "--format=@@%H %cI", "--name-only", "--", *sorted(known_paths),
                                 stdin_text=neg)) if new_commits else []
        cls = []
        for c in {x["commit"]: x for x in touched + by_path}.values():
            files = sorted(set(c["files"]))
            verdicts = []
            for f in files:
                if _exempt(f, c["commit"], phase):
                    verdicts.append((f, "exempt (this closeout's own namespace or permitted publication file)"))
                elif f in {s["path"] for s in OWNERS.values()}:
                    verdicts.append((f, "known owner record changed -> recompared below"))
                else:
                    verdicts.append((f, "UNEXPLAINED"))
                    stops.append(("STOP_AMBIGUOUS_CROSS_REF_STATE", f, c["commit"][:10]))
            cls.append({"commit": c["commit"], "date": c["date"], "files": verdicts})
        out["new_carrier_commits"] = cls
        paths = sorted(known_paths | {f for c in touched for f in c["files"]})
        tips = sorted({r["peeled"] for r in refs if r["peeled_type"] == "commit"})
        tip_inv = {t: tip_inventory(t, paths) for t in tips}
        tree_inv = {}
        old_trees = snap["tree_refs"]
        known = {tuple(x) for x in snap["known_carriers"]}
        for r in refs:
            if r["type"] == "tree":
                if r["object"] in old_trees:
                    tree_inv[r["object"]] = dict(old_trees[r["object"]])
                    continue
                inv = tree_carriers(r["object"])
                tree_inv[r["object"]] = inv
                for p, b in inv.items():
                    if (p, b) not in known and not p.startswith(EXEMPT):
                        stops.append(("STOP_AMBIGUOUS_CROSS_REF_STATE", p, f"new carrier in tree ref {r['ref']}"))
        rec = reconstruct(tip_inv)
        stops += rec["stops"]
        snap_obl = snap["reconstruction"]["obligations"]
        out["obligations_frozen"], out["obligations_now"] = snap_obl, rec["obligations"]
        if rec["obligations"] != snap_obl:
            stops.append(("STOP_INCOMPATIBLE_BINDING_DRIFT", "obligations", "recomputed table differs from the snapshot"))
        drift = []
        for kind, v in rec["versions"].items():
            sv = snap["reconstruction"]["versions"][kind]
            if v["current"] != sv["current"]:
                drift.append({"record": kind, "frozen": sv["current"], "now": v["current"]})
            snap_live = set(t for x in sv["versions"] if x["blob"] == sv["current"] for t in x["live_tips"])
            now_live = set(t for x in v["versions"] if x["blob"] == v["current"] for t in x["live_tips"])
            if snap_live != now_live:
                drift.append({"record": kind, "live_tips_frozen": sorted(snap_live), "live_tips_now": sorted(now_live)})
        out["binding_record_drift"] = drift
        out["compatible_drift"] = bool(drift) and not stops
        flags = flag_hits(tip_inv, tree_inv)
        new_flags = [h for h in flags if (h["path"], h["blob"]) not in known]
        stops += [("STOP_POSITIVE_CLOSURE_FLAG", h["path"], h["match"]) for h in new_flags]
        out["reconstruction_now"] = rec
    except Exception as exc:                                  # noqa: BLE001  (fail closed, with output)
        stops.append(("STOP_DISCOVERY_ERROR", type(exc).__name__, str(exc)[:300]))
    out["stops"] = stops
    out["verdict"] = "CONTINUE" if not stops else sorted({s[0] for s in stops})[0]
    out["pass"] = not stops
    return out


# ================================================================ administrative phase checks ===================
def changed_since_base() -> list:
    tracked = git("diff", "--name-only", BASE, "--").splitlines()
    status = [l[3:] for l in git("status", "--porcelain", "--ignored", "--untracked-files=all").splitlines()]
    return sorted(set(tracked + status))


def allowed_paths(phase: str) -> set:
    order = ALLOW["phase_order"]
    upto = max(order.index(phase), order.index("freeze"))      # the freeze files exist from the pre-freeze run on
    ok = {f"{ALLOW['namespace']}/{p}" for p, ph in ALLOW["namespace_files"].items() if order.index(ph) <= upto}
    if phase == "publication":
        ok |= set(ALLOW["public_files"])
    return ok


def freeze_commit() -> str | None:
    lines = git("log", "--diff-filter=A", "--format=%H", "--",
                f"{NS_REL}/protocol/K5_PARTIAL_CLOSEOUT_PROTOCOL_R2.md").splitlines()
    return lines[-1] if len(lines) == 1 else (None if not lines else "AMBIGUOUS")


def identity_check(phase: str) -> dict:
    fc = freeze_commit()
    if fc in (None, "AMBIGUOUS"):
        return {"ok": False, "freeze_commit": fc}
    diffs = []
    for p in ALLOW["frozen_files"]:
        full = f"{NS_REL}/{p}"
        if p == "README.md" and phase == "publication":
            continue
        fb = git("rev-parse", f"{fc}:{full}").strip()
        hb = git("rev-parse", f"HEAD:{full}", check=False).strip()
        wb = git("hash-object", str(REPO / full)).strip() if (REPO / full).exists() else None
        if not (fb == hb == wb):
            diffs.append({"file": p, "freeze": fb, "head": hb, "worktree": wb})
    later = [p for p in ALLOW["frozen_files"] if p != "README.md" and
             git("log", "--format=%H", f"{fc}..HEAD", "--", f"{NS_REL}/{p}").strip()]
    return {"ok": not diffs and not later, "freeze_commit": fc, "different": diffs, "touched_after_freeze": later,
            "files": len(ALLOW["frozen_files"])}


def cross_ref_path_exists(path: str) -> bool:
    snap_p = NS / "evidence" / "REF_SNAPSHOT_R2.json"
    if not snap_p.exists():
        return False
    snap = json.loads(snap_p.read_text())
    for kind, v in snap["reconstruction"]["versions"].items():
        for ver in v["versions"]:
            for tip in ver["live_tips"]:
                if git_ok("cat-file", "-e", f"{tip}:{path}"):
                    return True
    return False


def closeout_texts(extra_commit_msgs=True) -> dict:
    texts = {}
    for p in sorted((REPO / NS_REL).rglob("*")):
        if p.is_file() and "__pycache__" not in p.parts:
            texts[str(p.relative_to(REPO))] = p.read_text(errors="replace")
    for f in ALLOW["public_files"]:
        added = "\n".join(l[1:] for l in git("diff", BASE, "--", f).splitlines()
                          if l.startswith("+") and not l.startswith("+++"))
        if added:
            texts[f + " (added lines)"] = added
    if extra_commit_msgs:
        texts["commit messages since base"] = git("log", "--format=%B", f"{BASE}..HEAD")
    return texts


def run_checks(phase: str) -> dict:
    out = []

    def add(cid, ok, detail):
        out.append({"id": cid, "pass": bool(ok), "detail": detail})

    head = git("rev-parse", "HEAD").strip()
    add("S01 branch", git("symbolic-ref", "HEAD").strip() == BRANCH, BRANCH)
    add("S02 base (R1 freeze review 0d275038) is ancestor of HEAD", git_ok("merge-base", "--is-ancestor", BASE, "HEAD"), BASE)
    add("S03 rejected chains preserved in HEAD (route audit, predecessor 08e9acd1/591b4394, R1 dfcd8f79/0d275038)",
        all(git_ok("merge-base", "--is-ancestor", c, "HEAD") for c in LOCAL_CHAIN), LOCAL_CHAIN)
    add("S04 local main unchanged", git("rev-parse", "refs/heads/main").strip() == LOCAL_MAIN, LOCAL_MAIN)
    add("S05 remote main unchanged", git("rev-parse", "refs/remotes/origin/main").strip() == REMOTE_MAIN, REMOTE_MAIN)
    remote = [r for r in git("for-each-ref", "--format=%(refname)", "refs/remotes").splitlines()
              if r.endswith("/p5y-k5-tail-c11rd-d1d2-extension")]
    add("S06 no remote copy of the branch", not remote, remote)
    add("S07 no upstream configured", not git_ok("config", "--get", "branch.p5y-k5-tail-c11rd-d1d2-extension.remote"), "")

    add("C01 r5 blob unchanged", git("rev-parse", f"HEAD:{R5_PATH}").strip() == R5_BLOB, R5_BLOB)
    r5 = json.loads(git("show", f"HEAD:{R5_PATH}"))
    add("C02 r5: m=5 open [[306,309]], m=1,2,3 open [], union [[306,309]], K5_COVERAGE_COMPLETE false",
        r5["per_m"]["5"]["open_ranges"] == [[306, 309]] and all(r5["per_m"][m]["open_ranges"] == [] for m in "123")
        and r5["union_open_ranges"] == [[306, 309]] and r5["K5_COVERAGE_COMPLETE"] is False, "structure only")
    r6t = [p for p in git("ls-files").splitlines() if re.search(r"coverage_map_r6", p, re.I)]
    r6d = [str(p.relative_to(REPO)) for p in REPO.rglob("*") if re.search(r"coverage_map_r6", p.name, re.I)
           and ".git" not in p.parts]
    add("C03 no r6 in this worktree (tracked or on disk)", not r6t and not r6d, r6t + r6d)

    refs = dict(l.split(" ", 1)[::-1] for l in git("for-each-ref", "--format=%(objectname) %(refname)").splitlines())
    gov = {k: v for k, v in refs.items() if k.startswith(("refs/c11rd/", "refs/c12r2/", "refs/c12r1/", "refs/c12/"))}
    add("G01 governance refs exactly as pinned", gov == GOVERNANCE_REFS, sorted(gov))
    add("G02 forensic objects present", all(git("cat-file", "-t", o).strip() == t for o, t in FORENSIC_OBJECTS.items()),
        FORENSIC_OBJECTS)

    hc = git("diff", "--name-only", BASE, "HEAD", "--", *HISTORICAL_PATHS).splitlines()
    hd = git("status", "--porcelain", "--ignored", "--", *HISTORICAL_PATHS).splitlines()
    add("H01 historical namespaces (incl. both rejected closeouts and PS1_CURRENT_STATUS.md) byte-identical to base",
        not hc and not hd, hc + hd)
    miss = [(p, t) for p, t in VERDICT_PINS if t not in git("show", f"HEAD:{p}")]
    add("H02 historical verdict tokens present", not miss, {"pins": len(VERDICT_PINS), "missing": miss})
    add("H03 SR-K5 status files unchanged",
        git("rev-parse", f"HEAD:{K5_STATUS_PATH}").strip() == K5_STATUS_BLOB
        and git("rev-parse", f"HEAD:{READINESS_PATH}").strip() == READINESS_BLOB, [K5_STATUS_BLOB, READINESS_BLOB])

    changed = changed_since_base()
    allowed = allowed_paths(phase)
    add("P01 exact allowlist: every path changed since base (tracked, untracked, ignored) is allowed in this phase",
        not [p for p in changed if p not in allowed], {"unexpected": [p for p in changed if p not in allowed],
                                                       "changed": changed})
    if phase == "publication":
        pf = {f: public_file_check(f) for f in ALLOW["public_files"]}
        add("P02 public files: only the frozen stale lines replaced in correction form + one block at the frozen place",
            all(v["ok"] for v in pf.values()), pf)
        inv = stale_inventory(list(ALLOW["public_files"]))
        add("P03 no unmarked stale current-state K1 line remains in the public files",
            not [s for s in inv if s["status"] == "STALE"], inv)
    else:
        add("P02 public files byte-identical to base before publication",
            not git("diff", "--name-only", BASE, "--", *ALLOW["public_files"]).strip(), list(ALLOW["public_files"]))
        det = stale_inventory(list(ALLOW["public_files"]), rev=BASE)
        want = {(s["file"], s["line"], s["text"]) for s in ALLOW["stale_lines"]}
        got = {(s["file"], s["line"], s["text"]) for s in det if s["status"] == "STALE"}
        out_det = stale_inventory(["docs/research_synthesis/PS1_CURRENT_STATUS.md"], rev=BASE)
        want_out = {(s["file"], s["line"], s["text"]) for s in ALLOW["stale_outside_allowlist"]}
        got_out = {(s["file"], s["line"], s["text"]) for s in out_det if s["status"] == "STALE"}
        add("P03 stale-line detection at base equals the frozen stale_lines (allowlisted) and stale_outside_allowlist",
            got == want and got_out == want_out, {"allowlisted_detected": sorted(got), "outside_detected": sorted(got_out)})
    add("P04 no __pycache__ or .pyc in the R2 namespace",
        not [p for p in (REPO / NS_REL).rglob("*") if "__pycache__" in p.parts or p.suffix == ".pyc"], NS_REL)

    fmt = {}
    for rel, vocab in VERDICT_FILES.items():
        p = REPO / rel
        if p.is_file():
            lines = p.read_text().splitlines()
            fmt[rel] = len(lines) > 1 and lines[1] in vocab
    add("F01 verdict-line format of R2 review/adjudication documents present so far", all(fmt.values()), fmt)

    if phase in ("freeze", "adjudication", "publication"):
        ic = identity_check(phase)
        add("I01 post-freeze identity: every frozen R2 file byte-identical to the freeze commit (blob, HEAD, worktree)",
            ic["ok"], ic)

    cited, miss_c = set(), []
    pat = re.compile(r"`((?:level4|docs|p5y_[a-z0-9_]+)/[^`\s:]+?)(?::\d+(?:[-–]\d+)?)?`")
    order = ALLOW["phase_order"]
    future = {f"{NS_REL}/{p}" for p, ph in ALLOW["namespace_files"].items()
              if order.index(ph) > order.index(phase) or p.startswith("evidence/")}
    for rel, txt in closeout_texts(extra_commit_msgs=False).items():
        if rel.endswith(".md") or rel.endswith("(added lines)"):
            cited.update(pat.findall(txt))
    for c in sorted(cited):
        if any(ch in c for ch in "{}*<>…") or c in future:
            continue
        if any((REPO / x).exists() for x in (c, f"{CP}/{c}")) or cross_ref_path_exists(c):
            continue
        miss_c.append(c)
    add("R01 every cited repository path exists (worktree, or at a live tip carrying the owner record)", not miss_c,
        {"cited": len(cited), "missing": miss_c})

    ws = wording_selftest()
    add("T01 wording fixtures, R1-probe catches, and no-weakening monotonicity (R2 ⊇ predecessor, R2 ⊇ R1)", ws["pass"], ws)
    ss = stale_selftest()
    add("T02 stale-line classifier fixtures", ss["pass"], ss)
    pub = {k: v for k, v in closeout_texts(extra_commit_msgs=False).items()
           if k.startswith(f"{NS_REL}/publication/") or k == f"{NS_REL}/README.md" or k.endswith("(added lines)")}
    wf = {k: r2_findings(v) for k, v in pub.items()}
    wf = {k: v for k, v in wf.items() if v}
    add("W01 publication-facing text makes no banned assertion (R2 rule)", not wf, {"files": sorted(pub), "findings": wf})

    orig, ind = _original_hashes(), _independent_hashes()
    texts = closeout_texts()
    dh = frozenset(hashlib.sha256(x.encode()).hexdigest() for d in DECOYS for x in value_patterns(d))
    pos = _scan({"planted": f"a bound of {DECOYS[0][:7]} and {DECOYS[1][:9]}"}, dh)
    neg = _scan({"clean": "values 1.23456 and 7/9 and 2.5e3"}, dh)
    oh, ih = _scan(texts, orig), _scan(texts, ind)
    add("L01 value-free leak scan: 0 original / 0 independent D1/D2 renderings; decoys behave",
        len(orig) == 17 and not oh and not ih and pos and not neg,
        {"files_scanned": len(texts), "original_hits": len(oh), "independent_hits": len(ih),
         "decoy_positive_fired": bool(pos), "decoy_negative_quiet": not neg, "hit_files": sorted(set(oh) | set(ih))})
    add("L02 hash-set, helper and predecessor/R1 checker sources at pinned blobs",
        [git("rev-parse", f"HEAD:{p}").strip() for p in (VALIDATE_PATH, RUNS_PATH, QUALIFY_PATH, COMPARE_PATH)]
        == [VALIDATE_BLOB, RUNS_BLOB, QUALIFY_BLOB, COMPARE_BLOB]
        and git("rev-parse", f"HEAD:{PRED_NS}/code/closeout_checks.py").strip() == PRED_CHECKER_BLOB
        and git("rev-parse", f"HEAD:{R1_NS}/code/closeout_checks_r1.py").strip() == R1_CHECKER_BLOB, "6 blobs")
    hi = helper_identity()
    add("L03 scan helpers code-identical (AST, docstrings ignored) to cited sources", not hi["different"], hi)

    if phase == "publication":
        r = subprocess.run([sys.executable, "-I", "-S", "-B", "docs/research_synthesis/verify_synthesis.py",
                            "--no-diff-check"], cwd=REPO, capture_output=True, text=True,
                           stdin=subprocess.DEVNULL, timeout=600)
        add("V01 research-synthesis document verifier (--no-diff-check) passes",
            r.returncode == 0 and "SYNTHESIS VERIFICATION OK" in r.stdout, (r.stdout or r.stderr).strip()[:200])

    return {"schema": "rebaseguard.p5y.k5.partial-closeout-r2.admin-checks.v1", "phase": phase, "head": head,
            "base": BASE, "scientific_computation": "NONE (administrative checks only)", "checks": out,
            "pass": all(c["pass"] for c in out), "summary": f"{sum(c['pass'] for c in out)}/{len(out)}"}


def main() -> int:
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--phase", choices=ALLOW["phase_order"])
    g.add_argument("--snapshot", action="store_true")
    g.add_argument("--diff", metavar="SNAPSHOT_JSON")
    ap.add_argument("--diff-phase", choices=ALLOW["phase_order"], default="adjudication")
    ap.add_argument("--out")
    a = ap.parse_args()
    if not (sys.flags.isolated and sys.flags.no_site and sys.flags.dont_write_bytecode):
        print("refused: run with python3 -I -S -B", file=sys.stderr)
        return 2
    if a.snapshot:
        res = build_snapshot()
        res["pass"] = res["verdict"] == "CONTINUE"
    elif a.diff:
        res = diff_snapshot(json.loads(pathlib.Path(a.diff).read_text()), a.diff_phase)
    else:
        res = run_checks(a.phase)
    txt = json.dumps(res, indent=1, sort_keys=True, default=list) + "\n"
    if a.out:
        pathlib.Path(a.out).write_text(txt)
    print(txt if not a.out else f"{res.get('summary', res.get('verdict', ''))} pass={res['pass']} -> {a.out}")
    return 0 if res["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
