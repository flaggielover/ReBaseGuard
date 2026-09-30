"""Positive and negative controls for the narrow scanner allowance (owner rulings 2, "QUARANTINE SCANNER").

  python3 tests/test_p309_scan_allowance.py   -> evidence/fc2/SCAN_ALLOWANCE_CONTROLS.json; exit 0 iff all pass

Each negative control plants one defect into a temporary copy of the guard source (or into a temporary scan root)
and requires the allowance to be refused or a formal finding to fire.  The genuine guard must pass.  Nothing is
executed from the scanned sources.
"""
from __future__ import annotations

import ast
import datetime
import hashlib
import json
import shutil
import sys
import tempfile
from pathlib import Path

FNS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(FNS / "code"))
import p309_scan as S  # noqa: E402

GUARD = (FNS / "code" / "p309_guard.py").read_text()
LIT, CONST = S.LIT, S.CONST
DEF_LINE = next(l for l in GUARD.splitlines() if l.startswith(CONST + " = "))


def refused(src: str) -> bool:
    return bool(S.allowance_check(ast.parse(src)))


def kinds(src: str, rel: str = "code/p309_guard.py") -> set:
    return {f["kind"] for f in S.formal_rules(ast.parse(src), rel)}


def planted(old: str, new: str) -> str:
    assert GUARD.count(old) == 1, old
    return GUARD.replace(old, new)


def full_scan(files: dict) -> dict:
    """a temporary scan root: the given files plus both planted controls and the allowance config."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        for rel in ("tests/planted_control_p309.py", "tests/planted_control_p309_formal.py",
                    "config/SCANNER_ALLOWANCE_P309.json"):
            (root / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(FNS / rel, root / rel)
        for rel, src in files.items():
            (root / rel).parent.mkdir(parents=True, exist_ok=True)
            (root / rel).write_text(src)
        return S.scan(root)


def run() -> dict:
    R = {}
    tail = "\n\ndef _planted():\n    return {}\n"
    R["genuine_guard_allowance_holds"] = not refused(GUARD) and not kinds(GUARD)
    R["genuine_full_scan_pass"] = full_scan({"code/p309_guard.py": GUARD})["verdict"] == "PASS"
    R["C1_second_literal_occurrence"] = refused(GUARD + tail.format('"' + LIT + '"'))
    R["C2_literal_outside_the_assignment"] = refused(planted(DEF_LINE, CONST + ' = "refs/x"') +
                                                     tail.format('"' + LIT + '"'))
    R["C3_rebinding"] = refused(GUARD + f"\n{CONST} = 'refs/p309-test/x'\n")
    mut = GUARD + f"\n\ndef _arm(repo):\n    return _git(repo, 'update-ref', {CONST}, 'HEAD')\n"
    R["C4_update_ref_with_constant"] = refused(mut) and "MARKER_MUTATION" in kinds(mut)
    push = GUARD + "\n\ndef _p(repo):\n    return _git(repo, 'push', 'origin', '" + LIT + "')\n"
    R["C5_push_with_literal"] = refused(push) and "MARKER_MUTATION" in kinds(push)
    ns = GUARD + "\n\ndef _d(repo):\n    return _git(repo, 'update-ref', '-d', _PROD_NAMESPACE + 'x')\n"
    R["C5b_delete_in_namespace"] = "MARKER_MUTATION" in kinds(ns)
    res = full_scan({"code/other_unlisted.py": GUARD})
    R["C6_unlisted_file"] = res["verdict"] == "FAIL" and any(f["file"] == "code/other_unlisted.py"
                                                             for f in res["findings"])
    gw = GUARD + "\n\ndef _w():\n    Path(_PROD_GRANT_PATH).write_text('{}')\n"
    R["C7_grant_write"] = "GRANT_WRITE" in kinds(gw)
    gw2 = GUARD + "\n\ndef _w2(repo):\n    return _git(repo, 'add', 'authorization/P309_GRANT.json')\n"
    R["C7b_git_add_grant"] = "GRANT_WRITE" in kinds(gw2)
    al = GUARD + f"\n_m = {CONST}\n"
    R["C8_alias_outside_class_attr"] = "MARKER_ALIAS" in kinds(al)
    rb = "import p309_guard as G\nG.PRODUCTION_MARKER = G.TEST_MARKER\n"
    R["C9_attribute_rebind_elsewhere"] = "MARKER_REBIND" in kinds(rb, "tests/x.py")
    rt = '"""q309: refusal-test"""\nX = "' + LIT + '"\n'
    res = full_scan({"code/p309_guard.py": GUARD, "tests/test_refusal_x.py": rt})
    R["C10_refusal_test_mark_does_not_cover_literal"] = res["verdict"] == "FAIL"
    res = full_scan({"code/p309_guard.py": GUARD})
    R["C11_formal_planted_control_fires_all"] = res["formal_controls_fire_all_kinds"]
    R["C12_allowed_findings_are_listed"] = len(res["allowed_marker_name"]) == len(S.NAMES)
    # the pending-result NAME: allowed only in the guard
    pend = [n for n in S.NAMES if n["constant"] == "PENDING_REF"][0]["literal"]
    res = full_scan({"code/p309_guard.py": GUARD, "code/p309_driver_x.py": 'P = "' + pend + '"\n'})
    R["C13_pending_literal_outside_guard"] = res["verdict"] == "FAIL"
    # exactly-once sites: an unlisted ref mutation through a context attribute is a finding ...
    site_src = ("def _arm_marker(ctx, c):\n    _assert_execute_context(ctx)\n"
                "    return git('update-ref', ctx.marker_ref, c, '0' * 40)\n")
    R["C14_unlisted_site_is_a_finding"] = "MARKER_MUTATION" in kinds(site_src, "code/p309_driver.py")
    # ... a listed site (file, function, ast sha) is sanctioned, and any change to its body is a finding again
    import hashlib as _h
    fn = next(n for n in ast.walk(ast.parse(site_src)) if isinstance(n, ast.FunctionDef))
    saved = list(S.SITES)
    S.SITES[:] = [{"file": "code/p309_driver.py", "function": "_arm_marker",
                   "ast_sha256": _h.sha256(ast.dump(fn).encode()).hexdigest()}]
    try:
        hits: list = []
        ok_listed = not S.formal_rules(ast.parse(site_src), "code/p309_driver.py", hits) and len(hits) == 1
        changed = site_src.replace("'0' * 40", "'HEAD'")
        R["C15_listed_site_sanctioned_changed_body_refused"] = ok_listed and "MARKER_MUTATION" in kinds(
            changed, "code/p309_driver.py")
    finally:
        S.SITES[:] = saved
    return R


if __name__ == "__main__":
    import p309_env as E
    E.log("tests/test_p309_scan_allowance.py", "scanner allowance controls (static; temporary copies)",
          klass="GOVERNANCE", notes="static analysis only; nothing from the scanned sources is executed")
    r = run()
    ok = all(r.values())
    out = {"utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
           "scan_sha256": hashlib.sha256((FNS / "code" / "p309_scan.py").read_bytes()).hexdigest(),
           "test_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), "all_pass": ok, "results": r}
    (E.evidence_dir("fc2") / "SCAN_ALLOWANCE_CONTROLS.json").write_text(json.dumps(out, indent=1,
                                                                                      sort_keys=True) + "\n")
    for k, v in r.items():
        print(f"[{'PASS' if v else 'FAIL'}] {k}")
    sys.exit(0 if ok else 1)
