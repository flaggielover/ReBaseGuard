"""The frozen slot-N marker lifecycle (EXECUTOR_SPEC_R3.md R3-2 / R3-3; SCIENCE_PREREGISTRATION_R4.completion_semantics
and retry_policy.slots_and_ledger). Shared by the supervisor, its recovery mode and the qualification. Never computes
science; never launches the executor.

    <output_namespace>/slot-N/
        RUN_STATE.json                      supervisor: pid, argv, boot id, start epoch, authorization sha256, slot,
                                            attempt_uid, protocol sha256, executor identity
        ATTEMPT_LOG.jsonl                   executor: VALIDATED / ARITHMETIC_STARTED / SEALED | VOID (no numbers)
        SCIENTIFIC_RECORD_SEALED.json       executor (real)          | MANUFACTURED_RECORD_SEALED.json (qualification)
        VOID_RECORD_SEALED.json             executor (real)          | MANUFACTURED_VOID_RECORD_SEALED.json
        RUN_COMPLETE.json | RUN_FAILED.json supervisor or recovery: exactly one terminal marker per attempt

Every marker and seal is written tmp + fsync + no-overwrite link + directory fsync. The committed ledger GOVERNS the
host files: outcome_entry derives the OUTCOME mechanically; reconcile refuses any disagreement.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
from pathlib import Path

RUN_STATE, ATTEMPT_LOG = "RUN_STATE.json", "ATTEMPT_LOG.jsonl"
RUN_COMPLETE, RUN_FAILED = "RUN_COMPLETE.json", "RUN_FAILED.json"
SEALS = {"real": ("SCIENTIFIC_RECORD_SEALED.json", "VOID_RECORD_SEALED.json"),
         "manufactured": ("MANUFACTURED_RECORD_SEALED.json", "MANUFACTURED_VOID_RECORD_SEALED.json")}
ALL_SEALS = SEALS["real"] + SEALS["manufactured"]
TERMINALS = (RUN_COMPLETE, RUN_FAILED)
STATE_SCHEMA = "rebaseguard.p5y.k5.cusum-real-point-executor.run-state.v1"
COMPLETE_SCHEMA = "rebaseguard.p5y.k5.cusum-real-point-executor.run-complete.v1"
FAILED_SCHEMA = "rebaseguard.p5y.k5.cusum-real-point-executor.run-failed.v1"
OUTCOME_KEYS = {"event", "slot", "arithmetic_started", "failure_class", "run_failed_sha256", "sealed_record_sha256"}
STATE_KEYS = {"schema", "pid", "argv", "boot_id", "start_epoch", "authorization_sha256", "slot", "attempt_uid",
              "protocol_sha256", "executor_identity_sha256", "mode", "prelaunch_decision", "prelaunch_decision_sha256"}


class MarkerError(RuntimeError):
    pass


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def canonical(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()


def mask_digits(text) -> str:
    """No numbers leave the sealed record: every digit of a free-text failure string is masked."""
    return re.sub(r"\d", "#", str(text))


def boot_id() -> str | None:
    try:
        return Path("/proc/sys/kernel/random/boot_id").read_text().strip()
    except OSError:
        return None


def fsync_dir(path: Path) -> None:
    fd = os.open(str(path), os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def write_new(directory: Path, name: str, obj: dict) -> Path:
    """tmp + fsync + no-overwrite link + directory fsync. Refuses (FileExistsError) if the name already exists."""
    directory = Path(directory)
    final = directory / name
    tmp = directory / f".{name}.{os.getpid()}.tmp"
    data = (json.dumps(obj, indent=1, sort_keys=True) + "\n").encode()
    with open(tmp, "wb") as fh:
        fh.write(data)
        fh.flush()
        os.fsync(fh.fileno())
    try:
        os.link(tmp, final)
    finally:
        os.unlink(tmp)
    fsync_dir(directory)
    return final


def write_terminal(slot: Path, name: str, obj: dict) -> Path:
    """Exactly one terminal marker per attempt: refuse if either terminal marker already exists."""
    if name not in TERMINALS:
        raise MarkerError(f"not a terminal marker: {name}")
    if any((Path(slot) / t).exists() for t in TERMINALS):
        raise MarkerError("DUPLICATE_TERMINAL_MARKER: the attempt already has a terminal marker")
    path = write_new(slot, name, obj)
    if all((Path(slot) / t).exists() for t in TERMINALS):
        raise MarkerError("DUPLICATE_TERMINAL_MARKER: both terminal markers exist")
    return path


def load_json(path: Path):
    """(object, problem). A missing file is (None, None); an unreadable or non-object file is a problem."""
    if not path.exists():
        return None, None
    if path.is_symlink() or not path.is_file():
        return None, f"{path.name} is not a regular file"
    try:
        obj = json.loads(path.read_text())
    except ValueError:
        return None, f"{path.name} malformed"
    return (obj, None) if isinstance(obj, dict) else (None, f"{path.name} is not an object")


def read_events(slot: Path) -> tuple[list, dict]:
    """Parsed ATTEMPT_LOG events. A final partial line (crash while appending) is recorded, not trusted; any other
    unparseable line is a torn log."""
    path = Path(slot) / ATTEMPT_LOG
    info = {"partial_final_line": False, "torn": False}
    if not path.exists():
        return [], info
    raw = path.read_bytes()
    lines = raw.split(b"\n")
    events = []
    for i, line in enumerate(lines):
        if not line.strip():
            continue
        try:
            events.append(json.loads(line))
        except ValueError:
            if i == len(lines) - 1 and not raw.endswith(b"\n"):
                info["partial_final_line"] = True
            else:
                info["torn"] = True
    return events, info


def seal_valid(path: Path, attempt_uid) -> tuple[bool, str]:
    obj, problem = load_json(path)
    if problem or obj is None:
        return False, problem or "missing"
    s = obj.get("scientific")
    if not isinstance(s, dict) or obj.get("scientific_hash") != sha(canonical(s)):
        return False, f"{path.name}: scientific hash does not recompute"
    if attempt_uid is not None and (obj.get("metadata") or {}).get("attempt_uid") != attempt_uid:
        return False, f"{path.name}: sealed for another attempt"
    return True, "ok"


def build_run_state(*, pid, argv, boot, start_epoch, authorization_sha256, slot, attempt_uid, protocol_sha256,
                    executor_identity_sha256, mode, prelaunch_decision=None) -> dict:
    """r4: a governed attempt binds the single authoritative prelaunch decision (EXECUTOR_SPEC_R4.md R4-1); null for the
    non-governed qualification modes."""
    return {"schema": STATE_SCHEMA, "pid": pid, "argv": list(argv), "boot_id": boot, "start_epoch": start_epoch,
            "authorization_sha256": authorization_sha256, "slot": slot, "attempt_uid": attempt_uid,
            "protocol_sha256": protocol_sha256, "executor_identity_sha256": executor_identity_sha256, "mode": mode,
            "prelaunch_decision": prelaunch_decision,
            "prelaunch_decision_sha256": sha(canonical(prelaunch_decision)) if prelaunch_decision is not None else None}


def seal_names(mode: str) -> tuple[str, str]:
    return SEALS["real" if mode == "real" else "manufactured"]


# ------------------------------------------------------------------ slot classification (recovery, D3)
def classify(slot: Path, *, current_boot: str | None, pid_alive_with_argv=None) -> dict:
    """Class A/B/C/D/E of one slot from persisted evidence, plus LIVE and TERMINAL flags. Pure except for the
    liveness probe (exact /proc argv equality), which is only consulted when no terminal marker exists."""
    slot = Path(slot)
    out = {"slot": slot.name, "problems": [], "terminal": None, "live": False, "recovered_evidence": None}
    state, sp = load_json(slot / RUN_STATE)
    if sp:
        out["problems"].append(sp)
    if state is not None and set(state) != STATE_KEYS:
        out["problems"].append("RUN_STATE fields differ from the contract")
    uid = state.get("attempt_uid") if isinstance(state, dict) else None
    mode = state.get("mode") if isinstance(state, dict) else None
    events, info = read_events(slot)
    out["log"] = info
    if info["torn"]:
        out["problems"].append("ATTEMPT_LOG torn")
    names = [e.get("event") for e in events]
    if any(e.get("attempt_uid") != uid for e in events):
        out["problems"].append("ATTEMPT_LOG events from another attempt")
    allowed_orders = ([], ["VALIDATED"], ["VALIDATED", "ARITHMETIC_STARTED"],
                      ["VALIDATED", "ARITHMETIC_STARTED", "SEALED"], ["VALIDATED", "ARITHMETIC_STARTED", "VOID"])
    if names not in [list(o) for o in allowed_orders]:
        out["problems"].append(f"events out of order {names}")
    present = [n for n in ALL_SEALS if (slot / n).exists()]
    sci = [n for n in present if n in (SEALS["real"][0], SEALS["manufactured"][0])]
    void = [n for n in present if n in (SEALS["real"][1], SEALS["manufactured"][1])]
    if sci and void:
        out["problems"].append("SCIENTIFIC_AND_VOID_SEAL_CONFLICT")
    if mode is not None and any(n not in seal_names(mode) for n in present):
        out["problems"].append("seal name does not match the attempt mode")
    for n in present:
        ok, why = seal_valid(slot / n, uid)
        if not ok:
            out["problems"].append(why)
    if present and state is None:
        out["problems"].append("seal without RUN_STATE")
    terms = {}
    for t in TERMINALS:
        obj, tp = load_json(slot / t)
        if tp:
            out["problems"].append(tp)
        if obj is not None:
            terms[t] = obj
            if obj.get("attempt_uid") != uid:
                out["problems"].append(f"{t} belongs to another attempt (stale marker)")
    if len(terms) == 2:
        out["problems"].append("DUPLICATE_TERMINAL_MARKER")
    if RUN_COMPLETE in terms and not sci:
        out["problems"].append("RUN_COMPLETE without a valid scientific seal")
    if sci and RUN_COMPLETE in terms:
        sealed_sha = sha((slot / sci[0]).read_bytes())
        if terms[RUN_COMPLETE].get("sealed_record_sha256") != sealed_sha:
            out["problems"].append("RUN_COMPLETE names another sealed record")
    if RUN_FAILED in terms and sci:
        out["problems"].append("RUN_FAILED beside a scientific seal")
    started = "ARITHMETIC_STARTED" in names or bool(present)
    if out["problems"]:
        cls = "E"
    elif sci:
        cls = "C"
    elif void:
        cls = "D"
    elif started:
        cls = "B"
    else:
        cls = "A"
    out.update({"class": cls, "attempt_uid": uid, "mode": mode, "arithmetic_started": started, "events": names,
                "seals": present, "terminal": sorted(terms) or None})
    if cls != "E" and not terms and state is not None and state.get("boot_id") == current_boot \
            and pid_alive_with_argv is not None and pid_alive_with_argv(state.get("pid"), state.get("argv")):
        out["live"] = True
    return out


def recovery_action(c: dict) -> str:
    """The frozen action per class (EXECUTOR_SPEC_R3.md R3-3)."""
    if c["class"] == "E":
        return "ADJUDICATION_REQUIRED"
    if c["live"]:
        return "LIVE_NO_ACTION"
    if c["terminal"]:
        return "TERMINAL_NO_ACTION"
    return {"A": "WRITE_RUN_FAILED_NOT_STARTED", "B": "WRITE_RUN_FAILED_INTERRUPTED",
            "C": "CONSUME_SEALED_RECORD_WRITE_RUN_COMPLETE_RECOVERED", "D": "WRITE_RUN_FAILED_VOID"}[c["class"]]


# ------------------------------------------------------------------ ledger (D2)
def outcome_entry(slot: Path) -> dict:
    """The OUTCOME ledger entry derived mechanically from the host files (the operator appends exactly this)."""
    import probe_rules as PR
    slot = Path(slot)
    comp, _ = load_json(slot / RUN_COMPLETE)
    fail, _ = load_json(slot / RUN_FAILED)
    if (comp is None) == (fail is None):
        raise MarkerError("slot has no single terminal marker")
    seal = next((n for n in ALL_SEALS if (slot / n).exists()), None)
    if comp is not None:
        return {"event": "OUTCOME", "slot": slot.name, "arithmetic_started": True, "failure_class": "COMPLETED",
                "run_failed_sha256": None, "sealed_record_sha256": comp["sealed_record_sha256"]}
    return {"event": "OUTCOME", "slot": slot.name, "arithmetic_started": fail["arithmetic_started"],
            "failure_class": PR.failure_class(fail.get("supervisor_evidence") or {}),
            "run_failed_sha256": sha((slot / RUN_FAILED).read_bytes()),
            "sealed_record_sha256": sha((slot / seal).read_bytes()) if seal else None}


def reconcile(slot: Path, ledger_entries: list) -> list:
    """Problems between the committed ledger and the host files of one slot (frozen P09 / P11 semantics)."""
    import probe_rules as PR
    slot = Path(slot)
    mine = [e for e in ledger_entries if e.get("slot") == slot.name]
    notices = [e for e in mine if e.get("event") == "LAUNCH_NOTICE"]
    outcomes = [e for e in mine if e.get("event") == "OUTCOME"]
    p = []
    if len(notices) != 1:
        p.append("slot lacks exactly one LAUNCH_NOTICE")
    if len(outcomes) != 1 or set(outcomes[0]) != OUTCOME_KEYS:
        return p + ["slot lacks exactly one well-formed OUTCOME"]
    out = outcomes[0]
    state, _ = load_json(slot / RUN_STATE)
    if notices and state is not None and notices[0].get("authorization_sha256") != state.get("authorization_sha256"):
        p.append("LAUNCH_NOTICE and RUN_STATE name different authorizations")
    try:
        derived = outcome_entry(slot)
    except MarkerError as exc:
        return p + [str(exc)]
    for k in OUTCOME_KEYS:
        if out.get(k) != derived.get(k):
            p.append(f"ledger OUTCOME.{k} disagrees with the host files")
    fail, _ = load_json(slot / RUN_FAILED)
    if fail is not None:
        if fail.get("arithmetic_started") is not out.get("arithmetic_started"):
            p.append("RUN_FAILED.arithmetic_started disagrees with the ledger")
        if PR.failure_class(fail.get("supervisor_evidence") or {}) != out.get("failure_class"):
            p.append("derived failure class disagrees with the ledger")
    seals = [e for e in mine if e.get("event") in ("SCIENTIFIC_RECORD_SEALED", "VOID_RECORD_SEALED")]
    host_seal = next((n for n in ALL_SEALS if (slot / n).exists()), None)
    if host_seal and (len(seals) != 1 or seals[0].get("sha256") != sha((slot / host_seal).read_bytes())):
        p.append("host seal has no matching ledger seal event")
    if not host_seal and (seals or out.get("sealed_record_sha256") is not None):
        p.append("ledger records a seal the host does not hold (a seal even if the host file is gone)")
    return p
