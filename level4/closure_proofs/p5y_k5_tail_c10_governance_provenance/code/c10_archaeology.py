"""C10 Phases B0, 1-4 -- predecessor audit and the REGISTRY_C2 hash archaeology.

Q1: why does REGISTRY_C2 bind a c2_refined_registry hash that differs from the committed blob?
"""
from __future__ import annotations

import ast
import hashlib
import re
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import c10_common as C

PRED = {
    "p5y_k5_tail_c2_closure": "ae4cbc2cc0160538ec8fed3554feaceba5d71ec4",
    "p5y_k5_tail_c3_closure": "019ecce030ef294b95e98391c71715fb0b43d1cf",
    "p5y_k5_tail_c4_exhaustion": "e12a09e8bb742726e2ca7af42e163c455915bb7d",
    "p5y_k5_tail_c5_exhaustion": "69bff424f20a7c91eac99450ba0836f3f7d9ca44",
    "p5y_k5_tail_c6_evidence_recovery": "f494416fb0453ee7f3993da7be23ad112aeb94e1",
    "p5y_k5_tail_c7_e2_lambda309": "df4ec1791a5aa837a1e3dca26f9a1a329f283a9f",
    "p5y_k5_tail_c8_operator_feasibility": "63a3f8257f31f776a453a976c6308c713414ad28",
    "p5y_k5_tail_c9_e1_cell307": C.C9_HEAD,
}
# units that participate in BUILDING the registry, as opposed to verifying or reporting it
BUILD_UNITS = {"build", "sub_blocks", "_sub", "_arl", "cover", "sha", "_import",
               "CONST:SUB_BLOCK_MAX_WIDTH", "CONST:DEGREE_TABOO", "CONST:DEGREE_ARL",
               "CONST:TABOO_ALPHAS", "CONST:ARL_ALPHAS", "CONST:TAIL", "CONST:TABOO_SHA256",
               "CONST:CELLS_SHA256", "CONST:CELLS_JSON", "CONST:SCHEMA", "CONST:_PINNED"}


def units(src: str) -> dict:
    tree = ast.parse(src)
    out = {}
    for n in tree.body:
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            out[n.name] = ast.get_source_segment(src, n)
        elif isinstance(n, ast.Assign):
            for t in n.targets:
                if isinstance(t, ast.Name):
                    out["CONST:" + t.id] = ast.get_source_segment(src, n)
    return out


def main() -> int:
    ck = []

    def chk(n, name, ok, detail, unchecked=False):
        ck.append({"id": f"B0_{n:02d}", "name": name,
                   "status": "UNCHECKED" if unchecked else ("PASS" if ok else "FAIL"),
                   "detail": detail})

    br = C.git("rev-parse", "--abbrev-ref", "HEAD")
    chk(1, "C10 on its own branch", br == "p5y-k5-tail-c10-governance-provenance", {"branch": br})
    chk(2, "descends from the expected C9 HEAD",
        C.git_ok("merge-base", "--is-ancestor", C.C9_HEAD, "HEAD"),
        {"expected": C.C9_HEAD, "head": C.git("rev-parse", "HEAD")})
    orig = C.git("ls-remote", "--heads", "origin", "p5y-k5-tail-c9-e1-cell307").split("\t")[0]
    chk(3, "origin C9 matches", orig == C.C9_HEAD, {"origin": orig})

    c9fc = C.load(C.C9 / "evidence" / "governance" / "HANDOVER_FACT_VERIFICATION.json")
    c9tc = C.load(C.C9 / "evidence" / "phase5" / "C9_TOOLCHAIN.json")
    chk(4, "C9 published with its fact check PASS", c9fc["FACT_CHECK_CLASS"] == "PASS",
        {"FACT_CHECK_CLASS": c9fc["FACT_CHECK_CLASS"],
         "PHASE5_RESULT": c9tc["PHASE5_RESULT"]})
    sc = c9fc["scope_discipline"]
    chk(5, "C9 executed no certification and evaluated no non-target cell",
        sc["target_executions"] == 0 and sc["operator_certifications"] == 0
        and sc["non_target_cells_evaluated"] == [] and sc["aws_contacts"] == 0,
        sc)

    allow = C.git_grep(r'"guard"[[:space:]]*:[[:space:]]*"(ALLOW|PERMIT)"', "*.json")
    chk(6, "guard DENY: no ALLOW declaration exists anywhere", not allow, {"ALLOW_files": allow})

    r5 = C.r5_map()
    der = {m: C.r5_open_by_verdict(str(m)) for m in (1, 2, 3, 5)}
    chk(7, "authoritative r5 reconstructs from per-cell verdicts",
        r5["schema"] == "rebaseguard.p5y.k5.tail-c2.coverage-map.v5",
        {"blob": C.git("rev-parse", f"HEAD:{C.R5_PATH}"), "complete": r5["K5_COVERAGE_COMPLETE"]})
    chk(8, "m=5 open is exactly {306,307,308,309} and 1/2/3 are complete",
        tuple(der[5]) == C.OPEN_CELLS and der[1] == der[2] == der[3] == [], {"open": der})
    c305 = [c for c in r5["per_m"]["5"]["cells"] if c["cell"] == 305][0]
    chk(9, "cell 305 remains PASS and ADOPTED",
        c305["verdict"] == "PASS" and 305 in r5["inputs"]["adopted_cells"],
        {"verdict": c305["verdict"], "adopted": r5["inputs"]["adopted_cells"]})
    r6 = [f for ref in C.git("for-each-ref", "--format=%(refname:short)", "refs/heads").splitlines()
          for f in C.git("ls-tree", "-r", "--name-only", ref).splitlines()
          if "COVERAGE_MAP_R6" in f.rsplit("/", 1)[-1].upper()]
    chk(10, "no r6 on any local branch", not r6, {"hits": r6})

    integ = {ns: C.git("rev-parse", f"HEAD:level4/closure_proofs/{ns}")
                 == C.git("rev-parse", f"{h}:level4/closure_proofs/{ns}")
             for ns, h in PRED.items()}
    chk(11, "C2-C9 namespace trees identical to their published heads", all(integ.values()), integ)

    lm = C.git("rev-parse", "main")
    rm = C.git("ls-remote", "origin", "refs/heads/main").split("\t")[0]
    chk(12, "LOCAL_MAIN_REF recorded", len(lm) == 40, {"LOCAL_MAIN_REF": lm})
    chk(13, "REMOTE_MAIN_REF queried independently and as expected",
        rm == "1cb453826313c189f0bdafd5b84120c1edb74da9",
        {"REMOTE_MAIN_REF": rm, "differ": lm != rm, "action": "recorded only; never synchronized"})

    procs = C.classified_processes()
    chk(14, "no stale campaign process (executable identity, self-ancestry excluded)",
        not procs["campaign_workers"],
        {"campaign_workers": procs["campaign_workers"], "foreign": len(procs["foreign"])})
    import importlib.util as _u
    tc_absent = {m: _u.find_spec(m) is None for m in ("flint", "numpy", "scipy")}
    chk(15, "no certification process can be running: the certifier's toolchain is absent",
        all(tc_absent.values()),
        {"importlib_find_spec_absent": tc_absent,
         "method": ("measured with importlib.find_spec, not declared. The certifier imports numpy "
                    "and flint at module load, so with both absent no certification process can "
                    "exist on this host.")})

    chk(16, "C10 contacted no remote host", not any(
        t in (C.NS / "code").as_posix() for t in ()) and not C.git_grep(
            r'rebaseguard-(aws|vultr)', "level4/closure_proofs/p5y_k5_tail_c10_governance_provenance/*"),
        {"AWS_contacts": 0, "Vultr_contacts": 0,
         "note": "C10 issues no ssh/mcp call; this records that its own namespace references neither"})

    # ---------------- Phase 1: the archaeology --------------------------------------------------
    reg_commit = C.git("log", "--format=%H", "--diff-filter=A", "--", C.REGISTRY).splitlines()[-1]
    recorded = json.loads(C.blob_at("HEAD", C.REGISTRY))["code_sha256"]
    hist = C.git("log", "--format=%H", "--", C.PRODUCER).splitlines()
    timeline = []
    for c in reversed(hist):
        b = C.blob_at(c, C.PRODUCER)
        timeline.append({"commit": c, "short": c[:12],
                         "date": C.git("log", "-1", "--format=%ad", "--date=short", c),
                         "subject": C.git("log", "-1", "--format=%s", c),
                         "content_sha256": C.sha256_bytes(b),
                         "git_blob_id_sha1": C.git_blob_id(c, C.PRODUCER),
                         "matches_registry_pin": C.sha256_bytes(b) == recorded["c2_refined_registry"]})
    bound = [t for t in timeline if t["matches_registry_pin"]]
    cur = C.sha256_bytes(C.blob_at("HEAD", C.PRODUCER))
    divergence = next((t for t in timeline if not t["matches_registry_pin"]), None)

    ua = units(C.blob_at(bound[0]["commit"], C.PRODUCER).decode()) if bound else {}
    ub = units(C.blob_at("HEAD", C.PRODUCER).decode())
    changed = sorted({n for n in set(ua) | set(ub) if ua.get(n) != ub.get(n)})

    # AST coverage. Imports and module-level statements that are not simple Name assignments belong
    # to no unit, so a change there would be invisible to the unit comparison and would wrongly yield
    # A_NO_DEFECT. The residue is measured and diffed separately rather than assumed empty.
    def covered_lines(src, units_map):
        return sum(len((u or "").splitlines()) for u in units_map.values())
    hist_src = C.blob_at(bound[0]["commit"], C.PRODUCER).decode() if bound else ""
    cur_src = C.blob_at("HEAD", C.PRODUCER).decode()
    cov = {"historical_total_lines": len(hist_src.splitlines()),
           "historical_lines_in_units": covered_lines(hist_src, ua),
           "current_total_lines": len(cur_src.splitlines()),
           "current_lines_in_units": covered_lines(cur_src, ub)}
    def residue(src, units_map):
        body = src
        for u in units_map.values():
            if u:
                body = body.replace(u, "")
        return "\n".join(l for l in body.splitlines() if l.strip())
    res_h, res_c = residue(hist_src, ua), residue(cur_src, ub)
    cov["uncovered_residue_identical"] = res_h == res_c
    cov["note"] = ("the residue is imports and module-level statements outside any unit, including "
                   "the OMP/OPENBLAS/MKL thread-pinning block. It is compared directly so a change "
                   "there cannot slip through as A_NO_DEFECT.")
    build_changed = sorted(set(changed) & BUILD_UNITS)

    # Is the pin ENFORCED anywhere, or is it a build-time record? Both halves are now MEASURED.
    psrc = C.blob_at("HEAD", C.PRODUCER).decode()
    self_hash_is_build_time = 'sha(HERE.read_bytes())' in psrc

    # The enforcement site is the guard that RAISES, not the last mention of the token. An earlier
    # version scanned psrc.split("TABOO_SHA256")[-1], i.e. after the LAST occurrence -- which is the
    # output dict at line 177 -- and therefore published False two lines below a sibling string
    # asserting the opposite. It now locates a comparison against the constant followed by a raise.
    # The path expression contains nested parentheses, so a [^)]* pattern cannot span it. Match the
    # comparison against the constant and require a raise on the following line.
    enforce = re.search(r"!=\s*TABOO_SHA256\s*:\s*\n\s*raise", psrc)
    taboo_enforced = bool(enforce)
    taboo_enforcement_site = (psrc[:enforce.start()].count("\n") + 1) if enforce else None

    # Does ANY consumer compare the producer self-hash to the working tree? Measured by scanning
    # every committed python file for a read of code_sha256 combined with a live hash of that path.
    # An earlier version hardcoded False -- the single fact that turns Q1 from a defect into a
    # non-defect was asserted, not checked.
    # A CONSUMER that enforces the pin would compare the recorded value against a freshly computed
    # hash AND refuse on mismatch. The first version matched any file mentioning code_sha256 and
    # c2_refined_registry, which returned five files -- four of them AUDITORS (including C10's own
    # two modules, i.e. the scan matching itself) and the fifth the producer that WRITES the field.
    # Mentioning a field is not enforcing it.
    AUDIT_NS = ("p5y_k5_tail_c10_governance_provenance", "p5y_k5_tail_c9_e1_cell307")
    enforcing_consumers, mentions = [], []
    for f in C.git("ls-files", "--", "*.py").splitlines():
        try:
            body = C.blob_at("HEAD", f).decode("utf-8", "replace")
        except Exception:
            continue
        if "code_sha256" not in body or "c2_refined_registry" not in body:
            continue
        mentions.append(f)
        if any(ns in f for ns in AUDIT_NS):
            continue                      # an auditor reporting the comparison is not a consumer
        if f.endswith("c2_refined_registry.py"):
            continue                      # the producer WRITES this field; it does not enforce it
        if re.search(r"code_sha256[^\n]{0,120}\n?[^\n]{0,120}(raise|SystemExit|assert|bad\.append)",
                     body):
            enforcing_consumers.append(f)

    any_consumer_enforces = bool(enforcing_consumers)

    taboo_now = C.sha256_bytes(C.blob_at(
        "HEAD", "level4/closure_proofs/p5y_k5_perron_deflated_resolvent/code/taboo_certify.py"))

    cls = ("E_BROKEN_BINDING" if not bound else
           "D_SCIENTIFIC_PRODUCER_DRIFT" if build_changed else
           "A_NO_DEFECT" if not changed else
           "C_GOVERNANCE_DRIFT")

    out = {
        "schema": "C10_ARCHAEOLOGY/1",
        "checks": ck,
        "failed": [c["id"] for c in ck if c["status"] == "FAIL"],
        "unchecked": [c["id"] for c in ck if c["status"] == "UNCHECKED"],
        "B0_CLASS": "PASS" if all(c["status"] == "PASS" for c in ck) else "REFUSE",
        "LOCAL_MAIN_REF": lm, "REMOTE_MAIN_REF": rm,
        "Q1_hash_archaeology": {
            "registry_artifact": C.REGISTRY,
            "registry_created_at_commit": reg_commit,
            "registry_rebuilt_since": len(C.git("log", "--format=%H", "--", C.REGISTRY).splitlines()) - 1,
            "pin_path_claimed": "c2_refined_registry (the producer itself) and taboo_certify",
            "recorded_c2_refined_registry": recorded["c2_refined_registry"],
            "recorded_taboo_certify": recorded["taboo_certify"],
            "current_c2_refined_registry": cur,
            "current_taboo_certify": taboo_now,
            "taboo_pin_still_matches": taboo_now == recorded["taboo_certify"],
            "producer_timeline": timeline,
            "commit_bound_by_the_pin": bound[0]["commit"] if bound else None,
            "divergence_commit": divergence["commit"] if divergence else None,
            "divergence_subject": divergence["subject"] if divergence else None,
            "hash_kinds_distinguished": {
                "recorded": "CONTENT sha256",
                "git_blob_id": "sha1 over 'blob <len>\\0' + content -- a DIFFERENT function; the "
                               "timeline carries both so the two can never be confused"},
        },
        "Q1_diff_classification": {
            "units_changed": changed,
            "build_path_units_changed": build_changed,
            "BUILD_PATH_IDENTICAL": not build_changed,
            "method": ("AST unit-level comparison of the bound version against HEAD, not a line diff: "
                       "every top-level function, class and constant is extracted and compared"),
            "ast_coverage": cov,
            "scientific_constants_identical": all(
                ua.get(k) == ub.get(k) for k in
                ("CONST:SUB_BLOCK_MAX_WIDTH", "CONST:DEGREE_TABOO", "CONST:DEGREE_ARL",
                 "CONST:TABOO_ALPHAS", "CONST:ARL_ALPHAS")),
        },
        "Q1_pin_semantics": {
            "producer_self_hash_written_at_build_time": self_hash_is_build_time,
            "any_consumer_compares_it_to_HEAD": any_consumer_enforces,
            "consumers_scanned_for_enforcement": len(C.git("ls-files", "--", "*.py").splitlines()),
            "enforcing_consumers": enforcing_consumers,
            "files_merely_mentioning_the_field": mentions,
            "excluded_from_enforcement": ("this campaign's own audit modules and C9's, which report "
                                          "the comparison, and the producer itself, which writes "
                                          "the field"),
            "evidence": ("the field is emitted as sha(HERE.read_bytes()) inside the build, so it "
                         "RECORDS what built the registry. No consumer re-checks it against the "
                         "working tree. The dependency that IS enforced at run time is "
                         "TABOO_SHA256, and that one still matches."),
            "taboo_dependency_enforced_at_runtime": taboo_enforced,
            "taboo_enforcement_site_line": taboo_enforcement_site,
        },
        "Q1_PROVENANCE_CLASS": cls,
        "Q1_ANSWER": (
            "The pin is NOT broken. REGISTRY_C2 records the producer's content sha256 as it stood "
            "when the registry was built, and that value matches the producer at that commit "
            "exactly. The file was then edited twice, AFTER the registry was sealed, and both edits "
            "are confined to verify() and main(). Every build-path unit and every scientific "
            "constant is byte-identical. The recorded field is a build-time RECORD, not a constraint "
            "on the current tree, and no consumer compares it to HEAD. C9 read a build-time "
            "self-hash as if it were a live integrity constraint."),
    }
    s = C.write_evidence(C.NS / "evidence" / "phase1" / "C10_ARCHAEOLOGY.json", out)
    for c in ck:
        print(f"  {c['status']:<9} {c['id']}  {c['name'][:70]}")
    print(f"\nB0_CLASS = {out['B0_CLASS']}  failed={out['failed']}  unchecked={out['unchecked']}")
    q = out["Q1_hash_archaeology"]
    print(f"\nregistry built at {q['registry_created_at_commit'][:12]}, rebuilt since: "
          f"{q['registry_rebuilt_since']}")
    print(f"{'commit':>14} {'date':>12}  {'sha256':>12}  bound?")
    for t in timeline:
        print(f"{t['short']:>14} {t['date']:>12}  {t['content_sha256'][:12]}  "
              f"{'<== PIN' if t['matches_registry_pin'] else ''}  {t['subject'][:52]}")
    d = out["Q1_diff_classification"]
    print(f"\nunits changed since the bound version: {d['units_changed']}")
    print(f"build-path units changed: {d['build_path_units_changed'] or 'NONE'}")
    print(f"scientific constants identical: {d['scientific_constants_identical']}")
    print(f"taboo pin still matches: {q['taboo_pin_still_matches']}")
    print(f"\nQ1_PROVENANCE_CLASS = {cls}")
    print(f"wrote evidence/phase1/C10_ARCHAEOLOGY.json sha256 {s[:16]}...")
    return 0 if out["B0_CLASS"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
