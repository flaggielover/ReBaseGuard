# Delta review: SUCCESSOR_ROUTE_AUDIT_308_ADDENDUM_A1.md against route-review conditions RC1-RC6
DELTA_REJECTED

Reviewer: reviewROUTE, the same independent reviewer, resumed. Date: 2026-09-30.

Mode: read-only. No git write, no driver mode, nothing computed for cells 305-309 or the band, no effect estimate
on 308, cell 309 untouched.

Reviewed object: `registry/SUCCESSOR_ROUTE_AUDIT_308_ADDENDUM_A1.md` at research `ce145e51` (100 lines). The
original audit is byte-unchanged since `bddd85f8` (verified). The base review is `REVIEW_SUCCESSOR_ROUTE_308.md` at
`a1d1c7d4`, sha256 `47bbd9b7…8c230be` (verified).

Also read, for the cross-references A1 makes:
* `governance/SUCCESSOR_GOVERNANCE_308_ADDENDUM_A1.md` §1, §3 and §4 (S12-S15);
* `governance/SUCCESSOR_ARCHITECTURE_308.md` §4;
* `ledger/USER_TEXTS_SUCCESSOR_308.md` §1c (the brief's §26, verbatim).

## 1. What A1 discharges

* **The route is unchanged: MB-S.** The science list in A1 §3 matches RC1. Nothing in A1 adds a member or changes a
  rule or the criterion.
* **RC3: discharged.**
  * MB-S is stated to be a candidate only until the governance determination is accepted. The rejection
    `e3c60491` is cited correctly.
  * The incident-review C9 quotation and the qualification-review E7 quotation are exact.
  * The second consumption is admissible only through S1 (lifting mitigation 5) and S7, and is disclosed in the
    adjudication.
* **RC1: stated faithfully for its pre-marker scope, and not weakened.**
  * The science is listed at `c46434a3`.
  * The driver's science functions must be text-identical, checked by a function-level AST equality test in
    qualification; any change needs an equivalence argument and falls under RC2.
  * The guard may differ only in namespace, ref and marker constants, and a test enforces this.
  * D11 is classed as infrastructure.
* **RC2: stated faithfully for its pre-marker scope.** It covers:
  * the pin set: the interpreter path and sha256, the libpython sha256, `sys.version`, the OS build and the
    architecture;
  * the ban on OS and Python updates between qualification and execution;
  * the MBR1_REPRO case (QC02, QC03 blocks 0-2, the QC04 pair, exact equality with timing stripped), with STOP on
    any mismatch and E8 applied.
* **RC4: mostly discharged.**
  * "Strongest" is now scoped.
  * The determinism claim is made conditional on RC2.
  * The deferral is stated as a preference under S4.
  * "Not tonight" is withdrawn.
  * The catch-all row is given a status.
  * The exceptions are DR1, N1 and N2 below.
* **RC5: partly discharged.** The HOST row is added. For the MB-VAR row, see DR3.
* **RC6: partly discharged.**
  * Risks (a) to (e) and the four original risks are all carried.
  * The advance decision is made: sealed checkpoints with mandatory resume.
  * Q12 is re-measured under the new launcher.
  * For the resume semantics, see DR2.

## 2. Defects (grounds for rejection; each needs a bounded erratum)

* **DR1. The foreclosure sentence misstates the user's §26, and the claim that the user will see the trade has
  nothing behind it.**
  * **What A1 says.** A1 §1 says that adding C11R-I2 or COR-T after an MB-S outcome is something "the grant, U6,
    the brief's §26 and the floor r2 / cell-306 precedent forbid". It concludes that choosing MB-S "forecloses"
    those members.
  * **What §26 says, verbatim** (USER_TEXTS §1c): "If such a route genuinely existed prospectively before the target
    was seen, document temporal evidence and obtain independent governance review before considering it."
    * C11R-I2 and COR-T were recorded in registry r2 (`8da57f89`) before the MB r1 freeze.
    * §26 therefore does not forbid them. It sets a path for them: temporal evidence plus independent governance
      review, with the post-result liability that entails.
  * **The other citations do not support "forbid" either.**
    * U6 and the grant speak of variants selected "from its result", meaning MB r1's result.
    * The cell-306 precedent concerns re-running the same route after an observed outcome.
    * The accurate statement is the one my review made: deferring now *may* foreclose them, or at least makes any
      later use post-result, exposed and governed.
  * **The cited place does not carry the trade.** A1 says the user sees this trade before S1 via the governance
    addendum A1 §3. That section lists six items for the S1 ruling, and none of them is this trade.
  * **Repair:**
    * Correct the sentence to match §26 verbatim.
    * Drop "§26" and the precedent from the list of texts said to forbid.
    * Either put the trade into the S1 content, or stop claiming that it is there.
* **DR2. A1's own RC6 choice opens a gap in RC2, and A1 states the determinism claim for resume without its
  condition.**
  * A1 item 7 says: "Because of determinism, a resumed evaluation equals an uninterrupted one."
  * Resume exists for the host-reset case and may run on another boot, up to 7 days after the marker (architecture
    §4).
  * RC2's pin is checked only "before the marker". Architecture §4's resume checks checkpoint hash, schema and
    binding, but not the platform.
  * Suppose an OS or Python update lands at a reboot within the window. Resume would then mix job records from two
    platforms. REVIEW_A0_CERTIFIER_R1 N2 says the certified values are platform-dependent, so the claim would be
    false.
  * **Repair:**
    * Re-verify the full RC2 pin at every resume, and in any mode that computes.
    * A mismatch goes to a frozen terminal rule (close-indeterminate), never a mixed-platform resume.
    * The no-update rule covers the whole post-marker window up to the deadline, with automatic updates disabled.
    * Make the sentence conditional on the pin holding at every resume and on verified checkpoints.
* **DR3. The MB-VAR row drops the verification-budget variant.**
  * RC5 and my check 6 name protocol decision **D14, the verification budgets**, as a lever, for example a budget
    that would admit C1b upper rungs with d ≥ 8.
  * A1 lists a "D14 slot rule" instead. That is a different object: the A0 slot of THEOREM_RLR307's D14 member.
    The budget variant is absent.
  * **Repair:** add "verification budgets (protocol D14)" to MB-VAR. The slot rule may stay, labelled unambiguously.

## 3. Notes (not grounds for rejection)

* **N1 (P1).** "Only P0 is certified" should read "only P0's pruning is certified in full". PRUNING_308 P-D-b and
  P-D-c are certified results bearing on P1's family, and registry r2 says "the certified part is stated in
  PRUNING_308".
* **N2 (R2).** Two sharper wordings:
  * The C1b lower rung is also D5(ii)'s precondition for admitting any C2b rung: without it the status is
    ALARM_UNAVAILABLE and the rung is not admitted. "Alarm only" should say so.
  * "Supplies no upper bound" should read "no pointwise upper bound". The same pinned C1b produces the RLR block
    certificates.
* **N3 (RC1).** The successor protocol should list the driver's science functions (at least the check-4 list of my
  review). The AST test should also cover the module-level names those functions reference: constants, helpers and
  imported module objects. Text-identical functions can otherwise bind to different values.
* **N4 (HOST row).** RC2's pin cannot hold on another host by construction. The row therefore means "S4 changed
  branch only". My RC5 wording ("unless RC2 is discharged there") invited the tension; A1's reason column resolves
  it correctly.
* **N5 (D11 and caps).** A1 says D11 "is re-derived" by the §3.2 rule. Governance addendum A1 §3 item 4 and GC-9
  make the choice between keeping MB r1's caps and re-deriving them a recorded user decision. The two texts should
  say the same thing.

## 4. Verdict

A1 keeps the route and discharges RC3. It states RC1 and RC2 without weakening them for their pre-marker scope, and
carries the risk register. It is rejected on three bounded defects:
* DR1: a misstatement of the user's §26, and an unsupported claim that the user will see the trade;
* DR2: the determinism claim for resume is stated without the platform pin at resume;
* DR3: the verification-budget variant is missing from MB-VAR.

An erratum repairing DR1-DR3, with A1 and the audit kept unchanged, and a narrow re-check by this reviewer, suffice.
The ROUTE_ACCEPTED verdict under RC1-RC6 stands.

New target evaluations: 0. Band drifts: 0. Proxies: 0.
