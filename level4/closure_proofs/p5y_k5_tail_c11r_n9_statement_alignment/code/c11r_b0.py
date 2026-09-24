"""C11R Phase B0 -- reconstruction of the authoritative predecessor state.

Every fact is established by something executable. LOCAL_MAIN_REF and REMOTE_MAIN_REF are recorded
SEPARATELY, because a scratch clone's ls-remote can read the local repository rather than GitHub.

REVISION 3 (review round 2, B-2). Revision 2 json-loaded every JSON file under the closure tree to
find guard settings -- the quarantine and the registry included -- and read C11's committed result
artifact, which compares against original values, with `git show`. Neither content now enters this
process. Both facts are established by COUNT-ONLY `git grep` (`-c`/`-l`): git reads the files in its
own process and returns file names and match counts, never a line of content.
"""
from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import c11r_common as C
import c11r_procs as PR

checks = []


def chk(n, name, ok, detail):
    checks.append({"id": f"B0_{n:02d}", "name": name, "pass": bool(ok), "detail": detail})


def main() -> int:
    # 1 -- on the C11R branch, which descends from the expected C11 HEAD
    branch = C.git("rev-parse", "--abbrev-ref", "HEAD")
    chk(1, "on the C11R branch", branch == "p5y-k5-tail-c11r-n9-statement-alignment",
        {"branch": branch})

    head = C.git("rev-parse", "HEAD")
    desc = C.git_ok("merge-base", "--is-ancestor", C.C11_HEAD, "HEAD")
    chk(2, "descends from the expected C11 HEAD 440bcd91", desc,
        {"expected_c11_head": C.C11_HEAD, "head": head})

    # 3 -- C11 published: the branch exists on origin at that HEAD
    ls = C.git_run(C.REPO, "ls-remote", "origin",
                   "refs/heads/p5y-k5-tail-c11-n9-independent-certifier", check=False).stdout.split()
    chk(3, "C11 is published on origin at 440bcd91", bool(ls) and ls[0] == C.C11_HEAD,
        {"remote_c11_ref": ls[0] if ls else None})

    # 4, 5 -- C11's own final verdict, established by COUNT-ONLY grep of its committed artifact:
    # the key occurs exactly once, and exactly once with the expected value. Content never enters.
    def count_at(commit, pattern, rel):
        out = C.git("grep", "-c", "-E", pattern, commit, "--", rel) if C.git_ok(
            "grep", "-q", "-E", pattern, commit, "--", rel) else ""
        return sum(int(ln.rsplit(":", 1)[1]) for ln in out.splitlines() if ln)

    r11_rel = "level4/closure_proofs/p5y_k5_tail_c11_n9_independent_certifier/evidence/n9/" \
              "C11_N9_RESULT.json"
    v_any = count_at(C.C11_HEAD, '"N9_VERDICT": ', r11_rel)
    v_inv = count_at(C.C11_HEAD, '"N9_VERDICT": "EXECUTION_INVALID"', r11_rel)
    s_any = count_at(C.C11_HEAD, '"N9_STATUS_AFTER_C11": ', r11_rel)
    s_open = count_at(C.C11_HEAD, '"N9_STATUS_AFTER_C11": "OPEN"', r11_rel)
    chk(4, "C11 verdict is EXECUTION_INVALID and is not rewritten as success",
        v_any == 1 and v_inv == 1,
        {"method": "count-only git grep at the C11 HEAD; no content read",
         "key_occurrences": v_any, "occurrences_with_EXECUTION_INVALID": v_inv})
    chk(5, "N9 is OPEN entering C11R", s_any == 1 and s_open == 1,
        {"method": "count-only git grep at the C11 HEAD; no content read",
         "key_occurrences": s_any, "occurrences_with_OPEN": s_open})

    # 6, 7 -- r5 authoritative, m=5 open set
    m5 = C.r5_open_by_verdict("5")
    r5 = C.r5_map()
    # 6 -- r5 is authoritative: its object id is unchanged since the C11 HEAD, and no coverage map
    # of a later revision exists anywhere in the tree. Round 3's version could not fail (review 3,
    # N-7): the map's `revision` field is null and the path constant contains "R5".
    import re as _re
    r5_head, r5_c11 = C.git_object_at("HEAD", C.R5_PATH), C.git_object_at(C.C11_HEAD, C.R5_PATH)
    maps = [f for f in C.git("ls-tree", "-r", "--name-only", "HEAD").splitlines()
            if _re.search(r"K5_COVERAGE_MAP_R(\d+)\.json$", f)]
    revs = sorted(int(_re.search(r"_R(\d+)\.json$", f).group(1)) for f in maps)
    chk(6, "r5 is the authoritative coverage map: unchanged since C11, and the latest revision",
        r5_head is not None and r5_head == r5_c11 and revs and max(revs) == 5,
        {"r5_object_at_HEAD": r5_head, "r5_object_at_C11_HEAD": r5_c11,
         "coverage_map_revisions_present": revs, "schema": r5.get("schema")})
    chk(7, "m=5 open set is exactly {306, 307, 308, 309}", tuple(m5) == C.OPEN_CELLS,
        {"open_m5": m5})

    # 8 -- no r6
    r6 = [f for f in C.git("ls-tree", "-r", "--name-only", "HEAD").splitlines()
          if "COVERAGE_MAP_R6" in f.rsplit("/", 1)[-1].upper()]
    chk(8, "no r6 coverage map exists", not r6, {"hits": r6})

    # 9 -- main untouched, LOCAL and REMOTE recorded SEPARATELY
    local_main = C.git("rev-parse", "refs/heads/main") if C.git_ok(
        "rev-parse", "--verify", "refs/heads/main") else None
    rm = C.git_run(C.REPO, "ls-remote", "origin", "refs/heads/main", check=False).stdout.split()
    remote_main = rm[0] if rm else None
    chk(9, "REMOTE main is untouched at the expected commit",
        remote_main == C.REMOTE_MAIN_EXPECTED,
        {"LOCAL_MAIN_REF": local_main, "REMOTE_MAIN_REF": remote_main,
         "expected_remote": C.REMOTE_MAIN_EXPECTED,
         "note": ("recorded separately on purpose: in a --no-local scratch clone `ls-remote origin` "
                  "reads the LOCAL repository, not GitHub. This runs from the primary checkout."),
         "divergence_is_known_and_not_reconciled_here": local_main != remote_main})

    # 10 -- guard DENY. A guard is a SETTING: a JSON key "guard" whose value is "ALLOW". The
    # pattern requires an UNESCAPED quote before the key, so prose quoting the phrase inside a JSON
    # string (where the quotes are escaped) is not a setting and does not match. Names only: git
    # reads the working tree in its own process; the protected files are excluded besides.
    guard_rx = r'(^|[^\\])"guard"[[:space:]]*:[[:space:]]*"[Aa][Ll][Ll][Oo][Ww]"'
    # The exclusions are EXACT paths from common.is_protected, as literal pathspecs. A `**/x/**`
    # exclusion is not what it looks like: without :(glob) magic git excluded all but one file,
    # which made the first version of this check vacuous. The scanned count below guards that.
    spec = "level4/closure_proofs/*.json"
    all_json = C.git("ls-files", "--cached", "--others", "--exclude-standard", "--",
                     spec).splitlines()
    protected = sorted(f for f in all_json if C.is_protected(f))
    excl = [f":(exclude,literal){f}" for f in protected]
    hits = C.git("grep", "--untracked", "-l", "-E", guard_rx, "--", spec,
                 *excl).splitlines() if C.git_ok("grep", "--untracked", "-q", "-E", guard_rx,
                                                 "--", spec, *excl) else []
    scanned = len(C.git("ls-files", "--cached", "--others", "--exclude-standard", "--", spec,
                        *excl).splitlines())
    coverage_ok = scanned == len(all_json) - len(protected) and scanned > 0
    # control: the same pattern, run by the same git, over two planted files outside the repo --
    # one real setting (must match) and one prose quotation inside a JSON string (must not)
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        (pathlib.Path(td) / "setting.json").write_text('{"x": {"guard": "ALLOW"}}\n')
        (pathlib.Path(td) / "prose.json").write_text(
            '{"note": "the phrase \\"guard\\": \\"ALLOW\\" is quoted prose"}\n')
        (pathlib.Path(td) / "deny.json").write_text('{"guard": "DENY"}\n')
        ctl = C.git_run(td, "grep", "--no-index", "-l", "-E", guard_rx, "--", ".",
                        check=False).stdout.split()
    guard_ctl = {"matched": sorted(ctl), "expected": ["setting.json"],
                 "pass": sorted(ctl) == ["setting.json"]}
    chk(10, "guard DENY: no ALLOW guard SETTING anywhere at C11R start",
        not hits and guard_ctl["pass"] and coverage_ok,
        {"allow_settings": hits, "json_files_scanned": scanned,
         "json_files_total": len(all_json), "protected_json_excluded": len(protected),
         "coverage_exact": coverage_ok,
         "method": ("names-only git grep for an unescaped \"guard\": \"ALLOW\" key/value over "
                    "every JSON file in the closure tree, tracked and untracked; protected files "
                    "excluded; no content enters this process"),
         "pattern_control": guard_ctl})

    # 11 -- C2..C11 integrity: nothing outside the C11R namespace has moved since C11 HEAD
    moved = [f for f in C.git("diff", "--name-only", f"{C.C11_HEAD}..HEAD").splitlines()
             if "p5y_k5_tail_c11r_n9_statement_alignment" not in f]
    chk(11, "C2-C11 integrity: no predecessor file modified", not moved, {"moved": moved})

    # 12 -- AWS untouched. Scanned by AST over IMPORTS and string literals, with THIS MODULE
    # EXCLUDED: a scanner that lists its own search terms matches itself and always fires.
    # (C10 lesson: exclude yourself from your own scans.)
    import ast as _ast
    self_name = pathlib.Path(__file__).name
    REMOTE = ("boto3", "botocore", "paramiko", "fabric", "aws", "ssh", "rebaseguard-aws",
              "rebaseguard-vultr")
    hits, scanned_mods = [], []
    for f in sorted((C.NS / "code").glob("*.py")):
        if f.name == self_name:
            continue
        scanned_mods.append(f.name)
        tree = _ast.parse(f.read_text())
        for n in _ast.walk(tree):
            if isinstance(n, _ast.Import):
                for a in n.names:
                    if a.name.split(".")[0].lower() in REMOTE:
                        hits.append(f"{f.name}: import {a.name}")
            elif isinstance(n, _ast.ImportFrom) and n.module:
                if n.module.split(".")[0].lower() in REMOTE:
                    hits.append(f"{f.name}: from {n.module}")
            elif isinstance(n, _ast.Constant) and isinstance(n.value, str):
                low = n.value.lower()
                if any(t in low for t in ("boto3", "paramiko", "rebaseguard-aws",
                                          "rebaseguard-vultr")) or low.startswith("ssh "):
                    hits.append(f"{f.name}: literal {n.value[:40]!r}")
    chk(12, "AWS untouched: no AWS, SSH or remote-worker surface in C11R code", not hits,
        {"hits": hits, "modules_scanned": scanned_mods, "self_excluded": self_name,
         "policy": "AWS IS FORBIDDEN for this campaign; local execution only"})

    # supporting record: the toolchain the ORIGINAL certifier needs must remain absent, which is
    # what makes an accidental import of it fail loudly rather than silently succeed.
    tc = C.toolchain_present()
    chk(13, "the original certifier's backend is absent, so accidental reuse cannot run",
        not tc["numpy"] and not tc["flint"], {"importlib_find_spec": tc})

    procs = PR.campaign_workers()
    chk(14, "no campaign worker is running (detector revision 2, framework Python included)",
        not procs["workers"],
        {"workers": procs["workers"], "foreign_python": procs["foreign_python"],
         "interpreters_seen": procs["interpreters_seen"], "mechanism": procs["mechanism"]})

    failed = [c["id"] for c in checks if not c["pass"]]
    out = {"schema": "C11R_B0/1",
           "campaign": "C11R -- N9 statement-alignment repair",
           "purpose": ("determine whether the already-independent C11 certifier can certify THE "
                       "SAME STATEMENT N9 requires: block-uniform drift over the frozen e-block, "
                       "and the six operator constants for cell 306"),
           "predecessor": {"branch": "p5y-k5-tail-c11-n9-independent-certifier",
                           "head": C.C11_HEAD,
                           "verdict": "EXECUTION_INVALID" if v_inv == 1 else "UNCONFIRMED",
                           "n9_status": "OPEN" if s_open == 1 else "UNCONFIRMED",
                           "preserved_invalid": True},
           "LOCAL_MAIN_REF": local_main, "REMOTE_MAIN_REF": remote_main,
           "checks": checks, "failed": failed,
           "B0_CLASS": "PASS" if not failed else "REFUSE"}
    s = C.write_evidence(C.NS / "evidence" / "b0" / "C11R_B0.json", out, producer=__file__)
    for c in checks:
        print(f"  {'PASS' if c['pass'] else 'FAIL'}  {c['id']}  {c['name']}")
    print(f"\nB0_CLASS = {out['B0_CLASS']}   checks={len(checks)}  failed={failed}")
    print(f"LOCAL_MAIN_REF  = {local_main}")
    print(f"REMOTE_MAIN_REF = {remote_main}")
    print(f"wrote evidence/b0/C11R_B0.json sha256 {s[:16]}...")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
