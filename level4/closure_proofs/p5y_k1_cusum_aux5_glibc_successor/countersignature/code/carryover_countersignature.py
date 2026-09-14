"""Independent carry-over countersignature for the CUSUM Aux5 new-glibc successor: deterministic builder and fail-closed verifier.

GOVERNANCE ONLY. NON-CERTIFYING. It never starts a certifier, never reads or writes a runtime root, and never authorizes
production. A valid countersignature records CARRYOVER_AUTHORIZED = YES and PRODUCTION_LAUNCH_AUTHORIZED = NO. Its validity
does not depend on a successor checkpoint; glibc_successor.launch_readiness stays NOT_READY until a successor checkpoint,
run authorization and launch preflight exist and pass.

  python carryover_countersignature.py build --signing F   write config/COUNTERSIGNATURE.json and its hash file (never overwrites)
  python carryover_countersignature.py verify              exit 0 iff the committed countersignature is valid
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve()
sys.path.insert(0, str(HERE.parents[2] / "code"))

import glibc_successor as G                                                     # noqa: E402
import q6_result as R                                                           # noqa: E402

CS_REL = "config/COUNTERSIGNATURE.json"
CS_HASH_REL = "countersignature/COUNTERSIGNATURE_HASH"
RECORD_REL = "countersignature/README.md"
BRANCH = "p5y-postk1-frontier"
UNSETTLED_RUN = "R20260913T115713Z-103963"
STOP_ISSUE = "D_" + G.STOP_KEY
REVOKED_COUNTERSIGNATURE = "a58b1ad175567b232531ee4a65d131bbf48d6a72b9c7d1f71ac996e04734821f"
UTC_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")

COMMITS = {
    "base_commit": G.BASE_COMMIT,
    "proposal_freeze_commit": "3e26bb3016a45236a3ecb38236dc0ddd463e5650",
    "q6_result_commit": "74d6efb3c68a05c386444a1d3322c403b726408a",
    "q6_evidence_repair_commit": "575a1ee28567a284d21fffd24c2b782daa717275",
}

Q1 = "evidence/requalification_r1/qualification_r1"
NS_PINS = {
    "config/GLIBC_SUCCESSOR_PROPOSAL.json": "964dc9691a4d5261d244c64426b6438a2ca7e6d2ef7329c26399345d60e34241",
    "config/PREDECESSOR_BINDING.json": "0676fc8267bac3fc6044ab4cb9f57c8769b2b9d62e0d2f0bb2a2d3b1d9db8ac3",
    "evidence/requalification_r1/Q6_RESULT.json": "894f2e8aae6eb38beb2d389a1447a0fce8e1d0d3189fb49ca683701604dc3d88",
    "config/REQUALIFICATION_PROTOCOL.json": "38a7f97884736e3e7cb1e35bcf7e6e2d7d82abbe263fc0cfcdb9feaad019d244",
    "config/Q6_REFERENCE.json": "124376c0f98a112ebc2404db72bec782646d1d14fd8a359b8dd6425df5548597",
    "config/CPU_CAP_CONTINUITY.json": "ada6309602eccc18881c8fc5a6a79607a0572f3e81d8a12aafcd0ec871644866",
    "CARRYOVER_PROTOCOL.md": "3812b13b04ff1df186724cdd33516cad9545a01be072ca89ce96fc166bd94c01",
    "SUCCESSOR_CHECKPOINT_SPEC.md": "6cc0d187ef0efd19d7eb5dbdaf61425f66cb055651f1ca1f72e4fae9934aa945",
    "HOST_CONTAINMENT_PLAN.md": "fa8417dff0309bc676486e2f801fe486b7cb32a1c3894a770f875b9a690021c6",
    "HOST_DRIFT_FORENSIC_AUDIT.md": "b4d40f32eba88ffb3a8890317c70d5b6a47e1c74ed03cb0cf5bdc9a3d884a535",
    "code/glibc_successor.py": "785c6bddf9b0b8acc551a7fd7c10df79fcecd181f5dc8910b6f26bc605fa53b6",
    "evidence/containment/PRE_STATE.json": "7c1e6d24d5214428d82e44621acccd942a56e96dc733cbf15bae55337c923d20",
    "evidence/containment/POST_STATE.json": "5af4e10228278be2308cf0caf584328c2a320118f2e24d081f575fd3bcef5940",
    "evidence/containment/POST_RUN_STATE.json": "9cead60d02167a4f7e45d1e982ed5bd2511c63f04d01eb23083e3c9ef36bcf72",
    "evidence/requalification_r1/HOST_AT_RUN_END.json": "4db9e45dbb1ba6f63c6bc378e61abc467737b8ad722b085cc32f40de3a056c1f",
    "evidence/requalification_r1/RUN_METADATA.json": "cf0b901b09ec3120dfde586dea256fd45cbcd8626f59fc4eb43e0d04877e7223",
    "evidence/requalification_r1/ANALYSIS_RESULT.json": "1376825ebbf0c1f2f04f6d7823ee05e99404b77b081e45d8835bf2c6f195ba8e",
    f"{Q1}/c318_A/run.log": "9fe3882fcbab04103cb066f6b621188efc3575301ca70fa056ad6e2eb81a031d",
    f"{Q1}/c318_B/run.log": "3e9b2928a5b31df5257a3221701ff1c57f9b35ad061e1d2cf49c6abb667ae73d",
    f"{Q1}/c323_A/run.log": "063d6764593193e8efdfc20ce1569c10e98c2c1ee180b7f37706b0e249d22a5b",
    f"{Q1}/c323_B/run.log": "8fa7578b854f48bf86e0eb6bbafb54cdd7edb582a2c5e837c293f34265136ad3",
    f"{Q1}/c318_A/aux5_CUSUM_318_256.json": "1227ccfac08ae816d3fe71905aa34be836b2b38461e6b024e6b2b931980aedd3",
    f"{Q1}/c318_B/aux5_CUSUM_318_256.json": "670c87edcfda4c0122c3b5490bb3cc44fbb67884188fe0707cb283e074aa1752",
    f"{Q1}/c323_A/aux5_CUSUM_323_256.json": "1271938a317f96dfef3979c30f98493fe4b3ee5988af3842d04df712394645be",
    f"{Q1}/c323_B/aux5_CUSUM_323_256.json": "2671319a942b2306c61ec5964ffa6f87f29eddb432e5f9686a58629060913835",
}
# bound by hash inside the countersignature (rebuild equality), without an independent pin
NS_BOUND = tuple(sorted(set(NS_PINS) | {
    "README.md", "config/GLIBC_SUCCESSOR_PROPOSAL_HASH", "code/q6_result.py", "tests/test_glibc_successor.py",
    "tests/test_q6_result.py", "evidence/requalification_r1/Q6_RESULT.md", "evidence/requalification_r1/HOST_AT_LAUNCH.json",
    "evidence/requalification_r1/PROBE.json", "evidence/requalification_r1/AFFINITY_AT_LAUNCH.json", f"{Q1}/checkout_head",
    f"{Q1}/c318_A/rc", f"{Q1}/c318_B/rc", f"{Q1}/c323_A/rc", f"{Q1}/c323_B/rc",
    RECORD_REL, "countersignature/code/carryover_countersignature.py",
    "countersignature/tests/test_carryover_countersignature.py"}))

LP = "level4/closure_proofs"
CLAUSE_SOURCE = f"{LP}/p5y_k1_cover_ledger_successor/CHECKPOINT.md"
REPO_PINS = {
    CLAUSE_SOURCE: "c487421fed7fe1e12362d785841dff88933f286b10d0942a5bfebfe571fd8b84",
    f"{G.SUCC_REL}/config/PROVENANCE_CHECKPOINT.json": G.EXPECTED["checkpoint_sha256"],
    f"{G.SUCC_REL}/config/RUN_AUTHORIZATION.json": G.EXPECTED["authorization_sha256"],
    f"{G.SUCC_REL}/config/COUNTERSIGNATURE.json": G.EXPECTED["countersignature_sha256"],
    f"{G.SUCC_REL}/config/FREEZE_RECORD.json": "e61dcc15f8f6ab89752596109782d9108e8d25962271e3858b6c8b8a7af31ec1",
    f"{G.SUCC_REL}/code/prov_integrity.py": "117a38116bc9711e57b5e8ddd2b9e2705fe1581cbbc2cf5e2c33e63a3c442375",
    f"{G.ISS_REL}/evidence/revocation_r1/REVOCATION.json": "69290aed4bf6239700d9acf849cb45ad65dba2a00542ac80d54fc660f308f4db",
    f"{G.ISS_REL}/evidence/post_signature_r2/POST_SIGNATURE_RECORD.json":
        "868ed32c4a300479cba0d08bfd67a86593d2c0bca975ff8954c3a3172f7b7112",
    f"{LP}/p5y_k2k5_postk1_audit/config/K4_ASSEMBLY_CHECKPOINT.json":
        "95b1fd16ac420d6f545cbb2619a6086ced31c6d748a9c801ca7f7c114e77a1e1",
    f"{LP}/p5y_k2k5_postk1_audit/code/k4_assembly.py": "6e9518b0dc1f399984a36af313fd58ad80746e80f2c3a356a35ddef6c3568de7",
    f"{LP}/p5y_k1_ps1_portable_recovery/config/GENERATION_TRANSITION.json":
        "039aecfe2e25284f492704cc363b70a7cf6dc89c629c868973038b8af20178d9",
}
PROTECTED_TREES = {
    f"{LP}/p5y_k1_cusum_aux5_successor": "7ccf1c59700f518efc3f1421f4f5ec7752ee268c",
    f"{LP}/p5y_k1_cusum_aux5_production_checkpoint": "3d897656b2ff8d4293f7d9ac1e6366b0d4c2686c",
    f"{LP}/p5y_k1_cusum_aux5_production_provenance_successor": "f4df63d9e9108a07eaecb633cf66dc59a234e07d",
    f"{LP}/p5y_k1_cusum_aux5_countersignature_issuance": "f3ada05b656cc8a349a386abdff7ffcdfd25d511",
    f"{LP}/p5y_k1_cusum_kernel": "61dc3d1d81e3557b7639a2848a158c100dcc4213",
    f"{LP}/p5y_k1_cusum_completion_successor": "0779273faf6907186516df480347e79883515b2f",
    f"{LP}/p5y_postk1_precompute_resolution": "8c19e113a0c91974cbc9112582f9ec22d26fb94e",
    f"{LP}/p5y_k2k5_postk1_audit": "f8ccc1b8e7848c7162eab3592b9f6b2f5413393f",
    f"{LP}/p5y_k1_cover_ledger_successor": "82af78565f115f65ced76d962b22c755432e823b",
}

AUTHORIZATIONS = {
    "CARRYOVER_AUTHORIZED": True,
    "CARRYOVER_RULE_ACTIVE_IN_PRODUCTION": False,
    "PRODUCTION_LAUNCH_AUTHORIZED": False,
    "SUCCESSOR_CHECKPOINT_CREATED": False,
    "SUCCESSOR_RUN_AUTHORIZATION_CREATED": False,
    "PRODUCTION_RESTARTED": False,
    "Q6_RERUN": False,
    "PREDECESSOR_CELLS_RECOMPUTED": False,
    "PREDECESSOR_ARTIFACT_MODIFIED": False,
    "PREDECESSOR_TERMINAL_DISPOSITION_CLEARED": False,
}
LAUNCH_SEMANTICS = {
    "countersignature_role": "NECESSARY_BUT_NOT_SUFFICIENT_FOR_PRODUCTION_LAUNCH",
    "verdict_label_note": "the verdict label APPROVED_CARRYOVER_AND_SUCCESSOR_LAUNCH is fixed by SUCCESSOR_CHECKPOINT_SPEC.md "
                          "section 1 and glibc_successor.COUNTERSIGN_VERDICT; it grants carry-over only and launches nothing",
    "carryover_rule_activation": "per CARRYOVER_PROTOCOL.md activation condition (d), the approved rule becomes active in "
                                 "production only when a successor checkpoint binds this countersignature",
    "launch_requires": [
        "a valid successor checkpoint that binds this countersignature sha256 and every SUCCESSOR_CHECKPOINT_SPEC.md binding",
        "a pre-result successor run authorization (result_bearing false) bound to that checkpoint",
        "the successor launch preflight (SUCCESSOR_CHECKPOINT_SPEC.md section 5) passing",
        "glibc_successor.py launch-readiness returning READY_TO_LAUNCH_SUCCESSOR",
        "an explicit operator launch command",
    ],
    "checkpoint_existence_is_a_validity_condition_of_this_countersignature": False,
}
APPROVALS = {
    "A1_predecessor_carryover_set": "cells 0-127 are the predecessor carry-over set: the 128 verified (record, envelope) pairs "
                                    "of the terminal predecessor ledger, unchanged",
    "A2_successor_production_universe": "cells 128-325 (198 cells) are the only successor production universe",
    "A3_disjoint_union_composite_model": "SUCCESSOR_PRODUCTION_RESULT = OLD_CARRYOVER (0-127) disjoint-union NEW_SUCCESSOR "
                                         "(128-325), covering exactly 0-325",
    "A4_cells_124_127_admissible": "cells 124-127 are admissible: reserved and started before the libc replacement, sealed "
                                   "under the frozen rule that stops admissions only, with verified envelopes",
    "A5_q6_runtime_equivalence": "Q6 (cells 318 and 323, two repeats each, scientific and all certificate hashes identical to "
                                 "the predecessor qualification under the new glibc) is sufficient runtime-equivalence evidence",
    "A6_k4_composite_attestation": "the K4 composite attestation of SUCCESSOR_CHECKPOINT_SPEC.md section 6 is an admissible "
                                   "additive consumer path, subject to conditions (b) and (c)",
    "A7_predecessor_ledger_preserved": "the predecessor " + G.TERMINAL + " ledger, journal, reaper, records and envelopes stay "
                                       "immutable historical evidence; its terminal disposition is never cleared or rewritten",
    "A8_predecessor_authority_preserved": "the old 128 records stay governed by predecessor authorization "
                                          + G.EXPECTED["authorization_sha256"] + " and active countersignature "
                                          + G.EXPECTED["countersignature_sha256"] + "; nothing here relabels or mutates them",
    "A9_continuous_cap": "the absolute 300 CPU-h campaign cap is accounted continuously across predecessor and successor",
}
PARTITION = {
    "OLD_CARRYOVER": [0, 127],
    "NEW_SUCCESSOR": [128, 325],
    "universe": 326,
    "rule": "disjoint union, exactly cells 0-325; no OLD_CARRYOVER cell is ever recomputed or entered into the successor ledger",
}
CPU = {
    "PREDECESSOR_SETTLED_CPU_US": 262686610580,
    "ABSOLUTE_CAP_US": 1080000000000,
    "SUCCESSOR_RESIDUAL_CAP_US": 817313389420,
    "ADMISSION_INVARIANT": [115, 100],
    "RESERVATION_US": 3600000000,
}
CPU_STATEMENTS = {
    "predecessor_cpu_cannot_be_reset": "predecessor settled CPU is charged once, as ABSOLUTE_CAP_US - SUCCESSOR_RESIDUAL_CAP_US, "
                                       "and can never be reset, removed or offset",
    "qualification_cpu_excluded_but_disclosed": "Q6 requalification CPU is excluded from the campaign cap and disclosed",
    "absolute_cap_may_not_be_raised": "the absolute 300 CPU-h cap may only be confirmed or lowered, never raised",
    "no_duplicate_charging_of_old_cells": "old cells enter only through the residual cap; the successor ledger has no import "
                                          "transition and never reads predecessor reaper records",
    "no_undercharging_of_predecessor_settlement": "the unsettled predecessor supervisor run and the unmatched keeper exit are "
                                                  "included in PREDECESSOR_SETTLED_CPU_US",
}
CLAUSE_QUOTE = "Old records are evidence only; they cannot satisfy new coverage."
CLAUSE_CONTEXT = "Resume identity includes new checkpoint hash, exact cell-table hash, backend"
CLAUSE = {
    "id": "COVER_LEDGER_SUCCESSOR_OLD_RECORDS_EVIDENCE_ONLY",
    "source_path": CLAUSE_SOURCE,
    "source_sha256": REPO_PINS[CLAUSE_SOURCE],
    "quote": CLAUSE_QUOTE,
    "quote_line": 215,
    "context": CLAUSE_CONTEXT,
    "context_line": 213,
    "finding": "NOT_PROHIBITIVE",
    "reasons": {
        "R1_old_records_do_not_satisfy_successor_ledger_coverage":
            "the successor ledger universe is exactly 128-325; cells 0-127 are not rows in it and any successor attempt on "
            "them is refused, so no old record satisfies the new ledger's coverage",
        "R2_old_records_remain_predecessor_authorized":
            "the old records satisfy only the coverage of their own predecessor authorization and ledger, which admitted "
            "them before the drift; they are not re-authorized here",
        "R3_no_resume_or_import_transition":
            "there is no resume record, no import transition and no predecessor ledger or reaper row read into the "
            "successor; the clause governs resume identity and nothing is resumed",
        "R4_successor_ledger_covers_only_128_325":
            "every successor cell, including 318 and 323, is produced by a fresh attempt under the successor's own "
            "authorization-born genesis",
        "R5_final_result_is_explicitly_governed_disjoint_union":
            "the final scientific result is the explicit, hash-bound, pre-launch disjoint union approved here, never a "
            "silent carry-over and never a claim that the predecessor ledger completed",
        "R6_composite_k4_attestation_is_new_additive_consumer_path":
            "the composite K4 attestation is a new additive consumer path approved by this countersignature; the "
            "predecessor sanctioned consumer path is unchanged for the predecessor ledger",
    },
    "purpose_preserved": "cell table, producer identity (including backend-library hashes) and runtime contract are "
                         "unchanged; the frozen drift rule requires requalification and a new checkpoint, not recomputation",
}
OTHER_PROVISIONS = {
    "predecessor_drift_rule": {
        "source_path": f"{G.SUCC_REL}/config/PROVENANCE_CHECKPOINT.json", "source_sha256": G.EXPECTED["checkpoint_sha256"],
        "finding": "SATISFIED: a glibc change requires requalification (Q6 PASS) and a new checkpoint (the future successor "
                   "checkpoint); it does not require recomputation"},
    "predecessor_sanctioned_consumer_path": {
        "source_path": f"{G.SUCC_REL}/code/prov_integrity.py", "source_sha256": REPO_PINS[f"{G.SUCC_REL}/code/prov_integrity.py"],
        "finding": "UNCHANGED_FOR_THE_PREDECESSOR: INTEGRITY_READY_FOR_ADJUDICATION requires a COMPLETE ledger, so the "
                   "predecessor ledger alone is never disposition-bearing; composite consumption of its 128 pairs is a "
                   "separate additive path allowed only under conditions (b) and (c)"},
    "k4_assembly_checkpoint": {
        "source_path": f"{LP}/p5y_k2k5_postk1_audit/config/K4_ASSEMBLY_CHECKPOINT.json",
        "source_sha256": REPO_PINS[f"{LP}/p5y_k2k5_postk1_audit/config/K4_ASSEMBLY_CHECKPOINT.json"],
        "finding": "NOT_PROHIBITIVE: integrity.CUSUM and k4_assembly.check_cusum_attestation require the attestation schema, "
                   "cells_verified == 326, all scientific hashes verified, one producer identity and a producer checkpoint "
                   "sha256; no clause requires one physical ledger"},
    "ps1_generation_transition": {
        "source_path": f"{LP}/p5y_k1_ps1_portable_recovery/config/GENERATION_TRANSITION.json",
        "source_sha256": REPO_PINS[f"{LP}/p5y_k1_ps1_portable_recovery/config/GENERATION_TRANSITION.json"],
        "finding": "PRECEDENT_FOR_A_PERMANENTLY_AUTHORITATIVE_STOP_ONLY: it carried no scientific result "
                   "(historical_results_affected NONE); the absence of a scientific carry-over precedent is not a blocker "
                   "because this rule is explicit, frozen before the Q6 result, result-agnostic and independently reviewed"},
}
CONDITIONS = {
    "a": "The successor checkpoint and launch preflight must enforce every binding in SUCCESSOR_CHECKPOINT_SPEC.md (sha256 "
         + NS_PINS["SUCCESSOR_CHECKPOINT_SPEC.md"] + "), including the exact host and runtime identity (every fact of "
         "REQUALIFICATION_PROTOCOL.json host, all 11 system-library hashes, the producer identity and runtime contract), the "
         "containment POST_STATE, and the production universe exactly 128-325; any missing or differing binding refuses "
         "the launch.",
    "b": "The future composite audit must run the frozen prov_integrity.audit unchanged on the predecessor ledger and may "
         "tolerate exactly two predecessor audit issues: " + STOP_ISSUE + ", only for the bound HOST_DRIFT stop, and "
         "D_unsettled_supervisor_runs, only for " + UNSETTLED_RUN + ". Any other predecessor audit issue (including any "
         "A_, B_, C_ or D_open_attempts issue) must fail closed.",
    "c": "The future K4 composite attestation must use the successor checkpoint sha256 as producer_checkpoint_sha256, while "
         "the successor checkpoint itself binds the predecessor checkpoint " + G.EXPECTED["checkpoint_sha256"] + ". Both "
         "provenance halves (each ledger state sha256, genesis entry sha256, authorization block and verified pairs) must "
         "be explicitly disclosed, and no record enters K4 unless its pair verified.",
    "d": "This countersignature is NECESSARY BUT NOT SUFFICIENT for production launch. Despite the frozen verdict label "
         + G.COUNTERSIGN_VERDICT + ", CARRYOVER_AUTHORIZED = YES but PRODUCTION_LAUNCH_AUTHORIZED = NO until a valid "
         "successor checkpoint, a successor run authorization and the successor launch preflight all exist and pass.",
    "e": "Any reboot (a boot id different from the one bound at the successor checkpoint), provider maintenance, or host or "
         "runtime identity drift before or during successor production must fail closed: the launch is refused or "
         "admissions stop under the successor host guard.",
}
CONDITION_TOKENS = {
    "a": ("SUCCESSOR_CHECKPOINT_SPEC.md", "launch preflight", "host and runtime identity", "128-325"),
    "b": ("prov_integrity.audit unchanged", STOP_ISSUE, "D_unsettled_supervisor_runs", UNSETTLED_RUN, "must fail closed"),
    "c": ("producer_checkpoint_sha256", "successor checkpoint", G.EXPECTED["checkpoint_sha256"], "provenance halves"),
    "d": ("NECESSARY BUT NOT SUFFICIENT", "CARRYOVER_AUTHORIZED = YES", "PRODUCTION_LAUNCH_AUTHORIZED = NO",
          "successor checkpoint", "run authorization", "launch preflight"),
    "e": ("reboot", "provider maintenance", "drift", "must fail closed"),
}
HOST_KEYS = ("host_name", "machine_id_sha256", "cpu_model", "logical_cpus", "physical_cores", "smt_groups", "kernel_release",
             "libc_path", "libc_sha256", "glibc_package_version", "system_libraries_sha256", "packages")
APT_UNITS = {"apt-daily.timer": "disabled", "apt-daily-upgrade.timer": "disabled", "apt-daily.service": "masked",
             "apt-daily-upgrade.service": "masked"}
PHASE_A_ITEMS = ("01_proposal_manifest_verifies", "02_predecessor_binding_verifies", "03_q6_result_verifies_clean_checkout",
                 "04_q6_result_rebuilds_byte_for_byte", "05_run_logs_present_and_bound", "06_q6_tests_11_of_11",
                 "07_proposal_tests_24_of_24", "08_protected_trees_unchanged", "09_origin_main_unchanged",
                 "10_old_128_carryover_admissible")


def _sha(p) -> str:
    return G.sha256_file(p)


def _json(p):
    return json.loads(Path(p).read_bytes())


def record_envelope_digest(binding: dict) -> str:
    """sha256 over 'sha256  relpath' lines of the 128 records and 128 envelopes, sorted by path bytes (sha256sum format)."""
    rows = []
    for c in binding["cells"]:
        rows += [(c["record"], c["record_sha256_file"]), (c["envelope"], c["envelope_sha256_file"])]
    rows.sort(key=lambda r: r[0].encode())
    return G.sha256_bytes("".join(f"{h}  {p}\n" for p, h in rows).encode())


def build_countersignature(ns=G.NS, repo=G.REPO, *, signing) -> dict:
    """Deterministic in the committed tree and the signing section."""
    ns, repo = Path(ns), Path(repo)
    binding = _json(ns / "config/PREDECESSOR_BINDING.json")
    rq = _json(ns / "config/REQUALIFICATION_PROTOCOL.json")
    q6 = _json(ns / R.RESULT_REL)
    post = _json(ns / "evidence/containment/POST_STATE.json")
    pred, acc, audit = binding["predecessor"], binding["accounting"], binding["integrity"]["frozen_audit"]
    s = signing if isinstance(signing, dict) else {}
    labels = ("318A", "318B", "323A", "323B")
    return {
        "schema": G.COUNTERSIGN_SCHEMA, "verdict": G.COUNTERSIGN_VERDICT, "synthetic": False,
        "proposal_sha256": _sha(ns / G.PROPOSAL), "q6_result_sha256": _sha(ns / R.RESULT_REL),
        "reviewer": s.get("reviewer"),
        "reviewer_independent_of_authoring_session": s.get("reviewer_independent_of_authoring_session"),
        "signed_utc": s.get("signed_utc"), "branch": BRANCH, "commits": COMMITS,
        "authorizations": AUTHORIZATIONS, "launch_semantics": LAUNCH_SEMANTICS, "approvals": APPROVALS,
        "partition": PARTITION,
        "cpu_continuity": {**CPU, "statements": CPU_STATEMENTS,
                           "predecessor_settlement_components_usec": {
                               "committed_in_ledger": acc["committed_total_usec"],
                               "supervisor_run_settlement_REAPER_RUSAGE": acc["settlement_extra_usec"],
                               "unmatched_keeper_exit_overhead": acc["unmatched_overhead_usec"]},
                           "qualification_cpu": {
                               "total_cpu_seconds": q6["qualification_cpu_accounting"]["total_cpu_seconds"],
                               "c_max_cpu_seconds": q6["qualification_cpu_accounting"]["c_max_cpu_seconds"],
                               "counted_against_campaign_cap": False, "disclosed": True}},
        "opposing_clause_adjudication": CLAUSE, "other_frozen_provisions": OTHER_PROVISIONS, "conditions": CONDITIONS,
        "predecessor": {
            "binding_sha256": _sha(ns / "config/PREDECESSOR_BINDING.json"),
            "checkpoint_sha256": pred["checkpoint_sha256"],
            "freeze_record_sha256": _sha(repo / f"{G.SUCC_REL}/config/FREEZE_RECORD.json"),
            "authorization": pred["production_authorization"],
            "active_countersignature_sha256": G.EXPECTED["countersignature_sha256"],
            "revoked_countersignature_sha256": REVOKED_COUNTERSIGNATURE,
            "ledger_schema": pred["ledger_schema"], "runtime_root": pred["runtime_root"],
            "disposition": pred["disposition"], "stop": pred["stop"], "cell_status_counts": pred["cell_status_counts"],
            "files_sha256": binding["files"], "ledger_state_sha256": binding["ledger_state_sha256"],
            "genesis_entry_sha256": binding["journal"]["genesis_entry_sha256"],
            "last_entry_sha256": binding["journal"]["last_entry_sha256"], "journal_entries": binding["journal"]["entries"],
            "cells_digest_sha256": binding["cells_digest_sha256"],
            "carryover_cells": [min(c["cell"] for c in binding["cells"]), max(c["cell"] for c in binding["cells"])],
            "carryover_pairs": len(binding["cells"]),
            "frozen_audit": {k: audit[k] for k in ("domain", "sealed", "verified_pairs", "pairs_sha256", "issue_keys",
                                                   "disposition", "complete", "INTEGRITY_READY_FOR_ADJUDICATION")},
            "full_seal_reverified_cells": binding["integrity"]["full_seal_reverified_cells"],
            "unsettled_supervisor_runs": sorted(r for r, x in acc["supervisor_runs"].items() if not x.get("settled")),
            "record_envelope_digest_sha256": record_envelope_digest(binding),
            "record_envelope_digest_definition": "sha256 over 'sha256  relpath' lines (sha256sum format) of the 128 record "
                                                 "and 128 envelope files, sorted by path bytes",
            "drift": binding["drift"], "host_clock": binding["host_clock"]},
        "q6": {
            "result_sha256": _sha(ns / R.RESULT_REL),
            **{k: q6[k] for k in ("Q6_FINAL", "CARRYOVER_ROUTE", "Q6_ORIGINAL_GATES", "Q6_SCIENTIFIC_HASH_IDENTITY",
                                  "Q6_CERTIFICATE_HASH_IDENTITY")},
            "scientific_content_hash": {c: q6["cells"][c]["A"]["scientific_content_hash"] for c in ("318", "323")},
            "certificates_per_cell": {c: len(q6["cells"][c]["A"]["certificate_hashes"]) for c in ("318", "323")},
            "record_sha256": {k: q6["runs"][k]["record_sha256"] for k in labels},
            "run_log_sha256": {k: q6["runs"][k]["run_log_sha256"] for k in labels},
            "libc_sha256": q6["libc_sha256"], "glibc_package_version": q6["glibc_package_version"]},
        "host": {k: rq["host"][k] for k in HOST_KEYS},
        "producer": rq["producer"],
        "containment": {
            **{n: _sha(ns / f"evidence/containment/{n}.json") for n in ("PRE_STATE", "POST_STATE", "POST_RUN_STATE")},
            "holds": post["holds"], "apt_units": {u: post["units"][u]["enabled"] for u in APT_UNITS},
            "restore_rule": "HOST_CONTAINMENT_PLAN.md section 3, only after the successor campaign is COMPLETE or drained"},
        "record_sha256": _sha(ns / RECORD_REL),
        "bound_files_sha256": {rel: _sha(ns / rel) for rel in NS_BOUND},
        "repo_objects_sha256": {rel: _sha(repo / rel) for rel in REPO_PINS},
        "protected_trees": PROTECTED_TREES,
        "signing": s,
    }


# ====================================================================== checks
def check_structure(cs: dict) -> list[str]:
    p = []
    if cs.get("schema") != G.COUNTERSIGN_SCHEMA or cs.get("verdict") != G.COUNTERSIGN_VERDICT or cs.get("synthetic") is not False:
        p.append("COUNTERSIGNATURE_SCHEMA: schema, verdict or synthetic flag")
    auth = cs.get("authorizations") if isinstance(cs.get("authorizations"), dict) else {}
    if auth.get("PRODUCTION_LAUNCH_AUTHORIZED") is not False:
        p.append("AUTHORIZATIONS: a countersignature can never authorize production launch")
    if auth.get("CARRYOVER_AUTHORIZED") is not True:
        p.append("AUTHORIZATIONS: carry-over is not recorded as authorized")
    if auth != AUTHORIZATIONS:
        p.append("AUTHORIZATIONS: differ from the approved authorization state")
    if cs.get("launch_semantics") != LAUNCH_SEMANTICS:
        p.append("LAUNCH_SEMANTICS: necessary-but-not-sufficient semantics missing or altered")
    ap = cs.get("approvals") if isinstance(cs.get("approvals"), dict) else {}
    for k, text in APPROVALS.items():
        if k not in ap:
            p.append(f"APPROVAL_MISSING: {k}")
        elif ap[k] != text:
            p.append(f"APPROVAL_ALTERED: {k}")
    part = cs.get("partition") if isinstance(cs.get("partition"), dict) else {}
    if part != PARTITION:
        p.append("PARTITION: differs from OLD_CARRYOVER 0-127 / NEW_SUCCESSOR 128-325")
    try:
        old = range(part["OLD_CARRYOVER"][0], part["OLD_CARRYOVER"][1] + 1)
        new = range(part["NEW_SUCCESSOR"][0], part["NEW_SUCCESSOR"][1] + 1)
        p += [f"PARTITION: {x}" for x in G.check_partition(old, new) + G.check_no_recomputation(new)]
    except (KeyError, TypeError, IndexError):
        p.append("PARTITION: unreadable")
    cpu = cs.get("cpu_continuity") if isinstance(cs.get("cpu_continuity"), dict) else {}
    for k, v in CPU.items():
        if cpu.get(k) != v:
            p.append(f"CPU: {k} != {v}")
    if cpu.get("SUCCESSOR_RESIDUAL_CAP_US") != (cpu.get("ABSOLUTE_CAP_US") or 0) - (cpu.get("PREDECESSOR_SETTLED_CPU_US") or 0):
        p.append("CPU: residual != absolute - predecessor settled")
    if cpu.get("SUCCESSOR_RESIDUAL_CAP_US") == cpu.get("ABSOLUTE_CAP_US"):
        p.append("CPU: CAP_RESET_FORBIDDEN")
    if cpu.get("statements") != CPU_STATEMENTS:
        p.append("CPU: continuity statements missing or altered")
    conds = cs.get("conditions") if isinstance(cs.get("conditions"), dict) else {}
    for k, text in CONDITIONS.items():
        got = conds.get(k)
        if not isinstance(got, str) or not got.strip():
            p.append(f"CONDITION_MISSING: ({k})")
            continue
        missing = [t for t in CONDITION_TOKENS[k] if t not in got]
        if missing:
            p.append(f"CONDITION_WEAKENED: ({k}) lacks {missing}")
        if got != text:
            p.append(f"CONDITION_ALTERED: ({k})")
    cl = cs.get("opposing_clause_adjudication")
    if not isinstance(cl, dict):
        p.append("CLAUSE_ADJUDICATION_MISSING: the cover-ledger clause '" + CLAUSE_QUOTE + "' is not adjudicated")
    else:
        if cl.get("quote") != CLAUSE_QUOTE or cl.get("source_path") != CLAUSE_SOURCE:
            p.append("CLAUSE_ADJUDICATION: quote or source not identified exactly")
        if cl.get("finding") != "NOT_PROHIBITIVE":
            p.append("CLAUSE_ADJUDICATION: finding is not NOT_PROHIBITIVE")
        reasons = cl.get("reasons") if isinstance(cl.get("reasons"), dict) else {}
        for k in CLAUSE["reasons"]:
            if not isinstance(reasons.get(k), str) or not reasons[k].strip():
                p.append(f"CLAUSE_ADJUDICATION: reason missing {k}")
        if cl != CLAUSE:
            p.append("CLAUSE_ADJUDICATION_ALTERED")
    return p


def check_pins(ns, repo) -> list[str]:
    p = []
    for base, pins in ((Path(ns), NS_PINS), (Path(repo), REPO_PINS)):
        for rel, want in pins.items():
            f = base / rel
            if not f.is_file():
                p.append(f"BOUND_HASH: {rel} missing")
            elif _sha(f) != want:
                p.append(f"BOUND_HASH: {rel} changed")
    return p


def check_clause_source(repo) -> list[str]:
    try:
        lines = (Path(repo) / CLAUSE_SOURCE).read_text().splitlines()
    except OSError:
        return ["CLAUSE_SOURCE: unreadable"]
    ok = (len(lines) >= CLAUSE["quote_line"] and CLAUSE_QUOTE in lines[CLAUSE["quote_line"] - 1]
          and CLAUSE_CONTEXT in lines[CLAUSE["context_line"] - 1])
    return [] if ok else ["CLAUSE_SOURCE: the adjudicated clause is not at its bound location"]


def git_state(repo) -> dict:
    def run(*args):
        return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, timeout=60)
    if run("rev-parse", "--is-inside-work-tree").stdout.strip() != "true":
        raise ValueError("not a git checkout")
    trees = {}
    for rel in PROTECTED_TREES:
        r = run("rev-parse", f"HEAD:{rel}")
        trees[rel] = r.stdout.strip() if r.returncode == 0 else None
    ancestors = {k: run("merge-base", "--is-ancestor", c, "HEAD").returncode == 0 for k, c in COMMITS.items()}
    st = run("status", "--porcelain", "--", *PROTECTED_TREES)
    return {"trees": trees, "ancestors": ancestors, "dirty": st.stdout.splitlines() if st.returncode == 0 else None}


def check_git(reader, repo) -> list[str]:
    try:
        st = reader(repo)
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        return [f"PROTECTED_TREES_UNVERIFIABLE: {type(exc).__name__}: {exc}"]
    p = []
    trees = st.get("trees") or {}
    for rel, want in PROTECTED_TREES.items():
        if trees.get(rel) != want:
            p.append(f"PROTECTED_TREE_CHANGED: {rel}")
    for k in COMMITS:
        if (st.get("ancestors") or {}).get(k) is not True:
            p.append(f"COMMIT_NOT_IN_HISTORY: {k}")
    if st.get("dirty") is None:
        p.append("PROTECTED_TREES_UNVERIFIABLE: status")
    elif st["dirty"]:
        p.append(f"PROTECTED_TREE_DIRTY: {st['dirty'][:5]}")
    return p


def check_signing(signing, ns) -> list[str]:
    s = signing if isinstance(signing, dict) else {}
    p = []
    if not isinstance(s.get("reviewer"), str) or not s["reviewer"].strip():
        p.append("SIGNING: reviewer missing")
    if s.get("reviewer_independent_of_authoring_session") is not True:
        p.append("SIGNING: reviewer not independent of the authoring session")
    disc = s.get("independence_disclosure")
    if not isinstance(disc, str) or not all(c in disc for c in (COMMITS["proposal_freeze_commit"], COMMITS["q6_result_commit"],
                                                                   COMMITS["q6_evidence_repair_commit"])):
        p.append("SIGNING: independence disclosure must name the proposal, Q6 and evidence-repair commits")
    if not isinstance(s.get("signed_utc"), str) or not UTC_RE.match(s["signed_utc"]):
        p.append("SIGNING: signed_utc")
    if s.get("branch") != BRANCH or s.get("branch_tip_at_signing") != COMMITS["q6_evidence_repair_commit"]:
        p.append("SIGNING: branch or branch tip at signing")
    pa = s.get("phase_a_reverification") if isinstance(s.get("phase_a_reverification"), dict) else {}
    for k in PHASE_A_ITEMS:
        if pa.get(k) not in ("PASS", "YES"):
            p.append(f"SIGNING: phase A item {k} not PASS")
    try:
        binding = _json(Path(ns) / "config/PREDECESSOR_BINDING.json")
        host = _json(Path(ns) / "config/REQUALIFICATION_PROTOCOL.json")["host"]
        post = _json(Path(ns) / "evidence/containment/POST_STATE.json")
        want = {"host_name": host["host_name"], "boot_id": binding["host_clock"]["boot_id"],
                "kernel_release": host["kernel_release"], "libc_sha256": host["libc_sha256"],
                "predecessor_files_sha256": binding["files"], "record_envelope_digest_sha256": record_envelope_digest(binding),
                "files_modified_after_final_seal": 0, "holds": post["holds"], "apt_units": APT_UNITS,
                "certifier_or_ledger_processes": 0, "successor_runtime_root_present": False}
    except (OSError, ValueError, KeyError, TypeError) as exc:
        return p + [f"SIGNING: bound state unreadable: {type(exc).__name__}"]
    live = s.get("live_host_observation") if isinstance(s.get("live_host_observation"), dict) else {}
    if not isinstance(live.get("observed_utc"), str) or not UTC_RE.match(live["observed_utc"]):
        p.append("SIGNING: live observation time")
    for k, v in want.items():
        if live.get(k) != v:
            p.append(f"SIGNING: live observation {k} differs from the bound state")
    return p


def launch_readiness_with_countersignature_only(ns, cs: dict, raw: bytes) -> dict:
    ns = Path(ns)
    q6_raw = (ns / R.RESULT_REL).read_bytes()
    q6 = G.evaluate_q6(json.loads(q6_raw), _json(ns / "config/Q6_REFERENCE.json"), result_sha256=G.sha256_bytes(q6_raw))
    return G.launch_readiness(proposal_problems=[], proposal_sha256=_sha(ns / G.PROPOSAL), q6=q6, countersignature=cs,
                              countersignature_sha256=G.sha256_bytes(raw), checkpoint=None)


def verify_countersignature(ns=G.NS, repo=G.REPO, *, git_reader=None) -> list[str]:
    ns, repo = Path(ns), Path(repo)
    try:
        raw = (ns / CS_REL).read_bytes()
        cs = json.loads(raw)
    except (OSError, ValueError) as exc:
        return [f"COUNTERSIGNATURE_UNREADABLE: {type(exc).__name__}: {exc}"]
    if not isinstance(cs, dict):
        return ["COUNTERSIGNATURE_SCHEMA: not an object"]
    p = []
    try:
        if (ns / CS_HASH_REL).read_text().strip() != G.sha256_bytes(raw):
            p.append("COUNTERSIGNATURE_HASH_FILE: differs from the countersignature sha256")
    except OSError:
        p.append("COUNTERSIGNATURE_HASH_FILE: missing")
    p += check_structure(cs)
    p += check_pins(ns, repo)
    p += check_clause_source(repo)
    p += [f"Q6: {x}" for x in R.verify_result(ns, repo)]
    p += check_git(git_reader or git_state, repo)
    p += check_signing(cs.get("signing"), ns)
    try:
        if raw != G.dump(build_countersignature(ns, repo, signing=cs.get("signing"))):
            p.append("COUNTERSIGNATURE_DOES_NOT_REBUILD: a bound object or the countersignature changed")
    except (OSError, ValueError, KeyError, TypeError, IndexError) as exc:
        p.append(f"COUNTERSIGNATURE_DOES_NOT_REBUILD: {type(exc).__name__}: {exc}")
    try:
        rep = launch_readiness_with_countersignature_only(ns, cs, raw)
        if rep["state"] != "NOT_READY":
            p.append("LAUNCH_READINESS: a countersignature alone must never make the successor launch-ready")
        if rep["problems"] != ["SUCCESSOR_CHECKPOINT_ABSENT"]:
            p.append(f"LAUNCH_READINESS: frozen launch_readiness does not accept this countersignature: {rep['problems'][:6]}")
    except (OSError, ValueError, KeyError, TypeError) as exc:
        p.append(f"LAUNCH_READINESS: {type(exc).__name__}: {exc}")
    return p


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="CUSUM Aux5 new-glibc carry-over countersignature (governance only)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build")
    b.add_argument("--signing", required=True)
    sub.add_parser("verify")
    a = ap.parse_args(argv)
    if a.cmd == "build":
        if (G.NS / CS_REL).exists() or (G.NS / CS_HASH_REL).exists():
            print(json.dumps({"BUILD_REFUSED": "a countersignature already exists; it is never overwritten"}, indent=1))
            return 30
        signing = json.loads(Path(a.signing).read_bytes())
        signing.setdefault("signed_utc", datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))
        pre = (check_signing(signing, G.NS) + check_pins(G.NS, G.REPO) + check_clause_source(G.REPO)
               + [f"Q6: {x}" for x in R.verify_result()] + check_git(git_state, G.REPO))
        data = G.dump(build_countersignature(signing=signing))
        pre += check_structure(json.loads(data))
        if pre:
            print(json.dumps({"BUILD_REFUSED": pre}, indent=1))
            return 30
        (G.NS / CS_REL).write_bytes(data)
        (G.NS / CS_HASH_REL).write_text(G.sha256_bytes(data) + "\n")
        problems = verify_countersignature()
        print(json.dumps({"COUNTERSIGNATURE_SHA256": G.sha256_bytes(data), "COUNTERSIGNATURE_VALID": not problems,
                          "problems": problems}, indent=1))
        return 0 if not problems else 30
    problems = verify_countersignature()
    print(json.dumps({"COUNTERSIGNATURE_VALID": not problems, "CARRYOVER_AUTHORIZED": not problems,
                      "PRODUCTION_LAUNCH_AUTHORIZED": False, "problems": problems}, indent=1))
    return 0 if not problems else 30


if __name__ == "__main__":
    raise SystemExit(main())
