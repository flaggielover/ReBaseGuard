"""K5 tail adoption floor r2 -- read-only verifier.

Checks, and records in evidence/FLOOR_R2_VERIFY.json:
  * every quoted frozen sentence the specification relies on occurs verbatim in its source, and the source is the
    bound blob at HEAD (C2, C10, THEOREM_AD, the N9 adjudication and its review);
  * both config JSONs verify their own sha256 field; they carry no JSON number value, and their only decimal
    tokens are the two inherited parameters (x1.25 and the disclosed 3.7e-97 offset);
  * the governance state: N9 adjudication and review in HEAD's lineage, r5 byte-identical, no r6, the consumed
    ref at G, nothing outside this namespace changed since the adjudication review;
  * no rendering of the original D1/D2 values (frozen hash set) and none of the independent D1/D2 values (hash set
    built in memory, never printed) in any file of this namespace.
It computes no Gamma, no atom constant and no margin.

    python3 -I -S -B floor_r2_verify.py [--out FILE]
"""
import argparse
import hashlib
import importlib.util
import json
import pathlib
import re
import subprocess
import sys
from fractions import Fraction as F

HERE = pathlib.Path(__file__).resolve().parent
NS = HERE.parent
REPO = NS.parents[2]
NS_REL = "level4/closure_proofs/p5y_k5_tail_floor_r2"
L = "level4/closure_proofs"
C2A = f"{L}/p5y_k5_tail_c2_closure/evidence/adjudication/C2_ADJUDICATION.md"
C2N = f"{L}/p5y_k5_tail_c2_closure/phase_d/CELL_306_ADOPTION.md"
C10R = f"{L}/p5y_k5_tail_c10_governance_provenance/README.md"
C10J = f"{L}/p5y_k5_tail_c10_governance_provenance/evidence/phase5/C10_GOVERNANCE.json"
TAD = f"{L}/p5y_k5_perron_deflated_resolvent/theorem/THEOREM_AD.md"
DC = f"{L}/p5y_k5_perron_deflated_resolvent/code/deflated_consume.py"
C2F = f"{L}/p5y_k5_tail_c2_closure/code/c2_d5_forecast.py"
ADJ = f"{L}/p5y_k5_tail_c11rd_d1d2_extension/adjudication/ADJUDICATION_C11RD_N9.md"
ADJR = f"{L}/p5y_k5_tail_c11rd_d1d2_extension/review/C11RD_ADJUDICATION_REVIEW.md"
R5 = f"{L}/p5y_k5_tail_c2_closure/evidence/coverage/K5_COVERAGE_MAP_R5.json"
ENV = {"PATH": "/usr/bin:/bin", "HOME": "/var/empty", "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": "/dev/null",
       "GIT_NO_REPLACE_OBJECTS": "1", "GIT_OPTIONAL_LOCKS": "0"}

C11R = f"{L}/p5y_k5_tail_c11r_n9_statement_alignment"
C11RD = f"{L}/p5y_k5_tail_c11rd_d1d2_extension"
BLOBS = {C2A: "cfc5b3ed9a74", C2N: "f5db4cd9286f", C10R: "6e0e70a988da", C10J: "bc3fb1e6118c", TAD: "586ecc6d3a9e",
         DC: "a0a836fa83c6", C2F: "18403dbec855", R5: "f978eeb6",
         # bound by blob id only (not opened here)
         f"{L}/p5y_k5_tail_c2_closure/evidence/phase_d5/C2_D5_FORECAST.json": "a191557f",
         f"{L}/p5y_k5_tail_c2_closure/evidence/registry_c2/REGISTRY_C2.json": "1a3adfd3",
         f"{L}/p5y_k5_tail_operator_registry/evidence/registry_c1/REGISTRY_C1.json": "f6d84bdb",
         f"{L}/p5y_k5_m5_tail_closure/code/tct_rule.py": "98f6eee4",
         f"{C11R}/evidence/comparison/C11R_COMPARISON.json": "5269c2aa",
         f"{C11R}/evidence/runs/C11R_RUNS.json": "a5351603",
         f"{C11R}/evidence/table/C11R_N9_STATEMENTS.json": "58b4066f"}
# the C11RD comparison and runs are bound by commit (8e2defab, 4547bcd4) and the runs' sha256
C11RD_AT = {f"{C11RD}/evidence/comparison/C11RD_COMPARISON.json": "8e2defab",
            f"{C11RD}/evidence/runs/C11RD_RUNS.json": "4547bcd4"}
C11RD_RUNS_SHA256_PREFIX = "c28a8cea"
# every commit the rule or the gate cites: (commit, a word its subject must contain)
COMMITS = [("7d67989d", "adjudication"), ("fb237288", "ADJUDICATION_ACCEPTED"), ("22537709", "EXECUTION_ACCEPTED"),
           ("7375b9cd", "COMPARISON_ACCEPTED"), ("2c24a989", "comparison"), ("5ff4cc5b", "seal"),
           ("3c1eff11", "READY_TO_QUALIFY"), ("e27c2ffd", "QUALIFICATION_ACCEPTED"), ("db1c6118", "EXECUTION_ACCEPTED"),
           ("90265349", "COMPARISON_ACCEPTED"), ("8e2defab", "comparator"), ("4547bcd4", "SEAL"), ("ce5b8595", "freeze"),
           ("4b716d43", "")]
# sources a quotation in the specification may come from
SPEC_QUOTE_SOURCES = [C2A, C2N, C10R, C10J, TAD, DC, C2F, ADJ, ADJR]

QUOTES = [
    (C2A, "It is **prospective**: it governs future adoptions of K5 m = 5 tail cells from this"),
    (C2A, "> A pair (m, k) may be adopted only if the frozen K5-B certifies it (Γ < 0 under the campaign's own frozen closure"),
    (C2A, "> **F1 — supply independence.** Γ < 0 also holds under a certified atom-constant supply that does **not** depend on"),
    (C2A, "> certifier of the operator constants) remains open, and lapses when N9 is closed."),
    (C2A, "> **F2 — degradation survival.** Γ < 0 still holds when every atom constant of the chosen supply is degraded"),
    (C2A, "> uniformly in the unfavourable direction by the factor **×1.25**, i.e. the cell's uniform-A margin is ≥ 1.25."),
    (C2A, "- a **second, independently written certifier** reproducing the six operator constants for cell 306 (closing N9),"),
    (C2A, "  at which point the registry-dependence objection is answered and a successor should freeze a replacement floor"),
    (C2A, "  requiring agreement between two independent certifier implementations rather than F1; **or**"),
    (C2A, "1. **The floor above is now the standard** for K5 m = 5 tail adoptions, prospectively. A successor that wishes to"),
    (C2A, "   replace it must freeze the replacement **before** recomputing any magnitude, as the D′ document itself insists."),
    (C2A, "4. **N9 and N10 remain open and are now load-bearing for adoption**, by limb F1 of the floor."),
    (C2A, "the componentwise best of C1's and C2's six operator constants"),
    (C2A, "The open risk is N9: a possible systematic error"),
    (C2N, "That is a\nre-execution with different inputs, not an independent check"),
    (C10R, "> A future successor **may** freeze a different prospective adoption rule without retroactively"),
    (C10R, "What it may **not** do is re-adjudicate 305 or 306 under a new rule, or apply its own"),
    (C10J, "answer IMPLEMENTATION INDEPENDENCE, not merely add margin"),
    (C10J, "the floor in force at the time of that successor's own freeze"),
    (TAD, "A0 = Ā_eff,   A1 = Ā_eff (κ₁C + δ₁),   A2 = Ā_eff (2κ₁²C² + κ₂C + 2κ₁Cδ₁ + 2δ₁² + δ₂),   Ā_eff := min(Ā, τ/D_lo)"),
    (DC, "def atom_constants_r2(Abar: F, tau: F, C: F, Dlo: F, D1: F, D2: F, k1: F = K1_BOUND, k2: F = K2_BOUND) -> dict:"),
    (C2F, '"""The gate\'s D4 rule: A_j := min over valid supplies, componentwise, with provenance per field."""'),
    (C2F, 'raise SystemExit("operator constants violate tau >= 1, C >= tau, Dlo > 0, Abar >= 1")'),
]


def git(*args, text=True):
    return subprocess.run(["/usr/bin/git", "--no-replace-objects", "-c", "core.commitGraph=false", "-C", str(REPO), *args],
                          capture_output=True, text=text, env=ENV)


def numbers_in(obj) -> list:
    if isinstance(obj, bool) or obj is None or isinstance(obj, str):
        return []
    if isinstance(obj, (int, float)):
        return [obj]
    if isinstance(obj, dict):
        return [x for v in obj.values() for x in numbers_in(v)]
    return [x for v in obj for x in numbers_in(v)]


def strings_in(obj) -> list:
    if isinstance(obj, str):
        return [obj]
    if isinstance(obj, dict):
        return [s for k, v in obj.items() for s in [k, *strings_in(v)]]
    if isinstance(obj, list):
        return [s for v in obj for s in strings_in(v)]
    return []


def norm(text: str) -> str:
    """Whitespace-normalised text with markdown blockquote markers removed (quotations in the spec are re-wrapped)."""
    return " ".join(" ".join(re.sub(r"^\s*(?:>\s?)*", "", ln) for ln in text.splitlines()).split())


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out")
    a = ap.parse_args(argv)
    C, info = {}, {}
    blob_ok = {p: git("rev-parse", f"HEAD:{p}").stdout.strip().startswith(b) for p, b in BLOBS.items()}
    C["every bound source is its recorded blob at HEAD"] = all(blob_ok.values())
    info["blobs"] = blob_ok
    at_ok = {p: git("rev-parse", f"{c}:{p}").stdout.strip() == git("rev-parse", f"HEAD:{p}").stdout.strip() != ""
             for p, c in C11RD_AT.items()}
    runs_raw = git("show", f"HEAD:{C11RD}/evidence/runs/C11RD_RUNS.json", text=False).stdout
    C["C11RD comparison and runs unchanged since their commits; runs sha256 as recorded"] = all(at_ok.values()) and \
        hashlib.sha256(runs_raw).hexdigest().startswith(C11RD_RUNS_SHA256_PREFIX)
    subj = {c: git("log", "-1", "--format=%s", c).stdout.strip() for c, _ in COMMITS}
    bad = [c for c, w in COMMITS if git("merge-base", "--is-ancestor", c, "HEAD").returncode != 0 or w not in subj[c]]
    C[f"all {len(COMMITS)} cited commits are in HEAD's lineage with the cited role"] = bad == []
    info["commit_problems"] = bad
    missing = [(p, q[:70]) for p, q in QUOTES if q not in git("show", f"HEAD:{p}").stdout]
    C[f"all {len(QUOTES)} quoted frozen sentences occur verbatim in their sources"] = missing == []
    info["missing_quotes"] = missing
    srcs = [norm(git("show", f"HEAD:{p}").stdout) for p in SPEC_QUOTE_SOURCES]
    spec_quotes = re.findall(r'\*"(.+?)"\*', (NS / "FLOOR_R2_SPECIFICATION.md").read_text(), re.S)
    pieces = [norm(x).strip(" ,.") for q in spec_quotes for x in re.split(r"…|\.\.\.", q) if norm(x).strip(" ,.")]
    unfound = [x[:70] for x in pieces if not any(x in s for s in srcs)]
    C["every quotation in the specification occurs verbatim (modulo line wrapping and elisions) in a bound source"] = \
        bool(spec_quotes) and unfound == []
    info["specification_quotations"] = len(spec_quotes)
    info["specification_quotations_unfound"] = unfound
    for name in ("K5_TAIL_ADOPTION_FLOOR_R2.json", "CELL306_ADOPTION_GATE_R2.json"):
        body = json.loads((NS / "config" / name).read_text())
        sha = body.pop("sha256")
        C[f"{name}: sha256 field verifies"] = hashlib.sha256(json.dumps(body, sort_keys=True).encode()).hexdigest() == sha
        C[f"{name}: no JSON number value (only text, ids and booleans)"] = numbers_in(body) == []
        decs = sorted({t for s in strings_in(body) for t in re.findall(r"(?<![0-9A-Za-z./])[0-9]+\.[0-9]+(?:e-?[0-9]+)?", s)})
        C[f"{name}: decimal tokens are only the inherited parameters"] = set(decs) <= {"1.25", "3.7e-97"}
        info[f"{name}_decimal_tokens"] = decs
    adj = git("show", f"HEAD:{ADJ}").stdout
    rev = git("show", f"HEAD:{ADJR}").stdout
    C["N9 adjudication holds exactly one N9_CLOSED line; its review exactly one ADJUDICATION_ACCEPTED line"] = \
        [ln.strip() for ln in adj.splitlines()].count("N9_CLOSED") == 1 and \
        [ln.strip() for ln in rev.splitlines()].count("ADJUDICATION_ACCEPTED") == 1
    C["adjudication 7d67989d and its review fb237288 are in HEAD's lineage"] = all(
        git("merge-base", "--is-ancestor", c, "HEAD").returncode == 0 for c in ("7d67989d3da6595180ca3c01d34f2bdf4543ae73",
                                                                              "fb237288a7cf481c14cd2f85c18bb363d2ebe44a"))
    names = git("ls-tree", "-r", "--name-only", "HEAD").stdout.split()
    C["no K5 coverage map r6 exists"] = not any(re.search(r"K5_COVERAGE_MAP_R6", n, re.I) for n in names)
    C["the consumed execution ref still points at G"] = git("rev-parse", "refs/c11rd/r1-execution-consumed").stdout.strip() == \
        "4b716d43ce8c48fb52dd320b91c33d2379cce410"
    changed = git("diff", "--name-only", "fb237288a7cf481c14cd2f85c18bb363d2ebe44a", "HEAD").stdout.split()
    pending = [ln[3:] for ln in git("status", "--porcelain", "--untracked-files=all").stdout.splitlines()]
    foreign = [p for p in changed + pending if not p.startswith(NS_REL + "/")]
    C["nothing outside this namespace changed since the adjudication review"] = foreign == []
    info["foreign_changes"] = foreign
    # leak scans (values never printed)
    code = REPO / f"{L}/p5y_k5_tail_c11rd_d1d2_extension/code"
    spec = importlib.util.spec_from_file_location("q", REPO / f"{L}/p5y_k5_tail_c11rd_d1d2_extension/qualification_r1q_r1/code/c11rd_qualify.py")
    Q = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(Q)
    texts = {str(f.relative_to(NS)): f.read_text() for f in sorted(NS.rglob("*")) if f.is_file()}
    runs = json.loads((code.parent / "evidence/runs/C11RD_RUNS.json").read_text())
    ind = frozenset(hashlib.sha256(x.encode()).hexdigest() for k in ("D1", "D2")
                    for x in Q.CM.value_patterns(format(float(F(runs["targets"][k]["value"])), ".12f")))
    C["no rendering of the original D1/D2 values in this namespace"] = not Q._broad_hashed_scan(texts, Q.V.ORIGINAL_PATTERN_SHA256)["hits"]
    C["no rendering of the independent D1/D2 values in this namespace"] = not Q._broad_hashed_scan(texts, ind)["hits"]
    info["files_scanned"] = sorted(texts)
    # negative controls: each detector above must fire on a planted defect and stay silent on a clean input
    decoy = frozenset(hashlib.sha256(x.encode()).hexdigest() for x in Q.CM.value_patterns("0.123456789012"))
    ctl = {
        "mutated quotation is not found": not any("re-adjudicating 306 under a new rule, which is the thing" in s for s in srcs)
                                          and any("re-adjudicating 305 or 306 under a new rule, which is the thing" in s for s in srcs),
        "planted JSON number is detected": numbers_in({"a": [{"b": 1}]}) == [1],
        "planted decimal token is detected": re.findall(r"(?<![0-9A-Za-z./])[0-9]+\.[0-9]+(?:e-?[0-9]+)?", "x 2.5") == ["2.5"],
        "planted decoy value is detected; clean text is not": bool(Q._broad_hashed_scan({"x": "v 0.1234567890 w"}, decoy)["hits"])
                                                              and not Q._broad_hashed_scan({"x": "clean"}, decoy)["hits"],
        "a non-ancestor commit is refused": git("merge-base", "--is-ancestor", "HEAD", "7d67989d").returncode != 0,
    }
    C["negative controls: every detector fires on a planted defect"] = all(ctl.values())
    info["negative_controls"] = ctl
    out = {"schema": "rebaseguard.p5y.k5.tail-floor-r2.verify", "HEAD": git("rev-parse", "HEAD").stdout.strip(),
           "pass": all(C.values()), "checks": C, "information": info, "verifier_sha256": hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()}
    text = json.dumps(out, indent=1, sort_keys=True, ensure_ascii=False) + "\n"
    if a.out:
        pathlib.Path(a.out).write_text(text)
    print(f"FLOOR_R2_VERIFY {'PASS' if out['pass'] else 'FAIL'} ({sum(C.values())}/{len(C)})")
    for k, v in C.items():
        if not v:
            print("  FAIL", k)
    return 0 if out["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
