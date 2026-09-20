# Independent adjudication r1 — sealed theorem-TC successor (CUSUM K5 lower front, cells 11–44)

Adjudicator: fresh context. Did not write the successor, did not review it before the freeze, did not authorize it.
Brief: `review/ADJUDICATION_BRIEF.md`. Worktree `/Users/suzhe/ReBaseGuard-k5lf` at `ad108619`
(branch history `p5y-postk1-frontier`). Date 2026-09-20.

Method: reproduce rather than trust. Everything below was recomputed locally from the committed bytes with
stdlib Python (exact `Fraction` arithmetic). No remote host was contacted. No file was modified except this
directory. Nothing was committed.

**Verdict: `ADJUDICATION = ADOPTED`.** 27 PASS, 6 INFO, 3 NOT_CHECKABLE_LOCALLY, 0 FAIL.

> **State at adjudication.** The brief names `ad108619` as the current commit. The worktree HEAD advanced to
> `7ee92476` (Campaign B, m = 5 tail) *while this adjudication was in progress*; I did not make that commit. I
> re-checked and it disturbs nothing adjudicated here — see rows 1.5 and 8.3. All findings below are stated against
> the sealed range `3f540a33 … ad108619`, which is fixed and unaffected.

---

## 1. Checklist

| # | Check | Verdict | Evidence |
|---|---|---|---|
| 1.1 | Commit order: gates → pre-freeze → freeze → qualification → authorization → guard → tooling → checkpoint → seal → consumption, each an ancestor of the next | PASS | `git merge-base --is-ancestor` OK for all 10 links from `7cb01e38`; `git log 7cb01e38..ad108619` is linear, no merges |
| 1.2 | After the freeze `3f540a33`, nothing outside `evidence/tc_r1/` changes | PASS | `git diff --name-only 3f540a33 ad108619` filtered on the prefix is **empty**; per-step `--name-status` shows only the expected additions (and one `M` on `GUARD.json` at the seal: ALLOW → DENY) |
| 1.3 | Adopted namespaces byte-unchanged since the start frontier `7cb01e38` | PASS | `git diff --name-status 7cb01e38 ad108619` outside `p5y_k5_lower_front_order3/` is **empty**. Tree hashes identical for `p5y_k5_perron_deflated_resolvent` (`db967365`), `p5y_k5b_independent_countersignature` (`f238c648`), `p5y_k1_cusum_aux5_composite_closure` (`48dd56cd`); T-EXT, slot-1 and coverage map r3 are inside that unchanged set |
| 1.4 | Working tree state | INFO | One untracked file: `evidence/tc_r1/checkpoints/CP_005_sealed_consumed.json`. It is a resume aid (README: "checkpoints — resume aids only, never evidence"), is not pinned, and is read by nothing. No tracked file is modified |
| 2.1 | Every protocol pin matches at the seal | PASS | All **84/84** pins in `config/TC_PROTOCOL.json` recomputed locally at `ad108619`: 0 mismatches, 0 missing. All 41 `loaded_repository_modules` are in the pin set. **No pinned path lies under `evidence/tc_r1/`**, so the post-freeze mutable prefix cannot touch a pin — the 84 pins are freeze-immutable by construction |
| 2.2 | Protocol identity | PASS | `sha256(config/TC_PROTOCOL.json) = 10ff7e37e9b6…924f`, equal to the value in SEAL, AUTHORIZATION, GUARD, TC_INDEX, every cell record's `binding`, and TC_CONSUMPTION |
| 2.3 | Qualification ran at the freeze commit and passed S00–S09 | PASS (host-reported for the runtime steps) | `QUALIFICATION_RESULT.json` `S00.head = S00.freeze_commit = 3f540a33…`, `namespace_clean: true`, every `S0x.pass: true`, `verdict: QUALIFIED`; file sha `f95da15f…` equals the value bound by AUTHORIZATION and SEAL. S02/S06/S09 are the run host's own report (authorization Note C) — see 2.4 |
| 2.4 | Runtime pins (`python 3.12.3`, `python-flint 0.9.0`, `numpy 2.5.2`, `scipy 1.18.1`, `venv`, 1 thread) | NOT_CHECKABLE_LOCALLY | No python-flint and no numpy here, and remote access is forbidden. Verified only that the runtime block recorded in all 34 cell records is byte-equal to `TC_PROTOCOL.runtime` and to `QUALIFICATION_RESULT.S02.runtime`, and that `loaded_repository_modules_before == after == 40` on every record |
| 3.1 | Every cell file sha equals TC_INDEX and SEAL | PASS | 34/34 recomputed; addresses are exactly 11…44; `sha256(TC_INDEX.json) = 51c5ca93…` as stated |
| 3.2 | Reproduction of cells 11 and 44 byte-identical to the first run | PASS | `repro/TC_CELL_11.json` and `repro/TC_CELL_44.json` are **byte-equal** to the `cells/` originals (not merely equal modulo metadata), and their shas equal the index entries |
| 3.3 | Ledger: one START and one ok OUTPUT per address, RUN_END with identical reproduction | PASS | 72 rows: 1 RUN_START, 34 START (exactly 11…44, once each), 34 OUTPUT (all `ok`, sha == index), 2 REPRO (11, 44, `identical` and `ok`, sha == index), 1 RUN_END. Every row carries `head = 74d67ef4…`. `sha256(RUN_LEDGER.jsonl) = dd43fd4d…` as sealed |
| 3.4 | CPU accounting and budget | PASS | Σ(34 OUTPUT + 2 REPRO) `cpu_seconds` = 51130.640857267 = `RUN_END.cpu_seconds_total` = `TC_INDEX.cpu_seconds_total`; /3600 = 14.20296 h = SEAL's **14.203**. Under the enforced protocol cap 30, under the frozen prose cap 24, and under the campaign hard cap 40 |
| 3.5 | Each record's binding is consistent with the history | PASS | All 34 records: `protocol_sha256 = 10ff7e37…`, `freeze_commit = 3f540a33…`, `authorization_sha256 = 4b920423…`, `head = 74d67ef4…`, `guard_sha256 = 619ca11b…`. `git show 74d67ef4:…/GUARD.json` **is** state `ALLOW` for exactly addresses 11–44 and hashes to `619ca11b…`; `git show bc4235d0:…/GUARD.json` is `DENY`. Every record is `mode: real`, `identity_gate.identical: true`, 262 fields compared |
| 3.6 | The K1 records consumed are the **adopted** K1 records | PASS | All 34 `k1_record_sha256` values equal `TC_PROTOCOL.k1_record_sha256`, and each equals, **per cell**, the entry `k4_records/aux5_CUSUM_<k>_256.json` in the adopted `COMPOSITE_EXPORT_MANIFEST.json` (sha `29ad1f9b…`, the value pinned by the frozen consumption adapter). This ties the run to adopted K1 evidence without needing the record files |
| 3.7 | Governance file hashes | PASS | `AUTHORIZATION.json` → `4b920423…` (as bound by GUARD, SEAL, every record); `AUTHORIZATION_REVIEW.md` → `5daf81f5…` (as bound by AUTHORIZATION); `QUALIFICATION_RESULT.json` → `f95da15f…`. Governance commit order matches `governance_schema.order` |
| 4.1 | **Independent** recomputation of H_TC,m(k), cells 11–44, m ∈ {1,2,3,5} | PASS | I wrote my own implementation from `theorem/THEOREM_TC.md` alone (Taylor p0/p1/p2, the P3 Env4 envelope, the σ4 closed form for r = 0 and the J/h Leibniz tower for r ≥ 1, rad = A0·p2 + 2A1·p1 + A2·p0, the centre-motion half-width ρ\|Ĝ(a)\|, and the assembly re-derived from c(m,t) = 1/t − 1/m). `tc_rule.py` and `tc_crosscheck.py` were not imported, read or copied while writing it. Result: **136/136 exact rational equality** with the sealed `tc_audit[k][m].H_TC` — identical numerators and denominators, not a tolerance |
| 4.2 | My implementation is capable of failing | PASS | Perturbing each of `delta_G`, `eps_src[3]`, `sup.G`, `norms.k[4]`, `norms.j[2]`, `sup_S0[4]`, `sup_S0[0]`, `rho`, `abs_G_at_a`, `H_at_a`, `W2[3:0]`, `W2[0:3]`, `A1` changes my output. The agreement is not a degeneracy |
| 4.3 | A-constants equal the adopted audit values (acceptance item 5) | PASS | 34 cells × 4 m × {A0, A1, A2} = **408/408** exact matches against `DEFLATED_CONSUMPTION.json` `consumptions[m].audit[k]`. A is independent of m, as the adopted registry-r1 block rule implies |
| 4.4 | H_final is the intersection, non-empty everywhere | PASS | `H_final == H_TC ∩ H_adopted` on all 136 (recomputed from my own H_TC and the adopted `cells[k].H`); no empty intersection; **strictly tightening on all 136**, and mag(H) strictly decreases on all 136 (≈ 5×–16× narrower, e.g. cell 11 m1 279.3 → 17.85, cell 44 m5 213.8 → 40.79) |
| 4.5 | `tc_rule` and `tc_crosscheck` agree exactly on every cell and m (acceptance item 3) | PASS | I ran both frozen modules myself (pins `8d402d11…`, `1c72117f…`): **136/136** agreement, equal to my own path and to the sealed `H_TC` — three independent implementations, one sealed record |
| 5.1 | Baseline: frozen K5-B on the adopted data, **without** TC | PASS | I rebuilt the K5-B cell inputs 0–159 myself (geometry from the frozen `cells.json`; R/D/H/M from `DEFLATED_CONSUMPTION.json`; L₁ from the adopted slot-1 record and the T-EXT Λ re-derived by the frozen `text_consume.text_objects`) and ran the frozen `k5b_check.k5b_literal` (pin `ddd54dc4…`). It reproduces the adopted pass sets **and the full 160-entry `via` map** for all four m (135/129/128/126 passing on 0–159). This validates my cell construction |
| 5.2 | Frozen K5-B with **my** recomputed H_TC on cells 11–44 | PASS | Same construction with `H ← H ∩ H_TC(mine)` and `M ← min(M, mag(H))` on 11–44: **160/160 cells pass for every m on 0–159**, and my `via` map is identical to the sealed consumption's for all four m. The sealed pass/via derivation is reproduced exactly from an independent enclosure |
| 5.3 | No previously passing cell regresses | PASS | Adopted-pass ⊆ TC-pass for every m over 0–309 (empty set difference in each case), and the declared `newly_passing` equals the actual difference for each m. Structurally guaranteed too: narrowing H can only raise `H.lo` and lower `M`, which can only lower Γ, raise μ/ℓ and lower γ — the recurrence is monotone in the right direction |
| 5.4 | `rows_sha256` over the full universe 0–309 | NOT_CHECKABLE_LOCALLY | The adopted consumption publishes per-cell R/D/H/M only for 0–159; rows 160–309 need the K1 records, which live only on the compute host. Checked instead: pass/open ranges, counts, `newly_passing`, and the complete `via` map on 0–159 |
| 5.5 | The frozen K5-B module is itself sound | PASS | `python3 -B code/k5b_check.py run` executed locally: overall `status: PASS` (soundness fuzz, mutation sensitivity, symbolic spine, readiness-scan cross-check, and adversarial cases A1–A11 all pass). The module I used in 5.1/5.2 is the genuine, self-verifying frozen theorem |
| 6.1 | Cell geometry equals `cells.json` | PASS | For all 34: `e0`, `rho`, `left`, `right` exactly equal the frozen CUSUM cover entry at that index (second component 0 everywhere), and `left + ρ = e0 = right − ρ`. The CUSUM cover is indices 0–325 with 0–159 contiguous at the head, so my 0–159 slice is the right one |
| 6.2 | Assembly coefficients equal the frozen table | PASS | Re-derived independently from c(m,t) = 1/t − 1/m: F_r ↦ 1/m for r < m, W_(r,t−r−1) ↦ 1/t − 1/m for 1 ≤ t < m, r < t. Identical to `p5y_k1_cover_ledger_implementation/code/assembly.py::coefficients` for m ∈ {1,2,3,5}, and the 10 W2 keys in every record are exactly the pairs (r, j) with r + j ≤ 3 that this table requires for m = 5 |
| 7 | The manufactured suite is capable of failing | PASS (with note N3) | 48 fixtures × 25-point grid, ground truth computed by 256-bit Arb matrix solves on a finite analogue of the CUSUM structure — a genuine independent oracle, not a self-comparison. 0 containment violations; the structured families run at tightness 0.984–0.99999, i.e. the true value sits within ~1e-5 of the bound, so the fixtures are demanding and a dropped term must show. 20/20 mutants detected, each a real source-text edit to `tc_rule.py`. `frozen_table_ok` and `crosscheck_ok` both true. See note N3 for its one real blind spot |
| 8.1 | K5 status wording: PARTIAL | PASS | m = 5 still open on the tail [305, 309], which this successor does not touch. `evidence/tc_r1/code/coverage_map_r4.py` sets `K5_COVERAGE_COMPLETE = not union_open`, so the r4 map would carry `false` and `union_open_ranges = [[305,309]]`. **K5 remains PARTIAL.** Authorization condition C8 is satisfied |
| 8.2 | The authoritative coverage map has not been pre-emptively changed | PASS | No `K5_COVERAGE_MAP_R4.json` exists anywhere in the tree. The adopted `K5_COVERAGE_MAP_R3.json` (`union_open_ranges = [[11,44],[305,309]]`, `K5_COVERAGE_COMPLETE: false`) is byte-unchanged. The generator was committed but never run — this adjudication is the gate, as intended |
| D1 | Disclosure: `PYTHONINTMAXSTRDIGITS=0` | INFO | Benign. CPython's 4300-digit int→str guard **raises `ValueError`; it never truncates**, and the note records that the first invocation raised before writing any output. The variable only affects decimal printing inside `consumption_adapter.row_json`; all comparisons are exact `Fraction` comparisons. I independently hit and lifted the same guard, and my results matched the seal exactly. See note N2 |
| D2 | Disclosure C7: frozen `Order3Certifier` run on real cells 11–44 while the order-3 registry stays FROZEN_EMPTY | INFO (with obligation) | Not a soundness defect and not a mechanical gate breach — see note N1. Adoption carries an obligation |
| D3 | `note_A_cap_discrepancy`: frozen prose 24 CPU-h vs binding protocol 30 | INFO | Immaterial to this run: the actual spend 14.203 CPU-h is under **both** numbers, and under the campaign hard cap 40. A documentation defect, correctly disclosed. See note N4 |
| S1 | The certified values of the **new** order-3 fields | NOT_CHECKABLE_LOCALLY | See note N5 — the precise residual trust boundary of this adjudication |

Counts: **PASS 27 · INFO 4 · NOT_CHECKABLE_LOCALLY 3 · FAIL 0.**

---

## 2. Notes

### N1 — the parallel channel (disclosure C7). Accepted, with an obligation.

This is the most substantive disclosure and I examined it directly rather than deferring to the authorization review.

`p5y_k5_cusum_order3_real_producer/config/REAL_CELL_AUTHORIZATION_REGISTRY.json` is `FROZEN_EMPTY` and its `rule`
ends with the unconditional sentence "No entry exists: no real CUSUM cell may be evaluated by this producer." The TC
run executed that producer's frozen `Order3Certifier` (and `rung3_residual.g_residual`) on 34 real CUSUM cells.

I find this **within the letter and within the stated rationale**, for four reasons I verified myself:

1. The gated entry points `certify_real_cell` and `rung3_engine.certify_order3` were not executed. The registry check
   lives inside `certify_real_cell`; it is the gate on that entry point, and it was not crossed.
2. The frozen prose claim in `code/cusum_order3.py` is explicitly namespace-scoped: "NOT EXECUTED ON ANY CUSUM CELL
   **IN THIS NAMESPACE**." The TC run is a different namespace under its own authorization, so the frozen sentence is
   not falsified as written.
3. The registry's own `why_empty` states the reason: no mechanism permits a real cell to be used for **producer
   qualification** while being excluded from scientific K5 evidence. The TC use is the opposite case — it is scientific
   K5 evidence and it qualifies nothing about the order-3 producer. The reason the registry is empty does not reach it.
4. No uncertified order-3 value is recorded. I checked every record field by field: the only order-3 quantities present
   are `delta_G` (a certified residual bound), `sup.G` (a certified candidate supremum) and `abs_G_at_a` (a certified
   magnitude upper bound). No signed Ĝ value and no whole-cell R‴ interval exists anywhere in the seal.

It was also pre-registered in the frozen protocol (`producer.parallel_channel`) **before** the run, accepted by the
independent authorization review as condition C7, and re-disclosed in `SEAL.json`.

**Obligation on adoption.** The registry sentence, read alone, now misleads. Adoption should be accompanied by a
cross-reference from the order-3 namespace to `evidence/tc_r1/SEAL.json` `disclosure_C7_parallel_channel`, so that
"no real CUSUM cell may be evaluated by this producer" is not read as a statement of historical fact about cells 11–44.
I cannot make that edit under this brief; I record it as a required follow-up, not as a blocker.

### N2 — what the `PYTHONINTMAXSTRDIGITS` disclosure really says

Beyond being benign, it records a durable operational fact worth carrying forward: the adopted, frozen consumption
adapter (`consumption_adapter.row_json`) **cannot serialize TC-sized exact rationals under default CPython ≥ 3.11**.
Any future consumption of a theorem-TC-class result will hit the same wall. That is a property of the frozen adapter,
not of this run, and it is correctly handled here by an environment setting that changes no value.

### N3 — the one blind spot in the manufactured suite, and why it is closed

The suite's ground-truth containment oracle covers the r = 0 terms, the A-constant terms and the centre motion. It does
**not** cover the r ≥ 1 source tower or the W assembly: `tc_manufactured.synthetic_records` says so in its own docstring
("they are compared against tc_crosscheck, not truth"). Consistently, mutants **M18 (h-tower drops K₀), M19 (W endpoint
swap) and M20 (drop W terms) were caught only by `crosscheck`**, never by containment. Two implementations agreeing is
weaker evidence than an oracle.

That blind spot is closed by this adjudication, not by the qualification. My item-4 implementation was written from the
theorem text with no sight of either frozen module, derives the h-tower and the W assembly independently, is
demonstrably sensitive to `norms.j`, `sup_S0[0]`, `W2[3:0]` and `W2[0:3]` (check 4.2), and agrees exactly on all 136
enclosures. Three independent paths now agree where the qualification had two.

### N4 — budget

Enforced cap 30 (protocol, binding), frozen prose 24, forecast 16.3, actual 14.203. The spend is under every number in
play, so the discrepancy could not have changed any decision in this run. It must be repaired before any future
Campaign A run, where a cap between 24 and 30 could become load-bearing.

### N5 — the residual trust boundary (precise statement)

I verified the theorem's **arithmetic** exactly and completely: given the record fields and the A-constants, H_TC is
provably the value the theorem prescribes, on every cell and every m. What I could not re-derive locally is whether the
record's *inputs* are correct certified bounds for the real cells, because that needs the K1 records and python-flint.

That surface is not uniform, and the distinction matters:

- The **K1-derived and Aux3-derived** fields (`delta_F`, `delta_D`, `delta_H`, `eps_src[0..2]`, `norms.k`, `norms.j`,
  `sup_S0`, `W2`, `H_at_a`, `sup.{F,D,H}`) are covered by the producer's identity gate — 262 fields per cell recomputed
  and compared exactly against the sealed K1 record — and I verified independently (check 3.6) that the records it read
  are the adopted ones, by per-cell sha against the adopted composite export manifest.
- The **new order-3** fields (`delta_G`, `eps_src[3]`, `sup.G`, `abs_G_at_a`) have no identity gate against prior
  adopted evidence, because no prior adopted evidence exists for them. They are this campaign's genuinely new trust
  surface, and their certification rests on the frozen `Order3Certifier` / `rung3_residual.g_residual` executing
  correctly on the host.

One structural safeguard limits the damage a wrong order-3 candidate could do: every order-3 quantity enters H_TC only
through the **non-negative** half-width ρ·|Ĝ(a)| + rad_r (I confirmed all four are ≥ 0 on all 34 × 5 records), while
the enclosure **centre remains the adopted order-2 candidate Ĥ_r(a)**. An order-3 candidate that is simply wrong
therefore cannot shift the enclosure off the true value; it can only fail to widen enough, and only if its *certified
bounds* are understated. The exposure is confined to the correctness of those four certified bounds, which is where
the manufactured suite, the cross-check and qualification S06 are aimed.

This is the ordinary trust boundary of this campaign's model (authorization Note C), not a new one, and it is the same
boundary the adopted Perron-deflated predecessor already stands on.

---

## 3. What I did not check

- Anything requiring the compute host (forbidden by the brief and by the campaign model): the K1 record contents, the
  runtime versions, the producer's actual execution, and `rows_sha256` over cells 160–309.
- The correctness of the frozen `Order3Certifier`'s numerics (note N5).

Everything else in the brief was done locally and is reported above.

---

## 4. Verdict

The commit chain is ordered, linear and confined. Nothing adopted moved. All 84 pins hold and none of them could have
moved. The seal is internally exact and externally tied to adopted K1 evidence cell by cell. The reproduction is
byte-identical. The guard was ALLOW for exactly the 34 pre-registered addresses at the run head and DENY again at the
seal. The theorem's enclosure reproduces exactly from an implementation written independently of both frozen paths, and
the pass/open derivation reproduces exactly from the frozen K5-B driven by that independent enclosure, `via` labels
included. No previously passing cell regresses, and no intersection is empty. The three disclosures are accurately
described and none of them reaches the result's validity. K5 remains PARTIAL: the m = 5 tail [305, 309] is untouched.

The sealed result may change the authoritative K5 coverage map, subject to the obligation in note N1.

`ADJUDICATION = ADOPTED`
