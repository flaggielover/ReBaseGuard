"""The provenance-successor supervisor: the predecessor supervisor with an authorization-gated genesis and envelope
binding. NON-CERTIFYING.

Differences from the predecessor supervisor (everything else, including admission, drain, the cap invariant, crash
reconciliation and the keeper, is the predecessor's unchanged code):
  1  the verified run authorization + independent countersignature are loaded BEFORE the ledger is opened; without
     them no ledger is created and nothing is admitted
  2  the ledger is a ProvenanceLedger: its genesis carries the authorization block; an existing ledger not born under
     this authorization is refused
  3  immediately after every SEALED attempt the envelope is derived, verified as a pair, and bound (PROVENANCE_BOUND)
  4  on start, and before any disposition is recorded, every sealed-but-unbound attempt is bound

  python prov_supervisor.py --synthetic-spec CFG.json [--keep]      synthetic acceptance only
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import prov_schema as S                                                      # noqa: E402
import prod_ledger as L                                                      # noqa: E402
import prod_supervisor as PS                                                 # noqa: E402
import prov_ledger as PL                                                     # noqa: E402
from prod_common import Refusal                                              # noqa: E402
from prov_authorization import load_authz                                    # noqa: E402
from prov_envelope import check_genesis                                      # noqa: E402
from prov_spec import synthetic_spec                                         # noqa: E402


class ProvenanceSupervisor(PS.Supervisor):
    def __init__(self, spec, *, authz_loader, preflight=None):
        super().__init__(spec, preflight=preflight)
        self.authz_loader, self.authz = authz_loader, None

    def _run_locked(self, lock) -> int:
        spec = self.spec
        probe_usec = 0
        if self.preflight is not None:
            ready, report, probe_usec = self.preflight()
            if not ready:
                PS.log("NOT_READY", failures=[c for c in report["checks"] if c["status"] != "PASS"])
                return PS.EXIT_REFUSED
        self.authz = self.authz_loader()            # refuses (e.g. COUNTERSIGNATURE_MISSING) before any ledger exists
        if L.Paths(spec.root).drain.exists():
            raise Refusal("DRAIN_PRESENT", "a DRAIN marker is present; remove it explicitly before relaunching")
        led = PL.ProvenanceLedger(spec, lock, run_id=self.run_id, authz=self.authz)
        relation = led.open(allow_genesis=True)
        check_genesis(led.state, L.Ledger.read_journal(led.p.journal)[0], self.authz)
        sealed = L.verify_sealed_evidence(spec, led.state)
        bound = PL.verify_bound_envelopes(spec, led.state)
        st = led.state
        in_flight = any(a["status"] in L.OPEN for a in st["attempts"].values())
        if st["disposition"] in L.TERMINAL and not in_flight and not PL.unbound_sealed(st):
            PS.log("TERMINAL", disposition=st["disposition"], halt=st["halt"])
            return PS.EXIT_FOR[st["disposition"]]
        reaped, unreadable = L.read_reaper(led.p)
        overhead = L.unmatched_overhead(reaped, st)
        led.txn("RUN_OPENED", lambda s: L.op_run_open(s, self.run_id, os.getpid(), probe_usec, overhead),
                {"run_id": self.run_id, "relation": relation})
        report = L.reconcile(led, reaped, unreadable)
        recovered = []
        for aid in PL.unbound_sealed(led.state):
            PL.bind_envelope(led, self.authz, aid)
            recovered.append(aid)
        PS.log("OPENED", run_id=self.run_id, relation=relation, sealed_verified=sealed, envelopes_verified=bound,
               reconciled=report, envelopes_bound_on_start=recovered, authorization=self.authz.block)
        if led.state["disposition"] in L.TERMINAL and not any(a["status"] in L.OPEN for a in led.state["attempts"].values()):
            return self._finish(led, led.state["disposition"], budget=led.state["budget_exhaustion"])
        return self._loop(led)

    def _finalize(self, led, aid: str, status: int, ru) -> None:
        super()._finalize(led, aid, status, ru)
        if led.state["attempts"][aid]["status"] == "SEALED":
            prov = PL.bind_envelope(led, self.authz, aid)
            PS.log(S.PROVENANCE_EVENT, attempt=aid, envelope_sha256=prov["envelope_sha256"])

    def _finish(self, led, disposition: str, budget=None) -> int:
        for aid in PL.unbound_sealed(led.state):
            PL.bind_envelope(led, self.authz, aid)
        return super()._finish(led, disposition, budget=budget)


def synthetic_authz(spec, cfg: dict):
    return load_authz(spec, auth_path=cfg["authorization_path"], hash_path=cfg["authorization_hash_path"],
                      cs_path=cfg["countersignature_path"], freeze_record_sha256=cfg["freeze_record_sha256"])


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="CUSUM Aux5 provenance supervisor (synthetic acceptance entry)")
    ap.add_argument("--synthetic-spec", required=True)
    ap.add_argument("--keep", action="store_true")
    a = ap.parse_args(argv)
    cfg = json.loads(Path(a.synthetic_spec).read_text())
    spec = synthetic_spec(cfg)
    if a.keep:
        return PS.keep([sys.executable, "-B", str(Path(__file__).resolve()), "--synthetic-spec", a.synthetic_spec],
                       root=spec.root)
    return ProvenanceSupervisor(spec, authz_loader=lambda: synthetic_authz(spec, cfg)).run()


if __name__ == "__main__":
    raise SystemExit(main())
