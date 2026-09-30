"""q309: planted-control -- formal-namespace planted negative control for code/p309_scan.py (NEVER RUN, NEVER IMPORTED).

Each statement below is a deliberate violation that the scan must detect.  The module raises at import, and nothing
below ever executes.  Research kinds: CELL_LITERAL, BAND_LITERAL, FORBIDDEN_IMPORT, TARGET_PATH.  Formal kinds:
MARKER_MUTATION, MARKER_ALIAS, MARKER_REBIND, GRANT_WRITE.
"""
raise SystemExit("planted control: never run")

import subprocess  # noqa: E402
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
