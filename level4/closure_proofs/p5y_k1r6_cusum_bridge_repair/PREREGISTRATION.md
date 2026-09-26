# Preregistration — P5Y-K1R6-CUSUM-BRIDGE-REPAIR

Written, qualified, committed and frozen before any genuine K1R6 computation.

Production (not run here) processes each of the cells 1000 and 1001 in a fresh evidence directory, in this order:
1. `run_cell` checks the thread contract, the 256-bit precision and that the evidence directory does not exist.
2. `bridge_cell` loads the cell from the hash-verified K1R4 table, and the schema is checked.
3. The identity resolver's record must equal the certified cell.
4. The initial TCB gate runs, then the K1R6 module binding, then the zero-case record is reset.
5. `certify` runs the frozen block, with `K1R6Certifier` as the only class difference.
6. `build_certificates` / `verify_chain` build the chain through `identity_k1r6`.
7. `assemble` produces the record, including the hashed `k1r6_bridge.zero_case` firing record, and the `hash_v2` scientific hash is computed.
8. The final TCB gate runs, then `ScipyGuard.require_clean()`, then the hash is rebound.
9. The final gate re-verifies and the module binding is checked again.
10. The record and marker are sealed atomically.

Every frozen kill gate applies. A module loaded outside the manifest, or a shadowed successor module, fails closed: nothing is sealed.
The zero base case fires only on the exact zero polynomial, and every firing is recorded.
Expected cost is 2 × 0.632 CPU-h; the previous 0.61 CPU-h of unsealed consumption is carried forward.
Committed CPU-h is read from each marker. The shared cap is 150 CPU-h.
K1R6 decides nothing about K1: P5 = P5X = P5Y-K1 = PARTIAL.
