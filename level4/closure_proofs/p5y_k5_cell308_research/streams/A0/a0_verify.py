"""Stream A0: RE-VERIFICATION of a stored pointwise certificate WITHOUT the float proposal (condition C1 of
REVIEW_C2B_STRATEGY_R1; task C3).

``verify_certificate(cert)`` is the ONE verification function.  It uses only the stored exact object:

  C2B_P1_SUPER    nodal integers W (scale 2^-Qbits), mesh N, drift e  ->  pinned c2b_exact.certify(Setup(N, e), W)
  C2B_P1_SUB      same data                                           ->  a0_c2b.sub_certify(Setup(N, e), W)
  C1B_PW_W_SUPER  strip polynomials with exact dyadic coefficients    ->  pinned c1b_certpw.check_supersolution(
                                                                           Ctx(e, BW), W, whole=True)

and PASSES iff (i) the stored sha256 matches the canonical serialisation of W, (ii) the object shape is the declared
one, (iii) the certificate inequality is certified by the exact checker, and (iv) the exact value at the atom equals
the stored claim.  No float, no proposal, no selection is involved.  The drift is validated first (declared drift +
both quarantine guards).

CLI:  python3 -I -B -S a0_verify.py CERTFILE [CERTFILE ...]
"""
from __future__ import annotations

import json
import sys
import time
from fractions import Fraction as F
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import a0_common as A  # noqa: E402


def _fail(reason, **kw):
    return {"verdict": "FAIL", "reason": reason, **kw}


def verify_certificate(cert: dict) -> dict:
    t0 = time.process_time()
    kind = cert.get("certifier")
    e = A.declared_drift(F(cert["drift"]))
    claim = F(cert["claim_w_atom"])
    if kind in ("C2B_P1_SUPER", "C2B_P1_SUB"):
        import a0_c2b as C2
        try:
            W = [[int(x) for x in col] for col in cert["W"]]
        except (TypeError, ValueError):
            return _fail("W_NOT_INTEGER")
        if C2.w_sha256(W) != cert["W_sha256"]:
            return _fail("W_SHA256_MISMATCH")
        if cert.get("kind") != "whole":
            return _fail("KIND_NOT_WHOLE")
        EX = A.load_c2b()["c2b_exact"]
        S = EX.Setup(int(cert["N"]), e)
        if len(W) != len(S.mesh.cols) or any(len(W[i]) != c for i, c in enumerate(S.mesh.cols)):
            return _fail("W_SHAPE_MISMATCH")
        Qb = int(cert["Qbits"])
        res = EX.certify(S, W, Qb, True) if kind == "C2B_P1_SUPER" else C2.sub_certify(S, W, Qb, True)
        detail = {k: res.get(k) for k in ("certified", "failing_cells", "cells_checked", "min_slack_float", "reason")}
        if not res["certified"]:
            return _fail("CERTIFICATE_INEQUALITY_NOT_CERTIFIED", detail=detail,
                         cpu_seconds=round(time.process_time() - t0, 2))
        if F(res["w_atom"]) != claim:
            return _fail("CLAIM_MISMATCH", detail=detail)
        return {"verdict": "PASS", "certifier": kind, "drift": A.fs(e), "bound": A.fs(claim),
                "direction": "upper" if kind == "C2B_P1_SUPER" else "lower", "detail": detail,
                "cpu_seconds": round(time.process_time() - t0, 2)}
    if kind in ("C1B_PW_W_SUPER", "C1B_PW_W_SUPER_HULL"):
        import a0_c1b as C1
        Wser = cert["W"]
        if C1.w_sha256(Wser) != cert["W_sha256"]:
            return _fail("W_SHA256_MISMATCH")
        M = A.load_c1b(tight_ct=True, block_light=False)
        cp, PW = M["c1b_certpw"], M["c1b_pw"]
        if tuple(cert["BW"]) != tuple(PW.BW_PW) or len(Wser) != len(PW.BW_PW) - 1:
            return _fail("BW_OR_SHAPE_MISMATCH")
        W = [C1.poly_de(L) for L in Wser]
        lines: list = []
        if kind == "C1B_PW_W_SUPER_HULL":
            import a0_c1bh as H
            lo, hi = (F(x) for x in cert["hull"])
            if (lo, hi) != H.hull_of(e):
                return _fail("HULL_NOT_THE_DECLARED_DYADIC_HULL")
            A.C.guard_drift(lo, hi)
            A._OVQ.guard_drift(lo, hi)
            cx = cp.Ctx((lo + hi) / 2, PW.BW_PW, lines.append, (hi - lo) / 2)
        else:
            cx = cp.Ctx(e, PW.BW_PW, lines.append)
        try:
            sW = cp.check_supersolution(cx, W, True, "W")
        except ValueError as exc:                       # e.g. non-dyadic coefficients: the pinned checker refuses
            return _fail("CHECKER_REFUSED_INPUT", detail={"error": str(exc)[:120]},
                         cpu_seconds=round(time.process_time() - t0, 2))
        detail = {"certified": sW["certified"], "residual_lo": float(sW["residual_lo"]),
                  "w_min_lo": float(sW["w_min_lo"]), "boxes": sW["boxes"]}
        if not sW["certified"]:
            return _fail("CERTIFICATE_INEQUALITY_NOT_CERTIFIED", detail=detail,
                         cpu_seconds=round(time.process_time() - t0, 2))
        if cp.at_atom(W) != claim:
            return _fail("CLAIM_MISMATCH", detail=detail)
        return {"verdict": "PASS", "certifier": kind, "drift": A.fs(e), "bound": A.fs(claim), "direction": "upper",
                "detail": detail, "cpu_seconds": round(time.process_time() - t0, 2)}
    return _fail("UNKNOWN_CERTIFIER")


def verify_file(path: Path) -> dict:
    raw = path.read_bytes()
    out = verify_certificate(json.loads(raw))
    out["file"] = path.name
    out["file_sha256"] = A.sha256_bytes(raw)
    return out


if __name__ == "__main__":
    argv = list(sys.argv[1:])
    out_tag = None
    if "--out" in argv:
        i = argv.index("--out")
        out_tag = argv[i + 1]
        del argv[i:i + 2]
    rows = []
    for p in argv:
        rows.append(verify_file(Path(p)))
        r = rows[-1]
        print(json.dumps({k: r[k] for k in ("file", "verdict") if k in r} | {"reason": r.get("reason")}), flush=True)
    if out_tag:
        A.write_json(A.RESULTS / f"C3_REVERIFY_{out_tag}.json",
                     {"schema": "A0_C3_REVERIFY/1", "rows": rows, "n": len(rows),
                      "all_pass": bool(rows) and all(r["verdict"] == "PASS" for r in rows),
                      "code": {"a0": A.own_code_sha256()}})
        A.ledger("a0_verify.py", f"stream C C3 re-verification of stored certificates ({out_tag}, {len(rows)} files)",
                 notes="exact re-check without the float proposal; declared validation drifts only")
    sys.exit(0 if rows and all(r["verdict"] == "PASS" for r in rows) else 1)
