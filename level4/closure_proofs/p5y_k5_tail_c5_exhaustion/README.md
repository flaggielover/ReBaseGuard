# P5Y / K5 Campaign C5 — order-3-surrogate / rho deterministic exhaustion

C5 asks whether committed evidence can be recombined, with **zero new-real scientific addresses**, to materially
tighten the order-3 surrogate or the rho contribution for the remaining K5 tail — and, if not, what deterministic
family can be rigorously exhausted instead.

Successor to C4, which is complete and immutable. C2, C3 and C4 are unmodified. `NEW_REAL_SCIENTIFIC_ADDRESSES = 0`;
guard `REAL_SCIENTIFIC_COMPUTE = DENY`; no kernel evaluated, no operator certification run, no remote host contacted.

**The two main refs are different and stay different.** `LOCAL_MAIN_REF = c123b9bb`, `REMOTE_MAIN_REF = 1cb45382`.
C5 modifies neither and reconciles neither, and every audit here names which one it means.

| phase | artifact |
|---|---|
| B0 successor audit | `evidence/b0/C5_B0_AUDIT.json` |
| 1 blocker decomposition | `phase_1/C5_BLOCKER_DECOMPOSITION.md`, `evidence/phase1/C5_DECOMPOSITION.json` |
| 2 C4 sensitivity reproduction | `evidence/phase2/C5_SENSITIVITY.json` |
| 3-5 route search, ledger, kill gates | `phase_3/C5_ROUTE_SEARCH.md`, `evidence/ledger/C5_ROUTE_LEDGER.json` |
| 6 selected mechanism | `code/c5_transport.py` (theorem C5-T) |
| 7 frozen gate | `config/FEASIBILITY_GATES_C5.json` |
| 8 mutation suite | `evidence/mutations/C5_MUTATIONS.json` |
| 9 pre-forecast review | `review/REVIEW_C5_PREFORECAST_R2.md` (NOT_READY), `review/REVIEW_C5_PREFORECAST_R3.md` (the clearance) |
| 10 forecast | `evidence/forecast/C5_FORECAST.json` |
| 12 adjudication | `evidence/adjudication/C5_ADJUDICATION.md` — ACCEPTED_WITH_SCOPE_LIMITATION, adopted set [] |

Post-adjudication corrections are in `ERRATUM_C5_GATE.md` (E1–E9) and `OPEN_NOTES_DISPOSITION_C5.md`.

## What C5 found, in one paragraph

The K5-B direct clause is `Gamma = g_hi + rho*x_hi*M`, and only `M` is improvable: `g_hi` is the sealed K1 record
and `rho`, `x_hi` are the cover. Inside `M`, **82% of the radius sum flows through `A0` times the order-3
surrogate and the order-4 envelope, while the genuinely measured residual contributes 0.1%.** Every route that
could move those is blocked on data that is not in the committed corpus (the K1 object candidates), or on new-real
measurement (a finer cover, an order-4 measurement, the R-stage). What *is* available is a strictly tighter
transport, theorem **C5-T**, which is exact, zero-new-real, and provably optimal for its input set.
