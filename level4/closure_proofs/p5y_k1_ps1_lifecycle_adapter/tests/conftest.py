"""Result-free fixtures for the PS1 adapter. Every synthetic campaign runs in a FRESH local git clone of the PS1
authorization tag (own .git, so its runtime exclude policy is independent) with a SYNTHETIC_CONTROL contract that the
contract loader refuses to point at any production root or production runtime directory."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ADAPTER = Path(__file__).resolve().parents[1]
OPS = ADAPTER / "ops"
sys.path.insert(0, str(OPS))
import opscommon as OC                                          # noqa: E402

PY = sys.executable


def parent():
    c = json.loads(OC.CONTRACT_PATH.read_text())
    return c["parent"]["tag"], c["parent"]["commit"]


def make_clone(dest: Path) -> Path:
    tag, commit = parent()
    top = subprocess.check_output(["git", "-C", str(ADAPTER), "rev-parse", "--show-toplevel"]).decode().strip()
    subprocess.run(["git", "clone", "-q", "--local", "--no-checkout", top, str(dest)], check=True)
    subprocess.run(["git", "-C", str(dest), "-c", "advice.detachedHead=false", "checkout", "-q", "--detach", tag], check=True)
    assert subprocess.check_output(["git", "-C", str(dest), "rev-parse", "HEAD"]).decode().strip() == commit
    import runtime_state as RS
    RS.install_git_policy(dest)
    return dest


def synthetic_contract(tmp: Path, root: Path, control: dict) -> Path:
    c = json.loads(OC.CONTRACT_PATH.read_text())
    c["mode"] = "SYNTHETIC_CONTROL"
    ctl = tmp / "control.json"
    ctl.write_text(json.dumps(control))
    c["accounting"]["poll_interval_s"] = 0.5
    c["service"]["unit_prefix"] = "rbg-synthetic-"
    c["parent"]["workers"]["AWS"] = len(control["cores"])
    for role in list(c["hosts"]):
        spec = c["hosts"][role]
        spec["production_root"] = str(root if role == "AWS" else tmp / f"absent-{role}")
        spec["ops_root"] = str(ADAPTER)
        spec["python"] = PY
        spec["runtime_dir"] = str(tmp / f"runtime-{role}")
        spec["launch_prefix"] = []
        spec["online_cpus"] = os.cpu_count()
        c["service"]["environment"][role]["RBG_SYNTH_CONTROL"] = str(ctl)
    c["synthetic"] = {"entry": "tests/synthetic_entry.py", "service_mode": False,
                      "boot_id_file": str(tmp / "boot_id"), "boot_time_file": str(tmp / "boot_time")}
    (tmp / "boot_id").write_text("synthetic-boot-1\n")
    (tmp / "boot_time").write_text("0\n")
    p = tmp / "synthetic_contract.json"
    p.write_text(json.dumps(c, indent=1, sort_keys=True))
    return p


@pytest.fixture
def campaign(tmp_path):
    root = make_clone(tmp_path / "clone")

    def mk(control):
        return synthetic_contract(tmp_path, root, control), root
    return mk


def supervise(contract: Path, run_id: str, timeout=900):
    return subprocess.run([PY, str(OPS / "supervisor.py"), "--contract", str(contract), "--role", "AWS", "--run-id", run_id],
                          capture_output=True, text=True, timeout=timeout)
