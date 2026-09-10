"""Pre-T2 governance verifier (generate | verify). Executes ONLY frozen code.

Produces and checks:
  * authorized-runtime reference records for T2 references A (Task1R F_0),
    B (Gate-2F hhat_1) and C (O9 packet, per shift), computed by the FROZEN
    certifiers under the bound runtime contract, with drift against the
    immutable historical records;
  * the executable P1 panel universe (Task1R span construction), with exact
    rational P1 checks for three constructions;
  * sha256 of every historical artifact this successor must never alter.
It changes no threshold, degree, precision, patch or candidate.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from fractions import Fraction as Fr
from pathlib import Path

HERE = Path(__file__).resolve().parent
NS = HERE.parent
ROOT = NS.parents[2]
CP = ROOT / "level4/closure_proofs"
for _p in (CP / "p5y_k1_sr_o9_executor_t1_successor/code",
           CP / "p5y_k1_task1r_budget_harness/code",
           CP / "p5y_k1_binding_campaign/task1",
           CP / "p5y_gate2f_sr_metric_b"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import sr_o9_candidates as T                                        # noqa: E402
import t1_reference as TR                                           # noqa: E402
import harness as H                                                 # noqa: E402
import sr_local as L                                                # noqa: E402
import sr_patch                                                     # noqa: E402
from flint import arb                                               # noqa: E402
from rebaseguard_certify.arb_backend import workprec                # noqa: E402

AUTHORIZED_RUNTIME = "d49f043755ef658a60e3c4017022ddecf0642a087a6e5bb0c1f2aefbe9721191"
T1_COMMIT = "ab8d197398dc1d11e7ef983c9d66347080356da1"
HISTORICAL = (
    "p5y_k1_task1r_budget_harness/results/task1r_F0_qualification.json",
    "p5y_k1_task1r_budget_harness/adjudication/TASK1R_ADJUDICATION.json",
    "p5y_k1_task1r_budget_harness/config/frozen_parameters.json",
    "p5y_k1_task1r_budget_harness/code/harness.py",
    "p5y_k1_binding_campaign/task1/task1_f0.py",
    "p5y_gate2f_sr_metric_b/results/sr_metric_b.json",
    "p5y_gate2f_sr_metric_b/sr_metric_b.py",
    "p5y_gate2e_sr_metric/sr_metric.py",
    "p5y_gate2d_sr_realcandidate/sr_realcandidate.py",
    "p5y_gate2b_sr_cover/GATE2B_RESULT.md",
    "p5y_gate2b_sr_cover/results/sr_cover.json",
    "p5y_gate2b_sr_cover/sr_cover.py",
    "p5y_k1_sr_backend_o9_successor/config/protocol.json",
    "p5y_k1_sr_backend_o9_successor/RESULT.md",
    "p5y_k1_sr_backend_cost_audit/config/frozen_audit.json",
    "p5y_k1_sr_cap_authorized_successor/config/protocol.json",
    "p5y_k1_sr_cap_authorized_successor/PROTOCOL.md",
    "p5y_k1_sr_cap_authorized_successor/evidence/cap_derivation.json",
    "p5y_k1_sr_cap_authorized_successor/evidence/packet.py",
    "p5y_k1_sr_cap_authorized_successor/evidence/worker.py",
    "p5y_k1_cover_ledger_successor/config/checkpoint.json",
    "p5y_k1_cover_ledger_successor/config/cost_model.json",
    "p5y_k1_sr_qualification/code/sr_patch.py",
    "p5y_k1_sr_production_authorized_successor/config/LAUNCH_AUTHORIZATION.json",
    "p5y_k1_sr_o9_executor_t1_successor/config/T1_MANIFEST.json",
)
REFS = NS / "config/AUTHORIZED_RUNTIME_REFERENCES.json"
PANELS = NS / "config/P1_PANEL_UNIVERSE.json"
INCIDENTAL_B = ("t_compose_median", "t_compose_min", "t_compose_max", "t_spread", "cell_cpu")


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def canon(o) -> bytes:
    return T.canonical(o)


def live_runtime_hash() -> str:
    sys.path.insert(0, str(CP / "p5y_k1_sr_production_authorized_successor/driver"))
    import integrated_sr_launcher as ISL
    import production_launcher as PL
    return ISL.gate_runtime_identity(PL.load_production_authorization(), "AWS")["runtime_contract_hash"]


def historical_hashes() -> dict:
    return {rel: sha(CP / rel) for rel in HISTORICAL}


def rel_drift(now, hist):
    if isinstance(now, bool) or not isinstance(now, (int, float)) or not isinstance(hist, (int, float)):
        return None
    return 0.0 if now == hist else (abs(now - hist) / abs(hist) if hist else float("inf"))


# ------------------------------------------------------------- reference A
def reference_A() -> dict:
    rec = json.loads((CP / HISTORICAL[0]).read_text())
    par = json.loads((CP / HISTORICAL[2]).read_text())["selection"]
    C_SR = rec["amplification"]["C_at_e"]
    mant, diag, _ = T.reference_F0()
    with workprec(256):
        g = H.geometry()
        p1 = H.p1_rule(g["H"], g["span"])
        den = arb(2) ** T.SCALE_BITS
        cand = [[arb(m) / den for m in row] for row in mant]
        out = H.certify(cand, par["D_selected"], par["Z_selected"], g, p1, C_SR,
                        {"dyadic_rounding_abs_sum": diag["dyadic_rounding_abs_sum"]})
    hist = rec["certificate"]
    drift = {k: rel_drift(out["components"][k], hist["components"][k]) for k in hist["components"]}
    drift["delta_F0"] = rel_drift(out["delta_F0"], hist["delta_F0"])
    return {
        "object": "F_0", "patch": list(H.PATCH), "e": f"{H.E_NUM}/{H.E_DEN}",
        "D": par["D_selected"], "Z": par["Z_selected"], "n_panels": out["n_panels"], "C_SR": C_SR,
        "candidate_mantissa_sha256": hashlib.sha256(canon(mant)).hexdigest(),
        "frozen_certifier": "p5y_k1_task1r_budget_harness/code/harness.py::certify (baseline run_panels)",
        "authorized_runtime_output": out,
        "authorized_runtime_output_sha256": hashlib.sha256(canon(out)).hexdigest(),
        "historical": {"delta_F0": hist["delta_F0"], "components": hist["components"],
                       "per_line_PASS": {k: v["PASS"] for k, v in hist["per_line"].items()}},
        "drift_rel": drift,
        "verdicts_equal_historical": ({k: v["PASS"] for k, v in out["per_line"].items()}
                                      == {k: v["PASS"] for k, v in hist["per_line"].items()}
                                      and out["all_lines_pass"] == hist["all_lines_pass"]),
    }


# ------------------------------------------------------------- reference B
def reference_B() -> dict:
    import sr_metric_b as G
    hist = json.loads((CP / HISTORICAL[5]).read_text())["cells"]["hhat_1"][0]
    g = G.geometry_and_Ed()
    cell = G.S2E.run_cell(256, g["cand1"], g["eps1"], g["geo"], g["e"], g["h_z"], "hhat_1")
    sci = {k: v for k, v in cell.items() if k not in INCIDENTAL_B}
    kernel_identity = {k: sci[k] == hist[k] for k in ("acc_enclosure", "acc_abs", "err_kernel_rem_width",
                                                      "err_interval_radius", "E_d", "bits")}
    wmax = Fr(hist["w_panel_max_ABS"])
    return {
        "object": "hhat_1", "bits": 256, "n_z": g["n_z"],
        "frozen_certifier": "p5y_gate2e_sr_metric/sr_metric.py::run_cell via p5y_gate2f_sr_metric_b",
        "authorized_runtime_output": sci,
        "authorized_runtime_output_sha256": hashlib.sha256(canon(sci)).hexdigest(),
        "kernel_identity_equal_historical": kernel_identity,
        "runtime_sensitive_fields": sorted(k for k in sci if k in hist and sci[k] != hist[k]),
        "historical": {k: hist[k] for k in ("w_panel_total_ABS", "eps_cand", "err_candidate_propagated",
                                            "ABS_PASS", "w_panel_max_ABS")},
        "drift_rel": {k: rel_drift(sci[k], hist[k]) for k in ("w_panel_total_ABS", "eps_cand",
                                                              "err_candidate_propagated")},
        "exact_abs_gate_now": Fr(sci["w_panel_total_ABS"]) <= wmax,
        "verdicts_equal_historical": sci["ABS_PASS"] == hist["ABS_PASS"],
    }


# ------------------------------------------------------------- reference C
def reference_C() -> dict:
    r = TR.reproduce()
    mant, _, _ = T.reference_F0()
    per_shift = {}
    with T.scientific_precision():
        P, packet_sha = TR.load_cap_packet()
        ctxs = P.build_contexts()
        AVs = [P.absvecs_of(c["sh"]) for c in ctxs]
        cands = {"real": T.to_arb_matrix(mant), "dense": P.dense_random_candidate(1)}
        for name, cand in cands.items():
            hs = {s: hashlib.sha256() for s in (0, 1, 2, 3)}
            for ci, c in enumerate(ctxs):
                coef, ex, ez = P.contract_O9(c["pd"], cand, P.build_Rbig(c["pd"]), AVs[ci])
                h = hs[c["shift"]]
                h.update(repr((c["patch"], c["panel"], c["shift"])).encode())
                for row in coef:
                    for v in row:
                        h.update(repr(TR.exact(v)).encode())
                h.update(repr(TR.exact(ex)).encode())
                h.update(repr(TR.exact(ez)).encode())
            per_shift[name] = {str(s): h.hexdigest() for s, h in hs.items()}
    return {"packet_py_sha256": packet_sha, "n_contexts": len(ctxs),
            "committed_hashes": {"real": r["recorded_real"], "dense": r["recorded_dense"]},
            "reproduced": {"real": r["t1_F0_packet_hash"], "dense": r["dense_control_packet_hash"]},
            "equal": r["t1_F0_matches_authorized_runtime_identity"] and r["dense_control_replica_faithful"],
            "per_shift_hashes": per_shift,
            "shift_semantics_note": ("committed packet contexts use CENTRED moment shifts (N[k+m]); "
                                     "these hashes certify the O9 contraction kernel. Raw z^s moment "
                                     "weights required by the 102-contract census are a T2 unit-tested "
                                     "exact identity, not a historical reference.")}


# ------------------------------------------------------------ panel universe
def _p1_exact(h: arb, Hh: arb, M: arb, fact: arb) -> tuple[bool, str, str]:
    thr, guard = Fr(1, 10 ** 9), Fr(1, 10 ** 6)
    E = M * ((h + Hh) ** (H.SOFTPLUS_DEGREE + 1)) / fact
    Eu = E.upper().fmpq()
    Eq = Fr(int(Eu.p), int(Eu.q))
    ok = Eq <= thr and (thr - Eq) / thr >= guard
    return ok, str(float(Eq)), str(float((thr - Eq) / thr))


def panel_universe() -> dict:
    rows = []
    fails = {"exec_span": 0, "census_on_span": 0, "census_on_core": 0, "census_repaired_on_core_count_diff": 0}
    worst = {"exec_span": 1.0, "census_on_span": 1.0, "census_on_core": 1.0}
    with workprec(256):
        _A, _b, c = L.sr_constants()
        M = L.softplus_derivative_bound_tight(H.SOFTPLUS_DEGREE + 1)
        fact = arb(math.factorial(H.SOFTPLUS_DEGREE + 1))
        for p in sr_patch.live_patches():
            geo = L.patch_geometry(p.i, p.j, grid=64)
            p_c = (geo["yp"][0] + geo["yp"][1]) / arb(2)
            m_c = (geo["ym"][0] + geo["ym"][1]) / arb(2)
            Hh = (geo["yp"][1] - geo["yp"][0]) / arb(2)
            span = (c - p_c) - (m_c - c)
            core = geo["core"][1] - geo["core"][0]
            p1 = H.p1_rule(Hh, span)
            n_exec = p1["n_panels"]
            h_z = arb(p1["H_max"]) - Hh
            n_core_rep = int(math.ceil(float((core / (arb(2) * h_z)).upper())))
            res = {}
            for name, length, n in (("exec_span", span, n_exec), ("census_on_span", span, p.n_z),
                                    ("census_on_core", core, p.n_z)):
                ok, _E, hr = _p1_exact(length / (arb(2) * arb(n)), Hh, M, fact)
                res[name] = ok
                fails[name] += (not ok)
                worst[name] = min(worst[name], float(hr))
            fails["census_repaired_on_core_count_diff"] += (n_core_rep != p.n_z)
            rows.append([p.i, p.j, n_exec, n_exec + 2, p.n_z, p.panels,
                         res["exec_span"], res["census_on_span"], res["census_on_core"]])
    table = {"columns": ["i", "j", "n_z_exec", "panels_exec", "n_z_census", "panels_census",
                         "P1_exec_span", "P1_census_count_on_span", "P1_census_count_on_core"],
             "rows": rows}
    return {
        "schema": "rebaseguard.p5y.k1.sr.o9.p1-panel-universe.v1",
        "rule": "task1r-span-p1-v1: n_z = ceil(span/(2 h_z)), h_z = H_max - H, H_max from the frozen asymmetric "
                "P1 rule target inside workprec(512); span = U_c - L_c at the patch centre; n_z contracted "
                "panels [L_c + 2hk, L_c + 2h(k+1)], h = span/(2 n_z); plus 2 analytic endpoint slivers (B_end)",
        "canonical_panel_id": "SRpanel:v2:task1r-span-p1:64:{i}:{j}:{k}/{n_z_exec}   (k = 0..n_z_exec-1)",
        "canonical_sliver_id": "SRsliver:v2:task1r-span-p1:64:{i}:{j}:{L|U}",
        "live_patches": len(rows),
        "contracted_panels_exec": sum(r[2] for r in rows),
        "sliver_units_exec": 2 * len(rows),
        "panel_units_exec_census_convention": sum(r[3] for r in rows),
        "contracted_panels_census": sum(r[4] for r in rows),
        "panel_units_census": sum(r[5] for r in rows),
        "patches_count_differs": sum(1 for r in rows if r[2] != r[4]),
        "P1_fail_counts": fails, "P1_worst_headroom_rel": worst,
        "reference_patch_17_11": next(r for r in rows if (r[0], r[1]) == (17, 11)),
        "table_sha256": hashlib.sha256(canon(table)).hexdigest(),
        "table": table,
    }


# ----------------------------------------------------------------- driver
def build() -> dict:
    return {"runtime_contract_hash": live_runtime_hash(),
            "historical_sha256": historical_hashes(),
            "A": reference_A(), "B": reference_B(), "C": reference_C()}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=("generate", "verify"))
    a = ap.parse_args(argv)
    T.check_threads()
    refs, panels = build(), panel_universe()
    if refs["runtime_contract_hash"] != AUTHORIZED_RUNTIME:
        print("REFUSE: live runtime is not the authorized contract"); return 2
    if a.mode == "generate":
        REFS.write_bytes(canon({"schema": "rebaseguard.p5y.k1.sr.o9.authorized-runtime-references.v1",
                                "authorized_runtime_contract": AUTHORIZED_RUNTIME, "t1_commit": T1_COMMIT,
                                **refs}))
        PANELS.write_bytes(canon(panels))
    committed_refs = json.loads(REFS.read_text())
    committed_panels = json.loads(PANELS.read_text())
    checks = {
        "runtime_is_authorized": refs["runtime_contract_hash"] == AUTHORIZED_RUNTIME,
        "historical_artifacts_unchanged": refs["historical_sha256"] == committed_refs["historical_sha256"],
        "A_output_identical_to_committed": refs["A"]["authorized_runtime_output_sha256"]
                                           == committed_refs["A"]["authorized_runtime_output_sha256"],
        "A_candidate_identical": refs["A"]["candidate_mantissa_sha256"]
                                 == committed_refs["A"]["candidate_mantissa_sha256"],
        "A_verdicts_equal_historical": refs["A"]["verdicts_equal_historical"],
        "B_output_identical_to_committed": refs["B"]["authorized_runtime_output_sha256"]
                                           == committed_refs["B"]["authorized_runtime_output_sha256"],
        "B_kernel_identity_equal_historical": all(refs["B"]["kernel_identity_equal_historical"].values()),
        "B_verdict_equal_historical": refs["B"]["verdicts_equal_historical"],
        "B_exact_abs_gate": refs["B"]["exact_abs_gate_now"],
        "C_committed_packet_hashes_reproduced": refs["C"]["equal"],
        "C_per_shift_identical_to_committed": refs["C"]["per_shift_hashes"]
                                              == committed_refs["C"]["per_shift_hashes"],
        "panel_universe_identical_to_committed": panels["table_sha256"] == committed_panels["table_sha256"],
        "exec_panel_universe_P1_all_pass": panels["P1_fail_counts"]["exec_span"] == 0,
    }
    out = {"checks": checks, "all_pass": all(checks.values()),
           "A_drift_rel": refs["A"]["drift_rel"], "B_drift_rel": refs["B"]["drift_rel"],
           "B_runtime_sensitive_fields": refs["B"]["runtime_sensitive_fields"],
           "panels": {k: v for k, v in panels.items() if k != "table"}}
    (NS / "evidence/pre_t2_verification.json").write_bytes(canon(out))
    print(json.dumps(out, indent=1, default=str))
    return 0 if out["all_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
