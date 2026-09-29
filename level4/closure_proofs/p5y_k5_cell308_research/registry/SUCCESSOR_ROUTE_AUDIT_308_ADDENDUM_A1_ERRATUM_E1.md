# Cell-308 successor route audit, addendum A1: erratum E1 (coordinator; route delta review DR1 to DR3)

**Why.** The delta review `reviews/REVIEW_SUCCESSOR_ROUTE_308_DELTA.md` (research `fc723105`, sha256 `fe6ee79d…100aeb0`)
returned DELTA_REJECTED on DR1–DR3. ROUTE_ACCEPTED under RC1–RC6 stands.

**Status of the earlier files.** A1 (`ce145e51`) and the original audit (`bddd85f8`) stay byte-unchanged. E1 replaces
the passages named below and nothing else. The route is unchanged: MB-S.

## DR1: the foreclosure sentence (A1 §1, the C11R-I2 / COR-T bullet)

**Replaced:**

> **The foreclosure consequence.** Once MB-S has an observed outcome, adding either member would be a variant selected
> after a result, which the grant, U6, the brief's §26 and the floor r2 / cell-306 precedent forbid. Choosing MB-S
> therefore **forecloses** those members for cell 308 unless they are adopted **before** the MB-S freeze.
>
> The user should see this trade before the S1 ruling (successor-governance addendum A1 §3).

**Replacement:**

> **The consequence of deferring.** Deferring C11R-I2 and COR-T now *may* foreclose them for cell 308, or at least
> makes any later use post-result, exposed and governed. The texts, verbatim:
>
> * The grant and U6 speak of variants selected "from its result", meaning MB r1's result.
> * The cell-306 precedent concerns re-running the same route after an observed outcome.
> * The brief's §26 (`ledger/USER_TEXTS_SUCCESSOR_308.md` §1c) says: "If such a route genuinely existed
>   prospectively before the target was seen, document temporal evidence and obtain independent governance review
>   before considering it."
>
> Both members were recorded in registry r2 (`8da57f89`) before the MB r1 freeze. So §26 sets a **path** for them,
> not a prohibition: temporal evidence plus independent governance review, carrying the post-result liability if
> MB-S has by then an observed outcome.
>
> The trade is **not** among the six items of the S1 content (successor-governance addendum A1 §3). The coordinator
> **will state it explicitly in the brief put to the user for the S1 ruling**: adopt the members before the MB-S
> freeze, or accept that any later use is post-result and governed as §26 says.

## DR2: determinism of a resumed evaluation (A1 §3 platform pinning and §5 item 7)

**Replaced (A1 §5 item 7, second bullet):**

> Because of determinism, a resumed evaluation equals an uninterrupted one.

**Replacement:**

> A resumed evaluation equals an uninterrupted one **only if the full RC2 platform pin holds at every resume, and
> every checkpoint used is verified**.

**Added to A1 §3 (platform pinning), binding on the successor:**

* **The pin is re-checked everywhere that computes.** The full RC2 pin (interpreter path and sha256, libpython
  sha256, `sys.version`, OS build, architecture) is re-verified at `execute` **and at every `resume`**, and in any
  mode that computes.
* **A mismatch at resume** goes to the frozen terminal rule: `close-indeterminate`, CONSUMED_UNRECORDED class. There
  is never a mixed-platform resume.
* **The no-update rule covers the whole post-marker window**, up to the 7-day resume deadline.
  * The host's automatic OS and software updates must be disabled for that window. This is an operator action by
    the user; the campaign never changes system settings.
  * The successor preflight **records**, read-only, the automatic-update settings, and **refuses** to start when
    automatic installation is enabled.

## DR3: the MB-VAR row (A1 §2)

**Replaced (the first-column text of MB-VAR):**

> R-MB parameter variants: partition (D1), RLR ladder (D3), pointwise ladder (D4), admission rule (D5), D14 slot rule,
> extra pointwise drifts

**Replacement:**

> R-MB parameter variants: partition (D1), RLR ladder (D3), pointwise ladder (D4), admission rule (D5), **verification
> budgets (protocol D14: `vd_pl` and `vd_verify` budgets; e.g. a budget that would admit C1b upper rungs with
> d ≥ 8)**, the A0 slot rule of THEOREM_RLR307's D14 member (labelled so, to avoid confusion with protocol D14),
> extra pointwise drifts

The status (NOT SELECTED) and the target-free reason are unchanged.

## Notes applied (delta review N1, N5)

* **N1 (A1 §1, P1 bullet).** "only P0 is certified" reads "**only P0's pruning is certified in full**". PRUNING_308
  P-D-b and P-D-c are certified results bearing on P1's family.
* **N5 (A1 §3, the D11 bullet).** "It is re-derived only by the frozen §3.2 rule from decoy runtimes" reads:
  "**whether the caps are kept or re-derived by the frozen §3.2 rule from decoy runtimes is a user decision under
  §14 / G2** (successor-governance addendum A1 §3 item 4, S16(c)). Either way, only decoy evidence is used".

Everything else in A1 stands as the delta review accepted it.
