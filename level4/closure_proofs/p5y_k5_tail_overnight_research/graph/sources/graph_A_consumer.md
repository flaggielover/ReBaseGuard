# Graph A — the consumer chain from primitives to Γ (K5, CUSUM, m = 5, cells 306–309)

**Read-only reconstruction.** Worktree `/Users/suzhe/ReBaseGuard-k5ov`, branch `p5y-k5-tail-overnight-306-309`, HEAD
`6735d945` (= `8b9fc0bb` + the overnight charter commit). Unless stated otherwise, every path below is relative to
`level4/closure_proofs/`. `F:n` means file F, line n. Every number below is **quoted** from a committed file. I did not
compute any Γ, margin, radius, magnitude, factor, critical constant or derived number for cells 305–309.

**Quarantine compliance, including one slip.** I ran no repository code, no tests and no campaign driver. I wrote no
file except this one. I contacted no remote host. I used `git hash-object` (no `-w`) and `git log` / `git show`
read-only. **Disclosure:** one of my shell commands contained a stray `python3 -c "print('noop')" >/dev/null`. It is a
Python invocation, although it loads no repository code, reads no file, computes nothing and writes nothing. I record it
here because the quarantine forbids any Python.

Short aliases used below:

| alias | path |
|---|---|
| BRIDGE | `p5y_k5_feasibility/K5_GLOBAL_BRIDGE.md` (added `6f1d351b`, 2026-09-13) |
| TC | `p5y_k5_lower_front_order3/theorem/THEOREM_TC.md` (added `38c74494`, 2026-09-20) |
| TCT | `p5y_k5_m5_tail_closure/theorem/THEOREM_TCT.md` (added `ae153a69`; last edit `76c37de1`, 2026-09-20) |
| AD | `p5y_k5_perron_deflated_resolvent/theorem/THEOREM_AD.md` (added `f0231499`, 2026-09-19) |
| KB | `p5y_k5b_independent_countersignature/code/k5b_check.py` (added `d7d3c08b`; sha256 pin `ddd54dc4…`) |
| ADP | `p5y_k5b_consumption_adapter/code/consumption_adapter.py` (added `a2bb280d`; pin `fbad7d33…`) |
| TCR | `p5y_k5_lower_front_order3/code/tc_rule.py` (added `38c74494`; pin `8d402d11…`, blob `ce101d17`) |
| TCTR | `p5y_k5_m5_tail_closure/code/tct_rule.py` (added `62227f77`, last `46655b31`; blob `98f6eee4`) |
| TF2 | `p5y_k5_m5_tail_closure/code/tail_forecast_r2.py` (added `62227f77`; blob `edec817e`, sha256 `5ab31ae5…`) |
| DC | `p5y_k5_perron_deflated_resolvent/code/deflated_consume.py` (added `f0231499`; blob `a0a836fa`, sha256 `ef5d0474…`) |
| D5 | `p5y_k5_tail_c2_closure/code/c2_d5_forecast.py` (added `51f8844b`, last `5a94568a`; blob `18403dbe`) |
| D5J | `p5y_k5_tail_c2_closure/evidence/phase_d5/C2_D5_FORECAST.json` (added `5a94568a`; blob `a191557f`) |
| ROB | `p5y_k5_tail_c2_closure/evidence/phase_d5/C2_ROBUSTNESS_AND_R_ATTRIBUTION.json` (`5a94568a`) |
| CRIT | `p5y_k5_tail_c2_closure/evidence/phase_d5/C2_CRITICAL_RATIOS.json` (`12585997`) |
| D1J | `p5y_k5_tail_c2_closure/evidence/phase_d1/C2_D1_BLOCKER.json` (`e71378a0`) |
| C2ADJ | `p5y_k5_tail_c2_closure/evidence/adjudication/C2_ADJUDICATION.md` (`ae4cbc2c`) |
| C3B | `p5y_k5_tail_c3_closure/evidence/phase_c1/C3_BLOCKER.json` (`24c038ec`) |
| C3ADJ | `p5y_k5_tail_c3_closure/evidence/adjudication/C3_ADJUDICATION.md` (`019ecce0`) |
| C4T | `p5y_k5_tail_c4_exhaustion/phase_1/C4_TARGET_RECONSTRUCTION.md` (`c9b06abf`) |
| C4ADJ | `p5y_k5_tail_c4_exhaustion/evidence/adjudication/C4_ADJUDICATION.md` (`e12a09e8`) |
| C5T | `p5y_k5_tail_c5_exhaustion/code/c5_transport.py` (added `27a12bef`, last `5fad47ad`) |
| C5MECH | `p5y_k5_tail_c5_exhaustion/phase_6/C5_SELECTED_MECHANISM.md` (`5fad47ad`) |
| C5DEC | `p5y_k5_tail_c5_exhaustion/evidence/phase1/C5_DECOMPOSITION.json` (`27a12bef`) |
| C5SEN | `p5y_k5_tail_c5_exhaustion/evidence/phase2/C5_SENSITIVITY.json` (`27a12bef`) |
| C5FC | `p5y_k5_tail_c5_exhaustion/evidence/forecast/C5_FORECAST.json` (`8b2be7ab`) |
| C5ADJ | `p5y_k5_tail_c5_exhaustion/evidence/adjudication/C5_ADJUDICATION.md` (`69bff424`) |
| C8R | `p5y_k5_tail_c8_operator_feasibility/README.md` (`07511435`) |
| C8CH | `p5y_k5_tail_c8_operator_feasibility/code/c8_chain.py` (`218cc314`) |
| C8ADJ | `p5y_k5_tail_c8_operator_feasibility/review/ADJUDICATION_C8.md` (`63a3f825`) |
| FLR | `p5y_k5_tail_floor_r2/config/K5_TAIL_ADOPTION_FLOOR_R2.json` (`a15d083b`, 2026-09-27) |
| FLS | `p5y_k5_tail_floor_r2/FLOOR_R2_SPECIFICATION.md` (`a15d083b`) |
| TIN_k | `p5y_k5_m5_tail_closure/evidence/measurement_r1/TCT_INPUTS_{k}.json` (`ae153a69`) |
| ATI | `p5y_k5_m5_tail_closure/evidence/measurement_r1/ADOPTED_TAIL_INPUTS.json` (`5ed8f059`; protocol pin `485fb125…`) |
| TFJ | `p5y_k5_m5_tail_closure/evidence/forecast_r2/TAIL_FORECAST_R2.json` (`ae153a69`) |
| EXD | `p5y_k5_m5_tail_closure/phase_c/EXECUTION_DECISION.md` (`ae153a69`) |
| C12 | `p5y_k5_tail_c12r2_cell306_adoption/evidence/execution/C12R2_CELL306_RESULT.json` (`276f4d41`) |

I verified the floor-r2 bindings with `git hash-object`: `c2_d5_forecast.py` = `18403dbec855…`,
`deflated_consume.py` = `a0a836fa83c6…` and `tct_rule.py` = `98f6eee4d867…` in this worktree.

---

## 0. The chain in one expression (symbolic only)

### 0.1 The frozen adoption quantity (floor r2, FLR:76)

The adoption quantity is the direct clause of the frozen K5-B, evaluated by the C2 consumer path (D5:79-89; KB:166):

```
Γ(5,k;S) = g_hi + ρ·x_hi·M
g_hi     = R.hi − e0·D.lo                       (R = R_interval, D = D_interval of the sealed K1 record, m = 5)
M        = M_R2                                  if max(H.lo, lo) > min(H.hi, hi)          (empty intersection)
         = min(M_R2, max(|max(H.lo,lo)|, |min(H.hi,hi)|))   otherwise
[lo,hi]  = 𝓗_5(S) = TC-T whole-cell enclosure of R''_5     (TCTR:180-209)
H        = R2_interval of the sealed K1 record
```

The TC-T enclosure for m = 5 is (TCTR:195-209, TCR:35-41, TCT:124-128):

```
lo = C_lo − S̄(A),   hi = C_hi + S̄(A)
C_lo/C_hi = (1/5)·Σ_{r=0..4} Ĥ_r(a).lo/hi + Σ_{t=1..4} Σ_{r<t} (1/t − 1/5)·W_(r,t−r−1).lo/hi
S̄(A) = (1/5)·Σ_{r=0..4} half_r,   half_r = rad_r = A0·p2(r) + 2·A1·p1(r) + A2·p0(r)     (|Ĝ(a)| = 0)
p2 = f_H + ρ f_G + ρ² Env4/2
p1 = f_D + ρ f_H + ρ² f_G/2 + ρ³ Env4/6
p0 = f_F + ρ f_D + ρ² f_H/2 + ρ³ f_G/6 + ρ⁴ Env4/24
f_F = δ_F + ε_src[0],  f_D = δ_D + ε_src[1],  f_H = δ_H + ε_src[2]                     (midpoint)
f_G = k3·s_F + 3k2·s_D + 3k1·s_H + σ3 + ε_src[3]                                        (P2′, Ĝ := 0)
Env4 = σ4 + 6k2·s_H + 4k3·(s_D + ρ s_H) + k4·(s_F + ρ s_D + ρ² s_H/2)                    (P3 at s_G = 0)
```

Here σ3 comes from the (P3′) midpoint tower and σ4 from the (P3′) cell tower (TCTR:94-138). A = (A0, A1, A2) is the
chosen supply S (D5:70-76). For S_I1 it is the componentwise minimum over the Lemma G, C1 and C2 supplies.

### 0.2 Binding-regime closed form (what the committed evidence shows holds on 306–309)

Three committed facts put all four cells in one regime:

- 𝓗 ⊆ R2_interval on all five tail cells, so the intersection is 𝓗 itself (C2ADJ:229-232: *"𝓗 ⊆ R2_interval on all
  five … the TC-T enclosure, not the record, sets M everywhere"*).
- The lower end binds. D5J's `M_after_exact` string equals `H_exact[0]` with the sign removed, on every cell (306:
  D5J:50/54; 307: :82/86; 308: :114/118; 309: :146/150). C5 states the same for its own supply (C5 phase_1
  `C5_BLOCKER_DECOMPOSITION.md`:34-36: *"on all four cells the lower end binds, so `M = |C_lo| + S` exactly"*).
- The Ĥ_r(a) are point intervals (for example TIN_306:72-75), and C_lo < 0 on all four cells (C5DEC:24-27, 87-90,
  150-153, 213-216).

So, as long as 𝓗 stays inside R2_interval, the lower end binds and M < M_R2:

```
Γ(S) = [R.hi − e0·D.lo]  +  ρ·x_hi·|C_lo|  +  ρ·x_hi·( A0·P̄2 + 2·A1·P̄1 + A2·P̄0 ),     P̄j := (1/5)·Σ_r p_j(r)
```

Γ is **affine in (A0, A1, A2)**. It is affine in a uniform scale s of A until M saturates at M_R2 (C8CH:87-94, 118-121).
Everything multiplying A (P̄j, C_lo, g_hi, ρ, x_hi) is independent of A.

### 0.3 Supply factorisations

- **Lemma G** (TCTR:65-76, TCT:20-33): A0 = C, A1 = k1·C², A2 = k2·C² + 2·k1²·C³, with C = `C_upper`.
- **Lemma Dv′ r2** (DC:97-109, AD:81-89): A0 = eff, A1 = eff·(κ1·C_T + δ1),
  A2 = eff·(2κ1²C_T² + κ2·C_T + 2κ1·C_T·δ1 + 2δ1² + δ2), where eff := Ā_eff = min(Ā, τ/D_lo), δ1 = D1/D_lo,
  δ2 = D2/D_lo, κ1 = 7978846/10⁷ and κ2 = 9678830/10⁷ (DC:55-56). So under a Dv′ supply **S̄ = eff·[P̄2 + 2(κ1C_T+δ1)P̄1
  + (…)P̄0]**, and Γ is affine in eff at fixed (C_T, δ1, δ2) (C8CH:21-27).

### 0.4 The C5-T variant (not the adoption quantity; see §2)

```
Γ_C5T = g_hi + max( (−H_lo)⁺·ρ(x_hi − ρ/2) , (H_hi)⁺·ρ(x_lo + ρ/2) )        (C5T:14-20, 81-86)
```

On 306–309 the rightward branch binds (C5FC `binding_direction: "rightward"` at :56, 93, 130, 167). The penalty is
therefore ρ·(x_hi − ρ/2)·(|C_lo| + S̄).

### 0.5 DAG

```
cells.json ─► e0, ρ, x_lo, x_hi ───────────────────────────────────────────────────────────────┐
K1 record ─► R_interval, D_interval ─► g_hi ────────────────────────────────────────────────────►│
K1 record ─► R2_interval, M_R2 ─────────────────────────────────────────► ∩ , clip ─► M ────────►│ Γ = g_hi + ρ x_hi M
K1 record ─► C_upper, k_i, j_i ─► Lemma G A_G ─┐                                   ▲             │  (k5b_literal direct)
registries C1/C2 (I1), C11R/C11RD (I2) ─► Dv′ ─┴► D4 min ─► A ─► rad_r ─► S̄ ─► 𝓗_5 ┘             │
replayed K1 ─► δ_{F,D,H}, ε_src, s_{F,D,H}, sup_S0, Ĥ_r(a), W2 ─► f_{F,D,H}, f_G, Env4 ─► p0,p1,p2 ─► rad_r
Aux3 evidence (S:r:3, h:j:3) ─► towers ─► σ3 (→ f_G), σ4 (→ Env4)
                                                                                                └► chain clause (μ,ℓ,γ,U) — evaluated by k5b_literal, NOT part of the adoption quantity
```

---

## 1. Nodes, from primitives to Γ

Field legend: **Def** = definition · **Impl** = implementation · **Src** = source artifact and commit · **Val** = committed
values for 306–309 · **Bound** = kind of certified bound · **→Γ** = how it enters Γ · **Scope** = per-cell or shared ·
**Dom** = dominance per committed evidence · **Impr** = improvable? · **Sci** = does improvement need new science /
new real compute? · **Frozen** = is it on the C2 consumer path bound by floor r2 (D5 `18403dbe` + DC `a0a836fa` +
TCTR `98f6eee4` + the k5b_literal direct clause)?

### Layer P — primitives

**N1. Cover geometry e0, ρ, x_lo = left, x_hi = right**

- **Def:** C_k = [e0 − ρ, e0 + ρ] (BRIDGE:7).
- **Impl:** `KM.rat(cov[...])` at D5:87. The cover is loaded by the frozen loader `k5_minimality` (pin `3a54f0fb`,
  ADP:28-31) and filtered to CUSUM (TF2:121). The adapter checks the record's e0/ρ against the cover (ADP:134-140).
- **Src:** `p5y_k1_cover_ledger_successor/config/cells.json` (added `b58e62e4`, 2026-09-05; sha256 `341eb5e9…`).
- **Val** (TIN_k lines 45/51/172/173):

  | cell | e0 | left | ρ | right |
  |---|---|---|---|---|
  | 306 | `17452573/10000000` | `680769/400000` | `108337/2500000` | `17885921/10000000` |
  | 307 | `36710051/20000000` | `17885921/10000000` | `938209/20000000` | `1882413/1000000` |
  | 308 | `38663231/20000000` | `1882413/1000000` | `1014971/20000000` | `19839101/10000000` |
  | 309 | `40761931/20000000` | `19839101/10000000` | `1083729/20000000` | `2092283/1000000` |

- **Bound:** exact rationals.
- **→Γ:** ρ appears twice. It is the transport factor ρ·x_hi, and inside TC-T it is the Taylor radius (TIN `rho`,
  TCTR:185). e0 enters g_hi. The dominant radius term A0·ρ·f_G is therefore quadratic in ρ overall, and the Env4 term is
  cubic.
- **Scope:** per cell.
- **Dom:** C4 reports *"enclosure `ρ` × 0.5 → critical A0 7.534321"* against a baseline of 3.214236 at 309 (C4ADJ:235).
  C5 reports the "ρ halved" diagnostic Γ = −0.13044835098940574 / −0.08664698724276013 / −0.05001973715651464 for
  307/308/309 (C5SEN:247-262, DIAGNOSTIC; see §5 item 9).
- **Impr:** yes, by refining the cover.
- **Sci:** new K1 real compute plus governance. Route T4 was *"INFEASIBLE (governance)"* (TAIL_ROUTE_COMPARISON.md:13);
  C8 lists B1 cover refinement as NEW_REAL.
- **Frozen:** yes (input).

**N2 / N3. Midpoint enclosures R_k = R_interval ∋ R(e0), D_k = D_interval ∋ R′(e0) (m = 5)**

- **Def:** An Arb ball Σ_{r<m}(1/m)·[origin_r ± eps_mid] + (W terms) (AD:131-142). eps_mid comes from the generic K1
  DAG rules eps(F) = C·f_F and eps(D) = C·(f_D + k1·eps(F)) (TCT:35-37; AD:127-128).
- **Impl:** read at D5:88 (`ad["R_interval"]["hi"]`, `ad["D_interval"]["lo"]`) from the ATI extract. ADP:141-150 reads
  the same fields from the records.
- **Src:** the K1 records (off-host; manifest `COMPOSITE_EXPORT_MANIFEST.json`, sha `29ad1f9b`). The committed extract is
  ATI.
- **Val:** exact rationals at ATI:192-204 (306), :297-311 (307), :402-416 (308), :506-520 (309). No decimals are
  committed per field; g_hi is quoted under N15.
- **Bound:** two-sided certified intervals (outward-rounded Arb).
- **→Γ:** only through g_hi.
- **Scope:** per cell.
- **Dom:** g_hi *"is 59–60% of the closure deficit"* (C6_ADJUDICATION.md:606; REVIEW_C6_FORENSIC.md:401).
- **Impr:** C5 phase 1 says **no — sealed** (`C5_BLOCKER_DECOMPOSITION.md`:17). But AD Corollary T/C step 2 tightens R
  and R′ at the midpoint for registry-covered cells (AD:149-150). The tail consumer applies deflation only on
  [0,148] (TF2:63, 136; DC:180), so the tail g_hi carries the undeflated generic eps_mid. No committed artifact
  evaluates this for 306–309 (see §5 item 3). Joint R/D information (route D4) *"NEVER EXISTED … TRUE_NEW_REAL_REQUIRED"*
  (C6_ADJUDICATION.md:602-607).
- **Sci:** Corollary T would be deterministic and zero-new-real, but it needs a new consumer freeze. Joint R/D
  information needs new real compute.
- **Frozen:** yes (input).

**N4. Whole-cell record enclosure H = R2_interval ⊇ R″(C_k), and M_R2**

- **Def:** Σ(1/m)[Ĥ_r(a) ± eps_cell_refined[H:r]] + Σ c·W (TCTR:293-312; AD:131-142).
- **Impl:** D5:83-86.
- **Src:** the K1 record, via ATI.
- **Val:** M_R2 at ATI:196 (306) = `24441055674252543/4503599627370496`; :301 (307), :406 (308), :511 (309) are exact
  rationals. The decimal "adopted M" is 5.4270 / 5.3352 / 5.2961 / 5.2699 (EXD:110-113).
- **Bound:** two-sided, outward.
- **→Γ:** it clips 𝓗 (it never binds on 306–309) and caps M (the saturation value).
- **Scope:** per cell.
- **Dom:** not binding. *"mag(𝓗)/M_R2 = 0.6575 / 0.6471 / 0.6469 / 0.6519 / 0.6453"* for 305…309 (C2ADJ:231).
- **Impr:** irrelevant while not binding.
- **Frozen:** yes.

**N5. C = `C_upper`, the frozen K1 one-sided block bound ≥ sup_cell ‖(I − K_e)⁻¹‖**

- **Impl:** D5:173 (taken from the record) → TCTR:65-76.
- **Src:** the K1 record; ATI:109, :214, :319, :424.
- **Val:** `31054358416/4294967296`, `28687329103/4294967296`, `26517718059/4294967296`, `24835280415/4294967296` for
  306–309. Decimals are 7.230406258255243 / 6.6792892997618765 / 6.174137363908812 / 5.782414324348792 (D1J:339, 524,
  709, 894; also D5J:300, 317, 334, 351 as the G-supply A0).
- **Bound:** upper.
- **→Γ:** only through the Lemma G supply (N16).
- **Scope:** per cell.
- **Dom:** the G supply loses every field to C2 on every cell (D5J provenance :61-65, 93-97, 125-129, 157-161).
- **Impr/Sci:** frozen K1 value; changing it needs new K1 work.
- **Frozen:** yes (G is inside the D4 min).

**N6. Drift-aware norms k_i ≥ sup_cell ‖K_i(e)‖ and j_i ≥ ‖J_i‖ (i = 0..4)**

- **Impl:** TCTR:186-187; D5:195.
- **Src:** replayed by the frozen chain in `code/tct_inputs.py` (TCT:141-145); TIN_k:53-68.
- **Val:** exact rationals at TIN_306:55-67 (not restated). Observation: the j list equals the k list shifted by one
  index (compare TIN_306:55-59 with :63-67). This is a string comparison only.
- **Bound:** upper.
- **→Γ:** through f_G (k1, k2, k3), Env4 (k2, k3, k4), the towers, and Lemma G (k1, k2). Lemma Dv′ uses the global κ1
  and κ2 instead (DC:55-56).
- **Scope:** per cell.
- **Impr:** these are frozen certificates.
- **Frozen:** yes.

**N7. Midpoint residuals δ_F, δ_D, δ_H (per r) and source errors ε_src[0..3]**

- **Def:** TC (P2), TC:23-36.
- **Impl:** TCTR:169-172.
- **Src:** TIN_k `r[r]` (e.g. TIN_306:76-84).
- **Val:** exact rationals, not restated.
- **Bound:** upper.
- **→Γ:** f_F, f_D, f_H and the ε_src[3] allowance inside f_G.
- **Scope:** per cell × r.
- **Dom:** negligible. Under the C1 supply f_F, f_D and f_H are 0.28–0.60 %, ~0.3 % and ~0.15 % of the radius
  (`phase_d/D1_BLOCKER_DIAGNOSIS.md`:13-21). A0·f_H is 0.0853537818494967–0.1146132975416325 % of S̄ (C5DEC:51-53,
  114-116, 177-179, 240-242). *"A 10 % cut in the residuals … moves the critical A0 by 0.014 %"* (C4ADJ:237).
- **Impr:** yes, but pointless.
- **Frozen:** yes.

**N8. Candidate suprema s_F, s_D, s_H ≥ ‖F̂‖, ‖D̂‖, ‖Ĥ‖ (sup over X)**

- **Impl:** TCTR:160.
- **Src:** TIN_k `r[r].sup` (e.g. TIN_306:85-89).
- **Val:** exact rationals (not restated).
- **Bound:** upper.
- **→Γ:** f_G (3k1·s_H + 3k2·s_D + k3·s_F) and the candidate part of Env4.
- **Scope:** per cell × r.
- **Dom:** the candidate-sup part of f_G (mean over r) is 4.504057031287246 / 4.293174334905271 / 4.123322084507262 /
  3.913762350232831 (D1J:215, 399, 584, 769). The candidate part of Env4 is 10.318704600222183 / 9.830878289181237 /
  9.45019284400126 / 8.972695763341997 (D1J:211, 395, 580, 765). These are supply-independent quantities, even though
  they are recorded in the C1-supply file. At 309, *"candidate sup norms `sup{F,D,H}` × 0.5 → critical A0 4.160309"*
  (C4ADJ:234). A cut of *"2.0562%"* in the candidate sup norms voids the 309 exclusion under C5-T (C5FC:26;
  C5ADJ:552).
- **Impr:** yes, by tighter certified sup norms (route A1 / R5).
- **Sci:** DATA/toolchain (C8R:80); zero-new-real per C6.
- **Frozen:** yes (input).

**N9. sup_S0[n] (n = 0..4), drift-aware closed-form bounds of sup_cell ‖S_0^(n)‖**

- **Impl:** TCTR:188; pure tower at TCTR:80-91.
- **Src:** TIN_k:175-181.
- **→Γ:** the towers → σ3 and σ4. σ4(r=0) = sup_S0[4].
- **Val:** σ4(r=0) = 1.3359486909392215 on each of 306–309 (TFJ:4760, 4824, 4888, 4952). That the value is identical
  across cells is an observation from committed values only.
- **Frozen:** yes.

**N10. Adopted Aux3 order-3 evidence (candidate_suprema and midpoint_eps for `S:r:3`, `Sclosed:0:3`, `h:j:3`)**

- **Impl:** TCTR:127-138.
- **Src:** the K1 record `auxiliary_evidence`, extracted at ATI (306: ATI:110-132).
- **Bound:** midpoint upper bounds (TCT:85-89).
- **→Γ:** σ3 (midpoint tower) and σ4 (cell tower, with the mean-value correction).
- **Scope:** per cell.
- **Dom:** *"The live half of (P3′) is `S:r:3` for r = 1…4 and `h:j:3` for j = 2, 3, 4"* (TCT:114-117).
- **Frozen:** yes.

**N11. Centres Ĥ_r(a) (`H_at_a`)**

- **Def:** the frozen K1 order-2 candidate evaluated at the atom a; a point interval.
- **Src:** replayed (TCT:141-145). It is not in the 262-field identity gate. It is checked by the *derived identity gate*,
  which tests containment with a normalised endpoint tolerance of 10⁻⁶ (TCTR:284-315; measured worst gap 3.6279×10⁻⁸,
  C2ADJ:62-64).
- **Val:** e.g. TIN_306:72-75.
- **→Γ:** C_lo and C_hi, with coefficient 1/5.
- **Scope:** per cell × r.
- **Impr:** no (these are centres).
- **Frozen:** yes.

**N12. W-enclosures W_(r,j)(C) (`W2`), frozen whole-cell enclosures "origin ± cellwise node"**

- **Def:** TC:63-67.
- **Src:** replayed; TIN_306:2-43 holds 10 intervals.
- **→Γ:** C_lo, via the coefficients c = 1/t − 1/5 (TCR:39-40; TCTR:274-279). Their widths are what make the centre an
  interval, since the Ĥ_r(a) are points.
- **Val:** centre [C_lo, C_hi] (A-independent; recorded by C5):
  - 306 `[-0.4344657902310661, 0.002368359708562891]` (C5DEC:24-27)
  - 307 `[-0.41060745427623985, 0.07377993089373563]` (:87-90)
  - 308 `[-0.3934538793417449, 0.14388513336335515]` (:150-153)
  - 309 `[-0.37796680149668355, 0.20498531691994368]` (:213-216)
- **Dom:** *"`|C_lo|` ≈ 0.38 against `S` ≈ 2.94, so `S` is the target"* (`C5_BLOCKER_DECOMPOSITION.md`:36).
- **Impr:** yes. C4ADJ:263-264 names *"the `W2` enclosures"* as an unexcluded mechanism.
- **Sci:** new K1-level certified work (not quantified anywhere).
- **Frozen:** yes.

**N13. Operator constants (C_T, τ, Ā, D_lo, D1, D2) per registry**

- **Def:** AD:158-175. Ā ≥ sup E_a[τ]; τ ≥ sup τ_a; C_T ≥ sup ‖Ĝ‖; D_lo ≤ inf D; D1 ≥ sup |D′|; D2 ≥ sup |D″|.
- **Impl:** D5:198-203. `block_for` composes with max on uppers and min on D_lo (DC:146-171). REGISTRY_C2 composes
  sub-blocks inside the registry.
- **Src:**
  - I1: `p5y_k5_tail_operator_registry/evidence/registry_c1/REGISTRY_C1.json` (`4ccee386`) and
    `p5y_k5_tail_c2_closure/evidence/registry_c2/REGISTRY_C2.json` (`5a94568a`).
  - I2 (cell 306 only): `C11R_COMPARISON.json` (`2c24a989`) and C11RD.
- **Val:**
  - C1 decimals per cell: D1J:220-227 (306) *"Abar 7.9124167116351645, C_T 5.670984263954273, D1 1.519244732778201,
    D2 25.787949325480753, D_lo 0.7908924765725055, tau 5.0707461515756025"*; :404-411 (307); :589-596 (308);
    :774-781 (309).
  - C2 composed exact rationals: REGISTRY_C2.json:181-185 and :347 (306), :351-354 and :532 (307), :536-539 and :733
    (308), :737-740 and :934 (309).
  - I2 at 306: Ā = `3429/500` (C11R_COMPARISON.json:75), τ = `3429/500` (:171), D_lo = `101/200` (:147).
- **Bound:** uppers, plus one lower bound (D_lo).
- **→Γ:** only through N17, then N18.
- **Scope:** per cell.
- **Dom:** *"D_lo and τ are the only operator levers that matter … D2 is irrelevant"* (`D1_BLOCKER_DIAGNOSIS.md`:98-103).
- **Impr:** yes (E1/R3 operator certification).
- **Sci:** operator-only and zero-new-real, but *"No certifying host exists in scope"* (C8R:113-116).
- **Frozen:** the I1 registries, yes (FLS:94). I2 is not on the historical path; floor r2 substitutes it as S_I2.

**N14. κ1 = 7978846/10⁷ and κ2 = 9678830/10⁷**

- **Def:** rational upper bounds of E|He_1| = √(2/π) and E|He_2| = 4φ(1) (DC:53-56; AD:24).
- **Scope:** shared by all cells and all supplies (FLS:95).
- **Frozen:** yes.

### Layer D — derived nodes

**N15. g_hi = R.hi − e0·D.lo ≥ g(e0), where g(e) = R(e) − e·R′(e)**

- **Def:** BRIDGE:16, 27. `hi(R − e0 D) = R.hi − e0 D.lo` requires e0 ≥ 0 (KB:163-166).
- **Impl:** D5:88; KB:166.
- **Val:** −0.302674155894373 / −0.2716387904948848 / −0.24489517123463297 / −0.22332604549393695 (C5DEC:30, 93, 156,
  219). The equivalent M_needed = −g_hi/(ρ·x_hi) is 3.905055721051138 / 3.0761483479002325 / 2.432397764101128 /
  1.969827744481147 (D1J:202, 386, 571, 756; C5DEC:13, 75, 138, 201).
- **Bound:** an upper bound of g at the midpoint. It is exact interval arithmetic on two *independent* intervals.
- **→Γ:** additive.
- **Scope:** per cell. It is A-independent.
- **Dom:** 59–60 % of the closure deficit (see N2).
- **Impr/Sci:** see N2/N3.
- **Frozen:** yes.

**N16. Lemma G supply A_G**

- **Def:** A0 = C, A1 = k1·C², A2 = k2·C² + 2k1²·C³ (TCT:26-28).
- **Impl:** TCTR:65-76, called at D5:197.
- **Src:** TCT §1.
- **Val (decimals):**
  - 306: `7.230406258255243 / 41.697052649841126 / 531.4670671630953` (D5J:300-302)
  - 307: `6.6792892997618765 / 35.57778229811774 / 422.1285970238484` (:317-319)
  - 308: `6.174137363908812 / 30.393446012323317 / 336.052306022857` (:334-336)
  - 309: `5.782414324348792 / 26.650741928068 / 277.9282709148853` (:351-353)
- **Bound:** upper, by submultiplicativity (TCT:30-33).
- **→Γ:** it is a candidate in the D4 minimum.
- **Scope:** per cell.
- **Dom:** never selected on the tail (provenance C2 everywhere).
- **Frozen:** yes.

**N17. eff = Ā_eff = min(Ā, τ/D_lo); δ1 = D1/D_lo, δ2 = D2/D_lo; Lemma Dv′ r2 supply A_Dv′**

- **Def:** AD:81-89.
- **Impl:** DC:97-109, called at D5:200 and cross-checked against `_atom_independent` (D5:60-67, 201-202).
- **Val:**
  - C1 supply A: 306 `6.411422920029179 / 41.326208144609154 / 665.5436573260256` (D5J:290-292); 307 :307-309;
    308 :324-326; 309 :341-343.
  - C2 supply A: 306 `6.121808203299506 / 31.776552901884617 / 372.98795136463804` (D5J:295-297); 307 :312-314;
    308 :329-331; 309 :346-348.
  - I2 at 306: A0 = `3429/500` (C12:125).
- **Min branch:** *"Ā > τ/D_lo on all five cells, so Ā_eff = τ/D_lo and the ARL supersolution never binds"* under I1
  (C2ADJ:255-257). Under I2 at 306 the committed A0 equals the committed I2 Ā (and τ), `3429/500`, so the Ā branch is
  the active one there. This is a reading of committed strings; no substitution was done.
- **Bound:** upper. The quotient rule is bounded term by term (AD:74-77, 88-89).
- **→Γ:** A0 multiplies P̄2, 2A1 multiplies P̄1, A2 multiplies P̄0. eff is a common factor of all three.
- **Scope:** per cell. κ is shared.
- **Dom:** A0·p2 is 81.4946010624007 / 81.56107503551327 / 81.65849469865014 / 81.94654148245344 % of S̄ under
  operator_mixed (C5DEC:38-39, 101-102, 164-165, 227-228). Under C1, a 10 % A0 improvement gives 6.20–6.30 % magnitude
  gain; A1 gives 1.63–1.66 %; A2 gives 0.22–0.23 % (`D1_BLOCKER_DIAGNOSIS.md`:57-61; D1J:309-327 etc.).
- **Impr:** yes (N13). eff is floored by Lemma SM(d), eff ≥ Λ_k (N34).
- **Sci:** operator certification.
- **Frozen:** yes.

**N18. The chosen supply S: A_j = min over valid supplies (D4 rule)**

- **Def:** gate `D4_combination_rule` (D5J:169).
- **Impl:** D5:70-76, called at :204.
- **Val:** S_I1 equals the C2 supply on every field of every cell (provenance D5J:61-65, 93-97, 125-129, 157-161; C2ADJ:209-211).
- **Bound:** the minimum of valid upper bounds.
- **Scope:** per cell.
- **Impr:** the operator-level mixed tuple (C3's D′) is componentwise tighter (CRIT `operator_mixed`; C3ADJ:304-307).
  Floor r2 forbids cross-implementation mixing (FLS:57-60, 79-83) and excludes the D′ supply from S_I (FLS:92-93).
- **Frozen:** yes. `combine` is in D5.

**N19. Towers**

- **Def:** pure tower P[j,n]; midpoint tower t_mid[j,3] = min(P[j,3], h3_mid[j]); cell tower
  t_cell[j,3] = min(P[j,3], h3_mid[j] + ρ·P[j,4]); t_cell[j,4] re-derived by Leibniz and clamped (TCT:96-98).
- **Impl:** TCTR:80-116; independent re-derivation at TCTR:224-238.
- **Bound:** upper. It uses pointwise Leibniz bounds and the Leibniz triangle inequality.
- **→Γ:** σ3 and σ4.
- **Scope:** per cell.
- **Frozen:** yes.

**N20. σ3(r) ≥ ‖S_r‴(e0)‖**

- **Def:** min(tower Leibniz bound, adopted Aux3 bound) (TCTR:119-124, 135-137).
- **Val (per r = 0..4):**
  - 306: 0.700150075207459, 2.466187684779108, 3.4346794012869877, 4.246039339694608, 3.194870148892824 (TFJ:4759-4803)
  - 307: 0.700150075207459, 2.787134764216958, 3.047367727515121, 4.391011338169276, 2.3493987147520827 (TFJ:4823-4867)
  - 308: 0.6994867176884412, 3.0047924194342253, 3.168593649305406, 4.107785332147262, 2.1457290071145434 (TFJ:4887-4931)
  - 309: 0.6942432544652429, 3.0428536545961493, 3.4115955301531913, 3.8053165761575127, 2.2502431948866337 (TFJ:4951-4995)
  - Means over r: 2.8083853299721975 / 2.6550125239721796 / 2.6252774251379756 / 2.640850442051746 (D1J:217, 401, 586, 771).
- **Bound:** midpoint upper.
- **→Γ:** inside f_G, as A0·ρ·σ3 (plus the A1 and A2 counterparts).
- **Dom:** *"`sigma3` is 42–48 % of it [f_G] at r ≥ 1"* (`C5_BLOCKER_DECOMPOSITION.md`:59-62).
- **Impr:** yes, via sharper order-3 source evidence.
- **Sci:** new certified source evidence.
- **Frozen:** yes.

**N21. σ4(r) ≥ sup_cell ‖S_r⁗‖**

- **Def:** the cell tower (TCTR:137; TCT:96-112).
- **Val (per r):**
  - 306: 1.3359486909392215, 16.23242147075951, 53.16121895285929, 124.20360998400186, 233.09403465017857 (TFJ:4760-4804)
  - 307: 1.3359486909392215, 15.99459135286653, 53.431529537372526, 125.17453153075496, 232.75398221595944
  - 308: 1.3359486909392215, 15.755306364751773, 53.62061561726245, 125.25740172346511, 233.53803037780415
  - 309: 1.3359486909392215, 15.514975339053162, 53.434609493424745, 124.46145338043222, 235.1170467048456 (TFJ:4952-4996)
  - Means: 85.60544674974768 / 85.73811666557853 / 85.90146055484453 / 85.97280672173899 (D1J:212, 396, 581, 766).
- **Bound:** whole-cell upper.
- **→Γ:** Env4, then ρ²·Env4/2 in p2 and higher powers of ρ elsewhere.
- **Dom:** *"σ₄ reaches ≈ 235 at r = 4 through the J/h tower, for which no adopted order-4 evidence exists"* (EXD:130-131).
  σ4 is ~89 % of mean Env4 (D1J, e.g. 306 Env4_sigma4 85.61 against Env4_cand 10.32).
- **Impr:** yes, via order-4 evidence or a sharper tower theorem.
- **Sci:** order-4 measurement is NEW_REAL; a tower theorem is new mathematics.
- **Frozen:** yes.

**N22. f_F, f_D, f_H (midpoint)**

- **Def:** TC:25-28.
- **Impl:** TCTR:169-171.
- **Dom:** negligible (N7).
- **Frozen:** yes.

**N23. f_G, the order-3 surrogate (P2′, Ĝ := 0)**

- **Def:** f_G = 3k1·s_H + 3k2·s_D + k3·s_F + σ3, plus ε_src[3] (TCT:44-61). It bounds ‖φ‴(e0)‖, where
  φ‴(e0) = S‴ + 3K1Ĥ + 3K2D̂ + K3F̂.
- **Impl:** TCTR:142-150, 163, 172.
- **Val (per r, including ε_src[3]):**
  - 306: 5.584021669496869, 7.273678929811893, 7.481681217334524, 8.872030157162333, 7.365597694664826 (TFJ:4755-4799)
  - 307: 5.3345489776554045, 7.394410397395466, 7.296422409702939, 8.697177029620482, 6.034555934971045
  - 308: 5.122173715565618, 7.368443040522273, 7.592114762105587, 8.43231127759643, 5.244869296187715
  - 309: 4.901285924245842, 7.222976361910761, 7.849781318713328, 7.861980815646118, 4.953474158032464 (TFJ:4947-4991)
  - Means: 7.315401933694089 / 6.951422949869067 / 6.751982418395525 / 6.557899715709704 (C3B:12, 97, 182, 267).
  - Inside the mean f_G, ε_src[3] contributes 0.002959572434645126 / 0.0032360909916171066 / 0.0033829087502877772 /
    0.0032869234251259464 (D1J:216, 400, 585, 770).
- **Bound:** a midpoint norm bound by the triangle inequality with no cancellation.
- **→Γ:** A0·ρ·f_G (p2), 2A1·ρ²·f_G/2 (p1), A2·ρ³·f_G/6 (p0).
- **Scope:** per cell × r. It is A-independent.
- **Dom:** **the dominant channel.** A0·ρ·f_G is 63.37429889225686 / 61.58839800839967 / 60.04153815919196 /
  58.79748314449863 % of S̄ under operator_mixed (C5DEC:55-57, 118-120, 181-183, 244-246). Under C1, the f_G-bearing
  terms are 78.49 / 76.44 / 74.67 / 73.08 % of the radius (D1J:189, 373, 558, 743). Under Lemma G they are
  *"78.7 / 77.1 / 75.0 / 73.2 / 71.6 %"* for 305…309 (EXD:132).
- **Impr:** yes, by three routes:
  - a real Ĝ (R-stage; it pays s_G through Env4 and |Ĝ(a)| through centre motion; critical ratios in ROB/CRIT);
  - a cancellation theorem (C6 A3 *"unwritten cancellation theorem"*, C6_ADJUDICATION.md:596-600);
  - tighter s_X or σ3.
- **Sci:** a real Ĝ is NEW_REAL; cancellation is a new theorem.
- **Frozen:** yes. f_G is exactly what the frozen TCTR computes.

**N24. Env4 ≥ sup_cell ‖φ⁗‖ at s_G = 0**

- **Def:** TC:39-44; TCT:128.
- **Impl:** TCR:66-71, called at TCTR:173.
- **Val (per r):**
  - 306: 11.92949745242114, 27.11624190249508, 62.51160199245052, 135.07121658030195, 242.99219882218068 (TFJ:4754-4798)
  - 307: 11.394968869341609, 26.42781383765746, 63.27375351348167, 135.31775897883182, 241.4306795744863
  - 308: 10.94526487228573, 25.6394030388303, 63.88541063042463, 135.52085515441254, 240.7673332982758
  - 309: 10.482576078657639, 24.960240256697983, 63.74162112854803, 134.13719829756545, 241.40587666393583
  - Means: 95.92415134996988 / 95.56899495475977 / 95.3516533988458 / 94.945502485081 (C3B:11, 96, 181, 266).
- **Bound:** a whole-cell sup. It uses the triangle inequality, submultiplicativity and |t| ≤ ρ.
- **→Γ:** A0·ρ²·Env4/2 and similar terms.
- **Dom:** A0·ρ²·Env4/2 is 18.005688872602203 / 19.860117631968542 / 21.515050870692455 / 23.06370455610532 % of S̄
  (C5DEC:59-61, 122-124, 185-187, 248-250). *"The order-3 residual term A0·ρ·f_G is the largest single term everywhere
  except at r = 4 on cells 308 and 309, where the (P3) remainder A0·ρ²·Env4/2 overtakes it"* (EXD:130-131).
- **Impr/Sci:** see N21.
- **Frozen:** yes.

**N25. p0, p1, p2 (Taylor bounds on sup_cell ‖φ‖, ‖φ′‖, ‖φ″‖)**

- **Def:** TC:55-57.
- **Impl:** TCR:74-80.
- **Val:** only one committed example, at 309, r = 0: *"1.5·10⁻⁴, 0.0076, 0.28"* (EXD:165).
- **Bound:** upper, via the integral remainder and |t| ≤ ρ (TC:73-75).
- **Frozen:** yes.

**N26. rad_r = A0·p2 + 2A1·p1 + A2·p0 (= half_r, since |Ĝ(a)| = 0)**

- **Def:** TC:61, 80.
- **Impl:** TCR:83-91; TCTR:175-177.
- **Val:** under Lemma G per r:
  - 306: 2.3541613606239657, 3.1629362166093347, 3.5084334987492487, 4.64743781764684, 4.913112550936473 (TFJ:4756-4800)
  - 307: 2.2534342811259265, 3.2175816806453685, 3.4810751069935204, 4.667474341994589, 4.527680602802392
  - 308: 2.1679349880647143, 3.212253974372957, 3.6470707881140316, 4.656643546954542, 4.374447562251335
  - 309: 2.0771809869276625, 3.156873820435134, 3.7860751656211593, 4.497784984143401, 4.41362266582514
  - S̄ under operator_mixed: 3.0035717035044875 / 2.963991477417979 / 2.9781931709702425 / 2.9415576519776843
    (C5DEC:47, 110, 173, 236; also C3B:19, 104, 189, 274).
  - Mean rad under C1: 3.3967982236855265 / 3.3640652287690207 / 3.391683098778534 / 3.345449805962768 (D1J:256, 440,
    625, 810).
  - Under the C2 supply (S_I1) no per-r or S̄ value is committed. Only the resulting magnitude is committed (N28).
- **Bound:** the triangle inequality over the three terms of E″ = Rφ″ + 2(∂R)φ′ + (∂²R)φ, each bounded by
  (operator norm at the atom) × (sup norm) (TC:76-80).
- **→Γ:** S̄ = (1/5)Σ_r rad_r, times ρ·x_hi.
- **Scope:** per cell × r.
- **Frozen:** yes.

**N27. The assembly coefficients c(5) and the centre [C_lo, C_hi]**

- **Def:** F_r gets 1/5; W_(r,t−r−1) gets 1/t − 1/5 for t = 1..4 (TCR:35-41). All coefficients are ≥ 0, which is
  enforced (TCTR:205-206).
- **Val:** see N12.
- **Frozen:** yes.

**N28. 𝓗_5 = [C_lo − S̄, C_hi + S̄]**

- **Def:** TC:67; TCT:126.
- **Impl:** TCTR:180-209, cross-checked by the independent path TCTR:213-280, with a refusal on disagreement at D5:81-82.
- **Val (magnitude of 𝓗 = M, S_I1):**
  - 306 3.5119460127500672 (D5J:58); 307 3.451359412896 (:90); 308 3.4524564789357517 (:122); 309 3.400934402274074
    (:154).
  - Exact H_exact is at D5J:49-52, 81-84, 113-116, 145-148.
  - Lemma G (Campaign B TCT0): 4.151682 / 4.040057 / 4.005124 / 3.964274 (EXD:110-113).
- **Frozen:** yes.

**N29. M = min(M_R2, mag(H ∩ 𝓗))**

- **Def:** TC:96; TCT:129.
- **Impl:** D5:85-86; TF2:156-163 (compose).
- **Val:** `M_after` equals the magnitude on all four cells (D5J:53, 85, 117, 149).
- **Bound:** valid because the intersection of two valid enclosures is valid (C2ADJ:229-230).
- **→Γ:** ρ·x_hi·M.
- **Frozen:** yes.

**N30. Γ, the K5-B direct clause (the adoption quantity)**

- **Def:** BRIDGE:27, 44.
- **Impl:** D5:88-89; KB:166.
- **Src:** BRIDGE (`6f1d351b`); the implementation is `k5b_literal`, pinned `ddd54dc4`.
- **Val (S_I1):** Γ = −0.030469257709306738 / 0.033132953404317905 / 0.10270008356594545 / 0.16224941061997425 (D5J:47,
  79, 111, 143). `Gamma_exact` is at D5J:48, 80, 112, 144.
- **Val (other supplies):**
  - Lemma G: 0.01911558504907568 / 0.08511776989151419 / 0.15834296474510035 / 0.2261171664714765 (CRIT:249, 263, 277, 291)
  - C1: −0.005719468367263504 / 0.061683080290831596 / 0.13619454282611712 / 0.19881031084487408 (CRIT:33, 47, 61, 75)
  - operator_mixed: −0.03619777996457939 / 0.026354631323170525 / 0.09456414496566364 / 0.15301968889418385 (CRIT:393, 407, 421, 435)
  - min(G, C1): −0.0072384583425146275 / 0.058722721820044455 / 0.13095734077307422 / 0.1939882799114945 (CRIT:321, 335, 349, 363)
  - S_I2, 306 only: **0.005159101140006536** (C12:129; `C12R2_FLOOR_R2_APPLICATION.md`:19)
- **Bound:** the mean-value transport (BRIDGE:44).
- **→Γ:** it is Γ.
- **Frozen:** yes.

**N31. Γ_C5T, the exact-weight, sign-aware transport**

- **Def:** C5MECH:3-25.
- **Impl:** C5T:52-86.
- **Val (operator_mixed):** −0.03942593367711184 / 0.022641576453031827 / 0.09022244922018692 / 0.148146342573649 (C5FC:44, 81, 118, 155).
- **Bound:** attained within the two-input family (C5ADJ:175-181).
- **Frozen:** **no.** It is not on the floor-r2 path (§2).

**N32. The chain clause of k5b_literal (μ_k, ℓ_k, γ_k, U_k)**

- **Def:** BRIDGE:22-33.
- **Impl:** KB:177-189. It is evaluated by `compose` (TF2:164) but not by D5 `direct()`.
- **Val:** m = 5 `tail_via` under S_I1: 305 "direct", 306 "direct", 307/308/309 `null` (D5J:243-249). At m = 1/2/3 the tail
  passes via "chain" in many cells (D5J:181-222).
- **Note:** *"C2 uses **only** the direct clause, never the chain clause — which is strictly stricter than the theorem's
  own pass condition"* (C2ADJ:222-227). Campaign B named the chain requirement *"certify μ_k ≥ ≈ −0.29 for the chain"*
  (`phase_b/TAIL_ROUTE_COMPARISON.md`:4-5). The coupling between cells (γ_306 feeds U_307) is not part of the adoption
  quantity.
- **Frozen:** the FLR quantity is "the k5b_literal direct clause" only.

**N33. Adoption predicates**

- **Closure:** Γ < 0, strict (FLR:77).
- **Requirement:** 1/s*, where s* is the largest uniform A-scale that still passes. It is found by bisection (D5:92-105).
  - S_I1: 1.0 / 1.1407635748126312 / 1.5002877825423833 / 1.8990148694205993 (D5J:66, 98, 130, 162)
  - G: 1.0710617972762992 / 1.3616182784492443 / 1.7713435857396018 / 2.252902516639924 (CRIT:254-296)
- **Uniform-A margin (F2):** the largest inflation of A before the cell reopens (`c3_blocker.py`:81-92). At 306 it is
  1.1277375254679296 on C2 / D4 (C3B:45, 58), 1.1554876238748288 on operator_mixed (C3B:84), and 1.1277 per C2ADJ:476.
  Under C5-T with operator_mixed it is 1.171431 (C8R:52).
- **F2:** margin ≥ 1.25 (FLR:95-100).
- **F1′:** Γ(S_I1) < 0 **and** Γ(S_I2) < 0 (FLR:92).
- **Frozen:** these are the rule's predicates over N30.

**N34. The Lemma SM(d) floor, Λ_k = sup_cell E_a[τ](e)**

- **Def:** AD:51. *"A0 admissible ⇔ A0 ≥ Λ_k"* (C4T:8-18).
- **Val:**
  - C4 certified floors 3.512733596022926 (308) and 3.297250281519544 (309) (C5SEN:15, 30).
  - C7's primary 309 bound is 3.586306094 (`p5y_k5_tail_c7_e2_lambda309/OPEN_NOTES_DISPOSITION_C7.md`:32). Monte Carlo
    gives 3.98842 ± 0.00050 (:61).
  - The Monte-Carlo diagnostics are 4.5929 / 4.311 / 4.0473 for 307/308/309 (C5SEN:6, 21, 36).
- **→Γ:** **it does not enter Γ.** *"`Γ` depends on `A0` and **never on `Λ`**. By Lemma SM(d), `Λ` enters the decision
  only as the **floor** below which no admissible `A0` can go"* (C8R:32-35).
- **Scope:** per cell.
- **Frozen:** no (it is a constraint, not an input).

---

## 2. Which clause is authoritative for adoption, and where eff, the A0 minimum and the Lemma SM floor enter

**For adoption, the frozen K5-B direct clause through C2's consumer path is authoritative.** Floor r2 is in force: it
was accepted as REPLACEMENT_FLOOR_ACCEPTED `3fadb422`, and it is later than C5. It fixes the adoption quantity as:

> *"Gamma(5, k; S): the exact rational K5-B value for pair (m = 5, k) computed by the frozen consumer path that produced
> C2's committed Gamma_exact (… c2_d5_forecast.py blob 18403dbe … deflated_consume.py blob a0a836fa, … tct_rule.py blob
> 98f6eee4 and the k5b_literal direct clause), with the atom constants S substituted and every other input unchanged"*
> (FLR:76; FLS:85-100)

C12-R2 applied exactly this quantity to cell 306 (`C12R2_FLOOR_R2_APPLICATION.md`:12-20).

**C5-T is the adopted authoritative transport for scientific statements.** C5's adjudication adopted it *"ONLY where its
premise holds … It supersedes `rho·x_hi·M` on every K1 cell with `x_lo > 0`"* (C5ADJ:561-565). C8 uses it throughout
(C8R:43; `evidence/phase9/C8_DECISION.json`:24: *"C5-T (adopted by C5's adjudication); C2 frozen clause cross-checks
only"*). The route audit review flagged the mismatch as N5 (`p5y_k5_tail_route_audit/review/ROUTE_AUDIT_R1_REVIEW.md`:185-201).

Since P_C5T < ρ·x_hi·M strictly (C5MECH:27-29), closure under the adoption quantity implies closure under C5-T, but not
the other way round. Every C8 or C9 "×eff" factor is a C5-T number and is **not** the r2 adoption quantity.

A residual ambiguity: floor r2's base clause reads *"Γ < 0 under the campaign's own frozen closure rule"* (FLR:87;
FLS:54-55), while `quantity_compared.adoption_quantity` pins the direct clause (see §5).

**Where eff and A0 = min(Ā, τ/D_lo) enter.** eff enters only through the atom constants.

- Lemma Dv′ gives A0 = eff and A1, A2 = eff × (tame factors) (DC:102-105; AD:86).
- The D4 minimum then selects them per field (D5:70-76).
- They enter rad_r linearly (TCR:83-87), then S̄ = (1/5)Σ rad_r, then the lower endpoint lo = C_lo − S̄, then M, and
  finally ρ·x_hi·M.

In the binding regime (§0.2): Γ = g_hi + ρ·x_hi·(|C_lo| + eff·Q), with Q = P̄2 + 2(κ1C_T + δ1)P̄1 + (…)P̄0.

C8's "uniform factor on eff" (C8CH:21-27; C8R:47-48) is a uniform scaling of all three A. It is exact as a model of a τ-
or Ā-only improvement with (C_T, D_lo, D1, D2) fixed. It is conservative for a D_lo improvement, because δ1 and δ2 also
fall then. It does not describe Lemma G or mixed provenance. On the tail, S_I1 has C2 provenance on every field, so the
model applies there.

Which branch of the minimum is active:
- Under I1 the τ/D_lo branch is active (C2ADJ:255-257). The Ā certificate is inert.
- Under I2 at 306, A0 = `3429/500` = I2's Ā (C12:125; C11R_COMPARISON.json:75), so the Ā branch is active.

**Where the Lemma SM floor enters.** It never enters Γ.

- It constrains the feasible A0: any admissible supply has A0 = eff ≥ Λ_k (C4T:8-18; AD:51).
- Within the atom-constant family and with A1 = A2 ≥ 0, this gives Γ ≥ g_hi + ρ·x_hi·(|C_lo| + Λ_k·P̄2). That is the
  C4/C7 exclusion argument at 309:
  - C4ADJ:92-99;
  - C8R:63-70: *"the clause tolerates `A0 ≤ 3.266416` and the floor forces `A0 ≥ 3.586306`"*;
  - the C5-T ceiling 3.266415728267196 (C5FC:17).
- It is monotone in A0 only while the intersection stays non-empty (C4T:96-99).

---

## 3. Inequality steps where looseness can arise

1. **Interval hull of g(e0) from independent R and D.** g_hi = R.hi − e0·D.lo (KB:166; D5:88). No R/D correlation is
   used, and no joint object exists (C5 ledger D4 "KILLED … DATA", `phase_3/C5_ROUTE_SEARCH.md`:54; C6 *"NEVER
   EXISTED"*, C6_ADJUDICATION.md:602-607).
2. **Outward-rounded Arb balls in the K1 record.** R_interval, D_interval and R2_interval are Arb balls
   origin ± arb(0, eps.abs_upper()) (AD:137-141). The measured over-width of the record against the exact rebuild is
   2.7–3.6·10⁻⁸ (TCT:147-151).
3. **Generic (undeflated) midpoint eps inside R and D.** eps(F) = C·f_F and eps(D) = C(f_D + k1·eps(F)) (TCT:35-37;
   AD:127-128). Lemma SM(d) says C_upper is the non-sharp one-sided bound (AD:58-61). The tail consumer does not apply
   Corollary T to R or D (deflation domain (0,148): TF2:63, 136; DC:180).
4. **Mean-value transport, sign-blind and with the endpoint weight.** |g(e) − g(e0)| ≤ ρ·sup|t·R″| ≤ ρ·x_hi·M
   (BRIDGE:44). |t| ≤ x_hi is used over the whole range, and |R″| ≤ M = max(|H_lo|, |H_hi|) is sign-blind. C5-T removes
   the |t| slack (1.21–1.29 %, C5DEC:8, 71, 134, 197) and shows that sign-awareness buys nothing on the tail (C5MECH:31-36).
5. **One whole-cell M.** A single sup over the whole cell is used, not sub-cell pieces. C5ADJ:207-209 lists *"a midpoint
   or sub-cell enclosure of `R''`, any bound on `R'''`"* as unexcluded third inputs.
6. **Intersection and magnitude.** M = min(M_R2, max(|a|, |b|)) (D5:85-86). This is only a max/min; it is not lossy
   beyond taking the magnitude of the signed interval.
7. **Independent summation over r (triangle inequality) and interval W terms.** 𝓗_5 sums centre ± half_r with weight
   1/5 over r, and the W intervals with weights c ≥ 0 (TCTR:195-209; TC:84). No cancellation between objects r and no
   dependency between W and F errors is used. The W endpoints are frozen enclosures (C4ADJ:263).
8. **Error identity bounded term by term.** |E″(a)| ≤ A0‖φ″‖ + 2A1‖φ′‖ + A2‖φ‖ (TC:80). Each term is operator-at-atom ×
   sup-norm. **The order-0 channel bound is sharp only at f = 1**: *"Replacing `A0‖φ_H‖` by `(Ĝ|φ_H|)(a)/D_e` … escapes
   the floor entirely"* (C4ADJ:256-259; AD:51, 58-61).
9. **Atom constants.**
   - Lemma G uses submultiplicativity, ‖∂R‖ ≤ C·k1·C and ‖∂²R‖ ≤ 2C·k1·C·k1·C + C·k2·C (TCT:30-33).
   - Lemma Dv′ uses quotient-rule bounds term by term (AD:74-77, 88-89).
   - Ā_eff = min(Ā, τ/D_lo), where τ/D_lo is sup τ over inf D taken *independently* over the cell. *"`τ/D_lo` computed
     from composed `τ` (max) and composed `D_lo` (min) is ≥ the true cell-wise supremum"* (C2ADJ:257-258).
   - Sub-block composition takes the max of the uppers and the min of D_lo (DC:166-170; C2 registry `sub_rows`).
     Observation from committed strings: at 306 and 307 every composed C2 constant equals sub-block 0's value (the
     left-most sub-block), e.g. REGISTRY_C2.json:182-185 vs :203-206 and :347 vs :216 (306), and :351-354 vs :372-375
     and :532 vs :385 (307). The cell constants are therefore set by the lowest-drift 1/100 sub-block.
10. **Rational upper bounds κ1, κ2** of the Gaussian moments (DC:55-56). The slack is negligible.
11. **D4 minimum at the A level rather than the operator level.** It is sound, but looser than the componentwise best
    operator tuple (C3's D′, CRIT `operator_mixed`).
12. **Taylor remainders.** p_j bounds use the integral remainder with ‖φ⁗‖ ≤ Env4 uniformly and |t| ≤ ρ for every term
    (TC:55-57, 73-75; TCR:77-79). Each Taylor term is bounded separately (triangle inequality).
13. **Env4.** φ⁗ = S⁗ + Σ C(4,i)K_iF̃^(4−i), bounded by the triangle inequality, submultiplicativity (k_i·s_X) and
    |t| ≤ ρ (TC:39-44; TCR:69-71).
14. **f_G (P2′).** ‖S‴ + 3K1Ĥ + 3K2D̂ + K3F̂‖ ≤ σ3 + 3k1·s_H + 3k2·s_D + k3·s_F, with no cancellation (TCTR:142-150).
    The implementation also adds ε_src[3] *"on top"*, a redundant extra allowance because the identity already uses the
    true source (TCT:59-61; TCTR:172).
15. **σ3 and σ4 towers.**
    - The Leibniz recursions compound triangle bounds, and ‖h_j‖ ≤ 1 (TCTR:80-91).
    - The σ4 cell tower adds a mean-value correction ρ·P[j,4] (TCTR:111).
    - The tower is loose at order 3 (TCT:79-80: *"σ3 = 5.9, 16.9, 36.5, 67.2 … against adopted values of 3.04, 3.41,
      3.81, 2.25"* at 309). The (P3′) minimum repairs order 3 only. σ4 at r = 4 falls *"from the pure tower's 345.10 to
      235"* (TCT:104-107).
16. **Ĝ := 0.** The Taylor candidate stops at order 2. The order-3 drift t·F‴(e0)(a) is not represented as centre
    motion; it is charged to the radius via ρ·A0·‖φ‴(e0)‖, a sup-norm bound (TCT:44-57, 63-72).
17. **Direct clause only.** The chain clause (N32) is ignored by the adoption quantity (C2ADJ:222-227).
18. **Bisection in requirement and margin.** The last passing endpoint is returned, so these never overstate (D5:92-105;
    `c2_critical_ratio.py`:95-96).

---

## 4. Committed per-cell decompositions and sensitivities for 306–309

Evidence types:
- **EXACT** — an exact evaluation of the frozen consumer on certified inputs under a certified supply;
- **EXACT-KO** — exact but at a non-certified tuple (a knockout such as A1 = A2 = 0);
- **CF** — counterfactual / hypothetical scaling;
- **DIAG** — scaled sweep with the crosscheck aligned (C5 convention; C5 `knock`, `c5_common.py`:70-108);
- **MC** — Monte-Carlo or float diagnostic.

| # | quantity | 306 | 307 | 308 | 309 | where | type / supply / clause |
|---|---|---|---|---|---|---|---|
| 1 | Γ | −0.030469257709306738 | 0.033132953404317905 | 0.10270008356594545 | 0.16224941061997425 | D5J:47,79,111,143 | EXACT / S_I1 / direct |
| 2 | magnitude = M_after | 3.5119460127500672 | 3.451359412896 | 3.4524564789357517 | 3.400934402274074 | D5J:53-58,85-90,117-122,149-154 | EXACT / S_I1 |
| 3 | required uniform A reduction | 1.0 | 1.1407635748126312 | 1.5002877825423833 | 1.8990148694205993 | D5J:66,98,130,162 | EXACT (bisection) / S_I1 |
| 4 | margin M_needed/M_after | 1.111935 | 0.891286 | 0.704541 | 0.579202 | C2ADJ:67 | EXACT / S_I1 |
| 5 | Γ at every A ×1.25 | 0.02916329270548208 | 0.10026123289693721 | 0.17969560795046136 | 0.24793043042352722 | ROB:16,28,40,52 | CF / S_I1 / direct |
| 6 | Γ with perfect order-3 (f_G → ε_src[3], s_G = |Ĝ(a)| = 0) | −0.21751603611711204 | −0.17175591984010868 | −0.12665519383926 | −0.08732986165115685 | ROB:17,29,41,53; CRIT:106,120,134,148 | CF / S_I1 |
| 7 | magnitude with perfect order-3 | 1.0986970521070953 | 1.1311143264496613 | 1.1744072175613398 | 1.199542379772895 | ROB:23,35,47,59 | CF / S_I1 |
| 8 | critical s_G/s_H (real Ĝ, 0.681 model) | 54.8673607560044 | 37.32219327967945 | 23.26034927841336 | 14.15799020701014 | ROB:20,32,44,56 | CF (evidence model) / S_I1 |
| 9 | Γ, Lemma G | 0.01911558504907568 | 0.08511776989151419 | 0.15834296474510035 | 0.2261171664714765 | CRIT:249,263,277,291 | EXACT / G |
| 10 | critical s_G/s_H, Lemma G | 47.986101203397524 | 32.032829281673614 | 19.195056304643465 | 10.54598319680089 | CRIT:252,266,280,294 | CF / G |
| 11 | Γ, C1 | −0.005719468367263504 | 0.061683080290831596 | 0.13619454282611712 | 0.19881031084487408 | CRIT:33,47,61,75 | EXACT / C1 |
| 12 | Γ, operator_mixed (D′) | −0.03619777996457939 | 0.026354631323170525 | 0.09456414496566364 | 0.15301968889418385 | CRIT:393,407,421,435 | EXACT / D′ (not an r2 supply) |
| 13 | Γ, S_I2 | 0.005159101140006536 | — | — | — | C12:129 | EXACT / I2 / direct (sealed, once) |
| 14 | Lemma G TCT0 table: adopted M; mag; M needed; Γ before; Γ after; margin | 5.4270; 4.151682; 3.9051; +0.117964; +0.019116; 0.941× | 5.3352; 4.040057; 3.0761; +0.199484; +0.085118; 0.761× | 5.2961; 4.005124; 2.4324; +0.288317; +0.158343; 0.607× | 5.2699; 3.964274; 1.9698; +0.374145; +0.226117; 0.497× | EXD:110-113 | EXACT / G |
| 15 | A0-only / uniform reduction needed (G) | 1.0913136533967474 / 1.0710617972773384 | 1.5019033758901599 / 1.361618278450789 | 2.205574719994057 / 1.7713435857400779 | 3.294278768636855 / 2.2529025166407797 | `ATOM_CONSTANT_REQUIREMENT.json`:12-36 | EXACT (bisection) / G |
| 16 | per-r σ3, σ4, f_G, Env4, rad | §1 N20, N21, N23, N24, N26 | same | same | same | TFJ:4745-4996 | EXACT (A-independent except rad) / G |
| 17 | 12-term radius shares (A0ρf_G; A0ρ²Env4/2; A1ρ²f_G) | 0.5983560203231182; 0.17000286433626902; 0.16713507280222797 | 0.5803594595384862; 0.18714575322592514; 0.16445975489513068 | 0.5647903310157965; 0.2023847668735945; 0.16217506600654977 | 0.553420848377577; 0.21708301545495404; 0.15800452108364518 | D1J:267/263/275, 451/447/459, 636/632/644, 821/817/829 | EXACT / C1 |
| 18 | f_G share (grouped) | 0.78493144543567 | 0.7644034300030144 | 0.7467227795739954 | 0.7307909448688887 | D1J:189,373,558,743 | EXACT / C1 |
| 19 | Env4 share (grouped) | 0.20442175737043453 | 0.22565840400321727 | 0.24466677951396842 | 0.26220003761664684 | D1J:193,377,562,747 | EXACT / C1 |
| 20 | 10 % single-input magnitude gains (A0, A1, A2, A_all, D_lo, τ, C_T, D1, D2) | D1J:309-367 | D1J:493-552 (C_T clamped) | D1J:678-737 (clamped) | D1J:863-922 (clamped) | D1J | CF / C1 |
| 21 | S̄ split: A0·p2 / 2A1·p1 / A2·p0 (% of S̄) | 81.4946010624007 / 16.80152427160426 / 1.7038746659950406 | 81.56107503551327 / 16.771446740439206 / 1.6674782240475226 | 81.65849469865014 / 16.72673110664821 / 1.6147741947016507 | 81.94654148245344 / 16.512706314134338 / 1.5407522034122179 | C5DEC:34-45,97-108,160-171,223-234 | EXACT / D′ |
| 22 | within A0·p2: A0·f_H / A0·ρ·f_G / A0·ρ²·Env4/2 (%) | 0.1146132975416325 / 63.37429889225686 / 18.005688872602203 | 0.11255939514505924 / 61.58839800839967 / 19.860117631968542 | 0.10190566876572453 / 60.04153815919196 / 21.515050870692455 | 0.0853537818494967 / 58.79748314449863 / 23.06370455610532 | C5DEC:50-62,113-125,176-188,239-251 | EXACT / D′ |
| 23 | g_hi; centre; S̄; M_needed | see N15, N12, N26 | | | | C5DEC | EXACT (A-independent except S̄) |
| 24 | Γ_C5T; penalty C5T vs frozen | −0.03942593367711184; 0.2632482222172612 vs 0.2664763759297936 | 0.022641576453031827; 0.29428036694791665 vs 0.2979934218180554 | 0.09022244922018692; 0.3351176204548199 vs 0.3394593162002966 | 0.148146342573649; 0.371472388067586 vs 0.3763457343881208 | C5FC:44,63-64 / 81,100-101 / 118,137-138 / 155,174-175 | EXACT / D′ / C5-T |
| 25 | M_needed_C5T | 3.9529425406367737 | 3.114961360548343 | 2.463911269745421 | 1.9956699149869883 | C5FC:47,84,121,158 | EXACT |
| 26 | Γ at A1 = A2 = 0 (A0 as certified, D′) | −0.079278659 | −0.021906451 | +0.039567846 | +0.092812423 | C4T:74-77; C3ADJ:348-351; C5SEN:231-240 | EXACT-KO / D′ / direct |
| 27 | critical A0 at A1 = A2 = 0 | — (C3ADJ gives 8.5136) | — (C3ADJ gives 6.1725) | 4.375228833136 | 3.214236022678 | C4T:74-77; C3ADJ:348-351 | EXACT-KO |
| 28 | 306 critical A0 with A1, A2 at certified values | 7.1501 (certified A0 6.0045) | — | — | — | C3ADJ:297-298 | EXACT-KO / D′ |
| 29 | knockouts: f_G → 0; Env4 → 0; both; σ3 → 0; σ4 → 0; both σ; sups halved; sups → 0; ρ halved; all four → 0 | not computed | C5SEN:86-277 | same | same | C5SEN:65-281 | DIAG / D′ / direct |
| 30 | Γ at the C4 floor / diagnostic Λ (A1 = A2 = 0) | — | diag 4.5929: −0.06023471904979815 | floor 3.512733596022926: −0.04046754262884166 (CERTIFIED); diag 4.311: −0.0030135621984619903 | floor 3.297250281519544: 0.004661129657978103 (CERTIFIED); diag 4.0473: 0.0467753283095086 | C5SEN:2-41 | EXACT-KO + MC |
| 31 | 309 perturbation → critical A0 | — | — | — | residuals ×0.9 → 3.214686; sup_S0 ×0.5 → 3.367552; sup{F,D,H} ×0.5 → 4.160309; ρ ×0.5 → 7.534321 | C4ADJ:229-235 | DIAG |
| 32 | 309 exclusion fragility: slack in critical A0 (C5-T / frozen); voiding cuts | — | — | — | 0.9439874105892017 % / 2.582705758256717 %; all_four 0.6076076662635768 %, sup-norms 2.0561597034092847 %, f_G 1.3039933276160391 %, σ3 3.236522299841146 %, σ4 3.6694468495892534 %, Env4 3.3226707586807693 % | C5FC:15-31 | EXACT (clause) / DIAG (sweeps) |
| 33 | uniform-A margin at 306 | C1 1.0217239006485588; C2 = D4 1.1277375254679296; D′ 1.1554876238748288; D′ + C5-T 1.171431 | — | — | — | C3B:32,45,58,84; C8R:52 | EXACT (bisection) |
| 34 | ×eff to close / to adopt (C5-T, D′) | — / 1.067071 | 1.096007 / 1.370009 | 1.438423 / 1.798029 | 1.818354 / 2.272943 | C8R:52-55 | CF |
| 35 | 307 alpha-lever projected eff tightening | — | 1.137406 (floor α) / 1.098807 (α = 1.07), against required 1.096007246 / 1.370009058 | — | — | `p5y_k5_tail_c9_e1_cell307/README.md`:37-42 | CF (projection) |
| 36 | 306 C5-T at A ×1.25 (D′) | +0.018069433 | — | — | — | C5ADJ:157 | CF |
| 37 | C6 E1 oracle (frozen clause) | — | −0.0602 | −0.0030 | +0.0468 | C6_ADJUDICATION.md:615 | DIAG |
| 38 | 309 Λ lower bound; MC Λ | — | — | MC 4.311 (C4T:119-121) | 3.586306094 (C7 OPEN_NOTES:32); MC 3.98842 ± 0.00050 (:61) | | EXACT bound / MC |
| 39 | Campaign B σ3 tower vs adopted, σ4(r=4) repair, magnitude | — | — | — | σ3 tower 5.9/16.9/36.5/67.2 vs adopted 3.04/3.41/3.81/2.25; σ4 345.10 → 235; magnitude 4.2617 → 3.9643 | TCT:79-80, 104-107 | EXACT / G |
| 40 | Lemma-G per-r decomposition at 309 (r = 3, 4) | — | — | — | r3: rad 4.4978, A0ρf_G 2.463 (55 %), A0ρ²Env4/2 1.139 (25 %); r4: 4.4136, 1.552 (35 %), 2.049 (46 %) | EXD:123-126 | EXACT / G |

---

## 5. Ambiguities and inconsistencies

1. **Two authoritative clauses.**
   - C5ADJ:561-565 makes C5-T authoritative for x_lo > 0, and C8 builds every factor on it (C8R:43;
     `C8_DECISION.json`:24).
   - Floor r2 pins the adoption quantity to the frozen direct clause (FLR:76). C12-R2 used that quantity.
   - FLR's base clause says *"the campaign's own frozen closure rule"* (FLR:87), which leaves room for a campaign to
     freeze C5-T. The field `adoption_quantity` does not leave that room.
   - The route audit review N5 records the mismatch (ROUTE_AUDIT_R1_REVIEW.md:185-201). Any "×eff" figure from C8 or C9
     is a C5-T/D′ number, not an r2 number.
2. **Three "306 margins" under different supplies and clauses:** 1.1277 (S_I1, frozen), 1.1554876 (D′, frozen) and
   1.171431 (D′, C5-T). Their requirements are 1.108452 / 1.081806 / 1.067071 (C8ADJ:124-128). A fourth, different
   notion is also called "margin": M_needed/M_after, 1.112× (C2 README:74; C2ADJ:475). The C2 README "margin" column is
   *not* the F2 uniform-A margin.
3. **Is g_hi improvable?**
   - C5 phase 1: *"no — sealed"* (`C5_BLOCKER_DECOMPOSITION.md`:17).
   - C5ADJ:207-209: *"everything that improves `g_hi` … remain[s] entirely unexcluded."*
   - AD Corollary T/C step 2 tightens R and R′ at the midpoint for registry-covered cells (AD:149-150), but the tail
     consumer deflates only on [0,148] (TF2:63, 136). The registries covering 306–309 (C1, C2) are used only for H.
   - Campaign B's T1 was refused for the *whole-cell H* use of Corollary T (TAIL_ROUTE_COMPARISON.md:10; EXD:161-167).
     That refusal says nothing about the midpoint R/D use.
   - I found no committed evaluation of this lever.
4. **Supply labelling of the decompositions.** D1 (D1J; `D1_BLOCKER_DIAGNOSIS.md`) is under **C1** (the JSON key
   `closes_under_C1_constants`). C5DEC is under **D′** (via `c3_selector.build`, `c5_common.py`:61-66). The Campaign B
   tables are under **Lemma G**. C2's adopted supply S_I1 has **no** committed per-term decomposition or sensitivity; only
   Γ, magnitude, requirement, ×1.25, perfect-order-3 and critical ratio exist for it.
   - C5's README summary (*"59–62 % … 20–23 %"*) covers 307–309 only (`C5_BLOCKER_DECOMPOSITION.md`:44-51). At 306 the
     C5DEC figures are 63.37 % and 18.01 %.
   - C3ADJ:188 names its Γ column "mixed", and CRIT names the same numbers `operator_mixed`.
5. **"Perfect order-3" is not physically attainable.** In the definitions in CRIT, ROB, D1J and C5SEN, the order-3
   dict has s_G = |Ĝ(a)| = δ_G = 0, so f_G falls to ε_src[3] while s_F, s_D, s_H stay (`c2_critical_ratio.py`:189;
   `c2_d1_blocker.py`:245-248). A candidate with zero supremum and zero residual would need F‴ ≡ 0. The
   `c2_critical_ratio.gamma_with` docstring itself warns that the limit does not agree with the zero-candidate route
   (`c2_critical_ratio.py`:73-77).
6. **The ×1.25 degraded Γ (ROB `Gamma_degraded_125pct`) has no committed producer.** It appears only in ROB and in review
   text. The critical-ratio producer was likewise first *"an uncommitted scratch file"* (`c2_critical_ratio.py`:3-7). The
   C2 adjudicator re-derived the ×1.25 values independently (C2ADJ:65-66). F2 for 306 therefore rests on an adjudicator
   re-derivation plus a producer-less JSON.
7. **F2 strictness.** The text is *"Γ < 0 still holds when …, i.e. the cell's uniform-A margin is ≥ 1.25"* (FLR:99). At
   margin exactly 1.25, Γ(1.25A) = 0, which fails the strict Γ < 0. C8ADJ:134-137 notes the same infimum issue for the
   ×eff factors.
8. **Unpinned loads inside the frozen consumer.** D5 loads `tail_forecast_r2.py` *without* a sha pin (D5:144). That file
   imports `tct_rule` from the path (TF2:40-41). D5 uses the ATI extract for R, D, R2 and M_R2 without re-checking it
   against the records (the field-by-field check is in `TF2.main`, TF2:327-347, which D5 does not call). Floor r2
   compensates by binding `tct_rule` by blob (FLR:76). C12-R2 records the sha256 values of `tct_rule`,
   `tail_forecast_r2` and `adopted_inputs` (C12:79, 106, 109). No check binds `tail_forecast_r2` in floor r2's quantity
   text.
9. **The "ρ halved (cover refinement)" diagnostic is not a cover refinement.** C5's `knock` scales `meas["rho"]` only,
   i.e. the TC-T Taylor ρ (`c5_common.py`:85-86). `direct()` takes the transport ρ·x_hi from `cells.json` (D5:87-88), and
   g_hi would change with new midpoints. C5SEN:247-262 and C4ADJ:235 therefore model half of the effect. They are labelled
   DIAG, but they are quoted as *"cover refinement"* (C5ADJ:215).
10. **The ε_src[3] allowance is redundant.** It is added on top of f_G, which already carries the true source
    (TCT:59-61). It is small (≈0.003 mean) but double-counted.
11. **The meaning of `eff` depends on the supply.** C8 treats eff = A0 and a uniform factor on eff (C8CH:23-27). Under I1
    eff = τ/D_lo, with the Ā certificate inert (C2ADJ:255-257). Under I2 (306) eff = Ā = `3429/500` (C12:125;
    C11R_COMPARISON.json:75). FLS:141 calls 3429/500 the exact supremum of C11R's F_H weight *used as C_T* in the C11RD
    propagation, while the consumer takes C_T from C11R's outward-rounded record (FLS:144-145). The same rational thus
    appears as I2's Ā, τ and (in propagation) C_T, and is quoted in the governance documents with different roles.
12. **The chain clause is excluded from the adoption quantity**, although the frozen theorem's pass condition includes it
    (BRIDGE:30-33; KB:185-189). At m = 1, 2, 3 the tail passes via "chain" (D5J:181-222). γ_306 feeds U_307, so a
    closure of 306 changes 307's chain bound. That coupling is outside every committed adoption rule. Campaign B's
    μ ≥ ≈ −0.29 target (TAIL_ROUTE_COMPARISON.md:4-5) was never pursued.
13. **Scope of floor r2.** Its F1′ and all of its operative text cover cell 306 only; 307–309 are *"OUT OF SCOPE"*
    (FLR:107; FLS:196-203). No committed rule fixes the adoption quantity or supply for 307–309 beyond r2's standing
    base clause plus F2.
14. **Numbers in the TCT prose versus the evidence.** TCT:163-164 gives 0.94×/0.76×/0.61×/0.50× (Lemma G margins). They
    match EXD:110-113 (0.941/0.761/0.607/0.497). TCT:39 gives *"A0 = 5.782–7.733"*, which is consistent. I found no
    numeric contradiction here.
15. **The D1 diagnosis table headers omit the supply.** `D1_BLOCKER_DIAGNOSIS.md`:11-17 lists "required uniform
    A-reduction 1.262057 / 1.663451 / 2.101597". These are C1-supply values (CRIT C1 :52, 66, 80), not C2's adopted
    1.1407… / 1.5003… / 1.8990…. The table does not say so.

---

## 6. What I did not do

- I did not open the off-host K1 record store; the ATI extract was the only record view.
- I did not verify any exact-rational string by arithmetic.
- I did not recompute or re-order any quantity.
- I did not read REGISTRY_C1 line-by-line; its per-cell constants are quoted from D1J.
- I did not read the C9–C12 driver code or the C11R/C11RD certifier code beyond the comparison JSON fields cited.
