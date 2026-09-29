# Firewalled reader A: cell-309 provenance (hand-back, condensed layout, no 305–309 numbers)

The reader was read-only. It found no cell-308 formal ref or directory. Its exposures are ledgered.

## A. Authoritative status

* **r5** (blob f978eeb6, committed at ae4cbc2c): m=5 cell 309 has verdict OPEN, primary INTERVAL_WIDTH, region TAIL,
  zone SCALAR_ONLY, and flags [H_BOUND, CURVATURE_SLACK, THEOREM_DOMAIN]. union_open [[306,309]]. There is no r6.
* **C4** (e12a09e8) is ACCEPTED_WITH_SCOPE_LIMITATION, with EXCLUDED CELL SET [309] (C4_ADJUDICATION:490, 514-516;
  scope :496-503).
* **C5** Condition 1: the C4 scope sentence must be restated under C5-T (C5_ADJUDICATION:549-556).
* **C7** C7_CLASS is STRENGTHENED (a certified Λ_309 lower bound), ACCEPTED_WITH_CONDITIONS (df4ec179).
* **C8** (C8_ADOPTION.json:6): "MATHEMATICALLY_REFUTED_WITHIN_SCOPE; the escape route is BLOCKED, not refuted"
  (63a3f825).
* **Route audit r1** (ROUTE_AUDIT_R1:289-309, accepted 2f36352e): REFUTED WITHIN SCOPE; UNKNOWN outside the scope;
  F1′ UNAVAILABLE.
* **Handovers.** The overnight report gives 309 as OPEN and not FREEZE_READY. The 307 final report gives 309 as
  untouched and says "do not apply RLR to 308 or 309".
* **Programme.** K5 is PARTIAL and P5Y is NOT_YET_CLOSED. The closeout wording "OPEN; refuted only within C4
  Condition 1's scope" is not authoritative, because all three closeout freezes were rejected.

## B. Certificates, supplies and evaluations that touched 309

1. Feasibility 6f1d351b (probe set {0,221,309}), never run.
2. Sealed K1 Aux5 record for 309 (R, D, R2, M_R2, C_upper), record sha 95be4c65…; C6 caps its provenance at P3.
   Premise binding 10769e07: the PB6 gate R(2) > −2 passes on 309.
3. Readiness audit e8680998: K1-only K5-B shows 305–309 failing the direct clause (reproduced by E6, ff3b6a4a).
4. Frontier consumptions:
   * first probe 84299314;
   * T-EXT a3547b9b;
   * Perron-deflated 7cb01e38 (map r3);
   * Campaign A TC f2ac1eb3 (map r4).

   All left 309 open; the tail is outside the deflation domain.
5. Campaign B (78b065e1 → ae153a69): the replay measurement TCT_INPUTS_309 and TC-T (Lemma G, Ĝ := 0, (P3′)). The
   direct-clause forecast does not close 309. Route T2 (real order-3) was refuted and the campaign STOPPED before the
   freeze.
6. C1 (ee1e4385 / 4ccee386 / 5289b6ce): REGISTRY_C1 (Arb/FLINT taboo_certify) at 309; a Dv′ supply through TC-T and
   the direct clause leaves it open (MARGINAL); STOP.
7. C2 (seal e644bcb5, adjudication ae4cbc2c): REGISTRY_C2 and S_I1 = min{Lemma G, C1, C2} under the direct clause.
   309 is open (D_PARTIAL); only [305] was adopted.
8. C3 (seal e815a217, adjudication 019ecce0): operator-mixed D′ supply; 309 open; REJECTED (empty set). Knockout, see C.
9. C4 (e12a09e8): a Theorem L lower bound on E_a[τ] at e_lo(309) in exact rationals. Consumer evaluated at (B,0,0).
   EXCLUDED [309].
10. C5 (8b2be7ab, 69bff424): C5-T forecast at 309 under D′ (MARGINAL); the transport family is EXHAUSTED.
11. C6 (f494416f): forensic; recovered 309's record (P3).
12. C7 (511a3c92, df4ec179): four certified lower bounds on Λ_309. The PRIMARY (L3-elementary) has an empty
    dependency set.
13. C8 (d58176ae, 63a3f825): counterfactual oracles at 309 are COUNTERFACTUAL_ONLY / DIAGNOSTIC.

Campaigns that did not touch 309: C9–C12-R2, floor r2, overnight (0 Γ309) and 307 RLR (0 Γ309).

## C. Committed negatives and their exact scope

* **C1 MARGINAL.** One Dv′ supply through TC-T and the direct clause. Atom deflation buys little on A0 at the tail;
  Ā is inert.
* **Campaign B T2.** The USEFUL class for a real order-3 candidate was refuted under the frozen K5-B. It hinges on the
  centre motion ρ|Ĝ(a)|.
* **C2 D1 finding 3.** "No plausible operator tightening closes cell 309": A0 = τ/D_lo ≥ τ, a genuine hitting time.
* **C3 knockout.** The operator-mixed D′ supply at its certified A0, with A1 = A2 = 0, under the frozen TC-T/K5-B
  direct clause and the frozen inputs, leaves Γ > 0 at 308 and 309. The adjudicator says this is not exhaustion: no Λ
  floor existed yet.
* **C4 exclusion (Condition 1).**
  * Scope: every atom-constant triple whose A0 is a valid **uniform** order-0 bound on the closed cell, consumed
    through the frozen TC-T and the frozen direct clause, at the frozen inputs, at 309.
  * `does_not_cover`: **residual-specific (non-norm-only) order-0 bounds**; any change to TC-T, the clause or the
    inputs; order-3 candidates.
* **C5 restatement.** The exclusion survives under C5-T, but thinner. Condition 2: no restatement without re-deriving
  it under one's own clause, or E2 (done by C7).
* **C5 transport exhaustion.** Only transports that use exactly g_hi and a whole-cell [H_lo, H_hi]. "Exhausts the
  transport, not the cell."
* **C7 E2 family ceiling.** Exclusion direction only.
* **C8.**
  * R1 and R2 have zero leverage, and R3/E1 cannot close 309.
  * The refutation holds within the atom-constant family at the committed sup norms.
  * R5 (sup norms) voids it but is DATA_BLOCKED.
* **C5 route ledger.**
  * A5 (σ3) and A6 (σ4) are refuted at 308/309 only.
  * B2 was killed as NEW_REAL, later narrowed to the fixed-(g_hi, L, U) family.
* **Overnight scoped families** F1–F7 (SCOPED_NEGATIVE_FAMILIES_309 §1).

## D. Known bounds, stated symbolically

* **A0 floor.** Any admissible A0 ≥ Λ_309 := sup_{e∈C309} E_a[τ](e) (Lemma SM(d)). By Theorem M the sup sits at e_lo.
  The certified lower bounds on Λ come from Theorem L (C4) and C7-E2. There is no certified UPPER bound on Λ_309.
* **Supply upper bounds.** Lemma G: A0 = C_upper, A1 = k1C², A2 = k2C² + 2k1²C³. Dv′: A0 = eff = min(Ā, τ/D_lo).
* **Knockout inequality.** With A1, A2 ≥ 0, Γ ≥ g_hi + ρx_hi(|C_lo| + Λ_309·P̄2), which is ≥ 0 at 309 under the direct
  clause and under C5-T. Monotonicity in A_i holds while 𝓗 ∩ R2 ≠ ∅.
* **Transport optimality.**
  * C5-T is minimax-optimal for its two-input family.
  * TPT-O: g_hi + P* is the sup over C² functions consistent with (g_hi, L, U).
  * CR-3: real refinement into N removes 1 − 1/N^j of the order-j slack.
* **Tightening routes.**
  * SC: f_G^SC ≤ f_G^sur, strict only for exact sups.
  * RSO: the gain factor ‖ψ‖/μ_a(ψ) ≥ 1; it collapses to F1 for constant ψ.
* **Domain.** K5-B-T (TAIL_DESIGN, design only) would restrict the test to [x_lo, 2], removing THEOREM_DOMAIN.

## E. Routes proposed for 309, and their disposition

| route | disposition |
|---|---|
| K1-only direct clause | failed |
| probe {0,221,309} | never run |
| K5-B-T sub-cell points | design, deferred |
| T1 AD tightening | INFEASIBLE |
| T2 real order-3 | refuted, STOP |
| T4 finer cover | INFEASIBLE (governance) |
| C1 registry | MARGINAL |
| C2 D-stage | insufficient |
| D′ | insufficient |
| R-stage R-b | design, blocked |
| C4 Λ lower bound | succeeded as exclusion |
| C5-T | adopted, closes nothing |
| A1 sup-norm | DATA |
| A3 cancellation | DATA plus theory |
| B1 cover refinement | NEW_REAL, the largest lever |
| E1 operator certification | cannot close 309 |
| E2 Λ floor | STRENGTHENED (exclusion) |
| R4 real order-3 | NEW_REAL_BLOCKED (a "perfect order-3" diagnostic closes but is unattainable) |
| R5 sup norms | DATA_BLOCKED |
| **RSO** | DEFER (research); **"reach is narrow alone (A0·f_H only)"** |
| R-asm | DEFER |
| Architecture D | rejected three times |
| SC | VALIDATED_NON_TARGET, data-blocked |
| CR | BLOCKED (NEW_REAL) |
| B2c | THEORY_ONLY |
| TPT | sound, tail use BLOCKED (incident 01) |
| TPT-B | negligible |
| Corollary-T g_hi | inventory only |
| RLR | cannot close 309 (C3 knockout) |

Reader's inference: overnight §M's "C2b A0 plus RLR for 309" is inconsistent with F1, because A0 is floored by Λ_309.

## F. Temporal-integrity record

**Earlier campaigns:**
* C1: gate defect caught before the freeze.
* Campaign B: the T2 forecast was arithmetically wrong.
* C2: README edited post-hoc; the 306 floor was judged after the result.
* C4: the freeze was RETROSPECTIVE; c9b06abf held the final 309 numbers before gate 376950be (erratum E2).
* C5: the transport code landed 20 s before the gate (disclosed).
* C7: the gate was frozen after exploratory evaluation; E1, E4 and E6 errata (KG8 narrowed in its favour).
* C8: gate before results; N8.

**Overnight:**
* Incident 01 (4403f86f → 2f0fb5e1; residue F13 → eb55bcab).
* Incident 02, which directly involves 309: a re-attribution of C7's 309 floor at the shared endpoint to 308,
  withdrawn at 0d32a2e8. It led to R2.4.
* Incident 03: 308 only. L6: 306 only.

**What predates what.** All C1–C8, C10, route-audit and floor-r2 evidence predates the overnight incidents.

**This campaign.** 309R1-01 (1f6b724a) and 309R1-02 (daa1bd64).

## G. Consumer dependence (qualitative)

* The failure is curvature/width slack: g_hi is negative but small against ρ·x·M, and 309 is the extreme of the tail
  trend.
* g_hi is sealed; only M is improvable under the frozen clause.
* **The A0·P̄2 term dominates S̄.** Within p2, ρf_G (the order-3 surrogate) dominates and ρ²Env4/2 comes second.
  f_F, f_D and f_H are negligible. At r = 4 on 308/309, the Env4 remainder overtakes the order-3 term.
* |C_lo| is small, the A1 terms are small, and A2 is negligible. Ā is inert; C_T has almost no headroom.
* 309's critical A0 is driven by the candidate sup norms (which feed f_G and Env4) and by ρ; residuals barely move it.
* Under C5-T the rightward branch binds. THEOREM_DOMAIN applies because K5-B is cell-granular beyond e = 2.

## H. User decisions and blockers

* U1: certifying host (C6 Condition 7; no host has numpy or flint).
* U2: P3 admissibility (C6 Condition 10).
* U3: floor extension.
* The guard is DENY; N1, N3, N5 and N7 are open.
* There is no I2 for 309, so F1′ is UNAVAILABLE.
* Incident disclosure is a precondition for TPT.
* C5 Condition 2 applies.
* The closeout is unfrozen.
