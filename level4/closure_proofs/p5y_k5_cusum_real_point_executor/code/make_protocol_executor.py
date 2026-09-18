"""Emit config/EXECUTOR_QUALIFICATION_PROTOCOL.json (frozen) or a DEV copy (python3 -B code/make_protocol_executor.py [--dev OUT])."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
CP = NS.parents[0]
REPO = NS.parents[2]
REL = "level4/closure_proofs/p5y_k5_cusum_real_point_executor/"
EXECUTOR_SOURCES = ["code/paths.py", "code/executor_core.py", "code/backends.py", "code/input_adapters.py",
                    "code/authorization_interface.py", "code/lifecycle.py", "code/executor_cli.py", "code/supervisor.py",
                    "code/qualification_gates.py", "code/consumer.py"]
QUALIFICATION_SOURCES = ["code/smoke.py", "code/exec_fixtures.py", "code/qualify_executor.py", "code/make_protocol_executor.py",
                         "config/REAL_INPUT_GUARD.json", "config/EXTERNAL_AUTHORIZATION_TEMPLATE.json",
                         "config/FIXTURE_LIMITS.json", "EXECUTOR_SPEC.md", "EXECUTOR_SPEC_R2.md", "EXECUTOR_SPEC_R3.md", "TRUST_MODEL.md"]
V = {"S": "SUPPORTS_K5B_FIRST_CELL", "I": "INCONCLUSIVE", "C": "CONTRADICTS_REQUIRED_POSITIVE_SIGN",
     "P": "POINT_POSITIVE", "N": "POINT_NEGATIVE", "U": "POINT_UNDETERMINED"}


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def vs(code: str) -> dict:
    """'SP SP IN CN' -> per-m expected [verdict, point] for m = 1, 2, 3, 5."""
    return {m: [V[c[0]], V[c[1]]] for m, c in zip(("1", "2", "3", "5"), code.split())}


def fixtures():
    return [
        {"id": "XF01_positive_L1", "purpose": "decisively positive L1", "seed": 7001, "C_target": 3, "x1": "1/4000",
         "noise": "0", "expect": {"verdicts": vs("SP SP SP SP")}},
        {"id": "XF02_inconclusive_transport", "purpose": "inconclusive transported interval (point positive)", "seed": 7011,
         "C_target": 5, "x1": "1/16", "noise": "1/100000", "expect": {"verdicts": vs("IP IP IP IP")}},
        {"id": "XF03_negative_U1", "purpose": "decisively negative U1", "seed": 7003, "C_target": 3, "x1": "1/4000",
         "noise": "0", "expect": {"verdicts": vs("CN CN CN CN")}},
        {"id": "XF04_point_negative_U0", "purpose": "point-negative U0 with inconclusive transport", "seed": 7004,
         "C_target": 5, "x1": "1/16", "noise": "1/100000", "expect": {"verdicts": vs("IN IN IP IP")}},
        {"id": "XF05_tight_M5", "purpose": "tight M5", "seed": 7015, "C_target": 3, "x1": "1/4000", "noise": "0",
         "expect": {"verdicts": vs("SP SP SP SP"), "M5_ratio_max": "DEV"}},
        {"id": "XF06_loose_valid_M5", "purpose": "loose but valid M5", "seed": 7002, "C_target": 3, "x1": "1/4000",
         "noise": "0", "expect": {"verdicts": vs("SP SP SP SP"), "M5_ratio_min_m1": "DEV"}},
        {"id": "XF07_parity_pure", "purpose": "parity-pure source (exact candidates)", "seed": 7005, "C_target": 3,
         "x1": "1/4000", "noise": "0", "expect": {"verdicts": vs("CN CN CN CN")}},
        {"id": "XF08_parity_contamination", "purpose": "controlled parity contamination (k_scale 2, noise)", "seed": 7018,
         "C_target": 20, "k_scale": "2", "x1": "1/100", "noise": "1/100000", "expect": {"verdicts": vs("SP SP SP SP")}},
        {"id": "XF09_near_zero_boundary", "purpose": "near-zero scientific boundary (m = 1, 2 straddle zero)", "seed": 7002,
         "C_target": 5, "x1": "1/50", "noise": "1/100000", "expect": {"verdicts": vs("IP IP SP SP")}},
    ]


def mutations():
    M = [
        ("E01_WRONG_M", "executor_core.py", 'L0, U0 = out0["m"][m]["R3_mid"]', 'L0, U0 = out0["m"][M_SET[M_SET.index(m) - 1]]["R3_mid"]'),
        ("E02_WRONG_POINT_E", "backends.py", "gr0 = SS.GradedRig(sysm, F(0), F(0), seed=seed, noise=noise)",
         "gr0 = SS.GradedRig(sysm, x1 / 2, F(0), seed=seed, noise=noise)"),
        ("E03_WRONG_CELL_ENDPOINT", "executor_core.py", 'x1 = F(ctx.k1_binding["right"])', 'x1 = F(ctx.k1_binding["right"]) / 2'),
        ("E04_WRONG_K1_IDENTITY_ACCEPTED", "executor_core.py", 'if b["record_sha256"] != want["record_sha256"] or',
         'if False and b["record_sha256"] != want["record_sha256"] or'),
        ("E05_ODD_EVEN_COMPONENT_SWAP", "backends.py", "out[node] = (ex(ge), ex(go))", "out[node] = (ex(go), ex(ge))"),
        ("E06_OMIT_DERIVATIVE_SOURCE_TERM", "backends.py", '"S0": {n: ex(grH.rig.T["S", 0, n]) for n in range(7)},',
         '"S0": {n: ex(grH.rig.T["S", 0, n]) * (n != 1) for n in range(7)},'),
        ("E07_WRONG_GRADED_CONSTANT", "backends.py", '"C_e0": ex(grH.C_e0), "C_o0": ex(grH.C_o0),',
         '"C_e0": ex(grH.C_o0), "C_o0": ex(grH.C_e0),'),
        ("E08_WRONG_LOCAL_M5_ANCHOR", "executor_core.py", 'out0["mid"]["nodes"], x1=R1E.exact(x1))',
         'out0["mid"]["nodes"], x1=R1E.exact(0))'),
        ("E09_WRONG_TRANSPORT_FACTOR", "executor_core.py", "tf = x1 * x1 / 2", "tf = x1 * x1 / 4"),
        ("E10_WRONG_L1_SIGN", "executor_core.py", '"L1": L0 - tf * M5', '"L1": L0 + tf * M5'),
        ("E11_WRONG_U1_SIGN", "executor_core.py", '"U1": U0 + tf * M5', '"U1": U0 - tf * M5'),
        ("E12_SERIALIZE_MIDPOINT", "executor_core.py", 'L0, U0 = out0["m"][m]["R3_mid"]',
         'L0 = U0 = sum(out0["m"][m]["R3_mid"]) / 2'),
        ("E13_REUSE_STALE_CERTIFICATE", "executor_core.py", "stages = run_stages_before_enclosure(backend, ctx)",
         'stages = globals().setdefault("_STALE_STAGES", run_stages_before_enclosure(backend, ctx))'),
        ("E14_BYPASS_REAL_INPUT_GUARD", "executor_core.py",
         "    decision = enforce_guard(backend, ctx)                   # FIRST: before any backend method",
         "    decision = guard_decision(None, ctx)                     # FIRST: before any backend method"),
        ("E15_SILENT_PRECISION_CHANGE", "executor_core.py", "R1E.precision(ctx.precision_bits):", "R1E.precision(128):"),
        ("E16_MUTATE_SCIENTIFIC_ADDRESS", "executor_core.py", 'k1_record_sha256=ctx.k1_binding["record_sha256"],',
         'k1_record_sha256="0" * 64,'),
    ]
    return [{"id": i, "file": f, "old": o, "new": n, "required": True} for i, f, o, n in M]


def production_mutations():
    """P01-P04: the shared _CusumStack methods (detected in the real-stage smoke by the unmutated shared checks)."""
    M = [
        ("P01_CONSTANTS_ODD_EVEN_SWAP", "backends.py", '"C_e0": ex(c["C_e0"]), "C_o0": ex(c["C_o0"]),',
         '"C_e0": ex(c["C_o0"]), "C_o0": ex(c["C_e0"]),'),
        ("P02_HULL_BASE_WRONG_X1", "backends.py", '"eta": ex(x1), "S0": {n: H6.sup_S0_on(n, F(0), x1)',
         '"eta": ex(x1 / 2), "S0": {n: H6.sup_S0_on(n, F(0), x1)'),
        ("P03_ORIGIN_WRONG_ORDER", "backends.py", 'cert.origin(("W", (r, j), 3)) for r in range(4)',
         'cert.origin(("W", (r, j), 2)) for r in range(4)'),
        ("P04_CANDIDATE_PARITY_SWAP", "backends.py", "out[node] = (v.e, v.o)", "out[node] = (v.o, v.e)"),
    ]
    return [{"id": i, "file": f, "old": o, "new": n, "required": True} for i, f, o, n in M]


def authorization_mutations():
    """A01-A03 (r3): countersignature / binding validator mutants (detected in the D1 authorization suite)."""
    M = [
        ("A01_COUNTERSIGNATURE_AUTHORIZATION_IGNORED", "authorization_interface.py",
         'if c.get("protocol_authorization_sha256") != facts.get("auth_sha"):', "if False:"),
        ("A02_CONTEXT_EXECUTOR_BINDING_IGNORED", "authorization_interface.py",
         "if ctx.executor_binding_sha256 != am_sha:", "if False:"),
        ("A03_COUNTERSIGNER_INDEPENDENCE_IGNORED", "authorization_interface.py",
         'if not cs.get("identity") or cs.get("independent_of_execution_host") is not True \\',
         'if not cs.get("identity") \\'),
    ]
    return [{"id": i, "file": f, "old": o, "new": n, "required": True} for i, f, o, n in M]


def d1_mutations():
    """D01-D04: in-process prelaunch verification mutants (detected in the D1 authorization suite)."""
    M = [
        ("D01_VERIFIER_SOURCE_NOT_CHECKED", "authorization_interface.py",
         "    problems = verifier_source_problems(module)\n", "    problems = []\n"),
        ("D02_STALE_REPORT_ACCEPTED", "authorization_interface.py",
         'if not HEX40.match(str(report.get("head"))) or report.get("head") != facts.get("head"):',
         'if not HEX40.match(str(report.get("head"))):'),
        ("D03_AUTHORIZATION_CHANGE_AFTER_VERIFY_IGNORED", "authorization_interface.py",
         'if a0 is None or report.get("authorization_sha256") != a0 or a1 != a0:',
         'if a0 is None or report.get("authorization_sha256") != a0:'),
        ("D04_OPERATOR_MATERIAL_ACCEPTED", "authorization_interface.py",
         "    if ctx is None or present:\n", "    if ctx is None:\n"),
    ]
    return [{"id": i, "file": f, "old": o, "new": n, "required": True} for i, f, o, n in M]


def lifecycle_mutations():
    """L01-L04: marker lifecycle / ledger mutants (detected in the D2 lifecycle suite)."""
    M = [
        ("L01_COMPLETE_WITHOUT_VALID_SEAL", "supervisor.py",
         'valid_complete = (code == 0 and sci is not None and sci["valid"] and void is None',
         "valid_complete = (code == 0 and sci is not None"),
        ("L02_SCIENTIFIC_VOID_SEAL_CONFLICT_ALLOWED", "executor_core.py",
         '    if any((out / n).exists() for n in SEAL_NAMES):\n        raise ExecutorRefusal("SEAL_CONFLICT',
         '    if False:\n        raise ExecutorRefusal("SEAL_CONFLICT'),
        ("L03_VOID_SEALED_ON_TRANSIENT_DISK_FULL", "executor_core.py",
         '    if isinstance(exc, OSError) and getattr(exc, "errno", None) in TRANSIENT_ERRNOS:', "    if False:"),
        ("L04_LEDGER_DISAGREEMENT_IGNORED", "lifecycle.py",
         "        if out.get(k) != derived.get(k):", "        if False:"),
    ]
    return [{"id": i, "file": f, "old": o, "new": n, "required": True} for i, f, o, n in M]


def recovery_mutations():
    """R01-R02: reboot-recovery mutants (detected in the D3 recovery suite)."""
    M = [
        ("R01_SEALED_SLOT_MADE_RETRYABLE", "lifecycle.py",
         '"C": "CONSUME_SEALED_RECORD_WRITE_RUN_COMPLETE_RECOVERED"', '"C": "WRITE_RUN_FAILED_INTERRUPTED"'),
        ("R02_TORN_STATE_ACCEPTED", "lifecycle.py",
         '    if out["problems"]:\n        cls = "E"', '    if False:\n        cls = "E"'),
    ]
    return [{"id": i, "file": f, "old": o, "new": n, "required": True} for i, f, o, n in M]


def void_mutations():
    """V01: VOID sealing dropped (detected by the supervisor CPU-limit test)."""
    return [{"id": "V01_VOID_SEAL_DROPPED", "file": "executor_core.py",
             "old": "            seal(void, out, VOID_NAMES[bool(backend.real_input)])",
             "new": "            pass", "required": True}]


def cramer_mutations():
    """C01: the certificate stack first imported at 256 bits (detected by the fail-closed CRAMER contract check)."""
    return [{"id": "C01_WRONG_FIRST_IMPORT_PRECISION", "file": "backends.py",
             "old": '    with flint_ctx.workprec(CRAMER_CONTRACT["construction_precision_bits"]):\n        import odd_block_certificate',
             "new": "    with flint_ctx.workprec(256):\n        import odd_block_certificate", "required": True}]


def executor_pins() -> dict:
    """config/EXECUTOR_PINS.json: every byte the real path or its gates depend on, except the guard policy file (the
    one file activation changes) and this pins file itself (bound through the executor identity)."""
    out = dict(pins())
    prereg = json.loads((CP / "p5y_k5_cusum_first_real_probe_protocol/protocol/SCIENCE_PREREGISTRATION_R4.json").read_text())
    ident = prereg["k1_input_identity"]
    for rel in (ident["record"], ident["manifest"], "level4/closure_proofs/p5y_k1_cover_ledger_successor/config/cells.json",
                "level4/closure_proofs/p5y_gammatilde_point_certificate/result/RUNG_256.json",
                "level4/closure_proofs/p5y_gammatilde_point_certificate/code/point_eval.py"):
        out[rel] = sha(REPO / rel)
    for f in sorted((NS / "code").glob("*.py")):
        out[REL + "code/" + f.name] = sha(f)
    for f in ("config/EXTERNAL_AUTHORIZATION_TEMPLATE.json", "config/FIXTURE_LIMITS.json"):
        out[REL + f] = sha(NS / f)
    return dict(sorted(out.items()))


def pins() -> dict:
    r4 = json.loads((CP / "p5y_k5_cusum_order3_r4_tightening/config/QUALIFICATION_PROTOCOL_R4.json").read_text())
    out = {}
    for key in ("r1_bound_sha256", "r2_bound_sha256", "r3_bound_sha256", "bound_code_sha256", "bound_config_sha256"):
        out.update(r4[key])
    for rel in ("level4/closure_proofs/p5y_k5_cusum_order3_r4_tightening/config/QUALIFICATION_PROTOCOL_R4.json",
                "level4/closure_proofs/p5y_k5_cusum_order3_r4_tightening/evidence/qualification_r4/QUALIFICATION_RESULT_R4.json",
                "level4/closure_proofs/p5y_k5_cusum_first_real_probe_protocol/protocol/SCIENCE_PREREGISTRATION_R4.json",
                "level4/closure_proofs/p5y_k5_cusum_first_real_probe_protocol/code/probe_rules.py",
                "level4/closure_proofs/p5y_k5_cusum_first_real_probe_protocol/code/prelaunch_verify.py",
                "level4/closure_proofs/p5y_gammatilde_point_certificate/code/point_core.py"):
        out[rel] = sha(REPO / rel)
    return out


def build(dev: bool) -> dict:
    science = CP / "p5y_k5_cusum_first_real_probe_protocol/protocol/SCIENCE_PREREGISTRATION_R4.json"
    prereg = json.loads(science.read_text())
    pins_file = NS / "config/EXECUTOR_PINS.json"
    pins_obj = {"schema": "rebaseguard.p5y.k5.cusum-real-point-executor.pins.v1",
                "rule": "Q05/Q13: every listed file has this sha256 at attempt start and at seal; config/REAL_INPUT_GUARD.json is deliberately not listed (activation changes only it and the published authorization)",
                "files": executor_pins()}
    raw = (json.dumps(pins_obj, indent=1, sort_keys=True) + "\n").encode()
    if not pins_file.exists() or pins_file.read_bytes() != raw:
        pins_file.write_bytes(raw)
    import authorization_interface as AI
    ex_src = {REL + f: sha(NS / f) for f in EXECUTOR_SOURCES}
    identity = AI.executor_identity()
    fx = fixtures()
    limits = json.loads((NS / "config/FIXTURE_LIMITS.json").read_text()) if (NS / "config/FIXTURE_LIMITS.json").exists() else {}
    for f in fx:
        for k in ("M5_ratio_max", "M5_ratio_min_m1"):
            if f["expect"].get(k) == "DEV":
                if k in limits.get(f["id"], {}):
                    f["expect"][k] = limits[f["id"]][k]
                elif dev:
                    f["expect"].pop(k)
                else:
                    raise SystemExit(f"{f['id']}: {k} not calibrated")
    return {
        "schema": "rebaseguard.p5y.k5.cusum-real-point-executor.qualification-protocol.v2",
        "status": "DEV_CALIBRATION_ONLY" if dev else "FROZEN_PRE_QUALIFICATION",
        "scope": "manufactured systems, synthetic candidates and operator certificates only; REAL_INPUT_ARITHMETIC_GUARD = DENY; "
                 "no real K1 cell executed; no real R''', R^(5), L1 or U1 formed",
        "science_preregistration_sha256": sha(science),
        "runtime_contract": prereg["host_runtime_contract"],
        "cpu_ceiling": prereg["cpu_ceiling"],
        "cost_model": {"committed_collocation_cpu_seconds": 1501.7,
                       "committed_collocation_basis": "GammaTilde point run at e = 0 (order-2 collocation + stack) 1160.5 CPU-s + Aux3 auxiliary order-3 evidence of cell 0 171.2 CPU-s + R1 rung-3 candidate recompute ~170 CPU-s (all committed); the real Arb residual, graded-range, certificate-load and hull stages are MEASURED by the smoke",
                       "enclosure_and_tower_allowance_cpu_seconds": 120, "safety_factor": 1.5},
        "fixtures": fx,
        "separation_fixtures": {"SUPPORTS": "XF01_positive_L1", "INCONCLUSIVE": "XF02_inconclusive_transport",
                                "CONTRADICTS": "XF03_negative_U1"},
        "crosscheck_fixtures": ["XF01_positive_L1", "XF03_negative_U1", "XF04_point_negative_U0", "XF08_parity_contamination"],
        "smoke_seed": 9401 if not dev else 99401,
        "mutations": mutations(),
        "production_mutations": production_mutations(),
        "authorization_mutations": authorization_mutations(),
        "void_mutations": void_mutations(),
        "d1_mutations": d1_mutations(),
        "lifecycle_mutations": lifecycle_mutations(),
        "recovery_mutations": recovery_mutations(),
        "cramer_mutations": cramer_mutations(),
        "supervisor_tests": {"fixture": "XF01_positive_L1", "cpu_limit": {"cpu_soft": 20, "cpu_hard": 40, "wall": 600},
                             "wall_timeout": {"cpu_soft": 600, "cpu_hard": 900, "wall": 15},
                             "external_kill": {"cpu_soft": 600, "cpu_hard": 900, "wall": 600}},
        "executor_pins_sha256": sha(pins_file),
        "inherited_r4_parts": ["odd_certificate", "first_cell", "b01", "r5_mutations", "m5_crosscheck", "failclosed"],
        "pins_sha256": pins(),
        "executor_sources_sha256": {**ex_src, **{REL + f: sha(NS / f) for f in QUALIFICATION_SOURCES}},
        "executor_identity": identity,
        "executor_identity_sha256": identity["executor_identity_sha256"],
    }


if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "--dev":
        Path(sys.argv[2]).write_text(json.dumps(build(True), indent=1) + "\n")
    else:
        (NS / "config/EXECUTOR_QUALIFICATION_PROTOCOL.json").write_text(json.dumps(build(False), indent=1) + "\n")
