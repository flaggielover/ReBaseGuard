#!/usr/bin/env python3
"""Append one execution-ledger row: led.py RC "COMMAND" "PURPOSE"."""
import datetime
import json
import sys

LEDGER = "/tmp/claude-0/-home-user-ReBaseGuard/ede4e097-f9ec-54f5-9e84-81294f8ad688/scratchpad/t5/review/EXEC_LEDGER.jsonl"
rc, cmd, purpose = int(sys.argv[1]), sys.argv[2], sys.argv[3]
row = {"utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
       "command": cmd, "purpose": purpose, "rc": rc}
with open(LEDGER, "a") as fh:
    fh.write(json.dumps(row) + "\n")
