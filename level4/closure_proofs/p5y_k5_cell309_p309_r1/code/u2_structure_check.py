"""Mechanical evidence for the U2 corrected proposition (owner rulings 2, 2026-09-30; formal campaign p5y_k5_cell309_p309_r1).

  python3 code/u2_structure_check.py      -> evidence/u2/U2_STRUCTURE_CHECK_V2.json; exit 0 iff every check passes

Version 2 (U2 check conditions U3/U4): adds U3a (adapter fields bound by AST to the frozen tct_rule roles), U3b
(srk_coefficients selects exactly min(old, new), None -> old), U3c (Stage-1 isolation over every loaded C1B module and
the guard modules with a role whitelist; RLR307 helper and C1B pins against their own pin tables) and U4 (the driver,
the rehearsal and the FC2 components: direct() called unchanged via the shim, no forbidden consumer call, Stage-1
functions read no record or measurement, record fields only in their frozen roles, target inputs only from the
historical control / execute, FC2 components isolated).  Version 1 evidence (U2_STRUCTURE_CHECK.json) stays as committed.

Nothing is evaluated: no kernel, no consumer function, no cell.  Every check is a static analysis of pinned source
text (Python AST) or of JSON key names.  No number of any tail cell is read or printed.

S1  Symbolic identity (exact polynomial arithmetic over Q, no sampling).  From the pinned sources:
      * the SRK branch expressions new3, new4 of srk_assemble.srk_coefficients;
      * the frozen TC-T expressions: tct_rule.fG_zero_candidate (+ eps3, as tct_rule.tail_object adds it) and
        tc_rule.env4 at sG = 0 (the (P2') candidate Ĝ := 0 that tct_rule uses when order3 is None);
      * srk_assemble.p_terms / rad_tct versus tc_rule.taylor_bounds / radius.
    Checks: new3[G_i := A0*k_i] == A0*fG_TCT; new4[G_i := A0*k_i] == A0*Env4_TCT; p_terms == taylor_bounds;
    rad_tct == radius.  Consequence: every sub-expression of adopted (P3-provenance) scalars in rad_r^SRK is one the
    frozen TC-T radius already forms; SRK changes only the operator-side multipliers A0*k_i -> Gamma_i.
S2  Field inventory: every key the Stage-2 path reads from each input object, extracted from the AST of
    srk_adapter (fields_for_r, assemble, srk_enclosure), tct_rule (tail_enclosure, tail_object, sigmas),
    c2_d5_forecast.direct and c2_d5_forecast.main (the validation gates).  Printed as key names only.
S3  Producer / Stage-1 isolation: the Stage-1a producer, gate and verifier modules and the Stage-1b code (RLR307
    stage-1 driver, independent reconstruction, pinned loader, and the C1B_R2 load-bearing files) are scanned for
    imports and for file-read calls; no Stage-1 module may import a consumer/record module or name a record,
    measurement, adopted-input or registry file.
S4  No record field is recomputed: in c2_d5_forecast.direct the adopted fields R2_interval, M_R2, R_interval,
    D_interval enter only by subscript read (never as an assignment target), and srk_adapter never subscripts them.
"""
from __future__ import annotations

import ast
import datetime
import hashlib
import json
import re
import subprocess
import sys
from fractions import Fraction as Fr
from pathlib import Path

FNS = Path(__file__).resolve().parents[1]
REPO = FNS.parents[2]
CP = "level4/closure_proofs/"
RNS = CP + "p5y_k5_cell309_research_r1/"
MANIFEST = RNS + "protocol_prep/P309_CANDIDATE_FREEZE_MANIFEST.json"
SRC = {
    "srk_assemble": RNS + "impl/srk_assemble.py",
    "srk_adapter": RNS + "impl/srk_adapter.py",
    "tct_rule": CP + "p5y_k5_m5_tail_closure/code/tct_rule.py",
    "tc_rule": CP + "p5y_k5_lower_front_order3/code/tc_rule.py",
    "c2_d5_forecast": CP + "p5y_k5_tail_c2_closure/code/c2_d5_forecast.py",
}
STAGE1 = {
    "srk_kernel": RNS + "impl/srk_kernel.py", "srk_float": RNS + "impl/srk_float.py",
    "srk_envelope": RNS + "impl/srk_envelope.py", "srk_certify": RNS + "impl/srk_certify.py",
    "srk_gate": RNS + "impl/srk_gate.py", "srk_verify_indep": RNS + "verify/srk_verify_indep.py",
    "rlr307_stage1": CP + "p5y_k5_cell307_rlr_r1/code/rlr307_stage1.py",
    "rlr307_independent": CP + "p5y_k5_cell307_rlr_r1/code/rlr307_independent.py",
    "rlr307_pinned": CP + "p5y_k5_cell307_rlr_r1/code/rlr307_pinned.py",
}
C1B_DIR = CP + "p5y_k5_tail_overnight_research/streams/C_308/LR/cusum/"
C1B_PINS = CP + "p5y_k5_tail_overnight_research/validation/C1B_R2_CODE_PINS.json"
CONSUMER_MODULES = re.compile(r"^(tct_rule|tc_rule|tc_crosscheck|c2_\w+|tail_forecast\w*|deflated_consume|k5b_\w+|"
                              r"tct_inputs|tc_producer|text_consume|c1_\w+|c12\w*)$")
RECORD_WORDS = re.compile(r"TCT_INPUTS|ADOPTED_TAIL|K1_RECORD|k1_record|Aux5|record_manifest|records_dir|"
                          r"REGISTRY_C[12]|measurement_r|auxiliary_evidence|candidate_suprema|midpoint_eps|"
                          r"eps_cell|R2_interval|C_upper|payload")


# ---------------------------------------------------------------- exact polynomials over Q (dict monomial -> Fr)
def _mono(*pairs):
    return tuple(sorted(pairs))


def P_const(c):
    return {(): Fr(c)} if c else {}


def P_sym(s):
    return {_mono((s, 1)): Fr(1)}


def P_add(a, b, sign=1):
    out = dict(a)
    for m, c in b.items():
        out[m] = out.get(m, Fr(0)) + sign * c
        if out[m] == 0:
            del out[m]
    return out


def P_mul(a, b):
    out = {}
    for m1, c1 in a.items():
        for m2, c2 in b.items():
            d = dict(m1)
            for s, e in m2:
                d[s] = d.get(s, 0) + e
            m = tuple(sorted(d.items()))
            out[m] = out.get(m, Fr(0)) + c1 * c2
            if out[m] == 0:
                del out[m]
    return out


def P_subst(p, sub: dict):
    """substitute symbol -> polynomial."""
    out = {}
    for m, c in p.items():
        term = P_const(c)
        for s, e in m:
            base = sub.get(s, P_sym(s))
            for _ in range(e):
                term = P_mul(term, base)
        out = P_add(out, term)
    return out


class Unsupported(ValueError):
    pass


def to_poly(node, symmap) -> dict:
    """AST expression -> polynomial.  symmap(node) returns a symbol name for Name/Subscript/Call leaves, or None."""
    if isinstance(node, ast.BinOp):
        a, b = to_poly(node.left, symmap), to_poly(node.right, symmap)
        if isinstance(node.op, ast.Add):
            return P_add(a, b)
        if isinstance(node.op, ast.Sub):
            return P_add(a, b, -1)
        if isinstance(node.op, ast.Mult):
            return P_mul(a, b)
        if isinstance(node.op, ast.Div):
            if set(b) - {()}:
                raise Unsupported("division by a non-constant")
            return P_mul(a, P_const(Fr(1) / b[()]))
        if isinstance(node.op, ast.Pow):
            if set(b) - {()} or b[()].denominator != 1 or b[()] < 0:
                raise Unsupported("non-integer power")
            out = P_const(1)
            for _ in range(int(b[()])):
                out = P_mul(out, a)
            return out
        raise Unsupported(type(node.op).__name__)
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
        return P_mul(P_const(-1), to_poly(node.operand, symmap))
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)) and not isinstance(node.value, bool):
        return P_const(Fr(node.value))
    s = symmap(node)
    if s is None:
        raise Unsupported(ast.dump(node)[:80])
    return P_sym(s)


def _fn(tree, name):
    for n in ast.walk(tree):
        if isinstance(n, ast.FunctionDef) and n.name == name:
            return n
    raise KeyError(name)


def _assigned(fn, target):
    """the unique non-None expression assigned to `target` (a `target = None` sentinel branch is skipped)."""
    vals = [n.value for n in ast.walk(fn) if isinstance(n, ast.Assign)
            and any(isinstance(t, ast.Name) and t.id == target for t in n.targets)
            and not (isinstance(n.value, ast.Constant) and n.value.value is None)]
    if len(vals) != 1:
        raise KeyError(f"{target}: {len(vals)} non-None assignments")
    return vals[0]


def _returned(fn):
    rets = [n.value for n in ast.walk(fn) if isinstance(n, ast.Return) and n.value is not None]
    return rets[-1]


def _leaf(node):
    """k[3] -> k3 ; f["sH"] -> sH ; g[1] -> G1 ; A['A0'] -> A0 ; plain names unchanged."""
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Subscript) and isinstance(node.value, ast.Name) and isinstance(node.slice, ast.Constant):
        base, key = node.value.id, node.slice.value
        if base == "k":
            return f"k{key}"
        if base == "g":
            return f"G{key}"
        if base in ("f", "A"):
            return str(key)
    return None


def _src(rel):
    raw = (REPO / rel).read_bytes()
    return raw, ast.parse(raw.decode("utf-8"))


def s1_identity() -> dict:
    _, sa = _src(SRC["srk_assemble"])
    _, tr = _src(SRC["tct_rule"])
    _, tc = _src(SRC["tc_rule"])
    sc = _fn(sa, "srk_coefficients")
    new3 = to_poly(_assigned(sc, "new3"), _leaf)
    new4 = to_poly(_assigned(sc, "new4"), _leaf)
    fG0 = to_poly(_returned(_fn(tr, "fG_zero_candidate")), _leaf)
    # tct_rule.tail_object: fG = residual_G + F(meas_r['eps_src'][3]) -- confirm that exact statement shape
    tobj = _fn(tr, "tail_object")
    fg_stmt = ast.unparse(_assigned(tobj, "fG"))
    fg_shape_ok = fg_stmt.replace(" ", "") == "residual_G+F(meas_r['eps_src'][3])"
    res_ok = ast.unparse(_fn(tr, "tail_object")).count("residual_G = fG_zero_candidate(k, sF, sD, sH, sigma3)") == 1
    fG_tct = P_add(fG0, P_sym("eps3"))
    env4 = to_poly(_returned(_fn(tc, "env4")), _leaf)
    env4_0 = P_subst(env4, {"sG": {}})                        # (P2'): sG = 0
    sub = {f"G{i}": P_mul(P_sym("A0"), P_sym(f"k{i}")) for i in (1, 2, 3, 4)}
    id3 = P_subst(new3, sub) == P_mul(P_sym("A0"), fG_tct)
    id4 = P_subst(new4, sub) == P_mul(P_sym("A0"), env4_0)
    # p-terms and radius
    pt = _fn(sa, "p_terms")
    tb = _fn(tc, "taylor_bounds")
    ren = {"fF": "fF", "fD": "fD", "fH": "fH", "fG": "fG", "Env4": "Env4", "rho": "rho", "e4": "Env4"}

    def lf(n):
        s = _leaf(n)
        return ren.get(s, s) if s is not None else None
    same_p = all(to_poly(_assigned(pt, p), lf) == to_poly(_assigned(tb, p), lf) for p in ("p0", "p1", "p2"))
    rt = to_poly(_returned(_fn(sa, "rad_tct")), _leaf)
    rr = to_poly(_returned(_fn(tc, "radius")), _leaf)
    same_rad = rt == rr
    # rad_srk: with B3 := A0*fG, B4 := A0*Env4 it equals rad_tct after expanding p2
    rs = _fn(sa, "rad_srk")
    rad = to_poly(_assigned(rs, "rad"), _leaf)
    p2 = to_poly(_assigned(pt, "p2"), lf)
    rad_sub = P_subst(rad, {"B3": P_mul(P_sym("A0"), P_sym("fG")), "B4": P_mul(P_sym("A0"), P_sym("Env4"))})
    rad_tct_expanded = P_subst(rt, {"p2": p2})
    same_order0 = rad_sub == rad_tct_expanded
    # linear structure in Gamma: coefficients of G_i are the adopted-scalar sub-expressions (printed as symbol names)
    def coeff(p, g):
        out = {}
        for m, c in p.items():
            d = dict(m)
            if d.get(g) == 1:
                d.pop(g)
                mm = tuple(sorted(d.items()))
                out[mm] = out.get(mm, Fr(0)) + c
        return out

    def show(p):
        return " + ".join(f"{c}*" + "*".join(f"{s}^{e}" if e > 1 else s for s, e in m) if m else str(c)
                          for m, c in sorted(p.items()))
    return {
        "fG_statement_shape_ok": fg_shape_ok and res_ok,
        "new3_is_A0_fG_with_A0k_i_replaced_by_Gamma_i": id3,
        "new4_is_A0_Env4_at_sG0_with_A0k_i_replaced_by_Gamma_i": id4,
        "p_terms_identical_to_tc_rule_taylor_bounds": same_p,
        "rad_tct_identical_to_tc_rule_radius": same_rad,
        "rad_srk_with_TCT_branches_equals_rad_tct": same_order0,
        "gamma_coefficients_new3": {g: show(coeff(new3, g)) for g in ("G1", "G2", "G3")},
        "gamma_coefficients_new4": {g: show(coeff(new4, g)) for g in ("G2", "G3", "G4")},
        "k_coefficients_A0fG_TCT": {k: show(coeff(fG_tct, k)) for k in ("k1", "k2", "k3")},
        "k_coefficients_Env4_TCT_sG0": {k: show(coeff(env4_0, k)) for k in ("k2", "k3", "k4")},
    }


def _keys(fn, roots: set) -> list:
    """subscript chains rooted at the given variable names: meas['r'][..]['sup']['F'] -> meas.r.*.sup.F"""
    out = set()
    for n in ast.walk(fn):
        if isinstance(n, ast.Subscript) or (isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                                             and n.func.attr == "get"):
            chain, cur = [], n
            while True:
                if isinstance(cur, ast.Subscript):
                    s = cur.slice
                    chain.append(repr(s.value) if isinstance(s, ast.Constant) else "*")
                    cur = cur.value
                elif isinstance(cur, ast.Call) and isinstance(cur.func, ast.Attribute) and cur.func.attr == "get":
                    a0 = cur.args[0] if cur.args else None
                    chain.append(repr(a0.value) if isinstance(a0, ast.Constant) else "*")
                    cur = cur.func.value
                else:
                    break
            if isinstance(cur, ast.Name) and cur.id in roots:
                out.add(cur.id + "." + ".".join(c.strip("'\"") for c in reversed(chain)))
    # keep maximal chains only
    return sorted(k for k in out if not any(o != k and o.startswith(k + ".") for o in out))


def s2_inventory() -> dict:
    _, ad = _src(SRC["srk_adapter"])
    _, tr = _src(SRC["tct_rule"])
    _, c2 = _src(SRC["c2_d5_forecast"])
    return {
        "srk_adapter.fields_for_r": _keys(_fn(ad, "fields_for_r"), {"meas", "m", "obj_r", "A"}),
        "srk_adapter.assemble": _keys(_fn(ad, "assemble"), {"meas"}),
        "srk_adapter.srk_enclosure": _keys(_fn(ad, "srk_enclosure"), {"meas", "o", "frozen_obj"}),
        "tct_rule.tail_enclosure": _keys(_fn(tr, "tail_enclosure"), {"meas", "aux", "order3"}),
        "tct_rule.tail_object": _keys(_fn(tr, "tail_object"), {"meas_r", "order3"}),
        "tct_rule.sigmas": _keys(_fn(tr, "sigmas"), {"aux", "cs", "me"}),
        "c2_d5_forecast.direct": _keys(_fn(c2, "direct"), {"ad", "cov"}),
        "c2_d5_forecast.main (per-cell validation and supply)": _keys(_fn(c2, "main"), {"d", "rec", "meas", "blk",
                                                                                       "adopted", "st"}),
    }


def _scan_module(rel: str, refusal_lists=()) -> dict:
    """refusal_lists: module-level names whose string constants are refusal patterns (a guard's forbidden-path list),
    excluded from the record-word scan and reported separately."""
    raw, tree = _src(rel)
    imports, reads, named = set(), [], set()
    skip = set()
    for n in tree.body:
        if isinstance(n, ast.Assign) and any(getattr(t, "id", None) in refusal_lists for t in n.targets):
            skip |= {id(x) for x in ast.walk(n)}
    for n in ast.walk(tree):
        if id(n) in skip:
            continue
        if isinstance(n, ast.Import):
            imports.update(a.name.split(".")[0] for a in n.names)
        elif isinstance(n, ast.ImportFrom) and n.module:
            imports.add(n.module.split(".")[0])
        elif isinstance(n, ast.Call):
            f = n.func
            nm = f.attr if isinstance(f, ast.Attribute) else (f.id if isinstance(f, ast.Name) else "")
            if nm in ("open", "read_bytes", "read_text", "load", "loads", "load_frozen", "import_module",
                      "spec_from_file_location", "exec"):
                reads.append(nm)
        elif isinstance(n, ast.Constant) and isinstance(n.value, str):
            for m in RECORD_WORDS.finditer(n.value):
                named.add(m.group(0).lower())
    consumer_imports = sorted(i for i in imports if CONSUMER_MODULES.match(i))
    return {"sha256": hashlib.sha256(raw).hexdigest(), "imports": sorted(imports),
            "consumer_or_record_imports": consumer_imports, "file_read_calls": sorted(set(reads)),
            "record_words_in_string_constants": sorted(named)}


C1B_LOAD_ORDER = ("c1b_gauss", "c1b_kernel", "c1b_float", "c1b_pw", "c1b_prov", "c1b_certpw")
GUARD_MODULES = {"q309_guard": RNS + "code/q309_guard.py", "p309_guard": "level4/closure_proofs/p5y_k5_cell309_p309_r1/code/p309_guard.py"}
GUARD_ALLOWED_IMPORTS = {"q309_guard", "__future__", "ast", "datetime", "fractions", "hashlib", "importlib", "json", "os",
                         "pathlib", "platform", "re", "socket", "subprocess", "sys"}


def s3_isolation() -> dict:
    out = {k: _scan_module(v) for k, v in STAGE1.items()}
    pins = json.loads((REPO / C1B_PINS).read_bytes())
    for f in sorted(set(pins["load_bearing"]) | {n + ".py" for n in C1B_LOAD_ORDER}):
        out["c1b:" + f] = _scan_module(C1B_DIR + f)
    for k, v in GUARD_MODULES.items():                     # role whitelist: a guard imports only stdlib + q309_guard
        r = _scan_module(v, refusal_lists=("FORBIDDEN_PATH_PATTERNS",))
        r["non_whitelisted_imports"] = sorted(set(r["imports"]) - GUARD_ALLOWED_IMPORTS)
        if r["non_whitelisted_imports"]:
            r["consumer_or_record_imports"] = r["consumer_or_record_imports"] + r["non_whitelisted_imports"]
        out["guard:" + k] = r
    return out


def s4_no_record_recompute() -> dict:
    _, c2 = _src(SRC["c2_d5_forecast"])
    _, ad = _src(SRC["srk_adapter"])
    d = _fn(c2, "direct")
    fields = {"R2_interval", "M_R2", "R_interval", "D_interval"}
    assigned = [ast.unparse(t) for n in ast.walk(d) if isinstance(n, (ast.Assign, ast.AugAssign))
                for t in (n.targets if isinstance(n, ast.Assign) else [n.target])
                if isinstance(t, ast.Subscript)]
    read = sorted({n.slice.value for n in ast.walk(d) if isinstance(n, ast.Subscript)
                   and isinstance(n.slice, ast.Constant) and n.slice.value in fields})
    adapter_touch = sorted({n.slice.value for n in ast.walk(ad) if isinstance(n, ast.Subscript)
                            and isinstance(n.slice, ast.Constant) and n.slice.value in fields | {"C_upper",
                            "eps_cell_refined", "candidate_suprema", "midpoint_eps", "auxiliary_evidence"}})
    return {"direct_reads_adopted_fields": read, "direct_subscript_assignments": assigned,
            "adapter_subscripts_record_fields": adapter_touch}


# ------------------------------------------------------------------ U3(a): adapter fields bound to the frozen roles
FIELD_BINDING = {   # adapter key -> (adapter expression with m/obj_r/A, frozen expression in tct_rule, with names)
    "sF": ("F(m['sup']['F'])", "sup:F"), "sD": ("F(m['sup']['D'])", "sup:D"), "sH": ("F(m['sup']['H'])", "sup:H"),
    "fF": ("F(m['delta_F']) + F(m['eps_src'][0])", "F(meas_r['delta_F']) + F(meas_r['eps_src'][0])"),
    "fD": ("F(m['delta_D']) + F(m['eps_src'][1])", "F(meas_r['delta_D']) + F(meas_r['eps_src'][1])"),
    "fH": ("F(m['delta_H']) + F(m['eps_src'][2])", "F(meas_r['delta_H']) + F(meas_r['eps_src'][2])"),
    "fG": ("F(obj_r['f_G'])", "obj:f_G"), "Env4": ("F(obj_r['env4'])", "obj:env4"),
    "sigma3": ("F(obj_r['sigma3'])", "sig:sigma3"), "sigma4": ("F(obj_r['sigma4'])", "sig:sigma4"),
    "eps3": ("F(m['eps_src'][3])", "F(meas_r['eps_src'][3])"),
    "rho": ("F(rho)", None), "A0": ("F(A['A0'])", None), "A1": ("F(A['A1'])", None), "A2": ("F(A['A2'])", None)}


def u3_field_binding() -> dict:
    _, ad = _src(SRC["srk_adapter"])
    _, tr = _src(SRC["tct_rule"])
    fr = _fn(ad, "fields_for_r")
    ret = _returned(fr)
    got = {k.value: ast.unparse(v) for k, v in zip(ret.keys, ret.values)} if isinstance(ret, ast.Dict) else {}
    to = _fn(tr, "tail_object")
    frozen = {n.targets[0].id: ast.unparse(n.value) for n in ast.walk(to) if isinstance(n, ast.Assign)
              and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name)}
    gen = [ast.unparse(n.value) for n in ast.walk(to) if isinstance(n, ast.Assign) and isinstance(n.targets[0], ast.Tuple)
           and [e.id for e in n.targets[0].elts] == ["sF", "sD", "sH"]]
    ret_obj = _returned(to)
    obj_keys = {k.value: ast.unparse(v) for k, v in zip(ret_obj.keys, ret_obj.values)}
    sig = ast.unparse(_fn(tr, "sigmas"))
    res = {}
    for key, (aexpr, fexpr) in FIELD_BINDING.items():
        ok = got.get(key, "").replace('"', "'") == aexpr
        if fexpr and fexpr.startswith("sup:"):
            ok = ok and gen == ["(F(meas_r['sup'][x]) for x in ('F', 'D', 'H'))"]
        elif fexpr and fexpr.startswith("obj:"):
            ok = ok and fexpr[4:] in obj_keys
        elif fexpr and fexpr.startswith("sig:"):
            ok = ok and f"'{fexpr[4:]}'" in sig
        elif fexpr:
            ok = ok and (fexpr in frozen.values() or fexpr in ast.unparse(to))
        res[key] = ok
    res["_no_extra_keys"] = set(got) == set(FIELD_BINDING)
    return res


def u3_branch_selection() -> dict:
    _, sa = _src(SRC["srk_assemble"])
    sc = _fn(sa, "srk_coefficients")
    txt = {n.targets[0].id: ast.unparse(n.value) for n in ast.walk(sc) if isinstance(n, ast.Assign)
           and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name)}
    tup = [n for n in ast.walk(sc) if isinstance(n, ast.Assign) and isinstance(n.targets[0], ast.Tuple)
           and [getattr(e, "id", None) for e in n.targets[0].elts] == ["old3", "old4"]]
    rs = _fn(sa, "rad_srk")
    uses = [ast.unparse(n.value) for n in ast.walk(rs) if isinstance(n, ast.Assign) and isinstance(n.targets[0], ast.Tuple)
            and [getattr(e, "id", None) for e in n.targets[0].elts][:2] == ["B3", "B4"]]
    return {"old_is_frozen_product": bool(tup) and ast.unparse(tup[0].value) == "(A0 * f['fG'], A0 * f['Env4'])",
            "B3_is_min_old_new": txt.get("B3") == "old3 if new3 is None or new3 >= old3 else new3",
            "B4_is_min_old_new": txt.get("B4") == "old4 if new4 is None or new4 >= old4 else new4",
            "rad_uses_selected_branches": uses == ["srk_coefficients(f, g)"]}


# ------------------------------------------------------------------ U4: the drivers and the FC2 components
DRIVER = {"p309_driver": "level4/closure_proofs/p5y_k5_cell309_p309_r1/code/p309_driver.py",
          "p309_rehearse": "level4/closure_proofs/p5y_k5_cell309_p309_r1/code/p309_rehearse.py"}
VARIANT = "level4/closure_proofs/p5y_k5_cell309_p309_r1/verify/srk_verify_indep_scoped.py"
FORBIDDEN_CONSUMER_CALLS = {"main", "compose", "requirement", "classify", "critical_ratio", "atom_constant_requirement",
                            "adopted_state", "tail_enclosures", "order3_inputs"}
STAGE1_FUNCS = {"stage1a", "job_stage1a", "stage1b", "job_stage1b", "run_jobs", "_spawn_job", "stage1a_jobs",
                "_check_worker_pins", "decoy_stage1a", "decoy_stage1b"}
STAGE1_FORBIDDEN_NAMES = {"cell_inputs", "s_i1", "historical_control", "evaluate_srk", "evaluate_tct", "meas", "aux",
                          "ci", "ad", "tct_inputs_target", "adopted_inputs", "registry_c1", "registry_c2",
                          "record_manifest", "c2_forecast", "coverage_r5"}
RECORD_FIELDS = {"C_upper", "auxiliary_evidence", "eps_cell_refined", "R2_interval", "M_R2", "R_interval", "D_interval",
                 "record_sha256", "candidate_suprema", "midpoint_eps"}


def u4_drivers() -> dict:
    out = {}
    trees = {k: _src(v)[1] for k, v in DRIVER.items()}
    d = trees["p309_driver"]
    ev = _fn(d, "evaluate_srk")
    direct_calls = [n for n in ast.walk(ev) if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                    and n.func.attr == "direct"]
    shim_ok = (len(direct_calls) == 1 and isinstance(direct_calls[0].args[0], ast.Name)
               and direct_calls[0].args[0].id == "shim")
    cross = any(isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr ==
                "tail_enclosure_crosscheck" for n in ast.walk(ev))
    shim_cls = next(n for n in ast.walk(d) if isinstance(n, ast.ClassDef) and n.name == "_SRKShim")
    te = next(n for n in shim_cls.body if isinstance(n, ast.FunctionDef) and n.name == "tail_enclosure")
    te_ok = any(isinstance(n, ast.Raise) for n in ast.walk(te)) and "self._args" in ast.unparse(te)
    out["i_direct_called_unchanged_via_shim"] = shim_ok and cross and te_ok
    bad_calls = []
    for k, t in trees.items():
        for n in ast.walk(t):
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr in FORBIDDEN_CONSUMER_CALLS:
                bad_calls.append(f"{k}:{n.lineno}:{n.func.attr}")
            if isinstance(n, ast.Constant) and isinstance(n.value, str) and (
                    "baseline" in n.value or "FEASIBILITY_GATES" in n.value):
                bad_calls.append(f"{k}:{n.lineno}:gate-baseline string")
    out["ii_no_forbidden_consumer_calls"] = not bad_calls
    out["ii_detail"] = bad_calls
    leaks = []
    for fn in [n for n in ast.walk(d) if isinstance(n, ast.FunctionDef) and n.name in STAGE1_FUNCS]:
        names = {x.id for x in ast.walk(fn) if isinstance(x, ast.Name)} | {
            x.value for x in ast.walk(fn) if isinstance(x, ast.Constant) and isinstance(x.value, str)} | {
            x.attr for x in ast.walk(fn) if isinstance(x, ast.Attribute)}
        hit = sorted(names & STAGE1_FORBIDDEN_NAMES)
        if hit:
            leaks.append(f"{fn.name}:{hit}")
    out["iii_stage1_reads_no_record_or_measurement"] = not leaks
    out["iii_detail"] = leaks
    stores, reads_outside = [], []
    for k, t in trees.items():
        fn_of = {}
        for fnode in [n for n in ast.walk(t) if isinstance(n, ast.FunctionDef)]:
            for x in ast.walk(fnode):
                fn_of.setdefault(id(x), fnode.name)
        for n in ast.walk(t):
            if isinstance(n, ast.Subscript) and isinstance(n.slice, ast.Constant) and n.slice.value in RECORD_FIELDS:
                where = fn_of.get(id(n))
                if isinstance(n.ctx, ast.Store):
                    stores.append(f"{k}:{where}:{n.slice.value}")
                elif k == "p309_driver" and where not in ("cell_inputs",):
                    reads_outside.append(f"{k}:{where}:{n.slice.value}")
    # the one store allowed is C2 main's copy of the adopted C_upper into the measurement dict, in cell_inputs
    out["iv_record_fields_read_only_in_frozen_roles"] = (stores == ["p309_driver:cell_inputs:C_upper"]
                                                         and not reads_outside)
    out["iv_detail"] = {"stores": stores, "reads_outside_cell_inputs": reads_outside}
    ci = _fn(d, "cell_inputs")
    callers = sorted({fn.name for fn in ast.walk(d) if isinstance(fn, ast.FunctionDef) and fn.name != "cell_inputs"
                      and any(isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == "cell_inputs"
                              for n in ast.walk(fn))})
    out["v_cell_inputs_callers"] = callers
    out["v_cell_inputs_only_from_the_control"] = callers == ["historical_control"] and "execute" in ast.unparse(ci)
    comp = {k: _scan_module(v) for k, v in {"p309_guard": GUARD_MODULES["p309_guard"], "variant": VARIANT}.items()
            if (REPO / v).exists()}
    out["vi_fc2_components_isolated"] = all(not v["consumer_or_record_imports"]
                                            and not v["record_words_in_string_constants"] for v in comp.values())
    out["vi_detail"] = {k: {"imports": v["imports"], "record_words": v["record_words_in_string_constants"]}
                        for k, v in comp.items()}
    return out


def pins_match_stage1b() -> dict:
    """the RLR307 helpers against the 307 driver's HELPER_SHA256 and the C1B files against C1B_R2_CODE_PINS."""
    import re as _re
    drv = (REPO / "level4/closure_proofs/p5y_k5_cell307_rlr_r1/code/rlr307_driver.py").read_text()
    tree = ast.parse(drv)
    helper = next(ast.literal_eval(n.value) for n in tree.body if isinstance(n, ast.Assign)
                  and getattr(n.targets[0], "id", "") == "HELPER_SHA256")
    out = {}
    for name, want in helper.items():
        rel = "level4/closure_proofs/p5y_k5_cell307_rlr_r1/code/" + name
        out[rel] = hashlib.sha256((REPO / rel).read_bytes()).hexdigest() == want
    cpins = json.loads((REPO / C1B_PINS).read_bytes())["pins"]
    for n in C1B_LOAD_ORDER:
        rel = C1B_DIR + n + ".py"
        want = cpins[n + ".py"]
        out[rel] = bool(_re.fullmatch(r"[0-9a-f]{64}", want)) and hashlib.sha256((REPO / rel).read_bytes()).hexdigest() == want
    return out


def pins_match() -> dict:
    man = json.loads((REPO / MANIFEST).read_bytes())
    pins = {p["path"]: p for p in man["code_pins"]}
    out = {}
    for rel in list(SRC.values()) + [v for k, v in STAGE1.items() if not k.startswith("rlr307")]:
        p = pins.get(rel)
        sha = hashlib.sha256((REPO / rel).read_bytes()).hexdigest()
        out[rel] = "PINNED_MATCH" if p and p.get("sha256") == sha else ("PINNED_MISMATCH" if p else "NOT_IN_MANIFEST")
    return out


def main() -> int:
    s1, s2, s3, s4 = s1_identity(), s2_inventory(), s3_isolation(), s4_no_record_recompute()
    pm = pins_match()
    u3a, u3b, u4, p1b = u3_field_binding(), u3_branch_selection(), u4_drivers(), pins_match_stage1b()
    checks = {
        "S1_symbolic_identity": all(v for k, v in s1.items() if isinstance(v, bool)),
        "S3_stage1_no_consumer_or_record_import": all(not v["consumer_or_record_imports"] for v in s3.values()),
        "S3_stage1_no_record_file_named": all(not v["record_words_in_string_constants"] for v in s3.values()),
        "S4_direct_reads_adopted_fields_without_assignment": (not s4["direct_subscript_assignments"]
                                                               and set(s4["direct_reads_adopted_fields"]) ==
                                                               {"R2_interval", "M_R2", "R_interval", "D_interval"}),
        "S4_adapter_touches_no_record_field": not s4["adapter_subscripts_record_fields"],
        "pins": all(v == "PINNED_MATCH" for v in pm.values()),
        "U3a_adapter_fields_bound_to_frozen_roles": all(u3a.values()),
        "U3b_branch_selection_is_min": all(u3b.values()),
        "U3c_stage1b_pins": all(p1b.values()),
        "U4_drivers": all(v for k, v in u4.items() if isinstance(v, bool)),
    }
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=REPO, capture_output=True, text=True).stdout.strip()
    out = {"schema": "p309.u2-structure-check/1", "git_head": head,
           "utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
           "tool_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
           "ok": all(checks.values()), "checks": checks, "S1": s1, "S2": s2, "S3": s3, "S4": s4, "pins": pm,
           "U3a": u3a, "U3b": u3b, "U3c_pins_stage1b": p1b, "U4": u4, "version": 2}
    sys.path.insert(0, str(FNS / "code"))
    import p309_env as E
    d = E.evidence_dir("u2")
    (d / "U2_STRUCTURE_CHECK_V2.json").write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    print(json.dumps({"ok": out["ok"], "checks": checks}, indent=1))
    return 0 if out["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
