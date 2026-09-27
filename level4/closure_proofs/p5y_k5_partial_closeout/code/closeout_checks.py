"""Administrative / mechanical checks for the K5 PARTIAL closeout (CUSUM m = 5).

This module performs NO scientific computation. It never evaluates Gamma, never reads a TCT input, registry
constant or certificate value into any calculation, and imports no module of any campaign. It uses only the
standard library and `git`:

* repository state, refs, ancestry and blob identity;
* byte-identity of historical namespaces against the pre-closeout base;
* presence of pinned historical verdict tokens;
* additive-only rule for the three permitted publication edits;
* existence of cited repository paths;
* review/adjudication verdict-line format;
* a value-free hashed leak scan (original and independent D1/D2 renderings, never printed).

The hashed-scan helpers (`_exp10`, `_digits`, `_dec_str`, `_rendering_hashes`, `_tokens` and the three regexes)
are copied verbatim from `p5y_k5_tail_c11rd_d1d2_extension/qualification_r1q_r1/code/c11rd_qualify.py`
(blob 9a55edf196887b62f0e249578a682116b52c364b), and `value_patterns` from `.../code/c11rd_compare.py`
(blob e536605b0ff9e411483a819433ffb9d34fc6e652). They are string/number rendering utilities. The original
hash set is read from `.../code/c11rd_validate.py` (blob 22293e05417132b4b0e1693126df343e14418a26) by AST
literal parsing, without importing or executing that module.

Usage:  python3 -I -S -B closeout_checks.py --phase {prefreeze,freeze,adjudication,publication} [--out FILE]
        python3 -I -S -B closeout_checks.py --sr-refs [--out FILE]      (slow: pickaxe over all refs)
"""

from __future__ import annotations

import argparse
import ast
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
NS_REL = "level4/closure_proofs/p5y_k5_partial_closeout"
CP = "level4/closure_proofs"

BASE = "2f36352e9401c135cca5d614d0d6f22620ebc0eb"          # route-audit r1 review commit = pre-closeout HEAD
START_HEAD = BASE
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
ROUTE_AUDIT_CHAIN = ["d52cec02", "1667ea88", "27e259f4", "802be11e", "4a4b1392", "2f36352e"]
K5_STATUS_PATH = f"{CP}/p5y_k5_remaining_cell_closure/K5_STATUS.md"
K5_STATUS_BLOB = "d212f0d52126cd4c7d062fc11c335484482903b0"
SR_K5_TEXT = "| SR K5 | NOT STARTED"

# Historical records that the closeout must leave byte-identical (vs BASE).
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
    f"{CP}/p5y_k5_tail_route_audit",
]

# (path, token that must appear in the file at HEAD) -- historical verdicts, never rewritten.
VERDICT_PINS = [
    (f"{CP}/p5y_k5_tail_operator_registry/README.md", "MARGINAL"),
    (f"{CP}/p5y_k5_m5_tail_closure/README.md", "STOPPED"),
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
]

# Publication files the frozen protocol permits to change, additively only, and only in phase "publication".
ADDITIVE_PUBLICATION_FILES = ["README.md", "docs/research_synthesis/README.md",
                              "docs/research_synthesis/LIMITATIONS_AND_OPEN_ITEMS.md"]

# Verdict-line (line 2) vocabulary for the closeout's own review/adjudication documents.
VERDICT_FILES = {
    f"{NS_REL}/review/CLOSEOUT_FREEZE_REVIEW.md": {"CLOSEOUT_FREEZE_ACCEPTED", "CLOSEOUT_FREEZE_REJECTED"},
    f"{NS_REL}/adjudication/K5_CUSUM_FINAL_ADJUDICATION.md": {"K5_CLOSED", "K5_FAIL_MATHEMATICAL",
                                                               "K5_INCONCLUSIVE"},
    f"{NS_REL}/review/K5_ADJUDICATION_REVIEW.md": {"K5_ADJUDICATION_ACCEPTED", "K5_ADJUDICATION_REJECTED"},
}

# Closeout artifacts that are declared by the protocol but created only in a later phase (citable before they exist;
# the publication file must exist in phase "publication").
FUTURE_ARTIFACTS = ("review/CLOSEOUT_FREEZE_REVIEW.md", "adjudication/K5_CUSUM_FINAL_ADJUDICATION.md",
                    "review/K5_ADJUDICATION_REVIEW.md", "publication/K5_CUSUM_CLOSEOUT_STATUS.md",
                    "evidence/PUBLICATION_CHECKS.json")

# Overclaim phrases that publication text may not contain (current-vs-final language, protocol §11).
BANNED_PUBLICATION_PHRASES = (
    "final coverage map", "mathematically final", "all routes exhausted", "all routes are exhausted",
    "is mathematically impossible", "cannot be closed", "can never be closed", "is unclosable",
    "h3a is false", "h3a is refuted", "refutes h3a", "h3a is proved", "h3a is established", "h3a holds for",
    "306 failed", "no route exists", "k5 is closed",
)

C11RD = f"{CP}/p5y_k5_tail_c11rd_d1d2_extension"
VALIDATE_PATH, VALIDATE_BLOB = f"{C11RD}/code/c11rd_validate.py", "22293e05417132b4b0e1693126df343e14418a26"
RUNS_PATH, RUNS_BLOB = f"{C11RD}/evidence/runs/C11RD_RUNS.json", "30e2dfd0ac87aad74f8a9490fee99623cbdf151d"

GIT_ENV = {"PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin", "HOME": "/var/empty",
           "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": "/dev/null", "LC_ALL": "C"}


def git(*args, check=True) -> str:
    r = subprocess.run(["git", *args], cwd=REPO, env=GIT_ENV, capture_output=True, text=True,
                       stdin=subprocess.DEVNULL, timeout=900)
    if check and r.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: {r.stderr.strip()[:300]}")
    return r.stdout


def git_ok(*args) -> bool:
    return subprocess.run(["git", *args], cwd=REPO, env=GIT_ENV, capture_output=True,
                          stdin=subprocess.DEVNULL, timeout=900).returncode == 0


# ---------------------------------------------------------------- hashed-scan helpers (verbatim copies) --------
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
    src = git("show", f"HEAD:{VALIDATE_PATH}")
    for node in ast.parse(src).body:
        if isinstance(node, ast.Assign) and any(getattr(t, "id", None) == "ORIGINAL_PATTERN_SHA256"
                                                for t in node.targets):
            return frozenset(e.value for e in node.value.args[0].elts)
    raise RuntimeError("ORIGINAL_PATTERN_SHA256 literal not found")


def _independent_hashes() -> frozenset:
    runs = json.loads(git("show", f"HEAD:{RUNS_PATH}"))
    return frozenset(hashlib.sha256(x.encode()).hexdigest() for k in ("D1", "D2")
                     for x in value_patterns(format(float(F(runs["targets"][k]["value"])), ".12f")))


# ---------------------------------------------------------------- checks ---------------------------------------
def changed_since_base() -> list:
    tracked = git("diff", "--name-only", BASE, "--").splitlines()
    untracked = git("ls-files", "--others", "--exclude-standard").splitlines()
    return sorted(set(tracked + untracked))


def closeout_texts(extra_commit_msgs: bool = True) -> dict:
    texts = {}
    for p in sorted((REPO / NS_REL).rglob("*")):
        if p.is_file() and "__pycache__" not in p.parts:
            texts[str(p.relative_to(REPO))] = p.read_text(errors="replace")
    for f in ADDITIVE_PUBLICATION_FILES:
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
    add("S02 base is ancestor of HEAD", git_ok("merge-base", "--is-ancestor", BASE, "HEAD"), BASE)
    add("S03 route-audit chain ancestors of HEAD",
        all(git_ok("merge-base", "--is-ancestor", c, "HEAD") for c in ROUTE_AUDIT_CHAIN), ROUTE_AUDIT_CHAIN)
    add("S04 local main unchanged", git("rev-parse", "refs/heads/main").strip() == LOCAL_MAIN, LOCAL_MAIN)
    add("S05 remote main unchanged", git("rev-parse", "refs/remotes/origin/main").strip() == REMOTE_MAIN, REMOTE_MAIN)
    remote_copies = [r for r in git("for-each-ref", "--format=%(refname)", "refs/remotes").splitlines()
                     if r.endswith("/p5y-k5-tail-c11rd-d1d2-extension")]
    add("S06 no remote copy of the branch", not remote_copies, remote_copies)
    add("S07 no upstream configured",
        not git_ok("config", "--get", "branch.p5y-k5-tail-c11rd-d1d2-extension.remote"), "branch.*.remote unset")

    add("C01 r5 blob unchanged", git("rev-parse", f"HEAD:{R5_PATH}").strip() == R5_BLOB, R5_BLOB)
    r5 = json.loads(git("show", f"HEAD:{R5_PATH}"))
    add("C02 r5 m=5 open [[306,309]], m=1,2,3 open [], union [[306,309]], coverage incomplete",
        r5["per_m"]["5"]["open_ranges"] == [[306, 309]] and all(r5["per_m"][m]["open_ranges"] == []
                                                                 for m in ("1", "2", "3"))
        and r5["union_open_ranges"] == [[306, 309]] and r5["K5_COVERAGE_COMPLETE"] is False, "structure fields only")
    r6_tracked = [p for p in git("ls-files").splitlines() if re.search(r"coverage_map_r6", p, re.I)]
    r6_disk = [str(p.relative_to(REPO)) for p in REPO.rglob("*") if re.search(r"coverage_map_r6", p.name, re.I)
               and ".git" not in p.parts]
    add("C03 no r6 anywhere (tracked or on disk)", not r6_tracked and not r6_disk, r6_tracked + r6_disk)

    refs = dict(l.split(" ", 1)[::-1] for l in git("for-each-ref", "--format=%(objectname) %(refname)").splitlines())
    gov_now = {k: v for k, v in refs.items() if k.startswith(("refs/c11rd/", "refs/c12r2/", "refs/c12r1/",
                                                              "refs/c12/"))}
    add("G01 governance refs exactly as pinned", gov_now == GOVERNANCE_REFS, sorted(gov_now))
    add("G02 forensic objects present with expected types",
        all(git("cat-file", "-t", o).strip() == t for o, t in FORENSIC_OBJECTS.items()), FORENSIC_OBJECTS)
    other = sorted(k for k in refs if not k.startswith(("refs/heads/", "refs/remotes/", "refs/tags/", "refs/c11rd/",
                                                        "refs/c12r2/")))
    add("G03 other non-branch refs (observation only)", True, {"count": len(other),
                                                               "prefixes": sorted({"/".join(k.split("/")[:2]) for k in other})})

    hist_changed = git("diff", "--name-only", BASE, "HEAD", "--", *HISTORICAL_PATHS).splitlines()
    hist_dirty = git("status", "--porcelain", "--", *HISTORICAL_PATHS).splitlines()
    add("H01 historical namespaces byte-identical to base (committed and working tree)",
        not hist_changed and not hist_dirty, hist_changed + hist_dirty)
    missing_pins = [(p, t) for p, t in VERDICT_PINS if t not in git("show", f"HEAD:{p}")]
    add("H02 historical verdict tokens present", not missing_pins, {"pins": len(VERDICT_PINS), "missing": missing_pins})
    add("H03 K5_STATUS unchanged and still records SR K5 NOT STARTED",
        git("rev-parse", f"HEAD:{K5_STATUS_PATH}").strip() == K5_STATUS_BLOB
        and SR_K5_TEXT in git("show", f"HEAD:{K5_STATUS_PATH}"), K5_STATUS_PATH)

    changed = changed_since_base()
    allowed = [NS_REL + "/"] + (ADDITIVE_PUBLICATION_FILES if phase == "publication" else [])
    outside = [p for p in changed if not any(p == a or p.startswith(a) for a in allowed)]
    add("P01 changes since base confined to the closeout namespace (+ permitted publication files in phase "
        "publication)", not outside, outside)
    dels = {}
    for f in ADDITIVE_PUBLICATION_FILES:
        for line in git("diff", "--numstat", BASE, "--", f).splitlines():
            a, d, _ = line.split("\t", 2)
            if d != "0":
                dels[f] = d
    add("P02 publication edits are additive only (0 deleted lines)", not dels, dels)
    add("P03 no __pycache__ or .pyc in the closeout namespace",
        not [p for p in (REPO / NS_REL).rglob("*") if "__pycache__" in p.parts or p.suffix == ".pyc"], NS_REL)

    fmt = {}
    for rel, vocab in VERDICT_FILES.items():
        p = REPO / rel
        if p.is_file():
            lines = p.read_text().splitlines()
            fmt[rel] = len(lines) > 1 and lines[1].strip() in vocab and lines[1] == lines[1].strip()
    add("F01 verdict-line format of closeout review/adjudication documents present so far",
        all(fmt.values()), fmt)

    cited, missing = set(), []
    pat = re.compile(r"`((?:level4|docs|p5y_[a-z0-9_]+)/[^`\s:]+?)(?::\d+(?:[-–]\d+)?)?`")
    for rel, txt in closeout_texts(extra_commit_msgs=False).items():
        if rel.endswith("(added lines)") or rel.endswith(".md"):
            for m in pat.findall(txt):
                cited.add(m)
    future = {f"{NS_REL}/{x}" for x in FUTURE_ARTIFACTS if not (phase == "publication" and x.startswith("publication/"))}
    for c in sorted(cited):
        if any(ch in c for ch in "{}*<>…") or c in future:
            continue
        cands = [c, f"{CP}/{c}"]
        if not any((REPO / x).exists() for x in cands):
            missing.append(c)
    add("R01 every backticked repository path cited in closeout documents exists", not missing,
        {"cited": len(cited), "missing": missing})

    orig, ind = _original_hashes(), _independent_hashes()
    texts = closeout_texts()
    dh = frozenset(hashlib.sha256(x.encode()).hexdigest() for d in DECOYS for x in value_patterns(d))
    pos = _scan({"planted": f"a bound of {DECOYS[0][:7]} and {DECOYS[1][:9]}"}, dh)
    neg = _scan({"clean": "values 1.23456 and 7/9 and 2.5e3"}, dh)
    o_hits, i_hits = _scan(texts, orig), _scan(texts, ind)
    add("L01 value-free leak scan: 0 original and 0 independent D1/D2 renderings; decoy controls fire correctly",
        len(orig) == 17 and not o_hits and not i_hits and pos and not neg,
        {"files_scanned": len(texts), "original_hits": len(o_hits), "independent_hits": len(i_hits),
         "original_set_size": len(orig), "decoy_positive_fired": bool(pos), "decoy_negative_quiet": not neg,
         "hit_files": sorted(set(o_hits) | set(i_hits))})
    add("L02 hash-set sources at pinned blobs",
        git("rev-parse", f"HEAD:{VALIDATE_PATH}").strip() == VALIDATE_BLOB
        and git("rev-parse", f"HEAD:{RUNS_PATH}").strip() == RUNS_BLOB, [VALIDATE_BLOB, RUNS_BLOB])

    if phase == "publication":
        pub = {k: v for k, v in closeout_texts(extra_commit_msgs=False).items()
               if k.startswith(f"{NS_REL}/publication/") or k.endswith("(added lines)")}
        found = {k: [b for b in BANNED_PUBLICATION_PHRASES if b in re.sub(r"\s+", " ", v).lower()]
                 for k, v in pub.items()}
        found = {k: v for k, v in found.items() if v}
        add("W01 publication text carries none of the banned overclaim phrases", bool(pub) and not found,
            {"files": sorted(pub), "found": found})
        r = subprocess.run([sys.executable, "-I", "-S", "-B", "docs/research_synthesis/verify_synthesis.py",
                            "--no-diff-check"], cwd=REPO, capture_output=True, text=True,
                           stdin=subprocess.DEVNULL, timeout=600)
        add("V01 research-synthesis document verifier (--no-diff-check) passes",
            r.returncode == 0 and "SYNTHESIS VERIFICATION OK" in r.stdout, r.stdout.strip()[:200] or r.stderr[:200])

    return {"schema": "rebaseguard.p5y.k5.partial-closeout.admin-checks.v1", "phase": phase, "head": head,
            "base": BASE, "scientific_computation": "NONE (administrative checks only)",
            "checks": out, "pass": all(c["pass"] for c in out),
            "summary": f"{sum(c['pass'] for c in out)}/{len(out)}"}


def sr_refs() -> dict:
    """Pickaxe over every ref: every commit that adds or removes the text 'SR K5'."""
    log = git("log", "--all", "--format=%H %ad %s", "--date=short", "-S", "SR K5").splitlines()
    commits = [l.split(" ", 2) for l in log]
    local_ok = [c for c in commits if c[0].startswith("a3547b9b")
                or git_ok("merge-base", "--is-ancestor", "c5324a78441c23aa985e59e7c878625e31a3fa4c", c[0])
                and git_ok("merge-base", "--is-ancestor", c[0], "HEAD")]
    unexpected = [c for c in commits if c not in local_ok]
    nrefs = len(git("for-each-ref", "--format=%(refname)", "refs/heads", "refs/remotes", "refs/tags").splitlines())
    return {"schema": "rebaseguard.p5y.k5.partial-closeout.sr-k5-refs.v1", "refs_scanned": nrefs,
            "commits_touching_SR_K5_text": [f"{c[0][:8]} {c[1]} {c[2][:100]}" for c in commits],
            "unexpected": [f"{c[0][:8]} {c[2][:100]}" for c in unexpected],
            "pass": not unexpected and SR_K5_TEXT in git("show", f"HEAD:{K5_STATUS_PATH}")}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase", choices=["prefreeze", "freeze", "adjudication", "publication"])
    ap.add_argument("--sr-refs", action="store_true")
    ap.add_argument("--out")
    a = ap.parse_args()
    if not (sys.flags.isolated and sys.flags.no_site and sys.flags.dont_write_bytecode):
        print("refused: run with python3 -I -S -B", file=sys.stderr)
        return 2
    res = sr_refs() if a.sr_refs else run_checks(a.phase or "prefreeze")
    txt = json.dumps(res, indent=1, sort_keys=True) + "\n"
    if a.out:
        pathlib.Path(a.out).write_text(txt)
    print(txt if not a.out else f"{res.get('summary', '')} pass={res['pass']} -> {a.out}")
    return 0 if res["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
