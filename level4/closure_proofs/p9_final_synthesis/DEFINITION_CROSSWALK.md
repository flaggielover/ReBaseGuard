# Definition crosswalk — where P1–P8 use the same name for different objects

The purpose of this file is to stop a reader from chaining two results that
share a symbol but not an estimand. Differences are **classified, not renamed**.

Classes: `IDENTICAL` · `ALGEBRAICALLY_EQUIVALENT` ·
`SAME_LIMIT_DIFFERENT_FINITE_ESTIMAND` · `DIFFERENT_BY_CONVENTION` ·
`DIFFERENT_QUANTITY` · `UNRESOLVED`.

---

## X-01 — the stopped-selection gain `Gamma`, across P1/P2/P4 and the core

| pair | class |
|---|---|
| core `Gamma` (m=1 CUSUM) vs P1 `GammaTilde_1` | `IDENTICAL` |
| P1 `GammaTilde_m = E_0[A_m T_tau]` vs P2 `GammaTilde_m^SR = E_0[A_m T_tau]` | `DIFFERENT_QUANTITY` |
| P1/P2 `GammaTilde_m` vs P4 `Gamma_{D,m,f} = E_0[A_m sum_{t<=tau} psi(Z_t)]` at `psi(z)=z` | `ALGEBRAICALLY_EQUIVALENT` |

The middle row is the one that misleads. P1 and P2 write the **same functional
expression** because both are `E_0[A_m T_tau]`; they are different numbers
because `tau`, `A_m` and `T_tau` are all measurable with respect to a different
detector's path. The empirical values differ throughout
(`15.92 / 13.26 / 11.96 / 10.23` vs `17.45 / 14.50 / 12.97 / 11.05`). Writing
"the gain" without naming the detector is a category error, and it propagates
straight into `rho_c`.

P4's specialisation is genuinely algebraic: `psi(z) = z` for the standard
Gaussian location family turns `sum_{t<=tau} psi(Z_t)` into `T_tau`.

---

## X-02 — **the most dangerous row**: local `Gamma` vs stationary `Gamma_eff`

| object | where | what it is |
|---|---|---|
| `GammaTilde` | P1, P2, P3, P4 | a **derivative at `e = 0`**: the stopped-selection gain of the conditional-mean map at the origin |
| `Gamma_eff = 1 + sbar` | P5-T11, P7-B | a **stationary average** under the invariant law `pi` |

**Class: `DIFFERENT_QUANTITY`.**

They enter two different formulas that look almost identical:

```text
rho_c = 1 / |1 - GammaTilde|          (P3: local boundary, at the origin)
ACF1  = rho (1 - Gamma_eff)           (P5-T11 / P7-B: stationary autocorrelation)
```

`GammaTilde ~ 10–17`; `Gamma_eff` is a `pi`-average of a selection strength
that **vanishes** away from the origin (P5-MECH), so it is much smaller. Any
sentence that computes a boundary from `Gamma_eff`, or an autocorrelation from
`GammaTilde`, is wrong. P9 found no repository artifact that does this — but
the two symbols are one letter apart and the formulas are one sign apart, so
the row is recorded as a standing hazard.

---

## X-03 — convention A vs convention B vs the Stage-A minimum-dwell process

| pair | class |
|---|---|
| convention A (`w = min(m,tau)`, denominator `w`) vs convention B (fixed-`m` denominator) | `DIFFERENT_BY_CONVENTION` |
| convention A vs the Stage-A minimum-dwell process, `m > 1` | `DIFFERENT_QUANTITY` |
| convention A vs the Stage-A minimum-dwell process, `m = 1` | `IDENTICAL` |
| convention A vs the Track-1B random-window convention | `DIFFERENT_BY_CONVENTION` |

P1's definition audit **proves** the second and third rows: the Stage-A process
is distinct for `m>1` and coincides only at `m=1`. This is why historical
Stage-D D2.3 and Track 1A remain failed while the Track-1B theorem stands — they
are results about different objects, not a repair (`PROJ-STAGED`). Convention A
and B must be "reported side by side and never merged".

The random denominator is not a technicality: it is what creates the exact
nonnegative short-cycle correction on `{tau < m}` that P1's and P4's proofs
both carry explicitly.

---

## X-04 — P3's derivative estimand vs P4's generalized estimand

**Class: `ALGEBRAICALLY_EQUIVALENT` in the limit;
`SAME_LIMIT_DIFFERENT_FINITE_ESTIMAND` for the numerical routes.**

P3 consumes the closed P1/P2 gains directly. P4 estimates its generalized gain
by two routes:

* **Route A** — the score route, an expectation of a stopped path functional;
* **Route B** — a finite-difference of `g_m` at step `h`.

These agree only as `h -> 0`. P4's adjudication traced the `skewnormal4/SR/m=2`
anomaly (`|z| = 4.29`) to exactly this: finite-step bias in the asymmetric
frozen-SR map, resolving to `0.09–0.56` combined SE at the smallest step pair.
P5's adjudicator independently labels the local derivative correspondence
`EXACT THEOREM` while its numerical estimates are
`CONSISTENT_WITH_NUMERICAL_BIAS`. Comparing a Route-A number to a Route-B number
at a coarse step is comparing two different finite estimands.

---

## X-05 — three different things all called "ARL"

**Class: `DIFFERENT_QUANTITY` (all three pairs).** P7-D0 makes the separation
mandatory.

| name | definition | frozen value |
|---|---|---|
| nominal `A(0)` | one cycle from a **perfect** reference, `e = 0` | CUSUM `465.12`, SR `464.86` |
| fresh-reference ARL (`rho = 0`) | `E[A(e)]` with `e ~ N(0, 1/m)` — a **mixture**, not `A(0)` | `79.91–162.03` |
| full-reuse ARL (`rho = 1`) | stationary average under the reuse chain | `48.36–80.05` |

The gap between rows 1 and 2 is a **matched-information / reset-reference**
effect — it is *not* reuse and *not* burn-in. Attributing the whole
`465 -> 48` drop to reuse inflates the reuse-attributable effect by roughly a
factor of two: the reuse-attributable loss is `39.5%–50.6%` (row 2 → row 3),
not `82.8%–89.6%` (row 1 → row 3). Both numbers are true; only one of them
answers "what does reuse cost?".

---

## X-06 — `rho_c` as a local boundary vs as an operational threshold

**Class: `DIFFERENT_QUANTITY`.** P3 defines `rho_c = 1/|1-GammaTilde|` as the
first-order local stability boundary of the deterministic conditional-mean map
at the origin. P7's `RHO_C_STATUS = LOCAL_MATHEMATICAL_BOUNDARY_ONLY` records
that under its frozen operational criterion this is **not** an operational
safety boundary. `rho < rho_c` is not a safety rule. There is no repository
quantity "operational `rho_c`"; the crossing hypothesis that would have created
one was rejected (`P7-R2`, 0/4 metrics peaked).

---

## X-07 — P5's fixed-policy kernel vs P6's closed-loop kernel

**Class: `DIFFERENT_QUANTITY`.** P5-T7 is stated per fixed `(D, m, rho)`: `rho`
is a constant. P6-T6B is a closed-loop invariant law for a **memoryless
admissible policy** `u` with `rho_max < 1`. P6's `THEORY.md` §4.3 enumerates the
differences rather than asserting that T6-B generalises T7.

Two consequences P9 enforces:

* A stationary quantity computed under fixed `rho` (P5, P7) may **not** be
  quoted as the stationary behaviour of the adaptive policy.
* Policies that **read the detector state** are outside T6-B entirely — not
  merely unproved, but outside the theorem's hypothesis class.

---

## X-08 — finite-horizon vs stationary operational metrics (P9-original)

**Class: `SAME_LIMIT_DIFFERENT_FINITE_ESTIMAND`.**

P9's independent reproduction (`CROSS_PRIORITY_REPRODUCTION.md`) measured the
full-reuse cycle length by cycle index and found the approach to stationarity is
**slow and oscillatory**, not monotone:

```text
SR,    m=1, rho=1, mean cycle length by cycle:
  460.5,  5.8,  73.7,  38.2,  53.6,  46.0,  48.6,  46.4, ... -> ~48.5
```

The resulting estimate depends materially on the averaging convention:

| convention | SR `m=1` | CUSUM `m=1` |
|---|---:|---:|
| discard cycle 1 | `46.96` | `48.34` |
| discard 3 | `47.81` | `49.33` |
| discard 6 | `48.22` | `49.84` |
| discard 10 | `48.49` | `49.97` |
| pool **all** cycles incl. cycle 1 | `67.64` | `69.31` |

The last row is `40%` above the stationary value purely because the perfect
first cycle is included. Any cross-priority comparison of an operational ARL
must state its burn-in convention; P9 found this explains a `45.21` vs `48.36`
apparent disagreement with P7 (`D-11`) with no scientific content whatsoever.

---

## X-09 — P4's `Gamma` vs Stage-D's `Gamma_psi`

**Class: `UNRESOLVED`** at the anchor commit.

A factor-of-`3.35` gap between a P4 value and a Stage-D D3 value is on record.
Claude's P8 discovery reports **provisionally** that the gap is *entirely
definitional*. P9 does **not** adopt that: it is
`PROVISIONAL_P8_PENDING_CODEX` (`P8-P5`). If Codex confirms it, this row
becomes `DIFFERENT_BY_CONVENTION`; if not, it stays `UNRESOLVED`. Separately,
Stage D is itself `PARTIAL`, so its `Gamma_psi` values are frozen conventions,
not closed premises.

---

## X-10 — the `P9` label collision

**Class: `DIFFERENT_QUANTITY`** — and it is not even a quantity comparison.
P5's premise ledger numbers its premises `P1`…`P15`; premise `P9` is the
`m`-monotonicity claim (`P5-N4`). It is **not** Priority 9. Eleven repository
occurrences of `P9` are all this premise. See `P9_DEFINITION_AUDIT.md` §3 `U1`.

The same collision exists for `P8` (premise `P8` = RMS/ARL co-optimality),
`P10` and `P11`. A reader who resolves `P8`/`P9` to priorities inside any
`p6_*` document will import the wrong claim.

---

## Summary

| class | rows |
|---|---|
| `IDENTICAL` | X-01 (core vs P1 at `m=1`), X-03 (`m=1` only) |
| `ALGEBRAICALLY_EQUIVALENT` | X-01 (P4 at `psi(z)=z`), X-04 (in the limit) |
| `SAME_LIMIT_DIFFERENT_FINITE_ESTIMAND` | X-04 (Route A/B), **X-08** |
| `DIFFERENT_BY_CONVENTION` | X-03 (A vs B, Track 1B) |
| `DIFFERENT_QUANTITY` | X-01 (CUSUM vs SR), **X-02**, X-03 (`m>1`), X-05, X-06, X-07, X-10 |
| `UNRESOLVED` | X-09 |

The two rows a reviewer should check first are **X-02** (local vs stationary
gain) and **X-05** (three ARLs), because both can be misused without producing
any visibly wrong number.
