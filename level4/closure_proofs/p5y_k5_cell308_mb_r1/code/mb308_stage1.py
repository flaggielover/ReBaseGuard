"""Cell-308 MB campaign (r1) -- Stage 1 (B3): block RLR rungs, the pointwise Lambda ladder, independent verification.

Frozen rules (design D1-D5, D8; none depends on a target value):
  D1/D2  geometry    the cover [x_lo, x_hi] is split by C2's rule into N equal tiles E_i; B_i = the outward 2^-20 hull of
                     E_i; b_i = lo(B_i) (dyadic, <= lo(E_i)). Computed by the pinned rlr307_stage1 (P1, P2) and
                     cross-checked against the guard's own copy of the rule.
  D3     RLR block   the pinned rlr307_stage1.certify_rung (c1b_certpw.certify_degree on the hull, e-free PW_d
                     candidate, flags TIGHT_CT = BLOCK_LIGHT = True) at every d of LADDER_RLR = (4, 6, 8); the block
                     record is rlr307_stage1.ladder_compose over the CERTIFIED rungs (Lemma Lad), cross-checked exactly
                     against rlr307_independent.ladder / block_supply. No certified rung => no record (members 3/4 absent).
  D4     pointwise   at every b_i: C2b exact-scale rungs N in (20, 40, 80) (upper = pinned c2b_exact.certify, lower =
                     A0 sub_certify) and C1b W-only rungs d in (8, 10, 12) (flags TIGHT_CT = True, BLOCK_LIGHT = False);
                     no early stopping.
  D5     verification each CERTIFIED upper rung's persisted certificate is re-verified by stream VERIFY's
                     independent verifier within a FIXED operation-count budget (VERIFY_BUDGET), with outcome
                     VERIFIED / REFUTED (rigorous witness, or stored claim != W(a)) / UNDECIDED:
                       C2b super -> vd_pl.verify_pl (P1 format), inside the C2B job;
                       C1b       -> vd_verify.verify (strip format) for d <= C1B_VERIFY_MAX_D only; the frozen degrees
                                    8, 10, 12 are NOT_INDEPENDENTLY_VERIFIED (VERIFIER_REPORT D7: infeasible in budget)
                                    and never admitted; they are computed for their Lambda_lo (the cross alarm).
  Admission (REVIEW_A0_CERTIFIER_R1 C2, coordinator notes 3 and 5): an upper rung is admitted only if VERIFIED AND a
  certified lower rung of the OTHER implementation has L_other <= U. REFUTED, or L_other > U for any certified upper
  rung => INCONSISTENT (after the marker: INDETERMINATE). No other-implementation lower rung => ALARM_UNAVAILABLE (not
  admitted). UNDECIDED => not admitted. U_i = min over admitted rungs (see `pointwise`); missing U => no value.
  Rung exceptions raised inside a pinned certifier = rung not certified; MemoryError / OSError / a guard refusal =
  execution failure (a refused admitted object must never silently weaken a member).
"""
from __future__ import annotations

import hashlib
import time
from fractions import Fraction as F

import mb308_a0core as A0C

LADDER_RLR = (4, 6, 8)
LADDER_C2B_N = (20, 40, 80)
LADDER_C1B_D = (8, 10, 12)
DEV_LADDER = {"RLR": (4,), "C2B": (20,), "C1B": (4,)}    # decoy mode only (plumbing / timing); never a frozen rule
RLR_FLAGS = (True, True)                                  # TIGHT_CT, BLOCK_LIGHT for the block rungs (307 rule 3.6)
PW_FLAGS = (True, False)                                  # TIGHT_CT, BLOCK_LIGHT for the pointwise C1b rungs (A0 rule)
FORMAL_LATENT = "formal cell-308 MB certificate; sealed evidence only"
# Independent verification (D5, coordinator note 5; VERIFIER_REPORT D7): the strip verifier cannot verify C1b
# certificates of degree >= 8 within any sensible budget, so C1b upper rungs with d > C1B_VERIFY_MAX_D are recorded
# NOT_INDEPENDENTLY_VERIFIED and never admitted (they are still computed for their Lambda_lo, the cross alarm).
# Fixed per-certificate budgets (operation counts, never wall clock); outcomes VERIFIED / REFUTED(witness) / UNDECIDED.
C1B_VERIFY_MAX_D = 6
VERIFY_BUDGET = {"C2B_PL": {"max_depth": 12, "max_boxes": 10 ** 6},
                 "C1B_STRIP": {"max_boxes": 200000, "min_width": F(1, 2 ** 40)}}


class InfrastructureFailure(RuntimeError):
    """An execution failure (not a scientific non-certificate)."""


def fs(x) -> str:
    x = F(x)
    return f"{x.numerator}/{x.denominator}"


# ------------------------------------------------------------------ geometry (D1, D2)
def plan(S1, guard, x_lo, x_hi) -> list:
    """Blocks by the pinned rlr307_stage1 rules P1/P2, cross-checked against the guard's copy (tiles, hulls, b_i)."""
    blocks = S1.blocks_for(F(x_lo), F(x_hi))
    g = guard.geometry(x_lo, x_hi)
    if len(blocks) != len(g):
        raise ValueError("geometry: block counts differ between rlr307_stage1 and the guard")
    out = []
    for b, h in zip(blocks, g):
        if (b["sub_lo"], b["sub_hi"]) != h["tile"] or (b["hull_lo"], b["hull_hi"]) != h["hull"]:
            raise ValueError("geometry: rlr307_stage1 and the guard disagree")
        out.append({"index": b["index"], "tile": (b["sub_lo"], b["sub_hi"]), "hull": (b["hull_lo"], b["hull_hi"]),
                    "b": b["hull_lo"]})
    if out[0]["tile"][0] != F(x_lo) or out[-1]["tile"][1] != F(x_hi) or any(
            out[i]["tile"][1] != out[i + 1]["tile"][0] for i in range(len(out) - 1)):
        raise ValueError("geometry: the tiles do not tile the cover exactly")
    if any(not out[i]["b"] < out[i + 1]["b"] for i in range(len(out) - 1)) or out[0]["b"] < 0:
        raise ValueError("geometry: the pointwise drifts b_i are not strictly increasing and >= 0")
    return out


def jobs(blocks: list, ladder: dict, which=None) -> list:
    """Phase-A jobs (kind, block, rung), longest expected first; `which` restricts to the listed block indices."""
    idx = [b["index"] for b in blocks if which is None or b["index"] in which]
    js = [("RLR", i, d) for i in idx for d in ladder["RLR"]]
    js += [("C1B", i, d) for i in idx for d in ladder["C1B"]]
    js += [("C2B", i, n) for i in idx for n in ladder["C2B"]]
    weight = {"RLR": 3, "C1B": 2, "C2B": 1}
    return sorted(js, key=lambda j: (-weight[j[0]], -j[2], j[1]))


# ------------------------------------------------------------------ one job (runs in a worker)
def run_job(ctx: dict, kind: str, block: dict, rung: int, payload=None) -> dict:
    """ctx: {"c1b", "c2b", "S1", "vf", "guard", "latent", "set_flags"}; returns an exact, JSON-able record."""
    t0 = time.time()
    base = {"kind": kind, "block": block["index"], "rung": rung}
    try:
        if kind == "RLR":
            ctx["set_flags"](ctx["c1b"], *RLR_FLAGS)
            rec = ctx["S1"].certify_rung(ctx["c1b"], block["hull"][0], block["hull"][1], rung)
            log = rec.pop("_log", [])
            rec["_log_sha256"] = hashlib.sha256("\n".join(log).encode()).hexdigest()
            rec["_log_lines"] = len(log)
            out = {**base, "status": rec.get("status"), "record": rec}
        elif kind == "C1B":
            ctx["set_flags"](ctx["c1b"], *PW_FLAGS)
            r = A0C.c1b_w_rung(ctx["c1b"], ctx["guard"], block["b"], rung, ctx["latent"])
            out = {**base, "status": r["record"]["status"], "record": r["record"], "cert": r["cert"]}
        elif kind == "C2B":
            r = A0C.c2bx_rung(ctx["c2b"], ctx["guard"], block["b"], rung, ctx["latent"])
            out = {**base, "status_U": r["record"]["status_U"], "status_L": r["record"]["status_L"],
                   "record": r["record"],
                   "certs": {k: {x: c[x] for x in ("certifier", "drift", "N", "Qbits", "W_sha256", "claim_w_atom")}
                             | {"cert_sha256": A0C.sha256_bytes(A0C.canon(c))} for k, c in r["certs"].items()},
                   "verification": c2b_verify(ctx, r["certs"].get("super"))}
        elif kind == "VER":
            out = {**base, "verification": verify_c1b(ctx, block["b"], payload)}
        else:
            raise ValueError(f"unknown job kind {kind}")
    except (MemoryError, OSError, InfrastructureFailure, ctx["guard"].QuarantineRefusal):
        raise                                                    # infrastructure / a guard refusal: execution failure
    except Exception as exc:                                     # the pinned certifier raised: rung not certified
        out = {**base, "status": "RUNG_EXCEPTION", "error": f"{type(exc).__name__}: {exc}"[:400]}
        if kind == "VER":
            out["verification"] = {"verdict": "EXCEPTION", "accepted": False, "error": out["error"]}
    out["wall_seconds"] = round(time.time() - t0, 1)
    return out


def _verdict(res: dict, claim_ok: bool) -> str:
    if res["verdict"] == "PASS" and res.get("certified") is True and claim_ok:
        return "VERIFIED"
    if res["verdict"] == "FAIL":
        return "REFUTED"                        # a rigorous witness, or the stored claim is not W(a)
    return "UNDECIDED"


def c2b_verify(ctx: dict, cert) -> dict:
    """D5 for one C2b SUPER certificate: stream VERIFY's independent P1 verifier (vd_pl.verify_pl), serial, within
    VERIFY_BUDGET['C2B_PL']; W(a) must equal the stored claim exactly."""
    if cert is None:
        return {"verdict": "NO_CERTIFICATE", "accepted": False}
    if ctx["vf"] is None or ctx["vf"].get("c2b_pl") is None:
        return {"verdict": "UNVERIFIED", "accepted": False, "reason": "C2B_PL_HOOK absent (fail-closed)"}
    PL = ctx["vf"]["c2b_pl"]
    if cert.get("certifier") != "C2B_P1_SUPER" or cert.get("kind") != "whole":
        return {"verdict": "REFUSED", "accepted": False, "reason": "not a whole-kernel C2b supersolution"}
    try:
        W = PL.from_a0_cert(cert)
    except ValueError as exc:
        return {"verdict": "REFUSED", "accepted": False, "reason": str(exc)[:80]}
    b = VERIFY_BUDGET["C2B_PL"]
    res = PL.verify_pl(W, F(cert["drift"]), direction="super", workers=1, max_depth=b["max_depth"],
                       max_boxes=b["max_boxes"], claim=cert["claim_w_atom"])
    claim_ok = res.get("W_at_atom_equals_claim") is True
    v = _verdict(res, claim_ok)
    return {"verdict": v, "accepted": v == "VERIFIED", "W_at_atom_equals_claim": claim_ok, "boxes": res["boxes"],
            "n_undecided": res["n_undecided"], "seconds": res["seconds"], "sha256_W_verifier": res["sha256_W"],
            "witness": ctx["vf"]["vd"].jsonable(res.get("witness_if_refuted")), "budget": dict(b)}


def verify_c1b(ctx: dict, b, cert: dict) -> dict:
    """D5 for one C1b certificate at the exact drift b (serial verifier, workers = 1)."""
    if F(cert["drift"]) != F(b) or cert.get("certifier") != "C1B_PW_W_SUPER":
        return {"verdict": "REFUSED", "accepted": False, "reason": "certificate drift / kind mismatch"}
    if A0C.c1b_w_sha256(cert["W"]) != cert["W_sha256"]:
        return {"verdict": "REFUSED", "accepted": False, "reason": "W_SHA256_MISMATCH"}
    vd, ad = ctx["vf"]["vd"], ctx["vf"]["adapt"]
    W = ad.from_c1b_raw({"BW": cert["BW"], "W_unscaled": cert["W"], "eta_W": "0/1"})
    bud = VERIFY_BUDGET["C1B_STRIP"]
    res = vd.verify(W, F(b), workers=1, opts={"max_boxes": bud["max_boxes"], "min_width": bud["min_width"]})
    claim_ok = F(res["W_at_atom"]) == F(cert["claim_w_atom"])
    v = _verdict(res, claim_ok) if claim_ok or res["verdict"] != "PASS" else "REFUTED"
    return {"verdict": v, "accepted": v == "VERIFIED", "W_at_atom_equals_claim": claim_ok,
            "sha256_W_verifier": res["sha256_W"], "boxes": res["residual_bb"].get("boxes"),
            "seconds": res["seconds"], "witness": vd.jsonable(res.get("witness_if_refuted")),
            "budget": {"max_boxes": bud["max_boxes"], "min_width": fs(bud["min_width"])}}


# ------------------------------------------------------------------ composition (S1c, S1d)
def pointwise(rungs_c2b: list, rungs_c1b: list, vers: dict) -> dict:
    """U/L at one b_i under the amended D4/D5 rule (REVIEW_A0_CERTIFIER_R1 condition C2; coordinator ruling):
      * an upper rung is ADMITTED only if (i) its persisted certificate passed the independent verifier (C1b now;
        C2b only once the C2B_PL_HOOK exists) and (ii) at least one certified LOWER rung of the OTHER implementation
        exists and L_other <= U (L_C2b = max C2b sub rung; L_C1b = max C1b Lambda_lo);
      * L_other > U for ANY certified upper rung (verified or not) => INCONSISTENT (a cross-implementation soundness
        alarm); within one implementation L <= U holds by construction and is not an alarm;
      * a verified upper rung without any other-implementation lower rung is NOT admitted: ALARM_UNAVAILABLE;
      * an upper rung REFUTED by the independent verifier (a rigorous witness) => INCONSISTENT;
      * C1b upper rungs with d > C1B_VERIFY_MAX_D are NOT_INDEPENDENTLY_VERIFIED, never admitted (coordinator note 5);
      * U = min over admitted rungs; no admitted rung => no U (NOT_CERTIFIED or ALARM_UNAVAILABLE).
    The alarm sensitivity (U - L_other, exact) is recorded for every admitted rung."""
    L_c2b = [F(r["record"]["L"]) for r in rungs_c2b if r.get("status_L") == "CERTIFIED" and r["record"].get("L")]
    L_c1b = [F(r["record"]["L"]) for r in rungs_c1b if r.get("status") == "CERTIFIED" and r["record"].get("L")]
    Lmax = {"C2B": max(L_c2b) if L_c2b else None, "C1B": max(L_c1b) if L_c1b else None}
    other = {"C2B": "C1B", "C1B": "C2B"}
    uppers, refuted = [], []
    for r in rungs_c2b:
        if r.get("status_U") == "CERTIFIED":
            v = r.get("verification", {})
            if v.get("verdict") == "REFUTED":
                refuted.append(f"C2B:N={r['rung']}")
            uppers.append({"impl": "C2B", "rung": f"N={r['rung']}", "U": F(r["record"]["U"]),
                           "verified": bool(v.get("accepted")), "verdict": v.get("verdict")})
    for r in rungs_c1b:
        if r.get("status") == "CERTIFIED":
            if r["rung"] > C1B_VERIFY_MAX_D:
                v = {"verdict": "NOT_INDEPENDENTLY_VERIFIED", "accepted": False}
            else:
                v = vers.get(r["rung"], {"verdict": "NOT_RUN", "accepted": False})
            if v.get("verdict") == "REFUTED":
                refuted.append(f"C1B:d={r['rung']}")
            uppers.append({"impl": "C1B", "rung": f"d={r['rung']}", "U": F(r["record"]["U"]),
                           "verified": bool(v.get("accepted")), "verdict": v.get("verdict")})
    alarms, admitted, unavailable = [], [], []
    for u in uppers:
        lo = Lmax[other[u["impl"]]]
        u["L_other"] = None if lo is None else fs(lo)
        if lo is not None and lo > u["U"]:
            alarms.append(f"{u['impl']}:{u['rung']}")
        if u["verified"]:
            if lo is None:
                unavailable.append(f"{u['impl']}:{u['rung']}")
            elif lo <= u["U"]:
                admitted.append(u)
                u["alarm_sensitivity"] = fs(u["U"] - lo)
    if alarms or refuted:                       # a cross-implementation alarm or a verifier refutation
        status, U = "INCONSISTENT", None
    elif admitted:
        status, U = "CERTIFIED", min(u["U"] for u in admitted)
    else:
        status, U = ("ALARM_UNAVAILABLE" if unavailable else "NOT_CERTIFIED"), None
    Ls = [x for x in (Lmax["C2B"], Lmax["C1B"]) if x is not None]
    return {"status": status, "U": None if U is None else fs(U), "L": fs(max(Ls)) if Ls else None,
            "L_C2B": None if Lmax["C2B"] is None else fs(Lmax["C2B"]),
            "L_C1B": None if Lmax["C1B"] is None else fs(Lmax["C1B"]),
            "U_rungs": [f"{u['impl']}:{u['rung']}" for u in admitted if U is not None and u["U"] == U],
            "uppers": [{k: (fs(v) if isinstance(v, F) else v) for k, v in u.items()} for u in uppers],
            "alarms": alarms, "alarm_unavailable": unavailable, "refuted_rungs": refuted}


def rlr_block(S1, IND, cp, rung_results: list, kappa: tuple) -> dict | None:
    """Lemma Lad over the CERTIFIED RLR rungs of one block, cross-checked exactly (rlr307_independent)."""
    cert = [r["record"] for r in rung_results if r.get("status") == "CERTIFIED"]
    brec = S1.ladder_compose(cp, cert)
    lad = IND.ladder(cert)
    if lad is None:
        if brec["status"] != "NOT_CERTIFIED":
            raise ValueError("ladder status disagrees with the independent Lemma Lad")
        return None
    isup = IND.block_supply(lad, *kappa)
    same = all(F(brec[k]) == lad[k] for k in IND.UPPER_KEYS + IND.LOWER_KEYS) and \
        all(F(brec[k]) == isup[k] for k in ("A0_SUPPLY", "A1_SUPPLY", "A2_SUPPLY"))
    for r in cert:
        ind = IND.block_supply(r, *kappa)
        same = same and all(F(r[k]) == ind[k] for k in ("A0_SUPPLY", "A1_SUPPLY", "A2_SUPPLY", "G0", "G1", "G2"))
    if not same:
        raise ValueError("RLR ladder / block supply disagrees with rlr307_independent")
    return brec


def envelope(U_list: list) -> list:
    """Lemma M-U monotone envelope over the pre-declared increasing b_i: Ubar_i = min_{j <= i} U_j (None = +inf)."""
    out, cur = [], None
    for u in U_list:
        if u is not None and (cur is None or F(u) < cur):
            cur = F(u)
        out.append(cur)
    return out
