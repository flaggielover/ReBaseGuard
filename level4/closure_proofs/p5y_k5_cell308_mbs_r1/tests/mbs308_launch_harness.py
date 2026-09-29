"""MB-S r1 tests: the LAUNCHING side of the launchd integration test. Run by a shell in its own session; it installs the
transient LaunchAgent (test label org.rebaseguard.mbs308.test.<utc>, plist in scratch, logs under
~/Library/Logs/ReBaseGuard/mbs308-test/) whose program is the SYNTHETIC payload, writes the launch record (with the
launcher's detachment proof), then sleeps until the test kills its process group and session.

    mbs308_launch_harness.py <nss code dir> <scratch dir> <label> <payload args json>
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path


def main() -> int:
    code, scratch, label, pargs = sys.argv[1], Path(sys.argv[2]), sys.argv[3], json.loads(sys.argv[4])
    sys.path.insert(0, code)
    import mbs308_launch as L
    log_dir = Path.home() / "Library/Logs/ReBaseGuard/mbs308-test"
    program = [L.PYTHON, "-I", "-S", "-B", str(Path(__file__).resolve().parent / "mbs308_payload.py"), *pargs]
    try:
        rec = L.launch(program, label, scratch / "plists", log_dir, scratch, record_dir=scratch)
        (scratch / "launch_record.json").write_text(json.dumps(rec, indent=1, sort_keys=True))
    except L.LaunchRefused as e:
        (scratch / "launch_record.json").write_text(json.dumps({"refused": str(e)}))
        return 2
    time.sleep(600)
    return 0


if __name__ == "__main__":
    sys.exit(main())
