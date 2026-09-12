"""PS1 lifecycle adapter acceptance (result-free). Synthetic campaigns only; never a production path."""
import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

import pytest

ADAPTER = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ADAPTER / "code"))
sys.path.insert(0, str(ADAPTER / "ops"))
import opscommon as OC                      # noqa: E402
import conftest as CF                       # noqa: E402

LIFECYCLE = ADAPTER.parent / "p5y_k1_sr_production_lifecycle_successor"


def ledger(root):
    return json.loads((root / "level4/closure_proofs/p5y_k1_ps1_production/production/PRODUCTION_LEDGER.json").read_text())


def test_ops_byte_identical_except_asserted_constant():
    import make_ops_adapter as MK
    built = MK.build()
    for rel, text in built.items():
        assert (ADAPTER / rel).read_text() == text, rel
    for f in MK.OPS:
        same = (ADAPTER / "ops" / f).read_bytes() == (LIFECYCLE / "ops" / f).read_bytes()
        assert same == (f not in ("opscommon.py", "prodctl.py")), f


def test_contract_hash_bound_and_rendered_service():
    c = OC.load_contract()
    assert c["mode"] == "PRODUCTION" and c["scientific_identity_changed"] is False
    assert c["parent"]["per_host_hard_caps_present"] is False and c["parent"]["total_cells"] == 369
    import prodctl as PC
    rid = "20260101T000000Z-deadbeef"
    argv = PC.render_start(c, "AWS", rid)
    assert argv[:3] == ["sudo", "-n", "systemd-run"] and f"--unit=rbg-p5y-k1-ps1-prod-aws-{rid}.service" in argv
    assert "-p" in argv and "CPUAccounting=yes" in argv and "KillMode=control-group" in argv
    assert argv[-7].endswith("ops/supervisor.py")


def test_release_sites_classified_on_ps1_launcher():
    import ledger_ops as LO
    c = OC.load_contract()
    spec = c["hosts"]["AWS"]
    launcher = ADAPTER.parent / "p5y_k1_ps1_production/driver/production_launcher.py"
    sys.path.insert(0, str(launcher.parent))
    import global_budget as GB
    import multihost as M
    b = GB.GlobalBudget(Path("/nonexistent/L.json"), M.validate_governed_cost, M.gate_global_cap,
                        overhead_cpu_h=c["parent"]["governed_overhead_cpu_h"], cap_cpu_h=M.validate_governed_cap(M.GLOBAL_CPU_CAP))
    LO.make_ops_budget(GB, b, "T", str(launcher))          # refuses unless every release site occurs exactly once


def test_clean_completion(campaign):
    contract, root = campaign({"spin_s": 0.3, "cells": [0, 1, 2, 3, 4], "cores": [16, 17]})
    r = CF.supervise(contract, "20260101T000001Z-aaaa0001")
    assert r.returncode == 0, r.stdout + r.stderr
    st = ledger(root)
    assert sorted(int(c) for c in st["completed_cells"]) == [0, 1, 2, 3, 4]
    assert not st["open_reservations"]
    run = st["operational_lifecycle"]["runs"]["20260101T000001Z-aaaa0001"]
    assert run["status"] == "SETTLED" and run["settlement"]["charged_after_cpu_h"] > 0
    cells = sorted((root / "level4/closure_proofs/p5y_k1_ps1_production/production/cells").glob("*.json"))
    assert [p.name for p in cells] == ["0000.json", "0001.json", "0002.json", "0003.json", "0004.json"]


def test_worker_loss_is_torn_then_retried(campaign):
    contract, root = campaign({"spin_s": 0.3, "cells": [4, 5, 6, 7], "cores": [16, 17], "die": {"4": [1]}})
    r1 = CF.supervise(contract, "20260101T000002Z-aaaa0002")
    assert r1.returncode != 0
    st = ledger(root)
    assert st["operational_lifecycle"]["torn_attempts"].get("4") == 1
    assert not any(k.startswith("AWS:") for k in st["open_reservations"])
    r2 = CF.supervise(contract, "20260101T000003Z-aaaa0003")
    assert r2.returncode == 0, r2.stdout + r2.stderr
    assert sorted(int(c) for c in ledger(root)["completed_cells"]) == [4, 5, 6, 7]


def test_scientific_failure_halts_and_refuses_restart(campaign):
    contract, root = campaign({"spin_s": 0.3, "cells": [8, 9, 10, 11], "cores": [16, 17], "fail": {"8": [1]}})
    r = CF.supervise(contract, "20260101T000004Z-aaaa0004")
    assert r.returncode == 20, r.stdout + r.stderr
    assert ledger(root)["operational_lifecycle"]["halt"]
    r2 = CF.supervise(contract, "20260101T000005Z-aaaa0005")
    assert r2.returncode == 30 and "HALTED" in (r2.stdout + r2.stderr)


def test_sigkill_of_whole_run_recovers(campaign):
    contract, root = campaign({"spin_s": 0.3, "cells": [12, 13, 14, 15], "cores": [16, 17], "hang": {"12": [1]}})
    p = subprocess.Popen([CF.PY, str(ADAPTER / "ops/supervisor.py"), "--contract", str(contract), "--role", "AWS",
                          "--run-id", "20260101T000006Z-aaaa0006"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                         start_new_session=True)
    t_end = time.time() + 120
    while time.time() < t_end:
        try:
            st = ledger(root)
            if any(k.startswith("AWS:") for k in st["open_reservations"]):
                break
        except (FileNotFoundError, json.JSONDecodeError):
            pass
        time.sleep(0.5)
    time.sleep(2)
    os.killpg(p.pid, signal.SIGKILL)                      # the whole run dies at once (power-loss analogue)
    p.wait()
    r = CF.supervise(contract, "20260101T000007Z-aaaa0007")
    assert r.returncode == 0, r.stdout + r.stderr
    st = ledger(root)
    assert sorted(int(c) for c in st["completed_cells"]) == [12, 13, 14, 15]
    assert st["operational_lifecycle"]["runs"]["20260101T000006Z-aaaa0006"]["status"] == "SETTLED"
    assert st["operational_lifecycle"]["torn_attempts"].get("12") == 1
