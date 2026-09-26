"""K1R5 qualification. NO certificate solve: prepare()/certify()/run_cell science never execute."""
import ast
import copy
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from fractions import Fraction as Fr
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
CFG = NS / "config"
REPO = Path("/home/ubuntu/work/ReBaseGuard")
AUX4 = REPO / "level4/closure_proofs/p5y_k1_cusum_aux4_fullcover"
sys.path.insert(0, str(NS / "driver"))
import k1r5_cusum_entry as E                                        # noqa: E402
OUT, NEG = [], []


def gate(name, ok, detail=""):
    OUT.append({"gate": name, "status": "PASS" if ok else "FAIL", "detail": detail})
    print(f"  {'PASS' if ok else 'FAIL'}  {name}" + (f" -- {detail}" if detail else ""))


def neg(name, fn, expect):
    try:
        fn()
    except (Exception, SystemExit) as e:                            # noqa: BLE001
        ok = expect.lower() in f"{type(e).__name__}: {e}".lower()
        NEG.append({"control": name, "rejected": True, "expected_reason": ok, "reason": str(e)[:150]})
        print(f"  {'PASS' if ok else 'FAIL'}  NEG {name} -- {type(e).__name__}: {str(e)[:100]}")
        return
    NEG.append({"control": name, "rejected": False, "expected_reason": False})
    print(f"  FAIL  NEG {name} -- ACCEPTED")


def q1_q2_decode():
    good = 0
    for idx in E.BRIDGE_INDICES:
        cell = E.bridge_cell(idx)
        c = E.aux_certifier.Aux3Certifier(copy.deepcopy(cell), bits=256)   # __init__ only
        L, R, e, r, C = (Fr(cell["left"][0]), Fr(cell["right"][0]), Fr(cell["e0"][0]),
                         Fr(cell["rho"][0]), Fr(cell["C_upper"]))
        ok = ((c.left, c.right, c.e0, c.rho, c.C) == (L, R, e, r, C) and c.e0 == (L + R) / 2
              and c.rho == (R - L) / 2 and not hasattr(c, "obj"))
        good += ok
        print(f"        cell {idx}: left {c.left} right {c.right} e0 {c.e0} rho {c.rho} C {c.C}")
    gate("1 both bridge records decode exactly through the real frozen certifier", good == 2, f"{good}/2")
    gate("2 exact left/right/e0/rho/C_upper + midpoint/half-width assertions", good == 2)


def q3_accepts_exactly_two():
    ok = [E.bridge_cell(i)["index"] for i in (1000, 1001)] == [1000, 1001]
    import argparse                                                     # noqa: F401
    gate("3 production entry accepts exactly the two bridge indices",
         ok and tuple(E.BRIDGE_INDICES) == (1000, 1001))


def q7_kernel():
    aux = json.loads((AUX4 / "manifests/producer_manifest_v2.json").read_text())
    drift = [f for f, h in aux["files"].items() if E._sha(REPO / f) != h]
    man = json.loads((CFG / "PRODUCER_MANIFEST.json").read_text())["files"]
    k1 = [f for f, h in man.items() if E._sha(f) != h]
    q4 = E._sha(AUX4 / "code/qualify4.py") == aux["files"]["level4/closure_proofs/p5y_k1_cusum_aux4_fullcover/code/qualify4.py"]
    gate("7 frozen kernel files byte-identical (58 aux4 files; qualify4 incl. its production guard)",
         not drift and not k1 and q4, f"aux4 drift {drift}, K1R5 manifest drift {k1}")


def q_ast_identity():
    src = (AUX4 / "code/qualify4.py").read_text()
    rc = next(n for n in ast.parse(src).body if isinstance(n, ast.FunctionDef) and n.name == "run_cell")
    wsrc = (NS / "driver/k1r5_cusum_entry.py").read_text()
    wtree = ast.parse(wsrc)
    cf = next(n for n in wtree.body if isinstance(n, ast.FunctionDef) and n.name == "certify")
    d = lambda n: ast.dump(n, include_attributes=False)                 # noqa: E731
    i = next(k for k, s in enumerate(rc.body) if isinstance(s, ast.Assign) and d(s.targets[0]) == d(ast.Name(id="threading", ctx=ast.Store())))
    frozen = [s for s in rc.body[i:] if not (isinstance(s, ast.Assign) and d(s.targets[0]) == d(ast.Name(id="cell", ctx=ast.Store())))]
    fh, fg = frozen[:3], frozen[3]                                       # threading, t0/w0, guard ; with guard
    wh, wg = cf.body[:3], cf.body[3]
    head_ok = [d(x) for x in fh] == [d(x) for x in wh]
    items_ok = d(fg.items[0]) == d(wg.items[0])
    fb, wb = fg.body, wg.body
    same = [d(fb[k]) == d(wb[k]) for k in (0, 1, 2, 4, 5)]               # workprec block, aux record, aux_hash, certs, chain
    ctx_ok = d(fb[3].targets[0]) == d(wb[3].targets[0]) and "ID" in d(fb[3].value) and "producer_context" in d(wb[3].value)
    forbidden = [n.attr for n in ast.walk(wtree) if isinstance(n, ast.Attribute)
                 and n.attr in ("run_cell", "initial_gate", "final_gate", "context") and
                 isinstance(n.value, ast.Name) and n.value.id in ("Q4", "manifest_v2", "ID")]
    gate("AST: certify() is the frozen run_cell block verbatim (only cell source and ctx differ)",
         head_ok and items_ok and all(same) and ctx_ok and not forbidden,
         f"head {head_ok}, with-items {items_ok}, block stmts {same}, ctx {ctx_ok}, forbidden calls {forbidden}")


def q8_schema():
    s = json.loads((CFG / "RESULT_SCHEMA.json").read_text())
    hist = json.loads((AUX4 / "diagnostics/cells/aux4_CUSUM_325_256.json").read_text())
    tree = ast.parse((NS / "driver/k1r5_cusum_entry.py").read_text())
    asm = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "assemble")
    upd = next(n for n in ast.walk(asm) if isinstance(n, ast.Call) and getattr(n.func, "attr", "") == "update")
    keys = {k.value for k in upd.args[0].keys if isinstance(k, ast.Constant)}
    ok = (set(s["output_record"]["top_level_keys"]) == set(hist) | {"k1r5_bridge"}
          and keys <= set(s["output_record"]["top_level_keys"]))
    gate("8 result schema explicitly frozen (aux4 record keys + k1r5_bridge; assemble() writes only schema keys)",
         ok, f"{len(s['output_record']['top_level_keys'])} keys; assemble writes {len(keys)}")


def q9_q10_seal():
    """Plumbing only, on HISTORICAL aux4 data (not a bridge result; nothing persisted)."""
    rec = json.loads((AUX4 / "diagnostics/cells/aux4_CUSUM_325_256.json").read_text())
    rec["k1r5_bridge"] = {"index": 1000, "plumbing_test": True, "k1r5_checkpoint_sha256": "0" * 64}
    h1, h2 = E.H.record_scientific_hash(copy.deepcopy(rec)), E.H.record_scientific_hash(copy.deepcopy(rec))
    rec["scientific_content_hash"] = h1
    with tempfile.TemporaryDirectory() as td:
        a, b = Path(td) / "a", Path(td) / "b"
        ma, mb = E.seal(a, 1000, rec, "plumbing"), E.seal(b, 1000, rec, "plumbing")
        same_bytes = (a / "k1r5_CUSUM_1000_256.json").read_bytes() == (b / "k1r5_CUSUM_1000_256.json").read_bytes()
        same_marker = {k: v for k, v in ma.items() if k != "completed_utc"} == \
                      {k: v for k, v in mb.items() if k != "completed_utc"}
        collide = False
        try:
            E.seal(a, 1000, rec, "plumbing")
        except FileExistsError:
            collide = True
        files = sorted(p.name for p in a.iterdir())
    gate("9 evidence directory per-cell and collision-free", collide and files == ["cell_done_1000.json", "k1r5_CUSUM_1000_256.json"],
         f"re-seal into an existing dir refused: {collide}; files {files}")
    gate("10 sealing and scientific-content hash deterministic", h1 == h2 and same_bytes and same_marker,
         "hash_v2 twice equal; two seals byte-identical (marker equal except completed_utc)")


def q_tcb_import_closure():
    code = ("import sys; sys.path.insert(0, %r); import k1r5_cusum_entry as E; "
            "import json; print(json.dumps(E.verify_tcb('qualification-import-closure')))") % str(NS / "driver")
    r = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, timeout=600)
    ok = r.returncode == 0 and "loaded_repository_modules" in r.stdout
    gate("TCB gate passes on the production import closure (fresh process)", ok, (r.stdout or r.stderr).strip()[-160:])


def negatives():
    good = E.bridge_cell(1000)
    bare = {**good, "left": "11/2", "right": "95887899/16777216", "e0": "188162587/33554432", "rho": "3613211/33554432"}
    neg("1 K1R2 bare-string record", lambda: E.check_schema(bare), "affine")
    neg("2 e0 not the midpoint", lambda: E.check_schema({**good, "e0": [str(Fr(good["e0"][0]) + Fr(1, 10**9)), "0/1"]}), "midpoint")
    neg("3 rho not the half-width", lambda: E.check_schema({**good, "rho": [str(Fr(good["rho"][0]) + Fr(1, 10**9)), "0/1"]}), "half-width")
    def mutated_table():
        t = json.loads(E.K1R4_TABLE.read_text())
        t["cells"][0]["C_upper"] = t["cells"][0]["C_upper"][:-1] + ("3" if t["cells"][0]["C_upper"][-1] != "3" else "7")
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "t.json"
            p.write_text(json.dumps(t, indent=1, sort_keys=True) + "\n")
            saved, E.K1R4_TABLE = E.K1R4_TABLE, p
            try:
                E.bridge_cell(1000)
            finally:
                E.K1R4_TABLE = saved
    neg("4 one-digit mutated bridge record", mutated_table, "frozen hash")
    neg("5 historical CUSUM index 0 as new work", lambda: E.bridge_cell(0), "historical")
    neg("6 historical CUSUM index 325 as new work", lambda: E.bridge_cell(325), "historical")
    neg("7 unknown bridge index 1002", lambda: E.bridge_cell(1002), "not a k1r5")
    with tempfile.TemporaryDirectory() as td:
        neg("8 pre-existing evidence directory", lambda: E.run_cell(1000, td, "q"), "already exists")
    neg("9 wrong precision", lambda: E.run_cell(1000, "/nonexistent/k1r5", "q", bits=128), "precision")
    def broken_threads():
        old = os.environ.get("OMP_NUM_THREADS")
        os.environ["OMP_NUM_THREADS"] = "2"
        try:
            E.run_cell(1000, "/nonexistent/k1r5", "q")
        finally:
            os.environ["OMP_NUM_THREADS"] = old
    neg("10 thread contract broken", broken_threads, "thread contract")
    neg("11 CLI rejects a historical index", lambda: E.main(["--cell", "325", "--evidence-dir", "/x", "--task-id", "q"]), "systemexit")
    neg("12 unmanifested module loaded (this qualifier)", lambda: E.verify_tcb("negative"), "outside")
    rej = sum(1 for x in NEG if x["rejected"] and x["expected_reason"])
    gate("negative controls rejected for the expected reason", rej == len(NEG), f"{rej}/{len(NEG)}")


def q11_concurrency_and_no_solve():
    ev = [p.name for p in (NS / "evidence").rglob("*") if p.is_file() and p.name.startswith(("k1r5_CUSUM", "cell_done"))]
    gate("11 no genuine certificate solve has run", not ev, f"bridge evidence files: {ev}")
    k4w = (NS.parent / "p5y_k1r4_bridge_successor/driver/k1r4_bridge_cellseq.py").read_text()
    k5w = (NS / "driver/k1r5_cusum_entry.py").read_text()
    c = json.loads((CFG / "CONCURRENCY.json").read_text())
    ok = ("mkdir(parents=True, exist_ok=False)" in k4w and "mkdir(parents=True, exist_ok=False)" in k5w
          and c["shared_mutable_files"] == [] and "flock" not in k5w and "flock" not in k4w
          and c["resources"]["combined_peak_gib"] < c["resources"]["host_ram_gib"]
          and c["resources"]["processes"] <= c["resources"]["physical_cores"])
    gate("CUSUM can run concurrently with K1R4 SR (disjoint evidence roots, no shared file/lock, per-process single-thread, 8 procs <= 16 cores, 2.2 of 123 GiB)", ok)
    return ok


def main() -> int:
    print("K1R5 CUSUM-entry qualification")
    q1_q2_decode()
    q3_accepts_exactly_two()
    q_ast_identity()
    q7_kernel()
    q8_schema()
    q9_q10_seal()
    q_tcb_import_closure()
    negatives()
    conc = q11_concurrency_and_no_solve()
    bad = [g for g in OUT if g["status"] != "PASS"]
    res = {"schema": "rebaseguard.p5y.k1r5.qualification.v1", "gates": OUT, "negative_controls": NEG,
           "gates_passed": len(OUT) - len(bad), "gates_total": len(OUT),
           "negatives_passed": sum(1 for x in NEG if x["rejected"] and x["expected_reason"]),
           "negatives_total": len(NEG), "cusum_can_run_concurrently_with_k1r4_sr": conc,
           "verdict": "PASS" if not bad else "FAIL", "decisive_computation": False,
           "checkpoint_sha256": (CFG / "CHECKPOINT_HASH").read_text().strip()}
    (NS / "evidence/QUALIFICATION_K1R5.json").write_text(json.dumps(res, indent=1, sort_keys=True) + "\n")
    print(f"\n{res['gates_passed']}/{res['gates_total']} gates, {res['negatives_passed']}/{res['negatives_total']} negatives")
    print("K1R5_QUALIFICATION = " + res["verdict"])
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
