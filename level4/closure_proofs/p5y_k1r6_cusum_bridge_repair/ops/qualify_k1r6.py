"""K1R6 qualification. NO genuine bridge science: prepare()/all_residuals() never run on cells 1000/1001.

Synthetic polynomials exercise the range operator; the historical r2 self-test polynomials (e = 1/4) exercise
it on real residuals; the post-science path is exercised by ops/replay_post_science.py on NON-GENUINE,
relabelled historical content in a deleted temporary directory.
"""
import ast
import copy
import hashlib
import json
import os
import random
import shutil
import subprocess
import sys
import tempfile
from fractions import Fraction as Fr
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
CFG = NS / "config"
WT = NS.parents[2]
REPO = Path("/home/ubuntu/work/ReBaseGuard")
CPR = REPO / "level4/closure_proofs"
AUX4 = CPR / "p5y_k1_cusum_aux4_fullcover"
K1R4 = NS.parent / "p5y_k1r4_bridge_successor"
K1R5 = NS.parent / "p5y_k1r5_cusum_entry"
sys.path.insert(0, str(NS / "driver"))
sys.path.insert(0, str(NS / "code"))
import k1r6_cusum_entry as E                                        # noqa: E402
import identity_k1r6 as IDB                                         # noqa: E402
import k1r6_chain as CH                                             # noqa: E402
import fast_range_k1r6 as FRT                                       # noqa: E402
import k1r6_certifier as KC                                         # noqa: E402
import k1r6_bridge_resolver as RES                                  # noqa: E402
import make_k1r6_stages as GEN                                      # noqa: E402
import identity4 as ID4                                             # noqa: E402
import fast_range as FR0                                            # noqa: E402
import aux_certifier                                                # noqa: E402
from cusum_layer2 import Pair                                       # noqa: E402
from flint import arb, ctx as FCTX                                  # noqa: E402
from rebaseguard_certify.residual import (_bernstein_max_abs, _max_abs_on_reachable,  # noqa: E402
                                          _power_to_bernstein)
OUT, NEG = [], []
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()   # noqa: E731
PY = sys.executable


def gate(name, ok, detail=""):
    OUT.append({"gate": name, "status": "PASS" if ok else "FAIL", "detail": detail})
    print(f"  {'PASS' if ok else 'FAIL'}  {name}" + (f" -- {detail}" if detail else ""))
    return ok


def neg(name, fn, expect):
    try:
        fn()
    except (Exception, SystemExit) as e:                            # noqa: BLE001
        ok = expect.lower() in f"{type(e).__name__}: {e}".lower()
        NEG.append({"control": name, "rejected": True, "expected_reason": ok, "reason": str(e)[:160]})
        print(f"  {'PASS' if ok else 'FAIL'}  NEG {name} -- {type(e).__name__}: {str(e)[:100]}")
        return
    NEG.append({"control": name, "rejected": False, "expected_reason": False})
    print(f"  FAIL  NEG {name} -- ACCEPTED")


def ctl(name, ok, detail=""):
    """A positive/behavioural control (Part G items that must be ACCEPTED or take a given branch)."""
    NEG.append({"control": name, "rejected": None, "expected_reason": bool(ok), "reason": detail})
    print(f"  {'PASS' if ok else 'FAIL'}  CTL {name}" + (f" -- {detail}" if detail else ""))


def bits(x):
    return (x.mid().man_exp(), x.rad().man_exp())


def git(*a):
    return subprocess.run(["git", "-C", str(WT), *a], capture_output=True, text=True).stdout


# ------------------------------------------------------------------ Part H: predecessors / kernel / TCB
def q_frozen_inputs():
    aux = json.loads((AUX4 / "manifests/producer_manifest_v2.json").read_text())
    drift = [f for f, h in aux["files"].items() if sha(REPO / f) != h]
    man = json.loads((CFG / "PRODUCER_MANIFEST.json").read_text())["files"]
    mdrift = [f for f, h in man.items() if sha(f) != h]
    k5 = git("diff", "--stat", "0cd4e8dd36615971745eb37c00197d735723cc82", "--", str(K1R5)) == "" and \
        git("status", "--porcelain", "--", str(K1R5)) == ""
    k4 = git("diff", "--stat", "d9e8f1185c04ee8beb339efff091a073e6ebc21d", "--", str(K1R4)) == "" and \
        git("status", "--porcelain", "--", str(K1R4)) == ""
    tbl = sha(RES.TABLE) == RES.PINNED_TABLE_SHA256 == \
        json.loads((K1R4 / "config/CHECKPOINT.json").read_text())["frozen_artifacts"]["CUSUM_BRIDGE_CELL_TABLE.json"]
    gate("H1 58 inherited aux4 kernel files == aux4's own recorded hashes; no changed inherited file",
         len(aux["files"]) == 58 and not drift, f"drift {drift}")
    gate("H2 producer manifest (69 files) byte-verified; binds kernel, generated modules, resolver, bridge table, "
         "transformation manifest, schemas, generator", len(man) == 69 and not mdrift, f"drift {mdrift}")
    gate("H3 K1R5 and K1R4 namespaces byte-identical to their freezes; bridge table == K1R4 checkpoint pin",
         k5 and k4 and tbl, f"K1R5 {k5} K1R4 {k4} table {tbl}")
    ident = json.loads((CFG / "PRODUCER_IDENTITY.json").read_text())
    k5id = json.loads((K1R5 / "config/PRODUCER_IDENTITY.json").read_text())["producer_identity_hash"]
    gate("H4 new K1R6 producer identity minted (not aux4's, not K1R5's)",
         ident["producer_identity_hash"] != k5id and ident["producer_manifest_hash"] == sha(CFG / "PRODUCER_MANIFEST.json"),
         ident["producer_identity_hash"])


def q_generation():
    r = subprocess.run([PY, str(NS / "code/make_k1r6_stages.py"), "--check"], capture_output=True, text=True)
    tm = json.loads((CFG / "TRANSFORMATION_MANIFEST.json").read_text())
    counts = {n: [(s["category"], s["expected_occurrences"]) for s in v["substitutions"]] for n, v in tm["stages"].items()}
    gate("G1 generated stages regenerate byte-identically from pinned frozen sources (counted substitutions)",
         r.returncode == 0, (r.stdout or r.stderr).strip()[:160])
    return counts


def strip_generated(text, appendix=None):
    lines = text.splitlines(keepends=True)
    assert lines[0].startswith("# GENERATED by code/make_k1r6_stages.py")
    body = "".join(lines[3:])
    if appendix:
        assert body.endswith(appendix)
        body = body[: -len(appendix)]
    return body


def inverse(text, subs):
    for old, new, cat, n, note in reversed(subs):
        if text.count(new) != n:
            raise AssertionError(f"inverse count {cat}: {new[:50]!r} x{text.count(new)} != {n}")
        text = text.replace(new, old)
    return text


def q_textual_equivalence():
    src_id = (AUX4 / "code/identity4.py").read_text()
    body = strip_generated((NS / "driver/identity_k1r6.py").read_text(), GEN.ID_APPENDIX)
    id_ok = inverse(body, GEN.ID_SUBS) == src_id
    same_scheme = (IDB.IDENTITY_FIELDS == ID4.IDENTITY_FIELDS and IDB.IDENTITY_KIND == ID4.IDENTITY_KIND
                   and not hasattr(IDB, "_cell_of"))
    gate("A1 identity_k1r6 == frozen identity4 except the 3 counted substitutions (R x2, V x1); identity kind, "
         "field list, admission and hashing text unchanged; historical _cell_of absent", id_ok and same_scheme,
         f"text {id_ok}, scheme {same_scheme}")
    q = (AUX4 / "code/qualify4.py").read_text()
    gsrc = (NS / "driver/k1r6_chain.py").read_text()
    ch_ok = []
    for fn, n in GEN.CHAIN_FUNCS:
        g = GEN.extract(gsrc, fn)
        ch_ok.append((g.replace("IDB.", "ID.") == GEN.extract(q, fn)) and g.count("IDB.") == n and "ID." not in g.replace("IDB.", ""))
    gate("A2 k1r6_chain build_certificates/_certified_content/_obligation_status/verify_chain == frozen qualify4 "
         "text with ID -> IDB only (3 + 0 + 0 + 7)", all(ch_ok), str(ch_ok))
    fr0 = (CPR / "p5x_global_nonlinear_dynamics/compute_optimization_r2/fast_range.py").read_text()
    fb = strip_generated((NS / "driver/fast_range_k1r6.py").read_text(), GEN.FR_APPENDIX)
    fr_ok = inverse(fb, GEN.FR_SUBS) == fr0
    tree = ast.parse((NS / "driver/fast_range_k1r6.py").read_text())
    bm = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "_bmax_total")
    iff = next(s for s in bm.body if isinstance(s, ast.If))
    cond = ast.unparse(iff.test)
    tail = ast.unparse(bm.body[-1])
    gate("B1 fast_range_k1r6 == frozen fast_range except P x1 + Z x4; empty test is exactly "
         "`type(u) is dict and len(u) == 0`; the non-empty branch is exactly the frozen call",
         fr_ok and cond == "type(u) is dict and len(u) == 0"
         and tail == "return _bernstein_max_abs(_power_to_bernstein(u), subdivision_depth)",
         f"text {fr_ok}; test `{cond}`; else `{tail}`")
    cl2 = (CPR / "p5y_k1_cover_ledger_implementation/code/cusum_layer2.py").read_text()
    rg = GEN.extract((NS / "driver/k1r6_certifier.py").read_text(), "_range", cls="K1R6Certifier")
    own = sorted(k for k in vars(KC.K1R6Certifier) if not (k.startswith("__") and k.endswith("__")))
    c_ok = (rg.replace("FRT.max_abs_on_reachable_fast(", "max_abs_on_reachable_fast(") == GEN.extract(cl2, "_range", cls="CellCertifier")
            and own == ["_range"] and KC.K1R6Certifier.__bases__ == (aux_certifier.Aux3Certifier,))
    gate("C1 K1R6Certifier(Aux3Certifier) overrides ONLY _range, = frozen cusum_layer2._range with 1 substitution",
         c_ok, f"own attributes {own}")
    k5 = (K1R5 / "driver/k1r5_cusum_entry.py").read_text()
    k6 = (NS / "driver/k1r6_cusum_entry.py").read_text()
    t = k5
    for s in GEN.ENTRY_SUBS:
        t = GEN.sub(t, s)
    fwd = (GEN.header("k1r5_entry", sha(K1R5 / "driver/k1r5_cusum_entry.py")) + GEN.ENTRY_PREFIX + t) == k6
    d = lambda n: ast.dump(n, include_attributes=False)             # noqa: E731
    f5 = next(n for n in ast.parse(k5).body if isinstance(n, ast.FunctionDef) and n.name == "certify")
    f6 = next(n for n in ast.parse(k6.replace("K1R6Certifier(cell, bits=bits)", "aux_certifier.Aux3Certifier(cell, bits=bits)")).body
              if isinstance(n, ast.FunctionDef) and n.name == "certify")
    cert_ok = d(f5) == d(f6) and k6.count("K1R6Certifier(cell, bits=bits)") == 1
    gate("D1 entry = K1R5 entry + declared substitutions only (K x1, I x2, B x5 incl. names, Z x1); certify() == "
         "K1R5 certify (itself proven = frozen run_cell block) except the certifier class", fwd and cert_ok,
         f"forward-regenerated {fwd}; certify AST {cert_ok}")


# ------------------------------------------------------------------ Part B / G: zero-case proofs and controls
def fired():
    return FRT.zero_case_record()["zero_case_count"]


def q_zero_case():
    FCTX.prec = 256
    N = {(0, 0): arb(3), (1, 1): arb(-2), (2, 0): arb(1) / arb(7)}
    Z = {(i, j): arb(0) for i in range(4) for j in range(4)}
    # G1 empty
    FRT.reset_zero_case()
    v, n = FRT._bmax_total({}, 0, "unit")
    try:
        _bernstein_max_abs(_power_to_bernstein({}), 0)
        frozen_raises = False
    except ValueError:
        frozen_raises = True
    ctl("G1 empty exact sparse polynomial -> exact 0 (frozen path raises ValueError)",
        v.is_exact() and v == 0 and n == 0 and fired() == 1 and frozen_raises, f"value {v}, exact {v.is_exact()}")
    # G2 explicit all-zero coefficients canonicalize to {} and give exactly the REFERENCE operator's value 0
    FRT.reset_zero_case()
    canon = FR0.affine_to_unit_square_fast(Z, arb(0), arb(1), arb(0), arb(1)) == {}
    vz, _ = FRT.max_abs_on_reachable_fast(Z, Z, subdivision_depth=0)
    vr, _ = _max_abs_on_reachable(Z, Z, subdivision_depth=0)
    try:
        FR0.max_abs_on_reachable_fast(Z, Z, subdivision_depth=0)
        fr_raises = False
    except ValueError:
        fr_raises = True
    ctl("G2 explicit all-zero coefficients -> canonical {} -> exact 0 == frozen REFERENCE operator value "
        "(frozen fast path raises)", canon and vz == 0 and vz.is_exact() and vr == 0 and vr.is_exact()
        and fired() == 4 and fr_raises, f"FRT {vz}, reference {vr}, firings {fired()}")

    def same(lo, hi, label, expect_fire=0):
        FRT.reset_zero_case()
        a, _ = FRT.max_abs_on_reachable_fast(lo, hi, subdivision_depth=0)
        b, _ = FR0.max_abs_on_reachable_fast(lo, hi, subdivision_depth=0)
        return bits(a) == bits(b) and fired() == expect_fire, f"{label}: FRT {a} frozen {b} firings {fired()}"

    ok, dt = same({(0, 0): arb(5)}, N, "constant")
    ctl("G3 nonzero constant -> non-empty (frozen) path, bit-identical, no firing", ok, dt)
    tiny = arb(2) ** -400
    tiny3 = arb(1) / arb(3) * arb(2) ** -400
    keep = all((0, 0) in FR0.affine_to_unit_square_fast({(0, 0): c}, arb(0), arb(1), arb(0), arb(1)) for c in (tiny, tiny3))
    ok1, d1 = same({(0, 0): tiny}, N, "2^-400")
    ok2, d2 = same({(0, 0): tiny3}, N, "(1/3)2^-400")
    ctl("G4 tiny nonzero rational (exact 2^-400; inexact (1/3)2^-400) retained -> non-empty path, bit-identical",
        keep and ok1 and ok2, f"retained {keep}")
    zr = arb(0, arb(2) ** -300)
    keep0 = (0, 0) in FR0.affine_to_unit_square_fast({(0, 0): zr}, arb(0), arb(1), arb(0), arb(1)) and not zr.is_zero()
    ok, dt = same({(0, 0): zr}, N, "0 +/- 2^-300")
    ctl("G5 0 +/- r (r > 0) is NOT exact zero -> kept, non-empty path, bit-identical", keep0 and ok, dt)
    lead = {(0, 0): arb(1), (1, 0): arb(2), (6, 6): arb(0), (5, 0): arb(0)}
    lu = FR0.affine_to_unit_square_fast(FR0.__dict__.get("_x", lead) if False else lead, arb(0), arb(1), arb(0), arb(1))
    okl, dl = same(lead, N, "leading zeros")
    FRT.reset_zero_case()
    allz_hi = {(6, 6): arb(0), (0, 0): arb(0), (3, 1): arb(0)}
    vv, _ = FRT.max_abs_on_reachable_fast(allz_hi, N, subdivision_depth=0)
    ctl("G6 higher degree with zero leading terms canonicalizes (zero keys dropped, nonzero kept; path frozen); "
        "all-zero high-degree -> {} -> fires once (low)", set(lu) <= {(0, 0), (1, 0)} and set(lu) and okl
        and fired() == 1 and FRT.zero_case_record()["firings"][0]["part"] == "low", f"{dl}; all-zero low fires {fired()}")
    inter = {(i, j): arb(0) for i in range(4) for j in range(4)}
    inter[(2, 1)] = arb(5)
    inter[(0, 0)] = arb(1)
    ok, dt = same(inter, inter, "interior")
    ctl("G7 one nonzero interior coefficient among zeros -> non-empty path, bit-identical, no firing", ok, dt)
    # G8: mutation of the generated totality rule -> refusal on the production path (module binding) and by hash
    with tempfile.TemporaryDirectory() as td:
        m = (NS / "driver/fast_range_k1r6.py").read_text().replace("if type(u) is dict and len(u) == 0:", "if len(u) <= 1:")
        (Path(td) / "fast_range_k1r6.py").write_text(m)
        code = ("import sys; sys.path.insert(0, %r); sys.path.insert(0, %r); import k1r6_cusum_entry as E; "
                "E.verify_k1r6_modules()") % (str(NS / "driver"), td)
        r = subprocess.run([PY, "-c", code], capture_output=True, text=True, timeout=600)
        tm = json.loads((CFG / "TRANSFORMATION_MANIFEST.json").read_text())["stages"]["fast_range_k1r6.py"]["generated_sha256"]
        hash_refused = hashlib.sha256(m.encode()).hexdigest() != tm
        err = (r.stderr.strip().splitlines() or [""])[-1]
        if r.returncode != 0 and "module binding" in err and hash_refused:
            NEG.append({"control": "G8 mutated totality rule (shadowed module)", "rejected": True, "expected_reason": True, "reason": err[:160]})
            print(f"  PASS  NEG G8 mutated totality rule -- {err[:100]}")
        else:
            NEG.append({"control": "G8 mutated totality rule (shadowed module)", "rejected": r.returncode != 0, "expected_reason": False, "reason": err[:160]})
            print(f"  FAIL  NEG G8 mutated totality rule -- rc {r.returncode} {err[:100]}")


def q_part_b_proofs():
    FCTX.prec = 256
    rnd = random.Random(20260926)
    drop = 0
    for _ in range(600):
        c = arb(rnd.choice([1, -1]) * rnd.randint(1, 10 ** 6)) * arb(2) ** rnd.randint(-500, 20)
        if rnd.random() < 0.5:
            c = c / arb(rnd.choice([3, 7, 11, 13]))
        i, j = rnd.randint(0, 6), rnd.randint(0, 6)
        for a, b_, c0, d in ((0, 1, 0, 1), (1, 4, 0, 1), (4, 5, 0, 1), (0, 1, 4, 5)):
            if not FR0.affine_to_unit_square_fast({(i, j): c}, arb(a), arb(b_), arb(c0), arb(d)):
                drop += 1
    gate("B2 a nonzero coefficient is never dropped (600 random exact/inexact monomials x 4 part maps: 0 empty)",
         drop == 0, f"empty outputs {drop}")
    # B7 downstream accepts range 0: the frozen certify() on the zero residual through the K1R6 _range
    inst = object.__new__(KC.K1R6Certifier)
    inst.rho, inst.depth, inst.bernstein_calls, inst.kernel_calls, inst.kernel_cpu = Fr(1, 8), 0, 0, 0, 0.0
    FRT.reset_zero_case()
    o = inst.certify("F_1", Pair({}), arb(2) ** -60, arb(3))
    ok_new = o["polynomial_residual"] == 0 and o["delta_mid"] >= 0 and o["delta_cell"] >= o["delta_mid"] and fired() == 4
    o0 = FRT.zero_case_record()["firings"][0]
    old = object.__new__(aux_certifier.Aux3Certifier)
    old.rho, old.depth, old.bernstein_calls, old.kernel_calls, old.kernel_cpu = Fr(1, 8), 0, 0, 0, 0.0
    try:
        old.certify("F_1", Pair({}), arb(2) ** -60, arb(3))
        old_raises = False
    except ValueError:
        old_raises = True
    div_log = []
    aux = json.loads((AUX4 / "manifests/producer_manifest_v2.json").read_text())["files"]
    for f in aux:
        if not f.endswith(".py"):
            continue
        tr = ast.parse((REPO / f).read_text())
        for node in ast.walk(tr):
            if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Div, ast.FloorDiv, ast.Mod)):
                if isinstance(node.right, ast.Constant) and isinstance(node.right.value, str):
                    continue                                        # pathlib join / str format, not arithmetic
                r = ast.unparse(node.right)
                if any(k in r for k in ("polynomial_residual", "poly", "_range(", "delta_mid")):
                    div_log.append(f"{f.split('/')[-1]}:{node.lineno} / {r[:40]}")
            if isinstance(node, ast.Call) and ast.unparse(node.func).split(".")[-1] in ("log", "log2", "log10", "log1p"):
                a = ast.unparse(node)
                if any(k in a for k in ("polynomial_residual", "poly", "_range(", "delta_mid")):
                    div_log.append(f"{f.split('/')[-1]}:{node.lineno} {a[:40]}")
    gate("B7 downstream accepts range 0: frozen certify() on a zero residual via K1R6 _range -> delta_mid >= 0, "
         "delta_cell >= delta_mid, firings recorded with object name; frozen class raises; no division/log of a range "
         "output anywhere in the 58-file kernel", ok_new and old_raises and o0["object"] == "F_1" and not div_log,
         f"delta_mid {o['delta_mid']}, object {o0['object']}, frozen raises {old_raises}, div/log sites {div_log}")


def q_nonzero_equivalence():
    FCTX.prec = 256
    # historical: every sealed record ran through the SAME frozen fast path (fast_range.py pinned in aux4 manifest)
    import manifest_v2
    recs = sorted((AUX4 / "diagnostics/cells").glob("aux4_CUSUM_*_256.json"))
    mh = {json.loads(p.read_text())["producer_manifest_hash"] for p in recs}
    aux = json.loads((AUX4 / "manifests/producer_manifest_v2.json").read_text())["files"]
    rel = "level4/closure_proofs/p5x_global_nonlinear_dynamics/compute_optimization_r2/fast_range.py"
    src_pin = json.loads((CFG / "TRANSFORMATION_MANIFEST.json").read_text())["sources"]["fast_range"]["sha256"]
    zero = total = 0
    for p in recs:
        r = json.loads(p.read_text())
        for src in (r.get("objects", {}), r.get("auxiliary_evidence", {}).get("objects", {})):
            for o in src.values():
                if "polynomial_residual" in o:
                    total += 1
                    zero += Fr(str(o["polynomial_residual"])) == 0
    idx = sorted(int(p.name.split("_")[2]) for p in recs)
    gate("E1 all 326 historical CUSUM cells sealed under one aux4 producer whose manifest pins THIS fast_range.py; "
         "the frozen fast path raises on any empty part, so no historical range call had one; 0 of "
         f"{total} recorded range outputs are zero", idx == list(range(326)) and len(mh) == 1
         and mh == {manifest_v2.identity()["producer_manifest_hash"]} and aux[rel] == src_pin and zero == 0,
         f"records {len(recs)}, manifest hashes {len(mh)}, zero outputs {zero}/{total}")
    # r2 self-test polynomials: the REAL production residual at e = 1/4 (historical fixture)
    import ra_certifier as RA
    from rebaseguard_certify.arb_backend import rational, workprec
    from rebaseguard_certify.polynomial import bi_add, bi_scale, chebyshev_payload_to_power
    from rebaseguard_certify.residual import _kernel_polynomials
    e = rational(1, 4)
    cg, _ = RA.solve_candidates(0.25)
    pay = cg.to_chebyshev_dyadic(scale_bits=RA.SCALE_BITS)
    with workprec(RA.BITS):
        g = chebyshev_payload_to_power(pay)
        b = RA.phi_taylor_coefficients(RA.TAYLOR_N, e)
        kl, kh = _kernel_polynomials(g, b, z_weight=0)
        rw = RA.reward_rho1(RA.TAYLOR_N, e)
        rl = bi_add(bi_add(g, bi_scale(kl, -arb(1))), bi_scale(rw, -arb(1)))
        rh = bi_add(bi_add(g, bi_scale(kh, -arb(1))), bi_scale(rw, -arb(1)))
        FRT.reset_zero_case()
        a, _ = FRT.max_abs_on_reachable_fast(rl, rh, subdivision_depth=0)
        f0, _ = FR0.max_abs_on_reachable_fast(rl, rh, subdivision_depth=0)
        a3, _ = FRT.max_abs_on_reachable_fast(rl, rh, subdivision_depth=3)
        f3, _ = FR0.max_abs_on_reachable_fast(rl, rh, subdivision_depth=3)
    gate("E2 historical r2 self-test polynomials (real residual, e = 1/4): bit-identical at depth 0 and 3, no firing",
         bits(a) == bits(f0) and bits(a3) == bits(f3) and fired() == 0, f"{a} | {a3}")
    rnd = random.Random(1062)
    bad = fire = 0
    for k in range(400):
        deg = rnd.randint(0, 7)
        P = {}
        for _ in range(rnd.randint(1, 12)):
            i, j = rnd.randint(0, deg), rnd.randint(0, deg)
            c = arb(rnd.randint(-10 ** 9, 10 ** 9) or 1) * arb(2) ** rnd.randint(-300, 5)
            P[(i, j)] = c / arb(rnd.choice([1, 1, 3, 5, 7])) if rnd.random() < 0.7 else arb(0)
        P[(0, 0)] = arb(rnd.randint(1, 99)) / arb(rnd.choice([1, 2, 3]))
        Q = {(i, j): c * arb(rnd.randint(-5, 5) or 1) for (i, j), c in P.items()}
        Q[(1, 0)] = arb(rnd.randint(1, 50))
        Q[(0, 1)] = arb(-rnd.randint(1, 50))
        FRT.reset_zero_case()
        d = rnd.choice([0, 0, 1, 2])
        x, _ = FRT.max_abs_on_reachable_fast(P, Q, subdivision_depth=d)
        y, _ = FR0.max_abs_on_reachable_fast(P, Q, subdivision_depth=d)
        bad += bits(x) != bits(y)
        fire += fired()
    gate("E3 random exact/inexact nonzero corpus (400 polynomial pairs, depths 0-2): bit-identical, 0 firings",
         bad == 0 and fire == 0, f"mismatches {bad}, firings {fire}")


# ------------------------------------------------------------------ Part F
def q_post_science_replay():
    with tempfile.TemporaryDirectory(prefix="k1r6-qual-") as td:
        shutil.copy(NS / "ops/replay_post_science.py", td)
        r = subprocess.run([PY, str(Path(td) / "replay_post_science.py"), str(NS / "driver"),
                            str(AUX4 / "diagnostics/cells/aux4_CUSUM_325_256.json")],
                           capture_output=True, text=True, timeout=1800, cwd=td)
    try:
        o = json.loads(r.stdout.strip().splitlines()[-1])
    except Exception:                                               # noqa: BLE001
        gate("F1 post-science bridge-index replay", False, (r.stderr or r.stdout)[-300:])
        return {"cells": {}}
    acc = sum(1 for c in o["cells"].values() if c["accepted"])
    for i, c in sorted(o["cells"].items()):
        print(f"        cell {i}: accepted {c['accepted']}, units {c['units']}, final gate {c['final_gate']}")
    gate("F1 NON-GENUINE post-science replay on bridge indices: certificates -> bridge identity -> chain -> "
         "assemble -> scientific hash -> final TCB gate + SciPy guard + module binding -> seal -> independent "
         "re-verification; temporary seals deleted", r.returncode == 0 and acc == 2 and o["temporary_seals_deleted"]
         and o["non_genuine_plumbing_replay"] is True, f"{acc}/2 accepted")
    return o


def q_identity_negatives():
    ctxd = dict(source_certificate_hashes={}, auxiliary_evidence_hash=None, producer_manifest_hash="x",
                producer_manifest_schema="s", producer_manifest_path="p", producer_manifest_version=1,
                runtime_contract_hash="r", producer_identity_hash="i", precision_bits=256)
    ok = [RES.resolve("CUSUM", i) == E.bridge_cell(i) for i in (1000, 1001)]
    ctl("F2 cell 1000 and 1001 bridge identities resolve, equal to the entry's certified cells, cells_sha256 bound",
        all(ok) and IDB.canonical_identity(("CUSUM", 1001, "assembly", "5"), **ctxd)["cells_sha256"] == RES.BRIDGE_CELLS_SHA256, str(ok))
    neg("F3 historical index 0 rejected by the bridge resolver", lambda: RES.resolve("CUSUM", 0), "historical")
    neg("F4 historical index 325 rejected", lambda: RES.resolve("CUSUM", 325), "historical")
    neg("F5 unknown index 1002 rejected", lambda: RES.resolve("CUSUM", 1002), "not a k1r6")
    neg("F6 negative (far-field-style) index -1 rejected", lambda: RES.resolve("CUSUM", -1), "not a k1r6")
    neg("F7 SR detector rejected", lambda: RES.resolve("SR", 1000), "cusum bridge cells only")
    neg("F8 canonical_identity on a historical unit rejected (no fallback)",
        lambda: IDB.canonical_identity(("CUSUM", 325, "object", "h_1"), **ctxd), "historical")

    def altered_record():
        t = json.loads(RES.TABLE.read_text())
        c = t["cells"][0]
        c["C_upper"] = c["C_upper"][:-1] + ("3" if c["C_upper"][-1] != "3" else "7")
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "t.json"
            p.write_text(json.dumps(t, indent=1, sort_keys=True) + "\n")
            RES.resolve("CUSUM", 1000, table=p)
    neg("F9 altered bridge record rejected (table hash)", altered_record, "hash")
    neg("F10 altered bridge-table hash (pin) rejected", lambda: RES.resolve("CUSUM", 1000, pinned="0" * 64), "pin altered")

    def hist_chain():
        rec = json.loads((AUX4 / "diagnostics/cells/aux4_CUSUM_325_256.json").read_text())
        CH.build_certificates(rec, E.producer_context(256), "0" * 64)
    neg("F11 bridge certificate chain on historical cell 325 rejected", hist_chain, "historical")


def q_entry_negatives():
    good = E.bridge_cell(1000)
    neg("D2 K1R2 bare-string record", lambda: E.check_schema({**good, "left": "11/2"}), "affine")
    neg("D3 e0 not the midpoint", lambda: E.check_schema({**good, "e0": [str(Fr(good["e0"][0]) + Fr(1, 10 ** 9)), "0/1"]}), "midpoint")
    with tempfile.TemporaryDirectory() as td:
        neg("D4 pre-existing evidence directory", lambda: E.run_cell(1000, td, "q"), "already exists")
    neg("D5 wrong precision", lambda: E.run_cell(1000, "/nonexistent/k1r6", "q", bits=128), "precision")

    def broken_threads():
        old = os.environ.get("BLIS_NUM_THREADS")
        os.environ["OMP_NUM_THREADS"] = "2"
        try:
            E.run_cell(1000, "/nonexistent/k1r6", "q")
        finally:
            os.environ["OMP_NUM_THREADS"] = "1"
    neg("D6 thread contract broken", broken_threads, "thread contract")
    neg("D7 CLI rejects a historical index", lambda: E.main(["--cell", "325", "--evidence-dir", "/x", "--task-id", "q"]), "systemexit")
    neg("D8 unmanifested module loaded (this qualifier)", lambda: E.verify_tcb("negative"), "outside")


def q_tcb_closure_and_no_genuine():
    code = ("import sys, json; sys.path.insert(0, %r); import k1r6_cusum_entry as E; "
            "print(json.dumps({**E.verify_tcb('qualification-import-closure'), **E.verify_k1r6_modules()}))") % str(NS / "driver")
    r = subprocess.run([PY, "-c", code], capture_output=True, text=True, timeout=600)
    gate("H5 TCB gate + K1R6 module binding pass on the production import closure (fresh process)",
         r.returncode == 0 and "k1r6_modules" in r.stdout, (r.stdout or r.stderr).strip()[-160:])
    ev = [p.name for p in (NS / "evidence").rglob("*") if p.is_file() and p.name.startswith(("k1r6_CUSUM", "cell_done"))]
    run = Path("/home/ubuntu/work/k1-bridge-prod/run-20260926T075918Z/logs")
    pids = [json.loads((run / f"SR_{c}.launch.json").read_text())["pid"] for c in range(2000, 2006)]
    alive = [p for p in pids if Path(f"/proc/{p}").exists() and "k1r4_bridge_worker" in Path(f"/proc/{p}/cmdline").read_text()]
    exited = [c for c in range(2000, 2006) if (run / f"SR_{c}.exit.json").exists()]
    gate("I1 no genuine CUSUM 1000/1001 computation in qualification; the 6 running K1R4 SR processes untouched",
         not ev and len(alive) + len(exited) == 6, f"bridge evidence files {ev}; SR launch PIDs alive {len(alive)}/6, exited {exited}")


def main() -> int:
    print("K1R6 CUSUM bridge repair qualification")
    q_frozen_inputs()
    q_generation()
    q_textual_equivalence()
    q_zero_case()
    q_part_b_proofs()
    q_nonzero_equivalence()
    rep = q_post_science_replay()
    q_identity_negatives()
    q_entry_negatives()
    q_tcb_closure_and_no_genuine()
    bad = [g for g in OUT if g["status"] != "PASS"]
    npass = sum(1 for x in NEG if x["expected_reason"])
    res = {"schema": "rebaseguard.p5y.k1r6.qualification.v1", "gates": OUT, "controls": NEG,
           "gates_passed": len(OUT) - len(bad), "gates_total": len(OUT),
           "controls_passed": npass, "controls_total": len(NEG),
           "post_science_replay": {"NON_GENUINE": True, "cells": {i: {k: v for k, v in c.items() if k != "checks"} | {"checks": c["checks"]}
                                                                  for i, c in rep.get("cells", {}).items()}},
           "bridge_post_science_acceptance": f"{sum(1 for c in rep.get('cells', {}).values() if c['accepted'])}/2",
           "verdict": "PASS" if not bad and npass == len(NEG) else "FAIL",
           "genuine_bridge_computation": False, "previous_consumed_unsealed_cpu_h": 0.61,
           "checkpoint_sha256": (CFG / "CHECKPOINT_HASH").read_text().strip()}
    (NS / "evidence/QUALIFICATION_K1R6.json").write_text(json.dumps(res, indent=1, sort_keys=True, default=str) + "\n")
    print(f"\n{res['gates_passed']}/{res['gates_total']} gates, {npass}/{len(NEG)} controls")
    print("K1R6_QUALIFICATION = " + res["verdict"])
    return 0 if res["verdict"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
