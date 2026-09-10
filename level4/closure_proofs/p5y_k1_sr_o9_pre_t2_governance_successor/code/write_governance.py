"""Write config/PRE_T2_GOVERNANCE.json: the machine-readable pre-T2 rulings."""
import hashlib
import json
from fractions import Fraction as Fr
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
CP = NS.parents[0]
refs = json.loads((NS / "config/AUTHORIZED_RUNTIME_REFERENCES.json").read_text())
pan = json.loads((NS / "config/P1_PANEL_UNIVERSE.json").read_text())
ver = json.loads((NS / "evidence/pre_t2_verification.json").read_text())


def paths_with(node, needle, prefix=""):
    out = []
    if isinstance(node, dict):
        for k, v in node.items():
            out += paths_with(v, needle, f"{prefix}.{k}" if prefix else k)
    elif isinstance(node, list):
        for i, v in enumerate(node):
            out += paths_with(v, needle, f"{prefix}[{i}]")
    elif needle in str(node).replace(",", ""):
        out.append(prefix)
    return out


REBIND = {
    "p5y_k1_sr_backend_o9_successor/config/protocol.json": "O9 frozen_scope panel count (cost basis)",
    "p5y_k1_sr_backend_cost_audit/config/frozen_audit.json": "work model panel multiplier",
    "p5y_k1_sr_cap_authorized_successor/config/protocol.json": "cap scope panel count",
    "p5y_k1_sr_cap_authorized_successor/evidence/cap_derivation.json": "panel_contract_evaluations and per-cell reservation",
    "p5y_k1_cover_ledger_successor/config/cost_model.json": "cost model panel count",
    "p5y_k1_cover_ledger_successor/config/checkpoint.json": "non-binding cost/cover mention (binding blocks: P1, complexity, precision)",
    "p5y_k1_sr_production_authorized_successor/config/LAUNCH_AUTHORIZATION.json": "per_cell_reservation_cpu_h (derived from the cap basis)",
}
rebind = {}
for rel, why in REBIND.items():
    p = CP / rel
    d = json.loads(p.read_text())
    rebind[rel] = {"sha256": hashlib.sha256(p.read_bytes()).hexdigest(), "why": why,
                   "paths_83452": paths_with(d, "83452"),
                   "paths_2689824864": paths_with(d, "2689824864"),
                   "paths_11.474662": paths_with(d, "11.474662")}
for rel in ("p5y_k1_sr_cap_authorized_successor/PROTOCOL.md", "p5y_k1_sr_backend_o9_successor/RESULT.md",
            "p5y_gate2b_sr_cover/GATE2B_RESULT.md", "p5y_k1_sr_qualification/code/sr_patch.py"):
    p = CP / rel
    rebind[rel] = {"sha256": hashlib.sha256(p.read_bytes()).hexdigest(),
                   "why": "prose/code carrying the census panel count or census PatchIdentity(n_z, panels)",
                   "lines_83452": [i + 1 for i, l in enumerate(p.read_text().splitlines())
                                   if "83452" in l.replace(",", "")]}

cap = json.loads((CP / "p5y_k1_sr_cap_authorized_successor/evidence/cap_derivation.json").read_text())["step0_inputs"]
evals_old = cap["panel_contract_evaluations"]
evals_new = 102 * 316 * pan["contracted_panels_exec"]
rebased = {
    "status": "ARITHMETIC_REBASE_ONLY_NOT_A_REQUALIFICATION",
    "old_panel_contract_evaluations": evals_old,
    "old_basis": "102 x 316 x 83452 (census units, strips counted as contracted panels)",
    "new_panel_contract_evaluations": evals_new,
    "new_basis": f"102 x 316 x {pan['contracted_panels_exec']} (executed contracted span panels; slivers analytic)",
    "ratio": str(Fr(evals_new, evals_old)), "ratio_float": evals_new / evals_old,
    "contraction_cpu_h_dense_rebased": evals_new * cap["ms_per_contract_dense_random"] / 1000 / 3600,
    "contraction_cpu_h_real_rebased": evals_new * cap["ms_per_contract_real_F0"] / 1000 / 3600,
    "known_unmodelled_components": ["per-cell stage-1 PanelShared recompute or cache strategy (M0 tile-major)",
                                    "per-patch Taylor-model residual assembly for all 72 DAG nodes",
                                    "analytic sliver evaluation", "whole-cell envelope, refinement, ledger",
                                    "possible order-3 auxiliary evidence"],
}
g = {
    "schema": "rebaseguard.p5y.k1.sr.o9.pre-t2-governance.v1",
    "classification": "T2_GOVERNANCE_REPAIR_CLOSED",
    "parent": {"t1_commit": "ab8d197398dc1d11e7ef983c9d66347080356da1",
               "t1_tag": "p5y-k1-sr-o9-t1-candidate-construction"},
    "scientific_scope_changed": False,
    "unchanged": ["K1 theorem target sup_e |R_D,m(e)| < 2", "316 SR cells / 8849 obligations",
                  "3994 live patches (grid 64)", "D = 11, Z = 20", "precision 256 bits",
                  "bidegree (16,16)", "46 candidates / 102 (candidate, shift) contracts",
                  "P1 threshold 1e-9, headroom guard 1e-6, rule target (1-1e-3)1e-9",
                  "every ledger budget and gate", "far-field treatment"],
    "issue_1_reference_criterion": {
        "ruling": ("Historical Task1R/Gate-2F scalar records are immutable historical evidence produced under a "
                   "pre-resize runtime; by the frozen runtime-binding doctrine (aux4 RUNTIME_BINDING, "
                   "sr_patch.candidate_identity, cap PROTOCOL runtime refusal, replay_determinism) an identity is "
                   "(producer, runtime contract, inputs). T2 reference identity is therefore the frozen certifier "
                   "algorithm executed under the bound runtime contract, pinned by committed reference hashes; "
                   "historical scalars are drift/consistency evidence only. No threshold changes."),
        "runtime_contract": refs["authorized_runtime_contract"],
        "A_task1r_F0": {
            "A1": "live runtime contract hash (frozen gate_runtime_identity) == authorized",
            "A2": f"candidate mantissa sha256 == {refs['A']['candidate_mantissa_sha256']} and O9 packet hash == {refs['C']['committed_hashes']['real']}",
            "A3": f"frozen harness.certify canonical output sha256 == {refs['A']['authorized_runtime_output_sha256']}",
            "A4": "T2 certifier in task1r-baseline contraction mode returns components, delta_F0 and per_line byte-equal (canonical JSON) to the A3 output",
            "A5": "T2 O9 mode: Taylor coefficients exact()-identical to baseline mode per panel; ex, ez >= baseline (exact arb upper); delta_O9 >= delta_baseline; every gate compared in exact rationals",
            "A6_non_gating": "per-line PASS verdicts equal historical (gating); relative drift vs historical reported",
            "authorized_runtime_delta_F0": refs["A"]["authorized_runtime_output"]["delta_F0"],
            "historical_delta_F0": refs["A"]["historical"]["delta_F0"],
            "drift_rel": refs["A"]["drift_rel"]},
        "B_gate2f_hhat_1": {
            "B1": "live runtime contract hash == authorized",
            "B2": f"frozen Gate-2E run_cell(256, hhat_1) scientific output sha256 == {refs['B']['authorized_runtime_output_sha256']}",
            "B3": "kernel-identity fields byte-identical to the HISTORICAL record: " + ", ".join(sorted(refs["B"]["kernel_identity_equal_historical"])),
            "B4": "ABS_PASS equal historical; exact rational w_panel_total_ABS <= w_panel_max_ABS",
            "B5": "T2 panel-gate metric for hhat_1 at patch (17,11) equals the B2 output on every scientific field",
            "runtime_sensitive_fields": refs["B"]["runtime_sensitive_fields"],
            "drift_rel": refs["B"]["drift_rel"]},
        "C_o9": {
            "C1": "live runtime contract hash == authorized",
            "C2": f"T2 contraction reproduces committed packet hashes real {refs['C']['committed_hashes']['real']} and dense {refs['C']['committed_hashes']['dense']} over the {refs['C']['n_contexts']} frozen contexts (worker.py procedure)",
            "C3": "per-shift hashes (s = 0..3, real and dense) equal AUTHORIZED_RUNTIME_REFERENCES.C.per_shift_hashes",
            "C4": "worker baseline_check: coefficients bit-exact vs opt_backend.contract; error-channel shortfall < 2^-200",
            "C5": "raw z^s moment weights (census semantics) validated by a T2 unit test of the exact identity N^(s)_k = sum_t C(s,t) z_c^(s-t) N_(k+t)",
            "per_shift_hashes": refs["C"]["per_shift_hashes"]}},
    "issue_2_panel_universe": {
        "ruling": ("AUTHORITATIVE for execution: the binding P1 rule applied to the frozen certifier's own construction "
                   "(Task1R span partition + analytic endpoint slivers). The 83,452 census is P1-consistent for ITS "
                   "construction (core partition + strip panels; Gate-2B s7, re-verified: 0 failures) but that is not "
                   "the construction the frozen certifier executes; forcing census counts into the executed span "
                   "construction fails the binding P1 check on 1,011 patches. The census is superseded ONLY as the "
                   "executable T2 panel universe and as a cost multiplier; it remains immutable historical evidence."),
        "rule": pan["rule"], "canonical_panel_id": pan["canonical_panel_id"],
        "canonical_sliver_id": pan["canonical_sliver_id"],
        "contracted_panels_exec": pan["contracted_panels_exec"], "sliver_units_exec": pan["sliver_units_exec"],
        "panel_units_exec_census_convention": pan["panel_units_exec_census_convention"],
        "census_panel_units_historical": pan["panel_units_census"],
        "patches_count_differs": pan["patches_count_differs"], "P1_fail_counts": pan["P1_fail_counts"],
        "table_sha256": pan["table_sha256"],
        "boundaries": ("Executed boundaries are z_k = L_c + 2hk, h = span/(2 n_z_exec), for EVERY patch; they are "
                       "defined by the rule, never by the census (which fixed counts only). Relative to the census "
                       "construction every patch differs in construction (span vs core; analytic slivers vs strip "
                       "panels); the COUNT differs in 1,011 patches. Reference patch (17,11): n_z = 28 in both."),
        "local_gate_panel_max_n_panels_patch": "n_z_exec + 2 (equals Gate-2E N_PANELS = 30 at (17,11))",
        "o9_contract_identities": "the 102 (candidate, shift) contracts do not depend on panel IDs or counts: unchanged",
        "patch_identity": "sr_patch.PatchIdentity (census n_z, panels) remains historical; T2 uses the v2 panel IDs"},
    "rebinding_required": rebind,
    "cost_and_cap": {"cap_4500_status": "UNQUALIFIED",
                     "meaning": ("the historical 4500 CPU-h authorization record is preserved and not revoked, but its "
                                 "derivation basis (83,452 panel units as contracted panels) is superseded and it omits "
                                 "known components; it must be requalified at T7 from measured units before any "
                                 "production reauthorization"),
                     "rebased_contraction_line": rebased},
    "history_preserved": ["all historical Task1R/Gate-2F values", "the 83,452 census", "O9 and cap artifacts",
                          "T1 commit/history", "first production attempt 20260910T105333Z-640db8f2 and its settled "
                          "accounting (0 genuine cells, 16 cells torn_attempts=1)"],
    "supersession_scope": "future T2+ execution only, where inconsistent; no predecessor is edited",
    "t2_may_resume": True,
    "t2_resume_conditions": ["implement criteria A1-A6, B1-B5, C1-C5 as T2 gates",
                             "use the task1r-span-p1-v1 executable panel universe (table_sha256)",
                             "run verify_pre_t2.py verify with all checks true before T2 evidence is accepted"],
    "verification_evidence_sha256": hashlib.sha256((NS / "evidence/pre_t2_verification.json").read_bytes()).hexdigest(),
    "verification_all_pass": ver["all_pass"],
}
(NS / "config/PRE_T2_GOVERNANCE.json").write_text(json.dumps(g, indent=1, sort_keys=True) + "\n")
print(json.dumps({"rebased": rebased, "rebind_keys": {k: {kk: v[kk] for kk in v if kk.startswith(("paths", "lines"))} for k, v in rebind.items()}}, indent=1))
