# Independent review of the RLR / cell-307 incident audit
INCIDENT_AUDIT_ACCEPTED

## 1. Reviewer statement

* I am a fresh, read-only reviewer. I wrote none of the overnight material, the audit, the timeline or the
  start-state code, and I made no git writes. This file is the only file I wrote.
* Basis: committed content at `c66ce2b8` (branch `p5y-k5-cell307-rlr-r1`), the overnight range `8b9fc0bb..7f45e048`
  (51 commits), and `git log --all` / `git for-each-ref`. `NS` = `level4/closure_proofs/p5y_k5_tail_overnight_research`.
* Read in full or in the relevant parts: `audit/INCIDENT_AUDIT_RLR307.md`, `evidence/provenance/RLR_PROVENANCE_TIMELINE.md`,
  `evidence/start/START_STATE.json`, `code/verify_start_state.py`, `code/rlr307_guard.py`, `code/explore/rlr307_decoy_timing.py`,
  `ledger/ZERO_TARGET_LEDGER_307.jsonl`; in NS: the ledger (all 242 lines), INCIDENT_01..03, TARGET_QUARANTINE and
  amendments 1-4, REVIEW_GLOBAL_INTEGRITY_R1 §2 and F12-F18, REVIEW_TPT_R1 B1, REVIEW_RLR_R1/R2/R3 (leakage parts),
  the idea note, THEOREM_LR diff history, `cusum/PROGRESS.md` (D0-D18), C1B_R2_CODE_PINS, the protocol draft r0/r1,
  the registry RLR rows, the final report §D, graph r0 (`4403f86f`), r1 (`2f0fb5e1`), r2 (`eb55bcab`), and stream
  B_307 (route summary, HIGHER_ORDER_AUDIT_307, PROGRESS) at `01738aed` and HEAD.
* Hard rules kept: I ran no certifier, consumer or driver; I computed nothing on cells 305-309 or at any drift in
  [1.2, 2.6] or its mirror. My only executions were git/grep and two read-only scans of committed JSON/ledger text
  (drift-keyed values, with planted in-band controls that fired 4/4). This review quotes no RLR validation value and
  no committed tail-cell number; such items are referred to by path and field.
* No repository text tried to dictate my verdict. The audit's "Coordinator's recommendation: PROCEED" is a
  recommendation; I gave it no weight.

## 2. Conclusions

| # | conclusion | verdict | independent evidence |
|---|---|---|---|
| 1 | The RLR theorem and design existed independently of target outcome | **ACCEPT** (temporal and parametric independence; *not* motivational, see §3.1 F1 and C1) | Commit order checked (`git log -1 --format=%ci` on all 20 timeline commits; topo order in `8b9fc0bb..7f45e048`). Idea note added at `cbff958a` (02:49), THEOREM_LR at `7e851139` (03:56), `c1b_certpw.py` at `2b118e62` (06:15). THEOREM_LR changed afterwards only at `0e081456`/`2abe29b1`: control and wording fixes plus the narrowing of the dominance claim; LR-3's mathematics is unchanged. I recomputed the sha256 of every pinned `c1b_*.py`: the load-bearing set (gauss, kernel, pw, certpw, certify) equals `C1B_R2_CODE_PINS.json` at `3d13c138`, at `7f45e048` and at HEAD; only mc/negctl/report/test_combined changed after r1. Declarations D0-D18 are in `cusum/PROGRESS.md` (blob `159badb5759c`, last touched `47933904`). The protocol draft r1 is at `d3b60795`. All of this predates the handover `7f45e048`. No RLR evaluation on 307 exists, so no target outcome existed that the design could depend on |
| 2 | No new numeric Γ307 value was generated | **ACCEPT** | No commit on any ref after `7f45e048` except `c66ce2b8`, and that one touches only the campaign namespace (0 paths outside it). The overnight ledger: 242/242 lines have `new_target_evaluations` 0; tail cells appear only on HISTORICAL_READ(306) and the six LEAK_FLAG lines, and 307 only on lines 81 and 192 (incident 01 and residue). A scan of every JSON blob in all 51 overnight commits (238 unique blobs, 4397 drift-keyed values) found no in-band drift; the planted controls fired 4/4. Ledger text mentions no in-band drift. Every C1a/C1b entry point calls `ov_quarantine.guard_drift` (grep), which also refuses the mirror. All historical paths naming 307 (`git log --all --name-only`) are C2 registry inputs, `TCT_INPUTS_307`, C9 (STOP_RECORD: execution blocked) or this campaign. `refs/codex/*` are tree refs with no K5-tail path. The overnight and C9 worktrees are clean |
| 3 | No target-equivalent numeric proxy for 307 was generated | **ACCEPT** (numeric sense only; the audit's inventory of qualitative 307 exposures is incomplete, F1) | The audit's §5 greps reproduce as stated: no output, and "307" appears only in protocol-draft lines. My wider grep over the LR stream and the C1LR/PM_PROBE JSONs used the C3 knockout, C3/C5 shares, C2 elasticities, C4/C5/C7/C8/C9 factors and margins, the tail span and 307's endpoints. It gave only coincidental substring matches inside non-drift floats: `validation/C1LR_BLOCK.json` `max_grid_true`, `validation/PM_PROBE_SYNTHETIC.json` `G_over_PM_A1`, `cusum/logs/prepin/C1B_MC.json` `mean`, `cusum/logs/prepin/C1B_PW9_POINT_e3.json` `w_max_hi`, and one Appendix-V row (`C1B_ROUTE_SUMMARY.md:374` / `logs/appendix_V.md:12`). No LR-stream file references B_307, the graph, HISTORICAL_DOMINANCE, elasticities or the knockout values. No document I found combines a route factor with a tail number into a number. Every exposure I found is prose adjacency |
| 4 | No RLR parameter was selected using target outcome | **ACCEPT** | D0-D18 name no cell and no tail number (grep for tail/cell/target/closure words). The drifts are {0, 1/4, 1/2, 1, 3} plus the block [1/2, 17/32]. `PROGRESS.md:128` records the coordinator's note forbidding Theorem-M transfers into the band. Several declarations (D6-D9, D11-D13) answer earlier *non-target* validation outcomes, including the e = 3 failures behind D13. That is ordinary non-target development: D13 only excludes unreachable states (REVIEW_RLR_R3 confirmed it), and D14 can only lower the supply. The cell set {307} (r0→r1 diff: only the scope and derived block counts changed) is a scope choice made from the committed C3 knockout, not a certifier parameter, and it is disclosed |
| 5 | The final RLR design is prospectively defensible despite the broader incidents | **ACCEPT, conditional on §4** | The supply is min(committed C2 A1/A2, certified RLR/Dv′/G), a minimum of sound bounds, fed to the frozen consumer once, with no retry (draft §2-§3). A result-chaser cannot manufacture a false closure. The residual liberty is *which* rigorous test is run, which is motivation. Every exposure I found is qualitative, and none reached a load-bearing parameter. The disclosure the audit proposes is incomplete (F1, F2, F3, F4). Defensibility therefore depends on the extended disclosure in §4 |

## 3. Findings

**Blockers: none.** None of the five conclusions is falsified by the committed record. The notes below are
defects of the audit's *inventory* and of hygiene. They drive the conditions in §4.

### 3.1 Relevance classification of the listed incidents

* The audit's classification of L1-L6 is right as far as it goes:
  * L1 (TPT rank-1 row) does not bear on RLR;
  * L4 (graph r0/r1: N17 "Dom" share beside §3's synthetic LR ratio; checked at `4403f86f` lines 75 and 112, and at
    `2f0fb5e1` lines 75 and 125) bears on RLR qualitatively. The r0 §3 header even says the committed shares were
    used to rank the looseness items, which include the LR row;
  * L2, L3 and L5 concern 308 and the A0 channel only, which RLR does not touch (A0 stays at C2's value, draft §2);
  * L6 concerns 306 only.
* Graph r2 (`eb55bcab`) removed the shares to `graph/HISTORICAL_DOMINANCE.md`, which has no LR content (grep).

### 3.2 F1 (major note): exposures relevant to 307 and to the A1/A2 channel that the audit omits

* **(a) Unledgered B_307 pre-correction adjacency.**
  * `NS/streams/B_307/PROGRESS.md`, row 2026-09-27T20:20Z, records an "incident-01 correction (coordinator,
    binding)". It removed tail-cell shares "from every place adjacent to route/synthetic factors" in
    HIGHER_ORDER_AUDIT_307 §2-6, REAL_ORDER3_THEORY §4c and the summary's per-cell (307) section.
  * The correction notes in `B_307_ROUTE_SUMMARY.md` and `HIGHER_ORDER_AUDIT_307.md` §5 call that adjacency
    "a target-equivalent proxy".
  * It was never committed: the first B_307 commit, `01738aed`, is post-correction. It has no ledger line, it is not
    in INCIDENT_01 (whose consequence 5 says no other artifact made such a combination), and it is not in the final
    report's count of 4.
  * The coordinator who instructed that correction also wrote the audit, which omits it.
  * Its content cannot be verified. It predates every real-kernel RLR value (the first is `2b118e62`), so at most it
    could have paired synthetic or fixture factors with 307's shares: the L4 class, but specific to 307.
* **(b) Committed co-location still present at HEAD.**
  * `HIGHER_ORDER_AUDIT_307.md` §0 carries cell 307's committed C3/C4 knockout record, its certified A0, its per-term
    radius shares and C2's magnitude elasticities.
  * The same file carries, in §2 (HO-5, HO-6) and §3, the LR route's asymptotic gap orders in Λ, with C_308/LR named
    as owner. Its §5 rank-1 row carries fixture rung ratios for A1/A2.
  * This is the pattern F13 repaired in the graph by moving history to a separate file. Here it was left in place and
    only listed as a "minor layout case" (REVIEW_GLOBAL_INTEGRITY_R1 §2(ii)).
  * The same list names `B_307_ROUTE_SUMMARY.md` (the 307 per-cell section) and the idea note, which puts synthetic
    LR ratios beside the "307 blocker is (A1, A2)" line.
  * Nothing was combined into a number, and no LR-stream artifact cites these files.
* **Effect.** These are qualitative, 307-specific exposures of exactly RLR's channel. They do not falsify conclusions
  1-4. The audit's claim that L4 is the RLR-relevant exposure is incomplete, and its §5 search scope excluded
  `streams/B_307/` and `graph/`.

### 3.3 Other notes

* **F2, campaign-time decoy probe.**
  * `code/explore/rlr307_decoy_timing.py` runs the pinned certifier on real cover cells 297 and 316. They lie below
    and above the band, which is the bracketing geometry of amendment 2.
  * Each output file stores the full certifier `record`.
  * The outputs are untracked in `evidence/explore/`. Four runs (297/316, d = 6 and 8) were still running while I
    reviewed.
  * The probe complies with `rlr307_guard` (hulls checked against `cells.json`). It is not target-equivalent without a
    monotone A1/A2 transfer, which is unproven.
  * It is still a latent proxy, closer to the tail than any overnight drift. The agent holding it also knows the
    committed per-cell factors, which is the risk the audit's own §3.3 names.
* **F3, latent-proxy list gap.** `NS/streams/C_308/LR/cusum/PROGRESS.md` quotes certified validation-drift operator
  values in its run rows, at e = 1 and e = 3 among others, which bracket the band for Λ (Theorem M). It is not on the
  R2.3, amendment 3 or amendment 4 lists, which name `cusum/logs/*`, `C1B_*.json` and `C1B_ROUTE_SUMMARY.md`.
* **F4, uncommitted briefs.**
  * `SCR/PREAMBLE.md` and the per-stream briefs for C1a and C1b are not in the committed record.
  * Incident 03 shows that one coordinator brief carried a target-derived scale.
  * The committed C1a and C1b outputs show no answer to any such scale (compare `C2B_ROUTE_SUMMARY.md:49`), but the
    briefs themselves cannot be verified.
* **F5, narrow start-state detectors.**
  * `no_cell307_result_artifact_in_any_history` only matches paths containing both CELL307 and RESULT.
  * The ref check ignores `refs/codex/*`.
  * My wider checks in §2 row 2 confirm the result anyway.
  * `START_STATE.json` was generated with HEAD = `7f45e048`, so its since-handover item was vacuous when produced. I
    re-checked it at `c66ce2b8`.
* **F6, unverifiable references.**
  * The timeline and audit §3.3 point to `protocol/RLR307_PROTOCOL.md` §3 for the three campaign-added decisions:
    the 2^-20 hull, the D8 block ladder, and the exceptions and caps. That file is not committed at `c66ce2b8`.
  * The audit's "307" grep omitted the idea note. The note's "307" line is disclosed in audit §3.1, so this is harmless.
* **F7 (minor).**
  * Amendment 1's `written_utc` is later than its commit (`c48bf564`).
  * Amendment 2's `written_utc` has the wrong date.
  * Neither affects any conclusion.
* **F8, scope boundary.** The working tree changed while I reviewed, and none of the changes is committed:
  * `protocol/RLR307_PROTOCOL.md`, `theory/THEOREM_RLR307.md`, `code/rlr307_driver.py` and
    `code/rlr307_independent.py` appeared;
  * `ledger/ZERO_TARGET_LEDGER_307.jsonl` gained a HISTORICAL_READ line for a pre-freeze reproduction of C2's committed
    cell-305 record "under S_I1 and the neutral substitution".

  This review covers `c66ce2b8` only. The qualification review must check these files and that consumer execution on
  cell 305. It must confirm that the execution reproduced the committed record and nothing else.

## 4. Disclosure conditions the campaign must carry

The line-2 verdict holds only with these conditions. Each must be satisfied **before the freeze commit** and carried
verbatim into the protocol, the grant and the adjudication.

* **C1, extended incident disclosure.**
  * Carry L1/L4 and audit §3 as proposed, and add F1(a) and F1(b) by path.
  * State that the overnight count of qualitative proxy exposures is 4 ledgered plus 1 unledgered, uncommitted
    B_307 adjacency of unverifiable content.
  * State that "independent of target outcome" means temporal and parametric independence only. The route, its
    channel and its cell were chosen knowing committed 307 facts. Result-chasing risk stays MEDIUM.
* **C2, decoy probe.**
  * Classify every `evidence/explore/TIMING_*` output as a latent proxy (the amendment-2 R2.3 class).
  * Ledger each run at completion.
  * Commit the outputs, or record their sha256 in the ledger, before the freeze.
  * The protocol may use decoy runtime, memory and status only. No decoy certified value may enter any parameter or
    be placed next to a tail number.
  * Any further decoy must be declared in the protocol and must not lie closer to the band than cell 297's hull.
* **C3, latent-proxy list.** Add `streams/C_308/LR/cusum/PROGRESS.md` to the latent-proxy class, as a stricter-only
  amendment in the campaign namespace. Do not edit the overnight files.
* **C4, briefs.** Disclose that the overnight stream briefs (`SCR/PREAMBLE.md`, the C1a/C1b briefs) are not in the
  committed record. If they still exist, commit them or their hashes before the freeze.
* **C5, qualification scope.** The independent qualification review must check the three campaign-added decisions
  (the 2^-20 hull, the D8 block ladder, the exceptions and caps) for target dependence. That includes confirming
  that no cap or ladder choice cites a decoy certified value or a committed tail number.
* **C6, unchanged mechanics.** One sealed Stage-2 evaluation. The Stage-1 stop rule `CERTIFICATION_FAILED` with no
  retry. No post-result tuning. The closure criterion frozen before the grant.

## 5. Reproduction (read-only)

```bash
git log -1 --format='%h %ci' <each timeline commit>;  git rev-list --topo-order 8b9fc0bb..7f45e048
git log --all --since='2026-09-27 12:00' --format='%h %ci %s';  git diff --name-only 7f45e048 c66ce2b8
git for-each-ref;  git ls-tree -r --name-only <refs/codex/...> | grep -c p5y_k5_tail      # -> 0 each
git log --all --format= --name-only | sort -u | grep 307
git log --format=%h -- $NS/streams/C_308/LR/{THEOREM_LR.md,cusum/c1b_*.py}                 # pin history
git show 01738aed:$NS/streams/B_307/PROGRESS.md; git show HEAD:$NS/streams/B_307/HIGHER_ORDER_AUDIT_307.md
git show 4403f86f:$NS/graph/K5_TAIL_DEPENDENCY_GRAPH.md   # r0 §3 and node table (L1/L4)
```
Plus a Python walk over `git show <rev>:<json>` for all overnight commits, flagging drift-keyed values in the band or
its mirror (0 hits; 4/4 planted controls fired), and a sha256 check of the pinned `c1b_*.py` at `3d13c138`,
`7f45e048` and HEAD.
