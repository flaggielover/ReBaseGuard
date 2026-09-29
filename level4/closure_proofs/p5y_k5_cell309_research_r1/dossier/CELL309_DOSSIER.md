# Cell 309 (CUSUM, m = 5): authoritative reconstruction (Phase 0)

Reconstructed from committed records only. Sources:
* `dossier/sources/READER_A_309_HISTORY_REPORT.md` (firewalled reader A);
* `dossier/sources/READER_B_GOVERNANCE_REPORT.md` (reader B);
* `dossier/digests/*` (sanitized theory);
* the coordinator's own ledgered reads.

This document carries **no 305–309 numeric value**. Every such read is in `ledger/EXPOSURE_LEDGER.jsonl`.

## Start-state verification (from the repository, not from the prompt)

| claim in the instruction | verified | evidence |
|---|---|---|
| cell 307 has scientific closure under RLR, closure-only, not adopted | **yes** | `p5y_k5_cell307_rlr_r1/FINAL_REPORT.md` (b73b9449): CELL307_CLOSED_UNDER_RLR, ADJUDICATION_ACCEPTED; "not adoption in r5 …" |
| cell 308 has a separate formal campaign, out of scope | consistent. **No committed trace** of a 308 formal namespace or ref on origin (ls-remote 2026-09-29) | readers A and B, coordinator |
| cell 309 remains scientifically open | **yes** | r5 entry OPEN (INTERVAL_WIDTH, TAIL, flags H_BOUND/CURVATURE_SLACK/THEOREM_DOMAIN); 307 final report "309 untouched" |
| r5 authoritative, no r6 | **yes** | r5 blob f978eeb6, union_open [[306,309]]; no coverage-map r6 on any ref |
| K5 PARTIAL/open; P5Y not closed | **yes** | 307 final report §S; overnight §L |
| improving A1/A2 alone cannot solve the tail cells | **yes, for 308/309** | committed C3 knockout (C3_ADJUDICATION §K); 307 report "do not apply RLR to 308 or 309" |
| for 309, uniform/operator-constant tightening was insufficient | **yes** | C4 Condition 1 (REFUTED WITHIN SCOPE, uniform-A0 family), restated under C5-T (C5 Condition 1), strengthened by C7, C8 "MATHEMATICALLY_REFUTED_WITHIN_SCOPE; escape route BLOCKED, not refuted" |
| existing work: composite-sup/order-3 surrogate, TPT, cover refinement, sup-norm, genuine order-3, assembly/clause, residual-specific, SC/RSO | **yes** | overnight streams D/E/B; C5 route ledger; route audit |
| SC/RSO lacked candidate data | **yes** | candidate payloads never serialized (0/326, C6); U1/U2 |
| overnight TPT carries incident-01 liability | **yes** | `p5y_k5_tail_overnight_research/ledger/INCIDENT_01_TPT_GRAPH_PROXY.md`; THEOREM_TPT status "BLOCKED (PROXY_EXPOSURE)" |

## A. Current scientific status

**OPEN.**
* r5 lists 309 as OPEN.
* Route-level labels (not coverage changes): C4 EXCLUDED [309] within the uniform-A0 scope; C5 restated it under
  C5-T; C7 STRENGTHENED; C8 MATHEMATICALLY_REFUTED_WITHIN_SCOPE (escape BLOCKED, not refuted); route audit REFUTED
  WITHIN SCOPE / UNKNOWN outside.
* The accepted scoped wording is "OPEN; refuted within scope only" ("not unclosable", C4:503).
* No adoption; K5 PARTIAL; P5Y NOT_YET_CLOSED.

## B. Every historical certificate or supply that touched 309

Chronological (reader A §B):

| # | campaign | commit | object | consumer | outcome |
|---|---|---|---|---|---|
| 1 | feasibility | 6f1d351b | probe set {0,221,309} | — | never run |
| 2 | K1 Aux5 record | 95be4c65 (record sha) | R, D, R2, M_R2, C_upper | — | P3 provenance (C6); PB6 gate R(2) > −2 passes |
| 3 | readiness audit, E6 | e8680998, ff3b6a4a | K1-only K5-B | direct clause | fails |
| 4 | frontier consumptions | 84299314, a3547b9b, 7cb01e38, f2ac1eb3 | T-EXT, Perron-deflated, TC (lower front) | K5-B | 309 open (tail outside the deflation domain) |
| 5 | Campaign B | 78b065e1 → ae153a69 | TCT_INPUTS_309; TC-T (Lemma G, Ĝ := 0, (P3′)) | direct clause (forecast) | not closed; T2 real order-3 refuted; STOP |
| 6 | C1 | ee1e4385/4ccee386/5289b6ce | REGISTRY_C1 (Arb taboo) Dv′ | TC-T + direct | MARGINAL; STOP |
| 7 | C2 | e644bcb5 / ae4cbc2c | REGISTRY_C2, S_I1 = min{Lemma G, C1, C2} | direct clause (sealed D-stage) | open (D_PARTIAL) |
| 8 | C3 | e815a217 / 019ecce0 | operator-mixed D′ | direct clause (sealed) | open; REJECTED; knockout |
| 9 | C4 | e12a09e8 | Theorem L lower bound on E_a[τ] at e_lo | consumer at (B,0,0) | EXCLUDED [309] |
| 10 | C5 | 8b2be7ab / 69bff424 | C5-T under D′ | C5-T | MARGINAL; transport family EXHAUSTED |
| 11 | C6 | f494416f | record forensics | — | none |
| 12 | C7 | 511a3c92 / df4ec179 | four certified Λ_309 lower bounds | — | STRENGTHENED (exclusion) |
| 13 | C8 | d58176ae / 63a3f825 | counterfactual oracles | C5-T | diagnostic only |
| — | C9–C12-R2, floor r2, overnight, 307 RLR | — | — | — | **zero** 309 evaluations |

## C. Committed negative results and their exact scopes

| family | scope (held fixed) | consumer | verdict |
|---|---|---|---|
| F1 uniform-A0 | TC-T (P2′, P3′, Ĝ := 0), frozen inputs; any triple with A0 a valid **uniform** order-0 bound | direct clause, restated under C5-T | REFUTED WITHIN SCOPE. `does_not_cover`: residual-specific non-norm-only order-0 bounds; changes to TC-T, clause or inputs; order-3 candidates |
| C3 knockout | D′ A0 at its certified value, A1 = A2 = 0 | direct | Γ > 0 (not exhaustion; no Λ floor then) |
| F2 two-input transport | only (g_hi, whole-cell [H_lo, H_hi]), x_lo > 0 | any transport | EXHAUSTED ("the transport, not the cell"); TPT is outside (third input) |
| F3 E2 family | Wald/overshoot bounds | — | exclusion direction only |
| F4 C1 deflation | norm-only supply (∈ F1) | direct | MARGINAL |
| F5 T2 real order-3 | TC with a real Ĝ, lower-front evidence model | direct (forecast) | USEFUL refuted; hinge = centre motion |
| F6 C8 R1/R2 | floor raising | C5-T | zero leverage |
| F7 C5 ledger | B2 record-free split (killed); D2 sign-awareness (identity); A4 (killed); A1, A3 DATA; B1 NEW_REAL | — | — |

## D. Known bounds relevant to closure (symbolic)

* **Lower bound on every admissible A0:** A0 ≥ Λ_309 := sup_{C309} E_a[τ] (Lemma SM(d)).
  * The sup sits at e_lo (Theorem M).
  * Certified lower bounds: Theorem L (C4) and C7-E2 (the PRIMARY has an empty dependency set).
  * There is no certified upper bound on Λ_309.
* **Knockout inequality:** Γ(S) ≥ g_hi + ρx_hi(|C_lo| + Λ_309·P̄2) ≥ 0 at 309, under the direct clause and under C5-T.
* **Transport optimality:**
  * C5-T is minimax-optimal for the two-input family;
  * TPT-O: g_hi + P* is the sup for the three-input family;
  * CR-3: real refinement removes 1 − 1/N^j of order-j slack.
* **This campaign's ladder:** TC-T ≥ SRK ≥ RSO-P∘SC ≥ exact (`theory/PHASE1_RESULTS.md`, Theorem L).

## E–F. Routes proposed so far, and why they failed, stalled or remain open

See `dossier/ROUTE_MATRIX.md`, which is the complete matrix with classifications.

## G. Temporal-integrity incidents and exposures relevant to 309

| incident | when | nature | bearing on 309 |
|---|---|---|---|
| C4 retrospective freeze | 2026-09-22 | c9b06abf held final 309 numbers before gate 376950be (erratum E2) | the exclusion's own provenance; C4 repairs partly unlanded |
| C5 | 2026-09-22 | transport code landed 20 s before the gate (disclosed) | C5-T provenance |
| C7 | 2026-09-22 | gate frozen after exploratory evaluation; errata E1/E4/E6 (KG8 narrowed in its favour) | Λ_309 floor provenance |
| overnight incident 01 | 2026-09-28 (4403f86f → 2f0fb5e1; residue eb55bcab) | graph put tail radius shares beside TPT factors | TPT at 309 BLOCKED |
| overnight incident 02 | 2026-09-28 (7e851139 → 0d32a2e8) | C7's 309 floor re-attributed at the shared endpoint to 308 | rule R2.4: no cross-cell re-attribution (308 is live) |
| overnight incident 03 | 2026-09-28 | C2b brief scale from 308 figures | only if the C2b A0 certifier is used |
| **309R1-01** (this campaign) | 2026-09-29 (1f6b724a) | coordinator exposure to the incident-01 shares through an over-broad grep | TPT at 309: HIGH liability |
| **309R1-02** (this campaign) | 2026-09-29 (daa1bd64) | coordinator's in-band mental estimate while conceiving SRK | SRK motivation risk MEDIUM-HIGH; decoys below the band only |
| ledgered necessary reads | 2026-09-29 | graph A §0–3 (309 critical-A0 vs floor), THEOREM_TCT (tail lines, filtered) | known gap class; disclosed |

## H. What predates each incident

* **Predates every overnight incident:** all C1–C8, C10, route-audit and floor-r2 evidence on 309.
* **Predates 309R1-01 and 309R1-02:** this campaign's charter and quarantine (52e00290).
* **Postdates both:** THEOREM_SRK (3df7a1a5), all SRK code, and all decoy declarations and runs. Their provenance is
  therefore "conceived with committed tail-dominance knowledge (program-wide) plus 309R1-01/02". Their evidence is
  target-free by construction: decoys below the band, synthetic geometries and FSM.

## I. Genuinely prospective components

| component | prospective? | why |
|---|---|---|
| THEOREM_SRK (Lemmas SK, SV, SV′, SV-T), Theorem L, O3-N/O3-X, SRK-P | **yes (mathematics)** | no target quantity used; general statements. Motivation disclosed (MEDIUM-HIGH) |
| SRK certifier and assembly code | **yes** | never run on the band or a quarantined cell; the guard refuses both |
| SRK decoy evidence | **yes** | the declaration was committed before any real-geometry run (f0dbaa79). The real kernel is used at e ≤ 33/32 only |
| RLR certifier (overnight / 307) | prospective **for 307**. For 309 it is known insufficient alone (C3) | reusable as an A1/A2 supply component |
| TPT | the mathematics is prospective | its 309 use is liability-bearing (01, 309R1-01) |
| SC, RSO-P (overnight) | the mathematics is prospective | data-blocked |

## J. Dependence on the K5 consumer inequalities

Every route acts on exactly one link of the chain below. Graph A §3 lists all the inequalities.

    Γ = g_hi + ρ·x_hi·M,
    M = |C_lo| + S̄,
    S̄ = (1/5)Σ_r [A0 p2 + 2A1 p1 + A2 p0].

| link | inequality (graph A §3 item) | routes acting on it |
|---|---|---|
| g_hi | generic midpoint eps (item 3) | Corollary T |
| transport ρ·x_hi | items 4, 5 | C5-T (adopted for science), TPT, cover refinement |
| atom constants A | item 9 | Lemma G, Dv′, RLR, C2b. Floored by Λ (A0) |
| order-0 channel A0·‖φ″‖ | item 8 | **SRK (new)**, RSO |
| order-3 surrogate f_G | item 14 | SC-3, real Ĝ |
| order-4 envelope Env4 | items 13, 15 | SC-4w, SRK (weights), TC⁺ |
| Ĝ := 0 centre | item 16 | real Ĝ, O3-X |

Only the direct clause is the adoption quantity (floor r2). Any change beyond S is closure-only.
