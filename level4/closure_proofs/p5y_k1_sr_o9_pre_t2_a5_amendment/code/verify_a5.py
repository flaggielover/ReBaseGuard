"""A5 amendment verifier. Executes ONLY frozen code; changes no science.

Replaces the pre-T2 governance criterion A5 (a specification error: it demanded
bit-identity of O9 with the Task1R reference harness and delta_O9 >= delta_baseline,
contradicting the already-adjudicated optimized-backend acceptance doctrine) by the
frozen Section-10-compatible criterion A5.1-A5.5.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from fractions import Fraction as Fr
from pathlib import Path

HERE = Path(__file__).resolve().parent
NS = HERE.parent
ROOT = NS.parents[2]
CP = ROOT / "level4/closure_proofs"
GOV = CP / "p5y_k1_sr_o9_pre_t2_governance_successor"
ADJ = CP / "p5y_k1_sr_backend_cost_audit/adjudication/AUDIT_ADJUDICATION.json"
CAP_PROTOCOL = CP / "p5y_k1_sr_cap_authorized_successor/PROTOCOL.md"
CAP_ERRCH = CP / "p5y_k1_sr_cap_authorized_successor/evidence/error_channel_exact.json"
for _p in (CP / "p5y_k1_sr_o9_executor_t1_successor/code", CP / "p5y_k1_task1r_budget_harness/code",
           CP / "p5y_k1_sr_backend_cost_audit/code"):
    sys.path.insert(0, str(_p))
import sr_o9_candidates as T                                        # noqa: E402
import t1_reference as TR                                           # noqa: E402
import harness as H                                                 # noqa: E402
import opt_backend as OB                                            # noqa: E402
from flint import arb                                               # noqa: E402

OLD_A5 = ("T2 O9 mode: Taylor coefficients exact()-identical to baseline mode per panel; ex, ez >= "
          "baseline (exact arb upper); delta_O9 >= delta_baseline; every gate compared in exact rationals")
NEW_A5 = {
    "A5.1": "(a) O9 per-panel contraction output (every coefficient, ex, ez) bit-identical to the committed O9 "
            "reference for the same frozen inputs (packet contract_O9; committed packet hashes c72f65b3/c0fc8609 and "
            "the pre-T2 per-shift hashes, which include exact(ex) and exact(ez)); (b) against the accepted optimized "
            "backend opt_backend.contract: Taylor coefficients bit-identical, and error channels related EXACTLY as "
            "frozen-disclosed (cap PROTOCOL 'O9 error-channel observation', evidence/error_channel_exact.json, "
            "governance C4): O9 <= opt_backend with relative shortfall < 2^-200 (a rounding-order artefact, not a "
            "loosening). Error-channel bit-identity with opt_backend is NOT required; it is frozen-documented false.",
    "A5.2": "every O9 certified coefficient enclosure overlaps or contains the corresponding Task1R reference-harness "
            "enclosure (frozen cost-audit Section-10 criterion); bit-equality with the harness is NOT required",
    "A5.3": "the complete O9-mode certificate is independently recomputed and every frozen scientific line passes "
            "under exact/outward-safe comparison",
    "A5.4": "NO requirement delta_O9 >= delta_baseline: both are independently rigorous enclosures and the optimized "
            "backend is adjudicated as not uniformly conservative relative to the harness",
    "A5.5": "baseline Task1R mode remains the authoritative A4 reproduction path; O9 mode is the authoritative T2 "
            "evidence-execution path; historical Task1R and prior governance records remain immutable",
}


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def walk(node, pre=""):
    if isinstance(node, dict):
        for k, v in node.items():
            yield from walk(v, f"{pre}.{k}" if pre else k)
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from walk(v, f"{pre}[{i}]")
    else:
        yield pre, node


def doctrine() -> dict:
    d = json.loads(ADJ.read_text())
    leaves = list(walk(d))
    find = lambda pred: [(p, v) for p, v in leaves if pred(p, v)]          # noqa: E731
    bit_text = find(lambda p, v: isinstance(v, str) and "bit-equality was never the frozen criterion" in v)
    sec10 = find(lambda p, v: isinstance(v, str) and "Section 10 requires enclosure overlap / containment" in v)
    overlap = find(lambda p, v: p.endswith("enclosures_overlap") and v is True)
    uniform = find(lambda p, v: p.endswith("uniformly_conservative") and v is False)
    return {"file": str(ADJ.relative_to(CP)), "sha256": sha(ADJ),
            "bit_equality_not_frozen_criterion": [p for p, _ in bit_text],
            "section10_overlap_containment": [p for p, _ in sec10],
            "enclosures_overlap_true": [p for p, _ in overlap],
            "uniformly_conservative_false": [p for p, _ in uniform],
            "quote": bit_text[0][1][:400] if bit_text else None,
            "o9_error_channel_disclosure": {
                "cap_protocol": str(CAP_PROTOCOL.relative_to(CP)), "cap_protocol_sha256": sha(CAP_PROTOCOL),
                "cap_protocol_section_present": "Disclosed before results: the O9 error-channel observation" in CAP_PROTOCOL.read_text(),
                "error_channel_exact": str(CAP_ERRCH.relative_to(CP)), "error_channel_exact_sha256": sha(CAP_ERRCH),
                "conclusion": json.loads(CAP_ERRCH.read_text())["conclusion"],
                "disclosed_sample_max_rel": 1.25e-75},
            "present": bool(bit_text and sec10 and overlap and uniform)
                       and "Disclosed before results: the O9 error-channel observation" in CAP_PROTOCOL.read_text()}


def old_verifier() -> dict:
    env = {"HOME": "/home/ubuntu", "PATH": "/usr/bin:/bin", "LANG": "C.UTF-8",
           **{v: "1" for v in T.THREAD_VARS}}
    p = subprocess.run([sys.executable, str(GOV / "code/verify_pre_t2.py"), "verify"],
                       env=env, capture_output=True, text=True)
    out = json.loads(p.stdout)
    dirty = subprocess.run(["git", "-C", str(ROOT), "status", "--porcelain",
                            str(GOV.relative_to(ROOT))], capture_output=True, text=True).stdout.strip()
    return {"returncode": p.returncode, "all_pass": out["all_pass"], "checks": out["checks"],
            "governance_namespace_unchanged": dirty == ""}


def exact_le(v: float, allowance: Fr) -> bool:
    """Outward-safe: float(arb.abs_upper()) is within 2^-53 relative of the certified upper."""
    return Fr(v) * (1 + Fr(1, 2 ** 52)) <= allowance


def measure() -> dict:
    rec = json.loads((CP / "p5y_k1_task1r_budget_harness/results/task1r_F0_qualification.json").read_text())
    par = json.loads((CP / "p5y_k1_task1r_budget_harness/config/frozen_parameters.json").read_text())["selection"]
    D, Z = par["D_selected"], par["Z_selected"]
    C_SR = rec["amplification"]["C_at_e"]
    mant, diag, _ = T.reference_F0()
    ex_ = lambda x: (x.mid().man_exp(), x.rad().man_exp())                # noqa: E731
    with T.scientific_precision():
        g = H.geometry()
        p1 = H.p1_rule(g["H"], g["span"])
        n_z = p1["n_panels"]
        cand = [[arb(m) / arb(2) ** T.SCALE_BITS for m in r] for r in mant]
        P, _ = TR.load_cap_packet()
        n = cmp_ov = bit_opt = 0
        exz_ge = []
        per_panel = []
        shortfalls = []

        def dy(v):
            m_, e_ = v.man_exp()
            return Fr(int(m_)) * Fr(2) ** int(e_)
        for kp in range(n_z):
            cb, exb, ezb, h, ctxt = H.run_panels(cand, D, Z, g, p1, only_panel=kp)
            co, exo, ezo, _, _ = OB.run_panels_opt(cand, D, Z, g, p1, only_panel=kp)
            z_lo = g["L_c"] + arb(2) * h * arb(kp); z_hi = z_lo + arb(2) * h; z_c = (z_lo + z_hi) / arb(2)
            sh = OB.PanelShared(g["p_c"], g["m_c"], z_c, g["b"], ctxt)
            pd = OB.PanelDrift(sh, H.panel_moments(z_lo, z_hi, z_c, g["e"], 2 * Z + 1, h))
            c9, ex9, ez9 = P.contract_O9(pd, cand, P.build_Rbig(pd), P.absvecs_of(sh))
            for a in range(D + 1):
                for b in range(D + 1):
                    n += 1
                    x, y = cb[a][b], c9[a][b]
                    cmp_ov += not (x.lower() > y.upper() or y.lower() > x.upper())
                    bit_opt += ex_(co[a][b]) == ex_(y)
            per_panel.append(ex_(exo) == ex_(ex9) and ex_(ezo) == ex_(ez9))
            for o_, n_ in ((exo, ex9), (ezo, ez9)):
                ov, nv = dy(o_.abs_upper()), dy(n_.abs_upper())
                shortfalls.append((ov - nv) / ov if ov else Fr(0))
            exz_ge.append(bool(ex9.upper() >= exb.upper() and ez9.upper() >= ezb.upper()))
        frozen_rp = H.run_panels

        def o9_run_panels(cand_, D_, Z_, g_, p1_, *, majorant=False, only_panel=None):
            assert not majorant and only_panel is None
            nz = p1_["n_panels"]; h_ = g_["span"] / (arb(2) * arb(nz))
            ctxt_ = (g_["H"], h_, D_, Z_, [g_["H"] ** a for a in range(2 * D_ + 2)],
                     [h_ ** k for k in range(2 * Z_ + 2)])
            coef = [[arb(0)] * (D_ + 1) for _ in range(D_ + 1)]; ex_t = ez_t = arb(0)
            for kp in range(nz):
                zl = g_["L_c"] + arb(2) * h_ * arb(kp); zh = zl + arb(2) * h_; zc = (zl + zh) / arb(2)
                sh_ = OB.PanelShared(g_["p_c"], g_["m_c"], zc, g_["b"], ctxt_)
                pd_ = OB.PanelDrift(sh_, H.panel_moments(zl, zh, zc, g_["e"], 2 * Z_ + 1, h_))
                c_, e1, e2 = P.contract_O9(pd_, cand_, P.build_Rbig(pd_), P.absvecs_of(sh_))
                for a in range(D_ + 1):
                    for b in range(D_ + 1):
                        coef[a][b] += c_[a][b]
                ex_t += e1; ez_t += e2
            return coef, ex_t, ez_t, h_, ctxt_
        ci = {"dyadic_rounding_abs_sum": diag["dyadic_rounding_abs_sum"]}
        base = H.certify(cand, D, Z, g, p1, C_SR, ci)
        H.run_panels = o9_run_panels
        try:
            o9 = H.certify(cand, D, Z, g, p1, C_SR, ci)
        finally:
            H.run_panels = frozen_rp
    part = {k: Fr(v, 20) for k, v in H.PARTITION_20THS.items()}
    lines = {"equation_defect_polynomial": "B_eq", "truncation_patch_local": "B_trunc",
             "tail_zeta_and_moments": "B_tail", "endpoint_slivers": "B_end",
             "interval_arithmetic": "B_int", "rounding_exact_dyadic": "B_round"}
    Bc = Fr(H.B_CANDIDATE).limit_denominator(10 ** 6)
    exact_gates = {}
    for tag, cert in (("o9", o9), ("baseline", base)):
        exact_gates[tag] = {k: exact_le(cert["components"][k], Bc * part[ln] / Fr(C_SR))
                            for k, ln in lines.items()}
    comps = {k: {"baseline": base["components"][k], "o9": o9["components"][k]} for k in base["components"]}
    return {"patch": list(H.PATCH), "n_panels": n_z, "coefficients_compared": n,
            "A5_1_bit_identical_o9_vs_opt_backend": bit_opt,
            "A5_1_error_channels_bit_identical_panels_informational": sum(per_panel),
            "A5_2_overlap_o9_vs_harness": cmp_ov,
            "A5_1b_error_channel_o9_le_opt_all": all(x >= 0 for x in shortfalls),
            "A5_1b_error_channel_shortfall_lt_2m200_all": all(abs(x) < Fr(1, 2 ** 200) for x in shortfalls),
            "A5_1b_error_channel_max_rel_shortfall": float(max(shortfalls)),
            "A5_1b_error_channel_min_rel_shortfall": float(min(shortfalls)),
            "o9_error_channels_ge_baseline_panels": sum(exz_ge),
            "B_candidate_exact": str(Bc),
            "components": comps, "delta_baseline": base["delta_F0"], "delta_o9": o9["delta_F0"],
            "A5_3_o9_frozen_verdicts_all_pass": o9["all_lines_pass"],
            "A5_3_o9_exact_gates": exact_gates["o9"], "baseline_exact_gates": exact_gates["baseline"],
            "A5_4_delta_o9_lt_baseline_observed": o9["delta_F0"] < base["delta_F0"]}


def main() -> int:
    T.check_threads()
    doc, old, m = doctrine(), old_verifier(), measure()
    n = m["coefficients_compared"]
    checks = {
        "doctrine_bound_and_present": doc["present"],
        "old_verifier_all_pass": old["all_pass"] and old["returncode"] == 0,
        "old_governance_namespace_unchanged": old["governance_namespace_unchanged"],
        "A5_1a_bit_identical_to_committed_o9_reference": old["checks"]["C_committed_packet_hashes_reproduced"]
                                                         and old["checks"]["C_per_shift_identical_to_committed"],
        "A5_1b_coefficients_bit_identical_opt_backend_4032": m["A5_1_bit_identical_o9_vs_opt_backend"] == n == 4032,
        "A5_1b_error_channel_frozen_relation": m["A5_1b_error_channel_o9_le_opt_all"]
                                               and m["A5_1b_error_channel_shortfall_lt_2m200_all"],
        "A5_2_overlap_4032": m["A5_2_overlap_o9_vs_harness"] == n,
        "A5_3_o9_certificate_all_frozen_lines_pass": m["A5_3_o9_frozen_verdicts_all_pass"],
        "A5_3_o9_exact_gates_all_pass": all(m["A5_3_o9_exact_gates"].values()),
        "A4_baseline_exact_gates_all_pass": all(m["baseline_exact_gates"].values()),
    }
    out = {"schema": "rebaseguard.p5y.k1.sr.o9.a5-amendment.v1",
           "classification": "T2_A5_GOVERNANCE_AMENDMENT_CLOSED" if all(checks.values()) else "STOP",
           "amends": {"commit": "a296244c866368c78750eb5b1800aee8decbd249",
                      "file": "p5y_k1_sr_o9_pre_t2_governance_successor/config/PRE_T2_GOVERNANCE.json",
                      "file_sha256": sha(GOV / "config/PRE_T2_GOVERNANCE.json"),
                      "field": "issue_1_reference_criterion.A_task1r_F0.A5"},
           "old_A5": OLD_A5,
           "a51_encoding_note": ("A first encoding of A5.1 in this verifier also demanded error-channel bit-identity with "
                                 "opt_backend; that is frozen-documented false (O9 error channel smaller by <= ~2^-248 "
                                 "relative). A5.1 is encoded as the user's text '/ O9 reference' plus the frozen C4 "
                                 "relation; today's max relative shortfall at (17,11) is reported against the disclosed "
                                 "sample max 1.25e-75 (a sample statistic, not a frozen bound; the frozen bound is C4's "
                                 "2^-200)."),
           "old_A5_status": ("GOVERNANCE SPECIFICATION ERROR: contradicted the already-adjudicated optimized-backend "
                             "acceptance doctrine (bit-equality with the reference harness was never the frozen "
                             "criterion; the optimized certificate is adjudicated as not uniformly conservative)"),
           "new_A5": NEW_A5,
           "unchanged": ["A1-A4", "A6", "B1-B5", "C1-C5", "issue_2_panel_universe", "cap status UNQUALIFIED",
                         "every threshold, budget, patch, panel, D, Z, precision, degree, candidate, contract, "
                         "obligation and the theorem target"],
           "doctrine": doc, "old_verifier": old, "measurement": m, "checks": checks,
           "all_pass": all(checks.values())}
    (NS / "config/A5_AMENDMENT.json").write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    print(json.dumps({"checks": checks, "classification": out["classification"],
                      "doctrine_paths": {k: v for k, v in doc.items() if isinstance(v, list)},
                      "delta": [m["delta_baseline"], m["delta_o9"]]}, indent=1))
    return 0 if out["all_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
