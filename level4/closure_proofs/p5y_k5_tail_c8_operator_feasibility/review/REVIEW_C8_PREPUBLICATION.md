# C8 — hostile fresh-context pre-publication review

Reviewer: independent, fresh context, no part in C8. Worktree `/Users/suzhe/ReBaseGuard-k5c8`,
branch `p5y-k5-tail-c8-operator-feasibility`, HEAD `f0196012`.

## What I did

- Read `review/HANDOVER_C8_REVIEW.md`, `README.md`, `config/DECISION_GATE_C8.json` and all seven
  modules in `code/`, then all five artifacts under `evidence/`.
- Read the predecessor material C8 draws on **and the predecessor material C8 does not read**:
  `p5y_k5_tail_c2_closure/evidence/adjudication/C2_ADJUDICATION.md`,
  `p5y_k5_tail_c4_exhaustion/evidence/adjudication/C4_ADJUDICATION.md`,
  `C4_CERTIFICATE.json`, `C5_FORECAST.json`, `C6_CLASSIFICATION.json`,
  `p5y_k5_tail_c7_e2_lambda309/review/ADJUDICATION_C7.md`, `K5_COVERAGE_MAP_R5.json`,
  `ERRATUM_C2.md`, `phase_d/D_STAGE_DECISION.md`, `phase_d/CELL_306_ADOPTION.md`.
- **Ran all four runnable producers** (`c8_routes.py`, `c8_decision.py`, `c8_mutations.py`,
  `c8_factcheck.py`) under `PYTHONINTMAXSTRDIGITS=0`. All four reproduce their committed artifacts
  **byte-for-byte** (`git status` clean afterwards; I also diffed against a pre-run backup). I did
  not run `c8_b0_audit.py` because it issues network `git ls-remote` calls (see finding 14).
- Wrote four independent probes in the session scratchpad, which reimplement the **sealed** clause
  `c2_d5_forecast.direct()` and drive it over the committed tail inputs.
- No AWS, no Vultr, no SSH, no installs, no numpy/scipy/flint/mpmath/sympy/gmpy2, no state-changing
  git. I modified no file except this report.

Where I write "measured" below, the number came from my own probe through the sealed clause, not
from a C8 artifact.

---

## CRITICAL

### 1. Cell 306's blocker is **not** adoption. C8 contradicts the binding adoption floor that governs it.

**Where.** `README.md:47`, `README.md:59-61`; `code/c8_decision.py:90-93` and `:205-210`;
`evidence/phase9/C8_DECISION.json#/phase10_selection/rule_1_adoption_first`;
`config/DECISION_GATE_C8.json:47` (decision rule 1).

**What is wrong.** `C2_ADJUDICATION.md` §K sets a **prospective, binding** floor:

> **K5 tail adoption floor (r1)** … A pair (m, k) may be adopted only if the frozen K5-B certifies it
> **and at least one of**: **F1 — supply independence** (Γ < 0 also under Lemma G from `C_upper`,
> i.e. without the Arb/FLINT registry) … **F2 — degradation survival** (Γ < 0 at every atom constant
> × 1.25, i.e. uniform-A margin ≥ 1.25).

and its condition 1 states "The floor above is now the standard for K5 m = 5 tail adoptions,
prospectively." Cell 306 **fails both limbs**. I recomputed them through the sealed clause:

| limb | frozen K5-B clause | authoritative C5-T clause |
|---|---|---|
| F1 (Lemma G supply `G`) | Γ = **+0.019115585** → fails | M = **4.151682079** > budget 3.952942541 → fails |
| F2 (mixed supply × 1.25) | Γ = **+0.022002640** → fails | M = **4.188930420** > budget → fails |
| uniform-A margin | 1.1554876 (published in `C3_BLOCKER.json`) | **1.171431** (measured) — floor requires ≥ 1.25 |

Worse, the C2 adjudicator anticipated C8's exact claim and its exact number in advance:

> "Under the mixed supply, cell 306 improves to Γ = −0.036198 with a uniform-A margin of 1.1555 —
> better, but still short of F2 — so I should be plain that a D′ campaign **alone will not discharge
> this floor for cell 306**."

`−0.036198` is C8's own `Gamma_now` for 306 (`−0.036197779964579395`). The adjudicator then names
what *would* discharge it: a second independently written certifier (closing N9), **or** further
deterministic tightening to uniform-A margin ≥ 1.25, **or** a real order-3 candidate. All three are
**information**. C4's adjudicator says the same at §6/§7.6: "306 needs the adoption floor addressed,
**or a second independent certifier**."

C8 therefore ships the opposite of the governing verdict: "the blocker is **adoption**, not
information", "No new science should be bought for it", `action_for_C9: "a governance adoption step,
not a science campaign"`.

Three aggravating facts:

- C8 never opens `C2_ADJUDICATION.md`. `grep -i "adoption floor|F1|F2|1\.25|degrad|N9"` over the
  whole C8 namespace returns nothing.
- The decisive number is in a file C8 **does** read: `C3_BLOCKER.json` carries
  `per_supply.operator_mixed.uniform_A_margin = 1.1554876238748288`, and
  `code/c8_chain.py:135-141` (`committed_supplies`) explicitly enumerates the fields it keeps and
  **drops `uniform_A_margin`**.
- Gate rule 1 (`DECISION_GATE_C8.json:47`) is itself defective: it equates "passing under committed
  certified supplies" with "blocker is adoption" and contains no adoption-floor term, so applying it
  mechanically was guaranteed to produce this result.

**To fix.** Amend gate rule 1 to test the inherited adoption floor, not merely Γ < 0; recompute F1
and F2 for every cell claimed to be adoption-blocked; restate 306 as *passing the clause but failing
the F1/F2 floor*, with the three discharge routes C2 names; withdraw "no new science should be bought
for it" and the `rule_1_adoption_first` action. This also removes 306 from the "cheapest result in
the tail" framing entirely.

---

### 2. The route enumeration is incomplete, and "R4 is the only route with leverage on 309" is false against C8's own tree.

**Where.** `README.md:68`; `config/DECISION_GATE_C8.json:28-33` (`route_definitions`);
`evidence/phase4/C8_ROUTES.json#/phase5_perfect_information_oracles/routes` (R1–R4 only);
`evidence/phase9/C8_DECISION.json#/phase9_frontier`.

**What is wrong.** C8 invents its own four-route universe {R1 clipping, R2 uniformization, R3
operator certification, R4 order-3} and then selects from it. The committed tree already enumerates
more, and at least two of the missing ones bear on 309:

- `C4_ADJUDICATION.md` §7 names **seven** unexcluded deterministic mechanisms. #1 is
  *residual-specific order-0 bounds*: "SM(d) is sharp only at `f = 1`. Replacing `A0‖φ_H‖` by
  `(Ĝ|φ_H|)(a)/D_e` … sits legitimately below `E_a[τ]·‖φ‖` and **escapes the floor entirely**. …
  This is the sharpest unexcluded mechanism and the one a successor should cost first." That is a
  route which by construction defeats the Λ-floor argument C8's 309 refutation is built on, and C8
  neither costs it nor mentions it.
- `C5_FORECAST.json#/c4_exclusion_fragility/5_can_a_tighter_transport_void_it` states that a
  **2.0562 %** tightening of the candidate sup norms `sup{F,D,H}` "is comfortably reachable by an
  ENCLOSURE improvement … route A1 which would deliver exactly that is **DATA-blocked, not
  refuted**", i.e. it would **void the cell-309 exclusion**. C8 does not evaluate it.
- Also unconsidered: C4 §7.3 (a smaller ρ at 309, "the largest single lever in the probe"), §7.4
  (tightening the TC-T assembly or the K5-B clause — which is exactly what C5-T itself did), and
  C4-N1's designed-but-unrun R1 taboo-defect inversion and R5 two-sided `τ_a` certificate.

Because gate rule 2 ("prefer a sound ZERO-NEW-REAL analytic route if it achieves a material fraction
of the required improvement on at least one open cell") was tested against R1 and R2 only, the
`NEXT_ROUTE_OPERATOR_CERT` outcome is drawn from a candidate set that is demonstrably not the
committed tree's. A route-selection campaign whose candidate set is incomplete has not selected.

**To fix.** Enumerate routes from the predecessors' own published lists (C4 §7.1–§7.7, C4-N1,
C5 `c4_exclusion_fragility` field 4, C6's route table) rather than de novo; classify each against the
gate; re-run rule 2 and rule 3 over the full set. Withdraw README:68's exclusivity claim outright —
it is contradicted by `C5_FORECAST.json`, which C8 reads in three modules.

---

### 3. "M = magnitude": the clip is **reachable**, and dropping it is **not** conservative outside a neighbourhood of the certified supply.

**Where.** `code/c8_chain.py:104-121` (docstring of `M_of`), `code/c8_routes.py:75-80` (the DAG node
for `M`).

Both halves of the justification fail.

**(a) "Neither that interval nor `M_R2` is carried in any committed artifact, so the clip is
UNREACHABLE."** False. Both are carried per-cell, for m = 5, in
`p5y_k5_m5_tail_closure/evidence/measurement_r1/ADOPTED_TAIL_INPUTS.json` — **the same file
`c8_chain.py:66` opens**, two keys away from the `C_upper` and `auxiliary_evidence` it does read:

```
cells["309"]["m"]["5"] keys: ['D_interval', 'M_R2', 'R2_interval', 'R_interval']
    M_R2 = 5.269941292129297      R2_interval = [-5.269941292129297, 5.096959807552557]
```

The sealed clause is ten lines, `p5y_k5_tail_c2_closure/code/c2_d5_forecast.py:79-89`:

```python
H  = (F(ad["R2_interval"]["lo"]), F(ad["R2_interval"]["hi"]))
M0 = F(ad["M_R2"])
a, b = max(H[0], lo), min(H[1], hi)
M  = M0 if a > b else min(M0, max(abs(a), abs(b)))
```

`p5y_k5_tail_c3_closure/code/c3_blocker.py:77` calls that exact function, and
`p5y_k5_tail_operator_registry/code/c1_forecast.py:217-224` reimplements it. Two predecessors reach
the clip from committed evidence; C8 declares it unreachable.

C8 **is** right that `H_exact` / `H_tail_exact` in `C2_D5_FORECAST` is the TC-T enclosure and not the
R2 interval (confirmed at `tail_forecast_r2.py:158`, `audit[k]["H_tail"] = [str(lo), str(hi)]`). The
error is the inference from that to unreachability.

**(b) "Clipping can only DECREASE M … Gamma computed here is an upper bound on the sealed Gamma …
a threshold derived here is at least as demanding as the true one."** False beyond ≈ 2× the certified
supply. Measured, driving both clauses over a uniform scale on the mixed supply:

| cell | scale 1 (mag / sealed M) | scale 2 | scale 16 | scale 64 |
|---|---|---|---|---|
| 306 | 3.438037 / 3.438037 | 6.441609 / **5.427005** | 48.49 / **5.427005** | 192.66 / **5.427005** |
| 307 | 3.374599 / 3.374599 | 6.338590 / **5.335184** | 47.83 / **5.335184** | 190.11 / **5.335184** |
| 308 | 3.371647 / 3.371647 | 6.349840 / **5.296077** | 48.04 / **5.296077** | 191.00 / **5.296077** |
| 309 | 3.319525 / 3.319525 | 6.261082 / **5.269941** | 47.44 / **5.269941** | 188.64 / **5.269941** |

The sealed M saturates at `M_R2`; C8's M grows without bound. Above the clip point C8's Γ **exceeds**
the sealed Γ, so the stated direction reverses. This is not hypothetical: C4's own
`OPEN_NOTES_DISPOSITION_C4.md` item (g) records running the ladder to 10⁵ × the certified A0 with Γ
"saturating at **+0.288317** (308) and **+0.374145** (309)". I reproduced both exactly as
`g_hi + ρ·x_hi·M_R2` (308: −0.244895 + 0.0507486·1.9839101·5.296077 = +0.288317). C8's reconstruction
is structurally incapable of reproducing those two published numbers, and it never tries.

**Impact on the reported numbers: none.** Every threshold C8 reports is defined at M ≈ 2.0–3.95, well
below `M_R2` ≈ 5.27–5.43, and I verified the clip is inactive at all twenty committed supplies
(`M_sealed == max(|lo|,|hi|)` exactly, and the intersection is non-empty, at every one). So this is a
**justification** defect, not a numeric one — but the justification is load-bearing for every
counterfactual in the campaign, and both halves of it are wrong.

**To fix.** Delete the unreachability claim; import `c2_d5_forecast.direct` (as C3 does) or
reimplement the four-line clip from `ADOPTED_TAIL_INPUTS.json`; re-derive every ceiling through the
sealed clause; add C4's saturation values +0.288317 / +0.374145 as a reconstruction cross-check.

---

## MAJOR

### 4. The zero-leverage result for R1/R2 is asserted by construction. "Measured, not asserted" is false.

**Where.** `README.md:37-38`; `code/c8_routes.py:205-222`; `code/c8_factcheck.py:134-139`.

`c8_routes.py:207-210` computes the three quantities from the *identical expression*:

```python
r12[str(k)] = {"Gamma_now":                 float(ch.gamma(k, A)),
               "Gamma_with_Delta_clip_zero":float(ch.gamma(k, A)),
               "Gamma_with_Delta_cell_zero":float(ch.gamma(k, A)),
               "delta": 0.0}
```

and `:220` makes R2 a `dict()` copy of R1. `README.md:37-38` then reports "Measured, not asserted:
perfect information in either changes Γ by exactly **0.000000000** at every open cell." Nothing was
measured; a constant was printed three times. The fact-check ledger "verifies" the claim at
`c8_factcheck.py:138` by testing `routes[...]["R1"]["leverage"] == "ZERO"` — a string comparison
against the literal `c8_routes.py:218` wrote. In a campaign whose own mutant M16 is titled "a B0
check implemented as a tautology", this is the load-bearing negative of the whole campaign.

**The underlying argument is nevertheless sound**, and I checked it rather than taking it: Γ is
`g_hi + ρ·x_hi·M(A)`, A enters only through the TC-T enclosure (`tct_rule.py:196-208`), and Λ enters
only as an admissibility floor. `C4_ADJUDICATION.md:59-61` confirms the reading —
"§3 Lemma SM(d) states `sup_{‖f‖≤1}|[(I−K_e)⁻¹f](a)| = τ_a/D_e = E_a[τ]`, attained at `f = 1`. So
admissibility is *equivalent* to `A0 ≥ sup_cell E_a[τ] = Λ_k`". I looked hard for a path by which
better Λ lowers Γ and did not find one **under C8's reading of "perfect information"**: R1-perfect
(Δ_clip = 0) and R2-perfect (sup = endpoint) both sharpen a *lower* bound, and a lower bound can
never license a smaller A0. The gate's `leverage_test` does not define whether "perfect information
within a route" is one-sided or two-sided, and C8 silently takes the reading that makes R1/R2 zero.
That choice should be stated, because under the two-sided reading (exact knowledge of `sup_cell
E_a[τ]`) R1+R2 collapse into the R3 oracle and close 307 and 308.

**To fix.** Either make the oracle a real perturbation (evaluate Γ at the Λ-improved floor and show
the admissible set only shrinks) or delete the "measured" framing and present the structural lemma as
a lemma. Replace the ledger entry with a check that can fail. State the one-sided reading explicitly
in the gate.

### 5. The "cheapest sufficient fact" model contradicts Lemma Dv′, overstating two of three requirements and inventing a second fact for 308.

**Where.** `README.md:48-49`, `README.md:75-76`; `code/c8_routes.py:159-199`;
`code/c8_decision.py:69-105`; `config/DECISION_GATE_C8.json:24` and `:55`.

The gate states the physics: "`A1`, `A2` are `eff` times fixed multipliers, so all three are
**PROPORTIONAL to eff**", and `c8_chain.py:27` repeats it. The inversion then moves one field with
the other two frozen — a tuple no certifier can deliver. Measured through the sealed clause against
the C5-T budget:

| cell | C8's reported requirement | true uniform-`eff` requirement (measured) |
|---|---|---|
| 307 | `A0` 5.597996 → 4.996766, **1.1203×** | **1.096007×** |
| 308 | `A0` → floor **and** `A1` ≤ 17.632791 (1.2927×) | **1.438423×** on `eff`, one quantity |
| 309 | refuted | 1.818354× — still above what any admissible `eff` permits |

For **308** this is a substantive error, not a rounding one: scaling `eff` to its floor is a
1.485609× tightening, which carries `A1` to 22.793744/1.485609 = 15.34 ≤ 17.63 **automatically**. I
verified directly that `eff` at the floor closes 308 under both the sealed frozen clause and the
C5-T clause. C8 reports 308 as needing two independent facts when its own model says it needs one.

For **307**, `README.md:75-76`'s headline — "A `1.1203×` tightening of a single quantity is the
smallest sufficient information requirement anywhere in the tail" — is not the smallest even within
C8's own evidence: `C8_ROUTES.json#/phase4.../307/uniform_reduction_required` already carries
**1.1119662371370418**, which is also `C4_ADJUDICATION.md` §6's published "1.111966× uniform". The
gate's own tie-break says "the required improvement factor on the single quantity that must change",
and under Dv′ that quantity is `eff`.

The **route decision survives** (R3, 307 first: 1.0960 < 1.4384 < 1.8184). The quoted figures do not.

**To fix.** Make the inversion scale `(A0, A1, A2)` together as Dv′ requires, report the uniform-`eff`
factor as the primary requirement, keep the single-field factors as a labelled sensitivity, and
correct the 308 row and the README headline.

### 6. C5's inherited binding condition on restating the cell-309 exclusion is not discharged.

**Where.** `README.md:52-55`; `code/c8_decision.py:238-253`;
`evidence/phase9/C8_DECISION.json#/cell_309_refutation_attribution`.

`C5_FORECAST.json#/binding_conditions_on_any_successor` says, of itself, "A ranking can be ignored;
this is a **condition** and it **inherits**":

> 2. C4's verdict is scoped verbatim to "the frozen … K5-B direct clause". C5-T **REPLACES** that
>    clause. Any restatement must name the C5-T clause and **carry the margins in
>    `c4_exclusion_fragility`, not C4's 2.58 %**.

C8 restates the exclusion. It names the C5-T clause (good). It then goes back to C4's floor for its
attribution paragraph — "The refutation already held under C4's weaker floor 3.297250" — and carries
**no margin at all**. The margin C5 computed for exactly that comparison is
`slack_percent_C5T = 0.9439874105892017`, against C4's published 2.582705758256717, with C5's own
note "C4 published 2.58 %; under C5-T it is under 1 %". So the comparison C8 leans on has **0.94 %**
of slack, and the campaign's emitted `cell_309_refutation_attribution` block reports
`refuted_under_C4_floor: true` and `C7_raised_floor_by` without a single margin figure. The token
"fragility" appears nowhere in C8, and no module reads `binding_conditions_on_any_successor`.

**To fix.** Read and discharge C5's three inherited conditions explicitly; add
`slack_percent_C5T = 0.944 %` (C4 floor) and 9.79 % (C7 PRIMARY floor) to the attribution block and
to `README.md:52-57`.

### 7. "C4 did not decide" cells 306, 307, 308 — it did, and it published the same numbers.

**Where.** `README.md:56-57`; `code/c8_routes.py:244-247`.

`C4_CERTIFICATE.json` decides all four:

- 306 and 307: `excluded: false`, `critical_A0_reported_only: null`, with
  `outside_the_count: "the cell already closes at A1 = A2 = 0 with A0 exactly as certified"`;
- 308: `blocker_is_A0: true`, `critical_A0_reported_only: 4.375228833135616` — **bit-identical** to
  C8's `A0_ceiling_with_A1_A2_zero` for 308;
- 309: `excluded: true`, `critical_A0_reported_only: 3.2142360226778806` — which C8 does credit.

C4's `Gamma_at_bound` values (−0.14388116320706978 / −0.09298528787328704 / −0.04046754262884166 /
+0.004661129657978107) are **exactly** C8's `Gamma_at_A0_floor_A1_A2_zero` for all four cells.
`C4_ADJUDICATION.md` §6 additionally publishes 307's targets ("2.203053× reduction of `(A1, A2)` with
`A0` unchanged, or a 1.111966× uniform reduction") and §7.5 publishes 308's, and `C5_FORECAST.json`
already records `closed: [306]`, `still_open: [307, 308, 309]`. C8's genuinely new numbers are the
306/307 A0 ceilings (8.513589 / 6.172456) and the C5-T-budget versions of all of them. The
contribution sentence should say that and stop.

### 8. The mutation suite does not mutate; one mutant's detection flag is the literal `True`.

**Where.** `code/c8_mutations.py`; `README.md:106`.

- **`c8_mutations.py:73-82` (M05)** computes `bad` at line 75, **never uses it**, and passes the
  literal `True` as the `detected` argument at line 77. This is the precise defect C7's adjudicator
  made a binding condition — `ADJUDICATION_C7.md:257` and condition 4, "replace `chk(15)`'s literal
  `True`" — reproduced one campaign later, in a suite whose sibling mutant M16 is titled "a B0 check
  implemented as a tautology" and whose `README.md:108` advertises "no tautologies".
- M03, M07, M10, M11, M12, M13 and M18 are **string- or field-presence checks over artifacts the
  campaign itself wrote**. M18's detection test is `(C.NS / "code" / "c8_factcheck.py").exists()`.
  These cannot fail unless C8 edits its own prose.
- Only **M04, M08, M15, M17** perform a computation with a genuine chance of failing.

"18 planted bad decisions" (`README.md:106`) overstates by roughly 4×. Compare
`p5y_k5_tail_operator_registry/code/c1_mutations.py:182`, which actually mutates a committed input
(`M_R2 / 2`) and re-runs the chain. Nothing in C8's suite perturbs an input or a code path.

**To fix.** Replace M05's literal with the computed `bad`; convert the presence checks into real
mutants (perturb the artifact or monkey-patch the chain and assert the guard fires); restate the
count as the number of mutants that can fail.

### 9. The E1 toolchain is not "read from committed pins" — its source says it is recorded nowhere.

**Where.** `README.md:90-93`; `code/c8_decision.py:112-134`;
`evidence/phase9/C8_DECISION.json#/phase8_toolchain/SOURCE`
("version pins read from committed evidence; nothing was installed or queried");
`#/phase10_selection/rule_3_operator_certification/producer_and_toolchain_known: true`.

`p5y_k5_tail_c2_closure/phase_d/CELL_306_ADOPTION.md:33-40` gives exactly C8's three values (Python
3.12.3, numpy 2.5.2, python-flint 0.9.0, Linux x86_64) in a column headed "the worker that built the
registry — **reported, not recorded**", and states in bold immediately below: "The left column is
reported by this campaign and **is recorded in no committed artifact** … `REGISTRY_C2.json` carries
no host, toolchain or precision field". That is open note N10. The fourth value, **FLINT 3.6.0**, is
not in that table at all; its only occurrence in the tree is
`p5y_k1_sr_cap_authorized_successor/PROTOCOL.md:81`, a different programme line (SR cap, not the
CUSUM operator registry), and C8 cites no source for it.

Gate rule 3 conditions the selection of R3 on "the exact producer/toolchain is **known**". The
producer is genuinely committed (`p5y_k5_tail_operator_registry/code/c1_tail_registry.py`,
`p5y_k5_tail_c2_closure/code/c2_refined_registry.py`), so the producer half stands; the toolchain
half rests on unrecorded self-report that the source flags against its own interest.

**To fix.** Relabel the version block `REPORTED_NOT_RECORDED (C2 open note N10)`, cite
`CELL_306_ADOPTION.md` and the N9/N10 notes, drop or source FLINT 3.6.0, and either qualify
`producer_and_toolchain_known` or state that provisioning must re-establish the toolchain
independently.

---

## MINOR

### 10. The README quotes a figure its own source retracted, in the same sentence as the correction that replaced it.

`README.md:78-80` and `code/c8_decision.py:161-163`: "τ got **1.90–2.24 %** worse, and the net `A0`
gain was only **4.5–4.9 %**." `ERRATUM_C2.md:161` tightened both at once: "τ regressed by 1.90–2.24 %
(not '2–3 %'); the A0 gain is **4.49–4.65 %** of C1's value, or 4.71–4.88 % as C1/C2 − 1." And
`phase_d/D_STAGE_DECISION.md:44` says explicitly: "(The earlier '2–3 %' and **'4.5–4.9 %'** were
loose rather than wrong; tightened after the pre-freeze review.)" C8 took the corrected half of the
erratum row and the superseded half. Fix: quote 4.49–4.65 % (or 4.71–4.88 % with its basis named).

### 11. The host profiles still collide, and two of them budget work the campaign forbids or declares impossible.

`code/c8_decision.py:136-165`; `README.md:84-88`. The comment at `:136-139` says the first version
scaled the work allowance with core count so RECOMMENDED and FAST reported identical wall time, and
that this is fixed. It is not fixed, it is displaced: `SCOPE` gives 4× work / 2 cores and 16× work /
8 cores, the same ratio, so **MINIMUM and RECOMMENDED now both report 7.18 wall-h**. Separately,
RECOMMENDED and FAST scope "all four open cells", i.e. they budget operator certification for 306
(which gate rule 1 forbids buying information for) and 309 (declared MATHEMATICALLY_REFUTED), and
`phase9_frontier.R3.cpu_hours` quotes that scope as R3's headline cost. The multipliers 4× and 16×
have no source anywhere in the tree.

### 12. `g_hi` **is** carried per-cell in a single committed artifact.

`code/c8_chain.py:30-35`: "`g_hi` is not carried per-cell in any single committed artifact, so it is
recovered exactly from the committed pair `(Gamma_exact, M_after_exact)`". All three of its
components — `R_interval.hi`, `D_interval.lo`, `e0` — are in `ADOPTED_TAIL_INPUTS.json` per cell, and
the sealed clause computes it from exactly them (`c2_d5_forecast.py:88`). I recomputed both ways at
all five cells: difference exactly `0`. Harmless numerically, but the recovery apparatus exists only
because of a non-problem, and it is what forced the `H_exact`/`M_after_exact` reading that produced
finding 3.

### 13. Dead state with a comment describing behaviour that does not exist; an unperformed "verification".

`code/c8_chain.py:97`: `self.M0[k] = None  # recovered below if the intersection ever clips` —
nothing below recovers it and `self.M0` is never read anywhere in the namespace.
`code/c8_chain.py:117-118`: "The verification below confirms the clip does not bind at ANY of the
twenty committed supplies" — `verify()` never computes the clip. The **conclusion** is true (I
verified it directly), and it is *indirectly* implied because `C3_BLOCKER`'s Γ was computed **with**
the clip and agrees to 1.97e-17, but the docstring claims a check the code does not perform and does
not identify the indirect mechanism that actually establishes it.

### 14. `REMOTE_HOSTS_CONTACTED: 0` is contradicted by the producers that emit it.

`c8_b0_audit.py:43`, `:199` and `c8_mutations.py:151` each run `git ls-remote … origin …`. `origin`
in this worktree is `https://github.com/flaggielover/ReBaseGuard.git`, so every run makes HTTPS
queries to github.com — while `c8_b0_audit.py:221-223` and `README.md:7-8` record
`REMOTE_HOSTS_CONTACTED: 0`. The intent (no AWS, no Vultr, no compute host) is clearly met and I have
no concern about the substance; the field as written is false, and it means re-running the B0 audit
or the mutation suite requires network. Fix: scope the field to compute hosts, or add
`VCS_REMOTE_QUERIES: 3 (github.com, read-only ref listing)`.

### 15. "Not from its summary ranges" implies a disagreement that does not exist.

`README.md:12-13`. `K5_COVERAGE_MAP_R5.json#/per_m/5` declares `open_ranges: [[306, 309]]`,
`pass_ranges: [[0, 305]]`, `newly_passing: [305]` — the summary says the same thing as the per-cell
verdicts, and `c8_b0_audit.py:112-123` checks and records that they agree. The per-cell
reconstruction is the right method; the README's phrasing suggests the artifact's summary was
unreliable, which it was not. The underlying claim (open = {306,307,308,309}, 305 PASS/adopted, m=1,2,3
complete at 310 cells) is **correct** — I verified all of it independently.

### 16. The prose fact-check cannot see most of the README's numbers, and "backed" carries no semantics.

`code/c8_factcheck.py:26`: `NUM = re.compile(r"(?<![\w.])(\d+\.\d{4,})(?![\w])")` — only numerals with
**four or more** decimal places are scanned. That excludes `4.5`, `4.9`, `1.90`, `2.24`, `1.25`,
`3.12.3`, `2.5.2`, `0.9.0`, `3.6.0`, `10.76`, `43.06`, `7.18`, `1.79` — including finding 10's
misquote and every host-profile figure. `backed()` (`:67-71`) then accepts a numeral if *any* value
anywhere in *any* C8 JSON lies within half an ulp of its last printed digit, with no binding to the
field it is supposed to come from. A figure can be "backed" by an unrelated number.

### 17. B0_04's disposition check is shaped to the current text rather than to its stated property.

`code/c8_b0_audit.py:56-63`: `not_landed <= 2 and ("0 NOT_LANDED" in adj or "**0**" in adj)`. The
second disjunct is satisfied by any bolded zero anywhere in a 400-line adjudication; the first
tolerates up to two genuine `NOT_LANDED` rows. The stated property — "C7 final condition dispositions
leave no finding NOT_LANDED" — is not what is tested.

---

## OBSERVATIONS

### 18. Two published leverage figures for the same R3/E1 construction are not reconciled.

`C6_CLASSIFICATION.json#/routes/E1/leverage_upper_bound`: "at the diagnostic Lambda with A1 = A2 = 0:
307 closes (−0.0602), 308 barely closes (−0.0030), 309 does NOT (+0.0468)". C8's R3 oracle for the
same construction gives −0.09299 / −0.04047 / +0.004661 (which equal C4's `Gamma_at_bound` exactly).
Presumably a different diagnostic Λ, but C8 cites C6 elsewhere and does not say which Λ C6 used or
note that the numbers differ by a factor of ~10 at 309.

### 19. What I checked and found clean.

- **Gate ordering.** Gate blob sha256 `55e743320987a1e0…` matches `GATE_SHA` in all three producers
  and on disk. Commit positions in `git log --reverse`: B0 audit `70d6bf45` = 552, gate `218cc314` =
  553, first result artifact `d58176ae` = 554. Every RESULT artifact is strictly after the gate; the
  B0 STATE_AUDIT precedes it and the fact-check classifies it correctly rather than flagging it.
- **Non-blindness.** The gate discloses that it was frozen after exploratory computation
  (`:67-75`). I agree with the reasoning that the structural criteria are not threshold-fitted; note
  that the one numeric threshold (`material_fraction_definition`) is never actually exercised, because
  R1/R2 were excluded structurally and R3 closes cells outright.
- **Compute boundary.** No `numpy`/`scipy`/`flint`/`mpmath`/`sympy`/`gmpy2` import anywhere in
  `code/`; `toolchain_present()` uses `importlib.util.find_spec`, which resolves without importing;
  all arithmetic is `fractions.Fraction`. No kernel evaluation, no operator certification, no AWS or
  Vultr contact. Guard DENY, `EXECUTION_AUTHORIZED` untouched, main not modified. Only the VCS ref
  queries of finding 14.
- **Predecessor integrity.** B0_13 compares each of the six predecessor namespace trees at C8 HEAD
  against its own published head — a real check, and it passes.
- **Main refs.** `LOCAL_MAIN_REF c123b9bb…` is a genuine ancestor of `REMOTE_MAIN_REF 1cb45382…`
  (verified with `merge-base --is-ancestor`), so "local main is behind" is correct.
- **Reproducibility.** All four runnable producers regenerate their committed artifacts
  byte-for-byte.
- **Chain arithmetic.** 20/20 committed supplies reproduced (max |ΔΓ| 1.97e-17); M reproduced against
  C5's `M_used` at all four cells (max 2.50e-16); the 309 A0 ceiling 3.2664157282671957 equals C5's
  `critical_A0_C5T` 3.266415728267196; every figure in the README table matches `C5_FORECAST.json`
  and `C8_DECISION.json`. The arithmetic is not where this campaign's problems are.

### 20. The 309 refutation itself, on its stated scope, holds.

I attacked this hardest and could not break it **within route R3 / the atom-constant family**:

- Lemma SM(d) is an equality, not an inequality — `C4_ADJUDICATION.md:59-61`: "admissibility is
  *equivalent* to `A0 ≥ sup_cell E_a[τ] = Λ_k`". The units line up; the floor really is on `A0`, not
  on `τ`.
- Γ is nondecreasing in each of `A0, A1, A2`: the enclosure half-width is affine in `A` with
  nonnegative coefficients (`tct_rule.py:268`, assembled with nonnegative `c` at `:196-208`), and
  ρ·x_hi > 0 at every tail cell (x_hi ∈ [1.79, 2.09]).
- The oracle is strictly stronger than anything achievable: `A0 = Λ` is *below* the true `sup_cell
  E_a[τ]`, and `A1 = A2 = 0` is unreachable. Driven through the **sealed** clause it still fails:
  M(A0 = Λ₃₀₉, 0, 0) = **2.154096669** > C5-T budget 1.995669915 (and > frozen budget 1.969827744).
- The floor exceeds the ceiling under both floors: 3.586306 (C7 PRIMARY, 9.79 % margin) and 3.297250
  (C4, **0.944 %** margin under C5-T).

So "MATHEMATICALLY_REFUTED" meets the gate's standard **for that route and that family**. It does
**not** support the unqualified `README.md:68` claim that R4 is the only route with leverage on 309
(finding 2), and the attribution paragraph must carry C5's margins (finding 6).

---

## Summary

Every number in the campaign checks out and every producer is reproducible; the arithmetic is the
strongest part of this work. The defects are all in what the numbers are taken to **mean** and in
what the campaign did not read.

Three of them are disqualifying on their own. C8 declares cell 306's blocker to be adoption while a
**binding, prospective adoption floor** — set by the C2 adjudicator, which explicitly anticipated
C8's exact Γ and said a D′-class campaign would not discharge it — is failed by 306 on **both** limbs
under **both** clauses. C8 selects a route from a four-member candidate set it invented, while C4's
adjudication §7 and C5's fragility block name mechanisms with leverage on 309 that C8 never
evaluates, making `README.md:68` false against the campaign's own reads. And the "M = magnitude"
justification is wrong in both halves: the clip is carried in the very file `c8_chain.py` opens and
is implemented in a predecessor C8's sibling campaign already calls, and dropping it reverses the
claimed conservativeness above ≈ 2× the certified supply — a regime C4 published saturation values
for.

Two further findings would each be enough to hold publication on their own: the load-bearing negative
is a tautology dressed as a measurement, and the "cheapest sufficient fact" model contradicts the
proportionality the campaign's own gate asserts, inventing a second required fact for cell 308 and
overstating the headline 307 figure that the route choice is justified by.

The selected outcome (`NEXT_ROUTE_OPERATOR_CERT`, R3, cell 307 first) may well survive all of this —
307 is the cheapest target on every model I tried. But it has not been **established** by this
campaign, because the candidate set was incomplete, the comparison figures are wrong, and one of the
four cells is classified against its governing adjudication.

NOT_READY
