# P5Y pre-compute governance and theorem resolution (K2–K5, CUSUM successor)

**No result-bearing computation.** No certified value was computed, and no K1 production value was read. The live AWS campaign was not touched. The only executed arithmetic was:
- float sanity checks of closed-form Gaussian constants and the cap formula;
- one hash-equality check of the T4 integrity function on a committed non-production control record;
- unit tests on synthetic fixtures.

```text
K2_ANALYTIC_ROUTE                       = PASS_POSSIBLE     (Lemma K2-A: S_{D,m}(e) >= kappa_D/m^2 > 0, explicit, exact)
K2_MINIMAL_NEW_COMPUTE                  = NONE              (optional two-point rigorous evaluation of u(G_D) for the value)
K3_BINDING_USEFULNESS_CRITERION         = M_2(D,m) < inf    (already discharged: M_2 <= C_D, P5-T5/P5-T4)
K3_CRITERION_DERIVATION                 = back-solve of every frozen consumer (P5X-T6, P5X-T9(4), G4, G9/E3, Lean X2):
                                          none uses a quantitative M_2
K3_READY_TO_FREEZE                      = YES               (governance record for independent adjudication)
K4_CHECKPOINT_READY                     = YES               (FROZEN: K4_ASSEMBLY_CHECKPOINT.json sha256 95b1fd16...)
K4_NEW_COMPUTE_REQUIRED                 = NO
K4_WAITING_ONLY_FOR_COMPLETE_K1_INPUTS  = YES
K5_BINDING_TARGET                       = H3a (P5 THEOREM.md verbatim; P5X-T7(2) not substituted)
K5_THIRD_ORDER_CERTIFICATE_SUFFICIENT   = UNRESOLVED        (exact near 0 via Lemma K5-L; global closure depends on
                                                             unobserved K1 widths)
K5_MINIMAL_NEW_COMPUTE                  = certified R''' cell enclosures, m in {1,2,3,5}, 256 bits, on the frozen K1 cover
                                          cells meeting (0,2] (SR 0-294, CUSUM 0-309); gated by a predeclared
                                          feasibility oracle (SR {0,207,294}, CUSUM {0,221,309}); est. SR 1,500-2,870 CPU-h,
                                          CUSUM <= ~124 CPU-h (unmeasured)
CUSUM_RECOMMENDED_ROUTE                 = NEW_SUCCESSOR     (rebaseguard-vultr-02)
CUSUM_SUCCESSOR_REQUIRES_REPRODUCING_EXISTING_2_CELLS = YES
CUSUM_PROJECTED_CPU_HOURS               = 205.6 mean / 206.3 worst (Aux4-host basis; requalify on successor host)
CUSUM_PROPOSED_CPU_CAP                  = 300 CPU-h
CUSUM_CAP_DERIVATION                    = ceil_50(1.15*(1.10*N*c_max + W*R + 0.03*N*R + 0.02*1.10*N*c_max)), R = ceil_0.5(1.25*c_max)
CUSUM_READY_FOR_PREFREEZE               = YES
NEW_RESULT_BEARING_COMPUTE              = NONE
LIVE_AWS_CAMPAIGN_TOUCHED               = NO
```

| document | content |
|---|---|
| `K2_ANALYTIC_ROUTE.md` | full proof of Lemma K2-A; a rejected (numerically false) Mills-ratio shortcut; the frozen "order of magnitude" corollary shown unattainable for m = 5 |
| `K3_USEFULNESS_BACKSOLVE.md` | consumer table; weakest sufficient criterion; the alternative quantitative reading and why it forces C2 compute |
| `K4_FREEZE_AUDIT.md` | validity audit, the strict-domain amendment, signed-enclosure admissibility (corrects the prior "magnitude only" wording), freeze |
| `K5_TARGET_AND_THIRD_ORDER.md` | dated precedence ruling; expansion `R = a1 e + a3 e³ + …`; Lemma K5-L; Z1/Z2/Z3 chain; minimal design and feasibility risk |
| `CUSUM_SUCCESSOR_PREFREEZE.md`, `config/CUSUM_SUCCESSOR_PREFREEZE.json` | Route A vs B, host binding, 2-cell reproduction, cap formula with reserve evidence, requalification rule |
| `../p5y_k2k5_postk1_audit/config/K4_ASSEMBLY_CHECKPOINT.json` | frozen K4 procedure, schema, domain, integrity, disposition mapping, bound source hashes |

## Decisions still reserved for independent adjudication or the operator

1. K2: accept an EXACT explicit constant as satisfying G4's "certified `s_min`".
2. K3: supersede the THEOREM_ADJUDICATION "tight bound" reading, or uphold it, which forces C2 compute for both `s_min` and `M_2`.
3. P5X text defects: the "order of magnitude" corollary (unattainable for m = 5) and the literal P5X-T7(2) (false for L > sup s).
4. K5: authorise the feasibility oracle; SR third-order architecture risk (Aux3 SR `FEASIBILITY_FAIL` at the same C·ρ).
5. CUSUM: build the successor identity layer and freeze the prefreeze record; approve the qualification runs (cells 318, 323).
