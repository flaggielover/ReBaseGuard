"""Executor child process launched by supervisor.py (EXECUTOR_SPEC_R2.md R2-2, EXECUTOR_SPEC_R3.md R3-1 / R3-2).

    python -B code/executor_cli.py real          --output-dir SLOT --attempt-uid U --decision-sha256 D
    python -B code/executor_cli.py governed_manufactured --output-dir SLOT --attempt-uid U --decision-sha256 D
                                                 --fixture-id XF..   (qualification: the governed path, manufactured input)
    python -B code/executor_cli.py manufactured  --output-dir SLOT --attempt-uid U --fixture-id XF..   (qualification)
    python -B code/executor_cli.py burn          --output-dir SLOT --attempt-uid U --fixture-id XF..   (qualification)
    python -B code/executor_cli.py diskfull      --output-dir SLOT --attempt-uid U --fixture-id XF..   (qualification)

`real` builds the RealInputAdapter binding, CusumPointBackend and the preregistered context. Its executor binding is
the sha256 of the protocol's EXECUTION_BINDING_AMENDMENT.json file bytes (or UNBOUND when it does not exist). The
authorization decision was taken ONCE by the supervisor before the slot existed (EXECUTOR_SPEC_R4.md R4-1); this child
only re-checks, purely, that it matches the decision bound in RUN_STATE (digest passed as --decision-sha256). It never
calls the verifier, and there is no option to pass an authorization object or a verifier report. With
REAL_INPUT_ARITHMETIC_GUARD = DENY (the frozen policy) it is refused before any backend method and exits 3.

Signals: SIGXCPU (RLIMIT_CPU soft) -> CPU_RLIMIT inside execute (VOID); SIGUSR1 is the supervisor watchdog's wall signal
-> WALL_TIMEOUT inside execute (VOID). SIGTERM / SIGINT / SIGKILL keep their default meaning (external kill: no seal).
`burn` spends CPU after ARITHMETIC_STARTED; `diskfull` raises ENOSPC after it (transient: no seal). Neither touches real
input. Exit codes: 0 sealed; 3 refused before arithmetic; 4 failed after ARITHMETIC_STARTED.
"""
from __future__ import annotations

import os
import sys

_PINNED = {"OMP_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1", "MKL_NUM_THREADS": "1", "NUMEXPR_NUM_THREADS": "1"}
if "numpy" in sys.modules:
    raise RuntimeError("numpy imported before the thread contract was pinned")
os.environ.update(_PINNED)
os.environ["K1_THREADS_PINNED"] = "1"

import argparse  # noqa: E402
import errno  # noqa: E402
import hashlib  # noqa: E402
import json  # noqa: E402
import signal  # noqa: E402
from pathlib import Path  # noqa: E402

import paths  # noqa: E402

import executor_core as EC  # noqa: E402


def _on_wall(signum, frame):
    raise EC.ExecutorRefusal("WALL_TIMEOUT: wall limit reached (supervisor watchdog)")


def context(binding, out: Path, attempt_uid, executor_binding_sha256="UNBOUND_QUALIFICATION",
            decision_sha256=None) -> EC.ExecutionContext:
    return EC.standard_context(binding, out, attempt_uid=attempt_uid, executor_binding_sha256=executor_binding_sha256,
                               prelaunch_decision_sha256=decision_sha256)


def fixture(fid: str) -> dict:
    proto = json.loads((paths.NS / "config/EXECUTOR_QUALIFICATION_PROTOCOL.json").read_text())
    return next(f for f in proto["fixtures"] if f["id"] == fid)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=("real", "governed_manufactured", "manufactured", "burn", "diskfull"))
    ap.add_argument("--output-dir", required=True)
    ap.add_argument("--attempt-uid", required=True)
    ap.add_argument("--fixture-id")
    ap.add_argument("--decision-sha256")
    a = ap.parse_args(argv)
    signal.signal(signal.SIGUSR1, _on_wall)
    import backends as B
    import input_adapters as IA
    out = Path(a.output_dir)
    try:
        if a.mode == "real":
            binding = IA.RealInputAdapter().bind()
            backend = B.CusumPointBackend(binding)
            ctx = context(binding, out, a.attempt_uid, EC.amendment_binding(), a.decision_sha256)
        elif a.mode == "governed_manufactured":
            spec = fixture(a.fixture_id)
            binding = IA.ManufacturedInputAdapter().bind(spec)
            backend = B.ManufacturedPointBackend(spec)
            backend.governed = True                   # the governed path: permission required, supervisor required
            ctx = context(binding, out, a.attempt_uid, EC.amendment_binding(), a.decision_sha256)
        else:
            spec = fixture(a.fixture_id)
            binding = IA.ManufacturedInputAdapter().bind(spec)
            backend = {"manufactured": B.ManufacturedPointBackend, "burn": BurnPointBackend,
                       "diskfull": DiskFullPointBackend}[a.mode](spec)
            ctx = context(binding, out, a.attempt_uid)
        record = EC.execute(backend, ctx)
        print(json.dumps({"sealed": True, "scientific_hash": record["scientific_hash"]}), flush=True)
        return 0
    except BaseException as exc:
        log = out / "ATTEMPT_LOG.jsonl"
        started = log.exists() and '"ARITHMETIC_STARTED"' in log.read_text()
        print(f"EXECUTOR_REFUSAL: {type(exc).__name__}: {EC.mask(str(exc)[:400])}", file=sys.stderr, flush=True)
        return 4 if started else 3


class BurnPointBackend:
    """QUALIFICATION ONLY (real_input False): spends CPU in the first stage so a limit fires mid-arithmetic."""
    real_input = False
    real_operator = False

    def __init__(self, spec):
        self.spec = dict(spec)

    def describe(self):
        return {"backend": "BurnPointBackend", "fixture": self.spec.get("id")}

    def prepare_point(self, ctx):
        x = 0
        while True:                                  # ended only by SIGXCPU, SIGUSR1, SIGTERM or SIGKILL
            x = (x * 1103515245 + 12345) % 2147483648


class DiskFullPointBackend(BurnPointBackend):
    """QUALIFICATION ONLY (real_input False): the first stage fails with ENOSPC after ARITHMETIC_STARTED."""

    def describe(self):
        return {"backend": "DiskFullPointBackend", "fixture": self.spec.get("id")}

    def prepare_point(self, ctx):
        raise OSError(errno.ENOSPC, "No space left on device")


if __name__ == "__main__":
    sys.exit(main())
