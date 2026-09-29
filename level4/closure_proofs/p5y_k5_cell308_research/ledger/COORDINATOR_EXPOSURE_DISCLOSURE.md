# Coordinator exposure disclosure (written before any science of this campaign)

The campaign coordinator (the main agent of this session) is **not** target-blind. This record states exactly what it
knew and inferred about cell 308 before any route work started, so that motivation provenance can be judged by an
independent reviewer. Values are kept in `history/HISTORY_308.md`; this file names them by id only.

## E1. Committed facts read during start-state reconstruction (class HISTORICAL_READ)

* H1.1 (C2 D5 forecast record for 308, including Γ, the S_I1 atom constants and the required uniform reduction).
* H1.2–H1.3 (C3 mixed supply and the C3 knockout row for 308).
* H1.4–H1.5 (C4 frozen-clause critical A0; the C4 adjudicator's section-4 statement at the MC value).
* H1.6–H1.7 (C8 phase-4 inversion and the uniform-eff factors under C5-T).
* H2.1–H2.4 (certified floor, Monte-Carlo values, float diagnostic of Λ₃₀₈).
* From project memory and the overnight record: the committed C5 decomposition of the tail radius (H3), the TPT-G
  over-charge formula, and incidents 01–03 (H4).

## E2. Inferences the coordinator formed from committed facts only (no code, no new number written anywhere)

* **I-a (C3 knockout, restated).** An A1/A2-only improvement cannot close 308 under the frozen consumer and frozen
  inputs (H1.3). This is the committed pruning the campaign brief asks to verify.
* **I-b (idealised proportional-eff family).** Under Lemma Dv′ all three atom constants are proportional to
  eff = min(Ā, τ/D_lo) ≥ Λ₃₀₈. Reading H1.1/H1.2 against H1.7 and H2.2, the coordinator concluded that even
  eff = Λ₃₀₈ (a perfect order-0 certificate propagated proportionally) would not reach the committed uniform
  closure factor **if** Λ₃₀₈ is near its Monte-Carlo value. This compares committed numbers with committed numbers
  and the idealised limit of a family; it attaches no measured factor of any new route. Status: evidenced by an
  uncertified MC, not certified.
* **I-c (consumer side).** From I-a and I-b the coordinator concluded that a host-free route to 308 must change a
  consumer-side inequality (assembly/transport), not only the atom constants. The overnight campaign had already
  committed, before this campaign, that the strongest host-free combination is
  TPT ∘ min(RLR, Dv′, Lemma G) ∘ (tight A0) (`p5y_k5_tail_overnight_research/registry/CROSS_ROUTE_THEOREM_COMPARISON.md` §5).
* **I-d (inherited incident-01 state).** The coordinator knows both the committed tail radius shares and TPT-G's
  generic over-charge factors. It is therefore in the epistemic state that incident 01 recorded. It did not write or
  compute their product in this campaign. Any TPT/profile-transport use for 308 carries the incident-01 liability.
* **I-e (qualitative heuristic about the existing consumer).** While reading H1.5 the coordinator considered, in
  prose reasoning only, the order of magnitude of the sharp first- and second-order atom-constant channels for a
  Gaussian walk with a few steps to alarm, and judged the committed 18-fold requirement implausible to meet. This
  concerns the *existing-consumer* atom-constant family (already disfavoured by committed C4 Condition 3), not the
  outcome of any new route. No number was written.

## E3. Consequences for this campaign

* Result-chasing risk of any route that includes a profile transport (TPT/TPT-B): **MEDIUM–HIGH** (inherited from
  incident 01, plus I-b/I-c).
* Result-chasing risk of an order-0 (A0) certificate route alone: **MEDIUM** (the coordinator knows the committed
  thresholds H1.3–H1.6 and the MC values H2.2).
* Mitigations, bound into the charter:
  1. route selection by **logical dominance only** (include every reviewed, sound component; no choice among
     components by estimated effect);
  2. every parameter fixed by a target-free rule declared before any evaluation;
  3. no tail figure outside `history/` and `ledger/` (scanner-enforced);
  4. independent incident-independence review before any freeze;
  5. at most one target evaluation, of one frozen route.

## E1′. Addendum (2026-09-29; incident review condition C1(c)) — what the coordinator saw after the charter `33185113`

Values stay in `history/`; this addendum names what was seen.

* **Stream A hand-back** (read in full): the pruning statements P308-D (direct clause) and P308-T (C5-T clause) in
  words, the reconstruction results including the reproduced C4 factor and the value of Γ just above the critical A0,
  and discrepancies D1–D8 (including the C5 adjudicator's "misses by …" wording). The exact R4 coefficients in
  `history/recon/C3_KNOCKOUT_RECONSTRUCTION.json` were **not** opened by the coordinator; the review's statement that
  they were read is corrected here to "available to the coordinator in the sanctioned directory, not opened".
* **History entries written by the coordinator after the charter:** H1.8 (Campaign B's nominal forecast proxy) and
  H4.3b (the route-audit juxtaposition), from stream A's report.
* **Stream A0 tables** at all six non-target drifts, including the two drifts that bracket the quarantine band
  (11/10 and 27/10): certified relative slacks of the upper and lower bounds, and certification costs. No Λ value
  was read or written by the coordinator; the relative slacks are latent proxies for the tightness R-MB's order-0
  certificate will reach.
* **Stream ASSEMBLY, INDEP, INDEP_TUPLE, VERIFY reports:** decoy-only gain ratios, bracket widths, margins of
  non-target certificates.

**Statement required by C1(c).** Together with E1 (the committed tail thresholds, Monte-Carlo values and the C5
radius decomposition) and I-d (TPT-G's generic factors), the coordinator now holds every ingredient of an
incident-01-class estimator of R-MB's own outcome on cell 308 (order-0 tightness × committed thresholds; profile
transport factor × committed shares). **The coordinator has not formed that estimate, has written no such
combination, and will not.** No R-MB design decision after E1 depended on these ingredients: every parameter is fixed
by the dominance rule, inherited rules or non-target findings (audit a0 §4, a1 C1(a)).

## E1″. Addendum (2026-09-30; successor-governance review GC-6): observations of the MB308 r1 target run

This addendum names, and never values, what the coordinator and the reviewers observed about the one granted MB308 r1
evaluation (grant `afa93072`). The run was consumed, never sealed, and ended as CELL308_EXECUTION_INDETERMINATE. **No
target value was ever persisted, printed or read.** Every item below is a runtime or host observation: a latent
runtime proxy with no value content.

| observation | where recorded | who holds it |
|---|---|---|
| host readings at launch (thermal level, AC, lid, lowpowermode, load) | session transcript; recovery addendum A1 (g), labelled coordinator-reported | coordinator |
| the 23:10 JST read-only audit: process tree, worker start times and ages, per-worker CPU times, load average, thermal-pressure level | session transcript | coordinator |
| thermal-pressure level during the run | session transcript; REVIEW_EXECUTION_INTERRUPTION §4a/§4b; the execution review's disclosures | coordinator; reviewers reviewINT and reviewEXEC |
| per-coalition CPU of the run (powerlog) before and after 23:29, and the pool-load continuation | REVIEW_EXECUTION_INTERRUPTION §4b (quantitative); A1 and postexec (qualitative) | reviewINT; coordinator (read §4b); reviewEXEC; the adjudicator (reads the recovery chain) |
| host memory events in the window (ReportMemoryException, memory-pressure warning) | REVIEW_EXECUTION_INTERRUPTION §4b/N6; A1 (c) | reviewINT; coordinator; later readers of the chain |
| other applications active during the run | the execution review `a40211cc` | reviewEXEC; coordinator |

**Restrictions (successor-governance addendum A1, S13):**
* no successor brief contains these observations or points to REVIEW_EXECUTION_INTERRUPTION §4b;
* the successor's route, implementation and caps agents must not have seen them;
* the caps decision is justified from decoy and qualification evidence only.

**Disclosure.** The successor builder (brief 30, `8a4a02b4`) was launched before GC-6 existed. It was then told not to
read the recovery chain or the execution review, and to disclose any earlier reading in its BUILD_REPORT. The
successor route audit (`bddd85f8`) was written by the coordinator, who holds these observations. Its selection rests on
registry r2 and dominance, and uses none of them. The route review found no dependence on the lost run.
