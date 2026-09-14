"""Fixtures of the new-glibc successor SYNTHETIC acceptance. NON-RESULT-BEARING.

  GSCampaign   a synthetic successor campaign: synthetic countersignature fixture, a synthetic copy of the frozen
               successor checkpoint (runtime root replaced), a successor run authorization, gs_supervisor.py
  PredFixture  a synthetic terminal predecessor: provenance-shaped ledger over a 0-based universe, halted by a
               synthetic HOST_DRIFT once `sealed` records exist (one core), never settled (its run stays unsettled)

Settlement: every synthetic ledger is settled ONLY by the sanctioned operator command `gs_entry.py settle` in a fresh
interpreter (sanctioned_settle). The frozen harness settlement helper is disabled here and a source scan refuses any
direct settlement call in the successor tests.

Only synthetic workers run, in scratch roots outside the repository and outside every production runtime root.
"""
from __future__ import annotations

import copy
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
NS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(NS / "code"))
import gs_schema as GS                                                           # noqa: E402
sys.path.insert(0, str(GS.PROD_NS / "tests"))
import acceptance as PA                                                          # noqa: E402  frozen predecessor harness
import gs_authorization as GA                                                    # noqa: E402
import gs_composite as GC                                                        # noqa: E402
import gs_spec as SP                                                             # noqa: E402
import prod_supervisor as PS                                                     # noqa: E402
import prov_integrity as PI                                                      # noqa: E402
import prov_supervisor as PV                                                     # noqa: E402
from prod_common import Refusal, atomic_write_json, canonical, sha256_bytes, sha256_file  # noqa: E402
from prov_authorization import build_authorization as prov_build_authorization  # noqa: E402
from prov_authorization import synthetic_countersignature as prov_synthetic_countersignature  # noqa: E402
from prov_authorization import write_authorization as prov_write_authorization  # noqa: E402

SUPERVISOR = NS / "code/gs_supervisor.py"
ENTRY = NS / "code/gs_entry.py"
check, Fail, expect_refusal, refused_with = PA.check, PA.Fail, PA.expect_refusal, PA.refused_with
attempts, count, forge_next_state = PA.attempts, PA.count, PA.forge_next_state
SCENARIOS: list = []
CACHE: dict = {}
SETTLE_LOG: list = []          # every invocation of the sanctioned settlement command in this acceptance run


def scenario(*covers):
    def deco(fn):
        SCENARIOS.append((fn.__name__, covers, fn))
        return fn
    return deco


def expect_any(codes, fn, *args, **kw):
    try:
        fn(*args, **kw)
    except Refusal as r:
        check(r.code in codes, f"expected one of {codes}, got {r.code}: {r.detail}")
        return r
    raise Fail(f"expected one of {codes}; nothing was refused")


def real_checkpoint() -> tuple[dict, str]:
    return SP.load_checkpoint()


# ====================================================================== the sanctioned settlement command
def _entry_env() -> dict:
    return {k: v for k, v in os.environ.items() if k != PS.KEEPER_ENV}


def sanctioned_settle(target) -> tuple:
    """THE operator command `gs_entry.py settle`, in a fresh interpreter. `--synthetic-spec` only selects which synthetic
    campaign is loaded; the settlement code path is the production one. Returns (exit code, output, report or None)."""
    cfg = target.cfg["config_path"] if hasattr(target, "cfg") else str(target)
    r = subprocess.run([sys.executable, "-B", str(ENTRY), "settle", "--synthetic-spec", cfg], capture_output=True, text=True,
                       timeout=600, env=_entry_env())
    rep = json.loads(r.stdout) if r.returncode == 0 else None
    SETTLE_LOG.append({"config": cfg, "rc": r.returncode, "state": (rep or {}).get("state")})
    return r.returncode, r.stdout + r.stderr, rep


def sanctioned_settle_production() -> tuple:
    """`gs_entry.py settle` against the frozen production checkpoint (refuses: no successor ledger exists)."""
    r = subprocess.run([sys.executable, "-B", str(ENTRY), "settle"], capture_output=True, text=True, timeout=900,
                       env=_entry_env())
    SETTLE_LOG.append({"config": "PRODUCTION", "rc": r.returncode, "state": None})
    return r.returncode, r.stdout + r.stderr


def settle_refused(out: str, code: str) -> bool:
    return f"REFUSED [{code}]" in out


FORBIDDEN_SETTLEMENT_CALLS = tuple("".join(x) for x in ((".set", "tle("), ("recon", "cile("), ("op_settle", "_run("),
                                                        ("op_charge", "_overhead("), ("unmatched", "_overhead(")))
BYPASS_NEGATIVE_TEST_MARKER = "c13_helper"      # the one line that proves the helper is disabled


def settlement_bypass_scan() -> list:
    """No successor test file calls a settlement helper or a frozen settlement transition directly."""
    hits = []
    for f in sorted((NS / "tests").glob("*.py")):
        for i, line in enumerate(f.read_text().splitlines(), 1):
            code = line.split("#", 1)[0]
            if any(t in code for t in FORBIDDEN_SETTLEMENT_CALLS) and BYPASS_NEGATIVE_TEST_MARKER not in line:
                hits.append(f"{f.name}:{i}: {line.strip()[:120]}")
    return hits


def tree_digest(root: Path) -> str:
    """sha256 over every attempt and provenance file (records, envelopes, worker logs) of a runtime root."""
    rows = sorted((str(p.relative_to(root)), sha256_file(p)) for d in ("attempts", "provenance")
                  for p in (Path(root) / d).rglob("*") if p.is_file())
    return sha256_bytes(canonical(rows))


class _Base(PA.Campaign):
    predecessor_shape = False

    def start(self, keep: bool = True):
        self.runs += 1
        log_path = self.dir / f"run{self.runs}.log"
        env = {k: v for k, v in os.environ.items() if k != PS.KEEPER_ENV}
        argv = [sys.executable, "-B", str(SUPERVISOR), "--synthetic-spec", self.cfg["config_path"]]
        argv += ["--predecessor-shape"] if self.predecessor_shape else []
        with open(log_path, "wb") as log:
            p = subprocess.Popen(argv + (["--keep"] if keep else []), stdout=log, stderr=subprocess.STDOUT, env=env,
                                 start_new_session=True)
        p.log_path = log_path
        return p

    def view(self):
        return PI.ledger_view(self.spec)

    def settle(self):
        raise Fail("the frozen harness settlement helper is disabled in the successor acceptance; use gs_entry.py settle")

    def settle_via_entrypoint(self) -> dict:
        rc, out, rep = sanctioned_settle(self)
        check(rc == 0 and rep["state"] == "SETTLED" and not rep["unsettled_after"],
              f"{self.dir.name}: gs_entry.py settle exit {rc}: {out[-400:]}")
        return rep

    def run_complete(self, timeout: float = 600) -> dict:
        """Run to COMPLETE under the keeper, then settle through the sanctioned operator command `gs_entry.py settle`."""
        code, out = self.run(keep=True, timeout=timeout)
        check(code == PS.EXIT_COMPLETE, f"{self.dir.name}: exit {code}: {out[-300:]}")
        return self.settle_via_entrypoint()

    def audit(self):
        return PI.audit(self.spec, self.authz())

    def variant(self, scratch: Path, name: str):
        """A byte copy of the runtime root, verified with the ORIGINAL authorization (which binds the original root)."""
        v = object.__new__(type(self))
        v.dir = scratch / name
        v.dir.mkdir()
        v.cfg = dict(self.cfg, root=str(v.dir / "root"), config_path=str(v.dir / "cfg.json"))
        shutil.copytree(self.root, v.dir / "root")
        v.save()
        v.runs, v.origin = 0, self
        return v

    def authz(self):
        origin = getattr(self, "origin", None)
        return origin.authz() if origin is not None else self._authz()


class GSCampaign(_Base):
    def __init__(self, scratch: Path, name: str, *, countersign: bool = True, authorize: bool = True, **cfg):
        d = scratch / name
        base = {"cells": [128, 129, 130], "checkpoint_path": str(d / "checkpoint.json"),
                "authorization_path": str(d / "auth.json"), "authorization_hash_path": str(d / "auth.hash"),
                "countersignature_path": str(d / "cs.json")}
        base.update(cfg)
        super().__init__(scratch, name, **base)
        cs_sha = "0" * 64
        if countersign:
            data = (json.dumps(GA.synthetic_countersignature(f"SYNTHETIC-{name}"), indent=1, sort_keys=True) + "\n").encode()
            Path(self.cfg["countersignature_path"]).write_bytes(data)
            cs_sha = sha256_bytes(data)
        cp, _sha = real_checkpoint()
        self.cp = copy.deepcopy(cp)
        self.cp.update(runtime_root=self.cfg["root"], countersignature_sha256=cs_sha)
        atomic_write_json(self.cfg["checkpoint_path"], self.cp)
        self.auth = self.auth_sha = None
        if authorize:
            self.auth = GA.build_authorization(self.spec, self.cp, authorization_id=f"SYN-GS-AUTH-{name}",
                                               run_id=f"SYN-GS-RUN-{name}")
            self.auth_sha = GA.write_authorization(self.auth, self.cfg["authorization_path"], self.cfg["authorization_hash_path"])

    @property
    def spec(self):
        return SP.synthetic_drift_spec(self.cfg) if self.cfg.get("drift_after_records") else SP.synthetic_spec(self.cfg)

    def _authz(self):
        from gs_supervisor import synthetic_successor_authz
        return synthetic_successor_authz(self.spec, self.cfg)


class PredFixture(_Base):
    predecessor_shape = True

    def __init__(self, scratch: Path, name: str, *, sealed: int, universe: int, **cfg):
        d = scratch / name
        base = {"predecessor_shape": True, "cells": list(range(universe)), "cores": [0], "drift_after_records": sealed,
                "burn_s": 0.01, "heartbeat_s": 2.0, "authorization_path": str(d / "auth.json"),
                "authorization_hash_path": str(d / "auth.hash"), "countersignature_path": str(d / "cs.json"),
                "freeze_record_sha256": "0" * 64}
        base.update(cfg)
        super().__init__(scratch, name, **base)
        self.sealed = sealed
        auth = prov_build_authorization(self.spec, authorization_id=f"SYN-PRED-AUTH-{name}", run_id=f"SYN-PRED-RUN-{name}", host={})
        sha = prov_write_authorization(auth, self.cfg["authorization_path"], self.cfg["authorization_hash_path"])
        atomic_write_json(self.cfg["countersignature_path"],
                          prov_synthetic_countersignature(auth, sha, freeze_record_sha256=self.cfg["freeze_record_sha256"]))

    @property
    def spec(self):
        return SP.synthetic_drift_spec(self.cfg)

    def _authz(self):
        return PV.synthetic_authz(self.spec, self.cfg)

    def make_terminal(self, timeout: float = 2400):
        code, out = self.run(keep=True, timeout=timeout)
        st = self.state()
        check(code == PS.EXIT_HALTED and (st["halt"] or {}).get("reason") == "HOST_DRIFT"
              and count(st, "SEALED") == self.sealed and not attempts(st, status="RUNNING"),
              f"terminal predecessor fixture: exit {code} halt {st['halt']} sealed {count(st, 'SEALED')}: {out[-300:]}")
        return st

    def tolerance(self) -> dict:
        """Bound at 'binding time', exactly as PREDECESSOR_BINDING.json was collected before any successor object."""
        rep, st = self.audit(), self.state()
        return {"stop": st["halt"], "unsettled_runs": sorted(r for r, x in st["supervisor_runs"].items() if not x["settled"]),
                "pairs_sha256": GC.pairs_digest(rep["pairs"]), "ledger_state_sha256": rep["ledger_state_sha256"],
                "genesis_entry_sha256": rep["genesis_entry_sha256"], "carryover_cells": list(range(self.sealed))}


def composite(pred: PredFixture, succ: GSCampaign | None, tol: dict, *, succ_spec=None, quals=None) -> dict:
    spec = succ_spec or (succ.spec if succ is not None else None)
    exists = succ is not None and (succ.root / "ledger.json").exists()
    return GC.composite_audit(pred_spec=pred.spec, pred_authz=pred.authz(), succ_spec=spec,
                              succ_authz=succ.authz() if exists else None, tolerance=tol,
                              qualification_shas=quals if quals is not None else spec.qualification_record_sha256,
                              successor_ledger_exists=exists)


def full_composite(scratch: Path):
    """One terminal predecessor (0-127 sealed of 0-325) and one COMPLETE successor (128-325), cached per run.

    The successor runs to COMPLETE under its keeper; its frozen audit and the composite are recorded BEFORE settlement
    (never K4-ready), then it is settled by the sanctioned command `gs_entry.py settle`."""
    if "full" not in CACHE:
        pred = PredFixture(scratch, "fx_pred_full", sealed=128, universe=326)
        pred.make_terminal()
        tol = pred.tolerance()
        succ = GSCampaign(scratch, "fx_succ_full", cells=list(range(128, 326)), cores=[0, 2, 4, 6], burn_s=0.01,
                          heartbeat_s=2.0)
        code, out = succ.run(keep=True, timeout=2400)
        check(code == PS.EXIT_COMPLETE, f"successor fixture exit {code}: {out[-300:]}")
        unsettled_audit, unsettled_composite = succ.audit(), composite(pred, succ, tol)
        before = {"issues": sorted(unsettled_audit["issues"]), "ready": unsettled_audit["INTEGRITY_READY_FOR_ADJUDICATION"],
                  "composite": unsettled_composite["state"], "problems": unsettled_composite["problems"],
                  "settle": succ.settle_via_entrypoint()}
        CACHE["full"] = (pred, tol, succ, before)
    return CACHE["full"]


def file_sha_or_none(p: Path):
    return sha256_file(p) if p.is_file() else None
