# ADJUDICATION — C8, Operator-Information Feasibility and Route Selection

Adjudicator: independent, fresh context, no part in C8 and no part in the pre-publication review.
Worktree `/Users/suzhe/ReBaseGuard-k5c8`, branch `p5y-k5-tail-c8-operator-feasibility`,
HEAD `4e3696c0`. Gate blob on disk `55e743320987a1e0…`, frozen at `218cc314`, unchanged.

**The claim under test.** Commit `4e3696c0` states that the fresh-context review's three CRITICAL
findings are repaired. This adjudication tests that claim finding by finding against the committed
tree, not against the commit message.

## What I did

- Read `review/REVIEW_C8_PREPUBLICATION.md` in full, `README.md`, `config/DECISION_GATE_C8.json`,
  all eight modules in `code/`, and all six artifacts under `evidence/`.
- Read the predecessor material the repair depends on and the material it still does not read:
  `C2_ADJUDICATION.md` §K in full (I read the floor's own text, not C8's paraphrase),
  `C2_ADJUDICATION.md` conditions 1–7, `C4_ADJUDICATION.md` §6/§7/§8, `C4_CERTIFICATE.json`
  (including `cells/*/licence`), `OPEN_NOTES_DISPOSITION_C4.md`, `C5_FORECAST.json` in full
  (`c4_exclusion_fragility`, `binding_conditions_on_any_successor`, `clause_applied`),
  `c5_forecast.py` and `c5_transport.py` (the actual C5-T theorem, not its summary),
  `C6_CLASSIFICATION.json` routes A1/A3/E1/E2 and `RANKING_PREMISE_CORRECTED`,
  `ADJUDICATION_C7.md` §8 and its six conditions, `c2_d5_forecast.direct()`, `tct_rule.py`.
- **Ran all five runnable producers** (`c8_adoption.py`, `c8_routes.py`, `c8_decision.py`,
  `c8_mutations.py`, `c8_factcheck.py`) under `PYTHONINTMAXSTRDIGITS=0`. All five reproduce their
  committed artifacts **byte-for-byte**: `git status` was empty before and after. I did not run
  `c8_b0_audit.py` (it makes `git ls-remote` calls; see finding 14).
- Wrote five independent probes in the session scratchpad. They do **not** import any C8 module.
  They reimplement the sealed clause `c2_d5_forecast.direct()` from `ADOPTED_TAIL_INPUTS.json` +
  `tct_rule`, **including the mandatory independent `tail_enclosure_crosscheck`**, and — this is the
  test no previous reader performed — they reimplement **theorem C5-T itself** from
  `c5_transport.py` (`P = max((−H_lo)^+·w_R, (H_hi)^+·w_L)`) rather than accepting C8's scalar
  `M < M_needed_C5T` surrogate for it.
- No AWS, no Vultr, no SSH, no installs, no numpy/scipy/flint/mpmath/sympy/gmpy2, no state-changing
  git. I modified no file except this report. I authorized no execution and set no guard.

Where I write "measured" the number is from my own probe.

---

## Part 1 — did the repairs land?

### Summary table

| # | sev | finding | status | evidence |
|---|---|---|---|---|
| 1 | CRITICAL | 306 modelled against C2 §K's binding adoption floor | **PARTIAL** | science landed and is exactly right; the retracted sentence is still emitted by two producers; the repair **contravenes frozen gate rule 1**; only 1 of C2's 3 discharge routes carried |
| 2 | CRITICAL | route set incomplete; "R4 is the only route with leverage on 309" | **PARTIAL** | R5 added to README + a new side artifact and its figures are exact; the false claim survives **verbatim** in `C8_DECISION.json:76`; `phase9_frontier` still holds R1–R4; C4 §7.1/§7.3/§7.4 and C5's other five levers still unenumerated |
| 3 | CRITICAL | sealed `M_R2` clip implemented; conservativeness argument | **LANDED** | clip implemented from `cells[k]["m"]["5"]`; I reproduced 20/20 supplies (max 1.97e-17), C5's `M_used` (max 2.50e-16), and the saturation values exactly |
| 4 | MAJOR | zero-leverage "measured, not asserted" is a tautology | **NOT_LANDED** | `c8_routes.py:207-210` unchanged; ledger still string-compares `"ZERO"`; the **replacement** test is tautological too (demonstrated below) |
| 5 | MAJOR | "cheapest sufficient fact" contradicts Lemma Dv′ | **PARTIAL** | uniform-`eff` model is now primary and its four factors are exactly right; stale per-field rows remain, `why_307_first` still quotes 1.1203× and contradicts `selected_route` |
| 6 | MAJOR | C5's inherited condition on restating the 309 exclusion | **PARTIAL** | README now carries 2.0561597 % and 19.612136 %; `slack_percent_C5T = 0.944 %` still absent everywhere; `binding_conditions_on_any_successor` still read by no module; `cell_309_refutation_attribution` still carries no margin |
| 7 | MAJOR | "C4 did not decide 306/307/308" | **NOT_LANDED** | `c8_routes.py:244-247` unchanged; `README.md:56-57` region rewritten for other reasons but the contribution sentence was not corrected |
| 8 | MAJOR | mutation suite does not mutate; M05's literal `True` | **PARTIAL** | M05's literal replaced by a real comparison (`ceiling309 < floors[309]`); the four **new** mutants M19–M22 are field-presence checks over the artifact the same run wrote — the exact class the finding named; `README.md:121` still says "18" against 22 committed |
| 9 | MAJOR | E1 toolchain "read from committed pins" | **NOT_LANDED** | `README.md:105` and `phase8_toolchain.SOURCE` unchanged; tokens `N10`, `N9`, "reported, not recorded" appear nowhere in the namespace; FLINT 3.6.0 still unsourced; `producer_and_toolchain_known: true` unqualified |
| 10 | MINOR | quotes the retracted 4.5–4.9 % | **NOT_LANDED** | `README.md:94`, `c8_decision.py:162`, `C8_DECISION.json:165` unchanged |
| 11 | MINOR | host profiles collide; scope budgets forbidden work | **NOT_LANDED** | MINIMUM and RECOMMENDED both still 7.18 wall-h; 4×/16× still unsourced; scope still "all four", now including a cell C8 itself calls refuted |
| 12 | MINOR | `g_hi` **is** carried per-cell | **NOT_LANDED** | `c8_chain.py:29-35` unchanged. I recomputed `g_hi` both ways at all five cells: difference exactly **0** |
| 13 | MINOR | dead `self.M0`; an unperformed "verification" | **LANDED** | `M0` is now live and load-bearing; the false docstring sentence is gone; `verify()` now runs through the clipped `M_of` |
| 14 | MINOR | `REMOTE_HOSTS_CONTACTED: 0` vs `git ls-remote` | **NOT_LANDED** | three `ls-remote` call sites remain; no `VCS_REMOTE_QUERIES` field added |
| 15 | MINOR | "not from its summary ranges" implies a non-existent disagreement | **NOT_LANDED** | `README.md:12-13` unchanged |
| 16 | MINOR | fact-check regex sees only ≥4-decimal numerals; `backed()` unbound | **NOT_LANDED** | `c8_factcheck.py` untouched by the repair. **Regression:** committing the 522-line review widened the `review_sourced` escape hatch — any numeral the review mentions is now excused from `PROSE_FIGURE_UNBACKED` |
| 17 | MINOR | B0_04 shaped to the text | **NOT_LANDED** | `c8_b0_audit.py:56-63` unchanged |
| 18 | OBS | C6 vs C8 leverage figures unreconciled | **NOT_LANDED** | token "diagnostic Lambda" absent; C6's `E1.leverage_upper_bound` (+0.0468 at 309) still unreconciled with C8's +0.004661 |
| 19 | OBS | what the reviewer found clean | **re-verified** | see Part 2 |
| 20 | OBS | the 309 refutation holds on its stated scope | **re-verified, and strengthened** | I re-derived it under the **true** C5-T clause, which the reviewer did not |

Three LANDED, five PARTIAL, eleven NOT_LANDED, one observation re-verified.
**The claim "all three CRITICALs are now repaired" is false as stated: one landed, two landed in
part.**

### (a) CRITICAL 1 — cell 306 and the C2 §K adoption floor

I read `C2_ADJUDICATION.md` §K myself. The floor is exactly as the repair states it: a pair (m,k)
may be adopted only if the frozen K5-B certifies it **and at least one of** F1 (Γ < 0 also under a
registry-free Lemma G supply) or F2 (Γ < 0 at every atom constant ×1.25, i.e. uniform-A margin
≥ 1.25); condition 1 makes it prospective and binding.

**The science landed and is exactly right.** Measured through the sealed clause:

| cell | Γ now | uniform-A margin (C5-T) | F1: Γ under Lemma G | F2 | ×`eff` to close | ×`eff` to be adoptable |
|---|---|---|---|---|---|---|
| 306 | −0.036197780 | **1.171431** | **+0.019116** fail | fail | — | **1.067071** |
| 307 | +0.026354631 | — | +0.085118 fail | fail | 1.096007 | 1.370009 |
| 308 | +0.094564145 | — | +0.158343 fail | fail | 1.438423 | 1.798029 |
| 309 | +0.153019689 | — | +0.226117 fail | fail | 1.818354 | 2.272943 |

Every figure in `C8_ADOPTION.json` reproduces to the last digit I checked, and `+0.019116` is
bit-for-bit the number C2's adjudicator published for 306's F1 limb. 306 does fail both limbs and
does need 1.067071×. That part of the repair is real and I confirm it.

**Four things did not land.**

1. **The repair contravenes the frozen gate.** Gate rule 1 is not advisory: *"If a cell is already
   passing under committed certified supplies, its blocker is ADOPTION, not information. Route =
   GOVERNANCE, and no new information may be requested for it."* Cell 306 satisfies that predicate —
   it passes under committed certified supplies, under both clauses. The repaired campaign
   nonetheless requests information for 306 (`action_for_C9: "information, not a governance step"`)
   and makes it the **first target** of the selected route. The gate blob is unchanged, `gate_sha256`
   is still recorded, and `c8_decision.py:198` still reads "Phase 10: selection under the frozen
   gate". The deviation is *disclosed* (`CORRECTED_BY_REVIEW`, `SUPERSEDED_BY`) but it is not
   *governed*: no erratum, no amendment, no classification of the deviation. This is verbatim the
   shape C7's adjudicator made condition 1 — "do not leave the gate's text and the artifact's verdict
   in contradiction with nothing in the tree acknowledging it". The reviewer's remedy was *amend gate
   rule 1*; the campaign instead inverted its conclusion inside the artifact the rule governs. **A
   route-selection campaign's target is only as good as the frozen instrument it is derived from, and
   `306 first` is not derivable from this one.**
2. **The retracted sentence is still in the machine-readable evidence, twice.**
   `evidence/phase4/C8_ROUTES.json:182` — *"NONE — already passes under committed certified
   supplies; the blocker is ADOPTION, not information"*; `evidence/phase9/C8_DECISION.json:94` —
   *"The blocker is ADOPTION, not information."* Both are emitted live by `c8_routes.py:178` and
   `c8_decision.py:90-93`, neither of which the repair touched. A consumer reading the artifacts gets
   the retracted claim; a consumer reading the README gets the correction. That is precisely the
   failure mode C4's adjudicator named ("fixed in prose and left standing in the field a machine
   reads") and that C6's adjudicator named again for route A1.
3. **Only one of C2's three discharge routes is carried.** §K names three: a second independently
   written certifier closing **N9** (at which point a successor freezes a replacement floor
   requiring agreement between two certifier implementations *rather than F1*); deterministic
   tightening to margin ≥ 1.25; a real order-3 candidate (`Γ_perfect_order3(306) = −0.2175`). C4 §7.6
   repeats the first: *"306 needs the adoption floor addressed, **or a second independent
   certifier**"*. C8 carries only the second. The tokens `N9`, `N10` appear nowhere in the namespace.
   This matters materially: the N9 route has the *same* host prerequisite as R3 but a different
   deliverable, and it is not obviously more expensive than a 1.067071× tightening that C2 says
   a D′-class campaign will not deliver.
4. **The margin is the most favourable of three, unreconciled.** C8 reports 1.171431 (C5-T clause);
   C3_BLOCKER publishes `uniform_A_margin = 1.1554876238748288` (frozen clause) and `c8_chain.py`
   still drops that field; C2 §K's own application table gives 1.1277 for the adopted supply and
   quotes 1.1555 for the mixed one. The corresponding requirements are **1.067071 / 1.081806 /
   1.108452**. `README.md:52` prints 1.171431 in a table and `README.md:60` quotes "1.1555" nine
   lines below it with no reconciliation. Using C5-T is defensible — it is the authoritative clause —
   but C2 condition 1 says a successor wishing to replace the floor must freeze the replacement
   *before* recomputing any magnitude, and C8 has relaxed the floor's cost by 1.4 % post hoc without
   saying so. The verdict (fails F2) is robust under all three; the headline number is not.

Also unstated: 1.067071 is an **infimum**. At exactly that factor the uniform-A margin is exactly
1.25 and Γ = 0 at ×1.25, so F2's strict inequality fails. The same applies to 1.096007 / 1.438423 /
1.818354. This follows the predecessor's convention (`c2_d5_forecast.requirement`), so I do not treat
it as an error, but "needs a real 1.067071× tightening" should read "> 1.067071×".

### (b) CRITICAL 2 — route R5 and the exclusivity claim

**Landed.** R5 (source-sup norms = C6 route A1) is in `README.md`'s route table and has its own
block in `C8_ADOPTION.json`. Its figures are exact. Measured under the **true C5-T clause**, not
C8's surrogate:

- sup-norm cut voiding the 309 exclusion **at C4's floor: 2.056159703 %** — against
  `C5_FORECAST.json#/c4_exclusion_fragility/4_…/candidate_sup_norms_supF_supD_supH =
  2.0561597034092847`. Reproduced to nine decimals. The claim "reproduced here exactly" is true.
- **at the C7 PRIMARY floor: 19.612136317 %**. Also reproduced. The 9.5× robustness statement is
  sound (19.612/2.056 = 9.54).
- No cut voids anything at 306/307/308 (they are not excluded there), which the artifact records
  correctly as `excluded_at_*_floor: false`.

**Not landed.**

1. **The false claim is still in the tree, verbatim.** `evidence/phase9/C8_DECISION.json:76`:
   *"…and R4 is the only route with leverage on 309, so it is the successor to R3, not its rival"*,
   emitted live by `c8_decision.py:230`. The commit message says the claim "is false"; the producer
   still prints it. `c8_adoption.py` only *says* it was false, in a docstring.
2. **R5 is not in the route set that the selection reads.** `phase9_frontier` holds R1–R4 only;
   `phase5_perfect_information_oracles` holds R1–R4 only; gate rule 2 and rule 3 were evaluated over
   R1–R4 only. R5 exists in a side artifact and a README row. The frontier is the artifact a
   successor reads.
3. **R5's class is not one the frozen gate permits.** `classes_permitted` enumerates eight labels;
   `DATA_AND_TOOLCHAIN_BLOCKED` is not among them. A second, quieter deviation from the frozen gate.
4. **The class is also wrong on its merits.** C5 called A1 DATA-blocked; **C6 corrected that** and
   C8 reads C6 elsewhere. C6: *"for A1 and E1 the project is NOT missing data"*; A1 needs a
   certifying host that exists nowhere in scope, **a producer protocol permitting a non-identical
   sup, which does not exist and would itself need governance**, and an amount of slack in the
   certifier's own sup routine that C6 states is **not quantifiable** from committed evidence. C8
   carries the first half of C6's entry and omits the governance blocker and the non-quantifiability
   — the two facts that decide whether 19.6 % is reachable at all.
5. **The candidate set is still not the committed tree's.** The reviewer's remedy was to enumerate
   from the predecessors' own lists. C4 §7 names seven unexcluded deterministic mechanisms. C8 now
   covers #2 (as R5) and #7 (as R4). Still absent: **#1, residual-specific order-0 bounds** —
   *"escapes the floor entirely … the sharpest unexcluded mechanism and the one a successor should
   cost first"*, which by construction defeats the Λ-floor argument the 309 refutation rests on;
   #3, a smaller ρ at 309, "the largest single lever in the probe"; #4, tightening the TC-T assembly
   or the K5-B clause — which is exactly what C5-T itself did, i.e. a demonstrated-effective lever.
   C5's fragility field 4 lists five further quantified levers besides the sup norms
   (`env4_order4_envelope` 3.32 %, `f_G_order3_surrogate` 1.30 %, `sigma3` 3.24 %, `sigma4` 3.67 %,
   `all_four_together` 0.61 %); C8 evaluates none of them, although `all_four_together` at **0.608 %**
   is a *cheaper* requirement than the sup norms' 2.056 % at the same floor. A route-selection
   campaign that ranks by "smallest sufficient information requirement" has not seen the smallest one
   its own source publishes.

### (c) CRITICAL 3 — the sealed `M_R2` clip

**LANDED, and I verified every part of it independently.**

- `c8_chain.py:101-103` now reads `H` and `M_R2` from
  `ADOPTED_TAIL_INPUTS.json#/cells/k/m/5/{R2_interval,M_R2}`; I confirmed those keys exist
  (`['D_interval','M_R2','R2_interval','R_interval']`) and that the cell's *top-level* keys do not
  contain them, which is exactly the mistake the repair describes.
- `M_of` implements `M = M_R2 if a > b else min(M_R2, max(|a|,|b|))` — character-for-character the
  sealed `c2_d5_forecast.direct()` clip.
- **20/20 committed supplies reproduce** through my own reimplementation: max |ΔΓ| **1.97e-17**, max
  |Δmagnitude| 4.73e-16.
- **C5's `M_used` reproduces at all four cells**: max |ΔM| **2.50e-16**.
- **Saturation values reproduce exactly.** `g_hi + ρ·x_hi·M_R2` = **+0.288316809054** at 308 and
  **+0.374145054227** at 309, against `C4_CERTIFICATE.json#/cells/308/licence/Gamma_at_ladder_top
  = 0.2883168090540232` and `…/309/… = 0.374145054227244`. Both correct.
- I confirmed the clip **binds at none of the twenty committed supplies** and at none of the
  threshold points C8 reports, so finding 3's "impact on the reported numbers: none" still holds
  after the repair, as it must.

Three residual defects, none numeric:

- **308's saturation value exists only in the commit message.** The tree carries 309's
  (`C8_MUTATIONS.json:131`) and not 308's.
- **No cross-check against C4's published values.** The reviewer asked for the saturation to be
  added *as a reconstruction cross-check*. `gamma_saturation` is printed, never compared to
  `C4_CERTIFICATE`'s `Gamma_at_ladder_top`. M22's detection condition is
  `ch.M0[309] is not None and float(ch.gamma_saturation(309)) > 0` — it would pass for any positive
  number.
- **"The sealed clause is now implemented as written" is an overstatement.** `direct()` also runs
  `tail_enclosure_crosscheck` and **refuses** on disagreement; `c8_chain.enclosure` omits it
  entirely. I ran the crosscheck myself at all 20 committed supplies, at counterfactual `A`, and at
  scaled sup norms: it agrees everywhere, so nothing numeric rides on this — but the refusal that
  makes the sealed clause *sealed* is not in C8's copy of it.

### (d) is the zero-leverage claim still sound, and is its evidence now non-tautological?

**The claim is sound.** I checked it rather than accepting it. Γ = `g_hi + ρ·x_hi·M(A)`; `A` enters
only through the TC-T enclosure; Λ enters only through Lemma SM(d) as the admissibility floor on
`A0`. The gate itself fixes the one-sided reading — `admissibility_floor`: *"A certified **LOWER**
bound on E_a[τ] is therefore a FLOOR on any admissible A0"* — so R1-perfect and R2-perfect sharpen a
lower bound, and a lower bound can only shrink the admissible set. Zero closure leverage.
(C8 still never states this reading; it is derivable from the gate, so I do not hold it against the
result, but it should be one sentence in the README.)

**The evidence is still tautological.** `c8_routes.py:207-210` is untouched: three "different" Γ
values from one identical expression. `c8_factcheck.py:138` is untouched: the ledger entry
"R1 and R2 have exactly zero leverage" is still `routes[…]["R1"]["leverage"] == "ZERO"`, a string
comparison against the literal `c8_routes.py:218` wrote. And the **replacement** test is tautological
in the same way. `c8_adoption.py:153-159`:

```python
for name, fl in (("C4 floor", …), ("current floor", …), ("hypothetical floor 0", F(0)), …):
    Z = {"A0": fl, "A1": F(0), "A2": F(0)}
    verdicts[name] = {"Gamma_at_operator_supply": float(ch.gamma(k, A)),   # fl unused
                      ...}
gam_vals = {v["Gamma_at_operator_supply"] for v in verdicts.values()}
… "Gamma_invariant_across_four_floors": len(gam_vals) == 1
```

`fl` reaches `Z` and nothing else; `gamma(k, A)` takes no floor and is called with identical
arguments four times. I replayed this loop shape against a chain whose Γ **genuinely** depends on the
floor (`Γ = A0 + 1000·floor`) and it still reported
`Gamma_invariant_across_four_floors: True`. The field cannot be `False`; neither can
`exclusion_verdict_varies_with_floor`, since `M_of(k, Z)` is strictly monotone in `A0 = fl` and the
four floors are distinct. The only falsifiable new element is
`chain_module_reads_any_Lambda_artifact`, a three-token source grep. **A tautology was replaced by a
different tautology, in the campaign's own load-bearing negative, one campaign after C7's adjudicator
made this a binding condition.**

### (e) is the cell-309 refutation correctly scoped?

**Yes in the README and in `C8_ADOPTION.json`; no in the artifacts a machine reads.**
`cell_309_refutation_SCOPE` states the scope ("within the atom-constant family AT THE COMMITTED SUP
NORMS"), records `does_NOT_hold_unconditionally: true`, and classes it
`MATHEMATICALLY_REFUTED_WITHIN_SCOPE` with the escape recorded as BLOCKED, not refuted — which is the
distinction the gate exists to keep, and which `MATHEMATICALLY_REFUTED_requires` demands. I attacked
the refutation on its stated scope and could not break it; I re-derived it under the **true C5-T
clause** (which the reviewer did not — they used C8's `M < M_needed_C5T` surrogate):

| cell | A0 ceiling, true C5-T, A1=A2=0 | admissible floor | refuted |
|---|---|---|---|
| 306 | 8.631057819972 | 3.959880291 | no |
| 307 | 6.262333308183 | 3.734070431 | no |
| 308 | 4.442851487961 | 3.512733596 | no |
| 309 | **3.266415728267** | **3.586306094** | **yes** |

309's ceiling equals C5's published `critical_A0_C5T = 3.266415728267196` and all four equal C8's
`phase4_inversion_C5T` values exactly. **I further verified that C8's scalar surrogate is not merely
conservative but exactly equal to theorem C5-T at every point it reports**: at each threshold the
negative end of the signed enclosure dominates (`|H_lo| ≥ H_hi`) and the `M_R2` clip is inactive, so
`P = (−H_lo)^+·w_R = M·w_R` identically. I reproduced C5's own `Gamma_C5T` at all four cells to
≤2.8e-17. The arithmetic of this campaign is exact and I could not move a digit of it.

What is still missing: `MATHEMATICALLY_REFUTED` remains the unqualified verdict string in
`C8_ROUTES.json` and `C8_DECISION.json` (`operator_route_verdict`), the scope living only in the side
artifact; and C5's binding condition 2 is still only half-discharged (see finding 6 — the 0.944 %
figure that quantifies the very comparison C8's attribution paragraph leans on is nowhere in C8).

### (f) did the repairs introduce new defects?

Yes. Eight, beyond the unlanded parts above.

- **N1 (serious).** The selection now contravenes **frozen gate rule 1** while continuing to present
  itself as a selection under that gate. See (a).
- **N2.** `DATA_AND_TOOLCHAIN_BLOCKED` is not in the gate's `classes_permitted`.
- **N3.** `C8_DECISION.json` is now internally contradictory: `selected_route` says "targeted at cell
  306 first" while the adjacent `why_307_first` explains why 307 is first, using the superseded
  1.1203×; `rule_3…minimum_useful_improvement` is likewise still "A0 tightening of 1.1203x at cell
  307", and that field is what gate rule 3's realism test is applied to.
- **N4.** `C8_ADOPTION.json` carries **no `COUNTERFACTUAL` label at all**. The gate's compute
  boundary permits counterfactual calculation *"explicitly labelled COUNTERFACTUAL"*; every number in
  that artifact except the four `Gamma_now`/`M_now` values is a counterfactual. `C8_ROUTES.json`
  labels its oracle block; the new artifact does not.
- **N5.** The R5 sweep scales committed sup norms. C5 marks exactly this class of computation
  **DIAGNOSTIC** — *"DIAGNOSTIC for every scaled sweep (the independent TC-T crosscheck is aligned to
  the frozen path whenever an ingredient is scaled)"*. C8 records the two percentages with no status
  qualifier, and never runs the crosscheck at all.
- **N6.** Four new mutants of the class finding 8 condemned. M19–M22 read fields out of
  `C8_ADOPTION.json`, written by the same suite run; none perturbs an input or a code path. **M20 is
  the sharpest illustration: it reports DETECTED for "claiming a route is the ONLY one with leverage
  on cell 309" while that exact claim sits live in `C8_DECISION.json:76`.** The suite certifies the
  absence of a defect the tree contains.
- **N7.** `README.md:121` still advertises 18 mutants; the artifact has 22.
- **N8.** `C8_ADOPTION.json` is a RESULT artifact and is **not** in `c8_factcheck.py`'s gate-ordering
  list, so the ordering check no longer covers the tree it verifies. (Its first commit `4e3696c0` is
  in fact after the gate `218cc314`; the position is correct, merely unchecked.) Related: committing
  the 522-line review widened the `review_sourced` escape hatch in `backed()` — any prose numeral the
  review mentions is now exempt from `PROSE_FIGURE_UNBACKED`.

---

## Part 2 — what I re-verified and found clean

- **Reproducibility.** All five runnable producers regenerate their committed artifacts
  byte-for-byte; `git status` empty before and after.
- **Gate ordering and integrity.** Gate blob on disk hashes to `55e743320987a1e0…`, matching
  `GATE_SHA` in every producer; frozen at `218cc314`; every RESULT artifact's first commit is
  strictly later. The gate discloses its own non-blindness.
- **Chain arithmetic.** 20/20 supplies (1.97e-17), C5 `M_used` (2.50e-16), 309 ceiling equal to
  C5's `critical_A0_C5T`, C4's ladder-top saturation values at 308 and 309 exact, `g_hi` recovery
  identical to direct computation at all five cells, `Gamma_C5T` reproduced at all four cells.
- **Fidelity to C5-T.** C8's scalar-budget surrogate is *exactly* theorem C5-T at every point it
  reports (verified endpoint-dominance and clip-inactivity at each).
- **Compute boundary.** No numpy/scipy/flint/mpmath/sympy/gmpy2 import anywhere in `code/`; all
  arithmetic is `fractions.Fraction`; `toolchain_present()` uses `find_spec` and reports all six
  absent on this host, which I confirmed. No kernel evaluation, no operator certification, no AWS,
  no Vultr, no SSH. Guard DENY, `EXECUTION_AUTHORIZED` untouched, main not modified.
- **The open set.** `m=5` open = {306,307,308,309}, 305 PASS/adopted — correct.

---

## Part 3 — the fourteen questions

**1. What exact information is missing after C7?**
Not data. C6 established that the K1 candidate payloads never existed and that A1's and E1's inputs
are committed or exactly regenerable — "missing a toolchain" is true of the inputs and false of the
results. What is missing is a **certified result no campaign has ever computed**: a tighter certified
operator tuple (τ, D_lo, Ābar → `eff`, and D1, D2, C_T) for the tail cells. Quantified, as a single
uniform factor on `eff` under the authoritative C5-T clause, and stated as strict lower bounds:
306 **> 1.067071×** (to clear C2's adoption floor; it already closes), 307 **> 1.096007×** to close
and **> 1.370009×** to be adoptable, 308 **> 1.438423× / > 1.798029×**, 309 **> 1.818354× /
> 2.272943×** — the last unobtainable, because at A1 = A2 = 0 the clause tolerates A0 ≤ 3.266416
while Lemma SM(d) forces A0 ≥ 3.586306. Additionally missing, and not reducible to a factor: for 306,
an **independence** fact — a second, independently written certifier (C2 note N9), plus N10's
recording of the registry builder's own host and precision; for 309 outside the atom-constant family,
a **sup-norm tightening** of 19.612136 % at the current floor (2.056160 % at C4's); and for E2, a
theorem.

**2. Is R1 scientifically viable?** As science, yes — C4-N1 records a designed taboo-defect
inversion needing only the `sup_X` the frozen certifier already computes and discards. **As a closure
route, no: its perfect-information leverage is exactly zero**, because it sharpens a lower bound on
`E_a[τ]`, which the gate's own `admissibility_floor` clause makes a FLOOR on admissible `A0`, and Γ
does not depend on Λ. Gate `leverage_test` forbids selecting it as a closure route however cheap it
is. Its real value is that it *strengthens* exclusions — which is what C7 was.

**3. Is R2?** Same answer, same reason. R2 (cell uniformization, `sup_cell Λ(e) − Λ(e_lo)`) is sound
and also raises only the floor. Zero closure leverage.

**4. Is R3?** Yes. E1/operator certification is the only zero-new-real route with material closure
leverage on more than one open cell, its producer is committed
(`c1_tail_registry.py`, `c2_refined_registry.py`), and the programme has twice classified this work
as zero-new-real. Two qualifications C8 understates. Put in one currency — percentage reduction in
`eff` — 307 needs **8.760 %**, 308 needs **30.479 %** (306 needs 6.286 %, 309 needs 45.005 %), against
the **4.49–4.65 %** net `A0` gain C2 actually achieved when it refined the registry (per
`ERRATUM_C2.md`; not the 4.5–4.9 % C8 still quotes). That is **1.9× and 6.6×** the only refinement
this programme has ever measured — and C2 measured that refinement as **non-monotone** (τ regressed
1.90–2.24 % while `D_lo` improved). R3 is viable as the
next thing to attempt; it is not a thing to expect to succeed.

**5. Perfect-information leverage of each.**

| route | perfect-information leverage (measured) |
|---|---|
| R1 | **0.000000000** at every open cell; effect is to raise the floor, shrinking R3's room |
| R2 | **0.000000000**, same mechanism |
| R3 | A0 → Λ, A1 = A2 = 0: ceilings 8.631058 / 6.262333 / 4.442851 / 3.266416 vs floors 3.959880 / 3.734070 / 3.512734 / 3.586306 → makes 306 adoptable, closes 307 and 308, **cannot close 309** (floor exceeds ceiling by 9.79 %) |
| R4 | closes all four including 309 (Γ = −0.089759 at 309 with perfect order-3; C2 records Γ = −0.2175 at 306) |
| R5 | voids the 309 exclusion at a **2.056160 %** sup-norm cut against C4's floor, **19.612136 %** against C7's; C6's oracle (sup{F,D,H} → 0) closes 307, 308 and 309. Delivery-side slack **not quantifiable** from committed evidence |
| (unevaluated) | C4 §7.1 residual-specific order-0 bounds — escapes the Λ floor entirely, uncosted by anyone; C4 §7.3 smaller ρ at 309; C4 §7.4 TC-T/K5-B assembly; C5's `all_four_together` at **0.608 %**, a smaller requirement than R5's 2.056 % |

**6. Which route has the smallest sufficient information requirement?**
On the gate's tie-break as written, **306 via R3 at > 1.067071× on `eff`** — but frozen rule 1 bars
buying information for 306, so among gate-eligible targets it is **307 via R3 at > 1.096007×**.
Outside R1–R5, C5's `all_four_together` source-supply cut of **0.608 %** is a numerically smaller
requirement than anything C8 enumerates, and C8 does not evaluate it. The tie-break has therefore not
been applied to a complete set.

**7. Is any route analytically executable with zero toolchain?** **No.** R1 and R2 are the only
analytically executable ones and they buy exactly zero closure. R3, R4 and R5 all require Arb/FLINT
certification on a host that does not exist in scope. E2 is toolchain-free but is a theorem, and it
strengthens exclusions rather than closing cells.

**8. If not, is E1/operator certification justified?** **Yes, as the next route, and only as an
attempt.** It is the sole zero-new-real route with material leverage; gate rule 4 forbids new-real
while it is untested; it is cheapest on the gate's tie-break among eligible cells. The justification
is contingent on the historical-behaviour test in gate rule 3, and on the honest reading of that
history C8 does not give: C2's own refinement delivered 4.49–4.65 % where 307 needs an 8.760 %
reduction in `eff` and 308 needs 30.479 %, and it delivered it non-monotonically. For 306 specifically, E1 is **not** the only discharge — C2 §K's N9 route
(a second independently written certifier) is a different deliverable on the same host, and C8 never
weighs it.

**9. What exact toolchain/host would be sufficient?** A Linux x86_64 host with **numpy** and
**python-flint** (FLINT 3.x, which subsumes Arb) and at least 4 GB RAM; Python 3.12.x. **With the
caveat C8 omits**: `CELL_306_ADOPTION.md` prints exactly these values in a column headed *"reported,
not recorded"* and states that they are recorded in **no committed artifact** — that is open note
N10 — and "FLINT 3.6.0" has no source anywhere in this programme line. So the pins must be
**re-established by the provisioning step**, not read off. The cost anchor that *is* committed is
`REGISTRY_C2.json`'s `cpu_seconds_total` and the per-cell `arl.cpu_seconds`; C8's 10.76/43.06 CPU-h
extrapolations rest on unsourced 4×/16× work multipliers and on wall-hour figures that are internally
inconsistent (MINIMUM and RECOMMENDED both 7.18 h).

**10. Would provisioning that host be scientifically justified?** **Yes on the merits, and it is not
a campaign's decision to take.** Three of the five live routes (R3, R5, and the input half of R4) are
blocked on precisely this one thing, and no further analysis can unblock any of them — C6 established
that there is **no certifying host in scope at all** (local lacks all six libraries, which I
re-measured; vultr-02 re-measured read-only by C6; AWS forbidden), and that host provisioning is a
separately governed prerequisite requiring the user's decision. It should be put to the user as such,
with the honest risk stated: the dominant unknown is not CPU but whether a finer partition tightens
`eff` at all.

**11. Is any new-real campaign justified now?** **No.** Gate rule 4 forbids recommending new-real
while R3 remains untested; R4 is `NEW_REAL_BLOCKED`; C4 §8 holds the R-stage premise unavailable and
C2 condition 3 holds N7 undischarged. Guard stays DENY.

**12. Is broader deterministic exhaustion established?** **No.** C5's binding condition 3 is
explicit: the exhaustion result is of the **transport family only** and may never be restated as
deterministic exhaustion of cell 309, of the tail, or of K5. C4 §7 still names seven unexcluded
deterministic mechanisms, of which C8 evaluates two. C8's README says "not established", which is
correct.

**13. Is the R-stage prerequisite satisfied?** **No.** C4 §8: one cell of four, in the narrowest of
the available channels, is not exhaustion of the deterministic direction; 307's blocker is not `A0`
at all; 308's own deterministic path is unattempted; 306's blocker is an adoption floor no order-3
computation addresses. C8 says so and sets `R_stage: NOT AUTHORIZED`. I concur and I authorize
nothing.

**14. What should C9 do — exactly ONE primary route.**

> **`NEXT_ROUTE_OPERATOR_CERT` — R3 / E1 operator certification, zero-new-real, first target cell
> 307 at a uniform `eff` tightening of > 1.096007×, then cell 308 at > 1.438423×.**

This is the outcome the frozen gate yields and I confirm it. The **target** differs from C8's:
under frozen rule 1 cell 306 is routed to GOVERNANCE and no new information may be requested for it,
so `306 first` is not a selection this gate can produce. If — and only if — governance amends rule 1
to test the inherited C2 §K adoption floor rather than mere passing, and re-freezes it, then 306
becomes the cheaper first target at > 1.067071× and C9 should take it. That amendment is warranted on
the merits; making it is not a campaign's act.
C9 must additionally, before spending anything: put host provisioning to the user as a separately
governed prerequisite; complete the route enumeration from C4 §7.1/§7.3/§7.4, C5 fragility field 4
and C6's route table, and re-run the gate's rule 2 and tie-break over that set; and weigh C2's N9
route (a second independently written certifier) against the 1.067071× tightening for cell 306.
C9 must not execute R3, must not authorize the R-stage, and must not set guard ALLOW.

---

## Conditions

Blocking before this campaign is published or C9 is chartered:

1. **Restore gate compliance.** Either restate the selected target as cell 307 under frozen rule 1,
   or record a governed amendment to rule 1 (frozen and hashed, in the form the programme uses for
   errata) and re-select. Do not leave the gate's text and the artifact's action in contradiction.
2. **Make the producers emit the repaired claims.** `c8_routes.py:178`, `c8_decision.py:90-93` and
   `c8_decision.py:230` still write the two retracted CRITICAL claims into `C8_ROUTES.json` and
   `C8_DECISION.json`. Regenerate both artifacts. A repair recorded only in the README is the failure
   mode this programme convened adjudication to catch.
3. **Put R5 in the route set**, with a class the gate permits, and carry C6's two corrections: A1 is
   not a data problem, and its delivery-side slack is not quantifiable.

Non-blocking but required of the successor:

4. Replace the zero-leverage evidence with a test that can fail (perturb the chain, or state the
   structural lemma as a lemma and delete "measured"), and replace the ledger's string comparison.
5. Enumerate and classify C4 §7.1, §7.3, §7.4 and C5 fragility field 4's other five levers; re-run
   rule 2 and the tie-break over the full set.
6. Carry C2 §K's other two discharge routes for 306 (N9 second certifier; real order-3), and
   reconcile the three published margins (1.1277 / 1.1554876 / 1.171431) and their three
   requirements (1.108452 / 1.081806 / 1.067071), naming the clause each belongs to.
7. Discharge C5's `binding_conditions_on_any_successor` explicitly; add `slack_percent_C5T = 0.944 %`
   and the 9.79 % C7-floor margin to `cell_309_refutation_attribution`.
8. Label every counterfactual in `C8_ADOPTION.json`, and mark the scaled-sup sweep DIAGNOSTIC per C5.
9. Convert M19–M22 into real mutants; cross-check `gamma_saturation` against
   `C4_CERTIFICATE.json#/cells/*/licence/Gamma_at_ladder_top`; correct the README's mutant count.
10. Correct the state numbers findings 9, 10, 11, 12, 14, 15, 16, 17 name — none moves a digit, and
    all of them were already written down once.
11. Add `C8_ADOPTION.json` to the gate-ordering check, and state the strict-inequality reading of the
    four `eff` factors.
12. Import `c2_d5_forecast.direct` or reinstate its `tail_enclosure_crosscheck` refusal before any
    successor drives this chain at a new supply.

None of these bears on the validity of the arithmetic. I reproduced every load-bearing number in this
campaign independently, including theorem C5-T itself, and could not move one digit.

ACCEPTED_WITH_CONDITIONS
