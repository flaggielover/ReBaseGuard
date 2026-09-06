# P4Z Phases 19–20 — feasibility verdict and successor checkpoint

```text
P4Z_VERDICT = P4Z_READY_FOR_NUMERICAL_QUALIFICATION

P4_ORIGINAL_VERDICT      = PARTIAL     immutable, untouched
P4X_SUCCESSOR_VERDICT    = as recorded on its own branch, untouched
P4Y_OUTCOME              = DO_NOT_FREEZE_P4Y, untouched
LEVEL4_GLOBAL_CLOSURE    = NO
P4Z_PRODUCTION_RUN       = NOT LAUNCHED
P4Z_SCIENTIFIC_RESULTS   = NONE PRODUCED
```

## 1. What READY means, and what it does not

READY means the measurement architecture is now capable of **deciding** the
frozen gate on the 8 unadjudicated cells.  P4X could not: its 8 cells satisfied
neither branch of its own precondition.  P4Y could not: Pilot-4 proved that no
affordable reference could measure the precision scale of the historical
estimator at all.

READY does **not** mean the gate will pass.  Checkpoint A §10.1's principle is
inherited verbatim: the 3 % tolerance is not weakened, and if two
purchased-precision estimates disagree materially the gate must be allowed to
FAIL and must be reported as failing.  P4Z adds a third outcome,
`INCONCLUSIVE`, with an explicit definition, so that the P4X state of "neither
branch applies" cannot recur.

READY does not claim, and nothing here should be read as claiming:

* that historical P4 is repaired — it is not, and P4Z does not touch it;
* that P4 is CLOSED — it is `PARTIAL`;
* that P5Y is CLOSED, or that Level 4 is closed — neither is;
* that anything here is production ready.

## 2. The READY criteria, one by one

| criterion | status | evidence |
|---|---|---|
| exact theorem preserved | met | `GENERAL_LOCATION_THEOREM_AUDIT.md`; the inherited tree `eede9038` is unmodified and hash-locked by test |
| exact estimand preserved | met | `configs/estimand_contract.json`; `CANDIDATE_ESTIMATORS.md` §4 validity audit, 12 checks, both candidates |
| primary estimator mathematically valid | met | RB identity derived from the tower property on `F_{n-1}`; exactly unbiased; every moment finite by the bounded-survival lemma plus discharge lemma L1 |
| old failure mode addressed | met | measured VRF 75x to 10 668x on the unresolved cells; Hill 1.5 → 3.5–4.1; top-1 share 0.975 → 0.006 |
| tiny pilots consistent with the model | met | measured relSE *tighter* than predicted on both checked cells; two-sample `z` against the historical record 0.06–2.61 across 12 comparisons, all under 4 |
| sample complexity plausible | met | 6.1573 projected CPU-h against a 12.0 cap, worst configuration 1.339 against 2.0, with x4 variance and x3 CPU safety factors already applied; P4X spent 24.7493 and did not close |
| campaign governance fully frozen | met | `CAMPAIGN_GOVERNANCE.md` §§2–6, frozen in this commit before any result-bearing byte |

## 3. Residual risks, named

None of these is a reason to withhold READY; all are handled by a prespecified
kill gate or by `INCONCLUSIVE`.

1. **19 of 24 configurations were never piloted.**  `laplace`, `logistic` and
   `skewnormal4` sit on the gaussian regime envelope.  Handled by Stage 0 and
   kill gate `K3`.
2. **`skewnormal4` is the least-exercised analytic branch** — the only
   asymmetric family, and the only one whose `Mlow` is not elementary.  Its
   closed form is verified against quadrature to `1e-7`, but only at
   development time.  Handled by kill gate `K1`, which re-validates every
   family's four integrals against quadrature at run time before any block.
3. **`|z| <= 4` becomes the binding gate at P4Z precision.**  At relSE ~0.002 a
   residual 1 % systematic between routes fails `z` while passing `rel`
   comfortably.  This is a property of the frozen gate, not of any estimator,
   and P4Z does not touch the threshold.  Handled by fixing 200 blocks per
   route (so the SE is itself trustworthy) and by making Route B's uncertainty
   carry its Richardson truncation residual `T_B` — an honest widening, not a
   loosened threshold.  If the gate still fails, it fails.
4. **RB-MAP is less independent than the historical Route B** — it uses `f` and
   `F` analytically.  Disclosed in `CANDIDATE_ESTIMATORS.md` §3.4; partly
   offset by the Route-Q and Corollary-G2 controls of Phase 17.
5. **Both routes share the analytic TCB.**  Handled by kill gate `K1` and by
   the fail-closed producer gate.

## 4. The checkpoint

```text
CHECKPOINT              P4Z_CHECKPOINT_1
STATUS                  FROZEN.  Binding on any P4Z production run.
                        Binding on nothing historical.

THEOREM
  source                level4/closure_proofs/p4_theory_generalization
  tree object           eede90383da44c250871b1bb97d12045c897c8d9
  THEOREM.md blob       1fd9c35ae69f273c0acb2aad7106787a53b08a7e
  PROOF.md blob         3af5d735927623af1026b25a9414ff9bc6152350
  protocol blob         4f2b560ba119f072841efd26c2da40f068c741e0
  protocol sha256       2afa247e986f7c4ff063bf2bda60386a9783d001244821e7eb5aff12db03e627
  witness sha256        8c8173f708d2945608ec6c063d8494aec6772676a45890c0ed81069b0481ea15
  MODIFICATION          NOT PERMITTED

ESTIMAND
  Gamma_{D,m,f} = E_0[ A_m S_tau^psi ]        Theorem G1a, unchanged
  one scalar per (layer, detector, family, m); 96 theorem-supported cells
  contract              configs/estimand_contract.json
                        sha256 e04f5a6be23e3867e13be838ba6c74d5dd7993072f6455eddd329453b3802019

ESTIMATORS
  PRIMARY   RB-SCORE    src/rebaseguard_p4z/rbscore.py
                        sha256 981f4f09ed17c7afac59e81680128e882a9ee392e93254504d0227660351d975
  FALLBACK  RB-MAP      src/rebaseguard_p4z/rbmap.py
                        sha256 8166946145d82d5049665d78a80ff43d705d4e40f6b0d326af9d8de1e1648ec3
  CONTRACT  analytic    src/rebaseguard_p4z/analytic.py
                        sha256 71e576e2ad218801dbee80ebfbf0108e10b0128549e6500404ac813ac1ffc111
  REJECTED              historical Route A (F-01), historical Route B (F-02),
                        reflection-antithetic, Corollary-G2 control variate,
                        coarse FD step, fine FD step

SEED POLICY             rb_score 4090001, rb_map 4090002, neutrality 4090003,
                        fd_ladder 4090004, quadrature 4090005
                        stream_counter(batch, step) = ((batch<<32)|step) * 2^64
                        inherited verbatim; no worker/pid/shard/schedule input

BUDGET                  TOTAL_CPU_CAP             12.0 CPU-h
                        PER_CONFIGURATION_CPU_CAP  2.0 CPU-h
                        projected                  6.1573 CPU-h
                        projected worst config     1.339  CPU-h
                        blocks per route           200, fixed

STOPPING RULE           NON-ADAPTIVE.  200 blocks, then stop.  No top-up, no
                        second stage, no precision trigger, no post-hoc
                        extension.  This is the repair of F-04 and F-05.

GATE THRESHOLDS         relative <= 0.03      UNCHANGED
                        |z| <= 4.0            UNCHANGED
                        r* = 0.010823063      UNCHANGED
                        Route Q 1e-6          UNCHANGED
                        FD steps (0.05, 0.025), per-batch Richardson  UNCHANGED

UNCERTAINTY RULE        SE_A = MC batch SE
                        SE_B = hypot(MC batch SE, T_B)
                        T_B  = |R(0.2,0.1) - R(0.05,0.025)|, rounded outward
                        PASS / FAIL / INCONCLUSIVE as CAMPAIGN_GOVERNANCE.md §4

KILL GATES              K1..K9, CAMPAIGN_GOVERNANCE.md §6
                        none reads a discrepancy, a z, a sign of disagreement,
                        or whether a cell is close to passing

PRODUCER CONTRACT       CAMPAIGN_GOVERNANCE.md §3; fail-closed; exact path TCB;
                        no lazy-import gap; no broad swallowed exception;
                        runtime and backend identity bound; deterministic
                        scientific hash over all scientific fields; exact resume
                        identity; no stale producer admission

PILOT PLAN              Stage 0: 20 blocks per configuration, all 24, to check
                        the variance model and fire K3/K4 before the budget is
                        committed.  Stage 1: the remaining 180 blocks.
                        Stage 0 reads variance and cost only.

FULL-RUN COMMAND        NOT AUTHORISED BY THIS CHECKPOINT.
                        When authorised, and only on a host not held by the
                        CUSUM campaign:
                          OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
                          MKL_NUM_THREADS=1 python production/run_p4z.py \
                            --checkpoint configs/checkpoint_p4z.json --stage 0
                        `production/` does not exist in this commit, by design:
                        a checkpoint that ships a runnable production driver
                        invites the run.

NO-RESULT-CHANGE GOVERNANCE STATEMENT
    P4Z produces no scientific result artifact and changes no historical
    verdict.  P4 remains PARTIAL.  P4X and the four P4Y pilots remain exactly
    as their own branches record them.  No PARTIAL, FAIL or INCOMPLETE is
    converted to PASS.  No frozen numerical gate is relaxed.  Every threshold
    above is inherited unchanged, and the only precision number P4Z chooses
    (0.0025) is *tighter* than the frozen r*, which is not a threshold change.
```

## 5. Exact next action

Formalise the bounded-survival lemma (`CORRESPONDENCE_AND_FORMAL_PLAN.md`
§2.2), write `production/run_p4z.py` against this checkpoint, and **request
authorisation** for the Stage-0 pilot — to be scheduled only after the CUSUM
Aux4 campaign releases the 4 physical cores of the authoritative host.
