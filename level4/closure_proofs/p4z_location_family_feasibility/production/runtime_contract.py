"""P4Z Mac runtime contract -- build, bind and verify the result-bearing host.

The Mac is promoted from exploratory host to result-bearing host by this file.
Everything that could change a floating-point answer is recorded and hashed;
anything that cannot be determined is a hard failure, never a default.

Threading note, specific to this host.  numpy here is built against Apple
**Accelerate**, which does not honour ``OMP_NUM_THREADS`` or
``OPENBLAS_NUM_THREADS`` -- it threads through Grand Central Dispatch and reads
``VECLIB_MAXIMUM_THREADS``.  The P4Z estimators use element-wise ufuncs and
axis reductions only, with no BLAS call on any path, so they are single
threaded regardless; but the contract pins every relevant variable and the
driver *measures* the CPU-to-wall ratio of a probe rather than trusting that
argument.
"""

from __future__ import annotations

import hashlib
import json
import locale
import os
import platform
import subprocess
import sys
import sysconfig
from pathlib import Path

import numpy as np
import scipy

NS = Path(__file__).resolve().parent.parent
CONTRACT_PATH = NS / "production" / "mac_runtime_contract.json"

#: Environment variables pinned for every result-bearing process.  VECLIB is
#: the one that actually binds on this host; the others are pinned so that the
#: contract stays correct if the wheel is ever rebuilt against OpenBLAS or MKL.
REQUIRED_ENV = {
    "OMP_NUM_THREADS": "1",
    "OPENBLAS_NUM_THREADS": "1",
    "MKL_NUM_THREADS": "1",
    "VECLIB_MAXIMUM_THREADS": "1",
    "NUMEXPR_NUM_THREADS": "1",
    "PYTHONHASHSEED": "0",
    "LC_ALL": "C",
}


class RuntimeContractError(RuntimeError):
    """Fail-closed: the host's identity could not be established."""


def _sysctl(name: str) -> str:
    out = subprocess.run(["sysctl", "-n", name], capture_output=True, text=True)
    if out.returncode != 0 or not out.stdout.strip():
        raise RuntimeContractError(f"sysctl {name} unavailable")
    return out.stdout.strip()


def _sw_vers() -> dict[str, str]:
    out = subprocess.run(["sw_vers"], capture_output=True, text=True)
    if out.returncode != 0:
        raise RuntimeContractError("sw_vers unavailable")
    fields = {}
    for line in out.stdout.splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            fields[key.strip()] = value.strip()
    for key in ("ProductName", "ProductVersion", "BuildVersion"):
        if key not in fields:
            raise RuntimeContractError(f"sw_vers missing {key}")
    return fields


def _blas_identity() -> dict[str, str]:
    try:
        cfg = np.show_config(mode="dicts")
    except Exception as exc:  # noqa: BLE001 - re-raised as a contract failure
        raise RuntimeContractError(f"numpy build configuration unavailable: {exc}")
    deps = cfg.get("Build Dependencies", {})
    blas, lapack = deps.get("blas", {}), deps.get("lapack", {})
    if not blas.get("found") or not lapack.get("found"):
        raise RuntimeContractError("numpy reports no BLAS/LAPACK backend")
    compilers = cfg.get("Compilers", {}).get("c", {})
    return {
        "blas_name": str(blas.get("name")),
        "blas_version": str(blas.get("version")),
        "blas_detection_method": str(blas.get("detection method")),
        "lapack_name": str(lapack.get("name")),
        "numpy_c_compiler": str(compilers.get("name")),
        "numpy_c_compiler_version": str(compilers.get("version")),
        "honours_omp_num_threads": str(blas.get("name")).lower() != "accelerate",
        "thread_variable_that_binds":
            "VECLIB_MAXIMUM_THREADS" if str(blas.get("name")).lower() == "accelerate"
            else "OMP_NUM_THREADS",
    }


def _package_lock() -> dict[str, str]:
    """Versions of every package that can reach a scientific number."""
    import pytest  # noqa: PLC0415 - deliberately late, it is not a run-time dep

    return {
        "numpy": np.__version__,
        "scipy": scipy.__version__,
        "pytest": pytest.__version__,
    }


def _float_environment() -> dict[str, object]:
    finfo = np.finfo(np.float64)
    return {
        "float64_eps": float(finfo.eps),
        "float64_max": float(finfo.max),
        "float64_tiny": float(finfo.tiny),
        "numpy_errstate": {k: str(v) for k, v in np.geterr().items()},
        "float_repr_style": sys.float_repr_style,
        "byte_order": sys.byteorder,
        "fpu_mode_note":
            "no P4Z code alters the rounding mode, enables FTZ/DAZ, or uses "
            "fast-math; all arithmetic is IEEE-754 binary64 round-to-nearest",
    }


def build() -> dict[str, object]:
    """Assemble the contract.  Raises RuntimeContractError if anything is unknown."""
    physical = int(_sysctl("hw.physicalcpu"))
    logical = int(_sysctl("hw.logicalcpu"))
    try:
        perf = int(_sysctl("hw.perflevel0.physicalcpu"))
        eff = int(_sysctl("hw.perflevel1.physicalcpu"))
    except RuntimeContractError:
        perf, eff = physical, 0
    os_fields = _sw_vers()

    contract = {
        "schema": "rebaseguard.p4z-mac-runtime-contract.v1",
        "role": "RESULT_BEARING_HOST",
        "declaration": {
            "P4Z_NUMERICAL_HOST": "LOCAL_MAC",
            "AWS_CPU_USED_BY_P4Z": 0,
            "campaign_isolation": "MAC_ONLY",
        },
        "machine": {
            "architecture": platform.machine(),
            "cpu_brand": _sysctl("machdep.cpu.brand_string"),
            "physical_cores": physical,
            "logical_cores": logical,
            "performance_cores": perf,
            "efficiency_cores": eff,
            "simultaneous_multithreading": logical > physical,
            "memory_bytes": int(_sysctl("hw.memsize")),
            "cacheline_bytes": int(_sysctl("hw.cachelinesize")),
        },
        "operating_system": {
            "product": os_fields["ProductName"],
            "version": os_fields["ProductVersion"],
            "build": os_fields["BuildVersion"],
            "kernel": platform.version(),
            "release": platform.release(),
        },
        "python": {
            "version": platform.python_version(),
            "build": list(platform.python_build()),
            "compiler": platform.python_compiler(),
            "implementation": platform.python_implementation(),
            "executable": sys.executable,
            "abiflags": getattr(sys, "abiflags", ""),
            "config_CFLAGS": sysconfig.get_config_var("CFLAGS") or "",
            "config_OPT": sysconfig.get_config_var("OPT") or "",
            "maxsize": sys.maxsize,
        },
        "numerical_backend": _blas_identity(),
        "package_lock": _package_lock(),
        "threading_environment": dict(REQUIRED_ENV),
        "locale": {
            "preferred_encoding": locale.getpreferredencoding(False),
            "LC_ALL_required": REQUIRED_ENV["LC_ALL"],
            "filesystem_encoding": sys.getfilesystemencoding(),
        },
        "floating_point": _float_environment(),
    }
    return contract


def canonical(contract: dict[str, object]) -> str:
    return json.dumps(contract, indent=2, sort_keys=True, ensure_ascii=True)


def runtime_hash(contract: dict[str, object]) -> str:
    body = {k: v for k, v in contract.items() if k != "runtime_hash"}
    return hashlib.sha256(canonical(body).encode()).hexdigest()


def enforce_environment() -> None:
    """Fail closed unless the process was started with the pinned environment."""
    wrong = {k: os.environ.get(k) for k, v in REQUIRED_ENV.items()
             if os.environ.get(k) != v}
    if wrong:
        raise RuntimeContractError(
            "result-bearing execution requires the pinned threading/locale "
            f"environment; wrong or missing: {wrong}"
        )


def verify(path: Path = CONTRACT_PATH) -> dict[str, object]:
    """Rebuild the contract and compare it against the frozen one."""
    if not path.exists():
        raise RuntimeContractError(f"no frozen runtime contract at {path}")
    frozen = json.loads(path.read_text())
    stored = frozen.get("runtime_hash")
    if not stored:
        raise RuntimeContractError("frozen contract carries no runtime_hash")
    if runtime_hash(frozen) != stored:
        raise RuntimeContractError("frozen contract's own runtime_hash does not match")
    current = build()
    for section in ("machine", "operating_system", "python", "numerical_backend",
                    "package_lock", "threading_environment", "floating_point"):
        if current[section] != frozen[section]:
            diff = {k: (frozen[section].get(k), current[section].get(k))
                    for k in set(frozen[section]) | set(current[section])
                    if frozen[section].get(k) != current[section].get(k)}
            raise RuntimeContractError(
                f"runtime drift in {section!r}: frozen vs current {diff}")
    return frozen


def main() -> int:
    enforce_environment()
    contract = build()
    contract["runtime_hash"] = runtime_hash(contract)
    CONTRACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONTRACT_PATH.write_text(canonical(contract) + "\n")
    print(f"runtime_hash = {contract['runtime_hash']}")
    print(f"-> {CONTRACT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
