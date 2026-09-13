"""PHASE 2: the certifying trusted computing base, by exact path.

WHAT WAS WRONG WITH AUX3'S BOUNDARY
-----------------------------------
Aux3 decided coverage with a BASENAME whitelist:

    NON_CERTIFYING_BASENAMES = {..., "successor_producer.py", ...}

`successor_producer.py` is execution-relevant -- Aux3's own
`rejected_producer_identities()` imports it and puts its hash into the record,
inside the scientific hash -- yet the whitelist exempted it from coverage and it
was absent from the manifest. A basename is not an identity: any file anywhere in
the repository called `successor_producer.py` would have been exempted too.

THE RULE HERE
-------------
Membership is by exact repository-relative PATH. There is one set, `TCB_PATHS`,
enumerating every file whose bytes can change a certified number. Coverage asks
one question of every loaded repository module: is its exact path in that set? If
not, certification aborts. Nothing is exempted by name, and the non-certifying
modules of this namespace are simply never imported by the certifying process --
`tests/test_aux4.py` asserts that, so the boundary is a fact about what runs
rather than a promise about what was meant to run.

The set below is not guessed. It was MEASURED: a real certification was run with
`sys.modules` recorded, and every repository file that appeared is listed here.
`verify_coverage()` re-measures on every run.
"""
from __future__ import annotations

from pathlib import Path

import ancestry5
import ancestry4

# --- Aux4's own certifying modules ---------------------------------------
AUX5_MODULES = (
    "ancestry5.py", "tcb5.py", "runtime_identity5.py", "manifest_v3.py",
    "identity5.py", "qualify5.py",
)
# Aux4 modules imported IN PLACE and byte-identical: they define the scientific hash semantics,
# the field classification, the SciPy guard and the predecessor import bootstrap.
REUSED_AUX4_MODULES = ("ancestry4.py", "schema.py", "hash_v2.py", "scipy_guard.py")
# Aux4 identity-layer modules that must NEVER be loaded by the Aux5 certifying process.
AUX4_REPLACED_MODULES = ("tcb.py", "runtime_identity.py", "manifest_v2.py", "identity4.py", "qualify4.py")
# Aux5 namespace modules that are NOT certifying (never imported by the certifying process).
AUX5_NON_CERTIFYING = ("make_aux5.py", "analyze_qualification.py", "cap_formula.py")

# --- Aux3 science, imported and executed unchanged -------------------------
AUX3_MODULES = ("ancestry.py", "aux_collocation.py", "aux_certifier.py",
                "aux_refine.py", "aux_propagate.py")
# --- CUSUM completion successor modules actually executed ------------------
CUSUM_MODULES = ("order2.py", "refine2.py")
# --- final-completion modules actually executed ----------------------------
FINAL_MODULES = ("base.py", "sharp_norms.py", "sharp_certifier.py")
# --- Repair2 modules actually executed -------------------------------------
REPAIR2_MODULES = ("prior2.py", "producer.py", "certhash.py", "provenance.py",
                   "repair2_universe.py")
# --- Repair1 modules actually executed -------------------------------------
REPAIR1_MODULES = ("prior.py", "repair_layer2.py", "repair_scoped.py",
                   "repair_check.py", "repair_universe.py")
# --- reviewed-implementation modules actually executed ---------------------
REVIEWED_MODULES = ("spec.py", "intervals.py", "opnorms.py", "depgraph.py",
                    "universe.py", "assembly.py", "ledger.py", "refine.py",
                    "propagate.py", "scoped.py", "cusum_layer1.py",
                    "cusum_layer2.py", "qualify.py")
# --- frozen scientific inputs ---------------------------------------------
FROZEN_INPUTS = ("config/checkpoint.json", "config/cells.json",
                 "config/cover_witnesses.json", "config/record_schema.json",
                 "ERROR_ALGEBRA.md", "code/algebra.py")
# --- certified backend sources --------------------------------------------
BACKEND_INPUTS = (
    ancestry4.PROOF_SRC / "rebaseguard_certify/__init__.py",
    ancestry4.PROOF_SRC / "rebaseguard_certify/arb_backend.py",
    ancestry4.PROOF_SRC / "rebaseguard_certify/polynomial.py",
    ancestry4.PROOF_SRC / "rebaseguard_certify/residual.py",
    ancestry4.PROOF_SRC / "rebaseguard_certify/spectral_candidate.py",
    ancestry4.P5X / "certified_method_repair_ra/ra_certifier.py",
    ancestry4.P5X / "compute_optimization_r2/fast_range.py",
    ancestry4.GATE1 / "raw_certifier.py",
)
# --- generated artifacts whose CONTENTS affect certification ---------------
# Aux3's scipy probe influenced its runtime contract without being bound. Aux4
# binds every artifact it reads, including the predecessor manifest it cites as a
# rejected producer identity.
ARTIFACT_INPUTS = (
    ancestry4.AUX3_NS / "manifests/producer_manifest_v1.json",
    ancestry4.AUX3_NS / "evidence/scipy_execution_probe.json",
    ancestry5.AUX4_NS / "manifests/producer_manifest_v2.json",
)

# Third-party code lives outside the repository tree and is bound by the runtime
# contract's library hashes, not by this path set.
THIRD_PARTY_MARKERS = ("/.venv/", "/site-packages/")


def certifying_paths() -> list[Path]:
    out = [ancestry5.NS / "code" / n for n in AUX5_MODULES]
    out += [ancestry4.NS / "code" / n for n in REUSED_AUX4_MODULES]
    out += [ancestry4.AUX3_NS / "code" / n for n in AUX3_MODULES]
    out += [ancestry4.CUSUM_NS / "code" / n for n in CUSUM_MODULES]
    out += [ancestry4.FINAL_NS / "code" / n for n in FINAL_MODULES]
    out += [ancestry4.REPAIR2_NS / "code" / n for n in REPAIR2_MODULES]
    out += [ancestry4.REPAIR1_NS / "code" / n for n in REPAIR1_MODULES]
    out += [ancestry4.IMPL_NS / "code" / n for n in REVIEWED_MODULES]
    out += [ancestry4.SPEC_NS / n for n in FROZEN_INPUTS]
    out += list(BACKEND_INPUTS)
    out += list(ARTIFACT_INPUTS)
    return out


def tcb_paths() -> set[str]:
    """Exact repository-relative paths of every certifying input."""
    return {str(Path(p).resolve().relative_to(ancestry4.ROOT))
            for p in certifying_paths()}


def loaded_repository_files() -> list[str]:
    """Every repository file currently loaded as a module, by exact path."""
    import sys
    out = []
    for _, mod in sorted(sys.modules.items()):
        f = getattr(mod, "__file__", None)
        if not f:
            continue
        try:
            rel = str(Path(f).resolve().relative_to(ancestry4.ROOT))
        except ValueError:
            continue                                    # outside the repository
        if any(marker in "/" + rel for marker in THIRD_PARTY_MARKERS):
            continue                                    # bound by library hashes
        out.append(rel)
    return sorted(set(out))


def verify_coverage(tcb: set[str] | None = None) -> dict:
    """Fail-closed: every loaded repository module must be in the TCB by path."""
    tcb = tcb_paths() if tcb is None else tcb
    loaded = loaded_repository_files()
    uncovered = [p for p in loaded if p not in tcb]
    return {"ok": not uncovered,
            "loaded_repository_modules": len(loaded),
            "uncovered": uncovered,
            "tcb_size": len(tcb)}
