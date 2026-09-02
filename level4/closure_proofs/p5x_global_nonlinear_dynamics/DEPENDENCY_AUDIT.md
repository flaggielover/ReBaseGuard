# P5X proof dependency audit (Phase 2)

Built from the completed Phase-1 proofs (`PROOF.md`) and the frozen statements.
Every node carries exactly one class:

```text
ANALYTICALLY_PROVED       proved in PROOF.md or imported as an adjudicated theorem
CERTIFIED_SCALAR_REQUIRED true once a named outward-rounded interval exists
EMPIRICAL_ONLY            Monte Carlo; may never appear in a proof path
OPTIONAL                  not required by the mechanism theorem
```

---

## 1. Graph

```text
IMPORTED (adjudicated, ANALYTICALLY_PROVED)
  P5-T1  raw-mean identity ............. convention A
  P5-T2  M = rho R ,  V = rho^2 S + (1-rho)^2/m
  P5-T3  R odd, S even, R(0) = 0
  P5-T4  sup_x E_{x,e}[tau] <= C_D  (from any state, uniform in e)
  P5-T5  uniform even moments; Jensen step Rbar^2 <= sum_{t<=tau} raw_t^2
  P5-T7  unique invariant pi, all moments, per fixed (D,m,rho)
  P3     lambda(rho) = rho (1 - GammaTilde) ; rho_c = 1/|1-GammaTilde|
  ARB    Gamma_CUSUM, Gamma_SR enclosures at e = 0, m = 1

        P5-T4 ---------------------------+
          |                              |
          v                              v
  L1 (ANALYTICALLY_PROVED) ---------> P5X-T1  (a) invertibility
     ^        |                              (b) terminal-innovation identities
     |        |                              (c) convention-A selection map
  P5-T1       +--> L2 (ANALYTICALLY_PROVED) --> P5X-T2  second moments  [needs K_{z2,e}, D2]
     |        |
     |        +--> L5 (ANALYTICALLY_PROVED) --> smoothness in e -> low-degree candidate per cell
     |
  P5-T3,T5 --> L3 (ANALYTICALLY_PROVED) --> P5X-T3  far-field forgetting, explicit B_D

  P5X-T1 + L5 + [C5 resolvent] + [C1 cover] ==> P5X-T4  sup_e |R| <= R_max < 2
                                                        (CERTIFIED_SCALAR_REQUIRED)
  P5X-T3 closes |e| >= e_far analytically; C1 covers [0, e_far]

  P5X-T4 + P5-T2 ==> P5X-T5  global drift / trapping interval
                             (ANALYTICALLY_PROVED given the scalar R_max)

  P5X-T2 + [C2] ==> s_min = inf_e S > 0 ,  M_2 = sup_e E[Rbar^2] < infinity
                    (CERTIFIED_SCALAR_REQUIRED)

  P5-T2 + P5-T5 + P5-T7 --> L6 (ANALYTICALLY_PROVED) --> exact identity
  L6 + s_min + M_2 ==> P5X-T6  two-sided stationary dispersion bound
                               upper : CERTIFIED_SCALAR_REQUIRED (M_2)
                               lower : CERTIFIED_SCALAR_REQUIRED (s_min)

  P3 + ARB + P5X-T4 + P5X-T3 + P5X-T6 ==> P5X-T9  mechanism synthesis

  ---- optional, not on the mechanism path ----
  C3 (R' enclosures) ==> P5X-T7 shape; discharges H2/H3a/H3b        OPTIONAL
  L8 + C4            ==> P5X-T8 skeleton global dynamics            OPTIONAL
  L7 + C6 (M_4)      ==> P5X-T6b anti-concentration                 OPTIONAL
  L4                 ==  NOT PROVED (D3); replaced per cell by a drift-explicit
                         block-forcing resolvent bound proved from scratch
```

## 2. Node classification

| node | class | note |
|---|---|---|
| `P5-T1`,`T2`,`T3`,`T4`,`T5`,`T7`, `P3` | `ANALYTICALLY_PROVED` | imported at adjudicated scope; never restated as P5X work |
| existing `Gamma` enclosures | `CERTIFIED_SCALAR_REQUIRED` (already satisfied) | imported unchanged; used only by gate `G2` and by `P5X-T9`(1) |
| `L1` → `P5X-T1` | `ANALYTICALLY_PROVED` | exact; no numerics |
| `L2` → `P5X-T2` | `ANALYTICALLY_PROVED` | exact; needs `K_{z2,e}` (`D2`) |
| `L3` → `P5X-T3` | `ANALYTICALLY_PROVED` | one trivial certified scalar `B_D(e_far)` |
| `L5` | `ANALYTICALLY_PROVED` | qualitative; nothing certified depends on it |
| `L6` | `ANALYTICALLY_PROVED` | exact identity |
| `C1` cover of `R` on `[0, e_far]` | `CERTIFIED_SCALAR_REQUIRED` | mandatory |
| `C2` cover of `E[Rbar^2]`, `S` | `CERTIFIED_SCALAR_REQUIRED` | mandatory |
| `C5` per-cell resolvent | `CERTIFIED_SCALAR_REQUIRED` | mandatory; supplied per cell, not imported |
| `R_max`, `s_min`, `M_2` | `CERTIFIED_SCALAR_REQUIRED` | the only three numbers the mechanism theorem needs |
| `P5X-T4`, `P5X-T6` | `CERTIFIED_SCALAR_REQUIRED` | exact statements, certified constants |
| `P5X-T5`, `P5X-T9` | `ANALYTICALLY_PROVED` given those three scalars | pure algebra above the scalars |
| `C3`, `P5X-T7` | `OPTIONAL` | Level C |
| `L8`, `C4`, `P5X-T8` | `OPTIONAL` | Level D, skeleton only |
| `L7`, `C6`, `P5X-T6b` | `OPTIONAL` | anti-concentration |
| `L4` | **NOT PROVED** (`D3`) | not on any path; replaced per cell |
| P5 measured maps, chain statistics, the `feasibility/` probes | `EMPIRICAL_ONLY` | correspondence and falsification only |

## 3. The Monte-Carlo firewall, checked

Walking the graph backwards from `P5X-T9`, its premise closure is

```text
{ P3, ARB(Gamma), P5-T2, P5-T3, P5-T4, P5-T5, P5-T7,
  L1, L3, L6, P5X-T1, P5X-T2 (m>=2 only), P5X-T3, P5X-T4, P5X-T5, P5X-T6,
  C1, C2, C5, R_max, s_min, M_2 }
```

No node in that closure is `EMPIRICAL_ONLY`. In particular:

* the `feasibility/` probes (`reduction_probe.json`, `sr_domain_check.json`) are
  reachable from **no** theorem node — the first is a falsification test of `L1`
  and the second a witness for `D1`; a falsification test that did not falsify
  contributes no premise;
* P5's measured `R`, `S`, `rho_c`, `sup|R|` values are reachable only from the
  empirical correspondence checks `E1`–`E6`, which are consumers, not premises;
* the mechanism theorem's three constants come from `C1`/`C2`/`C5` alone.

`FROZEN_GATES.md` `G8` is the mechanical enforcement of this walk.

## 4. What the graph shows about risk

The mechanism theorem has a **single** point of numerical failure: the width of
the certified enclosures, which enters only through `R_max`, `s_min`, `M_2`. It
has a **single** point of mathematical failure: `L1`, which is now proved and was
additionally falsification-tested against an independently produced Monte Carlo
map. Everything optional hangs off `C3` and `C4` and can be dropped without
touching `P5X-T9`.

This is why the frozen protocol puts the stop-gate on enclosure *width* and
nothing else.
