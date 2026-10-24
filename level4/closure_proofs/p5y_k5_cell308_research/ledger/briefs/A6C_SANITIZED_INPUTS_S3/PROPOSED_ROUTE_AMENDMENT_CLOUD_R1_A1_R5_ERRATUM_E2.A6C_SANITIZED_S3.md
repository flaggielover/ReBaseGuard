# Erratum E2 to the proposed route amendment r5 (Cell-308 Cloud route r1) — bounded corrections after FR2 and S12

**Status: PROPOSED · NOT ACCEPTED · NOT IN FORCE.** This erratum corrects `PROPOSED_ROUTE_AMENDMENT_CLOUD_R1_A1_R5.md`
(`d0963b11…ba933`) together with erratum E1 (`b4728654…af41b`). Both are preserved unchanged.

Its sources:
* bounded check FR2 (`reviews/REVIEW_FORMAL_ROUTE_CLOUD_R1_FR2.md`, `1ad769bb…8cac`): K1, K7, K8, K9, K11, K15;
* S12 review (`reviews/REVIEW_S12_RISK_CLOUD_R1.md`, `9d549eb2…b55c`; S12_RATING HIGH, conditional): S1, S2, S4,
  S6, S10, S12, S13, S16, S18.

**Precedence.** Where amendment r5, erratum E1 and this erratum differ, this erratum governs, then E1, then r5. Nothing
is accepted or decided. `new_target_evaluations = 0` · `cell309_activity = none`.

## E2.1 — gate rows replaced (FR2 K1, K8)

* **§3 L-PIN row.** Replaced by L-DET packet erratum E1 §4, with erratum E2 to that packet. The pins:
  * interpreter path;
  * `sys.version`;
  * architecture (`machine`);
  * the build-provenance record;
  * the prefix manifest;
  * libpython (explicit);
  * the mapped system shared objects by path and sha256, with dpkg versions where dpkg owns them;
  * kernel and os-release.

  The rule "an unknown owner package never matches" applies only to objects that dpkg is expected to own (system
  libraries). It never applies to the interpreter prefix, which the manifest pins instead. D-INTERPRETER and L-PIN
  then agree.
* **§3 L-LIFE row and the D-HOST-LIFETIME row's carried items.** Replaced by `HOST_ATTESTATION_ACCEPTANCE_PROCEDURE_R3_20261016.md`
  §1–§5:
  * `C` fixes the accepted bytes;
  * the blobs at HEAD must equal those at `C`;
  * the veto is the L-LIFE veto over HEAD's whole history, plus ledger REJECTED lines, plus the owner's record;
  * per-part acceptance P1 / P2.

  `host_lifetime_attested` stays OPEN_DECISION while D-HOST-LIFETIME is not in `DECIDED`.
* **E1.2 sufficient condition 2** reads: "the L-DET pins of E2.1 (interpreter path, `sys.version`, architecture,
  build-provenance record, prefix manifest, libpython, mapped shared objects, kernel, os-release) are recorded and
  matched exactly at every later computing step".

## E2.2 — HOST row timing and record count (FR2 K7)

E1.2 is corrected in three ways.
* The HOST row reads **EXCLUDED until route-audit addendum A2 exists**, and CONDITIONAL only from A2.
* Sufficient condition 1 reads "on **all four cases (five records, listed by blob id in the reference addendum)**".
* The check that A2 needs is "a bounded conformance check of the corrected texts by a reviewer the owner launches
  outside the coordinator's environment" (procedure r3 §7 item 1).

## E2.3 — rating floor restated (S12 S6, S10; FR2 K9)

E1.6's replacement text is replaced by:

> for every decision that needs a rating, at a rating **not lower than HIGH**, with the decisive argument **lost** and
> the successor's value a **second, different draw**. The floor rests on accepted text that does not depend on any
> trigger:
> * route A1 §1 ("The value of MB-S equals the value the lost MB r1 run would have produced only on the same platform …
>   Off that platform the S4 'changed' branch applies");
> * route E2's escalation to HIGH;
> * the reader-checked brief R2 lines 208–209 ("conditional on byte-identical science on the pinned platform … otherwise
>   HIGH").
>
> [A6C-SANITIZED S3: original line 62 redacted, class K: quoted text naming an excluded source, source not established, redacted conservatively]
> [A6C-SANITIZED S3: original line 63 redacted, class K: quoted text naming an excluded source, source not established, redacted conservatively]
> [A6C-SANITIZED S3: original line 64 redacted, class K: quoted text naming an excluded source, source not established, redacted conservatively]

**MBS-5(b) (S10).** It binds evaluations "after the MB-S marker", and no MB-S marker exists. Its effect is on any
route after **this** route's marker. This route's current floor rests on the texts above.

## E2.4 — finality across platforms and outcomes (S12 S1; BLOCKING)

New rule (§1), proposed for the accepted amendment, the MBS-6 record and the S1 ruling:

> **Finality.** After this route's marker, any outcome ends route MB on cell 308 **on every platform and host**. That
> includes CLOSED, NOT_CLOSED, and every INDETERMINATE or INCIDENT class. The loss of the decisive argument ("a
> different draw") is never a ground for a further route. Any later route on cell 308 starts at a rating not lower than
> HIGH (MBS-5(b)), and discloses this route's marker, outcome and every host attempt.

This presupposes MBS-6 option (i), recorded before OD-1 (E2.5). It is owner-reserved.

## E2.5 — decisions before OD-1 and OD-3 (S12 S2, S11; BLOCKING S2)

The owner records **MBS-6 (i), MBS-7 (i) and the MBS-8 option before OD-1**. That is before any reading of a named
machine, and so also before OD-3 and the L-DET interpreter build. Each record states that no new-host runtime, no
inventory reading and no Q12 result existed when it was made.

The D-CAPS-CPU input "Q12's result under option (i) on that host" is **deleted**. Under MBS-8 (ii), the caps are
derived later from official decoy runtimes by the accepted §3.2 rule, with no further choice.

All 21 D-* items are decided before the Phase-1 inventory of the named machine. A later change needs a fresh S12
rating and a formal review with the readings in view.

## E2.6 — cross-host marker (S12 S4)

When this route's marker is written:
* its ref name and id (value-free) are recorded in the owner's record and mirrored in the canonical ledger;
* every later cell-308 preflight on any host asserts both markers, MB r1 `afa93072` and this route's marker, as named
  exceptions. This is the D-S15-NEWHOST analogue.

## E2.7 — host attempts, window bound, V-A runner, E8 (S12 S12, S13, S16, S18; FR2 K11, K15)

* **Host attempts (S12).**
  * Every machine inventoried for this route is recorded and disclosed in every later brief.
  * A designated-series, gate or qualification failure on the named host stops the route. Restarting needs a new owner
    ruling, with a fresh S12 rating and a formal review.
  * "No host shopping" covers candidates dropped before L-DET, too.
* **Window bound (S13).** Before the Phase-1 inventory of the named machine the owner fixes a maximum interval from the L-DET interpreter build to the marker.
  Its lapse, or any forced update or image change inside the window, stops the route on that platform. The number is
  a new constant and goes into the new-constant trace.
* **Order (K11).** The L-DET interpreter build follows acceptance part P1 (procedure r3 §4) and is an anchored step
  (r3 §5).
* **L-DET commit (K15).** The OD-3 record names the L-DET commit and lists, by path, every file that may differ
  between it and the freeze (none on the evaluation path). The owner commits that record before the attempt.
* **V-A runner (S16).** E1.7 also covers the runner. No V-A runner process is installed, or it is stopped and disabled,
  from the L-DET build to the seal, shown by a measured process list. Its updates count as an H3 vector. V-B is
  preferred.
* **E8 extended (S18).** No new-host decoy or L-DET runtime is placed next to an MB r1 runtime, or next to any cell-308
  quantity or projection, in any decision document (OD-1, MBS-8, the OD-3 record, the S1 brief).

## E2.8 — not changed

Everything else in amendment r5 and erratum E1 stands as proposed.
[A6C-SANITIZED S3 artifact of level4/closure_proofs/p5y_k5_cell308_research/governance/new_host_route_cloud_r1/PROPOSED_ROUTE_AMENDMENT_CLOUD_R1_A1_R5_ERRATUM_E2.md at 4f814796757bb1a14086b88d677adef94309d0f6 (7388 bytes, sha256 a9d616fb84fffefe42ede75c6e90735da23b3c6309463f81d8954ff9f4b26353). 3 lines redacted line-for-line (K=3); every other line is byte-identical to the original; line numbers are preserved.]
