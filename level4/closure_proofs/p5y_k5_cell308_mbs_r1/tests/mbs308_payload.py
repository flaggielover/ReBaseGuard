"""MB-S r1 tests: the SYNTHETIC launchd payload (never the driver's target path). It runs as the transient LaunchAgent
the launcher installs, starts the caffeinate supervisor for its own pid, writes a campaign pidfile into a scratch
repository's spool, and loops (heartbeat + the supervisor's record, atomically replaced every 0.25 s) until a stop file
appears or 240 s pass.

    mbs308_payload.py <nss code dir> <scratch git repo> <state file> <stop file>
"""
from __future__ import annotations

import json
import locale
import os
import sys
import time


def main() -> int:
    code, repo, state_file, stop_file = sys.argv[1:5]
    sys.path.insert(0, code)
    import mbs308_host as H
    import mbs308_state as S
    st = S.Store(repo, "refs/heads/main")
    events = []
    sup = H.CaffeinateSupervisor(sink=events.append, poll_s=0.1).start()
    pid_rec = S.write_pidfile(st, {"mode": "synthetic-payload", "label": os.environ.get("MBS308_LAUNCH_LABEL")})
    info = {"pid": os.getpid(), "ppid": os.getppid(), "pgid": os.getpgid(0), "sid": os.getsid(0),
            "xpc_service_name": os.environ.get("XPC_SERVICE_NAME"), "label": os.environ.get("MBS308_LAUNCH_LABEL"),
            "launched_by_launchd": H.launched_by_launchd(), "preferred_encoding": locale.getpreferredencoding(False),
            "identity": pid_rec["identity"]}
    t0, n = time.time(), 0
    while time.time() - t0 < 240 and not os.path.exists(stop_file):
        n += 1
        rec = dict(info, heartbeat=n, utc=S.utc(), caffeinate_pid=sup.current_pid(), supervisor=sup.record())
        tmp = state_file + ".tmp"
        with open(tmp, "w") as fh:
            json.dump(rec, fh)
        os.replace(tmp, state_file)
        time.sleep(0.25)
    sup.stop()
    return 0


if __name__ == "__main__":
    sys.exit(main())
