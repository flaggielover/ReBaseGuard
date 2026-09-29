# Re-check R3: route-audit erratum E1 against delta-review defects DR1-DR3
DELTA_ACCEPTED

Reviewer: reviewROUTE, the same independent reviewer, resumed. Date: 2026-09-30. Mode: read-only. No git write,
no driver mode, nothing for cells 305-309 or the band, no effect estimate on 308, cell 309 untouched.

**Reviewed object.** `registry/SUCCESSOR_ROUTE_AUDIT_308_ADDENDUM_A1_ERRATUM_E1.md` at research `a7c969e8` (86 lines).

**Base.** `reviews/REVIEW_SUCCESSOR_ROUTE_308_DELTA.md` at `fc723105`. I verified its sha256 as
`fe6ee79d…100aeb0`.

**Also read:**
* `governance/SUCCESSOR_GOVERNANCE_308_ADDENDUM_A1_ERRATUM_E1.md`, D1-D2;
* governance A1 §3 and S16;
* the grant's U6 and closing sentences;
* the ledger lines after 18:30Z.

## 1. Replaced passages are verbatim (PASS)

The original audit, A1, the architecture and governance A1 are byte-unchanged between `ce145e51` and `a7c969e8`
(empty git diff).

After stripping quote markers and whitespace, each passage E1 quotes as "Replaced" occurs exactly once in A1:
* DR1: the foreclosure sub-bullet and the "user should see this trade" sub-bullet;
* DR2: A1 §5 item 7, the second bullet;
* DR3: MB-VAR's first column;
* N1: "only P0 is certified";
* N5: "It is re-derived only by the frozen §3.2 rule from decoy runtimes".

E1's §26 quotation occurs verbatim in `ledger/USER_TEXTS_SUCCESSOR_308.md`.

## 2. Repairs (PASS)

* **DR1: repaired.**
  * "Forbid" and "forecloses" are gone. §26 is now quoted verbatim as a **path** (temporal evidence plus
    independent governance review), with the post-result liability.
  * The grant/U6 and cell-306 citations are stated correctly. The grant carries U6 verbatim ("from its result") and
    its own "no successor selected from the result".
  * The false cross-reference is withdrawn. E1 says the trade is **not** in governance A1 §3's six items, and
    governance E1 D1 now puts the trade in the brief the user sees for S1.
* **DR2: repaired, as specified.**
  * The sentence is conditional on the full RC2 pin holding at every resume, and on verified checkpoints.
  * The pin is re-verified at `execute`, at every `resume` and in any mode that computes.
  * A mismatch goes to `close-indeterminate`, with no mixed-platform resume.
  * The no-update rule covers the whole post-marker window up to the 7-day deadline.
  * Disabling automatic updates is the user's operator action. The campaign changes no system setting.
  * Preflight records the setting read-only and refuses when automatic installation is enabled.
* **DR3: repaired.**
  * The verification budgets (protocol D14: the `vd_pl` and `vd_verify` budgets, with the C1b d ≥ 8 example) are
    added to MB-VAR.
  * The A0 slot rule of THEOREM_RLR307's D14 member is labelled unambiguously.
  * The status and reason are unchanged, and the general reason covers the budget variant.
* **N1 and N5: applied with the wording given.**
  * S16(c) exists in governance A1.
  * N5 now agrees with governance A1 §3 item 4 and GC-9.

## 3. Nothing else changed; no new wrong claim (PASS)

E1 touches only the named passages. Its new statements are all accurate:
* "Both members were recorded in registry r2 (`8da57f89`) before the MB r1 freeze" is true (verified earlier).
* The grant/U6 wording is accurate.
* The architecture §4 terminal rule it relies on exists.

The route is unchanged: MB-S.

## 4. Residual notes (not grounds for rejection)

* **R3-N1. A time claim in A1 §3 is impossible (A1 text, not E1).** A1 §3 says the builder was instructed on
  RC1/RC2 "on 2026-09-29 at about 20:40Z".
  * A1 was committed at 18:50:39Z, and my route review was logged at 18:33:27Z. The claim cannot be true, and my
    delta review missed it.
  * Governance E1 D2 declares such coordinator annotations unreliable and makes the ledger's UTC authoritative.
    But no ledger line records the RC1/RC2 builder instruction.
  * Record one, or correct the time, when A1 is next touched.
* **R3-N2. The S1 trade should say what its first option means.** "Adopt the members before the MB-S freeze" means
  leaving MB-S for a route on S4's changed branch. That needs new code, reviews and qualification, and forgoes the
  determinism argument.
* **R3-N3. Architecture §4 needs the pin-mismatch rule.** Its frozen terminal rules must be amended to include
  E1's pin-mismatch rule. The build is "at risk" under S16 until it is.
* **R3-N4. Unapplied delta notes N2-N4 remain advisory.** In particular, N3 (the AST equality test should also cover
  the module-level names that the driver's science functions reference) is for the successor qualification reviewer.

## 5. Status of the route audit

The route audit, as amended by A1 and E1, is **ROUTE_ACCEPTED**: successor route MB-S, with the MB r1 science
byte-identical.
* **Discharged in text:** RC3, RC4 and RC5.
* **Carried as binding successor requirements:**
  * RC1 (the boundary, driver-function text identity, and a guard that differs only in its constants);
  * RC2 (the platform pin, extended by E1 to every resume, the whole post-marker no-update window, and the MBR1_REPRO
    exact reproduction);
  * RC6 (the risk register and governed checkpoints with mandatory resume).
* RC1, RC2 and RC6 are satisfied as facts only at the successor's qualification and freeze (governance S16(b)),
  which reviewers then check.

Nothing here authorises a target evaluation. New target evaluations: 0. Band drifts: 0. Proxies: 0.
