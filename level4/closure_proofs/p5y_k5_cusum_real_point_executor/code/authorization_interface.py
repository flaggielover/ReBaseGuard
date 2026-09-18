"""Real-mode authorization (EXECUTOR_SPEC_R3.md R3-1). PREPARED, NOT ACTIVE: the frozen guard policy is DENY.

Under the policy EXTERNAL_AUTHORIZATION, executor_core.decide permits real arithmetic only if validate(ctx) accepts.
The AUTHORITY is the frozen protocol's own verifier, called here IN PROCESS with its defaults only:

    report = prelaunch_verify.verify(prelaunch_verify.AUTH_ACTIVE)

and the decision consumes that returned object directly. There is no input path for a verifier report, and a context
carrying operator-supplied authorization material is refused. The authorization is the protocol's
protocol/AUTHORIZATION_ACTIVE.json, identified (as the verifier identifies it) by the sha256 of its FILE BYTES; the
executor is bound to it through EXECUTION_BINDING_AMENDMENT.json. The external countersignature
(authorization/COUNTERSIGNATURE_ACTIVE.json) is a SECOND, separately hashed requirement that must name the same
authorization bytes; it never replaces the verifier result.

This is a consistency and fail-closed mechanism. It is not a cryptographic authority and authenticates no one
(TRUST_MODEL.md). Activation changes only config/REAL_INPUT_GUARD.json and published protocol/authorization files,
never a source file, so the reviewed and qualified executor identity is the identity that runs.
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import time
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
REPO = NS.parents[2]
REL = "level4/closure_proofs/p5y_k5_cusum_real_point_executor/"
TEMPLATE_FILE = NS / "config/EXTERNAL_AUTHORIZATION_TEMPLATE.json"
COUNTERSIGNATURE_FILE = NS / "authorization/COUNTERSIGNATURE_ACTIVE.json"
AUTH_SCHEMA = "rebaseguard.p5y.k5.cusum-real-point-executor.external-countersignature.v2"
VERIFIER_REL = "level4/closure_proofs/p5y_k5_cusum_first_real_probe_protocol/code/prelaunch_verify.py"
REPORT_SCHEMA = "rebaseguard.p5y.k5.cusum-first-real-probe.prelaunch-report.v4"
CHECK_IDS = [f"P{i:02d}" for i in range(1, 13)]
# The executor identity: every source the real path executes or that decides a gate, plus the pins it checks.
IDENTITY_FILES = ["code/paths.py", "code/executor_core.py", "code/backends.py", "code/input_adapters.py",
                  "code/authorization_interface.py", "code/lifecycle.py", "code/executor_cli.py", "code/supervisor.py",
                  "code/qualification_gates.py", "code/consumer.py", "config/EXECUTOR_PINS.json"]
OPERATOR_MATERIAL_ATTRIBUTES = ("authorization_bundle", "prelaunch_report", "verifier_report")
HEX64 = re.compile(r"^[0-9a-f]{64}$")
HEX40 = re.compile(r"^[0-9a-f]{40}$")


def _sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def canonical(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True, default=str).encode()


def executor_identity() -> dict:
    files = {f: _sha((NS / f).read_bytes()) for f in IDENTITY_FILES}
    return {"files": files, "executor_identity_sha256": _sha(canonical(files))}


def _file_sha(path) -> str | None:
    p = Path(path)
    return _sha(p.read_bytes()) if p.is_file() and not p.is_symlink() else None


# ------------------------------------------------------------------ verifier source
def verifier_source_problems(module) -> list:
    """The imported verifier is the frozen file: its path, its bytes (preregistration packet_code_sha256 and the
    executor pins) and its verify function's code object."""
    import executor_core as EC
    problems = []
    want = (REPO / VERIFIER_REL).resolve()
    path = Path(getattr(module, "__file__", "") or "").resolve()
    if path != want:
        problems.append(f"verifier module is not the frozen file ({path})")
    digest = _file_sha(path)
    if digest is None or digest != EC.prereg()["packet_code_sha256"].get(VERIFIER_REL):
        problems.append("verifier bytes differ from the preregistration packet_code_sha256")
    try:
        pins = json.loads(EC.PINS_FILE.read_text())["files"]
    except (OSError, ValueError, KeyError):
        pins = {}
    if digest is None or pins.get(VERIFIER_REL) != digest:
        problems.append("verifier bytes differ from the executor pins")
    fn = getattr(module, "verify", None)
    code = getattr(fn, "__code__", None)
    if fn is None or getattr(fn, "__module__", None) != getattr(module, "__name__", None) or code is None \
            or Path(code.co_filename).resolve() != want:
        problems.append("verify is not the frozen module's own function")
    return problems


def run_verifier(verify_fn, auth_path):
    """Call the verifier with its defaults only; any exception refuses."""
    try:
        return verify_fn(auth_path), None
    except Exception as exc:                                                        # fail closed
        return None, f"verifier raised {type(exc).__name__}"


# ------------------------------------------------------------------ facts read by the executor itself
def live_facts(module) -> dict:
    import executor_core as EC
    auth_path = Path(module.AUTH_ACTIVE)
    facts = {"auth_path": str(auth_path),
             "auth_path_is_prereg_path": auth_path.resolve() == (REPO / EC.prereg()["authorization_path"]).resolve(),
             "auth_sha": _file_sha(auth_path), "amendment_sha": _file_sha(module.AMENDMENT),
             "science_sha": _file_sha(EC.SCIENCE_FILE),
             "head": subprocess.run(["git", "-C", str(REPO), "rev-parse", "HEAD"], capture_output=True,
                                    text=True).stdout.strip()}
    for key, path in (("auth", auth_path), ("amendment", Path(module.AMENDMENT))):
        try:
            facts[key] = json.loads(path.read_text()) if path.is_file() else None
        except ValueError:
            facts[key] = "MALFORMED"
    return facts


# ------------------------------------------------------------------ pure decision on the returned object
def decide_from_report(report, facts: dict, ctx) -> list:
    """Q01 on the verifier's returned object and the executor's own facts (before / after the call)."""
    p = []
    if not isinstance(report, dict):
        return ["verifier output is not an object"]
    checks = report.get("checks")
    if report.get("schema") != REPORT_SCHEMA:
        p.append("verifier output schema")
    if report.get("verdict") != "LAUNCH_PERMITTED" or report.get("failing_checks") != []:
        p.append(f"verifier verdict {report.get('verdict')!r}")
    if not isinstance(checks, dict) or sorted(checks) != CHECK_IDS or \
            not all(isinstance(c, dict) and c.get("pass") is True for c in checks.values()):
        p.append("verifier checks P01..P12 not all present and passing")
    if report.get("read_only") is not True:
        p.append("verifier output not read-only")
    if not facts.get("auth_path_is_prereg_path") or report.get("authorization_path") != facts.get("auth_path"):
        p.append("report names another authorization path")
    a0, a1 = facts.get("auth_sha"), facts.get("auth_sha_after")
    if a0 is None or report.get("authorization_sha256") != a0 or a1 != a0:
        p.append("authorization bytes differ from the verified authorization (another or changed authorization)")
    if report.get("science_sha256") != ctx.protocol_sha256 or facts.get("science_sha") != ctx.protocol_sha256:
        p.append("report names another protocol identity")
    if not HEX40.match(str(report.get("head"))) or report.get("head") != facts.get("head"):
        p.append("report is for another HEAD (stale)")
    for key in ("freeze_commit_derived", "authorization_commit_derived"):
        if not HEX40.match(str(report.get(key))):
            p.append(f"report lacks {key}")
    return p


def binding_problems(facts: dict, ctx) -> list:
    """The executor binding: amendment bytes <-> authorization <-> scientific address <-> running executor bytes."""
    p = []
    am_sha, auth, am = facts.get("amendment_sha"), facts.get("auth"), facts.get("amendment")
    if am_sha is None or not isinstance(am, dict):
        return ["no executor binding amendment"]
    if not isinstance(auth, dict) or (auth.get("PRODUCER_R4_IDENTITY") or {}).get("executor_binding_sha256") != am_sha:
        p.append("authorization names another executor binding")
    if ctx.executor_binding_sha256 != am_sha:
        p.append("context executor_binding_sha256 differs from the amendment (address would bind another executor)")
    srcs = am.get("executor_sources_sha256") or {}
    live = executor_identity()["files"]
    missing = [f for f, h in live.items() if srcs.get(REL + f) != h]
    if missing:
        p.append(f"amendment does not bind the running executor bytes: {missing[:4]}")
    return p


def countersignature_problems(facts: dict, report: dict, ctx, module, path: Path = COUNTERSIGNATURE_FILE) -> list:
    """Second requirement: a committed countersignature naming the same authorization bytes, amendment and slot."""
    import executor_core as EC
    import probe_rules as PR
    p = []
    path = Path(path)
    if not path.is_file() or path.is_symlink():
        return ["no countersignature at authorization/COUNTERSIGNATURE_ACTIVE.json"]
    try:
        c = json.loads(path.read_text())
    except ValueError:
        return ["countersignature malformed"]
    tmpl = json.loads(TEMPLATE_FILE.read_text())
    if not isinstance(c, dict) or set(c) != set(tmpl):
        return ["countersignature fields differ from the template"]
    try:
        committed = module.committed_unmodified(path)
        intro = module.introduced_by(path)
    except Exception:
        committed, intro = False, []
    if not committed or len(intro) != 1:
        p.append("countersignature not committed exactly once and unmodified")
    elif not module.is_ancestor(str(report.get("authorization_commit_derived")), intro[0]):
        p.append("countersignature not committed after the authorization")
    if c.get("schema") != AUTH_SCHEMA or c.get("status") != "COUNTERSIGNED" or c.get("EXECUTION_AUTHORIZED") is not True:
        p.append("countersignature not active")
    if c.get("result_blind") != tmpl["result_blind"]:
        p.append("result-blind statement differs from the template")
    if c.get("protocol_authorization_sha256") != facts.get("auth_sha"):
        p.append("countersignature names another authorization")
    if c.get("execution_binding_amendment_sha256") != facts.get("amendment_sha"):
        p.append("countersignature names another executor binding")
    slot = c.get("attempt_slot")
    try:
        slot_name = PR.slot_dir(slot) if isinstance(slot, int) else None
    except Exception:
        slot_name = None
    out = Path(ctx.output_dir)
    if slot_name is None or out.name != slot_name or str(out.parent) != EC.prereg()["output_namespace"]:
        p.append("countersignature slot / namespace differ from the context")
    if not re.match(r"^[0-9a-f]{32,}$", str(c.get("nonce"))):
        p.append("nonce")
    cs = c.get("countersigner") or {}
    if not cs.get("identity") or cs.get("independent_of_execution_host") is not True \
            or not isinstance(cs.get("utc"), (int, float)) or cs["utc"] > time.time():
        p.append("countersigner")
    return p


def validate(ctx) -> tuple[bool, list, dict]:
    """(accepted, problems, binding): the frozen verifier module and the fixed countersignature path. Nothing here
    computes science."""
    import prelaunch_verify as PV
    return validate_with(ctx, PV, COUNTERSIGNATURE_FILE)


def validate_with(ctx, module, countersignature_path) -> tuple[bool, list, dict]:
    """Every path fails closed. Operator-supplied material is refused, and a module that is not the frozen verifier is
    refused, BEFORE any verifier code runs."""
    present = [a for a in OPERATOR_MATERIAL_ATTRIBUTES if getattr(ctx, a, None) is not None]
    if ctx is None or present:
        return False, [f"operator-supplied authorization material is not accepted: {present}"], {}
    problems = verifier_source_problems(module)
    if problems:
        return False, problems, {}
    facts = live_facts(module)
    report, error = run_verifier(module.verify, module.AUTH_ACTIVE)
    facts["auth_sha_after"] = _file_sha(module.AUTH_ACTIVE)
    if error:
        return False, [error], {}
    problems = decide_from_report(report, facts, ctx)
    problems += binding_problems(facts, ctx)
    if not problems:
        problems += countersignature_problems(facts, report, ctx, module, countersignature_path)
    binding = {"authorization_path": facts["auth_path"], "authorization_sha256": facts.get("auth_sha"),
               "execution_binding_amendment_sha256": facts.get("amendment_sha"), "head": facts.get("head"),
               "prelaunch_report_sha256": _sha(canonical(report)) if isinstance(report, dict) else None,
               "prelaunch_verdict": report.get("verdict") if isinstance(report, dict) else None,
               "countersignature_sha256": _file_sha(countersignature_path), "verified_utc_epoch": time.time()}
    return (not problems), problems, binding


def authorization_unchanged(binding: dict) -> bool:
    """Re-hash the verified authorization bytes (at ARITHMETIC_STARTED and at seal)."""
    import prelaunch_verify as PV
    return bool(binding.get("authorization_sha256")) and _file_sha(PV.AUTH_ACTIVE) == binding["authorization_sha256"]
