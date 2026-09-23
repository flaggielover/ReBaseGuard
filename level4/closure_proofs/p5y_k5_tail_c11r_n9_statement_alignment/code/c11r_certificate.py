"""C11R round 3 -- from CERTIFICATE to PROPOSITION (blocker B-3), and the PRODUCTION GUARDS (B-4).

WHAT WAS WRONG. Round 2 built both the original and the independent statement with one template,
c11r_schema.statement(constant), keyed by the constant's NAME, and never looked at a certificate.
A certificate for the wrong kernel, from the original's route, or not certified at all, still
compared EQUIVALENT; so did a value no certificate produced (erratum E16). And the three guards that
would have caught some of that -- value tracing, screen-before-certify, and the NOT_IMPLEMENTED
disposition rule -- existed only inside the mutation suite (erratum E17).

WHAT THIS MODULE DOES. A certificate records FACTS about a certification call: the certifier that
ran (module, function, the module's hash), exactly what it was given (weight, drift block, depth,
panels, atom-removal argument) with a digest binding them, and what the certifier ITSELF returned.
`reconstruct` then DERIVES what that certificate proves, from those facts alone:

    certificate  ->  verified semantics  ->  reconstructed proposition(s)  ->  compare with original

  * which constants it proves comes from the DEDUCTIONS table, keyed by (certifier module,
    certifier function, the kernel the certifier reported) -- NOT by the name a target record uses.
    A K_e supersolution proves Abar and nothing else; claiming tau from it is refused;
  * the kernel, direction, drift block, state set, aggregation, premises and candidate function in
    the reconstructed proposition all come from the certificate;
  * the numerical bound is RECOMPUTED from the certified candidate function. A target value that
    differs is refused: that is the value-trace guard, now in production.

Changing the certificate while leaving the target's constant name fixed changes -- or voids -- the
reconstructed proposition. That is the property round 2 lacked.

STATEMENT EQUIVALENCE and NUMERICAL AGREEMENT are separate. This module decides what is PROVED;
c11r_equiv.compare decides whether that proposition is the original's; the comparator decides the
numeric class only for a proposition that is. A different value under the same legitimately proved
proposition changes the numeric class and leaves statement equivalence unchanged.

THE PRODUCTION GUARDS -- the single implementation, called by the runs producer's self-check and
by the comparator (whose verdict is EXECUTION_INVALID when one fails), and bound by module and
function name in the frozen gate. The mutation suite mutates their inputs; it holds no copy of any
rule.
  G10  screen_order   -- a POINTWISE_INFEASIBLE member is never sent; a certified one was screened
  G8   dispositions   -- NOT_IMPLEMENTED exactly where the frozen policy says, nowhere else
  VT   value tracing  -- evaluate_target: the value equals what the certificate proves
  G19  configuration_adherence -- every certificate was made at the ONE frozen depth and panels

WHAT RECONSTRUCTION CANNOT SEE. A certificate is a RECORD of a certification call, not a proof
object that can be re-checked cheaply. Reconstruction verifies the record's internal consistency
(certifier hash, digest over weight + inputs + certifier, reported kernel against the atom-removal
argument, margins against the certified flag, family shape, cover, aggregation, premises) and
derives the proposition from it. A record forged CONSISTENTLY -- a different weight, a recomputed
digest, a matching target value -- is detectable only by re-executing the certifier on the
recorded inputs. What binds the record is therefore the EXECUTION CHAIN (round 4, c11r_contract;
revision 3's version of this paragraph claimed a binding that did not exist -- erratum E25): the
runner refuses to start unless every load-bearing file is the frozen contract's version, the run
records the recomputed identity, and the comparator recomputes the whole chain (G20), requiring
every frozen path to be untouched since the approved commit -- so modified code can neither pass
the pre-flight nor be reverted unseen. A record hand-written without running the frozen runner at
all remains detectable only by re-execution. This limit is stated, not hidden: the mutation
suite's forged-certificate controls cover the inconsistent forgeries, the chain controls
(c11r_chain.py) the identity attacks.

This module reads no original magnitude and loads no artifact.
"""
from __future__ import annotations

import pathlib
import sys
from fractions import Fraction as F

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import c11r_common as C
import c11r_idrift as I
import c11r_schema as S

X, G = I.X, I.G
SUPER, SUB = "supersolution", "subsolution"

# What each certifier proves. Keyed by (module, function, kernel the certifier REPORTED).
DEDUCTIONS = {
    ("c11r_idrift.py", "supersolution_margin_iv", "K_e"): {
        "kind": SUPER, "route": "independent_supersolution", "direction": "UPPER_BOUND",
        "family": "w = A - B*m", "premises": (), "implemented": True,
        "inequality": "w >= 1 + K_e w on the cover, for every e in the drift block",
        "yields": {"Abar": "w_at_atom"}},
    ("c11r_idrift.py", "supersolution_margin_iv", "Khat_e"): {
        "kind": SUPER, "route": "independent_supersolution", "direction": "UPPER_BOUND",
        "family": "w = A - B*m", "premises": (), "implemented": True,
        "inequality": "w >= 1 + Khat_e w on the cover, for every e in the drift block",
        "yields": {"tau": "w_at_atom", "C_T": "sup_cover_w"}},
    ("c11r_boxdata.py", "subsolution_margin_iv", "Khat_e"): {
        "kind": SUB, "route": "independent_subsolution", "direction": "LOWER_BOUND",
        "family": "u = alpha + beta*m", "premises": (), "implemented": True,
        "inequality": "u <= h_1 + Khat_e u on the cover, u >= 0, h_min > 0, every e in the block",
        "yields": {"D_lo": "u_at_atom"}},
    # declared so that a conditional certificate is recognised AS conditional; not implemented
    ("c11r_derivative.py", "derivative_propagation", "Khat_e"): {
        "kind": "derivative", "route": "independent_derivative_propagation",
        "direction": "UPPER_BOUND", "family": "d', d''", "implemented": False,
        "premises": ("C_T_independent", "tau_independent"),
        "inequality": "residual-to-error propagation for d' and d''",
        "yields": {"D1": "not_implemented", "D2": "not_implemented"}},
}
CERTIFIER_MODULES = ("c11r_idrift.py", "c11r_boxdata.py")
COVER_FUNCTION = "c11_certifier.cover"
SINGLE = "single_certificate_whole_block"


# ---------------------------------------------------------------------------------------------
# construction -- the runs producer builds every certificate here, so there is one shape
# ---------------------------------------------------------------------------------------------
def weight_json(w: dict) -> dict:
    return {f"{i},{j}": str(F(c)) for (i, j), c in sorted(w.items())}


def weight_from(wj: dict) -> dict:
    return {tuple(int(x) for x in k.split(",")): F(v) for k, v in wj.items()}


def certifier_hashes(commit: str | None = None) -> dict:
    """sha256 of each certifier module: at a commit (post-seal) or as now on disk (pre-seal)."""
    out = {}
    for m in CERTIFIER_MODULES:
        path = C.HERE / m
        if commit:
            out[m] = C.sha256_bytes(C.blob_at(commit, str(path.relative_to(C.REPO))))
        else:
            out[m] = C.sha256_file(path)
    return out


def input_digest(weight: dict, inputs: dict, certifier: dict) -> str:
    return C.sha256_obj({"weight": weight, "inputs": inputs, "certifier": certifier})


def make_certificate(*, cid: str, family: str, w: dict, drift_block: tuple, depth: int,
                     panels: int, atom_removed: bool, certifier_module: str,
                     certifier_function: str, result: dict | None, screen: str, sent: bool,
                     seconds: float, premises=(), certifier_sha: str | None = None) -> dict:
    wj = weight_json(w)
    inputs = {"drift_block": [str(F(drift_block[0])), str(F(drift_block[1]))],
              "depth": depth, "panels": panels, "atom_removed_argument": bool(atom_removed)}
    certifier = {"module": certifier_module, "function": certifier_function,
                 "module_sha256": certifier_sha or C.sha256_file(C.HERE / certifier_module)}
    if result is None:
        res = {"kernel": None, "certified": False, "margin_lower_bound": None, "boxes": 0}
    else:
        res = {"kernel": result.get("kernel"), "certified": bool(result["certified"]),
               "margin_lower_bound": str(result["margin_lower_bound"]),
               "boxes": result["boxes"]}
        for f in ("w_min_lower_bound", "h_min_lower_bound"):
            if f in result:
                res[f] = str(result[f])
        if "u_nonnegative" in result:
            res["u_nonnegative"] = bool(result["u_nonnegative"])
    return S.certificate(certificate_id=cid, family=family, weight=wj, inputs=inputs,
                         input_digest=input_digest(wj, inputs, certifier), certifier=certifier,
                         certifier_result=res, cover={"function": COVER_FUNCTION, "depth": depth},
                         aggregation=SINGLE, premises=sorted(premises),
                         screen_classification=screen, sent_to_certification=bool(sent),
                         seconds=seconds)


# ---------------------------------------------------------------------------------------------
# reconstruction
# ---------------------------------------------------------------------------------------------
def _value(kind_of_value: str, w: dict, depth: int) -> F:
    if kind_of_value in ("w_at_atom", "u_at_atom"):
        return F(w.get((0, 0), 0))                 # every other monomial vanishes at (0, 0)
    if kind_of_value == "sup_cover_w":
        return max(X.poly_eval_iv(w, G.Iv(a, b), G.Iv(c, d)).hi
                   for (a, b, c, d) in X.cover(depth))
    raise ValueError(kind_of_value)


def reconstruct(cert: dict, *, expected_certifier_sha: dict, runs_producer: dict,
                deductions: dict | None = None) -> dict:
    """What this certificate PROVES, derived from its facts. Nothing is taken from a target."""
    D = DEDUCTIONS if deductions is None else deductions
    problems, independence = [], False
    for f in S.CERT_FIELDS:
        if f not in cert:
            problems.append(f"missing field {f!r}")
    if problems:
        return {"problems": problems, "independence_violation": False, "propositions": {},
                "values": {}}
    cf, res, inp = cert["certifier"], cert["certifier_result"], cert["inputs"]
    stem = str(cf.get("module", "")).removesuffix(".py").split("/")[-1]
    if stem in S.FORBIDDEN_PRODUCERS:
        independence = True
        problems.append(f"certifier {cf.get('module')!r} is in the original's load-bearing graph")
    key = (cf.get("module"), cf.get("function"), res.get("kernel"))
    ded = D.get(key)
    if ded is None:
        problems.append(f"no recognised certifier proves anything as {key}")
        return {"problems": problems, "independence_violation": independence,
                "propositions": {}, "values": {}, "deduction": None}
    if not ded["implemented"]:
        problems.append(f"route {ded['route']!r} is not implemented; nothing it names is proved")
    if expected_certifier_sha.get(cf["module"]) != cf.get("module_sha256"):
        problems.append(f"certifier hash {str(cf.get('module_sha256'))[:12]} differs from the "
                        f"expected {str(expected_certifier_sha.get(cf['module']))[:12]}")
    want_arg = res.get("kernel") == "Khat_e"
    if inp.get("atom_removed_argument") is not want_arg:
        problems.append(f"atom_removed_argument {inp.get('atom_removed_argument')!r} contradicts "
                        f"the kernel the certifier reported ({res.get('kernel')!r})")
    try:
        margin = F(res["margin_lower_bound"])
    except (TypeError, ValueError, KeyError):
        margin = None
    if ded["kind"] == SUPER:
        wmin = F(res["w_min_lower_bound"]) if res.get("w_min_lower_bound") is not None else None
        holds = margin is not None and wmin is not None and margin > 0 and wmin >= 0
    elif ded["kind"] == SUB:
        hmin = F(res["h_min_lower_bound"]) if res.get("h_min_lower_bound") is not None else None
        holds = (margin is not None and hmin is not None and margin > 0 and hmin > 0
                 and res.get("u_nonnegative") is True)
    else:
        holds = False
    if res.get("certified") is not holds:
        problems.append(f"certified={res.get('certified')!r} contradicts the reported margins")
    if not holds:
        problems.append("the certifier's own result does not establish the inequality")
    if input_digest(cert["weight"], inp, cf) != cert.get("input_digest"):
        problems.append("input digest does not match the recorded weight, inputs and certifier")
    lo, hi = F(inp["drift_block"][0]), F(inp["drift_block"][1])
    if not lo < hi:
        problems.append("drift block is empty or a single point")
    if cert.get("aggregation") != SINGLE:
        problems.append(f"aggregation {cert.get('aggregation')!r} does not follow from ONE "
                        f"interval-drift certificate, which proves the whole block at once")
    declared, needed = set(cert.get("premises", [])), set(ded["premises"])
    if declared != needed:
        missing, extra = sorted(needed - declared), sorted(declared - needed)
        if missing:
            problems.append(f"a conditional derivation is presented without its premises "
                            f"{missing}")
        if extra:
            problems.append(f"declares premises {extra} that its route does not consume")
    if any(p in S.SIX_CONSTANTS for p in declared):
        independence = True
        problems.append("consumes an ORIGINAL constant as a premise")
    cov = cert.get("cover", {})
    if cov.get("function") != COVER_FUNCTION or cov.get("depth") != inp.get("depth"):
        problems.append(f"cover {cov} is not {COVER_FUNCTION} at the certified depth, so the "
                        f"state set is not the one the certifier covered")
    elif res.get("certified") and isinstance(inp.get("depth"), int) and \
            res.get("boxes") != len(X.cover(inp["depth"])):
        problems.append(f"the certifier reports {res.get('boxes')} boxes; the cover at depth "
                        f"{inp['depth']} has {len(X.cover(inp['depth']))} (review 3, N-5)")
    if cert.get("family") != ded["family"]:
        problems.append(f"family {cert.get('family')!r} is not the certifier's {ded['family']!r}")
    try:
        w = weight_from(cert["weight"])
    except (ValueError, AttributeError):
        w = None
        problems.append("the certified candidate function cannot be read")
    if w is not None:
        if set(w) - {(0, 0), (0, 1)}:
            problems.append(f"weight has monomials {sorted(set(w) - {(0, 0), (0, 1)})} outside "
                            f"the family")
        a0, a1 = w.get((0, 0), F(0)), w.get((0, 1), F(0))
        if ded["kind"] == SUPER and not (a1 <= 0 and a0 >= 5 * (-a1)):
            problems.append("w = A - B*m needs B >= 0 and A >= 5B")
        if ded["kind"] == SUB and not (a0 > 0 and a1 >= 0):
            problems.append("u = alpha + beta*m needs alpha > 0 and beta >= 0")
    if res.get("certified") and (cert.get("screen_classification") != "POINTWISE_FEASIBLE"
                                 or not cert.get("sent_to_certification")):
        problems.append("certified without having passed the pointwise screen (G10)")

    props, values = {}, {}
    if not problems:
        for constant, how in ded["yields"].items():
            v = _value(how, w, inp["depth"])
            values[constant] = v
            props[constant] = {
                "constant": constant, "quantity": S.QUANTITY[constant],
                "kernel": res["kernel"], "convention": S.CONVENTION[res["kernel"]],
                "direction": ded["direction"], "state_set": S.STATE_SET_R,
                "proposition": S.PROPOSITION[constant],
                "drift_domain": [str(lo), str(hi)],
                "aggregation": {"method": SINGLE, "sub_blocks": 1},
                "dependencies": sorted(ded["premises"]),
                "producer": {"module": runs_producer["module"],
                             "file_sha256": runs_producer["sha256"], "route": ded["route"],
                             "certificate_id": cert["certificate_id"], "certifier": dict(cf)},
                "candidate_function": dict(cert["weight"]), "numerical_bound": str(v),
                "unconditional": not ded["premises"],
                "reconstructed_from": f"certificate {cert['certificate_id']}: {ded['inequality']}"}
    return {"problems": problems, "independence_violation": independence,
            "propositions": props, "values": values,
            "deduction": {"route": ded["route"], "yields": sorted(ded["yields"]),
                          "kind": ded["kind"]}}


# ---------------------------------------------------------------------------------------------
# the production guards
# ---------------------------------------------------------------------------------------------
def evaluate_target(constant: str, t: dict, recon: dict | None) -> dict:
    """Derivability and VALUE TRACING for one target, against its certificate's reconstruction.
    Also the converse (review 3, N-5): a target reported NOT_CERTIFIED whose cited certificate
    cleanly proves it was DEMOTED, which misreports the run as surely as an invented value."""
    if t.get("status") == "NOT_CERTIFIED" and recon is not None and not recon["problems"] \
            and constant in recon["propositions"]:
        return {"certified_claim": False, "ok": False, "independence": False,
                "problems": [f"its certificate {t.get('certificate_id')!r} proves {constant}, yet "
                             f"it is reported NOT_CERTIFIED (demoted)"]}
    if t.get("status") != "CERTIFIED":
        return {"certified_claim": False, "ok": None, "problems": []}
    p = []
    if recon is None:
        p.append(f"cites certificate {t.get('certificate_id')!r}, which does not exist")
        return {"certified_claim": True, "ok": False, "problems": p, "independence": False}
    if recon["problems"]:
        p.append(f"its certificate proves nothing: {recon['problems']}")
    elif constant not in recon["propositions"]:
        p.append(f"its certificate proves {sorted(recon['propositions'])}, not {constant!r}")
    else:
        if F(t["value"]) != recon["values"][constant]:
            p.append(f"value {t['value']} does not trace to the certificate, which proves "
                     f"{recon['values'][constant]}")
    return {"certified_claim": True, "ok": not p, "problems": p,
            "independence": recon.get("independence_violation", False),
            "proposition": recon["propositions"].get(constant) if not p else None}


def screen_order(runs: dict) -> list[str]:
    """G10: no POINTWISE_INFEASIBLE member sent on; every certified member was screened."""
    bad = []
    for cid, c in S.certificates(runs).items():
        if S.cert_screen_class(c) == "POINTWISE_INFEASIBLE" and S.cert_sent(c):
            bad.append(f"{cid}: POINTWISE_INFEASIBLE yet sent to certification")
        if S.cert_screen_class(c) == "NOT_REACHED" and S.cert_sent(c):
            bad.append(f"{cid}: never screened (NOT_REACHED) yet sent to certification")
        if c["certifier_result"].get("certified") and not (
                S.cert_screen_class(c) == "POINTWISE_FEASIBLE" and S.cert_sent(c)):
            bad.append(f"{cid}: certified without passing the pointwise screen")
    return bad


def dispositions(runs: dict, policy: dict) -> list[str]:
    """G8: NOT_IMPLEMENTED exactly for the constants the frozen policy does not implement."""
    implementable = set(policy["target_scope"]["implementable_under_this_policy"])
    bad = []
    for k, t in S.targets(runs).items():
        if k in implementable and t["status"] == "NOT_IMPLEMENTED":
            bad.append(f"{k}: the policy implements it, yet it is NOT_IMPLEMENTED")
        if k not in implementable and t["status"] != "NOT_IMPLEMENTED":
            bad.append(f"{k}: the policy does not implement it, yet it is {t['status']}")
    return bad


def configuration_adherence(runs: dict, policy: dict) -> list[str]:
    """G19: ONE execution at ONE configuration -- every certificate at the frozen depth and panels."""
    ch = policy["configuration"]["chosen"]
    want = (ch["depth"], ch["panels"])
    bad = []
    for cid, c in S.certificates(runs).items():
        got = (c["inputs"].get("depth"), c["inputs"].get("panels"))
        if got != want:
            bad.append(f"{cid}: made at depth/panels {got}, not the frozen {want}")
    return bad


def evaluate_run(runs: dict, policy: dict, *, expected_certifier_sha: dict,
                 runs_producer: dict, deductions: dict | None = None) -> dict:
    """Every production guard over one runs artifact."""
    recon = {cid: reconstruct(c, expected_certifier_sha=expected_certifier_sha,
                              runs_producer=runs_producer, deductions=deductions)
             for cid, c in S.certificates(runs).items()}
    tg = {k: evaluate_target(k, t, recon.get(t.get("certificate_id")))
          for k, t in S.targets(runs).items()}
    g10, g8 = screen_order(runs), dispositions(runs, policy)
    g19 = configuration_adherence(runs, policy)
    vt = {k: v["problems"] for k, v in tg.items() if v["ok"] is False}
    return {"reconstructions": {cid: {k: r[k] for k in ("problems", "independence_violation",
                                                        "deduction")}
                                for cid, r in recon.items()},
            "reconstructed": recon, "targets": tg,
            "G8": {"violations": g8, "PASS": not g8},
            "G10": {"violations": g10, "PASS": not g10},
            "G19": {"violations": g19, "PASS": not g19},
            "value_trace": {"violations": vt, "PASS": not vt},
            "ALL_GUARDS_PASS": not g8 and not g10 and not g19 and not vt}
