"""Tests of the band-scoped producer-side guard (code/p309_guard.py) against fc2/FC2_SPEC_R2.md section 8.

  python3 tests/test_p309_guard.py   -> evidence/fc2/GUARD_TESTS.json; exit 0 iff every test passes

Rules kept by every test (owner rulings 2):
* the production marker name, and any ref under the production namespace, is never created anywhere;
* nothing is ever written at the production grant path, in any repository;
* REAL-band items are presented to the admission check only (dry); nothing is computed;
* sandboxes are light repositories under the scratchpad (`git init` + a read-only alternates link to this
  repository's objects); they have no remote and are never pushed.
"""
from __future__ import annotations

import datetime
import hashlib
import json
import os
import platform
import shutil
import subprocess
import sys
import tempfile
from fractions import Fraction as F
from pathlib import Path

FNS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(FNS / "code"))
import p309_env as E  # noqa: E402
import p309_guard as G  # noqa: E402

REPO = E.REPO
SCRATCH = Path("/tmp/claude-0/-home-user-ReBaseGuard/ea54e9f6-e828-5447-be15-220ef2c329fd/scratchpad/fc2_sandbox_coordinator")
SB_BRANCH = "refs/heads/p309-test-sandbox"
H3_CELL_FILES = [E.RNS / "evidence" / "srk_decoys_cell" / f"cell_h3_k1_2_C1_3_20_51_S{j}.json" for j in range(4)]
REAL_ITEM = ("7/5", "3/2")     # q309: literal-ok (a REAL-band interval presented to the admission check only; dry)
REAL_MIRROR = ("-3/2", "-7/5")  # q309: literal-ok (mirror of the above; dry)
H3 = ("3", "1/2")
H5 = ("5", "1/2")
EW = ("341/1024", "201/512")


# ------------------------------------------------------------------------------------------------ sandbox helpers
def sh(repo: Path, *args, env=None, input_=None) -> str:
    e = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    e.update({"GIT_AUTHOR_NAME": "p309-test", "GIT_AUTHOR_EMAIL": "test@invalid", "GIT_COMMITTER_NAME": "p309-test",
              "GIT_COMMITTER_EMAIL": "test@invalid"})
    e.update(env or {})
    r = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, input=input_, env=e)
    if r.returncode != 0:
        raise RuntimeError(f"git {args}: {r.stderr.decode()[-300:]}")
    return r.stdout.decode()


def forbid_production_refs(sb: Path) -> None:
    refs = sh(sb, "for-each-ref", "--format=%(refname)").split()
    assert not [r for r in refs if r.startswith(G._PROD_NAMESPACE)], "a production-namespace ref exists"


def new_sandbox(name: str) -> Path:
    """a light sandbox: `git init` + a read-only alternates link to this repository's object store (+ its shallow
    boundary); this repository is shallow, so `git clone --shared` would copy the whole pack per sandbox."""
    sb = SCRATCH / name
    if sb.exists():
        shutil.rmtree(sb)
    sb.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "init", "-q", str(sb)], check=True, capture_output=True)
    (sb / ".git" / "objects" / "info" / "alternates").write_text(str(REPO / ".git" / "objects") + "\n")
    if (REPO / ".git" / "shallow").exists():
        shutil.copy(REPO / ".git" / "shallow", sb / ".git" / "shallow")
    head = subprocess.run(["git", "-C", str(REPO), "rev-parse", "HEAD"], capture_output=True, text=True,
                          check=True).stdout.strip()
    sh(sb, "update-ref", SB_BRANCH, head)
    sh(sb, "symbolic-ref", "HEAD", SB_BRANCH)
    forbid_production_refs(sb)
    return sb


def commit(sb: Path, parent: str, files: dict, msg: str, remove=()) -> str:
    """Plumbing commit on a temporary index: files {path: bytes}; never touches a work tree."""
    with tempfile.NamedTemporaryFile(dir=SCRATCH, delete=False) as tf:
        idx = tf.name
    try:
        env = {"GIT_INDEX_FILE": idx}
        sh(sb, "read-tree", parent, env=env)
        for path, data in files.items():
            blob = sh(sb, "hash-object", "-w", "--stdin", input_=data).strip()
            sh(sb, "update-index", "--add", "--cacheinfo", f"100644,{blob},{path}", env=env)
        for path in remove:
            sh(sb, "update-index", "--force-remove", path, env=env)
        tree = sh(sb, "write-tree", env=env).strip()
        return sh(sb, "commit-tree", tree, "-p", parent, "-m", msg).strip()
    finally:
        os.unlink(idx)


def set_head(sb: Path, c: str) -> None:
    sh(sb, "update-ref", SB_BRANCH, c)
    sh(sb, "symbolic-ref", "HEAD", SB_BRANCH)


def set_test_ref(sb: Path, ref: str, c: str) -> None:
    assert ref.startswith(("refs/p309-test/", "refs/heads/p309-test-", "refs/remotes/origin/p309-test-")), ref
    sh(sb, "update-ref", ref, c)


def manifest_bytes(path=None, sha=None) -> bytes:
    pins = [{"path": path or G.own_relpath(), "sha256": sha or G.own_id()[7:]}]
    return json.dumps({"schema": "P309_TEST_FREEZE_MANIFEST/1", "code_pins": pins}, sort_keys=True).encode()


def grant_dict(fc: str, msha: str, **over) -> dict:
    g = {"schema": "P309_TEST_GRANT/1", "campaign": G._TEST_CELL, "cell": G._TEST_CELL,
         "geometry": {"h": "3", "k": "1/2"}, "cell_interval": ["1/3", "20/51"], "drift_hull_Ew": list(EW),
         "frozen_commit": fc, "frozen_manifest_sha256": msha, "verifier_id": "sha256:" + "0" * 64,
         "guard_id": G.own_id(), "execution_host": {"host_id_sha256": G.host_id()},
         "runtime": {"python": platform.python_version()}, "marker_ref": G.TEST_MARKER,
         "not_after_utc": "2099-12-31T23:59:59Z"}
    for k, v in over.items():
        if v is DELETE:
            g.pop(k, None)
        else:
            g[k] = v
    return g


DELETE = object()
N2_REASONS = {"invalid_json": "JSONDecodeError", "missing_field": "grant misses", "wrong_type": "cell_interval malformed",
              "unknown_schema": "schema/campaign", "ew_lo_ge_hi": "drift_hull_Ew malformed",
              "non_rational": "not an exact rational"}


def why(d, fragment: str) -> tuple:
    """R4 NB2: a negative control passes only when it is refused FOR THE EXPECTED REASON"""
    return d[0] == "REFUSE" and fragment in d[1], d


def scenario(name: str, *, grant=None, grant_raw=None, manifest=None, extra_grant_files=None, marker="grant",
             head="grant", after=None):
    """Build a sandbox: base -> freeze commit (manifest) -> grant commit; returns (ctx, commits)."""
    sb = new_sandbox(name)
    base = sh(sb, "rev-parse", "HEAD").strip()
    man = manifest if manifest is not None else manifest_bytes()
    fc = commit(sb, base, {G._TEST_MANIFEST_PATH: man}, "TEST_ONLY freeze manifest")
    msha = hashlib.sha256(man).hexdigest()
    c = {"base": base, "freeze": fc}
    if grant is None and grant_raw is None:
        set_head(sb, fc)
    else:
        raw = grant_raw if grant_raw is not None else json.dumps(grant(fc, msha) if callable(grant) else grant,
                                                                 sort_keys=True).encode()
        files = {G._TEST_GRANT_PATH: raw}
        files.update(extra_grant_files or {})
        gc = commit(sb, fc, files, "TEST_ONLY grant")
        c["grant"] = gc
        tip = gc
        if after:
            tip = after(sb, c)
        set_head(sb, tip if head == "tip" else (gc if head == "grant" else c[head]))
        if marker == "grant":
            set_test_ref(sb, G.TEST_MARKER, gc)
        elif marker in c:
            set_test_ref(sb, G.TEST_MARKER, c[marker])
    forbid_production_refs(sb)
    return G.TestContext(sb), c, sb


def dec(item_geo, lo, hi, ctx=None, mode="official"):
    return G.admission_decision({"geometry": item_geo, "lo": lo, "hi": hi}, ctx=ctx, mode=mode)


def h3_blocks():
    out = []
    for f in H3_CELL_FILES:
        d = json.loads(f.read_text())
        out.append(tuple(d["block"]))
        assert tuple(d["weight_block"]) == EW
    return out


# ------------------------------------------------------------------------------------------------------ the tests
def run() -> dict:
    R = {}

    def t(name, cond, detail=""):
        R[name] = {"pass": bool(cond), "detail": str(detail)[:240]}

    # D1: REAL band, production context, dry (no grant exists in this repository)
    d = dec(H5, *REAL_ITEM)
    t("D1_real_band_production_no_grant", d[0] == "REFUSE" and "no grant" in d[1], d)
    d = dec(H5, *REAL_MIRROR)
    t("D1b_real_mirror_production_no_grant", d[0] == "REFUSE", d)
    t("D1c_decoy_interval_not_banded", dec(H5, "1/2", "17/32")[0] == "NOT_BANDED")
    try:
        G.guard_interval(H5, *REAL_ITEM)
        t("D1d_guard_interval_raises", False, "no exception")
    except G.QuarantineRefusal as exc:
        t("D1d_guard_interval_raises", True, exc)

    # P1: the TEST positive path
    good = lambda fc, ms: grant_dict(fc, ms)  # noqa: E731
    ctx, c, sb = scenario("p1", grant=good)
    blocks = h3_blocks()
    res = [dec(H3, lo, hi, ctx) for lo, hi in blocks] + [dec(H3, *EW, ctx)]
    t("P1_test_band_admitted_inside_Ew", all(r[0] == "ADMIT" for r in res), res[:2])
    try:
        for lo, hi in blocks:
            G.guard_interval(H3, lo, hi, ctx=ctx)
        ad = G.producer_adapter(ctx)
        ad.guard_drift(*blocks[0])
        ad.log_execution("test", "adapter log", klass="SYNTHETIC", drifts=[list(blocks[1])])
        t("P1b_guard_interval_and_adapter_allowed", len(ad.records) == 1)
    except Exception as exc:  # noqa: BLE001
        t("P1b_guard_interval_and_adapter_allowed", False, exc)
    # same valid sandbox: everything the positive path must still refuse
    t("N4a_interval_leaves_Ew", *why(dec(H3, "401/1024", "103/256", ctx), "not inside Ew"))
    t("N9a_test_ctx_real_band_geometry_5", *why(dec(H5, *REAL_ITEM, ctx), "only in the production context"))
    t("N9b_test_ctx_real_band_geometry_3", *why(dec(H3, *REAL_ITEM, ctx), "only in the production context"))
    t("N9c_production_ctx_test_band", *why(dec(H3, *EW), "only in a test context"))
    t("N12_guard_has_no_review_mode", *why(dec(H3, *EW, ctx, mode="review"), "no review mode"))
    t("N13a_fail_closed_on_git_error", _fail_closed(ctx))
    try:
        G.producer_adapter(ctx).guard_drift(*REAL_ITEM)
        t("N9d_test_adapter_real_band_raises", False)
    except G.QuarantineRefusal:
        t("N9d_test_adapter_real_band_raises", True)
    try:
        G.producer_adapter().guard_drift(*REAL_ITEM)
        t("D1e_production_adapter_real_band_raises", False)
    except G.QuarantineRefusal:
        t("D1e_production_adapter_real_band_raises", True)
    t("D1f_producer_call_site_refuses", _producer_call_site())

    # N1 no grant
    ctx1, _, _ = scenario("n1", grant=None)
    t("N1_no_test_grant", *why(dec(H3, *EW, ctx1), "no grant at HEAD"))

    # N2 malformed
    for nm, kw in {"invalid_json": dict(grant_raw=b"{not json"),
                   "missing_field": dict(grant=lambda fc, ms: grant_dict(fc, ms, runtime=DELETE)),
                   "wrong_type": dict(grant=lambda fc, ms: grant_dict(fc, ms, cell_interval="1/3,20/51")),
                   "unknown_schema": dict(grant=lambda fc, ms: grant_dict(fc, ms, schema="P309_TEST_GRANT/2")),
                   "ew_lo_ge_hi": dict(grant=lambda fc, ms: grant_dict(fc, ms, drift_hull_Ew=["201/512", "341/1024"])),
                   "non_rational": dict(grant=lambda fc, ms: grant_dict(fc, ms, drift_hull_Ew=["0.333", "201/512"]))
                   }.items():
        cx, _, _ = scenario("n2_" + nm, **kw)
        t("N2_" + nm, *why(dec(H3, *EW, cx), N2_REASONS[nm]))
    # N3 wrong cell
    cx, _, _ = scenario("n3a", grant=lambda fc, ms: grant_dict(fc, ms, cell="OTHER_CELL"))
    t("N3a_wrong_cell_string", *why(dec(H3, *EW, cx), "grant cell is not"))
    cx, _, _ = scenario("n3b", grant=lambda fc, ms: grant_dict(fc, ms, cell=G._PROD_CELL))
    t("N3b_wrong_cell_type", *why(dec(H3, *EW, cx), "grant cell is not"))
    # N4 wrong Ew
    cx, _, _ = scenario("n4b", grant=lambda fc, ms: grant_dict(fc, ms, drift_hull_Ew=["85/256", "201/512"]))
    t("N4b_Ew_not_outward_hull", *why(dec(H3, "341/1024", "1425/4096", cx), "outward 2^-10 hull"))
    cx, _, _ = scenario("n4c", grant=lambda fc, ms: grant_dict(fc, ms, cell_interval=["1/3", "3/8"],
                                                               drift_hull_Ew=["341/1024", "3/8"]))
    t("N4c_narrower_Ew_excludes_block", *why(dec(H3, *blocks[3], cx), "not inside Ew"))
    # N5 wrong guard id
    cx, _, _ = scenario("n5", grant=lambda fc, ms: grant_dict(fc, ms, guard_id="sha256:" + "1" * 64))
    t("N5_wrong_guard_id", *why(dec(H3, *EW, cx), "guard_id is not this file"))
    # N6 frozen identity
    cx, _, _ = scenario("n6a", grant=lambda fc, ms: grant_dict(fc, ms, frozen_manifest_sha256="2" * 64))
    t("N6a_manifest_sha_mismatch", *why(dec(H3, *EW, cx), "manifest sha256 mismatch"))
    cx, _, _ = scenario("n6b", manifest=manifest_bytes(path="level4/other.py"), grant=good)
    t("N6b_own_file_not_in_manifest", *why(dec(H3, *EW, cx), "not pinned"))
    cx, _, _ = scenario("n6c", manifest=manifest_bytes(sha="3" * 64), grant=good)
    t("N6c_own_file_other_sha", *why(dec(H3, *EW, cx), "not pinned"))
    cx, cc, sbx = scenario("n6d", grant=lambda fc, ms: grant_dict(fc, ms, frozen_commit="4" * 40))
    t("N6d_frozen_commit_unknown", *why(dec(H3, *EW, cx), "not an ancestor"))

    def orphan_freeze(fc, ms):
        return grant_dict(fc, ms)
    # frozen commit that exists but is not an ancestor: a sibling commit with the same manifest
    ctx_s, cs, sbs = scenario("n6e", grant=good)
    sib = commit(sbs, cs["base"], {G._TEST_MANIFEST_PATH: manifest_bytes(), "TEST_ONLY/sibling": b"x"}, "sibling")
    g2 = grant_dict(sib, hashlib.sha256(manifest_bytes()).hexdigest())
    gc2 = commit(sbs, cs["freeze"], {G._TEST_GRANT_PATH: json.dumps(g2, sort_keys=True).encode()}, "grant(sibling)")
    set_head(sbs, gc2)
    set_test_ref(sbs, G.TEST_MARKER, gc2)
    t("N6e_frozen_commit_not_ancestor", *why(dec(H3, *EW, G.TestContext(sbs)), "not an ancestor"))
    # N7 marker / grant commit
    cx, _, _ = scenario("n7a", grant=good, marker=None)
    t("N7a_marker_absent", *why(dec(H3, *EW, cx), "git rev-parse failed"))       # the marker does not resolve
    cx, _, _ = scenario("n7b", grant=good, marker="freeze")
    t("N7b_marker_elsewhere", *why(dec(H3, *EW, cx), "marker does not name"))
    cx, cc, sbx = scenario("n7c", grant=good)
    set_test_ref(sbx, "refs/p309-test/TEST_ONLY_EXTRA_REF", cc["grant"])
    t("N7c_extra_namespace_ref", *why(dec(H3, *EW, G.TestContext(sbx)), "holds other refs"))
    cx, _, _ = scenario("n7d", grant=good, head="tip",
                        after=lambda s, c: commit(s, c["grant"], {"TEST_ONLY/child": b"c"}, "child"))
    t("N7d_head_not_grant_commit", *why(dec(H3, *EW, cx), "HEAD is not the grant commit"))
    cx, _, _ = scenario("n7e", grant=good, extra_grant_files={"TEST_ONLY/other": b"o"})
    t("N7e_grant_commit_touches_other_file", *why(dec(H3, *EW, cx), "touches other paths"))

    def readd(s, c):
        rm = commit(s, c["grant"], {}, "remove grant", remove=(G._TEST_GRANT_PATH,))
        raw = sh(s, "show", f"{c['grant']}:{G._TEST_GRANT_PATH}").encode()
        c["grant2"] = commit(s, rm, {G._TEST_GRANT_PATH: raw}, "re-add grant")
        set_test_ref(s, G.TEST_MARKER, c["grant2"])
        return c["grant2"]
    cx, _, sbx = scenario("n7f", grant=good, head="tip", marker=None, after=readd)
    t("N7f_two_commits_add_grant", *why(dec(H3, *EW, G.TestContext(sbx)), "commits add the grant"))
    cx, _, _ = scenario("n7g", grant=lambda fc, ms: grant_dict(fc, ms, not_after_utc="2000-01-01T00:00:00Z"))
    t("N7g_expired", *why(dec(H3, *EW, cx), "grant expired"))
    cx, cc, sbx = scenario("n7h", grant=good)
    child = commit(sbx, cc["grant"], {"TEST_ONLY/seal": b"s"}, "a descendant on another ref")
    set_test_ref(sbx, "refs/heads/p309-test-other", child)
    t("N7h_strict_descendant_on_other_ref", *why(dec(H3, *EW, G.TestContext(sbx)), "strict descendant"))
    # R4 B7(d): E1-1's positive case -- a non-current ref exactly AT the grant commit (e.g. the remote-tracking ref
    # after the owner's grant is pushed and fetched) does not block admission; and a detached HEAD is refused
    cx, cc, sbx = scenario("n7i", grant=good)
    set_test_ref(sbx, "refs/remotes/origin/p309-test-sandbox", cc["grant"])
    d = dec(H3, *EW, G.TestContext(sbx))
    t("N7i_ref_at_grant_commit_admitted", d[0] == "ADMIT", d)
    cx, cc, sbx = scenario("n7j", grant=good)
    sh(sbx, "checkout", "-q", "--detach", cc["grant"])
    t("N7j_detached_head_refused", *why(dec(H3, *EW, G.TestContext(sbx)), "symbolic-ref"))
    # R4 B3: the pre-marker dry admission (premarker_check) -- ready before the marker, never an admission
    cx, cc, sbx = scenario("pm1", grant=good, marker=None)
    ok, why_ = G.premarker_check(cx)
    t("PM1_premarker_ready_without_marker", ok and "passes the pre-marker checks" in why_, why_)
    t("PM1b_no_admission_without_marker", *why(dec(H3, *EW, cx), "git rev-parse failed"))
    cx, _, _ = scenario("pm2", grant=good)
    ok, why_ = G.premarker_check(cx)
    t("PM2_premarker_refuses_when_namespace_not_empty", not ok and "not empty before the marker" in why_, why_)
    cx, _, _ = scenario("pm3", grant=lambda fc, ms: grant_dict(fc, ms, not_after_utc="2000-01-01T00:00:00Z"),
                        marker=None)
    ok, why_ = G.premarker_check(cx)
    t("PM3_premarker_refuses_expired", not ok and "grant expired" in why_, why_)
    cx, _, _ = scenario("pm4", grant=lambda fc, ms: grant_dict(fc, ms, execution_host={"host_id_sha256": "5" * 64}),
                        marker=None)
    ok, why_ = G.premarker_check(cx)
    t("PM4_premarker_refuses_wrong_host", not ok and "execution host mismatch" in why_, why_)
    ok, why_ = G.premarker_check(object())
    t("PM5_premarker_refuses_unknown_context", not ok, why_)
    # N8 host / runtime
    cx, _, _ = scenario("n8a", grant=lambda fc, ms: grant_dict(fc, ms, execution_host={"host_id_sha256": "5" * 64}))
    t("N8a_wrong_host", *why(dec(H3, *EW, cx), "execution host mismatch"))
    cx, _, _ = scenario("n8b", grant=lambda fc, ms: grant_dict(fc, ms, runtime={"python": "0.0.0"}))
    t("N8b_wrong_runtime", *why(dec(H3, *EW, cx), "runtime mismatch"))
    # N10 / N11: production authorization cannot be synthesized from test artifacts; synthetic marker substitution
    prod_shaped = lambda fc, ms: grant_dict(fc, ms, schema="P309_GRANT/1", campaign="p5y_k5_cell309_p309_r2",  # noqa: E731
                                            cell=G._PROD_CELL, geometry={"h": "5", "k": "1/2"},
                                            marker_ref=G.TEST_MARKER)
    cx, _, sbx = scenario("n10", grant=prod_shaped)
    t("N10a_production_ctx_ignores_sandbox", *why(dec(H5, *REAL_ITEM), "no grant at HEAD"))
    t("N10a2_test_ctx_refuses_production_shaped_grant", *why(dec(H3, *EW, cx), "schema/campaign"))
    t("N10b_real_band_with_test_ctx", *why(dec(H5, *REAL_ITEM, cx), "only in the production context"))
    t("N11_synthetic_marker_not_production", why(dec(H5, *REAL_ITEM), "no grant at HEAD")[0]
      and why(dec(H3, *EW, cx), "schema/campaign")[0])
    for nm, root in (("repo_root", REPO), ("repo_subdir", FNS)):
        try:
            G.TestContext(root)
            t(f"N10c_testcontext_refuses_{nm}", False, "constructed")
        except ValueError as exc:
            t(f"N10c_testcontext_refuses_{nm}", True, exc)
    # N13 fail closed: a context whose repository is not a git repository
    try:
        G.TestContext(SCRATCH.parent)
        t("N13b_testcontext_non_git_raises", False, "constructed")
    except Exception as exc:  # noqa: BLE001
        t("N13b_testcontext_non_git_raises", True, type(exc).__name__)
    # immutability / singleton
    try:
        G.PRODUCTION.marker_ref = G.TEST_MARKER
        t("S1_production_context_immutable", False)
    except AttributeError:
        t("S1_production_context_immutable", True)
    try:
        G._Production()
        t("S2_production_singleton", False)
    except RuntimeError:
        t("S2_production_singleton", True)
    # no production ref and no production grant path anywhere after all tests
    bad = []
    for p in sorted(SCRATCH.iterdir()) if SCRATCH.exists() else []:
        if (p / ".git").exists() or (p / "HEAD").exists():
            try:
                refs = sh(p, "for-each-ref", "--format=%(refname)").split()
                bad += [r for r in refs if r.startswith(G._PROD_NAMESPACE)]
                if sh(p, "log", "--all", "--format=%H", "--", G._PROD_GRANT_PATH).strip():
                    bad.append(f"{p.name}: production grant path in history")
            except RuntimeError:
                pass
    own_refs = sh(REPO, "for-each-ref", "--format=%(refname)").split()
    bad += [r for r in own_refs if r.startswith(G._PROD_NAMESPACE)]
    t("Z_no_production_marker_or_grant_anywhere", not bad, bad)
    return R


def _fail_closed(ctx) -> bool:
    orig = G._git_bytes

    def boom(*a, **k):
        raise OSError("injected")
    G._git_bytes = boom
    try:
        return why(dec(H3, *EW, ctx), "OSError")[0]
    finally:
        G._git_bytes = orig


def _producer_call_site() -> bool:
    """The pinned producer's own guard call (srk_certify.guard_geometry_block) refuses through the production
    adapter.  guard_geometry_block is a pure guard (it only calls Q.guard_drift); nothing is computed."""
    import srk_certify as S
    import srk_kernel as KX
    orig = S.Q
    S.Q = G.producer_adapter()
    try:
        S.guard_geometry_block(KX.Geom(5, F(1, 2)), F(*map(int, REAL_ITEM[0].split("/"))),
                               F(*map(int, REAL_ITEM[1].split("/"))))
        return False
    except G.QuarantineRefusal:
        return True
    finally:
        S.Q = orig


if __name__ == "__main__":
    E.log("tests/test_p309_guard.py", "FC2 guard tests (spec R2 section 8): sandbox TEST-band positive path on the "
          "declared h3 decoy-cell hull; dry REAL-band refusals", klass="SYNTHETIC",
          notes="admission checks only (git metadata, hashes, rationals); nothing evaluated; sandboxes are shared "
                "light repositories under the scratchpad (alternates, no remote), never pushed; no production ref or grant path created")
    res = run()
    ok = all(v["pass"] for v in res.values())
    out = {"utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
           "guard_sha256": G.own_id()[7:], "test_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
           "git_head": sh(REPO, "rev-parse", "HEAD").strip(), "all_pass": ok, "results": res}
    (E.evidence_dir("fc2") / "GUARD_TESTS.json").write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    for k, v in res.items():
        print(f"[{'PASS' if v['pass'] else 'FAIL'}] {k}  {'' if v['pass'] else v['detail']}")
    sys.exit(0 if ok else 1)
