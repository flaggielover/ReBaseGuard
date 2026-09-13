"""Build the FROZEN CUSUM Aux5 production checkpoint. NON-CERTIFYING.

Every value is read from a frozen artifact and cross-checked; the build refuses if any bound fact disagrees.
Nothing here changes a scientific definition: the producer, runtime contract, universe, geometry, precision,
record schema and scientific-hash semantics are the frozen Aux5/Aux4/K1 objects, bound by hash.

  python make_production_checkpoint.py probe-host --out ../config/HOST_IDENTITY.json   (on rebaseguard-vultr-02)
  python make_production_checkpoint.py build     -> ../config/PRODUCTION_CHECKPOINT.json and PRODUCTION_CHECKPOINT_HASH
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import time
from fractions import Fraction as F
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import prod_cells                                                                         # noqa: E402
import prod_ledger as L                                                                   # noqa: E402
import prod_sealer as SEAL                                                                # noqa: E402
from prod_common import (AUX4_NS, AUX5_NS, BOUND_HOST_FACTS, CHECKPOINT, CHECKPOINT_HASH,  # noqa: E402
                         GUARD_HOST_FACTS, K4_NS, NS, ROOT, SPEC_NS, Refusal, atomic_write_bytes, atomic_write_json,
                         host_facts, rel, sha256_bytes, sha256_file)
from prod_spec import (CHECKPOINT_SCHEMA, PRODUCTION_RUNTIME_ROOT, QUALIFICATION_RECORDS,   # noqa: E402
                       USEC_PER_CPU_H, manifest_identity)

AUX5_FREEZE_COMMIT = "d31ea4edd5a96be5c9ac0a7d4acea2a5a3c5e563"
AUX5_QUALIFICATION_COMMIT = "09aa94c9befb47ab6cc6336fd2b4ece15a2f6a1a"
FROZEN_IDENTITY = {
    "manifest_file_sha256": "611bd0a9f356b0e7f5e63da60567ac1afa9e69fc1f8c464c7e5b89aeedbd2b9f",
    "producer_manifest_hash": "b55a2da1fea0c7ee889f8da6a4b893c12d3ef24e2bc02d19bd5488187fd30fd9",
    "runtime_contract_hash": "bc75c9ea7cd5f9406a0509bb0a161aa2c013f80427d1035197989e3d202c845a",
    "producer_identity_hash": "3692d0feeaef71365798cd99399fdb6d744573f38d59dba5cfe2e99294f0ae19",
}
PROTOCOL_SHA256 = "81e28577fdb0ebf671e0ea99799245e6d02a58015cf7c8e7a229f0d4f26b1d94"
BOUND_HOST = "rebaseguard-vultr-02"
CHECKOUT_PATH = "/root/work/postk1-aux5"
CORES = [0, 2, 4, 6]
N_CELLS, WORKERS = 326, 4
RECORD_IDENTITY_KEYS = ("producer_manifest_hash", "runtime_contract_hash", "producer_identity_hash",
                        "implementation_hash_kind", "producer_manifest_path", "producer_manifest_schema",
                        "producer_manifest_version", "campaign")
WORKER_ENV = {"PATH": "/usr/bin:/bin", "HOME": "/root", "LANG": "C.UTF-8", "OMP_NUM_THREADS": "1",
              "OPENBLAS_NUM_THREADS": "1", "MKL_NUM_THREADS": "1", "NUMEXPR_NUM_THREADS": "1",
              "K1_THREADS_PINNED": "1", "PYTHONDONTWRITEBYTECODE": "1"}
HOST_IDENTITY = NS / "config/HOST_IDENTITY.json"
K4_ATTESTATION = NS / "config/K4_INPUT_SCHEMA_ATTESTATION.json"


def need(cond: bool, what: str) -> None:
    if not cond:
        raise Refusal("CHECKPOINT_BUILD_REFUSED", what)


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def bound_source_paths() -> list[Path]:
    own = sorted(NS.glob("code/*.py")) + sorted(NS.glob("tests/*.py")) + [HOST_IDENTITY, K4_ATTESTATION]
    aux5 = [AUX5_NS / x for x in (
        "code/qualify5.py", "code/cap_formula.py", "code/analyze_qualification.py", "code/run_qualification.sh",
        "manifests/producer_manifest_v3.json", "config/FREEZE_RECORD.json", "config/QUALIFICATION_PROTOCOL.json",
        "config/COST_CAP_FORMULA.json", "config/HOST_QUALIFICATION.json", "config/GENERATION_REPORT.json",
        "evidence/qualification_r1/QUALIFICATION_RESULT.json")] + [QUALIFICATION_RECORDS[k] for k in sorted(QUALIFICATION_RECORDS)]
    aux4 = [AUX4_NS / "code" / n for n in sorted(SEAL.HASH_MODULE_SHA256)]
    k4 = [K4_NS / "config/K4_ASSEMBLY_CHECKPOINT.json", K4_NS / "config/K4_ASSEMBLY_CHECKPOINT_HASH",
          K4_NS / "code/k4_assembly.py"]
    spec = [ROOT / prod_cells.CELLS_REL, SPEC_NS / "config/checkpoint.json"]
    return own + aux5 + aux4 + k4 + spec


def build() -> dict:
    # ---------------------------------------------------------- producer
    manifest_path = AUX5_NS / "manifests/producer_manifest_v3.json"
    need(sha256_file(manifest_path) == FROZEN_IDENTITY["manifest_file_sha256"], "manifest v3 file sha256")
    manifest = json.loads(manifest_path.read_text())
    ident = manifest_identity(manifest)
    for k, v in ident.items():
        need(v == FROZEN_IDENTITY[k], f"{k} recomputes to {v}")
    runtime = manifest["runtime"]
    aux5_freeze = json.loads((AUX5_NS / "config/FREEZE_RECORD.json").read_text())
    need(aux5_freeze["identity"] == {k: FROZEN_IDENTITY[k] for k in ident}, "Aux5 FREEZE_RECORD identity")
    certifier = AUX5_NS / "code/qualify5.py"
    need(manifest["files"][rel(certifier)] == sha256_file(certifier), "certifier bytes vs manifest")

    # ---------------------------------------------------------- qualification
    qres_path = AUX5_NS / "evidence/qualification_r1/QUALIFICATION_RESULT.json"
    qres = json.loads(qres_path.read_text())
    protocol_path = AUX5_NS / "config/QUALIFICATION_PROTOCOL.json"
    need(sha256_file(protocol_path) == PROTOCOL_SHA256 == qres["protocol_sha256"], "qualification protocol sha256")
    need(qres["QUALIFICATION"] == "PASS" and qres["CUSUM_DETERMINISM"] == "PASS" and all(qres["criteria"].values()),
         "qualification verdict")
    need(qres["production"] is False and qres["result_bearing"] is False
         and qres["transition_to_production_authorized"] is False, "qualification is non-production")
    need(qres["manifest_identity"] == {k: FROZEN_IDENTITY[k] for k in ident}, "qualification manifest identity")
    records = {k: json.loads(p.read_text()) for k, p in sorted(QUALIFICATION_RECORDS.items())}
    identity = {k: records["318A"][k] for k in RECORD_IDENTITY_KEYS}
    for key, rec in records.items():
        need({k: rec[k] for k in RECORD_IDENTITY_KEYS} == identity, f"record identity of {key}")
        need(rec["producer"]["runtime"] == runtime, f"record {key} runtime equals the manifest runtime")
    for k in ident:
        need(identity[k] == ident[k], f"record {k} equals the manifest identity")
    cpu = {k: r["cpu_seconds_including_dependencies"] for k, r in records.items()}
    c_max = max(cpu.values())
    need(c_max == qres["c_max_cpu_seconds"], "c_max recomputed from the records")

    # ---------------------------------------------------------- cost cap
    formula_path = AUX5_NS / "config/COST_CAP_FORMULA.json"
    formula = json.loads(formula_path.read_text())
    need(formula["status"] == "FROZEN_PRE_RESULT", "cost-cap formula frozen")
    cap_mod = load_module("aux5_cap_formula", AUX5_NS / "code/cap_formula.py")
    derived = cap_mod.cap(c_max_cpu_seconds=repr(c_max), n_cells=N_CELLS, workers=WORKERS)
    need(derived["exact"]["CAP"] == "300" and derived["CAP_cpu_h"] == 300, f"CAP derives to {derived['exact']['CAP']}")
    need(derived["exact"] == qres["derived_cap"]["exact"], "derived cap equals the qualification result")
    reservation = F(derived["exact"]["R"]) * USEC_PER_CPU_H
    need(reservation.denominator == 1, "reservation is an integer number of microseconds")

    # ---------------------------------------------------------- host
    host_doc = json.loads(HOST_IDENTITY.read_text())
    facts = host_doc["facts"]
    hq = json.loads((AUX5_NS / "config/HOST_QUALIFICATION.json").read_text())
    obs = hq["observed_2026-09-13"]
    need(facts["host_name"] == BOUND_HOST == runtime["host_name"] == hq["bound_host"], "host name")
    need(facts["kernel_release"] == obs["kernel"] and facts["cpu_model"] == obs["cpu_model"], "kernel / cpu model")
    need(facts["logical_cpus"] == obs["logical_cpus"] and facts["physical_cores"] == obs["physical_cores"] == WORKERS,
         "cpu topology")
    need(facts["smt_groups"] == obs["smt_pairs"], "SMT pairs")
    need([g[0] for g in facts["smt_groups"]] == CORES, "one worker core per physical core, as in qualification")
    need(str(facts["glibc_package_version"]).startswith(runtime["libc"][1] + "-"), "glibc package vs runtime libc")
    need(all(facts.get(k) is not None for k in BOUND_HOST_FACTS), "every bound host fact is present")

    # ---------------------------------------------------------- worker command (the qualification command)
    venv_python = runtime["venv_prefix"] + "/bin/python"
    argv = ["/usr/bin/env", "-i"] + [f"{k}={v}" for k, v in WORKER_ENV.items()] + [
        "/usr/bin/taskset", "-c", "{core}", venv_python, "{root}/" + rel(certifier),
        "--cell", "{cell}", "--bits", "256", "--out", "{out}"]
    launcher = (AUX5_NS / "code/run_qualification.sh").read_text()
    for token in [f"{k}={v}" for k, v in WORKER_ENV.items()] + [f"PY={venv_python}", "--bits 256", "taskset -c",
                                                               "env -i"]:
        need(token in launcher, f"worker command token {token!r} matches the qualification launcher")

    # ---------------------------------------------------------- universe and geometry
    k1spec = load_module("k1_frozen_spec", ROOT / "level4/closure_proofs/p5y_k1_cover_ledger_implementation/code/spec.py")
    need(k1spec.PRODUCTION_BITS == 256 and not k1spec.PRECISION_ESCALATION_ALLOWED
         and not k1spec.DEGREE_ADAPTATION_ALLOWED, "frozen precision rules")
    need(k1spec.TOTAL_UNITS == 17978 and k1spec.COUNTS["CUSUM"] == N_CELLS, "frozen universe")
    cells = prod_cells.cusum_cells()
    cover = prod_cells.cover_facts(cells)
    need(cover["contiguous"] and cover["all_endpoints_exact_non_symbolic"], "cover contiguity")
    k4cp = json.loads((K4_NS / "config/K4_ASSEMBLY_CHECKPOINT.json").read_text())
    need(cover["k4_domain"]["cells"] == 310 and cover["k4_domain"]["last_index"] == 309
         and cover["k4_domain"]["last_right"][0] in k4cp["domain"]["CUSUM"]["cells"], "K4 CUSUM domain")
    need(k4cp["domain"]["CUSUM"]["table_sha256"] == prod_cells.CELLS_SHA256, "K4 domain table")

    # ---------------------------------------------------------- K4
    att = json.loads(K4_ATTESTATION.read_text())
    need(att["K4_CUSUM_INPUT_SCHEMA_ATTESTED"] == "YES" and not att["problems"], "K4 structural attestation")
    k4_sha = sha256_file(K4_NS / "config/K4_ASSEMBLY_CHECKPOINT.json")
    need((K4_NS / "config/K4_ASSEMBLY_CHECKPOINT_HASH").read_text().strip() == k4_sha
         == att["k4_checkpoint"]["checkpoint_sha256"], "K4 checkpoint hash")

    H, S = SEAL.hash_modules()
    q_cpu_total = sum(cpu.values())
    cp = {
        "schema": CHECKPOINT_SCHEMA,
        "status": "FROZEN_PRE_PRODUCTION",
        "campaign_id": "p5y_k1_cusum_aux5_production",
        "frozen_utc": time.strftime("%Y-%m-%d", time.gmtime()),
        "result_bearing": False,
        "production_launched": False,
        "authorization": "This checkpoint makes the 326-cell CUSUM production LAUNCHABLE. It launches nothing. A launch "
                         "is an explicit operator action: prod_entry.py launch --confirm-checkpoint-sha256 <sha256 of "
                         "this file>, after prod_entry.py preflight prints READY.",
        "runtime_root": str(PRODUCTION_RUNTIME_ROOT),
        "checkout_path": CHECKOUT_PATH,
        "producer": {
            "namespace": rel(AUX5_NS), "freeze_commit": AUX5_FREEZE_COMMIT,
            "qualification_commit": AUX5_QUALIFICATION_COMMIT,
            "manifest_path": rel(manifest_path), "manifest_file_sha256": FROZEN_IDENTITY["manifest_file_sha256"],
            "record_identity": identity, "tcb_files": len(manifest["files"]),
            "certifier_path": rel(certifier), "certifier_sha256": sha256_file(certifier),
            "aux5_freeze_record_sha256": sha256_file(AUX5_NS / "config/FREEZE_RECORD.json"),
            "generation_report_sha256": sha256_file(AUX5_NS / "config/GENERATION_REPORT.json"),
            "statement": "The production certifier is the frozen, qualified Aux5 qualify5.py, unmodified and started as "
                         "a separate env -i interpreter; nothing in this namespace is on its certifying path.",
        },
        "runtime_contract": {
            "runtime_contract_hash": ident["runtime_contract_hash"], "schema": runtime["schema"],
            "venv_prefix": runtime["venv_prefix"], "venv_python": venv_python,
            "python_executable": runtime["python_executable"], "cpython_version_full": runtime["cpython_version_full"],
            "numpy_version": runtime["numpy_version"], "python_flint_version": runtime["python_flint_version"],
            "openblas_runtime_corename": runtime["openblas_runtime_corename"],
            "openblas_config": runtime["openblas_config"], "libc": runtime["libc"],
            "backend_libraries": runtime["backend_libraries"], "thread_environment": runtime["thread_environment"],
            "worker_environment": WORKER_ENV,
            "enforced_by": "the certifier's own initial and final gates (manifest_v3.verify + runtime compare) on every "
                           "cell, the entrypoint probe C06, and the seal check that producer.runtime equals this contract",
        },
        "host": {
            "bound_facts": {k: facts[k] for k in BOUND_HOST_FACTS},
            "host_identity_file_sha256": sha256_file(HOST_IDENTITY),
            "host_qualification_sha256": sha256_file(AUX5_NS / "config/HOST_QUALIFICATION.json"),
            "guard_before_every_admission": list(GUARD_HOST_FACTS),
            "drift_rule": "any difference in a bound fact refuses the launch (C04) or halts admissions (HOST_DRIFT); a "
                          "change of host, kernel, glibc bytes or runtime contract requires requalification and a new "
                          "checkpoint (COST_CAP_FORMULA rules)",
            "disclosures": host_doc.get("disclosures", {}),
        },
        "workers": {
            "count": WORKERS, "cores": CORES, "smt_groups": facts["smt_groups"],
            "shape": "one worker per physical core (logical 0,2,4,6), the measured qualification shape",
            "argv_template": argv, "cwd": "{root} = checkout_path",
            "parent_death_signal": "SIGKILL (PR_SET_PDEATHSIG): no worker outlives its supervisor",
            "resume_flag": "--skip-if-current is NOT used: every attempt recomputes; resume is at ledger level",
        },
        "scientific_universe": {
            "k1_spec_namespace": rel(SPEC_NS), "frozen_spec_hashes": k1spec.FROZEN_HASHES,
            "obligation_universe_total": k1spec.TOTAL_UNITS, "detector": "CUSUM", "cells": N_CELLS,
            "k1_spec_production_enabled_constant": k1spec.PRODUCTION_ENABLED,
            "statement": "unchanged. spec.PRODUCTION_ENABLED is a frozen constant of the reviewed K1 certifier lineage "
                         "(every CUSUM certifier since repair1 refuses to run if it is true); production authority is "
                         "conferred by this checkpoint and the sealed ledger, never by the certifier.",
        },
        "geometry": {"cells_table": prod_cells.CELLS_REL, "cells_sha256": prod_cells.CELLS_SHA256,
                     "geometry_digest": prod_cells.geometry_digest(cells), "geometry_fields": list(prod_cells.GEOMETRY_FIELDS),
                     "cover": cover,
                     "m_rho_domain_mapping": "every one of the 326 cells is certified for m in {1,2,3,5} at its frozen "
                                             "(e0, rho) with left = e0 - rho, right = e0 + rho; the K4 domain (0, 2] is "
                                             "the contiguous prefix of cells 0..309"},
        "precision": {"precision_bits": 256, "precision_escalation_allowed": False, "degree_adaptation_allowed": False,
                      "taylor_order": runtime["taylor_order"], "collocation_degree": runtime["collocation_degree"],
                      "collocation_quadrature": runtime["collocation_quadrature"],
                      "subdivision_depth": runtime["subdivision_depth"]},
        "result_schema": {
            "record_schema": SEAL.RECORD_SCHEMA, "auxiliary_schema": H.AUX_SCHEMA,
            "required_top_level": list(SEAL.REQUIRED_TOP_LEVEL), "per_m_keys_exact": list(SEAL.PER_M_KEYS),
            "m_values": list(prod_cells.M_VALUES), "interval_fields": list(SEAL.INTERVALS),
            "obligations_per_cell": SEAL.OBLIGATIONS_PER_CELL,
            "record_path": "attempts/<attempt id>/aux5_CUSUM_<cell>_256.json (read-only once sealed)",
            "synthetic_stamp_refused_in_production": SEAL.SYNTHETIC_STAMP,
            "record_flags_semantics": "the frozen certifier stamps production_run=false, result_bearing=false and "
                                      "scientific_certification_of_full_cover=false as constants inside the scientific "
                                      "hash (identical in qualification and production). Production status is "
                                      "conferred ONLY by a SEALED ledger attempt of this checkpoint; the flags are "
                                      "never read or rewritten.",
            "obligation_statuses": "never read by the ledger; scientific interpretation belongs to adjudication",
        },
        "scientific_hash": {
            "modules_sha256": SEAL.HASH_MODULE_SHA256,
            "semantics": "hash_v2 by EXCLUSION: every leaf not matching INCIDENTAL_PATHS is hashed; unknown fields are "
                         "SCIENTIFIC; canonical JSON, exact rational strings",
            "incidental_paths": list(S.INCIDENTAL_PATHS), "provenance_paths": list(S.PROVENANCE_PATHS),
            "seal_rule": "scientific_content_hash and auxiliary_evidence_hash recompute; audit_record ok; every K4 "
                         "consumed path is not INCIDENTAL",
        },
        "ledger": {
            "schemas": {"ledger": L.LEDGER_SCHEMA, "journal": L.JOURNAL_SCHEMA, "reaper": L.REAPER_SCHEMA,
                        "export": L.EXPORT_SCHEMA},
            "layout": {"ledger.json": "state, atomically replaced", "journal.jsonl": "hash-chained transitions",
                       "reaper.jsonl": "keeper rusage evidence", "campaign.lock": "kernel flock",
                       "DRAIN": "operator drain marker", "attempts/": "one directory per attempt"},
            "cell_states": list(L.CELL_STATES), "attempt_states": list(L.ATTEMPT_STATES),
            "transitions": "PENDING->RESERVED->RUNNING->SEALED | ->PENDING (TORN, RELEASED) | ->FAILED",
            "invariants": ["one scientific cell -> at most one SEALED attempt (DUPLICATE_SEALED_CELL)",
                           "a SEALED cell has no open attempt and is never re-admitted",
                           "committed CPU per bucket == sum of recorded charges (ACCOUNTING_CORRUPT)",
                           "the cap bound at genesis never changes (CAP_CHANGE_FORBIDDEN)",
                           "ledger state == journal head, or exactly one step past it (LEDGER_ROLLBACK_OR_MUTATION)"],
            "atomicity": "validate -> temp file, fsync, os.replace, fsync dir -> append journal line, fsync",
        },
        "lifecycle": {
            "poll_seconds": 5, "heartbeat_seconds": 60, "max_infra_tears_per_cell": L.MAX_INFRA_TEARS_PER_CELL,
            "reservation": "a PENDING cell is RESERVED (durable) before its worker is started, RUNNING (pid, start "
                           "ticks) immediately after; admission in ascending cell index, one per free bound core",
            "sealed_cell_rule": "a record is SEALED only after prod_sealer.verify_record passes and the file is made "
                                "read-only and its directory fsynced; the seal binds record sha256 and scientific hash",
            "torn_attempt_rule": "a worker lost to a signal or an orphaned attempt without a verifying record is TORN "
                                 "(charged, cell back to PENDING, retried); the 3rd infrastructure tear of one cell "
                                 "halts the campaign; partial files are never read",
            "failure_rule": "a nonzero worker exit, an exit 0 without a record, or a record failing the seal check is "
                            "FAILED: charged, never retried, the campaign halts",
            "duplicate_cell_rule": "one flock-holding supervisor per runtime root; op_reserve admits only PENDING cells; "
                                   "op_close refuses a cell owned by another attempt; validate refuses two seals",
            "skip_resume_rule": "on restart sealed cells are re-verified by sha256 and skipped; admission resumes at "
                                "the lowest PENDING index; the ledger is the only resume state",
            "graceful_drain": "SIGTERM/SIGINT to the keeper or supervisor, or the DRAIN marker: no new admission, "
                              "in-flight attempts finish and seal, disposition DRAINED; relaunch requires removing DRAIN",
            "restart_recovery": "a supervisor first reconciles every attempt and run left open by a dead predecessor",
            "crash_reconciliation": "open attempt with a live pid -> refused (LIVE_ORPHAN_WORKER); record present and "
                                    "verifying -> SEALED (recovered); keeper reap with exit != 0 -> FAILED; otherwise "
                                    "TORN (ORPHAN_ATTEMPT); charge = keeper rusage, else tail bound",
            "halt_rules": ["WORKER_REPORTED_FAILURE", "MALFORMED_RESULT", "RETRY_LIMIT", "HOST_DRIFT", "SPAWN_FAILED"],
            "cpu_evidence_hierarchy": ["WAIT4_RUSAGE", "REAPER_RUSAGE", "TAIL_BOUND_NOW", "TAIL_BOUND_REBOOT"],
            "exit_codes": {"COMPLETE": 0, "DRAINED": 10, "HALTED": 20, "REFUSED": 30,
                           "INCOMPLETE_BUDGET_EXHAUSTED": 40},
        },
        "cost_cap": {
            "formula": formula["formula"], "formula_path": rel(formula_path),
            "formula_file_sha256": sha256_file(formula_path),
            "cap_formula_py_sha256": sha256_file(AUX5_NS / "code/cap_formula.py"),
            "c_max_cpu_seconds": repr(c_max), "c_max_source": "max cpu_seconds_including_dependencies over the four "
                                                               "qualification runs (318A)",
            "N": N_CELLS, "W": WORKERS, "derived": derived, "cap_cpu_h": derived["CAP_cpu_h"],
            "cap_usec": derived["CAP_cpu_h"] * USEC_PER_CPU_H,
            "reservation_cpu_h": derived["exact"]["R"], "reservation_usec": int(reservation),
            "invariant": L.INVARIANT,
            "admission_rule": "admit iff 115 * (committed + sum_open max(R, sampled CPU) + R) <= 100 * CAP",
            "accounting_unit": "integer microseconds of CPU, cumulative across every run of this ledger",
            "retry_and_recovery_accounting": "every torn, failed and recovered attempt is charged to its bucket; "
                                             "supervisor, probe and keeper CPU are charged to the supervisor bucket",
            "exhaustion": "a denied admission with nothing in flight records INCOMPLETE_BUDGET_EXHAUSTED (terminal)",
            "never_raised": "the cap is bound into the ledger at genesis; any later difference is CAP_CHANGE_FORBIDDEN",
            "excluded_from_accounting": {
                "qualification_cpu_seconds": repr(q_cpu_total),
                "rule": "qualification is not a production cell and is not in N; COST_CAP_FORMULA.json does not include "
                        "it, so it is excluded and disclosed here",
                "synthetic_acceptance": "separate synthetic ledgers; never counted"},
        },
        "qualification": {
            "result_path": rel(qres_path), "result_sha256": sha256_file(qres_path),
            "protocol_path": rel(protocol_path), "protocol_sha256": PROTOCOL_SHA256, "verdict": "PASS",
            "record_paths": {k: rel(p) for k, p in sorted(QUALIFICATION_RECORDS.items())},
            "record_file_sha256": {k: sha256_file(p) for k, p in sorted(QUALIFICATION_RECORDS.items())},
            "scientific_content_hash": {k: r["scientific_content_hash"] for k, r in records.items()},
            "not_production": "cells 318 and 323 of qualification are NOT imported as production cells. Production "
                              "certifies all 326 cells, 318 and 323 included, in fresh attempts. The seal refuses a "
                              "file byte-identical to a qualification record (QUALIFICATION_RECORD_REUSE) and any "
                              "record claiming more CPU or wall time than its attempt used (CPU_EVIDENCE_INCONSISTENT). "
                              "Equality of a production scientific hash with a qualification hash is expected "
                              "(determinism) and is informational only.",
        },
        "k4": {
            "checkpoint_sha256": k4_sha, "k4_assembly_sha256": sha256_file(K4_NS / "code/k4_assembly.py"),
            "integrity_attestation_schema": "rebaseguard.p5y.k1.cusum-production.integrity-attestation.v1",
            "input_schema_attestation_path": rel(K4_ATTESTATION),
            "input_schema_attestation_sha256": sha256_file(K4_ATTESTATION),
            "K4_CUSUM_INPUT_SCHEMA_ATTESTED": att["K4_CUSUM_INPUT_SCHEMA_ATTESTED"],
            "export_layout": "prod_entry.py export: k4_records/ holds exactly one JSON per sealed cell (K4 globs *.json)",
            "k4_values_evaluated": False, "k4_assembly_run": False,
        },
        "entrypoint": {
            "path": rel(NS / "code/prod_entry.py"),
            "checks": ["C01_checkpoint_and_freeze", "C02_bound_sources", "C03_producer_identity", "C04_host_identity",
                       "C05_checkout", "C06_runtime_contract", "C07_universe_geometry", "C08_qualification_pass",
                       "C09_cost_cap", "C10_ledger_schema", "C11_k4_structural_attestation",
                       "C12_synthetic_acceptance", "C13_run_state", "C14_host_idle"],
            "launch": "prod_entry.py launch --confirm-checkpoint-sha256 <sha>; the supervisor re-runs every check under "
                      "the campaign lock before its first admission",
            "no_permissive_fallback": True,
        },
    }
    paths = bound_source_paths()
    cp["bound_sources"] = {rel(p): sha256_file(p) for p in paths}
    return cp


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("probe-host")
    p.add_argument("--out", required=True)
    sub.add_parser("build")
    a = ap.parse_args(argv)
    if a.cmd == "probe-host":
        import subprocess
        timers = {}
        for unit in ("apt-daily.timer", "apt-daily-upgrade.timer", "unattended-upgrades.service"):
            r = subprocess.run(["systemctl", "is-enabled", unit], capture_output=True, text=True)
            timers[unit] = r.stdout.strip() or r.stderr.strip()
        doc = {"schema": "rebaseguard.p5y.k1.cusum-aux5.host-identity.v1", "probed_utc": time.strftime(
                   "%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "facts": host_facts(),
               "disclosures": {"unit_state_observed": timers,
                               "note": "automatic upgrades are enabled on this host and are NOT modified; a glibc or "
                                       "kernel change is caught by the bound host facts and fails closed"}}
        atomic_write_json(a.out, doc)
        print(json.dumps(doc, indent=1))
        return 0
    try:
        cp = build()
    except Refusal as r:
        print(f"REFUSED [{r.code}] {r.detail}")
        return 1
    data = (json.dumps(cp, indent=1, sort_keys=True) + "\n").encode()
    atomic_write_bytes(CHECKPOINT, data)
    atomic_write_bytes(CHECKPOINT_HASH, (sha256_bytes(data) + "\n").encode())
    print(json.dumps({"checkpoint_sha256": sha256_bytes(data), "bound_sources": len(cp["bound_sources"]),
                      "cap_cpu_h": cp["cost_cap"]["cap_cpu_h"]}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
