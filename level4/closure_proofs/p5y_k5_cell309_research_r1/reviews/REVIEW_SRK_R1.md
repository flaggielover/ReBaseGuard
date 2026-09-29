# Independent route review R1 of SRK (cell-309 research campaign r1)
ROUTE_REVIEW: PENDING (review in progress; the reviewer decoy declaration below is written before those runs)

## Reviewer decoy declaration (written 2026-09-29T15:39Z, before any reviewer certification run)

Under the brief's "Allowed running" clause, the reviewer declares exactly these two extra decoy runs. Both use the
declared synthetic geometry h = 3, k = 1/2 on the declared block E = [1/4, 9/32], Hermite index 1, degree 8 only
(no rung above 8), and they call `certify_W` / `certify_weight` directly. Nothing is written into the repository
except this review: outputs go to the reviewer's scratchpad, and the campaign exec-ledger path is redirected there.

| id | purpose (THEOREM_SRK §8) | run | expected |
|---|---|---|---|
| RD-1 | test 1, too-small weight | whole kernel, `certify_weight(..., mutant="shrink_window")`, certificate JSON via `certificate_json`, then `verify/srk_verify_indep.py` (whole kernel) | REJECT (FALSE), or PROVED TRUE with the proof recorded |
| RD-2 | test 2, taboo instead of whole | taboo kernel (`certify_W(..., whole=False)`), certificate JSON as the producer writes it (no `kernel` key in the hashed body), verified twice: as-is (whole kernel) and with file-level `kernel: taboo` | REJECT as whole; ACCEPT as taboo |
