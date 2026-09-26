# Frozen scope — P5Y-K1R5-CUSUM-ENTRY

* Cells: exactly `1000 = (11/2, 95887899/16777216]` and `1001 = (95887899/16777216, 49750555/8388608]`,
  read from the hash-verified K1R4 table. Historical 0–325 and every other index are refused.
* Consumed schema: affine `[p, "0/1"]` for left/right/e0/rho/C_evaluation; plain-string `C_upper`;
  `e0 = (left+right)/2`, `rho = (right-left)/2` exactly.
* Inherited unchanged: target `< 2`, m ∈ {1,2,3,5}, 256 bits, `B_cover` cap 1/20, 150 CPU-h shared cap.
* Kernel: the 58 aux4 kernel files, byte-identical. Result schema: aux4's 44 record keys plus
  `k1r5_bridge`; scientific hash `hash_v2.record_scientific_hash`; marker `cell_done_<index>.json`.
* Evidence: one fresh directory per cell (`exist_ok=False`), disjoint from every K1R4 SR root.
* Concurrency with K1R4 SR: permitted — no shared file, lock or ledger; per-process single thread.
