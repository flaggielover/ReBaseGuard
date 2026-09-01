# P6R novelty scope

```text
Algorithmic novelty  = NOT ESTABLISHED
Theoretical novelty  = NOT ESTABLISHED
Formulation novelty  = PLAUSIBLE
Integration novelty  = PLAUSIBLE
```

This is the conservative wording returned by the independent adjudication. P6R
adopts it verbatim and **does not upgrade any line**. An upgrade would require a
genuinely stronger independent literature audit than either campaign has run,
and P6R runs none.

---

## What may be stated

* No direct prior formulation has yet been identified for the exact setting P6
  studies: **repeated post-alarm reuse of a stopping-time-selected terminal
  window, combined with fresh-sample acquisition, feeding a recursive
  reference-state update.** That is a statement about what a search did not
  find, and the search behind it was one sitting of web literature search with
  several sources read from abstracts. It is **weak evidence of absence**.

## What may not be stated

* That the **inverse-variance rule** is novel. `rho* = (1/k)/(V + 1/k)` is
  textbook inverse-variance weighting (sensor fusion, meta-analysis).
* That the **Jensen argument** is novel. Concavity of `Q(V) = nu V/(V+nu)` and
  the resulting gap are elementary.
* That the **Doeblin technique** is novel. The two-step whole-space minorisation
  is the standard construction (Meyn & Tweedie, 2nd ed., Thm 16.0.2), and P5's
  T7 used it first in this repository.
* That the **weight-adaptation shape** is novel. Making a weight a decreasing
  function of an observed magnitude is the adaptive-EWMA shape
  (Capizzi & Masarotto, *Technometrics* 45(3), 2003).
* That **gating reuse on a statistic** is novel. That is cautious parameter
  learning (Capizzi & Masarotto, *JQT* 52(4), 2020).

## Standing

`NOVELTY = NOT_INDEPENDENTLY_ADJUDICATED` for the formulation and integration
lines; `NOT ESTABLISHED` for the algorithmic and theoretical lines. The original
campaign's `NOVELTY_AUDIT.md` remains the only audit, with its own recorded
limits, and it is preserved unedited in the historical namespace.
