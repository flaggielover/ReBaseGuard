#!/usr/bin/env python3
"""Record/check byte-stability of the audit-only generated artifacts."""
from __future__ import annotations

import argparse
import hashlib
import json

import audit
from config import BASE, RESULTS, canonical_json
from integrity import verify as verify_integrity


def build() -> dict:
    generated = audit.build_all()
    stable = {
        name: (RESULTS / name).exists()
        and (RESULTS / name).read_text() == canonical_json(value)
        for name, value in generated.items()
    }
    digest_input = b"".join(
        canonical_json(generated[name]).encode()
        for name in sorted(generated)
    ) + (BASE / "DECISION_RULE.md").read_bytes()
    integrity = verify_integrity()
    passed = all(stable.values()) and integrity["status"] == "PASS"
    return {
        "schema": "rebaseguard.l4r12-reproduction.v1",
        "status": "PASS" if passed else "FAIL",
        "offline": True,
        "new_science_run": False,
        "generated_artifacts": sorted(generated),
        "artifact_stability": stable,
        "audit_artifacts_byte_stable": all(stable.values()),
        "decision_rule_in_digest": True,
        "digest": hashlib.sha256(digest_input).hexdigest(),
        "protected_history": integrity["status"],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = build()
    path = RESULTS / "reproduction.json"
    if args.check:
        if not path.exists() or json.loads(path.read_text()) != result:
            print("L4R-12 reproduction record is not byte-stable")
            return 1
    else:
        path.write_text(canonical_json(result))
    print(f"L4R-12 reproduction: {result['status']} ({result['digest'][:16]}...)")
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

