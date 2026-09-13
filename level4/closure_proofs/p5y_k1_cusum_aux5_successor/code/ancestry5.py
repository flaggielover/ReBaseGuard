"""Import bootstrap and predecessor facts for the Aux5 CUSUM successor.

Aux5 is the governed successor of `p5y_k1_cusum_aux4_fullcover` (commit f0954a9d), bound to the named host
`rebaseguard-vultr-02`. It changes ONLY the producer identity layer:

  EXTERNAL_VENV_LIBRARY_BINDING  Aux4 globbed backend libraries relative to the repository root, so an
                                 interpreter environment outside the tree bound an EMPTY map. Aux5 binds
                                 them by absolute resolved path from the site-packages actually imported.
  NAMED_HOST_RUNTIME_CONTRACT    host name, venv prefix, interpreter path and site-packages are bound; the
                                 arithmetic-relevant OpenBLAS (numpy's) is selected explicitly.

Everything scientific is imported in place and byte-identical: every Aux4 manifest-v2 science input, and the
Aux4 modules that define the scientific hash semantics (schema.py, hash_v2.py), the SciPy guard and the
predecessor import bootstrap (ancestry4.py). No Aux4 cell record is composed into any Aux5 ledger.
"""
from __future__ import annotations

import sys
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
ROOT = NS.parents[2]
AUX4_NS = ROOT / "level4/closure_proofs/p5y_k1_cusum_aux4_fullcover"

# Appended AFTER this namespace's own code directory (sys.path[0] for the runner), so no Aux4 identity-layer
# module can shadow an Aux5 one; the Aux5 modules carry distinct names in any case.
_AUX4_CODE = str(AUX4_NS / "code")
if _AUX4_CODE not in sys.path:
    sys.path.append(_AUX4_CODE)

import ancestry4                                                  # noqa: E402,F401  science sys.path bootstrap

AUX4_COMMIT = "f0954a9db09d22ad44151afdb557f823fe6eb393"
AUX4_IDENTITY = {
    "producer_manifest_hash": "72c75c2244f553d6fd08a6b1e0369eaaf01b2c3cda77a9e5a54943b6805b21cb",
    "runtime_contract_hash": "d49f043755ef658a60e3c4017022ddecf0642a087a6e5bb0c1f2aefbe9721191",
    "producer_identity_hash": "f85bd92cd5d32122d4b9618f5981c2a83653266b2a59b097339c6271ed9dcb7c",
    "status": "IMMUTABLE PREDECESSOR; its 2 cells (318, 323) are history, never composed",
}
BOUND_HOST = "rebaseguard-vultr-02"
ROUTE = {
    "chosen": "NEW_SUCCESSOR (p5y_postk1_precompute_resolution/CUSUM_SUCCESSOR_PREFREEZE.md)",
    "rejected": "RESTORE_AUX4: superseded apt CPython build + SkylakeX host shared with the live PS1 campaign",
}
