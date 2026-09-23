"""C11R Phase 14 -- target execution under the frozen policy. Rebuilt in revision 2.

NOT RUN BEFORE READY_TO_FREEZE. This module REFUSES unless config/C11R_AUTHORIZATION.json exists
with guard ALLOW, bound to the exact policy, statement table and this module's own hash. No such
artifact exists before the Phase 13 authorization, so an accidental run -- the erratum E1 lapse --
stops at the first line of main().

It reads no original magnitude: only the statement table (semantics) and the policy. It writes its
result through c11r_schema.emit_runs, the single constructor every verifier also uses.

WHAT IT DOES, exactly as config/C11R_POLICY.json freezes it:
  1  pointwise coefficients on the 15x15 grid of R over cell 306's block (the cheap screen);
  2  one box-data pass at the frozen configuration -- upper coefficients (K_e and Khat_e together)
     and lower coefficients (the sub-solution route);
  3  exact selection in each family: min A for F_K and F_H, max alpha for F_D;
  4  each selected member is screened pointwise (G10), and only a member that passes is certified:
     F_K and F_H by the REVIEWED supersolution_margin_iv, F_D by subsolution_margin_iv;
  5  targets written under the frozen schema; then STOP. No escalation, no retry.
"""
from __future__ import annotations

import pathlib
import resource
import sys
import time
from fractions import Fraction as F

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import c11r_boxdata as BD
import c11r_common as C
import c11r_idrift as I
import c11r_schema as S

X, G = I.X, I.G
AUTH = C.NS / "config" / "C11R_AUTHORIZATION.json"


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


def assemble(*, policy: dict, stmt: dict, e_lo: F, e_hi: F, D: int, P: int, n_boxes: int,
             certs: dict, selected: dict, stop_reason, timings: dict, total_seconds: float,
             peak_rss_mb: float, producer_sha256: str | None = None) -> dict:
    """Build the runs artifact from computed results. The ONLY emission path.

    main() calls it with real results; the mutation suite calls it with synthetic ones, so the
    mutants exercise exactly the structure a real run writes (erratum E7).
    """
    me = {"module": "c11r_runs.py",
          "file_sha256": producer_sha256 or C.sha256_file(pathlib.Path(__file__))}
    drift = (str(e_lo), str(e_hi))
    single = {"method": "single_certificate_whole_block", "sub_blocks": 1}

    def tgt(constant, cid, value, route):
        ok = cid in certs and certs[cid]["certified"] and value is not None
        if not ok:
            return S.target(constant, status="NOT_CERTIFIED", value=None, stmt=None,
                            reason=stop_reason or f"certificate {cid} did not certify",
                            certificate_id=cid if cid in certs else None)
        st = S.statement(constant, drift_domain=drift, aggregation=single, dependencies=(),
                         producer=dict(me, route=route, certificate_id=cid))
        return S.target(constant, status="CERTIFIED", value=value, stmt=st, reason=None,
                        certificate_id=cid)

    sK, sH, sD = selected.get("F_K", {}), selected.get("F_H", {}), selected.get("F_D", {})
    sup_H = None
    if "w" in sH:
        sup_H = max(X.poly_eval_iv(sH["w"], G.Iv(a, b), G.Iv(c, d)).hi
                    for (a, b, c, d) in X.cover(D))
    not_impl = ("PROSPECTIVELY_REACHABLE_BUT_NOT_IMPLEMENTED: requires the drift-derivative "
                "kernels Khat' and Khat'', h_1' and h_1'', operator norm bounds kernel_norm(0..3), "
                "a residual-to-error propagation argument consuming this campaign's own C_T and "
                "tau, and independent candidates for d' and d''")
    targets = {
        "Abar": tgt("Abar", "F_K", sK.get("A"), "independent_supersolution"),
        "tau": tgt("tau", "F_H", sH.get("A"), "independent_supersolution"),
        "C_T": tgt("C_T", "F_H", sup_H, "independent_supersolution"),
        "D_lo": tgt("D_lo", "F_D", sD.get("alpha"), "independent_subsolution"),
        "D1": S.target("D1", status="NOT_IMPLEMENTED", value=None, stmt=None, reason=not_impl,
                       certificate_id=None),
        "D2": S.target("D2", status="NOT_IMPLEMENTED", value=None, stmt=None, reason=not_impl,
                       certificate_id=None),
    }
    consistency = {
        "Abar_ge_tau": (None if not (sK.get("A") and sH.get("A")) else sK["A"] >= sH["A"]),
        "F_K_A_ge_pointwise_min": (None if "A" not in sK or sK.get("pointwise_A_min") is None
                                   else sK["A"] >= sK["pointwise_A_min"]),
        "F_H_A_ge_pointwise_min": (None if "A" not in sH or sH.get("pointwise_A_min") is None
                                   else sH["A"] >= sH["pointwise_A_min"]),
    }
    return S.emit_runs(
        policy_sha256=policy["sha256"], statements_sha256=stmt["sha256"], drift_block=drift,
        certificates=certs, targets=targets,
        extra={"configuration": {"depth": D, "panels": P, "boxes": n_boxes},
               "timings_seconds": timings, "stop_reason": stop_reason,
               "consistency_checks": consistency,
               "selection_detail": {k: v.get("selector") for k, v in selected.items()},
               "peak_rss_mb": peak_rss_mb, "total_seconds": total_seconds})


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
    timings, stop_reason = {}, None

    def over_cap():
        return (time.time() - t0) > cap_s or _rss_mb() > cap_mb

    with BD.PhiCache():
        # ---- 1. pointwise stage ------------------------------------------------------------
        t = time.time()
        pw = [BD.pointwise_coeffs(p, m, E) for (p, m) in BD.pointwise_grid(cfg["screen_grid"])]
        timings["pointwise"] = round(time.time() - t, 1)

        def pw_upper_min(key):
            best = None
            for j in range(int(b_max * grid) + 1):
                B = F(j, grid)
                need = BD.M_MAX * B
                for c in pw:
                    k1lo = c["K1"][0] - (c["atom1"][1] if key == "H" else 0)
                    h = 1 - k1lo
                    if h <= 0:
                        need = None
                        break
                    need = max(need, (1 - B * (c["Km"][1] - c["m"])) / h)
                if need is not None and (best is None or need < best):
                    best = need
            return best

        # ---- 2. box data -------------------------------------------------------------------
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

        certs, selected = {}, {}
        fams = (("F_K", "K", False, "K_e"), ("F_H", "H", True, "Khat_e"))
        for cid, key, ar, kernel in fams:
            rec = dict(route="independent_supersolution", kernel=kernel, family="w = A - B*m",
                       screen_classification="POINTWISE_FEASIBLE", sent_to_box_pass=False,
                       ladder_level="single", depth=D, panels=P, boxes=len(boxes),
                       selected=None, certified=False, margin_lower_bound=None,
                       w_min_lower_bound=None, seconds=0.0)
            if stop_reason or over_cap():
                # the cap is enforced BEFORE each certification, not only during the data pass,
                # so an overrun stops cleanly as RESOURCE_CAP, as the frozen policy states
                stop_reason = stop_reason or f"RESOURCE_CAP before certifying {cid}"
                certs[cid] = S.certificate(**rec)
                continue
            s = BD.select_upper(upper, key, grid=grid, b_max=b_max, mu=mu)
            if not s["feasible"]:
                certs[cid] = S.certificate(**rec)
                selected[cid] = {"selection": {k: str(v) for k, v in s.items()}}
                continue
            A, B = s["A"], s["B"]
            rec["selected"] = {"A": str(A), "B": str(B)}
            refuted = min(BD.pointwise_upper_hi(c, key, A, B) for c in pw) < 0
            if refuted:
                rec["screen_classification"] = "POINTWISE_INFEASIBLE"
                certs[cid] = S.certificate(**rec)
                continue
            rec["sent_to_box_pass"] = True
            t = time.time()
            w = {(0, 0): A, (0, 1): -B}
            r = I.supersolution_margin_iv(w, E, depth=D, panels=P, atom_removed=ar)
            rec.update(certified=r["certified"], margin_lower_bound=str(r["margin_lower_bound"]),
                       w_min_lower_bound=str(r["w_min_lower_bound"]),
                       seconds=round(time.time() - t, 1))
            certs[cid] = S.certificate(**rec)
            selected[cid] = {"A": A, "B": B, "w": w,
                             "pointwise_A_min": pw_upper_min(key),
                             "selector": {k: str(v) for k, v in s.items()}}

        # F_D, the sub-solution route
        rec = dict(route="independent_subsolution", kernel="Khat_e", family="u = alpha + beta*m",
                   screen_classification="POINTWISE_FEASIBLE", sent_to_box_pass=False,
                   ladder_level="single", depth=D, panels=P, boxes=len(boxes), selected=None,
                   certified=False, margin_lower_bound=None, w_min_lower_bound=None, seconds=0.0)
        if not stop_reason and over_cap():
            stop_reason = "RESOURCE_CAP before certifying F_D"
        if not stop_reason:
            s = BD.select_lower(lower, grid=grid, beta_max=beta_max, mu=mu)
            if s["feasible"]:
                al, be = s["alpha"], s["beta"]
                rec["selected"] = {"alpha": str(al), "beta": str(be)}
                if min(BD.pointwise_lower_hi(c, al, be) for c in pw) < 0:
                    rec["screen_classification"] = "POINTWISE_INFEASIBLE"
                else:
                    rec["sent_to_box_pass"] = True
                    t = time.time()
                    u = {(0, 0): al, (0, 1): be}
                    r = BD.subsolution_margin_iv(u, E, D, P)
                    rec.update(certified=r["certified"],
                               margin_lower_bound=str(r["margin_lower_bound"]),
                               w_min_lower_bound=str(r["h_min_lower_bound"]),
                               seconds=round(time.time() - t, 1))
                    selected["F_D"] = {"alpha": al, "beta": be, "u": u,
                                       "u_nonnegative": r["u_nonnegative"]}
        certs["F_D"] = S.certificate(**rec)

    runs = assemble(policy=policy, stmt=stmt, e_lo=e_lo, e_hi=e_hi, D=D, P=P,
                    n_boxes=len(boxes), certs=certs, selected=selected,
                    stop_reason=stop_reason, timings=timings,
                    total_seconds=round(time.time() - t0, 1), peak_rss_mb=round(_rss_mb(), 1))
    s = C.write_evidence(C.NS / "evidence" / "runs" / "C11R_RUNS.json", runs, producer=__file__)
    print(f"wrote evidence/runs/C11R_RUNS.json sha256 {s[:16]}...")
    print("NEXT: commit this artifact to seal it, set the guard back to DENY, and only then run "
          "c11r_compare.py.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
