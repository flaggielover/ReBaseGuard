"""Restricted DEV_ONLY observation composition for Cell-308 conditions A1/A2.

The only public inputs are a committed attestation reference and an observation
mode. Repository and current-machine binding come from the platform's canonical
verifier; root provenance remains the platform's separate initial-namespace and
D-HOST-LIFETIME contract. A verified record alone never grants that contract.

Memory output contains raw Linux observations and withholds effective limit and
headroom. The other-campaign detector is unavailable. Every result remains
development_only with operational_ready False and A1/A2/A5 unmet. No science,
pin point, evaluator, qualification or campaign is imported or executed. Mode
names select proposed gate observations; they launch nothing or authorize a step.
"""
from __future__ import annotations

import lx_platform as L

__all__ = ("observe",)


def observe(attestation_ref=None, *, mode="execute") -> dict:
    """Compose canonical observations without caller-selected trust seams."""
    if mode not in L.MODES:
        raise ValueError(f"mode must be one of {L.MODES}")

    repo_root = L._repository_root()
    attestation, reasons = L.attestation_valid(attestation_ref, repo_root=repo_root)
    verified = isinstance(attestation, dict)
    memory = dict(L.memory_readings(attestation_ref=attestation_ref))
    # Raw observations cannot become R-FREE/R-MEM quantities or allowances here.
    memory.pop("effective_limit", None)
    memory.pop("cgroup_min_headroom", None)

    launched = L.launched_by_systemd()
    preflight = L.preflight(
        repo_root, mode=mode, other_job_running=None, launched=launched,
        attestation_ref=attestation_ref,
    )
    return {
        "schema": "rebaseguard.p5y.k5.newhost-cloud-r1.dev-observation.v1",
        "development_only": True,
        "operational_ready": False,
        "attestation": {
            "verified": verified,
            "record_root_cgroup_is_real": verified and attestation.get("root_cgroup_is_real") is True,
            "root_cgroup_is_real": verified and memory.get("root_attested") is True,
            "reasons": reasons,
        },
        "raw_memory": {
            "classification": "RAW_LINUX_READINGS",
            "readings": memory,
            "withheld_quantities": ["effective_limit", "cgroup_min_headroom"],
            "note": "No R-FREE/R-MEM rule quantity or operational allowance is established.",
        },
        "preflight": preflight,
        "conditions": {
            "A1": "DEV_COMPOSITION_ONLY_OPERATIONAL_REVIEW_UNMET",
            "A2": "DEV_COMPOSITION_ONLY_OPERATIONAL_REVIEW_UNMET",
            "A5": "UNMET_FIXED_SCIENCE_IMPORT_LIST_AND_PIN_POINT",
        },
    }
