"""C11R Phase 14 -- target execution under the frozen policy. Revision 3.

NOT RUN BEFORE AN AUTHORIZATION. main() REFUSES at its first step unless
config/C11R_AUTHORIZATION.json exists with guard ALLOW, bound to cell 306 and to the exact policy,
statement table and this module's own hash. No such artifact exists, so an accidental run -- the
erratum E1 lapse -- stops before touching anything.

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
     No escalation, no retry. The resource cap is enforced before every certification.
"""
from __future__ import annotations

import pathlib
import resource
import sys
import time
from fractions import Fraction as F

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import c11r_boxdata as BD
import c11r_certificate as CV
import c11r_common as C
import c11r_idrift as I
import c11r_schema as S

X, G = I.X, I.G
AUTH = C.NS / "config" / "C11R_AUTHORIZATION.json"
TARGET_MAP = {"Abar": "F_K", "tau": "F_H", "C_T": "F_H", "D_lo": "F_D"}
NOT_IMPLEMENTED_REASON = (
    "PROSPECTIVELY_REACHABLE_BUT_NOT_IMPLEMENTED: requires the drift-derivative kernels Khat' and "
    "Khat'', h_1' and h_1'', operator norm bounds kernel_norm(0..3), a residual-to-error "
    "propagation argument consuming this campaign's own C_T and tau, and independent candidates "
    "for d' and d''")


def _rss_mb() -> float:
    r = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return r / (1024 * 1024) if sys.platform == "darwin" else r / 1024


def authorised(policy: dict, stmt: dict) -> list[str]:
    """Problems preventing execution. Empty means Phase 13 authorised exactly this run."""
    a = C.load(AUTH) if AUTH.exists() else None
    return check_authorization(a, policy, stmt, C.sha256_file(pathlib.Path(__file__)))


def check_authorization(a: dict | None, policy: dict, stmt: dict, self_sha: str) -> list[str]:
    """Pure: testable with a synthetic authorization, so no real one ever has to be written."""
    if a is None:
        return ["no Phase 13 authorization artifact exists; guard is DENY"]
    p = []
    if a.get("guard") != "ALLOW":
        p.append(f"guard is {a.get('guard')!r}")
    if a.get("cell") != 306:
        p.append(f"authorization names cell {a.get('cell')!r}, not 306")
    if a.get("policy_sha256") != policy["sha256"]:
        p.append("authorization is not bound to this policy")
    if a.get("statements_sha256") != stmt["sha256"]:
        p.append("authorization is not bound to this statement table")
    if a.get("runs_producer_sha256") != self_sha:
        p.append("authorization is not bound to this producer's hash")
    return p


def assemble(*, policy: dict, stmt: dict, certs: dict, stop_reason, extra: dict,
             producer_sha256: str | None = None, expected_certifier_sha: dict | None = None,
             deductions: dict | None = None) -> dict:
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
    runs = S.emit_runs(policy_sha256=policy["sha256"], statements_sha256=stmt["sha256"],
                       drift_block=(d["e_lo"], d["e_hi"]), certificates=certs, targets=targets,
                       extra=dict(extra, stop_reason=stop_reason))
    ev = CV.evaluate_run(runs, policy, expected_certifier_sha=exp, runs_producer=me,
                         deductions=deductions)
    runs["self_check"] = {"ALL_GUARDS_PASS": ev["ALL_GUARDS_PASS"], "G8": ev["G8"],
                          "G10": ev["G10"], "G19": ev["G19"], "value_trace": ev["value_trace"],
                          "reconstructions": ev["reconstructions"]}
    return runs


def main() -> int:
    t0 = time.time()
    policy = C.load(C.NS / "config" / "C11R_POLICY.json")
    stmt = C.load(C.NS / "evidence" / "table" / "C11R_N9_STATEMENTS.json")
    blocked = authorised(policy, stmt)
    if blocked:
        print("REFUSE: target execution is not authorised.")
        for b in blocked:
            print(f"  - {b}")
        return 2
    if policy["statements_sha256"] != stmt["sha256"]:
        raise SystemExit("REFUSE: the policy was frozen against a different statement table")

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
                    extra={"configuration": {"depth": D, "panels": P, "boxes": len(boxes)},
                           "timings_seconds": timings, "selection_detail": sel_detail,
                           "peak_rss_mb": round(_rss_mb(), 1),
                           "total_seconds": round(time.time() - t0, 1)})
    s = C.write_evidence(C.NS / "evidence" / "runs" / "C11R_RUNS.json", runs, producer=__file__)
    print(f"wrote evidence/runs/C11R_RUNS.json sha256 {s[:16]}...  "
          f"self-check guards pass: {runs['self_check']['ALL_GUARDS_PASS']}")
    print("NEXT: commit this artifact to seal it, set the guard back to DENY, and only then run "
          "c11r_compare.py.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
