# K5_PERRON_DEFLATION_FEASIBILITY — certified Perron(atom)-deflated resolvent for the CUSUM K5 front

Additive namespace. Starting frontier `p5y-postk1-frontier` @ `5a8c194d`. Nothing outside this directory is modified.
No real scientific computation, no new real campaign namespace, no authorization or countersignature, no new R''' or R⁽⁵⁾.

| file | content |
|---|---|
| `theorem/OPERATOR_AUDIT.md` | first-principles audit of K_e: state space, atom, positivity, the slow mode (renewal / quasi-stationary), nonnormality |
| `theorem/THEOREM_AD.md` | theorem AD: exact rank-one atom deflation (Sherman–Morrison at x0 = (0,0)), deflated point errors of the frozen K1 DAG, tightening and consumption corollaries, certification obligations |
| `code/operator_float_diagnostic.py`, `code/operator_float_profile.py` | NON-CERTIFIED operator-only float diagnostics (no source, no candidate, no R value) |
| `code/deflated_consume.py` | the pre-registered deterministic consumer (theorem AD rule → tightened records → frozen K5-B), with a forecast mode that takes non-certified constants |
| `evidence/` | diagnostics, forecasts, certified operator registry (when built) |

Order of work (temporal integrity): theorem + consumer rule registered first; forecast (non-certified constants) second;
feasibility thresholds frozen before any certified operator prototype; certified prototype; qualification; review.
