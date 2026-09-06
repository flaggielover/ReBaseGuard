"""PHASE 4: the complete runtime and numerical-backend identity.

WHY AUX3'S RUNTIME BINDING WAS INSUFFICIENT -- MEASURED, NOT ARGUED
------------------------------------------------------------------
Aux3 bound `numpy_version`, `python_flint_version`, the CPython major.minor and
the thread contract. That is not enough. The wheel's OpenBLAS is built
`DYNAMIC_ARCH`, so it selects a microkernel at RUNTIME from the detected CPU.
Forcing the selection on this very host, with everything Aux3 binds held fixed:

    OPENBLAS_CORETYPE=SkylakeX   vs   OPENBLAS_CORETYPE=Haswell
    -> 62 of 240 certified dyadic candidates DIFFER
       (cells 0, 150, 318, 325; sampled families h, S, F, D, H, W)

The float candidate solve goes through `numpy.linalg.solve`; a different kernel
sums in a different order, the candidate moves, and every certified residual
computed against that candidate moves with it. Two hosts carrying Aux3's exact
declared producer identity therefore produce different certificates. That is the
adjudicated RUNTIME_BINDING = FAIL, and it is also the mechanism behind
CERTIFICATE_DETERMINISM = FAIL.

Note also that `numpy.show_config()` reports the build-time default target
("Haswell" here) while the runtime selection is "SkylakeX". Binding the build
string alone would record the wrong fact.

WHAT IS BOUND, AND WHY EACH ITEM CAN MOVE A CERTIFIED NUMBER
------------------------------------------------------------
  openblas_runtime_corename   selects the GEMM/LAPACK microkernel  -> candidate
  openblas_config             build flags, interface width, threading model
  openblas_library_sha256     the exact library bytes actually mapped
  numpy_version               reduction order and lapack_lite behaviour
  python_flint_version        the ball-arithmetic wrapper
  flint/gmp/mpfr sha256       the exact Arb/FLINT backend bytes: every certified
                              interval endpoint is produced by these
  cpython_version + build     float parsing/formatting, dict/set iteration order
  thread contract             BLAS reduction order (already known from Gate 2C)
  precision_bits              256, frozen
  collocation degree/quadrature/subdivision, taylor order   frozen inputs

WHAT IS DELIBERATELY NOT BOUND
------------------------------
The CPU model string, hostname, PID, cgroup limits, wall time and free memory.
The CPU model is what OpenBLAS *reads* to choose a kernel, but it is the chosen
kernel that changes arithmetic; binding both would reject a legitimate host whose
different CPU selects the same kernel. `scipy_version` is not bound either -- see
`scipy_guard`: SciPy is imported but never called, and the guard enforces that at
runtime rather than trusting the version.
"""
from __future__ import annotations

import ctypes
import hashlib
import json
import os
import platform
import sys
from pathlib import Path

import ancestry4

SCHEMA = "k1.cusum-aux4.runtime-contract.v2"

# Backend shared objects whose bytes produce every certified number.
BACKEND_LIBRARY_GLOBS = (
    "level4/.venv/lib/python3.12/site-packages/python_flint.libs/libflint-*.so*",
    "level4/.venv/lib/python3.12/site-packages/python_flint.libs/libgmp-*.so*",
    "level4/.venv/lib/python3.12/site-packages/python_flint.libs/libmpfr-*.so*",
    "level4/.venv/lib/python3.12/site-packages/numpy.libs/libscipy_openblas64_-*.so",
)

THREAD_VARS = ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
               "NUMEXPR_NUM_THREADS")

# scipy_openblas64 exports its symbols with a 64-bit suffix.
_OPENBLAS_SYMBOLS = (("scipy_openblas_get_config64_", "openblas_config"),
                     ("scipy_openblas_get_corename64_", "openblas_runtime_corename"))


class RuntimeMismatch(RuntimeError):
    """The live runtime does not match the committed runtime contract."""


def sha256_file(path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def backend_libraries() -> dict:
    """repo-relative path -> sha256 for every numerical backend library."""
    out = {}
    for pattern in BACKEND_LIBRARY_GLOBS:
        for p in sorted(ancestry4.ROOT.glob(pattern)):
            out[str(p.relative_to(ancestry4.ROOT))] = sha256_file(p)
    return dict(sorted(out.items()))


def openblas_identity() -> dict:
    """The RUNTIME-selected OpenBLAS kernel, read from the mapped library."""
    import numpy                                             # noqa: F401
    with open("/proc/self/maps") as fh:
        lines = fh.read().splitlines()
    mapped = sorted({l.split()[-1] for l in lines
                     if l.split()[-1].startswith("/")
                     and "openblas" in l.split()[-1].lower()})
    out = {"openblas_libraries_mapped": [
        str(Path(p).resolve().relative_to(ancestry4.ROOT))
        if str(p).startswith(str(ancestry4.ROOT)) else p for p in mapped]}
    if not mapped:
        raise RuntimeMismatch("no OpenBLAS library is mapped; cannot identify the "
                              "numerical backend that produces the candidate")
    lib = ctypes.CDLL(mapped[0])
    for symbol, key in _OPENBLAS_SYMBOLS:
        f = getattr(lib, symbol)
        f.restype = ctypes.c_char_p
        f.argtypes = []
        out[key] = f().decode()
    out["openblas_coretype_env"] = os.environ.get("OPENBLAS_CORETYPE")
    return out


def contract() -> dict:
    """The complete runtime identity of THIS process."""
    import numpy
    import flint
    import spec

    ob = openblas_identity()
    return {
        "schema": SCHEMA,
        "cpython_version": platform.python_version(),
        "cpython_version_full": sys.version,
        "cpython_build": list(platform.python_build()),
        "cpython_compiler": platform.python_compiler(),
        "cpython_implementation": platform.python_implementation(),
        "platform_machine": platform.machine(),
        "libc": list(platform.libc_ver()),
        "numpy_version": numpy.__version__,
        "python_flint_version": flint.__version__,
        "openblas_runtime_corename": ob["openblas_runtime_corename"],
        "openblas_config": ob["openblas_config"],
        "openblas_coretype_env": ob["openblas_coretype_env"],
        "backend_libraries": backend_libraries(),
        "thread_environment": {v: os.environ.get(v) for v in THREAD_VARS},
        "flint_threads": 1,
        "precision_bits": spec.PRODUCTION_BITS,
        "taylor_order": 120,
        "collocation_degree": 12,
        "collocation_quadrature": 400,
        "subdivision_depth": 0,
    }


def contract_hash(c: dict | None = None) -> str:
    c = contract() if c is None else c
    return hashlib.sha256(
        (json.dumps(c, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
         + "\n").encode("ascii")).hexdigest()


def compare(committed: dict) -> list[str]:
    """Every way the live runtime differs from the committed contract."""
    live = contract()
    problems = []
    keys = set(committed) | set(live)
    for key in sorted(keys):
        if key == "openblas_coretype_env":
            # The env var is recorded for diagnosis; what binds is the kernel it
            # selected, which is compared as `openblas_runtime_corename`.
            continue
        if committed.get(key) != live.get(key):
            problems.append(f"runtime {key}: live {live.get(key)!r} != "
                            f"committed {committed.get(key)!r}")
    return problems


def require(committed: dict) -> dict:
    problems = compare(committed)
    if problems:
        raise RuntimeMismatch("; ".join(problems[:6]))
    for var in THREAD_VARS:
        if os.environ.get(var) != "1":
            raise RuntimeMismatch(
                f"threading contract violated: {var}={os.environ.get(var)!r}")
    return {"runtime_contract_hash": contract_hash(committed),
            "runtime_contract_schema": SCHEMA}


def main() -> None:
    print(json.dumps({"contract": contract(), "hash": contract_hash()},
                     indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
