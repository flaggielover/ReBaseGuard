# Stage F — Level-4 requirements reconstruction

**Purpose.** Recover what Level 4 was *pre-specified* to require, before assigning
any verdict. No requirement is invented here; every row cites a repository
document that predates the outcome it governs.

---

## 1. The central finding: no Level-4 closure specification exists

An exhaustive search found **no frozen Level-4 closure-criteria document and no
Level-4 status taxonomy** anywhere in the repository:

```
grep -rn "LEVEL-4-|LEVEL_4_CLOSED|LEVEL 4: CLOSED"  ->  no matches
```

The authoritative Level 1–3 closure report is explicit:

> `LEVEL 1–3: CLOSED` / `READY TO ENTER LEVEL 4`
> **"Level 4 is not authorized by this document and has not been started."**

and classifies Level-4 material as open, not as a specified target:

| ID | Statement | Label |
|---|---|---|
| L-09 | Level-4 multi-cycle dynamics; SR detector; `Gamma_SR > 2` | **OPEN** |
| L-10 | Global bifurcation / period-2 / invariant law / ARL theory; other `(k,h,m)` | **NOT CLAIMED** |

**Consequence.** Level 4 was defined *incrementally*: each stage (A, B, C, C.1,
D, E) arrived with its own brief, was frozen into its own protocol with its own
decision rule, and was closed against that rule. There is therefore no
pre-existing taxonomy to reuse, and Stage F falls back to the conservative
four-label set. This absence is itself a Level-4 finding: **the project never
pre-specified what "Level 4 closed" would mean**, which is precisely the
condition under which post-hoc definition is most tempting and least legitimate.

---

## 2. Two documents that *do* carry pre-specified scope

### 2.1 `staged_task_ranking.csv` / blueprint §5 — the MANDATORY classification

Dated **2026-08-22**, delivered as the Stage D theory blueprint + pilot, i.e.
**before** the Stage D confirmatory campaigns. It classifies twelve tasks:

| task | class | Stage D / repository outcome |
|---|---|---|
| m>1 derivative theorem | **MANDATORY** | **FAILED** — D2.3, 0/8 at the frozen primary step |
| SR derivative theorem | **MANDATORY** | **not proved** — numerical only (D1.2/D1.3) |
| m-rho phase map | **MANDATORY** | **NOT RUN** — D4, gate required D2 to survive |
| SR Monte Carlo derivative | **MANDATORY** | **DONE** — D1.2/D1.3 PASS |
| general location-family theorem | STRONG EXTENSION | **OPEN** — A1 unproved (D3.1) |
| Student-t campaign | STRONG EXTENSION | done (D3.2); `t3` **AMBIGUOUS** |
| contaminated Gaussian campaign | STRONG EXTENSION | done (D3.2), both families pass |
| h-rho phase map | STRONG EXTENSION | not run |
| SR nonlinear map | STRETCH | done as **CANDIDATE** (D1.4) |
| m>1 rigorous certificate | STRETCH | not attempted |
| SR rigorous period-2 | STRETCH / LEVEL-4+ | not attempted |
| skewed campaign | STRETCH / LEVEL-4+ | not attempted |

**MANDATORY tally: 1 of 4 delivered, 1 FAILED, 1 NOT RUN, 1 unproved.**

### 2.2 `staged_kill_gates.csv` — the gate document

| gate | verdict recorded at pilot time |
|---|---|
| D1 SR | PASSED — NOT KILLED |
| D2 m>1 | **PARTIAL KILL** |
| D3 non-Gaussian | NOT KILLED numerically; **rigour AT RISK** |
| D4 phase diagram | PROCEED, **DEMOTED** |

### 2.3 `rebaseguard_level4_design.md` — the earlier gate (2026-08-21 10:48)

Predates the Stage B certificate by ~3.5 hours. Its gate recommendation was
**`PROCEED-ALTERNATIVE-DYNAMICS`**, explicitly *not* `PROCEED-PERIOD2`, on the
ground that certifying the orbit would be "certifying a feature of a skeleton
that does not govern the observable process". Its ledger records:

| # | Claim | Label |
|---|---|---|
| 4 | `Gamma > 2` | OPEN / REQUIRES-RIGOROUS-CERTIFICATE *(later closed by the Arb certificate)* |
| 8 | `g` strictly decreasing ⟹ unique 2-cycle | needs certificate *(later delivered by Stage B)* |
| 9 | 2-cycle attracting, no period-4 | needs certificate *(later delivered by Stage B)* |
| **12** | **Period-2 describes the stochastic long run** | **FALSIFIED** |
| **13** | **Stationary mass away from 0 diagnoses reuse** | **FALSIFIED** |
| **14** | **Reuse is the dominant cause of ARL loss** | **FALSIFIED** |
| 16 | Detector-generality of the mechanism | **OPEN** (two Gaussian `m=1` witnesses only) |

---

## 3. Is the MANDATORY classification a Level-4 closure requirement?

The instruction requires this be settled on provenance, not convenience.

**Evidence that it is only a Stage-D execution priority:**

* The document is titled *"ReBaseGuard Level 4 — **Stage D**"*; its scope is Stage D.
* The table sits under a section headed **"TASK RANKING"**, with columns
  `score`, `p_success`, `compute_cost`, `proof_cost`, `reviewer_value` — the
  vocabulary of prioritisation, not of pass/fail criteria.
* The accompanying prose reads as sequencing advice: *"The two derivative
  theorems top the list because this session made them cheap."*
* A separate document, `staged_kill_gates.csv`, **is** the gate artifact and
  uses `kill_condition` / `verdict`. Ranking and gating are distinct files.

**Evidence that it is binding Level-4 scope:**

* It uses the word **MANDATORY**, not "high priority".
* It distinguishes a class **"STRETCH / LEVEL-4+"**, which presupposes a
  Level-4 scope boundary — so the author was classifying *relative to Level 4*.
* The blueprint elsewhere refers to work needed *"before Level 4 closure"*.

**Resolution: AMBIGUOUS.** Authorship intent cannot be settled without choosing
the reading that suits the outcome. Per the governing instruction, the
**conservative (stricter) interpretation applies: MANDATORY is treated as
binding Level-4 scope evidence.**

### 3.1 The verdict does not depend on this choice

This matters, and is stated so the interpretation cannot be blamed for the
result. **Both readings converge:**

* **Strict reading** (MANDATORY = Level-4 requirement): 3 of 4 MANDATORY items
  are FAILED / NOT RUN / unproved ⟹ Level 4 is not closed.
* **Lenient reading** (MANDATORY = Stage-D priority only): Level-4 closure then
  rests on the per-stage frozen decision rules, which returned
  `STAGE-C-PARTIAL`, `STAGE-D-PARTIAL`, `STAGE-E-PARTIAL` ⟹ Level 4 is not closed.

No reading available on the evidence yields Level-4 closure.

---

## 4. Requirements table

| Requirement | Original source | Frozen before outcome? | Mandatory / stretch | Evidence now available | Status |
|---|---|---|---|---|---|
| Level 1–3 closure holds as the foundation | `closure/LEVEL_1_3_CLOSURE_REPORT.md` | yes | prerequisite | Lean chain + Arb certificate; 90 tests | **PASS** |
| Multi-cycle oracle, reproducible | Stage A brief | yes | mandatory | Gates 4.1/4.2 closed, 290 tests | **PASS** |
| Conditional map `F_rho`, derivative correspondence at `m=1` | Stage A brief | yes | mandatory | three-route agreement | **PASS** |
| `Gamma_CUSUM > 2` rigorously | L1–3 ledger #4 | yes | mandatory | Arb enclosure `[3.9243, 27.8494]` | **PASS** |
| Rigorous period-2 for the deterministic skeleton at `rho=1` | Stage B brief | yes | mandatory (as briefed) | `STAGE-B-CLOSED-RIGOROUS-PERIOD2` | **PASS** |
| Stability-aware reuse policy with monitoring consequences | Stage C brief (`36bd6ba0…`) | yes | mandatory | `STAGE-C-PARTIAL`; C6 failed and left failed | **PARTIAL** |
| Confirmatory sensitivity of that policy | Stage C.1 (`7b45c091…`) | yes | mandatory | `STAGE-C1-CLOSED-CONFIRMED-SENSITIVITY` | **PASS** (narrow scope) |
| **SR Monte Carlo derivative** | ranking (MANDATORY) | yes | **mandatory** | `Gamma_SR = 17.3198 ± 0.0280`; D1.2/D1.3 PASS | **PASS** |
| **`m>1` derivative theorem** | ranking (MANDATORY) | yes | **mandatory** | **D2.3 FAILED**, 0/8 at `h = 0.05` | **FAIL** |
| **SR derivative theorem** (proved, not measured) | ranking (MANDATORY) | yes | **mandatory** | numerical only; no proof exists | **OPEN** |
| **`m`–`rho` phase map (D4)** | ranking (MANDATORY) | yes | **mandatory** | **NOT RUN** — protocol gate required D2 to survive | **FAIL (not run)** |
| Operational consequence of the `Gamma_m` crossing | Stage D protocol D2.5 (`925adecf…`) | yes | mandatory within D | **MATHEMATICAL, NOT OPERATIONAL** | **NEGATIVE RESULT** |
| Non-Gaussian robustness | Stage D D3 | yes | strong extension | 6/6 frozen estimand; `t3` **AMBIGUOUS** | **PARTIAL** |
| General location-family theorem | ranking (STRONG EXTENSION) | yes | stretch | A1 **UNPROVED** for every non-Gaussian family | **OPEN** |
| Semi-real external validation | Stage E protocol (`974487…`) | yes | mandatory within E | **0/3** tasks met H-E5 | **FAIL vs its own rule** |
| Prior-art / novelty verification | `rebaseguard_level4_design.md` §J item 4 | yes | mandatory ("hygiene item") | external reviews not persisted in repo | **OPEN / provenance gap** |
| Reproducibility of every stage | all protocols | yes | mandatory | 641 tests; all reproduce scripts present | **PASS** |
| Protocol integrity (hashes, no post-hoc edits) | all protocols | yes | mandatory | 4/4 hashes verified; 3/3 pre-commitments verified | **PASS** |

**Tally:** 9 PASS · 3 PARTIAL/negative · 3 FAIL · 3 OPEN.

---

## 5. Mechanical consequence

At least one pre-specified mandatory requirement is **explicitly FAILED**
(`m>1` derivative theorem / D2.3), one is **FAIL by non-execution** (D4), one
**fails against its own frozen rule** (Stage E, 0/3), and one is an **unclosed
hygiene item** (novelty verification). Substantial Level-4 results were
nonetheless established: a machine-checked identity, an Arb-certified bound, a
rigorous skeleton period-2 certificate, a confirmed sensitivity result, and a
two-detector numerical replication.

Under the fallback taxonomy this is, mechanically:

> **`LEVEL-4-PARTIAL`** — at least one mandatory Level-4 requirement remains
> unmet, while substantial Level-4 scientific results were established.

`LEVEL-4-CLOSED-WITH-LIMITATIONS` is **not available**: it may be used only "if
the original architecture permits such closure", and no original architecture
defining Level-4 closure exists. Choosing it here would be inventing the
requirement after seeing the outcome, which is the specific failure mode this
reconstruction exists to prevent.
