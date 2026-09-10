"""Result-free fixtures. Every synthetic campaign runs in a FRESH git clone of the
parent tag under a temporary directory with a SYNTHETIC_CONTROL contract; the
contract loader refuses any synthetic contract that points at a production root
or production runtime directory."""
from __future__ import annotations

import copy
import hashlib
import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

import pytest

SUCC = Path(__file__).resolve().parents[1]
OPS = SUCC / "ops"
sys.path.insert(0, str(OPS))
import opscommon as OC                                          # noqa: E402

PARENT_TAG = "p5y-k1-sr-production-authorized-preresult"
PARENT_COMMIT = "bd7cf269792bc146e911ee57a85533b7b7b1aa9d"
PY = sys.executable


def source_repo() -> str:
    """Any checkout of this repository that contains the parent tag."""
    top = subprocess.check_output(["git", "-C", str(SUCC), "rev-parse", "--show-toplevel"]).decode().strip()
    return top


def make_clone(dest: Path) -> Path:
    subprocess.run(["git", "clone", "-q", "--local", "--no-checkout", source_repo(), str(dest)],
                   check=True)
    subprocess.run(["git", "-C", str(dest), "-c", "advice.detachedHead=false", "checkout", "-q",
                    "--detach", PARENT_TAG], check=True)
    assert subprocess.check_output(["git", "-C", str(dest), "rev-parse", "HEAD"]).decode().strip() \
        == PARENT_COMMIT
    import runtime_state as RS
    RS.install_git_policy(dest)
    return dest


def ed25519_pair(d: Path):
    d.mkdir(parents=True, exist_ok=True)
    priv, pub = d / "synthetic_handoff_ed25519.pem", d / "synthetic_handoff_pub.pem"
    subprocess.run(["openssl", "genpkey", "-algorithm", "Ed25519", "-out", str(priv)], check=True)
    subprocess.run(["openssl", "pkey", "-in", str(priv), "-pubout", "-out", str(pub)], check=True)
    der = subprocess.check_output(["openssl", "pkey", "-pubin", "-in", str(pub), "-outform", "DER"])
    return priv, pub, hashlib.sha256(der).hexdigest()


def synthetic_contract(tmp: Path, *, aws_root=None, vultr_root=None, keys=None, poll=0.5,
                       control=None) -> Path:
    c = json.loads(OC.CONTRACT_PATH.read_text())
    c["mode"] = "SYNTHETIC_CONTROL"
    ctl = control or (tmp / "control.json")
    if not ctl.exists():
        ctl.write_text(json.dumps({"spin_s": 0.05}))
    c["accounting"]["poll_interval_s"] = poll
    c["service"]["unit_prefix"] = "rbg-synthetic-"
    for role, root in (("AWS", aws_root), ("VULTR", vultr_root)):
        spec = c["hosts"][role]
        spec["production_root"] = str(root or (tmp / f"absent-{role}"))
        spec["ops_root"] = str(SUCC)
        spec["python"] = PY
        spec["runtime_dir"] = str(tmp / f"runtime-{role}")
        spec["launch_prefix"] = []
        spec["online_cpus"] = os.cpu_count()
        c["service"]["environment"][role]["RBG_SYNTH_CONTROL"] = str(ctl)
    c["hosts"]["VULTR"]["producer_binding"] = "SOURCE_MANIFEST"
    syn = {"entry": "tests/synthetic_entry.py", "service_mode": False,
           "boot_id_file": str(tmp / "boot_id"), "boot_time_file": str(tmp / "boot_time")}
    if keys:
        c["hosts"]["AWS"]["handoff_private_key"] = str(keys[0])
        syn["handoff_pubkey"], syn["handoff_fingerprint"] = str(keys[1]), keys[2]
    c["synthetic"] = syn
    p = tmp / "synthetic_contract.json"
    p.write_text(json.dumps(c, indent=1, sort_keys=True))
    return p


def set_control(contract_path: Path, **ctl):
    c = json.loads(contract_path.read_text())
    Path(c["service"]["environment"]["AWS"]["RBG_SYNTH_CONTROL"]).write_text(json.dumps(ctl))


def start_supervisor(contract_path: Path, role: str, run_id=None, log=None):
    run_id = run_id or OC.new_run_id()
    out = open(log, "ab") if log else subprocess.DEVNULL
    p = subprocess.Popen([PY, str(OPS / "supervisor.py"), "--contract", str(contract_path),
                          "--role", role, "--run-id", run_id], stdout=out, stderr=subprocess.STDOUT,
                         start_new_session=True)
    return p, run_id


def run_supervisor(contract_path: Path, role: str, timeout=300, log=None):
    p, rid = start_supervisor(contract_path, role, log=log)
    try:
        return p.wait(timeout=timeout), rid
    except subprocess.TimeoutExpired:
        kill_tree(p.pid)
        p.wait()
        raise


def prodctl(contract_path: Path, role: str, *args):
    r = subprocess.run([PY, str(OPS / "prodctl.py"), *args, "--contract", str(contract_path),
                        "--role", role], capture_output=True, text=True, timeout=600)
    try:
        return r.returncode, json.loads(r.stdout)
    except json.JSONDecodeError:
        return r.returncode, {"raw": r.stdout, "err": r.stderr}


def ledger(root: Path) -> dict:
    p = Path(root) / OC.PARENT_NS_REL / "production/PRODUCTION_LEDGER.json"
    return json.loads(p.read_text()) if p.exists() else None


def wait_for(pred, timeout=120, step=0.05):
    t = time.time() + timeout
    while time.time() < t:
        try:
            if pred():
                return True
        except (json.JSONDecodeError, FileNotFoundError, KeyError, TypeError):
            pass
        time.sleep(step)
    raise TimeoutError("condition not reached")


def kill_tree(pid):
    """Simulate total loss of the supervisor's whole process group (host crash)."""
    try:
        os.killpg(pid, signal.SIGKILL)
    except ProcessLookupError:
        pass


def real_production_untouched():
    """The REAL production namespaces never receive a synthetic byte."""
    c = json.loads(OC.CONTRACT_PATH.read_text())
    out = {}
    for role, spec in c["hosts"].items():
        prod = Path(spec["production_root"]) / OC.PARENT_NS_REL / "production"
        try:
            present = prod.exists()
        except PermissionError:
            continue
        if present:
            out[role] = sorted(p.relative_to(prod).as_posix() for p in prod.rglob("*")
                               if p.is_file() and "__pycache__" not in p.parts)
    return out


@pytest.fixture(scope="session")
def keys(tmp_path_factory):
    return ed25519_pair(tmp_path_factory.mktemp("keys"))
