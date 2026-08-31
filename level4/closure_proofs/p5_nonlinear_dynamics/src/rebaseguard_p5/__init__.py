"""Level-4 Priority-5 nonlinear reference-state dynamics (isolated namespace).

P5 imports the frozen P7 detector/cycle/chain primitives read-only.  Nothing in
this package is imported by P1-P4 or P7.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
P5 = ROOT / "level4" / "closure_proofs" / "p5_nonlinear_dynamics"
P7 = ROOT / "level4" / "closure_proofs" / "p7_statistical_consequences"
P3 = ROOT / "level4" / "closure_proofs" / "m_rho_stability_priority3"
RESULTS = P5 / "results"
FIGURES = P5 / "figures"

# read-only import of the frozen P7 package
if str(P7 / "src") not in sys.path:
    sys.path.insert(0, str(P7 / "src"))

SEED_FAMILY = 20260501           # P5 root seed; distinct from P7 (20260831/20260917)
SEED_FAMILY_ALT = 20261119       # independent replication family
DETECTOR_CODE = {"cusum": 11, "sr": 13}   # never hash(str)

CUSUM = "cusum"
SR = "sr"
