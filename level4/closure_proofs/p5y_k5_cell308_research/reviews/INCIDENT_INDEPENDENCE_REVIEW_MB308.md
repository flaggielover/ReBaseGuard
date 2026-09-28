# Incident-independence review of route R-MB for CUSUM m = 5 cell 308 (independent reviewer reviewINC)

INCIDENT_AUDIT_ACCEPTED

The acceptance holds only with conditions C1-C9 (section "Conditions"). Each must be met before the MB308 freeze commit
and carried into the protocol, the grant and the adjudication. There are no blockers.

## 0. Scope, reviewer, method

* **Reviewer.** reviewINC. I am a fresh reviewer and I wrote none of the material reviewed. This file is the only
  file I wrote. I appended two ledger lines (class REVIEW, agent reviewINC): one for the namespace scan and one for a
  text scan of this file. I did no git add and no commit.
* **Basis.** Committed HEAD `93058f3a` of `p5y-k5-cell308-research` (14 campaign commits `33185113..93058f3a` on top
  of `b73b9449`), plus the working-tree ledger as I read it: 162 lines, of which 160 are committed and 2 are
  uncommitted streamD lines.
* **Out of scope.** The untracked formal namespace `p5y_k5_cell308_mb_r1/` was being written during this review
  (file mtimes up to the time I read it). I read its code but do not review it, except for the ledgered rehearsal
  covered in Q6.
* **What I read.** Everything listed in the brief. I also read:
  * `OV/reviews/REVIEW_C2B_STRATEGY_R1.md` N2;
  * `OV/streams/C_308/A0X/gen/C2B_ROUTE_SUMMARY.md` §2.1;
  * `LP/p5y_k5_m5_tail_closure/theorem/THEOREM_TCT.md` §0-§4, with digits masked;
  * `OV/streams/E_assembly/THEOREM_TPT.md` §0, with digits masked;
  * the C9 README (α lever);
  * the formal driver's `rehearse` / `control_ca` / `control_cb`.
* **What I ran.**
  * `git log`, `git show`, `git merge-base --is-ancestor` and `git ls-tree` / `cat-file` for every cited commit.
  * `code/c308_quarantine.py --scan` (ledgered).
  * My own extended grep. It uses the scanner's TAIL_FIGURES plus committed tail values that the scanner does not
    list (the R4 coefficients, the C3 uniform factor, the saturation value, the MC and floor digits) and the 308
    geometry. I ran it:
    * over the working tree of NS outside `history/` and `ledger/`;
    * over every NS blob committed in `b73b9449..HEAD`;
    * over the formal namespace.
* **Hard rules kept.** No certifier, consumer, driver or reconstruction was run. Nothing was computed for cells
  305-309 or at any drift in [6/5, 13/5] or its mirror. No committed tail figure is written here: history items are
  cited by id.
* **Not checked.** The agent briefs are not in the committed record. The session transcripts were not accessible to
  me, so the briefs could not be checked (C5).
* **Audit recommendation.** The audit's recommendation carried no weight.

## Q1. Prospective motivation of every load-bearing element

**Answer: yes, temporally and parametrically. Not motivationally.**

**Timeline check.** I checked every commit in audit §2 in the object store. Each exists, is an ancestor of HEAD, and
touches the named file.

| element | commit and time (+0900) |
|---|---|
| Theorem M: EXCLUSION_308 §(c) c.6 | added at `7e851139` 09-28 03:56:59; corrected at `0d32a2e8` 04:03 |
| Theorem M review / corrections | `07ab6b94` 05:13 / `5a49f37b` 05:14 |
| THEOREM_AD | added at `f0231499` 09-19 |
| TPT | `af4365aa` 02:46 |
| TPT-B | `ccc4ea36` 03:23 |
| cross-route §5 | `bcb9c699` 05:21, corrected at `0b44c947` 07:50 |
| B2c | `6d0f0615` 04:09 |
| RLR | `cbff958a` 02:49 … `d3b60795` 10:51 |
| 307 campaign | `cd5016f1` … `b73b9449` 20:53 |
| C2b / review | `06a7d6a5` 05:28 / `1ee93ac5` 06:06 |
| charter | `33185113` 21:36 |
| Theorem MB r0 / review / r1 | `b6ab352e` 21:48 / `5dd80cb9` 22:36 / `bfa9ad3c` 22:43 |

**Before any 308 outcome.** Every inherited element predates the charter. Every new element (the Theorem MB lemmas,
`tptb_tail`, the A0 exact-scale and `sub_certify` code, ladder R1-R6, D1-D12) predates any cell-308 value of R-MB,
because no such value exists: see Q2.

**Timeline defects.** None of them changes this answer.

* **(i) Unsupported start time.** Audit §2 gives Theorem M's start as "02:00". The object store supports only
  03:56.
* **(ii) Uncommitted at audit time.** The A0 components (`a0_ladder.py`, `a0_c2bx.py`, `a0_c2b.py`) were first
  committed at `646e7e18` (09-29 01:10). That is after the audit (`4b55c67e`, 23:46) and after design d0
  (`c8b68d4d`, 23:44), which already fixed D4. So the audit's A0 rows were not verifiable when it was written. The
  committed R1 matches d0/d1 D4.
* **(iii) Ordering claim contradicted by the ledger.** The A0 study says the ladder was fixed "before any exact-scale
  or hull result". The ledger shows otherwise:
  * the first c2bx job ran at 13:10:55Z and c1bh jobs at 13:37Z;
  * the ladder runs started at 13:43Z;
  * C1b d = 8 was added after those runs started.

  This is harmless for target independence (Q3), but the temporal claim is wrong.

**Motivation.** Motivation is not independent.

* Theorem M came out of the overnight 308 exclusion stream (incidents 02 and 03).
* TPT and TPT-B were designed with the committed tail radius structure known (incident 01).
* R-MB's family was chosen knowing I-a to I-e.

Like the 307 precedent (its conclusion 1 and C1), "independent of target outcome" can only mean temporal plus
parametric independence here (C3).

## Q2. New Gamma308 values or target-equivalent proxies

**Answer: no new Γ308 value and no numeric proxy of R-MB for 308.** One quarantine-scope deviation (C2).

**Ledger.** I parsed all 162 lines.
* Every line has `new_target_evaluations`, `target_equivalent_proxies` and `target_informed_optimisation` equal to 0.
* No line has a LEAK_FLAG.
* Cell 308 appears only on the coordinator's lines 2-3 (HISTORICAL_READ, PRUNING_FROM_COMMITTED) and on stream A's
  lines 9-10 and 98-99 (HISTORICAL_RECONSTRUCTION START/END, HISTORICAL_READ, PRUNING_FROM_COMMITTED).
* Cell 305 appears once, on line 145 (builder, HISTORICAL_RECONSTRUCTION; see Q6).
* No validation-class line names a tail cell or a band drift.

**Reconstruction.** It stayed inside its pre-registration.
* **Written before the run.** The mtimes are: `RECON_PREREGISTRATION.md` 13:00:13Z, `recon_308.py` 13:03:35Z, JSON
  13:04:30Z.
* **One run.** `log_event` is the first statement of `main()`, and the ledger holds exactly one START/END pair. So
  there was exactly one run of `main()`.
* **Registered points only.** The script evaluates the seven registered points and nothing else (P_SI1, P_MIX, P_KO,
  P_CRIT, P_4311, P_4375, P_ZERO).
* **Outputs reproduce committed values.** The 55/55 outputs reproduce committed values.
* **Git cannot show the order.** The pre-registration, script and output were committed together in `4349dd55`, so
  "pre-registration before the run" rests on mtimes and the ledger, not on git.

**Deviation from the frozen quarantine (C2).** The quarantine's `allowed` clause limits HISTORICAL_RECONSTRUCTION in
four ways:
1. to the C3 knockout row and the C4 §4 statement;
2. to output that is "only the committed value and an equality boolean";
3. to values in `history/HISTORY_308.md`;
4. to a stream's own pre-registration, which may not widen it.

Stream A's pre-registration widened it in two ways:
* R1 reproduces C2's S_I1 record.
* R4 writes the exact coefficients of the direct clause for 308 into `history/recon/`: g_hi, G0, C_lo, C_hi, P̄0-P̄2,
  the R2 interval, M_R2. These are a complete direct-clause Γ308 evaluator for any uniform supply.

Assessment of this deviation:
* **Equivalent to committed values.** Every coefficient is determined by committed inputs and values:
  * the adopted R2 interval and M_R2;
  * `cells.json`;
  * the committed H_exact;
  * the committed Γ at P_ZERO, P_KO, P_SI1 and P_MIX, which fix G0 and P̄2, then P̄1 and P̄0.

  So no new target information was created.
* **Not a proxy for R-MB.** R-MB's decision quantity is TPT-B, not the direct clause. By the dominance chain the
  evaluator yields only upper bounds that are uninformative about R-MB's sign.
* **Still a silent widening of a frozen gate.** It is the same defect class as "never narrow a frozen gate silently".

**Leak scans.**
* **Namespace scan.** `c308_quarantine.py --scan` gives PASS: 50 py and 312 text files, 0 findings, and both planted
  controls fired. Tail figures appear only in the six sanctioned `history/` files and `recon_308.py` (historical-read
  mark).
* **Own grep.** With the extended list:
  * no committed tail figure appears outside `history/` and `ledger/` in the working tree, in any blob committed in
    `b73b9449..HEAD`, or in the formal namespace;
  * the one exception is the scanner's own planted controls in `code/c308_quarantine.py` (self-excluded; C8);
  * the 308 cover geometry appears only in the quarantine config and the formal guard.
* **Stream outputs.** Validation-drift values stay in `streams/A0`, `streams/VERIFY` and `reviews/scratch_*`. None of
  them sits beside a tail number.

**Latent proxies.** The A0 certificates at 11/10 and 27/10 bracket the band. By Theorem M they bound Λ over the whole
band, 308 included. They are declared latent proxies, and no transfer has been written anywhere.

## Q3. Parameter selection and target information

**Answer: no R-MB parameter was selected using target information.** The audit's stated evidence for the pointwise
ladder is wrong, though (C1a).

| parameter | finding |
|---|---|
| **pointwise ladder** (C2b-x N ∈ {20, 40, 80}; C1b d ∈ {8, 10, 12}; min U / max L) | Selected from findings F1-F4 at the brief's declared drifts {1/2, 1, 11/10, 27/10, 3, 7/2} and from cost. The findings are: α grid binding; exact-scale selection; C1b non-monotone in d. U = min over certified rungs, so adding a rung can only tighten a valid bound, and dropping N = 160 was a cost cap. No selection rule reads a band value. **However**, the audit's premise "the stream had no tail figure" is false. `a0_c2bx.py:4` quotes `C2B_ROUTE_SUMMARY.md` §2.1 line 52. That section's line 49 is the incident-03 sentence: the brief's comparison scale derived from 308 figures. So stream A0 was exposed to the incident-03 scale, and this is undisclosed. Every ladder rung is far tighter than any such scale, so the scale could not discriminate between rungs. The exposure is qualitative and not load-bearing. |
| **partition / hulls / RLR ladder** | Inherited unchanged: C2's width rule, 307's 2^-20 hull, and 307's (4, 6, 8) with its flags. That is reuse, not re-tuning. The 307 review (C5) already put the 307-added decisions under qualification review. |
| **member set** | All available members (S_I1, Dv′-M on C1 and C2, D14-M, G), taken as a componentwise min. This is the committed pre-campaign dominance order (`CROSS_ROUTE_THEOREM_COMPARISON.md` §5, `bcb9c699`/`0b44c947`), so a target-blind dominance selector would pick the same set. Gap: C9's E1 / α lever (a tighter taboo τ) is absent from the registry and has no recorded target-free exclusion reason (C6). |
| **TPT-B consumer** | It carries the incident-01 liability, which is motivational. No free parameter: the piece-end rule is forced by review correction C4, and the cap split and tolerance are inherited from the pinned `tpt.py` r2. Including it is also what dominance dictates (TPT-B is the strongest proved transport, §5). |
| **decision Γ_dec = g_hi + max(P*_B, P_hi) < 0** | Target-free and anti-chasing. Both implementations must certify, the inequality is strict, and the arithmetic is exact. D12's bracket rule and D5's fail-closed admission (d1) can only make closure harder. |
| **EVAL_CAP / workers** | These come from decoy costs, which are runtime and not value. The decoy Stage-1 outputs at 297 and 316 will be latent proxies (C7b). |

## Q4. Coordinator inferences I-a..I-e and the result-chasing classification

**Are I-a to I-e a new proxy exposure?** No, not a new numeric one.

* **I-a.** It is the committed C3 knockout, which the brief asks the campaign to verify. Stream A reproduced it.
* **I-b.** It compares committed numbers with committed numbers (H1.1/H1.2 against H1.7 and H2.2) at the idealised
  limit of a family. No measured factor of a new route enters, so it satisfies the quarantine's PRUNING rule. But:
  * it rests on an uncertified Monte Carlo value;
  * it is an outcome judgement about a route component under a committed consumer (Dv′-M with eff → Λ₃₀₈, under
    C5-T), which is why it belongs in the disclosure.
* **I-c and I-e.** They are qualitative, and they concern the existing consumer.
* **I-d.** It is the inherited incident-01 state.

Ledger line 3 classes all of this correctly as PRUNING_FROM_COMMITTED.

**The disclosure is stale.** It was committed once, at `33185113`, and never updated. After it the coordinator read
and committed:
* stream A's R4 exact direct-clause coefficients, the pruning theorems P308-D/T and H1.8 (`4349dd55`);
* H4.3b (via the inventory);
* the A0 validation tables at the band-bracketing drifts (`646e7e18`).

The coordinator therefore now holds every ingredient of an incident-01-class estimator of R-MB's own outcome:
* the committed radius shares (H3) and the generic TPT-G charges;
* the committed atom constants and the MC Λ values;
* the uniform-eff factors;
* the exact direct-clause coefficients;
* certified Λ brackets across the band.

No one has formed that estimate, as far as the record shows. The state must still be disclosed as such (C1c, C3).

**Is route-family selection from committed facts acceptable?** Yes.
* The quarantine explicitly allows pruning from committed facts that attaches no measured gain of a new route.
* The brief instructs pruning by the C3 knockout.
* The 307 precedent accepted a channel and cell chosen from the same knockout.
* The choice made here (keep every component and add a consumer-side transport) coincides with the committed
  pre-campaign dominance order (§5). So the family would also be the output of a target-blind dominance selector.

This does not remove the motivational liability.

**Is MEDIUM–HIGH the right classification?** Yes. It should not be lowered.
* **Why not lower.** The route family, its consumer and its cell were chosen with committed 308 structure in view,
  and the coordinator holds a near-complete estimator.
* **Why not HIGH.**
  * No parameter is free after the freeze.
  * Every component is a certified bound, so a result-chaser cannot manufacture a false closure.
  * D10 forbids evaluating any other route on 308.
  * There is exactly one sealed evaluation, and NOT_CLOSED and INDETERMINATE are pre-declared outcomes.

The residual liberty is which valid test is run. That is motivation, which is exactly what MEDIUM–HIGH describes.

## Q5. Incidents 01-03 and H4.3b

**Answer: all relevant as disclosures. None blocks.** Incident 01, however, imposes a user-ruling precondition on the
grant (C4).

* **Incident 01 (+ residue; OV ledger lines 81 and 192).** Directly relevant, because R-MB's consumer is a profile
  transport. INCIDENT_01 consequence 2 and `FREEZE_DESIGN_TPT_TAIL.md` §0 set two requirements:
  * The authorizing user must see the incident.
  * The user must rule on U3 before any evaluation, either a floor extension or an explicit CLOSURE_ONLY.

  The research charter declares closure-only, but that is the coordinator's text. No committed record shows a user
  ruling taken knowing the incident, and the campaign brief is not committed. Disclosure suffices only if the grant
  records that ruling (C4). The overnight BLOCKED status was scoped to "this campaign" (the overnight one), so it does
  not bar a later, separately authorized campaign.
* **Incident 02 (line 155 + residue 193).** Classified correctly as exclusion-direction. R-MB uses only upper bounds
  certified at 308's own block drifts (Lemma M-U with N8: certificates only at the pre-declared b_i, inside the
  grant). No cross-cell attribution enters R-MB. It is relevant only as the provenance of Theorem M.
* **Incident 03 (line 175).** Relevant: C2b is on the U path. The audit's mitigation claim is inaccurate: stream A0
  read the §2.1 section that carries the scale sentence (Q3; C1a). The C2b code and checker are unaffected. The
  exposure is qualitative and non-parametric, so disclosure suffices once it is corrected.
* **H4.3b** (`ROUTE_AUDIT.md:315`, `d52cec02`, committed before any quarantine). It sets C9's projected 307 α-lever
  factor beside 308's C5-T closing factor. That is the incident-01 shape.
  * The audit's "no bearing on any R-MB parameter" is right for parameters.
  * It misses a route-selection bearing: the α lever (E1) is the one known tail route family that is missing from the
    308 registry.
  * If it was left out because of H4.3b, that would be pruning by a route factor set against a tail threshold, which
    the quarantine forbids.
  * A target-free reason exists: stdlib-only toolchain, while the α lever needs numpy/python-flint per the C9 STOP
    record, plus a host. But it is not recorded (C6).
* **L6 (306).** Not relevant.

## Q6. What the audit missed

**F1. Stream A0 exposure to the incident-03 scale.** See Q3 and Q5. The A0 study, the audit §3 L3 row and
conclusion 4 all say the stream held no tail information. They are wrong.

**F2. F2 and F3 exposure.**
* F2 read THEOREM_TCT §0-§4 and THEOREM_TPT §0-§2b, with its timeline at 14:47Z.
* F3 read THEOREM_TCT lines 1-131 (ledger 148).
* THEOREM_TCT §1-§3 carries committed tail-cell figures: the Lemma G supply ranges over 305-309, σ3 values, and
  per-cell values across 305-309. THEOREM_TPT §0 carries the committed midpoint-residual share.
* So F2's report sentence "No tail-cell number was read or written" and F3's "theorem text and input schema only"
  are inaccurate. The audit's §3 stream-exposure row omits both streams.
* Neither exposure can bias an exact-equality cross-check.

**F3. Stale coordinator disclosure.** See Q4.

**F4. Pre-review formal work.**
* The builder ran the untracked formal driver's `rehearse --cell 305` at 16:07:45Z (ledger 145), with
  `allow_uncommitted=True`. That was after the audit and before this review.
* It read the multi-cell committed files (C2 D5 forecast, adopted tail inputs, REGISTRY_C1/C2), which hold 308's
  records in memory.
* It reported equality booleans only. `control_cb` runs under tripwires on every transport penalty.
* QC01 declared this in d0 (`c8b68d4d`) before it ran, and the 307 campaign had the same pattern (307 review F8). It
  is acceptable in kind, but the audit does not mention it and its output file is not in the record (C7a).

**F5. Briefs not recorded.**
* No brief of this campaign is committed (streams A, C/A0, D, E, F2, F3, reviewMB, reviewA0, builder).
* The 307 campaign committed its overnight briefs with hashes after its review's C4.
* Charter rule 7 ("no tail figure in a brief") therefore cannot be verified.
* Two stream outputs depend visibly on brief content: A0's declared drifts are the band-bracketing ones, and
  ASSEMBLY's decoy regimes "follow the brief's wording" (C5).

**F6. Registry gap: C9 E1 / α lever.** See Q5 (C6).

**F7. Scanner planted strings.**
* `code/c308_quarantine.py` lines 294-319 hold committed tail figures in its planted controls.
* One of them is a synthetic incident-01-shaped phrase: a generic "route gain" on the order-3 term beside the
  committed critical A0.
* The file is self-excluded from the scan. The planted gain is not a measured factor, so this is not a proxy. It
  should still not be copied into the formal package (C8).

**F8. Quarantine widening by stream A's R1/R4.** See Q2 (C2).

**F9. Timeline precision.** See Q1 (i)-(iii).

**No other target reads found.** Beyond the above, I found:
* no read of target inputs outside `history/recon/` (stream A) and the builder rehearsal;
* no unledgered execution;
* no evaluation at a band drift.

`git status --short --ignored` shows no change under `level4/` outside the research and formal namespaces. In
particular the overnight and 307 namespaces are clean.

## Blockers

None. The committed record does not falsify any of the audit's five conclusions.

| # | status |
|---|---|
| 1 | accepted as temporal and parametric independence |
| 2 | accepted |
| 3 | accepted in the numeric sense |
| 4 | accepted on corrected evidence |
| 5 | accepted, with MEDIUM–HIGH retained |

The defects are gaps in the audit's inventory and hygiene. None of them reached a load-bearing element. This is the
same class of defect that the 307 review accepted with conditions.

## Conditions

Every condition must be met **before the MB308 freeze commit**. Every condition is carried verbatim into the
protocol, the grant and the adjudication.

**C1, audit a1.** Amend the incident audit as an addendum; the a0 text is kept. Add:
* **(a)** Stream A0 read the incident-03 sentence (`C2B_ROUTE_SUMMARY.md` §2.1, cited at `a0_c2bx.py:4`). State
  conclusion 4's evidence as the F1-F4 findings plus rung monotonicity, not as "no tail figure".
* **(b)** The F2/F3 exposures via THEOREM_TCT §1-§3 and THEOREM_TPT §0. Record them as exposures, with corrections
  noted beside the committed reports (the reports are not rewritten).
* **(c)** An addendum E1′ to `COORDINATOR_EXPOSURE_DISCLOSURE.md` listing:
  * what the coordinator read after `33185113`: R4 coefficients, P308-D/T, H1.8, H4.3b, the A0 tables at the
    band-bracketing drifts;
  * the statement that it holds every ingredient of an incident-01-class estimator of R-MB's outcome, and has not
    formed it.
* **(d)** The builder's rehearsal and the pre-review formal build.
* **(e)** The Q1 timeline corrections.

**C2, quarantine record.**
* Append one ledger line (class QUARANTINE_RULE_BREACH, proxies 0) recording that stream A's R1 and R4 exceeded the
  quarantine's HISTORICAL_RECONSTRUCTION allowance.
* Add an explicit amendment recording what is permitted.
* The R4 coefficients stay in `history/recon/` only.
* No formal-namespace file may read `C3_KNOCKOUT_RECONSTRUCTION.json`. C-A recomputes from committed inputs.

**C3, independence statement.**
* Every document uses "independent of target outcome" to mean temporal and parametric independence only.
* Motivational independence is not claimed: the family, the consumer and the cell were chosen knowing committed 308
  facts.
* The result-chasing risk stays MEDIUM–HIGH.

**C4, user ruling.** Before any target evaluation, the grant must record the user's explicit CLOSURE_ONLY ruling for
a profile-transport consumer on 308 (INCIDENT_01 consequence 2; FREEZE_DESIGN_TPT_TAIL §0.1-0.2). The ruling must be
taken with the following in view:
* incident 01 and its residue;
* incidents 02 and 03;
* H4.3b;
* I-a to I-e and the E1′ addendum;
* this review.

**C5, briefs.** Commit every agent brief of this campaign, or its sha256 in the ledger, before the freeze (307
precedent). This includes the builder and this reviewer. A brief found to contain a tail figure or a 308-derived
scale is recorded as an incident.

**C6, registry completeness.**
* Add C9 E1 / the α lever, and any other known tail route family that is absent, with a target-free status: toolchain,
  host, data, or logical position (S3/S5).
* State explicitly that it was not pruned by H4.3b.
* No component is excluded by estimated effect on 308.

**C7, rehearsal and decoys.**
* **(a)** The rehearsal:
  * commit the pre-freeze rehearsal's output file, or its hash;
  * the qualification review verifies, on the frozen driver, that C-A and C-B on 305 and C-B on 308 yield
    reproduction values and equality booleans only, with the tripwires provably armed.
* **(b)** The QC02 and QC03 decoy Stage-1 outputs on cells 297 and 316:
  * they are latent proxies (T1);
  * ledger each run;
  * commit the outputs or their hashes;
  * only runtime and status may enter EVAL_CAP;
  * never juxtapose them with a tail figure;
  * no decoy may lie nearer the band than 297 and 316.

**C8, scanner.**
* The formal package's scanner builds its planted tail strings at run time, or keeps them in a sanctioned file.
* It carries no gain-beside-threshold phrase.
* The research scanner's self-excluded literals are disclosed in a1.

**C9, unchanged mechanics.** These stay exactly as designed:
* D10: nothing but R-MB is evaluated on 308;
* d1 §5.4, frozen: Γ_dec = g_hi + max(P*_B, P_hi), strict, exact;
* one sealed execution, with no retry and no post-result tuning.

QC13's incident-independence gate must cite this file and check C1-C8 by path.

## Notes

* **N1. Working tree.** The tree moved while I reviewed:
  * streamD's VERIFY files and two of its ledger lines are uncommitted;
  * the formal namespace is untracked and was still being written.

  This review covers `93058f3a` plus the ledger as read. It does not qualify the formal code.
* **N2. Evidence strength.** The one-run evidence for R1-R4 comes from the ledger and from `log_event` being the
  first statement of `main()`. The pre-registration order comes from mtimes. Neither is a git fact.
* **N3. D5 in d1.** The fail-closed admission rule (the cross-implementation alarm; C2b rungs unadmitted until the PL
  verifier exists) can only make closure harder. It is not a result-chasing lever.
* **N4. Reproduction (read-only).**

  ```bash
  git log -1 --format='%h %cd' <each §2 commit>
  git merge-base --is-ancestor <c> HEAD
  git log --format=%h -- <NS file>
  python3 -I -S -B NS/code/c308_quarantine.py --scan        # PASS 50 py / 312 text, 0 findings
  grep -n 'C2B_ROUTE_SUMMARY' NS/streams/A0/a0_c2bx.py        # line 4
  sed -n 36,53p OV/streams/C_308/A0X/gen/C2B_ROUTE_SUMMARY.md # section 2.1, incident-03 sentence at 49
  ```

  Plus a digit-masked grep of THEOREM_TCT.md lines 1-131 and THEOREM_TPT.md §0, and the ledger parse in Q2.
