"""Focused tests for SYSTEMD_RECOVERY_EXECUTABLE_BINDING_DEFECT.

render_start() derives ExecStart and ExecStopPost from spec["ops_root"]. If that points at
the lifecycle adapter, the unit runs the ADAPTER's ops against the RECOVERY contract and
opscommon.load_contract refuses with "a non-frozen contract must be mode SYNTHETIC_CONTROL".
"""
import json
import sys
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(NS / "ops"))
from opscommon import host_spec, load_contract  # noqa: E402
import prodctl as PC  # noqa: E402

ADAPTER_OPS = "p5y_k1_ps1_lifecycle_adapter/ops"
RECOVERY_OPS = "p5y_k1_ps1_portable_recovery/ops"


def argv():
    c = load_contract(None)
    return PC.render_start(c, "AWS", "TESTRUNID"), c


def _exec_start(a):
    return " ".join(a[a.index("--") + 1:])


def _exec_stop_post(a):
    return next(x for x in a if x.startswith("ExecStopPost="))[len("ExecStopPost="):]


def test_exec_start_is_not_the_adapter_supervisor():
    a, _ = argv()
    assert ADAPTER_OPS + "/supervisor.py" not in _exec_start(a)


def test_exec_start_is_the_recovery_supervisor():
    a, _ = argv()
    assert RECOVERY_OPS + "/supervisor.py" in _exec_start(a)


def test_exec_stop_post_is_not_the_adapter_prodctl():
    a, _ = argv()
    assert ADAPTER_OPS + "/prodctl.py" not in _exec_stop_post(a)


def test_exec_stop_post_is_the_recovery_prodctl_settle_fallback():
    a, _ = argv()
    s = _exec_stop_post(a)
    assert RECOVERY_OPS + "/prodctl.py" in s and "settle-fallback" in s


def test_both_reference_the_same_deployed_recovery_contract():
    a, c = argv()
    cpath = c["_path"]
    assert "p5y_k1_ps1_portable_recovery/config/OPERATIONAL_CONTRACT.json" in str(cpath)
    assert str(cpath) in _exec_start(a) and str(cpath) in _exec_stop_post(a)


def test_contract_path_equals_recovery_ops_CONTRACT_PATH():
    """This is WHY the adapter refused: load_contract only takes the hash-verified frozen
    branch when the file IS that namespace's CONTRACT_PATH."""
    import opscommon as OC
    _, c = argv()
    assert Path(c["_path"]).resolve() == OC.CONTRACT_PATH.resolve()


def test_unit_resolves_generation2_roots_not_generation1():
    a, c = argv()
    spec = host_spec(c, "AWS")
    assert spec["production_root"] == "/home/ubuntu/work/ReBaseGuard-ps1-prod-gen2"
    assert spec["runtime_dir"] == "/home/ubuntu/rbg-runtime/p5y_k1_ps1_generation2"
    joined = " ".join(a)
    assert "/home/ubuntu/work/ReBaseGuard-ps1-prod/" not in joined, \
        "the unit must never resolve the generation-1 mutable root"


def test_recovery_ops_capabilities_still_active():
    assert "RECON.reconcile" in (NS / "ops" / "supervisor.py").read_text()
    assert "GRACEFUL_DRAIN" in (NS / "ops" / "ledger_ops.py").read_text()


def test_generation1_ledger_untouched():
    import hashlib
    p = Path("/home/ubuntu/work/ReBaseGuard-ps1-prod/level4/closure_proofs/"
             "p5y_k1_ps1_production/production/PRODUCTION_LEDGER.json")
    assert hashlib.sha256(p.read_bytes()).hexdigest() == \
        "0557bc229c3fcdb10cb0dd0b5836fa62a6b0e6c2512656e6ec7e49294b4d6cab"
