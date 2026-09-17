"""External-authorization interface (EXECUTOR_SPEC_R2.md R2-3). PREPARED, NOT ACTIVE.

The frozen guard policy is DENY, so validate() is never reached on a real path in this successor. Under the policy
EXTERNAL_AUTHORIZATION, executor_core.guard_decision permits real arithmetic only if validate(bundle, ctx) accepts:

    bundle = {"authorization": <countersigned copy of config/EXTERNAL_AUTHORIZATION_TEMPLATE.json>,
              "prelaunch_report": {"verdict": "LAUNCH_PERMITTED", "authorization_sha256": ..., "utc_epoch": ...}}

This is a CONSISTENCY check of a published, result-blind statement against the running executor. It is not a
cryptographic authority, and it cannot authenticate the countersigner or the host operator (TRUST_MODEL.md).
Activation changes only config/REAL_INPUT_GUARD.json and the published countersigned object: no source file, so the
executor identity reviewed and qualified beforehand is the identity that runs.
"""
from __future__ import annotations

import hashlib
import json
import re
import time
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
TEMPLATE_FILE = NS / "config/EXTERNAL_AUTHORIZATION_TEMPLATE.json"
AUTH_SCHEMA = "rebaseguard.p5y.k5.cusum-real-point-executor.external-authorization.v1"
# The executor identity: every source the real path executes or that decides a gate, plus the pins it checks.
IDENTITY_FILES = ["code/paths.py", "code/executor_core.py", "code/backends.py", "code/input_adapters.py",
                  "code/authorization_interface.py", "code/executor_cli.py", "code/supervisor.py",
                  "code/qualification_gates.py", "code/consumer.py", "config/EXECUTOR_PINS.json"]
HEX64 = re.compile(r"^[0-9a-f]{64}$")
HEX40 = re.compile(r"^[0-9a-f]{40}$")


def _sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def canonical(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()


def executor_identity() -> dict:
    files = {f: _sha((NS / f).read_bytes()) for f in IDENTITY_FILES}
    return {"files": files, "executor_identity_sha256": _sha(canonical(files))}


def validate(bundle, ctx) -> tuple[bool, list, str | None]:
    """(accepted, problems, authorization_sha256). Every check is fail closed; any problem refuses."""
    import executor_core as EC
    import probe_rules as PR
    problems = []
    if not isinstance(bundle, dict) or not isinstance(bundle.get("authorization"), dict) \
            or not isinstance(bundle.get("prelaunch_report"), dict) or ctx is None:
        return False, ["no authorization bundle / context"], None
    a, rep = bundle["authorization"], bundle["prelaunch_report"]
    auth_sha = _sha(canonical(a))
    tmpl = json.loads(TEMPLATE_FILE.read_text())
    p = EC.prereg()

    def need(cond, msg):
        if not cond:
            problems.append(msg)

    need(set(tmpl) <= set(a), f"missing template fields {sorted(set(tmpl) - set(a))}")
    need(a.get("schema") == AUTH_SCHEMA, "schema")
    need(a.get("status") == "COUNTERSIGNED", "status is not COUNTERSIGNED")
    need(a.get("EXECUTION_AUTHORIZED") is True, "EXECUTION_AUTHORIZED is not true")
    need(a.get("result_blind") == tmpl["result_blind"], "result-blind statement differs from the template")
    sci = a.get("science_preregistration") or {}
    need(sci.get("sha256") == _sha(EC.SCIENCE_FILE.read_bytes()) == ctx.protocol_sha256, "science sha256")
    ex = a.get("executor") or {}
    need(ex.get("identity_sha256") == executor_identity()["executor_identity_sha256"], "running executor identity")
    need(bool(HEX40.match(str(ex.get("freeze_commit")))) and bool(HEX40.match(str(ex.get("qualification_commit")))),
         "executor freeze / qualification commits")
    need(bool(HEX64.match(str(ex.get("qualification_result_sha256")))), "qualification result sha256")
    need(str(ex.get("static_review", "")).startswith("PASS"), "executor static review is not PASS")
    k1 = a.get("k1_input") or {}
    want = p["k1_input_identity"]
    need(k1.get("record_sha256") == want["record_sha256"] == ctx.k1_binding.get("record_sha256"), "K1 record sha256")
    need(k1.get("export_manifest_sha256") == want["manifest_sha256"], "K1 manifest sha256")
    need(a.get("cell") == tmpl["cell"] and ctx.k1_binding.get("right") == tmpl["cell"]["right"]
         and ctx.point_e == tmpl["cell"]["point_e"], "cell")
    need(a.get("m_set") == EC.M_SET == list(ctx.m_set), "m set")
    need(a.get("precision_bits") == ctx.precision_bits == EC.PRECISION, "precision")
    need(a.get("cpu_ceiling") == {k: v for k, v in p["cpu_ceiling"].items() if k != "enforcement"}, "CPU ceiling")
    need(a.get("host_runtime_identity_sha256") == p["host_runtime_identity_sha256"] == ctx.runtime_identity_sha256,
         "host runtime identity")
    slot = a.get("attempt_slot")
    try:
        slot_name = PR.slot_dir(slot) if isinstance(slot, int) else None
    except Exception:
        slot_name = None
    out = Path(ctx.output_dir)
    need(slot_name is not None and out.name == slot_name and str(out.parent) == a.get("output_namespace"),
         "output namespace / attempt slot")
    need(bool(re.match(r"^[0-9a-f]{32,}$", str(a.get("nonce")))), "nonce")
    cs = a.get("countersigner") or {}
    need(bool(cs.get("identity")) and cs.get("independent_of_execution_host") is True, "countersigner")
    utc = cs.get("utc")
    need(isinstance(utc, (int, float)) and utc <= time.time(), "countersignature utc")
    need(rep.get("verdict") == "LAUNCH_PERMITTED", "prelaunch verdict")
    need(rep.get("authorization_sha256") == auth_sha, "prelaunch report names another authorization")
    need(isinstance(rep.get("utc_epoch"), (int, float)) and isinstance(utc, (int, float)) and rep["utc_epoch"] >= utc,
         "prelaunch report predates the countersignature")
    return (not problems), problems, auth_sha
