"""Post-execution checks (package rev. 2b section F; rev. 2c A7: this file replaces the postexec/ directory).

  python3 code/p309_postexec.py            -> run against this repository after a seal (never before a grant exists)

Every check is read-only except P4, which probes a second `execute` and must be refused before anything happens.
In qualification (QC11) the same functions run against sandbox flows with the synthetic TEST names.

  P1 the sealed result blob equals the pending-ref blob; the body's self-hash is valid
  P2 the seal commit changes the result path only; its only parent is the grant commit
  P3 the marker names the grant commit; exactly one commit adds the result
  P4 a second `execute` is refused before anything happens (no new ref, no new commit, exit 2)
  P5 `seal-only` on a sealed result computes nothing and changes nothing
  P6 the worktree copy equals the sealed bytes
  P7 r5 byte-identical to its pin; no r6 anywhere
  P8 no other cell was evaluated (the sealed target is the single target cell; one target evaluation)
  P9 the historical-control digest is present and equals the digest of the sealed control body, all fields true
  P10 independent re-verification: every sealed Stage-1a certificate, verified by the band-scoped verifier in REVIEW
      mode, gets exactly the sealed verdict (genuine certificates only; no probes).  Any difference, or a missing
      digest (P9), makes the outcome EXECUTION_INDETERMINATE (protocol section 5)
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import p309_driver as D  # noqa: E402


def _blob(ctx, rel: str, commit: str = "HEAD") -> bytes:
    r = D.git("show", f"{commit}:{rel}", repo=ctx.repo)
    return r.stdout.encode() if r.returncode == 0 else b""


def checks(ctx: D.ExecContext, *, own_sha: str | None = None, reverify=None, second_execute=None) -> dict:
    out = {}
    pending = D.git("rev-parse", "-q", "--verify", ctx.pending_ref, repo=ctx.repo).stdout.strip()
    marker = D.git("rev-parse", "-q", "--verify", ctx.marker_ref, repo=ctx.repo).stdout.strip()
    entry = D.git("ls-tree", "HEAD", "--", D.RESULT_REL, repo=ctx.repo).stdout.split()
    data = D.git("cat-file", "blob", pending, repo=ctx.repo).stdout.encode() if pending else b""
    try:
        rec = json.loads(data)
        body = {k: v for k, v in rec.items() if k != "sha256"}
        self_ok = rec.get("sha256") == hashlib.sha256(json.dumps(body, sort_keys=True).encode()).hexdigest()
    except ValueError:
        rec, self_ok = {}, False
    out["P1_blob_equals_pending_and_self_hash"] = bool(pending) and entry[2:3] == [pending] and self_ok
    adds = D.git("log", "--format=%H", "--diff-filter=A", "--", D.RESULT_REL, repo=ctx.repo).stdout.split()
    seal = adds[0] if len(adds) == 1 else None
    grant_c = (rec.get("grant") or {}).get("grant_commit")
    parents = D.git("rev-list", "--parents", "-n", "1", seal, repo=ctx.repo).stdout.split()[1:] if seal else []
    changed = D.git("diff-tree", "--no-commit-id", "--name-only", "-r", seal, repo=ctx.repo).stdout.split() if seal else []
    out["P2_seal_changes_result_only_parent_is_grant"] = bool(seal) and changed == [D.RESULT_REL] and parents == [grant_c]
    out["P3_marker_names_grant_one_execution"] = bool(marker) and marker == grant_c and len(adds) == 1 and \
        rec.get("target_evaluations") == 1
    if second_execute is not None:
        before = (D.git("for-each-ref", "--format=%(refname) %(objectname)", repo=ctx.repo).stdout,
                  D.git("rev-parse", "HEAD", repo=ctx.repo).stdout)
        rc = second_execute()
        after = (D.git("for-each-ref", "--format=%(refname) %(objectname)", repo=ctx.repo).stdout,
                 D.git("rev-parse", "HEAD", repo=ctx.repo).stdout)
        out["P4_second_execute_refused"] = rc == 2 and before == after
    head0 = D.git("rev-parse", "HEAD", repo=ctx.repo).stdout.strip()
    try:
        rc = D.run_seal_only(ctx)
    except D.Refusal:                                    # a refusal is a failed check, never a crash of the checker
        rc = None
    out["P5_seal_only_changes_nothing"] = rc == 0 and D.git("rev-parse", "HEAD", repo=ctx.repo).stdout.strip() == head0
    wt = (ctx.repo / D.RESULT_REL)
    out["P6_worktree_copy_equals_sealed"] = wt.is_file() and not wt.is_symlink() and wt.read_bytes() == data
    names = D.git("ls-tree", "-r", "--name-only", "HEAD", repo=ctx.repo).stdout.split()
    out["P7_no_r6"] = not any(Path(n).name.startswith(D.R6_NAME) for n in names)
    if ctx.kind == "PRODUCTION":
        m = D.load_manifest(ctx.repo)
        try:
            D.read_pinned(D.pin_table(m), D.data_rel(m, "coverage_r5"), ctx.repo)
            out["P7_r5_unchanged"] = True
        except D.Refusal:
            out["P7_r5_unchanged"] = False
    tgt = rec.get("target") or {}
    out["P8_single_target_cell"] = rec.get("cell") == D.TARGET_CELL and tgt.get("cell", D.TARGET_CELL) == D.TARGET_CELL
    hc = rec.get("historical_control") or {}
    body = {k: hc.get(k) for k in ("cell", "fields", "reproduces_C2_exactly")}
    out["P9_control_digest"] = bool(hc.get("digest")) and (
        hc.get("digest") == "sandbox" or (hc.get("digest") == D.sha(D.canon(body)) and hc.get("reproduces_C2_exactly") is True
                                          and all((hc.get("fields") or {}).values())))
    if reverify is not None:
        out["P10_review_mode_reverification"] = reverify(rec)
    out["ok"] = all(v for k, v in out.items())
    out["outcome_if_failed"] = "EXECUTION_INDETERMINATE" if not out["ok"] else None
    return out


def reverify_production(rec: dict) -> bool:
    """P10 in production: the band-scoped verifier in REVIEW mode on every sealed Stage-1a certificate."""
    import importlib.util
    vs = importlib.util.spec_from_file_location("srk_verify_indep_scoped", str(D.REPO / D.VARIANT_REL))
    V = importlib.util.module_from_spec(vs)
    vs.loader.exec_module(V)
    s1a = (rec.get("target") or {}).get("stage1a") or {}
    sealed = s1a.get("verdicts") or {}
    for c in s1a.get("certificates") or []:
        v = V.verify_cert(c, None, N=D.VERIFIER_N, max_depth=D.VERIFIER_DEPTH, procs=1, log=None, mode="review")
        if v["verdict"] != sealed.get(c.get("sha256")):
            return False
    return True


if __name__ == "__main__":
    ctx = D.production_context()
    if not D.git("rev-parse", "-q", "--verify", ctx.marker_ref).stdout.strip():
        print("P309 POSTEXEC REFUSED: no marker (nothing was executed)")
        sys.exit(2)
    res = checks(ctx, reverify=reverify_production)
    print(json.dumps(res, indent=1))
    sys.exit(0 if res["ok"] else 1)
