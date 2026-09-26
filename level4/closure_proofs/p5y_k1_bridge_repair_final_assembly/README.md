# P5Y K1 bridge-repair final assembly (additive)

Binds the evidence below into `evidence/K1_REPAIR_ASSEMBLY.json`, which is produced by `code/assemble_k1_repair.py` (write-once; 11 gates):
- inherited B1 PASS (Aux5 composite admission);
- historical compact evidence: CUSUM 326 cells on [0, 11/2]; SR PS1 369 cells on [0, c_SR];
- the inherited P5X-T3 far field;
- the genuine K1R4 SR bridge: 6 cells on [33777657/5000000, 1883835/262144];
- the genuine K1R6 CUSUM bridge: 2 cells on (11/2, 49750555/8388608];
- the exact domain composition (both unions [0, infinity), uncovered width 0);
- producer identities, authorizations, runtime identities, and CPU accounting.

Sealed production evidence is copied byte-for-byte into `evidence/sealed/`. The SR patch archives (~30 MB, under
`/home/ubuntu/work/k1-bridge-prod/`) are bound by SHA-256.

This is a producer assembly, not an adjudication. It sets only `READY_FOR_INDEPENDENT_K1_SUCCESSOR_ADJUDICATION`,
never declares K1 CLOSED, and changes no historical state: P5 = P5X = P5Y-K1 = PARTIAL.
