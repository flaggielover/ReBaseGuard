# P6 failure-mode register

Preregistered *before* the campaign, so that each failure has a detector
attached rather than a post-hoc explanation. Each row: the failure, how it
happens, how it is detected, and what is done about it.

A failure mode with no detector is not registered — it is admitted. Where P6 has
no detector, the row says so.

---

## A. Information failures

### F1 — a policy uses the latent `e` accidentally
*How.* The frozen simulator works natively in latent coordinates (`D2`), so
`e_j` is sitting in scope at exactly the moment the policy is called. A single
attribute access leaks it, and the resulting policy looks brilliant.
*Detector.* **Structural, not procedural.** Implementable policies receive a
`CycleObservation` whose field set contains no latent quantity;
`tests/test_observability.py` asserts the field set exactly and asserts every
registered implementable policy has `requires_oracle = False`.
*Response.* Any result produced by a policy later found to be leaking is
discarded, not reclassified as an oracle result.
*Instance already found.* The history channel of `OBSERVABILITY_AUDIT.md` §4 is
legal in the model but leaks in the simulator whenever `e_0` is *known*, because
then `d_j = e_j - e_0 = e_j` exactly. Found while writing the harness; resolved
structurally (`OBSERVABILITY_AUDIT.md` §4a) and asserted by test. The general
lesson is recorded there: **the audit must be re-run against the harness, not
only against the mathematics.**

### F2 — concluding a monitoring gain from a reference-state gain
*How.* Writing "the policy reduces `E[e^2]`, therefore it improves ARL". This is
precisely the inference P7's candidate P7-E was **rejected** for (`S18`, `X6`),
and P7 states explicitly that reducing `E_pi[e^2]` is not proved to improve
every metric.
*Detector.* Review rule: every claim about a monitoring metric must cite a
*measurement* of that metric. A claim citing only a surrogate is a defect.
*Response.* Measure it, or drop the claim.

### F10 — the Family E filter is misspecified under a shift
*How.* The increment-observability construction (`OBSERVABILITY_AUDIT.md` §4)
assumes `theta` constant. Under `Delta > 0`, `mu_{j+1} - mu_j` no longer equals
`e_{j+1} - e_j`, and the filter drifts confidently in the wrong direction —
worst case, exactly into the blind spot `S10`.
*Detector.* Every filter-based policy is evaluated at `Delta in {0.5, 1, 2}` and
its estimation error is reported as a diagnostic against the true `e_j`.
*Response.* If the filter degrades under shift, it is reported as a
`Delta = 0`-only method, or dropped.

## B. Metric failures

### F3 — improves ARL by quietly becoming fresh-only
*How.* An adaptive policy discovers that `rho_j -> 0` maximises `Arl0` and
converges there, "beating" full reuse by abandoning the premise of the campaign.
*Detector.* `ES3` in `COMPUTE_PLAN.md` §3, plus the hard constraint `K4`
(`Fresh(U) <= Fresh(B0)`), plus the requirement that every comparison be at
**matched sample cost**.
*Response.* Report as `COST_DEGENERATE` with its numbers; it is an informative
negative, not a bug to hide.

### F4 — improves the mean but worsens the delay tail
*How.* The exact shape of the closed damage: at CUSUM `m=1, rho=1, Delta=1` the
median delay (`7`) is *better* than nominal while `q95 = 275` (`S9`).
*Detector.* `Dmean`, `Dmed`, `Dq95` and `Dtail(L)` are all mandatory in every
out-of-control table (`EVALUATION_PROTOCOL.md` §3). A table missing them is
rejected at review.
*Response.* The tail metric governs.

### F14 — a one-cycle metric hides a later-cycle collapse
*How.* Cycle 1 looks nominal (`463..474`) while cycle 2 collapses by `98%`
(`S8`). Any evaluation that starts from `e_0 = 0` and stops early sees only the
good half.
*Detector.* R1–R4 regimes are all mandatory (`EVALUATION_PROTOCOL.md` §5); `Coll
= E[tau_2]/E[tau_1]` is a reported gate (`K3`); R3 curves run to cycle 50.
*Response.* No claim may rest on R1 or R4 alone.

## C. Generalisation failures

### F5 — CRN misused in the uncertainty statement
*How.* Assuming paired runs are strongly coupled, sizing the campaign on the
paired variance, and reporting intervals that are too narrow. In this chain, two
policies decouple as soon as they make a different decision
(`STATISTICAL_DESIGN.md` §2).
*Detector.* Report the **measured** paired correlation per cell; size on the
unpaired variance.
*Response.* If the measured correlation is below `0.3`, either accept the cost
or switch to the per-cycle-substream mode, clearly labelled.

### F6 — overfitting to one detector, or to one `m`
*How.* A policy whose parameters were fitted at CUSUM `m=3` and reported there.
*Detector.* Every claim must reproduce on **both** detectors and at **>= 3**
values of `m`, with the effect resolved in each. `S13` licenses the *expectation*
of transfer, not the claim.
*Response.* A one-detector or one-`m` effect is reported as exactly that.

### F13 — an adaptive policy silently changes detector semantics
*How.* A policy that adjusts a threshold, imposes a minimum dwell, or seeds the
detector state after re-baselining. All are reasonable engineering ideas and all
destroy comparability with the closed P7 numbers.
*Detector.* Invariant `I1`: a constant policy must reproduce
`rebaseguard_p7.chain.simulate_chain` with **bit-identical `tau`**; and the
policy interface has no access to detector parameters.
*Response.* Out of scope; belongs to a successor campaign (`P6_METHOD_CANDIDATES.md`
§3).

## D. Selection and process failures

### F7 — post-selection winner bias
*How.* Screening `100` policies, reporting the best, and quoting its nominal
interval. With `100` arms and pure noise the maximum is roughly `2.5` sd above
the mean.
*Detector.* Tuning happens on `TUNE`; the reported numbers come from `EVAL`;
independent reproduction on `REPLAY` (`STATISTICAL_DESIGN.md` §9). Frontier
membership is bootstrapped (§6 there).
*Response.* A method that does not reproduce on `REPLAY` is not a P6 result.
`OPTIMIZATION_FORMULATIONS.md` E exists so that P6 is not *obliged* to name a
winner at all.

### F8 — hyperparameter search leakage
*How.* Fitting `phi`'s breakpoints on the same seeds used to report the effect;
or tuning at `Delta = 1` and evaluating at `Delta = 1`.
*Detector.* Seed-family separation asserted by test (`I5`); the shift used for
tuning is preregistered and distinct from at least one evaluation shift.
*Response.* Re-run on clean seeds or withdraw the claim.

### F9 — tuning/evaluation seed reuse
*How.* A convenience default, a copy-pasted config, a re-run that forgot the
family flag.
*Detector.* `tests/test_seeds.py` asserts the three families produce disjoint
streams; every result record carries `seed_family`, and a result whose family is
`TUNE` cannot enter a report.
*Response.* Mechanical rejection at report-build time.

### F12 — the method duplicates prior art
*How.* Adaptive/self-starting CUSUM, EWMA reference adaptation and post-alarm
restart rules are large literatures (`NOVELTY_AUDIT_PLAN.md`). A rediscovery
presented as a contribution is the most damaging outcome for a prescriptive
campaign.
*Detector.* The novelty audit runs **before** any closure claim, not after; the
current status is `NOVELTY = NOT_ADJUDICATED` and stays there until it does.
*Response.* Reposition as a *replication in a new setting* — which is still a
result — rather than as a new method.

## E. Premise failures

### F11 — importing a stationary-law assumption from unclosed P5
*How.* Writing `E_pi[.]` because P5's T7 says `pi` exists — while P5 is
`PENDING_CODEX`; or, subtler and more likely, applying T7 (proved for **fixed**
`(D, m, rho)`) to a **state-dependent** policy, where it does not hold at all
(`H7`).
*Detector.* Every objective has a finite-horizon form
(`OPTIMIZATION_FORMULATIONS.md` preamble); a review pass greps the campaign
documents for stationary notation and checks each occurrence against the branch
in force.
*Response.* Rewrite in finite-horizon form. The estimators do not change.

### F15 — `rho_c` reintroduced as a fake safety rule
*How.* It is the most natural-sounding thing in the whole repository and it is
wrong: the pre-committed test returned `LOCAL-MATHEMATICAL, NOT OPERATIONAL`
(`S11`) and the measured ARL optimum lies `1.25x..4.1x` **above** `rho_c`
(`S12`). It creeps back in as a plotting convention, then as a default, then as
a threshold.
*Detector.* `rho_c` is admissible only as a figure annotation
(`SAFETY_OBJECTIVES.md` §4 Tier 3). Any appearance in a policy definition, a
constraint, or a gate is a defect.
*Response.* Remove. `X1` is not negotiable.

### F16 — quoting `S14` and `P9` as if they agreed
*How.* "Reuse hurts more at large `m`" (`S14`, closed) and "larger `m` is better
on every metric" (`P9`, provisional) sound contradictory and are not: they are
measured against different controls — a same-`m` fresh ratio versus an absolute
level. A document quoting one without the other misleads.
*Detector.* `X8`; review rule.
*Response.* Always quote the pair with the resolution.

## F. Failures P6 currently has **no** detector for

Recorded honestly, because a register that claims complete coverage is itself a
failure mode.

| # | failure | why there is no detector |
|---|---|---|
| N1 | The frozen Gaussian core is itself unrepresentative of any real process | out of scope by construction (`X5`); only P8 can address it |
| N2 | The whole re-baselining formulation (reuse the terminal window at all) is the wrong operational design | P6 optimises within the formulation; it cannot evaluate the formulation |
| N3 | A policy that is safe in simulation but unimplementable for operational reasons (latency, auditability, operator trust) | no model of the operational environment exists in ReBaseGuard |
| N4 | Slow instabilities with a timescale beyond 50 cycles | R3 runs to 50 cycles; longer runs would catch more, at a cost not currently budgeted. **This is a known, accepted gap** |
