"""Administrative / mechanical checks for the K5 PARTIAL closeout, successor R1 (CUSUM m = 5).

Successor of `p5y_k5_partial_closeout/code/closeout_checks.py` (frozen at 08e9acd1; that freeze was REJECTED by
review 591b4394). This file is new; the predecessor is untouched.

This module performs NO scientific computation. It never evaluates Gamma, never reads a TCT input, registry
constant or certificate value into any calculation, and imports no module of any campaign. It uses only the
standard library and read-only `git`:

* repository state, refs, ancestry, blob identity;
* byte-identity of historical namespaces (now including the rejected predecessor closeout) against the base;
* presence of pinned historical verdict tokens;
* an EXACT per-phase allowlist of changed paths (tracked, untracked AND ignored files);
* additive-only and placement rules for the three permitted public publication edits;
* existence of cited repository paths; verdict-line format of review / adjudication documents;
* a clause-aware overclaim-wording scan with regression fixtures (prohibited / negated / scoped);
* a value-free hashed leak scan (original and independent D1/D2 renderings, never printed), whose helper
  functions are checked to be code-identical (AST, docstrings ignored) to their cited source blobs;
* a cross-ref snapshot of the current P5Y state read from CURRENT REF TIPS (never from remembered commit ids),
  with a frozen binding/informational classification and a frozen drift rule.

Usage (from anywhere; paths resolve from this file):
  python3 -I -S -B closeout_checks_r1.py --phase {prefreeze,freeze,adjudication,publication} [--out FILE]
  python3 -I -S -B closeout_checks_r1.py --xref [--out FILE]          (slow: several pickaxe passes over all refs)
"""

from __future__ import annotations

import argparse
import ast
import datetime
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
NS_REL = "level4/closure_proofs/p5y_k5_partial_closeout_r1"
CP = "level4/closure_proofs"
PRED_NS = f"{CP}/p5y_k5_partial_closeout"

BASE = "591b43948a07e5fd916de37b3ef4d38830bb7b94"          # predecessor freeze-review commit = pre-R1 HEAD
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
LOCAL_CHAIN = ["d52cec02", "1667ea88", "27e259f4", "802be11e", "4a4b1392", "2f36352e", "08e9acd1", "591b4394"]
K5_STATUS_PATH = f"{CP}/p5y_k5_remaining_cell_closure/K5_STATUS.md"
K5_STATUS_BLOB = "d212f0d52126cd4c7d062fc11c335484482903b0"
READINESS_PATH = f"{CP}/p5y_k5_order3_readiness_audit/README.md"
READINESS_BLOB = "597c9b2d2fc5370d0ec40e55b3cc546b3f299837"
SR_K5_TEXT = "| SR K5 | NOT STARTED: needs SR K1 records, plus an SR order-3 producer (`AUX3_SR_FEASIBILITY_FAIL` on record) |"

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
    f"{CP}/p5y_k5_tail_route_audit", PRED_NS, f"{CP}/p5y_k5_cusum_first_real_probe_result",
    f"{CP}/p5y_postk1_frontier",
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
    (f"{CP}/p5y_k5_tail_c11r_n9_statement_alignment/review/REVIEW_C11R_COMPARISON.md", "VERDICT: COMPARISON_ACCEPTED"),
    (f"{CP}/p5y_k5_tail_c11rd_d1d2_extension/review/C11RD_R1_QUALIFICATION_REVIEW.md", "QUALIFICATION_REJECTED"),
    (f"{CP}/p5y_k5_tail_c11rd_d1d2_extension/adjudication/ADJUDICATION_C11RD_N9.md", "N9_CLOSED"),
    (f"{CP}/p5y_k5_tail_c11rd_d1d2_extension/review/C11RD_ADJUDICATION_REVIEW.md", "ADJUDICATION_ACCEPTED"),
    (f"{CP}/p5y_k5_tail_floor_r2/review/FLOOR_R2_REVIEW.md", "REPLACEMENT_FLOOR_ACCEPTED"),
    (f"{CP}/p5y_k5_tail_c12_cell306_adoption/review/C12_QUALIFICATION_REVIEW.md", "QUALIFICATION_REJECTED"),
    (f"{CP}/p5y_k5_tail_c12r1_cell306_adoption/review/C12R1_QUALIFICATION_REVIEW.md", "QUALIFICATION_REJECTED"),
    (f"{CP}/p5y_k5_tail_c12r2_cell306_adoption/review/C12R2_QUALIFICATION_REVIEW.md", "QUALIFICATION_ACCEPTED"),
    (f"{CP}/p5y_k5_tail_c12r2_cell306_adoption/review/C12R2_EXECUTION_REVIEW.md", "EXECUTION_ACCEPTED"),
    (f"{CP}/p5y_k5_tail_c12r2_cell306_adoption/adjudication/C12R2_ADOPTION_ADJUDICATION.md", "CELL306_NOT_ADOPTED"),
    (f"{CP}/p5y_k5_tail_c12r2_cell306_adoption/review/C12R2_ADJUDICATION_REVIEW.md", "ADJUDICATION_ACCEPTED"),
    (f"{CP}/p5y_k5_tail_route_audit/review/ROUTE_AUDIT_REVIEW.md", "ROUTE_AUDIT_REJECTED"),
    (f"{CP}/p5y_k5_tail_route_audit/review/ROUTE_AUDIT_R1_REVIEW.md", "ROUTE_AUDIT_ACCEPTED"),
    (f"{PRED_NS}/review/CLOSEOUT_FREEZE_REVIEW.md", "CLOSEOUT_FREEZE_REJECTED"),
]

# ---- exact artifact allowlist (protocol R1 §13): every path that may differ from BASE, per phase -----------------
NS_FREEZE_FILES = ["README.md", "protocol/K5_PARTIAL_CLOSEOUT_PROTOCOL_R1.md", "code/closeout_checks_r1.py",
                   "evidence/PREFREEZE_CHECKS_R1.json", "evidence/XREF_SNAPSHOT_R1.json"]
NS_LATER_FILES = {
    "review/CLOSEOUT_FREEZE_REVIEW_R1.md": "adjudication",
    "evidence/PREADJUDICATION_XREF_R1.json": "adjudication",
    "adjudication/K5_CUSUM_FINAL_ADJUDICATION_R1.md": "adjudication",
    "review/K5_ADJUDICATION_REVIEW_R1.md": "publication",
    "evidence/PREPUBLICATION_XREF_R1.json": "publication",
    "publication/K5_CUSUM_CLOSEOUT_STATUS.md": "publication",
    "evidence/PUBLICATION_CHECKS_R1.json": "publication",
    "review/PUBLICATION_CONFORMANCE_R1.md": "publication",
}
PUBLIC_ADDITIVE_FILES = ["README.md", "docs/research_synthesis/README.md",
                         "docs/research_synthesis/LIMITATIONS_AND_OPEN_ITEMS.md"]
PHASE_ORDER = ["prefreeze", "freeze", "adjudication", "publication"]

VERDICT_FILES = {
    f"{NS_REL}/review/CLOSEOUT_FREEZE_REVIEW_R1.md": {"CLOSEOUT_FREEZE_ACCEPTED", "CLOSEOUT_FREEZE_REJECTED"},
    f"{NS_REL}/adjudication/K5_CUSUM_FINAL_ADJUDICATION_R1.md": {"K5_CLOSED", "K5_FAIL_MATHEMATICAL", "K5_INCONCLUSIVE"},
    f"{NS_REL}/review/K5_ADJUDICATION_REVIEW_R1.md": {"K5_ADJUDICATION_ACCEPTED", "K5_ADJUDICATION_REJECTED"},
    f"{NS_REL}/review/PUBLICATION_CONFORMANCE_R1.md": {"PUBLICATION_CONFORMANT", "PUBLICATION_NONCONFORMANT"},
}

C11RD = f"{CP}/p5y_k5_tail_c11rd_d1d2_extension"
VALIDATE_PATH, VALIDATE_BLOB = f"{C11RD}/code/c11rd_validate.py", "22293e05417132b4b0e1693126df343e14418a26"
RUNS_PATH, RUNS_BLOB = f"{C11RD}/evidence/runs/C11RD_RUNS.json", "30e2dfd0ac87aad74f8a9490fee99623cbdf151d"
QUALIFY_PATH, QUALIFY_BLOB = f"{C11RD}/qualification_r1q_r1/code/c11rd_qualify.py", "9a55edf196887b62f0e249578a682116b52c364b"
COMPARE_PATH, COMPARE_BLOB = f"{C11RD}/code/c11rd_compare.py", "e536605b0ff9e411483a819433ffb9d34fc6e652"

# ---- cross-ref facts (protocol R1 §4): refs are read at their CURRENT tips -------------------------------------
K1_REF = "refs/heads/p5y-k1-successor-final-assembly"
K1_FILE = f"{CP}/p5y_k1_successor_final_adjudication/evidence/FINAL_ADJUDICATION.json"
K1_EXPECTED = {"k1_successor_verdict": "K1_SUCCESSOR_CLOSED", "k1_scientific_line": "CLOSED_BY_LATER_SUCCESSOR_CAMPAIGN",
               "residual_blockers": "NONE", "sr_successor_science": "PASS", "cusum_successor_science": "PASS"}
K2K3_REF = "refs/heads/p5y-k2-k3-final-closure"
K2K3_FILE = f"{CP}/p5y_k2_k3_final_countersignature/FINAL_COUNTERSIGNATURE.json"
K4_REF = "refs/heads/p5y-k4r1-final-closure"
K4_FILE = f"{CP}/p5y_k4r1_final_adjudication/K4R1_FINAL_VERDICT.json"
K4_EXPECTED = {"K4R1_SUCCESSOR_VERDICT": "CLOSED", "K4_SCIENTIFIC_LINE": "CLOSED_BY_LATER_SUCCESSOR_CAMPAIGN",
               "K4_RESIDUAL_BLOCKERS": "NONE"}
P5Y_EXPECTED = {"K1": "CLOSED_BY_LATER_SUCCESSOR_CAMPAIGN", "K2": "CLOSED", "K3": "CLOSED",
                "K4": "CLOSED_BY_LATER_SUCCESSOR_CAMPAIGN", "K5": "OPEN", "P5Y": "NOT_YET_CLOSED"}
# Cross-ref artifacts cited by the protocol: they exist at the CURRENT tip of the named ref, not in this worktree.
XREF_ARTIFACTS = {K1_FILE: K1_REF, K2K3_FILE: K2K3_REF, K4_FILE: K4_REF,
                  f"{CP}/p5y_k4r1_final_adjudication/README.md": K4_REF}
INFORMATIONAL_REFS = [
    "refs/heads/p5y-k1-successor-final-assembly", "refs/remotes/origin/p5y-k1-successor-final-assembly",
    "refs/heads/p5y-k2-k3-final-closure", "refs/remotes/origin/p5y-k2-k3-final-closure",
    "refs/heads/p5y-k4r1-final-closure", "refs/remotes/origin/p5y-k4r1-final-closure",
    "refs/heads/p5y-k4-frozen-execution-r1", "refs/heads/p5y-k4r1-nearzero-successor",
    "refs/heads/p5y-k1-final-evidence", "refs/remotes/origin/p5y-postk1-frontier", BRANCH,
]
SR_K5_REGEX = r"SR K5|SR_K5|K5_SR|K5 \(SR\)|SR-side K5|SR/K5|SR half of K5|SR side of K5"
SR_K5_ALLOWED_COMMITS = {"a3547b9be694e04badb16bffcb01eaf9e9d413cd",   # K5_STATUS.md: SR K5 NOT STARTED (09-19)
                         "e86809982f4a47b96aa59aee4fd7a3b180402598"}   # readiness audit: K5_SR_K1_INPUTS_EXIST = NO
SR_K5_ALLOWED_PREFIXES = (f"{CP}/p5y_k5_tail_route_audit/", f"{PRED_NS}/", f"{NS_REL}/")
# Structured closure records only. (A bare "K5 CLOSED" matched two meta-mentions -- a C2 review's sweep list,
# d6a4def5, and a readiness-audit test's forbidden-string list, e8680998 -- which are not closure records.)
K5_CLOSED_REGEX = r'K5_DECLARED_CLOSED *(=|:) *"?(YES|true|True)|"K5": *"CLOSED|K5 = CLOSED|K5 CLOSED_BY|K5: CLOSED'
P5Y_CLOSED_REGEX = r'P5Y_DECLARED_CLOSED *(=|:) *"?(YES|true|True)|"P5Y": *"CLOSED"|P5Y = CLOSED|P5Y_STATUS = CLOSED'

GIT_ENV = {"PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin", "HOME": "/var/empty",
           "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": "/dev/null", "LC_ALL": "C"}


def git(*args, check=True) -> str:
    r = subprocess.run(["git", *args], cwd=REPO, env=GIT_ENV, capture_output=True, text=True,
                       stdin=subprocess.DEVNULL, timeout=1800)
    if check and r.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)[:120]} failed: {r.stderr.strip()[:300]}")
    return r.stdout


def git_ok(*args) -> bool:
    return subprocess.run(["git", *args], cwd=REPO, env=GIT_ENV, capture_output=True,
                          stdin=subprocess.DEVNULL, timeout=1800).returncode == 0


# ---------------------------------------------------------------- hashed-scan helpers (code-identical copies) ---
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
                  "_rendering_hashes": QUALIFY_PATH, "_tokens": QUALIFY_PATH, "value_patterns": COMPARE_PATH}
CONST_SOURCES = {"DEC": QUALIFY_PATH, "INTSCI": QUALIFY_PATH, "RAT": QUALIFY_PATH, "SCALES": QUALIFY_PATH,
                 "DECOYS": QUALIFY_PATH}


def _strip(node):
    node = ast.parse(ast.unparse(node)).body[0]
    if isinstance(node, ast.FunctionDef) and node.body and isinstance(node.body[0], ast.Expr) \
            and isinstance(getattr(node.body[0], "value", None), ast.Constant) \
            and isinstance(node.body[0].value.value, str):
        node.body = node.body[1:]
    return ast.dump(node, include_attributes=False)


def _defs(src: str) -> dict:
    out = {}
    for n in ast.parse(src).body:
        if isinstance(n, ast.FunctionDef):
            out[n.name] = n
        elif isinstance(n, ast.Assign) and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name):
            out[n.targets[0].id] = n
    return out


def helper_identity() -> dict:
    mine = _defs(pathlib.Path(__file__).read_text())
    src = {p: _defs(git("show", f"HEAD:{p}")) for p in {QUALIFY_PATH, COMPARE_PATH}}
    diff = [name for name, p in {**HELPER_SOURCES, **CONST_SOURCES}.items()
            if name not in src[p] or _strip(mine[name]) != _strip(src[p][name])]
    return {"compared": sorted({**HELPER_SOURCES, **CONST_SOURCES}), "different": diff}


def _scan(texts: dict, hashes: frozenset) -> dict:
    hits, memo = {}, {}
    for name, txt in texts.items():
        for t in _tokens(txt):
            if t not in memo:
                memo[t] = bool(_rendering_hashes(t) & hashes)
            if memo[t]:
                hits[name] = hits.get(name, 0) + 1
    return hits


def _original_hashes() -> frozenset:
    for node in ast.parse(git("show", f"HEAD:{VALIDATE_PATH}")).body:
        if isinstance(node, ast.Assign) and any(getattr(t, "id", None) == "ORIGINAL_PATTERN_SHA256"
                                                for t in node.targets):
            return frozenset(e.value for e in node.value.args[0].elts)
    raise RuntimeError("ORIGINAL_PATTERN_SHA256 literal not found")


def _independent_hashes() -> frozenset:
    runs = json.loads(git("show", f"HEAD:{RUNS_PATH}"))
    return frozenset(hashlib.sha256(x.encode()).hexdigest() for k in ("D1", "D2")
                     for x in value_patterns(format(float(F(runs["targets"][k]["value"])), ".12f")))


# ---------------------------------------------------------------- overclaim wording scan (repaired W01) --------
# Positive assertions that publication text may not make. A match is ALLOWED only when a negation cue precedes it
# inside the same clause (clauses are split at sentence punctuation and at coordinating conjunctions), so that
# "not evidence against H3a" or "not a statement that 309 is unclosable" pass while
# "K5 is not closed, and H3a is established" fails. Scoped refutation of 309 passes only with "within ... scope".
BANNED_ASSERTIONS = {
    "final map": r"\b(final|mathematically final) (authoritative )?coverage map\b|\bmathematically final\b",
    "exhaustion": r"\ball (routes|research directions|future routes|methods) (are|have been) exhausted\b"
                  r"|\bno (further |future )?route exists\b|\bno route (can|could) (ever )?close\b",
    "impossibility": r"\b(is|are) (mathematically )?(impossible to close|unclosable)\b|\bcan(not| never) be closed\b"
                     r"|\bis mathematically impossible\b",
    "h3a refuted": r"\bh3a is (false|refuted|disproved)\b|\b(refutes|disproves|falsifies) h3a\b"
                   r"|\bevidence against h3a\b",
    "h3a established": r"\bh3a (is|has been) (proved|established|certified|confirmed)\b|\bh3a holds\b",
    "306 failed": r"\b(cell )?306 failed\b",
    "k5 closed": r"\bk5 (is|has been) closed\b|\bcusum k5 is closed\b",
    "sr k5 complete": r"\bsr k5 (is |has been )?(complete|completed|closed|done)\b",
    "p5y closed": r"\bp5y (is|has been) closed\b",
    "309 unscoped refutation": r"\b309 is (mathematically )?refuted\b(?!\s+(only\s+)?within)",
}
NEGATION_CUES = r"\b(not|no|never|neither|nor|nothing|none|without|cannot|isn't|aren't|doesn't|don't)\b"
CLAUSE_SPLIT = r"[.;:!?\n]|,\s*(?:and|but|while|whereas|so)\b|\s(?:and|but|while|whereas)\s"

WORDING_FIXTURES = {
    "prohibited": ["H3a is established for CUSUM m = 5.", "Cell 309 is unclosable.",
                   "All routes are exhausted.", "This is the final coverage map.", "306 failed.",
                   "K5 is not closed, and H3a is established.", "The open cells are evidence against H3a.",
                   "Cell 309 is refuted.", "SR K5 is complete.", "P5Y is closed.", "CUSUM K5 is closed.",
                   "H3a holds for every m."],
    "negated": ["Unresolved cells are not evidence against H3a.",
                "This is not a statement that 309 is unclosable.",
                "r5 is not a mathematically final map.", "No claim is made that H3a is established.",
                "It does not mean that all routes are exhausted.", "Nothing here says that SR K5 is complete."],
    "scoped": ["Cell 309 is refuted within the stated scope only.",
               "309 is refuted only within the atom-constant family at the frozen inputs.",
               "No route that closes 307 has been certified.", "K5 remains OPEN; P5Y is NOT_YET_CLOSED.",
               "K5_INCONCLUSIVE is a certification/adoption conclusion under the current framework."],
}


def wording_findings(text: str) -> list:
    """Banned positive assertions, clause by clause; a match preceded by a negation cue in its clause is allowed."""
    found = []
    for clause in re.split(CLAUSE_SPLIT, text.lower()):
        for label, pat in BANNED_ASSERTIONS.items():
            for m in re.finditer(pat, clause):
                if not re.search(NEGATION_CUES, clause[:m.start()]):
                    found.append((label, clause.strip()[:120]))
    return found


def wording_selftest() -> dict:
    res = {"prohibited_caught": [], "prohibited_missed": [], "allowed_false_positive": []}
    for s in WORDING_FIXTURES["prohibited"]:
        (res["prohibited_caught"] if wording_findings(s) else res["prohibited_missed"]).append(s)
    for s in WORDING_FIXTURES["negated"] + WORDING_FIXTURES["scoped"]:
        if wording_findings(s):
            res["allowed_false_positive"].append(s)
    res["pass"] = not res["prohibited_missed"] and not res["allowed_false_positive"]
    return res


# ---------------------------------------------------------------- repository checks ------------------------------
def changed_since_base() -> list:
    tracked = git("diff", "--name-only", BASE, "--").splitlines()
    status = [l[3:] for l in git("status", "--porcelain", "--ignored", "--untracked-files=all").splitlines()]
    return sorted(set(tracked + status))


def allowed_paths(phase: str) -> set:
    idx = PHASE_ORDER.index(phase)
    ns = [f"{NS_REL}/{p}" for p in NS_FREEZE_FILES]
    ns += [f"{NS_REL}/{p}" for p, ph in NS_LATER_FILES.items() if PHASE_ORDER.index(ph) <= idx]
    if phase == "publication":
        ns += PUBLIC_ADDITIVE_FILES
    return set(ns)


def _hunks(path: str) -> list:
    return [tuple(int(x) if x else 1 for x in m.groups()) for m in
            re.finditer(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@", git("diff", "-U0", BASE, "--", path), re.M)]


def placement_check() -> dict:
    out = {}
    base_readme = git("show", f"{BASE}:README.md").splitlines()
    new_readme = (REPO / "README.md").read_text().splitlines()
    h = _hunks("README.md")
    if h:
        try:
            ps1 = next(i for i, l in enumerate(new_readme, 1) if l.startswith("## Current successor status (PS1)"))
            lim = next(i for i, l in enumerate(new_readme, 1) if l.startswith("## Limitations and negative results"))
            out["README.md"] = len(h) == 1 and h[0][1] == 0 and ps1 < h[0][2] and h[0][2] + h[0][3] - 1 < lim
        except StopIteration:
            out["README.md"] = False
    for f in PUBLIC_ADDITIVE_FILES[1:]:
        h = _hunks(f)
        if h:
            n_base = len(git("show", f"{BASE}:{f}").splitlines())
            out[f] = len(h) == 1 and h[0][1] == 0 and h[0][0] == n_base
    return out


def closeout_texts(extra_commit_msgs: bool = True) -> dict:
    texts = {}
    for p in sorted((REPO / NS_REL).rglob("*")):
        if p.is_file() and "__pycache__" not in p.parts:
            texts[str(p.relative_to(REPO))] = p.read_text(errors="replace")
    for f in PUBLIC_ADDITIVE_FILES:
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
    add("S02 base (predecessor freeze review 591b4394) is ancestor of HEAD",
        git_ok("merge-base", "--is-ancestor", BASE, "HEAD"), BASE)
    add("S03 local chain (route audit r0..r1, rejected freeze 08e9acd1, its review 591b4394) in HEAD",
        all(git_ok("merge-base", "--is-ancestor", c, "HEAD") for c in LOCAL_CHAIN), LOCAL_CHAIN)
    add("S04 local main unchanged", git("rev-parse", "refs/heads/main").strip() == LOCAL_MAIN, LOCAL_MAIN)
    add("S05 remote main unchanged", git("rev-parse", "refs/remotes/origin/main").strip() == REMOTE_MAIN, REMOTE_MAIN)
    remote = [r for r in git("for-each-ref", "--format=%(refname)", "refs/remotes").splitlines()
              if r.endswith("/p5y-k5-tail-c11rd-d1d2-extension")]
    add("S06 no remote copy of the branch", not remote, remote)
    add("S07 no upstream configured",
        not git_ok("config", "--get", "branch.p5y-k5-tail-c11rd-d1d2-extension.remote"), "unset")

    add("C01 r5 blob unchanged", git("rev-parse", f"HEAD:{R5_PATH}").strip() == R5_BLOB, R5_BLOB)
    r5 = json.loads(git("show", f"HEAD:{R5_PATH}"))
    add("C02 r5: m=5 open [[306,309]], m=1,2,3 open [], union [[306,309]], K5_COVERAGE_COMPLETE false",
        r5["per_m"]["5"]["open_ranges"] == [[306, 309]]
        and all(r5["per_m"][m]["open_ranges"] == [] for m in ("1", "2", "3"))
        and r5["union_open_ranges"] == [[306, 309]] and r5["K5_COVERAGE_COMPLETE"] is False, "structure only")
    r6t = [p for p in git("ls-files").splitlines() if re.search(r"coverage_map_r6", p, re.I)]
    r6d = [str(p.relative_to(REPO)) for p in REPO.rglob("*")
           if re.search(r"coverage_map_r6", p.name, re.I) and ".git" not in p.parts]
    add("C03 no r6 anywhere in this worktree (tracked or on disk)", not r6t and not r6d, r6t + r6d)

    refs = dict(l.split(" ", 1)[::-1] for l in git("for-each-ref", "--format=%(objectname) %(refname)").splitlines())
    gov = {k: v for k, v in refs.items() if k.startswith(("refs/c11rd/", "refs/c12r2/", "refs/c12r1/", "refs/c12/"))}
    add("G01 governance refs exactly as pinned", gov == GOVERNANCE_REFS, sorted(gov))
    add("G02 forensic objects present with expected types",
        all(git("cat-file", "-t", o).strip() == t for o, t in FORENSIC_OBJECTS.items()), FORENSIC_OBJECTS)

    hist_changed = git("diff", "--name-only", BASE, "HEAD", "--", *HISTORICAL_PATHS).splitlines()
    hist_dirty = git("status", "--porcelain", "--ignored", "--", *HISTORICAL_PATHS).splitlines()
    add("H01 historical namespaces (incl. the rejected predecessor closeout) byte-identical to base",
        not hist_changed and not hist_dirty, hist_changed + hist_dirty)
    missing = [(p, t) for p, t in VERDICT_PINS if t not in git("show", f"HEAD:{p}")]
    add("H02 historical verdict tokens present", not missing, {"pins": len(VERDICT_PINS), "missing": missing})
    add("H03 K5_STATUS and readiness audit unchanged; K5_STATUS records SR K5 NOT STARTED with both prerequisites",
        git("rev-parse", f"HEAD:{K5_STATUS_PATH}").strip() == K5_STATUS_BLOB
        and git("rev-parse", f"HEAD:{READINESS_PATH}").strip() == READINESS_BLOB
        and SR_K5_TEXT in git("show", f"HEAD:{K5_STATUS_PATH}"), [K5_STATUS_BLOB, READINESS_BLOB])

    changed = changed_since_base()
    allowed = allowed_paths(phase)
    add("P01 exact allowlist: every path changed since base (tracked, untracked, ignored) is allowed in this phase",
        not [p for p in changed if p not in allowed], {"unexpected": [p for p in changed if p not in allowed],
                                                       "changed": changed})
    dels = {}
    for f in PUBLIC_ADDITIVE_FILES:
        for line in git("diff", "--numstat", BASE, "--", f).splitlines():
            a, d, _ = line.split("\t", 2)
            if d != "0":
                dels[f] = d
    add("P02 public publication edits are additive only (0 deleted or modified lines)", not dels, dels)
    pl = placement_check()
    add("P03 public publication edits are single additive blocks at the frozen positions", all(pl.values()), pl)
    add("P04 no __pycache__ or .pyc in the successor namespace",
        not [p for p in (REPO / NS_REL).rglob("*") if "__pycache__" in p.parts or p.suffix == ".pyc"], NS_REL)

    fmt = {}
    for rel, vocab in VERDICT_FILES.items():
        p = REPO / rel
        if p.is_file():
            lines = p.read_text().splitlines()
            fmt[rel] = len(lines) > 1 and lines[1] in vocab
    add("F01 verdict-line format of successor review/adjudication documents present so far", all(fmt.values()), fmt)

    cited, missing_c = set(), []
    pat = re.compile(r"`((?:level4|docs|p5y_[a-z0-9_]+)/[^`\s:]+?)(?::\d+(?:[-–]\d+)?)?`")
    future = {f"{NS_REL}/{p}" for p, ph in NS_LATER_FILES.items()
              if PHASE_ORDER.index(ph) > PHASE_ORDER.index(phase) or p.startswith("evidence/")}
    for rel, txt in closeout_texts(extra_commit_msgs=False).items():
        if rel.endswith(".md") or rel.endswith("(added lines)"):
            cited.update(pat.findall(txt))
    for c in sorted(cited):
        if any(ch in c for ch in "{}*<>…") or c in future:
            continue
        if any((REPO / x).exists() for x in (c, f"{CP}/{c}")):
            continue
        ref = XREF_ARTIFACTS.get(c)
        if ref and git_ok("cat-file", "-e", f"{git('rev-parse', ref).strip()}:{c}"):
            continue
        missing_c.append(c)
    add("R01 every backticked repository path cited in successor documents exists (in this worktree, or for the "
        "declared cross-ref artifacts at their ref's current tip; declared later artifacts exempt until their phase)",
        not missing_c, {"cited": len(cited), "missing": missing_c})

    st = wording_selftest()
    add("T01 wording-scan regression fixtures: all prohibited caught, no negated/scoped false positive", st["pass"], st)
    pub = {k: v for k, v in closeout_texts(extra_commit_msgs=False).items()
           if k.startswith(f"{NS_REL}/publication/") or k == f"{NS_REL}/README.md" or k.endswith("(added lines)")}
    wf = {k: wording_findings(v) for k, v in pub.items()}
    wf = {k: v for k, v in wf.items() if v}
    add("W01 publication-facing text (publication/, namespace README, added public lines) makes no banned assertion",
        not wf, {"files": sorted(pub), "findings": wf})

    orig, ind = _original_hashes(), _independent_hashes()
    texts = closeout_texts()
    dh = frozenset(hashlib.sha256(x.encode()).hexdigest() for d in DECOYS for x in value_patterns(d))
    pos = _scan({"planted": f"a bound of {DECOYS[0][:7]} and {DECOYS[1][:9]}"}, dh)
    neg = _scan({"clean": "values 1.23456 and 7/9 and 2.5e3"}, dh)
    oh, ih = _scan(texts, orig), _scan(texts, ind)
    add("L01 value-free leak scan: 0 original and 0 independent D1/D2 renderings; decoy controls behave",
        len(orig) == 17 and not oh and not ih and pos and not neg,
        {"files_scanned": len(texts), "original_hits": len(oh), "independent_hits": len(ih),
         "decoy_positive_fired": bool(pos), "decoy_negative_quiet": not neg, "hit_files": sorted(set(oh) | set(ih))})
    add("L02 hash-set and helper sources at pinned blobs",
        [git("rev-parse", f"HEAD:{p}").strip() for p in (VALIDATE_PATH, RUNS_PATH, QUALIFY_PATH, COMPARE_PATH)]
        == [VALIDATE_BLOB, RUNS_BLOB, QUALIFY_BLOB, COMPARE_BLOB], "4 blobs")
    hi = helper_identity()
    add("L03 scan helpers are code-identical (AST, docstrings ignored) to their cited sources", not hi["different"], hi)

    if phase == "publication":
        r = subprocess.run([sys.executable, "-I", "-S", "-B", "docs/research_synthesis/verify_synthesis.py",
                            "--no-diff-check"], cwd=REPO, capture_output=True, text=True,
                           stdin=subprocess.DEVNULL, timeout=600)
        add("V01 research-synthesis document verifier (--no-diff-check) passes",
            r.returncode == 0 and "SYNTHESIS VERIFICATION OK" in r.stdout, (r.stdout or r.stderr).strip()[:200])

    return {"schema": "rebaseguard.p5y.k5.partial-closeout-r1.admin-checks.v1", "phase": phase, "head": head,
            "base": BASE, "scientific_computation": "NONE (administrative checks only)", "checks": out,
            "pass": all(c["pass"] for c in out), "summary": f"{sum(c['pass'] for c in out)}/{len(out)}"}


# ---------------------------------------------------------------- cross-ref snapshot (protocol R1 §4) -----------
def _json_at(ref: str, path: str):
    tip = git("rev-parse", "--verify", "-q", ref, check=False).strip()
    if not tip:
        return None, None
    txt = git("show", f"{tip}:{path}", check=False)
    return tip, (json.loads(txt) if txt.strip() else None)


def _pickaxe(regex: str) -> list:
    out, cur = [], None
    for line in git("log", "--all", "-G", regex, "--format=@@%H", "--name-only").splitlines():
        if line.startswith("@@"):
            cur = {"commit": line[2:], "files": []}
            out.append(cur)
        elif line.strip() and cur is not None:
            cur["files"].append(line.strip())
    return out


def xref_snapshot() -> dict:
    now = datetime.datetime.now(datetime.timezone.utc).astimezone().isoformat(timespec="seconds")
    binding, informational = [], []

    tip, k1 = _json_at(K1_REF, K1_FILE)
    k1s = (k1 or {}).get("scientific_verdict", {})
    got = {k: k1s.get(k) for k in K1_EXPECTED}
    binding.append({"id": "XB1 K1 state", "ref": K1_REF, "tip": tip, "artifact": K1_FILE, "observed": got,
                    "expected": K1_EXPECTED, "compatible": got == K1_EXPECTED})

    tip, kk = _json_at(K2K3_REF, K2K3_FILE)
    cs = (kk or {}).get("independent_countersignature", {})
    got = {"K2": cs.get("K2"), "K3": cs.get("K3")}
    binding.append({"id": "XB2 K2/K3 countersignature", "ref": K2K3_REF, "tip": tip, "artifact": K2K3_FILE,
                    "observed": got, "expected": {"K2": "PASS", "K3": "PASS"},
                    "compatible": got == {"K2": "PASS", "K3": "PASS"}})

    tip, k4 = _json_at(K4_REF, K4_FILE)
    got = {k: (k4 or {}).get(k) for k in K4_EXPECTED}
    binding.append({"id": "XB3 K4 state", "ref": K4_REF, "tip": tip, "artifact": K4_FILE, "observed": got,
                    "expected": K4_EXPECTED, "compatible": got == K4_EXPECTED})
    p5y = (k4 or {}).get("P5Y_STATE")
    binding.append({"id": "XB4 recorded P5Y_STATE (K1..K5, P5Y)", "ref": K4_REF, "tip": tip, "artifact": K4_FILE,
                    "observed": p5y, "expected": P5Y_EXPECTED, "compatible": p5y == P5Y_EXPECTED})

    sr = _pickaxe(SR_K5_REGEX)
    unexpected = [c for c in sr if c["commit"] not in SR_K5_ALLOWED_COMMITS
                  and not all(f.startswith(SR_K5_ALLOWED_PREFIXES) for f in c["files"])]
    tips = git("for-each-ref", "--format=%(objectname) %(refname)", "refs/heads", "refs/remotes", "refs/tags").splitlines()
    status_versions = {K5_STATUS_PATH: set(), READINESS_PATH: set()}
    for line in tips:
        obj = line.split(" ", 1)[0]
        for path in status_versions:
            b = git("rev-parse", "-q", "--verify", f"{obj}:{path}", check=False).strip()
            if b:
                status_versions[path].add(b)
    versions_ok = status_versions[K5_STATUS_PATH] <= {K5_STATUS_BLOB} and status_versions[READINESS_PATH] <= {READINESS_BLOB}
    binding.append({"id": "XB5 SR K5 NOT STARTED on every ref (SR-K5 status text and status-file versions unchanged)",
                    "method": f"git log --all -G '{SR_K5_REGEX}' --name-only; per-tip blob of status files",
                    "observed": {"commits": [c["commit"][:8] for c in sr], "unexpected":
                                 [(c["commit"][:8], c["files"]) for c in unexpected],
                                 "status_file_versions": {k: sorted(v) for k, v in status_versions.items()}},
                    "expected": "only a3547b9b, e8680998 and route-audit/closeout-namespace commits; one version each",
                    "compatible": not unexpected and versions_ok})

    k5c = _pickaxe(K5_CLOSED_REGEX)
    k5c_bad = [c for c in k5c if not all(f.startswith(SR_K5_ALLOWED_PREFIXES) for f in c["files"])]
    r6 = [l for l in git("log", "--all", "--format=%H", "--name-only", "--diff-filter=A", "--",
                         "*COVERAGE_MAP_R6*", "*coverage_map_r6*").splitlines() if "/" in l]
    p5c = _pickaxe(P5Y_CLOSED_REGEX)
    p5c_bad = [c for c in p5c if not all(f.startswith(SR_K5_ALLOWED_PREFIXES) for f in c["files"])]
    binding.append({"id": "XB6 no ref records K5 closed, a K5 coverage map r6, or P5Y closed",
                    "observed": {"k5_closed_commits": [(c["commit"][:8], c["files"][:3]) for c in k5c_bad],
                                 "r6_paths": r6, "p5y_closed_commits": [(c["commit"][:8], c["files"][:3]) for c in p5c_bad]},
                    "expected": "none", "compatible": not k5c_bad and not r6 and not p5c_bad})

    for r in INFORMATIONAL_REFS:
        informational.append({"ref": r, "tip": git("rev-parse", "--verify", "-q", r, check=False).strip() or None,
                              "tip_date": git("log", "-1", "--format=%cI", r, check=False).strip() or None,
                              "subject": git("log", "-1", "--format=%s", r, check=False).strip()[:120] or None})
    n_refs = len(tips)
    return {"schema": "rebaseguard.p5y.k5.partial-closeout-r1.xref.v1", "observed_at": now,
            "head": git("rev-parse", "HEAD").strip(), "refs_scanned": n_refs,
            "binding": binding, "informational": informational,
            "drift_rule": "binding facts are compared by STATE (the expected tokens at the ref's current tip), not by "
                          "tip id: a moved tip whose artifact yields identical tokens is COMPATIBLE_DRIFT (recorded); "
                          "any token change, missing ref or missing/unparseable artifact is INCOMPATIBLE -> STOP",
            "pass": all(b["compatible"] for b in binding)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase", choices=PHASE_ORDER)
    ap.add_argument("--xref", action="store_true")
    ap.add_argument("--out")
    a = ap.parse_args()
    if not (sys.flags.isolated and sys.flags.no_site and sys.flags.dont_write_bytecode):
        print("refused: run with python3 -I -S -B", file=sys.stderr)
        return 2
    res = xref_snapshot() if a.xref else run_checks(a.phase or "prefreeze")
    txt = json.dumps(res, indent=1, sort_keys=True, default=list) + "\n"
    if a.out:
        pathlib.Path(a.out).write_text(txt)
    print(txt if not a.out else f"{res.get('summary', '')} pass={res['pass']} -> {a.out}")
    return 0 if res["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
