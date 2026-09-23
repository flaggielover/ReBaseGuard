"""C11R Phase 12 -- qualification before any target execution. Revision 5. NOT RUN IN THIS TURN.

REVISION 5 (review round 4, N4-4; erratum E34). Revision 4 accepted ANY artifact whose class said
PASS: the item set was never required. The record is now in the TYPED SCHEMA c11r_contract fixes
(QUAL_ITEMS): exactly Q1-Q18, once each, canonical names, status PASS or FAIL, every item bound to
the same contract, approved commit and qualifier; an unknown item REFUSES; the class is derived
from the items and recomputed by the verifier. Q2 now checks tree identity AND history purity over
complete reachable history (R4-1), Q4 also checks what this process actually LOADED (N4-3), and
Q11 runs the status verifier now instead of reading its stored class.

REVISION 4 (review round 3, R3-1; erratum E25). The qualification artifact is built by ONE builder,
emit_qualification, which binds RECOMPUTED identities -- the execution contract, the gate, the
policy, the statement table and this qualifier's own code -- and the host facts the cost model
depends on. c11r_contract.verify_qualification refuses a qualification built under another
contract, tree or host, one whose class does not follow from its items, and a synthetic fixture.
main() runs only with --approved-commit <the reviewed commit>, and checks every frozen path against
it. The configuration is re-derived by the policy's revision-4 rule from the committed cost
artifact and the recorded non-target calibration.

It produces no target constant and computes nothing on cells 306-309. Every numerical re-exercise
runs on the NON-TARGET block NT = [5/2, 5/2 + 108337/1250000] or at the non-target scalar e = 5/2.

REVISION 3 (review round 2, B-5; erratum E18). Revision 2 still loaded the retired screen artifact
(a TARGET computation, deleted from the tree, so the module could not even run), re-exercised
scalar collapse at e = 18355/10000 -- a point inside OPEN cell 307's block -- ran its own cost probe
with a resource cap (5400 s, depth <= 5) that contradicted the frozen policy, and never checked the
policy's configuration. The rewrite takes the frozen policy as the SOLE configuration authority:
depth, panels, cap and safety factor are read from it, and the configuration is RE-DERIVED from the
committed cost artifact by the policy's own pure rule and must equal the frozen one. It reads no
retired artifact, no mixed table, no review prose and no quarantine (the firewall checks it like
every module).

`self_test()` exercises the pure and NON-TARGET components -- the configuration re-derivation, the
host-identity rule, the import scan, scalar collapse and the atom decomposition on NT -- without
writing anything. It is what this turn runs. `main()` runs the full qualification and writes
evidence/qualification/C11R_QUALIFICATION.json; it is for Phase 12, after READY_TO_FREEZE.
"""
from __future__ import annotations

import ast
import pathlib
import shutil
import sys
import time
from fractions import Fraction as F

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import c11r_certificate as CV
import c11r_common as C
import c11r_contract as CT
import c11r_cost as K
import c11r_idrift as I
import c11r_policy as POL
import c11r_procs as PR

X = I.X
NT = I.Blk(F(5, 2), F(5, 2) + F(108337, 1250000))
E_NT = F(5, 2)
FORBIDDEN_GRAPH = frozenset({"taboo_certify", "resolvent_certificate", "opnorms", "ra_certifier",
                             "fast_range", "intervals", "rebaseguard_certify", "rung3_engine",
                             "spec"})
FORBIDDEN_BACKEND = frozenset({"numpy", "scipy", "flint", "mpmath", "sympy", "gmpy2"})
REVIEWED_IDRIFT_COMMIT = "49b17ab4"
HOST_KEYS = ("node", "machine", "cpu_brand", "ncpu", "python", "implementation")


# ---------------------------------------------------------------------------------------------
# pure components
# ---------------------------------------------------------------------------------------------
def rederive_configuration(policy: dict, cost: dict) -> dict:
    """Apply the frozen policy's own rule to the committed cost artifact; compare to the freeze."""
    cfg = policy["configuration"]
    problems = []
    if F(cfg["safety_factor"]) != POL.SAFETY_FACTOR:
        problems.append("the frozen safety factor differs from the policy module's")
    if cfg["cap_seconds"] != POL.CAP_SECONDS or cfg["cap_rss_mb"] != POL.CAP_RSS_MB:
        problems.append("the frozen cap differs from the policy module's")
    if cfg["cost_model"]["source_artifact_sha256"] != cost["sha256"]:
        problems.append("the policy was frozen against a different cost artifact")
    model = POL.cost_model(cost)
    boxes_at = {int(k): v for k, v in cfg["boxes_at_depth"].items()}
    cal = {k: {"metric": v["metric"]} for k, v in cfg.get("calibration", {}).items()}
    _table, best = POL.choose(model, boxes_at, cal)
    derived = None if best is None else {"depth": best["depth"], "panels": best["panels"]}
    if derived != cfg["chosen"]:
        problems.append(f"re-derived configuration {derived} != frozen {cfg['chosen']}")
    return {"frozen": cfg["chosen"], "rederived": derived, "problems": problems}


def host_matches(cost_host: dict, now_host: dict) -> dict:
    """The cost model transfers only to the host it was measured on."""
    diff = {k: [cost_host.get(k), now_host.get(k)] for k in HOST_KEYS
            if cost_host.get(k) != now_host.get(k)}
    return {"match": not diff, "differences": diff}


def imported_roots(src: str) -> set[str]:
    roots = set()
    for n in ast.walk(ast.parse(src)):
        if isinstance(n, ast.Import):
            roots |= {a.name.split(".")[0] for a in n.names}
        elif isinstance(n, ast.ImportFrom) and n.level == 0 and n.module:
            roots.add(n.module.split(".")[0])
    return roots


def forbidden_imports(src: str) -> dict:
    """The production import rule for ONE source: the original certifier's load-bearing graph and
    its arithmetic backend are forbidden. import_scan applies it to the whole closure; the mutation
    suite applies it to planted sources."""
    roots = imported_roots(src)
    return {"graph": sorted(roots & FORBIDDEN_GRAPH), "backend": sorted(roots & FORBIDDEN_BACKEND)}


def import_scan() -> dict:
    closure = {}
    for m in sorted(C.HERE.glob("c11r_*.py")):
        closure.update(C.code_closure(m))
    graph, backend = set(), set()
    for rel in closure:
        f = forbidden_imports(C.read_code(rel))
        graph |= set(f["graph"])
        backend |= set(f["backend"])
    return {"modules": len(closure), "forbidden_graph_hits": sorted(graph),
            "forbidden_backend_hits": sorted(backend), "pass": not graph and not backend}


def scalar_collapse_nt() -> dict:
    """The block layer at a degenerate NON-TARGET drift reproduces C11's scalar certifier."""
    probes, ok = [], True
    PT = I.Blk(E_NT, E_NT)
    for w in ({(0, 0): F(9)}, {(0, 0): F(99, 10), (0, 1): F(-3, 2)}):
        for p, m in ((F(0), F(0)), (F(3), F(1))):
            a, b = X.kernel_apply(w, p, m, E_NT), I.kernel_apply_iv(w, p, m, PT)
            same = (a.lo, a.hi) == (b.lo, b.hi)
            ok = ok and same
            probes.append({"state": [str(p), str(m)], "bit_equal": same})
    return {"drift": "5/2 (non-target)", "probes": probes, "pass": ok}


def atom_decomposition_nt() -> dict:
    one = {(0, 0): F(1)}
    full = I.kernel_apply_iv(one, F(0), F(0), NT)
    hat = I.kernel_apply_iv(one, F(0), F(0), NT, atom_removed=True)
    at = I.atom_contribution_iv(one, F(0), F(0), NT)
    sep = max(full.lo - (hat + at).hi, (hat + at).lo - full.hi)
    return {"block": "NON-TARGET", "separation": float(sep), "pass": sep <= 0}


def self_test() -> dict:
    """The pure and NON-TARGET components, with planted controls. Writes nothing."""
    policy = C.load_allowlisted("config/C11R_POLICY.json")
    cost = C.load_allowlisted("evidence/cost/C11R_COST.json")
    rows = {}
    honest = rederive_configuration(policy, cost)
    rows["rederive_honest"] = {"pass": not honest["problems"], "detail": honest}
    tampered = {**policy, "configuration": {**policy["configuration"],
                                            "chosen": {"depth": 6, "panels": 128}}}
    t = rederive_configuration(tampered, cost)
    rows["rederive_rejects_a_tampered_choice"] = {"pass": bool(t["problems"]), "detail": t}
    raised = {**policy, "configuration": {**policy["configuration"], "cap_seconds": 99999}}
    r = rederive_configuration(raised, cost)
    rows["rederive_rejects_a_raised_cap"] = {"pass": bool(r["problems"]), "detail": r}
    h = cost["host"]
    rows["host_same"] = {"pass": host_matches(h, dict(h))["match"]}
    rows["host_other_cpu_rejected"] = {
        "pass": not host_matches(h, {**h, "cpu_brand": "another cpu"})["match"]}
    rows["import_scan"] = {"pass": import_scan()["pass"]}
    rows["scalar_collapse_nt"] = {"pass": scalar_collapse_nt()["pass"]}
    rows["atom_decomposition_nt"] = {"pass": atom_decomposition_nt()["pass"]}
    return {"rows": rows, "ALL_PASS": all(v["pass"] for v in rows.values()),
            "writes_nothing": True, "computes_on_open_cells": False}


# ---------------------------------------------------------------------------------------------
# the full qualification -- Phase 12 only, NOT run in this turn
# ---------------------------------------------------------------------------------------------
# the qualification artifact -- ONE builder, used by main() and by the synthetic chain controls
# ---------------------------------------------------------------------------------------------
def emit_qualification(repo, items: list, *, approved_commit: str, fixture: bool = False) -> dict:
    """A qualification record in the TYPED SCHEMA (review 4, N4-4; c11r_contract.QUAL_ITEMS):
    every item carries its canonical name, a status PASS or FAIL, and the same binding -- the
    execution contract, the approved commit and THIS qualifier's code as it runs now. The class
    is c11r_contract.qualification_disposition of the items, never set by hand; the verifier
    recomputes it and refuses a record whose stored class differs. Items are given as
    {"id", "status" | "pass", "detail"}; an unknown id is kept, so that the verifier refuses it."""
    roots = CT.chain_roots(repo)
    code = (roots.get("contract") or {}).get("code", {})
    qrel = next((r for r in code if r.endswith("/c11r_qualify.py")), None)
    me_now = CT.code_identity(repo, qrel)["sha256"] if qrel else None
    binding = {"execution_contract_sha256": roots.get("contract_digest"),
               "approved_commit": approved_commit, "qualifier_sha256": me_now}
    typed = []
    for i in items:
        status = i.get("status") or ("PASS" if i.get("pass") else "FAIL")
        typed.append({"id": i["id"], "name": CT.QUAL_ITEMS.get(i["id"], i.get("name")),
                      "status": status, "bound": dict(binding), "detail": i.get("detail", {})})
    d = CT.qualification_disposition(typed, binding)
    return {"schema": CT.QUAL_SCHEMA,
            "fixture": bool(fixture),
            "runs_before": "any target execution",
            "produces_target_constants": False,
            "computes_on_open_cells": False,
            "bound": {"execution_contract_sha256": roots.get("contract_digest"),
                      "gate_sha256": roots.get("gate_digest"),
                      "policy_sha256": roots.get("policy_digest"),
                      "statements_sha256": roots.get("statements_digest"),
                      "approved_commit": approved_commit,
                      "qualifier_sha256": me_now},
            "environment": {"host": CT.current_host()},
            "nt_configuration": {"block": "NON-TARGET [5/2, 5/2 + 108337/1250000]",
                                 "scalar_drift": "5/2", "import_scan": "full code closure"},
            "chain_root_problems": roots["problems"],
            "items": typed,
            "QUALIFICATION_CLASS": d["disposition"]}


def status_verify_only() -> dict:
    """Q11: the status verifier RUN NOW in its read-only mode (it writes nothing)."""
    import subprocess
    r = subprocess.run([sys.executable, str(C.HERE / "c11r_status.py"), "--verify-only"],
                       capture_output=True, text=True)
    last = (r.stdout.strip().splitlines() or [""])[-1]
    return {"exit": r.returncode, "last_line": last[:200],
            "pass": r.returncode == 0 and last.endswith("STATUS_CLASS = CONSISTENT")}


def main(approved_commit: str) -> int:
    """Phase 12 only, on the reviewed commit, on the user's instruction. NOT run in this turn."""
    items = []

    def item(iid, ok, detail):
        items.append({"id": iid, "status": "PASS" if ok else "FAIL", "detail": detail})

    t0 = time.time()
    policy = C.load_allowlisted("config/C11R_POLICY.json")
    gate = C.load_allowlisted("config/N9R_GATE_C11R.json")
    cost = C.load_allowlisted("evidence/cost/C11R_COST.json")
    val = C.load_allowlisted("evidence/validation/C11R_VALIDATION.json")
    mut = C.load_allowlisted("evidence/mutations/C11R_MUTATIONS.json")
    fw = C.load_allowlisted("evidence/firewall/C11R_FIREWALL.json")
    leak = C.load_allowlisted("evidence/leakcheck/C11R_LEAKCHECK.json")
    eq = C.load_allowlisted("evidence/equivalence/C11R_EQUIVALENCE.json")
    chain = C.load_allowlisted("evidence/chain/C11R_CHAIN_CONTROLS.json")

    roots = CT.chain_roots(C.REPO)
    item("Q1", not roots["problems"], {"problems": roots["problems"]})
    fs = CT.frozen_state(C.REPO, approved_commit)
    item("Q2", not (fs["ancestry"] or fs["tree_identity"] or fs["history_purity"]), fs)
    rd = rederive_configuration(policy, cost)
    item("Q3", not rd["problems"], rd)
    contract = CT.contract_at(C.REPO, approved_commit) or {"code": {}}
    exp = CT.expected_certifier_sha(contract) if contract["code"] else {}
    tree_cert = {m: C.sha256_file(C.HERE / m) for m in CV.CERTIFIER_MODULES}
    reviewed = C.sha256_bytes(C.blob_at(REVIEWED_IDRIFT_COMMIT, f"{C.NS_REL}/code/c11r_idrift.py"))
    loaded = CT.verify_loaded_modules(contract) if contract["code"] else {"problems": ["no contract"]}
    loaded["problems"] = loaded["problems"] + (CT.code_dir_shadows(contract, C.REPO)
                                               if contract["code"] else [])
    item("Q4", exp == tree_cert and tree_cert["c11r_idrift.py"] == reviewed
         and not loaded["problems"],
         {"contract": exp, "tree": tree_cert, "reviewed_idrift": reviewed,
          "loaded_modules": loaded})
    sc = import_scan()
    item("Q5", sc["pass"], sc)
    tc = C.toolchain_present()
    item("Q6", not tc["numpy"] and not tc["flint"], {"importlib_find_spec": tc})
    item("Q7", val["VALIDATION_CLASS"] == "PASS", {"failed": val["failed"]})
    item("Q8", mut["MUTATION_CLASS"] == "PASS", {"class": mut["MUTATION_CLASS"]})
    item("Q9", fw["FIREWALL_CLASS"] == "PASS", {})
    item("Q10", leak["LEAK_CLASS"] == "PASS", {})
    sv = status_verify_only()
    item("Q11", sv["pass"], sv)
    item("Q12", eq["EQUIV_CLASS"] == "READY" and eq["self_test"]["PASS"] is True, {})
    item("Q13", scalar_collapse_nt()["pass"], scalar_collapse_nt())
    item("Q14", atom_decomposition_nt()["pass"], atom_decomposition_nt())
    item("Q15", chain.get("CHAIN_CLASS") == "PASS", {"failed": chain.get("failed")})
    hm = host_matches(cost["host"], K.host_identity())
    item("Q16", hm["match"], hm)
    workers = PR.campaign_workers()["workers"]
    auth_exists = CT.artifact_exists(C.REPO, CT.AUTH_REL)
    runs_exists = (C.NS / "evidence" / "runs").exists()
    item("Q17", gate["guard"] == "DENY" and not auth_exists and not runs_exists and not workers,
         {"gate_guard": gate["guard"], "authorization_exists": auth_exists,
          "runs_exists": runs_exists, "workers": workers})
    du = shutil.disk_usage(str(C.REPO))
    item("Q18", du.free > 2 * 1024 ** 3, {"disk_free_gb": round(du.free / 1024 ** 3, 1)})

    out = emit_qualification(C.REPO, items, approved_commit=approved_commit)
    out["seconds"] = round(time.time() - t0, 1)
    s = C.write_evidence(C.NS / "evidence" / "qualification" / "C11R_QUALIFICATION.json", out,
                         producer=__file__)
    for i in out["items"]:
        print(f"  {i['status']:4s}  {i['id']:4s} {i['name'][:80]}")
    print(f"\nQUALIFICATION_CLASS = {out['QUALIFICATION_CLASS']} (recomputed from the items)")
    print(f"wrote evidence/qualification/C11R_QUALIFICATION.json sha256 {s[:16]}...")
    return 0 if out["QUALIFICATION_CLASS"] == "PASS" else 1


if __name__ == "__main__":
    if sys.argv[1:] == ["--self-test"]:
        r = self_test()
        for k, v in r["rows"].items():
            print(f"  {'PASS' if v['pass'] else 'FAIL'}  {k}")
        print(f"\nqualifier self-test ALL_PASS = {r['ALL_PASS']} (wrote nothing)")
        raise SystemExit(0 if r["ALL_PASS"] else 1)
    if len(sys.argv) == 3 and sys.argv[1] == "--approved-commit":
        raise SystemExit(main(sys.argv[2]))
    print("c11r_qualify.py runs only as Phase 12, on the reviewed commit, on the user's "
          "instruction: --approved-commit <sha>. Use --self-test for the pure non-target checks.")
    raise SystemExit(2)
