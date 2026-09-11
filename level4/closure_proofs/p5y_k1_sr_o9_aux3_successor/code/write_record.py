"""Write the immutable record and RESULT.md of the aux3-SR feasibility round from committed evidence only."""
import hashlib
import json
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
EV = NS / "evidence"
MS = ("2", "3", "5")
SUBSTANTIAL = 1.10          # kill-rule reading: a ratio above 1.10 is a substantial margin over 1


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def load(n):
    return json.loads((EV / n).read_text())


def main():
    p1, p2 = load("phase1_doctrine.json"), load("phase2_equations.json")
    orc, ext, v2 = load("phase34_oracle_c313.json"), load("phase34_tower_ext_c313.json"), load("phase34_consistent_v2_c313.json")
    det = [x for x in (EV / "replay/determinism.txt").read_text().split("\n") if x]
    arch = v2["variants"]["N4/true_midpoint/kz_exact"]
    worst = {m: arch[m]["B_cover_ratio"] for m in MS}
    fail = any(v > SUBSTANTIAL for v in worst.values())
    cls = "AUX3_SR_FEASIBILITY_FAIL" if fail else "PHASE5_WOULD_BE_NEXT"
    ev = {n: sha(EV / n) for n in ("phase1_doctrine.json", "phase2_equations.json", "phase34_oracle_c313.json",
                                   "phase34_tower_ext_c313.json", "phase34_consistent_v2_c313.json", "phase34_consistent_c313.json")}
    rec = {
        "schema": "rebaseguard.p5y.k1.sr.o9.aux3-sr-record.v1", "parent_commit": "d2981a5",
        "parent_tag": "p5y-k1-sr-o9-opnorm-successor-insufficient", "classification": cls,
        "evidence_sha256": ev,
        "phase1": {"ruling": p1["ruling"], "answers": p1["answers"]},
        "phase2": {k: p2[k] for k in ("auxiliary_candidates", "image_nodes", "n_auxiliary_candidates", "n_image_nodes",
                                      "n_new_contracts", "n_new_contracts_on_frozen_candidates", "new_raw_moment_shifts", "dag_sha256")},
        "phase4_true_function": {m: {k: orc["true"][m][k] for k in ("R2_e0", "R3_e0", "sup_cell_R2", "sup_cell_R4")}
                                 for m in ("1",) + MS},
        "phase4_cover_ratios": {
            "ideal_true_M_R4": {m: orc["cover"][m]["true_M_R4"]["B_cover_ratio"] for m in MS},
            "pure_norm_tower_order4_exact_norms": {m: orc["cover"][m]["tower_exact"]["B_cover_ratio"] for m in MS},
            "pure_norm_tower_order4_certform_norms": {m: orc["cover"][m]["tower_certform"]["B_cover_ratio"] for m in MS},
            "one_level_hybrid_true_lower_orders": {m: ext["one_level_hybrid"][m]["B_cover_ratio"] for m in MS},
            "self_consistent_N4_ideal_midpoint_exact_norms (THE ARCHITECTURE, best case)": worst,
            "all_self_consistent_variants": {k: ({m: v[m]["B_cover_ratio"] for m in ("1",) + MS} if "no_bound" not in v
                                                 else {"no_bound": v["no_bound"], "q_N": v["contraction_qN"]})
                                             for k, v in v2["variants"].items()},
            "contraction_qN": {k: v["contraction_qN"] for k, v in v2["variants"].items()},
            "pure_tower_minimal_taylor_order": ext["minimal_taylor_order"]},
        "kill_rule": f"any m in (2,3,5) with best-case certified-architecture ratio > {SUBSTANTIAL} -> AUX3_SR_FEASIBILITY_FAIL",
        "phases_not_run": {"5": "kill rule", "6": "kill rule", "7": "no successor evidence to govern"},
        "why": ("The true R_m is benign on cell 313 (sup_cell|R''''| ~ 0.44-0.91; ideal third-order cover 0.32), but every "
                "certifiable whole-cell fourth-order bound is norm-based. Pure norm towers give M_R4 ~ 2e3-4e3; the best "
                "self-consistent Taylor tower fed by IDEAL midpoint evidence (orders <= 3) and EXACT norms still leaves "
                "m=2,3,5 above 1, because the resolvent self-consistency q_N = C sum C(N,i) k_i rho^i/i! (C ~ 2, parent "
                "rho ~ 0.157) amplifies the remainder; adding order-4/5 midpoint candidates raises q_N toward and past 1."),
        "scaling_if_ever_pursued": {"aux_candidates_per_cell": p2["n_auxiliary_candidates"],
                                    "new_contracts_per_cell": p2["n_new_contracts"],
                                    "relative_to_frozen_T2_census": {"candidates": p2["n_auxiliary_candidates"] / 46,
                                                                     "contracts": p2["n_new_contracts"] / 102},
                                    "midpoint_only": True, "reusable_across_m": True,
                                    "measured": "NOT MEASURED (Phase 5 not run); T2-proportional estimate only"},
        "determinism_replay": det,
        "not_claimed": ["K1 CLOSED", "P5Y CLOSED", "PRODUCTION READY"],
        "untouched": ["theorem target", "B_cover = 1/20", "D, Z, precision, degree", "parent-cell geometry", "production",
                      "316-cell campaign", "historical 46/102 census", "all predecessors"]}
    (NS / "config/AUX3_SR_RECORD.json").write_text(json.dumps(rec, indent=1, sort_keys=True) + "\n")
    R = rec["phase4_cover_ratios"]
    L = ["# P5Y K1 SR O9 — aux3-style third-derivative evidence: feasibility + governance", "",
         f"**Classification: `{cls}`.** Parent `d2981a5`. Diagnostic only; nothing certified; no production; "
         "K1/P5Y not closed; not production ready.", "",
         "## Phase 1 — governance", "", f"Ruling `{p1['ruling']}`.", ""]
    L += [f"- **{k}**: {v}" for k, v in p1["answers"].items()]
    L += ["", "## Phase 2 — third-order equations", "",
          f"{p2['n_auxiliary_candidates']} auxiliary candidates (`{', '.join(p2['auxiliary_candidates'])}`), "
          f"{p2['n_image_nodes']} image nodes (`{', '.join(p2['image_nodes'])}`), {p2['n_new_contracts']} new contracts "
          f"({p2['n_new_contracts_on_frozen_candidates']} on frozen candidates), new raw moment shift(s) "
          f"{p2['new_raw_moment_shifts']}. All midpoint-only. DAG sha256 `{p2['dag_sha256'][:16]}`.", "",
          "## Phase 4 — feasibility oracle (cell 313)", "",
          "| m | R''(e0) | R'''(e0) | true sup R'' | true sup R'''' |", "|---|---:|---:|---:|---:|"]
    for m in ("1",) + MS:
        t = rec["phase4_true_function"][m]
        L.append(f"| {m} | {t['R2_e0']:.4g} | {t['R3_e0']:.4g} | {t['sup_cell_R2']:.4g} | {t['sup_cell_R4']:.4g} |")
    L += ["", "| B_cover / (1/20) | m2 | m3 | m5 |", "|---|---:|---:|---:|"]
    for lab, key in (("ideal (true M_R4)", "ideal_true_M_R4"), ("pure norm tower, order 4, exact norms", "pure_norm_tower_order4_exact_norms"),
                     ("pure norm tower, order 4, cert-form norms", "pure_norm_tower_order4_certform_norms"),
                     ("one-level hybrid (TRUE lower-order cell sups; not certifiable)", "one_level_hybrid_true_lower_orders"),
                     ("**self-consistent order-3 architecture, ideal midpoint, exact norms**",
                      "self_consistent_N4_ideal_midpoint_exact_norms (THE ARCHITECTURE, best case)")):
        L.append(f"| {lab} | " + " | ".join(f"{R[key][m]:.3g}" for m in MS) + " |")
    L += ["", "| self-consistent variant | q_N | m2 | m3 | m5 |", "|---|---:|---:|---:|---:|"]
    for k, v in R["all_self_consistent_variants"].items():
        L.append(f"| {k} | {R['contraction_qN'][k]:.3f} | " + (" | ".join(f"{v[m]:.3g}" for m in MS) if "no_bound" not in v
                                                                  else "no bound | no bound | no bound") + " |")
    L += ["", rec["why"], "", f"Kill rule: {rec['kill_rule']}. Phases 5–7 not run.", "",
          "## Cost / scaling (not measured)", "",
          f"{p2['n_auxiliary_candidates']} candidates and {p2['n_new_contracts']} contracts per cell "
          f"(+{100 * p2['n_auxiliary_candidates'] / 46:.0f}% / +{100 * p2['n_new_contracts'] / 102:.0f}% of the frozen T2 census), "
          "midpoint-only, reusable across m. Not measured because Phase 5 did not run.", "",
          "## Determinism", ""] + [f"- `{x}`" for x in det] + [""]
    (NS / "RESULT.md").write_text("\n".join(L))
    print(cls, worst, sha(NS / "config/AUX3_SR_RECORD.json"))


if __name__ == "__main__":
    main()
