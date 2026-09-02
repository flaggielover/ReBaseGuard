"""P8R address-class discipline — the structural half of the P8 repair.

Why this module exists
----------------------
The authoritative P8 adjudication (`p8_model_class_robustness/
INDEPENDENT_ADJUDICATION.md` §3, §13) failed gate `G14` in part because the SR
calibration *search* was rerun after its *verification* result had been
inspected, and the rerun then re-verified at the **same** address
(``experiment="p8_sr_calibration_verify"``, ``batch=7``).  Disclosure of that
reuse ("amendment A2") did not restore holdout independence.

P8R makes address reuse of that kind **impossible by construction** rather than
by discipline.  Every experiment tag in this campaign must be minted through
:func:`tag`, which requires an explicit :class:`AddressClass`.  The class name is
part of the string that is SHA-256'd into the address's second component, so two
different classes can never produce the same address for any value of the
remaining components.

The four classes
----------------
``CAL_SEARCH``
    Every threshold-search evaluation, in every stage, including the frozen
    retry stage.  The search may consume as many of these addresses as the
    frozen plan allows.
``CAL_VERIFY_1``
    The single held-out acceptance sample for a calibrated threshold.  Written
    once per family.  Once its value has been read, that family's threshold may
    **never** be changed and re-verified here.
``CAL_VERIFY_2``
    The one pre-reserved second-tier holdout, usable only by the frozen retry
    rule in ``CALIBRATION_PLAN.md`` §5, and only for a family whose
    ``CAL_VERIFY_1`` acceptance failed.
``PRODUCTION``
    Every scientific production result.  Disjoint from all three calibration
    classes.

Disjointness is a theorem about the address tuple, not a convention: the tag
component is ``sha256("p8r/<class>/<name>")[:8]``, so a ``PRODUCTION`` address
and a ``CAL_SEARCH`` address agree only if two distinct 64-bit SHA-256 prefixes
collide.  ``tests/test_address_separation.py`` additionally checks every tag
this campaign actually mints, pairwise, by exhaustive enumeration, and checks
the delivered *values* differ across classes at identical remaining components.
"""
from __future__ import annotations

import hashlib
from enum import Enum


class AddressClass(str, Enum):
    """The four disjoint RNG address classes of the P8R campaign."""

    CAL_SEARCH = "cal_search"
    CAL_VERIFY_1 = "cal_verify_1"
    CAL_VERIFY_2 = "cal_verify_2"
    PRODUCTION = "production"


#: classes whose addresses may be consulted while a threshold is still being
#: chosen.  Reading anything outside this set during a search is a leak.
SEARCH_ADMISSIBLE = frozenset({AddressClass.CAL_SEARCH})

#: classes that may carry a scientific production estimand.
PRODUCTION_ADMISSIBLE = frozenset({AddressClass.PRODUCTION})

_PREFIX = "p8r"


def tag(cls: AddressClass, name: str) -> str:
    """Mint the experiment tag ``"p8r/<class>/<name>"``.

    ``name`` must be a non-empty ``[a-z0-9_]`` token so that the tag string is
    canonical and a tag can be parsed back into its class.
    """
    if not isinstance(cls, AddressClass):
        raise TypeError("cls must be an AddressClass, not a bare string")
    if not name or not all(c.isalnum() or c == "_" for c in name) \
            or name != name.lower():
        raise ValueError(f"illegal experiment name {name!r}")
    return f"{_PREFIX}/{cls.value}/{name}"


def class_of(experiment: str) -> AddressClass:
    """Recover the :class:`AddressClass` of a tag minted by :func:`tag`."""
    parts = str(experiment).split("/")
    if len(parts) != 3 or parts[0] != _PREFIX:
        raise ValueError(f"{experiment!r} is not a P8R experiment tag")
    return AddressClass(parts[1])


def require_class(experiment: str, allowed) -> AddressClass:
    """Assert that ``experiment`` belongs to one of ``allowed``; return it."""
    c = class_of(experiment)
    allowed = frozenset(allowed)
    if c not in allowed:
        raise PermissionError(
            f"experiment {experiment!r} is class {c.value}; this call site "
            f"admits only {sorted(a.value for a in allowed)}")
    return c


def tag_digest(experiment: str) -> int:
    """The 64-bit address component derived from a tag.

    Kept here rather than in ``primitives`` so that the address-separation test
    can reason about tags without materialising any random field.
    """
    class_of(experiment)          # reject anything not minted by tag()
    return int.from_bytes(hashlib.sha256(experiment.encode()).digest()[:8],
                          "big")


# ---------------------------------------------------------------------------
# The complete, frozen tag inventory of the campaign.
#
# Declared here BEFORE production so that the address-separation test is an
# exhaustive check over the real campaign rather than a spot check, and so that
# any tag introduced later is visibly absent from the anchored source digest.
# ---------------------------------------------------------------------------

CAL_SEARCH_ARL0 = tag(AddressClass.CAL_SEARCH, "sr_arl0")
CAL_VERIFY_1_ARL0 = tag(AddressClass.CAL_VERIFY_1, "sr_arl0")
CAL_VERIFY_2_ARL0 = tag(AddressClass.CAL_VERIFY_2, "sr_arl0")

PROD_ARL0_CHECK = tag(AddressClass.PRODUCTION, "arl0_check")
PROD_GAMMA_E1 = tag(AddressClass.PRODUCTION, "gamma_e1")
PROD_GAMMA_E5 = tag(AddressClass.PRODUCTION, "gamma_e5")
PROD_CHAIN_E3 = tag(AddressClass.PRODUCTION, "chain_e3")
PROD_DRIFT_E4 = tag(AddressClass.PRODUCTION, "drift_e4")
# NOTE: the independent reimplementation (``experiments/run_independent_repro``)
# deliberately draws from an entropy source **outside** this address system --
# a different bit generator, a different stream construction, a different window
# data structure -- so that its agreement with production is a genuine
# cross-check and not a replay of the same Philox field.  It therefore mints no
# tag here.
#: every tag the frozen campaign is permitted to use.
TAG_INVENTORY = (
    CAL_SEARCH_ARL0,
    CAL_VERIFY_1_ARL0,
    CAL_VERIFY_2_ARL0,
    PROD_ARL0_CHECK,
    PROD_GAMMA_E1,
    PROD_GAMMA_E5,
    PROD_CHAIN_E3,
    PROD_DRIFT_E4,
)
