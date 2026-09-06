# P4Z Phases 11–16 — the successor campaign, frozen before any result

Nothing in this document may be amended after a scientific value is seen.

```text
PRIMARY_ESTIMATOR   = RB-SCORE   (Rao-Blackwellised score route, Candidate A)
FALLBACK_ESTIMATOR  = RB-MAP     (Rao-Blackwellised conditional-mean map, Candidate B)
REJECTED_ESTIMATORS = historical Route A, historical Route B,
                      reflection-antithetic, Corollary-G2 control variate,
                      coarse finite-difference step, fine finite-difference step
```

## 1. Phase 11 — the selection gate

`RB-MAP` is called a *fallback* in the sense of the brief: it is the retained
second method.  In the campaign it is not idle — it is the **second official
route of the frozen two-route correspondence gate**, exactly as the historical
Route B was.  The gate has always compared two routes and P4Z does not change
that.  "Primary" means: if the two routes disagree, RB-SCORE is the estimate of
record for every purpose other than the gate itself, and the gate is allowed to
fail.

| criterion | RB-SCORE | RB-MAP | why RB-SCORE is primary |
|---|---|---|---|
| exact estimand match | exact | exact | tie |
| governance defect | none | none | tie |
| plausible gate closure | relSE 0.0008–0.0043 at 320 000 paths | relSE 0.0017–0.0075 at 160 000 paths | RB-SCORE, by 2–4x |
| stable variance | every moment finite; measured Hill 3.3–4.6, top-1 0.003–0.012 | every moment finite; measured Hill 3.4–5.8 | tie in class, RB-SCORE tighter |
| cost plausibility | 0.91 CPU-h for the whole 24-configuration grid | 4.89 CPU-h | RB-SCORE, by 5x |
| implementation simplicity | one path per estimate | four coupled paths (2 shifts x 2 steps) per estimate | RB-SCORE |
| independent replayability | seed-deterministic, single stream | seed-deterministic, frozen Philox `(seed, batch, step)` stride `2^64` | tie |
| independence from the identity under test | **uses** `psi` and G1a | does not use `psi` or G1a | RB-MAP — the one criterion RB-SCORE loses |

RB-SCORE is primary on six criteria, ties on three, and loses one — the one
that is precisely why RB-MAP is retained rather than discarded.

**Rejections, with cause.**  Historical Route A: finding F-01, infinite second
moment for `t1p5`, measured Hill 1.5–1.6 and top-1 share up to 0.975.
Historical Route B: finding F-02, rare-event estimator of a heavy-tailed jump,
2.255e9 paths for relSE 0.0062.  The four P4X R0 candidates: measured and
rejected in R0, reasons in `OLD_ESTIMATOR_DIAGNOSIS.md` §3; P4Z re-derived the
fine-FD rejection independently and agrees.

## 2. Phase 12 — execution architecture

```text
SCOPE                   exactly the historical P4 theorem-supported scope.
                        2 layers x 2 detectors x 6 families x 4 m = 96 cells.
                        Not broadened.  Not to be narrowed after results.
                        OUTSIDE-ASSUMPTIONS cells: NEW COMPUTE = NONE.
                        Their evidence is P4X's C4, which is already PASS.

PATH BUDGET             per (layer, detector, family, route):
                          blocks      = 200          FIXED
                          block_paths = from results/estimator_feasibility.json
                          total paths = 200 * block_paths
                        The four m of a configuration share their paths, as in P4.

CPU BUDGET              TOTAL_CPU_CAP             = 12.0 CPU-hours
                        PER_CONFIGURATION_CPU_CAP =  2.0 CPU-hours
                        projected total 6.1573 CPU-h (route A 0.9389, B 5.2183)
                        cap = 1.95x the projection; P4X used 24.75 of 60.

SEED POLICY             master seeds, disjoint from every historical P4/P4X seed:
                          rb_score  4090001
                          rb_map    4090002
                          neutrality 4090003
                          fd_ladder  4090004
                          quadrature 4090005
                        Per-cell stream address = the frozen Philox rule
                        stream_counter(batch, step) = ((batch<<32)|step) * 2^64,
                        inherited verbatim, with a per-configuration base offset.
                        No worker id, pid, shard index or schedule enters a seed.

SHARDING                permitted, scheduling only.  A shard runs the identical
                        estimator at the identical block size with its own
                        Philox address; shards pool as blocks.  Total N, block
                        size, estimator, precision rule and gate unchanged.
                        Shard-sum invariant tested (P4Y's regression, reused).

RESUME IDENTITY         a resumed run must reproduce, bit for bit, the blocks a
                        single run would have produced.  Resume key =
                        sha256 over (protocol hash, estimator source hash,
                        analytic-contract hash, configuration, route, seed,
                        block index).  A block whose key does not match is
                        discarded, not adapted.

STOPPING CONDITION      NON-ADAPTIVE.  Every configuration runs its frozen 200
                        blocks and stops.  There is no top-up, no second stage,
                        no precision trigger and no cap-driven early exit.
                        This is the direct repair of findings F-04 and F-05:
                        a rule that cannot be triggered cannot leave a cell in
                        an unadjudicable state.

NO OVERRUN              a configuration projected to exceed its 2.0 CPU-h cap
                        at plan time is declared BUDGET_EXCLUDED *before the
                        run*, from the frozen cost model alone, and its cells
                        are reported INCONCLUSIVE.  A running configuration
                        that crosses the cap is killed and reported
                        INCONCLUSIVE.  Neither event may be repaired by
                        re-planning after the fact.

INCONCLUSIVE            an INCONCLUSIVE cell is reported as INCONCLUSIVE in the
                        verdict.  It is never counted as a PASS, never dropped
                        from the denominator, and never re-run under a
                        different budget within the same campaign.
```

Adaptive precision allocation is **not permitted**.  It was the mechanism of
F-04 and F-05, and the RB construction removes the need for it: the required
sample size is now predictable from a variance that exists.

## 3. Phase 13 — producer and provenance

Taken directly from the P5Y/CUSUM lessons.

```text
IMMUTABLE PRODUCER MANIFEST
    one manifest, written before T2, listing every path in the TCB with its
    git blob hash, and never rewritten.

EXACT PATH-BASED TCB
    p4z_location_family_feasibility/src/rebaseguard_p4z/{__init__,analytic,
        rbscore,rbmap}.py
    p4_theory_generalization/src/rebaseguard_p4_general/{detectors,families,
        simulate}.py                       [inherited, read-only]
    p4_theory_generalization/configs/P4_PROTOCOL.json   [inherited, read-only]
    p4z_location_family_feasibility/configs/{estimand_contract,
        checkpoint_p4z}.json
    Hashed by `git ls-tree --full-tree`, not by a directory walk.

NO LAZY-IMPORT GAP
    every module in the TCB is imported at producer start-up and its resolved
    __file__ is compared against the manifest.  An import that resolves outside
    the manifest is fatal.

NO BROAD SWALLOWED EXCEPTION
    no `except Exception` anywhere in the producer.  The analytic contract
    raises ValueError for a family without a first moment and for an empty
    survival interval; both are fatal, not skipped.

FAIL-CLOSED FINAL PRODUCER GATE
    the certificate is written only if every gate evaluated True.  Absence of a
    gate is a failure, not a default-pass.  A missing artifact is fatal.

RUNTIME AND BACKEND IDENTITY
    python version, numpy version, scipy version, BLAS backend, platform,
    thread count (must be 1) recorded and bound into the scientific hash.

DETERMINISTIC SCIENTIFIC HASH
    sha256 over the canonical JSON of: estimand contract, protocol hash,
    estimator source hashes, analytic-contract hash, seed policy, budget,
    per-cell block values.  All scientific fields bound; no field excluded.

SOURCE-CERTIFICATE CONTENT HASHES
    the inherited P4 protocol and witness are bound by content hash
    (2afa247e... and 8c8173f7...), not by path.

NO STALE PRODUCER ADMISSION
    a block whose producer hash differs from the manifest's is discarded.
```

**One new obligation, specific to P4Z.**  The analytic triple `(f, F, Mlow)` is
new load-bearing input.  The producer re-validates all four alarm-set
integrals against adaptive quadrature, for every family in scope, at run time,
before any block is produced, at a tolerance of `1e-7`.  Failure is fatal.
This is the fail-closed guard on the only genuinely new part of the TCB.

## 4. Phase 14 — the same thresholds, certified differently

**No scientific threshold changes.**  `0.03`, `|z| <= 4`, `1e-6` for Route Q
and `r* = 0.010823063` are inherited exactly.

What changes is how the certificate is computed.

```text
ESTIMATES        e_A  = mean of 200 RB-SCORE block means
                 e_B  = mean of 200 RB-MAP  block means (Richardson-combined
                        per block, frozen (0.05, 0.025))

UNCERTAINTY      SE_A = sd(block means) / sqrt(200)                    [MC only]
                 SE_B = sqrt( (sd(block means)/sqrt(200))^2 + T_B^2 )
                 T_B  = the Richardson truncation residual bound

TRUNCATION BOUND T_B is estimated from the frozen FD ladder run once per
                 configuration at h in {0.2, 0.1, 0.05, 0.025}: fit the O(h^2)
                 coefficient from the (0.2, 0.1) pair and report
                 T_B = |R(0.2,0.1) - R(0.05,0.025)|, the observed drift of the
                 Richardson value across a 4x change of step.  Rounded OUTWARD.

                 Rationale: the historical |z| <= 4 gate divided by Monte Carlo
                 error alone.  At P4X's precision the truncation residual was
                 invisible beneath it.  At P4Z's precision it is not, and a
                 statistic that ignores a known deterministic error term is the
                 same defect as finding F-06 in a different place.  Including it
                 makes the uncertainty honest; it does not move the threshold.

STATISTICS       rel = |e_A - e_B| / max(|e_A|, |e_B|)
                 z   = |e_A - e_B| / sqrt(SE_A^2 + SE_B^2)

PASS             rel <= 0.03  AND  z <= 4.0
                 AND both routes reached relSE <= r* on their own MC error
                 AND both routes' scale-stability diagnostics passed (below)

FAIL             rel > 0.03  OR  z > 4.0, with both routes' preconditions met.
                 A FAIL is reported as a FAIL.  Checkpoint A section 10.1's
                 principle is inherited verbatim: the gate must be allowed to
                 fail.

INCONCLUSIVE     any precondition unmet: a route missed r*, a scale-stability
                 diagnostic failed, a kill gate fired, or the configuration was
                 BUDGET_EXCLUDED.  Reported as INCONCLUSIVE.  Never a PASS.

SCALE STABILITY  per route, per configuration, inherited from P4Y Pilot-4:
                 top-1 share of squared deviation over the 200 block values
                     <= 0.10
                 top-5 share <= 0.30
                 These are the diagnostics that caught what agreement tests
                 missed.  They are preconditions, not gates on the science.

MULTIPLE COMPARISON
                 none applied, and none removed.  The frozen gate is a
                 per-cell conjunction over 96 cells with no correction, and
                 P4Z inherits it as it stands.  Applying a correction now
                 would loosen a frozen gate.  The 96-cell family-wise error
                 rate under the unchanged gate is reported as a disclosed
                 property, not used to adjudicate.

"ALMOST PASS"    does not exist.  Every cell is exactly one of PASS, FAIL,
                 INCONCLUSIVE.
```

## 5. Phase 15 — power and sample complexity

From `results/estimator_feasibility.json`, built from the micro-pilot by pure
arithmetic with two named safety factors: **x4 on variance** (the pilot sd is a
small-sample estimate) and **x3 on CPU** (unoptimised reference implementation).

```text
DESIGN TARGET     relative SE per route = 0.0025     (r* / 4.33)
CONFIDENCE        the frozen 1.96 * sqrt(2) * relSE <= 0.03 construction,
                  met with a 4.33x margin

REQUIRED SAMPLES  block structure fixed at 200 blocks; block_paths per
                  configuration from the regime envelope:
                    light    (gaussian, laplace, logistic, skewnormal4)
                    moderate (t3)
                    heavy    (t1p5)

                  worst configurations, per route (paths are variance derived
                  and timing independent; CPU is a measured rate):
                    */t3        3 380 400 paths   733 CPU-s (A) + 4 087 (B)
                    */t1p5      5 690 000 paths    93 CPU-s (A) +   516 (B)
                    */light       788 400 paths     5 CPU-s (A) +    23 (B)

PROJECTED CPU     route A   0.9389 CPU-h
                  route B   5.2183 CPU-h
                  TOTAL     6.1573 CPU-h     against a 12.0 CPU-h cap
                  worst configuration 1.339 CPU-h against a 2.0 cap
                  (P4X spent 24.7493 CPU-h and left 8 cells unadjudicated)

PROJECTED WALL    4 workers: ~1.6 h.  1 worker: ~6.2 h.
                  MUST NOT be scheduled while the CUSUM Aux4 campaign owns the
                  4 physical cores of the authoritative host.
```

The variance model is falsifiable: the pilot's per-path relative sd predicts
the block-mean relSE at 200 blocks to within the x4 safety factor, and Stage 0
of the campaign checks that prediction before the budget is committed.

**Named extrapolation risk.**  The pilot covers 5 of 24 configurations.
`laplace`, `logistic` and `skewnormal4` were never piloted and sit on the
gaussian envelope.  `skewnormal4` is additionally the only asymmetric family
and the least-exercised branch of the analytic contract.  Stage 0 must pilot it.

## 6. Phase 16 — kill gates, prespecified

Each is evaluated at a fixed point in the run, on a quantity that is not a
scientific result.  A kill gate ends the candidate honestly and may not trigger
a redesign.

| id | when | condition | action |
|---|---|---|---|
| `K1` | before any block, per family | any of the four alarm-set integrals differs from adaptive quadrature by more than `1e-7` | ABORT the whole campaign; the analytic TCB is wrong |
| `K2` | before any block, per detector | `alarm_bounds` disagrees with the frozen `Detector.step` on any of 10^5 probe residuals | ABORT; the stopping convention is not reproduced |
| `K3` | Stage 0, per configuration, after 20 blocks | measured per-path relative sd exceeds the model's by more than the x4 safety factor | KILL that configuration; report its cells INCONCLUSIVE |
| `K4` | Stage 0, per configuration | projected CPU to complete exceeds the 2.0 CPU-h per-configuration cap | BUDGET_EXCLUDED; cells INCONCLUSIVE, no blocks bought |
| `K5` | after all 200 blocks, per route | top-1 share of squared deviation over the 200 block values `> 0.10`, or top-5 `> 0.30` | that route is not scale-stable; cells INCONCLUSIVE |
| `K6` | after all 200 blocks, per route | achieved MC relSE `> r* = 0.010823063` | precondition unmet; cells INCONCLUSIVE |
| `K7` | per configuration, on the FD ladder | the `(0.2, 0.1)` Richardson value and the `(0.05, 0.025)` value differ by more than `0.02` relative | the truncation model does not hold; RB-MAP is not usable on that configuration; cells INCONCLUSIVE |
| `K8` | continuous | total CPU reaches 12.0 CPU-h | STOP; every unfinished cell INCONCLUSIVE |
| `K9` | continuous | any producer-gate failure: manifest mismatch, import outside the TCB, thread count != 1, stale producer hash, resume-key mismatch | ABORT |

`K3`, `K5`, `K6` and `K7` are evaluated on **precision and stability
statistics only**.  None of them reads a discrepancy, a `z`, a sign of
disagreement, whether a cell is close to passing, or whether the campaign would
close.  That exclusion is the P4X Checkpoint-A §8.1 trigger discipline,
inherited and tightened.

## 7. What P4Z does not authorise

* No production run is launched by this checkpoint.
* No run may be scheduled on a host whose cores are held by the CUSUM Aux4
  campaign.
* No historical P4, P4X or P4Y artifact may be modified, and none is.
* No PARTIAL, FAIL or INCOMPLETE in the historical record is converted.
