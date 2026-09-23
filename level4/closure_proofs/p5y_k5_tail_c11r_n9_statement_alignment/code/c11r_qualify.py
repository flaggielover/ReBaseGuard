"""C11R Phase 12 -- qualification before any target execution. Revision 3. NOT RUN IN THIS TURN.

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
import subprocess
import sys
import time
from fractions import Fraction as F

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import c11r_certificate as CV
import c11r_common as C
import c11r_cost as K
import c11r_idrift as I
import c11r_policy as POL

X = I.X
NT = I.Blk(F(5, 2), F(5, 2) + F(108337, 1250000))
E_NT = F(5, 2)
FROZEN_ARTIFACTS = ("config/C11R_POLICY.json", "config/N9R_GATE_C11R.json",
                    "evidence/table/C11R_N9_STATEMENTS.json", "evidence/cost/C11R_COST.json")
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
    _table, best = POL.choose(model, boxes_at)
    derived = None if best is None else {"depth": best["depth"], "panels": best["panels"]}
    if derived != cfg["chosen"]:
        problems.append(f"re-derived configuration {derived} != frozen {cfg['chosen']}")
    return {"frozen": cfg["chosen"], "rederived": derived, "problems": problems}


def host_matches(cost_host: dict, now_host: dict) -> dict:
    """The cost model transfers only to the host it was measured on."""
    diff = {k: [cost_host.get(k), now_host.get(k)] for k in HOST_KEYS
            if cost_host.get(k) != now_host.get(k)}
    return {"match": not diff, "differences": diff}


def import_scan() -> dict:
    roots = set()
    closure = {}
    for m in sorted(C.HERE.glob("c11r_*.py")):
        closure.update(C.code_closure(m))
    for rel in closure:
        for n in ast.walk(ast.parse(C.read_code(rel))):
            if isinstance(n, ast.Import):
                roots |= {a.name.split(".")[0] for a in n.names}
            elif isinstance(n, ast.ImportFrom) and n.level == 0 and n.module:
                roots.add(n.module.split(".")[0])
    return {"modules": len(closure), "forbidden_graph_hits": sorted(roots & FORBIDDEN_GRAPH),
            "forbidden_backend_hits": sorted(roots & FORBIDDEN_BACKEND),
            "pass": not (roots & FORBIDDEN_GRAPH) and not (roots & FORBIDDEN_BACKEND)}


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
items = []


def item(iid, name, ok, detail):
    items.append({"id": iid, "name": name, "pass": bool(ok), "detail": detail})


def main() -> int:
    t0 = time.time()
    policy = C.load_allowlisted("config/C11R_POLICY.json")
    gate = C.load_allowlisted("config/N9R_GATE_C11R.json")
    stmt = C.load_allowlisted("evidence/table/C11R_N9_STATEMENTS.json")
    cost = C.load_allowlisted("evidence/cost/C11R_COST.json")
    val = C.load_allowlisted("evidence/validation/C11R_VALIDATION.json")
    mut = C.load_allowlisted("evidence/mutations/C11R_MUTATIONS.json")
    fw = C.load_allowlisted("evidence/firewall/C11R_FIREWALL.json")
    leak = C.load_allowlisted("evidence/leakcheck/C11R_LEAKCHECK.json")
    st = C.load_allowlisted("evidence/status/C11R_STATUS.json")
    eq = C.load_allowlisted("evidence/equivalence/C11R_EQUIVALENCE.json")

    rd = rederive_configuration(policy, cost)
    item("Q1", "the frozen policy is the sole configuration authority and re-derives exactly",
         not rd["problems"] and policy["statements_sha256"] == stmt["sha256"], rd)

    dirty = {rel: bool(C.git("status", "--porcelain", "--", f"{C.NS_REL}/{rel}"))
             for rel in FROZEN_ARTIFACTS}
    committed = {rel: bool(C.git("log", "--format=%H", "-1", "--", f"{C.NS_REL}/{rel}"))
                 for rel in FROZEN_ARTIFACTS}
    item("Q2", "policy, gate, statement table and cost artifact are committed and unmodified",
         all(committed.values()) and not any(dirty.values()),
         {"committed": committed, "dirty": dirty})

    tool = {m: C.sha256_file(C.HERE / m) == v
            for m, v in gate["post_seal_toolchain_sha256"].items()}
    item("Q3", "every post-seal toolchain module matches the hash the gate froze", all(tool.values()),
         {"match": tool})

    head_cert = CV.certifier_hashes("HEAD")
    tree_cert = {m: C.sha256_file(C.HERE / m) for m in CV.CERTIFIER_MODULES}
    reviewed = C.sha256_bytes(C.blob_at(REVIEWED_IDRIFT_COMMIT, f"{C.NS_REL}/code/c11r_idrift.py"))
    item("Q4", "certifier hashes agree at HEAD and in the tree; c11r_idrift is the reviewed version",
         head_cert == tree_cert and tree_cert["c11r_idrift.py"] == reviewed,
         {"head": head_cert, "tree": tree_cert, "reviewed_idrift": reviewed})

    sc = import_scan()
    item("Q5", "no forbidden import graph and no forbidden backend in the code closure", sc["pass"],
         sc)
    tc = C.toolchain_present()
    item("Q6", "the original certifier's backend is absent from this environment",
         not tc["numpy"] and not tc["flint"], {"importlib_find_spec": tc})
    item("Q7", "VALIDATION_CLASS = PASS", val["VALIDATION_CLASS"] == "PASS",
         {"failed": val["failed"]})
    item("Q8", "MUTATION_CLASS = PASS", mut["MUTATION_CLASS"] == "PASS",
         {"class": mut["MUTATION_CLASS"]})
    item("Q9", "FIREWALL_CLASS = PASS", fw["FIREWALL_CLASS"] == "PASS", {})
    item("Q10", "LEAK_CLASS = PASS", leak["LEAK_CLASS"] == "PASS", {})
    item("Q11", "STATUS_CLASS = CONSISTENT", st["STATUS_CLASS"] == "CONSISTENT", {})
    item("Q12", "the equivalence comparator's self-test passes",
         eq["EQUIV_CLASS"] == "READY" and eq["self_test"]["PASS"] is True, {})
    item("Q13", "scalar collapse re-exercised at the NON-TARGET scalar 5/2",
         scalar_collapse_nt()["pass"], scalar_collapse_nt())
    item("Q14", "K_e = Khat_e + atom re-exercised on NT", atom_decomposition_nt()["pass"],
         atom_decomposition_nt())

    eqp = C.NS / "evidence" / "equivalence" / "C11R_EQUIVALENCE.json"
    before = C.sha256_file(eqp)
    subprocess.run([sys.executable, "-B", str(C.HERE / "c11r_equiv.py")], capture_output=True,
                   cwd=str(C.NS))
    item("Q15", "a deterministic producer reproduces byte-identically",
         before == C.sha256_file(eqp), {})

    hm = host_matches(cost["host"], K.host_identity())
    item("Q16", "this host is the host the cost model was measured on", hm["match"], hm)

    auth_exists = (C.NS / "config" / "C11R_AUTHORIZATION.json").exists()
    runs_exists = (C.NS / "evidence" / "runs").exists()
    item("Q17", "guard prerequisites: gate DENY, no authorization yet, no runs artifact",
         gate["guard"] == "DENY" and not auth_exists and not runs_exists,
         {"gate_guard": gate["guard"], "authorization_exists": auth_exists,
          "runs_exists": runs_exists})

    du = shutil.disk_usage(str(C.REPO))
    item("Q18", "disk space for the run", du.free > 2 * 1024 ** 3,
         {"disk_free_gb": round(du.free / 1024 ** 3, 1)})

    failed = [i["id"] for i in items if not i["pass"]]
    out = {"schema": "C11R_QUALIFICATION/3",
           "runs_before": "any target execution",
           "produces_target_constants": False,
           "computes_on_open_cells": False,
           "items": items, "failed": failed,
           "QUALIFICATION_CLASS": "PASS" if not failed else "NO_TARGET_EXECUTION",
           "seconds": round(time.time() - t0, 1)}
    s = C.write_evidence(C.NS / "evidence" / "qualification" / "C11R_QUALIFICATION.json", out,
                         producer=__file__)
    for i in items:
        print(f"  {'PASS' if i['pass'] else 'FAIL'}  {i['id']:4s} {i['name'][:80]}")
    print(f"\nQUALIFICATION_CLASS = {out['QUALIFICATION_CLASS']}  failed={failed}")
    print(f"wrote evidence/qualification/C11R_QUALIFICATION.json sha256 {s[:16]}...")
    return 0 if not failed else 1


if __name__ == "__main__":
    if sys.argv[1:] == ["--self-test"]:
        r = self_test()
        for k, v in r["rows"].items():
            print(f"  {'PASS' if v['pass'] else 'FAIL'}  {k}")
        print(f"\nqualifier self-test ALL_PASS = {r['ALL_PASS']} (wrote nothing)")
        raise SystemExit(0 if r["ALL_PASS"] else 1)
    raise SystemExit(main())
