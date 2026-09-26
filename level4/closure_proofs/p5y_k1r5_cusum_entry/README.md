# P5Y-K1R5-CUSUM-ENTRY

Narrow additive successor. Its **only** purpose is a qualified genuine production entry for the two
CUSUM bridge cells already frozen by K1R4 (indices 1000, 1001 over `(11/2, 49750555/8388608]`).
K1R4 froze those cells and the kernel but no orchestration to run them. SR is untouched.

**Why a wrapper and not the historical runner.** `qualify4.run_cell` resolves cells only from the
frozen 326-cell `spec.CELLS`, refuses when `spec.PRODUCTION_ENABLED`, and binds aux4's own producer
identity and TCB gate. It is neither edited nor called. `driver/k1r5_cusum_entry.certify()` re-executes
its statement block **verbatim** on the bridge cell dict; an AST test proves the blocks identical except
the cell source and the producer context. No scientific branch, threshold, formula or routine is copied:
every one is called.

**Identity.** Own producer manifest (the 58 aux4 kernel files, each re-verified against aux4's own
manifest, plus the wrapper), own producer identity bound through the unchanged `identity4` scheme,
own exact-path TCB gate. aux4's identity is not reused.

**Qualification.** 12/12 gates, 12/12 negative controls, 5/5 tests. No certificate was solved.
CUSUM may run concurrently with K1R4 SR.

    python3 driver/k1r5_cusum_entry.py --cell 1000 --evidence-dir <fresh dir> --task-id <id>
