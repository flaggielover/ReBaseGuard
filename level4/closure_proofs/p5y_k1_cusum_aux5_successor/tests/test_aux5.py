"""Focused tests for the Aux5 successor identity layer. No certification is run here."""
import hashlib
import json
import os
import socket
import subprocess
import sys
from pathlib import Path

import pytest

NS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(NS / "code"))
import ancestry5  # noqa: E402
import cap_formula  # noqa: E402

AUX4 = ancestry5.AUX4_NS
ROOT = ancestry5.ROOT


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def test_generated_modules_match_generation_report():
    rep = json.loads((NS / "config/GENERATION_REPORT.json").read_text())["generated"]
    assert set(rep) == {"runtime_identity5.py", "tcb5.py", "manifest_v3.py", "identity5.py", "qualify5.py"}
    for name, info in rep.items():
        assert sha(NS / "code" / name) == info["generated_sha256"]
        assert sha(ROOT / info["source"]) == info["source_sha256"]


def test_aux4_sources_and_science_byte_identical_to_aux4_manifest():
    import manifest_v3
    assert manifest_v3.science_unchanged_problems() == []
    aux4 = json.loads((AUX4 / "manifests/producer_manifest_v2.json").read_text())["files"]
    for n in ("ancestry4.py", "schema.py", "hash_v2.py", "scipy_guard.py"):
        rel = str((AUX4 / "code" / n).relative_to(ROOT))
        assert sha(ROOT / rel) == aux4[rel]


def test_tcb5_boundary():
    import tcb5
    paths = tcb5.tcb_paths()
    for n in tcb5.AUX5_MODULES:
        assert str((NS / "code" / n).relative_to(ROOT)) in paths
    for n in tcb5.REUSED_AUX4_MODULES:
        assert str((AUX4 / "code" / n).relative_to(ROOT)) in paths
    for n in tcb5.AUX4_REPLACED_MODULES:
        assert str((AUX4 / "code" / n).relative_to(ROOT)) not in paths
    assert str((AUX4 / "manifests/producer_manifest_v2.json").relative_to(ROOT)) in paths


def test_backend_libraries_bound_by_absolute_path():
    import runtime_identity5 as RI
    libs = RI.backend_libraries()
    assert libs and all(Path(k).is_absolute() and Path(k).exists() for k in libs)
    assert all(RI.sha256_file(k) == v for k, v in libs.items())
    for fam in RI.REQUIRED_LIBRARY_FAMILIES:
        assert any(Path(k).name.startswith(fam) for k in libs)


def test_openblas_primary_is_numpy_and_contract_binds_host():
    import runtime_identity5 as RI
    ob = RI.openblas_identity()
    assert ob["openblas_runtime_corename"]
    c = RI.contract()
    assert c["schema"] == "k1.cusum-aux5.runtime-contract.v3"
    assert c["host_name"] == socket.gethostname()
    assert c["venv_prefix"] == str(Path(sys.prefix).resolve())


def test_identity_kind_and_rejected_predecessors():
    import identity5
    assert identity5.IDENTITY_KIND == "cusum_aux5_manifest_bound_identity_v3"
    rej = identity5.rejected_producer_identities()
    assert rej["aux4_commit"] == ancestry5.AUX4_COMMIT
    assert rej["aux4_producer_manifest_hash"] == ancestry5.AUX4_IDENTITY["producer_manifest_hash"]


def test_cap_formula_reproduces_prefreeze_value():
    assert cap_formula.cap(c_max_cpu_seconds="2278.1")["CAP_cpu_h"] == 300
    assert cap_formula.cap(c_max_cpu_seconds="4000")["CAP_cpu_h"] >= cap_formula.cap(c_max_cpu_seconds="2278.1")["CAP_cpu_h"]


def test_protocol_forbids_automatic_production_transition():
    p = json.loads((NS / "config/QUALIFICATION_PROTOCOL.json").read_text())
    assert p["transition_to_production"]["authorized_by_this_protocol"] is False
    assert p["cells"] == [318, 323] and p["repeats_per_cell"] == 2 and p["result_bearing"] is False


@pytest.mark.skipif(not (NS / "manifests/producer_manifest_v3.json").exists(), reason="manifest not frozen yet")
def test_manifest_v3_verifies_on_bound_host():
    if socket.gethostname() != ancestry5.BOUND_HOST:
        pytest.skip("not the bound host")
    import manifest_v3
    state = manifest_v3.verify()
    assert state["ok"], state["problems"][:5]


def test_certifying_import_graph_excludes_aux4_identity_layer():
    try:
        import scipy  # noqa: F401
    except ImportError:
        pytest.skip("SciPy not installed in this interpreter")
    code = ("import json, sys\nimport qualify5, tcb5\n"
            "loaded = tcb5.loaded_repository_files()\n"
            "print(json.dumps({'coverage': tcb5.verify_coverage(), 'loaded': loaded}))\n")
    env = {"PATH": "/usr/bin:/bin", "HOME": os.environ.get("HOME", "/root"), "OMP_NUM_THREADS": "1",
           "OPENBLAS_NUM_THREADS": "1", "MKL_NUM_THREADS": "1", "NUMEXPR_NUM_THREADS": "1",
           "K1_THREADS_PINNED": "1", "PYTHONDONTWRITEBYTECODE": "1"}
    r = subprocess.run([sys.executable, "-c", code], cwd=str(NS / "code"), env=env, capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, r.stderr[-800:]
    out = json.loads(r.stdout.strip().splitlines()[-1])
    import tcb5
    replaced = {str((AUX4 / "code" / n).relative_to(ROOT)) for n in tcb5.AUX4_REPLACED_MODULES}
    assert out["coverage"]["ok"], out["coverage"]["uncovered"][:5]
    assert not (set(out["loaded"]) & replaced)
