# Stage D — protocol deviations

`STAGE_D_PROTOCOL.md` was frozen at sha256
`925adecf08c7234375333a26c3af934b005e0d8b4cfce470b77834d7245e8b2e` before any
confirmatory data existed, and adversarial check **A12 re-verified that hash
after all campaigns finished**. It was never edited.

## Deviations from the frozen protocol

**None.** No criterion was rewritten, no tolerance widened, no grid point
dropped, no threshold re-tuned after a `Gamma` was seen, and no failed result
removed.

## Choices the protocol left open, committed in writing before the relevant data

The protocol fixes criteria but not every nuisance parameter. Each open choice
was written down and hashed **before** the data it governs was generated. These
constrain; none loosens anything.

| Note | sha256 | Fixes | Written before |
|---|---|---|---|
| `D2_3_STEP_PRECOMMIT.md` | `7b7a54c6…` | FD primary step `h = 0.05`, variants, Richardson-as-diagnostic, D1.4 scan grid and 3 SE crossing rule | any induced-map data |
| `D2_5_PRECOMMIT.md` | `fb6272ef…` | `rho = 1`, `m` grid, replicates, shifts, and the rule that monotone curves are reported as *mathematical, not operational* | any D2.5 data |
| `D3_REGULARITY.md` | `9eafbcd2…` | D3.1 assumptions A1–A7 with evidential labels, including A5 | any D3 data |

`D2_3_STEP_PRECOMMIT.md` predicted the D2.3 failure mode, and `D3_REGULARITY.md`
A5 predicted the t3 estimand ambiguity, in both cases before the run. That is
the only reason either may be offered as a diagnosis rather than as an excuse.

## Code changed after the freeze, and why each is not a deviation

| Change | Why it is not a deviation | Evidence |
|---|---|---|
| SR threshold units bug fixed in `stopped.py` | Found **before** any confirmatory data. The recursion compared `log R` against a natural-units threshold, so SR never alarmed. No result depended on the broken path. | `tests/test_stopped.py::test_sr_threshold_is_natural_units_not_log` |
| `zbar_num` / `zbar_sq` accumulators added | Purely additive post-processing of already-drawn values; D2 was re-run and reproduced **bit-identically**. | D2 gamma values byte-equal before and after |
| `score` hook added for D3 | Inactive when `score is None`, so Gaussian results are unaffected; with `psi = identity` it reproduces `Gamma` **bit-for-bit**. | verified in-session; `test_score_hook_identity` |
| D1.4 root uncertainty widened to include bisection resolution | A **correction of an overstatement**, not a loosened tolerance: the quoted MC SE (0.000651) was smaller than the bisection cell (0.001562), so the reported precision was an artifact of the grid. The corrected interval is *wider*. | `d1_4_sr_map.json: resolution_limited = true` |
| Adversarial A11 rewritten | The check matched its own search list. The replacement derives values from the results files and scans **more** values than the original literals. | `notes/FAILURE_DIAGNOSES.md` F2 |
| `run_d2_gamma_m.py` key renamed `sum_gamma_all_lags` → `sum_gamma_first_L_lags` | The original name was **inaccurate**: the sum runs over the first `L = 120` lags, not all lags. Renaming an artifact key to match what it holds is a correctness fix. | `d2_gamma_m.json` |

## Stop conditions (protocol §9) — none triggered

| Condition | Status |
|---|---|
| frozen artifacts change | **NO** — no file outside `stage_d/` modified after the freeze timestamp |
| baseline tests fail for non-Stage-D reasons | **NO** |
| confirmatory seeds overlap prior work | **NO** — `20261001` / `20261002` / `20261031` appear nowhere in prior work |
| estimator mathematically inconsistent with the protocol | **NO**, but see `CORRESPONDENCE_AUDIT.md` Addendum A1: the *blueprint's* closed form is inconsistent with its own asymptotic claim, which Phase 0 refuted before the freeze |
| production contradicts the pilot requiring protocol redesign | **Contradiction occurred (D2.5), redesign did not.** The protocol's D2.5 row already prescribed the wording for exactly this outcome, so the contradiction was reported, not redesigned around |
