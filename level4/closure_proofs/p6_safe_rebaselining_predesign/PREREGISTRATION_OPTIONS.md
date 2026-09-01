# Preregistration options for P6 closure

P4 and P7 both demonstrated why frozen gates matter: P4's three failed gates are
*informative* precisely because they were written before the data existed and
were left unedited afterwards (`G2`), and P7's boundary verdict is credible
precisely because its threshold (`4 of 8` families) was pre-committed (`S11`).

This document proposes candidate gates. **No numerical threshold is finalised
here.** Where a number is needed, two or three defensible options are offered
with the argument for each, and the choice is an entry-gate decision.

---

## 1. Structural criteria (proposed as mandatory, no numbers needed)

These carry no free parameter, so they can be frozen now.

| # | criterion | rationale |
|---|---|---|
| C1 | **No metric is selected post hoc.** The primary objective, primary cell and materiality threshold are fixed before any `EVAL` data are produced | `F7` |
| C2 | **Every comparison carries an interval**, and uses P7's verdict labels verbatim | comparability with the closed campaign |
| C3 | **No latent-state information in any policy claimed implementable**, enforced structurally | `I2`, `F1` |
| C4 | **Reproduction across both frozen detectors**, with the effect resolved in each | `F6`; `S13` licenses the expectation, not the claim |
| C5 | **Reproduction on an independent seed family** (`REPLAY`), untouched during the campaign | `F7`, `F9` |
| C6 | **No change to frozen P1–P5/P7 semantics**; constant-policy correspondence is bit-identical in `tau` | `I1`, `I4`, `F13` |
| C7 | **Multi-cycle evaluation**: no claim rests on R1 or R4 alone; `Coll` is reported for every method | `S8`, `F14` |
| C8 | **Cost-matched comparison**: the headline comparison is against the best fixed `rho` at matched `Fresh`, never against `B3` alone | `F3`, `METHOD_NOVELTY_SEPARATION.md` §3 |
| C9 | **The novelty audit is executed before the confirmation stage** and its verdict recorded, whatever it is | `F12` |
| C10 | **Dropped candidates are reported** with reason and numbers | `COMPUTE_PLAN.md` §3 |

A method winning on one metric, in one cell, on one detector satisfies none of
these and closes nothing.

## 2. Criteria needing a number — options for approval

### G-A. Tail-risk improvement over full reuse

> The method improves the preregistered tail metric relative to `B3` (`rho = 1`)
> at the primary `(D, m, Delta)` cell, with the paired interval excluding zero.

| option | threshold | argument |
|---|---|---|
| **A1** | relative reduction `>= 25%` in `Dtail(100)` | matches the order of the closed damage (`S9`: `11.4%` at the worst cell), and is large enough that it cannot be a calibration artefact |
| **A2** | relative reduction `>= 10%`, `PRACTICALLY_MATERIAL` under P7's label | lower bar, consistent with P7's own materiality convention; risks certifying an effect too small to matter operationally |
| **A3** | `Dq95` reduction `>= 20%` | far cheaper to estimate (`STATISTICAL_DESIGN.md` §5); loses the "catastrophic" framing that `Dtail` carries |

*Recommendation:* **A1 as primary with A3 as the declared fallback** if the tail
event budget cannot be met. The fallback must be declared before the data are
seen, not chosen after.

### G-B. Do-no-harm on in-control performance

> The method does not materially reduce `Arl0` relative to an accepted control.

| option | control and threshold | argument |
|---|---|---|
| **B1** | `Arl0(U) >= 0.95 x Arl0(B2*)` where `B2*` is the best fixed `rho` at matched `Fresh` | the honest bar; a `5%` band is roughly twice the interval width anticipated at confirmation scale |
| **B2** | `Arl0(U) >= Arl0(B3)` (full reuse) | far too weak — `B3` is the known-worst case |
| **B3'** | `Arl0(U) >= Arl0(B0)` (fresh-only) | too strong: fresh-only is the sample-expensive extreme, and requiring it invites the cost degeneracy `F3` |

*Recommendation:* **B1.**

### G-C. Sample efficiency

> The method uses fewer fresh samples than fresh-only.

| option | threshold | argument |
|---|---|---|
| **C-i** | `Fresh(U) <= 0.5 x Fresh(B0)` | a substantive saving; "re-baselining is worth doing" needs a real number, not `epsilon` |
| **C-ii** | `Fresh(U) < Fresh(B0)`, interval excluding zero | minimal; admits methods that save almost nothing |
| **C-iii** | report the frontier and set no threshold | consistent with `OPTIMIZATION_FORMULATIONS.md` E; no gate to game |

*Recommendation:* **C-i as the gate, C-iii as the reported output.**

### G-D. Reproduction breadth

| option | requirement | argument |
|---|---|---|
| **D1** | resolved in `>= 6` of the 8 `(detector, m)` families | mirrors P7's pre-committed `4 of 8` structure at a higher bar, appropriate because P6 claims an improvement rather than detecting a signature |
| **D2** | resolved in all 8 | brittle: `m = 1` is unusable at any `rho` (`S14`) and may be unimprovable, which would block closure for a reason unrelated to the method |
| **D3** | resolved in `>= 3` of 8 | too weak to exclude `F6` |

*Recommendation:* **D1, with `m = 1` excluded from the count and reported
separately**, and the exclusion declared in advance with `S14` as its reason.

### G-E. Finite-cycle safety

| option | threshold | argument |
|---|---|---|
| **E1** | `Coll = E[tau_2]/E[tau_1] >= 0.5` | the closed collapse is to `~0.02` (`S8`); `0.5` is a large, unambiguous improvement |
| **E2** | `Coll(U) >= 2 x Coll(B2*)` | relative, avoids setting an absolute level that may be unreachable |
| **E3** | report `Coll`, gate on nothing | weakest; but honest if the pilot shows `Coll` is unreachable for every method |

*Recommendation:* decide after the **pilot** measures `Coll` for the baselines.
Setting E1's number before knowing whether any method can reach it risks either
a vacuous gate or an unreachable one. This is the one gate that should be
deferred to post-pilot, and that deferral is itself preregistered here.

## 3. The closure rule

Proposed form, for approval:

> **P6 CLOSED** requires C1–C10, plus G-A, G-B, G-C and G-D at the approved
> options, plus G-E's post-pilot criterion.
>
> **P6 PARTIAL** if the structural criteria hold and some but not all of G-A..E
> are met, with each failure reported in the P4 style: the gate unedited, the
> failure explained, and the correctly-specified alternative reported beside it
> where the gate itself is at fault.
>
> **P6 CLOSED (negative)** if C1–C10 hold, the oracle ceiling is measured, and
> the reproduced finding is that no implementable adaptive policy beats the
> matched-cost fixed `rho`. This is a legitimate closure, not a failure, and it
> is written into the rule so the campaign is not pressured toward a positive
> result (`METHOD_NOVELTY_SEPARATION.md` §4).

## 4. What must not become a gate

* Anything of the form `rho < rho_c`, or "operates below the boundary" (`X1`,
  `F15`).
* Any threshold on `Rms`, `E[e^2]` or another latent-layer surrogate as the
  *closure* criterion — surrogates may be optimised, never gated on (`F2`,
  `S18`).
* Recovering nominal `ARL_0` (`S20`, `E1`, `X12`).
* Any P5 numeric as a threshold (`X9`).
