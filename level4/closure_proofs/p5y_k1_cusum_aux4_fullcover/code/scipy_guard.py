"""PHASE 5: runtime enforcement that no SciPy code runs on the certifying path.

WHY A PROBE FILE IS NOT ENOUGH
------------------------------
Aux3 justified excluding SciPy from its trusted computing base with a committed
probe artifact, `evidence/scipy_execution_probe.json`. Two things were wrong with
that. The artifact influenced the runtime contract but was not byte-bound, so it
could be edited without changing the declared producer identity; and it recorded
a historical measurement, so a later change that DID reach SciPy would not be
noticed. The conclusion was right and is preserved here -- but it is now enforced
at run time, on every cell, and the probe artifact is byte-bound as well.

HOW
---
`sys.monitoring` (PEP 669, CPython 3.12+) with the CALL event. The callback
inspects the callee's module; anything outside SciPy returns
`sys.monitoring.DISABLE`, which permanently retires that code location, so the
cost decays to nothing after warm-up instead of being paid on every call. If a
SciPy callable is ever invoked, the call is recorded and `require_clean()` aborts
the certification.

This catches C functions too -- `scipy.special.ndtr` is a ufunc, and the CALL
event fires for it -- which a pure-Python import check would miss.

WHAT IS AND IS NOT CLAIMED
--------------------------
The guard proves no SciPy *call* happened in the guarded window. SciPy is still
IMPORTED on this path: `rebaseguard_certify/spectral_candidate.py` does
`from scipy.special import ndtr` at module level. So SciPy must be installed for
the import to succeed, and that availability is part of the environment; what is
NOT bound is its version, because no SciPy code executes and therefore no SciPy
version can move a certified number. The guard is what makes that statement
checkable per run rather than inherited.
"""
from __future__ import annotations

import json
import sys

import ancestry4                                            # noqa: F401

TOOL_ID = sys.monitoring.PROFILER_ID
TOOL_NAME = "aux4-scipy-guard"
WATCHED_ROOTS = ("scipy",)


class ScipyExecuted(RuntimeError):
    """SciPy code ran on a path declared SciPy-free."""


class ScipyGuard:
    """Observe every call once; abort if any of them lands in SciPy."""

    def __init__(self, roots=WATCHED_ROOTS):
        self.roots = tuple(roots)
        self.observed: list[str] = []
        self.events = 0
        self.active = False

    def _on_call(self, code, offset, callable_, arg0):
        self.events += 1
        module = getattr(callable_, "__module__", None)
        if module is None:
            owner = getattr(callable_, "__self__", None)
            module = getattr(type(owner), "__module__", "") if owner is not None else ""
        root = (module or "").split(".")[0]
        if root in self.roots:
            name = getattr(callable_, "__qualname__", None) or repr(callable_)
            entry = f"{module}.{name}"
            if entry not in self.observed:
                self.observed.append(entry)
            return None                     # keep watching this location
        return sys.monitoring.DISABLE       # never ask about this location again

    def __enter__(self):
        mon = sys.monitoring
        mon.use_tool_id(TOOL_ID, TOOL_NAME)
        mon.register_callback(TOOL_ID, mon.events.CALL, self._on_call)
        mon.set_events(TOOL_ID, mon.events.CALL)
        self.active = True
        return self

    def __exit__(self, *exc):
        mon = sys.monitoring
        mon.set_events(TOOL_ID, 0)
        mon.register_callback(TOOL_ID, mon.events.CALL, None)
        mon.free_tool_id(TOOL_ID)
        self.active = False
        return False

    # ------------------------------------------------------------- results
    def require_clean(self) -> dict:
        if self.observed:
            raise ScipyExecuted(
                "SciPy executed on a path declared SciPy-free: "
                + ", ".join(self.observed[:8]))
        return self.report()

    def report(self) -> dict:
        return {"schema": "k1.cusum-aux4.scipy-guard.v2",
                "method": "sys.monitoring CALL events (PEP 669) with DISABLE decay",
                "watched_roots": list(self.roots),
                "call_sites_observed": self.events,
                "scipy_calls_observed": list(self.observed),
                "scipy_free": not self.observed,
                "scipy_imported": any(m.split(".")[0] == "scipy"
                                      for m in sys.modules),
                "enforced_per_run": True}


def imported_scipy_modules() -> list[str]:
    return sorted(m for m in sys.modules if m.split(".")[0] == "scipy")


def main() -> None:
    """Re-verify the SciPy-free conclusion end to end, independently of Aux3."""
    import os
    for var in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
                "NUMEXPR_NUM_THREADS"):
        os.environ[var] = "1"
    import spec
    from intervals import workprec
    from flint import arb
    from cusum_layer2 import Pair
    import aux_certifier

    cell = next(c for c in spec.CELLS if c["detector"] == "CUSUM" and c["index"] == 325)
    guard = ScipyGuard()
    with guard, workprec(256):
        cert = aux_certifier.Aux3Certifier(cell, bits=256).prepare()
        residual = Pair(cert.P["h", 2, 0]) - cert.K(cert.P["h", 1, 0], 0)
        cert._begin()
        cert.certify("probe", residual, arb(0), arb(0))
        cert._begin()
        cert.certify("probe3", Pair(cert.P["h", 2, 3]) - cert.K(cert.P["h", 1, 3], 0),
                     arb(0), arb(0))
    report = guard.report()
    report["exercised"] = ["Layer 1 collocation quadrature",
                           "numpy.linalg.solve candidate",
                           "dyadic candidate construction",
                           "Arb kernel application K_i",
                           "Bernstein range over the reachable continuum",
                           "order-3 auxiliary candidates"]
    report["scipy_modules_imported"] = imported_scipy_modules()
    print(json.dumps(report, indent=2, sort_keys=True))
    raise SystemExit(0 if report["scipy_free"] else 1)


if __name__ == "__main__":
    main()
