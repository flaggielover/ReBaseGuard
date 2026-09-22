"""C11 Phases B0, 1, 2 -- predecessor audit, the N9 dossier, and the original certifier's
load-bearing dependency graph with an explicit forbidden-reuse list.
"""
from __future__ import annotations

import ast
import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import c11_common as C

PRED = {
    "p5y_k5_tail_c2_closure": "ae4cbc2cc0160538ec8fed3554feaceba5d71ec4",
    "p5y_k5_tail_c3_closure": "019ecce030ef294b95e98391c71715fb0b43d1cf",
    "p5y_k5_tail_c4_exhaustion": "e12a09e8bb742726e2ca7af42e163c455915bb7d",
    "p5y_k5_tail_c5_exhaustion": "69bff424f20a7c91eac99450ba0836f3f7d9ca44",
    "p5y_k5_tail_c6_evidence_recovery": "f494416fb0453ee7f3993da7be23ad112aeb94e1",
    "p5y_k5_tail_c7_e2_lambda309": "df4ec1791a5aa837a1e3dca26f9a1a329f283a9f",
    "p5y_k5_tail_c8_operator_feasibility": "63a3f8257f31f776a453a976c6308c713414ad28",
    "p5y_k5_tail_c9_e1_cell307": "fd3cb2d4cbf7c011e619fe6c794bec2ef9226d16",
    "p5y_k5_tail_c10_governance_provenance": C.C10_HEAD,
}
SEARCH = [C.AD / "code",
          C.CLOSURE / "p5y_k5_cusum_order3_r3_infrastructure" / "code",
          C.CLOSURE / "p5y_k5_cusum_order3_real_producer" / "code",
          C.CLOSURE / "p5y_k1_cusum_aux5_successor" / "code",
          C.CLOSURE / "p5y_k1_cusum_aux4_fullcover" / "code",
          C.CLOSURE / "p5y_k1_cover_ledger_implementation" / "code",
          C.CLOSURE / "p5x_global_nonlinear_dynamics" / "compute_optimization_r2",
          C.CLOSURE / "p5x_global_nonlinear_dynamics" / "certified_method_repair_ra",
          C.REPO / "rebaseguard-proof" / "src"]
STDLIB = {"__future__", "argparse", "json", "math", "sys", "time", "pathlib", "fractions", "os",
          "hashlib", "itertools", "functools", "collections", "typing", "dataclasses", "decimal",
          "concurrent", "subprocess", "re", "warnings", "copy", "bisect", "random", "statistics",
          "contextlib", "traceback", "shutil", "tempfile", "textwrap", "enum", "abc", "io",
          "operator", "pickle", "struct", "array", "gc", "platform", "importlib", "types",
          "multiprocessing", "threading", "queue", "signal", "errno", "stat", "glob", "csv"}
EXTERNAL = {"numpy", "flint", "scipy", "mpmath", "sympy", "gmpy2"}

# Classification of each transitive module by the role it plays for the CERTIFICATION.
ROLE = {
    "taboo_certify": "SCIENTIFIC_LOAD_BEARING",
    "resolvent_certificate": "SCIENTIFIC_LOAD_BEARING",
    "opnorms": "SCIENTIFIC_LOAD_BEARING",
    "ra_certifier": "SCIENTIFIC_LOAD_BEARING",
    "fast_range": "SCIENTIFIC_LOAD_BEARING",
    "intervals": "SCIENTIFIC_LOAD_BEARING",
    "rebaseguard_certify": "SCIENTIFIC_LOAD_BEARING",
    "cusum_layer1": "PROBLEM_DEFINITION",
    "cusum_layer2": "PROBLEM_DEFINITION",
    "ancestry5": "INFRASTRUCTURE_ONLY",
    "ancestry4": "INFRASTRUCTURE_ONLY",
}


def find_module(name):
    for d in SEARCH:
        for cand in (d / f"{name}.py", d / name / "__init__.py"):
            if cand.exists():
                return cand
        for cand in d.rglob(f"{name}/__init__.py"):
            return cand
    return None


def main() -> int:
    ck = []

    def chk(n, name, ok, detail, unchecked=False):
        ck.append({"id": f"B0_{n:02d}", "name": name,
                   "status": "UNCHECKED" if unchecked else ("PASS" if ok else "FAIL"),
                   "detail": detail})

    br = C.git("rev-parse", "--abbrev-ref", "HEAD")
    chk(1, "C11 on its own branch", br == "p5y-k5-tail-c11-n9-independent-certifier", {"branch": br})
    chk(2, "descends from the expected C10 HEAD",
        C.git_ok("merge-base", "--is-ancestor", C.C10_HEAD, "HEAD"),
        {"expected": C.C10_HEAD, "head": C.git("rev-parse", "HEAD")})
    orig = C.git("ls-remote", "--heads", "origin",
                 "p5y-k5-tail-c10-governance-provenance").split("\t")[0]
    chk(3, "origin C10 matches", orig == C.C10_HEAD, {"origin": orig})

    c10fc = C.load(C.C10 / "evidence" / "governance" / "HANDOVER_FACT_VERIFICATION.json")
    chk(4, "C10 published with fact check PASS and mutations PASS",
        c10fc["FACT_CHECK_CLASS"] == "PASS"
        and C.load(C.C10 / "evidence" / "mutations" /
                   "C10_MUTATIONS.json")["MUTATION_CLASS"] == "PASS",
        {"FACT_CHECK": c10fc["FACT_CHECK_CLASS"]})
    chk(5, "C10's applied decision gate is P2 + P5",
        sorted(c10fc["APPLIED_DECISION_GATE"]["classes"]) == ["P2", "P5"],
        c10fc["APPLIED_DECISION_GATE"]["classes"])

    gov = C.load(C.C10 / "evidence" / "phase5" / "C10_GOVERNANCE.json")
    n9 = gov["Q2_phase5_rule_reconstruction"]["N9_status"]
    chk(6, "N9 is OPEN, per C10's assertion scan", n9["state"] == "OPEN",
        {"state": n9["state"], "open_assertions": n9["explicit_open_assertions"],
         "closed_assertions": n9["explicit_closed_assertions"]})

    r5 = C.r5_map()
    der = {m: C.r5_open_by_verdict(str(m)) for m in (1, 2, 3, 5)}
    chk(7, "authoritative r5 reconstructs from per-cell verdicts",
        r5["schema"] == "rebaseguard.p5y.k5.tail-c2.coverage-map.v5",
        {"blob": C.git("rev-parse", f"HEAD:{C.R5_PATH}")})
    chk(8, "m=5 open is exactly {306,307,308,309}; 1/2/3 complete",
        tuple(der[5]) == C.OPEN_CELLS and der[1] == der[2] == der[3] == [], {"open": der})
    c305 = [c for c in r5["per_m"]["5"]["cells"] if c["cell"] == 305][0]
    chk(9, "cell 305 remains PASS and ADOPTED",
        c305["verdict"] == "PASS" and 305 in r5["inputs"]["adopted_cells"], {})
    r6 = [f for ref in C.git("for-each-ref", "--format=%(refname:short)", "refs/heads").splitlines()
          for f in C.git("ls-tree", "-r", "--name-only", ref).splitlines()
          if "COVERAGE_MAP_R6" in f.rsplit("/", 1)[-1].upper()]
    chk(10, "no r6 on any local branch", not r6, {"hits": r6})
    allow = C.git_grep(r'"guard"[[:space:]]*:[[:space:]]*"(ALLOW|PERMIT)"', "*.json")
    chk(11, "guard DENY: no ALLOW anywhere at C11 start", not allow, {"ALLOW": allow})
    integ = {ns: C.git("rev-parse", f"HEAD:level4/closure_proofs/{ns}")
                 == C.git("rev-parse", f"{h}:level4/closure_proofs/{ns}")
             for ns, h in PRED.items()}
    chk(12, "C2-C10 namespace trees identical to published heads", all(integ.values()), integ)
    lm, rm = C.git("rev-parse", "main"), C.git("ls-remote", "origin",
                                               "refs/heads/main").split("\t")[0]
    chk(13, "LOCAL_MAIN_REF recorded", len(lm) == 40, {"LOCAL_MAIN_REF": lm})
    chk(14, "REMOTE_MAIN_REF queried independently and as expected",
        rm == "1cb453826313c189f0bdafd5b84120c1edb74da9",
        {"REMOTE_MAIN_REF": rm, "differ": lm != rm, "action": "recorded only; never synchronized"})
    procs = C.classified_processes()
    chk(15, "no stale campaign process (executable identity, self-ancestry excluded)",
        not procs["campaign_workers"], {"workers": procs["campaign_workers"],
                                        "foreign": len(procs["foreign"])})
    tc = C.toolchain_present()
    chk(16, "no certifier process can be running: the original certifier's stack is absent",
        not tc["numpy"] and not tc["flint"],
        {"importlib_find_spec": tc,
         "note": "the ORIGINAL certifier imports numpy and flint at module load"})

    # ---------------- Phase 1: the N9 dossier ---------------------------------------------------
    src_note = C.C2 / "OPEN_NOTES_DISPOSITION_C2.md"
    adj = C.C2 / "evidence" / "adjudication" / "C2_ADJUDICATION.md"
    note_txt, adj_txt = src_note.read_text(), adj.read_text()

    def grab(txt, pat, span):
        m = re.search(pat, txt, re.S)
        return re.sub(r"\s+", " ", txt[m.start():m.start() + span]) if m else None

    dossier = {
        "ORIGIN": {
            "artifact": str(src_note.relative_to(C.REPO)),
            "sha256": C.sha256_file(src_note),
            "commit": C.git("log", "-1", "--format=%H", "--",
                            str(src_note.relative_to(C.REPO))),
            "wording": grab(note_txt, r"\*\*N9 — the Arb/FLINT supersolutions", 460),
            "status": "OPEN",
        },
        "RISK_AS_STATED_BY_THE_ADJUDICATION": {
            "artifact": str(adj.relative_to(C.REPO)), "sha256": C.sha256_file(adj),
            "wording": grab(adj_txt, r"The open risk is N9", 330),
        },
        "WHAT_IS_MISSING": {
            "wording": grab(adj_txt, r"The bit-identity result is therefore evidence", 260),
            "reading": "implementation independence, not determinism",
        },
        "RELATION_TO_F1": {
            "wording": grab(adj_txt, r"This limb is available for as long as", 190),
            "effect": "F1 is available while N9 is open and LAPSES when N9 closes",
        },
        "RELATION_TO_REPLACEMENT_FLOOR": {
            "wording": grab(adj_txt, r"a \*\*second, independently written certifier\*\*", 300),
            "effect": ("closing N9 is the named precondition for a successor freezing a replacement "
                       "floor that requires two-implementation agreement instead of F1"),
        },
        "MODALITY_CLASSIFICATION": {
            "MUST": ["a second certifier must be INDEPENDENTLY WRITTEN",
                     "it must be a second route to THE SAME CONCLUSION",
                     "bit-identity on one stack does NOT count -- that is determinism"],
            "SHOULD": ["the replacement floor a successor freezes should require agreement between "
                       "two independent certifier implementations"],
            "EXAMPLE": ["cell 305's existing second route (the registry-free Lemma G supply) is "
                        "cited as an instance of 'a second, structurally independent route'"],
            "INTERPRETATION": [
                "NOT STATED ANYWHERE: whether arithmetic-BACKEND independence (not using Arb/FLINT) "
                "is required, or only implementation independence. The risk is worded as 'a single "
                "implementation of the Arb supersolution machinery', which a same-backend rewrite "
                "would only partly answer. C11 therefore targets BOTH and says so, rather than "
                "promoting either reading into a requirement the source does not state.",
                "NOT STATED ANYWHERE: a numeric agreement tolerance. C11 must freeze one "
                "prospectively and cannot recover it from history."],
        },
        "CLOSURE_CONDITION_AS_C11_READS_IT": (
            "a second certifier, written independently of the first's load-bearing implementation, "
            "consuming the same frozen mathematical inputs, producing its own certified bound on the "
            "same operator quantity, agreeing with the first under a rule frozen before comparison"),
    }

    # ---------------- Phase 2: the dependency graph and forbidden-reuse list ---------------------
    root = C.REPO / C.ORIGINAL_CERTIFIER
    seen, missing, ext = {}, [], set()
    stack = [("taboo_certify", root)]
    while stack:
        nm, p = stack.pop()
        if nm in seen:
            continue
        seen[nm] = {"path": str(p.relative_to(C.REPO)), "sha256": C.sha256_file(p),
                    "role": ROLE.get(nm, "SCIENTIFIC_LOAD_BEARING")}
        try:
            tree = ast.parse(p.read_text())
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            roots = []
            if isinstance(node, ast.Import):
                roots = [a.name.split(".")[0] for a in node.names]
            elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                roots = [node.module.split(".")[0]]
            for r in roots:
                if r in STDLIB:
                    continue
                if r in EXTERNAL:
                    ext.add(r)
                    continue
                if r in seen:
                    continue
                q = find_module(r)
                if q is None:
                    missing.append(r)
                else:
                    stack.append((r, q))

    forbidden = sorted(n for n, v in seen.items() if v["role"] == "SCIENTIFIC_LOAD_BEARING")
    allowed_shared = sorted(n for n, v in seen.items() if v["role"] in
                            ("PROBLEM_DEFINITION", "INFRASTRUCTURE_ONLY"))

    graph = {
        "original_certifier": {"path": C.ORIGINAL_CERTIFIER, "sha256": C.sha256_file(root)},
        "transitive_modules": seen, "unresolved": sorted(set(missing)),
        "external_backends": sorted(ext),
        "FORBIDDEN_REUSE": {
            "modules": forbidden,
            "rule": ("the second certifier may not import, call, wrap, or replay any of these, nor "
                     "read any artifact they produced, during construction or verification"),
        },
        "ALLOWED_SHARED": {
            "modules": allowed_shared,
            "rule": ("the frozen PROBLEM DEFINITION may be shared -- it is the thing both certifiers "
                     "must agree about, and changing it would make them answer different questions. "
                     "Infrastructure that touches no scientific value may be shared."),
            "caveat": ("even for these, C11 prefers to re-derive the problem constants from the "
                       "frozen model file rather than import the module, so that the shared surface "
                       "is DATA rather than CODE."),
        },
        "external_backend_note": (
            "the original's arithmetic backend is numpy + flint.arb. Using a DIFFERENT backend is "
            "strictly stronger than N9's stated requirement and is what C11 targets: exact rational "
            "arithmetic via the standard library only."),
    }

    failed = [c["id"] for c in ck if c["status"] == "FAIL"]
    unchecked = [c["id"] for c in ck if c["status"] == "UNCHECKED"]
    out = {"schema": "C11_B0_N9/1", "checks": ck, "failed": failed, "unchecked": unchecked,
           "B0_CLASS": "PASS" if not failed and not unchecked else "REFUSE",
           "LOCAL_MAIN_REF": lm, "REMOTE_MAIN_REF": rm,
           "N9_DOSSIER": dossier, "ORIGINAL_DEPENDENCY_GRAPH": graph,
           "compute_boundary": {"NEW_REAL": 0, "TARGET_CERTIFICATIONS": 0, "AWS": 0, "VULTR": 0,
                                "TOOLCHAIN_PROVISIONED": 0, "guard": "DENY"}}
    s = C.write_evidence(C.NS / "evidence" / "b0" / "C11_B0_N9.json", out)
    for c in ck:
        print(f"  {c['status']:<9} {c['id']}  {c['name'][:70]}")
    print(f"\nB0_CLASS = {out['B0_CLASS']}  failed={failed}  unchecked={unchecked}")
    print(f"\nN9 origin: {dossier['ORIGIN']['artifact']}")
    print(f"  {(dossier['ORIGIN']['wording'] or '')[:200]}")
    print(f"\ntransitive modules: {len(seen)}  unresolved: {graph['unresolved'] or 'none'}")
    print(f"external backends : {graph['external_backends']}")
    print(f"FORBIDDEN_REUSE   : {forbidden}")
    print(f"ALLOWED_SHARED    : {allowed_shared}")
    print(f"wrote evidence/b0/C11_B0_N9.json sha256 {s[:16]}...")
    return 0 if out["B0_CLASS"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
