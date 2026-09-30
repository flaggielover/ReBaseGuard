"""Owner D5 exception controls: the ratified production mutation sites may EXIST, and nothing else may move a ref.

  python3 -I -S -B tests/test_p309_d5_exception.py   -> evidence/fc2/D5_EXCEPTION_CONTROLS.json; exit 0 iff all pass

The owner's D5 decision (governance/OWNER_D5_RATIFICATION_P309_VERBATIM.md) requires the scanner to keep rejecting:
  (1) any additional production marker mutation site;       (2) any additional pending-ref mutation site;
  (3) any unreviewed ref mutation path;                      (4) any dynamically constructed equivalent;
  (5) any mutation reachable without execute mode;           (6) any mutation reachable without a valid owner grant;
  (7) any qualification/test path capable of mutating the production refs.
Each static control plants one violation into a temporary copy of the namespace's code/config/tests/verify and requires
the formal scan (code/p309_scan.py) and/or the static check (code/p309_static_check.py, T4/T6/T7) to reject it.  The
runtime controls call `_assert_execute_context` -- the first statement of both sites (QC12 T4) -- in sandboxes with
the synthetic TEST names only.  The genuine copy must pass (positive control).  Nothing is executed from the planted
sources, no production ref is created anywhere, and nothing is evaluated.
"""
from __future__ import annotations

import datetime
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import types
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
        if old == "new":
            p.write_text(new)
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
NS_A, NS_B = _NS[:len(_NS) // 2], _NS[len(_NS) // 2:]
LEAF_A, LEAF_B = _LEAF[:len(_LEAF) // 2], _LEAF[len(_LEAF) // 2:]


def run() -> dict:
    R = {}

    def t(name, cond, detail=""):
        R[name] = {"pass": bool(cond), "detail": str(detail)[:300]}

    # positive control: the genuine tree
    scan, static = planted({})
    t("P0_genuine_tree_scan_pass", scan["verdict"] == "PASS", kinds(scan))
    t("P0b_genuine_tree_static_pass", all(v["pass"] for v in static.values()),
      {k: v["detail"] for k, v in static.items() if not v["pass"]})
    t("P0c_exactly_two_sanctioned_sites", sorted(x["function"] for x in scan["sanctioned_exactly_once_sites"]) ==
      ["_arm_marker", "_persist_pending"], scan["sanctioned_exactly_once_sites"])

    # (1) / (2) additional production mutation sites
    scan, _ = planted({DRIVER: ("+", "def _arm_again(ctx, gc):\n    _assert_execute_context(ctx)\n"
                                     "    git('update-ref', ctx.marker_ref, gc, '0' * 40, repo=ctx.repo)\n")})
    t("C01_additional_marker_site", "MARKER_MUTATION" in kinds(scan), kinds(scan))
    scan, _ = planted({DRIVER: ("+", "def _pend_again(ctx, b):\n    _assert_execute_context(ctx)\n"
                                     "    git('update-ref', ctx.pending_ref, b, '0' * 40, repo=ctx.repo)\n")})
    t("C02_additional_pending_site", "MARKER_MUTATION" in kinds(scan), kinds(scan))
    src = (FNS / DRIVER).read_text()
    i = src.index("def _arm_marker(")
    arm = src[i:src.index("\n\n\n", i)]
    scan, _ = planted({DRIVER: ("+", arm + "\n")})                      # a second def of the same name
    t("C03_duplicate_named_site", "MARKER_MUTATION" in kinds(scan) and len(scan["sanctioned_exactly_once_sites"]) < 2,
      kinds(scan))
    scan, _ = planted({"code/p309_other.py": ("new", "from p309_driver import git, _assert_execute_context\n\n\n" + arm
                                              + "\n")})
    t("C04_identical_site_in_another_file", "MARKER_MUTATION" in kinds(scan), kinds(scan))

    # (3) unreviewed ref mutation paths
    scan, _ = planted({DRIVER: ("+", "def _move(repo):\n    git('update-ref', 'refs/heads/x', 'HEAD', repo=repo)\n")})
    t("C05_unlisted_ref_mutation_non_production", "REF_MUTATION_UNLISTED" in kinds(scan), kinds(scan))
    scan, _ = planted({DRIVER: ('git("update-ref", ctx.branch_ref, cid, head, repo=ctx.repo)',
                                'git("update-ref", ctx.branch_ref + "", cid, head, repo=ctx.repo)')})
    t("C06_listed_function_changed", "REF_MUTATION_UNLISTED" in kinds(scan), kinds(scan))
    for verb in ("symbolic-ref", "push", "tag", "branch", "reset", "commit", "fast-import"):
        scan, _ = planted({"code/p309_rehearse.py": ("+", f"def _v(repo):\n    return D.git('{verb}', 'x', repo=repo)\n")})
        t(f"C07_unlisted_{verb}", "REF_MUTATION_UNLISTED" in kinds(scan), kinds(scan))
    scan, _ = planted({DRIVER: ("+", "def _raw(gd):\n    open(gd / 'refs' / 'heads' / 'x', 'w').write('0' * 40)\n")})
    t("C08_ref_file_write", "REF_FILE_WRITE" in kinds(scan), kinds(scan))
    scan, _ = planted({DRIVER: ("+", "def _raw2(gd):\n    os.makedirs(str(gd) + '/refs/p309')\n")})
    t("C08b_ref_dir_create", "REF_FILE_WRITE" in kinds(scan), kinds(scan))
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
    scan, static = planted({DRIVER: ("def _arm_marker(ctx: ExecContext, grant_commit: str) -> None:\n"
                                     "    _assert_execute_context(ctx)\n",
                                     "def _arm_marker(ctx: ExecContext, grant_commit: str) -> None:\n")})
    t("C19_site_without_execute_assertion", "MARKER_MUTATION" in kinds(scan) and static_fail(static, "T4_exactly_once_sites"),
      (kinds(scan), static["T4_exactly_once_sites"]["detail"]))
    scan, static = planted({DRIVER: ('    st = stage1a("decoy", cell, {"h": d["h"], "k": d["k"]}, verifier_id, workers=workers)',
                                     '    _arm_marker(production_context(), "0" * 40)\n'
                                     '    st = stage1a("decoy", cell, {"h": d["h"], "k": d["k"]}, verifier_id, workers=workers)')})
    t("C20_site_called_from_a_qualification_mode",
      static_fail(static, "T4_exactly_once_sites") and static_fail(static, "T1_no_path_from_qualification_modes_to_target"),
      static["T4_exactly_once_sites"]["detail"])

    # (6) mutation reachable without a valid owner grant
    scan, static = planted({DRIVER: ("    check_flags()\n    check_branch(ctx)\n    check_not_evaluated(ctx)\n",
                                     "    check_flags()\n    _arm_marker(ctx, 'x')\n    check_branch(ctx)\n"
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
    scan, static = planted({DRIVER: ("        _arm_marker(ctx, grant[\"grant_commit\"])\n",
                                     "        if grant:\n            _arm_marker(ctx, grant[\"grant_commit\"])\n")})
    t("C25_marker_inside_a_branch", static_fail(static, "T6_mutation_dominated_by_the_grant"),
      static["T6_mutation_dominated_by_the_grant"]["detail"])

    # (7) qualification / test paths
    for nm, body in (("production_context", "D.production_context()"),
                     ("execute_without_context", "D.run_execute('0' * 64)"),
                     ("execute_with_none", "D.run_execute('0' * 64, ctx=None)"),
                     ("seal_only_without_context", "D.run_seal_only()"),
                     ("site_call", "D._arm_marker(None, '0')"),
                     ("exec_context", "D.ExecContext('PRODUCTION', D.REPO, D.G.PRODUCTION, 'a', 'b', 'c', None)"),
                     ("driver_cli_execute", "subprocess.run([sys.executable, 'code/p309_driver.py', 'execute'])"),
                     ("driver_cli_seal_only", "subprocess.run([sys.executable, str(FNS / 'code' / 'p309_driver.py'), "
                                              "'seal-only'])")):
        scan, static = planted({"tests/test_evil.py": ("new", f"import subprocess, sys\nimport p309_driver as D\n\n\n"
                                                              f"def evil():\n    {body}\n")})
        t(f"C26_test_path_{nm}", static_fail(static, "T7_no_production_execution_from_tests_or_qualification"),
          static["T7_no_production_execution_from_tests_or_qualification"]["detail"])
    scan, _ = planted({"tests/test_evil2.py": ("new", "import p309_guard as G\n\n\ndef sh(*a):\n    pass\n\n\n"
                                                      "def evil(repo):\n    sh(repo, 'update-ref', G.PRODUCTION_MARKER, "
                                                      "'HEAD')\n")})
    t("C27_test_mutates_the_production_marker", "MARKER_MUTATION" in kinds(scan), kinds(scan))

    # runtime: the execute-context assertion (first statement of both sites; QC12 T4), TEST names only
    sb = SCRATCH / "rt_sandbox"
    if sb.exists():
        shutil.rmtree(sb)
    subprocess.run(["git", "init", "-q", str(sb)], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(sb), "-c", "user.name=t", "-c", "user.email=t@invalid", "commit", "-q",
                    "--allow-empty", "-m", "base"], check=True, capture_output=True)
    tc = G.TestContext(sb)
    good = types.SimpleNamespace(kind="SANDBOX", repo=tc.repo, guard_ctx=tc, marker_ref=G.TEST_MARKER,
                                 pending_ref=G.TEST_PENDING_REF)

    def refusal(mode, ctx) -> str:
        D._MODE["mode"] = mode
        try:
            D._assert_execute_context(ctx)
            return "allowed"
        except D.Refusal as exc:
            return exc.code
        finally:
            D._MODE.clear()
    t("R01_outside_execute_mode_refused", refusal("preflight", good) == "NOT_EXECUTE_MODE")
    t("R02_no_mode_refused", refusal(None, good) == "NOT_EXECUTE_MODE")
    t("R03_sandbox_context_in_execute_allowed", refusal("execute", good) == "allowed")
    t("R03b_sandbox_context_in_seal_only_allowed", refusal("seal-only", good) == "allowed")
    t("R04_production_kind_with_test_names_refused",
      refusal("execute", types.SimpleNamespace(**{**vars(good), "kind": "PRODUCTION"})) == "CONTEXT")
    t("R05_sandbox_kind_on_this_repository_refused",
      refusal("execute", types.SimpleNamespace(**{**vars(good), "repo": D.REPO})) == "CONTEXT")
    t("R06_sandbox_kind_with_production_guard_refused",
      refusal("execute", types.SimpleNamespace(**{**vars(good), "guard_ctx": G.PRODUCTION})) == "CONTEXT")
    t("R07_sandbox_kind_with_production_marker_name_refused",
      refusal("execute", types.SimpleNamespace(**{**vars(good), "marker_ref": G.PRODUCTION.marker_ref})) == "CONTEXT")
    t("R08_unknown_kind_refused", refusal("execute", types.SimpleNamespace(**{**vars(good), "kind": "OTHER"})) == "CONTEXT")
    refs = subprocess.run(["git", "-C", str(sb), "for-each-ref", "--format=%(refname)"], capture_output=True,
                          text=True).stdout.split()
    shutil.rmtree(sb)
    own = subprocess.run(["git", "-C", str(D.REPO), "for-each-ref", "--format=%(refname)"], capture_output=True,
                         text=True).stdout.split()
    t("Z_no_marker_namespace_ref_anywhere", not [r for r in refs + own if r.startswith((G._PROD_NAMESPACE,
                                                                                       G._TEST_NAMESPACE))],
      [r for r in refs + own if r.startswith((G._PROD_NAMESPACE, G._TEST_NAMESPACE))])
    return R


if __name__ == "__main__":
    SCRATCH.mkdir(parents=True, exist_ok=True)
    D.E.log("tests/test_p309_d5_exception.py", "owner D5 exception controls (static mutants in temporary copies; "
            "execute-context assertion in a scratch sandbox)", klass="GOVERNANCE",
            notes="static analysis of planted temporary copies; nothing from them is executed; TEST names only; "
                  "no production ref; nothing evaluated")
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
