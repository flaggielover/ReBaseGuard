# C10 — C2 provenance repair and prospective adoption governance audit

**Zero-science campaign.** No certification, no kernel, no operator tuple, no host, no toolchain.
Guard **DENY** throughout. No r6. r5 remains authoritative.

Two questions only.

## Q1 — Why does REGISTRY_C2 bind a hash that differs from the committed producer?

**It is not broken. C9 misread a build-time record as a live integrity constraint.**

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
The dependency that *is* enforced at run time is `TABOO_SHA256`, which refuses if the certifier has
moved — and that pin still matches exactly.

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
- **The adjudication directs its own replacement**: on closing N9, *"a successor should freeze a
  replacement floor requiring agreement between two independent certifier implementations rather
  than F1."*
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

**Cell 306.** C8's frozen rule 1 bound *C9's* selection, not every future campaign. A future
campaign that freezes its own gate before its own result may prospectively target 306. **C10 does not
authorize that** and does not retroactively alter C8 or C9.

## Discipline

Three scans were repaired rather than trusted. The N9 detector twice read a *conditional* — "lapses
**when** N9 is closed", whose own sentence says "remains open" — as an assertion that N9 had closed;
the fix captures preceding context and reports **AMBIGUOUS** rather than voting. Mutant M05 was a
tautology (`if ["build"]` is always truthy) and now re-runs the real classifier across every branch.

Mutations **14/14**, fact verification **15/15**. The ledger tags each claim `GIT_HISTORY`,
`NUMERICAL` or `GOVERNANCE`, because a governance *reading* is an argument and not a reproducible
fact, and should be weighed differently.
