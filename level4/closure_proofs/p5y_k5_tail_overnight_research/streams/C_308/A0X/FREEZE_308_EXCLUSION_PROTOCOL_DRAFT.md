# FREEZE_308_EXCLUSION_PROTOCOL_DRAFT — settle X308 by one certified computation

**DRAFT ONLY — NOT FROZEN — NOT AUTHORIZED FOR EXECUTION**

This file is a design sketch written by overnight stream C2a under the target quarantine. It has no freeze commit, no
qualification, no grant and no code. Executing any part of it at the cell-308 drift is forbidden tonight (Q1, Q2;
`config/QUARANTINE_AMENDMENT_1.json`). A later run would need a separately frozen protocol and an explicit user
authorization. Nothing below was computed. Numbers quoted are committed values (file:line in `EXCLUSION_308.md` §0).

**S8 correction notice (2026-09-28).** The first version of §9 did three things that are now removed and marked
"[S8-corrected]":
* it placed the committed MC value next to Theorem M as a location estimate for Lambda_308, which estimated the
  outcome;
* it quoted committed tail-cell supply constants and a C8 reduction factor that no future result is compared against;
* §4 quoted the MC number inside a prohibition.

The leakage analysis now only STATES which committed numbers a future certified result would be compared against.
It does not estimate where U or L would fall.

## 0. What it would settle

It would settle the proposition `X308: Lambda_308 >= A0*` of `EXCLUSION_308.md` §a.2.
* `Lambda_308 = sup_{e in [1882413/1000000, 19839101/10000000]} E_a[tau](e)`.
* A0* is the C5-T critical A0 of cell 308 at A1 = A2 = 0. Its committed float rendering is 4.442851487961334
  (`C8_DECISION.json:124`); this is not a certified enclosure.

Pre-registered outcome classes (exactly one is sealed):

| class | meaning |
|---|---|
| `X308_CERTIFIED` | certified L with L >= A0*_hi: the uniform-A0 atom-constant family is excluded at 308 (exclusion only) |
| `NOT_X308_CERTIFIED` | certified U with U < A0*_lo: the A0 floor does not exclude the family; no closure claim |
| `UNDECIDED` | neither holds; terminal for this protocol |
| `CERTIFICATE_FAILED` | a certificate or cross-check failed after the marker; terminal, sealed |
| `REFUSED` | a precondition failed before the marker; nothing consumed |

Both decisive directions are registered **before** anything is evaluated, and the protocol prefers neither.

## 0a. Mandatory incident disclosure (binding on any future X308 protocol)

Any future X308 freeze, qualification review, execution review and adjudication must disclose the following
exposures. The disclosure must cite the files and must not restate any tail number.

| # | incident | file | what it means for a future X308 run |
|---|---|---|---|
| D-02 | **Incident 02**: the first version of stream C2a created a zero-compute, target-cell derived quantity. It was a cross-cell re-attribution of a committed certified value by endpoint sharing, placed next to 308's A0*. It was withdrawn under S8 (committed 7e851139, corrected 0d32a2e8), and a `PROXY_EXPOSURE` ledger line was written | `ledger/INCIDENT_02_C2A_CROSS_CELL_FLOOR.md` | the designers of this draft were exposed to an exclusion-direction quantity for cell 308 |
| D-03 | **Incident 03**: the coordinator's C2b brief contained a comparison scale derived from committed cell-308 figures, and C2b answered it. The exposure is qualitative, and a `PROXY_EXPOSURE` ledger line was written | `ledger/INCIDENT_03_C2B_BRIEF_SCALE.md` | the generator's tightness was, once, discussed against a 308-derived scale; that sentence is not used |
| D-F12 | Same class as incident 02, residual. C2a's files re-attributed C7's committed family ceiling to 308's right endpoint, which amendment 2 R2.4 forbids. It was found by `reviews/REVIEW_GLOBAL_INTEGRITY_R1.md` F12 and has been re-worded | `reviews/REVIEW_GLOBAL_INTEGRITY_R1.md` F12 | no number was computed; the information content for the sign of X308 is nil (review M §3.2) |
| D-S8 | The first version of C2a estimated the X308 outcome from committed values plus Theorem M. This was withdrawn under S8 | `EXCLUSION_308.md` S8 correction notice | the designers knew the committed cell-308 values (see also §4 disclosure) |

Consequences for a future freeze:
* **Parameter selection.** Every parameter must be selected by the cell-independent rule of §4, which exists so that
  these exposures cannot steer it.
* **Result-chasing class.** The classification of §9 applies with these disclosures attached. The qualification review
  must confirm that no frozen parameter or rule depends on any exposed quantity.
* **Proxies.** No exposed quantity may enter the decision table (§7) or the comparator (§6).

## 1. Preconditions for freezing (P1 met; P2-P5 open)

| id | precondition | status |
|---|---|---|
| P1 | Theorem M (`EXCLUSION_308.md` §c.6) is reviewed and ACCEPTED by a fresh-context reviewer. It is also validated at the declared non-target drifts {0, 1/4, 1/2, 1, 3}, with a numerical negative control at an off-diagonal start (p0, 0), p0 > 0 (the §c.8 argument itself is a derivation, not a control; C-12) | **MET.** Theorem M is VALIDATED_NON_TARGET after `reviews/REVIEW_THEOREM_M_R1.md` (ACCEPTED_WITH_CORRECTIONS; C1/C2/N3 applied; review note N6; numerical controls in review §2.3) |
| P2 | C2b's generator and exact certifier (`streams/C_308/A0X/gen/`) are VALIDATED_NON_TARGET at the declared drifts. Planted-invalid W's must be detected (S2) and coverage recorded | in progress in C2b (a skeleton when this was written) |
| P3 | The C5-T consumer for cell 308 is identified by blob and executable from pinned bytes without importing any forbidden historical module (Q3). Alternatively, an independent re-implementation is qualified against C8's committed inversion values at the non-target cells | open |
| P4 | The user decides to authorize one target computation at an in-band drift, outside the overnight quarantine | not given. No agent may request it on its own initiative |
| P5 | The governance classification (§9) is recorded in the freeze and accepted by the user | draft only |

**Variant choice** is fixed at freeze and never changed after evaluation.
* **Variant P** (single drift e_lo, below) is used if P1 holds.
* Otherwise **Variant B** is used: block-uniform over the whole cell, via C2b's lemma "block-uniform check = pointwise
  check on a widened y-range" (`gen/PROGRESS.md` step 2). B does not depend on Theorem M but carries more slack.
* Ranking by theoretical slack (S1): P has strictly less avoidable slack. By Theorem M the block supremum is attained
  at e_lo, while B pays for the worst case over the block.

## 2. Pre-registered drift(s)

* **Variant P:** exactly `e_lo = 1882413/1000000`.
  * It is read as the exact rational `left` of the CUSUM entry with index 308 of
    `p5y_k1_cover_ledger_successor/config/cells.json` (sha256 `341eb5e9…`).
  * **Filter `detector == "CUSUM"` first.** The index collides with SR (`THEOREM_TCT.md:134-138`).
  * The driver refuses any other drift, including interior points and e_hi. Upper bounds transport only to larger e
    (`EXCLUSION_308.md` §b.2).
* **Variant B:** the closed block `[left, right]` of the same entry, both endpoints exact.
* Exactly one drift (or one block): no mesh of drifts, no second point, no "nearby" drift.

## 3. Certificate type

Both sides use the same pre-registered mesh and the same untrusted proposal family.

**Upper side (refutation).**
* W is a P1 function on C2b's uniform anti-diagonal triangulation of X, with mesh h = 1/N.
* It is certified to satisfy `W >= 1 + K_e W` on **all of X**: at e = e_lo in Variant P, for every e in the block in
  Variant B.
* Certification = exact vertex margins plus a rigorous P1 interpolation-error bound (C2b §5).
* Then `E_x[tau](e) <= W(x)` for all x, by Lemma T's induction with K_e >= 0 (`THEOREM_AD.md:34-41`).
* `U := W(a)` bounds Lambda(e_lo) (Variant P) or Lambda over the block (Variant B). Under Variant P, Theorem M makes U
  a bound on Lambda_308.

**Lower side (proof).**
* w is a P1 function on the same mesh, certified to satisfy `w <= 1 + K_{e_lo} w` on X.
* Then `w <= u := E_.[tau](e_lo)`. Proof: with d = w - u, d <= K d, so d^+ <= K d^+ <= K^n d^+.
* K^n -> 0 in norm because the upper certificate gives K W <= W - 1 <= theta W, with theta = 1 - 1/sup W
  (`THEOREM_AD.md:40-41`).
* Hence `L := w(a) <= Lambda(e_lo) <= Lambda_308`. The second inequality needs no theorem: e_lo is in the cell.
* The lower side is valid only if the upper certificate passed. If the upper side fails, L := -infinity.

(If C2b does not implement subsolutions, an alternative lower side is truncated Neumann sums with outward-rounded
lower envelopes. The choice must be made at freeze.)

## 4. Generator (untrusted) and parameter rule

* **Proposal.**
  * It is C2b's float Nystrom / product-integration value iteration on the same grid, the discrete equation of the
    family.
  * It is then inflated to `W = (1 + eta) W_float` and deflated to `w = (1 - eta') w_float`.
  * The proposal affects **tightness only, never validity** (the C7 disclosure principle,
    `p5y_k5_tail_c7_e2_lambda309/README.md:120-126`).
* **Parameters** (N, eta, eta', iteration count, float tolerance) are fixed at freeze by a **cell-independent rule**
  that uses non-target validation only.
  * Example rule: "the smallest N on a pre-declared ladder for which the certified relative enclosure width
    (U - L)/L is <= delta at every declared validation drift", with delta stated before any validation run.
* **Forbidden:** sizing N or delta from any committed cell-308 value (the MC included), or from any distance between
  such a value and A0*. That would be optimizing against the target (S1). **[S8-corrected]** The number is no longer
  quoted here.
* **Disclosure:** the designers knew both numbers. The rule must be written so that knowing them changes nothing it
  selects.
* **The float proposal at e_lo is itself an estimate of Lambda_308**, a target-equivalent number.
  * It is generated only **after** the marker, inside the sealed run.
  * It is never printed or logged outside the result file.

## 5. Arithmetic

* Python stdlib only: `fractions.Fraction` / integer fixed point, with outward rounding on a 2^-k grid (k frozen).
* Phi/phi enclosures come from `c7_gaussian.py`, a pure library permitted by Q3 after re-reading.
* No float reaches a certified value. Every kernel integral is enclosed with a proved remainder.
* Interpreter flags `-I -S -B` are enforced through `sys.flags` (C12-R1 N8).

## 6. Comparator (A0* bracket)

* **Stage C** runs inside the sealed run, **before** any Lambda computation.
  * It performs an exact bisection of the frozen C5-T clause of cell 308 with A1 = A2 = 0, from pinned consumer bytes
    (P3), to a pre-registered depth.
  * It returns `[A0*_lo, A0*_hi]` with the sign of Gamma certified at both ends:
    Gamma(A0*_lo,0,0) < 0 <= Gamma(A0*_hi,0,0).
  * It relies on the committed licence: Gamma is nondecreasing in A0, and a non-empty intersection is checked and
    **enforced** (C4 Condition 4, `C4_ADJUDICATION.md:539-541`).
* **A cross-check that can fail:** the bracket must contain the committed float 4.442851487961334. Otherwise the run
  ends as `CERTIFICATE_FAILED (CONSUMER_MISMATCH)`.
* The bracket is written into the result file before Stage L begins, so the comparator is fixed before Lambda is seen.
* **Rejected alternative:** evaluating Gamma(U,0,0) and Gamma(L,0,0) directly. It is valid, but it would publish two
  new knockout Gamma values at a target cell. The bracket only re-derives a number already committed as a float.

## 7. Acceptance rule (frozen decision table)

The rules are evaluated mechanically, in this order:

1. any Stage C failure → `CERTIFICATE_FAILED`;
2. upper certificate failed → U := +infinity (and L := -infinity);
3. lower certificate failed → L := -infinity;
4. `L > U` → `CERTIFICATE_FAILED (INCONSISTENT)`;
5. `U < 3.512733596` or `L > 5.218548599` → `CERTIFICATE_FAILED (CONTRADICTS_COMMITTED_CERTIFIED_BOUND)`.
   * 3.512733596 is the committed certified floor (F6) and 5.218548599 the committed certified A0 (F11).
   * These are strict comparisons against committed certified numbers, not tuned thresholds.
6. `L >= A0*_hi` → `X308_CERTIFIED`. **R-TIE**: equality counts as excluded, since Gamma = 0 is not closure.
7. `U < A0*_lo` → `NOT_X308_CERTIFIED`;
8. otherwise → `UNDECIDED`.

Rules 6 and 7 cannot both fire, because L <= U and A0*_lo <= A0*_hi. No other comparison enters the verdict.
Descriptive distances (e.g. U/A0*) may be written after the verdict but are never read by it (C4's pattern,
`C4_ADJUDICATION.md:95-99`).

## 8. Exactly-once mechanics (modelled on C12 / C12-R1 / C12-R2)

**Order:**
1. freeze;
2. qualification at the freeze commit;
3. fresh read-only qualification review, with line 2 exactly `QUALIFICATION_ACCEPTED` or `QUALIFICATION_REJECTED`
   (stop on reject);
4. user authorization;
5. grant commit, alone;
6. `execute`, once, at the grant commit;
7. execution review;
8. X308 adjudication;
9. adjudication review.

**Before the marker.** Seal preconditions are checked before anything is consumed:
* **Identity.** The worktree path, git dir, common dir and branch equal the frozen values, and HEAD is the grant
  commit. The grant chain freeze → qualification → review → grant is derived and checked exactly (C12-R2 §2).
* **Pins.** Every input is pinned by sha256 **and** git blob: cells.json, THEOREM_AD, the C5-T consumer bytes, C2b's
  generator and certifier, c7_gaussian, and this protocol.
* **Clean tree including ignored files**, restricted to the namespace
  (`git status --porcelain --ignored --untracked-files=all -- <ns>`), because `*.tmp` is gitignored
  (C12-R1 B1, `C12R1_QUALIFICATION_REVIEW.md:198-240`).
* **Output paths.** `os.path.lexists` must be false for the result `.json`, its `.tmp`, and every other output path.
  A planted file, directory, symlink, broken symlink, FIFO or socket is refused. The execution directory and its
  parents must not be symlinks (C12-R2 tests T1-T9).
* **Write probe.** A write probe in the execution directory succeeds and is removed.
* **Governance state.** No review, grant, adjudication, execution output, marker or pending ref of this campaign
  exists other than those the chain requires.

**The marker.** `git update-ref refs/x308/elo-consumed <grant> ""`. The empty old value makes it a create-only
compare-and-swap. If the ref exists, refuse. The marker is never deleted or moved (C12-R2 §6).

**After the marker:**
* **Stages.** Stage C, then Stage U, then Stage L, then the decision.
* **Failures.** Every exception, including KeyboardInterrupt, SystemExit and the wall cap, is caught, recorded and
  sealed. `write_result` and every sealer failure run inside the post-marker handler (C12-R1 repair 3).
* **Writing the result.** `os.open(path.tmp, O_CREAT|O_EXCL|O_NOFOLLOW|O_WRONLY)`, fsync, `os.replace`. Then `lstat`
  confirms a regular file, and the bytes are re-read and compared before sealing (C12-R1 repair 2; C12-R2 test X05).
* **Recovery.** `seal-only` recovers every post-marker failure and **never recomputes**.
* **Output.** Nothing target-derived is printed before the seal.

**Verifier.**
* It runs only when HEAD is the freeze commit. With `--review` it may also run at the qualification-evidence commit
  on it, but only with a clean tree and code bytes equal to the freeze (C12-R1 N3).
* It refuses at every later state: review, grant, execution or adjudication present.
* Its sandboxes are built **from the freeze commit, never from HEAD**. In C12 (B1), a verifier sandbox built at HEAD
  evaluated the target at the review and grant commits.
* Sandbox B substitutes:
  * a **decoy drift** outside the band (e.g. e = 3) for e_lo;
  * a decoy consumer for Stage C.
* Sandbox B runs every governance-state, filesystem-attack and post-marker test. No test ever evaluates at e_lo.

**Caps.**
* One invocation <= 900 s wall, evaluation <= 600 s. These are to be re-derived from non-target timing, not guessed.
* This machine only, no remote host, run under `nice`.

## 9. LEAKAGE ANALYSIS

**Q: Is a certified upper bound on Lambda_308 a Gamma proxy?**

It is not a proxy: it is a **Gamma input**. By Lemma SM(d), any certified U >= Lambda_308 is an admissible uniform A0
for cell 308 (`C4_TARGET_RECONSTRUCTION.md:8-18`). Four questions follow.

1. **Does U reveal the sign of Gamma under a committed supply? No.** This can be shown from committed numbers without
   computing anything.
   * **The committed numbers a future U would be compared against, for this question**, are two:
     * C8's largest closing A0 for cell 308 with the committed operator-mixed A1, A2 held fixed, **3.270701093**
       (`C8_DECISION.json:136`; its A1, A2 at :126-130). The C8 adjudicator verified this inversion to be exactly
       equal to C5-T at every point it reports (`ADJUDICATION_C8.md:274-276`).
     * The committed certified floor, **3.512733596** (`C8_DECISION.json:131`).
   * These two committed numbers already settle the question without any U. Every admissible A0 is
     >= Lambda_308 >= 3.512733596 > 3.270701093. So under the committed (A1, A2), **no admissible A0 closes 308**,
     and this holds for every U, not an estimated one.
   * This re-reads the committed C8 verdict; it is not a new evaluation. **[S8-corrected]** The first version also
     quoted the committed A1/A2 values and C8's A1 reduction figure. Neither is a comparison target, so both are
     removed.
2. **Does U reveal the knockout sign? Yes.** Comparing U with A0* *is* the X308 question (rule 7), which is the
   protocol's sanctioned purpose. The knockout (A1 = A2 = 0) is not a real supply (C4-N3), so this is not closure
   information.
3. **What U does carry.**
   * Together with *future* A1/A2 supplies, U fixes Gamma exactly. It would therefore tell a later campaign how much
     A1/A2 improvement closes 308 at A0 = U. That is precisely the per-cell "x-eff to close" kind of number S1 forbids
     using to choose or tune routes.
   * **Variant P** (scalar drift + Theorem M): floor r2 does not admit a scalar-drift A0 as a supply form (F16: "A
     scalar drift ... never qualifies"). U is therefore **CLOSURE-ONLY** at most.
   * **Variant B**: its block-uniform U has the floor's shape, but it is a single-implementation Abar-type statement.
     Floor r2's F1′ two-implementation rule would still not accept it alone.
4. **Informational increment over what is committed.**
   * **[S8-corrected]** The first version said here where the uncertified MC places Lambda_308, reading it through
     Theorem M. That is an outcome estimate and is withdrawn. This analysis does not estimate where U or L will fall,
     nor which outcome class the run would seal.
   * **The committed numbers U and L would be compared against** are exactly these:
     * the Stage-C bracket of A0*, which must contain the committed float 4.442851487961334 (§6);
     * the committed certified floor 3.512733596 and the committed certified A0 5.218548599, in rule 5 of §7.
   * The lower side L adds nothing closure-relevant. Lower bounds only raise the floor, which has zero leverage (C8's
     R1/R2 rows, `ADJUDICATION_C8.md:380-381`).

**Classification of result-chasing risk: MEDIUM.** This is higher than ROUTE_AUDIT_R1's LOW for X308, which covered
only the lower-bound version (`ROUTE_AUDIT_R1.md:450-459`). The risks and their mitigations:

| risk | what could go wrong | mitigation |
|---|---|---|
| procedural (optional stopping) | an `UNDECIDED` outcome invites a finer re-run until the "right" side appears | exactly one run; `UNDECIDED` is terminal; any successor is a new freeze that cites this sealed outcome and declares itself result-informed |
| parametric | the mesh and eta are tuned to the known distance between the MC and A0* | the §4 rule; freeze before any in-band evaluation; disclosure |
| downstream | U is used to size A1/A2 routes for 308 | the result file labels U `NOT_A_SUPPLY`; the adjudication must restate S1 and F16; consumption requires a user-decided floor extension frozen before any evaluation |

With all three mitigations in force, the residual risk is LOW–MEDIUM. Without them it is HIGH.

## 10. What a sealed outcome would and would not mean

* **`X308_CERTIFIED`:**
  * the uniform-A0 atom-constant family is excluded at 308, scoped exactly as in C4 Condition 1
    (`C4_ADJUDICATION.md:521-523`), against the C5-T consumer and the frozen measurement inputs;
  * zero closure leverage;
  * not "308 is unclosable".
* **`NOT_X308_CERTIFIED`:**
  * the A0 floor does not exclude 308;
  * **not** "308 is closable" (C4 Condition 3, C4-N3);
  * no coverage change, no adoption, no r6.
* **`UNDECIDED` / `CERTIFICATE_FAILED`:** no statement about 308; preserved as a negative result.
* In every case K5 remains PARTIAL and the guard stays DENY.

## 11. Open items before this draft could become a freeze

1. P2–P5 (§1); P1 is met.
2. C2b's subsolution side (or the Neumann alternative) specified and validated.
3. Stage C's depth and the exact consumer entry point pinned; qualification against C8's committed non-target values.
4. Timing caps derived from non-target runs.
5. An independent review of this draft *as a draft*, before any freeze is written.
