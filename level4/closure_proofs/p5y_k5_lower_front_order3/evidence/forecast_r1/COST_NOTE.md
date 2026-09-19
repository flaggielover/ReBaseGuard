# Cost basis of the theorem-TC run (measured before the freeze; no real TC value computed)

- Dev replays (`tc_producer.py replay`, K1/Aux3 reproduction with the identity gate and the synthetic-G extraction code
  path, no order-3 candidate proposed) on rebaseguard-vultr-02, two processes in parallel on 4 physical cores:
  cell 11 **1398.97 CPU-s**, cell 44 **1406.14 CPU-s** (peak RSS ≈ 255 MB). Both identity gates identical (262 fields).
- Mode real adds the rung-3 candidate proposal (`Order3Certifier._candidates_rung3` recomputes the order-3 collocation,
  ≈ 170 CPU-s per the order-3 producer's own note); the five G residual certificates are already exercised by the
  replay's synthetic-G path. Forecast per cell ≈ 1575 CPU-s.
- 34 addresses + 2 reproductions = 36 cell runs ≈ 56 700 CPU-s ≈ **15.8 CPU-h**; with a 3 % margin **16.3 CPU-h**
  (preferred campaign budget 20, hard 40). Protocol cap **24 CPU-h** (enforced by `tc_run`: no cell is launched once
  the spent CPU plus the reservation would exceed it; any unlaunched address makes the run VOID).
- Workers: **4** (one per physical core). More workers do not reduce wall time on 4 cores and inflate per-process CPU
  time through SMT sharing. Forecast wall time ≈ 36 × 1575 / 4 ≈ 3.9 h.
- The earlier forecast in `ROUTE_FORECAST.json` (953 CPU-s per cell) under-estimated the K1 residual certification;
  the class STRONG does not depend on cost, and the corrected forecast stays inside the preferred budget.
