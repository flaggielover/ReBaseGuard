# C10 — C2 provenance repair and prospective adoption governance audit

**Zero-science campaign.** No certification, no kernel, no operator tuple, no host, no toolchain.
Guard **DENY** throughout. No r6. r5 remains authoritative.

Two questions only.

## Q1 — Why does REGISTRY_C2 bind a hash that differs from the committed producer?

**It is not broken.**

*Prior art, cited.* C9's own stop-review had already established the bound commit, both divergence
commits and the verify/main localisation (`REVIEW_C9_STOP.md`). C10's first pass reproduced that
work without citing it, and also **mis-attributed a claim to C9**: C9 did not say the pin was a live
integrity constraint. `C9_TOOLCHAIN.json` states a true mismatch plus a reproducibility requirement
— *"any execution must resolve which producer actually built the registry"* — which this archaeology
**satisfies**. Both corrections stand against C10, not against C9.

C10's contribution is the *measurement*: the AST unit comparison with its coverage residue, the
located enforcement site, and the consumer scan.

| commit | date | producer content SHA-256 | |
|---|---|---|---|
| `e71378a09e34` | 2026-09-20 | `4ac24d9e1826…` | **← the pin** |
| `e9c230d3eb76` | 2026-09-21 | `629715c0afdf…` | *"the registry verifier could never pass; fixed"* |
| `2b045564d137` | 2026-09-21 | `0d1d8021a378…` | *"record two claims as verified rather than asserted"* |

The registry was built once, at `5a94568a`, and **never rebuilt**. Its recorded hash matches the
producer exactly as it stood then. The file was edited twice *afterwards*.

An **AST unit-level** comparison — not a line diff — of the bound version against HEAD finds exactly
two changed units, `main` and `verify`. Every build-path unit is byte-identical, and so is every
scientific constant (`SUB_BLOCK_MAX_WIDTH`, `DEGREE_TABOO`, `DEGREE_ARL`, `TABOO_ALPHAS`,
`ARL_ALPHAS`).

What settles it is what the field *means*: it is emitted inside the build as
`sha(HERE.read_bytes())`, so it **records what built the registry**. No consumer compares it to HEAD.
The dependency that *is* enforced at run time is `TABOO_SHA256` — located at
`c2_refined_registry.py:63`, where a mismatch raises — and that pin still matches exactly. A scan of
all 1461 committed Python files finds **no consumer** that compares the producer self-hash to HEAD:
five files mention the field, and all five are auditors (including C10's own two modules) or the
producer that writes it.

*Carried from C9's review and not dropped:* because `sha(HERE.read_bytes())` is written into every
new registry, **a rebuild today could not reproduce `REGISTRY_C2.json` byte-for-byte regardless** —
independently of this hash question.

**Class: `C_GOVERNANCE_DRIFT`.** Not `E` (the binding resolves), not `D` (no scientific logic
changed), not `B` (the edits are functional, not cosmetic). The drift is in governance instruments —
the verifier and a CLI evidence writer — while the historical scientific evidence stays bound to its
historical producer.

## Q2 — Is the C2 adoption floor binding on every future successor forever?

**No — and the answer is in the adjudication's own text, not in inference.**

- It was set by an **adjudication**, not a theorem and not a project-global invariant.
- It **declares itself prospective**: *"It is prospective: it governs future adoptions of K5 m = 5
  tail cells from this verdict onward. It does not reopen, impeach or revisit any cell already
  adopted…"*
- **F1 carries an explicit lapse condition**: *"available for as long as N9 … remains open, and
  lapses when N9 is closed."*
- **The verdict's Condition 1 states the replacement procedure directly** — this is the primary
  authority: *"**The floor above is now the standard** for K5 m = 5 tail adoptions, prospectively. A
  successor that wishes to replace it must freeze the replacement **before** recomputing any
  magnitude."*

  > **Binding precondition, and it has teeth.** A successor must freeze its replacement rule
  > **before** recomputing any magnitude. C8's own adjudicator used exactly this condition to fault
  > C8. C10's first pass never cited Condition 1 at all and omitted this precondition — a successor
  > following that draft could have computed first and frozen after, violating the verdict.

- *Corroborating only:* the "replacement floor … two independent certifier implementations" sentence
  is one of **three** routes for discharging the floor **for cell 306**, conditioned on closing N9.
  C10's first pass called it decisive; that was an **over-read** and is withdrawn.
- **Nothing claims permanence.** "Permanent" appears only about adopted *cells* — a statement about
  verdicts, not rules.
- **Precedent**: the same document records that Campaign A adopted cells 11–44 on a valid enclosure
  plus a frozen K5-B pass, with *no* robustness requirement.

> A future successor **may** freeze a different prospective adoption rule without retroactively
> altering C2. What it may **not** do is re-adjudicate 305 or 306 under a new rule, or apply its own
> rule to an adoption already made. Historical verdicts are immutable; the prospective rule is not.

**Gating fact: N9 is still OPEN** (6 explicit assertions across C2–C8, 0 closed). So F1 remains live
and the replacement route the adjudication names is **not yet reachable**.

## Consequences

**Cell 307.** α can close it in projection (up to 1.137406× against 1.096007× needed) but can
**never adopt** it under the inherited floor: F2 needs 1.370009×, and **F1 is invariant under α** —
F1 asks for `Γ < 0` under a supply that does *not* use the Arb/FLINT registry, while α tightens that
registry's own taboo supersolution.

> The rational next purchase is **closing N9** — a second, independently written certifier — not an
> α run. It unblocks *both* 306 and 307 and answers the failure mode the floor exists for. The
> adjudication says plainly that more margin is *"the wrong instrument for the risk that is actually
> open."*

*Caveat on the 306 margin figures.* C10 imports C8's 1.171431 / 1.067071. C8's own adjudicator
flagged those as the most favourable of three unreconciled margin values. They are used here as
C8 published them and are not independently re-derived.

**Cell 306.** C8's frozen rule 1 bound *C9's* selection, not every future campaign. A future
campaign that freezes its own gate before its own result may prospectively target 306. **C10 does not
authorize that** and does not retroactively alter C8 or C9.

## Discipline

Three scans were repaired rather than trusted. The N9 detector twice read a *conditional* — "lapses
**when** N9 is closed", whose own sentence says "remains open" — as an assertion that N9 had closed;
the fix captures preceding context and reports **AMBIGUOUS** rather than voting. Mutant M05 was a
tautology (`if ["build"]` is always truthy) and now re-runs the real classifier across every branch.

**Applied decision gate: `P2 + P5`** — provenance clean and a successor rule permitted, but the
replacement route is gated on N9, which is open. A governance bridge (a second independent certifier)
is required before any successor adoption of 306 or 307. The gate was frozen before adjudication and
is now actually *applied*; C10's first pass froze it and never used it.

**Adjudicated `ACCEPTED_WITH_CONDITIONS`.** The adjudicator found that commit `7f255f3d`'s claim
"both CRITICALs repaired" was not accurate as committed, and it was right on every count checked
here. A fix recorded but provably absent is worse than an open finding, and three were:

- the AST residue flag was **computed and never read** — the classifier ignored it, so an import-line
  or thread-pinning change still yielded `A_NO_DEFECT` while the flag sat `False` beside it. The
  classifier now consumes it; both planted residue-only mutations classify correctly.
- **one of four producers could not complete**: a rename left `c10_governance.py` raising `KeyError`
  after writing its evidence, so the artifact existed while the producer exited non-zero. Fixed and
  re-run end to end.
- the permanence scan read **one file for four words** while the gate and ledger described it as
  repo-wide — and it feeds the applied `SUCCESSOR_RULE_ALLOWED` predicate. Now 4803 committed files,
  co-occurrence with this floor required, **0 hits**, with C10's own namespace excluded because
  otherwise the scan matched itself.

Also corrected: `Q1_ANSWER` still carried the false attribution to C9 verbatim; `Q2_ANSWER` still
rested on the withdrawn cell-306 sentence while the same object withdrew it; M14 compared a dict
literal to itself and now exercises the ledger contract, including that injecting a
`NOT_REPRODUCED` entry flips the class to `REFUSE`; and the gate-ordering entry tested the
*absence* of an adjudication artifact, so it flipped to `NOT_REPRODUCED` the moment the campaign
progressed — it now tests ordering.

One committed artifact that **supports** this conclusion was never surfaced and is now cited:
`REVIEW_C9_STOP.md` independently recorded that the C2 gate is "over-read as programme-wide
immutability".

Mutations **14/14**, fact verification **15/15**. The ledger tags each claim `GIT_HISTORY`,
`NUMERICAL` or `GOVERNANCE`, because a governance *reading* is an argument and not a reproducible
fact, and should be weighed differently.
