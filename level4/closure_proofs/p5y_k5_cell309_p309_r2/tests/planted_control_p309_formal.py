"""q309: planted-control -- formal-namespace planted negative control for code/p309_scan.py (NEVER RUN, NEVER IMPORTED).

Each statement below is a deliberate violation that the scan must detect.  The module raises at import, and nothing
below ever executes.  Research kinds: CELL_LITERAL, BAND_LITERAL, FORBIDDEN_IMPORT, TARGET_PATH.  Formal kinds:
MARKER_MUTATION, MARKER_ALIAS, MARKER_REBIND, GRANT_WRITE; owner D5 kinds: REF_MUTATION_UNLISTED, MARKER_TOKEN,
REF_FILE_WRITE; R4 follow-up F1(b) process kinds: PROCESS_FORBIDDEN, PROCESS_SHELL, PROCESS_UNLISTED, PROCESS_ALIAS,
RUNNER_ALIAS, DYNAMIC_IMPORT, DYNAMIC_EXEC, GIT_OPTION_FORBIDDEN, GIT_CALL_OPAQUE, GIT_WRITE_UNLISTED, GITDIR_WRITE; R4 follow-up 2 closed-world kinds:
IMPORT_UNLISTED, INTROSPECTION, ENV_UNLISTED.
"""
raise SystemExit("planted control: never run")

import os  # noqa: E402
import subprocess  # noqa: E402
import sys  # noqa: E402
from fractions import Fraction  # noqa: E402
from pathlib import Path  # noqa: E402

import tct_rule  # noqa: E402,F401  FORBIDDEN_IMPORT
import p309_guard as G  # noqa: E402

CELL = 309                                   # CELL_LITERAL
DRIFT = Fraction(7, 5)                       # BAND_LITERAL
INPUTS = "TCT_INPUTS_309.json"               # TARGET_PATH
PRODUCTION_MARKER = G.PRODUCTION_MARKER      # MARKER_ALIAS (another binding of the marker name)
G.PRODUCTION_MARKER = G.TEST_MARKER          # MARKER_REBIND
subprocess.run(["git", "update-ref", G.PRODUCTION_MARKER, "HEAD"])                      # MARKER_MUTATION
Path(G._PROD_GRANT_PATH).write_text("{}")                                                # GRANT_WRITE
TOKEN = "refs/p5y-k5-cell309-p309-r2" + "/elsewhere"                                        # MARKER_TOKEN
open(".git/refs/heads/planted", "w")                                                     # REF_FILE_WRITE
os.system("git status")                                                                  # PROCESS_FORBIDDEN
subprocess.run("git status", shell=True)                                                 # PROCESS_SHELL
subprocess.run(["bash", "-c", "true"])                                                   # PROCESS_UNLISTED
RUN = subprocess.run                                                                     # PROCESS_ALIAS
RUNNER = G._git                                                                          # RUNNER_ALIAS
__import__(sys.argv[1])                                                                  # DYNAMIC_IMPORT
exec(sys.argv[2])                                                                        # DYNAMIC_EXEC
G._git(Path("."), "-c", "alias.x=update-ref", "x")                                       # GIT_OPTION_FORBIDDEN
G._git(Path("."), *sys.argv)                                                             # GIT_CALL_OPAQUE
G._git(Path("."), "hash-object", "-w", "planted")                                        # GIT_WRITE_UNLISTED
(Path(".git") / "planted").write_text("x")                                               # GITDIR_WRITE
import runpy  # noqa: E402                                                                # IMPORT_UNLISTED
vars(G)                                                                                  # INTROSPECTION
subprocess.run(["git", "status"], env={"GIT_CONFIG_COUNT": "1"})                        # ENV_UNLISTED
