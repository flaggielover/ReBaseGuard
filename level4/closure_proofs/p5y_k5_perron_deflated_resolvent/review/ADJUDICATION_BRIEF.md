# Brief for the independent adjudication of the sealed Perron-deflated consumption (to be used after the seal)

The adjudicator is a fresh context with no access to the producer's reasoning. It must reproduce, not trust.

1. From GitHub, clone `p5y-postk1-frontier` at the seal commit into its own directories: one on the Mac, one on
   rebaseguard-vultr-02 (`/root/work/k5p-adjudication`). Confirm that the freeze commit precedes the qualification commit,
   which precedes the seal, and that `git diff <5a8c194d>..<seal>` touches only `p5y_k5_perron_deflated_resolvent/`.
2. Recompute every pin of `config/SUCCESSOR_PROTOCOL.json`. Check the certifier runtime on vultr-02 against the protocol.
3. Registry: run `build_registry.py verify` on a declared deterministic sample (at least cells 11, 12, 40, 41, 80, 132,
   133, 144, 148 and 3 random blocks, seeded by the seal commit hash), or in full, and require byte identity. Run X-B in
   full.
4. Run `falsify_registry.py` (in full or on the same sample), also with its quadrature doubled (GL128), and require PASS.
   Compare its outputs by verdict and by values within tolerance (≈ 1e-12 relative), not by bytes: float results depend on
   the host in the last digits (review r3 F5). S01 (Arb) must be byte-identical on the pinned runtime.
5. Run the T-EXT replay (`deflated_consume.py replay`) and require byte identity with the adopted consumption.
6. Run `deflated_consume.py consume` at the seal head and require the result to be byte-identical to the sealed result
   (the result is a pure function of the frozen inputs; the evaluation head is recorded only in the ledger).
7. Independently re-derive, with its own code, the tightened R, R', R'' intervals of at least cells 11, 45, 100 and 148
   for every m from the raw records and the registry (theorem AD r2 formulas), and the frozen K5-B verdicts of those cells.
8. Audit the theorem use: the frozen ERROR_ALGEBRA premises, the Aux5 producer chain (S09 evidence), Corollary T, the
   T-EXT C2 intersection, and the monotonicity of K5-B.
9. Verdict: ADOPTED or NOT_ADOPTED, with a numbered checklist of PASS/FAIL checks. Report anything that differs.
