"""Strict internal wire helper for the future broker; creates NO authority.

ReceiptTracker records transport observations only. Manager start transaction,
actual peer authentication, held FDs and durable permits are separate native APIs.
No socket, process, cgroup, service or clock calls are made by this module.
"""
from dataclasses import dataclass
import re

VERBS = frozenset(("BIND", "READY", "STOP", "STOP_REQUESTED", "STOP_WRITE_UNKNOWN",
                   "LOCAL_QUIESCENT", "RETIRE", "RETIRING", "GATE_READY", "RELEASE", "CANCEL"))
MAX_PACKET = 96
GENERATION = re.compile(r"[0-9a-f]{32}")


def packet(verb, generation):
    if type(verb) is not str or verb not in VERBS:
        raise ValueError("unsupported verb")
    if type(generation) is not str or GENERATION.fullmatch(generation) is None:
        raise ValueError("invalid generation")
    return (verb+" "+generation+"\n").encode("ascii")


def parse(raw, *, descriptor_count=0, truncated=False, allow_handoff=False):
    if type(raw) is not bytes or not 0 < len(raw) <= MAX_PACKET:
        raise ValueError("invalid packet size/type")
    if type(descriptor_count) is not int or descriptor_count < 0 or type(truncated) is not bool or truncated:
        raise ValueError("truncated or invalid ancillary state")
    if type(allow_handoff) is not bool:
        raise ValueError("handoff policy must be boolean")
    try:
        verb, generation = raw.decode("ascii").removesuffix("\n").split(" ")
    except (UnicodeError, ValueError) as exc:
        raise ValueError("invalid frame") from exc
    if packet(verb, generation) != raw:
        raise ValueError("noncanonical frame")
    expected = 5 if allow_handoff and verb == "BIND" else 0
    if descriptor_count != expected or (allow_handoff and verb != "BIND"):
        raise ValueError("wrong descriptor/operation contract")
    return verb, generation


@dataclass
class ReceiptTracker:
    generation: str
    phase: str = "HANDOFF_PENDING"
    terminal_error: bool = False

    def __post_init__(self):
        packet("BIND", self.generation)

    def receive(self, raw):
        """Observe strict receipt ordering; never returns permission to release.

        A local quiescence receipt does not assert manager cleanup/reaping or
        formal STOPPED. A transport error is permanent for this tracker.
        """
        if self.terminal_error:
            raise ValueError("terminal transport error")
        try:
            verb, generation = parse(raw)
            if generation != self.generation:
                raise ValueError("stale or foreign generation")
            allowed = {
                "HANDOFF_PENDING": {"READY", "STOP_REQUESTED", "STOP_WRITE_UNKNOWN"},
                "READY": {"STOP_REQUESTED", "STOP_WRITE_UNKNOWN"},
                "STOP_REQUESTED": {"LOCAL_QUIESCENT"},
                "LOCAL_QUIESCENT": {"RETIRING"},
                "STOP_WRITE_UNKNOWN": set(), "RETIRING": set(),
            }
            if verb not in allowed[self.phase]:
                raise ValueError("out-of-order receipt")
            self.phase = verb
            return {"generation": generation, "transport_phase": verb,
                    "manager_cleanup_proven": False, "formal_run_authority": False}
        except ValueError:
            self.terminal_error = True
            raise
