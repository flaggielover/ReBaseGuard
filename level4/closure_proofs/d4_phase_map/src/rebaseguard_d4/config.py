"""Protocol-frozen D4 constants."""

from __future__ import annotations

from pathlib import Path

import numpy as np

CAMPAIGN = Path(__file__).resolve().parents[2]
REPO = Path(__file__).resolve().parents[5]
RESULTS = CAMPAIGN / "results"

PROTOCOL_SHA256 = "107a9597da6f4baad328e949745c75b486b10753a12086e0eb267100fd6964a0"
MASTER_SEED = 2026082404
Z95 = 1.959963984540054
BOUNDARY_TOLERANCE = 1e-12
RHO_SAFE = 0.029796

M_GRID = np.array(
    [1, 2, 5, 10, 20, 35, 50, 60, 65, 70, 72, 75, 80, 90, 100, 150, 250],
    dtype=np.int64,
)
RHO_GRID = np.array(
    [0.0, RHO_SAFE, 0.05, 0.10, 0.20, 0.30, 0.40, 0.50,
     0.60, 0.70, 0.80, 0.90, 0.95, 1.00],
    dtype=float,
)

GAMMA_BATCHES = 64
GAMMA_BATCH_PATHS = 25_000

EPSILON_LADDER = np.array([0.025, 0.0125, 0.00625], dtype=float)
DIRECT_REPLICATIONS = 2
DIRECT_BATCHES = 20
DIRECT_BATCH_PATHS = 12_500
DIRECT_CELLS = (
    ("V1", 1, 0.20),
    ("V2", 20, 0.20),
    ("V3", 20, 0.40),
    ("V4", 50, 0.70),
    ("V5", 50, 0.80),
    ("V6", 100, 1.00),
)

OPERATIONAL_BATCHES = 20
OPERATIONAL_REPLICATES_PER_BATCH = 250
OPERATIONAL_CYCLES = 60
OPERATIONAL_BURN_IN = 20
OPERATIONAL_CELLS = (
    (20, 0.20),
    (20, 0.40),
    (50, 0.60),
    (50, 0.90),
    (100, 1.00),
)
