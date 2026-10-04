# User decision brief — Cell-308 MB-S r1: designated, NOT_DERIVED at the R-FREE attainability gate

Target-free. Written from committed text only. No host reading was taken, simulated or edited for this brief; no
Cell-308 target evaluation and no Cell-309 activity of any kind. `new_target_evaluations = 0`.

Ledger class: NONTARGET_DRIFT_VALIDATION (verification and documentation only).

## 1. What was verified (independently, from the pushed branches)

| item | expected | found | result |
|---|---|---|---|
| candidate branch `p5y-k5-cell308-mbs-r1-candidate` | `142d97a90a1c3fafff394044aa1448674f7a633c` | same | OK |
| research branch `p5y-k5-cell308-mbs-r1-research` | `c6769158…` | `c67691583424e42ff128502e5fa531af5b4df2d8` | OK |
| designated evidence `evidence_prefreeze/MBS308_RRULES_DESIGNATED.json` sha256 | `86d3f8cb…ee90fe` | `86d3f8cba3543e2b165ac648f9858fef8fb5a0efc141fec77bfa0ab604ee90fe` | OK |
| evidence `commit` / `preflight.commit` | candidate code commit | `45b93b892129550a7e61c0e32baa0151771cd165` (parent of `142d97a9`) | OK |
| evidence `driver_sha256` | sha256 of `code/mbs308_driver.py` at `142d97a9` | `117624e9…beab1` = file | OK |
| evidence `designated`, `target_evaluations` | `true`, `0` | `true`, `0` | OK |
| derivation `evidence_prefreeze/MBS308_RRULES_DERIVATION.json` sha256 | ledger `derivation_sha256` | `8a4e7984…29c17` | OK |
| research copy `audit/DESIGNATED_DERIVATION_RFREE_STOP_86D3F8CB.json` | byte-identical to the derivation | `cmp` identical | OK |
| derivation `rules_sha256` / `tool_sha256` | `mbs308_rrules.py` / `mbs308_derive.py` | `c04239de…` / `da35e7e1…` = files | OK |
| derivation `status`, `stop_before_freeze`, `outputs` | `NOT_DERIVED`, `true`, all null | same | OK |
| derivation checks | only R-FREE fails | `r_free_attainable=false` (and `all_hold=false`); all 12 others `true` | OK |
| series history `ledger/MBS308_SERIES_HISTORY.jsonl` | 3 invalid + 1 designated | 8 rows: INVALID `f80158c4…`, HOST_NOT_PREPARED `7c431127…`, INVALID `ef28e8f3…`, DESIGNATED `86d3f8cb…` | OK |
| `audit/DESIGNATED_PREFREEZE_INVALID_00{1,2,3}_*.json` sha256 | the history's three hashes | equal, in order | OK |
| research ledger last line | binds all of the above | candidate `45b93b89`, evidence commit `142d97a9`, evidence/derivation sha256, `NOT_DERIVED`, `GATE_UNATTAINABLE`, `6979321856`, observed min/max | OK |
| final commits are additive only | no existing byte overwritten | `45b93b89→142d97a9`: 3 files, +9140/−0; `8d8b49ab→c6769158`: 2 files, +416/−0 | OK |
| no freeze / qualification / grant | absent | no `protocol/MBS308_FREEZE.json`, no `qualification/`, no `authorization/` | OK |

## 2. Independent recomputation of the stop

From the designated evidence and the committed R-MEM values (no tool output trusted):

* R-MEM step 4: s = 56443/38088 ≈ 1.482, k = max(3, 2s) = 3, MEM_CAP = roundup_256MiB(3 × 924 762 112) =
  **2 952 790 016**. Matches the derivation.
* R-FREE: MEM_CAP + (5 − 1) × P + D = 2 952 790 016 + 4 × 924 762 112 + 142 147 584 = 6 793 986 048;
  roundup_256MiB → **FREE_MEM_MIN = 6 979 321 856 bytes (6.5 GiB)**. Matches.
* The ten prepared readings (AC power, 30 s apart, 17:54:20Z–17:58:50Z on 2026-10-03), `free_memory_bytes`:
  3 911 155 712, 3 959 848 960, 3 983 474 688, 3 938 091 008, 3 911 892 992, 3 785 605 120, 3 874 881 536,
  3 870 867 456, 3 876 716 544, 3 855 581 184. Min 3.53 GiB, max 3.71 GiB. **Readings reaching FREE_MEM_MIN: 0 of
  10; longest consecutive run: 0** (rule needs ≥ 3). Shortfall at the best reading: 2 995 847 168 bytes (2.79 GiB).
* Re-running `code/mbs308_derive.py derive` on the committed evidence (Python 3.11, read-only `git cat-file` of the
  pinned 39-name driver) reproduces the committed derivation **byte-for-byte** (sha256 `8a4e7984…`), exit status 1.

Arithmetic context (not a prediction, not a reading): R-MEM's own feasibility check records hw.memsize − W_idle =
7 155 974 144 bytes. FREE_MEM_MIN leaves 176 652 288 bytes (≈ 168 MiB) of that for every non-wired page that is not
free, inactive, speculative or purgeable — WindowServer, the hosting app and all other resident processes together.
In the best designated reading that quantity was ≈ 3.05 GiB.

## 3. The implementation fails closed (target-free checks run for this brief)

* `mbs308_derive.derivation`: any failing check gives `status ≠ OK`, `stop_before_freeze = true` and every output
  `null`; the computed values are kept only under `outputs_as_computed`.
* `mbs308_repin.py apply` (dry run, no `--write`) on the committed derivation: **refused**
  `DERIVATION_NOT_APPLICABLE: STATUS_NOT_OK, STOP_BEFORE_FREEZE, A_RULE_CHECK_DOES_NOT_HOLD, OUTPUT_MISSING`, exit 2.
  Worktree unchanged.
* A forged copy of the derivation with `status = OK`, `stop_before_freeze = false`, every check `true` and the
  as-computed outputs promoted: `derivation_reasons` → `NOT_REPRODUCED_FROM_THE_EVIDENCE` (the apply step re-derives
  from the committed evidence).
* `mbs308_rrules.r_free` boundary probes on synthetic in-memory values (never written, not readings):
  3 consecutive at exactly FREE_MEM_MIN → ATTAINABLE; 2 consecutive → GATE_UNATTAINABLE; 3 at FREE_MEM_MIN − 1 →
  GATE_UNATTAINABLE; 3 non-consecutive → GATE_UNATTAINABLE; 9 readings → INVALID_READINGS. FREE_MEM_MIN is
  6 979 321 856 in every case: no input to the readings reduces it.
* `mbs308_measure.history_has_designated` on the committed series history → `true`: a further non-dev measurement
  is refused `ALREADY_DESIGNATED` before anything runs.
* The execute path needs `protocol/MBS308_FREEZE.json` and `authorization/MBS308_GRANT.json`; neither exists.

The candidate's own test suite was **not** run here: it is pinned to Python 3.14.5 on the macOS qualification host
(`PLATFORM_PINS`), and several test files drive the `execute`/`arm_target` paths through harnesses that need that
host. No implementation or documentation defect was found that needs a change; the candidate is untouched.

## 4. Is there a legal continuation on this 8 GiB host? No.

Each route below is closed by accepted text:

1. **Lower the threshold / change k, WORKERS or the floor.** Prohibited: R-FREE "the value is never reduced
   silently"; R-MEM step 5 "k, WORKERS and the floor are never reduced silently"; constraint of this session.
2. **Measure again on this candidate (best-of-N, a replacement series).** Prohibited: protocol §11.2 step 1(iv),
   accepted by REVIEW_PREMEASUREMENT_IMPLEMENTATION_MBS308 §5/§10 — "Once a series is designated … the tool refuses to
   run again (`ALREADY_DESIGNATED`): no best-of-N, no replacement." Enforced by `mbs308_measure` (verified above).
3. **Apply, freeze or qualify anyway.** Prohibited: §11.2 step 2 — a non-OK derivation "STOPS BEFORE FREEZE with no
   output at all"; step 3 refuses a derivation that is not OK (verified above). `designated = true` grants nothing.
4. **Run on another, larger host.** Not a continuation: USER_DECISION_BRIEF_308_SUCCESSOR_R2, host-identity row —
   "this host only: another host means S4's changed branch (route A1, HOST row)". S4's changed branch requires a
   written non-target motivation, a route amendment and review, new code reviews, a new qualification and a fresh
   incident re-rating (SUCCESSOR_GOVERNANCE_308 S4 and S8; ADDENDUM_A1 S12; brief R2 item 3(ii)). That is a new governance process, not a step of MB-S r1.

R-FREE's own text gives the consequence: "Otherwise it records GATE_UNATTAINABLE: `execute` cannot start on this
host". **The current state is the protocol-mandated stopping point for MB-S r1.**

## 5. Prohibited steps that were not executed

No Cell-308 target evaluation; no Cell-309 read, run or modification; no R-FREE or other threshold change; no reading
taken, simulated, edited, replaced or re-measured; no `INVALID_*` record or designated evidence touched; no apply,
freeze, qualification, grant or target result; no candidate commit.

## 6. For the owner (the only decisions that can move this)

Work on Cell-308 under MB-S can resume only through an owner ruling that opens a new, separately governed route.
Nothing in the accepted texts lets the builder choose among these. Stated without a recommendation:

* **(a) Close MB-S r1 as GATE_UNATTAINABLE on this host** and record it as such in the registry. No further action.
* **(b) Open a route on S4's changed branch for a different host**, with every S4/S8/S12 requirement met
  prospectively and target-free before any successor evaluation (new designated series on that host, new
  derivation, which must return `status = OK`, then apply, freeze, qualification and grant in order).
* **(c) Any other ruling** (for example on the rule text itself) is the owner's alone and needs its own independent
  review; this brief proposes none.

Until such a ruling exists the single legally permitted action is to keep the state as committed.
