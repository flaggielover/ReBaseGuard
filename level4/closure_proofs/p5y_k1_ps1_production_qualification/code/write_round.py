"""Write RESULT.md (report sections A-P) and the round record for the PS1 cost-requalification / authorization round
from committed evidence only."""
import json
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
E = NS / "evidence"
CP = NS.parent


def j(p):
    return json.loads(Path(p).read_text())


def main():
    adj = j(E / "PS1_AUTHORIZATION_ADJUDICATION.json")
    qs = j(E / "qual_summary.json")
    dec = j(E / "cost_decomposition.json")
    cons = j(CP / "p5y_k1_ps1_production/config/PS1_CONSTANTS.json")
    idl = j(E / "identity/id_small.json")
    probe = j(E / "runtime_probe_aws.json")
    mks = j(E / "qual/makespan_model.json")
    prov = j(E / "historical_ledger_provenance.json")
    rep = j(E / "acceptance/replay/replay.json")
    ser = {b: j(E / f"bench_opt/series_{b}.json") for b in ("b1", "b2", "b4", "b8", "b16")}
    fro = {b: j(E / f"bench/series_{b}.json") for b in ("b1", "b2", "b4")}
    st = qs["per_cell_cpu_h_stats"]
    pr = qs["projection_cpu_h"]
    L = ["# PS1 full-campaign cost requalification and pre-result production authorization", "",
         f"**Classification: `{adj['classification']}`.** `AWS_GENUINE_PS1_SR_PRODUCTION_AUTHORIZED_TO_START = "
         f"{adj['AWS_GENUINE_PS1_SR_PRODUCTION_AUTHORIZED_TO_START']}` - NOT started. Genuine PS1 production cells: 0.", "",
         "## A. Current cost decomposition (frozen certifier, idle core, full-cell model)", "",
         "| cell | CPU-h | basis | strips F | O9 core D | shared tensors B | drift tensors C | residual E | other |",
         "|---|---:|---|---:|---:|---:|---:|---:|---:|"]
    for s, c in sorted(dec["cells"].items(), key=lambda x: int(x[0])):
        sh = c["stage_share"]
        basis = ("Phase-4 measured" if c["cost_basis"] == "phase4_measured_cell"
                 else "13-cell mean (cell NOT in the qualification set; only its stage SHARES are its own)")
        L.append(f"| {s} | {c['cell_cpu_h']:.2f} | {basis} | " + " | ".join(
            f"{100 * sh.get(k, 0):.0f}%" for k in ("F_endpoint_strip_work", "D_operator_contractions", "B_shared_patch_tensors",
                                                  "C_raw_shift_drift_tensors", "E_residual_certification", "other_python_overhead")) + " |")
    L += ["", f"Topology duplication (L): 32-way SMT costs {dec['L_duplicated_by_topology']['smt_30_to_32_way_cpu_inflation_vs_16']:.2f}x "
          "the CPU of 16 physical-core workers for the same work; the committed runs used 30 workers.", "",
          "## B/C. Optimizations and measured speedups (all bit-identical)", "",
          f"- OPT-S/OPT-C shift-independent memoisation: frozen {idl['cpu_frozen']:.1f} s -> {idl['cpu_opt']:.1f} s on the identity set; "
          "343/343 cell-patch records bit-identical to committed certified records; full-cell identity of 6 certified cells.",
          "- One worker per physical core (16, pinned 0-15) instead of 30 on 16 cores.",
          "- Deterministic groups of 4 cells per worker (patch-outer, shared drift-independent panel cache).", "",
          "| cells per patch | frozen CPU-s/cell | optimised CPU-s/cell |", "|---:|---:|---:|"]
    for b, n in (("b1", 1), ("b2", 2), ("b4", 4), ("b8", 8), ("b16", 16)):
        f = f"{fro[b]['cpu_s'] / n:.1f}" if b in fro else "-"
        L.append(f"| {n} | {f} | {ser[b]['cpu_s'] / n:.1f} |")
    L += ["", "## D. Requalified projection (measured, 13 real cells, production unit, 16 physical-core workers)", "",
          f"Per-cell CPU-h: mean {st['mean']:.2f}, p50 {st['p50']:.2f}, p90 {st['p90']:.2f}, max {st['max']:.2f} (n={st['n']}).",
          f"369-cell projection: {pr['mean_based']:.0f} CPU-h (mean groups), {pr['worst_group_based']:.0f} (worst group); "
          f"+10% {pr['mean_plus_10pct']:.0f}, +15% {pr['mean_plus_15pct']:.0f}.", "",
          f"## E. Recommended global cap: {cons['GLOBAL_CPU_CAP']:.0f} CPU-h (PS1 only; derivation in config/PS1_CONSTANTS.json)", "",
          "## F/G. Throughput", "",
          f"AWS: Xeon 8488C, 16 physical cores, 123 GiB, runtime {probe['runtime']['sha256'][:16]}; 16 workers -> "
          f"about {16 * 24 / st['mean']:.0f} cells/day.",
          "Vultr: EPYC-Milan 8 vCPU (8 independent in the prior benchmark), 15 GiB; NOT qualified for PS1 (no PS1 code deployed).", "",
          "## H/I. Shard plan and wall time", "",
          "Production dispatches a WHOLE cell group to an idle worker slot and runs all 3,994 live patches for that "
          "group's cells inside the one worker; a group is never split across workers. Wall time is therefore the "
          f"makespan of {mks['groups']} tasks (92 groups of 4 cells + the terminal [368]) greedily dispatched to "
          f"{mks['workers']} slots.", "",
          "| basis | total CPU-h | ideal wall (perfectly divisible) | makespan | utilisation |", "|---|---:|---:|---:|---:|"]
    for nm, sc in mks["scenarios"].items():
        L.append(f"| {nm.replace('_', ' ')} | {sc['total_cpu_h']:.0f} | "
                 f"{sc['ideal_wall_h_if_perfectly_divisible'] / 24:.2f} d | {sc['makespan_wall_days']:.2f} d | "
                 f"{sc['utilisation']:.3f} |")
    sc0 = mks["scenarios"]["worst_group_based"]
    qc = mks["qualification_harness_contrast"]
    L += ["",
          f"Slot occupancy: {sc0['groups_per_slot']} (groups per slot). The only imbalance is quantisation - 93 does "
          f"not divide by 16 - costing {sc0['quantisation_factor_vs_ideal']:.3f}x over the perfectly divisible ideal.",
          "",
          f"The Phase-4 qualification harness had a DIFFERENT shape: all 16 workers split ONE group's patch range, and "
          f"the low patch indices carried 290/291 patches against ~244 and were the expensive ones, giving "
          f"{qc['mean_imbalance']:.2f}x within-group worker imbalance (measured 1.37/1.37/1.30 across the three "
          f"4-cell groups) and a long single-worker tail. That shape does NOT occur in production and is recorded in "
          "evidence/qual/makespan_model.json for contrast only.", "",
          "## J-M. Lifecycle, adapter, precision/transport, clean checkout", "",
          f"Lifecycle: REUSE_WITH_ADDITIVE_PS1_ADAPTER. Suite exit codes: {adj['suite_exit_codes']}.", "",
          f"Deterministic fresh-process replay of Phase-4 production-path records: {rep['identical']}, "
          f"all_identical={rep['all_identical']}.", "",
          "Executor identity: 343/343 cell-patch records bit-identical to committed certified records; full-cell "
          "identity (t3 delta and x0, consumed records, t4 ledgers, t5 statuses) for the 6 certified cells "
          "150, 360-363, 368, each 28/28.", "",
          "### Known pre-existing failure in the original audited lifecycle suite", "",
          "`original_lifecycle_suite` exits 1 on exactly one assertion, "
          "`test_lifecycle_integrated.py::test_real_production_namespaces_untouched`, which requires the real "
          "production namespace to contain only README.md. It also contains PRODUCTION_LEDGER.json, written by the "
          f"historical torn attempt of 2026-09-10 (sha256 {prov['sha256'][:16]}..., "
          f"{prov['genuine_completed_cells']} genuine cells completed, "
          f"{prov['committed_cpu_h_by_role']['AWS']:.6f} CPU-h committed, 16 cells torn). That file predates this "
          "round's parent commit by two days and is byte-unchanged; the suite is preserved unchanged and the "
          "assertion is a correct report, not a regression. adjudicate.py accepts the non-zero exit ONLY while the "
          "ledger hashes to the recorded historical value, still records no genuine cell, and that test is the sole "
          f"failure with no errors; disposition recorded as `{adj['original_lifecycle_suite_disposition']}`. Any "
          "mutation, any genuine cell, or any second failure fails the check closed.", "",
          "### Historical production ledger: superseded, not inherited", "",
          "The frozen authorization records the historical ledger as "
          "`IMMUTABLE HISTORY; SUPERSEDED FOR PS1 ONLY (not inherited)`. PS1 opens a fresh ledger under "
          "p5y_k1_ps1_production/production/, which is empty at freeze (README.md only). The historical ledger was "
          "read for verification and never written. Evidence: evidence/historical_ledger_provenance.json.", "",
          "## N. Commits", "",
          f"producer {adj['producer_commit']}, authorization {adj['authorization_commit']}, adapter {adj['adapter_commit']}.", "",
          "## O. Genuine production cells: 0", "",
          "## P. Start command (NOT RUN)", "",
          "    /home/ubuntu/work/ReBaseGuard/level4/.venv/bin/python \\",
          "      /home/ubuntu/work/ReBaseGuard-ps1-ops/level4/closure_proofs/p5y_k1_ps1_lifecycle_adapter/ops/prodctl.py start --role AWS",
          "", "Operator preconditions: " + "; ".join(adj["operator_preconditions_before_start"]), ""]
    (NS / "RESULT.md").write_text("\n".join(L))
    print("RESULT.md written;", adj["classification"])


if __name__ == "__main__":
    main()
