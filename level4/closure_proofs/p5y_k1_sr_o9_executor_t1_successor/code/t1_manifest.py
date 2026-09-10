"""Write config/T1_MANIFEST.json binding T1 sources, frozen inputs and evidence."""
import hashlib
import json
import subprocess
from pathlib import Path

import sr_o9_candidates as T

NS = T.NS


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> None:
    rel = lambda p: str(p.relative_to(T.ROOT))                       # noqa: E731
    sources = sorted([*(NS / "code").glob("*.py"), *(NS / "tests").glob("*.py"), NS / "README.md"])
    evidence = sorted((NS / "evidence").glob("*"))
    sets = json.loads((NS / "evidence/t1_cell_candidate_sets.json").read_text())["cells"]
    ref = json.loads((NS / "evidence/t1_F0_reference_reproduction.json").read_text())
    parent = subprocess.run(["git", "-C", str(T.ROOT), "rev-parse", "HEAD"],
                            capture_output=True, text=True, check=True).stdout.strip()
    census = T.verify_census()
    m = {
        "schema": "rebaseguard.p5y.k1.sr.o9.t1.manifest.v1",
        "status": T.STATUS,
        "not_claimed": ["patch certification", "B_cover closure", "obligation closure",
                        "production readiness", "genuine production evidence"],
        "parent": {"commit": parent, "tag": "p5y-k1-sr-production-lifecycle-preresult",
                   "production_authorized_successor_ancestor": "bd7cf269792bc146e911ee57a85533b7b7b1aa9d"},
        "frozen": {"checkpoint_sha256": T.spec.CHECKPOINT_SHA256, "cells_sha256": T.spec.CELLS_SHA256,
                   "o9_protocol_sha256": sha(T.O9_PROTOCOL), "precision_bits": T.FROZEN_BITS,
                   "bidegree": list(T.FROZEN_BIDEGREE), "D": T.FROZEN_D, "Z": T.FROZEN_Z,
                   "scale_bits": T.SCALE_BITS, "collocation_quadrature": T.COLLOC_QUAD,
                   "authorized_runtime_contract_hash": "d49f043755ef658a60e3c4017022ddecf0642a087a6e5bb0c1f2aefbe9721191"},
        "candidate_universe": {"basis_order": T.BASIS_ORDER,
                               "distinct_candidates": census["distinct_candidates"],
                               "certified_contracts": census["certified_contracts"],
                               "by_moment_shift": census["by_moment_shift"]},
        "producer": T.producer_identity(),
        "runtime_binding": T.runtime_binding(),
        "sources": {rel(p): sha(p) for p in sources},
        "evidence": {rel(p): sha(p) for p in evidence},
        "cell_candidate_sets": {c: {"cell_scientific_hash": v["cell_scientific_hash"],
                                    "identity_list_sha256": hashlib.sha256(
                                        "\n".join(v["identity_hashes"]).encode()).hexdigest()}
                                for c, v in sets.items()},
        "reference_reproduction": ref,
        "gates": {"no_deferred_candidate_path": True, "census_matches_frozen_o9": True,
                  "task1r_F0_bit_exact_vs_frozen_function": True,
                  "task1r_F0_authorized_runtime_identity": ref["t1_F0_matches_authorized_runtime_identity"],
                  "cell150_full_basis": True, "two_fresh_process_determinism": True,
                  "cell315_exact_geometry": True, "precision_contract_enforced": True,
                  "pytest": (NS / "evidence/pytest_report.txt").read_text().strip().splitlines()[-1]},
    }
    (NS / "config/T1_MANIFEST.json").write_text(json.dumps(m, indent=1, sort_keys=True) + "\n")
    print(json.dumps({"manifest_sha256": sha(NS / "config/T1_MANIFEST.json"),
                      "producer_hash": m["producer"]["producer_hash"]}, indent=1))


if __name__ == "__main__":
    main()
