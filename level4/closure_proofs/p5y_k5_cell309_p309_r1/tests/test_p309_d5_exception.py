"""Owner D5 exception controls: the ratified production mutation sites may EXIST, and nothing else may move a ref.

  python3 -I -S -B tests/test_p309_d5_exception.py   -> evidence/fc2/D5_EXCEPTION_CONTROLS.json; exit 0 iff all pass

The owner's D5 decision (governance/OWNER_D5_RATIFICATION_P309_VERBATIM.md) requires the scanner to keep rejecting:
  (1) any additional production marker mutation site;       (2) any additional pending-ref mutation site;
  (3) any unreviewed ref mutation path;                      (4) any dynamically constructed equivalent;
  (5) any mutation reachable without execute mode;           (6) any mutation reachable without a valid owner grant;
  (7) any qualification/test path capable of mutating the production refs.
Each static control plants one violation into a temporary copy of the namespace's code/config/tests/verify and requires
the formal scan (code/p309_scan.py) and/or the static check (code/p309_static_check.py, T4/T6/T7/T8) to reject it.  R4
follow-up (reviews/REVIEW_PREFREEZE_R4_FOLLOWUP_P309.md): R4's mutants M01-M15 are controls here (each must be rejected),
with further controls for the process allowlist (F1(b)), the hardened T7 (F1(c)) and the backstop's structure (T8).
The RUNTIME backstop controls (F1(a)) are in tests/test_p309_site_backstop.py.  The genuine copy must pass (positive
control).  Nothing is executed from the planted sources, no production ref is created anywhere, and nothing is
evaluated.  Forbidden function names are assembled from pieces at run time (QC12 T7 forbids them as strings here).
"""
from __future__ import annotations

import datetime
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

FNS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(FNS / "code"))
import p309_driver as D  # noqa: E402
import p309_scan as S  # noqa: E402
import p309_static_check as SC  # noqa: E402

G = D.G
DRIVER = "code/p309_driver.py"
SCRATCH = Path("/tmp/claude-0/-home-user-ReBaseGuard/ea54e9f6-e828-5447-be15-220ef2c329fd/scratchpad/d5_controls")


def copy_tree() -> Path:
    root = Path(tempfile.mkdtemp(prefix="d5ctl", dir=SCRATCH))
    for d in ("code", "config", "tests", "verify"):
        shutil.copytree(FNS / d, root / d, ignore=shutil.ignore_patterns("__pycache__"))
    return root


def planted(edits: dict) -> tuple:
    """edits: {rel: (old, new)} replaces once; {rel: ("+", text)} appends; {rel: ("new", text)} creates."""
    root = copy_tree()
    for rel, (old, new) in edits.items():
        p = root / rel
        if old in ("new", "new+x"):
            p.write_text(new)
            if old == "new+x":
                p.chmod(0o755)
        elif old == "+":
            p.write_text(p.read_text() + "\n" + new)
        else:
            src = p.read_text()
            assert src.count(old) == 1, (rel, old[:60])
            p.write_text(src.replace(old, new))
    scan = S.scan(root)
    static = SC.run(root)
    shutil.rmtree(root)
    return scan, static


def kinds(scan: dict) -> set:
    return {f["kind"] for f in scan["findings"]}


def static_fail(static: dict, test: str) -> bool:
    return not static[test]["pass"]


# pieces only, cut at run time from the configured tokens: this file never holds a production ref-name token
_NS, _LEAF = S.TOKENS[0] + "/", S.TOKENS[1]
# the driver names QC12 T7 forbids in tests, assembled from pieces (the controls plant them into temporary copies)
ARM, PEND, AEC = "_arm" + "_marker", "_persist" + "_pending", "_assert_execute" + "_context"
PCTX, MODE, AFTER = "production" + "_context", "_MO" + "DE", "after" + "_marker"
SCODES, BACKSTOP, NONCE = "_SITE" + "_CODES", "_site" + "_backstop", "_require_own" + "_run_nonce"
NS_A, NS_B = _NS[:len(_NS) // 2], _NS[len(_NS) // 2:]
LEAF_A, LEAF_B = _LEAF[:len(_LEAF) // 2], _LEAF[len(_LEAF) // 2:]


def run() -> dict:
    R = {}

    def t(name, cond, detail=""):
        R[name] = {"pass": bool(cond), "detail": str(detail)[:300]}
    T7 = "T7_no_production_execution_from_tests_or_qualification"

    # positive control: the genuine tree
    scan, static = planted({})
    t("P0_genuine_tree_scan_pass", scan["verdict"] == "PASS", kinds(scan))
    t("P0b_genuine_tree_static_pass", all(v["pass"] for v in static.values()),
      {k: v["detail"] for k, v in static.items() if not v["pass"]})
    t("P0c_exactly_two_sanctioned_sites", sorted(x["function"] for x in scan["sanctioned_exactly_once_sites"]) ==
      [ARM, PEND], scan["sanctioned_exactly_once_sites"])
    t("P0d_formal_control_fires_every_process_kind", scan["formal_controls_fire_all_kinds"],
      scan["formal_planted_controls"])

    # (1) / (2) additional production mutation sites
    scan, _ = planted({DRIVER: ("+", f"def _arm_again(ctx, gc):\n    {AEC}(ctx)\n"
                                     "    git('update-ref', ctx.marker_ref, gc, '0' * 40, repo=ctx.repo)\n")})
    t("C01_additional_marker_site", "MARKER_MUTATION" in kinds(scan), kinds(scan))
    scan, _ = planted({DRIVER: ("+", f"def _pend_again(ctx, b):\n    {AEC}(ctx)\n"
                                     "    git('update-ref', ctx.pending_ref, b, '0' * 40, repo=ctx.repo)\n")})
    t("C02_additional_pending_site", "MARKER_MUTATION" in kinds(scan), kinds(scan))
    src = (FNS / DRIVER).read_text()
    i = src.index(f"def {ARM}(")
    arm = src[i:src.index("\n\n\n", i)]
    scan, _ = planted({DRIVER: ("+", arm + "\n")})                      # a second def of the same name
    t("C03_duplicate_named_site", "MARKER_MUTATION" in kinds(scan) and len(scan["sanctioned_exactly_once_sites"]) < 2,
      kinds(scan))
    scan, _ = planted({"code/p309_other.py": ("new", f"from p309_driver import git, {AEC}\n\n\n" + arm + "\n")})
    t("C04_identical_site_in_another_file", "MARKER_MUTATION" in kinds(scan), kinds(scan))

    # (3) unreviewed ref mutation paths
    scan, _ = planted({DRIVER: ("+", "def _move(repo):\n    git('update-ref', 'refs/heads/x', 'HEAD', repo=repo)\n")})
    t("C05_unlisted_ref_mutation_non_production", "REF_MUTATION_UNLISTED" in kinds(scan), kinds(scan))
    scan, _ = planted({DRIVER: ('git("update-ref", ctx.branch_ref, cid, head, repo=ctx.repo)',
                                'git("update-ref", ctx.branch_ref + "", cid, head, repo=ctx.repo)')})
    t("C06_listed_function_changed", "REF_MUTATION_UNLISTED" in kinds(scan), kinds(scan))
    for verb in ("symbolic-ref", "push", "tag", "branch", "reset", "commit", "fast-import", "config", "gc",
                 "an-unknown-verb"):
        scan, _ = planted({"code/p309_rehearse.py": ("+", f"def _v(repo):\n    return D.git('{verb}', 'x', 'y', "
                                                          "repo=repo)\n")})
        t(f"C07_unlisted_{verb}", "REF_MUTATION_UNLISTED" in kinds(scan), kinds(scan))
    scan, _ = planted({"code/p309_rehearse.py": ("+", "def _v(repo):\n    return D.git('symbolic-ref', 'x', repo=repo)\n")})
    t("C07b_symbolic_ref_read_form_allowed", scan["verdict"] == "PASS", kinds(scan))
    scan, _ = planted({"code/p309_rehearse.py": ("+", "def _v(repo):\n    return D.git('hash-object', '-w', 'x', "
                                                      "repo=repo)\n")})
    t("C07c_object_write_unlisted", "GIT_WRITE_UNLISTED" in kinds(scan), kinds(scan))
    scan, _ = planted({DRIVER: ("+", "def _raw(gd):\n    open(gd / 'refs' / 'heads' / 'x', 'w').write('0' * 40)\n")})
    t("C08_ref_file_write", "REF_FILE_WRITE" in kinds(scan), kinds(scan))
    scan, _ = planted({DRIVER: ("+", "def _raw2(gd):\n    os.makedirs(str(gd) + '/refs/p309')\n")})
    t("C08b_ref_dir_create", "REF_FILE_WRITE" in kinds(scan), kinds(scan))
    scan, _ = planted({DRIVER: ("+", "def _raw3(ctx):\n    (git_dir(ctx) / 'x').write_text('y')\n")})
    t("C08c_git_dir_write", "GITDIR_WRITE" in kinds(scan), kinds(scan))
    scan, _ = planted({DRIVER: ("+", "def _raw4(gd):\n    (Path(gd) / 'HEAD').write_text('ref: refs/heads/x')\n")})
    t("C08d_head_file_write", "REF_FILE_WRITE" in kinds(scan), kinds(scan))
    scan, _ = planted({"tests/test_p309_exactly_once.py": ("+", "def _evil_subprocess(repo):\n"
                                                               "    subprocess.run(['git', '-C', str(repo), 'update-ref', "
                                                               "'refs/heads/y', 'HEAD'])\n")})
    t("C09_subprocess_git_ref_mutation", "REF_MUTATION_UNLISTED" in kinds(scan), kinds(scan))

    # (4) dynamically constructed equivalents
    dyn = (f"def _dyn(ctx, g):\n    ns = '{NS_A}' + '{NS_B}'\n    name = ns + '{LEAF_A}' + '{LEAF_B}'\n"
           f"    git('update-ref', name, g, repo=ctx.repo)\n")
    scan, _ = planted({DRIVER: ("+", dyn)})
    t("C10_dynamic_name_from_pieces", "REF_MUTATION_UNLISTED" in kinds(scan), kinds(scan))
    scan, _ = planted({DRIVER: ("+", "def _ga(g):\n    name = getattr(G, 'PRODUCTION_' + 'MARKER')\n"
                                     "    git('update-ref', name, g)\n")})
    t("C11_getattr_constructed", "REF_MUTATION_UNLISTED" in kinds(scan), kinds(scan))
    scan, _ = planted({DRIVER: ("+", "def _tup(ctx, g):\n    a, b = ctx.marker_ref, 1\n    git('update-ref', a, g)\n")})
    t("C12_alias_through_tuple", "MARKER_MUTATION" in kinds(scan), kinds(scan))
    scan, _ = planted({DRIVER: ("+", "def _nm(ctx):\n    return ctx.pending_ref\n\n\ndef _via(ctx, g):\n"
                                     "    r = _nm(ctx)\n    git('update-ref', r, g)\n")})
    t("C13_alias_through_return", "MARKER_MUTATION" in kinds(scan), kinds(scan))
    scan, _ = planted({DRIVER: ("+", "def _mv(r, g):\n    git('update-ref', r, g)\n\n\ndef _call(g):\n"
                                     "    _mv(G.PRODUCTION.marker_ref, g)\n")})
    t("C14_alias_through_parameter", "MARKER_MUTATION" in kinds(scan), kinds(scan))
    scan, _ = planted({DRIVER: ("+", "def _fs(ctx, g):\n    ref = f'{ctx.marker_ref}'\n    git('update-ref', ref, g)\n")})
    t("C15_alias_through_fstring", "MARKER_MUTATION" in kinds(scan), kinds(scan))
    scan, _ = planted({DRIVER: ("+", f"TOK = '{NS_A}{NS_B}' + 'elsewhere'\n")})
    t("C16_production_token_outside_definitions", "MARKER_TOKEN" in kinds(scan), kinds(scan))
    scan, _ = planted({DRIVER: ("+", "def _gw(ctx):\n    p = ctx.guard_ctx.grant_path\n    Path(p).write_text('{}')\n")})
    t("C17_grant_path_alias_write", "GRANT_WRITE" in kinds(scan), kinds(scan))
    mark = S.Q.CONTROL_MARK
    scan, _ = planted({"tests/test_planted_mark.py": ("new", f'"""{mark}"""\nimport p309_guard as G\n'
                                                             "G.PRODUCTION_MARKER = 'x'\n")})
    t("C18_control_mark_cannot_exempt_a_file", "CONTROL_MARK_UNLISTED" in kinds(scan) and scan["verdict"] == "FAIL",
      kinds(scan))

    # (5) mutation reachable without execute mode
    scan, static = planted({DRIVER: (f"def {ARM}(ctx: ExecContext, grant_commit: str) -> None:\n    {AEC}(ctx)\n",
                                     f"def {ARM}(ctx: ExecContext, grant_commit: str) -> None:\n")})
    t("C19_site_without_execute_assertion", "MARKER_MUTATION" in kinds(scan) and static_fail(static, "T4_exactly_once_sites"),
      (kinds(scan), static["T4_exactly_once_sites"]["detail"]))
    scan, static = planted({DRIVER: ('    st = stage1a("decoy", cell, {"h": d["h"], "k": d["k"]}, verifier_id, workers=workers)',
                                     f'    {ARM}({PCTX}(), "0" * 40)\n'
                                     '    st = stage1a("decoy", cell, {"h": d["h"], "k": d["k"]}, verifier_id, workers=workers)')})
    t("C20_site_called_from_a_qualification_mode",
      static_fail(static, "T4_exactly_once_sites") and static_fail(static, "T1_no_path_from_qualification_modes_to_target"),
      static["T4_exactly_once_sites"]["detail"])

    # (6) mutation reachable without a valid owner grant
    scan, static = planted({DRIVER: ("    check_flags()\n    check_branch(ctx)\n    check_not_evaluated(ctx)\n",
                                     f"    check_flags()\n    {ARM}(ctx, 'x')\n    check_branch(ctx)\n"
                                     "    check_not_evaluated(ctx)\n")})
    t("C21_marker_before_check_grant", static_fail(static, "T6_mutation_dominated_by_the_grant"),
      static["T6_mutation_dominated_by_the_grant"]["detail"])
    scan, static = planted({DRIVER: ("    admission = premarker_admission(ctx, g, m, cell)      # R4 B3: includes grant "
                                     "cell_interval == cell and Ew\n",
                                     "    admission = {}\n")})
    t("C22_dry_admission_removed", static_fail(static, "T6_mutation_dominated_by_the_grant"),
      static["T6_mutation_dominated_by_the_grant"]["detail"])
    scan, static = planted({DRIVER: ('        if not marker:\n            raise Refusal("SEAL_ONLY", "emergency evidence without a '
                                     'marker: nothing is persisted")\n', "")})
    t("C23_seal_only_marker_gate_removed", static_fail(static, "T6_mutation_dominated_by_the_grant"),
      static["T6_mutation_dominated_by_the_grant"]["detail"])
    scan, static = planted({DRIVER: ('    if (ctx is None or ctx.kind != "SANDBOX") and any(', '    if False and any(')})
    t("C24_hooks_allowed_in_production", static_fail(static, "T6_mutation_dominated_by_the_grant"),
      static["T6_mutation_dominated_by_the_grant"]["detail"])
    scan, static = planted({DRIVER: (f"        {ARM}(ctx, grant[\"grant_commit\"])\n",
                                     f"        if grant:\n            {ARM}(ctx, grant[\"grant_commit\"])\n")})
    t("C25_marker_inside_a_branch", static_fail(static, "T6_mutation_dominated_by_the_grant"),
      static["T6_mutation_dominated_by_the_grant"]["detail"])
    # the runtime backstop's structure (T8); its behaviour: tests/test_p309_site_backstop.py
    T8 = "T8_runtime_backstop_at_the_sites"
    for nm, old, new in (
            ("site_check_removed", f"    site = {SCODES}.get(sys._getframe(1).f_code)\n    if site is None:\n",
             f"    site = {SCODES}.get(sys._getframe(1).f_code) or 'arm'\n    if site is None:\n"),
            ("backstop_call_removed", f"    {BACKSTOP}(ctx, site)\n\n\n", "\n\n"),
            ("arm_grant_check_removed", "        ok, why = G.premarker_check(ctx.guard_ctx)\n",
             "        ok, why = True, ''\n"),
            ("arm_nonce_removed", f"        {NONCE}(ctx)\n        return\n", "        return\n"),
            ("pending_marker_check_removed", "    if not marker:\n        raise Refusal(\"NO_MARKER\"",
             "    if False:\n        raise Refusal(\"NO_MARKER\""),
            ("nonce_pid_check_removed", "rec[\"pid\"] != os.getpid()", "False"),
            ("third_site_code", f"{PEND}.__code__: \"pending\"}}",
             f"{PEND}.__code__: \"pending\", persist_emergency.__code__: \"pending\"}}")):
        scan, static = planted({DRIVER: (old, new)})
        t(f"C25b_backstop_{nm}", static_fail(static, T8), static[T8]["detail"])

    # (7) qualification / test paths
    for nm, body in (("production_ctx", f"D.{PCTX}()"),
                     ("execute_without_context", "D.run_execute('0' * 64)"),
                     ("execute_with_none", "D.run_execute('0' * 64, ctx=None)"),
                     ("seal_only_without_context", "D.run_seal_only()"),
                     ("site_call", f"D.{ARM}(None, '0')"),
                     ("exec_context", "D.ExecContext('PRODUCTION', D.REPO, D.G.PRODUCTION, 'a', 'b', 'c', None)"),
                     ("driver_cli_execute", "subprocess.run([sys.executable, 'code/p309_driver.py', 'execute'])"),
                     ("driver_cli_seal_only", "subprocess.run([sys.executable, str(FNS / 'code' / 'p309_driver.py'), "
                                              "'seal-only'])"),
                     ("mode_store", f"D.{MODE}['mode'] = 'execute'"),
                     ("module_dict", f"D.__dict__['{PEND[:9]}' + '{PEND[9:]}'](None, b'')"),
                     ("getattr_driver", f"getattr(D, '{ARM[:4]}' + '{ARM[4:]}')(None, '0')"),
                     ("vars_driver", "vars(D)"),
                     ("production_reference", "c = D.G.PRODUCTION"),
                     ("driver_attribute_store", "D.check_grant = lambda *a: {}"),
                     ("guard_attribute_store", "D.G.premarker_check = lambda *a: (True, '')"),
                     ("sys_modules", "sys.modules['p309_driver']"),
                     ("python_c_execute", f"subprocess.run([sys.executable, '-c', 'import p309_driver as D; "
                                          f"D.{MODE}.clear()'])"),
                     ("string_name", f"x = 'D.{ARM}'")):
        scan, static = planted({"tests/test_evil.py": ("new", f"import subprocess, sys\nimport p309_driver as D\n\n\n"
                                                              f"def evil():\n    {body}\n")})
        t(f"C26_test_path_{nm}", static_fail(static, T7), static[T7]["detail"])
    scan, static = planted({"tests/test_evil.py": ("new", f"from p309_driver import {ARM} as arm\n\n\ndef evil(c, g):\n"
                                                          "    arm(c, g)\n")})
    t("C26_test_path_import_from_alias", static_fail(static, T7), static[T7]["detail"])
    scan, static = planted({"tests/test_evil.py": ("new", "from p309_guard import PRODUCTION as P\n")})
    t("C26_test_path_import_production", static_fail(static, T7), static[T7]["detail"])
    scan, _ = planted({"tests/test_evil2.py": ("new", "import p309_guard as G\n\n\ndef sh(*a):\n    pass\n\n\n"
                                                      "def evil(repo):\n    sh(repo, 'update-ref', G.PRODUCTION_MARKER, "
                                                      "'HEAD')\n")})
    t("C27_test_mutates_the_production_marker", "MARKER_MUTATION" in kinds(scan), kinds(scan))
    ex = next(e for e in S.ALLOW["t7_exemptions"] if e["file"] == "tests/test_p309_guard.py")
    scan, static = planted({"tests/test_p309_guard.py": ("+", f"def _evil():\n    D.{MODE}['mode'] = 'execute'\n")})
    t("C28_t7_exemption_is_hash_bound", static_fail(static, T7) and ex["rules"] != [], static[T7]["detail"])

    # R4 follow-up F1: R4's mutants M01-M15 (reviews/R4_FOLLOWUP_D5_MUTANTS.py.txt), each must be rejected
    lit = _NS + _LEAF
    M = {
        "M01_file_named_q309_guard_in_FNS": {"code/q309_guard.py": ("new", "import subprocess\n\ndef arm(repo, g):\n"
                                             "    subprocess.run(['git', '-C', repo, 'update-ref', " + repr(lit) + ", g])\n")},
        "M02_os_system_shell_string_production": {DRIVER: ("+", "def _m02(ctx, g):\n    os.system('git update-ref ' + "
                                                                "G.PRODUCTION_MARKER + ' ' + g)\n")},
        "M03_shell_true_string": {"code/p309_rehearse.py": ("+", "def _m03(repo):\n    import subprocess\n    subprocess.run("
                                  "'git -C ' + str(repo) + ' update-ref refs/heads/x HEAD', shell=True)\n")},
        "M04_dynamic_verb_production": {DRIVER: ("+", "def _m04(ctx, g):\n    verb = 'update-' + 'ref'\n"
                                                      "    git(verb, ctx.marker_ref, g, '0' * 40, repo=ctx.repo)\n")},
        "M05_starred_args_pending": {DRIVER: ("+", "def _m05(ctx, b):\n    r = ctx.pending_ref\n    args = ['update-ref', "
                                                   "r, b]\n    git(*args, repo=ctx.repo)\n")},
        "M06_git_config_alias_production": {DRIVER: ("+", "def _m06(ctx, g):\n    git('-c', 'alias.u=update-ref', 'u', "
                                                          "ctx.marker_ref, g, '0' * 40, repo=ctx.repo)\n")},
        "M07_ref_file_dynamic_path": {DRIVER: ("+", "def _m07(gd):\n    p = Path(str(gd)) / ('re' + 'fs') / 'heads' / 'x'\n"
                                                    "    p.write_text('0' * 40)\n")},
        "M08_packed_refs_append_dynamic": {DRIVER: ("+", "def _m08(gd):\n    with open(str(gd) + '/packed' + '-refs', "
                                                         "'a') as fh:\n        fh.write('x')\n")},
        "M09_aliased_runner": {"code/p309_rehearse.py": ("+", "def _m09():\n    import subprocess\n    r = subprocess.run\n"
                                                              "    r(['git', 'update-ref', 'refs/heads/x', 'HEAD'])\n")},
        "M10_getattr_runner": {"code/p309_rehearse.py": ("+", "def _m10():\n    import subprocess\n    getattr(subprocess, "
                                                              "'run')(['git', 'update-ref', 'refs/heads/x', 'HEAD'])\n")},
        "M11_os_execvp": {"code/p309_rehearse.py": ("+", "def _m11():\n    import os\n    os.execvp('git', ['git', "
                                                         "'update-ref', 'refs/heads/x', 'HEAD'])\n")},
        "M12_getoutput_shell": {"code/p309_rehearse.py": ("+", "def _m12():\n    import subprocess\n    subprocess.getoutput("
                                                               "'git update-ref refs/heads/x HEAD')\n")},
        "M13_test_imports_site_under_alias": {"tests/test_m13.py": ("new",
            f"import types\nimport p309_driver as D\nfrom p309_driver import {ARM} as arm\n\n\ndef evil(g):\n"
            f"    D.{MODE}['mode'] = 'execute'\n"
            "    c = types.SimpleNamespace(kind='PRODUCTION', guard_ctx=D.G.PRODUCTION, marker_ref=D.G.PRODUCTION.marker_ref,\n"
            "                              pending_ref=D.G.PRODUCTION.pending_ref, repo=D.REPO)\n    arm(c, g)\n")},
        "M14_test_site_via_module_dict": {"tests/test_m14.py": ("new",
            f"import types\nimport p309_driver as D\n\n\ndef evil(data):\n    D.{MODE}['mode'] = 'seal-only'\n"
            "    c = types.SimpleNamespace(kind='PRODUCTION', guard_ctx=D.G.PRODUCTION, marker_ref=D.G.PRODUCTION.marker_ref,\n"
            "                              pending_ref=D.G.PRODUCTION.pending_ref, repo=D.REPO)\n"
            f"    D.__dict__['{PEND[:9]}' + '{PEND[9:]}'](c, data)\n")},
        "M15_shell_script_invoked": {"code/arm.sh": ("new", "git update-ref \"$1\" \"$2\"\n"),
                                     "code/p309_rehearse.py": ("+", "def _m15(ref, g):\n    import subprocess\n"
                                                                    "    subprocess.run(['bash', 'code/arm.sh', ref, g])\n")},
    }
    for name, edits in M.items():
        scan, static = planted(edits)
        failed = sorted(k for k, v in static.items() if not v["pass"])
        t(name, scan["verdict"] == "FAIL" or failed, (sorted(kinds(scan)), failed))
    # further process-allowlist controls
    for nm, edits, want in (
            ("executable_file", {"code/tool.py": ("new+x", "x = 1\n")}, "EXEC_BIT"),
            ("non_python_file", {"verify/data.bin": ("new", "x")}, "NONPY_FILE"),
            ("shadow_research_module", {"verify/srk_gate.py": ("new", "x = 1\n")}, "SHADOW_MODULE"),
            ("runner_used_as_value", {"code/p309_rehearse.py": ("+", "def _r():\n    return map(D.git, ['status'])\n")},
             "RUNNER_ALIAS"),
            ("unregistered_wrapper", {"code/p309_rehearse.py": ("+", "def _w(*a):\n    import subprocess\n"
                                                                     "    subprocess.run(['git', *a])\n")},
             "GIT_CALL_OPAQUE"),
            ("python_c_code_scanned", {"code/p309_rehearse.py": ("+", "def _p():\n    import subprocess, sys\n"
                                                                      "    subprocess.run([sys.executable, '-c', 'import os; "
                                                                      "os.system(\"git update-ref refs/heads/x HEAD\")'])\n")},
             "PROCESS_FORBIDDEN"),
            ("forbidden_git_option_after_verb", {"code/p309_rehearse.py": ("+", "def _o(repo):\n    return D.git('log', "
                                                                               "'--output=/tmp/x', repo=repo)\n")},
             "GIT_OPTION_FORBIDDEN"),
            ("dynamic_import", {"code/p309_rehearse.py": ("+", "def _i(n):\n    return __import__(n)\n")}, "DYNAMIC_IMPORT"),
            ("process_module_alias", {"code/p309_rehearse.py": ("+", "import subprocess as sp\nX = sp\n")}, "PROCESS_ALIAS"),
            ("listed_runner_changed", {"code/p309_guard.py": ('    return subprocess.run(["git", "-C", str(repo), *args], '
                                                              'capture_output=True, env=env).returncode == 0',
                                                              '    return subprocess.run(["git", "-C", str(repo), *args, '
                                                              '"x"], capture_output=True, env=env).returncode == 0')},
             "RUNNER_UNREVIEWED")):
        scan, _ = planted(edits)
        t(f"C29_{nm}", want in kinds(scan), kinds(scan))
    own = subprocess.run(["git", "-C", str(D.REPO), "for-each-ref", "--format=%(refname)"], capture_output=True,
                         text=True).stdout.split()
    t("Z_no_marker_namespace_ref_anywhere", not [r for r in own if r.startswith((G._PROD_NAMESPACE, G._TEST_NAMESPACE))],
      [r for r in own if r.startswith((G._PROD_NAMESPACE, G._TEST_NAMESPACE))])
    return R


if __name__ == "__main__":
    SCRATCH.mkdir(parents=True, exist_ok=True)
    D.E.log("tests/test_p309_d5_exception.py", "owner D5 exception controls and R4 follow-up mutants M01-M15 (static "
            "mutants in temporary copies)", klass="GOVERNANCE",
            notes="static analysis of planted temporary copies; nothing from them is executed; no ref created; "
                  "nothing evaluated")
    res = run()
    ok = all(v["pass"] for v in res.values())
    out = {"utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "all_pass": ok,
           "controls": len(res), "test_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
           "scan_sha256": hashlib.sha256((FNS / "code" / "p309_scan.py").read_bytes()).hexdigest(),
           "static_check_sha256": hashlib.sha256((FNS / "code" / "p309_static_check.py").read_bytes()).hexdigest(),
           "allowance_config_sha256": hashlib.sha256((FNS / "config" / "SCANNER_ALLOWANCE_P309.json").read_bytes()
                                                     ).hexdigest(), "results": res}
    (D.E.evidence_dir("fc2") / "D5_EXCEPTION_CONTROLS.json").write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    for k, v in res.items():
        print(f"[{'PASS' if v['pass'] else 'FAIL'}] {k}  {'' if v['pass'] else v['detail']}")
    sys.exit(0 if ok else 1)
