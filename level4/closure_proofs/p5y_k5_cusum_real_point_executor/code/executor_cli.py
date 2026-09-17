"""Executor child process launched by supervisor.py (EXECUTOR_SPEC_R2.md R2-2).

    python -B code/executor_cli.py real          --output-dir DIR [--authorization-bundle FILE]
    python -B code/executor_cli.py manufactured  --output-dir DIR --fixture-id XF..   (qualification)
    python -B code/executor_cli.py burn          --output-dir DIR --fixture-id XF..   (qualification: CPU-limit / kill tests)

`real` builds the RealInputAdapter binding, CusumPointBackend and the preregistered context, and calls
executor_core.execute. With REAL_INPUT_ARITHMETIC_GUARD = DENY (the frozen policy) it is refused before any backend
method, and the process exits 3 with an EXECUTOR_REFUSAL line. `burn` is a manufactured backend that spends CPU
after ARITHMETIC_STARTED so that the supervisor's RLIMIT_CPU path (SIGXCPU -> VOID seal) and an external kill can be
qualified; it never touches real input. SIGTERM (the supervisor's wall watchdog) raises inside execute, so the executor
seals VOID before exiting.
Exit codes: 0 sealed; 3 refused before arithmetic; 4 failed after ARITHMETIC_STARTED (VOID sealed); 5 other.
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
import hashlib  # noqa: E402
import json  # noqa: E402
import signal  # noqa: E402
from pathlib import Path  # noqa: E402

import paths  # noqa: E402

import executor_core as EC  # noqa: E402


def _on_sigterm(signum, frame):
    raise EC.ExecutorRefusal("WALL_TIMEOUT: terminated by the supervisor watchdog (SIGTERM)")


def context(binding, out: Path, bundle=None) -> EC.ExecutionContext:
    p = EC.prereg()
    return EC.ExecutionContext(k1_binding=binding, output_dir=out, producer_identity_sha256=p["producer_identity_sha256"],
                               protocol_sha256=hashlib.sha256(EC.SCIENCE_FILE.read_bytes()).hexdigest(),
                               runtime_identity_sha256=p["host_runtime_identity_sha256"], authorization_bundle=bundle)


def fixture(fid: str) -> dict:
    proto = json.loads((paths.NS / "config/EXECUTOR_QUALIFICATION_PROTOCOL.json").read_text())
    return next(f for f in proto["fixtures"] if f["id"] == fid)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=("real", "manufactured", "burn"))
    ap.add_argument("--output-dir", required=True)
    ap.add_argument("--fixture-id")
    ap.add_argument("--authorization-bundle")
    a = ap.parse_args(argv)
    signal.signal(signal.SIGTERM, _on_sigterm)
    import backends as B
    import input_adapters as IA
    out = Path(a.output_dir)
    started = False
    try:
        if a.mode == "real":
            bundle = json.loads(Path(a.authorization_bundle).read_text()) if a.authorization_bundle else None
            binding = IA.RealInputAdapter().bind()
            backend, ctx = B.CusumPointBackend(binding), context(binding, out, bundle)
        else:
            spec = fixture(a.fixture_id)
            binding = IA.ManufacturedInputAdapter().bind(spec)
            backend = (B.ManufacturedPointBackend if a.mode == "manufactured" else BurnPointBackend)(spec)
            ctx = context(binding, out)
        record = EC.execute(backend, ctx)
        print(json.dumps({"sealed": True, "scientific_hash": record["scientific_hash"]}), flush=True)
        return 0
    except BaseException as exc:
        log = out / "ATTEMPT_LOG.jsonl"
        started = log.exists() and '"ARITHMETIC_STARTED"' in log.read_text()
        print(f"EXECUTOR_REFUSAL: {type(exc).__name__}: {str(exc)[:400]}", file=sys.stderr, flush=True)
        if not started:
            return 3
        return 4


class BurnPointBackend:
    """QUALIFICATION ONLY (real_input False): spends CPU in the first stage so the CPU limit fires mid-arithmetic."""
    real_input = False
    real_operator = False

    def __init__(self, spec):
        self.spec = dict(spec)

    def describe(self):
        return {"backend": "BurnPointBackend", "fixture": self.spec.get("id")}

    def prepare_point(self, ctx):
        x = 0
        while True:                                  # ended only by SIGXCPU, SIGTERM or SIGKILL
            x = (x * 1103515245 + 12345) % 2147483648


if __name__ == "__main__":
    sys.exit(main())
