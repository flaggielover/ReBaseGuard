# P5Y K2/K3 final independent countersignature

Generated 2026-09-27T06:01:12Z. This record is additive and binds the review to source commit `6f1d351bd12c57d6438c61dda4bdd6aa2b46528a`, which is an ancestor of the checked frontier tip `5289b6cee7134dd66e3289c3a210c8de5abb6a2c`.

## Verdict

| Obligation | Independent countersignature | Scientific status |
|---|---|---|
| K2: `s_min = inf_e S_{D,m}(e) > 0` for CUSUM/SR and `m = 1,2,3,5` | **PASS** | **CLOSED** |
| K3: `M_2 = sup_e E_e[Rbar^2] < infinity` for the same frozen cases | **PASS** | **CLOSED** |

No scientific experiment or theorem rerun was performed. The review used exact arithmetic for the published rational constants and a fresh repository/history audit of the frozen downstream consumers.

## K2 review

The frozen packet's analytic proof applies to all real `e`. Its exact lower constants are

* CUSUM: `kappa = 121/46875`, from `G = 11` and `M = 125/22`;
* SR: `kappa = 49/30000`, using `log(A) < 13/2`, `G < 14`, and `M < 50/7`.

An exact rational replay confirms the factorial bounds `e_6 = 1957/720` and `sum 1/(2^k k!)` through `k=4` equals `633/384`; their product exceeds `663`, so the SR logarithmic bound is strict. Dividing either positive constant by `m^2` remains strictly positive for all four frozen values of `m`, covering all eight `(D,m)` cases without floating-point tolerance.

## K3 review

The later frozen P5X theorem consumes only finiteness of `M_2`, together with the K2 positivity lower arm. The historical consumer audit contains no binding numerical tightness criterion. In particular, `M_2 <= 100*s_min` is not a requirement and is not adopted here.

The frozen P5-T4/T5 argument supplies the exact uniform bounds `M_2 <= 10/Phi(-1)^10 <= 9.8959e8` for CUSUM and `M_2 <= 1/Phi(-(log(A)+1/2)) <= 1.4054e11` for SR, uniformly over the frozen `m` values and all real `e`. Therefore K3 is discharged as written.

## Provenance and status

The source packet files and their Git blob/SHA-256 identities are recorded in `FINAL_COUNTERSIGNATURE.json`. Their history shows introduction at the bound source commit only, with no later modification. Earlier adjudication and theorem-consumer records remain preserved. This publication adds only this namespace; it does not rewrite the source packet.

The public status is **K2 CLOSED, K3 CLOSED, K4 OPEN, K5 OPEN**. The existing K5 stop remains in force, and P5Y is not represented as fully closed.
