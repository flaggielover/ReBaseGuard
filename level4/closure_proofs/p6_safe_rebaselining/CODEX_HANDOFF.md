# P6 -> Codex handoff

```text
CAMPAIGN_SELF_CLASSIFICATION = P6 = CLOSED_CANDIDATE     (the campaign's own reading; the verdict is yours)
CANDIDATE_METHOD             = SAW-M (selection-aware weighting, second-moment form)
NOVELTY                      = PARTIAL / NOT_INDEPENDENTLY_ADJUDICATED
P5                           = FROZEN PARTIAL, untouched
PROTECTED TREE               = 2,907 tracked files outside the P6 namespaces, ZERO modified vs HEAD = bb03c0ea
COMMITS                      = NONE.  Nothing committed, nothing pushed.
```

**Do not trust this campaign's self-assessment.** Section 9 lists the attacks I
would run against it, ordered by how much damage they would do.

---

## 1. Claims, separated by kind

### EXACT THEOREM

| # | statement | premises |
|---|---|---|
| E1 | **T6-A.** For *every* `F_j`-measurable policy with `rho_j <= rho_max`, `k_j >= k_min`: `sup_x E[e_{j+1}^2 | e_j = x] <= rho_max^2 C_D + 1/k_min`, `C_D = sup_x E_x[tau_x]`. Uniform over the state **and over the policy** | T1, T4/T5 |
| E2 | **Lemma 3.1.** `E[e_{j+1}^2 | F_j] = rho^2 V + (1-rho)^2 nu` with `V = E[U_j^2 | F_j]`, `nu = 1/k`; minimised at `rho* = nu/(V+nu) in (0,1)`, value `Q*(V) = nu V/(V+nu)`; excess risk `= (V+nu)(rho-rho*)^2` | T1, T2 |
| E3 | **T6-C(i)** dominance: for any constant `rho_0`, the risk gap is `E[(V+nu)(rho_0 - rho*(V))^2] > 0` unless `V` is a.s. constant | T1, T2 |
| E4 | **T6-C(ii)** the Jensen identity: best constant `rho` attains `Q*(E V)`, the `F_j`-measurable rule attains `E[Q*(V)]`, `Q*` is strictly concave, so the entire advantage is `Gap = Q*(E V) - E[Q*(V)] ~ nu^2 Var(V)/(E V + nu)^3`. **Fixed-`rho` tuning is exactly the `V = const` member of the family** | T1, T2 |
| E5 | **T6-C(iii)** the plug-in criterion: `E[h(rho_hat;V)] < Q*(E V)` **iff** `E[(V+nu)(rho_hat - rho*(V))^2] < Gap` | T1, T2 |
| E6 | **T6-B.** For a *memoryless* admissible policy with `rho_max < 1`, `1 <= k <= k_max`: `(e_j)` is a time-homogeneous Markov chain, `P_u^2` satisfies a whole-space minorisation, so `P_u` has a **unique** invariant law, converges to it **uniformly geometrically** in TV from every start, and has **all** positive invariant moments; if `u` is sign-equivariant, `pi_u` is symmetric | T1, T4/T5, Doeblin |
| E7 | **T6-D(a).** The oracle one-step tail is exact: `P(|e_{j+1}|>c | H_j) = Phibar((c-rho U_j)sqrt k/(1-rho)) + Phi((-c-rho U_j)sqrt k/(1-rho))` | T1 |
| E8 | **T6-E.** Under the approved cost model, `rho == 1` is the unique zero-fresh-cost policy; every policy with `P(rho_j<1)>0` costs `>= k_min P(rho_j<1)` | cost model |

### CONDITIONAL THEOREM

| # | statement | condition |
|---|---|---|
| K1 | T6-B applies to SAW | SAW is memoryless **and** `rho_j <= nu/(s_floor+nu) < 1` structurally. Both are asserted by test; but the *proof* is new and unadjudicated |
| K2 | T6-D(b) Chebyshev tail bound `P(|e_{j+1}|>c|F_j) <= Q*(V)/c^2` | exact, but **never binding** at `c_beta ~ 0.28`: the bound exceeds 1 in every measured cell. Reported as a failed route |

### NUMERICAL EVIDENCE

| # | statement | scale |
|---|---|---|
| N1 | The observable readout `(zbar_j, tau_j)` explains **`R^2 = 0.95`** of the variance of the latent raw window mean, in all 8 `(detector, m)` families | 520,000 calibration cycles per cell |
| N2 | The selection inflates `E[U^2]` to `0.91`-`2.52` against the unselected `1/m` = `0.20`-`1.00`: a factor of **2.5x-4.7x** | same |
| N3 | T6-C(iii)'s criterion is satisfied in **8/8** cells; plug-in error is **7.4%-13.9%** of the Jensen gap; the plug-in's calibration correlation is `0.997`-`0.999` (see `RESULTS.md` section 6 for what that does and does not mean) | 480,000 cycles per cell |
| N4 | The predicted one-step `E[e^2]` gain (`6.0%`-`15.0%`) matches the **measured stationary** gain to within ~2 pp for `m >= 2`, and reproduces the ordering across `m` exactly | EVAL |
| N5 | SAW-M beats each cell's `B2*` at **matched `Fresh`** in **8/8** families on `Arl0`, `Rms`, `Dtail(100)`, `Dq95` and `Rdelta`; reproduced **8/8** on `REPLAY` with `B2*` re-selected there | `n_rep = 8000` IC, `60000` delay |
| N6 | The same holds in **18/18** `(detector, m, k)` frontier cells with SAW recalibrated at each `k`, and in **18/18** finite-reference `(detector, m, m_0)` cells | EVAL |
| N7 | The SAW-T Gaussian approximation errs by `0.0005`-`0.003` overall, worst decile-bin gap `0.013`-`0.020` | EVAL |

### EMPIRICAL OBSERVATION

| # | statement |
|---|---|
| O1 | **The ablation ladder is monotone in information** and the sensor ablation destroys the effect: `SAW_A_flat` (which *is* a fixed-`rho` policy, asserted bit-identical) differs from `B2*` by `+1.4%` `[-2.7%, +5.7%]` on the primary objective — **INCONCLUSIVE** |
| O2 | Thresholding the same sensor (`B6`, `B11`) is **worse** than the best fixed weight; the continuous inverse-variance weight is doing the work |
| O3 | SAW reuses **more** (`Wbar` `+64.8%`) while distorting **less**, at identical fresh cost, and is `11.4%` cheaper under the proportional cost sensitivity |
| O4 | `Dmed` is unchanged (`9` vs `9`) while `Dq95` falls `13.2%`: `S9`'s "the failure mode is a right tail" reproduced, and the repair is in the same place |
| O5 | The derived sensor-free weight `rho_flat = nu/(E[V]+nu) = 0.174`-`0.286`, computed with no grid search, lands within `0.4%` of the grid-searched `Arl0` optimum |
| O6 | SAW's advantage **decays with `k`** exactly as the Jensen gap does (`+12.9%` at `k=m=1` down to `+0.6%` at `k=20`): it matters most where fresh data is expensive |
| O7 | Measured pair correlations are `~0.00` throughout: CRN in this chain is seed alignment, not path coupling, as the pre-design warned |

### REJECTED CLAIM

| # | rejected |
|---|---|
| R1 | **A theorem-backed safety guarantee.** T6-D route 1 is exact and never binds; route 2 is open; route 3 is an approximation with a measured error. `METHOD_NOVELTY_SEPARATION.md` criterion `N2` is **not met** |
| R2 | **Algorithmic novelty.** The weight-adaptation shape is AEWMA-shaped (Capizzi & Masarotto 2003), the formula is textbook inverse-variance weighting, and gating on a statistic is cautious parameter learning (Capizzi & Masarotto 2020) |
| R3 | **`P8` at P5's strength.** `argmax_rho Arl0` and `argmin_rho Rms` coincide in only **2 of 8** cells on P6's grid (adjacent in the other 6, always with `Rms` at the larger `rho`), against P5's 7-of-8. The strong reading of RMS/ARL co-optimality does **not** reproduce |
| R4 | **That a perfect trigger is a ceiling.** Oracle `Z3` (reset iff true `|e|>0.3`) is far *worse* than the best implementable policy; oracle `Z4` (knows `Delta`) is worse than SAW. A badly shaped oracle bounds its own rule, not adaptivity |
| R5 | **Any monitoring inference from a reference-state gain** (`S18`, `X6`). Every monitoring number here is measured |
| R6 | **T7 transferred by analogy.** T6-B is proved from scratch; section 4.3 of `THEORY.md` names the three places it differs |

### OPEN QUESTION

| # | open |
|---|---|
| Q1 | **T6-B for policies with internal memory.** The Family-E filter, any EWMA rule, and `B10` fall outside it. The state must be augmented and the minorisation redone |
| Q2 | **A sharp sub-Gaussian bound on a stopping-time-selected window mean** (the pre-design's T6-D route 2). Without it there is no enforceable tail bound |
| Q3 | **Whether the stationary second moment of SAW is provably below the best fixed `rho`'s.** Measured yes; T6-C is one-step from a common entering law |
| Q4 | **Why the one-step prediction matches the stationary gain so well for `m >= 2` but under-predicts at `m = 1`** |
| Q5 | **Whether a history-using policy beats SAW.** The increment channel carries real information and SAW deliberately ignores it, to buy memorylessness and hence T6-B |
| Q6 | **`Delta = 0.5`.** No policy improves the delay tail there; the discrimination ratio says the apparent winner (full reuse) is pathological. What the right objective is in that regime is unresolved |

---

## 2. The final method, exactly

```text
DESIGN CONSTANTS, per (detector, m, k), fitted on TUNE seeds at Delta = 0 only:
    g0, g1   ordinary least squares of the latent raw window mean U on
             [ zbar , zbar/sqrt(tau) ]
    s0       mean squared residual on cycles with w == m
    s1       mean squared residual on cycles with w <  m   (= s0 if that group is empty)
  obtained inside a fixed-point loop (calibrate under the current policy,
  rebuild the policy, repeat; common random numbers across iterations).

STRUCTURAL CONSTANTS (not tuned; required by THEORY.md T6-B):
    rho_max = 0.95        s_floor = 1e-2

AT EVERY ALARM (memoryless; observables only):
    w    = min(m, tau)
    zbar = (1/w) * sum of the last w innovations z          # convention A
    mu   = ( g0 + g1 / sqrt(tau) ) * zbar
    s    = max( (w == m) ? s0 : s1 , s_floor )
    V    = mu*mu + s
    rho  = min( (1/k) / (V + 1/k) , rho_max )
    new reference = rho * (old reference + zbar) + (1 - rho) * mean(k fresh observations)
```

Cost per alarm: one square root, three multiplications, one division. No table,
no optimisation, no state. **Zero free hyperparameters** beyond the design
choices `(m, k)`.

### Frozen constants at the primary cell (CUSUM, `m = 3`, `k = 3`)

```text
g0 = 0.93840   g1 = -1.06668   s0 = 0.06263   s1 = 2.56008
E[V] = 1.3239  sd(V) = 0.8141  rho_flat = 0.2011  R^2 = 0.9517
```

All eight cells are in `results/calibration.json` under `<detector>_m<m>.final`.

### Seeds

```text
TUNE   root 0x50365455_4E45   calibration, screening, every design choice
EVAL   root 0x50364556_414C   every reported number
REPLAY root 0x50365245_504C   independent reproduction, untouched until confirmation was complete
stream = SeedSequence([root, sha256(detector)[:8], m, sha256(policy_id)[:8], sha256(cell_tag)[:8], block])
```

Disjointness is asserted by `tests/test_cost_and_metrics.py::test_seed_families_are_disjoint`.

### The freeze point

`results/calibration.json`, written by `stage1_foundation.py` from `TUNE` seeds
at `Delta = 0`, **before** `stage2_screen.py` or `stage4_confirm.py` ran. No
constant changed afterwards.

---

## 3. Baseline table — the primary cell, CUSUM `m = 3`, `Delta = 1`, EVAL

| policy | `Arl0` | `Rms` | `Fresh` | `Wbar` | `Coll` | `Dmean` | `Dmed` | `Dq95` | `Dtail100` | `Rdelta` |
|---|---|---|---|---|---|---|---|---|---|---|
| `B3` full reuse | 69.31 | 0.9235 | **0.00** | 1.000 | 0.016 | 64.65 | 9 | 341 | 0.1429 | 0.933 |
| `B0` fresh-only | 132.48 | 0.5751 | 3.00 | 0.000 | 0.289 | 41.53 | 9 | 184 | 0.0819 | 0.313 |
| `B2*` = `rho 0.15` | 144.10 | 0.5177 | 3.00 | 0.150 | 0.293 | 36.13 | 9 | 144 | 0.0677 | 0.251 |
| `SAW_A_flat` | 144.67 | 0.5132 | 3.00 | 0.201 | 0.280 | 36.31 | 9 | 146 | 0.0686 | 0.251 |
| **`SAW_M`** | **151.52** | **0.4909** | 3.00 | 0.247 | 0.301 | **33.24** | 9 | **125** | **0.0607** | **0.219** |
| `SAW_T` | 150.96 | 0.4950 | 3.00 | 0.214 | 0.308 | 33.36 | 9 | 128 | 0.0611 | 0.221 |
| `Z1` oracle | 156.53 | 0.4776 | 3.00 | 0.310 | 0.307 | 31.71 | 9 | 117 | 0.0572 | 0.203 |
| `B9` `k=2m` | 172.10 | 0.4041 | 6.00 | 0.200 | 0.333 | 23.70 | 9 | 75 | 0.0368 | 0.138 |
| `B9` `k=4m` | 190.59 | 0.3372 | 12.00 | 0.200 | 0.361 | 17.01 | 9 | 49 | 0.0170 | 0.089 |

## 4. Effect sizes and uncertainty — `SAW_M` vs `B2*`, paired, `B = 4000`

| metric | EVAL | REPLAY |
|---|---|---|
| `Dtail(100)` | **-10.4%** `[-14.3%, -6.4%]` | **-8.9%** `[-12.8%, -4.9%]` |
| `Dq95` | -13.2% `[-18.6%, -7.8%]` | -11.1% `[-16.3%, -6.3%]` |
| `Dmean` | -8.0% `[-11.3%, -4.5%]` | -6.1% `[-9.4%, -2.4%]` |
| `Dmed` | 0.0% (both `9`) | 0.0% |
| `Arl0` | +5.1% `[+4.5%, +5.7%]` | +4.8% `[+4.2%, +5.4%]` |
| `Rms` | -5.2% `[-5.4%, -5.0%]` | -4.4% `[-4.6%, -4.2%]` |
| `Tail(1.0)` | -20.4% `[-21.5%, -19.2%]` | — |
| `OutCal(0.25)` | -3.9% `[-4.2%, -3.6%]` | — |
| `Coll` | +0.8% `[-4.7%, +6.4%]` INCONCLUSIVE | +3.6% `[-2.0%, +9.6%]` INCONCLUSIVE |
| `Fresh` | 0.0% (matched exactly) | 0.0% |
| `Wbar` | +64.8% `[+64.6%, +64.9%]` | +23.6% `[+23.4%, +23.7%]` (vs `rho = 0.20`) |
| vs `B3`: `Dtail(100)` | **-57.6%** `[-59.1%, -56.0%]` | **-57.6%** `[-59.1%, -56.0%]` |

## 5. Ablations

| rung | recovers of SAW's `Arl0` gain (median over 8 cells) | primary-cell `Dtail(100)` vs `B2*` |
|---|---|---|
| `SAW_A_flat` (sensor off; **is** a fixed-`rho` policy) | ~7% | `+1.4%` `[-2.7%, +5.7%]` INCONCLUSIVE |
| `SAW_A_naive` (raw `zbar^2` proxy) | ~55% | `-4.1%` `[-8.0%, +0.1%]` INCONCLUSIVE |
| `SAW_A_no_tau` (no stopping geometry, refitted) | ~77% | `-9.3%` `[-13.1%, -5.4%]` resolved |
| **`SAW_M`** | 100% | `-10.4%` `[-14.3%, -6.4%]` material |
| `SAW_T` | ~89% | `-9.7%` resolved |
| `Z1` oracle | 109%-219% | `-15.5%` material |

## 6. Robustness

| axis | coverage | result |
|---|---|---|
| detectors | CUSUM, SR | 8/8 families; calibrated separately, no transfer assumed |
| windows | `m in {1,2,3,5}` | 8/8; gain decays with `m` as the Jensen gap does |
| fresh budget | `k in {m, 2m, 4m}`, recalibrated | 18/18 on `Arl0`/`Rms` |
| shift | `Delta in {0, 0.5, 1, 2}` | material at `1`; under-powered at `2`; **absent at `0.5`** |
| initialisation | `e_0 = 0` (canonical) and `e_0 ~ N(0,1/m_0)`, `m_0 in {20,50,100}` | 18/18 in the secondary regime |
| seeds | TUNE / EVAL / REPLAY | 8/8 reproduce; `B2*` moves grid point in 5/8 |

## 7. Closure gates

`10/10` structural (two qualifications recorded), `4/4` numeric gates PASS,
`G-E` `REPORTED_WITHOUT_THRESHOLD` with an ordering defect.
Full audit in `CLOSURE_GATES.md` section 5.

## 8. Exact commands for focused reproduction

```bash
cd /Users/suzhe/ReBaseGuard
V=level4/.venv/bin/python
P=level4/closure_proofs/p6_safe_rebaselining

# focused tests, both P6 suites together (125)                  ~21 s
$V -m pytest $P/tests level4/closure_proofs/p6_safe_rebaselining_predesign/tests -q
#   93 campaign + 32 pre-design.  tests/test_p6c_claims.py re-derives every
#   headline number in the documents from results/*.json.

# the whole campaign, in order
$V $P/experiments/stage1_foundation.py     #  ~7 min   correspondence, c_beta, calibration
$V $P/experiments/stage2_screen.py         #  ~9 min   pilot + screen, TUNE
$V $P/experiments/stage4_confirm.py eval   # ~58 min   confirmation
$V $P/experiments/analyse.py eval          #  ~8 min
$V $P/experiments/stage5_robustness.py     # ~68 min   frontier, finite reference, T6-C(iii)
$V $P/experiments/stage4_confirm.py replay # ~68 min
$V $P/experiments/analyse.py replay        #  ~8 min
```

Single-cell replay (any cell, in isolation — every stream is a pure function of
`(family, detector, m, policy_id, cell_tag, block)`):

```bash
level4/.venv/bin/python -c "
import sys, pathlib, numpy as np
R=pathlib.Path('level4/closure_proofs/p6_safe_rebaselining').resolve()
sys.path.insert(0,str(R/'experiments'))
from _registry import calib_for, load_calibration
from rebaseguard_p6c.runner import run_incontrol
from rebaseguard_p6c.saw import SawPolicy
c=calib_for(load_calibration(),'cusum',3)
out,res=run_incontrol(policy=SawPolicy(c,k=3), detector='cusum', m=3, family='eval',
                      n_rep=8000, n_cycles=100, burn_in=15, pair_tag='confirm_paired')
print('Arl0', out['Arl0'].mean(), 'Rms', out['Rms'].mean())"
```

## 9. What to attack, in order of expected damage

1. **`THEORY.md` T6-B step (c), the minorisation.** The load-bearing new claim
   is that on `{z_1 in J}` the cycle observation is *a function of `z_1` alone*,
   so a memoryless policy's decision cannot depend on `x`. That is true only for
   a policy that reads nothing outside the cycle just ended. `THEORY.md`
   section 1 now pins the exclusion explicitly (`cycle`, `prev_tau`,
   `prev_zbar`, `prev_rho`, `prev_m`, `prev_k`, `displacement`, `last_move` are
   all legally observable and all outside the theorem), and
   `test_saw_decision_depends_only_on_the_audited_observables` asserts SAW obeys
   it by perturbing each excluded field. **Check the exclusion list is complete
   and that the proof's "function of `z_1` alone" step really follows** — this
   is still the weakest link in the strongest theorem, and a single missed
   channel voids it.
2. **T6-C's `V`, and what the reported correlation actually measures.**
   `stage5_robustness.py::block_d_plugin_criterion` estimates the reference
   quantity by binning on `V_hat` itself (200 equal-count bins). That estimates
   `E[U^2 | V_hat]`, i.e. the plug-in's **calibration**, and *not*
   `E[U^2 | F_j]`. `RESULTS.md` section 6 now says so. Both the Jensen gap and
   the plug-in error are therefore `sigma(V_hat)`-restricted, which biases both
   in P6's disfavour — but an adjudicator should confirm that direction rather
   than take it on trust, and should re-estimate the gap on the full observable
   sigma-field (e.g. a held-out non-parametric fit on `(|zbar|, tau, w)`) to see
   how much larger it is and whether the criterion still holds against it.
3. **The claim that `Fresh` is matched.** It rests entirely on the step-shaped
   cost model `C_fresh = k 1{rho<1}`. If an operator's cost is proportional, or
   if the fresh window's monitoring downtime is priced differently, the whole
   comparison moves. `FreshProp` is reported (SAW is `11.4%` cheaper there too),
   but no other model was tried. **Attack the cost model, not the arithmetic.**
4. **`B2*` selection.** It moves grid point in 5 of 8 cells between `EVAL` and
   `REPLAY`, i.e. the fixed-`rho` objective is flat near its optimum. Try a
   finer `rho` grid (say `0.01` steps over `[0.05, 0.35]`) and check whether a
   better-resolved `B2*` closes the gap. My expectation is that it does not — the
   `flat` ablation lands within `0.4%` of the grid optimum and still loses by the
   full margin — but that is an expectation, not a measurement.
5. **C1's missing timestamp.** Nothing is committed, so the claim that
   `EXPERIMENT_PROTOCOL.md` and `CLOSURE_GATES.md` were written before the
   confirmation data existed rests on this campaign's account. The mtimes of
   `results/*.json` versus the `.md` files are the only physical evidence and
   they are weak.
6. **`G-E`'s ordering defect** (`results/gate_e.json`). The selection of option
   E3 is justified from baseline numbers alone and E1/E2 are reported unedited,
   but the SAW numbers were visible when the threshold field was written.
7. **The novelty audit.** One sitting of web search, several sources read from
   abstracts, no systematic database coverage, no independent adjudication.
   Queries 6, 7 and 14 — the three aimed at the actual mechanism — returned
   nothing, and I treat that as weak evidence. It may simply be the wrong
   vocabulary.
8. **`s1`.** The truncated-window variance is a group mean over 0%-5% of cycles,
   and in three cells over fewer than a hundred observations (CUSUM `m=2` gives
   `s1 = 22.77`). It affects almost no decisions and always conservatively, but
   it is the least stable constant in the method.
9. **`Delta = 0.5`.** SAW buys nothing there. If an adjudicator judges small
   shifts the operationally relevant regime, the campaign's headline is much
   narrower than it reads.
10. **The whole formulation.** P6 optimises inside the re-baselining design and
    cannot evaluate it (`N2` in the failure register). Nothing here says reusing
    the terminal window at all is a good idea.

## 10. Artifacts to attack

| path | what it is |
|---|---|
| `results/correspondence.json` | X1/X2/X3 and `c_beta`. If X1 or X3 is wrong, everything downstream is void |
| `results/calibration.json` | the four constants per cell, the fixed-point trace, the drift to the large final pass, the Jensen gap |
| `results/screen.json`, `results/pilot.json` | TUNE screening; the basis for the three drops |
| `results/gate_e.json` | the G-E deferral, its justification, and its recorded defect |
| `results/confirm_ic_{eval,replay}.json` | in-control confirmation, all policies, all cells |
| `results/confirm_delay_{eval,replay}.json` | delay confirmation, three shifts |
| `results/confirm_ic_*_<cell>.npz` | **per-replicate arrays** — the raw material for any re-analysis |
| `results/confirm_delay_primary_{eval,replay}.npz` | per-replicate delays at the primary cell |
| `results/analysis_{eval,replay}.json` | every effect size and interval reported |
| `results/robust_plugin_criterion.json` | T6-C(iii), the circular-binning target of attack #2 |
| `results/robust_frontier.json` | 18 `(detector,m,k)` cells with SAW recalibrated at each |
| `results/robust_finite_reference.json` | 18 `(detector,m,m_0)` cells |
| `results/robust_tail_approx.json` | the SAW-T Gaussian approximation error |
| `results/protected_tree.json`, `results/protected_manifest.json` | 2,907 file hashes; zero modified |
| `results/p5_verdict.json` | the P5 verdict recorded verbatim, with the source hash |
| `src/rebaseguard_p6c/saw.py` | the method, 170 lines |
| `src/rebaseguard_p6c/calibrate.py` | the plug-in and `c_beta` |
| `src/rebaseguard_p6c/chain.py` | the only file that could break the frozen semantics |
| `tests/` | 93 focused tests, including `test_p6c_claims.py`, which re-derives every documented headline number from the artifacts |

## 11. Repository state

* **Nothing committed, nothing pushed.** The worktree carries exactly two
  untracked directories: `level4/closure_proofs/p6_safe_rebaselining/` (this
  campaign) and `level4/closure_proofs/p6_safe_rebaselining_predesign/` (the
  frozen design phase).
* `git diff --name-only HEAD` is **empty**. `HEAD = bb03c0ea`, the authoritative
  P5 checkpoint. 2,907 tracked files outside the P6 namespaces, all
  byte-identical; manifest SHA-256 in `results/protected_tree.json`.
* **One P6-owned file outside this directory was edited**: the pre-design's
  `tests/test_scope.py`, whose namespace constant was widened from one P6
  namespace to two. The assertion's semantics are unchanged and the edit is
  recorded in `P5_TO_P6_DEPENDENCY_AUDIT.md` section 5.
* **P5's frozen gate G20** was already `FAIL` at P5 adjudication because the
  root `README.md` and the P6 pre-design existed. This campaign adds a third
  item to the same already-failed conjunct. It is not a new P5 regression.
* No P4 or P5 file was modified. No repository-wide verification was run;
  that belongs to adjudication.

## 12. If the verdict is not CLOSED

The campaign is written to survive a narrower verdict without rewriting:

* If **T6-B** is rejected, every stationary statement about SAW reverts to its
  finite-horizon estimator — which is what the code computes anyway — and the
  empirical results are untouched.
* If **T6-C** is rejected, SAW becomes an empirically-calibrated rule rather
  than a derived one, the novelty position weakens from "theoretical" to
  "integration", and the empirical results are untouched.
* If the **cost model** is rejected, the matched-cost claim must be restated on
  whatever model replaces it; `FreshProp` is already reported as the one
  alternative that was run.
* If **`G-E`'s defect** is judged disqualifying, the correct classification is
  `PARTIAL`, with `G-A`, `G-B`, `G-C/C'` and `G-D` standing.
