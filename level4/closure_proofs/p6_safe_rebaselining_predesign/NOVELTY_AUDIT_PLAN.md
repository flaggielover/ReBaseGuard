# P6 novelty audit plan

```text
NOVELTY = NOT_ADJUDICATED
```

That line is the status of this document and must not change until the audit
below has actually been executed. **Nothing in the P6 pre-design claims
novelty**, and no P6 closure claim may be made before this audit runs.

The reason the bar is higher than for P1–P5/P7: those campaigns were
*diagnostic* — they described a system. P6 is *prescriptive* — it will propose
an algorithm. A diagnostic result that unknowingly duplicates prior art is a
redundant description; a prescriptive result that does so is a method presented
as new that is not, which is the most damaging failure available to this project
(`F12`). Note also that P4's own novelty audit is **not adjudicated** (`G4`), so
there is no precedent in the repository to lean on.

---

## 1. Literature classes that must be checked

Each class below must be searched, and for each the audit must record: the
closest prior work found, the dimension on which P6 differs (or does not), and
an explicit verdict of `DISTINCT` / `OVERLAPPING` / `DUPLICATE`.

| # | class | why it is a threat to P6 |
|---|---|---|
| L1 | **Self-starting and adaptive CUSUM** (Hawkins; Hawkins & Olwell; self-starting charts generally) | the canonical treatment of "monitoring while the reference is being estimated". If a self-starting chart already solves the post-alarm re-baselining problem, P6's framing is the contribution, not its method |
| L2 | **Adaptive reference / parameter updating in control charts** | directly the mechanism P6 controls |
| L3 | **EWMA reference adaptation / adaptive centring** | an EWMA on the reference is *exactly* a fixed-`rho` reuse rule in disguise; the relationship must be stated explicitly, not discovered by a referee |
| L4 | **Post-alarm reset, restart and recalibration policies** | the closest match to P6's actual object |
| L5 | **Change-point restart rules; repeated/sequential change detection** (Lorden, Pollak, Moustakides lineage; repeated CUSUM/SR) | the theoretical frame P7/P5 already sit inside |
| L6 | **Selective data reuse / windowed re-estimation after a stopping time** | the specific pathology (reusing stopping-time-selected data) may have a name already |
| L7 | **Post-selection inference / selective inference** (Fithian–Sun–Taylor and successors) | the *mechanism* — conditioning on a selection event induced by a stopping rule — is a well-developed field, and the exact-conditional structure `S1` is a post-selection statement |
| L8 | **Adaptive sampling / adaptive design of experiments** | Family C's fresh-sample injection |
| L9 | **Sequential design; variable-sampling-interval and variable-sample-size control charts (VSI/VSS)** | VSS charts adapt the *sample size* from the current statistic — structurally very close to adaptive `m_j`/`k_j`. **This is the highest-risk class** |
| L10 | **Robust sequential detection** | Family D's clipping/shrinkage |
| L11 | **State-dependent / feedback control of monitoring rules**; adaptive thresholding | the general frame |
| L12 | **Estimation-effect literature for control charts** (Jensen, Jones-Farmer et al.: the effect of parameter estimation on chart performance) | this literature already quantifies the ARL damage from an estimated reference. P7's absolute effect is explicitly attributed to matched information rather than claimed as a discovery (`S21`); P6 must be equally careful |
| L13 | **Inverse-variance / precision weighting in sequential updating; Kalman-filter reference tracking** | Family F's greedy rule *is* inverse-variance weighting (`P6_THEORY_TARGETS.md` §7); this is standard and must be presented as such |
| L14 | **Bandit / exploration-exploitation formulations of monitoring** | any adaptive-`rho` rule can be cast this way |

## 2. Comparison dimensions

Prior art will overlap on some dimensions and not others. The audit must resolve
each candidate against **all** of these, because "different in some respect" is
not novelty:

1. **Object controlled** — reuse weight, window length, fresh-sample count,
   threshold, sampling interval.
2. **Trigger** — post-alarm only (P6) vs continuous adaptation (most of L2/L3).
3. **Information used** — P6's implementable set is `F01`–`F13` only, with an
   explicit prohibition on the latent error; much of the literature assumes the
   in-control parameters are estimable from a clean Phase-I sample.
4. **The recursion** — P6's distinguishing feature is that the reference is
   built from data selected *by the stopping time* and that this recurs
   cycle after cycle. Does the prior work have the recursion, or only one round?
5. **Objective** — delay tail / blind-spot probability (P6) vs mean ARL (most).
6. **Guarantee type** — asymptotic, exact-conditional, empirical.
7. **Cost accounting** — does the prior work charge for fresh samples (`H5`)?

Dimension 4 is the one most likely to carry whatever novelty exists, and
dimension 7 is the one most likely to be missing from prior work.

## 3. Search queries to run

To be executed against a literature search tool (Perplexity or equivalent) and
recorded verbatim with dates and results.

```
1  self-starting CUSUM control chart estimated parameters reference update
2  adaptive reference updating control chart post-alarm restart policy
3  EWMA adaptive centerline control chart reference adaptation
4  repeated change point detection restart rule CUSUM Shiryaev-Roberts recursive
5  effect of parameter estimation on CUSUM ARL Phase I sample size
6  data reuse after stopping time bias sequential detection
7  post-selection inference stopping time conditional distribution control chart
8  variable sample size control chart adaptive sample size VSS ARL
9  variable sampling interval adaptive control chart design
10 adaptive sampling sequential change detection sample allocation
11 robust sequential change detection contaminated reference
12 feedback control of statistical process control chart parameters
13 in-control ARL degradation reference re-estimation after false alarm
14 inverse variance weighting sequential parameter update shrinkage control chart
15 detection delay tail quantile control chart worst case delay
16 bandit formulation statistical process control adaptive monitoring
17 self-tuning monitoring reference baseline drift compensation
18 conditional distribution of the last m observations before a stopping time
```

Queries 6, 7 and 18 are the ones aimed at P6's actual mechanism; if the audit
turns up a match there, the novelty position changes materially and the campaign
must be reframed before it runs, not after.

## 4. Audit procedure

1. Run every query in §3; record results, dates and the tool used.
2. For each of L1–L14, record the closest prior work and a
   `DISTINCT`/`OVERLAPPING`/`DUPLICATE` verdict against the seven dimensions.
3. Where the verdict is `OVERLAPPING`, state the *specific* difference in one
   sentence and cite the dimension number. Vague differences do not count.
4. Produce `NOVELTY_AUDIT.md` with a per-class table and an overall verdict.
5. **Independent adjudication of the audit itself**, as with every other
   ReBaseGuard closure artifact.

## 5. Pre-commitments

* If any P6 method is found to duplicate prior art, it is **reported as a
  replication in a new setting**, not repositioned as novel by adding a feature
  after the fact (`F12`).
* The novelty verdict is made **before** the confirmation stage (P3 in
  `COMPUTE_PLAN.md`), not after results are in, so that the audit cannot be
  influenced by how good the numbers look.
* A P6 that contributes **no** new method but produces a defensible frontier,
  an oracle ceiling and a negative result is a legitimate closure outcome. The
  campaign is not required to be novel; it is required to be honest about
  whether it is.
