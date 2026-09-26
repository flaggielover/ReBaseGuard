"""K1R4 qualification: the twelve pre-freeze gates plus negative controls. NO decisive solve."""
import copy
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from fractions import Fraction as Fr
from pathlib import Path

for k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS",
          "BLIS_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[k] = "1"
NS = Path(__file__).resolve().parents[1]
CFG = NS / "config"
ROOT = Path("/home/ubuntu/work/ReBaseGuard")
sys.path.insert(0, str(NS / "driver"))
sys.path.insert(0, str(NS / "code"))
import k1r4_bridge_worker as W                                      # noqa: E402
OUT, NEG = [], []
C_SR_A = (4581762885148045, 8796093022208)
Q, A_DEN, A_NUM, C_DEN = 10_000_000, 1152921504606846976, 919898268343412807, 4294967296
OLD = Fr(3803026123175981, 562949953421312)
E_CLOSE = Fr(1883835, 262144)


def j(n):
    return json.loads((CFG / n).read_text())


def gate(name, ok, detail=""):
    OUT.append({"gate": name, "status": "PASS" if ok else "FAIL", "detail": detail})
    print(f"  {'PASS' if ok else 'FAIL'}  {name}" + (f" -- {detail}" if detail else ""))


def neg(name, fn, expect):
    try:
        fn()
    except Exception as e:                                          # noqa: BLE001
        ok = expect.lower() in str(e).lower()
        NEG.append({"control": name, "rejected": True, "reason": str(e)[:160], "expected_reason": ok})
        print(f"  {'PASS' if ok else 'FAIL'}  NEG {name} -- {type(e).__name__}: {str(e)[:110]}")
        return
    NEG.append({"control": name, "rejected": False})
    print(f"  FAIL  NEG {name} -- was ACCEPTED")


def arb_env():
    sys.path[:0] = [str(ROOT / "rebaseguard-proof/src")]
    from flint import arb
    from rebaseguard_certify.arb_backend import workprec, rational
    return arb, workprec, rational


def g1_q_sr():
    arb, workprec, rational = arb_env()
    d = j("Q_SR_DERIVATION.json")
    wit = json.loads((ROOT / "level4/closure_proofs/p5y_k1_cover_ledger_successor/config/cover_witnesses.json").read_text())
    with workprec(1024):
        c = (arb(C_SR_A[0]) / arb(C_SR_A[1])).log() + rational(1, 2)
        lo, hi = int((c.lower() * Q).floor().fmpq()), int((c.upper() * Q).floor().fmpq())
        qs = Fr(d["q_SR"])
        below = c - arb(qs.numerator) / arb(qs.denominator)
        nxt = arb(lo + 1) / arb(Q) - c
    ok = (lo == hi == wit["detectors"]["SR"]["terminal_floor_q"] and qs == Fr(lo, Q)
          and below.lower() > 0 and nxt.lower() > 0)
    gate("G1 q_SR derived from the frozen grid, q_SR < c_SR, canonical predecessor", ok,
         f"q_SR={d['q_SR']}, c_SR-q_SR={below.str(8)}, next-c_SR={nxt.str(8)} (1024-bit recheck)")
    return c


def g2_gap_free(c):
    arb, workprec, rational = arb_env()
    tab = j("SR_BRIDGE_CELL_TABLE.json")["cells"]
    qs = Fr(j("Q_SR_DERIVATION.json")["q_SR"])
    chain = all(Fr(a["right"][0]) == Fr(b["left"][0]) for a, b in zip(tab, tab[1:]))
    with workprec(1024):
        qa, ea = arb(qs.numerator) / arb(qs.denominator), arb(E_CLOSE.numerator) / arb(E_CLOSE.denominator)
        order = (c - qa).lower() > 0 and (ea - c).lower() > 0
    cu = j("CUSUM_BRIDGE_CELL_TABLE.json")["cells"]
    cchain = (Fr(cu[0]["left"][0]) == Fr(11, 2) and Fr(cu[0]["right"][0]) == Fr(cu[1]["left"][0])
              and Fr(cu[1]["right"][0]) == Fr(49750555, 8388608))
    ok = (Fr(tab[0]["left"][0]) == qs and Fr(tab[-1]["right"][0]) == E_CLOSE and chain and order and cchain
          and j("DOMAIN_COMPOSITION.json")["SR"]["uncovered_domain_width"] == "0")
    gate("G2 gap-free union (SR overlap [q_SR, c_SR]; CUSUM exact at 11/2)", ok,
         "[0,c_SR] U [q_SR,e_close] U [e_close,inf) and [0,11/2] U (11/2,e_close] U [e_close,inf)")


def cusum_schema_ok(cell) -> None:
    for f in ("left", "right", "e0", "rho"):
        v = cell[f]
        if not (isinstance(v, list) and len(v) == 2 and all(isinstance(x, str) for x in v) and Fr(v[1]) == 0):
            raise ValueError(f"CUSUM {f}: affine [p, '0/1'] pair required (K1R2 schema defect)")
    if not isinstance(cell["C_upper"], str) or isinstance(cell["C_upper"], list):
        raise ValueError("CUSUM C_upper: plain rational string required")


def g3_cusum():
    sys.path_backup = list(sys.path)
    R = ROOT / "level4/closure_proofs"
    for p in ("p5y_k1_cusum_aux4_fullcover", "p5y_k1_cusum_aux3_successor", "p5y_k1_cusum_completion_successor",
              "p5y_k1_final_completion", "p5y_k1_cover_ledger_repair2", "p5y_k1_cover_ledger_repair1",
              "p5y_k1_cover_ledger_implementation"):
        sys.path.append(str(R / p / "code"))
    import aux_certifier
    good = 0
    for cell in j("CUSUM_BRIDGE_CELL_TABLE.json")["cells"]:
        cusum_schema_ok(cell)
        c = aux_certifier.Aux3Certifier(copy.deepcopy(cell), bits=256)     # __init__ only; no prepare()
        L, Rr, E, H, C = (Fr(cell["left"][0]), Fr(cell["right"][0]), Fr(cell["e0"][0]),
                          Fr(cell["rho"][0]), Fr(cell["C_upper"]))
        if (c.left, c.right, c.e0, c.rho, c.C) == (L, Rr, E, H, C) and c.e0 == (L + Rr) / 2 \
                and c.rho == (Rr - L) / 2 and not hasattr(c, "obj"):
            good += 1
    gate("G3 CUSUM real-entry schema acceptance", good == 2, f"{good}/2 decoded exactly, no prepare()")
    return aux_certifier


def g4_universe():
    sys.path.insert(0, str(ROOT / "level4/closure_proofs/p5y_k1_cover_ledger_repair2/code"))
    import certhash
    W.setup_path()
    import k1r4_bridge_cells as SC
    SC.set_mode("BRIDGE")
    import k1r4_bridge_t5 as S5
    u = j("SR_BRIDGE_UNIVERSE.json")
    ok, n = len(certhash.OBJECTS) == 19, 0
    for rec in j("SR_BRIDGE_CELL_TABLE.json")["cells"]:
        built = [[x[0], rec["id"], x[2], x[3]]
                 for x in S5.universe.work_ids(cells=[SC.universe_carrier(rec)]) if x[2] != "far_field"]
        kinds = {}
        for x in built:
            kinds[x[2]] = kinds.get(x[2], 0) + 1
        good = (sorted(map(tuple, built)) == sorted(map(tuple, u["cells"][rec["id"]]["units"]))
                and kinds == {"object": 19, "dependency_bundle": 1, "curvature": 4, "assembly": 4})
        n += good
    gate("G4 SR obligation universe re-derived from definitions (19+1+4+4 = 28)", ok and n == 6,
         f"{n}/6 cells; certhash.OBJECTS has {len(certhash.OBJECTS)} objects")


def g5_reproducible():
    import make_bridge_stages as G
    with tempfile.TemporaryDirectory() as td:
        G.OUT = Path(td)
        man = G.generate()
        ok = all((Path(td) / n).read_bytes() == (NS / "driver" / n).read_bytes() for n in man["stages"])
    tm = j("TRANSFORMATION_MANIFEST.json")
    ok &= {k: v["generated_sha256"] for k, v in man["stages"].items()} == \
          {k: v["generated_sha256"] for k, v in tm["stages"].items()}
    subs = sum(len(v["substitutions"]) for v in tm["stages"].values())
    gate("G5 generated-stage reproducibility (fail-closed, counted substitutions)", ok,
         f"{len(man['stages'])} stages regenerated byte-identically; {subs} asserted substitutions")


def g6_replay():
    r = subprocess.run([sys.executable, str(NS / "ops/replay_369.py")], capture_output=True, text=True,
                       env=dict(os.environ, K1R4_REPLAY_PROCS="24"), timeout=1500)
    rep = json.loads((NS / "evidence/REPLAY_369.json").read_text())
    ok = (r.returncode == 0 and rep["cells_replayed"] == 369 and rep["cells_equivalent"] == 369
          and rep["scientific_leaf_differences"] == 0 and rep["patch_solves"] == 0)
    gate("G6 369/369 historical equivalence replay through generated stages", ok,
         f"{rep['cells_equivalent']}/369 equivalent, t5 bytes identical {rep['t5_bytes_identical']}, "
         f"hash matches {rep['scientific_content_hash_matches']}, {rep['cpu_s_total']} CPU-s")
    gate("G7 scientific leaf differences = 0", rep["scientific_leaf_differences"] == 0,
         str(rep["scientific_leaf_differences"]))


def g8_g9_entry():
    tab = j("SR_BRIDGE_CELL_TABLE.json")
    qs = Fr(j("Q_SR_DERIVATION.json")["q_SR"])
    expected, left = [], qs.numerator * (Q // qs.denominator)       # independent re-derivation
    for p in tab["bridge_parents"]:
        right = Fr(left + p["step_q"], Q)
        right = E_CLOSE if right > E_CLOSE else right
        a0 = Fr(left, Q)
        k = next(k for k in (1, 2, 4, 8, 16, 32, 64) if ((right - a0) / k) / 2 <= Fr(1, 25))
        expected += [(a0 + i * (right - a0) / k, a0 + (i + 1) * (right - a0) / k) for i in range(k)]
        left += p["step_q"]
    accepted, exact = 0, 0
    for c, (a, b) in zip(tab["cells"], expected):
        adm = W.admit(c["index"])
        accepted += 1
        g = adm["geometry"]
        for name, want in (("left", a), ("right", b), ("e0", (a + b) / 2), ("rho", (b - a) / 2)):
            from flint import arb, ctx
            saved = ctx.prec
            ctx.prec = 1024
            try:
                ok_contains = g[name].contains(arb(want.numerator) / arb(want.denominator))
            finally:
                ctx.prec = saved
            if not ok_contains:
                break
        else:
            exact += 1
    gate("G8 SR bridge entry acceptance through the ACTUAL production entry", accepted == len(tab["cells"]),
         f"{accepted}/{len(tab['cells'])}")
    gate("G9 exact decoded geometry equals independently derived values", exact == len(tab["cells"]),
         f"{exact}/{len(tab['cells'])} cells: left/right/e0/rho balls contain the independent exact values")


def compose_sr(lower: Fr, c) -> None:
    """The SR composition gate: a bridge lower endpoint must lie strictly below exact c_SR."""
    from flint import arb
    if not (c - arb(lower.numerator) / arb(lower.denominator)).lower() > 0:
        raise ValueError(f"bridge lower endpoint {lower} is not strictly below c_SR: uncovered gap")


def g10_negatives(c, aux_certifier):
    W.setup_path()
    import k1r4_bridge_cells as SC
    SC.set_mode("BRIDGE")
    good = copy.deepcopy(j("SR_BRIDGE_CELL_TABLE.json")["cells"][0])
    cu = copy.deepcopy(j("CUSUM_BRIDGE_CELL_TABLE.json")["cells"][0])
    bare = {**cu, "left": "11/2", "right": "95887899/16777216", "e0": "188162587/33554432",
            "rho": "3613211/33554432"}
    neg("1 K1R2 bare-string CUSUM schema defect", lambda: cusum_schema_ok(bare), "affine")
    k1r2 = aux_certifier.Aux3Certifier(bare, bits=256)
    NEG.append({"control": "1b K1R2 defect is SILENT inside the kernel (why the schema gate exists)",
                "rejected": True, "expected_reason": k1r2.e0 == 1,
                "reason": f"kernel decodes e0 = {k1r2.e0} instead of 188162587/33554432"})
    print(f"  {'PASS' if k1r2.e0 == 1 else 'FAIL'}  NEG 1b silent kernel decode e0 = {k1r2.e0} (proves the gate is necessary)")
    def mutate(f, v):
        r = copy.deepcopy(good); r[f] = v; return r
    e0 = Fr(good["e0"][0]); rho = Fr(good["rho"][0])
    import sr_o9_candidates as T

    def geometry_with_table(bad):
        """Make the mutated record the ACTIVE table entry, so byte-identity passes and the
        frozen geometry gate itself must refuse it."""
        tab = copy.deepcopy(j("SR_BRIDGE_CELL_TABLE.json"))
        tab["cells"][0] = bad
        with tempfile.TemporaryDirectory() as td:
            tp = Path(td) / "t.json"
            tp.write_text(json.dumps(tab, indent=1, sort_keys=True) + "\n")
            SC.TABLE = tp
            try:
                with T.scientific_precision():
                    SC.geometry(bad)
            finally:
                SC.TABLE = SC.BRIDGE_TABLE
    neg("2 e0 not the midpoint",
        lambda: geometry_with_table(mutate("e0", [str(e0 + Fr(1, 10**9)), "0/1"])), "e0 != (left+right)/2")
    neg("3 rho not the half-width",
        lambda: geometry_with_table(mutate("rho", [str(rho + Fr(1, 10**9)), "0/1"])), "rho != (right-left)/2")
    cup = good["C_upper"]; flip = cup[:-1] + ("7" if cup[-1] != "7" else "3")
    neg("4 one-digit mutated bridge record", lambda: SC.validate(mutate("C_upper", flip)), "differs")
    neg("5 historical PS1 index as new bridge work (entry)", lambda: W.admit(0), "not in the bridge ownership")
    neg("5b historical PS1 index at the registry", lambda: SC.cell(0), "inherited evidence")
    neg("6 unknown bridge index", lambda: W.admit(2006), "not in the bridge ownership")
    def bad_universe():
        import k1r4_bridge_t5 as S5
        built = [[x[0], good["id"], x[2], x[3]] for x in S5.universe.work_ids(cells=[SC.universe_carrier(good)])
                 if x[2] != "far_field"]
        declared = j("SR_BRIDGE_UNIVERSE.json")["cells"][good["id"]]["units"][:-1]       # one unit dropped
        if sorted(map(tuple, built)) != sorted(map(tuple, declared)):
            raise ValueError("obligation universe does not match the frozen declaration")
    neg("7 invalid bridge obligation universe", bad_universe, "does not match")
    ps1_sha = "dfaced89653bd71a0bab4a61729407694768456b1e841f042df84c4544bfe349"
    neg("8 PS1 successor_cells_sha256 substituted", lambda: W.admit(2000, successor_cells_sha256=ps1_sha),
        "not the bridge table")
    neg("9 VULTR host", lambda: W.admit(2000, role="VULTR"), "aws only")
    neg("9b non-AWS runtime vendor", lambda: W.admit(2000, host={"sys_vendor": "Vultr"}), "not the qualified aws")
    neg("10 synthetic task", lambda: W.admit(2000, task_kind="SYNTHETIC"), "synthetic")
    neg("10b handoff path", lambda: W.admit(2000, handoff=True), "handoff")
    neg("11 K1R/K1R3 gap endpoint (3.0e-17 above c_SR)", lambda: compose_sr(OLD, c), "uncovered gap")
    rej = sum(1 for x in NEG if x["rejected"] and x["expected_reason"])
    gate("G10 negative controls rejected for the expected reason", rej == len(NEG), f"{rej}/{len(NEG)}")


def g11_runtime():
    import flint
    h = W.host_facts()
    rt = j("RUNTIME_CONTRACT.json")["SR_BRIDGE"]
    ok = (h["sys_vendor"] == rt["sys_vendor"] and sys.executable == rt["python"]
          and flint.__version__ == rt["python_flint"] and os.cpu_count() == rt["online_cpus"])
    gate("G11 AWS runtime qualification", ok,
         f"{h['sys_vendor']}, {sys.executable}, flint {flint.__version__}, {os.cpu_count()} cpus")


def g12_no_solve():
    bad = [p.name for p in (NS / "evidence").rglob("*")
           if p.is_file() and (p.name.startswith(("patches_", "t3_", "t4_", "t5_", "cell_done")))]
    cp = j("CHECKPOINT.json")
    gate("G12 no genuine scientific bridge solve has occurred",
         not bad and cp["production_started"] is False and j("COST_ACCOUNTING.json")["consumed_genuine_cpu_h"] == 0.0,
         f"bridge evidence files: {bad}")


def main() -> int:
    print("K1R4 qualification")
    W.verify_freeze()
    c = g1_q_sr()
    g2_gap_free(c)
    aux = g3_cusum()
    g4_universe()
    g5_reproducible()
    g6_replay()
    g8_g9_entry()
    g10_negatives(c, aux)
    g11_runtime()
    g12_no_solve()
    bad = [g for g in OUT if g["status"] != "PASS"]
    res = {"schema": "rebaseguard.p5y.k1r4.qualification.v1", "gates": OUT, "negative_controls": NEG,
           "gates_passed": len(OUT) - len(bad), "gates_total": len(OUT),
           "negatives_passed": sum(1 for x in NEG if x["rejected"] and x["expected_reason"]),
           "negatives_total": len(NEG), "verdict": "PASS" if not bad else "FAIL",
           "decisive_computation": False, "genuine_cpu_h": 0.0,
           "checkpoint_sha256": (CFG / "CHECKPOINT_HASH").read_text().strip()}
    (NS / "evidence/QUALIFICATION_K1R4.json").write_text(json.dumps(res, indent=1, sort_keys=True) + "\n")
    print(f"\n{res['gates_passed']}/{res['gates_total']} gates, {res['negatives_passed']}/{res['negatives_total']} negatives")
    print("K1R4_QUALIFICATION = " + res["verdict"])
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
