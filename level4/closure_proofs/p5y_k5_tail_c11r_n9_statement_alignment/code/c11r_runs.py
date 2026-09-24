"""C11R Phase 14 -- target execution under the frozen policy. Revision 5.

REVISION 5 (review round 5; errata E39, E41, E44). R5-1: revision 4's closing instruction "set the
guard back to DENY" could only be carried out by deleting the authorization -- the evidence the
comparator verifies -- so following it made a valid run EXECUTION_INVALID. Execution PERMISSION
is now a separate record (c11r_contract.LIFECYCLE): `begin_execution` turns the committed GRANT
into DENY/EXECUTION_STARTED on disk BEFORE any science, `finish_execution` writes the runs artifact
and DENY/EXECUTION_COMPLETED bound to its digest, and NEXT_STEPS tells the operator to commit the
two together (the seal) and to leave the authorization untouched. N5-3: after the pre-flight the
runner loads the policy and the statement table through `load_verified_inputs`, which recomputes
their digests from the bytes it will use and re-derives the configuration from those bytes; the
run records the recomputed digests, never a stored field. N5-11: the certificate each target must
cite is the frozen schema's (c11r_schema.TARGET_CERTIFICATE).

NOT RUN BEFORE AN AUTHORIZATION. main() REFUSES at its first step unless the runner pre-flight
(c11r_contract.runner_preflight) passes. REVISION 4 (review round 3, R3-1; erratum E25): revision 3
checked only that the authorization's stored hash FIELDS equalled the policy's and table's stored
hash FIELDS, and bound only this module's own hash -- a policy edited in place passed. The
pre-flight now RECOMPUTES, independently of the authorization, the execution contract from bytes,
requires every frozen path to be byte-identical to the approved commit and untouched since,
verifies the gate, the qualification and the authorization against the recomputed identities,
requires every module of the bound code closure (this runner, the certifiers, the reconstruction
and guards included) to be the bound version, and refuses if another campaign worker is running
-- all BEFORE any target computation. The recomputed identity is recorded in the runs artifact
(`execution_identity`) for the comparator to check again. No authorization exists, so an
accidental run -- the erratum E1 lapse -- stops before touching anything.

It reads no original magnitude: only the statement table (semantics) and the frozen policy.

REVISION 3 (blockers B-3, B-4). Every certificate is built by c11r_certificate.make_certificate and
records FACTS -- the certifier, its hash, its exact inputs and the certifier's own result. A target
record carries a constant, a status, a value and the certificate it cites, and NO declared
statement. `assemble` takes each target's value from c11r_certificate.reconstruct -- what the
certificate proves -- never from the selector's bookkeeping, and then runs every production guard
over the finished artifact before it is written. The guard results are sealed with it, pass or
fail; the comparator re-evaluates them independently after the seal.

WHAT main() DOES, exactly as config/C11R_POLICY.json freezes it:
  1  pointwise coefficients on the 15x15 grid of R over cell 306's block (the cheap screen);
  2  one box-data pass at the frozen configuration -- upper coefficients (K_e and Khat_e together)
     and lower coefficients (the sub-solution route);
  3  exact selection in each family: min A for F_K and F_H, max alpha for F_D (ruled legitimate by
     review round 2, judgement A);
  4  each selected member is screened pointwise (G10), and only a member that passes is certified:
     F_K and F_H by the REVIEWED supersolution_margin_iv, F_D by subsolution_margin_iv;
  5  targets assembled from the reconstructions, guards evaluated, artifact written; then STOP.
     No escalation, no retry. The resource cap is checked before every stage and every
     certification; a certification already running is NOT interrupted, so the wall clock can
     exceed the cap by the duration of that one certification (review 4, N4-9). "No retry" is
     enforced against COMMITTED runs (c11r_contract.protocol_history refuses a second one anywhere
     in reachable history); a run never committed is invisible to git and is excluded by the
     protocol and the pre-flight's process detector, not proved absent.
"""
from __future__ import annotations

import json
import pathlib
import resource
import sys
import time
from fractions import Fraction as F

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import c11r_boxdata as BD
import c11r_certificate as CV
import c11r_common as C
import c11r_contract as CT
import c11r_idrift as I
import c11r_schema as S

X, G = I.X, I.G
TARGET_MAP = S.TARGET_CERTIFICATE             # the frozen citation rule (review 5, N5-11)
# What the operator does after the runner exits -- printed verbatim, and followed literally by
# the chain controls (review 5, R5-1).
NEXT_STEPS = (
    f"commit {CT.RUNS_REL} and {CT.PERMISSION_REL} TOGETHER, in ONE commit: that commit is the "
    f"seal",
    f"do NOT modify, remove or re-commit {CT.AUTH_REL}: it is immutable evidence the comparator "
    f"verifies",
    "execution permission is now DENY (EXECUTION_COMPLETED); nothing re-enables execution under "
    "this approved commit",
    "then run: c11r_compare.py --approved-commit <the approved commit, full 40-hex id>")
NOT_IMPLEMENTED_REASON = (
    "PROSPECTIVELY_REACHABLE_BUT_NOT_IMPLEMENTED: requires the drift-derivative kernels Khat' and "
    "Khat'', h_1' and h_1'', operator norm bounds kernel_norm(0..3), a residual-to-error "
    "propagation argument consuming this campaign's own C_T and tau, and independent candidates "
    "for d' and d''")


def _rss_mb() -> float:
    r = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return r / (1024 * 1024) if sys.platform == "darwin" else r / 1024


def preflight(repo=None, *, allow_fixture=False, check_processes=True) -> dict:
    """The runner's own pre-flight: the production chain check, run HERE, before any science.
    It does not rely on the authorization having checked anything (defence in depth)."""
    return CT.runner_preflight(repo, allow_fixture=allow_fixture, check_processes=check_processes)


def begin_execution(repo, identity: dict) -> dict:
    """AUTHORIZED -> EXECUTING, before any science: the permission on disk becomes
    DENY/EXECUTION_STARTED, ending the committed GRANT. A second invocation -- after a crash, or
    concurrently -- finds no GRANT on disk and its pre-flight refuses; the authorization is not
    touched."""
    grant = CT.load_artifact(repo, CT.PERMISSION_REL)
    if grant.get("transition") != "GRANT":
        raise SystemExit("REFUSE: execution permission on disk is not the GRANT")
    rec = CT.permission_record("EXECUTION_STARTED", approved_commit=identity["approved_commit"],
                               authorization_sha256=identity["authorization_sha256"],
                               grant_sha256=CT.body_digest(grant),
                               fixture=bool(grant.get("fixture")))
    CT.write_record(repo, CT.PERMISSION_REL, rec)
    return rec


def finish_execution(repo, runs_body: dict) -> dict:
    """EXECUTING -> EXECUTED_UNSEALED: write the runs artifact (the evidence body, exactly as
    write_evidence writes it) and DENY/EXECUTION_COMPLETED bound to its body digest."""
    started = CT.load_artifact(repo, CT.PERMISSION_REL)
    if started.get("transition") != "EXECUTION_STARTED":
        raise SystemExit("REFUSE: no execution in progress (permission is not EXECUTION_STARTED)")
    path = CT._root(repo) / C.NS_REL / CT.RUNS_REL
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(runs_body, indent=1, sort_keys=True) + "\n")
    rec = CT.permission_record("EXECUTION_COMPLETED", approved_commit=started["approved_commit"],
                               authorization_sha256=started["authorization_sha256"],
                               grant_sha256=started["grant_sha256"],
                               runs_sha256=CT.body_digest(runs_body),
                               fixture=bool(started.get("fixture")))
    CT.write_record(repo, CT.PERMISSION_REL, rec)
    return rec


def load_verified_inputs(repo, identity: dict) -> dict:
    """The policy and the statement table the run will USE, verified from THOSE bytes (review 5,
    N5-3): their body digests recomputed and equal to the pre-flight's recomputed identity (the
    contract's), their stored sha256 fields equal to the recomputed digests, and the
    configuration re-derived from the policy bytes equal to the bound one. Returns the documents
    and the recomputed identity, or the problems."""
    p = []

    def read(rel):
        raw = CT.artifact_bytes(repo, rel)               # read ONCE: these are the bytes in use
        if CT._root(repo).resolve() == C.REPO.resolve():
            C._READS[CT.ns_path(rel)] = C.sha256_bytes(raw)   # bound in the runs provenance
        return json.loads(raw)
    policy = read(CT.POLICY_REL)
    stmt = read(CT.STMT_REL)
    pol_d, st_d = CT.body_digest(policy), CT.body_digest(stmt)
    if pol_d != identity["policy_sha256"]:
        p.append("runner inputs: the policy bytes in use are not the pre-flight's (recomputed "
                 "digest differs)")
    if st_d != identity["statements_sha256"]:
        p.append("runner inputs: the statement table in use is not the pre-flight's")
    if policy.get("sha256") != pol_d or stmt.get("sha256") != st_d:
        p.append("runner inputs: a stored sha256 field does not equal the recomputed digest of "
                 "the bytes in use")
    cfg = policy.get("configuration", {})
    used = {"depth": cfg.get("chosen", {}).get("depth"), "panels": cfg.get("chosen", {}).get("panels"),
            "cap_seconds": cfg.get("cap_seconds"), "cap_rss_mb": cfg.get("cap_rss_mb"),
            "safety_factor": cfg.get("safety_factor"), "rule": cfg.get("rule")}
    if used != identity["configuration"]:
        p.append("runner inputs: the configuration derived from the policy bytes in use is not "
                 "the bound one")
    if policy.get("statements_sha256") != st_d:
        p.append("runner inputs: the policy was frozen against a different statement table")
    return {"problems": p, "policy": policy, "stmt": stmt,
            "recomputed": {"policy_sha256": pol_d, "statements_sha256": st_d}}


def assemble(*, policy: dict, stmt: dict, certs: dict, stop_reason, extra: dict,
             producer_sha256: str | None = None, expected_certifier_sha: dict | None = None,
             deductions: dict | None = None, identity: dict | None = None) -> dict:
    """Build the runs artifact from certificates. The ONLY emission path.

    main() calls it with real certificates; the mutation suite calls it with certificates built by
    the same c11r_certificate.make_certificate, so every mutant exercises exactly the structure and
    the guards a real run produces.
    """
    me = {"module": "c11r_runs.py",
          "sha256": producer_sha256 or C.sha256_file(pathlib.Path(__file__))}
    exp = expected_certifier_sha or CV.certifier_hashes()
    recon = {cid: CV.reconstruct(c, expected_certifier_sha=exp, runs_producer=me,
                                 deductions=deductions)
             for cid, c in certs.items()}
    implementable = set(policy["target_scope"]["implementable_under_this_policy"])
    targets = {}
    for k in S.SIX_CONSTANTS:
        if k not in implementable:
            targets[k] = S.target(k, status="NOT_IMPLEMENTED", value=None,
                                  reason=NOT_IMPLEMENTED_REASON, certificate_id=None)
            continue
        cid = TARGET_MAP[k]
        r = recon.get(cid)
        if r is not None and not r["problems"] and k in r["values"]:
            targets[k] = S.target(k, status="CERTIFIED", value=r["values"][k], reason=None,
                                  certificate_id=cid)
        else:
            why = (stop_reason or (f"certificate {cid} proves nothing: {r['problems']}"
                                   if r is not None else f"no certificate {cid}"))
            targets[k] = S.target(k, status="NOT_CERTIFIED", value=None, reason=why,
                                  certificate_id=cid if cid in certs else None)
    d = stmt["drift_domain"]
    # the RECOMPUTED digests of the documents in use, never their stored fields (review 5, N5-3)
    runs = S.emit_runs(policy_sha256=CT.body_digest(policy), statements_sha256=CT.body_digest(stmt),
                       drift_block=(d["e_lo"], d["e_hi"]), certificates=certs, targets=targets,
                       identity=identity or S.NO_IDENTITY,
                       extra=dict(extra, stop_reason=stop_reason))
    ev = CV.evaluate_run(runs, policy, expected_certifier_sha=exp, runs_producer=me,
                         deductions=deductions)
    runs["self_check"] = {"ALL_GUARDS_PASS": ev["ALL_GUARDS_PASS"], "G8": ev["G8"],
                          "G10": ev["G10"], "G19": ev["G19"], "value_trace": ev["value_trace"],
                          "reconstructions": ev["reconstructions"]}
    return runs


def main() -> int:
    t0 = time.time()
    pf = preflight(C.REPO)
    if pf["problems"]:
        print("REFUSE: target execution is not authorised by the recomputed chain.")
        for b in pf["problems"]:
            print(f"  - {b}")
        return 2
    identity = pf["identity"]
    vi = load_verified_inputs(C.REPO, identity)          # N5-3: verify the bytes in use
    if vi["problems"]:
        print("REFUSE: the inputs in use are not the verified ones.")
        for b in vi["problems"]:
            print(f"  - {b}")
        return 2
    policy, stmt = vi["policy"], vi["stmt"]
    begin_execution(C.REPO, identity)                    # AUTHORIZED -> EXECUTING, before science

    e_lo, e_hi = F(stmt["drift_domain"]["e_lo"]), F(stmt["drift_domain"]["e_hi"])
    E = I.Blk(e_lo, e_hi)
    cfg = policy["configuration"]
    D, P = cfg["chosen"]["depth"], cfg["chosen"]["panels"]
    cap_s, cap_mb = cfg["cap_seconds"], cfg["cap_rss_mb"]
    sel = policy["selector"]
    grid, b_max, beta_max = sel["grid"], F(sel["b_max"]), F(sel["beta_max"])
    mu = F(1, 2 ** 60)
    timings, stop_reason, certs, sel_detail = {}, None, {}, {}

    def over_cap():
        return (time.time() - t0) > cap_s or _rss_mb() > cap_mb

    def cert(cid, family, w, ar, module, function, result, screen, sent, secs):
        return CV.make_certificate(cid=cid, family=family, w=w, drift_block=(e_lo, e_hi),
                                   depth=D, panels=P, atom_removed=ar, certifier_module=module,
                                   certifier_function=function, result=result, screen=screen,
                                   sent=sent, seconds=secs)

    with BD.PhiCache():
        t = time.time()
        pw = [BD.pointwise_coeffs(p, m, E) for (p, m) in BD.pointwise_grid(cfg["screen_grid"])]
        timings["pointwise"] = round(time.time() - t, 1)

        boxes = X.cover(D)
        t = time.time()
        upper, lower = [], []
        for bx in boxes:
            if over_cap():
                stop_reason = "RESOURCE_CAP during the box-data pass"
                break
            upper.append(BD.box_upper_coeffs(*bx, E, P))
            lower.append(BD.box_lower_coeffs(*bx, E, P))
        timings["box_data"] = round(time.time() - t, 1)

        for cid, key, ar in (("F_K", "K", False), ("F_H", "H", True)):
            fam = "w = A - B*m"
            if stop_reason or over_cap():
                stop_reason = stop_reason or f"RESOURCE_CAP before certifying {cid}"
                certs[cid] = cert(cid, fam, {}, ar, "c11r_idrift.py", "supersolution_margin_iv",
                                  None, "NOT_REACHED", False, 0.0)
                continue
            s = BD.select_upper(upper, key, grid=grid, b_max=b_max, mu=mu)
            sel_detail[cid] = {k: str(v) for k, v in s.items()}
            if not s["feasible"]:
                certs[cid] = cert(cid, fam, {}, ar, "c11r_idrift.py", "supersolution_margin_iv",
                                  None, "NOT_REACHED", False, 0.0)
                continue
            w = {(0, 0): s["A"], (0, 1): -s["B"]}
            if min(BD.pointwise_upper_hi(c, key, s["A"], s["B"]) for c in pw) < 0:
                certs[cid] = cert(cid, fam, w, ar, "c11r_idrift.py", "supersolution_margin_iv",
                                  None, "POINTWISE_INFEASIBLE", False, 0.0)
                continue
            t = time.time()
            r = I.supersolution_margin_iv(w, E, depth=D, panels=P, atom_removed=ar)
            certs[cid] = cert(cid, fam, w, ar, "c11r_idrift.py", "supersolution_margin_iv", r,
                              "POINTWISE_FEASIBLE", True, round(time.time() - t, 1))

        fam = "u = alpha + beta*m"
        if not stop_reason and over_cap():
            stop_reason = "RESOURCE_CAP before certifying F_D"
        if stop_reason:
            certs["F_D"] = cert("F_D", fam, {}, True, "c11r_boxdata.py", "subsolution_margin_iv",
                                None, "NOT_REACHED", False, 0.0)
        else:
            s = BD.select_lower(lower, grid=grid, beta_max=beta_max, mu=mu)
            sel_detail["F_D"] = {k: str(v) for k, v in s.items()}
            u = {(0, 0): s["alpha"], (0, 1): s["beta"]} if s.get("alpha") is not None else {}
            if not s["feasible"]:
                certs["F_D"] = cert("F_D", fam, u, True, "c11r_boxdata.py",
                                    "subsolution_margin_iv", None, "NOT_REACHED", False, 0.0)
            elif min(BD.pointwise_lower_hi(c, s["alpha"], s["beta"]) for c in pw) < 0:
                certs["F_D"] = cert("F_D", fam, u, True, "c11r_boxdata.py",
                                    "subsolution_margin_iv", None, "POINTWISE_INFEASIBLE",
                                    False, 0.0)
            else:
                t = time.time()
                r = BD.subsolution_margin_iv(u, E, D, P)
                certs["F_D"] = cert("F_D", fam, u, True, "c11r_boxdata.py",
                                    "subsolution_margin_iv", r, "POINTWISE_FEASIBLE", True,
                                    round(time.time() - t, 1))

    runs = assemble(policy=policy, stmt=stmt, certs=certs, stop_reason=stop_reason,
                    identity=identity,
                    extra={"configuration": {"depth": D, "panels": P, "boxes": len(boxes)},
                           "timings_seconds": timings, "selection_detail": sel_detail,
                           "peak_rss_mb": round(_rss_mb(), 1),
                           "total_seconds": round(time.time() - t0, 1)})
    body = C.evidence_body(runs, producer=__file__)      # exactly what write_evidence writes
    finish_execution(C.REPO, body)                       # EXECUTING -> EXECUTED_UNSEALED
    print(f"wrote {CT.RUNS_REL} sha256 {body['sha256'][:16]}...  "
          f"self-check guards pass: {runs['self_check']['ALL_GUARDS_PASS']}")
    print(f"wrote {CT.PERMISSION_REL}: execution permission DENY (EXECUTION_COMPLETED)")
    print("NEXT:")
    for step in NEXT_STEPS:
        print(f"  - {step}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
