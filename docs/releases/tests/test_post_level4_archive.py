from __future__ import annotations

import importlib.util
from decimal import Decimal
from pathlib import Path

import pytest


MODULE = Path(__file__).resolve().parents[3] / "scripts/verify_post_level4_archive.py"
SPEC = importlib.util.spec_from_file_location("verify_post_level4_archive", MODULE)
assert SPEC and SPEC.loader
VERIFY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VERIFY)


def test_authorities_and_original_sr_tree() -> None:
    VERIFY.check_level4_authority()
    VERIFY.check_historical_tag()
    VERIFY.check_sr_authority()
    VERIFY.check_original_sr_files()


def test_current_documentation_and_reproducers() -> None:
    VERIFY.check_current_documentation()
    VERIFY.check_reproducers()


def test_leading_decimal_reads_arb_enclosure_center() -> None:
    assert VERIFY.leading_decimal("[5.800391799508442 +/- 1e-20]") == Decimal(
        "5.800391799508442"
    )


def test_stale_unqualified_sr_open_wording_fails_closed() -> None:
    with pytest.raises(VERIFY.VerificationError, match="unqualified current SR OPEN"):
        VERIFY.validate_current_doc_text(
            "current.md", "The rigorous SR Arb certificate remains open."
        )


def test_historical_sr_open_wording_is_allowed() -> None:
    VERIFY.validate_current_doc_text(
        "current.md",
        "At terminal Level-4 closure, the optional SR Arb certificate was OPEN; "
        "the post-Level-4 certificate is now closed.",
    )


def test_tracked_tree_has_no_generated_junk() -> None:
    VERIFY.check_repository_hygiene(allow_dirty=True)
