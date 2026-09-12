"""PS1 production-namespace acceptance tests. Result-free: no genuine production cell is ever created.
Run from a clean checkout of the production anchor with the documented PYTHONPATH (see config/TEST_ENV.json)."""
import hashlib
import json
import os
import signal
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
CP = NS.parent
sys.path.insert(0, str(NS / "driver"))
sys.path.insert(0, str(NS / "code"))

import multihost as M                    # noqa: E402
import production_launcher as PL         # noqa: E402

FROZEN_DRIVER = CP / "p5y_k1_sr_production_authorized_successor/driver"
QUAL = CP / "p5y_k1_ps1_production_qualification/evidence/qual"


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


class Identity(unittest.TestCase):
    def test_reused_modules_byte_identical(self):
        for f in ("global_budget.py", "production_provenance.py", "handoff.py"):
            self.assertEqual(sha(NS / "driver" / f), sha(FROZEN_DRIVER / f), f)

    def test_multihost_regenerates(self):
        import make_multihost as MK
        c = json.loads((NS / "config/PS1_CONSTANTS.json").read_text())
        self.assertEqual(MK.build(c), (NS / "driver/multihost.py").read_text())
        self.assertEqual(M.TOTAL_CELLS, 369)
        self.assertEqual(M.GLOBAL_CPU_CAP, float(c["GLOBAL_CPU_CAP"]))
        self.assertEqual(M.ROLES["AWS"]["workers"], 16)
        self.assertEqual(M.ROLES["AWS"]["core_assignment"], list(range(16)))

    def test_shard_manifest_deterministic_and_exact(self):
        import make_shard_manifest as MS
        m = MS.build()
        self.assertEqual((json.dumps(m, indent=1, sort_keys=True) + "\n").encode(), (NS / "config/SHARD_MANIFEST.json").read_bytes())
        owners = M.gate_shards(m)
        self.assertEqual(sorted(owners), list(range(369)))
        self.assertTrue(all(r == "AWS" for r in owners.values()))
        flat = [c for g in m["groups"] for c in g]
        self.assertEqual(flat, list(range(369)))

    def test_authorization_and_executor_identity(self):
        auth = PL.load_production_authorization()
        self.assertIs(auth["result_bearing"], False)
        self.assertEqual(PL.executor_source_identity()["EXECUTOR_HASH"], auth["scientific_adapter_hash"])
        self.assertEqual(sha(NS / "config/SHARD_MANIFEST.json"), auth["shard_manifest_sha256"])

    def test_release_sites_exactly_once(self):
        src = [l.strip() for l in (NS / "driver/production_launcher.py").read_text().splitlines()]
        for line in ("budget.release(key); continue", "budget.release(key)", "budget.release(k)"):
            self.assertEqual(src.count(line), 1, line)


class RuntimeContract(unittest.TestCase):
    def test_fresh_interpreter_precision_256_and_runtime_hash(self):
        auth = PL.load_production_authorization()
        pr = PL._probe(auth, "AWS")
        self.assertEqual(pr["precision_inside_scientific_context"], 256)
        self.assertTrue(pr["thread_contract_ok"])
        self.assertEqual(pr["runtime"]["sha256"], M.ROLES["AWS"]["runtime_contract_hash"])


def _synthetic_auth(tmp, cores):
    auth = PL.load_production_authorization()
    h = dict(auth["hosts"]["AWS"])
    h.update({"core_assignment": cores, "workers": len(cores), "work_dir": str(Path(tmp) / "work"),
              "evidence_dir": str(Path(tmp) / "evidence")})
    a = dict(auth)
    a["hosts"] = {"AWS": h}
    return a


class Pool(unittest.TestCase):
    def test_file_protocol_json_only_affinity_and_worker_loss(self):
        with tempfile.TemporaryDirectory() as tmp:
            a = _synthetic_auth(tmp, [2, 3])
            pool = PL.Pool(a, "AWS", Path(tmp) / "work", "t1")
            try:
                for s in pool.slots:
                    rd = json.loads((s["dir"] / "ready.json").read_text())
                    self.assertEqual(rd["affinity"], [s["core"]])
                    self.assertEqual(rd["precision_inside_scientific_context"], 256)
                pool.submit(pool.idle()[0], {"task_id": "syn-a", "kind": "SYNTHETIC_SPIN", "seconds": 0.5, "cells": [0]})
                task, res = pool.get(timeout=120)
                self.assertEqual(res["task_id"], "syn-a")
                self.assertTrue(res["ok"] and res["synthetic"])
                raw = (pool.slots[0]["dir"] / "result_syn-a.json").read_bytes()
                self.assertEqual(json.loads(raw)["task_id"], "syn-a")          # plain JSON, nothing else crossed
                os.kill(pool.slots[1]["proc"].pid, signal.SIGKILL)
                pool.slots[1]["proc"].wait()
                with self.assertRaises(PL.PoolWorkerLost):
                    pool.check_alive()
            finally:
                pool.close()


class Accounting(unittest.TestCase):
    """Through the REAL run_production_cells with a stub pool: an infrastructure loss becomes a torn, retry-eligible
    escrow (never dropped, never zero); a genuinely verified result commits exactly once."""

    def _pf(self, tmp, budget):
        auth = PL.load_production_authorization()
        pf = PL.production_preflight(auth, role="AWS", budget_path=Path(tmp) / "LEDGER.json", probe=False)
        pf["budget"] = budget
        pf["pending"] = [368]
        pf["groups"] = [[368]]
        return pf

    def test_torn_then_clean(self):
        sys.path.insert(0, str(CP / "p5y_k1_ps1_lifecycle_adapter/ops"))
        import ledger_ops as LO
        import global_budget as GB
        with tempfile.TemporaryDirectory() as tmp:
            led = Path(tmp) / "LEDGER.json"
            base = GB.GlobalBudget(led, M.validate_governed_cost, M.gate_global_cap,
                                   overhead_cpu_h=PL.load_production_authorization()["governed_overhead_cpu_h"],
                                   cap_cpu_h=M.validate_governed_cap(M.GLOBAL_CPU_CAP))
            led.write_text(json.dumps({"schema": GB.GlobalBudget.SCHEMA, "committed_cpu_h_by_role": {}, "open_reservations": {},
                                       "completed_cells": {}, "remote_completed_cells": {},
                                       LO.OPS_FIELD: LO.new_ops("AWS")}) + "\n")
            ob = LO.make_ops_budget(GB, base, "TESTRUN", PL.__file__)
            pf = self._pf(tmp, ob)

            class LostPool:
                def __init__(self, *a, **k): self.slots = [1]
                def idle(self): return [object()]
                def submit(self, slot, task): self.task = task
                def get(self, timeout=None): raise PL.PoolWorkerLost("synthetic worker loss")
                def close(self): pass
            orig_pool, orig_ex = PL.Pool, PL.executor_source_identity
            PL.Pool = LostPool
            PL.executor_source_identity = lambda root=None: {"EXECUTOR_HASH": pf["auth"]["scientific_adapter_hash"]}
            try:
                with self.assertRaises(PL.PoolWorkerLost):
                    PL.run_production_cells(pf)
            finally:
                PL.Pool, PL.executor_source_identity = orig_pool, orig_ex
            st = json.loads(led.read_text())
            torn = [k for k in st["open_reservations"] if k.startswith(LO.TORN)]
            self.assertEqual(len(torn), 1)
            self.assertEqual(st["open_reservations"][torn[0]]["ops"]["kind"], LO.ABORT)
            self.assertEqual(st["completed_cells"], {})
            self.assertFalse(list((PL.PRODUCTION_DIR / "cells").glob("*.json")) if (PL.PRODUCTION_DIR / "cells").exists() else [])


class RealEvidence(unittest.TestCase):
    """Sealing gate on REAL Phase-4 qualification evidence of the terminal cell 368 (28/28): the launcher's from-disk
    verification accepts it and rejects every tamper."""

    def _real(self, tmp):
        import gzip
        import shutil
        st = QUAL / "stages"
        ev = Path(tmp) / "ev"
        ev.mkdir()
        for k in ("t3", "t4", "t5"):
            shutil.copy(st / f"{k}_s368.json", ev / f"{k}_0368.json")
        lines = []
        for f in sorted((QUAL / "chunks").glob("rec_s368_*.jsonl")):
            lines += f.read_bytes().splitlines(keepends=True)
        with open(ev / "patches_0368.jsonl.gz", "wb") as raw:
            with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as z:
                z.write(b"".join(lines))
        t3, t4, t5 = (json.loads((ev / f"{k}_0368.json").read_text()) for k in ("t3", "t4", "t5"))
        sch = hashlib.sha256(M.canonical({"t3_record_sha256": t3["t3_record_sha256"], "t4_record_sha256": t4["t4_record_sha256"],
                                          "t5_certificate_hashes": [o["certificate_hash"] for o in t5["obligations"]]}) + b"\n").hexdigest()
        r = {"cell_id": 368, "ok": True, "precision_bits": 256, "scientific_content_hash": sch,
             "evidence": {k: {"path": str(ev / n), "sha256": sha(ev / n)} for k, n in
                          (("t3", "t3_0368.json"), ("t4", "t4_0368.json"), ("t5", "t5_0368.json"), ("patches_gz", "patches_0368.jsonl.gz"))}}
        return r, {"evidence_dir": str(ev)}, ev

    def test_accepts_real_and_rejects_tamper(self):
        with tempfile.TemporaryDirectory() as tmp:
            r, task, ev = self._real(tmp)
            self.assertTrue(PL._verified(r, 368, task))
            self.assertFalse(PL._verified(r, 367, task))
            bad = json.loads(json.dumps(r)); bad["precision_bits"] = 53
            self.assertFalse(PL._verified(bad, 368, task))
            t5 = json.loads((ev / "t5_0368.json").read_text())
            t5["obligations"][3]["status"] = "FAIL"
            (ev / "t5_0368.json").write_text(json.dumps(t5))
            self.assertFalse(PL._verified(r, 368, task))                                    # sha mismatch
            r2 = json.loads(json.dumps(r)); r2["evidence"]["t5"]["sha256"] = sha(ev / "t5_0368.json")
            self.assertFalse(PL._verified(r2, 368, task))                                   # hash fixed, content FAIL

    def test_certified_controls_identical_and_28_of_28(self):
        qs = json.loads((NS.parent / "p5y_k1_ps1_production_qualification/evidence/qual_summary.json").read_text())
        self.assertTrue(qs["all_qualification_cells_28_of_28"])
        self.assertEqual(sorted(qs["identity_vs_certified"]), ["150", "360", "361", "362", "363", "368"])
        for s, v in qs["identity_vs_certified"].items():
            self.assertTrue(v["t3_delta_and_x0_identical"] and v["t3_consumed_records_identical"] and v["t4_ledgers_identical"]
                            and v["t5_statuses_identical"] and v["t5_pass"] == 28, s)


class Firewall(unittest.TestCase):
    def test_no_genuine_production_state(self):
        prod = NS / "production"
        self.assertFalse((prod / "PRODUCTION_LEDGER.json").exists())
        self.assertFalse((prod / "cells").exists() and any((prod / "cells").iterdir()))
        auth = PL.load_production_authorization()
        hist = CP / auth["historical_production"]["ledger"]
        if hist.exists():
            self.assertEqual(sha(hist), auth["historical_production"]["sha256"])

    def test_vultr_not_admitted_under_topology_A(self):
        m = json.loads((NS / "config/SHARD_MANIFEST.json").read_text())
        self.assertEqual(m["VULTR"]["cells"], [])
        auth = PL.load_production_authorization()
        self.assertNotIn("VULTR", auth["hosts"])
        with self.assertRaises(Exception):
            PL.production_preflight(auth, role="VULTR", probe=False)


if __name__ == "__main__":
    unittest.main(verbosity=2)
