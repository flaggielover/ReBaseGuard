# Erratum E1 to the proposed route amendment r5 (Cell-308 Cloud route r1) — bounded corrections after FR1

**Status: PROPOSED · NOT ACCEPTED · NOT IN FORCE.** This erratum corrects `PROPOSED_ROUTE_AMENDMENT_CLOUD_R1_A1_R5.md`
(sha256 `d0963b11…ba933`), which is preserved unchanged. Its source is the formal route review FR1
(`reviews/REVIEW_FORMAL_ROUTE_CLOUD_R1_FR1.md`, sha256 `af150ef4…b6df`; ROUTE_TEXTS: ACCEPTED_WITH_CONDITIONS). Each
item below replaces or adds the named text. Where amendment r5 and this erratum differ, this erratum governs the
proposal. Nothing here is accepted or decided, and `DECIDED` stays empty. `new_target_evaluations = 0` ·
`cell309_activity = none`.

## E1.1 — §1 "Unchanged [ACCEPTED]" (FR1 G3, G35)

Replace the second and the first bullets' affected words as follows.

* **Members (G3).** Strike "the members" from the Unchanged [ACCEPTED] list. Insert instead: "the members: **[OPEN] owner
  decision MBS-7** (conditions register; brief R2 §5). This route presupposes MBS-7 option (i), members unchanged.
  The owner records MBS-7 **before OD-3**, because option (ii) would change the science that L-DET tests, and a
  decision taken after an L-DET outcome would be a post-result choice."
* **R-rule numbers (G35).** Replace "every number of R-MEM, R-FREE, R-EXCL-PCT and R-ALLOW" with "the **numbers** of
  R-MEM, R-FREE, R-EXCL-PCT and R-ALLOW. Their measured quantities on Linux, their base sets and any added parameters
  are **[OPEN]** in §4 (D-MEM-FREE, D-MEM-WIRED, D-MEM-PRESSURE, D-EXCL-WINDOW, D-ALLOW-PATHS, D-ALLOW-BASE39)."

## E1.2 — §1 and §5: what discharges the HOST row, and the S4 instrument (FR1 G1)

Add after the HOST-row quotation in §1:

> **[PROPOSED] HOST row on this route.** Before acceptance the row reads EXCLUDED. After the owner adopts this route,
> it reads **CONDITIONAL** on the one named host. RC2 counts as discharged on that host only when **all** of these
> hold:
> 1. **L-DET MATCH:** comparison (a) **and** (b) on all four compared records (L-DET erratum E1), non-vacuous and
>    control-detected, at the named L-DET commit;
> 2. the **L-DET pins** (interpreter provenance and prefix manifest, libpython, mapped shared objects, kernel,
>    os-release) are recorded, and are **matched exactly** at every later computing step: the designated series,
>    qualification, `execute`, and every `resume` / `recover`;
> 3. the **platform window** H1 / H3 / H8 holds from the L-DET interpreter build to the 7-day deadline (E1.4);
> 4. the accepted **MBR1_REPRO** case matches at the official qualification on the frozen commit (E1.3).
>
> Any failure of 1–4 returns the row to EXCLUDED on that platform and stops the route there.
>
> Discharging RC2 in this sense establishes **reproduction of MB r1's non-target records only**. It does not restore
> the decisive argument (route A1 §1). The successor stays on S4's changed branch, and its value is a second,
> different draw (§6).

**The instrument (gov S4: "a route audit (Phase 3)").** The formal route review FR1 is **not** the S4 route audit. The
instrument is a route-audit addendum, `registry/SUCCESSOR_ROUTE_AUDIT_308_ADDENDUM_A2.md`, written only after:
* the owner's adoption of this route and its D-* decisions;
* a fresh bounded check of the corrected texts.

It records the HOST row status above and is countersigned by the owner's decision record. Until it exists the HOST row
reads EXCLUDED.

## E1.3 — §5: L-DET is a pre-gate; MBR1_REPRO still runs (FR1 G4)

Add as §5 item 10:

> **10. Relation to MBR1_REPRO.** L-DET is an **additional pre-gate**, run once before any designated series. The
> accepted MBR1_REPRO case (route A1 §3) still runs at the official qualification, on the frozen commit.
> * That run is **not a repeat** under D-LDET-REPEAT: it is the accepted qualification case, not a second L-DET attempt.
> * A mismatch there is STOP and the S4 changed branch, exactly as route A1 §3 says.
>
> L-DET is bound to a **named commit** of the reviewed successor build. The evaluation-path files (the S11 science
> modules, the certifier imports, the comparison and view functions) must be byte-identical at the L-DET commit and at
> the freeze. The accepted amendment lists, by path, any file that may differ between them (none on the science
> path). A difference on the evaluation path invalidates the L-DET outcome for the freeze.

## E1.4 — §2.2: the platform window starts at the L-DET build (FR1 G5)

In rows H1, H3 and H8, replace "from the designated series" (H1) and "from qualification" (H3) with "**from the
interpreter build for L-DET** to the 7-day deadline". H8's "every official step" includes the L-DET attempt and the
interpreter build. A platform change between L-DET and the deadline voids the L-DET outcome. A re-run would be a
forbidden repeat, so the route stops on that platform.

## E1.5 — §3 L-EXCL and §4 D-EXCL-WINDOW (FR1 G8)

L-EXCL in §3 already reports a process that exits in the window "with unknown usage", so no reading is made. That
stays. Any D-EXCL-WINDOW ruling that charges an exited process "its last observed ticks" is withdrawn.

The start-gate re-read is a **new rule**, labelled as such:
* at most **3** re-reads before the marker;
* each reading recorded in full;
* none after the marker.

## E1.6 — §6: rating floor (FR1 G2)

Replace "for every decision that needs a rating, as **HIGH** … unless D-RC2-SCOPE is decided otherwise by an
independent reviewer and the owner" with:

> for every decision that needs a rating, at a rating **not lower than HIGH**. A platform change is S4's changed
> branch, so trigger T1's condition ("the science is then 'changed' under S4") holds by construction, and route E2
> escalates a fired trigger to HIGH. No rating below HIGH is possible without a written S12 finding that T1 has not
> fired on this route.

## E1.7 — option V-A (FR1 G28)

Wherever V-A is offered (the owner brief r5 OD-1 table; packet §7 row 2), add:
* **no agent session runs on the official host** from the L-DET interpreter build to the seal;
* in particular none runs during the designated series, qualification, `execute`, or any `resume` / `recover`.

This follows from S17 (no other session's compute) and MBS-3 / route E2 L6 (no in-run observation). A V-A runner that
cannot be stopped for that window disqualifies V-A.

## E1.8 — sources (FR1 G13, G36)

* **G13.** Brief R2 is a decision brief. Its §9 start-gate rows (thermal, AC, Low Power Mode, Memory) describe the
  MB-S protocol draft (`216c465f`), as brief R2 says at its line 402. The amendment's "[ACCEPTED] brief R2 §9" labels
  for those rows read instead: "protocol draft (`216c465f`) as described in brief R2 §9". Where an accepted text
  exists, it is cited instead: ratification items 4, 24 and 25, governance A1 S17, route E1 DR2. MBS-5(b) stays
  [ACCEPTED] through route E2.
* **G36.** ROUTE_PREPARATION line 19 instructs "Do not change … measurement rules or thresholds to accommodate the
  cloud", and line 41 permits putting a change to the owner. Every D-* ruling that changes a measurement rule therefore
  needs the owner to set line 19 aside **expressly**, rule by rule. The consolidated D-* package lists those rules.

## E1.9 — not changed

Everything else in amendment r5 stands as proposed. No [ACCEPTED] quotation is altered: FR1 F1 found them verbatim,
[A6C-SANITIZED S2: original line 115 redacted, class I: possible incident-review attribution, redacted conservatively]
[A6C-SANITIZED S2 artifact of level4/closure_proofs/p5y_k5_cell308_research/governance/new_host_route_cloud_r1/PROPOSED_ROUTE_AMENDMENT_CLOUD_R1_A1_R5_ERRATUM_E1.md at 4f814796757bb1a14086b88d677adef94309d0f6 (7474 bytes, sha256 b47286544b7f5c7e45e95b37bd1bdb0c9a6889fae4325cbcf081fe00deaaf41b). 1 lines redacted line-for-line (I=1); every other line is byte-identical to the original; line numbers are preserved.]
