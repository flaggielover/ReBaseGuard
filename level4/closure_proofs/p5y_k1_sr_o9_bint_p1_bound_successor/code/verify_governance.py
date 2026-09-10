"""Additive governance successor: P1 derivative-bound reuse for the softplus Lagrange factor.

generate : bind doctrine, run every check, write config/P1_BOUND_REUSE_AUTHORIZATION.json
verify   : recompute every check and hash, require equality with the written record
Governance/evidence only.  Declares no T2 closure.
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys
from fractions import Fraction as Fr
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
CP = NS.parent
REPO = CP.parents[1]
AUTH = NS / "config/P1_BOUND_REUSE_AUTHORIZATION.json"
TOKEN = "P1_DERIVATIVE_BOUND_REUSE_FOR_SOFTPLUS_LAGRANGE_FACTOR"
VENV = "/home/ubuntu/work/ReBaseGuard/level4/.venv/bin/python"
PRED_COMMITS = {"endpoint_strip_successor": "b48973d6", "bint_representation_audit": "fa92afb"}
PREDECESSOR_DIRS = ["p5y_k1_sr_o9_executor_t1_successor", "p5y_k1_sr_o9_pre_t2_governance_successor",
                    "p5y_k1_sr_o9_pre_t2_a5_amendment", "p5y_k1_sr_o9_t2_per_patch_successor",
                    "p5y_k1_sr_o9_endpoint_strip_successor", "p5y_k1_sr_o9_bint_representation_successor",
                    "p5y_k1_task1r_budget_harness", "p5y_gate2f_sr_metric_b", "p5y_k1_binding_campaign",
                    "p5y_k1_cover_ledger_successor", "p5y_k1_sr_qualification", "p5y_k1_sr_backend_cost_audit",
                    "p5x_global_nonlinear_dynamics/compute_optimization_r3_sr_symbolic"]
# path : (sha256 prefix recorded in the Phase-1 read, [verbatim fragments that must be present])
DOCTRINE = {
    "p5x_global_nonlinear_dynamics/compute_optimization_r3_sr_symbolic/PROOF.md": ("14d6f028", [
        "is a ball containing `sp^{(d+1)}(xi)/(d+1)!` for",
        "E_d := |A_{d+1}| H^{d+1}",
        "bounded by an absolute constant **independent of `u`**",
        "Both `a_k` and `A_{d+1}` are obtained by evaluating the power"]),
    "p5x_global_nonlinear_dynamics/compute_optimization_r3_sr_symbolic/sr_local.py": ("8de4d345", [
        "def softplus_derivative_bound_tight(order: int) -> arb:",
        "the convex-hull property gives",
        "L-R3.1 with the ABSOLUTE derivative bound",
        "Absolute derivative bound for softplus (PROOF.md L-R3.1 remark)",
        "a_next = coeffs[degree + 1]                      # contains sp^{(d+1)}(xi)/(d+1)!"]),
    "p5y_k1_task1r_budget_harness/code/harness.py": ("ea1f3e04", [
        "a, _E, a_next = L.softplus_local_enclosure(centre, rho, SOFTPLUS_DEGREE)",
        "M = L.softplus_derivative_bound_tight(SOFTPLUS_DEGREE + 1)",
        "E_d = M * ((h + H) ** (SOFTPLUS_DEGREE + 1)) / arb(math.factorial(SOFTPLUS_DEGREE + 1))"]),
    "p5y_k1_task1r_budget_harness/CHECKPOINT_T1R.md": ("0fc9296a", [
        "representation family or verdict semantic changes",
        "| `B_int` | 1 | 0.002 | Arb interval radius |"]),
    "p5y_k1_task1r_budget_harness/adjudication/TASK1R_ADJUDICATION.json": ("613f81a6", [
        "\"no_degree_adaptation\": true", "\"P1_workprec\": true"]),
    "p5y_k1_cover_ledger_successor/ERROR_ALGEBRA.md": ("4f32df02", [
        "An interval may be tighter only if a proved enclosure of the same expression",
        "No source uncertainty may silently become zero.",
        "No degree, precision, scope, P1, complexity,"]),
    "p5y_k1_binding_campaign/config/p1_rule.json": ("0d9e80a4", ["\"P1_CHECK_THRESHOLD\": 1e-09"]),
    "p5y_k1_sr_qualification/config/excluded_routes.json": ("80e16c58", [
        "\"id\": \"sr_local_panel_primitives\"", "\"correct_route\": \"Import, do not re-derive.\""]),
    "p5y_k1_sr_qualification/SR_DERIVATION.md": ("1d4f5f96", [
        "softplus enclosure by `softplus_local_enclosure` at degree 8"]),
    "p5y_gate2f_sr_metric_b/GATE2F_PREREGISTRATION.md": ("29d0d826", ["**NON-BINDING.**"]),
    "p5y_gate2f_sr_metric_b/GATE2F_RESULT.md": ("5c4799e1", ["| **P1 thresholds** |"]),
    "p5y_gate2f_sr_metric_b/GATE2F_SOURCE_MANIFEST.json": ("bcef56d2", []),
    "p5y_k1_sr_backend_cost_audit/adjudication/AUDIT_ADJUDICATION.json": ("d7edf59f", [
        "bit-equality was never the frozen criterion"]),
    "p5y_k1_sr_backend_cost_audit/code/opt_backend.py": ("825ed958", [
        "V = H.softplus_tm2(p_c + z_c - half, ctxt, +1)"]),
    "p5y_k1_sr_o9_pre_t2_governance_successor/config/PRE_T2_GOVERNANCE.json": ("ce02ad68", [
        "\"A5\": \"T2 O9 mode:"]),
    "p5y_k1_sr_o9_pre_t2_a5_amendment/config/A5_AMENDMENT.json": ("ebf730f7", []),
    "p5y_k1_sr_o9_endpoint_strip_successor/config/ENDPOINT_STRIP_MANIFEST.json": ("faecda8c", []),
}
MANIFEST_PINS = {"p5y_k1_binding_campaign/manifests/protected_inputs.json": [
                     "level4/closure_proofs/p5x_global_nonlinear_dynamics/compute_optimization_r3_sr_symbolic/sr_local.py"],
                 "p5y_k1_sr_cap_authorized_successor/config/governed_inputs_manifest.json": [
                     "level4/closure_proofs/p5x_global_nonlinear_dynamics/compute_optimization_r3_sr_symbolic/sr_local.py",
                     "level4/closure_proofs/p5y_k1_task1r_budget_harness/code/harness.py",
                     "level4/closure_proofs/p5y_k1_sr_backend_cost_audit/code/opt_backend.py"]}
SUCCESSOR_CODE = ["code/sr_o9_bint_p1.py", "code/a9_p1_proof.py"]
ENV = {"HOME": "/home/ubuntu", "PATH": "/usr/bin:/bin", "LANG": "C.UTF-8", **{k: "1" for k in (
    "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "BLIS_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS")}}
PYPATH = ":".join(str(CP / p) for p in ("p5y_k1_sr_o9_bint_p1_bound_successor/code", "p5y_k1_sr_o9_endpoint_strip_successor/code",
                                       "p5y_k1_sr_o9_t2_per_patch_successor/code", "p5y_k1_sr_o9_executor_t1_successor/code"))

ADJUDICATION = {
    "answer": "A",
    "answer_text": "Equivalent rigorous enclosure repair permitted by the frozen doctrine; not a change to a frozen scientific setting.",
    "Q1_requirement_is_only_a_valid_enclosure": {"answer": "YES",
        "basis": "PROOF.md L-R3.1 Claim: the containment holds whenever A_{d+1} 'is a ball containing sp^{(d+1)}(xi)/(d+1)! for every xi in U'. The claim is construction-independent."},
    "Q2_interval_series_declared_binding": {"answer": "NO",
        "basis": "The L-R3.1 Proof paragraph, the status table ('coefficients by interval arb_series'), SR_DERIVATION section 9 and the harness docstring DESCRIBE the construction used to discharge the hypothesis; none states it as a requirement. The same frozen file sr_local.py (hash-pinned by protected_inputs and governed_inputs_manifest) ships softplus_enclosure_absolute 'L-R3.1 with the ABSOLUTE derivative bound', and PROOF.md's L-R3.1 remark states every derivative is bounded by an absolute constant independent of u. Task1R 'representation family' refers to the candidate representation (exact-dyadic Chebyshev), and no frozen invariant in TASK1R_ADJUDICATION, the Task1R checkpoint, GATE2F (NON-BINDING; its only semantic change was the P1 threshold pair) or excluded_routes names the Lagrange-ball construction."},
    "Q3_M_over_9fact_frozen_proved_enclosure_same_quantity_same_domain": {"answer": "YES (domain is all of R, a superset of every U)",
        "basis": "sr_local.softplus_derivative_bound_tight(9) bounds |sp^(9)(u)| = |sigma^(8)(u)| for ALL real u (Bernstein convex hull on sigma in (0,1)); it is the M the frozen P1 rule uses to certify E_d = M rho^9/9! <= 1e-9 for the same ninth-order Lagrange remainder. evidence/A9_P1_PROOF.json re-proves it exactly."},
    "Q4_preserves_every_dependency_and_uncertainty_source": {"answer": "YES",
        "basis": "Both constructions enter the Lagrange factor as ONE constant ball multiplying (u-c)^9, i.e. (x + sign*z)^9 expanded binomially by the unchanged harness.softplus_tm2; neither tracks any correlation of the unknown xi with x or z, so no dependency exists to lose. a_0..a_8, centre, rho, the binomial expansion, all downstream Taylor-model algebra, moments, candidates, strips and rounding are the unchanged code. The new ball has midpoint 0 and radius >= M_exact/9! > 0: the remainder uncertainty is carried in full, not set to zero (ERROR_ALGEBRA section 1)."},
    "Q5_moves_uncertainty_between_frozen_budget_lines": {"answer": "NO",
        "basis": "The ball occupies the same Taylor-model coefficient slots as before; its radius reaches the certificate through the same unchanged channel (int = Arb interval radius, B_int). No line mapping (PC.LINES), allowance or nested budget is touched; E returned by softplus_local_enclosure is discarded by softplus_tm2 before and after."},
    "Q6_alters_frozen_threshold_or_degree": {"answer": "NO",
        "basis": "SOFTPLUS_DEGREE = 8 (Lagrange order 9), D = 11, Z = 20, 256 bits, candidate degree 16, P1 rule target/check/guard/workprec, panel geometry (n_z from the unchanged P1 rule), candidates, contracts, the 1/250 endpoint gate, B_int allowance and B_cover target are unchanged and asserted at runtime. ERROR_ALGEBRA section 7 forbids degree/precision/scope/P1/complexity/CPU/cell-splitting relaxation: none occurs; the P1 rule is reused, not relaxed."},
    "not_inferred_from_numerical_success": "The adjudication rests on the L-R3.1 hypothesis, ERROR_ALGEBRA section 1 and the exact proof; the fa92afb diagnostic numbers are reported only as prior evidence.",
}


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def git(*a):
    return subprocess.run(["git", "-C", str(REPO), *a], capture_output=True, text=True)


def compute():
    checks, rec = {}, {}
    doc = {}
    for rel, (pref, frags) in DOCTRINE.items():
        p = CP / rel
        text = p.read_text()
        h = sha(p)
        doc[rel] = {"sha256": h, "fragments": frags, "fragments_present": all(f in text for f in frags),
                    "prefix_matches_phase1_read": h.startswith(pref),
                    "unchanged_since_fa92afb": git("diff", "--quiet", "fa92afb", "--", f"level4/closure_proofs/{rel}").returncode == 0}
    rec["doctrine"] = doc
    checks["doctrine_hashes_match_phase1"] = all(v["prefix_matches_phase1_read"] for v in doc.values())
    checks["doctrine_fragments_present"] = all(v["fragments_present"] for v in doc.values())
    checks["doctrine_unchanged_since_fa92afb"] = all(v["unchanged_since_fa92afb"] for v in doc.values())
    pins = {}
    for man, keys in MANIFEST_PINS.items():
        m = json.loads((CP / man).read_text())
        flat = {}
        def walk(o):
            if isinstance(o, dict):
                for k, v in o.items():
                    if isinstance(v, str) and k.startswith("level4/"):
                        flat[k] = v
                    walk(v)
        walk(m)
        pins[man] = {k: {"pinned": flat.get(k), "current": sha(REPO / k), "equal": flat.get(k) == sha(REPO / k)} for k in keys}
    rec["manifest_pins"] = pins
    checks["frozen_sources_equal_governed_manifest_pins"] = all(v["equal"] for m in pins.values() for v in m.values())
    # predecessors
    anc = {k: git("merge-base", "--is-ancestor", c, "HEAD").returncode == 0 for k, c in PRED_COMMITS.items()}
    unchanged = {d: git("diff", "--quiet", "fa92afb", "--", f"level4/closure_proofs/{d}").returncode == 0
                 and not git("status", "--porcelain", "--", f"level4/closure_proofs/{d}").stdout.strip() for d in PREDECESSOR_DIRS}
    rec["predecessors"] = {"commits": PRED_COMMITS, "ancestors_of_HEAD": anc, "dirs_unchanged_vs_fa92afb_and_clean": unchanged}
    checks["predecessor_commits_are_ancestors"] = all(anc.values())
    checks["predecessor_dirs_unchanged"] = all(unchanged.values())
    # proof
    pr = subprocess.run([VENV, str(NS / "code/a9_p1_proof.py")], capture_output=True, text=True, cwd=NS / "code",
                        env={**ENV, "PYTHONPATH": PYPATH})
    proof = json.loads(pr.stdout)
    stored = json.loads((NS / "evidence/A9_P1_PROOF.json").read_text())
    rec["proof"] = {"file": "evidence/A9_P1_PROOF.json", "sha256": sha(NS / "evidence/A9_P1_PROOF.json"),
                    "rc": pr.returncode, "checks": proof["checks"]}
    checks["A9_P1_proof_all_pass"] = pr.returncode == 0 and proof["all_pass"]
    checks["A9_P1_proof_reproduces_stored"] = proof == stored
    # excluded routes
    ex = json.loads((CP / "p5y_k1_sr_qualification/config/excluded_routes.json").read_text())
    code = "".join((NS / f).read_text() for f in SUCCESSOR_CODE)
    banned = [s for r in ex["routes"] if r["class"] in ("GOVERNANCE_PROHIBITED", "IMPLEMENTATION_DEFECT")
              for s in r["banned_symbols"] if s in code]
    rec["excluded_routes"] = {"banned_symbols_found": banned, "route_ids": [r["id"] for r in ex["routes"]]}
    checks["no_excluded_route_used"] = not banned
    # frozen settings, asserted at runtime
    probe = ("import json,sr_o9_candidates as T,sr_o9_patch_certifier as PC,sr_o9_endpoint_strips as ES;H=PC.H;"
             "print(json.dumps({'D':T.FROZEN_D,'Z':T.FROZEN_Z,'bits':T.FROZEN_BITS,'cand_degree':T.CAND_DEGREE,"
             "'softplus_degree':H.SOFTPLUS_DEGREE,'prod_bits':H.PROD_BITS,'eps_P1':H.EPS_P1,"
             "'P1_check':H.P1_CHECK_THRESHOLD,'P1_workprec':H.P1_RULE_WORKPREC,'P1_guard':H.P1_HEADROOM_GUARD,"
             "'lines':PC.LINES,'nested':{k:str(v) for k,v in T.spec.NESTED_CANDIDATE.items()},'M_W':ES.M_W}))")
    fs = json.loads(subprocess.run([VENV, "-c", probe], capture_output=True, text=True, cwd=NS / "code",
                                   env={**ENV, "PYTHONPATH": PYPATH}).stdout)
    rec["frozen_settings_runtime"] = fs
    nested_ok = {k: Fr(fs["nested"][k]) == Fr(v) for k, v in
                 {"B_eq": "9/500", "B_trunc": "3/500", "B_tail": "3/500", "B_end": "1/250", "B_int": "1/500", "B_round": "1/500"}.items()}
    checks["frozen_settings_unchanged"] = (fs["D"] == 11 and fs["Z"] == 20 and fs["bits"] == 256 and fs["cand_degree"] == 16
                                           and fs["softplus_degree"] == 8 and fs["prod_bits"] == 256 and fs["eps_P1"] == 0.001
                                           and fs["P1_check"] == 1e-9 and fs["P1_workprec"] == 512 and fs["P1_guard"] == 1e-6
                                           and all(nested_ok.values()))
    # predecessor verifiers still pass on the preserved frozen-ball mode (no override installed)
    pv = {}
    for name, cmd in (("verify_pre_t2", [VENV, str(CP / "p5y_k1_sr_o9_pre_t2_governance_successor/code/verify_pre_t2.py"), "verify"]),
                      ("verify_a5", [VENV, str(CP / "p5y_k1_sr_o9_pre_t2_a5_amendment/code/verify_a5.py")])):
        r = subprocess.run(cmd, capture_output=True, text=True, cwd=REPO, env=ENV, timeout=3600)
        pv[name] = {"rc": r.returncode, "stdout_tail": r.stdout[-600:], "stderr_tail": r.stderr[-300:]}
    rec["predecessor_verifiers_frozen_ball_mode"] = pv
    checks["predecessor_verifiers_pass"] = all(v["rc"] == 0 for v in pv.values())
    rec["successor_code"] = {f: sha(NS / f) for f in SUCCESSOR_CODE}
    return checks, rec


def build():
    checks, rec = compute()
    return {
        "schema": "rebaseguard.p5y.k1.sr.o9.bint_p1_bound_reuse.v1",
        "binding": True, "additive": True,
        "authorizes": TOKEN,
        "scope": ("SR O9 per-patch certifier (endpoint-strip successor b48973d6 architecture): the SOURCE of the L-R3.1 "
                  "Lagrange-factor ball A_9 passed by sr_local.softplus_local_enclosure to harness.softplus_tm2, for every "
                  "core-panel and strip PanelShared construction. Nothing else."),
        "replacement": {"historical": "A_9 = coefficient 9 of arb_series(log(1+exp(x))) at x = centre + [-rho, rho] (interval series)",
                        "successor": "A9_P1 = arb(0, upper(M/9!)), M = sr_local.softplus_derivative_bound_tight(9) (frozen P1 rule's M)",
                        "E_d": "|A9_P1| rho^9 (L-R3.1); discarded by softplus_tm2 as before",
                        "implementation": "code/sr_o9_bint_p1.py::softplus_local_enclosure_p1, scoped context p1_lagrange_factor()"},
        "unchanged": ["theorem target", "D = 11", "Z = 20", "256 bits", "SR candidate degree 16", "softplus degree 8 / Lagrange order 9",
                      "Taylor polynomial a_0..a_8 (frozen function's own output)", "expansion centre", "panel radius rho = H + h",
                      "panel geometry (task1r-span-p1-v1, n_z from the unchanged P1 rule)", "endpoint-strip successor",
                      "candidates / 102 contracts", "B_int allowance and every nested line", "1/250 endpoint gate", "B_cover target",
                      "P1 rule and check", "harness.py, opt_backend.py, T2 certifier, endpoint strips (unchanged files)"],
        "supersession": ("The historical interval-series construction remains immutable historical evidence (Task1R, Gate-2E/2F, "
                         "T2 29ee382, endpoint strips b48973d6, B_int audit fa92afb) and is superseded for future T2 execution only."),
        "reference_conformance_scope": ("PRE_T2_GOVERNANCE A1-A6/B/C and the A5 amendment stay in force, unchanged, as conformance of the "
                                        "preserved frozen-ball mode (re-verified here by the untouched predecessor verifiers). They are "
                                        "not reinterpreted: the successor mode is certified by L-R3.1 with A9_P1 (evidence/A9_P1_PROOF.json) "
                                        "and differs from that mode only in A_9."),
        "T2_CLOSED": False,
        "adjudication": ADJUDICATION,
        "checks": checks, "all_pass": all(checks.values()),
        "classification": "BINT_P1_BOUND_REUSE_AUTHORIZED" if all(checks.values()) else "BINT_P1_BOUND_REUSE_NOT_AUTHORIZED",
        **rec,
    }


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=("generate", "verify"))
    a = ap.parse_args(argv)
    new = build()
    if a.mode == "generate":
        AUTH.write_text(json.dumps(new, indent=1, sort_keys=True) + "\n")
        ok = new["all_pass"]
    else:
        old = json.loads(AUTH.read_text())
        strip = lambda d: {k: v for k, v in d.items() if k != "predecessor_verifiers_frozen_ball_mode"}   # noqa: E731
        ok = new["all_pass"] and strip(new) == strip(old) and old["authorizes"] == TOKEN and old["T2_CLOSED"] is False
        (NS / "evidence/governance_verification.json").write_text(json.dumps(
            {"auth_sha256": sha(AUTH), "record_equal": strip(new) == strip(old), "checks": new["checks"], "PASS": ok}, indent=1, sort_keys=True) + "\n")
    print(json.dumps({"mode": a.mode, "checks": new["checks"], "PASS": ok, "classification": new["classification"]}, indent=1))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
