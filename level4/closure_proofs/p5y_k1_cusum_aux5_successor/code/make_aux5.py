"""Generate the Aux5 CUSUM successor identity layer from the committed Aux4 sources.

Every Aux4 source is first verified against the committed Aux4 producer manifest v2, then patched with
anchored substitutions (each anchor must occur exactly once). Science modules and the Aux4 modules that
define scientific-hash semantics (schema.py, hash_v2.py, scipy_guard.py, ancestry4.py) are NOT copied:
the successor imports them in place, byte-identical, by exact path.

Changes, and only these:
  runtime_identity5  backend libraries bound by ABSOLUTE resolved path from the numpy/flint site-packages
                     (repairs the external-venv defect: Aux4 globbed repo-relative paths and bound {});
                     the arithmetic-relevant OpenBLAS is selected explicitly (numpy's libscipy_openblas64_);
                     host name, venv prefix, interpreter path and site-packages are bound
  tcb5               successor modules + reused Aux4 modules by exact path; Aux4 manifest v2 bound as artifact
  manifest_v3        schema/version/artifact; verify() additionally requires every Aux4 science input to be
                     byte-identical to the Aux4 manifest v2
  identity5          identity kind v3; Aux4 commit and Aux4 manifest hash added to the rejected identities
  qualify5           imports the successor identity layer; campaign name and change list
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
AUX4 = NS.parent / "p5y_k1_cusum_aux4_fullcover"
ROOT = NS.parents[2]


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


P = {}   # target -> (source, [(old, new), ...])

P["runtime_identity5.py"] = ("runtime_identity.py", [
    ('import ancestry4\n',
     'import ancestry5                                           # noqa: F401\nimport ancestry4\nimport socket\n'),
    ('SCHEMA = "k1.cusum-aux4.runtime-contract.v2"', 'SCHEMA = "k1.cusum-aux5.runtime-contract.v3"'),
    ('''BACKEND_LIBRARY_GLOBS = (
    "level4/.venv/lib/python3.12/site-packages/python_flint.libs/libflint-*.so*",
    "level4/.venv/lib/python3.12/site-packages/python_flint.libs/libgmp-*.so*",
    "level4/.venv/lib/python3.12/site-packages/python_flint.libs/libmpfr-*.so*",
    "level4/.venv/lib/python3.12/site-packages/numpy.libs/libscipy_openblas64_-*.so",
)''',
     '''# AUX5 REPAIR (external venv): patterns are relative to the site-packages directory that ACTUALLY holds
# numpy and python-flint in this process, and every match is bound by its absolute resolved path.
BACKEND_LIBRARY_GLOBS = (
    "python_flint.libs/libflint-*.so*",
    "python_flint.libs/libgmp-*.so*",
    "python_flint.libs/libmpfr-*.so*",
    "numpy.libs/libscipy_openblas64_-*.so",
    "scipy.libs/libscipy_openblas-*.so",
)
REQUIRED_LIBRARY_FAMILIES = ("libflint-", "libgmp-", "libmpfr-", "libscipy_openblas64_-")'''),
    ('''def backend_libraries() -> dict:
    """repo-relative path -> sha256 for every numerical backend library."""
    out = {}
    for pattern in BACKEND_LIBRARY_GLOBS:
        for p in sorted(ancestry4.ROOT.glob(pattern)):
            out[str(p.relative_to(ancestry4.ROOT))] = sha256_file(p)
    return dict(sorted(out.items()))''',
     '''def site_packages() -> Path:
    """The site-packages directory of the numpy actually imported (must also hold python-flint)."""
    import numpy
    import flint
    sp = Path(numpy.__file__).resolve().parents[1]
    if Path(flint.__file__).resolve().parents[1] != sp:
        raise RuntimeMismatch("numpy and python-flint are not installed in the same site-packages")
    return sp


def backend_libraries() -> dict:
    """ABSOLUTE resolved path -> sha256 for every numerical backend library. Fails closed if a
    required family is absent (the Aux4 defect bound an empty map outside the repository tree)."""
    sp = site_packages()
    out = {}
    for pattern in BACKEND_LIBRARY_GLOBS:
        for p in sorted(sp.glob(pattern)):
            out[str(p.resolve())] = sha256_file(p)
    missing = [f for f in REQUIRED_LIBRARY_FAMILIES
               if not any(Path(k).name.startswith(f) for k in out)]
    if missing:
        raise RuntimeMismatch(f"backend library families not found under {sp}: {missing}")
    return dict(sorted(out.items()))'''),
    ('''    lib = ctypes.CDLL(mapped[0])''',
     '''    # AUX5: bind numpy's OpenBLAS explicitly (the float candidate solve runs through numpy.linalg);
    # SciPy's own OpenBLAS may also be mapped and is bound by bytes in backend_libraries, never called.
    primary = [p for p in mapped if Path(p).name.startswith("libscipy_openblas64_")]
    if len(primary) != 1:
        raise RuntimeMismatch(f"expected exactly one numpy OpenBLAS mapped, got {mapped}")
    lib = ctypes.CDLL(primary[0])'''),
    ('''        "backend_libraries": backend_libraries(),''',
     '''        "backend_libraries": backend_libraries(),
        "host_name": socket.gethostname(),
        "venv_prefix": str(Path(sys.prefix).resolve()),
        "python_executable": str(Path(sys.executable).resolve()),
        "site_packages": str(site_packages()),'''),
])

P["tcb5.py"] = ("tcb.py", [
    ('from pathlib import Path\n\nimport ancestry4\n', 'from pathlib import Path\n\nimport ancestry5\nimport ancestry4\n'),
    ('''AUX4_MODULES = (
    "ancestry4.py", "tcb.py", "runtime_identity.py", "scipy_guard.py",
    "manifest_v2.py", "schema.py", "hash_v2.py", "identity4.py", "qualify4.py",
)
# Aux4 modules that are NOT certifying. They are never imported by the
# certifying process; `test_aux4.py` proves it rather than assuming it.
AUX4_NON_CERTIFYING = (
    "aggregate_ledger.py", "audit4.py", "report4.py", "run_state.py",
)''',
     '''AUX5_MODULES = (
    "ancestry5.py", "tcb5.py", "runtime_identity5.py", "manifest_v3.py",
    "identity5.py", "qualify5.py",
)
# Aux4 modules imported IN PLACE and byte-identical: they define the scientific hash semantics,
# the field classification, the SciPy guard and the predecessor import bootstrap.
REUSED_AUX4_MODULES = ("ancestry4.py", "schema.py", "hash_v2.py", "scipy_guard.py")
# Aux4 identity-layer modules that must NEVER be loaded by the Aux5 certifying process.
AUX4_REPLACED_MODULES = ("tcb.py", "runtime_identity.py", "manifest_v2.py", "identity4.py", "qualify4.py")
# Aux5 namespace modules that are NOT certifying (never imported by the certifying process).
AUX5_NON_CERTIFYING = ("make_aux5.py", "analyze_qualification.py", "cap_formula.py")'''),
    ('''ARTIFACT_INPUTS = (
    ancestry4.AUX3_NS / "manifests/producer_manifest_v1.json",
    ancestry4.AUX3_NS / "evidence/scipy_execution_probe.json",
)''',
     '''ARTIFACT_INPUTS = (
    ancestry4.AUX3_NS / "manifests/producer_manifest_v1.json",
    ancestry4.AUX3_NS / "evidence/scipy_execution_probe.json",
    ancestry5.AUX4_NS / "manifests/producer_manifest_v2.json",
)'''),
    ('''    out = [ancestry4.NS / "code" / n for n in AUX4_MODULES]''',
     '''    out = [ancestry5.NS / "code" / n for n in AUX5_MODULES]
    out += [ancestry4.NS / "code" / n for n in REUSED_AUX4_MODULES]'''),
])

P["manifest_v3.py"] = ("manifest_v2.py", [
    ('import ancestry4\nimport runtime_identity\nimport tcb\n',
     'import ancestry5\nimport ancestry4\nimport runtime_identity5 as runtime_identity\nimport tcb5 as tcb\n'),
    ('SCHEMA = "k1.cusum-aux4.producer-manifest.v2"\nMANIFEST_VERSION = 2\nARTIFACT = ancestry4.NS / "manifests" / "producer_manifest_v2.json"',
     'SCHEMA = "k1.cusum-aux5.producer-manifest.v3"\nMANIFEST_VERSION = 3\nARTIFACT = ancestry5.NS / "manifests" / "producer_manifest_v3.json"\n'
     'AUX4_MANIFEST = ancestry5.AUX4_NS / "manifests" / "producer_manifest_v2.json"'),
    ('"kind": "cusum_aux4_fullcover_producer_manifest_v2",', '"kind": "cusum_aux5_successor_producer_manifest_v3",'),
    ('sorted(tcb.AUX4_NON_CERTIFYING),', 'sorted(tcb.AUX5_NON_CERTIFYING),'),
    ('''def manifest_hash(m: dict | None = None) -> str:''',
     '''def science_unchanged_problems() -> list[str]:
    """Every Aux4 manifest-v2 input that is not an Aux4 identity-layer module must be byte-identical here."""
    aux4 = json.loads(AUX4_MANIFEST.read_text())["files"]
    replaced = {str((ancestry5.AUX4_NS / "code" / n).relative_to(ancestry4.ROOT)) for n in tcb.AUX4_REPLACED_MODULES}
    out = []
    for rel, digest in sorted(aux4.items()):
        if rel in replaced:
            continue
        path = ancestry4.ROOT / rel
        if not path.exists() or sha256_file(path) != digest:
            out.append(f"science input differs from Aux4 manifest v2: {rel}")
    return out


def manifest_hash(m: dict | None = None) -> str:'''),
    ('''    problems += runtime_identity.compare(committed.get("runtime", {}))''',
     '''    problems += science_unchanged_problems()
    problems += runtime_identity.compare(committed.get("runtime", {}))'''),
])

P["identity5.py"] = ("identity4.py", [
    ('import ancestry4\n\nimport spec\n', 'import ancestry5\nimport ancestry4\n\nimport spec\n'),
    ('import manifest_v2\n', 'import manifest_v3 as manifest_v2\n'),
    ('IDENTITY_KIND = "cusum_aux4_manifest_bound_identity_v2"', 'IDENTITY_KIND = "cusum_aux5_manifest_bound_identity_v3"'),
    ('''        "aux3_commit": ancestry4.AUX3_COMMIT,
    }''',
     '''        "aux3_commit": ancestry4.AUX3_COMMIT,
        "aux4_commit": ancestry5.AUX4_COMMIT,
    }'''),
    ('''        out["aux3_producer_manifest_hash"] = hashlib.sha256(
            canonical(m)).hexdigest()
    return out''',
     '''        out["aux3_producer_manifest_hash"] = hashlib.sha256(
            canonical(m)).hexdigest()
    aux4 = ancestry5.AUX4_NS / "manifests" / "producer_manifest_v2.json"
    if aux4.exists():                           # byte-bound in the TCB
        out["aux4_producer_manifest_hash"] = hashlib.sha256(
            canonical(json.loads(aux4.read_text()))).hexdigest()
    return out'''),
])

P["qualify5.py"] = ("qualify4.py", [
    ('import ancestry4                                                # noqa: F401,E402',
     'import ancestry5                                                # noqa: F401,E402'),
    ('import identity4 as ID                                          # noqa: E402',
     'import identity5 as ID                                          # noqa: E402'),
    ('import manifest_v2                                              # noqa: E402',
     'import manifest_v3 as manifest_v2                               # noqa: E402'),
    ('"campaign": "p5y_k1_cusum_aux4_fullcover",', '"campaign": "p5y_k1_cusum_aux5_successor",'),
    ('"final_fail_closed_gate_after_scientific_hash"],',
     '"final_fail_closed_gate_after_scientific_hash",\n                        "aux5_external_venv_absolute_backend_binding",\n                        "aux5_named_host_runtime_contract_v3"],'),
])


def main() -> int:
    aux4_manifest = json.loads((AUX4 / "manifests/producer_manifest_v2.json").read_text())["files"]
    report = {"schema": "rebaseguard.p5y.k1.cusum-aux5.generation-report.v1", "generated": {}}
    for target, (source, subs) in P.items():
        src_path = AUX4 / "code" / source
        raw = src_path.read_bytes()
        rel = str(src_path.relative_to(ROOT))
        if aux4_manifest.get(rel) != sha(raw):
            raise SystemExit(f"Aux4 source {rel} does not match the committed Aux4 manifest v2")
        text = raw.decode()
        for i, (old, new) in enumerate(subs):
            n = text.count(old)
            if n != 1:
                raise SystemExit(f"{target}: anchor #{i} found {n} times (need exactly 1)")
            text = text.replace(old, new, 1)
        out = NS / "code" / target
        out.write_text(text)
        report["generated"][target] = {"source": rel, "source_sha256": sha(raw),
                                       "generated_sha256": sha(out.read_bytes()), "substitutions": len(subs)}
    (NS / "config").mkdir(exist_ok=True)
    (NS / "config/GENERATION_REPORT.json").write_text(json.dumps(report, indent=1, sort_keys=True) + "\n")
    print(json.dumps({k: v["substitutions"] for k, v in report["generated"].items()}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
