# P5Y Gate-2E temporal ledger

| anchor | meaning | evidence |
|---|---|---|
| `T0` | metric derivation + preregistration frozen | `GATE2E_PREREGISTRATION.md`, committed with **no** file under `results/`. The metric constants are hashed into `GATE2E_SOURCE_MANIFEST.json` at the same commit |
| `T1` | code/config/source hashes frozen | same commit; 20/20 pre-T2 tests green, including the decisive negative control that an over-tight budget prevents the precision grid from being entered |
| `T2` | first result-bearing evaluation under the new metric | creation of `results/sr_metric.json` |
| `T3` | all frozen objects and precision cells complete | same artifact |
| `T4` | final report | `GATE2E_RESULT.md` |

**Anti-circularity:** every input to the threshold (`boundary = 2`,
`w_target = 0.2`, the ledger shape, `C_SR(1/4)`, `n_z + 2`) predates Gate-2D and
is recorded in the manifest before T2. Gate-2D residuals appear only in the
preregistration's falsifiable predictions, which section 1 of the brief permits.

Pre-T2 correction, before any result-bearing computation: one test string match
that did not account for whitespace in the preregistration text. No threshold,
budget, object, grid or rule changed.
