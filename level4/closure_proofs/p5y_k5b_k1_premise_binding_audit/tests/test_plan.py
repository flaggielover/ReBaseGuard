"""The plan is unexecuted, cannot reopen B3, and its pins match the base commit bytes."""
import hashlib
import json
import subprocess
from pathlib import Path

NS = Path(__file__).resolve().parents[1]
REPO = NS.parents[2]
PLAN = json.loads((NS / "config/AUDIT_PLAN.json").read_text())


def test_status_and_scope():
    assert PLAN["status"] == "PLAN_ONLY_NOT_EXECUTED"
    assert not (NS / "evidence").exists()
    assert "does not reopen B3" in PLAN["relation_to_B3"]
    assert set(PLAN["questions"]) == {"PB2_L5_LOAD_BEARING", "PB3_DERIVATIVE_AT_ZERO_CONVENTION", "PB4_IDENTITY_OF_R",
                                      "PB5_R2_WHOLE_CELL_IN_AUX5_RECORDS", "PB6_SOURCE_OF_R_AT_2"}


def test_pins_match_base_commit():
    for path, digest in PLAN["pinned_at_base_commit"].items():
        blob = subprocess.run(["git", "-C", str(REPO), "show", f"{PLAN['base_commit']}:{path}"],
                              capture_output=True, check=True).stdout
        assert hashlib.sha256(blob).hexdigest() == digest, path


if __name__ == "__main__":
    test_status_and_scope()
    test_pins_match_base_commit()
    print("ok")
