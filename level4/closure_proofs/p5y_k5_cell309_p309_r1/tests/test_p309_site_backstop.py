"""R4 follow-up F1(a): runtime controls of the backstop at the two owner-ratified exactly-once sites.

  python3 -I -S -B tests/test_p309_site_backstop.py   -> evidence/fc6/SITE_BACKSTOP_CONTROLS.json; exit 0 iff all pass

The backstop lives in the driver's execute-context assertion, outside the ratified site ASTs (whose hashes are
unchanged).  These controls call the two sites themselves -- in light scratch sandboxes, with the guard's TestContext
and the synthetic TEST names only (TEST marker, TEST pending ref) -- and require:
  arm      refused without a grant at HEAD, without a run nonce, with a nonce of another process, outside execute mode,
           and when the marker namespace is not empty; allowed only with all of them (the TEST marker in the sandbox);
  pending  refused without a marker, with a marker whose commit carries no grant, and in execute mode without this
           process's run nonce; allowed in seal-only mode with a granted marker, and in execute mode with the nonce;
  caller   the assertion refuses any caller that is not one of the two sites (NOT_A_SITE);
  shape    the context-shape refusals (formerly the D5 R-controls): outside execute / seal-only mode, a PRODUCTION kind
           with TEST names, a SANDBOX kind on this repository, with the production guard context, with the production
           marker NAME, or of an unknown kind -- each refused before any site check.
No production-shaped context is ever passed to a site, nothing runs against this repository, no production ref is
created anywhere, and nothing is evaluated.  This file is listed in config t7_exemptions (it must name the sites and
the mode switch); the listing is bound to its AST hash.
"""
from __future__ import annotations

import datetime
import hashlib
import json
import os
import subprocess
import sys
import types
from pathlib import Path

FNS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(FNS / "code"))
sys.path.insert(0, str(FNS / "tests"))
import p309_driver as D  # noqa: E402
import test_p309_exactly_once as X  # noqa: E402  (the QC11 sandbox builders)

G = D.G


def refusal(fn, mode, *a) -> str:
    """run one site call (or the assertion) in `mode`; the refusal code, or 'allowed'"""
    D._MODE.clear()
    if mode is not None:
        D._MODE["mode"] = mode
    try:
        fn(*a)
        return "allowed"
    except D.Refusal as exc:
        return exc.code
    finally:
        D._MODE.clear()


def plant_nonce(sb: Path, pid: int) -> None:
    """a run nonce in the SANDBOX git dir naming `pid` (another process's nonce when pid is not ours)"""
    (X.git_dir_of(sb) / D.RUN_NONCE_NAME).write_text(json.dumps({"pid": pid, "token": "0" * 32}))


def drop_nonce(sb: Path) -> None:
    p = X.git_dir_of(sb) / D.RUN_NONCE_NAME
    if p.exists():
        p.unlink()


def run() -> dict:
    R = {}

    def t(name, cond, detail=""):
        R[name] = {"pass": bool(cond), "detail": str(detail)[:300]}
    me = os.getpid()

    # arm: the marker site
    sb0 = X.new_sandbox("BS_no_grant")                    # HEAD carries no grant
    c0 = X.ctx_of(sb0)
    head0 = X.sh(sb0, "rev-parse", "HEAD").strip()
    plant_nonce(sb0, me)
    t("B01_arm_without_a_grant_refused", refusal(D._arm_marker, "execute", c0, head0) == "GRANT_INVALID")
    drop_nonce(sb0)
    sb = X.new_sandbox("BS_granted")
    chain = X.build_chain(sb)
    ctx = X.ctx_of(sb)
    gc = chain["G"]
    t("B02_arm_without_a_run_nonce_refused", refusal(D._arm_marker, "execute", ctx, gc) == "RUN_NONCE")
    plant_nonce(sb, me + 1)
    t("B03_arm_with_another_process_nonce_refused", refusal(D._arm_marker, "execute", ctx, gc) == "RUN_NONCE")
    drop_nonce(sb)
    plant_nonce(sb, me)
    t("B04_arm_in_seal_only_mode_refused", refusal(D._arm_marker, "seal-only", ctx, gc) == "NOT_EXECUTE_MODE")
    t("B04b_arm_without_mode_refused", refusal(D._arm_marker, None, ctx, gc) == "NOT_EXECUTE_MODE")
    refs_before = X.refs(sb)
    t("B04c_no_refused_arm_moved_a_ref", X.refs(sb) == refs_before and G.TEST_MARKER not in refs_before)
    t("B05_arm_with_grant_nonce_and_execute_allowed", refusal(D._arm_marker, "execute", ctx, gc) == "allowed"
      and X.refs(sb).get(G.TEST_MARKER) == gc, X.refs(sb))
    t("B05b_second_arm_refused_by_the_backstop", refusal(D._arm_marker, "execute", ctx, gc) == "GRANT_INVALID")
    drop_nonce(sb)

    # pending: the evidence site (the marker exists in `sb`, at the grant commit)
    data = b'{"status": "TEST_ONLY backstop control"}'
    t("B06_pending_without_a_marker_refused", refusal(D._persist_pending, "seal-only", c0, data) == "NO_MARKER")
    sbm = X.new_sandbox("BS_marker_without_grant")         # a marker whose commit carries no grant
    X.build_chain(sbm)
    base = X.sh(sbm, "rev-parse", "HEAD~1").strip()
    X.sh(sbm, "update-ref", G.TEST_MARKER, base)
    t("B07_pending_with_an_ungranted_marker_refused",
      refusal(D._persist_pending, "seal-only", X.ctx_of(sbm), data) == "GRANT_INVALID")
    t("B08_pending_in_execute_without_nonce_refused",
      refusal(D._persist_pending, "execute", ctx, data) == "RUN_NONCE")
    t("B08b_pending_outside_execute_and_seal_only_refused",
      refusal(D._persist_pending, "preflight", ctx, data) == "NOT_EXECUTE_MODE")
    t("B09_pending_in_seal_only_with_a_granted_marker_allowed",
      refusal(D._persist_pending, "seal-only", ctx, data) == "allowed" and G.TEST_PENDING_REF in X.refs(sb), X.refs(sb))
    sbe = X.new_sandbox("BS_execute_pending")
    ce = X.build_chain(sbe)
    X.sh(sbe, "update-ref", G.TEST_MARKER, ce["G"])
    plant_nonce(sbe, me)
    t("B09b_pending_in_execute_with_the_nonce_allowed",
      refusal(D._persist_pending, "execute", X.ctx_of(sbe), data) == "allowed" and G.TEST_PENDING_REF in X.refs(sbe))
    drop_nonce(sbe)

    # caller: only the two sites pass the assertion
    t("B10_direct_call_is_not_a_site", refusal(D._assert_execute_context, "execute", ctx) == "NOT_A_SITE")

    def wrapper(c):
        D._assert_execute_context(c)
    t("B10b_a_wrapper_is_not_a_site", refusal(wrapper, "execute", ctx) == "NOT_A_SITE")
    t("B10c_site_codes_are_read_only", isinstance(D._SITE_CODES, types.MappingProxyType)
      and set(D._SITE_CODES.values()) == {"arm", "pending"} and len(D._SITE_CODES) == 2)

    # shape: refused before any site check (formerly the D5 R-controls), on the assertion itself
    fields = {"kind": "SANDBOX", "repo": ctx.repo, "guard_ctx": ctx.guard_ctx, "marker_ref": G.TEST_MARKER,
              "pending_ref": G.TEST_PENDING_REF}
    good = types.SimpleNamespace(**fields)
    A = D._assert_execute_context
    t("B11a_outside_execute_mode_refused", refusal(A, "preflight", good) == "NOT_EXECUTE_MODE")
    t("B11b_no_mode_refused", refusal(A, None, good) == "NOT_EXECUTE_MODE")
    t("B11c_production_kind_with_test_names_refused",
      refusal(A, "execute", types.SimpleNamespace(**{**fields, "kind": "PRODUCTION"})) == "CONTEXT")
    t("B11d_sandbox_kind_on_this_repository_refused",
      refusal(A, "execute", types.SimpleNamespace(**{**fields, "repo": D.REPO})) == "CONTEXT")
    t("B11e_sandbox_kind_with_production_guard_refused",
      refusal(A, "execute", types.SimpleNamespace(**{**fields, "guard_ctx": G.PRODUCTION})) == "CONTEXT")
    t("B11f_sandbox_kind_with_production_marker_name_refused",
      refusal(A, "execute", types.SimpleNamespace(**{**fields, "marker_ref": G.PRODUCTION.marker_ref})) == "CONTEXT")
    t("B11g_unknown_kind_refused", refusal(A, "execute", types.SimpleNamespace(**{**fields, "kind": "OTHER"})) ==
      "CONTEXT")
    t("B11h_good_shape_reaches_the_caller_check", refusal(A, "seal-only", good) == "NOT_A_SITE")

    sbs = [sb0, sb, sbm, sbe]
    refs = [r for s in sbs for r in X.refs(s)]
    own = subprocess.run(["git", "-C", str(D.REPO), "for-each-ref", "--format=%(refname)"], capture_output=True,
                         text=True).stdout.split()
    t("Z1_no_production_namespace_ref_in_any_sandbox", not [r for r in refs if r.startswith(G._PROD_NAMESPACE)], refs)
    t("Z2_no_marker_namespace_ref_in_this_repository",
      not [r for r in own if r.startswith((G._PROD_NAMESPACE, G._TEST_NAMESPACE))])
    return R


if __name__ == "__main__":
    X.SCRATCH.mkdir(parents=True, exist_ok=True)
    D.E.log("tests/test_p309_site_backstop.py", "R4 follow-up F1(a): runtime backstop controls at the two exactly-once "
            "sites (scratch sandboxes, TEST names only)", klass="GOVERNANCE",
            notes="light sandboxes under the scratchpad; the TEST marker / TEST pending ref only; no production-shaped "
                  "context reaches a site; no production ref; nothing evaluated")
    res = run()
    ok = all(v["pass"] for v in res.values())
    out = {"utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "all_pass": ok,
           "controls": len(res), "test_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
           "driver_sha256": hashlib.sha256(Path(D.__file__).read_bytes()).hexdigest(), "results": res}
    (D.E.evidence_dir("fc6") / "SITE_BACKSTOP_CONTROLS.json").write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    for k, v in res.items():
        print(f"[{'PASS' if v['pass'] else 'FAIL'}] {k}  {'' if v['pass'] else v['detail']}")
    sys.exit(0 if ok else 1)
