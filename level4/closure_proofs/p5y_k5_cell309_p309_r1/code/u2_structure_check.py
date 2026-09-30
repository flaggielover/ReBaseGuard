"""Mechanical evidence for the U2 corrected proposition (owner rulings 2, 2026-09-30; formal campaign p5y_k5_cell309_p309_r1).

  python3 code/u2_structure_check.py      -> evidence/u2/U2_STRUCTURE_CHECK.json; exit 0 iff every check passes

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


def _scan_module(rel: str) -> dict:
    raw, tree = _src(rel)
    imports, reads, named = set(), [], set()
    for n in ast.walk(tree):
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


def s3_isolation() -> dict:
    out = {k: _scan_module(v) for k, v in STAGE1.items()}
    pins = json.loads((REPO / C1B_PINS).read_bytes())
    for f in pins["load_bearing"]:
        out["c1b:" + f] = _scan_module(C1B_DIR + f)
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
    checks = {
        "S1_symbolic_identity": all(v for k, v in s1.items() if isinstance(v, bool)),
        "S3_stage1_no_consumer_or_record_import": all(not v["consumer_or_record_imports"] for v in s3.values()),
        "S3_stage1_no_record_file_named": all(not v["record_words_in_string_constants"] for v in s3.values()),
        "S4_direct_reads_adopted_fields_without_assignment": (not s4["direct_subscript_assignments"]
                                                               and set(s4["direct_reads_adopted_fields"]) ==
                                                               {"R2_interval", "M_R2", "R_interval", "D_interval"}),
        "S4_adapter_touches_no_record_field": not s4["adapter_subscripts_record_fields"],
        "pins": all(v == "PINNED_MATCH" for v in pm.values()),
    }
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=REPO, capture_output=True, text=True).stdout.strip()
    out = {"schema": "p309.u2-structure-check/1", "git_head": head,
           "utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
           "tool_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
           "ok": all(checks.values()), "checks": checks, "S1": s1, "S2": s2, "S3": s3, "S4": s4, "pins": pm}
    d = FNS / "evidence" / "u2"
    d.mkdir(parents=True, exist_ok=True)
    (d / "U2_STRUCTURE_CHECK.json").write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    print(json.dumps({"ok": out["ok"], "checks": checks}, indent=1))
    return 0 if out["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
