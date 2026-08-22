"""Outcome-blind constants copied from the frozen Track-3 protocol."""

from __future__ import annotations

FAMILIES = (
    "gaussian",
    "t10",
    "t5",
    "t3",
    "contam0.05",
    "contam0.1",
)

THRESHOLDS = {
    "gaussian": 5.0,
    "t10": 5.234517732360302,
    "t5": 5.669498491821448,
    "t3": 6.337011391962933,
    "contam0.05": 7.671712168173407,
    "contam0.1": 9.381983052368211,
}

HISTORICAL_ARL = {
    "gaussian": 465.599551,
    "t10": 466.565783,
    "t5": 464.873177,
    "t3": 465.891191,
    "contam0.05": 465.742994,
    "contam0.1": 464.356687,
}

H_STEPS = (0.05, 0.025, 0.0125)
PRIMARY_H = 0.0125
MASTER_SEED = 2026082307
K = 0.5
PROTOCOL_SHA256 = "52a27f178f91b88abfc78c28c327084eedafa61e6e91b24354a9faf1b3ed55f6"

ROUTE_A_BATCHES = 48
ROUTE_A_PATHS_PER_BATCH = 10_000
ROUTE_B_REPLICATIONS = 2
ROUTE_B_BATCHES = 48
ROUTE_B_PATHS_PER_BATCH = 5_000

